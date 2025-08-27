"""
Parallel OCR Processor

This module provides parallel processing capabilities for OCR operations,
optimizing throughput for multiple documents and different document formats.
"""

import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, Future
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import multiprocessing
import queue
import psutil
from functools import partial

from .ocr_performance_profiler import ocr_profiler

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing modes for parallel execution"""
    THREAD_POOL = "thread_pool"
    PROCESS_POOL = "process_pool"
    ASYNC_IO = "async_io"
    HYBRID = "hybrid"


class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class ProcessingTask:
    """Individual processing task"""
    task_id: str
    file_content: bytes
    mime_type: str
    priority: Priority = Priority.NORMAL
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_timestamp: float = field(default_factory=time.time)
    started_timestamp: Optional[float] = None
    completed_timestamp: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ProcessingStats:
    """Processing statistics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_processing_time: float = 0.0
    throughput_per_minute: float = 0.0
    active_workers: int = 0
    queue_size: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0


class TaskQueue:
    """Priority-based task queue for OCR processing"""
    
    def __init__(self, maxsize: int = 1000):
        """Initialize task queue with priority support"""
        self.maxsize = maxsize
        self._queues = {
            Priority.URGENT: queue.Queue(),
            Priority.HIGH: queue.Queue(),
            Priority.NORMAL: queue.Queue(),
            Priority.LOW: queue.Queue()
        }
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)
        self._size = 0
    
    def put(self, task: ProcessingTask, block: bool = True, timeout: Optional[float] = None):
        """Add task to queue with priority"""
        with self._not_full:
            if self._size >= self.maxsize:
                if not block:
                    raise queue.Full
                elif timeout is None:
                    while self._size >= self.maxsize:
                        self._not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time.time() + timeout
                    while self._size >= self.maxsize:
                        remaining = endtime - time.time()
                        if remaining <= 0.0:
                            raise queue.Full
                        self._not_full.wait(remaining)
            
            self._queues[task.priority].put(task)
            self._size += 1
            self._not_empty.notify()
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> ProcessingTask:
        """Get highest priority task from queue"""
        with self._not_empty:
            if self._size == 0:
                if not block:
                    raise queue.Empty
                elif timeout is None:
                    while self._size == 0:
                        self._not_empty.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time.time() + timeout
                    while self._size == 0:
                        remaining = endtime - time.time()
                        if remaining <= 0.0:
                            raise queue.Empty
                        self._not_empty.wait(remaining)
            
            # Get task from highest priority queue that has tasks
            for priority in [Priority.URGENT, Priority.HIGH, Priority.NORMAL, Priority.LOW]:
                if not self._queues[priority].empty():
                    task = self._queues[priority].get()
                    self._size -= 1
                    self._not_full.notify()
                    return task
            
            raise queue.Empty
    
    def qsize(self) -> int:
        """Return approximate queue size"""
        return self._size
    
    def empty(self) -> bool:
        """Return True if queue is empty"""
        return self._size == 0
    
    def full(self) -> bool:
        """Return True if queue is full"""
        return self._size >= self.maxsize


class ParallelOCRProcessor:
    """
    Parallel OCR processor with intelligent load balancing and resource management
    
    Features:
    - Multiple processing modes (threads, processes, async)
    - Priority-based task queue
    - Dynamic worker scaling
    - Resource monitoring and optimization
    - Fault tolerance and error handling
    """
    
    def __init__(self,
                 max_workers: Optional[int] = None,
                 processing_mode: ProcessingMode = ProcessingMode.HYBRID,
                 queue_maxsize: int = 1000,
                 enable_monitoring: bool = True,
                 memory_limit_mb: float = 2048.0,
                 cpu_limit_percent: float = 80.0):
        """
        Initialize parallel OCR processor
        
        Args:
            max_workers: Maximum number of workers (auto-detect if None)
            processing_mode: Processing mode to use
            queue_maxsize: Maximum queue size
            enable_monitoring: Enable resource monitoring
            memory_limit_mb: Memory usage limit in MB
            cpu_limit_percent: CPU usage limit percentage
        """
        self.processing_mode = processing_mode
        self.enable_monitoring = enable_monitoring
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit_percent = cpu_limit_percent
        
        # Auto-detect optimal worker count
        if max_workers is None:
            cpu_count = multiprocessing.cpu_count()
            if processing_mode == ProcessingMode.THREAD_POOL:
                self.max_workers = min(cpu_count * 2, 16)  # I/O bound
            elif processing_mode == ProcessingMode.PROCESS_POOL:
                self.max_workers = cpu_count  # CPU bound
            else:
                self.max_workers = min(cpu_count * 2, 12)  # Hybrid
        else:
            self.max_workers = max_workers
        
        # Initialize components
        self.task_queue = TaskQueue(maxsize=queue_maxsize)
        self.active_tasks: Dict[str, ProcessingTask] = {}
        self.completed_tasks: Dict[str, ProcessingTask] = {}
        self.stats = ProcessingStats()
        
        # Worker management
        self.workers: List[Union[ThreadPoolExecutor, ProcessPoolExecutor]] = []
        self.worker_futures: Dict[str, Future] = {}
        self.shutdown_event = threading.Event()
        
        # Monitoring
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_stats_update = time.time()
        
        # Thread safety
        self._lock = threading.Lock()
        
        logger.info(f"Parallel OCR Processor initialized with {self.max_workers} workers "
                   f"in {processing_mode.value} mode")
    
    def start(self):
        """Start the parallel processor"""
        try:
            logger.info("Starting parallel OCR processor")
            
            # Initialize workers based on processing mode
            if self.processing_mode == ProcessingMode.THREAD_POOL:
                self._start_thread_workers()
            elif self.processing_mode == ProcessingMode.PROCESS_POOL:
                self._start_process_workers()
            elif self.processing_mode == ProcessingMode.HYBRID:
                self._start_hybrid_workers()
            
            # Start monitoring if enabled
            if self.enable_monitoring:
                self.monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
                self.monitor_thread.start()
            
            logger.info("Parallel OCR processor started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start parallel processor: {e}")
            raise
    
    def stop(self, timeout: float = 30.0):
        """Stop the parallel processor"""
        try:
            logger.info("Stopping parallel OCR processor")
            
            # Signal shutdown
            self.shutdown_event.set()
            
            # Wait for active tasks to complete
            start_time = time.time()
            while self.active_tasks and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            # Shutdown workers
            for worker in self.workers:
                worker.shutdown(wait=True)
            
            # Stop monitoring
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5.0)
            
            logger.info("Parallel OCR processor stopped")
            
        except Exception as e:
            logger.error(f"Error stopping parallel processor: {e}")
    
    @ocr_profiler.profile_function("parallel_task_submission")
    def submit_task(self, 
                   task_id: str,
                   file_content: bytes,
                   mime_type: str,
                   priority: Priority = Priority.NORMAL,
                   callback: Optional[Callable] = None,
                   metadata: Dict[str, Any] = None) -> str:
        """
        Submit a task for parallel processing
        
        Args:
            task_id: Unique task identifier
            file_content: Document content
            mime_type: MIME type of document
            priority: Task priority
            callback: Optional callback function
            metadata: Additional metadata
            
        Returns:
            Task ID for tracking
        """
        try:
            task = ProcessingTask(
                task_id=task_id,
                file_content=file_content,
                mime_type=mime_type,
                priority=priority,
                callback=callback,
                metadata=metadata or {}
            )
            
            # Add to queue
            self.task_queue.put(task, timeout=5.0)
            
            with self._lock:
                self.stats.total_tasks += 1
                self.stats.queue_size = self.task_queue.qsize()
            
            logger.debug(f"Task {task_id} submitted with priority {priority.name}")
            return task_id
            
        except queue.Full:
            logger.error(f"Task queue full, cannot submit task {task_id}")
            raise RuntimeError("Task queue is full")
        except Exception as e:
            logger.error(f"Failed to submit task {task_id}: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a specific task"""
        with self._lock:
            # Check active tasks
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                return {
                    'status': 'processing',
                    'started_at': task.started_timestamp,
                    'processing_time': time.time() - task.started_timestamp if task.started_timestamp else 0,
                    'metadata': task.metadata
                }
            
            # Check completed tasks
            if task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]
                return {
                    'status': 'completed' if task.result else 'failed',
                    'started_at': task.started_timestamp,
                    'completed_at': task.completed_timestamp,
                    'processing_time': (task.completed_timestamp - task.started_timestamp) 
                                     if task.started_timestamp and task.completed_timestamp else 0,
                    'result': task.result,
                    'error': task.error,
                    'metadata': task.metadata
                }
            
            # Check if task is in queue
            return {'status': 'queued' if self._is_task_in_queue(task_id) else 'not_found'}
    
    def get_processing_stats(self) -> ProcessingStats:
        """Get current processing statistics"""
        with self._lock:
            # Update real-time stats
            self.stats.active_workers = len(self.worker_futures)
            self.stats.queue_size = self.task_queue.qsize()
            
            # Update throughput
            if self.stats.completed_tasks > 0:
                elapsed_time = time.time() - self.last_stats_update
                if elapsed_time > 0:
                    self.stats.throughput_per_minute = (self.stats.completed_tasks / elapsed_time) * 60
            
            return self.stats
    
    def _start_thread_workers(self):
        """Start thread-based workers"""
        executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="OCR-Worker")
        self.workers.append(executor)
        
        # Submit worker tasks
        for i in range(self.max_workers):
            future = executor.submit(self._worker_thread)
            self.worker_futures[f"thread-{i}"] = future
    
    def _start_process_workers(self):
        """Start process-based workers"""
        executor = ProcessPoolExecutor(max_workers=self.max_workers)
        self.workers.append(executor)
        
        # Submit worker tasks
        for i in range(self.max_workers):
            future = executor.submit(self._worker_process)
            self.worker_futures[f"process-{i}"] = future
    
    def _start_hybrid_workers(self):
        """Start hybrid workers (threads + processes)"""
        # Use threads for I/O bound tasks (document loading, preprocessing)
        thread_workers = max(1, self.max_workers // 2)
        thread_executor = ThreadPoolExecutor(max_workers=thread_workers, thread_name_prefix="OCR-Thread")
        self.workers.append(thread_executor)
        
        # Use processes for CPU bound tasks (OCR processing)
        process_workers = max(1, self.max_workers - thread_workers)
        process_executor = ProcessPoolExecutor(max_workers=process_workers)
        self.workers.append(process_executor)
        
        # Submit worker tasks
        for i in range(thread_workers):
            future = thread_executor.submit(self._worker_thread)
            self.worker_futures[f"thread-{i}"] = future
        
        for i in range(process_workers):
            future = process_executor.submit(self._worker_process)
            self.worker_futures[f"process-{i}"] = future
    
    def _worker_thread(self):
        """Thread worker for processing tasks"""
        worker_id = threading.current_thread().name
        logger.debug(f"Worker thread {worker_id} started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get task from queue
                task = self.task_queue.get(timeout=1.0)
                
                # Process task
                self._process_task(task, worker_id)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker thread {worker_id} error: {e}")
        
        logger.debug(f"Worker thread {worker_id} stopped")
    
    def _worker_process(self):
        """Process worker for CPU-intensive tasks"""
        worker_id = f"process-{multiprocessing.current_process().pid}"
        logger.debug(f"Worker process {worker_id} started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get task from queue
                task = self.task_queue.get(timeout=1.0)
                
                # Process task
                self._process_task(task, worker_id)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker process {worker_id} error: {e}")
        
        logger.debug(f"Worker process {worker_id} stopped")
    
    @ocr_profiler.profile_function("parallel_task_processing")
    def _process_task(self, task: ProcessingTask, worker_id: str):
        """Process a single task"""
        task.started_timestamp = time.time()
        
        try:
            # Add to active tasks
            with self._lock:
                self.active_tasks[task.task_id] = task
            
            logger.debug(f"Worker {worker_id} processing task {task.task_id}")
            
            # Import here to avoid circular imports
            from .document_processor import DocumentProcessor
            
            # Create processor instance
            processor = DocumentProcessor()
            if not processor.initialize():
                raise RuntimeError("Failed to initialize document processor")
            
            # Process document
            result = processor.process_invoice(
                task.file_content, 
                task.mime_type, 
                task.task_id
            )
            
            # Store result
            task.result = {
                'success': result.success,
                'extracted_data': result.extracted_data,
                'confidence_score': result.confidence_score,
                'processing_time': result.total_processing_time,
                'engines_used': result.engines_used,
                'worker_id': worker_id
            }
            
            task.completed_timestamp = time.time()
            
            # Update statistics
            with self._lock:
                self.stats.completed_tasks += 1
                processing_time = task.completed_timestamp - task.started_timestamp
                
                # Update average processing time
                if self.stats.completed_tasks == 1:
                    self.stats.average_processing_time = processing_time
                else:
                    self.stats.average_processing_time = (
                        (self.stats.average_processing_time * (self.stats.completed_tasks - 1) + processing_time) /
                        self.stats.completed_tasks
                    )
            
            # Call callback if provided
            if task.callback:
                try:
                    task.callback(task.result)
                except Exception as e:
                    logger.warning(f"Task callback failed for {task.task_id}: {e}")
            
            logger.debug(f"Task {task.task_id} completed successfully by worker {worker_id}")
            
        except Exception as e:
            task.error = str(e)
            task.completed_timestamp = time.time()
            
            with self._lock:
                self.stats.failed_tasks += 1
            
            logger.error(f"Task {task.task_id} failed in worker {worker_id}: {e}")
        
        finally:
            # Move from active to completed
            with self._lock:
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]
                self.completed_tasks[task.task_id] = task
                
                # Limit completed tasks history
                if len(self.completed_tasks) > 1000:
                    oldest_tasks = sorted(
                        self.completed_tasks.items(),
                        key=lambda x: x[1].completed_timestamp or 0
                    )[:100]
                    for task_id, _ in oldest_tasks:
                        del self.completed_tasks[task_id]
    
    def _monitor_resources(self):
        """Monitor system resources and adjust workers if needed"""
        logger.debug("Resource monitor started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get system metrics
                process = psutil.Process()
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()
                
                with self._lock:
                    self.stats.memory_usage_mb = memory_info.rss / 1024 / 1024
                    self.stats.cpu_usage_percent = cpu_percent
                
                # Check resource limits
                if self.stats.memory_usage_mb > self.memory_limit_mb:
                    logger.warning(f"Memory usage ({self.stats.memory_usage_mb:.1f}MB) "
                                 f"exceeds limit ({self.memory_limit_mb}MB)")
                    self._scale_down_workers()
                
                if self.stats.cpu_usage_percent > self.cpu_limit_percent:
                    logger.warning(f"CPU usage ({self.stats.cpu_usage_percent:.1f}%) "
                                 f"exceeds limit ({self.cpu_limit_percent}%)")
                    self._scale_down_workers()
                
                # Check if we can scale up
                elif (self.stats.queue_size > self.max_workers * 2 and 
                      self.stats.memory_usage_mb < self.memory_limit_mb * 0.7 and
                      self.stats.cpu_usage_percent < self.cpu_limit_percent * 0.7):
                    self._scale_up_workers()
                
                time.sleep(5.0)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                time.sleep(10.0)
        
        logger.debug("Resource monitor stopped")
    
    def _scale_up_workers(self):
        """Scale up workers if resources allow"""
        # Implementation would depend on the specific executor type
        # For now, just log the intention
        logger.info("Considering scaling up workers")
    
    def _scale_down_workers(self):
        """Scale down workers to reduce resource usage"""
        # Implementation would depend on the specific executor type
        # For now, just log the intention
        logger.info("Considering scaling down workers")
    
    def _is_task_in_queue(self, task_id: str) -> bool:
        """Check if task is still in queue (expensive operation)"""
        # This is a simplified check - in practice, you might want to maintain
        # a separate index of queued tasks for efficiency
        return self.task_queue.qsize() > 0
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for all tasks to complete"""
        start_time = time.time()
        
        while True:
            with self._lock:
                if not self.active_tasks and self.task_queue.empty():
                    return True
            
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(0.1)
    
    def clear_completed_tasks(self):
        """Clear completed tasks history"""
        with self._lock:
            self.completed_tasks.clear()
            logger.info("Completed tasks history cleared")


# Global parallel processor instance
parallel_processor = ParallelOCRProcessor()