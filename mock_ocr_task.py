
# Mock OCR Task - dodaj do faktury/tasks.py

from celery import shared_task
import time
import random
from .models import DocumentUpload, OCRResult, OCREngine

@shared_task(bind=True)
def mock_process_document_ocr_task(self, document_upload_id):
    """Mock OCR processing task"""
    
    try:
        document = DocumentUpload.objects.get(id=document_upload_id)
        
        # Symuluj przetwarzanie
        document.processing_status = 'processing'
        document.processing_started_at = timezone.now()
        document.save()
        
        # Symuluj czas przetwarzania
        time.sleep(random.uniform(2, 5))
        
        # Pobierz mock OCR engine
        mock_engine = OCREngine.objects.filter(engine_type='mock', is_active=True).first()
        
        if not mock_engine:
            raise Exception("Mock OCR Engine not found")
        
        # Utwórz mock wynik OCR
        ocr_result = OCRResult.objects.create(
            document=document,
            engine_used=mock_engine,
            confidence_score=mock_engine.configuration.get('mock_confidence', 0.85),
            confidence_level='high',
            extracted_text=mock_engine.configuration.get('mock_text', 'Mock OCR text'),
            extracted_data=mock_engine.configuration.get('mock_data', {}),
            processing_time=random.uniform(2, 5),
            needs_human_review=False
        )
        
        # Zaktualizuj status dokumentu
        document.processing_status = 'completed'
        document.processing_completed_at = timezone.now()
        document.save()
        
        return {
            'success': True,
            'document_id': document_upload_id,
            'ocr_result_id': ocr_result.id,
            'confidence': ocr_result.confidence_score
        }
        
    except Exception as e:
        # Oznacz jako failed
        try:
            document = DocumentUpload.objects.get(id=document_upload_id)
            document.processing_status = 'failed'
            document.error_message = str(e)
            document.save()
        except:
            pass
        
        raise e
