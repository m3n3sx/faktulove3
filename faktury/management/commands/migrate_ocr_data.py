"""
Django management command for migrating OCR data from Google Cloud to open-source engines.

This command handles:
1. Mapping Google Cloud processor versions to new OCR engines
2. Recalculating confidence scores for historical data
3. Validating data integrity during migration
4. Providing rollback capabilities

Usage:
    python manage.py migrate_ocr_data --dry-run  # Preview changes
    python manage.py migrate_ocr_data --execute  # Execute migration
    python manage.py migrate_ocr_data --rollback # Rollback migration
"""

import json
import logging
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.models import Q, Count, Avg
from django.utils import timezone as django_timezone

from faktury.models import (
    OCRResult, OCREngine, OCRProcessingStep, DocumentUpload, 
    Faktura, OCRValidation
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate OCR data from Google Cloud to open-source engines'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.migration_log = []
        self.rollback_data = {}
        self.stats = {
            'total_records': 0,
            'migrated_records': 0,
            'failed_records': 0,
            'confidence_updates': 0,
            'engine_mappings': 0,
        }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without executing them',
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Execute the migration',
        )
        parser.add_argument(
            '--rollback',
            action='store_true',
            help='Rollback the migration using stored backup data',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each batch (default: 100)',
        )
        parser.add_argument(
            '--backup-file',
            type=str,
            default='ocr_migration_backup.json',
            help='File to store backup data for rollback (default: ocr_migration_backup.json)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if validation fails',
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.verbosity = options['verbosity']
        self.dry_run = options['dry_run']
        self.batch_size = options['batch_size']
        self.backup_file = options['backup_file']
        self.force = options['force']
        
        try:
            if options['rollback']:
                self.handle_rollback()
            elif options['execute'] or options['dry_run']:
                self.handle_migration()
            else:
                self.stdout.write(
                    self.style.ERROR(
                        'Please specify --dry-run, --execute, or --rollback'
                    )
                )
                return
        except Exception as e:
            logger.error(f"Migration command failed: {e}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f'Migration failed: {e}')
            )
            raise CommandError(f'Migration failed: {e}')
    
    def handle_migration(self):
        """Handle the main migration process"""
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting OCR data migration {"(DRY RUN)" if self.dry_run else ""}'
            )
        )
        
        # Step 1: Validate pre-migration state
        if not self.validate_pre_migration():
            if not self.force:
                raise CommandError('Pre-migration validation failed. Use --force to override.')
            self.stdout.write(
                self.style.WARNING('Pre-migration validation failed, but continuing due to --force')
            )
        
        # Step 2: Create or update OCR engines
        self.create_ocr_engines()
        
        # Step 3: Migrate OCR results
        self.migrate_ocr_results()
        
        # Step 4: Update processing steps
        self.migrate_processing_steps()
        
        # Step 5: Recalculate confidence scores
        self.recalculate_confidence_scores()
        
        # Step 6: Validate post-migration state
        if not self.validate_post_migration():
            if not self.dry_run:
                self.stdout.write(
                    self.style.ERROR('Post-migration validation failed! Consider rollback.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Post-migration validation would fail in dry run')
                )
        
        # Step 7: Generate migration report
        self.generate_migration_report()
    
    def handle_rollback(self):
        """Handle rollback process"""
        self.stdout.write(
            self.style.WARNING('Starting OCR data migration rollback')
        )
        
        try:
            with open(self.backup_file, 'r') as f:
                self.rollback_data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f'Backup file {self.backup_file} not found')
        except json.JSONDecodeError:
            raise CommandError(f'Invalid backup file format: {self.backup_file}')
        
        self.execute_rollback()
        self.stdout.write(
            self.style.SUCCESS('Migration rollback completed successfully')
        )
    
    def validate_pre_migration(self) -> bool:
        """Validate system state before migration"""
        self.stdout.write('Validating pre-migration state...')
        
        validation_errors = []
        
        # Check for existing OCR results
        total_ocr_results = OCRResult.objects.count()
        self.stats['total_records'] = total_ocr_results
        
        if total_ocr_results == 0:
            validation_errors.append('No OCR results found to migrate')
        
        # Check for Google Cloud processor versions
        google_cloud_results = OCRResult.objects.filter(
            Q(processor_version__icontains='google') |
            Q(processor_version__icontains='document-ai') |
            Q(processor_version__isnull=True) |
            Q(processor_version='')
        ).count()
        
        if google_cloud_results == 0:
            validation_errors.append('No Google Cloud OCR results found to migrate')
        
        # Check database integrity
        orphaned_results = OCRResult.objects.filter(document__isnull=True).count()
        if orphaned_results > 0:
            validation_errors.append(f'Found {orphaned_results} orphaned OCR results')
        
        # Check for required fields
        missing_data_results = OCRResult.objects.filter(
            Q(extracted_data__isnull=True) | Q(extracted_data={})
        ).count()
        
        if missing_data_results > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'Found {missing_data_results} OCR results with missing extracted_data'
                )
            )
        
        if validation_errors:
            for error in validation_errors:
                self.stdout.write(self.style.ERROR(f'Validation error: {error}'))
            return False
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Pre-migration validation passed. Found {total_ocr_results} OCR results to migrate.'
            )
        )
        return True
    
    def create_ocr_engines(self):
        """Create or update OCR engine records"""
        self.stdout.write('Creating OCR engine records...')
        
        engines_config = [
            {
                'name': 'Google Cloud Document AI',
                'engine_type': 'google_cloud',
                'version': '1.0',
                'is_active': False,  # Deprecated
                'priority': 1,
                'configuration': {
                    'deprecated': True,
                    'migration_source': True,
                    'processor_types': ['invoice', 'document'],
                }
            },
            {
                'name': 'Tesseract OCR',
                'engine_type': 'tesseract',
                'version': '5.3.0',
                'is_active': True,
                'priority': 2,
                'configuration': {
                    'language': 'pol+eng',
                    'psm': 6,
                    'oem': 3,
                }
            },
            {
                'name': 'EasyOCR',
                'engine_type': 'easyocr',
                'version': '1.7.0',
                'is_active': True,
                'priority': 3,
                'configuration': {
                    'languages': ['pl', 'en'],
                    'gpu': False,
                }
            },
            {
                'name': 'Composite OCR Engine',
                'engine_type': 'composite',
                'version': '2.0',
                'is_active': True,
                'priority': 1,
                'configuration': {
                    'primary_engines': ['tesseract', 'easyocr'],
                    'confidence_threshold': 80.0,
                }
            }
        ]
        
        created_engines = {}
        
        for engine_config in engines_config:
            if not self.dry_run:
                engine, created = OCREngine.objects.get_or_create(
                    name=engine_config['name'],
                    engine_type=engine_config['engine_type'],
                    defaults=engine_config
                )
                
                if not created:
                    # Update existing engine
                    for field, value in engine_config.items():
                        if field not in ['name', 'engine_type']:
                            setattr(engine, field, value)
                    engine.save()
                
                created_engines[engine_config['engine_type']] = engine
                
                self.stdout.write(
                    f'  {"Created" if created else "Updated"} engine: {engine.name}'
                )
            else:
                self.stdout.write(
                    f'  Would create/update engine: {engine_config["name"]}'
                )
        
        self.created_engines = created_engines
    
    def migrate_ocr_results(self):
        """Migrate OCR results with processor version mapping"""
        self.stdout.write('Migrating OCR results...')
        
        # Get all OCR results that need migration
        ocr_results = OCRResult.objects.filter(
            Q(processor_version__icontains='google') |
            Q(processor_version__icontains='document-ai') |
            Q(processor_version__isnull=True) |
            Q(processor_version='') |
            Q(processor_version='mock')
        ).select_related('document')
        
        total_results = ocr_results.count()
        self.stdout.write(f'Found {total_results} OCR results to migrate')
        
        if total_results == 0:
            return
        
        # Process in batches
        batch_count = 0
        migrated_count = 0
        
        for batch_start in range(0, total_results, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total_results)
            batch = ocr_results[batch_start:batch_end]
            batch_count += 1
            
            self.stdout.write(
                f'Processing batch {batch_count} ({batch_start + 1}-{batch_end} of {total_results})'
            )
            
            if not self.dry_run:
                with transaction.atomic():
                    batch_migrated = self.migrate_ocr_batch(batch)
                    migrated_count += batch_migrated
            else:
                batch_migrated = self.preview_ocr_batch(batch)
                migrated_count += batch_migrated
        
        self.stats['migrated_records'] = migrated_count
        self.stdout.write(
            self.style.SUCCESS(f'Migrated {migrated_count} OCR results')
        )
    
    def migrate_ocr_batch(self, batch) -> int:
        """Migrate a batch of OCR results"""
        migrated_count = 0
        
        for ocr_result in batch:
            try:
                # Store original data for rollback
                original_data = {
                    'id': ocr_result.id,
                    'processor_version': ocr_result.processor_version,
                    'processing_location': ocr_result.processing_location,
                    'primary_engine_id': ocr_result.primary_engine_id,
                    'pipeline_version': ocr_result.pipeline_version,
                    'confidence_score': float(ocr_result.confidence_score),
                }
                
                if ocr_result.id not in self.rollback_data:
                    self.rollback_data[ocr_result.id] = original_data
                
                # Map processor version to new engine
                new_engine = self.map_processor_to_engine(ocr_result.processor_version)
                
                # Update OCR result fields
                ocr_result.primary_engine = new_engine
                ocr_result.processor_version = f'migrated_from_{ocr_result.processor_version or "unknown"}'
                ocr_result.processing_location = 'on_premises'
                ocr_result.pipeline_version = '2.0'
                
                # Add migration metadata
                if not ocr_result.engine_results:
                    ocr_result.engine_results = {}
                
                ocr_result.engine_results['migration_info'] = {
                    'migrated_at': django_timezone.now().isoformat(),
                    'original_processor': original_data['processor_version'],
                    'migration_version': '1.0',
                }
                
                ocr_result.save()
                migrated_count += 1
                
                # Create processing step record for historical tracking
                self.create_migration_processing_step(ocr_result, new_engine, original_data)
                
            except Exception as e:
                logger.error(f"Failed to migrate OCR result {ocr_result.id}: {e}")
                self.stats['failed_records'] += 1
        
        return migrated_count
    
    def preview_ocr_batch(self, batch) -> int:
        """Preview migration changes for a batch"""
        preview_count = 0
        
        for ocr_result in batch:
            new_engine = self.map_processor_to_engine(ocr_result.processor_version)
            
            self.stdout.write(
                f'  OCR Result {ocr_result.id}: '
                f'{ocr_result.processor_version or "None"} -> {new_engine.name}'
            )
            preview_count += 1
        
        return preview_count
    
    def map_processor_to_engine(self, processor_version: Optional[str]) -> 'OCREngine':
        """Map Google Cloud processor version to new OCR engine"""
        if not processor_version or processor_version in ['', 'mock']:
            # Default to composite engine for unknown processors
            return self.created_engines['composite']
        
        processor_lower = processor_version.lower()
        
        # Map based on processor version patterns
        if 'google' in processor_lower or 'document-ai' in processor_lower:
            # Google Cloud processors map to composite engine
            return self.created_engines['composite']
        elif 'tesseract' in processor_lower:
            return self.created_engines['tesseract']
        elif 'easyocr' in processor_lower:
            return self.created_engines['easyocr']
        else:
            # Default to composite engine
            return self.created_engines['composite']
    
    def create_migration_processing_step(self, ocr_result, engine, original_data):
        """Create a processing step record for migration tracking"""
        try:
            OCRProcessingStep.objects.create(
                ocr_result=ocr_result,
                step_name='migration_from_google_cloud',
                step_type='post_processing',
                engine_used=engine,
                step_order=999,  # High order to indicate post-processing
                step_status='completed',
                processing_time=0.0,
                confidence_score=ocr_result.confidence_score,
                step_data={
                    'migration_type': 'google_cloud_to_opensource',
                    'original_processor': original_data['processor_version'],
                    'migration_timestamp': django_timezone.now().isoformat(),
                },
                input_data=original_data,
                output_data={
                    'new_engine': engine.name,
                    'new_processor_version': ocr_result.processor_version,
                },
                started_at=django_timezone.now(),
                completed_at=django_timezone.now(),
            )
        except Exception as e:
            logger.warning(f"Failed to create migration processing step: {e}")
    
    def migrate_processing_steps(self):
        """Create processing steps for existing OCR results that don't have them"""
        self.stdout.write('Creating processing steps for migrated results...')
        
        # Find OCR results without processing steps
        ocr_results_without_steps = OCRResult.objects.filter(
            processing_steps__isnull=True
        ).distinct()
        
        count = ocr_results_without_steps.count()
        if count == 0:
            self.stdout.write('No OCR results need processing steps')
            return
        
        self.stdout.write(f'Creating processing steps for {count} OCR results')
        
        if not self.dry_run:
            for ocr_result in ocr_results_without_steps:
                try:
                    self.create_default_processing_steps(ocr_result)
                except Exception as e:
                    logger.error(f"Failed to create processing steps for {ocr_result.id}: {e}")
    
    def create_default_processing_steps(self, ocr_result):
        """Create default processing steps for an OCR result"""
        engine = ocr_result.primary_engine or self.created_engines['composite']
        
        steps = [
            {
                'step_name': 'document_preprocessing',
                'step_type': 'preprocessing',
                'step_order': 1,
                'confidence_score': 95.0,
            },
            {
                'step_name': 'ocr_text_extraction',
                'step_type': 'ocr_extraction',
                'step_order': 2,
                'confidence_score': ocr_result.confidence_score,
            },
            {
                'step_name': 'field_extraction',
                'step_type': 'field_extraction',
                'step_order': 3,
                'confidence_score': ocr_result.confidence_score * 0.9,
            },
            {
                'step_name': 'confidence_calculation',
                'step_type': 'confidence_calculation',
                'step_order': 4,
                'confidence_score': ocr_result.confidence_score,
            },
        ]
        
        for step_config in steps:
            OCRProcessingStep.objects.create(
                ocr_result=ocr_result,
                engine_used=engine,
                step_status='completed',
                processing_time=0.5,  # Estimated time
                step_data={'migrated': True, 'estimated': True},
                started_at=ocr_result.created_at,
                completed_at=ocr_result.created_at,
                **step_config
            )
    
    def recalculate_confidence_scores(self):
        """Recalculate confidence scores for historical data"""
        self.stdout.write('Recalculating confidence scores...')
        
        # Get OCR results that need confidence recalculation
        ocr_results = OCRResult.objects.filter(
            Q(field_confidence__isnull=True) |
            Q(field_confidence={}) |
            Q(confidence_score__lt=0) |
            Q(confidence_score__gt=100)
        )
        
        count = ocr_results.count()
        if count == 0:
            self.stdout.write('No confidence scores need recalculation')
            return
        
        self.stdout.write(f'Recalculating confidence scores for {count} OCR results')
        
        updated_count = 0
        
        for ocr_result in ocr_results:
            try:
                if not self.dry_run:
                    original_confidence = ocr_result.confidence_score
                    new_confidence = self.calculate_confidence_score(ocr_result)
                    
                    if new_confidence != original_confidence:
                        ocr_result.confidence_score = new_confidence
                        ocr_result.save(update_fields=['confidence_score', 'field_confidence'])
                        updated_count += 1
                else:
                    new_confidence = self.calculate_confidence_score(ocr_result)
                    self.stdout.write(
                        f'  OCR Result {ocr_result.id}: '
                        f'{ocr_result.confidence_score:.1f}% -> {new_confidence:.1f}%'
                    )
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to recalculate confidence for {ocr_result.id}: {e}")
        
        self.stats['confidence_updates'] = updated_count
        self.stdout.write(f'Updated confidence scores for {updated_count} OCR results')
    
    def calculate_confidence_score(self, ocr_result) -> float:
        """Calculate confidence score based on extracted data quality"""
        if not ocr_result.extracted_data:
            return 0.0
        
        # Field weights for confidence calculation
        field_weights = {
            'invoice_number': 0.20,
            'numer_faktury': 0.20,
            'invoice_date': 0.15,
            'data_wystawienia': 0.15,
            'supplier_name': 0.15,
            'sprzedawca_nazwa': 0.15,
            'buyer_name': 0.10,
            'nabywca_nazwa': 0.10,
            'total_amount': 0.20,
            'suma_brutto': 0.20,
            'net_amount': 0.10,
            'suma_netto': 0.10,
            'line_items': 0.10,
            'pozycje': 0.10,
        }
        
        total_weight = 0
        weighted_confidence = 0
        field_confidence = {}
        
        for field, weight in field_weights.items():
            if field in ocr_result.extracted_data:
                value = ocr_result.extracted_data[field]
                field_conf = self.calculate_field_confidence(field, value)
                field_confidence[field] = field_conf
                
                weighted_confidence += field_conf * weight
                total_weight += weight
        
        # Calculate overall confidence
        if total_weight > 0:
            overall_confidence = weighted_confidence / total_weight
        else:
            overall_confidence = 50.0  # Default for unknown data
        
        # Store field confidence
        ocr_result.field_confidence = field_confidence
        
        return min(100.0, max(0.0, overall_confidence))
    
    def calculate_field_confidence(self, field_name: str, value) -> float:
        """Calculate confidence for a specific field"""
        if not value or (isinstance(value, str) and not value.strip()):
            return 0.0
        
        # Base confidence for having a value
        confidence = 60.0
        
        # Field-specific confidence boosts
        if field_name in ['invoice_number', 'numer_faktury']:
            # Invoice numbers should follow patterns
            if isinstance(value, str) and len(value) > 3:
                confidence += 30.0
                if '/' in value or '-' in value:
                    confidence += 10.0
        
        elif field_name in ['invoice_date', 'data_wystawienia']:
            # Dates should be parseable
            if isinstance(value, str):
                try:
                    datetime.strptime(value, '%Y-%m-%d')
                    confidence += 40.0
                except ValueError:
                    confidence += 20.0  # Partial credit for date-like strings
        
        elif field_name in ['total_amount', 'suma_brutto', 'net_amount', 'suma_netto']:
            # Amounts should be numeric
            try:
                float(str(value).replace(',', '.'))
                confidence += 35.0
            except (ValueError, TypeError):
                confidence += 10.0
        
        elif field_name in ['supplier_name', 'sprzedawca_nazwa', 'buyer_name', 'nabywca_nazwa']:
            # Names should be reasonable length
            if isinstance(value, str) and len(value) > 5:
                confidence += 30.0
                if any(word in value.lower() for word in ['sp.', 'z', 'o.o.', 's.a.', 'spółka']):
                    confidence += 10.0  # Polish company indicators
        
        elif field_name in ['line_items', 'pozycje']:
            # Line items should be arrays with content
            if isinstance(value, list) and len(value) > 0:
                confidence += 30.0
                if all(isinstance(item, dict) for item in value):
                    confidence += 10.0
        
        return min(100.0, confidence)
    
    def validate_post_migration(self) -> bool:
        """Validate system state after migration"""
        self.stdout.write('Validating post-migration state...')
        
        validation_errors = []
        
        # Check that all OCR results have engines assigned
        results_without_engines = OCRResult.objects.filter(primary_engine__isnull=True).count()
        if results_without_engines > 0:
            validation_errors.append(f'{results_without_engines} OCR results missing primary engine')
        
        # Check confidence score ranges
        invalid_confidence = OCRResult.objects.filter(
            Q(confidence_score__lt=0) | Q(confidence_score__gt=100)
        ).count()
        if invalid_confidence > 0:
            validation_errors.append(f'{invalid_confidence} OCR results have invalid confidence scores')
        
        # Check for data integrity
        total_after = OCRResult.objects.count()
        if total_after != self.stats['total_records']:
            validation_errors.append(
                f'Record count mismatch: {self.stats["total_records"]} -> {total_after}'
            )
        
        # Check that all migrated results have processing steps
        results_without_steps = OCRResult.objects.filter(
            processing_steps__isnull=True
        ).distinct().count()
        if results_without_steps > 0:
            validation_errors.append(f'{results_without_steps} OCR results missing processing steps')
        
        if validation_errors:
            for error in validation_errors:
                self.stdout.write(self.style.ERROR(f'Validation error: {error}'))
            return False
        
        self.stdout.write(self.style.SUCCESS('Post-migration validation passed'))
        return True
    
    def execute_rollback(self):
        """Execute rollback using stored backup data"""
        if not self.rollback_data:
            raise CommandError('No rollback data available')
        
        rollback_count = 0
        
        with transaction.atomic():
            for ocr_result_id, original_data in self.rollback_data.items():
                try:
                    ocr_result = OCRResult.objects.get(id=ocr_result_id)
                    
                    # Restore original values
                    ocr_result.processor_version = original_data['processor_version']
                    ocr_result.processing_location = original_data['processing_location']
                    ocr_result.primary_engine_id = original_data.get('primary_engine_id')
                    ocr_result.pipeline_version = original_data['pipeline_version']
                    ocr_result.confidence_score = original_data['confidence_score']
                    
                    # Remove migration metadata
                    if ocr_result.engine_results and 'migration_info' in ocr_result.engine_results:
                        del ocr_result.engine_results['migration_info']
                    
                    ocr_result.save()
                    rollback_count += 1
                    
                    # Remove migration processing steps
                    OCRProcessingStep.objects.filter(
                        ocr_result=ocr_result,
                        step_name='migration_from_google_cloud'
                    ).delete()
                    
                except OCRResult.DoesNotExist:
                    logger.warning(f'OCR result {ocr_result_id} not found during rollback')
                except Exception as e:
                    logger.error(f'Failed to rollback OCR result {ocr_result_id}: {e}')
        
        self.stdout.write(f'Rolled back {rollback_count} OCR results')
    
    def generate_migration_report(self):
        """Generate and save migration report"""
        if not self.dry_run:
            # Save rollback data
            try:
                with open(self.backup_file, 'w') as f:
                    json.dump(self.rollback_data, f, indent=2)
                self.stdout.write(f'Backup data saved to {self.backup_file}')
            except Exception as e:
                logger.error(f'Failed to save backup data: {e}')
        
        # Generate report
        report = {
            'migration_timestamp': django_timezone.now().isoformat(),
            'dry_run': self.dry_run,
            'statistics': self.stats,
            'engines_created': len(getattr(self, 'created_engines', {})),
            'validation_passed': True,  # Assume passed if we got here
        }
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('MIGRATION REPORT')
        self.stdout.write('='*60)
        self.stdout.write(f'Migration type: {"DRY RUN" if self.dry_run else "EXECUTED"}')
        self.stdout.write(f'Total OCR results: {self.stats["total_records"]}')
        self.stdout.write(f'Migrated records: {self.stats["migrated_records"]}')
        self.stdout.write(f'Failed records: {self.stats["failed_records"]}')
        self.stdout.write(f'Confidence updates: {self.stats["confidence_updates"]}')
        self.stdout.write(f'OCR engines created: {len(getattr(self, "created_engines", {}))}')
        
        if not self.dry_run:
            self.stdout.write(f'Backup file: {self.backup_file}')
            self.stdout.write('\nTo rollback this migration, run:')
            self.stdout.write(f'python manage.py migrate_ocr_data --rollback --backup-file {self.backup_file}')
        
        self.stdout.write('='*60)