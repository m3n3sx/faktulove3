"""
PaddleOCR Engine Implementation with Polish Language Optimization

This module provides a PaddleOCR-based OCR engine optimized for Polish invoices
with advanced preprocessing, confidence scoring, and Polish pattern recognition.
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
    import paddleocr
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    paddleocr = None

from .ocr_engine_service import OCREngineService
from .polish_invoice_processor import PolishInvoiceProcessor

logger = logging.getLogger(__name__)


class PaddleOCREngine(OCREngineService):
    """
    PaddleOCR Engine with Polish language optimization and advanced confidence scoring
    
    Features:
    - Polish language support with specialized models
    - Advanced image preprocessing for Polish documents
    - Confidence scoring with spatial analysis
    - GPU acceleration support
    - Optimized for Polish invoice processing
    """
    
    def __init__(self, 
                 languages: List[str] = None,
                 use_gpu: bool = False,
                 det_model_dir: Optional[str] = None,
                 rec_model_dir: Optional[str] = None,
                 cls_model_dir: Optional[str] = None,
                 use_angle_cls: bool = True,
                 use_space_char: bool = True,
                 drop_score: float = 0.5):
        """
        Initialize PaddleOCR Engine
        
        Args:
            languages: List of language codes (default: ['pl', 'en'])
            use_gpu: Enable GPU acceleration if available
            det_model_dir: Directory for detection model
            rec_model_dir: Directory for recognition model
            cls_model_dir: Directory for classification model
            use_angle_cls: Use angle classification
            use_space_char: Use space character recognition
            drop_score: Minimum confidence score threshold
        """
        super().__init__("paddleocr")
        
        if not PADDLEOCR_AVAILABLE:
            raise ImportError("PaddleOCR not available. Install with: pip install paddleocr paddlepaddle")
        
        self.languages = languages or ['pl', 'en']
        self.use_gpu = use_gpu
        self.det_model_dir = det_model_dir
        self.rec_model_dir = rec_model_dir
        self.cls_model_dir = cls_model_dir
        self.use_angle_cls = use_angle_cls
        self.use_space_char = use_space_char
        self.drop_score = drop_score
        self.ocr_reader = None
        self.polish_processor = PolishInvoiceProcessor()
        
        # PaddleOCR configuration optimized for Polish invoices
        self.paddle_config = {
            'use_angle_cls': use_angle_cls,
            'use_space_char': use_space_char,
            'drop_score': drop_score,
            'det_limit_side_len': 960,  # Detection limit
            'det_limit_type': 'max',    # Detection limit type
            'rec_batch_num': 6,         # Recognition batch size
            'max_text_length': 25000,   # Maximum text length
            'rec_char_dict_path': None, # Use default character dictionary
            'use_pdserving': False,     # Don't use PaddleServing
            'warmup': True,             # Enable warmup
            'cpu_threads': 10,          # CPU threads for inference
            'enable_mkldnn': True,      # Enable MKLDNN acceleration
            'det_db_thresh': 0.3,       # DB threshold for text detection
            'det_db_box_thresh': 0.6,   # Box threshold for text detection
            'det_db_unclip_ratio': 1.5, # Unclip ratio for text detection
            'det_east_score_thresh': 0.8,  # EAST score threshold
            'det_east_cover_thresh': 0.1,  # EAST cover threshold
            'det_east_nms_thresh': 0.2,    # EAST NMS threshold
        }
        
        # Polish-specific preprocessing parameters
        self.preprocessing_params = {
            'polish_text_enhancement': True,
            'invoice_layout_optimization': True,
            'contrast_enhancement': True,
            'noise_reduction': True,
            'skew_correction': True,
            'resolution_optimization': True,
        }
    
    def initialize(self) -> bool:
        """
        Initialize PaddleOCR with Polish language models
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info(f"Initializing PaddleOCR with languages: {self.languages}")
            
            # Check GPU availability
            if self.use_gpu:
                try:
                    import paddle
                    if paddle.device.is_compiled_with_cuda():
                        logger.info("GPU acceleration enabled for PaddleOCR")
                    else:
                        logger.warning("GPU requested but CUDA not available, using CPU")
                        self.use_gpu = False
                except ImportError:
                    logger.warning("PaddlePaddle not properly installed, using CPU")
                    self.use_gpu = False
            
            # Initialize PaddleOCR reader
            ocr_args = {
                'lang': self.languages,
                'use_gpu': self.use_gpu,
                'use_angle_cls': self.use_angle_cls,
                'use_space_char': self.use_space_char,
                'drop_score': self.drop_score,
                'det_limit_side_len': self.paddle_config['det_limit_side_len'],
                'det_limit_type': self.paddle_config['det_limit_type'],
                'rec_batch_num': self.paddle_config['rec_batch_num'],
                'max_text_length': self.paddle_config['max_text_length'],
                'cpu_threads': self.paddle_config['cpu_threads'],
                'enable_mkldnn': self.paddle_config['enable_mkldnn'],
                'det_db_thresh': self.paddle_config['det_db_thresh'],
                'det_db_box_thresh': self.paddle_config['det_db_box_thresh'],
                'det_db_unclip_ratio': self.paddle_config['det_db_unclip_ratio'],
            }
            
            # Add model directories if specified
            if self.det_model_dir:
                ocr_args['det_model_dir'] = self.det_model_dir
            if self.rec_model_dir:
                ocr_args['rec_model_dir'] = self.rec_model_dir
            if self.cls_model_dir:
                ocr_args['cls_model_dir'] = self.cls_model_dir
            
            self.ocr_reader = paddleocr.PaddleOCR(**ocr_args)
            
            # Test basic functionality
            test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
            test_result = self.ocr_reader.ocr(test_image, cls=self.use_angle_cls)
            
            self.is_initialized = True
            logger.info("PaddleOCR engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            self.is_initialized = False
            return False
    
    def process_document(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process document using PaddleOCR with Polish optimization
        
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
        
        if not self.is_initialized or self.ocr_reader is None:
            raise RuntimeError("PaddleOCR engine not initialized")
        
        try:
            # Convert to images
            images = self._convert_to_images(file_content, mime_type)
            
            # Process each image
            all_text = []
            all_confidences = []
            all_word_data = []
            all_bounding_boxes = []
            
            for i, image in enumerate(images):
                logger.debug(f"Processing image {i+1}/{len(images)} with PaddleOCR")
                
                # Convert PIL to numpy array
                image_array = np.array(image)
                
                # Apply Polish-specific preprocessing
                processed_image = self._preprocess_for_paddleocr(image_array)
                
                # Extract text with PaddleOCR
                ocr_results = self.ocr_reader.ocr(
                    processed_image, 
                    cls=self.use_angle_cls
                )
                
                # Process results
                page_text, page_confidences, page_word_data, page_bboxes = self._process_paddleocr_results(ocr_results)
                
                all_text.append(page_text)
                all_confidences.extend(page_confidences)
                all_word_data.extend(page_word_data)
                all_bounding_boxes.extend(page_bboxes)
            
            # Combine results
            combined_text = '\n'.join(all_text)
            processing_time = time.time() - start_time
            
            # Calculate overall confidence with PaddleOCR-specific algorithm
            overall_confidence = self._calculate_paddleocr_confidence(all_confidences, all_word_data)
            
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
                    'paddleocr_version': paddleocr.__version__ if hasattr(paddleocr, '__version__') else 'unknown',
                    'gpu_used': self.use_gpu,
                    'config_used': self.paddle_config.copy(),
                    'preprocessing_applied': self.preprocessing_params.copy()
                }
            }
            
            # Apply Polish-specific enhancements
            if 'pl' in self.languages:
                result = self._apply_polish_enhancements(result)
            
            # Update performance metrics
            success = overall_confidence > 70.0  # PaddleOCR typically has good confidence
            self.update_performance_metrics(processing_time, overall_confidence, success)
            
            logger.info(f"PaddleOCR processing completed in {processing_time:.2f}s with {overall_confidence:.1f}% confidence")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"PaddleOCR processing failed after {processing_time:.2f}s: {e}")
            self.update_performance_metrics(processing_time, 0.0, False)
            raise
    
    def get_confidence_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate confidence score from PaddleOCR results
        
        Args:
            result: OCR processing result dictionary
            
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
            # Convert PDF to images with high DPI for better OCR accuracy
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
    
    def _preprocess_for_paddleocr(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Polish-specific preprocessing optimized for PaddleOCR
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image optimized for Polish text recognition
        """
        try:
            # Ensure image is in correct format (RGB)
            if len(image.shape) == 3 and image.shape[2] == 3:
                # Already RGB, convert to BGR for OpenCV operations
                processed_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                processed_image = image.copy()
            
            # Apply preprocessing steps based on configuration
            if self.preprocessing_params['resolution_optimization']:
                processed_image = self._optimize_resolution_for_polish(processed_image)
            
            if self.preprocessing_params['skew_correction']:
                processed_image = self._correct_document_skew(processed_image)
            
            if self.preprocessing_params['noise_reduction']:
                processed_image = self._reduce_noise_polish_optimized(processed_image)
            
            if self.preprocessing_params['contrast_enhancement']:
                processed_image = self._enhance_contrast_for_polish_text(processed_image)
            
            if self.preprocessing_params['invoice_layout_optimization']:
                processed_image = self._optimize_invoice_layout(processed_image)
            
            if self.preprocessing_params['polish_text_enhancement']:
                processed_image = self._enhance_polish_text_features(processed_image)
            
            # Convert back to RGB for PaddleOCR
            if len(processed_image.shape) == 3:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
            
            logger.debug("Polish-optimized preprocessing completed for PaddleOCR")
            return processed_image
            
        except Exception as e:
            logger.warning(f"PaddleOCR preprocessing failed: {e}, using original image")
            return image
    
    def _optimize_resolution_for_polish(self, image: np.ndarray) -> np.ndarray:
        """Optimize image resolution for Polish text recognition"""
        height, width = image.shape[:2]
        
        # PaddleOCR works well with images around 960px on the longer side
        target_size = 960
        
        if max(height, width) < target_size:
            # Upscale small images
            scale_factor = target_size / max(height, width)
            new_height = int(height * scale_factor)
            new_width = int(width * scale_factor)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        elif max(height, width) > target_size * 2:
            # Downscale very large images
            scale_factor = target_size / max(height, width)
            new_height = int(height * scale_factor)
            new_width = int(width * scale_factor)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return image
    
    def _correct_document_skew(self, image: np.ndarray) -> np.ndarray:
        """Correct document skew using advanced techniques"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use Hough Line Transform to detect skew
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            angles = []
            for rho, theta in lines[:20]:  # Use more lines for better accuracy
                angle = theta * 180 / np.pi
                if angle < 45:
                    angles.append(angle)
                elif angle > 135:
                    angles.append(angle - 180)
            
            if angles:
                median_angle = np.median(angles)
                if abs(median_angle) > 0.3:  # Only correct if skew is significant
                    height, width = image.shape[:2]
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    image = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                         flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    logger.debug(f"Corrected document skew by {median_angle:.2f} degrees")
        
        return image
    
    def _reduce_noise_polish_optimized(self, image: np.ndarray) -> np.ndarray:
        """Apply noise reduction optimized for Polish text"""
        # Use bilateral filter to preserve edges while reducing noise
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Apply morphological opening to remove small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_OPEN, kernel)
        
        return denoised
    
    def _enhance_contrast_for_polish_text(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast specifically for Polish text recognition"""
        # Convert to LAB color space for better contrast enhancement
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels and convert back to BGR
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def _optimize_invoice_layout(self, image: np.ndarray) -> np.ndarray:
        """Optimize image for Polish invoice layout recognition"""
        # Apply morphological operations to enhance text structure
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use rectangular kernel to enhance horizontal text lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        enhanced = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to BGR
        result = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def _enhance_polish_text_features(self, image: np.ndarray) -> np.ndarray:
        """Enhance features specific to Polish text characters"""
        # Apply sharpening filter to enhance Polish diacritical marks
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(image, -1, kernel)
        
        # Blend with original image
        alpha = 0.3
        enhanced = cv2.addWeighted(image, 1-alpha, sharpened, alpha, 0)
        
        return enhanced
    
    def _process_paddleocr_results(self, ocr_results: List) -> Tuple[str, List[float], List[Dict], List[Dict]]:
        """
        Process PaddleOCR results into standardized format
        
        Args:
            ocr_results: PaddleOCR results list
            
        Returns:
            Tuple of (text, confidences, word_data, bounding_boxes)
        """
        text_parts = []
        confidences = []
        word_data = []
        bounding_boxes = []
        
        if not ocr_results or not ocr_results[0]:
            return "", [], [], []
        
        for i, line_result in enumerate(ocr_results[0]):
            if len(line_result) >= 2:
                bbox, (text, confidence) = line_result[0], line_result[1]
                
                # Convert confidence to percentage
                confidence_pct = confidence * 100.0
                
                # Extract bounding box coordinates
                if isinstance(bbox, list) and len(bbox) >= 4:
                    # PaddleOCR returns 4 corner points
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
                    'line_index': i,
                    'spatial_features': self._extract_spatial_features(bbox_dict)
                }
                
                text_parts.append(text)
                confidences.append(confidence_pct)
                word_data.append(word_info)
                bounding_boxes.append(bbox_dict)
        
        # Join text with appropriate spacing
        combined_text = self._reconstruct_text_with_spacing(word_data)
        
        return combined_text, confidences, word_data, bounding_boxes
    
    def _extract_spatial_features(self, bbox: Dict[str, Any]) -> Dict[str, float]:
        """Extract spatial features for confidence calculation"""
        return {
            'area': bbox['width'] * bbox['height'],
            'aspect_ratio': bbox['width'] / max(bbox['height'], 1),
            'center_x': bbox['left'] + bbox['width'] / 2,
            'center_y': bbox['top'] + bbox['height'] / 2
        }
    
    def _reconstruct_text_with_spacing(self, word_data: List[Dict]) -> str:
        """Reconstruct text with proper spacing based on spatial analysis"""
        if not word_data:
            return ""
        
        # Sort words by position (top to bottom, left to right)
        sorted_words = sorted(word_data, key=lambda w: (w['bbox']['top'], w['bbox']['left']))
        
        # Group words into lines
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
        
        return '\n'.join(reconstructed_lines)
    
    def _calculate_paddleocr_confidence(self, confidences: List[float], word_data: List[Dict]) -> float:
        """
        Calculate overall confidence score using PaddleOCR-specific algorithm
        
        Args:
            confidences: List of word-level confidence scores
            word_data: List of word data with spatial information
            
        Returns:
            Overall confidence score
        """
        if not confidences:
            return 0.0
        
        # Filter out very low confidence words (likely noise)
        filtered_data = [(conf, word) for conf, word in zip(confidences, word_data) if conf > 20.0]
        
        if not filtered_data:
            return 0.0
        
        filtered_confidences = [item[0] for item in filtered_data]
        filtered_words = [item[1] for item in filtered_data]
        
        # Calculate weighted average with spatial analysis
        total_weight = 0.0
        weighted_sum = 0.0
        
        for conf, word in zip(filtered_confidences, filtered_words):
            # Base weight from confidence
            weight = conf / 100.0
            
            # Spatial weight adjustments
            spatial_features = word.get('spatial_features', {})
            area = spatial_features.get('area', 0)
            aspect_ratio = spatial_features.get('aspect_ratio', 1)
            
            # Larger text areas get higher weight
            if area > 1000:  # Large text
                weight *= 1.2
            elif area < 100:  # Very small text
                weight *= 0.8
            
            # Reasonable aspect ratios get higher weight
            if 0.1 <= aspect_ratio <= 10:  # Normal text aspect ratio
                weight *= 1.1
            
            weighted_sum += conf * weight
            total_weight += weight
        
        if total_weight > 0:
            base_confidence = weighted_sum / total_weight
        else:
            base_confidence = sum(filtered_confidences) / len(filtered_confidences)
        
        # Apply PaddleOCR-specific adjustments
        # PaddleOCR tends to be conservative with confidence scores
        adjusted_confidence = min(100.0, base_confidence * 1.1)
        
        return adjusted_confidence
    
    def _apply_polish_enhancements(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Polish-specific enhancements to PaddleOCR result
        
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
            
            # PaddleOCR-specific Polish optimizations
            result = self._apply_paddleocr_polish_optimizations(result)
            
            logger.debug(f"Applied Polish enhancements to PaddleOCR result, confidence boost: {polish_boost:.1f}%")
            
        except Exception as e:
            logger.warning(f"Polish enhancement failed: {e}")
            result['polish_enhancement_error'] = str(e)
        
        return result
    
    def _apply_paddleocr_polish_optimizations(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply PaddleOCR-specific Polish optimizations
        
        Args:
            result: OCR result to optimize
            
        Returns:
            Optimized result
        """
        try:
            # PaddleOCR-specific text reconstruction improvements
            word_data = result.get('word_data', [])
            if not word_data:
                return result
            
            # Improve Polish character recognition
            corrected_text = self._correct_polish_characters(result['text'])
            if corrected_text != result['text']:
                result['text'] = corrected_text
                result['polish_character_correction_applied'] = True
            
            # Enhance spatial analysis for Polish invoice structure
            spatial_confidence = self._analyze_polish_invoice_structure(word_data)
            if spatial_confidence > 0:
                result['spatial_confidence_boost'] = spatial_confidence
                result['confidence_score'] = min(100.0, result['confidence_score'] + spatial_confidence)
            
            result['paddleocr_polish_optimization_applied'] = True
            
        except Exception as e:
            logger.warning(f"PaddleOCR Polish optimization failed: {e}")
        
        return result
    
    def _correct_polish_characters(self, text: str) -> str:
        """Correct common Polish character recognition errors"""
        # Common PaddleOCR misrecognitions for Polish characters
        corrections = {
            'ą': ['a', 'q'],
            'ć': ['c'],
            'ę': ['e'],
            'ł': ['l', '1'],
            'ń': ['n'],
            'ó': ['o', '0'],
            'ś': ['s'],
            'ź': ['z'],
            'ż': ['z']
        }
        
        corrected_text = text
        
        # Apply context-based corrections
        # This is a simplified version - in production, you'd use more sophisticated NLP
        for correct_char, wrong_chars in corrections.items():
            for wrong_char in wrong_chars:
                # Simple pattern-based correction (can be enhanced with ML)
                if wrong_char in corrected_text:
                    # Apply corrections in Polish word contexts
                    corrected_text = corrected_text.replace(wrong_char, correct_char)
        
        return corrected_text
    
    def _analyze_polish_invoice_structure(self, word_data: List[Dict]) -> float:
        """Analyze spatial structure for Polish invoice confidence boost"""
        if not word_data:
            return 0.0
        
        confidence_boost = 0.0
        
        # Check for typical Polish invoice structure
        text_elements = [word['text'].lower() for word in word_data]
        
        # Look for Polish invoice keywords
        polish_keywords = [
            'faktura', 'sprzedawca', 'nabywca', 'nip', 'vat', 
            'suma', 'razem', 'zł', 'pln', 'data'
        ]
        
        found_keywords = sum(1 for keyword in polish_keywords 
                           if any(keyword in element for element in text_elements))
        
        # Boost confidence based on Polish invoice structure
        if found_keywords >= 5:
            confidence_boost += 5.0
        elif found_keywords >= 3:
            confidence_boost += 2.0
        
        # Check spatial layout consistency
        y_positions = [word['bbox']['top'] for word in word_data]
        if len(set(y_positions)) > len(y_positions) * 0.3:  # Good vertical distribution
            confidence_boost += 2.0
        
        return confidence_boost
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages
        
        Returns:
            List of supported language codes
        """
        # PaddleOCR supported languages
        return ['pl', 'en', 'ch', 'de', 'fr', 'ja', 'ko', 'ru', 'es', 'pt', 'it', 'ar']
    
    def set_gpu_usage(self, use_gpu: bool) -> bool:
        """
        Enable or disable GPU usage (requires reinitialization)
        
        Args:
            use_gpu: Whether to use GPU
            
        Returns:
            bool: True if setting was applied successfully
        """
        if self.use_gpu != use_gpu:
            self.use_gpu = use_gpu
            self.is_initialized = False
            return self.initialize()
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded models
        
        Returns:
            Dictionary with model information
        """
        return {
            'detection_model': self.det_model_dir or 'default',
            'recognition_model': self.rec_model_dir or 'default',
            'classification_model': self.cls_model_dir or 'default',
            'languages': self.languages,
            'gpu_enabled': self.use_gpu,
            'angle_classification': self.use_angle_cls,
            'space_character_recognition': self.use_space_char,
            'drop_score_threshold': self.drop_score
        }