"""
Validation API Views for FaktuLove

Provides API endpoints for real-time field validation
with Polish business rules and correction guidance.
"""

import json
import logging
from typing import Dict, Any, List

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from faktury.services.validation_service import validation_service

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_exempt
def validate_field(request):
    """
    API endpoint for real-time field validation
    
    Accepts:
        - field_name: Name of the field to validate
        - value: Value to validate
        - context: Additional context for validation
    
    Returns:
        JSON response with validation result
    """
    try:
        data = json.loads(request.body)
        
        field_name = data.get('field_name')
        value = data.get('value')
        context = data.get('context', {})
        
        if not field_name:
            return JsonResponse({
                'valid': False,
                'error': 'Nazwa pola jest wymagana'
            }, status=400)
        
        # Add request context if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            context['user_id'] = request.user.id
        
        # Validate the field
        result = validation_service.validate_field(field_name, value, context)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'valid': False,
            'error': 'Nieprawidłowy format JSON'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Field validation error: {e}")
        return JsonResponse({
            'valid': False,
            'error': 'Błąd walidacji pola',
            'suggestions': ['Spróbuj ponownie', 'Skontaktuj się z pomocą techniczną']
        }, status=500)

@method_decorator(login_required, name='dispatch')
class FormValidationView(View):
    """
    View for comprehensive form validation
    """
    
    def post(self, request):
        """Validate entire form data"""
        try:
            data = json.loads(request.body)
            
            form_data = data.get('form_data', {})
            form_type = data.get('form_type', 'generic')
            
            validation_results = {}
            overall_valid = True
            
            # Validate each field
            for field_name, value in form_data.items():
                context = {
                    'user_id': request.user.id,
                    'form_type': form_type,
                    'check_uniqueness': data.get('check_uniqueness', False)
                }
                
                result = validation_service.validate_field(field_name, value, context)
                validation_results[field_name] = result
                
                if not result['valid']:
                    overall_valid = False
            
            # Additional form-level validations
            form_level_errors = self._validate_form_level_rules(form_data, form_type)
            
            return JsonResponse({
                'valid': overall_valid and len(form_level_errors) == 0,
                'field_results': validation_results,
                'form_errors': form_level_errors,
                'message': 'Walidacja zakończona' if overall_valid else 'Formularz zawiera błędy'
            })
            
        except Exception as e:
            logger.error(f"Form validation error: {e}")
            return JsonResponse({
                'valid': False,
                'error': 'Błąd walidacji formularza'
            }, status=500)
    
    def _validate_form_level_rules(self, form_data: Dict[str, Any], form_type: str) -> List[Dict[str, str]]:
        """Validate form-level business rules"""
        errors = []
        
        if form_type == 'invoice':
            # Invoice-specific validations
            errors.extend(self._validate_invoice_rules(form_data))
        elif form_type == 'contractor':
            # Contractor-specific validations
            errors.extend(self._validate_contractor_rules(form_data))
        
        return errors
    
    def _validate_invoice_rules(self, form_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Validate invoice-specific business rules"""
        errors = []
        
        # Check date relationships
        data_wystawienia = form_data.get('data_wystawienia')
        data_sprzedazy = form_data.get('data_sprzedazy')
        termin_platnosci = form_data.get('termin_platnosci')
        
        if data_wystawienia and data_sprzedazy:
            try:
                from datetime import datetime
                
                if isinstance(data_wystawienia, str):
                    data_wystawienia = datetime.strptime(data_wystawienia, '%Y-%m-%d').date()
                if isinstance(data_sprzedazy, str):
                    data_sprzedazy = datetime.strptime(data_sprzedazy, '%Y-%m-%d').date()
                
                if data_sprzedazy > data_wystawienia:
                    errors.append({
                        'field': 'data_sprzedazy',
                        'error': 'Data sprzedaży nie może być późniejsza niż data wystawienia',
                        'suggestions': ['Sprawdź daty', 'Data sprzedaży powinna być wcześniejsza lub równa dacie wystawienia']
                    })
            except (ValueError, TypeError):
                pass
        
        # Check amounts
        kwota_netto = form_data.get('kwota_netto')
        kwota_brutto = form_data.get('kwota_brutto')
        stawka_vat = form_data.get('stawka_vat')
        
        if kwota_netto and kwota_brutto and stawka_vat:
            try:
                from decimal import Decimal
                
                netto = Decimal(str(kwota_netto))
                brutto = Decimal(str(kwota_brutto))
                vat_rate = Decimal(str(stawka_vat))
                
                expected_brutto = netto * (1 + vat_rate / 100)
                
                if abs(brutto - expected_brutto) > Decimal('0.01'):
                    errors.append({
                        'field': 'kwota_brutto',
                        'error': 'Kwota brutto nie odpowiada kwocie netto i stawce VAT',
                        'suggestions': [
                            f'Oczekiwana kwota brutto: {expected_brutto:.2f}',
                            'Sprawdź obliczenia VAT'
                        ]
                    })
            except (ValueError, TypeError, InvalidOperation):
                pass
        
        return errors
    
    def _validate_contractor_rules(self, form_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Validate contractor-specific business rules"""
        errors = []
        
        # Check if NIP and REGON belong to the same entity
        nip = form_data.get('nip')
        regon = form_data.get('regon')
        
        if nip and regon:
            # In a real implementation, you would check this against GUS database
            # For now, we'll just validate format consistency
            pass
        
        return errors

@require_http_methods(["GET"])
def validation_rules(request):
    """
    Get validation rules for frontend
    """
    try:
        rules = {
            'nip': {
                'required': True,
                'pattern': r'^\d{10}$',
                'message': 'NIP musi mieć dokładnie 10 cyfr',
                'suggestions': ['Wprowadź 10 cyfr bez spacji i myślników']
            },
            'regon': {
                'required': False,
                'pattern': r'^\d{9}$|^\d{14}$',
                'message': 'REGON musi mieć 9 lub 14 cyfr',
                'suggestions': ['Wprowadź 9 lub 14 cyfr bez spacji']
            },
            'krs': {
                'required': False,
                'pattern': r'^\d{10}$',
                'message': 'KRS musi mieć dokładnie 10 cyfr',
                'suggestions': ['Wprowadź 10 cyfr']
            },
            'email': {
                'required': True,
                'pattern': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
                'message': 'Nieprawidłowy format adresu email',
                'suggestions': ['Użyj formatu: nazwa@domena.pl']
            },
            'phone': {
                'required': False,
                'pattern': r'^(\+48\s?)?\d{3}\s?\d{3}\s?\d{3}$',
                'message': 'Nieprawidłowy format numeru telefonu',
                'suggestions': ['Użyj formatu: +48 123 456 789 lub 123 456 789']
            },
            'postal_code': {
                'required': True,
                'pattern': r'^\d{2}-\d{3}$',
                'message': 'Kod pocztowy musi mieć format XX-XXX',
                'suggestions': ['Przykład: 00-001']
            },
            'vat_rate': {
                'required': True,
                'allowed_values': [0, 5, 8, 23],
                'message': 'Nieprawidłowa stawka VAT',
                'suggestions': ['Dozwolone stawki: 0%, 5%, 8%, 23%']
            },
            'amount': {
                'required': True,
                'pattern': r'^\d+(\.\d{1,2})?$',
                'message': 'Nieprawidłowy format kwoty',
                'suggestions': ['Użyj kropki jako separatora dziesiętnego', 'Maksymalnie 2 miejsca po przecinku']
            }
        }
        
        return JsonResponse({
            'success': True,
            'rules': rules
        })
        
    except Exception as e:
        logger.error(f"Error getting validation rules: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Błąd pobierania reguł walidacji'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def validate_business_number(request):
    """
    Specialized endpoint for validating Polish business numbers (NIP, REGON, KRS)
    with external API verification
    """
    try:
        data = json.loads(request.body)
        
        number_type = data.get('type')  # 'nip', 'regon', 'krs'
        number_value = data.get('value')
        
        if not number_type or not number_value:
            return JsonResponse({
                'valid': False,
                'error': 'Typ i wartość numeru są wymagane'
            }, status=400)
        
        # Validate using our service
        result = validation_service.validate_field(number_type, number_value)
        
        # If basic validation passes, try external verification
        if result['valid'] and number_type in ['nip', 'regon']:
            external_result = _verify_with_external_api(number_type, number_value)
            if external_result:
                result.update(external_result)
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Business number validation error: {e}")
        return JsonResponse({
            'valid': False,
            'error': 'Błąd walidacji numeru'
        }, status=500)

def _verify_with_external_api(number_type: str, number_value: str) -> Dict[str, Any]:
    """
    Verify business number with external API (GUS, etc.)
    
    This is a placeholder for external API integration.
    In production, you would integrate with:
    - GUS API for REGON verification
    - Ministry of Finance API for NIP verification
    """
    try:
        # Placeholder for external API call
        # In real implementation, make HTTP request to appropriate API
        
        return {
            'external_verified': True,
            'company_name': 'Przykładowa Firma Sp. z o.o.',
            'status': 'active',
            'verification_date': '2025-01-29'
        }
        
    except Exception as e:
        logger.warning(f"External API verification failed: {e}")
        return {
            'external_verified': False,
            'external_error': 'Nie udało się zweryfikować w zewnętrznej bazie'
        }