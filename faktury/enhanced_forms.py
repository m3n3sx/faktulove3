"""
Enhanced invoice forms using design system Polish business components
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime
from decimal import Decimal

from .models import (
    Faktura, PozycjaFaktury, Kontrahent, Firma, Produkt, 
    FakturaCykliczna
)
from .forms import JEDNOSTKI


class EnhancedFakturaForm(forms.ModelForm):
    """Enhanced invoice form using design system components"""
    
    # Custom fields for enhanced functionality
    auto_numer = forms.BooleanField(
        initial=True,
        required=False,
        label="Automatyczna numeracja",
        widget=forms.CheckboxInput(attrs={
            'class': 'ds-checkbox',
            'data-testid': 'auto-numer-checkbox'
        })
    )
    
    wlasny_numer = forms.CharField(
        required=False,
        label="Własny numer faktury",
        widget=forms.TextInput(attrs={
            'class': 'ds-input',
            'placeholder': 'Wprowadź własny numer',
            'data-testid': 'wlasny-numer-input'
        })
    )
    
    # Enhanced date fields with Polish formatting
    data_wystawienia = forms.DateField(
        label="Data wystawienia",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={
            'class': 'ds-date-picker',
            'data-locale': 'pl-PL',
            'data-format': 'DD.MM.YYYY',
            'data-testid': 'data-wystawienia'
        })
    )
    
    data_sprzedazy = forms.DateField(
        label="Data sprzedaży",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={
            'class': 'ds-date-picker',
            'data-locale': 'pl-PL',
            'data-format': 'DD.MM.YYYY',
            'data-testid': 'data-sprzedazy'
        })
    )
    
    termin_platnosci = forms.DateField(
        label="Termin płatności",
        widget=forms.DateInput(attrs={
            'class': 'ds-date-picker',
            'data-locale': 'pl-PL',
            'data-format': 'DD.MM.YYYY',
            'data-testid': 'termin-platnosci'
        })
    )
    
    # Enhanced NIP validation for buyer
    nabywca_nip = forms.CharField(
        required=False,
        label="NIP nabywcy",
        widget=forms.TextInput(attrs={
            'class': 'ds-nip-validator',
            'data-real-time-validation': 'true',
            'data-show-validation-icon': 'true',
            'data-testid': 'nabywca-nip'
        })
    )
    
    # Currency fields with PLN formatting
    kwota_brutto = forms.DecimalField(
        required=False,
        label="Kwota brutto",
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'ds-currency-input',
            'data-currency': 'PLN',
            'data-locale': 'pl-PL',
            'data-testid': 'kwota-brutto'
        })
    )
    
    kwota_netto = forms.DecimalField(
        required=False,
        label="Kwota netto",
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'ds-currency-input',
            'data-currency': 'PLN',
            'data-locale': 'pl-PL',
            'data-testid': 'kwota-netto'
        })
    )
    
    kwota_vat = forms.DecimalField(
        required=False,
        label="Kwota VAT",
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'ds-currency-input',
            'data-currency': 'PLN',
            'data-locale': 'pl-PL',
            'data-testid': 'kwota-vat'
        })
    )
    
    # Recurring invoice fields
    cykliczna = forms.BooleanField(
        required=False,
        label="Faktura cykliczna",
        widget=forms.CheckboxInput(attrs={
            'class': 'ds-checkbox cykliczna-checkbox',
            'data-testid': 'cykliczna-checkbox'
        })
    )
    
    cykl = forms.ChoiceField(
        choices=FakturaCykliczna.CYKLE_WYBOR,
        required=False,
        label="Cykl generowania",
        widget=forms.Select(attrs={
            'class': 'ds-select',
            'data-testid': 'cykl-select'
        })
    )
    
    data_poczatkowa = forms.DateField(
        required=False,
        label="Data początkowa",
        widget=forms.DateInput(attrs={
            'class': 'ds-date-picker',
            'data-locale': 'pl-PL',
            'data-format': 'DD.MM.YYYY',
            'data-testid': 'data-poczatkowa'
        })
    )
    
    data_koncowa = forms.DateField(
        required=False,
        label="Data końcowa (opcjonalnie)",
        widget=forms.DateInput(attrs={
            'class': 'ds-date-picker',
            'data-locale': 'pl-PL',
            'data-format': 'DD.MM.YYYY',
            'data-testid': 'data-koncowa'
        })
    )

    class Meta:
        model = Faktura
        exclude = ['user', 'numer', 'kwota_oplacona', 'sprzedawca']
        widgets = {
            'typ_dokumentu': forms.Select(attrs={
                'class': 'ds-select',
                'data-testid': 'typ-dokumentu'
            }),
            'miejsce_wystawienia': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'miejsce-wystawienia'
            }),
            'sposob_platnosci': forms.Select(attrs={
                'class': 'ds-select',
                'data-testid': 'sposob-platnosci'
            }),
            'status': forms.Select(attrs={
                'class': 'ds-select',
                'data-testid': 'status'
            }),
            'waluta': forms.Select(attrs={
                'class': 'ds-select',
                'data-testid': 'waluta'
            }),
            'powod_zwolnienia': forms.Select(attrs={
                'class': 'ds-select',
                'data-testid': 'powod-zwolnienia'
            }),
            'nabywca': forms.Select(attrs={
                'class': 'ds-select',
                'data-testid': 'nabywca'
            }),
            'uwagi': forms.Textarea(attrs={
                'rows': 3,
                'class': 'ds-textarea',
                'data-testid': 'uwagi'
            }),
            'wystawca': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'wystawca'
            }),
            'odbiorca': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'odbiorca'
            }),
            'jak_obliczyc_rabat': forms.Select(attrs={
                'class': 'ds-select',
                'data-testid': 'jak-obliczyc-rabat'
            }),
            'rabat_procentowy_globalny': forms.NumberInput(attrs={
                'class': 'ds-input',
                'data-testid': 'rabat-procentowy'
            }),
            'rabat_kwotowy_globalny': forms.NumberInput(attrs={
                'class': 'ds-currency-input',
                'data-currency': 'PLN',
                'data-testid': 'rabat-kwotowy'
            }),
            'typ_faktury': forms.Select(attrs={
                'class': 'ds-select',
                'data-testid': 'typ-faktury'
            }),
            'zwolnienie_z_vat': forms.CheckboxInput(attrs={
                'class': 'ds-checkbox',
                'data-testid': 'zwolnienie-z-vat'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter nabywca queryset for current user
        if self.user:
            self.fields['nabywca'].queryset = Kontrahent.objects.filter(user=self.user)
        
        # Set up conditional field requirements
        self._setup_conditional_fields()

    def _setup_conditional_fields(self):
        """Setup conditional field requirements and visibility"""
        # Make NIP field required for business customers
        if self.instance and self.instance.nabywca and self.instance.nabywca.czy_firma:
            self.fields['nabywca_nip'].required = True

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate VAT exemption
        zwolnienie_z_vat = cleaned_data.get("zwolnienie_z_vat")
        powod_zwolnienia = cleaned_data.get("powod_zwolnienia")
        
        if zwolnienie_z_vat and not powod_zwolnienia:
            raise ValidationError("Jeśli zaznaczono zwolnienie z VAT, należy podać powód zwolnienia.")

        # Validate recurring invoice fields
        if cleaned_data.get('cykliczna'):
            if not cleaned_data.get('cykl'):
                raise ValidationError("Wybierz cykl dla faktury cyklicznej")
            if not cleaned_data.get('data_poczatkowa'):
                raise ValidationError("Data początkowa jest wymagana dla faktury cyklicznej")

        # Validate NIP if provided
        nabywca_nip = cleaned_data.get('nabywca_nip')
        if nabywca_nip:
            if not self._validate_nip(nabywca_nip):
                raise ValidationError("Podany NIP jest nieprawidłowy")

        return cleaned_data

    def _validate_nip(self, nip):
        """Validate Polish NIP number"""
        if not nip:
            return True
            
        # Remove all non-digit characters
        clean_nip = ''.join(filter(str.isdigit, nip))
        
        if len(clean_nip) != 10:
            return False
            
        # Check if all digits are the same
        if len(set(clean_nip)) == 1:
            return False
            
        # Calculate checksum
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(clean_nip[i]) * weights[i] for i in range(9)) % 11
        
        if checksum == 10:
            return False
            
        return checksum == int(clean_nip[9])


class EnhancedPozycjaFakturyForm(forms.ModelForm):
    """Enhanced invoice item form using design system components"""
    
    # Enhanced VAT rate selector
    vat = forms.ChoiceField(
        label="Stawka VAT",
        widget=forms.Select(attrs={
            'class': 'ds-vat-rate-selector',
            'data-include-exempt': 'true',
            'data-testid': 'vat-rate'
        })
    )
    
    # Currency inputs for prices
    cena_netto = forms.DecimalField(
        label="Cena netto",
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'ds-currency-input',
            'data-currency': 'PLN',
            'data-locale': 'pl-PL',
            'data-testid': 'cena-netto'
        })
    )
    
    # Quantity with proper formatting
    ilosc = forms.DecimalField(
        label="Ilość",
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'class': 'ds-input',
            'step': '0.001',
            'data-testid': 'ilosc'
        })
    )
    
    # Unit selector
    jednostka = forms.ChoiceField(
        choices=JEDNOSTKI,
        label="Jednostka",
        widget=forms.Select(attrs={
            'class': 'ds-select',
            'data-testid': 'jednostka'
        })
    )

    class Meta:
        model = PozycjaFaktury
        exclude = ['faktura']
        widgets = {
            'nazwa': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'nazwa'
            }),
            'rabat': forms.NumberInput(attrs={
                'min': 0,
                'class': 'ds-input',
                'data-testid': 'rabat'
            }),
            'rabat_typ': forms.Select(attrs={
                'class': 'ds-select',
                'data-testid': 'rabat-typ'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up VAT rate choices
        self.fields['vat'].choices = [
            ('23', '23%'),
            ('8', '8%'),
            ('5', '5%'),
            ('0', '0%'),
            ('zw', 'zw.'),
        ]

    def clean_cena_netto(self):
        """Validate net price"""
        cena_netto = self.cleaned_data.get('cena_netto')
        if cena_netto is not None and cena_netto < 0:
            raise ValidationError("Cena netto nie może być ujemna")
        return cena_netto

    def clean_ilosc(self):
        """Validate quantity"""
        ilosc = self.cleaned_data.get('ilosc')
        if ilosc is not None and ilosc <= 0:
            raise ValidationError("Ilość musi być większa od zera")
        return ilosc


class EnhancedKontrahentForm(forms.ModelForm):
    """Enhanced contractor form with NIP validation"""
    
    nip = forms.CharField(
        required=False,
        label="NIP",
        widget=forms.TextInput(attrs={
            'class': 'ds-nip-validator',
            'data-real-time-validation': 'true',
            'data-show-validation-icon': 'true',
            'data-testid': 'kontrahent-nip'
        })
    )

    class Meta:
        model = Kontrahent
        exclude = ['user']
        widgets = {
            'nazwa': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'nazwa'
            }),
            'regon': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'regon'
            }),
            'ulica': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'ulica'
            }),
            'numer_domu': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'numer-domu'
            }),
            'numer_mieszkania': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'numer-mieszkania'
            }),
            'kod_pocztowy': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'kod-pocztowy'
            }),
            'miejscowosc': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'miejscowosc'
            }),
            'kraj': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'kraj'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'ds-input',
                'data-testid': 'email'
            }),
            'telefon': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'telefon'
            }),
            'telefon_komorkowy': forms.TextInput(attrs={
                'class': 'ds-input',
                'data-testid': 'telefon-komorkowy'
            }),
            'czy_firma': forms.CheckboxInput(attrs={
                'class': 'ds-checkbox',
                'data-testid': 'czy-firma'
            }),
            'dodatkowy_opis': forms.Textarea(attrs={
                'class': 'ds-textarea',
                'rows': 3,
                'data-testid': 'dodatkowy-opis'
            }),
        }

    def clean_nip(self):
        """Validate NIP number"""
        nip = self.cleaned_data.get('nip')
        czy_firma = self.cleaned_data.get('czy_firma', False)
        
        if czy_firma and not nip:
            raise ValidationError("NIP jest wymagany dla firm")
            
        if nip and not self._validate_nip(nip):
            raise ValidationError("Podany NIP jest nieprawidłowy")
            
        return nip

    def _validate_nip(self, nip):
        """Validate Polish NIP number"""
        if not nip:
            return True
            
        # Remove all non-digit characters
        clean_nip = ''.join(filter(str.isdigit, nip))
        
        if len(clean_nip) != 10:
            return False
            
        # Check if all digits are the same
        if len(set(clean_nip)) == 1:
            return False
            
        # Calculate checksum
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(clean_nip[i]) * weights[i] for i in range(9)) % 11
        
        if checksum == 10:
            return False
            
        return checksum == int(clean_nip[9])


# Enhanced formsets
from django.forms import inlineformset_factory

EnhancedPozycjaFakturyFormSet = inlineformset_factory(
    Faktura,
    PozycjaFaktury,
    form=EnhancedPozycjaFakturyForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True,
    widgets={
        'DELETE': forms.CheckboxInput(attrs={'class': 'd-none'})
    }
)