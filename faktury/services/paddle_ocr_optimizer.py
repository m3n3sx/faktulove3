"""
PaddleOCR Optimizer

This module provides optimization strategies for PaddleOCR operations,
including model caching, memory optimization, and performance tuning.
"""

import logging
import time
import gc
import threading
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import weakref
import pickle
import hashlib
import os
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """Configuration for PaddleOCR optimization"""
    enable_model_caching: bool = True
    enable_result_caching: bool = True
    enable_memory_optimization: bool = True
    enable_preprocessing_cache: bool = True
    
    # Cache settings
    max_model_cache_size: int = 3
    max_result_cache_size: int = 100
    max_preprocessing_cache_size: int = 50
    cache_ttl_hours: float = 24.0
    
    # Memory optimization
    memory_optimization_threshold_mb: float = 600.0
    aggressive_cleanup_threshold_mb: float = 750.0
    gc_frequency_seconds: float = 300.0  # 5 minutes
    
    # Performance tuning
    batch_processing_enabled: bool = True
    max_batch_size: int = 5
    parallel_preprocessing: bool = True
    max_preprocessing_threads: int = 2


@dataclass
class CacheEntry:
    """Generic cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def touch(self):
        """Update access time and count"""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def is_expired(self, ttl_hours: float) -> bool:
        """Check if entry is expired"""
        age = datetime.now() - self.created_at
        return age.total_seconds() > (ttl_hours * 3600)
    
    def get_age_hours(self) -> float:
        """Get age in hours"""
        age = datetime.now() - self.created_at
        return age.total_seconds() / 3600


class LRUCache:
    """Thread-safe LRU cache with TTL and size limits"""
    
    def __init__(self, max_size: int, ttl_hours: float = 24.0):
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()
        self.total_size_bytes = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            entry = self.cache.get(key)
            if not entry:
                return None
            
            # Check if expired
            if entry.is_expired(self.ttl_hours):
                self._remove_entry(key)
                return None
            
            entry.touch()
            return entry.value
    
    def put(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        """Put value in cache"""
        with self.lock:
            # Calculate size
            size_bytes = self._estimate_size(value)
            
            # Remove existing entry if present
            if key in self.cache:
                self._remove_entry(key)
            
            # Evict entries if necessary
            while len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                size_bytes=size_bytes,
                metadata=metadata or {}
            )
            
            self.cache[key] = entry
            self.total_size_bytes += size_bytes
    
    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        entry = self.cache.pop(key, None)
        if entry:
            self.total_size_bytes -= entry.size_bytes
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed)
        self._remove_entry(lru_key)
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        try:
            return len(pickle.dumps(value))
        except Exception:
            import sys
            return sys.getsizeof(value)
    
    def clear(self):
        """Clear all entries"""
        with self.lock:
            self.cache.clear()
            self.total_size_bytes = 0
    
    def cleanup_expired(self):
        """Remove expired entries"""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired(self.ttl_hours)
            ]
            
            for key in expired_keys:
                self._remove_entry(key)
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'total_size_bytes': self.total_size_bytes,
                'hit_rate': self._calculate_hit_rate(),
                'entries': {
                    key: {
                        'age_hours': entry.get_age_hours(),
                        'access_count': entry.access_count,
                        'size_bytes': entry.size_bytes
                    }
                    for key, entry in self.cache.items()
                }
            }
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if not self.cache:
            return 0.0
        
        total_accesses = sum(entry.access_count for entry in self.cache.values())
        return total_accesses / len(self.cache) if self.cache else 0.0


class ModelOptimizer:
    """Optimizer for PaddleOCR models"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.model_cache = LRUCache(
            max_size=config.max_model_cache_size,
            ttl_hours=config.cache_ttl_hours
        ) if config.enable_model_caching else None
        
        self.optimization_history: deque = deque(maxlen=100)
        self.lock = threading.Lock()
    
    def get_cached_model(self, model_key: str) -> Optional[Any]:
        """Get cached model"""
        if not self.model_cache:
            return None
        
        model = self.model_cache.get(model_key)
        if model:
            logger.debug(f"Model cache hit: {model_key}")
        else:
            logger.debug(f"Model cache miss: {model_key}")
        
        return model
    
    def cache_model(self, model_key: str, model: Any, metadata: Optional[Dict[str, Any]] = None):
        """Cache model with metadata"""
        if not self.model_cache:
            return
        
        self.model_cache.put(model_key, model, metadata)
        logger.debug(f"Model cached: {model_key}")
    
    def optimize_model_loading(self, model_loader: Callable, model_key: str, **kwargs) -> Any:
        """Optimize model loading with caching"""
        # Try to get from cache first
        cached_model = self.get_cached_model(model_key)
        if cached_model:
            return cached_model
        
        # Load model
        start_time = time.time()
        model = model_loader(**kwargs)
        load_time = time.time() - start_time
        
        # Cache the model
        metadata = {
            'load_time': load_time,
            'kwargs': kwargs,
            'loaded_at': datetime.now().isoformat()
        }
        self.cache_model(model_key, model, metadata)
        
        logger.info(f"Model loaded and cached: {model_key} (load_time: {load_time:.2f}s)")
        return model
    
    def clear_model_cache(self):
        """Clear model cache"""
        if self.model_cache:
            self.model_cache.clear()
            logger.info("Model cache cleared")
    
    def get_model_cache_stats(self) -> Dict[str, Any]:
        """Get model cache statistics"""
        if not self.model_cache:
            return {'enabled': False}
        
        return {
            'enabled': True,
            **self.model_cache.get_stats()
        }


class ResultCache:
    """Cache for OCR processing results"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.cache = LRUCache(
            max_size=config.max_result_cache_size,
            ttl_hours=config.cache_ttl_hours
        ) if config.enable_result_caching else None
    
    def _generate_cache_key(self, file_content: bytes, processing_params: Dict[str, Any]) -> str:
        """Generate cache key for file content and parameters"""
        # Hash file content
        content_hash = hashlib.md5(file_content).hexdigest()
        
        # Hash processing parameters
        params_str = str(sorted(processing_params.items()))
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        return f"ocr_{content_hash}_{params_hash}"
    
    def get_cached_result(self, file_content: bytes, processing_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached OCR result"""
        if not self.cache:
            return None
        
        cache_key = self._generate_cache_key(file_content, processing_params)
        result = self.cache.get(cache_key)
        
        if result:
            logger.debug(f"OCR result cache hit: {cache_key[:16]}...")
        else:
            logger.debug(f"OCR result cache miss: {cache_key[:16]}...")
        
        return result
    
    def cache_result(self, file_content: bytes, processing_params: Dict[str, Any], result: Dict[str, Any]):
        """Cache OCR result"""
        if not self.cache:
            return
        
        cache_key = self._generate_cache_key(file_content, processing_params)
        
        # Add cache metadata to result
        cached_result = {
            **result,
            'cache_metadata': {
                'cached_at': datetime.now().isoformat(),
                'cache_key': cache_key,
                'processing_params': processing_params
            }
        }
        
        self.cache.put(cache_key, cached_result)
        logger.debug(f"OCR result cached: {cache_key[:16]}...")
    
    def clear_cache(self):
        """Clear result cache"""
        if self.cache:
            self.cache.clear()
            logger.info("Result cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get result cache statistics"""
        if not self.cache:
            return {'enabled': False}
        
        return {
            'enabled': True,
            **self.cache.get_stats()
        }


class MemoryOptimizer:
    """Memory optimization for PaddleOCR operations"""
    
    def __init__(self, config: OptimizationConfig, performance_monitor: Optional['PaddleOCRPerformanceMonitor'] = None):
        self.config = config
        self.performance_monitor = performance_monitor
        self.last_gc_time = time.time()
        self.optimization_stats = {
            'gc_runs': 0,
            'memory_freed_mb': 0.0,
            'cache_clears': 0
        }
    
    def should_optimize_memory(self) -> bool:
        """Check if memory optimization is needed"""
        if not self.performance_monitor:
            return False
        
        current_memory = self.performance_monitor.get_current_memory_mb()
        return current_memory >= self.config.memory_optimization_threshold_mb
    
    def optimize_memory(self, aggressive: bool = False) -> Dict[str, Any]:
        """Perform memory optimization"""
        start_memory = self.performance_monitor.get_current_memory_mb() if self.performance_monitor else 0.0
        
        optimization_actions = []
        
        # Force garbage collection
        gc.collect()
        self.optimization_stats['gc_runs'] += 1
        optimization_actions.append('garbage_collection')
        
        # Clear caches if aggressive or memory is critical
        current_memory = self.performance_monitor.get_current_memory_mb() if self.performance_monitor else 0.0
        
        if aggressive or current_memory >= self.config.aggressive_cleanup_threshold_mb:
            # This would be called from the main optimizer
            optimization_actions.append('cache_clearing_requested')
        
        end_memory = self.performance_monitor.get_current_memory_mb() if self.performance_monitor else 0.0
        memory_freed = start_memory - end_memory
        self.optimization_stats['memory_freed_mb'] += memory_freed
        
        result = {
            'memory_before_mb': start_memory,
            'memory_after_mb': end_memory,
            'memory_freed_mb': memory_freed,
            'actions_taken': optimization_actions,
            'aggressive': aggressive
        }
        
        logger.info(f"Memory optimization completed: freed {memory_freed:.1f}MB")
        return result
    
    def schedule_gc_if_needed(self):
        """Schedule garbage collection if needed"""
        current_time = time.time()
        
        if (current_time - self.last_gc_time) >= self.config.gc_frequency_seconds:
            if self.should_optimize_memory():
                self.optimize_memory()
            else:
                gc.collect()
                self.optimization_stats['gc_runs'] += 1
            
            self.last_gc_time = current_time
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get memory optimization statistics"""
        return {
            **self.optimization_stats,
            'last_gc_time': self.last_gc_time,
            'gc_frequency_seconds': self.config.gc_frequency_seconds
        }


class PaddleOCROptimizer:
    """
    Main optimizer for PaddleOCR operations
    
    Provides comprehensive optimization including model caching,
    result caching, memory optimization, and performance tuning.
    """
    
    def __init__(self, 
                 config: Optional[OptimizationConfig] = None,
                 performance_monitor: Optional['PaddleOCRPerformanceMonitor'] = None):
        """
        Initialize PaddleOCR optimizer
        
        Args:
            config: Optimization configuration
            performance_monitor: Performance monitor instance
        """
        self.config = config or OptimizationConfig()
        self.performance_monitor = performance_monitor
        
        # Initialize optimizers
        self.model_optimizer = ModelOptimizer(self.config)
        self.result_cache = ResultCache(self.config)
        self.memory_optimizer = MemoryOptimizer(self.config, performance_monitor)
        
        # Preprocessing cache
        self.preprocessing_cache = LRUCache(
            max_size=self.config.max_preprocessing_cache_size,
            ttl_hours=self.config.cache_ttl_hours
        ) if self.config.enable_preprocessing_cache else None
        
        # Statistics
        self.optimization_stats = {
            'total_optimizations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'memory_optimizations': 0
        }
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        logger.info("PaddleOCR Optimizer initialized")
    
    def optimize_model_loading(self, model_loader: Callable, model_key: str, **kwargs) -> Any:
        """Optimize model loading with caching"""
        return self.model_optimizer.optimize_model_loading(model_loader, model_key, **kwargs)
    
    def get_cached_result(self, file_content: bytes, processing_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached OCR result"""
        result = self.result_cache.get_cached_result(file_content, processing_params)
        
        if result:
            self.optimization_stats['cache_hits'] += 1
        else:
            self.optimization_stats['cache_misses'] += 1
        
        return result
    
    def cache_result(self, file_content: bytes, processing_params: Dict[str, Any], result: Dict[str, Any]):
        """Cache OCR result"""
        self.result_cache.cache_result(file_content, processing_params, result)
    
    def get_cached_preprocessing(self, preprocessing_key: str) -> Optional[Any]:
        """Get cached preprocessing result"""
        if not self.preprocessing_cache:
            return None
        
        return self.preprocessing_cache.get(preprocessing_key)
    
    def cache_preprocessing(self, preprocessing_key: str, preprocessed_data: Any):
        """Cache preprocessing result"""
        if not self.preprocessing_cache:
            return
        
        self.preprocessing_cache.put(preprocessing_key, preprocessed_data)
    
    def optimize_memory(self, aggressive: bool = False) -> Dict[str, Any]:
        """Perform comprehensive memory optimization"""
        self.optimization_stats['memory_optimizations'] += 1
        
        # Memory optimization
        memory_result = self.memory_optimizer.optimize_memory(aggressive)
        
        # Clear caches if aggressive
        if aggressive:
            self.model_optimizer.clear_model_cache()
            self.result_cache.clear_cache()
            if self.preprocessing_cache:
                self.preprocessing_cache.clear()
            
            memory_result['caches_cleared'] = True
        
        return memory_result
    
    def should_optimize_memory(self) -> bool:
        """Check if memory optimization is needed"""
        return self.memory_optimizer.should_optimize_memory()
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                time.sleep(300)  # Run every 5 minutes
                
                # Clean up expired cache entries
                if self.model_optimizer.model_cache:
                    expired = self.model_optimizer.model_cache.cleanup_expired()
                    if expired > 0:
                        logger.debug(f"Cleaned up {expired} expired model cache entries")
                
                if self.result_cache.cache:
                    expired = self.result_cache.cache.cleanup_expired()
                    if expired > 0:
                        logger.debug(f"Cleaned up {expired} expired result cache entries")
                
                if self.preprocessing_cache:
                    expired = self.preprocessing_cache.cleanup_expired()
                    if expired > 0:
                        logger.debug(f"Cleaned up {expired} expired preprocessing cache entries")
                
                # Schedule memory optimization if needed
                self.memory_optimizer.schedule_gc_if_needed()
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        return {
            'general_stats': self.optimization_stats,
            'model_cache': self.model_optimizer.get_model_cache_stats(),
            'result_cache': self.result_cache.get_cache_stats(),
            'preprocessing_cache': (
                self.preprocessing_cache.get_stats() 
                if self.preprocessing_cache else {'enabled': False}
            ),
            'memory_optimization': self.memory_optimizer.get_optimization_stats(),
            'configuration': {
                'model_caching_enabled': self.config.enable_model_caching,
                'result_caching_enabled': self.config.enable_result_caching,
                'memory_optimization_enabled': self.config.enable_memory_optimization,
                'preprocessing_cache_enabled': self.config.enable_preprocessing_cache
            }
        }
    
    def clear_all_caches(self):
        """Clear all caches"""
        self.model_optimizer.clear_model_cache()
        self.result_cache.clear_cache()
        if self.preprocessing_cache:
            self.preprocessing_cache.clear()
        
        logger.info("All caches cleared")
    
    def reconfigure(self, new_config: OptimizationConfig):
        """Reconfigure optimizer with new settings"""
        self.config = new_config
        
        # Reinitialize components if needed
        if not new_config.enable_model_caching and self.model_optimizer.model_cache:
            self.model_optimizer.clear_model_cache()
            self.model_optimizer.model_cache = None
        
        if not new_config.enable_result_caching and self.result_cache.cache:
            self.result_cache.clear_cache()
            self.result_cache.cache = None
        
        if not new_config.enable_preprocessing_cache and self.preprocessing_cache:
            self.preprocessing_cache.clear()
            self.preprocessing_cache = None
        
        logger.info("PaddleOCR Optimizer reconfigured")