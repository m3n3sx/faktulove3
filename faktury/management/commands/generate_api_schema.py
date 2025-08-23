"""
Management command to generate OpenAPI schema file for the API.
"""
import json
import yaml
from django.core.management.base import BaseCommand
from django.conf import settings
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema
from drf_spectacular.generators import SchemaGenerator


class Command(BaseCommand):
    help = 'Generate OpenAPI schema file for the FaktuLove OCR API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'yaml'],
            default='json',
            help='Output format for the schema file (default: json)'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='api_schema',
            help='Output filename (without extension)'
        )
        parser.add_argument(
            '--indent',
            type=int,
            default=2,
            help='Indentation for JSON output (default: 2)'
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='Generate schema for public endpoints only'
        )
    
    def handle(self, *args, **options):
        """Generate and save the OpenAPI schema."""
        try:
            self.stdout.write(
                self.style.SUCCESS('Generating OpenAPI schema for FaktuLove OCR API...')
            )
            
            # Create schema generator
            generator = SchemaGenerator(
                title=getattr(settings, 'SPECTACULAR_SETTINGS', {}).get('TITLE', 'FaktuLove OCR API'),
                description=getattr(settings, 'SPECTACULAR_SETTINGS', {}).get('DESCRIPTION', ''),
                version=getattr(settings, 'SPECTACULAR_SETTINGS', {}).get('VERSION', '1.0.0'),
                patterns=None,  # Use all URL patterns
            )
            
            # Generate the schema
            schema = generator.get_schema(request=None, public=options['public'])
            
            # Determine output format and filename
            output_format = options['format']
            filename = f"{options['output']}.{output_format}"
            
            # Write schema to file
            with open(filename, 'w', encoding='utf-8') as f:
                if output_format == 'json':
                    json.dump(
                        schema,
                        f,
                        indent=options['indent'],
                        ensure_ascii=False,
                        sort_keys=True
                    )
                else:  # yaml
                    yaml.dump(
                        schema,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=True,
                        indent=options['indent']
                    )
            
            # Display summary
            self.stdout.write(
                self.style.SUCCESS(f'✓ Schema generated successfully: {filename}')
            )
            
            # Count endpoints
            endpoint_count = 0
            if 'paths' in schema:
                for path, methods in schema['paths'].items():
                    endpoint_count += len([m for m in methods.keys() if m.upper() in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']])
            
            self.stdout.write(f'  • Total endpoints: {endpoint_count}')
            self.stdout.write(f'  • Format: {output_format.upper()}')
            self.stdout.write(f'  • File size: {self._get_file_size(filename)}')
            
            # Display available documentation URLs
            self.stdout.write('\n' + self.style.WARNING('Available documentation URLs:'))
            base_url = 'http://localhost:8000' if settings.DEBUG else 'https://faktulove.pl'
            self.stdout.write(f'  • Swagger UI: {base_url}/api/docs/')
            self.stdout.write(f'  • ReDoc: {base_url}/api/redoc/')
            self.stdout.write(f'  • OpenAPI Schema: {base_url}/api/schema/')
            
            # Display usage tips
            self.stdout.write('\n' + self.style.WARNING('Usage tips:'))
            self.stdout.write('  • Use the generated schema file for client SDK generation')
            self.stdout.write('  • Import the schema into Postman or Insomnia for API testing')
            self.stdout.write('  • Share the schema file with frontend developers')
            self.stdout.write('  • Use --public flag to generate schema without authentication requirements')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating schema: {str(e)}')
            )
            raise
    
    def _get_file_size(self, filename):
        """Get human-readable file size."""
        try:
            import os
            size = os.path.getsize(filename)
            
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            
            return f"{size:.1f} TB"
        except:
            return "Unknown"