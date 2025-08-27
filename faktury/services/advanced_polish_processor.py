#!/usr/bin/env python3
"""
Advanced Polish Invoice Processor - Enhanced Polish Legal Patterns
Comprehensive processor for Polish invoices with advanced validation and pattern recognition
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class InvoiceLayout(Enum):
    """Polish invoice layout types"""
    STANDARD = "standard"
    SIMPLIFIED = "simplified"
    PROFORMA = "proforma"
    CORRECTION = "correction"
    RECEIPT = "receipt"


@dataclass
class EntityRecognitionResult:
    """Result of ML-based entity recognition"""
    entity_type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int
    context: str


class AdvancedPolishInvoiceProcessor:
    """
    Enhanced specialized processor for Polish invoices with advanced pattern recognition,
    comprehensive validation, and legal compliance features
    """
    
    def __init__(self):
        """Initialize enhanced Polish patterns with comprehensive coverage"""
        
        # Advanced Polish patterns with weights and special cases
        self.POLISH_PATTERNS = {
            'nip_validation': {
                'weights': [6, 5, 7, 2, 3, 4, 5, 6, 7],
                'special_cases': ['0000000000', '1111111111', '2222222222', '3333333333', 
                                '4444444444', '5555555555', '6666666666', '7777777777',
                                '8888888888', '9999999999'],
                'patterns': [
                    r'\b\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}\b',
                    r'NIP\s*[:]?\s*(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2})',
                    r'VAT[-\s]*(\d{10})',
                    r'PL\s*(\d{10})',
                    r'(?:Identyfikator\s+podatkowy|Nr\s+VAT)[-:\s]*(\d{10})'
                ]
            },
            'regon_validation': {
                '9_digit': {
                    'weights': [8, 9, 2, 3, 4, 5, 6, 7],
                    'patterns': [
                        r'\b\d{9}\b',
                        r'REGON\s*[:]?\s*(\d{9})',
                        r'(?:Numer\s+)?REGON[-:\s]*(\d{9})'
                    ]
                },
                '14_digit': {
                    'weights': [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8],
                    'patterns': [
                        r'\b\d{14}\b',
                        r'REGON\s*[:]?\s*(\d{14})',
                        r'(?:Numer\s+)?REGON[-:\s]*(\d{14})'
                    ]
                }
            },
            'vat_rates': ['23', '8', '5', '0', 'zw', 'np', 'oo'],
            'company_forms': [
                'Spółka z ograniczoną odpowiedzialnością',
                'Sp. z o.o.',
                'Spółka Akcyjna',
                'S.A.',
                'Spółka jawna',
                'Sp. j.',
                'Spółka partnerska',
                'Sp. p.',
                'Spółka komandytowa',
                'Sp. k.',
                'Spółka komandytowo-akcyjna',
                'S.K.A.',
                'Przedsiębiorstwo Państwowe',
                'P.P.',
                'Zakład Pracy Chronionej',
                'Z.P.Ch.',
                'Spółdzielnia',
                'Fundacja',
                'Stowarzyszenie',
                'Organizacja Pożytku Publicznego',
                'O.P.P.'
            ]
        }
        
        # Enhanced Polish date patterns with comprehensive format support
        self.date_patterns = [
            # Standard formats
            r'\b(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})\b',  # DD.MM.YYYY, DD-MM-YYYY, DD/MM/YYYY
            r'\b(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})\b',  # YYYY.MM.DD, YYYY-MM-DD, YYYY/MM/DD
            r'\b(\d{1,2})\s+(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+(\d{4})\b',  # DD month YYYY
            # Labeled dates
            r'(?:Data\s+wystawienia|Data\s+sprzedaży|Termin\s+płatności|Data\s+odbioru)[-:\s]*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
            r'(?:Wystawiono|Sprzedano|Płatność|Odbioru)[-:\s]*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
            # Short year formats
            r'\b(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{2})\b',  # DD.MM.YY
            r'\b(\d{2})[.\-/](\d{1,2})[.\-/](\d{4})\b',    # YY.MM.YYYY
        ]
        
        # Polish month names mapping
        self.polish_months = {
            'stycznia': 1, 'lutego': 2, 'marca': 3, 'kwietnia': 4, 'maja': 5, 'czerwca': 6,
            'lipca': 7, 'sierpnia': 8, 'września': 9, 'października': 10, 'listopada': 11, 'grudnia': 12
        }
        
        # Enhanced VAT rate patterns
        self.vat_rate_patterns = [
            r'(\d{1,2}[,\.]\d{1,2})\s*%?\s*VAT',
            r'VAT\s*(\d{1,2}[,\.]\d{1,2})\s*%?',
            r'(\d{1,2}[,\.]\d{1,2})\s*%?\s*podatku',
            r'podatek\s*(\d{1,2}[,\.]\d{1,2})\s*%?',
            r'stawka\s*(\d{1,2}[,\.]\d{1,2})\s*%?',
            r'(\d{1,2}[,\.]\d{1,2})\s*%?\s*stawka',
            # Special VAT cases
            r'(zw|ZW)\s*[-–]\s*zwolniony',
            r'(np|NP)\s*[-–]\s*nie\s+podlega',
            r'(oo|OO)\s*[-–]\s*odwrotne\s+obciążenie',
            r'zwolniony\s+z\s+VAT',
            r'nie\s+podlega\s+VAT',
            r'odwrotne\s+obciążenie'
        ]
        
        # Enhanced currency patterns for Polish zloty
        self.currency_patterns = [
            r'([\d\s,]+)\s*(?:zł|PLN|złoty|złotych)',
            r'(?:suma|kwota|netto|brutto|VAT|razem|do\s+zapłaty)[:\s]*([\d\s,]+)\s*(?:zł|PLN)?',
            r'([\d\s,]+)\s*(?:EUR|€|euro)',
            r'([\d\s,]+)\s*(?:USD|\$|dolar)',
            r'([\d\s,]+)\s*(?:GBP|£|funt)',
            r'([\d\s,]+)\s*(?:CHF|frank)'
        ]
        
        # Enhanced invoice number patterns
        self.invoice_patterns = [
            r'(?:faktur[ay]?|invoice)\s*(?:nr|nr\.|numer|number)?[.:\s]*([a-zA-Z0-9\/\-_]+)',
            r'FV[/\-]?(\d+[/\-]\d+)',
            r'(\d{2,4}[/\-]\d{2,4}[/\-]\d{2,4})',
            r'Nr\s*(?:faktury|invoice)[.:\s]*([a-zA-Z0-9\/\-_]+)',
            r'(?:Numer|Number)\s*(?:faktury|invoice)[.:\s]*([a-zA-Z0-9\/\-_]+)',
            r'FAK\s*(\d+)',
            r'INV\s*(\d+)',
            r'(\d{4}\/\d{2}\/\d+)',
            r'(\d{2}\/\d{4}\/\d+)'
        ]

    def validate_nip_advanced(self, nip: str) -> Dict[str, Any]:
        """
        Advanced NIP validation with comprehensive checks
        
        Args:
            nip: NIP number to validate
            
        Returns:
            Dictionary with validation results and details
        """
        try:
            # Remove non-digit characters
            nip_clean = re.sub(r'[^\d]', '', nip)
            
            # Check length
            if len(nip_clean) != 10:
                return {
                    'is_valid': False,
                    'error': 'Invalid length',
                    'expected_length': 10,
                    'actual_length': len(nip_clean),
                    'confidence': 0.0
                }
            
            # Check for special cases (test numbers)
            if nip_clean in self.POLISH_PATTERNS['nip_validation']['special_cases']:
                return {
                    'is_valid': True,
                    'is_test_number': True,
                    'confidence': 0.5,
                    'warning': 'Test NIP number detected'
                }
            
            # Check for all same digits
            if len(set(nip_clean)) == 1:
                return {
                    'is_valid': False,
                    'error': 'All digits are the same',
                    'confidence': 0.0
                }
            
            # Polish NIP checksum algorithm
            weights = self.POLISH_PATTERNS['nip_validation']['weights']
            checksum = 0
            
            for i in range(9):
                checksum += int(nip_clean[i]) * weights[i]
            
            checksum = checksum % 11
            if checksum == 10:
                checksum = 0
            
            is_valid = checksum == int(nip_clean[9])
            
            # Calculate confidence based on various factors
            confidence = 1.0 if is_valid else 0.0
            
            # Additional confidence boost for valid checksum
            if is_valid:
                confidence = 1.0
                # Check for realistic patterns
                if nip_clean.startswith('0'):  # Government entities
                    confidence = 0.95
                elif nip_clean.startswith('1'):  # Private companies
                    confidence = 0.98
                else:
                    confidence = 0.97
            
            return {
                'is_valid': is_valid,
                'checksum_valid': is_valid,
                'confidence': confidence,
                'checksum_calculated': checksum,
                'checksum_expected': int(nip_clean[9]),
                'formatted_nip': f"{nip_clean[:3]}-{nip_clean[3:6]}-{nip_clean[6:8]}-{nip_clean[8:]}"
            }
            
        except Exception as e:
            logger.error(f"Advanced NIP validation failed: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'confidence': 0.0
            }

    def validate_regon_advanced(self, regon: str) -> Dict[str, Any]:
        """
        Advanced REGON validation with comprehensive checks
        
        Args:
            regon: REGON number to validate
            
        Returns:
            Dictionary with validation results and details
        """
        try:
            # Remove non-digit characters
            regon_clean = re.sub(r'[^\d]', '', regon)
            
            # Check length
            if len(regon_clean) not in [9, 14]:
                return {
                    'is_valid': False,
                    'error': 'Invalid length',
                    'expected_lengths': [9, 14],
                    'actual_length': len(regon_clean),
                    'confidence': 0.0
                }
            
            # REGON checksum algorithm
            if len(regon_clean) == 9:
                weights = self.POLISH_PATTERNS['regon_validation']['9_digit']['weights']
                checksum = 0
                
                for i in range(8):
                    checksum += int(regon_clean[i]) * weights[i]
                
                checksum = checksum % 11
                if checksum == 10:
                    checksum = 0
                
                is_valid = checksum == int(regon_clean[8])
                regon_type = '9-digit'
                
            elif len(regon_clean) == 14:
                weights = self.POLISH_PATTERNS['regon_validation']['14_digit']['weights']
                checksum = 0
                
                for i in range(13):
                    checksum += int(regon_clean[i]) * weights[i]
                
                checksum = checksum % 11
                if checksum == 10:
                    checksum = 0
                
                is_valid = checksum == int(regon_clean[13])
                regon_type = '14-digit'
            
            # Calculate confidence
            confidence = 1.0 if is_valid else 0.0
            
            # Additional validation for 14-digit REGON
            if len(regon_clean) == 14 and is_valid:
                # Check if first 9 digits form a valid 9-digit REGON
                first_nine = regon_clean[:9]
                nine_digit_validation = self.validate_regon_advanced(first_nine)
                if nine_digit_validation['is_valid']:
                    confidence = 0.99
                else:
                    confidence = 0.95
            
            return {
                'is_valid': is_valid,
                'regon_type': regon_type,
                'checksum_valid': is_valid,
                'confidence': confidence,
                'checksum_calculated': checksum,
                'checksum_expected': int(regon_clean[-1]),
                'formatted_regon': regon_clean
            }
            
        except Exception as e:
            logger.error(f"Advanced REGON validation failed: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'confidence': 0.0
            }

    def parse_polish_date_comprehensive(self, date_str: str) -> Dict[str, Any]:
        """
        Comprehensive Polish date parsing with multiple format support
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Dictionary with parsed date and validation results
        """
        try:
            # Try different date formats
            parsed_date = None
            format_used = None
            confidence = 0.0
            
            # Standard formats
            for pattern in self.date_patterns:
                match = re.search(pattern, date_str, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        # Handle DD.MM.YYYY format
                        if len(groups[0]) <= 2 and len(groups[1]) <= 2 and len(groups[2]) == 4:
                            try:
                                day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                                if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100:
                                    parsed_date = datetime(year, month, day)
                                    format_used = 'DD.MM.YYYY'
                                    confidence = 0.95
                                    break
                            except ValueError:
                                continue
                        
                        # Handle YYYY.MM.DD format
                        elif len(groups[0]) == 4 and len(groups[1]) <= 2 and len(groups[2]) <= 2:
                            try:
                                year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                                if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100:
                                    parsed_date = datetime(year, month, day)
                                    format_used = 'YYYY.MM.DD'
                                    confidence = 0.95
                                    break
                            except ValueError:
                                continue
                        
                        # Handle Polish month names
                        elif groups[1].lower() in self.polish_months:
                            try:
                                day = int(groups[0])
                                month = self.polish_months[groups[1].lower()]
                                year = int(groups[2])
                                if 1 <= day <= 31 and 1900 <= year <= 2100:
                                    parsed_date = datetime(year, month, day)
                                    format_used = 'DD month YYYY'
                                    confidence = 0.98
                                    break
                            except ValueError:
                                continue
            
            if parsed_date:
                return {
                    'is_valid': True,
                    'parsed_date': parsed_date,
                    'format_used': format_used,
                    'confidence': confidence,
                    'iso_format': parsed_date.strftime('%Y-%m-%d'),
                    'polish_format': parsed_date.strftime('%d.%m.%Y'),
                    'year': parsed_date.year,
                    'month': parsed_date.month,
                    'day': parsed_date.day
                }
            else:
                return {
                    'is_valid': False,
                    'error': 'Unable to parse date format',
                    'confidence': 0.0
                }
                
        except Exception as e:
            logger.error(f"Comprehensive date parsing failed: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'confidence': 0.0
            }

    def validate_vat_rate_polish(self, vat_rate: str) -> Dict[str, Any]:
        """
        Validate Polish VAT rates according to current law
        
        Args:
            vat_rate: VAT rate to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Normalize VAT rate
            vat_normalized = vat_rate.lower().strip()
            
            # Check for special VAT cases
            if vat_normalized in ['zw', 'zwolniony', 'zwolniony z vat']:
                return {
                    'is_valid': True,
                    'vat_type': 'zwolniony',
                    'rate': 0,
                    'confidence': 0.95,
                    'description': 'Zwolniony z VAT'
                }
            
            if vat_normalized in ['np', 'nie podlega', 'nie podlega vat']:
                return {
                    'is_valid': True,
                    'vat_type': 'nie_podlega',
                    'rate': 0,
                    'confidence': 0.95,
                    'description': 'Nie podlega VAT'
                }
            
            if vat_normalized in ['oo', 'odwrotne obciążenie', 'reverse charge']:
                return {
                    'is_valid': True,
                    'vat_type': 'odwrotne_obciazenie',
                    'rate': 0,
                    'confidence': 0.95,
                    'description': 'Odwrotne obciążenie'
                }
            
            # Check numeric VAT rates
            try:
                rate_float = float(vat_normalized.replace(',', '.'))
                
                # Validate against Polish VAT rates
                valid_rates = [0, 5, 8, 23]
                if rate_float in valid_rates:
                    return {
                        'is_valid': True,
                        'vat_type': 'standard',
                        'rate': rate_float,
                        'confidence': 0.98,
                        'description': f'Stawka {rate_float}%'
                    }
                else:
                    return {
                        'is_valid': False,
                        'error': f'Invalid VAT rate: {rate_float}%',
                        'valid_rates': valid_rates,
                        'confidence': 0.0
                    }
                    
            except ValueError:
                return {
                    'is_valid': False,
                    'error': 'Invalid VAT rate format',
                    'confidence': 0.0
                }
                
        except Exception as e:
            logger.error(f"VAT rate validation failed: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'confidence': 0.0
            }

    def recognize_polish_company_form(self, company_name: str) -> Dict[str, Any]:
        """
        Recognize Polish company legal forms
        
        Args:
            company_name: Company name to analyze
            
        Returns:
            Dictionary with recognition results
        """
        try:
            company_lower = company_name.lower()
            recognized_forms = []
            confidence = 0.0
            
            # Check for company forms
            for form in self.POLISH_PATTERNS['company_forms']:
                form_lower = form.lower()
                if form_lower in company_lower:
                    recognized_forms.append({
                        'form': form,
                        'position': company_lower.find(form_lower),
                        'confidence': 0.9
                    })
            
            # Check for abbreviations
            abbreviations = {
                'sp. z o.o.': 'Spółka z ograniczoną odpowiedzialnością',
                's.a.': 'Spółka Akcyjna',
                'sp. j.': 'Spółka jawna',
                'sp. p.': 'Spółka partnerska',
                'sp. k.': 'Spółka komandytowa',
                's.k.a.': 'Spółka komandytowo-akcyjna',
                'p.p.': 'Przedsiębiorstwo Państwowe',
                'z.p.ch.': 'Zakład Pracy Chronionej',
                'o.p.p.': 'Organizacja Pożytku Publicznego'
            }
            
            for abbrev, full_form in abbreviations.items():
                if abbrev in company_lower:
                    recognized_forms.append({
                        'form': full_form,
                        'abbreviation': abbrev,
                        'position': company_lower.find(abbrev),
                        'confidence': 0.95
                    })
            
            # Calculate overall confidence
            if recognized_forms:
                confidence = max(form['confidence'] for form in recognized_forms)
                primary_form = max(recognized_forms, key=lambda x: x['confidence'])
            else:
                primary_form = None
            
            return {
                'is_recognized': len(recognized_forms) > 0,
                'recognized_forms': recognized_forms,
                'primary_form': primary_form,
                'confidence': confidence,
                'total_forms_found': len(recognized_forms)
            }
            
        except Exception as e:
            logger.error(f"Company form recognition failed: {e}")
            return {
                'is_recognized': False,
                'error': str(e),
                'confidence': 0.0
            }

    def extract_all_advanced_patterns(self, text: str) -> Dict[str, Any]:
        """
        Extract all advanced patterns from text with comprehensive validation
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with all extracted patterns and validation results
        """
        try:
            results = {
                'nip_numbers': [],
                'regon_numbers': [],
                'vat_rates': [],
                'dates': [],
                'currency_amounts': [],
                'invoice_numbers': [],
                'company_forms': [],
                'validation_results': {}
            }
            
            # Extract NIP numbers with validation
            nip_matches = re.findall(r'\b\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}\b', text)
            for nip in nip_matches:
                nip_clean = re.sub(r'[^\d]', '', nip)
                if len(nip_clean) == 10:
                    validation = self.validate_nip_advanced(nip_clean)
                    results['nip_numbers'].append({
                        'value': nip_clean,
                        'original': nip,
                        'validation': validation
                    })
            
            # Extract REGON numbers with validation
            regon_matches = re.findall(r'\b\d{9}\b|\b\d{14}\b', text)
            for regon in regon_matches:
                validation = self.validate_regon_advanced(regon)
                results['regon_numbers'].append({
                    'value': regon,
                    'validation': validation
                })
            
            # Extract VAT rates with validation
            for pattern in self.vat_rate_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    validation = self.validate_vat_rate_polish(match)
                    results['vat_rates'].append({
                        'value': match,
                        'validation': validation
                    })
            
            # Extract dates with comprehensive parsing
            for pattern in self.date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        date_str = '.'.join(match)
                    else:
                        date_str = match
                    parsing = self.parse_polish_date_comprehensive(date_str)
                    results['dates'].append({
                        'value': date_str,
                        'parsing': parsing
                    })
            
            # Extract currency amounts
            for pattern in self.currency_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    results['currency_amounts'].append({
                        'value': match.strip(),
                        'pattern_used': pattern
                    })
            
            # Extract invoice numbers
            for pattern in self.invoice_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    results['invoice_numbers'].append({
                        'value': match,
                        'pattern_used': pattern
                    })
            
            # Extract company forms
            for form in self.POLISH_PATTERNS['company_forms']:
                if form.lower() in text.lower():
                    recognition = self.recognize_polish_company_form(form)
                    results['company_forms'].append({
                        'form': form,
                        'recognition': recognition
                    })
            
            # Calculate overall validation statistics
            results['validation_results'] = {
                'total_nip_found': len(results['nip_numbers']),
                'valid_nip_count': len([n for n in results['nip_numbers'] if n['validation']['is_valid']]),
                'total_regon_found': len(results['regon_numbers']),
                'valid_regon_count': len([r for r in results['regon_numbers'] if r['validation']['is_valid']]),
                'total_vat_rates_found': len(results['vat_rates']),
                'valid_vat_rates_count': len([v for v in results['vat_rates'] if v['validation']['is_valid']]),
                'total_dates_found': len(results['dates']),
                'valid_dates_count': len([d for d in results['dates'] if d['parsing']['is_valid']]),
                'total_company_forms_found': len(results['company_forms']),
                'recognized_company_forms_count': len([c for c in results['company_forms'] if c['recognition']['is_recognized']])
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Advanced pattern extraction failed: {e}")
            return {
                'error': str(e),
                'confidence': 0.0
            }

    def validate_polish_invoice_comprehensive(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of Polish invoice data
        
        Args:
            extracted_data: Extracted invoice data
            
        Returns:
            Dictionary with comprehensive validation results
        """
        try:
            validation_results = {
                'is_valid_polish_invoice': False,
                'validation_score': 0.0,
                'required_fields_present': [],
                'optional_fields_present': [],
                'validation_errors': [],
                'validation_warnings': [],
                'confidence_score': 0.0
            }
            
            # Required fields for Polish invoice
            required_fields = ['numer_faktury', 'data_wystawienia', 'sprzedawca_nip', 'nabywca_nip']
            optional_fields = ['regon', 'krs', 'vat_rates', 'suma_brutto', 'suma_netto', 'suma_vat']
            
            # Check required fields
            for field in required_fields:
                if field in extracted_data and extracted_data[field]:
                    validation_results['required_fields_present'].append(field)
                else:
                    validation_results['validation_errors'].append(f'Missing required field: {field}')
            
            # Check optional fields
            for field in optional_fields:
                if field in extracted_data and extracted_data[field]:
                    validation_results['optional_fields_present'].append(field)
            
            # Calculate validation score
            required_score = len(validation_results['required_fields_present']) / len(required_fields)
            optional_score = len(validation_results['optional_fields_present']) / len(optional_fields)
            
            validation_results['validation_score'] = (required_score * 0.7) + (optional_score * 0.3)
            validation_results['is_valid_polish_invoice'] = validation_results['validation_score'] >= 0.8
            
            # Calculate confidence score
            confidence_factors = []
            
            # NIP validation confidence
            if 'sprzedawca_nip' in extracted_data:
                nip_validation = self.validate_nip_advanced(extracted_data['sprzedawca_nip'])
                confidence_factors.append(nip_validation.get('confidence', 0.0))
            
            if 'nabywca_nip' in extracted_data:
                nip_validation = self.validate_nip_advanced(extracted_data['nabywca_nip'])
                confidence_factors.append(nip_validation.get('confidence', 0.0))
            
            # Date validation confidence
            if 'data_wystawienia' in extracted_data:
                date_parsing = self.parse_polish_date_comprehensive(extracted_data['data_wystawienia'])
                confidence_factors.append(date_parsing.get('confidence', 0.0))
            
            # Calculate overall confidence
            if confidence_factors:
                validation_results['confidence_score'] = sum(confidence_factors) / len(confidence_factors)
            else:
                validation_results['confidence_score'] = validation_results['validation_score']
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Comprehensive validation failed: {e}")
            return {
                'is_valid_polish_invoice': False,
                'error': str(e),
                'confidence_score': 0.0
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the processor"""
        return {
            'processor_version': '2.0-advanced',
            'features': [
                'Advanced NIP validation with checksum',
                'REGON validation (9 and 14 digit)',
                'Comprehensive Polish date parsing',
                'VAT rate validation',
                'Polish company form recognition',
                'Comprehensive pattern extraction'
            ],
            'supported_patterns': len(self.POLISH_PATTERNS),
            'date_formats_supported': len(self.date_patterns),
            'vat_rates_supported': len(self.POLISH_PATTERNS['vat_rates']),
            'company_forms_supported': len(self.POLISH_PATTERNS['company_forms'])
        }
