"""
OCR Engine Abstraction Layer for Open Source OCR Migration

This module provides a unified interface for different OCR engines,
allowing seamless switching between Tesseract, EasyOCR, and composite engines.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class OCREngineType(Enum):
    """Enumeration of available OCR engine types"""
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    COMPOSITE = "composite"
    PADDLEOCR = "paddleocr"


class DocumentType(Enum):
    """Document types for engine selection optimization"""
    POLISH_INVOICE = "polish_invoice"
    GENERAL_DOCUMENT = "general_document"
    HANDWRITTEN = "handwritten"
    LOW_QUALITY = "low_quality"


class OCREngineService(ABC):
    """
    Abstract base class for OCR engines providing standard interface
    
    This class defines the contract that all OCR engines must implement
    to ensure compatibility with the existing system.
    """
    
    def __init__(self, engine_name: str):
        self.engine_name = engine_name
        self.supported_formats = ['image/jpeg', 'image/png', 'image/tiff', 'application/pdf']
        self.is_initialized = False
        self.performance_metrics = {
            'total_processed': 0,
            'total_processing_time': 0.0,
            'average_confidence': 0.0,
            'success_rate': 0.0
        }
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the OCR engine with required models and configurations
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def process_document(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process document and extract text with confidence scores
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        pass
    
    @abstractmethod
    def get_confidence_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate overall confidence score for extraction results
        
        Args:
            result: OCR processing result dictionary
            
        Returns:
            float: Confidence score between 0.0 and 100.0
        """
        pass
    
    def supports_format(self, mime_type: str) -> bool:
        """
        Check if engine supports the given file format
        
        Args:
            mime_type: MIME type to check
            
        Returns:
            bool: True if format is supported
        """
        return mime_type in self.supported_formats
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get engine information and capabilities
        
        Returns:
            Dictionary with engine metadata
        """
        return {
            'name': self.engine_name,
            'type': self.__class__.__name__,
            'supported_formats': self.supported_formats,
            'is_initialized': self.is_initialized,
            'performance_metrics': self.performance_metrics.copy()
        }
    
    def update_performance_metrics(self, processing_time: float, confidence: float, success: bool):
        """Update engine performance metrics"""
        self.performance_metrics['total_processed'] += 1
        self.performance_metrics['total_processing_time'] += processing_time
        
        # Update average confidence
        total_processed = self.performance_metrics['total_processed']
        current_avg = self.performance_metrics['average_confidence']
        self.performance_metrics['average_confidence'] = (
            (current_avg * (total_processed - 1) + confidence) / total_processed
        )
        
        # Update success rate
        if success:
            current_success_count = self.performance_metrics['success_rate'] * (total_processed - 1)
            self.performance_metrics['success_rate'] = (current_success_count + 1) / total_processed
        else:
            current_success_count = self.performance_metrics['success_rate'] * (total_processed - 1)
            self.performance_metrics['success_rate'] = current_success_count / total_processed
    
    def get_average_processing_time(self) -> float:
        """Get average processing time per document"""
        if self.performance_metrics['total_processed'] > 0:
            return self.performance_metrics['total_processing_time'] / self.performance_metrics['total_processed']
        return 0.0
    
    def validate_input(self, file_content: bytes, mime_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate input parameters before processing
        
        Args:
            file_content: Binary content to validate
            mime_type: MIME type to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_content:
            return False, "Empty file content"
        
        if len(file_content) == 0:
            return False, "File content has zero length"
        
        if not self.supports_format(mime_type):
            return False, f"Unsupported format: {mime_type}"
        
        # Check file size limits (50MB max)
        max_size = 50 * 1024 * 1024  # 50MB
        if len(file_content) > max_size:
            return False, f"File size {len(file_content)} exceeds maximum {max_size}"
        
        return True, None
    
    def preprocess_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess raw OCR result to standardize format
        
        Args:
            raw_result: Raw result from OCR engine
            
        Returns:
            Standardized result dictionary
        """
        return {
            'raw_text': raw_result.get('text', ''),
            'confidence_score': self.get_confidence_score(raw_result),
            'engine_name': self.engine_name,
            'processing_metadata': raw_result.get('metadata', {}),
            'word_confidences': raw_result.get('word_confidences', []),
            'bounding_boxes': raw_result.get('bounding_boxes', []),
            'processing_time': raw_result.get('processing_time', 0.0)
        }


class OCREngineSelector:
    """
    Engine selection logic based on document type and performance metrics
    """
    
    def __init__(self):
        self.engine_preferences = {
            DocumentType.POLISH_INVOICE: [
                OCREngineType.PADDLEOCR,  # PaddleOCR as primary for Polish invoices
                OCREngineType.COMPOSITE,
                OCREngineType.TESSERACT,
                OCREngineType.EASYOCR
            ],
            DocumentType.GENERAL_DOCUMENT: [
                OCREngineType.PADDLEOCR,
                OCREngineType.TESSERACT,
                OCREngineType.EASYOCR,
                OCREngineType.COMPOSITE
            ],
            DocumentType.HANDWRITTEN: [
                OCREngineType.EASYOCR,
                OCREngineType.COMPOSITE,
                OCREngineType.PADDLEOCR,
                OCREngineType.TESSERACT
            ],
            DocumentType.LOW_QUALITY: [
                OCREngineType.PADDLEOCR,
                OCREngineType.COMPOSITE,
                OCREngineType.EASYOCR,
                OCREngineType.TESSERACT
            ]
        }
    
    def select_engine(self, 
                     document_type: DocumentType, 
                     available_engines: List[OCREngineService],
                     performance_threshold: float = 80.0) -> Optional[OCREngineService]:
        """
        Select the best engine for the given document type
        
        Args:
            document_type: Type of document to process
            available_engines: List of available engine instances
            performance_threshold: Minimum performance threshold
            
        Returns:
            Selected engine instance or None if no suitable engine found
        """
        preferences = self.engine_preferences.get(document_type, [])
        engine_map = {engine.engine_name: engine for engine in available_engines}
        
        # Try engines in preference order
        for engine_type in preferences:
            for engine in available_engines:
                if (engine_type.value in engine.engine_name.lower() and 
                    engine.is_initialized and
                    engine.performance_metrics['average_confidence'] >= performance_threshold):
                    return engine
        
        # Fallback: return any initialized engine
        for engine in available_engines:
            if engine.is_initialized:
                logger.warning(f"Using fallback engine: {engine.engine_name}")
                return engine
        
        logger.error("No suitable OCR engine available")
        return None
    
    def get_engine_ranking(self, 
                          document_type: DocumentType,
                          available_engines: List[OCREngineService]) -> List[Tuple[OCREngineService, float]]:
        """
        Get ranked list of engines with scores for the document type
        
        Args:
            document_type: Type of document to process
            available_engines: List of available engine instances
            
        Returns:
            List of (engine, score) tuples sorted by score descending
        """
        rankings = []
        preferences = self.engine_preferences.get(document_type, [])
        
        for engine in available_engines:
            if not engine.is_initialized:
                continue
            
            score = 0.0
            
            # Base score from performance metrics
            score += engine.performance_metrics['average_confidence'] * 0.4
            score += engine.performance_metrics['success_rate'] * 100 * 0.3
            
            # Speed bonus (inverse of processing time)
            avg_time = engine.get_average_processing_time()
            if avg_time > 0:
                speed_score = min(30.0, 30.0 / avg_time)  # Max 30 points for speed
                score += speed_score * 0.2
            
            # Preference bonus
            engine_type_matches = [
                pref for pref in preferences 
                if pref.value in engine.engine_name.lower()
            ]
            if engine_type_matches:
                preference_index = preferences.index(engine_type_matches[0])
                preference_bonus = (len(preferences) - preference_index) * 2
                score += preference_bonus * 0.1
            
            rankings.append((engine, score))
        
        # Sort by score descending
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings


class OCREngineFactory:
    """
    Factory class for creating and managing OCR engine instances
    """
    
    _instances = {}
    
    @classmethod
    def create_engine(cls, engine_type: OCREngineType, **kwargs) -> OCREngineService:
        """
        Create OCR engine instance
        
        Args:
            engine_type: Type of engine to create
            **kwargs: Additional configuration parameters
            
        Returns:
            OCR engine instance
        """
        if engine_type == OCREngineType.TESSERACT:
            from .tesseract_ocr_engine import TesseractOCREngine
            return TesseractOCREngine(**kwargs)
        elif engine_type == OCREngineType.EASYOCR:
            from .easyocr_engine import EasyOCREngine
            return EasyOCREngine(**kwargs)
        elif engine_type == OCREngineType.COMPOSITE:
            from .composite_ocr_engine import CompositeOCREngine
            return CompositeOCREngine(**kwargs)
        elif engine_type == OCREngineType.PADDLEOCR:
            from .paddle_ocr_engine import PaddleOCREngine
            return PaddleOCREngine(**kwargs)
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")
    
    @classmethod
    def get_engine(cls, engine_type: OCREngineType, **kwargs) -> OCREngineService:
        """
        Get singleton engine instance
        
        Args:
            engine_type: Type of engine to get
            **kwargs: Additional configuration parameters
            
        Returns:
            OCR engine instance (singleton)
        """
        key = f"{engine_type.value}_{hash(frozenset(kwargs.items()))}"
        
        if key not in cls._instances:
            cls._instances[key] = cls.create_engine(engine_type, **kwargs)
        
        return cls._instances[key]
    
    @classmethod
    def get_all_engines(cls, **kwargs) -> List[OCREngineService]:
        """
        Get instances of all available engines
        
        Args:
            **kwargs: Configuration parameters for engines
            
        Returns:
            List of all engine instances
        """
        engines = []
        for engine_type in OCREngineType:
            try:
                engine = cls.get_engine(engine_type, **kwargs)
                engines.append(engine)
            except Exception as e:
                logger.warning(f"Failed to create {engine_type.value} engine: {e}")
        
        return engines
    
    @classmethod
    def initialize_all_engines(cls, **kwargs) -> List[OCREngineService]:
        """
        Initialize all available engines
        
        Args:
            **kwargs: Configuration parameters for engines
            
        Returns:
            List of successfully initialized engines
        """
        engines = cls.get_all_engines(**kwargs)
        initialized_engines = []
        
        for engine in engines:
            try:
                if engine.initialize():
                    initialized_engines.append(engine)
                    logger.info(f"Successfully initialized {engine.engine_name}")
                else:
                    logger.warning(f"Failed to initialize {engine.engine_name}")
            except Exception as e:
                logger.error(f"Error initializing {engine.engine_name}: {e}")
        
        return initialized_engines