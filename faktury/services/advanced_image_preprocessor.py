#!/usr/bin/env python3
"""
Advanced Image Preprocessor for PaddleOCR
Polish-specific image preprocessing for optimal OCR results
"""

import logging
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from typing import Tuple, Optional, List, Dict, Any
import io

logger = logging.getLogger(__name__)

class AdvancedImagePreprocessor:
    """
    Advanced image preprocessing for Polish documents
    Optimizes images for PaddleOCR with Polish-specific enhancements
    """
    
    def __init__(self):
        """Initialize preprocessor with Polish-specific parameters"""
        
        # Preprocessing parameters
        self.noise_reduction_strength = 0.3
        self.contrast_enhancement_factor = 1.2
        self.brightness_enhancement_factor = 1.1
        self.sharpen_strength = 1.5
        
        # Polish document specific parameters
        self.polish_text_enhancement = True
        self.skew_correction_enabled = True
        self.resolution_optimization = True
        self.background_removal = True
        
        # Quality thresholds
        self.min_resolution = (800, 600)
        self.max_resolution = (4000, 3000)
        self.optimal_dpi = 300
    
    def preprocess_for_paddleocr(self, image: Image.Image) -> Image.Image:
        """
        Comprehensive preprocessing pipeline for PaddleOCR
        
        Args:
            image: Input PIL Image
            
        Returns:
            Preprocessed PIL Image optimized for PaddleOCR
        """
        try:
            logger.info("Starting advanced image preprocessing")
            
            # Step 1: Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Step 2: Resolution optimization
            if self.resolution_optimization:
                image = self.optimize_resolution(image)
            
            # Step 3: Background removal and enhancement
            if self.background_removal:
                image = self.remove_background_noise(image)
            
            # Step 4: Polish-specific text enhancement
            if self.polish_text_enhancement:
                image = self.enhance_polish_text(image)
            
            # Step 5: Skew correction
            if self.skew_correction_enabled:
                image = self.correct_document_orientation(image)
            
            # Step 6: Noise reduction
            image = self.reduce_noise(image)
            
            # Step 7: Contrast and brightness enhancement
            image = self.enhance_contrast_and_brightness(image)
            
            # Step 8: Sharpening
            image = self.sharpen_image(image)
            
            # Step 9: Final optimization for invoice layout
            image = self.optimize_for_invoice_layout(image)
            
            logger.info("Advanced image preprocessing completed")
            return image
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {e}")
            return image
    
    def optimize_resolution(self, image: Image.Image) -> Image.Image:
        """
        Optimize image resolution for OCR processing
        
        Args:
            image: Input PIL Image
            
        Returns:
            Resolution-optimized PIL Image
        """
        try:
            width, height = image.size
            
            # Check if resolution is too low
            if width < self.min_resolution[0] or height < self.min_resolution[1]:
                # Upscale using high-quality interpolation
                scale_factor = max(
                    self.min_resolution[0] / width,
                    self.min_resolution[1] / height
                )
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.LANCZOS)
                logger.debug(f"Upscaled image from {width}x{height} to {new_width}x{new_height}")
            
            # Check if resolution is too high
            elif width > self.max_resolution[0] or height > self.max_resolution[1]:
                # Downscale while maintaining aspect ratio
                scale_factor = min(
                    self.max_resolution[0] / width,
                    self.max_resolution[1] / height
                )
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.LANCZOS)
                logger.debug(f"Downscaled image from {width}x{height} to {new_width}x{new_height}")
            
            return image
            
        except Exception as e:
            logger.error(f"Error optimizing resolution: {e}")
            return image
    
    def remove_background_noise(self, image: Image.Image) -> Image.Image:
        """
        Remove background noise and enhance document clarity
        
        Args:
            image: Input PIL Image
            
        Returns:
            Background-cleaned PIL Image
        """
        try:
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Convert to grayscale for processing
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply adaptive thresholding to separate text from background
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up noise
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            # Convert back to PIL Image
            cleaned_image = Image.fromarray(cleaned)
            
            # Convert back to RGB
            cleaned_image = cleaned_image.convert('RGB')
            
            return cleaned_image
            
        except Exception as e:
            logger.error(f"Error removing background noise: {e}")
            return image
    
    def enhance_polish_text(self, image: Image.Image) -> Image.Image:
        """
        Polish-specific text enhancement for better OCR accuracy
        
        Args:
            image: Input PIL Image
            
        Returns:
            Polish-text-enhanced PIL Image
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Apply bilateral filter to preserve edges while smoothing
            filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # Convert back to PIL Image
            enhanced_image = Image.fromarray(filtered)
            
            # Convert back to RGB
            enhanced_image = enhanced_image.convert('RGB')
            
            return enhanced_image
            
        except Exception as e:
            logger.error(f"Error enhancing Polish text: {e}")
            return image
    
    def correct_document_orientation(self, image: Image.Image) -> Image.Image:
        """
        Correct document skew and orientation
        
        Args:
            image: Input PIL Image
            
        Returns:
            Orientation-corrected PIL Image
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Find lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Calculate angles
                angles = []
                for rho, theta in lines[:10]:  # Use first 10 lines
                    angle = theta * 180 / np.pi
                    if angle < 45:
                        angles.append(angle)
                    elif angle > 135:
                        angles.append(angle - 180)
                
                if angles:
                    # Calculate median angle for skew correction
                    median_angle = np.median(angles)
                    
                    # Apply rotation if angle is significant
                    if abs(median_angle) > 0.5:
                        # Get image center
                        height, width = gray.shape
                        center = (width // 2, height // 2)
                        
                        # Create rotation matrix
                        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                        
                        # Apply rotation
                        rotated = cv2.warpAffine(img_array, rotation_matrix, (width, height))
                        
                        # Convert back to PIL Image
                        corrected_image = Image.fromarray(rotated)
                        logger.debug(f"Corrected document skew by {median_angle:.2f} degrees")
                        return corrected_image
            
            return image
            
        except Exception as e:
            logger.error(f"Error correcting document orientation: {e}")
            return image
    
    def reduce_noise(self, image: Image.Image) -> Image.Image:
        """
        Reduce image noise while preserving text quality
        
        Args:
            image: Input PIL Image
            
        Returns:
            Noise-reduced PIL Image
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Apply non-local means denoising
            denoised = cv2.fastNlMeansDenoisingColored(
                img_array, None, 
                h=self.noise_reduction_strength * 10,
                hColor=self.noise_reduction_strength * 10,
                templateWindowSize=7,
                searchWindowSize=21
            )
            
            # Convert back to PIL Image
            denoised_image = Image.fromarray(denoised)
            
            return denoised_image
            
        except Exception as e:
            logger.error(f"Error reducing noise: {e}")
            return image
    
    def enhance_contrast_and_brightness(self, image: Image.Image) -> Image.Image:
        """
        Enhance contrast and brightness for better text visibility
        
        Args:
            image: Input PIL Image
            
        Returns:
            Enhanced PIL Image
        """
        try:
            # Enhance contrast
            contrast_enhancer = ImageEnhance.Contrast(image)
            image = contrast_enhancer.enhance(self.contrast_enhancement_factor)
            
            # Enhance brightness
            brightness_enhancer = ImageEnhance.Brightness(image)
            image = brightness_enhancer.enhance(self.brightness_enhancement_factor)
            
            return image
            
        except Exception as e:
            logger.error(f"Error enhancing contrast and brightness: {e}")
            return image
    
    def sharpen_image(self, image: Image.Image) -> Image.Image:
        """
        Sharpen image to improve text clarity
        
        Args:
            image: Input PIL Image
            
        Returns:
            Sharpened PIL Image
        """
        try:
            # Apply unsharp mask filter
            sharpened = image.filter(ImageFilter.UnsharpMask(
                radius=2, 
                percent=150, 
                threshold=3
            ))
            
            return sharpened
            
        except Exception as e:
            logger.error(f"Error sharpening image: {e}")
            return image
    
    def optimize_for_invoice_layout(self, image: Image.Image) -> Image.Image:
        """
        Optimize image specifically for invoice layout recognition
        
        Args:
            image: Input PIL Image
            
        Returns:
            Invoice-optimized PIL Image
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply morphological operations to enhance text regions
            kernel = np.ones((2, 2), np.uint8)
            enhanced = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Apply slight Gaussian blur to smooth edges
            smoothed = cv2.GaussianBlur(enhanced, (1, 1), 0)
            
            # Convert back to PIL Image
            optimized_image = Image.fromarray(smoothed)
            
            # Convert back to RGB
            optimized_image = optimized_image.convert('RGB')
            
            return optimized_image
            
        except Exception as e:
            logger.error(f"Error optimizing for invoice layout: {e}")
            return image
    
    def preprocess_pdf_page(self, pdf_content: bytes, page_number: int = 0) -> Image.Image:
        """
        Preprocess a specific page from PDF content
        
        Args:
            pdf_content: PDF file content as bytes
            page_number: Page number to process (0-indexed)
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            from pdf2image import convert_from_bytes
            
            # Convert PDF page to image
            images = convert_from_bytes(
                pdf_content, 
                first_page=page_number + 1, 
                last_page=page_number + 1,
                dpi=self.optimal_dpi
            )
            
            if images:
                # Preprocess the extracted image
                return self.preprocess_for_paddleocr(images[0])
            else:
                logger.warning(f"No image extracted from PDF page {page_number}")
                return Image.new('RGB', (800, 600), 'white')
                
        except ImportError:
            logger.warning("pdf2image not available. Install with: pip install pdf2image")
            return Image.new('RGB', (800, 600), 'white')
        except Exception as e:
            logger.error(f"Error preprocessing PDF page: {e}")
            return Image.new('RGB', (800, 600), 'white')
    
    def batch_preprocess(self, images: List[Image.Image]) -> List[Image.Image]:
        """
        Preprocess multiple images in batch
        
        Args:
            images: List of input PIL Images
            
        Returns:
            List of preprocessed PIL Images
        """
        try:
            preprocessed_images = []
            
            for i, image in enumerate(images):
                logger.debug(f"Preprocessing image {i+1}/{len(images)}")
                preprocessed = self.preprocess_for_paddleocr(image)
                preprocessed_images.append(preprocessed)
            
            logger.info(f"Batch preprocessing completed for {len(images)} images")
            return preprocessed_images
            
        except Exception as e:
            logger.error(f"Error in batch preprocessing: {e}")
            return images
    
    def get_preprocessing_metadata(self) -> Dict[str, Any]:
        """
        Get preprocessing configuration metadata
        
        Returns:
            Dictionary with preprocessing parameters
        """
        return {
            'noise_reduction_strength': self.noise_reduction_strength,
            'contrast_enhancement_factor': self.contrast_enhancement_factor,
            'brightness_enhancement_factor': self.brightness_enhancement_factor,
            'sharpen_strength': self.sharpen_strength,
            'polish_text_enhancement': self.polish_text_enhancement,
            'skew_correction_enabled': self.skew_correction_enabled,
            'resolution_optimization': self.resolution_optimization,
            'background_removal': self.background_removal,
            'min_resolution': self.min_resolution,
            'max_resolution': self.max_resolution,
            'optimal_dpi': self.optimal_dpi
        }
    
    def update_preprocessing_parameters(self, **kwargs) -> None:
        """
        Update preprocessing parameters
        
        Args:
            **kwargs: Parameter updates
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.info(f"Updated preprocessing parameter: {key} = {value}")
            else:
                logger.warning(f"Unknown preprocessing parameter: {key}")
    
    def create_preprocessing_pipeline(self, steps: List[str]) -> callable:
        """
        Create a custom preprocessing pipeline
        
        Args:
            steps: List of preprocessing step names
            
        Returns:
            Custom preprocessing function
        """
        def custom_pipeline(image: Image.Image) -> Image.Image:
            """Custom preprocessing pipeline"""
            try:
                for step in steps:
                    if step == 'optimize_resolution':
                        image = self.optimize_resolution(image)
                    elif step == 'remove_background_noise':
                        image = self.remove_background_noise(image)
                    elif step == 'enhance_polish_text':
                        image = self.enhance_polish_text(image)
                    elif step == 'correct_document_orientation':
                        image = self.correct_document_orientation(image)
                    elif step == 'reduce_noise':
                        image = self.reduce_noise(image)
                    elif step == 'enhance_contrast_and_brightness':
                        image = self.enhance_contrast_and_brightness(image)
                    elif step == 'sharpen_image':
                        image = self.sharpen_image(image)
                    elif step == 'optimize_for_invoice_layout':
                        image = self.optimize_for_invoice_layout(image)
                    else:
                        logger.warning(f"Unknown preprocessing step: {step}")
                
                return image
                
            except Exception as e:
                logger.error(f"Error in custom preprocessing pipeline: {e}")
                return image
        
        return custom_pipeline