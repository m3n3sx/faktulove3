"""
File Upload Service
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FileValidationError(Exception):
    """File validation error"""
    pass

class FileUploadService:
    def validate_file(self, uploaded_file):
        """Validate uploaded file"""
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff']
        
        if uploaded_file.content_type not in allowed_types:
            raise FileValidationError('Nieobsługiwany typ pliku')
        
        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
            raise FileValidationError('Plik jest za duży')
        
        return True