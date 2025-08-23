"""
Polish Invoice Processor - Custom training and pattern recognition for Polish invoices
"""

import re
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


class PolishInvoiceProcessor:
    """
    Specialized processor for Polish invoices with enhanced pattern recognition
    """
    
    def __init__(self):
        self.polish_patterns = {
            # Polish VAT patterns
            'vat_patterns': [
                r'VAT[-\s]*(\d{10})',  # VAT-1234567890
                r'NIP[-\s]*(\d{3}[-\s]*\d{3}[-\s]*\d{2}[-\s]*\d{2})',  # NIP 123-456-78-90
                r'NIP[-\s]*(\d{10})',  # NIP 1234567890
                r'(\d{3}[-\s]*\d{3}[-\s]*\d{2}[-\s]*\d{2})',  # 123-456-78-90
            ],
            
            # Polish date patterns
            'date_patterns': [
                r'(\d{2})[.-](\d{2})[.-](\d{4})',  # DD.MM.YYYY or DD-MM-YYYY
                r'(\d{4})[.-](\d{2})[.-](\d{2})',  # YYYY-MM-DD
                r'(\d{2})\s+(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+(\d{4})',  # Polish month names
            ],
            
            # Polish currency patterns
            'currency_patterns': [
                r'(\d+[,.]?\d*)\s*zł',  # 123,45 zł
                r'(\d+[,.]?\d*)\s*PLN',  # 123,45 PLN
                r'PLN\s*(\d+[,.]?\d*)',  # PLN 123,45
                r'(\d+[,.]?\d*)\s*złotych',  # 123,45 złotych
            ],
            
            # Polish company identifiers
            'company_patterns': [
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(Sp\.\s*z\s*o\.o\.)',  # Company Sp. z o.o.
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(S\.A\.)',  # Company S.A.
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(Spółka\s*Akcyjna)',  # Spółka Akcyjna
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(Sp\.\s*j\.)',  # Sp. j.
            ],
            
            # Polish invoice numbers
            'invoice_number_patterns': [
                r'(?:Faktura|FV|F|Nr)\s*[:/]?\s*(\d+[/\-]\d+[/\-]\d+)',  # FV/123/2024
                r'(?:Faktura|FV|F|Nr)\s*[:/]?\s*(\d+)',  # F 123
                r'(\d+[/\-]\d+[/\-]\d+)',  # 123/01/2024
            ],
            
            # Polish VAT rates
            'vat_rate_patterns': [
                r'(\d+)%\s*VAT',
                r'VAT\s*(\d+)%',
                r'(\d+)\s*proc\.?\s*VAT',
                r'stawka\s*VAT\s*(\d+)%',
            ]
        }
        
        self.polish_months = {
            'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04',
            'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08',
            'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'
        }
        
        self.common_polish_terms = {
            'seller_terms': ['sprzedawca', 'wystawca', 'usługodawca', 'dostawca'],
            'buyer_terms': ['nabywca', 'odbiorca', 'kupujący', 'zamawiający'],
            'amount_terms': ['suma', 'razem', 'łącznie', 'do zapłaty', 'należność'],
            'vat_terms': ['VAT', 'podatek', 'stawka'],
            'date_terms': ['data wystawienia', 'data sprzedaży', 'termin płatności']
        }

    def enhance_extraction(self, raw_text: str, base_extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance base OCR extraction with Polish-specific patterns
        """
        enhanced_data = base_extraction.copy()
        
        try:
            # Enhance VAT number extraction
            enhanced_data.update(self._extract_polish_vat_numbers(raw_text))
            
            # Enhance date extraction
            enhanced_data.update(self._extract_polish_dates(raw_text))
            
            # Enhance company names
            enhanced_data.update(self._extract_polish_companies(raw_text))
            
            # Enhance amounts and currency
            enhanced_data.update(self._extract_polish_amounts(raw_text))
            
            # Enhance invoice numbers
            enhanced_data.update(self._extract_polish_invoice_numbers(raw_text))
            
            # Add confidence boost for Polish patterns
            enhanced_data['polish_confidence_boost'] = self._calculate_polish_confidence(raw_text)
            
            # Apply confidence boost
            if 'confidence_score' in enhanced_data:
                boost = enhanced_data['polish_confidence_boost']
                enhanced_data['confidence_score'] = min(100.0, enhanced_data['confidence_score'] + boost)
            
            logger.info(f"Polish enhancement applied, confidence boost: {enhanced_data.get('polish_confidence_boost', 0):.1f}%")
            
        except Exception as e:
            logger.error(f"Error in Polish enhancement: {e}")
            enhanced_data['polish_enhancement_error'] = str(e)
        
        return enhanced_data

    def _extract_polish_vat_numbers(self, text: str) -> Dict[str, Any]:
        """Extract VAT numbers using Polish patterns"""
        vat_data = {}
        
        for pattern in self.polish_patterns['vat_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Clean and validate VAT numbers
                clean_vats = []
                for match in matches:
                    clean_vat = re.sub(r'[^\d]', '', match)
                    if len(clean_vat) == 10:  # Polish NIP is 10 digits
                        clean_vats.append(clean_vat)
                
                if clean_vats:
                    vat_data['polish_vat_numbers'] = clean_vats
                    if not vat_data.get('supplier_nip'):
                        vat_data['supplier_nip'] = clean_vats[0]
                    if len(clean_vats) > 1 and not vat_data.get('buyer_nip'):
                        vat_data['buyer_nip'] = clean_vats[1]
                break
        
        return vat_data

    def _extract_polish_dates(self, text: str) -> Dict[str, Any]:
        """Extract dates using Polish patterns"""
        date_data = {}
        
        for pattern in self.polish_patterns['date_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if pattern.count('stycznia|lutego') > 0:  # Polish month names pattern
                for match in matches:
                    try:
                        day, month_name, year = match
                        month = self.polish_months.get(month_name.lower())
                        if month:
                            date_str = f"{year}-{month}-{day.zfill(2)}"
                            if not date_data.get('invoice_date'):
                                date_data['invoice_date'] = date_str
                    except Exception:
                        continue
            else:
                for match in matches:
                    try:
                        if len(match) == 3:  # DD.MM.YYYY format
                            day, month, year = match
                            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        else:  # YYYY-MM-DD format
                            year, month, day = match
                            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        
                        if not date_data.get('invoice_date'):
                            date_data['invoice_date'] = date_str
                        elif not date_data.get('due_date'):
                            date_data['due_date'] = date_str
                    except Exception:
                        continue
        
        return date_data

    def _extract_polish_companies(self, text: str) -> Dict[str, Any]:
        """Extract company names using Polish patterns"""
        company_data = {}
        
        for pattern in self.polish_patterns['company_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    company_name = f"{match[0].strip()} {match[1].strip()}"
                else:
                    company_name = match.strip()
                
                if not company_data.get('supplier_name'):
                    company_data['supplier_name'] = company_name
                elif not company_data.get('buyer_name'):
                    company_data['buyer_name'] = company_name
        
        return company_data

    def _extract_polish_amounts(self, text: str) -> Dict[str, Any]:
        """Extract amounts using Polish currency patterns"""
        amount_data = {}
        amounts = []
        
        for pattern in self.polish_patterns['currency_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Convert Polish decimal notation (comma) to dot
                    amount_str = match.replace(',', '.')
                    amount = float(amount_str)
                    amounts.append(amount)
                except ValueError:
                    continue
        
        if amounts:
            amounts.sort(reverse=True)  # Largest first
            amount_data['polish_amounts'] = amounts
            
            # Assign amounts based on size
            if not amount_data.get('total_amount'):
                amount_data['total_amount'] = str(amounts[0])
            
            # Try to identify net and VAT amounts
            if len(amounts) >= 3:
                total = amounts[0]
                for i in range(1, len(amounts)):
                    for j in range(i + 1, len(amounts)):
                        net = amounts[i]
                        vat = amounts[j]
                        if abs(net + vat - total) < 0.01:  # Found net + VAT = total
                            amount_data['net_amount'] = str(net)
                            amount_data['vat_amount'] = str(vat)
                            break
        
        return amount_data

    def _extract_polish_invoice_numbers(self, text: str) -> Dict[str, Any]:
        """Extract invoice numbers using Polish patterns"""
        invoice_data = {}
        
        for pattern in self.polish_patterns['invoice_number_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the first match as invoice number
                invoice_data['invoice_number'] = matches[0]
                break
        
        return invoice_data

    def _calculate_polish_confidence(self, text: str) -> float:
        """Calculate confidence boost based on Polish pattern recognition"""
        confidence_boost = 0.0
        text_lower = text.lower()
        
        # Check for Polish terms
        polish_term_count = 0
        total_terms = 0
        
        for category, terms in self.common_polish_terms.items():
            total_terms += len(terms)
            for term in terms:
                if term in text_lower:
                    polish_term_count += 1
        
        # Base boost from Polish terms
        if total_terms > 0:
            term_ratio = polish_term_count / total_terms
            confidence_boost += term_ratio * 10.0  # Up to 10% boost
        
        # Pattern-based boosts
        pattern_matches = 0
        total_patterns = 0
        
        for category, patterns in self.polish_patterns.items():
            total_patterns += len(patterns)
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    pattern_matches += 1
        
        if total_patterns > 0:
            pattern_ratio = pattern_matches / total_patterns
            confidence_boost += pattern_ratio * 15.0  # Up to 15% boost
        
        # Currency check
        if any(curr in text_lower for curr in ['zł', 'pln', 'złoty']):
            confidence_boost += 5.0
        
        # VAT check
        if 'vat' in text_lower or 'nip' in text_lower:
            confidence_boost += 5.0
        
        return min(confidence_boost, 25.0)  # Max 25% boost

    def validate_polish_invoice(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data against Polish invoice requirements
        """
        validation_results = {
            'is_valid_polish_invoice': True,
            'validation_errors': [],
            'validation_warnings': []
        }
        
        # Required fields for Polish invoices
        required_fields = [
            'supplier_name', 'supplier_nip', 
            'buyer_name', 'invoice_number', 
            'invoice_date', 'net_amount', 'vat_amount', 'total_amount'
        ]
        
        for field in required_fields:
            if not extracted_data.get(field):
                validation_results['validation_errors'].append(f"Missing required field: {field}")
                validation_results['is_valid_polish_invoice'] = False
        
        # Validate NIP format
        for nip_field in ['supplier_nip', 'buyer_nip']:
            nip = extracted_data.get(nip_field)
            if nip and not self._validate_nip(nip):
                validation_results['validation_warnings'].append(f"Invalid NIP format: {nip}")
        
        # Validate amounts
        try:
            net = float(extracted_data.get('net_amount', 0))
            vat = float(extracted_data.get('vat_amount', 0))
            total = float(extracted_data.get('total_amount', 0))
            
            if abs(net + vat - total) > 0.01:
                validation_results['validation_warnings'].append("Net + VAT ≠ Total amount")
        except (ValueError, TypeError):
            validation_results['validation_errors'].append("Invalid amount format")
        
        return validation_results

    def _validate_nip(self, nip: str) -> bool:
        """Validate Polish NIP number using checksum algorithm"""
        if not nip:
            return False
        
        # Clean NIP - remove all non-digits
        clean_nip = re.sub(r'[^\d]', '', nip)
        
        if len(clean_nip) != 10:
            return False
        
        # NIP checksum validation
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(clean_nip[i]) * weights[i] for i in range(9)) % 11
        
        return checksum == int(clean_nip[9])

    def get_training_data_sample(self) -> Dict[str, Any]:
        """
        Generate sample training data for custom model training
        """
        return {
            'patterns': self.polish_patterns,
            'sample_invoices': [
                {
                    'text': 'Faktura VAT Nr FV/001/2024\nSprzedawca: ACME Sp. z o.o.\nNIP: 123-456-78-90\nNabywca: Klient Sp. j.\nDo zapłaty: 1230,00 zł',
                    'expected_extraction': {
                        'invoice_number': 'FV/001/2024',
                        'supplier_name': 'ACME Sp. z o.o.',
                        'supplier_nip': '1234567890',
                        'buyer_name': 'Klient Sp. j.',
                        'total_amount': '1230.00',
                        'currency': 'PLN'
                    }
                }
            ],
            'validation_rules': [
                'NIP must be 10 digits with valid checksum',
                'Total amount = Net amount + VAT amount',
                'Invoice number must follow Polish format',
                'Date must be in DD.MM.YYYY or YYYY-MM-DD format'
            ]
        }
