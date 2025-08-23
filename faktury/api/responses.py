"""
Response formatters for OCR REST API.

This module provides consistent response formatting for all API endpoints,
ensuring uniform JSON structure for both success and error responses.
"""

from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class APIResponseFormatter:
    """Formatter for consistent API responses."""
    
    @staticmethod
    def success(data=None, message=None, status_code=status.HTTP_200_OK):
        """
        Format a successful API response.
        
        Args:
            data: Response data (dict, list, or None)
            message: Optional success message
            status_code: HTTP status code (default: 200)
            
        Returns:
            Response: DRF Response object with formatted data
        """
        response_data = {
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if message:
            response_data['message'] = message
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Format an error API response.
        
        Args:
            code: Error code string
            message: Error message
            details: Additional error details (dict)
            status_code: HTTP status code (default: 400)
            
        Returns:
            Response: DRF Response object with formatted error
        """
        response_data = {
            'success': False,
            'error': {
                'code': code,
                'message': message,
                'details': details or {}
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def validation_error(errors, message="Validation failed"):
        """
        Format a validation error response.
        
        Args:
            errors: Validation errors (typically from serializer.errors)
            message: Error message
            
        Returns:
            Response: DRF Response object with formatted validation errors
        """
        # Process DRF serializer errors into a more user-friendly format
        processed_errors = APIResponseFormatter._process_validation_errors(errors)
        
        return APIResponseFormatter.error(
            code='VALIDATION_ERROR',
            message=message,
            details=processed_errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def _process_validation_errors(errors):
        """
        Process DRF validation errors into a consistent format.
        
        Args:
            errors: DRF serializer errors
            
        Returns:
            dict: Processed errors with field names and messages
        """
        processed = {}
        
        if isinstance(errors, dict):
            for field, messages in errors.items():
                if isinstance(messages, list):
                    processed[field] = messages
                else:
                    processed[field] = [str(messages)]
        elif isinstance(errors, list):
            processed['non_field_errors'] = errors
        else:
            processed['non_field_errors'] = [str(errors)]
            
        return processed
    
    @staticmethod
    def paginated_response(queryset, serializer_class, request, message=None):
        """
        Format a paginated response.
        
        Args:
            queryset: Django queryset
            serializer_class: Serializer class to use
            request: DRF request object
            message: Optional message
            
        Returns:
            Response: DRF Response object with paginated data
        """
        from rest_framework.pagination import PageNumberPagination
        
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 20))
        paginator.max_page_size = 100
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = serializer_class(page, many=True, context={'request': request})
            
            response_data = {
                'results': serializer.data,
                'pagination': {
                    'count': paginator.page.paginator.count,
                    'page': paginator.page.number,
                    'page_size': len(page),
                    'total_pages': paginator.page.paginator.num_pages,
                    'has_next': paginator.page.has_next(),
                    'has_previous': paginator.page.has_previous(),
                }
            }
            
            return APIResponseFormatter.success(
                data=response_data,
                message=message
            )
        
        # Fallback for non-paginated response
        serializer = serializer_class(queryset, many=True, context={'request': request})
        return APIResponseFormatter.success(
            data={'results': serializer.data},
            message=message
        )


class APIResponseMiddleware:
    """
    Middleware to ensure all API responses have consistent timestamp formatting.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Only process API responses
        if (hasattr(response, 'data') and 
            request.path.startswith('/api/') and 
            isinstance(response.data, dict)):
            
            # Add timestamp if not present
            if 'timestamp' not in response.data or response.data['timestamp'] is None:
                response.data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
                
            # Log API response for monitoring
            self._log_api_response(request, response)
        
        return response
    
    def _log_api_response(self, request, response):
        """Log API response for monitoring and debugging."""
        try:
            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'user': getattr(request, 'user', None),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self._get_client_ip(request),
            }
            
            # Log successful responses at INFO level
            if 200 <= response.status_code < 400:
                logger.info(
                    f"API {request.method} {request.path} - {response.status_code}",
                    extra=log_data
                )
            # Log client errors at WARNING level
            elif 400 <= response.status_code < 500:
                logger.warning(
                    f"API {request.method} {request.path} - {response.status_code}",
                    extra=log_data
                )
            # Log server errors at ERROR level
            else:
                logger.error(
                    f"API {request.method} {request.path} - {response.status_code}",
                    extra=log_data
                )
                
        except Exception as e:
            # Don't let logging errors break the response
            logger.error(f"Error logging API response: {e}")
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def log_api_operation(operation_name, user=None, details=None, level=logging.INFO):
    """
    Log API operations for monitoring and debugging.
    
    Args:
        operation_name: Name of the operation being performed
        user: User performing the operation
        details: Additional details to log
        level: Logging level (default: INFO)
    """
    log_data = {
        'operation': operation_name,
        'user': user,
        'details': details or {}
    }
    
    logger.log(
        level,
        f"API Operation: {operation_name}",
        extra=log_data
    )


def log_api_error(error_code, error_message, user=None, details=None, exc_info=None):
    """
    Log API errors with consistent formatting.
    
    Args:
        error_code: Error code string
        error_message: Error message
        user: User associated with the error
        details: Additional error details
        exc_info: Exception information for stack trace
    """
    log_data = {
        'error_code': error_code,
        'error_message': error_message,
        'user': user,
        'details': details or {}
    }
    
    logger.error(
        f"API Error: {error_code} - {error_message}",
        extra=log_data,
        exc_info=exc_info
    )