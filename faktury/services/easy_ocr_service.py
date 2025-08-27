#!/usr/bin/env python3
"""
EasyOCR Service - Fallback Engine
Reliable fallback OCR engine with simplified processing for Polish invoices
"""

import os
import re
import time
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import io

# EasyOCR imports
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("EasyOCR not available. Install with: pip install easyocr")

# Polish patterns for basic recognition
from .polish_patterns import PolishPatterns

logger = logging.getLogger(__name__)

@dataclass
class EasyOCRExtractedField:
    """Represents an extracted field from EasyOCR"""
    value: str
    confidence: float
    field_type: str
    validation_status: str

class EasyOCRError(Exception):
    """Base exception for EasyOCR errors"""
    pass

class EasyOCRInitializationError(EasyOCRError):
    """Raised when EasyOCR fails to initialize"""
    pass

class EasyOCRProcessingError(EasyOCRError):
    """Raised when document processing fails"""
    pass

class EasyOCRService:
    """
    EasyOCR Service - Fallback Engine
    Focuses on reliability over accuracy with simplified processing
    """
    
    def __init__(self, 
                 languages: List[str] = ['pl', 'en'],
                 use_gpu: bool = False,
                 model_path: Optional[str] = None):
        """
        Initialize EasyOCR service
        
        Args:
            languages: List of language codes (default: ['pl', 'en'])
            use_gpu: Whether to use GPU acceleration
            model_path: Custom model path
        """
        self.languages = languages
        self.use_gpu = use_gpu
        self.model_path = model_path
        
        # Initialize components
        self.reader = None
        self.polish_patterns = PolishPatterns()
        
        # Performance tracking
        self.processing_times = []
        self.memory_usage = []
        self.accuracy_metrics = []
        
        # Initialize OCR engine
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize EasyOCR reader"""
        try:
            if not EASYOCR_AVAILABLE:
                raise EasyOCRInitializationError("EasyOCR not available")
            
            # Initialize EasyOCR reader
            self.reader = easyocr.Reader(
                self.languages,
                gpu=self.use_gpu,
                model_storage_directory=self.model_path,
                download_enabled=True,
                verbose=False
            )
            
            logger.info(f"EasyOCR initialized with languages: {self.languages}")
            
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise EasyOCRInitializationError(f"EasyOCR initialization failed: {e}")
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process invoice with EasyOCR
        
        Args:
            file_content: File content as bytes
            mime_type: MIME type of the file
            
        Returns:
            Dictionary with extracted data and metadata
        """
        start_time = time.time()
        
        try:
            logger.info("Starting EasyOCR invoice processing")
            
            # Convert file to image
            image = self._convert_to_image(file_content, mime_type)
            
            # Basic preprocessing
            processed_image = self._basic_preprocessing(image)
            
            # OCR processing
            ocr_results = self._perform_ocr(processed_image)
            
            # Extract basic fields
            extracted_data = self._extract_basic_fields(ocr_results)
            
            # Calculate confidence
            confidence_score = self._calculate_confidence(ocr_results, extracted_data)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # Prepare result
            result = {
                'extracted_data': extracted_data,
                'confidence_score': confidence_score,
                'processing_time': processing_time,
                'processor_version': 'EasyOCR-2.0',
                'engine_metadata': {
                    'engine_type': 'easyocr',
                    'languages': self.languages,
                    'gpu_used': self.use_gpu,
                    'total_text_blocks': len(ocr_results),
                    'average_confidence': np.mean([block[2] for block in ocr_results]) if ocr_results else 0.0
                },
                'raw_ocr_results': ocr_results,
                'preprocessing_applied': ['basic_enhancement', 'noise_reduction'],
                'fallback_used': False
            }
            
            logger.info(f"EasyOCR processing completed in {processing_time:.2f}s with confidence {confidence_score:.2f}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"EasyOCR processing failed after {processing_time:.2f}s: {e}")
            raise EasyOCRProcessingError(f"EasyOCR processing failed: {e}")
    
    def _convert_to_image(self, file_content: bytes, mime_type: str) -> Image.Image:
        """Convert file content to PIL Image"""
        try:
            if mime_type.startswith('image/'):
                # Direct image file
                image = Image.open(io.BytesIO(file_content))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                return image
            
            elif mime_type == 'application/pdf':
                # PDF file - convert first page
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(file_content, first_page=1, last_page=1, dpi=200)
                if images:
                    return images[0].convert('RGB')
                else:
                    raise EasyOCRProcessingError("Failed to convert PDF to image")
            
            else:
                raise EasyOCRProcessingError(f"Unsupported MIME type: {mime_type}")
                
        except Exception as e:
            logger.error(f"Error converting file to image: {e}")
            raise EasyOCRProcessingError(f"File conversion failed: {e}")
    
    def _basic_preprocessing(self, image: Image.Image) -> Image.Image:
        """Apply basic image preprocessing for reliability"""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Basic enhancement
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            # Basic noise reduction
            image = image.filter(ImageFilter.MedianFilter(size=1))
            
            return image
            
        except Exception as e:
            logger.warning(f"Preprocessing failed, using original image: {e}")
            return image
    
    def _perform_ocr(self, image: Image.Image) -> List[Tuple]:
        """Perform OCR on the image"""
        try:
            # Convert PIL Image to numpy array
            img_array = np.array(image)
            
            # Perform OCR
            results = self.reader.readtext(img_array)
            
            logger.info(f"EasyOCR extracted {len(results)} text blocks")
            return results
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise EasyOCRProcessingError(f"OCR processing failed: {e}")
    
    def _extract_basic_fields(self, ocr_results: List[Tuple]) -> Dict[str, Any]:
        """
        Extract basic fields from OCR results
        Simplified field extraction focusing on reliability
        """
        try:
            # Combine all text
            full_text = ' '.join([text[1] for text in ocr_results])
            
            extracted_fields = {}
            
            # Extract basic patterns
            patterns = self.polish_patterns.extract_all_patterns(full_text)
            
            # Map patterns to invoice fields
            if patterns['nip_numbers']:
                extracted_fields['sprzedawca_nip'] = patterns['nip_numbers'][0]
                if len(patterns['nip_numbers']) > 1:
                    extracted_fields['nabywca_nip'] = patterns['nip_numbers'][1]
            
            if patterns['polish_dates']:
                extracted_fields['data_wystawienia'] = patterns['polish_dates'][0]
            
            if patterns['invoice_numbers']:
                extracted_fields['numer_faktury'] = patterns['invoice_numbers'][0]
            
            if patterns['currency_amounts']:
                # Find the largest amount (likely total)
                amounts = []
                for amount_str in patterns['currency_amounts']:
                    try:
                        # Clean amount string and convert to float
                        clean_amount = re.sub(r'[^\d,]', '', amount_str).replace(',', '.')
                        if clean_amount:
                            amounts.append(float(clean_amount))
                    except ValueError:
                        continue
                
                if amounts:
                    max_amount = max(amounts)
                    extracted_fields['suma_brutto'] = f"{max_amount:.2f}"
            
            if patterns['vat_rates']:
                extracted_fields['vat_rate'] = patterns['vat_rates'][0]
            
            # Extract company names (simplified)
            company_keywords = ['sp. z o.o.', 's.a.', 'spółka', 'company', 'ltd']
            for text in [text[1] for text in ocr_results]:
                for keyword in company_keywords:
                    if keyword.lower() in text.lower():
                        if 'sprzedawca_nazwa' not in extracted_fields:
                            extracted_fields['sprzedawca_nazwa'] = text.strip()
                        break
            
            logger.info(f"Extracted {len(extracted_fields)} basic fields")
            return extracted_fields
            
        except Exception as e:
            logger.error(f"Field extraction failed: {e}")
            return {}
    
    def _calculate_confidence(self, ocr_results: List[Tuple], extracted_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score
        Simplified confidence calculation focusing on reliability
        """
        try:
            if not ocr_results:
                return 0.0
            
            # Base confidence from OCR results
            ocr_confidences = [result[2] for result in ocr_results]
            base_confidence = np.mean(ocr_confidences) if ocr_confidences else 0.0
            
            # Field extraction confidence
            field_confidence = 0.0
            if extracted_data:
                # Simple scoring based on number of extracted fields
                field_count = len(extracted_data)
                if field_count >= 5:
                    field_confidence = 0.9
                elif field_count >= 3:
                    field_confidence = 0.7
                elif field_count >= 1:
                    field_confidence = 0.5
                else:
                    field_confidence = 0.2
            
            # Polish pattern validation boost
            polish_boost = 0.0
            if 'sprzedawca_nip' in extracted_data:
                nip = extracted_data['sprzedawca_nip']
                if self.polish_patterns.validate_nip(nip):
                    polish_boost = 0.1
            
            # Calculate final confidence
            final_confidence = (base_confidence * 0.6 + field_confidence * 0.3 + polish_boost * 0.1)
            
            # Ensure confidence is within bounds
            final_confidence = max(0.0, min(1.0, final_confidence))
            
            return final_confidence
            
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
                'engine_type': 'easyocr',
                'languages': self.languages,
                'gpu_enabled': self.use_gpu
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def is_available(self) -> bool:
        """Check if EasyOCR is available"""
        return EASYOCR_AVAILABLE and self.reader is not None
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information"""
        return {
            'name': 'EasyOCR',
            'version': '2.0',
            'type': 'fallback',
            'languages': self.languages,
            'gpu_support': self.use_gpu,
            'available': self.is_available(),
            'reliability_focus': True,
            'accuracy_target': 0.85
        }
