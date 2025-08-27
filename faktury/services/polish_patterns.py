#!/usr/bin/env python3
"""
Polish Patterns for Invoice Processing
Contains regex patterns and validation logic for Polish business documents
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PolishPatterns:
    """
    Polish-specific patterns for invoice field extraction
    Provides regex patterns and validation for Polish business documents
    """
    
    def __init__(self):
        """Initialize Polish patterns with comprehensive regex expressions"""
        
        # NIP patterns (Polish Tax Identification Number)
        self.nip_patterns = [
            r'\b\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3}\b',
            r'NIP\s*[:]?\s*(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3})',
            r'(\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}[\-\s]?\d{3})'
        ]
        
        # REGON patterns (Business Registry Number)
        self.regon_patterns = [
            r'\b\d{9}\b',  # 9-digit REGON
            r'\b\d{14}\b',  # 14-digit REGON
            r'REGON\s*[:]?\s*(\d{9}|\d{14})',
            r'(\d{9}|\d{14})'
        ]
        
        # KRS patterns (National Court Register)
        self.krs_patterns = [
            r'\bKRS\s*[:]?\s*(\d{10})\b',
            r'(\d{10})'
        ]
        
        # Polish date patterns
        self.date_patterns = [
            r'\b\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4}\b',
            r'\b\d{4}[\.\-]\d{1,2}[\.\-]\d{1,2}\b',
            r'data\s*[:]?\s*(\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})',
            r'wystawiono\s*[:]?\s*(\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})'
        ]
        
        # Invoice number patterns
        self.invoice_patterns = [
            r'faktur[ay]?\s*[nr]?[o]?[r]?[.]?\s*[:]?\s*([a-zA-Z0-9\/\-_]+)',
            r'invoice\s*[nr]?[o]?[r]?[.]?\s*[:]?\s*([a-zA-Z0-9\/\-_]+)',
            r'FV[/\-]?(\d+[/\-]\d+)',
            r'(\d{2,4}[/\-]\d{2,4}[/\-]\d{2,4})',
            r'Nr\s*faktury\s*[:]?\s*([a-zA-Z0-9\/\-_]+)'
        ]
        
        # Currency amount patterns (Polish format with comma as decimal separator)
        self.currency_patterns = [
            r'([\d\s,]+)\s*[zł|PLN]',
            r'([\d\s,]+)\s*[złoty|złotych]',
            r'([\d\s,]+)\s*[EUR|€]',
            r'([\d\s,]+)\s*[USD|\$]',
            r'([\d\s,]+)\s*[GBP|£]'
        ]
        
        # VAT rate patterns
        self.vat_patterns = [
            r'(\d{1,2}[,\.]\d{1,2})\s*%?\s*VAT',
            r'VAT\s*(\d{1,2}[,\.]\d{1,2})\s*%?',
            r'(\d{1,2}[,\.]\d{1,2})\s*%?\s*podatku',
            r'podatek\s*(\d{1,2}[,\.]\d{1,2})\s*%?'
        ]
        
        # Company name patterns
        self.company_patterns = [
            r'(Sp\.\s*z\s*o\.\s*o\.)',
            r'(S\.\s*A\.)',
            r'(Spółka\s+Akcyjna)',
            r'(Spółka\s+z\s+ograniczoną\s+odpowiedzialnością)',
            r'(Spółka\s+Jawna)',
            r'(Spółka\s+Komandytowa)',
            r'(Spółka\s+Komandytowo-Akcyjna)',
            r'(Przedsiębiorstwo\s+Państwowe)',
            r'(Zakład\s+Pracy\s+Chronionej)'
        ]
        
        # Payment method patterns
        self.payment_patterns = [
            r'(przelew\s+bankowy)',
            r'(gotówka)',
            r'(karta\s+płatnicza)',
            r'(czek)',
            r'(weksel)',
            r'(kredyt\s+kupiecki)',
            r'(leasing)',
            r'(faktoring)'
        ]
        
        # Payment terms patterns
        self.terms_patterns = [
            r'(\d+)\s*dni',
            r'(\d+)\s*dni\s*od\s*wystawienia',
            r'(\d+)\s*dni\s*od\s*dostawy',
            r'(\d+)\s*dni\s*od\s*odbioru',
            r'(\d+)\s*dni\s*od\s*daty\s*faktury',
            r'(\d+)\s*dni\s*od\s*daty\s*wystawienia'
        ]
        
        # Bank account patterns
        self.bank_account_patterns = [
            r'(\d{2}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4})',
            r'(\d{2}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4})',
            r'IBAN\s*[:]?\s*([A-Z]{2}\d{2}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4})',
            r'konto\s*[:]?\s*(\d{2}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4})'
        ]
        
        # Email patterns
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'email\s*[:]?\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'e-mail\s*[:]?\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
        ]
        
        # Phone patterns
        self.phone_patterns = [
            r'(\+\d{2}\s+\d{3}\s+\d{3}\s+\d{3})',
            r'(\d{3}\s+\d{3}\s+\d{3})',
            r'(\d{3}[\-\s]\d{3}[\-\s]\d{3})',
            r'telefon\s*[:]?\s*(\+\d{2}\s+\d{3}\s+\d{3}\s+\d{3})',
            r'tel\.\s*[:]?\s*(\+\d{2}\s+\d{3}\s+\d{3}\s+\d{3})'
        ]
        
        # Address patterns
        self.address_patterns = [
            r'(ul\.\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)',
            r'(al\.\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)',
            r'(os\.\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)',
            r'(\d{2}-\d{3}\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)',
            r'(\d{2}\s+\d{3}\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)'
        ]
    
    def extract_nip_numbers(self, text: str) -> List[str]:
        """Extract NIP numbers from text"""
        nip_numbers = []
        
        for pattern in self.nip_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the NIP number
                nip_clean = re.sub(r'[^\d]', '', match)
                if len(nip_clean) == 10:
                    nip_numbers.append(nip_clean)
        
        return list(set(nip_numbers))  # Remove duplicates
    
    def extract_regon_numbers(self, text: str) -> List[str]:
        """Extract REGON numbers from text"""
        regon_numbers = []
        
        for pattern in self.regon_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                regon_clean = re.sub(r'[^\d]', '', match)
                if len(regon_clean) in [9, 14]:
                    regon_numbers.append(regon_clean)
        
        return list(set(regon_numbers))
    
    def extract_krs_numbers(self, text: str) -> List[str]:
        """Extract KRS numbers from text"""
        krs_numbers = []
        
        for pattern in self.krs_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                krs_clean = re.sub(r'[^\d]', '', match)
                if len(krs_clean) == 10:
                    krs_numbers.append(krs_clean)
        
        return list(set(krs_numbers))
    
    def extract_vat_rates(self, text: str) -> List[str]:
        """Extract VAT rates from text"""
        vat_rates = []
        
        for pattern in self.vat_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Standardize VAT rate format
                vat_rate = match.replace(',', '.')
                try:
                    rate = float(vat_rate)
                    if 0 <= rate <= 100:
                        vat_rates.append(vat_rate)
                except ValueError:
                    continue
        
        return list(set(vat_rates))
    
    def extract_polish_dates(self, text: str) -> List[str]:
        """Extract Polish date formats from text"""
        dates = []
        
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Try to parse and validate the date
                try:
                    # Handle different date formats
                    if '.' in match:
                        # DD.MM.YYYY or YYYY.MM.DD
                        parts = match.split('.')
                        if len(parts) == 3:
                            if len(parts[0]) == 4:  # YYYY.MM.DD
                                date_obj = datetime.strptime(match, '%Y.%m.%d')
                            else:  # DD.MM.YYYY
                                date_obj = datetime.strptime(match, '%d.%m.%Y')
                        else:
                            continue
                    elif '-' in match:
                        # DD-MM-YYYY or YYYY-MM-DD
                        parts = match.split('-')
                        if len(parts) == 3:
                            if len(parts[0]) == 4:  # YYYY-MM-DD
                                date_obj = datetime.strptime(match, '%Y-%m-%d')
                            else:  # DD-MM-YYYY
                                date_obj = datetime.strptime(match, '%d-%m-%Y')
                        else:
                            continue
                    else:
                        continue
                    
                    # Validate reasonable date range (1900-2100)
                    if 1900 <= date_obj.year <= 2100:
                        dates.append(match)
                        
                except ValueError:
                    continue
        
        return list(set(dates))
    
    def extract_currency_amounts(self, text: str) -> List[str]:
        """Extract currency amounts from text"""
        amounts = []
        
        for pattern in self.currency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up amount
                amount_clean = re.sub(r'[^\d,\s]', '', match).strip()
                if amount_clean:
                    amounts.append(amount_clean)
        
        return list(set(amounts))
    
    def extract_invoice_numbers(self, text: str) -> List[str]:
        """Extract invoice numbers from text"""
        invoice_numbers = []
        
        for pattern in self.invoice_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and len(match.strip()) > 0:
                    invoice_numbers.append(match.strip())
        
        return list(set(invoice_numbers))
    
    def extract_company_names(self, text: str) -> List[str]:
        """Extract company names and types from text"""
        company_names = []
        
        for pattern in self.company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and len(match.strip()) > 0:
                    company_names.append(match.strip())
        
        return list(set(company_names))
    
    def extract_payment_methods(self, text: str) -> List[str]:
        """Extract payment methods from text"""
        payment_methods = []
        
        for pattern in self.payment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and len(match.strip()) > 0:
                    payment_methods.append(match.strip())
        
        return list(set(payment_methods))
    
    def extract_payment_terms(self, text: str) -> List[str]:
        """Extract payment terms from text"""
        payment_terms = []
        
        for pattern in self.terms_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    days = int(match)
                    if 0 <= days <= 365:  # Reasonable range
                        payment_terms.append(f"{days} dni")
                except ValueError:
                    continue
        
        return list(set(payment_terms))
    
    def extract_bank_accounts(self, text: str) -> List[str]:
        """Extract bank account numbers from text"""
        bank_accounts = []
        
        for pattern in self.bank_account_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                account_clean = re.sub(r'[^\d]', '', match)
                if len(account_clean) == 26:  # Polish IBAN length
                    bank_accounts.append(match.strip())
        
        return list(set(bank_accounts))
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        emails = []
        
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and '@' in match:
                    emails.append(match.strip())
        
        return list(set(emails))
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phones = []
        
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and len(re.sub(r'[^\d]', '', match)) >= 9:
                    phones.append(match.strip())
        
        return list(set(phones))
    
    def extract_addresses(self, text: str) -> List[str]:
        """Extract addresses from text"""
        addresses = []
        
        for pattern in self.address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and len(match.strip()) > 5:
                    addresses.append(match.strip())
        
        return list(set(addresses))
    
    def validate_nip(self, nip: str) -> bool:
        """
        Validate Polish NIP with checksum algorithm
        
        Args:
            nip: NIP number to validate
            
        Returns:
            True if NIP is valid, False otherwise
        """
        try:
            # Remove non-digit characters
            nip_clean = re.sub(r'[^\d]', '', nip)
            
            # Check length
            if len(nip_clean) != 10:
                return False
            
            # Polish NIP checksum algorithm
            weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
            checksum = 0
            
            for i in range(9):
                checksum += int(nip_clean[i]) * weights[i]
            
            checksum = checksum % 11
            if checksum == 10:
                checksum = 0
            
            return checksum == int(nip_clean[9])
            
        except Exception as e:
            logger.error(f"NIP validation failed: {e}")
            return False
    
    def validate_regon(self, regon: str) -> bool:
        """
        Validate Polish REGON with checksum algorithm
        
        Args:
            regon: REGON number to validate
            
        Returns:
            True if REGON is valid, False otherwise
        """
        try:
            # Remove non-digit characters
            regon_clean = re.sub(r'[^\d]', '', regon)
            
            # Check length
            if len(regon_clean) not in [9, 14]:
                return False
            
            # REGON checksum algorithm
            if len(regon_clean) == 9:
                weights = [8, 9, 2, 3, 4, 5, 6, 7]
                checksum = 0
                
                for i in range(8):
                    checksum += int(regon_clean[i]) * weights[i]
                
                checksum = checksum % 11
                if checksum == 10:
                    checksum = 0
                
                return checksum == int(regon_clean[8])
            
            elif len(regon_clean) == 14:
                weights = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
                checksum = 0
                
                for i in range(13):
                    checksum += int(regon_clean[i]) * weights[i]
                
                checksum = checksum % 11
                if checksum == 10:
                    checksum = 0
                
                return checksum == int(regon_clean[13])
            
            return False
            
        except Exception as e:
            logger.error(f"REGON validation failed: {e}")
            return False
    
    def validate_krs(self, krs: str) -> bool:
        """
        Validate Polish KRS number
        
        Args:
            krs: KRS number to validate
            
        Returns:
            True if KRS is valid, False otherwise
        """
        try:
            # Remove non-digit characters
            krs_clean = re.sub(r'[^\d]', '', krs)
            
            # Check length
            if len(krs_clean) != 10:
                return False
            
            # KRS validation (simplified - just check format)
            return True
            
        except Exception as e:
            logger.error(f"KRS validation failed: {e}")
            return False
    
    def get_all_patterns(self) -> Dict[str, List[str]]:
        """Get all patterns for testing and validation"""
        return {
            'nip_patterns': self.nip_patterns,
            'regon_patterns': self.regon_patterns,
            'krs_patterns': self.krs_patterns,
            'date_patterns': self.date_patterns,
            'invoice_patterns': self.invoice_patterns,
            'currency_patterns': self.currency_patterns,
            'vat_patterns': self.vat_patterns,
            'company_patterns': self.company_patterns,
            'payment_patterns': self.payment_patterns,
            'terms_patterns': self.terms_patterns,
            'bank_account_patterns': self.bank_account_patterns,
            'email_patterns': self.email_patterns,
            'phone_patterns': self.phone_patterns,
            'address_patterns': self.address_patterns
        }
    
    def extract_all_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract all patterns from text"""
        return {
            'nip_numbers': self.extract_nip_numbers(text),
            'regon_numbers': self.extract_regon_numbers(text),
            'krs_numbers': self.extract_krs_numbers(text),
            'vat_rates': self.extract_vat_rates(text),
            'polish_dates': self.extract_polish_dates(text),
            'currency_amounts': self.extract_currency_amounts(text),
            'invoice_numbers': self.extract_invoice_numbers(text),
            'company_names': self.extract_company_names(text),
            'payment_methods': self.extract_payment_methods(text),
            'payment_terms': self.extract_payment_terms(text),
            'bank_accounts': self.extract_bank_accounts(text),
            'emails': self.extract_emails(text),
            'phones': self.extract_phones(text),
            'addresses': self.extract_addresses(text)
        }
