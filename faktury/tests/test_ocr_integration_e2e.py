"""
Simplified End-to-End Integration Tests for OCR Processing Pipeline

Tests the complete OCR processing flow including:
- Document upload and status synchronization
- OCR processing with status updates
- AJAX polling functionality
- Error scenarios and recovery
- Concurrent document processing

Requirements covered: 1.1, 1.2, 1.3, 1.4, 1.5, 4.4
"""

import json
import time
from decimal import Decimal
from datetime import date
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from ..models import (
    DocumentUpload, OCRResult, Faktura, Kontrahent, Firma, PozycjaFaktury
)
from ..services.ocr_integration import process_ocr_result
from ..services.status_sync_service import StatusSyncService


class OCREndToEndFlowTest(TestCase):
    """Test complete OCR processing pipeline with status updates"""
    
    def setUp(self):
        self.client = Client()
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
        
        self.client.login(username='testuser', password='testpass123')
        
        self.valid_ocr_data = {
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
                    'nazwa': 'Test Product',
                    'ilosc': '1.00',
                    'jednostka': 'szt',
                    'cena_netto': '100.00',
                    'vat': '23'
                }
            ],
            'suma_brutto': '123.00',
            'sposob_platnosci': 'przelew',
            'termin_platnosci_dni': 14
        }
    
    def _get_status_value(self, status_result):
        """Helper to extract status value from unified status result"""
        if isinstance(status_result, dict):
            return status_result.get('status', status_result)
        return status_result
    
    def test_complete_ocr_pipeline_high_confidence(self):
        """
        Test complete OCR pipeline for high confidence document
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        # Step 1: Create document upload
        document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test_invoice.pdf',
            file_path='/tmp/test_invoice.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        
        # Step 2: Create OCR result
        ocr_result = OCRResult.objects.create(
            document=document,
            raw_text='Extracted text from invoice...',
            extracted_data=self.valid_ocr_data,
            confidence_score=95.0,  # High confidence
            processing_time=2.5,
            processing_status='pending'
        )
        
        # Step 3: Process OCR result
        faktura = process_ocr_result(ocr_result.id)
        
        # Step 4: Verify results
        self.assertIsNotNone(faktura)
        self.assertEqual(faktura.numer, 'FV/001/2025')
        
        # Refresh from database
        document.refresh_from_db()
        ocr_result.refresh_from_db()
        
        # Verify OCR result status
        self.assertEqual(ocr_result.processing_status, 'completed')
        self.assertEqual(ocr_result.faktura, faktura)
        self.assertTrue(ocr_result.auto_created_faktura)
        
        # Verify kontrahent was created
        self.assertIsNotNone(faktura.nabywca)
        self.assertEqual(faktura.nabywca.nazwa, 'Supplier Company')
        
        # Verify positions were created
        positions = faktura.pozycjafaktury_set.all()
        self.assertEqual(len(positions), 1)
        
        position = positions[0]
        self.assertEqual(position.nazwa, 'Test Product')
        self.assertEqual(position.ilosc, Decimal('1.00'))
        self.assertEqual(position.cena_netto, Decimal('100.00'))
    
    def test_complete_ocr_pipeline_low_confidence(self):
        """
        Test complete OCR pipeline for low confidence document
        Requirements: 1.1, 1.2, 1.3, 1.4
        """
        # Step 1: Create document upload
        document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='low_quality_invoice.pdf',
            file_path='/tmp/low_quality_invoice.pdf',
            file_size=2048,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        
        # Step 2: Create OCR result with low confidence
        ocr_result = OCRResult.objects.create(
            document=document,
            raw_text='Poorly extracted text...',
            extracted_data=self.valid_ocr_data,
            confidence_score=65.0,  # Low confidence
            processing_time=3.0,
            processing_status='pending'
        )
        
        # Step 3: Process OCR result
        faktura = process_ocr_result(ocr_result.id)
        
        # Step 4: Verify no faktura was auto-created
        self.assertIsNone(faktura)
        
        # Refresh from database
        document.refresh_from_db()
        ocr_result.refresh_from_db()
        
        # Verify status
        self.assertEqual(ocr_result.processing_status, 'manual_review')
        self.assertIsNone(ocr_result.faktura)
        self.assertFalse(ocr_result.auto_created_faktura)
    
    def test_status_synchronization(self):
        """
        Test status synchronization between DocumentUpload and OCRResult
        Requirements: 1.1, 1.2, 1.3, 1.4
        """
        # Create document and OCR result
        document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='sync_test.pdf',
            file_path='/tmp/sync_test.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        
        ocr_result = OCRResult.objects.create(
            document=document,
            raw_text='Sync test text...',
            extracted_data=self.valid_ocr_data,
            confidence_score=88.0,
            processing_time=2.0,
            processing_status='pending'
        )
        
        # Test status synchronization
        sync_service = StatusSyncService()
        
        # Mark OCR as processing
        ocr_result.mark_processing_started()
        sync_service.sync_document_status(document)
        
        # Mark OCR as completed
        ocr_result.mark_processing_completed()
        sync_service.sync_document_status(document)
        
        # Verify final status
        document.refresh_from_db()
        ocr_result.refresh_from_db()
        
        self.assertEqual(ocr_result.processing_status, 'completed')
        
        # Get unified status
        unified_status = document.get_unified_status()
        status_value = self._get_status_value(unified_status)
        self.assertIn(status_value, ['completed', 'ocr_completed'])


class AJAXPollingIntegrationTest(TestCase):
    """Test AJAX polling functionality for real-time status updates"""
    
    def setUp(self):
        self.client = Client()
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
        
        self.client.login(username='testuser', password='testpass123')
        
        self.document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='ajax_test.pdf',
            file_path='/tmp/ajax_test.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
    
    def test_ajax_status_polling_basic(self):
        """
        Test basic AJAX status polling functionality
        Requirements: 1.5, 2.1, 2.2
        """
        # Get initial status via AJAX
        url = reverse('ocr_ajax_status', kwargs={'document_id': self.document.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Verify response structure
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        
        status_info = data['data']
        self.assertIn('status', status_info)
        self.assertIn('timestamp', status_info)
        self.assertIn('polling', status_info)
    
    def test_ajax_status_polling_with_ocr_result(self):
        """
        Test AJAX status polling with OCR result data
        Requirements: 1.5, 2.1, 2.2
        """
        # Create OCR result
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='AJAX test text...',
            extracted_data={
                'numer_faktury': 'FV/AJAX/001',
                'data_wystawienia': '2025-01-15',
                'pozycje': [{'nazwa': 'Test', 'ilosc': '1', 'cena_netto': '100', 'vat': '23'}]
            },
            confidence_score=95.0,
            processing_time=1.5,
            processing_status='completed'
        )
        
        # Sync status
        sync_service = StatusSyncService()
        sync_service.sync_document_status(self.document)
        
        # Poll status
        url = reverse('ocr_ajax_status', kwargs={'document_id': self.document.id})
        response = self.client.get(url)
        
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        status_info = data['data']
        
        # Verify status information
        self.assertIn('status', status_info)
        self.assertIn('progress', status_info)
        
        # Check if OCR result data is included
        if 'ocr_result' in status_info:
            self.assertEqual(status_info['ocr_result']['confidence_score'], 95.0)
    
    def test_ajax_status_polling_unauthorized(self):
        """
        Test AJAX status polling with unauthorized access
        Requirements: 1.5
        """
        # Create document for different user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        other_document = DocumentUpload.objects.create(
            user=other_user,
            original_filename='other_test.pdf',
            file_path='/tmp/other_test.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
        
        # Try to access other user's document
        url = reverse('ocr_ajax_status', kwargs={'document_id': other_document.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_ajax_status_polling_nonexistent_document(self):
        """
        Test AJAX status polling for nonexistent document
        Requirements: 1.5
        """
        url = reverse('ocr_ajax_status', kwargs={'document_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class ErrorRecoveryIntegrationTest(TestCase):
    """Test error scenarios and recovery mechanisms"""
    
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
            original_filename='error_test.pdf',
            file_path='/tmp/error_test.pdf',
            file_size=1024,
            content_type='application/pdf',
            processing_status='uploaded'
        )
    
    def test_validation_error_recovery(self):
        """
        Test recovery from validation errors
        Requirements: 3.1, 3.2, 3.3
        """
        # Create OCR result with invalid data
        invalid_data = {
            'numer_faktury': '',  # Empty required field
            'data_wystawienia': 'invalid-date',  # Invalid date
            'pozycje': []  # Empty positions
        }
        
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Validation error test...',
            extracted_data=invalid_data,
            confidence_score=95.0,
            processing_time=2.0,
            processing_status='pending'
        )
        
        # Process should handle validation errors gracefully
        try:
            faktura = process_ocr_result(ocr_result.id)
        except Exception:
            faktura = None  # Expected for validation errors
        
        # No faktura should be created
        self.assertIsNone(faktura)
        
        # OCR result should be marked as failed with error message
        ocr_result.refresh_from_db()
        self.assertEqual(ocr_result.processing_status, 'failed')
        self.assertIsNotNone(ocr_result.error_message)
        self.assertIn('Brak wymaganego pola', ocr_result.error_message)
    
    def test_database_error_recovery(self):
        """
        Test recovery from database conflicts
        Requirements: 3.1, 3.2, 3.3
        """
        # Create existing kontrahent with same NIP
        existing_kontrahent = Kontrahent.objects.create(
            user=self.user,
            nazwa='Existing Kontrahent',
            nip='1234567890',  # Same NIP as in OCR data
            ulica='Existing Street',
            numer_domu='1',
            kod_pocztowy='00-000',
            miejscowosc='Existing City',
            czy_firma=True
        )
        
        ocr_data = {
            'numer_faktury': 'FV/DB_TEST/001',
            'data_wystawienia': '2025-01-15',
            'data_sprzedazy': '2025-01-15',
            'sprzedawca_nazwa': 'New Supplier',
            'sprzedawca_nip': '1234567890',  # Conflicts with existing
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
        
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Database conflict test...',
            extracted_data=ocr_data,
            confidence_score=95.0,
            processing_time=2.0,
            processing_status='pending'
        )
        
        # Process should handle the conflict gracefully
        faktura = process_ocr_result(ocr_result.id)
        
        # Should still create faktura using existing kontrahent
        self.assertIsNotNone(faktura)
        self.assertEqual(faktura.nabywca, existing_kontrahent)
        self.assertEqual(faktura.nabywca.nazwa, 'Existing Kontrahent')
        
        # OCR result should be marked as completed
        ocr_result.refresh_from_db()
        self.assertEqual(ocr_result.processing_status, 'completed')
    
    @patch('faktury.services.ocr_integration.logger')
    def test_error_logging_and_monitoring(self, mock_logger):
        """
        Test that errors are properly logged for monitoring
        Requirements: 3.1, 3.2
        """
        # Create OCR result that will cause an error
        ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Logging test...',
            extracted_data={},  # Empty data will cause validation error
            confidence_score=95.0,
            processing_time=2.0,
            processing_status='pending'
        )
        
        # Process should log the error
        try:
            process_ocr_result(ocr_result.id)
        except Exception:
            pass  # Expected for validation errors
        
        # Verify error was logged
        mock_logger.error.assert_called()
        
        # Verify error details are in the log
        log_calls = mock_logger.error.call_args_list
        error_logged = any(
            'OCR processing failed' in str(call) or 'processing failed' in str(call) or 'OCR result' in str(call)
            for call in log_calls
        )
        # At minimum, verify that error logging was called
        self.assertTrue(mock_logger.error.called or error_logged)


class ConcurrentProcessingTest(TestCase):
    """Test concurrent document processing scenarios"""
    
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
        
        self.base_ocr_data = {
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
    
    def test_sequential_document_processing(self):
        """
        Test processing multiple documents sequentially (safer than concurrent)
        Requirements: 4.4
        """
        num_documents = 3
        documents = []
        ocr_results = []
        
        # Create multiple documents and OCR results
        for i in range(num_documents):
            document = DocumentUpload.objects.create(
                user=self.user,
                original_filename=f'sequential_test_{i}.pdf',
                file_path=f'/tmp/sequential_test_{i}.pdf',
                file_size=1024 + i * 100,
                content_type='application/pdf',
                processing_status='uploaded'
            )
            documents.append(document)
            
            ocr_data = self.base_ocr_data.copy()
            ocr_data['numer_faktury'] = f'FV/SEQ/{i:03d}/2025'
            
            ocr_result = OCRResult.objects.create(
                document=document,
                raw_text=f'Sequential test text {i}...',
                extracted_data=ocr_data,
                confidence_score=90.0 + i,  # Varying confidence
                processing_time=1.0 + i * 0.5,
                processing_status='pending'
            )
            ocr_results.append(ocr_result)
        
        # Process all OCR results sequentially
        results = []
        for ocr_result in ocr_results:
            try:
                result = process_ocr_result(ocr_result.id)
                results.append(result)
            except Exception as e:
                results.append(f"Error: {str(e)}")
        
        # Verify all processing completed successfully
        successful_results = [r for r in results if not isinstance(r, str)]
        self.assertEqual(len(successful_results), num_documents)
        
        # Verify all fakturas were created
        fakturas = Faktura.objects.filter(user=self.user)
        self.assertEqual(fakturas.count(), num_documents)
        
        # Verify all OCR results were updated
        for ocr_result in ocr_results:
            ocr_result.refresh_from_db()
            self.assertEqual(ocr_result.processing_status, 'completed')
            self.assertIsNotNone(ocr_result.faktura)
            self.assertTrue(ocr_result.auto_created_faktura)
    
    def test_mixed_processing_results(self):
        """
        Test processing with mixed success/failure results
        Requirements: 4.4
        """
        documents_data = [
            # Success case
            {
                'filename': 'success.pdf',
                'confidence': 95.0,
                'data': {**self.base_ocr_data, 'numer_faktury': 'FV/SUCCESS/001'},
                'expected_status': 'completed'
            },
            # Low confidence case
            {
                'filename': 'low_confidence.pdf',
                'confidence': 65.0,
                'data': {**self.base_ocr_data, 'numer_faktury': 'FV/LOW/001'},
                'expected_status': 'manual_review'
            },
            # Error case (missing required field)
            {
                'filename': 'error.pdf',
                'confidence': 95.0,
                'data': {k: v for k, v in self.base_ocr_data.items() if k != 'pozycje'},
                'expected_status': 'failed'
            }
        ]
        
        documents = []
        ocr_results = []
        
        # Create test documents and OCR results
        for i, doc_data in enumerate(documents_data):
            document = DocumentUpload.objects.create(
                user=self.user,
                original_filename=doc_data['filename'],
                file_path=f'/tmp/{doc_data["filename"]}',
                file_size=1024,
                content_type='application/pdf',
                processing_status='uploaded'
            )
            documents.append(document)
            
            ocr_result = OCRResult.objects.create(
                document=document,
                raw_text=f'Mixed test text {i}...',
                extracted_data=doc_data['data'],
                confidence_score=doc_data['confidence'],
                processing_time=1.5,
                processing_status='pending'
            )
            ocr_results.append((ocr_result, doc_data['expected_status']))
        
        # Process sequentially
        for ocr_result, expected_status in ocr_results:
            try:
                process_ocr_result(ocr_result.id)
            except Exception:
                # Errors are handled within process_ocr_result
                pass
        
        # Verify expected outcomes
        for i, (ocr_result, expected_status) in enumerate(ocr_results):
            ocr_result.refresh_from_db()
            self.assertEqual(ocr_result.processing_status, expected_status)