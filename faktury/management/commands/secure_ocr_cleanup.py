"""
Management command for secure OCR file cleanup

This command provides secure cleanup operations for OCR temporary files:
- Age-based cleanup of old temporary files
- Document-specific cleanup
- Secure file deletion with overwriting
- Audit logging of cleanup operations
"""

import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from faktury.services.ocr_security_service import (
    get_cleanup_service,
    get_audit_logger,
    OCRSecurityError
)
from faktury.models import DocumentUpload, OCRResult

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Securely clean up OCR temporary files and processing data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--age-hours',
            type=int,
            default=24,
            help='Clean up files older than specified hours (default: 24)'
        )
        
        parser.add_argument(
            '--document-id',
            type=str,
            help='Clean up files for specific document ID'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without actually deleting files'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup even for recently processed documents'
        )
        
        parser.add_argument(
            '--cleanup-database',
            action='store_true',
            help='Also clean up old database records for processed documents'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        """Execute the cleanup command"""
        
        self.verbosity = 2 if options['verbose'] else 1
        self.cleanup_service = get_cleanup_service()
        self.audit_logger = get_audit_logger()
        
        try:
            if options['document_id']:
                # Clean up specific document
                self._cleanup_document(options['document_id'], options['dry_run'])
            else:
                # Clean up old files
                self._cleanup_old_files(
                    options['age_hours'],
                    options['dry_run'],
                    options['force']
                )
            
            if options['cleanup_database'] and not options['dry_run']:
                self._cleanup_database_records(options['age_hours'])
            
            self.stdout.write(
                self.style.SUCCESS('OCR cleanup completed successfully')
            )
            
        except Exception as e:
            logger.error(f"OCR cleanup failed: {e}")
            raise CommandError(f'Cleanup failed: {e}')
    
    def _cleanup_document(self, document_id: str, dry_run: bool):
        """Clean up files for specific document"""
        
        self.stdout.write(f'Cleaning up document: {document_id}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN: No files will actually be deleted')
            )
            
            # Find files that would be deleted
            temp_dir = self.cleanup_service.encryption_service.temp_dir
            from pathlib import Path
            
            pattern = f"{document_id}_*"
            files_found = list(Path(temp_dir).glob(pattern))
            
            if files_found:
                self.stdout.write(f'Would delete {len(files_found)} files:')
                for file_path in files_found:
                    self.stdout.write(f'  - {file_path}')
            else:
                self.stdout.write('No files found for this document')
            
            return
        
        # Perform actual cleanup
        try:
            cleanup_result = self.cleanup_service.cleanup_document_files(
                document_id, 'manual_cleanup'
            )
            
            self.stdout.write(
                f'Document cleanup completed: '
                f'{cleanup_result["files_deleted"]}/{cleanup_result["files_found"]} files deleted'
            )
            
            if cleanup_result.get('files_failed', 0) > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'{cleanup_result["files_failed"]} files failed to delete'
                    )
                )
            
        except OCRSecurityError as e:
            raise CommandError(f'Document cleanup failed: {e}')
    
    def _cleanup_old_files(self, age_hours: int, dry_run: bool, force: bool):
        """Clean up old temporary files"""
        
        self.stdout.write(f'Cleaning up files older than {age_hours} hours')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN: No files will actually be deleted')
            )
            
            # Find files that would be deleted
            temp_dir = self.cleanup_service.encryption_service.temp_dir
            from pathlib import Path
            
            cutoff_time = timezone.now() - timedelta(hours=age_hours)
            old_files = []
            
            for file_path in Path(temp_dir).glob("*.enc"):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(
                        file_path.stat().st_mtime, tz=timezone.utc
                    )
                    if file_mtime < cutoff_time:
                        old_files.append(file_path)
            
            if old_files:
                self.stdout.write(f'Would delete {len(old_files)} old files:')
                if self.verbosity >= 2:
                    for file_path in old_files:
                        file_mtime = datetime.fromtimestamp(
                            file_path.stat().st_mtime, tz=timezone.utc
                        )
                        self.stdout.write(f'  - {file_path} (modified: {file_mtime})')
            else:
                self.stdout.write('No old files found')
            
            return
        
        # Check for recent processing if not forced
        if not force:
            recent_processing = self._check_recent_processing(age_hours)
            if recent_processing:
                self.stdout.write(
                    self.style.WARNING(
                        f'Found {recent_processing} documents processed in last {age_hours} hours. '
                        'Use --force to cleanup anyway.'
                    )
                )
                return
        
        # Perform actual cleanup
        try:
            # Set cleanup age on service
            original_age = self.cleanup_service.cleanup_age_hours
            self.cleanup_service.cleanup_age_hours = age_hours
            
            cleanup_result = self.cleanup_service.cleanup_old_files()
            
            # Restore original age
            self.cleanup_service.cleanup_age_hours = original_age
            
            self.stdout.write(
                f'Age-based cleanup completed: '
                f'{cleanup_result["total_files_deleted"]}/{cleanup_result["total_files_found"]} files deleted'
            )
            
            if cleanup_result.get('total_files_failed', 0) > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'{cleanup_result["total_files_failed"]} files failed to delete'
                    )
                )
            
        except OCRSecurityError as e:
            raise CommandError(f'Age-based cleanup failed: {e}')
    
    def _cleanup_database_records(self, age_hours: int):
        """Clean up old database records"""
        
        self.stdout.write('Cleaning up old database records')
        
        cutoff_time = timezone.now() - timedelta(hours=age_hours)
        
        # Clean up old DocumentUpload records
        old_uploads = DocumentUpload.objects.filter(
            upload_date__lt=cutoff_time,
            processing_status__in=['completed', 'failed', 'cancelled']
        )
        
        upload_count = old_uploads.count()
        if upload_count > 0:
            # Log before deletion
            self.audit_logger.log_security_event(
                'database_cleanup',
                {
                    'record_type': 'DocumentUpload',
                    'records_deleted': upload_count,
                    'cutoff_time': cutoff_time.isoformat(),
                    'cleanup_reason': 'age_based_cleanup'
                },
                severity='info'
            )
            
            old_uploads.delete()
            self.stdout.write(f'Deleted {upload_count} old DocumentUpload records')
        
        # Clean up old OCRResult records (keep those linked to Fakturas)
        old_results = OCRResult.objects.filter(
            created_at__lt=cutoff_time,
            faktura__isnull=True,  # Only delete unlinked results
            processing_status__in=['completed', 'failed']
        )
        
        result_count = old_results.count()
        if result_count > 0:
            # Log before deletion
            self.audit_logger.log_security_event(
                'database_cleanup',
                {
                    'record_type': 'OCRResult',
                    'records_deleted': result_count,
                    'cutoff_time': cutoff_time.isoformat(),
                    'cleanup_reason': 'age_based_cleanup'
                },
                severity='info'
            )
            
            old_results.delete()
            self.stdout.write(f'Deleted {result_count} old OCRResult records')
        
        if upload_count == 0 and result_count == 0:
            self.stdout.write('No old database records found')
    
    def _check_recent_processing(self, age_hours: int) -> int:
        """Check for recent OCR processing activity"""
        
        cutoff_time = timezone.now() - timedelta(hours=age_hours)
        
        # Count recent OCR results
        recent_results = OCRResult.objects.filter(
            created_at__gte=cutoff_time
        ).count()
        
        return recent_results
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"