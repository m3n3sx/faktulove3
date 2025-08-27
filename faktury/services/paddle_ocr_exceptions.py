"""
PaddleOCR-specific Exception Hierarchy

This module defines custom exceptions for PaddleOCR processing errors,
providing detailed error classification and handling capabilities.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class PaddleOCRErrorType(Enum):
    """Classification of PaddleOCR error types"""
    INITIALIZATION = "initialization"
    MODEL_LOADING = "model_loading"
    PROCESSING = "processing"
    MEMORY = "memory"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"


class PaddleOCRError(Exception):
    """
    Base exception for PaddleOCR errors
    
    This is the base class for all PaddleOCR-related exceptions,
    providing common functionality for error handling and logging.
    """
    
    def __init__(self, 
                 message: str, 
                 error_type: PaddleOCRErrorType = PaddleOCRErrorType.PROCESSING,
                 details: Optional[Dict[str, Any]] = None,
                 original_error: Optional[Exception] = None):
        """
        Initialize PaddleOCR error
        
        Args:
            message: Human-readable error message
            error_type: Classification of error type
            details: Additional error details and context
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}
        self.original_error = original_error
        self.timestamp = self._get_timestamp()
        
        # Log the error for debugging
        logger.error(f"PaddleOCR Error [{error_type.value}]: {message}")
        if details:
            logger.debug(f"Error details: {details}")
        if original_error:
            logger.debug(f"Original error: {original_error}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for error tracking"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization"""
        return {
            'error_type': self.error_type.value,
            'message': str(self),
            'details': self.details,
            'timestamp': self.timestamp,
            'original_error': str(self.original_error) if self.original_error else None
        }
    
    def is_retryable(self) -> bool:
        """Check if this error type is retryable"""
        retryable_types = {
            PaddleOCRErrorType.PROCESSING,
            PaddleOCRErrorType.MEMORY,
            PaddleOCRErrorType.TIMEOUT
        }
        return self.error_type in retryable_types


class PaddleOCRInitializationError(PaddleOCRError):
    """
    Raised when PaddleOCR fails to initialize
    
    This error occurs when PaddleOCR cannot be initialized due to:
    - Missing dependencies
    - Invalid configuration
    - Model loading failures
    - System resource issues
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(
            message, 
            PaddleOCRErrorType.INITIALIZATION, 
            details, 
            original_error
        )
    
    def is_retryable(self) -> bool:
        """Initialization errors are generally not retryable"""
        return False


class PaddleOCRModelError(PaddleOCRError):
    """
    Raised when model loading or model-related operations fail
    
    This error occurs when:
    - Models cannot be downloaded or loaded
    - Model files are corrupted
    - Incompatible model versions
    - Model validation failures
    """
    
    def __init__(self, message: str, model_name: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        details = details or {}
        if model_name:
            details['model_name'] = model_name
        
        super().__init__(
            message, 
            PaddleOCRErrorType.MODEL_LOADING, 
            details, 
            original_error
        )
    
    def is_retryable(self) -> bool:
        """Model errors may be retryable if they're temporary"""
        # Check if it's a temporary network issue
        if self.original_error:
            error_str = str(self.original_error).lower()
            temporary_indicators = ['network', 'connection', 'timeout', 'temporary']
            return any(indicator in error_str for indicator in temporary_indicators)
        return False


class PaddleOCRProcessingError(PaddleOCRError):
    """
    Raised when document processing fails
    
    This error occurs during document processing when:
    - Image preprocessing fails
    - OCR processing encounters errors
    - Text extraction fails
    - Invalid input formats
    """
    
    def __init__(self, message: str, processing_stage: Optional[str] = None,
                 document_info: Optional[Dict[str, Any]] = None,
                 details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        details = details or {}
        if processing_stage:
            details['processing_stage'] = processing_stage
        if document_info:
            details['document_info'] = document_info
        
        super().__init__(
            message, 
            PaddleOCRErrorType.PROCESSING, 
            details, 
            original_error
        )


class PaddleOCRMemoryError(PaddleOCRError):
    """
    Raised when memory-related issues occur
    
    This error occurs when:
    - Memory usage exceeds configured limits
    - Out of memory conditions
    - Memory allocation failures
    - Large document processing issues
    """
    
    def __init__(self, message: str, memory_usage_mb: Optional[float] = None,
                 memory_limit_mb: Optional[float] = None,
                 details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        details = details or {}
        if memory_usage_mb is not None:
            details['memory_usage_mb'] = memory_usage_mb
        if memory_limit_mb is not None:
            details['memory_limit_mb'] = memory_limit_mb
        
        super().__init__(
            message, 
            PaddleOCRErrorType.MEMORY, 
            details, 
            original_error
        )


class PaddleOCRTimeoutError(PaddleOCRError):
    """
    Raised when processing times out
    
    This error occurs when:
    - Processing takes longer than configured timeout
    - Model loading times out
    - Network operations time out
    - System becomes unresponsive
    """
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None,
                 elapsed_seconds: Optional[float] = None,
                 operation: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        details = details or {}
        if timeout_seconds is not None:
            details['timeout_seconds'] = timeout_seconds
        if elapsed_seconds is not None:
            details['elapsed_seconds'] = elapsed_seconds
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message, 
            PaddleOCRErrorType.TIMEOUT, 
            details, 
            original_error
        )


class PaddleOCRValidationError(PaddleOCRError):
    """
    Raised when validation fails
    
    This error occurs when:
    - Input validation fails
    - Configuration validation fails
    - Output validation fails
    - Polish pattern validation fails
    """
    
    def __init__(self, message: str, validation_type: Optional[str] = None,
                 invalid_value: Optional[Any] = None,
                 details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        details = details or {}
        if validation_type:
            details['validation_type'] = validation_type
        if invalid_value is not None:
            details['invalid_value'] = str(invalid_value)
        
        super().__init__(
            message, 
            PaddleOCRErrorType.VALIDATION, 
            details, 
            original_error
        )
    
    def is_retryable(self) -> bool:
        """Validation errors are generally not retryable"""
        return False


class PaddleOCRConfigurationError(PaddleOCRError):
    """
    Raised when configuration issues occur
    
    This error occurs when:
    - Invalid configuration parameters
    - Missing required configuration
    - Configuration conflicts
    - Environment setup issues
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_value: Optional[Any] = None,
                 details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        details = details or {}
        if config_key:
            details['config_key'] = config_key
        if config_value is not None:
            details['config_value'] = str(config_value)
        
        super().__init__(
            message, 
            PaddleOCRErrorType.CONFIGURATION, 
            details, 
            original_error
        )
    
    def is_retryable(self) -> bool:
        """Configuration errors are generally not retryable"""
        return False


class PaddleOCRDependencyError(PaddleOCRError):
    """
    Raised when dependency issues occur
    
    This error occurs when:
    - Required libraries are missing
    - Version incompatibilities
    - System dependencies not available
    - GPU/CUDA issues
    """
    
    def __init__(self, message: str, dependency_name: Optional[str] = None,
                 required_version: Optional[str] = None,
                 current_version: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None, 
                 original_error: Optional[Exception] = None):
        details = details or {}
        if dependency_name:
            details['dependency_name'] = dependency_name
        if required_version:
            details['required_version'] = required_version
        if current_version:
            details['current_version'] = current_version
        
        super().__init__(
            message, 
            PaddleOCRErrorType.DEPENDENCY, 
            details, 
            original_error
        )
    
    def is_retryable(self) -> bool:
        """Dependency errors are generally not retryable"""
        return False


def classify_error(error: Exception) -> PaddleOCRErrorType:
    """
    Classify an exception into a PaddleOCR error type
    
    Args:
        error: Exception to classify
        
    Returns:
        PaddleOCRErrorType: Classified error type
    """
    if isinstance(error, PaddleOCRError):
        return error.error_type
    
    error_str = str(error).lower()
    error_type_name = type(error).__name__.lower()
    
    # Memory-related errors
    if any(keyword in error_str for keyword in ['memory', 'out of memory', 'memoryerror']):
        return PaddleOCRErrorType.MEMORY
    
    if 'memoryerror' in error_type_name:
        return PaddleOCRErrorType.MEMORY
    
    # Timeout-related errors
    if any(keyword in error_str for keyword in ['timeout', 'timed out', 'time limit']):
        return PaddleOCRErrorType.TIMEOUT
    
    if 'timeout' in error_type_name:
        return PaddleOCRErrorType.TIMEOUT
    
    # Model-related errors
    if any(keyword in error_str for keyword in ['model', 'download', 'load', 'checkpoint']):
        return PaddleOCRErrorType.MODEL_LOADING
    
    # Configuration-related errors
    if any(keyword in error_str for keyword in ['config', 'setting', 'parameter']):
        return PaddleOCRErrorType.CONFIGURATION
    
    # Dependency-related errors
    if any(keyword in error_str for keyword in ['import', 'module', 'dependency', 'library']):
        return PaddleOCRErrorType.DEPENDENCY
    
    if 'importerror' in error_type_name or 'modulenotfounderror' in error_type_name:
        return PaddleOCRErrorType.DEPENDENCY
    
    # Validation-related errors
    if any(keyword in error_str for keyword in ['validation', 'invalid', 'format']):
        return PaddleOCRErrorType.VALIDATION
    
    if 'valueerror' in error_type_name:
        return PaddleOCRErrorType.VALIDATION
    
    # Default to processing error
    return PaddleOCRErrorType.PROCESSING


def wrap_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> PaddleOCRError:
    """
    Wrap a generic exception in a PaddleOCR-specific error
    
    Args:
        error: Original exception
        context: Additional context information
        
    Returns:
        PaddleOCRError: Wrapped error with appropriate type
    """
    if isinstance(error, PaddleOCRError):
        return error
    
    error_type = classify_error(error)
    message = f"PaddleOCR operation failed: {str(error)}"
    
    # Create appropriate error type
    if error_type == PaddleOCRErrorType.INITIALIZATION:
        return PaddleOCRInitializationError(message, context, error)
    elif error_type == PaddleOCRErrorType.MODEL_LOADING:
        return PaddleOCRModelError(message, details=context, original_error=error)
    elif error_type == PaddleOCRErrorType.MEMORY:
        return PaddleOCRMemoryError(message, details=context, original_error=error)
    elif error_type == PaddleOCRErrorType.TIMEOUT:
        return PaddleOCRTimeoutError(message, details=context, original_error=error)
    elif error_type == PaddleOCRErrorType.VALIDATION:
        return PaddleOCRValidationError(message, details=context, original_error=error)
    elif error_type == PaddleOCRErrorType.CONFIGURATION:
        return PaddleOCRConfigurationError(message, details=context, original_error=error)
    elif error_type == PaddleOCRErrorType.DEPENDENCY:
        return PaddleOCRDependencyError(message, details=context, original_error=error)
    else:
        return PaddleOCRProcessingError(message, details=context, original_error=error)