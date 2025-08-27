"""
OCR Fallback Handler Service

This service handles OCR processing failures and implements fallback mechanisms
to ensure robust document processing with automatic recovery strategies.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from ..models import OCRResult, DocumentUpload, OCREngine, OCRProcessingStep, OCRProcessingLog
from .ocr_service_factory import OCRServiceFactory
from .image_preprocessor import ImagePreprocessor
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of OCR processing failures"""
    ENGINE_ERROR = "engine_error"
    PREPROCESSING_ERROR = "preprocessing_error"
    EXTRACTION_ERROR = "extraction_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    RESOURCE_ERROR = "resource_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"


class ProcessingStrategy(Enum):
    """Processing strategies for different failure scenarios"""
    RETRY_SAME_ENGINE = "retry_same_engine"
    SWITCH_ENGINE = "switch_engine"
    RETRY_WITH_PREPROCESSING = "retry_with_preprocessing"
    PARTIAL_PROCESSING = "partial_processing"
    MANUAL_REVIEW = "manual_review"
    ABORT_PROCESSING = "abort_processing"


class OCRFallbackHandler:
    """
    Service for handling OCR processing failures and implementing fallback mechanisms
    """
    
    # Maximum retry attempts for different failure types
    MAX_RETRIES = {
        FailureType.ENGINE_ERROR: 2,
        FailureType.PREPROCESSING_ERROR: 3,
        FailureType.EXTRACTION_ERROR: 2,
        FailureType.VALIDATION_ERROR: 1,
        FailureType.TIMEOUT_ERROR: 1,
        FailureType.RESOURCE_ERROR: 2,
        FailureType.NETWORK_ERROR: 3,
        FailureType.UNKNOWN_ERROR: 1
    }
    
    # Retry delays in seconds
    RETRY_DELAYS = {
        FailureType.ENGINE_ERROR: 30,
        FailureType.PREPROCESSING_ERROR: 10,
        FailureType.EXTRACTION_ERROR: 20,
        FailureType.VALIDATION_ERROR: 5,
        FailureType.TIMEOUT_ERROR: 60,
        FailureType.RESOURCE_ERROR: 45,
        FailureType.NETWORK_ERROR: 15,
        FailureType.UNKNOWN_ERROR: 30
    }
    
    # Engine priority order for fallback
    ENGINE_PRIORITY = [
        'opensource',  # Primary engine
        'tesseract',   # Fallback 1
        'easyocr',     # Fallback 2
        'google',      # Legacy fallback
        'mock'         # Testing fallback
    ]
    
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.document_processor = DocumentProcessor()
        
        # Preprocessing strategies for retry attempts
        self.preprocessing_strategies = [
            {'deskew': True, 'denoise': True, 'enhance_contrast': True},
            {'deskew': True, 'denoise': False, 'enhance_contrast': True, 'sharpen': True},
            {'deskew': False, 'denoise': True, 'enhance_contrast': False, 'blur_reduction': True},
            {'minimal_processing': True}  # Minimal preprocessing as last resort
        ]
    
    def handle_processing_failure(self, document_id: int, error: Exception, 
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle OCR processing failure with automatic recovery strategies
        
        Args:
            document_id: ID of the document that failed processing
            error: The exception that occurred
            context: Additional context about the failure
            
        Returns:
            Dict containing recovery results and next steps
        """
        try:
            # Get document and current OCR result
            document = DocumentUpload.objects.get(id=document_id)
            ocr_result = OCRResult.objects.filter(document=document).first()
            
            # Classify the failure type
            failure_type = self._classify_failure(error, context)
            
            # Log the failure
            self._log_processing_failure(document, error, failure_type, context)
            
            # Determine processing strategy
            strategy = self._determine_strategy(document, failure_type, ocr_result)
            
            # Execute recovery strategy
            recovery_result = self._execute_recovery_strategy(
                document, strategy, failure_type, error, context
            )
            
            logger.info(f"Handled processing failure for document {document_id} with strategy {strategy.value}")
            
            return {
                'success': True,
                'failure_type': failure_type.value,
                'strategy': strategy.value,
                'recovery_result': recovery_result,
                'next_action': recovery_result.get('next_action', 'completed')
            }
            
        except Exception as e:
            logger.error(f"Failed to handle processing failure for document {document_id}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'next_action': 'manual_review'
            }
    
    def _classify_failure(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> FailureType:
        """Classify the type of failure based on error and context"""
        error_message = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Network-related errors
        if any(keyword in error_message for keyword in ['connection', 'network', 'timeout', 'unreachable']):
            return FailureType.NETWORK_ERROR
        
        # Resource-related errors
        if any(keyword in error_message for keyword in ['memory', 'disk', 'resource', 'quota']):
            return FailureType.RESOURCE_ERROR
        
        # Engine-specific errors
        if any(keyword in error_message for keyword in ['tesseract', 'easyocr', 'engine', 'ocr']):
            return FailureType.ENGINE_ERROR
        
        # Preprocessing errors
        if any(keyword in error_message for keyword in ['image', 'preprocessing', 'opencv', 'pillow']):
            return FailureType.PREPROCESSING_ERROR
        
        # Extraction errors
        if any(keyword in error_message for keyword in ['extraction', 'parsing', 'field', 'data']):
            return FailureType.EXTRACTION_ERROR
        
        # Validation errors
        if any(keyword in error_message for keyword in ['validation', 'invalid', 'format']):
            return FailureType.VALIDATION_ERROR
        
        # Timeout errors
        if 'timeout' in error_type or 'timeout' in error_message:
            return FailureType.TIMEOUT_ERROR
        
        return FailureType.UNKNOWN_ERROR
    
    def _determine_strategy(self, document: DocumentUpload, failure_type: FailureType, 
                          ocr_result: Optional[OCRResult]) -> ProcessingStrategy:
        """Determine the best recovery strategy based on failure type and history"""
        
        # Get failure history for this document
        failure_count = self._get_failure_count(document, failure_type)
        total_failures = self._get_total_failure_count(document)
        
        # Check if we've exceeded retry limits
        max_retries = self.MAX_RETRIES.get(failure_type, 1)
        
        if failure_count >= max_retries:
            if total_failures >= 5:  # Too many total failures
                return ProcessingStrategy.MANUAL_REVIEW
            else:
                # Try different approach
                if failure_type == FailureType.ENGINE_ERROR:
                    return ProcessingStrategy.SWITCH_ENGINE
                elif failure_type == FailureType.PREPROCESSING_ERROR:
                    return ProcessingStrategy.RETRY_WITH_PREPROCESSING
                else:
                    return ProcessingStrategy.PARTIAL_PROCESSING
        
        # Strategy based on failure type
        if failure_type == FailureType.ENGINE_ERROR:
            if failure_count == 0:
                return ProcessingStrategy.RETRY_SAME_ENGINE
            else:
                return ProcessingStrategy.SWITCH_ENGINE
        
        elif failure_type == FailureType.PREPROCESSING_ERROR:
            return ProcessingStrategy.RETRY_WITH_PREPROCESSING
        
        elif failure_type == FailureType.NETWORK_ERROR:
            return ProcessingStrategy.RETRY_SAME_ENGINE
        
        elif failure_type == FailureType.RESOURCE_ERROR:
            return ProcessingStrategy.RETRY_SAME_ENGINE
        
        elif failure_type == FailureType.EXTRACTION_ERROR:
            return ProcessingStrategy.PARTIAL_PROCESSING
        
        elif failure_type == FailureType.VALIDATION_ERROR:
            return ProcessingStrategy.PARTIAL_PROCESSING
        
        elif failure_type == FailureType.TIMEOUT_ERROR:
            return ProcessingStrategy.RETRY_WITH_PREPROCESSING  # Try with simpler preprocessing
        
        else:
            return ProcessingStrategy.RETRY_SAME_ENGINE
    
    def _execute_recovery_strategy(self, document: DocumentUpload, strategy: ProcessingStrategy,
                                 failure_type: FailureType, error: Exception,
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the determined recovery strategy"""
        
        try:
            if strategy == ProcessingStrategy.RETRY_SAME_ENGINE:
                return self._retry_same_engine(document, failure_type)
            
            elif strategy == ProcessingStrategy.SWITCH_ENGINE:
                return self._switch_engine(document, context)
            
            elif strategy == ProcessingStrategy.RETRY_WITH_PREPROCESSING:
                return self._retry_with_preprocessing(document, failure_type)
            
            elif strategy == ProcessingStrategy.PARTIAL_PROCESSING:
                return self._handle_partial_processing(document, error, context)
            
            elif strategy == ProcessingStrategy.MANUAL_REVIEW:
                return self._queue_for_manual_review(document, error, context)
            
            elif strategy == ProcessingStrategy.ABORT_PROCESSING:
                return self._abort_processing(document, error)
            
            else:
                logger.warning(f"Unknown recovery strategy: {strategy}")
                return self._queue_for_manual_review(document, error, context)
                
        except Exception as e:
            logger.error(f"Recovery strategy {strategy.value} failed: {e}", exc_info=True)
            return self._queue_for_manual_review(document, error, {'recovery_error': str(e)})
    
    def _retry_same_engine(self, document: DocumentUpload, failure_type: FailureType) -> Dict[str, Any]:
        """Retry processing with the same engine after a delay"""
        
        # Schedule retry with delay
        retry_delay = self.RETRY_DELAYS.get(failure_type, 30)
        retry_time = timezone.now() + timedelta(seconds=retry_delay)
        
        # Update document status
        document.processing_status = 'retry_scheduled'
        document.retry_count = (document.retry_count or 0) + 1
        document.next_retry_at = retry_time
        document.save(update_fields=['processing_status', 'retry_count', 'next_retry_at'])
        
        logger.info(f"Scheduled retry for document {document.id} in {retry_delay} seconds")
        
        return {
            'action': 'retry_scheduled',
            'retry_time': retry_time.isoformat(),
            'retry_delay': retry_delay,
            'next_action': 'retry_processing'
        }
    
    def _switch_engine(self, document: DocumentUpload, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Switch to a different OCR engine"""
        
        current_engine = context.get('current_engine', 'opensource') if context else 'opensource'
        
        # Find next available engine
        next_engine = self._get_next_available_engine(current_engine, document)
        
        if not next_engine:
            logger.warning(f"No alternative engines available for document {document.id}")
            return self._queue_for_manual_review(document, Exception("No alternative engines available"), context)
        
        try:
            # Update document to use new engine
            document.processing_status = 'retry_with_different_engine'
            document.retry_count = (document.retry_count or 0) + 1
            document.preferred_engine = next_engine
            document.save(update_fields=['processing_status', 'retry_count', 'preferred_engine'])
            
            # Try processing with new engine immediately
            ocr_service = OCRServiceFactory.get_service(next_engine)
            
            # Process document with new engine
            result = self._process_with_engine(document, ocr_service, next_engine)
            
            logger.info(f"Successfully switched to engine {next_engine} for document {document.id}")
            
            return {
                'action': 'engine_switched',
                'new_engine': next_engine,
                'previous_engine': current_engine,
                'processing_result': result,
                'next_action': 'completed' if result.get('success') else 'manual_review'
            }
            
        except Exception as e:
            logger.error(f"Failed to switch engine for document {document.id}: {e}")
            return self._queue_for_manual_review(document, e, context)
    
    def _retry_with_preprocessing(self, document: DocumentUpload, failure_type: FailureType) -> Dict[str, Any]:
        """Retry processing with different preprocessing settings"""
        
        current_attempt = document.retry_count or 0
        
        if current_attempt >= len(self.preprocessing_strategies):
            logger.warning(f"Exhausted preprocessing strategies for document {document.id}")
            return self._queue_for_manual_review(document, Exception("All preprocessing strategies failed"), None)
        
        try:
            # Get next preprocessing strategy
            preprocessing_config = self.preprocessing_strategies[current_attempt]
            
            # Update document status
            document.processing_status = 'retry_with_preprocessing'
            document.retry_count = current_attempt + 1
            document.save(update_fields=['processing_status', 'retry_count'])
            
            # Apply new preprocessing and retry
            result = self._process_with_preprocessing(document, preprocessing_config)
            
            logger.info(f"Retried document {document.id} with preprocessing strategy {current_attempt + 1}")
            
            return {
                'action': 'preprocessing_retry',
                'preprocessing_config': preprocessing_config,
                'attempt': current_attempt + 1,
                'processing_result': result,
                'next_action': 'completed' if result.get('success') else 'continue_retry'
            }
            
        except Exception as e:
            logger.error(f"Preprocessing retry failed for document {document.id}: {e}")
            return self._queue_for_manual_review(document, e, {'preprocessing_attempt': current_attempt})
    
    def _handle_partial_processing(self, document: DocumentUpload, error: Exception,
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle partial processing success with incomplete data"""
        
        try:
            # Get existing OCR result if any
            ocr_result = OCRResult.objects.filter(document=document).first()
            
            if not ocr_result:
                # No partial data available, queue for manual review
                return self._queue_for_manual_review(document, error, context)
            
            # Check if we have enough data for partial success
            extracted_data = ocr_result.extracted_data or {}
            confidence_score = ocr_result.confidence_score or 0.0
            
            # Define minimum requirements for partial success
            required_fields = ['numer_faktury', 'data_wystawienia', 'sprzedawca_nazwa']
            available_fields = [field for field in required_fields if extracted_data.get(field)]
            
            if len(available_fields) >= 2 and confidence_score >= 30.0:
                # Accept partial processing
                ocr_result.processing_status = 'partial_success'
                ocr_result.manual_verification_required = True
                ocr_result.processing_notes = f"Partial processing due to: {str(error)}"
                ocr_result.save(update_fields=['processing_status', 'manual_verification_required', 'processing_notes'])
                
                document.processing_status = 'partial_success'
                document.save(update_fields=['processing_status'])
                
                logger.info(f"Accepted partial processing for document {document.id} with {len(available_fields)} fields")
                
                return {
                    'action': 'partial_success',
                    'available_fields': available_fields,
                    'confidence_score': confidence_score,
                    'requires_manual_verification': True,
                    'next_action': 'manual_verification'
                }
            else:
                # Insufficient data for partial success
                return self._queue_for_manual_review(document, error, context)
                
        except Exception as e:
            logger.error(f"Failed to handle partial processing for document {document.id}: {e}")
            return self._queue_for_manual_review(document, error, context)
    
    def _queue_for_manual_review(self, document: DocumentUpload, error: Exception,
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Queue document for manual review"""
        
        try:
            # Update document status
            document.processing_status = 'manual_review_required'
            document.manual_review_reason = str(error)[:500]  # Limit length
            document.manual_review_queued_at = timezone.now()
            document.save(update_fields=[
                'processing_status', 'manual_review_reason', 'manual_review_queued_at'
            ])
            
            # Create or update OCR result for manual review
            ocr_result, created = OCRResult.objects.get_or_create(
                document=document,
                defaults={
                    'processing_status': 'manual_review_required',
                    'manual_verification_required': True,
                    'processing_notes': f"Queued for manual review: {str(error)}",
                    'confidence_score': 0.0
                }
            )
            
            if not created:
                ocr_result.processing_status = 'manual_review_required'
                ocr_result.manual_verification_required = True
                ocr_result.processing_notes = f"Queued for manual review: {str(error)}"
                ocr_result.save(update_fields=[
                    'processing_status', 'manual_verification_required', 'processing_notes'
                ])
            
            logger.info(f"Queued document {document.id} for manual review")
            
            return {
                'action': 'queued_for_manual_review',
                'reason': str(error),
                'queue_time': timezone.now().isoformat(),
                'next_action': 'manual_review'
            }
            
        except Exception as e:
            logger.error(f"Failed to queue document {document.id} for manual review: {e}")
            return {
                'action': 'queue_failed',
                'error': str(e),
                'next_action': 'system_error'
            }
    
    def _abort_processing(self, document: DocumentUpload, error: Exception) -> Dict[str, Any]:
        """Abort processing completely"""
        
        try:
            document.processing_status = 'processing_aborted'
            document.processing_error = str(error)[:500]
            document.save(update_fields=['processing_status', 'processing_error'])
            
            logger.warning(f"Aborted processing for document {document.id}: {error}")
            
            return {
                'action': 'processing_aborted',
                'reason': str(error),
                'next_action': 'aborted'
            }
            
        except Exception as e:
            logger.error(f"Failed to abort processing for document {document.id}: {e}")
            return {
                'action': 'abort_failed',
                'error': str(e),
                'next_action': 'system_error'
            }
    
    def _get_next_available_engine(self, current_engine: str, document: DocumentUpload) -> Optional[str]:
        """Get the next available OCR engine for fallback"""
        
        try:
            current_index = self.ENGINE_PRIORITY.index(current_engine)
        except ValueError:
            current_index = -1
        
        # Try engines after current one
        for engine in self.ENGINE_PRIORITY[current_index + 1:]:
            if self._is_engine_available(engine):
                return engine
        
        # Try engines before current one
        for engine in self.ENGINE_PRIORITY[:current_index]:
            if self._is_engine_available(engine):
                return engine
        
        return None
    
    def _is_engine_available(self, engine_name: str) -> bool:
        """Check if an OCR engine is available"""
        try:
            service = OCRServiceFactory.get_service(engine_name)
            return service is not None
        except Exception:
            return False
    
    def _process_with_engine(self, document: DocumentUpload, ocr_service, engine_name: str) -> Dict[str, Any]:
        """Process document with specific OCR engine"""
        try:
            # Read document file
            with open(document.file.path, 'rb') as f:
                file_content = f.read()
            
            # Process with OCR service
            result = ocr_service.process_invoice(file_content, document.file_type)
            
            # Update or create OCR result
            ocr_result, created = OCRResult.objects.get_or_create(
                document=document,
                defaults={
                    'extracted_data': result.get('extracted_data', {}),
                    'confidence_score': result.get('confidence_score', 0.0),
                    'processing_status': 'completed',
                    'processor_version': f"{engine_name}_fallback"
                }
            )
            
            if not created:
                ocr_result.extracted_data = result.get('extracted_data', {})
                ocr_result.confidence_score = result.get('confidence_score', 0.0)
                ocr_result.processing_status = 'completed'
                ocr_result.processor_version = f"{engine_name}_fallback"
                ocr_result.save()
            
            return {'success': True, 'result': result}
            
        except Exception as e:
            logger.error(f"Failed to process document {document.id} with engine {engine_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_with_preprocessing(self, document: DocumentUpload, 
                                  preprocessing_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process document with specific preprocessing configuration"""
        try:
            # Read document file
            with open(document.file.path, 'rb') as f:
                file_content = f.read()
            
            # Apply preprocessing
            processed_content = self.preprocessor.preprocess_document(
                file_content, document.file_type, **preprocessing_config
            )
            
            # Process with current OCR service
            ocr_service = OCRServiceFactory.get_service()
            result = ocr_service.process_invoice(processed_content, document.file_type)
            
            # Update OCR result
            ocr_result, created = OCRResult.objects.get_or_create(
                document=document,
                defaults={
                    'extracted_data': result.get('extracted_data', {}),
                    'confidence_score': result.get('confidence_score', 0.0),
                    'processing_status': 'completed',
                    'preprocessing_applied': preprocessing_config
                }
            )
            
            if not created:
                ocr_result.extracted_data = result.get('extracted_data', {})
                ocr_result.confidence_score = result.get('confidence_score', 0.0)
                ocr_result.processing_status = 'completed'
                ocr_result.preprocessing_applied = preprocessing_config
                ocr_result.save()
            
            return {'success': True, 'result': result}
            
        except Exception as e:
            logger.error(f"Failed to process document {document.id} with preprocessing: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_failure_count(self, document: DocumentUpload, failure_type: FailureType) -> int:
        """Get the number of failures of a specific type for a document"""
        return OCRProcessingLog.objects.filter(
            document=document,
            level='ERROR',
            details__failure_type=failure_type.value
        ).count()
    
    def _get_total_failure_count(self, document: DocumentUpload) -> int:
        """Get the total number of processing failures for a document"""
        return OCRProcessingLog.objects.filter(
            document=document,
            level='ERROR'
        ).count()
    
    def _log_processing_failure(self, document: DocumentUpload, error: Exception,
                              failure_type: FailureType, context: Optional[Dict[str, Any]] = None):
        """Log processing failure for debugging and monitoring"""
        try:
            OCRProcessingLog.objects.create(
                document=document,
                level='ERROR',
                message=f'Processing failed: {str(error)}',
                details={
                    'error_message': str(error),
                    'error_type': type(error).__name__,
                    'failure_type': failure_type.value,
                    'context': context or {},
                    'timestamp': timezone.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to log processing failure: {e}")


class ManualReviewQueue:
    """
    Service for managing documents that require manual review
    """
    
    @staticmethod
    def get_pending_reviews(user=None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get documents pending manual review"""
        
        query = DocumentUpload.objects.filter(
            processing_status='manual_review_required'
        ).select_related('user').prefetch_related('ocrresult_set')
        
        if user:
            query = query.filter(user=user)
        
        documents = query.order_by('manual_review_queued_at')[:limit]
        
        review_items = []
        for doc in documents:
            ocr_result = doc.ocrresult_set.first()
            
            review_items.append({
                'document_id': doc.id,
                'filename': doc.filename,
                'uploaded_at': doc.uploaded_at,
                'queued_at': doc.manual_review_queued_at,
                'reason': doc.manual_review_reason,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'confidence_score': ocr_result.confidence_score if ocr_result else 0.0,
                'extracted_data': ocr_result.extracted_data if ocr_result else {},
                'processing_attempts': doc.retry_count or 0
            })
        
        return review_items
    
    @staticmethod
    def complete_manual_review(document_id: int, reviewer_user, 
                             corrected_data: Dict[str, Any], 
                             approved: bool = True) -> Dict[str, Any]:
        """Complete manual review of a document"""
        
        try:
            with transaction.atomic():
                document = DocumentUpload.objects.get(id=document_id)
                ocr_result = OCRResult.objects.filter(document=document).first()
                
                if not ocr_result:
                    raise ValueError("No OCR result found for document")
                
                if approved:
                    # Update OCR result with corrected data
                    ocr_result.extracted_data = corrected_data
                    ocr_result.processing_status = 'manually_verified'
                    ocr_result.manual_verification_required = False
                    ocr_result.manually_verified_by = reviewer_user
                    ocr_result.manually_verified_at = timezone.now()
                    ocr_result.save()
                    
                    # Update document status
                    document.processing_status = 'completed'
                    document.manual_review_completed_at = timezone.now()
                    document.manual_review_completed_by = reviewer_user
                    document.save()
                    
                    # Log completion
                    OCRProcessingLog.objects.create(
                        document=document,
                        level='INFO',
                        message=f'Manual review completed by {reviewer_user.username}',
                        details={
                            'reviewer': reviewer_user.username,
                            'approved': True,
                            'corrections_made': True
                        }
                    )
                    
                    return {'success': True, 'action': 'approved_and_corrected'}
                    
                else:
                    # Reject the document
                    document.processing_status = 'rejected'
                    document.manual_review_completed_at = timezone.now()
                    document.manual_review_completed_by = reviewer_user
                    document.save()
                    
                    ocr_result.processing_status = 'rejected'
                    ocr_result.save()
                    
                    # Log rejection
                    OCRProcessingLog.objects.create(
                        document=document,
                        level='WARNING',
                        message=f'Manual review rejected by {reviewer_user.username}',
                        details={
                            'reviewer': reviewer_user.username,
                            'approved': False,
                            'rejection_reason': 'Manual review rejected'
                        }
                    )
                    
                    return {'success': True, 'action': 'rejected'}
                    
        except Exception as e:
            logger.error(f"Failed to complete manual review for document {document_id}: {e}")
            return {'success': False, 'error': str(e)}