"""
Google Document AI Service for Invoice OCR Processing
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from .polish_invoice_processor import PolishInvoiceProcessor
import re
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    from google.cloud import documentai
    from google.auth.exceptions import DefaultCredentialsError
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    documentai = None

logger = logging.getLogger(__name__)


class DocumentAIService:
    """Google Document AI service for processing invoice documents"""
    
    def __init__(self):
        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImproperlyConfigured(
                "Google Cloud Document AI libraries not installed. "
                "Run: pip install google-cloud-documentai"
            )
        
        try:
            self.client = documentai.DocumentProcessorServiceClient()
            self.config = settings.DOCUMENT_AI_CONFIG
            self.project_id = self.config['project_id']
            self.location = self.config['location']
            self.processor_id = self.config['processor_id']
            
            if not self.processor_id:
                raise ImproperlyConfigured(
                    "DOCUMENT_AI_PROCESSOR_ID environment variable not set"
                )
                
        except DefaultCredentialsError:
            raise ImproperlyConfigured(
                "Google Cloud credentials not configured. "
                "Set GOOGLE_APPLICATION_CREDENTIALS environment variable."
            )
        
        # Initialize Polish invoice processor
        self.polish_processor = PolishInvoiceProcessor()
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process invoice document with Google Document AI
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        start_time = time.time()
        
        try:
            # Validate file size
            max_size = self.config['max_file_size']
            if len(file_content) > max_size:
                raise ValueError(f"File size {len(file_content)} exceeds maximum {max_size}")
            
            # Configure the process request
            name = self.client.processor_path(
                self.project_id, 
                self.location, 
                self.processor_id
            )
            
            # Create raw document
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=mime_type
            )
            
            # Process the document
            request = documentai.ProcessRequest(
                name=name,
                raw_document=raw_document
            )
            
            logger.info(f"Processing document with Document AI processor: {self.processor_id}")
            result = self.client.process_document(request=request)
            document = result.document
            
            processing_time = time.time() - start_time
            
            # Extract structured data
            extracted_data = self.extract_invoice_fields(document)
            extracted_data['processing_time'] = processing_time
            extracted_data['processor_version'] = self.config['processor_version']
            extracted_data['processing_location'] = self.location
            
            logger.info(f"Document processed successfully in {processing_time:.2f}s")
            return extracted_data
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Document AI processing failed after {processing_time:.2f}s: {e}")
            raise
    
    def extract_invoice_fields(self, document) -> Dict[str, Any]:
        """Extract specific invoice fields from Document AI response"""
        
        extracted_data = {
            # Basic invoice information
            'invoice_number': None,
            'invoice_date': None,
            'due_date': None,
            'currency': 'PLN',
            
            # Supplier information
            'supplier_name': None,
            'supplier_nip': None,
            'supplier_address': None,
            'supplier_city': None,
            'supplier_postal_code': None,
            
            # Buyer information
            'buyer_name': None,
            'buyer_nip': None,
            'buyer_address': None,
            'buyer_city': None,
            'buyer_postal_code': None,
            
            # Financial information
            'total_amount': None,
            'net_amount': None,
            'vat_amount': None,
            'payment_method': None,
            'bank_account': None,
            
            # Line items
            'line_items': [],
            
            # Metadata
            'confidence_score': 0.0,
            'field_confidence': {},
            'raw_text': document.text,
        }
        
        # Extract entities from Document AI response
        overall_confidence = 0.0
        confidence_count = 0
        
        for entity in document.entities:
            field_name = entity.type_
            field_value = entity.mention_text
            confidence = entity.confidence
            
            # Track confidence for overall score
            if confidence > 0:
                overall_confidence += confidence
                confidence_count += 1
            
            # Store field-specific confidence
            extracted_data['field_confidence'][field_name] = confidence
            
            # Map Document AI fields to our structure
            if field_name == 'invoice_id':
                extracted_data['invoice_number'] = field_value
            elif field_name == 'invoice_date':
                extracted_data['invoice_date'] = self._parse_date(field_value)
            elif field_name == 'due_date':
                extracted_data['due_date'] = self._parse_date(field_value)
            elif field_name == 'supplier_name':
                extracted_data['supplier_name'] = field_value
            elif field_name == 'supplier_tax_id':
                extracted_data['supplier_nip'] = self._clean_nip(field_value)
            elif field_name == 'supplier_address':
                extracted_data['supplier_address'] = field_value
            elif field_name == 'receiver_name':
                extracted_data['buyer_name'] = field_value
            elif field_name == 'receiver_tax_id':
                extracted_data['buyer_nip'] = self._clean_nip(field_value)
            elif field_name == 'receiver_address':
                extracted_data['buyer_address'] = field_value
            elif field_name == 'total_amount':
                extracted_data['total_amount'] = self._parse_amount(field_value)
            elif field_name == 'net_amount':
                extracted_data['net_amount'] = self._parse_amount(field_value)
            elif field_name == 'vat_amount':
                extracted_data['vat_amount'] = self._parse_amount(field_value)
            elif field_name == 'currency':
                extracted_data['currency'] = field_value
        
        # Extract line items from tables
        extracted_data['line_items'] = self._extract_line_items(document)
        
        # Calculate overall confidence score
        if confidence_count > 0:
            extracted_data['confidence_score'] = (overall_confidence / confidence_count) * 100
        
        # Apply Polish-specific enhancements
        extracted_data = self._enhance_with_polish_patterns(extracted_data)
        
        return extracted_data
    
    def _extract_line_items(self, document) -> list:
        """Extract line items from document tables"""
        line_items = []
        
        for page in document.pages:
            for table in page.tables:
                # Process table rows to extract line items
                headers = []
                
                # Get headers from first row
                if table.header_rows:
                    header_row = table.header_rows[0]
                    for cell in header_row.cells:
                        headers.append(cell.layout.text_anchor.content.strip())
                
                # Process data rows
                for row in table.body_rows:
                    line_item = {}
                    for i, cell in enumerate(row.cells):
                        header = headers[i] if i < len(headers) else f'col_{i}'
                        value = cell.layout.text_anchor.content.strip()
                        line_item[header] = value
                    
                    if line_item:  # Only add non-empty line items
                        line_items.append(line_item)
        
        return line_items
    
    def _parse_date(self, date_string: str) -> Optional[str]:
        """Parse date string to ISO format"""
        if not date_string:
            return None
        
        # Polish date patterns
        patterns = settings.POLISH_OCR_PATTERNS['date_patterns']
        
        for pattern in patterns:
            match = re.search(pattern, date_string)
            if match:
                try:
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
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[^\d,.-]', '', amount_string)
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
        
        # Extract digits only
        nip_digits = re.sub(r'[^\d]', '', nip_string)
        
        # Polish NIP should have 10 digits
        if len(nip_digits) == 10:
            return nip_digits
        
        logger.warning(f"Invalid NIP format: {nip_string}")
        return nip_string  # Return original if can't clean
    
    def _enhance_with_polish_patterns(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance extraction with Polish-specific patterns using specialized processor"""
        raw_text = extracted_data.get('raw_text', '')
        
        if not raw_text:
            return extracted_data
        
        # Use specialized Polish invoice processor for enhancement
        enhanced_data = self.polish_processor.enhance_extraction(raw_text, extracted_data)
        
        # Add validation results
        validation_results = self.polish_processor.validate_polish_invoice(enhanced_data)
        enhanced_data.update(validation_results)
        
        logger.info(f"Polish enhancement completed. Valid invoice: {validation_results['is_valid_polish_invoice']}")
        
        return enhanced_data
    
    def validate_processor_availability(self) -> bool:
        """Check if Document AI processor is available"""
        try:
            name = self.client.processor_path(
                self.project_id,
                self.location, 
                self.processor_id
            )
            
            # Try to get processor info
            processor = self.client.get_processor(name=name)
            return processor.state == documentai.Processor.State.ENABLED
            
        except Exception as e:
            logger.error(f"Processor availability check failed: {e}")
            return False


class MockDocumentAIService:
    """Mock service for testing without Google Cloud credentials"""
    
    def __init__(self):
        """Initialize mock service with Polish processor"""
        self.polish_processor = PolishInvoiceProcessor()
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Mock processing that returns sample data enhanced with Polish patterns"""
        logger.info("Using mock Document AI service with Polish enhancement")
        
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
            'processor_version': 'mock',
            'processing_location': 'mock',
            'raw_text': 'Faktura VAT Nr FV/001/2024\nSprzedawca: Test Supplier Sp. z o.o.\nNIP: 123-456-78-90\nNabywca: Test Buyer Sp. z o.o.\nNIP: 098-765-43-21\nDo zapłaty: 1230,00 zł\nNetto: 1000,00 zł\nVAT 23%: 230,00 zł',
        }
        
        # Enhance with Polish processor
        enhanced_data = self.polish_processor.enhance_extraction(base_data['raw_text'], base_data)
        
        # Add validation results
        validation_results = self.polish_processor.validate_polish_invoice(enhanced_data)
        enhanced_data.update(validation_results)
        
        return enhanced_data


def get_document_ai_service():
    """Factory function to get Document AI service"""
    # For testing, always use mock service if no credentials
    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        logger.warning("Google Cloud credentials not configured, using mock service")
        return MockDocumentAIService()
    
    # Try to use real Document AI service
    try:
        return DocumentAIService()
    except Exception as e:
        logger.warning(f"Document AI service not available: {e}, falling back to mock service")
        return MockDocumentAIService()


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