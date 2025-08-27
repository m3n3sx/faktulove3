"""
File Upload Service for OCR Document Processing
"""

import os
import logging
import hashlib
from typing import Tuple, Optional
from pathlib import Path
import magic
from PIL import Image
import pdf2image

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

from ..models import DocumentUpload

logger = logging.getLogger(__name__)


class FileUploadService:
    """Service for handling file uploads and validation"""
    
    def __init__(self):
        self.supported_types = settings.SUPPORTED_DOCUMENT_TYPES
        self.max_file_size = settings.OCR_CONFIG['max_file_size']
        
        # Create upload directory if it doesn't exist
        self.upload_dir = Path(settings.MEDIA_ROOT) / 'ocr_uploads'
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def handle_upload(self, uploaded_file: UploadedFile, user: User) -> DocumentUpload:
        """
        Handle file upload with validation and storage
        
        Args:
            uploaded_file: Django UploadedFile instance
            user: User who uploaded the file
            
        Returns:
            DocumentUpload instance
            
        Raises:
            ValidationError: If file validation fails
        """
        # Validate file
        self._validate_file(uploaded_file)
        
        # Generate secure filename
        filename = self._generate_secure_filename(uploaded_file.name)
        
        # Save file to disk
        file_path = self._save_file(uploaded_file, filename)
        
        # Create DocumentUpload record
        document_upload = DocumentUpload.objects.create(
            user=user,
            original_filename=uploaded_file.name,
            file_path=str(file_path),
            file_size=uploaded_file.size,
            content_type=uploaded_file.content_type,
        )
        
        logger.info(f"File uploaded successfully: {document_upload.id} - {uploaded_file.name}")
        
        # Trigger OCR processing automatically
        self._trigger_ocr_processing(document_upload)
        
        return document_upload
    
    def _validate_file(self, uploaded_file: UploadedFile) -> None:
        """Validate uploaded file"""
        
        # Check file size
        if uploaded_file.size > self.max_file_size:
            raise ValidationError(
                f"File size ({uploaded_file.size} bytes) exceeds maximum allowed size "
                f"({self.max_file_size} bytes)"
            )
        
        # Validate MIME type
        if uploaded_file.content_type not in self.supported_types:
            supported_list = ', '.join(self.supported_types.keys())
            raise ValidationError(
                f"Unsupported file type: {uploaded_file.content_type}. "
                f"Supported types: {supported_list}"
            )
        
        # Validate file content matches MIME type
        try:
            # Read first chunk to detect actual file type
            uploaded_file.seek(0)
            file_header = uploaded_file.read(1024)
            uploaded_file.seek(0)
            
            detected_type = magic.from_buffer(file_header, mime=True)
            
            if detected_type != uploaded_file.content_type:
                logger.warning(
                    f"MIME type mismatch: declared={uploaded_file.content_type}, "
                    f"detected={detected_type}"
                )
                
                # Allow some common mismatches
                allowed_mismatches = {
                    'application/pdf': ['application/pdf'],
                    'image/jpeg': ['image/jpeg', 'image/jpg'],
                    'image/png': ['image/png'],
                    'image/tiff': ['image/tiff', 'image/tif'],
                }
                
                declared_type = uploaded_file.content_type
                if declared_type in allowed_mismatches:
                    if detected_type not in allowed_mismatches[declared_type]:
                        raise ValidationError(
                            f"File content does not match declared type. "
                            f"Expected: {declared_type}, Detected: {detected_type}"
                        )
        
        except Exception as e:
            logger.warning(f"File content validation failed: {e}")
            # Don't fail upload for validation issues, just log
    
    def _generate_secure_filename(self, original_filename: str) -> str:
        """Generate secure filename with timestamp and hash"""
        
        # Extract file extension
        file_ext = Path(original_filename).suffix.lower()
        
        # Create hash of original filename + timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        hash_input = f"{original_filename}_{timestamp}".encode('utf-8')
        file_hash = hashlib.md5(hash_input).hexdigest()[:8]
        
        return f"{timestamp}_{file_hash}{file_ext}"
    
    def _save_file(self, uploaded_file: UploadedFile, filename: str) -> Path:
        """Save uploaded file to disk"""
        
        # Create date-based subdirectory
        date_subdir = timezone.now().strftime('%Y/%m/%d')
        save_dir = self.upload_dir / date_subdir
        save_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = save_dir / filename
        
        # Write file to disk
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        return file_path
    
    def get_file_content(self, document_upload: DocumentUpload) -> bytes:
        """Get file content for OCR processing"""
        
        file_path = Path(document_upload.file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def convert_to_images(self, document_upload: DocumentUpload) -> list:
        """Convert document to images if needed (for PDFs)"""
        
        if document_upload.content_type != 'application/pdf':
            return [document_upload.file_path]
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(
                document_upload.file_path,
                dpi=300,  # High DPI for better OCR
                fmt='jpeg'
            )
            
            image_paths = []
            base_path = Path(document_upload.file_path)
            
            for i, image in enumerate(images):
                image_path = base_path.parent / f"{base_path.stem}_page_{i+1}.jpg"
                image.save(image_path, 'JPEG', quality=95)
                image_paths.append(str(image_path))
            
            return image_paths
            
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise
    
    def optimize_image_for_ocr(self, image_path: str) -> str:
        """Optimize image for better OCR results"""
        
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (Document AI has size limits)
                max_dimension = 2048
                if max(img.size) > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                # Enhance contrast for better OCR
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
                
                # Save optimized image
                optimized_path = image_path.replace('.jpg', '_optimized.jpg')
                img.save(optimized_path, 'JPEG', quality=95, optimize=True)
                
                return optimized_path
                
        except Exception as e:
            logger.warning(f"Image optimization failed: {e}")
            return image_path  # Return original if optimization fails
    
    def cleanup_file(self, document_upload: DocumentUpload) -> None:
        """Clean up uploaded file and related files"""
        
        try:
            file_path = Path(document_upload.file_path)
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Cleaned up file: {file_path}")
            
            # Clean up any generated images
            parent_dir = file_path.parent
            base_name = file_path.stem
            
            for related_file in parent_dir.glob(f"{base_name}_*"):
                related_file.unlink()
                logger.info(f"Cleaned up related file: {related_file}")
                
        except Exception as e:
            logger.error(f"File cleanup failed: {e}")
    
    def get_file_info(self, document_upload: DocumentUpload) -> dict:
        """Get detailed file information"""
        
        file_path = Path(document_upload.file_path)
        
        info = {
            'exists': file_path.exists(),
            'size': document_upload.file_size,
            'content_type': document_upload.content_type,
            'original_name': document_upload.original_filename,
            'upload_time': document_upload.upload_timestamp,
            'processing_status': document_upload.processing_status,
        }
        
        if file_path.exists():
            stat = file_path.stat()
            info.update({
                'actual_size': stat.st_size,
                'modified_time': timezone.datetime.fromtimestamp(stat.st_mtime),
                'is_readable': os.access(file_path, os.R_OK),
            })
        
        return info
    
    def _trigger_ocr_processing(self, document_upload):
        """Trigger OCR processing for uploaded document"""
        try:
            # Import here to avoid circular imports
            from .ocr_service_factory import get_ocr_service
            from ..models import OCRResult
            
            logger.info(f"Starting OCR processing for document {document_upload.id}")
            
            # Mark document as processing
            document_upload.mark_processing_started()
            
            # Get file content
            file_content = self.get_file_content(document_upload)
            
            # Get OCR service
            ocr_service = get_ocr_service()
            
            # Process document
            extracted_data = ocr_service.process_invoice(
                file_content, 
                document_upload.content_type
            )
            
            # Create OCR result
            ocr_result = OCRResult.objects.create(
                document=document_upload,
                raw_text=extracted_data.get('raw_text', ''),
                extracted_data=self._convert_to_faktura_format(extracted_data),
                confidence_score=extracted_data.get('confidence_score', 0.0),
                processing_time=extracted_data.get('processing_time', 0.0),
                field_confidence=extracted_data.get('field_confidence', {}),
                processor_version=extracted_data.get('processor_version', ''),
                processing_location=extracted_data.get('processing_location', ''),
                processing_status='pending'  # Will trigger automatic processing via signals
            )
            
            # Mark document as completed
            document_upload.mark_processing_completed()
            
            logger.info(f"OCR processing completed for document {document_upload.id}, created OCR result {ocr_result.id}")
            
        except Exception as e:
            logger.error(f"OCR processing failed for document {document_upload.id}: {str(e)}")
            document_upload.mark_processing_failed(str(e))
    
    def _convert_to_faktura_format(self, extracted_data):
        """Convert Document AI format to our Faktura format"""
        return {
            'numer_faktury': extracted_data.get('invoice_number', ''),
            'data_wystawienia': extracted_data.get('invoice_date', ''),
            'data_sprzedazy': extracted_data.get('invoice_date', ''),  # Use same date if not specified
            'sprzedawca_nazwa': extracted_data.get('supplier_name', ''),
            'sprzedawca_nip': extracted_data.get('supplier_nip', ''),
            'sprzedawca_ulica': self._extract_street_from_address(extracted_data.get('supplier_address', '')),
            'sprzedawca_numer_domu': '1',  # Default, could be extracted from address
            'sprzedawca_kod_pocztowy': self._extract_postal_code(extracted_data.get('supplier_address', '')),
            'sprzedawca_miejscowosc': extracted_data.get('supplier_city', ''),
            'nabywca_nazwa': extracted_data.get('buyer_name', ''),
            'nabywca_nip': extracted_data.get('buyer_nip', ''),
            'pozycje': self._convert_line_items(extracted_data.get('line_items', [])),
            'suma_brutto': str(extracted_data.get('total_amount', '0.00')),
            'suma_netto': str(extracted_data.get('net_amount', '0.00')),
            'sposob_platnosci': 'przelew',  # Default
            'termin_platnosci_dni': 14,  # Default
            'waluta': extracted_data.get('currency', 'PLN'),
        }
    
    def _convert_line_items(self, line_items):
        """Convert line items to our format"""
        converted_items = []
        
        for item in line_items:
            converted_item = {
                'nazwa': item.get('description', 'Pozycja'),
                'ilosc': item.get('quantity', '1'),
                'jednostka': 'szt',  # Default
                'cena_netto': item.get('unit_price', '0.00'),
                'vat': self._extract_vat_rate(item.get('vat_rate', '23%')),
            }
            converted_items.append(converted_item)
        
        # If no line items found, create a default one
        if not converted_items:
            converted_items.append({
                'nazwa': 'Usługa/Towar',
                'ilosc': '1',
                'jednostka': 'szt',
                'cena_netto': '0.00',
                'vat': '23'
            })
        
        return converted_items
    
    def _extract_street_from_address(self, address):
        """Extract street from full address"""
        if not address:
            return ''
        
        # Simple extraction - take first line
        lines = address.split('\n')
        return lines[0].strip() if lines else ''
    
    def _extract_postal_code(self, address):
        """Extract postal code from address"""
        if not address:
            return ''
        
        import re
        # Polish postal code pattern: XX-XXX
        match = re.search(r'\d{2}-\d{3}', address)
        return match.group(0) if match else ''
    
    def _extract_vat_rate(self, vat_string):
        """Extract VAT rate number from string like '23%'"""
        if not vat_string:
            return '23'
        
        import re
        match = re.search(r'(\d+)', str(vat_string))
        return match.group(1) if match else '23'


class FileValidationError(ValidationError):
    """Custom exception for file validation errors"""
    pass


def validate_document_file(uploaded_file: UploadedFile) -> None:
    """Standalone function to validate document files"""
    service = FileUploadService()
    service._validate_file(uploaded_file)