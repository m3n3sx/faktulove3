"""
Management command for controlling OCR deployment
"""

import json
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from faktury.services.feature_flag_service import feature_flags
from faktury.services.deployment_monitoring_service import deployment_monitor


class Command(BaseCommand):
    help = 'Manage OCR deployment rollout and monitoring'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=[
                'status', 'advance', 'rollback', 'enable', 'disable',
                'health', 'report', 'maintenance-on', 'maintenance-off'
            ],
            help='Action to perform'
        )
        
        parser.add_argument(
            '--percentage',
            type=int,
            help='Set specific rollout percentage (0-100)'
        )
        
        parser.add_argument(
            '--hours',
            type=int,
            default=1,
            help='Time window in hours for reports (default: 1)'
        )
        
        parser.add_argument(
            '--reason',
            type=str,
            help='Reason for maintenance mode'
        )
        
        parser.add_argument(
            '--output',
            choices=['json', 'text'],
            default='text',
            help='Output format (default: text)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        try:
            if action == 'status':
                self.show_status(options)
            elif action == 'advance':
                self.advance_rollout(options)
            elif action == 'rollback':
                self.rollback_rollout(options)
            elif action == 'enable':
                self.enable_opensource(options)
            elif action == 'disable':
                self.disable_opensource(options)
            elif action == 'health':
                self.show_health(options)
            elif action == 'report':
                self.generate_report(options)
            elif action == 'maintenance-on':
                self.enable_maintenance(options)
            elif action == 'maintenance-off':
                self.disable_maintenance(options)
                
        except Exception as e:
            raise CommandError(f'Command failed: {str(e)}')

    def show_status(self, options):
        """Show current deployment status"""
        stats = feature_flags.get_rollout_statistics()
        
        if options['output'] == 'json':
            self.stdout.write(json.dumps(stats, indent=2))
        else:
            self.stdout.write(self.style.SUCCESS('🚀 OCR Deployment Status'))
            self.stdout.write('=' * 50)
            
            current_stage = stats['current_stage']
            self.stdout.write(f"Current Stage: {current_stage['stage']}")
            self.stdout.write(f"Rollout Percentage: {current_stage['current_percentage']}%")
            self.stdout.write(f"Description: {current_stage['description']}")
            
            self.stdout.write('\n📊 Feature Flags:')
            flags = stats['flags']
            self.stdout.write(f"  • Open-source OCR: {'✅' if flags.get('use_opensource_ocr') else '❌'}")
            self.stdout.write(f"  • Google Cloud disabled: {'✅' if flags.get('disable_google_cloud') else '❌'}")
            self.stdout.write(f"  • Gradual rollout: {'✅' if flags.get('gradual_rollout_enabled') else '❌'}")
            self.stdout.write(f"  • Maintenance mode: {'🚨' if flags.get('maintenance_mode') else '✅'}")
            
            self.stdout.write(f"\n🕒 Last updated: {stats['last_updated']}")

    def advance_rollout(self, options):
        """Advance to next rollout stage"""
        if options.get('percentage') is not None:
            # Set specific percentage
            percentage = options['percentage']
            if not (0 <= percentage <= 100):
                raise CommandError('Percentage must be between 0 and 100')
            
            feature_flags.set_flag('rollout_percentage', percentage)
            feature_flags.set_flag('gradual_rollout_enabled', True)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Rollout percentage set to {percentage}%')
            )
        else:
            # Advance to next stage
            result = feature_flags.advance_rollout_stage()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Advanced rollout from {result["previous_percentage"]}% '
                    f'to {result["new_percentage"]}%'
                )
            )
            self.stdout.write(f'Stage: {result["stage"]}')
            self.stdout.write(f'Description: {result["description"]}')

    def rollback_rollout(self, options):
        """Rollback to previous rollout stage"""
        result = feature_flags.rollback_rollout_stage()
        
        self.stdout.write(
            self.style.WARNING(
                f'⚠️ Rolled back from {result["previous_percentage"]}% '
                f'to {result["new_percentage"]}%'
            )
        )
        self.stdout.write(f'Description: {result["description"]}')

    def enable_opensource(self, options):
        """Enable open-source OCR completely"""
        feature_flags.set_flag('use_opensource_ocr', True)
        feature_flags.set_flag('disable_google_cloud', True)
        feature_flags.set_flag('rollout_percentage', 100)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Open-source OCR enabled for all users')
        )

    def disable_opensource(self, options):
        """Disable open-source OCR completely"""
        feature_flags.set_flag('use_opensource_ocr', False)
        feature_flags.set_flag('disable_google_cloud', False)
        feature_flags.set_flag('gradual_rollout_enabled', False)
        feature_flags.set_flag('rollout_percentage', 0)
        
        self.stdout.write(
            self.style.WARNING('⚠️ Open-source OCR disabled - reverted to Google Cloud')
        )

    def show_health(self, options):
        """Show system health status"""
        health = deployment_monitor.check_health_status()
        
        if options['output'] == 'json':
            self.stdout.write(json.dumps(health, indent=2))
        else:
            status_icon = {
                'healthy': '✅',
                'warning': '⚠️',
                'critical': '🚨'
            }.get(health['overall_status'], '❓')
            
            self.stdout.write(f'{status_icon} Overall Status: {health["overall_status"].upper()}')
            
            if health['alerts']:
                self.stdout.write('\n🚨 Alerts:')
                for alert in health['alerts']:
                    icon = '🚨' if alert['type'] == 'critical' else '⚠️'
                    self.stdout.write(f'  {icon} {alert["message"]}')
            
            self.stdout.write('\n📊 Health Checks:')
            for check_name, check_data in health['checks'].items():
                status_icon = '✅' if check_data['status'] == 'pass' else '❌'
                self.stdout.write(
                    f'  {status_icon} {check_name}: {check_data["value"]:.3f} '
                    f'(threshold: {check_data["threshold"]:.3f})'
                )

    def generate_report(self, options):
        """Generate deployment report"""
        hours = options['hours']
        report = deployment_monitor.generate_deployment_report(hours)
        
        if options['output'] == 'json':
            self.stdout.write(json.dumps(report, indent=2, default=str))
        else:
            self.stdout.write(self.style.SUCCESS('📊 Deployment Report'))
            self.stdout.write('=' * 50)
            
            summary = report['executive_summary']
            self.stdout.write(f"Time Window: {hours} hours")
            self.stdout.write(f"Overall Health: {summary['overall_health']}")
            self.stdout.write(f"Total Processed: {summary['total_processed']}")
            self.stdout.write(f"Success Rate: {summary['success_rate']:.2%}")
            self.stdout.write(f"Avg Processing Time: {summary['avg_processing_time']:.2f}s")
            self.stdout.write(f"Avg Confidence: {summary['avg_confidence']:.2%}")
            
            if report['recommendations']:
                self.stdout.write('\n💡 Recommendations:')
                for i, rec in enumerate(report['recommendations'], 1):
                    self.stdout.write(f'  {i}. {rec}')

    def enable_maintenance(self, options):
        """Enable maintenance mode"""
        reason = options.get('reason', 'Scheduled maintenance')
        feature_flags.enable_maintenance_mode(reason)
        
        self.stdout.write(
            self.style.WARNING(f'🚨 Maintenance mode enabled: {reason}')
        )

    def disable_maintenance(self, options):
        """Disable maintenance mode"""
        feature_flags.disable_maintenance_mode()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Maintenance mode disabled')
        )