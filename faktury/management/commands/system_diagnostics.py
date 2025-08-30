"""
Management command for system diagnostics and information collection.

Provides comprehensive system diagnostic information for troubleshooting.
"""

import json
import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from faktury.services.maintenance_service import MaintenanceService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Collect system diagnostic information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path for diagnostic report (default: stdout)'
        )
        
        parser.add_argument(
            '--format',
            choices=['json', 'text'],
            default='text',
            help='Output format (default: text)'
        )
        
        parser.add_argument(
            '--include-sensitive',
            action='store_true',
            help='Include sensitive information (use with caution)'
        )

    def handle(self, *args, **options):
        """Execute system diagnostics collection."""
        try:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Collecting system diagnostics at {timezone.now()}"
                )
            )
            
            maintenance_service = MaintenanceService()
            diagnostic_info = maintenance_service.collect_diagnostic_info()
            
            # Format and output diagnostic information
            if options['format'] == 'json':
                self._output_json_format(diagnostic_info, options)
            else:
                self._output_text_format(diagnostic_info, options)
            
            self.stdout.write(
                self.style.SUCCESS("System diagnostics collection completed")
            )
            
        except Exception as e:
            logger.error(f"System diagnostics command failed: {e}")
            raise CommandError(f"System diagnostics failed: {e}")

    def _output_json_format(self, diagnostic_info, options):
        """Output diagnostic information in JSON format."""
        json_output = json.dumps(diagnostic_info, indent=2, default=str)
        
        output_file = options.get('output')
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(json_output)
                self.stdout.write(f"Diagnostic report saved to: {output_file}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to save report: {e}")
                )
        else:
            self.stdout.write(json_output)

    def _output_text_format(self, diagnostic_info, options):
        """Output diagnostic information in human-readable text format."""
        output_lines = []
        
        # Header
        output_lines.append("=" * 60)
        output_lines.append("FAKTULOVE SYSTEM DIAGNOSTIC REPORT")
        output_lines.append("=" * 60)
        output_lines.append(f"Generated: {diagnostic_info['timestamp']}")
        output_lines.append("")
        
        # System Information
        output_lines.append("SYSTEM INFORMATION")
        output_lines.append("-" * 30)
        sys_info = diagnostic_info.get('system_info', {})
        for key, value in sys_info.items():
            output_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        output_lines.append("")
        
        # Database Information
        output_lines.append("DATABASE INFORMATION")
        output_lines.append("-" * 30)
        db_info = diagnostic_info.get('database_info', {})
        for key, value in db_info.items():
            output_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        output_lines.append("")
        
        # Application Information
        output_lines.append("APPLICATION INFORMATION")
        output_lines.append("-" * 30)
        app_info = diagnostic_info.get('application_info', {})
        for key, value in app_info.items():
            output_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        output_lines.append("")
        
        # Performance Information
        output_lines.append("PERFORMANCE INFORMATION")
        output_lines.append("-" * 30)
        perf_info = diagnostic_info.get('performance_info', {})
        for key, value in perf_info.items():
            if 'time' in key.lower():
                output_lines.append(f"{key.replace('_', ' ').title()}: {value} ms")
            else:
                output_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        output_lines.append("")
        
        # Errors (if any)
        errors = diagnostic_info.get('errors', [])
        if errors:
            output_lines.append("ERRORS ENCOUNTERED")
            output_lines.append("-" * 30)
            for error in errors:
                output_lines.append(f"❌ {error}")
            output_lines.append("")
        
        # System Health Summary
        output_lines.append("SYSTEM HEALTH SUMMARY")
        output_lines.append("-" * 30)
        
        # Calculate health score
        total_metrics = len(app_info) + len(perf_info)
        error_count = len(errors)
        health_score = max(0, 100 - (error_count * 10))
        
        if health_score >= 90:
            health_status = "Excellent"
            status_style = self.style.SUCCESS
        elif health_score >= 70:
            health_status = "Good"
            status_style = self.style.SUCCESS
        elif health_score >= 50:
            health_status = "Fair"
            status_style = self.style.WARNING
        else:
            health_status = "Poor"
            status_style = self.style.ERROR
        
        output_lines.append(f"Health Score: {health_score}/100 ({health_status})")
        output_lines.append(f"Total Errors: {error_count}")
        output_lines.append("")
        
        # Recommendations
        output_lines.append("RECOMMENDATIONS")
        output_lines.append("-" * 30)
        
        recommendations = self._generate_recommendations(diagnostic_info)
        for recommendation in recommendations:
            output_lines.append(f"💡 {recommendation}")
        
        output_lines.append("")
        output_lines.append("=" * 60)
        
        # Output to file or stdout
        text_output = "\n".join(output_lines)
        
        output_file = options.get('output')
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(text_output)
                self.stdout.write(f"Diagnostic report saved to: {output_file}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to save report: {e}")
                )
        else:
            # Output with appropriate styling
            for line in output_lines:
                if line.startswith("❌"):
                    self.stdout.write(self.style.ERROR(line))
                elif line.startswith("💡"):
                    self.stdout.write(self.style.WARNING(line))
                elif "Health Score" in line:
                    if health_score >= 70:
                        self.stdout.write(self.style.SUCCESS(line))
                    elif health_score >= 50:
                        self.stdout.write(self.style.WARNING(line))
                    else:
                        self.stdout.write(self.style.ERROR(line))
                else:
                    self.stdout.write(line)

    def _generate_recommendations(self, diagnostic_info):
        """Generate recommendations based on diagnostic information."""
        recommendations = []
        
        # Check for errors
        if diagnostic_info.get('errors'):
            recommendations.append("Address the errors listed above to improve system stability")
        
        # Check application metrics
        app_info = diagnostic_info.get('application_info', {})
        
        failed_uploads = app_info.get('failed_uploads', 0)
        if failed_uploads > 10:
            recommendations.append(f"High number of failed uploads ({failed_uploads}). Check OCR service configuration")
        
        total_invoices = app_info.get('total_invoices', 0)
        if total_invoices == 0:
            recommendations.append("No invoices found. Consider creating test data or checking data migration")
        
        # Check performance metrics
        perf_info = diagnostic_info.get('performance_info', {})
        
        avg_response_time = perf_info.get('avg_response_time_1h', 0)
        if avg_response_time and avg_response_time > 1000:  # > 1 second
            recommendations.append("High average response time detected. Consider database optimization")
        
        total_errors = perf_info.get('total_errors_1h', 0)
        if total_errors and total_errors > 50:
            recommendations.append("High error rate detected. Check application logs for issues")
        
        # Check system information
        sys_info = diagnostic_info.get('system_info', {})
        
        if sys_info.get('debug_mode'):
            recommendations.append("Debug mode is enabled. Disable for production environments")
        
        # Default recommendation if no issues found
        if not recommendations:
            recommendations.append("System appears to be running normally. Continue regular monitoring")
        
        return recommendations