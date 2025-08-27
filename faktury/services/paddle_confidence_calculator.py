#!/usr/bin/env python3
"""
PaddleOCR Confidence Calculator
Advanced confidence scoring algorithms for Polish invoice processing
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceMetrics:
    """Confidence metrics for OCR results"""
    overall_confidence: float
    field_confidence: Dict[str, float]
    spatial_confidence: float
    polish_context_confidence: float
    validation_confidence: float
    processing_confidence: float

class PaddleConfidenceCalculator:
    """
    Advanced confidence calculator for PaddleOCR results
    Provides sophisticated confidence scoring for Polish invoice processing
    """
    
    def __init__(self):
        """Initialize confidence calculator with Polish-specific weights"""
        
        # Field importance weights for Polish invoices
        self.field_weights = {
            'numer_faktury': 0.15,
            'data_wystawienia': 0.12,
            'sprzedawca_nip': 0.14,
            'nabywca_nip': 0.14,
            'suma_brutto': 0.13,
            'suma_netto': 0.10,
            'suma_vat': 0.10,
            'sprzedawca_nazwa': 0.08,
            'nabywca_nazwa': 0.08,
            'pozycje': 0.06
        }
        
        # Polish context validation weights
        self.polish_context_weights = {
            'nip_validation': 0.25,
            'date_format': 0.20,
            'currency_format': 0.20,
            'vat_rate': 0.15,
            'company_type': 0.10,
            'address_format': 0.10
        }
        
        # Spatial analysis weights
        self.spatial_weights = {
            'text_alignment': 0.30,
            'field_positioning': 0.25,
            'layout_consistency': 0.25,
            'document_structure': 0.20
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 0.85,
            'medium': 0.70,
            'low': 0.50,
            'critical': 0.30
        }
        
        # Polish-specific confidence boosters
        self.polish_boosters = {
            'valid_nip': 0.15,
            'polish_date_format': 0.10,
            'polish_currency': 0.08,
            'polish_vat_rate': 0.08,
            'polish_company_type': 0.05
        }
    
    def calculate_overall_confidence(self, ocr_results: List[Dict], extracted_data: Dict) -> float:
        """
        Calculate overall confidence score for OCR results
        
        Args:
            ocr_results: Raw OCR results from PaddleOCR
            extracted_data: Extracted structured data
            
        Returns:
            Overall confidence score (0.0 - 1.0)
        """
        try:
            # Calculate individual confidence components
            field_confidence = self.calculate_field_confidence(extracted_data)
            spatial_confidence = self.analyze_spatial_consistency(ocr_results)
            polish_context_confidence = self.validate_polish_context(extracted_data)
            processing_confidence = self.calculate_processing_confidence(ocr_results)
            
            # Weighted combination
            overall_confidence = (
                field_confidence * 0.40 +
                spatial_confidence * 0.25 +
                polish_context_confidence * 0.20 +
                processing_confidence * 0.15
            )
            
            # Apply Polish-specific boosts
            overall_confidence = self.apply_polish_boosts(overall_confidence, extracted_data)
            
            # Ensure confidence is within bounds
            overall_confidence = max(0.0, min(1.0, overall_confidence))
            
            logger.info(f"Overall confidence calculated: {overall_confidence:.3f}")
            return overall_confidence
            
        except Exception as e:
            logger.error(f"Error calculating overall confidence: {e}")
            return 0.0
    
    def calculate_field_confidence(self, extracted_data: Dict) -> float:
        """
        Calculate field-level confidence scores
        
        Args:
            extracted_data: Extracted structured data
            
        Returns:
            Weighted field confidence score
        """
        try:
            total_weighted_confidence = 0.0
            total_weight = 0.0
            
            for field_name, weight in self.field_weights.items():
                field_value = extracted_data.get(field_name, '')
                
                if isinstance(field_value, dict) and 'confidence' in field_value:
                    # Handle ExtractedField objects
                    confidence = field_value['confidence']
                elif hasattr(field_value, 'confidence'):
                    # Handle ExtractedField dataclass
                    confidence = field_value.confidence
                else:
                    # Simple field confidence calculation
                    confidence = self.calculate_simple_field_confidence(field_value, field_name)
                
                total_weighted_confidence += confidence * weight
                total_weight += weight
            
            field_confidence = total_weighted_confidence / total_weight if total_weight > 0 else 0.0
            
            logger.debug(f"Field confidence calculated: {field_confidence:.3f}")
            return field_confidence
            
        except Exception as e:
            logger.error(f"Error calculating field confidence: {e}")
            return 0.0
    
    def calculate_simple_field_confidence(self, field_value: Any, field_name: str) -> float:
        """
        Calculate confidence for simple field values
        
        Args:
            field_value: Field value
            field_name: Name of the field
            
        Returns:
            Confidence score for the field
        """
        if not field_value:
            return 0.0
        
        # Base confidence based on field type
        base_confidence = 0.5
        
        # NIP validation
        if 'nip' in field_name.lower():
            if self.validate_nip_format(field_value):
                base_confidence += 0.3
            if self.validate_nip_checksum(field_value):
                base_confidence += 0.2
        
        # Date validation
        elif 'data' in field_name.lower() or 'date' in field_name.lower():
            if self.validate_polish_date(field_value):
                base_confidence += 0.4
        
        # Amount validation
        elif any(keyword in field_name.lower() for keyword in ['suma', 'amount', 'kwota']):
            if self.validate_currency_amount(field_value):
                base_confidence += 0.3
        
        # Invoice number validation
        elif 'numer' in field_name.lower() or 'invoice' in field_name.lower():
            if self.validate_invoice_number(field_value):
                base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def analyze_spatial_consistency(self, ocr_results: List[Dict]) -> float:
        """
        Analyze spatial layout consistency
        
        Args:
            ocr_results: Raw OCR results with bounding boxes
            
        Returns:
            Spatial confidence score
        """
        try:
            if not ocr_results or not ocr_results[0]:
                return 0.0
            
            # Extract text positions
            text_positions = []
            for result in ocr_results:
                for line in result:
                    if len(line) >= 2:
                        bbox = line[0]
                        center_x = sum(point[0] for point in bbox) / len(bbox)
                        center_y = sum(point[1] for point in bbox) / len(bbox)
                        text_positions.append((center_x, center_y))
            
            if not text_positions:
                return 0.0
            
            # Calculate spatial metrics
            x_positions = [pos[0] for pos in text_positions]
            y_positions = [pos[1] for pos in text_positions]
            
            # Text alignment score
            left_aligned_ratio = sum(1 for x in x_positions if x < 0.3) / len(x_positions)
            
            # Layout consistency score
            y_spacing_std = np.std(y_positions) if len(y_positions) > 1 else 0
            layout_consistency = max(0, 1 - y_spacing_std)
            
            # Document structure score
            structure_score = self.analyze_document_structure(text_positions)
            
            # Weighted spatial confidence
            spatial_confidence = (
                left_aligned_ratio * self.spatial_weights['text_alignment'] +
                layout_consistency * self.spatial_weights['layout_consistency'] +
                structure_score * self.spatial_weights['document_structure']
            )
            
            logger.debug(f"Spatial confidence calculated: {spatial_confidence:.3f}")
            return spatial_confidence
            
        except Exception as e:
            logger.error(f"Error analyzing spatial consistency: {e}")
            return 0.0
    
    def validate_polish_context(self, extracted_data: Dict) -> float:
        """
        Validate Polish-specific context and patterns
        
        Args:
            extracted_data: Extracted structured data
            
        Returns:
            Polish context confidence score
        """
        try:
            context_scores = {}
            
            # NIP validation
            seller_nip = extracted_data.get('sprzedawca_nip', '')
            buyer_nip = extracted_data.get('nabywca_nip', '')
            
            nip_score = 0.0
            if seller_nip and self.validate_nip_checksum(seller_nip):
                nip_score += 0.5
            if buyer_nip and self.validate_nip_checksum(buyer_nip):
                nip_score += 0.5
            context_scores['nip_validation'] = nip_score
            
            # Date format validation
            issue_date = extracted_data.get('data_wystawienia', '')
            date_score = 1.0 if self.validate_polish_date(issue_date) else 0.0
            context_scores['date_format'] = date_score
            
            # Currency format validation
            total_gross = extracted_data.get('suma_brutto', '')
            currency_score = 1.0 if self.validate_currency_amount(total_gross) else 0.0
            context_scores['currency_format'] = currency_score
            
            # VAT rate validation
            vat_score = self.validate_polish_vat_rates(extracted_data)
            context_scores['vat_rate'] = vat_score
            
            # Company type validation
            company_score = self.validate_polish_company_types(extracted_data)
            context_scores['company_type'] = company_score
            
            # Address format validation
            address_score = self.validate_polish_address_format(extracted_data)
            context_scores['address_format'] = address_score
            
            # Calculate weighted Polish context confidence
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for context_type, score in context_scores.items():
                weight = self.polish_context_weights.get(context_type, 0.0)
                total_weighted_score += score * weight
                total_weight += weight
            
            polish_context_confidence = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            logger.debug(f"Polish context confidence calculated: {polish_context_confidence:.3f}")
            return polish_context_confidence
            
        except Exception as e:
            logger.error(f"Error validating Polish context: {e}")
            return 0.0
    
    def calculate_processing_confidence(self, ocr_results: List[Dict]) -> float:
        """
        Calculate confidence based on processing quality
        
        Args:
            ocr_results: Raw OCR results
            
        Returns:
            Processing confidence score
        """
        try:
            if not ocr_results or not ocr_results[0]:
                return 0.0
            
            # Calculate average OCR confidence
            total_confidence = 0.0
            total_texts = 0
            
            for result in ocr_results:
                for line in result:
                    if len(line) >= 2:
                        confidence = line[1][1] if isinstance(line[1], (list, tuple)) else 0.0
                        total_confidence += confidence
                        total_texts += 1
            
            avg_confidence = total_confidence / total_texts if total_texts > 0 else 0.0
            
            # Text density score (more text = better processing)
            text_density = min(len(ocr_results[0]) / 50.0, 1.0) if ocr_results[0] else 0.0
            
            # Processing confidence combines OCR confidence and text density
            processing_confidence = (avg_confidence * 0.7 + text_density * 0.3)
            
            logger.debug(f"Processing confidence calculated: {processing_confidence:.3f}")
            return processing_confidence
            
        except Exception as e:
            logger.error(f"Error calculating processing confidence: {e}")
            return 0.0
    
    def apply_polish_boosts(self, base_confidence: float, extracted_data: Dict) -> float:
        """
        Apply Polish-specific confidence boosts
        
        Args:
            base_confidence: Base confidence score
            extracted_data: Extracted structured data
            
        Returns:
            Boosted confidence score
        """
        try:
            total_boost = 0.0
            
            # NIP validation boost
            seller_nip = extracted_data.get('sprzedawca_nip', '')
            buyer_nip = extracted_data.get('nabywca_nip', '')
            
            if seller_nip and self.validate_nip_checksum(seller_nip):
                total_boost += self.polish_boosters['valid_nip']
            if buyer_nip and self.validate_nip_checksum(buyer_nip):
                total_boost += self.polish_boosters['valid_nip']
            
            # Polish date format boost
            issue_date = extracted_data.get('data_wystawienia', '')
            if self.validate_polish_date(issue_date):
                total_boost += self.polish_boosters['polish_date_format']
            
            # Polish currency boost
            total_gross = extracted_data.get('suma_brutto', '')
            if self.validate_currency_amount(total_gross):
                total_boost += self.polish_boosters['polish_currency']
            
            # Polish VAT rate boost
            if self.validate_polish_vat_rates(extracted_data) > 0.5:
                total_boost += self.polish_boosters['polish_vat_rate']
            
            # Polish company type boost
            if self.validate_polish_company_types(extracted_data) > 0.5:
                total_boost += self.polish_boosters['polish_company_type']
            
            # Apply boost (capped at 0.3 to avoid over-inflation)
            boosted_confidence = base_confidence + min(total_boost, 0.3)
            
            return min(boosted_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error applying Polish boosts: {e}")
            return base_confidence
    
    def validate_nip_format(self, nip: str) -> bool:
        """Validate NIP format"""
        if not nip:
            return False
        
        nip_clean = ''.join(filter(str.isdigit, str(nip)))
        return len(nip_clean) == 10
    
    def validate_nip_checksum(self, nip: str) -> bool:
        """Validate NIP checksum"""
        try:
            nip_clean = ''.join(filter(str.isdigit, str(nip)))
            
            if len(nip_clean) != 10:
                return False
            
            weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
            checksum = 0
            
            for i in range(9):
                checksum += int(nip_clean[i]) * weights[i]
            
            checksum = checksum % 11
            if checksum == 10:
                checksum = 0
            
            return checksum == int(nip_clean[9])
            
        except Exception:
            return False
    
    def validate_polish_date(self, date_str: str) -> bool:
        """Validate Polish date format"""
        if not date_str:
            return False
        
        import re
        from datetime import datetime
        
        # Polish date patterns
        patterns = [
            r'\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4}',
            r'\d{4}[\.\-]\d{1,2}[\.\-]\d{1,2}'
        ]
        
        for pattern in patterns:
            if re.match(pattern, str(date_str)):
                try:
                    if '.' in str(date_str):
                        if len(str(date_str).split('.')[0]) == 4:
                            datetime.strptime(str(date_str), '%Y.%m.%d')
                        else:
                            datetime.strptime(str(date_str), '%d.%m.%Y')
                    elif '-' in str(date_str):
                        if len(str(date_str).split('-')[0]) == 4:
                            datetime.strptime(str(date_str), '%Y-%m-%d')
                        else:
                            datetime.strptime(str(date_str), '%d-%m-%Y')
                    return True
                except ValueError:
                    continue
        
        return False
    
    def validate_currency_amount(self, amount: str) -> bool:
        """Validate Polish currency amount format"""
        if not amount:
            return False
        
        import re
        
        # Polish currency patterns
        patterns = [
            r'[\d\s,]+',
            r'[\d\s,]+ zł',
            r'[\d\s,]+ PLN'
        ]
        
        for pattern in patterns:
            if re.match(pattern, str(amount), re.IGNORECASE):
                return True
        
        return False
    
    def validate_invoice_number(self, invoice_num: str) -> bool:
        """Validate invoice number format"""
        if not invoice_num:
            return False
        
        # Basic validation - should contain alphanumeric characters
        return len(str(invoice_num).strip()) > 0
    
    def validate_polish_vat_rates(self, extracted_data: Dict) -> float:
        """Validate Polish VAT rates"""
        try:
            # Check for common Polish VAT rates
            vat_rates = [0, 5, 8, 23]
            found_valid_rates = 0
            
            # This is a simplified validation - in practice you'd extract VAT rates from the document
            return 0.5  # Default score
            
        except Exception:
            return 0.0
    
    def validate_polish_company_types(self, extracted_data: Dict) -> float:
        """Validate Polish company types"""
        try:
            # Check for Polish company type indicators
            company_types = ['Sp. z o.o.', 'S.A.', 'Spółka Akcyjna', 'Spółka z ograniczoną odpowiedzialnością']
            
            seller_name = extracted_data.get('sprzedawca_nazwa', '')
            buyer_name = extracted_data.get('nabywca_nazwa', '')
            
            found_types = 0
            for company_type in company_types:
                if company_type.lower() in str(seller_name).lower():
                    found_types += 1
                if company_type.lower() in str(buyer_name).lower():
                    found_types += 1
            
            return min(found_types / 2.0, 1.0)
            
        except Exception:
            return 0.0
    
    def validate_polish_address_format(self, extracted_data: Dict) -> float:
        """Validate Polish address format"""
        try:
            # Simplified address validation
            return 0.5  # Default score
            
        except Exception:
            return 0.0
    
    def analyze_document_structure(self, text_positions: List[Tuple[float, float]]) -> float:
        """Analyze document structure based on text positions"""
        try:
            if not text_positions:
                return 0.0
            
            # Calculate structure metrics
            y_positions = [pos[1] for pos in text_positions]
            
            # Check for logical document flow (top to bottom)
            sorted_y = sorted(y_positions)
            structure_consistency = 1.0 - abs(np.corrcoef(range(len(sorted_y)), sorted_y)[0, 1])
            
            return max(0.0, structure_consistency)
            
        except Exception:
            return 0.0
    
    def get_confidence_level(self, confidence_score: float) -> str:
        """
        Get confidence level description
        
        Args:
            confidence_score: Confidence score (0.0 - 1.0)
            
        Returns:
            Confidence level description
        """
        if confidence_score >= self.confidence_thresholds['high']:
            return 'high'
        elif confidence_score >= self.confidence_thresholds['medium']:
            return 'medium'
        elif confidence_score >= self.confidence_thresholds['low']:
            return 'low'
        else:
            return 'critical'
    
    def get_detailed_confidence_metrics(self, ocr_results: List[Dict], extracted_data: Dict) -> ConfidenceMetrics:
        """
        Get detailed confidence metrics
        
        Args:
            ocr_results: Raw OCR results
            extracted_data: Extracted structured data
            
        Returns:
            Detailed confidence metrics
        """
        try:
            field_confidence = self.calculate_field_confidence(extracted_data)
            spatial_confidence = self.analyze_spatial_consistency(ocr_results)
            polish_context_confidence = self.validate_polish_context(extracted_data)
            processing_confidence = self.calculate_processing_confidence(ocr_results)
            
            overall_confidence = self.calculate_overall_confidence(ocr_results, extracted_data)
            
            # Calculate individual field confidences
            field_confidences = {}
            for field_name in self.field_weights.keys():
                field_value = extracted_data.get(field_name, '')
                field_confidences[field_name] = self.calculate_simple_field_confidence(field_value, field_name)
            
            return ConfidenceMetrics(
                overall_confidence=overall_confidence,
                field_confidence=field_confidences,
                spatial_confidence=spatial_confidence,
                polish_context_confidence=polish_context_confidence,
                validation_confidence=polish_context_confidence,
                processing_confidence=processing_confidence
            )
            
        except Exception as e:
            logger.error(f"Error getting detailed confidence metrics: {e}")
            return ConfidenceMetrics(
                overall_confidence=0.0,
                field_confidence={},
                spatial_confidence=0.0,
                polish_context_confidence=0.0,
                validation_confidence=0.0,
                processing_confidence=0.0
            )