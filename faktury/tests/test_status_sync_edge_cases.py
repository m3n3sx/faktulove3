"""
Edge case tests for Status Synchronization Service

Tests edge cases, error conditions, and boundary scenarios for the status
synchronization system between DocumentUpload and OCRResult models.
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction, IntegrityError
from unittest.mock import patch, MagicMock
from decimal import Decimal

from ..models import DocumentUpload, OCRResult, Firma, Kontrahent, Faktura
from ..services.status_sync_service import StatusSyncService, StatusSyncError


class StatusSyncEdgeCasesTest(TestCase):
    """Test edge cases in status synchronization"""
    
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
    
    def test_sync_with_deleted_ocr_result(self):
        """Test sync behavior when OCR result is deleted during processing"""
        # Create OCR result
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='completed'
        )
        
        # Delete OCR result
        ocr_result.delete()
        
        # Sync should return False (no OCR result to sync)
        result = StatusSyncService.sync_document_status(self.document)
        self.assertFalse(result)
    
    def test_sync_with_corrupted_ocr_data(self):
        """Test sync with corrupted OCR result data"""
        # Disconnect signal to prevent automatic sync
        from django.db.models.signals import post_save
        from ..signals import handle_ocr_result_created
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Set document to different status first
            self.document.processing_status = 'processing'
            self.document.save()
            
            # Create OCR result with None values
            ocr_result = OCRResult.objects.create(
                document=self.document,
                raw_text='',
                extracted_data={},
                confidence_score=0.0,
                processing_time=0.0,
                processing_status='completed'
            )
            
            # Should still sync successfully
            result = StatusSyncService.sync_document_status(self.document)
            self.assertTrue(result)
            
            self.document.refresh_from_db()
            self.assertEqual(self.document.processing_status, 'completed')
        finally:
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_sync_with_extreme_confidence_scores(self):
        """Test sync with extreme confidence scores"""
        from django.db.models.signals import post_save
        from ..signals import handle_ocr_result_created
        
        test_cases = [
            (-10.0, 'completed'),  # Negative confidence
            (0.0, 'completed'),    # Zero confidence
            (100.0, 'completed'),  # Perfect confidence
            (150.0, 'completed'),  # Over 100% confidence
        ]
        
        for confidence, expected_status in test_cases:
            with self.subTest(confidence=confidence):
                # Disconnect signal to prevent automatic sync
                post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
                
                try:
                    # Clean up previous OCR result
                    OCRResult.objects.filter(document=self.document).delete()
                    
                    # Set document to different status first
                    self.document.processing_status = 'processing'
                    self.document.save()
                    
                    ocr_result = OCRResult.objects.create(
                        document=self.document,
                        raw_text='test text',
                        extracted_data={'test': 'data'},
                        confidence_score=confidence,
                        processing_time=2.0,
                        processing_status='completed'
                    )
                    
                    result = StatusSyncService.sync_document_status(self.document)
                    self.assertTrue(result)
                    
                    self.document.refresh_from_db()
                    self.assertEqual(self.document.processing_status, expected_status)
                finally:
                    post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_sync_with_very_long_error_messages(self):
        """Test sync with very long error messages"""
        from django.db.models.signals import post_save
        from ..signals import handle_ocr_result_created
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Set document to different status first
            self.document.processing_status = 'processing'
            self.document.save()
            
            long_error = "Error: " + "x" * 10000  # Very long error message
            
            ocr_result = OCRResult.objects.create(
                document=self.document,
                raw_text='',
                extracted_data={},
                confidence_score=0.0,
                processing_time=0.5,
                processing_status='failed',
                error_message=long_error
            )
            
            result = StatusSyncService.sync_document_status(self.document)
            self.assertTrue(result)
            
            self.document.refresh_from_db()
            self.assertEqual(self.document.processing_status, 'failed')
            self.assertEqual(self.document.error_message, long_error)
        finally:
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_sync_with_unicode_and_special_characters(self):
        """Test sync with unicode and special characters in data"""
        from django.db.models.signals import post_save
        from ..signals import handle_ocr_result_created
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Set document to different status first
            self.document.processing_status = 'processing'
            self.document.save()
            
            special_text = "Tëst tëxt wïth spëcïäl chäräctërs: 中文 العربية 🚀 💯"
            special_data = {
                'unicode_field': 'Ñoñó Ñañá',
                'emoji_field': '🎉🎊🎈',
                'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
                'mixed': 'Test 测试 тест テスト'
            }
            
            ocr_result = OCRResult.objects.create(
                document=self.document,
                raw_text=special_text,
                extracted_data=special_data,
                confidence_score=85.0,
                processing_time=2.0,
                processing_status='completed'
            )
            
            result = StatusSyncService.sync_document_status(self.document)
            self.assertTrue(result)
            
            self.document.refresh_from_db()
            self.assertEqual(self.document.processing_status, 'completed')
        finally:
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_combined_status_with_missing_timestamps(self):
        """Test combined status calculation with missing timestamps"""
        # Create document with missing timestamps
        self.document.processing_started_at = None
        self.document.processing_completed_at = None
        self.document.save()
        
        status = StatusSyncService.get_combined_status(self.document)
        
        # Should handle None timestamps gracefully
        self.assertIsNone(status['processing_started_at'])
        self.assertIsNone(status['processing_completed_at'])
        self.assertIsNotNone(status['upload_timestamp'])
    
    def test_combined_status_with_future_timestamps(self):
        """Test combined status with future timestamps (edge case)"""
        future_time = timezone.now() + timezone.timedelta(days=1)
        
        self.document.processing_started_at = future_time
        self.document.processing_completed_at = future_time
        self.document.save()
        
        status = StatusSyncService.get_combined_status(self.document)
        
        # Should handle future timestamps without errors
        self.assertIsNotNone(status['processing_started_at'])
        self.assertIsNotNone(status['processing_completed_at'])
    
    def test_bulk_sync_with_empty_list(self):
        """Test bulk sync with empty document list"""
        stats = StatusSyncService.bulk_sync_documents([])
        
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['updated'], 0)
        self.assertEqual(stats['failed'], 0)
        self.assertEqual(stats['skipped'], 0)
    
    def test_bulk_sync_with_none_values(self):
        """Test bulk sync with None values in list"""
        documents = [self.document, None, self.document]
        
        # Should handle None values gracefully
        with self.assertRaises(AttributeError):
            StatusSyncService.bulk_sync_documents(documents)
    
    def test_status_display_with_malformed_data(self):
        """Test status display with malformed data"""
        # Create OCR result with malformed extracted_data
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data="not a dict",  # Should be dict but is string
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='completed'
        )
        
        # Should handle malformed data gracefully
        display_data = StatusSyncService.get_status_display_data(self.document)
        
        self.assertIsInstance(display_data, dict)
        self.assertIn('status', display_data)
        self.assertIn('display', display_data)
    
    def test_processing_progress_with_invalid_status(self):
        """Test processing progress with invalid status"""
        self.document.processing_status = 'invalid_status'
        self.document.save()
        
        progress = StatusSyncService.get_processing_progress(self.document)
        
        # Should return 0 for unknown status
        self.assertEqual(progress, 0)
    
    def test_css_class_methods_with_none_input(self):
        """Test CSS class methods with None input"""
        # Should handle None gracefully
        status_class = StatusSyncService._get_status_css_class(None)
        self.assertEqual(status_class, 'badge-secondary')
        
        progress_class = StatusSyncService._get_progress_css_class(None)
        self.assertEqual(progress_class, 'progress-bar-danger')
        
        icon_class = StatusSyncService._get_status_icon_class(None)
        self.assertEqual(icon_class, 'ri-question-line')
    
    def test_sync_with_database_transaction_rollback(self):
        """Test sync behavior during database transaction rollback"""
        try:
            with transaction.atomic():
                ocr_result = OCRResult.objects.create(
                    document=self.document,
                    raw_text='test text',
                    extracted_data={'test': 'data'},
                    confidence_score=85.0,
                    processing_time=2.0,
                    processing_status='completed'
                )
                
                # Force a rollback
                raise IntegrityError("Forced rollback")
                
        except IntegrityError:
            pass
        
        # OCR result should not exist after rollback
        self.assertFalse(OCRResult.objects.filter(document=self.document).exists())
        
        # Document status should remain unchanged
        self.document.refresh_from_db()
        self.assertEqual(self.document.processing_status, 'queued')  # From upload signal
    
    def test_memory_usage_with_large_datasets(self):
        """Test memory usage with large extracted data"""
        from django.db.models.signals import post_save
        from ..signals import handle_ocr_result_created
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Set document to different status first
            self.document.processing_status = 'processing'
            self.document.save()
            
            # Create large extracted data
            large_data = {
                f'field_{i}': f'value_{i}' * 1000 for i in range(100)
            }
            
            ocr_result = OCRResult.objects.create(
                document=self.document,
                raw_text='x' * 10000,  # Large text
                extracted_data=large_data,
                confidence_score=85.0,
                processing_time=2.0,
                processing_status='completed'
            )
            
            # Should handle large data without memory issues
            result = StatusSyncService.sync_document_status(self.document)
            self.assertTrue(result)
            
            status = StatusSyncService.get_combined_status(self.document)
            self.assertIsInstance(status, dict)
        finally:
            post_save.connect(handle_ocr_result_created, sender=OCRResult)


class StatusSyncConcurrencyTest(TransactionTestCase):
    """Test concurrency scenarios in status synchronization"""
    
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
    
    def test_concurrent_status_updates(self):
        """Test concurrent status updates don't cause data corruption"""
        import threading
        import time
        
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='pending'
        )
        
        results = []
        errors = []
        
        def update_status(status, delay=0):
            try:
                time.sleep(delay)
                ocr_result.processing_status = status
                ocr_result.save()
                result = StatusSyncService.sync_document_status(self.document)
                results.append((status, result))
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads updating status concurrently
        threads = [
            threading.Thread(target=update_status, args=('processing', 0.1)),
            threading.Thread(target=update_status, args=('completed', 0.2)),
            threading.Thread(target=update_status, args=('failed', 0.3)),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should not have any errors
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        
        # Should have results from all threads
        self.assertEqual(len(results), 3)
        
        # Final state should be consistent
        self.document.refresh_from_db()
        ocr_result.refresh_from_db()
        
        # Document status should match final OCR status
        expected_doc_status = StatusSyncService.OCR_TO_DOCUMENT_STATUS_MAP.get(
            ocr_result.processing_status
        )
        self.assertEqual(self.document.processing_status, expected_doc_status)
    
    def test_deadlock_prevention(self):
        """Test that status sync doesn't cause database deadlocks"""
        import threading
        
        # Create multiple documents and OCR results
        documents = []
        ocr_results = []
        
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
            
            ocr = OCRResult.objects.create(
                document=doc,
                raw_text=f'test text {i}',
                extracted_data={'test': f'data_{i}'},
                confidence_score=85.0 + i,
                processing_time=2.0,
                processing_status='pending'
            )
            ocr_results.append(ocr)
        
        errors = []
        
        def bulk_update_status():
            try:
                # Update all OCR results to completed
                for ocr in ocr_results:
                    ocr.processing_status = 'completed'
                    ocr.save()
                    StatusSyncService.sync_document_status(ocr.document)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads doing bulk updates
        threads = [
            threading.Thread(target=bulk_update_status)
            for _ in range(3)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should not have deadlock errors
        deadlock_errors = [e for e in errors if 'deadlock' in str(e).lower()]
        self.assertEqual(len(deadlock_errors), 0, f"Deadlock errors: {deadlock_errors}")
        
        # All documents should be updated
        for doc in documents:
            doc.refresh_from_db()
            self.assertEqual(doc.processing_status, 'completed')


class StatusSyncPerformanceTest(TestCase):
    """Test performance aspects of status synchronization"""
    
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
    
    def test_bulk_sync_performance(self):
        """Test performance of bulk synchronization"""
        import time
        from django.db.models.signals import post_save
        from ..signals import handle_ocr_result_created
        
        # Disconnect signal to prevent automatic sync
        post_save.disconnect(handle_ocr_result_created, sender=OCRResult)
        
        try:
            # Create many documents
            documents = []
            for i in range(50):
                doc = DocumentUpload.objects.create(
                    user=self.user,
                    original_filename=f'test_{i}.pdf',
                    file_path=f'/test/path/test_{i}.pdf',
                    file_size=1024,
                    content_type='application/pdf',
                    processing_status='processing'
                )
                documents.append(doc)
                
                # Add OCR result for half of them
                if i % 2 == 0:
                    OCRResult.objects.create(
                        document=doc,
                        raw_text=f'test text {i}',
                        extracted_data={'test': f'data_{i}'},
                        confidence_score=85.0,
                        processing_time=2.0,
                        processing_status='completed'
                    )
            
            # Measure bulk sync performance
            start_time = time.time()
            stats = StatusSyncService.bulk_sync_documents(documents)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should complete within reasonable time (less than 5 seconds for 50 documents)
            self.assertLess(processing_time, 5.0)
            
            # Should have correct statistics
            self.assertEqual(stats['total'], 50)
            self.assertEqual(stats['updated'], 25)  # Half have OCR results
            self.assertEqual(stats['skipped'], 25)  # Half don't have OCR results
            self.assertEqual(stats['failed'], 0)
        finally:
            post_save.connect(handle_ocr_result_created, sender=OCRResult)
    
    def test_combined_status_query_efficiency(self):
        """Test that combined status queries are efficient"""
        # Create document with OCR result
        document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='efficiency_test.pdf',
            file_path='/test/path/efficiency_test.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='completed'
        )
        
        OCRResult.objects.create(
            document=document,
            raw_text='test text',
            extracted_data={'test': 'data'},
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='completed'
        )
        
        # Measure query performance
        import time
        from django.db import connection
        
        # Reset query count
        connection.queries_log.clear()
        
        start_time = time.time()
        
        # Get combined status multiple times
        for _ in range(10):
            StatusSyncService.get_combined_status(document)
        
        end_time = time.time()
        
        processing_time = end_time - start_time
        query_count = len(connection.queries)
        
        # Should be fast (less than 1 second for 10 calls)
        self.assertLess(processing_time, 1.0)
        
        # Should not make excessive queries (less than 20 for 10 calls)
        self.assertLess(query_count, 20)