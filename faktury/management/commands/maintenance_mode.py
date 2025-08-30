"""
Management command for maintenance mode operations.

Provides functionality to enable/disable maintenance mode and check status.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from faktury.services.maintenance_service import MaintenanceService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage system maintenance mode'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Maintenance mode actions')
        
        # Enable maintenance mode
        enable_parser = subparsers.add_parser('enable', help='Enable maintenance mode')
        enable_parser.add_argument(
            '--message',
            type=str,
            default='System maintenance in progress. Please try again later.',
            help='Custom maintenance message for users'
        )
        
        # Disable maintenance mode
        disable_parser = subparsers.add_parser('disable', help='Disable maintenance mode')
        
        # Check maintenance mode status
        status_parser = subparsers.add_parser('status', help='Check maintenance mode status')

    def handle(self, *args, **options):
        """Execute maintenance mode operations."""
        try:
            maintenance_service = MaintenanceService()
            
            action = options.get('action')
            
            if action == 'enable':
                self._enable_maintenance_mode(maintenance_service, options)
            elif action == 'disable':
                self._disable_maintenance_mode(maintenance_service, options)
            elif action == 'status':
                self._check_maintenance_status(maintenance_service, options)
            else:
                self.stdout.write(
                    self.style.ERROR(
                        "Please specify an action: enable, disable, or status"
                    )
                )
                return
            
        except Exception as e:
            logger.error(f"Maintenance mode command failed: {e}")
            raise CommandError(f"Maintenance mode operation failed: {e}")

    def _enable_maintenance_mode(self, maintenance_service, options):
        """Enable maintenance mode."""
        message = options.get('message')
        
        self.stdout.write("Enabling maintenance mode...")
        self.stdout.write(f"Message: {message}")
        
        try:
            success = maintenance_service.enable_maintenance_mode(message)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS("Maintenance mode enabled successfully")
                )
                self.stdout.write(
                    self.style.WARNING(
                        "Users will now see the maintenance page when accessing the system"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR("Failed to enable maintenance mode")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to enable maintenance mode: {e}")
            )

    def _disable_maintenance_mode(self, maintenance_service, options):
        """Disable maintenance mode."""
        self.stdout.write("Disabling maintenance mode...")
        
        try:
            success = maintenance_service.disable_maintenance_mode()
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS("Maintenance mode disabled successfully")
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        "System is now accessible to users"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR("Failed to disable maintenance mode")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to disable maintenance mode: {e}")
            )

    def _check_maintenance_status(self, maintenance_service, options):
        """Check maintenance mode status."""
        try:
            status = maintenance_service.is_maintenance_mode_enabled()
            
            if status['enabled']:
                self.stdout.write(
                    self.style.WARNING("🔧 Maintenance mode is ENABLED")
                )
                self.stdout.write(f"Message: {status.get('message', 'N/A')}")
                self.stdout.write(f"Enabled at: {status.get('enabled_at', 'N/A')}")
                self.stdout.write(f"Enabled by: {status.get('enabled_by', 'N/A')}")
            else:
                self.stdout.write(
                    self.style.SUCCESS("✅ Maintenance mode is DISABLED")
                )
                self.stdout.write("System is accessible to users")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to check maintenance status: {e}")
            )