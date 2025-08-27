"""
PaddleOCR Memory Usage Monitoring and Optimization

This module provides comprehensive memory monitoring and optimization
for PaddleOCR operations, including usage tracking, limits enforcement,
and automatic optimization strategies.
"""

import logging
import time
import gc
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - memory monitoring will be limited")

from .paddle_ocr_exceptions import PaddleOCRMemoryError

logger = logging.getLogger(__name__)


class MemoryOptimizationLevel(Enum):
    """Memory optimization levels"""
    NONE = "none"
    BASIC = "basic"
    AGGRESSIVE = "aggressive"
    EXTREME = "extreme"


@dataclass
class MemorySnapshot:
    """Memory usage snapshot"""
    timestamp: float
    process_memory_mb: float
    system_memory_mb: float
    available_memory_mb: float
    memory_percent: float
    operation: Optional[str] = None


@dataclass
class MemoryLimits:
    """Memory usage limits configuration"""
    max_process_memory_mb: float = 800.0
    max_system_memory_percent: float = 80.0
    warning_threshold_mb: float = 600.0
    critical_threshold_mb: float = 750.0
    cleanup_threshold_mb: float = 700.0


class PaddleOCRMemoryMonitor:
    """
    Memory usage monitor for PaddleOCR operations
    
    This monitor provides:
    - Real-time memory usage tracking
    - Memory limit enforcement
    - Automatic cleanup and optimization
    - Memory usage reporting and alerts
    - Optimization recommendations
    """
    
    def __init__(self,
                 limits: Optional[MemoryLimits] = None,
                 optimization_level: MemoryOptimizationLevel = MemoryOptimizationLevel.BASIC,
                 monitoring_interval: float = 1.0,
                 enable_alerts: bool = True):
        """
        Initialize memory monitor
        
        Args:
            limits: Memory usage limits configuration
            optimization_level: Level of memory optimization to apply
            monitoring_interval: Interval for memory monitoring (seconds)
            enable_alerts: Enable memory usage alerts
        """
        self.limits = limits or MemoryLimits()
        self.optimization_level = optimization_level
        self.monitoring_interval = monitoring_interval
        self.enable_alerts = enable_alerts
        
        # Memory tracking
        self.snapshots: List[MemorySnapshot] = []
        self.max_snapshots = 1000  # Keep last 1000 snapshots
        self.baseline_memory = None
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'peak_memory_mb': 0.0,
            'average_memory_mb': 0.0,
            'memory_warnings': 0,
            'memory_cleanups': 0,
            'optimization_actions': 0,
            'memory_errors': 0
        }
        
        # Optimization strategies
        self.optimization_strategies = {
            MemoryOptimizationLevel.BASIC: self._basic_optimization,
            MemoryOptimizationLevel.AGGRESSIVE: self._aggressive_optimization,
            MemoryOptimizationLevel.EXTREME: self._extreme_optimization
        }
        
        logger.info(f"Memory monitor initialized with {optimization_level.value} optimization")
        
        # Establish baseline
        self._establish_baseline()
    
    def _establish_baseline(self):
        """Establish baseline memory usage"""
        try:
            snapshot = self._take_snapshot("baseline")
            self.baseline_memory = snapshot.process_memory_mb
            logger.info(f"Memory baseline established: {self.baseline_memory:.1f} MB")
        except Exception as error:
            logger.warning(f"Failed to establish memory baseline: {error}")
            self.baseline_memory = 0.0
    
    def _take_snapshot(self, operation: Optional[str] = None) -> MemorySnapshot:
        """Take a memory usage snapshot"""
        if not PSUTIL_AVAILABLE:
            # Fallback to basic memory tracking
            import resource
            memory_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # Convert to MB
            return MemorySnapshot(
                timestamp=time.time(),
                process_memory_mb=memory_mb,
                system_memory_mb=0.0,
                available_memory_mb=0.0,
                memory_percent=0.0,
                operation=operation
            )
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()
            
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                process_memory_mb=memory_info.rss / 1024 / 1024,
                system_memory_mb=system_memory.total / 1024 / 1024,
                available_memory_mb=system_memory.available / 1024 / 1024,
                memory_percent=system_memory.percent,
                operation=operation
            )
            
            # Update statistics
            if snapshot.process_memory_mb > self.stats['peak_memory_mb']:
                self.stats['peak_memory_mb'] = snapshot.process_memory_mb
            
            return snapshot
            
        except Exception as error:
            logger.warning(f"Failed to take memory snapshot: {error}")
            return MemorySnapshot(
                timestamp=time.time(),
                process_memory_mb=0.0,
                system_memory_mb=0.0,
                available_memory_mb=0.0,
                memory_percent=0.0,
                operation=operation
            )
    
    def _store_snapshot(self, snapshot: MemorySnapshot):
        """Store memory snapshot with size limit"""
        with self.lock:
            self.snapshots.append(snapshot)
            
            # Keep only recent snapshots
            if len(self.snapshots) > self.max_snapshots:
                self.snapshots = self.snapshots[-self.max_snapshots:]
    
    @contextmanager
    def monitor_operation(self, operation_name: str):
        """Context manager for monitoring a specific operation"""
        start_snapshot = self._take_snapshot(f"{operation_name}_start")
        self._store_snapshot(start_snapshot)
        
        logger.debug(f"Starting memory monitoring for {operation_name}")
        
        try:
            yield self
            
        finally:
            end_snapshot = self._take_snapshot(f"{operation_name}_end")
            self._store_snapshot(end_snapshot)
            
            # Calculate memory usage for operation
            memory_used = end_snapshot.process_memory_mb - start_snapshot.process_memory_mb
            
            logger.debug(f"Operation {operation_name} used {memory_used:.1f} MB "
                        f"(peak: {end_snapshot.process_memory_mb:.1f} MB)")
            
            # Check for memory issues
            self._check_memory_limits(end_snapshot, operation_name)
    
    def _check_memory_limits(self, snapshot: MemorySnapshot, operation: str = "unknown"):
        """Check if memory usage exceeds limits"""
        process_memory = snapshot.process_memory_mb
        
        # Check critical threshold
        if process_memory > self.limits.critical_threshold_mb:
            self.stats['memory_errors'] += 1
            
            if process_memory > self.limits.max_process_memory_mb:
                error_msg = (f"Memory usage {process_memory:.1f} MB exceeds maximum "
                           f"{self.limits.max_process_memory_mb:.1f} MB during {operation}")
                logger.error(error_msg)
                
                # Attempt emergency cleanup
                self._emergency_cleanup()
                
                raise PaddleOCRMemoryError(
                    error_msg,
                    memory_usage_mb=process_memory,
                    memory_limit_mb=self.limits.max_process_memory_mb,
                    details={'operation': operation, 'snapshot': snapshot.__dict__}
                )
            else:
                logger.critical(f"Memory usage {process_memory:.1f} MB is critical during {operation}")
                self._trigger_optimization()
        
        # Check warning threshold
        elif process_memory > self.limits.warning_threshold_mb:
            self.stats['memory_warnings'] += 1
            
            if self.enable_alerts:
                logger.warning(f"Memory usage {process_memory:.1f} MB exceeds warning threshold "
                             f"{self.limits.warning_threshold_mb:.1f} MB during {operation}")
            
            # Trigger cleanup if above cleanup threshold
            if process_memory > self.limits.cleanup_threshold_mb:
                self._trigger_cleanup()
    
    def _trigger_cleanup(self):
        """Trigger memory cleanup"""
        logger.info("Triggering memory cleanup")
        
        try:
            # Force garbage collection
            collected = gc.collect()
            logger.debug(f"Garbage collection freed {collected} objects")
            
            # Apply optimization strategy
            if self.optimization_level != MemoryOptimizationLevel.NONE:
                self._apply_optimization()
            
            self.stats['memory_cleanups'] += 1
            
        except Exception as error:
            logger.error(f"Memory cleanup failed: {error}")
    
    def _trigger_optimization(self):
        """Trigger memory optimization"""
        logger.info("Triggering memory optimization")
        
        try:
            self._apply_optimization()
            self.stats['optimization_actions'] += 1
            
        except Exception as error:
            logger.error(f"Memory optimization failed: {error}")
    
    def _apply_optimization(self):
        """Apply memory optimization based on configured level"""
        if self.optimization_level == MemoryOptimizationLevel.NONE:
            return
        
        strategy = self.optimization_strategies.get(self.optimization_level)
        if strategy:
            strategy()
    
    def _basic_optimization(self):
        """Basic memory optimization"""
        logger.debug("Applying basic memory optimization")
        
        # Force garbage collection
        gc.collect()
        
        # Clear any cached data if available
        # This would be implemented based on specific PaddleOCR caching
    
    def _aggressive_optimization(self):
        """Aggressive memory optimization"""
        logger.debug("Applying aggressive memory optimization")
        
        # Basic optimization first
        self._basic_optimization()
        
        # Additional aggressive measures
        # Force collection of all generations
        for generation in range(3):
            gc.collect(generation)
        
        # Clear more caches and temporary data
        # Implementation would depend on PaddleOCR internals
    
    def _extreme_optimization(self):
        """Extreme memory optimization"""
        logger.debug("Applying extreme memory optimization")
        
        # Aggressive optimization first
        self._aggressive_optimization()
        
        # Extreme measures - may impact performance
        # This could include clearing model caches, reducing batch sizes, etc.
        # Implementation would be very specific to PaddleOCR usage patterns
    
    def _emergency_cleanup(self):
        """Emergency memory cleanup when limits are exceeded"""
        logger.critical("Performing emergency memory cleanup")
        
        try:
            # Force immediate garbage collection
            for _ in range(3):
                gc.collect()
            
            # Apply extreme optimization
            self._extreme_optimization()
            
            # Additional emergency measures could be implemented here
            
        except Exception as error:
            logger.error(f"Emergency cleanup failed: {error}")
    
    def start_monitoring(self):
        """Start continuous memory monitoring"""
        if self.monitoring_active:
            logger.warning("Memory monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous memory monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        
        logger.info("Memory monitoring stopped")
    
    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                snapshot = self._take_snapshot("monitoring")
                self._store_snapshot(snapshot)
                self._check_memory_limits(snapshot, "monitoring")
                
                time.sleep(self.monitoring_interval)
                
            except Exception as error:
                logger.error(f"Error in monitoring loop: {error}")
                time.sleep(self.monitoring_interval)
    
    def get_current_usage(self) -> Dict[str, Any]:
        """Get current memory usage information"""
        snapshot = self._take_snapshot("current_usage")
        
        usage_info = {
            'process_memory_mb': snapshot.process_memory_mb,
            'system_memory_mb': snapshot.system_memory_mb,
            'available_memory_mb': snapshot.available_memory_mb,
            'memory_percent': snapshot.memory_percent,
            'baseline_memory_mb': self.baseline_memory,
            'memory_increase_mb': snapshot.process_memory_mb - (self.baseline_memory or 0),
            'limits': {
                'max_process_memory_mb': self.limits.max_process_memory_mb,
                'warning_threshold_mb': self.limits.warning_threshold_mb,
                'critical_threshold_mb': self.limits.critical_threshold_mb
            },
            'status': self._get_memory_status(snapshot)
        }
        
        return usage_info
    
    def _get_memory_status(self, snapshot: MemorySnapshot) -> str:
        """Get memory status description"""
        memory_mb = snapshot.process_memory_mb
        
        if memory_mb > self.limits.critical_threshold_mb:
            return "critical"
        elif memory_mb > self.limits.warning_threshold_mb:
            return "warning"
        else:
            return "normal"
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        current_usage = self.get_current_usage()
        
        # Calculate average memory usage
        if self.snapshots:
            total_memory = sum(s.process_memory_mb for s in self.snapshots)
            self.stats['average_memory_mb'] = total_memory / len(self.snapshots)
        
        statistics = {
            'current_usage': current_usage,
            'statistics': self.stats.copy(),
            'configuration': {
                'optimization_level': self.optimization_level.value,
                'monitoring_interval': self.monitoring_interval,
                'limits': {
                    'max_process_memory_mb': self.limits.max_process_memory_mb,
                    'max_system_memory_percent': self.limits.max_system_memory_percent,
                    'warning_threshold_mb': self.limits.warning_threshold_mb,
                    'critical_threshold_mb': self.limits.critical_threshold_mb
                }
            },
            'snapshots_count': len(self.snapshots),
            'monitoring_active': self.monitoring_active,
            'psutil_available': PSUTIL_AVAILABLE
        }
        
        return statistics
    
    def get_memory_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get memory usage history"""
        snapshots = self.snapshots[-limit:] if limit else self.snapshots
        
        return [
            {
                'timestamp': s.timestamp,
                'process_memory_mb': s.process_memory_mb,
                'system_memory_mb': s.system_memory_mb,
                'available_memory_mb': s.available_memory_mb,
                'memory_percent': s.memory_percent,
                'operation': s.operation
            }
            for s in snapshots
        ]
    
    def clear_history(self):
        """Clear memory usage history"""
        with self.lock:
            self.snapshots.clear()
        
        logger.info("Memory usage history cleared")
    
    def reset_statistics(self):
        """Reset memory statistics"""
        self.stats = {
            'peak_memory_mb': 0.0,
            'average_memory_mb': 0.0,
            'memory_warnings': 0,
            'memory_cleanups': 0,
            'optimization_actions': 0,
            'memory_errors': 0
        }
        
        logger.info("Memory statistics reset")
    
    def optimize_for_document_size(self, file_size_mb: float) -> MemoryOptimizationLevel:
        """Recommend optimization level based on document size"""
        if file_size_mb < 5:
            return MemoryOptimizationLevel.NONE
        elif file_size_mb < 20:
            return MemoryOptimizationLevel.BASIC
        elif file_size_mb < 50:
            return MemoryOptimizationLevel.AGGRESSIVE
        else:
            return MemoryOptimizationLevel.EXTREME
    
    def __enter__(self):
        """Context manager entry"""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_monitoring()