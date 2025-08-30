"""
Management command for automated system health monitoring.

This command can be run periodically (via cron) to monitor system health
and send alerts when issues are detected.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from faktury.services.health_check_service import HealthCheckService
from faktury.views_modules.health_monitoring_views import HealthAlertingService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Monitor system health and send alerts if issues are detected'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only perform health check without sending alerts'
        )
        
        parser.add_argument(
            '--component',
            type=str,
            help='Check specific component only (database, ocr_services, static_assets, system_resources, cache)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed health information'
        )
        
        parser.add_argument(
            '--force-alert',
            action='store_true',
            help='Force send test alert regardless of system status'
        )

    def handle(self, *args, **options):
        """Execute the health monitoring command."""
        try:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Starting system health monitoring at {timezone.now()}"
                )
            )
            
            health_service = HealthCheckService()
            
            if options['component']:
                # Check specific component
                self._check_specific_component(health_service, options['component'], options['verbose'])
            else:
                # Full system health check
                self._perform_full_health_check(health_service, options)
            
            self.stdout.write(
                self.style.SUCCESS("System health monitoring completed successfully")
            )
            
        except Exception as e:
            logger.error(f"Health monitoring command failed: {e}")
            raise CommandError(f"Health monitoring failed: {e}")

    def _check_specific_component(self, health_service, component_name, verbose):
        """Check health of a specific component."""
        self.stdout.write(f"Checking {component_name} health...")
        
        try:
            if component_name == 'database':
                result = health_service.check_database_health()
            elif component_name == 'ocr_services':
                result = health_service.check_ocr_services()
            elif component_name == 'static_assets':
                result = health_service.check_static_assets()
            elif component_name == 'system_resources':
                result = health_service.check_system_resources()
            elif component_name == 'cache':
                result = health_service.check_cache_health()
            else:
                raise CommandError(f"Unknown component: {component_name}")
            
            # Display results
            status_style = self._get_status_style(result['status'])
            self.stdout.write(
                status_style(f"{component_name}: {result['status'].upper()}")
            )
            
            if verbose:
                self._display_component_details(result)
            
            if result.get('errors'):
                for error in result['errors']:
                    self.stdout.write(self.style.ERROR(f"  Error: {error}"))
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to check {component_name}: {e}")
            )

    def _perform_full_health_check(self, health_service, options):
        """Perform full system health check."""
        self.stdout.write("Performing comprehensive health check...")
        
        # Generate health report
        health_report = health_service.generate_health_report()
        
        # Display overall status
        overall_style = self._get_status_style(health_report['overall_status'])
        self.stdout.write(
            overall_style(f"Overall System Status: {health_report['overall_status'].upper()}")
        )
        
        # Display component summary
        summary = health_report['summary']
        self.stdout.write(f"Components Summary:")
        self.stdout.write(f"  Healthy: {summary['healthy_components']}")
        self.stdout.write(f"  Warnings: {summary['warning_components']}")
        self.stdout.write(f"  Errors: {summary['error_components']}")
        
        if options['verbose']:
            self._display_detailed_report(health_report)
        
        # Handle alerting
        if not options['check_only']:
            self._handle_alerting(health_report, options['force_alert'])

    def _display_detailed_report(self, health_report):
        """Display detailed health report."""
        self.stdout.write("\nDetailed Component Status:")
        
        for component_name, component_data in health_report['components'].items():
            status_style = self._get_status_style(component_data['status'])
            self.stdout.write(
                status_style(f"\n{component_name.replace('_', ' ').title()}: {component_data['status'].upper()}")
            )
            
            self._display_component_details(component_data)
            
            if component_data.get('errors'):
                for error in component_data['errors']:
                    self.stdout.write(self.style.ERROR(f"    Error: {error}"))

    def _display_component_details(self, component_data):
        """Display component-specific details."""
        # Database details
        if 'response_time' in component_data:
            self.stdout.write(f"    Response Time: {component_data['response_time']}ms")
        
        if 'connection_count' in component_data:
            self.stdout.write(f"    Connections: {component_data['connection_count']}")
        
        # OCR services details
        if 'engines' in component_data:
            self.stdout.write("    OCR Engines:")
            for engine_name, engine_data in component_data['engines'].items():
                status = "Available" if engine_data['available'] else "Unavailable"
                success_rate = engine_data.get('success_rate', 0)
                self.stdout.write(f"      {engine_name}: {status} ({success_rate}% success)")
        
        # System resources details
        if 'cpu_usage' in component_data:
            self.stdout.write(f"    CPU Usage: {component_data['cpu_usage']}%")
        
        if 'memory_usage' in component_data:
            memory = component_data['memory_usage']
            self.stdout.write(f"    Memory Usage: {memory.get('used_percent', 0)}%")
        
        if 'disk_usage' in component_data:
            disk = component_data['disk_usage']
            self.stdout.write(f"    Disk Usage: {disk.get('used_percent', 0)}%")
        
        # Cache details
        if 'cache_backend' in component_data:
            self.stdout.write(f"    Cache Backend: {component_data['cache_backend']}")
            test_result = "Passed" if component_data.get('test_result') else "Failed"
            self.stdout.write(f"    Test Result: {test_result}")

    def _handle_alerting(self, health_report, force_alert):
        """Handle alert sending based on health status."""
        try:
            alerting_service = HealthAlertingService()
            
            if force_alert:
                self.stdout.write("Forcing test alert...")
                # Send a test alert
                test_message = f"""
TEST ALERT - FaktuLove System Health Monitoring

This is a test alert to verify the alerting system is working.

Current System Status: {health_report['overall_status'].upper()}
Timestamp: {health_report['timestamp']}

If you receive this message, the health monitoring system is functioning correctly.
                """.strip()
                
                success = alerting_service._send_alert("Test Alert", test_message)
                if success:
                    self.stdout.write(self.style.SUCCESS("Test alert sent successfully"))
                else:
                    self.stdout.write(self.style.WARNING("Failed to send test alert"))
            else:
                # Normal alert checking
                alert_result = alerting_service.check_and_send_alerts()
                
                if alert_result.get('alerts_sent'):
                    alerts = ', '.join(alert_result['alerts_sent'])
                    self.stdout.write(
                        self.style.WARNING(f"Alerts sent: {alerts}")
                    )
                else:
                    self.stdout.write("No alerts needed - system is healthy")
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to handle alerting: {e}")
            )

    def _get_status_style(self, status):
        """Get appropriate style for status."""
        if status == 'healthy':
            return self.style.SUCCESS
        elif status == 'warning':
            return self.style.WARNING
        else:
            return self.style.ERROR