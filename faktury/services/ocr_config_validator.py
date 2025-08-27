"""
OCR Configuration Validator

This module provides validation and startup checks for the OCR system
to ensure proper configuration and availability of required services.
"""

import logging
import os
import requests
from typing import Dict, List, Tuple, Any
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class OCRConfigValidator:
    """Validates OCR system configuration and service availability"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation checks
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Starting OCR configuration validation...")
        
        # Reset validation state
        self.errors = []
        self.warnings = []
        self.info = []
        
        # Run validation checks
        self._validate_feature_flags()
        self._validate_ocr_config()
        self._validate_paddleocr_config()
        self._validate_service_availability()
        self._validate_google_cloud_removal()
        self._validate_environment_variables()
        self._validate_dependencies()
        
        # Compile results
        results = {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'summary': self._generate_summary()
        }
        
        # Log results
        if results['is_valid']:
            logger.info("OCR configuration validation passed")
        else:
            logger.error(f"OCR configuration validation failed with {len(self.errors)} errors")
        
        return results
    
    def _validate_feature_flags(self):
        """Validate OCR feature flags configuration"""
        try:
            flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
            
            if not flags:
                self.errors.append("OCR_FEATURE_FLAGS not configured in settings")
                return
            
            # Check required flags
            required_flags = ['use_opensource_ocr', 'disable_google_cloud', 'validate_ocr_config']
            for flag in required_flags:
                if flag not in flags:
                    self.warnings.append(f"Missing feature flag: {flag}")
                elif flags[flag]:
                    self.info.append(f"Feature flag enabled: {flag}")
            
            # Validate flag consistency
            if flags.get('use_opensource_ocr') and not flags.get('disable_google_cloud'):
                self.warnings.append("Using open source OCR but Google Cloud not disabled")
            
        except Exception as e:
            self.errors.append(f"Error validating feature flags: {e}")
    
    def _validate_ocr_config(self):
        """Validate OCR configuration settings"""
        try:
            ocr_config = getattr(settings, 'OCR_CONFIG', {})
            
            if not ocr_config:
                self.errors.append("OCR_CONFIG not found in settings")
                return
            
            # Check required configuration keys
            required_keys = ['service_url', 'timeout', 'max_retries', 'engines']
            for key in required_keys:
                if key not in ocr_config:
                    self.errors.append(f"Missing OCR config key: {key}")
            
            # Validate engines configuration
            engines = ocr_config.get('engines', {})
            if not engines:
                self.errors.append("No OCR engines configured")
            else:
                for engine_name, engine_config in engines.items():
                    if not engine_config.get('enabled', False):
                        self.warnings.append(f"OCR engine disabled: {engine_name}")
                    else:
                        self.info.append(f"OCR engine enabled: {engine_name}")
            
            # Validate file size limits
            max_file_size = ocr_config.get('max_file_size')
            if not max_file_size or max_file_size <= 0:
                self.warnings.append("Invalid or missing max_file_size configuration")
            
        except Exception as e:
            self.errors.append(f"Error validating OCR config: {e}")
    
    def _validate_paddleocr_config(self):
        """Validate PaddleOCR configuration settings"""
        try:
            paddleocr_config = getattr(settings, 'PADDLEOCR_CONFIG', {})
            
            if not paddleocr_config:
                self.warnings.append("PADDLEOCR_CONFIG not found in settings")
                return
            
            # Check if PaddleOCR is enabled
            if not paddleocr_config.get('enabled', False):
                self.info.append("PaddleOCR is disabled")
                return
            
            self.info.append("PaddleOCR is enabled")
            
            # Validate core configuration
            required_keys = ['languages', 'model_dir', 'timeout', 'max_retries']
            for key in required_keys:
                if key not in paddleocr_config:
                    self.errors.append(f"Missing PaddleOCR config key: {key}")
            
            # Validate model directory
            model_dir = paddleocr_config.get('model_dir')
            if model_dir and not os.path.exists(model_dir):
                self.warnings.append(f"PaddleOCR model directory does not exist: {model_dir}")
            elif model_dir:
                self.info.append(f"PaddleOCR model directory configured: {model_dir}")
            
            # Validate languages
            languages = paddleocr_config.get('languages', [])
            if not languages:
                self.errors.append("PaddleOCR languages not configured")
            elif 'pl' not in languages:
                self.warnings.append("Polish language not configured for PaddleOCR")
            else:
                self.info.append(f"PaddleOCR languages configured: {', '.join(languages)}")
            
            # Validate memory settings
            memory_config = paddleocr_config.get('memory', {})
            max_memory = memory_config.get('max_memory_mb', 0)
            warning_threshold = memory_config.get('warning_threshold_mb', 0)
            critical_threshold = memory_config.get('critical_threshold_mb', 0)
            
            if max_memory <= 0:
                self.errors.append("PaddleOCR max_memory_mb must be greater than 0")
            elif warning_threshold >= critical_threshold:
                self.errors.append("PaddleOCR memory warning threshold must be less than critical threshold")
            elif critical_threshold >= max_memory:
                self.errors.append("PaddleOCR memory critical threshold must be less than max memory")
            else:
                self.info.append(f"PaddleOCR memory limits configured: {max_memory}MB max")
            
            # Validate timeout settings
            timeouts = paddleocr_config.get('timeouts', {})
            processing_timeout = timeouts.get('processing', 0)
            if processing_timeout <= 0:
                self.errors.append("PaddleOCR processing timeout must be greater than 0")
            else:
                self.info.append(f"PaddleOCR processing timeout: {processing_timeout}s")
            
            # Validate confidence settings
            confidence = paddleocr_config.get('confidence', {})
            min_threshold = confidence.get('min_threshold', -1)
            high_threshold = confidence.get('high_threshold', -1)
            
            if not (0 <= min_threshold <= 1):
                self.errors.append("PaddleOCR confidence min_threshold must be between 0 and 1")
            elif not (0 <= high_threshold <= 1):
                self.errors.append("PaddleOCR confidence high_threshold must be between 0 and 1")
            elif min_threshold >= high_threshold:
                self.errors.append("PaddleOCR confidence min_threshold must be less than high_threshold")
            else:
                self.info.append(f"PaddleOCR confidence thresholds: {min_threshold} - {high_threshold}")
            
            # Validate worker settings
            max_workers = paddleocr_config.get('max_workers', 0)
            if max_workers <= 0:
                self.errors.append("PaddleOCR max_workers must be greater than 0")
            else:
                self.info.append(f"PaddleOCR max workers: {max_workers}")
            
            # Validate performance configuration
            perf_config = getattr(settings, 'PADDLEOCR_PERFORMANCE_CONFIG', {})
            if perf_config:
                max_concurrent = perf_config.get('max_concurrent_requests', 0)
                if max_concurrent <= 0:
                    self.errors.append("PaddleOCR max_concurrent_requests must be greater than 0")
                else:
                    self.info.append(f"PaddleOCR max concurrent requests: {max_concurrent}")
            
            # Validate GPU settings
            use_gpu = paddleocr_config.get('use_gpu', False)
            if use_gpu:
                self.info.append("PaddleOCR GPU acceleration enabled")
                # Check if GPU is actually available (optional check)
                try:
                    import paddle
                    if paddle.device.is_compiled_with_cuda():
                        self.info.append("CUDA support available for PaddleOCR")
                    else:
                        self.warnings.append("GPU enabled but CUDA not available")
                except ImportError:
                    self.warnings.append("GPU enabled but PaddlePaddle not available for verification")
            else:
                self.info.append("PaddleOCR using CPU mode")
            
            # Validate preprocessing settings
            preprocessing = paddleocr_config.get('preprocessing', {})
            if preprocessing.get('enabled', False):
                enabled_features = [k for k, v in preprocessing.items() if v and k != 'enabled']
                self.info.append(f"PaddleOCR preprocessing enabled: {', '.join(enabled_features)}")
            
            # Validate Polish optimization settings
            polish_opt = paddleocr_config.get('polish_optimization', {})
            if polish_opt.get('enabled', False):
                enabled_features = [k for k, v in polish_opt.items() if v and k != 'enabled']
                self.info.append(f"PaddleOCR Polish optimization enabled: {', '.join(enabled_features)}")
            
            # Validate fallback configuration
            fallback = paddleocr_config.get('fallback', {})
            if fallback.get('enabled', False):
                fallback_engines = fallback.get('fallback_engines', [])
                if fallback_engines:
                    self.info.append(f"PaddleOCR fallback engines: {', '.join(fallback_engines)}")
                else:
                    self.warnings.append("PaddleOCR fallback enabled but no fallback engines configured")
            
        except Exception as e:
            self.errors.append(f"Error validating PaddleOCR config: {e}")
    
    def _validate_service_availability(self):
        """Check if OCR service is available"""
        try:
            ocr_config = getattr(settings, 'OCR_CONFIG', {})
            service_url = ocr_config.get('service_url')
            
            if not service_url:
                self.errors.append("OCR service URL not configured")
                return
            
            # Try to connect to OCR service
            timeout = ocr_config.get('timeout', 30)
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                if response.status_code == 200:
                    self.info.append(f"OCR service available at {service_url}")
                else:
                    self.warnings.append(f"OCR service returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.warnings.append(f"OCR service not available at {service_url}: {e}")
            
        except Exception as e:
            self.errors.append(f"Error checking service availability: {e}")
    
    def _validate_google_cloud_removal(self):
        """Validate that Google Cloud dependencies are properly removed"""
        try:
            # Check for deprecated Google Cloud settings
            deprecated_settings = [
                'GOOGLE_CLOUD_PROJECT',
                'GOOGLE_APPLICATION_CREDENTIALS', 
                'DOCUMENT_AI_CONFIG'
            ]
            
            for setting_name in deprecated_settings:
                if hasattr(settings, setting_name):
                    value = getattr(settings, setting_name)
                    if value:
                        self.warnings.append(f"Deprecated Google Cloud setting still present: {setting_name}")
            
            # Check environment variables
            deprecated_env_vars = [
                'GOOGLE_CLOUD_PROJECT',
                'GOOGLE_APPLICATION_CREDENTIALS',
                'DOCUMENT_AI_PROCESSOR_ID'
            ]
            
            for env_var in deprecated_env_vars:
                if os.getenv(env_var):
                    self.warnings.append(f"Deprecated Google Cloud environment variable: {env_var}")
            
            # Check feature flags
            flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
            if not flags.get('disable_google_cloud'):
                self.warnings.append("Google Cloud not explicitly disabled in feature flags")
            else:
                self.info.append("Google Cloud properly disabled")
            
        except Exception as e:
            self.errors.append(f"Error validating Google Cloud removal: {e}")
    
    def _validate_environment_variables(self):
        """Validate required environment variables"""
        try:
            # Check for required OCR environment variables
            required_env_vars = {
                'USE_OPENSOURCE_OCR': 'Open source OCR flag',
                'DISABLE_GOOGLE_CLOUD': 'Google Cloud disable flag',
            }
            
            # Check for PaddleOCR environment variables if enabled
            paddleocr_enabled = os.getenv('PADDLEOCR_ENABLED', 'True').lower() in ('true', '1', 'yes', 'on')
            if paddleocr_enabled:
                paddleocr_env_vars = {
                    'PADDLEOCR_MODEL_DIR': 'PaddleOCR model directory',
                    'PADDLEOCR_LANGUAGES': 'PaddleOCR languages',
                    'PADDLEOCR_MAX_MEMORY': 'PaddleOCR memory limit',
                    'PADDLEOCR_MAX_WORKERS': 'PaddleOCR worker count',
                    'PADDLEOCR_TIMEOUT': 'PaddleOCR processing timeout',
                }
                required_env_vars.update(paddleocr_env_vars)
            
            for env_var, description in required_env_vars.items():
                value = os.getenv(env_var)
                if not value:
                    self.warnings.append(f"Missing environment variable: {env_var} ({description})")
                elif value.lower() in ('true', '1', 'yes', 'on'):
                    self.info.append(f"Environment variable properly set: {env_var}")
            
            # Check for optional but recommended variables
            optional_env_vars = {
                'OCR_SERVICE_URL': 'OCR service endpoint',
                'OCR_TIMEOUT': 'OCR processing timeout',
                'OCR_MAX_RETRIES': 'OCR retry attempts',
            }
            
            for env_var, description in optional_env_vars.items():
                value = os.getenv(env_var)
                if not value:
                    self.info.append(f"Optional environment variable not set: {env_var} ({description})")
                else:
                    self.info.append(f"Optional environment variable set: {env_var}")
            
        except Exception as e:
            self.errors.append(f"Error validating environment variables: {e}")
    
    def _validate_dependencies(self):
        """Validate that required dependencies are available"""
        try:
            # Check for open source OCR dependencies
            required_modules = [
                ('cv2', 'OpenCV for image processing'),
                ('PIL', 'Pillow for image handling'),
                ('numpy', 'NumPy for numerical operations'),
                ('requests', 'Requests for HTTP communication'),
            ]
            
            for module_name, description in required_modules:
                try:
                    __import__(module_name)
                    self.info.append(f"Required dependency available: {module_name}")
                except ImportError:
                    self.errors.append(f"Missing required dependency: {module_name} ({description})")
            
            # Check for optional but recommended modules
            optional_modules = [
                ('tesseract', 'Tesseract OCR engine'),
                ('easyocr', 'EasyOCR engine'),
                ('pdf2image', 'PDF to image conversion'),
            ]
            
            # Check for PaddleOCR dependencies if enabled
            paddleocr_enabled = getattr(settings, 'PADDLEOCR_CONFIG', {}).get('enabled', False)
            if paddleocr_enabled:
                paddleocr_modules = [
                    ('paddlepaddle', 'PaddlePaddle framework'),
                    ('paddleocr', 'PaddleOCR library'),
                ]
                optional_modules.extend(paddleocr_modules)
            
            for module_name, description in optional_modules:
                try:
                    __import__(module_name)
                    self.info.append(f"Optional dependency available: {module_name}")
                except ImportError:
                    self.warnings.append(f"Optional dependency not available: {module_name} ({description})")
            
            # Check for deprecated Google Cloud dependencies
            deprecated_modules = [
                ('google.cloud.documentai', 'Google Cloud Document AI'),
                ('google.auth', 'Google Cloud Authentication'),
            ]
            
            for module_name, description in deprecated_modules:
                try:
                    __import__(module_name)
                    self.warnings.append(f"Deprecated dependency still installed: {module_name} ({description})")
                except ImportError:
                    self.info.append(f"Deprecated dependency properly removed: {module_name}")
            
        except Exception as e:
            self.errors.append(f"Error validating dependencies: {e}")
    
    def _generate_summary(self) -> str:
        """Generate a summary of validation results"""
        total_checks = len(self.errors) + len(self.warnings) + len(self.info)
        
        if len(self.errors) == 0:
            if len(self.warnings) == 0:
                return f"✅ All {total_checks} validation checks passed successfully"
            else:
                return f"⚠️  Validation passed with {len(self.warnings)} warnings out of {total_checks} checks"
        else:
            return f"❌ Validation failed with {len(self.errors)} errors and {len(self.warnings)} warnings out of {total_checks} checks"


def validate_ocr_configuration() -> Dict[str, Any]:
    """
    Convenience function to validate OCR configuration
    
    Returns:
        Dictionary with validation results
    """
    validator = OCRConfigValidator()
    return validator.validate_all()


def check_startup_requirements() -> bool:
    """
    Check if all startup requirements are met for OCR system
    
    Returns:
        True if all requirements are met, False otherwise
    """
    try:
        results = validate_ocr_configuration()
        
        # Log summary
        logger.info(results['summary'])
        
        # Log errors and warnings
        for error in results['errors']:
            logger.error(f"OCR Config Error: {error}")
        
        for warning in results['warnings']:
            logger.warning(f"OCR Config Warning: {warning}")
        
        # Return validation status
        return results['is_valid']
        
    except Exception as e:
        logger.error(f"Failed to check startup requirements: {e}")
        return False