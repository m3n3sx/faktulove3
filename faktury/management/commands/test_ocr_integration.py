"""
Management command to test OCR integration functionality with status synchronization

Usage:
    python manage.py test_ocr_integration --user-id 1
    python manage.py test_ocr_integration --create-test-data
    python manage.py test_ocr_integration --process-pending
    python manage.py test_ocr_integration --test-status-sync
    python manage.py test_ocr_integration --verify-status --document-id 123
"""

import json
import time
from decimal import Decimal
from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction, models
from django.utils import timezone

from faktury.models import DocumentUpload, OCRResult, Faktura, Firma
from faktury.services.ocr_integration import (
    process_ocr_result, create_faktura_from_ocr_manual, get_ocr_processing_stats
)
from faktury.services.status_sync_service import StatusSyncService, StatusSyncError


class Command(BaseCommand):
    help = 'Test OCR integration functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to test with'
        )
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test OCR data'
        )
        parser.add_argument(
            '--process-pending',
            action='store_true',
            help='Process all pending OCR results'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show OCR processing statistics'
        )
        parser.add_argument(
            '--ocr-result-id',
            type=int,
            help='Process specific OCR result ID'
        )
        parser.add_argument(
            '--test-status-sync',
            action='store_true',
            help='Test status synchronization functionality'
        )
        parser.add_argument(
            '--verify-status',
            action='store_true',
            help='Verify status consistency for documents'
        )
        parser.add_argument(
            '--document-id',
            type=int,
            help='Specific document ID to verify status for'
        )
        parser.add_argument(
            '--test-confidence-scenarios',
            action='store_true',
            help='Test various confidence scenarios and status transitions'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug output for detailed status information'
        )

    def handle(self, *args, **options):
        self.debug = options.get('debug', False)
        
        if options['create_test_data']:
            self.create_test_data()
        elif options['process_pending']:
            self.process_pending_results()
        elif options['stats']:
            self.show_statistics(options.get('user_id'))
        elif options['ocr_result_id']:
            self.process_specific_result(options['ocr_result_id'])
        elif options['test_status_sync']:
            self.test_status_synchronization()
        elif options['verify_status']:
            self.verify_status_consistency(options.get('document_id'))
        elif options['test_confidence_scenarios']:
            self.test_confidence_scenarios()
        else:
            self.show_help()

    def create_test_data(self):
        """Create test OCR data for testing"""
        self.stdout.write("Creating test OCR data...")
        
        # Find or create test user
        try:
            user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
            self.stdout.write(f"Created test user: {user.username}")
        
        # Find or create test company
        try:
            firma = user.firma
        except Firma.DoesNotExist:
            firma = Firma.objects.create(
                user=user,
                nazwa='Test Company OCR',
                nip='9876543210',
                ulica='Test Street',
                numer_domu='1',
                kod_pocztowy='00-000',
                miejscowosc='Test City'
            )
            self.stdout.write(f"Created test company: {firma.nazwa}")
        
        # Create test documents and OCR results
        test_cases = [
            {
                'filename': 'high_confidence_invoice.pdf',
                'confidence': 95.0,
                'invoice_number': 'FV/HIGH/001/2025'
            },
            {
                'filename': 'medium_confidence_invoice.pdf',
                'confidence': 85.0,
                'invoice_number': 'FV/MED/001/2025'
            },
            {
                'filename': 'low_confidence_invoice.pdf',
                'confidence': 70.0,
                'invoice_number': 'FV/LOW/001/2025'
            }
        ]
        
        for i, case in enumerate(test_cases):
            # Create document
            document = DocumentUpload.objects.create(
                user=user,
                original_filename=case['filename'],
                file_path=f'/tmp/{case["filename"]}',
                file_size=1024 * (i + 1),
                content_type='application/pdf',
                processing_status='completed'
            )
            
            # Create OCR data
            ocr_data = {
                'numer_faktury': case['invoice_number'],
                'data_wystawienia': '2025-01-15',
                'data_sprzedazy': '2025-01-15',
                'sprzedawca_nazwa': f'Supplier Company {i+1}',
                'sprzedawca_nip': f'123456789{i}',
                'sprzedawca_ulica': f'Supplier Street {i+1}',
                'sprzedawca_numer_domu': str(10 + i),
                'sprzedawca_kod_pocztowy': f'1{i}-{i}{i}{i}',
                'sprzedawca_miejscowosc': f'Supplier City {i+1}',
                'nabywca_nazwa': firma.nazwa,
                'pozycje': [
                    {
                        'nazwa': f'Test Product {i+1}',
                        'ilosc': str(i + 1),
                        'jednostka': 'szt',
                        'cena_netto': str(100.00 * (i + 1)),
                        'vat': '23'
                    }
                ],
                'suma_brutto': str(123.00 * (i + 1)),
                'sposob_platnosci': 'przelew',
                'termin_platnosci_dni': 14
            }
            
            # Create OCR result
            ocr_result = OCRResult.objects.create(
                document=document,
                raw_text=f'Raw OCR text for {case["filename"]}...',
                extracted_data=ocr_data,
                confidence_score=case['confidence'],
                processing_time=2.0 + i * 0.5,
                processing_status='pending'
            )
            
            self.stdout.write(
                f"Created OCR result {ocr_result.id}: {case['filename']} "
                f"(confidence: {case['confidence']}%)"
            )
        
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(test_cases)} test OCR results")
        )

    def process_pending_results(self):
        """Process all pending OCR results"""
        self.stdout.write("Processing pending OCR results...")
        
        pending_results = OCRResult.objects.filter(processing_status='pending')
        count = pending_results.count()
        
        if count == 0:
            self.stdout.write("No pending OCR results found")
            return
        
        self.stdout.write(f"Found {count} pending OCR results")
        
        processed = 0
        errors = 0
        
        for ocr_result in pending_results:
            try:
                self.stdout.write(f"Processing OCR result {ocr_result.id}...")
                
                faktura = process_ocr_result(ocr_result.id)
                
                if faktura:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Created Faktura {faktura.numer}"
                        )
                    )
                else:
                    ocr_result.refresh_from_db()
                    self.stdout.write(
                        self.style.WARNING(
                            f"  → Status: {ocr_result.get_processing_status_display()}"
                        )
                    )
                
                processed += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Error: {str(e)}")
                )
                errors += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {processed} OCR results ({errors} errors)"
            )
        )

    def process_specific_result(self, ocr_result_id):
        """Process specific OCR result with status verification"""
        try:
            ocr_result = OCRResult.objects.get(id=ocr_result_id)
        except OCRResult.DoesNotExist:
            raise CommandError(f"OCR result {ocr_result_id} not found")
        
        document = ocr_result.document
        
        self.stdout.write(f"Processing OCR result {ocr_result_id}...")
        self.stdout.write(f"  Document: {document.original_filename}")
        self.stdout.write(f"  Document ID: {document.id}")
        self.stdout.write(f"  Confidence: {ocr_result.confidence_score}%")
        self.stdout.write(f"  OCR Status: {ocr_result.get_processing_status_display()}")
        
        # Show status before processing
        self._debug_status(document, "Before processing")
        
        try:
            faktura = process_ocr_result(ocr_result_id)
            
            # Refresh from database
            document.refresh_from_db()
            ocr_result.refresh_from_db()
            
            # Show status after processing
            self._debug_status(document, "After processing")
            
            if faktura:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created Faktura {faktura.numer}")
                )
                self.stdout.write(f"  Faktura ID: {faktura.id}")
                self.stdout.write(f"  Sprzedawca: {faktura.sprzedawca.nazwa}")
                self.stdout.write(f"  Nabywca: {faktura.nabywca.nazwa}")
                self.stdout.write(f"  Positions: {faktura.pozycjafaktury_set.count()}")
                
                # Verify status synchronization
                sync_service = StatusSyncService()
                combined_status = sync_service.get_combined_status(document)
                self.stdout.write(f"  Combined Status: {combined_status}")
                
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"→ No Faktura created. Status: {ocr_result.get_processing_status_display()}"
                    )
                )
                if ocr_result.error_message:
                    self.stdout.write(f"  Error: {ocr_result.error_message}")
                
                # Show why no faktura was created
                if ocr_result.confidence_score < 90.0:
                    if ocr_result.processing_status == 'manual_review':
                        self.stdout.write(f"  → Low confidence ({ocr_result.confidence_score}%) requires manual review")
                    elif ocr_result.processing_status == 'completed':
                        self.stdout.write(f"  → Medium confidence ({ocr_result.confidence_score}%) completed without auto-creation")
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {str(e)}"))
            
            # Check if error was handled in status
            ocr_result.refresh_from_db()
            document.refresh_from_db()
            
            self._debug_status(document, "After error")
            
            if ocr_result.processing_status == 'failed':
                self.stdout.write("  → Error properly recorded in OCR result status")

    def show_statistics(self, user_id=None):
        """Show OCR processing statistics"""
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f"OCR Statistics for user: {user.username}")
                stats = get_ocr_processing_stats(user)
            except User.DoesNotExist:
                raise CommandError(f"User {user_id} not found")
        else:
            self.stdout.write("Global OCR Statistics")
            from django.db.models import Count, Avg
            from faktury.models import OCRResult
            
            stats = OCRResult.objects.aggregate(
                total_processed=Count('id'),
                avg_confidence=Avg('confidence_score'),
                auto_created_count=Count('id', filter=models.Q(auto_created_faktura=True)),
                manual_review_count=Count('id', filter=models.Q(processing_status='manual_review')),
                failed_count=Count('id', filter=models.Q(processing_status='failed')),
            )
            
            total = stats['total_processed'] or 0
            if total > 0:
                stats['success_rate'] = ((stats['auto_created_count'] or 0) / total) * 100
                stats['manual_review_rate'] = ((stats['manual_review_count'] or 0) / total) * 100
                stats['failure_rate'] = ((stats['failed_count'] or 0) / total) * 100
            else:
                stats['success_rate'] = 0
                stats['manual_review_rate'] = 0
                stats['failure_rate'] = 0
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"Total Processed: {stats['total_processed']}")
        self.stdout.write(f"Average Confidence: {stats['avg_confidence']:.1f}%" if stats['avg_confidence'] else "Average Confidence: N/A")
        self.stdout.write(f"Auto-created Faktury: {stats['auto_created_count']}")
        self.stdout.write(f"Manual Review Required: {stats['manual_review_count']}")
        self.stdout.write(f"Failed Processing: {stats['failed_count']}")
        self.stdout.write("\nRates:")
        self.stdout.write(f"  Success Rate: {stats['success_rate']:.1f}%")
        self.stdout.write(f"  Manual Review Rate: {stats['manual_review_rate']:.1f}%")
        self.stdout.write(f"  Failure Rate: {stats['failure_rate']:.1f}%")
        self.stdout.write("="*50)

    def test_status_synchronization(self):
        """Test status synchronization functionality"""
        self.stdout.write(self.style.SUCCESS("Testing Status Synchronization"))
        self.stdout.write("="*60)
        
        # Find or create test user and company
        user, firma = self._get_or_create_test_user()
        
        # Create test document
        document = DocumentUpload.objects.create(
            user=user,
            original_filename='status_sync_test.pdf',
            file_path='/tmp/status_sync_test.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        
        self.stdout.write(f"Created test document {document.id}")
        self._debug_status(document, "Initial state")
        
        # Test 1: Create OCR result and test sync
        self.stdout.write("\n1. Testing OCR result creation and sync...")
        ocr_result = OCRResult.objects.create(
            document=document,
            raw_text='Status sync test text...',
            extracted_data=self._get_test_ocr_data('FV/SYNC/001/2025'),
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='pending'
        )
        
        # Sync status
        sync_service = StatusSyncService()
        sync_result = sync_service.sync_document_status(document)
        
        document.refresh_from_db()
        self._debug_status(document, "After OCR result creation")
        self.stdout.write(f"  Sync result: {sync_result}")
        
        # Test 2: Mark OCR as processing
        self.stdout.write("\n2. Testing OCR processing status...")
        ocr_result.mark_processing_started()
        sync_service.sync_document_status(document)
        
        document.refresh_from_db()
        self._debug_status(document, "After marking as processing")
        
        # Test 3: Complete OCR processing
        self.stdout.write("\n3. Testing OCR completion...")
        ocr_result.mark_processing_completed()
        sync_service.sync_document_status(document)
        
        document.refresh_from_db()
        self._debug_status(document, "After OCR completion")
        
        # Test 4: Test unified status
        self.stdout.write("\n4. Testing unified status...")
        unified_status = document.get_unified_status()
        combined_status = sync_service.get_combined_status(document)
        
        self.stdout.write(f"  Unified status: {unified_status}")
        self.stdout.write(f"  Combined status: {combined_status}")
        
        # Test 5: Test error scenario
        self.stdout.write("\n5. Testing error scenario...")
        error_document = DocumentUpload.objects.create(
            user=user,
            original_filename='error_test.pdf',
            file_path='/tmp/error_test.pdf',
            file_size=512,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        
        error_ocr = OCRResult.objects.create(
            document=error_document,
            raw_text='Error test...',
            extracted_data={},  # Invalid data
            confidence_score=95.0,
            processing_time=1.0,
            processing_status='pending'
        )
        
        error_ocr.mark_processing_failed("Test error message")
        sync_service.sync_document_status(error_document)
        
        error_document.refresh_from_db()
        self._debug_status(error_document, "After error scenario")
        
        self.stdout.write(self.style.SUCCESS("\n✓ Status synchronization tests completed"))
    
    def verify_status_consistency(self, document_id=None):
        """Verify status consistency for documents"""
        self.stdout.write(self.style.SUCCESS("Verifying Status Consistency"))
        self.stdout.write("="*60)
        
        if document_id:
            try:
                documents = [DocumentUpload.objects.get(id=document_id)]
                self.stdout.write(f"Checking document {document_id}")
            except DocumentUpload.DoesNotExist:
                raise CommandError(f"Document {document_id} not found")
        else:
            documents = DocumentUpload.objects.all()[:10]  # Limit to 10 for testing
            self.stdout.write(f"Checking {documents.count()} documents")
        
        sync_service = StatusSyncService()
        inconsistencies = 0
        
        for document in documents:
            self.stdout.write(f"\nDocument {document.id}: {document.original_filename}")
            
            # Get current statuses
            doc_status = document.processing_status
            unified_status = document.get_unified_status()
            
            # Check if there's an OCR result
            try:
                ocr_result = document.ocrresult
                ocr_status = ocr_result.processing_status
                
                self.stdout.write(f"  Document status: {doc_status}")
                self.stdout.write(f"  OCR status: {ocr_status}")
                self.stdout.write(f"  Unified status: {unified_status}")
                
                # Check for inconsistencies by comparing with expected document status
                expected_doc_status = sync_service.OCR_TO_DOCUMENT_STATUS_MAP.get(ocr_status)
                
                if isinstance(unified_status, dict):
                    unified_status_value = unified_status.get('status')
                else:
                    unified_status_value = unified_status
                
                # Check if document status matches expected status from OCR
                if expected_doc_status and doc_status != expected_doc_status:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Document status inconsistency! Expected: {expected_doc_status}, Got: {doc_status}"
                        )
                    )
                    inconsistencies += 1
                    
                    # Try to fix
                    self.stdout.write("  Attempting to sync...")
                    sync_result = sync_service.sync_document_status(document)
                    document.refresh_from_db()
                    
                    if sync_result:
                        self.stdout.write(self.style.SUCCESS("  ✓ Fixed"))
                    else:
                        self.stdout.write(self.style.WARNING("  → No changes made"))
                else:
                    self.stdout.write(self.style.SUCCESS("  ✓ Consistent"))
                    
            except OCRResult.DoesNotExist:
                self.stdout.write(f"  Document status: {doc_status}")
                self.stdout.write(f"  OCR status: None")
                self.stdout.write(f"  Unified status: {unified_status}")
                self.stdout.write(self.style.SUCCESS("  ✓ No OCR result (consistent)"))
        
        if inconsistencies == 0:
            self.stdout.write(self.style.SUCCESS(f"\n✓ All documents are consistent"))
        else:
            self.stdout.write(
                self.style.WARNING(f"\n⚠ Found {inconsistencies} inconsistencies")
            )
    
    def test_confidence_scenarios(self):
        """Test various confidence scenarios and status transitions"""
        self.stdout.write(self.style.SUCCESS("Testing Confidence Scenarios"))
        self.stdout.write("="*60)
        
        user, firma = self._get_or_create_test_user()
        
        confidence_scenarios = [
            {'confidence': 98.0, 'expected_auto_create': True, 'description': 'Very High Confidence'},
            {'confidence': 92.0, 'expected_auto_create': True, 'description': 'High Confidence'},
            {'confidence': 85.0, 'expected_auto_create': False, 'description': 'Medium Confidence'},
            {'confidence': 75.0, 'expected_auto_create': False, 'description': 'Low-Medium Confidence'},
            {'confidence': 65.0, 'expected_auto_create': False, 'description': 'Low Confidence'},
            {'confidence': 45.0, 'expected_auto_create': False, 'description': 'Very Low Confidence'},
        ]
        
        for i, scenario in enumerate(confidence_scenarios):
            self.stdout.write(f"\n{i+1}. Testing {scenario['description']} ({scenario['confidence']}%)")
            
            # Create document
            document = DocumentUpload.objects.create(
                user=user,
                original_filename=f'confidence_test_{i+1}.pdf',
                file_path=f'/tmp/confidence_test_{i+1}.pdf',
                file_size=1024,
                content_type='application/pdf',
                processing_status='uploaded'
            )
            
            # Create OCR result
            ocr_result = OCRResult.objects.create(
                document=document,
                raw_text=f'Confidence test {i+1}...',
                extracted_data=self._get_test_ocr_data(f'FV/CONF/{i+1:03d}/2025'),
                confidence_score=scenario['confidence'],
                processing_time=1.5,
                processing_status='pending'
            )
            
            self._debug_status(document, "Before processing")
            
            # Process the OCR result
            try:
                faktura = process_ocr_result(ocr_result.id)
                
                # Refresh from database
                document.refresh_from_db()
                ocr_result.refresh_from_db()
                
                self._debug_status(document, "After processing")
                
                # Verify expectations
                if scenario['expected_auto_create']:
                    if faktura:
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Faktura auto-created as expected: {faktura.numer}"))
                        self.stdout.write(f"    OCR confidence: {ocr_result.confidence_score}%")
                        self.stdout.write(f"    Processing status: {ocr_result.processing_status}")
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  ✗ Expected auto-creation but no Faktura created")
                        )
                else:
                    if faktura:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠ Unexpected auto-creation: {faktura.numer}")
                        )
                    else:
                        self.stdout.write(self.style.SUCCESS(f"  ✓ No auto-creation as expected"))
                        self.stdout.write(f"    Processing status: {ocr_result.processing_status}")
                        
                        if ocr_result.processing_status == 'manual_review':
                            self.stdout.write(f"    → Requires manual review (correct for {scenario['confidence']}%)")
                        elif ocr_result.processing_status == 'completed':
                            self.stdout.write(f"    → Completed without auto-creation (correct for {scenario['confidence']}%)")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Processing error: {str(e)}"))
                
                # Check if error was handled properly
                ocr_result.refresh_from_db()
                if ocr_result.processing_status == 'failed':
                    self.stdout.write(f"    → Marked as failed (error handled)")
                    self.stdout.write(f"    → Error message: {ocr_result.error_message}")
        
        self.stdout.write(self.style.SUCCESS("\n✓ Confidence scenario tests completed"))
    
    def _get_or_create_test_user(self):
        """Get or create test user and company"""
        try:
            user = User.objects.get(username='testuser_status')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='testuser_status',
                email='status@example.com',
                password='testpass123'
            )
        
        try:
            firma = user.firma
        except Firma.DoesNotExist:
            # Use a unique NIP for status testing
            import random
            unique_nip = f"987654321{random.randint(0, 9)}"
            
            # Check if NIP already exists and generate a new one if needed
            while Firma.objects.filter(nip=unique_nip).exists():
                unique_nip = f"987654321{random.randint(0, 9)}"
            
            firma = Firma.objects.create(
                user=user,
                nazwa='Status Test Company',
                nip=unique_nip,
                ulica='Status Test Street',
                numer_domu='1',
                kod_pocztowy='00-000',
                miejscowosc='Status Test City'
            )
        
        return user, firma
    
    def _get_test_ocr_data(self, invoice_number):
        """Get test OCR data"""
        return {
            'numer_faktury': invoice_number,
            'data_wystawienia': '2025-01-15',
            'data_sprzedazy': '2025-01-15',
            'sprzedawca_nazwa': 'Test Supplier Company',
            'sprzedawca_nip': '1234567890',
            'sprzedawca_ulica': 'Supplier Street',
            'sprzedawca_numer_domu': '10',
            'sprzedawca_kod_pocztowy': '11-111',
            'sprzedawca_miejscowosc': 'Supplier City',
            'nabywca_nazwa': 'Status Test Company',
            'pozycje': [
                {
                    'nazwa': 'Test Product',
                    'ilosc': '1.00',
                    'jednostka': 'szt',
                    'cena_netto': '100.00',
                    'vat': '23'
                }
            ],
            'suma_brutto': '123.00',
            'sposob_platnosci': 'przelew',
            'termin_platnosci_dni': 14
        }
    
    def _debug_status(self, document, context=""):
        """Debug status information"""
        if not self.debug and context != "Initial state":
            return
            
        try:
            ocr_result = document.ocrresult
            ocr_status = ocr_result.processing_status
            ocr_confidence = ocr_result.confidence_score
        except OCRResult.DoesNotExist:
            ocr_status = "None"
            ocr_confidence = "N/A"
        
        unified_status = document.get_unified_status()
        
        self.stdout.write(f"  Status Debug ({context}):")
        self.stdout.write(f"    Document status: {document.processing_status}")
        self.stdout.write(f"    OCR status: {ocr_status}")
        self.stdout.write(f"    OCR confidence: {ocr_confidence}")
        self.stdout.write(f"    Unified status: {unified_status}")
        self.stdout.write(f"    Timestamp: {timezone.now().strftime('%H:%M:%S')}")

    def show_help(self):
        """Show usage help"""
        self.stdout.write("OCR Integration Test Command with Status Synchronization")
        self.stdout.write("\nUsage examples:")
        self.stdout.write("  python manage.py test_ocr_integration --create-test-data")
        self.stdout.write("  python manage.py test_ocr_integration --process-pending")
        self.stdout.write("  python manage.py test_ocr_integration --stats")
        self.stdout.write("  python manage.py test_ocr_integration --stats --user-id 1")
        self.stdout.write("  python manage.py test_ocr_integration --ocr-result-id 123")
        self.stdout.write("  python manage.py test_ocr_integration --test-status-sync --debug")
        self.stdout.write("  python manage.py test_ocr_integration --verify-status")
        self.stdout.write("  python manage.py test_ocr_integration --verify-status --document-id 123")
        self.stdout.write("  python manage.py test_ocr_integration --test-confidence-scenarios")
        self.stdout.write("\nOptions:")
        self.stdout.write("  --create-test-data           Create test OCR data")
        self.stdout.write("  --process-pending            Process all pending OCR results")
        self.stdout.write("  --stats                      Show processing statistics")
        self.stdout.write("  --user-id ID                 Specify user ID for stats")
        self.stdout.write("  --ocr-result-id ID           Process specific OCR result")
        self.stdout.write("  --test-status-sync           Test status synchronization functionality")
        self.stdout.write("  --verify-status              Verify status consistency")
        self.stdout.write("  --document-id ID             Specific document ID to verify")
        self.stdout.write("  --test-confidence-scenarios  Test various confidence scenarios")
        self.stdout.write("  --debug                      Enable debug output")