"""
PaddleOCR Resource Manager

This module provides resource management for PaddleOCR operations, including
concurrent request handling, memory management, and processing optimization.
"""

import logging
import time
import threading
import queue
from typing import Dict, Any, Optional, List, Callable, NamedTuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from contextlib import contextmanager
import weakref

logger = logging.getLogger(__name__)


@dataclass
class ProcessingRequest:
    """Represents a processing request with metadata"""
    request_id: str
    operation_type: str
    priority: int = 0
    created_at: datetime = None
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class ProcessingResult(NamedTuple):
    """Result of a processing operation"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    processing_time: float = 0.0
    memory_used_mb: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class ResourcePool:
    """Resource pool configuration"""
    max_workers: int = 3
    max_memory_mb: float = 800.0
    max_queue_size: int = 10
    worker_timeout: float = 30.0
    cleanup_interval: float = 60.0


class WorkerThread:
    """Individual worker thread for processing OCR requests"""
    
    def __init__(self, worker_id: str, resource_manager: 'PaddleOCRResourceManager'):
        self.worker_id = worker_id
        self.resource_manager = resource_manager
        self.is_active = False
        self.current_request: Optional[ProcessingRequest] = None
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.last_activity = datetime.now()
        
    def start(self):
        """Start the worker thread"""
        if self.thread and self.thread.is_alive():
            return
        
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._worker_loop, name=f"PaddleOCR-Worker-{self.worker_id}")
        self.thread.daemon = True
        self.thread.start()
        logger.debug(f"Worker {self.worker_id} started")
    
    def stop(self):
        """Stop the worker thread"""
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)
        logger.debug(f"Worker {self.worker_id} stopped")
    
    def _worker_loop(self):
        """Main worker loop"""
        while not self.stop_event.is_set():
            try:
                # Get next request from queue
                try:
                    request = self.resource_manager._get_next_request(timeout=1.0)
                    if request is None:
                        continue
                except Exception as e:
                    logger.debug(f"Worker {self.worker_id} queue timeout: {e}")
                    continue
                
                self.current_request = request
                self.is_active = True
                self.last_activity = datetime.now()
                
                # Process the request
                result = self._process_request(request)
                
                # Return result
                self.resource_manager._complete_request(request.request_id, result)
                
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")
                if self.current_request:
                    error_result = ProcessingResult(
                        success=False,
                        error=e,
                        metadata={'worker_id': self.worker_id}
                    )
                    self.resource_manager._complete_request(
                        self.current_request.request_id, error_result
                    )
            finally:
                self.current_request = None
                self.is_active = False
    
    def _process_request(self, request: ProcessingRequest) -> ProcessingResult:
        """Process a single request"""
        start_time = time.time()
        start_memory = self.resource_manager.performance_monitor.get_current_memory_mb()
        
        try:
            # Get the processing function
            processor = self.resource_manager._get_processor(request.operation_type)
            if not processor:
                raise ValueError(f"No processor found for operation: {request.operation_type}")
            
            # Execute with timeout if specified
            if request.timeout:
                result = self._execute_with_timeout(processor, request)
            else:
                result = processor(request)
            
            processing_time = time.time() - start_time
            end_memory = self.resource_manager.performance_monitor.get_current_memory_mb()
            
            return ProcessingResult(
                success=True,
                result=result,
                processing_time=processing_time,
                memory_used_mb=end_memory - start_memory,
                metadata={
                    'worker_id': self.worker_id,
                    'operation_type': request.operation_type
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            end_memory = self.resource_manager.performance_monitor.get_current_memory_mb()
            
            return ProcessingResult(
                success=False,
                error=e,
                processing_time=processing_time,
                memory_used_mb=end_memory - start_memory,
                metadata={
                    'worker_id': self.worker_id,
                    'operation_type': request.operation_type
                }
            )
    
    def _execute_with_timeout(self, processor: Callable, request: ProcessingRequest) -> Any:
        """Execute processor with timeout"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Processing timeout after {request.timeout}s")
        
        # Set up timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(request.timeout))
        
        try:
            return processor(request)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


class PaddleOCRResourceManager:
    """
    Resource manager for PaddleOCR operations
    
    Manages concurrent processing, resource allocation, and optimization
    for PaddleOCR operations with configurable resource limits and
    intelligent request scheduling.
    """
    
    def __init__(self, 
                 resource_pool: Optional[ResourcePool] = None,
                 performance_monitor: Optional['PaddleOCRPerformanceMonitor'] = None):
        """
        Initialize resource manager
        
        Args:
            resource_pool: Resource pool configuration
            performance_monitor: Performance monitor instance
        """
        self.resource_pool = resource_pool or ResourcePool()
        self.performance_monitor = performance_monitor
        
        # Request management
        self.request_queue = queue.PriorityQueue(maxsize=self.resource_pool.max_queue_size)
        self.pending_requests: Dict[str, Future] = {}
        self.completed_requests: Dict[str, ProcessingResult] = {}
        self.request_counter = 0
        self.lock = threading.RLock()
        
        # Worker management
        self.workers: Dict[str, WorkerThread] = {}
        self.active_workers = 0
        self.max_workers = self.resource_pool.max_workers
        
        # Processing functions registry
        self.processors: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'completed_requests': 0,
            'failed_requests': 0,
            'queue_full_rejections': 0,
            'timeout_errors': 0,
            'memory_limit_rejections': 0
        }
        
        # Start initial workers
        self._start_workers()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        logger.info(f"PaddleOCR Resource Manager initialized with {self.max_workers} workers")
    
    def register_processor(self, operation_type: str, processor: Callable):
        """Register a processor function for an operation type"""
        self.processors[operation_type] = processor
        logger.debug(f"Registered processor for operation: {operation_type}")
    
    def submit_request(self, 
                      operation_type: str,
                      processor_args: Dict[str, Any],
                      priority: int = 0,
                      timeout: Optional[float] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit a processing request
        
        Args:
            operation_type: Type of operation to perform
            processor_args: Arguments for the processor function
            priority: Request priority (lower numbers = higher priority)
            timeout: Processing timeout in seconds
            metadata: Additional metadata
            
        Returns:
            Request ID for tracking
        """
        with self.lock:
            # Check memory limits
            if self.performance_monitor:
                memory_status = self.performance_monitor.check_memory_limits()
                if memory_status['status'] == 'critical':
                    self.stats['memory_limit_rejections'] += 1
                    raise RuntimeError(f"Memory limit exceeded: {memory_status['current_memory_mb']:.1f}MB")
            
            # Generate request ID
            self.request_counter += 1
            request_id = f"req_{self.request_counter}_{int(time.time())}"
            
            # Create request
            request = ProcessingRequest(
                request_id=request_id,
                operation_type=operation_type,
                priority=priority,
                timeout=timeout or self.resource_pool.worker_timeout,
                metadata={
                    'processor_args': processor_args,
                    **(metadata or {})
                }
            )
            
            # Try to add to queue
            try:
                # Use negative priority for priority queue (lower number = higher priority)
                self.request_queue.put((-priority, request), block=False)
                
                # Create future for result tracking
                future = Future()
                self.pending_requests[request_id] = future
                
                self.stats['total_requests'] += 1
                
                logger.debug(f"Request {request_id} submitted for {operation_type}")
                return request_id
                
            except queue.Full:
                self.stats['queue_full_rejections'] += 1
                raise RuntimeError(f"Request queue is full (max: {self.resource_pool.max_queue_size})")
    
    def get_result(self, request_id: str, timeout: Optional[float] = None) -> ProcessingResult:
        """
        Get result for a request
        
        Args:
            request_id: Request ID
            timeout: Timeout for waiting for result
            
        Returns:
            Processing result
        """
        # Check if already completed
        if request_id in self.completed_requests:
            return self.completed_requests.pop(request_id)
        
        # Wait for completion
        future = self.pending_requests.get(request_id)
        if not future:
            raise ValueError(f"Request {request_id} not found")
        
        try:
            result = future.result(timeout=timeout)
            return result
        except Exception as e:
            logger.error(f"Error getting result for request {request_id}: {e}")
            return ProcessingResult(
                success=False,
                error=e,
                metadata={'request_id': request_id}
            )
    
    def cancel_request(self, request_id: str) -> bool:
        """Cancel a pending request"""
        future = self.pending_requests.get(request_id)
        if future:
            cancelled = future.cancel()
            if cancelled:
                self.pending_requests.pop(request_id, None)
                logger.debug(f"Request {request_id} cancelled")
            return cancelled
        return False
    
    def _get_next_request(self, timeout: float = 1.0) -> Optional[ProcessingRequest]:
        """Get next request from queue"""
        try:
            priority, request = self.request_queue.get(timeout=timeout)
            return request
        except queue.Empty:
            return None
    
    def _complete_request(self, request_id: str, result: ProcessingResult):
        """Complete a request with result"""
        future = self.pending_requests.pop(request_id, None)
        if future:
            future.set_result(result)
            
            # Update statistics
            if result.success:
                self.stats['completed_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
                if isinstance(result.error, TimeoutError):
                    self.stats['timeout_errors'] += 1
            
            logger.debug(f"Request {request_id} completed: success={result.success}")
        else:
            # Store result for later retrieval
            self.completed_requests[request_id] = result
    
    def _get_processor(self, operation_type: str) -> Optional[Callable]:
        """Get processor function for operation type"""
        return self.processors.get(operation_type)
    
    def _start_workers(self):
        """Start worker threads"""
        for i in range(self.max_workers):
            worker_id = f"worker_{i}"
            worker = WorkerThread(worker_id, self)
            self.workers[worker_id] = worker
            worker.start()
            self.active_workers += 1
    
    def _stop_workers(self):
        """Stop all worker threads"""
        for worker in self.workers.values():
            worker.stop()
        self.workers.clear()
        self.active_workers = 0
    
    def _cleanup_loop(self):
        """Cleanup loop for removing old completed requests"""
        while True:
            try:
                time.sleep(self.resource_pool.cleanup_interval)
                
                # Clean up old completed requests
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(minutes=10)  # Keep for 10 minutes
                
                old_requests = [
                    req_id for req_id, result in self.completed_requests.items()
                    if hasattr(result, 'completed_at') and result.completed_at < cutoff_time
                ]
                
                for req_id in old_requests:
                    self.completed_requests.pop(req_id, None)
                
                if old_requests:
                    logger.debug(f"Cleaned up {len(old_requests)} old completed requests")
                
                # Check worker health
                self._check_worker_health()
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def _check_worker_health(self):
        """Check worker thread health and restart if needed"""
        current_time = datetime.now()
        
        for worker_id, worker in list(self.workers.items()):
            # Check if worker thread is alive
            if not worker.thread or not worker.thread.is_alive():
                logger.warning(f"Worker {worker_id} thread died, restarting")
                worker.stop()
                new_worker = WorkerThread(worker_id, self)
                self.workers[worker_id] = new_worker
                new_worker.start()
            
            # Check for stuck workers
            elif worker.is_active and worker.current_request:
                time_since_activity = current_time - worker.last_activity
                if time_since_activity.total_seconds() > self.resource_pool.worker_timeout * 2:
                    logger.warning(f"Worker {worker_id} appears stuck, restarting")
                    worker.stop()
                    new_worker = WorkerThread(worker_id, self)
                    self.workers[worker_id] = new_worker
                    new_worker.start()
    
    def scale_workers(self, new_worker_count: int):
        """Dynamically scale the number of workers"""
        if new_worker_count < 1 or new_worker_count > 10:
            raise ValueError("Worker count must be between 1 and 10")
        
        current_count = len(self.workers)
        
        if new_worker_count > current_count:
            # Add workers
            for i in range(current_count, new_worker_count):
                worker_id = f"worker_{i}"
                worker = WorkerThread(worker_id, self)
                self.workers[worker_id] = worker
                worker.start()
                self.active_workers += 1
            
            logger.info(f"Scaled up to {new_worker_count} workers")
            
        elif new_worker_count < current_count:
            # Remove workers
            workers_to_remove = list(self.workers.keys())[new_worker_count:]
            for worker_id in workers_to_remove:
                worker = self.workers.pop(worker_id)
                worker.stop()
                self.active_workers -= 1
            
            logger.info(f"Scaled down to {new_worker_count} workers")
        
        self.max_workers = new_worker_count
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            'queue_size': self.request_queue.qsize(),
            'max_queue_size': self.resource_pool.max_queue_size,
            'pending_requests': len(self.pending_requests),
            'completed_requests': len(self.completed_requests),
            'active_workers': self.active_workers,
            'max_workers': self.max_workers,
            'worker_status': {
                worker_id: {
                    'is_active': worker.is_active,
                    'current_request': worker.current_request.request_id if worker.current_request else None,
                    'last_activity': worker.last_activity.isoformat()
                }
                for worker_id, worker in self.workers.items()
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get resource manager statistics"""
        queue_status = self.get_queue_status()
        
        return {
            **self.stats,
            'queue_status': queue_status,
            'resource_limits': {
                'max_workers': self.resource_pool.max_workers,
                'max_memory_mb': self.resource_pool.max_memory_mb,
                'max_queue_size': self.resource_pool.max_queue_size,
                'worker_timeout': self.resource_pool.worker_timeout
            },
            'registered_processors': list(self.processors.keys())
        }
    
    def shutdown(self):
        """Shutdown the resource manager"""
        logger.info("Shutting down PaddleOCR Resource Manager")
        
        # Stop accepting new requests
        self.request_queue = None
        
        # Cancel pending requests
        for request_id, future in self.pending_requests.items():
            future.cancel()
        
        # Stop workers
        self._stop_workers()
        
        logger.info("PaddleOCR Resource Manager shutdown complete")
    
    @contextmanager
    def managed_processing(self, operation_type: str, **processor_args):
        """Context manager for managed processing"""
        request_id = None
        try:
            request_id = self.submit_request(operation_type, processor_args)
            yield request_id
        except Exception as e:
            if request_id:
                self.cancel_request(request_id)
            raise