"""
OCR Integration Service for FaktuLove

This service handles the integration between OCR results and Faktura creation,
including automatic invoice generation and manual verification workflows.
Updated to use the new OCR service factory for seamless switching between implementations.
Enhanced with comprehensive security and privacy features.
"""

import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, Tuple, List
from django.db import transaction, models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import OCRResult, Faktura, Kontrahent, Firma, PozycjaFaktury, OCRValidation
from .status_sync_service import StatusSyncService, StatusSyncError
from .ocr_service_factory import get_ocr_service
from .ocr_fallback_handler import OCRFallbackHandler, ManualReviewQueue
from .ocr_security_service import (
    get_file_encryption_service,
    get_ocr_auth_service,
    get_audit_logger,
    get_cleanup_service,
    get_premises_validator,
    OCRSecurityError
)

logger = logging.getLogger(__name__)


class OCRIntegrationError(Exception):
    """Custom exception for OCR integration errors"""
    pass


class OCRDataValidator:
    """Enhanced validator for OCR extracted data with support for multiple OCR engines"""
    
    # Field mappings for different OCR engine formats
    FIELD_MAPPINGS = {
        # Google Cloud Document AI format
        'google': {
            'invoice_number': 'numer_faktury',
            'invoice_date': 'data_wystawienia',
            'due_date': 'data_sprzedazy',
            'supplier_name': 'sprzedawca_nazwa',
            'buyer_name': 'nabywca_nazwa',
            'line_items': 'pozycje',
            'total_amount': 'suma_brutto',
            'net_amount': 'suma_netto',
            'vat_amount': 'suma_vat',
            'supplier_nip': 'sprzedawca_nip',
            'buyer_nip': 'nabywca_nip'
        },
        # Open Source OCR format
        'opensource': {
            'invoice_number': 'numer_faktury',
            'invoice_date': 'data_wystawienia',
            'due_date': 'data_sprzedazy',
            'supplier_name': 'sprzedawca_nazwa',
            'buyer_name': 'nabywca_nazwa',
            'line_items': 'pozycje',
            'total_amount': 'suma_brutto',
            'net_amount': 'suma_netto',
            'vat_amount': 'suma_vat',
            'supplier_nip': 'sprzedawca_nip',
            'buyer_nip': 'nabywca_nip'
        }
    }
    
    REQUIRED_FIELDS = [
        'numer_faktury',
        'data_wystawienia', 
        'data_sprzedazy',
        'sprzedawca_nazwa',
        'nabywca_nazwa',
        'pozycje'
    ]
    
    # Confidence thresholds for different validation levels
    CONFIDENCE_THRESHOLDS = {
        'high': 90.0,      # Auto-create faktura
        'medium': 70.0,    # Manual review recommended
        'low': 50.0        # Requires manual validation
    }
    
    @classmethod
    def validate_ocr_data(cls, extracted_data: Dict[str, Any], 
                         confidence_score: float = 0.0,
                         engine_type: str = 'opensource') -> Tuple[bool, list]:
        """
        Enhanced validation for OCR extracted data with engine-specific handling
        
        Args:
            extracted_data: Extracted data from OCR
            confidence_score: Overall confidence score
            engine_type: Type of OCR engine ('google', 'opensource')
        
        Returns:
            Tuple[bool, list]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Normalize data format based on engine type
        normalized_data = cls._normalize_data_format(extracted_data, engine_type)
        
        # Check required fields with confidence-based validation
        for field in cls.REQUIRED_FIELDS:
            field_value = normalized_data.get(field)
            field_confidence = cls._get_field_confidence(extracted_data, field, confidence_score)
            
            if not field_value:
                if field_confidence < cls.CONFIDENCE_THRESHOLDS['low']:
                    errors.append(f"Brak wymaganego pola: {field} (niska pewność: {field_confidence:.1f}%)")
                else:
                    errors.append(f"Brak wymaganego pola: {field}")
        
        # Enhanced date validation with Polish format support
        date_fields = [('data_wystawienia', 'data wystawienia'), ('data_sprzedazy', 'data sprzedaży')]
        for field_name, display_name in date_fields:
            if normalized_data.get(field_name):
                if not cls._validate_date_enhanced(normalized_data[field_name]):
                    field_confidence = cls._get_field_confidence(extracted_data, field_name, confidence_score)
                    errors.append(f"Nieprawidłowa {display_name} (pewność: {field_confidence:.1f}%)")
        
        # Enhanced position validation
        pozycje = normalized_data.get('pozycje', [])
        if not isinstance(pozycje, list) or len(pozycje) == 0:
            errors.append("Brak pozycji na fakturze")
        else:
            for i, pozycja in enumerate(pozycje):
                pos_errors = cls._validate_position_enhanced(pozycja, i + 1, confidence_score)
                errors.extend(pos_errors)
        
        # Enhanced amount validation with Polish number format support
        amount_fields = [('suma_brutto', 'suma brutto'), ('suma_netto', 'suma netto')]
        for field_name, display_name in amount_fields:
            if normalized_data.get(field_name):
                if not cls._validate_amount_enhanced(normalized_data[field_name]):
                    field_confidence = cls._get_field_confidence(extracted_data, field_name, confidence_score)
                    errors.append(f"Nieprawidłowa {display_name} (pewność: {field_confidence:.1f}%)")
        
        # Validate Polish NIP numbers
        nip_fields = [('sprzedawca_nip', 'NIP sprzedawcy'), ('nabywca_nip', 'NIP nabywcy')]
        for field_name, display_name in nip_fields:
            if normalized_data.get(field_name):
                if not cls._validate_polish_nip(normalized_data[field_name]):
                    field_confidence = cls._get_field_confidence(extracted_data, field_name, confidence_score)
                    errors.append(f"Nieprawidłowy {display_name} (pewność: {field_confidence:.1f}%)")
        
        # Cross-validation checks
        cross_validation_errors = cls._perform_cross_validation(normalized_data, confidence_score)
        errors.extend(cross_validation_errors)
        
        return len(errors) == 0, errors
    
    @classmethod
    def _normalize_data_format(cls, extracted_data: Dict[str, Any], engine_type: str) -> Dict[str, Any]:
        """Normalize data format based on OCR engine type"""
        if engine_type not in cls.FIELD_MAPPINGS:
            return extracted_data
        
        mapping = cls.FIELD_MAPPINGS[engine_type]
        normalized = {}
        
        # Map fields from engine format to internal format
        for engine_field, internal_field in mapping.items():
            if engine_field in extracted_data:
                normalized[internal_field] = extracted_data[engine_field]
        
        # Copy unmapped fields as-is
        for key, value in extracted_data.items():
            if key not in mapping and key not in normalized:
                normalized[key] = value
        
        return normalized
    
    @classmethod
    def _get_field_confidence(cls, extracted_data: Dict[str, Any], field_name: str, 
                            default_confidence: float) -> float:
        """Get confidence score for a specific field"""
        field_confidence = extracted_data.get('field_confidence', {})
        return field_confidence.get(field_name, default_confidence)
    
    @classmethod
    def _validate_date_enhanced(cls, date_str: str) -> bool:
        """Enhanced date validation with Polish format support"""
        try:
            if isinstance(date_str, str):
                # Polish date formats
                formats = [
                    '%Y-%m-%d',      # ISO format
                    '%d.%m.%Y',      # Polish format with dots
                    '%d/%m/%Y',      # Polish format with slashes
                    '%d-%m-%Y',      # Polish format with dashes
                    '%Y.%m.%d',      # Alternative ISO with dots
                ]
                
                for fmt in formats:
                    try:
                        datetime.strptime(date_str, fmt)
                        return True
                    except ValueError:
                        continue
                return False
            return True
        except Exception:
            return False
    
    @classmethod
    def _validate_amount_enhanced(cls, amount_str: str) -> bool:
        """Enhanced amount validation with Polish number format support"""
        try:
            if not amount_str:
                return False
            
            import re
            # Clean the amount string - remove currency symbols and spaces
            cleaned = re.sub(r'[^\d,.-]', '', str(amount_str))
            
            # Handle Polish decimal separator (comma)
            if ',' in cleaned and '.' in cleaned:
                # Both comma and dot present - assume comma is thousands separator
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Only comma - assume it's decimal separator
                cleaned = cleaned.replace(',', '.')
            
            # Validate the cleaned amount
            Decimal(cleaned)
            return True
        except (InvalidOperation, ValueError, TypeError):
            return False
    
    @classmethod
    def _validate_polish_nip(cls, nip_str: str) -> bool:
        """Validate Polish NIP number with checksum verification"""
        try:
            if not nip_str:
                return False
            
            import re
            # Extract digits only
            nip_digits = re.sub(r'[^\d]', '', str(nip_str))
            
            # Polish NIP should have 10 digits
            if len(nip_digits) != 10:
                return False
            
            # Validate NIP checksum
            weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
            checksum = sum(int(nip_digits[i]) * weights[i] for i in range(9)) % 11
            
            if checksum == 10:
                return False
            
            return checksum == int(nip_digits[9])
        except (ValueError, IndexError):
            return False
    
    @classmethod
    def _validate_position_enhanced(cls, pozycja: Dict[str, Any], position_num: int, 
                                  confidence_score: float) -> list:
        """Enhanced validation for invoice positions"""
        errors = []
        required_pos_fields = ['nazwa', 'ilosc', 'cena_netto', 'vat']
        
        for field in required_pos_fields:
            if not pozycja.get(field):
                errors.append(f"Pozycja {position_num}: brak pola {field}")
        
        # Enhanced numeric field validation
        numeric_fields = [('ilosc', 'ilość'), ('cena_netto', 'cena netto')]
        for field_name, display_name in numeric_fields:
            if pozycja.get(field_name):
                if not cls._validate_amount_enhanced(str(pozycja[field_name])):
                    errors.append(f"Pozycja {position_num}: nieprawidłowa {display_name}")
        
        # Validate VAT rate
        if pozycja.get('vat'):
            if not cls._validate_vat_rate(pozycja['vat']):
                errors.append(f"Pozycja {position_num}: nieprawidłowa stawka VAT")
        
        return errors
    
    @classmethod
    def _validate_vat_rate(cls, vat_str: str) -> bool:
        """Validate VAT rate format"""
        try:
            import re
            # Extract percentage value
            vat_match = re.search(r'(\d+(?:[.,]\d+)?)', str(vat_str))
            if not vat_match:
                return False
            
            vat_value = float(vat_match.group(1).replace(',', '.'))
            # Common Polish VAT rates
            valid_rates = [0, 5, 8, 23, 7, 22]  # Including historical rates
            
            return vat_value in valid_rates or 0 <= vat_value <= 100
        except (ValueError, AttributeError):
            return False
    
    @classmethod
    def _perform_cross_validation(cls, normalized_data: Dict[str, Any], 
                                confidence_score: float) -> list:
        """Perform cross-validation checks between related fields"""
        errors = []
        
        # Validate amount consistency
        try:
            suma_netto = normalized_data.get('suma_netto')
            suma_vat = normalized_data.get('suma_vat')
            suma_brutto = normalized_data.get('suma_brutto')
            
            if all([suma_netto, suma_vat, suma_brutto]):
                netto_decimal = Decimal(str(suma_netto).replace(',', '.'))
                vat_decimal = Decimal(str(suma_vat).replace(',', '.'))
                brutto_decimal = Decimal(str(suma_brutto).replace(',', '.'))
                
                calculated_brutto = netto_decimal + vat_decimal
                
                # Allow small rounding differences
                if abs(calculated_brutto - brutto_decimal) > Decimal('0.02'):
                    errors.append(f"Niezgodność sum: netto + VAT ≠ brutto (różnica: {abs(calculated_brutto - brutto_decimal)})")
        except (InvalidOperation, ValueError, TypeError):
            # Skip validation if amounts can't be parsed
            pass
        
        # Validate date consistency
        try:
            data_wystawienia = normalized_data.get('data_wystawienia')
            data_sprzedazy = normalized_data.get('data_sprzedazy')
            
            if data_wystawienia and data_sprzedazy:
                # Parse dates for comparison
                from datetime import datetime
                
                for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        date_wyst = datetime.strptime(data_wystawienia, fmt).date()
                        date_sprz = datetime.strptime(data_sprzedazy, fmt).date()
                        
                        # Data sprzedaży shouldn't be much later than data wystawienia
                        if (date_sprz - date_wyst).days > 365:
                            errors.append("Data sprzedaży znacznie późniejsza niż data wystawienia")
                        break
                    except ValueError:
                        continue
        except Exception:
            # Skip date validation if parsing fails
            pass
        
        return errors
    
    @staticmethod
    def _validate_date(date_str: str) -> bool:
        """Validate date string"""
        try:
            if isinstance(date_str, str):
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
                    try:
                        datetime.strptime(date_str, fmt)
                        return True
                    except ValueError:
                        continue
                return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def _validate_position(pozycja: Dict[str, Any], position_num: int) -> list:
        """Validate single invoice position"""
        errors = []
        required_pos_fields = ['nazwa', 'ilosc', 'cena_netto', 'vat']
        
        for field in required_pos_fields:
            if not pozycja.get(field):
                errors.append(f"Pozycja {position_num}: brak pola {field}")
        
        # Validate numeric fields
        for field in ['ilosc', 'cena_netto']:
            if pozycja.get(field):
                try:
                    Decimal(str(pozycja[field]))
                except (InvalidOperation, ValueError):
                    errors.append(f"Pozycja {position_num}: nieprawidłowa wartość {field}")
        
        return errors


class FakturaCreator:
    """Enhanced Faktura creator with support for multiple OCR engine formats"""
    
    def __init__(self, user: User, processing_strategy: str = 'standard'):
        self.user = user
        self.processing_strategy = processing_strategy
        
        # Processing strategies for different confidence levels
        self.strategies = {
            'strict': {'min_confidence': 95.0, 'require_all_fields': True},
            'standard': {'min_confidence': 80.0, 'require_all_fields': False},
            'lenient': {'min_confidence': 60.0, 'require_all_fields': False}
        }
    
    def create_from_ocr(self, ocr_result: OCRResult) -> Faktura:
        """
        Enhanced Faktura creation with multiple OCR engine support
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            Faktura: Created invoice
            
        Raises:
            OCRIntegrationError: If creation fails
        """
        try:
            with transaction.atomic():
                extracted_data = ocr_result.extracted_data
                
                # Detect OCR engine type from processor version
                engine_type = self._detect_engine_type(ocr_result)
                
                # Enhanced validation with engine-specific handling
                is_valid, errors = OCRDataValidator.validate_ocr_data(
                    extracted_data, 
                    ocr_result.confidence_score,
                    engine_type
                )
                
                # Apply processing strategy
                strategy_config = self.strategies.get(self.processing_strategy, self.strategies['standard'])
                
                if not is_valid:
                    if ocr_result.confidence_score < strategy_config['min_confidence']:
                        raise OCRIntegrationError(f"Błędy walidacji (niska pewność {ocr_result.confidence_score:.1f}%): {'; '.join(errors)}")
                    elif strategy_config['require_all_fields']:
                        raise OCRIntegrationError(f"Błędy walidacji (tryb ścisły): {'; '.join(errors)}")
                    else:
                        logger.warning(f"Proceeding with validation errors due to {self.processing_strategy} strategy: {'; '.join(errors)}")
                
                # Normalize data format for internal processing
                normalized_data = self._normalize_extracted_data(extracted_data, engine_type)
                
                # Get or create kontrahent with enhanced data handling
                kontrahent = self._get_or_create_kontrahent_enhanced(normalized_data, engine_type)
                
                # Get user's company
                try:
                    firma = self.user.firma
                except Firma.DoesNotExist:
                    raise OCRIntegrationError("Użytkownik nie ma przypisanej firmy")
                
                # Create faktura with enhanced data handling
                faktura = self._create_faktura_enhanced(normalized_data, firma, kontrahent, ocr_result, engine_type)
                
                # Create positions with enhanced handling
                self._create_positions_enhanced(faktura, normalized_data.get('pozycje', []), engine_type)
                
                # Update OCR result with atomic status changes
                ocr_result.faktura = faktura
                ocr_result.auto_created_faktura = True
                ocr_result.save(update_fields=['faktura', 'auto_created_faktura'])
                ocr_result.mark_processing_completed()
                
                # Update Faktura OCR fields with enhanced metadata
                self._update_faktura_ocr_metadata(faktura, ocr_result, engine_type)
                
                # Sync document status after successful faktura creation
                try:
                    StatusSyncService.sync_document_status(ocr_result.document)
                    logger.debug(f"Synced document status after creating Faktura {faktura.numer}")
                except StatusSyncError as e:
                    logger.warning(f"Failed to sync document status after creating Faktura {faktura.numer}: {str(e)}")
                    # Don't fail the entire creation for sync errors
                
                logger.info(f"Successfully created Faktura {faktura.numer} from OCR result {ocr_result.id} using {engine_type} engine")
                return faktura
                
        except Exception as e:
            logger.error(f"Failed to create Faktura from OCR result {ocr_result.id}: {str(e)}", exc_info=True)
            
            # Enhanced error handling with retry logic
            self._handle_creation_error(ocr_result, e)
            
            raise OCRIntegrationError(f"Nie udało się utworzyć faktury: {str(e)}")
    
    def _detect_engine_type(self, ocr_result: OCRResult) -> str:
        """Detect OCR engine type from processor version or other metadata"""
        processor_version = ocr_result.processor_version or ''
        
        if 'opensource' in processor_version.lower():
            return 'opensource'
        elif 'google' in processor_version.lower() or 'document-ai' in processor_version.lower():
            return 'google'
        else:
            # Try to detect from data structure
            extracted_data = ocr_result.extracted_data or {}
            
            # Check for Google Cloud Document AI specific fields
            if 'entities' in extracted_data or 'pages' in extracted_data:
                return 'google'
            
            # Check for open source specific fields
            if 'raw_ocr_results' in extracted_data or 'processing_steps' in extracted_data:
                return 'opensource'
            
            # Default to opensource for new implementation
            return 'opensource'
    
    def _normalize_extracted_data(self, extracted_data: Dict[str, Any], engine_type: str) -> Dict[str, Any]:
        """Normalize extracted data format for internal processing"""
        if engine_type == 'google':
            return self._normalize_google_format(extracted_data)
        elif engine_type == 'opensource':
            return self._normalize_opensource_format(extracted_data)
        else:
            return extracted_data
    
    def _normalize_google_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Google Cloud Document AI format"""
        # Google format is already normalized in most cases
        normalized = data.copy()
        
        # Map Google-specific field names if needed
        field_mapping = {
            'invoice_number': 'numer_faktury',
            'invoice_date': 'data_wystawienia',
            'due_date': 'data_sprzedazy',
            'supplier_name': 'sprzedawca_nazwa',
            'buyer_name': 'nabywca_nazwa',
            'total_amount': 'suma_brutto',
            'net_amount': 'suma_netto',
            'vat_amount': 'suma_vat',
            'supplier_nip': 'sprzedawca_nip',
            'buyer_nip': 'nabywca_nip'
        }
        
        for google_field, internal_field in field_mapping.items():
            if google_field in data and internal_field not in normalized:
                normalized[internal_field] = data[google_field]
        
        return normalized
    
    def _normalize_opensource_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Open Source OCR format"""
        normalized = data.copy()
        
        # Map open source field names to internal format
        field_mapping = {
            'invoice_number': 'numer_faktury',
            'invoice_date': 'data_wystawienia',
            'due_date': 'data_sprzedazy',
            'supplier_name': 'sprzedawca_nazwa',
            'buyer_name': 'nabywca_nazwa',
            'total_amount': 'suma_brutto',
            'net_amount': 'suma_netto',
            'vat_amount': 'suma_vat',
            'supplier_nip': 'sprzedawca_nip',
            'buyer_nip': 'nabywca_nip',
            'line_items': 'pozycje'
        }
        
        for os_field, internal_field in field_mapping.items():
            if os_field in data and internal_field not in normalized:
                normalized[internal_field] = data[os_field]
        
        # Handle line items format conversion
        if 'line_items' in data and isinstance(data['line_items'], list):
            normalized['pozycje'] = self._convert_line_items_format(data['line_items'])
        
        return normalized
    
    def _convert_line_items_format(self, line_items: list) -> list:
        """Convert line items to internal format"""
        converted = []
        
        for item in line_items:
            if isinstance(item, dict):
                converted_item = {
                    'nazwa': item.get('description', ''),
                    'ilosc': item.get('quantity', '1'),
                    'jednostka': item.get('unit', 'szt'),
                    'cena_netto': item.get('unit_price', '0'),
                    'vat': item.get('vat_rate', '23%'),
                    'wartosc_netto': item.get('net_amount', '0'),
                    'wartosc_brutto': item.get('gross_amount', '0')
                }
                converted.append(converted_item)
        
        return converted
    
    def _get_or_create_kontrahent_enhanced(self, normalized_data: Dict[str, Any], engine_type: str) -> Kontrahent:
        """Enhanced kontrahent creation with better data handling"""
        sprzedawca_data = {
            'nazwa': normalized_data.get('sprzedawca_nazwa', ''),
            'nip': self._clean_nip(normalized_data.get('sprzedawca_nip', '')),
            'ulica': normalized_data.get('sprzedawca_ulica', ''),
            'numer_domu': normalized_data.get('sprzedawca_numer_domu', ''),
            'kod_pocztowy': normalized_data.get('sprzedawca_kod_pocztowy', ''),
            'miejscowosc': normalized_data.get('sprzedawca_miejscowosc', ''),
            'kraj': normalized_data.get('sprzedawca_kraj', 'Polska'),
        }
        
        # Handle address parsing from single field if needed
        if not sprzedawca_data['ulica'] and normalized_data.get('supplier_address'):
            parsed_address = self._parse_address(normalized_data['supplier_address'])
            sprzedawca_data.update(parsed_address)
        
        # Try to find existing kontrahent by NIP first, then by name
        existing_kontrahent = None
        
        if sprzedawca_data['nip']:
            existing_kontrahent = Kontrahent.objects.filter(
                user=self.user,
                nip=sprzedawca_data['nip']
            ).first()
        
        if not existing_kontrahent and sprzedawca_data['nazwa']:
            # Try to find by similar name
            existing_kontrahent = Kontrahent.objects.filter(
                user=self.user,
                nazwa__icontains=sprzedawca_data['nazwa'][:20]  # Partial match
            ).first()
        
        if existing_kontrahent:
            logger.info(f"Found existing Kontrahent: {existing_kontrahent.nazwa}")
            # Update with new information if available
            self._update_kontrahent_data(existing_kontrahent, sprzedawca_data)
            return existing_kontrahent
        
        # Create new kontrahent
        kontrahent = Kontrahent.objects.create(
            user=self.user,
            czy_firma=True,
            **{k: v for k, v in sprzedawca_data.items() if v}  # Only non-empty values
        )
        
        logger.info(f"Created new Kontrahent: {kontrahent.nazwa}")
        return kontrahent
    
    def _clean_nip(self, nip_str: str) -> str:
        """Clean NIP number format"""
        if not nip_str:
            return ''
        
        import re
        # Extract digits only
        nip_digits = re.sub(r'[^\d]', '', str(nip_str))
        
        # Polish NIP should have 10 digits
        if len(nip_digits) == 10:
            return nip_digits
        
        return nip_str  # Return original if can't clean
    
    def _parse_address(self, address_str: str) -> Dict[str, str]:
        """Parse address string into components"""
        if not address_str:
            return {}
        
        import re
        parsed = {}
        
        # Try to extract postal code and city
        postal_match = re.search(r'(\d{2}-\d{3})\s+([^,]+)', address_str)
        if postal_match:
            parsed['kod_pocztowy'] = postal_match.group(1)
            parsed['miejscowosc'] = postal_match.group(2).strip()
        
        # Extract street (everything before postal code or city)
        if postal_match:
            street_part = address_str[:postal_match.start()].strip().rstrip(',')
            if street_part:
                parsed['ulica'] = street_part
        
        return parsed
    
    def _update_kontrahent_data(self, kontrahent: Kontrahent, new_data: Dict[str, str]):
        """Update existing kontrahent with new data if fields are empty"""
        updated = False
        
        for field, value in new_data.items():
            if value and not getattr(kontrahent, field, None):
                setattr(kontrahent, field, value)
                updated = True
        
        if updated:
            kontrahent.save()
            logger.info(f"Updated Kontrahent {kontrahent.nazwa} with new data")
    
    def _create_faktura_enhanced(self, normalized_data: Dict[str, Any], firma: Firma, 
                               kontrahent: Kontrahent, ocr_result: OCRResult, engine_type: str) -> Faktura:
        """Enhanced Faktura creation with better data handling"""
        
        # Parse dates with enhanced format support
        data_wystawienia = self._parse_date_enhanced(normalized_data.get('data_wystawienia'))
        data_sprzedazy = self._parse_date_enhanced(normalized_data.get('data_sprzedazy'))
        
        # Calculate payment term with fallback
        termin_platnosci_dni = normalized_data.get('termin_platnosci_dni', 14)
        if data_wystawienia:
            termin_platnosci = data_wystawienia + timedelta(days=termin_platnosci_dni)
        else:
            termin_platnosci = timezone.now().date() + timedelta(days=termin_platnosci_dni)
        
        # Generate invoice number if not provided or invalid
        numer_faktury = normalized_data.get('numer_faktury', '')
        if not numer_faktury or len(numer_faktury) < 3:
            numer_faktury = self._generate_invoice_number(firma)
            logger.warning(f"Generated invoice number {numer_faktury} due to missing/invalid OCR extraction")
        
        faktura = Faktura.objects.create(
            user=self.user,
            typ_dokumentu='FV',  # Default to VAT invoice
            numer=numer_faktury,
            data_wystawienia=data_wystawienia or timezone.now().date(),
            data_sprzedazy=data_sprzedazy or timezone.now().date(),
            miejsce_wystawienia=normalized_data.get('miejsce_wystawienia', ''),
            sprzedawca=firma,
            nabywca=kontrahent,
            typ_faktury='koszt',  # OCR invoices are typically cost invoices
            sposob_platnosci=normalized_data.get('sposob_platnosci', 'przelew'),
            termin_platnosci=termin_platnosci,
            status='wystawiona',
            waluta=normalized_data.get('waluta', 'PLN'),
            uwagi=f"Utworzona automatycznie z OCR {engine_type} (pewność: {ocr_result.confidence_score:.1f}%)",
            auto_numer=False,  # Don't auto-generate number, use OCR extracted
        )
        
        return faktura
    
    def _generate_invoice_number(self, firma: Firma) -> str:
        """Generate invoice number when OCR extraction fails"""
        from datetime import datetime
        current_date = datetime.now()
        
        # Simple format: FV/YYYY/MM/sequential
        base_number = f"FV/{current_date.year}/{current_date.month:02d}"
        
        # Find next sequential number
        existing_count = Faktura.objects.filter(
            sprzedawca=firma,
            numer__startswith=base_number
        ).count()
        
        return f"{base_number}/{existing_count + 1:03d}"
    
    def _create_positions_enhanced(self, faktura: Faktura, pozycje_data: list, engine_type: str):
        """Enhanced position creation with better error handling"""
        if not pozycje_data:
            # Create a default position if none provided
            PozycjaFaktury.objects.create(
                faktura=faktura,
                nazwa="Pozycja z OCR (brak szczegółów)",
                ilosc=Decimal('1'),
                jednostka='szt',
                cena_netto=Decimal('0.00'),
                vat='23%'
            )
            logger.warning(f"Created default position for Faktura {faktura.numer} due to missing OCR data")
            return
        
        for i, pozycja_data in enumerate(pozycje_data):
            try:
                # Enhanced data parsing with fallbacks
                nazwa = pozycja_data.get('nazwa', f'Pozycja {i+1}')
                ilosc = self._parse_decimal(pozycja_data.get('ilosc', '1'))
                cena_netto = self._parse_decimal(pozycja_data.get('cena_netto', '0'))
                vat = str(pozycja_data.get('vat', '23%'))
                
                PozycjaFaktury.objects.create(
                    faktura=faktura,
                    nazwa=nazwa,
                    ilosc=ilosc,
                    jednostka=pozycja_data.get('jednostka', 'szt'),
                    cena_netto=cena_netto,
                    vat=vat,
                    rabat=self._parse_decimal(pozycja_data.get('rabat')) if pozycja_data.get('rabat') else None,
                    rabat_typ=pozycja_data.get('rabat_typ', 'procent') if pozycja_data.get('rabat') else None
                )
            except Exception as e:
                logger.error(f"Failed to create position {i+1} for Faktura {faktura.numer}: {e}")
                # Create fallback position
                PozycjaFaktury.objects.create(
                    faktura=faktura,
                    nazwa=f"Pozycja {i+1} (błąd OCR)",
                    ilosc=Decimal('1'),
                    jednostka='szt',
                    cena_netto=Decimal('0.00'),
                    vat='23%'
                )
    
    def _parse_decimal(self, value) -> Decimal:
        """Parse decimal value with Polish format support"""
        if value is None:
            return Decimal('0')
        
        try:
            # Handle Polish decimal separator
            str_value = str(value).replace(',', '.')
            # Remove any non-numeric characters except dots
            import re
            cleaned = re.sub(r'[^\d.-]', '', str_value)
            return Decimal(cleaned) if cleaned else Decimal('0')
        except (InvalidOperation, ValueError):
            return Decimal('0')
    
    def _parse_date_enhanced(self, date_str: str) -> Optional[date]:
        """Enhanced date parsing with Polish format support"""
        if not date_str:
            return None
        
        if isinstance(date_str, date):
            return date_str
        
        # Polish date formats
        formats = [
            '%Y-%m-%d',      # ISO format
            '%d.%m.%Y',      # Polish format with dots
            '%d/%m/%Y',      # Polish format with slashes
            '%d-%m-%Y',      # Polish format with dashes
            '%Y.%m.%d',      # Alternative ISO with dots
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _update_faktura_ocr_metadata(self, faktura: Faktura, ocr_result: OCRResult, engine_type: str):
        """Update Faktura with enhanced OCR metadata"""
        faktura.source_document = ocr_result.document
        faktura.ocr_confidence = ocr_result.confidence_score
        faktura.ocr_processing_time = ocr_result.processing_time
        faktura.ocr_extracted_at = timezone.now()
        faktura.manual_verification_required = ocr_result.needs_human_review
        
        # Add engine-specific metadata to uwagi if not already present
        if engine_type not in (faktura.uwagi or ''):
            current_uwagi = faktura.uwagi or ''
            faktura.uwagi = f"{current_uwagi}\nSilnik OCR: {engine_type}".strip()
        
        faktura.save()
    
    def _handle_creation_error(self, ocr_result: OCRResult, error: Exception):
        """Enhanced error handling with retry logic"""
        try:
            # Determine if error is retryable
            retryable_errors = [
                'connection',
                'timeout',
                'temporary',
                'network'
            ]
            
            error_str = str(error).lower()
            is_retryable = any(keyword in error_str for keyword in retryable_errors)
            
            if is_retryable:
                # Mark for retry instead of failed
                ocr_result.processing_status = 'pending'
                ocr_result.error_message = f"Retryable error: {str(error)}"
                ocr_result.save(update_fields=['processing_status', 'error_message'])
                logger.info(f"Marked OCR result {ocr_result.id} for retry due to retryable error")
            else:
                # Mark as failed
                ocr_result.mark_processing_failed(str(error))
            
            # Sync document status
            StatusSyncService.sync_document_status(ocr_result.document)
            
        except Exception as sync_error:
            logger.error(f"Failed to handle creation error for OCR result {ocr_result.id}: {str(sync_error)}")
    
    def _get_or_create_kontrahent(self, extracted_data: Dict[str, Any]) -> Kontrahent:
        """Get or create kontrahent from OCR data"""
        sprzedawca_data = {
            'nazwa': extracted_data['sprzedawca_nazwa'],
            'nip': extracted_data.get('sprzedawca_nip', ''),
            'ulica': extracted_data.get('sprzedawca_ulica', ''),
            'numer_domu': extracted_data.get('sprzedawca_numer_domu', ''),
            'kod_pocztowy': extracted_data.get('sprzedawca_kod_pocztowy', ''),
            'miejscowosc': extracted_data.get('sprzedawca_miejscowosc', ''),
            'kraj': extracted_data.get('sprzedawca_kraj', 'Polska'),
        }
        
        # Try to find existing kontrahent by NIP, or create new one
        if sprzedawca_data['nip']:
            existing_kontrahent = Kontrahent.objects.filter(
                user=self.user,
                nip=sprzedawca_data['nip']
            ).first()
            
            if existing_kontrahent:
                logger.info(f"Found existing Kontrahent: {existing_kontrahent.nazwa}")
                return existing_kontrahent
        
        # Create new kontrahent
        kontrahent = Kontrahent.objects.create(
            user=self.user,
            czy_firma=True,
            **sprzedawca_data
        )
        
        logger.info(f"Created new Kontrahent: {kontrahent.nazwa}")
        return kontrahent
    
    def _create_faktura(self, extracted_data: Dict[str, Any], firma: Firma, 
                       kontrahent: Kontrahent, ocr_result: OCRResult) -> Faktura:
        """Create Faktura instance"""
        
        # Parse dates
        data_wystawienia = self._parse_date(extracted_data['data_wystawienia'])
        data_sprzedazy = self._parse_date(extracted_data['data_sprzedazy'])
        
        # Calculate payment term (default 14 days if not specified)
        termin_platnosci_dni = extracted_data.get('termin_platnosci_dni', 14)
        termin_platnosci = data_wystawienia + timedelta(days=termin_platnosci_dni)
        
        faktura = Faktura.objects.create(
            user=self.user,
            typ_dokumentu='FV',  # Default to VAT invoice
            numer=extracted_data['numer_faktury'],
            data_wystawienia=data_wystawienia,
            data_sprzedazy=data_sprzedazy,
            miejsce_wystawienia=extracted_data.get('miejsce_wystawienia', ''),
            sprzedawca=firma,
            nabywca=kontrahent,
            typ_faktury='koszt',  # OCR invoices are typically cost invoices
            sposob_platnosci=extracted_data.get('sposob_platnosci', 'przelew'),
            termin_platnosci=termin_platnosci,
            status='wystawiona',
            waluta=extracted_data.get('waluta', 'PLN'),
            uwagi=f"Utworzona automatycznie z OCR (pewność: {ocr_result.confidence_score:.1f}%)",
            auto_numer=False,  # Don't auto-generate number, use OCR extracted
        )
        
        return faktura
    
    def _create_positions(self, faktura: Faktura, pozycje_data: list):
        """Create invoice positions"""
        for pozycja_data in pozycje_data:
            PozycjaFaktury.objects.create(
                faktura=faktura,
                nazwa=pozycja_data['nazwa'],
                ilosc=Decimal(str(pozycja_data['ilosc'])),
                jednostka=pozycja_data.get('jednostka', 'szt'),
                cena_netto=Decimal(str(pozycja_data['cena_netto'])),
                vat=str(pozycja_data['vat']),
                rabat=pozycja_data.get('rabat'),
                rabat_typ=pozycja_data.get('rabat_typ', 'procent') if pozycja_data.get('rabat') else None
            )
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string to date object"""
        if isinstance(date_str, date):
            return date_str
        
        # Try different formats
        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Cannot parse date: {date_str}")


def process_ocr_result(ocr_result_id: int, processing_strategy: str = 'standard') -> Optional[Faktura]:
    """
    Enhanced OCR result processing with multiple confidence thresholds and processing strategies
    
    Args:
        ocr_result_id: ID of OCRResult to process
        processing_strategy: Processing strategy ('strict', 'standard', 'lenient')
        
    Returns:
        Faktura: Created invoice or None if not created
    """
    ocr_result = None
    try:
        # Use atomic transaction to ensure consistent status updates
        with transaction.atomic():
            ocr_result = OCRResult.objects.select_related('document', 'document__user').get(id=ocr_result_id)
            
            logger.info(f"Starting enhanced OCR result processing for ID {ocr_result_id} with confidence {ocr_result.confidence_score:.1f}% using {processing_strategy} strategy")
            
            # Mark as processing and sync document status
            ocr_result.mark_processing_started()
            
            # Sync document status immediately after OCR status change
            try:
                StatusSyncService.sync_document_status(ocr_result.document)
                logger.debug(f"Synced document status after marking OCR result {ocr_result_id} as processing")
            except StatusSyncError as e:
                logger.warning(f"Failed to sync document status for OCR result {ocr_result_id}: {str(e)}")
                # Continue processing even if sync fails
            
            # Check if already has faktura
            if ocr_result.faktura:
                logger.info(f"OCR result {ocr_result_id} already has associated Faktura {ocr_result.faktura.id}")
                # Ensure status is properly synced for existing faktura
                ocr_result.mark_processing_completed()
                StatusSyncService.sync_document_status(ocr_result.document)
                return ocr_result.faktura
            
            # Enhanced processing with multiple confidence thresholds
            faktura = None
            confidence_thresholds = _get_confidence_thresholds(processing_strategy)
            
            if ocr_result.confidence_score >= confidence_thresholds['auto_create']:
                # High confidence - auto create faktura
                logger.info(f"Auto-creating Faktura for OCR result {ocr_result_id} (high confidence: {ocr_result.confidence_score:.1f}%)")
                
                try:
                    creator = FakturaCreator(ocr_result.document.user, processing_strategy)
                    faktura = creator.create_from_ocr(ocr_result)
                    
                    # Status is already updated in creator.create_from_ocr()
                    logger.info(f"Successfully auto-created Faktura {faktura.numer} from OCR result {ocr_result_id}")
                    
                except OCRIntegrationError as e:
                    logger.error(f"Failed to auto-create Faktura for OCR result {ocr_result_id}: {str(e)}")
                    
                    # Enhanced error handling with fallback strategies
                    if _should_retry_with_different_strategy(e, processing_strategy):
                        fallback_strategy = _get_fallback_strategy(processing_strategy)
                        logger.info(f"Retrying with {fallback_strategy} strategy")
                        return process_ocr_result(ocr_result_id, fallback_strategy)
                    
                    # Mark as failed and sync status
                    ocr_result.mark_processing_failed(str(e))
                    StatusSyncService.sync_document_status(ocr_result.document)
                    raise
                    
            elif ocr_result.confidence_score >= confidence_thresholds['manual_review']:
                # Medium confidence - mark for manual review with enhanced metadata
                logger.info(f"Marking OCR result {ocr_result_id} for manual review (medium confidence: {ocr_result.confidence_score:.1f}%)")
                ocr_result.mark_manual_review_required()
                
                # Add processing suggestions to help manual review
                _add_manual_review_suggestions(ocr_result, processing_strategy)
                
            elif ocr_result.confidence_score >= confidence_thresholds['minimum']:
                # Low but acceptable confidence - mark as completed but don't auto-create
                logger.info(f"OCR result {ocr_result_id} processed but not auto-created (low confidence: {ocr_result.confidence_score:.1f}%)")
                ocr_result.mark_processing_completed()
                
            else:
                # Very low confidence - mark as failed or for manual review based on strategy
                if processing_strategy == 'lenient':
                    logger.info(f"Marking OCR result {ocr_result_id} for manual review (very low confidence: {ocr_result.confidence_score:.1f}%)")
                    ocr_result.mark_manual_review_required()
                else:
                    logger.warning(f"OCR result {ocr_result_id} failed due to very low confidence: {ocr_result.confidence_score:.1f}%")
                    ocr_result.mark_processing_failed(f"Confidence too low: {ocr_result.confidence_score:.1f}%")
            
            # Final status synchronization
            try:
                StatusSyncService.sync_document_status(ocr_result.document)
                logger.debug(f"Final status sync completed for OCR result {ocr_result_id}")
            except StatusSyncError as e:
                logger.error(f"Failed final status sync for OCR result {ocr_result_id}: {str(e)}")
                # Don't fail the entire process for sync errors
            
            logger.info(f"Enhanced OCR result processing completed for ID {ocr_result_id}, final status: {ocr_result.processing_status}")
            return faktura
            
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found")
        return None
        
    except OCRIntegrationError:
        # Already handled above, just re-raise
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error processing OCR result {ocr_result_id}: {str(e)}", exc_info=True)
        
        # Enhanced error handling with retry logic
        try:
            if ocr_result:
                # Check if this is a retryable error
                if _is_retryable_error(e):
                    logger.info(f"Marking OCR result {ocr_result_id} for retry due to retryable error")
                    ocr_result.processing_status = 'pending'
                    ocr_result.error_message = f"Retryable error: {str(e)}"
                    ocr_result.save(update_fields=['processing_status', 'error_message'])
                else:
                    ocr_result.mark_processing_failed(f"Unexpected error: {str(e)}")
                
                StatusSyncService.sync_document_status(ocr_result.document)
        except Exception as sync_error:
            logger.error(f"Failed to update status after error for OCR result {ocr_result_id}: {str(sync_error)}")
        
        return None


def _get_confidence_thresholds(processing_strategy: str) -> Dict[str, float]:
    """Get confidence thresholds for processing strategy"""
    thresholds = {
        'strict': {
            'auto_create': 95.0,
            'manual_review': 85.0,
            'minimum': 70.0
        },
        'standard': {
            'auto_create': 90.0,
            'manual_review': 70.0,
            'minimum': 50.0
        },
        'lenient': {
            'auto_create': 80.0,
            'manual_review': 60.0,
            'minimum': 30.0
        }
    }
    
    return thresholds.get(processing_strategy, thresholds['standard'])


def _should_retry_with_different_strategy(error: Exception, current_strategy: str) -> bool:
    """Determine if error should trigger retry with different strategy"""
    error_str = str(error).lower()
    
    # Retry with more lenient strategy for validation errors
    validation_keywords = ['walidacji', 'validation', 'nieprawidłowa', 'brak']
    
    if any(keyword in error_str for keyword in validation_keywords):
        return current_strategy in ['strict', 'standard']
    
    return False


def _get_fallback_strategy(current_strategy: str) -> str:
    """Get fallback strategy for retry"""
    fallback_map = {
        'strict': 'standard',
        'standard': 'lenient',
        'lenient': 'lenient'  # No further fallback
    }
    
    return fallback_map.get(current_strategy, 'standard')


def _is_retryable_error(error: Exception) -> bool:
    """Check if error is retryable"""
    error_str = str(error).lower()
    retryable_keywords = [
        'connection', 'timeout', 'network', 'temporary',
        'service unavailable', 'rate limit', 'quota'
    ]
    
    return any(keyword in error_str for keyword in retryable_keywords)


def _add_manual_review_suggestions(ocr_result: OCRResult, processing_strategy: str):
    """Add suggestions for manual review based on processing results"""
    try:
        extracted_data = ocr_result.extracted_data or {}
        field_confidence = extracted_data.get('field_confidence', {})
        
        suggestions = []
        
        # Identify low-confidence fields
        for field, confidence in field_confidence.items():
            if confidence < 70.0:
                suggestions.append(f"Sprawdź pole '{field}' (pewność: {confidence:.1f}%)")
        
        # Add strategy-specific suggestions
        if processing_strategy == 'strict':
            suggestions.append("Użyto trybu ścisłego - wszystkie pola wymagają wysokiej pewności")
        elif processing_strategy == 'lenient':
            suggestions.append("Użyto trybu łagodnego - akceptowane są niższe pewności")
        
        # Store suggestions in OCR result
        if suggestions:
            if not ocr_result.error_message:
                ocr_result.error_message = ""
            
            ocr_result.error_message += f"\nSugestie do przeglądu:\n" + "\n".join(suggestions)
            ocr_result.save(update_fields=['error_message'])
            
    except Exception as e:
        logger.error(f"Failed to add manual review suggestions for OCR result {ocr_result.id}: {e}")


def create_faktura_from_ocr_manual(ocr_result_id: int, user: User, 
                                  processing_strategy: str = 'lenient') -> Faktura:
    """
    Enhanced manual Faktura creation with processing strategy support
    
    Args:
        ocr_result_id: ID of OCRResult
        user: User creating the invoice
        processing_strategy: Processing strategy for manual creation
        
    Returns:
        Faktura: Created invoice
        
    Raises:
        OCRIntegrationError: If creation fails
    """
    try:
        with transaction.atomic():
            ocr_result = OCRResult.objects.select_related('document').get(id=ocr_result_id)
            
            if ocr_result.faktura:
                raise OCRIntegrationError("OCR result już ma przypisaną fakturę")
            
            logger.info(f"Starting enhanced manual Faktura creation from OCR result {ocr_result_id} by user {user.username} using {processing_strategy} strategy")
            
            # Mark as processing for manual creation
            if ocr_result.processing_status != 'processing':
                ocr_result.mark_processing_started()
                try:
                    StatusSyncService.sync_document_status(ocr_result.document)
                except StatusSyncError as e:
                    logger.warning(f"Failed to sync document status during manual creation for OCR result {ocr_result_id}: {str(e)}")
            
            # Use enhanced creator with strategy support
            creator = FakturaCreator(user, processing_strategy)
            faktura = creator.create_from_ocr(ocr_result)
            
            # Final status sync is handled in creator.create_from_ocr()
            logger.info(f"Successfully manually created Faktura {faktura.numer} from OCR result {ocr_result_id} by user {user.username} using {processing_strategy} strategy")
            return faktura
        
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found for manual creation")
        raise OCRIntegrationError("OCR result nie istnieje")
        
    except OCRIntegrationError:
        # Re-raise OCR integration errors
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during manual Faktura creation from OCR result {ocr_result_id}: {str(e)}", exc_info=True)
        
        # Enhanced error handling for manual creation
        try:
            ocr_result = OCRResult.objects.get(id=ocr_result_id)
            
            # For manual creation, be more lenient with errors
            if processing_strategy == 'lenient' and _is_validation_error(e):
                logger.info(f"Marking OCR result {ocr_result_id} for manual review due to validation error in lenient mode")
                ocr_result.mark_manual_review_required()
                ocr_result.error_message = f"Manual creation validation error: {str(e)}"
                ocr_result.save(update_fields=['error_message'])
            else:
                ocr_result.mark_processing_failed(f"Manual creation failed: {str(e)}")
            
            StatusSyncService.sync_document_status(ocr_result.document)
        except Exception as sync_error:
            logger.error(f"Failed to update status after manual creation error for OCR result {ocr_result_id}: {str(sync_error)}")
        
        raise OCRIntegrationError(f"Nie udało się utworzyć faktury: {str(e)}")


def _is_validation_error(error: Exception) -> bool:
    """Check if error is a validation error that might be acceptable in lenient mode"""
    error_str = str(error).lower()
    validation_keywords = [
        'walidacji', 'validation', 'nieprawidłowa', 'brak wymaganego pola',
        'invalid', 'missing required field'
    ]
    
    return any(keyword in error_str for keyword in validation_keywords)


def retry_failed_ocr_processing(ocr_result_id: int, processing_strategy: str = None) -> Optional[Faktura]:
    """
    Enhanced retry processing with strategy support and intelligent fallback
    
    Args:
        ocr_result_id: ID of OCRResult to retry
        processing_strategy: Optional strategy override for retry
        
    Returns:
        Faktura: Created invoice or None if not created
        
    Raises:
        OCRIntegrationError: If retry fails
    """
    try:
        ocr_result = OCRResult.objects.select_related('document', 'document__user').get(id=ocr_result_id)
        
        if ocr_result.processing_status not in ['failed', 'manual_review', 'pending']:
            raise OCRIntegrationError(f"OCR result {ocr_result_id} is not in a retryable state (current: {ocr_result.processing_status})")
        
        # Determine retry strategy
        if not processing_strategy:
            # Intelligent strategy selection based on previous failure
            previous_error = ocr_result.error_message or ''
            if 'validation' in previous_error.lower() or 'walidacji' in previous_error.lower():
                processing_strategy = 'lenient'
            elif 'confidence' in previous_error.lower() or 'pewność' in previous_error.lower():
                processing_strategy = 'standard'
            else:
                processing_strategy = 'lenient'  # Default to lenient for retries
        
        logger.info(f"Retrying failed OCR processing for result {ocr_result_id} with {processing_strategy} strategy")
        
        # Clear previous error state
        ocr_result.error_message = None
        ocr_result.processing_status = 'pending'
        ocr_result.save(update_fields=['error_message', 'processing_status'])
        
        # Process again with strategy
        return process_ocr_result(ocr_result_id, processing_strategy)
        
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found for retry")
        raise OCRIntegrationError("OCR result nie istnieje")


def sync_ocr_document_status(ocr_result_id: int) -> bool:
    """
    Manually sync document status for an OCR result
    
    Args:
        ocr_result_id: ID of OCRResult to sync
        
    Returns:
        bool: True if sync was successful
        
    Raises:
        OCRIntegrationError: If sync fails
    """
    try:
        ocr_result = OCRResult.objects.select_related('document').get(id=ocr_result_id)
        
        logger.info(f"Manually syncing document status for OCR result {ocr_result_id}")
        
        success = StatusSyncService.sync_document_status(ocr_result.document)
        
        if success:
            logger.info(f"Successfully synced document status for OCR result {ocr_result_id}")
        else:
            logger.info(f"No status change needed for OCR result {ocr_result_id}")
        
        return success
        
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found for status sync")
        raise OCRIntegrationError("OCR result nie istnieje")
        
    except StatusSyncError as e:
        logger.error(f"Failed to sync document status for OCR result {ocr_result_id}: {str(e)}")
        raise OCRIntegrationError(f"Nie udało się zsynchronizować statusu: {str(e)}")


def get_ocr_processing_stats(user: User) -> Dict[str, Any]:
    """
    Get OCR processing statistics for user
    
    Args:
        user: User to get stats for
        
    Returns:
        Dict with processing statistics
    """
    from django.db.models import Count, Avg
    
    ocr_results = OCRResult.objects.filter(document__user=user)
    
    stats = ocr_results.aggregate(
        total_processed=Count('id'),
        avg_confidence=Avg('confidence_score'),
        auto_created_count=Count('id', filter=models.Q(auto_created_faktura=True)),
        manual_review_count=Count('id', filter=models.Q(processing_status='manual_review')),
        failed_count=Count('id', filter=models.Q(processing_status='failed')),
    )
    
    # Calculate success rate
    total = stats['total_processed'] or 0
    if total > 0:
        stats['success_rate'] = ((stats['auto_created_count'] or 0) / total) * 100
        stats['manual_review_rate'] = ((stats['manual_review_count'] or 0) / total) * 100
        stats['failure_rate'] = ((stats['failed_count'] or 0) / total) * 100
    else:
        stats['success_rate'] = 0
        stats['manual_review_rate'] = 0
        stats['failure_rate'] = 0
    
    logger.debug(f"OCR processing stats for user {user.username}: {stats}")
    return stats


def get_ocr_processing_debug_info(ocr_result_id: int) -> Dict[str, Any]:
    """
    Get detailed debug information for OCR processing
    
    Args:
        ocr_result_id: ID of OCRResult to debug
        
    Returns:
        Dict with detailed debug information
    """
    try:
        ocr_result = OCRResult.objects.select_related('document', 'document__user', 'faktura').get(id=ocr_result_id)
        
        # Get combined status from sync service
        combined_status = StatusSyncService.get_combined_status(ocr_result.document)
        
        debug_info = {
            'ocr_result_id': ocr_result.id,
            'document_id': ocr_result.document.id,
            'user_id': ocr_result.document.user.id,
            'username': ocr_result.document.user.username,
            'ocr_status': ocr_result.processing_status,
            'document_status': ocr_result.document.processing_status,
            'combined_status': combined_status,
            'confidence_score': ocr_result.confidence_score,
            'can_auto_create': ocr_result.can_auto_create_faktura,
            'needs_review': ocr_result.needs_human_review,
            'has_faktura': ocr_result.faktura is not None,
            'faktura_id': ocr_result.faktura.id if ocr_result.faktura else None,
            'auto_created': ocr_result.auto_created_faktura,
            'error_message': ocr_result.error_message,
            'created_at': ocr_result.created_at.isoformat(),
            'updated_at': ocr_result.updated_at.isoformat(),
            'document_upload_timestamp': ocr_result.document.upload_timestamp.isoformat(),
            'document_processing_started': ocr_result.document.processing_started_at.isoformat() if ocr_result.document.processing_started_at else None,
            'document_processing_completed': ocr_result.document.processing_completed_at.isoformat() if ocr_result.document.processing_completed_at else None,
            'document_error_message': ocr_result.document.error_message,
        }
        
        logger.info(f"Debug info collected for OCR result {ocr_result_id}")
        return debug_info
        
    except OCRResult.DoesNotExist:
        logger.error(f"OCR result {ocr_result_id} not found for debug info")
        return {
            'error': 'OCR result not found',
            'ocr_result_id': ocr_result_id
        }
        
    except Exception as e:
        logger.error(f"Error collecting debug info for OCR result {ocr_result_id}: {str(e)}", exc_info=True)
        return {
            'error': str(e),
            'ocr_result_id': ocr_result_id
        }


class OCRIntegrationService:
    """
    Enhanced OCR integration service with support for multiple OCR engines and processing strategies
    
    This service provides a unified interface for OCR-related operations with enhanced
    support for the new open-source OCR engine while maintaining backward compatibility.
    """
    
    def __init__(self, user: User = None, processing_strategy: str = 'standard'):
        self.user = user
        self.processing_strategy = processing_strategy
        self.ocr_service = get_ocr_service()  # Get OCR service from factory
        self.fallback_handler = OCRFallbackHandler()  # Initialize fallback handler
        
        # Security services
        self.encryption_service = get_file_encryption_service()
        self.auth_service = get_ocr_auth_service()
        self.audit_logger = get_audit_logger()
        self.cleanup_service = get_cleanup_service()
        self.premises_validator = get_premises_validator()
        
        logger.info(f"Initialized OCRIntegrationService with {processing_strategy} strategy and security enhancements")
    
    def create_faktura_from_ocr_result(self, ocr_result: OCRResult, 
                                     override_strategy: str = None) -> Faktura:
        """
        Create a Faktura from validated OCR result with enhanced processing
        
        Args:
            ocr_result: OCRResult instance with validated data
            override_strategy: Optional strategy override for this operation
            
        Returns:
            Faktura: Created invoice
            
        Raises:
            OCRIntegrationError: If creation fails
        """
        if not self.user:
            self.user = ocr_result.document.user
        
        strategy = override_strategy or self.processing_strategy
        
        try:
            # Use the enhanced FakturaCreator with strategy support
            creator = FakturaCreator(self.user, strategy)
            faktura = creator.create_from_ocr(ocr_result)
            
            logger.info(f"Successfully created Faktura {faktura.numer} from OCR result {ocr_result.id} via OCRIntegrationService using {strategy} strategy")
            return faktura
            
        except Exception as e:
            logger.error(f"Failed to create Faktura from OCR result {ocr_result.id} via OCRIntegrationService: {str(e)}", exc_info=True)
            
            # Handle creation failure with fallback mechanisms
            if ocr_result.document:
                fallback_result = self.fallback_handler.handle_processing_failure(
                    ocr_result.document.id, e, {'operation': 'faktura_creation', 'ocr_result_id': ocr_result.id}
                )
                logger.info(f"Fallback handling result: {fallback_result}")
            
            raise OCRIntegrationError(f"Failed to create invoice via OCRIntegrationService: {str(e)}")
    
    def process_document_with_ocr(self, file_content: bytes, mime_type: str, 
                                user: User = None) -> Dict[str, Any]:
        """
        Process document directly with OCR service and return results
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            user: User for processing context
            
        Returns:
            Dictionary with OCR processing results
            
        Raises:
            OCRIntegrationError: If processing fails
        """
        if not user:
            user = self.user
        
        try:
            logger.info(f"Processing document with OCR service for user {user.username if user else 'unknown'}")
            
            # Process document with OCR service
            ocr_results = self.ocr_service.process_invoice(file_content, mime_type)
            
            # Enhance results with processing metadata
            ocr_results.update({
                'processing_strategy': self.processing_strategy,
                'ocr_service_type': type(self.ocr_service).__name__,
                'processed_at': timezone.now().isoformat(),
                'user_id': user.id if user else None
            })
            
            logger.info(f"Successfully processed document with confidence {ocr_results.get('confidence_score', 0):.1f}%")
            return ocr_results
            
        except Exception as e:
            logger.error(f"Failed to process document with OCR service: {str(e)}", exc_info=True)
            raise OCRIntegrationError(f"OCR processing failed: {str(e)}")
    
    def process_document_with_fallback(self, document_id: int) -> Dict[str, Any]:
        """
        Process document with automatic fallback handling
        
        Args:
            document_id: ID of the document to process
            
        Returns:
            Dictionary with processing results and fallback information
        """
        try:
            from ..models import DocumentUpload
            document = DocumentUpload.objects.get(id=document_id)
            
            # Read document file
            with open(document.file.path, 'rb') as f:
                file_content = f.read()
            
            # Try initial processing
            try:
                result = self.process_document_with_ocr(file_content, document.file_type, document.user)
                
                return {
                    'success': True,
                    'result': result,
                    'fallback_used': False,
                    'processing_method': 'primary'
                }
                
            except Exception as processing_error:
                logger.warning(f"Primary processing failed for document {document_id}, attempting fallback")
                
                # Use fallback handler
                fallback_result = self.fallback_handler.handle_processing_failure(
                    document_id, processing_error, {'operation': 'document_processing'}
                )
                
                return {
                    'success': fallback_result.get('success', False),
                    'result': fallback_result.get('recovery_result', {}),
                    'fallback_used': True,
                    'processing_method': 'fallback',
                    'fallback_strategy': fallback_result.get('strategy'),
                    'original_error': str(processing_error)
                }
                
        except Exception as e:
            logger.error(f"Failed to process document {document_id} with fallback: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'fallback_used': False,
                'processing_method': 'failed'
            }
    
    def retry_failed_processing(self, document_id: int, retry_strategy: str = None) -> Dict[str, Any]:
        """
        Retry failed OCR processing with specific strategy
        
        Args:
            document_id: ID of the document to retry
            retry_strategy: Specific retry strategy to use
            
        Returns:
            Dictionary with retry results
        """
        try:
            from ..models import DocumentUpload
            document = DocumentUpload.objects.get(id=document_id)
            
            if document.processing_status not in ['failed', 'manual_review_required', 'retry_scheduled']:
                return {
                    'success': False,
                    'error': f"Document is not in a retryable state: {document.processing_status}"
                }
            
            # Determine retry strategy
            if not retry_strategy:
                # Let fallback handler determine strategy
                dummy_error = Exception("Manual retry requested")
                fallback_result = self.fallback_handler.handle_processing_failure(
                    document_id, dummy_error, {'operation': 'manual_retry'}
                )
                return fallback_result
            else:
                # Use specific strategy
                if retry_strategy == 'switch_engine':
                    return self._retry_with_engine_switch(document)
                else:
                    return {
                        'success': False,
                        'error': f"Unknown retry strategy: {retry_strategy}"
                    }
                    
        except Exception as e:
            logger.error(f"Failed to retry processing for document {document_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def secure_process_document(self, file_content: bytes, mime_type: str, 
                              document_id: str, user: User = None,
                              request_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Securely process document with comprehensive security features
        
        Args:
            file_content: Binary content of the document
            mime_type: MIME type of the document
            document_id: Unique document identifier
            user: User performing the operation
            request_metadata: Additional request metadata (IP, user agent, etc.)
            
        Returns:
            Dictionary with processing results and security metadata
        """
        if not user:
            user = self.user
        
        if not user:
            raise OCRSecurityError("User authentication required for secure processing")
        
        processing_start = timezone.now()
        security_context = {
            'document_id': document_id,
            'user_id': user.id,
            'processing_start': processing_start.isoformat(),
            'request_metadata': request_metadata or {}
        }
        
        try:
            # 1. Validate on-premises processing
            processing_config = {
                'service_url': getattr(self.ocr_service, 'service_url', 'local'),
                'engines': getattr(self.ocr_service, 'engines', ['tesseract', 'easyocr'])
            }
            
            if not self.premises_validator.validate_processing_location(processing_config):
                raise OCRSecurityError("Processing configuration violates on-premises requirement")
            
            # 2. Generate OCR token for this session
            ocr_token = self.auth_service.generate_ocr_token(user, document_id)
            security_context['ocr_token'] = ocr_token[:16] + '...'  # Log partial token only
            
            # 3. Encrypt and store file temporarily
            encrypted_path, encryption_metadata = self.encryption_service.encrypt_file(
                file_content, document_id, 'original'
            )
            security_context['encrypted_file'] = encrypted_path
            
            # 4. Log document upload
            file_info = {
                'size': len(file_content),
                'mime_type': mime_type,
                'ip_address': request_metadata.get('ip_address'),
                'user_agent': request_metadata.get('user_agent')
            }
            self.audit_logger.log_document_upload(user, document_id, file_info, True)
            
            # 5. Log processing start
            self.audit_logger.log_processing_start(user, document_id, processing_config)
            
            # 6. Perform OCR processing
            try:
                ocr_results = self.process_document_with_ocr(file_content, mime_type, user)
                processing_success = True
            except Exception as processing_error:
                logger.error(f"OCR processing failed for document {document_id}: {processing_error}")
                
                # Try fallback processing
                fallback_result = self.fallback_handler.handle_processing_failure(
                    document_id, processing_error, {'operation': 'secure_processing'}
                )
                
                if fallback_result.get('success'):
                    ocr_results = fallback_result.get('recovery_result', {})
                    processing_success = True
                    security_context['fallback_used'] = True
                else:
                    processing_success = False
                    ocr_results = {'error': str(processing_error)}
            
            # 7. Log processing completion
            result_summary = {
                'confidence_score': ocr_results.get('confidence_score', 0),
                'processing_time': (timezone.now() - processing_start).total_seconds(),
                'fields_extracted': len(ocr_results.get('extracted_data', {})),
                'success': processing_success
            }
            self.audit_logger.log_processing_complete(user, document_id, result_summary)
            
            # 8. Secure cleanup of temporary files
            cleanup_result = self.cleanup_service.cleanup_document_files(
                document_id, 'processing_complete'
            )
            security_context['cleanup_result'] = cleanup_result
            
            # 9. Prepare secure response
            secure_response = {
                'success': processing_success,
                'document_id': document_id,
                'processing_time': result_summary['processing_time'],
                'confidence_score': result_summary['confidence_score'],
                'data_location': 'on_premises',
                'security_validated': True,
                'encryption_used': True,
                'audit_logged': True,
                'cleanup_completed': cleanup_result.get('files_deleted', 0) > 0
            }
            
            if processing_success:
                # Only include extracted data if processing was successful
                secure_response['extracted_data'] = ocr_results.get('extracted_data', {})
                secure_response['raw_text'] = ocr_results.get('raw_text', '')
                secure_response['processor_version'] = ocr_results.get('processor_version', 'opensource')
            else:
                secure_response['error'] = ocr_results.get('error', 'Processing failed')
            
            # Add security metadata
            secure_response['security_context'] = {
                'processing_location': 'on_premises',
                'encryption_applied': True,
                'audit_trail_created': True,
                'secure_cleanup_performed': True,
                'authentication_validated': True
            }
            
            logger.info(f"Secure OCR processing completed for document {document_id} with confidence {result_summary['confidence_score']:.1f}%")
            return secure_response
            
        except OCRSecurityError as e:
            # Log security violation
            self.audit_logger.log_security_event(
                'secure_processing_violation',
                {
                    'document_id': document_id,
                    'user_id': user.id,
                    'error': str(e),
                    'security_context': security_context
                },
                severity='error'
            )
            
            # Ensure cleanup even on security error
            try:
                self.cleanup_service.cleanup_document_files(document_id, 'security_error')
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed after security error: {cleanup_error}")
            
            raise
            
        except Exception as e:
            logger.error(f"Secure OCR processing failed for document {document_id}: {e}")
            
            # Log processing failure
            self.audit_logger.log_processing_complete(user, document_id, {
                'success': False,
                'error': str(e),
                'processing_time': (timezone.now() - processing_start).total_seconds()
            })
            
            # Ensure cleanup on any error
            try:
                self.cleanup_service.cleanup_document_files(document_id, 'processing_error')
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed after processing error: {cleanup_error}")
            
            return {
                'success': False,
                'error': str(e),
                'document_id': document_id,
                'security_validated': False,
                'cleanup_attempted': True
            }
    
    def get_manual_review_queue(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get documents pending manual review for the current user
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of documents pending manual review
        """
        return ManualReviewQueue.get_pending_reviews(user=self.user, limit=limit)
    
    def complete_manual_review(self, document_id: int, corrected_data: Dict[str, Any], 
                             approved: bool = True) -> Dict[str, Any]:
        """
        Complete manual review of a document
        
        Args:
            document_id: ID of the document being reviewed
            corrected_data: Corrected OCR data
            approved: Whether the document is approved
            
        Returns:
            Dictionary with review completion results
        """
        if not self.user:
            return {
                'success': False,
                'error': 'User required for manual review completion'
            }
        
        return ManualReviewQueue.complete_manual_review(
            document_id, self.user, corrected_data, approved
        )
    
    def _retry_with_engine_switch(self, document) -> Dict[str, Any]:
        """Retry processing with a different OCR engine"""
        try:
            # Get current engine and switch to alternative
            current_engine = getattr(document, 'preferred_engine', 'opensource')
            
            # Try switching engines
            from .ocr_service_factory import OCRServiceFactory
            
            # Get available engines
            available_engines = ['opensource', 'tesseract', 'easyocr']
            
            for engine in available_engines:
                if engine != current_engine:
                    try:
                        # Switch to new engine
                        OCRServiceFactory.switch_implementation(engine)
                        new_service = OCRServiceFactory.get_service()
                        
                        # Try processing with new engine
                        with open(document.file.path, 'rb') as f:
                            file_content = f.read()
                        
                        result = new_service.process_invoice(file_content, document.file_type)
                        
                        # Update document with new engine preference
                        document.preferred_engine = engine
                        document.processing_status = 'completed'
                        document.save()
                        
                        logger.info(f"Successfully switched to engine {engine} for document {document.id}")
                        
                        return {
                            'success': True,
                            'new_engine': engine,
                            'result': result,
                            'action': 'engine_switched'
                        }
                        
                    except Exception as e:
                        logger.warning(f"Engine {engine} failed for document {document.id}: {e}")
                        continue
            
            return {
                'success': False,
                'error': 'All available engines failed',
                'action': 'all_engines_failed'
            }
            
        except Exception as e:
            logger.error(f"Failed to retry with engine switch for document {document.id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'action': 'retry_failed'
            }
    
    def _retry_with_preprocessing(self, document) -> Dict[str, Any]:
        """Retry processing with different preprocessing settings"""
        try:
            # Try different preprocessing configurations
            preprocessing_configs = [
                {'deskew': True, 'denoise': True, 'enhance_contrast': True},
                {'deskew': True, 'denoise': False, 'enhance_contrast': True, 'sharpen': True},
                {'deskew': False, 'denoise': True, 'enhance_contrast': False, 'blur_reduction': True},
                {'minimal_processing': True}
            ]
            
            current_attempt = getattr(document, 'retry_count', 0)
            
            if current_attempt >= len(preprocessing_configs):
                return {
                    'success': False,
                    'error': 'All preprocessing strategies exhausted',
                    'action': 'preprocessing_exhausted'
                }
            
            config = preprocessing_configs[current_attempt]
            
            # Apply preprocessing and retry
            from .image_preprocessor import ImagePreprocessor
            preprocessor = ImagePreprocessor()
            
            with open(document.file.path, 'rb') as f:
                file_content = f.read()
            
            processed_content = preprocessor.preprocess_document(
                file_content, document.file_type, **config
            )
            
            # Process with current OCR service
            result = self.ocr_service.process_invoice(processed_content, document.file_type)
            
            # Update document
            document.retry_count = current_attempt + 1
            document.processing_status = 'completed'
            document.save()
            
            logger.info(f"Successfully retried document {document.id} with preprocessing config {current_attempt + 1}")
            
            return {
                'success': True,
                'preprocessing_config': config,
                'attempt': current_attempt + 1,
                'result': result,
                'action': 'preprocessing_retry_success'
            }
            
        except Exception as e:
            logger.error(f"Failed to retry with preprocessing for document {document.id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'action': 'preprocessing_retry_failed'
            }
    
    def _attempt_partial_processing(self, document) -> Dict[str, Any]:
        """Attempt to extract partial data from failed processing"""
        try:
            # Get existing OCR result if any
            ocr_result = OCRResult.objects.filter(document=document).first()
            
            if not ocr_result or not ocr_result.extracted_data:
                return {
                    'success': False,
                    'error': 'No partial data available',
                    'action': 'no_partial_data'
                }
            
            # Check if we have minimum required data
            extracted_data = ocr_result.extracted_data
            required_fields = ['numer_faktury', 'data_wystawienia', 'sprzedawca_nazwa']
            available_fields = [field for field in required_fields if extracted_data.get(field)]
            
            if len(available_fields) >= 2:
                # Accept partial processing
                ocr_result.processing_status = 'partial_success'
                ocr_result.manual_verification_required = True
                ocr_result.save()
                
                document.processing_status = 'partial_success'
                document.save()
                
                return {
                    'success': True,
                    'available_fields': available_fields,
                    'requires_manual_verification': True,
                    'action': 'partial_success_accepted'
                }
            else:
                return {
                    'success': False,
                    'error': f'Insufficient data for partial processing. Available fields: {available_fields}',
                    'action': 'insufficient_partial_data'
                }
                
        except Exception as e:
            logger.error(f"Failed to attempt partial processing for document {document.id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'action': 'partial_processing_failed'
            }
    
    def validate_ocr_result(self, ocr_result: OCRResult, corrections: dict, 
                          validation_notes: str = "", user: User = None) -> dict:
        """
        Enhanced validation with support for multiple OCR engine formats
        
        Args:
            ocr_result: OCRResult instance to validate
            corrections: Dictionary of field corrections
            validation_notes: Optional notes about validation
            user: User performing validation (defaults to self.user)
            
        Returns:
            dict: Enhanced validation results with engine-specific handling
        """
        if not user:
            user = self.user or ocr_result.document.user
        
        try:
            # Detect OCR engine type for proper validation
            engine_type = self._detect_ocr_engine_type(ocr_result)
            
            # Normalize corrections based on engine type
            normalized_corrections = self._normalize_corrections(corrections, engine_type)
            
            # Apply corrections using the OCRResult model method
            result = ocr_result.apply_manual_corrections(normalized_corrections, validated_by=user)
            
            # Re-validate with enhanced validator
            is_valid, validation_errors = OCRDataValidator.validate_ocr_data(
                ocr_result.extracted_data,
                ocr_result.confidence_score,
                engine_type
            )
            
            # Create validation record with enhanced metadata
            validation_record = self._create_validation_record(
                ocr_result, normalized_corrections, validation_notes, user, engine_type
            )
            
            logger.info(f"Successfully validated OCR result {ocr_result.id} with {len(corrections)} corrections using {engine_type} engine")
            
            return {
                'ocr_result_id': ocr_result.id,
                'updated_fields': result['updated_fields'],
                'new_confidence_scores': result['new_confidence_scores'],
                'overall_confidence': ocr_result.confidence_score,
                'validation_id': validation_record.id if validation_record else None,
                'can_create_faktura': ocr_result.can_create_faktura(),
                'engine_type': engine_type,
                'is_valid_after_corrections': is_valid,
                'validation_errors': validation_errors,
                'processing_strategy': self.processing_strategy
            }
            
        except Exception as e:
            logger.error(f"Failed to validate OCR result {ocr_result.id}: {str(e)}", exc_info=True)
            raise OCRIntegrationError(f"Failed to validate OCR result: {str(e)}")
    
    def get_processing_recommendations(self, ocr_result: OCRResult) -> Dict[str, Any]:
        """
        Get processing recommendations based on OCR result analysis
        
        Args:
            ocr_result: OCRResult to analyze
            
        Returns:
            Dictionary with processing recommendations
        """
        try:
            engine_type = self._detect_ocr_engine_type(ocr_result)
            confidence_thresholds = _get_confidence_thresholds(self.processing_strategy)
            
            recommendations = {
                'engine_type': engine_type,
                'confidence_score': ocr_result.confidence_score,
                'processing_strategy': self.processing_strategy,
                'recommended_action': self._get_recommended_action(ocr_result, confidence_thresholds),
                'field_analysis': self._analyze_field_confidence(ocr_result),
                'validation_suggestions': self._get_validation_suggestions(ocr_result),
                'alternative_strategies': self._get_alternative_strategies(ocr_result)
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get processing recommendations for OCR result {ocr_result.id}: {str(e)}")
            return {
                'error': str(e),
                'ocr_result_id': ocr_result.id
            }
    
    def _detect_ocr_engine_type(self, ocr_result: OCRResult) -> str:
        """Detect OCR engine type from OCR result metadata"""
        processor_version = ocr_result.processor_version or ''
        
        if 'opensource' in processor_version.lower():
            return 'opensource'
        elif 'google' in processor_version.lower() or 'document-ai' in processor_version.lower():
            return 'google'
        else:
            # Try to detect from data structure
            extracted_data = ocr_result.extracted_data or {}
            
            # Check for Google Cloud Document AI specific fields
            if 'entities' in extracted_data or 'pages' in extracted_data:
                return 'google'
            
            # Check for open source specific fields
            if 'raw_ocr_results' in extracted_data or 'processing_steps' in extracted_data:
                return 'opensource'
            
            # Default to opensource for new implementation
            return 'opensource'
    
    def _normalize_corrections(self, corrections: dict, engine_type: str) -> dict:
        """Normalize corrections based on OCR engine type"""
        if engine_type == 'google':
            # Google format corrections
            field_mapping = {
                'invoice_number': 'numer_faktury',
                'invoice_date': 'data_wystawienia',
                'supplier_name': 'sprzedawca_nazwa',
                'buyer_name': 'nabywca_nazwa',
                'total_amount': 'suma_brutto'
            }
        else:
            # Open source format corrections
            field_mapping = {
                'invoice_number': 'numer_faktury',
                'invoice_date': 'data_wystawienia',
                'supplier_name': 'sprzedawca_nazwa',
                'buyer_name': 'nabywca_nazwa',
                'total_amount': 'suma_brutto'
            }
        
        normalized = {}
        for field, value in corrections.items():
            # Map field names if needed
            normalized_field = field_mapping.get(field, field)
            normalized[normalized_field] = value
        
        return normalized
    
    def _get_recommended_action(self, ocr_result: OCRResult, confidence_thresholds: Dict[str, float]) -> str:
        """Get recommended action based on confidence score"""
        confidence = ocr_result.confidence_score
        
        if confidence >= confidence_thresholds['auto_create']:
            return 'auto_create'
        elif confidence >= confidence_thresholds['manual_review']:
            return 'manual_review'
        elif confidence >= confidence_thresholds['minimum']:
            return 'manual_validation'
        else:
            return 'reprocess_or_reject'
    
    def _analyze_field_confidence(self, ocr_result: OCRResult) -> Dict[str, Any]:
        """Analyze field-level confidence scores"""
        extracted_data = ocr_result.extracted_data or {}
        field_confidence = extracted_data.get('field_confidence', {})
        
        analysis = {
            'high_confidence_fields': [],
            'medium_confidence_fields': [],
            'low_confidence_fields': [],
            'missing_confidence_fields': []
        }
        
        for field, value in extracted_data.items():
            if field == 'field_confidence':
                continue
                
            confidence = field_confidence.get(field, ocr_result.confidence_score)
            
            if confidence >= 90.0:
                analysis['high_confidence_fields'].append({'field': field, 'confidence': confidence})
            elif confidence >= 70.0:
                analysis['medium_confidence_fields'].append({'field': field, 'confidence': confidence})
            elif confidence >= 50.0:
                analysis['low_confidence_fields'].append({'field': field, 'confidence': confidence})
            else:
                analysis['missing_confidence_fields'].append({'field': field, 'confidence': confidence})
        
        return analysis
    
    def _get_validation_suggestions(self, ocr_result: OCRResult) -> list:
        """Get validation suggestions based on OCR result analysis"""
        suggestions = []
        extracted_data = ocr_result.extracted_data or {}
        field_confidence = extracted_data.get('field_confidence', {})
        
        # Check for common validation issues
        if not extracted_data.get('numer_faktury'):
            suggestions.append("Sprawdź numer faktury - może być nieczytelny")
        
        if field_confidence.get('data_wystawienia', 0) < 70:
            suggestions.append("Zweryfikuj datę wystawienia")
        
        if field_confidence.get('suma_brutto', 0) < 80:
            suggestions.append("Sprawdź kwotę brutto - może wymagać korekty")
        
        if not extracted_data.get('sprzedawca_nip'):
            suggestions.append("Dodaj NIP sprzedawcy jeśli jest dostępny")
        
        return suggestions
    
    def _get_alternative_strategies(self, ocr_result: OCRResult) -> list:
        """Get alternative processing strategies"""
        current_strategy = self.processing_strategy
        confidence = ocr_result.confidence_score
        
        alternatives = []
        
        if current_strategy == 'strict' and confidence < 95:
            alternatives.append({
                'strategy': 'standard',
                'reason': 'Niższa pewność - spróbuj standardowego trybu'
            })
        
        if current_strategy in ['strict', 'standard'] and confidence < 80:
            alternatives.append({
                'strategy': 'lenient',
                'reason': 'Bardzo niska pewność - spróbuj łagodnego trybu'
            })
        
        if confidence < 60:
            alternatives.append({
                'strategy': 'manual_processing',
                'reason': 'Bardzo niska pewność - rozważ ręczne przetwarzanie'
            })
        
        return alternatives
    
    def _create_validation_record(self, ocr_result: OCRResult, corrections: dict, 
                                notes: str, user: User, engine_type: str) -> Optional['OCRValidation']:
        """
        Create enhanced validation record with engine-specific metadata
        
        Args:
            ocr_result: OCRResult instance
            corrections: Applied corrections
            notes: Validation notes
            user: User who performed validation
            engine_type: Type of OCR engine used
            
        Returns:
            OCRValidation instance or None
        """
        try:
            from ..models import OCRValidation
            
            # Check if validation record already exists (OneToOne relationship)
            validation_record, created = OCRValidation.objects.get_or_create(
                ocr_result=ocr_result,
                defaults={
                    'validated_by': user,
                    'validation_notes': notes,
                    'corrections_applied': corrections,
                    'validation_timestamp': timezone.now(),
                    'engine_type': engine_type,
                    'processing_strategy': self.processing_strategy
                }
            )
            
            if not created:
                # Update existing record
                validation_record.validated_by = user
                validation_record.validation_notes = notes
                validation_record.corrections_applied = corrections
                validation_record.validation_timestamp = timezone.now()
                validation_record.engine_type = engine_type
                validation_record.processing_strategy = self.processing_strategy
                validation_record.save()
            
            return validation_record
            
        except Exception as e:
            logger.error(f"Failed to create validation record for OCR result {ocr_result.id}: {str(e)}")
            return None


def get_ocr_engine_capabilities() -> Dict[str, Any]:
    """
    Get capabilities and status of available OCR engines
    
    Returns:
        Dictionary with OCR engine capabilities and status
    """
    try:
        from .ocr_service_factory import OCRServiceFactory
        
        service_info = OCRServiceFactory.get_service_info()
        
        # Get current OCR service
        current_service = get_ocr_service()
        
        capabilities = {
            'current_implementation': service_info['current_implementation'],
            'available_implementations': service_info['available_implementations'],
            'google_cloud_available': service_info['google_cloud_available'],
            'opensource_available': service_info['opensource_available'],
            'current_service_type': type(current_service).__name__,
            'processor_available': current_service.validate_processor_availability() if hasattr(current_service, 'validate_processor_availability') else True,
            'supported_formats': ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'],
            'supported_languages': ['pl', 'en'],
            'processing_strategies': ['strict', 'standard', 'lenient'],
            'confidence_thresholds': {
                'strict': _get_confidence_thresholds('strict'),
                'standard': _get_confidence_thresholds('standard'),
                'lenient': _get_confidence_thresholds('lenient')
            }
        }
        
        return capabilities
        
    except Exception as e:
        logger.error(f"Failed to get OCR engine capabilities: {str(e)}")
        return {
            'error': str(e),
            'current_implementation': 'unknown',
            'available_implementations': [],
            'processor_available': False
        }


def switch_ocr_engine(implementation: str) -> Dict[str, Any]:
    """
    Switch OCR engine implementation
    
    Args:
        implementation: Target implementation ('google', 'opensource', 'mock')
        
    Returns:
        Dictionary with switch results
    """
    try:
        from .ocr_service_factory import OCRServiceFactory
        
        logger.info(f"Attempting to switch OCR engine to {implementation}")
        
        success = OCRServiceFactory.switch_implementation(implementation)
        
        if success:
            # Clear any cached services
            OCRServiceFactory.clear_cache()
            
            # Verify the switch
            new_service = get_ocr_service()
            
            result = {
                'success': True,
                'new_implementation': implementation,
                'service_type': type(new_service).__name__,
                'processor_available': new_service.validate_processor_availability() if hasattr(new_service, 'validate_processor_availability') else True,
                'message': f"Successfully switched to {implementation} OCR engine"
            }
        else:
            result = {
                'success': False,
                'error': f"Failed to switch to {implementation} - implementation not available",
                'current_implementation': OCRServiceFactory._get_configured_implementation()
            }
        
        logger.info(f"OCR engine switch result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error switching OCR engine to {implementation}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'current_implementation': 'unknown'
        }


def get_processing_strategy_recommendations(ocr_result: OCRResult) -> Dict[str, Any]:
    """
    Get processing strategy recommendations for an OCR result
    
    Args:
        ocr_result: OCRResult to analyze
        
    Returns:
        Dictionary with strategy recommendations
    """
    try:
        confidence = ocr_result.confidence_score
        extracted_data = ocr_result.extracted_data or {}
        field_confidence = extracted_data.get('field_confidence', {})
        
        recommendations = {
            'ocr_result_id': ocr_result.id,
            'overall_confidence': confidence,
            'recommended_strategies': [],
            'field_analysis': {},
            'risk_assessment': 'low'
        }
        
        # Analyze field confidence
        low_confidence_fields = []
        for field, field_conf in field_confidence.items():
            if field_conf < 70.0:
                low_confidence_fields.append({'field': field, 'confidence': field_conf})
        
        recommendations['field_analysis'] = {
            'total_fields': len(field_confidence),
            'low_confidence_fields': low_confidence_fields,
            'low_confidence_count': len(low_confidence_fields)
        }
        
        # Determine risk assessment
        if confidence < 60.0 or len(low_confidence_fields) > 3:
            recommendations['risk_assessment'] = 'high'
        elif confidence < 80.0 or len(low_confidence_fields) > 1:
            recommendations['risk_assessment'] = 'medium'
        
        # Strategy recommendations
        if confidence >= 95.0:
            recommendations['recommended_strategies'] = [
                {'strategy': 'strict', 'reason': 'Bardzo wysoka pewność - bezpieczne użycie trybu ścisłego'},
                {'strategy': 'standard', 'reason': 'Alternatywnie standardowy tryb'}
            ]
        elif confidence >= 85.0:
            recommendations['recommended_strategies'] = [
                {'strategy': 'standard', 'reason': 'Wysoka pewność - standardowy tryb zalecany'},
                {'strategy': 'strict', 'reason': 'Tryb ścisły możliwy ale może być zbyt restrykcyjny'}
            ]
        elif confidence >= 70.0:
            recommendations['recommended_strategies'] = [
                {'strategy': 'standard', 'reason': 'Średnia pewność - standardowy tryb zalecany'},
                {'strategy': 'lenient', 'reason': 'Tryb łagodny jako alternatywa'}
            ]
        else:
            recommendations['recommended_strategies'] = [
                {'strategy': 'lenient', 'reason': 'Niska pewność - tylko tryb łagodny zalecany'},
                {'strategy': 'manual_processing', 'reason': 'Rozważ ręczne przetwarzanie'}
            ]
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Failed to get strategy recommendations for OCR result {ocr_result.id}: {str(e)}")
        return {
            'error': str(e),
            'ocr_result_id': ocr_result.id,
            'recommended_strategies': [{'strategy': 'standard', 'reason': 'Błąd analizy - użyj standardowego trybu'}]
        }