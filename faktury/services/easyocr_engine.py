"""
EasyOCR Engine Implementation with Confidence Scoring

This module provides an EasyOCR-based OCR engine optimized for Polish text
with advanced confidence scoring and preprocessing capabilities.
"""

import logging
import time
import tempfile
import os
import io
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from PIL import Image
import cv2
from pdf2image import convert_from_bytes

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None

from .ocr_engine_service import OCREngineService
from .polish_invoice_processor import PolishInvoiceProcessor

logger = logging.getLogger(__name__)


class EasyOCREngine(OCREngineService):
    """
    EasyOCR Engine with Polish language support and confidence scoring
    
    Features:
    - Multi-language support (Polish + English)
    - GPU acceleration support
    - Advanced confidence scoring
    - Bounding box detection
    - Optimized for handwritten and low-quality text
    """
    
    def __init__(self, 
                 languages: List[str] = None,
                 gpu: bool = False,
                 model_storage_directory: Optional[str] = None,
                 download_enabled: bool = True):
        """
        Initialize EasyOCR Engine
        
        Args:
            languages: List of language codes (default: ['pl', 'en'])
            gpu: Enable GPU acceleration if available
            model_storage_directory: Directory to store models
            download_enabled: Allow automatic model downloading
        """
        super().__init__("easyocr")
        
        if not EASYOCR_AVAILABLE:
            raise ImportError("EasyOCR not available. Install with: pip install easyocr")
        
        self.languages = languages or ['pl', 'en']
        self.gpu = gpu
        self.model_storage_directory = model_storage_directory
        self.download_enabled = download_enabled
        self.reader = None
        self.polish_processor = PolishInvoiceProcessor()
        
        # EasyOCR configuration
        self.easyocr_config = {
            'paragraph': False,  # Don't group text into paragraphs
            'width_ths': 0.7,   # Text width threshold
            'height_ths': 0.7,  # Text height threshold
            'decoder': 'greedy', # Decoding method
            'beamWidth': 5,     # Beam search width
            'batch_size': 1,    # Batch size for processing
            'workers': 0,       # Number of workers (0 = auto)
            'allowlist': None,  # Character whitelist (None = all)
            'blocklist': None,  # Character blacklist
            'detail': 1,        # Return detailed results with bounding boxes
            'rotation_info': None,  # Rotation information
            'text_threshold': 0.7,  # Text detection threshold
            'low_text': 0.4,    # Low text threshold
            'link_threshold': 0.4,  # Link threshold
            'canvas_size': 2560,    # Canvas size for text detection
            'mag_ratio': 1.5,   # Magnification ratio
            'slope_ths': 0.1,   # Slope threshold
            'ycenter_ths': 0.5, # Y-center threshold
            'add_margin': 0.1,  # Add margin to bounding boxes
        }
    
    def initialize(self) -> bool:
        """
        Initialize EasyOCR reader with specified languages
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info(f"Initializing EasyOCR with languages: {self.languages}")
            
            # Check GPU availability
            if self.gpu:
                try:
                    import torch
                    if torch.cuda.is_available():
                        logger.info("GPU acceleration enabled")
                    else:
                        logger.warning("GPU requested but not available, using CPU")
                        self.gpu = False
                except ImportError:
                    logger.warning("PyTorch not available, using CPU")
                    self.gpu = False
            
            # Initialize EasyOCR reader
            self.reader = easyocr.Reader(
                self.languages,
                gpu=self.gpu,
                model_storage_directory=self.model_storage_directory,
                download_enabled=self.download_enabled,
                verbose=False
            )
            
            # Test basic functionality
            test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
            test_result = self.reader.readtext(test_image)
            
            self.is_initialized = True
            logger.info("EasyOCR engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            self.is_initialized = False
            return False
    
    def process_document(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process document using EasyOCR with confidence scoring
        
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
        
        if not self.is_initialized or self.reader is None:
            raise RuntimeError("EasyOCR engine not initialized")
        
        try:
            # Convert to images
            images = self._convert_to_images(file_content, mime_type)
            
            # Process each image
            all_text = []
            all_confidences = []
            all_word_data = []
            all_bounding_boxes = []
            
            for i, image in enumerate(images):
                logger.debug(f"Processing image {i+1}/{len(images)} with EasyOCR")
                
                # Convert PIL to numpy array
                image_array = np.array(image)
                
                # Apply preprocessing if needed
                processed_image = self._preprocess_for_easyocr(image_array)
                
                # Extract text with EasyOCR
                results = self.reader.readtext(
                    processed_image,
                    paragraph=self.easyocr_config['paragraph'],
                    width_ths=self.easyocr_config['width_ths'],
                    height_ths=self.easyocr_config['height_ths'],
                    decoder=self.easyocr_config['decoder'],
                    beamWidth=self.easyocr_config['beamWidth'],
                    batch_size=self.easyocr_config['batch_size'],
                    workers=self.easyocr_config['workers'],
                    allowlist=self.easyocr_config['allowlist'],
                    blocklist=self.easyocr_config['blocklist'],
                    detail=self.easyocr_config['detail'],
                    rotation_info=self.easyocr_config['rotation_info'],
                    text_threshold=self.easyocr_config['text_threshold'],
                    low_text=self.easyocr_config['low_text'],
                    link_threshold=self.easyocr_config['link_threshold'],
                    canvas_size=self.easyocr_config['canvas_size'],
                    mag_ratio=self.easyocr_config['mag_ratio'],
                    slope_ths=self.easyocr_config['slope_ths'],
                    ycenter_ths=self.easyocr_config['ycenter_ths'],
                    add_margin=self.easyocr_config['add_margin']
                )
                
                # Process results
                page_text, page_confidences, page_word_data, page_bboxes = self._process_easyocr_results(results)
                
                all_text.append(page_text)
                all_confidences.extend(page_confidences)
                all_word_data.extend(page_word_data)
                all_bounding_boxes.extend(page_bboxes)
            
            # Combine results
            combined_text = '\n'.join(all_text)
            processing_time = time.time() - start_time
            
            # Calculate overall confidence
            overall_confidence = self._calculate_confidence_score(all_confidences)
            
            # Create result dictionary
            result = {
                'text': combined_text,
                'confidence_score': overall_confidence,
                'word_confidences': all_confidences,
                'word_data': all_word_data,
                'bounding_boxes': all_bounding_boxes,
                'processing_time': processing_time,
                'engine_name': self.engine_name,
                'languages_used': self.languages,
                'pages_processed': len(images),
                'metadata': {
                    'easyocr_version': easyocr.__version__ if hasattr(easyocr, '__version__') else 'unknown',
                    'gpu_used': self.gpu,
                    'config_used': self.easyocr_config.copy()
                }
            }
            
            # Apply Polish-specific enhancements
            if 'pl' in self.languages:
                result = self._apply_polish_enhancements(result)
            
            # Update performance metrics
            success = overall_confidence > 60.0  # EasyOCR typically has higher confidence
            self.update_performance_metrics(processing_time, overall_confidence, success)
            
            logger.info(f"EasyOCR processing completed in {processing_time:.2f}s with {overall_confidence:.1f}% confidence")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"EasyOCR processing failed after {processing_time:.2f}s: {e}")
            self.update_performance_metrics(processing_time, 0.0, False)
            raise
    
    def get_confidence_score(self, result: Dict[str, Any]) -> float:
        """
        Get confidence score from EasyOCR result
        
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
                    fmt='RGB'
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
    
    def _preprocess_for_easyocr(self, image: np.ndarray) -> np.ndarray:
        """
        Apply preprocessing optimized for EasyOCR
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        try:
            # EasyOCR works well with minimal preprocessing
            # Apply only essential improvements
            
            # Ensure image is in correct format
            if len(image.shape) == 3 and image.shape[2] == 3:
                # RGB image - convert to BGR for OpenCV operations
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Resize if image is too small (EasyOCR works better with larger images)
            height, width = image.shape[:2]
            if height < 600 or width < 600:
                scale_factor = max(600 / height, 600 / width)
                new_height = int(height * scale_factor)
                new_width = int(width * scale_factor)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Light denoising (EasyOCR is robust to noise)
            image = cv2.bilateralFilter(image, 5, 50, 50)
            
            # Convert back to RGB for EasyOCR
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            return image
            
        except Exception as e:
            logger.warning(f"EasyOCR preprocessing failed: {e}, using original image")
            return image
    
    def _process_easyocr_results(self, results: List[Tuple]) -> Tuple[str, List[float], List[Dict], List[Dict]]:
        """
        Process EasyOCR results into standardized format
        
        Args:
            results: EasyOCR results list
            
        Returns:
            Tuple of (text, confidences, word_data, bounding_boxes)
        """
        text_parts = []
        confidences = []
        word_data = []
        bounding_boxes = []
        
        for i, result in enumerate(results):
            if len(result) >= 3:
                bbox, text, confidence = result[:3]
                
                # Convert confidence to percentage
                confidence_pct = confidence * 100.0
                
                # Extract bounding box coordinates
                if isinstance(bbox, list) and len(bbox) >= 4:
                    # EasyOCR returns 4 corner points
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    bbox_dict = {
                        'left': int(min(x_coords)),
                        'top': int(min(y_coords)),
                        'width': int(max(x_coords) - min(x_coords)),
                        'height': int(max(y_coords) - min(y_coords)),
                        'corners': bbox
                    }
                else:
                    bbox_dict = {'left': 0, 'top': 0, 'width': 0, 'height': 0, 'corners': []}
                
                # Create word data entry
                word_info = {
                    'text': text,
                    'confidence': confidence_pct,
                    'bbox': bbox_dict,
                    'word_index': i
                }
                
                text_parts.append(text)
                confidences.append(confidence_pct)
                word_data.append(word_info)
                bounding_boxes.append(bbox_dict)
        
        # Join text with spaces
        combined_text = ' '.join(text_parts)
        
        return combined_text, confidences, word_data, bounding_boxes
    
    def _calculate_confidence_score(self, confidences: List[float]) -> float:
        """
        Calculate overall confidence score from word confidences
        
        Args:
            confidences: List of word-level confidence scores
            
        Returns:
            Overall confidence score
        """
        if not confidences:
            return 0.0
        
        # EasyOCR confidence calculation
        # Use weighted average with emphasis on higher confidence words
        
        # Filter out very low confidence words (likely noise)
        filtered_confidences = [c for c in confidences if c > 10.0]
        
        if not filtered_confidences:
            return 0.0
        
        # Calculate weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        
        for conf in filtered_confidences:
            # Weight increases with confidence
            weight = conf / 100.0
            weighted_sum += conf * weight
            total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return sum(filtered_confidences) / len(filtered_confidences)
    
    def _apply_polish_enhancements(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Polish-specific enhancements to EasyOCR result
        
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
            
            # EasyOCR-specific Polish optimizations
            result = self._apply_easyocr_polish_optimizations(result)
            
            logger.debug(f"Applied Polish enhancements to EasyOCR result, confidence boost: {polish_boost:.1f}%")
            
        except Exception as e:
            logger.warning(f"Polish enhancement failed: {e}")
            result['polish_enhancement_error'] = str(e)
        
        return result
    
    def _apply_easyocr_polish_optimizations(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply EasyOCR-specific Polish optimizations
        
        Args:
            result: OCR result to optimize
            
        Returns:
            Optimized result
        """
        try:
            # EasyOCR sometimes splits Polish words incorrectly
            # Try to merge words that should be together
            
            word_data = result.get('word_data', [])
            if not word_data:
                return result
            
            # Sort words by position (top to bottom, left to right)
            sorted_words = sorted(word_data, key=lambda w: (w['bbox']['top'], w['bbox']['left']))
            
            # Group words into lines based on vertical position
            lines = []
            current_line = []
            line_threshold = 20  # pixels
            
            for word in sorted_words:
                if not current_line:
                    current_line.append(word)
                else:
                    # Check if word is on the same line
                    last_word = current_line[-1]
                    if abs(word['bbox']['top'] - last_word['bbox']['top']) <= line_threshold:
                        current_line.append(word)
                    else:
                        lines.append(current_line)
                        current_line = [word]
            
            if current_line:
                lines.append(current_line)
            
            # Reconstruct text with proper spacing
            reconstructed_lines = []
            for line in lines:
                line_text = ' '.join([word['text'] for word in line])
                reconstructed_lines.append(line_text)
            
            result['text'] = '\n'.join(reconstructed_lines)
            result['easyocr_polish_optimization_applied'] = True
            
        except Exception as e:
            logger.warning(f"EasyOCR Polish optimization failed: {e}")
        
        return result
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages
        
        Returns:
            List of supported language codes
        """
        if self.reader:
            return self.reader.lang_list
        else:
            # Default supported languages
            return ['pl', 'en', 'de', 'fr', 'es', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']
    
    def set_gpu_usage(self, use_gpu: bool) -> bool:
        """
        Enable or disable GPU usage (requires reinitialization)
        
        Args:
            use_gpu: Whether to use GPU
            
        Returns:
            bool: True if setting was applied successfully
        """
        if self.gpu != use_gpu:
            self.gpu = use_gpu
            self.is_initialized = False
            return self.initialize()
        return True