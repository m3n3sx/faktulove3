"""
Celery tasks for OCR document processing
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from .models import DocumentUpload, OCRResult, OCRProcessingLog, Faktura, Kontrahent, Firma
from .services.document_ai_service import get_document_ai_service
from .services.file_upload_service import FileUploadService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_ocr_document(self, document_upload_id: int) -> Dict[str, Any]:
    """
    Process uploaded document with OCR
    
    Args:
        document_upload_id: ID of DocumentUpload to process
        
    Returns:
        Dictionary with processing results
    """
    try:
        # Get document upload record
        document_upload = DocumentUpload.objects.get(id=document_upload_id)
        
        # Log processing start
        _log_processing_event(
            document_upload, 
            'INFO', 
            'OCR processing started',
            {'task_id': self.request.id}
        )
        
        # Mark as processing started
        document_upload.mark_processing_started()
        
        # Initialize services
        ai_service = get_document_ai_service()
        file_service = FileUploadService()
        
        # Get file content
        file_content = file_service.get_file_content(document_upload)
        
        # Process with Document AI
        extracted_data = ai_service.process_invoice(
            file_content=file_content,
            mime_type=document_upload.content_type
        )
        
        # Convert Decimal objects to strings for JSON serialization
        extracted_data_serializable = _convert_decimals_to_strings(extracted_data)
        
        # Store OCR results
        ocr_result = OCRResult.objects.create(
            document=document_upload,
            raw_text=extracted_data.get('raw_text', ''),
            extracted_data=extracted_data_serializable,
            confidence_score=extracted_data.get('confidence_score', 0.0),
            processing_time=extracted_data.get('processing_time', 0.0),
            field_confidence=extracted_data.get('field_confidence', {}),
            processor_version=extracted_data.get('processor_version', ''),
            processing_location=extracted_data.get('processing_location', ''),
        )
        
        # Determine processing workflow based on confidence
        confidence = extracted_data.get('confidence_score', 0.0)
        thresholds = settings.OCR_SETTINGS['confidence_thresholds']
        
        if confidence >= thresholds['auto_approve']:
            # High confidence - try to create invoice automatically
            try:
                faktura = _create_invoice_from_ocr(ocr_result, document_upload.user)
                ocr_result.faktura = faktura
                ocr_result.save()
                
                workflow_result = 'auto_created'
                _log_processing_event(
                    document_upload,
                    'INFO',
                    f'Invoice auto-created: {faktura.numer}',
                    {'faktura_id': faktura.id, 'confidence': confidence}
                )
                
            except Exception as e:
                logger.warning(f"Auto-creation failed for document {document_upload_id}: {e}")
                workflow_result = 'review_required'
                _log_processing_event(
                    document_upload,
                    'WARNING',
                    f'Auto-creation failed: {str(e)}',
                    {'confidence': confidence}
                )
                
        elif confidence >= thresholds['review_required']:
            # Medium confidence - queue for human review
            workflow_result = 'review_required'
            _log_processing_event(
                document_upload,
                'INFO',
                'Queued for human review',
                {'confidence': confidence}
            )
            
        else:
            # Low confidence - require manual entry
            workflow_result = 'manual_entry'
            _log_processing_event(
                document_upload,
                'INFO',
                'Manual entry required',
                {'confidence': confidence}
            )
        
        # Mark processing as completed
        document_upload.mark_processing_completed()
        
        result = {
            'status': 'success',
            'document_id': document_upload_id,
            'ocr_result_id': ocr_result.id,
            'confidence_score': confidence,
            'workflow_result': workflow_result,
            'processing_time': extracted_data.get('processing_time', 0.0),
        }
        
        _log_processing_event(
            document_upload,
            'INFO',
            'OCR processing completed successfully',
            result
        )
        
        return result
        
    except DocumentUpload.DoesNotExist:
        error_msg = f"DocumentUpload {document_upload_id} not found"
        logger.error(error_msg)
        return {'status': 'error', 'message': error_msg}
        
    except Exception as e:
        error_msg = f"OCR processing failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Mark document as failed if it exists
        try:
            document_upload = DocumentUpload.objects.get(id=document_upload_id)
            document_upload.mark_processing_failed(error_msg)
            
            _log_processing_event(
                document_upload,
                'ERROR',
                error_msg,
                {'task_id': self.request.id, 'retry_count': self.request.retries}
            )
        except DocumentUpload.DoesNotExist:
            pass
        
        # Retry if within limits
        if self.request.retries < self.max_retries:
            # Exponential backoff: 60s, 120s, 240s
            countdown = 60 * (2 ** self.request.retries)
            logger.info(f"Retrying OCR processing in {countdown}s (attempt {self.request.retries + 1})")
            raise self.retry(countdown=countdown, exc=e)
        
        return {
            'status': 'error',
            'message': error_msg,
            'document_id': document_upload_id
        }


def _create_invoice_from_ocr(ocr_result: OCRResult, user: User) -> Faktura:
    """
    Create Faktura from OCR results
    
    Args:
        ocr_result: OCR result with extracted data
        user: User who uploaded the document
        
    Returns:
        Created Faktura instance
    """
    extracted_data = ocr_result.extracted_data
    
    # Get or create supplier (sprzedawca)
    supplier_data = {
        'nazwa': extracted_data.get('supplier_name', ''),
        'nip': extracted_data.get('supplier_nip', ''),
        'ulica': _extract_address_part(extracted_data.get('supplier_address', ''), 'street'),
        'miejscowosc': extracted_data.get('supplier_city', ''),
        'kod_pocztowy': extracted_data.get('supplier_postal_code', ''),
    }
    
    # Try to find existing supplier by NIP
    supplier_firma = None
    if supplier_data['nip']:
        try:
            supplier_firma = Firma.objects.get(nip=supplier_data['nip'])
        except Firma.DoesNotExist:
            pass
    
    if not supplier_firma:
        # For now, use user's company as supplier
        # In production, you might want to create a new Firma or handle differently
        supplier_firma = user.firma
    
    # Get or create buyer (nabywca) 
    buyer_data = {
        'nazwa': extracted_data.get('buyer_name', ''),
        'nip': extracted_data.get('buyer_nip', ''),
        'ulica': _extract_address_part(extracted_data.get('buyer_address', ''), 'street'),
        'miejscowosc': extracted_data.get('buyer_city', ''),
        'kod_pocztowy': extracted_data.get('buyer_postal_code', ''),
    }
    
    # Try to find existing buyer by NIP
    buyer_kontrahent = None
    if buyer_data['nip']:
        try:
            buyer_kontrahent = Kontrahent.objects.filter(
                user=user,
                nip=buyer_data['nip']
            ).first()
        except Kontrahent.DoesNotExist:
            pass
    
    if not buyer_kontrahent and buyer_data['nazwa']:
        # Create new kontrahent
        buyer_kontrahent = Kontrahent.objects.create(
            user=user,
            nazwa=buyer_data['nazwa'],
            nip=buyer_data['nip'] or '',
            ulica=buyer_data['ulica'] or '',
            numer_domu='1',  # Default value
            miejscowosc=buyer_data['miejscowosc'] or '',
            kod_pocztowy=buyer_data['kod_pocztowy'] or '',
            czy_firma=bool(buyer_data['nip']),
        )
    
    if not buyer_kontrahent:
        raise ValueError("Could not determine buyer for invoice")
    
    # Parse dates
    invoice_date = _parse_date_from_ocr(extracted_data.get('invoice_date'))
    due_date = _parse_date_from_ocr(extracted_data.get('due_date'))
    
    if not invoice_date:
        invoice_date = timezone.now().date()
    
    if not due_date:
        due_date = invoice_date + timedelta(days=30)  # Default 30 days
    
    # Create Faktura
    faktura = Faktura.objects.create(
        user=user,
        numer=extracted_data.get('invoice_number', f'OCR/{timezone.now().strftime("%Y%m%d%H%M%S")}'),
        data_wystawienia=invoice_date,
        data_sprzedazy=invoice_date,
        termin_platnosci=due_date,
        miejsce_wystawienia=user.firma.miejscowosc if hasattr(user, 'firma') else 'Warszawa',
        sprzedawca=supplier_firma,
        nabywca=buyer_kontrahent,
        typ_faktury='sprzedaz',  # Default
        waluta=extracted_data.get('currency', 'PLN'),
        
        # OCR metadata
        # Note: These fields need to be added to Faktura model
        # source_document=ocr_result.document,
        # ocr_confidence=ocr_result.confidence_score,
        # manual_verification_required=ocr_result.needs_human_review,
        # ocr_processing_time=ocr_result.processing_time,
        # ocr_extracted_at=timezone.now(),
    )
    
    # Create invoice line items
    line_items = extracted_data.get('line_items', [])
    if line_items:
        _create_invoice_line_items(faktura, line_items)
    else:
        # Create single line item from totals
        _create_single_line_item_from_totals(faktura, extracted_data)
    
    return faktura


def _create_invoice_line_items(faktura: Faktura, line_items: list):
    """Create PozycjaFaktury from line items"""
    from .models import PozycjaFaktury
    
    for item in line_items:
        # Parse line item data
        nazwa = item.get('description', 'Pozycja z OCR')
        ilosc = _parse_decimal_from_ocr(item.get('quantity', '1'))
        cena_netto = _parse_decimal_from_ocr(item.get('unit_price', '0'))
        vat_rate = _parse_vat_rate(item.get('vat_rate', '23'))
        
        PozycjaFaktury.objects.create(
            faktura=faktura,
            nazwa=nazwa,
            ilosc=ilosc,
            cena_netto=cena_netto,
            vat=vat_rate,
            jednostka='szt',  # Default unit
        )


def _create_single_line_item_from_totals(faktura: Faktura, extracted_data: dict):
    """Create single line item from total amounts"""
    from .models import PozycjaFaktury
    
    net_amount = extracted_data.get('net_amount')
    total_amount = extracted_data.get('total_amount')
    vat_amount = extracted_data.get('vat_amount')
    
    if net_amount:
        net_amount = _parse_decimal_from_ocr(net_amount)
    elif total_amount and vat_amount:
        total_amount = _parse_decimal_from_ocr(total_amount)
        vat_amount = _parse_decimal_from_ocr(vat_amount)
        net_amount = total_amount - vat_amount
    else:
        net_amount = Decimal('0.00')
    
    # Calculate VAT rate
    vat_rate = '23'  # Default
    if net_amount > 0 and vat_amount:
        vat_amount = _parse_decimal_from_ocr(vat_amount)
        calculated_rate = (vat_amount / net_amount * 100).quantize(Decimal('1'))
        if calculated_rate in [Decimal('23'), Decimal('8'), Decimal('5'), Decimal('0')]:
            vat_rate = str(calculated_rate)
    
    PozycjaFaktury.objects.create(
        faktura=faktura,
        nazwa='Usługa/Towar z OCR',
        ilosc=Decimal('1.00'),
        cena_netto=net_amount,
        vat=vat_rate,
        jednostka='szt',
    )


@shared_task
def cleanup_old_documents():
    """Clean up old processed documents"""
    try:
        cleanup_days = settings.OCR_SETTINGS['cleanup_after_days']
        cutoff_date = timezone.now() - timedelta(days=cleanup_days)
        
        # Find old completed documents
        old_documents = DocumentUpload.objects.filter(
            processing_status='completed',
            processing_completed_at__lt=cutoff_date
        )
        
        file_service = FileUploadService()
        cleaned_count = 0
        
        for document in old_documents:
            try:
                # Clean up files
                file_service.cleanup_file(document)
                
                # Delete database records
                # Note: OCR results will be cascade deleted
                document.delete()
                cleaned_count += 1
                
            except Exception as e:
                logger.error(f"Failed to cleanup document {document.id}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} old documents")
        return {'cleaned_count': cleaned_count}
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        return {'error': str(e)}


@shared_task
def cleanup_failed_documents():
    """Clean up old failed documents"""
    try:
        # Clean up failed documents older than 7 days
        cutoff_date = timezone.now() - timedelta(days=7)
        
        failed_documents = DocumentUpload.objects.filter(
            processing_status='failed',
            processing_completed_at__lt=cutoff_date
        )
        
        file_service = FileUploadService()
        cleaned_count = 0
        
        for document in failed_documents:
            try:
                file_service.cleanup_file(document)
                document.delete()
                cleaned_count += 1
            except Exception as e:
                logger.error(f"Failed to cleanup failed document {document.id}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} failed documents")
        return {'cleaned_count': cleaned_count}
        
    except Exception as e:
        logger.error(f"Failed document cleanup task failed: {e}")
        return {'error': str(e)}


# Helper functions

def _log_processing_event(document: DocumentUpload, level: str, message: str, details: dict = None):
    """Log OCR processing event"""
    try:
        OCRProcessingLog.objects.create(
            document=document,
            level=level,
            message=message,
            details=details or {}
        )
    except Exception as e:
        logger.error(f"Failed to log processing event: {e}")


def _parse_date_from_ocr(date_string):
    """Parse date from OCR extracted string"""
    if not date_string:
        return None
    
    try:
        # Try ISO format first
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        pass
    
    # Try other common formats
    formats = ['%d.%m.%Y', '%d-%m-%Y', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date: {date_string}")
    return None


def _parse_decimal_from_ocr(value) -> Decimal:
    """Parse decimal value from OCR result"""
    if isinstance(value, Decimal):
        return value
    
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    
    if isinstance(value, str):
        # Clean string and convert
        cleaned = value.replace(',', '.').replace(' ', '')
        # Remove currency symbols
        cleaned = ''.join(c for c in cleaned if c.isdigit() or c == '.')
        try:
            return Decimal(cleaned)
        except:
            return Decimal('0.00')
    
    return Decimal('0.00')


def _convert_decimals_to_strings(data):
    """Convert Decimal objects to strings in nested data structures"""
    if isinstance(data, dict):
        return {key: _convert_decimals_to_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_decimals_to_strings(item) for item in data]
    elif isinstance(data, Decimal):
        return str(data)
    else:
        return data


def _parse_vat_rate(vat_string) -> str:
    """Parse VAT rate from string"""
    if not vat_string:
        return '23'
    
    # Extract numbers from string
    import re
    numbers = re.findall(r'\d+', str(vat_string))
    
    if numbers:
        rate = int(numbers[0])
        if rate in [23, 8, 5, 0]:
            return str(rate)
    
    return '23'  # Default


def _extract_address_part(address_string: str, part: str) -> str:
    """Extract part of address (simplified)"""
    if not address_string:
        return ''
    
    if part == 'street':
        # Return first line of address
        lines = address_string.split('\n')
        return lines[0].strip() if lines else ''
    
    return address_string