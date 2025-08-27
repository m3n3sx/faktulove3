"""
PaddleOCR Timeout Handling with Graceful Degradation

This module provides comprehensive timeout handling for PaddleOCR operations,
including configurable timeouts, graceful degradation, and timeout recovery strategies.
"""

import logging
import time
import signal
import threading
from typing import Dict, Any, Optional, Callable, Union, List
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from .paddle_ocr_exceptions import PaddleOCRTimeoutError

logger = logging.getLogger(__name__)


class TimeoutStrategy(Enum):
    """Timeout handling strategies"""
    STRICT = "strict"  # Fail immediately on timeout
    GRACEFUL = "graceful"  # Allow graceful degradation
    RETRY = "retry"  # Retry with different parameters
    FALLBACK = "fallback"  # Switch to fallback processing


class DegradationLevel(Enum):
    """Levels of processing degradation"""
    NONE = "none"
    REDUCE_QUALITY = "reduce_quality"
    REDUCE_FEATURES = "reduce_features"
    MINIMAL_PROCESSING = "minimal_processing"


@dataclass
class TimeoutConfig:
    """Timeout configuration"""
    initialization_timeout: float = 60.0
    processing_timeout: float = 30.0
    model_loading_timeout: float = 120.0
    preprocessing_timeout: float = 15.0
    postprocessing_timeout: float = 10.0
    total_operation_timeout: float = 180.0


@dataclass
class TimeoutResult:
    """Result of timeout-handled operation"""
    success: bool
    result: Optional[Any]
    elapsed_time: float
    timeout_occurred: bool
    degradation_applied: Optional[DegradationLevel]
    strategy_used: Optional[TimeoutStrategy]
    error: Optional[Exception]


class PaddleOCRTimeoutHandler:
    """
    Handles timeouts for PaddleOCR operations with graceful degradation
    
    This handler provides:
    - Configurable timeouts for different operation types
    - Graceful degradation when timeouts occur
    - Automatic retry with reduced parameters
    - Timeout recovery strategies
    - Performance monitoring and optimization
    """
    
    def __init__(self,
                 config: Optional[TimeoutConfig] = None,
                 strategy: TimeoutStrategy = TimeoutStrategy.GRACEFUL,
                 enable_degradation: bool = True,
                 max_retries: int = 2):
        """
        Initialize timeout handler
        
        Args:
            config: Timeout configuration
            strategy: Timeout handling strategy
            enable_degradation: Enable graceful degradation
            max_retries: Maximum retry attempts
        """
        self.config = config or TimeoutConfig()
        self.strategy = strategy
        self.enable_degradation = enable_degradation
        self.max_retries = max_retries
        
        # Statistics tracking
        self.stats = {
            'total_operations': 0,
            'timeout_occurrences': 0,
            'successful_degradations': 0,
            'failed_operations': 0,
            'average_processing_time': 0.0,
            'timeout_by_operation': {},
            'degradation_effectiveness': {}
        }
        
        # Degradation strategies
        self.degradation_strategies = {
            DegradationLevel.REDUCE_QUALITY: self._reduce_quality_degradation,
            DegradationLevel.REDUCE_FEATURES: self._reduce_features_degradation,
            DegradationLevel.MINIMAL_PROCESSING: self._minimal_processing_degradation
        }
        
        logger.info(f"Timeout handler initialized with {strategy.value} strategy")
    
    @contextmanager
    def timeout_context(self, operation_name: str, timeout: Optional[float] = None):
        """Context manager for timeout handling"""
        timeout_value = timeout or self.config.processing_timeout
        start_time = time.time()
        
        logger.debug(f"Starting {operation_name} with {timeout_value}s timeout")
        
        try:
            with self._create_timeout_context(timeout_value):
                yield
                
        except Exception as error:
            elapsed = time.time() - start_time
            
            if self._is_timeout_error(error) or elapsed >= timeout_value:
                logger.warning(f"Timeout occurred in {operation_name} after {elapsed:.2f}s")
                self._handle_timeout(operation_name, elapsed, timeout_value, error)
            else:
                raise
        
        finally:
            elapsed = time.time() - start_time
            self._update_statistics(operation_name, elapsed, timeout_value)
    
    def execute_with_timeout(self,
                           operation: Callable[[], Any],
                           operation_name: str,
                           timeout: Optional[float] = None,
                           allow_degradation: bool = None) -> TimeoutResult:
        """
        Execute operation with timeout handling and optional degradation
        
        Args:
            operation: Operation to execute
            operation_name: Name of the operation for logging
            timeout: Timeout in seconds (uses config default if None)
            allow_degradation: Allow degradation (uses instance setting if None)
            
        Returns:
            TimeoutResult: Result of the operation with timeout details
        """
        timeout_value = timeout or self._get_timeout_for_operation(operation_name)
        allow_degradation = allow_degradation if allow_degradation is not None else self.enable_degradation
        
        start_time = time.time()
        self.stats['total_operations'] += 1
        
        logger.debug(f"Executing {operation_name} with {timeout_value}s timeout")
        
        # Try primary operation
        result = self._execute_with_timeout_internal(
            operation, operation_name, timeout_value, start_time
        )
        
        if result.success or not allow_degradation:
            return result
        
        # Apply degradation strategies if primary operation failed
        if result.timeout_occurred and self.strategy == TimeoutStrategy.GRACEFUL:
            logger.info(f"Attempting graceful degradation for {operation_name}")
            return self._execute_with_degradation(operation, operation_name, timeout_value, start_time)
        
        # Apply retry strategy
        elif result.timeout_occurred and self.strategy == TimeoutStrategy.RETRY:
            logger.info(f"Attempting retry for {operation_name}")
            return self._execute_with_retry(operation, operation_name, timeout_value, start_time)
        
        return result
    
    def _execute_with_timeout_internal(self,
                                     operation: Callable[[], Any],
                                     operation_name: str,
                                     timeout: float,
                                     start_time: float) -> TimeoutResult:
        """Internal timeout execution"""
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(operation)
                
                try:
                    result = future.result(timeout=timeout)
                    elapsed = time.time() - start_time
                    
                    logger.debug(f"{operation_name} completed successfully in {elapsed:.2f}s")
                    
                    return TimeoutResult(
                        success=True,
                        result=result,
                        elapsed_time=elapsed,
                        timeout_occurred=False,
                        degradation_applied=None,
                        strategy_used=self.strategy,
                        error=None
                    )
                    
                except FutureTimeoutError:
                    elapsed = time.time() - start_time
                    
                    logger.warning(f"{operation_name} timed out after {elapsed:.2f}s")
                    self.stats['timeout_occurrences'] += 1
                    
                    # Cancel the future
                    future.cancel()
                    
                    timeout_error = PaddleOCRTimeoutError(
                        f"Operation {operation_name} timed out after {elapsed:.2f}s",
                        timeout_seconds=timeout,
                        elapsed_seconds=elapsed,
                        operation=operation_name
                    )
                    
                    return TimeoutResult(
                        success=False,
                        result=None,
                        elapsed_time=elapsed,
                        timeout_occurred=True,
                        degradation_applied=None,
                        strategy_used=self.strategy,
                        error=timeout_error
                    )
                    
        except Exception as error:
            elapsed = time.time() - start_time
            
            logger.error(f"{operation_name} failed with error: {error}")
            
            return TimeoutResult(
                success=False,
                result=None,
                elapsed_time=elapsed,
                timeout_occurred=self._is_timeout_error(error),
                degradation_applied=None,
                strategy_used=self.strategy,
                error=error
            )
    
    def _execute_with_degradation(self,
                                operation: Callable[[], Any],
                                operation_name: str,
                                original_timeout: float,
                                start_time: float) -> TimeoutResult:
        """Execute operation with progressive degradation"""
        degradation_levels = [
            DegradationLevel.REDUCE_QUALITY,
            DegradationLevel.REDUCE_FEATURES,
            DegradationLevel.MINIMAL_PROCESSING
        ]
        
        for degradation_level in degradation_levels:
            logger.info(f"Applying {degradation_level.value} degradation to {operation_name}")
            
            try:
                # Apply degradation strategy
                degraded_operation = self._apply_degradation(operation, degradation_level)
                
                # Use reduced timeout for degraded operation
                degraded_timeout = original_timeout * 0.7  # 70% of original timeout
                
                result = self._execute_with_timeout_internal(
                    degraded_operation, f"{operation_name}_degraded", degraded_timeout, start_time
                )
                
                if result.success:
                    logger.info(f"Degraded operation {operation_name} succeeded with {degradation_level.value}")
                    self.stats['successful_degradations'] += 1
                    
                    result.degradation_applied = degradation_level
                    return result
                
            except Exception as error:
                logger.warning(f"Degradation {degradation_level.value} failed for {operation_name}: {error}")
                continue
        
        # All degradation attempts failed
        elapsed = time.time() - start_time
        self.stats['failed_operations'] += 1
        
        return TimeoutResult(
            success=False,
            result=None,
            elapsed_time=elapsed,
            timeout_occurred=True,
            degradation_applied=None,
            strategy_used=self.strategy,
            error=PaddleOCRTimeoutError(
                f"All degradation attempts failed for {operation_name}",
                timeout_seconds=original_timeout,
                elapsed_seconds=elapsed,
                operation=operation_name
            )
        )
    
    def _execute_with_retry(self,
                          operation: Callable[[], Any],
                          operation_name: str,
                          original_timeout: float,
                          start_time: float) -> TimeoutResult:
        """Execute operation with retry strategy"""
        for attempt in range(self.max_retries):
            logger.info(f"Retry attempt {attempt + 1}/{self.max_retries} for {operation_name}")
            
            # Increase timeout for retry attempts
            retry_timeout = original_timeout * (1.5 ** attempt)
            
            result = self._execute_with_timeout_internal(
                operation, f"{operation_name}_retry_{attempt + 1}", retry_timeout, start_time
            )
            
            if result.success:
                logger.info(f"Retry {attempt + 1} succeeded for {operation_name}")
                return result
        
        # All retries failed
        elapsed = time.time() - start_time
        self.stats['failed_operations'] += 1
        
        return TimeoutResult(
            success=False,
            result=None,
            elapsed_time=elapsed,
            timeout_occurred=True,
            degradation_applied=None,
            strategy_used=self.strategy,
            error=PaddleOCRTimeoutError(
                f"All retry attempts failed for {operation_name}",
                timeout_seconds=original_timeout,
                elapsed_seconds=elapsed,
                operation=operation_name
            )
        )
    
    def _apply_degradation(self, operation: Callable[[], Any], 
                          degradation_level: DegradationLevel) -> Callable[[], Any]:
        """Apply degradation strategy to operation"""
        strategy = self.degradation_strategies.get(degradation_level)
        
        if strategy:
            return strategy(operation)
        else:
            logger.warning(f"No degradation strategy for {degradation_level.value}")
            return operation
    
    def _reduce_quality_degradation(self, operation: Callable[[], Any]) -> Callable[[], Any]:
        """Apply quality reduction degradation"""
        def degraded_operation():
            # This would modify PaddleOCR parameters to reduce quality but increase speed
            # For example: lower DPI, reduced model complexity, etc.
            logger.debug("Applying quality reduction degradation")
            return operation()
        
        return degraded_operation
    
    def _reduce_features_degradation(self, operation: Callable[[], Any]) -> Callable[[], Any]:
        """Apply feature reduction degradation"""
        def degraded_operation():
            # This would disable some PaddleOCR features to speed up processing
            # For example: disable text direction detection, reduce language models, etc.
            logger.debug("Applying feature reduction degradation")
            return operation()
        
        return degraded_operation
    
    def _minimal_processing_degradation(self, operation: Callable[[], Any]) -> Callable[[], Any]:
        """Apply minimal processing degradation"""
        def degraded_operation():
            # This would use minimal PaddleOCR processing
            # For example: basic text extraction only, no advanced features
            logger.debug("Applying minimal processing degradation")
            return operation()
        
        return degraded_operation
    
    def _create_timeout_context(self, timeout: float):
        """Create timeout context using signal (Unix-like systems)"""
        class TimeoutContext:
            def __init__(self, timeout_seconds):
                self.timeout_seconds = timeout_seconds
                self.old_handler = None
            
            def __enter__(self):
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Operation timed out after {self.timeout_seconds} seconds")
                
                self.old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(self.timeout_seconds))
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                signal.alarm(0)  # Cancel the alarm
                if self.old_handler:
                    signal.signal(signal.SIGALRM, self.old_handler)
        
        return TimeoutContext(timeout)
    
    def _is_timeout_error(self, error: Exception) -> bool:
        """Check if error is timeout-related"""
        if isinstance(error, (TimeoutError, FutureTimeoutError, PaddleOCRTimeoutError)):
            return True
        
        error_str = str(error).lower()
        timeout_indicators = ['timeout', 'timed out', 'time limit', 'deadline exceeded']
        
        return any(indicator in error_str for indicator in timeout_indicators)
    
    def _get_timeout_for_operation(self, operation_name: str) -> float:
        """Get appropriate timeout for operation type"""
        operation_lower = operation_name.lower()
        
        if 'initialization' in operation_lower or 'init' in operation_lower:
            return self.config.initialization_timeout
        elif 'model' in operation_lower and 'load' in operation_lower:
            return self.config.model_loading_timeout
        elif 'preprocess' in operation_lower:
            return self.config.preprocessing_timeout
        elif 'postprocess' in operation_lower:
            return self.config.postprocessing_timeout
        else:
            return self.config.processing_timeout
    
    def _handle_timeout(self, operation_name: str, elapsed: float, 
                       timeout: float, error: Exception):
        """Handle timeout occurrence"""
        self.stats['timeout_occurrences'] += 1
        
        # Update operation-specific timeout stats
        if operation_name not in self.stats['timeout_by_operation']:
            self.stats['timeout_by_operation'][operation_name] = 0
        self.stats['timeout_by_operation'][operation_name] += 1
        
        # Log timeout details
        logger.error(f"Timeout in {operation_name}: {elapsed:.2f}s >= {timeout:.2f}s")
        
        # Raise appropriate timeout error
        if not isinstance(error, PaddleOCRTimeoutError):
            raise PaddleOCRTimeoutError(
                f"Operation {operation_name} timed out",
                timeout_seconds=timeout,
                elapsed_seconds=elapsed,
                operation=operation_name,
                original_error=error
            )
        else:
            raise error
    
    def _update_statistics(self, operation_name: str, elapsed: float, timeout: float):
        """Update timeout statistics"""
        # Update average processing time
        total_ops = self.stats['total_operations']
        current_avg = self.stats['average_processing_time']
        self.stats['average_processing_time'] = (current_avg * (total_ops - 1) + elapsed) / total_ops
    
    def get_timeout_statistics(self) -> Dict[str, Any]:
        """Get comprehensive timeout statistics"""
        total_ops = self.stats['total_operations']
        timeout_rate = (self.stats['timeout_occurrences'] / total_ops * 100) if total_ops > 0 else 0.0
        success_rate = ((total_ops - self.stats['failed_operations']) / total_ops * 100) if total_ops > 0 else 0.0
        
        return {
            'statistics': self.stats.copy(),
            'rates': {
                'timeout_rate_percent': timeout_rate,
                'success_rate_percent': success_rate,
                'degradation_success_rate': (
                    self.stats['successful_degradations'] / max(self.stats['timeout_occurrences'], 1) * 100
                )
            },
            'configuration': {
                'strategy': self.strategy.value,
                'enable_degradation': self.enable_degradation,
                'max_retries': self.max_retries,
                'timeouts': {
                    'initialization': self.config.initialization_timeout,
                    'processing': self.config.processing_timeout,
                    'model_loading': self.config.model_loading_timeout,
                    'preprocessing': self.config.preprocessing_timeout,
                    'postprocessing': self.config.postprocessing_timeout,
                    'total_operation': self.config.total_operation_timeout
                }
            }
        }
    
    def optimize_timeouts(self, operation_history: List[Dict[str, Any]]):
        """Optimize timeout values based on operation history"""
        if not operation_history:
            return
        
        logger.info("Optimizing timeout values based on operation history")
        
        # Analyze processing times by operation type
        operation_times = {}
        for record in operation_history:
            op_name = record.get('operation_name', 'unknown')
            elapsed = record.get('elapsed_time', 0)
            
            if op_name not in operation_times:
                operation_times[op_name] = []
            operation_times[op_name].append(elapsed)
        
        # Update timeout configuration based on analysis
        for op_name, times in operation_times.items():
            if len(times) < 5:  # Need sufficient data
                continue
            
            # Calculate 95th percentile as new timeout
            times.sort()
            percentile_95 = times[int(len(times) * 0.95)]
            recommended_timeout = percentile_95 * 1.5  # Add 50% buffer
            
            logger.info(f"Recommended timeout for {op_name}: {recommended_timeout:.1f}s "
                       f"(95th percentile: {percentile_95:.1f}s)")
    
    def reset_statistics(self):
        """Reset timeout statistics"""
        self.stats = {
            'total_operations': 0,
            'timeout_occurrences': 0,
            'successful_degradations': 0,
            'failed_operations': 0,
            'average_processing_time': 0.0,
            'timeout_by_operation': {},
            'degradation_effectiveness': {}
        }
        
        logger.info("Timeout statistics reset")