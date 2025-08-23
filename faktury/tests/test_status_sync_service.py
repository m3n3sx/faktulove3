"""
Unit tests for Status Synchronization Service

Tests the status synchronization between DocumentUpload and OCRResult models.
"""

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch
from django.db.models.signals import post_save

from ..models import DocumentUpload, OCRResult, Firma
from ..services.status_sync_service import StatusSyncService, StatusSyncError
from ..signals import handle_ocr_result_created


class StatusSyncServiceTest(TestCase):
    """Test Status Synchronization Service"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Company',
            nip='1234567890',
            ulica='Test Street',
            numer_domu='1',
            kod_pocztowy='00-000',
            miejscowosc='Test City'
        )
        
        self.document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test.pdf',
            file_path='/test/path/test.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
    
    def test_get_combined_status_without_ocr_result(self):
        """Test getting combined status for document without OCR result"""
        status = StatusSyncService.get_combined_status(self.document)
        
        # Document status is 'queued' due to the upload signal
        self.assertEqual(status['status'], 'queued')
        self.assertEqual(status['display'], 'W kolejce')
        self.assertEqual(status['progress'], 15)
        self.assertFalse(status['can_retry'])
        self.assertFalse(status['is_final'])
        self.assertFalse(status['has_ocr_result'])
    
    def test_get_combined_status_with_ocr_result_pending(self):
        """Test getting combined status with pending OCR result"""
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=85.0,
            processing_time=1.5,
            processing_status='pending'
        )
        
        # Update document status to processing
        self.document.processing_status = 'processing'
        self.document.save()
        
        status = StatusSyncService.get_combined_status(self.document)
        
        self.assertEqual(status['status'], 'queued')
        self.assertEqual(status['display'], 'W kolejce')
        self.assertEqual(status['progress'], 20)
        self.assertTrue(status['has_ocr_result'])
        self.assertEqual(status['confidence_score'], 85.0)
    
    def test_get_combined_status_with_ocr_result_completed(self):
        """Test getting combined status with completed OCR result"""
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=95.0,
            processing_time=2.0,
            processing_status='completed'
        )
        
        # Update document status to completed
        self.document.processing_status = 'completed'
        self.document.save()
        
        status = StatusSyncService.get_combined_status(self.document)
        
        self.assertEqual(status['status'], 'ocr_completed')
        self.assertEqual(status['display'], 'OCR zakończone')
        self.assertEqual(status['progress'], 80)
        self.assertTrue(status['has_ocr_result'])
        self.assertEqual(status['confidence_score'], 95.0)
    
    def test_get_combined_status_with_manual_review(self):
        """Test getting combined status for manual review"""
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=75.0,
            processing_time=1.8,
            processing_status='manual_review'
        )
        
        # Update document status to completed
        self.document.processing_status = 'completed'
        self.document.save()
        
        status = StatusSyncService.get_combined_status(self.document)
        
        self.assertEqual(status['status'], 'manual_review')
        self.assertEqual(status['display'], 'Wymaga przeglądu')
        self.assertEqual(status['progress'], 90)
        self.assertTrue(status['has_ocr_result'])
    
    def test_sync_document_status_no_ocr_result(self):
        """Test syncing document status when no OCR result exists"""
        result = StatusSyncService.sync_document_status(self.document)
        
        self.assertFalse(result)
        # Document status should remain unchanged (queued due to upload signal)
        self.document.refresh_from_db()
        self.assertEqual(self.document.processing_status, 'queued')
    
    def test_sync_document_status_with_ocr_result(self):
        """Test syncing document status with OCR result"""
        # Disconnect the signal to prevent automatic status update
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Ensure document is in a different state than what OCR result will require
            self.document.processing_status = 'processing'
            self.document.save()
            
            ocr_result = OCRResult.objects.create(
                document=self.document,
                raw_text='test text',
                extracted_data={'test': 'data'},
                confidence_score=90.0,
                processing_time=2.5,
                processing_status='completed'
            )
            
            # Document should be updated to completed
            result = StatusSyncService.sync_document_status(self.document)
            
            self.assertTrue(result)
            self.document.refresh_from_db()
            self.assertEqual(self.document.processing_status, 'completed')
            self.assertIsNotNone(self.document.processing_completed_at)
        finally:
            # Reconnect the signal
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_sync_document_status_with_failed_ocr(self):
        """Test syncing document status with failed OCR"""
        # Disconnect the signal to prevent automatic status update
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            error_message = "OCR processing failed"
            ocr_result = OCRResult.objects.create(
                document=self.document,
                raw_text='',
                extracted_data={},
                confidence_score=0.0,
                processing_time=0.5,
                processing_status='failed',
                error_message=error_message
            )
            
            result = StatusSyncService.sync_document_status(self.document)
            
            self.assertTrue(result)
            self.document.refresh_from_db()
            self.assertEqual(self.document.processing_status, 'failed')
            self.assertEqual(self.document.error_message, error_message)
            self.assertIsNotNone(self.document.processing_completed_at)
        finally:
            # Reconnect the signal
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_get_status_display_data(self):
        """Test getting status display data"""
        display_data = StatusSyncService.get_status_display_data(self.document)
        
        self.assertIn('status_class', display_data)
        self.assertIn('progress_class', display_data)
        self.assertIn('icon_class', display_data)
        self.assertIn('show_spinner', display_data)
        self.assertIn('show_retry_button', display_data)
        self.assertIn('show_progress_bar', display_data)
        
        # Check CSS classes for queued status
        self.assertEqual(display_data['status_class'], 'badge-info')
        self.assertEqual(display_data['icon_class'], 'ri-time-line')
        self.assertTrue(display_data['show_spinner'])  # queued status should show spinner
    
    def test_get_processing_progress(self):
        """Test getting processing progress"""
        progress = StatusSyncService.get_processing_progress(self.document)
        self.assertEqual(progress, 15)  # queued status should be 15%
    
    def test_bulk_sync_documents(self):
        """Test bulk synchronization of documents"""
        # Create additional documents
        doc2 = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test2.pdf',
            file_path='/test/path/test2.pdf',
            file_size=2048,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        
        doc3 = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test3.pdf',
            file_path='/test/path/test3.pdf',
            file_size=3072,
            content_type='application/pdf',
            processing_status='processing'
        )
        
        # Disconnect the signal to prevent automatic status update
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Add OCR result to one document - ensure it needs updating
            doc3.processing_status = 'processing'  # Different from what OCR result will require
            doc3.save()
            
            OCRResult.objects.create(
                document=doc3,
                raw_text='test text',
                extracted_data={'test': 'data'},
                confidence_score=88.0,
                processing_time=1.2,
                processing_status='completed'
            )
            
            documents = [self.document, doc2, doc3]
            stats = StatusSyncService.bulk_sync_documents(documents)
            
            self.assertEqual(stats['total'], 3)
            self.assertEqual(stats['updated'], 1)  # Only doc3 should be updated
            self.assertEqual(stats['failed'], 0)
            self.assertEqual(stats['skipped'], 2)  # doc1 and doc2 have no OCR results
        finally:
            # Reconnect the signal
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_model_methods(self):
        """Test that model methods work correctly"""
        # Test DocumentUpload methods
        unified_status = self.document.get_unified_status()
        self.assertIsInstance(unified_status, dict)
        self.assertEqual(unified_status['status'], 'queued')
        
        display_data = self.document.get_status_display_data()
        self.assertIsInstance(display_data, dict)
        self.assertIn('status_class', display_data)
        
        progress = self.document.get_processing_progress()
        self.assertIsInstance(progress, int)
        self.assertEqual(progress, 15)  # queued status should be 15%
    
    def test_ocr_result_sync_method(self):
        """Test OCRResult sync method"""
        # Disconnect the signal to prevent automatic status update
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Ensure document is in a different state
            self.document.processing_status = 'processing'
            self.document.save()
            
            ocr_result = OCRResult.objects.create(
                document=self.document,
                raw_text='test text',
                extracted_data={'test': 'data'},
                confidence_score=92.0,
                processing_time=1.8,
                processing_status='completed'
            )
            
            result = ocr_result.sync_document_status()
            self.assertTrue(result)
            
            self.document.refresh_from_db()
            self.assertEqual(self.document.processing_status, 'completed')
        finally:
            # Reconnect the signal
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_all_status_transitions(self):
        """Test all possible status transitions"""
        # Disconnect the signal to prevent automatic status update
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Test each OCR status and verify document status sync
            test_cases = [
                ('pending', 'processing'),
                ('processing', 'processing'),
                ('completed', 'completed'),
                ('failed', 'failed'),
                ('manual_review', 'completed'),
            ]
            
            for ocr_status, expected_doc_status in test_cases:
                with self.subTest(ocr_status=ocr_status):
                    # Reset document status
                    self.document.processing_status = 'uploaded'
                    self.document.processing_started_at = None
                    self.document.processing_completed_at = None
                    self.document.error_message = None
                    self.document.save()
                    
                    # Delete any existing OCR result
                    OCRResult.objects.filter(document=self.document).delete()
                    
                    # Create OCR result with specific status
                    ocr_result = OCRResult.objects.create(
                        document=self.document,
                        raw_text='test text',
                        extracted_data={'test': 'data'},
                        confidence_score=85.0,
                        processing_time=2.0,
                        processing_status=ocr_status,
                        error_message='Test error' if ocr_status == 'failed' else None
                    )
                    
                    # Sync status
                    result = StatusSyncService.sync_document_status(self.document)
                    self.assertTrue(result)
                    
                    # Verify document status
                    self.document.refresh_from_db()
                    self.assertEqual(self.document.processing_status, expected_doc_status)
                    
                    # Verify timestamps
                    if expected_doc_status == 'processing':
                        self.assertIsNotNone(self.document.processing_started_at)
                    elif expected_doc_status in ['completed', 'failed']:
                        self.assertIsNotNone(self.document.processing_completed_at)
                    
                    # Verify error message for failed status
                    if ocr_status == 'failed':
                        self.assertEqual(self.document.error_message, 'Test error')
        finally:
            # Reconnect the signal
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_status_sync_error_handling(self):
        """Test error handling in status synchronization"""
        # Test with invalid OCR status
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            ocr_result = OCRResult.objects.create(
                document=self.document,
                raw_text='test text',
                extracted_data={'test': 'data'},
                confidence_score=85.0,
                processing_time=2.0,
                processing_status='completed'
            )
            
            # Manually set invalid status to test error handling
            ocr_result.processing_status = 'invalid_status'
            ocr_result.save(update_fields=['processing_status'])
            
            # This should return False for unknown status
            result = StatusSyncService.sync_document_status(self.document)
            self.assertFalse(result)
            
        finally:
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_combined_status_edge_cases(self):
        """Test edge cases in combined status calculation"""
        # Test with document in cancelled status
        self.document.processing_status = 'cancelled'
        self.document.save()
        
        status = StatusSyncService.get_combined_status(self.document)
        self.assertEqual(status['status'], 'cancelled')
        self.assertEqual(status['display'], 'Anulowano')
        self.assertTrue(status['is_final'])
        
        # Test with unknown status combination
        self.document.processing_status = 'unknown_status'
        self.document.save()
        
        status = StatusSyncService.get_combined_status(self.document)
        self.assertEqual(status['status'], 'unknown_status')
        self.assertEqual(status['progress'], 0)
    
    def test_status_display_data_completeness(self):
        """Test that status display data contains all required fields"""
        display_data = StatusSyncService.get_status_display_data(self.document)
        
        required_fields = [
            'status_class', 'progress_class', 'icon_class',
            'show_spinner', 'show_retry_button', 'show_progress_bar',
            'status', 'display', 'progress', 'can_retry', 'is_final'
        ]
        
        for field in required_fields:
            self.assertIn(field, display_data, f"Missing field: {field}")
    
    def test_processing_progress_calculation(self):
        """Test processing progress calculation for all statuses"""
        test_statuses = [
            ('uploaded', 10),
            ('queued', 15),
            ('processing', 30),
            ('ocr_completed', 80),
            ('manual_review', 95),
            ('completed', 100),
            ('failed', 0),
            ('cancelled', 0),
        ]
        
        for status, expected_progress in test_statuses:
            with self.subTest(status=status):
                self.document.processing_status = status
                self.document.save()
                
                progress = StatusSyncService.get_processing_progress(self.document)
                self.assertEqual(progress, expected_progress)
    
    def test_bulk_sync_with_mixed_scenarios(self):
        """Test bulk sync with various document scenarios"""
        # Create documents with different scenarios
        doc_no_ocr = DocumentUpload.objects.create(
            user=self.user,
            original_filename='no_ocr.pdf',
            file_path='/test/path/no_ocr.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        
        doc_with_ocr = DocumentUpload.objects.create(
            user=self.user,
            original_filename='with_ocr.pdf',
            file_path='/test/path/with_ocr.pdf',
            file_size=2048,
            content_type='application/pdf',
            processing_status='processing'
        )
        
        doc_failed = DocumentUpload.objects.create(
            user=self.user,
            original_filename='failed.pdf',
            file_path='/test/path/failed.pdf',
            file_size=3072,
            content_type='application/pdf',
            processing_status='processing'
        )
        
        # Disconnect signal to prevent automatic updates
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Add OCR results
            OCRResult.objects.create(
                document=doc_with_ocr,
                raw_text='test text',
                extracted_data={'test': 'data'},
                confidence_score=90.0,
                processing_time=2.0,
                processing_status='completed'
            )
            
            OCRResult.objects.create(
                document=doc_failed,
                raw_text='',
                extracted_data={},
                confidence_score=0.0,
                processing_time=0.5,
                processing_status='failed',
                error_message='Processing failed'
            )
            
            # Bulk sync
            documents = [doc_no_ocr, doc_with_ocr, doc_failed]
            stats = StatusSyncService.bulk_sync_documents(documents)
            
            self.assertEqual(stats['total'], 3)
            self.assertEqual(stats['updated'], 2)  # doc_with_ocr and doc_failed
            self.assertEqual(stats['skipped'], 1)  # doc_no_ocr
            self.assertEqual(stats['failed'], 0)
            
            # Verify updates
            doc_with_ocr.refresh_from_db()
            doc_failed.refresh_from_db()
            
            self.assertEqual(doc_with_ocr.processing_status, 'completed')
            self.assertEqual(doc_failed.processing_status, 'failed')
            self.assertEqual(doc_failed.error_message, 'Processing failed')
            
        finally:
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_status_sync_service_exception_handling(self):
        """Test StatusSyncService exception handling"""
        # Create a mock document that will cause an exception
        with patch.object(DocumentUpload, 'save') as mock_save:
            mock_save.side_effect = Exception("Database error")
            
            post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
            
            try:
                ocr_result = OCRResult.objects.create(
                    document=self.document,
                    raw_text='test text',
                    extracted_data={'test': 'data'},
                    confidence_score=85.0,
                    processing_time=2.0,
                    processing_status='completed'
                )
                
                # This should raise StatusSyncError
                with self.assertRaises(StatusSyncError):
                    StatusSyncService.sync_document_status(self.document)
                    
            finally:
                post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_combined_status_with_exception(self):
        """Test combined status calculation with exceptions"""
        # Create a document that will cause an exception when accessing ocrresult
        # by mocking the property to raise an exception
        with patch('faktury.models.DocumentUpload.ocrresult', new_callable=lambda: property(lambda self: (_ for _ in ()).throw(Exception("Database error")))):
            status = StatusSyncService.get_combined_status(self.document)
            
            # Should return error status due to exception handling in the service
            self.assertEqual(status['status'], 'error')
            self.assertEqual(status['display'], 'Błąd systemu')
            self.assertTrue(status['can_retry'])
            self.assertFalse(status['is_final'])
            self.assertIn('error_message', status)
    
    def test_css_class_methods(self):
        """Test CSS class generation methods"""
        # Test status CSS classes
        test_cases = [
            ('uploaded', 'badge-secondary'),
            ('queued', 'badge-info'),
            ('processing', 'badge-warning'),
            ('ocr_completed', 'badge-success'),
            ('manual_review', 'badge-warning'),
            ('failed', 'badge-danger'),
            ('cancelled', 'badge-secondary'),
            ('error', 'badge-danger'),
            ('unknown', 'badge-secondary'),  # fallback
        ]
        
        for status, expected_class in test_cases:
            with self.subTest(status=status):
                css_class = StatusSyncService._get_status_css_class(status)
                self.assertEqual(css_class, expected_class)
        
        # Test progress CSS classes
        progress_cases = [
            (0, 'progress-bar-danger'),
            (25, 'progress-bar-info'),
            (60, 'progress-bar-warning'),
            (90, 'progress-bar-success'),
        ]
        
        for progress, expected_class in progress_cases:
            with self.subTest(progress=progress):
                css_class = StatusSyncService._get_progress_css_class(progress)
                self.assertEqual(css_class, expected_class)
        
        # Test icon CSS classes
        icon_cases = [
            ('uploaded', 'ri-upload-line'),
            ('queued', 'ri-time-line'),
            ('processing', 'ri-loader-line'),
            ('ocr_completed', 'ri-check-line'),
            ('manual_review', 'ri-eye-line'),
            ('failed', 'ri-error-warning-line'),
            ('cancelled', 'ri-close-line'),
            ('error', 'ri-alert-line'),
            ('unknown', 'ri-question-line'),  # fallback
        ]
        
        for status, expected_class in icon_cases:
            with self.subTest(status=status):
                icon_class = StatusSyncService._get_status_icon_class(status)
                self.assertEqual(icon_class, expected_class)