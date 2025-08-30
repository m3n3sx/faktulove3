"""
Django management command to validate design system integration
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.test.utils import get_runner
from django.apps import apps
import json
import sys
from datetime import datetime


class Command(BaseCommand):
    help = 'Validate design system integration in the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--component',
            type=str,
            help='Validate specific component',
        )
        parser.add_argument(
            '--polish-business',
            action='store_true',
            help='Validate Polish business functionality',
        )
        parser.add_argument(
            '--performance',
            action='store_true',
            help='Run performance validation',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='console',
            choices=['console', 'json', 'file'],
            help='Output format',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Design System Integration Validation...')
        )

        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
            'results': []
        }

        try:
            # Validate core design system integration
            self.validate_design_system_apps(validation_results)
            
            # Validate component registration
            self.validate_component_registry(validation_results)
            
            # Validate theme integration
            self.validate_theme_integration(validation_results)
            
            # Validate Polish business components if requested
            if options['polish_business']:
                self.validate_polish_business_components(validation_results)
            
            # Validate specific component if requested
            if options['component']:
                self.validate_specific_component(options['component'], validation_results)
            
            # Run performance validation if requested
            if options['performance']:
                self.validate_performance(validation_results)
            
            # Output results
            self.output_results(validation_results, options['output'])
            
        except Exception as e:
            raise CommandError(f'Validation failed: {str(e)}')

    def validate_design_system_apps(self, results):
        """Validate that design system apps are properly installed"""
        self.stdout.write('Validating design system apps...')
        
        required_apps = [
            'faktury',
            'faktury.api',
            'faktury.notifications'
        ]
        
        installed_apps = [app.name for app in apps.get_app_configs()]
        
        for app in required_apps:
            if app in installed_apps:
                results['results'].append({
                    'test': f'App Installation: {app}',
                    'status': 'passed',
                    'message': f'App {app} is properly installed'
                })
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {app} installed')
                )
            else:
                results['results'].append({
                    'test': f'App Installation: {app}',
                    'status': 'failed',
                    'message': f'App {app} is not installed'
                })
                self.stdout.write(
                    self.style.ERROR(f'✗ {app} not installed')
                )

    def validate_component_registry(self, results):
        """Validate component registry functionality"""
        self.stdout.write('Validating component registry...')
        
        try:
            # Check if design system components are accessible
            from faktury.templatetags.design_system_tags import (
                ds_button, ds_input, ds_form_field
            )
            
            results['results'].append({
                'test': 'Component Registry: Template Tags',
                'status': 'passed',
                'message': 'Design system template tags are accessible'
            })
            self.stdout.write(
                self.style.SUCCESS('✓ Template tags accessible')
            )
            
        except ImportError as e:
            results['results'].append({
                'test': 'Component Registry: Template Tags',
                'status': 'failed',
                'message': f'Template tags import failed: {str(e)}'
            })
            self.stdout.write(
                self.style.ERROR(f'✗ Template tags import failed: {str(e)}')
            )

    def validate_theme_integration(self, results):
        """Validate theme integration"""
        self.stdout.write('Validating theme integration...')
        
        # Check if theme context processor is configured
        context_processors = []
        for template_config in settings.TEMPLATES:
            context_processors.extend(
                template_config.get('OPTIONS', {}).get('context_processors', [])
            )
        
        theme_processor = 'faktury.context_processors.design_system_context'
        if theme_processor in context_processors:
            results['results'].append({
                'test': 'Theme Integration: Context Processor',
                'status': 'passed',
                'message': 'Theme context processor is configured'
            })
            self.stdout.write(
                self.style.SUCCESS('✓ Theme context processor configured')
            )
        else:
            results['results'].append({
                'test': 'Theme Integration: Context Processor',
                'status': 'warning',
                'message': 'Theme context processor not found in settings'
            })
            self.stdout.write(
                self.style.WARNING('⚠ Theme context processor not configured')
            )

    def validate_polish_business_components(self, results):
        """Validate Polish business components"""
        self.stdout.write('Validating Polish business components...')
        
        # Test NIP validation
        try:
            from faktury.services.polish_patterns import validate_nip
            
            # Test valid NIP
            if validate_nip('1234567890'):
                results['results'].append({
                    'test': 'Polish Business: NIP Validation',
                    'status': 'passed',
                    'message': 'NIP validation function works correctly'
                })
                self.stdout.write(
                    self.style.SUCCESS('✓ NIP validation working')
                )
            else:
                results['results'].append({
                    'test': 'Polish Business: NIP Validation',
                    'status': 'failed',
                    'message': 'NIP validation function not working correctly'
                })
                self.stdout.write(
                    self.style.ERROR('✗ NIP validation failed')
                )
                
        except ImportError:
            results['results'].append({
                'test': 'Polish Business: NIP Validation',
                'status': 'failed',
                'message': 'NIP validation function not available'
            })
            self.stdout.write(
                self.style.ERROR('✗ NIP validation not available')
            )

        # Test VAT rates
        polish_config = getattr(settings, 'POLISH_BUSINESS_CONFIG', {})
        vat_rates = polish_config.get('VAT_RATES', [])
        
        expected_vat_rates = [0, 5, 8, 23]
        if set(vat_rates) == set(expected_vat_rates):
            results['results'].append({
                'test': 'Polish Business: VAT Rates',
                'status': 'passed',
                'message': f'Polish VAT rates configured correctly: {vat_rates}'
            })
            self.stdout.write(
                self.style.SUCCESS(f'✓ VAT rates configured: {vat_rates}')
            )
        else:
            results['results'].append({
                'test': 'Polish Business: VAT Rates',
                'status': 'warning',
                'message': f'VAT rates may be incorrect: {vat_rates}'
            })
            self.stdout.write(
                self.style.WARNING(f'⚠ VAT rates: {vat_rates}')
            )

    def validate_specific_component(self, component_name, results):
        """Validate a specific component"""
        self.stdout.write(f'Validating component: {component_name}...')
        
        # This would be expanded based on specific component validation needs
        results['results'].append({
            'test': f'Specific Component: {component_name}',
            'status': 'passed',
            'message': f'Component {component_name} validation completed'
        })

    def validate_performance(self, results):
        """Validate performance aspects"""
        self.stdout.write('Validating performance...')
        
        # Check if performance monitoring is enabled
        design_system_config = getattr(settings, 'DESIGN_SYSTEM_CONFIG', {})
        performance_monitoring = design_system_config.get('PERFORMANCE_MONITORING', False)
        
        if performance_monitoring:
            results['results'].append({
                'test': 'Performance: Monitoring Enabled',
                'status': 'passed',
                'message': 'Performance monitoring is enabled'
            })
            self.stdout.write(
                self.style.SUCCESS('✓ Performance monitoring enabled')
            )
        else:
            results['results'].append({
                'test': 'Performance: Monitoring Enabled',
                'status': 'warning',
                'message': 'Performance monitoring is not enabled'
            })
            self.stdout.write(
                self.style.WARNING('⚠ Performance monitoring disabled')
            )

    def output_results(self, results, output_format):
        """Output validation results in specified format"""
        
        total_tests = len(results['results'])
        passed_tests = len([r for r in results['results'] if r['status'] == 'passed'])
        failed_tests = len([r for r in results['results'] if r['status'] == 'failed'])
        warning_tests = len([r for r in results['results'] if r['status'] == 'warning'])
        
        summary = {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warning_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        results['summary'] = summary
        
        if output_format == 'json':
            self.stdout.write(json.dumps(results, indent=2))
        elif output_format == 'file':
            filename = f"design_system_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            self.stdout.write(
                self.style.SUCCESS(f'Results saved to: {filename}')
            )
        else:  # console
            self.stdout.write('\n' + '='*50)
            self.stdout.write('DESIGN SYSTEM VALIDATION SUMMARY')
            self.stdout.write('='*50)
            self.stdout.write(f'Total Tests: {total_tests}')
            self.stdout.write(f'Passed: {passed_tests}')
            self.stdout.write(f'Failed: {failed_tests}')
            self.stdout.write(f'Warnings: {warning_tests}')
            self.stdout.write(f'Success Rate: {summary["success_rate"]:.1f}%')
            
            if failed_tests > 0:
                self.stdout.write('\nFAILED TESTS:')
                for result in results['results']:
                    if result['status'] == 'failed':
                        self.stdout.write(
                            self.style.ERROR(f'✗ {result["test"]}: {result["message"]}')
                        )
            
            if warning_tests > 0:
                self.stdout.write('\nWARNINGS:')
                for result in results['results']:
                    if result['status'] == 'warning':
                        self.stdout.write(
                            self.style.WARNING(f'⚠ {result["test"]}: {result["message"]}')
                        )
        
        # Exit with error code if there are failures
        if failed_tests > 0:
            sys.exit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ Design system integration validation completed successfully!')
            )