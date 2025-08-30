"""
Validation Service for FaktuLove

Provides real-time form validation with Polish business rules,
field-specific error highlighting, and correction guidance.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

class ValidationService:
    """
    Comprehensive validation service with Polish business rules
    
    Features:
    - Real-time field validation
    - Polish business number validation (NIP, REGON, KRS)
    - VAT rate validation
    - Date range validation
    - Amount and currency validation
    - Email and phone validation
    - Custom business rule validation
    """
    
    # Polish VAT rates (as of 2025)
    VALID_VAT_RATES = [0, 5, 8, 23]
    
    # Polish postal code pattern
    POSTAL_CODE_PATTERN = r'^\d{2}-\d{3}$'
    
    # Polish phone number patterns
    PHONE_PATTERNS = [
        r'^\+48\s?\d{3}\s?\d{3}\s?\d{3}$',  # +48 123 456 789
        r'^\d{3}\s?\d{3}\s?\d{3}$',         # 123 456 789
        r'^\d{9}$'                          # 123456789
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
    
    def validate_field(self, field_name: str, value: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Validate a single field with appropriate business rules
        
        Args:
            field_name: Name of the field to validate
            value: Value to validate
            context: Additional context for validation
            
        Returns:
            Dict containing validation result
        """
        try:
            # Route to appropriate validator based on field name
            if field_name == 'nip':
                return self.validate_nip(value)
            elif field_name == 'regon':
                return self.validate_regon(value)
            elif field_name == 'krs':
                return self.validate_krs(value)
            elif field_name == 'email':
                return self.validate_email_field(value)
            elif field_name == 'phone':
                return self.validate_phone(value)
            elif field_name == 'postal_code':
                return self.validate_postal_code(value)
            elif field_name in ['vat_rate', 'stawka_vat']:
                return self.validate_vat_rate(value)
            elif field_name in ['amount', 'kwota', 'cena', 'wartosc']:
                return self.validate_amount(value)
            elif field_name in ['date', 'data']:
                return self.validate_date(value)
            elif field_name in ['invoice_number', 'numer_faktury']:
                return self.validate_invoice_number(value, context)
            else:
                return self.validate_generic_field(field_name, value)
                
        except Exception as e:
            self.logger.error(f"Validation error for field {field_name}: {e}")
            return {
                'valid': False,
                'error': 'Błąd walidacji pola',
                'suggestions': ['Sprawdź format danych', 'Skontaktuj się z pomocą techniczną']
            }
    
    def validate_nip(self, nip: str) -> Dict[str, Any]:
        """
        Validate Polish NIP (Tax Identification Number)
        
        Args:
            nip: NIP number to validate
            
        Returns:
            Dict containing validation result
        """
        if not nip:
            return {
                'valid': False,
                'error': 'NIP jest wymagany',
                'suggestions': ['Wprowadź 10-cyfrowy numer NIP']
            }
        
        # Clean the NIP (remove spaces, hyphens)
        clean_nip = re.sub(r'[\s\-]', '', str(nip))
        
        # Check length
        if len(clean_nip) != 10:
            return {
                'valid': False,
                'error': 'NIP musi mieć dokładnie 10 cyfr',
                'suggestions': [
                    'Sprawdź czy NIP ma 10 cyfr',
                    'Usuń spacje i myślniki',
                    'Przykład poprawnego NIP: 1234567890'
                ]
            }
        
        # Check if all characters are digits
        if not clean_nip.isdigit():
            return {
                'valid': False,
                'error': 'NIP może zawierać tylko cyfry',
                'suggestions': [
                    'Usuń wszystkie litery i znaki specjalne',
                    'NIP składa się tylko z cyfr'
                ]
            }
        
        # Validate checksum
        if not self._validate_nip_checksum(clean_nip):
            return {
                'valid': False,
                'error': 'Nieprawidłowa suma kontrolna NIP',
                'suggestions': [
                    'Sprawdź czy wszystkie cyfry zostały wprowadzone poprawnie',
                    'Zweryfikuj NIP w bazie REGON',
                    'Skontaktuj się z kontrahentem w celu potwierdzenia'
                ]
            }
        
        return {
            'valid': True,
            'message': 'NIP jest prawidłowy',
            'formatted_value': self._format_nip(clean_nip)
        }
    
    def validate_regon(self, regon: str) -> Dict[str, Any]:
        """
        Validate Polish REGON number
        
        Args:
            regon: REGON number to validate
            
        Returns:
            Dict containing validation result
        """
        if not regon:
            return {
                'valid': False,
                'error': 'REGON jest wymagany',
                'suggestions': ['Wprowadź 9 lub 14-cyfrowy numer REGON']
            }
        
        # Clean the REGON
        clean_regon = re.sub(r'[\s\-]', '', str(regon))
        
        # Check length (9 or 14 digits)
        if len(clean_regon) not in [9, 14]:
            return {
                'valid': False,
                'error': 'REGON musi mieć 9 lub 14 cyfr',
                'suggestions': [
                    'REGON 9-cyfrowy dla osób fizycznych',
                    'REGON 14-cyfrowy dla jednostek lokalnych',
                    'Usuń spacje i myślniki'
                ]
            }
        
        # Check if all characters are digits
        if not clean_regon.isdigit():
            return {
                'valid': False,
                'error': 'REGON może zawierać tylko cyfry',
                'suggestions': ['Usuń wszystkie litery i znaki specjalne']
            }
        
        # Validate checksum
        if not self._validate_regon_checksum(clean_regon):
            return {
                'valid': False,
                'error': 'Nieprawidłowa suma kontrolna REGON',
                'suggestions': [
                    'Sprawdź czy wszystkie cyfry zostały wprowadzone poprawnie',
                    'Zweryfikuj REGON w bazie GUS'
                ]
            }
        
        return {
            'valid': True,
            'message': 'REGON jest prawidłowy',
            'formatted_value': clean_regon
        }
    
    def validate_krs(self, krs: str) -> Dict[str, Any]:
        """
        Validate Polish KRS (National Court Register) number
        
        Args:
            krs: KRS number to validate
            
        Returns:
            Dict containing validation result
        """
        if not krs:
            return {
                'valid': True,  # KRS is optional
                'message': 'KRS jest opcjonalny'
            }
        
        # Clean the KRS
        clean_krs = re.sub(r'[\s\-]', '', str(krs))
        
        # Check length (10 digits)
        if len(clean_krs) != 10:
            return {
                'valid': False,
                'error': 'KRS musi mieć dokładnie 10 cyfr',
                'suggestions': [
                    'Sprawdź czy KRS ma 10 cyfr',
                    'Usuń spacje i myślniki',
                    'Przykład: 0000123456'
                ]
            }
        
        # Check if all characters are digits
        if not clean_krs.isdigit():
            return {
                'valid': False,
                'error': 'KRS może zawierać tylko cyfry',
                'suggestions': ['Usuń wszystkie litery i znaki specjalne']
            }
        
        return {
            'valid': True,
            'message': 'KRS jest prawidłowy',
            'formatted_value': clean_krs
        }
    
    def validate_email_field(self, email: str) -> Dict[str, Any]:
        """
        Validate email address
        
        Args:
            email: Email address to validate
            
        Returns:
            Dict containing validation result
        """
        if not email:
            return {
                'valid': False,
                'error': 'Adres email jest wymagany',
                'suggestions': ['Wprowadź prawidłowy adres email']
            }
        
        try:
            validate_email(email)
            return {
                'valid': True,
                'message': 'Adres email jest prawidłowy'
            }
        except ValidationError:
            return {
                'valid': False,
                'error': 'Nieprawidłowy format adresu email',
                'suggestions': [
                    'Sprawdź czy adres zawiera znak @',
                    'Przykład: nazwa@domena.pl',
                    'Usuń spacje na początku i końcu'
                ]
            }
    
    def validate_phone(self, phone: str) -> Dict[str, Any]:
        """
        Validate Polish phone number
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Dict containing validation result
        """
        if not phone:
            return {
                'valid': True,  # Phone is usually optional
                'message': 'Numer telefonu jest opcjonalny'
            }
        
        # Check against Polish phone patterns
        for pattern in self.PHONE_PATTERNS:
            if re.match(pattern, phone.strip()):
                return {
                    'valid': True,
                    'message': 'Numer telefonu jest prawidłowy',
                    'formatted_value': self._format_phone(phone)
                }
        
        return {
            'valid': False,
            'error': 'Nieprawidłowy format numeru telefonu',
            'suggestions': [
                'Użyj formatu: +48 123 456 789',
                'Lub: 123 456 789',
                'Lub: 123456789'
            ]
        }
    
    def validate_postal_code(self, postal_code: str) -> Dict[str, Any]:
        """
        Validate Polish postal code
        
        Args:
            postal_code: Postal code to validate
            
        Returns:
            Dict containing validation result
        """
        if not postal_code:
            return {
                'valid': False,
                'error': 'Kod pocztowy jest wymagany',
                'suggestions': ['Wprowadź kod pocztowy w formacie XX-XXX']
            }
        
        if re.match(self.POSTAL_CODE_PATTERN, postal_code.strip()):
            return {
                'valid': True,
                'message': 'Kod pocztowy jest prawidłowy'
            }
        
        return {
            'valid': False,
            'error': 'Nieprawidłowy format kodu pocztowego',
            'suggestions': [
                'Użyj formatu: XX-XXX',
                'Przykład: 00-001',
                'Sprawdź czy kod ma 5 cyfr i myślnik'
            ]
        }
    
    def validate_vat_rate(self, vat_rate: Any) -> Dict[str, Any]:
        """
        Validate VAT rate
        
        Args:
            vat_rate: VAT rate to validate
            
        Returns:
            Dict containing validation result
        """
        if vat_rate is None or vat_rate == '':
            return {
                'valid': False,
                'error': 'Stawka VAT jest wymagana',
                'suggestions': [f'Dozwolone stawki: {", ".join(map(str, self.VALID_VAT_RATES))}%']
            }
        
        try:
            rate = float(vat_rate)
            if rate in self.VALID_VAT_RATES:
                return {
                    'valid': True,
                    'message': f'Stawka VAT {rate}% jest prawidłowa'
                }
            else:
                return {
                    'valid': False,
                    'error': f'Nieprawidłowa stawka VAT: {rate}%',
                    'suggestions': [
                        f'Dozwolone stawki VAT w Polsce: {", ".join(map(str, self.VALID_VAT_RATES))}%',
                        'Sprawdź aktualną tabelę stawek VAT'
                    ]
                }
        except (ValueError, TypeError):
            return {
                'valid': False,
                'error': 'Stawka VAT musi być liczbą',
                'suggestions': [
                    'Wprowadź liczbę (np. 23)',
                    f'Dozwolone stawki: {", ".join(map(str, self.VALID_VAT_RATES))}%'
                ]
            }
    
    def validate_amount(self, amount: Any) -> Dict[str, Any]:
        """
        Validate monetary amount
        
        Args:
            amount: Amount to validate
            
        Returns:
            Dict containing validation result
        """
        if amount is None or amount == '':
            return {
                'valid': False,
                'error': 'Kwota jest wymagana',
                'suggestions': ['Wprowadź kwotę w formacie: 123.45']
            }
        
        try:
            decimal_amount = Decimal(str(amount))
            
            if decimal_amount < 0:
                return {
                    'valid': False,
                    'error': 'Kwota nie może być ujemna',
                    'suggestions': ['Wprowadź kwotę większą lub równą 0']
                }
            
            if decimal_amount > Decimal('999999999.99'):
                return {
                    'valid': False,
                    'error': 'Kwota jest zbyt duża',
                    'suggestions': ['Maksymalna kwota: 999,999,999.99']
                }
            
            # Check decimal places
            if decimal_amount.as_tuple().exponent < -2:
                return {
                    'valid': False,
                    'error': 'Kwota może mieć maksymalnie 2 miejsca po przecinku',
                    'suggestions': [
                        'Użyj formatu: 123.45',
                        'Zaokrąglij do groszy'
                    ]
                }
            
            return {
                'valid': True,
                'message': 'Kwota jest prawidłowa',
                'formatted_value': f"{decimal_amount:.2f}"
            }
            
        except (InvalidOperation, ValueError, TypeError):
            return {
                'valid': False,
                'error': 'Nieprawidłowy format kwoty',
                'suggestions': [
                    'Użyj kropki jako separatora dziesiętnego',
                    'Przykład: 123.45',
                    'Nie używaj spacji ani innych znaków'
                ]
            }
    
    def validate_date(self, date_value: Any) -> Dict[str, Any]:
        """
        Validate date
        
        Args:
            date_value: Date to validate
            
        Returns:
            Dict containing validation result
        """
        if not date_value:
            return {
                'valid': False,
                'error': 'Data jest wymagana',
                'suggestions': ['Wprowadź datę w formacie DD.MM.RRRR']
            }
        
        # Handle different date formats
        if isinstance(date_value, date):
            return {
                'valid': True,
                'message': 'Data jest prawidłowa'
            }
        
        # Try to parse string date
        date_formats = ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']
        
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_value), date_format).date()
                
                # Check if date is reasonable (not too far in past or future)
                today = date.today()
                if parsed_date.year < 1900 or parsed_date.year > today.year + 10:
                    return {
                        'valid': False,
                        'error': 'Data jest poza dozwolonym zakresem',
                        'suggestions': [
                            'Sprawdź czy rok jest prawidłowy',
                            f'Dozwolony zakres: 1900 - {today.year + 10}'
                        ]
                    }
                
                return {
                    'valid': True,
                    'message': 'Data jest prawidłowa',
                    'formatted_value': parsed_date.strftime('%d.%m.%Y')
                }
                
            except ValueError:
                continue
        
        return {
            'valid': False,
            'error': 'Nieprawidłowy format daty',
            'suggestions': [
                'Użyj formatu: DD.MM.RRRR',
                'Przykład: 31.12.2025',
                'Lub: RRRR-MM-DD (2025-12-31)'
            ]
        }
    
    def validate_invoice_number(self, invoice_number: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Validate invoice number
        
        Args:
            invoice_number: Invoice number to validate
            context: Additional context (e.g., company, year)
            
        Returns:
            Dict containing validation result
        """
        if not invoice_number:
            return {
                'valid': False,
                'error': 'Numer faktury jest wymagany',
                'suggestions': ['Wprowadź unikalny numer faktury']
            }
        
        # Basic format validation
        if len(invoice_number.strip()) < 1:
            return {
                'valid': False,
                'error': 'Numer faktury nie może być pusty',
                'suggestions': ['Wprowadź numer faktury']
            }
        
        # Check for uniqueness if context provided
        if context and context.get('check_uniqueness'):
            from faktury.models import Faktura
            
            existing = Faktura.objects.filter(
                numer=invoice_number.strip(),
                firma_id=context.get('firma_id')
            ).exists()
            
            if existing:
                return {
                    'valid': False,
                    'error': 'Numer faktury już istnieje',
                    'suggestions': [
                        'Użyj innego numeru faktury',
                        'Sprawdź czy faktura nie została już utworzona',
                        'Dodaj sufiks lub prefiks do numeru'
                    ]
                }
        
        return {
            'valid': True,
            'message': 'Numer faktury jest prawidłowy'
        }
    
    def validate_generic_field(self, field_name: str, value: Any) -> Dict[str, Any]:
        """
        Generic field validation
        
        Args:
            field_name: Name of the field
            value: Value to validate
            
        Returns:
            Dict containing validation result
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return {
                'valid': False,
                'error': f'Pole {field_name} jest wymagane',
                'suggestions': [f'Wprowadź wartość dla pola {field_name}']
            }
        
        return {
            'valid': True,
            'message': 'Pole jest prawidłowe'
        }
    
    def _validate_nip_checksum(self, nip: str) -> bool:
        """Validate NIP checksum using Polish algorithm"""
        if len(nip) != 10:
            return False
        
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        
        return checksum == int(nip[9])
    
    def _validate_regon_checksum(self, regon: str) -> bool:
        """Validate REGON checksum"""
        if len(regon) == 9:
            weights = [8, 9, 2, 3, 4, 5, 6, 7]
            checksum = sum(int(regon[i]) * weights[i] for i in range(8)) % 11
            return checksum % 10 == int(regon[8])
        elif len(regon) == 14:
            weights = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
            checksum = sum(int(regon[i]) * weights[i] for i in range(13)) % 11
            return checksum % 10 == int(regon[13])
        
        return False
    
    def _format_nip(self, nip: str) -> str:
        """Format NIP for display"""
        return f"{nip[:3]}-{nip[3:6]}-{nip[6:8]}-{nip[8:]}"
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number for display"""
        clean_phone = re.sub(r'[\s\-]', '', phone)
        if clean_phone.startswith('+48'):
            clean_phone = clean_phone[3:]
        
        if len(clean_phone) == 9:
            return f"+48 {clean_phone[:3]} {clean_phone[3:6]} {clean_phone[6:]}"
        
        return phone


# Global validation service instance
validation_service = ValidationService()