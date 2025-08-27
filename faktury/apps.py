"""
Django app configuration for faktury application
"""

from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FakturyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faktury'
    verbose_name = 'FaktuLove Invoice Management'
    
    def ready(self):
        """
        Called when Django starts up.
        Perform startup checks and configuration validation.
        """
        # Import signals to ensure they are registered
        try:
            from . import signals
        except ImportError:
            pass
        
        # Run OCR configuration validation if enabled
        self._validate_ocr_configuration()
    
    def _validate_ocr_configuration(self):
        """Validate OCR configuration during startup"""
        try:
            # Check if validation is enabled
            flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
            if not flags.get('validate_ocr_config', False):
                return
            
            # Skip validation during migrations and certain management commands
            import sys
            if len(sys.argv) > 1:
                command = sys.argv[1]
                skip_commands = ['migrate', 'makemigrations', 'collectstatic', 'shell', 'test']
                if command in skip_commands:
                    return
            
            # Import and run validation
            from faktury.services.ocr_config_validator import check_startup_requirements
            
            logger.info("Running OCR configuration validation during startup...")
            
            if check_startup_requirements():
                logger.info("✅ OCR configuration validation passed")
            else:
                logger.warning("⚠️  OCR configuration validation found issues - check logs for details")
                
        except ImportError:
            # OCR validator not available - skip validation
            logger.debug("OCR configuration validator not available - skipping startup validation")
        except Exception as e:
            # Don't fail startup due to validation errors
            logger.warning(f"OCR configuration validation failed during startup: {e}")