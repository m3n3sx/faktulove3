"""
OCR Integration Service for FaktuLove

This service handles the integration between OCR results and Faktura creation,
including automatic invoice generation and manual verification workflows.
"""

import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, Tuple
from django.db import transaction, models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import OCRResult, Faktura, Kontrahent, Firma, PozycjaFaktury, OCRValidation
from .status_sync_service import StatusSyncService, StatusSyncError

logger = logging.getLogger(__name__)


class OCRIntegrationError(Exception):
    """Custom exception for OCR integration errors"""
    pass


class OCRDataValidator:
    """Validates OCR extracted data before creating Faktura"""
    
    REQUIRED_FIELDS = [
        'numer_faktury',
        'data_wystawienia', 
        'data_sprzedazy',
        'sprzedawca_nazwa',
        'nabywca_nazwa',
        'pozycje'
    ]
    
    @classmethod
    def validate_ocr_data(cls, extracted_data: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate OCR extracted data
        
        Returns:
            Tuple[bool, list]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if not extracted_data.get(field):
                errors.append(f"Brak wymaganego pola: {field}")
        
        # Validate dates
        if extracted_data.get('data_wystawienia'):
            if not cls._validate_date(extracted_data['data_wystawienia']):
                errors.append("Nieprawidłowa data wystawienia")
        
        if extracted_data.get('data_sprzedazy'):
            if not cls._validate_date(extracted_data['data_sprzedazy']):
                errors.append("Nieprawidłowa data sprzedaży")
        
        # Validate positions
        pozycje = extracted_data.get('pozycje', [])
        if not isinstance(pozycje, list) or len(pozycje) == 0:
            errors.append("Brak pozycji na fakturze")
        else:
            for i, pozycja in enumerate(pozycje):
                pos_errors = cls._validate_position(pozycja, i + 1)
                errors.extend(pos_errors)
        
        # Validate amounts
        if extracted_data.get('suma_brutto'):
            try:
                Decimal(str(extracted_data['suma_brutto']))
            except (InvalidOperation, ValueError):
                errors.append("Nieprawidłowa suma brutto")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_date(date_str: str) -> bool:
        """Validate date string"""
        try:
            if isinstance(date_str, str):
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
                    try:
                        datetime.strptime(date_str, fmt)
                        return True
                    except ValueError:
                        continue
                return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def _validate_position(pozycja: Dict[str, Any], position_num: int) -> list:
        """Validate single invoice position"""
        errors = []
        required_pos_fields = ['nazwa', 'ilosc', 'cena_netto', 'vat']
        
        for field in required_pos_fields:
            if not pozycja.get(field):
                errors.append(f"Pozycja {position_num}: brak pola {field}")
        
        # Validate numeric fields
        for field in ['ilosc', 'cena_netto']:
            if pozycja.get(field):
                try:
                    Decimal(str(pozycja[field]))
                except (InvalidOperation, ValueError):
                    errors.append(f"Pozycja {position_num}: nieprawidłowa wartość {field}")
        
        return errors


class FakturaCreator:
    """Creates Faktura from OCR data"""
    
    def __init__(self, user: User):
        self.user = user
    
    def create_from_ocr(self, ocr_result: OCRResult) -> Faktura:
        """
        Create Faktura from OCR result
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            Faktura: Created invoice
            
        Raises:
            OCRIntegrationError: If creation fails
        """
        try:
            with transaction.atomic():
                extracted_data = ocr_result.extracted_data
                
                # Validate data
                is_valid, errors = OCRDataValidator.validate_ocr_data(extracted_data)
                if not is_valid:
                    raise OCRIntegrationError(f"Błędy walidacji: {'; '.join(errors)}")
                
                # Get or create kontrahent (sprzedawca for cost invoice)
                kontrahent = self._get_or_create_kontrahent(extracted_data)
                
                # Get user's company
                try:
                    firma = self.user.firma
                except Firma.DoesNotExist:
                    raise OCRIntegrationError("Użytkownik nie ma przypisanej firmy")
                
                # Create faktura
                faktura = self._create_faktura(extracted_data, firma, kontrahent, ocr_result)
                
                # Create positions
                self._create_positions(faktura, extracted_data['pozycje'])
                
                # Update OCR result with atomic status changes
                ocr_result.faktura = faktura
                ocr_result.auto_created_faktura = True
                ocr_result.save(update_fields=['faktura', 'auto_created_faktura'])
                ocr_result.mark_processing_completed()
                
                # Update Faktura OCR fields
                faktura.source_document = ocr_result.document
                faktura.ocr_confidence = ocr_result.confidence_score
                faktura.ocr_processing_time = ocr_result.processing_time
                faktura.ocr_extracted_at = timezone.now()
                faktura.manual_verification_required = ocr_result.needs_human_review
                faktura.save()
                
                # Sync document status after successful faktura creation
                try:
                    StatusSyncService.sync_document_status(ocr_result.document)
                    logger.debug(f"Synced document status after creating Faktura {faktura.numer}")
                except StatusSyncError as e:
                    logger.warning(f"Failed to sync document status after creating Faktura {faktura.numer}: {str(e)}")
                    # Don't fail the entire creation for sync errors
                
                logger.info(f"Successfully created Faktura {faktura.numer} from OCR result {ocr_result.id}")
                return faktura
                
        except Exception as e:
            logger.error(f"Failed to create Faktura from OCR result {ocr_result.id}: {str(e)}", exc_info=True)
            
            # Mark OCR result as failed with proper error handling
            try:
                ocr_result.mark_processing_failed(str(e))
                # Sync document status after marking as failed
                StatusSyncService.sync_document_status(ocr_result.document)
            except Exception as sync_error:
                logger.error(f"Failed to update status after Faktura creation error for OCR result {ocr_result.id}: {str(sync_error)}")
            
            raise OCRIntegrationError(f"Nie udało się utworzyć faktury: {str(e)}")
    
    def _get_or_create_kontrahent(self, extracted_data: Dict[str, Any]) -> Kontrahent:
        """Get or create kontrahent from OCR data"""
        sprzedawca_data = {
            'nazwa': extracted_data['sprzedawca_nazwa'],
            'nip': extracted_data.get('sprzedawca_nip', ''),
            'ulica': extracted_data.get('sprzedawca_ulica', ''),
            'numer_domu': extracted_data.get('sprzedawca_numer_domu', ''),
            'kod_pocztowy': extracted_data.get('sprzedawca_kod_pocztowy', ''),
            'miejscowosc': extracted_data.get('sprzedawca_miejscowosc', ''),
            'kraj': extracted_data.get('sprzedawca_kraj', 'Polska'),
        }
        
        # Try to find existing kontrahent by NIP, or create new one
        if sprzedawca_data['nip']:
            existing_kontrahent = Kontrahent.objects.filter(
                user=self.user,
                nip=sprzedawca_data['nip']
            ).first()
            
            if existing_kontrahent:
                logger.info(f"Found existing Kontrahent: {existing_kontrahent.nazwa}")
                return existing_kontrahent
        
        # Create new kontrahent
        kontrahent = Kontrahent.objects.create(
            user=self.user,
            czy_firma=True,
            **sprzedawca_data
        )
        
        logger.info(f"Created new Kontrahent: {kontrahent.nazwa}")
        return kontrahent
    
    def _create_faktura(self, extracted_data: Dict[str, Any], firma: Firma, 
                       kontrahent: Kontrahent, ocr_result: OCRResult) -> Faktura:
        """Create Faktura instance"""
        
        # Parse dates
        data_wystawienia = self._parse_date(extracted_data['data_wystawienia'])
        data_sprzedazy = self._parse_date(extracted_data['data_sprzedazy'])
        
        # Calculate payment term (default 14 days if not specified)
        termin_platnosci_dni = extracted_data.get('termin_platnosci_dni', 14)
        termin_platnosci = data_wystawienia + timedelta(days=termin_platnosci_dni)
        
        faktura = Faktura.objects.create(
            user=self.user,
            typ_dokumentu='FV',  # Default to VAT invoice
            numer=extracted_data['numer_faktury'],
            data_wystawienia=data_wystawienia,
            data_sprzedazy=data_sprzedazy,
            miejsce_wystawienia=extracted_data.get('miejsce_wystawienia', ''),
            sprzedawca=firma,
            nabywca=kontrahent,
            typ_faktury='koszt',  # OCR invoices are typically cost invoices
            sposob_platnosci=extracted_data.get('sposob_platnosci', 'przelew'),
            termin_platnosci=termin_platnosci,
            status='wystawiona',
            waluta=extracted_data.get('waluta', 'PLN'),
            uwagi=f"Utworzona automatycznie z OCR (pewność: {ocr_result.confidence_score:.1f}%)",
            auto_numer=False,  # Don't auto-generate number, use OCR extracted
        )
        
        return faktura
    
    def _create_positions(self, faktura: Faktura, pozycje_data: list):
        """Create invoice positions"""
        for pozycja_data in pozycje_data:
            PozycjaFaktury.objects.create(
                faktura=faktura,
                nazwa=pozycja_data['nazwa'],
                ilosc=Decimal(str(pozycja_data['ilosc'])),
                jednostka=pozycja_data.get('jednostka', 'szt'),
                cena_netto=Decimal(str(pozycja_data['cena_netto'])),
                vat=str(pozycja_data['vat']),
                rabat=pozycja_data.get('rabat'),
                rabat_typ=pozycja_data.get('rabat_typ', 'procent') if pozycja_data.get('rabat') else None
            )
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string to date object"""
        if isinstance(date_str, date):
            return date_str
        
        # Try different formats
        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Cannot parse date: {date_str}")


def process_ocr_result(ocr_result_id: int) -> Optional[Faktura]:
    """
    Main function to process OCR result and create Faktura with proper status synchronization
    
    Args:
        ocr_result_id: ID of OCRResult to process
        
    Returns:
        Faktura: Created invoice or None if not created
    """
    ocr_result = None
    try:
        # Use atomic transaction to ensure consistent status updates
        with transaction.atomic():
            ocr_result = OCRResult.objects.select_related('document', 'document__user').get(id=ocr_result_id)
            
            logger.info(f"Starting OCR result processing for ID {ocr_result_id} with confidence {ocr_result.confidence_score:.1f}%")
            
            # Mark as processing and sync document status
            ocr_result.mark_processing_started()
            
            # Sync document status immediately after OCR status change
            try:
                StatusSyncService.sync_document_status(ocr_result.document)
                logger.debug(f"Synced document status after marking OCR result {ocr_result_id} as processing")
            except StatusSyncError as e:
                logger.warning(f"Failed to sync document status for OCR result {ocr_result_id}: {str(e)}")
                # Continue processing even if sync fails
            
            # Check if already has faktura
            if ocr_result.faktura:
                logger.info(f"OCR result {ocr_result_id} already has associated Faktura {ocr_result.faktura.id}")
                # Ensure status is properly synced for existing faktura
                ocr_result.mark_processing_completed()
                StatusSyncService.sync_document_status(ocr_result.document)
                return ocr_result.faktura
            
            # Process based on confidence level
            faktura = None
            
            if ocr_result.can_auto_create_faktura:
                # High confidence - auto create faktura
                logger.info(f"Auto-creating Faktura for OCR result {ocr_result_id} (high confidence: {ocr_result.confidence_score:.1f}%)")
                
                try:
                    creator = FakturaCreator(ocr_result.document.user)
                    faktura = creator.create_from_ocr(ocr_result)
                    
                    # Status is already updated in creator.create_from_ocr()
                    logger.info(f"Successfully auto-created Faktura {faktura.numer} from OCR result {ocr_result_id}")
                    
                except OCRIntegrationError as e:
                    logger.error(f"Failed to auto-create Faktura for OCR result {ocr_result_id}: {str(e)}")
                    # Mark as failed and sync status
                    ocr_result.mark_processing_failed(str(e))
                    StatusSyncService.sync_document_status(ocr_result.document)
                    raise
                    
            elif ocr_result.needs_human_review:
                # Low confidence - mark for manual review
                logger.info(f"Marking OCR result {ocr_result_id} for manual review (low confidence: {ocr_result.confidence_score:.1f}%)")
                ocr_result.mark_manual_review_required()
                
            else:
                # Medium confidence - mark as completed but don't auto-create
                logger.info(f"OCR result {ocr_result_id} processed but not auto-created (medium confidence: {ocr_result.confidence_score:.1f}%)")
                ocr_result.mark_processing_completed()
            
            # Final status synchronization
            try:
                StatusSyncService.sync_document_status(ocr_result.document)
                logger.debug(f"Final status sync completed for OCR result {ocr_result_id}")
            except StatusSyncError as e:
                logger.error(f"Failed final status sync for OCR result {ocr_result_id}: {str(e)}")
                # Don't fail the entire process for sync errors
            
            logger.info(f"OCR result processing completed for ID {ocr_result_id}, final status: {ocr_result.processing_status}")
            return faktura
            
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found")
        return None
        
    except OCRIntegrationError:
        # Already handled above, just re-raise
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error processing OCR result {ocr_result_id}: {str(e)}", exc_info=True)
        
        # Attempt to mark as failed and sync status
        try:
            if ocr_result:
                ocr_result.mark_processing_failed(f"Unexpected error: {str(e)}")
                StatusSyncService.sync_document_status(ocr_result.document)
        except Exception as sync_error:
            logger.error(f"Failed to update status after error for OCR result {ocr_result_id}: {str(sync_error)}")
        
        return None


def create_faktura_from_ocr_manual(ocr_result_id: int, user: User) -> Faktura:
    """
    Manually create Faktura from OCR result (for manual review cases) with proper status synchronization
    
    Args:
        ocr_result_id: ID of OCRResult
        user: User creating the invoice
        
    Returns:
        Faktura: Created invoice
        
    Raises:
        OCRIntegrationError: If creation fails
    """
    try:
        with transaction.atomic():
            ocr_result = OCRResult.objects.select_related('document').get(id=ocr_result_id)
            
            if ocr_result.faktura:
                raise OCRIntegrationError("OCR result już ma przypisaną fakturę")
            
            logger.info(f"Starting manual Faktura creation from OCR result {ocr_result_id} by user {user.username}")
            
            # Mark as processing for manual creation
            if ocr_result.processing_status != 'processing':
                ocr_result.mark_processing_started()
                try:
                    StatusSyncService.sync_document_status(ocr_result.document)
                except StatusSyncError as e:
                    logger.warning(f"Failed to sync document status during manual creation for OCR result {ocr_result_id}: {str(e)}")
            
            creator = FakturaCreator(user)
            faktura = creator.create_from_ocr(ocr_result)
            
            # Final status sync is handled in creator.create_from_ocr()
            logger.info(f"Successfully manually created Faktura {faktura.numer} from OCR result {ocr_result_id} by user {user.username}")
            return faktura
        
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found for manual creation")
        raise OCRIntegrationError("OCR result nie istnieje")
        
    except OCRIntegrationError:
        # Re-raise OCR integration errors
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during manual Faktura creation from OCR result {ocr_result_id}: {str(e)}", exc_info=True)
        
        # Attempt to mark as failed and sync status
        try:
            ocr_result = OCRResult.objects.get(id=ocr_result_id)
            ocr_result.mark_processing_failed(f"Manual creation failed: {str(e)}")
            StatusSyncService.sync_document_status(ocr_result.document)
        except Exception as sync_error:
            logger.error(f"Failed to update status after manual creation error for OCR result {ocr_result_id}: {str(sync_error)}")
        
        raise OCRIntegrationError(f"Nie udało się utworzyć faktury: {str(e)}")


def retry_failed_ocr_processing(ocr_result_id: int) -> Optional[Faktura]:
    """
    Retry processing for a failed OCR result with proper error recovery
    
    Args:
        ocr_result_id: ID of OCRResult to retry
        
    Returns:
        Faktura: Created invoice or None if not created
        
    Raises:
        OCRIntegrationError: If retry fails
    """
    try:
        ocr_result = OCRResult.objects.select_related('document', 'document__user').get(id=ocr_result_id)
        
        if ocr_result.processing_status not in ['failed', 'manual_review']:
            raise OCRIntegrationError(f"OCR result {ocr_result_id} is not in a retryable state (current: {ocr_result.processing_status})")
        
        logger.info(f"Retrying failed OCR processing for result {ocr_result_id}")
        
        # Clear previous error state
        ocr_result.error_message = None
        ocr_result.save(update_fields=['error_message'])
        
        # Process again
        return process_ocr_result(ocr_result_id)
        
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found for retry")
        raise OCRIntegrationError("OCR result nie istnieje")


def sync_ocr_document_status(ocr_result_id: int) -> bool:
    """
    Manually sync document status for an OCR result
    
    Args:
        ocr_result_id: ID of OCRResult to sync
        
    Returns:
        bool: True if sync was successful
        
    Raises:
        OCRIntegrationError: If sync fails
    """
    try:
        ocr_result = OCRResult.objects.select_related('document').get(id=ocr_result_id)
        
        logger.info(f"Manually syncing document status for OCR result {ocr_result_id}")
        
        success = StatusSyncService.sync_document_status(ocr_result.document)
        
        if success:
            logger.info(f"Successfully synced document status for OCR result {ocr_result_id}")
        else:
            logger.info(f"No status change needed for OCR result {ocr_result_id}")
        
        return success
        
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found for status sync")
        raise OCRIntegrationError("OCR result nie istnieje")
        
    except StatusSyncError as e:
        logger.error(f"Failed to sync document status for OCR result {ocr_result_id}: {str(e)}")
        raise OCRIntegrationError(f"Nie udało się zsynchronizować statusu: {str(e)}")


def get_ocr_processing_stats(user: User) -> Dict[str, Any]:
    """
    Get OCR processing statistics for user
    
    Args:
        user: User to get stats for
        
    Returns:
        Dict with processing statistics
    """
    from django.db.models import Count, Avg
    
    ocr_results = OCRResult.objects.filter(document__user=user)
    
    stats = ocr_results.aggregate(
        total_processed=Count('id'),
        avg_confidence=Avg('confidence_score'),
        auto_created_count=Count('id', filter=models.Q(auto_created_faktura=True)),
        manual_review_count=Count('id', filter=models.Q(processing_status='manual_review')),
        failed_count=Count('id', filter=models.Q(processing_status='failed')),
    )
    
    # Calculate success rate
    total = stats['total_processed'] or 0
    if total > 0:
        stats['success_rate'] = ((stats['auto_created_count'] or 0) / total) * 100
        stats['manual_review_rate'] = ((stats['manual_review_count'] or 0) / total) * 100
        stats['failure_rate'] = ((stats['failed_count'] or 0) / total) * 100
    else:
        stats['success_rate'] = 0
        stats['manual_review_rate'] = 0
        stats['failure_rate'] = 0
    
    logger.debug(f"OCR processing stats for user {user.username}: {stats}")
    return stats


def get_ocr_processing_debug_info(ocr_result_id: int) -> Dict[str, Any]:
    """
    Get detailed debug information for OCR processing
    
    Args:
        ocr_result_id: ID of OCRResult to debug
        
    Returns:
        Dict with detailed debug information
    """
    try:
        ocr_result = OCRResult.objects.select_related('document', 'document__user', 'faktura').get(id=ocr_result_id)
        
        # Get combined status from sync service
        combined_status = StatusSyncService.get_combined_status(ocr_result.document)
        
        debug_info = {
            'ocr_result_id': ocr_result.id,
            'document_id': ocr_result.document.id,
            'user_id': ocr_result.document.user.id,
            'username': ocr_result.document.user.username,
            'ocr_status': ocr_result.processing_status,
            'document_status': ocr_result.document.processing_status,
            'combined_status': combined_status,
            'confidence_score': ocr_result.confidence_score,
            'can_auto_create': ocr_result.can_auto_create_faktura,
            'needs_review': ocr_result.needs_human_review,
            'has_faktura': ocr_result.faktura is not None,
            'faktura_id': ocr_result.faktura.id if ocr_result.faktura else None,
            'auto_created': ocr_result.auto_created_faktura,
            'error_message': ocr_result.error_message,
            'created_at': ocr_result.created_at.isoformat(),
            'updated_at': ocr_result.updated_at.isoformat(),
            'document_upload_timestamp': ocr_result.document.upload_timestamp.isoformat(),
            'document_processing_started': ocr_result.document.processing_started_at.isoformat() if ocr_result.document.processing_started_at else None,
            'document_processing_completed': ocr_result.document.processing_completed_at.isoformat() if ocr_result.document.processing_completed_at else None,
            'document_error_message': ocr_result.document.error_message,
        }
        
        logger.info(f"Debug info collected for OCR result {ocr_result_id}")
        return debug_info
        
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found for debug info")
        return {
            'error': 'OCR result not found',
            'ocr_result_id': ocr_result_id
        }
        
    except Exception as e:
        logger.error(f"Error collecting debug info for OCR result {ocr_result_id}: {str(e)}", exc_info=True)
        return {
            'error': str(e),
            'ocr_result_id': ocr_result_id
        }


class OCRIntegrationService:
    """
    Service class for OCR integration operations.
    
    This class provides a unified interface for OCR-related operations
    including creating invoices from OCR results and managing validation workflows.
    """
    
    def __init__(self, user: User = None):
        self.user = user
    
    def create_faktura_from_ocr_result(self, ocr_result: OCRResult) -> Faktura:
        """
        Create a Faktura from validated OCR result.
        
        Args:
            ocr_result: OCRResult instance with validated data
            
        Returns:
            Faktura: Created invoice
            
        Raises:
            OCRIntegrationError: If creation fails
        """
        if not self.user:
            self.user = ocr_result.document.user
        
        try:
            # Use the existing FakturaCreator to create the invoice
            creator = FakturaCreator(self.user)
            faktura = creator.create_from_ocr(ocr_result)
            
            logger.info(f"Successfully created Faktura {faktura.numer} from OCR result {ocr_result.id} via OCRIntegrationService")
            return faktura
            
        except Exception as e:
            logger.error(f"Failed to create Faktura from OCR result {ocr_result.id} via OCRIntegrationService: {str(e)}", exc_info=True)
            raise OCRIntegrationError(f"Failed to create invoice via OCRIntegrationService: {str(e)}")
    
    def validate_ocr_result(self, ocr_result: OCRResult, corrections: dict, 
                          validation_notes: str = "", user: User = None) -> dict:
        """
        Validate and apply corrections to OCR result.
        
        Args:
            ocr_result: OCRResult instance to validate
            corrections: Dictionary of field corrections
            validation_notes: Optional notes about validation
            user: User performing validation (defaults to self.user)
            
        Returns:
            dict: Validation results including updated fields and confidence scores
        """
        if not user:
            user = self.user or ocr_result.document.user
        
        try:
            # Apply corrections using the OCRResult model method
            result = ocr_result.apply_manual_corrections(corrections, validated_by=user)
            
            # Create validation record
            validation_record = self._create_validation_record(
                ocr_result, corrections, validation_notes, user
            )
            
            logger.info(f"Successfully validated OCR result {ocr_result.id} with {len(corrections)} corrections")
            
            return {
                'ocr_result_id': ocr_result.id,
                'updated_fields': result['updated_fields'],
                'new_confidence_scores': result['new_confidence_scores'],
                'overall_confidence': ocr_result.confidence_score,
                'validation_id': validation_record.id if validation_record else None,
                'can_create_faktura': ocr_result.can_create_faktura(),
            }
            
        except Exception as e:
            logger.error(f"Failed to validate OCR result {ocr_result.id}: {str(e)}", exc_info=True)
            raise OCRIntegrationError(f"Failed to validate OCR result: {str(e)}")
    
    def _create_validation_record(self, ocr_result: OCRResult, corrections: dict, 
                                notes: str, user: User) -> OCRValidation:
        """
        Create a validation record for audit purposes.
        
        Args:
            ocr_result: OCRResult instance
            corrections: Applied corrections
            notes: Validation notes
            user: User who performed validation
            
        Returns:
            OCRValidation instance
        """
        try:
            # Check if validation record already exists (OneToOne relationship)
            validation_record, created = OCRValidation.objects.get_or_create(
                ocr_result=ocr_result,
                defaults={
                    'validated_by': user,
                    'corrections_made': corrections,
                    'validation_notes': notes,
                    'accuracy_rating': 8,  # Default rating for manual corrections
                }
            )
            
            if not created:
                # Update existing validation record
                validation_record.corrections_made.update(corrections)
                validation_record.validation_notes = notes
                validation_record.validated_by = user
                validation_record.save(update_fields=['corrections_made', 'validation_notes', 'validated_by'])
                logger.info(f"Updated existing validation record for OCR result {ocr_result.id}")
            else:
                logger.info(f"Created new validation record for OCR result {ocr_result.id}")
            
            return validation_record
            
        except Exception as e:
            logger.error(f"Failed to create validation record for OCR result {ocr_result.id}: {str(e)}")
            # Create a simple validation record without the problematic fields
            try:
                validation_record = OCRValidation(
                    ocr_result=ocr_result,
                    validated_by=user,
                    corrections_made=corrections,
                    validation_notes=notes,
                    accuracy_rating=8
                )
                validation_record.save()
                return validation_record
            except Exception as inner_e:
                logger.error(f"Failed to create fallback validation record: {str(inner_e)}")
                return None
    
    def get_validation_suggestions(self, ocr_result: OCRResult) -> list:
        """
        Get suggestions for fields that need validation.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            list: List of validation suggestions
        """
        suggestions = []
        field_confidence = ocr_result.field_confidence or {}
        
        # Check critical fields with low confidence
        critical_fields = {
            'numer_faktury': 'Invoice number has low confidence - please verify',
            'data_wystawienia': 'Issue date has low confidence - please verify',
            'suma_brutto': 'Total amount has low confidence - please verify',
            'sprzedawca': 'Seller information has low confidence - please verify',
            'nabywca': 'Buyer information has low confidence - please verify'
        }
        
        for field, message in critical_fields.items():
            confidence = field_confidence.get(field, ocr_result.confidence_score)
            if confidence < 80.0 and field in (ocr_result.extracted_data or {}):
                suggestions.append({
                    'field': field,
                    'message': message,
                    'confidence': confidence,
                    'priority': 'high' if confidence < 60.0 else 'medium'
                })
        
        return suggestions
    
    def get_review_priorities(self, ocr_result: OCRResult) -> dict:
        """
        Get field review priorities based on confidence scores.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            dict: Fields categorized by review priority
        """
        field_confidence = ocr_result.field_confidence or {}
        extracted_data = ocr_result.extracted_data or {}
        
        priorities = {
            'high': [],      # < 60% confidence
            'medium': [],    # 60-80% confidence
            'low': []        # > 80% confidence
        }
        
        for field, value in extracted_data.items():
            confidence = field_confidence.get(field, ocr_result.confidence_score)
            
            if confidence < 60.0:
                priority = 'high'
            elif confidence < 80.0:
                priority = 'medium'
            else:
                priority = 'low'
            
            priorities[priority].append({
                'field': field,
                'confidence': confidence,
                'value': value
            })
        
        return priorities