"""
Management command to validate OCR security configuration

This command validates that the OCR system is properly configured for security:
- On-premises processing validation
- File encryption configuration
- Authentication and authorization setup
- Audit logging configuration
- Security middleware setup
"""

import os
import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User

from faktury.services.ocr_security_service import (
    get_file_encryption_service,
    get_ocr_auth_service,
    get_audit_logger,
    get_premises_validator,
    OCRSecurityError
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate OCR security configuration and setup'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Attempt to fix configuration issues automatically'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output with detailed checks'
        )
        
        parser.add_argument(
            '--test-encryption',
            action='store_true',
            help='Test file encryption/decryption functionality'
        )
        
        parser.add_argument(
            '--test-auth',
            action='store_true',
            help='Test OCR authentication functionality'
        )
    
    def handle(self, *args, **options):
        """Execute the security validation"""
        
        self.verbosity = 2 if options['verbose'] else 1
        self.fix_issues = options['fix_issues']
        
        self.stdout.write(
            self.style.HTTP_INFO('=== OCR Security Configuration Validation ===')
        )
        
        validation_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'issues': []
        }
        
        try:
            # Core configuration validation
            self._validate_core_settings(validation_results)
            
            # On-premises processing validation
            self._validate_on_premises_config(validation_results)
            
            # File encryption validation
            self._validate_encryption_config(validation_results)
            
            # Authentication validation
            self._validate_auth_config(validation_results)
            
            # Audit logging validation
            self._validate_audit_logging(validation_results)
            
            # Middleware validation
            self._validate_middleware_config(validation_results)
            
            # File permissions validation
            self._validate_file_permissions(validation_results)
            
            # Optional functional tests
            if options['test_encryption']:
                self._test_encryption_functionality(validation_results)
            
            if options['test_auth']:
                self._test_auth_functionality(validation_results)
            
            # Summary
            self._print_validation_summary(validation_results)
            
            if validation_results['failed'] > 0:
                raise CommandError(
                    f'Security validation failed with {validation_results["failed"]} critical issues'
                )
            
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            raise CommandError(f'Validation failed: {e}')
    
    def _validate_core_settings(self, results):
        """Validate core security settings"""
        
        self.stdout.write('\n1. Core Security Settings')
        
        # Check SECRET_KEY
        if not settings.SECRET_KEY or settings.SECRET_KEY == 'django-insecure-default':
            self._add_issue(results, 'CRITICAL', 'SECRET_KEY is not set or using default value')
        else:
            self._add_pass(results, 'SECRET_KEY is properly configured')
        
        # Check DEBUG setting
        if settings.DEBUG:
            self._add_warning(results, 'DEBUG is enabled - should be False in production')
        else:
            self._add_pass(results, 'DEBUG is disabled')
        
        # Check ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS or '*' in settings.ALLOWED_HOSTS:
            self._add_warning(results, 'ALLOWED_HOSTS should be restricted in production')
        else:
            self._add_pass(results, 'ALLOWED_HOSTS is properly configured')
        
        # Check OCR feature flags
        ocr_flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
        if not ocr_flags.get('disable_google_cloud', False):
            self._add_issue(results, 'CRITICAL', 'Google Cloud is not disabled - violates on-premises requirement')
        else:
            self._add_pass(results, 'Google Cloud is properly disabled')
        
        if not ocr_flags.get('use_opensource_ocr', False):
            self._add_issue(results, 'CRITICAL', 'Open source OCR is not enabled')
        else:
            self._add_pass(results, 'Open source OCR is enabled')
    
    def _validate_on_premises_config(self, results):
        """Validate on-premises processing configuration"""
        
        self.stdout.write('\n2. On-Premises Processing Configuration')
        
        # Check OCR service URL
        ocr_config = getattr(settings, 'OCR_CONFIG', {})
        service_url = ocr_config.get('service_url', '')
        
        if not service_url:
            self._add_issue(results, 'CRITICAL', 'OCR service URL is not configured')
        elif any(domain in service_url.lower() for domain in ['googleapis.com', 'aws.com', 'azure.com']):
            self._add_issue(results, 'CRITICAL', f'OCR service URL points to external service: {service_url}')
        elif service_url.startswith('http://localhost') or service_url.startswith('http://127.0.0.1'):
            self._add_pass(results, 'OCR service URL is configured for local processing')
        else:
            self._add_warning(results, f'OCR service URL should be validated: {service_url}')
        
        # Check OCR engines configuration
        engines = ocr_config.get('engines', {})
        if not engines:
            self._add_issue(results, 'CRITICAL', 'No OCR engines configured')
        else:
            local_engines = ['tesseract', 'easyocr', 'paddleocr']
            configured_engines = list(engines.keys())
            
            has_local = any(engine in configured_engines for engine in local_engines)
            if not has_local:
                self._add_issue(results, 'CRITICAL', 'No local OCR engines configured')
            else:
                self._add_pass(results, f'Local OCR engines configured: {configured_engines}')
        
        # Test premises validator
        try:
            validator = get_premises_validator()
            test_config = {
                'service_url': service_url,
                'engines': list(engines.keys()) if engines else []
            }
            
            if validator.validate_processing_location(test_config):
                self._add_pass(results, 'On-premises validation passed')
            else:
                self._add_issue(results, 'CRITICAL', 'On-premises validation failed')
        except Exception as e:
            self._add_issue(results, 'ERROR', f'On-premises validator error: {e}')
    
    def _validate_encryption_config(self, results):
        """Validate file encryption configuration"""
        
        self.stdout.write('\n3. File Encryption Configuration')
        
        try:
            encryption_service = get_file_encryption_service()
            
            # Check temp directory
            temp_dir = encryption_service.temp_dir
            if not os.path.exists(temp_dir):
                if self.fix_issues:
                    os.makedirs(temp_dir, mode=0o700, exist_ok=True)
                    self._add_pass(results, f'Created secure temp directory: {temp_dir}')
                else:
                    self._add_issue(results, 'ERROR', f'Temp directory does not exist: {temp_dir}')
            else:
                # Check permissions
                stat_info = os.stat(temp_dir)
                permissions = oct(stat_info.st_mode)[-3:]
                
                if permissions != '700':
                    if self.fix_issues:
                        os.chmod(temp_dir, 0o700)
                        self._add_pass(results, f'Fixed temp directory permissions: {temp_dir}')
                    else:
                        self._add_warning(results, f'Temp directory permissions should be 700, found: {permissions}')
                else:
                    self._add_pass(results, f'Temp directory has secure permissions: {temp_dir}')
            
            # Check cryptography library
            try:
                from cryptography.fernet import Fernet
                self._add_pass(results, 'Cryptography library is available')
            except ImportError:
                self._add_issue(results, 'CRITICAL', 'Cryptography library is not installed')
            
        except Exception as e:
            self._add_issue(results, 'ERROR', f'Encryption service error: {e}')
    
    def _validate_auth_config(self, results):
        """Validate authentication configuration"""
        
        self.stdout.write('\n4. Authentication Configuration')
        
        # Check JWT configuration
        jwt_config = getattr(settings, 'SIMPLE_JWT', {})
        if not jwt_config:
            self._add_issue(results, 'ERROR', 'JWT configuration is missing')
        else:
            # Check token lifetime
            access_lifetime = jwt_config.get('ACCESS_TOKEN_LIFETIME')
            if access_lifetime and access_lifetime.total_seconds() > 3600:  # 1 hour
                self._add_warning(results, 'JWT access token lifetime is longer than recommended (1 hour)')
            else:
                self._add_pass(results, 'JWT access token lifetime is appropriate')
            
            # Check signing key
            signing_key = jwt_config.get('SIGNING_KEY')
            if not signing_key or signing_key == settings.SECRET_KEY:
                self._add_pass(results, 'JWT using SECRET_KEY for signing')
            else:
                self._add_pass(results, 'JWT has dedicated signing key')
        
        # Check rate limiting
        throttle_rates = getattr(settings, 'REST_FRAMEWORK', {}).get('DEFAULT_THROTTLE_RATES', {})
        ocr_rates = {k: v for k, v in throttle_rates.items() if 'ocr' in k}
        
        if not ocr_rates:
            self._add_warning(results, 'No OCR-specific rate limiting configured')
        else:
            self._add_pass(results, f'OCR rate limiting configured: {ocr_rates}')
        
        # Check cache configuration for rate limiting
        try:
            cache.set('test_key', 'test_value', 1)
            cache.get('test_key')
            cache.delete('test_key')
            self._add_pass(results, 'Cache backend is working for rate limiting')
        except Exception as e:
            self._add_issue(results, 'ERROR', f'Cache backend error: {e}')
    
    def _validate_audit_logging(self, results):
        """Validate audit logging configuration"""
        
        self.stdout.write('\n5. Audit Logging Configuration')
        
        # Check logging configuration
        logging_config = getattr(settings, 'LOGGING', {})
        
        # Check for security logger
        loggers = logging_config.get('loggers', {})
        security_logger = loggers.get('faktury.api.security')
        
        if not security_logger:
            self._add_issue(results, 'ERROR', 'Security audit logger is not configured')
        else:
            handlers = security_logger.get('handlers', [])
            if 'security_file' in handlers:
                self._add_pass(results, 'Security audit logging is configured')
            else:
                self._add_warning(results, 'Security logger should include file handler')
        
        # Check log directory
        logs_dir = getattr(settings, 'LOGS_DIR', None)
        if not logs_dir:
            self._add_warning(results, 'LOGS_DIR is not configured')
        elif not os.path.exists(logs_dir):
            if self.fix_issues:
                os.makedirs(logs_dir, mode=0o755, exist_ok=True)
                self._add_pass(results, f'Created logs directory: {logs_dir}')
            else:
                self._add_issue(results, 'ERROR', f'Logs directory does not exist: {logs_dir}')
        else:
            self._add_pass(results, f'Logs directory exists: {logs_dir}')
        
        # Test audit logger
        try:
            audit_logger = get_audit_logger()
            self._add_pass(results, 'Audit logger service is available')
        except Exception as e:
            self._add_issue(results, 'ERROR', f'Audit logger error: {e}')
    
    def _validate_middleware_config(self, results):
        """Validate security middleware configuration"""
        
        self.stdout.write('\n6. Security Middleware Configuration')
        
        middleware = getattr(settings, 'MIDDLEWARE', [])
        
        # Check for security middleware
        security_middlewares = [
            'django.middleware.security.SecurityMiddleware',
            'faktury.middleware.SecurityHeadersMiddleware',
            'faktury.middleware.ocr_security_middleware.OCRSecurityMiddleware',
            'faktury.middleware.ocr_security_middleware.OCRFileSecurityMiddleware'
        ]
        
        for middleware_class in security_middlewares:
            if middleware_class in middleware:
                self._add_pass(results, f'Security middleware enabled: {middleware_class.split(".")[-1]}')
            else:
                if 'ocr_security_middleware' in middleware_class:
                    self._add_warning(results, f'OCR security middleware not enabled: {middleware_class.split(".")[-1]}')
                else:
                    self._add_issue(results, 'ERROR', f'Security middleware missing: {middleware_class.split(".")[-1]}')
        
        # Check CORS configuration
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        if '*' in str(cors_origins) or not cors_origins:
            self._add_warning(results, 'CORS origins should be restricted in production')
        else:
            self._add_pass(results, 'CORS origins are properly configured')
    
    def _validate_file_permissions(self, results):
        """Validate file and directory permissions"""
        
        self.stdout.write('\n7. File Permissions Validation')
        
        # Check media directory permissions
        media_root = getattr(settings, 'MEDIA_ROOT', '')
        if media_root and os.path.exists(media_root):
            stat_info = os.stat(media_root)
            permissions = oct(stat_info.st_mode)[-3:]
            
            if permissions not in ['755', '750']:
                self._add_warning(results, f'Media directory permissions should be 755 or 750, found: {permissions}')
            else:
                self._add_pass(results, f'Media directory has appropriate permissions: {permissions}')
        
        # Check OCR upload directory
        ocr_upload_dir = os.path.join(media_root, 'ocr_uploads') if media_root else None
        if ocr_upload_dir and os.path.exists(ocr_upload_dir):
            stat_info = os.stat(ocr_upload_dir)
            permissions = oct(stat_info.st_mode)[-3:]
            
            if permissions not in ['755', '750', '700']:
                if self.fix_issues:
                    os.chmod(ocr_upload_dir, 0o750)
                    self._add_pass(results, 'Fixed OCR upload directory permissions')
                else:
                    self._add_warning(results, f'OCR upload directory permissions should be more restrictive: {permissions}')
            else:
                self._add_pass(results, f'OCR upload directory has secure permissions: {permissions}')
    
    def _test_encryption_functionality(self, results):
        """Test file encryption functionality"""
        
        self.stdout.write('\n8. Encryption Functionality Test')
        
        try:
            encryption_service = get_file_encryption_service()
            
            # Test data
            test_data = b"This is a test document for OCR encryption validation"
            test_document_id = "test_doc_12345"
            
            # Test encryption
            encrypted_path, metadata = encryption_service.encrypt_file(
                test_data, test_document_id, 'test'
            )
            
            if os.path.exists(encrypted_path):
                self._add_pass(results, 'File encryption successful')
                
                # Test decryption
                decrypted_data = encryption_service.decrypt_file(
                    encrypted_path, test_document_id
                )
                
                if decrypted_data == test_data:
                    self._add_pass(results, 'File decryption successful')
                else:
                    self._add_issue(results, 'ERROR', 'File decryption failed - data mismatch')
                
                # Test secure deletion
                if encryption_service.secure_delete_file(encrypted_path):
                    self._add_pass(results, 'Secure file deletion successful')
                else:
                    self._add_warning(results, 'Secure file deletion may have failed')
            else:
                self._add_issue(results, 'ERROR', 'File encryption failed - file not created')
            
        except Exception as e:
            self._add_issue(results, 'ERROR', f'Encryption functionality test failed: {e}')
    
    def _test_auth_functionality(self, results):
        """Test authentication functionality"""
        
        self.stdout.write('\n9. Authentication Functionality Test')
        
        try:
            auth_service = get_ocr_auth_service()
            
            # Create test user if needed
            test_user, created = User.objects.get_or_create(
                username='ocr_test_user',
                defaults={'email': 'test@example.com', 'is_active': True}
            )
            
            test_document_id = "test_doc_auth_12345"
            
            # Test token generation
            token = auth_service.generate_ocr_token(test_user, test_document_id)
            if token:
                self._add_pass(results, 'OCR token generation successful')
                
                # Test token validation
                validated_user = auth_service.validate_ocr_token(token, test_document_id)
                if validated_user and validated_user.id == test_user.id:
                    self._add_pass(results, 'OCR token validation successful')
                else:
                    self._add_issue(results, 'ERROR', 'OCR token validation failed')
            else:
                self._add_issue(results, 'ERROR', 'OCR token generation failed')
            
            # Test rate limiting
            if auth_service.check_rate_limit(test_user, 'test'):
                self._add_pass(results, 'Rate limiting functionality working')
            else:
                self._add_warning(results, 'Rate limiting may be too restrictive')
            
            # Clean up test user if created
            if created:
                test_user.delete()
            
        except Exception as e:
            self._add_issue(results, 'ERROR', f'Authentication functionality test failed: {e}')
    
    def _add_pass(self, results, message):
        """Add a passed validation"""
        results['passed'] += 1
        if self.verbosity >= 2:
            self.stdout.write(f'  ✓ {message}', self.style.SUCCESS)
    
    def _add_warning(self, results, message):
        """Add a warning"""
        results['warnings'] += 1
        results['issues'].append(('WARNING', message))
        self.stdout.write(f'  ⚠ {message}', self.style.WARNING)
    
    def _add_issue(self, results, severity, message):
        """Add a failed validation"""
        if severity in ['CRITICAL', 'ERROR']:
            results['failed'] += 1
        else:
            results['warnings'] += 1
        
        results['issues'].append((severity, message))
        
        if severity == 'CRITICAL':
            self.stdout.write(f'  ✗ {message}', self.style.ERROR)
        else:
            self.stdout.write(f'  ✗ {message}', self.style.WARNING)
    
    def _print_validation_summary(self, results):
        """Print validation summary"""
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('VALIDATION SUMMARY')
        self.stdout.write('='*60)
        
        self.stdout.write(f'Passed: {results["passed"]}', self.style.SUCCESS)
        self.stdout.write(f'Warnings: {results["warnings"]}', self.style.WARNING)
        self.stdout.write(f'Failed: {results["failed"]}', self.style.ERROR)
        
        if results['issues']:
            self.stdout.write('\nISSUES TO ADDRESS:')
            for severity, message in results['issues']:
                if severity == 'CRITICAL':
                    self.stdout.write(f'  {severity}: {message}', self.style.ERROR)
                else:
                    self.stdout.write(f'  {severity}: {message}', self.style.WARNING)
        
        if results['failed'] == 0:
            self.stdout.write('\n✓ OCR security validation PASSED', self.style.SUCCESS)
        else:
            self.stdout.write(f'\n✗ OCR security validation FAILED with {results["failed"]} critical issues', self.style.ERROR)