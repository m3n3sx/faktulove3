"""
Test cases for OCR validation API endpoint.
"""
import json
from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from faktury.models import DocumentUpload, OCRResult, Firma, Kontrahent
from faktury.api.views import OCRValidationAPIView


class OCRValidationAPIViewTest(TestCase):
    """Test cases for OCRValidationAPIView."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test company
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
        self.document_upload = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test_invoice.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='completed'
        )
        
        # Create test OCR result
        self.ocr_result = OCRResult.objects.create(
            document=self.document_upload,
            raw_text='Test OCR text',
            extracted_data={
                'numer_faktury': 'FV/2025/001',
                'data_wystawienia': '2025-08-20',
                'data_sprzedazy': '2025-08-20',
                'sprzedawca': {
                    'nazwa': 'Test Seller',
                    'nip': '9876543210'
                },
                'nabywca': {
                    'nazwa': 'Test Buyer',
                    'nip': '1111111111'
                },
                'suma_brutto': 1000.00,
                'pozycje': [
                    {
                        'nazwa': 'Test Product',
                        'ilosc': 1,
                        'cena_netto': 813.01,
                        'vat': '23'
                    }
                ]
            },
            confidence_score=85.0,
            processing_time=10.5,
            processing_status='completed',
            field_confidence={
                'numer_faktury': 90.0,
                'data_wystawienia': 95.0,
                'sprzedawca.nazwa': 80.0,
                'nabywca.nazwa': 85.0,
                'suma_brutto': 85.0
            }
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
        
        # API endpoint URL
        self.url = reverse('api:v1:ocr-validate', kwargs={'result_id': self.ocr_result.id})
    
    def test_successful_validation_without_faktura_creation(self):
        """Test successful OCR validation without creating Faktura."""
        corrections = {
            'numer_faktury': 'FV/2025/001-CORRECTED',
            'sprzedawca.nip': '1111111111'
        }
        
        data = {
            'corrections': corrections,
            'create_faktura': False,
            'validation_notes': 'Corrected invoice number and NIP'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        response_data = response.data['data']
        self.assertEqual(response_data['ocr_result_id'], self.ocr_result.id)
        self.assertIn('numer_faktury', response_data['updated_fields'])
        self.assertIn('sprzedawca.nip', response_data['updated_fields'])
        self.assertEqual(response_data['new_confidence_scores']['numer_faktury'], 100.0)
        self.assertEqual(response_data['new_confidence_scores']['sprzedawca.nip'], 100.0)
        self.assertFalse(response_data['faktura_created'])
        
        # Verify OCR result was updated
        self.ocr_result.refresh_from_db()
        self.assertEqual(self.ocr_result.extracted_data['numer_faktury'], 'FV/2025/001-CORRECTED')
        self.assertEqual(self.ocr_result.extracted_data['sprzedawca']['nip'], '1111111111')
        self.assertEqual(self.ocr_result.field_confidence['numer_faktury'], 100.0)
        self.assertEqual(self.ocr_result.field_confidence['sprzedawca.nip'], 100.0)
    
    def test_successful_validation_with_faktura_creation(self):
        """Test successful OCR validation with Faktura creation."""
        
        corrections = {
            'numer_faktury': 'FV/2025/001-FINAL'
        }
        
        data = {
            'corrections': corrections,
            'create_faktura': True,
            'validation_notes': 'Final validation'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        response_data = response.data['data']
        self.assertTrue(response_data['faktura_created'])
        self.assertIsNotNone(response_data['faktura_id'])
        self.assertIsInstance(response_data['faktura_id'], int)
        
        # Verify Faktura was created
        self.assertIsNotNone(response_data['faktura_id'])
        self.assertIsInstance(response_data['faktura_id'], int)
    
    def test_validation_with_invalid_corrections(self):
        """Test validation with invalid corrections format."""
        data = {
            'corrections': 'invalid_format',  # Should be dict
            'create_faktura': False
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'VALIDATION_ERROR')
    
    def test_validation_with_empty_corrections(self):
        """Test validation with empty corrections."""
        data = {
            'corrections': {},
            'create_faktura': False
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        response_data = response.data['data']
        self.assertEqual(len(response_data['updated_fields']), 0)
    
    def test_validation_nonexistent_ocr_result(self):
        """Test validation of non-existent OCR result."""
        url = reverse('api:v1:ocr-validate', kwargs={'result_id': 99999})
        
        data = {
            'corrections': {'numer_faktury': 'test'},
            'create_faktura': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'OCR_RESULT_NOT_FOUND')
    
    def test_validation_unauthorized_user(self):
        """Test validation by unauthorized user."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Create OCR result for other user
        other_document = DocumentUpload.objects.create(
            user=other_user,
            original_filename='other_invoice.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='completed'
        )
        
        other_ocr_result = OCRResult.objects.create(
            document=other_document,
            raw_text='Other OCR text',
            extracted_data={'numer_faktury': 'FV/2025/002'},
            confidence_score=85.0,
            processing_time=10.5,
            processing_status='completed'
        )
        
        url = reverse('api:v1:ocr-validate', kwargs={'result_id': other_ocr_result.id})
        
        data = {
            'corrections': {'numer_faktury': 'test'},
            'create_faktura': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'OCR_RESULT_NOT_FOUND')
    
    def test_validation_unauthenticated_user(self):
        """Test validation by unauthenticated user."""
        self.client.force_authenticate(user=None)
        
        data = {
            'corrections': {'numer_faktury': 'test'},
            'create_faktura': False
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_nested_field_corrections(self):
        """Test corrections to nested fields."""
        corrections = {
            'sprzedawca.nazwa': 'Updated Seller Name',
            'sprzedawca.nip': '2222222222'
        }
        
        data = {
            'corrections': corrections,
            'create_faktura': False
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify nested corrections were applied
        self.ocr_result.refresh_from_db()
        self.assertEqual(self.ocr_result.extracted_data['sprzedawca']['nazwa'], 'Updated Seller Name')
        self.assertEqual(self.ocr_result.extracted_data['sprzedawca']['nip'], '2222222222')
    
    def test_confidence_score_recalculation(self):
        """Test that confidence scores are recalculated after corrections."""
        original_confidence = self.ocr_result.confidence_score
        
        corrections = {
            'numer_faktury': 'FV/2025/001-UPDATED',
            'suma_brutto': 1500.00
        }
        
        data = {
            'corrections': corrections,
            'create_faktura': False
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify confidence score was recalculated
        self.ocr_result.refresh_from_db()
        self.assertNotEqual(self.ocr_result.confidence_score, original_confidence)
        self.assertEqual(self.ocr_result.field_confidence['numer_faktury'], 100.0)
        self.assertEqual(self.ocr_result.field_confidence['suma_brutto'], 100.0)