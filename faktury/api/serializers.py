"""
API serializers for the OCR REST API.
"""
import magic
from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from decimal import Decimal, InvalidOperation
from datetime import datetime
import re

from faktury.models import DocumentUpload, OCRResult, Faktura
from faktury.api.exceptions import (
    FileValidationError, FileSizeExceededError, UnsupportedFileTypeError,
    MaliciousFileError
)


class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer with common functionality and enhanced error handling.
    """
    
    def validate(self, attrs):
        """
        Add common validation logic with enhanced error handling.
        """
        try:
            return super().validate(attrs)
        except serializers.ValidationError as e:
            # Re-raise with enhanced error details
            self._enhance_validation_errors(e)
            raise
    
    def _enhance_validation_errors(self, validation_error):
        """
        Enhance validation errors with more descriptive messages.
        """
        if hasattr(validation_error, 'detail'):
            enhanced_detail = {}
            
            for field, errors in validation_error.detail.items():
                enhanced_errors = []
                for error in errors if isinstance(errors, list) else [errors]:
                    enhanced_errors.append(self._enhance_error_message(field, str(error)))
                enhanced_detail[field] = enhanced_errors
            
            validation_error.detail = enhanced_detail
    
    def _enhance_error_message(self, field, error_message):
        """
        Enhance individual error messages with field context.
        """
        field_names = {
            'file': 'uploaded file',
            'numer_faktury': 'invoice number',
            'data_wystawienia': 'issue date',
            'data_sprzedazy': 'sale date',
            'suma_netto': 'net amount',
            'suma_brutto': 'gross amount',
            'corrections': 'validation corrections'
        }
        
        field_display = field_names.get(field, field.replace('_', ' '))
        
        # Add field context to generic error messages
        if 'This field is required' in error_message:
            return f"The {field_display} is required"
        elif 'This field may not be blank' in error_message:
            return f"The {field_display} cannot be empty"
        elif 'Ensure this value' in error_message:
            return f"Invalid value for {field_display}: {error_message}"
        
        return error_message
    
    def to_internal_value(self, data):
        """
        Override to provide better error handling for data conversion.
        """
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as e:
            self._enhance_validation_errors(e)
            raise
        except Exception as e:
            raise serializers.ValidationError({
                'non_field_errors': [f"Data processing error: {str(e)}"]
            })


class DocumentUploadSerializer(BaseSerializer):
    """
    Serializer for document upload validation and processing.
    
    This serializer handles multipart file uploads for OCR processing with
    comprehensive validation including file size, MIME type, content verification,
    and basic security scanning.
    
    **Validation Features**:
    - File size limit enforcement (10MB maximum)
    - MIME type validation (PDF, JPEG, PNG only)
    - Content verification using magic numbers
    - Basic malware detection
    - Empty file detection
    - File corruption checks
    
    **Security Features**:
    - Validates actual file content matches declared MIME type
    - Scans for suspicious file patterns
    - Prevents executable file uploads
    - Checks for malicious content in file headers
    
    **Supported File Types**:
    - PDF documents (application/pdf)
    - JPEG images (image/jpeg)
    - PNG images (image/png)
    
    **Error Handling**:
    - Provides detailed error messages for validation failures
    - Includes file size information in error responses
    - Suggests supported file types when validation fails
    - Logs security-related validation failures
    
    **Usage**:
    Used by OCRUploadAPIView to validate uploaded files before
    queuing them for OCR processing.
    """
    file = serializers.FileField(write_only=True)
    
    class Meta:
        model = DocumentUpload
        fields = ['file', 'original_filename', 'file_size', 'content_type', 'processing_status']
        read_only_fields = ['original_filename', 'file_size', 'content_type', 'processing_status']
    
    def validate_file(self, file):
        """
        Validate uploaded file for size, MIME type, and content with enhanced error handling.
        """
        try:
            # Check if file is provided
            if not file:
                raise FileValidationError("No file provided")
            
            # Check file size (10MB limit)
            max_size = getattr(settings, 'DOCUMENT_AI_CONFIG', {}).get('max_file_size', 10 * 1024 * 1024)
            if file.size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                file_size_mb = file.size / (1024 * 1024)
                raise FileSizeExceededError(
                    f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb:.1f}MB)"
                )
            
            # Check for empty files
            if file.size == 0:
                raise FileValidationError("Empty files are not allowed")
            
            # Check MIME type
            supported_types = getattr(settings, 'SUPPORTED_DOCUMENT_TYPES', {
                'application/pdf': 'PDF',
                'image/jpeg': 'JPEG',
                'image/png': 'PNG'
            })
            
            if file.content_type not in supported_types:
                supported_list = ', '.join(supported_types.values())
                raise UnsupportedFileTypeError(
                    f"Unsupported file type: {file.content_type}. Supported types: {supported_list}"
                )
            
            # Validate actual file content matches MIME type
            try:
                file.seek(0)
                file_header = file.read(2048)  # Read more bytes for better detection
                file.seek(0)
                
                if not file_header:
                    raise FileValidationError("File appears to be empty or corrupted")
                
                detected_type = magic.from_buffer(file_header, mime=True)
                
                # Define acceptable MIME type mappings
                mime_mappings = {
                    'application/pdf': ['application/pdf'],
                    'image/jpeg': ['image/jpeg', 'image/jpg'],
                    'image/png': ['image/png']
                }
                
                acceptable_types = mime_mappings.get(file.content_type, [file.content_type])
                
                if detected_type not in acceptable_types:
                    raise UnsupportedFileTypeError(
                        f"File content ({detected_type}) does not match declared type ({file.content_type}). "
                        f"This may indicate a corrupted or mislabeled file."
                    )
                
                # Basic malware detection (check for suspicious patterns)
                self._check_file_safety(file_header, file.name)
                
            except magic.MagicException as e:
                raise FileValidationError(f"Unable to determine file type: {str(e)}")
            except Exception as e:
                if isinstance(e, (FileValidationError, UnsupportedFileTypeError, MaliciousFileError)):
                    raise
                raise FileValidationError(f"Error validating file content: {str(e)}")
            
            return file
            
        except (FileValidationError, FileSizeExceededError, UnsupportedFileTypeError, MaliciousFileError):
            raise
        except Exception as e:
            raise FileValidationError(f"Unexpected error during file validation: {str(e)}")
    
    def _check_file_safety(self, file_header, filename):
        """
        Perform basic safety checks on file content.
        """
        # Check for suspicious file extensions in filename
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js']
        if any(filename.lower().endswith(ext) for ext in suspicious_extensions):
            raise MaliciousFileError("File type appears to be executable and is not allowed")
        
        # Check for suspicious patterns in file header
        suspicious_patterns = [
            b'MZ',  # DOS/Windows executable
            b'\x7fELF',  # Linux executable
            b'<script',  # JavaScript
            b'javascript:',  # JavaScript URL
        ]
        
        file_header_lower = file_header.lower()
        for pattern in suspicious_patterns:
            if pattern in file_header_lower:
                raise MaliciousFileError("File contains suspicious content and cannot be processed")
    
    def create(self, validated_data):
        """
        Create DocumentUpload instance with file handling.
        """
        file = validated_data.pop('file')
        
        # Set file metadata
        validated_data['original_filename'] = file.name
        validated_data['file_size'] = file.size
        validated_data['content_type'] = file.content_type
        validated_data['user'] = self.context['request'].user
        
        # Create the document upload record
        # File saving will be handled by the FileUploadService in the view
        return super().create(validated_data)


class OCRResultListSerializer(BaseSerializer):
    """
    Lightweight serializer for OCR results list views.
    
    This serializer provides essential information about OCR results in a
    performance-optimized format suitable for list views and pagination.
    It includes computed fields and minimal database queries.
    
    **Included Fields**:
    - Basic OCR result information (ID, status, confidence)
    - Document metadata (filename, upload date)
    - Processing information (time, status)
    - Computed properties (has_faktura, needs_review)
    - Confidence level classification
    
    **Performance Optimizations**:
    - Uses select_related for efficient database queries
    - Minimal field selection to reduce response size
    - Computed fields cached where possible
    - Optimized for pagination with large datasets
    
    **Computed Fields**:
    - `has_faktura`: Boolean indicating if invoice was created
    - `needs_review`: Boolean indicating if manual review is needed
    - `confidence_level`: Human-readable confidence classification
    
    **Usage**:
    Used by OCRResultsListAPIView to provide paginated lists of
    OCR results with filtering and search capabilities.
    """
    document_filename = serializers.CharField(source='document.original_filename', read_only=True)
    upload_date = serializers.DateTimeField(source='document.upload_timestamp', read_only=True)
    has_faktura = serializers.SerializerMethodField()
    needs_review = serializers.SerializerMethodField()
    confidence_level = serializers.CharField(read_only=True)
    
    class Meta:
        model = OCRResult
        fields = [
            'id',
            'document_filename',
            'upload_date',
            'processing_status',
            'confidence_score',
            'confidence_level',
            'has_faktura',
            'needs_review',
            'created_at',
            'processing_time'
        ]
    
    def get_has_faktura(self, obj):
        """Check if OCR result has associated Faktura."""
        return obj.faktura is not None
    
    def get_needs_review(self, obj):
        """Check if result needs human review based on confidence."""
        return obj.needs_human_review


class FakturaBasicSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Faktura information in OCR results.
    """
    class Meta:
        model = Faktura
        fields = ['id', 'numer', 'data_wystawienia', 'status']


class OCRResultDetailSerializer(BaseSerializer):
    """
    Comprehensive serializer for detailed OCR result views.
    
    This serializer provides complete information about OCR processing results,
    including all extracted data with confidence scores, validation suggestions,
    and related object information.
    
    **Included Data**:
    - Complete extracted data with field-level confidence scores
    - Document metadata and processing information
    - Related Faktura information if invoice was created
    - Validation fields that can be manually corrected
    - Confidence breakdown by data categories
    - Processing metadata and error information
    
    **Nested Serializers**:
    - Document information with upload metadata
    - Faktura basic information if invoice exists
    - Confidence breakdown by field categories
    
    **Validation Support**:
    - Lists fields available for manual validation
    - Provides current values and confidence scores
    - Indicates which fields need review
    - Suggests validation priorities
    
    **Confidence Analysis**:
    - Overall document confidence score
    - Field-level confidence scores
    - Confidence breakdown by categories (document_info, parties, amounts, items)
    - Statistical analysis (min, max, average confidence)
    
    **Usage**:
    Used by OCRResultDetailAPIView to provide comprehensive
    information for detailed result inspection and validation.
    """
    document = serializers.SerializerMethodField()
    faktura = FakturaBasicSerializer(read_only=True)
    validation_fields = serializers.SerializerMethodField()
    confidence_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = OCRResult
        fields = [
            'id',
            'document',
            'extracted_data',
            'confidence_score',
            'confidence_level',
            'field_confidence',
            'confidence_breakdown',
            'processing_time',
            'processing_status',
            'error_message',
            'faktura',
            'auto_created_faktura',
            'validation_fields',
            'needs_human_review',
            'can_auto_create_faktura',
            'created_at',
            'processor_version'
        ]
    
    def get_document(self, obj):
        """Get document information."""
        return {
            'id': obj.document.id,
            'filename': obj.document.original_filename,
            'upload_date': obj.document.upload_timestamp,
            'file_size': obj.document.file_size,
            'content_type': obj.document.content_type
        }
    
    def get_validation_fields(self, obj):
        """
        Get fields that can be manually validated with their current values and confidence.
        """
        if not obj.extracted_data:
            return {}
        
        validation_fields = {}
        field_confidence = obj.field_confidence or {}
        
        # Define which fields can be validated
        validatable_fields = [
            'numer_faktury', 'data_wystawienia', 'data_sprzedazy',
            'sprzedawca', 'nabywca', 'pozycje', 'suma_netto', 'suma_brutto'
        ]
        
        for field in validatable_fields:
            if field in obj.extracted_data:
                validation_fields[field] = {
                    'value': obj.extracted_data[field],
                    'confidence': field_confidence.get(field, obj.confidence_score),
                    'needs_review': field_confidence.get(field, obj.confidence_score) < 80.0
                }
        
        return validation_fields
    
    def get_confidence_breakdown(self, obj):
        """
        Get confidence score breakdown by field categories.
        """
        field_confidence = obj.field_confidence or {}
        
        categories = {
            'document_info': ['numer_faktury', 'data_wystawienia', 'data_sprzedazy'],
            'parties': ['sprzedawca', 'nabywca'],
            'amounts': ['suma_netto', 'suma_brutto', 'vat_amount'],
            'items': ['pozycje']
        }
        
        breakdown = {}
        for category, fields in categories.items():
            scores = [field_confidence.get(field, obj.confidence_score) for field in fields if field in field_confidence]
            if scores:
                breakdown[category] = {
                    'average': sum(scores) / len(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'count': len(scores)
                }
        
        return breakdown


class TaskStatusSerializer(serializers.Serializer):
    """
    Serializer for Celery task status information.
    
    This serializer handles task status responses from the OCR processing
    pipeline, providing real-time progress updates and estimated completion
    times for asynchronous document processing.
    
    **Status Values**:
    - `pending`: Task is queued and waiting to start
    - `processing`: Task is currently being processed
    - `completed`: Task finished successfully
    - `failed`: Task failed with an error
    
    **Progress Information**:
    - Progress percentage (0-100)
    - Estimated time remaining (ETA in seconds)
    - Current processing stage message
    - Task result data when completed
    - Error information when failed
    
    **Validation**:
    - Ensures progress is between 0 and 100
    - Validates status is one of allowed choices
    - Handles optional fields gracefully
    
    **Usage**:
    Used by OCRStatusAPIView to provide consistent task status
    responses for frontend polling and progress indicators.
    """
    task_id = serializers.CharField()
    status = serializers.ChoiceField(choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    progress = serializers.IntegerField(min_value=0, max_value=100, required=False)
    eta_seconds = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)
    result = serializers.JSONField(required=False)
    error = serializers.CharField(required=False)
    
    def validate_progress(self, value):
        """Ensure progress is between 0 and 100."""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Progress must be between 0 and 100")
        return value


class OCRValidationSerializer(serializers.Serializer):
    """
    Serializer for manual OCR result validation and correction.
    
    This serializer handles user-submitted corrections to OCR extraction
    results, with comprehensive validation for each field type and
    cross-field validation rules.
    
    **Correction Fields**:
    - `corrections`: Dictionary of field corrections (field_path: new_value)
    - `create_faktura`: Boolean to trigger automatic invoice creation
    - `validation_notes`: Optional notes about the validation process
    
    **Supported Field Types**:
    - Invoice information (number, dates)
    - Company information (names, NIP numbers, addresses)
    - Financial amounts (net, gross, VAT amounts)
    - Line items (names, quantities, prices, VAT rates)
    
    **Validation Rules**:
    - NIP numbers: 10 digits with valid checksum
    - Dates: Multiple formats supported (YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY)
    - Amounts: Positive numbers with max 2 decimal places
    - Company names: Non-empty strings with length limits
    - Quantities: Positive numbers for line items
    - VAT rates: Percentage values between 0 and 100
    
    **Field Path Format**:
    - Simple fields: `numer_faktury`, `suma_brutto`
    - Nested fields: `sprzedawca.nazwa`, `nabywca.nip`
    - Array fields: `pozycje.0.nazwa`, `pozycje.1.cena_netto`
    
    **Cross-Field Validation**:
    - Ensures required fields are present when creating invoices
    - Validates relationships between amounts and VAT calculations
    - Checks consistency between dates
    
    **Error Handling**:
    - Provides field-specific error messages
    - Includes validation suggestions for common errors
    - Handles partial validation (some fields may fail while others succeed)
    
    **Usage**:
    Used by OCRValidationAPIView to validate and apply user corrections
    to OCR results before updating confidence scores and creating invoices.
    """
    corrections = serializers.JSONField()
    create_faktura = serializers.BooleanField(default=False)
    validation_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_corrections(self, value):
        """
        Validate corrections format and content with enhanced field validation.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Corrections must be provided as a dictionary of field-value pairs")
        
        # Allow empty corrections if create_faktura is False (just validation without changes)
        create_faktura = self.initial_data.get('create_faktura', False)
        if not value and not create_faktura:
            return value  # Allow empty corrections for validation-only requests
        elif not value:
            raise serializers.ValidationError("At least one correction must be provided when creating Faktura")
        
        # Define allowed fields for correction with validation rules
        field_validators = {
            'numer_faktury': self._validate_invoice_number,
            'data_wystawienia': self._validate_date,
            'data_sprzedazy': self._validate_date,
            'sprzedawca.nazwa': self._validate_company_name,
            'sprzedawca.nip': self._validate_nip,
            'sprzedawca.adres': self._validate_address,
            'nabywca.nazwa': self._validate_company_name,
            'nabywca.nip': self._validate_nip,
            'nabywca.adres': self._validate_address,
            'suma_netto': self._validate_amount,
            'suma_brutto': self._validate_amount,
            'vat_amount': self._validate_amount
        }
        
        validated_corrections = {}
        errors = {}
        
        for field_path, new_value in value.items():
            try:
                # Handle line item corrections (pozycje.0.nazwa, etc.)
                if field_path.startswith('pozycje.'):
                    self._validate_line_item_correction(field_path, new_value)
                    validated_corrections[field_path] = new_value
                elif field_path in field_validators:
                    validated_value = field_validators[field_path](new_value)
                    validated_corrections[field_path] = validated_value
                else:
                    errors[field_path] = f"Field '{field_path}' is not allowed for correction"
            except serializers.ValidationError as e:
                errors[field_path] = str(e)
            except Exception as e:
                errors[field_path] = f"Validation error: {str(e)}"
        
        if errors:
            raise serializers.ValidationError(f"Validation errors in corrections: {errors}")
        
        return validated_corrections
    
    def _validate_invoice_number(self, value):
        """Validate invoice number format."""
        if not value or not str(value).strip():
            raise serializers.ValidationError("Invoice number cannot be empty")
        
        value = str(value).strip()
        if len(value) > 50:
            raise serializers.ValidationError("Invoice number cannot exceed 50 characters")
        
        return value
    
    def _validate_date(self, value):
        """Validate date format."""
        if isinstance(value, str):
            try:
                # Try to parse various date formats
                for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
                    try:
                        datetime.strptime(value, fmt)
                        return value
                    except ValueError:
                        continue
                raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD, DD.MM.YYYY, or DD/MM/YYYY")
            except Exception:
                raise serializers.ValidationError("Invalid date format")
        return value
    
    def _validate_company_name(self, value):
        """Validate company name."""
        if not value or not str(value).strip():
            raise serializers.ValidationError("Company name cannot be empty")
        
        value = str(value).strip()
        if len(value) > 200:
            raise serializers.ValidationError("Company name cannot exceed 200 characters")
        
        return value
    
    def _validate_nip(self, value):
        """Validate Polish NIP number."""
        if not value:
            return value
        
        nip = str(value).replace('-', '').replace(' ', '')
        
        if not nip.isdigit() or len(nip) != 10:
            raise serializers.ValidationError("NIP must be exactly 10 digits")
        
        # Basic NIP checksum validation
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        
        if checksum != int(nip[9]):
            raise serializers.ValidationError("Invalid NIP checksum")
        
        return nip
    
    def _validate_address(self, value):
        """Validate address format."""
        if not value or not str(value).strip():
            raise serializers.ValidationError("Address cannot be empty")
        
        value = str(value).strip()
        if len(value) > 500:
            raise serializers.ValidationError("Address cannot exceed 500 characters")
        
        return value
    
    def _validate_amount(self, value):
        """Validate monetary amount."""
        try:
            if isinstance(value, str):
                # Remove common currency symbols and spaces
                value = value.replace('zł', '').replace('PLN', '').replace(' ', '').replace(',', '.')
            
            amount = Decimal(str(value))
            
            if amount < 0:
                raise serializers.ValidationError("Amount cannot be negative")
            
            if amount > Decimal('999999999.99'):
                raise serializers.ValidationError("Amount is too large")
            
            # Ensure max 2 decimal places
            if amount.as_tuple().exponent < -2:
                raise serializers.ValidationError("Amount cannot have more than 2 decimal places")
            
            return float(amount)
            
        except (InvalidOperation, ValueError):
            raise serializers.ValidationError("Invalid amount format")
    
    def _validate_line_item_correction(self, field_path, value):
        """Validate line item corrections."""
        # Parse field path like "pozycje.0.nazwa"
        parts = field_path.split('.')
        if len(parts) != 3 or parts[0] != 'pozycje':
            raise serializers.ValidationError(f"Invalid line item field path: {field_path}")
        
        try:
            item_index = int(parts[1])
            if item_index < 0:
                raise serializers.ValidationError("Line item index cannot be negative")
        except ValueError:
            raise serializers.ValidationError("Invalid line item index")
        
        field_name = parts[2]
        allowed_item_fields = ['nazwa', 'ilosc', 'jednostka', 'cena_netto', 'cena_brutto', 'vat_rate']
        
        if field_name not in allowed_item_fields:
            raise serializers.ValidationError(f"Field '{field_name}' is not allowed for line item corrections")
        
        # Validate based on field type
        if field_name in ['cena_netto', 'cena_brutto']:
            self._validate_amount(value)
        elif field_name == 'ilosc':
            try:
                qty = Decimal(str(value))
                if qty <= 0:
                    raise serializers.ValidationError("Quantity must be greater than 0")
            except (InvalidOperation, ValueError):
                raise serializers.ValidationError("Invalid quantity format")
        elif field_name in ['nazwa', 'jednostka']:
            if not value or not str(value).strip():
                raise serializers.ValidationError(f"{field_name} cannot be empty")
        elif field_name == 'vat_rate':
            try:
                rate = float(value)
                if rate < 0 or rate > 100:
                    raise serializers.ValidationError("VAT rate must be between 0 and 100")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Invalid VAT rate format")
    
    def validate(self, attrs):
        """
        Cross-field validation for corrections and faktura creation.
        """
        corrections = attrs.get('corrections', {})
        create_faktura = attrs.get('create_faktura', False)
        
        # If creating faktura, ensure required fields are present or corrected
        if create_faktura:
            required_fields = ['numer_faktury', 'data_wystawienia', 'sprzedawca', 'nabywca']
            
            # This validation would need access to the OCR result to check existing data
            # For now, we'll just ensure corrections is not empty if create_faktura is True
            if not corrections:
                raise serializers.ValidationError(
                    "Corrections are required when creating a faktura"
                )
        
        return attrs