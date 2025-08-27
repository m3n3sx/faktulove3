"""
Django management command to validate OCR configuration
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from faktury.services.ocr_config_validator import validate_ocr_configuration
import json


class Command(BaseCommand):
    help = 'Validate OCR system configuration and service availability'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results in JSON format',
        )
        parser.add_argument(
            '--fail-on-warnings',
            action='store_true',
            help='Exit with error code if warnings are found',
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Only show errors and warnings',
        )
    
    def handle(self, *args, **options):
        """Run OCR configuration validation"""
        
        self.stdout.write(
            self.style.HTTP_INFO('🔍 Validating OCR Configuration...\n')
        )
        
        try:
            # Run validation
            results = validate_ocr_configuration()
            
            # Output results
            if options['json']:
                self.stdout.write(json.dumps(results, indent=2))
                return
            
            # Human-readable output
            self._display_results(results, options)
            
            # Determine exit code
            if not results['is_valid']:
                raise CommandError("OCR configuration validation failed")
            
            if options['fail_on_warnings'] and results['warnings']:
                raise CommandError(f"OCR configuration has {len(results['warnings'])} warnings")
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ OCR configuration validation completed successfully')
            )
            
        except Exception as e:
            raise CommandError(f"Validation failed: {e}")
    
    def _display_results(self, results, options):
        """Display validation results in human-readable format"""
        
        # Display summary
        self.stdout.write(f"📊 {results['summary']}\n")
        
        # Display errors
        if results['errors']:
            self.stdout.write(self.style.ERROR('❌ ERRORS:'))
            for error in results['errors']:
                self.stdout.write(f"   • {error}")
            self.stdout.write('')
        
        # Display warnings
        if results['warnings']:
            self.stdout.write(self.style.WARNING('⚠️  WARNINGS:'))
            for warning in results['warnings']:
                self.stdout.write(f"   • {warning}")
            self.stdout.write('')
        
        # Display info (unless quiet mode)
        if results['info'] and not options['quiet']:
            self.stdout.write(self.style.HTTP_INFO('ℹ️  INFORMATION:'))
            for info in results['info']:
                self.stdout.write(f"   • {info}")
            self.stdout.write('')
        
        # Display configuration summary
        if not options['quiet']:
            self._display_config_summary()
    
    def _display_config_summary(self):
        """Display current OCR configuration summary"""
        self.stdout.write(self.style.HTTP_INFO('⚙️  CURRENT CONFIGURATION:'))
        
        # Feature flags
        flags = getattr(settings, 'OCR_FEATURE_FLAGS', {})
        self.stdout.write(f"   • Open Source OCR: {'✅' if flags.get('use_opensource_ocr') else '❌'}")
        self.stdout.write(f"   • PaddleOCR Primary: {'✅' if flags.get('paddleocr_primary') else '❌'}")
        self.stdout.write(f"   • Google Cloud Disabled: {'✅' if flags.get('disable_google_cloud') else '❌'}")
        self.stdout.write(f"   • Config Validation: {'✅' if flags.get('validate_ocr_config') else '❌'}")
        
        # PaddleOCR configuration
        paddleocr_config = getattr(settings, 'PADDLEOCR_CONFIG', {})
        if paddleocr_config:
            enabled = paddleocr_config.get('enabled', False)
            self.stdout.write(f"   • PaddleOCR Enabled: {'✅' if enabled else '❌'}")
            
            if enabled:
                languages = paddleocr_config.get('languages', [])
                self.stdout.write(f"   • PaddleOCR Languages: {', '.join(languages) if languages else 'None'}")
                
                use_gpu = paddleocr_config.get('use_gpu', False)
                self.stdout.write(f"   • PaddleOCR GPU: {'✅' if use_gpu else '❌'}")
                
                max_memory = paddleocr_config.get('max_memory_mb', 'Not configured')
                self.stdout.write(f"   • PaddleOCR Memory Limit: {max_memory}MB")
                
                max_workers = paddleocr_config.get('max_workers', 'Not configured')
                self.stdout.write(f"   • PaddleOCR Workers: {max_workers}")
        
        # OCR service configuration
        ocr_config = getattr(settings, 'OCR_CONFIG', {})
        if ocr_config:
            service_url = ocr_config.get('service_url', 'Not configured')
            self.stdout.write(f"   • Service URL: {service_url}")
            
            timeout = ocr_config.get('timeout', 'Not configured')
            self.stdout.write(f"   • Timeout: {timeout}s")
            
            engines = ocr_config.get('engines', {})
            enabled_engines = [name for name, config in engines.items() if config.get('enabled')]
            self.stdout.write(f"   • Enabled Engines: {', '.join(enabled_engines) if enabled_engines else 'None'}")
        
        # OCR Engine Priority
        engine_priority = getattr(settings, 'OCR_ENGINE_PRIORITY', [])
        if engine_priority:
            self.stdout.write(f"   • Engine Priority: {' → '.join(engine_priority)}")
        
        self.stdout.write('')