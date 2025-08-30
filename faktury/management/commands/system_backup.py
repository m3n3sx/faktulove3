"""
Management command for system backup and restore operations.

Provides backup creation, restoration, and backup management functionality.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from faktury.services.maintenance_service import MaintenanceService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage system backups (create, restore, list)'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Backup actions')
        
        # Create backup
        create_parser = subparsers.add_parser('create', help='Create a new backup')
        create_parser.add_argument(
            '--name',
            type=str,
            help='Custom backup name (default: auto-generated)'
        )
        create_parser.add_argument(
            '--components',
            nargs='+',
            choices=['database', 'media', 'config', 'all'],
            default=['all'],
            help='Components to backup (default: all)'
        )
        
        # Restore backup
        restore_parser = subparsers.add_parser('restore', help='Restore from backup')
        restore_parser.add_argument(
            'backup_name',
            type=str,
            help='Name of backup to restore'
        )
        restore_parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm restoration (required for safety)'
        )
        
        # List backups
        list_parser = subparsers.add_parser('list', help='List available backups')
        list_parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed backup information'
        )
        
        # Delete backup
        delete_parser = subparsers.add_parser('delete', help='Delete a backup')
        delete_parser.add_argument(
            'backup_name',
            type=str,
            help='Name of backup to delete'
        )
        delete_parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion (required for safety)'
        )

    def handle(self, *args, **options):
        """Execute backup operations."""
        try:
            maintenance_service = MaintenanceService()
            
            action = options.get('action')
            
            if action == 'create':
                self._create_backup(maintenance_service, options)
            elif action == 'restore':
                self._restore_backup(maintenance_service, options)
            elif action == 'list':
                self._list_backups(maintenance_service, options)
            elif action == 'delete':
                self._delete_backup(maintenance_service, options)
            else:
                self.stdout.write(
                    self.style.ERROR(
                        "Please specify an action: create, restore, list, or delete"
                    )
                )
                return
            
        except Exception as e:
            logger.error(f"Backup command failed: {e}")
            raise CommandError(f"Backup operation failed: {e}")

    def _create_backup(self, maintenance_service, options):
        """Create a new backup."""
        self.stdout.write("Creating system backup...")
        
        backup_name = options.get('name')
        components = options.get('components', ['all'])
        
        if backup_name:
            self.stdout.write(f"Backup name: {backup_name}")
        
        self.stdout.write(f"Components: {', '.join(components)}")
        
        try:
            backup_results = maintenance_service.create_backup(backup_name)
            
            if backup_results['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Backup created successfully: {backup_results['backup_name']}"
                    )
                )
                
                self.stdout.write(f"Backup path: {backup_results['backup_path']}")
                self.stdout.write(f"Backup size: {self._format_size(backup_results['backup_size'])}")
                self.stdout.write(f"Components: {', '.join(backup_results['components'])}")
                
            else:
                self.stdout.write(
                    self.style.ERROR("Backup creation failed")
                )
                for error in backup_results['errors']:
                    self.stdout.write(self.style.ERROR(f"  Error: {error}"))
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Backup creation failed: {e}")
            )

    def _restore_backup(self, maintenance_service, options):
        """Restore from backup."""
        backup_name = options['backup_name']
        
        if not options.get('confirm'):
            self.stdout.write(
                self.style.ERROR(
                    "Restoration requires confirmation. Use --confirm flag."
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: Restoration will overwrite current data!"
                )
            )
            return
        
        self.stdout.write(f"Restoring from backup: {backup_name}")
        self.stdout.write(
            self.style.WARNING(
                "This will overwrite current system data. Proceeding..."
            )
        )
        
        try:
            restore_results = maintenance_service.restore_backup(backup_name)
            
            if restore_results['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Backup restored successfully: {backup_name}"
                    )
                )
                
                self.stdout.write(f"Restored components: {', '.join(restore_results['restored_components'])}")
                
            else:
                self.stdout.write(
                    self.style.ERROR("Backup restoration failed")
                )
                for error in restore_results['errors']:
                    self.stdout.write(self.style.ERROR(f"  Error: {error}"))
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Backup restoration failed: {e}")
            )

    def _list_backups(self, maintenance_service, options):
        """List available backups."""
        self.stdout.write("Available backups:")
        
        try:
            backups = maintenance_service.list_backups()
            
            if not backups:
                self.stdout.write("No backups found.")
                return
            
            for backup in backups:
                self.stdout.write(f"\n📦 {backup['name']}")
                self.stdout.write(f"   Created: {backup['created_at']}")
                self.stdout.write(f"   Size: {self._format_size(backup['size'])}")
                
                if options.get('detailed'):
                    if backup.get('components'):
                        self.stdout.write(f"   Components: {', '.join(backup['components'])}")
                    self.stdout.write(f"   Path: {backup['path']}")
                    
                    if backup.get('django_version'):
                        self.stdout.write(f"   Django Version: {backup['django_version']}")
                    if backup.get('database_engine'):
                        self.stdout.write(f"   Database: {backup['database_engine']}")
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to list backups: {e}")
            )

    def _delete_backup(self, maintenance_service, options):
        """Delete a backup."""
        backup_name = options['backup_name']
        
        if not options.get('confirm'):
            self.stdout.write(
                self.style.ERROR(
                    "Deletion requires confirmation. Use --confirm flag."
                )
            )
            return
        
        self.stdout.write(f"Deleting backup: {backup_name}")
        
        try:
            import os
            import shutil
            
            backup_path = os.path.join(maintenance_service.backup_directory, backup_name)
            
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
                self.stdout.write(
                    self.style.SUCCESS(f"Backup deleted successfully: {backup_name}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Backup not found: {backup_name}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to delete backup: {e}")
            )

    def _format_size(self, size_bytes):
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"