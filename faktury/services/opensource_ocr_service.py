"""
Open Source OCR Service for Invoice Processing

This service replaces Google Cloud Document AI with a comprehensive open-source
OCR solution while maintaining identical interface and method signatures for
backward compatibility.
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .document_processor import DocumentProcessor
from .polish_invoice_processor import PolishInvoiceProcessor

logger = logging.getLogger(__name__)


class OpenSourceOCRService:
    """
    Open Source OCR service for processing invoice documents
    
    This service maintains identical interface to DocumentAIService while using
    the new open-source OCR pipeline with Tesseract, EasyOCR, and enhanced
    Polish language processing capabilities.
    """
    
    def __init__(self):
        """Initialize the open source OCR service"""
        try:
            # Initialize document processor with OCR engines
            self.document_processor = DocumentProcessor(
                max_workers=getattr(settings, 'OCR_MAX_WORKERS', 3),
                enable_parallel_processing=getattr(settings, 'OCR_PARALLEL_PROCESSING', True),
                confidence_threshold=getattr(settings, 'OCR_CONFIDENCE_THRESHOLD', 70.0),
                max_retries=getattr(settings, 'OCR_MAX_RETRIES', 2),
                fallback_enabled=getattr(settings, 'OCR_FALLBACK_ENABLED', True)
            )
            
            # Initialize Polish invoice processor for compatibility
            self.polish_processor = PolishInvoiceProcessor()
            
            # Configuration for compatibility with existing code
            self.config = {
                'processor_version': 'opensource-v1.0',
                'max_file_size': getattr(settings, 'OCR_MAX_FILE_SIZE', 50 * 1024 * 1024),  # 50MB
                'location': 'local',
                'project_id': 'opensource-ocr'
            }
            
            # Initialize the document processor
            if not self.document_processor.initialize():
                raise ImproperlyConfigured(
                    "Failed to initialize open source OCR engines. "
                    "Please check OCR engine configuration and dependencies."
                )
            
            logger.info("OpenSourceOCRService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenSourceOCRService: {e}")
            raise ImproperlyConfigured(
                f"Open Source OCR service initialization failed: {e}"
            )
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process invoice document with open source OCR pipeline
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            
        Returns:
            Dictionary containing extracted data and metadata (compatible with DocumentAI format)
        """
        start_time = time.time()
        
        try:
            # Validate file size
            max_size = self.config['max_file_size']
            if len(file_content) > max_size:
                raise ValueError(f"File size {len(file_content)} exceeds maximum {max_size}")
            
            logger.info(f"Processing document with open source OCR pipeline")
            
            # Process document through the new OCR pipeline
            processing_result = self.document_processor.process_invoice(
                file_content=file_content,
                mime_type=mime_type
            )
            
            if not processing_result.success:
                error_msg = "OCR processing failed"
                if processing_result.error_details:
                    error_msg += f": {processing_result.error_details.get('message', 'Unknown error')}"
                raise RuntimeError(error_msg)
            
            processing_time = time.time() - start_time
            
            # Extract structured data from processing result
            extracted_data = self.extract_invoice_fields(processing_result)
            extracted_data['processing_time'] = processing_time
            extracted_data['processor_version'] = self.config['processor_version']
            extracted_data['processing_location'] = self.config['location']
            
            logger.info(f"Document processed successfully in {processing_time:.2f}s")
            return extracted_data
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Open source OCR processing failed after {processing_time:.2f}s: {e}")
            raise
    
    def extract_invoice_fields(self, processing_result) -> Dict[str, Any]:
        """
        Extract specific invoice fields from processing result
        
        Args:
            processing_result: ProcessingResult from document processor
            
        Returns:
            Dictionary with extracted invoice data in DocumentAI-compatible format
        """
        try:
            # Get extracted data from processing result
            final_data = processing_result.extracted_data
            extracted_fields = final_data.get('extracted_fields', {})
            line_items = final_data.get('line_items', [])
            seller_info = final_data.get('seller_info')
            buyer_info = final_data.get('buyer_info')
            confidence_analysis = final_data.get('confidence_analysis', {})
            
            # Initialize result structure compatible with DocumentAI format
            extracted_data = {
                # Basic invoice information
                'invoice_number': self._get_field_value(extracted_fields, 'numer_faktury'),
                'invoice_date': self._get_field_value(extracted_fields, 'invoice_date'),
                'due_date': self._get_field_value(extracted_fields, 'due_date'),
                'currency': 'PLN',
                
                # Supplier information
                'supplier_name': seller_info.nazwa if seller_info else None,
                'supplier_nip': seller_info.nip if seller_info else self._get_field_value(extracted_fields, 'seller_nip'),
                'supplier_address': self._format_address(seller_info) if seller_info else None,
                'supplier_city': seller_info.miejscowosc if seller_info else None,
                'supplier_postal_code': seller_info.kod_pocztowy if seller_info else None,
                
                # Buyer information
                'buyer_name': buyer_info.nazwa if buyer_info else None,
                'buyer_nip': buyer_info.nip if buyer_info else self._get_field_value(extracted_fields, 'buyer_nip'),
                'buyer_address': self._format_address(buyer_info) if buyer_info else None,
                'buyer_city': buyer_info.miejscowosc if buyer_info else None,
                'buyer_postal_code': buyer_info.kod_pocztowy if buyer_info else None,
                
                # Financial information
                'total_amount': self._get_field_value(extracted_fields, 'total_amount'),
                'net_amount': self._get_field_value(extracted_fields, 'net_amount'),
                'vat_amount': self._get_field_value(extracted_fields, 'vat_amount'),
                'payment_method': self._get_field_value(extracted_fields, 'payment_method'),
                'bank_account': self._get_field_value(extracted_fields, 'bank_accounts'),
                
                # Line items (convert to DocumentAI format)
                'line_items': self._convert_line_items(line_items),
                
                # Metadata
                'confidence_score': processing_result.confidence_score,
                'field_confidence': self._extract_field_confidences(extracted_fields),
                'raw_text': self._get_raw_text_from_result(processing_result),
            }
            
            # Apply Polish-specific enhancements for compatibility
            extracted_data = self._enhance_with_polish_patterns(extracted_data)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting invoice fields: {e}")
            # Return minimal structure to maintain compatibility
            return {
                'invoice_number': None,
                'invoice_date': None,
                'due_date': None,
                'currency': 'PLN',
                'supplier_name': None,
                'supplier_nip': None,
                'supplier_address': None,
                'buyer_name': None,
                'buyer_nip': None,
                'buyer_address': None,
                'total_amount': None,
                'net_amount': None,
                'vat_amount': None,
                'line_items': [],
                'confidence_score': 0.0,
                'field_confidence': {},
                'raw_text': '',
                'extraction_error': str(e)
            }
    
    def _get_field_value(self, extracted_fields: Dict[str, Any], field_name: str) -> Any:
        """Get field value, handling ExtractedField objects"""
        field = extracted_fields.get(field_name)
        if field is None:
            return None
        
        # Handle ExtractedField objects
        if hasattr(field, 'value'):
            return field.value
        
        # Handle list of ExtractedField objects
        if isinstance(field, list) and field:
            if hasattr(field[0], 'value'):
                return field[0].value
            return field[0]
        
        return field
    
    def _format_address(self, company_info) -> Optional[str]:
        """Format company address from CompanyInfo object"""
        if not company_info:
            return None
        
        address_parts = []
        
        if company_info.ulica:
            street_part = company_info.ulica
            if company_info.numer_domu:
                street_part += f" {company_info.numer_domu}"
            address_parts.append(street_part)
        
        if company_info.kod_pocztowy and company_info.miejscowosc:
            address_parts.append(f"{company_info.kod_pocztowy} {company_info.miejscowosc}")
        elif company_info.miejscowosc:
            address_parts.append(company_info.miejscowosc)
        
        return ', '.join(address_parts) if address_parts else None
    
    def _convert_line_items(self, line_items: list) -> list:
        """Convert line items to DocumentAI-compatible format"""
        converted_items = []
        
        for item in line_items:
            if hasattr(item, 'nazwa'):  # LineItem object
                converted_items.append({
                    'description': item.nazwa,
                    'quantity': str(item.ilosc),
                    'unit': item.jednostka,
                    'unit_price': str(item.cena_netto),
                    'vat_rate': item.vat,
                    'net_amount': str(item.wartosc_netto),
                    'gross_amount': str(item.wartosc_brutto)
                })
            elif isinstance(item, dict):
                # Already in dictionary format
                converted_items.append(item)
        
        return converted_items
    
    def _extract_field_confidences(self, extracted_fields: Dict[str, Any]) -> Dict[str, float]:
        """Extract field-level confidence scores"""
        field_confidences = {}
        
        for field_name, field_value in extracted_fields.items():
            if hasattr(field_value, 'confidence'):
                field_confidences[field_name] = field_value.confidence
            elif isinstance(field_value, list) and field_value and hasattr(field_value[0], 'confidence'):
                field_confidences[field_name] = field_value[0].confidence
            else:
                field_confidences[field_name] = 50.0  # Default confidence
        
        return field_confidences
    
    def _get_raw_text_from_result(self, processing_result) -> str:
        """Extract raw OCR text from processing result"""
        if processing_result.raw_ocr_results:
            # Get text from the best OCR result
            best_result = max(processing_result.raw_ocr_results, 
                            key=lambda r: r.get('confidence_score', 0.0))
            return best_result.get('raw_text', '')
        
        return ''
    
    def _enhance_with_polish_patterns(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance extraction with Polish-specific patterns using specialized processor"""
        raw_text = extracted_data.get('raw_text', '')
        
        if not raw_text:
            return extracted_data
        
        try:
            # Use specialized Polish invoice processor for enhancement
            enhanced_data = self.polish_processor.enhance_extraction(raw_text, extracted_data)
            
            # Add validation results
            validation_results = self.polish_processor.validate_polish_invoice(enhanced_data)
            enhanced_data.update(validation_results)
            
            logger.info(f"Polish enhancement completed. Valid invoice: {validation_results.get('is_valid_polish_invoice', False)}")
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error in Polish pattern enhancement: {e}")
            return extracted_data
    
    def validate_processor_availability(self) -> bool:
        """Check if OCR processor is available"""
        try:
            return self.document_processor.is_initialized
        except Exception as e:
            logger.error(f"Processor availability check failed: {e}")
            return False
    
    # Additional methods for compatibility with DocumentAIService interface
    def _parse_date(self, date_string: str) -> Optional[str]:
        """Parse date string to ISO format"""
        if not date_string:
            return None
        
        # Use the same date parsing logic as DocumentAIService
        import re
        from datetime import datetime
        
        # Polish date patterns
        patterns = getattr(settings, 'POLISH_OCR_PATTERNS', {}).get('date_patterns', [
            r'(\d{1,2})[.-/](\d{1,2})[.-/](\d{4})',
            r'(\d{4})[.-/](\d{1,2})[.-/](\d{1,2})'
        ])
        
        for pattern in patterns:
            match = re.search(pattern, date_string)
            if match:
                try:
                    if len(match.group(1)) == 4:  # YYYY-MM-DD
                        year, month, day = match.groups()
                    else:  # DD-MM-YYYY
                        day, month, year = match.groups()
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except (ValueError, AttributeError):
                    continue
        
        # Try to parse as-is
        try:
            parsed_date = datetime.strptime(date_string, '%Y-%m-%d')
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            logger.warning(f"Could not parse date: {date_string}")
            return None
    
    def _parse_amount(self, amount_string: str) -> Optional[Decimal]:
        """Parse amount string to Decimal"""
        if not amount_string:
            return None
        
        try:
            import re
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[^\d,.-]', '', str(amount_string))
            # Replace comma with dot for decimal separator
            cleaned = cleaned.replace(',', '.')
            return Decimal(cleaned)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse amount: {amount_string}")
            return None
    
    def _clean_nip(self, nip_string: str) -> Optional[str]:
        """Clean and validate NIP number"""
        if not nip_string:
            return None
        
        import re
        # Extract digits only
        nip_digits = re.sub(r'[^\d]', '', str(nip_string))
        
        # Polish NIP should have 10 digits
        if len(nip_digits) == 10:
            return nip_digits
        
        logger.warning(f"Invalid NIP format: {nip_string}")
        return nip_string  # Return original if can't clean


class MockOpenSourceOCRService:
    """Mock service for testing without OCR engines"""
    
    def __init__(self):
        """Initialize mock service with Polish processor"""
        self.polish_processor = PolishInvoiceProcessor()
        self.config = {
            'processor_version': 'mock-opensource-v1.0',
            'max_file_size': 50 * 1024 * 1024,
            'location': 'mock',
            'project_id': 'mock-opensource-ocr'
        }
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Mock processing that returns sample data enhanced with Polish patterns"""
        logger.info("Using mock open source OCR service with Polish enhancement")
        
        # Base mock data
        base_data = {
            'invoice_number': 'FV/001/2024',
            'invoice_date': '2024-01-15',
            'due_date': '2024-02-15',
            'supplier_name': 'Test Supplier Sp. z o.o.',
            'supplier_nip': '1234567890',
            'buyer_name': 'Test Buyer Sp. z o.o.',
            'buyer_nip': '0987654321',
            'total_amount': '1230.00',
            'net_amount': '1000.00',
            'vat_amount': '230.00',
            'currency': 'PLN',
            'line_items': [
                {
                    'description': 'Test Product',
                    'quantity': '1',
                    'unit_price': '1000.00',
                    'vat_rate': '23%',
                    'net_amount': '1000.00',
                }
            ],
            'confidence_score': 85.0,
            'processing_time': 2.5,
            'processor_version': self.config['processor_version'],
            'processing_location': self.config['location'],
            'raw_text': 'Faktura VAT Nr FV/001/2024\nSprzedawca: Test Supplier Sp. z o.o.\nNIP: 123-456-78-90\nNabywca: Test Buyer Sp. z o.o.\nNIP: 098-765-43-21\nDo zapłaty: 1230,00 zł\nNetto: 1000,00 zł\nVAT 23%: 230,00 zł',
        }
        
        # Enhance with Polish processor
        enhanced_data = self.polish_processor.enhance_extraction(base_data['raw_text'], base_data)
        
        # Add validation results
        validation_results = self.polish_processor.validate_polish_invoice(enhanced_data)
        enhanced_data.update(validation_results)
        
        return enhanced_data
    
    def extract_invoice_fields(self, processing_result) -> Dict[str, Any]:
        """Mock field extraction"""
        return processing_result
    
    def validate_processor_availability(self) -> bool:
        """Mock processor availability check"""
        return True


def get_opensource_ocr_service():
    """Factory function to get Open Source OCR service"""
    # Check if we should use mock service for testing
    if getattr(settings, 'USE_MOCK_OCR_SERVICE', False):
        logger.warning("Using mock open source OCR service")
        return MockOpenSourceOCRService()
    
    # Try to use real open source OCR service
    try:
        return OpenSourceOCRService()
    except Exception as e:
        logger.warning(f"Open source OCR service not available: {e}, falling back to mock service")
        return MockOpenSourceOCRService()


def create_faktura_from_ocr(ocr_result):
    """
    Create Faktura from OCR result
    
    Args:
        ocr_result: OCRResult instance with extracted data
        
    Returns:
        Created Faktura instance or None if creation failed
    """
    try:
        from faktury.tasks import _create_invoice_from_ocr
        return _create_invoice_from_ocr(ocr_result, ocr_result.document.user)
    except Exception as e:
        logger.error(f"Failed to create invoice from OCR: {e}")
        return None