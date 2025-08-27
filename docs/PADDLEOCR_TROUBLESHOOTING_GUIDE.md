# PaddleOCR Troubleshooting and Debugging Guide

## Overview

This guide provides comprehensive troubleshooting information for PaddleOCR integration in the FaktuLove system. It covers common issues, debugging techniques, error resolution, and maintenance procedures.

## Common Issues and Solutions

### 1. Installation and Setup Issues

#### Issue: PaddleOCR Installation Fails

**Symptoms:**
```bash
ERROR: Could not install packages due to an EnvironmentError
pip install paddleocr fails with dependency conflicts
```

**Solutions:**

1. **Clean Installation:**
```bash
# Remove existing installations
pip uninstall paddlepaddle paddleocr -y

# Clear pip cache
pip cache purge

# Install with specific versions
pip install paddlepaddle==2.5.2
pip install paddleocr==2.7.0.3
```

2. **System Dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1

# CentOS/RHEL
sudo yum install -y mesa-libGL glib2 libSM libXext libXrender libgomp
```

3. **Virtual Environment:**
```bash
# Create clean environment
python -m venv paddleocr_env
source paddleocr_env/bin/activate
pip install --upgrade pip
pip install paddleocr
```

#### Issue: Polish Language Models Not Found

**Symptoms:**
```python
PaddleOCRModelError: Polish language models not available
FileNotFoundError: Model files not found in ~/.paddleocr/
```

**Solutions:**

1. **Manual Model Download:**
```python
import paddleocr
import os

# Force download Polish models
ocr = paddleocr.PaddleOCR(lang='pl', show_log=True)
print("Models downloaded to:", ocr.text_recognizer.character_dict_path)
```

2. **Check Model Directory:**
```bash
# Check if models exist
ls -la ~/.paddleocr/whl/
ls -la ~/.paddleocr/whl/det/
ls -la ~/.paddleocr/whl/rec/

# Set custom model directory
export PADDLEOCR_MODEL_DIR=/app/paddle_models
mkdir -p $PADDLEOCR_MODEL_DIR
```

3. **Download Specific Models:**
```python
from paddleocr import PaddleOCR

# Download with specific configuration
ocr = PaddleOCR(
    lang='pl',
    det_model_dir='/app/paddle_models/det',
    rec_model_dir='/app/paddle_models/rec',
    cls_model_dir='/app/paddle_models/cls',
    show_log=True
)
```

### 2. Runtime Errors

#### Issue: Memory Errors During Processing

**Symptoms:**
```python
MemoryError: Cannot allocate memory for tensor
RuntimeError: CUDA out of memory
Process killed (OOM)
```

**Solutions:**

1. **Reduce Memory Usage:**
```python
# Optimize configuration for low memory
PADDLEOCR_CONFIG = {
    'use_gpu': False,  # Use CPU to save GPU memory
    'rec_batch_num': 1,  # Reduce batch size
    'det_limit_side_len': 960,  # Reduce image resolution
    'max_text_length': 10000,  # Reduce text buffer
    'performance': {
        'max_memory_mb': 512,
        'batch_size': 1,
        'max_workers': 1
    }
}
```

2. **Image Preprocessing:**
```python
from PIL import Image
import numpy as np

def reduce_image_size(image_path, max_size=1920):
    """Reduce image size to save memory"""
    with Image.open(image_path) as img:
        # Calculate new size maintaining aspect ratio
        width, height = img.size
        if max(width, height) > max_size:
            ratio = max_size / max(width, height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return np.array(img)
```

3. **Memory Monitoring:**
```python
import psutil
import gc

class MemoryManager:
    def __init__(self, max_memory_mb=800):
        self.max_memory_mb = max_memory_mb
    
    def check_memory(self):
        memory_usage = psutil.virtual_memory().used / 1024 / 1024
        if memory_usage > self.max_memory_mb:
            gc.collect()  # Force garbage collection
            return False
        return True
    
    def cleanup_if_needed(self):
        if not self.check_memory():
            # Force cleanup
            gc.collect()
            # Restart OCR service if needed
            return True
        return False
```

#### Issue: Processing Timeouts

**Symptoms:**
```python
TimeoutError: OCR processing exceeded maximum time limit
ConnectionTimeout: Request timed out after 30 seconds
```

**Solutions:**

1. **Increase Timeout Settings:**
```python
PADDLEOCR_CONFIG['performance']['timeout_seconds'] = 60

# For Django views
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import signal

class TimeoutHandler:
    def __init__(self, timeout_seconds=30):
        self.timeout_seconds = timeout_seconds
    
    def timeout_handler(self, signum, frame):
        raise TimeoutError(f"Processing exceeded {self.timeout_seconds} seconds")
    
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.timeout_seconds)
        return self
    
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

# Usage
try:
    with TimeoutHandler(60):
        result = ocr_service.process_invoice(file_content, mime_type)
except TimeoutError:
    # Fallback to faster OCR engine
    result = fallback_ocr_service.process_invoice(file_content, mime_type)
```

2. **Optimize Processing Speed:**
```python
# Fast processing configuration
FAST_CONFIG = {
    'preprocessing': {
        'enabled': False  # Disable preprocessing for speed
    },
    'drop_score': 0.7,  # Higher threshold for speed
    'det_limit_side_len': 640,  # Lower resolution
    'rec_batch_num': 1  # Smaller batches
}
```

#### Issue: Low Accuracy on Polish Text

**Symptoms:**
```python
# Poor recognition results
extracted_data = {
    'numer_faktury': 'FV/O01/2O24',  # Should be FV/001/2024
    'sprzedawca_nip': '12345678qO',   # Should be 1234567890
}
confidence_score = 0.45  # Low confidence
```

**Solutions:**

1. **Improve Image Quality:**
```python
import cv2
import numpy as np

class ImageEnhancer:
    def enhance_for_ocr(self, image):
        """Enhance image for better OCR accuracy"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
```

2. **Polish-Specific Configuration:**
```python
POLISH_OPTIMIZED_CONFIG = {
    'lang': 'pl',  # Polish only
    'drop_score': 0.3,  # Lower threshold for Polish
    'use_space_char': True,
    'use_angle_cls': True,
    'det_limit_side_len': 1280,  # Higher resolution
    'rec_batch_num': 6,
    'max_text_length': 25000
}
```

3. **Post-processing Validation:**
```python
import re

class PolishTextValidator:
    def __init__(self):
        self.nip_pattern = re.compile(r'\b\d{10}\b')
        self.date_pattern = re.compile(r'\b\d{2}[.-]\d{2}[.-]\d{4}\b')
        self.amount_pattern = re.compile(r'\b\d+[,.]?\d*\b')
    
    def validate_and_correct(self, text, field_type):
        """Validate and correct common OCR errors"""
        if field_type == 'nip':
            # Common OCR errors: O->0, l->1, S->5
            corrected = text.replace('O', '0').replace('l', '1').replace('S', '5')
            match = self.nip_pattern.search(corrected)
            return match.group() if match else text
        
        elif field_type == 'date':
            # Fix common date errors
            corrected = text.replace('O', '0').replace('l', '1')
            match = self.date_pattern.search(corrected)
            return match.group() if match else text
        
        return text
```

### 3. Performance Issues

#### Issue: Slow Processing Speed

**Symptoms:**
```python
# Processing takes >10 seconds per document
processing_time = 15.3  # Too slow
```

**Solutions:**

1. **Enable GPU Acceleration:**
```python
# Check GPU availability
import paddle
if paddle.is_compiled_with_cuda():
    PADDLEOCR_CONFIG['use_gpu'] = True
    PADDLEOCR_CONFIG['gpu_mem'] = 2000
```

2. **Optimize Image Resolution:**
```python
def optimize_image_resolution(image, target_dpi=150):
    """Optimize image resolution for speed vs quality"""
    height, width = image.shape[:2]
    
    # Calculate optimal size
    max_dimension = 1920 if target_dpi >= 200 else 1280
    
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(image, (new_width, new_height), 
                         interpolation=cv2.INTER_LANCZOS4)
    
    return image
```

3. **Parallel Processing:**
```python
from concurrent.futures import ThreadPoolExecutor
import queue

class ParallelProcessor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.result_queue = queue.Queue()
    
    def process_batch(self, documents):
        """Process multiple documents in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for doc in documents:
                future = executor.submit(self._process_single, doc)
                futures.append(future)
            
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    results.append({'error': str(e)})
            
            return results
```

#### Issue: High Memory Usage

**Symptoms:**
```bash
# Memory usage keeps increasing
Memory usage: 1.2GB and growing
Docker container killed (OOMKilled)
```

**Solutions:**

1. **Memory Leak Detection:**
```python
import tracemalloc
import gc

class MemoryProfiler:
    def __init__(self):
        tracemalloc.start()
        self.snapshots = []
    
    def take_snapshot(self, label):
        """Take memory snapshot"""
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append((label, snapshot))
        
        if len(self.snapshots) > 1:
            self._compare_snapshots()
    
    def _compare_snapshots(self):
        """Compare memory usage between snapshots"""
        current_label, current = self.snapshots[-1]
        previous_label, previous = self.snapshots[-2]
        
        top_stats = current.compare_to(previous, 'lineno')
        
        print(f"Memory comparison: {previous_label} -> {current_label}")
        for stat in top_stats[:10]:
            print(stat)
    
    def force_cleanup(self):
        """Force memory cleanup"""
        gc.collect()
        # Clear PaddleOCR model cache if needed
        import paddle
        if hasattr(paddle, 'device') and hasattr(paddle.device, 'cuda'):
            paddle.device.cuda.empty_cache()
```

2. **Resource Management:**
```python
class ResourceManager:
    def __init__(self, max_memory_mb=800):
        self.max_memory_mb = max_memory_mb
        self.ocr_instances = {}
    
    def get_ocr_instance(self, config_key):
        """Get or create OCR instance with resource management"""
        if config_key not in self.ocr_instances:
            # Check memory before creating new instance
            if self._check_memory_usage():
                self.ocr_instances[config_key] = PaddleOCR(**config)
            else:
                # Cleanup and retry
                self._cleanup_instances()
                self.ocr_instances[config_key] = PaddleOCR(**config)
        
        return self.ocr_instances[config_key]
    
    def _cleanup_instances(self):
        """Cleanup OCR instances to free memory"""
        for key in list(self.ocr_instances.keys()):
            del self.ocr_instances[key]
        gc.collect()
```

### 4. Integration Issues

#### Issue: Django Integration Problems

**Symptoms:**
```python
ImportError: cannot import name 'PaddleOCRService'
AttributeError: 'PaddleOCRService' object has no attribute 'process_invoice'
```

**Solutions:**

1. **Check Service Registration:**
```python
# In faktury/services/ocr_service_factory.py
from faktury.services.paddle_ocr_service import PaddleOCRService

class OCRServiceFactory:
    _services = {
        'paddleocr': PaddleOCRService,
        'tesseract': TesseractOCRService,
        'easyocr': EasyOCRService,
    }
    
    @classmethod
    def get_service(cls, engine_type='paddleocr'):
        if engine_type not in cls._services:
            raise ValueError(f"Unknown OCR engine: {engine_type}")
        
        return cls._services[engine_type]()
```

2. **Verify Settings Configuration:**
```python
# In settings.py
from django.core.exceptions import ImproperlyConfigured

def validate_paddleocr_config():
    """Validate PaddleOCR configuration"""
    required_settings = ['PADDLEOCR_CONFIG', 'OCR_ENGINE_PRIORITY']
    
    for setting in required_settings:
        if not hasattr(settings, setting):
            raise ImproperlyConfigured(f"Missing required setting: {setting}")
    
    # Check if PaddleOCR is available
    try:
        import paddleocr
    except ImportError:
        raise ImproperlyConfigured("PaddleOCR not installed")

# Call during Django startup
validate_paddleocr_config()
```

#### Issue: Celery Task Failures

**Symptoms:**
```python
# Celery worker errors
celery.exceptions.WorkerLostError: Worker exited prematurely
MemoryError in Celery task
```

**Solutions:**

1. **Celery Configuration:**
```python
# In celery.py
from celery import Celery
import os

app = Celery('faktulove')

# Configure for OCR tasks
app.conf.update(
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes hard limit
    worker_max_memory_per_child=800000,  # 800MB per worker
    worker_disable_rate_limits=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# OCR-specific queue
app.conf.task_routes = {
    'faktury.tasks.process_document_ocr_task': {'queue': 'ocr_queue'},
}
```

2. **Task Implementation:**
```python
from celery import shared_task
from celery.exceptions import Retry
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_document_ocr_task(self, document_id, file_content, mime_type):
    """Process document with OCR using PaddleOCR"""
    try:
        from faktury.services.paddle_ocr_service import PaddleOCRService
        
        # Initialize service with memory limits
        ocr_service = PaddleOCRService()
        
        # Process document
        result = ocr_service.process_invoice(file_content, mime_type)
        
        # Save result to database
        from faktury.models import OCRResult
        OCRResult.objects.create(
            document_id=document_id,
            extracted_data=result['extracted_data'],
            confidence_score=result['confidence_score'],
            processor_version='paddleocr-v2.7'
        )
        
        return result
        
    except MemoryError as e:
        logger.error(f"Memory error in OCR task: {e}")
        # Retry with reduced settings
        if self.request.retries < 2:
            raise self.retry(countdown=60, exc=e)
        else:
            # Fallback to different OCR engine
            return self._fallback_processing(document_id, file_content, mime_type)
    
    except Exception as e:
        logger.error(f"OCR task failed: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=e)
        raise
```

### 5. Debugging Techniques

#### Enable Debug Logging

```python
import logging

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)

# PaddleOCR specific logging
paddle_logger = logging.getLogger('paddleocr')
paddle_logger.setLevel(logging.DEBUG)

# Service logging
service_logger = logging.getLogger('faktury.services.paddle_ocr_service')
service_logger.setLevel(logging.DEBUG)

# Add file handler
handler = logging.FileHandler('paddleocr_debug.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

paddle_logger.addHandler(handler)
service_logger.addHandler(handler)
```

#### Debug OCR Results

```python
class OCRDebugger:
    def __init__(self):
        self.debug_enabled = True
    
    def debug_ocr_result(self, image, ocr_result, save_debug=True):
        """Debug OCR results with visual output"""
        if not self.debug_enabled:
            return
        
        import cv2
        import numpy as np
        
        # Create debug image with bounding boxes
        debug_image = image.copy()
        
        for line in ocr_result:
            # Extract bounding box and text
            bbox = line[0]
            text = line[1][0]
            confidence = line[1][1]
            
            # Draw bounding box
            points = np.array(bbox, dtype=np.int32)
            cv2.polylines(debug_image, [points], True, (0, 255, 0), 2)
            
            # Add text and confidence
            cv2.putText(debug_image, f"{text} ({confidence:.2f})", 
                       (int(bbox[0][0]), int(bbox[0][1]) - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        if save_debug:
            cv2.imwrite('debug_ocr_result.jpg', debug_image)
        
        return debug_image
    
    def analyze_confidence_distribution(self, ocr_result):
        """Analyze confidence score distribution"""
        confidences = [line[1][1] for line in ocr_result]
        
        analysis = {
            'total_detections': len(confidences),
            'avg_confidence': sum(confidences) / len(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'low_confidence_count': len([c for c in confidences if c < 0.5]),
            'high_confidence_count': len([c for c in confidences if c > 0.8])
        }
        
        print("Confidence Analysis:")
        for key, value in analysis.items():
            print(f"  {key}: {value}")
        
        return analysis
```

#### Performance Profiling

```python
import cProfile
import pstats
from functools import wraps

def profile_ocr_function(func):
    """Decorator to profile OCR functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
            
            # Save profile results
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # Top 20 functions
            
            # Save to file
            stats.dump_stats(f'profile_{func.__name__}.prof')
        
        return result
    return wrapper

# Usage
@profile_ocr_function
def process_invoice_with_profiling(file_content, mime_type):
    ocr_service = PaddleOCRService()
    return ocr_service.process_invoice(file_content, mime_type)
```

### 6. Health Checks and Monitoring

#### Health Check Implementation

```python
from django.http import JsonResponse
from django.views import View
import time

class PaddleOCRHealthCheck(View):
    def get(self, request):
        """Health check endpoint for PaddleOCR service"""
        health_status = {
            'service': 'paddleocr',
            'status': 'unknown',
            'timestamp': time.time(),
            'checks': {}
        }
        
        try:
            # Check if PaddleOCR can be imported
            import paddleocr
            health_status['checks']['import'] = 'ok'
            
            # Check if models are available
            try:
                ocr = paddleocr.PaddleOCR(lang='pl', show_log=False)
                health_status['checks']['models'] = 'ok'
            except Exception as e:
                health_status['checks']['models'] = f'error: {str(e)}'
            
            # Check memory usage
            import psutil
            memory_usage = psutil.virtual_memory().used / 1024 / 1024
            health_status['checks']['memory_mb'] = memory_usage
            
            if memory_usage > 1000:
                health_status['checks']['memory_status'] = 'warning'
            else:
                health_status['checks']['memory_status'] = 'ok'
            
            # Overall status
            if all(check in ['ok', memory_usage] for check in health_status['checks'].values()):
                health_status['status'] = 'healthy'
            else:
                health_status['status'] = 'unhealthy'
                
        except Exception as e:
            health_status['status'] = 'error'
            health_status['error'] = str(e)
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return JsonResponse(health_status, status=status_code)
```

#### Monitoring Metrics

```python
import time
from collections import defaultdict, deque

class OCRMetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.recent_metrics = defaultdict(lambda: deque(maxlen=100))
    
    def record_processing_time(self, processing_time):
        """Record processing time metric"""
        self.metrics['processing_times'].append(processing_time)
        self.recent_metrics['processing_times'].append(processing_time)
    
    def record_confidence_score(self, confidence):
        """Record confidence score metric"""
        self.metrics['confidence_scores'].append(confidence)
        self.recent_metrics['confidence_scores'].append(confidence)
    
    def record_error(self, error_type):
        """Record error occurrence"""
        self.metrics['errors'].append({
            'type': error_type,
            'timestamp': time.time()
        })
    
    def get_current_stats(self):
        """Get current performance statistics"""
        recent_times = list(self.recent_metrics['processing_times'])
        recent_confidences = list(self.recent_metrics['confidence_scores'])
        
        if not recent_times:
            return {}
        
        return {
            'avg_processing_time': sum(recent_times) / len(recent_times),
            'max_processing_time': max(recent_times),
            'min_processing_time': min(recent_times),
            'avg_confidence': sum(recent_confidences) / len(recent_confidences) if recent_confidences else 0,
            'total_processed': len(recent_times),
            'error_count': len([e for e in self.metrics['errors'] 
                              if time.time() - e['timestamp'] < 3600])  # Last hour
        }

# Global metrics collector
metrics_collector = OCRMetricsCollector()
```

This comprehensive troubleshooting guide should help resolve most issues encountered with PaddleOCR integration in the FaktuLove system.