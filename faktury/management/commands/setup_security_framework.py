"""
Management command to set up the enhanced security framework
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up enhanced security framework for FaktuLove'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-policies',
            action='store_true',
            help='Create default data retention policies',
        )
        parser.add_argument(
            '--setup-config',
            action='store_true',
            help='Set up default security configurations',
        )
        parser.add_argument(
            '--test-encryption',
            action='store_true',
            help='Test encryption functionality',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up enhanced security framework...')
        )
        
        try:
            # Run database migrations first
            self._run_migrations()
            
            if options['create_policies']:
                self._create_data_retention_policies()
            
            if options['setup_config']:
                self._setup_security_configurations()
            
            if options['test_encryption']:
                self._test_encryption()
            
            # Always set up basic security
            self._setup_basic_security()
            
            self.stdout.write(
                self.style.SUCCESS('Security framework setup completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up security framework: {e}')
            )
            logger.error(f"Security framework setup error: {e}")
    
    def _run_migrations(self):
        """Run database migrations for security models"""
        self.stdout.write('Running database migrations...')
        
        from django.core.management import call_command
        call_command('makemigrations', 'faktury', verbosity=0)
        call_command('migrate', verbosity=0)
        
        self.stdout.write(self.style.SUCCESS('✓ Database migrations completed'))
    
    def _create_data_retention_policies(self):
        """Create default data retention policies"""
        self.stdout.write('Creating data retention policies...')
        
        from faktury.models import DataRetentionPolicy
        
        policies = [
            {
                'data_type': 'audit_logs',
                'retention_days': 2555,  # 7 years for audit logs
                'auto_cleanup': False,  # Keep audit logs
                'archive_before_delete': True,
                'legal_hold': True,
                'description': 'Logi audytu muszą być przechowywane przez 7 lat zgodnie z przepisami'
            },
            {
                'data_type': 'user_data',
                'retention_days': 1095,  # 3 years for user data
                'auto_cleanup': False,
                'archive_before_delete': True,
                'legal_hold': False,
                'description': 'Dane użytkowników przechowywane przez 3 lata'
            },
            {
                'data_type': 'invoice_data',
                'retention_days': 1825,  # 5 years for invoice data
                'auto_cleanup': False,
                'archive_before_delete': True,
                'legal_hold': True,
                'description': 'Dane faktur muszą być przechowywane przez 5 lat zgodnie z przepisami podatkowymi'
            },
            {
                'data_type': 'ocr_data',
                'retention_days': 365,  # 1 year for OCR data
                'auto_cleanup': True,
                'archive_before_delete': False,
                'legal_hold': False,
                'description': 'Dane OCR przechowywane przez rok'
            },
            {
                'data_type': 'session_data',
                'retention_days': 30,  # 30 days for session data
                'auto_cleanup': True,
                'archive_before_delete': False,
                'legal_hold': False,
                'description': 'Dane sesji przechowywane przez 30 dni'
            },
            {
                'data_type': 'performance_data',
                'retention_days': 90,  # 90 days for performance data
                'auto_cleanup': True,
                'archive_before_delete': False,
                'legal_hold': False,
                'description': 'Dane wydajności przechowywane przez 90 dni'
            },
            {
                'data_type': 'error_logs',
                'retention_days': 180,  # 6 months for error logs
                'auto_cleanup': True,
                'archive_before_delete': True,
                'legal_hold': False,
                'description': 'Logi błędów przechowywane przez 6 miesięcy'
            },
            {
                'data_type': 'temporary_files',
                'retention_days': 7,  # 7 days for temporary files
                'auto_cleanup': True,
                'archive_before_delete': False,
                'legal_hold': False,
                'description': 'Pliki tymczasowe usuwane po 7 dniach'
            },
            {
                'data_type': 'uploaded_documents',
                'retention_days': 1095,  # 3 years for uploaded documents
                'auto_cleanup': False,
                'archive_before_delete': True,
                'legal_hold': False,
                'description': 'Przesłane dokumenty przechowywane przez 3 lata'
            },
        ]
        
        created_count = 0
        for policy_data in policies:
            policy, created = DataRetentionPolicy.objects.get_or_create(
                data_type=policy_data['data_type'],
                defaults=policy_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created policy for {policy_data["data_type"]}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created {created_count} data retention policies')
        )
    
    def _setup_security_configurations(self):
        """Set up default security configurations"""
        self.stdout.write('Setting up security configurations...')
        
        from faktury.models import SecurityConfiguration
        
        configurations = [
            {
                'name': 'password_policy',
                'config_type': 'password_policy',
                'value': {
                    'min_length': 8,
                    'require_uppercase': True,
                    'require_lowercase': True,
                    'require_numbers': True,
                    'require_special_chars': True,
                    'max_age_days': 90,
                    'history_count': 5,
                    'lockout_attempts': 5,
                    'lockout_duration_minutes': 15
                },
                'description': 'Polityka haseł dla użytkowników systemu'
            },
            {
                'name': 'session_security',
                'config_type': 'session_timeout',
                'value': {
                    'timeout_minutes': 60,
                    'max_concurrent_sessions': 2,
                    'rotate_key_hours': 4,
                    'check_ip_change': True,
                    'force_logout_on_suspicious': True
                },
                'description': 'Ustawienia bezpieczeństwa sesji'
            },
            {
                'name': 'rate_limiting',
                'config_type': 'rate_limiting',
                'value': {
                    'api_requests_per_minute': 100,
                    'login_attempts_per_15min': 5,
                    'ocr_uploads_per_5min': 20,
                    'general_requests_per_5min': 200,
                    'enable_ip_blocking': True,
                    'block_duration_minutes': 30
                },
                'description': 'Ograniczenia częstotliwości żądań'
            },
            {
                'name': 'encryption_settings',
                'config_type': 'encryption_settings',
                'value': {
                    'encrypt_sensitive_data': True,
                    'encryption_algorithm': 'Fernet',
                    'key_rotation_days': 90,
                    'secure_file_deletion': True,
                    'encrypt_audit_details': True
                },
                'description': 'Ustawienia szyfrowania danych'
            },
            {
                'name': 'audit_settings',
                'config_type': 'audit_settings',
                'value': {
                    'log_all_actions': True,
                    'log_failed_attempts': True,
                    'log_suspicious_activity': True,
                    'encrypt_audit_logs': True,
                    'real_time_monitoring': True,
                    'alert_on_violations': True
                },
                'description': 'Ustawienia audytu i monitorowania'
            },
            {
                'name': 'compliance_settings',
                'config_type': 'compliance_settings',
                'value': {
                    'gdpr_compliance': True,
                    'data_retention_enforcement': True,
                    'right_to_be_forgotten': True,
                    'data_portability': True,
                    'consent_management': True,
                    'breach_notification_hours': 72
                },
                'description': 'Ustawienia zgodności z GDPR'
            }
        ]
        
        created_count = 0
        for config_data in configurations:
            config, created = SecurityConfiguration.objects.get_or_create(
                name=config_data['name'],
                defaults=config_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created configuration: {config_data["name"]}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created {created_count} security configurations')
        )
    
    def _test_encryption(self):
        """Test encryption functionality"""
        self.stdout.write('Testing encryption functionality...')
        
        from faktury.services.security_service import SecurityService
        
        try:
            security_service = SecurityService()
            
            # Test data encryption
            test_data = {
                'nip': '1234567890',
                'company_name': 'Test Company Sp. z o.o.',
                'sensitive_info': 'This is sensitive information'
            }
            
            # Encrypt data
            encrypted_data = security_service.encrypt_sensitive_data(test_data)
            self.stdout.write(f'  ✓ Data encrypted successfully')
            
            # Decrypt data
            decrypted_data = security_service.decrypt_sensitive_data(encrypted_data)
            self.stdout.write(f'  ✓ Data decrypted successfully')
            
            # Verify data integrity
            import json
            original_data = json.dumps(test_data, sort_keys=True)
            recovered_data = json.dumps(json.loads(decrypted_data), sort_keys=True)
            
            if original_data == recovered_data:
                self.stdout.write(f'  ✓ Data integrity verified')
            else:
                raise Exception("Data integrity check failed")
            
            # Test password hashing
            test_password = "TestPassword123!"
            hashed_password, salt = security_service.hash_password_additional(test_password)
            self.stdout.write(f'  ✓ Password hashed successfully')
            
            # Verify password
            if security_service.verify_password_additional(test_password, hashed_password, salt):
                self.stdout.write(f'  ✓ Password verification successful')
            else:
                raise Exception("Password verification failed")
            
            self.stdout.write(
                self.style.SUCCESS('✓ All encryption tests passed')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Encryption test failed: {e}')
            )
            raise
    
    def _setup_basic_security(self):
        """Set up basic security features"""
        self.stdout.write('Setting up basic security features...')
        
        # Create initial audit log entry
        try:
            from faktury.services.security_service import SecurityService
            from faktury.models import SecurityAuditLog
            
            security_service = SecurityService()
            
            # Get or create system user for automated actions
            system_user, created = User.objects.get_or_create(
                username='system',
                defaults={
                    'email': 'system@faktulove.pl',
                    'first_name': 'System',
                    'last_name': 'FaktuLove',
                    'is_active': False,  # System user should not be able to log in
                    'is_staff': False,
                }
            )
            
            if created:
                self.stdout.write('  ✓ Created system user for automated actions')
            
            # Create initial audit log entry
            security_service.create_audit_log(
                user=system_user,
                action='system_maintenance',
                resource_type='system',
                details={'action': 'security_framework_setup'},
                success=True
            )
            
            self.stdout.write('  ✓ Created initial audit log entry')
            
            # Set up logging configuration
            self._setup_security_logging()
            
            self.stdout.write(
                self.style.SUCCESS('✓ Basic security setup completed')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Basic security setup failed: {e}')
            )
            raise
    
    def _setup_security_logging(self):
        """Set up security logging configuration"""
        self.stdout.write('Setting up security logging...')
        
        import os
        
        # Ensure logs directory exists
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create security log files if they don't exist
        security_log_file = os.path.join(logs_dir, 'security.log')
        audit_log_file = os.path.join(logs_dir, 'audit.log')
        
        for log_file in [security_log_file, audit_log_file]:
            if not os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write(f"# Security log file created on {timezone.now().isoformat()}\n")
        
        self.stdout.write('  ✓ Security log files created')
        
        # Log initial security setup
        logger.info("Security framework setup completed successfully")
        
        self.stdout.write('  ✓ Security logging configured')