"""
Company Management Service for multi-tenancy support
"""
import logging
from typing import List, Dict, Optional, Any
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from ..models import Firma, Kontrahent, Partnerstwo, Faktura, UserProfile

logger = logging.getLogger(__name__)


class CompanyManagementService:
    """
    Service for managing multiple companies and multi-tenancy support
    """
    
    def __init__(self):
        self.logger = logger
    
    def create_test_companies(self) -> List[Firma]:
        """
        Create test companies with realistic Polish business data
        """
        test_companies_data = [
            {
                'nazwa': 'TechSoft Sp. z o.o.',
                'nip': '1234567890',
                'regon': '123456789',
                'ulica': 'Marszałkowska',
                'numer_domu': '15',
                'numer_mieszkania': '3A',
                'kod_pocztowy': '00-001',
                'miejscowosc': 'Warszawa',
                'kraj': 'Polska',
                'user_data': {
                    'username': 'techsoft_admin',
                    'email': 'admin@techsoft.pl',
                    'first_name': 'Jan',
                    'last_name': 'Kowalski'
                }
            },
            {
                'nazwa': 'Budowlanka Kraków Sp. z o.o.',
                'nip': '9876543210',
                'regon': '987654321',
                'ulica': 'Floriańska',
                'numer_domu': '42',
                'kod_pocztowy': '31-021',
                'miejscowosc': 'Kraków',
                'kraj': 'Polska',
                'user_data': {
                    'username': 'budowlanka_admin',
                    'email': 'biuro@budowlanka.pl',
                    'first_name': 'Anna',
                    'last_name': 'Nowak'
                }
            },
            {
                'nazwa': 'Gastro Deluxe S.A.',
                'nip': '5555666677',
                'regon': '555666777',
                'ulica': 'Piotrkowska',
                'numer_domu': '88',
                'kod_pocztowy': '90-001',
                'miejscowosc': 'Łódź',
                'kraj': 'Polska',
                'user_data': {
                    'username': 'gastro_admin',
                    'email': 'kontakt@gastrodeluxe.pl',
                    'first_name': 'Piotr',
                    'last_name': 'Wiśniewski'
                }
            },
            {
                'nazwa': 'IT Solutions Gdańsk Sp. z o.o.',
                'nip': '1111222233',
                'regon': '111222333',
                'ulica': 'Długa',
                'numer_domu': '12',
                'numer_mieszkania': '5',
                'kod_pocztowy': '80-001',
                'miejscowosc': 'Gdańsk',
                'kraj': 'Polska',
                'user_data': {
                    'username': 'itsolutions_admin',
                    'email': 'info@itsolutions.pl',
                    'first_name': 'Michał',
                    'last_name': 'Zieliński'
                }
            },
            {
                'nazwa': 'Consulting Pro Wrocław Sp. z o.o.',
                'nip': '7777888899',
                'regon': '777888999',
                'ulica': 'Rynek',
                'numer_domu': '25',
                'kod_pocztowy': '50-001',
                'miejscowosc': 'Wrocław',
                'kraj': 'Polska',
                'user_data': {
                    'username': 'consulting_admin',
                    'email': 'biuro@consultingpro.pl',
                    'first_name': 'Katarzyna',
                    'last_name': 'Lewandowska'
                }
            }
        ]
        
        created_companies = []
        
        try:
            with transaction.atomic():
                for company_data in test_companies_data:
                    # Check if company already exists
                    if Firma.objects.filter(nip=company_data['nip']).exists():
                        self.logger.info(f"Company with NIP {company_data['nip']} already exists, skipping")
                        continue
                    
                    # Create user for company
                    user_data = company_data.pop('user_data')
                    
                    # Check if user already exists
                    if User.objects.filter(username=user_data['username']).exists():
                        self.logger.info(f"User {user_data['username']} already exists, skipping")
                        continue
                    
                    user = User.objects.create_user(
                        username=user_data['username'],
                        email=user_data['email'],
                        password='TestPassword123!',  # Default test password
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name']
                    )
                    
                    # Create user profile
                    UserProfile.objects.create(
                        user=user,
                        imie=user_data['first_name'],
                        nazwisko=user_data['last_name']
                    )
                    
                    # Create company
                    firma = Firma.objects.create(
                        user=user,
                        **company_data
                    )
                    
                    # Create corresponding contractor record
                    Kontrahent.objects.create(
                        user=user,
                        nazwa=firma.nazwa,
                        nip=firma.nip,
                        regon=firma.regon,
                        ulica=firma.ulica,
                        numer_domu=firma.numer_domu,
                        numer_mieszkania=firma.numer_mieszkania,
                        kod_pocztowy=firma.kod_pocztowy,
                        miejscowosc=firma.miejscowosc,
                        kraj=firma.kraj,
                        czy_firma=True,
                        is_own_company=True,
                        firma=firma
                    )
                    
                    created_companies.append(firma)
                    self.logger.info(f"Created test company: {firma.nazwa}")
                
        except Exception as e:
            self.logger.error(f"Error creating test companies: {str(e)}")
            raise
        
        return created_companies
    
    def switch_company_context(self, user: User, company_id: int) -> bool:
        """
        Switch user context between companies (for multi-company users)
        """
        try:
            # Verify user has access to this company
            if not self.user_has_company_access(user, company_id):
                raise ValidationError("User does not have access to this company")
            
            # Store company context in session (this would be handled in views)
            # For now, we'll just validate the access
            company = Firma.objects.get(id=company_id)
            self.logger.info(f"User {user.username} switched to company context: {company.nazwa}")
            
            return True
            
        except Firma.DoesNotExist:
            self.logger.error(f"Company with ID {company_id} does not exist")
            return False
        except Exception as e:
            self.logger.error(f"Error switching company context: {str(e)}")
            return False
    
    def user_has_company_access(self, user: User, company_id: int) -> bool:
        """
        Check if user has access to specific company
        """
        try:
            # Check if user owns the company
            if Firma.objects.filter(id=company_id, user=user).exists():
                return True
            
            # Check if user has partnership access to company
            user_company = Firma.objects.filter(user=user).first()
            if user_company:
                partnership_exists = Partnerstwo.objects.filter(
                    models.Q(firma1=user_company, firma2_id=company_id) |
                    models.Q(firma1_id=company_id, firma2=user_company),
                    aktywne=True
                ).exists()
                
                if partnership_exists:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking company access: {str(e)}")
            return False
    
    def get_user_companies(self, user: User) -> List[Dict[str, Any]]:
        """
        Get all companies user has access to
        """
        companies = []
        
        try:
            # Get user's own company
            user_company = Firma.objects.filter(user=user).first()
            if user_company:
                companies.append({
                    'id': user_company.id,
                    'nazwa': user_company.nazwa,
                    'nip': user_company.nip,
                    'is_owner': True,
                    'access_type': 'owner'
                })
                
                # Get companies through partnerships
                partnerships = Partnerstwo.objects.filter(
                    models.Q(firma1=user_company) | models.Q(firma2=user_company),
                    aktywne=True
                ).select_related('firma1', 'firma2')
                
                for partnership in partnerships:
                    partner_company = partnership.firma2 if partnership.firma1 == user_company else partnership.firma1
                    companies.append({
                        'id': partner_company.id,
                        'nazwa': partner_company.nazwa,
                        'nip': partner_company.nip,
                        'is_owner': False,
                        'access_type': 'partnership',
                        'partnership_type': partnership.typ_partnerstwa
                    })
            
        except Exception as e:
            self.logger.error(f"Error getting user companies: {str(e)}")
        
        return companies
    
    def create_company_permissions(self, user: User, company: Firma, permissions: List[str]) -> bool:
        """
        Create company-specific permissions for user
        """
        try:
            # This would integrate with Django's permission system
            # For now, we'll use the partnership system as a proxy
            
            # Create basic contractor record for cross-company access
            if not Kontrahent.objects.filter(user=user, firma=company).exists():
                user_firma = Firma.objects.filter(user=user).first()
                if user_firma:
                    Kontrahent.objects.create(
                        user=user,
                        nazwa=company.nazwa,
                        nip=company.nip,
                        ulica=company.ulica,
                        numer_domu=company.numer_domu,
                        kod_pocztowy=company.kod_pocztowy,
                        miejscowosc=company.miejscowosc,
                        czy_firma=True,
                        firma=company
                    )
            
            self.logger.info(f"Created permissions for user {user.username} on company {company.nazwa}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating company permissions: {str(e)}")
            return False
    
    def get_company_statistics(self, company: Firma) -> Dict[str, Any]:
        """
        Get statistics for a company
        """
        try:
            stats = {
                'total_invoices': Faktura.objects.filter(sprzedawca=company).count(),
                'total_sales': Faktura.objects.filter(
                    sprzedawca=company, 
                    typ_faktury='sprzedaz'
                ).count(),
                'total_costs': Faktura.objects.filter(
                    user=company.user,
                    typ_faktury='koszt'
                ).count(),
                'active_partnerships': Partnerstwo.objects.filter(
                    models.Q(firma1=company) | models.Q(firma2=company),
                    aktywne=True
                ).count(),
                'total_contractors': Kontrahent.objects.filter(user=company.user).count(),
            }
            
            # Calculate revenue (this would need proper calculation)
            revenue_invoices = Faktura.objects.filter(
                sprzedawca=company,
                typ_faktury='sprzedaz',
                status='oplacona'
            )
            
            total_revenue = Decimal('0.00')
            for invoice in revenue_invoices:
                total_revenue += invoice.suma_brutto
            
            stats['total_revenue'] = total_revenue
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting company statistics: {str(e)}")
            return {}
    
    def validate_company_data(self, company_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate company data before creation/update
        """
        errors = {}
        
        # Validate NIP
        nip = company_data.get('nip', '').replace('-', '').replace(' ', '')
        if nip:
            if len(nip) != 10 or not nip.isdigit():
                errors.setdefault('nip', []).append('NIP musi składać się z 10 cyfr')
            elif Firma.objects.filter(nip=nip).exists():
                errors.setdefault('nip', []).append('Firma z tym numerem NIP już istnieje')
        
        # Validate required fields
        required_fields = ['nazwa', 'ulica', 'numer_domu', 'kod_pocztowy', 'miejscowosc']
        for field in required_fields:
            if not company_data.get(field):
                errors.setdefault(field, []).append(f'Pole {field} jest wymagane')
        
        # Validate postal code
        kod_pocztowy = company_data.get('kod_pocztowy', '')
        if kod_pocztowy and not self._validate_postal_code(kod_pocztowy):
            errors.setdefault('kod_pocztowy', []).append('Nieprawidłowy format kodu pocztowego')
        
        return errors
    
    def _validate_postal_code(self, postal_code: str) -> bool:
        """
        Validate Polish postal code format
        """
        import re
        pattern = r'^\d{2}-\d{3}$'
        return bool(re.match(pattern, postal_code))
    
    def create_company_backup(self, company: Firma) -> Dict[str, Any]:
        """
        Create backup of company data
        """
        try:
            backup_data = {
                'company': {
                    'nazwa': company.nazwa,
                    'nip': company.nip,
                    'regon': company.regon,
                    'ulica': company.ulica,
                    'numer_domu': company.numer_domu,
                    'numer_mieszkania': company.numer_mieszkania,
                    'kod_pocztowy': company.kod_pocztowy,
                    'miejscowosc': company.miejscowosc,
                    'kraj': company.kraj,
                },
                'invoices_count': Faktura.objects.filter(sprzedawca=company).count(),
                'contractors_count': Kontrahent.objects.filter(user=company.user).count(),
                'partnerships_count': Partnerstwo.objects.filter(
                    models.Q(firma1=company) | models.Q(firma2=company)
                ).count(),
                'backup_date': timezone.now().isoformat()
            }
            
            return backup_data
            
        except Exception as e:
            self.logger.error(f"Error creating company backup: {str(e)}")
            return {}