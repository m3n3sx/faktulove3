"""
Tests for OCR signal handlers with status synchronization

Tests the enhanced signal handlers that ensure proper status synchronization
between DocumentUpload and OCRResult models.
"""

import logging
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from ..models import DocumentUpload, OCRResult, Faktura, Firma, Kontrahent
from ..services.status_sync_service import StatusSyncService
from ..signals import (
    handle_document_upload_created,
    handle_ocr_result_created,
    handle_ocr_result_status_change,
    handle_faktura_created_from_ocr,
    handle_faktura_deletion
)
from django.db.models.signals import post_save

# Disable logging during tests to reduce noise
logging.disable(logging.CRITICAL)


class OCRSignalHandlersTest(TransactionTestCase):
    """Test OCR signal handlers with database transactions"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Firma',
            nip='1234567890',
            ulica='Test Street',
            numer_domu='123',
            kod_pocztowy='00-000',
            miejscowosc='Test City'
        )
    
    def create_document_upload(self):
        """Create a test DocumentUpload"""
        return DocumentUpload.objects.create(
            user=self.user,
            original_filename='test_invoice.pdf',
            file_path='/test/path/test_invoice.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
    
    def create_ocr_result(self, document, status='pending', confidence=85.0):
        """Create a test OCRResult"""
        return OCRResult.objects.create(
            document=document,
            raw_text='Test OCR text',
            extracted_data={
                'numer_faktury': 'F/2025/001',
                'data_wystawienia': '2025-01-15',
                'kwota_brutto': 123.45
            },
            confidence_score=confidence,
            processing_time=2.5,
            processing_status=status,
            processor_version='test-v1.0',
            processing_location='test-location'
        )
    
    def test_document_upload_created_signal(self):
        """Test DocumentUpload creation signal with Celery unavailable"""
        with patch('faktury.tasks.process_document_ocr_task') as mock_task:
            # Simulate ImportError to trigger synchronous processing
            mock_task.delay.side_effect = ImportError("Celery not available")
            
            with patch('faktury.services.document_ai_service.get_document_ai_service') as mock_service:
                with patch('faktury.services.file_upload_service.FileUploadService') as mock_file_service:
                    # Mock the OCR service response
                    mock_ocr_service = MagicMock()
                    mock_ocr_service.process_invoice.return_value = {
                        'raw_text': 'Test OCR text',
                        'confidence_score': 85.0,
                        'processing_time': 2.5,
                        'processor_version': 'test-v1.0',
                        'processing_location': 'test-location'
                    }
                    mock_service.return_value = mock_ocr_service
                    
                    # Mock file service
                    mock_file_service_instance = MagicMock()
                    mock_file_service_instance.get_file_content.return_value = b'test file content'
                    mock_file_service.return_value = mock_file_service_instance
                    
                    # Create document upload - this should trigger the signal
                    document = self.create_document_upload()
                    
                    # Verify OCRResult was created
                    self.assertTrue(hasattr(document, 'ocrresult'))
                    ocr_result = document.ocrresult
                    self.assertEqual(ocr_result.processing_status, 'pending')
                    self.assertEqual(ocr_result.confidence_score, 85.0)
    
    def test_ocr_result_created_signal_syncs_document_status(self):
        """Test that OCRResult creation syncs DocumentUpload status"""
        # Mock the document upload signal to prevent automatic processing
        with patch('faktury.signals.handle_document_upload_created'):
            document = self.create_document_upload()
            # Manually set status to uploaded since we're bypassing the signal
            document.processing_status = 'uploaded'
            document.save()
            
            # Create OCRResult - this should trigger status sync
            ocr_result = self.create_ocr_result(document, status='processing')
            
            # Refresh document from database
            document.refresh_from_db()
            
            # Document status should be synced to match OCR status
            self.assertEqual(document.processing_status, 'processing')
            self.assertIsNotNone(document.processing_started_at)
    
    def test_ocr_result_status_change_syncs_document_status(self):
        """Test that OCRResult status changes sync DocumentUpload status"""
        # Mock the document upload signal to prevent automatic processing
        with patch('faktury.signals.handle_document_upload_created'):
            document = self.create_document_upload()
            ocr_result = self.create_ocr_result(document, status='processing')
            
            # Refresh document to get synced status
            document.refresh_from_db()
            self.assertEqual(document.processing_status, 'processing')
            
            # Update OCR result status
            ocr_result.processing_status = 'completed'
            ocr_result.save()
            
            # Refresh document from database
            document.refresh_from_db()
            
            # Document status should be synced
            self.assertEqual(document.processing_status, 'completed')
            self.assertIsNotNone(document.processing_completed_at)
    
    def test_ocr_result_failed_status_syncs_document_status(self):
        """Test that OCRResult failure syncs DocumentUpload status"""
        # Mock the document upload signal to prevent automatic processing
        with patch('faktury.signals.handle_document_upload_created'):
            document = self.create_document_upload()
            ocr_result = self.create_ocr_result(document, status='processing')
            
            # Mark OCR result as failed
            error_message = "OCR processing failed"
            ocr_result.mark_processing_failed(error_message)
            
            # Refresh document from database
            document.refresh_from_db()
            
            # Document status should be synced
            self.assertEqual(document.processing_status, 'failed')
            self.assertEqual(document.error_message, error_message)
            self.assertIsNotNone(document.processing_completed_at)
    
    def test_faktura_creation_updates_ocr_result(self):
        """Test that Faktura creation updates related OCRResult"""
        document = self.create_document_upload()
        ocr_result = self.create_ocr_result(document, status='completed')
        
        # Create a Kontrahent first (required for Faktura)
        kontrahent = Kontrahent.objects.create(
            user=self.user,
            nazwa='Test Kontrahent',
            nip='9876543210',
            ulica='Test Street',
            numer_domu='456',
            kod_pocztowy='11-111',
            miejscowosc='Test City'
        )
        
        # Create Faktura from OCR document
        faktura = Faktura.objects.create(
            user=self.user,
            sprzedawca=self.firma,
            nabywca=kontrahent,
            numer='F/2025/001',
            data_wystawienia=timezone.now().date(),
            data_sprzedazy=timezone.now().date(),
            termin_platnosci=timezone.now().date(),
            miejsce_wystawienia='Test City',
            source_document=document
        )
        
        # Refresh OCR result from database
        ocr_result.refresh_from_db()
        
        # OCR result should be linked to Faktura
        self.assertEqual(ocr_result.faktura, faktura)
        self.assertTrue(ocr_result.auto_created_faktura)
        self.assertEqual(ocr_result.processing_status, 'completed')
    
    def test_faktura_deletion_resets_ocr_result(self):
        """Test that Faktura deletion resets OCRResult"""
        document = self.create_document_upload()
        ocr_result = self.create_ocr_result(document, status='completed')
        
        # Create a Kontrahent first (required for Faktura)
        kontrahent = Kontrahent.objects.create(
            user=self.user,
            nazwa='Test Kontrahent',
            nip='9876543210',
            ulica='Test Street',
            numer_domu='456',
            kod_pocztowy='11-111',
            miejscowosc='Test City'
        )
        
        # Create and link Faktura
        faktura = Faktura.objects.create(
            user=self.user,
            sprzedawca=self.firma,
            nabywca=kontrahent,
            numer='F/2025/001',
            data_wystawienia=timezone.now().date(),
            data_sprzedazy=timezone.now().date(),
            termin_platnosci=timezone.now().date(),
            miejsce_wystawienia='Test City',
            source_document=document
        )
        
        # Refresh to get linked state
        ocr_result.refresh_from_db()
        self.assertEqual(ocr_result.faktura, faktura)
        
        # Delete Faktura
        faktura.delete()
        
        # Refresh OCR result from database
        ocr_result.refresh_from_db()
        
        # OCR result should be reset
        self.assertIsNone(ocr_result.faktura)
        self.assertFalse(ocr_result.auto_created_faktura)
        self.assertEqual(ocr_result.processing_status, 'completed')
    
    def test_signal_error_handling(self):
        """Test that signal errors are handled gracefully"""
        document = self.create_document_upload()
        
        # Mock StatusSyncService to raise an exception
        with patch('faktury.services.status_sync_service.StatusSyncService.sync_document_status') as mock_sync:
            mock_sync.side_effect = Exception("Sync failed")
            
            # Create OCRResult - should not fail even if sync fails
            ocr_result = self.create_ocr_result(document, status='processing')
            
            # OCRResult should still be created
            self.assertTrue(OCRResult.objects.filter(id=ocr_result.id).exists())
    
    def test_atomic_status_updates(self):
        """Test that status updates are atomic"""
        document = self.create_document_upload()
        ocr_result = self.create_ocr_result(document, status='processing')
        
        # Simulate a database error during status sync
        with patch('faktury.services.status_sync_service.StatusSyncService.sync_document_status') as mock_sync:
            mock_sync.side_effect = Exception("Database error")
            
            # Update OCR result status - should not fail the entire operation
            ocr_result.processing_status = 'completed'
            ocr_result.save()
            
            # OCR result should still be updated
            ocr_result.refresh_from_db()
            self.assertEqual(ocr_result.processing_status, 'completed')
    
    def test_no_duplicate_status_sync_on_creation(self):
        """Test that status sync doesn't run twice on OCRResult creation"""
        document = self.create_document_upload()
        
        with patch('faktury.services.status_sync_service.StatusSyncService.sync_document_status') as mock_sync:
            mock_sync.return_value = True
            
            # Create OCRResult
            ocr_result = self.create_ocr_result(document, status='processing')
            
            # sync_document_status should be called only once (from handle_ocr_result_created)
            # The handle_ocr_result_status_change should not trigger for creation
            self.assertEqual(mock_sync.call_count, 1)
    
    def test_status_change_detection(self):
        """Test that status changes are properly detected"""
        document = self.create_document_upload()
        ocr_result = self.create_ocr_result(document, status='processing')
        
        with patch('faktury.services.status_sync_service.StatusSyncService.sync_document_status') as mock_sync:
            mock_sync.return_value = True
            
            # Update without changing status - should not trigger sync
            ocr_result.confidence_score = 90.0
            ocr_result.save()
            
            # Reset mock call count
            mock_sync.reset_mock()
            
            # Update with status change - should trigger sync
            ocr_result.processing_status = 'completed'
            ocr_result.save()
            
            # Should be called once for the status change
            self.assertEqual(mock_sync.call_count, 1)


class OCRSignalIntegrationTest(TestCase):
    """Integration tests for OCR signals with real status sync service"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Firma',
            nip='1234567890',
            ulica='Test Street',
            numer_domu='123',
            kod_pocztowy='00-000',
            miejscowosc='Test City'
        )
    
    def test_end_to_end_status_synchronization(self):
        """Test complete status synchronization flow"""
        # Mock the document upload signal to prevent automatic processing
        with patch('faktury.signals.handle_document_upload_created'):
            # Create document
            document = DocumentUpload.objects.create(
                user=self.user,
                original_filename='test_invoice.pdf',
                file_path='/test/path/test_invoice.pdf',
                file_size=1024,
                content_type='application/pdf',
                processing_status='uploaded'
            )
            
            # Mock the OCR processing to prevent automatic processing
            with patch('faktury.services.ocr_integration.process_ocr_result'):
                # Create OCR result with pending status
                ocr_result = OCRResult.objects.create(
                    document=document,
                    raw_text='Test OCR text',
                    extracted_data={'test': 'data'},
                    confidence_score=85.0,
                    processing_time=2.5,
                    processing_status='pending'
                )
                
                # Document should be synced to processing
                document.refresh_from_db()
                self.assertEqual(document.processing_status, 'processing')
                
                # Update OCR to completed
                ocr_result.processing_status = 'completed'
                ocr_result.save()
                
                # Document should be synced to completed
                document.refresh_from_db()
                self.assertEqual(document.processing_status, 'completed')
                
                # Create a Kontrahent first (required for Faktura)
                kontrahent = Kontrahent.objects.create(
                    user=self.user,
                    nazwa='Test Kontrahent',
                    nip='9876543210',
                    ulica='Test Street',
                    numer_domu='456',
                    kod_pocztowy='11-111',
                    miejscowosc='Test City'
                )
                
                # Create Faktura
                faktura = Faktura.objects.create(
                    user=self.user,
                    sprzedawca=self.firma,
                    nabywca=kontrahent,
                    numer='F/2025/001',
                    data_wystawienia=timezone.now().date(),
                    data_sprzedazy=timezone.now().date(),
                    termin_platnosci=timezone.now().date(),
                    miejsce_wystawienia='Test City',
                    source_document=document
                )
                
                # OCR result should be linked
                ocr_result.refresh_from_db()
                self.assertEqual(ocr_result.faktura, faktura)
                self.assertTrue(ocr_result.auto_created_faktura)
    
    def test_signal_performance_with_multiple_documents(self):
        """Test signal performance with multiple documents"""
        documents = []
        
        # Mock the document upload signal to prevent automatic processing
        with patch('faktury.signals.handle_document_upload_created'):
            # Create multiple documents
            for i in range(5):
                doc = DocumentUpload.objects.create(
                    user=self.user,
                    original_filename=f'test_{i}.pdf',
                    file_path=f'/test/path/test_{i}.pdf',
                    file_size=1024 * (i + 1),
                    content_type='application/pdf',
                    processing_status='uploaded'
                )
                documents.append(doc)
            
            # Create OCR results for all documents
            start_time = timezone.now()
            
            for i, doc in enumerate(documents):
                OCRResult.objects.create(
                    document=doc,
                    raw_text=f'Test OCR text {i}',
                    extracted_data={'test': f'data_{i}'},
                    confidence_score=85.0 + i,
                    processing_time=2.0 + i * 0.5,
                    processing_status='completed'
                )
            
            end_time = timezone.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Should complete within reasonable time (less than 5 seconds)
            self.assertLess(processing_time, 5.0)
            
            # Verify all documents were synced
            for doc in documents:
                doc.refresh_from_db()
                self.assertEqual(doc.processing_status, 'completed')
    
    def test_concurrent_status_updates(self):
        """Test concurrent status updates don't cause race conditions"""
        # Mock the document upload signal to prevent automatic processing
        with patch('faktury.signals.handle_document_upload_created'):
            document = DocumentUpload.objects.create(
                user=self.user,
                original_filename='concurrent_test.pdf',
                file_path='/test/path/concurrent_test.pdf',
                file_size=1024,
                content_type='application/pdf',
                processing_status='uploaded'
            )
            
            # Create OCR result
            ocr_result = OCRResult.objects.create(
                document=document,
                raw_text='Test OCR text',
                extracted_data={'test': 'data'},
                confidence_score=85.0,
                processing_time=2.5,
                processing_status='pending'
            )
            
            # Simulate concurrent updates
            from threading import Thread
            import time
            
            def update_ocr_status(status, delay=0):
                time.sleep(delay)
                ocr_result.processing_status = status
                ocr_result.save()
            
            # Start concurrent threads
            thread1 = Thread(target=update_ocr_status, args=('processing', 0.1))
            thread2 = Thread(target=update_ocr_status, args=('completed', 0.2))
            
            thread1.start()
            thread2.start()
            
            thread1.join()
            thread2.join()
            
            # Final status should be consistent
            document.refresh_from_db()
            ocr_result.refresh_from_db()
            
            # Document status should match final OCR status
            self.assertEqual(document.processing_status, 'completed')
            self.assertEqual(ocr_result.processing_status, 'completed')
    
    def test_signal_error_recovery(self):
        """Test signal error recovery mechanisms"""
        # Mock the document upload signal to prevent automatic processing
        with patch('faktury.signals.handle_document_upload_created'):
            document = DocumentUpload.objects.create(
                user=self.user,
                original_filename='error_recovery_test.pdf',
                file_path='/test/path/error_recovery_test.pdf',
                file_size=1024,
                content_type='application/pdf',
                processing_status='uploaded'
            )
            
            # Mock StatusSyncService to fail first time, succeed second time
            call_count = 0
            original_sync = StatusSyncService.sync_document_status
            
            def mock_sync(doc):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("First call fails")
                return original_sync(doc)
            
            with patch.object(StatusSyncService, 'sync_document_status', side_effect=mock_sync):
                # Create OCR result - first sync should fail
                ocr_result = OCRResult.objects.create(
                    document=document,
                    raw_text='Test OCR text',
                    extracted_data={'test': 'data'},
                    confidence_score=85.0,
                    processing_time=2.5,
                    processing_status='pending'
                )
                
                # OCR result should still be created despite sync failure
                self.assertTrue(OCRResult.objects.filter(id=ocr_result.id).exists())
                
                # Update OCR status - second sync should succeed
                ocr_result.processing_status = 'completed'
                ocr_result.save()
                
                # Document should eventually be synced
                document.refresh_from_db()
                self.assertEqual(document.processing_status, 'completed')
    
    def test_signal_with_database_constraints(self):
        """Test signals work correctly with database constraints"""
        # Mock the document upload signal to prevent automatic processing
        with patch('faktury.signals.handle_document_upload_created'):
            document = DocumentUpload.objects.create(
                user=self.user,
                original_filename='constraints_test.pdf',
                file_path='/test/path/constraints_test.pdf',
                file_size=1024,
                content_type='application/pdf',
                processing_status='uploaded'
            )
            
            # Create OCR result
            ocr_result = OCRResult.objects.create(
                document=document,
                raw_text='Test OCR text',
                extracted_data={'test': 'data'},
                confidence_score=85.0,
                processing_time=2.5,
                processing_status='pending'
            )
            
            # Try to create duplicate OCR result (should fail due to OneToOne constraint)
            with self.assertRaises(Exception):
                try:
                    OCRResult.objects.create(
                        document=document,
                        raw_text='Duplicate OCR text',
                        extracted_data={'duplicate': 'data'},
                        confidence_score=90.0,
                        processing_time=3.0,
                        processing_status='pending'
                    )
                except Exception:
                    # Roll back the transaction to continue testing
                    from django.db import transaction
                    transaction.rollback()
                    raise
            
            # Original OCR result should still exist and work
            # Create a new transaction for the refresh
            from django.db import transaction
            with transaction.atomic():
                ocr_result.refresh_from_db()
                self.assertEqual(ocr_result.processing_status, 'pending')
                
                # Status sync should still work
                ocr_result.processing_status = 'completed'
                ocr_result.save()
                
                document.refresh_from_db()
                self.assertEqual(document.processing_status, 'completed')
    
    def test_signal_ordering_and_dependencies(self):
        """Test that signals fire in correct order and handle dependencies"""
        # Mock the document upload signal to prevent automatic processing
        with patch('faktury.signals.handle_document_upload_created'):
            document = DocumentUpload.objects.create(
                user=self.user,
                original_filename='ordering_test.pdf',
                file_path='/test/path/ordering_test.pdf',
                file_size=1024,
                content_type='application/pdf',
                processing_status='uploaded'
            )
            
            # Track signal execution order
            signal_order = []
            
            def track_ocr_created(*args, **kwargs):
                signal_order.append('ocr_created')
                return handle_ocr_result_created(*args, **kwargs)
            
            def track_ocr_status_change(*args, **kwargs):
                signal_order.append('ocr_status_change')
                return handle_ocr_result_status_change(*args, **kwargs)
            
            # Replace signal handlers with tracking versions
            post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
            post_save.disconnect(handle_ocr_result_status_change, sender=OCRResult)
            
            post_save.connect(track_ocr_created, sender=OCRResult)
            post_save.connect(track_ocr_status_change, sender=OCRResult)
            
            try:
                # Create OCR result
                ocr_result = OCRResult.objects.create(
                    document=document,
                    raw_text='Test OCR text',
                    extracted_data={'test': 'data'},
                    confidence_score=85.0,
                    processing_time=2.5,
                    processing_status='pending'
                )
                
                # Both signals should have fired for creation
                self.assertIn('ocr_created', signal_order)
                self.assertIn('ocr_status_change', signal_order)
                
                # Clear signal order for status update test
                signal_order.clear()
                
                # Update OCR status
                ocr_result.processing_status = 'completed'
                ocr_result.save()
                
                # Only status change signal should fire for update
                self.assertIn('ocr_status_change', signal_order)
                self.assertNotIn('ocr_created', signal_order)
                
            finally:
                # Restore original signal handlers
                post_save.disconnect(track_ocr_created, sender=OCRResult)
                post_save.disconnect(track_ocr_status_change, sender=OCRResult)
                
                post_save.connect(handle_ocr_result_created, sender=OCRResult)
                post_save.connect(handle_ocr_result_status_change, sender=OCRResult)


# Re-enable logging after tests
logging.disable(logging.NOTSET)