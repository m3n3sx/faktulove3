"""
Enhanced forms for company management
"""
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from .models import Firma, Kontrahent, Partnerstwo


class EnhancedFirmaForm(forms.ModelForm):
    """
    Enhanced company form with validation and multi-tenancy support
    """
    
    class Meta:
        model = Firma
        exclude = ['user']
        widgets = {
            'nazwa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nazwa firmy'
            }),
            'nip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890',
                'pattern': '[0-9]{10}',
                'title': 'NIP musi składać się z 10 cyfr'
            }),
            'regon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456789 lub 12345678901234'
            }),
            'ulica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nazwa ulicy'
            }),
            'numer_domu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1A'
            }),
            'numer_mieszkania': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12'
            }),
            'kod_pocztowy': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00-000',
                'pattern': '[0-9]{2}-[0-9]{3}',
                'title': 'Format: XX-XXX'
            }),
            'miejscowosc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Miasto'
            }),
            'kraj': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Polska'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def clean_nip(self):
        """
        Validate NIP number
        """
        nip = self.cleaned_data.get('nip', '').replace('-', '').replace(' ', '')
        
        if nip:
            # Check format
            if len(nip) != 10 or not nip.isdigit():
                raise ValidationError('NIP musi składać się z 10 cyfr')
            
            # Check if NIP already exists (excluding current instance)
            existing_query = Firma.objects.filter(nip=nip)
            if self.instance and self.instance.pk:
                existing_query = existing_query.exclude(pk=self.instance.pk)
            
            if existing_query.exists():
                raise ValidationError('Firma z tym numerem NIP już istnieje')
            
            # Validate NIP checksum
            if not self._validate_nip_checksum(nip):
                raise ValidationError('Nieprawidłowy numer NIP (błędna suma kontrolna)')
        
        return nip
    
    def _validate_nip_checksum(self, nip: str) -> bool:
        """
        Validate Polish NIP checksum
        """
        if len(nip) != 10:
            return False
        
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        
        if checksum == 10:
            return False
        
        return checksum == int(nip[9])
    
    def clean_regon(self):
        """
        Validate REGON number
        """
        regon = self.cleaned_data.get('regon', '').replace('-', '').replace(' ', '')
        
        if regon:
            if len(regon) not in [9, 14] or not regon.isdigit():
                raise ValidationError('REGON musi składać się z 9 lub 14 cyfr')
        
        return regon
    
    def clean_kod_pocztowy(self):
        """
        Validate postal code
        """
        kod = self.cleaned_data.get('kod_pocztowy', '')
        
        if kod:
            import re
            if not re.match(r'^\d{2}-\d{3}$', kod):
                raise ValidationError('Kod pocztowy musi mieć format XX-XXX')
        
        return kod


class CompanyContextSwitchForm(forms.Form):
    """
    Form for switching between company contexts
    """
    company = forms.ModelChoiceField(
        queryset=Firma.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        }),
        label='Wybierz firmę'
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get companies user has access to
        user_companies = []
        
        # User's own company
        if hasattr(user, 'firma'):
            user_companies.append(user.firma)
        
        # Companies through partnerships
        if hasattr(user, 'firma'):
            partnerships = Partnerstwo.objects.filter(
                models.Q(firma1=user.firma) | models.Q(firma2=user.firma),
                aktywne=True
            ).select_related('firma1', 'firma2')
            
            for partnership in partnerships:
                partner_company = partnership.firma2 if partnership.firma1 == user.firma else partnership.firma1
                user_companies.append(partner_company)
        
        self.fields['company'].queryset = Firma.objects.filter(
            id__in=[company.id for company in user_companies]
        ).distinct()


class EnhancedPartnerstwoForm(forms.ModelForm):
    """
    Enhanced partnership form with better validation
    """
    
    class Meta:
        model = Partnerstwo
        fields = [
            'firma2', 'typ_partnerstwa', 'opis', 
            'data_rozpoczecia', 'data_zakonczenia',
            'aktywne', 'auto_ksiegowanie'
        ]
        widgets = {
            'firma2': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'typ_partnerstwa': forms.Select(attrs={
                'class': 'form-select'
            }),
            'opis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Opis partnerstwa (opcjonalnie)'
            }),
            'data_rozpoczecia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'data_zakonczenia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'aktywne': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'auto_ksiegowanie': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user:
            # Exclude user's own company from partner selection
            self.fields['firma2'].queryset = Firma.objects.exclude(user=user)
            self.fields['firma2'].label = "Firma partnerska"
        
        # Set initial values
        self.fields['aktywne'].initial = True
        self.fields['auto_ksiegowanie'].initial = True
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate dates
        start_date = cleaned_data.get('data_rozpoczecia')
        end_date = cleaned_data.get('data_zakonczenia')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError({
                'data_zakonczenia': 'Data zakończenia musi być późniejsza niż data rozpoczęcia'
            })
        
        return cleaned_data


class PartnershipInviteForm(forms.Form):
    """
    Form for inviting companies to partnership
    """
    company_nip = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234567890',
            'pattern': '[0-9]{10}',
            'title': 'Wprowadź 10-cyfrowy numer NIP'
        }),
        label='NIP firmy partnerskiej'
    )
    
    partnership_type = forms.ChoiceField(
        choices=Partnerstwo.TYP_PARTNERSTWA_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Typ partnerstwa'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Wiadomość do partnera (opcjonalnie)'
        }),
        required=False,
        label='Wiadomość'
    )
    
    auto_accounting = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Włącz auto-księgowanie'
    )
    
    def clean_company_nip(self):
        """
        Validate and find company by NIP
        """
        nip = self.cleaned_data.get('company_nip', '').replace('-', '').replace(' ', '')
        
        if not nip:
            raise ValidationError('NIP jest wymagany')
        
        if len(nip) != 10 or not nip.isdigit():
            raise ValidationError('NIP musi składać się z 10 cyfr')
        
        try:
            company = Firma.objects.get(nip=nip)
            self.cleaned_data['target_company'] = company
        except Firma.DoesNotExist:
            raise ValidationError('Nie znaleziono firmy z podanym numerem NIP')
        
        return nip


class CompanyPermissionsForm(forms.Form):
    """
    Form for managing company-specific permissions
    """
    PERMISSION_CHOICES = [
        ('view_invoices', 'Przeglądanie faktur'),
        ('create_invoices', 'Tworzenie faktur'),
        ('edit_invoices', 'Edycja faktur'),
        ('delete_invoices', 'Usuwanie faktur'),
        ('view_contractors', 'Przeglądanie kontrahentów'),
        ('manage_contractors', 'Zarządzanie kontrahentami'),
        ('view_reports', 'Przeglądanie raportów'),
        ('manage_partnerships', 'Zarządzanie partnerstwami'),
    ]
    
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Użytkownik'
    )
    
    permissions = forms.MultipleChoiceField(
        choices=PERMISSION_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Uprawnienia'
    )
    
    def __init__(self, company=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        
        if company:
            # Filter users who have access to this company
            partnership_users = User.objects.filter(
                models.Q(firma__partnerstwa_jako_firma1__firma2=company) |
                models.Q(firma__partnerstwa_jako_firma2__firma1=company)
            ).distinct()
            
            self.fields['user'].queryset = partnership_users


class CompanyStatisticsFilterForm(forms.Form):
    """
    Form for filtering company statistics
    """
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False,
        label='Od daty'
    )
    
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False,
        label='Do daty'
    )
    
    invoice_type = forms.ChoiceField(
        choices=[
            ('', 'Wszystkie'),
            ('sprzedaz', 'Sprzedaż'),
            ('koszt', 'Koszty')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        label='Typ faktury'
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'Wszystkie'),
            ('wystawiona', 'Wystawione'),
            ('oplacona', 'Opłacone'),
            ('cz_oplacona', 'Częściowo opłacone'),
            ('anulowana', 'Anulowane')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        label='Status'
    )
    
    partner_company = forms.ModelChoiceField(
        queryset=Firma.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        label='Firma partnerska'
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'firma'):
            # Get partner companies
            partnerships = Partnerstwo.objects.filter(
                models.Q(firma1=user.firma) | models.Q(firma2=user.firma),
                aktywne=True
            ).select_related('firma1', 'firma2')
            
            partner_companies = []
            for partnership in partnerships:
                partner = partnership.firma2 if partnership.firma1 == user.firma else partnership.firma1
                partner_companies.append(partner)
            
            self.fields['partner_company'].queryset = Firma.objects.filter(
                id__in=[company.id for company in partner_companies]
            )