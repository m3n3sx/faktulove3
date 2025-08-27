"""
Optimized Image Preprocessor with Caching and Performance Enhancements

This module provides an optimized version of the image preprocessor with:
- Intelligent caching for frequently processed document types
- Parallel processing for multi-page documents
- Adaptive preprocessing based on document characteristics
- Performance monitoring and optimization
"""

import io
import logging
import hashlib
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import cv2
from pdf2image import convert_from_bytes
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from functools import lru_cache
import pickle
import os
import time
from dataclasses import dataclass

from .ocr_performance_profiler import ocr_profiler

logger = logging.getLogger(__name__)


@dataclass
class PreprocessingProfile:
    """Preprocessing profile for different document types"""
    name: str
    target_dpi: int
    noise_reduction_strength: int
    contrast_enhancement: float
    sharpness_enhancement: float
    skew_correction: bool
    morphological_operations: bool
    bilateral_filter_params: Tuple[int, int, int]  # d, sigmaColor, sigmaSpace


class DocumentTypeClassifier:
    """Classify documents to apply appropriate preprocessing profiles"""
    
    def __init__(self):
        self.profiles = {
            'high_quality_invoice': PreprocessingProfile(
                name='high_quality_invoice',
                target_dpi=300,
                noise_reduction_strength=1,
                contrast_enhancement=1.1,
                sharpness_enhancement=1.05,
                skew_correction=True,
                morphological_operations=False,
                bilateral_filter_params=(5, 50, 50)
            ),
            'low_quality_invoice': PreprocessingProfile(
                name='low_quality_invoice',
                target_dpi=400,
                noise_reduction_strength=3,
                contrast_enhancement=1.3,
                sharpness_enhancement=1.2,
                skew_correction=True,
                morphological_operations=True,
                bilateral_filter_params=(9, 75, 75)
            ),
            'scanned_document': PreprocessingProfile(
                name='scanned_document',
                target_dpi=350,
                noise_reduction_strength=2,
                contrast_enhancement=1.2,
                sharpness_enhancement=1.1,
                skew_correction=True,
                morphological_operations=True,
                bilateral_filter_params=(7, 60, 60)
            ),
            'photo_document': PreprocessingProfile(
                name='photo_document',
                target_dpi=400,
                noise_reduction_strength=3,
                contrast_enhancement=1.4,
                sharpness_enhancement=1.3,
                skew_correction=True,
                morphological_operations=True,
                bilateral_filter_params=(11, 80, 80)
            ),
            'digital_document': PreprocessingProfile(
                name='digital_document',
                target_dpi=300,
                noise_reduction_strength=0,
                contrast_enhancement=1.0,
                sharpness_enhancement=1.0,
                skew_correction=False,
                morphological_operations=False,
                bilateral_filter_params=(3, 30, 30)
            )
        }
    
    def classify_document(self, image: Image.Image) -> PreprocessingProfile:
        """Classify document type based on image characteristics"""
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Calculate image quality metrics
            metrics = self._calculate_image_metrics(img_array)
            
            # Classify based on metrics
            if metrics['noise_level'] < 0.1 and metrics['contrast'] > 0.8:
                return self.profiles['digital_document']
            elif metrics['noise_level'] > 0.4 or metrics['blur_level'] > 0.3:
                return self.profiles['photo_document']
            elif metrics['contrast'] < 0.4:
                return self.profiles['low_quality_invoice']
            elif metrics['sharpness'] > 0.7:
                return self.profiles['high_quality_invoice']
            else:
                return self.profiles['scanned_document']
                
        except Exception as e:
            logger.warning(f"Document classification failed: {e}, using default profile")
            return self.profiles['scanned_document']
    
    def _calculate_image_metrics(self, img_array: np.ndarray) -> Dict[str, float]:
        """Calculate image quality metrics for classification"""
        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Calculate metrics
            metrics = {}
            
            # Noise level (using Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            metrics['noise_level'] = min(1.0, laplacian_var / 1000.0)
            
            # Contrast (standard deviation of pixel intensities)
            metrics['contrast'] = gray.std() / 128.0
            
            # Sharpness (gradient magnitude)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            metrics['sharpness'] = min(1.0, gradient_magnitude.mean() / 50.0)
            
            # Blur level (inverse of sharpness)
            metrics['blur_level'] = 1.0 - metrics['sharpness']
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Failed to calculate image metrics: {e}")
            return {
                'noise_level': 0.2,
                'contrast': 0.5,
                'sharpness': 0.5,
                'blur_level': 0.5
            }


class PreprocessingCache:
    """Intelligent caching system for preprocessed images"""
    
    def __init__(self, cache_dir: str = None, max_cache_size_mb: int = 500):
        """
        Initialize preprocessing cache
        
        Args:
            cache_dir: Directory to store cache files
            max_cache_size_mb: Maximum cache size in MB
        """
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), '.ocr_cache')
        self.max_cache_size_mb = max_cache_size_mb
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'size_mb': 0
        }
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Thread lock for cache operations
        self._lock = threading.Lock()
        
        # Initialize cache size
        self._update_cache_size()
    
    def _generate_cache_key(self, file_content: bytes, profile: PreprocessingProfile) -> str:
        """Generate cache key based on file content and preprocessing profile"""
        # Create hash from file content and profile parameters
        content_hash = hashlib.md5(file_content).hexdigest()
        profile_hash = hashlib.md5(str(profile.__dict__).encode()).hexdigest()
        return f"{content_hash}_{profile_hash}"
    
    def get(self, file_content: bytes, profile: PreprocessingProfile) -> Optional[List[bytes]]:
        """Get preprocessed images from cache"""
        cache_key = self._generate_cache_key(file_content, profile)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        try:
            with self._lock:
                if os.path.exists(cache_file):
                    with open(cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    # Update access time
                    os.utime(cache_file)
                    
                    self.cache_stats['hits'] += 1
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_data['images']
                else:
                    self.cache_stats['misses'] += 1
                    return None
                    
        except Exception as e:
            logger.warning(f"Cache retrieval failed for key {cache_key}: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def put(self, file_content: bytes, profile: PreprocessingProfile, images: List[bytes]):
        """Store preprocessed images in cache"""
        cache_key = self._generate_cache_key(file_content, profile)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        try:
            with self._lock:
                # Check cache size before adding
                if self._should_evict_cache():
                    self._evict_old_entries()
                
                cached_data = {
                    'images': images,
                    'profile': profile,
                    'timestamp': time.time()
                }
                
                with open(cache_file, 'wb') as f:
                    pickle.dump(cached_data, f)
                
                self._update_cache_size()
                logger.debug(f"Cached preprocessed images for key: {cache_key}")
                
        except Exception as e:
            logger.warning(f"Cache storage failed for key {cache_key}: {e}")
    
    def _should_evict_cache(self) -> bool:
        """Check if cache should be evicted"""
        return self.cache_stats['size_mb'] > self.max_cache_size_mb
    
    def _evict_old_entries(self):
        """Evict oldest cache entries"""
        try:
            cache_files = []
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    filepath = os.path.join(self.cache_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    cache_files.append((filepath, mtime))
            
            # Sort by modification time (oldest first)
            cache_files.sort(key=lambda x: x[1])
            
            # Remove oldest 25% of files
            files_to_remove = len(cache_files) // 4
            for filepath, _ in cache_files[:files_to_remove]:
                os.remove(filepath)
                logger.debug(f"Evicted cache file: {filepath}")
            
            self._update_cache_size()
            
        except Exception as e:
            logger.error(f"Cache eviction failed: {e}")
    
    def _update_cache_size(self):
        """Update cache size statistics"""
        try:
            total_size = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    filepath = os.path.join(self.cache_dir, filename)
                    total_size += os.path.getsize(filepath)
            
            self.cache_stats['size_mb'] = total_size / 1024 / 1024
            
        except Exception as e:
            logger.warning(f"Failed to update cache size: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': hit_rate,
            'size_mb': self.cache_stats['size_mb'],
            'max_size_mb': self.max_cache_size_mb
        }
    
    def clear(self):
        """Clear all cache entries"""
        try:
            with self._lock:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.pkl'):
                        os.remove(os.path.join(self.cache_dir, filename))
                
                self.cache_stats = {'hits': 0, 'misses': 0, 'size_mb': 0}
                logger.info("Cache cleared")
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")


class OptimizedImagePreprocessor:
    """
    Optimized image preprocessor with caching and performance enhancements
    
    Features:
    - Intelligent document type classification
    - Adaptive preprocessing profiles
    - Intelligent caching system
    - Parallel processing for multi-page documents
    - Performance monitoring and optimization
    """
    
    def __init__(self, 
                 enable_caching: bool = True,
                 cache_dir: str = None,
                 max_cache_size_mb: int = 500,
                 max_workers: int = 4,
                 enable_profiling: bool = True):
        """
        Initialize optimized image preprocessor
        
        Args:
            enable_caching: Enable intelligent caching
            cache_dir: Directory for cache storage
            max_cache_size_mb: Maximum cache size in MB
            max_workers: Maximum number of worker threads
            enable_profiling: Enable performance profiling
        """
        self.enable_caching = enable_caching
        self.max_workers = max_workers
        self.enable_profiling = enable_profiling
        
        # Initialize components
        self.classifier = DocumentTypeClassifier()
        
        if enable_caching:
            self.cache = PreprocessingCache(cache_dir, max_cache_size_mb)
        else:
            self.cache = None
        
        # Supported formats
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
        
        # Performance statistics
        self.stats = {
            'total_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time': 0.0,
            'parallel_processing_used': 0
        }
        
        logger.info("Optimized Image Preprocessor initialized")
    
    @ocr_profiler.profile_function("optimized_preprocessing")
    def preprocess_document(self, file_content: bytes, mime_type: str) -> List[bytes]:
        """
        Apply optimized preprocessing with caching and performance monitoring
        
        Args:
            file_content: Raw file content as bytes
            mime_type: MIME type of the file
            
        Returns:
            List of preprocessed image bytes
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting optimized preprocessing for {mime_type}")
            
            if mime_type not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {mime_type}")
            
            # Convert to images first
            with ocr_profiler.profile_stage("image_conversion"):
                processor = self.supported_formats[mime_type]
                images = processor(file_content)
            
            if not images:
                raise ValueError("No images could be extracted from document")
            
            # Classify document type using first image
            with ocr_profiler.profile_stage("document_classification"):
                profile = self.classifier.classify_document(images[0])
                logger.debug(f"Document classified as: {profile.name}")
            
            # Check cache first
            cached_result = None
            if self.enable_caching and self.cache:
                with ocr_profiler.profile_stage("cache_lookup"):
                    cached_result = self.cache.get(file_content, profile)
                
                if cached_result:
                    self.stats['cache_hits'] += 1
                    processing_time = time.time() - start_time
                    logger.info(f"Cache hit! Preprocessing completed in {processing_time:.2f}s")
                    return cached_result
                else:
                    self.stats['cache_misses'] += 1
            
            # Process images with optimized pipeline
            if len(images) > 1 and self.max_workers > 1:
                # Parallel processing for multi-page documents
                with ocr_profiler.profile_stage("parallel_preprocessing"):
                    processed_images = self._process_images_parallel(images, profile)
                    self.stats['parallel_processing_used'] += 1
            else:
                # Sequential processing
                with ocr_profiler.profile_stage("sequential_preprocessing"):
                    processed_images = self._process_images_sequential(images, profile)
            
            # Cache the result
            if self.enable_caching and self.cache:
                with ocr_profiler.profile_stage("cache_storage"):
                    self.cache.put(file_content, profile, processed_images)
            
            # Update statistics
            processing_time = time.time() - start_time
            self.stats['total_processed'] += 1
            self.stats['average_processing_time'] = (
                (self.stats['average_processing_time'] * (self.stats['total_processed'] - 1) + processing_time) /
                self.stats['total_processed']
            )
            
            logger.info(f"Optimized preprocessing completed in {processing_time:.2f}s "
                       f"for {len(processed_images)} images")
            return processed_images
            
        except Exception as e:
            logger.error(f"Optimized preprocessing failed: {str(e)}")
            raise
    
    def _process_pdf(self, file_content: bytes) -> List[Image.Image]:
        """Convert PDF to images with optimization"""
        try:
            logger.debug("Converting PDF to images")
            images = convert_from_bytes(
                file_content,
                dpi=300,  # Standard DPI for good quality
                fmt='RGB',
                thread_count=min(2, self.max_workers),  # Limit threads for PDF conversion
                first_page=None,
                last_page=None,
                use_pdftocairo=True,  # Use Cairo backend for better performance
                poppler_path=None
            )
            logger.debug(f"Converted PDF to {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"PDF conversion failed: {str(e)}")
            raise
    
    def _process_image(self, file_content: bytes) -> List[Image.Image]:
        """Load and validate image with optimization"""
        try:
            image = Image.open(io.BytesIO(file_content))
            # Convert to RGB if needed (more efficient than later conversion)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return [image]
        except Exception as e:
            logger.error(f"Image loading failed: {str(e)}")
            raise
    
    def _process_images_parallel(self, images: List[Image.Image], profile: PreprocessingProfile) -> List[bytes]:
        """Process multiple images in parallel"""
        processed_images = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks
            future_to_index = {
                executor.submit(self._apply_preprocessing_pipeline, image, profile): i
                for i, image in enumerate(images)
            }
            
            # Collect results in order
            results = [None] * len(images)
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"Parallel preprocessing failed for image {index}: {e}")
                    # Use fallback processing
                    results[index] = self._apply_fallback_preprocessing(images[index])
            
            # Filter out None results
            processed_images = [img for img in results if img is not None]
        
        return processed_images
    
    def _process_images_sequential(self, images: List[Image.Image], profile: PreprocessingProfile) -> List[bytes]:
        """Process images sequentially"""
        processed_images = []
        
        for i, image in enumerate(images):
            try:
                processed_image = self._apply_preprocessing_pipeline(image, profile)
                processed_images.append(processed_image)
            except Exception as e:
                logger.error(f"Sequential preprocessing failed for image {i}: {e}")
                # Use fallback processing
                fallback_image = self._apply_fallback_preprocessing(image)
                if fallback_image:
                    processed_images.append(fallback_image)
        
        return processed_images
    
    def _apply_preprocessing_pipeline(self, image: Image.Image, profile: PreprocessingProfile) -> bytes:
        """Apply optimized preprocessing pipeline based on profile"""
        try:
            # Step 1: Resolution optimization
            image = self._optimize_resolution(image, profile.target_dpi)
            
            # Step 2: Noise reduction (if needed)
            if profile.noise_reduction_strength > 0:
                image = self._reduce_noise_optimized(image, profile)
            
            # Step 3: Skew correction (if enabled)
            if profile.skew_correction:
                image = self._correct_skew_optimized(image)
            
            # Step 4: Contrast enhancement
            if profile.contrast_enhancement != 1.0:
                image = self._enhance_contrast_optimized(image, profile.contrast_enhancement)
            
            # Step 5: Sharpness enhancement
            if profile.sharpness_enhancement != 1.0:
                image = self._enhance_sharpness_optimized(image, profile.sharpness_enhancement)
            
            # Step 6: Morphological operations (if enabled)
            if profile.morphological_operations:
                image = self._apply_morphological_operations_optimized(image)
            
            # Step 7: Final OCR optimization
            image = self._final_ocr_optimization(image)
            
            # Convert to bytes
            output = io.BytesIO()
            image.save(output, format='PNG', optimize=True, compress_level=6)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Preprocessing pipeline failed: {str(e)}")
            raise
    
    def _apply_fallback_preprocessing(self, image: Image.Image) -> Optional[bytes]:
        """Apply minimal fallback preprocessing"""
        try:
            # Just basic optimization
            if image.mode != 'L':
                image = image.convert('L')
            
            # Basic contrast enhancement
            image = ImageOps.autocontrast(image, cutoff=2)
            
            # Convert to bytes
            output = io.BytesIO()
            image.save(output, format='PNG', optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Fallback preprocessing failed: {e}")
            return None
    
    @lru_cache(maxsize=128)
    def _optimize_resolution(self, image: Image.Image, target_dpi: int) -> Image.Image:
        """Optimize image resolution with caching"""
        try:
            width, height = image.size
            
            # Estimate current DPI
            estimated_dpi = max(width, height) / 8.5  # Assume letter size
            
            if abs(estimated_dpi - target_dpi) > 50:  # Only resize if significant difference
                scale_factor = target_dpi / estimated_dpi
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                # Use appropriate resampling method based on scale factor
                if scale_factor > 1:
                    # Upscaling - use LANCZOS for quality
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    # Downscaling - use AREA for better performance
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                logger.debug(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            return image
            
        except Exception as e:
            logger.warning(f"Resolution optimization failed: {str(e)}")
            return image
    
    def _reduce_noise_optimized(self, image: Image.Image, profile: PreprocessingProfile) -> Image.Image:
        """Apply optimized noise reduction"""
        try:
            # Convert to numpy array for OpenCV operations
            img_array = np.array(image)
            
            # Apply bilateral filter with profile-specific parameters
            d, sigma_color, sigma_space = profile.bilateral_filter_params
            filtered = cv2.bilateralFilter(img_array, d, sigma_color, sigma_space)
            
            # Apply additional noise reduction based on strength
            if profile.noise_reduction_strength >= 2:
                # Apply median filter for salt-and-pepper noise
                filtered = cv2.medianBlur(filtered, 3)
            
            if profile.noise_reduction_strength >= 3:
                # Apply morphological opening for additional noise removal
                kernel = np.ones((2, 2), np.uint8)
                filtered = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
            
            # Convert back to PIL Image
            return Image.fromarray(filtered)
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {str(e)}")
            return image
    
    def _correct_skew_optimized(self, image: Image.Image) -> Image.Image:
        """Apply optimized skew correction"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale for skew detection
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Use Hough Line Transform for skew detection (optimized)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None and len(lines) > 0:
                angles = []
                for rho, theta in lines[:10]:  # Use only first 10 lines for speed
                    angle = theta * 180 / np.pi
                    if angle < 45:
                        angles.append(angle)
                    elif angle > 135:
                        angles.append(angle - 180)
                
                if angles:
                    median_angle = np.median(angles)
                    if abs(median_angle) > 0.5:  # Only correct if skew is significant
                        height, width = img_array.shape[:2]
                        center = (width // 2, height // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                        
                        # Apply rotation
                        corrected = cv2.warpAffine(
                            img_array, rotation_matrix, (width, height),
                            flags=cv2.INTER_LINEAR,  # Faster than INTER_CUBIC
                            borderMode=cv2.BORDER_REPLICATE
                        )
                        
                        return Image.fromarray(corrected)
            
            return image
            
        except Exception as e:
            logger.warning(f"Skew correction failed: {str(e)}")
            return image
    
    def _enhance_contrast_optimized(self, image: Image.Image, enhancement_factor: float) -> Image.Image:
        """Apply optimized contrast enhancement"""
        try:
            # Use PIL's built-in contrast enhancement (faster than OpenCV for this)
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(enhancement_factor)
            
        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {str(e)}")
            return image
    
    def _enhance_sharpness_optimized(self, image: Image.Image, enhancement_factor: float) -> Image.Image:
        """Apply optimized sharpness enhancement"""
        try:
            # Use PIL's built-in sharpness enhancement
            enhancer = ImageEnhance.Sharpness(image)
            return enhancer.enhance(enhancement_factor)
            
        except Exception as e:
            logger.warning(f"Sharpness enhancement failed: {str(e)}")
            return image
    
    def _apply_morphological_operations_optimized(self, image: Image.Image) -> Image.Image:
        """Apply optimized morphological operations"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale for morphological operations
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply morphological closing to connect broken text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
            closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to original format
            if len(img_array.shape) == 3:
                result = cv2.cvtColor(closed, cv2.COLOR_GRAY2RGB)
            else:
                result = closed
            
            return Image.fromarray(result)
            
        except Exception as e:
            logger.warning(f"Morphological operations failed: {str(e)}")
            return image
    
    def _final_ocr_optimization(self, image: Image.Image) -> Image.Image:
        """Apply final optimizations for OCR"""
        try:
            # Convert to grayscale for OCR (most OCR engines work better with grayscale)
            if image.mode != 'L':
                image = image.convert('L')
            
            # Apply slight Gaussian blur to smooth text edges
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Apply unsharp mask to enhance text edges
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            return image
            
        except Exception as e:
            logger.warning(f"Final OCR optimization failed: {str(e)}")
            return image
    
    def get_preprocessing_info(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Get information about preprocessing that would be applied"""
        try:
            # Get basic info from original preprocessor logic
            if mime_type == 'application/pdf':
                images = convert_from_bytes(file_content, dpi=72)  # Low DPI for info only
                page_count = len(images)
                sample_image = images[0]
            else:
                page_count = 1
                sample_image = Image.open(io.BytesIO(file_content))
            
            # Classify document
            profile = self.classifier.classify_document(sample_image)
            
            width, height = sample_image.size
            estimated_dpi = max(width, height) / 8.5
            
            # Check cache status
            cache_status = "disabled"
            if self.enable_caching and self.cache:
                cached_result = self.cache.get(file_content, profile)
                cache_status = "hit" if cached_result else "miss"
            
            return {
                'page_count': page_count,
                'original_size': (width, height),
                'estimated_dpi': round(estimated_dpi),
                'detected_profile': profile.name,
                'target_dpi': profile.target_dpi,
                'will_resize': abs(estimated_dpi - profile.target_dpi) > 50,
                'cache_status': cache_status,
                'parallel_processing': page_count > 1 and self.max_workers > 1,
                'supported_format': mime_type in self.supported_formats
            }
            
        except Exception as e:
            logger.error(f"Failed to get preprocessing info: {str(e)}")
            return {
                'error': str(e),
                'supported_format': mime_type in self.supported_formats
            }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = self.stats.copy()
        
        # Add cache statistics if available
        if self.enable_caching and self.cache:
            cache_stats = self.cache.get_stats()
            stats.update({
                'cache_hit_rate': cache_stats['hit_rate'],
                'cache_size_mb': cache_stats['size_mb'],
                'cache_max_size_mb': cache_stats['max_size_mb']
            })
        
        return stats
    
    def clear_cache(self):
        """Clear preprocessing cache"""
        if self.enable_caching and self.cache:
            self.cache.clear()
            logger.info("Preprocessing cache cleared")
    
    def optimize_cache_size(self):
        """Optimize cache size by removing old entries"""
        if self.enable_caching and self.cache:
            self.cache._evict_old_entries()
            logger.info("Cache optimized")