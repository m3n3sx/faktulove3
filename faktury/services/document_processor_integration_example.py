"""
Document Processor Integration Example

This example demonstrates how to use the DocumentProcessor as the main
orchestrator for OCR processing pipeline with real components.
"""

import logging
import os
from typing import Dict, Any

from .document_processor import DocumentProcessor
from .ocr_engine_service import OCREngineFactory, OCREngineType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demonstrate_document_processor():
    """
    Demonstrate DocumentProcessor functionality with mock data
    """
    print("=== Document Processor Integration Example ===\n")
    
    # Initialize the document processor
    print("1. Initializing DocumentProcessor...")
    processor = DocumentProcessor(
        max_workers=2,
        enable_parallel_processing=True,
        confidence_threshold=70.0,
        max_retries=2,
        fallback_enabled=True
    )
    
    # Initialize the processor (this would normally initialize real OCR engines)
    success = processor.initialize()
    if not success:
        print("❌ Failed to initialize DocumentProcessor")
        return
    
    print(f"✅ DocumentProcessor initialized successfully")
    print(f"   - OCR engines available: {len(processor.ocr_engines)}")
    print(f"   - Parallel processing: {processor.enable_parallel_processing}")
    print(f"   - Confidence threshold: {processor.confidence_threshold}%")
    print()
    
    # Get health status
    print("2. Checking system health...")
    health = processor.get_health_status()
    print(f"   - Overall status: {health['status']}")
    print(f"   - Components initialized: {len(health['components'])}")
    print(f"   - OCR engines: {len(health['engines'])}")
    if health['issues']:
        print(f"   - Issues: {health['issues']}")
    print()
    
    # Simulate processing a document
    print("3. Processing sample document...")
    
    # Create mock document content (in real usage, this would be actual file bytes)
    sample_document = b"Mock invoice document content for testing"
    mime_type = "image/jpeg"
    
    try:
        # Process the document
        result = processor.process_invoice(
            file_content=sample_document,
            mime_type=mime_type,
            document_id="example_001"
        )
        
        # Display results
        print(f"   - Processing successful: {result.success}")
        print(f"   - Overall confidence: {result.confidence_score:.1f}%")
        print(f"   - Processing time: {result.total_processing_time:.3f}s")
        print(f"   - Engines used: {result.engines_used}")
        print(f"   - Fallback applied: {result.fallback_applied}")
        print(f"   - Processing steps: {len(result.processing_steps)}")
        
        # Show processing steps
        print("\n   Processing Pipeline Steps:")
        for i, step in enumerate(result.processing_steps, 1):
            status_icon = "✅" if step.status.value == "completed" else "❌" if step.status.value == "failed" else "⚠️"
            print(f"   {i}. {status_icon} {step.stage.value.replace('_', ' ').title()}")
            print(f"      - Status: {step.status.value}")
            print(f"      - Duration: {step.duration:.3f}s" if step.duration else "      - Duration: N/A")
            if step.retry_count > 0:
                print(f"      - Retries: {step.retry_count}")
            if step.error_message:
                print(f"      - Error: {step.error_message}")
        
        # Show extracted data (if any)
        if result.extracted_data:
            print(f"\n   Extracted Data:")
            extracted_fields = result.extracted_data.get('extracted_fields', {})
            for field, value in extracted_fields.items():
                print(f"   - {field}: {value}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
    
    print()
    
    # Show processing statistics
    print("4. Processing Statistics...")
    stats = processor.get_processing_statistics()
    
    overall_stats = stats['overall_stats']
    print(f"   - Total processed: {overall_stats['total_processed']}")
    print(f"   - Success rate: {overall_stats['success_rate']:.1f}%")
    print(f"   - Average processing time: {overall_stats['average_processing_time']:.3f}s")
    print(f"   - Fallback usage rate: {overall_stats['fallback_usage_rate']:.1f}%")
    
    # Show stage performance
    print(f"\n   Stage Performance:")
    for stage_name, stage_stats in stats['stage_performance'].items():
        if stage_stats['total_attempts'] > 0:
            success_rate = (stage_stats['successful_attempts'] / stage_stats['total_attempts']) * 100
            print(f"   - {stage_name.replace('_', ' ').title()}:")
            print(f"     • Success rate: {success_rate:.1f}%")
            print(f"     • Average duration: {stage_stats['average_duration']:.3f}s")
    
    # Show engine performance
    print(f"\n   Engine Performance:")
    for engine_name, engine_stats in stats['engine_performance'].items():
        if engine_stats['usage_count'] > 0:
            success_rate = (engine_stats['success_count'] / engine_stats['usage_count']) * 100
            print(f"   - {engine_name}:")
            print(f"     • Usage count: {engine_stats['usage_count']}")
            print(f"     • Success rate: {success_rate:.1f}%")
            print(f"     • Average confidence: {engine_stats['average_confidence']:.1f}%")
            print(f"     • Average processing time: {engine_stats['average_processing_time']:.3f}s")
    
    print("\n=== Example Complete ===")


def demonstrate_error_handling():
    """
    Demonstrate error handling and fallback mechanisms
    """
    print("\n=== Error Handling and Fallback Demo ===\n")
    
    processor = DocumentProcessor(
        max_workers=1,
        enable_parallel_processing=False,
        confidence_threshold=80.0,  # High threshold
        max_retries=1,
        fallback_enabled=True
    )
    
    # Try to initialize (may fail if no real engines available)
    if not processor.initialize():
        print("⚠️  No real OCR engines available - this is expected in test environment")
        return
    
    print("1. Testing with invalid input...")
    
    # Test with empty content
    result = processor.process_invoice(b"", "image/jpeg")
    print(f"   - Empty content result: {'Success' if result.success else 'Failed (expected)'}")
    if result.error_details:
        print(f"   - Error stage: {result.error_details['stage']}")
        print(f"   - Error message: {result.error_details['message']}")
    
    print("\n2. Testing with unsupported format...")
    
    # Test with unsupported format
    result = processor.process_invoice(b"test content", "application/unknown")
    print(f"   - Unsupported format result: {'Success' if result.success else 'Failed (expected)'}")
    if result.error_details:
        print(f"   - Error stage: {result.error_details['stage']}")
    
    print("\n=== Error Handling Demo Complete ===")


def demonstrate_parallel_vs_sequential():
    """
    Demonstrate parallel vs sequential processing
    """
    print("\n=== Parallel vs Sequential Processing Demo ===\n")
    
    # Test parallel processing
    print("1. Testing parallel processing...")
    parallel_processor = DocumentProcessor(
        max_workers=3,
        enable_parallel_processing=True,
        confidence_threshold=70.0
    )
    
    if parallel_processor.initialize():
        sample_doc = b"Sample document for parallel processing test"
        result = parallel_processor.process_invoice(sample_doc, "image/jpeg")
        print(f"   - Parallel processing time: {result.total_processing_time:.3f}s")
        print(f"   - Engines used: {len(result.engines_used)}")
    
    # Test sequential processing
    print("\n2. Testing sequential processing...")
    sequential_processor = DocumentProcessor(
        max_workers=1,
        enable_parallel_processing=False,
        confidence_threshold=70.0
    )
    
    if sequential_processor.initialize():
        sample_doc = b"Sample document for sequential processing test"
        result = sequential_processor.process_invoice(sample_doc, "image/jpeg")
        print(f"   - Sequential processing time: {result.total_processing_time:.3f}s")
        print(f"   - Engines used: {len(result.engines_used)}")
    
    print("\n=== Processing Comparison Complete ===")


if __name__ == "__main__":
    """
    Run the integration examples
    """
    try:
        demonstrate_document_processor()
        demonstrate_error_handling()
        demonstrate_parallel_vs_sequential()
        
    except Exception as e:
        logger.error(f"Example execution failed: {e}", exc_info=True)
        print(f"\n❌ Example failed: {e}")
    
    print("\n🎉 All examples completed!")