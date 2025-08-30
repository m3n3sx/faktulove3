"""
Enhanced Security Service for FaktuLove
Provides comprehensive security features including encryption, audit logging, and input validation
"""

import hashlib
import hmac
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import json
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.html import escape
import bleach


logger = logging.getLogger(__name__)


class SecurityService:
    """
    Comprehensive security service for FaktuLove application
    """
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.audit_logger = logging.getLogger('security_audit')
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for data encryption"""
        key_setting = getattr(settings, 'ENCRYPTION_KEY', None)
        if key_setting:
            return key_setting.encode()
        
        # Generate key from SECRET_KEY for consistency
        password = settings.SECRET_KEY.encode()
        salt = b'faktulove_salt_2025'  # Fixed salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_sensitive_data(self, data: Union[str, dict]) -> str:
        """
        Encrypt sensitive data for storage
        
        Args:
            data: Data to encrypt (string or dict)
            
        Returns:
            Encrypted data as base64 string
        """
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise SecurityException("Data encryption failed")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted data as string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise SecurityException("Data decryption failed")
    
    def validate_and_sanitize_input(self, data: Dict[str, Any], validation_rules: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Validate and sanitize user input according to Polish business rules
        
        Args:
            data: Input data to validate
            validation_rules: Validation rules for each field
            
        Returns:
            Sanitized and validated data
        """
        sanitized_data = {}
        errors = {}
        
        for field, value in data.items():
            if field in validation_rules:
                rules = validation_rules[field]
                try:
                    sanitized_value = self._validate_field(field, value, rules)
                    sanitized_data[field] = sanitized_value
                except ValidationError as e:
                    errors[field] = str(e)
            else:
                # Default sanitization for unknown fields
                sanitized_data[field] = self._sanitize_string(str(value))
        
        if errors:
            raise ValidationError(errors)
        
        return sanitized_data
    
    def _validate_field(self, field_name: str, value: Any, rules: Dict) -> Any:
        """Validate individual field according to rules"""
        if value is None and rules.get('required', False):
            raise ValidationError(f"Pole {field_name} jest wymagane")
        
        if value is None:
            return None
        
        # Convert to string for validation
        str_value = str(value).strip()
        
        # Check length constraints
        if 'max_length' in rules and len(str_value) > rules['max_length']:
            raise ValidationError(f"Pole {field_name} może mieć maksymalnie {rules['max_length']} znaków")
        
        if 'min_length' in rules and len(str_value) < rules['min_length']:
            raise ValidationError(f"Pole {field_name} musi mieć co najmniej {rules['min_length']} znaków")
        
        # Pattern validation
        if 'pattern' in rules:
            if not re.match(rules['pattern'], str_value):
                raise ValidationError(f"Pole {field_name} ma nieprawidłowy format")
        
        # Polish-specific validations
        if rules.get('type') == 'nip':
            return self._validate_nip(str_value)
        elif rules.get('type') == 'regon':
            return self._validate_regon(str_value)
        elif rules.get('type') == 'email':
            return self._validate_email(str_value)
        elif rules.get('type') == 'phone':
            return self._validate_phone(str_value)
        elif rules.get('type') == 'amount':
            return self._validate_amount(str_value)
        
        # Sanitize string
        return self._sanitize_string(str_value)
    
    def _validate_nip(self, nip: str) -> str:
        """Validate Polish NIP number"""
        # Remove spaces and dashes
        nip = re.sub(r'[\s\-]', '', nip)
        
        if not re.match(r'^\d{10}$', nip):
            raise ValidationError("NIP musi składać się z 10 cyfr")
        
        # Validate NIP checksum
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        
        if checksum != int(nip[9]):
            raise ValidationError("Nieprawidłowa suma kontrolna NIP")
        
        return nip
    
    def _validate_regon(self, regon: str) -> str:
        """Validate Polish REGON number"""
        regon = re.sub(r'[\s\-]', '', regon)
        
        if len(regon) not in [9, 14]:
            raise ValidationError("REGON musi mieć 9 lub 14 cyfr")
        
        if not regon.isdigit():
            raise ValidationError("REGON może zawierać tylko cyfry")
        
        return regon
    
    def _validate_email(self, email: str) -> str:
        """Validate email address"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Nieprawidłowy adres email")
        return email.lower()
    
    def _validate_phone(self, phone: str) -> str:
        """Validate Polish phone number"""
        # Remove spaces, dashes, and plus signs
        phone = re.sub(r'[\s\-\+]', '', phone)
        
        # Polish phone number patterns
        if re.match(r'^48\d{9}$', phone):  # +48 prefix
            return phone
        elif re.match(r'^\d{9}$', phone):  # 9 digits
            return f"48{phone}"
        else:
            raise ValidationError("Nieprawidłowy numer telefonu")
    
    def _validate_amount(self, amount: str) -> str:
        """Validate monetary amount"""
        # Replace comma with dot for decimal separator
        amount = amount.replace(',', '.')
        
        try:
            float_amount = float(amount)
            if float_amount < 0:
                raise ValidationError("Kwota nie może być ujemna")
            return f"{float_amount:.2f}"
        except ValueError:
            raise ValidationError("Nieprawidłowa kwota")
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string input to prevent XSS"""
        # HTML escape
        value = escape(value)
        
        # Use bleach for additional sanitization
        allowed_tags = []  # No HTML tags allowed
        value = bleach.clean(value, tags=allowed_tags, strip=True)
        
        return value.strip()
    
    def create_audit_log(self, user: Optional[User], action: str, resource_type: str, 
                        resource_id: Optional[str] = None, details: Optional[Dict] = None,
                        ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                        success: bool = True, error_message: Optional[str] = None):
        """
        Create comprehensive audit log entry
        
        Args:
            user: User performing the action
            action: Action being performed
            resource_type: Type of resource being accessed
            resource_id: ID of the resource
            details: Additional details about the action
            ip_address: User's IP address
            user_agent: User's browser user agent
            success: Whether the action was successful
            error_message: Error message if action failed
        """
        try:
            from faktury.models import SecurityAuditLog
            
            # Encrypt sensitive details
            encrypted_details = None
            if details:
                encrypted_details = self.encrypt_sensitive_data(details)
            
            audit_entry = SecurityAuditLog.objects.create(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                encrypted_details=encrypted_details,
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else None,  # Truncate long user agents
                success=success,
                error_message=error_message,
                timestamp=timezone.now()
            )
            
            # Also log to file for backup
            self.audit_logger.info(
                f"User: {user.username if user else 'Anonymous'} | "
                f"Action: {action} | "
                f"Resource: {resource_type}:{resource_id} | "
                f"Success: {success} | "
                f"IP: {ip_address} | "
                f"Timestamp: {timezone.now().isoformat()}"
            )
            
            return audit_entry
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            # Don't raise exception to avoid breaking the main operation
    
    def check_rate_limit(self, identifier: str, limit: int, window_minutes: int) -> bool:
        """
        Check if rate limit is exceeded
        
        Args:
            identifier: Unique identifier (user ID, IP address, etc.)
            limit: Maximum number of requests
            window_minutes: Time window in minutes
            
        Returns:
            True if within limit, False if exceeded
        """
        cache_key = f"rate_limit:{identifier}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return False
        
        # Increment counter
        cache.set(cache_key, current_count + 1, timeout=window_minutes * 60)
        return True
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_password_additional(self, password: str, salt: Optional[str] = None) -> tuple:
        """
        Additional password hashing for extra security
        
        Args:
            password: Password to hash
            salt: Optional salt (will generate if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with high iteration count
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        hashed = hashlib.pbkdf2_hmac('sha256', password_bytes, salt_bytes, 100000)
        return base64.b64encode(hashed).decode(), salt
    
    def verify_password_additional(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify additional password hash"""
        try:
            new_hash, _ = self.hash_password_additional(password, salt)
            return hmac.compare_digest(new_hash, hashed_password)
        except Exception:
            return False
    
    def detect_suspicious_activity(self, user: User, request_data: Dict) -> List[str]:
        """
        Detect suspicious activity patterns
        
        Args:
            user: User to check
            request_data: Request information
            
        Returns:
            List of detected suspicious activities
        """
        suspicious_activities = []
        
        # Check for rapid successive logins
        if self._check_rapid_logins(user):
            suspicious_activities.append("Rapid successive login attempts")
        
        # Check for unusual IP addresses
        if self._check_unusual_ip(user, request_data.get('ip_address')):
            suspicious_activities.append("Login from unusual IP address")
        
        # Check for unusual user agent
        if self._check_unusual_user_agent(user, request_data.get('user_agent')):
            suspicious_activities.append("Login from unusual device/browser")
        
        # Check for off-hours access
        if self._check_off_hours_access():
            suspicious_activities.append("Access during unusual hours")
        
        return suspicious_activities
    
    def _check_rapid_logins(self, user: User) -> bool:
        """Check for rapid successive login attempts"""
        cache_key = f"login_attempts:{user.id}"
        attempts = cache.get(cache_key, [])
        
        # Check if more than 5 attempts in last 5 minutes
        recent_attempts = [
            attempt for attempt in attempts 
            if datetime.fromisoformat(attempt) > datetime.now() - timedelta(minutes=5)
        ]
        
        return len(recent_attempts) > 5
    
    def _check_unusual_ip(self, user: User, ip_address: str) -> bool:
        """Check if IP address is unusual for this user"""
        if not ip_address:
            return False
        
        # Get user's recent IP addresses from audit log
        try:
            from faktury.models import SecurityAuditLog
            recent_ips = SecurityAuditLog.objects.filter(
                user=user,
                timestamp__gte=timezone.now() - timedelta(days=30)
            ).values_list('ip_address', flat=True).distinct()
            
            return ip_address not in recent_ips
        except Exception:
            return False
    
    def _check_unusual_user_agent(self, user: User, user_agent: str) -> bool:
        """Check if user agent is unusual for this user"""
        if not user_agent:
            return False
        
        # Simple check - could be enhanced with ML
        try:
            from faktury.models import SecurityAuditLog
            recent_agents = SecurityAuditLog.objects.filter(
                user=user,
                timestamp__gte=timezone.now() - timedelta(days=7)
            ).values_list('user_agent', flat=True).distinct()
            
            # Check if user agent is completely different
            return user_agent not in recent_agents
        except Exception:
            return False
    
    def _check_off_hours_access(self) -> bool:
        """Check if access is during off-hours (configurable)"""
        current_hour = datetime.now().hour
        # Define business hours (8 AM to 8 PM)
        business_start = getattr(settings, 'BUSINESS_HOURS_START', 8)
        business_end = getattr(settings, 'BUSINESS_HOURS_END', 20)
        
        return current_hour < business_start or current_hour > business_end
    
    def secure_file_deletion(self, file_path: str) -> bool:
        """
        Securely delete file by overwriting with random data
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import os
            
            if not os.path.exists(file_path):
                return True
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite with random data multiple times
            with open(file_path, 'r+b') as file:
                for _ in range(3):  # 3 passes
                    file.seek(0)
                    file.write(secrets.token_bytes(file_size))
                    file.flush()
                    os.fsync(file.fileno())
            
            # Finally delete the file
            os.remove(file_path)
            return True
            
        except Exception as e:
            logger.error(f"Secure file deletion failed for {file_path}: {e}")
            return False


class SecurityException(Exception):
    """Custom exception for security-related errors"""
    pass


# Polish business validation rules
POLISH_VALIDATION_RULES = {
    'nip': {
        'type': 'nip',
        'required': True,
        'max_length': 13  # Including dashes
    },
    'regon': {
        'type': 'regon',
        'required': False,
        'max_length': 14
    },
    'company_name': {
        'type': 'string',
        'required': True,
        'min_length': 2,
        'max_length': 200
    },
    'email': {
        'type': 'email',
        'required': True,
        'max_length': 254
    },
    'phone': {
        'type': 'phone',
        'required': False,
        'max_length': 15
    },
    'amount': {
        'type': 'amount',
        'required': True
    },
    'invoice_number': {
        'type': 'string',
        'required': True,
        'min_length': 1,
        'max_length': 50,
        'pattern': r'^[A-Za-z0-9\/\-_]+$'
    },
    'address': {
        'type': 'string',
        'required': True,
        'min_length': 5,
        'max_length': 200
    },
    'postal_code': {
        'type': 'string',
        'required': True,
        'pattern': r'^\d{2}-\d{3}$'
    },
    'city': {
        'type': 'string',
        'required': True,
        'min_length': 2,
        'max_length': 100
    }
}