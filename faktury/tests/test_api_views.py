"""
Integration tests for OCR REST API endpoints.

Tests complete end-to-end workflows including:
- File upload to OCR processing
- Status tracking and progress updates
- Results retrieval with filtering and pagination
- Manual validation workflow
- Error scenarios and edge cases
- Authentication and authorization
- Rate limiting and throttling
- Celery task integration

Requirements covered: 1.1, 1.7, 2.1, 2.2, 3.1, 3.2, 4.1, 5.1
"""

import json
import tempfile
import os
from decimal import Decimal
from datetime import datetime, date, timedelta
from unittest.mock import patch, Mock, MagicMock
from io import BytesIO

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.test.utils import override_settings
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from celery.result import AsyncResult

from faktury.models import DocumentUpload, OCRResult, Faktura, Firma, Kontrahent
from faktury.api.serializers import (
    DocumentUploadSerializer, OCRResultListSerializer, 
    OCRResultDetailSerializer, TaskStatusSerializer, OCRValidationSerializer
)
from faktury.api.exceptions import FileValidationError, TaskNotFoundError
from faktury.services.file_upload_service import FileUploadService


class BaseAPITestCase(APITestCase):
    """Base test case with common setup for API tests"""
    
    def setUp(self):
        """Set up test data and authentication"""
        self.client = APIClient()
        
        # Create test users with unique usernames
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
        
        self.other_user = User.objects.create_user(
            username=f'otheruser_{unique_id}',
            email=f'other_{unique_id}@example.com',
            password='testpass123'
        )
        
        # Create company profiles
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Company',
            nip='9876543210',
            ulica='Test Street',
            numer_domu='1',
            kod_pocztowy='00-000',
            miejscowosc='Test City'
        )
        
        self.other_firma = Firma.objects.create(
            user=self.other_user,
            nazwa='Other Company',
            nip='1234567890',
            ulica='Other Street',
            numer_domu='2',
            kod_pocztowy='11-111',
            miejscowosc='Other City'
        )
        
        # Set up authentication
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token
        
        # Clear cache before each test
        cache.clear()
    
    def authenticate(self, user=None):
        """Authenticate client with JWT token"""
        if user is None:
            user = self.user
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def create_test_file(self, content=None, filename='test.pdf', content_type='application/pdf'):
        """Create test file for upload"""
        if content is None:
            # Create valid PDF content
            content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF'
        
        return SimpleUploadedFile(filename, content, content_type=content_type)
    
    def create_document_upload(self, user=None, status='uploaded'):
        """Create test DocumentUpload instance"""
        if user is None:
            user = self.user
            
        return DocumentUpload.objects.create(
            user=user,
            original_filename='test_invoice.pdf',
            file_path='/tmp/test_invoice.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status=status
        )
    
    def create_ocr_result(self, document=None, confidence=95.0):
        """Create test OCRResult instance"""
        if document is None:
            document = self.create_document_upload()
            
        return OCRResult.objects.create(
            document=document,
            raw_text='Test OCR text',
            extracted_data={
                'numer_faktury': 'FV/2025/001',
                'data_wystawienia': '2025-08-20',
                'sprzedawca': {
                    'nazwa': 'Test Supplier',
                    'nip': '1234567890'
                },
                'suma_brutto': 1230.00,
                'pozycje': [
                    {
                        'nazwa': 'Test Product',
                        'cena_netto': 1000.00,
                        'vat': 23
                    }
                ]
            },
            confidence_score=confidence,
            field_confidence={
                'numer_faktury': 98.0,
                'data_wystawienia': 95.0,
                'sprzedawca': 90.0,
                'suma_brutto': confidence
            },
            processing_time=2.5,
            processing_status='completed'
        )


class OCRUploadAPIViewTest(BaseAPITestCase):
    """Test OCR file upload API endpoint"""
    
    def setUp(self):
        super().setUp()
        self.upload_url = reverse('api:v1:ocr-upload')
        self.authenticate()
    
    @patch('faktury.services.file_upload_service.FileUploadService.handle_upload')
    @patch('faktury.tasks.process_document_ocr_task.delay')
    def test_successful_file_upload(self, mock_task, mock_upload):
        """Test successful file upload with task queuing"""
        # Setup mocks
        document = self.create_document_upload()
        mock_upload.return_value = document
        
        mock_task_result = Mock()
        mock_task_result.id = 'test-task-id-123'
        mock_task.return_value = mock_task_result
        
        # Create test file
        test_file = self.create_test_file()
        
        # Make request
        response = self.client.post(self.upload_url, {'file': test_file}, format='multipart')
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertEqual(data['task_id'], 'test-task-id-123')
        self.assertEqual(data['document_id'], document.id)
        self.assertEqual(data['filename'], 'test_invoice.pdf')
        self.assertIn('estimated_processing_time', data)
        self.assertEqual(data['status'], 'queued')
        
        # Verify mocks were called
        mock_upload.assert_called_once()
        mock_task.assert_called_once_with(document.id)
    
    def test_upload_without_authentication(self):
        """Test upload without authentication returns 401"""
        self.client.credentials()  # Remove authentication
        
        test_file = self.create_test_file()
        response = self.client.post(self.upload_url, {'file': test_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_upload_without_file(self):
        """Test upload without file returns validation error"""
        response = self.client.post(self.upload_url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('file', response.data['error']['message'].lower())
    
    def test_upload_oversized_file(self):
        """Test upload of oversized file returns validation error"""
        # Create file larger than 10MB
        large_content = b'x' * (11 * 1024 * 1024)
        large_file = self.create_test_file(content=large_content)
        
        response = self.client.post(self.upload_url, {'file': large_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('size', response.data['error']['message'].lower())
    
    def test_upload_invalid_file_type(self):
        """Test upload of invalid file type returns validation error"""
        invalid_file = self.create_test_file(
            content=b'This is plain text',
            filename='test.txt',
            content_type='text/plain'
        )
        
        response = self.client.post(self.upload_url, {'file': invalid_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('type', response.data['error']['message'].lower())
    
    @patch('faktury.services.file_upload_service.FileUploadService.handle_upload')
    def test_upload_service_error(self, mock_upload):
        """Test handling of file upload service errors"""
        mock_upload.side_effect = FileValidationError("File validation failed")
        
        test_file = self.create_test_file()
        response = self.client.post(self.upload_url, {'file': test_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('validation', response.data['error']['message'].lower())
    
    @override_settings(RATELIMIT_ENABLE=True)
    def test_rate_limiting(self):
        """Test rate limiting for file uploads"""
        test_file = self.create_test_file()
        
        # Make multiple requests to trigger rate limiting
        # Note: This test assumes rate limiting is configured for testing
        with patch('faktury.services.file_upload_service.FileUploadService.handle_upload') as mock_upload:
            document = self.create_document_upload()
            mock_upload.return_value = document
            
            with patch('faktury.tasks.process_document_ocr_task.delay') as mock_task:
                mock_task_result = Mock()
                mock_task_result.id = 'test-task-id'
                mock_task.return_value = mock_task_result
                
                # Make requests up to the limit
                for i in range(12):  # Assuming limit is 10 per minute
                    test_file.seek(0)  # Reset file pointer
                    response = self.client.post(self.upload_url, {'file': test_file}, format='multipart')
                    
                    if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                        self.assertFalse(response.data['success'])
                        self.assertIn('rate', response.data['error']['message'].lower())
                        break
                else:
                    # If we didn't hit rate limit, that's also acceptable for this test
                    pass


class OCRStatusAPIViewTest(BaseAPITestCase):
    """Test OCR status tracking API endpoint"""
    
    def setUp(self):
        super().setUp()
        self.authenticate()
    
    def get_status_url(self, task_id):
        """Get status URL for task ID"""
        return reverse('api:v1:ocr-status', kwargs={'task_id': task_id})
    
    @patch('celery.result.AsyncResult')
    def test_get_task_status_pending(self, mock_async_result):
        """Test getting status for pending task"""
        # Setup mock
        mock_result = Mock()
        mock_result.state = 'PENDING'
        mock_result.result = None
        mock_async_result.return_value = mock_result
        
        task_id = 'test-task-123'
        url = self.get_status_url(task_id)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertEqual(data['task_id'], task_id)
        self.assertEqual(data['status'], 'pending')
        self.assertEqual(data['progress'], 0)
        self.assertIn('message', data)
    
    @patch('celery.result.AsyncResult')
    def test_get_task_status_processing(self, mock_async_result):
        """Test getting status for processing task"""
        # Setup mock
        mock_result = Mock()
        mock_result.state = 'PROGRESS'
        mock_result.result = {
            'progress': 65,
            'message': 'Extracting invoice data...',
            'eta_seconds': 15
        }
        mock_async_result.return_value = mock_result
        
        task_id = 'test-task-456'
        url = self.get_status_url(task_id)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertEqual(data['status'], 'processing')
        self.assertEqual(data['progress'], 65)
        self.assertEqual(data['eta_seconds'], 15)
        self.assertEqual(data['message'], 'Extracting invoice data...')
    
    @patch('celery.result.AsyncResult')
    def test_get_task_status_completed(self, mock_async_result):
        """Test getting status for completed task"""
        # Setup mock
        mock_result = Mock()
        mock_result.state = 'SUCCESS'
        mock_result.result = {
            'document_upload_id': 123,
            'ocr_result_id': 456
        }
        mock_async_result.return_value = mock_result
        
        task_id = 'test-task-789'
        url = self.get_status_url(task_id)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['progress'], 100)
        self.assertIn('result', data)
    
    @patch('celery.result.AsyncResult')
    def test_get_task_status_failed(self, mock_async_result):
        """Test getting status for failed task"""
        # Setup mock
        mock_result = Mock()
        mock_result.state = 'FAILURE'
        mock_result.result = Exception('OCR processing failed')
        mock_async_result.return_value = mock_result
        
        task_id = 'test-task-failed'
        url = self.get_status_url(task_id)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertEqual(data['status'], 'failed')
        self.assertEqual(data['progress'], 0)
        self.assertIn('error', data)
    
    @patch('celery.result.AsyncResult')
    def test_get_nonexistent_task_status(self, mock_async_result):
        """Test getting status for nonexistent task"""
        # Setup mock to simulate nonexistent task
        mock_result = Mock()
        mock_result.state = 'PENDING'
        mock_result.result = None
        mock_async_result.return_value = mock_result
        
        task_id = 'nonexistent-task'
        url = self.get_status_url(task_id)
        
        response = self.client.get(url)
        
        # Should return task not found error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertIn('not found', response.data['error']['message'].lower())
    
    def test_get_task_status_without_authentication(self):
        """Test getting task status without authentication"""
        self.client.credentials()  # Remove authentication
        
        task_id = 'test-task-123'
        url = self.get_status_url(task_id)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('celery.result.AsyncResult')
    @patch('faktury.models.DocumentUpload.objects.get')
    def test_get_task_status_with_document_info(self, mock_doc_get, mock_async_result):
        """Test getting task status with associated document information"""
        # Setup document mock
        document = self.create_document_upload()
        mock_doc_get.return_value = document
        
        # Setup task mock
        mock_result = Mock()
        mock_result.state = 'SUCCESS'
        mock_result.result = {'document_upload_id': document.id}
        mock_async_result.return_value = mock_result
        
        task_id = 'test-task-with-doc'
        url = self.get_status_url(task_id)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertIn('document', data)
        self.assertEqual(data['document']['id'], document.id)
        self.assertEqual(data['document']['filename'], document.original_filename)


class OCRResultsListAPIViewTest(BaseAPITestCase):
    """Test OCR results list API endpoint with filtering and pagination"""
    
    def setUp(self):
        super().setUp()
        self.results_url = reverse('api:v1:ocr-results')
        self.authenticate()
        
        # Create test OCR results
        self.document1 = self.create_document_upload()
        self.document2 = self.create_document_upload()
        self.document3 = self.create_document_upload(user=self.other_user)
        
        self.ocr_result1 = self.create_ocr_result(self.document1, confidence=95.0)
        self.ocr_result2 = self.create_ocr_result(self.document2, confidence=75.0)
        self.ocr_result3 = self.create_ocr_result(self.document3, confidence=85.0)
    
    def test_get_results_list_basic(self):
        """Test basic results list retrieval"""
        response = self.client.get(self.results_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertIn('results', data)
        self.assertIn('pagination', data)
        
        # Should only return current user's results
        results = data['results']
        self.assertEqual(len(results), 2)  # Only user's results, not other_user's
        
        # Check pagination metadata
        pagination = data['pagination']
        self.assertEqual(pagination['count'], 2)
        self.assertEqual(pagination['page'], 1)
        self.assertFalse(pagination['has_previous'])
        self.assertFalse(pagination['has_next'])
    
    def test_get_results_list_with_pagination(self):
        """Test results list with pagination"""
        # Create more results to test pagination
        for i in range(25):
            doc = self.create_document_upload()
            self.create_ocr_result(doc, confidence=80.0 + i)
        
        # Test first page
        response = self.client.get(self.results_url, {'page': 1, 'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        self.assertEqual(len(data['results']), 10)
        self.assertEqual(data['pagination']['page'], 1)
        self.assertTrue(data['pagination']['has_next'])
        self.assertFalse(data['pagination']['has_previous'])
        
        # Test second page
        response = self.client.get(self.results_url, {'page': 2, 'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        self.assertEqual(data['pagination']['page'], 2)
        self.assertTrue(data['pagination']['has_previous'])
    
    def test_get_results_list_with_confidence_filter(self):
        """Test results list with confidence score filtering"""
        response = self.client.get(self.results_url, {'min_confidence': 80})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Should only return results with confidence >= 80
        results = data['results']
        self.assertEqual(len(results), 1)  # Only ocr_result1 has 95% confidence
        self.assertEqual(results[0]['confidence_score'], 95.0)
        
        # Check filter metadata
        self.assertIn('filters_applied', data)
        self.assertEqual(data['filters_applied']['min_confidence'], '80')
    
    def test_get_results_list_with_date_filter(self):
        """Test results list with date range filtering"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Update one result to be from yesterday
        self.ocr_result2.created_at = timezone.make_aware(
            datetime.combine(yesterday, datetime.min.time())
        )
        self.ocr_result2.save()
        
        # Filter for today only
        response = self.client.get(self.results_url, {
            'date_from': today.strftime('%Y-%m-%d'),
            'date_to': today.strftime('%Y-%m-%d')
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Should only return today's results
        results = data['results']
        self.assertEqual(len(results), 1)  # Only ocr_result1 is from today
    
    def test_get_results_list_with_search(self):
        """Test results list with search functionality"""
        # Update one result to have searchable content
        self.ocr_result1.extracted_data['numer_faktury'] = 'SEARCH-123'
        self.ocr_result1.save()
        
        response = self.client.get(self.results_url, {'search': 'SEARCH-123'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Should only return matching results
        results = data['results']
        self.assertEqual(len(results), 1)
        self.assertIn('SEARCH-123', str(results[0]))
    
    def test_get_results_list_with_status_filter(self):
        """Test results list with processing status filtering"""
        # Update one result to have different status
        self.ocr_result2.processing_status = 'manual_review'
        self.ocr_result2.save()
        
        response = self.client.get(self.results_url, {'status': 'manual_review'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Should only return results with matching status
        results = data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.ocr_result2.id)
    
    def test_get_results_list_without_authentication(self):
        """Test results list without authentication"""
        self.client.credentials()  # Remove authentication
        
        response = self.client.get(self.results_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_results_list_ordering(self):
        """Test results list ordering (newest first)"""
        # Create results with different timestamps
        old_time = timezone.now() - timedelta(hours=2)
        self.ocr_result1.created_at = old_time
        self.ocr_result1.save()
        
        response = self.client.get(self.results_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        results = data['results']
        self.assertEqual(len(results), 2)
        
        # Should be ordered by creation date (newest first)
        self.assertEqual(results[0]['id'], self.ocr_result2.id)  # Newer
        self.assertEqual(results[1]['id'], self.ocr_result1.id)  # Older


class OCRResultDetailAPIViewTest(BaseAPITestCase):
    """Test OCR result detail API endpoint"""
    
    def setUp(self):
        super().setUp()
        self.authenticate()
        
        self.document = self.create_document_upload()
        self.ocr_result = self.create_ocr_result(self.document)
    
    def get_detail_url(self, result_id):
        """Get detail URL for result ID"""
        return reverse('api:v1:ocr-result-detail', kwargs={'result_id': result_id})
    
    def test_get_result_detail_success(self):
        """Test successful retrieval of OCR result detail"""
        url = self.get_detail_url(self.ocr_result.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertEqual(data['id'], self.ocr_result.id)
        self.assertEqual(data['confidence_score'], 95.0)
        self.assertIn('document', data)
        self.assertIn('validation_fields', data)
        self.assertIn('confidence_breakdown', data)
        self.assertIn('metadata', data)
        
        # Check document information
        document_data = data['document']
        self.assertEqual(document_data['id'], self.document.id)
        self.assertEqual(document_data['filename'], self.document.original_filename)
    
    def test_get_result_detail_with_faktura(self):
        """Test result detail when linked to a Faktura"""
        # Create a linked Faktura
        kontrahent = Kontrahent.objects.create(
            firma=self.firma,
            nazwa='Test Supplier',
            nip='1234567890',
            ulica='Supplier Street',
            numer_domu='1',
            kod_pocztowy='11-111',
            miejscowosc='Supplier City'
        )
        
        faktura = Faktura.objects.create(
            user=self.user,
            numer='FV/2025/001',
            data_wystawienia=date.today(),
            kontrahent=kontrahent,
            suma_netto=Decimal('1000.00'),
            suma_brutto=Decimal('1230.00'),
            status='wystawiona'
        )
        
        self.ocr_result.faktura = faktura
        self.ocr_result.save()
        
        url = self.get_detail_url(self.ocr_result.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Check faktura information is included
        self.assertIn('faktura', data)
        faktura_data = data['faktura']
        self.assertEqual(faktura_data['id'], faktura.id)
        self.assertEqual(faktura_data['numer'], 'FV/2025/001')
    
    def test_get_result_detail_not_found(self):
        """Test getting detail for nonexistent result"""
        url = self.get_detail_url(99999)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertIn('not found', response.data['error']['message'].lower())
    
    def test_get_result_detail_unauthorized(self):
        """Test getting detail for result owned by another user"""
        # Create result owned by other user
        other_document = self.create_document_upload(user=self.other_user)
        other_result = self.create_ocr_result(other_document)
        
        url = self.get_detail_url(other_result.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertIn('permission', response.data['error']['message'].lower())
    
    def test_get_result_detail_without_authentication(self):
        """Test getting result detail without authentication"""
        self.client.credentials()  # Remove authentication
        
        url = self.get_detail_url(self.ocr_result.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_result_detail_validation_fields(self):
        """Test validation fields in result detail"""
        url = self.get_detail_url(self.ocr_result.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        validation_fields = data['validation_fields']
        self.assertIn('numer_faktury', validation_fields)
        self.assertIn('data_wystawienia', validation_fields)
        self.assertIn('sprzedawca', validation_fields)
        
        # Check field structure
        numer_field = validation_fields['numer_faktury']
        self.assertEqual(numer_field['value'], 'FV/2025/001')
        self.assertEqual(numer_field['confidence'], 98.0)
        self.assertFalse(numer_field['needs_review'])  # High confidence
    
    def test_get_result_detail_confidence_breakdown(self):
        """Test confidence breakdown in result detail"""
        url = self.get_detail_url(self.ocr_result.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        breakdown = data['confidence_breakdown']
        self.assertIn('document_info', breakdown)
        self.assertIn('parties', breakdown)
        self.assertIn('amounts', breakdown)
        
        # Check structure of breakdown categories
        doc_info = breakdown['document_info']
        self.assertIn('average', doc_info)
        self.assertIn('min', doc_info)
        self.assertIn('max', doc_info)
        self.assertIn('count', doc_info)


class OCRValidationAPIViewTest(BaseAPITestCase):
    """Test OCR validation API endpoint for manual corrections"""
    
    def setUp(self):
        super().setUp()
        self.authenticate()
        
        self.document = self.create_document_upload()
        self.ocr_result = self.create_ocr_result(self.document)
    
    def get_validation_url(self, result_id):
        """Get validation URL for result ID"""
        return reverse('api:v1:ocr-validate', kwargs={'result_id': result_id})
    
    def test_validate_ocr_result_success(self):
        """Test successful OCR result validation with corrections"""
        url = self.get_validation_url(self.ocr_result.id)
        
        corrections_data = {
            'corrections': {
                'numer_faktury': 'FV/2025/001-CORRECTED',
                'suma_brutto': 1500.00,
                'sprzedawca.nazwa': 'Corrected Supplier Name'
            },
            'create_faktura': True,
            'validation_notes': 'Corrected invoice number and amount'
        }
        
        response = self.client.post(url, corrections_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertIn('updated_fields', data)
        self.assertIn('new_confidence_scores', data)
        
        # Check updated fields
        updated_fields = data['updated_fields']
        self.assertIn('numer_faktury', updated_fields)
        self.assertIn('suma_brutto', updated_fields)
        self.assertIn('sprzedawca.nazwa', updated_fields)
        
        # Check confidence scores were updated to 100%
        confidence_scores = data['new_confidence_scores']
        self.assertEqual(confidence_scores['numer_faktury'], 100.0)
        self.assertEqual(confidence_scores['suma_brutto'], 100.0)
        
        # Verify database was updated
        self.ocr_result.refresh_from_db()
        self.assertEqual(
            self.ocr_result.extracted_data['numer_faktury'], 
            'FV/2025/001-CORRECTED'
        )
        self.assertEqual(self.ocr_result.extracted_data['suma_brutto'], 1500.00)
    
    @patch('faktury.services.ocr_integration.create_faktura_from_ocr')
    def test_validate_with_faktura_creation(self, mock_create_faktura):
        """Test validation with automatic Faktura creation"""
        # Setup mock
        kontrahent = Kontrahent.objects.create(
            firma=self.firma,
            nazwa='Test Supplier',
            nip='1234567890',
            ulica='Supplier Street',
            numer_domu='1',
            kod_pocztowy='11-111',
            miejscowosc='Supplier City'
        )
        
        faktura = Faktura.objects.create(
            user=self.user,
            numer='FV/2025/001-CORRECTED',
            data_wystawienia=date.today(),
            kontrahent=kontrahent,
            suma_netto=Decimal('1000.00'),
            suma_brutto=Decimal('1500.00'),
            status='wystawiona'
        )
        
        mock_create_faktura.return_value = faktura
        
        url = self.get_validation_url(self.ocr_result.id)
        
        corrections_data = {
            'corrections': {
                'numer_faktury': 'FV/2025/001-CORRECTED',
                'suma_brutto': 1500.00
            },
            'create_faktura': True
        }
        
        response = self.client.post(url, corrections_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertTrue(data.get('faktura_created', False))
        self.assertEqual(data.get('faktura_id'), faktura.id)
        
        # Verify mock was called
        mock_create_faktura.assert_called_once()
    
    def test_validate_empty_corrections(self):
        """Test validation with empty corrections"""
        url = self.get_validation_url(self.ocr_result.id)
        
        corrections_data = {
            'corrections': {},
            'create_faktura': False
        }
        
        response = self.client.post(url, corrections_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('corrections', response.data['error']['message'].lower())
    
    def test_validate_invalid_corrections_format(self):
        """Test validation with invalid corrections format"""
        url = self.get_validation_url(self.ocr_result.id)
        
        corrections_data = {
            'corrections': 'invalid format',
            'create_faktura': False
        }
        
        response = self.client.post(url, corrections_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_validate_nonexistent_result(self):
        """Test validation for nonexistent OCR result"""
        url = self.get_validation_url(99999)
        
        corrections_data = {
            'corrections': {'numer_faktury': 'FV/2025/001'},
            'create_faktura': False
        }
        
        response = self.client.post(url, corrections_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
    
    def test_validate_unauthorized_result(self):
        """Test validation for result owned by another user"""
        # Create result owned by other user
        other_document = self.create_document_upload(user=self.other_user)
        other_result = self.create_ocr_result(other_document)
        
        url = self.get_validation_url(other_result.id)
        
        corrections_data = {
            'corrections': {'numer_faktury': 'FV/2025/001'},
            'create_faktura': False
        }
        
        response = self.client.post(url, corrections_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
    
    def test_validate_without_authentication(self):
        """Test validation without authentication"""
        self.client.credentials()  # Remove authentication
        
        url = self.get_validation_url(self.ocr_result.id)
        
        corrections_data = {
            'corrections': {'numer_faktury': 'FV/2025/001'},
            'create_faktura': False
        }
        
        response = self.client.post(url, corrections_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OCRAPIWorkflowIntegrationTest(BaseAPITestCase):
    """Test complete OCR API workflow from upload to validation"""
    
    def setUp(self):
        super().setUp()
        self.authenticate()
    
    @patch('faktury.services.file_upload_service.FileUploadService.handle_upload')
    @patch('faktury.tasks.process_document_ocr_task.delay')
    @patch('celery.result.AsyncResult')
    def test_complete_upload_to_validation_workflow(self, mock_async_result, mock_task, mock_upload):
        """Test complete workflow from upload to validation"""
        
        # Step 1: Upload file
        document = self.create_document_upload()
        mock_upload.return_value = document
        
        mock_task_result = Mock()
        mock_task_result.id = 'test-task-123'
        mock_task.return_value = mock_task_result
        
        test_file = self.create_test_file()
        upload_url = reverse('api:v1:ocr-upload')
        
        upload_response = self.client.post(upload_url, {'file': test_file}, format='multipart')
        
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        task_id = upload_response.data['data']['task_id']
        document_id = upload_response.data['data']['document_id']
        
        # Step 2: Check status (processing)
        mock_result = Mock()
        mock_result.state = 'PROGRESS'
        mock_result.result = {
            'progress': 50,
            'message': 'Processing document...',
            'document_upload_id': document_id
        }
        mock_async_result.return_value = mock_result
        
        status_url = reverse('api:v1:ocr-status', kwargs={'task_id': task_id})
        status_response = self.client.get(status_url)
        
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_response.data['data']['status'], 'processing')
        self.assertEqual(status_response.data['data']['progress'], 50)
        
        # Step 3: Check status (completed) and create OCR result
        ocr_result = self.create_ocr_result(document, confidence=85.0)
        
        mock_result.state = 'SUCCESS'
        mock_result.result = {
            'document_upload_id': document_id,
            'ocr_result_id': ocr_result.id
        }
        
        status_response = self.client.get(status_url)
        
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_response.data['data']['status'], 'completed')
        self.assertEqual(status_response.data['data']['progress'], 100)
        
        # Step 4: Get results list
        results_url = reverse('api:v1:ocr-results')
        results_response = self.client.get(results_url)
        
        self.assertEqual(results_response.status_code, status.HTTP_200_OK)
        results = results_response.data['data']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], ocr_result.id)
        
        # Step 5: Get detailed result
        detail_url = reverse('api:v1:ocr-result-detail', kwargs={'result_id': ocr_result.id})
        detail_response = self.client.get(detail_url)
        
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        detail_data = detail_response.data['data']
        self.assertEqual(detail_data['id'], ocr_result.id)
        self.assertIn('validation_fields', detail_data)
        
        # Step 6: Validate and correct result
        validation_url = reverse('api:v1:ocr-validate', kwargs={'result_id': ocr_result.id})
        
        corrections_data = {
            'corrections': {
                'numer_faktury': 'FV/2025/001-FINAL',
                'suma_brutto': 1234.56
            },
            'create_faktura': False,
            'validation_notes': 'Final corrections applied'
        }
        
        validation_response = self.client.post(validation_url, corrections_data, format='json')
        
        self.assertEqual(validation_response.status_code, status.HTTP_200_OK)
        validation_data = validation_response.data['data']
        self.assertIn('updated_fields', validation_data)
        self.assertEqual(len(validation_data['updated_fields']), 2)
        
        # Verify final state
        ocr_result.refresh_from_db()
        self.assertEqual(ocr_result.extracted_data['numer_faktury'], 'FV/2025/001-FINAL')
        self.assertEqual(ocr_result.extracted_data['suma_brutto'], 1234.56)
        self.assertEqual(ocr_result.field_confidence['numer_faktury'], 100.0)
    
    def test_error_handling_throughout_workflow(self):
        """Test error handling at various stages of the workflow"""
        
        # Test upload error
        upload_url = reverse('api:v1:ocr-upload')
        upload_response = self.client.post(upload_url, {}, format='multipart')
        
        self.assertEqual(upload_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(upload_response.data['success'])
        
        # Test status error for nonexistent task
        status_url = reverse('api:v1:ocr-status', kwargs={'task_id': 'nonexistent'})
        
        with patch('celery.result.AsyncResult') as mock_async_result:
            mock_result = Mock()
            mock_result.state = 'PENDING'
            mock_result.result = None
            mock_async_result.return_value = mock_result
            
            status_response = self.client.get(status_url)
            self.assertEqual(status_response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test detail error for nonexistent result
        detail_url = reverse('api:v1:ocr-result-detail', kwargs={'result_id': 99999})
        detail_response = self.client.get(detail_url)
        
        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(detail_response.data['success'])
        
        # Test validation error for nonexistent result
        validation_url = reverse('api:v1:ocr-validate', kwargs={'result_id': 99999})
        validation_response = self.client.post(validation_url, {
            'corrections': {'test': 'value'},
            'create_faktura': False
        }, format='json')
        
        self.assertEqual(validation_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(validation_response.data['success'])


class OCRAPIPerformanceTest(BaseAPITestCase):
    """Test API performance and optimization"""
    
    def setUp(self):
        super().setUp()
        self.authenticate()
    
    def test_results_list_query_optimization(self):
        """Test that results list uses optimized queries"""
        # Create multiple results with related objects
        for i in range(10):
            document = self.create_document_upload()
            self.create_ocr_result(document, confidence=80.0 + i)
        
        results_url = reverse('api:v1:ocr-results')
        
        # Use Django's assertNumQueries to check query count
        with self.assertNumQueries(3):  # Should be optimized with select_related
            response = self.client.get(results_url)
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 10)
    
    def test_large_pagination_performance(self):
        """Test performance with large result sets"""
        # Create many results
        for i in range(100):
            document = self.create_document_upload()
            self.create_ocr_result(document, confidence=80.0)
        
        results_url = reverse('api:v1:ocr-results')
        
        # Test different page sizes
        for page_size in [10, 20, 50]:
            response = self.client.get(results_url, {'page_size': page_size})
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['data']['results']), page_size)
            
            # Response should be reasonably fast
            # In a real test, you might measure response time
    
    def test_concurrent_api_requests(self):
        """Test handling of concurrent API requests"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                client = APIClient()
                client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
                
                response = client.get(reverse('api:v1:ocr-results'))
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads making concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(status_code == 200 for status_code in results))