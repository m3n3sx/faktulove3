"""
Enhanced Security Middleware for FaktuLove
Provides comprehensive security features including session management, audit logging, and threat detection
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from faktury.services.security_service import SecurityService


logger = logging.getLogger(__name__)


class EnhancedSecurityMiddleware(MiddlewareMixin):
    """
    Enhanced security middleware providing comprehensive security features
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.security_service = SecurityService()
        self.excluded_paths = [
            '/static/',
            '/media/',
            '/admin/jsi18n/',
            '/favicon.ico',
            '/robots.txt',
        ]
        
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process incoming request for security checks"""
        
        # Skip security checks for excluded paths
        if any(request.path.startswith(path) for path in self.excluded_paths):
            return None
        
        # Add security headers
        self._add_security_headers(request)
        
        # Check for suspicious activity
        if request.user.is_authenticated:
            suspicious_activities = self._check_suspicious_activity(request)
            if suspicious_activities:
                self._handle_suspicious_activity(request, suspicious_activities)
        
        # Rate limiting
        if not self._check_rate_limits(request):
            return self._rate_limit_response(request)
        
        # Session security
        self._check_session_security(request)
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process response to add security headers and audit logging"""
        
        # Skip for excluded paths
        if any(request.path.startswith(path) for path in self.excluded_paths):
            return response
        
        # Add security headers to response
        self._add_response_security_headers(response)
        
        # Log request for audit trail
        self._create_audit_log(request, response)
        
        return response
    
    def _add_security_headers(self, request: HttpRequest) -> None:
        """Add security headers to request context"""
        # Store security context for later use
        request.security_context = {
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'timestamp': timezone.now(),
            'session_key': request.session.session_key,
        }
    
    def _add_response_security_headers(self, response: HttpResponse) -> None:
        """Add comprehensive security headers to response"""
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response['Content-Security-Policy'] = csp_policy
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=()'
        )
        
        # HSTS header for HTTPS
        if getattr(settings, 'SECURE_SSL_REDIRECT', False):
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Feature Policy
        response['Feature-Policy'] = (
            "geolocation 'none'; "
            "microphone 'none'; "
            "camera 'none'; "
            "payment 'none'; "
            "usb 'none';"
        )
    
    def _check_suspicious_activity(self, request: HttpRequest) -> list:
        """Check for suspicious activity patterns"""
        try:
            request_data = {
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'path': request.path,
                'method': request.method,
            }
            
            return self.security_service.detect_suspicious_activity(request.user, request_data)
        except Exception as e:
            logger.error(f"Error checking suspicious activity: {e}")
            return []
    
    def _handle_suspicious_activity(self, request: HttpRequest, activities: list) -> None:
        """Handle detected suspicious activities"""
        try:
            # Log suspicious activity
            self.security_service.create_audit_log(
                user=request.user,
                action='suspicious_activity',
                resource_type='session',
                details={'activities': activities},
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=False,
                error_message=f"Suspicious activities detected: {', '.join(activities)}"
            )
            
            # Take action based on severity
            high_risk_activities = [
                'Rapid successive login attempts',
                'Login from unusual IP address'
            ]
            
            if any(activity in high_risk_activities for activity in activities):
                # Force logout for high-risk activities
                logout(request)
                messages.warning(
                    request,
                    "Wykryto podejrzaną aktywność. Zostałeś wylogowany ze względów bezpieczeństwa."
                )
            else:
                # Just log for lower-risk activities
                messages.info(
                    request,
                    "Wykryto nietypową aktywność na Twoim koncie. Sprawdź ustawienia bezpieczeństwa."
                )
                
        except Exception as e:
            logger.error(f"Error handling suspicious activity: {e}")
    
    def _check_rate_limits(self, request: HttpRequest) -> bool:
        """Check rate limits for different types of requests"""
        try:
            # Get identifier for rate limiting
            if request.user.is_authenticated:
                identifier = f"user:{request.user.id}"
            else:
                identifier = f"ip:{self._get_client_ip(request)}"
            
            # Different limits for different paths
            if request.path.startswith('/api/'):
                return self.security_service.check_rate_limit(
                    f"api:{identifier}", 
                    limit=100, 
                    window_minutes=5
                )
            elif request.path.startswith('/accounts/login/'):
                return self.security_service.check_rate_limit(
                    f"login:{identifier}", 
                    limit=5, 
                    window_minutes=15
                )
            elif request.path.startswith('/ocr/'):
                return self.security_service.check_rate_limit(
                    f"ocr:{identifier}", 
                    limit=20, 
                    window_minutes=5
                )
            else:
                # General rate limit
                return self.security_service.check_rate_limit(
                    f"general:{identifier}", 
                    limit=200, 
                    window_minutes=5
                )
                
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return True  # Allow request if rate limiting fails
    
    def _rate_limit_response(self, request: HttpRequest) -> HttpResponse:
        """Return rate limit exceeded response"""
        
        # Log rate limit violation
        self.security_service.create_audit_log(
            user=request.user if request.user.is_authenticated else None,
            action='rate_limit_exceeded',
            resource_type='system',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=False,
            error_message="Rate limit exceeded"
        )
        
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Przekroczono limit żądań. Spróbuj ponownie za chwilę.',
                'retry_after': 300  # 5 minutes
            }, status=429)
        else:
            messages.error(
                request,
                "Przekroczono limit żądań. Spróbuj ponownie za chwilę."
            )
            return redirect('home')
    
    def _check_session_security(self, request: HttpRequest) -> None:
        """Check session security and validity"""
        if not request.user.is_authenticated:
            return
        
        try:
            # Check session timeout
            session_timeout = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 60)
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                last_activity_time = datetime.fromisoformat(last_activity)
                if datetime.now() - last_activity_time > timedelta(minutes=session_timeout):
                    logout(request)
                    messages.warning(
                        request,
                        "Sesja wygasła ze względów bezpieczeństwa. Zaloguj się ponownie."
                    )
                    return
            
            # Update last activity
            request.session['last_activity'] = datetime.now().isoformat()
            
            # Check for session hijacking
            stored_ip = request.session.get('ip_address')
            current_ip = self._get_client_ip(request)
            
            if stored_ip and stored_ip != current_ip:
                # IP changed - potential session hijacking
                logout(request)
                self.security_service.create_audit_log(
                    user=request.user,
                    action='security_violation',
                    resource_type='session',
                    details={'old_ip': stored_ip, 'new_ip': current_ip},
                    ip_address=current_ip,
                    success=False,
                    error_message="Session IP address changed - potential hijacking"
                )
                messages.error(
                    request,
                    "Wykryto zmianę adresu IP. Zostałeś wylogowany ze względów bezpieczeństwa."
                )
                return
            
            # Store current IP if not set
            if not stored_ip:
                request.session['ip_address'] = current_ip
                
        except Exception as e:
            logger.error(f"Error checking session security: {e}")
    
    def _create_audit_log(self, request: HttpRequest, response: HttpResponse) -> None:
        """Create audit log entry for the request"""
        try:
            # Only log significant actions
            significant_paths = [
                '/accounts/login/',
                '/accounts/logout/',
                '/api/',
                '/admin/',
                '/ocr/',
                '/faktury/',
                '/export/',
                '/import/',
            ]
            
            if not any(request.path.startswith(path) for path in significant_paths):
                return
            
            # Determine action based on path and method
            action = self._determine_action(request.path, request.method)
            if not action:
                return
            
            # Determine resource type and ID
            resource_type, resource_id = self._determine_resource(request.path)
            
            # Create audit log
            self.security_service.create_audit_log(
                user=request.user if request.user.is_authenticated else None,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=200 <= response.status_code < 400,
                error_message=f"HTTP {response.status_code}" if response.status_code >= 400 else None
            )
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
    
    def _determine_action(self, path: str, method: str) -> Optional[str]:
        """Determine action type based on path and method"""
        if '/accounts/login/' in path:
            return 'login'
        elif '/accounts/logout/' in path:
            return 'logout'
        elif '/admin/' in path:
            return 'admin_access'
        elif '/api/' in path:
            return 'api_access'
        elif '/ocr/' in path:
            if method == 'POST':
                return 'ocr_upload'
            else:
                return 'ocr_process'
        elif '/faktury/' in path:
            if method == 'POST':
                return 'invoice_create'
            elif method == 'PUT' or method == 'PATCH':
                return 'invoice_update'
            elif method == 'DELETE':
                return 'invoice_delete'
            else:
                return 'invoice_view'
        elif '/export/' in path:
            return 'data_export'
        elif '/import/' in path:
            return 'data_import'
        
        return None
    
    def _determine_resource(self, path: str) -> tuple:
        """Determine resource type and ID from path"""
        if '/faktury/' in path:
            # Try to extract invoice ID from path
            parts = path.split('/')
            for i, part in enumerate(parts):
                if part == 'faktury' and i + 1 < len(parts):
                    try:
                        resource_id = int(parts[i + 1])
                        return 'invoice', str(resource_id)
                    except ValueError:
                        pass
            return 'invoice', None
        elif '/admin/' in path:
            return 'system', None
        elif '/api/' in path:
            return 'api', None
        elif '/ocr/' in path:
            return 'document', None
        
        return 'system', None
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware for enhanced session security
    """
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process request for session security"""
        
        if not request.user.is_authenticated:
            return None
        
        # Check for concurrent sessions
        if self._check_concurrent_sessions(request):
            logout(request)
            messages.warning(
                request,
                "Wykryto logowanie z innego urządzenia. Zostałeś wylogowany ze względów bezpieczeństwa."
            )
            return redirect('login')
        
        # Rotate session key periodically
        self._rotate_session_key(request)
        
        return None
    
    def _check_concurrent_sessions(self, request: HttpRequest) -> bool:
        """Check for concurrent sessions from different devices"""
        try:
            # Get current session info
            current_session_key = request.session.session_key
            user_id = request.user.id
            
            # Check cache for other active sessions
            cache_key = f"user_sessions:{user_id}"
            active_sessions = cache.get(cache_key, [])
            
            # Clean up expired sessions
            active_sessions = [
                session for session in active_sessions
                if session.get('expires', 0) > timezone.now().timestamp()
            ]
            
            # Check if current session is in the list
            current_session_found = False
            for session in active_sessions:
                if session.get('session_key') == current_session_key:
                    current_session_found = True
                    break
            
            # Add current session if not found
            if not current_session_found:
                session_info = {
                    'session_key': current_session_key,
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'created': timezone.now().timestamp(),
                    'expires': (timezone.now() + timedelta(hours=24)).timestamp(),
                }
                active_sessions.append(session_info)
            
            # Check for multiple sessions (allow max 2 concurrent sessions)
            max_sessions = getattr(settings, 'MAX_CONCURRENT_SESSIONS', 2)
            if len(active_sessions) > max_sessions:
                # Keep only the most recent sessions
                active_sessions.sort(key=lambda x: x.get('created', 0), reverse=True)
                active_sessions = active_sessions[:max_sessions]
                
                # Check if current session survived the cut
                current_session_survived = any(
                    session.get('session_key') == current_session_key
                    for session in active_sessions
                )
                
                if not current_session_survived:
                    return True  # Force logout
            
            # Update cache
            cache.set(cache_key, active_sessions, timeout=86400)  # 24 hours
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking concurrent sessions: {e}")
            return False
    
    def _rotate_session_key(self, request: HttpRequest) -> None:
        """Rotate session key periodically for security"""
        try:
            last_rotation = request.session.get('last_key_rotation')
            if last_rotation:
                last_rotation_time = datetime.fromisoformat(last_rotation)
                # Rotate key every 4 hours
                if datetime.now() - last_rotation_time > timedelta(hours=4):
                    request.session.cycle_key()
                    request.session['last_key_rotation'] = datetime.now().isoformat()
            else:
                request.session['last_key_rotation'] = datetime.now().isoformat()
                
        except Exception as e:
            logger.error(f"Error rotating session key: {e}")
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip


class InputValidationMiddleware(MiddlewareMixin):
    """
    Middleware for comprehensive input validation and sanitization
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.security_service = SecurityService()
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process request for input validation"""
        
        # Skip validation for safe methods and excluded paths
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return None
        
        excluded_paths = ['/admin/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in excluded_paths):
            return None
        
        try:
            # Validate and sanitize POST data
            if request.POST:
                self._validate_post_data(request)
            
            # Validate file uploads
            if request.FILES:
                self._validate_file_uploads(request)
                
        except ValidationError as e:
            return JsonResponse({
                'error': 'Validation failed',
                'message': str(e),
                'details': e.message_dict if hasattr(e, 'message_dict') else None
            }, status=400)
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return JsonResponse({
                'error': 'Validation error',
                'message': 'Wystąpił błąd podczas walidacji danych'
            }, status=400)
        
        return None
    
    def _validate_post_data(self, request: HttpRequest) -> None:
        """Validate POST data"""
        # Import here to avoid circular imports
        from faktury.services.security_service import POLISH_VALIDATION_RULES
        from django.core.exceptions import ValidationError
        
        # Get validation rules based on the form/endpoint
        validation_rules = self._get_validation_rules(request.path)
        
        if validation_rules:
            # Convert QueryDict to regular dict
            post_data = dict(request.POST.items())
            
            # Validate and sanitize
            try:
                sanitized_data = self.security_service.validate_and_sanitize_input(
                    post_data, validation_rules
                )
                
                # Update request.POST with sanitized data
                # Note: This is a bit hacky but necessary for middleware
                request._post = request.POST.copy()
                for key, value in sanitized_data.items():
                    request._post[key] = value
                    
            except ValidationError as e:
                raise e
    
    def _validate_file_uploads(self, request: HttpRequest) -> None:
        """Validate file uploads"""
        from django.core.exceptions import ValidationError
        
        for field_name, uploaded_file in request.FILES.items():
            # Check file size
            max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024)
            if uploaded_file.size > max_size:
                raise ValidationError(f"Plik {uploaded_file.name} jest zbyt duży")
            
            # Check file type
            allowed_types = getattr(settings, 'ALLOWED_UPLOAD_TYPES', [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'image/tiff'
            ])
            
            if uploaded_file.content_type not in allowed_types:
                raise ValidationError(f"Typ pliku {uploaded_file.content_type} nie jest dozwolony")
            
            # Check filename for malicious content
            if self._is_malicious_filename(uploaded_file.name):
                raise ValidationError("Nazwa pliku zawiera niedozwolone znaki")
    
    def _get_validation_rules(self, path: str) -> Dict[str, Dict]:
        """Get validation rules based on request path"""
        from faktury.services.security_service import POLISH_VALIDATION_RULES
        
        if '/faktury/' in path:
            return {
                'numer': POLISH_VALIDATION_RULES['invoice_number'],
                'kwota_netto': POLISH_VALIDATION_RULES['amount'],
                'kwota_brutto': POLISH_VALIDATION_RULES['amount'],
            }
        elif '/kontrahent/' in path:
            return {
                'nazwa': POLISH_VALIDATION_RULES['company_name'],
                'nip': POLISH_VALIDATION_RULES['nip'],
                'regon': POLISH_VALIDATION_RULES['regon'],
                'email': POLISH_VALIDATION_RULES['email'],
                'telefon': POLISH_VALIDATION_RULES['phone'],
                'adres': POLISH_VALIDATION_RULES['address'],
                'kod_pocztowy': POLISH_VALIDATION_RULES['postal_code'],
                'miasto': POLISH_VALIDATION_RULES['city'],
            }
        elif '/firma/' in path:
            return {
                'nazwa': POLISH_VALIDATION_RULES['company_name'],
                'nip': POLISH_VALIDATION_RULES['nip'],
                'regon': POLISH_VALIDATION_RULES['regon'],
                'ulica': POLISH_VALIDATION_RULES['address'],
                'kod_pocztowy': POLISH_VALIDATION_RULES['postal_code'],
                'miejscowosc': POLISH_VALIDATION_RULES['city'],
            }
        
        return {}
    
    def _is_malicious_filename(self, filename: str) -> bool:
        """Check if filename contains malicious content"""
        malicious_patterns = [
            '../',
            '..\\',
            '<script',
            'javascript:',
            'vbscript:',
            'onload=',
            'onerror=',
        ]
        
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in malicious_patterns)


from django.core.exceptions import ValidationError