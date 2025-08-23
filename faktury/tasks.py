"""
Celery tasks for OCR processing

Handles asynchronous OCR result processing and Faktura creation
"""

import logging
from celery import shared_task
from django.utils import timezone
from django.db import models

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_ocr_task(self, document_upload_id):
    """
    Celery task to process uploaded document with OCR and create OCRResult
    
    Args:
        document_upload_id: ID of DocumentUpload to process
        
    Returns:
        dict: Processing result with status and details
    """
    try:
        from .models import DocumentUpload, OCRResult
        from .services.file_upload_service import FileUploadService
        from .services.document_ai_service import get_document_ai_service
        
        logger.info(f"Starting document OCR processing task for ID: {document_upload_id}")
        
        # Get document upload
        try:
            document_upload = DocumentUpload.objects.get(id=document_upload_id)
        except DocumentUpload.DoesNotExist:
            logger.error(f"DocumentUpload {document_upload_id} not found")
            return {
                'status': 'error',
                'message': f'DocumentUpload {document_upload_id} not found',
                'document_upload_id': document_upload_id
            }
        
        # Mark as processing started
        document_upload.mark_processing_started()
        
        # Get file content
        file_service = FileUploadService()
        file_content = file_service.get_file_content(document_upload)
        
        # Process with OCR service
        ocr_service = get_document_ai_service()
        extracted_data = ocr_service.process_invoice(file_content, document_upload.content_type)
        
        # Create OCRResult
        ocr_result = OCRResult.objects.create(
            document=document_upload,
            raw_text=extracted_data.get('raw_text', ''),
            extracted_data=extracted_data,
            confidence_score=extracted_data.get('confidence_score', 0.0),
            processing_time=extracted_data.get('processing_time', 0.0),
            processor_version=extracted_data.get('processor_version', 'unknown'),
            processing_location=extracted_data.get('processing_location', 'unknown'),
            processing_status='pending'  # Will be processed by OCR integration
        )
        
        # Mark document as completed
        document_upload.mark_processing_completed()
        
        logger.info(f"Document OCR processing completed for {document_upload_id}, created OCRResult {ocr_result.id}")
        
        return {
            'status': 'success',
            'message': f'OCR processing completed',
            'document_upload_id': document_upload_id,
            'ocr_result_id': ocr_result.id,
            'confidence_score': ocr_result.confidence_score
        }
        
    except Exception as exc:
        logger.error(f"Error in document OCR processing task for {document_upload_id}: {str(exc)}", exc_info=True)
        
        # Mark document as failed
        try:
            document_upload = DocumentUpload.objects.get(id=document_upload_id)
            document_upload.mark_processing_failed(str(exc))
        except DocumentUpload.DoesNotExist:
            pass
        
        # Retry the task if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying document OCR processing task for {document_upload_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        return {
            'status': 'error',
            'message': f'Task failed after {self.max_retries} retries: {str(exc)}',
            'document_upload_id': document_upload_id
        }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_ocr_result_task(self, ocr_result_id):
    """
    Celery task to process OCR result and create Faktura
    
    Args:
        ocr_result_id: ID of OCRResult to process
        
    Returns:
        dict: Processing result with status and details
    """
    try:
        from .services.ocr_integration import process_ocr_result
        from .models import OCRResult
        
        logger.info(f"Starting OCR result processing task for ID: {ocr_result_id}")
        
        # Check if OCR result exists
        try:
            ocr_result = OCRResult.objects.get(id=ocr_result_id)
        except OCRResult.DoesNotExist:
            logger.error(f"OCR result {ocr_result_id} not found")
            return {
                'status': 'error',
                'message': f'OCR result {ocr_result_id} not found',
                'ocr_result_id': ocr_result_id
            }
        
        # Process the OCR result
        faktura = process_ocr_result(ocr_result_id)
        
        if faktura:
            logger.info(f"Successfully processed OCR result {ocr_result_id}, created Faktura {faktura.numer}")
            return {
                'status': 'success',
                'message': f'Created Faktura {faktura.numer}',
                'ocr_result_id': ocr_result_id,
                'faktura_id': faktura.id,
                'faktura_numer': faktura.numer
            }
        else:
            logger.info(f"OCR result {ocr_result_id} processed but no Faktura created")
            return {
                'status': 'processed',
                'message': 'OCR result processed but no Faktura created',
                'ocr_result_id': ocr_result_id
            }
            
    except Exception as exc:
        logger.error(f"Error in OCR processing task for {ocr_result_id}: {str(exc)}", exc_info=True)
        
        # Retry the task if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying OCR processing task for {ocr_result_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        # Mark OCR result as failed if all retries exhausted
        try:
            from .models import OCRResult
            ocr_result = OCRResult.objects.get(id=ocr_result_id)
            ocr_result.mark_processing_failed(f"Task failed after {self.max_retries} retries: {str(exc)}")
        except OCRResult.DoesNotExist:
            pass
        
        return {
            'status': 'error',
            'message': f'Task failed after {self.max_retries} retries: {str(exc)}',
            'ocr_result_id': ocr_result_id
        }


@shared_task
def batch_process_pending_ocr_results():
    """
    Celery task to process all pending OCR results
    
    This can be run periodically to catch any OCR results that weren't
    processed automatically due to system issues.
    
    Returns:
        dict: Batch processing results
    """
    try:
        from .models import OCRResult
        
        logger.info("Starting batch processing of pending OCR results")
        
        # Get all pending OCR results
        pending_results = OCRResult.objects.filter(
            processing_status='pending'
        ).select_related('document', 'document__user')
        
        total_count = pending_results.count()
        processed_count = 0
        error_count = 0
        
        logger.info(f"Found {total_count} pending OCR results to process")
        
        for ocr_result in pending_results:
            try:
                # Trigger individual processing task
                process_ocr_result_task.delay(ocr_result.id)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error queuing OCR result {ocr_result.id}: {str(e)}")
                error_count += 1
        
        result = {
            'status': 'completed',
            'total_found': total_count,
            'queued_for_processing': processed_count,
            'errors': error_count,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Batch processing completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error in batch OCR processing task: {str(exc)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(exc),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def cleanup_failed_ocr_results(days_old=7):
    """
    Celery task to clean up old failed OCR results
    
    Args:
        days_old: Number of days after which to clean up failed results
        
    Returns:
        dict: Cleanup results
    """
    try:
        from .models import OCRResult
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        logger.info(f"Starting cleanup of failed OCR results older than {days_old} days")
        
        # Find old failed results
        failed_results = OCRResult.objects.filter(
            processing_status='failed',
            created_at__lt=cutoff_date
        )
        
        count = failed_results.count()
        
        if count > 0:
            # Delete the failed results
            failed_results.delete()
            logger.info(f"Cleaned up {count} failed OCR results")
        else:
            logger.info("No failed OCR results to clean up")
        
        return {
            'status': 'completed',
            'cleaned_up_count': count,
            'cutoff_date': cutoff_date.isoformat(),
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error in OCR cleanup task: {str(exc)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(exc),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def generate_ocr_processing_report(user_id=None):
    """
    Generate OCR processing statistics report
    
    Args:
        user_id: Optional user ID to generate report for specific user
        
    Returns:
        dict: Processing statistics
    """
    try:
        from .services.ocr_integration import get_ocr_processing_stats
        from django.contrib.auth.models import User
        from .models import OCRResult
        
        logger.info(f"Generating OCR processing report for user {user_id or 'all users'}")
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                stats = get_ocr_processing_stats(user)
                stats['user_id'] = user_id
                stats['username'] = user.username
            except User.DoesNotExist:
                return {
                    'status': 'error',
                    'message': f'User {user_id} not found'
                }
        else:
            # Global statistics
            from django.db.models import Count, Avg
            
            stats = OCRResult.objects.aggregate(
                total_processed=Count('id'),
                avg_confidence=Avg('confidence_score'),
                auto_created_count=Count('id', filter=models.Q(auto_created_faktura=True)),
                manual_review_count=Count('id', filter=models.Q(processing_status='manual_review')),
                failed_count=Count('id', filter=models.Q(processing_status='failed')),
            )
            
            # Calculate rates
            total = stats['total_processed'] or 0
            if total > 0:
                stats['success_rate'] = ((stats['auto_created_count'] or 0) / total) * 100
                stats['manual_review_rate'] = ((stats['manual_review_count'] or 0) / total) * 100
                stats['failure_rate'] = ((stats['failed_count'] or 0) / total) * 100
            else:
                stats['success_rate'] = 0
                stats['manual_review_rate'] = 0
                stats['failure_rate'] = 0
        
        stats['status'] = 'completed'
        stats['timestamp'] = timezone.now().isoformat()
        
        logger.info(f"OCR processing report generated: {stats}")
        return stats
        
    except Exception as exc:
        logger.error(f"Error generating OCR processing report: {str(exc)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(exc),
            'timestamp': timezone.now().isoformat()
        }