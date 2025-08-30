"""
Management command for database maintenance operations.

Provides database cleanup, optimization, and maintenance functionality.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from faktury.services.maintenance_service import MaintenanceService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Perform database maintenance operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old data from database'
        )
        
        parser.add_argument(
            '--optimize',
            action='store_true',
            help='Optimize database performance'
        )
        
        parser.add_argument(
            '--days-to-keep',
            type=int,
            default=90,
            help='Number of days of data to keep during cleanup (default: 90)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without actually doing it'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about operations'
        )

    def handle(self, *args, **options):
        """Execute database maintenance operations."""
        try:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Starting database maintenance at {timezone.now()}"
                )
            )
            
            maintenance_service = MaintenanceService()
            
            if options['cleanup']:
                self._perform_cleanup(maintenance_service, options)
            
            if options['optimize']:
                self._perform_optimization(maintenance_service, options)
            
            if not options['cleanup'] and not options['optimize']:
                self.stdout.write(
                    self.style.WARNING(
                        "No operation specified. Use --cleanup or --optimize"
                    )
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS("Database maintenance completed successfully")
            )
            
        except Exception as e:
            logger.error(f"Database maintenance command failed: {e}")
            raise CommandError(f"Database maintenance failed: {e}")

    def _perform_cleanup(self, maintenance_service, options):
        """Perform database cleanup operations."""
        self.stdout.write("Performing database cleanup...")
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No data will be deleted")
            )
            # In a real implementation, you would add dry-run logic here
            return
        
        days_to_keep = options['days_to_keep']
        self.stdout.write(f"Keeping data from last {days_to_keep} days")
        
        try:
            cleanup_results = maintenance_service.cleanup_old_data(days_to_keep)
            
            if cleanup_results['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS("Database cleanup completed successfully")
                )
                
                if options['verbose']:
                    self._display_cleanup_results(cleanup_results)
            else:
                self.stdout.write(
                    self.style.ERROR("Database cleanup failed")
                )
                for error in cleanup_results['errors']:
                    self.stdout.write(self.style.ERROR(f"  Error: {error}"))
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Database cleanup failed: {e}")
            )

    def _perform_optimization(self, maintenance_service, options):
        """Perform database optimization operations."""
        self.stdout.write("Performing database optimization...")
        
        try:
            optimization_results = maintenance_service.optimize_database()
            
            if optimization_results['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS("Database optimization completed successfully")
                )
                
                if options['verbose']:
                    self._display_optimization_results(optimization_results)
            else:
                self.stdout.write(
                    self.style.ERROR("Database optimization failed")
                )
                for error in optimization_results['errors']:
                    self.stdout.write(self.style.ERROR(f"  Error: {error}"))
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Database optimization failed: {e}")
            )

    def _display_cleanup_results(self, results):
        """Display detailed cleanup results."""
        self.stdout.write("\nCleanup Results:")
        
        for item_type, count in results['cleaned_items'].items():
            self.stdout.write(f"  {item_type.replace('_', ' ').title()}: {count} items")
        
        total_items = sum(results['cleaned_items'].values())
        self.stdout.write(f"\nTotal items cleaned: {total_items}")

    def _display_optimization_results(self, results):
        """Display detailed optimization results."""
        self.stdout.write("\nOptimization Operations:")
        
        for operation in results['operations']:
            self.stdout.write(f"  ✓ {operation}")
        
        if results['performance_improvement']:
            self.stdout.write("\nPerformance Improvements:")
            for metric, improvement in results['performance_improvement'].items():
                self.stdout.write(f"  {metric}: {improvement}")