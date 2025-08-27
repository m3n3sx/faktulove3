"""
Celery tasks for Ensemble OCR processing

Handles asynchronous OCR result processing with ensemble engines and Faktura creation
"""

import logging
import time
from celery import shared_task
from django.utils import timezone
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_ocr_task(self, document_upload_id):
    """
    Celery task to process uploaded document with Ensemble OCR and create OCRResult
    
    Args:
        document_upload_id: ID of DocumentUpload to process
        
    Returns:
        dict: Processing result with status and details
    """
    try:
        from .models import DocumentUpload, OCRResult, OCREngine, OCRProcessingStep
        from .services.file_upload_service import FileUploadService
        from .services.ensemble_ocr_service import EnsembleOCRService
        
        logger.info(f"Starting ensemble document OCR processing task for ID: {document_upload_id}")
        
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
        
        # Initialize ensemble OCR service
        ensemble_config = getattr(settings, 'ENSEMBLE_OCR_CONFIG', {})
        ensemble_service = EnsembleOCRService(**ensemble_config)
        
        # Process with ensemble OCR
        start_time = time.time()
        extracted_data = ensemble_service.process_invoice(file_content, document_upload.content_type)
        total_processing_time = time.time() - start_time
        
        # Track cost savings
        cost_savings = _calculate_cost_savings(extracted_data)
        
        # Create OCRResult with ensemble metadata
        ocr_result = OCRResult.objects.create(
            document=document_upload,
            raw_text=extracted_data.get('raw_text', ''),
            extracted_data=extracted_data.get('extracted_data', {}),
            confidence_score=extracted_data.get('confidence_score', 0.0),
            processing_time=total_processing_time,
            processor_version=extracted_data.get('processor_version', 'Ensemble-OCR-2.0'),
            processing_location='local',
            processing_status='pending',
            # Ensemble-specific fields
            engine_results=extracted_data.get('ensemble_results', {}),
            best_engine_result=extracted_data.get('engine_metadata', {}).get('best_engine', 'unknown'),
            pipeline_version='2.0',
            preprocessing_applied=extracted_data.get('preprocessing_applied', []),
            fallback_used=extracted_data.get('fallback_used', False),
            ensemble_engines_used=extracted_data.get('engine_metadata', {}).get('ensemble_engines_used', []),
            vendor_independent=True,
            cost_savings=cost_savings
        )
        
        # Mark document as completed
        document_upload.mark_processing_completed()
        
        logger.info(f"Ensemble document OCR processing completed for {document_upload_id}, created OCRResult {ocr_result.id}")
        
        return {
            'status': 'success',
            'message': f'Ensemble OCR processing completed',
            'document_upload_id': document_upload_id,
            'ocr_result_id': ocr_result.id,
            'confidence_score': ocr_result.confidence_score,
            'cost_savings': cost_savings,
            'engines_used': extracted_data.get('engine_metadata', {}).get('ensemble_engines_used', []),
            'vendor_independent': True
        }
        
    except Exception as exc:
        logger.error(f"Error in document OCR processing task for {document_upload_id}: {str(exc)}", exc_info=True)
        
        # Use fallback handler for error recovery
        try:
            from .services.ocr_fallback_handler import OCRFallbackHandler
            
            fallback_handler = OCRFallbackHandler()
            fallback_result = fallback_handler.handle_processing_failure(
                document_upload_id, exc, {'operation': 'document_ocr_processing', 'task_retry': self.request.retries}
            )
            
            logger.info(f"Fallback handling result for document {document_upload_id}: {fallback_result}")
            
            # If fallback suggests retry and we haven't exceeded max retries
            if (fallback_result.get('next_action') == 'retry_processing' and 
                self.request.retries < self.max_retries):
                logger.info(f"Retrying document OCR processing task for {document_upload_id} (attempt {self.request.retries + 1})")
                raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
            
            # Return fallback result
            return {
                'status': 'fallback_handled',
                'message': f'Fallback handling completed: {fallback_result.get("strategy", "unknown")}',
                'document_upload_id': document_upload_id,
                'fallback_result': fallback_result
            }
            
        except Exception as fallback_exc:
            logger.error(f"Fallback handling failed for document {document_upload_id}: {fallback_exc}")
            
            # Mark document as failed as last resort
            try:
                document_upload = DocumentUpload.objects.get(id=document_upload_id)
                document_upload.mark_processing_failed(str(exc))
            except DocumentUpload.DoesNotExist:
                pass
            
            return {
                'status': 'error',
                'message': f'Task and fallback failed: {str(exc)}',
                'document_upload_id': document_upload_id,
                'fallback_error': str(fallback_exc)
            }


def _calculate_cost_savings(extracted_data: dict) -> dict:
    """
    Calculate cost savings from using ensemble OCR instead of Google Cloud
    
    Args:
        extracted_data: OCR processing result data
        
    Returns:
        Dictionary with cost savings information
    """
    try:
        # Google Cloud Document AI pricing (approximate)
        google_cloud_cost_per_page = 0.15  # USD per page
        
        # Ensemble OCR cost (local processing)
        ensemble_cost_per_page = 0.01  # USD per page (electricity, compute)
        
        # Calculate savings
        pages_processed = 1  # Default to 1 page
        if 'engine_metadata' in extracted_data:
            # Try to determine number of pages from metadata
            metadata = extracted_data['engine_metadata']
            if 'total_pages' in metadata:
                pages_processed = metadata['total_pages']
        
        google_cost = google_cloud_cost_per_page * pages_processed
        ensemble_cost = ensemble_cost_per_page * pages_processed
        savings = google_cost - ensemble_cost
        
        return {
            'google_cloud_cost': google_cost,
            'ensemble_cost': ensemble_cost,
            'savings_per_page': savings,
            'pages_processed': pages_processed,
            'savings_percentage': (savings / google_cost * 100) if google_cost > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error calculating cost savings: {e}")
        return {
            'google_cloud_cost': 0.15,
            'ensemble_cost': 0.01,
            'savings_per_page': 0.14,
            'pages_processed': 1,
            'savings_percentage': 93.33
        }


def _is_retryable_error(exc: Exception) -> bool:
    """
    Determine if an error is retryable
    
    Args:
        exc: Exception to check
        
    Returns:
        True if error is retryable, False otherwise
    """
    retryable_errors = [
        'timeout',
        'connection',
        'network',
        'temporary',
        'rate limit',
        'service unavailable',
        'engine failure',
        'memory',
        'resource'
    ]
    
    error_str = str(exc).lower()
    return any(retryable_error in error_str for retryable_error in retryable_errors)


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
        
        # Use fallback handler for error recovery
        try:
            from .services.ocr_fallback_handler import OCRFallbackHandler
            from .models import OCRResult
            
            # Get the document ID for fallback handling
            try:
                ocr_result = OCRResult.objects.get(id=ocr_result_id)
                document_id = ocr_result.document.id
                
                fallback_handler = OCRFallbackHandler()
                fallback_result = fallback_handler.handle_processing_failure(
                    document_id, exc, {
                        'operation': 'ocr_result_processing', 
                        'ocr_result_id': ocr_result_id,
                        'task_retry': self.request.retries
                    }
                )
                
                logger.info(f"Fallback handling result for OCR result {ocr_result_id}: {fallback_result}")
                
                # If fallback suggests retry and we haven't exceeded max retries
                if (fallback_result.get('next_action') == 'retry_processing' and 
                    self.request.retries < self.max_retries):
                    logger.info(f"Retrying OCR processing task for {ocr_result_id} (attempt {self.request.retries + 1})")
                    raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
                
                # Return fallback result
                return {
                    'status': 'fallback_handled',
                    'message': f'Fallback handling completed: {fallback_result.get("strategy", "unknown")}',
                    'ocr_result_id': ocr_result_id,
                    'fallback_result': fallback_result
                }
                
            except OCRResult.DoesNotExist:
                logger.error(f"OCR result {ocr_result_id} not found for fallback handling")
                
        except Exception as fallback_exc:
            logger.error(f"Fallback handling failed for OCR result {ocr_result_id}: {fallback_exc}")
        
        # Mark OCR result as failed as last resort
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
def process_retry_queue():
    """
    Process documents scheduled for retry
    
    Returns:
        dict: Retry processing results
    """
    try:
        from .models import DocumentUpload
        from django.utils import timezone
        
        logger.info("Starting retry queue processing")
        
        # Get documents scheduled for retry
        retry_documents = DocumentUpload.objects.filter(
            processing_status='retry_scheduled',
            next_retry_at__lte=timezone.now()
        ).select_related('user')
        
        total_count = retry_documents.count()
        processed_count = 0
        error_count = 0
        
        logger.info(f"Found {total_count} documents scheduled for retry")
        
        for document in retry_documents:
            try:
                # Reset status and trigger processing
                document.processing_status = 'queued'
                document.next_retry_at = None
                document.save(update_fields=['processing_status', 'next_retry_at'])
                
                # Trigger document processing task
                process_document_ocr_task.delay(document.id)
                processed_count += 1
                
                logger.info(f"Queued document {document.id} for retry processing")
                
            except Exception as e:
                logger.error(f"Error processing retry for document {document.id}: {str(e)}")
                error_count += 1
        
        result = {
            'status': 'completed',
            'total_found': total_count,
            'queued_for_retry': processed_count,
            'errors': error_count,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Retry queue processing completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error in retry queue processing task: {str(exc)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(exc),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def process_manual_review_queue_notifications():
    """
    Send notifications for documents in manual review queue
    
    Returns:
        dict: Notification processing results
    """
    try:
        from .services.ocr_fallback_handler import ManualReviewQueue
        from .services.notification_service import NotificationService
        from django.contrib.auth.models import User
        
        logger.info("Processing manual review queue notifications")
        
        # Get pending reviews grouped by user
        all_pending = ManualReviewQueue.get_pending_reviews(limit=1000)
        
        # Group by user
        user_reviews = {}
        for review in all_pending:
            user_id = review.get('user_id')  # Assuming this is available
            if user_id not in user_reviews:
                user_reviews[user_id] = []
            user_reviews[user_id].append(review)
        
        notification_count = 0
        error_count = 0
        
        for user_id, reviews in user_reviews.items():
            try:
                user = User.objects.get(id=user_id)
                
                # Send notification about pending reviews
                NotificationService.send_manual_review_notification(
                    user, len(reviews), reviews[:5]  # Send details for first 5
                )
                
                notification_count += 1
                logger.info(f"Sent manual review notification to user {user.username} for {len(reviews)} documents")
                
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found for manual review notification")
                error_count += 1
            except Exception as e:
                logger.error(f"Error sending notification to user {user_id}: {str(e)}")
                error_count += 1
        
        result = {
            'status': 'completed',
            'total_pending_reviews': len(all_pending),
            'notifications_sent': notification_count,
            'errors': error_count,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Manual review notifications completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error in manual review notification task: {str(exc)}", exc_info=True)
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


@shared_task
def update_vendor_independence_status():
    """
    Task to update vendor independence status and metrics
    """
    try:
        from .models import OCRResult
        from django.db.models import Count, Avg
        
        logger.info("Updating vendor independence status")
        
        # Calculate vendor independence metrics
        total_processed = OCRResult.objects.count()
        vendor_independent = OCRResult.objects.filter(vendor_independent=True).count()
        vendor_independence_percentage = (vendor_independent / total_processed * 100) if total_processed > 0 else 0
        
        # Calculate cost savings
        total_cost_savings = OCRResult.objects.aggregate(
            total_savings=Avg('cost_savings__savings_per_page')
        )['total_savings'] or 0
        
        # Update settings or cache with metrics
        from django.core.cache import cache
        cache.set('vendor_independence_metrics', {
            'total_processed': total_processed,
            'vendor_independent': vendor_independent,
            'vendor_independence_percentage': vendor_independence_percentage,
            'total_cost_savings': total_cost_savings,
            'last_updated': timezone.now().isoformat()
        }, timeout=3600)  # Cache for 1 hour
        
        logger.info(f"Vendor independence status updated: {vendor_independence_percentage:.1f}% independent")
        
        return {
            'status': 'success',
            'vendor_independence_percentage': vendor_independence_percentage,
            'total_cost_savings': total_cost_savings
        }
        
    except Exception as e:
        logger.error(f"Error updating vendor independence status: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def monitor_ensemble_engine_performance():
    """
    Task to monitor ensemble engine performance and health
    """
    try:
        from .services.ensemble_ocr_service import EnsembleOCRService
        
        logger.info("Monitoring ensemble engine performance")
        
        # Initialize ensemble service
        ensemble_config = getattr(settings, 'ENSEMBLE_OCR_CONFIG', {})
        ensemble_service = EnsembleOCRService(**ensemble_config)
        
        # Get engine status
        engine_status = ensemble_service.get_engine_status()
        
        # Get performance metrics
        performance_metrics = ensemble_service.get_performance_metrics()
        
        # Store metrics in cache
        from django.core.cache import cache
        cache.set('ensemble_engine_status', {
            'engine_status': engine_status,
            'performance_metrics': performance_metrics,
            'last_updated': timezone.now().isoformat()
        }, timeout=1800)  # Cache for 30 minutes
        
        logger.info("Ensemble engine performance monitoring completed")
        
        return {
            'status': 'success',
            'engines_available': len([e for e in engine_status.values() if e.get('available', False)]),
            'total_engines': len(engine_status)
        }
        
    except Exception as e:
        logger.error(f"Error monitoring ensemble engine performance: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def track_cost_savings():
    """
    Task to track and aggregate cost savings from ensemble OCR
    """
    try:
        from .models import OCRResult
        from django.db.models import Sum, Count, Avg
        
        logger.info("Tracking cost savings from ensemble OCR")
        
        # Calculate total cost savings
        cost_stats = OCRResult.objects.aggregate(
            total_documents=Count('id'),
            total_savings=Sum('cost_savings__savings_per_page'),
            avg_savings_per_document=Avg('cost_savings__savings_per_page')
        )
        
        # Calculate monthly savings
        from datetime import datetime, timedelta
        month_ago = timezone.now() - timedelta(days=30)
        monthly_stats = OCRResult.objects.filter(
            created_at__gte=month_ago
        ).aggregate(
            monthly_documents=Count('id'),
            monthly_savings=Sum('cost_savings__savings_per_page')
        )
        
        # Store in cache
        from django.core.cache import cache
        cache.set('cost_savings_metrics', {
            'total_documents': cost_stats['total_documents'] or 0,
            'total_savings': cost_stats['total_savings'] or 0,
            'avg_savings_per_document': cost_stats['avg_savings_per_document'] or 0,
            'monthly_documents': monthly_stats['monthly_documents'] or 0,
            'monthly_savings': monthly_stats['monthly_savings'] or 0,
            'last_updated': timezone.now().isoformat()
        }, timeout=3600)  # Cache for 1 hour
        
        logger.info(f"Cost savings tracking completed: ${cost_stats['total_savings']:.2f} total savings")
        
        return {
            'status': 'success',
            'total_savings': cost_stats['total_savings'] or 0,
            'monthly_savings': monthly_stats['monthly_savings'] or 0
        }
        
    except Exception as e:
        logger.error(f"Error tracking cost savings: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }