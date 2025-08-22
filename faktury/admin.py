import datetime
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import (
    Kontrahent, Faktura, Produkt, PozycjaFaktury, Firma, UserProfile, Partnerstwo,
    DocumentUpload, OCRResult, OCRValidation, OCRProcessingLog
)


admin.site.register(Firma)
admin.site.register(Produkt)
admin.site.register(PozycjaFaktury)
admin.site.register(UserProfile)
admin.site.register(Partnerstwo)

@admin.register(Faktura)
class FakturaAdmin(admin.ModelAdmin):
    list_filter = ('typ_dokumentu', 'status')
    actions = ['stwórz_korektę']

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


class KontrahentResource(resources.ModelResource):
    class Meta:
        model = Kontrahent
        fields = ('nazwa', 'nip', 'adres', 'miasto', 'kod_pocztowy', 'kraj', 'email', 'telefon')
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
        fields = ('nazwa', 'cena_netto', 'vat', 'jednostka', 'opis')
        export_order = fields

@admin.register(Kontrahent)
class KontrahentAdmin(ImportExportModelAdmin):
    resource_class = KontrahentResource


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
    list_display = ['document_filename', 'confidence_score', 'confidence_level', 'processing_time', 'has_invoice', 'created_at']
    list_filter = ['confidence_level', 'created_at', 'processor_version']
    search_fields = ['document__original_filename', 'document__user__username', 'faktura__numer']
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