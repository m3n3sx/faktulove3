"""
Django management command for rolling back OCR data migration.

This command provides comprehensive rollback capabilities for the OCR migration:
1. Restore original processor versions and metadata
2. Remove migration-specific data and processing steps
3. Restore original confidence scores
4. Validate rollback integrity

Usage:
    python manage.py rollback_ocr_migration --backup-file backup.json --dry-run
    python manage.py rollback_ocr_migration --backup-file backup.json --execute
    python manage.py rollback_ocr_migration --auto-detect-backup --execute
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from faktury.models import (
    OCRResult, OCREngine, OCRProcessingStep, OCRValidation, OCRProcessingLog
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Rollback OCR data migration to pre-migration state'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rollback_stats = {
            'total_records': 0,
            'restored_records': 0,
            'failed_records': 0,
            'removed_steps': 0,
            'removed_engines': 0,
            'validation_errors': [],
        }
        self.backup_data = {}
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-file',
            type=str,
            help='JSON backup file containing pre-migration data',
        )
        parser.add_argument(
            '--auto-detect-backup',
            action='store_true',
            help='Automatically detect and use the most recent backup file',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview rollback changes without executing them',
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Execute the rollback',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each batch (default: 100)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force rollback even if validation fails',
        )
        parser.add_argument(
            '--preserve-new-data',
            action='store_true',
            help='Preserve data created after migration (e.g., new OCR results)',
        )
        parser.add_argument(
            '--cleanup-migration-artifacts',
            action='store_true',
            help='Remove migration-specific engines and processing steps',
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.verbosity = options['verbosity']
        self.dry_run = options['dry_run']
        self.batch_size = options['batch_size']
        self.force = options['force']
        self.preserve_new_data = options['preserve_new_data']
        self.cleanup_artifacts = options['cleanup_migration_artifacts']
        
        try:
            # Load backup data
            if options['auto_detect_backup']:
                self.load_auto_detected_backup()
            elif options['backup_file']:
                self.load_backup_file(options['backup_file'])
            else:
                raise CommandError('Please specify --backup-file or --auto-detect-backup')
            
            if options['execute'] or options['dry_run']:
                self.execute_rollback()
            else:
                self.stdout.write(
                    self.style.ERROR('Please specify --dry-run or --execute')
                )
                return
            
            self.generate_rollback_report()
            
        except Exception as e:
            logger.error(f"Rollback command failed: {e}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f'Rollback failed: {e}')
            )
            raise CommandError(f'Rollback failed: {e}')
    
    def load_backup_file(self, backup_file: str):
        """Load backup data from specified file"""
        self.stdout.write(f'Loading backup data from {backup_file}...')
        
        try:
            with open(backup_file, 'r') as f:
                self.backup_data = json.load(f)
            
            if not isinstance(self.backup_data, dict):
                raise ValueError('Backup file must contain a JSON object')
            
            record_count = len(self.backup_data)
            self.rollback_stats['total_records'] = record_count
            
            self.stdout.write(
                self.style.SUCCESS(f'Loaded backup data for {record_count} records')
            )
            
        except FileNotFoundError:
            raise CommandError(f'Backup file not found: {backup_file}')
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON in backup file: {e}')
        except Exception as e:
            raise CommandError(f'Failed to load backup file: {e}')
    
    def load_auto_detected_backup(self):
        """Auto-detect and load the most recent backup file"""
        import os
        import glob
        
        self.stdout.write('Auto-detecting backup file...')
        
        # Look for backup files in current directory
        backup_patterns = [
            'ocr_migration_backup*.json',
            'ocr_backup*.json',
            'migration_backup*.json',
        ]
        
        backup_files = []
        for pattern in backup_patterns:
            backup_files.extend(glob.glob(pattern))
        
        if not backup_files:
            raise CommandError(
                'No backup files found. Please specify --backup-file explicitly.'
            )
        
        # Get the most recent backup file
        most_recent = max(backup_files, key=os.path.getmtime)
        
        self.stdout.write(f'Using backup file: {most_recent}')
        self.load_backup_file(most_recent)
    
    def execute_rollback(self):
        """Execute the rollback process"""
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting OCR migration rollback {"(DRY RUN)" if self.dry_run else ""}'
            )
        )
        
        # Step 1: Validate rollback prerequisites
        if not self.validate_rollback_prerequisites():
            if not self.force:
                raise CommandError('Rollback validation failed. Use --force to override.')
            self.stdout.write(
                self.style.WARNING('Rollback validation failed, but continuing due to --force')
            )
        
        # Step 2: Restore OCR result data
        self.restore_ocr_results()
        
        # Step 3: Clean up migration artifacts
        if self.cleanup_artifacts:
            self.cleanup_migration_artifacts()
        
        # Step 4: Validate rollback integrity
        self.validate_rollback_integrity()
    
    def validate_rollback_prerequisites(self) -> bool:
        """Validate that rollback can be performed safely"""
        self.stdout.write('Validating rollback prerequisites...')
        
        validation_errors = []
        
        # Check if backup data is valid
        if not self.backup_data:
            validation_errors.append('No backup data loaded')
        
        # Check if OCR results exist for rollback
        backup_ids = list(self.backup_data.keys())
        existing_results = OCRResult.objects.filter(
            id__in=backup_ids
        ).values_list('id', flat=True)
        
        missing_results = set(backup_ids) - set(str(id) for id in existing_results)
        if missing_results:
            validation_errors.append(
                f'{len(missing_results)} OCR results from backup not found in database'
            )
        
        # Check for data integrity
        if not self.preserve_new_data:
            # Check if there are new OCR results created after migration
            try:
                # Assume migration happened recently if we have migration processing steps
                migration_steps = OCRProcessingStep.objects.filter(
                    step_name='migration_from_google_cloud'
                ).order_by('-started_at').first()
                
                if migration_steps:
                    migration_time = migration_steps.started_at
                    new_results = OCRResult.objects.filter(
                        created_at__gt=migration_time
                    ).count()
                    
                    if new_results > 0:
                        validation_errors.append(
                            f'{new_results} new OCR results created after migration. '
                            'Use --preserve-new-data to keep them.'
                        )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not check for new data: {e}')
                )
        
        if validation_errors:
            for error in validation_errors:
                self.stdout.write(self.style.ERROR(f'Validation error: {error}'))
            return False
        
        self.stdout.write(self.style.SUCCESS('Rollback prerequisites validated'))
        return True
    
    def restore_ocr_results(self):
        """Restore OCR results to pre-migration state"""
        self.stdout.write('Restoring OCR results...')
        
        total_records = len(self.backup_data)
        if total_records == 0:
            self.stdout.write('No records to restore')
            return
        
        # Process in batches
        batch_count = 0
        restored_count = 0
        
        backup_items = list(self.backup_data.items())
        
        for batch_start in range(0, total_records, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total_records)
            batch = backup_items[batch_start:batch_end]
            batch_count += 1
            
            self.stdout.write(
                f'Processing batch {batch_count} ({batch_start + 1}-{batch_end} of {total_records})'
            )
            
            if not self.dry_run:
                with transaction.atomic():
                    batch_restored = self.restore_batch(batch)
                    restored_count += batch_restored
            else:
                batch_restored = self.preview_restore_batch(batch)
                restored_count += batch_restored
        
        self.rollback_stats['restored_records'] = restored_count
        self.stdout.write(
            self.style.SUCCESS(f'Restored {restored_count} OCR results')
        )
    
    def restore_batch(self, batch: List[tuple]) -> int:
        """Restore a batch of OCR results"""
        restored_count = 0
        
        for ocr_result_id, original_data in batch:
            try:
                ocr_result = OCRResult.objects.get(id=int(ocr_result_id))
                
                # Restore original fields
                ocr_result.processor_version = original_data.get('processor_version')
                ocr_result.processing_location = original_data.get('processing_location')
                ocr_result.pipeline_version = original_data.get('pipeline_version', '1.0')
                ocr_result.confidence_score = original_data.get('confidence_score', 0.0)
                
                # Clear migration-specific fields
                ocr_result.primary_engine = None
                
                # Remove migration metadata from engine_results
                if ocr_result.engine_results and 'migration_info' in ocr_result.engine_results:
                    engine_results = ocr_result.engine_results.copy()
                    del engine_results['migration_info']
                    ocr_result.engine_results = engine_results
                
                # Clear new architecture fields
                ocr_result.best_engine_result = None
                ocr_result.preprocessing_applied = []
                ocr_result.fallback_used = False
                
                ocr_result.save()
                restored_count += 1
                
                # Remove migration processing steps
                self.remove_migration_processing_steps(ocr_result)
                
            except OCRResult.DoesNotExist:
                logger.warning(f'OCR result {ocr_result_id} not found during rollback')
                self.rollback_stats['failed_records'] += 1
            except Exception as e:
                logger.error(f'Failed to restore OCR result {ocr_result_id}: {e}')
                self.rollback_stats['failed_records'] += 1
        
        return restored_count
    
    def preview_restore_batch(self, batch: List[tuple]) -> int:
        """Preview restore changes for a batch"""
        preview_count = 0
        
        for ocr_result_id, original_data in batch:
            try:
                ocr_result = OCRResult.objects.get(id=int(ocr_result_id))
                
                self.stdout.write(
                    f'  OCR Result {ocr_result_id}: '
                    f'processor_version: {ocr_result.processor_version} -> {original_data.get("processor_version")}, '
                    f'confidence: {ocr_result.confidence_score} -> {original_data.get("confidence_score")}'
                )
                preview_count += 1
                
            except OCRResult.DoesNotExist:
                self.stdout.write(
                    f'  OCR Result {ocr_result_id}: NOT FOUND'
                )
        
        return preview_count
    
    def remove_migration_processing_steps(self, ocr_result):
        """Remove migration-specific processing steps"""
        try:
            removed_count = OCRProcessingStep.objects.filter(
                ocr_result=ocr_result,
                step_name__in=[
                    'migration_from_google_cloud',
                    'document_preprocessing',  # If created during migration
                    'ocr_text_extraction',     # If created during migration
                    'field_extraction',        # If created during migration
                    'confidence_calculation',  # If created during migration
                ],
                step_data__migrated=True  # Only remove steps marked as migrated
            ).delete()
            
            self.rollback_stats['removed_steps'] += removed_count[0]
            
        except Exception as e:
            logger.warning(f'Failed to remove processing steps for OCR result {ocr_result.id}: {e}')
    
    def cleanup_migration_artifacts(self):
        """Clean up migration-specific artifacts"""
        self.stdout.write('Cleaning up migration artifacts...')
        
        if not self.dry_run:
            # Remove migration-specific OCR engines
            migration_engines = OCREngine.objects.filter(
                Q(name__icontains='migration') |
                Q(configuration__migration_source=True) |
                Q(engine_type='google_cloud', is_active=False)
            )
            
            removed_engines = 0
            for engine in migration_engines:
                # Only remove if no active processing steps reference it
                active_steps = OCRProcessingStep.objects.filter(
                    engine_used=engine,
                    step_status__in=['pending', 'processing']
                ).count()
                
                if active_steps == 0:
                    engine.delete()
                    removed_engines += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Keeping engine {engine.name} - has active processing steps'
                        )
                    )
            
            self.rollback_stats['removed_engines'] = removed_engines
            self.stdout.write(f'Removed {removed_engines} migration engines')
            
            # Remove migration processing logs
            migration_logs = OCRProcessingLog.objects.filter(
                message__icontains='migration'
            )
            log_count = migration_logs.count()
            migration_logs.delete()
            
            self.stdout.write(f'Removed {log_count} migration log entries')
        else:
            # Preview cleanup
            migration_engines = OCREngine.objects.filter(
                Q(name__icontains='migration') |
                Q(configuration__migration_source=True) |
                Q(engine_type='google_cloud', is_active=False)
            ).count()
            
            migration_logs = OCRProcessingLog.objects.filter(
                message__icontains='migration'
            ).count()
            
            self.stdout.write(f'Would remove {migration_engines} migration engines')
            self.stdout.write(f'Would remove {migration_logs} migration log entries')
    
    def validate_rollback_integrity(self):
        """Validate rollback integrity"""
        self.stdout.write('Validating rollback integrity...')
        
        validation_errors = []
        
        # Check that processor versions are restored
        google_cloud_results = OCRResult.objects.filter(
            Q(processor_version__icontains='migrated_from') |
            Q(primary_engine__isnull=False)
        ).count()
        
        if google_cloud_results > 0:
            validation_errors.append(
                f'{google_cloud_results} OCR results still show migration artifacts'
            )
        
        # Check confidence score validity
        invalid_confidence = OCRResult.objects.filter(
            Q(confidence_score__lt=0) | Q(confidence_score__gt=100)
        ).count()
        
        if invalid_confidence > 0:
            validation_errors.append(
                f'{invalid_confidence} OCR results have invalid confidence scores'
            )
        
        # Check for remaining migration processing steps
        migration_steps = OCRProcessingStep.objects.filter(
            step_name='migration_from_google_cloud'
        ).count()
        
        if migration_steps > 0:
            validation_errors.append(
                f'{migration_steps} migration processing steps still exist'
            )
        
        if validation_errors:
            for error in validation_errors:
                self.stdout.write(self.style.ERROR(f'Validation error: {error}'))
                self.rollback_stats['validation_errors'].append(error)
            
            if not self.force:
                raise CommandError('Rollback validation failed')
        else:
            self.stdout.write(self.style.SUCCESS('Rollback integrity validated'))
    
    def generate_rollback_report(self):
        """Generate and display rollback report"""
        stats = self.rollback_stats
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('ROLLBACK REPORT')
        self.stdout.write('='*60)
        self.stdout.write(f'Rollback type: {"DRY RUN" if self.dry_run else "EXECUTED"}')
        self.stdout.write(f'Total records in backup: {stats["total_records"]}')
        self.stdout.write(f'Restored records: {stats["restored_records"]}')
        self.stdout.write(f'Failed records: {stats["failed_records"]}')
        self.stdout.write(f'Removed processing steps: {stats["removed_steps"]}')
        
        if self.cleanup_artifacts:
            self.stdout.write(f'Removed migration engines: {stats["removed_engines"]}')
        
        if stats['validation_errors']:
            self.stdout.write('\nVALIDATION ERRORS:')
            for error in stats['validation_errors']:
                self.stdout.write(f'  • {error}')
        
        # Overall status
        if stats['failed_records'] == 0 and not stats['validation_errors']:
            self.stdout.write(
                self.style.SUCCESS('\n✓ ROLLBACK COMPLETED SUCCESSFULLY')
            )
        else:
            self.stdout.write(
                self.style.ERROR('\n✗ ROLLBACK COMPLETED WITH ERRORS')
            )
        
        if not self.dry_run:
            self.stdout.write('\nTo verify rollback success, run:')
            self.stdout.write('python manage.py validate_ocr_migration --pre-migration')
        
        self.stdout.write('='*60)