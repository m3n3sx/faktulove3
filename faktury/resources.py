from import_export import resources, fields
from .models import Kontrahent, Produkt, Faktura, PozycjaFaktury

class KontrahentResource(resources.ModelResource):
    class Meta:
        model = Kontrahent
        fields = ('nazwa', 'nip', 'adres', 'miasto', 'kod_pocztowy', 'kraj', 'email', 'telefon')

class ProduktResource(resources.ModelResource):
    class Meta:
        model = Produkt
        fields = ('nazwa', 'cena_netto', 'vat', 'jednostka', 'opis')

class FakturaResource(resources.ModelResource):
    pozycje = fields.Field(column_name='pozycje', attribute='pozycjafaktury_set')
    
    class Meta:
        model = Faktura
        fields = ('id', 'numer', 'data_wystawienia', 'data_sprzedazy', 'sprzedawca', 'nabywca', 'status', 'pozycje')
        export_order = fields  # Zachowaj kolejność
    def dehydrate_pozycje(self, faktura):
        return " | ".join([
            f"{p.nazwa} ({p.ilosc}{p.jednostka} x {p.cena_netto} + {p.vat}%)"
            for p in faktura.pozycjafaktury_set.all()
        ])
