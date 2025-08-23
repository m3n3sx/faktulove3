"""
Logging configuration for OCR REST API.

This module provides comprehensive logging setup for API operations,
including request/response logging, error tracking, and performance monitoring.
"""

import logging
import json
from datetime import datetime
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import time


class APILoggingFormatter(logging.Formatter):
    """
    Custom formatter for API logs with structured JSON output.
    """
    
    def format(self, record):
        """Format log record as structured JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'user'):
            log_data['user'] = str(record.user) if record.user else None
            log_data['user_id'] = record.user.id if record.user and hasattr(record.user, 'id') else None
        
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        if hasattr(record, 'operation'):
            log_data['operation'] = record.operation
        
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        
        if hasattr(record, 'response_time'):
            log_data['response_time_ms'] = record.response_time
        
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        
        if hasattr(record, 'user_agent'):
            log_data['user_agent'] = record.user_agent
        
        if hasattr(record, 'error_code'):
            log_data['error_code'] = record.error_code
        
        if hasattr(record, 'details'):
            log_data['details'] = record.details
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class APIRequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware for comprehensive API request/response logging.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('faktury.api.requests')
    
    def __call__(self, request):
        # Skip non-API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        start_time = time.time()
        request_id = self._generate_request_id()
        
        # Log request
        self._log_request(request, request_id)
        
        # Process request
        response = self.get_response(request)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Log response
        self._log_response(request, response, request_id, response_time)
        
        return response
    
    def _generate_request_id(self):
        """Generate unique request ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _log_request(self, request, request_id):
        """Log incoming API request."""
        try:
            # Get request body for POST/PUT requests (but limit size)
            request_body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if hasattr(request, 'body') and request.body:
                        body_str = request.body.decode('utf-8')
                        if len(body_str) > 1000:  # Limit body size in logs
                            body_str = body_str[:1000] + '... (truncated)'
                        
                        # Try to parse as JSON for better formatting
                        try:
                            request_body = json.loads(body_str)
                        except json.JSONDecodeError:
                            request_body = body_str
                except Exception:
                    request_body = '<unable to decode>'
            
            self.logger.info(
                f"API Request: {request.method} {request.path}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.GET),
                    'user': request.user if hasattr(request, 'user') else None,
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'content_type': request.content_type,
                    'request_body': request_body
                }
            )
        except Exception as e:
            self.logger.error(f"Error logging request: {e}")
    
    def _log_response(self, request, response, request_id, response_time):
        """Log API response."""
        try:
            # Determine log level based on status code
            if response.status_code < 400:
                log_level = logging.INFO
            elif response.status_code < 500:
                log_level = logging.WARNING
            else:
                log_level = logging.ERROR
            
            # Get response data (but limit size)
            response_data = None
            if hasattr(response, 'data'):
                try:
                    data_str = json.dumps(response.data, default=str)
                    if len(data_str) > 2000:  # Limit response size in logs
                        data_str = data_str[:2000] + '... (truncated)'
                    response_data = json.loads(data_str)
                except Exception:
                    response_data = '<unable to serialize>'
            
            self.logger.log(
                log_level,
                f"API Response: {request.method} {request.path} - {response.status_code}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'user': request.user if hasattr(request, 'user') else None,
                    'ip_address': self._get_client_ip(request),
                    'response_data': response_data
                }
            )
            
            # Log slow requests
            if response_time > 1000:  # More than 1 second
                self.logger.warning(
                    f"Slow API Request: {request.method} {request.path} took {response_time:.2f}ms",
                    extra={
                        'request_id': request_id,
                        'method': request.method,
                        'path': request.path,
                        'response_time': response_time,
                        'user': request.user if hasattr(request, 'user') else None,
                        'operation': 'slow_request'
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Error logging response: {e}")
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIOperationLogger:
    """
    Logger for specific API operations with structured logging.
    """
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.logger = logging.getLogger('faktury.api.operations')
    
    def log_start(self, user=None, details=None):
        """Log the start of an operation."""
        self.logger.info(
            f"Starting operation: {self.operation_name}",
            extra={
                'operation': self.operation_name,
                'phase': 'start',
                'user': user,
                'details': details or {}
            }
        )
    
    def log_success(self, user=None, details=None, duration_ms=None):
        """Log successful completion of an operation."""
        self.logger.info(
            f"Operation completed successfully: {self.operation_name}",
            extra={
                'operation': self.operation_name,
                'phase': 'success',
                'user': user,
                'details': details or {},
                'duration_ms': duration_ms
            }
        )
    
    def log_error(self, error, user=None, details=None, duration_ms=None):
        """Log operation error."""
        self.logger.error(
            f"Operation failed: {self.operation_name} - {str(error)}",
            extra={
                'operation': self.operation_name,
                'phase': 'error',
                'user': user,
                'error': str(error),
                'error_type': type(error).__name__,
                'details': details or {},
                'duration_ms': duration_ms
            },
            exc_info=True
        )
    
    def log_warning(self, message, user=None, details=None):
        """Log operation warning."""
        self.logger.warning(
            f"Operation warning: {self.operation_name} - {message}",
            extra={
                'operation': self.operation_name,
                'phase': 'warning',
                'user': user,
                'warning': message,
                'details': details or {}
            }
        )


class SecurityLogger:
    """
    Logger for security-related events in the API.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('faktury.api.security')
    
    def log_authentication_failure(self, request, reason):
        """Log authentication failure."""
        self.logger.warning(
            f"Authentication failed: {reason}",
            extra={
                'event': 'authentication_failure',
                'reason': reason,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'path': request.path,
                'method': request.method
            }
        )
    
    def log_authorization_failure(self, request, user, resource):
        """Log authorization failure."""
        self.logger.warning(
            f"Authorization failed: User {user} attempted to access {resource}",
            extra={
                'event': 'authorization_failure',
                'user': user,
                'resource': resource,
                'ip_address': self._get_client_ip(request),
                'path': request.path,
                'method': request.method
            }
        )
    
    def log_rate_limit_exceeded(self, request, user, limit_type):
        """Log rate limit exceeded."""
        self.logger.warning(
            f"Rate limit exceeded: {limit_type}",
            extra={
                'event': 'rate_limit_exceeded',
                'limit_type': limit_type,
                'user': user,
                'ip_address': self._get_client_ip(request),
                'path': request.path,
                'method': request.method
            }
        )
    
    def log_suspicious_activity(self, request, activity_type, details):
        """Log suspicious activity."""
        self.logger.error(
            f"Suspicious activity detected: {activity_type}",
            extra={
                'event': 'suspicious_activity',
                'activity_type': activity_type,
                'details': details,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'path': request.path,
                'method': request.method
            }
        )
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Convenience functions for common logging operations
def log_api_operation(operation_name):
    """Decorator for logging API operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = APIOperationLogger(operation_name)
            start_time = time.time()
            
            # Try to extract user from args (typically request.user)
            user = None
            for arg in args:
                if hasattr(arg, 'user'):
                    user = arg.user
                    break
            
            logger.log_start(user=user)
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.log_success(user=user, duration_ms=duration_ms)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.log_error(e, user=user, duration_ms=duration_ms)
                raise
        
        return wrapper
    return decorator


def get_security_logger():
    """Get security logger instance."""
    return SecurityLogger()


def get_operation_logger(operation_name):
    """Get operation logger instance."""
    return APIOperationLogger(operation_name)


# Django logging configuration for API
API_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'api_json': {
            '()': 'faktury.api.logging_config.APILoggingFormatter',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'api_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/api.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'api_json',
        },
        'api_error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/api_errors.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'formatter': 'api_json',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'formatter': 'api_json',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'faktury.api': {
            'handlers': ['api_file', 'api_error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'faktury.api.requests': {
            'handlers': ['api_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'faktury.api.operations': {
            'handlers': ['api_file', 'api_error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'faktury.api.security': {
            'handlers': ['security_file', 'api_error_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}