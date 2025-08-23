"""
Modular views for faktury application

This package organizes views into logical modules:
- auth_views.py - Authentication and user management
- invoice_views.py - Invoice management (creation, editing, PDF)
- contractor_views.py - Contractor management
- company_views.py - Company management
- product_views.py - Product management
- team_views.py - Team and task management
- notification_views.py - Notifications
- api_views.py - API endpoints
- dashboard_views.py - Dashboard and reports
"""

# Import all views to maintain compatibility with existing URLs
from .auth_views import *
from .contractor_views import *
from .company_views import *
from .api_views import *
from .dashboard_views import *
from .ocr_views import *
# from .import_export_views import *  # Will be created later

# TODO: Import remaining modules as they are created
# from .invoice_views import *
# from .product_views import *
# from .team_views import *
# from .notification_views import *

# Maintain backward compatibility
__all__ = [
    # Auth views
    'register', 'user_profile', 'rejestracja',
    
    # Dashboard
    'panel_uzytkownika', 'faktury_sprzedaz', 'faktury_koszt',
    
    # Invoice views
    'szczegoly_faktury', 'dodaj_fakture_sprzedaz', 'dodaj_fakture_koszt',
    'edytuj_fakture', 'usun_fakture', 'generuj_pdf', 'wyslij_fakture_mailem',
    'generuj_wiele_pdf', 'update_payment', 'wyslij_przypomnienie',
    'zarzadzaj_cyklem', 'stworz_proforma', 'stworz_korekte', 'stworz_paragon',
    'generate_kp', 'kp_list', 'szczegoly_kp', 'konwertuj_proforme_na_fakture',
    
    # Contractor views
    'kontrahenci', 'dodaj_kontrahenta', 'dodaj_kontrahenta_ajax',
    'edytuj_kontrahenta', 'usun_kontrahenta', 'szczegoly_kontrahenta',
    'pobierz_dane_kontrahenta', 'pobierz_dane_z_gus',
    
    # Company views
    'dodaj_firme', 'edytuj_firme',
    
    # Product views
    'produkty', 'dodaj_produkt', 'dodaj_produkt_ajax', 'edytuj_produkt',
    'usun_produkt', 'pobierz_dane_produktu',
    
    # Team views
    'lista_zespolow', 'szczegoly_zespolu', 'dodaj_zespol', 'edytuj_zespol',
    'usun_zespol', 'wyslij_wiadomosc', 'dodaj_zadanie', 'edytuj_zadanie',
    'usun_zadanie', 'oznacz_zadanie_jako_wykonane', 'szczegoly_czlonka_zespolu',
    'twoje_sprawy', 'get_events', 'moje_zadania', 'dodaj_zadanie_uzytkownika',
    'edytuj_zadanie_uzytkownika', 'usun_zadanie_uzytkownika',
    'oznacz_zadanie_uzytkownika_wykonane', 'szczegoly_zadania_uzytkownika',
    'get_calendar_data',
    
    # Partnership views
    'dodaj_partnerstwo', 'lista_partnerstw', 'usun_partnerstwo', 'edytuj_partnerstwo',
    
    # Notification views
    'notifications', 'mark_notification_read', 'notifications_list',
    'delete_notification', 'mark_all_notifications_read', 'notifications_json',
    'unread_notifications_count', 'szczegoly_wiadomosci', 'odp_wiadomosc',
    'lista_wiadomosci', 'wyslij_systemowa',
    
    # Import/Export views
    'export_kontrahenci', 'import_kontrahenci', 'export_produkty',
    'import_produkty', 'export_faktury', 'import_faktury',
    
    # API views
    'api_faktury_list', 'api_faktura_detail', 'api_kontrahenci_list',
    'api_kontrahent_detail', 'api_produkty_list', 'api_produkt_detail',
    'api_zadania_list', 'api_zadanie_detail', 'check_payment_terms',
    
    # OCR views
    'ocr_upload_view', 'ocr_status_view', 'ocr_results_list', 'ocr_result_detail',
    'create_invoice_from_ocr', 'api_upload_document', 'api_processing_status',
    'api_ocr_statistics',
]
