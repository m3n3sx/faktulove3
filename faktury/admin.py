import datetime
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django import forms
from django.contrib import messages
from django.utils.html import format_html
from .models import (
    Kontrahent, Faktura, Produkt, PozycjaFaktury, Firma, UserProfile, Partnerstwo,
    DocumentUpload, OCRResult, OCRValidation, OCRProcessingLog, OCREngine, OCRProcessingStep
)
from .admin_widgets import (
    NIPWidget, CurrencyWidget, VATRateWidget, PolishDateWidget, 
    InvoiceStatusWidget, CompanySelectWidget
)
from .services.admin_enhancement_service import admin_enhancement_service


class FirmaAdminForm(forms.ModelForm):
    """Enhanced form for Firma with design system widgets"""
    
    class Meta:
        model = Firma
        fields = '__all__'
        widgets = {
            'nip': NIPWidget(),
        }

@admin.register(Firma)
class FirmaAdmin(admin.ModelAdmin):
    form = FirmaAdminForm
    list_display = ['nazwa', 'nip_formatted', 'miejscowosc']
    search_fields = ['nazwa', 'nip', 'miejscowosc']
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('nazwa', 'nip'),
            'classes': ('django-design-system', 'django-polish-business')
        }),
        ('Adres', {
            'fields': ('ulica', 'numer_domu', 'numer_mieszkania', 'miejscowosc', 'kod_pocztowy', 'kraj'),
            'classes': ('django-design-system',)
        }),
        ('Użytkownik', {
            'fields': ('user',),
            'classes': ('django-design-system',)
        }),
    )
    
    def nip_formatted(self, obj):
        """Display formatted NIP"""
        if obj.nip:
            import re
            clean_nip = re.sub(r'\D', '', str(obj.nip))
            if len(clean_nip) == 10:
                return f"{clean_nip[:3]}-{clean_nip[3:6]}-{clean_nip[6:8]}-{clean_nip[8:10]}"
        return obj.nip
    
    nip_formatted.short_description = 'NIP'

class ProduktAdminForm(forms.ModelForm):
    """Enhanced form for Produkt with design system widgets"""
    
    class Meta:
        model = Produkt
        fields = '__all__'
        widgets = {
            'cena_netto': CurrencyWidget(),
            'vat': VATRateWidget(),
        }

@admin.register(Produkt)
class ProduktAdmin(admin.ModelAdmin):
    form = ProduktAdminForm
    list_display = ['nazwa', 'cena_netto_formatted', 'vat_formatted', 'jednostka']
    list_filter = ['vat', 'jednostka']
    search_fields = ['nazwa']
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('nazwa',),
            'classes': ('django-design-system',)
        }),
        ('Ceny i podatki', {
            'fields': ('cena_netto', 'vat', 'jednostka'),
            'classes': ('django-design-system', 'django-polish-business')
        }),
        ('Użytkownik', {
            'fields': ('user',),
            'classes': ('django-design-system',)
        }),
    )
    
    def cena_netto_formatted(self, obj):
        """Display formatted price"""
        if obj.cena_netto:
            return f"{obj.cena_netto:,.2f} PLN".replace(',', ' ').replace('.', ',')
        return obj.cena_netto
    
    cena_netto_formatted.short_description = 'Cena netto'
    
    def vat_formatted(self, obj):
        """Display formatted VAT rate"""
        if obj.vat is not None:
            if obj.vat == -1:
                return 'zw.'
            elif obj.vat == 0:
                return '0%'
            else:
                return f'{int(obj.vat * 100)}%'
        return obj.vat
    
    vat_formatted.short_description = 'VAT'

class PozycjaFakturyAdminForm(forms.ModelForm):
    """Enhanced form for PozycjaFaktury with design system widgets"""
    
    class Meta:
        model = PozycjaFaktury
        fields = '__all__'
        widgets = {
            'cena_netto': CurrencyWidget(),
            'vat': VATRateWidget(),
        }

@admin.register(PozycjaFaktury)
class PozycjaFakturyAdmin(admin.ModelAdmin):
    form = PozycjaFakturyAdminForm
    list_display = ['nazwa', 'faktura', 'ilosc', 'cena_netto_formatted', 'vat_formatted']
    list_filter = ['vat', 'jednostka']
    search_fields = ['nazwa', 'faktura__numer']
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('faktura', 'nazwa'),
            'classes': ('django-design-system',)
        }),
        ('Ilość i ceny', {
            'fields': ('ilosc', 'jednostka', 'cena_netto', 'vat'),
            'classes': ('django-design-system', 'django-polish-business')
        }),
        ('Rabat', {
            'fields': ('rabat', 'rabat_typ'),
            'classes': ('django-design-system',)
        }),
    )
    
    def cena_netto_formatted(self, obj):
        """Display formatted price"""
        if obj.cena_netto:
            return f"{obj.cena_netto:,.2f} PLN".replace(',', ' ').replace('.', ',')
        return obj.cena_netto
    
    cena_netto_formatted.short_description = 'Cena netto'
    
    def vat_formatted(self, obj):
        """Display formatted VAT rate"""
        if obj.vat is not None:
            if obj.vat == -1:
                return 'zw.'
            elif obj.vat == 0:
                return '0%'
            else:
                return f'{int(obj.vat * 100)}%'
        return obj.vat
    
    vat_formatted.short_description = 'VAT'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telefon', 'imie', 'nazwisko']
    search_fields = ['user__username', 'user__email', 'telefon', 'imie', 'nazwisko']
    
    fieldsets = (
        ('Użytkownik', {
            'fields': ('user',),
            'classes': ('django-design-system',)
        }),
        ('Profil', {
            'fields': ('avatar', 'imie', 'nazwisko', 'telefon'),
            'classes': ('django-design-system',)
        }),
    )

@admin.register(Partnerstwo)
class PartnerstwoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'typ_partnerstwa', 'data_rozpoczecia', 'data_zakonczenia', 'aktywne']
    list_filter = ['aktywne', 'data_rozpoczecia', 'typ_partnerstwa']
    search_fields = ['firma1__nazwa', 'firma2__nazwa']
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('firma1', 'firma2', 'typ_partnerstwa', 'opis'),
            'classes': ('django-design-system',)
        }),
        ('Daty', {
            'fields': ('data_rozpoczecia', 'data_zakonczenia'),
            'classes': ('django-design-system', 'django-polish-business')
        }),
        ('Status', {
            'fields': ('aktywne', 'auto_ksiegowanie'),
            'classes': ('django-design-system',)
        }),
    )

class FakturaAdminForm(forms.ModelForm):
    """Enhanced form for Faktura with design system widgets"""
    
    class Meta:
        model = Faktura
        fields = '__all__'
        widgets = {
            'data_wystawienia': PolishDateWidget(),
            'data_sprzedazy': PolishDateWidget(),
            'termin_platnosci': PolishDateWidget(),
            'status': InvoiceStatusWidget(),
            'sprzedawca': CompanySelectWidget(),
            'nabywca': CompanySelectWidget(),
        }

@admin.register(Faktura)
class FakturaAdmin(admin.ModelAdmin):
    form = FakturaAdminForm
    list_display = ['numer', 'data_wystawienia', 'sprzedawca', 'nabywca', 'status_badge', 'ocr_confidence', 'manual_verification_required']
    list_filter = ('typ_dokumentu', 'status', 'manual_verification_required', 'ocr_extracted_at')
    search_fields = ['numer', 'sprzedawca__nazwa', 'nabywca__nazwa']
    readonly_fields = ['ocr_confidence', 'ocr_processing_time', 'ocr_extracted_at', 'source_document']
    actions = ['stwórz_korektę', 'bulk_mark_paid', 'bulk_mark_sent', 'bulk_export_pdf']
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('numer', 'data_wystawienia', 'data_sprzedazy', 'termin_platnosci', 'status'),
            'classes': ('django-design-system', 'django-polish-business')
        }),
        ('Kontrahenci', {
            'fields': ('sprzedawca', 'nabywca'),
            'classes': ('django-design-system', 'django-polish-business')
        }),
        ('Szczegóły', {
            'fields': ('typ_dokumentu', 'typ_faktury', 'waluta', 'sposob_platnosci', 'uwagi'),
            'classes': ('django-design-system',)
        }),
        ('OCR Information', {
            'fields': ('source_document', 'ocr_confidence', 'manual_verification_required', 'ocr_processing_time', 'ocr_extracted_at'),
            'classes': ('collapse', 'django-design-system')
        }),
    )
    
    def status_badge(self, obj):
        """Display status as a badge"""
        status_map = {
            'draft': ('Szkic', 'draft'),
            'sent': ('Wysłana', 'sent'),
            'paid': ('Opłacona', 'paid'),
            'overdue': ('Przeterminowana', 'overdue'),
            'cancelled': ('Anulowana', 'cancelled'),
        }
        
        if obj.status in status_map:
            text, css_class = status_map[obj.status]
            return f'<span class="status-badge {css_class}">{text}</span>'
        return obj.status
    
    status_badge.short_description = 'Status'
    status_badge.allow_tags = True

    def stworz_korekte(self, request, queryset):
        for faktura in queryset:
        # Generuj nowy numer dla korekty
            today = datetime.date.today()
            ostatnia_korekta = Faktura.objects.filter(
            user=faktura.user,
            data_wystawienia__year=today.year,
            data_wystawienia__month=today.month,
            typ_dokumentu='KOR',
        ).order_by('-numer').first()

        if ostatnia_korekta:
            try:
                ostatni_numer = int(ostatnia_korekta.numer.split('/')[1])
                numer_korekty = f"KOR/{ostatni_numer + 1:02d}/{today.month:02d}/{today.year}"
            except (ValueError, IndexError):
                liczba_korekt = Faktura.objects.filter(
                    user=faktura.user,
                    data_wystawienia__year=today.year,
                    data_wystawienia__month=today.month,
                    typ_dokumentu='KOR'
                ).count()
                numer_korekty = f"KOR/{liczba_korekt + 1:02d}/{today.month:02d}/{today.year}"
        else:
            numer_korekty = f"KOR/01/{today.month:02d}/{today.year}"

        # Utwórz nową Fakturę (korektę)
        korekta = Faktura.objects.create(
            user=faktura.user,
            typ_dokumentu='KOR',
            dokument_podstawowy=faktura,
            numer=numer_korekty,  # Użyj wygenerowanego numeru
            data_wystawienia=datetime.date.today(),  # Data wystawienia korekty
            data_sprzedazy=faktura.data_sprzedazy,
            miejsce_wystawienia=faktura.miejsce_wystawienia,
            sprzedawca=faktura.sprzedawca,
            nabywca=faktura.nabywca,
            typ_faktury=faktura.typ_faktury,
            zwolnienie_z_vat=faktura.zwolnienie_z_vat,
            powod_zwolnienia=faktura.powod_zwolnienia,
            sposob_platnosci=faktura.sposob_platnosci,
            termin_platnosci=faktura.termin_platnosci,
            waluta=faktura.waluta,
            wystawca=faktura.wystawca,
            odbiorca=faktura.odbiorca,
            uwagi=faktura.uwagi,
            auto_numer=faktura.auto_numer,
            wlasny_numer=faktura.wlasny_numer,
        )

        # Skopiuj pozycje faktury
        for pozycja in faktura.pozycjafaktury_set.all():
            PozycjaFaktury.objects.create(
                faktura=korekta,
                nazwa=pozycja.nazwa,
                ilosc=pozycja.ilosc,
                jednostka=pozycja.jednostka,
                cena_netto=pozycja.cena_netto,
                vat=pozycja.vat,
                rabat=pozycja.rabat,
                rabat_typ=pozycja.rabat_typ,
            )
    
    def bulk_mark_paid(self, request, queryset):
        """Bulk action to mark invoices as paid"""
        updated = queryset.update(status='paid')
        messages.success(
            request, 
            f'Oznaczono {updated} faktur jako opłacone'
        )
    bulk_mark_paid.short_description = "Oznacz jako opłacone"
    
    def bulk_mark_sent(self, request, queryset):
        """Bulk action to mark invoices as sent"""
        updated = queryset.update(status='sent')
        messages.success(
            request, 
            f'Oznaczono {updated} faktur jako wysłane'
        )
    bulk_mark_sent.short_description = "Oznacz jako wysłane"
    
    def bulk_export_pdf(self, request, queryset):
        """Bulk action to export invoices as PDF"""
        # This would need PDF generation implementation
        messages.info(
            request, 
            f'Eksport PDF dla {queryset.count()} faktur zostanie wkrótce zaimplementowany'
        )
    bulk_export_pdf.short_description = "Eksportuj jako PDF"


class KontrahentAdminForm(forms.ModelForm):
    """Enhanced form for Kontrahent with design system widgets"""
    
    class Meta:
        model = Kontrahent
        fields = '__all__'
        widgets = {
            'nip': NIPWidget(),
        }

class KontrahentResource(resources.ModelResource):
    class Meta:
        model = Kontrahent
        fields = ('nazwa', 'nip', 'ulica', 'numer_domu', 'miejscowosc', 'kod_pocztowy', 'kraj', 'email', 'telefon')
        export_order = fields

class FakturaResource(resources.ModelResource):
    pozycje = fields.Field(column_name='pozycje', attribute='pozycje')
    
    class Meta:
        model = Faktura
        fields = ('numer', 'data_wystawienia', 'data_sprzedazy', 'sprzedawca', 'nabywca', 'status', 'pozycje')
        export_order = fields
    
    def dehydrate_pozycje(self, faktura):
        return ", ".join([f"{p.nazwa} ({p.ilosc}{p.jednostka})" for p in faktura.pozycjafaktury_set.all()])

class ProduktResource(resources.ModelResource):
    class Meta:
        model = Produkt
        fields = ('nazwa', 'cena_netto', 'vat', 'jednostka')
        export_order = fields

@admin.register(Kontrahent)
class KontrahentAdmin(ImportExportModelAdmin):
    form = KontrahentAdminForm
    resource_class = KontrahentResource
    list_display = ['nazwa', 'nip_formatted', 'miejscowosc', 'email', 'telefon', 'is_own_company']
    list_filter = ['is_own_company', 'kraj', 'czy_firma']
    search_fields = ['nazwa', 'nip', 'email', 'miejscowosc']
    actions = ['bulk_mark_as_company', 'bulk_export_contacts']
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('nazwa', 'nip', 'is_own_company'),
            'classes': ('django-design-system', 'django-polish-business')
        }),
        ('Adres', {
            'fields': ('ulica', 'numer_domu', 'numer_mieszkania', 'miejscowosc', 'kod_pocztowy', 'kraj'),
            'classes': ('django-design-system',)
        }),
        ('Kontakt', {
            'fields': ('email', 'telefon'),
            'classes': ('django-design-system',)
        }),
    )
    
    def nip_formatted(self, obj):
        """Display formatted NIP"""
        if obj.nip:
            import re
            clean_nip = re.sub(r'\D', '', str(obj.nip))
            if len(clean_nip) == 10:
                return f"{clean_nip[:3]}-{clean_nip[3:6]}-{clean_nip[6:8]}-{clean_nip[8:10]}"
        return obj.nip
    
    nip_formatted.short_description = 'NIP'


# ============================================================================
# OCR ADMIN CONFIGURATIONS
# ============================================================================

@admin.register(DocumentUpload)
class DocumentUploadAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'processing_status', 'upload_timestamp', 'file_size_mb']
    list_filter = ['processing_status', 'content_type', 'upload_timestamp']
    search_fields = ['original_filename', 'user__username', 'user__email']
    readonly_fields = ['upload_timestamp', 'processing_started_at', 'processing_completed_at', 'file_size']
    date_hierarchy = 'upload_timestamp'
    
    def file_size_mb(self, obj):
        return f"{obj.file_size / (1024 * 1024):.2f} MB"
    file_size_mb.short_description = 'Rozmiar'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(OCRResult)
class OCRResultAdmin(admin.ModelAdmin):
    list_display = ['document_filename', 'confidence_score', 'processing_time', 'has_invoice', 'vendor_independent', 'ocr_engine', 'created_at']
    list_filter = ['created_at', 'processor_version', 'vendor_independent', 'google_cloud_replaced', 'ocr_engine']
    search_fields = ['document__original_filename', 'document__user__username', 'faktura__numer', 'ocr_engine']
    readonly_fields = ['created_at', 'processing_time', 'confidence_score', 'raw_text']
    date_hierarchy = 'created_at'
    
    def document_filename(self, obj):
        return obj.document.original_filename
    document_filename.short_description = 'Plik'
    
    def has_invoice(self, obj):
        return bool(obj.faktura)
    has_invoice.boolean = True
    has_invoice.short_description = 'Faktura utworzona'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('document', 'faktura')
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('document', 'confidence_score', 'processing_time', 'processing_status')
        }),
        ('Dane OCR', {
            'fields': ('raw_text', 'extracted_data', 'field_confidence')
        }),
        ('Vendor Independence', {
            'fields': ('vendor_independent', 'google_cloud_replaced', 'ocr_engine', 'ensemble_engines_used', 'cost_per_processing'),
            'classes': ('collapse',)
        }),
        ('Powiązania', {
            'fields': ('faktura', 'auto_created_faktura')
        }),
    )


@admin.register(OCRValidation)
class OCRValidationAdmin(admin.ModelAdmin):
    list_display = ['document_filename', 'validated_by', 'accuracy_rating', 'corrections_count', 'validation_timestamp']
    list_filter = ['accuracy_rating', 'validation_timestamp']
    search_fields = ['ocr_result__document__original_filename', 'validated_by__username']
    readonly_fields = ['validation_timestamp', 'corrections_count']
    date_hierarchy = 'validation_timestamp'
    
    def document_filename(self, obj):
        return obj.ocr_result.document.original_filename
    document_filename.short_description = 'Plik'
    
    def corrections_count(self, obj):
        return obj.corrections_count
    corrections_count.short_description = 'Liczba poprawek'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ocr_result__document', 'validated_by')


@admin.register(OCRProcessingLog)
class OCRProcessingLogAdmin(admin.ModelAdmin):
    list_display = ['document_filename', 'level', 'message_preview', 'timestamp']
    list_filter = ['level', 'timestamp']
    search_fields = ['document__original_filename', 'message']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def document_filename(self, obj):
        return obj.document.original_filename
    document_filename.short_description = 'Plik'
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Wiadomość'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('document')


@admin.register(OCREngine)
class OCREngineAdmin(admin.ModelAdmin):
    list_display = ['name', 'engine_type', 'version', 'is_active', 'priority', 'total_documents_processed', 'average_confidence_score']
    list_filter = ['engine_type', 'is_active', 'created_at']
    search_fields = ['name', 'version']
    readonly_fields = ['created_at', 'updated_at', 'total_documents_processed', 'average_processing_time', 'average_confidence_score', 'success_rate']
    ordering = ['priority', 'name']
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('name', 'engine_type', 'version', 'is_active', 'priority')
        }),
        ('Konfiguracja', {
            'fields': ('configuration',)
        }),
        ('Statystyki wydajności', {
            'fields': ('total_documents_processed', 'average_processing_time', 'average_confidence_score', 'success_rate'),
            'classes': ('collapse',)
        }),
        ('Metadane', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OCRProcessingStep)
class OCRProcessingStepAdmin(admin.ModelAdmin):
    list_display = ['step_name', 'ocr_result_filename', 'engine_used', 'step_status', 'confidence_score', 'processing_time', 'started_at']
    list_filter = ['step_type', 'step_status', 'engine_used', 'started_at']
    search_fields = ['step_name', 'ocr_result__document__original_filename', 'engine_used__name']
    readonly_fields = ['started_at', 'completed_at', 'processing_time']
    date_hierarchy = 'started_at'
    
    def ocr_result_filename(self, obj):
        return obj.ocr_result.document.original_filename
    ocr_result_filename.short_description = 'Plik'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ocr_result__document', 'engine_used')
    
    fieldsets = (
        ('Informacje o kroku', {
            'fields': ('ocr_result', 'step_name', 'step_type', 'engine_used', 'step_order')
        }),
        ('Status i wyniki', {
            'fields': ('step_status', 'confidence_score', 'processing_time', 'started_at', 'completed_at')
        }),
        ('Dane', {
            'fields': ('input_data', 'output_data', 'step_data', 'error_message'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# ADMIN ENHANCEMENT SERVICE SETUP
# ============================================================================

# Setup enhanced admin features
try:
    admin_enhancement_service.setup_enhanced_admin()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to setup enhanced admin features: {str(e)}")


# Add bulk operations to existing admin classes
def add_bulk_operations_to_kontrahent():
    """Add bulk operations to KontrahentAdmin"""
    def bulk_mark_as_company(modeladmin, request, queryset):
        """Bulk action to mark contractors as companies"""
        updated = queryset.update(czy_firma=True)
        messages.success(
            request, 
            f'Oznaczono {updated} kontrahentów jako firmy'
        )
    bulk_mark_as_company.short_description = "Oznacz jako firmy"
    
    def bulk_export_contacts(modeladmin, request, queryset):
        """Bulk action to export contact information"""
        messages.info(
            request, 
            f'Eksport kontaktów dla {queryset.count()} kontrahentów zostanie wkrótce zaimplementowany'
        )
    bulk_export_contacts.short_description = "Eksportuj kontakty"
    
    # Add actions to KontrahentAdmin
    if Kontrahent in admin.site._registry:
        kontrahent_admin = admin.site._registry[Kontrahent]
        if kontrahent_admin.actions is None:
            kontrahent_admin.actions = []
        elif isinstance(kontrahent_admin.actions, tuple):
            kontrahent_admin.actions = list(kontrahent_admin.actions)
        kontrahent_admin.actions.extend([bulk_mark_as_company, bulk_export_contacts])


def add_bulk_operations_to_firma():
    """Add bulk operations to FirmaAdmin"""
    def bulk_activate_companies(modeladmin, request, queryset):
        """Bulk action to activate companies"""
        # Assuming there's an 'active' field, otherwise skip this
        messages.info(
            request, 
            f'Aktywacja {queryset.count()} firm zostanie wkrótce zaimplementowana'
        )
    bulk_activate_companies.short_description = "Aktywuj firmy"
    
    # Add actions to FirmaAdmin
    if Firma in admin.site._registry:
        firma_admin = admin.site._registry[Firma]
        if firma_admin.actions is None:
            firma_admin.actions = []
        elif isinstance(firma_admin.actions, tuple):
            firma_admin.actions = list(firma_admin.actions)
        firma_admin.actions.append(bulk_activate_companies)


# Apply bulk operations
try:
    add_bulk_operations_to_kontrahent()
    add_bulk_operations_to_firma()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to add bulk operations: {str(e)}")


# Customize admin site
admin.site.site_header = "FaktuLove - Panel Administracyjny"
admin.site.site_title = "FaktuLove Admin"
admin.site.index_title = "Zarządzanie systemem FaktuLove"