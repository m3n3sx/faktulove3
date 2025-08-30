"""
Management command to demonstrate partnership functionality
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta

from faktury.services.company_management_service import CompanyManagementService
from faktury.services.partnership_manager import PartnershipManager
from faktury.services.partnership_invoice_templates import PartnershipInvoiceTemplateService
from faktury.models import Firma, Kontrahent, Partnerstwo, Faktura, PozycjaFaktury


class Command(BaseCommand):
    help = 'Demonstrate partnership functionality with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-invoices',
            action='store_true',
            help='Create sample invoices between partners',
        )
        parser.add_argument(
            '--create-templates',
            action='store_true',
            help='Create invoice templates for partnerships',
        )
        parser.add_argument(
            '--generate-reports',
            action='store_true',
            help='Generate partnership reports',
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting partnership demonstration...')
            
            # Initialize services
            company_service = CompanyManagementService()
            partnership_manager = PartnershipManager()
            template_service = PartnershipInvoiceTemplateService()
            
            # Create test companies if they don't exist
            self.stdout.write('Ensuring test companies exist...')
            companies = company_service.create_test_companies()
            
            if not companies:
                # Get existing companies
                companies = list(Firma.objects.filter(
                    nip__in=['1234567890', '9876543210', '5555666677', '1111222233', '7777888899']
                ))
            
            if len(companies) < 2:
                raise CommandError('Need at least 2 companies for partnership demonstration')
            
            # Create partnerships between companies
            self.stdout.write('Creating partnerships...')
            partnerships_created = self._create_sample_partnerships(companies, partnership_manager)
            
            # Create sample invoices if requested
            if options['create_invoices']:
                self.stdout.write('Creating sample invoices...')
                invoices_created = self._create_sample_invoices(companies)
                self.stdout.write(f'Created {invoices_created} sample invoices')
            
            # Create invoice templates if requested
            if options['create_templates']:
                self.stdout.write('Creating invoice templates...')
                templates_created = self._create_invoice_templates(partnerships_created, template_service)
                self.stdout.write(f'Created {len(templates_created)} invoice templates')
            
            # Generate reports if requested
            if options['generate_reports']:
                self.stdout.write('Generating partnership reports...')
                self._generate_partnership_reports(partnerships_created, partnership_manager)
            
            self.stdout.write(
                self.style.SUCCESS('Partnership demonstration completed successfully!')
            )
            
            # Display summary
            self._display_summary(companies, partnerships_created)
            
        except Exception as e:
            raise CommandError(f'Error during partnership demonstration: {str(e)}')
    
    def _create_sample_partnerships(self, companies, partnership_manager):
        """Create sample partnerships between companies"""
        partnerships = []
        
        try:
            with transaction.atomic():
                # Create partnerships between first 4 companies
                partnership_configs = [
                    {
                        'company1_idx': 0,
                        'company2_idx': 1,
                        'type': 'dostawca',
                        'description': 'TechSoft dostarcza usługi IT dla Budowlanki'
                    },
                    {
                        'company1_idx': 1,
                        'company2_idx': 2,
                        'type': 'odbiorca',
                        'description': 'Budowlanka świadczy usługi budowlane dla Gastro Deluxe'
                    },
                    {
                        'company1_idx': 2,
                        'company2_idx': 3,
                        'type': 'wspolpraca',
                        'description': 'Gastro Deluxe i IT Solutions współpracują w projektach'
                    },
                    {
                        'company1_idx': 0,
                        'company2_idx': 3,
                        'type': 'wspolpraca',
                        'description': 'TechSoft i IT Solutions wymieniają się usługami'
                    }
                ]
                
                for config in partnership_configs:
                    if config['company1_idx'] < len(companies) and config['company2_idx'] < len(companies):
                        company1 = companies[config['company1_idx']]
                        company2 = companies[config['company2_idx']]
                        
                        # Check if partnership already exists
                        existing = Partnerstwo.objects.filter(
                            models.Q(firma1=company1, firma2=company2) |
                            models.Q(firma1=company2, firma2=company1)
                        ).first()
                        
                        if not existing:
                            partner_data = {
                                'partner_company_id': company2.id,
                                'typ_partnerstwa': config['type'],
                                'opis': config['description'],
                                'aktywne': True,
                                'auto_ksiegowanie': True
                            }
                            
                            partnership = partnership_manager._create_single_partnership(
                                company1, partner_data
                            )
                            
                            if partnership:
                                partnerships.append(partnership)
                                self.stdout.write(
                                    f'  Created partnership: {company1.nazwa} ↔ {company2.nazwa}'
                                )
                        else:
                            partnerships.append(existing)
                            self.stdout.write(
                                f'  Partnership already exists: {company1.nazwa} ↔ {company2.nazwa}'
                            )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating partnerships: {str(e)}')
            )
        
        return partnerships
    
    def _create_sample_invoices(self, companies):
        """Create sample invoices between partner companies"""
        invoices_created = 0
        
        try:
            # Get partnerships
            partnerships = Partnerstwo.objects.filter(
                firma1__in=companies,
                firma2__in=companies
            )
            
            for partnership in partnerships:
                # Create invoices in both directions
                invoices_created += self._create_invoices_for_partnership(partnership)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample invoices: {str(e)}')
            )
        
        return invoices_created
    
    def _create_invoices_for_partnership(self, partnership):
        """Create sample invoices for a specific partnership"""
        invoices_created = 0
        
        try:
            # Create 2-3 invoices from company1 to company2
            contractor1 = Kontrahent.objects.filter(
                user=partnership.firma1.user,
                firma=partnership.firma2
            ).first()
            
            if contractor1:
                for i in range(2):
                    invoice = Faktura.objects.create(
                        user=partnership.firma1.user,
                        sprzedawca=partnership.firma1,
                        nabywca=contractor1,
                        numer=f'DEMO/{partnership.id}/{i+1}/2024',
                        data_wystawienia=date.today() - timedelta(days=30-i*10),
                        data_sprzedazy=date.today() - timedelta(days=30-i*10),
                        termin_platnosci=date.today() - timedelta(days=16-i*10),
                        miejsce_wystawienia=partnership.firma1.miejscowosc,
                        typ_faktury='sprzedaz',
                        status='oplacona' if i == 0 else 'wystawiona'
                    )
                    
                    # Add sample items
                    PozycjaFaktury.objects.create(
                        faktura=invoice,
                        nazwa=f'Usługi {partnership.get_typ_partnerstwa_display().lower()}',
                        ilosc=Decimal('1.00'),
                        jednostka='usł',
                        cena_netto=Decimal('1000.00') + Decimal(str(i * 500)),
                        vat='23'
                    )
                    
                    invoices_created += 1
            
            # Create 1-2 invoices from company2 to company1
            contractor2 = Kontrahent.objects.filter(
                user=partnership.firma2.user,
                firma=partnership.firma1
            ).first()
            
            if contractor2:
                for i in range(1):
                    invoice = Faktura.objects.create(
                        user=partnership.firma2.user,
                        sprzedawca=partnership.firma2,
                        nabywca=contractor2,
                        numer=f'DEMO/{partnership.id}/R{i+1}/2024',
                        data_wystawienia=date.today() - timedelta(days=20-i*10),
                        data_sprzedazy=date.today() - timedelta(days=20-i*10),
                        termin_platnosci=date.today() - timedelta(days=6-i*10),
                        miejsce_wystawienia=partnership.firma2.miejscowosc,
                        typ_faktury='sprzedaz',
                        status='wystawiona'
                    )
                    
                    # Add sample items
                    PozycjaFaktury.objects.create(
                        faktura=invoice,
                        nazwa='Usługi zwrotne',
                        ilosc=Decimal('1.00'),
                        jednostka='usł',
                        cena_netto=Decimal('750.00'),
                        vat='23'
                    )
                    
                    invoices_created += 1
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating invoices for partnership {partnership.id}: {str(e)}')
            )
        
        return invoices_created
    
    def _create_invoice_templates(self, partnerships, template_service):
        """Create sample invoice templates"""
        templates = []
        
        try:
            for partnership in partnerships:
                template_data = {
                    'name': f'Monthly Services - {partnership.firma2.nazwa}',
                    'description': f'Recurring monthly invoice template for {partnership.get_typ_partnerstwa_display().lower()} services',
                    'payment_terms': 14,
                    'payment_method': 'przelew',
                    'auto_generate': True,
                    'generation_frequency': 'monthly',
                    'generation_day': 1,
                    'default_items': [
                        {
                            'nazwa': f'Monthly {partnership.get_typ_partnerstwa_display()} Services',
                            'cena_netto': '2000.00',
                            'vat': '23',
                            'jednostka': 'usł',
                            'ilosc': 1
                        }
                    ],
                    'include_logo': True,
                    'custom_notes': f'Recurring services as per partnership agreement with {partnership.firma2.nazwa}',
                    'discount_value': 5,  # 5% discount for recurring services
                }
                
                template = template_service.create_invoice_template(partnership, template_data)
                templates.append(template)
                
                self.stdout.write(
                    f'  Created template: {template["name"]}'
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating invoice templates: {str(e)}')
            )
        
        return templates
    
    def _generate_partnership_reports(self, partnerships, partnership_manager):
        """Generate and display partnership reports"""
        try:
            for partnership in partnerships:
                self.stdout.write(f'\n--- Partnership Report: {partnership.firma1.nazwa} ↔ {partnership.firma2.nazwa} ---')
                
                # Get partnership details
                details = partnership_manager.get_partnership_details(partnership)
                
                self.stdout.write(f'Type: {partnership.get_typ_partnerstwa_display()}')
                self.stdout.write(f'Active: {"Yes" if partnership.aktywne else "No"}')
                self.stdout.write(f'Auto-accounting: {"Yes" if partnership.auto_ksiegowanie else "No"}')
                self.stdout.write(f'Total transactions: {details.get("total_transactions", 0)}')
                self.stdout.write(f'Total value: {details.get("total_value", 0):.2f} PLN')
                self.stdout.write(f'Balance: {details.get("balance", 0):.2f} PLN')
                
                # Get transaction tracking
                tracking = partnership_manager.track_partner_transactions(partnership)
                
                if tracking.get('monthly_breakdown'):
                    self.stdout.write('\nMonthly breakdown:')
                    for month_data in tracking['monthly_breakdown'][-3:]:  # Last 3 months
                        self.stdout.write(
                            f'  {month_data["month"]}: '
                            f'{month_data["company1_to_company2"]:.2f} PLN → / '
                            f'← {month_data["company2_to_company1"]:.2f} PLN'
                        )
                
                # Get recommendations
                recommendations = partnership_manager._generate_partnership_recommendations(partnership)
                if recommendations:
                    self.stdout.write('\nRecommendations:')
                    for rec in recommendations:
                        self.stdout.write(f'  • {rec}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating reports: {str(e)}')
            )
    
    def _display_summary(self, companies, partnerships):
        """Display summary of demonstration"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('PARTNERSHIP DEMONSTRATION SUMMARY')
        self.stdout.write('='*60)
        
        self.stdout.write(f'Companies available: {len(companies)}')
        for company in companies:
            self.stdout.write(f'  • {company.nazwa} (NIP: {company.nip})')
        
        self.stdout.write(f'\nPartnerships created: {len(partnerships)}')
        for partnership in partnerships:
            self.stdout.write(
                f'  • {partnership.firma1.nazwa} ↔ {partnership.firma2.nazwa} '
                f'({partnership.get_typ_partnerstwa_display()})'
            )
        
        # Count invoices
        total_invoices = Faktura.objects.filter(
            sprzedawca__in=companies
        ).count()
        
        self.stdout.write(f'\nTotal invoices in system: {total_invoices}')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('ACCESS INSTRUCTIONS')
        self.stdout.write('='*60)
        self.stdout.write('1. Login with any test company credentials:')
        for company in companies[:3]:  # Show first 3
            username = company.user.username
            self.stdout.write(f'   Username: {username}, Password: TestPassword123!')
        
        self.stdout.write('\n2. Navigate to:')
        self.stdout.write('   • Company Dashboard: /companies/dashboard/')
        self.stdout.write('   • Partnership Management: /companies/partnerships/')
        self.stdout.write('   • Company List: /companies/list/')
        
        self.stdout.write('\n3. Try these features:')
        self.stdout.write('   • Switch between company contexts')
        self.stdout.write('   • View partnership details and analytics')
        self.stdout.write('   • Create new partnerships by NIP')
        self.stdout.write('   • Generate partnership reports')
        self.stdout.write('   • Manage invoice templates')