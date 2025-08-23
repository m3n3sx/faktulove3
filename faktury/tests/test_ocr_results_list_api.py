"""
Unit tests for OCR Results List API endpoint.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.request import Request
from faktury.models import DocumentUpload, OCRResult, Firma
from faktury.api.views import OCRResultsListAPIView
from faktury.api.serializers import OCRResultListSerializer
from datetime import datetime, timedelta
import json


class OCRResultsListAPIViewTest(TestCase):
    """Test cases for OCRResultsListAPIView."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser_ocr_api',
            password='testpass123'
        )
        
        # Create another user to test ownership filtering
        self.other_user = User.objects.create_user(
            username='otheruser_ocr_api',
            password='testpass123'
        )
        
        # Create companies
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Company',
            nip='1234567890',
            ulica='Test Street',
            numer_domu='1',
            kod_pocztowy='00-000',
            miejscowosc='Test City'
        )
        
        self.other_firma = Firma.objects.create(
            user=self.other_user,
            nazwa='Other Company',
            nip='0987654321',
            ulica='Other Street',
            numer_domu='2',
            kod_pocztowy='11-111',
            miejscowosc='Other City'
        )
        
        # Create test documents
        self.doc1 = DocumentUpload.objects.create(
            user=self.user,
            original_filename='invoice1.pdf',
            file_path='/test/path1.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='completed'
        )
        
        self.doc2 = DocumentUpload.objects.create(
            user=self.user,
            original_filename='receipt2.jpg',
            file_path='/test/path2.jpg',
            file_size=2048,
            content_type='image/jpeg',
            processing_status='completed'
        )
        
        # Document from other user (should not appear in results)
        self.other_doc = DocumentUpload.objects.create(
            user=self.other_user,
            original_filename='other_invoice.pdf',
            file_path='/test/other_path.pdf',
            file_size=1500,
            content_type='application/pdf',
            processing_status='completed'
        )
        
        # Create OCR results
        self.ocr1 = OCRResult.objects.create(
            document=self.doc1,
            raw_text='Test OCR text 1',
            extracted_data={
                'numer_faktury': 'FV/2025/001',
                'sprzedawca': {'nazwa': 'Test Seller 1'},
                'suma_netto': 1000.00
            },
            confidence_score=95.5,
            processing_time=12.3,
            processing_status='completed'
        )
        
        self.ocr2 = OCRResult.objects.create(
            document=self.doc2,
            raw_text='Test OCR text 2',
            extracted_data={
                'numer_faktury': 'FV/2025/002',
                'sprzedawca': {'nazwa': 'Test Seller 2'},
                'suma_netto': 2000.00
            },
            confidence_score=75.2,
            processing_time=15.7,
            processing_status='manual_review'
        )
        
        # OCR result from other user (should not appear)
        self.other_ocr = OCRResult.objects.create(
            document=self.other_doc,
            raw_text='Other OCR text',
            extracted_data={
                'numer_faktury': 'FV/2025/999',
                'sprzedawca': {'nazwa': 'Other Seller'},
                'suma_netto': 500.00
            },
            confidence_score=88.0,
            processing_time=10.0,
            processing_status='completed'
        )
        
        # Set up API factory and view
        self.factory = APIRequestFactory()
        self.view = OCRResultsListAPIView()
    
    def _make_request(self, url, user=None):
        """Helper method to create authenticated request."""
        django_request = self.factory.get(url)
        force_authenticate(django_request, user=user or self.user)
        return Request(django_request)
    
    def test_basic_queryset_filtering(self):
        """Test that queryset is filtered by user ownership."""
        request = self._make_request('/api/ocr/results/')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        
        # Should only return OCR results for the authenticated user
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.ocr1, queryset)
        self.assertIn(self.ocr2, queryset)
        self.assertNotIn(self.other_ocr, queryset)
    
    def test_date_filtering(self):
        """Test date range filtering."""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Test filtering with date range that includes today
        url = f'/api/ocr/results/?date_from={yesterday}&date_to={tomorrow}'
        request = self._make_request(url)
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 2)
        
        # Test filtering with date range that excludes today
        past_date = today - timedelta(days=10)
        url = f'/api/ocr/results/?date_from={past_date}&date_to={yesterday}'
        request = self._make_request(url)
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_confidence_filtering(self):
        """Test confidence score filtering."""
        # Filter for high confidence (>= 90)
        request = self._make_request('/api/ocr/results/?min_confidence=90')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.ocr1, queryset)  # 95.5% confidence
        self.assertNotIn(self.ocr2, queryset)  # 75.2% confidence
        
        # Filter for medium confidence (>= 75)
        request = self._make_request('/api/ocr/results/?min_confidence=75')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 2)
    
    def test_status_filtering(self):
        """Test processing status filtering."""
        # Filter for completed status
        request = self._make_request('/api/ocr/results/?status=completed')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.ocr1, queryset)
        
        # Filter for manual_review status
        request = self._make_request('/api/ocr/results/?status=manual_review')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.ocr2, queryset)
    
    def test_search_filtering(self):
        """Test search functionality."""
        # Search by invoice number
        request = self._make_request('/api/ocr/results/?search=FV/2025/001')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.ocr1, queryset)
        
        # Search by filename
        request = self._make_request('/api/ocr/results/?search=invoice1')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.ocr1, queryset)
        
        # Search by seller name
        request = self._make_request('/api/ocr/results/?search=Test Seller 2')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.ocr2, queryset)
    
    def test_combined_filtering(self):
        """Test multiple filters applied together."""
        # Combine confidence and status filters
        request = self._make_request('/api/ocr/results/?min_confidence=70&status=completed')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.ocr1, queryset)
    
    def test_invalid_filter_values(self):
        """Test that invalid filter values are ignored gracefully."""
        # Invalid date format
        request = self._make_request('/api/ocr/results/?date_from=invalid-date')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 2)  # Should return all results
        
        # Invalid confidence value
        request = self._make_request('/api/ocr/results/?min_confidence=invalid')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 2)  # Should return all results
        
        # Invalid status
        request = self._make_request('/api/ocr/results/?status=invalid_status')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 2)  # Should return all results
    
    def test_filter_info_metadata(self):
        """Test that filter information is correctly extracted."""
        request = self._make_request('/api/ocr/results/?min_confidence=90&search=test&page_size=10')
        self.view.request = request
        
        filter_info = self.view._get_filter_info()
        
        self.assertEqual(filter_info['min_confidence'], '90')
        self.assertEqual(filter_info['search'], 'test')
        self.assertEqual(filter_info['page_size'], '10')
        self.assertNotIn('date_from', filter_info)
        self.assertNotIn('status', filter_info)
    
    def test_ordering(self):
        """Test that results are ordered by creation date (newest first)."""
        request = self._make_request('/api/ocr/results/')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        results = list(queryset)
        
        # Results should be ordered by -created_at
        self.assertTrue(results[0].created_at >= results[1].created_at)
    
    def test_select_related_optimization(self):
        """Test that queryset uses select_related for performance."""
        request = self._make_request('/api/ocr/results/')
        self.view.request = request
        
        queryset = self.view.get_queryset()
        
        # Check that select_related is applied
        self.assertIn('document', queryset.query.select_related)
        self.assertIn('faktura', queryset.query.select_related)
    
    def test_serializer_class(self):
        """Test that correct serializer is used."""
        self.assertEqual(self.view.serializer_class, OCRResultListSerializer)
    
    def test_pagination_class(self):
        """Test pagination configuration."""
        from faktury.api.views import OCRResultsPagination
        self.assertEqual(self.view.pagination_class, OCRResultsPagination)
        
        # Test pagination settings
        pagination = OCRResultsPagination()
        self.assertEqual(pagination.page_size, 20)
        self.assertEqual(pagination.max_page_size, 100)
        self.assertEqual(pagination.page_size_query_param, 'page_size')