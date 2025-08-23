#!/usr/bin/env python3
"""
Test script for OCR validation API endpoint implementation.
This script tests the completed OCR validation API methods.
"""

import os
import sys

# Setup Django environment before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')

import django
django.setup()

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import Mock, patch, MagicMock

from faktury.models import DocumentUpload, OCRResult, OCRValidation, Firma
from faktury.api.views import OCRValidationAPIView
from faktury.api.serializers import OCRValidationSerializer
from rest_framework.test import APIRequestFactory
import json


class TestOCRValidationAPI:
    """Test class for OCR validation API implementation."""
    
    def __init__(self):
        self.factory = APIRequestFactory()
        self.view = OCRValidationAPIView()
        self.setup_test_data()
    
    def setup_test_data(self):
        """Setup test data for validation tests."""
        # Create or get test user
        self.user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        
        # Create or get test company
        self.firma, created = Firma.objects.get_or_create(
            user=self.user,
            defaults={
                'nazwa': 'Test Company',
                'nip': '1234567890',
                'ulica': 'Test Street',
                'numer_domu': '123',
                'kod_pocztowy': '00-000',
                'miejscowosc': 'Test City'
            }
        )
        
        # Create test document upload
        self.document_upload = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test_invoice.pdf',
            file_path='test/path/test_invoice.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='completed'
        )
        
        # Create test OCR result
        self.ocr_result = OCRResult.objects.create(
            document=self.document_upload,
            extracted_data={
                'numer_faktury': 'FV/2025/001',
                'data_wystawienia': '2025-08-20',
                'sprzedawca': {
                    'nazwa': 'Test Seller',
                    'nip': '9876543210'
                },
                'suma_brutto': 1000.00,
                'pozycje': [
                    {
                        'nazwa': 'Test Service',
                        'cena_netto': 800.00,
                        'ilosc': 1
                    }
                ]
            },
            field_confidence={
                'numer_faktury': 95.5,
                'data_wystawienia': 88.2,
                'sprzedawca': 75.0,
                'suma_brutto': 92.1
            },
            confidence_score=87.7,
            processing_status='completed'
        )
    
    def test_apply_corrections(self):
        """Test the _apply_corrections method."""
        print("Testing _apply_corrections method...")
        
        corrections = {
            'numer_faktury': 'FV/2025/001-CORRECTED',
            'sprzedawca.nip': '1111111111',
            'pozycje.0.cena_netto': 900.00
        }
        
        # Test the method
        updated_fields = self.view._apply_corrections(self.ocr_result, corrections)
        
        # Verify results
        assert 'numer_faktury' in updated_fields
        assert 'sprzedawca.nip' in updated_fields
        assert 'pozycje.0.cena_netto' in updated_fields
        
        # Check that data was actually updated
        assert self.ocr_result.extracted_data['numer_faktury'] == 'FV/2025/001-CORRECTED'
        assert self.ocr_result.extracted_data['sprzedawca']['nip'] == '1111111111'
        assert self.ocr_result.extracted_data['pozycje'][0]['cena_netto'] == 900.00
        
        print("✓ _apply_corrections method works correctly")
    
    def test_update_confidence_scores(self):
        """Test the _update_confidence_scores method."""
        print("Testing _update_confidence_scores method...")
        
        updated_fields = ['numer_faktury', 'sprzedawca.nip']
        
        # Test the method
        new_scores = self.view._update_confidence_scores(self.ocr_result, updated_fields)
        
        # Verify results
        assert new_scores['numer_faktury'] == 100.0
        assert new_scores['sprzedawca.nip'] == 100.0
        assert self.ocr_result.field_confidence['numer_faktury'] == 100.0
        assert self.ocr_result.field_confidence['sprzedawca.nip'] == 100.0
        
        # Check that overall confidence was recalculated
        assert self.ocr_result.confidence_score > 87.7  # Should be higher now
        
        print("✓ _update_confidence_scores method works correctly")
    
    def test_create_validation_record(self):
        """Test the _create_validation_record method."""
        print("Testing _create_validation_record method...")
        
        corrections = {'numer_faktury': 'FV/2025/001-CORRECTED'}
        notes = 'Test validation notes'
        
        # Test the method
        validation_record = self.view._create_validation_record(
            self.ocr_result, corrections, notes, self.user
        )
        
        # Verify results
        assert validation_record is not None
        assert validation_record.ocr_result == self.ocr_result
        assert validation_record.validated_by == self.user
        assert validation_record.corrections_made == corrections
        assert validation_record.validation_notes == notes
        
        print("✓ _create_validation_record method works correctly")
    
    def test_create_faktura_from_result(self):
        """Test the _create_faktura_from_result method."""
        print("Testing _create_faktura_from_result method...")
        
        # Mock the request user
        self.view.request = Mock()
        self.view.request.user = self.user
        
        # Mock the OCR integration service
        with patch('faktury.services.ocr_integration.create_faktura_from_ocr_manual') as mock_create:
            # Create a mock Faktura
            mock_faktura = Mock()
            mock_faktura.id = 123
            mock_faktura.numer = 'FV/2025/001'
            mock_faktura.status = 'created'
            mock_create.return_value = mock_faktura
            
            # Test the method
            result = self.view._create_faktura_from_result(self.ocr_result)
            
            # Verify results
            assert result is not None
            assert result['id'] == 123
            assert result['number'] == 'FV/2025/001'
            assert result['status'] == 'created'
            
            print("✓ _create_faktura_from_result method works correctly")
    
    def test_get_validation_suggestions(self):
        """Test the _get_validation_suggestions method."""
        print("Testing _get_validation_suggestions method...")
        
        # Set low confidence for sprzedawca to trigger suggestion
        self.ocr_result.field_confidence['sprzedawca'] = 50.0
        
        # Test the method
        suggestions = self.view._get_validation_suggestions(self.ocr_result)
        
        # Verify results
        assert len(suggestions) > 0
        sprzedawca_suggestion = next((s for s in suggestions if s['field'] == 'sprzedawca'), None)
        assert sprzedawca_suggestion is not None
        assert sprzedawca_suggestion['priority'] == 'high'
        assert sprzedawca_suggestion['confidence'] == 50.0
        
        print("✓ _get_validation_suggestions method works correctly")
    
    def test_get_review_priorities(self):
        """Test the _get_review_priorities method."""
        print("Testing _get_review_priorities method...")
        
        # Test the method
        priorities = self.view._get_review_priorities(self.ocr_result)
        
        # Verify results
        assert 'high' in priorities
        assert 'medium' in priorities
        assert 'low' in priorities
        
        # Check that fields are categorized correctly
        total_fields = len(priorities['high']) + len(priorities['medium']) + len(priorities['low'])
        assert total_fields > 0
        
        print("✓ _get_review_priorities method works correctly")
    
    def test_serializer_validation(self):
        """Test the OCRValidationSerializer."""
        print("Testing OCRValidationSerializer...")
        
        # Test valid data
        valid_data = {
            'corrections': {
                'numer_faktury': 'FV/2025/001-CORRECTED',
                'sprzedawca.nip': '1111111111'
            },
            'create_faktura': True,
            'validation_notes': 'Test validation'
        }
        
        serializer = OCRValidationSerializer(data=valid_data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        
        # Test invalid data
        invalid_data = {
            'corrections': 'not a dict',  # Should be a dictionary
            'create_faktura': 'not a boolean'  # Should be a boolean
        }
        
        serializer = OCRValidationSerializer(data=invalid_data)
        assert not serializer.is_valid()
        
        print("✓ OCRValidationSerializer works correctly")
    
    def run_all_tests(self):
        """Run all tests."""
        print("Starting OCR Validation API tests...\n")
        
        try:
            self.test_apply_corrections()
            self.test_update_confidence_scores()
            self.test_create_validation_record()
            self.test_create_faktura_from_result()
            self.test_get_validation_suggestions()
            self.test_get_review_priorities()
            self.test_serializer_validation()
            
            print("\n✅ All OCR Validation API tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main test function."""
    tester = TestOCRValidationAPI()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 OCR Validation API implementation is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 OCR Validation API implementation has issues!")
        sys.exit(1)


if __name__ == '__main__':
    main()