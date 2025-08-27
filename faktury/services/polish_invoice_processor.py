"""
Polish Invoice Processor - Enhanced custom training and pattern recognition for Polish invoices
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

# Conditional Django import
try:
    from django.conf import settings
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    settings = None

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


class PolishInvoiceProcessor:
    """
    Enhanced specialized processor for Polish invoices with advanced pattern recognition,
    ML-based entity recognition, and multi-layout support
    """
    
    def __init__(self):
        # Enhanced Polish patterns with more comprehensive coverage
        self.polish_patterns = {
            # Enhanced Polish VAT patterns
            'vat_patterns': [
                r'VAT[-\s]*(\d{10})',  # VAT-1234567890
                r'NIP[-\s]*(\d{3}[-\s]*\d{3}[-\s]*\d{2}[-\s]*\d{2})',  # NIP 123-456-78-90
                r'NIP[-\s]*(\d{10})',  # NIP 1234567890
                r'(\d{3}[-\s]*\d{3}[-\s]*\d{2}[-\s]*\d{2})',  # 123-456-78-90
                r'(?:NIP|VAT|Numer\s+VAT)[-:\s]*(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})',  # Various prefixes
                r'(?:Identyfikator\s+podatkowy|Nr\s+VAT)[-:\s]*(\d{10})',  # Full descriptions
                r'PL\s*(\d{10})',  # EU VAT format PL1234567890
            ],
            
            # Enhanced Polish date patterns
            'date_patterns': [
                r'(\d{2})[.-/](\d{2})[.-/](\d{4})',  # DD.MM.YYYY, DD-MM-YYYY, DD/MM/YYYY
                r'(\d{4})[.-/](\d{2})[.-/](\d{2})',  # YYYY-MM-DD, YYYY.MM.DD, YYYY/MM/DD
                r'(\d{1,2})\s+(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+(\d{4})',  # Polish month names
                r'(?:dnia\s+)?(\d{1,2})[.-/](\d{1,2})[.-/](\d{4})',  # "dnia DD.MM.YYYY"
                r'(\d{2})\.(\d{2})\.(\d{2})',  # DD.MM.YY
                r'(?:Data\s+wystawienia|Data\s+sprzedaży|Termin\s+płatności)[-:\s]*(\d{1,2}[.-/]\d{1,2}[.-/]\d{2,4})',  # Labeled dates
            ],
            
            # Enhanced Polish currency patterns
            'currency_patterns': [
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*zł',  # 1 234,45 zł (with thousands separator)
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*PLN',  # 1 234,45 PLN
                r'PLN\s*(\d+(?:\s?\d{3})*[,.]?\d*)',  # PLN 1 234,45
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*złotych?',  # złoty/złotych
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*zł(?:otych)?',  # Various złoty forms
                r'(?:Suma|Razem|Łącznie|Do\s+zapłaty)[-:\s]*(\d+(?:\s?\d{3})*[,.]?\d*)\s*(?:zł|PLN)',  # Labeled amounts
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*gr',  # grosze
            ],
            
            # Enhanced Polish company identifiers
            'company_patterns': [
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(Sp(?:ółka)?\.?\s*z\s*o\.?o\.?)',  # Sp. z o.o. variations
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(S\.?A\.?)',  # S.A. variations
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(Spółka\s*Akcyjna)',  # Full form
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(Sp\.?\s*j\.?)',  # Sp. j.
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(Sp\.?\s*k\.?)',  # Sp. k.
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(Sp\.?\s*p\.?)',  # Sp. p.
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(P\.?P\.?H\.?U?\.?)',  # PPHU
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(Firma\s+(?:Handlowa|Usługowa))',  # Firma types
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]+?)\s*(Przedsiębiorstwo)',  # Przedsiębiorstwo
            ],
            
            # Enhanced Polish invoice numbers
            'invoice_number_patterns': [
                r'(?:Faktura|FV|F|Nr|Numer)[-:\s]*([A-Z]*\d+[/\-]\d+[/\-]\d+)',  # FV/123/2024, FV-123-2024
                r'(?:Faktura|FV|F|Nr|Numer)[-:\s]*([A-Z]*\d+)',  # F 123, FV123
                r'([A-Z]*\d+[/\-]\d+[/\-]\d+)',  # 123/01/2024
                r'(?:Faktura\s+VAT|FV)[-:\s]*([A-Z0-9/\-]+)',  # Faktura VAT FV/123/2024
                r'(?:Nr\s+faktury|Numer\s+faktury)[-:\s]*([A-Z0-9/\-]+)',  # Nr faktury: 123/2024
                r'([A-Z]{2,4}[/\-]\d+[/\-]\d{2,4})',  # ABC/123/2024
            ],
            
            # Enhanced Polish VAT rates
            'vat_rate_patterns': [
                r'(\d+)%\s*VAT',
                r'VAT\s*(\d+)%',
                r'(\d+)\s*proc\.?\s*VAT',
                r'stawka\s*VAT\s*(\d+)%',
                r'(\d+)%\s*podatku',
                r'zwolnione\s*z\s*VAT',  # VAT exempt
                r'0%\s*VAT',  # 0% VAT
                r'(\d+),(\d+)%\s*VAT',  # Decimal VAT rates like 23,00%
            ],
            
            # Polish address patterns
            'address_patterns': [
                r'(\d{2}-\d{3})\s+([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)',  # 00-000 City
                r'ul\.\s*([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(\d+[a-zA-Z]?(?:/\d+)?)',  # ul. Street 123
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(\d+[a-zA-Z]?(?:/\d+)?)',  # Street 123
                r'(?:al\.|aleja)\s*([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(\d+[a-zA-Z]?)',  # Aleja
                r'(?:pl\.|plac)\s*([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s]+)\s*(\d+[a-zA-Z]?)',  # Plac
            ],
            
            # Polish bank account patterns (IBAN)
            'bank_account_patterns': [
                r'PL\s*(\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4})',  # Polish IBAN
                r'(?:Nr\s+konta|Numer\s+konta|Konto)[-:\s]*PL\s*(\d{26})',  # Account number
                r'(\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4})',  # IBAN without PL
            ],
            
            # Polish REGON patterns
            'regon_patterns': [
                r'REGON[-:\s]*(\d{9})',  # 9-digit REGON
                r'REGON[-:\s]*(\d{14})',  # 14-digit REGON
                r'(?:Nr\s+REGON|Numer\s+REGON)[-:\s]*(\d{9,14})',
            ],
            
            # Polish KRS patterns
            'krs_patterns': [
                r'KRS[-:\s]*(\d{10})',  # KRS number
                r'(?:Nr\s+KRS|Numer\s+KRS)[-:\s]*(\d{10})',
            ]
        }
        
        self.polish_months = {
            'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04',
            'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08',
            'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12',
            'styczeń': '01', 'luty': '02', 'marzec': '03', 'kwiecień': '04',
            'maj': '05', 'czerwiec': '06', 'lipiec': '07', 'sierpień': '08',
            'wrzesień': '09', 'październik': '10', 'listopad': '11', 'grudzień': '12'
        }
        
        # Enhanced Polish terms with more comprehensive coverage
        self.common_polish_terms = {
            'seller_terms': [
                'sprzedawca', 'wystawca', 'usługodawca', 'dostawca', 'wykonawca',
                'zleceniodawca', 'podmiot', 'firma', 'przedsiębiorstwo', 'organizacja'
            ],
            'buyer_terms': [
                'nabywca', 'odbiorca', 'kupujący', 'zamawiający', 'zleceniobiorca',
                'klient', 'kontrahent', 'strona', 'płatnik'
            ],
            'amount_terms': [
                'suma', 'razem', 'łącznie', 'do zapłaty', 'należność', 'wartość',
                'kwota', 'całość', 'ogółem', 'suma końcowa', 'suma całkowita'
            ],
            'vat_terms': [
                'VAT', 'podatek', 'stawka', 'podatek od towarów i usług',
                'VAT należny', 'VAT naliczony', 'zwolnione z VAT'
            ],
            'date_terms': [
                'data wystawienia', 'data sprzedaży', 'termin płatności',
                'data wykonania', 'data dostawy', 'data powstania obowiązku podatkowego',
                'wystawiono', 'sprzedano', 'wykonano', 'dostarczono'
            ],
            'invoice_terms': [
                'faktura', 'faktura VAT', 'faktura korygująca', 'faktura pro forma',
                'rachunek', 'nota', 'dokument', 'paragon'
            ],
            'payment_terms': [
                'płatność', 'zapłata', 'uregulowanie', 'wpłata', 'przelew',
                'gotówka', 'karta', 'czek', 'pobranie'
            ]
        }
        
        # Layout-specific patterns for different invoice types
        self.layout_patterns = {
            InvoiceLayout.STANDARD: {
                'header_indicators': ['faktura vat', 'faktura', 'invoice'],
                'required_sections': ['sprzedawca', 'nabywca', 'pozycje', 'podsumowanie'],
                'structure_weight': 1.0
            },
            InvoiceLayout.SIMPLIFIED: {
                'header_indicators': ['paragon', 'rachunek', 'nota'],
                'required_sections': ['sprzedawca', 'suma'],
                'structure_weight': 0.8
            },
            InvoiceLayout.PROFORMA: {
                'header_indicators': ['pro forma', 'proforma', 'faktura zaliczkowa', 'pf/'],
                'required_sections': ['sprzedawca', 'nabywca', 'pozycje'],
                'structure_weight': 0.9
            },
            InvoiceLayout.CORRECTION: {
                'header_indicators': ['faktura korygująca', 'korekta', 'nota korygująca'],
                'required_sections': ['sprzedawca', 'nabywca', 'korekta'],
                'structure_weight': 1.1
            },
            InvoiceLayout.RECEIPT: {
                'header_indicators': ['paragon fiskalny', 'paragon', 'kwit'],
                'required_sections': ['sprzedawca', 'pozycje', 'suma'],
                'structure_weight': 0.7
            }
        }
        
        # ML-based entity recognition patterns
        self.entity_patterns = {
            'COMPANY_NAME': [
                r'([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]{5,50})\s*(?:Sp\.|S\.A\.|Firma|Przedsiębiorstwo)',
                r'(?:Sprzedawca|Nabywca|Firma)[-:\s]*([A-ZĄĆĘŁŃÓŚŻŹ][a-ząćęłńóśżź\s\-&.,"()0-9]{3,50})'
            ],
            'NIP_NUMBER': [
                r'(?:NIP|VAT)[-:\s]*(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})',
                r'PL\s*(\d{10})'
            ],
            'INVOICE_NUMBER': [
                r'(?:Faktura|FV|Nr)[-:\s]*([A-Z0-9/\-]{3,20})',
                r'([A-Z]{2,4}[/\-]\d+[/\-]\d{2,4})'
            ],
            'AMOUNT': [
                r'(\d+(?:\s?\d{3})*[,.]?\d*)\s*(?:zł|PLN)',
                r'(?:Suma|Razem|Do zapłaty)[-:\s]*(\d+(?:\s?\d{3})*[,.]?\d*)'
            ],
            'DATE': [
                r'(\d{1,2}[.-/]\d{1,2}[.-/]\d{2,4})',
                r'(\d{1,2}\s+(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+\d{4})'
            ]
        }

    def enhance_extraction(self, raw_text: str, base_extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced extraction with ML-based entity recognition and multi-layout support
        """
        enhanced_data = base_extraction.copy()
        
        try:
            # Detect invoice layout type
            layout_type = self._detect_invoice_layout(raw_text)
            enhanced_data['detected_layout'] = layout_type.value
            
            # Apply ML-based entity recognition
            ml_entities = self._extract_entities_ml(raw_text)
            enhanced_data['ml_entities'] = ml_entities
            
            # Enhance VAT number extraction with improved validation
            enhanced_data.update(self._extract_polish_vat_numbers_enhanced(raw_text))
            
            # Enhance date extraction with multiple formats
            enhanced_data.update(self._extract_polish_dates_enhanced(raw_text))
            
            # Enhance company names with layout-aware extraction
            enhanced_data.update(self._extract_polish_companies_enhanced(raw_text, layout_type))
            
            # Enhance amounts and currency with better parsing
            enhanced_data.update(self._extract_polish_amounts_enhanced(raw_text))
            
            # Enhance invoice numbers with layout-specific patterns
            enhanced_data.update(self._extract_polish_invoice_numbers_enhanced(raw_text, layout_type))
            
            # Extract additional Polish-specific fields
            enhanced_data.update(self._extract_additional_polish_fields(raw_text))
            
            # Calculate improved confidence score
            enhanced_data['polish_confidence_boost'] = self._calculate_enhanced_polish_confidence(
                raw_text, enhanced_data, layout_type
            )
            
            # Apply confidence boost
            if 'confidence_score' in enhanced_data:
                boost = enhanced_data['polish_confidence_boost']
                enhanced_data['confidence_score'] = min(100.0, enhanced_data['confidence_score'] + boost)
            
            # Cross-validate extracted data
            validation_results = self._cross_validate_extraction(enhanced_data, ml_entities)
            enhanced_data.update(validation_results)
            
            logger.info(f"Enhanced Polish extraction completed. Layout: {layout_type.value}, "
                       f"Confidence boost: {enhanced_data.get('polish_confidence_boost', 0):.1f}%")
            
        except Exception as e:
            logger.error(f"Error in enhanced Polish extraction: {e}")
            enhanced_data['polish_enhancement_error'] = str(e)
        
        return enhanced_data

    def _detect_invoice_layout(self, text: str) -> InvoiceLayout:
        """Detect the type of Polish invoice layout"""
        text_lower = text.lower()
        layout_scores = {}
        
        for layout_type, patterns in self.layout_patterns.items():
            score = 0.0
            
            # Check header indicators
            for indicator in patterns['header_indicators']:
                if indicator in text_lower:
                    score += 2.0
            
            # Check required sections
            for section in patterns['required_sections']:
                if section in text_lower:
                    score += 1.0
            
            # Apply structure weight
            score *= patterns['structure_weight']
            layout_scores[layout_type] = score
        
        # Return layout with highest score, default to STANDARD
        if layout_scores:
            return max(layout_scores.items(), key=lambda x: x[1])[0]
        return InvoiceLayout.STANDARD

    def _extract_entities_ml(self, text: str) -> List[EntityRecognitionResult]:
        """ML-based entity recognition for Polish invoice elements"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Calculate confidence based on pattern specificity and context
                    confidence = self._calculate_entity_confidence(
                        entity_type, match.group(1) if match.groups() else match.group(0), 
                        text, match.start(), match.end()
                    )
                    
                    entities.append(EntityRecognitionResult(
                        entity_type=entity_type,
                        value=match.group(1) if match.groups() else match.group(0),
                        confidence=confidence,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=text[max(0, match.start()-20):match.end()+20]
                    ))
        
        # Sort by confidence and remove duplicates
        entities.sort(key=lambda x: x.confidence, reverse=True)
        return self._deduplicate_entities(entities)

    def _calculate_entity_confidence(self, entity_type: str, value: str, text: str, 
                                   start_pos: int, end_pos: int) -> float:
        """Calculate confidence score for extracted entity"""
        base_confidence = 0.7
        
        # Entity-specific confidence adjustments
        if entity_type == 'NIP_NUMBER':
            if self._validate_nip_enhanced(value):
                base_confidence += 0.25
            else:
                base_confidence -= 0.3
        
        elif entity_type == 'AMOUNT':
            # Check if amount is in reasonable range and format
            try:
                amount_val = float(value.replace(',', '.').replace(' ', ''))
                if 0.01 <= amount_val <= 1000000:  # Reasonable invoice amount range
                    base_confidence += 0.15
            except ValueError:
                base_confidence -= 0.2
        
        elif entity_type == 'DATE':
            # Validate date format and reasonableness
            if self._validate_polish_date(value):
                base_confidence += 0.2
        
        elif entity_type == 'COMPANY_NAME':
            # Check for Polish company indicators
            if any(indicator in value.lower() for indicator in ['sp.', 's.a.', 'firma', 'pphu']):
                base_confidence += 0.2
        
        # Context-based confidence adjustments
        context = text[max(0, start_pos-30):end_pos+30].lower()
        
        # Check for relevant keywords in context
        relevant_keywords = {
            'NIP_NUMBER': ['nip', 'vat', 'podatek'],
            'AMOUNT': ['zł', 'pln', 'suma', 'razem', 'zapłaty'],
            'DATE': ['data', 'dnia', 'wystawienia', 'sprzedaży'],
            'COMPANY_NAME': ['sprzedawca', 'nabywca', 'firma'],
            'INVOICE_NUMBER': ['faktura', 'nr', 'numer']
        }
        
        if entity_type in relevant_keywords:
            for keyword in relevant_keywords[entity_type]:
                if keyword in context:
                    base_confidence += 0.1
                    break
        
        return min(1.0, max(0.0, base_confidence))

    def _deduplicate_entities(self, entities: List[EntityRecognitionResult]) -> List[EntityRecognitionResult]:
        """Remove duplicate entities, keeping highest confidence ones"""
        seen = {}
        result = []
        
        for entity in entities:
            key = (entity.entity_type, entity.value.strip().lower())
            if key not in seen or seen[key].confidence < entity.confidence:
                seen[key] = entity
        
        return list(seen.values())

    def _extract_polish_vat_numbers_enhanced(self, text: str) -> Dict[str, Any]:
        """Enhanced VAT number extraction with improved validation"""
        vat_data = {}
        found_nips = []
        
        for pattern in self.polish_patterns['vat_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_nip = re.sub(r'[^\d]', '', match)
                if len(clean_nip) == 10 and self._validate_nip_enhanced(clean_nip):
                    found_nips.append({
                        'nip': clean_nip,
                        'formatted': self._format_nip(clean_nip),
                        'validation_score': self._calculate_nip_validation_score(clean_nip, text)
                    })
        
        if found_nips:
            # Sort by validation score
            found_nips.sort(key=lambda x: x['validation_score'], reverse=True)
            
            vat_data['polish_vat_numbers'] = [nip['nip'] for nip in found_nips]
            vat_data['formatted_nips'] = [nip['formatted'] for nip in found_nips]
            
            # Assign primary NIP (highest validation score)
            if not vat_data.get('supplier_nip'):
                vat_data['supplier_nip'] = found_nips[0]['nip']
                vat_data['supplier_nip_formatted'] = found_nips[0]['formatted']
            
            # Assign secondary NIP if available
            if len(found_nips) > 1 and not vat_data.get('buyer_nip'):
                vat_data['buyer_nip'] = found_nips[1]['nip']
                vat_data['buyer_nip_formatted'] = found_nips[1]['formatted']
        
        return vat_data

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

    def _extract_polish_dates_enhanced(self, text: str) -> Dict[str, Any]:
        """Enhanced date extraction with multiple Polish formats and validation"""
        date_data = {}
        found_dates = []
        
        for pattern in self.polish_patterns['date_patterns']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    date_str = None
                    context = text[max(0, match.start()-20):match.end()+20].lower()
                    
                    if 'stycznia|lutego' in pattern:  # Polish month names pattern
                        groups = match.groups()
                        if len(groups) >= 3:
                            day, month_name, year = groups[0], groups[1], groups[2]
                            month = self.polish_months.get(month_name.lower())
                            if month:
                                date_str = f"{year}-{month}-{day.zfill(2)}"
                    else:
                        groups = match.groups()
                        if len(groups) >= 3:
                            if len(groups[0]) == 4:  # YYYY-MM-DD format
                                year, month, day = groups[0], groups[1], groups[2]
                            else:  # DD.MM.YYYY format
                                day, month, year = groups[0], groups[1], groups[2]
                                if len(year) == 2:  # Convert YY to YYYY
                                    year = f"20{year}" if int(year) < 50 else f"19{year}"
                            
                            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    
                    if date_str and self._validate_polish_date(date_str):
                        # Determine date type based on context
                        date_type = self._classify_date_type(context)
                        found_dates.append({
                            'date': date_str,
                            'type': date_type,
                            'context': context,
                            'confidence': self._calculate_date_confidence(date_str, context)
                        })
                
                except Exception as e:
                    logger.debug(f"Error parsing date: {e}")
                    continue
        
        # Sort by confidence and assign dates
        found_dates.sort(key=lambda x: x['confidence'], reverse=True)
        
        for date_info in found_dates:
            if date_info['type'] == 'invoice' and not date_data.get('invoice_date'):
                date_data['invoice_date'] = date_info['date']
            elif date_info['type'] == 'sale' and not date_data.get('sale_date'):
                date_data['sale_date'] = date_info['date']
            elif date_info['type'] == 'due' and not date_data.get('due_date'):
                date_data['due_date'] = date_info['date']
            elif not date_data.get('invoice_date'):  # Fallback
                date_data['invoice_date'] = date_info['date']
        
        if found_dates:
            date_data['all_found_dates'] = [d['date'] for d in found_dates]
        
        return date_data

    def _classify_date_type(self, context: str) -> str:
        """Classify date type based on context"""
        context_lower = context.lower()
        
        if any(term in context_lower for term in ['wystawienia', 'wystawiono', 'data faktury']):
            return 'invoice'
        elif any(term in context_lower for term in ['sprzedaży', 'sprzedano', 'wykonania', 'dostawy', 'wykonano']):
            return 'sale'
        elif any(term in context_lower for term in ['płatności', 'zapłaty', 'termin']):
            return 'due'
        else:
            return 'unknown'

    def _calculate_date_confidence(self, date_str: str, context: str) -> float:
        """Calculate confidence score for extracted date"""
        confidence = 0.7
        
        # Check if date is reasonable (not too old or too far in future)
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            current_year = datetime.now().year
            
            if current_year - 5 <= date_obj.year <= current_year + 1:
                confidence += 0.2
            else:
                confidence -= 0.3
        except ValueError:
            confidence -= 0.4
        
        # Context-based confidence
        context_lower = context.lower()
        if any(term in context_lower for term in ['data', 'dnia', 'wystawienia', 'sprzedaży']):
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))

    def _validate_polish_date(self, date_str: str) -> bool:
        """Validate Polish date format and reasonableness"""
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            current_year = datetime.now().year
            
            # Check if date is within reasonable range
            return 1990 <= date_obj.year <= current_year + 2
        except ValueError:
            return False

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

    def _extract_polish_companies_enhanced(self, text: str, layout_type: InvoiceLayout) -> Dict[str, Any]:
        """Enhanced company extraction with layout-aware processing"""
        company_data = {}
        found_companies = []
        
        # Split text into sections for better company identification
        sections = self._identify_text_sections(text)
        
        for pattern in self.polish_patterns['company_patterns']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match.groups(), tuple) and len(match.groups()) >= 2:
                    company_name = f"{match.group(1).strip()} {match.group(2).strip()}"
                else:
                    company_name = match.group(0).strip()
                
                # Clean up company name
                company_name = self._clean_company_name(company_name)
                
                # Determine company role based on context and section
                role = self._determine_company_role(match, text, sections)
                
                found_companies.append({
                    'name': company_name,
                    'role': role,
                    'confidence': self._calculate_company_confidence(company_name, match, text),
                    'position': match.start()
                })
        
        # Sort by confidence and position
        found_companies.sort(key=lambda x: (x['confidence'], -x['position']), reverse=True)
        
        # Assign companies based on role and confidence
        for company in found_companies:
            if company['role'] == 'seller' and not company_data.get('supplier_name'):
                company_data['supplier_name'] = company['name']
            elif company['role'] == 'buyer' and not company_data.get('buyer_name'):
                company_data['buyer_name'] = company['name']
            elif not company_data.get('supplier_name'):  # Fallback
                company_data['supplier_name'] = company['name']
        
        if found_companies:
            company_data['all_found_companies'] = [c['name'] for c in found_companies]
        
        return company_data

    def _identify_text_sections(self, text: str) -> Dict[str, Tuple[int, int]]:
        """Identify different sections of the invoice text"""
        sections = {}
        text_lower = text.lower()
        
        # Find seller section
        seller_indicators = ['sprzedawca', 'wystawca', 'usługodawca', 'dostawca']
        for indicator in seller_indicators:
            pos = text_lower.find(indicator)
            if pos != -1:
                sections['seller'] = (pos, pos + 200)  # Approximate section length
                break
        
        # Find buyer section
        buyer_indicators = ['nabywca', 'odbiorca', 'kupujący', 'zamawiający']
        for indicator in buyer_indicators:
            pos = text_lower.find(indicator)
            if pos != -1:
                sections['buyer'] = (pos, pos + 200)
                break
        
        return sections

    def _clean_company_name(self, name: str) -> str:
        """Clean and normalize company name"""
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Remove common prefixes that might be captured
        prefixes_to_remove = ['sprzedawca:', 'nabywca:', 'firma:', 'nazwa:']
        for prefix in prefixes_to_remove:
            if name.lower().startswith(prefix):
                name = name[len(prefix):].strip()
        
        return name

    def _determine_company_role(self, match, text: str, sections: Dict[str, Tuple[int, int]]) -> str:
        """Determine if company is seller or buyer based on context"""
        match_pos = match.start()
        
        # Check which section the match falls into
        for section_type, (start, end) in sections.items():
            if start <= match_pos <= end:
                return 'seller' if section_type == 'seller' else 'buyer'
        
        # Fallback: check surrounding context
        context = text[max(0, match_pos-50):match_pos+50].lower()
        
        if any(term in context for term in ['sprzedawca', 'wystawca', 'usługodawca']):
            return 'seller'
        elif any(term in context for term in ['nabywca', 'odbiorca', 'kupujący']):
            return 'buyer'
        
        return 'unknown'

    def _calculate_company_confidence(self, company_name: str, match, text: str) -> float:
        """Calculate confidence score for extracted company"""
        confidence = 0.6
        
        # Length-based confidence (reasonable company name length)
        if 5 <= len(company_name) <= 100:
            confidence += 0.2
        else:
            confidence -= 0.2
        
        # Check for Polish company type indicators
        company_types = ['sp. z o.o.', 's.a.', 'sp. j.', 'sp. k.', 'pphu', 'firma']
        if any(comp_type in company_name.lower() for comp_type in company_types):
            confidence += 0.15
        
        # Context-based confidence
        context = text[max(0, match.start()-30):match.end()+30].lower()
        if any(term in context for term in ['sprzedawca', 'nabywca', 'firma']):
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))

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

    def _extract_polish_amounts_enhanced(self, text: str) -> Dict[str, Any]:
        """Enhanced amount extraction with better parsing and validation"""
        amount_data = {}
        found_amounts = []
        
        for pattern in self.polish_patterns['currency_patterns']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1) if match.groups() else match.group(0)
                    
                    # Clean and normalize amount
                    clean_amount = self._clean_polish_amount(amount_str)
                    amount_value = float(clean_amount)
                    
                    # Determine amount type based on context
                    context = text[max(0, match.start()-30):match.end()+30].lower()
                    amount_type = self._classify_amount_type(context, amount_value)
                    
                    found_amounts.append({
                        'value': amount_value,
                        'formatted': amount_str,
                        'type': amount_type,
                        'context': context,
                        'confidence': self._calculate_amount_confidence(amount_value, context)
                    })
                
                except (ValueError, AttributeError) as e:
                    logger.debug(f"Error parsing amount: {e}")
                    continue
        
        # Sort by confidence and value
        found_amounts.sort(key=lambda x: (x['confidence'], x['value']), reverse=True)
        
        # Assign amounts based on type and confidence
        for amount_info in found_amounts:
            amount_type = amount_info['type']
            value_str = f"{amount_info['value']:.2f}"
            
            if amount_type == 'total' and not amount_data.get('total_amount'):
                amount_data['total_amount'] = value_str
            elif amount_type == 'net' and not amount_data.get('net_amount'):
                amount_data['net_amount'] = value_str
            elif amount_type == 'vat' and not amount_data.get('vat_amount'):
                amount_data['vat_amount'] = value_str
            elif amount_type == 'gross' and not amount_data.get('gross_amount'):
                amount_data['gross_amount'] = value_str
        
        # Try to calculate missing amounts if we have some
        if found_amounts:
            amount_data = self._calculate_missing_amounts(amount_data, found_amounts)
            amount_data['all_found_amounts'] = [a['value'] for a in found_amounts]
        
        return amount_data

    def _clean_polish_amount(self, amount_str: str) -> str:
        """Clean Polish amount string for parsing"""
        # Remove currency symbols and extra text
        clean = re.sub(r'[^\d\s,.]', '', amount_str)
        
        # Handle thousands separators (spaces) and decimal separators (comma)
        # Polish format: 1 234,56 or 1234,56
        if ',' in clean and '.' in clean:
            # Both comma and dot present - assume dot is thousands, comma is decimal
            clean = clean.replace('.', '').replace(',', '.')
        elif ',' in clean:
            # Only comma - assume it's decimal separator
            clean = clean.replace(' ', '').replace(',', '.')
        else:
            # Only spaces and dots - remove spaces
            clean = clean.replace(' ', '')
        
        return clean

    def _classify_amount_type(self, context: str, amount_value: float) -> str:
        """Classify amount type based on context and value"""
        context_lower = context.lower()
        
        # Check for explicit labels
        if any(term in context_lower for term in ['suma', 'razem', 'łącznie', 'do zapłaty', 'należność']):
            return 'total'
        elif any(term in context_lower for term in ['netto', 'wartość netto', 'bez vat']):
            return 'net'
        elif any(term in context_lower for term in ['vat', 'podatek', 'kwota vat']):
            return 'vat'
        elif any(term in context_lower for term in ['brutto', 'z vat', 'wartość brutto']):
            return 'gross'
        else:
            # Heuristic based on amount value (VAT amounts are typically smaller)
            if amount_value < 100:
                return 'vat'
            else:
                return 'total'

    def _calculate_amount_confidence(self, amount_value: float, context: str) -> float:
        """Calculate confidence score for extracted amount"""
        confidence = 0.7
        
        # Value-based confidence (reasonable invoice amounts)
        if 0.01 <= amount_value <= 1000000:
            confidence += 0.2
        else:
            confidence -= 0.3
        
        # Context-based confidence
        context_lower = context.lower()
        if any(term in context_lower for term in ['zł', 'pln', 'suma', 'razem', 'zapłaty']):
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))

    def _calculate_missing_amounts(self, amount_data: Dict[str, Any], found_amounts: List[Dict]) -> Dict[str, Any]:
        """Calculate missing amounts using VAT calculation rules"""
        try:
            # Try to find net + VAT = total relationship
            amounts = [a['value'] for a in found_amounts]
            amounts.sort(reverse=True)
            
            for i, total in enumerate(amounts):
                for j, net in enumerate(amounts[i+1:], i+1):
                    vat = total - net
                    if vat > 0 and any(abs(a - vat) < 0.01 for a in amounts[j+1:]):
                        # Found valid net + VAT = total
                        if not amount_data.get('total_amount'):
                            amount_data['total_amount'] = f"{total:.2f}"
                        if not amount_data.get('net_amount'):
                            amount_data['net_amount'] = f"{net:.2f}"
                        if not amount_data.get('vat_amount'):
                            amount_data['vat_amount'] = f"{vat:.2f}"
                        break
        
        except Exception as e:
            logger.debug(f"Error calculating missing amounts: {e}")
        
        return amount_data

    def _extract_additional_polish_fields(self, text: str) -> Dict[str, Any]:
        """Extract additional Polish-specific fields"""
        additional_data = {}
        
        # Extract REGON numbers
        regon_numbers = []
        for pattern in self.polish_patterns['regon_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            regon_numbers.extend(matches)
        
        if regon_numbers:
            additional_data['regon_numbers'] = regon_numbers
            additional_data['supplier_regon'] = regon_numbers[0]
        
        # Extract KRS numbers
        krs_numbers = []
        for pattern in self.polish_patterns['krs_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            krs_numbers.extend(matches)
        
        if krs_numbers:
            additional_data['krs_numbers'] = krs_numbers
            additional_data['supplier_krs'] = krs_numbers[0]
        
        # Extract bank account numbers
        bank_accounts = []
        for pattern in self.polish_patterns['bank_account_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_account = re.sub(r'[^\d]', '', match)
                if len(clean_account) == 26:  # Polish IBAN length
                    bank_accounts.append(f"PL{clean_account}")
        
        if bank_accounts:
            additional_data['bank_accounts'] = bank_accounts
            additional_data['supplier_bank_account'] = bank_accounts[0]
        
        # Extract addresses
        addresses = []
        for pattern in self.polish_patterns['address_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            addresses.extend([' '.join(match) if isinstance(match, tuple) else match for match in matches])
        
        if addresses:
            additional_data['addresses'] = addresses[:2]  # Limit to 2 addresses
        
        return additional_data

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

    def _extract_polish_invoice_numbers_enhanced(self, text: str, layout_type: InvoiceLayout) -> Dict[str, Any]:
        """Enhanced invoice number extraction with layout-specific patterns"""
        invoice_data = {}
        found_numbers = []
        
        # Use layout-specific patterns if available
        patterns = self.polish_patterns['invoice_number_patterns']
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                invoice_number = match.group(1) if match.groups() else match.group(0)
                
                # Clean and validate invoice number
                clean_number = self._clean_invoice_number(invoice_number)
                if self._validate_polish_invoice_number(clean_number):
                    context = text[max(0, match.start()-20):match.end()+20].lower()
                    
                    found_numbers.append({
                        'number': clean_number,
                        'original': invoice_number,
                        'confidence': self._calculate_invoice_number_confidence(clean_number, context),
                        'position': match.start()
                    })
        
        # Sort by confidence and position (earlier in document is better)
        found_numbers.sort(key=lambda x: (x['confidence'], -x['position']), reverse=True)
        
        if found_numbers:
            invoice_data['invoice_number'] = found_numbers[0]['number']
            invoice_data['all_found_invoice_numbers'] = [n['number'] for n in found_numbers]
        
        return invoice_data

    def _clean_invoice_number(self, number: str) -> str:
        """Clean and normalize invoice number"""
        # Remove extra whitespace and common prefixes
        clean = number.strip()
        
        # Remove common prefixes that might be captured
        prefixes = ['faktura', 'fv', 'f', 'nr', 'numer', ':']
        for prefix in prefixes:
            if clean.lower().startswith(prefix):
                clean = clean[len(prefix):].strip(' :/-')
        
        return clean

    def _validate_polish_invoice_number(self, number: str) -> bool:
        """Validate Polish invoice number format"""
        if not number or len(number) < 3:
            return False
        
        # Common Polish invoice number patterns
        valid_patterns = [
            r'^[A-Z]*\d+[/\-]\d+[/\-]\d+$',  # FV/123/2024
            r'^[A-Z]*\d+$',  # FV123
            r'^\d+[/\-]\d+[/\-]\d+$',  # 123/01/2024
        ]
        
        return any(re.match(pattern, number) for pattern in valid_patterns)

    def _calculate_invoice_number_confidence(self, number: str, context: str) -> float:
        """Calculate confidence score for invoice number"""
        confidence = 0.7
        
        # Pattern-based confidence
        if re.match(r'^[A-Z]+[/\-]\d+[/\-]\d{4}$', number):  # FV/123/2024
            confidence += 0.2
        elif re.match(r'^\d+[/\-]\d+[/\-]\d{4}$', number):  # 123/01/2024
            confidence += 0.15
        
        # Context-based confidence
        if any(term in context for term in ['faktura', 'nr', 'numer']):
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))

    def _cross_validate_extraction(self, extracted_data: Dict[str, Any], 
                                 ml_entities: List[EntityRecognitionResult]) -> Dict[str, Any]:
        """Cross-validate extracted data with ML entities"""
        validation_data = {}
        
        # Cross-validate NIP numbers
        extracted_nips = extracted_data.get('polish_vat_numbers', [])
        ml_nips = [e.value for e in ml_entities if e.entity_type == 'NIP_NUMBER']
        
        if extracted_nips and ml_nips:
            # Check for consistency
            common_nips = set(extracted_nips) & set(ml_nips)
            if common_nips:
                validation_data['nip_cross_validation'] = 'consistent'
                validation_data['validated_nips'] = list(common_nips)
            else:
                validation_data['nip_cross_validation'] = 'inconsistent'
        
        # Cross-validate amounts
        extracted_amounts = extracted_data.get('all_found_amounts', [])
        ml_amounts = [float(e.value.replace(',', '.').replace(' ', '')) 
                     for e in ml_entities if e.entity_type == 'AMOUNT']
        
        if extracted_amounts and ml_amounts:
            # Check for similar amounts (within 1% tolerance)
            consistent_amounts = []
            for ext_amt in extracted_amounts:
                for ml_amt in ml_amounts:
                    if abs(ext_amt - ml_amt) / max(ext_amt, ml_amt) < 0.01:
                        consistent_amounts.append(ext_amt)
                        break
            
            if consistent_amounts:
                validation_data['amount_cross_validation'] = 'consistent'
                validation_data['validated_amounts'] = consistent_amounts
            else:
                validation_data['amount_cross_validation'] = 'inconsistent'
        
        return validation_data

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

    def _calculate_enhanced_polish_confidence(self, text: str, extracted_data: Dict[str, Any], 
                                            layout_type: InvoiceLayout) -> float:
        """Calculate enhanced confidence boost based on comprehensive Polish pattern recognition"""
        confidence_boost = 0.0
        text_lower = text.lower()
        
        # Base confidence from Polish terms (improved weighting)
        polish_term_score = self._calculate_term_confidence(text_lower)
        confidence_boost += polish_term_score * 8.0  # Up to 8% boost
        
        # Pattern-based confidence (enhanced)
        pattern_score = self._calculate_pattern_confidence(text, extracted_data)
        confidence_boost += pattern_score * 12.0  # Up to 12% boost
        
        # Layout-specific confidence
        layout_score = self._calculate_layout_confidence(text_lower, layout_type)
        confidence_boost += layout_score * 5.0  # Up to 5% boost
        
        # Data validation confidence
        validation_score = self._calculate_validation_confidence(extracted_data)
        confidence_boost += validation_score * 10.0  # Up to 10% boost
        
        # ML entity consistency confidence
        ml_consistency_score = self._calculate_ml_consistency_confidence(extracted_data)
        confidence_boost += ml_consistency_score * 8.0  # Up to 8% boost
        
        # Cross-validation confidence
        cross_validation_score = self._calculate_cross_validation_confidence(extracted_data)
        confidence_boost += cross_validation_score * 7.0  # Up to 7% boost
        
        return min(confidence_boost, 50.0)  # Max 50% boost

    def _calculate_term_confidence(self, text_lower: str) -> float:
        """Calculate confidence based on Polish terms presence"""
        total_score = 0.0
        total_weight = 0.0
        
        # Weighted term categories
        term_weights = {
            'invoice_terms': 2.0,
            'seller_terms': 1.5,
            'buyer_terms': 1.5,
            'amount_terms': 1.8,
            'vat_terms': 2.0,
            'date_terms': 1.2,
            'payment_terms': 1.0
        }
        
        for category, terms in self.common_polish_terms.items():
            if category in term_weights:
                weight = term_weights[category]
                found_terms = sum(1 for term in terms if term in text_lower)
                category_score = found_terms / len(terms)
                total_score += category_score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0

    def _calculate_pattern_confidence(self, text: str, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence based on pattern matching success"""
        pattern_scores = []
        
        # Check each pattern category
        for category, patterns in self.polish_patterns.items():
            category_matches = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    category_matches += 1
            
            if patterns:
                category_score = category_matches / len(patterns)
                pattern_scores.append(category_score)
        
        return sum(pattern_scores) / len(pattern_scores) if pattern_scores else 0.0

    def _calculate_layout_confidence(self, text_lower: str, layout_type: InvoiceLayout) -> float:
        """Calculate confidence based on detected layout type"""
        if layout_type not in self.layout_patterns:
            return 0.0
        
        layout_config = self.layout_patterns[layout_type]
        
        # Check header indicators
        header_score = 0.0
        for indicator in layout_config['header_indicators']:
            if indicator in text_lower:
                header_score += 1.0
        header_score /= len(layout_config['header_indicators'])
        
        # Check required sections
        section_score = 0.0
        for section in layout_config['required_sections']:
            if section in text_lower:
                section_score += 1.0
        section_score /= len(layout_config['required_sections'])
        
        # Apply structure weight
        return (header_score + section_score) / 2.0 * layout_config['structure_weight']

    def _calculate_validation_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence based on data validation results"""
        validation_score = 0.0
        checks = 0
        
        # NIP validation
        nips = extracted_data.get('polish_vat_numbers', [])
        if nips:
            valid_nips = sum(1 for nip in nips if self._validate_nip_enhanced(nip))
            validation_score += valid_nips / len(nips)
            checks += 1
        
        # Amount consistency
        if all(key in extracted_data for key in ['net_amount', 'vat_amount', 'total_amount']):
            try:
                net = float(extracted_data['net_amount'])
                vat = float(extracted_data['vat_amount'])
                total = float(extracted_data['total_amount'])
                
                if abs(net + vat - total) < 0.01:
                    validation_score += 1.0
                checks += 1
            except (ValueError, TypeError):
                pass
        
        # Date validation
        dates = extracted_data.get('all_found_dates', [])
        if dates:
            valid_dates = sum(1 for date in dates if self._validate_polish_date(date))
            validation_score += valid_dates / len(dates)
            checks += 1
        
        return validation_score / checks if checks > 0 else 0.0

    def _calculate_ml_consistency_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence based on ML entity consistency"""
        ml_entities = extracted_data.get('ml_entities', [])
        if not ml_entities:
            return 0.0
        
        # Calculate average confidence of ML entities
        avg_confidence = sum(entity.confidence for entity in ml_entities) / len(ml_entities)
        return avg_confidence

    def _calculate_cross_validation_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence based on cross-validation results"""
        confidence_score = 0.0
        validations = 0
        
        # NIP cross-validation
        if extracted_data.get('nip_cross_validation') == 'consistent':
            confidence_score += 1.0
        validations += 1
        
        # Amount cross-validation
        if extracted_data.get('amount_cross_validation') == 'consistent':
            confidence_score += 1.0
        validations += 1
        
        return confidence_score / validations if validations > 0 else 0.0

    def _validate_nip_enhanced(self, nip: str) -> bool:
        """Enhanced NIP validation with additional checks"""
        if not nip:
            return False
        
        # Clean NIP - remove all non-digits
        clean_nip = re.sub(r'[^\d]', '', nip)
        
        if len(clean_nip) != 10:
            return False
        
        # Check for obviously invalid patterns
        if clean_nip == '0000000000' or len(set(clean_nip)) == 1:
            return False
        
        # NIP checksum validation
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        try:
            checksum = sum(int(clean_nip[i]) * weights[i] for i in range(9)) % 11
            return checksum == int(clean_nip[9])
        except (ValueError, IndexError):
            return False

    def _format_nip(self, nip: str) -> str:
        """Format NIP in standard Polish format XXX-XXX-XX-XX"""
        clean_nip = re.sub(r'[^\d]', '', nip)
        if len(clean_nip) == 10:
            return f"{clean_nip[:3]}-{clean_nip[3:6]}-{clean_nip[6:8]}-{clean_nip[8:10]}"
        return nip

    def _calculate_nip_validation_score(self, nip: str, text: str) -> float:
        """Calculate validation score for NIP based on context and format"""
        score = 0.5
        
        # Checksum validation
        if self._validate_nip_enhanced(nip):
            score += 0.4
        
        # Context validation
        nip_pos = text.lower().find(nip.replace('-', '').replace(' ', ''))
        if nip_pos != -1:
            context = text[max(0, nip_pos-30):nip_pos+30].lower()
            if any(term in context for term in ['nip', 'vat', 'podatek']):
                score += 0.1
        
        return min(1.0, score)

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
        
        # Validate NIP format with enhanced validation
        for nip_field in ['supplier_nip', 'buyer_nip']:
            nip = extracted_data.get(nip_field)
            if nip and not self._validate_nip_enhanced(nip):
                validation_results['validation_warnings'].append(f"Invalid NIP format: {nip}")
                # Also check with basic validation for backward compatibility
                if not self._validate_nip(nip):
                    validation_results['validation_errors'].append(f"NIP checksum validation failed: {nip}")
                    validation_results['is_valid_polish_invoice'] = False
        
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

    def get_enhanced_training_data_sample(self) -> Dict[str, Any]:
        """
        Generate enhanced sample training data for custom model training with ML features
        """
        return {
            'enhanced_patterns': self.polish_patterns,
            'entity_patterns': self.entity_patterns,
            'layout_patterns': self.layout_patterns,
            'sample_invoices': [
                {
                    'text': 'Faktura VAT Nr FV/001/2024\nData wystawienia: 15.01.2024\nSprzedawca: ACME Sp. z o.o.\nul. Testowa 123, 00-001 Warszawa\nNIP: 123-456-78-90\nREGON: 123456789\nNabywca: Klient Sp. j.\nul. Przykładowa 456, 00-002 Kraków\nNIP: 987-654-32-10\nWartość netto: 1000,00 zł\nVAT 23%: 230,00 zł\nDo zapłaty: 1230,00 zł',
                    'expected_extraction': {
                        'invoice_number': 'FV/001/2024',
                        'invoice_date': '2024-01-15',
                        'supplier_name': 'ACME Sp. z o.o.',
                        'supplier_nip': '1234567890',
                        'supplier_nip_formatted': '123-456-78-90',
                        'supplier_regon': '123456789',
                        'buyer_name': 'Klient Sp. j.',
                        'buyer_nip': '9876543210',
                        'net_amount': '1000.00',
                        'vat_amount': '230.00',
                        'total_amount': '1230.00',
                        'currency': 'PLN',
                        'detected_layout': 'standard'
                    }
                },
                {
                    'text': 'Faktura Pro Forma Nr PF/002/2024\nSprzedawca: XYZ S.A.\nNIP: 555-666-77-88\nNabywca: ABC PPHU\nRazem: 2460,00 PLN',
                    'expected_extraction': {
                        'invoice_number': 'PF/002/2024',
                        'supplier_name': 'XYZ S.A.',
                        'supplier_nip': '5556667788',
                        'buyer_name': 'ABC PPHU',
                        'total_amount': '2460.00',
                        'currency': 'PLN',
                        'detected_layout': 'proforma'
                    }
                }
            ],
            'enhanced_validation_rules': [
                'NIP must be 10 digits with valid checksum algorithm',
                'Total amount = Net amount + VAT amount (within 0.01 tolerance)',
                'Invoice number must follow Polish format patterns',
                'Date must be in DD.MM.YYYY, YYYY-MM-DD, or Polish month name format',
                'Company names must include Polish business entity types',
                'VAT rates must be valid Polish rates (0%, 5%, 8%, 23%)',
                'REGON must be 9 or 14 digits',
                'Bank accounts must follow Polish IBAN format (PL + 26 digits)',
                'Layout detection must match document structure',
                'ML entity confidence must be above 0.6 threshold'
            ],
            'confidence_calculation_factors': {
                'polish_terms': 8.0,
                'pattern_matching': 12.0,
                'layout_detection': 5.0,
                'data_validation': 10.0,
                'ml_consistency': 8.0,
                'cross_validation': 7.0,
                'maximum_boost': 50.0
            }
        }

    def get_training_data_sample(self) -> Dict[str, Any]:
        """
        Generate sample training data for custom model training (backward compatibility)
        """
        enhanced_data = self.get_enhanced_training_data_sample()
        
        # Return simplified version for backward compatibility
        return {
            'patterns': enhanced_data['enhanced_patterns'],
            'sample_invoices': [
                {
                    'text': invoice['text'],
                    'expected_extraction': {
                        k: v for k, v in invoice['expected_extraction'].items()
                        if k in ['invoice_number', 'supplier_name', 'supplier_nip', 
                                'buyer_name', 'total_amount', 'currency']
                    }
                }
                for invoice in enhanced_data['sample_invoices']
            ],
            'validation_rules': [
                'NIP must be 10 digits with valid checksum',
                'Total amount = Net amount + VAT amount',
                'Invoice number must follow Polish format',
                'Date must be in DD.MM.YYYY or YYYY-MM-DD format'
            ]
        }
