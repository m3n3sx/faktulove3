"""
Management command to clean up old OCR documents and processing logs.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

from faktury.models import DocumentUpload, OCRResult, OCRProcessingLog
from faktury.services.file_upload_service import FileUploadService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up old OCR documents and processing logs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete documents older than this many days (default: 30)'
        )
        
        parser.add_argument(
            '--logs-days',
            type=int,
            default=90,
            help='Delete processing logs older than this many days (default: 90)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation'
        )

    def handle(self, *args, **options):
        days = options['days']
        logs_days = options['logs_days']
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting OCR cleanup process...')
        )
        
        # Calculate cutoff dates
        documents_cutoff = timezone.now() - timedelta(days=days)
        logs_cutoff = timezone.now() - timedelta(days=logs_days)
        
        self.stdout.write(f'Documents cutoff date: {documents_cutoff.date()}')
        self.stdout.write(f'Logs cutoff date: {logs_cutoff.date()}')
        
        # Find documents to clean up
        old_documents = DocumentUpload.objects.filter(
            processing_completed_at__lt=documents_cutoff,
            processing_status__in=['completed', 'failed']
        ).select_related('user')
        
        # Find logs to clean up
        old_logs = OCRProcessingLog.objects.filter(
            timestamp__lt=logs_cutoff
        )
        
        documents_count = old_documents.count()
        logs_count = old_logs.count()
        
        self.stdout.write(f'Found {documents_count} old documents to clean up')
        self.stdout.write(f'Found {logs_count} old processing logs to clean up')
        
        if documents_count == 0 and logs_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No old data found. Nothing to clean up.')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No actual deletion will occur')
            )
            self._show_cleanup_details(old_documents, old_logs)
            return
        
        # Confirm deletion
        if not force:
            confirm = input(
                f'Are you sure you want to delete {documents_count} documents '
                f'and {logs_count} logs? [y/N]: '
            )
            if confirm.lower() != 'y':
                self.stdout.write('Cleanup cancelled.')
                return
        
        # Perform cleanup
        with transaction.atomic():
            self._cleanup_documents(old_documents)
            self._cleanup_logs(old_logs)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cleanup completed successfully! '
                f'Removed {documents_count} documents and {logs_count} logs.'
            )
        )

    def _show_cleanup_details(self, documents, logs):
        """Show details of what would be cleaned up"""
        
        if documents.exists():
            self.stdout.write('\nDocuments to be deleted:')
            for doc in documents[:10]:  # Show first 10
                self.stdout.write(
                    f'  - {doc.original_filename} '
                    f'(user: {doc.user.username}, '
                    f'completed: {doc.processing_completed_at.date()})'
                )
            
            if documents.count() > 10:
                self.stdout.write(f'  ... and {documents.count() - 10} more')
        
        if logs.exists():
            self.stdout.write('\nProcessing logs to be deleted:')
            log_summary = logs.values('level').annotate(
                count=models.Count('id')
            ).order_by('level')
            
            for summary in log_summary:
                self.stdout.write(
                    f'  - {summary["level"]}: {summary["count"]} entries'
                )

    def _cleanup_documents(self, documents):
        """Clean up documents and their files"""
        file_service = FileUploadService()
        cleaned_files = 0
        cleaned_db = 0
        
        for document in documents:
            try:
                # Clean up physical files
                file_service.cleanup_file(document)
                cleaned_files += 1
                
                # Delete database records (OCR results will cascade)
                document.delete()
                cleaned_db += 1
                
            except Exception as e:
                logger.error(f'Failed to cleanup document {document.id}: {e}')
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to cleanup document {document.original_filename}: {e}'
                    )
                )
        
        self.stdout.write(f'Cleaned up {cleaned_files} files and {cleaned_db} database records')

    def _cleanup_logs(self, logs):
        """Clean up processing logs"""
        deleted_count = logs.delete()[0]
        self.stdout.write(f'Deleted {deleted_count} processing log entries')


# Import models at module level for aggregation
from django.db import models