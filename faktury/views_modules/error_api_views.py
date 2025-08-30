"""
Error API Views for FaktuLove

Provides API endpoints for error reporting, network status checking,
and offline data synchronization.
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings

from faktury.services.error_manager import error_manager
from faktury.services.offline_handler import offline_handler

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_exempt
def javascript_errors(request):
    """
    Endpoint for reporting JavaScript errors from the frontend
    """
    try:
        data = json.loads(request.body)
        
        error_info = {
            'error_type': 'JavaScriptError',
            'message': data.get('message', ''),
            'filename': data.get('filename', ''),
            'line_number': data.get('lineno', 0),
            'column_number': data.get('colno', 0),
            'stack': data.get('stack', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'url': data.get('url', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Log the JavaScript error
        logger.error(f"JavaScript Error: {error_info['message']}", extra=error_info)
        
        # Store for monitoring
        from django.core.cache import cache
        cache_key = f"js_error_{datetime.now().strftime('%Y%m%d_%H')}"
        errors = cache.get(cache_key, [])
        errors.append(error_info)
        cache.set(cache_key, errors, 3600)
        
        return JsonResponse({
            'success': True,
            'message': 'Error reported successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to process JavaScript error report: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to report error'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def static_file_errors(request):
    """
    Endpoint for reporting static file loading errors
    """
    try:
        data = json.loads(request.body)
        
        error_info = {
            'error_type': 'StaticFileError',
            'file_url': data.get('file_url', ''),
            'file_type': data.get('file_type', ''),
            'error_message': data.get('error_message', ''),
            'page_url': data.get('page_url', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Log the static file error
        logger.warning(f"Static File Error: {error_info['file_url']}", extra=error_info)
        
        return JsonResponse({
            'success': True,
            'message': 'Static file error reported successfully',
            'suggestions': [
                'Sprawdź połączenie internetowe',
                'Odśwież stronę',
                'Wyczyść cache przeglądarki'
            ]
        })
        
    except Exception as e:
        logger.error(f"Failed to process static file error report: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to report error'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def performance_metrics(request):
    """
    Endpoint for reporting performance metrics from the frontend
    """
    try:
        data = json.loads(request.body)
        
        metrics = {
            'page_load_time': data.get('page_load_time', 0),
            'dom_content_loaded': data.get('dom_content_loaded', 0),
            'first_paint': data.get('first_paint', 0),
            'first_contentful_paint': data.get('first_contentful_paint', 0),
            'largest_contentful_paint': data.get('largest_contentful_paint', 0),
            'cumulative_layout_shift': data.get('cumulative_layout_shift', 0),
            'first_input_delay': data.get('first_input_delay', 0),
            'page_url': data.get('page_url', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Log performance metrics
        logger.info(f"Performance Metrics: {metrics['page_url']}", extra=metrics)
        
        # Store for analysis
        from django.core.cache import cache
        cache_key = f"perf_metrics_{datetime.now().strftime('%Y%m%d_%H')}"
        metrics_list = cache.get(cache_key, [])
        metrics_list.append(metrics)
        cache.set(cache_key, metrics_list, 3600)
        
        return JsonResponse({
            'success': True,
            'message': 'Performance metrics recorded successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to process performance metrics: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to record metrics'
        }, status=500)

@require_http_methods(["GET"])
def network_status(request):
    """
    Endpoint for checking network connectivity and system status
    """
    try:
        status = error_manager.get_network_status()
        
        # Add additional system health checks
        system_status = {
            'database': _check_database_health(),
            'cache': _check_cache_health(),
            'static_files': _check_static_files_health()
        }
        
        response_data = {
            'network': status,
            'system': system_status,
            'timestamp': datetime.now().isoformat(),
            'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Network status check failed: {e}")
        return JsonResponse({
            'network': {
                'online': False,
                'status': 'error',
                'message': 'Błąd sprawdzania statusu sieci'
            },
            'error': str(e)
        }, status=500)

@method_decorator(login_required, name='dispatch')
class OfflineSyncView(View):
    """
    View for handling offline data synchronization
    """
    
    def get(self, request):
        """Get offline sync status for current user"""
        try:
            sync_status = offline_handler.get_sync_status(request.user.id)
            return JsonResponse({
                'success': True,
                'sync_status': sync_status
            })
            
        except Exception as e:
            logger.error(f"Failed to get sync status: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Błąd pobierania statusu synchronizacji'
            }, status=500)
    
    def post(self, request):
        """Synchronize offline data for current user"""
        try:
            sync_result = offline_handler.sync_offline_data(request.user.id)
            return JsonResponse({
                'success': True,
                'sync_result': sync_result
            })
            
        except Exception as e:
            logger.error(f"Failed to sync offline data: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Błąd synchronizacji danych offline'
            }, status=500)

@method_decorator(login_required, name='dispatch')
class ErrorReportView(View):
    """
    View for comprehensive error reporting
    """
    
    def post(self, request):
        """Report an error with full context"""
        try:
            data = json.loads(request.body)
            
            # Create a mock exception for error handling
            class ReportedError(Exception):
                pass
            
            error = ReportedError(data.get('message', 'User reported error'))
            
            # Handle the error using ErrorManager
            error_info = error_manager.handle_error(
                error=error,
                request=request,
                context=data.get('context', {}),
                user_message=data.get('user_message')
            )
            
            return JsonResponse({
                'success': True,
                'error_id': f"USR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.user.id}",
                'message': 'Błąd został zgłoszony i zostanie przeanalizowany',
                'recovery_suggestions': error_info['recovery_suggestions'],
                'support_contact': {
                    'email': getattr(settings, 'SUPPORT_EMAIL', 'support@faktulove.pl'),
                    'phone': getattr(settings, 'SUPPORT_PHONE', '+48 123 456 789')
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to process error report: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Nie udało się zgłosić błędu'
            }, status=500)

def _check_database_health() -> Dict[str, Any]:
    """Check database connectivity and performance"""
    try:
        from django.db import connection
        from django.core.management.color import no_style
        
        # Simple database query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        return {
            'status': 'healthy',
            'message': 'Baza danych działa prawidłowo',
            'response_time': 'fast'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Błąd bazy danych: {str(e)}',
            'response_time': 'timeout'
        }

def _check_cache_health() -> Dict[str, Any]:
    """Check cache system health"""
    try:
        from django.core.cache import cache
        
        # Test cache write/read
        test_key = f"health_check_{datetime.now().timestamp()}"
        test_value = "test"
        
        cache.set(test_key, test_value, 60)
        retrieved_value = cache.get(test_key)
        
        if retrieved_value == test_value:
            cache.delete(test_key)
            return {
                'status': 'healthy',
                'message': 'Cache działa prawidłowo'
            }
        else:
            return {
                'status': 'warning',
                'message': 'Cache może działać nieprawidłowo'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Błąd cache: {str(e)}'
        }

def _check_static_files_health() -> Dict[str, Any]:
    """Check static files availability"""
    try:
        import os
        from django.conf import settings
        
        # Check if static files directory exists
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root and os.path.exists(static_root):
            return {
                'status': 'healthy',
                'message': 'Pliki statyczne dostępne'
            }
        else:
            return {
                'status': 'warning',
                'message': 'Katalog plików statycznych może być niedostępny'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Błąd plików statycznych: {str(e)}'
        }