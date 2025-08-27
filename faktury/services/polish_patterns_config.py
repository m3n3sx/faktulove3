"""
Polish Invoice Patterns Configuration
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PatternType(Enum):
    NIP = "nip"
    REGON = "regon"
    KRS = "krs"
    DATE = "date"
    CURRENCY = "currency"
    VAT_RATE = "vat_rate"
    INVOICE_NUMBER = "invoice_number"
    POSTAL_CODE = "postal_code"


@dataclass
class PatternMatch:
    value: str
    pattern_type: PatternType
    confidence: float
    validation_passed: bool
    position: Optional[Tuple[int, int]] = None
    context: Optional[str] = None


class PolishPatternsConfig:
    """Polish patterns configuration for invoice processing"""
    
    NIP_PATTERNS = {
        'standard': r'\b\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b',
        'with_prefix': r'(?:NIP[:\s]*)?(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})\b',
        'loose': r'\b\d{10}\b',
    }
    
    DATE_PATTERNS = {
        'dd_mm_yyyy_dot': r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b',
        'dd_mm_yyyy_dash': r'\b(\d{1,2})-(\d{1,2})-(\d{4})\b',
        'yyyy_mm_dd': r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',
    }
    
    CURRENCY_PATTERNS = {
        'pln_symbol': r'(\d+[,.]?\d*)\s*(?:zł|PLN)',
        'simple_amount': r'\b(\d+[,.]\d{2})\b',
    }
    
    VAT_RATES = {
        'standard_rates': [0, 5, 8, 23],
        'patterns': {
            'percentage': r'(\d{1,2})%',
            'vat_context': r'(?:VAT|podatek)[:\s]*(\d{1,2})%',
        }
    }
    
    INVOICE_NUMBER_PATTERNS = {
        'fv_format': r'(?:FV|Faktura)[/\-\s]*(\d+)[/\-]?(\d{2,4})?',
        'standard': r'(?:Nr|Numer)[:\s]*([A-Z0-9/\-]+)',
    }
    
    POSTAL_CODE_PATTERNS = {
        'standard': r'\b(\d{2})-(\d{3})\b',
    }

    @staticmethod
    def validate_nip(nip: str) -> bool:
        """Validate Polish NIP number using checksum algorithm"""
        clean_nip = re.sub(r'[^0-9]', '', nip)
        
        if len(clean_nip) != 10:
            return False
            
        digits = [int(d) for d in clean_nip]
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        
        checksum = sum(digit * weight for digit, weight in zip(digits[:9], weights)) % 11
        
        if checksum == 10:
            return False
            
        return checksum == digits[9]

    @staticmethod
    def validate_polish_date(date_str: str) -> Tuple[bool, Optional[str]]:
        """Validate and normalize Polish date formats"""
        date_str = date_str.strip()
        
        patterns = [
            (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', '%d.%m.%Y'),
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%d-%m-%Y'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        ]
        
        for pattern, format_str in patterns:
            match = re.match(pattern, date_str)
            if match:
                try:
                    from datetime import datetime
                    if format_str.startswith('%Y'):
                        year, month, day = match.groups()
                        date_obj = datetime(int(year), int(month), int(day))
                    else:
                        day, month, year = match.groups()
                        date_obj = datetime(int(year), int(month), int(day))
                    
                    return True, date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        return False, None

    @staticmethod
    def validate_vat_rate(rate_str: str) -> Tuple[bool, Optional[float]]:
        """Validate Polish VAT rate"""
        match = re.search(r'(\d{1,2})', rate_str)
        if not match:
            return False, None
            
        rate = int(match.group(1))
        
        valid_rates = PolishPatternsConfig.VAT_RATES['standard_rates']
        if rate in valid_rates:
            return True, float(rate)
        
        return False, None

    @staticmethod
    def calculate_pattern_confidence(
        pattern_type: PatternType,
        value: str,
        context: Optional[str] = None,
        validation_passed: bool = False
    ) -> float:
        """Calculate confidence score for a pattern match"""
        base_confidence = 0.5
        
        if validation_passed:
            base_confidence += 0.3
        
        if pattern_type == PatternType.NIP:
            if len(re.sub(r'[^0-9]', '', value)) == 10:
                base_confidence += 0.1
            if context and re.search(r'(?i)nip|tax.id', context):
                base_confidence += 0.2
                
        elif pattern_type == PatternType.DATE:
            if re.match(r'\d{1,2}\.\d{1,2}\.\d{4}', value):
                base_confidence += 0.1
            if context and re.search(r'(?i)data|date', context):
                base_confidence += 0.2
                
        elif pattern_type == PatternType.CURRENCY:
            if re.search(r'(?i)zł|pln', value):
                base_confidence += 0.2
            if context and re.search(r'(?i)suma|total', context):
                base_confidence += 0.1
                
        elif pattern_type == PatternType.VAT_RATE:
            if '%' in value:
                base_confidence += 0.1
            if context and re.search(r'(?i)vat|podatek', context):
                base_confidence += 0.2
        
        return min(1.0, max(0.0, base_confidence))

    @staticmethod
    def extract_patterns_from_text(
        text: str,
        pattern_types: Optional[List[PatternType]] = None
    ) -> List[PatternMatch]:
        """Extract all patterns from text with confidence scoring"""
        if pattern_types is None:
            pattern_types = list(PatternType)
        
        matches = []
        
        for pattern_type in pattern_types:
            if pattern_type == PatternType.NIP:
                matches.extend(PolishPatternsConfig._extract_nip_patterns(text))
            elif pattern_type == PatternType.DATE:
                matches.extend(PolishPatternsConfig._extract_date_patterns(text))
            elif pattern_type == PatternType.CURRENCY:
                matches.extend(PolishPatternsConfig._extract_currency_patterns(text))
            elif pattern_type == PatternType.VAT_RATE:
                matches.extend(PolishPatternsConfig._extract_vat_patterns(text))
        
        return matches

    @staticmethod
    def _extract_nip_patterns(text: str) -> List[PatternMatch]:
        """Extract NIP patterns from text"""
        matches = []
        
        for pattern_name, pattern in PolishPatternsConfig.NIP_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = match.group(1) if match.groups() else match.group(0)
                validation_passed = PolishPatternsConfig.validate_nip(value)
                
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                confidence = PolishPatternsConfig.calculate_pattern_confidence(
                    PatternType.NIP, value, context, validation_passed
                )
                
                matches.append(PatternMatch(
                    value=value,
                    pattern_type=PatternType.NIP,
                    confidence=confidence,
                    validation_passed=validation_passed,
                    position=(match.start(), match.end()),
                    context=context
                ))
        
        return matches

    @staticmethod
    def _extract_date_patterns(text: str) -> List[PatternMatch]:
        """Extract date patterns from text"""
        matches = []
        
        for pattern_name, pattern in PolishPatternsConfig.DATE_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = match.group(0)
                validation_passed, normalized_date = PolishPatternsConfig.validate_polish_date(value)
                
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                confidence = PolishPatternsConfig.calculate_pattern_confidence(
                    PatternType.DATE, value, context, validation_passed
                )
                
                matches.append(PatternMatch(
                    value=normalized_date if normalized_date else value,
                    pattern_type=PatternType.DATE,
                    confidence=confidence,
                    validation_passed=validation_passed,
                    position=(match.start(), match.end()),
                    context=context
                ))
        
        return matches

    @staticmethod
    def _extract_currency_patterns(text: str) -> List[PatternMatch]:
        """Extract currency patterns from text"""
        matches = []
        
        for pattern_name, pattern in PolishPatternsConfig.CURRENCY_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = match.group(0)
                
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                confidence = PolishPatternsConfig.calculate_pattern_confidence(
                    PatternType.CURRENCY, value, context, True
                )
                
                matches.append(PatternMatch(
                    value=value,
                    pattern_type=PatternType.CURRENCY,
                    confidence=confidence,
                    validation_passed=True,
                    position=(match.start(), match.end()),
                    context=context
                ))
        
        return matches

    @staticmethod
    def _extract_vat_patterns(text: str) -> List[PatternMatch]:
        """Extract VAT rate patterns from text"""
        matches = []
        
        for pattern_name, pattern in PolishPatternsConfig.VAT_RATES['patterns'].items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = match.group(0)
                validation_passed, rate_value = PolishPatternsConfig.validate_vat_rate(value)
                
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                confidence = PolishPatternsConfig.calculate_pattern_confidence(
                    PatternType.VAT_RATE, value, context, validation_passed
                )
                
                matches.append(PatternMatch(
                    value=str(rate_value) + '%' if rate_value is not None else value,
                    pattern_type=PatternType.VAT_RATE,
                    confidence=confidence,
                    validation_passed=validation_passed,
                    position=(match.start(), match.end()),
                    context=context
                ))
        
        return matches


# Configuration constants
POLISH_VAT_RATES = PolishPatternsConfig.VAT_RATES['standard_rates']
POLISH_DATE_FORMATS = list(PolishPatternsConfig.DATE_PATTERNS.keys())
POLISH_CURRENCY_SYMBOLS = ['zł', 'PLN', 'złoty', 'złotych']

# Export main classes and functions
__all__ = [
    'PolishPatternsConfig',
    'PatternType',
    'PatternMatch',
    'POLISH_VAT_RATES',
    'POLISH_DATE_FORMATS',
    'POLISH_CURRENCY_SYMBOLS',
]
