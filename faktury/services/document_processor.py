"""
Document Processing Orchestrator for Open Source OCR Migration

This service acts as the main processing coordinator that chains preprocessing,
OCR processing, and field extraction with comprehensive error handling,
fallback mechanisms, and parallel processing capabilities.

Enhanced with performance optimization features:
- Intelligent caching for frequently processed document types
- Performance profiling and bottleneck identification
- Optimized image preprocessing with adaptive profiles
- Parallel processing for multiple document formats
"""

import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import json
import traceback

from .ocr_engine_service import OCREngineService, OCREngineFactory, OCREngineType, DocumentType, OCREngineSelector
from .image_preprocessor import ImagePreprocessor
from .optimized_image_preprocessor import OptimizedImagePreprocessor
from .confidence_calculator import ConfidenceCalculator
from .invoice_field_extractor import InvoiceFieldExtractor
from .polish_invoice_processor import PolishInvoiceProcessor
from .ocr_performance_profiler import ocr_profiler
from .ocr_result_cache import ocr_cache
from .ocr_engine_optimizer import ocr_optimizer, OptimizationStrategy

logger = logging.getLogger(__name__)


class ProcessingStage(Enum):
    """Stages of document processing pipeline"""
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    OCR_PROCESSING = "ocr_processing"
    FIELD_EXTRACTION = "field_extraction"
    CONFIDENCE_CALCULATION = "confidence_calculation"
    VALIDATION_CHECKS = "validation_checks"
    RESULT_COMPILATION = "result_compilation"


class ProcessingStatus(Enum):
    """Status of processing operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


@dataclass
class ProcessingStep:
    """Individual processing step metadata"""
    stage: ProcessingStage
    status: ProcessingStatus
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    engine_used: Optional[str] = None
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Complete processing result with metadata"""
    success: bool
    extracted_data: Dict[str, Any]
    confidence_score: float
    processing_steps: List[ProcessingStep]
    total_processing_time: float
    engines_used: List[str]
    fallback_applied: bool = False
    error_details: Optional[Dict[str, Any]] = None
    raw_ocr_results: List[Dict[str, Any]] = field(default_factory=list)
    preprocessing_info: Dict[str, Any] = field(default_factory=dict)


class DocumentProcessingError(Exception):
    """Custom exception for document processing errors"""
    def __init__(self, message: str, stage: ProcessingStage, details: Dict[str, Any] = None):
        super().__init__(message)
        self.stage = stage
        self.details = details or {}


class DocumentProcessor:
    """
    Main document processing orchestrator
    
    This service coordinates the complete OCR processing pipeline:
    1. Input validation and preprocessing
    2. Parallel OCR processing with multiple engines
    3. Field extraction and data structuring
    4. Confidence calculation and validation
    5. Error handling and fallback mechanisms
    6. Processing metadata tracking
    """
    
    def __init__(self, 
                 max_workers: int = 3,
                 enable_parallel_processing: bool = True,
                 confidence_threshold: float = 70.0,
                 max_retries: int = 2,
                 fallback_enabled: bool = True,
                 enable_performance_optimization: bool = True,
                 enable_caching: bool = True,
                 optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED):
        """
        Initialize Document Processor with performance optimizations
        
        Args:
            max_workers: Maximum number of parallel workers
            enable_parallel_processing: Enable parallel OCR engine processing
            confidence_threshold: Minimum confidence threshold for acceptance
            max_retries: Maximum number of retry attempts per stage
            fallback_enabled: Enable fallback mechanisms
            enable_performance_optimization: Enable performance optimizations
            enable_caching: Enable intelligent caching
            optimization_strategy: OCR optimization strategy
        """
        self.max_workers = max_workers
        self.enable_parallel_processing = enable_parallel_processing
        self.confidence_threshold = confidence_threshold
        self.max_retries = max_retries
        self.fallback_enabled = fallback_enabled
        self.enable_performance_optimization = enable_performance_optimization
        self.enable_caching = enable_caching
        self.optimization_strategy = optimization_strategy
        
        # Initialize processing components with optimization
        if enable_performance_optimization:
            self.image_preprocessor = OptimizedImagePreprocessor(
                enable_caching=enable_caching,
                max_workers=max_workers
            )
        else:
            self.image_preprocessor = ImagePreprocessor()
        
        self.confidence_calculator = ConfidenceCalculator()
        self.field_extractor = InvoiceFieldExtractor()
        self.polish_processor = PolishInvoiceProcessor()
        self.engine_selector = OCREngineSelector()
        
        # Initialize OCR engines
        self.ocr_engines = []
        self.is_initialized = False
        
        # Processing statistics
        self.processing_stats = {
            'total_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'average_processing_time': 0.0,
            'stage_performance': {},
            'engine_usage': {},
            'fallback_usage': 0
        }
        
        logger.info("DocumentProcessor initialized")
    
    def initialize(self) -> bool:
        """
        Initialize the document processor and all its components
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing DocumentProcessor components")
            
            # Initialize OCR engines
            self.ocr_engines = OCREngineFactory.initialize_all_engines()
            
            if not self.ocr_engines:
                logger.error("No OCR engines could be initialized")
                return False
            
            logger.info(f"Initialized {len(self.ocr_engines)} OCR engines: {[e.engine_name for e in self.ocr_engines]}")
            
            # Initialize processing statistics for each stage
            for stage in ProcessingStage:
                self.processing_stats['stage_performance'][stage.value] = {
                    'total_attempts': 0,
                    'successful_attempts': 0,
                    'average_duration': 0.0,
                    'error_count': 0
                }
            
            # Initialize engine usage statistics
            for engine in self.ocr_engines:
                self.processing_stats['engine_usage'][engine.engine_name] = {
                    'usage_count': 0,
                    'success_count': 0,
                    'average_confidence': 0.0,
                    'average_processing_time': 0.0
                }
            
            self.is_initialized = True
            logger.info("DocumentProcessor initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"DocumentProcessor initialization failed: {e}", exc_info=True)
            self.is_initialized = False
            return False
    
    @ocr_profiler.profile_function("document_processing")
    def process_invoice(self, file_content: bytes, mime_type: str, document_id: Optional[str] = None) -> ProcessingResult:
        """
        Process invoice document through optimized pipeline with caching and profiling
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            document_id: Optional document identifier for tracking
            
        Returns:
            ProcessingResult containing extracted data and metadata
        """
        start_time = time.time()
        processing_steps = []
        
        logger.info(f"Starting optimized document processing for document_id: {document_id}")
        
        if not self.is_initialized:
            raise DocumentProcessingError(
                "DocumentProcessor not initialized",
                ProcessingStage.VALIDATION,
                {"document_id": document_id}
            )
        
        # Check cache first if enabled
        if self.enable_caching:
            with ocr_profiler.profile_stage("cache_lookup"):
                cached_result = ocr_cache.get(file_content, mime_type)
                if cached_result:
                    logger.info(f"Cache hit for document_id: {document_id}")
                    return self._create_cached_processing_result(cached_result, start_time)
        
        try:
            # Stage 1: Input Validation
            validation_step = self._execute_stage(
                ProcessingStage.VALIDATION,
                self._validate_input,
                file_content, mime_type
            )
            processing_steps.append(validation_step)
            
            if validation_step.status == ProcessingStatus.FAILED:
                raise DocumentProcessingError(
                    f"Input validation failed: {validation_step.error_message}",
                    ProcessingStage.VALIDATION,
                    {"validation_errors": validation_step.metadata}
                )
            
            # Stage 2: Image Preprocessing
            preprocessing_step = self._execute_stage(
                ProcessingStage.PREPROCESSING,
                self._preprocess_document,
                file_content, mime_type
            )
            processing_steps.append(preprocessing_step)
            
            if preprocessing_step.status == ProcessingStatus.FAILED:
                if self.fallback_enabled:
                    logger.warning("Preprocessing failed, using original document")
                    preprocessed_images = [file_content]
                    preprocessing_step.status = ProcessingStatus.SKIPPED
                else:
                    raise DocumentProcessingError(
                        f"Preprocessing failed: {preprocessing_step.error_message}",
                        ProcessingStage.PREPROCESSING
                    )
            else:
                preprocessed_images = preprocessing_step.metadata.get('processed_images', [file_content])
            
            # Stage 3: OCR Processing (parallel or sequential)
            ocr_step = self._execute_stage(
                ProcessingStage.OCR_PROCESSING,
                self._process_with_ocr_engines,
                preprocessed_images, mime_type
            )
            processing_steps.append(ocr_step)
            
            if ocr_step.status == ProcessingStatus.FAILED:
                raise DocumentProcessingError(
                    f"OCR processing failed: {ocr_step.error_message}",
                    ProcessingStage.OCR_PROCESSING,
                    {"ocr_errors": ocr_step.metadata}
                )
            
            ocr_results = ocr_step.metadata.get('ocr_results', [])
            best_ocr_result = ocr_step.metadata.get('best_result', {})
            
            # Stage 4: Field Extraction
            extraction_step = self._execute_stage(
                ProcessingStage.FIELD_EXTRACTION,
                self._extract_invoice_fields,
                best_ocr_result.get('raw_text', ''), best_ocr_result
            )
            processing_steps.append(extraction_step)
            
            if extraction_step.status == ProcessingStatus.FAILED:
                raise DocumentProcessingError(
                    f"Field extraction failed: {extraction_step.error_message}",
                    ProcessingStage.FIELD_EXTRACTION
                )
            
            extracted_data = extraction_step.metadata.get('extracted_data', {})
            
            # Stage 5: Confidence Calculation
            confidence_step = self._execute_stage(
                ProcessingStage.CONFIDENCE_CALCULATION,
                self._calculate_confidence,
                extracted_data, best_ocr_result, best_ocr_result.get('raw_text', ''), ocr_results
            )
            processing_steps.append(confidence_step)
            
            confidence_result = confidence_step.metadata.get('confidence_result', {})
            overall_confidence = confidence_result.get('overall_confidence', 0.0)
            
            # Stage 6: Final Validation
            validation_step = self._execute_stage(
                ProcessingStage.VALIDATION_CHECKS,
                self._perform_final_validation,
                extracted_data, overall_confidence
            )
            processing_steps.append(validation_step)
            
            # Stage 7: Result Compilation
            compilation_step = self._execute_stage(
                ProcessingStage.RESULT_COMPILATION,
                self._compile_final_result,
                extracted_data, confidence_result, ocr_results, preprocessing_step.metadata
            )
            processing_steps.append(compilation_step)
            
            # Create final processing result
            total_time = time.time() - start_time
            engines_used = list(set(step.engine_used for step in processing_steps if step.engine_used))
            # Also get engines from OCR results
            if ocr_results:
                ocr_engines = [r.get('engine_name') for r in ocr_results if r.get('engine_name')]
                engines_used.extend(ocr_engines)
                engines_used = list(set(engines_used))  # Remove duplicates
            fallback_applied = any(step.status == ProcessingStatus.SKIPPED for step in processing_steps)
            
            result = ProcessingResult(
                success=True,
                extracted_data=compilation_step.metadata.get('final_data', extracted_data),
                confidence_score=overall_confidence,
                processing_steps=processing_steps,
                total_processing_time=total_time,
                engines_used=engines_used,
                fallback_applied=fallback_applied,
                raw_ocr_results=ocr_results,
                preprocessing_info=preprocessing_step.metadata
            )
            
            # Cache successful results if enabled
            if self.enable_caching and result.success and overall_confidence > 60.0:
                with ocr_profiler.profile_stage("cache_storage"):
                    cache_data = {
                        'extracted_data': result.extracted_data,
                        'confidence_score': result.confidence_score,
                        'processing_time': result.total_processing_time,
                        'engines_used': result.engines_used,
                        'cache_timestamp': time.time()
                    }
                    ocr_cache.put(file_content, mime_type, cache_data)
            
            # Update statistics
            self._update_processing_stats(result)
            
            logger.info(f"Optimized document processing completed successfully in {total_time:.2f}s with {overall_confidence:.1f}% confidence")
            return result
            
        except DocumentProcessingError as e:
            total_time = time.time() - start_time
            logger.error(f"Document processing failed at stage {e.stage.value}: {e}")
            
            result = ProcessingResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                processing_steps=processing_steps,
                total_processing_time=total_time,
                engines_used=[],
                error_details={
                    'stage': e.stage.value,
                    'message': str(e),
                    'details': e.details
                }
            )
            
            self._update_processing_stats(result)
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Unexpected error in document processing: {e}", exc_info=True)
            
            result = ProcessingResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                processing_steps=processing_steps,
                total_processing_time=total_time,
                engines_used=[],
                error_details={
                    'stage': 'unknown',
                    'message': str(e),
                    'traceback': traceback.format_exc()
                }
            )
            
            self._update_processing_stats(result)
            return result
    
    def _execute_stage(self, stage: ProcessingStage, func, *args, **kwargs) -> ProcessingStep:
        """
        Execute a processing stage with error handling and retry logic
        
        Args:
            stage: Processing stage being executed
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            ProcessingStep with execution results
        """
        step = ProcessingStep(stage=stage, status=ProcessingStatus.PENDING)
        
        for attempt in range(self.max_retries + 1):
            step.start_time = time.time()
            step.retry_count = attempt
            step.status = ProcessingStatus.IN_PROGRESS
            
            try:
                result = func(*args, **kwargs)
                step.end_time = time.time()
                step.duration = step.end_time - step.start_time
                step.status = ProcessingStatus.COMPLETED
                
                # Store result in metadata
                if isinstance(result, dict):
                    step.metadata.update(result)
                else:
                    step.metadata['result'] = result
                
                # Update stage statistics
                self._update_stage_stats(stage, step.duration, True)
                
                logger.debug(f"Stage {stage.value} completed in {step.duration:.2f}s")
                break
                
            except Exception as e:
                step.end_time = time.time()
                step.duration = step.end_time - step.start_time
                step.error_message = str(e)
                step.metadata['error_details'] = {
                    'exception_type': type(e).__name__,
                    'traceback': traceback.format_exc()
                }
                
                if attempt < self.max_retries:
                    step.status = ProcessingStatus.RETRYING
                    logger.warning(f"Stage {stage.value} failed (attempt {attempt + 1}), retrying: {e}")
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                else:
                    step.status = ProcessingStatus.FAILED
                    logger.error(f"Stage {stage.value} failed after {attempt + 1} attempts: {e}")
                    
                    # Update stage statistics
                    self._update_stage_stats(stage, step.duration, False)
        
        return step
    
    def _create_cached_processing_result(self, cached_data: Dict[str, Any], start_time: float) -> ProcessingResult:
        """Create ProcessingResult from cached data"""
        total_time = time.time() - start_time
        
        return ProcessingResult(
            success=True,
            extracted_data=cached_data.get('extracted_data', {}),
            confidence_score=cached_data.get('confidence_score', 0.0),
            processing_steps=[],  # No processing steps for cached results
            total_processing_time=total_time,
            engines_used=cached_data.get('engines_used', []),
            fallback_applied=False,
            raw_ocr_results=[],
            preprocessing_info={'cache_hit': True, 'cache_timestamp': cached_data.get('cache_timestamp')}
        )
    
    def _validate_input(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Validate input parameters"""
        errors = []
        
        if not file_content:
            errors.append("Empty file content")
        
        if len(file_content) == 0:
            errors.append("File content has zero length")
        
        # Check file size limits (50MB max)
        max_size = 50 * 1024 * 1024
        if len(file_content) > max_size:
            errors.append(f"File size {len(file_content)} exceeds maximum {max_size}")
        
        # Check supported formats
        supported_formats = ['image/jpeg', 'image/png', 'image/tiff', 'application/pdf']
        if mime_type not in supported_formats:
            errors.append(f"Unsupported format: {mime_type}")
        
        if errors:
            raise ValueError(f"Input validation failed: {'; '.join(errors)}")
        
        return {
            'file_size': len(file_content),
            'mime_type': mime_type,
            'validation_passed': True
        }
    
    def _preprocess_document(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Preprocess document for optimal OCR"""
        try:
            processed_images = self.image_preprocessor.preprocess_document(file_content, mime_type)
            preprocessing_info = self.image_preprocessor.get_preprocessing_info(file_content, mime_type)
            
            return {
                'processed_images': processed_images,
                'preprocessing_info': preprocessing_info,
                'images_count': len(processed_images)
            }
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            raise
    
    def _process_with_ocr_engines(self, processed_images: List[bytes], mime_type: str) -> Dict[str, Any]:
        """Process document with multiple OCR engines"""
        if not processed_images:
            raise ValueError("No processed images available")
        
        # Use first image for now (multi-page support can be added later)
        image_content = processed_images[0]
        
        # Select appropriate engines based on document type
        document_type = DocumentType.POLISH_INVOICE  # Assume Polish invoice for now
        available_engines = [engine for engine in self.ocr_engines if engine.is_initialized]
        
        if not available_engines:
            raise RuntimeError("No initialized OCR engines available")
        
        ocr_results = []
        
        if self.enable_parallel_processing and len(available_engines) > 1:
            # Parallel processing
            ocr_results = self._process_parallel_ocr(image_content, mime_type, available_engines)
        else:
            # Sequential processing
            ocr_results = self._process_sequential_ocr(image_content, mime_type, available_engines)
        
        if not ocr_results:
            raise RuntimeError("No valid OCR results obtained")
        
        # Select best result
        best_result = max(ocr_results, key=lambda r: r.get('confidence_score', 0.0))
        
        return {
            'ocr_results': ocr_results,
            'best_result': best_result,
            'engines_used': [r.get('engine_name', 'unknown') for r in ocr_results],
            'total_engines': len(available_engines)
        }
    
    def _process_parallel_ocr(self, image_content: bytes, mime_type: str, engines: List[OCREngineService]) -> List[Dict[str, Any]]:
        """Process document with multiple OCR engines in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(engines))) as executor:
            # Submit tasks
            future_to_engine = {
                executor.submit(self._safe_ocr_process, engine, image_content, mime_type): engine
                for engine in engines
            }
            
            # Collect results
            for future in as_completed(future_to_engine):
                engine = future_to_engine[future]
                try:
                    result = future.result(timeout=60)  # 60 second timeout per engine
                    if result:
                        result['engine_name'] = engine.engine_name
                        results.append(result)
                        self._update_engine_stats(engine.engine_name, result, True)
                except Exception as e:
                    logger.error(f"Parallel OCR processing failed for {engine.engine_name}: {e}")
                    self._update_engine_stats(engine.engine_name, {}, False)
        
        return results
    
    def _process_sequential_ocr(self, image_content: bytes, mime_type: str, engines: List[OCREngineService]) -> List[Dict[str, Any]]:
        """Process document with OCR engines sequentially"""
        results = []
        
        for engine in engines:
            try:
                result = self._safe_ocr_process(engine, image_content, mime_type)
                if result:
                    result['engine_name'] = engine.engine_name
                    results.append(result)
                    self._update_engine_stats(engine.engine_name, result, True)
            except Exception as e:
                logger.error(f"Sequential OCR processing failed for {engine.engine_name}: {e}")
                self._update_engine_stats(engine.engine_name, {}, False)
        
        return results
    
    def _safe_ocr_process(self, engine: OCREngineService, image_content: bytes, mime_type: str) -> Optional[Dict[str, Any]]:
        """Safely process document with OCR engine"""
        try:
            start_time = time.time()
            result = engine.process_document(image_content, mime_type)
            processing_time = time.time() - start_time
            
            if result:
                result['processing_time'] = processing_time
                return result
            
        except Exception as e:
            logger.error(f"OCR engine {engine.engine_name} failed: {e}")
        
        return None
    
    def _extract_invoice_fields(self, raw_text: str, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured invoice fields from OCR text"""
        try:
            confidence_data = {
                'confidence_score': ocr_result.get('confidence_score', 0.0),
                'field_confidence': ocr_result.get('field_confidence', {})
            }
            
            extraction_result = self.field_extractor.extract_fields(raw_text, confidence_data)
            
            return {
                'extracted_data': extraction_result,
                'extraction_method': 'pattern_matching',
                'fields_extracted': len(extraction_result.get('extracted_fields', {}))
            }
            
        except Exception as e:
            logger.error(f"Field extraction failed: {e}")
            raise
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any], ocr_result: Dict[str, Any], 
                            raw_text: str, all_ocr_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive confidence score"""
        try:
            # Get extracted fields from the extraction result
            fields_data = extracted_data.get('extracted_fields', {})
            
            confidence_result = self.confidence_calculator.calculate_overall_confidence(
                extracted_data=fields_data,
                ocr_confidence=ocr_result,
                raw_text=raw_text,
                engine_results=all_ocr_results
            )
            
            return {
                'confidence_result': confidence_result,
                'calculation_method': 'weighted_composite'
            }
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            raise
    
    def _perform_final_validation(self, extracted_data: Dict[str, Any], confidence_score: float) -> Dict[str, Any]:
        """Perform final validation checks"""
        validation_results = {
            'confidence_check': confidence_score >= self.confidence_threshold,
            'required_fields_check': True,
            'data_consistency_check': True,
            'validation_passed': True
        }
        
        # Check for required fields
        required_fields = ['numer_faktury', 'total_amount']
        fields_data = extracted_data.get('extracted_fields', {})
        
        missing_fields = []
        for field in required_fields:
            if field not in fields_data or not fields_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            validation_results['required_fields_check'] = False
            validation_results['missing_fields'] = missing_fields
            validation_results['validation_passed'] = False
        
        # Overall validation
        validation_results['validation_passed'] = (
            validation_results['confidence_check'] and
            validation_results['required_fields_check'] and
            validation_results['data_consistency_check']
        )
        
        return validation_results
    
    def _compile_final_result(self, extracted_data: Dict[str, Any], confidence_result: Dict[str, Any],
                            ocr_results: List[Dict[str, Any]], preprocessing_info: Dict[str, Any]) -> Dict[str, Any]:
        """Compile final processing result"""
        final_data = {
            'extracted_fields': extracted_data.get('extracted_fields', {}),
            'line_items': extracted_data.get('line_items', []),
            'seller_info': extracted_data.get('seller_info'),
            'buyer_info': extracted_data.get('buyer_info'),
            'confidence_analysis': confidence_result,
            'processing_metadata': {
                'ocr_engines_used': len(ocr_results),
                'preprocessing_applied': bool(preprocessing_info),
                'extraction_method': 'composite_pipeline'
            }
        }
        
        return {
            'final_data': final_data,
            'compilation_successful': True
        }
    
    def _update_stage_stats(self, stage: ProcessingStage, duration: float, success: bool):
        """Update statistics for processing stage"""
        # Initialize stage stats if not exists
        if stage.value not in self.processing_stats['stage_performance']:
            self.processing_stats['stage_performance'][stage.value] = {
                'total_attempts': 0,
                'successful_attempts': 0,
                'average_duration': 0.0,
                'error_count': 0
            }
        
        stage_stats = self.processing_stats['stage_performance'][stage.value]
        stage_stats['total_attempts'] += 1
        
        if success:
            stage_stats['successful_attempts'] += 1
        else:
            stage_stats['error_count'] += 1
        
        # Update average duration
        total_attempts = stage_stats['total_attempts']
        current_avg = stage_stats['average_duration']
        stage_stats['average_duration'] = (current_avg * (total_attempts - 1) + duration) / total_attempts
    
    def _update_engine_stats(self, engine_name: str, result: Dict[str, Any], success: bool):
        """Update statistics for OCR engine usage"""
        if engine_name not in self.processing_stats['engine_usage']:
            return
        
        engine_stats = self.processing_stats['engine_usage'][engine_name]
        engine_stats['usage_count'] += 1
        
        if success:
            engine_stats['success_count'] += 1
            
            confidence = result.get('confidence_score', 0.0)
            processing_time = result.get('processing_time', 0.0)
            
            # Update average confidence
            usage_count = engine_stats['usage_count']
            current_avg_conf = engine_stats['average_confidence']
            engine_stats['average_confidence'] = (current_avg_conf * (usage_count - 1) + confidence) / usage_count
            
            # Update average processing time
            current_avg_time = engine_stats['average_processing_time']
            engine_stats['average_processing_time'] = (current_avg_time * (usage_count - 1) + processing_time) / usage_count
    
    def _update_processing_stats(self, result: ProcessingResult):
        """Update overall processing statistics"""
        self.processing_stats['total_processed'] += 1
        
        if result.success:
            self.processing_stats['successful_processing'] += 1
        else:
            self.processing_stats['failed_processing'] += 1
        
        if result.fallback_applied:
            self.processing_stats['fallback_usage'] += 1
        
        # Update average processing time
        total_processed = self.processing_stats['total_processed']
        current_avg = self.processing_stats['average_processing_time']
        self.processing_stats['average_processing_time'] = (
            (current_avg * (total_processed - 1) + result.total_processing_time) / total_processed
        )
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        return {
            'overall_stats': {
                'total_processed': self.processing_stats['total_processed'],
                'success_rate': (
                    self.processing_stats['successful_processing'] / 
                    max(1, self.processing_stats['total_processed'])
                ) * 100,
                'average_processing_time': self.processing_stats['average_processing_time'],
                'fallback_usage_rate': (
                    self.processing_stats['fallback_usage'] / 
                    max(1, self.processing_stats['total_processed'])
                ) * 100
            },
            'stage_performance': self.processing_stats['stage_performance'],
            'engine_performance': self.processing_stats['engine_usage'],
            'system_info': {
                'initialized_engines': len(self.ocr_engines),
                'parallel_processing_enabled': self.enable_parallel_processing,
                'max_workers': self.max_workers,
                'confidence_threshold': self.confidence_threshold
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the document processor"""
        health_status = {
            'status': 'healthy',
            'initialized': self.is_initialized,
            'components': {},
            'engines': {},
            'issues': []
        }
        
        # Check component health
        components = {
            'image_preprocessor': self.image_preprocessor,
            'confidence_calculator': self.confidence_calculator,
            'field_extractor': self.field_extractor,
            'polish_processor': self.polish_processor
        }
        
        for name, component in components.items():
            health_status['components'][name] = {
                'available': component is not None,
                'initialized': True  # Assume initialized if available
            }
        
        # Check engine health
        for engine in self.ocr_engines:
            health_status['engines'][engine.engine_name] = {
                'initialized': engine.is_initialized,
                'performance_metrics': engine.performance_metrics
            }
            
            if not engine.is_initialized:
                health_status['issues'].append(f"Engine {engine.engine_name} not initialized")
        
        # Overall health assessment
        if not self.is_initialized:
            health_status['status'] = 'unhealthy'
            health_status['issues'].append("DocumentProcessor not initialized")
        elif not self.ocr_engines:
            health_status['status'] = 'degraded'
            health_status['issues'].append("No OCR engines available")
        elif len([e for e in self.ocr_engines if e.is_initialized]) < len(self.ocr_engines):
            health_status['status'] = 'degraded'
        
        return health_status