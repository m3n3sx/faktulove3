"""
Management command to display OCR processing statistics.
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Min, Max, Q
from django.utils import timezone
from datetime import timedelta
import json

from faktury.models import DocumentUpload, OCRResult, OCRValidation, OCRProcessingLog


class Command(BaseCommand):
    help = 'Display OCR processing statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Show statistics for the last N days (default: 30)'
        )
        
        parser.add_argument(
            '--format',
            choices=['table', 'json'],
            default='table',
            help='Output format (default: table)'
        )
        
        parser.add_argument(
            '--user',
            type=str,
            help='Show statistics for specific user (username)'
        )

    def handle(self, *args, **options):
        days = options['days']
        output_format = options['format']
        username = options['user']
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base querysets
        documents_qs = DocumentUpload.objects.filter(
            upload_timestamp__gte=start_date
        )
        results_qs = OCRResult.objects.filter(
            created_at__gte=start_date
        )
        validations_qs = OCRValidation.objects.filter(
            validation_timestamp__gte=start_date
        )
        
        # Filter by user if specified
        if username:
            documents_qs = documents_qs.filter(user__username=username)
            results_qs = results_qs.filter(document__user__username=username)
            validations_qs = validations_qs.filter(validated_by__username=username)
        
        # Collect statistics
        stats = self._collect_statistics(
            documents_qs, results_qs, validations_qs, start_date, end_date
        )
        
        # Output results
        if output_format == 'json':
            self._output_json(stats)
        else:
            self._output_table(stats, days, username)

    def _collect_statistics(self, documents_qs, results_qs, validations_qs, start_date, end_date):
        """Collect comprehensive OCR statistics"""
        
        # Document statistics
        total_documents = documents_qs.count()
        
        document_stats = documents_qs.aggregate(
            completed=Count('id', filter=Q(processing_status='completed')),
            failed=Count('id', filter=Q(processing_status='failed')),
            processing=Count('id', filter=Q(processing_status='processing')),
            uploaded=Count('id', filter=Q(processing_status='uploaded')),
        )
        
        # OCR results statistics
        total_results = results_qs.count()
        
        if total_results > 0:
            results_stats = results_qs.aggregate(
                avg_confidence=Avg('confidence_score'),
                min_confidence=Min('confidence_score'),
                max_confidence=Max('confidence_score'),
                avg_processing_time=Avg('processing_time'),
                min_processing_time=Min('processing_time'),
                max_processing_time=Max('processing_time'),
                high_confidence=Count('id', filter=Q(confidence_score__gte=95)),
                medium_confidence=Count('id', filter=Q(confidence_score__gte=80, confidence_score__lt=95)),
                low_confidence=Count('id', filter=Q(confidence_score__lt=80)),
                with_invoice=Count('id', filter=Q(faktura__isnull=False)),
            )
        else:
            results_stats = {
                'avg_confidence': 0,
                'min_confidence': 0,
                'max_confidence': 0,
                'avg_processing_time': 0,
                'min_processing_time': 0,
                'max_processing_time': 0,
                'high_confidence': 0,
                'medium_confidence': 0,
                'low_confidence': 0,
                'with_invoice': 0,
            }
        
        # Validation statistics
        total_validations = validations_qs.count()
        
        if total_validations > 0:
            validation_stats = validations_qs.aggregate(
                avg_accuracy=Avg('accuracy_rating'),
                min_accuracy=Min('accuracy_rating'),
                max_accuracy=Max('accuracy_rating'),
                avg_time_spent=Avg('time_spent_minutes'),
                total_corrections=Count('id', filter=Q(corrections_made__isnull=False)),
            )
        else:
            validation_stats = {
                'avg_accuracy': 0,
                'min_accuracy': 0,
                'max_accuracy': 0,
                'avg_time_spent': 0,
                'total_corrections': 0,
            }
        
        # User statistics
        user_stats = documents_qs.values('user__username').annotate(
            document_count=Count('id'),
            completed_count=Count('id', filter=Q(processing_status='completed')),
        ).order_by('-document_count')[:10]
        
        # Daily statistics
        daily_stats = documents_qs.extra(
            select={'day': 'date(upload_timestamp)'}
        ).values('day').annotate(
            uploads=Count('id'),
            completed=Count('id', filter=Q(processing_status='completed')),
        ).order_by('day')
        
        # Error statistics
        error_logs = OCRProcessingLog.objects.filter(
            timestamp__gte=start_date,
            level__in=['ERROR', 'CRITICAL']
        )
        
        error_stats = {
            'total_errors': error_logs.count(),
            'error_types': list(error_logs.values('message').annotate(
                count=Count('id')
            ).order_by('-count')[:5])
        }
        
        return {
            'period': {
                'start_date': start_date.date(),
                'end_date': end_date.date(),
                'days': (end_date - start_date).days,
            },
            'documents': {
                'total': total_documents,
                **document_stats,
            },
            'results': {
                'total': total_results,
                **results_stats,
            },
            'validations': {
                'total': total_validations,
                **validation_stats,
            },
            'users': list(user_stats),
            'daily': list(daily_stats),
            'errors': error_stats,
        }

    def _output_table(self, stats, days, username):
        """Output statistics in table format"""
        
        self.stdout.write(
            self.style.SUCCESS(f'\n=== OCR Statistics Report ===')
        )
        
        # Period info
        period = stats['period']
        self.stdout.write(f'Period: {period["start_date"]} to {period["end_date"]} ({days} days)')
        if username:
            self.stdout.write(f'User: {username}')
        
        # Document statistics
        docs = stats['documents']
        self.stdout.write(f'\n📄 DOCUMENT PROCESSING:')
        self.stdout.write(f'  Total uploaded: {docs["total"]}')
        self.stdout.write(f'  Completed: {docs["completed"]} ({self._percentage(docs["completed"], docs["total"])}%)')
        self.stdout.write(f'  Failed: {docs["failed"]} ({self._percentage(docs["failed"], docs["total"])}%)')
        self.stdout.write(f'  Currently processing: {docs["processing"]}')
        self.stdout.write(f'  Waiting in queue: {docs["uploaded"]}')
        
        # OCR results
        results = stats['results']
        if results['total'] > 0:
            self.stdout.write(f'\n🤖 OCR ACCURACY:')
            self.stdout.write(f'  Total processed: {results["total"]}')
            self.stdout.write(f'  Average confidence: {results["avg_confidence"]:.1f}%')
            self.stdout.write(f'  Confidence range: {results["min_confidence"]:.1f}% - {results["max_confidence"]:.1f}%')
            self.stdout.write(f'  High confidence (95%+): {results["high_confidence"]} ({self._percentage(results["high_confidence"], results["total"])}%)')
            self.stdout.write(f'  Medium confidence (80-95%): {results["medium_confidence"]} ({self._percentage(results["medium_confidence"], results["total"])}%)')
            self.stdout.write(f'  Low confidence (<80%): {results["low_confidence"]} ({self._percentage(results["low_confidence"], results["total"])}%)')
            self.stdout.write(f'  Auto-created invoices: {results["with_invoice"]} ({self._percentage(results["with_invoice"], results["total"])}%)')
            
            self.stdout.write(f'\n⏱️ PROCESSING PERFORMANCE:')
            self.stdout.write(f'  Average processing time: {results["avg_processing_time"]:.1f}s')
            self.stdout.write(f'  Processing time range: {results["min_processing_time"]:.1f}s - {results["max_processing_time"]:.1f}s')
        
        # Validation statistics
        validations = stats['validations']
        if validations['total'] > 0:
            self.stdout.write(f'\n✅ HUMAN VALIDATION:')
            self.stdout.write(f'  Total validations: {validations["total"]}')
            self.stdout.write(f'  Average accuracy rating: {validations["avg_accuracy"]:.1f}/10')
            self.stdout.write(f'  Rating range: {validations["min_accuracy"]}/10 - {validations["max_accuracy"]}/10')
            if validations['avg_time_spent']:
                self.stdout.write(f'  Average validation time: {validations["avg_time_spent"]:.1f} minutes')
            self.stdout.write(f'  Documents with corrections: {validations["total_corrections"]}')
        
        # Top users
        if stats['users']:
            self.stdout.write(f'\n👥 TOP USERS:')
            for i, user in enumerate(stats['users'][:5], 1):
                self.stdout.write(
                    f'  {i}. {user["user__username"]}: {user["document_count"]} documents '
                    f'({user["completed_count"]} completed)'
                )
        
        # Errors
        errors = stats['errors']
        if errors['total_errors'] > 0:
            self.stdout.write(f'\n❌ ERRORS:')
            self.stdout.write(f'  Total errors: {errors["total_errors"]}')
            if errors['error_types']:
                self.stdout.write('  Most common error types:')
                for error in errors['error_types'][:3]:
                    self.stdout.write(f'    - {error["message"][:50]}... ({error["count"]} times)')
        
        # Daily trend (last 7 days)
        if stats['daily']:
            recent_days = stats['daily'][-7:]
            self.stdout.write(f'\n📊 DAILY TREND (Last 7 days):')
            for day in recent_days:
                success_rate = self._percentage(day['completed'], day['uploads']) if day['uploads'] > 0 else 0
                self.stdout.write(f'  {day["day"]}: {day["uploads"]} uploads, {day["completed"]} completed ({success_rate}%)')

    def _output_json(self, stats):
        """Output statistics in JSON format"""
        # Convert dates to strings for JSON serialization
        stats['period']['start_date'] = stats['period']['start_date'].isoformat()
        stats['period']['end_date'] = stats['period']['end_date'].isoformat()
        
        for daily in stats['daily']:
            if 'day' in daily and daily['day']:
                daily['day'] = str(daily['day'])
        
        self.stdout.write(json.dumps(stats, indent=2, default=str))

    def _percentage(self, part, total):
        """Calculate percentage safely"""
        if total == 0:
            return 0
        return round((part / total) * 100, 1)