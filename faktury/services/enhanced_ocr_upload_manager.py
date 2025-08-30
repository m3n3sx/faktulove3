"""
Enhanced OCR Upload Manager
"""
import uuid
import logging
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class EnhancedOCRUploadManager:
    def __init__(self):
        self.uploads = {}
        
    def validate_upload_request(self, uploaded_file, user) -> Dict[str, Any]:
        """Validate upload request"""
        try:
            # Basic validation
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff']
            if uploaded_file.content_type not in allowed_types:
                return {'valid': False, 'error': 'Nieobsługiwany typ pliku'}
            
            if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
                return {'valid': False, 'error': 'Plik jest za duży (maksymalnie 10MB)'}
            
            return {
                'valid': True,
                'file_info': {
                    'size': uploaded_file.size,
                    'type': uploaded_file.content_type,
                    'estimated_processing_time': 30
                }
            }
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {'valid': False, 'error': 'Błąd walidacji'}
    
    def queue_upload(self, uploaded_file, user) -> str:
        """Queue upload for processing"""
        upload_id = str(uuid.uuid4())
        
        self.uploads[upload_id] = {
            'id': upload_id,
            'filename': uploaded_file.name,
            'user': user,
            'status': 'queued',
            'created_at': timezone.now(),
            'progress': 0
        }
        
        return upload_id
    
    def get_upload_progress(self, upload_id) -> Optional[Dict[str, Any]]:
        """Get upload progress"""
        return self.uploads.get(upload_id)
    
    def get_user_uploads(self, user, limit=5) -> List[Dict[str, Any]]:
        """Get user's recent uploads"""
        user_uploads = [
            upload for upload in self.uploads.values() 
            if upload['user'] == user
        ]
        return sorted(user_uploads, key=lambda x: x['created_at'], reverse=True)[:limit]
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status"""
        return {
            'total_uploads': len(self.uploads),
            'queued': len([u for u in self.uploads.values() if u['status'] == 'queued']),
            'processing': len([u for u in self.uploads.values() if u['status'] == 'processing']),
            'completed': len([u for u in self.uploads.values() if u['status'] == 'completed'])
        }

def get_upload_manager():
    """Get upload manager instance"""
    return EnhancedOCRUploadManager()