"""
Error Handling Middleware for FaktuLove

Provides comprehensive error handling, logging, and user feedback
with automatic retry mechanisms and offline capability detection.
"""

import logging
import json
import traceback
from typing import Optional, Dict, Any
from datetime import datetime

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, OperationalError
from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser

from faktury.services.error_manager import error_manager

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Comprehensive error handling middleware
    
    Features:
    - Catches and handles all unhandled exceptions
    - Provides user-friendly error pages
    - Logs errors for monitoring
    - Supports AJAX error responses
    - Implements retry mechanisms
    - Detects offline scenarios
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> Optional[HttpResponse]:
        """
        Process unhandled exceptions and provide appropriate responses
        """
        try:
            # Handle the error using ErrorManager
            error_info = error_manager.handle_error(
                error=exception,
                request=request,
                context=self._get_request_context(request)
            )
            
            # Determine response type based on request
            if self._is_ajax_request(request):
                return self._handle_ajax_error(request, error_info)
            elif self._is_api_request(request):
                return self._handle_api_error(request, error_info)
            else:
                return self._handle_html_error(request, exception, error_info)
                
        except Exception as middleware_error:
            # Fallback error handling if middleware itself fails
            logger.critical(f"Error handling middleware failed: {middleware_error}", exc_info=True)
            return self._fallback_error_response(request, exception)
    
    def _get_request_context(self, request: HttpRequest) -> Dict[str, Any]:
        """Extract relevant context from request"""
        context = {
            'url': request.build_absolute_uri(),
            'method': request.method,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'ip_address': self._get_client_ip(request),
        }
        
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            context['user_id'] = request.user.id
            context['username'] = request.user.username
            
        if hasattr(request, 'session'):
            context['session_key'] = request.session.session_key
            
        return context
    
    def _is_ajax_request(self, request: HttpRequest) -> bool:
        """Check if request is AJAX"""
        return (
            request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or
            request.content_type == 'application/json' or
            'ajax' in request.path.lower()
        )
    
    def _is_api_request(self, request: HttpRequest) -> bool:
        """Check if request is API call"""
        return (
            request.path.startswith('/api/') or
            request.content_type == 'application/json' or
            'application/json' in request.META.get('HTTP_ACCEPT', '')
        )
    
    def _handle_ajax_error(self, request: HttpRequest, error_info: Dict[str, Any]) -> JsonResponse:
        """Handle AJAX errors with JSON response"""
        response_data = {
            'success': False,
            'error': True,
            'message': error_info['user_message'],
            'error_type': error_info['error_type'],
            'timestamp': error_info['timestamp'],
            'recovery_suggestions': error_info['recovery_suggestions'],
            'can_retry': error_info['can_retry']
        }
        
        # Add retry information if applicable
        if error_info['can_retry']:
            response_data['retry_after'] = 5  # seconds
            response_data['max_retries'] = 3
        
        # Add network status for connectivity issues
        if 'network' in error_info['error_message'].lower() or 'connection' in error_info['error_message'].lower():
            network_status = error_manager.get_network_status()
            response_data['network_status'] = network_status
            
            if not network_status['online']:
                response_data['offline_mode'] = error_manager.create_offline_fallback(request, 'ajax_request')
        
        status_code = self._get_status_code_for_error(error_info['error_type'])
        return JsonResponse(response_data, status=status_code)
    
    def _handle_api_error(self, request: HttpRequest, error_info: Dict[str, Any]) -> JsonResponse:
        """Handle API errors with structured JSON response"""
        response_data = {
            'error': {
                'code': error_info['error_type'],
                'message': error_info['user_message'],
                'timestamp': error_info['timestamp'],
                'request_id': f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"
            },
            'suggestions': error_info['recovery_suggestions']
        }
        
        # Add detailed error info for development
        if settings.DEBUG:
            response_data['debug'] = {
                'traceback': error_info['traceback'],
                'context': error_info['context']
            }
        
        status_code = self._get_status_code_for_error(error_info['error_type'])
        return JsonResponse(response_data, status=status_code)
    
    def _handle_html_error(self, request: HttpRequest, exception: Exception, error_info: Dict[str, Any]) -> HttpResponse:
        """Handle HTML errors with appropriate error pages"""
        
        # Handle specific error types
        if isinstance(exception, PermissionDenied):
            return error_manager.handle_403_error(request)
        
        # Handle validation errors with form context
        if isinstance(exception, ValidationError):
            return self._handle_validation_error(request, exception, error_info)
        
        # Handle database errors
        if isinstance(exception, (IntegrityError, OperationalError)):
            return self._handle_database_error(request, exception, error_info)
        
        # Default to 500 error
        return error_manager.handle_500_error(request)
    
    def _handle_validation_error(self, request: HttpRequest, exception: ValidationError, error_info: Dict[str, Any]) -> HttpResponse:
        """Handle validation errors with form feedback"""
        context = {
            'error_type': 'validation',
            'title': 'Błąd walidacji danych',
            'message': error_info['user_message'],
            'suggestions': error_info['recovery_suggestions'],
            'validation_errors': exception.message_dict if hasattr(exception, 'message_dict') else [str(exception)]
        }
        
        return render(request, 'faktury/errors/validation_error.html', context, status=400)
    
    def _handle_database_error(self, request: HttpRequest, exception: Exception, error_info: Dict[str, Any]) -> HttpResponse:
        """Handle database errors with recovery options"""
        context = {
            'error_type': 'database',
            'title': 'Błąd bazy danych',
            'message': error_info['user_message'],
            'suggestions': error_info['recovery_suggestions'],
            'can_retry': True,
            'retry_delay': 5
        }
        
        return render(request, 'faktury/errors/database_error.html', context, status=503)
    
    def _get_status_code_for_error(self, error_type: str) -> int:
        """Get appropriate HTTP status code for error type"""
        status_codes = {
            'ValidationError': 400,
            'PermissionDenied': 403,
            'Http404': 404,
            'IntegrityError': 409,
            'OperationalError': 503,
            'TimeoutError': 504,
        }
        return status_codes.get(error_type, 500)
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _fallback_error_response(self, request: HttpRequest, exception: Exception) -> HttpResponse:
        """Fallback error response when middleware fails"""
        if self._is_ajax_request(request) or self._is_api_request(request):
            return JsonResponse({
                'error': True,
                'message': 'Wystąpił nieoczekiwany błąd systemu.',
                'timestamp': datetime.now().isoformat()
            }, status=500)
        
        # Simple HTML fallback
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Błąd systemu - FaktuLove</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="error">
                <h1>Błąd systemu</h1>
                <p>Wystąpił nieoczekiwany błąd. Spróbuj ponownie za kilka minut.</p>
                <button onclick="history.back()">Wróć</button>
                <button onclick="location.reload()">Odśwież</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content, status=500)


class NetworkStatusMiddleware(MiddlewareMixin):
    """
    Middleware to detect and handle network connectivity issues
    """
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Check network status and add to request context"""
        # Add network status to request for templates
        request.network_status = error_manager.get_network_status()
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Add network status headers to response"""
        if hasattr(request, 'network_status'):
            response['X-Network-Status'] = 'online' if request.network_status['online'] else 'offline'
        return response


class RetryMiddleware(MiddlewareMixin):
    """
    Middleware to handle automatic retry mechanisms
    """
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Check for retry requests and handle them"""
        retry_id = request.GET.get('retry_id')
        if retry_id:
            # Handle retry request
            return self._handle_retry_request(request, retry_id)
        return None
    
    def _handle_retry_request(self, request: HttpRequest, retry_id: str) -> Optional[HttpResponse]:
        """Handle automatic retry request"""
        from django.core.cache import cache
        
        retry_data = cache.get(f"retry_{retry_id}")
        if retry_data:
            # Log retry attempt
            logger.info(f"Retry attempt for request: {retry_id}")
            
            # Remove retry parameter and redirect
            new_url = request.build_absolute_uri().replace(f'?retry_id={retry_id}', '').replace(f'&retry_id={retry_id}', '')
            from django.shortcuts import redirect
            return redirect(new_url)
        
        return None