"""
Invoice Field Extraction Engine for Polish Invoices

This service provides structured data extraction from OCR text,
specifically optimized for Polish invoice formats with comprehensive
field recognition, validation, and cross-validation capabilities.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class FieldType(Enum):
    """Types of invoice fields that can be extracted"""
    INVOICE_NUMBER = "invoice_number"
    DATE = "date"
    AMOUNT = "amount"
    COMPANY_NAME = "company_name"
    NIP_NUMBER = "nip_number"
    ADDRESS = "address"
    LINE_ITEM = "line_item"
    VAT_RATE = "vat_rate"
    BANK_ACCOUNT = "bank_account"


class ExtractionMethod(Enum):
    """Methods used for field extraction"""
    PATTERN_MATCHING = "pattern_matching"
    CONTEXT_ANALYSIS = "context_analysis"
    POSITION_BASED = "position_based"
    ML_RECOGNITION = "ml_recognition"
    CROSS_VALIDATION = "cross_validation"


@dataclass
class ExtractedField:
    """Container for extracted field information"""
    field_type: FieldType
    value: Any
    confidence: float
    extraction_method: ExtractionMethod
    context: str = ""
    position: Tuple[int, int] = (0, 0)  # start, end positions in text
    validation_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineItem:
    """Container for invoice line item information"""
    nazwa: str
    ilosc: Decimal
    jednostka: str
    cena_netto: Decimal
    vat: str
    wartosc_netto: Decimal
    wartosc_brutto: Decimal
    confidence: float
    line_number: int


@dataclass
class CompanyInfo:
    """Container for company information"""
    nazwa: str
    nip: str = ""
    regon: str = ""
    krs: str = ""
    ulica: str = ""
    numer_domu: str = ""
    kod_pocztowy: str = ""
    miejscowosc: str = ""
    kraj: str = "Polska"
    confidence: float = 0.0


class InvoiceFieldExtractor:
    """
    Advanced invoice field extraction engine for Polish invoices
    
    This service implements pattern-based extraction, company information recognition,
    line item parsing, VAT calculations, and cross-validation between multiple
    extraction methods to ensure high accuracy.
    """
    
    def __init__(self):
        self.polish_patterns = self._initialize_polish_patterns()
        self.validation_rules = self._initialize_validation_rules()
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'field_success_rates': {},
            'method_performance': {}
        }
    
    def extract_fields(self, ocr_text: str, confidence_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract structured invoice data from OCR text
        
        Args:
            ocr_text: Raw OCR text from document
            confidence_data: OCR confidence information
            
        Returns:
            Dictionary containing extracted invoice fields
        """
        try:
            logger.info("Starting invoice field extraction")
            
            # Initialize extraction result
            extraction_result = {
                'extracted_fields': {},
                'line_items': [],
                'seller_info': None,
                'buyer_info': None,
                'extraction_metadata': {
                    'total_fields_attempted': 0,
                    'successful_extractions': 0,
                    'confidence_scores': {},
                    'validation_results': {},
                    'cross_validation_results': {}
                }
            }
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(ocr_text)
            
            # Extract basic invoice fields
            basic_fields = self._extract_basic_fields(cleaned_text, confidence_data)
            extraction_result['extracted_fields'].update(basic_fields)
            
            # Extract company information
            seller_info, buyer_info = self._extract_company_information(cleaned_text)
            extraction_result['seller_info'] = seller_info
            extraction_result['buyer_info'] = buyer_info
            
            # Extract line items
            try:
                line_items = self._extract_line_items(cleaned_text)
                extraction_result['line_items'] = line_items
                logger.debug(f"Extracted {len(line_items)} line items")
            except Exception as e:
                logger.error(f"Error extracting line items: {e}")
                extraction_result['line_items'] = []
            
            # Perform cross-validation
            try:
                validation_results = self._perform_cross_validation(extraction_result, cleaned_text)
                extraction_result['extraction_metadata']['cross_validation_results'] = validation_results
            except Exception as e:
                logger.error(f"Error in cross-validation: {e}")
                extraction_result['extraction_metadata']['cross_validation_results'] = {
                    'error': str(e),
                    'overall_validation_score': 0.0
                }
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(extraction_result)
            extraction_result['overall_confidence'] = overall_confidence
            
            # Update statistics
            self._update_extraction_stats(extraction_result)
            
            logger.info(f"Field extraction completed with confidence: {overall_confidence:.1f}%")
            return extraction_result
            
        except Exception as e:
            logger.error(f"Error in invoice field extraction: {e}", exc_info=True)
            return {
                'extracted_fields': {},
                'line_items': [],
                'seller_info': None,
                'buyer_info': None,
                'extraction_error': str(e),
                'overall_confidence': 0.0
            }
    
    def _initialize_polish_patterns(self) -> Dict[str, List[str]]:
        """Initialize Polish-specific regex patterns for field extraction"""
        return {
            'invoice_numbers': [
                r'(?:Faktura|FV|F|Nr|Numer)[-:\s]*([A-Z]*\d+[/\-]\d+[/\-]\d+)',
                r'(?:Faktura\s+VAT\s+Nr|FAKTURA\s+VAT\s+Nr)[-:\s]*([A-Z0-9/\-]+)',
                r'(?:Faktura|FV|F|Nr|Numer)[-:\s]*([A-Z]*\d+)',
                r'([A-Z]*\d+[/\-]\d+[/\-]\d+)',
                r'(?:Faktura\s+VAT|FV)[-:\s]*([A-Z0-9/\-]+)',
                r'(?:Nr\s+faktury|Numer\s+faktury)[-:\s]*([A-Z0-9/\-]+)',
                r'([A-Z]{2,4}[/\-]\d+[/\-]\d{2,4})',
            ],
            'dates': [
                r'(\d{2})[.-/](\d{2})[.-/](\d{4})',
                r'(\d{4})[.-/](\d{2})[.-/](\d{2})',
                r'(\d{1,2})\s+(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+(\d{4})',
                r'(?:dnia\s+)?(\d{1,2})[.-/](\d{1,2})[.-/](\d{4})',
                r'(\d{2})\.(\d{2})\.(\d{2})',
                r'(?:Data\s+wystawienia|Data\s+sprzedaży|Termin\s+płatności)[-:\s]*(\d{1,2}[.-/]\d{1,2}[.-/]\d{2,4})',
            ],
            'amounts': [
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*zł',
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*PLN',
                r'PLN\s*(\d+(?:\s?\d{3})*[,.]?\d*)',
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*złotych?',
                r'(?:Suma|Razem|Łącznie|Do\s+zapłaty)[-:\s]*(\d+(?:\s?\d{3})*[,.]?\d*)\s*(?:zł|PLN)',
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*gr',
            ],
            'nip_numbers': [
                r'(?:NIP|VAT)[-:\s]*(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})',
                r'PL\s*(\d{10})',
                r'(?:Identyfikator\s+podatkowy|Nr\s+VAT)[-:\s]*(\d{10})',
                r'(\d{3}[-\s]*\d{3}[-\s]*\d{2}[-\s]*\d{2})',
            ],
            'company_names': [
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(Sp(?:ółka)?\.?\s*z\s*o\.?o\.?)',
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(S\.?A\.?)',
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(Spółka\s*Akcyjna)',
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(P\.?P\.?H\.?U?\.?)',
                r'(?:Sprzedawca|Nabywca|Firma)[-:\s]*([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]{3,50})',
            ],
            'addresses': [
                r'(\d{2}-\d{3})\s+([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)',
                r'ul\.\s*([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(\d+[a-zA-Z]?(?:/\d+)?)',
                r'(?:al\.|aleja)\s*([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(\d+[a-zA-Z]?)',
                r'(?:pl\.|plac)\s*([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(\d+[a-zA-Z]?)',
            ],
            'vat_rates': [
                r'(\d+)%\s*VAT',
                r'VAT\s*(\d+)%',
                r'(\d+)\s*proc\.?\s*VAT',
                r'stawka\s*VAT\s*(\d+)%',
                r'(\d+),(\d+)%\s*VAT',
                r'zwolnione\s*z\s*VAT',
                r'0%\s*VAT',
            ],
            'bank_accounts': [
                r'PL\s*(\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4})',
                r'(?:Nr\s+konta|Numer\s+konta|Konto)[-:\s]*PL\s*(\d{26})',
                r'(\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4})',
            ]
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for extracted fields"""
        return {
            'nip_validation': {
                'length': 10,
                'checksum_weights': [6, 5, 7, 2, 3, 4, 5, 6, 7]
            },
            'date_validation': {
                'min_year': 1990,
                'max_year': datetime.now().year + 2,
                'formats': ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']
            },
            'amount_validation': {
                'min_value': 0.01,
                'max_value': 10000000.00,
                'decimal_places': 2
            },
            'invoice_number_validation': {
                'min_length': 3,
                'max_length': 50,
                'allowed_chars': r'[A-Z0-9/\-]+'
            }
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess OCR text for better extraction"""
        if not text:
            return ""
        
        # Remove excessive whitespace but preserve line breaks
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive spaces within lines but keep the line structure
            cleaned_line = re.sub(r'[ \t]+', ' ', line.strip())
            if cleaned_line:  # Only add non-empty lines
                cleaned_lines.append(cleaned_line)
        
        text = '\n'.join(cleaned_lines)
        
        # Fix common OCR errors in Polish text
        text = text.replace('ą', 'ą').replace('ć', 'ć').replace('ę', 'ę')
        text = text.replace('ł', 'ł').replace('ń', 'ń').replace('ó', 'ó')
        text = text.replace('ś', 'ś').replace('ź', 'ź').replace('ż', 'ż')
        
        # Fix common number formatting issues (but be careful not to break table structure)
        text = re.sub(r'(\d),(\d{2})\s*zł', r'\1,\2 zł', text)  # Fix currency formatting
        
        return text.strip()
    
    def _extract_basic_fields(self, text: str, confidence_data: Dict[str, Any] = None) -> Dict[str, ExtractedField]:
        """Extract basic invoice fields using pattern matching"""
        extracted_fields = {}
        
        # Extract invoice numbers
        invoice_numbers = self._extract_invoice_numbers(text)
        if invoice_numbers:
            extracted_fields['numer_faktury'] = invoice_numbers[0]
        
        # Extract dates
        dates = self._extract_dates(text)
        extracted_fields.update(dates)
        
        # Extract amounts
        amounts = self._extract_amounts(text)
        extracted_fields.update(amounts)
        
        # Extract NIP numbers
        nip_numbers = self._extract_nip_numbers(text)
        extracted_fields.update(nip_numbers)
        
        # Extract VAT rates
        vat_rates = self._extract_vat_rates(text)
        if vat_rates:
            extracted_fields['vat_rates'] = vat_rates
        
        # Extract bank accounts
        bank_accounts = self._extract_bank_accounts(text)
        if bank_accounts:
            extracted_fields['bank_accounts'] = bank_accounts
        
        return extracted_fields
    
    def _extract_invoice_numbers(self, text: str) -> List[ExtractedField]:
        """Extract invoice numbers using multiple patterns"""
        found_numbers = []
        
        for pattern in self.polish_patterns['invoice_numbers']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                invoice_number = match.group(1) if match.groups() else match.group(0)
                
                # Validate invoice number
                if self._validate_invoice_number(invoice_number):
                    confidence = self._calculate_pattern_confidence(
                        pattern, match, text, FieldType.INVOICE_NUMBER
                    )
                    
                    found_numbers.append(ExtractedField(
                        field_type=FieldType.INVOICE_NUMBER,
                        value=invoice_number.strip(),
                        confidence=confidence,
                        extraction_method=ExtractionMethod.PATTERN_MATCHING,
                        context=text[max(0, match.start()-20):match.end()+20],
                        position=(match.start(), match.end())
                    ))
        
        # Sort by confidence and remove duplicates
        found_numbers.sort(key=lambda x: x.confidence, reverse=True)
        return self._deduplicate_fields(found_numbers)
    
    def _extract_dates(self, text: str) -> Dict[str, ExtractedField]:
        """Extract dates with type classification"""
        date_fields = {}
        found_dates = []
        
        polish_months = {
            'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04',
            'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08',
            'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'
        }
        
        for pattern in self.polish_patterns['dates']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    date_str = None
                    context = text[max(0, match.start()-30):match.end()+30].lower()
                    
                    if any(month in pattern for month in polish_months.keys()):
                        # Polish month names pattern
                        groups = match.groups()
                        if len(groups) >= 3:
                            day, month_name, year = groups[0], groups[1], groups[2]
                            month = polish_months.get(month_name.lower())
                            if month:
                                date_str = f"{year}-{month}-{day.zfill(2)}"
                    else:
                        # Numeric date patterns
                        groups = match.groups()
                        if len(groups) >= 3:
                            if len(groups[0]) == 4:  # YYYY-MM-DD format
                                year, month, day = groups[0], groups[1], groups[2]
                            else:  # DD.MM.YYYY format
                                day, month, year = groups[0], groups[1], groups[2]
                                if len(year) == 2:
                                    year = f"20{year}" if int(year) < 50 else f"19{year}"
                            
                            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    
                    if date_str and self._validate_date(date_str):
                        date_type = self._classify_date_type(context)
                        confidence = self._calculate_date_confidence(date_str, context)
                        
                        found_dates.append({
                            'date': date_str,
                            'type': date_type,
                            'confidence': confidence,
                            'context': context,
                            'position': (match.start(), match.end())
                        })
                
                except Exception as e:
                    logger.debug(f"Error parsing date: {e}")
                    continue
        
        # Sort by confidence and assign dates
        found_dates.sort(key=lambda x: x['confidence'], reverse=True)
        
        for date_info in found_dates:
            field_name = f"{date_info['type']}_date"
            if field_name not in date_fields:
                date_fields[field_name] = ExtractedField(
                    field_type=FieldType.DATE,
                    value=date_info['date'],
                    confidence=date_info['confidence'],
                    extraction_method=ExtractionMethod.PATTERN_MATCHING,
                    context=date_info['context'],
                    position=date_info['position'],
                    metadata={'date_type': date_info['type']}
                )
        
        return date_fields
    
    def _extract_amounts(self, text: str) -> Dict[str, ExtractedField]:
        """Extract monetary amounts with type classification"""
        amount_fields = {}
        found_amounts = []
        
        for pattern in self.polish_patterns['amounts']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1) if match.groups() else match.group(0)
                    context = text[max(0, match.start()-30):match.end()+30].lower()
                    
                    # Clean and parse amount
                    clean_amount = self._clean_amount_string(amount_str)
                    amount_value = self._parse_amount(clean_amount)
                    
                    if amount_value and self._validate_amount(amount_value):
                        amount_type = self._classify_amount_type(context)
                        confidence = self._calculate_amount_confidence(amount_value, context)
                        
                        found_amounts.append({
                            'amount': amount_value,
                            'type': amount_type,
                            'confidence': confidence,
                            'context': context,
                            'position': (match.start(), match.end())
                        })
                
                except Exception as e:
                    logger.debug(f"Error parsing amount: {e}")
                    continue
        
        # Sort by confidence and assign amounts
        found_amounts.sort(key=lambda x: x['confidence'], reverse=True)
        
        for amount_info in found_amounts:
            field_name = f"{amount_info['type']}_amount"
            if field_name not in amount_fields:
                amount_fields[field_name] = ExtractedField(
                    field_type=FieldType.AMOUNT,
                    value=float(amount_info['amount']),
                    confidence=amount_info['confidence'],
                    extraction_method=ExtractionMethod.PATTERN_MATCHING,
                    context=amount_info['context'],
                    position=amount_info['position'],
                    metadata={'amount_type': amount_info['type']}
                )
        
        return amount_fields
    
    def _extract_nip_numbers(self, text: str) -> Dict[str, ExtractedField]:
        """Extract and validate NIP numbers"""
        nip_fields = {}
        found_nips = []
        
        for pattern in self.polish_patterns['nip_numbers']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                nip_str = match.group(1) if match.groups() else match.group(0)
                clean_nip = re.sub(r'[^\d]', '', nip_str)
                
                if len(clean_nip) == 10 and self._validate_nip(clean_nip):
                    context = text[max(0, match.start()-30):match.end()+30].lower()
                    nip_type = self._classify_nip_type(context)
                    confidence = self._calculate_nip_confidence(clean_nip, context)
                    
                    found_nips.append({
                        'nip': clean_nip,
                        'type': nip_type,
                        'confidence': confidence,
                        'context': context,
                        'position': (match.start(), match.end())
                    })
        
        # Sort by confidence and assign NIPs
        found_nips.sort(key=lambda x: x['confidence'], reverse=True)
        
        for nip_info in found_nips:
            field_name = f"{nip_info['type']}_nip"
            if field_name not in nip_fields:
                nip_fields[field_name] = ExtractedField(
                    field_type=FieldType.NIP_NUMBER,
                    value=nip_info['nip'],
                    confidence=nip_info['confidence'],
                    extraction_method=ExtractionMethod.PATTERN_MATCHING,
                    context=nip_info['context'],
                    position=nip_info['position'],
                    metadata={'nip_type': nip_info['type']}
                )
        
        return nip_fields
    
    def _extract_vat_rates(self, text: str) -> List[ExtractedField]:
        """Extract VAT rates from text"""
        found_rates = []
        
        for pattern in self.polish_patterns['vat_rates']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if 'zwolnione' in match.group(0).lower():
                    vat_rate = 'zw'
                elif '0%' in match.group(0):
                    vat_rate = '0'
                else:
                    rate_match = re.search(r'(\d+)(?:,(\d+))?', match.group(0))
                    if rate_match:
                        if rate_match.group(2):  # Decimal rate
                            vat_rate = f"{rate_match.group(1)}.{rate_match.group(2)}"
                        else:
                            vat_rate = rate_match.group(1)
                    else:
                        continue
                
                context = text[max(0, match.start()-20):match.end()+20]
                confidence = self._calculate_pattern_confidence(
                    pattern, match, text, FieldType.VAT_RATE
                )
                
                found_rates.append(ExtractedField(
                    field_type=FieldType.VAT_RATE,
                    value=vat_rate,
                    confidence=confidence,
                    extraction_method=ExtractionMethod.PATTERN_MATCHING,
                    context=context,
                    position=(match.start(), match.end())
                ))
        
        return self._deduplicate_fields(found_rates)
    
    def _extract_bank_accounts(self, text: str) -> List[ExtractedField]:
        """Extract bank account numbers (IBAN)"""
        found_accounts = []
        
        for pattern in self.polish_patterns['bank_accounts']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                account_str = match.group(1) if match.groups() else match.group(0)
                clean_account = re.sub(r'[^\d]', '', account_str)
                
                if len(clean_account) == 26:  # Polish IBAN without country code
                    full_iban = f"PL{clean_account}"
                    if self._validate_iban(full_iban):
                        context = text[max(0, match.start()-20):match.end()+20]
                        confidence = self._calculate_pattern_confidence(
                            pattern, match, text, FieldType.BANK_ACCOUNT
                        )
                        
                        found_accounts.append(ExtractedField(
                            field_type=FieldType.BANK_ACCOUNT,
                            value=full_iban,
                            confidence=confidence,
                            extraction_method=ExtractionMethod.PATTERN_MATCHING,
                            context=context,
                            position=(match.start(), match.end())
                        ))
        
        return self._deduplicate_fields(found_accounts)    

    def _extract_company_information(self, text: str) -> Tuple[Optional[CompanyInfo], Optional[CompanyInfo]]:
        """Extract seller and buyer company information"""
        try:
            # Split text into sections to identify seller and buyer areas
            sections = self._identify_company_sections(text)
            
            seller_info = None
            buyer_info = None
            
            if sections.get('seller_section'):
                seller_info = self._extract_company_from_section(
                    sections['seller_section'], 'seller'
                )
            
            if sections.get('buyer_section'):
                buyer_info = self._extract_company_from_section(
                    sections['buyer_section'], 'buyer'
                )
            
            return seller_info, buyer_info
            
        except Exception as e:
            logger.error(f"Error extracting company information: {e}")
            return None, None
    
    def _identify_company_sections(self, text: str) -> Dict[str, str]:
        """Identify seller and buyer sections in the text"""
        sections = {}
        
        # Polish terms for seller and buyer sections
        seller_terms = ['sprzedawca', 'wystawca', 'usługodawca', 'dostawca']
        buyer_terms = ['nabywca', 'odbiorca', 'kupujący', 'zamawiający']
        
        lines = text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line indicates seller section
            if any(term in line_lower for term in seller_terms):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                current_section = 'seller_section'
                section_content = [line]
                continue
            
            # Check if line indicates buyer section
            if any(term in line_lower for term in buyer_terms):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                current_section = 'buyer_section'
                section_content = [line]
                continue
            
            # Add line to current section
            if current_section:
                section_content.append(line)
        
        # Add final section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
        
        return sections
    
    def _extract_company_from_section(self, section_text: str, company_type: str) -> CompanyInfo:
        """Extract company information from a text section"""
        company_info = CompanyInfo(nazwa="")
        
        # Extract company name
        company_name = self._extract_company_name(section_text)
        if company_name:
            company_info.nazwa = company_name
        
        # Extract NIP
        nip_match = None
        for pattern in self.polish_patterns['nip_numbers']:
            match = re.search(pattern, section_text, re.IGNORECASE)
            if match:
                nip_str = match.group(1) if match.groups() else match.group(0)
                clean_nip = re.sub(r'[^\d]', '', nip_str)
                if len(clean_nip) == 10 and self._validate_nip(clean_nip):
                    company_info.nip = clean_nip
                    break
        
        # Extract address components
        address_info = self._extract_address_from_section(section_text)
        company_info.ulica = address_info.get('ulica', '')
        company_info.numer_domu = address_info.get('numer_domu', '')
        company_info.kod_pocztowy = address_info.get('kod_pocztowy', '')
        company_info.miejscowosc = address_info.get('miejscowosc', '')
        
        # Calculate confidence based on extracted information
        confidence = 0.0
        if company_info.nazwa:
            confidence += 40.0
        if company_info.nip:
            confidence += 30.0
        if company_info.ulica:
            confidence += 15.0
        if company_info.kod_pocztowy:
            confidence += 15.0
        
        company_info.confidence = min(100.0, confidence)
        
        return company_info
    
    def _extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name using Polish business entity patterns"""
        for pattern in self.polish_patterns['company_names']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    return f"{match.group(1).strip()} {match.group(2).strip()}"
                else:
                    return match.group(0).strip()
        
        # Fallback: look for capitalized words that might be company names
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if (len(line) > 10 and 
                line[0].isupper() and 
                not line.lower().startswith(('ul.', 'al.', 'pl.', 'nip', 'regon'))):
                return line
        
        return None
    
    def _extract_address_from_section(self, text: str) -> Dict[str, str]:
        """Extract address components from text section"""
        address_info = {}
        
        # Extract postal code and city
        postal_match = re.search(r'(\d{2}-\d{3})\s+([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)', text)
        if postal_match:
            address_info['kod_pocztowy'] = postal_match.group(1)
            address_info['miejscowosc'] = postal_match.group(2).strip()
        
        # Extract street and house number
        for pattern in self.polish_patterns['addresses']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'ul.' in pattern or 'al.' in pattern or 'pl.' in pattern:
                    address_info['ulica'] = match.group(1).strip()
                    address_info['numer_domu'] = match.group(2).strip()
                    break
        
        return address_info
    
    def _extract_line_items(self, text: str) -> List[LineItem]:
        """Extract invoice line items with VAT calculations"""
        line_items = []
        
        try:
            # Look for table-like structures in the text
            lines = text.split('\n')
            table_section = self._identify_line_items_section(lines)
            
            if not table_section:
                return line_items
            
            # Parse line items from table section
            for i, line in enumerate(table_section):
                line_item = self._parse_line_item(line, i + 1)
                if line_item:
                    line_items.append(line_item)
            
            logger.info(f"Extracted {len(line_items)} line items")
            return line_items
            
        except Exception as e:
            logger.error(f"Error extracting line items: {e}")
            return []
    
    def _identify_line_items_section(self, lines: List[str]) -> List[str]:
        """Identify the section containing line items"""
        table_indicators = [
            'lp', 'l.p.', 'nazwa', 'opis', 'ilość', 'ilosc', 'j.m.', 'jednostka',
            'cena', 'wartość', 'wartosc', 'vat', 'brutto', 'netto'
        ]
        
        start_idx = None
        end_idx = None
        
        # Find start of table
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in table_indicators):
                # Check if this line contains multiple indicators (likely header)
                indicator_count = sum(1 for indicator in table_indicators if indicator in line_lower)
                if indicator_count >= 3:
                    start_idx = i + 1  # Start after header
                    break
        
        if start_idx is None:
            return []
        
        # Find end of table (look for summary terms)
        summary_terms = ['suma', 'razem', 'łącznie', 'do zapłaty', 'podsumowanie']
        for i in range(start_idx, len(lines)):
            line_lower = lines[i].lower()
            if any(term in line_lower for term in summary_terms):
                end_idx = i
                break
        
        if end_idx is None:
            end_idx = len(lines)
        
        return lines[start_idx:end_idx]
    
    def _parse_line_item(self, line: str, line_number: int) -> Optional[LineItem]:
        """Parse a single line item from text"""
        try:
            # Skip empty lines or lines that are too short
            if not line.strip() or len(line.strip()) < 10:
                return None
            
            # Split line by pipe characters or multiple spaces
            if '|' in line:
                parts = [part.strip() for part in line.split('|')]
            else:
                # Split by multiple spaces (2 or more)
                parts = [part.strip() for part in re.split(r'\s{2,}', line) if part.strip()]
            
            if len(parts) < 6:  # Need at least: lp, nazwa, ilosc, jednostka, cena, vat, wartosci
                return self._parse_line_item_alternative(line, line_number)
            
            try:
                # Skip line number if present
                start_idx = 1 if parts[0].isdigit() else 0
                
                nazwa = parts[start_idx].strip()
                ilosc = Decimal(str(parts[start_idx + 1]).replace(',', '.'))
                jednostka = parts[start_idx + 2].strip()
                cena_netto = Decimal(str(parts[start_idx + 3]).replace(',', '.'))
                vat = parts[start_idx + 4].strip()
                wartosc_netto = Decimal(str(parts[start_idx + 5]).replace(',', '.'))
                
                # Try to get brutto value if available
                if len(parts) > start_idx + 6:
                    wartosc_brutto = Decimal(str(parts[start_idx + 6]).replace(',', '.'))
                else:
                    # Calculate brutto from netto and VAT
                    if vat.replace('%', '').isdigit():
                        vat_rate = Decimal(vat.replace('%', '')) / 100
                        wartosc_brutto = wartosc_netto * (1 + vat_rate)
                    else:
                        wartosc_brutto = wartosc_netto
                
            except (InvalidOperation, ValueError, IndexError):
                return self._parse_line_item_alternative(line, line_number)
            
            # Calculate confidence based on data consistency
            confidence = self._calculate_line_item_confidence(
                ilosc, cena_netto, wartosc_netto, wartosc_brutto, vat
            )
            
            return LineItem(
                nazwa=nazwa,
                ilosc=ilosc,
                jednostka=jednostka,
                cena_netto=cena_netto,
                vat=vat,
                wartosc_netto=wartosc_netto,
                wartosc_brutto=wartosc_brutto,
                confidence=confidence,
                line_number=line_number
            )
            
        except Exception as e:
            logger.debug(f"Error parsing line item: {e}")
            return None
    
    def _parse_line_item_alternative(self, line: str, line_number: int) -> Optional[LineItem]:
        """Alternative parsing method for different line item formats"""
        # Extract numbers from the line
        numbers = re.findall(r'\d+(?:[,.]?\d+)?', line)
        if len(numbers) < 4:
            return None
        
        # Extract text (likely product name)
        text_parts = re.findall(r'[A-Za-ząćęłńóśżźĄĆĘŁŃÓŚŻŹ\s]+', line)
        nazwa = ' '.join(text_parts).strip() if text_parts else f"Pozycja {line_number}"
        
        try:
            # Assume standard order: quantity, unit price, net value, gross value
            ilosc = Decimal(numbers[0].replace(',', '.'))
            cena_netto = Decimal(numbers[1].replace(',', '.'))
            wartosc_netto = Decimal(numbers[-2].replace(',', '.'))
            wartosc_brutto = Decimal(numbers[-1].replace(',', '.'))
            
            # Extract VAT rate
            vat_match = re.search(r'(\d+)%|zw', line, re.IGNORECASE)
            vat = vat_match.group(0) if vat_match else '23'
            
            # Default unit
            jednostka = 'szt'
            
            confidence = self._calculate_line_item_confidence(
                ilosc, cena_netto, wartosc_netto, wartosc_brutto, vat
            )
            
            return LineItem(
                nazwa=nazwa,
                ilosc=ilosc,
                jednostka=jednostka,
                cena_netto=cena_netto,
                vat=vat,
                wartosc_netto=wartosc_netto,
                wartosc_brutto=wartosc_brutto,
                confidence=confidence,
                line_number=line_number
            )
            
        except (InvalidOperation, ValueError, IndexError):
            return None
    
    def _perform_cross_validation(self, extraction_result: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Perform cross-validation between multiple extraction methods"""
        validation_results = {
            'field_validations': {},
            'consistency_checks': {},
            'confidence_adjustments': {}
        }
        
        try:
            # Validate extracted amounts against line items
            amount_validation = self._validate_amounts_against_line_items(
                extraction_result.get('extracted_fields', {}),
                extraction_result.get('line_items', [])
            )
            validation_results['field_validations']['amounts'] = amount_validation
            
            # Validate company information consistency
            company_validation = self._validate_company_information(
                extraction_result.get('seller_info'),
                extraction_result.get('buyer_info'),
                extraction_result.get('extracted_fields', {})
            )
            validation_results['field_validations']['companies'] = company_validation
            
            # Validate date consistency
            date_validation = self._validate_date_consistency(
                extraction_result.get('extracted_fields', {})
            )
            validation_results['field_validations']['dates'] = date_validation
            
            # Calculate overall validation score
            validation_score = self._calculate_validation_score(validation_results)
            validation_results['overall_validation_score'] = validation_score
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in cross-validation: {e}")
            return {'error': str(e), 'overall_validation_score': 0.0}
    
    def _validate_amounts_against_line_items(self, fields: Dict[str, Any], 
                                           line_items: List[LineItem]) -> Dict[str, Any]:
        """Validate extracted amounts against calculated line item totals"""
        validation = {'is_valid': True, 'discrepancies': [], 'confidence_adjustment': 0.0}
        
        if not line_items:
            return validation
        
        # Calculate totals from line items
        calculated_netto = sum(item.wartosc_netto for item in line_items)
        calculated_brutto = sum(item.wartosc_brutto for item in line_items)
        
        # Compare with extracted amounts
        for field_name, field in fields.items():
            # Handle both single fields and lists of fields
            fields_to_check = [field] if not isinstance(field, list) else field
            
            for single_field in fields_to_check:
                if not isinstance(single_field, ExtractedField):
                    continue
                    
                if 'amount' in field_name and single_field.field_type == FieldType.AMOUNT:
                    extracted_amount = Decimal(str(single_field.value))
                    
                    if 'netto' in field_name.lower():
                        difference = abs(extracted_amount - calculated_netto)
                        tolerance = calculated_netto * Decimal('0.05')  # 5% tolerance
                        
                        if difference > tolerance:
                            validation['is_valid'] = False
                            validation['discrepancies'].append({
                                'field': field_name,
                                'extracted': float(extracted_amount),
                                'calculated': float(calculated_netto),
                                'difference': float(difference)
                            })
                            validation['confidence_adjustment'] -= 20.0
                        else:
                            validation['confidence_adjustment'] += 10.0
                    
                    elif 'brutto' in field_name.lower():
                        difference = abs(extracted_amount - calculated_brutto)
                        tolerance = calculated_brutto * Decimal('0.05')
                        
                        if difference > tolerance:
                            validation['is_valid'] = False
                            validation['discrepancies'].append({
                                'field': field_name,
                                'extracted': float(extracted_amount),
                                'calculated': float(calculated_brutto),
                                'difference': float(difference)
                            })
                            validation['confidence_adjustment'] -= 20.0
                        else:
                            validation['confidence_adjustment'] += 10.0
        
        return validation
    
    def _validate_company_information(self, seller_info: Optional[CompanyInfo], 
                                    buyer_info: Optional[CompanyInfo],
                                    fields: Dict[str, Any]) -> Dict[str, Any]:
        """Validate company information consistency"""
        validation = {'is_valid': True, 'issues': [], 'confidence_adjustment': 0.0}
        
        # Check if NIP numbers from fields match company info
        for field_name, field in fields.items():
            # Handle both single fields and lists of fields
            fields_to_check = [field] if not isinstance(field, list) else field
            
            for single_field in fields_to_check:
                if not isinstance(single_field, ExtractedField):
                    continue
                    
                if single_field.field_type == FieldType.NIP_NUMBER:
                    nip_value = single_field.value
                    
                    if 'seller' in field_name or 'sprzedawca' in field_name:
                        if seller_info and seller_info.nip and seller_info.nip != nip_value:
                            validation['is_valid'] = False
                            validation['issues'].append(f"Seller NIP mismatch: {seller_info.nip} vs {nip_value}")
                            validation['confidence_adjustment'] -= 15.0
                        else:
                            validation['confidence_adjustment'] += 5.0
                    
                    elif 'buyer' in field_name or 'nabywca' in field_name:
                        if buyer_info and buyer_info.nip and buyer_info.nip != nip_value:
                            validation['is_valid'] = False
                            validation['issues'].append(f"Buyer NIP mismatch: {buyer_info.nip} vs {nip_value}")
                            validation['confidence_adjustment'] -= 15.0
                        else:
                            validation['confidence_adjustment'] += 5.0
        
        return validation
    
    def _validate_date_consistency(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Validate date field consistency"""
        validation = {'is_valid': True, 'issues': [], 'confidence_adjustment': 0.0}
        
        dates = {}
        for field_name, field in fields.items():
            # Handle both single fields and lists of fields
            fields_to_check = [field] if not isinstance(field, list) else field
            
            for single_field in fields_to_check:
                if not isinstance(single_field, ExtractedField):
                    continue
                    
                if single_field.field_type == FieldType.DATE:
                    try:
                        date_obj = datetime.strptime(single_field.value, '%Y-%m-%d').date()
                        dates[field_name] = date_obj
                    except ValueError:
                        validation['issues'].append(f"Invalid date format: {single_field.value}")
                        validation['confidence_adjustment'] -= 10.0
        
        # Check date logic (invoice date should be <= sale date <= due date)
        if 'invoice_date' in dates and 'sale_date' in dates:
            if dates['invoice_date'] > dates['sale_date']:
                validation['is_valid'] = False
                validation['issues'].append("Invoice date is after sale date")
                validation['confidence_adjustment'] -= 15.0
        
        if 'sale_date' in dates and 'due_date' in dates:
            if dates['sale_date'] > dates['due_date']:
                validation['is_valid'] = False
                validation['issues'].append("Sale date is after due date")
                validation['confidence_adjustment'] -= 15.0
        
        return validation
    
    def _calculate_overall_confidence(self, extraction_result: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the extraction"""
        total_confidence = 0.0
        field_count = 0
        
        # Weight different field types
        field_weights = {
            FieldType.INVOICE_NUMBER: 20.0,
            FieldType.DATE: 15.0,
            FieldType.AMOUNT: 25.0,
            FieldType.COMPANY_NAME: 15.0,
            FieldType.NIP_NUMBER: 20.0,
            FieldType.LINE_ITEM: 5.0
        }
        
        # Calculate weighted confidence from extracted fields
        for field_name, field in extraction_result.get('extracted_fields', {}).items():
            if isinstance(field, ExtractedField):
                weight = field_weights.get(field.field_type, 5.0)
                total_confidence += field.confidence * weight / 100.0
                field_count += 1
            elif isinstance(field, list):
                # Handle lists of fields (like VAT rates, bank accounts)
                for item in field:
                    if isinstance(item, ExtractedField):
                        weight = field_weights.get(item.field_type, 5.0)
                        total_confidence += item.confidence * weight / 100.0
                        field_count += 1
        
        # Add confidence from company information
        if extraction_result.get('seller_info'):
            total_confidence += extraction_result['seller_info'].confidence * 0.15
            field_count += 1
        
        if extraction_result.get('buyer_info'):
            total_confidence += extraction_result['buyer_info'].confidence * 0.10
            field_count += 1
        
        # Add confidence from line items
        line_items = extraction_result.get('line_items', [])
        if line_items:
            avg_line_confidence = sum(item.confidence for item in line_items) / len(line_items)
            total_confidence += avg_line_confidence * 0.10
            field_count += 1
        
        # Apply cross-validation adjustments
        validation_results = extraction_result.get('extraction_metadata', {}).get('cross_validation_results', {})
        validation_score = validation_results.get('overall_validation_score', 0.0)
        total_confidence += validation_score * 0.15
        
        # Calculate final confidence
        if field_count > 0:
            final_confidence = total_confidence / field_count * 100.0
        else:
            final_confidence = 0.0
        
        return min(100.0, max(0.0, final_confidence))
    
    # Helper methods for validation and calculation
    
    def _validate_invoice_number(self, invoice_number: str) -> bool:
        """Validate invoice number format"""
        rules = self.validation_rules['invoice_number_validation']
        return (rules['min_length'] <= len(invoice_number) <= rules['max_length'] and
                re.match(rules['allowed_chars'], invoice_number))
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date string"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            rules = self.validation_rules['date_validation']
            return rules['min_year'] <= date_obj.year <= rules['max_year']
        except ValueError:
            return False
    
    def _validate_amount(self, amount: Decimal) -> bool:
        """Validate amount value"""
        rules = self.validation_rules['amount_validation']
        return rules['min_value'] <= float(amount) <= rules['max_value']
    
    def _validate_nip(self, nip: str) -> bool:
        """Validate Polish NIP number using checksum"""
        if len(nip) != 10 or not nip.isdigit():
            return False
        
        # Reject obviously invalid NIPs
        if nip == "0000000000" or nip == "1111111111" or len(set(nip)) == 1:
            return False
        
        weights = self.validation_rules['nip_validation']['checksum_weights']
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        
        # Handle special case where checksum is 10
        if checksum == 10:
            return False
        
        return checksum == int(nip[9])
    
    def _validate_iban(self, iban: str) -> bool:
        """Basic IBAN validation for Polish accounts"""
        if not iban.startswith('PL') or len(iban) != 28:
            return False
        
        # Basic format check - full IBAN validation would be more complex
        return iban[2:].isdigit()
    
    def _clean_amount_string(self, amount_str: str) -> str:
        """Clean amount string for parsing"""
        # Remove spaces and normalize decimal separators
        clean = re.sub(r'\s+', '', amount_str)
        clean = clean.replace(',', '.')
        return clean
    
    def _parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string to Decimal"""
        try:
            return Decimal(amount_str)
        except (InvalidOperation, ValueError):
            return None
    
    def _classify_date_type(self, context: str) -> str:
        """Classify date type based on context"""
        context_lower = context.lower()
        
        if any(term in context_lower for term in ['wystawienia', 'wystawiono', 'data faktury']):
            return 'invoice'
        elif any(term in context_lower for term in ['sprzedaży', 'sprzedano', 'wykonania', 'dostawy']):
            return 'sale'
        elif any(term in context_lower for term in ['płatności', 'zapłaty', 'termin']):
            return 'due'
        else:
            return 'unknown'
    
    def _classify_amount_type(self, context: str) -> str:
        """Classify amount type based on context"""
        context_lower = context.lower()
        
        if any(term in context_lower for term in ['suma', 'razem', 'łącznie', 'do zapłaty']):
            return 'total'
        elif 'netto' in context_lower:
            return 'netto'
        elif 'brutto' in context_lower:
            return 'brutto'
        elif 'vat' in context_lower:
            return 'vat'
        else:
            return 'unknown'
    
    def _classify_nip_type(self, context: str) -> str:
        """Classify NIP type based on context"""
        context_lower = context.lower()
        
        if any(term in context_lower for term in ['sprzedawca', 'wystawca', 'dostawca']):
            return 'seller'
        elif any(term in context_lower for term in ['nabywca', 'odbiorca', 'kupujący']):
            return 'buyer'
        else:
            return 'unknown'
    
    def _calculate_pattern_confidence(self, pattern: str, match: re.Match, 
                                    text: str, field_type: FieldType) -> float:
        """Calculate confidence score for pattern-based extraction"""
        base_confidence = 70.0
        
        # Pattern specificity bonus
        if len(pattern) > 50:
            base_confidence += 10.0
        
        # Context relevance bonus
        context = text[max(0, match.start()-30):match.end()+30].lower()
        
        relevant_terms = {
            FieldType.INVOICE_NUMBER: ['faktura', 'nr', 'numer'],
            FieldType.DATE: ['data', 'dnia', 'termin'],
            FieldType.AMOUNT: ['zł', 'pln', 'suma', 'razem'],
            FieldType.NIP_NUMBER: ['nip', 'vat', 'podatek'],
            FieldType.COMPANY_NAME: ['sprzedawca', 'nabywca', 'firma']
        }
        
        if field_type in relevant_terms:
            for term in relevant_terms[field_type]:
                if term in context:
                    base_confidence += 5.0
                    break
        
        return min(100.0, base_confidence)
    
    def _calculate_date_confidence(self, date_str: str, context: str) -> float:
        """Calculate confidence score for extracted date"""
        confidence = 70.0
        
        # Date format bonus
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            confidence += 10.0
        
        # Reasonableness check
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            current_year = datetime.now().year
            
            if current_year - 5 <= date_obj.year <= current_year + 1:
                confidence += 15.0
            else:
                confidence -= 20.0
        except ValueError:
            confidence -= 30.0
        
        # Context relevance
        if any(term in context for term in ['data', 'dnia', 'wystawienia', 'sprzedaży']):
            confidence += 5.0
        
        return min(100.0, max(0.0, confidence))
    
    def _calculate_amount_confidence(self, amount: Decimal, context: str) -> float:
        """Calculate confidence score for extracted amount"""
        confidence = 70.0
        
        # Reasonable amount range
        amount_float = float(amount)
        if 0.01 <= amount_float <= 1000000:
            confidence += 15.0
        else:
            confidence -= 25.0
        
        # Context relevance
        if any(term in context for term in ['zł', 'pln', 'suma', 'razem', 'zapłaty']):
            confidence += 10.0
        
        return min(100.0, max(0.0, confidence))
    
    def _calculate_nip_confidence(self, nip: str, context: str) -> float:
        """Calculate confidence score for extracted NIP"""
        confidence = 60.0
        
        # Checksum validation
        if self._validate_nip(nip):
            confidence += 30.0
        else:
            confidence -= 40.0
        
        # Context relevance
        if any(term in context for term in ['nip', 'vat', 'podatek']):
            confidence += 10.0
        
        return min(100.0, max(0.0, confidence))
    
    def _calculate_line_item_confidence(self, ilosc: Decimal, cena_netto: Decimal,
                                      wartosc_netto: Decimal, wartosc_brutto: Decimal,
                                      vat: str) -> float:
        """Calculate confidence score for line item"""
        confidence = 60.0
        
        try:
            # Check calculation consistency
            calculated_netto = ilosc * cena_netto
            tolerance = calculated_netto * Decimal('0.05')
            
            if abs(calculated_netto - wartosc_netto) <= tolerance:
                confidence += 20.0
            else:
                confidence -= 15.0
            
            # Check VAT calculation if possible
            if vat.isdigit():
                vat_rate = Decimal(vat) / 100
                calculated_brutto = wartosc_netto * (1 + vat_rate)
                brutto_tolerance = calculated_brutto * Decimal('0.05')
                
                if abs(calculated_brutto - wartosc_brutto) <= brutto_tolerance:
                    confidence += 15.0
                else:
                    confidence -= 10.0
            
        except (InvalidOperation, ValueError):
            confidence -= 20.0
        
        return min(100.0, max(0.0, confidence))
    
    def _calculate_validation_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall validation score"""
        total_score = 0.0
        validations = validation_results.get('field_validations', {})
        
        for validation in validations.values():
            if isinstance(validation, dict):
                adjustment = validation.get('confidence_adjustment', 0.0)
                total_score += adjustment
        
        return max(-50.0, min(50.0, total_score))  # Cap between -50 and +50
    
    def _deduplicate_fields(self, fields: List[ExtractedField]) -> List[ExtractedField]:
        """Remove duplicate fields, keeping highest confidence ones"""
        seen = {}
        result = []
        
        for field in fields:
            key = (field.field_type, str(field.value).lower().strip())
            if key not in seen or seen[key].confidence < field.confidence:
                seen[key] = field
        
        return list(seen.values())
    
    def _update_extraction_stats(self, extraction_result: Dict[str, Any]):
        """Update extraction statistics"""
        self.extraction_stats['total_extractions'] += 1
        
        if extraction_result.get('overall_confidence', 0) > 70.0:
            self.extraction_stats['successful_extractions'] += 1
        
        # Update field success rates
        for field_name, field in extraction_result.get('extracted_fields', {}).items():
            if isinstance(field, ExtractedField):
                if field.field_type.value not in self.extraction_stats['field_success_rates']:
                    self.extraction_stats['field_success_rates'][field.field_type.value] = {'total': 0, 'successful': 0}
                
                self.extraction_stats['field_success_rates'][field.field_type.value]['total'] += 1
                if field.confidence > 70.0:
                    self.extraction_stats['field_success_rates'][field.field_type.value]['successful'] += 1
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get extraction performance statistics"""
        stats = self.extraction_stats.copy()
        
        # Calculate success rates
        if stats['total_extractions'] > 0:
            stats['overall_success_rate'] = stats['successful_extractions'] / stats['total_extractions']
        else:
            stats['overall_success_rate'] = 0.0
        
        # Calculate field-specific success rates
        for field_type, field_stats in stats['field_success_rates'].items():
            if field_stats['total'] > 0:
                field_stats['success_rate'] = field_stats['successful'] / field_stats['total']
            else:
                field_stats['success_rate'] = 0.0
        
        return stats