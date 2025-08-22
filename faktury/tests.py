from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Firma, Kontrahent, Partnerstwo, Faktura, PozycjaFaktury  # Import PozycjaFaktury
from django.contrib.messages import get_messages
import datetime # Import datetime

class AutoKsiegowanieTestCase(TestCase):
    def setUp(self):
        # Tworzenie użytkowników
        self.user1 = User.objects.create_user(username='firma1', password='test123')
        self.user2 = User.objects.create_user(username='firma2', password='test123')

        # Tworzenie firm
        self.firma1 = Firma.objects.create(user=self.user1, nazwa="Testowa Firma 1", nip="1234567890")
        self.firma2 = Firma.objects.create(user=self.user2, nazwa="Testowa Firma 2", nip="0987654321")

        # Tworzenie kontrahentów
        self.kontrahent1 = Kontrahent.objects.create(
            user=self.user1,
            nazwa="Kontrahent 1",
            nip="1234567890"
        )
        self.kontrahent2 = Kontrahent.objects.create(
            user=self.user2,
            nazwa="Kontrahent 2",
            nip="0987654321"
        )

        # Tworzenie partnerstwa
        self.partnerstwo = Partnerstwo.objects.create(
            firma1=self.firma1,
            firma2=self.firma2,
            auto_ksiegowanie=True #Added check for auto_ksiegowanie
        )

    def test_autoksiegowanie(self):
        # Logowanie jako firma1
        client = Client()
        client.login(username='firma1', password='test123')

        # Wysłanie danych faktury
        response = client.post(reverse('dodaj_fakture'), {
            'numer': 'TEST/01/2025',
            'data_wystawienia': '2025-03-03',
            'data_sprzedazy': '2025-03-03',
            'miejsce_wystawienia': 'Warszawa',
            'nabywca': self.kontrahent2.id,
            'typ_faktury': 'sprzedaz',
            'typ_dokumentu': 'FV',  # <--- ADD THIS
            'sposob_platnosci': 'przelew',
            'termin_platnosci': '2025-03-10',
            'status': 'wystawiona',
            'waluta': 'PLN',
            'pozycje-TOTAL_FORMS': '1',
            'pozycje-INITIAL_FORMS': '0',
            'pozycje-0-nazwa': 'Usługa testowa',
            'pozycje-0-ilosc': '1',
            'pozycje-0-jednostka': 'szt',
            'pozycje-0-cena_netto': '100.00',
            'pozycje-0-vat': '23',
            'pozycje-0-id': '', #Add ID
            'pozycje-0-faktura': '', #Add faktura
            'pozycje-0-rabat': '0', #Add rabat
            'pozycje-0-rabat_typ': 'procent', #Add rabat_typ
        })

        # Sprawdź czy odpowiedź jest poprawna (przekierowanie)
        self.assertEqual(response.status_code, 302)

        # Sprawdź czy utworzono fakturę (firma1)
        faktura1 = Faktura.objects.filter(user=self.user1).first()
        self.assertIsNotNone(faktura1)

        # Sprawdź czy utworzono kopię faktury u partnera (firma2)
        faktura2 = Faktura.objects.filter(user=self.user2).first()
        self.assertIsNotNone(faktura2)

        # Check values of faktura1
        # Don't hardcode the invoice number.  Check that it's NOT None, and matches the expected pattern.
        self.assertIsNotNone(faktura1.numer)
        self.assertTrue(faktura1.numer.startswith('FV/')) #Automatyczny numer
        self.assertEqual(faktura1.data_wystawienia.strftime('%Y-%m-%d'), '2025-03-03')
        self.assertEqual(faktura1.nabywca, self.kontrahent2)
        self.assertEqual(faktura1.typ_faktury, 'sprzedaz')
        self.assertEqual(faktura1.sprzedawca, self.firma1)
        self.assertEqual(faktura1.user, self.user1)


        # Check values of faktura2 (the synchronized copy)
        self.assertIsNotNone(faktura2.numer)
        self.assertTrue(faktura2.numer.startswith('P/FV/'))  # Automatyczny numer z P/
        self.assertEqual(faktura2.data_wystawienia.strftime('%Y-%m-%d'), '2025-03-03')
        self.assertEqual(faktura2.nabywca.nazwa, "Testowa Firma 1") # Check reversed buyer/seller
        self.assertEqual(faktura2.sprzedawca, self.firma2) # Check reversed buyer/seller
        self.assertEqual(faktura2.typ_faktury, 'koszt')  # VERY IMPORTANT: Check that it's a 'koszt'
        self.assertEqual(faktura2.user, self.user2)
        self.assertEqual(faktura2.status, 'od partnera')

        # Check invoice items (faktura1)
        pozycja1 = PozycjaFaktury.objects.filter(faktura=faktura1).first()
        self.assertIsNotNone(pozycja1)
        self.assertEqual(pozycja1.nazwa, 'Usługa testowa')
        self.assertEqual(float(pozycja1.cena_netto), 100.00)  # Convert Decimal to float for comparison

        # Check invoice items (faktura2)
        pozycja2 = PozycjaFaktury.objects.filter(faktura=faktura2).first()
        self.assertIsNotNone(pozycja2)
        self.assertEqual(pozycja2.nazwa, 'Usługa testowa')
        self.assertEqual(float(pozycja2.cena_netto), 100.00)

        #Check if partnerstwo is created correctly
        self.assertTrue(self.partnerstwo.auto_ksiegowanie)

    def test_autoksiegowanie_no_firma(self):
        #Test case when user does not have Firma
        client = Client()
        user3 = User.objects.create_user(username='firma3', password='test123')
        client.login(username='firma3', password='test123')
        response = client.post(reverse('dodaj_fakture'), {
            'numer': 'TEST/01/2025',
            'data_wystawienia': '2025-03-03',
            'data_sprzedazy': '2025-03-03',
            'miejsce_wystawienia': 'Warszawa',
            'nabywca': self.kontrahent2.id,
            'typ_faktury': 'sprzedaz',
            'typ_dokumentu': 'FV',  # <--- ADD THIS
            'sposob_platnosci': 'przelew',
            'termin_platnosci': '2025-03-10',
            'status': 'wystawiona',
            'waluta': 'PLN',
            'pozycje-TOTAL_FORMS': '1',
            'pozycje-INITIAL_FORMS': '0',
            'pozycje-0-nazwa': 'Usługa testowa',
            'pozycje-0-ilosc': '1',
            'pozycje-0-jednostka': 'szt',
            'pozycje-0-cena_netto': '100.00',
            'pozycje-0-vat': '23',
            'pozycje-0-id': '',
            'pozycje-0-faktura': '',
            'pozycje-0-rabat': '0',
            'pozycje-0-rabat_typ': 'procent',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dodaj_firme'))  # Check for redirect
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Uzupełnij dane swojej firmy przed wystawieniem faktury.") # Corrected assertion

    def test_autoksiegowanie_form_invalid(self):
        #Test with invalid form
        client = Client()
        client.login(username='firma1', password='test123')

        # Invalid data (missing required field 'data_wystawienia')
        response = client.post(reverse('dodaj_fakture'), {
            'numer': 'TEST/01/2025',
            # 'data_wystawienia': '2025-03-03',  # Missing required field
            'data_sprzedazy': '2025-03-03',
            'miejsce_wystawienia': 'Warszawa',
            'nabywca': self.kontrahent2.id,
            'typ_faktury': 'sprzedaz',
            'sposob_platnosci': 'przelew',
            'termin_platnosci': '2025-03-10',
            'status': 'wystawiona',
            'waluta': 'PLN',
            'pozycje-TOTAL_FORMS': '1',
            'pozycje-INITIAL_FORMS': '0',
            'pozycje-0-nazwa': 'Usługa testowa',
            'pozycje-0-ilosc': '1',
            'pozycje-0-jednostka': 'szt',
            'pozycje-0-cena_netto': '100.00',
            'pozycje-0-vat': '23',
            'pozycje-0-id': '', #Add ID
            'pozycje-0-faktura': '', #Add faktura
            'pozycje-0-rabat': '0', #Add rabat
            'pozycje-0-rabat_typ': 'procent', #Add rabat_typ
        })
        self.assertEqual(response.status_code, 200)  # Expect 200 OK (form re-renders with errors)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Popraw błędy w formularzu" in str(message) for message in messages))