"""
Performance tests for FaktuLove OCR system
Tests processing speed, accuracy, and system load
"""

import time
import threading
import concurrent.futures
import statistics
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from faktury.models import DocumentUpload, OCRResult, Faktura, Firma
from faktury.services.document_ai_service import get_document_ai_service
from faktury.services.polish_invoice_processor import PolishInvoiceProcessor

User = get_user_model()


class OCRPerformanceTestCase(TestCase):
    """Test OCR system performance metrics"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='perftest',
            email='perf@test.com',
            password='perfpass123'
        )
        
        self.firma = Firma.objects.create(
            nazwa='Performance Test Company',
            nip='1234567890',
            user=self.user
        )
        
        self.ocr_service = get_document_ai_service()
        self.polish_processor = PolishInvoiceProcessor()
        
        # Create test PDF content
        self.test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Faktura testowa) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
    
    def test_processing_speed_target(self):
        """Test that processing meets 5-second target"""
        processing_times = []
        
        # Process 10 documents and measure time
        for i in range(10):
            start_time = time.time()
            
            result = self.ocr_service.process_invoice(
                self.test_pdf_content,
                'application/pdf'
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            processing_times.append(processing_time)
            
            # Verify result is valid
            self.assertIsNotNone(result)
            self.assertIn('confidence_score', result)
        
        # Calculate statistics
        avg_time = statistics.mean(processing_times)
        max_time = max(processing_times)
        min_time = min(processing_times)
        
        print(f"Processing times: {processing_times}")
        print(f"Average: {avg_time:.2f}s, Max: {max_time:.2f}s, Min: {min_time:.2f}s")
        
        # Verify performance targets
        self.assertLess(avg_time, 5.0, f"Average processing time {avg_time:.2f}s exceeds 5s target")
        self.assertLess(max_time, 10.0, f"Maximum processing time {max_time:.2f}s exceeds 10s limit")
        
        # Target: 98% of documents processed under 5 seconds
        under_5s = sum(1 for t in processing_times if t < 5.0)
        success_rate = (under_5s / len(processing_times)) * 100
        
        self.assertGreaterEqual(success_rate, 98.0, 
                               f"Success rate {success_rate:.1f}% below 98% target")
    
    def test_concurrent_processing(self):
        """Test concurrent document processing"""
        def process_document(doc_id):
            start_time = time.time()
            
            result = self.ocr_service.process_invoice(
                self.test_pdf_content,
                'application/pdf'
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            return {
                'doc_id': doc_id,
                'processing_time': processing_time,
                'success': result is not None,
                'confidence': result.get('confidence_score', 0.0) if result else 0.0
            }
        
        # Test with 50 concurrent documents (target requirement)
        num_documents = 50
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_doc = {
                executor.submit(process_document, i): i 
                for i in range(num_documents)
            }
            
            for future in concurrent.futures.as_completed(future_to_doc):
                result = future.result()
                results.append(result)
        
        # Verify all documents were processed
        self.assertEqual(len(results), num_documents)
        
        # Calculate performance metrics
        processing_times = [r['processing_time'] for r in results]
        success_count = sum(1 for r in results if r['success'])
        avg_confidence = statistics.mean([r['confidence'] for r in results])
        
        avg_time = statistics.mean(processing_times)
        max_time = max(processing_times)
        
        print(f"Concurrent processing results:")
        print(f"Documents processed: {len(results)}")
        print(f"Success rate: {(success_count/num_documents)*100:.1f}%")
        print(f"Average processing time: {avg_time:.2f}s")
        print(f"Maximum processing time: {max_time:.2f}s")
        print(f"Average confidence: {avg_confidence:.1f}%")
        
        # Verify concurrent processing targets
        self.assertEqual(success_count, num_documents, 
                        "All documents should be processed successfully")
        self.assertLess(avg_time, 5.0, 
                       f"Average concurrent processing time {avg_time:.2f}s exceeds 5s target")
        self.assertGreaterEqual(avg_confidence, 90.0, 
                               f"Average confidence {avg_confidence:.1f}% below 90% target")
    
    def test_accuracy_target(self):
        """Test that accuracy meets 98% target"""
        # Create test data with known expected values
        test_cases = [
            {
                'input': {
                    'invoice_number': 'FV/2024/001',
                    'total_amount': '1230.00',
                    'supplier_name': 'ACME Corp Sp. z o.o.',
                    'supplier_nip': '1234567890'
                },
                'expected_fields': ['invoice_number', 'total_amount', 'supplier_name', 'supplier_nip']
            },
            {
                'input': {
                    'invoice_number': 'FV/2024/002',
                    'total_amount': '567.89',
                    'buyer_name': 'Test Company Ltd.',
                    'buyer_nip': '0987654321'
                },
                'expected_fields': ['invoice_number', 'total_amount', 'buyer_name', 'buyer_nip']
            }
        ]
        
        accuracy_scores = []
        
        for test_case in test_cases:
            # Simulate OCR processing
            result = self.ocr_service.process_invoice(
                self.test_pdf_content,
                'application/pdf'
            )
            
            # Check field extraction accuracy
            expected_fields = test_case['expected_fields']
            extracted_fields = [field for field in expected_fields if field in result]
            
            field_accuracy = len(extracted_fields) / len(expected_fields)
            accuracy_scores.append(field_accuracy)
            
            # Verify confidence score
            confidence = result.get('confidence_score', 0.0)
            self.assertGreaterEqual(confidence, 85.0, 
                                   f"Confidence score {confidence} below 85% threshold")
        
        # Calculate overall accuracy
        overall_accuracy = statistics.mean(accuracy_scores) * 100
        
        print(f"Field extraction accuracy: {overall_accuracy:.1f}%")
        
        # Verify accuracy target
        self.assertGreaterEqual(overall_accuracy, 98.0, 
                               f"Overall accuracy {overall_accuracy:.1f}% below 98% target")
    
    def test_memory_usage(self):
        """Test memory usage during processing"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process multiple documents
        for i in range(20):
            result = self.ocr_service.process_invoice(
                self.test_pdf_content,
                'application/pdf'
            )
            self.assertIsNotNone(result)
        
        # Check memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory / 1024 / 1024:.1f}MB -> {final_memory / 1024 / 1024:.1f}MB")
        print(f"Memory increase: {memory_increase / 1024 / 1024:.1f}MB")
        
        # Memory increase should be reasonable (less than 200MB for 20 documents)
        self.assertLess(memory_increase, 200 * 1024 * 1024, 
                       f"Memory increase {memory_increase / 1024 / 1024:.1f}MB exceeds 200MB limit")
    
    def test_polish_processor_performance(self):
        """Test Polish processor performance"""
        polish_text = """
        FAKTURA VAT Nr FV/2024/001
        Data wystawienia: 15.01.2024
        Sprzedawca: ACME Corp Sp. z o.o. NIP: 123-456-78-90
        Nabywca: Test Company Sp. z o.o. NIP: 098-765-43-21
        Do zapłaty: 1230,00 zł
        """
        
        processing_times = []
        
        for i in range(10):
            start_time = time.time()
            
            enhanced_data = self.polish_processor.enhance_extraction(
                polish_text,
                {'raw_text': polish_text}
            )
            
            validation = self.polish_processor.validate_polish_invoice(enhanced_data)
            
            end_time = time.time()
            processing_times.append(end_time - start_time)
            
            # Verify enhancement worked
            self.assertIn('polish_vat_numbers', enhanced_data)
            self.assertIn('is_valid_polish_invoice', validation)
        
        avg_time = statistics.mean(processing_times)
        max_time = max(processing_times)
        
        print(f"Polish processor times: {processing_times}")
        print(f"Average: {avg_time:.3f}s, Max: {max_time:.3f}s")
        
        # Polish processing should be very fast (< 100ms)
        self.assertLess(avg_time, 0.1, 
                       f"Polish processor average time {avg_time:.3f}s exceeds 100ms target")
    
    def test_system_load(self):
        """Test system load under stress"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Monitor system resources during processing
        cpu_usage = []
        memory_usage = []
        
        def process_with_monitoring():
            start_cpu = process.cpu_percent()
            start_memory = process.memory_info().rss
            
            result = self.ocr_service.process_invoice(
                self.test_pdf_content,
                'application/pdf'
            )
            
            end_cpu = process.cpu_percent()
            end_memory = process.memory_info().rss
            
            return {
                'cpu_usage': (start_cpu + end_cpu) / 2,
                'memory_usage': end_memory - start_memory,
                'success': result is not None
            }
        
        # Process documents and monitor resources
        results = []
        for i in range(10):
            result = process_with_monitoring()
            results.append(result)
            cpu_usage.append(result['cpu_usage'])
            memory_usage.append(result['memory_usage'])
        
        avg_cpu = statistics.mean(cpu_usage)
        max_cpu = max(cpu_usage)
        avg_memory = statistics.mean(memory_usage)
        
        print(f"CPU usage: avg={avg_cpu:.1f}%, max={max_cpu:.1f}%")
        print(f"Memory usage: avg={avg_memory / 1024 / 1024:.1f}MB")
        
        # Verify system load is reasonable
        self.assertLess(avg_cpu, 80.0, 
                       f"Average CPU usage {avg_cpu:.1f}% exceeds 80% limit")
        self.assertLess(max_cpu, 95.0, 
                       f"Maximum CPU usage {max_cpu:.1f}% exceeds 95% limit")
        
        # All processing should succeed
        success_count = sum(1 for r in results if r['success'])
        self.assertEqual(success_count, 10, "All documents should be processed successfully")
    
    def test_response_time_target(self):
        """Test API response time targets"""
        from django.test import Client
        
        client = Client()
        client.force_login(self.user)
        
        response_times = []
        
        # Test API endpoints response times
        endpoints = [
            '/api/ocr/statistics/',
            '/api/ocr/documents/',
        ]
        
        for endpoint in endpoints:
            for i in range(5):  # Test each endpoint 5 times
                start_time = time.time()
                
                response = client.get(endpoint)
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                self.assertEqual(response.status_code, 200)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        print(f"API response times: {response_times}")
        print(f"Average: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s")
        
        # API response should be under 100ms
        self.assertLess(avg_response_time, 0.1, 
                       f"Average API response time {avg_response_time:.3f}s exceeds 100ms target")
        self.assertLess(max_response_time, 0.5, 
                       f"Maximum API response time {max_response_time:.3f}s exceeds 500ms limit")
    
    def test_throughput_target(self):
        """Test system throughput (documents per minute)"""
        start_time = time.time()
        
        # Process documents as fast as possible
        documents_processed = 0
        max_documents = 100
        
        while documents_processed < max_documents:
            result = self.ocr_service.process_invoice(
                self.test_pdf_content,
                'application/pdf'
            )
            
            if result is not None:
                documents_processed += 1
            else:
                break
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate throughput
        throughput_dpm = (documents_processed / total_time) * 60  # documents per minute
        
        print(f"Throughput test:")
        print(f"Documents processed: {documents_processed}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Throughput: {throughput_dpm:.1f} documents/minute")
        
        # Target: 1000 documents per minute
        self.assertGreaterEqual(throughput_dpm, 1000, 
                               f"Throughput {throughput_dpm:.1f} dpm below 1000 dpm target")
        
        # All documents should be processed successfully
        self.assertEqual(documents_processed, max_documents, 
                        "All documents should be processed successfully")
    
    def tearDown(self):
        """Clean up test data"""
        DocumentUpload.objects.filter(user=self.user).delete()
        OCRResult.objects.filter(document__user=self.user).delete()
        Faktura.objects.filter(user=self.user).delete()
        Firma.objects.filter(user=self.user).delete()
        User.objects.filter(username='perftest').delete()


if __name__ == '__main__':
    # Run performance tests
    import django
    django.setup()
    
    test_case = OCRPerformanceTestCase()
    test_case.setUp()
    
    print("🚀 Running OCR Performance Tests...")
    print("=" * 50)
    
    # Run all performance tests
    test_case.test_processing_speed_target()
    test_case.test_concurrent_processing()
    test_case.test_accuracy_target()
    test_case.test_memory_usage()
    test_case.test_polish_processor_performance()
    test_case.test_system_load()
    test_case.test_response_time_target()
    test_case.test_throughput_target()
    
    test_case.tearDown()
    
    print("=" * 50)
    print("✅ All performance tests passed!")
    print("🎯 OCR system meets all performance targets!")
