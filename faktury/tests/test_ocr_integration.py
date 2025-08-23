"""
Unit tests for OCR integration functionality

Tests the integration between OCR results and Faktura creation,
including validation, automatic processing, and error handling.
"""

import json
from decimal import Decimal
from datetime import date, datetime
from unittest.mock import patch, MagicMock

from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import (
    DocumentUpload, OCRResult, Faktura, Kontrahent, Firma, PozycjaFaktury
)
from ..services.ocr_integration import (
    OCRDataValidator, FakturaCreator, OCRIntegrationError,
    process_ocr_result, create_faktura_from_ocr_manual, get_ocr_processing_stats
)


class OCRDataValidatorTest(TestCase):
    """Test OCR data validation"""
    
    def setUp(self):
        self.valid_data = {
            'numer_faktury': 'FV/001/2025',
            'data_wystawienia': '2025-01-15',
            'data_sprzedazy': '2025-01-15',
            'sprzedawca_nazwa': 'Test Sp. z o.o.',
            'sprzedawca_nip': '1234567890',
            'nabywca_nazwa': 'Buyer Company',
            'pozycje': [
                {
                    'nazwa': 'Test Product',
                    'ilosc': '1.00',
                    'cena_netto': '100.00',
                    'vat': '23'
                }
            ],
            'suma_brutto': '123.00'
        }
    
    def test_valid_data_passes_validation(self):
        """Test that valid data passes validation"""
        is_valid, errors = OCRDataValidator.validate_ocr_data(self.valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_missing_required_fields_fails_validation(self):
        """Test that missing required fields fail validation"""
        invalid_data = self.valid_data.copy()
        del invalid_data['numer_faktury']
        del invalid_data['pozycje']
        
        is_valid, errors = OCRDataValidator.validate_ocr_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Brak wymaganego pola: numer_faktury', errors)
        self.assertIn('Brak wymaganego pola: pozycje', errors)
    
    def test_invalid_date_fails_validation(self):
        """Test that invalid dates fail validation"""
        invalid_data = self.valid_data.copy()
        invalid_data['data_wystawienia'] = 'invalid-date'
        
        is_valid, errors = OCRDataValidator.validate_ocr_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Nieprawidłowa data wystawienia', errors)
    
    def test_empty_positions_fails_validation(self):
        """Test that empty positions fail validation"""
        invalid_data = self.valid_data.copy()
        invalid_data['pozycje'] = []
        
        is_valid, errors = OCRDataValidator.validate_ocr_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Brak pozycji na fakturze', errors)
    
    def test_invalid_position_data_fails_validation(self):
        """Test that invalid position data fails validation"""
        invalid_data = self.valid_data.copy()
        invalid_data['pozycje'] = [
            {
                'nazwa': 'Test Product',
                'ilosc': 'invalid',
                'cena_netto': '100.00',
                'vat': '23'
            }
        ]
        
        is_valid, errors = OCRDataValidator.validate_ocr_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Pozycja 1: nieprawidłowa wartość ilosc', errors)


class FakturaCreatorTest(TestCase):
    """Test Faktura creation from OCR data"""
    
    def setUp(self):
        # Create test user and company
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Company',
            nip='9876543210',
            ulica='Test Street',
            numer_domu='1',
            kod_pocztowy='00-000',
            miejscowosc='Test City'
        )
        
        # Create test document and OCR result
        self.document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test_invoice.pdf',
            file_path='/tmp/test_invoice.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='completed'
        )
        
        self.ocr_data = {
            'numer_faktury': 'FV/001/2025',
            'data_wystawienia': '2025-01-15',
            'data_sprzedazy': '2025-01-15',
            'sprzedawca_nazwa': 'Supplier Company',
            'sprzedawca_nip': '1234567890',
            'sprzedawca_ulica': 'Supplier Street',
            'sprzedawca_numer_domu': '10',
            'sprzedawca_kod_pocztowy': '11-111',
            'sprzedawca_miejscowosc': 'Supplier City',
            'nabywca_nazwa': 'Test Company',
            'pozycje': [
                {
                    'nazwa': 'Test Product 1',
                    'ilosc': '2.00',
                    'jednostka': 'szt',
                    'cena_netto': '50.00',
                    'vat': '23'
                },
                {
                    'nazwa': 'Test Product 2',
                    'ilosc': '1.00',
                    'jednostka': 'szt',
                    'cena_netto': '100.00',
                    'vat': '8'
                }
            ],
            'suma_brutto': '231.00',
            'sposob_platnosci': 'przelew',
            'termin_platnosci_dni': 14
        }
        
        self.ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Raw OCR text...',
            extracted_data=self.ocr_data,
            confidence_score=95.0,
            processing_time=2.5
        )
    
    def test_create_faktura_from_ocr_success(self):
        """Test successful Faktura creation from OCR"""
        creator = FakturaCreator(self.user)
        faktura = creator.create_from_ocr(self.ocr_result)
        
        # Check faktura fields
        self.assertEqual(faktura.numer, 'FV/001/2025')
        self.assertEqual(faktura.data_wystawienia, date(2025, 1, 15))
        self.assertEqual(faktura.data_sprzedazy, date(2025, 1, 15))
        self.assertEqual(faktura.sprzedawca, self.firma)
        self.assertEqual(faktura.typ_faktury, 'koszt')
        self.assertEqual(faktura.sposob_platnosci, 'przelew')
        self.assertEqual(faktura.waluta, 'PLN')
        self.assertTrue(faktura.uwagi.startswith('Utworzona automatycznie z OCR'))
        
        # Check OCR fields
        self.assertEqual(faktura.source_document, self.document)
        self.assertEqual(faktura.ocr_confidence, 95.0)
        self.assertEqual(faktura.ocr_processing_time, 2.5)
        self.assertIsNotNone(faktura.ocr_extracted_at)
        self.assertFalse(faktura.manual_verification_required)  # High confidence
        
        # Check kontrahent was created
        self.assertIsNotNone(faktura.nabywca)
        self.assertEqual(faktura.nabywca.nazwa, 'Supplier Company')
        self.assertEqual(faktura.nabywca.nip, '1234567890')
        
        # Check positions were created
        positions = faktura.pozycjafaktury_set.all()
        self.assertEqual(len(positions), 2)
        
        pos1 = positions[0]
        self.assertEqual(pos1.nazwa, 'Test Product 1')
        self.assertEqual(pos1.ilosc, Decimal('2.00'))
        self.assertEqual(pos1.cena_netto, Decimal('50.00'))
        self.assertEqual(pos1.vat, '23')
        
        # Check OCR result was updated
        self.ocr_result.refresh_from_db()
        self.assertEqual(self.ocr_result.faktura, faktura)
        self.assertTrue(self.ocr_result.auto_created_faktura)
        self.assertEqual(self.ocr_result.processing_status, 'completed')
    
    def test_create_faktura_with_existing_kontrahent(self):
        """Test Faktura creation when kontrahent already exists"""
        # Create existing kontrahent
        existing_kontrahent = Kontrahent.objects.create(
            user=self.user,
            nazwa='Existing Supplier',
            nip='1234567890',  # Same NIP as in OCR data
            ulica='Old Street',
            numer_domu='5',
            kod_pocztowy='22-222',
            miejscowosc='Old City',
            czy_firma=True
        )
        
        creator = FakturaCreator(self.user)
        faktura = creator.create_from_ocr(self.ocr_result)
        
        # Should use existing kontrahent
        self.assertEqual(faktura.nabywca, existing_kontrahent)
        self.assertEqual(faktura.nabywca.nazwa, 'Existing Supplier')  # Original name preserved
    
    def test_create_faktura_invalid_data_raises_error(self):
        """Test that invalid OCR data raises OCRIntegrationError"""
        # Create OCR result with invalid data
        invalid_data = self.ocr_data.copy()
        del invalid_data['numer_faktury']  # Remove required field
        
        invalid_ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Invalid OCR text...',
            extracted_data=invalid_data,
            confidence_score=95.0,
            processing_time=2.5
        )
        
        creator = FakturaCreator(self.user)
        
        with self.assertRaises(OCRIntegrationError):
            creator.create_from_ocr(invalid_ocr_result)
        
        # Check OCR result was marked as failed
        invalid_ocr_result.refresh_from_db()
        self.assertEqual(invalid_ocr_result.processing_status, 'failed')
        self.assertIsNotNone(invalid_ocr_result.error_message)
    
    def test_create_faktura_without_company_raises_error(self):
        """Test that user without company raises error"""
        # Create user without company
        user_no_company = User.objects.create_user(
            username='nocompany',
            email='nocompany@example.com',
            password='testpass123'
        )
        
        creator = FakturaCreator(user_no_company)
        
        with self.assertRaises(OCRIntegrationError) as cm:
            creator.create_from_ocr(self.ocr_result)
        
        self.assertIn('nie ma przypisanej firmy', str(cm.exception))


class OCRIntegrationServiceTest(TestCase):
    """Test OCR integration service functions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Company',
            nip='9876543210',
            ulica='Test Street',
            numer_domu='1',
            kod_pocztowy='00-000',
            miejscowosc='Test City'
        )
        
        self.document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test_invoice.pdf',
            file_path='/tmp/test_invoice.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='completed'
        )
        
        self.valid_ocr_data = {
            'numer_faktury': 'FV/001/2025',
            'data_wystawienia': '2025-01-15',
            'data_sprzedazy': '2025-01-15',
            'sprzedawca_nazwa': 'Supplier Company',
            'sprzedawca_nip': '1234567890',
            'nabywca_nazwa': 'Test Company',
            'pozycje': [
                {
                    'nazwa': 'Test Product',
                    'ilosc': '1.00',
                    'cena_netto': '100.00',
                    'vat': '23'
                }
            ]
        }
    
    def test_process_ocr_result_high_confidence_auto_creates(self):
        """Test that high confidence OCR results auto-create Faktura"""
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='High confidence OCR text...',
            extracted_data=self.valid_ocr_data,
            confidence_score=95.0,  # High confidence
            processing_time=2.0
        )
        
        faktura = process_ocr_result(ocr_result.id)
        
        self.assertIsNotNone(faktura)
        self.assertEqual(faktura.numer, 'FV/001/2025')
        
        ocr_result.refresh_from_db()
        self.assertEqual(ocr_result.processing_status, 'completed')
        self.assertEqual(ocr_result.faktura, faktura)
        self.assertTrue(ocr_result.auto_created_faktura)
    
    def test_process_ocr_result_low_confidence_manual_review(self):
        """Test that low confidence OCR results require manual review"""
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Low confidence OCR text...',
            extracted_data=self.valid_ocr_data,
            confidence_score=70.0,  # Low confidence
            processing_time=2.0
        )
        
        faktura = process_ocr_result(ocr_result.id)
        
        self.assertIsNone(faktura)
        
        ocr_result.refresh_from_db()
        self.assertEqual(ocr_result.processing_status, 'manual_review')
        self.assertIsNone(ocr_result.faktura)
        self.assertFalse(ocr_result.auto_created_faktura)
    
    def test_process_ocr_result_medium_confidence_no_auto_create(self):
        """Test that medium confidence OCR results don't auto-create but complete"""
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Medium confidence OCR text...',
            extracted_data=self.valid_ocr_data,
            confidence_score=85.0,  # Medium confidence
            processing_time=2.0
        )
        
        faktura = process_ocr_result(ocr_result.id)
        
        self.assertIsNone(faktura)
        
        ocr_result.refresh_from_db()
        self.assertEqual(ocr_result.processing_status, 'completed')
        self.assertIsNone(ocr_result.faktura)
        self.assertFalse(ocr_result.auto_created_faktura)
    
    def test_process_ocr_result_already_has_faktura(self):
        """Test processing OCR result that already has associated Faktura"""
        # Create existing faktura
        existing_faktura = Faktura.objects.create(
            user=self.user,
            numer='EXISTING/001/2025',
            data_wystawienia=date.today(),
            data_sprzedazy=date.today(),
            miejsce_wystawienia='Test City',
            sprzedawca=self.firma,
            nabywca=Kontrahent.objects.create(
                user=self.user,
                nazwa='Test Kontrahent',
                ulica='Test Street',
                numer_domu='1',
                kod_pocztowy='00-000',
                miejscowosc='Test City'
            ),
            termin_platnosci=date.today()
        )
        
        ocr_result = OCRResult.objects.create(
            document=self.document,
            faktura=existing_faktura,  # Already has faktura
            raw_text='OCR text...',
            extracted_data=self.valid_ocr_data,
            confidence_score=95.0,
            processing_time=2.0
        )
        
        faktura = process_ocr_result(ocr_result.id)
        
        self.assertEqual(faktura, existing_faktura)
    
    def test_process_ocr_result_nonexistent_id(self):
        """Test processing non-existent OCR result ID"""
        faktura = process_ocr_result(99999)  # Non-existent ID
        self.assertIsNone(faktura)
    
    def test_create_faktura_from_ocr_manual_success(self):
        """Test manual Faktura creation from OCR"""
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Manual OCR text...',
            extracted_data=self.valid_ocr_data,
            confidence_score=75.0,  # Would normally require manual review
            processing_time=2.0,
            processing_status='manual_review'
        )
        
        faktura = create_faktura_from_ocr_manual(ocr_result.id, self.user)
        
        self.assertIsNotNone(faktura)
        self.assertEqual(faktura.numer, 'FV/001/2025')
        
        ocr_result.refresh_from_db()
        self.assertEqual(ocr_result.faktura, faktura)
        self.assertTrue(ocr_result.auto_created_faktura)
    
    def test_create_faktura_from_ocr_manual_already_has_faktura(self):
        """Test manual creation when OCR result already has Faktura"""
        existing_faktura = Faktura.objects.create(
            user=self.user,
            numer='EXISTING/001/2025',
            data_wystawienia=date.today(),
            data_sprzedazy=date.today(),
            miejsce_wystawienia='Test City',
            sprzedawca=self.firma,
            nabywca=Kontrahent.objects.create(
                user=self.user,
                nazwa='Test Kontrahent',
                ulica='Test Street',
                numer_domu='1',
                kod_pocztowy='00-000',
                miejscowosc='Test City'
            ),
            termin_platnosci=date.today()
        )
        
        ocr_result = OCRResult.objects.create(
            document=self.document,
            faktura=existing_faktura,
            raw_text='OCR text...',
            extracted_data=self.valid_ocr_data,
            confidence_score=75.0,
            processing_time=2.0
        )
        
        with self.assertRaises(OCRIntegrationError) as cm:
            create_faktura_from_ocr_manual(ocr_result.id, self.user)
        
        self.assertIn('już ma przypisaną fakturę', str(cm.exception))
    
    def test_get_ocr_processing_stats(self):
        """Test OCR processing statistics generation"""
        # Create various OCR results
        OCRResult.objects.create(
            document=self.document,
            raw_text='Auto-created OCR...',
            extracted_data=self.valid_ocr_data,
            confidence_score=95.0,
            processing_time=2.0,
            processing_status='completed',
            auto_created_faktura=True
        )
        
        document2 = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test2.pdf',
            file_path='/tmp/test2.pdf',
            file_size=2048,
            content_type='application/pdf'
        )
        
        OCRResult.objects.create(
            document=document2,
            raw_text='Manual review OCR...',
            extracted_data=self.valid_ocr_data,
            confidence_score=70.0,
            processing_time=3.0,
            processing_status='manual_review',
            auto_created_faktura=False
        )
        
        stats = get_ocr_processing_stats(self.user)
        
        self.assertEqual(stats['total_processed'], 2)
        self.assertEqual(stats['auto_created_count'], 1)
        self.assertEqual(stats['manual_review_count'], 1)
        self.assertEqual(stats['failed_count'], 0)
        self.assertEqual(stats['success_rate'], 50.0)
        self.assertEqual(stats['manual_review_rate'], 50.0)
        self.assertEqual(stats['failure_rate'], 0.0)


class OCRModelTest(TestCase):
    """Test OCR model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test.pdf',
            file_path='/tmp/test.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
    
    def test_ocr_result_confidence_properties(self):
        """Test OCR result confidence-based properties"""
        # High confidence
        high_confidence = OCRResult.objects.create(
            document=self.document,
            raw_text='High confidence text',
            extracted_data={},
            confidence_score=95.0,
            processing_time=2.0
        )
        
        self.assertFalse(high_confidence.needs_human_review)
        self.assertTrue(high_confidence.can_auto_create_faktura)
        self.assertEqual(high_confidence.confidence_level, 'high')
        
        # Medium confidence
        medium_confidence = OCRResult.objects.create(
            document=self.document,
            raw_text='Medium confidence text',
            extracted_data={},
            confidence_score=85.0,
            processing_time=2.0
        )
        
        self.assertFalse(medium_confidence.needs_human_review)
        self.assertFalse(medium_confidence.can_auto_create_faktura)
        self.assertEqual(medium_confidence.confidence_level, 'medium')
        
        # Low confidence
        low_confidence = OCRResult.objects.create(
            document=self.document,
            raw_text='Low confidence text',
            extracted_data={},
            confidence_score=70.0,
            processing_time=2.0
        )
        
        self.assertTrue(low_confidence.needs_human_review)
        self.assertFalse(low_confidence.can_auto_create_faktura)
        self.assertEqual(low_confidence.confidence_level, 'low')
    
    def test_ocr_result_status_methods(self):
        """Test OCR result status management methods"""
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Test text',
            extracted_data={},
            confidence_score=85.0,
            processing_time=2.0
        )
        
        # Test mark_processing_started
        ocr_result.mark_processing_started()
        self.assertEqual(ocr_result.processing_status, 'processing')
        
        # Test mark_processing_completed
        ocr_result.mark_processing_completed()
        self.assertEqual(ocr_result.processing_status, 'completed')
        
        # Test mark_processing_failed
        error_msg = 'Test error message'
        ocr_result.mark_processing_failed(error_msg)
        self.assertEqual(ocr_result.processing_status, 'failed')
        self.assertEqual(ocr_result.error_message, error_msg)
        
        # Test mark_manual_review_required
        ocr_result.mark_manual_review_required()
        self.assertEqual(ocr_result.processing_status, 'manual_review')
    
    @patch('faktury.services.ocr_integration.process_ocr_result')
    def test_ocr_result_save_triggers_processing(self, mock_process):
        """Test that saving new OCR result triggers processing"""
        # Mock the process function to avoid actual processing
        mock_process.return_value = None
        
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Test text',
            extracted_data={},
            confidence_score=85.0,
            processing_time=2.0
        )
        
        # Should trigger processing for new OCR result
        mock_process.assert_called_once_with(ocr_result.id)


class OCRSignalsTest(TransactionTestCase):
    """Test OCR integration signals"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test.pdf',
            file_path='/tmp/test.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
    
    @patch('faktury.tasks.process_ocr_result_task.delay')
    def test_document_completion_triggers_ocr_processing(self, mock_task):
        """Test that document completion triggers OCR processing"""
        # Create OCR result
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Test text',
            extracted_data={},
            confidence_score=85.0,
            processing_time=2.0,
            processing_status='pending'
        )
        
        # Mark document as completed (should trigger signal)
        self.document.processing_status = 'completed'
        self.document.save()
        
        # Should trigger Celery task
        mock_task.assert_called_once_with(ocr_result.id)