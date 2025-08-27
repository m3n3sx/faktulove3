"""
PaddleOCR Performance Monitor

This module provides comprehensive performance monitoring and optimization for PaddleOCR operations,
including memory usage tracking, processing time monitoring, concurrent request handling,
and model caching strategies.
"""

import logging
import time
import threading
import psutil
import gc
from typing import Dict, Any, Optional, List, NamedTuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, RLock
import weakref

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for OCR operations"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    memory_before_mb: float = 0.0
    memory_after_mb: float = 0.0
    memory_peak_mb: float = 0.0
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def memory_used_mb(self) -> float:
        """Calculate memory used during operation"""
        return self.memory_after_mb - self.memory_before_mb
    
    @property
    def memory_peak_delta_mb(self) -> float:
        """Calculate peak memory delta from start"""
        return self.memory_peak_mb - self.memory_before_mb


@dataclass
class ResourceLimits:
    """Resource limits for OCR operations"""
    max_memory_mb: float = 800.0
    max_processing_time_seconds: float = 30.0
    max_concurrent_requests: int = 3
    memory_warning_threshold_mb: float = 600.0
    memory_critical_threshold_mb: float = 750.0
    gc_threshold_mb: float = 500.0


@dataclass
class ModelCacheEntry:
    """Model cache entry with metadata"""
    model: Any
    last_accessed: datetime
    access_count: int = 0
    memory_size_mb: float = 0.0
    
    def touch(self):
        """Update access time and count"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class ConcurrentRequestManager:
    """Manages concurrent OCR requests with resource limits"""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.active_requests = 0
        self.request_queue = deque()
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent, thread_name_prefix="PaddleOCR")
        
    def acquire_slot(self, timeout: Optional[float] = None) -> bool:
        """Acquire a processing slot for OCR operation"""
        with self.condition:
            start_time = time.time()
            
            while self.active_requests >= self.max_concurrent:
                if timeout is not None:
                    elapsed = time.time() - start_time
                    remaining = timeout - elapsed
                    if remaining <= 0:
                        return False
                    if not self.condition.wait(timeout=remaining):
                        return False
                else:
                    self.condition.wait()
            
            self.active_requests += 1
            return True
    
    def release_slot(self):
        """Release a processing slot"""
        with self.condition:
            if self.active_requests > 0:
                self.active_requests -= 1
                self.condition.notify()
    
    @contextmanager
    def request_slot(self, timeout: Optional[float] = None):
        """Context manager for request slot management"""
        if not self.acquire_slot(timeout):
            raise RuntimeError(f"Could not acquire processing slot within {timeout}s")
        
        try:
            yield
        finally:
            self.release_slot()
    
    def submit_task(self, func: Callable, *args, **kwargs):
        """Submit a task to the thread pool"""
        return self.executor.submit(func, *args, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current request manager statistics"""
        with self.lock:
            return {
                'active_requests': self.active_requests,
                'max_concurrent': self.max_concurrent,
                'queue_size': len(self.request_queue),
                'thread_pool_active': self.executor._threads and len(self.executor._threads),
                'thread_pool_max': self.executor._max_workers
            }


class ModelCache:
    """Thread-safe model cache with LRU eviction and memory management"""
    
    def __init__(self, max_size: int = 3, max_memory_mb: float = 400.0):
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        self.cache: Dict[str, ModelCacheEntry] = {}
        self.lock = RLock()
        self.total_memory_mb = 0.0
        
    def get(self, key: str) -> Optional[Any]:
        """Get model from cache"""
        with self.lock:
            entry = self.cache.get(key)
            if entry:
                entry.touch()
                logger.debug(f"Model cache hit for key: {key}")
                return entry.model
            
            logger.debug(f"Model cache miss for key: {key}")
            return None
    
    def put(self, key: str, model: Any, memory_size_mb: float = 0.0):
        """Put model in cache with LRU eviction"""
        with self.lock:
            # If model already exists, update it
            if key in self.cache:
                old_entry = self.cache[key]
                self.total_memory_mb -= old_entry.memory_size_mb
            
            # Check if we need to evict models
            while (len(self.cache) >= self.max_size or 
                   self.total_memory_mb + memory_size_mb > self.max_memory_mb):
                if not self.cache:
                    break
                self._evict_lru()
            
            # Add new entry
            entry = ModelCacheEntry(
                model=model,
                last_accessed=datetime.now(),
                memory_size_mb=memory_size_mb
            )
            self.cache[key] = entry
            self.total_memory_mb += memory_size_mb
            
            logger.debug(f"Model cached with key: {key}, memory: {memory_size_mb:.1f}MB")
    
    def _evict_lru(self):
        """Evict least recently used model"""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed)
        
        entry = self.cache.pop(lru_key)
        self.total_memory_mb -= entry.memory_size_mb
        
        logger.debug(f"Evicted LRU model: {lru_key}, freed {entry.memory_size_mb:.1f}MB")
        
        # Force garbage collection for large models
        if entry.memory_size_mb > 50.0:
            gc.collect()
    
    def clear(self):
        """Clear all cached models"""
        with self.lock:
            self.cache.clear()
            self.total_memory_mb = 0.0
            gc.collect()
            logger.info("Model cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'total_memory_mb': self.total_memory_mb,
                'max_memory_mb': self.max_memory_mb,
                'entries': {
                    key: {
                        'last_accessed': entry.last_accessed.isoformat(),
                        'access_count': entry.access_count,
                        'memory_size_mb': entry.memory_size_mb
                    }
                    for key, entry in self.cache.items()
                }
            }


class PaddleOCRPerformanceMonitor:
    """
    Comprehensive performance monitor for PaddleOCR operations
    
    Features:
    - Memory usage tracking and limits enforcement
    - Processing time monitoring and optimization
    - Concurrent request handling with resource management
    - Model caching and reuse strategies
    - Performance metrics collection and analysis
    """
    
    def __init__(self, 
                 resource_limits: Optional[ResourceLimits] = None,
                 enable_model_cache: bool = True,
                 enable_concurrent_management: bool = True,
                 metrics_history_size: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            resource_limits: Resource limits configuration
            enable_model_cache: Enable model caching
            enable_concurrent_management: Enable concurrent request management
            metrics_history_size: Number of metrics to keep in history
        """
        self.resource_limits = resource_limits or ResourceLimits()
        self.enable_model_cache = enable_model_cache
        self.enable_concurrent_management = enable_concurrent_management
        self.metrics_history_size = metrics_history_size
        
        # Performance tracking
        self.metrics_history: deque = deque(maxlen=metrics_history_size)
        self.operation_stats: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
        
        # Model cache
        if self.enable_model_cache:
            self.model_cache = ModelCache(
                max_size=3,
                max_memory_mb=self.resource_limits.max_memory_mb * 0.5  # 50% of total limit
            )
        else:
            self.model_cache = None
        
        # Concurrent request management
        if self.enable_concurrent_management:
            self.request_manager = ConcurrentRequestManager(
                max_concurrent=self.resource_limits.max_concurrent_requests
            )
        else:
            self.request_manager = None
        
        # Memory monitoring
        self.process = psutil.Process()
        self.memory_samples: deque = deque(maxlen=100)
        self.last_gc_time = time.time()
        
        logger.info(f"PaddleOCR Performance Monitor initialized with limits: "
                   f"memory={self.resource_limits.max_memory_mb}MB, "
                   f"concurrent={self.resource_limits.max_concurrent_requests}, "
                   f"timeout={self.resource_limits.max_processing_time_seconds}s")
    
    def get_current_memory_mb(self) -> float:
        """Get current memory usage in MB"""
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0
    
    def check_memory_limits(self) -> Dict[str, Any]:
        """Check current memory usage against limits"""
        current_memory = self.get_current_memory_mb()
        
        status = {
            'current_memory_mb': current_memory,
            'limit_mb': self.resource_limits.max_memory_mb,
            'warning_threshold_mb': self.resource_limits.memory_warning_threshold_mb,
            'critical_threshold_mb': self.resource_limits.memory_critical_threshold_mb,
            'status': 'ok'
        }
        
        if current_memory >= self.resource_limits.memory_critical_threshold_mb:
            status['status'] = 'critical'
            status['action_required'] = 'immediate_cleanup'
        elif current_memory >= self.resource_limits.memory_warning_threshold_mb:
            status['status'] = 'warning'
            status['action_required'] = 'consider_cleanup'
        
        return status
    
    def enforce_memory_limits(self) -> bool:
        """Enforce memory limits and perform cleanup if necessary"""
        memory_status = self.check_memory_limits()
        
        if memory_status['status'] == 'critical':
            logger.warning(f"Critical memory usage: {memory_status['current_memory_mb']:.1f}MB")
            
            # Clear model cache
            if self.model_cache:
                self.model_cache.clear()
            
            # Force garbage collection
            gc.collect()
            
            # Check again after cleanup
            new_memory = self.get_current_memory_mb()
            logger.info(f"Memory after cleanup: {new_memory:.1f}MB")
            
            return new_memory < self.resource_limits.memory_critical_threshold_mb
        
        elif memory_status['status'] == 'warning':
            logger.info(f"Memory warning: {memory_status['current_memory_mb']:.1f}MB")
            
            # Trigger garbage collection if it's been a while
            current_time = time.time()
            if current_time - self.last_gc_time > 60:  # 1 minute
                gc.collect()
                self.last_gc_time = current_time
        
        return True
    
    @contextmanager
    def monitor_operation(self, operation_name: str, **additional_data):
        """Context manager for monitoring OCR operations"""
        # Check memory limits before starting
        if not self.enforce_memory_limits():
            raise RuntimeError(f"Memory limit exceeded: {self.get_current_memory_mb():.1f}MB")
        
        # Acquire concurrent request slot if enabled
        request_context = (self.request_manager.request_slot(
            timeout=self.resource_limits.max_processing_time_seconds
        ) if self.request_manager else self._null_context())
        
        with request_context:
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                start_time=time.time(),
                memory_before_mb=self.get_current_memory_mb(),
                additional_data=additional_data
            )
            
            peak_memory = metrics.memory_before_mb
            
            try:
                # Monitor peak memory during operation
                def memory_monitor():
                    nonlocal peak_memory
                    while metrics.end_time is None:
                        current = self.get_current_memory_mb()
                        peak_memory = max(peak_memory, current)
                        time.sleep(0.1)
                
                # Start memory monitoring thread
                monitor_thread = threading.Thread(target=memory_monitor, daemon=True)
                monitor_thread.start()
                
                yield metrics
                
                # Operation completed successfully
                metrics.success = True
                
            except Exception as e:
                metrics.success = False
                metrics.error_message = str(e)
                logger.error(f"Operation {operation_name} failed: {e}")
                raise
                
            finally:
                # Finalize metrics
                metrics.end_time = time.time()
                metrics.processing_time = metrics.end_time - metrics.start_time
                metrics.memory_after_mb = self.get_current_memory_mb()
                metrics.memory_peak_mb = peak_memory
                
                # Store metrics
                with self.lock:
                    self.metrics_history.append(metrics)
                    self.operation_stats[operation_name].append(metrics.processing_time)
                
                # Log performance info
                logger.info(f"Operation {operation_name} completed: "
                           f"time={metrics.processing_time:.2f}s, "
                           f"memory_used={metrics.memory_used_mb:.1f}MB, "
                           f"peak_delta={metrics.memory_peak_delta_mb:.1f}MB, "
                           f"success={metrics.success}")
                
                # Check for performance issues
                self._check_performance_issues(metrics)
    
    def _check_performance_issues(self, metrics: PerformanceMetrics):
        """Check for performance issues and log warnings"""
        if metrics.processing_time > self.resource_limits.max_processing_time_seconds:
            logger.warning(f"Operation {metrics.operation_name} exceeded time limit: "
                          f"{metrics.processing_time:.2f}s > {self.resource_limits.max_processing_time_seconds}s")
        
        if metrics.memory_peak_mb > self.resource_limits.memory_critical_threshold_mb:
            logger.warning(f"Operation {metrics.operation_name} exceeded memory threshold: "
                          f"{metrics.memory_peak_mb:.1f}MB > {self.resource_limits.memory_critical_threshold_mb}MB")
    
    @contextmanager
    def _null_context(self):
        """Null context manager"""
        yield
    
    def get_cached_model(self, cache_key: str) -> Optional[Any]:
        """Get model from cache"""
        if not self.model_cache:
            return None
        return self.model_cache.get(cache_key)
    
    def cache_model(self, cache_key: str, model: Any, memory_size_mb: float = 0.0):
        """Cache model with memory size estimation"""
        if not self.model_cache:
            return
        
        # Estimate memory size if not provided
        if memory_size_mb == 0.0:
            memory_size_mb = self._estimate_model_memory_size(model)
        
        self.model_cache.put(cache_key, model, memory_size_mb)
    
    def _estimate_model_memory_size(self, model: Any) -> float:
        """Estimate memory size of a model in MB"""
        try:
            # Try to get size from model attributes
            if hasattr(model, 'get_memory_usage'):
                return model.get_memory_usage() / 1024 / 1024
            
            # Rough estimation based on object size
            import sys
            size_bytes = sys.getsizeof(model)
            
            # For complex objects, multiply by a factor
            if hasattr(model, '__dict__'):
                size_bytes *= 10  # Rough multiplier for complex objects
            
            return size_bytes / 1024 / 1024
            
        except Exception as e:
            logger.debug(f"Failed to estimate model memory size: {e}")
            return 50.0  # Default estimate
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Perform performance optimization"""
        optimization_results = {
            'memory_cleanup': False,
            'cache_optimization': False,
            'gc_performed': False,
            'memory_before_mb': self.get_current_memory_mb()
        }
        
        # Check if optimization is needed
        memory_status = self.check_memory_limits()
        
        if memory_status['status'] in ['warning', 'critical']:
            # Clear model cache if memory is high
            if self.model_cache and memory_status['status'] == 'critical':
                self.model_cache.clear()
                optimization_results['cache_optimization'] = True
            
            # Force garbage collection
            gc.collect()
            optimization_results['gc_performed'] = True
            optimization_results['memory_cleanup'] = True
        
        optimization_results['memory_after_mb'] = self.get_current_memory_mb()
        optimization_results['memory_freed_mb'] = (
            optimization_results['memory_before_mb'] - optimization_results['memory_after_mb']
        )
        
        logger.info(f"Performance optimization completed: "
                   f"freed {optimization_results['memory_freed_mb']:.1f}MB")
        
        return optimization_results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self.lock:
            current_memory = self.get_current_memory_mb()
            
            # Calculate operation statistics
            operation_stats = {}
            for op_name, times in self.operation_stats.items():
                if times:
                    operation_stats[op_name] = {
                        'count': len(times),
                        'avg_time': sum(times) / len(times),
                        'min_time': min(times),
                        'max_time': max(times),
                        'total_time': sum(times)
                    }
            
            # Recent metrics summary
            recent_metrics = list(self.metrics_history)[-10:]  # Last 10 operations
            recent_success_rate = (
                sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
                if recent_metrics else 1.0
            )
            
            stats = {
                'current_memory_mb': current_memory,
                'memory_limits': {
                    'max_mb': self.resource_limits.max_memory_mb,
                    'warning_mb': self.resource_limits.memory_warning_threshold_mb,
                    'critical_mb': self.resource_limits.memory_critical_threshold_mb
                },
                'operation_statistics': operation_stats,
                'recent_success_rate': recent_success_rate,
                'total_operations': len(self.metrics_history),
                'performance_features': {
                    'model_cache_enabled': self.enable_model_cache,
                    'concurrent_management_enabled': self.enable_concurrent_management
                }
            }
            
            # Add model cache stats if enabled
            if self.model_cache:
                stats['model_cache'] = self.model_cache.get_stats()
            
            # Add request manager stats if enabled
            if self.request_manager:
                stats['request_manager'] = self.request_manager.get_stats()
            
            return stats
    
    def reset_stats(self):
        """Reset performance statistics"""
        with self.lock:
            self.metrics_history.clear()
            self.operation_stats.clear()
            logger.info("Performance statistics reset")