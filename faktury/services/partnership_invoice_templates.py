"""
Partnership Invoice Templates Service
"""
import logging
from typing import List, Dict, Optional, Any
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from ..models import Firma, Kontrahent, Partnerstwo, Faktura, PozycjaFaktury, Produkt

logger = logging.getLogger(__name__)


class PartnershipInvoiceTemplateService:
    """
    Service for managing partnership-specific invoice templates and workflows
    """
    
    def __init__(self):
        self.logger = logger
    
    def create_invoice_template(self, partnership: Partnerstwo, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive invoice template for partnership
        """
        try:
            template = {
                'id': f"template_{partnership.id}_{timezone.now().timestamp()}",
                'partnership_id': partnership.id,
                'name': template_data.get('name', f'Template for {partnership.firma2.nazwa}'),
                'description': template_data.get('description', ''),
                'created_at': timezone.now(),
                'updated_at': timezone.now(),
                
                # Invoice settings
                'invoice_settings': {
                    'typ_dokumentu': template_data.get('typ_dokumentu', 'FV'),
                    'payment_terms_days': template_data.get('payment_terms', 14),
                    'payment_method': template_data.get('payment_method', 'przelew'),
                    'currency': template_data.get('currency', 'PLN'),
                    'place_of_issue': template_data.get('place_of_issue', partnership.firma1.miejscowosc),
                },
                
                # Template items
                'default_items': template_data.get('default_items', []),
                
                # Automation settings
                'automation': {
                    'auto_generate': template_data.get('auto_generate', False),
                    'generation_frequency': template_data.get('generation_frequency', 'monthly'),
                    'generation_day': template_data.get('generation_day', 1),
                    'next_generation_date': template_data.get('next_generation_date'),
                    'auto_send': template_data.get('auto_send', False),
                    'auto_remind': template_data.get('auto_remind', False),
                    'reminder_days': template_data.get('reminder_days', [7, 3, 1]),
                },
                
                # Customization settings
                'customization': {
                    'include_logo': template_data.get('include_logo', True),
                    'custom_header': template_data.get('custom_header', ''),
                    'custom_footer': template_data.get('custom_footer', ''),
                    'custom_notes': template_data.get('custom_notes', ''),
                    'color_scheme': template_data.get('color_scheme', 'default'),
                },
                
                # Discount and pricing
                'pricing': {
                    'global_discount_type': template_data.get('discount_type', 'percentage'),
                    'global_discount_value': template_data.get('discount_value', 0),
                    'apply_discount_to': template_data.get('apply_discount_to', 'net'),
                    'rounding_precision': template_data.get('rounding_precision', 2),
                },
                
                # Validation rules
                'validation': {
                    'require_approval': template_data.get('require_approval', False),
                    'approval_threshold': template_data.get('approval_threshold', 0),
                    'validate_items': template_data.get('validate_items', True),
                    'validate_totals': template_data.get('validate_totals', True),
                }
            }
            
            # Validate template data
            validation_errors = self._validate_template_data(template)
            if validation_errors:
                raise ValidationError(validation_errors)
            
            self.logger.info(f"Created invoice template for partnership {partnership.id}")
            return template
            
        except Exception as e:
            self.logger.error(f"Error creating invoice template: {str(e)}")
            raise
    
    def generate_invoice_from_template(self, template: Dict[str, Any], generation_date: Optional[date] = None) -> Faktura:
        """
        Generate invoice from template
        """
        try:
            partnership = Partnerstwo.objects.get(id=template['partnership_id'])
            
            if not generation_date:
                generation_date = date.today()
            
            # Get contractor for the partner company
            contractor = Kontrahent.objects.filter(
                user=partnership.firma1.user,
                firma=partnership.firma2
            ).first()
            
            if not contractor:
                raise ValidationError(f"No contractor found for partner company {partnership.firma2.nazwa}")
            
            # Generate invoice number
            invoice_number = self._generate_invoice_number(
                partnership.firma1,
                template['invoice_settings']['typ_dokumentu'],
                generation_date
            )
            
            # Calculate payment due date
            payment_terms_days = template['invoice_settings']['payment_terms_days']
            due_date = generation_date + timedelta(days=payment_terms_days)
            
            # Create invoice
            with transaction.atomic():
                invoice = Faktura.objects.create(
                    user=partnership.firma1.user,
                    sprzedawca=partnership.firma1,
                    nabywca=contractor,
                    typ_dokumentu=template['invoice_settings']['typ_dokumentu'],
                    numer=invoice_number,
                    data_wystawienia=generation_date,
                    data_sprzedazy=generation_date,
                    termin_platnosci=due_date,
                    miejsce_wystawienia=template['invoice_settings']['place_of_issue'],
                    sposob_platnosci=template['invoice_settings']['payment_method'],
                    waluta=template['invoice_settings']['currency'],
                    typ_faktury='sprzedaz',
                    uwagi=template['customization']['custom_notes']
                )
                
                # Add invoice items from template
                for item_data in template['default_items']:
                    self._create_invoice_item(invoice, item_data, template)
                
                # Apply global discount if specified
                if template['pricing']['global_discount_value'] > 0:
                    self._apply_global_discount(invoice, template['pricing'])
                
                self.logger.info(f"Generated invoice {invoice.numer} from template for partnership {partnership.id}")
                return invoice
                
        except Exception as e:
            self.logger.error(f"Error generating invoice from template: {str(e)}")
            raise
    
    def _create_invoice_item(self, invoice: Faktura, item_data: Dict[str, Any], template: Dict[str, Any]):
        """
        Create invoice item from template data
        """
        try:
            # Handle product reference or direct item data
            if 'product_id' in item_data:
                product = Produkt.objects.get(id=item_data['product_id'])
                nazwa = product.nazwa
                cena_netto = product.cena_netto
                vat = product.vat
                jednostka = product.jednostka
            else:
                nazwa = item_data['nazwa']
                cena_netto = Decimal(str(item_data['cena_netto']))
                vat = item_data['vat']
                jednostka = item_data.get('jednostka', 'szt')
            
            ilosc = Decimal(str(item_data.get('ilosc', 1)))
            
            # Apply item-specific discount if specified
            rabat = item_data.get('rabat', 0)
            rabat_typ = item_data.get('rabat_typ', 'procent')
            
            PozycjaFaktury.objects.create(
                faktura=invoice,
                nazwa=nazwa,
                ilosc=ilosc,
                jednostka=jednostka,
                cena_netto=cena_netto,
                vat=vat,
                rabat=rabat if rabat > 0 else None,
                rabat_typ=rabat_typ if rabat > 0 else None
            )
            
        except Exception as e:
            self.logger.error(f"Error creating invoice item: {str(e)}")
            raise
    
    def _apply_global_discount(self, invoice: Faktura, pricing_config: Dict[str, Any]):
        """
        Apply global discount to invoice
        """
        try:
            discount_type = pricing_config['global_discount_type']
            discount_value = pricing_config['global_discount_value']
            
            if discount_type == 'percentage':
                invoice.rabat_procentowy_globalny = Decimal(str(discount_value))
                invoice.jak_obliczyc_rabat = 'proc_netto'
            elif discount_type == 'amount':
                invoice.rabat_kwotowy_globalny = Decimal(str(discount_value))
                invoice.jak_obliczyc_rabat = 'kwotowo'
            
            invoice.save()
            
        except Exception as e:
            self.logger.error(f"Error applying global discount: {str(e)}")
            raise
    
    def _generate_invoice_number(self, company: Firma, document_type: str, generation_date: date) -> str:
        """
        Generate unique invoice number
        """
        try:
            # Get last invoice number for this month
            last_invoice = Faktura.objects.filter(
                sprzedawca=company,
                typ_dokumentu=document_type,
                data_wystawienia__year=generation_date.year,
                data_wystawienia__month=generation_date.month
            ).order_by('-numer').first()
            
            if last_invoice:
                try:
                    # Extract number from format: TYPE/NNN/MM/YYYY
                    parts = last_invoice.numer.split('/')
                    if len(parts) >= 2:
                        last_number = int(parts[1])
                        next_number = last_number + 1
                    else:
                        next_number = 1
                except (ValueError, IndexError):
                    # Fallback: count invoices + 1
                    count = Faktura.objects.filter(
                        sprzedawca=company,
                        typ_dokumentu=document_type,
                        data_wystawienia__year=generation_date.year,
                        data_wystawienia__month=generation_date.month
                    ).count()
                    next_number = count + 1
            else:
                next_number = 1
            
            return f"{document_type}/{next_number:03d}/{generation_date.month:02d}/{generation_date.year}"
            
        except Exception as e:
            self.logger.error(f"Error generating invoice number: {str(e)}")
            # Fallback to timestamp-based number
            timestamp = int(generation_date.timestamp())
            return f"{document_type}/{timestamp}/{generation_date.month:02d}/{generation_date.year}"
    
    def schedule_recurring_invoices(self, template: Dict[str, Any]) -> List[date]:
        """
        Calculate next generation dates for recurring invoices
        """
        try:
            if not template['automation']['auto_generate']:
                return []
            
            frequency = template['automation']['generation_frequency']
            generation_day = template['automation']['generation_day']
            start_date = template['automation'].get('next_generation_date')
            
            if not start_date:
                start_date = date.today()
            elif isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            scheduled_dates = []
            current_date = start_date
            
            # Generate next 12 occurrences
            for _ in range(12):
                if frequency == 'monthly':
                    # Set to specific day of month
                    try:
                        scheduled_date = current_date.replace(day=generation_day)
                    except ValueError:
                        # Handle months with fewer days (e.g., Feb 30 -> Feb 28)
                        import calendar
                        last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                        scheduled_date = current_date.replace(day=min(generation_day, last_day))
                    
                    scheduled_dates.append(scheduled_date)
                    current_date = scheduled_date + relativedelta(months=1)
                    
                elif frequency == 'quarterly':
                    scheduled_date = current_date.replace(day=generation_day)
                    scheduled_dates.append(scheduled_date)
                    current_date = scheduled_date + relativedelta(months=3)
                    
                elif frequency == 'yearly':
                    scheduled_date = current_date.replace(day=generation_day)
                    scheduled_dates.append(scheduled_date)
                    current_date = scheduled_date + relativedelta(years=1)
                    
                elif frequency == 'weekly':
                    scheduled_dates.append(current_date)
                    current_date = current_date + timedelta(weeks=1)
                    
                else:  # daily
                    scheduled_dates.append(current_date)
                    current_date = current_date + timedelta(days=1)
            
            return scheduled_dates
            
        except Exception as e:
            self.logger.error(f"Error scheduling recurring invoices: {str(e)}")
            return []
    
    def get_template_analytics(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get analytics for template usage
        """
        try:
            partnership = Partnerstwo.objects.get(id=template['partnership_id'])
            
            # Get invoices that might have been generated from this template
            # (This is a simplified approach - in production, you'd want to track template usage)
            recent_invoices = Faktura.objects.filter(
                sprzedawca=partnership.firma1,
                nabywca__firma=partnership.firma2,
                data_wystawienia__gte=timezone.now().date() - timedelta(days=365)
            ).order_by('-data_wystawienia')
            
            analytics = {
                'total_invoices_generated': recent_invoices.count(),
                'total_value_generated': sum(inv.suma_brutto for inv in recent_invoices),
                'average_invoice_value': 0,
                'success_rate': 0,
                'payment_rate': 0,
                'average_payment_time': 0,
                'monthly_breakdown': self._get_monthly_invoice_breakdown(recent_invoices),
                'item_usage_stats': self._get_item_usage_stats(recent_invoices, template),
                'performance_metrics': {
                    'generation_time_saved': self._calculate_time_saved(recent_invoices.count()),
                    'error_rate': 0,  # Would track template generation errors
                    'user_satisfaction': 0,  # Would track user feedback
                }
            }
            
            if recent_invoices.count() > 0:
                analytics['average_invoice_value'] = analytics['total_value_generated'] / recent_invoices.count()
                
                paid_invoices = recent_invoices.filter(status='oplacona')
                analytics['payment_rate'] = (paid_invoices.count() / recent_invoices.count()) * 100
                
                # Calculate average payment time
                payment_times = []
                for invoice in paid_invoices:
                    if hasattr(invoice, 'payment_date'):  # Assuming payment_date field exists
                        payment_time = (invoice.payment_date - invoice.data_wystawienia).days
                        payment_times.append(payment_time)
                
                if payment_times:
                    analytics['average_payment_time'] = sum(payment_times) / len(payment_times)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting template analytics: {str(e)}")
            return {}
    
    def _get_monthly_invoice_breakdown(self, invoices) -> List[Dict[str, Any]]:
        """
        Get monthly breakdown of invoice generation
        """
        monthly_data = {}
        
        for invoice in invoices:
            month_key = invoice.data_wystawienia.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'month': month_key,
                    'count': 0,
                    'total_value': Decimal('0.00'),
                    'paid_count': 0,
                    'paid_value': Decimal('0.00')
                }
            
            monthly_data[month_key]['count'] += 1
            monthly_data[month_key]['total_value'] += invoice.suma_brutto
            
            if invoice.status == 'oplacona':
                monthly_data[month_key]['paid_count'] += 1
                monthly_data[month_key]['paid_value'] += invoice.suma_brutto
        
        return sorted(monthly_data.values(), key=lambda x: x['month'])
    
    def _get_item_usage_stats(self, invoices, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics on template item usage
        """
        template_items = {item['nazwa']: 0 for item in template['default_items']}
        
        for invoice in invoices:
            for position in invoice.pozycjafaktury_set.all():
                if position.nazwa in template_items:
                    template_items[position.nazwa] += 1
        
        return template_items
    
    def _calculate_time_saved(self, invoice_count: int) -> float:
        """
        Calculate estimated time saved by using templates
        """
        # Assume 15 minutes saved per invoice by using template
        minutes_per_invoice = 15
        total_minutes_saved = invoice_count * minutes_per_invoice
        return total_minutes_saved / 60  # Return hours
    
    def _validate_template_data(self, template: Dict[str, Any]) -> List[str]:
        """
        Validate template data
        """
        errors = []
        
        # Validate required fields
        if not template.get('name'):
            errors.append("Template name is required")
        
        # Validate invoice settings
        invoice_settings = template.get('invoice_settings', {})
        if invoice_settings.get('payment_terms_days', 0) < 0:
            errors.append("Payment terms must be positive")
        
        # Validate default items
        default_items = template.get('default_items', [])
        for i, item in enumerate(default_items):
            if not item.get('nazwa'):
                errors.append(f"Item {i+1}: Name is required")
            
            try:
                price = Decimal(str(item.get('cena_netto', 0)))
                if price < 0:
                    errors.append(f"Item {i+1}: Price must be positive")
            except (ValueError, TypeError):
                errors.append(f"Item {i+1}: Invalid price format")
        
        # Validate automation settings
        automation = template.get('automation', {})
        if automation.get('auto_generate'):
            frequency = automation.get('generation_frequency')
            if frequency not in ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']:
                errors.append("Invalid generation frequency")
            
            generation_day = automation.get('generation_day', 1)
            if not isinstance(generation_day, int) or generation_day < 1 or generation_day > 31:
                errors.append("Generation day must be between 1 and 31")
        
        return errors
    
    def update_template(self, template: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing template with new data
        """
        try:
            # Deep merge updates into template
            updated_template = self._deep_merge(template.copy(), updates)
            updated_template['updated_at'] = timezone.now()
            
            # Validate updated template
            validation_errors = self._validate_template_data(updated_template)
            if validation_errors:
                raise ValidationError(validation_errors)
            
            self.logger.info(f"Updated template {template['id']}")
            return updated_template
            
        except Exception as e:
            self.logger.error(f"Error updating template: {str(e)}")
            raise
    
    def _deep_merge(self, base: Dict, updates: Dict) -> Dict:
        """
        Deep merge two dictionaries
        """
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result