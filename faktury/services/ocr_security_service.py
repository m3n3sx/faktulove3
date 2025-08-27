"""
OCR Security Service for FaktuLove

This service provides comprehensive security and privacy enhancements for OCR processing:
- File encryption for temporary processing data
- Secure cleanup of temporary files
- Authentication and authorization for OCR service access
- Audit logging for document processing operations
- On-premises processing validation
"""

import os
import logging
import tempfile
import shutil
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from django.db import transaction

from ..models import OCRResult, DocumentUpload

logger = logging.getLogger('faktury.api.security')


class OCRSecurityError(Exception):
    """Custom exception for OCR security-related errors"""
    pass


class FileEncryptionService:
    """Service for encrypting and decrypting temporary OCR files"""
    
    def __init__(self):
        self.key_cache = {}
        self.temp_dir = self._get_secure_temp_dir()
        
    def _get_secure_temp_dir(self) -> str:
        """Get or create secure temporary directory for OCR processing"""
        temp_base = getattr(settings, 'OCR_TEMP_DIR', None)
        if not temp_base:
            temp_base = os.path.join(tempfile.gettempdir(), 'faktulove_ocr_secure')
        
        os.makedirs(temp_base, mode=0o700, exist_ok=True)
        return temp_base
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _get_encryption_key(self, document_id: str) -> Fernet:
        """Get or create encryption key for document"""
        if document_id in self.key_cache:
            return self.key_cache[document_id]
        
        # Use document ID and secret key to generate consistent encryption key
        secret = settings.SECRET_KEY
        salt = hashlib.sha256(document_id.encode()).digest()[:16]
        key = self._derive_key(secret, salt)
        
        fernet = Fernet(key)
        self.key_cache[document_id] = fernet
        return fernet
    
    def encrypt_file(self, file_content: bytes, document_id: str, 
                    file_type: str = 'document') -> Tuple[str, Dict[str, Any]]:
        """
        Encrypt file content and save to secure temporary location
        
        Args:
            file_content: Binary content to encrypt
            document_id: Unique document identifier
            file_type: Type of file (document, processed, result)
            
        Returns:
            Tuple of (encrypted_file_path, encryption_metadata)
        """
        try:
            fernet = self._get_encryption_key(document_id)
            
            # Encrypt the content
            encrypted_content = fernet.encrypt(file_content)
            
            # Generate secure filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{document_id}_{file_type}_{timestamp}.enc"
            file_path = os.path.join(self.temp_dir, filename)
            
            # Write encrypted content to file
            with open(file_path, 'wb') as f:
                f.write(encrypted_content)
            
            # Set secure file permissions
            os.chmod(file_path, 0o600)
            
            # Create metadata
            metadata = {
                'encrypted_path': file_path,
                'original_size': len(file_content),
                'encrypted_size': len(encrypted_content),
                'encryption_timestamp': timezone.now().isoformat(),
                'file_type': file_type,
                'checksum': hashlib.sha256(file_content).hexdigest()
            }
            
            logger.info(f"File encrypted for document {document_id}: {filename}")
            return file_path, metadata
            
        except Exception as e:
            logger.error(f"File encryption failed for document {document_id}: {e}")
            raise OCRSecurityError(f"File encryption failed: {e}")
    
    def decrypt_file(self, encrypted_file_path: str, document_id: str) -> bytes:
        """
        Decrypt file content from encrypted file
        
        Args:
            encrypted_file_path: Path to encrypted file
            document_id: Document identifier for key derivation
            
        Returns:
            Decrypted file content
        """
        try:
            if not os.path.exists(encrypted_file_path):
                raise OCRSecurityError(f"Encrypted file not found: {encrypted_file_path}")
            
            fernet = self._get_encryption_key(document_id)
            
            # Read encrypted content
            with open(encrypted_file_path, 'rb') as f:
                encrypted_content = f.read()
            
            # Decrypt content
            decrypted_content = fernet.decrypt(encrypted_content)
            
            logger.debug(f"File decrypted for document {document_id}")
            return decrypted_content
            
        except Exception as e:
            logger.error(f"File decryption failed for document {document_id}: {e}")
            raise OCRSecurityError(f"File decryption failed: {e}")
    
    def secure_delete_file(self, file_path: str) -> bool:
        """
        Securely delete file by overwriting with random data
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deletion successful
        """
        try:
            if not os.path.exists(file_path):
                return True
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite with random data multiple times
            with open(file_path, 'r+b') as f:
                for _ in range(3):  # 3 passes of random data
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Remove the file
            os.remove(file_path)
            
            logger.debug(f"File securely deleted: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Secure file deletion failed for {file_path}: {e}")
            return False


class OCRAuthenticationService:
    """Service for OCR-specific authentication and authorization"""
    
    def __init__(self):
        self.session_timeout = timedelta(hours=2)
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    def generate_ocr_token(self, user: User, document_id: str) -> str:
        """
        Generate secure token for OCR processing session
        
        Args:
            user: User requesting OCR processing
            document_id: Document identifier
            
        Returns:
            Secure token for OCR session
        """
        try:
            # Create token payload
            payload = {
                'user_id': user.id,
                'document_id': document_id,
                'timestamp': timezone.now().isoformat(),
                'expires': (timezone.now() + self.session_timeout).isoformat(),
                'nonce': secrets.token_hex(16)
            }
            
            # Sign the payload
            payload_json = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                settings.SECRET_KEY.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Combine payload and signature
            token_data = {
                'payload': payload,
                'signature': signature
            }
            
            # Encode as base64
            token = base64.urlsafe_b64encode(
                json.dumps(token_data).encode()
            ).decode()
            
            # Cache token for validation
            cache_key = f"ocr_token:{token[:32]}"
            cache.set(cache_key, {
                'user_id': user.id,
                'document_id': document_id,
                'created': timezone.now().isoformat()
            }, timeout=self.session_timeout.total_seconds())
            
            logger.info(f"OCR token generated for user {user.id}, document {document_id}")
            return token
            
        except Exception as e:
            logger.error(f"OCR token generation failed: {e}")
            raise OCRSecurityError(f"Token generation failed: {e}")
    
    def validate_ocr_token(self, token: str, document_id: str) -> Optional[User]:
        """
        Validate OCR processing token
        
        Args:
            token: Token to validate
            document_id: Expected document ID
            
        Returns:
            User if token is valid, None otherwise
        """
        try:
            # Check token format
            if not token or len(token) < 32:
                return None
            
            # Check cache first
            cache_key = f"ocr_token:{token[:32]}"
            cached_data = cache.get(cache_key)
            if not cached_data:
                logger.warning(f"OCR token not found in cache: {token[:32]}")
                return None
            
            # Decode token
            try:
                token_data = json.loads(
                    base64.urlsafe_b64decode(token.encode()).decode()
                )
            except Exception:
                logger.warning(f"Invalid OCR token format: {token[:32]}")
                return None
            
            payload = token_data.get('payload', {})
            signature = token_data.get('signature', '')
            
            # Verify signature
            payload_json = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                settings.SECRET_KEY.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning(f"OCR token signature mismatch: {token[:32]}")
                return None
            
            # Check expiration
            expires = datetime.fromisoformat(payload.get('expires', ''))
            if timezone.now() > expires:
                logger.warning(f"OCR token expired: {token[:32]}")
                cache.delete(cache_key)
                return None
            
            # Check document ID
            if payload.get('document_id') != document_id:
                logger.warning(f"OCR token document ID mismatch: {token[:32]}")
                return None
            
            # Get user
            try:
                user = User.objects.get(id=payload.get('user_id'))
                logger.debug(f"OCR token validated for user {user.id}")
                return user
            except User.DoesNotExist:
                logger.warning(f"OCR token user not found: {payload.get('user_id')}")
                return None
            
        except Exception as e:
            logger.error(f"OCR token validation error: {e}")
            return None
    
    def check_rate_limit(self, user: User, operation: str) -> bool:
        """
        Check if user has exceeded rate limits for OCR operations
        
        Args:
            user: User to check
            operation: Type of operation (upload, process, validate)
            
        Returns:
            True if within limits, False if rate limited
        """
        try:
            # Define rate limits per operation
            # Higher limits for development/testing
            limits = {
                'upload': {'count': 50, 'window': 300},      # 50 uploads per 5 minutes (was 10)
                'process': {'count': 100, 'window': 300},    # 100 processes per 5 minutes (was 20)
                'validate': {'count': 200, 'window': 300},   # 200 validations per 5 minutes (was 50)
            }
            
            limit_config = limits.get(operation, {'count': 10, 'window': 300})
            
            # Check current usage
            cache_key = f"ocr_rate_limit:{user.id}:{operation}"
            current_count = cache.get(cache_key, 0)
            
            if current_count >= limit_config['count']:
                logger.warning(f"Rate limit exceeded for user {user.id}, operation {operation}")
                return False
            
            # Increment counter
            cache.set(cache_key, current_count + 1, timeout=limit_config['window'])
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error to avoid blocking legitimate users
    
    def log_failed_attempt(self, user_id: Optional[int], operation: str, 
                          reason: str, ip_address: str = None):
        """
        Log failed authentication/authorization attempt
        
        Args:
            user_id: User ID if available
            operation: Operation attempted
            reason: Reason for failure
            ip_address: Client IP address
        """
        try:
            log_data = {
                'event': 'ocr_auth_failure',
                'user_id': user_id,
                'operation': operation,
                'reason': reason,
                'ip_address': ip_address,
                'timestamp': timezone.now().isoformat(),
                'severity': 'warning'
            }
            
            logger.warning(f"OCR authentication failure: {json.dumps(log_data)}")
            
            # Track failed attempts for potential lockout
            if user_id:
                cache_key = f"ocr_failed_attempts:{user_id}"
                attempts = cache.get(cache_key, 0) + 1
                cache.set(cache_key, attempts, timeout=self.lockout_duration.total_seconds())
                
                if attempts >= self.max_failed_attempts:
                    # Lock out user
                    lockout_key = f"ocr_lockout:{user_id}"
                    cache.set(lockout_key, True, timeout=self.lockout_duration.total_seconds())
                    logger.error(f"User {user_id} locked out from OCR operations")
            
        except Exception as e:
            logger.error(f"Failed to log authentication failure: {e}")


class OCRAuditLogger:
    """Service for comprehensive audit logging of OCR operations"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger('faktury.api.security')
    
    def log_document_upload(self, user: User, document_id: str, 
                           file_info: Dict[str, Any], success: bool = True):
        """Log document upload event"""
        self._log_audit_event('document_upload', {
            'user_id': user.id,
            'username': user.username,
            'document_id': document_id,
            'file_size': file_info.get('size', 0),
            'file_type': file_info.get('mime_type', 'unknown'),
            'success': success,
            'ip_address': file_info.get('ip_address'),
            'user_agent': file_info.get('user_agent')
        })
    
    def log_processing_start(self, user: User, document_id: str, 
                           processing_config: Dict[str, Any]):
        """Log OCR processing start"""
        self._log_audit_event('processing_start', {
            'user_id': user.id,
            'username': user.username,
            'document_id': document_id,
            'engines_used': processing_config.get('engines', []),
            'processing_mode': processing_config.get('mode', 'standard'),
            'on_premises': True  # Always true for our implementation
        })
    
    def log_processing_complete(self, user: User, document_id: str, 
                              result_summary: Dict[str, Any]):
        """Log OCR processing completion"""
        self._log_audit_event('processing_complete', {
            'user_id': user.id,
            'username': user.username,
            'document_id': document_id,
            'confidence_score': result_summary.get('confidence_score', 0),
            'processing_time': result_summary.get('processing_time', 0),
            'fields_extracted': result_summary.get('fields_extracted', 0),
            'success': result_summary.get('success', False),
            'data_location': 'on_premises'
        })
    
    def log_data_access(self, user: User, document_id: str, 
                       access_type: str, data_accessed: List[str]):
        """Log access to OCR data"""
        self._log_audit_event('data_access', {
            'user_id': user.id,
            'username': user.username,
            'document_id': document_id,
            'access_type': access_type,  # view, download, modify
            'fields_accessed': data_accessed,
            'access_granted': True
        })
    
    def log_data_modification(self, user: User, document_id: str, 
                            changes: Dict[str, Any]):
        """Log modifications to OCR data"""
        self._log_audit_event('data_modification', {
            'user_id': user.id,
            'username': user.username,
            'document_id': document_id,
            'fields_modified': list(changes.keys()),
            'modification_type': 'manual_correction',
            'change_count': len(changes)
        })
    
    def log_file_cleanup(self, document_id: str, files_cleaned: List[str], 
                        cleanup_reason: str):
        """Log file cleanup operations"""
        self._log_audit_event('file_cleanup', {
            'document_id': document_id,
            'files_cleaned': len(files_cleaned),
            'cleanup_reason': cleanup_reason,
            'cleanup_method': 'secure_deletion',
            'files_list': files_cleaned[:10]  # Log first 10 files only
        })
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          severity: str = 'warning'):
        """Log security-related events"""
        self._log_audit_event('security_event', {
            'event_type': event_type,
            'severity': severity,
            **details
        })
    
    def _log_audit_event(self, event_type: str, event_data: Dict[str, Any]):
        """Internal method to log audit events"""
        try:
            audit_record = {
                'event_type': event_type,
                'timestamp': timezone.now().isoformat(),
                'system': 'ocr_processing',
                'version': '1.0',
                **event_data
            }
            
            # Log as structured JSON
            self.audit_logger.info(json.dumps(audit_record))
            
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")


class SecureFileCleanupService:
    """Service for secure cleanup of temporary OCR files"""
    
    def __init__(self):
        self.encryption_service = FileEncryptionService()
        self.audit_logger = OCRAuditLogger()
        self.cleanup_age_hours = getattr(settings, 'OCR_CLEANUP_HOURS', 24)
    
    def cleanup_document_files(self, document_id: str, reason: str = 'processing_complete') -> Dict[str, Any]:
        """
        Clean up all files associated with a document
        
        Args:
            document_id: Document identifier
            reason: Reason for cleanup
            
        Returns:
            Cleanup summary
        """
        try:
            cleanup_summary = {
                'document_id': document_id,
                'files_found': 0,
                'files_deleted': 0,
                'files_failed': 0,
                'cleanup_reason': reason,
                'cleanup_time': timezone.now().isoformat()
            }
            
            # Find all files for this document
            temp_dir = self.encryption_service.temp_dir
            pattern = f"{document_id}_*"
            
            files_to_delete = []
            for file_path in Path(temp_dir).glob(pattern):
                if file_path.is_file():
                    files_to_delete.append(str(file_path))
            
            cleanup_summary['files_found'] = len(files_to_delete)
            
            # Securely delete each file
            for file_path in files_to_delete:
                if self.encryption_service.secure_delete_file(file_path):
                    cleanup_summary['files_deleted'] += 1
                else:
                    cleanup_summary['files_failed'] += 1
            
            # Log cleanup operation
            self.audit_logger.log_file_cleanup(
                document_id, files_to_delete, reason
            )
            
            logger.info(f"Document cleanup completed for {document_id}: "
                       f"{cleanup_summary['files_deleted']}/{cleanup_summary['files_found']} files deleted")
            
            return cleanup_summary
            
        except Exception as e:
            logger.error(f"Document cleanup failed for {document_id}: {e}")
            return {
                'document_id': document_id,
                'error': str(e),
                'cleanup_reason': reason,
                'cleanup_time': timezone.now().isoformat()
            }
    
    def cleanup_old_files(self) -> Dict[str, Any]:
        """
        Clean up old temporary files based on age
        
        Returns:
            Cleanup summary
        """
        try:
            cleanup_summary = {
                'total_files_found': 0,
                'total_files_deleted': 0,
                'total_files_failed': 0,
                'cleanup_time': timezone.now().isoformat(),
                'age_threshold_hours': self.cleanup_age_hours
            }
            
            temp_dir = Path(self.encryption_service.temp_dir)
            cutoff_time = timezone.now() - timedelta(hours=self.cleanup_age_hours)
            
            # Find old files
            old_files = []
            for file_path in temp_dir.glob("*.enc"):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
                    if file_mtime < cutoff_time:
                        old_files.append(str(file_path))
            
            cleanup_summary['total_files_found'] = len(old_files)
            
            # Group files by document ID for audit logging
            document_files = {}
            for file_path in old_files:
                filename = Path(file_path).name
                if '_' in filename:
                    doc_id = filename.split('_')[0]
                    if doc_id not in document_files:
                        document_files[doc_id] = []
                    document_files[doc_id].append(file_path)
            
            # Delete files and log by document
            for doc_id, files in document_files.items():
                deleted_count = 0
                for file_path in files:
                    if self.encryption_service.secure_delete_file(file_path):
                        deleted_count += 1
                        cleanup_summary['total_files_deleted'] += 1
                    else:
                        cleanup_summary['total_files_failed'] += 1
                
                # Log cleanup for this document
                self.audit_logger.log_file_cleanup(
                    doc_id, files, f'age_based_cleanup_{self.cleanup_age_hours}h'
                )
            
            logger.info(f"Age-based cleanup completed: "
                       f"{cleanup_summary['total_files_deleted']}/{cleanup_summary['total_files_found']} files deleted")
            
            return cleanup_summary
            
        except Exception as e:
            logger.error(f"Age-based cleanup failed: {e}")
            return {
                'error': str(e),
                'cleanup_time': timezone.now().isoformat()
            }


class OnPremisesValidator:
    """Service to validate that all OCR processing remains on-premises"""
    
    def __init__(self):
        self.audit_logger = OCRAuditLogger()
        self.blocked_domains = [
            'googleapis.com',
            'google.com',
            'googleapi.com',
            'gcp.com',
            'cloud.google.com'
        ]
    
    def validate_processing_location(self, processing_config: Dict[str, Any]) -> bool:
        """
        Validate that processing configuration ensures on-premises processing
        
        Args:
            processing_config: Configuration for OCR processing
            
        Returns:
            True if processing is guaranteed to be on-premises
        """
        try:
            # Check for any external service URLs
            service_url = processing_config.get('service_url', '')
            if service_url:
                for domain in self.blocked_domains:
                    if domain in service_url.lower():
                        self.audit_logger.log_security_event(
                            'external_service_blocked',
                            {
                                'service_url': service_url,
                                'blocked_domain': domain,
                                'action': 'processing_rejected'
                            },
                            severity='error'
                        )
                        return False
            
            # Check for cloud-based engines
            engines = processing_config.get('engines', [])
            for engine in engines:
                if isinstance(engine, dict):
                    engine_type = engine.get('type', '').lower()
                    if 'cloud' in engine_type or 'google' in engine_type:
                        self.audit_logger.log_security_event(
                            'cloud_engine_blocked',
                            {
                                'engine_type': engine_type,
                                'action': 'engine_rejected'
                            },
                            severity='error'
                        )
                        return False
            
            # Validate that local engines are configured
            local_engines = ['tesseract', 'easyocr', 'paddleocr']
            has_local_engine = any(
                engine.lower() in str(engines).lower() 
                for engine in local_engines
            )
            
            if not has_local_engine:
                self.audit_logger.log_security_event(
                    'no_local_engines',
                    {
                        'engines_configured': engines,
                        'action': 'validation_warning'
                    },
                    severity='warning'
                )
            
            return True
            
        except Exception as e:
            logger.error(f"On-premises validation failed: {e}")
            return False
    
    def validate_data_storage(self, storage_config: Dict[str, Any]) -> bool:
        """
        Validate that data storage is local/on-premises
        
        Args:
            storage_config: Storage configuration
            
        Returns:
            True if storage is on-premises
        """
        try:
            # Check storage paths
            storage_paths = [
                storage_config.get('temp_dir', ''),
                storage_config.get('media_root', ''),
                storage_config.get('upload_dir', '')
            ]
            
            for path in storage_paths:
                if path and ('://' in path or path.startswith('gs://') or path.startswith('s3://')):
                    self.audit_logger.log_security_event(
                        'external_storage_detected',
                        {
                            'storage_path': path,
                            'action': 'storage_rejected'
                        },
                        severity='error'
                    )
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Data storage validation failed: {e}")
            return False


# Factory functions for easy service access
def get_file_encryption_service() -> FileEncryptionService:
    """Get file encryption service instance"""
    return FileEncryptionService()


def get_ocr_auth_service() -> OCRAuthenticationService:
    """Get OCR authentication service instance"""
    return OCRAuthenticationService()


def get_audit_logger() -> OCRAuditLogger:
    """Get audit logger service instance"""
    return OCRAuditLogger()


def get_cleanup_service() -> SecureFileCleanupService:
    """Get secure file cleanup service instance"""
    return SecureFileCleanupService()


def get_premises_validator() -> OnPremisesValidator:
    """Get on-premises validator service instance"""
    return OnPremisesValidator()