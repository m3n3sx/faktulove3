# PaddleOCR Performance Tuning and Optimization Guide

## Overview

This guide provides detailed instructions for optimizing PaddleOCR performance in the FaktuLove system. It covers memory management, processing speed optimization, accuracy tuning, and resource utilization strategies specifically for Polish invoice processing.

## Performance Targets

### Baseline Performance Metrics

- **Processing Time**: < 2 seconds per invoice
- **Memory Usage**: < 800MB per process
- **Accuracy**: > 90% on Polish invoice test set
- **Confidence Correlation**: > 85% correlation with actual accuracy
- **Throughput**: 10+ concurrent requests
- **Availability**: 99.9% uptime

## Memory Optimization

### Memory Configuration

```python
# Optimal memory settings for different environments

# Development Environment (4GB RAM)
PADDLEOCR_CONFIG['performance'] = {
    'max_memory_mb': 512,
    'max_workers': 1,
    'batch_size': 1,
    'model_cache_size': 2
}

# Production Environment (8GB+ RAM)
PADDLEOCR_CONFIG['performance'] = {
    'max_memory_mb': 1024,
    'max_workers': 3,
    'batch_size': 2,
    'model_cache_size': 4
}

# High-Performance Environment (16GB+ RAM)
PADDLEOCR_CONFIG['performance'] = {
    'max_memory_mb': 2048,
    'max_workers': 6,
    'batch_size': 4,
    'model_cache_size': 8
}
```

### Memory Monitoring

```python
from faktury.services.paddle_ocr_service import PaddleOCRService
import psutil
import gc

class MemoryMonitor:
    def __init__(self):
        self.baseline_memory = psutil.virtual_memory().used
    
    def check_memory_usage(self):
        current_memory = psutil.virtual_memory().used
        memory_increase = current_memory - self.baseline_memory
        return {
            'current_mb': current_memory / 1024 / 1024,
            'increase_mb': memory_increase / 1024 / 1024,
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    
    def force_cleanup(self):
        gc.collect()
        # Force PaddleOCR model cleanup if needed
        PaddleOCRService.cleanup_models()

# Usage example
monitor = MemoryMonitor()
# ... process documents ...
memory_stats = monitor.check_memory_usage()
if memory_stats['increase_mb'] > 500:
    monitor.force_cleanup()
```

### Memory Leak Prevention

```python
# Implement proper resource cleanup
class OptimizedPaddleOCRService(PaddleOCRService):
    def __init__(self):
        super().__init__()
        self.processing_count = 0
        self.cleanup_threshold = 100
    
    def process_invoice(self, file_content, mime_type):
        try:
            result = super().process_invoice(file_content, mime_type)
            self.processing_count += 1
            
            # Periodic cleanup
            if self.processing_count >= self.cleanup_threshold:
                self._cleanup_resources()
                self.processing_count = 0
            
            return result
        finally:
            # Always cleanup temporary resources
            self._cleanup_temp_files()
    
    def _cleanup_resources(self):
        import gc
        gc.collect()
        # Clear model cache if memory usage is high
        if self._get_memory_usage() > 800:
            self._reload_models()
```

## Processing Speed Optimization

### Image Preprocessing Optimization

```python
# Fast preprocessing pipeline for high-volume processing
FAST_PREPROCESSING_CONFIG = {
    'preprocessing': {
        'enabled': True,
        'noise_reduction': False,      # Disable for speed
        'contrast_enhancement': True,   # Keep for quality
        'skew_correction': False,      # Disable for speed
        'resolution_optimization': True # Keep for efficiency
    }
}

# Quality preprocessing pipeline for accuracy
QUALITY_PREPROCESSING_CONFIG = {
    'preprocessing': {
        'enabled': True,
        'noise_reduction': True,
        'contrast_enhancement': True,
        'skew_correction': True,
        'resolution_optimization': True,
        'advanced_filtering': True
    }
}

# Adaptive preprocessing based on document quality
class AdaptivePreprocessor:
    def __init__(self):
        self.quality_threshold = 0.7
    
    def get_preprocessing_config(self, image_quality_score):
        if image_quality_score > self.quality_threshold:
            return FAST_PREPROCESSING_CONFIG
        else:
            return QUALITY_PREPROCESSING_CONFIG
```

### Parallel Processing

```python
import concurrent.futures
from typing import List, Dict, Any

class ParallelOCRProcessor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.ocr_service = PaddleOCRService()
    
    def process_multiple_invoices(self, documents: List[Dict]) -> List[Dict]:
        """Process multiple documents in parallel"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_doc = {
                executor.submit(
                    self.ocr_service.process_invoice,
                    doc['content'],
                    doc['mime_type']
                ): doc for doc in documents
            }
            
            results = []
            for future in concurrent.futures.as_completed(future_to_doc):
                doc = future_to_doc[future]
                try:
                    result = future.result(timeout=30)
                    result['document_id'] = doc['id']
                    results.append(result)
                except Exception as exc:
                    print(f'Document {doc["id"]} generated an exception: {exc}')
                    results.append({
                        'document_id': doc['id'],
                        'error': str(exc),
                        'confidence_score': 0.0
                    })
            
            return results

# Usage
processor = ParallelOCRProcessor(max_workers=4)
results = processor.process_multiple_invoices(document_batch)
```

### Batch Processing Optimization

```python
class BatchOCRProcessor:
    def __init__(self, batch_size=4):
        self.batch_size = batch_size
        self.ocr_service = PaddleOCRService()
    
    def process_batch(self, documents: List[bytes]) -> List[Dict]:
        """Process documents in optimized batches"""
        results = []
        
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            
            # Pre-load models once per batch
            self.ocr_service.ensure_models_loaded()
            
            batch_results = []
            for doc in batch:
                result = self.ocr_service.process_invoice(doc, 'application/pdf')
                batch_results.append(result)
            
            results.extend(batch_results)
            
            # Optional: cleanup between batches
            if len(batch_results) == self.batch_size:
                self.ocr_service.cleanup_temp_resources()
        
        return results
```

## GPU Acceleration

### GPU Configuration

```python
# Check GPU availability
import paddle

def configure_gpu():
    if paddle.is_compiled_with_cuda():
        gpu_count = paddle.device.cuda.device_count()
        print(f"GPU available: {gpu_count} devices")
        
        # Configure GPU settings
        PADDLEOCR_CONFIG.update({
            'use_gpu': True,
            'gpu_mem': 2000,  # MB
            'enable_mkldnn': True,
            'cpu_threads': 4
        })
        
        return True
    else:
        print("GPU not available, using CPU")
        PADDLEOCR_CONFIG.update({
            'use_gpu': False,
            'enable_mkldnn': True,
            'cpu_threads': 8
        })
        return False

# GPU memory management
class GPUMemoryManager:
    def __init__(self):
        self.gpu_available = configure_gpu()
    
    def monitor_gpu_memory(self):
        if self.gpu_available:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            return {
                'total': info.total / 1024**2,  # MB
                'used': info.used / 1024**2,   # MB
                'free': info.free / 1024**2    # MB
            }
        return None
    
    def cleanup_gpu_memory(self):
        if self.gpu_available:
            paddle.device.cuda.empty_cache()
```

### CPU Optimization

```python
# CPU-specific optimizations
CPU_OPTIMIZED_CONFIG = {
    'use_gpu': False,
    'enable_mkldnn': True,
    'cpu_threads': 8,
    'use_tensorrt': False,
    'precision': 'fp32',
    'ir_optim': True
}

# Multi-threading configuration
import os
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
```

## Accuracy Optimization

### Polish-Specific Tuning

```python
# Optimized settings for Polish invoices
POLISH_OPTIMIZED_CONFIG = {
    'languages': ['pl'],  # Polish only for better accuracy
    'drop_score': 0.3,    # Lower threshold for Polish text
    'use_space_char': True,
    'use_angle_cls': True,
    'det_limit_side_len': 1280,  # Higher resolution for Polish text
    'det_limit_type': 'max',
    'rec_batch_num': 6,
    'max_text_length': 25000,
    'polish_optimization': {
        'enabled': True,
        'nip_validation': True,
        'date_format_enhancement': True,
        'currency_parsing': True,
        'spatial_analysis': True,
        'context_validation': True
    }
}

# Confidence threshold optimization
class ConfidenceOptimizer:
    def __init__(self):
        self.field_thresholds = {
            'numer_faktury': 0.85,
            'data_wystawienia': 0.80,
            'sprzedawca_nip': 0.90,
            'nabywca_nip': 0.90,
            'suma_brutto': 0.85,
            'suma_netto': 0.85,
            'suma_vat': 0.85
        }
    
    def should_accept_field(self, field_name: str, confidence: float) -> bool:
        threshold = self.field_thresholds.get(field_name, 0.75)
        return confidence >= threshold
    
    def get_review_priority(self, extracted_data: Dict) -> str:
        """Determine review priority based on confidence scores"""
        low_confidence_fields = []
        
        for field, value in extracted_data.items():
            if isinstance(value, dict) and 'confidence' in value:
                if not self.should_accept_field(field, value['confidence']):
                    low_confidence_fields.append(field)
        
        if not low_confidence_fields:
            return 'auto_accept'
        elif len(low_confidence_fields) <= 2:
            return 'quick_review'
        else:
            return 'full_review'
```

### Model Fine-tuning

```python
# Custom model configuration for Polish invoices
CUSTOM_MODEL_CONFIG = {
    'det_model_dir': '/app/paddle_models/custom_det_polish',
    'rec_model_dir': '/app/paddle_models/custom_rec_polish',
    'cls_model_dir': '/app/paddle_models/custom_cls_polish',
    'char_dict_path': '/app/paddle_models/polish_dict.txt'
}

class CustomModelManager:
    def __init__(self):
        self.model_versions = {
            'standard': 'v2.7',
            'polish_optimized': 'v2.7-pl-opt',
            'invoice_specialized': 'v2.7-pl-inv'
        }
    
    def select_best_model(self, document_type: str) -> str:
        """Select optimal model based on document characteristics"""
        if document_type == 'polish_invoice':
            return 'invoice_specialized'
        elif document_type == 'polish_document':
            return 'polish_optimized'
        else:
            return 'standard'
```

## Caching Strategies

### Model Caching

```python
import functools
import time
from typing import Optional

class ModelCache:
    def __init__(self, max_size=4, ttl=3600):  # 1 hour TTL
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get_model(self, model_key: str):
        """Get cached model or load new one"""
        current_time = time.time()
        
        if model_key in self.cache:
            model, timestamp = self.cache[model_key]
            if current_time - timestamp < self.ttl:
                return model
            else:
                # Model expired, remove from cache
                del self.cache[model_key]
        
        # Load new model
        model = self._load_model(model_key)
        
        # Add to cache (with LRU eviction if needed)
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[model_key] = (model, current_time)
        return model
    
    def _load_model(self, model_key: str):
        """Load PaddleOCR model"""
        from paddleocr import PaddleOCR
        return PaddleOCR(lang='pl', **self._get_model_config(model_key))

# Global model cache instance
model_cache = ModelCache()
```

### Result Caching

```python
import hashlib
import pickle
from django.core.cache import cache

class OCRResultCache:
    def __init__(self, cache_timeout=3600):  # 1 hour
        self.cache_timeout = cache_timeout
    
    def get_cache_key(self, file_content: bytes, config: Dict) -> str:
        """Generate cache key from file content and config"""
        content_hash = hashlib.md5(file_content).hexdigest()
        config_hash = hashlib.md5(str(sorted(config.items())).encode()).hexdigest()
        return f"ocr_result_{content_hash}_{config_hash}"
    
    def get_cached_result(self, file_content: bytes, config: Dict) -> Optional[Dict]:
        """Get cached OCR result"""
        cache_key = self.get_cache_key(file_content, config)
        return cache.get(cache_key)
    
    def cache_result(self, file_content: bytes, config: Dict, result: Dict):
        """Cache OCR result"""
        cache_key = self.get_cache_key(file_content, config)
        cache.set(cache_key, result, self.cache_timeout)
    
    def invalidate_cache(self, file_content: bytes, config: Dict):
        """Invalidate specific cache entry"""
        cache_key = self.get_cache_key(file_content, config)
        cache.delete(cache_key)

# Usage in OCR service
class CachedPaddleOCRService(PaddleOCRService):
    def __init__(self):
        super().__init__()
        self.result_cache = OCRResultCache()
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict:
        # Check cache first
        config = self.get_current_config()
        cached_result = self.result_cache.get_cached_result(file_content, config)
        
        if cached_result:
            return cached_result
        
        # Process normally
        result = super().process_invoice(file_content, mime_type)
        
        # Cache result
        self.result_cache.cache_result(file_content, config, result)
        
        return result
```

## Performance Monitoring

### Real-time Metrics

```python
import time
import statistics
from collections import deque
from typing import Deque, Dict, List

class PerformanceMonitor:
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.processing_times: Deque[float] = deque(maxlen=window_size)
        self.confidence_scores: Deque[float] = deque(maxlen=window_size)
        self.memory_usage: Deque[float] = deque(maxlen=window_size)
        self.error_count = 0
        self.total_processed = 0
    
    def record_processing(self, processing_time: float, confidence: float, memory_mb: float):
        """Record processing metrics"""
        self.processing_times.append(processing_time)
        self.confidence_scores.append(confidence)
        self.memory_usage.append(memory_mb)
        self.total_processed += 1
    
    def record_error(self):
        """Record processing error"""
        self.error_count += 1
    
    def get_current_stats(self) -> Dict:
        """Get current performance statistics"""
        if not self.processing_times:
            return {}
        
        return {
            'avg_processing_time': statistics.mean(self.processing_times),
            'median_processing_time': statistics.median(self.processing_times),
            'p95_processing_time': self._percentile(self.processing_times, 95),
            'avg_confidence': statistics.mean(self.confidence_scores),
            'avg_memory_usage': statistics.mean(self.memory_usage),
            'error_rate': self.error_count / max(self.total_processed, 1),
            'throughput_per_minute': len(self.processing_times) / (max(self.processing_times) / 60) if self.processing_times else 0
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def should_alert(self) -> Dict[str, bool]:
        """Check if performance alerts should be triggered"""
        stats = self.get_current_stats()
        
        return {
            'high_processing_time': stats.get('avg_processing_time', 0) > 5.0,
            'low_confidence': stats.get('avg_confidence', 1.0) < 0.7,
            'high_memory_usage': stats.get('avg_memory_usage', 0) > 800,
            'high_error_rate': stats.get('error_rate', 0) > 0.1
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()
```

### Automated Performance Tuning

```python
class AutoTuner:
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.tuning_history = []
        self.current_config = PADDLEOCR_CONFIG.copy()
    
    def analyze_and_tune(self):
        """Analyze performance and adjust configuration"""
        stats = self.performance_monitor.get_current_stats()
        alerts = self.performance_monitor.should_alert()
        
        adjustments = {}
        
        # Tune based on performance issues
        if alerts['high_processing_time']:
            adjustments.update(self._tune_for_speed())
        
        if alerts['high_memory_usage']:
            adjustments.update(self._tune_for_memory())
        
        if alerts['low_confidence']:
            adjustments.update(self._tune_for_accuracy())
        
        if adjustments:
            self._apply_adjustments(adjustments)
            self.tuning_history.append({
                'timestamp': time.time(),
                'stats': stats,
                'adjustments': adjustments
            })
    
    def _tune_for_speed(self) -> Dict:
        """Optimize for processing speed"""
        return {
            'preprocessing.noise_reduction': False,
            'preprocessing.skew_correction': False,
            'drop_score': 0.6,
            'det_limit_side_len': 960
        }
    
    def _tune_for_memory(self) -> Dict:
        """Optimize for memory usage"""
        return {
            'performance.batch_size': 1,
            'performance.max_workers': 2,
            'rec_batch_num': 4
        }
    
    def _tune_for_accuracy(self) -> Dict:
        """Optimize for accuracy"""
        return {
            'preprocessing.noise_reduction': True,
            'preprocessing.contrast_enhancement': True,
            'drop_score': 0.3,
            'det_limit_side_len': 1280
        }
    
    def _apply_adjustments(self, adjustments: Dict):
        """Apply configuration adjustments"""
        for key, value in adjustments.items():
            keys = key.split('.')
            config_section = self.current_config
            
            for k in keys[:-1]:
                config_section = config_section[k]
            
            config_section[keys[-1]] = value
        
        # Restart OCR service with new config
        self._restart_ocr_service()
```

## Load Testing and Benchmarking

### Load Testing Script

```python
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
import statistics

class LoadTester:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.results = []
    
    async def test_concurrent_requests(self, num_requests=50, concurrency=10):
        """Test concurrent OCR requests"""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def make_request(session, request_id):
            async with semaphore:
                start_time = time.time()
                try:
                    # Simulate OCR request
                    with open('test_invoice.pdf', 'rb') as f:
                        data = aiohttp.FormData()
                        data.add_field('file', f, filename='test.pdf')
                        
                        async with session.post(
                            f'{self.base_url}/api/ocr/process/',
                            data=data
                        ) as response:
                            result = await response.json()
                            processing_time = time.time() - start_time
                            
                            self.results.append({
                                'request_id': request_id,
                                'status_code': response.status,
                                'processing_time': processing_time,
                                'confidence': result.get('confidence_score', 0),
                                'success': response.status == 200
                            })
                
                except Exception as e:
                    self.results.append({
                        'request_id': request_id,
                        'error': str(e),
                        'processing_time': time.time() - start_time,
                        'success': False
                    })
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                make_request(session, i) 
                for i in range(num_requests)
            ]
            await asyncio.gather(*tasks)
    
    def generate_report(self) -> Dict:
        """Generate load test report"""
        successful_results = [r for r in self.results if r['success']]
        processing_times = [r['processing_time'] for r in successful_results]
        confidences = [r['confidence'] for r in successful_results if 'confidence' in r]
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful_results),
            'success_rate': len(successful_results) / len(self.results),
            'avg_processing_time': statistics.mean(processing_times) if processing_times else 0,
            'median_processing_time': statistics.median(processing_times) if processing_times else 0,
            'p95_processing_time': self._percentile(processing_times, 95) if processing_times else 0,
            'avg_confidence': statistics.mean(confidences) if confidences else 0,
            'requests_per_second': len(successful_results) / max(processing_times) if processing_times else 0
        }

# Run load test
async def run_load_test():
    tester = LoadTester()
    await tester.test_concurrent_requests(num_requests=100, concurrency=20)
    report = tester.generate_report()
    print(f"Load test results: {report}")

# asyncio.run(run_load_test())
```

## Production Deployment Optimization

### Docker Optimization

```dockerfile
# Optimized Dockerfile for PaddleOCR
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for optimization
ENV OMP_NUM_THREADS=8
ENV MKL_NUM_THREADS=8
ENV PADDLEOCR_MODEL_DIR=/app/paddle_models
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download models during build
RUN python -c "import paddleocr; paddleocr.PaddleOCR(lang='pl')"

# Copy application
COPY . /app
WORKDIR /app

# Set resource limits
LABEL memory="2g"
LABEL cpu="2"

CMD ["gunicorn", "--config", "gunicorn.conf.py", "faktulove.wsgi:application"]
```

### Kubernetes Deployment

```yaml
# kubernetes/paddleocr-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: paddleocr-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: paddleocr-service
  template:
    metadata:
      labels:
        app: paddleocr-service
    spec:
      containers:
      - name: paddleocr
        image: faktulove/paddleocr:latest
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2"
        env:
        - name: PADDLEOCR_ENABLED
          value: "true"
        - name: PADDLEOCR_MAX_MEMORY
          value: "1024"
        - name: PADDLEOCR_MAX_WORKERS
          value: "3"
        volumeMounts:
        - name: model-cache
          mountPath: /app/paddle_models
        livenessProbe:
          httpGet:
            path: /health/paddleocr/
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/paddleocr/ready/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: paddleocr-models
```

### Monitoring and Alerting

```yaml
# prometheus/paddleocr-alerts.yaml
groups:
- name: paddleocr
  rules:
  - alert: PaddleOCRHighProcessingTime
    expr: avg(paddleocr_processing_time_seconds) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "PaddleOCR processing time is high"
      description: "Average processing time is {{ $value }} seconds"
  
  - alert: PaddleOCRHighMemoryUsage
    expr: paddleocr_memory_usage_mb > 800
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "PaddleOCR memory usage is high"
      description: "Memory usage is {{ $value }}MB"
  
  - alert: PaddleOCRLowAccuracy
    expr: avg(paddleocr_confidence_score) < 0.7
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "PaddleOCR accuracy is low"
      description: "Average confidence is {{ $value }}"
```

This comprehensive performance guide provides all the tools and strategies needed to optimize PaddleOCR for production use in the FaktuLove system.