"""
Enhanced forms for Polish invoice system
Formularze zgodne z polskim prawem VAT i przepisami księgowymi
"""
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from decimal import Decimal
import datetime
import re

from .models import Faktura, PozycjaFaktury, Firma, Kontrahent
from .enhanced_models import EnhancedFaktura, EnhancedPozycjaFaktury


class PolishVATValidatorMixin:
    """Mixin do walidacji zgodnie z polskim prawem VAT"""
    
    def clean_nip(self):
        """Walidacja numeru NIP"""
        nip = self.cleaned_data.get('nip', '').replace('-', '').replace(' ', '')
        
        if not nip:
            return nip
            
        if not re.match(r'^\d{10}$', nip):
            raise ValidationError('NIP musi składać się z 10 cyfr')
            
        # Walidacja sumy kontrolnej NIP
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        
        # Jeśli suma kontrolna wynosi 10, to cyfra kontrolna powinna być 0
        if checksum == 10:
            checksum = 0
            
        if checksum != int(nip[9]):
            raise ValidationError('Nieprawidłowa suma kontrolna NIP')
            
        return nip
    
    def clean_regon(self):
        """Walidacja numeru REGON"""
        regon = self.cleaned_data.get('regon', '').replace('-', '').replace(' ', '')
        
        if not regon:
            return regon
            
        if len(regon) not in [9, 14]:
            raise ValidationError('REGON musi mieć 9 lub 14 cyfr')
            
        if not regon.isdigit():
            raise ValidationError('REGON może zawierać tylko cyfry')
            
        # Walidacja sumy kontrolnej REGON-9
        if len(regon) == 9:
            weights = [8, 9, 2, 3, 4, 5, 6, 7]
            checksum = sum(int(regon[i]) * weights[i] for i in range(8)) % 11
            checksum = 0 if checksum == 10 else checksum
            
            if checksum != int(regon[8]):
                raise ValidationError('Nieprawidłowa suma kontrolna REGON')
                
        return regon


class EnhancedFakturaForm(forms.ModelForm, PolishVATValidatorMixin):
    """
    Rozszerzony formularz faktury zgodny z polskim prawem VAT
    """
    
    # Dodatkowe pola formularza
    auto_numer = forms.BooleanField(
        initial=True,
        required=False,
        label="Automatyczna numeracja",
        help_text="Automatyczne nadawanie numeru faktury zgodnie ze schematem",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    wlasny_numer = forms.CharField(
        required=False,
        label="Własny numer faktury",
        help_text="Własny schemat numeracji (wymagane gdy auto_numer = False)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'np. FV/2024/001'
        })
    )
    
    # Walidacja terminów płatności
    dni_platnosci = forms.IntegerField(
        required=False,
        initial=14,
        min_value=0,
        max_value=365,
        label="Dni do płatności",
        help_text="Liczba dni od daty wystawienia do terminu płatności",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '365'
        })
    )
    
    # Dodatkowe informacje VAT
    vat_margin = forms.BooleanField(
        required=False,
        label="Procedura marży (art. 120 ustawy o VAT)",
        help_text="Zastosowanie procedury marży dla towarów używanych",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    odwrotne_obciazenie = forms.BooleanField(
        required=False,
        label="Odwrotne obciążenie VAT",
        help_text="Stosowane przy sprzedaży do podatników VAT UE",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Pola dla faktur korygujących
    powod_korekty = forms.CharField(
        required=False,
        max_length=500,
        label="Powód korekty",
        help_text="Wymagane dla faktur korygujących",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Opisz powód wystawienia faktury korygującej...'
        })
    )
    
    class Meta:
        model = Faktura
        fields = [
            'typ_dokumentu', 'data_wystawienia', 'data_sprzedazy',
            'miejsce_wystawienia', 'sprzedawca', 'nabywca',
            'sposob_platnosci', 'termin_platnosci', 'status',
            'waluta', 'zwolnienie_z_vat', 'powod_zwolnienia',
            'numer_konta_bankowego', 'tytul_przelewu',
            'wystawca', 'odbiorca', 'uwagi'
        ]
        
        widgets = {
            'typ_dokumentu': forms.Select(attrs={'class': 'form-select'}),
            'data_wystawienia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'data_sprzedazy': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'termin_platnosci': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'miejsce_wystawienia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Miejscowość wystawienia'
            }),
            'sprzedawca': forms.Select(attrs={'class': 'form-select'}),
            'nabywca': forms.Select(attrs={'class': 'form-select'}),
            'sposob_platnosci': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'waluta': forms.Select(attrs={'class': 'form-select'}),
            'powod_zwolnienia': forms.Select(attrs={'class': 'form-select'}),
            'numer_konta_bankowego': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IBAN lub numer konta'
            }),
            'tytul_przelewu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Tytuł przelewu...'
            }),
            'wystawca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Imię i nazwisko osoby wystawiającej'
            }),
            'odbiorca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Imię i nazwisko osoby odbierającej'
            }),
            'uwagi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dodatkowe uwagi...'
            }),
            'zwolnienie_z_vat': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'typ_dokumentu': 'Typ dokumentu *',
            'data_wystawienia': 'Data wystawienia *',
            'data_sprzedazy': 'Data sprzedaży/wykonania *',
            'miejsce_wystawienia': 'Miejsce wystawienia *',
            'sprzedawca': 'Sprzedawca *',
            'nabywca': 'Nabywca *',
            'sposob_platnosci': 'Sposób płatności',
            'termin_platnosci': 'Termin płatności *',
            'status': 'Status',
            'waluta': 'Waluta',
            'zwolnienie_z_vat': 'Zwolniona z VAT',
            'powod_zwolnienia': 'Podstawa prawna zwolnienia',
            'numer_konta_bankowego': 'Numer konta bankowego',
            'tytul_przelewu': 'Tytuł przelewu',
            'wystawca': 'Osoba wystawiająca',
            'odbiorca': 'Osoba odbierająca',
            'uwagi': 'Uwagi',
        }
        
        help_texts = {
            'data_sprzedazy': 'Data wykonania dostawy/usługi (art. 106e ust. 5 pkt 3 ustawy o VAT)',
            'zwolnienie_z_vat': 'Zaznacz jeśli transakcja jest zwolniona z VAT',
            'powod_zwolnienia': 'Wybierz podstawę prawną zwolnienia z VAT',
            'numer_konta_bankowego': 'Wymagane przy płatności przelewem (min. kwota wg ustawy)',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Ustaw domyślne wartości
        if not self.instance.pk:  # Nowy obiekt
            self.fields['data_wystawienia'].initial = datetime.date.today()
            self.fields['data_sprzedazy'].initial = datetime.date.today()
            
            # Ustaw termin płatności na podstawie dni_platnosci
            if self.data.get('dni_platnosci'):
                dni = int(self.data['dni_platnosci'])
                self.fields['termin_platnosci'].initial = (
                    datetime.date.today() + datetime.timedelta(days=dni)
                )
        
        # Filter choices based on user
        if self.user:
            # Filter sprzedawca (Firma) - user's companies
            from .models import Firma
            self.fields['sprzedawca'].queryset = Firma.objects.filter(user=self.user)
            
            # Filter nabywca (Kontrahent) - user's contractors  
            from .models import Kontrahent
            self.fields['nabywca'].queryset = Kontrahent.objects.filter(firma__user=self.user)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Walidacja numeracji
        auto_numer = cleaned_data.get('auto_numer', True)
        wlasny_numer = cleaned_data.get('wlasny_numer', '')
        
        if not auto_numer and not wlasny_numer:
            raise ValidationError(
                'Musisz wybrać automatyczną numerację lub podać własny numer faktury'
            )
        
        # Walidacja dat
        data_wystawienia = cleaned_data.get('data_wystawienia')
        data_sprzedazy = cleaned_data.get('data_sprzedazy')
        termin_platnosci = cleaned_data.get('termin_platnosci')
        
        if data_wystawienia and data_sprzedazy:
            if data_sprzedazy > data_wystawienia + datetime.timedelta(days=30):
                raise ValidationError(
                    'Data sprzedaży nie może być później niż 30 dni od daty wystawienia'
                )
        
        if data_wystawienia and termin_platnosci:
            if termin_platnosci < data_wystawienia:
                raise ValidationError(
                    'Termin płatności nie może być wcześniejszy niż data wystawienia'
                )
        
        # Walidacja zwolnień z VAT
        zwolnienie_z_vat = cleaned_data.get('zwolnienie_z_vat', False)
        powod_zwolnienia = cleaned_data.get('powod_zwolnienia')
        
        if zwolnienie_z_vat and not powod_zwolnienia:
            raise ValidationError(
                'Musisz podać podstawę prawną zwolnienia z VAT'
            )
        
        # Walidacja korekt
        typ_dokumentu = cleaned_data.get('typ_dokumentu')
        powod_korekty = cleaned_data.get('powod_korekty')
        
        if typ_dokumentu in ['KOR', 'KP', 'KN'] and not powod_korekty:
            raise ValidationError(
                'Musisz podać powód korekty dla faktury korygującej'
            )
        
        # Walidacja konta bankowego przy przelewach
        sposob_platnosci = cleaned_data.get('sposob_platnosci')
        numer_konta = cleaned_data.get('numer_konta_bankowego')
        
        if sposob_platnosci == 'przelew' and not numer_konta:
            self.add_error('numer_konta_bankowego', 
                          'Numer konta jest wymagany przy płatności przelewem')
        
        return cleaned_data
    
    def clean_numer_konta_bankowego(self):
        """Walidacja numeru konta bankowego"""
        numer = self.cleaned_data.get('numer_konta_bankowego', '')
        
        if not numer:
            return numer
        
        # Usuń spacje i myślniki
        numer = numer.replace(' ', '').replace('-', '')
        
        # Walidacja IBAN
        if len(numer) >= 15:  # Potencjalny IBAN
            if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]+$', numer):
                raise ValidationError('Nieprawidłowy format numeru IBAN')
        
        # Walidacja polskiego numeru konta
        elif len(numer) == 26:  # Polski numer konta
            if not numer.isdigit():
                raise ValidationError('Polski numer konta może zawierać tylko cyfry')
        
        return numer


class EnhancedPozycjaFakturyForm(forms.ModelForm):
    """
    Rozszerzony formularz pozycji faktury
    """
    
    # Dodatkowe pola
    katalog_pkwiu = forms.BooleanField(
        required=False,
        label="Wybierz z katalogu PKWiU",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = PozycjaFaktury
        fields = [
            'nazwa', 'ilosc', 'jednostka', 'cena_netto',
            'vat', 'rabat', 'rabat_typ'
        ]
        
        widgets = {
            'nazwa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nazwa towaru/usługi...'
            }),
            'ilosc': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'jednostka': forms.Select(attrs={'class': 'form-select'}),
            'cena_netto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'vat': forms.Select(attrs={'class': 'form-select'}),
            'rabat': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'rabat_typ': forms.Select(attrs={'class': 'form-select'}),
        }
        
        labels = {
            'nazwa': 'Nazwa towaru/usługi *',
            'ilosc': 'Ilość *',
            'jednostka': 'Jednostka *',
            'cena_netto': 'Cena netto *',
            'vat': 'Stawka VAT *',
            'rabat': 'Rabat',
            'rabat_typ': 'Typ rabatu',
        }
    
    def clean_cena_netto(self):
        """Walidacja ceny netto"""
        cena = self.cleaned_data.get('cena_netto')
        
        if cena is not None and cena < 0:
            raise ValidationError('Cena netto nie może być ujemna')
        
        if cena is not None and cena > Decimal('999999.99'):
            raise ValidationError('Cena netto jest za wysoka')
        
        return cena
    
    def clean_ilosc(self):
        """Walidacja ilości"""
        ilosc = self.cleaned_data.get('ilosc')
        
        if ilosc is not None and ilosc <= 0:
            raise ValidationError('Ilość musi być większa od zera')
        
        return ilosc
    
    def clean_rabat(self):
        """Walidacja rabatu"""
        rabat = self.cleaned_data.get('rabat')
        rabat_typ = self.cleaned_data.get('rabat_typ')
        
        if rabat is not None and rabat < 0:
            raise ValidationError('Rabat nie może być ujemny')
        
        if rabat_typ == 'procent' and rabat is not None and rabat > 100:
            raise ValidationError('Rabat procentowy nie może być większy niż 100%')
        
        return rabat


# Formset dla pozycji faktury
EnhancedPozycjaFakturyFormSet = inlineformset_factory(
    Faktura,
    PozycjaFaktury,
    form=EnhancedPozycjaFakturyForm,
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=True,
    widgets={
        'DELETE': forms.CheckboxInput(attrs={'class': 'form-check-input'})
    }
)


class FakturaProFormaForm(EnhancedFakturaForm):
    """Formularz dla faktury pro forma"""
    
    class Meta(EnhancedFakturaForm.Meta):
        pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['typ_dokumentu'].initial = 'FP'
        self.fields['typ_dokumentu'].widget.attrs['readonly'] = True


class FakturaKorygujacaForm(EnhancedFakturaForm):
    """Formularz dla faktury korygującej"""
    
    dokument_podstawowy = forms.ModelChoiceField(
        queryset=Faktura.objects.none(),
        label="Dokument podstawowy *",
        help_text="Faktura, którą koryguje ten dokument",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta(EnhancedFakturaForm.Meta):
        fields = EnhancedFakturaForm.Meta.fields + ['dokument_podstawowy']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['dokument_podstawowy'].queryset = Faktura.objects.filter(
                user=user,
                typ_dokumentu__in=['FV', 'FVS']
            ).order_by('-data_wystawienia')
        
        self.fields['typ_dokumentu'].initial = 'KOR'
        self.fields['powod_korekty'].required = True


class RachunekForm(EnhancedFakturaForm):
    """Formularz dla rachunku"""
    
    class Meta(EnhancedFakturaForm.Meta):
        pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['typ_dokumentu'].initial = 'RC'
        # Rachunek nie wymaga wszystkich pól faktury VAT
        self.fields['zwolnienie_z_vat'].initial = True
        self.fields['powod_zwolnienia'].initial = 'art43_1'


class FakturaZaliczkowaForm(EnhancedFakturaForm):
    """Formularz dla faktury zaliczkowej"""
    
    procent_zaliczki = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.01'),
        max_value=Decimal('100.00'),
        label="Procent zaliczki *",
        help_text="Procent wartości zamówienia płatny jako zaliczka",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'max': '100'
        })
    )
    
    class Meta(EnhancedFakturaForm.Meta):
        fields = EnhancedFakturaForm.Meta.fields + ['procent_zaliczki']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['typ_dokumentu'].initial = 'FZ'


class DokumentKasowyForm(EnhancedFakturaForm):
    """Formularz dla dokumentów kasowych KP/KW"""
    
    rodzaj_operacji = forms.ChoiceField(
        choices=[
            ('wplata', 'Wpłata (KP)'),
            ('wyplata', 'Wypłata (KW)')
        ],
        label="Rodzaj operacji *",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    nazwa_operacji = forms.CharField(
        max_length=200,
        label="Nazwa operacji *",
        help_text="Opis operacji kasowej",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'np. Wpłata za fakturę FV/001/2024'
        })
    )
    
    kwota = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        label="Kwota *",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01'
        })
    )
    
    class Meta(EnhancedFakturaForm.Meta):
        fields = [
            'data_wystawienia', 'miejsce_wystawienia',
            'rodzaj_operacji', 'nazwa_operacji', 'kwota',
            'nabywca', 'uwagi'
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        rodzaj = cleaned_data.get('rodzaj_operacji')
        
        if rodzaj == 'wplata':
            cleaned_data['typ_dokumentu'] = 'KP_DOK'
        else:
            cleaned_data['typ_dokumentu'] = 'KW_DOK'
        
        return cleaned_data


# Formularze dla wybranych kontrahentów i produktów
class KontrahentQuickSelectForm(forms.Form):
    """Szybki wybór kontrahenta z podpowiedziami"""
    
    kontrahent = forms.ModelChoiceField(
        queryset=Kontrahent.objects.none(),
        label="Wybierz kontrahenta",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'kontrahent-select'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['kontrahent'].queryset = Kontrahent.objects.filter(
                firma__user=user
            ).order_by('nazwa')


class ProduktQuickSelectForm(forms.Form):
    """Szybki wybór produktu z katalogu"""
    
    produkt = forms.ModelChoiceField(
        queryset=None,
        label="Wybierz z katalogu",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'produkt-select'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            from .models import Produkt
            self.fields['produkt'].queryset = Produkt.objects.filter(
                user=user
            ).order_by('nazwa')
