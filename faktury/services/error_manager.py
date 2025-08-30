"""
Comprehensive Error Management Framework for FaktuLove

This module provides centralized error handling, logging, and user feedback
with Polish language support and business-specific error recovery mechanisms.
"""

import logging
import traceback
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

# Configure logger
logger = logging.getLogger(__name__)

class ErrorManager:
    """
    Centralized error handling and user feedback system
    
    Features:
    - Polish language error messages
    - Error recovery suggestions
    - Automatic retry mechanisms
    - Offline capability detection
    - Comprehensive error logging
    """
    
    # Polish error messages for common scenarios
    POLISH_ERROR_MESSAGES = {
        # File upload errors
        'file_upload_failed': 'Przesyłanie pliku nie powiodło się. Sprawdź połączenie internetowe i spróbuj ponownie.',
        'file_too_large': 'Plik jest zbyt duży. Maksymalny rozmiar to {max_size}MB.',
        'invalid_file_type': 'Nieprawidłowy typ pliku. Dozwolone formaty: {allowed_types}.',
        'file_corrupted': 'Plik jest uszkodzony lub nie można go odczytać.',
        
        # OCR processing errors
        'ocr_processing_failed': 'Przetwarzanie dokumentu nie powiodło się. Upewnij się, że plik jest czytelny i spróbuj ponownie.',
        'ocr_service_unavailable': 'Usługa OCR jest tymczasowo niedostępna. Spróbuj ponownie za kilka minut.',
        'ocr_low_confidence': 'Jakość rozpoznania tekstu jest niska. Sprawdź jakość dokumentu i spróbuj ponownie.',
        'ocr_timeout': 'Przetwarzanie dokumentu trwa zbyt długo. Spróbuj z mniejszym plikiem.',
        
        # Business validation errors
        'invalid_nip': 'Podany numer NIP jest nieprawidłowy. Sprawdź format i cyfry kontrolne.',
        'invalid_regon': 'Podany numer REGON jest nieprawidłowy.',
        'invalid_krs': 'Podany numer KRS jest nieprawidłowy.',
        'duplicate_invoice_number': 'Faktura o tym numerze już istnieje.',
        'invalid_vat_rate': 'Nieprawidłowa stawka VAT. Dozwolone wartości: {allowed_rates}.',
        'invalid_date_range': 'Nieprawidłowy zakres dat. Data końcowa musi być późniejsza niż początkowa.',
        
        # Database errors
        'database_error': 'Wystąpił problem z bazą danych. Spróbuj ponownie za chwilę.',
        'connection_timeout': 'Przekroczono limit czasu połączenia. Sprawdź połączenie internetowe.',
        'data_integrity_error': 'Naruszenie integralności danych. Sprawdź poprawność wprowadzonych informacji.',
        
        # Authentication and permissions
        'permission_denied': 'Nie masz uprawnień do wykonania tej operacji.',
        'session_expired': 'Sesja wygasła. Zaloguj się ponownie.',
        'invalid_credentials': 'Nieprawidłowe dane logowania.',
        'account_locked': 'Konto zostało zablokowane. Skontaktuj się z administratorem.',
        
        # Network and connectivity
        'network_error': 'Błąd połączenia sieciowego. Sprawdź połączenie internetowe.',
        'server_unavailable': 'Serwer jest tymczasowo niedostępny. Spróbuj ponownie za kilka minut.',
        'timeout_error': 'Przekroczono limit czasu operacji.',
        
        # Form validation
        'required_field': 'To pole jest wymagane.',
        'invalid_email': 'Nieprawidłowy adres email.',
        'password_too_weak': 'Hasło jest zbyt słabe. Użyj co najmniej 8 znaków, w tym cyfr i znaków specjalnych.',
        'passwords_dont_match': 'Hasła nie są identyczne.',
        
        # General errors
        'unexpected_error': 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie lub skontaktuj się z pomocą techniczną.',
        'maintenance_mode': 'System jest w trybie konserwacji. Spróbuj ponownie później.',
        'rate_limit_exceeded': 'Przekroczono limit żądań. Spróbuj ponownie za {retry_after} sekund.',
    }
    
    # Error recovery suggestions
    ERROR_RECOVERY_SUGGESTIONS = {
        'file_upload_failed': [
            'Sprawdź połączenie internetowe',
            'Upewnij się, że plik nie jest uszkodzony',
            'Spróbuj z mniejszym plikiem',
            'Odśwież stronę i spróbuj ponownie'
        ],
        'ocr_processing_failed': [
            'Sprawdź jakość skanowanego dokumentu',
            'Upewnij się, że tekst jest czytelny',
            'Spróbuj z dokumentem w lepszej rozdzielczości',
            'Użyj formatu PDF zamiast obrazu'
        ],
        'invalid_nip': [
            'Sprawdź czy NIP ma 10 cyfr',
            'Usuń spacje i myślniki z numeru',
            'Sprawdź cyfry kontrolne',
            'Zweryfikuj NIP w bazie REGON'
        ],
        'database_error': [
            'Odśwież stronę',
            'Spróbuj ponownie za kilka minut',
            'Sprawdź połączenie internetowe',
            'Skontaktuj się z pomocą techniczną'
        ],
        'permission_denied': [
            'Zaloguj się ponownie',
            'Sprawdź czy masz odpowiednie uprawnienia',
            'Skontaktuj się z administratorem',
            'Upewnij się, że jesteś w odpowiedniej firmie'
        ]
    }
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        
    def handle_error(self, 
                    error: Exception, 
                    request: Optional[HttpRequest] = None,
                    context: Optional[Dict[str, Any]] = None,
                    user_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle any error with comprehensive logging and user feedback
        
        Args:
            error: The exception that occurred
            request: HTTP request object (if available)
            context: Additional context information
            user_message: Custom user-friendly message
            
        Returns:
            Dict containing error information and user feedback
        """
        error_info = self._analyze_error(error, request, context)
        
        # Log the error
        self._log_error(error_info)
        
        # Get user-friendly message
        if user_message:
            error_info['user_message'] = user_message
        else:
            error_info['user_message'] = self._get_user_friendly_message(error_info)
        
        # Get recovery suggestions
        error_info['recovery_suggestions'] = self._get_recovery_suggestions(error_info)
        
        # Check for automatic retry possibility
        error_info['can_retry'] = self._can_auto_retry(error_info)
        
        # Store error for potential retry
        if error_info['can_retry']:
            self._store_for_retry(error_info)
        
        return error_info
    
    def handle_404_error(self, request: HttpRequest) -> HttpResponse:
        """Handle 404 errors with helpful suggestions"""
        context = {
            'error_type': '404',
            'title': 'Strona nie została znaleziona',
            'message': 'Przepraszamy, ale strona której szukasz nie istnieje.',
            'suggestions': [
                'Sprawdź czy adres URL jest poprawny',
                'Użyj menu nawigacji aby znaleźć odpowiednią stronę',
                'Wróć do strony głównej',
                'Skorzystaj z wyszukiwarki'
            ],
            'helpful_links': [
                {'url': reverse('panel_uzytkownika'), 'text': 'Strona główna'},
                {'url': reverse('faktury_sprzedaz'), 'text': 'Faktury sprzedaży'},
                {'url': reverse('kontrahenci'), 'text': 'Kontrahenci'},
                {'url': reverse('produkty'), 'text': 'Produkty'},
            ]
        }
        
        # Log 404 for analysis
        self.logger.warning(f"404 Error: {request.path} - User: {request.user if hasattr(request, 'user') else 'Anonymous'}")
        
        return render(request, 'faktury/errors/404.html', context, status=404)
    
    def handle_500_error(self, request: HttpRequest) -> HttpResponse:
        """Handle server errors with recovery options"""
        context = {
            'error_type': '500',
            'title': 'Błąd serwera',
            'message': 'Wystąpił nieoczekiwany błąd serwera. Nasze zespół został powiadomiony.',
            'suggestions': [
                'Odśwież stronę',
                'Spróbuj ponownie za kilka minut',
                'Sprawdź czy wszystkie dane zostały zapisane',
                'Skontaktuj się z pomocą techniczną jeśli problem się powtarza'
            ],
            'support_info': {
                'email': getattr(settings, 'SUPPORT_EMAIL', 'support@faktulove.pl'),
                'phone': getattr(settings, 'SUPPORT_PHONE', '+48 123 456 789')
            }
        }
        
        return render(request, 'faktury/errors/500.html', context, status=500)
    
    def handle_403_error(self, request: HttpRequest) -> HttpResponse:
        """Handle permission denied errors"""
        context = {
            'error_type': '403',
            'title': 'Brak uprawnień',
            'message': 'Nie masz uprawnień do wykonania tej operacji.',
            'suggestions': [
                'Zaloguj się ponownie',
                'Sprawdź czy jesteś w odpowiedniej firmie',
                'Skontaktuj się z administratorem w celu nadania uprawnień',
                'Upewnij się, że Twoje konto jest aktywne'
            ]
        }
        
        return render(request, 'faktury/errors/403.html', context, status=403)
    
    def create_user_friendly_message(self, error: Exception, context: Optional[Dict] = None) -> str:
        """Convert technical errors to user-friendly Polish messages"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Check for specific error patterns
        if isinstance(error, ValidationError):
            if 'nip' in error_message:
                return self.POLISH_ERROR_MESSAGES['invalid_nip']
            elif 'email' in error_message:
                return self.POLISH_ERROR_MESSAGES['invalid_email']
            elif 'required' in error_message:
                return self.POLISH_ERROR_MESSAGES['required_field']
        
        elif isinstance(error, IntegrityError):
            if 'unique' in error_message or 'duplicate' in error_message:
                return self.POLISH_ERROR_MESSAGES['duplicate_invoice_number']
            return self.POLISH_ERROR_MESSAGES['data_integrity_error']
        
        elif isinstance(error, PermissionDenied):
            return self.POLISH_ERROR_MESSAGES['permission_denied']
        
        elif 'timeout' in error_message:
            return self.POLISH_ERROR_MESSAGES['timeout_error']
        
        elif 'connection' in error_message:
            return self.POLISH_ERROR_MESSAGES['network_error']
        
        # Default message
        return self.POLISH_ERROR_MESSAGES['unexpected_error']
    
    def log_error_for_monitoring(self, error: Exception, request: Optional[HttpRequest] = None, extra_data: Optional[Dict] = None) -> None:
        """Log errors for system monitoring and alerting"""
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat(),
        }
        
        if request:
            error_data.update({
                'url': request.build_absolute_uri(),
                'method': request.method,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self._get_client_ip(request),
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
            })
        
        if extra_data:
            error_data.update(extra_data)
        
        # Log to file
        self.logger.error(f"Error occurred: {error_data['error_type']}", extra=error_data)
        
        # Store in cache for monitoring dashboard
        cache_key = f"error_log_{datetime.now().strftime('%Y%m%d_%H')}"
        errors = cache.get(cache_key, [])
        errors.append(error_data)
        cache.set(cache_key, errors, 3600)  # Store for 1 hour
        
        # Send alert for critical errors
        if self._is_critical_error(error):
            self._send_error_alert(error_data)
    
    def get_network_status(self) -> Dict[str, Any]:
        """Check network connectivity and return status"""
        try:
            # Simple connectivity check
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=5)
            return {
                'online': True,
                'message': 'Połączenie internetowe działa prawidłowo',
                'last_check': datetime.now().isoformat()
            }
        except:
            return {
                'online': False,
                'message': 'Brak połączenia internetowego',
                'last_check': datetime.now().isoformat(),
                'suggestions': [
                    'Sprawdź połączenie Wi-Fi lub kabel sieciowy',
                    'Sprawdź ustawienia proxy',
                    'Skontaktuj się z administratorem sieci'
                ]
            }
    
    def create_offline_fallback(self, request: HttpRequest, operation: str) -> Dict[str, Any]:
        """Create offline fallback for operations"""
        return {
            'offline_mode': True,
            'message': 'Tryb offline - dane zostaną zsynchronizowane po przywróceniu połączenia',
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'suggestions': [
                'Kontynuuj pracę offline',
                'Dane zostaną automatycznie zsynchronizowane',
                'Sprawdź połączenie internetowe'
            ]
        }
    
    def _analyze_error(self, error: Exception, request: Optional[HttpRequest], context: Optional[Dict]) -> Dict[str, Any]:
        """Analyze error and extract relevant information"""
        return {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat(),
            'request_info': self._extract_request_info(request) if request else None,
            'context': context or {},
            'severity': self._determine_severity(error),
        }
    
    def _extract_request_info(self, request: HttpRequest) -> Dict[str, Any]:
        """Extract relevant information from request"""
        return {
            'url': request.build_absolute_uri(),
            'method': request.method,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': self._get_client_ip(request),
            'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
            'session_key': request.session.session_key if hasattr(request, 'session') else None,
        }
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _determine_severity(self, error: Exception) -> str:
        """Determine error severity level"""
        if isinstance(error, (ValidationError, PermissionDenied)):
            return 'low'
        elif isinstance(error, IntegrityError):
            return 'medium'
        else:
            return 'high'
    
    def _log_error(self, error_info: Dict[str, Any]) -> None:
        """Log error information"""
        severity = error_info.get('severity', 'medium')
        
        if severity == 'high':
            self.logger.error(f"High severity error: {error_info['error_type']}", extra=error_info)
        elif severity == 'medium':
            self.logger.warning(f"Medium severity error: {error_info['error_type']}", extra=error_info)
        else:
            self.logger.info(f"Low severity error: {error_info['error_type']}", extra=error_info)
    
    def _get_user_friendly_message(self, error_info: Dict[str, Any]) -> str:
        """Get user-friendly message based on error analysis"""
        error_type = error_info['error_type']
        error_message = error_info['error_message'].lower()
        
        # Try to match specific error patterns
        for key, message in self.POLISH_ERROR_MESSAGES.items():
            if key in error_message or any(word in error_message for word in key.split('_')):
                return message
        
        # Default based on error type
        if 'Validation' in error_type:
            return self.POLISH_ERROR_MESSAGES['unexpected_error']
        elif 'Permission' in error_type:
            return self.POLISH_ERROR_MESSAGES['permission_denied']
        elif 'Integrity' in error_type:
            return self.POLISH_ERROR_MESSAGES['data_integrity_error']
        
        return self.POLISH_ERROR_MESSAGES['unexpected_error']
    
    def _get_recovery_suggestions(self, error_info: Dict[str, Any]) -> List[str]:
        """Get recovery suggestions based on error type"""
        error_message = error_info['error_message'].lower()
        
        # Try to match specific error patterns
        for key, suggestions in self.ERROR_RECOVERY_SUGGESTIONS.items():
            if key in error_message or any(word in error_message for word in key.split('_')):
                return suggestions
        
        # Default suggestions
        return [
            'Odśwież stronę',
            'Spróbuj ponownie za kilka minut',
            'Sprawdź połączenie internetowe',
            'Skontaktuj się z pomocą techniczną'
        ]
    
    def _can_auto_retry(self, error_info: Dict[str, Any]) -> bool:
        """Determine if error can be automatically retried"""
        error_type = error_info['error_type']
        error_message = error_info['error_message'].lower()
        
        # Don't retry validation or permission errors
        if error_type in ['ValidationError', 'PermissionDenied']:
            return False
        
        # Don't retry integrity errors
        if 'IntegrityError' in error_type:
            return False
        
        # Retry network and timeout errors
        if any(word in error_message for word in ['timeout', 'connection', 'network']):
            return True
        
        return False
    
    def _store_for_retry(self, error_info: Dict[str, Any]) -> None:
        """Store error information for potential retry"""
        retry_key = f"retry_{error_info['timestamp']}"
        cache.set(retry_key, error_info, 300)  # Store for 5 minutes
    
    def _is_critical_error(self, error: Exception) -> bool:
        """Determine if error is critical and requires immediate attention"""
        critical_errors = [
            'DatabaseError',
            'OperationalError',
            'SystemError',
            'MemoryError'
        ]
        return type(error).__name__ in critical_errors
    
    def _send_error_alert(self, error_data: Dict[str, Any]) -> None:
        """Send alert for critical errors"""
        try:
            subject = f"[FaktuLove] Critical Error: {error_data['error_type']}"
            message = f"""
            Critical error occurred in FaktuLove:
            
            Error Type: {error_data['error_type']}
            Message: {error_data['error_message']}
            Timestamp: {error_data['timestamp']}
            URL: {error_data.get('url', 'N/A')}
            User: {error_data.get('user_id', 'Anonymous')}
            
            Traceback:
            {error_data['traceback']}
            """
            
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@faktulove.pl')
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])
        except Exception as e:
            self.logger.error(f"Failed to send error alert: {e}")


# Global error manager instance
error_manager = ErrorManager()