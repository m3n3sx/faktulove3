"""
OCR Service Factory for Seamless Implementation Switching

This factory provides a seamless way to switch between Google Cloud Document AI
and the new Open Source OCR implementation while maintaining backward compatibility.
"""

import logging
from typing import Union, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class OCRServiceFactory:
    """
    Factory class for creating OCR service instances
    
    This factory allows seamless switching between different OCR implementations
    based on configuration settings, with automatic fallback mechanisms.
    """
    
    _instance = None
    _service_cache = {}
    
    @classmethod
    def get_ocr_service(cls, force_implementation: Optional[str] = None):
        """
        Get OCR service instance based on configuration
        
        Args:
            force_implementation: Force specific implementation ('google', 'opensource', 'mock')
            
        Returns:
            OCR service instance (DocumentAIService or OpenSourceOCRService)
        """
        # Determine which implementation to use
        implementation = force_implementation or cls._get_configured_implementation()
        
        # Check cache first
        if implementation in cls._service_cache:
            cached_service = cls._service_cache[implementation]
            if cls._validate_service(cached_service):
                return cached_service
            else:
                # Remove invalid service from cache
                del cls._service_cache[implementation]
        
        # Create new service instance
        service = cls._create_service(implementation)
        
        # Cache the service if it's valid
        if service and cls._validate_service(service):
            cls._service_cache[implementation] = service
        
        return service
    
    @classmethod
    def _get_configured_implementation(cls) -> str:
        """Get the configured OCR implementation from settings"""
        # Check feature flags first
        flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
        
        # Check for explicit configuration
        ocr_implementation = getattr(settings, 'OCR_IMPLEMENTATION', None)
        
        if ocr_implementation:
            return ocr_implementation.lower()
        
        # Check OCR engine priority from settings
        engine_priority = getattr(settings, 'OCR_ENGINE_PRIORITY', ['paddleocr', 'opensource', 'google'])
        
        for engine in engine_priority:
            if engine == 'paddleocr' and flags.get('use_paddleocr', True):
                if cls._is_paddleocr_available():
                    return 'paddleocr'
            elif engine == 'opensource' and flags.get('use_opensource_ocr', True):
                if cls._is_opensource_available():
                    return 'opensource'
            elif engine == 'google' and not flags.get('disable_google_cloud', False):
                if cls._is_google_cloud_available():
                    return 'google'
        
        # Fallback logic
        if cls._is_paddleocr_available():
            return 'paddleocr'
        elif cls._is_opensource_available():
            return 'opensource'
        elif not flags.get('disable_google_cloud', False) and cls._is_google_cloud_available():
            return 'google'
        else:
            logger.warning("No OCR implementation available, falling back to mock")
            return 'mock'
    
    @classmethod
    def _create_service(cls, implementation: str):
        """Create OCR service instance for the specified implementation"""
        try:
            if implementation == 'google':
                return cls._create_google_service()
            elif implementation == 'opensource':
                return cls._create_opensource_service()
            elif implementation == 'paddleocr':
                return cls._create_paddleocr_service()
            elif implementation == 'mock':
                return cls._create_mock_service()
            else:
                logger.error(f"Unknown OCR implementation: {implementation}")
                return cls._create_fallback_service()
                
        except Exception as e:
            logger.error(f"Failed to create {implementation} OCR service: {e}")
            return cls._create_fallback_service()
    
    @classmethod
    def _create_google_service(cls):
        """Create Google Cloud Document AI service"""
        # Check if Google Cloud is disabled
        flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
        if flags.get('disable_google_cloud', False):
            raise RuntimeError("Google Cloud OCR is disabled by feature flag")
        
        try:
            from .document_ai_service import DocumentAIService
            service = DocumentAIService()
            logger.info("Created Google Cloud Document AI service")
            return service
        except Exception as e:
            logger.error(f"Failed to create Google Cloud service: {e}")
            raise
    
    @classmethod
    def _create_opensource_service(cls):
        """Create Open Source OCR service"""
        try:
            from .opensource_ocr_service import OpenSourceOCRService
            service = OpenSourceOCRService()
            logger.info("Created Open Source OCR service")
            return service
        except Exception as e:
            logger.error(f"Failed to create Open Source OCR service: {e}")
            raise
    
    @classmethod
    def _create_paddleocr_service(cls):
        """Create PaddleOCR service"""
        try:
            from .paddle_ocr_service import PaddleOCRService, MockPaddleOCRService
            
            # Try to create real PaddleOCR service first
            try:
                service = PaddleOCRService()
                logger.info("Created PaddleOCR service")
                return service
            except Exception as e:
                logger.warning(f"Failed to create PaddleOCR service, falling back to mock: {e}")
                service = MockPaddleOCRService()
                logger.info("Created Mock PaddleOCR service")
                return service
                
        except Exception as e:
            logger.error(f"Failed to create PaddleOCR service: {e}")
            raise
    
    @classmethod
    def _create_mock_service(cls):
        """Create mock OCR service"""
        try:
            # Try to create mock services in priority order
            try:
                from .paddle_ocr_service import MockPaddleOCRService
                service = MockPaddleOCRService()
                logger.info("Created Mock PaddleOCR service")
                return service
            except ImportError:
                pass
            
            try:
                from .opensource_ocr_service import MockOpenSourceOCRService
                service = MockOpenSourceOCRService()
                logger.info("Created Mock Open Source OCR service")
                return service
            except ImportError:
                pass
            
            try:
                from .document_ai_service import MockDocumentAIService
                service = MockDocumentAIService()
                logger.info("Created Mock Document AI service")
                return service
            except ImportError:
                pass
            
            raise ImportError("No mock OCR service available")
            
        except Exception as e:
            logger.error(f"Failed to create mock OCR service: {e}")
            raise
    
    @classmethod
    def _create_fallback_service(cls):
        """Create fallback service when primary service fails"""
        logger.warning("Creating fallback OCR service")
        
        # Check feature flags to determine fallback order
        flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
        
        # Use engine priority for fallback order
        engine_priority = getattr(settings, 'OCR_ENGINE_PRIORITY', ['paddleocr', 'opensource', 'google'])
        fallback_order = engine_priority + ['mock']  # Always include mock as final fallback
        
        # Remove disabled engines from fallback order
        if flags.get('disable_google_cloud', False):
            fallback_order = [engine for engine in fallback_order if engine != 'google']
        
        for fallback_impl in fallback_order:
            try:
                service = cls._create_service(fallback_impl)
                if service:
                    logger.info(f"Successfully created fallback service: {fallback_impl}")
                    return service
            except Exception as e:
                logger.debug(f"Fallback {fallback_impl} failed: {e}")
                continue
        
        # If all fallbacks fail, raise an error
        raise RuntimeError("All OCR service implementations failed to initialize")
    
    @classmethod
    def _is_google_cloud_available(cls) -> bool:
        """Check if Google Cloud Document AI is available"""
        try:
            # Check feature flags first
            flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
            if flags.get('disable_google_cloud', False):
                return False
            
            # Check for Google Cloud credentials
            google_credentials = getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', None)
            if not google_credentials:
                return False
            
            # Check for Document AI configuration
            document_ai_config = getattr(settings, 'DOCUMENT_AI_CONFIG', None)
            if not document_ai_config:
                return False
            
            # Check if required fields are present
            required_fields = ['project_id', 'location', 'processor_id']
            if not all(field in document_ai_config for field in required_fields):
                return False
            
            # Try to import Google Cloud libraries
            try:
                from google.cloud import documentai
                return True
            except ImportError:
                return False
                
        except Exception as e:
            logger.debug(f"Google Cloud availability check failed: {e}")
            return False
    
    @classmethod
    def _is_opensource_available(cls) -> bool:
        """Check if Open Source OCR is available"""
        try:
            # Check if OCR engines are configured
            ocr_engines_enabled = getattr(settings, 'OCR_ENGINES_ENABLED', True)
            if not ocr_engines_enabled:
                return False
            
            # Try to import required modules
            try:
                from .document_processor import DocumentProcessor
                from .ocr_engine_service import OCREngineFactory
                return True
            except ImportError as e:
                logger.debug(f"Open source OCR import failed: {e}")
                return False
                
        except Exception as e:
            logger.debug(f"Open source OCR availability check failed: {e}")
            return False
    
    @classmethod
    def _is_paddleocr_available(cls) -> bool:
        """Check if PaddleOCR is available"""
        try:
            # Check feature flags first
            flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
            if not flags.get('use_paddleocr', True):
                return False
            
            # Check PaddleOCR configuration
            paddleocr_config = getattr(settings, 'PADDLEOCR_CONFIG', {})
            if not paddleocr_config.get('enabled', True):
                return False
            
            # Try to import PaddleOCR modules
            try:
                import paddleocr
                from .paddle_ocr_service import PaddleOCRService
                return True
            except ImportError as e:
                logger.debug(f"PaddleOCR import failed: {e}")
                return False
                
        except Exception as e:
            logger.debug(f"PaddleOCR availability check failed: {e}")
            return False
    
    @classmethod
    def _validate_service(cls, service) -> bool:
        """Validate that a service instance is working"""
        try:
            if hasattr(service, 'validate_processor_availability'):
                return service.validate_processor_availability()
            else:
                # Basic validation - check if service has required methods
                required_methods = ['process_invoice', 'extract_invoice_fields']
                return all(hasattr(service, method) for method in required_methods)
        except Exception as e:
            logger.debug(f"Service validation failed: {e}")
            return False
    
    @classmethod
    def get_available_implementations(cls) -> list:
        """Get list of available OCR implementations"""
        implementations = []
        
        if cls._is_paddleocr_available():
            implementations.append('paddleocr')
        
        if cls._is_opensource_available():
            implementations.append('opensource')
        
        if cls._is_google_cloud_available():
            implementations.append('google')
        
        # Mock is always available
        implementations.append('mock')
        
        return implementations
    
    @classmethod
    def switch_implementation(cls, implementation: str) -> bool:
        """
        Switch to a different OCR implementation
        
        Args:
            implementation: Target implementation ('google', 'opensource', 'mock')
            
        Returns:
            bool: True if switch was successful
        """
        try:
            # Clear cache to force recreation
            cls._service_cache.clear()
            
            # Try to create the new service
            service = cls._create_service(implementation)
            
            if service and cls._validate_service(service):
                # Update configuration
                settings.OCR_IMPLEMENTATION = implementation
                cls._service_cache[implementation] = service
                logger.info(f"Successfully switched to {implementation} OCR implementation")
                return True
            else:
                logger.error(f"Failed to switch to {implementation} - service not available")
                return False
                
        except Exception as e:
            logger.error(f"Error switching to {implementation} implementation: {e}")
            return False
    
    @classmethod
    def clear_cache(cls):
        """Clear the service cache"""
        cls._service_cache.clear()
        logger.info("OCR service cache cleared")
    
    @classmethod
    def get_service_info(cls) -> dict:
        """Get information about current OCR service configuration"""
        current_impl = cls._get_configured_implementation()
        available_impls = cls.get_available_implementations()
        
        return {
            'current_implementation': current_impl,
            'available_implementations': available_impls,
            'cached_services': list(cls._service_cache.keys()),
            'paddleocr_available': cls._is_paddleocr_available(),
            'opensource_available': cls._is_opensource_available(),
            'google_cloud_available': cls._is_google_cloud_available()
        }


# Convenience functions for backward compatibility
def get_document_ai_service():
    """
    Factory function to get OCR service (maintains backward compatibility)
    
    This function maintains the same interface as the original get_document_ai_service
    but now returns the appropriate OCR service based on configuration.
    """
    return OCRServiceFactory.get_ocr_service()


def get_ocr_service(implementation: Optional[str] = None):
    """
    Get OCR service with optional implementation specification
    
    Args:
        implementation: Optional implementation to force ('google', 'opensource', 'mock')
        
    Returns:
        OCR service instance
    """
    return OCRServiceFactory.get_ocr_service(force_implementation=implementation)


def switch_ocr_implementation(implementation: str) -> bool:
    """
    Switch OCR implementation
    
    Args:
        implementation: Target implementation ('google', 'opensource', 'mock')
        
    Returns:
        bool: True if switch was successful
    """
    return OCRServiceFactory.switch_implementation(implementation)


def get_ocr_service_info() -> dict:
    """Get information about OCR service configuration"""
    return OCRServiceFactory.get_service_info()