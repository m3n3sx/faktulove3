"""
OCR Performance Profiler

This module provides comprehensive performance profiling and optimization
for the OCR processing pipeline, identifying bottlenecks and providing
optimization recommendations.
"""

import logging
import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import json
from contextlib import contextmanager
from functools import wraps
import traceback

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric data"""
    name: str
    duration: float
    memory_usage: float
    cpu_usage: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class ProfilerReport:
    """Performance profiler report"""
    total_duration: float
    total_memory_peak: float
    average_cpu_usage: float
    stage_metrics: Dict[str, List[PerformanceMetric]]
    bottlenecks: List[Dict[str, Any]]
    optimization_recommendations: List[str]
    system_info: Dict[str, Any]


class OCRPerformanceProfiler:
    """
    Comprehensive performance profiler for OCR pipeline
    
    Features:
    - Stage-by-stage performance tracking
    - Memory and CPU usage monitoring
    - Bottleneck identification
    - Optimization recommendations
    - Real-time performance alerts
    """
    
    def __init__(self, 
                 enable_memory_tracking: bool = True,
                 enable_cpu_tracking: bool = True,
                 alert_threshold_seconds: float = 30.0,
                 memory_alert_threshold_mb: float = 1024.0):
        """
        Initialize performance profiler
        
        Args:
            enable_memory_tracking: Enable memory usage tracking
            enable_cpu_tracking: Enable CPU usage tracking
            alert_threshold_seconds: Alert if stage takes longer than this
            memory_alert_threshold_mb: Alert if memory usage exceeds this
        """
        self.enable_memory_tracking = enable_memory_tracking
        self.enable_cpu_tracking = enable_cpu_tracking
        self.alert_threshold_seconds = alert_threshold_seconds
        self.memory_alert_threshold_mb = memory_alert_threshold_mb
        
        # Performance data storage
        self.metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.active_profiles: Dict[str, Dict[str, Any]] = {}
        self.system_baseline: Dict[str, float] = {}
        
        # Performance history (last 100 operations)
        self.performance_history: deque = deque(maxlen=100)
        
        # Thread-local storage for nested profiling
        self.local = threading.local()
        
        # Initialize system baseline
        self._establish_system_baseline()
        
        logger.info("OCR Performance Profiler initialized")
    
    def _establish_system_baseline(self):
        """Establish system performance baseline"""
        try:
            process = psutil.Process()
            self.system_baseline = {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'available_memory_mb': psutil.virtual_memory().available / 1024 / 1024,
                'cpu_count': psutil.cpu_count(),
                'cpu_freq_mhz': psutil.cpu_freq().current if psutil.cpu_freq() else 0
            }
            logger.info(f"System baseline established: {self.system_baseline}")
        except Exception as e:
            logger.warning(f"Failed to establish system baseline: {e}")
            self.system_baseline = {}
    
    @contextmanager
    def profile_stage(self, stage_name: str, metadata: Dict[str, Any] = None):
        """
        Context manager for profiling a processing stage
        
        Args:
            stage_name: Name of the stage being profiled
            metadata: Additional metadata to store with metrics
        """
        start_time = time.time()
        start_memory = 0
        start_cpu = 0
        
        # Get initial system metrics
        try:
            if self.enable_memory_tracking:
                process = psutil.Process()
                start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            if self.enable_cpu_tracking:
                start_cpu = psutil.cpu_percent(interval=None)
        except Exception as e:
            logger.warning(f"Failed to get initial metrics for {stage_name}: {e}")
        
        # Store in thread-local for nested profiling
        if not hasattr(self.local, 'profile_stack'):
            self.local.profile_stack = []
        
        profile_data = {
            'stage_name': stage_name,
            'start_time': start_time,
            'start_memory': start_memory,
            'start_cpu': start_cpu,
            'metadata': metadata or {}
        }
        
        self.local.profile_stack.append(profile_data)
        self.active_profiles[stage_name] = profile_data
        
        try:
            yield self
        except Exception as e:
            # Record error in profile
            profile_data['error'] = str(e)
            raise
        finally:
            # Calculate final metrics
            end_time = time.time()
            duration = end_time - start_time
            
            try:
                if self.enable_memory_tracking:
                    process = psutil.Process()
                    end_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_usage = end_memory - start_memory
                else:
                    memory_usage = 0
                
                if self.enable_cpu_tracking:
                    end_cpu = psutil.cpu_percent(interval=None)
                    cpu_usage = max(0, end_cpu - start_cpu)
                else:
                    cpu_usage = 0
            except Exception as e:
                logger.warning(f"Failed to get final metrics for {stage_name}: {e}")
                memory_usage = 0
                cpu_usage = 0
            
            # Create performance metric
            metric = PerformanceMetric(
                name=stage_name,
                duration=duration,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                timestamp=end_time,
                metadata=profile_data['metadata'].copy(),
                error=profile_data.get('error')
            )
            
            # Store metric
            self.metrics[stage_name].append(metric)
            
            # Check for performance alerts
            self._check_performance_alerts(metric)
            
            # Clean up
            if stage_name in self.active_profiles:
                del self.active_profiles[stage_name]
            
            if hasattr(self.local, 'profile_stack') and self.local.profile_stack:
                self.local.profile_stack.pop()
            
            logger.debug(f"Stage '{stage_name}' completed in {duration:.2f}s, "
                        f"Memory: {memory_usage:.1f}MB, CPU: {cpu_usage:.1f}%")
    
    def profile_function(self, stage_name: str = None, metadata: Dict[str, Any] = None):
        """
        Decorator for profiling functions
        
        Args:
            stage_name: Name of the stage (defaults to function name)
            metadata: Additional metadata to store
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                name = stage_name or f"{func.__module__}.{func.__name__}"
                with self.profile_stage(name, metadata):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check for performance alerts and log warnings"""
        alerts = []
        
        # Duration alert
        if metric.duration > self.alert_threshold_seconds:
            alerts.append(f"Stage '{metric.name}' took {metric.duration:.2f}s "
                         f"(threshold: {self.alert_threshold_seconds}s)")
        
        # Memory alert
        if metric.memory_usage > self.memory_alert_threshold_mb:
            alerts.append(f"Stage '{metric.name}' used {metric.memory_usage:.1f}MB "
                         f"(threshold: {self.memory_alert_threshold_mb}MB)")
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Performance Alert: {alert}")
    
    def get_stage_statistics(self, stage_name: str) -> Dict[str, Any]:
        """Get statistics for a specific stage"""
        if stage_name not in self.metrics:
            return {}
        
        metrics = self.metrics[stage_name]
        durations = [m.duration for m in metrics if m.error is None]
        memory_usage = [m.memory_usage for m in metrics if m.error is None]
        cpu_usage = [m.cpu_usage for m in metrics if m.error is None]
        
        if not durations:
            return {'error': 'No successful executions recorded'}
        
        return {
            'execution_count': len(metrics),
            'success_count': len(durations),
            'error_count': len(metrics) - len(durations),
            'duration': {
                'mean': statistics.mean(durations),
                'median': statistics.median(durations),
                'min': min(durations),
                'max': max(durations),
                'stdev': statistics.stdev(durations) if len(durations) > 1 else 0
            },
            'memory_usage': {
                'mean': statistics.mean(memory_usage) if memory_usage else 0,
                'median': statistics.median(memory_usage) if memory_usage else 0,
                'min': min(memory_usage) if memory_usage else 0,
                'max': max(memory_usage) if memory_usage else 0
            },
            'cpu_usage': {
                'mean': statistics.mean(cpu_usage) if cpu_usage else 0,
                'median': statistics.median(cpu_usage) if cpu_usage else 0,
                'min': min(cpu_usage) if cpu_usage else 0,
                'max': max(cpu_usage) if cpu_usage else 0
            }
        }
    
    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks in the pipeline"""
        bottlenecks = []
        
        for stage_name in self.metrics:
            stats = self.get_stage_statistics(stage_name)
            if 'duration' not in stats:
                continue
            
            duration_stats = stats['duration']
            
            # Identify bottlenecks based on various criteria
            bottleneck_score = 0
            reasons = []
            
            # High average duration
            if duration_stats['mean'] > 10.0:
                bottleneck_score += 3
                reasons.append(f"High average duration: {duration_stats['mean']:.2f}s")
            
            # High variability (inconsistent performance)
            if duration_stats['stdev'] > duration_stats['mean'] * 0.5:
                bottleneck_score += 2
                reasons.append(f"High variability: {duration_stats['stdev']:.2f}s stdev")
            
            # High maximum duration
            if duration_stats['max'] > 30.0:
                bottleneck_score += 2
                reasons.append(f"High maximum duration: {duration_stats['max']:.2f}s")
            
            # High memory usage
            if 'memory_usage' in stats and stats['memory_usage']['mean'] > 500:
                bottleneck_score += 1
                reasons.append(f"High memory usage: {stats['memory_usage']['mean']:.1f}MB")
            
            # High error rate
            if stats['error_count'] > stats['success_count'] * 0.1:
                bottleneck_score += 2
                error_rate = stats['error_count'] / stats['execution_count'] * 100
                reasons.append(f"High error rate: {error_rate:.1f}%")
            
            if bottleneck_score > 0:
                bottlenecks.append({
                    'stage_name': stage_name,
                    'bottleneck_score': bottleneck_score,
                    'reasons': reasons,
                    'statistics': stats
                })
        
        # Sort by bottleneck score
        bottlenecks.sort(key=lambda x: x['bottleneck_score'], reverse=True)
        return bottlenecks
    
    def generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on profiling data"""
        recommendations = []
        bottlenecks = self.identify_bottlenecks()
        
        for bottleneck in bottlenecks[:5]:  # Top 5 bottlenecks
            stage_name = bottleneck['stage_name']
            stats = bottleneck['statistics']
            
            # Stage-specific recommendations
            if 'preprocessing' in stage_name.lower():
                recommendations.extend([
                    f"Consider optimizing image preprocessing for '{stage_name}' - "
                    f"average duration: {stats['duration']['mean']:.2f}s",
                    "Implement image caching for frequently processed document types",
                    "Consider reducing image resolution for faster processing",
                    "Implement parallel preprocessing for multi-page documents"
                ])
            
            elif 'ocr' in stage_name.lower():
                recommendations.extend([
                    f"OCR engine '{stage_name}' is a bottleneck - "
                    f"average duration: {stats['duration']['mean']:.2f}s",
                    "Consider tuning OCR engine parameters for speed vs accuracy",
                    "Implement OCR result caching for similar documents",
                    "Consider using faster OCR engines for low-confidence documents"
                ])
            
            elif 'extraction' in stage_name.lower():
                recommendations.extend([
                    f"Field extraction '{stage_name}' needs optimization - "
                    f"average duration: {stats['duration']['mean']:.2f}s",
                    "Optimize regex patterns for better performance",
                    "Implement pattern caching for common invoice layouts",
                    "Consider using compiled regex patterns"
                ])
            
            # Memory-specific recommendations
            if 'memory_usage' in stats and stats['memory_usage']['mean'] > 200:
                recommendations.append(
                    f"High memory usage in '{stage_name}' ({stats['memory_usage']['mean']:.1f}MB) - "
                    "consider memory optimization techniques"
                )
            
            # Error-specific recommendations
            if stats['error_count'] > 0:
                error_rate = stats['error_count'] / stats['execution_count'] * 100
                recommendations.append(
                    f"High error rate in '{stage_name}' ({error_rate:.1f}%) - "
                    "implement better error handling and fallback mechanisms"
                )
        
        # General recommendations
        if len(self.metrics) > 0:
            total_stages = len(self.metrics)
            if total_stages > 5:
                recommendations.append(
                    f"Pipeline has {total_stages} stages - consider consolidating "
                    "or parallelizing stages where possible"
                )
        
        # System-level recommendations
        if self.system_baseline:
            available_memory = self.system_baseline.get('available_memory_mb', 0)
            if available_memory < 1024:
                recommendations.append(
                    f"Low available memory ({available_memory:.0f}MB) - "
                    "consider increasing system memory or optimizing memory usage"
                )
            
            cpu_count = self.system_baseline.get('cpu_count', 1)
            if cpu_count > 1:
                recommendations.append(
                    f"System has {cpu_count} CPU cores - consider implementing "
                    "parallel processing where applicable"
                )
        
        return list(set(recommendations))  # Remove duplicates
    
    def generate_report(self) -> ProfilerReport:
        """Generate comprehensive performance report"""
        # Calculate overall metrics
        all_metrics = []
        for stage_metrics in self.metrics.values():
            all_metrics.extend(stage_metrics)
        
        if not all_metrics:
            return ProfilerReport(
                total_duration=0,
                total_memory_peak=0,
                average_cpu_usage=0,
                stage_metrics={},
                bottlenecks=[],
                optimization_recommendations=[],
                system_info=self.system_baseline
            )
        
        successful_metrics = [m for m in all_metrics if m.error is None]
        
        total_duration = sum(m.duration for m in successful_metrics)
        total_memory_peak = max(m.memory_usage for m in successful_metrics) if successful_metrics else 0
        average_cpu_usage = statistics.mean(m.cpu_usage for m in successful_metrics) if successful_metrics else 0
        
        # Generate bottlenecks and recommendations
        bottlenecks = self.identify_bottlenecks()
        recommendations = self.generate_optimization_recommendations()
        
        return ProfilerReport(
            total_duration=total_duration,
            total_memory_peak=total_memory_peak,
            average_cpu_usage=average_cpu_usage,
            stage_metrics=dict(self.metrics),
            bottlenecks=bottlenecks,
            optimization_recommendations=recommendations,
            system_info=self.system_baseline
        )
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        try:
            report = self.generate_report()
            
            # Convert to serializable format
            export_data = {
                'report_timestamp': time.time(),
                'total_duration': report.total_duration,
                'total_memory_peak': report.total_memory_peak,
                'average_cpu_usage': report.average_cpu_usage,
                'bottlenecks': report.bottlenecks,
                'optimization_recommendations': report.optimization_recommendations,
                'system_info': report.system_info,
                'stage_statistics': {}
            }
            
            # Add stage statistics
            for stage_name in self.metrics:
                export_data['stage_statistics'][stage_name] = self.get_stage_statistics(stage_name)
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Performance metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def clear_metrics(self):
        """Clear all stored metrics"""
        self.metrics.clear()
        self.active_profiles.clear()
        self.performance_history.clear()
        logger.info("Performance metrics cleared")
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time performance statistics"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'timestamp': time.time(),
                'memory_usage_mb': memory_info.rss / 1024 / 1024,
                'memory_percent': process.memory_percent(),
                'cpu_percent': process.cpu_percent(),
                'active_profiles': list(self.active_profiles.keys()),
                'total_stages_profiled': len(self.metrics),
                'system_memory_available_mb': psutil.virtual_memory().available / 1024 / 1024,
                'system_cpu_percent': psutil.cpu_percent()
            }
        except Exception as e:
            logger.error(f"Failed to get real-time stats: {e}")
            return {'error': str(e)}


# Global profiler instance
ocr_profiler = OCRPerformanceProfiler()