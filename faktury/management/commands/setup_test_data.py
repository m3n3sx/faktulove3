"""
Management command to create test companies and partnerships for auto-accounting system testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faktury.models import Firma, Partnerstwo, Kontrahent
from django.db import transaction
import random


class Command(BaseCommand):
    help = 'Creates test companies and partnerships for auto-accounting system testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of test users to create (default: 5)'
        )
        parser.add_argument(
            '--partnerships',
            type=int,
            default=3,
            help='Number of partnerships to create (default: 3)'
        )

    def handle(self, *args, **options):
        users_count = options['users']
        partnerships_count = options['partnerships']

        with transaction.atomic():
            self.stdout.write('Creating test data for auto-accounting system...')
            
            # Create test users and companies
            test_users = []
            test_companies = []
            
            for i in range(users_count):
                # Create user
                username = f'testuser{i+1}'
                email = f'test{i+1}@faktulove.pl'
                
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': f'Test{i+1}',
                        'last_name': 'User',
                        'is_active': True
                    }
                )
                
                if created:
                    user.set_password('testpass123')
                    user.save()
                    self.stdout.write(f'Created user: {username}')
                
                test_users.append(user)
                
                # Create company for user
                company_data = self.get_company_data(i+1)
                firma, created = Firma.objects.get_or_create(
                    user=user,
                    defaults=company_data
                )
                
                if created:
                    self.stdout.write(f'Created company: {firma.nazwa}')
                
                test_companies.append(firma)
                
                # Create some contractors for each company
                self.create_contractors_for_company(user, i+1)
            
            # Create partnerships between companies
            self.create_partnerships(test_companies, partnerships_count)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {users_count} test companies and {partnerships_count} partnerships'
                )
            )
            
            # Display summary
            self.display_summary(test_users, test_companies)

    def get_company_data(self, index):
        """Generate test company data"""
        companies = [
            {
                'nazwa': 'TechSoft Solutions Sp. z o.o.',
                'nip': '1234567890',
                'regon': '123456789',
                'ulica': 'ul. Technologiczna',
                'numer_domu': '15',
                'kod_pocztowy': '00-001',
                'miejscowosc': 'Warszawa',
                'kraj': 'Polska'
            },
            {
                'nazwa': 'Creative Design Studio',
                'nip': '2345678901',
                'regon': '234567890',
                'ulica': 'ul. Artystyczna',
                'numer_domu': '8',
                'kod_pocztowy': '31-001',
                'miejscowosc': 'Kraków',
                'kraj': 'Polska'
            },
            {
                'nazwa': 'Marketing Pro Sp. z o.o.',
                'nip': '3456789012',
                'regon': '345678901',
                'ulica': 'ul. Marketingowa',
                'numer_domu': '22',
                'kod_pocztowy': '50-001',
                'miejscowosc': 'Wrocław',
                'kraj': 'Polska'
            },
            {
                'nazwa': 'Consulting Excellence',
                'nip': '4567890123',
                'regon': '456789012',
                'ulica': 'ul. Doradcza',
                'numer_domu': '5',
                'kod_pocztowy': '80-001',
                'miejscowosc': 'Gdańsk',
                'kraj': 'Polska'
            },
            {
                'nazwa': 'Innovation Labs Sp. z o.o.',
                'nip': '5678901234',
                'regon': '567890123',
                'ulica': 'ul. Innowacyjna',
                'numer_domu': '12',
                'kod_pocztowy': '60-001',
                'miejscowosc': 'Poznań',
                'kraj': 'Polska'
            }
        ]
        
        return companies[(index - 1) % len(companies)]

    def create_contractors_for_company(self, user, company_index):
        """Create test contractors for a company"""
        contractors_data = [
            {
                'nazwa': 'ABC Supplies Sp. z o.o.',
                'nip': f'11{company_index}1234567',
                'ulica': 'ul. Dostawcza',
                'numer_domu': '10',
                'kod_pocztowy': '00-100',
                'miejscowosc': 'Warszawa',
                'telefon': '+48 22 111 22 33',
                'email': 'orders@abc-supplies.pl',
                'czy_firma': True
            },
            {
                'nazwa': 'XYZ Services',
                'nip': f'22{company_index}2345678',
                'ulica': 'ul. Usługowa',
                'numer_domu': '20',
                'kod_pocztowy': '31-100',
                'miejscowosc': 'Kraków',
                'telefon': '+48 12 222 33 44',
                'email': 'info@xyz-services.pl',
                'czy_firma': True
            },
            {
                'nazwa': 'Professional Partners',
                'nip': f'33{company_index}3456789',
                'ulica': 'ul. Partnerska',
                'numer_domu': '30',
                'kod_pocztowy': '50-100',
                'miejscowosc': 'Wrocław',
                'telefon': '+48 71 333 44 55',
                'email': 'contact@partners.pl',
                'czy_firma': True
            }
        ]
        
        for contractor_data in contractors_data:
            contractor, created = Kontrahent.objects.get_or_create(
                user=user,
                nip=contractor_data['nip'],
                defaults=contractor_data
            )
            
            if created:
                self.stdout.write(f'  Created contractor: {contractor.nazwa}')

    def create_partnerships(self, companies, partnerships_count):
        """Create partnerships between companies"""
        if len(companies) < 2:
            self.stdout.write('Not enough companies to create partnerships')
            return
        
        partnerships_created = 0
        
        for i in range(partnerships_count):
            # Select two different companies randomly
            company1, company2 = random.sample(companies, 2)
            
            # Create partnership
            partnership, created = Partnerstwo.objects.get_or_create(
                firma1=company1,
                firma2=company2,
                defaults={
                    'opis': f'Strategiczne partnerstwo między {company1.nazwa} a {company2.nazwa}',
                    'data_rozpoczecia': '2024-01-01',
                    'aktywne': True,
                    'auto_ksiegowanie': True,
                    'typ_partnerstwa': 'wspolpraca'
                }
            )
            
            if created:
                partnerships_created += 1
                self.stdout.write(f'Created partnership: {company1.nazwa} - {company2.nazwa}')
        
        self.stdout.write(f'Total partnerships created: {partnerships_created}')

    def display_summary(self, users, companies):
        """Display summary of created test data"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('TEST DATA SUMMARY')
        self.stdout.write('='*50)
        
        for i, (user, company) in enumerate(zip(users, companies)):
            self.stdout.write(f'\nTest User {i+1}:')
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Password: testpass123')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Company: {company.nazwa}')
            self.stdout.write(f'  NIP: {company.nip}')
        
        partnerships = Partnerstwo.objects.all()
        if partnerships.exists():
            self.stdout.write(f'\nPartnerships ({partnerships.count()}):')
            for partnership in partnerships:
                self.stdout.write(f'  - {partnership.firma1.nazwa} ↔ {partnership.firma2.nazwa} ({partnership.get_typ_partnerstwa_display()})')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('You can now test the auto-accounting system with these companies!')
        self.stdout.write('='*50)