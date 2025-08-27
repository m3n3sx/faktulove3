# Polish Patterns Configuration

This document describes the comprehensive Polish patterns configuration for OCR processing of Polish invoices in the FaktuLove system.

## Overview

The `PolishPatternsConfig` class provides:
- Pattern recognition for Polish-specific data (NIP, REGON, KRS, dates, currency, VAT rates)
- Validation algorithms with checksum verification
- Confidence scoring for extracted patterns
- Context-aware pattern matching

## Supported Patterns

### 1. NIP (Tax Identification Number)

**Patterns:**
- `standard`: `\b\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b`
- `with_prefix`: `(?:NIP[:\s]*)?(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})\b`
- `loose`: `\b\d{10}\b`

**Validation:**
- Uses official Polish NIP checksum algorithm
- Validates 10-digit format
- Weights: [6, 5, 7, 2, 3, 4, 5, 6, 7]

**Examples:**
- `123-456-78-90` (with dashes)
- `123 456 78 90` (with spaces)
- `1234567890` (without separators)

### 2. REGON (Business Registry Number)

**Patterns:**
- `regon_9`: `\b\d{9}\b` (9-digit REGON)
- `regon_14`: `\b\d{14}\b` (14-digit REGON)
- `with_prefix`: `(?:REGON[:\s]*)?(\d{9}|\d{14})\b`

**Validation:**
- Supports both 9-digit and 14-digit REGON numbers
- Uses official REGON checksum algorithms
- 9-digit weights: [8, 9, 2, 3, 4, 5, 6, 7]
- 14-digit weights: [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]

### 3. KRS (Court Registry Number)

**Patterns:**
- `standard`: `\b\d{10}\b`
- `with_prefix`: `(?:KRS[:\s]*)?(\d{10})\b`

**Validation:**
- Must be exactly 10 digits
- Cannot start with 0

### 4. Polish Date Formats

**Patterns:**
- `dd_mm_yyyy_dot`: `\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b`
- `dd_mm_yyyy_dash`: `\b(\d{1,2})-(\d{1,2})-(\d{4})\b`
- `yyyy_mm_dd`: `\b(\d{4})-(\d{1,2})-(\d{1,2})\b`

**Validation:**
- Validates date ranges (1-31 days, 1-12 months)
- Normalizes to ISO format (YYYY-MM-DD)
- Handles leap years

**Examples:**
- `15.01.2024` → `2024-01-15`
- `15-01-2024` → `2024-01-15`
- `2024-01-15` → `2024-01-15`

### 5. Currency Patterns (Polish Złoty)

**Patterns:**
- `pln_symbol`: `(\d+[,.]?\d*)\s*(?:zł|PLN)`
- `simple_amount`: `\b(\d+[,.]\d{2})\b`

**Examples:**
- `1230,00 zł`
- `1230.00 PLN`
- `1230,00`

### 6. Polish VAT Rates

**Standard Rates:** [0, 5, 8, 23]

**Patterns:**
- `percentage`: `(\d{1,2})%`
- `vat_context`: `(?:VAT|podatek)[:\s]*(\d{1,2})%`

**Examples:**
- `23%`
- `VAT 8%`
- `podatek 5%`

### 7. Invoice Number Patterns

**Patterns:**
- `fv_format`: `(?:FV|Faktura)[/\-\s]*(\d+)[/\-]?(\d{2,4})?`
- `standard`: `(?:Nr|Numer)[:\s]*([A-Z0-9/\-]+)`

**Examples:**
- `FV/001/2024`
- `Faktura 123/24`
- `Nr: ABC-001/2024`

### 8. Polish Postal Codes

**Pattern:**
- `standard`: `\b(\d{2})-(\d{3})\b`

**Examples:**
- `00-001`
- `30-123`

## Confidence Scoring

The confidence scoring algorithm considers:

### Base Confidence: 0.5

### Validation Bonus: +0.3
- Applied when pattern passes validation checks

### Pattern-Specific Bonuses:

**NIP:**
- +0.1 for correct 10-digit format
- +0.2 for context keywords ("NIP", "tax ID")

**Date:**
- +0.1 for Polish format (DD.MM.YYYY)
- +0.2 for context keywords ("data", "date")

**Currency:**
- +0.2 for Polish currency symbols ("zł", "PLN")
- +0.1 for context keywords ("suma", "total")

**VAT Rate:**
- +0.1 for percentage symbol
- +0.2 for context keywords ("VAT", "podatek")

### Confidence Range: 0.0 - 1.0

## Usage Examples

### Basic Pattern Extraction

```python
from faktury.services.polish_patterns_config import PolishPatternsConfig, PatternType

config = PolishPatternsConfig()

# Extract all patterns from text
text = "NIP: 123-456-78-90, Data: 15.01.2024, VAT 23%"
matches = config.extract_patterns_from_text(text)

for match in matches:
    print(f"{match.pattern_type.value}: {match.value} (confidence: {match.confidence:.2f})")
```

### Specific Pattern Validation

```python
# Validate NIP
is_valid = config.validate_nip("123-456-78-90")
print(f"NIP valid: {is_valid}")

# Validate and normalize date
is_valid, normalized = config.validate_polish_date("15.01.2024")
print(f"Date: {normalized}")

# Validate VAT rate
is_valid, rate = config.validate_vat_rate("23%")
print(f"VAT rate: {rate}%")
```

### Extract Specific Pattern Types

```python
# Extract only NIP and date patterns
matches = config.extract_patterns_from_text(text, [PatternType.NIP, PatternType.DATE])
```

## Integration with PaddleOCR

The Polish patterns configuration is designed to work seamlessly with the PaddleOCR service:

```python
from faktury.services.paddle_ocr_service import PaddleOCRService
from faktury.services.polish_patterns_config import PolishPatternsConfig

# In PaddleOCR service
config = PolishPatternsConfig()
ocr_text = "extracted text from PaddleOCR"

# Extract and validate patterns
matches = config.extract_patterns_from_text(ocr_text)

# Filter high-confidence matches
high_confidence_matches = [m for m in matches if m.confidence > 0.8]
```

## Configuration Constants

```python
from faktury.services.polish_patterns_config import (
    POLISH_VAT_RATES,
    POLISH_DATE_FORMATS,
    POLISH_CURRENCY_SYMBOLS
)

print(f"VAT rates: {POLISH_VAT_RATES}")  # [0, 5, 8, 23]
print(f"Date formats: {POLISH_DATE_FORMATS}")  # ['dd_mm_yyyy_dot', ...]
print(f"Currency symbols: {POLISH_CURRENCY_SYMBOLS}")  # ['zł', 'PLN', ...]
```

## Error Handling

The configuration handles various error scenarios:

- **Invalid formats**: Returns False for validation methods
- **Missing patterns**: Returns empty lists for extraction methods
- **Malformed input**: Gracefully handles regex errors
- **Date validation**: Handles invalid dates (e.g., 32.01.2024)

## Performance Considerations

- **Compiled regex patterns**: Patterns are compiled once and reused
- **Context extraction**: Limited to 50 characters before/after match
- **Confidence calculation**: Optimized for real-time processing
- **Memory usage**: Minimal memory footprint for pattern storage

## Testing

Comprehensive test suite available in `faktury/tests/test_polish_patterns_config.py`:

```bash
python manage.py test faktury.tests.test_polish_patterns_config
```

## Future Enhancements

Planned improvements:
- Support for additional Polish business identifiers
- Enhanced spatial analysis for invoice layout
- Machine learning-based confidence scoring
- Support for handwritten text patterns
- Integration with Polish business registries for validation