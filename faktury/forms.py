from django import forms
from .models import (User, Faktura, Partnerstwo, PozycjaFaktury, Kontrahent,
                     Firma, Produkt, UserProfile, Zespol, CzlonekZespolu,
                     Wiadomosc, Zadanie, ZadanieUzytkownika, FakturaCykliczna)
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User # User jest już importowany w models.py
from django.forms import inlineformset_factory, DateInput
from django.core.exceptions import ValidationError
import datetime  # Potrzebne do domyślnej daty
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date

JEDNOSTKI = [
    ('szt', 'szt'),
    ('kg', 'kg'),
    ('m', 'm'),
    ('l', 'l'),
    ('usł', 'usł'),
    ('godz', 'godz'),
    ('dzień', 'dzień'),
    ('inne', 'inne'),
]

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'imie', 'nazwisko', 'telefon']
        widgets = {  # Dodajemy style
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'imie': forms.TextInput(attrs={'class': 'form-control'}),
            'nazwisko': forms.TextInput(attrs={'class': 'form-control'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control'}),
        }
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    username = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError("Adres email jest nieprawidłowy. Upewnij się, że zawiera znak @.")
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Ten email jest już zajęty.")
        return email

class KontrahentForm(forms.ModelForm):
    class Meta:
        model = Kontrahent
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if Kontrahent.objects.filter(
            firma=cleaned_data['firma'],
            nip=cleaned_data['nip']
        ).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Kontrahent z tym NIP już istnieje w tej firmie")


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class FirmaForm(forms.ModelForm):
    class Meta:
        model = Firma
        exclude = ['user']  # Wyklucz pole user, bo będzie przypisywane automatycznie
        widgets = {  # Dodajemy style
            'nazwa': forms.TextInput(attrs={'class': 'form-control'}),
            'nip': forms.TextInput(attrs={'class': 'form-control'}),
            'regon': forms.TextInput(attrs={'class': 'form-control'}),
            'ulica': forms.TextInput(attrs={'class': 'form-control'}),
            'numer_domu': forms.TextInput(attrs={'class': 'form-control'}),
            'numer_mieszkania': forms.TextInput(attrs={'class': 'form-control'}),
            'kod_pocztowy': forms.TextInput(attrs={'class': 'form-control'}),
            'miejscowosc': forms.TextInput(attrs={'class': 'form-control'}),
            'kraj': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class KontrahentForm(forms.ModelForm):
    class Meta:
        model = Kontrahent
        exclude = ['user']
        widgets = {  # Dodajemy style
            'nazwa': forms.TextInput(attrs={'class': 'form-control'}),
            'nip': forms.TextInput(attrs={'class': 'form-control'}),
            'regon': forms.TextInput(attrs={'class': 'form-control'}),
            'ulica': forms.TextInput(attrs={'class': 'form-control'}),
            'numer_domu': forms.TextInput(attrs={'class': 'form-control'}),
            'numer_mieszkania': forms.TextInput(attrs={'class': 'form-control'}),
            'kod_pocztowy': forms.TextInput(attrs={'class': 'form-control'}),
            'miejscowosc': forms.TextInput(attrs={'class': 'form-control'}),
            'kraj': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control'}),
            'telefon_komorkowy': forms.TextInput(attrs={'class': 'form-control'}),
            'adres_korespondencyjny_ulica': forms.TextInput(attrs={'class': 'form-control'}),
            'adres_korespondencyjny_numer_domu': forms.TextInput(attrs={'class': 'form-control'}),
            'adres_korespondencyjny_numer_mieszkania': forms.TextInput(attrs={'class': 'form-control'}),
            'adres_korespondencyjny_kod_pocztowy': forms.TextInput(attrs={'class': 'form-control'}),
            'adres_korespondencyjny_miejscowosc': forms.TextInput(attrs={'class': 'form-control'}),
            'adres_korespondencyjny_kraj': forms.TextInput(attrs={'class': 'form-control'}),
            'dodatkowy_opis': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'czy_firma': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }

class ProduktForm(forms.ModelForm):
    class Meta:
        model = Produkt
        exclude = ['user']
        widgets = {  # Dodajemy style
            'nazwa': forms.TextInput(attrs={'class': 'form-control'}),
            'jednostka': forms.TextInput(attrs={'class': 'form-control'}),
            'cena_netto': forms.NumberInput(attrs={'class': 'form-control'}),
            'vat': forms.Select(attrs={'class': 'form-select'}),
        }
class DateInput(forms.DateInput):
    input_type = 'date'
    
    def __init__(self, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(**kwargs)

class FakturaForm(forms.ModelForm):
    auto_numer = forms.BooleanField(
        initial=True,
        required=False,
        label="Automatyczna numeracja",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    wlasny_numer = forms.CharField(
        required=False,
        label="Własny numer faktury",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź własny numer'})
    )
    cykliczna = forms.BooleanField(
        required=False, 
        label="Faktura cykliczna",
        widget=forms.CheckboxInput(attrs={'class': 'cykliczna-checkbox'})
    )
    cykl = forms.ChoiceField(
        choices=FakturaCykliczna.CYKLE_WYBOR, 
        required=False,
        label="Cykl generowania"
    )
    data_poczatkowa = forms.DateField(
        required=False,
        label="Data początkowa",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    data_koncowa = forms.DateField(
        required=False,
        label="Data końcowa (opcjonalnie)",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    data_wystawienia = forms.DateField(
        widget=DateInput(format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'],
        initial=datetime.date.today()
    )
    
    data_sprzedazy = forms.DateField(
        widget=DateInput(format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'],
        initial=datetime.date.today()
    )
    status = forms.ChoiceField(
        label="Status płatności",
        choices=Faktura.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sposob_platnosci = forms.ChoiceField(
        label="Sposób płatności",
        choices=Faktura.SPOSOB_PLATNOSCI_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True  # Dodaj wymagane pole
    )
    class Meta:
        model = Faktura
        exclude = ['user', 'numer', 'kwota_oplacona', 'sprzedawca'] 
        widgets = {
            'typ_dokumentu': forms.Select(attrs={'class': 'form-select'}),
            'data_wystawienia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_sprzedazy': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'termin_platnosci': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'miejsce_wystawienia' : forms.TextInput(attrs={'class' : 'form-control'}),
            'sposob_platnosci' : forms.Select(attrs={'class' : 'form-select'}),
            'status' : forms.Select(attrs={'class' : 'form-select'}), # Nie edytujemy w dodawaniu
            'waluta' : forms.Select(attrs={'class' : 'form-select'}),
            'powod_zwolnienia' : forms.Select(attrs={'class' : 'form-select'}),
            'nabywca' : forms.Select(attrs={'class': 'form-select'}),
            'uwagi': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'wystawca': forms.TextInput(attrs={'class': 'form-control'}),
            'odbiorca': forms.TextInput(attrs={'class': 'form-control'}),
            'jak_obliczyc_rabat': forms.Select(attrs={'class': 'form-select'}),  # Zostawiamy, ale nie używamy w JS
            'rabat_procentowy_globalny': forms.NumberInput(attrs={'class': 'form-control'}), # Zostawiamy, ale nie używamy w JS
            'rabat_kwotowy_globalny': forms.NumberInput(attrs={'class': 'form-control'}),  # Zostawiamy, ale nie używamy w JS
            'typ_faktury': forms.Select(attrs={'class': 'form-select'}), # Dodajemy pole typ_faktury
        }

   
    nazwa = forms.CharField(label="Nazwa firmy", required=False)
    adres = forms.CharField(label="Adres", required=False)
    #Niestandardowe czyszczenie
    def clean(self):
        cleaned_data = super().clean()
        zwolnienie_z_vat = cleaned_data.get("zwolnienie_z_vat")
        powod_zwolnienia = cleaned_data.get("powod_zwolnienia")
        
        if zwolnienie_z_vat and not powod_zwolnienia:
            raise forms.ValidationError("Jeśli zaznaczono zwolnienie z VAT, należy podać powód zwolnienia.")

        if cleaned_data.get('cykliczna'):
            if not cleaned_data.get('cykl'):
                raise ValidationError("Wybierz cykl dla faktury cyklicznej")
            if not cleaned_data.get('data_poczatkowa'):
                raise ValidationError("Data początkowa jest wymagana dla faktury cyklicznej")
        return cleaned_data
    
class PozycjaFakturyForm(forms.ModelForm):
    jednostka = forms.ChoiceField(choices=JEDNOSTKI, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = PozycjaFaktury
        exclude = ['faktura']
        widgets = {
            'nazwa': forms.TextInput(attrs={'class': 'form-control'}),
            'rabat': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'rabat_typ': forms.Select(attrs={'class': 'form-select'}),
            'ilosc': forms.NumberInput(attrs={'class': 'form-control'}),
            'cena_netto': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'vat': forms.Select(attrs={'class': 'form-select'}),
        }


PozycjaFakturyFormSet = inlineformset_factory(
    Faktura,
    PozycjaFaktury,
    form=PozycjaFakturyForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True,
    widgets={
        'DELETE': forms.CheckboxInput(attrs={'class': 'd-none'})
    }
)

class FakturaCyklicznaForm(forms.ModelForm):
    class Meta:
        model = FakturaCykliczna
        fields = ['cykl', 'data_poczatkowa', 'data_koncowa']
        widgets = {
            'data_poczatkowa': forms.DateInput(attrs={'type': 'date'}),
            'data_koncowa': forms.DateInput(attrs={'type': 'date'}),
        }

class KwotaOplaconaForm(forms.ModelForm):
    class Meta:
        model = Faktura
        fields = ['kwota_oplacona', 'status']
        widgets = {
          'kwota_oplacona': forms.NumberInput(attrs={'class': 'form-control'}),
          'status' : forms.Select(attrs={'class' : 'form-select'})
        }

class FakturaProformaForm(FakturaForm):
    class Meta(FakturaForm.Meta):
        labels = {
            'termin_platnosci': 'Termin ważności proformy'
        }

class FakturaProformaForm(FakturaForm):
    class Meta(FakturaForm.Meta):
        labels = {
            'termin_platnosci': 'Termin ważności proformy (dni)'
        }
        help_texts = {
            'nabywca': 'Wybierz kontrahenta z bazy lub dodaj nowego'
        }

class KorektaFakturyForm(FakturaForm):
    class Meta(FakturaForm.Meta):
        help_texts = {
            'dokument_podstawowy': 'Wybierz fakturę do korekty'
        }
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('dokument_podstawowy'):
            raise ValidationError("Wybierz fakturę do korekty")
        return cleaned_data

class ParagonForm(FakturaForm):
    class Meta(FakturaForm.Meta):
        fields = ['nabywca', 'data_wystawienia', 'kasa']


class ImportFakturXMLForm(forms.Form):  # Używamy forms.Form, nie ModelForm
    plik_xml = forms.FileField(
        label='Wybierz plik XML',
        widget=forms.FileInput(attrs={'accept': '.xml'})  # Ogranicz do .xml
    )

class ZespolForm(forms.ModelForm):
    class Meta:
        model = Zespol
        fields = ['nazwa', 'opis'] # 'firma' będzie ustawiane automatycznie
        widgets = {
            'nazwa': forms.TextInput(attrs={'class': 'form-control'}),
            'opis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CzlonekZespoluForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='Użytkownik', widget=forms.Select(attrs={'class': 'form-select'}), required=False)
    class Meta:
        model = CzlonekZespolu
        fields = ['user', 'rola', 'imie', 'nazwisko', 'email'] # Include all profile fields
        widgets = {
            'rola' : forms.Select(attrs={'class': 'form-select'})
        }

CzlonekZespoluFormSet = inlineformset_factory(
    Zespol,
    CzlonekZespolu,
    form=CzlonekZespoluForm,
    extra=1,
    can_delete=True
)



class ZadanieForm(forms.ModelForm):
    class Meta:
        model = Zadanie
        fields = ['tytul', 'opis', 'termin_wykonania', 'status', 'priorytet', 'przypisane_do']
        widgets = {
            'tytul': forms.TextInput(attrs={'class': 'form-control'}),
            'opis': forms.Textarea(attrs={'class': 'form-control', 'rows':4}),
            'termin_wykonania': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priorytet': forms.Select(attrs={'class': 'form-select'}),
            'przypisane_do': forms.Select(attrs={'class': 'form-select'}),
        }
class ZadanieUzytkownikaForm(forms.ModelForm):
    class Meta:
        model = ZadanieUzytkownika
        fields = ['tytul', 'opis', 'termin_wykonania', 'faktura']  # 'faktura' jest *tutaj*
        widgets = {
            'tytul': forms.TextInput(attrs={'class': 'form-control'}),
            'opis': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'termin_wykonania': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'faktura': forms.Select(attrs={'class': 'form-select'}), # Używamy Select
        }

class RaportFakturForm(forms.Form):
    data_od = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data od", initial=datetime.date.today)
    data_do = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label = "Data do", initial=datetime.date.today)
    STATUS_CHOICES = (
        ('wszystkie', 'Wszystkie'),
        ('wystawiona', 'Wystawiona'),
        ('oplacona', 'Opłacona'),
        ('czesc_oplacona', 'Częściowo opłacona'),
        ('nieoplacona', 'Nieopłacona'),
        ('przeterminowana', 'Przeterminowana'),
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES, label="Status faktury")

class PartnerstwoForm(forms.ModelForm):
    class Meta:
        model = Partnerstwo
        fields = ['firma2', 'aktywne', 'auto_ksiegowanie', 'typ_partnerstwa', 'opis', 'data_rozpoczecia', 'data_zakonczenia']  # Dodaj nowe pola
        widgets = {
            'firma2': forms.Select(attrs={'class': 'form-select'}),
            'typ_partnerstwa': forms.Select(attrs={'class': 'form-select'}),  # Użyj Select dla choices
            'opis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), #Dodaj opis
            'data_rozpoczecia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), #Dodaj date
            'data_zakonczenia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),#Dodaj date
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['firma2'].queryset = Firma.objects.exclude(user=user)
            self.fields['firma2'].label = "Firma partnerska"


class KpForm(FakturaForm):
    numer_konta_bankowego = forms.CharField(
        max_length=26,
        label="Numer konta bankowego",
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    tytul_przelewu = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta(FakturaForm.Meta):
        fields = ['nabywca', 'kwota_oplacona', 'numer_konta_bankowego', 'tytul_przelewu']




class SystemowaWiadomoscForm(forms.ModelForm):
    class Meta:
        model = Wiadomosc
        fields = ['temat', 'tresc']
        widgets = {
            'tresc': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }


class WiadomoscForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(WiadomoscForm, self).__init__(*args, **kwargs)
        # Aktualizacja queryset’u dla pola odbiorcy, aby wykluczyć zalogowanego użytkownika
        if user and 'odbiorca_user' in self.fields:
            self.fields['odbiorca_user'].queryset = self.fields['odbiorca_user'].queryset.exclude(pk=user.pk)
    
    class Meta:
        model = Wiadomosc
        # Używamy nazwy pola 'odbiorca_user' zgodnie z modelem
        fields = ['temat', 'tresc', 'odbiorca_user', 'partnerstwo']
        widgets = {
            'tresc': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'partnerstwo': forms.Select(attrs={'class': 'form-select'}),
        }
