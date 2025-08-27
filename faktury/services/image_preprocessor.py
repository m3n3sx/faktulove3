"""
Image preprocessing service for OCR optimization.

This service handles document preprocessing to improve OCR accuracy,
including PDF conversion, image enhancement, and format optimization.
"""

import io
import logging
import numpy as np
from typing import Tuple, Optional, List
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import cv2
from pdf2image import convert_from_bytes
from skimage import filters, morphology, transform
from skimage.feature import canny
from skimage.transform import hough_line, hough_line_peaks
import math

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Preprocess images for optimal OCR results"""
    
    def __init__(self):
        """Initialize the image preprocessor with default settings"""
        self.default_dpi = 300
        self.min_dpi = 150
        self.max_dpi = 600
        self.supported_formats = {
            'application/pdf': self._process_pdf,
            'image/jpeg': self._process_image,
            'image/jpg': self._process_image,
            'image/png': self._process_image,
            'image/tiff': self._process_image,
            'image/tif': self._process_image,
            'image/bmp': self._process_image,
            'image/webp': self._process_image
        }
    
    def preprocess_document(self, file_content: bytes, mime_type: str) -> List[bytes]:
        """
        Apply preprocessing filters to improve OCR accuracy.
        
        Args:
            file_content: Raw file content as bytes
            mime_type: MIME type of the file
            
        Returns:
            List of preprocessed image bytes (multiple pages for PDFs)
            
        Raises:
            ValueError: If file format is not supported
            Exception: If preprocessing fails
        """
        try:
            logger.info(f"Starting preprocessing for {mime_type}")
            
            if mime_type not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {mime_type}")
            
            # Process based on file type
            processor = self.supported_formats[mime_type]
            images = processor(file_content)
            
            # Apply preprocessing pipeline to each image
            processed_images = []
            for i, image in enumerate(images):
                logger.debug(f"Processing image {i+1}/{len(images)}")
                processed_image = self._apply_preprocessing_pipeline(image)
                processed_images.append(processed_image)
            
            logger.info(f"Successfully preprocessed {len(processed_images)} images")
            return processed_images
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise
    
    def _process_pdf(self, file_content: bytes) -> List[Image.Image]:
        """Convert PDF to images"""
        try:
            logger.debug("Converting PDF to images")
            images = convert_from_bytes(
                file_content,
                dpi=self.default_dpi,
                fmt='RGB',
                thread_count=2
            )
            logger.debug(f"Converted PDF to {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"PDF conversion failed: {str(e)}")
            raise
    
    def _process_image(self, file_content: bytes) -> List[Image.Image]:
        """Load and validate image"""
        try:
            image = Image.open(io.BytesIO(file_content))
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return [image]
        except Exception as e:
            logger.error(f"Image loading failed: {str(e)}")
            raise
    
    def _apply_preprocessing_pipeline(self, image: Image.Image) -> bytes:
        """
        Apply complete preprocessing pipeline to an image.
        
        Pipeline steps:
        1. Resolution optimization
        2. Deskewing and rotation correction
        3. Noise reduction
        4. Contrast enhancement
        5. Final optimization
        """
        try:
            # Step 1: Resolution optimization
            image = self._optimize_resolution(image)
            
            # Step 2: Deskewing and rotation correction
            image = self._correct_skew_and_rotation(image)
            
            # Step 3: Noise reduction
            image = self._reduce_noise(image)
            
            # Step 4: Contrast enhancement
            image = self._enhance_contrast(image)
            
            # Step 5: Final optimization for OCR
            image = self._final_ocr_optimization(image)
            
            # Convert to bytes
            output = io.BytesIO()
            image.save(output, format='PNG', optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Preprocessing pipeline failed: {str(e)}")
            raise
    
    def _optimize_resolution(self, image: Image.Image) -> Image.Image:
        """Optimize image resolution for OCR"""
        try:
            width, height = image.size
            
            # Calculate current DPI (estimate based on size)
            estimated_dpi = max(width, height) / 8.5  # Assume letter size
            
            if estimated_dpi < self.min_dpi:
                # Upscale if too low resolution
                scale_factor = self.default_dpi / estimated_dpi
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.debug(f"Upscaled image from {width}x{height} to {new_width}x{new_height}")
                
            elif estimated_dpi > self.max_dpi:
                # Downscale if too high resolution
                scale_factor = self.default_dpi / estimated_dpi
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.debug(f"Downscaled image from {width}x{height} to {new_width}x{new_height}")
            
            return image
            
        except Exception as e:
            logger.warning(f"Resolution optimization failed: {str(e)}")
            return image
    
    def _correct_skew_and_rotation(self, image: Image.Image) -> Image.Image:
        """Detect and correct image skew and rotation"""
        try:
            # Convert PIL image to numpy array for processing
            img_array = np.array(image)
            
            # Convert to grayscale for skew detection
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Detect skew angle
            skew_angle = self._detect_skew_angle(gray)
            
            if abs(skew_angle) > 0.5:  # Only correct if skew is significant
                # Rotate image to correct skew
                rotated = transform.rotate(img_array, skew_angle, resize=True, preserve_range=True)
                rotated = rotated.astype(np.uint8)
                
                # Convert back to PIL Image
                corrected_image = Image.fromarray(rotated)
                logger.debug(f"Corrected skew by {skew_angle:.2f} degrees")
                return corrected_image
            
            return image
            
        except Exception as e:
            logger.warning(f"Skew correction failed: {str(e)}")
            return image
    
    def _detect_skew_angle(self, gray_image: np.ndarray) -> float:
        """Detect skew angle using Hough line transform"""
        try:
            # Apply edge detection
            edges = canny(gray_image, sigma=2, low_threshold=0.1, high_threshold=0.2)
            
            # Apply Hough line transform
            tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
            h, theta, d = hough_line(edges, theta=tested_angles)
            
            # Find peaks in Hough space
            hough_peaks = hough_line_peaks(h, theta, d, num_peaks=20)
            
            if len(hough_peaks[1]) == 0:
                return 0.0
            
            # Calculate most common angle
            angles = hough_peaks[1]
            angle_degrees = np.degrees(angles)
            
            # Filter angles to reasonable range for text
            valid_angles = angle_degrees[np.abs(angle_degrees) < 45]
            
            if len(valid_angles) == 0:
                return 0.0
            
            # Return median angle
            return np.median(valid_angles)
            
        except Exception as e:
            logger.warning(f"Skew detection failed: {str(e)}")
            return 0.0
    
    def _reduce_noise(self, image: Image.Image) -> Image.Image:
        """Apply noise reduction filters"""
        try:
            # Convert to numpy array for advanced filtering
            img_array = np.array(image)
            
            # Apply bilateral filter to reduce noise while preserving edges
            if len(img_array.shape) == 3:
                filtered = cv2.bilateralFilter(img_array, 9, 75, 75)
            else:
                filtered = cv2.bilateralFilter(img_array, 9, 75, 75)
            
            # Convert back to PIL and apply additional filters
            filtered_image = Image.fromarray(filtered)
            
            # Apply median filter for salt-and-pepper noise
            filtered_image = filtered_image.filter(ImageFilter.MedianFilter(size=3))
            
            logger.debug("Applied noise reduction filters")
            return filtered_image
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {str(e)}")
            return image
    
    def _enhance_contrast(self, image: Image.Image) -> Image.Image:
        """Enhance image contrast for better OCR"""
        try:
            # Auto-adjust levels
            image = ImageOps.autocontrast(image, cutoff=2)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # Increase contrast by 20%
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)  # Increase sharpness by 10%
            
            logger.debug("Applied contrast enhancement")
            return image
            
        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {str(e)}")
            return image
    
    def _final_ocr_optimization(self, image: Image.Image) -> Image.Image:
        """Apply final optimizations specifically for OCR"""
        try:
            # Convert to grayscale for OCR (most OCR engines work better with grayscale)
            if image.mode != 'L':
                image = image.convert('L')
            
            # Apply slight Gaussian blur to smooth text edges
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Apply unsharp mask to enhance text edges
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            logger.debug("Applied final OCR optimizations")
            return image
            
        except Exception as e:
            logger.warning(f"Final OCR optimization failed: {str(e)}")
            return image
    
    def get_preprocessing_info(self, file_content: bytes, mime_type: str) -> dict:
        """Get information about preprocessing that would be applied"""
        try:
            if mime_type == 'application/pdf':
                # Get PDF page count
                images = convert_from_bytes(file_content, dpi=72)  # Low DPI for info only
                page_count = len(images)
                sample_image = images[0]
            else:
                page_count = 1
                sample_image = Image.open(io.BytesIO(file_content))
            
            width, height = sample_image.size
            estimated_dpi = max(width, height) / 8.5
            
            return {
                'page_count': page_count,
                'original_size': (width, height),
                'estimated_dpi': round(estimated_dpi),
                'will_resize': estimated_dpi < self.min_dpi or estimated_dpi > self.max_dpi,
                'target_dpi': self.default_dpi,
                'supported_format': mime_type in self.supported_formats
            }
            
        except Exception as e:
            logger.error(f"Failed to get preprocessing info: {str(e)}")
            return {
                'error': str(e),
                'supported_format': mime_type in self.supported_formats
            }