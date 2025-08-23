"""
Local OCR Service using pytesseract for Invoice Processing
"""

import logging
import time
import re
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import pytesseract
from PIL import Image
import io
from pdf2image import convert_from_bytes

from django.conf import settings

logger = logging.getLogger(__name__)


class LocalOCRService:
    """Local OCR service using pytesseract for processing invoice documents"""
    
    def __init__(self):
        try:
            # Test if tesseract is available
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
        except Exception as e:
            logger.error(f"Tesseract OCR not available: {e}")
            raise Exception("Tesseract OCR not installed. Please install tesseract-ocr.")
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process invoice document with local OCR
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        start_time = time.time()
        
        try:
            # Convert file to image if needed
            if mime_type == 'application/pdf':
                # Convert PDF to images
                logger.info("Converting PDF to images for OCR processing")
                images = convert_from_bytes(file_content, first_page=1, last_page=1)
                if not images:
                    logger.error("Failed to convert PDF to images")
                    return self._get_fallback_data()
                
                # Use first page for OCR
                image = images[0]
                logger.info(f"PDF converted to image: {image.size}")
            else:
                # Process image directly
                image = Image.open(io.BytesIO(file_content))
            
            # Extract text using OCR
            raw_text = pytesseract.image_to_string(image, lang='pol')
            
            processing_time = time.time() - start_time
            
            # Extract structured data from text
            extracted_data = self._extract_invoice_fields(raw_text)
            extracted_data['processing_time'] = processing_time
            extracted_data['raw_text'] = raw_text
            
            # Calculate confidence score based on extracted data
            confidence_score = self._calculate_confidence_score(extracted_data, raw_text)
            extracted_data['confidence_score'] = confidence_score
            extracted_data['processor_version'] = 'local-tesseract'
            extracted_data['processing_location'] = 'local'
            
            logger.info(f"Local OCR processing completed in {processing_time:.2f}s")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Local OCR processing failed: {e}")
            return self._get_fallback_data()
    
    def _extract_invoice_fields(self, raw_text: str) -> Dict[str, Any]:
        """Extract invoice fields from OCR text"""
        extracted_data = {
            'invoice_number': '',
            'invoice_date': '',
            'due_date': '',
            'supplier_name': '',
            'supplier_nip': '',
            'buyer_name': '',
            'buyer_nip': '',
            'total_amount': '',
            'net_amount': '',
            'vat_amount': '',
            'currency': 'PLN',
            'line_items': [],
        }
        
        # Extract invoice number
        invoice_patterns = [
            r'FAKTURA\s*[VW]A\s*[:\s]*([A-Z0-9\/\-]+)',
            r'FAKTURA\s*[:\s]*([A-Z0-9\/\-]+)',
            r'NR\s*FAKTURY\s*[:\s]*([A-Z0-9\/\-]+)',
            r'FAKTURA\s*NR\s*[:\s]*([A-Z0-9\/\-]+)',
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                extracted_data['invoice_number'] = match.group(1).strip()
                break
        
        # Extract dates
        date_patterns = [
            r'DATA\s*WYSTAWIENIA\s*[:\s]*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',
            r'DATA\s*FAKTURY\s*[:\s]*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',
            r'(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                extracted_data['invoice_date'] = match.group(1).strip()
                break
        
        # Extract amounts
        amount_patterns = [
            r'DO\s*ZAPŁATY\s*[:\s]*([\d\s,\.]+)\s*[A-Z]{3}',
            r'KWOTA\s*BRUTTO\s*[:\s]*([\d\s,\.]+)\s*[A-Z]{3}',
            r'SUMA\s*[:\s]*([\d\s,\.]+)\s*[A-Z]{3}',
            r'([\d\s,\.]+)\s*[A-Z]{3}',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(' ', '').replace(',', '.')
                try:
                    amount = float(amount_str)
                    extracted_data['total_amount'] = f"{amount:.2f}"
                    break
                except ValueError:
                    continue
        
        # Extract NIP numbers
        nip_pattern = r'NIP\s*[:\s]*(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3})'
        nip_matches = re.findall(nip_pattern, raw_text, re.IGNORECASE)
        
        if len(nip_matches) >= 2:
            extracted_data['supplier_nip'] = nip_matches[0].replace(' ', '').replace('-', '')
            extracted_data['buyer_nip'] = nip_matches[1].replace(' ', '').replace('-', '')
        elif len(nip_matches) == 1:
            extracted_data['supplier_nip'] = nip_matches[0].replace(' ', '').replace('-', '')
        
        # Extract company names (simplified)
        company_patterns = [
            r'SPRZEDAWCA\s*[:\s]*([^\n]+)',
            r'NABYWCA\s*[:\s]*([^\n]+)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                if 'sprzedawca' in pattern.lower():
                    extracted_data['supplier_name'] = company_name
                else:
                    extracted_data['buyer_name'] = company_name
        
        return extracted_data
    
    def _calculate_confidence_score(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Calculate confidence score based on extracted data quality"""
        score = 0.0
        total_fields = 0
        
        # Check if we have basic invoice structure
        if 'FAKTURA' in raw_text.upper() or 'INVOICE' in raw_text.upper():
            score += 20.0
            total_fields += 1
        
        # Check invoice number
        if extracted_data['invoice_number']:
            score += 15.0
            total_fields += 1
        
        # Check invoice date
        if extracted_data['invoice_date']:
            score += 15.0
            total_fields += 1
        
        # Check total amount
        if extracted_data['total_amount']:
            score += 20.0
            total_fields += 1
        
        # Check supplier/buyer information
        if extracted_data['supplier_name'] or extracted_data['supplier_nip']:
            score += 15.0
            total_fields += 1
        
        if extracted_data['buyer_name'] or extracted_data['buyer_nip']:
            score += 15.0
            total_fields += 1
        
        # Normalize score
        if total_fields > 0:
            final_score = min(score, 100.0)
        else:
            final_score = 0.0
        
        logger.info(f"OCR confidence score: {final_score:.1f}% (extracted {total_fields} fields)")
        return final_score
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Return fallback data when OCR fails"""
        return {
            'invoice_number': '',
            'invoice_date': '',
            'due_date': '',
            'supplier_name': '',
            'supplier_nip': '',
            'buyer_name': '',
            'buyer_nip': '',
            'total_amount': '',
            'net_amount': '',
            'vat_amount': '',
            'currency': 'PLN',
            'line_items': [],
            'confidence_score': 0.0,
            'processing_time': 0.0,
            'processor_version': 'local-tesseract',
            'processing_location': 'local',
            'raw_text': 'OCR processing failed',
        }


def get_local_ocr_service():
    """Factory function to get local OCR service"""
    return LocalOCRService()
