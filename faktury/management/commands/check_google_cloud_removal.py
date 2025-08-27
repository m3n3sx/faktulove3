"""
Django management command to check for remaining Google Cloud references
"""

import os
import re
import ast
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Check for remaining Google Cloud references in the codebase'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix some issues automatically',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about each finding',
        )
    
    def handle(self, *args, **options):
        """Check for Google Cloud references"""
        
        self.stdout.write(
            self.style.HTTP_INFO('🔍 Checking for Google Cloud references...\n')
        )
        
        findings = {
            'settings': [],
            'environment': [],
            'imports': [],
            'code_references': [],
            'configuration': []
        }
        
        # Check Django settings
        self._check_settings(findings)
        
        # Check environment variables
        self._check_environment(findings)
        
        # Check code files
        self._check_code_files(findings, options['verbose'])
        
        # Display results
        self._display_results(findings, options)
        
        # Determine if any issues were found
        total_issues = sum(len(issues) for issues in findings.values())
        
        if total_issues == 0:
            self.stdout.write(
                self.style.SUCCESS('\n✅ No Google Cloud references found!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  Found {total_issues} Google Cloud references')
            )
    
    def _check_settings(self, findings):
        """Check Django settings for Google Cloud references"""
        deprecated_settings = [
            'GOOGLE_CLOUD_PROJECT',
            'GOOGLE_APPLICATION_CREDENTIALS',
            'DOCUMENT_AI_CONFIG'
        ]
        
        for setting_name in deprecated_settings:
            if hasattr(settings, setting_name):
                value = getattr(settings, setting_name)
                if value:
                    findings['settings'].append({
                        'setting': setting_name,
                        'value': str(value)[:100] + '...' if len(str(value)) > 100 else str(value),
                        'location': 'Django settings'
                    })
    
    def _check_environment(self, findings):
        """Check environment variables for Google Cloud references"""
        deprecated_env_vars = [
            'GOOGLE_CLOUD_PROJECT',
            'GOOGLE_APPLICATION_CREDENTIALS',
            'DOCUMENT_AI_PROCESSOR_ID'
        ]
        
        for env_var in deprecated_env_vars:
            value = os.getenv(env_var)
            if value:
                findings['environment'].append({
                    'variable': env_var,
                    'value': value[:50] + '...' if len(value) > 50 else value,
                    'source': 'Environment variable'
                })
    
    def _check_code_files(self, findings, verbose):
        """Check code files for Google Cloud references"""
        # Define patterns to search for
        patterns = {
            'imports': [
                r'from\s+google\.cloud\s+import',
                r'import\s+google\.cloud',
                r'from\s+.*document_ai_service.*import.*DocumentAIService',
                r'import.*documentai'
            ],
            'code_references': [
                r'DocumentAIService\(',
                r'google\.cloud',
                r'documentai\.',
                r'GOOGLE_APPLICATION_CREDENTIALS',
                r'GOOGLE_CLOUD_PROJECT',
                r'DOCUMENT_AI_CONFIG'
            ]
        }
        
        # Get project root
        project_root = Path(settings.BASE_DIR)
        
        # Files to check
        python_files = list(project_root.rglob('*.py'))
        config_files = list(project_root.rglob('*.env*')) + list(project_root.rglob('*.sh'))
        
        all_files = python_files + config_files
        
        for file_path in all_files:
            # Skip certain directories
            skip_dirs = ['.git', '__pycache__', '.venv', 'venv', 'node_modules', 'staticfiles']
            if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for patterns
                for category, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            line_content = content.split('\n')[line_num - 1].strip()
                            
                            # Skip comments and documentation
                            if line_content.startswith('#') or '"""' in line_content or "'''" in line_content:
                                continue
                            
                            findings[category].append({
                                'file': str(file_path.relative_to(project_root)),
                                'line': line_num,
                                'content': line_content,
                                'pattern': pattern,
                                'match': match.group()
                            })
                            
                            if verbose:
                                self.stdout.write(f"  Found in {file_path.name}:{line_num}: {line_content}")
            
            except (UnicodeDecodeError, PermissionError):
                # Skip files that can't be read
                continue
    
    def _display_results(self, findings, options):
        """Display the findings"""
        
        # Settings issues
        if findings['settings']:
            self.stdout.write(self.style.ERROR('❌ DJANGO SETTINGS ISSUES:'))
            for issue in findings['settings']:
                self.stdout.write(f"   • {issue['setting']}: {issue['value']}")
            self.stdout.write('')
        
        # Environment issues
        if findings['environment']:
            self.stdout.write(self.style.ERROR('❌ ENVIRONMENT VARIABLE ISSUES:'))
            for issue in findings['environment']:
                self.stdout.write(f"   • {issue['variable']}: {issue['value']}")
            self.stdout.write('')
        
        # Import issues
        if findings['imports']:
            self.stdout.write(self.style.WARNING('⚠️  IMPORT ISSUES:'))
            for issue in findings['imports']:
                self.stdout.write(f"   • {issue['file']}:{issue['line']} - {issue['match']}")
                if options['verbose']:
                    self.stdout.write(f"     {issue['content']}")
            self.stdout.write('')
        
        # Code reference issues
        if findings['code_references']:
            self.stdout.write(self.style.WARNING('⚠️  CODE REFERENCE ISSUES:'))
            for issue in findings['code_references']:
                self.stdout.write(f"   • {issue['file']}:{issue['line']} - {issue['match']}")
                if options['verbose']:
                    self.stdout.write(f"     {issue['content']}")
            self.stdout.write('')
        
        # Recommendations
        self._display_recommendations(findings)
    
    def _display_recommendations(self, findings):
        """Display recommendations for fixing issues"""
        self.stdout.write(self.style.HTTP_INFO('💡 RECOMMENDATIONS:'))
        
        if findings['settings']:
            self.stdout.write('   • Remove deprecated Google Cloud settings from Django configuration')
        
        if findings['environment']:
            self.stdout.write('   • Remove deprecated Google Cloud environment variables from .env files')
        
        if findings['imports']:
            self.stdout.write('   • Replace Google Cloud imports with open source alternatives')
            self.stdout.write('   • Use ocr_service_factory.get_ocr_service() instead of DocumentAIService')
        
        if findings['code_references']:
            self.stdout.write('   • Update code to use OpenSourceOCRService instead of DocumentAIService')
            self.stdout.write('   • Remove references to Google Cloud configuration variables')
        
        self.stdout.write('   • Run "python manage.py validate_ocr_config" to verify OCR configuration')
        self.stdout.write('   • Set USE_OPENSOURCE_OCR=True and DISABLE_GOOGLE_CLOUD=True in environment')
        self.stdout.write('')