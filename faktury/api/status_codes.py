"""
HTTP status code mappings and utilities for OCR REST API.

This module provides consistent HTTP status code handling across all API endpoints
with proper mapping for different error types and success scenarios.
"""

from rest_framework import status
from enum import Enum


class APIStatusCode(Enum):
    """
    Enumeration of API-specific status codes with descriptions.
    """
    
    # Success codes (2xx)
    SUCCESS = (status.HTTP_200_OK, "Operation completed successfully")
    CREATED = (status.HTTP_201_CREATED, "Resource created successfully")
    ACCEPTED = (status.HTTP_202_ACCEPTED, "Request accepted for processing")
    NO_CONTENT = (status.HTTP_204_NO_CONTENT, "Operation completed, no content to return")
    
    # Client error codes (4xx)
    BAD_REQUEST = (status.HTTP_400_BAD_REQUEST, "Invalid request data")
    UNAUTHORIZED = (status.HTTP_401_UNAUTHORIZED, "Authentication required")
    FORBIDDEN = (status.HTTP_403_FORBIDDEN, "Access denied")
    NOT_FOUND = (status.HTTP_404_NOT_FOUND, "Resource not found")
    METHOD_NOT_ALLOWED = (status.HTTP_405_METHOD_NOT_ALLOWED, "HTTP method not allowed")
    NOT_ACCEPTABLE = (status.HTTP_406_NOT_ACCEPTABLE, "Requested format not acceptable")
    CONFLICT = (status.HTTP_409_CONFLICT, "Resource conflict")
    GONE = (status.HTTP_410_GONE, "Resource no longer available")
    PRECONDITION_FAILED = (status.HTTP_412_PRECONDITION_FAILED, "Precondition failed")
    PAYLOAD_TOO_LARGE = (status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Request payload too large")
    UNSUPPORTED_MEDIA_TYPE = (status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported media type")
    UNPROCESSABLE_ENTITY = (status.HTTP_422_UNPROCESSABLE_ENTITY, "Validation failed")
    TOO_MANY_REQUESTS = (status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded")
    
    # Server error codes (5xx)
    INTERNAL_SERVER_ERROR = (status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
    NOT_IMPLEMENTED = (status.HTTP_501_NOT_IMPLEMENTED, "Feature not implemented")
    BAD_GATEWAY = (status.HTTP_502_BAD_GATEWAY, "Bad gateway")
    SERVICE_UNAVAILABLE = (status.HTTP_503_SERVICE_UNAVAILABLE, "Service temporarily unavailable")
    GATEWAY_TIMEOUT = (status.HTTP_504_GATEWAY_TIMEOUT, "Gateway timeout")
    
    @property
    def code(self):
        """Get the HTTP status code."""
        return self.value[0]
    
    @property
    def message(self):
        """Get the default message for this status code."""
        return self.value[1]


class ErrorCodeMapping:
    """
    Maps application error codes to appropriate HTTP status codes.
    """
    
    # File validation errors
    FILE_VALIDATION_ERROR = APIStatusCode.BAD_REQUEST
    FILE_SIZE_EXCEEDED = APIStatusCode.PAYLOAD_TOO_LARGE
    UNSUPPORTED_FILE_TYPE = APIStatusCode.UNSUPPORTED_MEDIA_TYPE
    MALICIOUS_FILE_DETECTED = APIStatusCode.BAD_REQUEST
    FILE_CORRUPTED = APIStatusCode.BAD_REQUEST
    FILE_EMPTY = APIStatusCode.BAD_REQUEST
    
    # Authentication and authorization errors
    AUTHENTICATION_REQUIRED = APIStatusCode.UNAUTHORIZED
    INVALID_CREDENTIALS = APIStatusCode.UNAUTHORIZED
    TOKEN_EXPIRED = APIStatusCode.UNAUTHORIZED
    TOKEN_INVALID = APIStatusCode.UNAUTHORIZED
    PERMISSION_DENIED = APIStatusCode.FORBIDDEN
    UNAUTHORIZED_ACCESS = APIStatusCode.FORBIDDEN
    QUOTA_EXCEEDED = APIStatusCode.FORBIDDEN
    
    # Resource errors
    RESOURCE_NOT_FOUND = APIStatusCode.NOT_FOUND
    TASK_NOT_FOUND = APIStatusCode.NOT_FOUND
    RESULT_NOT_FOUND = APIStatusCode.NOT_FOUND
    USER_NOT_FOUND = APIStatusCode.NOT_FOUND
    DOCUMENT_NOT_FOUND = APIStatusCode.NOT_FOUND
    
    # Validation errors
    VALIDATION_ERROR = APIStatusCode.BAD_REQUEST
    INVALID_DATA_FORMAT = APIStatusCode.BAD_REQUEST
    MISSING_REQUIRED_FIELD = APIStatusCode.BAD_REQUEST
    INVALID_FIELD_VALUE = APIStatusCode.BAD_REQUEST
    FIELD_TOO_LONG = APIStatusCode.BAD_REQUEST
    FIELD_TOO_SHORT = APIStatusCode.BAD_REQUEST
    INVALID_DATE_FORMAT = APIStatusCode.BAD_REQUEST
    INVALID_AMOUNT_FORMAT = APIStatusCode.BAD_REQUEST
    INVALID_NIP_FORMAT = APIStatusCode.BAD_REQUEST
    
    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = APIStatusCode.TOO_MANY_REQUESTS
    UPLOAD_LIMIT_EXCEEDED = APIStatusCode.TOO_MANY_REQUESTS
    API_LIMIT_EXCEEDED = APIStatusCode.TOO_MANY_REQUESTS
    
    # Processing errors
    OCR_PROCESSING_ERROR = APIStatusCode.INTERNAL_SERVER_ERROR
    CELERY_TASK_ERROR = APIStatusCode.INTERNAL_SERVER_ERROR
    SERVICE_UNAVAILABLE = APIStatusCode.SERVICE_UNAVAILABLE
    PROCESSING_TIMEOUT = APIStatusCode.GATEWAY_TIMEOUT
    EXTERNAL_SERVICE_ERROR = APIStatusCode.BAD_GATEWAY
    
    # Business logic errors
    INSUFFICIENT_CONFIDENCE = APIStatusCode.UNPROCESSABLE_ENTITY
    CANNOT_CREATE_FAKTURA = APIStatusCode.UNPROCESSABLE_ENTITY
    DUPLICATE_INVOICE_NUMBER = APIStatusCode.CONFLICT
    INVALID_BUSINESS_RULE = APIStatusCode.UNPROCESSABLE_ENTITY
    
    @classmethod
    def get_status_code(cls, error_code):
        """
        Get HTTP status code for a given error code.
        
        Args:
            error_code: String error code
            
        Returns:
            APIStatusCode: Corresponding status code enum
        """
        return getattr(cls, error_code, APIStatusCode.INTERNAL_SERVER_ERROR)


class StatusCodeUtils:
    """
    Utility functions for working with HTTP status codes.
    """
    
    @staticmethod
    def is_success(status_code):
        """Check if status code indicates success (2xx)."""
        return 200 <= status_code < 300
    
    @staticmethod
    def is_client_error(status_code):
        """Check if status code indicates client error (4xx)."""
        return 400 <= status_code < 500
    
    @staticmethod
    def is_server_error(status_code):
        """Check if status code indicates server error (5xx)."""
        return 500 <= status_code < 600
    
    @staticmethod
    def get_error_category(status_code):
        """
        Get error category for a status code.
        
        Returns:
            str: 'success', 'client_error', 'server_error', or 'unknown'
        """
        if StatusCodeUtils.is_success(status_code):
            return 'success'
        elif StatusCodeUtils.is_client_error(status_code):
            return 'client_error'
        elif StatusCodeUtils.is_server_error(status_code):
            return 'server_error'
        else:
            return 'unknown'
    
    @staticmethod
    def should_retry(status_code):
        """
        Determine if a request should be retried based on status code.
        
        Args:
            status_code: HTTP status code
            
        Returns:
            bool: True if request should be retried
        """
        # Retry on server errors and specific client errors
        retry_codes = [
            status.HTTP_429_TOO_MANY_REQUESTS,  # Rate limited
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_502_BAD_GATEWAY,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.HTTP_504_GATEWAY_TIMEOUT,
        ]
        return status_code in retry_codes
    
    @staticmethod
    def get_retry_after(status_code, default_seconds=60):
        """
        Get suggested retry delay for a status code.
        
        Args:
            status_code: HTTP status code
            default_seconds: Default retry delay
            
        Returns:
            int: Suggested retry delay in seconds
        """
        retry_delays = {
            status.HTTP_429_TOO_MANY_REQUESTS: 60,  # 1 minute
            status.HTTP_500_INTERNAL_SERVER_ERROR: 30,  # 30 seconds
            status.HTTP_502_BAD_GATEWAY: 10,  # 10 seconds
            status.HTTP_503_SERVICE_UNAVAILABLE: 120,  # 2 minutes
            status.HTTP_504_GATEWAY_TIMEOUT: 30,  # 30 seconds
        }
        return retry_delays.get(status_code, default_seconds)


class ResponseBuilder:
    """
    Builder class for creating consistent API responses with proper status codes.
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset builder to initial state."""
        self._status_code = APIStatusCode.SUCCESS
        self._data = None
        self._message = None
        self._error_code = None
        self._error_details = {}
        return self
    
    def success(self, data=None, message=None, status_code=APIStatusCode.SUCCESS):
        """Set success response parameters."""
        self._status_code = status_code
        self._data = data
        self._message = message or status_code.message
        return self
    
    def error(self, error_code, message=None, details=None, status_code=None):
        """Set error response parameters."""
        if status_code is None:
            status_code = ErrorCodeMapping.get_status_code(error_code)
        
        self._status_code = status_code
        self._error_code = error_code
        self._message = message or status_code.message
        self._error_details = details or {}
        return self
    
    def build(self):
        """
        Build the response dictionary.
        
        Returns:
            tuple: (response_data, status_code)
        """
        from datetime import datetime
        
        response_data = {
            'success': StatusCodeUtils.is_success(self._status_code.code),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if response_data['success']:
            response_data['data'] = self._data
            if self._message:
                response_data['message'] = self._message
        else:
            response_data['error'] = {
                'code': self._error_code,
                'message': self._message,
                'details': self._error_details
            }
        
        return response_data, self._status_code.code


# Convenience functions
def build_success_response(data=None, message=None, status_code=APIStatusCode.SUCCESS):
    """Build a success response."""
    builder = ResponseBuilder()
    return builder.success(data, message, status_code).build()


def build_error_response(error_code, message=None, details=None, status_code=None):
    """Build an error response."""
    builder = ResponseBuilder()
    return builder.error(error_code, message, details, status_code).build()


def build_validation_error_response(validation_errors, message="Validation failed"):
    """Build a validation error response."""
    return build_error_response(
        error_code='VALIDATION_ERROR',
        message=message,
        details=validation_errors,
        status_code=APIStatusCode.BAD_REQUEST
    )


def build_not_found_response(resource_type="Resource"):
    """Build a not found error response."""
    return build_error_response(
        error_code='RESOURCE_NOT_FOUND',
        message=f"{resource_type} not found",
        status_code=APIStatusCode.NOT_FOUND
    )


def build_permission_denied_response(message="Permission denied"):
    """Build a permission denied error response."""
    return build_error_response(
        error_code='PERMISSION_DENIED',
        message=message,
        status_code=APIStatusCode.FORBIDDEN
    )


def build_rate_limit_response(retry_after=60):
    """Build a rate limit exceeded error response."""
    return build_error_response(
        error_code='RATE_LIMIT_EXCEEDED',
        message="Rate limit exceeded. Please try again later.",
        details={'retry_after_seconds': retry_after},
        status_code=APIStatusCode.TOO_MANY_REQUESTS
    )