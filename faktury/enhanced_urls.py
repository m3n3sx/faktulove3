"""
Enhanced URLs for Polish invoice system
URLe dla wszystkich typów dokumentów zgodnych z polskim prawem
"""
from django.urls import path
from . import enhanced_invoice_views

app_name = 'enhanced'

urlpatterns = [
    # Lista dokumentów
    path('dokumenty/', enhanced_invoice_views.lista_dokumentow, name='lista_dokumentow'),
    
    # Faktury VAT
    path('nowa-faktura-vat/', enhanced_invoice_views.dodaj_fakture_vat, name='dodaj_fakture_vat'),
    
    # Faktury Pro Forma
    path('nowa-proforma/', enhanced_invoice_views.dodaj_proforma, name='dodaj_proforma'),
    path('konwertuj-proforma/<int:proforma_id>/', enhanced_invoice_views.konwertuj_proforma_na_fakture, name='konwertuj_proforma'),
    
    # Faktury korygujące
    path('nowa-korekta/', enhanced_invoice_views.dodaj_korekte, name='dodaj_korekte'),
    path('nowa-korekta/<int:faktura_id>/', enhanced_invoice_views.dodaj_korekte, name='dodaj_korekte_dla'),
    
    # Rachunki
    path('nowy-rachunek/', enhanced_invoice_views.dodaj_rachunek, name='dodaj_rachunek'),
    
    # Faktury zaliczkowe
    path('nowa-faktura-zaliczkowa/', enhanced_invoice_views.dodaj_fakture_zaliczkowa, name='dodaj_fakture_zaliczkowa'),
    
    # Dokumenty kasowe
    path('nowy-dokument-kasowy/', enhanced_invoice_views.dodaj_dokument_kasowy, name='dodaj_dokument_kasowy'),
    
    # Raporty
    path('raport-vat/', enhanced_invoice_views.raport_vat, name='raport_vat'),
    
    # API endpoints
    path('api/kontrahenci-autocomplete/', enhanced_invoice_views.api_kontrahenci_autocomplete, name='api_kontrahenci_autocomplete'),
    path('api/produkty-autocomplete/', enhanced_invoice_views.api_produkty_autocomplete, name='api_produkty_autocomplete'),
    path('api/kontrahenci-create/', enhanced_invoice_views.api_kontrahenci_create, name='api_kontrahenci_create'),
]
