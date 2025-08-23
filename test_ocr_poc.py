#!/usr/bin/env python3
"""
POC Test Script for Google Document AI Integration
This script demonstrates basic invoice processing capabilities
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktury_projekt.settings')
import django
django.setup()

from faktury.services.document_ai_service import DocumentAIService, MockDocumentAIService
from faktury.services.file_upload_service import FileUploadService
from faktury.models import DocumentUpload, OCRResult
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)


def test_mock_service():
    """Test with mock service first"""
    print_header("Testing Mock Document AI Service")
    
    # Initialize mock service
    service = MockDocumentAIService()
    
    # Create test document
    test_text = """
    FAKTURA VAT
    Nr: FV/2024/01/001
    
    Sprzedawca:
    TestCompany Sp. z o.o.
    ul. Testowa 123
    00-001 Warszawa
    NIP: 123-456-78-90
    
    Nabywca:
    Klient Test S.A.
    ul. Przykładowa 456
    00-002 Kraków
    NIP: 987-654-32-10
    
    Pozycje:
    1. Usługa konsultingowa - 1000.00 PLN netto (23% VAT)
    2. Licencja oprogramowania - 2000.00 PLN netto (23% VAT)
    
    Suma netto: 3000.00 PLN
    VAT 23%: 690.00 PLN
    Suma brutto: 3690.00 PLN
    """
    
    # Process document
    result = service.process_invoice(test_text.encode(), 'text/plain')
    
    print("\nExtracted Data:")
    print(json.dumps(result, indent=2))
    print(f"\nConfidence Score: {result.get('confidence_score', 0):.2%}")
    print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
    
    return result


def test_file_upload():
    """Test file upload service"""
    print_header("Testing File Upload Service")
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='test_ocr_user',
        defaults={'email': 'test@example.com'}
    )
    
    # Create or get user's company
    from faktury.models import Firma
    firma, created = Firma.objects.get_or_create(
        user=user,
        defaults={
            'nazwa': 'Test Company Sp. z o.o.',
            'nip': '1234567890',
            'ulica': 'Testowa 123',
            'numer_domu': '1',
            'kod_pocztowy': '00-001',
            'miejscowosc': 'Warszawa',
            'kraj': 'Polska'
        }
    )
    
    # Create test file
    test_content = b"Test invoice content for OCR processing"
    test_file = SimpleUploadedFile(
        "test_invoice.pdf",
        test_content,
        content_type="application/pdf"
    )
    
    # Initialize upload service
    upload_service = FileUploadService()
    
    # Process upload
    try:
        document = upload_service.handle_upload(test_file, user)
        print(f"\nDocument uploaded successfully!")
        print(f"ID: {document.id}")
        print(f"Filename: {document.original_filename}")
        print(f"Size: {document.file_size} bytes")
        print(f"Path: {document.file_path}")
        
        return document
    except Exception as e:
        print(f"\nUpload error: {e}")
        return None


def test_ocr_processing(document_id):
    """Test OCR processing with mock service"""
    print_header("Testing OCR Processing")
    
    try:
        # Get document
        document = DocumentUpload.objects.get(id=document_id)
        
        # Process with mock service
        from faktury.tasks import process_ocr_document
        
        print(f"\nProcessing document: {document.original_filename}")
        
        # Call task directly (synchronously for testing)
        result = process_ocr_document(document.id)
        
        if result:
            # Get OCR result
            ocr_result = OCRResult.objects.get(document=document)
            
            print(f"\nOCR Processing completed!")
            print(f"Confidence: {ocr_result.confidence_score:.2%}")
            print(f"Processing time: {ocr_result.processing_time:.2f}s")
            
            print("\nExtracted entities:")
            for entity_type, entity_data in ocr_result.extracted_data.items():
                if isinstance(entity_data, dict) and 'value' in entity_data:
                    print(f"  {entity_type}: {entity_data['value']} "
                          f"(confidence: {entity_data.get('confidence', 0):.2%})")
            
            return ocr_result
        else:
            print("\nOCR Processing failed!")
            
    except Exception as e:
        print(f"\nProcessing error: {e}")
        import traceback
        traceback.print_exc()


def test_invoice_creation(ocr_result_id):
    """Test automatic invoice creation from OCR"""
    print_header("Testing Invoice Creation from OCR")
    
    try:
        from faktury.services.document_ai_service import create_faktura_from_ocr
        
        # Get OCR result
        ocr_result = OCRResult.objects.get(id=ocr_result_id)
        
        # Create invoice
        faktura = create_faktura_from_ocr(ocr_result)
        
        if faktura:
            print(f"\nInvoice created successfully!")
            print(f"Invoice number: {faktura.numer}")
            print(f"Seller: {faktura.firma_sprzedawca.nazwa}")
            print(f"Buyer: {faktura.firma_nabywca.nazwa}")
            print(f"Total gross: {faktura.suma_brutto} PLN")
            
            print("\nInvoice items:")
            for item in faktura.pozycjafaktury_set.all():
                print(f"  - {item.nazwa}: {item.ilosc} x {item.cena_netto} PLN "
                      f"(VAT {item.stawka_vat}%)")
        else:
            print("\nInvoice creation failed - manual review required")
            
    except Exception as e:
        print(f"\nInvoice creation error: {e}")
        import traceback
        traceback.print_exc()


def test_statistics():
    """Display OCR statistics"""
    print_header("OCR Processing Statistics")
    
    from django.db.models import Avg, Count, Q
    
    # Overall statistics
    stats = OCRResult.objects.aggregate(
        total_processed=Count('id'),
        avg_confidence=Avg('confidence_score'),
        avg_processing_time=Avg('processing_time'),
        high_confidence=Count('id', filter=Q(confidence_score__gte=95)),
        medium_confidence=Count('id', filter=Q(confidence_score__gte=80, confidence_score__lt=95)),
        low_confidence=Count('id', filter=Q(confidence_score__lt=80))
    )
    
    print(f"\nTotal documents processed: {stats['total_processed']}")
    print(f"Average confidence score: {stats['avg_confidence'] or 0:.2%}")
    print(f"Average processing time: {stats['avg_processing_time'] or 0:.2f}s")
    
    print("\nConfidence distribution:")
    print(f"  High (≥95%): {stats['high_confidence']} documents")
    print(f"  Medium (80-95%): {stats['medium_confidence']} documents")
    print(f"  Low (<80%): {stats['low_confidence']} documents")
    
    # Recent results
    print("\nRecent OCR results:")
    recent_results = OCRResult.objects.order_by('-created_at')[:5]
    for result in recent_results:
        print(f"  - {result.document.original_filename}: "
              f"{result.confidence_score:.1f}% confidence, "
              f"{result.processing_time:.2f}s")


def main():
    """Main test execution"""
    print("\n" + "="*60)
    print(" FaktuLove OCR POC Test Suite")
    print(" Testing Google Document AI Integration")
    print("="*60)
    
    try:
        # Test 1: Mock service
        mock_result = test_mock_service()
        
        # Test 2: File upload
        document = test_file_upload()
        
        if document:
            # Test 3: OCR processing
            ocr_result = test_ocr_processing(document.id)
            
            if ocr_result:
                # Test 4: Invoice creation
                test_invoice_creation(ocr_result.id)
        
        # Test 5: Statistics
        test_statistics()
        
        print("\n" + "="*60)
        print(" POC Test Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Configure real Google Document AI credentials")
        print("2. Test with actual invoice PDFs")
        print("3. Fine-tune extraction patterns for Polish invoices")
        print("4. Implement UI improvements")
        
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()