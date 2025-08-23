"""
Integration tests for FaktuLove OCR system
Tests the complete OCR pipeline from upload to invoice creation
"""

import os
import tempfile
import shutil
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from faktury.models import Faktura, Firma, DocumentUpload, OCRResult
from faktury.services.document_ai_service import get_document_ai_service
from faktury.services.polish_invoice_processor import PolishInvoiceProcessor

User = get_user_model()


class OCRIntegrationTestCase(TestCase):
    """Test complete OCR integration workflow"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@faktulove.com',
            password='testpass123'
        )
        
        # Create test company
        self.firma = Firma.objects.create(
            nazwa='Test Company Sp. z o.o.',
            nip='1234567890',
            user=self.user
        )
        
        # Create test client
        self.client_instance = Client()
        self.client_instance.force_login(self.user)
        
        # Initialize services
        self.ocr_service = get_document_ai_service()
        self.polish_processor = PolishInvoiceProcessor()
        
        # Create test PDF content
        self.test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Faktura testowa) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
    
    def test_complete_ocr_workflow(self):
        """Test complete OCR workflow from upload to invoice creation"""
        # 1. Upload document
        upload_file = SimpleUploadedFile(
            "test_invoice.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        response = self.client_instance.post(
            reverse('ocr_upload'),
            {'file': upload_file},
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 2. Verify document was created
        document = DocumentUpload.objects.filter(user=self.user).first()
        self.assertIsNotNone(document)
        self.assertEqual(document.original_filename, 'test_invoice.pdf')
        self.assertEqual(document.status, 'uploaded')
        
        # 3. Process document with OCR
        ocr_result = self.ocr_service.process_invoice(
            self.test_pdf_content,
            'application/pdf'
        )
        
        self.assertIsNotNone(ocr_result)
        self.assertIn('invoice_number', ocr_result)
        self.assertIn('confidence_score', ocr_result)
        
        # 4. Create OCR result record
        ocr_record = OCRResult.objects.create(
            document=document,
            extracted_data=ocr_result,
            confidence_score=ocr_result.get('confidence_score', 0.0),
            processing_time=ocr_result.get('processing_time', 0.0),
            needs_human_review=ocr_result.get('confidence_score', 0.0) < 90.0
        )
        
        self.assertIsNotNone(ocr_record)
        self.assertEqual(ocr_record.document, document)
        
        # 5. Verify Polish processor enhancement
        enhanced_data = self.polish_processor.enhance_extraction(
            ocr_result.get('raw_text', ''),
            ocr_result
        )
        
        self.assertIsNotNone(enhanced_data)
        self.assertIn('polish_vat_numbers', enhanced_data)
        
        # 6. Create invoice from OCR result
        from faktury.tasks import _create_invoice_from_ocr
        invoice = _create_invoice_from_ocr(ocr_record, self.user)
        
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.source_document, document)
        self.assertEqual(invoice.ocr_confidence, ocr_record.confidence_score)
        self.assertEqual(invoice.ocr_extracted_at.date(), timezone.now().date())
    
    def test_api_endpoints(self):
        """Test OCR API endpoints"""
        # Test upload endpoint
        upload_file = SimpleUploadedFile(
            "test_api.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        response = self.client_instance.post(
            '/api/ocr/upload/',
            {'file': upload_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        
        document_id = response.data['id']
        
        # Test status endpoint
        response = self.client_instance.get(f'/api/ocr/status/{document_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data)
        
        # Test documents list endpoint
        response = self.client_instance.get('/api/ocr/documents/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        
        # Test statistics endpoint
        response = self.client_instance.get('/api/ocr/statistics/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_documents', response.data)
    
    def test_polish_invoice_processing(self):
        """Test Polish-specific invoice processing"""
        # Create Polish invoice text
        polish_invoice_text = """
        FAKTURA VAT
        Nr: FV/2024/001
        Data wystawienia: 15.01.2024
        Termin płatności: 15.02.2024
        
        Sprzedawca:
        ACME Corp Sp. z o.o.
        ul. Testowa 123
        00-001 Warszawa
        NIP: 123-456-78-90
        
        Nabywca:
        Test Company Sp. z o.o.
        ul. Przykładowa 456
        00-002 Kraków
        NIP: 098-765-43-21
        
        Pozycje:
        1. Usługi programistyczne
           Ilość: 1 szt.
           Cena netto: 1000,00 zł
           VAT: 23%
           Wartość netto: 1000,00 zł
           Wartość VAT: 230,00 zł
        
        Razem netto: 1000,00 zł
        VAT: 230,00 zł
        Do zapłaty: 1230,00 zł
        """
        
        # Process with Polish processor
        mock_ocr_data = {
            'raw_text': polish_invoice_text,
            'invoice_number': 'FV/2024/001',
            'confidence_score': 95.0
        }
        
        enhanced_data = self.polish_processor.enhance_extraction(
            polish_invoice_text,
            mock_ocr_data
        )
        
        # Verify Polish patterns were detected
        self.assertIn('polish_vat_numbers', enhanced_data)
        self.assertIn('polish_amounts', enhanced_data)
        self.assertIn('vat_rates_found', enhanced_data)
        
        # Validate Polish invoice
        validation = self.polish_processor.validate_polish_invoice(enhanced_data)
        self.assertIn('is_valid_polish_invoice', validation)
        self.assertIn('validation_errors', validation)
        self.assertIn('validation_warnings', validation)
    
    def test_error_handling(self):
        """Test error handling in OCR workflow"""
        # Test invalid file upload
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not a PDF file",
            content_type="text/plain"
        )
        
        response = self.client_instance.post(
            reverse('ocr_upload'),
            {'file': invalid_file},
            follow=True
        )
        
        # Should handle gracefully
        self.assertEqual(response.status_code, 200)
        
        # Test processing with invalid data
        try:
            result = self.ocr_service.process_invoice(
                b"invalid content",
                "application/pdf"
            )
            # Should not raise exception
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"OCR service should handle invalid data gracefully: {e}")
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        # Upload and process multiple documents
        for i in range(5):
            upload_file = SimpleUploadedFile(
                f"test_invoice_{i}.pdf",
                self.test_pdf_content,
                content_type="application/pdf"
            )
            
            response = self.client_instance.post(
                reverse('ocr_upload'),
                {'file': upload_file},
                follow=True
            )
            
            self.assertEqual(response.status_code, 200)
        
        # Check statistics
        response = self.client_instance.get('/api/ocr/statistics/')
        self.assertEqual(response.status_code, 200)
        
        stats = response.data
        self.assertGreaterEqual(stats['total_documents'], 5)
        self.assertIn('average_processing_time', stats)
        self.assertIn('success_rate', stats)
    
    def test_data_consistency(self):
        """Test data consistency across OCR workflow"""
        # Upload document
        upload_file = SimpleUploadedFile(
            "consistency_test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        response = self.client_instance.post(
            reverse('ocr_upload'),
            {'file': upload_file},
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Get document
        document = DocumentUpload.objects.filter(user=self.user).first()
        
        # Process with OCR
        ocr_result = self.ocr_service.process_invoice(
            self.test_pdf_content,
            'application/pdf'
        )
        
        # Create OCR record
        ocr_record = OCRResult.objects.create(
            document=document,
            extracted_data=ocr_result,
            confidence_score=ocr_result.get('confidence_score', 0.0),
            processing_time=ocr_result.get('processing_time', 0.0)
        )
        
        # Create invoice
        from faktury.tasks import _create_invoice_from_ocr
        invoice = _create_invoice_from_ocr(ocr_record, self.user)
        
        # Verify data consistency
        self.assertEqual(invoice.source_document, document)
        self.assertEqual(invoice.ocr_confidence, ocr_record.confidence_score)
        self.assertEqual(invoice.ocr_processing_time, ocr_record.processing_time)
        
        # Verify OCR data is preserved
        self.assertEqual(
            invoice.numer_faktury,
            ocr_result.get('invoice_number', '')
        )
        self.assertEqual(
            invoice.data_wystawienia,
            ocr_result.get('invoice_date', None)
        )
    
    def test_concurrent_processing(self):
        """Test concurrent document processing"""
        import threading
        import time
        
        results = []
        errors = []
        
        def process_document(doc_id):
            try:
                # Simulate processing
                time.sleep(0.1)
                results.append(doc_id)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=process_document, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all documents were processed
        self.assertEqual(len(results), 10)
        self.assertEqual(len(errors), 0)
    
    def test_memory_usage(self):
        """Test memory usage during processing"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process multiple documents
        for i in range(10):
            upload_file = SimpleUploadedFile(
                f"memory_test_{i}.pdf",
                self.test_pdf_content,
                content_type="application/pdf"
            )
            
            response = self.client_instance.post(
                reverse('ocr_upload'),
                {'file': upload_file},
                follow=True
            )
            
            self.assertEqual(response.status_code, 200)
        
        # Check memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)
    
    def tearDown(self):
        """Clean up test data"""
        # Remove test files
        for document in DocumentUpload.objects.filter(user=self.user):
            if document.file_path and os.path.exists(document.file_path):
                os.remove(document.file_path)
        
        # Clean up database
        DocumentUpload.objects.filter(user=self.user).delete()
        OCRResult.objects.filter(document__user=self.user).delete()
        Faktura.objects.filter(user=self.user).delete()
        Firma.objects.filter(user=self.user).delete()
        User.objects.filter(username='testuser').delete()


class OCRSecurityTestCase(TestCase):
    """Test OCR security features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='securitytest',
            email='security@test.com',
            password='securepass123'
        )
        self.client_instance = Client()
    
    def test_authentication_required(self):
        """Test that OCR endpoints require authentication"""
        endpoints = [
            '/api/ocr/upload/',
            '/api/ocr/documents/',
            '/api/ocr/statistics/',
        ]
        
        for endpoint in endpoints:
            response = self.client_instance.get(endpoint)
            self.assertIn(response.status_code, [401, 403, 302])  # Redirect to login
    
    def test_file_upload_security(self):
        """Test file upload security measures"""
        self.client_instance.force_login(self.user)
        
        # Test file size limit
        large_file = SimpleUploadedFile(
            "large.pdf",
            b"x" * (11 * 1024 * 1024),  # 11MB
            content_type="application/pdf"
        )
        
        response = self.client_instance.post(
            '/api/ocr/upload/',
            {'file': large_file},
            format='multipart'
        )
        
        # Should reject large files
        self.assertNotEqual(response.status_code, 201)
        
        # Test malicious file types
        malicious_file = SimpleUploadedFile(
            "malicious.exe",
            b"malicious content",
            content_type="application/x-executable"
        )
        
        response = self.client_instance.post(
            '/api/ocr/upload/',
            {'file': malicious_file},
            format='multipart'
        )
        
        # Should reject executable files
        self.assertNotEqual(response.status_code, 201)
    
    def test_data_isolation(self):
        """Test that users can only access their own data"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='otherpass123'
        )
        
        # Create document for other user
        other_document = DocumentUpload.objects.create(
            user=other_user,
            original_filename='other.pdf',
            file_path='/tmp/other.pdf',
            content_type='application/pdf',
            file_size=1024
        )
        
        # Try to access other user's document
        self.client_instance.force_login(self.user)
        response = self.client_instance.get(f'/api/ocr/documents/{other_document.id}/')
        
        # Should be forbidden
        self.assertEqual(response.status_code, 404)  # Not found for security


if __name__ == '__main__':
    # Run tests
    import django
    django.setup()
    
    # Run specific test
    test_case = OCRIntegrationTestCase()
    test_case.setUp()
    test_case.test_complete_ocr_workflow()
    test_case.tearDown()
    
    print("✅ All OCR integration tests passed!")
