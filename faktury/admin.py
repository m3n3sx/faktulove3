import datetime
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Kontrahent, Faktura, Produkt, PozycjaFaktury, Firma, UserProfile, Partnerstwo


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