"""
Integration example for InvoiceFieldExtractor with existing OCR system

This example demonstrates how to integrate the new InvoiceFieldExtractor
with the existing OCR processing pipeline.
"""

import logging
from typing import Dict, Any, Optional
from decimal import Decimal

from .invoice_field_extractor import InvoiceFieldExtractor, ExtractedField, LineItem, CompanyInfo
from .polish_invoice_processor import PolishInvoiceProcessor

logger = logging.getLogger(__name__)


class EnhancedOCRProcessor:
    """
    Enhanced OCR processor that combines the existing PolishInvoiceProcessor
    with the new InvoiceFieldExtractor for improved accuracy and functionality.
    """
    
    def __init__(self):
        self.field_extractor = InvoiceFieldExtractor()
        self.polish_processor = PolishInvoiceProcessor()
    
    def process_invoice_text(self, ocr_text: str, ocr_confidence_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process invoice text using both the legacy Polish processor and new field extractor
        
        Args:
            ocr_text: Raw OCR text from document
            ocr_confidence_data: OCR confidence information from OCR engine
            
        Returns:
            Enhanced extraction results combining both processors
        """
        try:
            logger.info("Starting enhanced invoice processing")
            
            # Use the new field extractor as primary processor
            primary_result = self.field_extractor.extract_fields(ocr_text, ocr_confidence_data)
            
            # Use Polish processor for additional enhancement
            enhanced_result = self.polish_processor.enhance_extraction(ocr_text, primary_result)
            
            # Combine results with preference for field extractor
            final_result = self._combine_extraction_results(primary_result, enhanced_result)
            
            logger.info(f"Enhanced processing completed with confidence: {final_result.get('overall_confidence', 0):.1f}%")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in enhanced invoice processing: {e}", exc_info=True)
            return {
                'extracted_fields': {},
                'line_items': [],
                'seller_info': None,
                'buyer_info': None,
                'processing_error': str(e),
                'overall_confidence': 0.0
            }
    
    def _combine_extraction_results(self, primary_result: Dict[str, Any], 
                                  enhanced_result: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results from field extractor and Polish processor"""
        
        # Start with primary result as base
        combined_result = primary_result.copy()
        
        # Enhance with Polish processor results where confidence is higher
        if enhanced_result.get('polish_confidence_boost', 0) > 0:
            # Apply Polish confidence boost
            current_confidence = combined_result.get('overall_confidence', 0)
            boost = enhanced_result.get('polish_confidence_boost', 0)
            combined_result['overall_confidence'] = min(100.0, current_confidence + boost)
        
        # Merge enhanced Polish-specific fields
        if enhanced_result.get('polish_vat_numbers'):
            combined_result['enhanced_nip_numbers'] = enhanced_result['polish_vat_numbers']
        
        if enhanced_result.get('formatted_nips'):
            combined_result['formatted_nip_numbers'] = enhanced_result['formatted_nips']
        
        # Add processing metadata
        combined_result['processing_metadata'] = {
            'primary_processor': 'InvoiceFieldExtractor',
            'enhancement_processor': 'PolishInvoiceProcessor',
            'combined_processing': True,
            'polish_boost_applied': enhanced_result.get('polish_confidence_boost', 0) > 0
        }
        
        return combined_result
    
    def convert_to_legacy_format(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert new extraction format to legacy format for backward compatibility
        
        This method ensures that existing code expecting the old format continues to work.
        """
        legacy_result = {}
        
        # Convert extracted fields
        extracted_fields = extraction_result.get('extracted_fields', {})
        
        # Map invoice number
        if 'numer_faktury' in extracted_fields:
            field = extracted_fields['numer_faktury']
            if isinstance(field, ExtractedField):
                legacy_result['numer_faktury'] = field.value
        
        # Map dates
        for date_type in ['invoice_date', 'sale_date', 'due_date']:
            if date_type in extracted_fields:
                field = extracted_fields[date_type]
                if isinstance(field, ExtractedField):
                    legacy_key = date_type.replace('_date', '_data')
                    if date_type == 'invoice_date':
                        legacy_key = 'data_wystawienia'
                    elif date_type == 'sale_date':
                        legacy_key = 'data_sprzedazy'
                    elif date_type == 'due_date':
                        legacy_key = 'termin_platnosci'
                    
                    legacy_result[legacy_key] = field.value
        
        # Map amounts
        for amount_type in ['total_amount', 'netto_amount', 'brutto_amount']:
            if amount_type in extracted_fields:
                field = extracted_fields[amount_type]
                if isinstance(field, ExtractedField):
                    if amount_type == 'total_amount':
                        legacy_result['suma_brutto'] = field.value
                    elif amount_type == 'netto_amount':
                        legacy_result['suma_netto'] = field.value
                    elif amount_type == 'brutto_amount':
                        legacy_result['suma_brutto'] = field.value
        
        # Map company information
        seller_info = extraction_result.get('seller_info')
        if seller_info and isinstance(seller_info, CompanyInfo):
            legacy_result['sprzedawca_nazwa'] = seller_info.nazwa
            legacy_result['sprzedawca_nip'] = seller_info.nip
            legacy_result['sprzedawca_ulica'] = seller_info.ulica
            legacy_result['sprzedawca_numer_domu'] = seller_info.numer_domu
            legacy_result['sprzedawca_kod_pocztowy'] = seller_info.kod_pocztowy
            legacy_result['sprzedawca_miejscowosc'] = seller_info.miejscowosc
            legacy_result['sprzedawca_kraj'] = seller_info.kraj
        
        buyer_info = extraction_result.get('buyer_info')
        if buyer_info and isinstance(buyer_info, CompanyInfo):
            legacy_result['nabywca_nazwa'] = buyer_info.nazwa
            legacy_result['nabywca_nip'] = buyer_info.nip
            legacy_result['nabywca_ulica'] = buyer_info.ulica
            legacy_result['nabywca_numer_domu'] = buyer_info.numer_domu
            legacy_result['nabywca_kod_pocztowy'] = buyer_info.kod_pocztowy
            legacy_result['nabywca_miejscowosc'] = buyer_info.miejscowosc
            legacy_result['nabywca_kraj'] = buyer_info.kraj
        
        # Convert line items
        line_items = extraction_result.get('line_items', [])
        legacy_positions = []
        
        for item in line_items:
            if isinstance(item, LineItem):
                legacy_position = {
                    'nazwa': item.nazwa,
                    'ilosc': float(item.ilosc),
                    'jednostka': item.jednostka,
                    'cena_netto': float(item.cena_netto),
                    'vat': item.vat.replace('%', '') if '%' in item.vat else item.vat,
                    'wartosc_netto': float(item.wartosc_netto),
                    'wartosc_brutto': float(item.wartosc_brutto)
                }
                legacy_positions.append(legacy_position)
        
        legacy_result['pozycje'] = legacy_positions
        
        # Add confidence score
        legacy_result['confidence_score'] = extraction_result.get('overall_confidence', 0.0)
        
        return legacy_result
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics from both processors"""
        field_extractor_stats = self.field_extractor.get_extraction_statistics()
        
        return {
            'field_extractor_stats': field_extractor_stats,
            'combined_processor': 'EnhancedOCRProcessor',
            'version': '1.0.0'
        }


# Example usage function
def example_usage():
    """Example of how to use the enhanced OCR processor"""
    
    # Sample Polish invoice text
    sample_invoice = """
    FAKTURA VAT Nr FV/001/2024
    
    Data wystawienia: 15.01.2024
    Data sprzedaży: 15.01.2024
    Termin płatności: 29.01.2024
    
    SPRZEDAWCA:
    Example Company Sp. z o.o.
    ul. Przykładowa 123
    00-001 Warszawa
    NIP: 526-000-12-46
    
    NABYWCA:
    Client ABC S.A.
    al. Kliencka 456
    01-002 Kraków
    NIP: 123-456-32-18
    
    Lp. | Nazwa towaru/usługi | Ilość | J.m. | Cena netto | VAT | Wartość netto | Wartość brutto
    1   | Usługa konsultacyjna | 10    | godz | 150,00     | 23% | 1500,00       | 1845,00
    2   | Materiały biurowe    | 1     | kpl  | 200,00     | 23% | 200,00        | 246,00
    
    Razem netto: 1700,00 zł
    VAT 23%: 391,00 zł
    Razem brutto: 2091,00 zł
    
    Do zapłaty: 2091,00 zł
    """
    
    # Initialize enhanced processor
    processor = EnhancedOCRProcessor()
    
    # Process the invoice
    result = processor.process_invoice_text(sample_invoice)
    
    # Print results
    print("=== Enhanced OCR Processing Results ===")
    print(f"Overall confidence: {result.get('overall_confidence', 0):.1f}%")
    print(f"Extracted fields: {len(result.get('extracted_fields', {}))}")
    print(f"Line items: {len(result.get('line_items', []))}")
    print(f"Seller: {result.get('seller_info', {}).nazwa if result.get('seller_info') else 'Not found'}")
    print(f"Buyer: {result.get('buyer_info', {}).nazwa if result.get('buyer_info') else 'Not found'}")
    
    # Convert to legacy format for backward compatibility
    legacy_result = processor.convert_to_legacy_format(result)
    print("\n=== Legacy Format Conversion ===")
    print(f"Invoice number: {legacy_result.get('numer_faktury', 'Not found')}")
    print(f"Issue date: {legacy_result.get('data_wystawienia', 'Not found')}")
    print(f"Total amount: {legacy_result.get('suma_brutto', 'Not found')}")
    print(f"Positions: {len(legacy_result.get('pozycje', []))}")
    
    return result, legacy_result


if __name__ == "__main__":
    # Run example
    example_usage()