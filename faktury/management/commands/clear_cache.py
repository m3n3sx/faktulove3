"""
Management command to clear application cache
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Clear application cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pattern',
            type=str,
            help='Cache key pattern to clear (optional)',
        )

    def handle(self, *args, **options):
        pattern = options.get('pattern')
        
        if pattern:
            self.stdout.write(f'Clearing cache with pattern: {pattern}')
            try:
                cache.delete_pattern(pattern)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully cleared cache pattern: {pattern}')
                )
            except AttributeError:
                self.stdout.write(
                    self.style.WARNING('Cache backend does not support pattern deletion')
                )
        else:
            self.stdout.write('Clearing entire cache...')
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared entire cache')
            )
