"""
PaddleOCR Performance Configuration Example

This module provides example configuration for PaddleOCR performance optimization
and monitoring features. Add these settings to your Django settings.py file.
"""

# Example Django settings for PaddleOCR Performance Optimization
PADDLEOCR_PERFORMANCE_CONFIG = {
    # Basic PaddleOCR Configuration
    'enabled': True,
    'languages': ['pl', 'en'],
    'use_gpu': False,  # Set to True if GPU available
    'model_dir': '/path/to/paddle_models/',
    'timeout': 30,
    'max_retries': 2,
    
    # Performance Monitoring Configuration
    'performance': {
        'max_memory_mb': 800.0,
        'max_processing_time': 30.0,
        'max_concurrent_requests': 3,
        'memory_warning_threshold_mb': 600.0,
        'memory_critical_threshold_mb': 750.0,
        'gc_threshold_mb': 500.0,
        'enable_model_cache': True,
        'enable_concurrent_management': True,
        'metrics_history_size': 1000
    },
    
    # Resource Management Configuration
    'resource_management': {
        'max_workers': 3,
        'max_memory_mb': 800.0,
        'max_queue_size': 10,
        'worker_timeout': 30.0,
        'cleanup_interval': 60.0
    },
    
    # Optimization Configuration
    'optimization': {
        'enable_model_caching': True,
        'enable_result_caching': True,
        'enable_memory_optimization': True,
        'enable_preprocessing_cache': True,
        
        # Cache Settings
        'max_model_cache_size': 3,
        'max_result_cache_size': 100,
        'max_preprocessing_cache_size': 50,
        'cache_ttl_hours': 24.0,
        
        # Memory Optimization
        'memory_optimization_threshold_mb': 600.0,
        'aggressive_cleanup_threshold_mb': 750.0,
        'gc_frequency_seconds': 300.0,  # 5 minutes
        
        # Performance Tuning
        'batch_processing_enabled': True,
        'max_batch_size': 5,
        'parallel_preprocessing': True,
        'max_preprocessing_threads': 2
    },
    
    # Error Handling Configuration
    'fallback': {
        'strategy': 'retry_then_fallback',
        'max_retries': 2,
        'retry_delay': 1.0
    },
    
    # Memory Monitoring Configuration
    'memory': {
        'max_memory_mb': 800.0,
        'warning_threshold_mb': 600.0,
        'critical_threshold_mb': 750.0,
        'optimization_level': 'basic',
        'enable_alerts': True
    },
    
    # Timeout Configuration
    'timeouts': {
        'initialization': 60.0,
        'processing': 30.0,
        'model_loading': 120.0,
        'preprocessing': 15.0,
        'postprocessing': 10.0,
        'strategy': 'graceful',
        'enable_degradation': True
    },
    
    # Preprocessing Configuration
    'preprocessing': {
        'enabled': True,
        'noise_reduction': True,
        'contrast_enhancement': True,
        'skew_correction': True,
        'resolution_optimization': True
    },
    
    # Polish Optimization Configuration
    'polish_optimization': {
        'enabled': True,
        'nip_validation': True,
        'date_format_enhancement': True,
        'currency_parsing': True,
        'spatial_analysis': True
    }
}

# Environment Variables for Production
"""
# PaddleOCR Performance Configuration
PADDLEOCR_PERFORMANCE_ENABLED=true
PADDLEOCR_MAX_MEMORY_MB=800
PADDLEOCR_MAX_WORKERS=3
PADDLEOCR_MAX_CONCURRENT_REQUESTS=3
PADDLEOCR_ENABLE_MODEL_CACHE=true
PADDLEOCR_ENABLE_RESULT_CACHE=true
PADDLEOCR_CACHE_TTL_HOURS=24
PADDLEOCR_MEMORY_OPTIMIZATION_THRESHOLD=600
PADDLEOCR_GC_FREQUENCY_SECONDS=300

# Resource Management
PADDLEOCR_RESOURCE_MAX_QUEUE_SIZE=10
PADDLEOCR_WORKER_TIMEOUT=30
PADDLEOCR_CLEANUP_INTERVAL=60

# Optimization Features
PADDLEOCR_OPTIMIZATION_ENABLED=true
PADDLEOCR_MODEL_CACHE_SIZE=3
PADDLEOCR_RESULT_CACHE_SIZE=100
PADDLEOCR_PREPROCESSING_CACHE_SIZE=50
PADDLEOCR_BATCH_PROCESSING=true
PADDLEOCR_PARALLEL_PREPROCESSING=true
"""

# Example usage in Django views
EXAMPLE_USAGE = """
from faktury.services.paddle_ocr_service import PaddleOCRService

# Initialize with performance optimization
ocr_service = PaddleOCRService(
    enable_performance_monitoring=True,
    enable_resource_management=True,
    enable_optimization=True
)

# Process document with performance monitoring
result = ocr_service.process_invoice(file_content, mime_type)

# Get performance statistics
stats = ocr_service.get_performance_stats()
print(f"Processing time: {result.get('processing_time', 0):.2f}s")
print(f"Memory usage: {stats.get('performance_monitor', {}).get('current_memory_mb', 0):.1f}MB")

# Optimize performance if needed
if stats.get('performance_monitor', {}).get('current_memory_mb', 0) > 600:
    optimization_result = ocr_service.optimize_performance()
    print(f"Optimization completed: {optimization_result['actions_performed']}")

# Scale resources dynamically
ocr_service.scale_resources(worker_count=4, memory_limit_mb=1000.0)

# Clear caches if needed
ocr_service.clear_caches()
"""

# Monitoring and Alerting Integration
MONITORING_INTEGRATION = """
# Example Prometheus metrics integration
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
ocr_requests_total = Counter('paddleocr_requests_total', 'Total OCR requests')
ocr_processing_time = Histogram('paddleocr_processing_seconds', 'OCR processing time')
ocr_memory_usage = Gauge('paddleocr_memory_mb', 'OCR memory usage in MB')
ocr_cache_hits = Counter('paddleocr_cache_hits_total', 'Cache hits')
ocr_cache_misses = Counter('paddleocr_cache_misses_total', 'Cache misses')

# In your OCR processing code:
def process_with_monitoring(ocr_service, file_content, mime_type):
    ocr_requests_total.inc()
    
    with ocr_processing_time.time():
        result = ocr_service.process_invoice(file_content, mime_type)
    
    # Update metrics
    stats = ocr_service.get_performance_stats()
    if 'performance_monitor' in stats:
        ocr_memory_usage.set(stats['performance_monitor'].get('current_memory_mb', 0))
    
    if 'optimizer' in stats:
        optimizer_stats = stats['optimizer']['general_stats']
        ocr_cache_hits.inc(optimizer_stats.get('cache_hits', 0))
        ocr_cache_misses.inc(optimizer_stats.get('cache_misses', 0))
    
    return result
"""

# Health Check Integration
HEALTH_CHECK_INTEGRATION = """
# Example health check endpoint
from django.http import JsonResponse
from django.views import View

class PaddleOCRHealthView(View):
    def get(self, request):
        try:
            from faktury.services.paddle_ocr_service import PaddleOCRService
            
            # Initialize service
            ocr_service = PaddleOCRService()
            
            # Get performance stats
            stats = ocr_service.get_performance_stats()
            
            # Check health indicators
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'performance': {
                    'memory_mb': stats.get('performance_monitor', {}).get('current_memory_mb', 0),
                    'active_requests': stats.get('resource_manager', {}).get('queue_status', {}).get('active_requests', 0),
                    'cache_hit_rate': self._calculate_cache_hit_rate(stats),
                    'recent_success_rate': stats.get('performance_monitor', {}).get('recent_success_rate', 1.0)
                }
            }
            
            # Check for issues
            memory_mb = health_status['performance']['memory_mb']
            if memory_mb > 750:
                health_status['status'] = 'critical'
                health_status['issues'] = ['high_memory_usage']
            elif memory_mb > 600:
                health_status['status'] = 'warning'
                health_status['issues'] = ['elevated_memory_usage']
            
            success_rate = health_status['performance']['recent_success_rate']
            if success_rate < 0.9:
                health_status['status'] = 'warning'
                health_status.setdefault('issues', []).append('low_success_rate')
            
            return JsonResponse(health_status)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=500)
    
    def _calculate_cache_hit_rate(self, stats):
        optimizer_stats = stats.get('optimizer', {}).get('general_stats', {})
        hits = optimizer_stats.get('cache_hits', 0)
        misses = optimizer_stats.get('cache_misses', 0)
        total = hits + misses
        return hits / total if total > 0 else 0.0
"""

# Performance Tuning Guidelines
PERFORMANCE_TUNING_GUIDELINES = """
# Performance Tuning Guidelines for PaddleOCR

## Memory Optimization
1. Set appropriate memory limits based on your system:
   - Development: 400-600MB
   - Production: 800-1200MB
   - High-load: 1200-2000MB

2. Configure cache sizes based on usage patterns:
   - Model cache: 2-5 models (depending on languages used)
   - Result cache: 50-200 results (based on duplicate processing frequency)
   - Preprocessing cache: 20-100 items (based on similar document types)

3. Adjust garbage collection frequency:
   - High-load systems: 60-120 seconds
   - Normal load: 300-600 seconds
   - Low load: 600-1200 seconds

## Concurrent Processing
1. Worker count should match CPU cores:
   - 2-4 cores: 2-3 workers
   - 4-8 cores: 3-5 workers
   - 8+ cores: 5-8 workers

2. Queue size should be 2-3x worker count:
   - Prevents memory buildup
   - Provides reasonable wait times
   - Allows for burst handling

## Caching Strategy
1. Enable model caching for:
   - Multiple language processing
   - Repeated processing sessions
   - Long-running services

2. Enable result caching for:
   - Document reprocessing scenarios
   - Batch processing with duplicates
   - Development/testing environments

3. Enable preprocessing caching for:
   - Similar document types
   - Repeated processing of same formats
   - High-volume processing

## Monitoring and Alerting
1. Monitor key metrics:
   - Memory usage (alert at 80% of limit)
   - Processing time (alert if >2x normal)
   - Success rate (alert if <95%)
   - Queue size (alert if consistently >50% capacity)

2. Set up automated optimization:
   - Memory cleanup at 75% usage
   - Cache clearing at 90% usage
   - Worker scaling based on queue size

3. Performance baselines:
   - Processing time: <2 seconds per invoice
   - Memory usage: <800MB per process
   - Success rate: >95%
   - Cache hit rate: >20% (if applicable)
"""