"""
OCR Security Middleware for FaktuLove

This middleware enforces security policies for OCR-related operations:
- Authentication and authorization checks
- Rate limiting for OCR operations
- Request validation and sanitization
- Security headers for OCR endpoints
- Audit logging for security events
"""

import json
import logging
import time
from typing import Optional, Dict, Any
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

from ..services.ocr_security_service import (
    get_ocr_auth_service,
    get_audit_logger,
    get_premises_validator,
    OCRSecurityError
)

logger = logging.getLogger('faktury.api.security')


class OCRSecurityMiddleware(MiddlewareMixin):
    """Middleware to enforce OCR security policies"""
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.auth_service = get_ocr_auth_service()
        self.audit_logger = get_audit_logger()
        self.premises_validator = get_premises_validator()
        
        # OCR endpoint patterns
        self.ocr_endpoints = [
            '/api/ocr/',
            '/api/v1/ocr/',
            '/ocr/',
            '/upload/',
            '/process/',
        ]
        
        # Security headers for OCR endpoints
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': self._get_csp_policy(),
            'X-OCR-Processing': 'on-premises',
            'X-Data-Location': 'local'
        }
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process incoming request for OCR security"""
        
        # Check if this is an OCR-related request
        if not self._is_ocr_request(request):
            return None
        
        # Add security context to request
        request.ocr_security = {
            'start_time': time.time(),
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'is_ocr_request': True
        }
        
        # Validate on-premises processing
        if not self._validate_on_premises_request(request):
            self.audit_logger.log_security_event(
                'external_processing_blocked',
                {
                    'ip_address': request.ocr_security['ip_address'],
                    'user_agent': request.ocr_security['user_agent'],
                    'path': request.path,
                    'method': request.method
                },
                severity='error'
            )
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 'EXTERNAL_PROCESSING_BLOCKED',
                    'message': 'External OCR processing is not allowed'
                }
            }, status=403)
        
        # Check authentication for protected endpoints
        auth_result = self._check_ocr_authentication(request)
        if auth_result:
            return auth_result
        
        # Check rate limiting
        rate_limit_result = self._check_rate_limiting(request)
        if rate_limit_result:
            return rate_limit_result
        
        # Validate request content
        validation_result = self._validate_request_content(request)
        if validation_result:
            return validation_result
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process response for OCR security"""
        
        # Add security headers to OCR responses
        if hasattr(request, 'ocr_security') and request.ocr_security.get('is_ocr_request'):
            for header, value in self.security_headers.items():
                response[header] = value
            
            # Log successful OCR operation
            if hasattr(request, 'user') and request.user.is_authenticated:
                processing_time = time.time() - request.ocr_security['start_time']
                
                self.audit_logger.log_security_event(
                    'ocr_request_completed',
                    {
                        'user_id': request.user.id,
                        'path': request.path,
                        'method': request.method,
                        'status_code': response.status_code,
                        'processing_time': processing_time,
                        'ip_address': request.ocr_security['ip_address'],
                        'success': 200 <= response.status_code < 300
                    },
                    severity='info'
                )
        
        return response
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> Optional[HttpResponse]:
        """Handle exceptions in OCR requests"""
        
        if hasattr(request, 'ocr_security') and request.ocr_security.get('is_ocr_request'):
            # Log security-related exceptions
            if isinstance(exception, OCRSecurityError):
                self.audit_logger.log_security_event(
                    'ocr_security_exception',
                    {
                        'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                        'path': request.path,
                        'method': request.method,
                        'exception_type': type(exception).__name__,
                        'exception_message': str(exception),
                        'ip_address': request.ocr_security['ip_address']
                    },
                    severity='error'
                )
                
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'OCR_SECURITY_ERROR',
                        'message': 'OCR security policy violation'
                    }
                }, status=403)
        
        return None
    
    def _is_ocr_request(self, request: HttpRequest) -> bool:
        """Check if request is OCR-related"""
        return any(endpoint in request.path for endpoint in self.ocr_endpoints)
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _validate_on_premises_request(self, request: HttpRequest) -> bool:
        """Validate that request is for on-premises processing"""
        try:
            # Check for any external service indicators in headers
            external_indicators = [
                'X-Google-Cloud',
                'X-AWS-',
                'X-Azure-',
                'X-External-OCR'
            ]
            
            for header_name in request.META:
                for indicator in external_indicators:
                    if indicator.lower() in header_name.lower():
                        return False
            
            # Check request body for external service configurations
            if request.method == 'POST' and hasattr(request, 'body'):
                try:
                    if request.content_type == 'application/json':
                        body = json.loads(request.body.decode('utf-8'))
                        
                        # Check for external service URLs
                        service_url = body.get('service_url', '')
                        if service_url and any(domain in service_url.lower() 
                                             for domain in ['googleapis.com', 'aws.com', 'azure.com']):
                            return False
                        
                        # Validate processing configuration
                        processing_config = body.get('processing_config', {})
                        if processing_config:
                            return self.premises_validator.validate_processing_location(processing_config)
                
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # If we can't parse the body, allow the request to proceed
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"On-premises validation error: {e}")
            return True  # Allow on error to avoid blocking legitimate requests
    
    def _check_ocr_authentication(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Check OCR-specific authentication with improved JWT validation"""
        
        # Skip authentication for public endpoints
        public_endpoints = ['/api/ocr/health/', '/api/ocr/status/', '/api/v1/auth/', '/ocr/get-csrf-token/']
        if any(endpoint in request.path for endpoint in public_endpoints):
            return None
        
        # Only check authentication for API endpoints, not HTML pages
        if '/api/' in request.path:
            # For API endpoints, check JWT authentication first
            jwt_result = self._validate_jwt_authentication(request)
            if jwt_result:
                return jwt_result
            
            # Check if user is authenticated (either via JWT or session)
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                self.auth_service.log_failed_attempt(
                    None, 'ocr_access', 'not_authenticated', 
                    request.ocr_security['ip_address']
                )
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'AUTHENTICATION_REQUIRED',
                        'message': 'Authentication required for OCR operations'
                    }
                }, status=401)
            
            # Check if user is locked out
            lockout_key = f"ocr_lockout:{request.user.id}"
            if cache.get(lockout_key):
                self.auth_service.log_failed_attempt(
                    request.user.id, 'ocr_access', 'user_locked_out',
                    request.ocr_security['ip_address']
                )
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'USER_LOCKED_OUT',
                        'message': 'User temporarily locked out from OCR operations'
                    }
                }, status=429)
            
            # Check OCR token for sensitive operations
            if request.method in ['POST', 'PUT', 'DELETE']:
                ocr_token = request.META.get('HTTP_X_OCR_TOKEN')
                document_id = self._extract_document_id(request)
                
                if ocr_token and document_id:
                    validated_user = self.auth_service.validate_ocr_token(ocr_token, document_id)
                    if not validated_user or validated_user.id != request.user.id:
                        self.auth_service.log_failed_attempt(
                            request.user.id, 'ocr_token_validation', 'invalid_token',
                            request.ocr_security['ip_address']
                        )
                        return JsonResponse({
                            'success': False,
                            'error': {
                                'code': 'INVALID_OCR_TOKEN',
                                'message': 'Invalid or expired OCR token'
                            }
                        }, status=403)
        
        # For HTML pages, let Django's @login_required handle authentication
        return None
    
    def _check_rate_limiting(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Check rate limiting for OCR operations"""
        
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Determine operation type
        operation = 'process'
        if 'upload' in request.path:
            operation = 'upload'
        elif 'validate' in request.path:
            operation = 'validate'
        
        # Check rate limit
        if not self.auth_service.check_rate_limit(request.user, operation):
            self.audit_logger.log_security_event(
                'rate_limit_exceeded',
                {
                    'user_id': request.user.id,
                    'operation': operation,
                    'path': request.path,
                    'ip_address': request.ocr_security['ip_address']
                },
                severity='warning'
            )
            
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': f'Rate limit exceeded for {operation} operations'
                }
            }, status=429)
        
        return None
    
    def _validate_request_content(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Validate request content for security"""
        
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return None
        
        # Check content type
        if request.content_type and 'multipart/form-data' not in request.content_type:
            if request.content_type not in ['application/json', 'application/x-www-form-urlencoded']:
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'INVALID_CONTENT_TYPE',
                        'message': 'Invalid content type for OCR operation'
                    }
                }, status=400)
        
        # Check content length
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length:
            try:
                length = int(content_length)
                max_size = getattr(settings, 'OCR_MAX_UPLOAD_SIZE', 10 * 1024 * 1024)  # 10MB default
                
                if length > max_size:
                    return JsonResponse({
                        'success': False,
                        'error': {
                            'code': 'FILE_TOO_LARGE',
                            'message': f'File size exceeds maximum allowed size of {max_size} bytes'
                        }
                    }, status=413)
            except ValueError:
                pass
        
        return None
    
    def _validate_jwt_authentication(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Validate JWT token for API requests"""
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
            from django.contrib.auth.models import AnonymousUser
            
            # Get JWT authenticator
            jwt_auth = JWTAuthentication()
            
            # Try to authenticate the request
            try:
                auth_result = jwt_auth.authenticate(request)
                if auth_result is not None:
                    user, token = auth_result
                    request.user = user
                    request.auth = token
                    
                    # Log successful JWT authentication
                    self.audit_logger.log_security_event(
                        'jwt_authentication_success',
                        {
                            'user_id': user.id,
                            'path': request.path,
                            'method': request.method,
                            'ip_address': request.ocr_security['ip_address']
                        },
                        severity='info'
                    )
                    return None
                else:
                    # No JWT token provided, check if it's required
                    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                    if auth_header.startswith('Bearer '):
                        # Bearer token provided but invalid
                        return JsonResponse({
                            'success': False,
                            'error': {
                                'code': 'INVALID_JWT_TOKEN',
                                'message': 'Invalid or expired JWT token'
                            }
                        }, status=401)
                    
                    # No JWT token, will fall back to session authentication
                    return None
                    
            except (InvalidToken, TokenError) as e:
                self.audit_logger.log_security_event(
                    'jwt_authentication_failed',
                    {
                        'path': request.path,
                        'method': request.method,
                        'error': str(e),
                        'ip_address': request.ocr_security['ip_address']
                    },
                    severity='warning'
                )
                
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'JWT_AUTHENTICATION_FAILED',
                        'message': 'JWT token validation failed'
                    }
                }, status=401)
                
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 'AUTHENTICATION_ERROR',
                    'message': 'Authentication system error'
                }
            }, status=500)
    
    def _extract_document_id(self, request: HttpRequest) -> Optional[str]:
        """Extract document ID from request"""
        
        # Try URL path first
        path_parts = request.path.strip('/').split('/')
        for i, part in enumerate(path_parts):
            if part in ['document', 'doc'] and i + 1 < len(path_parts):
                return path_parts[i + 1]
        
        # Try request body
        if request.method == 'POST' and hasattr(request, 'body'):
            try:
                if request.content_type == 'application/json':
                    body = json.loads(request.body.decode('utf-8'))
                    return body.get('document_id')
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        # Try query parameters
        return request.GET.get('document_id')
    
    def _get_csp_policy(self) -> str:
        """Generate Content Security Policy for FaktuLove application"""
        
        # Check if we're in debug mode for more permissive policies
        debug_mode = getattr(settings, 'DEBUG', False)
        
        # Base policy - restrictive by default
        policy_parts = [
            "default-src 'self'",
            
            # Scripts: Allow self, inline scripts, and trusted CDNs
            # In production, we should use nonces instead of 'unsafe-inline'
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' " +
            ("cdn.jsdelivr.net cdnjs.cloudflare.com code.iconify.design " +
             "cdn.datatables.net" if debug_mode else ""),
            
            # Styles: Allow self, inline styles, and trusted CDNs
            "style-src 'self' 'unsafe-inline' " +
            "fonts.googleapis.com cdn.jsdelivr.net cdnjs.cloudflare.com " +
            "code.iconify.design cdn.datatables.net",
            
            # Fonts: Allow Google Fonts and other font CDNs
            "font-src 'self' fonts.gstatic.com fonts.googleapis.com " +
            "cdn.jsdelivr.net cdnjs.cloudflare.com",
            
            # Images: Allow self, data URLs, and common image CDNs
            "img-src 'self' data: blob: " +
            "cdn.jsdelivr.net cdnjs.cloudflare.com",
            
            # Connect: Allow self and API endpoints
            "connect-src 'self' " +
            ("cdn.jsdelivr.net cdnjs.cloudflare.com" if debug_mode else ""),
            
            # Media: Allow self and data URLs
            "media-src 'self' data: blob:",
            
            # Objects: Restrict to self only
            "object-src 'self'",
            
            # Base URI: Restrict to self
            "base-uri 'self'",
            
            # Form actions: Allow self
            "form-action 'self'",
            
            # Frame ancestors: Deny (prevent clickjacking)
            "frame-ancestors 'none'",
            
            # Upgrade insecure requests in production
            "upgrade-insecure-requests" if not debug_mode else ""
        ]
        
        # Filter out empty parts and join
        policy = "; ".join(part.strip() for part in policy_parts if part.strip())
        
        return policy


class OCRFileSecurityMiddleware(MiddlewareMixin):
    """Middleware specifically for OCR file upload security"""
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.audit_logger = get_audit_logger()
        
        # Allowed file types
        self.allowed_mime_types = [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/tiff',
            'image/gif'
        ]
        
        # File signature validation
        self.file_signatures = {
            b'\x25\x50\x44\x46': 'application/pdf',  # PDF
            b'\xFF\xD8\xFF': 'image/jpeg',            # JPEG
            b'\x89\x50\x4E\x47': 'image/png',         # PNG
            b'\x49\x49\x2A\x00': 'image/tiff',        # TIFF LE
            b'\x4D\x4D\x00\x2A': 'image/tiff',        # TIFF BE
            b'\x47\x49\x46\x38': 'image/gif',         # GIF
        }
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process file upload requests"""
        
        # Only process file uploads
        if not (request.method == 'POST' and 
                request.content_type and 
                'multipart/form-data' in request.content_type):
            return None
        
        # Check if this is an OCR upload
        if not any(endpoint in request.path for endpoint in ['/upload', '/ocr']):
            return None
        
        # Validate uploaded files
        for file_key, uploaded_file in request.FILES.items():
            validation_result = self._validate_uploaded_file(uploaded_file, request)
            if validation_result:
                return validation_result
        
        return None
    
    def _validate_uploaded_file(self, uploaded_file, request: HttpRequest) -> Optional[HttpResponse]:
        """Validate individual uploaded file"""
        
        try:
            # Check file size
            max_size = getattr(settings, 'OCR_MAX_FILE_SIZE', 10 * 1024 * 1024)  # 10MB
            if uploaded_file.size > max_size:
                self.audit_logger.log_security_event(
                    'file_size_exceeded',
                    {
                        'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                        'filename': uploaded_file.name,
                        'file_size': uploaded_file.size,
                        'max_size': max_size,
                        'ip_address': self._get_client_ip(request)
                    },
                    severity='warning'
                )
                
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'FILE_TOO_LARGE',
                        'message': f'File size {uploaded_file.size} exceeds maximum {max_size} bytes'
                    }
                }, status=413)
            
            # Check MIME type
            if uploaded_file.content_type not in self.allowed_mime_types:
                self.audit_logger.log_security_event(
                    'invalid_file_type',
                    {
                        'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                        'filename': uploaded_file.name,
                        'content_type': uploaded_file.content_type,
                        'allowed_types': self.allowed_mime_types,
                        'ip_address': self._get_client_ip(request)
                    },
                    severity='warning'
                )
                
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'INVALID_FILE_TYPE',
                        'message': f'File type {uploaded_file.content_type} not allowed'
                    }
                }, status=400)
            
            # Validate file signature
            file_header = uploaded_file.read(8)
            uploaded_file.seek(0)  # Reset file pointer
            
            signature_valid = False
            for signature, mime_type in self.file_signatures.items():
                if file_header.startswith(signature):
                    if mime_type == uploaded_file.content_type:
                        signature_valid = True
                        break
            
            if not signature_valid:
                self.audit_logger.log_security_event(
                    'file_signature_mismatch',
                    {
                        'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                        'filename': uploaded_file.name,
                        'declared_type': uploaded_file.content_type,
                        'file_header': file_header.hex(),
                        'ip_address': self._get_client_ip(request)
                    },
                    severity='error'
                )
                
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'FILE_SIGNATURE_MISMATCH',
                        'message': 'File signature does not match declared type'
                    }
                }, status=400)
            
            return None
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 'FILE_VALIDATION_ERROR',
                    'message': 'File validation failed'
                }
            }, status=500)
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip