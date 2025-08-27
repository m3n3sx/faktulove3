"""
Confidence Calculation System for OCR Processing

This service provides comprehensive confidence scoring for OCR results by combining
multiple confidence sources with weighted algorithms, pattern matching validation,
business rule validation, and Polish language-specific boost factors.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class ConfidenceSource(Enum):
    """Sources of confidence information"""
    OCR_ENGINE = "ocr_engine"
    PATTERN_MATCHING = "pattern_matching"
    DATA_VALIDATION = "data_validation"
    POLISH_LANGUAGE = "polish_language"
    CROSS_VALIDATION = "cross_validation"
    BUSINESS_RULES = "business_rules"


@dataclass
class ConfidenceComponent:
    """Individual confidence component"""
    source: ConfidenceSource
    score: float
    weight: float
    details: Dict[str, Any] = field(default_factory=dict)
    field_name: Optional[str] = None


@dataclass
class FieldConfidence:
    """Confidence information for a specific field"""
    field_name: str
    value: Any
    base_confidence: float
    components: List[ConfidenceComponent] = field(default_factory=list)
    final_confidence: float = 0.0
    validation_results: Dict[str, Any] = field(default_factory=dict)


class ConfidenceCalculator:
    """
    Advanced confidence calculation system for OCR results
    
    This service implements weighted scoring algorithms, OCR engine confidence
    aggregation, pattern matching confidence, data validation confidence using
    business rules, and Polish language boost factors for recognized patterns.
    """
    
    def __init__(self):
        self.confidence_weights = self._initialize_confidence_weights()
        self.polish_patterns = self._initialize_polish_patterns()
        self.business_rules = self._initialize_business_rules()
        self.field_importance = self._initialize_field_importance()
        
        # Performance tracking
        self.calculation_stats = {
            'total_calculations': 0,
            'average_confidence': 0.0,
            'source_performance': {},
            'field_performance': {}
        }
    
    def calculate_overall_confidence(self, 
                                   extracted_data: Dict[str, Any], 
                                   ocr_confidence: Dict[str, Any],
                                   raw_text: str = "",
                                   engine_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive confidence score for OCR extraction results
        
        Args:
            extracted_data: Extracted invoice data
            ocr_confidence: OCR engine confidence information
            raw_text: Original OCR text for pattern analysis
            engine_results: Results from multiple OCR engines
            
        Returns:
            Dictionary containing detailed confidence analysis
        """
        try:
            logger.info("Starting comprehensive confidence calculation")
            
            # Initialize confidence result
            confidence_result = {
                'overall_confidence': 0.0,
                'field_confidences': {},
                'confidence_components': [],
                'validation_results': {},
                'polish_boost_applied': 0.0,
                'calculation_metadata': {
                    'total_fields_analyzed': 0,
                    'high_confidence_fields': 0,
                    'low_confidence_fields': 0,
                    'validation_failures': 0,
                    'boost_factors_applied': []
                }
            }
            
            # Calculate field-level confidences
            field_confidences = self._calculate_field_confidences(
                extracted_data, ocr_confidence, raw_text, engine_results
            )
            confidence_result['field_confidences'] = {
                field.field_name: {
                    'confidence': field.final_confidence,
                    'components': [
                        {
                            'source': comp.source.value,
                            'score': comp.score,
                            'weight': comp.weight,
                            'details': comp.details
                        } for comp in field.components
                    ],
                    'validation_results': field.validation_results
                } for field in field_confidences
            }
            
            # Aggregate OCR engine confidences
            engine_confidence = self._aggregate_engine_confidences(
                ocr_confidence, engine_results
            )
            
            # Calculate pattern matching confidence
            pattern_confidence = self._calculate_pattern_matching_confidence(
                extracted_data, raw_text
            )
            
            # Calculate data validation confidence
            validation_confidence = self._calculate_data_validation_confidence(
                extracted_data
            )
            
            # Calculate Polish language boost
            polish_boost = self._calculate_polish_language_boost(
                extracted_data, raw_text
            )
            
            # Create confidence components
            components = [
                ConfidenceComponent(
                    source=ConfidenceSource.OCR_ENGINE,
                    score=engine_confidence['score'],
                    weight=self.confidence_weights['ocr_engine'],
                    details=engine_confidence['details']
                ),
                ConfidenceComponent(
                    source=ConfidenceSource.PATTERN_MATCHING,
                    score=pattern_confidence['score'],
                    weight=self.confidence_weights['pattern_matching'],
                    details=pattern_confidence['details']
                ),
                ConfidenceComponent(
                    source=ConfidenceSource.DATA_VALIDATION,
                    score=validation_confidence['score'],
                    weight=self.confidence_weights['data_validation'],
                    details=validation_confidence['details']
                ),
                ConfidenceComponent(
                    source=ConfidenceSource.POLISH_LANGUAGE,
                    score=polish_boost['score'],
                    weight=self.confidence_weights['polish_language'],
                    details=polish_boost['details']
                )
            ]
            
            # Calculate weighted overall confidence
            overall_confidence = self._calculate_weighted_confidence(components)
            
            # Apply final adjustments and constraints
            final_confidence = self._apply_confidence_constraints(
                overall_confidence, extracted_data, field_confidences
            )
            
            # Update result
            confidence_result.update({
                'overall_confidence': final_confidence,
                'confidence_components': [
                    {
                        'source': comp.source.value,
                        'score': comp.score,
                        'weight': comp.weight,
                        'weighted_contribution': comp.score * comp.weight,
                        'details': comp.details
                    } for comp in components
                ],
                'polish_boost_applied': polish_boost['score'],
                'validation_results': validation_confidence['details']
            })
            
            # Update metadata
            self._update_calculation_metadata(
                confidence_result, field_confidences, components
            )
            
            # Update performance statistics
            self._update_calculation_stats(confidence_result)
            
            logger.info(f"Confidence calculation completed: {final_confidence:.1f}%")
            return confidence_result
            
        except Exception as e:
            logger.error(f"Error in confidence calculation: {e}", exc_info=True)
            return {
                'overall_confidence': 0.0,
                'field_confidences': {},
                'confidence_components': [],
                'calculation_error': str(e)
            }
    
    def _initialize_confidence_weights(self) -> Dict[str, float]:
        """Initialize weights for different confidence sources"""
        return {
            'ocr_engine': 0.35,        # OCR engine confidence
            'pattern_matching': 0.25,   # Pattern recognition confidence
            'data_validation': 0.25,    # Business rule validation
            'polish_language': 0.15,    # Polish language boost
            'cross_validation': 0.10    # Cross-validation between methods
        }
    
    def _initialize_polish_patterns(self) -> Dict[str, List[str]]:
        """Initialize Polish-specific patterns for confidence boosting"""
        return {
            'polish_company_indicators': [
                r'Sp\.?\s*z\s*o\.?o\.?',
                r'S\.?A\.?',
                r'Spółka\s*Akcyjna',
                r'P\.?P\.?H\.?U?\.?',
                r'Firma\s+(?:Handlowa|Usługowa)',
                r'Przedsiębiorstwo'
            ],
            'polish_vat_patterns': [
                r'NIP[-:\s]*\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}',
                r'VAT[-:\s]*\d{10}',
                r'PL\s*\d{10}'
            ],
            'polish_currency_patterns': [
                r'\d+(?:\s?\d{3})*[,.]?\d*\s*zł',
                r'\d+(?:\s?\d{3})*[,.]?\d*\s*PLN',
                r'złotych?',
                r'grosze?'
            ],
            'polish_date_patterns': [
                r'\d{1,2}\s+(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+\d{4}',
                r'\d{2}[.-]\d{2}[.-]\d{4}'
            ],
            'polish_invoice_terms': [
                r'faktura\s*VAT',
                r'faktura\s*korygująca',
                r'pro\s*forma',
                r'rachunek',
                r'paragon'
            ],
            'polish_business_terms': [
                r'sprzedawca',
                r'nabywca',
                r'usługodawca',
                r'zamawiający',
                r'wykonawca'
            ]
        }
    
    def _initialize_business_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business validation rules"""
        return {
            'nip_validation': {
                'length': 10,
                'checksum_weights': [6, 5, 7, 2, 3, 4, 5, 6, 7],
                'confidence_boost': 15.0
            },
            'amount_validation': {
                'min_value': 0.01,
                'max_value': 10000000.00,
                'reasonable_range': (1.0, 100000.0),
                'confidence_boost': 10.0
            },
            'date_validation': {
                'min_year': 1990,
                'max_year': datetime.now().year + 2,
                'reasonable_range_years': 5,
                'confidence_boost': 12.0
            },
            'invoice_number_validation': {
                'min_length': 3,
                'max_length': 50,
                'pattern': r'^[A-Z0-9/\-]+$',
                'confidence_boost': 8.0
            },
            'company_name_validation': {
                'min_length': 3,
                'max_length': 200,
                'polish_entity_boost': 20.0
            }
        }
    
    def _initialize_field_importance(self) -> Dict[str, float]:
        """Initialize importance weights for different fields"""
        return {
            'numer_faktury': 1.0,
            'invoice_date': 0.9,
            'total_amount': 0.95,
            'supplier_nip': 0.85,
            'buyer_nip': 0.8,
            'supplier_name': 0.75,
            'buyer_name': 0.7,
            'line_items': 0.6,
            'vat_rates': 0.5,
            'bank_account': 0.4
        }
    
    def _calculate_field_confidences(self, 
                                   extracted_data: Dict[str, Any],
                                   ocr_confidence: Dict[str, Any],
                                   raw_text: str,
                                   engine_results: List[Dict[str, Any]] = None) -> List[FieldConfidence]:
        """Calculate confidence for individual fields"""
        field_confidences = []
        
        # Get field confidence data from OCR
        field_confidence_data = ocr_confidence.get('field_confidence', {})
        
        for field_name, field_value in extracted_data.items():
            # Handle ExtractedField objects from invoice field extractor
            if hasattr(field_value, 'value'):
                actual_value = field_value.value
                base_confidence = getattr(field_value, 'confidence', 50.0)
            else:
                actual_value = field_value
                base_confidence = field_confidence_data.get(field_name, 50.0)
            
            if actual_value is None or actual_value == "":
                continue
            
            # Create field confidence object
            field_conf = FieldConfidence(
                field_name=field_name,
                value=actual_value,
                base_confidence=base_confidence
            )
            
            # Add OCR engine confidence component
            ocr_score = base_confidence
            field_conf.components.append(ConfidenceComponent(
                source=ConfidenceSource.OCR_ENGINE,
                score=ocr_score,
                weight=0.4,
                field_name=field_name,
                details={'raw_ocr_confidence': ocr_score}
            ))
            
            # Add pattern matching confidence
            pattern_score = self._calculate_field_pattern_confidence(
                field_name, actual_value, raw_text
            )
            field_conf.components.append(ConfidenceComponent(
                source=ConfidenceSource.PATTERN_MATCHING,
                score=pattern_score,
                weight=0.3,
                field_name=field_name,
                details={'pattern_matches': pattern_score > 70.0}
            ))
            
            # Add validation confidence
            validation_score, validation_details = self._validate_field_value(
                field_name, actual_value
            )
            field_conf.components.append(ConfidenceComponent(
                source=ConfidenceSource.DATA_VALIDATION,
                score=validation_score,
                weight=0.2,
                field_name=field_name,
                details=validation_details
            ))
            
            # Add Polish language boost
            polish_score = self._calculate_field_polish_boost(
                field_name, actual_value, raw_text
            )
            field_conf.components.append(ConfidenceComponent(
                source=ConfidenceSource.POLISH_LANGUAGE,
                score=polish_score,
                weight=0.1,
                field_name=field_name,
                details={'polish_patterns_found': polish_score > 0}
            ))
            
            # Calculate final field confidence
            field_conf.final_confidence = self._calculate_weighted_confidence(
                field_conf.components
            )
            
            field_conf.validation_results = validation_details
            field_confidences.append(field_conf)
        
        return field_confidences
    
    def _aggregate_engine_confidences(self, 
                                    ocr_confidence: Dict[str, Any],
                                    engine_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Aggregate confidence scores from multiple OCR engines"""
        try:
            engine_scores = []
            engine_details = {}
            
            # Get primary OCR confidence
            primary_confidence = ocr_confidence.get('confidence_score', 0.0)
            if primary_confidence > 0:
                engine_scores.append(primary_confidence)
                engine_details['primary_engine'] = primary_confidence
            
            # Get additional engine results if available
            if engine_results:
                for i, result in enumerate(engine_results):
                    engine_conf = result.get('confidence_score', 0.0)
                    if engine_conf > 0:
                        engine_scores.append(engine_conf)
                        engine_name = result.get('engine_name', f'engine_{i}')
                        engine_details[engine_name] = engine_conf
            
            if not engine_scores:
                return {'score': 0.0, 'details': {'error': 'No engine confidence available'}}
            
            # Calculate aggregated confidence using weighted average
            if len(engine_scores) == 1:
                aggregated_score = engine_scores[0]
            else:
                # Use harmonic mean for conservative estimate when multiple engines
                harmonic_mean = len(engine_scores) / sum(1/score for score in engine_scores if score > 0)
                # Boost slightly for consensus
                consensus_boost = min(10.0, len(engine_scores) * 2.0)
                aggregated_score = min(100.0, harmonic_mean + consensus_boost)
            
            return {
                'score': aggregated_score,
                'details': {
                    'engine_scores': engine_details,
                    'aggregation_method': 'harmonic_mean_with_consensus_boost',
                    'engines_count': len(engine_scores),
                    'score_variance': statistics.variance(engine_scores) if len(engine_scores) > 1 else 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"Error aggregating engine confidences: {e}")
            return {'score': 0.0, 'details': {'error': str(e)}}
    
    def _calculate_pattern_matching_confidence(self, 
                                             extracted_data: Dict[str, Any],
                                             raw_text: str) -> Dict[str, Any]:
        """Calculate confidence based on successful pattern extractions"""
        try:
            pattern_scores = []
            pattern_details = {}
            
            # Check invoice number patterns
            if 'numer_faktury' in extracted_data:
                invoice_score = self._validate_invoice_number_pattern(
                    extracted_data['numer_faktury'], raw_text
                )
                pattern_scores.append(invoice_score)
                pattern_details['invoice_number_pattern'] = invoice_score
            
            # Check date patterns
            date_fields = [k for k in extracted_data.keys() if 'date' in k.lower()]
            if date_fields:
                date_score = self._validate_date_patterns(extracted_data, raw_text)
                pattern_scores.append(date_score)
                pattern_details['date_patterns'] = date_score
            
            # Check amount patterns
            amount_fields = [k for k in extracted_data.keys() if 'amount' in k.lower()]
            if amount_fields:
                amount_score = self._validate_amount_patterns(extracted_data, raw_text)
                pattern_scores.append(amount_score)
                pattern_details['amount_patterns'] = amount_score
            
            # Check NIP patterns
            nip_fields = [k for k in extracted_data.keys() if 'nip' in k.lower()]
            if nip_fields:
                nip_score = self._validate_nip_patterns(extracted_data, raw_text)
                pattern_scores.append(nip_score)
                pattern_details['nip_patterns'] = nip_score
            
            # Check company name patterns
            company_fields = [k for k in extracted_data.keys() if 'name' in k.lower()]
            if company_fields:
                company_score = self._validate_company_patterns(extracted_data, raw_text)
                pattern_scores.append(company_score)
                pattern_details['company_patterns'] = company_score
            
            # Calculate overall pattern confidence
            if pattern_scores:
                overall_score = sum(pattern_scores) / len(pattern_scores)
            else:
                overall_score = 0.0
            
            return {
                'score': overall_score,
                'details': {
                    'pattern_scores': pattern_details,
                    'patterns_validated': len(pattern_scores),
                    'average_pattern_score': overall_score
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating pattern matching confidence: {e}")
            return {'score': 0.0, 'details': {'error': str(e)}}
    
    def _calculate_data_validation_confidence(self, 
                                            extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence using business rules validation"""
        try:
            validation_scores = []
            validation_details = {}
            
            # Validate NIP numbers
            nip_fields = [k for k in extracted_data.keys() if 'nip' in k.lower()]
            for field in nip_fields:
                field_value = extracted_data[field]
                if field_value:
                    # Handle ExtractedField objects
                    if hasattr(field_value, 'value'):
                        field_value = field_value.value
                    is_valid, score = self._validate_nip_business_rules(str(field_value) if field_value else "")
                    validation_scores.append(score)
                    validation_details[f'{field}_validation'] = {
                        'is_valid': is_valid,
                        'score': score
                    }
            
            # Validate amounts
            amount_fields = [k for k in extracted_data.keys() if 'amount' in k.lower()]
            for field in amount_fields:
                field_value = extracted_data[field]
                if field_value:
                    # Handle ExtractedField objects
                    if hasattr(field_value, 'value'):
                        field_value = field_value.value
                    is_valid, score = self._validate_amount_business_rules(field_value)
                    validation_scores.append(score)
                    validation_details[f'{field}_validation'] = {
                        'is_valid': is_valid,
                        'score': score
                    }
            
            # Validate dates
            date_fields = [k for k in extracted_data.keys() if 'date' in k.lower()]
            for field in date_fields:
                field_value = extracted_data[field]
                if field_value:
                    # Handle ExtractedField objects
                    if hasattr(field_value, 'value'):
                        field_value = field_value.value
                    is_valid, score = self._validate_date_business_rules(str(field_value) if field_value else "")
                    validation_scores.append(score)
                    validation_details[f'{field}_validation'] = {
                        'is_valid': is_valid,
                        'score': score
                    }
            
            # Validate invoice numbers
            if 'numer_faktury' in extracted_data and extracted_data['numer_faktury']:
                field_value = extracted_data['numer_faktury']
                # Handle ExtractedField objects
                if hasattr(field_value, 'value'):
                    field_value = field_value.value
                is_valid, score = self._validate_invoice_number_business_rules(
                    str(field_value) if field_value else ""
                )
                validation_scores.append(score)
                validation_details['invoice_number_validation'] = {
                    'is_valid': is_valid,
                    'score': score
                }
            
            # Calculate overall validation confidence
            if validation_scores:
                overall_score = sum(validation_scores) / len(validation_scores)
            else:
                overall_score = 50.0  # Neutral score when no validations possible
            
            return {
                'score': overall_score,
                'details': {
                    'validation_results': validation_details,
                    'validations_performed': len(validation_scores),
                    'average_validation_score': overall_score,
                    'all_validations_passed': all(
                        result.get('is_valid', False) 
                        for result in validation_details.values()
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating data validation confidence: {e}")
            return {'score': 0.0, 'details': {'error': str(e)}}
    
    def _calculate_polish_language_boost(self, 
                                       extracted_data: Dict[str, Any],
                                       raw_text: str) -> Dict[str, Any]:
        """Calculate Polish language boost factors for recognized patterns"""
        try:
            boost_factors = []
            boost_details = {}
            
            # Check for Polish company indicators
            company_boost = self._check_polish_company_patterns(extracted_data, raw_text)
            if company_boost > 0:
                boost_factors.append(company_boost)
                boost_details['company_patterns'] = company_boost
            
            # Check for Polish VAT patterns
            vat_boost = self._check_polish_vat_patterns(extracted_data, raw_text)
            if vat_boost > 0:
                boost_factors.append(vat_boost)
                boost_details['vat_patterns'] = vat_boost
            
            # Check for Polish currency patterns
            currency_boost = self._check_polish_currency_patterns(extracted_data, raw_text)
            if currency_boost > 0:
                boost_factors.append(currency_boost)
                boost_details['currency_patterns'] = currency_boost
            
            # Check for Polish date patterns
            date_boost = self._check_polish_date_patterns(extracted_data, raw_text)
            if date_boost > 0:
                boost_factors.append(date_boost)
                boost_details['date_patterns'] = date_boost
            
            # Check for Polish invoice terminology
            invoice_boost = self._check_polish_invoice_terms(raw_text)
            if invoice_boost > 0:
                boost_factors.append(invoice_boost)
                boost_details['invoice_terms'] = invoice_boost
            
            # Check for Polish business terminology
            business_boost = self._check_polish_business_terms(raw_text)
            if business_boost > 0:
                boost_factors.append(business_boost)
                boost_details['business_terms'] = business_boost
            
            # Calculate overall Polish boost
            if boost_factors:
                # Use average but cap the boost to prevent over-boosting
                overall_boost = min(25.0, sum(boost_factors) / len(boost_factors))
            else:
                overall_boost = 0.0
            
            return {
                'score': overall_boost,
                'details': {
                    'boost_factors': boost_details,
                    'patterns_found': len(boost_factors),
                    'total_boost_applied': overall_boost,
                    'boost_categories': list(boost_details.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating Polish language boost: {e}")
            return {'score': 0.0, 'details': {'error': str(e)}}
    
    def _calculate_weighted_confidence(self, components: List[ConfidenceComponent]) -> float:
        """Calculate weighted confidence score from components"""
        if not components:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for component in components:
            if component.score >= 0:  # Only include valid scores
                total_weighted_score += component.score * component.weight
                total_weight += component.weight
        
        if total_weight == 0:
            return 0.0
        
        return min(100.0, max(0.0, total_weighted_score / total_weight))
    
    def _apply_confidence_constraints(self, 
                                    base_confidence: float,
                                    extracted_data: Dict[str, Any],
                                    field_confidences: List[FieldConfidence]) -> float:
        """Apply final constraints and adjustments to confidence score"""
        adjusted_confidence = base_confidence
        
        # Penalty for missing critical fields
        critical_fields = ['numer_faktury', 'total_amount']
        missing_critical = sum(1 for field in critical_fields 
                             if field not in extracted_data or not extracted_data[field])
        
        if missing_critical > 0:
            penalty = missing_critical * 15.0
            adjusted_confidence = max(0.0, adjusted_confidence - penalty)
        
        # Bonus for high field confidence consistency
        if field_confidences:
            field_scores = [fc.final_confidence for fc in field_confidences]
            if field_scores:
                min_field_confidence = min(field_scores)
                avg_field_confidence = sum(field_scores) / len(field_scores)
                
                # If all fields have reasonably high confidence, apply bonus
                if min_field_confidence > 70.0 and avg_field_confidence > 80.0:
                    consistency_bonus = min(10.0, (avg_field_confidence - 80.0) / 2.0)
                    adjusted_confidence = min(100.0, adjusted_confidence + consistency_bonus)
                
                # If there's high variance in field confidences, apply penalty
                if len(field_scores) > 1:
                    variance = statistics.variance(field_scores)
                    if variance > 400:  # High variance (std dev > 20)
                        variance_penalty = min(10.0, variance / 100.0)
                        adjusted_confidence = max(0.0, adjusted_confidence - variance_penalty)
        
        return round(adjusted_confidence, 2)
    
    # Helper methods for pattern validation
    def _validate_invoice_number_pattern(self, invoice_number: Any, raw_text: str) -> float:
        """Validate invoice number against Polish patterns"""
        if not invoice_number:
            return 0.0
        
        # Convert to string if needed
        if hasattr(invoice_number, 'value'):
            invoice_number = str(invoice_number.value)
        else:
            invoice_number = str(invoice_number)
        
        # Check if invoice number matches Polish patterns
        polish_patterns = [
            r'[A-Z]*\d+[/\-]\d+[/\-]\d+',
            r'FV[/\-]\d+[/\-]\d+',
            r'[A-Z]{2,4}[/\-]\d+[/\-]\d{2,4}'
        ]
        
        for pattern in polish_patterns:
            if re.match(pattern, invoice_number):
                # Check if pattern appears in context
                if invoice_number in raw_text:
                    return 85.0
                else:
                    return 70.0
        
        # Basic validation - has numbers and reasonable length
        if re.search(r'\d', invoice_number) and 3 <= len(invoice_number) <= 50:
            return 60.0
        
        return 30.0
    
    def _validate_date_patterns(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Validate date patterns"""
        date_fields = [k for k in extracted_data.keys() if 'date' in k.lower()]
        if not date_fields:
            return 0.0
        
        valid_dates = 0
        total_dates = len(date_fields)
        
        for field in date_fields:
            date_value = extracted_data[field]
            # Handle ExtractedField objects
            if hasattr(date_value, 'value'):
                date_value = date_value.value
            if self._is_valid_date_format(str(date_value) if date_value else ""):
                valid_dates += 1
        
        return (valid_dates / total_dates) * 100.0
    
    def _validate_amount_patterns(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Validate amount patterns"""
        amount_fields = [k for k in extracted_data.keys() if 'amount' in k.lower()]
        if not amount_fields:
            return 0.0
        
        valid_amounts = 0
        total_amounts = len(amount_fields)
        
        for field in amount_fields:
            amount_value = extracted_data[field]
            # Handle ExtractedField objects
            if hasattr(amount_value, 'value'):
                amount_value = amount_value.value
            if self._is_valid_amount(amount_value):
                valid_amounts += 1
        
        return (valid_amounts / total_amounts) * 100.0
    
    def _validate_nip_patterns(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Validate NIP patterns"""
        nip_fields = [k for k in extracted_data.keys() if 'nip' in k.lower()]
        if not nip_fields:
            return 0.0
        
        valid_nips = 0
        total_nips = len(nip_fields)
        
        for field in nip_fields:
            nip_value = extracted_data[field]
            # Handle ExtractedField objects
            if hasattr(nip_value, 'value'):
                nip_value = nip_value.value
            if self._validate_nip_checksum(str(nip_value) if nip_value else ""):
                valid_nips += 1
        
        return (valid_nips / total_nips) * 100.0
    
    def _validate_company_patterns(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Validate company name patterns"""
        company_fields = [k for k in extracted_data.keys() if 'name' in k.lower()]
        if not company_fields:
            return 0.0
        
        polish_indicators = 0
        total_companies = len(company_fields)
        
        for field in company_fields:
            company_name = extracted_data[field]
            # Handle ExtractedField objects
            if hasattr(company_name, 'value'):
                company_name = company_name.value
            if self._has_polish_company_indicators(str(company_name) if company_name else ""):
                polish_indicators += 1
        
        if polish_indicators > 0:
            return min(100.0, (polish_indicators / total_companies) * 100.0 + 20.0)
        
        return 50.0  # Neutral score for companies without clear Polish indicators
    
    # Business rule validation methods
    def _validate_nip_business_rules(self, nip: str) -> Tuple[bool, float]:
        """Validate NIP using business rules"""
        if not nip or len(nip) != 10:
            return False, 0.0
        
        if not nip.isdigit():
            return False, 0.0
        
        # Validate NIP checksum
        if self._validate_nip_checksum(nip):
            return True, 95.0
        else:
            return False, 20.0
    
    def _validate_amount_business_rules(self, amount: Union[str, float, Decimal]) -> Tuple[bool, float]:
        """Validate amount using business rules"""
        try:
            if isinstance(amount, str):
                amount = float(amount.replace(',', '.').replace(' ', ''))
            elif isinstance(amount, Decimal):
                amount = float(amount)
            
            rules = self.business_rules['amount_validation']
            
            if rules['min_value'] <= amount <= rules['max_value']:
                # Check if amount is in reasonable range
                if rules['reasonable_range'][0] <= amount <= rules['reasonable_range'][1]:
                    return True, 90.0
                else:
                    return True, 70.0  # Valid but unusual amount
            else:
                return False, 30.0
                
        except (ValueError, TypeError):
            return False, 0.0
    
    def _validate_date_business_rules(self, date_value: str) -> Tuple[bool, float]:
        """Validate date using business rules"""
        try:
            if isinstance(date_value, str):
                # Try to parse date
                date_obj = datetime.strptime(date_value, '%Y-%m-%d').date()
            else:
                return False, 0.0
            
            rules = self.business_rules['date_validation']
            current_year = datetime.now().year
            
            if rules['min_year'] <= date_obj.year <= rules['max_year']:
                # Check if date is within reasonable range
                if abs(date_obj.year - current_year) <= rules['reasonable_range_years']:
                    return True, 90.0
                else:
                    return True, 70.0  # Valid but old/future date
            else:
                return False, 30.0
                
        except (ValueError, TypeError):
            return False, 0.0
    
    def _validate_invoice_number_business_rules(self, invoice_number: str) -> Tuple[bool, float]:
        """Validate invoice number using business rules"""
        if not invoice_number:
            return False, 0.0
        
        rules = self.business_rules['invoice_number_validation']
        
        # Check length
        if not (rules['min_length'] <= len(invoice_number) <= rules['max_length']):
            return False, 30.0
        
        # Check pattern
        if re.match(rules['pattern'], invoice_number):
            return True, 85.0
        else:
            # Check if it at least contains numbers
            if re.search(r'\d', invoice_number):
                return True, 60.0
            else:
                return False, 20.0
    
    # Polish language boost helper methods
    def _check_polish_company_patterns(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Check for Polish company patterns"""
        boost = 0.0
        
        for pattern in self.polish_patterns['polish_company_indicators']:
            if re.search(pattern, raw_text, re.IGNORECASE):
                boost += 5.0
        
        return min(20.0, boost)
    
    def _check_polish_vat_patterns(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Check for Polish VAT patterns"""
        boost = 0.0
        
        for pattern in self.polish_patterns['polish_vat_patterns']:
            if re.search(pattern, raw_text, re.IGNORECASE):
                boost += 4.0
        
        return min(15.0, boost)
    
    def _check_polish_currency_patterns(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Check for Polish currency patterns"""
        boost = 0.0
        
        for pattern in self.polish_patterns['polish_currency_patterns']:
            if re.search(pattern, raw_text, re.IGNORECASE):
                boost += 3.0
        
        return min(12.0, boost)
    
    def _check_polish_date_patterns(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Check for Polish date patterns"""
        boost = 0.0
        
        for pattern in self.polish_patterns['polish_date_patterns']:
            if re.search(pattern, raw_text, re.IGNORECASE):
                boost += 3.0
        
        return min(10.0, boost)
    
    def _check_polish_invoice_terms(self, raw_text: str) -> float:
        """Check for Polish invoice terminology"""
        boost = 0.0
        
        for pattern in self.polish_patterns['polish_invoice_terms']:
            if re.search(pattern, raw_text, re.IGNORECASE):
                boost += 2.0
        
        return min(8.0, boost)
    
    def _check_polish_business_terms(self, raw_text: str) -> float:
        """Check for Polish business terminology"""
        boost = 0.0
        
        for pattern in self.polish_patterns['polish_business_terms']:
            if re.search(pattern, raw_text, re.IGNORECASE):
                boost += 2.0
        
        return min(8.0, boost)
    
    # Utility methods
    def _calculate_field_pattern_confidence(self, field_name: str, field_value: Any, raw_text: str) -> float:
        """Calculate pattern confidence for a specific field"""
        if not field_value:
            return 0.0
        
        # Field-specific pattern validation
        if 'nip' in field_name.lower():
            return 90.0 if self._validate_nip_checksum(str(field_value)) else 30.0
        elif 'date' in field_name.lower():
            return 85.0 if self._is_valid_date_format(str(field_value)) else 25.0
        elif 'amount' in field_name.lower():
            return 80.0 if self._is_valid_amount(field_value) else 20.0
        elif 'numer' in field_name.lower():
            return self._validate_invoice_number_pattern(str(field_value), raw_text)
        else:
            return 60.0  # Default confidence for other fields
    
    def _validate_field_value(self, field_name: str, field_value: Any) -> Tuple[float, Dict[str, Any]]:
        """Validate field value and return confidence score with details"""
        validation_details = {'field_name': field_name, 'validations_performed': []}
        
        if not field_value:
            return 0.0, validation_details
        
        confidence_scores = []
        
        # Field-specific validation
        if 'nip' in field_name.lower():
            is_valid, score = self._validate_nip_business_rules(str(field_value))
            confidence_scores.append(score)
            validation_details['validations_performed'].append({
                'type': 'nip_validation',
                'is_valid': is_valid,
                'score': score
            })
        
        elif 'date' in field_name.lower():
            is_valid, score = self._validate_date_business_rules(str(field_value))
            confidence_scores.append(score)
            validation_details['validations_performed'].append({
                'type': 'date_validation',
                'is_valid': is_valid,
                'score': score
            })
        
        elif 'amount' in field_name.lower():
            is_valid, score = self._validate_amount_business_rules(field_value)
            confidence_scores.append(score)
            validation_details['validations_performed'].append({
                'type': 'amount_validation',
                'is_valid': is_valid,
                'score': score
            })
        
        elif 'numer' in field_name.lower():
            is_valid, score = self._validate_invoice_number_business_rules(str(field_value))
            confidence_scores.append(score)
            validation_details['validations_performed'].append({
                'type': 'invoice_number_validation',
                'is_valid': is_valid,
                'score': score
            })
        
        # Calculate average validation score
        if confidence_scores:
            avg_score = sum(confidence_scores) / len(confidence_scores)
        else:
            avg_score = 50.0  # Neutral score for fields without specific validation
        
        validation_details['average_validation_score'] = avg_score
        return avg_score, validation_details
    
    def _calculate_field_polish_boost(self, field_name: str, field_value: Any, raw_text: str) -> float:
        """Calculate Polish language boost for a specific field"""
        if not field_value:
            return 0.0
        
        boost = 0.0
        field_value_str = str(field_value)
        
        # Company name fields
        if 'name' in field_name.lower():
            if self._has_polish_company_indicators(field_value_str):
                boost += 15.0
        
        # NIP fields
        elif 'nip' in field_name.lower():
            if len(field_value_str) == 10 and field_value_str.isdigit():
                boost += 10.0
        
        # Amount fields
        elif 'amount' in field_name.lower():
            if 'zł' in raw_text or 'PLN' in raw_text:
                boost += 8.0
        
        # Date fields
        elif 'date' in field_name.lower():
            polish_months = ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
                           'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia']
            if any(month in raw_text.lower() for month in polish_months):
                boost += 6.0
        
        return boost
    
    def _validate_nip_checksum(self, nip: str) -> bool:
        """Validate Polish NIP checksum"""
        if not nip or len(nip) != 10 or not nip.isdigit():
            return False
        
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        
        return checksum == int(nip[9])
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date string is in valid format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def _is_valid_amount(self, amount: Any) -> bool:
        """Check if amount is valid"""
        try:
            if isinstance(amount, str):
                amount = float(amount.replace(',', '.').replace(' ', ''))
            elif isinstance(amount, Decimal):
                amount = float(amount)
            
            return 0.01 <= amount <= 10000000.0
        except (ValueError, TypeError):
            return False
    
    def _has_polish_company_indicators(self, company_name: str) -> bool:
        """Check if company name has Polish business entity indicators"""
        if not company_name:
            return False
        
        indicators = ['sp. z o.o.', 's.a.', 'spółka akcyjna', 'p.p.h.u.', 
                     'firma', 'przedsiębiorstwo']
        
        company_lower = company_name.lower()
        return any(indicator in company_lower for indicator in indicators)
    
    def _update_calculation_metadata(self, 
                                   confidence_result: Dict[str, Any],
                                   field_confidences: List[FieldConfidence],
                                   components: List[ConfidenceComponent]):
        """Update calculation metadata"""
        metadata = confidence_result['calculation_metadata']
        
        metadata['total_fields_analyzed'] = len(field_confidences)
        metadata['high_confidence_fields'] = sum(
            1 for fc in field_confidences if fc.final_confidence >= 80.0
        )
        metadata['low_confidence_fields'] = sum(
            1 for fc in field_confidences if fc.final_confidence < 60.0
        )
        
        # Count validation failures
        validation_failures = 0
        for fc in field_confidences:
            for comp in fc.components:
                if comp.source == ConfidenceSource.DATA_VALIDATION and comp.score < 50.0:
                    validation_failures += 1
        metadata['validation_failures'] = validation_failures
        
        # List boost factors applied
        boost_factors = []
        for comp in components:
            if comp.source == ConfidenceSource.POLISH_LANGUAGE and comp.score > 0:
                boost_factors.extend(comp.details.get('boost_categories', []))
        metadata['boost_factors_applied'] = boost_factors
    
    def _update_calculation_stats(self, confidence_result: Dict[str, Any]):
        """Update performance statistics"""
        self.calculation_stats['total_calculations'] += 1
        
        overall_conf = confidence_result['overall_confidence']
        total_calcs = self.calculation_stats['total_calculations']
        current_avg = self.calculation_stats['average_confidence']
        
        # Update running average
        self.calculation_stats['average_confidence'] = (
            (current_avg * (total_calcs - 1) + overall_conf) / total_calcs
        )
        
        # Update source performance
        for comp in confidence_result['confidence_components']:
            source = comp['source']
            if source not in self.calculation_stats['source_performance']:
                self.calculation_stats['source_performance'][source] = {
                    'count': 0,
                    'average_score': 0.0
                }
            
            source_stats = self.calculation_stats['source_performance'][source]
            source_stats['count'] += 1
            current_avg = source_stats['average_score']
            source_stats['average_score'] = (
                (current_avg * (source_stats['count'] - 1) + comp['score']) / source_stats['count']
            )
    
    def get_calculation_statistics(self) -> Dict[str, Any]:
        """Get performance statistics for confidence calculations"""
        return self.calculation_stats.copy()