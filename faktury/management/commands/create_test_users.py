"""
Management command to create test users and test auto-accounting functionality
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from faktury.models import Firma, Kontrahent, Partnerstwo, Faktura, PozycjaFaktury, Produkt, UserProfile
from django.utils.module_loading import import_string

# Import services functions directly from the business_services.py file
from faktury.business_services import auto_ksieguj_fakture_service, sprawdz_partnerstwa_auto_ksiegowanie
from decimal import Decimal
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create test users and test auto-accounting functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Create test users with companies and partnerships',
        )
        parser.add_argument(
            '--test-auto-accounting',
            action='store_true',
            help='Test auto-accounting functionality',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing test data',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all operations (clean, create users, test)',
        )

    def handle(self, *args, **options):
        if options['all']:
            self.clean_test_data()
            self.create_test_users()
            self.test_auto_accounting()
        else:
            if options['clean']:
                self.clean_test_data()
            if options['create_users']:
                self.create_test_users()
            if options['test_auto_accounting']:
                self.test_auto_accounting()

    def clean_test_data(self):
        """Clean existing test data"""
        self.stdout.write(self.style.WARNING('🧹 Czyszczenie danych testowych...'))
        
        # Delete test users and related data
        test_usernames = ['testfirma1', 'testfirma2', 'testfirma3', 'testklient1']
        
        for username in test_usernames:
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f"Usuwanie użytkownika: {username}")
                user.delete()
            except User.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS('✅ Dane testowe zostały wyczyszczone'))

    def create_test_users(self):
        """Create test users with companies and partnerships"""
        self.stdout.write(self.style.SUCCESS('👥 Tworzenie użytkowników testowych...'))
        
        with transaction.atomic():
            # User 1 - Firma A (Dostawca IT)
            user1 = User.objects.create_user(
                username='testfirma1',
                email='firma1@test.com',
                password='Test123!',
                first_name='Jan',
                last_name='Kowalski'
            )
            
            profile1 = UserProfile.objects.create(
                user=user1,
                imie='Jan',
                nazwisko='Kowalski',
                telefon='+48123456789'
            )
            
            firma1 = Firma.objects.create(
                user=user1,
                nazwa='TechSoft Solutions Sp. z o.o.',
                nip='1234567890',
                regon='123456789',
                ulica='ul. Technologiczna',
                numer_domu='15',
                kod_pocztowy='00-001',
                miejscowosc='Warszawa',
                kraj='Polska'
            )
            
            # User 2 - Firma B (Agencja Marketingowa)
            user2 = User.objects.create_user(
                username='testfirma2',
                email='firma2@test.com',
                password='Test123!',
                first_name='Anna',
                last_name='Nowak'
            )
            
            profile2 = UserProfile.objects.create(
                user=user2,
                imie='Anna',
                nazwisko='Nowak',
                telefon='+48987654321'
            )
            
            firma2 = Firma.objects.create(
                user=user2,
                nazwa='Creative Marketing Agency',
                nip='0987654321',
                regon='987654321',
                ulica='al. Kreatywna',
                numer_domu='25',
                kod_pocztowy='30-001',
                miejscowosc='Kraków',
                kraj='Polska'
            )
            
            # User 3 - Firma C (Księgowość)
            user3 = User.objects.create_user(
                username='testfirma3',
                email='firma3@test.com',
                password='Test123!',
                first_name='Piotr',
                last_name='Wiśniewski'
            )
            
            profile3 = UserProfile.objects.create(
                user=user3,
                imie='Piotr',
                nazwisko='Wiśniewski',
                telefon='+48555666777'
            )
            
            firma3 = Firma.objects.create(
                user=user3,
                nazwa='ProBooks Biuro Rachunkowe',
                nip='5555666777',
                regon='555666777',
                ulica='ul. Księgowa',
                numer_domu='8',
                kod_pocztowy='50-001',
                miejscowosc='Wrocław',
                kraj='Polska'
            )
            
            # Klient testowy (bez firmy)
            user_klient = User.objects.create_user(
                username='testklient1',
                email='klient1@test.com',
                password='Test123!',
                first_name='Maria',
                last_name='Testowa'
            )
            
            profile_klient = UserProfile.objects.create(
                user=user_klient,
                imie='Maria',
                nazwisko='Testowa',
                telefon='+48111222333'
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Utworzono użytkownika: {user1.username} - {firma1.nazwa}'))
            self.stdout.write(self.style.SUCCESS(f'✅ Utworzono użytkownika: {user2.username} - {firma2.nazwa}'))
            self.stdout.write(self.style.SUCCESS(f'✅ Utworzono użytkownika: {user3.username} - {firma3.nazwa}'))
            self.stdout.write(self.style.SUCCESS(f'✅ Utworzono klienta: {user_klient.username}'))
            
            # Tworzenie kontrahentów wzajemnych
            self.create_cross_contractors(user1, user2, firma1, firma2)
            self.create_cross_contractors(user1, user3, firma1, firma3)
            self.create_cross_contractors(user2, user3, firma2, firma3)
            
            # Tworzenie partnerstw
            self.create_partnerships(firma1, firma2, firma3)
            
            # Tworzenie produktów testowych
            self.create_test_products(user1, user2, user3)

    def create_cross_contractors(self, user1, user2, firma1, firma2):
        """Create cross contractors between companies"""
        # Firma1 jako kontrahent w systemie firmy2 (użytkownik user2 dodaje kontrahenta firma1)
        try:
            kontrahent1_w_2, created = Kontrahent.objects.get_or_create(
                user=user2,
                nip=firma1.nip,
                defaults={
                    'nazwa': firma1.nazwa,
                    'ulica': firma1.ulica,
                    'numer_domu': firma1.numer_domu,
                    'kod_pocztowy': firma1.kod_pocztowy,
                    'miejscowosc': firma1.miejscowosc,
                    'czy_firma': True,
                    'firma': firma1
                }
            )
        except Exception as e:
            # Jeśli wystąpi błąd, sprawdź czy kontrahent już istnieje
            kontrahent1_w_2 = Kontrahent.objects.filter(user=user2, nip=firma1.nip).first()
            if not kontrahent1_w_2:
                self.stdout.write(self.style.ERROR(f"Błąd tworzenia kontrahenta {firma1.nazwa}: {e}"))
        
        # Firma2 jako kontrahent w systemie firmy1 (użytkownik user1 dodaje kontrahenta firma2)
        try:
            kontrahent2_w_1, created = Kontrahent.objects.get_or_create(
                user=user1,
                nip=firma2.nip,
                defaults={
                    'nazwa': firma2.nazwa,
                    'ulica': firma2.ulica,
                    'numer_domu': firma2.numer_domu,
                    'kod_pocztowy': firma2.kod_pocztowy,
                    'miejscowosc': firma2.miejscowosc,
                    'czy_firma': True,
                    'firma': firma2
                }
            )
        except Exception as e:
            # Jeśli wystąpi błąd, sprawdź czy kontrahent już istnieje
            kontrahent2_w_1 = Kontrahent.objects.filter(user=user1, nip=firma2.nip).first()
            if not kontrahent2_w_1:
                self.stdout.write(self.style.ERROR(f"Błąd tworzenia kontrahenta {firma2.nazwa}: {e}"))
        
        self.stdout.write(f"📋 Utworzono wzajemnych kontrahentów: {firma1.nazwa} ↔ {firma2.nazwa}")

    def create_partnerships(self, firma1, firma2, firma3):
        """Create partnerships between companies"""
        # Partnerstwo 1: TechSoft ↔ Creative (z auto-księgowaniem)
        partnerstwo1 = Partnerstwo.objects.create(
            firma1=firma1,
            firma2=firma2,
            aktywne=True,
            auto_ksiegowanie=True,
            typ_partnerstwa='wspolpraca',
            opis='Współpraca w projektach IT i marketingu',
            data_rozpoczecia=date.today() - timedelta(days=30)
        )
        
        # Partnerstwo 2: TechSoft ↔ ProBooks (z auto-księgowaniem)
        partnerstwo2 = Partnerstwo.objects.create(
            firma1=firma1,
            firma2=firma3,
            aktywne=True,
            auto_ksiegowanie=True,
            typ_partnerstwa='dostawca',
            opis='Usługi księgowe dla TechSoft',
            data_rozpoczecia=date.today() - timedelta(days=60)
        )
        
        # Partnerstwo 3: Creative ↔ ProBooks (bez auto-księgowania)
        partnerstwo3 = Partnerstwo.objects.create(
            firma1=firma2,
            firma2=firma3,
            aktywne=True,
            auto_ksiegowanie=False,
            typ_partnerstwa='wspolpraca',
            opis='Sporadyczna współpraca w projektach',
            data_rozpoczecia=date.today() - timedelta(days=15)
        )
        
        self.stdout.write(self.style.SUCCESS(f'🤝 Utworzono partnerstwo: {firma1.nazwa} ↔ {firma2.nazwa} (AUTO: ON)'))
        self.stdout.write(self.style.SUCCESS(f'🤝 Utworzono partnerstwo: {firma1.nazwa} ↔ {firma3.nazwa} (AUTO: ON)'))
        self.stdout.write(self.style.SUCCESS(f'🤝 Utworzono partnerstwo: {firma2.nazwa} ↔ {firma3.nazwa} (AUTO: OFF)'))

    def create_test_products(self, user1, user2, user3):
        """Create test products for each company"""
        # Produkty TechSoft
        Produkt.objects.create(
            user=user1,
            nazwa='Tworzenie strony internetowej',
            cena_netto=Decimal('5000.00'),
            vat='23',
            jednostka='szt'
        )
        
        Produkt.objects.create(
            user=user1,
            nazwa='Konsultacje IT',
            cena_netto=Decimal('250.00'),
            vat='23',
            jednostka='godz'
        )
        
        # Produkty Creative
        Produkt.objects.create(
            user=user2,
            nazwa='Kampania reklamowa',
            cena_netto=Decimal('3000.00'),
            vat='23',
            jednostka='szt'
        )
        
        Produkt.objects.create(
            user=user2,
            nazwa='Projekt graficzny',
            cena_netto=Decimal('800.00'),
            vat='23',
            jednostka='szt'
        )
        
        # Produkty ProBooks
        Produkt.objects.create(
            user=user3,
            nazwa='Prowadzenie księgowości',
            cena_netto=Decimal('500.00'),
            vat='23',
            jednostka='mies'
        )
        
        Produkt.objects.create(
            user=user3,
            nazwa='Deklaracja VAT',
            cena_netto=Decimal('150.00'),
            vat='23',
            jednostka='szt'
        )
        
        self.stdout.write(self.style.SUCCESS('📦 Utworzono produkty testowe dla wszystkich firm'))

    def test_auto_accounting(self):
        """Test auto-accounting functionality"""
        self.stdout.write(self.style.SUCCESS('🧮 Testowanie auto-księgowania...'))
        
        try:
            # Get test companies
            user1 = User.objects.get(username='testfirma1')
            user2 = User.objects.get(username='testfirma2')
            user3 = User.objects.get(username='testfirma3')
            
            firma1 = Firma.objects.get(user=user1)  # TechSoft
            firma2 = Firma.objects.get(user=user2)  # Creative
            firma3 = Firma.objects.get(user=user3)  # ProBooks
            
            # Get contractors
            kontrahent_creative = Kontrahent.objects.get(user=user1, firma=firma2)
            kontrahent_probooks = Kontrahent.objects.get(user=user1, firma=firma3)
            
            # Get products
            produkt_konsultacje = Produkt.objects.get(user=user1, nazwa='Konsultacje IT')
            produkt_strona = Produkt.objects.get(user=user1, nazwa='Tworzenie strony internetowej')
            
            self.stdout.write('📋 Scenario 1: TechSoft wystawia fakturę dla Creative (z auto-księgowaniem)')
            
            # Create invoice from TechSoft to Creative
            faktura1 = Faktura.objects.create(
                user=user1,
                sprzedawca=firma1,
                nabywca=kontrahent_creative,
                typ_faktury='sprzedaz',
                numer=f'FS/2024/001',
                data_wystawienia=date.today(),
                data_sprzedazy=date.today(),
                termin_platnosci=date.today() + timedelta(days=14),
                status='wystawiona',
                miejsce_wystawienia='Warszawa'
            )
            
            # Add invoice items
            PozycjaFaktury.objects.create(
                faktura=faktura1,
                nazwa=produkt_konsultacje.nazwa,
                ilosc=10,
                jednostka=produkt_konsultacje.jednostka,
                cena_netto=produkt_konsultacje.cena_netto,
                vat=produkt_konsultacje.vat
            )
            
            # Test auto-accounting
            self.stdout.write('🔄 Uruchamianie auto-księgowania...')
            auto_ksieguj_fakture_service(faktura1)
            
            # Check if corresponding cost invoice was created
            faktura_koszt = Faktura.objects.filter(
                user=user2,
                typ_faktury='koszt'
            ).first()
            
            if faktura_koszt:
                self.stdout.write(self.style.SUCCESS(f'✅ Auto-księgowanie SUKCES! Utworzono fakturę kosztową: {faktura_koszt.numer}'))
                self.stdout.write(f'   📄 Faktura sprzedaży: {faktura1.numer} (TechSoft)')
                self.stdout.write(f'   📄 Faktura kosztowa: {faktura_koszt.numer} (Creative)')
                self.stdout.write(f'   💰 Kwota: {faktura1.wartosc_brutto if hasattr(faktura1, "wartosc_brutto") else "N/A"} zł')
            else:
                self.stdout.write(self.style.ERROR('❌ Auto-księgowanie nie działało - brak faktury kosztowej'))
            
            self.stdout.write('\n📋 Scenario 2: TechSoft wystawia fakturę dla ProBooks (z auto-księgowaniem)')
            
            # Create second invoice
            faktura2 = Faktura.objects.create(
                user=user1,
                sprzedawca=firma1,
                nabywca=kontrahent_probooks,
                typ_faktury='sprzedaz',
                numer=f'FS/2024/002',
                data_wystawienia=date.today(),
                data_sprzedazy=date.today(),
                termin_platnosci=date.today() + timedelta(days=30),
                status='wystawiona',
                miejsce_wystawienia='Warszawa'
            )
            
            PozycjaFaktury.objects.create(
                faktura=faktura2,
                nazwa=produkt_strona.nazwa,
                ilosc=1,
                jednostka=produkt_strona.jednostka,
                cena_netto=produkt_strona.cena_netto,
                vat=produkt_strona.vat
            )
            
            # Test auto-accounting
            auto_ksieguj_fakture_service(faktura2)
            
            # Check results
            faktura_koszt2 = Faktura.objects.filter(
                user=user3,
                typ_faktury='koszt'
            ).first()
            
            if faktura_koszt2:
                self.stdout.write(self.style.SUCCESS(f'✅ Auto-księgowanie SUKCES! Utworzono fakturę kosztową: {faktura_koszt2.numer}'))
                self.stdout.write(f'   📄 Faktura sprzedaży: {faktura2.numer} (TechSoft)')
                self.stdout.write(f'   📄 Faktura kosztowa: {faktura_koszt2.numer} (ProBooks)')
                self.stdout.write(f'   💰 Kwota: {faktura2.wartosc_brutto if hasattr(faktura2, "wartosc_brutto") else "N/A"} zł')
            else:
                self.stdout.write(self.style.ERROR('❌ Auto-księgowanie nie działało - brak faktury kosztowej'))
            
            # Test bulk auto-accounting check
            self.stdout.write('\n📋 Scenario 3: Sprawdzanie masowego auto-księgowania')
            
            processed_count = sprawdz_partnerstwa_auto_ksiegowanie(user1)
            self.stdout.write(f'📊 Przetworzono {processed_count} faktur w sprawdzeniu masowym')
            
            # Summary
            self.stdout.write('\n📊 PODSUMOWANIE TESTÓW:')
            total_faktury_sprzedaz = Faktura.objects.filter(typ_faktury='sprzedaz').count()
            total_faktury_koszt = Faktura.objects.filter(typ_faktury='koszt').count()
            total_partnerstwa = Partnerstwo.objects.filter(auto_ksiegowanie=True).count()
            
            self.stdout.write(f'   📄 Faktury sprzedaży: {total_faktury_sprzedaz}')
            self.stdout.write(f'   📄 Faktury kosztowe: {total_faktury_koszt}')
            self.stdout.write(f'   🤝 Partnerstwa z auto-księgowaniem: {total_partnerstwa}')
            
            if total_faktury_koszt > 0:
                self.stdout.write(self.style.SUCCESS('🎉 AUTO-KSIĘGOWANIE DZIAŁA POPRAWNIE!'))
            else:
                self.stdout.write(self.style.ERROR('💥 AUTO-KSIĘGOWANIE NIE DZIAŁA'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Błąd podczas testowania: {str(e)}'))
            logger.error(f"Auto-accounting test error: {e}", exc_info=True)

    def print_login_info(self):
        """Print login information for test users"""
        self.stdout.write('\n🔐 DANE LOGOWANIA UŻYTKOWNIKÓW TESTOWYCH:')
        self.stdout.write('='*50)
        
        test_users = [
            ('testfirma1', 'TechSoft Solutions', 'Usługi IT'),
            ('testfirma2', 'Creative Marketing', 'Marketing'),
            ('testfirma3', 'ProBooks', 'Księgowość'),
            ('testklient1', 'Klient Testowy', 'Osoba fizyczna')
        ]
        
        for username, company, desc in test_users:
            self.stdout.write(f'👤 Username: {username}')
            self.stdout.write(f'   Password: Test123!')
            self.stdout.write(f'   Company: {company}')
            self.stdout.write(f'   Type: {desc}')
            self.stdout.write('   ' + '-'*30)
