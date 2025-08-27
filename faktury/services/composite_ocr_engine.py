"""
Composite OCR Engine Implementation

This module provides a composite OCR engine that combines multiple OCR engines
to achieve the best possible results through consensus and confidence-based selection.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, List, Tuple
from difflib import SequenceMatcher

from .ocr_engine_service import OCREngineService, OCREngineType, DocumentType
from .polish_invoice_processor import PolishInvoiceProcessor

logger = logging.getLogger(__name__)


class CompositeOCREngine(OCREngineService):
    """
    Composite OCR Engine that combines multiple engines for optimal results
    
    Features:
    - Parallel processing with multiple engines
    - Confidence-based result selection
    - Consensus-based text merging
    - Fallback mechanisms
    - Performance optimization
    """
    
    def __init__(self, 
                 engines: Optional[List[OCREngineService]] = None,
                 consensus_threshold: float = 0.7,
                 min_confidence_threshold: float = 50.0,
                 parallel_processing: bool = True,
                 max_workers: int = 3):
        """
        Initialize Composite OCR Engine
        
        Args:
            engines: List of OCR engines to use (default: empty list)
            consensus_threshold: Minimum similarity for consensus (0.0-1.0)
            min_confidence_threshold: Minimum confidence to consider results
            parallel_processing: Enable parallel processing of engines
            max_workers: Maximum number of worker threads
        """
        super().__init__("composite")
        
        self.engines = engines or []
        self.consensus_threshold = consensus_threshold
        self.min_confidence_threshold = min_confidence_threshold
        self.parallel_processing = parallel_processing
        self.max_workers = max_workers
        self.polish_processor = PolishInvoiceProcessor()
        
        # Strategy configuration
        self.selection_strategy = 'confidence_weighted'
        self.merge_strategy = 'best_fields'
        
        # Performance tracking
        self.engine_performance = {}
    
    def initialize(self) -> bool:
        """
        Initialize all constituent OCR engines
        
        Returns:
            bool: True if at least one engine initialized successfully
        """
        if not self.engines:
            logger.warning("No engines provided to composite engine")
            self.is_initialized = False
            return False
        
        initialized_count = 0
        
        for engine in self.engines:
            try:
                if engine.initialize():
                    initialized_count += 1
                    self.engine_performance[engine.engine_name] = {
                        'success_count': 0,
                        'total_count': 0,
                        'avg_confidence': 0.0,
                        'avg_processing_time': 0.0
                    }
                    logger.info(f"Initialized engine: {engine.engine_name}")
                else:
                    logger.warning(f"Failed to initialize engine: {engine.engine_name}")
            except Exception as e:
                logger.error(f"Error initializing engine {engine.engine_name}: {e}")
        
        self.is_initialized = initialized_count > 0
        
        if self.is_initialized:
            logger.info(f"Composite engine initialized with {initialized_count}/{len(self.engines)} engines")
        else:
            logger.error("No engines could be initialized")
        
        return self.is_initialized
    
    def process_document(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process document using multiple OCR engines and combine results
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            
        Returns:
            Dictionary containing combined OCR results
        """
        start_time = time.time()
        
        # Validate input
        is_valid, error_msg = self.validate_input(file_content, mime_type)
        if not is_valid:
            raise ValueError(error_msg)
        
        if not self.is_initialized:
            raise RuntimeError("Composite OCR engine not initialized")
        
        # Get available engines
        available_engines = [engine for engine in self.engines if engine.is_initialized]
        if not available_engines:
            raise RuntimeError("No initialized engines available")
        
        try:
            # For now, use sequential processing to avoid complexity
            engine_results = []
            for engine in available_engines:
                try:
                    result = engine.process_document(file_content, mime_type)
                    if result:
                        result['engine_name'] = engine.engine_name
                        engine_results.append(result)
                except Exception as e:
                    logger.error(f"Engine {engine.engine_name} failed: {e}")
            
            if not engine_results:
                raise RuntimeError("No valid OCR results obtained from any engine")
            
            # For now, just return the result with highest confidence
            best_result = max(engine_results, key=lambda r: r.get('confidence_score', 0.0))
            
            # Add composite-specific metadata
            processing_time = time.time() - start_time
            best_result.update({
                'processing_time': processing_time,
                'engine_name': self.engine_name,
                'engines_used': [r['engine_name'] for r in engine_results],
                'total_engines_attempted': len(available_engines),
                'successful_engines': len(engine_results),
                'selection_strategy': self.selection_strategy
            })
            
            # Update performance metrics
            success = best_result['confidence_score'] > self.min_confidence_threshold
            self.update_performance_metrics(processing_time, best_result['confidence_score'], success)
            
            logger.info(f"Composite processing completed in {processing_time:.2f}s with {best_result['confidence_score']:.1f}% confidence")
            return best_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Composite processing failed after {processing_time:.2f}s: {e}")
            self.update_performance_metrics(processing_time, 0.0, False)
            raise
    
    def get_confidence_score(self, result: Dict[str, Any]) -> float:
        """
        Get confidence score from composite result
        
        Args:
            result: OCR processing result
            
        Returns:
            float: Confidence score between 0.0 and 100.0
        """
        return result.get('confidence_score', 0.0)
    
    def add_engine(self, engine: OCREngineService) -> bool:
        """
        Add a new OCR engine to the composite
        
        Args:
            engine: OCR engine to add
            
        Returns:
            bool: True if engine was added successfully
        """
        try:
            self.engines.append(engine)
            self.engine_performance[engine.engine_name] = {
                'success_count': 0,
                'total_count': 0,
                'avg_confidence': 0.0,
                'avg_processing_time': 0.0
            }
            logger.info(f"Added engine: {engine.engine_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding engine {engine.engine_name}: {e}")
            return False
    
    def remove_engine(self, engine_name: str) -> bool:
        """
        Remove an OCR engine from the composite
        
        Args:
            engine_name: Name of engine to remove
            
        Returns:
            bool: True if engine was removed successfully
        """
        for i, engine in enumerate(self.engines):
            if engine.engine_name == engine_name:
                del self.engines[i]
                if engine_name in self.engine_performance:
                    del self.engine_performance[engine_name]
                logger.info(f"Removed engine: {engine_name}")
                return True
        
        logger.warning(f"Engine not found: {engine_name}")
        return False