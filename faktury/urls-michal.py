from django.urls import path, include
from django.contrib.auth import views as auth_views
from faktury.views import (
    auth_views, team_views, invoice_views, contractor_views,
    product_views, task_views, firm_views, partnership_views,  utils
)

urlpatterns = [
    # Panel użytkownika
    path('', auth_views.user_profile, name='panel_uzytkownika'),

    # Firma
    path('firma/dodaj/', firm_views.dodaj_firme, name='dodaj_firme'),
    path('firma/edytuj/<int:pk>/', firm_views.edytuj_firme, name='edytuj_firme'),
    
    # Rejestracja i logowanie
    path('accounts/', include('allauth.urls')),
    
    # Faktury
    path('faktury/sprzedaz/', invoice_views.faktury_sprzedaz, name='faktury_sprzedaz'),
    path('faktury/koszt/', invoice_views.faktury_koszt, name='faktury_koszt'),
    path('faktura/dodaj/', invoice_views.dodaj_fakture_sprzedaz, name='dodaj_fakture'),
    path('faktura/dodaj/koszt/', invoice_views.dodaj_fakture_koszt, name='dodaj_fakture_koszt'),
    path('faktura/edytuj/<int:pk>/', invoice_views.edytuj_fakture, name='edytuj_fakture'),
    path('faktura/usun/<int:pk>/', invoice_views.usun_fakture, name='usun_fakture'),
    path('faktura/<int:pk>/', invoice_views.szczegoly_faktury, name='szczegoly_faktury'),
    path('faktura/<int:pk>/wyslij/', invoice_views.wyslij_fakture_mailem, name='wyslij_fakture'),
    path('faktura/<int:pk>/przypomnij/', invoice_views.wyslij_przypomnienie, name='wyslij_przypomnienie'),

    # Partnerzy
    path('partnerstwa/', partnership_views.lista_partnerstw, name='lista_partnerstw'),
    path('partnerstwa/dodaj/', partnership_views.dodaj_partnerstwo, name='dodaj_partnerstwo'),
    path('partnerstwa/edytuj/<int:pk>/', partnership_views.edytuj_partnerstwo, name='edytuj_partnerstwo'),
    path('partnerstwa/usun/<int:pk>/', partnership_views.usun_partnerstwo, name='usun_partnerstwo'),
    
    # Kontrahenci
    path('kontrahenci/', contractor_views.kontrahenci, name='kontrahenci'),
    path('kontrahenci/dodaj/', contractor_views.dodaj_kontrahenta, name='dodaj_kontrahenta'),
    path('kontrahenci/edytuj/<int:pk>/', contractor_views.edytuj_kontrahenta, name='edytuj_kontrahenta'),
    path('kontrahenci/usun/<int:pk>/', contractor_views.usun_kontrahenta, name='usun_kontrahenta'),
    path('kontrahenci/<int:pk>/', contractor_views.szczegoly_kontrahenta, name='szczegoly_kontrahenta'),
    path('kontrahenci/import/', contractor_views.import_kontrahenci, name='import_kontrahenci'),
    
    # Produkty
    path('produkty/', product_views.produkty, name='produkty'),
    path('produkty/dodaj/', product_views.dodaj_produkt, name='dodaj_produkt'),
    path('produkty/edytuj/<int:pk>/', product_views.edytuj_produkt, name='edytuj_produkt'),
    path('produkty/usun/<int:pk>/', product_views.usun_produkt, name='usun_produkt'),
    
    # Zadania
    path('moje_zadania/', task_views.moje_zadania, name='moje_zadania'),
    path('zadania/dodaj/', task_views.dodaj_zadanie_uzytkownika, name='dodaj_zadanie_uzytkownika'),
    path('zadania/edytuj/<int:pk>/', task_views.edytuj_zadanie_uzytkownika, name='edytuj_zadanie_uzytkownika'),
    path('zadania/usun/<int:pk>/', task_views.usun_zadanie_uzytkownika, name='usun_zadanie_uzytkownika'),
    path('zadania/oznacz/<int:pk>/', task_views.oznacz_zadanie_uzytkownika_wykonane, name='oznacz_zadanie_uzytkownika'),
    path('zadania/<int:pk>/', task_views.szczegoly_zadania_uzytkownika, name='szczegoly_zadania_uzytkownika'),
    path('twoje-sprawy/', task_views.twoje_sprawy, name='twoje_sprawy'),
    
    # Zespoły
    path('zespoly/', team_views.lista_zespolow, name='lista_zespolow'),
    path('zespoly/<int:zespol_id>/', team_views.szczegoly_zespolu, name='szczegoly_zespolu'),
    path('zespoly/dodaj/', team_views.dodaj_zespol, name='dodaj_zespol'),
    path('zespoly/edytuj/<int:zespol_id>/', team_views.edytuj_zespol, name='edytuj_zespol'),
    path('zespoly/usun/<int:zespol_id>/', team_views.usun_zespol, name='usun_zespol'),
]
