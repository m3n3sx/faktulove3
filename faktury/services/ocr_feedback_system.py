"""
OCR Feedback System
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class OCRFeedbackSystem:
    def generate_ocr_feedback(self, ocr_result):
        """Generate OCR feedback"""
        return {
            'confidence': ocr_result.confidence_score,
            'suggestions': ['Sprawdź dokument', 'Popraw jakość skanowania'],
            'accuracy': 'high' if ocr_result.confidence_score > 0.8 else 'medium'
        }
    
    def get_confidence_explanation(self, confidence_score):
        """Get confidence explanation"""
        if confidence_score > 0.9:
            return {'level': 'high', 'description': 'Bardzo wysoka pewność rozpoznania'}
        elif confidence_score > 0.7:
            return {'level': 'medium', 'description': 'Średnia pewność rozpoznania'}
        else:
            return {'level': 'low', 'description': 'Niska pewność rozpoznania'}
    
    def suggest_improvements(self, ocr_result):
        """Suggest improvements"""
        return [
            'Użyj lepszej jakości skanu',
            'Upewnij się, że dokument jest dobrze oświetlony',
            'Sprawdź czy dokument nie jest przekrzywiony'
        ]

def get_feedback_system():
    """Get feedback system instance"""
    return OCRFeedbackSystem()