"""
Minimal Composite OCR Engine Implementation for Testing

This is a simplified version without problematic imports for testing the abstraction layer.
"""

import logging
import time
from typing import Dict, Any, Optional, List

from .ocr_engine_service import OCREngineService
from .polish_invoice_processor import PolishInvoiceProcessor

logger = logging.getLogger(__name__)


class CompositeOCREngine(OCREngineService):
    """
    Minimal Composite OCR Engine for testing
    """
    
    def __init__(self, 
                 engines: Optional[List[OCREngineService]] = None,
                 consensus_threshold: float = 0.7,
                 min_confidence_threshold: float = 50.0):
        """
        Initialize Composite OCR Engine
        """
        super().__init__("composite")
        
        self.engines = engines or []
        self.consensus_threshold = consensus_threshold
        self.min_confidence_threshold = min_confidence_threshold
        self.polish_processor = PolishInvoiceProcessor()
    
    def initialize(self) -> bool:
        """
        Initialize all constituent OCR engines
        """
        if not self.engines:
            logger.warning("No engines provided to composite engine")
            return False
        
        initialized_count = 0
        for engine in self.engines:
            try:
                if engine.initialize():
                    initialized_count += 1
            except Exception as e:
                logger.error(f"Error initializing engine {engine.engine_name}: {e}")
        
        self.is_initialized = initialized_count > 0
        return self.is_initialized
    
    def process_document(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process document using multiple OCR engines
        """
        # Validate input
        is_valid, error_msg = self.validate_input(file_content, mime_type)
        if not is_valid:
            raise ValueError(error_msg)
        
        if not self.is_initialized:
            raise RuntimeError("Composite OCR engine not initialized")
        
        # For minimal implementation, just return a mock result
        return {
            'text': 'Mock composite OCR result',
            'confidence_score': 85.0,
            'engine_name': self.engine_name,
            'processing_time': 1.0,
            'engines_used': [engine.engine_name for engine in self.engines if engine.is_initialized]
        }
    
    def get_confidence_score(self, result: Dict[str, Any]) -> float:
        """
        Get confidence score from composite result
        """
        return result.get('confidence_score', 0.0)