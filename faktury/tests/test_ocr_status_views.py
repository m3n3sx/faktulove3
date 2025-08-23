"""
Unit tests for OCR Status Views

Tests the AJAX endpoints for real-time status polling and unified status information.
"""

import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from ..models import DocumentUpload, OCRResult, Firma
from ..services.status_sync_service import StatusSyncService


class OCRStatusViewsTest(TestCase):
    """Test OCR status AJAX endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test firma
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Company',
            nip='1234567890',
            ulica='Test Street',
            numer_domu='1',
            kod_pocztowy='00-000',
            miejscowosc='Test City'
        )
        
        # Create test document upload
        # Note: The signal will change status from 'uploaded' to 'queued' automatically
        self.document_upload = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test_document.pdf',
            file_path='/test/path/test_document.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        # Refresh from database to get the updated status from signals
        self.document_upload.refresh_from_db()
        
        # Login user
        self.client.login(username='testuser', password='testpass123')
    
    def test_get_status_ajax_success(self):
        """Test successful AJAX status request"""
        url = reverse('ocr_ajax_status', kwargs={'document_id': self.document_upload.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['document_id'], self.document_upload.id)
        # After creation, the signal changes status to 'queued'
        self.assertEqual(data['data']['status'], 'queued')
        self.assertIn('polling', data['data'])
        # Verify document status is 'queued' after signal processing
        self.assertEqual(data['data']['document_status'], 'queued')
    
    def test_get_status_ajax_document_not_found(self):
        """Test AJAX status request for non-existent document"""
        url = reverse('ocr_ajax_status', kwargs={'document_id': 99999})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'DOCUMENT_NOT_FOUND')
    
    def test_get_status_ajax_unauthorized(self):
        """Test AJAX status request without authentication"""
        self.client.logout()
        url = reverse('ocr_ajax_status', kwargs={'document_id': self.document_upload.id})
        
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_get_status_ajax_wrong_user(self):
        """Test AJAX status request for document owned by different user"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Create document for other user
        other_document = DocumentUpload.objects.create(
            user=other_user,
            original_filename='other_document.pdf',
            file_path='/test/path/other_document.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        
        url = reverse('ocr_ajax_status', kwargs={'document_id': other_document.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_status_display_ajax_success(self):
        """Test successful display status AJAX request"""
        url = reverse('ocr_ajax_status_display', kwargs={'document_id': self.document_upload.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('status_class', data['data'])
        self.assertIn('icon_class', data['data'])
        self.assertIn('show_spinner', data['data'])
    
    def test_get_progress_ajax_success(self):
        """Test successful progress AJAX request"""
        url = reverse('ocr_ajax_progress', kwargs={'document_id': self.document_upload.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('progress', data['data'])
        self.assertIsInstance(data['data']['progress'], int)
        self.assertGreaterEqual(data['data']['progress'], 0)
        self.assertLessEqual(data['data']['progress'], 100)
    
    def test_api_get_status_success(self):
        """Test successful REST API status request"""
        url = reverse('ocr_api_status_unified', kwargs={'document_id': self.document_upload.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['document_id'], self.document_upload.id)
        self.assertIn('api_version', data['data'])
    
    def test_api_bulk_status_success(self):
        """Test successful bulk status API request"""
        # Create another document
        document2 = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test_document2.pdf',
            file_path='/test/path/test_document2.pdf',
            file_size=2048,
            content_type='application/pdf',
            processing_status='processing'
        )
        
        url = reverse('ocr_api_bulk_status')
        document_ids = f"{self.document_upload.id},{document2.id}"
        
        response = self.client.get(url, {'document_ids': document_ids})
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn(str(self.document_upload.id), data['data'])
        self.assertIn(str(document2.id), data['data'])
        self.assertEqual(data['metadata']['requested_count'], 2)
        self.assertEqual(data['metadata']['found_count'], 2)
    
    def test_api_bulk_status_no_document_ids(self):
        """Test bulk status API request without document IDs"""
        url = reverse('ocr_api_bulk_status')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'MISSING_DOCUMENT_IDS')
    
    def test_api_bulk_status_invalid_document_ids(self):
        """Test bulk status API request with invalid document IDs"""
        url = reverse('ocr_api_bulk_status')
        
        response = self.client.get(url, {'document_ids': 'invalid,not_a_number'})
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'INVALID_DOCUMENT_IDS')
    
    def test_api_bulk_status_too_many_documents(self):
        """Test bulk status API request with too many document IDs"""
        url = reverse('ocr_api_bulk_status')
        document_ids = ','.join([str(i) for i in range(1, 52)])  # 51 documents
        
        response = self.client.get(url, {'document_ids': document_ids})
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'TOO_MANY_DOCUMENTS')
    
    def test_status_with_ocr_result(self):
        """Test status endpoint with OCR result present"""
        # Create OCR result
        ocr_result = OCRResult.objects.create(
            document=self.document_upload,
            raw_text='Test OCR text',
            extracted_data={'test': 'data'},
            confidence_score=85.5,
            processing_time=2.5,
            processing_status='completed'
        )
        
        url = reverse('ocr_ajax_status', kwargs={'document_id': self.document_upload.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['has_ocr_result'])
        self.assertEqual(data['data']['confidence_score'], 85.5)
        self.assertFalse(data['data']['auto_created_faktura'])
    
    @patch('faktury.services.status_sync_service.StatusSyncService.sync_document_status')
    def test_status_sync_error_handling(self, mock_sync):
        """Test handling of status sync errors"""
        # Make sync_document_status raise an exception
        mock_sync.side_effect = Exception("Sync failed")
        
        url = reverse('ocr_ajax_status', kwargs={'document_id': self.document_upload.id})
        
        response = self.client.get(url)
        
        # Should still return status even if sync fails
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        # Sync should have been attempted
        mock_sync.assert_called_once_with(self.document_upload)
    
    def test_polling_intervals(self):
        """Test that different statuses return appropriate polling intervals"""
        test_cases = [
            ('uploaded', 2000),
            ('processing', 1000),
            ('completed', 0),
            ('failed', 30000),
        ]
        
        for status, expected_interval in test_cases:
            self.document_upload.processing_status = status
            self.document_upload.save()
            
            url = reverse('ocr_ajax_status', kwargs={'document_id': self.document_upload.id})
            response = self.client.get(url)
            
            data = json.loads(response.content)
            self.assertEqual(
                data['data']['polling']['interval_ms'], 
                expected_interval,
                f"Wrong interval for status {status}"
            )
    
    def test_post_method_not_allowed(self):
        """Test that POST method is not allowed on GET-only endpoints"""
        url = reverse('ocr_ajax_status', kwargs={'document_id': self.document_upload.id})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 405)  # Method Not Allowed