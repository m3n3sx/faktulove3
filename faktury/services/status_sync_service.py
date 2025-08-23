"""
Status Synchronization Service for OCR Processing

This service handles the synchronization of status between DocumentUpload and OCRResult models,
providing unified status information for the frontend and ensuring consistent state management.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from ..models import DocumentUpload, OCRResult

logger = logging.getLogger(__name__)


class StatusSyncError(Exception):
    """Custom exception for status synchronization errors"""
    pass


class StatusSyncService:
    """Service for synchronizing status between DocumentUpload and OCRResult models"""
    
    # Status mapping from OCRResult to DocumentUpload
    OCR_TO_DOCUMENT_STATUS_MAP = {
        'pending': 'processing',
        'processing': 'processing', 
        'completed': 'completed',
        'failed': 'failed',
        'manual_review': 'completed',  # Document processing is complete, just needs review
    }
    
    # Combined status for frontend display
    COMBINED_STATUS_MAP = {
        # DocumentUpload status -> OCRResult status -> Combined status
        ('uploaded', None): {
            'status': 'uploaded',
            'display': 'Przesłano',
            'description': 'Dokument został przesłany i oczekuje na przetwarzanie',
            'progress': 10,
            'can_retry': False,
            'is_final': False
        },
        ('queued', None): {
            'status': 'queued',
            'display': 'W kolejce',
            'description': 'Dokument oczekuje na rozpoczęcie przetwarzania OCR',
            'progress': 15,
            'can_retry': False,
            'is_final': False
        },
        ('processing', 'pending'): {
            'status': 'queued',
            'display': 'W kolejce',
            'description': 'Dokument oczekuje na rozpoczęcie przetwarzania OCR',
            'progress': 20,
            'can_retry': False,
            'is_final': False
        },
        ('processing', 'processing'): {
            'status': 'processing',
            'display': 'Przetwarzanie',
            'description': 'Trwa przetwarzanie OCR dokumentu',
            'progress': 50,
            'can_retry': False,
            'is_final': False
        },
        ('completed', 'completed'): {
            'status': 'ocr_completed',
            'display': 'OCR zakończone',
            'description': 'Przetwarzanie OCR zostało zakończone pomyślnie',
            'progress': 80,
            'can_retry': False,
            'is_final': False
        },
        ('completed', 'manual_review'): {
            'status': 'manual_review',
            'display': 'Wymaga przeglądu',
            'description': 'OCR zakończone, dane wymagają weryfikacji manualnej',
            'progress': 90,
            'can_retry': False,
            'is_final': False
        },
        ('failed', 'failed'): {
            'status': 'failed',
            'display': 'Błąd przetwarzania',
            'description': 'Wystąpił błąd podczas przetwarzania dokumentu',
            'progress': 0,
            'can_retry': True,
            'is_final': True
        },
        ('cancelled', None): {
            'status': 'cancelled',
            'display': 'Anulowano',
            'description': 'Przetwarzanie dokumentu zostało anulowane',
            'progress': 0,
            'can_retry': False,
            'is_final': True
        },
        # Additional status combinations for better coverage
        ('processing', None): {
            'status': 'processing',
            'display': 'Przetwarzanie',
            'description': 'Dokument jest przetwarzany',
            'progress': 30,
            'can_retry': False,
            'is_final': False
        },
        ('completed', None): {
            'status': 'completed',
            'display': 'Zakończone',
            'description': 'Przetwarzanie zostało zakończone',
            'progress': 100,
            'can_retry': False,
            'is_final': True
        },
        ('failed', None): {
            'status': 'failed',
            'display': 'Błąd przetwarzania',
            'description': 'Wystąpił błąd podczas przetwarzania dokumentu',
            'progress': 0,
            'can_retry': True,
            'is_final': True
        },
        ('ocr_completed', None): {
            'status': 'ocr_completed',
            'display': 'OCR zakończone',
            'description': 'Przetwarzanie OCR zostało zakończone',
            'progress': 80,
            'can_retry': False,
            'is_final': False
        },
        ('integration_processing', None): {
            'status': 'integration_processing',
            'display': 'Tworzenie faktury',
            'description': 'Trwa tworzenie faktury na podstawie OCR',
            'progress': 90,
            'can_retry': False,
            'is_final': False
        },
        ('manual_review', None): {
            'status': 'manual_review',
            'display': 'Wymaga przeglądu',
            'description': 'Dokument wymaga weryfikacji manualnej',
            'progress': 95,
            'can_retry': False,
            'is_final': False
        }
    }
    
    @classmethod
    def sync_document_status(cls, document_upload: DocumentUpload) -> bool:
        """
        Update DocumentUpload status based on its OCRResult status
        
        Args:
            document_upload: DocumentUpload instance to sync
            
        Returns:
            bool: True if status was updated, False otherwise
            
        Raises:
            StatusSyncError: If synchronization fails
        """
        try:
            with transaction.atomic():
                # Get the related OCRResult if it exists
                ocr_result = None
                try:
                    ocr_result = document_upload.ocrresult
                except ObjectDoesNotExist:
                    # No OCRResult yet, document should remain in current status
                    logger.debug(f"No OCRResult found for document {document_upload.id}")
                    return False
                
                # Determine new status based on OCR result
                ocr_status = ocr_result.processing_status
                new_document_status = cls.OCR_TO_DOCUMENT_STATUS_MAP.get(ocr_status)
                
                if not new_document_status:
                    logger.warning(f"Unknown OCR status '{ocr_status}' for document {document_upload.id}")
                    return False
                
                # Always update document status to match OCR status, regardless of current document status
                # This ensures proper synchronization even if document status is out of sync
                if document_upload.processing_status != new_document_status:
                    old_status = document_upload.processing_status
                    document_upload.processing_status = new_document_status
                    
                    # Update timestamps based on new status
                    if new_document_status == 'processing' and not document_upload.processing_started_at:
                        document_upload.processing_started_at = timezone.now()
                    elif new_document_status in ['completed', 'failed'] and not document_upload.processing_completed_at:
                        document_upload.processing_completed_at = timezone.now()
                    
                    # Copy error message if OCR failed
                    if new_document_status == 'failed' and ocr_result.error_message:
                        document_upload.error_message = ocr_result.error_message
                    
                    document_upload.save(update_fields=[
                        'processing_status', 
                        'processing_started_at', 
                        'processing_completed_at',
                        'error_message'
                    ])
                    
                    logger.info(f"Updated document {document_upload.id} status: {old_status} -> {new_document_status}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to sync status for document {document_upload.id}: {str(e)}", exc_info=True)
            raise StatusSyncError(f"Status synchronization failed: {str(e)}")
    
    @classmethod
    def get_combined_status(cls, document_upload: DocumentUpload) -> Dict[str, Any]:
        """
        Get unified status information for frontend display
        
        Args:
            document_upload: DocumentUpload instance
            
        Returns:
            Dict containing unified status information
        """
        try:
            # Get OCR result status if available
            ocr_status = None
            ocr_result = None
            try:
                ocr_result = document_upload.ocrresult
                ocr_status = ocr_result.processing_status
            except ObjectDoesNotExist:
                pass
            
            # Get combined status info
            status_key = (document_upload.processing_status, ocr_status)
            status_info = cls.COMBINED_STATUS_MAP.get(status_key)
            
            if not status_info:
                # Fallback for unknown status combinations
                status_info = {
                    'status': document_upload.processing_status,
                    'display': document_upload.get_processing_status_display(),
                    'description': 'Status nieznany',
                    'progress': 0,
                    'can_retry': False,
                    'is_final': False
                }
                logger.warning(f"Unknown status combination for document {document_upload.id}: {status_key}")
            
            # Add additional metadata
            result = status_info.copy()
            result.update({
                'document_id': document_upload.id,
                'document_status': document_upload.processing_status,
                'ocr_status': ocr_status,
                'upload_timestamp': document_upload.upload_timestamp.isoformat(),
                'processing_started_at': document_upload.processing_started_at.isoformat() if document_upload.processing_started_at else None,
                'processing_completed_at': document_upload.processing_completed_at.isoformat() if document_upload.processing_completed_at else None,
                'error_message': document_upload.error_message,
                'has_ocr_result': ocr_result is not None,
            })
            
            # Add OCR-specific information if available
            if ocr_result:
                result.update({
                    'confidence_score': ocr_result.confidence_score,
                    'auto_created_faktura': ocr_result.auto_created_faktura,
                    'has_faktura': ocr_result.faktura is not None,
                    'faktura_id': ocr_result.faktura.id if ocr_result.faktura else None,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get combined status for document {document_upload.id}: {str(e)}", exc_info=True)
            # Return safe fallback
            return {
                'status': 'error',
                'display': 'Błąd systemu',
                'description': 'Wystąpił błąd podczas pobierania statusu',
                'progress': 0,
                'can_retry': True,
                'is_final': False,
                'document_id': document_upload.id,
                'error_message': str(e)
            }
    
    @classmethod
    def get_status_display_data(cls, document_upload: DocumentUpload) -> Dict[str, Any]:
        """
        Get status display data optimized for templates
        
        Args:
            document_upload: DocumentUpload instance
            
        Returns:
            Dict containing display-optimized status data
        """
        combined_status = cls.get_combined_status(document_upload)
        
        # Add template-friendly data
        display_data = {
            'status_class': cls._get_status_css_class(combined_status['status']),
            'progress_class': cls._get_progress_css_class(combined_status['progress']),
            'icon_class': cls._get_status_icon_class(combined_status['status']),
            'show_spinner': combined_status['status'] in ['processing', 'queued'],
            'show_retry_button': combined_status['can_retry'],
            'show_progress_bar': not combined_status['is_final'],
        }
        
        # Merge with combined status
        display_data.update(combined_status)
        
        return display_data
    
    @classmethod
    def get_processing_progress(cls, document_upload: DocumentUpload) -> int:
        """
        Get processing progress percentage
        
        Args:
            document_upload: DocumentUpload instance
            
        Returns:
            int: Progress percentage (0-100)
        """
        combined_status = cls.get_combined_status(document_upload)
        return combined_status.get('progress', 0)
    
    @classmethod
    def _get_status_css_class(cls, status: str) -> str:
        """Get CSS class for status display"""
        status_classes = {
            'uploaded': 'badge-secondary',
            'queued': 'badge-info',
            'processing': 'badge-warning',
            'ocr_completed': 'badge-success',
            'manual_review': 'badge-warning',
            'failed': 'badge-danger',
            'cancelled': 'badge-secondary',
            'error': 'badge-danger'
        }
        return status_classes.get(status, 'badge-secondary')
    
    @classmethod
    def _get_progress_css_class(cls, progress: int) -> str:
        """Get CSS class for progress bar"""
        if progress is None or progress == 0:
            return 'progress-bar-danger'
        elif progress < 50:
            return 'progress-bar-info'
        elif progress < 80:
            return 'progress-bar-warning'
        else:
            return 'progress-bar-success'
    
    @classmethod
    def _get_status_icon_class(cls, status: str) -> str:
        """Get icon class for status display"""
        icon_classes = {
            'uploaded': 'ri-upload-line',
            'queued': 'ri-time-line',
            'processing': 'ri-loader-line',
            'ocr_completed': 'ri-check-line',
            'manual_review': 'ri-eye-line',
            'failed': 'ri-error-warning-line',
            'cancelled': 'ri-close-line',
            'error': 'ri-alert-line'
        }
        return icon_classes.get(status, 'ri-question-line')
    
    @classmethod
    def bulk_sync_documents(cls, document_uploads: list) -> Dict[str, int]:
        """
        Bulk synchronize status for multiple documents
        
        Args:
            document_uploads: List of DocumentUpload instances
            
        Returns:
            Dict with sync statistics
        """
        stats = {
            'total': len(document_uploads),
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        for document in document_uploads:
            try:
                if cls.sync_document_status(document):
                    stats['updated'] += 1
                else:
                    stats['skipped'] += 1
            except StatusSyncError:
                stats['failed'] += 1
        
        logger.info(f"Bulk sync completed: {stats}")
        return stats