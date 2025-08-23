"""
Tests for model status methods

Tests the status-related methods added to DocumentUpload and OCRResult models
to ensure they work correctly and integrate properly with the status sync service.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock

from ..models import DocumentUpload, OCRResult, Firma
from ..services.status_sync_service import StatusSyncService


class DocumentUploadStatusMethodsTest(TestCase):
    """Test DocumentUpload status-related methods"""
    
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
    
    def test_get_unified_status_method(self):
        """Test DocumentUpload.get_unified_status() method"""
        # Test without OCR result
        unified_status = self.document.get_unified_status()
        
        self.assertIsInstance(unified_status, dict)
        self.assertIn('status', unified_status)
        self.assertIn('display', unified_status)
        self.assertIn('progress', unified_status)
        self.assertEqual(unified_status['document_id'], self.document.id)
        self.assertFalse(unified_status['has_ocr_result'])
        
        # Test with OCR result
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='completed'
        )
        
        unified_status = self.document.get_unified_status()
        
        self.assertTrue(unified_status['has_ocr_result'])
        self.assertEqual(unified_status['confidence_score'], 85.0)
        self.assertFalse(unified_status['auto_created_faktura'])
    
    def test_get_status_display_data_method(self):
        """Test DocumentUpload.get_status_display_data() method"""
        display_data = self.document.get_status_display_data()
        
        self.assertIsInstance(display_data, dict)
        
        # Check for template-friendly fields
        required_fields = [
            'status_class', 'progress_class', 'icon_class',
            'show_spinner', 'show_retry_button', 'show_progress_bar'
        ]
        
        for field in required_fields:
            self.assertIn(field, display_data)
        
        # Check CSS classes are strings
        self.assertIsInstance(display_data['status_class'], str)
        self.assertIsInstance(display_data['progress_class'], str)
        self.assertIsInstance(display_data['icon_class'], str)
        
        # Check boolean flags
        self.assertIsInstance(display_data['show_spinner'], bool)
        self.assertIsInstance(display_data['show_retry_button'], bool)
        self.assertIsInstance(display_data['show_progress_bar'], bool)
    
    def test_get_processing_progress_method(self):
        """Test DocumentUpload.get_processing_progress() method"""
        progress = self.document.get_processing_progress()
        
        self.assertIsInstance(progress, int)
        self.assertGreaterEqual(progress, 0)
        self.assertLessEqual(progress, 100)
        
        # Test with different statuses
        test_statuses = ['uploaded', 'queued', 'processing', 'completed', 'failed']
        
        for status in test_statuses:
            with self.subTest(status=status):
                self.document.processing_status = status
                self.document.save()
                
                progress = self.document.get_processing_progress()
                self.assertIsInstance(progress, int)
                self.assertGreaterEqual(progress, 0)
                self.assertLessEqual(progress, 100)
    
    def test_mark_processing_started_method(self):
        """Test DocumentUpload.mark_processing_started() method"""
        # Initially no processing start time
        self.assertIsNone(self.document.processing_started_at)
        self.assertEqual(self.document.processing_status, 'queued')  # From upload signal
        
        # Mark as started
        self.document.mark_processing_started()
        
        # Refresh from database
        self.document.refresh_from_db()
        
        self.assertEqual(self.document.processing_status, 'processing')
        self.assertIsNotNone(self.document.processing_started_at)
        self.assertIsNone(self.document.processing_completed_at)
    
    def test_mark_processing_completed_method(self):
        """Test DocumentUpload.mark_processing_completed() method"""
        # Initially no completion time
        self.assertIsNone(self.document.processing_completed_at)
        
        # Mark as completed
        self.document.mark_processing_completed()
        
        # Refresh from database
        self.document.refresh_from_db()
        
        self.assertEqual(self.document.processing_status, 'completed')
        self.assertIsNotNone(self.document.processing_completed_at)
    
    def test_mark_processing_failed_method(self):
        """Test DocumentUpload.mark_processing_failed() method"""
        error_message = "Processing failed due to invalid format"
        
        # Initially no error
        self.assertIsNone(self.document.error_message)
        self.assertIsNone(self.document.processing_completed_at)
        
        # Mark as failed
        self.document.mark_processing_failed(error_message)
        
        # Refresh from database
        self.document.refresh_from_db()
        
        self.assertEqual(self.document.processing_status, 'failed')
        self.assertEqual(self.document.error_message, error_message)
        self.assertIsNotNone(self.document.processing_completed_at)
    
    def test_processing_duration_property(self):
        """Test DocumentUpload.processing_duration property"""
        # Initially no duration (no timestamps)
        self.assertIsNone(self.document.processing_duration)
        
        # Set start time
        start_time = timezone.now()
        self.document.processing_started_at = start_time
        self.document.save()
        
        # Still no duration (no end time)
        self.assertIsNone(self.document.processing_duration)
        
        # Set end time
        end_time = start_time + timezone.timedelta(seconds=30)
        self.document.processing_completed_at = end_time
        self.document.save()
        
        # Should have duration
        duration = self.document.processing_duration
        self.assertIsNotNone(duration)
        self.assertEqual(duration, 30.0)  # 30 seconds
    
    def test_str_method(self):
        """Test DocumentUpload.__str__() method"""
        str_repr = str(self.document)
        
        self.assertIn(self.document.original_filename, str_repr)
        self.assertIn(self.document.get_processing_status_display(), str_repr)
    
    def test_method_integration_with_status_sync_service(self):
        """Test that model methods properly integrate with StatusSyncService"""
        # Mock StatusSyncService methods to verify they're called
        with patch.object(StatusSyncService, 'get_combined_status') as mock_combined:
            mock_combined.return_value = {'status': 'test', 'progress': 50}
            
            result = self.document.get_unified_status()
            
            mock_combined.assert_called_once_with(self.document)
            self.assertEqual(result, {'status': 'test', 'progress': 50})
        
        with patch.object(StatusSyncService, 'get_status_display_data') as mock_display:
            mock_display.return_value = {'status_class': 'test-class'}
            
            result = self.document.get_status_display_data()
            
            mock_display.assert_called_once_with(self.document)
            self.assertEqual(result, {'status_class': 'test-class'})
        
        with patch.object(StatusSyncService, 'get_processing_progress') as mock_progress:
            mock_progress.return_value = 75
            
            result = self.document.get_processing_progress()
            
            mock_progress.assert_called_once_with(self.document)
            self.assertEqual(result, 75)


class OCRResultStatusMethodsTest(TestCase):
    """Test OCRResult status-related methods"""
    
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
        
        self.ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='pending'
        )
    
    def test_needs_human_review_property(self):
        """Test OCRResult.needs_human_review property"""
        # Test with low confidence (should need review)
        self.ocr_result.confidence_score = 75.0
        self.assertTrue(self.ocr_result.needs_human_review)
        
        # Test with high confidence (should not need review)
        self.ocr_result.confidence_score = 85.0
        self.assertFalse(self.ocr_result.needs_human_review)
        
        # Test boundary case
        self.ocr_result.confidence_score = 80.0
        self.assertFalse(self.ocr_result.needs_human_review)
        
        self.ocr_result.confidence_score = 79.9
        self.assertTrue(self.ocr_result.needs_human_review)
    
    def test_can_auto_create_faktura_property(self):
        """Test OCRResult.can_auto_create_faktura property"""
        # Test with low confidence (should not auto-create)
        self.ocr_result.confidence_score = 85.0
        self.assertFalse(self.ocr_result.can_auto_create_faktura)
        
        # Test with high confidence (should auto-create)
        self.ocr_result.confidence_score = 95.0
        self.assertTrue(self.ocr_result.can_auto_create_faktura)
        
        # Test boundary case
        self.ocr_result.confidence_score = 90.0
        self.assertTrue(self.ocr_result.can_auto_create_faktura)
        
        self.ocr_result.confidence_score = 89.9
        self.assertFalse(self.ocr_result.can_auto_create_faktura)
    
    def test_confidence_level_property(self):
        """Test OCRResult.confidence_level property"""
        test_cases = [
            (95.0, 'high'),
            (90.0, 'high'),
            (89.9, 'medium'),
            (85.0, 'medium'),
            (80.0, 'medium'),
            (79.9, 'low'),
            (50.0, 'low'),
            (0.0, 'low'),
        ]
        
        for confidence, expected_level in test_cases:
            with self.subTest(confidence=confidence):
                self.ocr_result.confidence_score = confidence
                self.assertEqual(self.ocr_result.confidence_level, expected_level)
    
    def test_mark_processing_started_method(self):
        """Test OCRResult.mark_processing_started() method"""
        self.assertEqual(self.ocr_result.processing_status, 'pending')
        
        self.ocr_result.mark_processing_started()
        
        # Refresh from database
        self.ocr_result.refresh_from_db()
        self.assertEqual(self.ocr_result.processing_status, 'processing')
    
    def test_mark_processing_completed_method(self):
        """Test OCRResult.mark_processing_completed() method"""
        self.ocr_result.mark_processing_completed()
        
        # Refresh from database
        self.ocr_result.refresh_from_db()
        self.assertEqual(self.ocr_result.processing_status, 'completed')
    
    def test_mark_processing_failed_method(self):
        """Test OCRResult.mark_processing_failed() method"""
        error_message = "OCR processing failed"
        
        self.assertIsNone(self.ocr_result.error_message)
        
        self.ocr_result.mark_processing_failed(error_message)
        
        # Refresh from database
        self.ocr_result.refresh_from_db()
        self.assertEqual(self.ocr_result.processing_status, 'failed')
        self.assertEqual(self.ocr_result.error_message, error_message)
    
    def test_mark_manual_review_required_method(self):
        """Test OCRResult.mark_manual_review_required() method"""
        self.ocr_result.mark_manual_review_required()
        
        # Refresh from database
        self.ocr_result.refresh_from_db()
        self.assertEqual(self.ocr_result.processing_status, 'manual_review')
    
    def test_sync_document_status_method(self):
        """Test OCRResult.sync_document_status() method"""
        # Mock StatusSyncService to verify it's called
        with patch.object(StatusSyncService, 'sync_document_status') as mock_sync:
            mock_sync.return_value = True
            
            result = self.ocr_result.sync_document_status()
            
            mock_sync.assert_called_once_with(self.document)
            self.assertTrue(result)
    
    def test_str_method(self):
        """Test OCRResult.__str__() method"""
        str_repr = str(self.ocr_result)
        
        self.assertIn('OCR:', str_repr)
        self.assertIn(self.document.original_filename, str_repr)
        self.assertIn('85.0%', str_repr)
    
    def test_save_method_behavior(self):
        """Test OCRResult.save() method behavior"""
        # Test that save method doesn't interfere with normal operation
        original_status = self.ocr_result.processing_status
        
        self.ocr_result.confidence_score = 90.0
        self.ocr_result.save()
        
        # Refresh from database
        self.ocr_result.refresh_from_db()
        
        # Status should remain the same, confidence should be updated
        self.assertEqual(self.ocr_result.processing_status, original_status)
        self.assertEqual(self.ocr_result.confidence_score, 90.0)
    
    def test_method_chaining(self):
        """Test that status methods can be chained properly"""
        # Test that methods return None (can't be chained) but work correctly
        result1 = self.ocr_result.mark_processing_started()
        self.assertIsNone(result1)
        
        result2 = self.ocr_result.mark_processing_completed()
        self.assertIsNone(result2)
        
        # Verify final state
        self.ocr_result.refresh_from_db()
        self.assertEqual(self.ocr_result.processing_status, 'completed')
    
    def test_status_methods_with_database_errors(self):
        """Test status methods handle database errors gracefully"""
        # Mock save to raise an exception
        with patch.object(OCRResult, 'save') as mock_save:
            mock_save.side_effect = Exception("Database error")
            
            # Methods should raise the exception (not handle it silently)
            with self.assertRaises(Exception):
                self.ocr_result.mark_processing_completed()
    
    def test_properties_with_edge_case_values(self):
        """Test properties with edge case confidence values"""
        edge_cases = [-10.0, 0.0, 100.0, 150.0, None]
        
        for confidence in edge_cases:
            with self.subTest(confidence=confidence):
                if confidence is not None:
                    self.ocr_result.confidence_score = confidence
                    
                    # Properties should not raise exceptions
                    try:
                        needs_review = self.ocr_result.needs_human_review
                        can_auto_create = self.ocr_result.can_auto_create_faktura
                        level = self.ocr_result.confidence_level
                        
                        # All should return valid values
                        self.assertIsInstance(needs_review, bool)
                        self.assertIsInstance(can_auto_create, bool)
                        self.assertIn(level, ['low', 'medium', 'high'])
                        
                    except Exception as e:
                        self.fail(f"Property failed with confidence {confidence}: {e}")


class ModelStatusIntegrationTest(TestCase):
    """Test integration between DocumentUpload and OCRResult status methods"""
    
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
    
    def test_document_and_ocr_status_synchronization(self):
        """Test that document and OCR status methods work together"""
        from django.db.models.signals import post_save
        from ..signals import handle_ocr_result_created, handle_ocr_result_status_change
        
        # Disconnect signals to test manual sync
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        post_save.disconnect(handle_ocr_result_status_change, sender=OCRResult)
        
        try:
            # Set document to uploaded status
            self.document.processing_status = 'uploaded'
            self.document.save()
            
            # Create OCR result
            ocr_result = OCRResult.objects.create(
                document=self.document,
                raw_text='test text',
                extracted_data={'test': 'data'},
                confidence_score=85.0,
                processing_time=2.0,
                processing_status='pending'
            )
            
            # Update OCR status and sync document
            ocr_result.mark_processing_started()
            ocr_result.sync_document_status()
            
            # Document should be updated
            self.document.refresh_from_db()
            self.assertEqual(self.document.processing_status, 'processing')
            
            # Complete OCR processing and sync
            ocr_result.mark_processing_completed()
            ocr_result.sync_document_status()
            
            # Document should be completed
            self.document.refresh_from_db()
            self.assertEqual(self.document.processing_status, 'completed')
            
            # Unified status should reflect both
            unified_status = self.document.get_unified_status()
            self.assertEqual(unified_status['status'], 'ocr_completed')
            self.assertTrue(unified_status['has_ocr_result'])
        finally:
            # Reconnect signals
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
            post_save.connect(handle_ocr_result_status_change, sender=OCRResult)
    
    def test_error_handling_integration(self):
        """Test error handling integration between models"""
        # Create OCR result
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='pending'
        )
        
        # Mark OCR as failed
        error_message = "OCR processing failed"
        ocr_result.mark_processing_failed(error_message)
        ocr_result.sync_document_status()
        
        # Document should also be failed with same error
        self.document.refresh_from_db()
        self.assertEqual(self.document.processing_status, 'failed')
        self.assertEqual(self.document.error_message, error_message)
        
        # Unified status should show error state
        unified_status = self.document.get_unified_status()
        self.assertEqual(unified_status['status'], 'failed')
        self.assertTrue(unified_status['can_retry'])
        self.assertTrue(unified_status['is_final'])
    
    def test_timestamp_consistency(self):
        """Test that timestamps are consistent between models"""
        # Create OCR result
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='pending'
        )
        
        # Mark document as started
        self.document.mark_processing_started()
        start_time = self.document.processing_started_at
        
        # Mark OCR as completed and sync
        ocr_result.mark_processing_completed()
        ocr_result.sync_document_status()
        
        # Document should have completion time
        self.document.refresh_from_db()
        self.assertIsNotNone(self.document.processing_completed_at)
        self.assertIsNotNone(start_time)
        
        # Processing duration should be calculable
        duration = self.document.processing_duration
        self.assertIsNotNone(duration)
        self.assertGreater(duration, 0)