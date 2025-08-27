"""
Example usage of PaddleConfidenceCalculator

This example demonstrates how to use the PaddleConfidenceCalculator
for advanced confidence scoring of PaddleOCR results with Polish context validation.
"""

from faktury.services.paddle_confidence_calculator import PaddleConfidenceCalculator


def example_paddle_confidence_calculation():
    """Example of using PaddleConfidenceCalculator with sample data"""
    
    # Initialize the calculator
    calculator = PaddleConfidenceCalculator()
    
    # Sample PaddleOCR results (format: [bounding_box, (text, confidence)])
    paddle_results = [
        [
            [[100, 50], [300, 50], [300, 80], [100, 80]],
            ('FAKTURA VAT Nr FV/001/2024', 0.95)
        ],
        [
            [[100, 100], [400, 100], [400, 130], [100, 130]],
            ('ABC Company Sp. z o.o.', 0.88)
        ],
        [
            [[100, 150], [250, 150], [250, 180], [100, 180]],
            ('NIP: 526-000-12-46', 0.92)
        ],
        [
            [[100, 200], [200, 200], [200, 230], [100, 230]],
            ('Data: 15.01.2024', 0.85)
        ],
        [
            [[100, 250], [180, 250], [180, 280], [100, 280]],
            ('1 230,00 zł', 0.90)
        ],
        [
            [[100, 300], [300, 300], [300, 330], [100, 330]],
            ('Suma brutto: 1 230,00 zł', 0.87)
        ]
    ]
    
    # Sample extracted data from PaddleOCR processing
    extracted_data = {
        'numer_faktury': 'FV/001/2024',
        'sprzedawca_nazwa': 'ABC Company Sp. z o.o.',
        'sprzedawca_nip': '5260001246',
        'data_wystawienia': '15.01.2024',
        'suma_brutto': '1230.00',
        'pozycje': [
            {
                'nazwa': 'Usługa konsultingowa',
                'ilosc': '1',
                'cena_netto': '1000.00',
                'stawka_vat': '23%',
                'kwota_vat': '230.00',
                'kwota_brutto': '1230.00'
            }
        ]
    }
    
    # Image dimensions (width, height)
    image_dimensions = (800, 600)
    
    print("=== PaddleOCR Confidence Calculator Example ===\n")
    
    # Calculate overall confidence
    confidence_result = calculator.calculate_overall_confidence(
        paddle_results=paddle_results,
        extracted_data=extracted_data,
        image_dimensions=image_dimensions
    )
    
    # Display results
    print(f"Overall Confidence: {confidence_result['overall_confidence']:.1f}%\n")
    
    print("Confidence Components:")
    for component in confidence_result['confidence_components']:
        print(f"  {component['source']}: {component['score']:.1f}% "
              f"(weight: {component['weight']:.2f}, "
              f"contribution: {component['weighted_contribution']:.1f})")
    
    print(f"\nField Confidences:")
    for field_name, field_data in confidence_result['field_confidences'].items():
        print(f"  {field_name}: {field_data['confidence']:.1f}%")
        if field_data.get('polish_validation'):
            validations = [k for k, v in field_data['polish_validation'].items() if v]
            if validations:
                print(f"    Polish validations passed: {', '.join(validations)}")
    
    print(f"\nSpatial Analysis:")
    spatial_details = confidence_result['spatial_analysis']
    if spatial_details:
        print(f"  Alignment Score: {spatial_details.get('alignment_score', 0):.1f}%")
        print(f"  Spacing Score: {spatial_details.get('spacing_score', 0):.1f}%")
        print(f"  Layout Score: {spatial_details.get('layout_score', 0):.1f}%")
    
    print(f"\nPolish Validation:")
    polish_details = confidence_result['polish_validation']
    if polish_details and 'pattern_scores' in polish_details:
        for pattern_type, score in polish_details['pattern_scores'].items():
            print(f"  {pattern_type}: {score:.1f}%")
    
    print(f"\nText Quality Metrics:")
    text_quality = confidence_result['text_quality_metrics']
    if text_quality:
        print(f"  Average Character Confidence: {text_quality.get('average_character_confidence', 0):.1f}%")
        print(f"  Average Text Length: {text_quality.get('average_text_length', 0):.1f}")
        print(f"  Digit Ratio: {text_quality.get('digit_ratio', 0):.2f}")
    
    # Example of field-level confidence calculation
    print(f"\n=== Field-Level Confidence Example ===\n")
    
    # Calculate confidence for a specific field
    nip_box_data = {
        'confidence': 0.92,
        'box': [[100, 150], [250, 150], [250, 180], [100, 180]]
    }
    
    field_confidence = calculator.calculate_field_confidence(
        field_name='sprzedawca_nip',
        field_value='5260001246',
        paddle_box_data=nip_box_data,
        context_data={'image_dimensions': image_dimensions}
    )
    
    print(f"NIP Field Confidence: {field_confidence['confidence']:.1f}%")
    print(f"PaddleOCR Confidence: {field_confidence['paddle_confidence']:.1f}%")
    
    print(f"\nSpatial Metrics:")
    spatial_metrics = field_confidence['spatial_metrics']
    print(f"  Width: {spatial_metrics.get('width', 0):.1f}px")
    print(f"  Height: {spatial_metrics.get('height', 0):.1f}px")
    print(f"  Aspect Ratio: {spatial_metrics.get('aspect_ratio', 0):.2f}")
    
    print(f"\nPolish Validation:")
    polish_validation = field_confidence['polish_validation']
    for validation_type, result in polish_validation.items():
        print(f"  {validation_type}: {result}")
    
    # Display calculator statistics
    print(f"\n=== Calculator Statistics ===\n")
    stats = calculator.get_calculation_stats()
    print(f"Total Calculations: {stats['total_calculations']}")
    print(f"Average Confidence: {stats['average_confidence']:.1f}%")
    print(f"Spatial Analysis Usage: {stats['spatial_analysis_usage_rate']:.1f}%")
    print(f"Polish Boost Usage: {stats['polish_boost_usage_rate']:.1f}%")


def example_nip_validation():
    """Example of NIP validation functionality"""
    
    calculator = PaddleConfidenceCalculator()
    
    print("\n=== NIP Validation Examples ===\n")
    
    # Test various NIP numbers
    test_nips = [
        '5260001246',  # Valid NIP
        '123-456-78-90',  # Invalid NIP (wrong checksum)
        '526000124',  # Too short
        '52600012466',  # Too long
        'ABC1234567'  # Invalid format
    ]
    
    for nip in test_nips:
        is_valid = calculator._validate_nip_checksum(nip)
        print(f"NIP: {nip:15} -> {'Valid' if is_valid else 'Invalid'}")


def example_polish_patterns():
    """Example of Polish pattern recognition"""
    
    calculator = PaddleConfidenceCalculator()
    
    print("\n=== Polish Pattern Recognition Examples ===\n")
    
    # Test company names
    company_names = [
        'ABC Company Sp. z o.o.',
        'XYZ Corporation S.A.',
        'Test P.P.H.U.',
        'Simple Company',  # No Polish indicators
        'Foreign Ltd.'  # No Polish indicators
    ]
    
    print("Company Name Validation:")
    for name in company_names:
        has_indicators = calculator._check_polish_company_indicators(name)
        print(f"  {name:25} -> {'Has Polish indicators' if has_indicators else 'No Polish indicators'}")
    
    # Test date formats
    dates = [
        '15.01.2024',
        '15-01-2024',
        '15 stycznia 2024',
        '2024-01-15',  # Invalid format
        '15/01/2024'  # Invalid format
    ]
    
    print(f"\nDate Format Validation:")
    for date in dates:
        is_valid = calculator._validate_polish_date_format(date)
        print(f"  {date:20} -> {'Valid Polish format' if is_valid else 'Invalid format'}")
    
    # Test amount formats
    amounts = [
        '1230.00',
        '1230,00',
        '1 230,00 zł',
        '1230.00 PLN',
        '$1230.00',  # Invalid
        'invalid_amount'  # Invalid
    ]
    
    print(f"\nAmount Format Validation:")
    for amount in amounts:
        is_valid = calculator._validate_polish_amount_format(amount)
        print(f"  {amount:15} -> {'Valid Polish format' if is_valid else 'Invalid format'}")


if __name__ == '__main__':
    # Run examples
    example_paddle_confidence_calculation()
    example_nip_validation()
    example_polish_patterns()