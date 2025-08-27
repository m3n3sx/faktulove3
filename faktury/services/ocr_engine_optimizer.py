"""
OCR Engine Parameter Optimizer

This module provides optimization of OCR engine parameters specifically
for Polish invoice processing, including adaptive parameter tuning based
on document characteristics and performance feedback.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .ocr_performance_profiler import ocr_profiler

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """OCR optimization strategies"""
    SPEED_FOCUSED = "speed_focused"
    ACCURACY_FOCUSED = "accuracy_focused"
    BALANCED = "balanced"
    POLISH_OPTIMIZED = "polish_optimized"


@dataclass
class OCRParameters:
    """OCR engine parameters configuration"""
    # Tesseract parameters
    tesseract_oem: int = 3  # OCR Engine Mode (0-3)
    tesseract_psm: int = 6  # Page Segmentation Mode (0-13)
    tesseract_dpi: int = 300  # DPI setting
    tesseract_timeout: int = 60  # Timeout in seconds
    tesseract_preserve_interword_spaces: bool = True
    tesseract_char_whitelist: str = ""  # Character whitelist
    tesseract_char_blacklist: str = ""  # Character blacklist
    
    # EasyOCR parameters
    easyocr_width_ths: float = 0.7  # Text width threshold
    easyocr_height_ths: float = 0.7  # Text height threshold
    easyocr_decoder: str = "greedy"  # Decoding method
    easyocr_beamWidth: int = 5  # Beam search width
    easyocr_batch_size: int = 1  # Batch size
    easyocr_text_threshold: float = 0.7  # Text detection threshold
    easyocr_low_text: float = 0.4  # Low text threshold
    easyocr_link_threshold: float = 0.4  # Link threshold
    easyocr_canvas_size: int = 2560  # Canvas size
    easyocr_mag_ratio: float = 1.5  # Magnification ratio
    
    # Performance parameters
    max_processing_time: float = 30.0  # Maximum processing time
    min_confidence_threshold: float = 70.0  # Minimum confidence threshold
    parallel_processing: bool = True  # Enable parallel processing
    
    # Polish-specific parameters
    polish_language_boost: float = 1.2  # Boost for Polish patterns
    polish_nip_validation: bool = True  # Enable NIP validation
    polish_date_formats: bool = True  # Enable Polish date formats
    polish_currency_patterns: bool = True  # Enable Polish currency patterns
    
    # Metadata
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    created_timestamp: float = field(default_factory=time.time)
    performance_score: float = 0.0
    usage_count: int = 0


@dataclass
class OptimizationResult:
    """Result of parameter optimization"""
    optimized_parameters: OCRParameters
    performance_improvement: float
    optimization_time: float
    test_results: List[Dict[str, Any]]
    recommendations: List[str]


class ParameterOptimizer:
    """Optimize OCR parameters based on document characteristics and performance"""
    
    def __init__(self):
        """Initialize parameter optimizer"""
        self.optimization_history: List[OptimizationResult] = []
        self.parameter_sets: Dict[str, OCRParameters] = {}
        self.performance_cache: Dict[str, float] = {}
        self._lock = threading.Lock()
        
        # Initialize default parameter sets
        self._initialize_default_parameters()
        
        logger.info("OCR Engine Parameter Optimizer initialized")
    
    def _initialize_default_parameters(self):
        """Initialize default parameter sets for different strategies"""
        
        # Speed-focused parameters
        self.parameter_sets['speed_focused'] = OCRParameters(
            tesseract_oem=1,  # Legacy engine (faster)
            tesseract_psm=6,  # Uniform block of text
            tesseract_dpi=200,  # Lower DPI for speed
            tesseract_timeout=15,  # Shorter timeout
            easyocr_width_ths=0.8,  # Higher threshold for speed
            easyocr_height_ths=0.8,
            easyocr_text_threshold=0.8,
            easyocr_canvas_size=1280,  # Smaller canvas
            max_processing_time=15.0,
            min_confidence_threshold=60.0,
            strategy=OptimizationStrategy.SPEED_FOCUSED
        )
        
        # Accuracy-focused parameters
        self.parameter_sets['accuracy_focused'] = OCRParameters(
            tesseract_oem=3,  # LSTM engine (more accurate)
            tesseract_psm=6,  # Uniform block of text
            tesseract_dpi=400,  # Higher DPI for accuracy
            tesseract_timeout=120,  # Longer timeout
            tesseract_preserve_interword_spaces=True,
            easyocr_width_ths=0.6,  # Lower threshold for accuracy
            easyocr_height_ths=0.6,
            easyocr_text_threshold=0.6,
            easyocr_canvas_size=3840,  # Larger canvas
            max_processing_time=60.0,
            min_confidence_threshold=80.0,
            strategy=OptimizationStrategy.ACCURACY_FOCUSED
        )
        
        # Balanced parameters
        self.parameter_sets['balanced'] = OCRParameters(
            tesseract_oem=3,  # LSTM engine
            tesseract_psm=6,  # Uniform block of text
            tesseract_dpi=300,  # Standard DPI
            tesseract_timeout=60,  # Standard timeout
            tesseract_preserve_interword_spaces=True,
            easyocr_width_ths=0.7,
            easyocr_height_ths=0.7,
            easyocr_text_threshold=0.7,
            easyocr_canvas_size=2560,
            max_processing_time=30.0,
            min_confidence_threshold=70.0,
            strategy=OptimizationStrategy.BALANCED
        )
        
        # Polish-optimized parameters
        self.parameter_sets['polish_optimized'] = OCRParameters(
            tesseract_oem=3,  # LSTM engine
            tesseract_psm=6,  # Uniform block of text
            tesseract_dpi=350,  # Optimized for Polish text
            tesseract_timeout=90,
            tesseract_preserve_interword_spaces=True,
            tesseract_char_whitelist=(
                "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                "ĄĆĘŁŃÓŚŹŻąćęłńóśźż.,/-:()[]{}%€$zł "
            ),
            easyocr_width_ths=0.65,  # Optimized for Polish text
            easyocr_height_ths=0.65,
            easyocr_text_threshold=0.65,
            easyocr_canvas_size=2880,
            max_processing_time=45.0,
            min_confidence_threshold=75.0,
            polish_language_boost=1.3,
            polish_nip_validation=True,
            polish_date_formats=True,
            polish_currency_patterns=True,
            strategy=OptimizationStrategy.POLISH_OPTIMIZED
        )
    
    @ocr_profiler.profile_function("parameter_optimization")
    def optimize_parameters(self, 
                           document_samples: List[bytes],
                           target_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
                           max_optimization_time: float = 300.0) -> OptimizationResult:
        """
        Optimize OCR parameters based on document samples
        
        Args:
            document_samples: List of document samples for testing
            target_strategy: Target optimization strategy
            max_optimization_time: Maximum time to spend on optimization
            
        Returns:
            OptimizationResult with optimized parameters
        """
        start_time = time.time()
        
        logger.info(f"Starting parameter optimization with strategy: {target_strategy.value}")
        
        try:
            # Get base parameters for the strategy
            base_params = self.parameter_sets.get(
                target_strategy.value, 
                self.parameter_sets['balanced']
            ).copy()
            
            # Test base parameters
            with ocr_profiler.profile_stage("baseline_testing"):
                baseline_results = self._test_parameters(base_params, document_samples)
                baseline_score = self._calculate_performance_score(baseline_results)
            
            logger.info(f"Baseline performance score: {baseline_score:.2f}")
            
            # Optimize parameters using different approaches
            optimization_approaches = [
                self._optimize_tesseract_parameters,
                self._optimize_easyocr_parameters,
                self._optimize_polish_parameters,
                self._optimize_performance_parameters
            ]
            
            best_params = base_params
            best_score = baseline_score
            all_test_results = baseline_results.copy()
            
            for approach in optimization_approaches:
                if time.time() - start_time > max_optimization_time:
                    logger.warning("Optimization time limit reached")
                    break
                
                try:
                    with ocr_profiler.profile_stage(f"optimization_{approach.__name__}"):
                        optimized_params = approach(best_params, document_samples)
                        test_results = self._test_parameters(optimized_params, document_samples)
                        score = self._calculate_performance_score(test_results)
                    
                    if score > best_score:
                        best_params = optimized_params
                        best_score = score
                        all_test_results.extend(test_results)
                        logger.info(f"Improved performance with {approach.__name__}: {score:.2f}")
                    
                except Exception as e:
                    logger.warning(f"Optimization approach {approach.__name__} failed: {e}")
                    continue
            
            # Generate recommendations
            recommendations = self._generate_optimization_recommendations(
                best_params, all_test_results, target_strategy
            )
            
            # Create optimization result
            optimization_time = time.time() - start_time
            performance_improvement = ((best_score - baseline_score) / baseline_score * 100) if baseline_score > 0 else 0
            
            result = OptimizationResult(
                optimized_parameters=best_params,
                performance_improvement=performance_improvement,
                optimization_time=optimization_time,
                test_results=all_test_results,
                recommendations=recommendations
            )
            
            # Store optimization result
            with self._lock:
                self.optimization_history.append(result)
                self.parameter_sets[f"optimized_{target_strategy.value}_{int(time.time())}"] = best_params
            
            logger.info(f"Parameter optimization completed in {optimization_time:.2f}s. "
                       f"Performance improvement: {performance_improvement:.1f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Parameter optimization failed: {e}")
            raise
    
    def _test_parameters(self, parameters: OCRParameters, document_samples: List[bytes]) -> List[Dict[str, Any]]:
        """Test OCR parameters on document samples"""
        results = []
        
        # Import here to avoid circular imports
        from .tesseract_ocr_engine import TesseractOCREngine
        from .easyocr_engine import EasyOCREngine
        
        try:
            # Create engines with optimized parameters
            tesseract_config = self._build_tesseract_config(parameters)
            tesseract_engine = TesseractOCREngine(config=tesseract_config)
            tesseract_engine.initialize()
            
            easyocr_engine = EasyOCREngine()
            easyocr_engine.easyocr_config.update(self._build_easyocr_config(parameters))
            easyocr_engine.initialize()
            
            # Test on samples
            for i, sample in enumerate(document_samples[:5]):  # Limit to 5 samples for speed
                try:
                    # Test Tesseract
                    start_time = time.time()
                    tesseract_result = tesseract_engine.process_document(sample, 'image/png')
                    tesseract_time = time.time() - start_time
                    
                    # Test EasyOCR
                    start_time = time.time()
                    easyocr_result = easyocr_engine.process_document(sample, 'image/png')
                    easyocr_time = time.time() - start_time
                    
                    results.append({
                        'sample_index': i,
                        'tesseract_confidence': tesseract_result.get('confidence_score', 0),
                        'tesseract_time': tesseract_time,
                        'tesseract_text_length': len(tesseract_result.get('text', '')),
                        'easyocr_confidence': easyocr_result.get('confidence_score', 0),
                        'easyocr_time': easyocr_time,
                        'easyocr_text_length': len(easyocr_result.get('text', '')),
                        'parameters_hash': hash(str(parameters.__dict__))
                    })
                    
                except Exception as e:
                    logger.warning(f"Testing failed for sample {i}: {e}")
                    results.append({
                        'sample_index': i,
                        'error': str(e),
                        'parameters_hash': hash(str(parameters.__dict__))
                    })
            
        except Exception as e:
            logger.error(f"Parameter testing failed: {e}")
        
        return results
    
    def _calculate_performance_score(self, test_results: List[Dict[str, Any]]) -> float:
        """Calculate overall performance score from test results"""
        if not test_results:
            return 0.0
        
        valid_results = [r for r in test_results if 'error' not in r]
        if not valid_results:
            return 0.0
        
        # Calculate weighted score
        confidence_scores = []
        time_scores = []
        
        for result in valid_results:
            # Confidence score (0-100)
            avg_confidence = (
                result.get('tesseract_confidence', 0) + 
                result.get('easyocr_confidence', 0)
            ) / 2
            confidence_scores.append(avg_confidence)
            
            # Time score (inverse of time, normalized)
            avg_time = (
                result.get('tesseract_time', 60) + 
                result.get('easyocr_time', 60)
            ) / 2
            time_score = max(0, 100 - (avg_time * 2))  # Penalize slow processing
            time_scores.append(time_score)
        
        # Weighted average (70% confidence, 30% speed)
        if confidence_scores and time_scores:
            avg_confidence = statistics.mean(confidence_scores)
            avg_time_score = statistics.mean(time_scores)
            return (avg_confidence * 0.7) + (avg_time_score * 0.3)
        
        return 0.0
    
    def _optimize_tesseract_parameters(self, base_params: OCRParameters, 
                                     document_samples: List[bytes]) -> OCRParameters:
        """Optimize Tesseract-specific parameters"""
        optimized = base_params.__class__(**base_params.__dict__)
        
        # Test different OEM modes
        best_score = 0
        for oem in [1, 3]:  # Legacy and LSTM
            test_params = base_params.__class__(**optimized.__dict__)
            test_params.tesseract_oem = oem
            
            results = self._test_parameters(test_params, document_samples[:2])  # Quick test
            score = self._calculate_performance_score(results)
            
            if score > best_score:
                best_score = score
                optimized.tesseract_oem = oem
        
        # Test different PSM modes for invoices
        best_score = 0
        for psm in [6, 7, 8]:  # Different text block modes
            test_params = base_params.__class__(**optimized.__dict__)
            test_params.tesseract_psm = psm
            
            results = self._test_parameters(test_params, document_samples[:2])
            score = self._calculate_performance_score(results)
            
            if score > best_score:
                best_score = score
                optimized.tesseract_psm = psm
        
        # Optimize DPI
        best_score = 0
        for dpi in [250, 300, 350, 400]:
            test_params = base_params.__class__(**optimized.__dict__)
            test_params.tesseract_dpi = dpi
            
            results = self._test_parameters(test_params, document_samples[:2])
            score = self._calculate_performance_score(results)
            
            if score > best_score:
                best_score = score
                optimized.tesseract_dpi = dpi
        
        return optimized
    
    def _optimize_easyocr_parameters(self, base_params: OCRParameters, 
                                   document_samples: List[bytes]) -> OCRParameters:
        """Optimize EasyOCR-specific parameters"""
        optimized = base_params.__class__(**base_params.__dict__)
        
        # Test different threshold combinations
        threshold_combinations = [
            (0.6, 0.6, 0.6),  # Low thresholds for better detection
            (0.7, 0.7, 0.7),  # Balanced
            (0.8, 0.8, 0.8),  # High thresholds for speed
        ]
        
        best_score = 0
        for width_ths, height_ths, text_ths in threshold_combinations:
            test_params = base_params.__class__(**optimized.__dict__)
            test_params.easyocr_width_ths = width_ths
            test_params.easyocr_height_ths = height_ths
            test_params.easyocr_text_threshold = text_ths
            
            results = self._test_parameters(test_params, document_samples[:2])
            score = self._calculate_performance_score(results)
            
            if score > best_score:
                best_score = score
                optimized.easyocr_width_ths = width_ths
                optimized.easyocr_height_ths = height_ths
                optimized.easyocr_text_threshold = text_ths
        
        # Test different canvas sizes
        best_score = 0
        for canvas_size in [1920, 2560, 3840]:
            test_params = base_params.__class__(**optimized.__dict__)
            test_params.easyocr_canvas_size = canvas_size
            
            results = self._test_parameters(test_params, document_samples[:2])
            score = self._calculate_performance_score(results)
            
            if score > best_score:
                best_score = score
                optimized.easyocr_canvas_size = canvas_size
        
        return optimized
    
    def _optimize_polish_parameters(self, base_params: OCRParameters, 
                                  document_samples: List[bytes]) -> OCRParameters:
        """Optimize Polish-specific parameters"""
        optimized = base_params.__class__(**base_params.__dict__)
        
        # Enable Polish optimizations
        optimized.polish_nip_validation = True
        optimized.polish_date_formats = True
        optimized.polish_currency_patterns = True
        
        # Test different language boost values
        best_score = 0
        for boost in [1.0, 1.1, 1.2, 1.3, 1.5]:
            test_params = base_params.__class__(**optimized.__dict__)
            test_params.polish_language_boost = boost
            
            results = self._test_parameters(test_params, document_samples[:2])
            score = self._calculate_performance_score(results)
            
            if score > best_score:
                best_score = score
                optimized.polish_language_boost = boost
        
        # Optimize character whitelist for Polish
        polish_chars = "ĄĆĘŁŃÓŚŹŻąćęłńóśźż"
        base_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        symbols = ".,/-:()[]{}%€$zł "
        
        optimized.tesseract_char_whitelist = base_chars + polish_chars + symbols
        
        return optimized
    
    def _optimize_performance_parameters(self, base_params: OCRParameters, 
                                       document_samples: List[bytes]) -> OCRParameters:
        """Optimize performance-related parameters"""
        optimized = base_params.__class__(**base_params.__dict__)
        
        # Test different timeout values
        results = self._test_parameters(optimized, document_samples[:2])
        avg_time = statistics.mean([
            (r.get('tesseract_time', 0) + r.get('easyocr_time', 0)) / 2
            for r in results if 'error' not in r
        ]) if results else 30.0
        
        # Set timeout to 2x average processing time, but at least 30s
        optimized.tesseract_timeout = max(30, int(avg_time * 2))
        optimized.max_processing_time = max(30.0, avg_time * 1.5)
        
        # Adjust confidence threshold based on results
        if results:
            avg_confidence = statistics.mean([
                (r.get('tesseract_confidence', 0) + r.get('easyocr_confidence', 0)) / 2
                for r in results if 'error' not in r
            ])
            
            # Set threshold to 10% below average confidence
            optimized.min_confidence_threshold = max(50.0, avg_confidence * 0.9)
        
        return optimized
    
    def _build_tesseract_config(self, parameters: OCRParameters) -> str:
        """Build Tesseract configuration string from parameters"""
        config_parts = [
            f"--oem {parameters.tesseract_oem}",
            f"--psm {parameters.tesseract_psm}",
            f"-c tessedit_char_whitelist={parameters.tesseract_char_whitelist}",
            f"-c tessedit_char_blacklist={parameters.tesseract_char_blacklist}",
        ]
        
        if parameters.tesseract_preserve_interword_spaces:
            config_parts.append("-c preserve_interword_spaces=1")
        
        return " ".join(config_parts)
    
    def _build_easyocr_config(self, parameters: OCRParameters) -> Dict[str, Any]:
        """Build EasyOCR configuration dictionary from parameters"""
        return {
            'width_ths': parameters.easyocr_width_ths,
            'height_ths': parameters.easyocr_height_ths,
            'decoder': parameters.easyocr_decoder,
            'beamWidth': parameters.easyocr_beamWidth,
            'batch_size': parameters.easyocr_batch_size,
            'text_threshold': parameters.easyocr_text_threshold,
            'low_text': parameters.easyocr_low_text,
            'link_threshold': parameters.easyocr_link_threshold,
            'canvas_size': parameters.easyocr_canvas_size,
            'mag_ratio': parameters.easyocr_mag_ratio
        }
    
    def _generate_optimization_recommendations(self, 
                                             parameters: OCRParameters,
                                             test_results: List[Dict[str, Any]],
                                             strategy: OptimizationStrategy) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if not test_results:
            return ["No test results available for recommendations"]
        
        valid_results = [r for r in test_results if 'error' not in r]
        if not valid_results:
            return ["All tests failed - check OCR engine configuration"]
        
        # Analyze performance
        avg_confidence = statistics.mean([
            (r.get('tesseract_confidence', 0) + r.get('easyocr_confidence', 0)) / 2
            for r in valid_results
        ])
        
        avg_time = statistics.mean([
            (r.get('tesseract_time', 0) + r.get('easyocr_time', 0)) / 2
            for r in valid_results
        ])
        
        # Generate recommendations based on performance
        if avg_confidence < 70:
            recommendations.append(
                f"Low average confidence ({avg_confidence:.1f}%) - consider using accuracy-focused parameters"
            )
            recommendations.append("Increase DPI settings for better text recognition")
            recommendations.append("Enable morphological operations in preprocessing")
        
        if avg_time > 30:
            recommendations.append(
                f"High processing time ({avg_time:.1f}s) - consider speed optimizations"
            )
            recommendations.append("Reduce canvas size for EasyOCR")
            recommendations.append("Use lower DPI settings if accuracy is acceptable")
        
        # Strategy-specific recommendations
        if strategy == OptimizationStrategy.POLISH_OPTIMIZED:
            recommendations.append("Enable Polish language boost for better recognition")
            recommendations.append("Use Polish-specific character whitelist")
            recommendations.append("Enable NIP validation for invoice processing")
        
        elif strategy == OptimizationStrategy.SPEED_FOCUSED:
            recommendations.append("Use Tesseract Legacy engine (OEM 1) for faster processing")
            recommendations.append("Increase confidence thresholds to reduce processing time")
            recommendations.append("Reduce image preprocessing steps")
        
        elif strategy == OptimizationStrategy.ACCURACY_FOCUSED:
            recommendations.append("Use higher DPI settings (350-400)")
            recommendations.append("Enable all preprocessing steps")
            recommendations.append("Use lower confidence thresholds for better coverage")
        
        # Parameter-specific recommendations
        if parameters.tesseract_dpi < 300:
            recommendations.append("Consider increasing DPI for better text quality")
        
        if parameters.easyocr_canvas_size > 3000:
            recommendations.append("Large canvas size may slow processing - consider reducing")
        
        return recommendations
    
    def get_optimized_parameters(self, strategy: OptimizationStrategy) -> OCRParameters:
        """Get optimized parameters for a specific strategy"""
        # Look for recent optimized parameters
        strategy_key = f"optimized_{strategy.value}"
        recent_optimized = None
        
        with self._lock:
            for key, params in self.parameter_sets.items():
                if key.startswith(strategy_key):
                    if recent_optimized is None or params.created_timestamp > recent_optimized.created_timestamp:
                        recent_optimized = params
        
        if recent_optimized:
            return recent_optimized
        
        # Return default parameters for strategy
        return self.parameter_sets.get(strategy.value, self.parameter_sets['balanced'])
    
    def save_optimization_results(self, filepath: str):
        """Save optimization results to file"""
        try:
            export_data = {
                'optimization_history': [
                    {
                        'parameters': result.optimized_parameters.__dict__,
                        'performance_improvement': result.performance_improvement,
                        'optimization_time': result.optimization_time,
                        'recommendations': result.recommendations,
                        'test_results_count': len(result.test_results)
                    }
                    for result in self.optimization_history
                ],
                'parameter_sets': {
                    key: params.__dict__ for key, params in self.parameter_sets.items()
                },
                'export_timestamp': time.time()
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Optimization results saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save optimization results: {e}")
    
    def load_optimization_results(self, filepath: str):
        """Load optimization results from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Load parameter sets
            for key, params_dict in data.get('parameter_sets', {}).items():
                self.parameter_sets[key] = OCRParameters(**params_dict)
            
            logger.info(f"Optimization results loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load optimization results: {e}")


# Global optimizer instance
ocr_optimizer = ParameterOptimizer()