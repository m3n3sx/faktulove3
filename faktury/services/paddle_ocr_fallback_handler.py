"""
PaddleOCR Fallback Handler

This module implements automatic fallback mechanisms for PaddleOCR failures,
providing seamless switching to alternative OCR engines when PaddleOCR encounters issues.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable, Union
from enum import Enum
from dataclasses import dataclass

from .paddle_ocr_exceptions import (
    PaddleOCRError, PaddleOCRErrorType, PaddleOCRInitializationError,
    PaddleOCRProcessingError, PaddleOCRTimeoutError, PaddleOCRMemoryError,
    classify_error, wrap_error
)

logger = logging.getLogger(__name__)


class FallbackStrategy(Enum):
    """Fallback strategy options"""
    IMMEDIATE = "immediate"  # Fallback immediately on any error
    RETRY_THEN_FALLBACK = "retry_then_fallback"  # Retry first, then fallback
    SELECTIVE = "selective"  # Fallback only for specific error types
    DISABLED = "disabled"  # No fallback, raise original error


class FallbackEngine(Enum):
    """Available fallback OCR engines"""
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    OPENSOURCE = "opensource"
    GOOGLE_CLOUD = "google"


@dataclass
class FallbackAttempt:
    """Record of a fallback attempt"""
    engine: FallbackEngine
    success: bool
    processing_time: float
    error: Optional[Exception] = None
    confidence_score: Optional[float] = None
    timestamp: Optional[str] = None


@dataclass
class FallbackResult:
    """Result of fallback processing"""
    success: bool
    final_engine: Optional[FallbackEngine]
    result_data: Optional[Dict[str, Any]]
    attempts: List[FallbackAttempt]
    total_processing_time: float
    original_error: Optional[Exception]


class PaddleOCRFallbackHandler:
    """
    Handles automatic fallback from PaddleOCR to alternative OCR engines
    
    This handler provides sophisticated fallback logic that can:
    - Automatically detect PaddleOCR failures
    - Retry operations with different parameters
    - Switch to alternative OCR engines
    - Track fallback performance and success rates
    - Provide detailed fallback reporting
    """
    
    def __init__(self,
                 strategy: FallbackStrategy = FallbackStrategy.RETRY_THEN_FALLBACK,
                 fallback_engines: List[FallbackEngine] = None,
                 max_retries: int = 2,
                 retry_delay: float = 1.0,
                 timeout_threshold: float = 30.0,
                 memory_threshold_mb: float = 800.0):
        """
        Initialize fallback handler
        
        Args:
            strategy: Fallback strategy to use
            fallback_engines: List of engines to try in order
            max_retries: Maximum retry attempts before fallback
            retry_delay: Delay between retry attempts
            timeout_threshold: Timeout threshold for operations
            memory_threshold_mb: Memory usage threshold for fallback
        """
        self.strategy = strategy
        self.fallback_engines = fallback_engines or [
            FallbackEngine.TESSERACT,
            FallbackEngine.EASYOCR,
            FallbackEngine.OPENSOURCE
        ]
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout_threshold = timeout_threshold
        self.memory_threshold_mb = memory_threshold_mb
        
        # Statistics tracking
        self.fallback_stats = {
            'total_attempts': 0,
            'successful_fallbacks': 0,
            'failed_fallbacks': 0,
            'engine_success_rates': {engine.value: {'attempts': 0, 'successes': 0} 
                                   for engine in FallbackEngine},
            'error_type_counts': {error_type.value: 0 
                                for error_type in PaddleOCRErrorType}
        }
        
        # Cache for fallback engines
        self._engine_cache = {}
        
        logger.info(f"PaddleOCR fallback handler initialized with strategy: {strategy.value}")
    
    def execute_with_fallback(self,
                            primary_operation: Callable[[], Dict[str, Any]],
                            file_content: bytes,
                            mime_type: str,
                            operation_name: str = "process_document") -> FallbackResult:
        """
        Execute operation with automatic fallback handling
        
        Args:
            primary_operation: Primary PaddleOCR operation to execute
            file_content: Document content for fallback processing
            mime_type: MIME type of the document
            operation_name: Name of the operation for logging
            
        Returns:
            FallbackResult: Result of the operation with fallback details
        """
        start_time = time.time()
        attempts = []
        original_error = None
        
        self.fallback_stats['total_attempts'] += 1
        
        logger.info(f"Executing {operation_name} with fallback strategy: {self.strategy.value}")
        
        # Try primary PaddleOCR operation
        try:
            result = self._execute_with_retry(primary_operation, operation_name)
            
            total_time = time.time() - start_time
            logger.info(f"Primary PaddleOCR operation succeeded in {total_time:.2f}s")
            
            return FallbackResult(
                success=True,
                final_engine=None,  # Primary engine succeeded
                result_data=result,
                attempts=attempts,
                total_processing_time=total_time,
                original_error=None
            )
            
        except Exception as error:
            original_error = error
            wrapped_error = wrap_error(error) if not isinstance(error, PaddleOCRError) else error
            
            logger.warning(f"Primary PaddleOCR operation failed: {wrapped_error}")
            self._update_error_stats(wrapped_error.error_type)
            
            # Check if fallback should be attempted
            if not self._should_fallback(wrapped_error):
                logger.info("Fallback disabled or not applicable for this error type")
                return FallbackResult(
                    success=False,
                    final_engine=None,
                    result_data=None,
                    attempts=attempts,
                    total_processing_time=time.time() - start_time,
                    original_error=original_error
                )
        
        # Execute fallback strategy
        logger.info("Attempting fallback to alternative OCR engines")
        fallback_result = self._execute_fallback(file_content, mime_type, attempts)
        
        # Update statistics
        if fallback_result.success:
            self.fallback_stats['successful_fallbacks'] += 1
        else:
            self.fallback_stats['failed_fallbacks'] += 1
        
        fallback_result.original_error = original_error
        fallback_result.total_processing_time = time.time() - start_time
        
        return fallback_result
    
    def _execute_with_retry(self, operation: Callable[[], Dict[str, Any]], 
                          operation_name: str) -> Dict[str, Any]:
        """Execute operation with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retrying {operation_name} (attempt {attempt + 1}/{self.max_retries + 1})")
                    time.sleep(self.retry_delay * attempt)  # Exponential backoff
                
                return operation()
                
            except Exception as error:
                last_error = error
                wrapped_error = wrap_error(error) if not isinstance(error, PaddleOCRError) else error
                
                logger.warning(f"Attempt {attempt + 1} failed: {wrapped_error}")
                
                # Don't retry for non-retryable errors
                if not wrapped_error.is_retryable():
                    logger.info(f"Error type {wrapped_error.error_type.value} is not retryable")
                    break
                
                # Don't retry on the last attempt
                if attempt >= self.max_retries:
                    break
        
        # All retries failed
        raise last_error
    
    def _should_fallback(self, error: PaddleOCRError) -> bool:
        """Determine if fallback should be attempted for this error"""
        if self.strategy == FallbackStrategy.DISABLED:
            return False
        
        if self.strategy == FallbackStrategy.IMMEDIATE:
            return True
        
        if self.strategy == FallbackStrategy.SELECTIVE:
            # Only fallback for specific error types
            fallback_error_types = {
                PaddleOCRErrorType.INITIALIZATION,
                PaddleOCRErrorType.MODEL_LOADING,
                PaddleOCRErrorType.PROCESSING,
                PaddleOCRErrorType.TIMEOUT,
                PaddleOCRErrorType.MEMORY
            }
            return error.error_type in fallback_error_types
        
        # Default: RETRY_THEN_FALLBACK
        return True
    
    def _execute_fallback(self, file_content: bytes, mime_type: str, 
                         attempts: List[FallbackAttempt]) -> FallbackResult:
        """Execute fallback to alternative OCR engines"""
        
        for engine in self.fallback_engines:
            attempt_start = time.time()
            
            try:
                logger.info(f"Attempting fallback to {engine.value}")
                
                # Get or create engine instance
                engine_instance = self._get_fallback_engine(engine)
                if not engine_instance:
                    logger.warning(f"Fallback engine {engine.value} not available")
                    continue
                
                # Process document with fallback engine
                result = engine_instance.process_invoice(file_content, mime_type)
                
                processing_time = time.time() - attempt_start
                confidence_score = result.get('confidence_score', 0.0)
                
                # Record successful attempt
                attempt = FallbackAttempt(
                    engine=engine,
                    success=True,
                    processing_time=processing_time,
                    confidence_score=confidence_score,
                    timestamp=self._get_timestamp()
                )
                attempts.append(attempt)
                
                # Update statistics
                self._update_engine_stats(engine, True)
                
                logger.info(f"Fallback to {engine.value} succeeded in {processing_time:.2f}s "
                           f"with {confidence_score:.1f}% confidence")
                
                # Add fallback metadata to result
                result['fallback_metadata'] = {
                    'fallback_used': True,
                    'fallback_engine': engine.value,
                    'fallback_processing_time': processing_time,
                    'primary_engine_failed': True,
                    'attempts': [attempt.engine.value for attempt in attempts]
                }
                
                return FallbackResult(
                    success=True,
                    final_engine=engine,
                    result_data=result,
                    attempts=attempts,
                    total_processing_time=0,  # Will be set by caller
                    original_error=None
                )
                
            except Exception as error:
                processing_time = time.time() - attempt_start
                
                # Record failed attempt
                attempt = FallbackAttempt(
                    engine=engine,
                    success=False,
                    processing_time=processing_time,
                    error=error,
                    timestamp=self._get_timestamp()
                )
                attempts.append(attempt)
                
                # Update statistics
                self._update_engine_stats(engine, False)
                
                logger.warning(f"Fallback to {engine.value} failed in {processing_time:.2f}s: {error}")
                continue
        
        # All fallback engines failed
        logger.error("All fallback engines failed")
        
        return FallbackResult(
            success=False,
            final_engine=None,
            result_data=None,
            attempts=attempts,
            total_processing_time=0,  # Will be set by caller
            original_error=None
        )
    
    def _get_fallback_engine(self, engine: FallbackEngine):
        """Get or create fallback engine instance"""
        if engine in self._engine_cache:
            return self._engine_cache[engine]
        
        try:
            if engine == FallbackEngine.TESSERACT:
                engine_instance = self._create_tesseract_engine()
            elif engine == FallbackEngine.EASYOCR:
                engine_instance = self._create_easyocr_engine()
            elif engine == FallbackEngine.OPENSOURCE:
                engine_instance = self._create_opensource_engine()
            elif engine == FallbackEngine.GOOGLE_CLOUD:
                engine_instance = self._create_google_cloud_engine()
            else:
                logger.error(f"Unknown fallback engine: {engine}")
                return None
            
            if engine_instance:
                self._engine_cache[engine] = engine_instance
                logger.debug(f"Created and cached {engine.value} engine")
            
            return engine_instance
            
        except Exception as error:
            logger.error(f"Failed to create {engine.value} engine: {error}")
            return None
    
    def _create_tesseract_engine(self):
        """Create Tesseract OCR engine"""
        try:
            from .tesseract_ocr_engine import TesseractOCREngine
            return TesseractOCREngine()
        except ImportError:
            logger.warning("Tesseract OCR engine not available")
            return None
    
    def _create_easyocr_engine(self):
        """Create EasyOCR engine"""
        try:
            from .easyocr_engine import EasyOCREngine
            return EasyOCREngine()
        except ImportError:
            logger.warning("EasyOCR engine not available")
            return None
    
    def _create_opensource_engine(self):
        """Create Open Source OCR service"""
        try:
            from .opensource_ocr_service import OpenSourceOCRService
            return OpenSourceOCRService()
        except ImportError:
            logger.warning("Open Source OCR service not available")
            return None
    
    def _create_google_cloud_engine(self):
        """Create Google Cloud Document AI service"""
        try:
            from .document_ai_service import DocumentAIService
            return DocumentAIService()
        except ImportError:
            logger.warning("Google Cloud Document AI service not available")
            return None
    
    def _update_engine_stats(self, engine: FallbackEngine, success: bool):
        """Update engine success statistics"""
        stats = self.fallback_stats['engine_success_rates'][engine.value]
        stats['attempts'] += 1
        if success:
            stats['successes'] += 1
    
    def _update_error_stats(self, error_type: PaddleOCRErrorType):
        """Update error type statistics"""
        self.fallback_stats['error_type_counts'][error_type.value] += 1
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_fallback_statistics(self) -> Dict[str, Any]:
        """Get fallback statistics and performance metrics"""
        stats = self.fallback_stats.copy()
        
        # Calculate success rates
        for engine, engine_stats in stats['engine_success_rates'].items():
            attempts = engine_stats['attempts']
            successes = engine_stats['successes']
            engine_stats['success_rate'] = (successes / attempts * 100) if attempts > 0 else 0.0
        
        # Calculate overall fallback success rate
        total_fallbacks = stats['successful_fallbacks'] + stats['failed_fallbacks']
        stats['overall_fallback_success_rate'] = (
            stats['successful_fallbacks'] / total_fallbacks * 100
        ) if total_fallbacks > 0 else 0.0
        
        # Add configuration info
        stats['configuration'] = {
            'strategy': self.strategy.value,
            'fallback_engines': [engine.value for engine in self.fallback_engines],
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'timeout_threshold': self.timeout_threshold,
            'memory_threshold_mb': self.memory_threshold_mb
        }
        
        return stats
    
    def reset_statistics(self):
        """Reset fallback statistics"""
        self.fallback_stats = {
            'total_attempts': 0,
            'successful_fallbacks': 0,
            'failed_fallbacks': 0,
            'engine_success_rates': {engine.value: {'attempts': 0, 'successes': 0} 
                                   for engine in FallbackEngine},
            'error_type_counts': {error_type.value: 0 
                                for error_type in PaddleOCRErrorType}
        }
        logger.info("Fallback statistics reset")
    
    def clear_engine_cache(self):
        """Clear cached fallback engines"""
        self._engine_cache.clear()
        logger.info("Fallback engine cache cleared")
    
    def validate_fallback_engines(self) -> Dict[str, bool]:
        """Validate availability of fallback engines"""
        validation_results = {}
        
        for engine in self.fallback_engines:
            try:
                engine_instance = self._get_fallback_engine(engine)
                if engine_instance and hasattr(engine_instance, 'validate_processor_availability'):
                    validation_results[engine.value] = engine_instance.validate_processor_availability()
                else:
                    validation_results[engine.value] = engine_instance is not None
            except Exception as error:
                logger.warning(f"Validation failed for {engine.value}: {error}")
                validation_results[engine.value] = False
        
        return validation_results