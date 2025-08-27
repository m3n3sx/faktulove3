#!/usr/bin/env python3
"""
Ensemble OCR Service - Main Coordinator
Orchestrates multiple OCR engines with voting algorithms and confidence-based selection
"""

import os
import time
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# Import OCR engines
from .paddle_ocr_service import PaddleOCRService
from .easy_ocr_service import EasyOCRService
from .local_ocr_service import LocalOCRService

logger = logging.getLogger(__name__)

@dataclass
class EngineResult:
    """Represents a result from a single OCR engine"""
    engine_name: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    processing_time: float
    engine_metadata: Dict[str, Any]
    raw_ocr_results: Any
    preprocessing_applied: List[str]
    fallback_used: bool
    error_message: Optional[str] = None

@dataclass
class EnsembleResult:
    """Represents the final ensemble result"""
    best_result: EngineResult
    all_results: List[EngineResult]
    ensemble_confidence: float
    voting_metadata: Dict[str, Any]
    processing_time: float
    engines_used: List[str]
    fallback_used: bool

class EnsembleOCRError(Exception):
    """Base exception for Ensemble OCR errors"""
    pass

class EnsembleOCRInitializationError(EnsembleOCRError):
    """Raised when Ensemble OCR fails to initialize"""
    pass

class EnsembleOCRProcessingError(EnsembleOCRError):
    """Raised when document processing fails"""
    pass

class EnsembleOCRService:
    """
    Ensemble OCR Controller - Main Coordinator
    Orchestrates multiple OCR engines with voting algorithms and confidence-based selection
    """
    
    def __init__(self, 
                 engine_config: Dict[str, Any] = None,
                 voting_threshold: float = 0.8,
                 timeout_per_engine: int = 30,
                 max_workers: int = 3):
        """
        Initialize Ensemble OCR Service
        
        Args:
            engine_config: Configuration for individual engines
            voting_threshold: Confidence threshold for voting algorithm
            timeout_per_engine: Timeout per engine in seconds
            max_workers: Maximum number of concurrent workers
        """
        self.engine_config = engine_config or {}
        self.voting_threshold = voting_threshold
        self.timeout_per_engine = timeout_per_engine
        self.max_workers = max_workers
        
        # Initialize engines
        self.engines = {}
        self.engine_priorities = []
        self.engine_weights = {}
        
        # Performance tracking
        self.processing_times = []
        self.accuracy_metrics = []
        self.engine_performance = {}
        
        # Initialize engines
        self._initialize_engines()
    
    def _initialize_engines(self) -> None:
        """Initialize all available OCR engines"""
        try:
            logger.info("Initializing Ensemble OCR engines")
            
            # Initialize PaddleOCR (primary engine)
            try:
                paddle_config = self.engine_config.get('paddleocr', {})
                self.engines['paddleocr'] = PaddleOCRService(**paddle_config)
                self.engine_priorities.append('paddleocr')
                self.engine_weights['paddleocr'] = 0.5  # Primary weight
                logger.info("PaddleOCR engine initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {e}")
            
            # Initialize EasyOCR (fallback engine)
            try:
                easy_config = self.engine_config.get('easyocr', {})
                self.engines['easyocr'] = EasyOCRService(**easy_config)
                self.engine_priorities.append('easyocr')
                self.engine_weights['easyocr'] = 0.3  # Fallback weight
                logger.info("EasyOCR engine initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {e}")
            
            # Initialize Tesseract (last resort engine)
            try:
                tesseract_config = self.engine_config.get('tesseract', {})
                self.engines['tesseract'] = LocalOCRService(**tesseract_config)
                self.engine_priorities.append('tesseract')
                self.engine_weights['tesseract'] = 0.2  # Last resort weight
                logger.info("Tesseract engine initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Tesseract: {e}")
            
            if not self.engines:
                raise EnsembleOCRInitializationError("No OCR engines could be initialized")
            
            logger.info(f"Ensemble OCR initialized with {len(self.engines)} engines: {list(self.engines.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ensemble OCR: {e}")
            raise EnsembleOCRInitializationError(f"Ensemble OCR initialization failed: {e}")
    
    def process_invoice(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process invoice with ensemble OCR
        
        Args:
            file_content: File content as bytes
            mime_type: MIME type of the file
            
        Returns:
            Dictionary with ensemble results and metadata
        """
        start_time = time.time()
        
        try:
            logger.info("Starting Ensemble OCR invoice processing")
            
            # Process with all available engines
            engine_results = self._process_with_all_engines(file_content, mime_type)
            
            if not engine_results:
                raise EnsembleOCRProcessingError("No engines successfully processed the document")
            
            # Select best result using voting algorithm
            best_result = self._select_best_result(engine_results)
            
            # Combine results for enhanced accuracy
            ensemble_result = self._combine_results(engine_results, best_result)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # Prepare final result
            result = {
                'extracted_data': ensemble_result.best_result.extracted_data,
                'confidence_score': ensemble_result.ensemble_confidence,
                'processing_time': processing_time,
                'processor_version': 'Ensemble-OCR-2.0',
                'engine_metadata': {
                    'ensemble_engines_used': ensemble_result.engines_used,
                    'best_engine': ensemble_result.best_result.engine_name,
                    'voting_metadata': ensemble_result.voting_metadata,
                    'fallback_used': ensemble_result.fallback_used,
                    'total_engines_available': len(self.engines),
                    'engines_successful': len(engine_results)
                },
                'ensemble_results': {
                    'best_result': {
                        'engine': ensemble_result.best_result.engine_name,
                        'confidence': ensemble_result.best_result.confidence_score,
                        'processing_time': ensemble_result.best_result.processing_time
                    },
                    'all_results': [
                        {
                            'engine': r.engine_name,
                            'confidence': r.confidence_score,
                            'processing_time': r.processing_time,
                            'error': r.error_message
                        } for r in ensemble_result.all_results
                    ]
                },
                'preprocessing_applied': ensemble_result.best_result.preprocessing_applied,
                'fallback_used': ensemble_result.fallback_used
            }
            
            logger.info(f"Ensemble OCR processing completed in {processing_time:.2f}s with confidence {ensemble_result.ensemble_confidence:.2f}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Ensemble OCR processing failed after {processing_time:.2f}s: {e}")
            raise EnsembleOCRProcessingError(f"Ensemble OCR processing failed: {e}")
    
    def _process_with_all_engines(self, file_content: bytes, mime_type: str) -> List[EngineResult]:
        """
        Process document with all available engines concurrently
        
        Args:
            file_content: File content as bytes
            mime_type: MIME type of the file
            
        Returns:
            List of engine results
        """
        engine_results = []
        
        # Process engines in priority order with timeout
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks for all engines
            future_to_engine = {}
            for engine_name, engine in self.engines.items():
                future = executor.submit(self._process_with_engine, engine_name, engine, file_content, mime_type)
                future_to_engine[future] = engine_name
            
            # Collect results with timeout
            for future in as_completed(future_to_engine, timeout=self.timeout_per_engine * len(self.engines)):
                engine_name = future_to_engine[future]
                try:
                    result = future.result(timeout=self.timeout_per_engine)
                    if result:
                        engine_results.append(result)
                        logger.info(f"Engine {engine_name} completed successfully")
                except TimeoutError:
                    logger.warning(f"Engine {engine_name} timed out")
                    engine_results.append(EngineResult(
                        engine_name=engine_name,
                        extracted_data={},
                        confidence_score=0.0,
                        processing_time=self.timeout_per_engine,
                        engine_metadata={},
                        raw_ocr_results=None,
                        preprocessing_applied=[],
                        fallback_used=False,
                        error_message="Processing timeout"
                    ))
                except Exception as e:
                    logger.error(f"Engine {engine_name} failed: {e}")
                    engine_results.append(EngineResult(
                        engine_name=engine_name,
                        extracted_data={},
                        confidence_score=0.0,
                        processing_time=0.0,
                        engine_metadata={},
                        raw_ocr_results=None,
                        preprocessing_applied=[],
                        fallback_used=False,
                        error_message=str(e)
                    ))
        
        return engine_results
    
    def _process_with_engine(self, engine_name: str, engine: Any, file_content: bytes, mime_type: str) -> Optional[EngineResult]:
        """
        Process document with a single engine
        
        Args:
            engine_name: Name of the engine
            engine: Engine instance
            file_content: File content as bytes
            mime_type: MIME type of the file
            
        Returns:
            Engine result or None if failed
        """
        try:
            start_time = time.time()
            
            # Process with engine
            result = engine.process_invoice(file_content, mime_type)
            
            processing_time = time.time() - start_time
            
            # Create EngineResult
            engine_result = EngineResult(
                engine_name=engine_name,
                extracted_data=result.get('extracted_data', {}),
                confidence_score=result.get('confidence_score', 0.0),
                processing_time=processing_time,
                engine_metadata=result.get('engine_metadata', {}),
                raw_ocr_results=result.get('raw_ocr_results'),
                preprocessing_applied=result.get('preprocessing_applied', []),
                fallback_used=result.get('fallback_used', False)
            )
            
            return engine_result
            
        except Exception as e:
            logger.error(f"Engine {engine_name} processing failed: {e}")
            return None
    
    def _select_best_result(self, engine_results: List[EngineResult]) -> EngineResult:
        """
        Select best result using voting algorithm
        
        Args:
            engine_results: List of engine results
            
        Returns:
            Best engine result
        """
        try:
            # Filter out failed results
            valid_results = [r for r in engine_results if r.error_message is None and r.confidence_score > 0]
            
            if not valid_results:
                # If no valid results, return the first available result
                return engine_results[0] if engine_results else None
            
            # Weighted voting based on confidence and engine priority
            weighted_scores = []
            for result in valid_results:
                weight = self.engine_weights.get(result.engine_name, 0.1)
                weighted_score = result.confidence_score * weight
                weighted_scores.append((weighted_score, result))
            
            # Sort by weighted score (descending)
            weighted_scores.sort(key=lambda x: x[0], reverse=True)
            
            best_result = weighted_scores[0][1]
            logger.info(f"Selected best result from {best_result.engine_name} with weighted score {weighted_scores[0][0]:.3f}")
            
            return best_result
            
        except Exception as e:
            logger.error(f"Error selecting best result: {e}")
            # Return first available result as fallback
            return engine_results[0] if engine_results else None
    
    def _combine_results(self, engine_results: List[EngineResult], best_result: EngineResult) -> EnsembleResult:
        """
        Combine results from multiple engines for enhanced accuracy
        
        Args:
            engine_results: List of all engine results
            best_result: Best engine result
            
        Returns:
            Ensemble result with combined data
        """
        try:
            # Calculate ensemble confidence
            valid_results = [r for r in engine_results if r.error_message is None and r.confidence_score > 0]
            
            if len(valid_results) >= 2:
                # Multiple engines succeeded - use weighted average
                total_weight = 0
                weighted_confidence = 0
                
                for result in valid_results:
                    weight = self.engine_weights.get(result.engine_name, 0.1)
                    weighted_confidence += result.confidence_score * weight
                    total_weight += weight
                
                ensemble_confidence = weighted_confidence / total_weight if total_weight > 0 else best_result.confidence_score
                
                # Boost confidence if multiple engines agree
                if len(valid_results) >= 3:
                    ensemble_confidence = min(ensemble_confidence * 1.1, 1.0)
                
            else:
                # Single engine or fallback
                ensemble_confidence = best_result.confidence_score
            
            # Prepare voting metadata
            voting_metadata = {
                'total_engines': len(engine_results),
                'successful_engines': len(valid_results),
                'confidence_scores': {r.engine_name: r.confidence_score for r in engine_results},
                'processing_times': {r.engine_name: r.processing_time for r in engine_results},
                'voting_threshold': self.voting_threshold,
                'ensemble_confidence': ensemble_confidence
            }
            
            # Determine if fallback was used
            fallback_used = best_result.engine_name != 'paddleocr' or best_result.fallback_used
            
            # Create ensemble result
            ensemble_result = EnsembleResult(
                best_result=best_result,
                all_results=engine_results,
                ensemble_confidence=ensemble_confidence,
                voting_metadata=voting_metadata,
                processing_time=sum(r.processing_time for r in engine_results),
                engines_used=[r.engine_name for r in engine_results if r.error_message is None],
                fallback_used=fallback_used
            )
            
            return ensemble_result
            
        except Exception as e:
            logger.error(f"Error combining results: {e}")
            # Return basic ensemble result
            return EnsembleResult(
                best_result=best_result,
                all_results=engine_results,
                ensemble_confidence=best_result.confidence_score,
                voting_metadata={'error': str(e)},
                processing_time=best_result.processing_time,
                engines_used=[best_result.engine_name],
                fallback_used=best_result.fallback_used
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            return {
                'average_processing_time': np.mean(self.processing_times) if self.processing_times else 0.0,
                'total_processed': len(self.processing_times),
                'accuracy_metrics': np.mean(self.accuracy_metrics) if self.accuracy_metrics else 0.0,
                'engine_performance': self.engine_performance,
                'engine_type': 'ensemble',
                'engines_available': list(self.engines.keys()),
                'engine_priorities': self.engine_priorities,
                'voting_threshold': self.voting_threshold
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def is_available(self) -> bool:
        """Check if ensemble OCR is available"""
        return len(self.engines) > 0
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information"""
        return {
            'name': 'Ensemble OCR',
            'version': '2.0',
            'type': 'ensemble',
            'engines_available': list(self.engines.keys()),
            'engine_priorities': self.engine_priorities,
            'available': self.is_available(),
            'voting_algorithm': True,
            'confidence_based_selection': True,
            'accuracy_target': 0.95
        }
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get status of all engines"""
        status = {}
        for engine_name, engine in self.engines.items():
            try:
                if hasattr(engine, 'is_available'):
                    status[engine_name] = {
                        'available': engine.is_available(),
                        'info': engine.get_engine_info() if hasattr(engine, 'get_engine_info') else {}
                    }
                else:
                    status[engine_name] = {
                        'available': True,
                        'info': {}
                    }
            except Exception as e:
                status[engine_name] = {
                    'available': False,
                    'error': str(e)
                }
        
        return status
