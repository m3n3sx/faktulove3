#!/usr/bin/env python3
"""
Demonstration script for ImagePreprocessor integration.

This script shows how the ImagePreprocessor can be integrated
into the existing OCR pipeline to improve document processing.
"""

import os
import sys
import io
from PIL import Image, ImageDraw

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from faktury.services.image_preprocessor import ImagePreprocessor


def create_sample_documents():
    """Create sample documents for demonstration"""
    documents = []
    
    # 1. High quality invoice
    high_quality = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(high_quality)
    
    invoice_text = [
        "FAKTURA VAT Nr: FV/2024/001",
        "Data: 15.01.2024",
        "Sprzedawca: Firma ABC Sp. z o.o.",
        "NIP: 123-456-78-90",
        "Nabywca: Klient XYZ S.A.",
        "NIP: 987-654-32-10",
        "Pozycja: Usługa - 1000,00 PLN",
        "VAT 23%: 230,00 PLN",
        "RAZEM: 1230,00 PLN"
    ]
    
    y = 50
    for line in invoice_text:
        draw.text((50, y), line, fill='black')
        y += 40
    
    documents.append(("High Quality Invoice", high_quality))
    
    # 2. Low resolution document
    low_res = Image.new('RGB', (200, 300), color='white')
    draw = ImageDraw.Draw(low_res)
    draw.text((10, 10), "Low Resolution", fill='black')
    draw.text((10, 30), "Document", fill='black')
    draw.text((10, 50), "NIP: 123-456-78-90", fill='black')
    
    documents.append(("Low Resolution Document", low_res))
    
    # 3. High resolution document
    high_res = Image.new('RGB', (2400, 3000), color='white')
    draw = ImageDraw.Draw(high_res)
    draw.text((100, 100), "High Resolution Document", fill='black')
    draw.text((100, 200), "This document has very high resolution", fill='black')
    draw.text((100, 300), "and needs to be downscaled for OCR", fill='black')
    
    documents.append(("High Resolution Document", high_res))
    
    return documents


def image_to_bytes(image, format='PNG'):
    """Convert PIL Image to bytes"""
    output = io.BytesIO()
    image.save(output, format=format)
    return output.getvalue()


def demonstrate_preprocessing():
    """Demonstrate preprocessing capabilities"""
    print("🚀 ImagePreprocessor Demonstration")
    print("=" * 50)
    
    # Initialize preprocessor
    preprocessor = ImagePreprocessor()
    
    # Create sample documents
    documents = create_sample_documents()
    
    for doc_name, doc_image in documents:
        print(f"\n📄 Processing: {doc_name}")
        print("-" * 30)
        
        # Convert to bytes
        doc_bytes = image_to_bytes(doc_image)
        
        # Get preprocessing info
        info = preprocessor.get_preprocessing_info(doc_bytes, 'image/png')
        print(f"Original size: {info['original_size']}")
        print(f"Estimated DPI: {info['estimated_dpi']}")
        print(f"Will resize: {info['will_resize']}")
        
        # Preprocess the document
        try:
            processed_images = preprocessor.preprocess_document(doc_bytes, 'image/png')
            processed_image = Image.open(io.BytesIO(processed_images[0]))
            
            print(f"Processed size: {processed_image.size}")
            print(f"Processed mode: {processed_image.mode}")
            print("✅ Preprocessing successful")
            
            # Save for inspection
            filename = f"demo_{doc_name.lower().replace(' ', '_')}"
            doc_image.save(f"{filename}_original.png")
            processed_image.save(f"{filename}_processed.png")
            print(f"💾 Saved as {filename}_*.png")
            
        except Exception as e:
            print(f"❌ Preprocessing failed: {e}")


def demonstrate_format_support():
    """Demonstrate different format support"""
    print(f"\n🗂️  Supported Formats")
    print("-" * 30)
    
    preprocessor = ImagePreprocessor()
    
    for format_type in preprocessor.supported_formats.keys():
        print(f"✅ {format_type}")


def demonstrate_performance():
    """Demonstrate preprocessing performance"""
    print(f"\n⏱️  Performance Demonstration")
    print("-" * 30)
    
    import time
    
    preprocessor = ImagePreprocessor()
    
    # Test different image sizes
    sizes = [
        ("Small", (400, 300)),
        ("Medium", (800, 600)),
        ("Large", (1600, 1200)),
        ("Extra Large", (2400, 1800))
    ]
    
    for size_name, (width, height) in sizes:
        # Create test image
        test_image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(test_image)
        draw.text((50, 50), f"Test {size_name}", fill='black')
        
        image_bytes = image_to_bytes(test_image)
        
        # Measure processing time
        start_time = time.time()
        result = preprocessor.preprocess_document(image_bytes, 'image/png')
        end_time = time.time()
        
        processing_time = end_time - start_time
        processed_image = Image.open(io.BytesIO(result[0]))
        
        print(f"{size_name:12} ({width:4}x{height:4}): {processing_time:5.2f}s -> {processed_image.size}")
        
        # Check requirement compliance
        if processing_time <= 30:
            print(f"             ✅ Meets 30s requirement")
        else:
            print(f"             ⚠️  Exceeds 30s requirement")


def demonstrate_integration_example():
    """Show how to integrate with existing OCR pipeline"""
    print(f"\n🔗 Integration Example")
    print("-" * 30)
    
    print("""
# Example integration with existing OCR service:

from faktury.services.image_preprocessor import ImagePreprocessor
from faktury.services.ocr_service_factory import get_ocr_service  # Use factory for service selection

class EnhancedOCRService:
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.ocr_service = get_ocr_service()  # Use factory to get appropriate OCR service
    
    def process_document(self, file_content: bytes, mime_type: str):
        # Step 1: Preprocess document for better OCR
        processed_images = self.preprocessor.preprocess_document(file_content, mime_type)
        
        # Step 2: Process each image with OCR
        results = []
        for image_bytes in processed_images:
            result = self.ocr_service.process_document(image_bytes, 'image/png')
            results.append(result)
        
        # Step 3: Combine results if multiple pages
        return self.combine_results(results)
    
    def combine_results(self, results):
        # Combine multiple page results
        combined_text = '\\n'.join([r.get('extracted_text', '') for r in results])
        avg_confidence = sum([r.get('confidence', 0) for r in results]) / len(results)
        
        return {
            'extracted_text': combined_text,
            'confidence': avg_confidence,
            'page_count': len(results)
        }

# Usage:
enhanced_ocr = EnhancedOCRService()
result = enhanced_ocr.process_document(file_content, mime_type)
    """)


def main():
    """Run the complete demonstration"""
    try:
        demonstrate_preprocessing()
        demonstrate_format_support()
        demonstrate_performance()
        demonstrate_integration_example()
        
        print(f"\n🎉 Demonstration completed successfully!")
        print(f"Check the generated demo_*.png files to see preprocessing results.")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())