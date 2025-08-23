"""
Custom exception classes for OCR REST API.

This module defines API-specific exceptions that provide consistent error handling
across all OCR API endpoints with proper HTTP status codes and error messages.
"""

from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class OCRAPIException(Exception):
    """Base exception class for OCR API errors."""
    
    default_message = "An error occurred in the OCR API"
    default_code = "OCR_API_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def __init__(self, message=None, code=None, status_code=None, details=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.status_code = status_code or self.status_code
        self.details = details or {}
        super().__init__(self.message)


class FileValidationError(OCRAPIException):
    """Exception raised when file validation fails."""
    
    default_message = "File validation failed"
    default_code = "FILE_VALIDATION_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST


class FileSizeExceededError(FileValidationError):
    """Exception raised when uploaded file exceeds size limit."""
    
    default_message = "File size exceeds the maximum allowed limit"
    default_code = "FILE_SIZE_EXCEEDED"
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


class UnsupportedFileTypeError(FileValidationError):
    """Exception raised when uploaded file type is not supported."""
    
    default_message = "File type is not supported"
    default_code = "UNSUPPORTED_FILE_TYPE"
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


class MaliciousFileError(FileValidationError):
    """Exception raised when uploaded file is detected as malicious."""
    
    default_message = "File appears to be malicious and cannot be processed"
    default_code = "MALICIOUS_FILE_DETECTED"
    status_code = status.HTTP_400_BAD_REQUEST


class OCRProcessingError(OCRAPIException):
    """Exception raised when OCR processing fails."""
    
    default_message = "OCR processing failed"
    default_code = "OCR_PROCESSING_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class TaskNotFoundError(OCRAPIException):
    """Exception raised when requested task is not found."""
    
    default_message = "Task not found"
    default_code = "TASK_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class ResultNotFoundError(OCRAPIException):
    """Exception raised when requested OCR result is not found."""
    
    default_message = "OCR result not found"
    default_code = "RESULT_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class UnauthorizedAccessError(OCRAPIException):
    """Exception raised when user tries to access unauthorized resources."""
    
    default_message = "You don't have permission to access this resource"
    default_code = "UNAUTHORIZED_ACCESS"
    status_code = status.HTTP_403_FORBIDDEN


class RateLimitExceededError(OCRAPIException):
    """Exception raised when rate limit is exceeded."""
    
    default_message = "Rate limit exceeded. Please try again later"
    default_code = "RATE_LIMIT_EXCEEDED"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


class ValidationError(OCRAPIException):
    """Exception raised when data validation fails."""
    
    default_message = "Validation failed"
    default_code = "VALIDATION_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST


class QuotaExceededError(OCRAPIException):
    """Exception raised when user quota is exceeded."""
    
    default_message = "Upload quota exceeded"
    default_code = "QUOTA_EXCEEDED"
    status_code = status.HTTP_403_FORBIDDEN


class ServiceUnavailableError(OCRAPIException):
    """Exception raised when OCR service is temporarily unavailable."""
    
    default_message = "OCR service is temporarily unavailable"
    default_code = "SERVICE_UNAVAILABLE"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class CeleryTaskError(OCRAPIException):
    """Exception raised when Celery task operations fail."""
    
    default_message = "Task processing error"
    default_code = "CELERY_TASK_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    
    This handler catches OCR API exceptions and formats them according to
    the standard API response format. It also logs errors appropriately.
    """
    # Get the standard error response
    response = exception_handler(exc, context)
    
    # Handle OCR API exceptions
    if isinstance(exc, OCRAPIException):
        custom_response_data = {
            'success': False,
            'error': {
                'code': exc.code,
                'message': exc.message,
                'details': exc.details
            },
            'timestamp': None  # Will be set by response formatter
        }
        
        # Log the error
        logger.error(
            f"OCR API Error: {exc.code} - {exc.message}",
            extra={
                'exception_type': type(exc).__name__,
                'status_code': exc.status_code,
                'details': exc.details,
                'request_path': context.get('request', {}).get('path'),
                'user': getattr(context.get('request', {}), 'user', None)
            }
        )
        
        return Response(custom_response_data, status=exc.status_code)
    
    # Handle DRF validation errors
    if response is not None:
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data = {
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Validation failed',
                    'details': response.data
                },
                'timestamp': None  # Will be set by response formatter
            }
            response.data = custom_response_data
            
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data = {
                'success': False,
                'error': {
                    'code': 'AUTHENTICATION_REQUIRED',
                    'message': 'Authentication credentials were not provided',
                    'details': {}
                },
                'timestamp': None
            }
            response.data = custom_response_data
            
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data = {
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'You do not have permission to perform this action',
                    'details': {}
                },
                'timestamp': None
            }
            response.data = custom_response_data
            
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data = {
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'The requested resource was not found',
                    'details': {}
                },
                'timestamp': None
            }
            response.data = custom_response_data
            
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_response_data = {
                'success': False,
                'error': {
                    'code': 'METHOD_NOT_ALLOWED',
                    'message': 'Method not allowed',
                    'details': {'allowed_methods': response.data.get('detail', '')}
                },
                'timestamp': None
            }
            response.data = custom_response_data
    
    return response