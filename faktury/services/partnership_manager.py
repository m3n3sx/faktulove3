"""
Partnership Manager for complex business relationships
"""
import logging
from typing import List, Dict, Optional, Any, Tuple
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, date

from ..models import Firma, Kontrahent, Partnerstwo, Faktura, PozycjaFaktury

logger = logging.getLogger(__name__)


class PartnershipManager:
    """
    Service for managing complex business partnerships and relationships
    """
    
    def __init__(self):
        self.logger = logger
    
    def create_business_partners(self, company: Firma, partners_data: List[Dict[str, Any]]) -> List[Partnerstwo]:
        """
        Create multiple business partners for a company
        """
        created_partnerships = []
        
        try:
            with transaction.atomic():
                for partner_data in partners_data:
                    partnership = self._create_single_partnership(company, partner_data)
                    if partnership:
                        created_partnerships.append(partnership)
                        
        except Exception as e:
            self.logger.error(f"Error creating business partners: {str(e)}")
            raise
        
        return created_partnerships
    
    def _create_single_partnership(self, company: Firma, partner_data: Dict[str, Any]) -> Optional[Partnerstwo]:
        """
        Create a single partnership
        """
        try:
            partner_company = Firma.objects.get(id=partner_data['partner_company_id'])
            
            # Check if partnership already exists
            existing = Partnerstwo.objects.filter(
                models.Q(firma1=company, firma2=partner_company) |
                models.Q(firma1=partner_company, firma2=company)
            ).first()
            
            if existing:
                self.logger.warning(f"Partnership between {company.nazwa} and {partner_company.nazwa} already exists")
                return existing
            
            partnership = Partnerstwo.objects.create(
                firma1=company,
                firma2=partner_company,
                typ_partnerstwa=partner_data.get('typ_partnerstwa', 'wspolpraca'),
                opis=partner_data.get('opis', ''),
                data_rozpoczecia=partner_data.get('data_rozpoczecia'),
                data_zakonczenia=partner_data.get('data_zakonczenia'),
                aktywne=partner_data.get('aktywne', True),
                auto_ksiegowanie=partner_data.get('auto_ksiegowanie', True)
            )
            
            # Create contractor records for both companies
            self._create_cross_contractors(company, partner_company)
            
            self.logger.info(f"Created partnership between {company.nazwa} and {partner_company.nazwa}")
            return partnership
            
        except Firma.DoesNotExist:
            self.logger.error(f"Partner company with ID {partner_data['partner_company_id']} not found")
            return None
        except Exception as e:
            self.logger.error(f"Error creating partnership: {str(e)}")
            return None
    
    def _create_cross_contractors(self, company1: Firma, company2: Firma):
        """
        Create contractor records for both companies to enable invoicing
        """
        try:
            # Create company2 as contractor for company1's user
            if not Kontrahent.objects.filter(user=company1.user, nip=company2.nip).exists():
                Kontrahent.objects.create(
                    user=company1.user,
                    nazwa=company2.nazwa,
                    nip=company2.nip,
                    regon=company2.regon,
                    ulica=company2.ulica,
                    numer_domu=company2.numer_domu,
                    numer_mieszkania=company2.numer_mieszkania,
                    kod_pocztowy=company2.kod_pocztowy,
                    miejscowosc=company2.miejscowosc,
                    kraj=company2.kraj,
                    czy_firma=True,
                    firma=company2
                )
            
            # Create company1 as contractor for company2's user
            if not Kontrahent.objects.filter(user=company2.user, nip=company1.nip).exists():
                Kontrahent.objects.create(
                    user=company2.user,
                    nazwa=company1.nazwa,
                    nip=company1.nip,
                    regon=company1.regon,
                    ulica=company1.ulica,
                    numer_domu=company1.numer_domu,
                    numer_mieszkania=company1.numer_mieszkania,
                    kod_pocztowy=company1.kod_pocztowy,
                    miejscowosc=company1.miejscowosc,
                    kraj=company1.kraj,
                    czy_firma=True,
                    firma=company1
                )
                
        except Exception as e:
            self.logger.error(f"Error creating cross contractors: {str(e)}")
    
    def get_partnership_details(self, partnership: Partnerstwo) -> Dict[str, Any]:
        """
        Get detailed information about a partnership
        """
        try:
            # Get transaction statistics
            company1_sales = Faktura.objects.filter(
                sprzedawca=partnership.firma1,
                nabywca__firma=partnership.firma2,
                typ_faktury='sprzedaz'
            )
            
            company2_sales = Faktura.objects.filter(
                sprzedawca=partnership.firma2,
                nabywca__firma=partnership.firma1,
                typ_faktury='sprzedaz'
            )
            
            # Calculate totals
            company1_total = sum(invoice.suma_brutto for invoice in company1_sales)
            company2_total = sum(invoice.suma_brutto for invoice in company2_sales)
            
            # Get recent transactions
            recent_transactions = list(company1_sales.order_by('-data_wystawienia')[:5]) + \
                                list(company2_sales.order_by('-data_wystawienia')[:5])
            recent_transactions.sort(key=lambda x: x.data_wystawienia, reverse=True)
            
            return {
                'partnership': partnership,
                'company1_sales_count': company1_sales.count(),
                'company2_sales_count': company2_sales.count(),
                'company1_total_value': company1_total,
                'company2_total_value': company2_total,
                'total_transactions': company1_sales.count() + company2_sales.count(),
                'total_value': company1_total + company2_total,
                'recent_transactions': recent_transactions[:10],
                'balance': company1_total - company2_total,
                'partnership_duration': self._calculate_partnership_duration(partnership),
                'average_monthly_value': self._calculate_average_monthly_value(partnership)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting partnership details: {str(e)}")
            return {}
    
    def _calculate_partnership_duration(self, partnership: Partnerstwo) -> int:
        """
        Calculate partnership duration in days
        """
        start_date = partnership.data_rozpoczecia or partnership.data_utworzenia.date()
        end_date = partnership.data_zakonczenia or date.today()
        return (end_date - start_date).days
    
    def _calculate_average_monthly_value(self, partnership: Partnerstwo) -> Decimal:
        """
        Calculate average monthly transaction value
        """
        try:
            duration_months = max(1, self._calculate_partnership_duration(partnership) / 30)
            
            total_value = Decimal('0.00')
            
            # Get all transactions between partners
            transactions = Faktura.objects.filter(
                models.Q(
                    sprzedawca=partnership.firma1,
                    nabywca__firma=partnership.firma2
                ) | models.Q(
                    sprzedawca=partnership.firma2,
                    nabywca__firma=partnership.firma1
                )
            )
            
            for transaction in transactions:
                total_value += transaction.suma_brutto
            
            return total_value / Decimal(str(duration_months))
            
        except Exception as e:
            self.logger.error(f"Error calculating average monthly value: {str(e)}")
            return Decimal('0.00')
    
    def create_partnership_invoice_template(self, partnership: Partnerstwo, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create invoice template specific to partnership
        """
        try:
            template = {
                'partnership_id': partnership.id,
                'template_name': template_data.get('name', f'Template for {partnership.firma2.nazwa}'),
                'default_payment_terms': template_data.get('payment_terms', 14),
                'default_payment_method': template_data.get('payment_method', 'przelew'),
                'default_items': template_data.get('default_items', []),
                'auto_generate': template_data.get('auto_generate', False),
                'generation_frequency': template_data.get('generation_frequency', 'monthly'),
                'next_generation_date': template_data.get('next_generation_date'),
                'template_settings': {
                    'include_logo': template_data.get('include_logo', True),
                    'custom_notes': template_data.get('custom_notes', ''),
                    'discount_percentage': template_data.get('discount_percentage', 0),
                    'vat_rate': template_data.get('vat_rate', '23'),
                }
            }
            
            self.logger.info(f"Created invoice template for partnership {partnership.id}")
            return template
            
        except Exception as e:
            self.logger.error(f"Error creating invoice template: {str(e)}")
            return {}
    
    def track_partner_transactions(self, partnership: Partnerstwo, date_from: Optional[date] = None, date_to: Optional[date] = None) -> Dict[str, Any]:
        """
        Track and analyze transactions between partners
        """
        try:
            # Set default date range if not provided
            if not date_from:
                date_from = date.today() - timedelta(days=365)  # Last year
            if not date_to:
                date_to = date.today()
            
            # Get transactions in both directions
            company1_to_company2 = Faktura.objects.filter(
                sprzedawca=partnership.firma1,
                nabywca__firma=partnership.firma2,
                data_wystawienia__range=[date_from, date_to]
            ).order_by('-data_wystawienia')
            
            company2_to_company1 = Faktura.objects.filter(
                sprzedawca=partnership.firma2,
                nabywca__firma=partnership.firma1,
                data_wystawienia__range=[date_from, date_to]
            ).order_by('-data_wystawienia')
            
            # Calculate statistics
            stats = {
                'date_range': {
                    'from': date_from,
                    'to': date_to
                },
                'company1_to_company2': {
                    'count': company1_to_company2.count(),
                    'total_value': sum(inv.suma_brutto for inv in company1_to_company2),
                    'paid_count': company1_to_company2.filter(status='oplacona').count(),
                    'unpaid_count': company1_to_company2.exclude(status='oplacona').count(),
                    'transactions': list(company1_to_company2)
                },
                'company2_to_company1': {
                    'count': company2_to_company1.count(),
                    'total_value': sum(inv.suma_brutto for inv in company2_to_company1),
                    'paid_count': company2_to_company1.filter(status='oplacona').count(),
                    'unpaid_count': company2_to_company1.exclude(status='oplacona').count(),
                    'transactions': list(company2_to_company1)
                }
            }
            
            # Calculate balance
            stats['balance'] = {
                'company1_owes': stats['company2_to_company1']['total_value'],
                'company2_owes': stats['company1_to_company2']['total_value'],
                'net_balance': stats['company1_to_company2']['total_value'] - stats['company2_to_company1']['total_value']
            }
            
            # Monthly breakdown
            stats['monthly_breakdown'] = self._get_monthly_breakdown(
                company1_to_company2, company2_to_company1, date_from, date_to
            )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error tracking partner transactions: {str(e)}")
            return {}
    
    def _get_monthly_breakdown(self, transactions1, transactions2, date_from: date, date_to: date) -> List[Dict[str, Any]]:
        """
        Get monthly breakdown of transactions
        """
        monthly_data = {}
        
        # Process transactions from company1 to company2
        for transaction in transactions1:
            month_key = transaction.data_wystawienia.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'month': month_key,
                    'company1_to_company2': Decimal('0.00'),
                    'company2_to_company1': Decimal('0.00'),
                    'count1': 0,
                    'count2': 0
                }
            monthly_data[month_key]['company1_to_company2'] += transaction.suma_brutto
            monthly_data[month_key]['count1'] += 1
        
        # Process transactions from company2 to company1
        for transaction in transactions2:
            month_key = transaction.data_wystawienia.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'month': month_key,
                    'company1_to_company2': Decimal('0.00'),
                    'company2_to_company1': Decimal('0.00'),
                    'count1': 0,
                    'count2': 0
                }
            monthly_data[month_key]['company2_to_company1'] += transaction.suma_brutto
            monthly_data[month_key]['count2'] += 1
        
        # Calculate net balance for each month
        for month_data in monthly_data.values():
            month_data['net_balance'] = month_data['company1_to_company2'] - month_data['company2_to_company1']
        
        return sorted(monthly_data.values(), key=lambda x: x['month'])
    
    def generate_partnership_report(self, partnership: Partnerstwo) -> Dict[str, Any]:
        """
        Generate comprehensive partnership report
        """
        try:
            report = {
                'partnership_info': {
                    'id': partnership.id,
                    'company1': partnership.firma1.nazwa,
                    'company2': partnership.firma2.nazwa,
                    'type': partnership.get_typ_partnerstwa_display(),
                    'active': partnership.aktywne,
                    'auto_accounting': partnership.auto_ksiegowanie,
                    'start_date': partnership.data_rozpoczecia,
                    'end_date': partnership.data_zakonczenia,
                    'description': partnership.opis
                },
                'statistics': self.get_partnership_details(partnership),
                'transaction_tracking': self.track_partner_transactions(partnership),
                'recommendations': self._generate_partnership_recommendations(partnership),
                'generated_at': timezone.now()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating partnership report: {str(e)}")
            return {}
    
    def _generate_partnership_recommendations(self, partnership: Partnerstwo) -> List[str]:
        """
        Generate recommendations for partnership optimization
        """
        recommendations = []
        
        try:
            details = self.get_partnership_details(partnership)
            
            # Check transaction balance
            if abs(details.get('balance', 0)) > 10000:  # Significant imbalance
                recommendations.append(
                    "Rozważ wyrównanie salda transakcji między partnerami"
                )
            
            # Check auto-accounting
            if not partnership.auto_ksiegowanie:
                recommendations.append(
                    "Włącz auto-księgowanie dla automatyzacji procesów"
                )
            
            # Check transaction frequency
            total_transactions = details.get('total_transactions', 0)
            duration_months = max(1, self._calculate_partnership_duration(partnership) / 30)
            
            if total_transactions / duration_months < 1:  # Less than 1 transaction per month
                recommendations.append(
                    "Niska częstotliwość transakcji - rozważ intensyfikację współpracy"
                )
            
            # Check payment terms
            recent_transactions = details.get('recent_transactions', [])
            overdue_count = sum(1 for t in recent_transactions if t.status != 'oplacona' and t.termin_platnosci < date.today())
            
            if overdue_count > 0:
                recommendations.append(
                    f"Masz {overdue_count} przeterminowanych faktur - skontaktuj się z partnerem"
                )
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def validate_partnership_data(self, partnership_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate partnership data
        """
        errors = {}
        
        # Check required fields
        if not partnership_data.get('firma2'):
            errors.setdefault('firma2', []).append('Partner company is required')
        
        # Validate dates
        start_date = partnership_data.get('data_rozpoczecia')
        end_date = partnership_data.get('data_zakonczenia')
        
        if start_date and end_date and start_date > end_date:
            errors.setdefault('data_zakonczenia', []).append('End date must be after start date')
        
        # Validate partnership type
        valid_types = ['dostawca', 'odbiorca', 'wspolpraca', 'inne']
        if partnership_data.get('typ_partnerstwa') not in valid_types:
            errors.setdefault('typ_partnerstwa', []).append('Invalid partnership type')
        
        return errors