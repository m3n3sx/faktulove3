from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import datetime
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q
import logging
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
logger = logging.getLogger(__name__)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    imie = models.CharField(max_length=100, blank=True)
    nazwisko = models.CharField(max_length=100, blank=True)
    telefon = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username





class Firma(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='firma')
    nazwa = models.CharField(max_length=255)
    nip = models.CharField(max_length=20, unique=True, blank=True, null=True)
    regon = models.CharField(max_length=20, blank=True, null=True)
    ulica = models.CharField(max_length=255)
    numer_domu = models.CharField(max_length=10)
    numer_mieszkania = models.CharField(max_length=10, blank=True, null=True)
    kod_pocztowy = models.CharField(max_length=10)
    miejscowosc = models.CharField(max_length=255)
    kraj = models.CharField(max_length=255, default="Polska")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['nip']),
            models.Index(fields=['nazwa']),
        ]

    def __str__(self):
        return self.nazwa
    
    @property
    def kontrahent(self):
        return self.kontrahent_set.first()

class Partnerstwo(models.Model):
    TYP_PARTNERSTWA_CHOICES = [
        ('dostawca', 'Dostawca'),
        ('odbiorca', 'Odbiorca'),
        ('wspolpraca', 'Współpraca'),
        ('inne', 'Inne'),
    ]
    firma1 = models.ForeignKey(
        'Firma',
        on_delete=models.CASCADE,
        related_name='partnerstwa_jako_firma1',
        verbose_name='Firma 1'
    )
    firma2 = models.ForeignKey(
        'Firma',
        on_delete=models.CASCADE,
        related_name='partnerstwa_jako_firma2',
        verbose_name='Firma 2'
    )
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    aktywne = models.BooleanField(default=True)
    auto_ksiegowanie = models.BooleanField(default=True)
    typ_partnerstwa = models.CharField(
        max_length=20,
        choices=TYP_PARTNERSTWA_CHOICES,
        default='wspolpraca',  # Ustaw domyślną wartość
        verbose_name='Typ partnerstwa'  # Dodaj verbose_name
    )
    opis = models.TextField(blank=True, null=True, verbose_name="Opis partnerstwa")
    data_rozpoczecia = models.DateField(null=True, blank=True, verbose_name="Data rozpoczęcia")
    data_zakonczenia = models.DateField(null=True, blank=True, verbose_name="Data zakończenia")
    class Meta:
        unique_together = [['firma1', 'firma2']]
        verbose_name_plural = 'Partnerstwa'

    def clean(self):
        # Sprawdź, czy firma1 i firma2 istnieją
        if not hasattr(self, 'firma1') or not hasattr(self, 'firma2'):
            return  # Nie waliduj, jeśli brakuje którejś z firm

        # Walidacja, aby firma1 i firma2 były różne
        if self.firma1 == self.firma2:
            raise ValidationError("Firma nie może być partnerem sama ze sobą.")
        
        # Walidacja, aby nie istniało już takie partnerstwo
        if Partnerstwo.objects.filter(
            (Q(firma1=self.firma1, firma2=self.firma2) | Q(firma1=self.firma2, firma2=self.firma1))
        ).exclude(pk=self.pk).exists():  # Dodaj .exclude(pk=self.pk)
             raise ValidationError("Partnerstwo między tymi firmami już istnieje.")

    def __str__(self):
        return f"Partnerstwo: {self.firma1.nazwa} i {self.firma2.nazwa} ({self.get_typ_partnerstwa_display()})" #Dodaj typ partnerstwa do stringa

class Zespol(models.Model):
    firma = models.ForeignKey(Firma, on_delete=models.CASCADE, related_name='zespoly')
    nazwa = models.CharField(max_length=100)
    opis = models.TextField(blank=True, null=True)
    czlonkowie = models.ManyToManyField(User, through='CzlonekZespolu', related_name='zespoly')

    def __str__(self):
        return self.nazwa

class CzlonekZespolu(models.Model):
    ROLE_CHOICES = [
        ('wlasciciel', 'Właściciel'),
        ('pracownik', 'Pracownik'),
        ('ksiegowosc', 'Księgowość'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Make user optional initially
    zespol = models.ForeignKey(Zespol, on_delete=models.CASCADE)
    rola = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pracownik')
    imie = models.CharField(max_length=100)
    nazwisko = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"{self.imie} {self.nazwisko} ({self.zespol.nazwa}) - {self.get_rola_display()}"

    class Meta:
        unique_together = ('user', 'zespol')

class Wiadomosc(models.Model):
    TYP_WIADOMOSCI = [
        ('partner', 'Od partnera'),
        ('system', 'Systemowa'),
        ('zespol', 'Wiadomość zespołowa'),
    ]

    # Universal sender field
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='utworzone_wiadomosci', verbose_name="Autor")
    
    # Pola dla wiadomości między użytkownikami
    nadawca_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='wyslane_wiadomosci')
    odbiorca_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='odebrane_wiadomosci')
    
    # Pola dla wiadomości zespołowych
    zespol = models.ForeignKey(Zespol, on_delete=models.CASCADE, null=True, blank=True, related_name='wiadomosci')
    nadawca_czlonek = models.ForeignKey(CzlonekZespolu, on_delete=models.SET_NULL, null=True, blank=True, related_name='wyslane_wiadomosci_zespol')
    odbiorca_czlonek = models.ForeignKey(CzlonekZespolu, on_delete=models.SET_NULL, null=True, blank=True, related_name='odebrane_wiadomosci_zespol')
    
    temat = models.CharField(max_length=255)
    tresc = models.TextField()
    data_wyslania = models.DateTimeField(auto_now_add=True)
    przeczytana = models.BooleanField(default=False)
    typ_wiadomosci = models.CharField(max_length=10, choices=TYP_WIADOMOSCI, default='partner')
    partnerstwo = models.ForeignKey(Partnerstwo, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Thread support
    wiadomosc_nadrzedna = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='odpowiedzi', verbose_name="Wiadomość nadrzędna")
    
    # Additional fields
    priorytet = models.CharField(
        max_length=10,
        choices=[('niski', 'Niski'), ('normalny', 'Normalny'), ('wysoki', 'Wysoki')],
        default='normalny'
    )
    zalaczniki = models.JSONField(default=list, blank=True)  # Store file attachments info

    def __str__(self):
        if self.typ_wiadomosci == 'zespol':
            return f"{self.temat} (od {self.nadawca_czlonek})"
        return f"{self.temat} ({self.get_typ_wiadomosci_display()})"

    class Meta:
        ordering = ['-data_wyslania']
        verbose_name_plural = "Wiadomości"
        indexes = [
            models.Index(fields=['odbiorca_user', 'przeczytana']),
            models.Index(fields=['typ_wiadomosci', 'data_wyslania']),
            models.Index(fields=['autor', 'data_wyslania']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-set autor if not set
        if not self.autor:
            if self.nadawca_user:
                self.autor = self.nadawca_user
            elif self.nadawca_czlonek:
                self.autor = self.nadawca_czlonek.user
        super().save(*args, **kwargs)
    
    def clean(self):
        # Walidacja dla wiadomości zespołowych
        if self.typ_wiadomosci == 'zespol':
            if not self.zespol:
                raise ValidationError("Wiadomość zespołowa wymaga określenia zespołu")
            if not self.nadawca_czlonek:
                raise ValidationError("Wiadomość zespołowa wymaga określenia nadawcy")
        # Walidacja dla wiadomości między użytkownikami
        elif self.typ_wiadomosci in ['partner', 'system']:
            if not self.odbiorca_user:
                raise ValidationError("Wiadomość wymaga określenia odbiorcy")
    
    @property
    def is_reply(self):
        """Check if this message is a reply"""
        return self.wiadomosc_nadrzedna is not None
    
    @property
    def replies_count(self):
        """Count replies to this message"""
        return self.odpowiedzi.count()
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.przeczytana:
            self.przeczytana = True
            self.save(update_fields=['przeczytana'])
    
    def get_thread_messages(self):
        """Get all messages in this thread"""
        if self.wiadomosc_nadrzedna:
            # This is a reply, get the parent thread
            parent = self.wiadomosc_nadrzedna
            return Wiadomosc.objects.filter(
                models.Q(id=parent.id) | models.Q(wiadomosc_nadrzedna=parent)
            ).order_by('data_wyslania')
        else:
            # This is the parent, get all replies
            return Wiadomosc.objects.filter(
                models.Q(id=self.id) | models.Q(wiadomosc_nadrzedna=self)
            ).order_by('data_wyslania')

class Zadanie(models.Model):
    STATUS_CHOICES = [
        ('nowe', 'Nowe'),
        ('w_trakcie', 'W trakcie'),
        ('zakonczone', 'Zakończone'),
    ]
    PRIORYTET_CHOICES = [
        ('niski', 'Niski'),
        ('sredni', 'Średni'),
        ('wysoki', 'Wysoki'),
    ]
    zespol = models.ForeignKey(Zespol, on_delete=models.CASCADE, related_name='zadania')
    przypisane_do = models.ForeignKey(CzlonekZespolu, on_delete=models.SET_NULL, null=True, blank=True, related_name='zadania')
    tytul = models.CharField(max_length=255)
    opis = models.TextField()
    termin_wykonania = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nowe')
    priorytet = models.CharField(max_length=20, choices=PRIORYTET_CHOICES, default='sredni')
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    data_zakonczenia = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.tytul
    
    class Meta:
        ordering = ['termin_wykonania', 'priorytet']

class Kontrahent(models.Model):
    is_own_company = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nazwa = models.CharField(max_length=255)
    nip = models.CharField(max_length=20, blank=True, null=True)
    regon = models.CharField(max_length=20, blank=True, null=True)
    ulica = models.CharField(max_length=255)
    numer_domu = models.CharField(max_length=10)
    numer_mieszkania = models.CharField(max_length=10, blank=True, null=True)
    kod_pocztowy = models.CharField(max_length=10)
    miejscowosc = models.CharField(max_length=255)
    kraj = models.CharField(max_length=255, default="Polska")
    czy_firma = models.BooleanField(default=True)
    firma = models.ForeignKey(Firma, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Powiązana firma"))
    email = models.EmailField(blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True, null=True)
    telefon_komorkowy = models.CharField(max_length=20, blank=True, null=True)
    adres_korespondencyjny_ulica = models.CharField(max_length=255, blank=True, null=True)
    adres_korespondencyjny_numer_domu = models.CharField(max_length=10, blank=True, null=True)
    adres_korespondencyjny_numer_mieszkania = models.CharField(max_length=10, blank=True, null=True)
    adres_korespondencyjny_kod_pocztowy = models.CharField(max_length=10, blank=True, null=True)
    adres_korespondencyjny_miejscowosc = models.CharField(max_length=255, blank=True, null=True)
    adres_korespondencyjny_kraj = models.CharField(max_length=255, blank=True, null=True, default="Polska")
    dodatkowy_opis = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['firma', 'nip'],
                name='unique_nip_per_firma'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'nazwa']),
            models.Index(fields=['nip']),
            models.Index(fields=['czy_firma']),
        ]

    def __str__(self):
        return self.nazwa
    
    def clean(self):
        if not self.user_id:
            raise ValidationError("Pole user jest wymagane")



class Produkt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nazwa = models.CharField(max_length=255)
    jednostka = models.CharField(max_length=10)
    cena_netto = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.CharField(max_length=5, choices=[
        ('23', '23%'), ('8', '8%'), ('5', '5%'), ('0', '0%'), ('zw', 'zw')
    ])

    class Meta:
        indexes = [
            models.Index(fields=['user', 'nazwa']),
            models.Index(fields=['vat']),
        ]

    def __str__(self):
        return self.nazwa

class FakturaQuerySet(models.QuerySet):
    def with_related(self):
        """Fetch faktury with related objects to avoid N+1 queries"""
        return self.select_related('nabywca', 'sprzedawca', 'user').prefetch_related('pozycjafaktury_set')
    
    def for_user(self, user):
        """Filter faktury for specific user"""
        return self.filter(user=user)
    
    def sprzedaz(self):
        """Filter sales invoices"""
        return self.filter(typ_faktury='sprzedaz')
    
    def koszt(self):
        """Filter cost invoices"""  
        return self.filter(typ_faktury='koszt')
    
    def oplacone(self):
        """Filter paid invoices"""
        return self.filter(status='oplacona')
    
    def nieoplacone(self):
        """Filter unpaid invoices"""
        return self.exclude(status='oplacona')


class FakturaManager(models.Manager):
    def get_queryset(self):
        return FakturaQuerySet(self.model, using=self._db)
    
    def with_related(self):
        return self.get_queryset().with_related()
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)
    
    def sprzedaz(self):
        return self.get_queryset().sprzedaz()
    
    def koszt(self):
        return self.get_queryset().koszt()


class Faktura(models.Model):
    TYP_DOKUMENTU_CHOICES = [
        ('FV', 'Faktura VAT'),
        ('FP', 'Faktura Proforma'),
        ('KOR', 'Korekta Faktury'),
        ('RC', 'Rachunek'),
        ('PAR', 'Paragon'),
        ('KP', 'KP - Dowód Wpłaty'),
        ('RB', 'Rachunek Bankowy'),
    ]
    SPOSOB_PLATNOSCI_CHOICES = [
        ('przelew', 'Przelew'),
        ('gotowka', 'Gotówka'),
    ]
    STATUS_CHOICES = [
        ('wystawiona', 'Wystawiona'),
        ('oplacona', 'Opłacona'),
        ('cz_oplacona', 'Częściowo opłacona'),
        ('anulowana', 'Anulowana'),
    ]
    WALUTA_CHOICES = [
        ('PLN', 'PLN'),
        ('EUR', 'EUR'),
        ('USD', 'USD'),
    ]
    RABAT_OBLICZANIE_CHOICES = [
        ('proc_netto', '% od ceny jednostkowej netto'),
        ('proc_brutto', '% od ceny jednostkowej brutto'),
        ('proc_calk_brutto', '% od ceny całościowej brutto'),
        ('kwotowo', 'Kwotowo'),
    ]
    TYP_FAKTURY_CHOICES = [
        ('sprzedaz', 'Sprzedaż'),
        ('koszt', 'Koszt'),
    ]
    POWOD_ZWOLNIENIA = [
        ('art43', 'Zwolnienie ze względu na rodzaj prowadzonej działalności (art. 43 ust 1 ustawy o VAT)'),
        ('art113', 'Zwolnienie ze względu na nieprzekroczenie 200 000 PLN obrotu (art. 113 ust 1 i 9 ustawy o VAT)'),
        ('art82', 'Zwolnienie na mocy rozporządzenia MF (art. 82 ust 3 ustawy o VAT)'),
    ]

    dokument_podstawowy = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Dokument podstawowy'
    )
    data_realizacji = models.DateField(null=True, blank=True)
    metoda_platnosci = models.CharField(
        max_length=20,
        choices=[('gotowka', 'Gotówka'), ('przelew', 'Przelew'), ('karta', 'Karta')],
        null=True,
        blank=True
    )

    numer_konta_bankowego = models.CharField(
        max_length=26,
        blank=True,
        null=True,
        verbose_name="Numer konta"
    )
    
    tytul_przelewu = models.TextField(
        blank=True,
        null=True,
        verbose_name="Tytuł przelewu"
    )

    kasa = models.CharField(max_length=50, null=True, blank=True, verbose_name="Numer kasy")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    typ_dokumentu = models.CharField(max_length=3, choices=TYP_DOKUMENTU_CHOICES, default='FV')
    numer = models.CharField(max_length=50)
    data_wystawienia = models.DateField(default=datetime.date.today)
    data_sprzedazy = models.DateField()
    miejsce_wystawienia = models.CharField(max_length=255)
    sprzedawca = models.ForeignKey(Firma, on_delete=models.CASCADE, related_name='sprzedawca_faktury')
    nabywca = models.ForeignKey(Kontrahent, on_delete=models.CASCADE, related_name='nabywca_faktury')
    typ_faktury = models.CharField(max_length=10, choices=TYP_FAKTURY_CHOICES, default='sprzedaz')
    zwolnienie_z_vat = models.BooleanField(default=False)
    powod_zwolnienia = models.CharField(max_length=10, choices=POWOD_ZWOLNIENIA, blank=True, null=True)
    sposob_platnosci = models.CharField(
        max_length=20,
        choices=SPOSOB_PLATNOSCI_CHOICES,
        default='przelew',
        blank=False,
        null=False
    )
    termin_platnosci = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='wystawiona')
    kwota_oplacona = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    jak_obliczyc_rabat = models.CharField(max_length=20, choices=RABAT_OBLICZANIE_CHOICES, blank=True, null=True)
    rabat_procentowy_globalny = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    rabat_kwotowy_globalny = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    waluta = models.CharField(max_length=3, choices=WALUTA_CHOICES, default='PLN')
    wystawca = models.CharField(max_length=255, blank=True, null=True)
    odbiorca = models.CharField(max_length=255, blank=True, null=True)
    uwagi = models.TextField(blank=True, null=True)
    auto_numer = models.BooleanField(default=True, verbose_name="Automatyczna numeracja")
    wlasny_numer = models.CharField(max_length=50, blank=True, null=True, verbose_name="Własny numer faktury")
    kp = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='powiazana_faktury')
    
    # OCR Integration Fields
    source_document = models.ForeignKey(
        'DocumentUpload', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Dokument źródłowy OCR"
    )
    ocr_confidence = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Pewność OCR (%)"
    )
    manual_verification_required = models.BooleanField(
        default=False,
        verbose_name="Wymaga weryfikacji manualnej"
    )
    ocr_processing_time = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Czas przetwarzania OCR (s)"
    )
    ocr_extracted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data ekstrakcji OCR"
    )
    def clean(self):
        if self.typ_dokumentu == 'KOR' and not self.dokument_podstawowy:
            raise ValidationError("Korekta wymaga wskazania dokumentu podstawowego")
        
    def save(self, *args, **kwargs):
        if self.auto_numer and not self.wlasny_numer and not self.numer:
            today = datetime.date.today()
            ostatnia_faktura = Faktura.objects.filter(
                user=self.user,
                data_wystawienia__year=today.year,
                data_wystawienia__month=today.month,
                typ_dokumentu=self.typ_dokumentu
            ).order_by('-numer').first()

            if ostatnia_faktura:
                try:
                    ostatni_numer = int(ostatnia_faktura.numer.split('/')[1])
                    self.numer = f"{self.typ_dokumentu}/{ostatni_numer + 1:02d}/{today.month:02d}/{today.year}"
                except (ValueError, IndexError):
                    liczba_faktur = Faktura.objects.filter(
                        user=self.user,
                        data_wystawienia__year=today.year,
                        data_wystawienia__month=today.month,
                        typ_dokumentu=self.typ_dokumentu
                    ).count()
                    self.numer = f"{self.typ_dokumentu}/{liczba_faktur + 1:02d}/{today.month:02d}/{today.year}"
            else:
                self.numer = f"{self.typ_dokumentu}/01/{today.month:02d}/{today.year}"
        elif self.wlasny_numer:
            self.numer = self.wlasny_numer
        super().save(*args, **kwargs) # Zachowaj super().save() dla standardowego zachowania zapisu
    
        if self.nabywca and self.nabywca.firma:
            try:
                partnerstwo = Partnerstwo.objects.filter(
                (Q(firma1=self.sprzedawca, firma2=self.nabywca.firma) | Q(firma1=self.nabywca.firma, firma2=self.sprzedawca)) &
                Q(aktywne=True) &
                Q(auto_ksiegowanie=True)
                ).first()

                if partnerstwo:
                    firma_odbiorcy = partnerstwo.firma2 if partnerstwo.firma1 == self.sprzedawca else partnerstwo.firma1
                
                    try:
                        nabywca_kontrahent = Kontrahent.objects.get(
                            user=firma_odbiorcy.user,
                            nip=self.sprzedawca.nip
                        )
                    except Kontrahent.DoesNotExist:
                        nabywca_kontrahent = Kontrahent.objects.create(
                            user=firma_odbiorcy.user,
                            nazwa=self.sprzedawca.nazwa,
                            nip=self.sprzedawca.nip,
                            ulica=self.sprzedawca.ulica,
                            numer_domu=self.sprzedawca.numer_domu,
                            kod_pocztowy=self.sprzedawca.kod_pocztowy,
                            miejscowosc=self.sprzedawca.miejscowosc,
                            czy_firma=True
                        )  
                    except Kontrahent.MultipleObjectsReturned:
                        nabywca_kontrahent = Kontrahent.objects.filter(
                            user=firma_odbiorcy.user,
                            nip=self.sprzedawca.nip
                        ).first()
                        logger.warning(f"Znaleziono duplikaty kontrahenta NIP: {self.sprzedawca.nip}, używam pierwszego: ID {nabywca_kontrahent.id}")     
                    
                    
                
                    if not Faktura.objects.filter(user=firma_odbiorcy.user, numer=self.numer).exists():
                        with transaction.atomic():
                            kopia_faktury = Faktura.objects.create(
                                user=firma_odbiorcy.user,
                                numer=self.numer,
                                typ_dokumentu=self.typ_dokumentu,
                                data_wystawienia=self.data_wystawienia,
                                data_sprzedazy=self.data_sprzedazy,
                                miejsce_wystawienia=self.miejsce_wystawienia,
                                sprzedawca=self.nabywca.firma,
                                nabywca=nabywca_kontrahent,
                                typ_faktury='koszt',
                                sposob_platnosci=self.sposob_platnosci,
                                termin_platnosci=self.termin_platnosci,
                                status='wystawiona',
                                waluta=self.waluta,
                                uwagi=f"Auto-księgowanie z {self.sprzedawca.nazwa}"
                            )
                        
                            # Skopiuj pozycje
                            for pozycja in self.pozycjafaktury_set.all():
                                PozycjaFaktury.objects.create(
                                    faktura=kopia_faktury,
                                    nazwa=pozycja.nazwa,
                                    ilosc=pozycja.ilosc,
                                    jednostka=pozycja.jednostka,
                                    cena_netto=pozycja.cena_netto,
                                    vat=pozycja.vat,
                                    rabat=pozycja.rabat,
                                    rabat_typ=pozycja.rabat_typ
                                )
                        logger.info(f"Utworzono auto-księgowanie dla faktury {self.numer}")

            except Exception as e:
                logger.error(f"Błąd auto-księgowania faktury {self.numer}: {str(e)}", exc_info=True)
                raise

        faktura_cykliczna = models.ForeignKey(
        'FakturaCykliczna',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generowane_faktury'
    )
    
    # Auto-accounting fields
    auto_ksiegowana = models.BooleanField(default=False, verbose_name="Auto-księgowana")
    faktura_zrodlowa = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faktury_pochodne',
        verbose_name="Faktura źródłowa"
    )
    
    # Add custom manager
    objects = FakturaManager()
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'data_wystawienia']),
            models.Index(fields=['user', 'typ_faktury']),
            models.Index(fields=['numer']),
            models.Index(fields=['status']),
            models.Index(fields=['termin_platnosci']),
            models.Index(fields=['data_sprzedazy']),
            models.Index(fields=['typ_dokumentu']),
        ]
        ordering = ['-data_wystawienia']

    def delete(self, *args, **kwargs):
        ZadanieUzytkownika.objects.filter(faktura=self).delete()
        super().delete(*args, **kwargs)
        
    def clean(self):
        super().clean()
        if self.sposob_platnosci == 'gotowka':
            self.can_generate_kp = True
        else:
            self.can_generate_kp = False
    @property
    def can_generate_kp(self):
        return self.sposob_platnosci == 'gotowka'

    @can_generate_kp.setter
    def can_generate_kp(self, value):
        if value:
            self.sposob_platnosci = 'gotowka'
        else:
            self.sposob_platnosci = 'przelew'
            
    @property
    def suma_brutto(self):
        total = Decimal('0.00')
        for pozycja in self.pozycjafaktury_set.all():
            total += pozycja.wartosc_brutto
        return total.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
   
def generate_kp(self):
    if self.sposob_platnosci != 'gotowka':
        raise ValueError("Kasa Pieniężna może być wygenerowana tylko dla płatności w gotówce.")
    
    kp = Faktura.objects.create(
        user=self.user,  # Ensure the user is set
        typ_dokumentu='KP',
        numer=self._generate_kp_number(),
        sprzedawca=self.sprzedawca,
        nabywca=self.nabywca,
        data_wystawienia=datetime.timezone.now().date(),
        data_sprzedazy=self.data_sprzedazy,
        termin_platnosci=self.termin_platnosci,
        miejsce_wystawienia=self.miejsce_wystawienia,
        sposob_platnosci=self.sposob_platnosci,
        typ_faktury=self.typ_faktury,
        kwota_oplacona=self.suma_brutto
    )
    
    # Copy positions from the original invoice
    for position in self.pozycjafaktury_set.all():
        PozycjaFaktury.objects.create(
            faktura=kp,
            nazwa=position.nazwa,
            ilosc=position.ilosc,
            cena_netto=position.cena_netto,
            vat=position.vat,
            jednostka=position.jednostka
        )
    
    return kp

    def _generate_kp_number(self):
        year = datetime.date.today().year
        count = Faktura.objects.filter(
            user=self.user,
            typ_dokumentu='KP',
            data_wystawienia__year=year
        ).count() + 1
        return f"KP/{year}/{count:04d}"

    
    

class PozycjaFaktury(models.Model):
    faktura = models.ForeignKey(Faktura, on_delete=models.CASCADE)
    nazwa = models.CharField(max_length=255)
    rabat = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    rabat_typ = models.CharField(max_length=10, choices=[('procent', 'Procent'), ('kwota', 'Kwota')], blank=True, null=True)
    ilosc = models.DecimalField(max_digits=10, decimal_places=2)
    jednostka = models.CharField(max_length=10)
    cena_netto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    vat = models.CharField(max_length=5, choices=[
        ('23', '23%'), ('8', '8%'), ('5', '5%'), ('0', '0%'), ('zw', 'zw')
    ])

    @property
    def wartosc_netto(self):
        try:
            cena = Decimal(str(self.cena_netto))
            ilosc = Decimal(str(self.ilosc))
            
            if self.rabat_typ == 'procent' and self.rabat:
                cena *= (1 - Decimal(str(self.rabat))/100)
            elif self.rabat_typ == 'kwota' and self.rabat:
                cena -= Decimal(str(self.rabat))
            
            wartosc = cena * ilosc
            if self.faktura.typ_faktury == 'koszt':
                wartosc = -wartosc
                
            return wartosc.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        
        except Exception as e:
            logger.error(f"Błąd obliczeń: {str(e)}")
            return Decimal('0.00')

    @property
    def wartosc_brutto(self):
        try:
            if self.vat == 'zw':
                return self.wartosc_netto
            
            vat = Decimal(str(self.vat))/100
            return (self.wartosc_netto * (1 + vat)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        
        except Exception as e:
            logger.error(f"Błąd obliczeń: {str(e)}")
            return Decimal('0.00')

    
class FakturaCykliczna(models.Model):
    CYKLE_WYBOR = (
        ('D', 'Dzienny'),
        ('W', 'Tygodniowy'),
        ('2W', 'Co 2 tygodnie'),
        ('M', 'Miesięczny'),
        ('2M', 'Co 2 miesiące'),
        ('3M', 'Co 3 miesiące'),
        ('6M', 'Co 6 miesięcy'),
        ('R', 'Roczny'),
    )
    
    oryginalna_faktura = models.ForeignKey(Faktura, on_delete=models.CASCADE, related_name='cykle')
    cykl = models.CharField(max_length=2, choices=CYKLE_WYBOR, default='M')
    data_poczatkowa = models.DateField()
    data_koncowa = models.DateField(null=True, blank=True, help_text="Pozostaw puste dla nieskończonego cyklu")
    nastepna_generacja = models.DateField()
    liczba_cykli = models.PositiveIntegerField(default=0, help_text="Liczba wygenerowanych faktur")
    maksymalna_liczba_cykli = models.PositiveIntegerField(null=True, blank=True, help_text="Maksymalna liczba faktur do wygenerowania")
    aktywna = models.BooleanField(default=True)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    ostatnia_generacja = models.DateTimeField(null=True, blank=True)
    
    # Notification settings
    powiadom_o_generacji = models.BooleanField(default=True, verbose_name="Powiadamiaj o generacji")
    dni_przed_generacja = models.PositiveIntegerField(default=3, verbose_name="Dni przed generacją do powiadomienia")

    class Meta:
        verbose_name = "Faktura cykliczna"
        verbose_name_plural = "Faktury cykliczne"
        ordering = ['-data_utworzenia']
        indexes = [
            models.Index(fields=['aktywna', 'nastepna_generacja']),
            models.Index(fields=['oryginalna_faktura']),
        ]

    def __str__(self):
        return f"{self.oryginalna_faktura.numer} ({self.get_cykl_display()})"
    
    def save(self, *args, **kwargs):
        # Set initial next generation date if not set
        if not self.nastepna_generacja and self.data_poczatkowa:
            self.nastepna_generacja = self.data_poczatkowa
        super().save(*args, **kwargs)
    
    @property
    def dni_do_nastepnej_generacji(self):
        """Days until next generation"""
        if not self.nastepna_generacja:
            return None
        today = timezone.now().date()
        delta = self.nastepna_generacja - today
        return delta.days
    
    @property
    def czy_mozna_generowac(self):
        """Check if invoice can be generated"""
        if not self.aktywna:
            return False
        
        today = timezone.now().date()
        if self.nastepna_generacja > today:
            return False
            
        if self.data_koncowa and today > self.data_koncowa:
            return False
            
        if self.maksymalna_liczba_cykli and self.liczba_cykli >= self.maksymalna_liczba_cykli:
            return False
            
        return True
    
    def oblicz_nastepna_date(self):
        """Calculate next generation date based on cycle"""
        from dateutil.relativedelta import relativedelta
        
        if self.cykl == 'D':
            return self.nastepna_generacja + timezone.timedelta(days=1)
        elif self.cykl == 'W':
            return self.nastepna_generacja + timezone.timedelta(weeks=1)
        elif self.cykl == '2W':
            return self.nastepna_generacja + timezone.timedelta(weeks=2)
        elif self.cykl == 'M':
            return self.nastepna_generacja + relativedelta(months=1)
        elif self.cykl == '2M':
            return self.nastepna_generacja + relativedelta(months=2)
        elif self.cykl == '3M':
            return self.nastepna_generacja + relativedelta(months=3)
        elif self.cykl == '6M':
            return self.nastepna_generacja + relativedelta(months=6)
        elif self.cykl == 'R':
            return self.nastepna_generacja + relativedelta(years=1)
        else:
            # Default to monthly
            return self.nastepna_generacja + relativedelta(months=1)
    
    def generuj_fakture(self):
        """Generate next invoice in cycle"""
        if not self.czy_mozna_generowac:
            return None
            
        from .services import generuj_fakture_cykliczna
        return generuj_fakture_cykliczna(self)
    
    def zakoncz_cykl(self, powod="Zakończony ręcznie"):
        """End the cycle"""
        self.aktywna = False
        self.save()
        
        # Create notification
        Notification.objects.create(
            user=self.oryginalna_faktura.user,
            title="Cykl faktury zakończony",
            content=f"Cykl faktury {self.oryginalna_faktura.numer} został zakończony. Powód: {powod}",
            type="INFO"
        )

class ZadanieUzytkownika(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tytul = models.CharField(max_length=255)
    opis = models.TextField(blank=True)
    termin_wykonania = models.DateField()
    wykonane = models.BooleanField(default=False)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    faktura = models.ForeignKey(Faktura, on_delete=models.SET_NULL, null=True, blank=True, related_name='zadania_uzytkownika')

    def __str__(self):
        return f"{self.tytul} - {self.user.username}"

    class Meta:
        ordering = ['termin_wykonania']

def validate_korekta(self):
    if self.typ_dokumentu == 'KOR':
        if not self.dokument_podstawowy:
            raise ValidationError("Korekta wymaga dokumentu podstawowego")
        if self.dokument_podstawowy.typ_dokumentu not in ['FV', 'FP']:
            raise ValidationError("Można korygować tylko faktury i proformy")

def validate_paragon(self):
    if self.typ_dokumentu == 'PAR':
        if not self.kasa:
            raise ValidationError("Paragon wymaga numeru kasy")
        if self.metoda_platnosci != 'gotowka':
            raise ValidationError("Paragon dotyczy tylko płatności gotówkowych")   


# ============================================================================
# OCR AND DOCUMENT PROCESSING MODELS
# ============================================================================

class DocumentUpload(models.Model):
    """Track uploaded documents for OCR processing"""
    
    STATUS_CHOICES = [
        ('uploaded', 'Przesłany'),
        ('queued', 'W kolejce'),
        ('processing', 'Przetwarzany'),
        ('ocr_completed', 'OCR zakończone'),
        ('integration_processing', 'Tworzenie faktury'),
        ('completed', 'Zakończony'),
        ('failed', 'Błąd'),
        ('manual_review', 'Wymaga przeglądu'),
        ('cancelled', 'Anulowany'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    original_filename = models.CharField(max_length=255, verbose_name="Nazwa pliku")
    file_path = models.CharField(max_length=500, verbose_name="Ścieżka pliku")
    file_size = models.BigIntegerField(verbose_name="Rozmiar pliku (bytes)")
    content_type = models.CharField(max_length=100, verbose_name="Typ MIME")
    upload_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data przesłania")
    processing_status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='uploaded',
        verbose_name="Status przetwarzania"
    )
    processing_started_at = models.DateTimeField(null=True, blank=True, verbose_name="Rozpoczęcie przetwarzania")
    processing_completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Zakończenie przetwarzania")
    error_message = models.TextField(blank=True, null=True, verbose_name="Komunikat błędu")
    
    class Meta:
        verbose_name = "Przesłany dokument"
        verbose_name_plural = "Przesłane dokumenty"
        ordering = ['-upload_timestamp']
        indexes = [
            models.Index(fields=['user', '-upload_timestamp']),
            models.Index(fields=['processing_status']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.get_processing_status_display()})"
    
    @property
    def processing_duration(self):
        """Calculate processing duration in seconds"""
        if self.processing_started_at and self.processing_completed_at:
            return (self.processing_completed_at - self.processing_started_at).total_seconds()
        return None
    
    def mark_processing_started(self):
        """Mark document as processing started"""
        self.processing_status = 'processing'
        self.processing_started_at = timezone.now()
        self.save(update_fields=['processing_status', 'processing_started_at'])
    
    def mark_processing_completed(self):
        """Mark document as processing completed"""
        self.processing_status = 'completed'
        self.processing_completed_at = timezone.now()
        self.save(update_fields=['processing_status', 'processing_completed_at'])
    
    def mark_processing_failed(self, error_message):
        """Mark document as processing failed"""
        self.processing_status = 'failed'
        self.processing_completed_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=['processing_status', 'processing_completed_at', 'error_message'])
    
    def get_unified_status(self):
        """
        Get unified status considering OCR result
        
        Returns:
            Dict: Combined status information including document and OCR status,
                 progress, display text, and metadata for frontend use
        """
        from .services.status_sync_service import StatusSyncService
        return StatusSyncService.get_combined_status(self)
    
    def get_status_display_data(self):
        """
        Get status with display metadata optimized for templates
        
        Returns:
            Dict: Status data with CSS classes, icons, progress indicators,
                 and template-friendly display information
        """
        from .services.status_sync_service import StatusSyncService
        return StatusSyncService.get_status_display_data(self)
    
    def get_processing_progress(self):
        """
        Get processing progress percentage based on current status
        
        Returns:
            int: Progress percentage (0-100) indicating how far through
                 the OCR processing pipeline the document has progressed
        """
        from .services.status_sync_service import StatusSyncService
        return StatusSyncService.get_processing_progress(self)
    
    def to_api_dict(self, include_sensitive=False):
        """
        Convert DocumentUpload to API-friendly dictionary
        
        Args:
            include_sensitive (bool): Whether to include sensitive information
            
        Returns:
            dict: API-friendly representation of the document upload
        """
        data = {
            'id': self.id,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'content_type': self.content_type,
            'upload_timestamp': self.upload_timestamp.isoformat() if self.upload_timestamp else None,
            'processing_status': self.processing_status,
            'processing_status_display': self.get_processing_status_display(),
            'processing_duration': self.processing_duration,
            'has_ocr_result': hasattr(self, 'ocrresult'),
            'processing_progress': self.get_processing_progress(),
        }
        
        # Add processing timestamps
        if self.processing_started_at:
            data['processing_started_at'] = self.processing_started_at.isoformat()
        if self.processing_completed_at:
            data['processing_completed_at'] = self.processing_completed_at.isoformat()
        
        # Add error information if present
        if self.error_message:
            data['error_message'] = self.error_message
        
        # Add sensitive information if requested
        if include_sensitive:
            data['file_path'] = self.file_path
            data['user_id'] = self.user_id
        
        # Add OCR result summary if available
        if hasattr(self, 'ocrresult'):
            ocr_result = self.ocrresult
            data['ocr_result'] = {
                'id': ocr_result.id,
                'confidence_score': ocr_result.confidence_score,
                'processing_status': ocr_result.processing_status,
                'has_faktura': ocr_result.faktura_id is not None,
                'needs_review': ocr_result.needs_human_review,
            }
        
        return data
    
    def get_task_id(self):
        """
        Get associated Celery task ID for tracking processing status
        
        Returns:
            str: Task ID if available, None otherwise
        """
        # Check if there's a task ID stored in the database
        # This would require adding a task_id field to the model or using a separate tracking mechanism
        
        # For now, we'll use a simple approach based on the document ID and status
        # In a production system, you might want to store the actual Celery task ID
        
        if self.processing_status in ['queued', 'processing']:
            # Generate a predictable task ID based on document ID
            # This assumes the task naming convention follows a pattern
            return f"process_document_ocr_task_{self.id}"
        
        return None
    
    def get_api_status(self):
        """
        Get status formatted for API responses with additional metadata
        
        Returns:
            dict: Status information formatted for API consumption
        """
        status_data = {
            'status': self.processing_status,
            'status_display': self.get_processing_status_display(),
            'progress': self.get_processing_progress(),
            'is_processing': self.processing_status in ['queued', 'processing'],
            'is_completed': self.processing_status in ['completed', 'ocr_completed'],
            'is_failed': self.processing_status == 'failed',
            'needs_review': self.processing_status == 'manual_review',
        }
        
        # Add timing information
        if self.processing_started_at:
            status_data['processing_started_at'] = self.processing_started_at.isoformat()
        
        if self.processing_completed_at:
            status_data['processing_completed_at'] = self.processing_completed_at.isoformat()
            
        if self.processing_duration:
            status_data['processing_duration_seconds'] = self.processing_duration
        
        # Add ETA estimation for processing documents
        if self.processing_status in ['queued', 'processing']:
            status_data['estimated_completion'] = self._estimate_completion_time()
        
        # Add error information if present
        if self.error_message:
            status_data['error_message'] = self.error_message
        
        return status_data
    
    def _estimate_completion_time(self):
        """
        Estimate completion time based on processing history and queue length
        
        Returns:
            dict: Estimated completion time information
        """
        from datetime import timedelta
        
        # Calculate average processing time for similar documents
        # Get completed documents and calculate duration in Python
        completed_docs = DocumentUpload.objects.filter(
            processing_status='completed',
            content_type=self.content_type,
            processing_started_at__isnull=False,
            processing_completed_at__isnull=False
        )[:50]  # Limit to recent 50 documents for performance
        
        durations = []
        for doc in completed_docs:
            if doc.processing_duration:
                durations.append(doc.processing_duration)
        
        if durations:
            avg_processing_time = sum(durations) / len(durations)
        else:
            avg_processing_time = 30.0  # Default 30 seconds
        
        # Count documents ahead in queue
        queue_position = DocumentUpload.objects.filter(
            processing_status__in=['queued', 'processing'],
            upload_timestamp__lt=self.upload_timestamp
        ).count()
        
        # Estimate total time
        estimated_seconds = avg_processing_time + (queue_position * avg_processing_time)
        estimated_completion = timezone.now() + timedelta(seconds=estimated_seconds)
        
        return {
            'eta_seconds': int(estimated_seconds),
            'estimated_completion_time': estimated_completion.isoformat(),
            'queue_position': queue_position,
            'average_processing_time': avg_processing_time
        }


class OCRResult(models.Model):
    """Store OCR extraction results"""
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Oczekuje'),
        ('processing', 'Przetwarzanie'),
        ('completed', 'Zakończone'),
        ('failed', 'Błąd'),
        ('manual_review', 'Wymaga przeglądu'),
    ]
    
    document = models.OneToOneField(
        DocumentUpload, 
        on_delete=models.CASCADE, 
        verbose_name="Dokument"
    )
    faktura = models.ForeignKey(
        Faktura, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ocr_results',
        verbose_name="Powiązana faktura"
    )
    raw_text = models.TextField(verbose_name="Surowy tekst OCR")
    extracted_data = models.JSONField(verbose_name="Wyodrębnione dane")  # Structured data from Document AI
    confidence_score = models.FloatField(verbose_name="Pewność OCR (%)")
    processing_time = models.FloatField(verbose_name="Czas przetwarzania (s)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    
    # Processing status and error handling
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending',
        verbose_name="Status przetwarzania"
    )
    error_message = models.TextField(blank=True, null=True, verbose_name="Komunikat błędu")
    auto_created_faktura = models.BooleanField(default=False, verbose_name="Automatycznie utworzona faktura")
    
    # Detailed confidence scores for different fields
    field_confidence = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Pewność poszczególnych pól"
    )
    
    # Processing metadata
    processor_version = models.CharField(max_length=50, blank=True, verbose_name="Wersja procesora")
    processing_location = models.CharField(max_length=50, blank=True, verbose_name="Lokalizacja przetwarzania")
    
    class Meta:
        verbose_name = "Wynik OCR"
        verbose_name_plural = "Wyniki OCR"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['faktura']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['processing_status']),
            # Note: Compound index with related fields is created in migration 0024
        ]
    
    def __str__(self):
        return f"OCR: {self.document.original_filename} ({self.confidence_score:.1f}%)"
    
    def save(self, *args, **kwargs):
        """Override save to handle automatic faktura creation"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Trigger automatic processing for new OCR results
        # Processing is handled by signals to avoid circular imports
        if is_new and self.processing_status == 'pending':
            # The post_save signal will handle the processing
            pass
    
    @property
    def needs_human_review(self):
        """Check if result needs human review based on confidence"""
        return self.confidence_score < 80.0
    
    @property
    def can_auto_create_faktura(self):
        """Check if confidence is high enough for automatic faktura creation"""
        return self.confidence_score >= 90.0
    
    @property
    def confidence_level(self):
        """Get confidence level category"""
        if self.confidence_score >= 90.0:
            return 'high'
        elif self.confidence_score >= 80.0:
            return 'medium'
        else:
            return 'low'
    
    def mark_processing_started(self):
        """Mark OCR result as processing started"""
        self.processing_status = 'processing'
        self.save(update_fields=['processing_status'])
    
    def mark_processing_completed(self):
        """Mark OCR result as processing completed"""
        self.processing_status = 'completed'
        self.save(update_fields=['processing_status'])
    
    def mark_processing_failed(self, error_message):
        """Mark OCR result as processing failed"""
        self.processing_status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['processing_status', 'error_message'])
    
    def mark_manual_review_required(self):
        """Mark OCR result as requiring manual review"""
        self.processing_status = 'manual_review'
        self.save(update_fields=['processing_status'])
    
    def sync_document_status(self):
        """Sync parent document status"""
        from .services.status_sync_service import StatusSyncService
        return StatusSyncService.sync_document_status(self.document)
    
    def get_validation_fields(self):
        """
        Get fields that can be manually validated with their current values and confidence.
        
        Returns:
            dict: Dictionary of validatable fields with values and confidence scores
        """
        if not self.extracted_data:
            return {}
        
        validation_fields = {}
        field_confidence = self.field_confidence or {}
        
        # Define which fields can be validated
        validatable_fields = [
            'numer_faktury', 'data_wystawienia', 'data_sprzedazy',
            'sprzedawca', 'nabywca', 'pozycje', 'suma_netto', 'suma_brutto'
        ]
        
        for field in validatable_fields:
            if field in self.extracted_data:
                validation_fields[field] = {
                    'value': self.extracted_data[field],
                    'confidence': field_confidence.get(field, self.confidence_score),
                    'needs_review': field_confidence.get(field, self.confidence_score) < 80.0
                }
        
        return validation_fields
    
    def apply_manual_corrections(self, corrections, validated_by=None):
        """
        Apply user corrections and update confidence scores.
        
        Args:
            corrections (dict): Dictionary of field corrections
            validated_by (User): User who made the corrections
            
        Returns:
            dict: Summary of applied corrections
        """
        if not corrections:
            return {'updated_fields': [], 'new_confidence_scores': {}}
        
        updated_fields = []
        new_confidence_scores = {}
        
        # Make a copy of extracted_data to modify
        updated_data = self.extracted_data.copy() if self.extracted_data else {}
        updated_field_confidence = self.field_confidence.copy() if self.field_confidence else {}
        
        for field_path, new_value in corrections.items():
            try:
                # Handle nested field paths (e.g., 'sprzedawca.nazwa', 'pozycje.0.cena_netto')
                if '.' in field_path:
                    self._apply_nested_correction(updated_data, field_path, new_value)
                else:
                    updated_data[field_path] = new_value
                
                # Set confidence to 100% for manually corrected fields
                updated_field_confidence[field_path] = 100.0
                new_confidence_scores[field_path] = 100.0
                updated_fields.append(field_path)
                
            except (KeyError, IndexError, TypeError) as e:
                logger.warning(f"Failed to apply correction for field {field_path}: {str(e)}")
                continue
        
        # Update the model fields
        self.extracted_data = updated_data
        self.field_confidence = updated_field_confidence
        
        # Recalculate overall confidence score
        self._recalculate_confidence_score()
        
        # Save the changes
        self.save(update_fields=['extracted_data', 'field_confidence', 'confidence_score'])
        
        # Create validation record if user provided
        if validated_by:
            self._create_validation_record(corrections, validated_by)
        
        return {
            'updated_fields': updated_fields,
            'new_confidence_scores': new_confidence_scores
        }
    
    def _apply_nested_correction(self, data, field_path, new_value):
        """
        Apply correction to nested field using dot notation.
        
        Args:
            data (dict): Data dictionary to modify
            field_path (str): Dot-separated field path (e.g., 'sprzedawca.nazwa')
            new_value: New value to set
        """
        parts = field_path.split('.')
        current = data
        
        # Navigate to the parent of the target field
        for part in parts[:-1]:
            # Handle array indices
            if part.isdigit():
                current = current[int(part)]
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        # Set the final value
        final_key = parts[-1]
        if final_key.isdigit():
            current[int(final_key)] = new_value
        else:
            current[final_key] = new_value
    
    def _recalculate_confidence_score(self):
        """
        Recalculate overall confidence score based on field confidence scores.
        """
        if not self.field_confidence:
            return
        
        # Calculate weighted average of field confidence scores
        field_weights = {
            'numer_faktury': 0.15,
            'data_wystawienia': 0.10,
            'sprzedawca': 0.20,
            'nabywca': 0.15,
            'suma_brutto': 0.20,
            'pozycje': 0.20
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for field, confidence in self.field_confidence.items():
            weight = field_weights.get(field, 0.05)  # Default weight for other fields
            weighted_sum += confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            self.confidence_score = weighted_sum / total_weight
        
    def _create_validation_record(self, corrections, validated_by):
        """
        Create a validation record for tracking manual corrections.
        
        Args:
            corrections (dict): Applied corrections
            validated_by (User): User who made the corrections
        """
        try:
            # Check if validation record already exists
            validation, created = OCRValidation.objects.get_or_create(
                ocr_result=self,
                defaults={
                    'validated_by': validated_by,
                    'corrections_made': corrections,
                    'accuracy_rating': 8,  # Default rating for manual corrections
                    'validation_notes': 'Manual corrections applied via API'
                }
            )
            
            if not created:
                # Update existing validation record
                validation.corrections_made.update(corrections)
                validation.validation_timestamp = timezone.now()
                validation.save(update_fields=['corrections_made', 'validation_timestamp'])
                
        except Exception as e:
            logger.error(f"Failed to create validation record: {str(e)}")
    
    def can_create_faktura(self):
        """
        Check if OCR result has sufficient data quality to create a Faktura.
        
        Returns:
            bool: True if Faktura can be created
        """
        if not self.extracted_data:
            return False
        
        # Check if required fields are present with sufficient confidence
        required_fields = ['numer_faktury', 'data_wystawienia', 'sprzedawca_nazwa', 'suma_brutto']
        field_confidence = self.field_confidence or {}
        
        for field in required_fields:
            if field not in self.extracted_data:
                return False
            
            confidence = field_confidence.get(field, self.confidence_score)
            if confidence < 70.0:  # Minimum confidence threshold
                return False
        
        return True
    
    def to_api_dict(self, include_sensitive=False):
        """
        Convert OCRResult to API-friendly dictionary
        
        Args:
            include_sensitive (bool): Whether to include sensitive information
            
        Returns:
            dict: API-friendly representation of the OCR result
        """
        data = {
            'id': self.id,
            'document': {
                'id': self.document.id,
                'filename': self.document.original_filename,
                'upload_date': self.document.upload_timestamp.isoformat() if self.document.upload_timestamp else None,
            },
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level,
            'processing_status': self.processing_status,
            'processing_status_display': self.get_processing_status_display(),
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'needs_review': self.needs_human_review,
            'can_auto_create_faktura': self.can_auto_create_faktura,
            'can_create_faktura': self.can_create_faktura(),
            'has_faktura': self.faktura_id is not None,
            'auto_created_faktura': self.auto_created_faktura,
        }
        
        # Add faktura information if available
        if self.faktura:
            data['faktura'] = {
                'id': self.faktura.id,
                'numer': self.faktura.numer,
                'url': f'/api/faktury/{self.faktura.id}/',
                'suma_brutto': float(self.faktura.suma_brutto) if hasattr(self.faktura, 'suma_brutto') else None,
            }
        
        # Add processing metadata
        if self.processor_version:
            data['processor_version'] = self.processor_version
        if self.processing_location:
            data['processing_location'] = self.processing_location
        
        # Add error information if present
        if self.error_message:
            data['error_message'] = self.error_message
        
        # Add sensitive information if requested
        if include_sensitive:
            data['raw_text'] = self.raw_text
            data['extracted_data'] = self.extracted_data
            data['field_confidence'] = self.field_confidence
        else:
            # Include only summary of extracted data
            if self.extracted_data:
                data['extracted_data_summary'] = {
                    'has_invoice_number': 'numer_faktury' in self.extracted_data,
                    'has_date': 'data_wystawienia' in self.extracted_data,
                    'has_seller': 'sprzedawca' in self.extracted_data,
                    'has_buyer': 'nabywca' in self.extracted_data,
                    'has_total': 'suma_brutto' in self.extracted_data,
                    'items_count': len(self.extracted_data.get('pozycje', [])),
                }
        
        return data
    
    def get_validation_fields(self):
        """
        Get fields that can be manually validated with their current values and confidence.
        
        Returns:
            dict: Dictionary of validatable fields with values and confidence scores
        """
        if not self.extracted_data:
            return {}
        
        validation_fields = {}
        field_confidence = self.field_confidence or {}
        
        # Define which fields can be validated
        validatable_fields = [
            'numer_faktury', 'data_wystawienia', 'data_sprzedazy',
            'sprzedawca', 'nabywca', 'pozycje', 'suma_netto', 'suma_brutto'
        ]
        
        for field in validatable_fields:
            if field in self.extracted_data:
                validation_fields[field] = {
                    'value': self.extracted_data[field],
                    'confidence': field_confidence.get(field, self.confidence_score),
                    'needs_review': field_confidence.get(field, self.confidence_score) < 80.0,
                    'field_type': self._get_field_type(field),
                    'validation_rules': self._get_field_validation_rules(field),
                }
        
        return validation_fields
    
    def _get_field_type(self, field_name):
        """
        Get the expected data type for a field
        
        Args:
            field_name (str): Name of the field
            
        Returns:
            str: Field type (string, number, date, object, array)
        """
        field_types = {
            'numer_faktury': 'string',
            'data_wystawienia': 'date',
            'data_sprzedazy': 'date',
            'suma_netto': 'number',
            'suma_brutto': 'number',
            'sprzedawca': 'object',
            'nabywca': 'object',
            'pozycje': 'array',
        }
        return field_types.get(field_name, 'string')
    
    def _get_field_validation_rules(self, field_name):
        """
        Get validation rules for a field
        
        Args:
            field_name (str): Name of the field
            
        Returns:
            dict: Validation rules for the field
        """
        validation_rules = {
            'numer_faktury': {
                'required': True,
                'max_length': 50,
                'pattern': r'^[A-Z0-9\/\-]+$',
            },
            'data_wystawienia': {
                'required': True,
                'format': 'YYYY-MM-DD',
            },
            'data_sprzedazy': {
                'required': True,
                'format': 'YYYY-MM-DD',
            },
            'suma_netto': {
                'required': True,
                'min_value': 0,
                'decimal_places': 2,
            },
            'suma_brutto': {
                'required': True,
                'min_value': 0,
                'decimal_places': 2,
            },
            'sprzedawca': {
                'required': True,
                'required_fields': ['nazwa', 'nip'],
            },
            'nabywca': {
                'required': True,
                'required_fields': ['nazwa'],
            },
            'pozycje': {
                'required': True,
                'min_items': 1,
                'item_required_fields': ['nazwa', 'cena_netto', 'ilosc'],
            },
        }
        return validation_rules.get(field_name, {})
    
    def get_api_status(self):
        """
        Get status formatted for API responses with additional metadata
        
        Returns:
            dict: Status information formatted for API consumption
        """
        status_data = {
            'status': self.processing_status,
            'status_display': self.get_processing_status_display(),
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level,
            'needs_review': self.needs_human_review,
            'can_create_faktura': self.can_create_faktura(),
            'has_faktura': self.faktura_id is not None,
            'auto_created': self.auto_created_faktura,
        }
        
        # Add processing time information
        if self.processing_time:
            status_data['processing_time_seconds'] = self.processing_time
        
        # Add creation timestamp
        if self.created_at:
            status_data['created_at'] = self.created_at.isoformat()
        
        # Add error information if present
        if self.error_message:
            status_data['error_message'] = self.error_message
        
        # Add field-level confidence summary
        if self.field_confidence:
            low_confidence_fields = [
                field for field, confidence in self.field_confidence.items()
                if confidence < 80.0
            ]
            status_data['low_confidence_fields'] = low_confidence_fields
            status_data['fields_needing_review'] = len(low_confidence_fields)
        
        return status_data
    
    def get_processing_progress(self):
        """
        Get processing progress percentage for OCR result
        
        Returns:
            int: Progress percentage (0-100)
        """
        progress_map = {
            'pending': 10,
            'processing': 50,
            'completed': 100,
            'failed': 0,
            'manual_review': 90,
        }
        return progress_map.get(self.processing_status, 0)
    
    def get_task_id(self):
        """
        Get associated Celery task ID for OCR result processing
        
        Returns:
            str: Task ID if available, None otherwise
        """
        if self.processing_status in ['pending', 'processing']:
            # Generate a predictable task ID based on OCR result ID
            return f"process_ocr_result_task_{self.id}"
        
        return None


class OCRValidation(models.Model):
    """Track manual validation of OCR results"""
    
    ACCURACY_CHOICES = [(i, f"{i}/10") for i in range(1, 11)]
    
    ocr_result = models.OneToOneField(
        OCRResult, 
        on_delete=models.CASCADE,
        verbose_name="Wynik OCR"
    )
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Zwalidowany przez"
    )
    validation_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data walidacji")
    corrections_made = models.JSONField(default=dict, verbose_name="Wprowadzone poprawki")
    accuracy_rating = models.IntegerField(
        choices=ACCURACY_CHOICES,
        verbose_name="Ocena dokładności"
    )
    validation_notes = models.TextField(blank=True, verbose_name="Notatki walidacji")
    time_spent_minutes = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Czas walidacji (minuty)"
    )
    
    class Meta:
        verbose_name = "Walidacja OCR"
        verbose_name_plural = "Walidacje OCR"
        ordering = ['-validation_timestamp']
        indexes = [
            models.Index(fields=['validated_by', '-validation_timestamp']),
            models.Index(fields=['accuracy_rating']),
        ]
    
    def __str__(self):
        return f"Walidacja: {self.ocr_result.document.original_filename} ({self.accuracy_rating}/10)"
    
    @property
    def corrections_count(self):
        """Count number of corrections made"""
        return len(self.corrections_made) if self.corrections_made else 0


# ============================================================================
# EXTENSIONS TO EXISTING FAKTURA MODEL
# ============================================================================

# Add OCR-related fields to existing Faktura model
def add_ocr_fields_to_faktura():
    """
    This function documents the fields that need to be added to the Faktura model.
    They should be added manually to avoid migration conflicts.
    """
    ocr_fields = {
        'source_document': models.ForeignKey(
            'DocumentUpload', 
            on_delete=models.SET_NULL, 
            null=True, 
            blank=True,
            verbose_name="Dokument źródłowy"
        ),
        'ocr_confidence': models.FloatField(
            null=True, 
            blank=True,
            verbose_name="Pewność OCR (%)"
        ),
        'manual_verification_required': models.BooleanField(
            default=False,
            verbose_name="Wymaga weryfikacji"
        ),
        'ocr_processing_time': models.FloatField(
            null=True, 
            blank=True,
            verbose_name="Czas przetwarzania OCR (s)"
        ),
        'ocr_extracted_at': models.DateTimeField(
            null=True,
            blank=True,
            verbose_name="Data ekstrakcji OCR"
        ),
    }
    return ocr_fields


class OCRProcessingLog(models.Model):
    """Log OCR processing events for debugging and monitoring"""
    
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'), 
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    document = models.ForeignKey(
        DocumentUpload,
        on_delete=models.CASCADE,
        verbose_name="Dokument"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Znacznik czasu")
    level = models.CharField(max_length=10, choices=LOG_LEVELS, verbose_name="Poziom")
    message = models.TextField(verbose_name="Wiadomość")
    details = models.JSONField(default=dict, blank=True, verbose_name="Szczegóły")
    
    class Meta:
        verbose_name = "Log przetwarzania OCR"
        verbose_name_plural = "Logi przetwarzania OCR"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['document', '-timestamp']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"{self.level}: {self.document.original_filename} - {self.message[:50]}"
