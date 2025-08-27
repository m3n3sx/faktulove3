#!/usr/bin/env python3
"""
Example usage of Enhanced Polish Processor

This example demonstrates how to use the EnhancedPolishProcessor
for extracting and validating Polish invoice data.
"""

from enhanced_polish_processor import EnhancedPolishProcessor


def main():
    """Demonstrate Enhanced Polish Processor functionality."""
    
    # Initialize the processor
    processor = EnhancedPolishProcessor()
    
    # Sample Polish invoice text
    sample_invoice_text = """
    FAKTURA VAT
    Nr: FV/001/2024
    Data wystawienia: 15.01.2024
    Data sprzedaży: 15.01.2024
    
    Sprzedawca:
    Test Company Sp. z o.o.
    ul. Testowa 123, 00-001 Warszawa
    NIP: 526-000-12-46
    REGON: 123456785
    KRS: 1234567890
    
    Nabywca:
    Client Company Ltd.
    ul. Kliencka 456, 00-002 Kraków
    NIP: 701-000-14-53
    
    Pozycje faktury:
    1. Usługa konsultingowa - 1000,00 zł netto
    2. VAT 23% - 230,00 zł
    
    Podsumowanie:
    Suma netto: 1000,00 zł
    VAT 23%: 230,00 zł
    Suma brutto: 1230,00 zł
    
    Termin płatności: 30 dni
    """
    
    print("=== Enhanced Polish Processor Demo ===\n")
    
    # Extract all Polish invoice fields
    print("1. Extracting Polish invoice fields...")
    extracted_data = processor.extract_polish_invoice_fields(sample_invoice_text)
    
    print("Extracted fields:")
    for field, value in extracted_data.items():
        print(f"  {field}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Validate extracted patterns
    print("2. Validating Polish patterns...")
    validation_results = processor.validate_polish_patterns(extracted_data)
    
    print("Validation results:")
    for field, is_valid in validation_results.items():
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"  {field}: {status}")
    
    print("\n" + "="*50 + "\n")
    
    # Calculate confidence scores
    print("3. Calculating field confidence scores...")
    
    confidence_tests = [
        ('526-000-12-46', 'nip'),
        ('2024-01-15', 'date'),
        ('1230.00', 'amount'),
        ('23', 'vat_rate'),
        ('FV/001/2024', 'invoice_number'),
    ]
    
    print("Confidence scores:")
    for field_value, field_type in confidence_tests:
        confidence = processor.calculate_field_confidence(field_value, field_type)
        print(f"  {field_type} '{field_value}': {confidence:.2f}")
    
    print("\n" + "="*50 + "\n")
    
    # Test individual validation functions
    print("4. Testing individual validation functions...")
    
    # NIP validation
    test_nips = ['526-000-12-46', '1234567890', '0000000000']
    print("NIP validation:")
    for nip in test_nips:
        is_valid = processor.validate_nip(nip.replace('-', ''))
        status = "✓" if is_valid else "✗"
        print(f"  {nip}: {status}")
    
    # REGON validation
    test_regons = ['123456785', '12345678512347', '12345678']
    print("\nREGON validation:")
    for regon in test_regons:
        is_valid = processor.validate_regon(regon)
        status = "✓" if is_valid else "✗"
        print(f"  {regon}: {status}")
    
    # Date parsing
    test_dates = ['15.01.2024', '2024-01-15', '15 stycznia 2024']
    print("\nDate parsing:")
    for date_text in test_dates:
        dates = processor.extract_polish_dates(date_text)
        print(f"  '{date_text}' -> {dates}")
    
    print("\n" + "="*50 + "\n")
    print("Demo completed successfully!")


if __name__ == '__main__':
    main()