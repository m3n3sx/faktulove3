"""
Management command to create test companies for multi-tenancy demonstration
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faktury.services.company_management_service import CompanyManagementService
from faktury.services.partnership_manager import PartnershipManager


class Command(BaseCommand):
    help = 'Create test companies with realistic Polish business data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-partnerships',
            action='store_true',
            help='Create partnerships between test companies',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of test companies to create (default: 5)',
        )

    def handle(self, *args, **options):
        try:
            company_service = CompanyManagementService()
            
            self.stdout.write('Creating test companies...')
            
            with transaction.atomic():
                created_companies = company_service.create_test_companies()
                
                if created_companies:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created {len(created_companies)} test companies:'
                        )
                    )
                    
                    for company in created_companies:
                        self.stdout.write(f'  - {company.nazwa} (NIP: {company.nip})')
                    
                    # Create partnerships if requested
                    if options['with_partnerships'] and len(created_companies) >= 2:
                        self.stdout.write('\nCreating partnerships between companies...')
                        partnership_manager = PartnershipManager()
                        
                        partnerships_created = 0
                        
                        # Create partnerships between first few companies
                        for i in range(min(3, len(created_companies) - 1)):
                            company1 = created_companies[i]
                            company2 = created_companies[i + 1]
                            
                            partnership_data = {
                                'partner_company_id': company2.id,
                                'typ_partnerstwa': 'wspolpraca',
                                'opis': f'Testowe partnerstwo między {company1.nazwa} a {company2.nazwa}',
                                'aktywne': True,
                                'auto_ksiegowanie': True
                            }
                            
                            partnership = partnership_manager._create_single_partnership(
                                company1, partnership_data
                            )
                            
                            if partnership:
                                partnerships_created += 1
                                self.stdout.write(
                                    f'  - Partnership: {company1.nazwa} ↔ {company2.nazwa}'
                                )
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Successfully created {partnerships_created} partnerships'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING('Test companies already exist or none were created')
                    )
                    
        except Exception as e:
            raise CommandError(f'Error creating test companies: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS('\nTest company creation completed successfully!')
        )
        
        # Display usage instructions
        self.stdout.write('\n' + '='*50)
        self.stdout.write('USAGE INSTRUCTIONS:')
        self.stdout.write('='*50)
        self.stdout.write('1. Login credentials for test companies:')
        self.stdout.write('   Username: [company_name]_admin (e.g., techsoft_admin)')
        self.stdout.write('   Password: TestPassword123!')
        self.stdout.write('')
        self.stdout.write('2. Access the company dashboard at: /companies/dashboard/')
        self.stdout.write('3. Switch between companies using the context switcher')
        self.stdout.write('4. Manage partnerships at: /companies/partnerships/')
        self.stdout.write('')
        self.stdout.write('Test companies created:')
        if created_companies:
            for company in created_companies:
                username = company.user.username
                self.stdout.write(f'  - {company.nazwa}: {username}')