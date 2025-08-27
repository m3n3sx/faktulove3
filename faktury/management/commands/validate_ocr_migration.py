"""
Django management command for validating OCR data migration integrity.

This command provides comprehensive validation of the OCR data migration process:
1. Pre-migration validation
2. Post-migration validation
3. Data integrity checks
4. Performance impact analysis

Usage:
    python manage.py validate_ocr_migration --pre-migration   # Before migration
    python manage.py validate_ocr_migration --post-migration  # After migration
    python manage.py validate_ocr_migration --full-check      # Complete validation
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import Q, Count, Avg, Min, Max, Sum
from django.utils import timezone

from faktury.models import (
    OCRResult, OCREngine, OCRProcessingStep, DocumentUpload, 
    Faktura, OCRValidation, OCRProcessingLog
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate OCR data migration integrity and performance'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validation_results = {
            'timestamp': None,
            'validation_type': None,
            'checks_passed': 0,
            'checks_failed': 0,
            'warnings': 0,
            'errors': [],
            'warnings_list': [],
            'statistics': {},
            'recommendations': [],
        }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pre-migration',
            action='store_true',
            help='Run pre-migration validation checks',
        )
        parser.add_argument(
            '--post-migration',
            action='store_true',
            help='Run post-migration validation checks',
        )
        parser.add_argument(
            '--full-check',
            action='store_true',
            help='Run comprehensive validation (includes performance analysis)',
        )
        parser.add_argument(
            '--output-file',
            type=str,
            help='Save validation results to JSON file',
        )
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Attempt to automatically fix detected issues',
        )
        parser.add_argument(
            '--sample-size',
            type=int,
            default=1000,
            help='Sample size for performance testing (default: 1000)',
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.verbosity = options['verbosity']
        self.output_file = options.get('output_file')
        self.fix_issues = options['fix_issues']
        self.sample_size = options['sample_size']
        
        self.validation_results['timestamp'] = timezone.now().isoformat()
        
        try:
            if options['pre_migration']:
                self.validation_results['validation_type'] = 'pre_migration'
                self.run_pre_migration_validation()
            elif options['post_migration']:
                self.validation_results['validation_type'] = 'post_migration'
                self.run_post_migration_validation()
            elif options['full_check']:
                self.validation_results['validation_type'] = 'full_check'
                self.run_full_validation()
            else:
                self.stdout.write(
                    self.style.ERROR(
                        'Please specify --pre-migration, --post-migration, or --full-check'
                    )
                )
                return
            
            self.generate_validation_report()
            
        except Exception as e:
            logger.error(f"Validation command failed: {e}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f'Validation failed: {e}')
            )
            raise CommandError(f'Validation failed: {e}')
    
    def run_pre_migration_validation(self):
        """Run validation checks before migration"""
        self.stdout.write(
            self.style.SUCCESS('Running pre-migration validation...')
        )
        
        # Basic data integrity checks
        self.check_database_integrity()
        self.check_ocr_data_completeness()
        self.check_google_cloud_dependencies()
        self.analyze_current_performance()
        
        # Migration readiness checks
        self.check_migration_prerequisites()
        self.estimate_migration_impact()
    
    def run_post_migration_validation(self):
        """Run validation checks after migration"""
        self.stdout.write(
            self.style.SUCCESS('Running post-migration validation...')
        )
        
        # Data integrity after migration
        self.check_database_integrity()
        self.check_migration_completeness()
        self.validate_engine_assignments()
        self.validate_confidence_scores()
        self.check_processing_steps()
        
        # Performance validation
        self.analyze_post_migration_performance()
        self.validate_api_compatibility()
    
    def run_full_validation(self):
        """Run comprehensive validation"""
        self.stdout.write(
            self.style.SUCCESS('Running full validation...')
        )
        
        # All validation checks
        self.check_database_integrity()
        self.check_ocr_data_completeness()
        self.check_migration_completeness()
        self.validate_engine_assignments()
        self.validate_confidence_scores()
        self.check_processing_steps()
        
        # Performance analysis
        self.analyze_current_performance()
        self.analyze_post_migration_performance()
        self.validate_api_compatibility()
        
        # Advanced checks
        self.check_data_consistency()
        self.analyze_confidence_distribution()
        self.check_processing_pipeline_integrity()
    
    def check_database_integrity(self):
        """Check basic database integrity"""
        self.stdout.write('Checking database integrity...')
        
        checks = [
            ('OCR Results exist', lambda: OCRResult.objects.exists()),
            ('Document Uploads exist', lambda: DocumentUpload.objects.exists()),
            ('No orphaned OCR Results', lambda: not OCRResult.objects.filter(document__isnull=True).exists()),
            ('No orphaned Processing Steps', lambda: not OCRProcessingStep.objects.filter(ocr_result__isnull=True).exists()),
            ('Valid foreign key relationships', self.check_foreign_key_integrity),
        ]
        
        for check_name, check_func in checks:
            try:
                if check_func():
                    self.pass_check(check_name)
                else:
                    self.fail_check(check_name, 'Check returned False')
            except Exception as e:
                self.fail_check(check_name, str(e))
    
    def check_foreign_key_integrity(self) -> bool:
        """Check foreign key integrity"""
        with connection.cursor() as cursor:
            # Check OCRResult -> DocumentUpload
            cursor.execute("""
                SELECT COUNT(*) FROM faktury_ocrresult ocr
                LEFT JOIN faktury_documentupload doc ON ocr.document_id = doc.id
                WHERE doc.id IS NULL
            """)
            orphaned_ocr = cursor.fetchone()[0]
            
            if orphaned_ocr > 0:
                self.add_error(f'Found {orphaned_ocr} OCR results with invalid document references')
                return False
            
            # Check OCRProcessingStep -> OCRResult
            cursor.execute("""
                SELECT COUNT(*) FROM faktury_ocrprocessingstep step
                LEFT JOIN faktury_ocrresult ocr ON step.ocr_result_id = ocr.id
                WHERE ocr.id IS NULL
            """)
            orphaned_steps = cursor.fetchone()[0]
            
            if orphaned_steps > 0:
                self.add_error(f'Found {orphaned_steps} processing steps with invalid OCR result references')
                return False
        
        return True
    
    def check_ocr_data_completeness(self):
        """Check OCR data completeness"""
        self.stdout.write('Checking OCR data completeness...')
        
        total_results = OCRResult.objects.count()
        self.validation_results['statistics']['total_ocr_results'] = total_results
        
        if total_results == 0:
            self.fail_check('OCR Results exist', 'No OCR results found in database')
            return
        
        # Check for missing extracted data
        missing_data = OCRResult.objects.filter(
            Q(extracted_data__isnull=True) | Q(extracted_data={})
        ).count()
        
        if missing_data > 0:
            percentage = (missing_data / total_results) * 100
            if percentage > 10:
                self.fail_check(
                    'Extracted data completeness',
                    f'{missing_data} ({percentage:.1f}%) OCR results missing extracted data'
                )
            else:
                self.add_warning(
                    f'{missing_data} ({percentage:.1f}%) OCR results missing extracted data'
                )
        else:
            self.pass_check('Extracted data completeness')
        
        # Check for missing confidence scores
        invalid_confidence = OCRResult.objects.filter(
            Q(confidence_score__isnull=True) |
            Q(confidence_score__lt=0) |
            Q(confidence_score__gt=100)
        ).count()
        
        if invalid_confidence > 0:
            self.fail_check(
                'Confidence score validity',
                f'{invalid_confidence} OCR results have invalid confidence scores'
            )
        else:
            self.pass_check('Confidence score validity')
        
        # Check for missing raw text
        missing_text = OCRResult.objects.filter(
            Q(raw_text__isnull=True) | Q(raw_text='')
        ).count()
        
        if missing_text > 0:
            percentage = (missing_text / total_results) * 100
            if percentage > 5:
                self.add_warning(
                    f'{missing_text} ({percentage:.1f}%) OCR results missing raw text'
                )
        
        self.validation_results['statistics']['missing_data_count'] = missing_data
        self.validation_results['statistics']['invalid_confidence_count'] = invalid_confidence
        self.validation_results['statistics']['missing_text_count'] = missing_text
    
    def check_google_cloud_dependencies(self):
        """Check for Google Cloud dependencies"""
        self.stdout.write('Checking Google Cloud dependencies...')
        
        # Check processor versions
        google_cloud_results = OCRResult.objects.filter(
            Q(processor_version__icontains='google') |
            Q(processor_version__icontains='document-ai') |
            Q(processor_version__isnull=True) |
            Q(processor_version='')
        ).count()
        
        total_results = OCRResult.objects.count()
        
        if google_cloud_results > 0:
            percentage = (google_cloud_results / total_results) * 100 if total_results > 0 else 0
            self.validation_results['statistics']['google_cloud_results'] = google_cloud_results
            self.validation_results['statistics']['google_cloud_percentage'] = percentage
            
            if percentage > 50:
                self.add_warning(
                    f'{google_cloud_results} ({percentage:.1f}%) OCR results use Google Cloud processors'
                )
            
            self.pass_check('Google Cloud dependency detection')
        else:
            self.pass_check('No Google Cloud dependencies found')
    
    def check_migration_prerequisites(self):
        """Check migration prerequisites"""
        self.stdout.write('Checking migration prerequisites...')
        
        # Check if OCREngine model exists and has data
        try:
            engine_count = OCREngine.objects.count()
            if engine_count == 0:
                self.add_warning('No OCR engines configured - migration will create them')
            else:
                self.pass_check(f'OCR engines configured ({engine_count} engines)')
        except Exception as e:
            self.add_warning(f'OCREngine model not available: {e}')
        
        # Check available disk space (simplified check)
        import shutil
        try:
            total, used, free = shutil.disk_usage('/')
            free_gb = free // (1024**3)
            if free_gb < 1:
                self.fail_check('Disk space', f'Only {free_gb}GB free space available')
            else:
                self.pass_check(f'Sufficient disk space ({free_gb}GB available)')
        except Exception as e:
            self.add_warning(f'Could not check disk space: {e}')
    
    def check_migration_completeness(self):
        """Check if migration was completed successfully"""
        self.stdout.write('Checking migration completeness...')
        
        total_results = OCRResult.objects.count()
        
        # Check for unmigrated processor versions
        unmigrated = OCRResult.objects.filter(
            Q(processor_version__icontains='google') |
            Q(processor_version__icontains='document-ai') |
            (Q(processor_version__isnull=True) & ~Q(primary_engine__isnull=False))
        ).count()
        
        if unmigrated > 0:
            percentage = (unmigrated / total_results) * 100 if total_results > 0 else 0
            self.fail_check(
                'Migration completeness',
                f'{unmigrated} ({percentage:.1f}%) OCR results not migrated'
            )
        else:
            self.pass_check('All OCR results migrated')
        
        # Check for missing engine assignments
        missing_engines = OCRResult.objects.filter(primary_engine__isnull=True).count()
        
        if missing_engines > 0:
            percentage = (missing_engines / total_results) * 100 if total_results > 0 else 0
            self.fail_check(
                'Engine assignment completeness',
                f'{missing_engines} ({percentage:.1f}%) OCR results missing engine assignment'
            )
        else:
            self.pass_check('All OCR results have engine assignments')
        
        self.validation_results['statistics']['unmigrated_count'] = unmigrated
        self.validation_results['statistics']['missing_engines_count'] = missing_engines
    
    def validate_engine_assignments(self):
        """Validate OCR engine assignments"""
        self.stdout.write('Validating engine assignments...')
        
        # Check engine distribution
        engine_stats = OCRResult.objects.values(
            'primary_engine__name', 'primary_engine__engine_type'
        ).annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence_score')
        ).order_by('-count')
        
        if not engine_stats:
            self.fail_check('Engine assignments', 'No engine assignments found')
            return
        
        self.validation_results['statistics']['engine_distribution'] = list(engine_stats)
        
        # Check for reasonable distribution
        total_results = sum(stat['count'] for stat in engine_stats)
        
        for stat in engine_stats:
            percentage = (stat['count'] / total_results) * 100
            engine_name = stat['primary_engine__name'] or 'Unknown'
            
            if percentage > 90:
                self.add_warning(
                    f'Engine "{engine_name}" handles {percentage:.1f}% of all results'
                )
        
        self.pass_check('Engine assignment validation')
    
    def validate_confidence_scores(self):
        """Validate confidence score distribution and validity"""
        self.stdout.write('Validating confidence scores...')
        
        # Get confidence statistics
        confidence_stats = OCRResult.objects.aggregate(
            min_confidence=Min('confidence_score'),
            max_confidence=Max('confidence_score'),
            avg_confidence=Avg('confidence_score'),
            count=Count('id')
        )
        
        self.validation_results['statistics']['confidence_stats'] = confidence_stats
        
        # Check for valid range
        if confidence_stats['min_confidence'] < 0:
            self.fail_check(
                'Confidence score range',
                f'Minimum confidence score is {confidence_stats["min_confidence"]}'
            )
        elif confidence_stats['max_confidence'] > 100:
            self.fail_check(
                'Confidence score range',
                f'Maximum confidence score is {confidence_stats["max_confidence"]}'
            )
        else:
            self.pass_check('Confidence scores within valid range (0-100)')
        
        # Check for reasonable distribution
        avg_confidence = confidence_stats['avg_confidence']
        if avg_confidence and avg_confidence < 50:
            self.add_warning(
                f'Average confidence score is low: {avg_confidence:.1f}%'
            )
        elif avg_confidence and avg_confidence > 95:
            self.add_warning(
                f'Average confidence score is suspiciously high: {avg_confidence:.1f}%'
            )
        else:
            self.pass_check(f'Reasonable average confidence: {avg_confidence:.1f}%')
    
    def check_processing_steps(self):
        """Check processing steps integrity"""
        self.stdout.write('Checking processing steps...')
        
        try:
            total_steps = OCRProcessingStep.objects.count()
            results_with_steps = OCRResult.objects.filter(
                processing_steps__isnull=False
            ).distinct().count()
            
            total_results = OCRResult.objects.count()
            
            if results_with_steps == 0:
                self.add_warning('No OCR results have processing steps')
            else:
                percentage = (results_with_steps / total_results) * 100 if total_results > 0 else 0
                if percentage < 50:
                    self.add_warning(
                        f'Only {percentage:.1f}% of OCR results have processing steps'
                    )
                else:
                    self.pass_check(f'{percentage:.1f}% of OCR results have processing steps')
            
            self.validation_results['statistics']['total_processing_steps'] = total_steps
            self.validation_results['statistics']['results_with_steps'] = results_with_steps
            
        except Exception as e:
            self.add_warning(f'Could not check processing steps: {e}')
    
    def analyze_current_performance(self):
        """Analyze current system performance"""
        self.stdout.write('Analyzing current performance...')
        
        # Get processing time statistics
        processing_stats = OCRResult.objects.aggregate(
            min_time=Min('processing_time'),
            max_time=Max('processing_time'),
            avg_time=Avg('processing_time'),
            count=Count('id')
        )
        
        self.validation_results['statistics']['processing_time_stats'] = processing_stats
        
        # Check for reasonable processing times
        avg_time = processing_stats['avg_time']
        if avg_time and avg_time > 60:
            self.add_warning(
                f'Average processing time is high: {avg_time:.1f} seconds'
            )
        elif avg_time and avg_time < 1:
            self.add_warning(
                f'Average processing time is suspiciously low: {avg_time:.1f} seconds'
            )
        else:
            self.pass_check(f'Reasonable processing times (avg: {avg_time:.1f}s)')
    
    def analyze_post_migration_performance(self):
        """Analyze performance after migration"""
        self.stdout.write('Analyzing post-migration performance...')
        
        # Compare pre and post migration performance if data available
        try:
            # Get recent results (assuming they are post-migration)
            recent_cutoff = timezone.now() - timedelta(days=7)
            recent_stats = OCRResult.objects.filter(
                created_at__gte=recent_cutoff
            ).aggregate(
                avg_time=Avg('processing_time'),
                avg_confidence=Avg('confidence_score'),
                count=Count('id')
            )
            
            if recent_stats['count'] > 0:
                self.validation_results['statistics']['recent_performance'] = recent_stats
                self.pass_check(f'Recent performance data available ({recent_stats["count"]} results)')
            else:
                self.add_warning('No recent OCR results for performance comparison')
                
        except Exception as e:
            self.add_warning(f'Could not analyze post-migration performance: {e}')
    
    def validate_api_compatibility(self):
        """Validate API compatibility after migration"""
        self.stdout.write('Validating API compatibility...')
        
        # Check that OCR results can be serialized properly
        try:
            sample_results = OCRResult.objects.all()[:10]
            
            for result in sample_results:
                # Test basic API methods
                api_dict = result.to_api_dict()
                validation_fields = result.get_validation_fields()
                api_status = result.get_api_status()
                
                # Basic validation
                if not isinstance(api_dict, dict):
                    self.fail_check('API serialization', 'to_api_dict() not returning dict')
                    return
                
                if not isinstance(validation_fields, dict):
                    self.fail_check('API validation', 'get_validation_fields() not returning dict')
                    return
                
                if not isinstance(api_status, dict):
                    self.fail_check('API status', 'get_api_status() not returning dict')
                    return
            
            self.pass_check('API compatibility validation')
            
        except Exception as e:
            self.fail_check('API compatibility', f'API methods failing: {e}')
    
    def estimate_migration_impact(self):
        """Estimate migration impact"""
        self.stdout.write('Estimating migration impact...')
        
        total_results = OCRResult.objects.count()
        
        # Estimate processing time (rough calculation)
        estimated_seconds = total_results * 0.1  # 0.1 seconds per record
        estimated_minutes = estimated_seconds / 60
        
        self.validation_results['statistics']['migration_estimate'] = {
            'total_records': total_results,
            'estimated_seconds': estimated_seconds,
            'estimated_minutes': estimated_minutes,
        }
        
        if estimated_minutes > 60:
            self.add_warning(
                f'Migration estimated to take {estimated_minutes:.1f} minutes'
            )
        else:
            self.pass_check(f'Migration estimated to take {estimated_minutes:.1f} minutes')
    
    def analyze_confidence_distribution(self):
        """Analyze confidence score distribution"""
        self.stdout.write('Analyzing confidence distribution...')
        
        # Get confidence distribution
        confidence_ranges = [
            (0, 20, 'Very Low'),
            (20, 40, 'Low'),
            (40, 60, 'Medium'),
            (60, 80, 'High'),
            (80, 100, 'Very High'),
        ]
        
        distribution = {}
        total_results = OCRResult.objects.count()
        
        for min_conf, max_conf, label in confidence_ranges:
            count = OCRResult.objects.filter(
                confidence_score__gte=min_conf,
                confidence_score__lt=max_conf
            ).count()
            
            percentage = (count / total_results) * 100 if total_results > 0 else 0
            distribution[label] = {
                'count': count,
                'percentage': percentage,
                'range': f'{min_conf}-{max_conf}%'
            }
        
        self.validation_results['statistics']['confidence_distribution'] = distribution
        
        # Check for concerning distributions
        if distribution['Very Low']['percentage'] > 20:
            self.add_warning(
                f'{distribution["Very Low"]["percentage"]:.1f}% of results have very low confidence'
            )
        
        if distribution['Very High']['percentage'] > 80:
            self.add_warning(
                f'{distribution["Very High"]["percentage"]:.1f}% of results have very high confidence (suspicious)'
            )
    
    def check_data_consistency(self):
        """Check data consistency across related models"""
        self.stdout.write('Checking data consistency...')
        
        # Check OCRResult <-> Faktura consistency
        ocr_with_faktura = OCRResult.objects.filter(faktura__isnull=False).count()
        faktura_with_ocr = Faktura.objects.filter(
            source_document__isnull=False
        ).count()
        
        if abs(ocr_with_faktura - faktura_with_ocr) > 10:
            self.add_warning(
                f'OCR-Faktura relationship inconsistency: '
                f'{ocr_with_faktura} OCR results vs {faktura_with_ocr} Fakturas'
            )
        else:
            self.pass_check('OCR-Faktura relationship consistency')
        
        # Check DocumentUpload <-> OCRResult consistency
        docs_with_ocr = DocumentUpload.objects.filter(
            ocrresult__isnull=False
        ).count()
        ocr_with_docs = OCRResult.objects.filter(
            document__isnull=False
        ).count()
        
        if docs_with_ocr != ocr_with_docs:
            self.fail_check(
                'Document-OCR relationship consistency',
                f'{docs_with_ocr} documents vs {ocr_with_docs} OCR results'
            )
        else:
            self.pass_check('Document-OCR relationship consistency')
    
    def check_processing_pipeline_integrity(self):
        """Check processing pipeline integrity"""
        self.stdout.write('Checking processing pipeline integrity...')
        
        try:
            # Check step ordering
            invalid_ordering = OCRProcessingStep.objects.filter(
                step_order__lt=1
            ).count()
            
            if invalid_ordering > 0:
                self.fail_check(
                    'Processing step ordering',
                    f'{invalid_ordering} steps have invalid ordering'
                )
            else:
                self.pass_check('Processing step ordering valid')
            
            # Check step completion
            incomplete_steps = OCRProcessingStep.objects.filter(
                step_status='processing',
                started_at__lt=timezone.now() - timedelta(hours=1)
            ).count()
            
            if incomplete_steps > 0:
                self.add_warning(
                    f'{incomplete_steps} processing steps appear stuck'
                )
            else:
                self.pass_check('No stuck processing steps')
                
        except Exception as e:
            self.add_warning(f'Could not check processing pipeline: {e}')
    
    def pass_check(self, check_name: str):
        """Record a passed check"""
        self.validation_results['checks_passed'] += 1
        if self.verbosity >= 2:
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ {check_name}')
            )
    
    def fail_check(self, check_name: str, error_message: str):
        """Record a failed check"""
        self.validation_results['checks_failed'] += 1
        error = f'{check_name}: {error_message}'
        self.validation_results['errors'].append(error)
        
        self.stdout.write(
            self.style.ERROR(f'  ✗ {error}')
        )
    
    def add_warning(self, warning_message: str):
        """Add a warning"""
        self.validation_results['warnings'] += 1
        self.validation_results['warnings_list'].append(warning_message)
        
        if self.verbosity >= 1:
            self.stdout.write(
                self.style.WARNING(f'  ⚠ {warning_message}')
            )
    
    def add_error(self, error_message: str):
        """Add an error"""
        self.validation_results['errors'].append(error_message)
    
    def generate_validation_report(self):
        """Generate and display validation report"""
        results = self.validation_results
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('VALIDATION REPORT')
        self.stdout.write('='*60)
        self.stdout.write(f'Validation Type: {results["validation_type"].upper()}')
        self.stdout.write(f'Timestamp: {results["timestamp"]}')
        self.stdout.write(f'Checks Passed: {results["checks_passed"]}')
        self.stdout.write(f'Checks Failed: {results["checks_failed"]}')
        self.stdout.write(f'Warnings: {results["warnings"]}')
        
        if results['errors']:
            self.stdout.write('\nERRORS:')
            for error in results['errors']:
                self.stdout.write(f'  • {error}')
        
        if results['warnings_list']:
            self.stdout.write('\nWARNINGS:')
            for warning in results['warnings_list']:
                self.stdout.write(f'  • {warning}')
        
        # Statistics summary
        if results['statistics']:
            self.stdout.write('\nSTATISTICS:')
            for key, value in results['statistics'].items():
                if isinstance(value, dict):
                    self.stdout.write(f'  {key}:')
                    for sub_key, sub_value in value.items():
                        self.stdout.write(f'    {sub_key}: {sub_value}')
                else:
                    self.stdout.write(f'  {key}: {value}')
        
        # Overall status
        if results['checks_failed'] == 0:
            self.stdout.write(
                self.style.SUCCESS('\n✓ VALIDATION PASSED')
            )
        else:
            self.stdout.write(
                self.style.ERROR('\n✗ VALIDATION FAILED')
            )
        
        self.stdout.write('='*60)
        
        # Save to file if requested
        if self.output_file:
            try:
                with open(self.output_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                self.stdout.write(f'\nValidation results saved to: {self.output_file}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to save results: {e}')
                )