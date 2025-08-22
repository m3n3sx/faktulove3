"""
Main views module for faktury application

This file imports all views from modular structure to maintain 
backward compatibility with existing URL configurations.

The views are organized in the following modules:
- auth_views.py - Authentication and user management
- dashboard_views.py - Dashboard and reporting
- company_views.py - Company management
- contractor_views.py - Contractor management
- product_views.py - Product management
- invoice_views.py - Invoice management
- team_views.py - Team and task management
- notification_views.py - Notifications
- api_views.py - API endpoints
"""

# Import all views from modular structure
from .views.auth_views import *
from .views.dashboard_views import *
from .views.company_views import *
from .views.contractor_views import *
from .views.api_views import *

# TODO: Import remaining modules as they are created
# from .views.product_views import *
# from .views.invoice_views import *
# from .views.team_views import *
# from .views.notification_views import *

# Import remaining views from original file temporarily
# These will be moved to appropriate modules in next iterations
from .views_original import (
    # Product views
    produkty, dodaj_produkt, dodaj_produkt_ajax, edytuj_produkt,
    usun_produkt, pobierz_dane_produktu,
    
    # Invoice views
    szczegoly_faktury, dodaj_fakture_sprzedaz, dodaj_fakture_koszt,
    edytuj_fakture, usun_fakture, generuj_pdf, wyslij_fakture_mailem,
    generuj_wiele_pdf, update_payment, wyslij_przypomnienie,
    zarzadzaj_cyklem, stworz_proforma, stworz_korekte, stworz_paragon,
    generate_kp, kp_list, szczegoly_kp, konwertuj_proforme_na_fakture,
    
    # Team views
    lista_zespolow, szczegoly_zespolu, dodaj_zespol, edytuj_zespol,
    usun_zespol, wyslij_wiadomosc, dodaj_zadanie, edytuj_zadanie,
    usun_zadanie, oznacz_zadanie_jako_wykonane, szczegoly_czlonka_zespolu,
    twoje_sprawy, get_events, moje_zadania, dodaj_zadanie_uzytkownika,
    edytuj_zadanie_uzytkownika, usun_zadanie_uzytkownika,
    oznacz_zadanie_uzytkownika_wykonane, szczegoly_zadania_uzytkownika,
    get_calendar_data,
    
    # Partnership views
    dodaj_partnerstwo, lista_partnerstw, usun_partnerstwo, edytuj_partnerstwo,
    
    # Notification views
    notifications, mark_notification_read, notifications_list,
    delete_notification, mark_all_notifications_read, notifications_json,
    unread_notifications_count, szczegoly_wiadomosci, odp_wiadomosc,
    lista_wiadomosci, wyslij_systemowa,
    
    # Import/Export views
    export_kontrahenci, import_kontrahenci, export_produkty,
    import_produkty, export_faktury, import_faktury,
)
