"""
Django signals for OCR integration

Handles automatic processing triggers and integration between
DocumentUpload, OCRResult, and Faktura models.
"""

import logging
from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import DocumentUpload, OCRResult, Faktura

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DocumentUpload)
def handle_document_upload_created(sender, instance, created, **kwargs):
    """
    Handle DocumentUpload creation
    
    Triggers OCR processing when document is uploaded
    """
    if created:
        logger.info(f"New document uploaded: {instance.id} - {instance.original_filename}")
        
        # Start OCR processing automatically
        try:
            from .tasks import process_document_ocr_task
            # Update status to queued before starting async task
            with transaction.atomic():
                instance.processing_status = 'queued'
                instance.save(update_fields=['processing_status'])
            
            process_document_ocr_task.delay(instance.id)
            logger.info(f"Queued OCR processing task for document {instance.id}")
            
        except ImportError:
            # Fallback to synchronous processing
            logger.warning("Celery not available, processing OCR synchronously")
            
            try:
                with transaction.atomic():
                    from .services.ocr_service_factory import get_ocr_service
                    from .services.file_upload_service import FileUploadService
                    from .models import OCRResult
                    
                    # Mark as processing
                    instance.mark_processing_started()
                    
                    # Get file content and process
                    file_service = FileUploadService()
                    file_content = file_service.get_file_content(instance)
                    
                    ocr_service = get_ocr_service()
                    extracted_data = ocr_service.process_invoice(file_content, instance.content_type)
                    
                    # Create OCRResult - this will trigger the OCR result signals
                    ocr_result = OCRResult.objects.create(
                        document=instance,
                        raw_text=extracted_data.get('raw_text', ''),
                        extracted_data=extracted_data,
                        confidence_score=extracted_data.get('confidence_score', 0.0),
                        processing_time=extracted_data.get('processing_time', 0.0),
                        processor_version=extracted_data.get('processor_version', 'unknown'),
                        processing_location=extracted_data.get('processing_location', 'unknown'),
                        processing_status='pending'
                    )
                    
                    logger.info(f"Synchronous OCR processing completed for document {instance.id}")
                    
            except Exception as e:
                logger.error(f"Synchronous OCR processing failed for document {instance.id}: {str(e)}")
                try:
                    with transaction.atomic():
                        instance.mark_processing_failed(str(e))
                except Exception as save_error:
                    logger.error(f"Failed to mark document {instance.id} as failed: {str(save_error)}")


@receiver(post_save, sender=OCRResult)
def handle_ocr_result_created(sender, instance, created, **kwargs):
    """
    Handle OCRResult creation and updates
    
    Automatically processes new OCR results and synchronizes DocumentUpload status
    """
    try:
        with transaction.atomic():
            if created:
                logger.info(f"New OCR result created: {instance.id} with confidence {instance.confidence_score:.1f}%")
                
                # Sync document status immediately after OCR result creation
                try:
                    from .services.status_sync_service import StatusSyncService
                    StatusSyncService.sync_document_status(instance.document)
                    logger.debug(f"Synced document status for OCR result {instance.id}")
                except Exception as sync_error:
                    logger.error(f"Failed to sync document status for OCR result {instance.id}: {str(sync_error)}")
                    # Don't fail the entire operation if sync fails
                
                # Trigger automatic processing for new OCR results
                if instance.processing_status == 'pending':
                    logger.info(f"Triggering automatic processing for OCR result {instance.id}")
                    
                    # Always use synchronous processing for now (Celery may not be running)
                    try:
                        from .services.ocr_integration import process_ocr_result
                        logger.info(f"Processing OCR result {instance.id} synchronously")
                        process_ocr_result(instance.id)
                        logger.info(f"OCR result {instance.id} processing completed")
                    except Exception as e:
                        logger.error(f"OCR result {instance.id} processing failed: {str(e)}")
                        instance.mark_processing_failed(str(e))
                        # Sync status after marking as failed
                        try:
                            from .services.status_sync_service import StatusSyncService
                            StatusSyncService.sync_document_status(instance.document)
                        except Exception as sync_error:
                            logger.error(f"Failed to sync document status after OCR failure: {str(sync_error)}")
                
            else:
                # Handle status changes for existing OCR results
                logger.debug(f"OCR result {instance.id} updated with status: {instance.processing_status}")
                
                # Always sync document status when OCR result status changes
                try:
                    from .services.status_sync_service import StatusSyncService
                    status_updated = StatusSyncService.sync_document_status(instance.document)
                    if status_updated:
                        logger.info(f"Document status synced for OCR result {instance.id} status change")
                except Exception as sync_error:
                    logger.error(f"Failed to sync document status for OCR result {instance.id} update: {str(sync_error)}")
                
                # Log specific status transitions
                if instance.processing_status == 'completed' and instance.faktura:
                    logger.info(f"OCR result {instance.id} completed with Faktura {instance.faktura.numer}")
                    
                elif instance.processing_status == 'manual_review':
                    logger.info(f"OCR result {instance.id} requires manual review (confidence: {instance.confidence_score:.1f}%)")
                    
                    # TODO: Send notification to user about manual review requirement
                    # This could trigger an email, in-app notification, etc.
                    
                elif instance.processing_status == 'failed':
                    logger.error(f"OCR result {instance.id} processing failed: {instance.error_message}")
                    
                    # TODO: Send error notification to user
                    # This could trigger an email, in-app notification, etc.
                    
    except Exception as e:
        logger.error(f"Critical error in OCR result signal handler for {instance.id}: {str(e)}", exc_info=True)
        # Re-raise to ensure the error is visible
        raise


@receiver(post_save, sender=OCRResult)
def handle_ocr_result_status_change(sender, instance, created, **kwargs):
    """
    Handle OCRResult status changes specifically for status synchronization
    
    This signal ensures DocumentUpload status is always in sync with OCRResult status
    """
    if not created:  # Only handle updates, not creation (handled by handle_ocr_result_created)
        try:
            # Check if processing_status field was actually updated
            if hasattr(instance, '_state') and instance._state.adding:
                return  # Skip if this is actually a creation
            
            # Get the previous status from database to detect changes
            try:
                old_instance = OCRResult.objects.get(pk=instance.pk)
                if old_instance.processing_status == instance.processing_status:
                    return  # No status change, skip synchronization
            except OCRResult.DoesNotExist:
                return  # Instance doesn't exist in DB yet
            
            logger.debug(f"OCR result {instance.id} status changed to: {instance.processing_status}")
            
            # Perform atomic status synchronization
            with transaction.atomic():
                try:
                    from .services.status_sync_service import StatusSyncService
                    status_updated = StatusSyncService.sync_document_status(instance.document)
                    
                    if status_updated:
                        logger.info(f"Document {instance.document.id} status synchronized after OCR result {instance.id} status change")
                    else:
                        logger.debug(f"Document {instance.document.id} status already in sync with OCR result {instance.id}")
                        
                except Exception as sync_error:
                    logger.error(f"Failed to sync document status for OCR result {instance.id} status change: {str(sync_error)}")
                    # Don't re-raise to avoid breaking the OCR result save operation
                    
        except Exception as e:
            logger.error(f"Error in OCR result status change handler for {instance.id}: {str(e)}", exc_info=True)


@receiver(post_save, sender=Faktura)
def handle_faktura_created_from_ocr(sender, instance, created, **kwargs):
    """
    Handle Faktura creation from OCR
    
    Updates related OCR result and performs additional processing
    """
    if created and instance.source_document:
        logger.info(f"Faktura {instance.numer} created from OCR document {instance.source_document.id}")
        
        # Update OCR result if not already linked
        try:
            with transaction.atomic():
                ocr_result = instance.source_document.ocrresult
                if not ocr_result.faktura:
                    ocr_result.faktura = instance
                    ocr_result.auto_created_faktura = True
                    # Mark as completed if not already
                    if ocr_result.processing_status != 'completed':
                        ocr_result.processing_status = 'completed'
                    ocr_result.save(update_fields=['faktura', 'auto_created_faktura', 'processing_status'])
                    
                    # Sync document status after linking faktura
                    try:
                        from .services.status_sync_service import StatusSyncService
                        StatusSyncService.sync_document_status(instance.source_document)
                        logger.debug(f"Synced document status after Faktura {instance.numer} creation")
                    except Exception as sync_error:
                        logger.error(f"Failed to sync document status after Faktura creation: {str(sync_error)}")
                
        except OCRResult.DoesNotExist:
            logger.warning(f"No OCR result found for Faktura {instance.numer} source document")
        except Exception as e:
            logger.error(f"Error linking Faktura {instance.numer} to OCR result: {str(e)}", exc_info=True)
        
        # TODO: Additional processing for OCR-created invoices
        # - Send confirmation notification
        # - Update processing statistics
        # - Trigger additional workflows


@receiver(pre_delete, sender=Faktura)
def handle_faktura_deletion(sender, instance, **kwargs):
    """
    Handle Faktura deletion
    
    Updates related OCR result status when Faktura is deleted
    """
    if instance.source_document:
        try:
            with transaction.atomic():
                ocr_result = instance.source_document.ocrresult
                if ocr_result.faktura == instance:
                    # Reset OCR result status to allow recreation
                    ocr_result.faktura = None
                    ocr_result.auto_created_faktura = False
                    ocr_result.processing_status = 'completed'  # Keep as completed but unlinked
                    ocr_result.save(update_fields=['faktura', 'auto_created_faktura', 'processing_status'])
                    
                    # Sync document status after unlinking faktura
                    try:
                        from .services.status_sync_service import StatusSyncService
                        StatusSyncService.sync_document_status(instance.source_document)
                        logger.debug(f"Synced document status after Faktura {instance.numer} deletion")
                    except Exception as sync_error:
                        logger.error(f"Failed to sync document status after Faktura deletion: {str(sync_error)}")
                    
                    logger.info(f"Reset OCR result {ocr_result.id} after Faktura {instance.numer} deletion")
                    
        except OCRResult.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error handling Faktura {instance.numer} deletion: {str(e)}", exc_info=True)


@receiver(post_save, sender=OCRResult)
def update_faktura_ocr_fields(sender, instance, created, **kwargs):
    """
    Update Faktura OCR fields when OCRResult is updated
    
    Keeps OCR metadata in sync between OCRResult and Faktura
    """
    if instance.faktura and not created:
        try:
            with transaction.atomic():
                # Update Faktura OCR fields
                faktura = instance.faktura
                updated_fields = []
                
                if faktura.ocr_confidence != instance.confidence_score:
                    faktura.ocr_confidence = instance.confidence_score
                    updated_fields.append('ocr_confidence')
                
                if faktura.ocr_processing_time != instance.processing_time:
                    faktura.ocr_processing_time = instance.processing_time
                    updated_fields.append('ocr_processing_time')
                
                # Update manual verification requirement based on current confidence
                manual_verification_required = instance.needs_human_review
                if faktura.manual_verification_required != manual_verification_required:
                    faktura.manual_verification_required = manual_verification_required
                    updated_fields.append('manual_verification_required')
                
                if updated_fields:
                    faktura.save(update_fields=updated_fields)
                    logger.debug(f"Updated Faktura {faktura.numer} OCR fields: {updated_fields}")
                    
        except Exception as e:
            logger.error(f"Error updating Faktura OCR fields for OCR result {instance.id}: {str(e)}", exc_info=True)


# Signal connection helper for apps.py
def connect_ocr_signals():
    """
    Helper function to ensure signals are connected
    Call this from apps.py ready() method
    """
    logger.info("OCR integration signals connected")


# Disconnect signals helper for testing
def disconnect_ocr_signals():
    """
    Helper function to disconnect signals (useful for testing)
    """
    post_save.disconnect(handle_document_upload_created, sender=DocumentUpload)
    post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
    post_save.disconnect(handle_ocr_result_status_change, sender=OCRResult)
    post_save.disconnect(handle_faktura_created_from_ocr, sender=Faktura)
    pre_delete.disconnect(handle_faktura_deletion, sender=Faktura)
    post_save.disconnect(update_faktura_ocr_fields, sender=OCRResult)
    
    logger.info("OCR integration signals disconnected")