"""
Tesseract OCR Engine Implementation with Polish Language Optimization

This module provides a Tesseract-based OCR engine optimized for Polish invoices
with advanced preprocessing and confidence scoring.
"""

import logging
import time
import tempfile
import os
import io
from typing import Dict, Any, Optional, List, Tuple
from decimal import Decimal
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from pdf2image import convert_from_bytes

from .ocr_engine_service import OCREngineService
from .polish_invoice_processor import PolishInvoiceProcessor

logger = logging.getLogger(__name__)


class TesseractOCREngine(OCREngineService):
    """
    Tesseract OCR Engine with Polish language optimization
    
    Features:
    - Polish language support with custom configuration
    - Advanced image preprocessing for better accuracy
    - Confidence scoring and word-level analysis
    - PDF to image conversion
    - Optimized settings for invoice processing
    """
    
    def __init__(self, 
                 languages: str = 'pol+eng',
                 config: Optional[str] = None,
                 preprocessing_enabled: bool = True):
        """
        Initialize Tesseract OCR Engine
        
        Args:
            languages: Tesseract language codes (default: 'pol+eng')
            config: Custom Tesseract configuration string
            preprocessing_enabled: Enable image preprocessing
        """
        super().__init__("tesseract")
        
        self.languages = languages
        self.preprocessing_enabled = preprocessing_enabled
        self.polish_processor = PolishInvoiceProcessor()
        
        # Default Tesseract configuration optimized for Polish invoices
        self.default_config = (
            '--oem 3 --psm 6 '  # LSTM OCR Engine Mode, Uniform block of text
            '-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            'ĄĆĘŁŃÓŚŹŻąćęłńóśźż.,/-:()[]{}%€$zł '  # Polish characters and common symbols
            '-c preserve_interword_spaces=1 '
            '-c textord_really_old_xheight=1 '
            '-c textord_min_linesize=2.5'
        )
        
        self.config = config or self.default_config
        
        # Preprocessing parameters
        self.preprocessing_params = {
            'deskew_enabled': True,
            'noise_removal': True,
            'contrast_enhancement': True,
            'resolution_optimization': True,
            'morphological_operations': True
        }
    
    def initialize(self) -> bool:
        """
        Initialize Tesseract engine and verify installation
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Check if Tesseract is installed
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            
            # Check if Polish language pack is available
            available_languages = pytesseract.get_languages()
            required_langs = self.languages.split('+')
            
            missing_langs = [lang for lang in required_langs if lang not in available_languages]
            if missing_langs:
                logger.error(f"Missing Tesseract language packs: {missing_langs}")
                logger.info(f"Available languages: {available_languages}")
                return False
            
            logger.info(f"Tesseract initialized with languages: {self.languages}")
            
            # Test basic functionality
            test_image = Image.new('RGB', (100, 50), color='white')
            test_result = pytesseract.image_to_string(test_image, lang=self.languages, config=self.config)
            
            self.is_initialized = True
            logger.info("Tesseract OCR engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Tesseract: {e}")
            self.is_initialized = False
            return False
    
    def process_document(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process document using Tesseract OCR with Polish optimization
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        start_time = time.time()
        
        # Validate input
        is_valid, error_msg = self.validate_input(file_content, mime_type)
        if not is_valid:
            raise ValueError(error_msg)
        
        if not self.is_initialized:
            raise RuntimeError("Tesseract engine not initialized")
        
        try:
            # Convert to image(s)
            images = self._convert_to_images(file_content, mime_type)
            
            # Process each image
            all_text = []
            all_confidences = []
            all_word_data = []
            
            for i, image in enumerate(images):
                logger.debug(f"Processing image {i+1}/{len(images)}")
                
                # Preprocess image if enabled
                if self.preprocessing_enabled:
                    processed_image = self._preprocess_image(image)
                else:
                    processed_image = image
                
                # Extract text with detailed data
                text_data = self._extract_text_with_confidence(processed_image)
                
                all_text.append(text_data['text'])
                all_confidences.extend(text_data['word_confidences'])
                all_word_data.extend(text_data['word_data'])
            
            # Combine results
            combined_text = '\n'.join(all_text)
            processing_time = time.time() - start_time
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(all_confidences)
            
            # Create result dictionary
            result = {
                'text': combined_text,
                'confidence_score': overall_confidence,
                'word_confidences': all_confidences,
                'word_data': all_word_data,
                'processing_time': processing_time,
                'engine_name': self.engine_name,
                'languages_used': self.languages,
                'pages_processed': len(images),
                'metadata': {
                    'tesseract_version': str(pytesseract.get_tesseract_version()),
                    'config_used': self.config,
                    'preprocessing_enabled': self.preprocessing_enabled
                }
            }
            
            # Apply Polish-specific enhancements
            if 'pol' in self.languages:
                result = self._apply_polish_enhancements(result)
            
            # Update performance metrics
            success = overall_confidence > 50.0  # Consider successful if confidence > 50%
            self.update_performance_metrics(processing_time, overall_confidence, success)
            
            logger.info(f"Tesseract processing completed in {processing_time:.2f}s with {overall_confidence:.1f}% confidence")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Tesseract processing failed after {processing_time:.2f}s: {e}")
            self.update_performance_metrics(processing_time, 0.0, False)
            raise
    
    def get_confidence_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate confidence score from Tesseract result
        
        Args:
            result: OCR processing result
            
        Returns:
            float: Confidence score between 0.0 and 100.0
        """
        return result.get('confidence_score', 0.0)
    
    def _convert_to_images(self, file_content: bytes, mime_type: str) -> List[Image.Image]:
        """
        Convert file content to PIL Images
        
        Args:
            file_content: Binary file content
            mime_type: MIME type of the file
            
        Returns:
            List of PIL Image objects
        """
        if mime_type == 'application/pdf':
            # Convert PDF to images
            try:
                images = convert_from_bytes(
                    file_content,
                    dpi=300,  # High DPI for better OCR accuracy
                    fmt='RGB',
                    thread_count=2
                )
                logger.debug(f"Converted PDF to {len(images)} images")
                return images
            except Exception as e:
                logger.error(f"PDF conversion failed: {e}")
                raise ValueError(f"Failed to convert PDF: {e}")
        
        else:
            # Handle image files
            try:
                image = Image.open(io.BytesIO(file_content))
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                return [image]
            except Exception as e:
                logger.error(f"Image loading failed: {e}")
                raise ValueError(f"Failed to load image: {e}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Apply preprocessing to improve OCR accuracy
        
        Args:
            image: Input PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Apply preprocessing steps
            if self.preprocessing_params['resolution_optimization']:
                cv_image = self._optimize_resolution(cv_image)
            
            if self.preprocessing_params['deskew_enabled']:
                cv_image = self._deskew_image(cv_image)
            
            if self.preprocessing_params['noise_removal']:
                cv_image = self._remove_noise(cv_image)
            
            if self.preprocessing_params['contrast_enhancement']:
                cv_image = self._enhance_contrast(cv_image)
            
            if self.preprocessing_params['morphological_operations']:
                cv_image = self._apply_morphological_operations(cv_image)
            
            # Convert back to PIL
            processed_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            logger.debug("Image preprocessing completed")
            return processed_image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}, using original image")
            return image
    
    def _optimize_resolution(self, image: np.ndarray) -> np.ndarray:
        """Optimize image resolution for OCR"""
        height, width = image.shape[:2]
        
        # Target resolution for optimal OCR (around 300 DPI equivalent)
        target_height = 2000
        
        if height < target_height:
            # Upscale small images
            scale_factor = target_height / height
            new_width = int(width * scale_factor)
            image = cv2.resize(image, (new_width, target_height), interpolation=cv2.INTER_CUBIC)
        elif height > target_height * 2:
            # Downscale very large images
            scale_factor = target_height / height
            new_width = int(width * scale_factor)
            image = cv2.resize(image, (new_width, target_height), interpolation=cv2.INTER_AREA)
        
        return image
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Correct image skew/rotation"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use Hough Line Transform to detect skew
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            angles = []
            for rho, theta in lines[:10]:  # Use first 10 lines
                angle = theta * 180 / np.pi
                if angle < 45:
                    angles.append(angle)
                elif angle > 135:
                    angles.append(angle - 180)
            
            if angles:
                median_angle = np.median(angles)
                if abs(median_angle) > 0.5:  # Only correct if skew is significant
                    height, width = image.shape[:2]
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    image = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                         flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return image
    
    def _remove_noise(self, image: np.ndarray) -> np.ndarray:
        """Remove noise from image"""
        # Apply bilateral filter to reduce noise while preserving edges
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Apply morphological opening to remove small noise
        kernel = np.ones((2, 2), np.uint8)
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_OPEN, kernel)
        
        return denoised
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels and convert back to BGR
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def _apply_morphological_operations(self, image: np.ndarray) -> np.ndarray:
        """Apply morphological operations to improve text clarity"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply morphological closing to connect broken text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
        closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to BGR
        result = cv2.cvtColor(closed, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def _extract_text_with_confidence(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text with word-level confidence data
        
        Args:
            image: PIL Image to process
            
        Returns:
            Dictionary with text and confidence data
        """
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(
                image, 
                lang=self.languages, 
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=self.languages,
                config=self.config
            )
            
            # Process word-level data
            word_confidences = []
            word_data = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:  # Only include words with confidence > 0
                    word_info = {
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'bbox': {
                            'left': data['left'][i],
                            'top': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        },
                        'block_num': data['block_num'][i],
                        'par_num': data['par_num'][i],
                        'line_num': data['line_num'][i],
                        'word_num': data['word_num'][i]
                    }
                    
                    word_confidences.append(int(data['conf'][i]))
                    word_data.append(word_info)
            
            return {
                'text': text,
                'word_confidences': word_confidences,
                'word_data': word_data
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {
                'text': '',
                'word_confidences': [],
                'word_data': []
            }
    
    def _calculate_overall_confidence(self, word_confidences: List[int]) -> float:
        """
        Calculate overall confidence score from word confidences
        
        Args:
            word_confidences: List of word-level confidence scores
            
        Returns:
            Overall confidence score
        """
        if not word_confidences:
            return 0.0
        
        # Use weighted average with higher weight for higher confidence words
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for conf in word_confidences:
            # Weight is proportional to confidence (higher confidence = higher weight)
            weight = max(1.0, conf / 100.0)
            total_weighted_score += conf * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_weighted_score / total_weight
        else:
            return 0.0
    
    def _apply_polish_enhancements(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Polish-specific enhancements to OCR result
        
        Args:
            result: Base OCR result
            
        Returns:
            Enhanced result with Polish optimizations
        """
        try:
            # Use Polish processor for enhancement
            enhanced_data = self.polish_processor.enhance_extraction(
                result['text'], 
                result
            )
            
            # Merge enhanced data back into result
            result.update(enhanced_data)
            
            # Add Polish-specific confidence boost
            polish_boost = enhanced_data.get('polish_confidence_boost', 0.0)
            if polish_boost > 0:
                result['confidence_score'] = min(100.0, result['confidence_score'] + polish_boost)
                result['polish_enhancement_applied'] = True
                result['polish_confidence_boost'] = polish_boost
            
            logger.debug(f"Applied Polish enhancements, confidence boost: {polish_boost:.1f}%")
            
        except Exception as e:
            logger.warning(f"Polish enhancement failed: {e}")
            result['polish_enhancement_error'] = str(e)
        
        return result


