"""
API mixins for common functionality across views.
"""
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from .responses import APIResponseFormatter
from .exceptions import OCRAPIException
import logging

logger = logging.getLogger(__name__)


class BaseAPIMixin:
    """
    Base mixin for all API views providing common functionality.
    """
    
    def success_response(self, data=None, message=None, status_code=status.HTTP_200_OK):
        """Create a success response using the response formatter."""
        return APIResponseFormatter.success(data, message, status_code)
    
    def error_response(self, code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Create an error response using the response formatter."""
        return APIResponseFormatter.error(code, message, details, status_code)
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to add common request processing.
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except OCRAPIException as e:
            return self.error_response(
                message=e.message,
                code=e.code,
                details=e.details,
                status_code=e.status_code
            )
        except Exception as e:
            logger.error(f"Unexpected error in API view: {str(e)}", exc_info=True)
            return self.error_response(
                message="An unexpected error occurred",
                code="INTERNAL_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def handle_exception(self, exc):
        """
        Handle exceptions with consistent API responses.
        """
        if isinstance(exc, OCRAPIException):
            return self.error_response(
                message=exc.message,
                code=exc.code,
                details=exc.details,
                status_code=exc.status_code
            )
        
        # Let DRF handle other exceptions
        return super().handle_exception(exc)


class OwnershipMixin:
    """
    Mixin to ensure users can only access their own resources.
    """
    
    def get_queryset(self):
        """
        Filter queryset to only include objects owned by the current user.
        """
        queryset = super().get_queryset()
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            # Check model type and apply appropriate filtering
            model_name = queryset.model.__name__
            
            if model_name == 'OCRResult':
                # OCRResult ownership through document.user
                return queryset.filter(document__user=self.request.user)
            elif model_name == 'DocumentUpload':
                # DocumentUpload has direct user relationship
                return queryset.filter(user=self.request.user)
            elif hasattr(queryset.model, 'user'):
                # Generic user field
                return queryset.filter(user=self.request.user)
            elif hasattr(queryset.model, 'uploaded_by'):
                # Alternative user field name
                return queryset.filter(uploaded_by=self.request.user)
        return queryset.none()
    
    def check_object_permissions(self, request, obj):
        """
        Check if the user has permission to access the object.
        """
        super().check_object_permissions(request, obj)
        
        # Check ownership based on object type
        model_name = obj.__class__.__name__
        
        if model_name == 'OCRResult':
            # OCRResult ownership through document.user
            if obj.document.user != request.user:
                raise PermissionDenied("You don't have permission to access this resource")
        elif model_name == 'DocumentUpload':
            # DocumentUpload has direct user relationship
            if obj.user != request.user:
                raise PermissionDenied("You don't have permission to access this resource")
        elif hasattr(obj, 'user') and obj.user != request.user:
            # Generic user field
            raise PermissionDenied("You don't have permission to access this resource")
        elif hasattr(obj, 'uploaded_by') and obj.uploaded_by != request.user:
            # Alternative user field name
            raise PermissionDenied("You don't have permission to access this resource")


class CompanyProfileMixin:
    """
    Mixin to ensure user has an active company profile.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Check if user has an active company profile before processing request.
        """
        if request.user.is_authenticated:
            try:
                # Check if user has a company profile
                from faktury.models import Firma
                firma = Firma.objects.filter(user=request.user).first()
                if not firma:
                    return self.error_response(
                        message="Company profile required to access this resource",
                        code="COMPANY_PROFILE_REQUIRED",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                
                # Store company in request for later use
                request.company = firma
                
            except Exception as e:
                logger.error(f"Error checking company profile: {str(e)}", exc_info=True)
                return self.error_response(
                    message="Error validating company profile",
                    code="COMPANY_VALIDATION_ERROR",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return super().dispatch(request, *args, **kwargs)


class FileValidationMixin:
    """
    Mixin for file upload validation.
    """
    
    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/tiff',
    ]
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def validate_file(self, file):
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file object
            
        Returns:
            bool: True if valid
            
        Raises:
            APIException: If validation fails
        """
        from .exceptions import FileSizeExceededError, UnsupportedFileTypeError
        
        # Check file size
        if file.size > self.MAX_FILE_SIZE:
            raise FileSizeExceededError(
                message=f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE // (1024*1024)}MB",
                details={"file_size": file.size, "max_size": self.MAX_FILE_SIZE}
            )
        
        # Check MIME type
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise UnsupportedFileTypeError(
                message=f"File type '{file.content_type}' is not supported",
                details={"file_type": file.content_type, "allowed_types": self.ALLOWED_MIME_TYPES}
            )
        
        # Additional file validation can be added here
        # (e.g., virus scanning, file header validation)
        
        return True


class RateLimitMixin:
    """
    Mixin for custom rate limiting logic.
    """
    
    def check_rate_limit(self, request):
        """
        Check if request should be rate limited.
        
        Args:
            request: HTTP request object
            
        Returns:
            tuple: (is_allowed, retry_after)
        """
        # This can be extended with custom rate limiting logic
        # For now, rely on DRF throttling
        return True, None
    
    def dispatch(self, request, *args, **kwargs):
        """
        Check rate limits before processing request.
        """
        is_allowed, retry_after = self.check_rate_limit(request)
        
        if not is_allowed:
            return self.rate_limited_response(
                message="Rate limit exceeded. Please try again later.",
                retry_after=retry_after
            )
        
        return super().dispatch(request, *args, **kwargs)


class LoggingMixin:
    """
    Mixin for API request/response logging.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Log API requests and responses.
        """
        # Log request
        logger.info(f"API Request: {request.method} {request.path}", extra={
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
            'ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        })
        
        # Process request
        response = super().dispatch(request, *args, **kwargs)
        
        # Log response
        logger.info(f"API Response: {response.status_code}", extra={
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
            'status_code': response.status_code,
            'path': request.path,
        })
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip