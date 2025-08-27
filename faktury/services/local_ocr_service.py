"""
Enhanced Local OCR Service using Tesseract for Invoice Processing
Last resort OCR engine with maximum reliability and Polish language support
"""

import logging
import time
import re
import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from decimal import Decimal
from datetime import datetime
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
from pdf2image import convert_from_bytes
from pathlib import Path

from django.conf import settings

# Polish patterns for enhanced recognition
from .polish_patterns import PolishPatterns

logger = logging.getLogger(__name__)


class LocalOCRService:
    """
    Enhanced Local OCR service using Tesseract for processing invoice documents
    Last resort engine with maximum reliability and Polish language optimization
    """
    
    def __init__(self, 
                 languages: List[str] = ['pol', 'eng'],
                 config: str = None,
                 timeout: int = 30):
        """
        Initialize enhanced Tesseract OCR service
        
        Args:
            languages: List of language codes (default: ['pol', 'eng'])
            config: Custom Tesseract configuration
            timeout: Processing timeout in seconds
        """
        self.languages = languages
        self.timeout = timeout
        self.polish_patterns = PolishPatterns()
        
        # Performance tracking
        self.processing_times = []
        self.memory_usage = []
        self.accuracy_metrics = []
        
        try:
            # Test if tesseract is available
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR is available (version: {version})")
            
            # Set default config if not provided
            if config is None:
                config = self._get_tesseract_config()
            
            self.config = config
            
        except Exception as e:
            logger.error(f"Tesseract OCR not available: {e}")
            raise Exception("Tesseract OCR not installed. Please install tesseract-ocr and tesseract-ocr-pol.")
    
    def _get_tesseract_config(self) -> str:
        """
        Get optimized Tesseract configuration for Polish invoices
        
        Returns:
            Tesseract configuration string
        """
        return '--oem 1 --psm 6 -l pol+eng --dpi 300'
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process invoice document with enhanced local OCR
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        start_time = time.time()
        
        try:
            logger.info("Starting enhanced Tesseract invoice processing")
            
            # Convert file to image if needed
            image = self._convert_to_image(file_content, mime_type)
            
            # Apply advanced preprocessing
            processed_image = self._advanced_preprocessing(image)
            
            # Extract text using enhanced OCR
            raw_text = self._perform_enhanced_ocr(processed_image)
            
            # Extract structured data from text
            extracted_data = self._extract_with_fallback_patterns(raw_text)
            
            # Calculate confidence score
            confidence_score = self._calculate_enhanced_confidence(extracted_data, raw_text)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # Prepare result
            result = {
                'extracted_data': extracted_data,
                'confidence_score': confidence_score,
                'processing_time': processing_time,
                'processor_version': 'Enhanced-Tesseract-2.0',
                'engine_metadata': {
                    'engine_type': 'tesseract',
                    'languages': self.languages,
                    'config': self.config,
                    'preprocessing_applied': ['advanced_preprocessing', 'noise_reduction', 'contrast_enhancement'],
                    'total_text_length': len(raw_text)
                },
                'raw_text': raw_text,
                'preprocessing_applied': ['advanced_preprocessing', 'noise_reduction', 'contrast_enhancement'],
                'fallback_used': False
            }
            
            logger.info(f"Enhanced Tesseract processing completed in {processing_time:.2f}s with confidence {confidence_score:.2f}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Enhanced Tesseract processing failed after {processing_time:.2f}s: {e}")
            return self._get_fallback_data()
    
    def _convert_to_image(self, file_content: bytes, mime_type: str) -> Image.Image:
        """Convert file content to PIL Image with error handling"""
        try:
            if mime_type == 'application/pdf':
                # Convert PDF to images with higher DPI
                logger.info("Converting PDF to images for OCR processing")
                images = convert_from_bytes(file_content, first_page=1, last_page=1, dpi=300)
                if not images:
                    logger.error("Failed to convert PDF to images")
                    raise Exception("PDF conversion failed")
                
                # Use first page for OCR
                image = images[0]
                logger.info(f"PDF converted to image: {image.size}")
                return image
            else:
                # Process image directly
                image = Image.open(io.BytesIO(file_content))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                return image
                
        except Exception as e:
            logger.error(f"Error converting file to image: {e}")
            raise Exception(f"File conversion failed: {e}")
    
    def _advanced_preprocessing(self, image: Image.Image) -> Image.Image:
        """
        Apply advanced image preprocessing for maximum reliability
        
        Args:
            image: Input PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            logger.info("Applying advanced preprocessing")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Noise reduction
            denoised = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
            
            # Convert back to PIL
            denoised_image = Image.fromarray(denoised)
            
            # Contrast enhancement
            enhancer = ImageEnhance.Contrast(denoised_image)
            enhanced = enhancer.enhance(1.3)
            
            # Brightness adjustment
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(1.1)
            
            # Sharpening
            enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            
            # Resolution optimization
            width, height = enhanced.size
            if width < 800 or height < 600:
                # Upscale for better OCR
                scale_factor = max(800 / width, 600 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                enhanced = enhanced.resize((new_width, new_height), Image.LANCZOS)
                logger.info(f"Upscaled image from {width}x{height} to {new_width}x{new_height}")
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Advanced preprocessing failed, using original image: {e}")
            return image
    
    def _perform_enhanced_ocr(self, image: Image.Image) -> str:
        """
        Perform enhanced OCR with multiple attempts and error recovery
        
        Args:
            image: Preprocessed PIL Image
            
        Returns:
            Extracted text
        """
        try:
            # First attempt with optimized config
            raw_text = pytesseract.image_to_string(
                image, 
                config=self.config,
                timeout=self.timeout
            )
            
            # If no text extracted, try with different PSM modes
            if not raw_text.strip():
                logger.warning("No text extracted with default config, trying alternative PSM modes")
                
                alternative_configs = [
                    '--oem 1 --psm 3 -l pol+eng',  # Fully automatic page segmentation
                    '--oem 1 --psm 4 -l pol+eng',  # Assume single column of text
                    '--oem 1 --psm 8 -l pol+eng',  # Single word
                    '--oem 1 --psm 13 -l pol+eng', # Raw line
                ]
                
                for alt_config in alternative_configs:
                    try:
                        raw_text = pytesseract.image_to_string(
                            image, 
                            config=alt_config,
                            timeout=self.timeout
                        )
                        if raw_text.strip():
                            logger.info(f"Successfully extracted text with config: {alt_config}")
                            break
                    except Exception as e:
                        logger.warning(f"Failed with config {alt_config}: {e}")
                        continue
            
            if not raw_text.strip():
                logger.error("Failed to extract any text from image")
                return ""
            
            logger.info(f"Extracted {len(raw_text)} characters of text")
            return raw_text
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return ""
    
    def _extract_with_fallback_patterns(self, raw_text: str) -> Dict[str, Any]:
        """
        Extract invoice fields with enhanced pattern matching and fallback logic
        
        Args:
            raw_text: Raw OCR text
            
        Returns:
            Dictionary with extracted fields
        """
        try:
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
            
            # Use Polish patterns for enhanced extraction
            patterns = self.polish_patterns.extract_all_patterns(raw_text)
            
            # Extract NIP numbers
            if patterns['nip_numbers']:
                extracted_data['supplier_nip'] = patterns['nip_numbers'][0]
                if len(patterns['nip_numbers']) > 1:
                    extracted_data['buyer_nip'] = patterns['nip_numbers'][1]
            
            # Extract dates
            if patterns['polish_dates']:
                extracted_data['invoice_date'] = patterns['polish_dates'][0]
                if len(patterns['polish_dates']) > 1:
                    extracted_data['due_date'] = patterns['polish_dates'][1]
            
            # Extract invoice numbers
            if patterns['invoice_numbers']:
                extracted_data['invoice_number'] = patterns['invoice_numbers'][0]
            
            # Extract currency amounts
            if patterns['currency_amounts']:
                # Find the largest amount (likely total)
                amounts = []
                for amount_str in patterns['currency_amounts']:
                    try:
                        clean_amount = re.sub(r'[^\d,]', '', amount_str).replace(',', '.')
                        if clean_amount:
                            amounts.append(float(clean_amount))
                    except ValueError:
                        continue
                
                if amounts:
                    max_amount = max(amounts)
                    extracted_data['total_amount'] = f"{max_amount:.2f}"
            
            # Extract VAT rates
            if patterns['vat_rates']:
                extracted_data['vat_rate'] = patterns['vat_rates'][0]
            
            # Fallback to original patterns if Polish patterns didn't extract enough
            if not extracted_data['invoice_number']:
                extracted_data = self._extract_invoice_fields_fallback(raw_text, extracted_data)
            
            logger.info(f"Extracted {len([v for v in extracted_data.values() if v])} fields")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Enhanced field extraction failed: {e}")
            return self._extract_invoice_fields_fallback(raw_text, {})
    
    def _extract_invoice_fields_fallback(self, raw_text: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback field extraction using original patterns"""
        extracted_data = existing_data.copy() if existing_data else {
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
    
    def _calculate_enhanced_confidence(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """
        Calculate enhanced confidence score with Polish validation
        
        Args:
            extracted_data: Extracted invoice data
            raw_text: Raw OCR text
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        try:
            score = 0.0
            total_fields = 0
            
            # Base confidence from text quality
            if raw_text and len(raw_text.strip()) > 50:
                score += 0.1
                total_fields += 1
            
            # Check if we have basic invoice structure
            if 'FAKTURA' in raw_text.upper() or 'INVOICE' in raw_text.upper():
                score += 0.15
                total_fields += 1
            
            # Check invoice number
            if extracted_data.get('invoice_number'):
                score += 0.12
                total_fields += 1
            
            # Check invoice date
            if extracted_data.get('invoice_date'):
                score += 0.12
                total_fields += 1
            
            # Check total amount
            if extracted_data.get('total_amount'):
                score += 0.15
                total_fields += 1
            
            # Check supplier/buyer information
            if extracted_data.get('supplier_name') or extracted_data.get('supplier_nip'):
                score += 0.12
                total_fields += 1
            
            if extracted_data.get('buyer_name') or extracted_data.get('buyer_nip'):
                score += 0.12
                total_fields += 1
            
            # Polish validation boost
            polish_boost = 0.0
            if extracted_data.get('supplier_nip'):
                if self.polish_patterns.validate_nip(extracted_data['supplier_nip']):
                    polish_boost += 0.05
            
            if extracted_data.get('buyer_nip'):
                if self.polish_patterns.validate_nip(extracted_data['buyer_nip']):
                    polish_boost += 0.05
            
            # Calculate final confidence
            if total_fields > 0:
                final_score = min(score + polish_boost, 1.0)
            else:
                final_score = 0.0
            
            logger.info(f"Enhanced confidence score: {final_score:.2f} (extracted {total_fields} fields, Polish boost: {polish_boost:.2f})")
            return final_score
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5  # Default confidence
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            return {
                'average_processing_time': np.mean(self.processing_times) if self.processing_times else 0.0,
                'total_processed': len(self.processing_times),
                'memory_usage': np.mean(self.memory_usage) if self.memory_usage else 0.0,
                'accuracy_metrics': np.mean(self.accuracy_metrics) if self.accuracy_metrics else 0.0,
                'engine_type': 'tesseract',
                'languages': self.languages,
                'config': self.config,
                'timeout': self.timeout
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def is_available(self) -> bool:
        """Check if Tesseract is available"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information"""
        return {
            'name': 'Enhanced Tesseract',
            'version': '2.0',
            'type': 'last_resort',
            'languages': self.languages,
            'config': self.config,
            'available': self.is_available(),
            'reliability_focus': True,
            'accuracy_target': 0.80
        }
    
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
