"""
Enhanced models for Polish invoice system
Wszystkie dokumenty zgodne z polskim prawem VAT
"""
from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime


class EnhancedFaktura(models.Model):
    """
    Rozszerzony model faktury zgodny z polskim prawem VAT
    Art. 106e-106p ustawy o VAT
    """
    
    # Typy dokumentów zgodne z polskim prawem
    TYP_DOKUMENTU_CHOICES = [
        # Faktury podstawowe
        ('FV', 'Faktura VAT'),
        ('FVS', 'Faktura VAT Sprzedażowa'),
        ('FVK', 'Faktura VAT Kosztowa'),
        ('FP', 'Faktura Pro Forma'),
        
        # Faktury korygujące
        ('KOR', 'Faktura Korygująca'),
        ('KP', 'Korekta Pozytywna'),
        ('KN', 'Korekta Negatywna'),
        
        # Faktury specjalne
        ('FZ', 'Faktura Zaliczkowa'),
        ('FK', 'Faktura Końcowa'),
        ('FO', 'Faktura Ostateczna'),
        ('FA', 'Faktura Abonamentowa'),
        
        # Dokumenty sprzedaży
        ('RC', 'Rachunek'),
        ('PAR', 'Paragon Fiskalny'),
        ('WZ', 'Wydanie Zewnętrzne'),
        ('KW', 'Korekta WZ'),
        
        # Dokumenty bankowe i kasowe
        ('KP_DOK', 'KP - Dokument Kasowy Przychodowy'),
        ('KW_DOK', 'KW - Dokument Kasowy Rozchodowy'),
        ('WB', 'Wyciąg Bankowy'),
        
        # Inne dokumenty
        ('NOT', 'Nota księgowa'),
        ('DU', 'Dowód Uznania'),
        ('DO', 'Dowód Obciążenia'),
        ('WDT', 'Faktura WDT (wewnątrzwspólnotowa dostawa)'),
        ('IMP', 'Faktura Importowa'),
        ('EXP', 'Faktura Eksportowa'),
    ]
    
    # Stawki VAT zgodne z polskim prawem
    VAT_RATES = [
        ('23', '23% - stawka podstawowa'),
        ('8', '8% - stawka obniżona I'),
        ('5', '5% - stawka obniżona II'),
        ('0', '0% - stawka zerowa'),
        ('zw', 'zw - zwolniona z VAT'),
        ('np', 'np - nie podlega VAT'),
        ('oo', 'oo - odwrotne obciążenie'),
    ]
    
    # Rodzaje zwolnień z VAT
    POWOD_ZWOLNIENIA_CHOICES = [
        # Art. 43 - zwolnienia podmiotowe
        ('art43_1', 'Art. 43 ust. 1 - mały podatnik'),
        ('art43_2', 'Art. 43 ust. 2 - działalność nieopodatkowana'),
        
        # Art. 113 - zwolnienia z tytułu wysokości obrotów
        ('art113_1', 'Art. 113 ust. 1 - limit 200 tys. PLN'),
        ('art113_9', 'Art. 113 ust. 9 - limit 50 tys. EUR'),
        
        # Inne zwolnienia
        ('art82', 'Art. 82 ust. 3 - rozporządzenie MF'),
        ('art100', 'Art. 100 - dostawa wewnątrzwspólnotowa'),
        ('art15', 'Art. 15 - działalność w interesie publicznym'),
    ]
    
    # Metody płatności
    SPOSOB_PLATNOSCI_CHOICES = [
        ('gotowka', 'Gotówka'),
        ('przelew', 'Przelew bankowy'),
        ('karta', 'Karta płatnicza'),
        ('blik', 'BLIK'),
        ('paypal', 'PayPal'),
        ('pobranie', 'Za pobraniem'),
        ('czek', 'Czek'),
        ('weksel', 'Weksel'),
        ('kompensata', 'Kompensata'),
        ('dotacja', 'Dotacja/Refundacja'),
    ]
    
    # Status dokumentu
    STATUS_CHOICES = [
        ('projekt', 'Projekt'),
        ('wystawiona', 'Wystawiona'),
        ('wyslana', 'Wysłana'),
        ('dostarczona', 'Dostarczona'),
        ('oplacona', 'Opłacona'),
        ('cz_oplacona', 'Częściowo opłacona'),
        ('przeterminowana', 'Przeterminowana'),
        ('anulowana', 'Anulowana'),
        ('skorygowana', 'Skorygowana'),
        ('zaksiegowana', 'Zaksięgowana'),
    ]
    
    # Waluty
    WALUTA_CHOICES = [
        ('PLN', 'Polski złoty'),
        ('EUR', 'Euro'),
        ('USD', 'Dolar amerykański'),
        ('GBP', 'Funt brytyjski'),
        ('CHF', 'Frank szwajcarski'),
        ('CZK', 'Korona czeska'),
        ('NOK', 'Korona norweska'),
        ('SEK', 'Korona szwedzka'),
    ]
    
    # Typ transakcji
    TYP_TRANSAKCJI_CHOICES = [
        ('krajowa', 'Transakcja krajowa'),
        ('uew', 'Transakcja wewnątrzwspólnotowa UE'),
        ('eksport', 'Eksport (poza UE)'),
        ('import', 'Import'),
        ('trójstronna', 'Transakcja trójstronna'),
        ('usługa_odwrotne', 'Usługa z odwrotnym obciążeniem'),
    ]
    
    # Podstawowe pola faktury
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    
    # Identyfikacja dokumentu
    typ_dokumentu = models.CharField(
        max_length=10, 
        choices=TYP_DOKUMENTU_CHOICES, 
        default='FV',
        verbose_name="Typ dokumentu"
    )
    numer = models.CharField(max_length=100, verbose_name="Numer dokumentu")
    numer_wewnetrzny = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="Numer wewnętrzny"
    )
    
    # Daty
    data_wystawienia = models.DateField(
        default=datetime.date.today,
        verbose_name="Data wystawienia"
    )
    data_sprzedazy = models.DateField(verbose_name="Data sprzedaży/wykonania")
    data_dostawy = models.DateField(
        blank=True, 
        null=True,
        verbose_name="Data dostawy"
    )
    
    # Miejsce i osoby
    miejsce_wystawienia = models.CharField(
        max_length=255,
        verbose_name="Miejsce wystawienia"
    )
    wystawca = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Osoba wystawiająca"
    )
    odbiorca = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Osoba odbierająca"
    )
    
    # Strony transakcji
    sprzedawca = models.ForeignKey(
        'Firma', 
        on_delete=models.CASCADE, 
        related_name='faktury_sprzedawca',
        verbose_name="Sprzedawca"
    )
    nabywca = models.ForeignKey(
        'Kontrahent', 
        on_delete=models.CASCADE, 
        related_name='faktury_nabywca',
        verbose_name="Nabywca"
    )
    
    # Typ transakcji i zwolnienia
    typ_transakcji = models.CharField(
        max_length=20,
        choices=TYP_TRANSAKCJI_CHOICES,
        default='krajowa',
        verbose_name="Typ transakcji"
    )
    zwolnienie_z_vat = models.BooleanField(
        default=False,
        verbose_name="Zwolniona z VAT"
    )
    powod_zwolnienia = models.CharField(
        max_length=20,
        choices=POWOD_ZWOLNIENIA_CHOICES,
        blank=True,
        null=True,
        verbose_name="Podstawa prawna zwolnienia"
    )
    
    # Płatność
    sposob_platnosci = models.CharField(
        max_length=20,
        choices=SPOSOB_PLATNOSCI_CHOICES,
        default='przelew',
        verbose_name="Sposób płatności"
    )
    termin_platnosci = models.DateField(verbose_name="Termin płatności")
    
    # Dane bankowe
    numer_konta_bankowego = models.CharField(
        max_length=34,  # IBAN może mieć do 34 znaków
        blank=True,
        null=True,
        verbose_name="Numer konta bankowego"
    )
    swift_bic = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name="Kod SWIFT/BIC"
    )
    bank_nazwa = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nazwa banku"
    )
    
    # Tytuł przelewu
    tytul_przelewu = models.TextField(
        blank=True,
        null=True,
        verbose_name="Tytuł przelewu"
    )
    
    # Waluta i kursy
    waluta = models.CharField(
        max_length=3,
        choices=WALUTA_CHOICES,
        default='PLN',
        verbose_name="Waluta"
    )
    kurs_waluty = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name="Kurs waluty"
    )
    data_kursu = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data kursu waluty"
    )
    tabela_kursow = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Tabela kursów NBP"
    )
    
    # Status i płatności
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='wystawiona',
        verbose_name="Status"
    )
    kwota_oplacona = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Kwota opłacona"
    )
    
    # Rabaty globalne
    rabat_procentowy_globalny = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Rabat procentowy globalny"
    )
    rabat_kwotowy_globalny = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name="Rabat kwotowy globalny"
    )
    
    # Kasa fiskalna
    kasa = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Numer kasy fiskalnej"
    )
    nr_paragonu_fiskalnego = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Numer paragonu fiskalnego"
    )
    
    # Dokumenty powiązane
    dokument_podstawowy = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Dokument podstawowy (dla korekt)'
    )
    
    # Uwagi i notatki
    uwagi = models.TextField(
        blank=True,
        null=True,
        verbose_name="Uwagi"
    )
    uwagi_wewnetrzne = models.TextField(
        blank=True,
        null=True,
        verbose_name="Uwagi wewnętrzne"
    )
    
    # Pola systemowe
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    data_modyfikacji = models.DateTimeField(auto_now=True)
    
    # Pola audytu
    czy_wydrukowana = models.BooleanField(default=False)
    czy_wyslana_email = models.BooleanField(default=False)
    
    # JPK/VAT
    jpk_kod_pozycji = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Kod pozycji JPK_VAT"
    )
    
    class Meta:
        verbose_name = "Faktura Enhanced"
        verbose_name_plural = "Faktury Enhanced"
        ordering = ['-data_wystawienia', '-numer']
        
    def __str__(self):
        return f"{self.get_typ_dokumentu_display()} {self.numer}"
    
    @property
    def suma_netto(self):
        """Suma netto wszystkich pozycji"""
        return self.pozycje.aggregate(
            suma=models.Sum('wartosc_netto')
        )['suma'] or Decimal('0.00')
    
    @property
    def suma_vat(self):
        """Suma VAT wszystkich pozycji"""
        return self.pozycje.aggregate(
            suma=models.Sum('kwota_vat')
        )['suma'] or Decimal('0.00')
    
    @property
    def suma_brutto(self):
        """Suma brutto wszystkich pozycji"""
        return self.pozycje.aggregate(
            suma=models.Sum('wartosc_brutto')
        )['suma'] or Decimal('0.00')
    
    @property
    def pozostalo_do_zaplaty(self):
        """Kwota pozostała do zapłaty"""
        return max(self.suma_brutto - self.kwota_oplacona, Decimal('0.00'))
    
    @property
    def czy_oplacona(self):
        """Czy faktura jest w pełni opłacona"""
        return self.kwota_oplacona >= self.suma_brutto
    
    @property
    def czy_przeterminowana(self):
        """Czy faktura jest przeterminowana"""
        if self.czy_oplacona:
            return False
        return datetime.date.today() > self.termin_platnosci
    
    def aktualizuj_status_platnosci(self):
        """Automatyczne aktualizowanie statusu na podstawie wpłat"""
        if self.czy_oplacona:
            self.status = 'oplacona'
        elif self.kwota_oplacona > 0:
            self.status = 'cz_oplacona'
        elif self.czy_przeterminowana:
            self.status = 'przeterminowana'
        else:
            self.status = 'wystawiona'
        
    def save(self, *args, **kwargs):
        self.aktualizuj_status_platnosci()
        super().save(*args, **kwargs)


class EnhancedPozycjaFaktury(models.Model):
    """
    Rozszerzona pozycja faktury zgodna z polskim prawem VAT
    """
    
    # Jednostki miar zgodne z polskimi standardami
    JEDNOSTKI_CHOICES = [
        # Jednostki podstawowe
        ('szt', 'sztuka'),
        ('kg', 'kilogram'),
        ('g', 'gram'),
        ('t', 'tona'),
        ('l', 'litr'),
        ('ml', 'mililitr'),
        ('m', 'metr'),
        ('cm', 'centymetr'),
        ('mm', 'milimetr'),
        ('km', 'kilometr'),
        ('m2', 'metr kwadratowy'),
        ('m3', 'metr sześcienny'),
        
        # Jednostki czasu
        ('godz', 'godzina'),
        ('min', 'minuta'),
        ('dzień', 'dzień'),
        ('mies', 'miesiąc'),
        ('rok', 'rok'),
        
        # Jednostki usług
        ('usł', 'usługa'),
        ('kpl', 'komplet'),
        ('par', 'para'),
        ('op', 'opakowanie'),
        
        # Inne
        ('proc', 'procent'),
        ('pkt', 'punkt'),
        ('inne', 'inne'),
    ]
    
    faktura = models.ForeignKey(
        EnhancedFaktura,
        on_delete=models.CASCADE,
        related_name='pozycje',
        verbose_name="Faktura"
    )
    
    # Numer pozycji na fakturze
    lp = models.PositiveIntegerField(verbose_name="Lp.")
    
    # Opis towaru/usługi
    nazwa = models.CharField(max_length=500, verbose_name="Nazwa towaru/usługi")
    kod_towaru = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Kod towaru"
    )
    pkwiu = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Kod PKWiU"
    )
    
    # Ilość i jednostka
    ilosc = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(0)],
        verbose_name="Ilość"
    )
    jednostka = models.CharField(
        max_length=10,
        choices=JEDNOSTKI_CHOICES,
        default='szt',
        verbose_name="Jednostka miary"
    )
    
    # Ceny
    cena_netto = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(0)],
        verbose_name="Cena jednostkowa netto"
    )
    
    # Rabat
    rabat = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name="Rabat"
    )
    rabat_typ = models.CharField(
        max_length=10,
        choices=[('procent', 'Procent'), ('kwota', 'Kwota')],
        blank=True,
        null=True,
        verbose_name="Typ rabatu"
    )
    
    # VAT
    vat = models.CharField(
        max_length=5,
        choices=EnhancedFaktura.VAT_RATES,
        default='23',
        verbose_name="Stawka VAT"
    )
    
    # Dla transakcji zagranicznych
    cena_netto_waluta = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name="Cena netto w walucie obcej"
    )
    
    class Meta:
        verbose_name = "Pozycja faktury Enhanced"
        verbose_name_plural = "Pozycje faktury Enhanced"
        ordering = ['lp']
        
    def __str__(self):
        return f"{self.lp}. {self.nazwa[:50]}"
    
    @property
    def cena_po_rabacie(self):
        """Cena jednostkowa po rabacie"""
        cena = self.cena_netto
        
        if self.rabat and self.rabat > 0:
            if self.rabat_typ == 'procent':
                cena = cena * (1 - self.rabat / 100)
            elif self.rabat_typ == 'kwota':
                cena = max(cena - self.rabat, Decimal('0.00'))
                
        return cena.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    
    @property
    def wartosc_netto(self):
        """Wartość netto pozycji (ilość × cena po rabacie)"""
        wartosc = self.cena_po_rabacie * self.ilosc
        return wartosc.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def kwota_vat(self):
        """Kwota VAT pozycji"""
        if self.vat in ['zw', 'np', 'oo']:
            return Decimal('0.00')
        
        try:
            stawka_vat = Decimal(self.vat) / 100
            kwota = self.wartosc_netto * stawka_vat
            return kwota.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except (ValueError, TypeError):
            return Decimal('0.00')
    
    @property
    def wartosc_brutto(self):
        """Wartość brutto pozycji (netto + VAT)"""
        return self.wartosc_netto + self.kwota_vat
    
    def save(self, *args, **kwargs):
        # Auto-increment lp if not set
        if not self.lp:
            last_lp = EnhancedPozycjaFaktury.objects.filter(
                faktura=self.faktura
            ).aggregate(models.Max('lp'))['lp__max'] or 0
            self.lp = last_lp + 1
            
        super().save(*args, **kwargs)
