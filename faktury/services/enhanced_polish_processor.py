"""
Enhanced Polish Invoice Processor for PaddleOCR Integration

This module provides specialized pattern recognition and validation for Polish invoices,
including NIP validation with checksum verification, REGON/KRS extraction, Polish date
format parsing, and VAT rate recognition.
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class EnhancedPolishProcessor:
    """
    Enhanced processor for Polish invoice pattern extraction and validation.
    Designed to work with PaddleOCR results for maximum accuracy on Polish documents.
    """
    
    # Polish VAT rates (current as of 2024)
    POLISH_VAT_RATES = [0, 5, 8, 23]
    
    # Polish date format patterns
    DATE_PATTERNS = [
        r'\b(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})\b',  # DD.MM.YYYY, DD-MM-YYYY, DD/MM/YYYY
        r'\b(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})\b',  # YYYY.MM.DD, YYYY-MM-DD, YYYY/MM/DD
        r'\b(\d{1,2})\s+(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+(\d{4})\b',  # DD month YYYY
    ]
    
    # Polish month names mapping
    POLISH_MONTHS = {
        'stycznia': 1, 'lutego': 2, 'marca': 3, 'kwietnia': 4, 'maja': 5, 'czerwca': 6,
        'lipca': 7, 'sierpnia': 8, 'września': 9, 'października': 10, 'listopada': 11, 'grudnia': 12
    }
    
    # Currency patterns for Polish zloty
    CURRENCY_PATTERNS = [
        r'(\d+(?:[,\.]\d{2})?)\s*(?:zł|PLN|złotych)',  # Amount with currency
        r'(?:suma|kwota|netto|brutto|VAT)[:\s]*(\d+[,\.]\d{2})',  # Labeled amounts
    ]
    
    def __init__(self):
        """Initialize the Enhanced Polish Processor."""
        self.logger = logging.getLogger(__name__)
        
    def extract_polish_invoice_fields(self, text: str, ocr_boxes: List[Dict] = None) -> Dict[str, Any]:
        """
        Extract Polish invoice fields using spatial analysis and pattern recognition.
        
        Args:
            text: Raw OCR text
            ocr_boxes: List of OCR bounding boxes with text and coordinates
            
        Returns:
            Dictionary containing extracted Polish invoice fields
        """
        extracted_data = {}
        
        if not text:
            return extracted_data
        
        try:
            # Extract NIP numbers
            nip_numbers = self.extract_nip_numbers(text)
            if nip_numbers:
                extracted_data['sprzedawca_nip'] = nip_numbers[0]  # First NIP is usually seller
                if len(nip_numbers) > 1:
                    extracted_data['nabywca_nip'] = nip_numbers[1]  # Second NIP is buyer
            
            # Extract REGON numbers
            regon_numbers = self.extract_regon_numbers(text)
            if regon_numbers:
                extracted_data['regon'] = regon_numbers[0]
            
            # Extract KRS numbers
            krs_numbers = self.extract_krs_numbers(text)
            if krs_numbers:
                extracted_data['krs'] = krs_numbers[0]
            
            # Extract dates
            dates = self.extract_polish_dates(text)
            if dates:
                # Try to identify invoice date and sale date
                extracted_data['data_wystawienia'] = dates[0]
                if len(dates) > 1:
                    extracted_data['data_sprzedazy'] = dates[1]
                else:
                    extracted_data['data_sprzedazy'] = dates[0]  # Same as issue date if only one
            
            # Extract VAT rates
            vat_rates = self.extract_vat_rates(text)
            if vat_rates:
                extracted_data['vat_rates'] = vat_rates
            
            # Extract currency amounts
            amounts = self.extract_currency_amounts(text)
            if amounts:
                # Try to identify different amount types
                extracted_data['amounts'] = amounts
                
                # Try to identify specific amounts by context
                for line in text.split('\n'):
                    line = line.strip()
                    if 'suma netto' in line.lower():
                        amount_match = re.search(r'(\d+[,\.]\d{2})', line)
                        if amount_match:
                            extracted_data['suma_netto'] = self.standardize_amount(amount_match.group(1))
                    elif 'suma brutto' in line.lower():
                        amount_match = re.search(r'(\d+[,\.]\d{2})', line)
                        if amount_match:
                            extracted_data['suma_brutto'] = self.standardize_amount(amount_match.group(1))
                    elif 'vat' in line.lower() and any(char.isdigit() for char in line):
                        amount_match = re.search(r'(\d+[,\.]\d{2})', line)
                        if amount_match:
                            extracted_data['suma_vat'] = self.standardize_amount(amount_match.group(1))
                
                # Fallback to positional logic if specific amounts not found
                if 'suma_brutto' not in extracted_data and amounts:
                    if len(amounts) >= 3:
                        # Assume last three are netto, VAT, brutto
                        extracted_data['suma_netto'] = amounts[-3]
                        extracted_data['suma_vat'] = amounts[-2]
                        extracted_data['suma_brutto'] = amounts[-1]
                    elif len(amounts) >= 1:
                        extracted_data['suma_brutto'] = amounts[-1]  # At least total amount
            
            # Extract invoice number
            invoice_number = self.extract_invoice_number(text)
            if invoice_number:
                extracted_data['numer_faktury'] = invoice_number
                
            self.logger.info(f"Extracted {len(extracted_data)} Polish invoice fields")
            
        except Exception as e:
            self.logger.error(f"Error extracting Polish invoice fields: {e}")
            
        return extracted_data
    
    def extract_nip_numbers(self, text: str) -> List[str]:
        """
        Extract NIP numbers from text with validation.
        
        Args:
            text: Input text to search
            
        Returns:
            List of valid NIP numbers found
        """
        if not text:
            return []
            
        nip_patterns = [
            r'NIP[:\s]*(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})',  # NIP: 123-456-78-90
            r'NIP[:\s]*(\d{10})',  # NIP: 1234567890
        ]
        
        found_nips = []
        
        for pattern in nip_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                nip_candidate = re.sub(r'[-\s]', '', match.group(1))
                if self.validate_nip(nip_candidate):
                    formatted_nip = self.format_nip(nip_candidate)
                    if formatted_nip not in found_nips:
                        found_nips.append(formatted_nip)
        
        return found_nips
    
    def validate_nip(self, nip: str) -> bool:
        """
        Validate Polish NIP number with checksum verification.
        
        Args:
            nip: NIP number to validate (digits only)
            
        Returns:
            True if NIP is valid, False otherwise
        """
        if not nip or not isinstance(nip, str):
            return False
            
        # Remove any non-digit characters
        nip_digits = re.sub(r'\D', '', nip)
        
        # NIP must be exactly 10 digits
        if len(nip_digits) != 10:
            return False
            
        # Convert to list of integers
        try:
            digits = [int(d) for d in nip_digits]
        except ValueError:
            return False
        
        # Reject obvious invalid patterns
        if all(d == digits[0] for d in digits):  # All same digits
            return False
            
        # NIP checksum algorithm
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(digit * weight for digit, weight in zip(digits[:9], weights)) % 11
        
        # If checksum is 10, it's invalid
        if checksum == 10:
            return False
            
        # Checksum must equal the 10th digit
        return checksum == digits[9]
    
    def format_nip(self, nip: str) -> str:
        """
        Format NIP number in standard Polish format: XXX-XXX-XX-XX
        
        Args:
            nip: NIP number (digits only)
            
        Returns:
            Formatted NIP number
        """
        if len(nip) == 10:
            return f"{nip[:3]}-{nip[3:6]}-{nip[6:8]}-{nip[8:10]}"
        return nip
    
    def extract_regon_numbers(self, text: str) -> List[str]:
        """
        Extract and validate REGON numbers from text.
        
        Args:
            text: Input text to search
            
        Returns:
            List of valid REGON numbers found
        """
        regon_patterns = [
            r'REGON[:\s]*(\d{9})',  # 9-digit REGON
            r'REGON[:\s]*(\d{14})',  # 14-digit REGON
            r'(?:^|\s)(\d{9})(?:\s|$)',  # Standalone 9 digits (context-dependent)
            r'(?:^|\s)(\d{14})(?:\s|$)',  # Standalone 14 digits (context-dependent)
        ]
        
        found_regons = []
        
        for pattern in regon_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                regon_candidate = match.group(1)
                if self.validate_regon(regon_candidate):
                    if regon_candidate not in found_regons:
                        found_regons.append(regon_candidate)
        
        return found_regons
    
    def validate_regon(self, regon: str) -> bool:
        """
        Validate Polish REGON number with checksum verification.
        
        Args:
            regon: REGON number to validate
            
        Returns:
            True if REGON is valid, False otherwise
        """
        if not regon or not isinstance(regon, str):
            return False
            
        # Remove any non-digit characters
        regon_digits = re.sub(r'\D', '', regon)
        
        # REGON can be 9 or 14 digits
        if len(regon_digits) not in [9, 14]:
            return False
            
        try:
            digits = [int(d) for d in regon_digits]
        except ValueError:
            return False
        
        if len(regon_digits) == 9:
            # 9-digit REGON checksum
            weights = [8, 9, 2, 3, 4, 5, 6, 7]
            checksum = sum(digit * weight for digit, weight in zip(digits[:8], weights)) % 11
            return checksum % 10 == digits[8]
        else:
            # 14-digit REGON checksum (first validate 9-digit part)
            if not self.validate_regon(regon_digits[:9]):
                return False
            weights = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
            checksum = sum(digit * weight for digit, weight in zip(digits[:13], weights)) % 11
            return checksum % 10 == digits[13]
    
    def extract_krs_numbers(self, text: str) -> List[str]:
        """
        Extract KRS (National Court Register) numbers from text.
        
        Args:
            text: Input text to search
            
        Returns:
            List of KRS numbers found
        """
        krs_patterns = [
            r'KRS[:\s]*(\d{10})',  # KRS: 1234567890
            r'(?:Sąd|Sadu|Rejestru)[^0-9]*(\d{10})',  # Court register context
        ]
        
        found_krs = []
        
        for pattern in krs_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                krs_candidate = match.group(1)
                if self.validate_krs(krs_candidate):
                    if krs_candidate not in found_krs:
                        found_krs.append(krs_candidate)
        
        return found_krs
    
    def validate_krs(self, krs: str) -> bool:
        """
        Validate KRS number format.
        
        Args:
            krs: KRS number to validate
            
        Returns:
            True if KRS format is valid, False otherwise
        """
        if not krs or not isinstance(krs, str):
            return False
            
        # Remove any non-digit characters
        krs_digits = re.sub(r'\D', '', krs)
        
        # KRS should be 10 digits
        return len(krs_digits) == 10 and krs_digits.isdigit()
    
    def extract_polish_dates(self, text: str) -> List[str]:
        """
        Extract and parse Polish date formats from text.
        
        Args:
            text: Input text to search
            
        Returns:
            List of dates in ISO format (YYYY-MM-DD)
        """
        found_dates = []
        
        for pattern in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = self.parse_polish_date(match)
                if date_str and date_str not in found_dates:
                    found_dates.append(date_str)
        
        return found_dates
    
    def parse_polish_date(self, match) -> Optional[str]:
        """
        Parse a Polish date match into ISO format.
        
        Args:
            match: Regex match object containing date components
            
        Returns:
            Date in ISO format (YYYY-MM-DD) or None if invalid
        """
        try:
            groups = match.groups()
            
            if len(groups) == 3:
                if groups[1] in self.POLISH_MONTHS:
                    # Format: DD month YYYY
                    day = int(groups[0])
                    month = self.POLISH_MONTHS[groups[1]]
                    year = int(groups[2])
                elif groups[0].isdigit() and len(groups[0]) == 4:
                    # Format: YYYY-MM-DD
                    year = int(groups[0])
                    month = int(groups[1])
                    day = int(groups[2])
                else:
                    # Format: DD-MM-YYYY
                    day = int(groups[0])
                    month = int(groups[1])
                    year = int(groups[2])
                
                # Validate date
                if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100:
                    try:
                        datetime(year, month, day)  # Validate actual date
                        return f"{year:04d}-{month:02d}-{day:02d}"
                    except ValueError:
                        pass
                        
        except (ValueError, IndexError):
            pass
            
        return None
    
    def extract_vat_rates(self, text: str) -> List[int]:
        """
        Extract Polish VAT rates from text.
        
        Args:
            text: Input text to search
            
        Returns:
            List of valid Polish VAT rates found
        """
        vat_patterns = [
            r'(\d{1,2})%\s*VAT',  # XX% VAT
            r'VAT\s*(\d{1,2})%',  # VAT XX%
            r'(\d{1,2})\s*%',  # XX% (context-dependent)
        ]
        
        found_rates = []
        
        for pattern in vat_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    rate = int(match.group(1))
                    if rate in self.POLISH_VAT_RATES and rate not in found_rates:
                        found_rates.append(rate)
                except ValueError:
                    continue
        
        return sorted(found_rates)
    
    def extract_currency_amounts(self, text: str) -> List[str]:
        """
        Extract currency amounts from text, handling Polish decimal separators.
        
        Args:
            text: Input text to search
            
        Returns:
            List of currency amounts in standardized format
        """
        found_amounts = []
        
        for pattern in self.CURRENCY_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1)
                standardized_amount = self.standardize_amount(amount_str)
                if standardized_amount and standardized_amount not in found_amounts:
                    found_amounts.append(standardized_amount)
        
        return found_amounts
    
    def standardize_amount(self, amount_str: str) -> Optional[str]:
        """
        Standardize Polish currency amount format.
        
        Args:
            amount_str: Raw amount string
            
        Returns:
            Standardized amount string or None if invalid
        """
        if not amount_str:
            return None
            
        # Replace Polish decimal comma with dot
        normalized = amount_str.replace(',', '.')
        
        try:
            # Validate as decimal
            amount = Decimal(normalized)
            if amount >= 0:
                return f"{amount:.2f}"
        except InvalidOperation:
            pass
            
        return None
    
    def extract_invoice_number(self, text: str) -> Optional[str]:
        """
        Extract Polish invoice number from text.
        
        Args:
            text: Input text to search
            
        Returns:
            Invoice number or None if not found
        """
        invoice_patterns = [
            r'(?:Faktura|FV|F)\s*(?:nr\.?|numer|#)\s*([A-Z0-9/\-\.]+)',  # Faktura nr. XXX
            r'(?:Faktura|FV|F)[:\s]+([A-Z0-9/\-\.]+)',  # Faktura: XXX
            r'Nr\s*faktury[:\s]+([A-Z0-9/\-\.]+)',  # Nr faktury: XXX
            r'Nr[:\s]+([A-Z0-9/\-\.]+)',  # Nr: XXX (more specific)
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # Filter out obvious non-invoice numbers
                if len(candidate) >= 3 and not candidate.upper() in ['VAT', 'NIP', 'KRS', 'FAKTURY']:
                    return candidate
        
        return None
    
    def validate_polish_patterns(self, extracted_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate Polish-specific patterns in extracted data.
        
        Args:
            extracted_data: Dictionary of extracted invoice data
            
        Returns:
            Dictionary of validation results for each field
        """
        validation_results = {}
        
        # Validate NIP numbers
        for field in ['sprzedawca_nip', 'nabywca_nip']:
            if field in extracted_data:
                nip = re.sub(r'\D', '', str(extracted_data[field]))
                validation_results[f'{field}_valid'] = self.validate_nip(nip)
        
        # Validate REGON
        if 'regon' in extracted_data:
            validation_results['regon_valid'] = self.validate_regon(str(extracted_data['regon']))
        
        # Validate KRS
        if 'krs' in extracted_data:
            validation_results['krs_valid'] = self.validate_krs(str(extracted_data['krs']))
        
        # Validate VAT rates
        if 'vat_rates' in extracted_data:
            rates = extracted_data['vat_rates']
            if isinstance(rates, list):
                validation_results['vat_rates_valid'] = all(rate in self.POLISH_VAT_RATES for rate in rates)
            else:
                validation_results['vat_rates_valid'] = False
        
        # Validate dates
        for field in ['data_wystawienia', 'data_sprzedazy']:
            if field in extracted_data:
                date_str = str(extracted_data[field])
                validation_results[f'{field}_valid'] = self.validate_date_format(date_str)
        
        # Validate amounts
        for field in ['suma_netto', 'suma_vat', 'suma_brutto']:
            if field in extracted_data:
                amount_str = str(extracted_data[field])
                validation_results[f'{field}_valid'] = self.validate_amount_format(amount_str)
        
        return validation_results
    
    def validate_date_format(self, date_str: str) -> bool:
        """
        Validate date format (ISO format expected).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid date format, False otherwise
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def validate_amount_format(self, amount_str: str) -> bool:
        """
        Validate currency amount format.
        
        Args:
            amount_str: Amount string to validate
            
        Returns:
            True if valid amount format, False otherwise
        """
        try:
            amount = Decimal(amount_str)
            return amount >= 0
        except (InvalidOperation, ValueError):
            return False
    
    def calculate_field_confidence(self, field_value: str, field_type: str, context: Dict = None) -> float:
        """
        Calculate confidence score for a specific field type based on Polish patterns.
        
        Args:
            field_value: The extracted field value
            field_type: Type of field (nip, regon, date, amount, etc.)
            context: Additional context information
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not field_value:
            return 0.0
            
        context = context or {}
        base_confidence = 0.5  # Base confidence for any extracted value
        
        try:
            if field_type == 'nip':
                nip_digits = re.sub(r'\D', '', field_value)
                if len(nip_digits) == 10:
                    base_confidence = 0.7
                    if self.validate_nip(nip_digits):
                        return 0.95  # High confidence for valid NIP
                    else:
                        return 0.3   # Low confidence for invalid NIP
                        
            elif field_type == 'regon':
                if self.validate_regon(field_value):
                    return 0.9
                else:
                    return 0.3
                    
            elif field_type == 'krs':
                if self.validate_krs(field_value):
                    return 0.85
                else:
                    return 0.3
                    
            elif field_type == 'date':
                if self.validate_date_format(field_value):
                    return 0.9
                else:
                    return 0.2
                    
            elif field_type == 'amount':
                if self.validate_amount_format(field_value):
                    return 0.8
                else:
                    return 0.2
                    
            elif field_type == 'vat_rate':
                try:
                    rate = int(field_value.replace('%', ''))
                    if rate in self.POLISH_VAT_RATES:
                        return 0.9
                    else:
                        return 0.3
                except ValueError:
                    return 0.2
                    
            elif field_type == 'invoice_number':
                # Invoice numbers typically have specific patterns
                if re.match(r'^[A-Z0-9/\-\.]+$', field_value):
                    return 0.8
                else:
                    return 0.5
                    
        except Exception as e:
            self.logger.error(f"Error calculating confidence for {field_type}: {e}")
            
        return base_confidence