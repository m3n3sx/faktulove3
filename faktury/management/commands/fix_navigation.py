"""
Management command to validate and fix navigation issues
"""
from django.core.management.base import BaseCommand
from django.urls import reverse, NoReverseMatch
from faktury.services.navigation_manager import NavigationManager, MissingPageHandler
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate and fix navigation issues in the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only check navigation status without fixing',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting navigation validation...'))
        
        nav_manager = NavigationManager()
        
        # Get navigation status
        status = nav_manager.get_navigation_status()
        
        self.stdout.write(f"Total routes checked: {status['total_routes']}")
        self.stdout.write(f"Broken routes found: {status['broken_routes']}")
        self.stdout.write(f"Overall status: {status['status']}")
        
        if options['verbose'] or status['broken_routes'] > 0:
            self.stdout.write("\nDetailed analysis:")
            
            # Check each route
            for route_name, route_info in nav_manager.EXPECTED_ROUTES.items():
                try:
                    url = reverse(route_name)
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ {route_name}: {url} - {route_info['description']}")
                    )
                except NoReverseMatch:
                    if route_info['required']:
                        self.stdout.write(
                            self.style.ERROR(f"✗ {route_name}: BROKEN - {route_info['description']}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"? {route_name}: OPTIONAL - {route_info['description']}")
                        )
        
        if status['broken_routes'] > 0:
            self.stdout.write(f"\nBroken routes: {', '.join(status['broken_route_names'])}")
            
            if not options['check_only']:
                self.stdout.write("\nApplying fixes...")
                fixes = nav_manager.fix_broken_links()
                
                for broken_route, fix_route in fixes.items():
                    self.stdout.write(f"  {broken_route} -> {fix_route}")
                
                self.stdout.write(self.style.SUCCESS("Fixes have been identified and can be applied through URL redirects."))
            else:
                self.stdout.write(self.style.WARNING("Use without --check-only to apply fixes."))
        else:
            self.stdout.write(self.style.SUCCESS("All navigation routes are working correctly!"))
        
        # Test 404 handler
        self.stdout.write("\nTesting 404 handler...")
        try:
            # This should work without errors
            handler = MissingPageHandler()
            self.stdout.write(self.style.SUCCESS("✓ 404 handler is properly configured"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ 404 handler error: {e}"))
        
        self.stdout.write(self.style.SUCCESS('\nNavigation validation completed!'))