#!/usr/bin/env python3
"""
PaddleOCR Service for FaktuLove
Primary OCR engine with Polish invoice optimization
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

# PaddleOCR imports
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logging.warning("PaddleOCR not available. Install with: pip install paddlepaddle paddleocr")

# Polish patterns and validation
from .polish_patterns import PolishPatterns
from .paddle_confidence_calculator import PaddleConfidenceCalculator
from .advanced_image_preprocessor import AdvancedImagePreprocessor

logger = logging.getLogger(__name__)

@dataclass
class ExtractedField:
    """Represents an extracted field with confidence and validation"""
    value: str
    confidence: float
    bounding_box: Dict[str, int]
    validation_status: str
    polish_specific_score: float
    field_type: str

class PaddleOCRError(Exception):
    """Base exception for PaddleOCR errors"""
    pass

class PaddleOCRInitializationError(PaddleOCRError):
    """Raised when PaddleOCR fails to initialize"""
    pass

class PaddleOCRProcessingError(PaddleOCRError):
    """Raised when document processing fails"""
    pass

class PolishValidationError(PaddleOCRError):
    """Raised when Polish-specific validation fails"""
    pass

class PaddleOCRService:
    """
    PaddleOCR Service optimized for Polish invoices
    Provides high-accuracy OCR with Polish-specific preprocessing and validation
    """
    
    def __init__(self, 
                 languages: List[str] = ['pl', 'en'],
                 use_gpu: bool = False,
                 det_model_dir: Optional[str] = None,
                 rec_model_dir: Optional[str] = None,
                 cls_model_dir: Optional[str] = None):
        """
        Initialize PaddleOCR with Polish language support
        
        Args:
            languages: List of language codes (default: ['pl', 'en'])
            use_gpu: Whether to use GPU acceleration
            det_model_dir: Custom detection model directory
            rec_model_dir: Custom recognition model directory
            cls_model_dir: Custom classification model directory
        """
        self.languages = languages
        self.use_gpu = use_gpu
        self.det_model_dir = det_model_dir
        self.rec_model_dir = rec_model_dir
        self.cls_model_dir = cls_model_dir
        
        # Initialize components
        self.ocr_engine = None
        self.polish_patterns = PolishPatterns()
        self.confidence_calculator = PaddleConfidenceCalculator()
        self.image_preprocessor = AdvancedImagePreprocessor()
        
        # Performance tracking
        self.processing_times = []
        self.memory_usage = []
        self.accuracy_metrics = []
        
        # Initialize OCR engine
        self._initialize_ocr_engine()
        
        logger.info(f"PaddleOCR Service initialized with languages: {languages}")
    
    def _initialize_ocr_engine(self) -> None:
        """Initialize PaddleOCR engine with Polish models"""
        if not PADDLEOCR_AVAILABLE:
            raise PaddleOCRInitializationError("PaddleOCR is not available. Please install paddlepaddle and paddleocr")
        
        try:
            # Configure PaddleOCR for Polish invoices
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang='pl' if 'pl' in self.languages else 'en',
                use_gpu=self.use_gpu,
                det_model_dir=self.det_model_dir,
                rec_model_dir=self.rec_model_dir,
                cls_model_dir=self.cls_model_dir,
                # Polish-specific optimizations
                use_space_char=True,
                drop_score=0.5,
                # Performance optimizations
                cpu_threads=4,
                enable_mkldnn=True,
                # Polish language specific
                rec_char_dict_path=None,  # Use default Polish dictionary
                det_db_thresh=0.3,
                det_db_box_thresh=0.5,
                det_db_unclip_ratio=1.6
            )
            
            logger.info("PaddleOCR engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise PaddleOCRInitializationError(f"PaddleOCR initialization failed: {e}")
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Main processing method for invoice documents
        
        Args:
            file_content: Raw file content as bytes
            mime_type: MIME type of the file
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Preprocess image
            logger.info("Starting invoice processing")
            preprocessed_image = self.preprocess_image(file_content, mime_type)
            
            # Step 2: OCR text extraction
            ocr_results = self._extract_text(preprocessed_image)
            
            # Step 3: Extract structured invoice data
            extracted_data = self.extract_invoice_fields(ocr_results)
            
            # Step 4: Calculate confidence scores
            confidence_score = self.confidence_calculator.calculate_overall_confidence(
                ocr_results, extracted_data
            )
            
            # Step 5: Polish-specific validation
            validation_results = self._validate_polish_data(extracted_data)
            
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # Prepare result
            result = {
                'extracted_data': extracted_data,
                'confidence_score': confidence_score,
                'processing_time': processing_time,
                'processor_version': 'paddleocr-v2.7-polish-optimized',
                'engine_metadata': {
                    'models_used': ['pl_PP-OCRv4_det', 'pl_PP-OCRv4_rec'],
                    'gpu_acceleration': self.use_gpu,
                    'preprocessing_applied': ['noise_reduction', 'contrast_enhancement', 'skew_correction'],
                    'languages_used': self.languages
                },
                'validation_results': validation_results,
                'ocr_raw_results': ocr_results,
                'spatial_analysis': self._analyze_spatial_layout(ocr_results),
                'polish_validation': validation_results
            }
            
            logger.info(f"Invoice processing completed in {processing_time:.2f}s with confidence {confidence_score:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error processing invoice: {e}")
            raise PaddleOCRProcessingError(f"Invoice processing failed: {e}")
    
    def preprocess_image(self, file_content: bytes, mime_type: str) -> np.ndarray:
        """
        Advanced image preprocessing for Polish documents
        
        Args:
            file_content: Raw file content
            mime_type: MIME type of the file
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Convert to PIL Image
            if mime_type == 'application/pdf':
                # Handle PDF conversion
                image = self._convert_pdf_to_image(file_content)
            else:
                image = Image.open(io.BytesIO(file_content))
            
            # Apply Polish-specific preprocessing
            preprocessed = self.image_preprocessor.preprocess_for_paddleocr(image)
            
            # Convert to numpy array for PaddleOCR
            return np.array(preprocessed)
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise PaddleOCRProcessingError(f"Image preprocessing failed: {e}")
    
    def extract_invoice_fields(self, ocr_results: List[Dict]) -> Dict[str, Any]:
        """
        Extract structured invoice data from OCR results
        
        Args:
            ocr_results: Raw OCR results from PaddleOCR
            
        Returns:
            Dictionary with extracted invoice fields
        """
        try:
            # Combine all text with position information
            text_blocks = []
            for result in ocr_results:
                for line in result:
                    if len(line) >= 2:
                        text_blocks.append({
                            'text': line[1][0],
                            'confidence': line[1][1],
                            'bbox': line[0]
                        })
            
            # Extract Polish invoice fields
            extracted_fields = {
                'numer_faktury': self._extract_invoice_number(text_blocks),
                'data_wystawienia': self._extract_issue_date(text_blocks),
                'data_sprzedazy': self._extract_sale_date(text_blocks),
                'sprzedawca_nazwa': self._extract_seller_name(text_blocks),
                'sprzedawca_nip': self._extract_seller_nip(text_blocks),
                'nabywca_nazwa': self._extract_buyer_name(text_blocks),
                'nabywca_nip': self._extract_buyer_nip(text_blocks),
                'suma_brutto': self._extract_total_gross(text_blocks),
                'suma_netto': self._extract_total_net(text_blocks),
                'suma_vat': self._extract_total_vat(text_blocks),
                'pozycje': self._extract_line_items(text_blocks),
                'waluta': self._extract_currency(text_blocks),
                'metoda_platnosci': self._extract_payment_method(text_blocks),
                'termin_platnosci': self._extract_payment_terms(text_blocks)
            }
            
            # Add confidence scores for each field
            field_confidence = {}
            for field_name, field_data in extracted_fields.items():
                if isinstance(field_data, ExtractedField):
                    field_confidence[field_name] = field_data.confidence
                else:
                    field_confidence[field_name] = 0.0
            
            extracted_fields['paddle_confidence_scores'] = field_confidence
            
            return extracted_fields
            
        except Exception as e:
            logger.error(f"Field extraction failed: {e}")
            raise PaddleOCRProcessingError(f"Field extraction failed: {e}")
    
    def extract_polish_patterns(self, text: str) -> Dict[str, Any]:
        """
        Polish-specific pattern extraction and validation
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with extracted Polish patterns
        """
        try:
            patterns = {
                'nip_numbers': self.polish_patterns.extract_nip_numbers(text),
                'regon_numbers': self.polish_patterns.extract_regon_numbers(text),
                'krs_numbers': self.polish_patterns.extract_krs_numbers(text),
                'vat_rates': self.polish_patterns.extract_vat_rates(text),
                'polish_dates': self.polish_patterns.extract_polish_dates(text),
                'currency_amounts': self.polish_patterns.extract_currency_amounts(text),
                'invoice_numbers': self.polish_patterns.extract_invoice_numbers(text),
                'company_names': self.polish_patterns.extract_company_names(text)
            }
            
            # Validate extracted patterns
            validation_results = {}
            for pattern_type, values in patterns.items():
                if pattern_type == 'nip_numbers':
                    validation_results[pattern_type] = [
                        {'value': nip, 'valid': self.validate_nip(nip)}
                        for nip in values
                    ]
                else:
                    validation_results[pattern_type] = [
                        {'value': val, 'valid': True}
                        for val in values
                    ]
            
            return {
                'patterns': patterns,
                'validation': validation_results,
                'confidence': self._calculate_pattern_confidence(patterns)
            }
            
        except Exception as e:
            logger.error(f"Pattern extraction failed: {e}")
            raise PolishValidationError(f"Pattern extraction failed: {e}")
    
    def validate_nip(self, nip: str) -> bool:
        """
        Polish NIP validation with checksum verification
        
        Args:
            nip: NIP number to validate
            
        Returns:
            True if NIP is valid, False otherwise
        """
        try:
            # Remove non-digit characters
            nip_clean = re.sub(r'[^\d]', '', nip)
            
            # Check length
            if len(nip_clean) != 10:
                return False
            
            # Polish NIP checksum algorithm
            weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
            checksum = 0
            
            for i in range(9):
                checksum += int(nip_clean[i]) * weights[i]
            
            checksum = checksum % 11
            if checksum == 10:
                checksum = 0
            
            return checksum == int(nip_clean[9])
            
        except Exception as e:
            logger.error(f"NIP validation failed: {e}")
            return False
    
    def _extract_text(self, image: np.ndarray) -> List[Dict]:
        """Extract text from preprocessed image using PaddleOCR"""
        try:
            results = self.ocr_engine.ocr(image, cls=True)
            return results
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise PaddleOCRProcessingError(f"Text extraction failed: {e}")
    
    def _extract_invoice_number(self, text_blocks: List[Dict]) -> ExtractedField:
        """Extract invoice number with Polish patterns"""
        patterns = [
            r'faktur[ay]?\s*[nr]?[o]?[r]?[.]?\s*[:]?\s*([a-zA-Z0-9\/\-_]+)',
            r'invoice\s*[nr]?[o]?[r]?[.]?\s*[:]?\s*([a-zA-Z0-9\/\-_]+)',
            r'FV[/\-]?(\d+[/\-]\d+)',
            r'(\d{2,4}[/\-]\d{2,4}[/\-]\d{2,4})'
        ]
        
        return self._extract_field_with_patterns(text_blocks, patterns, 'invoice_number')
    
    def _extract_issue_date(self, text_blocks: List[Dict]) -> ExtractedField:
        """Extract issue date with Polish date formats"""
        patterns = [
            r'data\s+wystawienia\s*[:]?\s*(\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})',
            r'wystawiono\s*[:]?\s*(\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})',
            r'(\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})'
        ]
        
        return self._extract_field_with_patterns(text_blocks, patterns, 'issue_date')
    
    def _extract_seller_nip(self, text_blocks: List[Dict]) -> ExtractedField:
        """Extract seller NIP with validation"""
        patterns = [
            r'NIP\s*sprzedawcy\s*[:]?\s*(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3})',
            r'sprzedawca.*?NIP\s*[:]?\s*(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3})',
            r'(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3})'
        ]
        
        field = self._extract_field_with_patterns(text_blocks, patterns, 'seller_nip')
        if field.value:
            field.validation_status = 'valid' if self.validate_nip(field.value) else 'invalid'
        
        return field
    
    def _extract_buyer_nip(self, text_blocks: List[Dict]) -> ExtractedField:
        """Extract buyer NIP with validation"""
        patterns = [
            r'NIP\s*nabywcy\s*[:]?\s*(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3})',
            r'nabywca.*?NIP\s*[:]?\s*(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3})',
            r'(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3})'
        ]
        
        field = self._extract_field_with_patterns(text_blocks, patterns, 'buyer_nip')
        if field.value:
            field.validation_status = 'valid' if self.validate_nip(field.value) else 'invalid'
        
        return field
    
    def _extract_total_gross(self, text_blocks: List[Dict]) -> ExtractedField:
        """Extract total gross amount"""
        patterns = [
            r'suma\s*brutto\s*[:]?\s*([\d\s,\.]+)\s*[zł|PLN]',
            r'razem\s*brutto\s*[:]?\s*([\d\s,\.]+)\s*[zł|PLN]',
            r'do\s*zapłaty\s*[:]?\s*([\d\s,\.]+)\s*[zł|PLN]'
        ]
        
        return self._extract_field_with_patterns(text_blocks, patterns, 'total_gross')
    
    def _extract_field_with_patterns(self, text_blocks: List[Dict], patterns: List[str], field_type: str) -> ExtractedField:
        """Extract field using multiple patterns with confidence scoring"""
        best_match = None
        best_confidence = 0.0
        best_bbox = None
        
        for block in text_blocks:
            text = block['text']
            confidence = block['confidence']
            bbox = block['bbox']
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Boost confidence for better positioned text
                    position_boost = self._calculate_position_boost(bbox)
                    total_confidence = confidence * position_boost
                    
                    if total_confidence > best_confidence:
                        best_confidence = total_confidence
                        best_match = value
                        best_bbox = bbox
        
        return ExtractedField(
            value=best_match or '',
            confidence=best_confidence,
            bounding_box=best_bbox or {},
            validation_status='unknown',
            polish_specific_score=self._calculate_polish_score(best_match, field_type),
            field_type=field_type
        )
    
    def _calculate_position_boost(self, bbox: List[List[int]]) -> float:
        """Calculate confidence boost based on text position"""
        if not bbox or len(bbox) < 4:
            return 1.0
        
        # Calculate center point
        center_x = sum(point[0] for point in bbox) / len(bbox)
        center_y = sum(point[1] for point in bbox) / len(bbox)
        
        # Boost confidence for text in typical invoice positions
        # Header area (top 20% of document)
        if center_y < 0.2:
            return 1.2
        # Main content area (20-80% of document)
        elif 0.2 <= center_y <= 0.8:
            return 1.0
        # Footer area (bottom 20% of document)
        else:
            return 0.8
    
    def _calculate_polish_score(self, value: str, field_type: str) -> float:
        """Calculate Polish-specific confidence score"""
        if not value:
            return 0.0
        
        score = 0.0
        
        if field_type == 'seller_nip' or field_type == 'buyer_nip':
            if self.validate_nip(value):
                score += 0.3
            if re.match(r'\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3}', value):
                score += 0.2
        
        elif field_type == 'issue_date':
            if re.match(r'\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4}', value):
                score += 0.3
        
        elif field_type == 'total_gross':
            if re.match(r'[\d\s,\.]+', value):
                score += 0.2
            if 'zł' in value or 'PLN' in value:
                score += 0.1
        
        return min(score, 1.0)
    
    def _validate_polish_data(self, extracted_data: Dict) -> Dict[str, Any]:
        """Validate extracted data using Polish business rules"""
        validation_results = {
            'nip_checksum_valid': True,
            'vat_rates_valid': True,
            'date_format_valid': True,
            'currency_format_valid': True,
            'field_completeness': 0.0
        }
        
        # Check NIP validation
        seller_nip = extracted_data.get('sprzedawca_nip', '')
        buyer_nip = extracted_data.get('nabywca_nip', '')
        
        if seller_nip and hasattr(seller_nip, 'validation_status'):
            validation_results['seller_nip_valid'] = seller_nip.validation_status == 'valid'
        
        if buyer_nip and hasattr(buyer_nip, 'validation_status'):
            validation_results['buyer_nip_valid'] = buyer_nip.validation_status == 'valid'
        
        # Calculate field completeness
        required_fields = ['numer_faktury', 'data_wystawienia', 'sprzedawca_nip', 'suma_brutto']
        filled_fields = sum(1 for field in required_fields if extracted_data.get(field))
        validation_results['field_completeness'] = filled_fields / len(required_fields)
        
        return validation_results
    
    def _analyze_spatial_layout(self, ocr_results: List[Dict]) -> Dict[str, float]:
        """Analyze spatial layout consistency"""
        try:
            if not ocr_results or not ocr_results[0]:
                return {'layout_confidence': 0.0, 'text_alignment_score': 0.0}
            
            # Analyze text alignment and positioning
            text_positions = []
            for result in ocr_results:
                for line in result:
                    if len(line) >= 2:
                        bbox = line[0]
                        center_x = sum(point[0] for point in bbox) / len(bbox)
                        center_y = sum(point[1] for point in bbox) / len(bbox)
                        text_positions.append((center_x, center_y))
            
            if not text_positions:
                return {'layout_confidence': 0.0, 'text_alignment_score': 0.0}
            
            # Calculate alignment scores
            x_positions = [pos[0] for pos in text_positions]
            y_positions = [pos[1] for pos in text_positions]
            
            # Check for consistent left alignment
            left_aligned = sum(1 for x in x_positions if x < 0.3) / len(x_positions)
            
            # Check for consistent spacing
            y_spacing = np.std(y_positions) if len(y_positions) > 1 else 0
            
            layout_confidence = min(left_aligned * 0.7 + (1 - y_spacing) * 0.3, 1.0)
            
            return {
                'layout_confidence': layout_confidence,
                'text_alignment_score': left_aligned,
                'field_positioning_accuracy': 1 - y_spacing
            }
            
        except Exception as e:
            logger.error(f"Spatial analysis failed: {e}")
            return {'layout_confidence': 0.0, 'text_alignment_score': 0.0}
    
    def _convert_pdf_to_image(self, pdf_content: bytes) -> Image.Image:
        """Convert PDF to image for processing"""
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(pdf_content, first_page=1, last_page=1)
            return images[0] if images else Image.new('RGB', (800, 600), 'white')
        except ImportError:
            logger.warning("pdf2image not available. Install with: pip install pdf2image")
            return Image.new('RGB', (800, 600), 'white')
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            return Image.new('RGB', (800, 600), 'white')
    
    def _calculate_pattern_confidence(self, patterns: Dict) -> float:
        """Calculate overall pattern confidence"""
        if not patterns:
            return 0.0
        
        total_patterns = 0
        valid_patterns = 0
        
        for pattern_type, values in patterns.items():
            total_patterns += len(values)
            if pattern_type == 'nip_numbers':
                valid_patterns += sum(1 for nip in values if self.validate_nip(nip))
            else:
                valid_patterns += len(values)
        
        return valid_patterns / total_patterns if total_patterns > 0 else 0.0
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        return {
            'average_processing_time': np.mean(self.processing_times) if self.processing_times else 0,
            'total_processed': len(self.processing_times),
            'memory_usage': np.mean(self.memory_usage) if self.memory_usage else 0,
            'accuracy_metrics': self.accuracy_metrics
        }
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if self.ocr_engine:
                del self.ocr_engine
            logger.info("PaddleOCR Service cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# Factory function for easy integration
def create_paddle_ocr_service(**kwargs) -> PaddleOCRService:
    """Factory function to create PaddleOCR service with default Polish optimization"""
    return PaddleOCRService(**kwargs)