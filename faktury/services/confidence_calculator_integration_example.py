"""
Integration Example for ConfidenceCalculator

This example demonstrates how to integrate the ConfidenceCalculator
with existing OCR services and processing pipelines.
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal

from .confidence_calculator import ConfidenceCalculator
from .polish_invoice_processor import PolishInvoiceProcessor
from .invoice_field_extractor import InvoiceFieldExtractor

logger = logging.getLogger(__name__)


class EnhancedOCRProcessor:
    """
    Enhanced OCR processor that integrates confidence calculation
    with existing OCR services for comprehensive result analysis.
    """
    
    def __init__(self):
        self.confidence_calculator = ConfidenceCalculator()
        self.polish_processor = PolishInvoiceProcessor()
        self.field_extractor = InvoiceFieldExtractor()
    
    def process_document_with_confidence(self, 
                                       file_content: bytes,
                                       mime_type: str,
                                       ocr_engines: List[Any] = None) -> Dict[str, Any]:
        """
        Process document with comprehensive confidence analysis
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            ocr_engines: List of OCR engines to use
            
        Returns:
            Dictionary containing OCR results with detailed confidence analysis
        """
        try:
            logger.info("Starting enhanced OCR processing with confidence calculation")
            
            # Step 1: Perform OCR extraction (simulated here)
            ocr_results = self._perform_ocr_extraction(file_content, mime_type, ocr_engines)
            
            # Step 2: Extract structured fields
            extracted_data = self._extract_structured_fields(
                ocr_results['raw_text'], 
                ocr_results.get('field_confidence', {})
            )
            
            # Step 3: Apply Polish language enhancements
            enhanced_data = self._apply_polish_enhancements(
                ocr_results['raw_text'], 
                extracted_data
            )
            
            # Step 4: Calculate comprehensive confidence
            confidence_analysis = self.confidence_calculator.calculate_overall_confidence(
                extracted_data=enhanced_data,
                ocr_confidence=ocr_results,
                raw_text=ocr_results['raw_text'],
                engine_results=ocr_results.get('engine_results', [])
            )
            
            # Step 5: Combine results
            final_result = {
                'raw_text': ocr_results['raw_text'],
                'extracted_data': enhanced_data,
                'confidence_analysis': confidence_analysis,
                'processing_metadata': {
                    'engines_used': ocr_results.get('engines_used', []),
                    'processing_time': ocr_results.get('processing_time', 0.0),
                    'polish_enhancements_applied': True,
                    'confidence_calculation_version': '1.0'
                },
                'recommendations': self._generate_processing_recommendations(confidence_analysis)
            }
            
            logger.info(f"Enhanced OCR processing completed with {confidence_analysis['overall_confidence']:.1f}% confidence")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in enhanced OCR processing: {e}", exc_info=True)
            return {
                'raw_text': '',
                'extracted_data': {},
                'confidence_analysis': {'overall_confidence': 0.0, 'error': str(e)},
                'processing_error': str(e)
            }
    
    def _perform_ocr_extraction(self, 
                              file_content: bytes, 
                              mime_type: str,
                              ocr_engines: List[Any] = None) -> Dict[str, Any]:
        """
        Simulate OCR extraction (in real implementation, this would call actual OCR engines)
        """
        # This is a simulation - in real implementation, you would:
        # 1. Call multiple OCR engines (Tesseract, EasyOCR, etc.)
        # 2. Aggregate their results
        # 3. Return combined OCR data
        
        sample_ocr_result = {
            'raw_text': """
            FAKTURA VAT Nr FV/123/01/2024
            Data wystawienia: 15 stycznia 2024
            Data sprzedaży: 15 stycznia 2024
            Termin płatności: 29 stycznia 2024
            
            Sprzedawca:
            ABC Firma Sp. z o.o.
            ul. Testowa 123
            00-001 Warszawa
            NIP: 123-456-78-90
            REGON: 123456789
            
            Nabywca:
            XYZ Klient S.A.
            ul. Przykładowa 456
            00-002 Kraków
            NIP: 098-765-43-21
            
            Lp. | Nazwa towaru/usługi | Ilość | J.m. | Cena netto | VAT | Wartość netto | Wartość brutto
            1   | Usługa konsultingowa | 10    | godz | 150,00     | 23% | 1 500,00      | 1 845,00
            2   | Materiały biurowe    | 1     | kpl  | 250,00     | 23% | 250,00        | 307,50
            
            Razem netto: 1 750,00 zł
            VAT 23%: 402,50 zł
            Do zapłaty: 2 152,50 zł
            
            Sposób płatności: przelew
            Nr konta: PL 12 3456 7890 1234 5678 9012 3456
            """,
            'confidence_score': 87.5,
            'field_confidence': {
                'numer_faktury': 92.0,
                'invoice_date': 89.0,
                'sale_date': 89.0,
                'due_date': 85.0,
                'supplier_name': 88.0,
                'supplier_nip': 91.0,
                'buyer_name': 86.0,
                'buyer_nip': 88.0,
                'total_amount': 94.0,
                'net_amount': 90.0,
                'vat_amount': 87.0,
                'bank_account': 83.0
            },
            'processing_time': 2.3,
            'engines_used': ['tesseract', 'easyocr'],
            'engine_results': [
                {'engine_name': 'tesseract', 'confidence_score': 85.0},
                {'engine_name': 'easyocr', 'confidence_score': 90.0}
            ]
        }
        
        return sample_ocr_result
    
    def _extract_structured_fields(self, 
                                 raw_text: str, 
                                 field_confidence: Dict[str, float]) -> Dict[str, Any]:
        """
        Extract structured fields using the field extractor
        """
        try:
            # Use the invoice field extractor
            extraction_result = self.field_extractor.extract_fields(
                raw_text, 
                {'field_confidence': field_confidence}
            )
            
            # Convert extraction result to flat structure for confidence calculation
            extracted_data = {}
            
            # Basic fields
            if extraction_result.get('extracted_fields'):
                extracted_data.update(extraction_result['extracted_fields'])
            
            # Company information
            if extraction_result.get('seller_info'):
                seller = extraction_result['seller_info']
                extracted_data.update({
                    'supplier_name': seller.nazwa,
                    'supplier_nip': seller.nip,
                    'supplier_address': f"{seller.ulica} {seller.numer_domu}",
                    'supplier_city': seller.miejscowosc,
                    'supplier_postal_code': seller.kod_pocztowy
                })
            
            if extraction_result.get('buyer_info'):
                buyer = extraction_result['buyer_info']
                extracted_data.update({
                    'buyer_name': buyer.nazwa,
                    'buyer_nip': buyer.nip,
                    'buyer_address': f"{buyer.ulica} {buyer.numer_domu}",
                    'buyer_city': buyer.miejscowosc,
                    'buyer_postal_code': buyer.kod_pocztowy
                })
            
            # Line items summary
            if extraction_result.get('line_items'):
                line_items = extraction_result['line_items']
                extracted_data['line_items_count'] = len(line_items)
                extracted_data['line_items_total_confidence'] = (
                    sum(item.confidence for item in line_items) / len(line_items)
                    if line_items else 0.0
                )
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting structured fields: {e}")
            return {}
    
    def _apply_polish_enhancements(self, 
                                 raw_text: str, 
                                 base_extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Polish language enhancements to extracted data
        """
        try:
            # Use the Polish invoice processor for enhancements
            enhanced_data = self.polish_processor.enhance_extraction(
                raw_text, 
                base_extraction
            )
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error applying Polish enhancements: {e}")
            return base_extraction
    
    def _generate_processing_recommendations(self, 
                                           confidence_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate processing recommendations based on confidence analysis
        """
        recommendations = []
        overall_confidence = confidence_analysis.get('overall_confidence', 0.0)
        
        # Overall confidence recommendations
        if overall_confidence >= 90.0:
            recommendations.append({
                'type': 'auto_process',
                'priority': 'high',
                'message': 'High confidence - suitable for automatic processing',
                'action': 'auto_create_faktura'
            })
        elif overall_confidence >= 75.0:
            recommendations.append({
                'type': 'review_recommended',
                'priority': 'medium',
                'message': 'Medium confidence - review recommended before processing',
                'action': 'queue_for_review'
            })
        else:
            recommendations.append({
                'type': 'manual_review_required',
                'priority': 'high',
                'message': 'Low confidence - manual review required',
                'action': 'require_manual_review'
            })
        
        # Field-specific recommendations
        field_confidences = confidence_analysis.get('field_confidences', {})
        low_confidence_fields = [
            field for field, data in field_confidences.items()
            if data.get('confidence', 0.0) < 70.0
        ]
        
        if low_confidence_fields:
            recommendations.append({
                'type': 'field_review',
                'priority': 'medium',
                'message': f'Low confidence fields require attention: {", ".join(low_confidence_fields)}',
                'action': 'highlight_fields',
                'fields': low_confidence_fields
            })
        
        # Validation failure recommendations
        validation_results = confidence_analysis.get('validation_results', {})
        if not validation_results.get('all_validations_passed', True):
            recommendations.append({
                'type': 'validation_failure',
                'priority': 'high',
                'message': 'Some business rule validations failed',
                'action': 'check_validation_details',
                'details': validation_results
            })
        
        # Polish language boost recommendations
        polish_boost = confidence_analysis.get('polish_boost_applied', 0.0)
        if polish_boost > 10.0:
            recommendations.append({
                'type': 'polish_patterns_detected',
                'priority': 'low',
                'message': f'Strong Polish language patterns detected (+{polish_boost:.1f}% boost)',
                'action': 'confidence_boost_applied'
            })
        
        return recommendations
    
    def get_confidence_statistics(self) -> Dict[str, Any]:
        """
        Get confidence calculation statistics
        """
        return self.confidence_calculator.get_calculation_statistics()


# Example usage function
def example_usage():
    """
    Example of how to use the enhanced OCR processor with confidence calculation
    """
    processor = EnhancedOCRProcessor()
    
    # Simulate processing a document
    sample_file_content = b"sample_pdf_content"  # In real use, this would be actual file bytes
    mime_type = "application/pdf"
    
    # Process document
    result = processor.process_document_with_confidence(
        file_content=sample_file_content,
        mime_type=mime_type
    )
    
    # Print results
    print("=== OCR Processing Results ===")
    print(f"Overall Confidence: {result['confidence_analysis']['overall_confidence']:.1f}%")
    print(f"Extracted Fields: {len(result['extracted_data'])}")
    print(f"Processing Recommendations: {len(result['recommendations'])}")
    
    # Print field confidences
    print("\n=== Field Confidences ===")
    for field, data in result['confidence_analysis']['field_confidences'].items():
        print(f"{field}: {data['confidence']:.1f}%")
    
    # Print recommendations
    print("\n=== Processing Recommendations ===")
    for rec in result['recommendations']:
        print(f"- {rec['type']}: {rec['message']} (Priority: {rec['priority']})")
    
    # Print confidence components
    print("\n=== Confidence Components ===")
    for comp in result['confidence_analysis']['confidence_components']:
        contribution = comp['weighted_contribution']
        print(f"- {comp['source']}: {comp['score']:.1f}% (weight: {comp['weight']:.2f}, contribution: {contribution:.1f})")
    
    return result


if __name__ == "__main__":
    # Run example
    example_usage()