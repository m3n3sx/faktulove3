# Explicit import version - import specific functions we need
from .views_original import (
    # Auth views
    register, user_profile, rejestracja,
    
    # Dashboard views
    panel_uzytkownika, faktury_sprzedaz, faktury_koszt,
    
    # Invoice views 
    szczegoly_faktury, dodaj_fakture_sprzedaz, dodaj_fakture_koszt,
    edytuj_fakture, usun_fakture, generuj_pdf, wyslij_fakture_mailem,
    generuj_wiele_pdf, update_payment, wyslij_przypomnienie,
    zarzadzaj_cyklem, stworz_proforma, stworz_korekte, stworz_paragon,
    generate_kp, kp_list, szczegoly_kp, konwertuj_proforme_na_fakture,
    
    # Contractor views
    kontrahenci, dodaj_kontrahenta, dodaj_kontrahenta_ajax,
    edytuj_kontrahenta, usun_kontrahenta, szczegoly_kontrahenta,
    pobierz_dane_kontrahenta, pobierz_dane_z_gus,
    
    # Company views
    dodaj_firme, edytuj_firme,
    
    # Product views
    produkty, dodaj_produkt, dodaj_produkt_ajax, edytuj_produkt,
    usun_produkt, pobierz_dane_produktu,
    
    # Team views
    lista_zespolow, szczegoly_zespolu, dodaj_zespol, edytuj_zespol,
    usun_zespol, wyslij_wiadomosc, dodaj_zadanie, edytuj_zadanie,
    usun_zadanie, oznacz_zadanie_jako_wykonane, szczegoly_czlonka_zespolu,
    twoje_sprawy, get_events, moje_zadania, dodaj_zadanie_uzytkownika,
    edytuj_zadanie_uzytkownika, usun_zadanie_uzytkownika,
    oznacz_zadanie_uzytkownika_wykonane, szczegoly_zadania_uzytkownika,
    get_calendar_data,
    
    # Notification views
    notifications, mark_notification_read, notifications_list,
    delete_notification, mark_all_notifications_read, notifications_json,
    unread_notifications_count, szczegoly_wiadomosci, odp_wiadomosc,
    lista_wiadomosci, wyslij_systemowa,
    
    # API views
    api_faktury_list, api_faktura_detail, api_kontrahenci_list,
    api_kontrahent_detail, api_produkty_list, api_produkt_detail,
    api_zadania_list, api_zadanie_detail, check_payment_terms,
)

# Add new modular views
try:
    from .views.import_export_views import (
        export_kontrahenci, import_kontrahenci, export_produkty,
        import_produkty, export_faktury, import_faktury
    )
    from .views.partnership_views import (
        dodaj_partnerstwo, lista_partnerstw, usun_partnerstwo, edytuj_partnerstwo
    )
    from .views.recurring_views import (
        lista_faktur_cyklicznych, dodaj_fakture_cykliczna, edytuj_fakture_cykliczna,
        usun_fakture_cykliczna, generuj_fakture_cykliczna_manualnie, zakoncz_cykl_faktury
    )
    from .views.calendar_views import (
        kalendarz, get_events_json, dashboard_kalendarza, get_calendar_stats
    )
except ImportError:
    # Create placeholder functions for import/export if they don't exist
    from django.shortcuts import redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    
    @login_required
    def export_kontrahenci(request):
        messages.info(request, "Funkcja eksportu będzie dostępna wkrótce.")
        return redirect('kontrahenci')
    
    @login_required
    def import_kontrahenci(request):
        messages.info(request, "Funkcja importu będzie dostępna wkrótce.")
        return redirect('kontrahenci')
    
    @login_required
    def export_produkty(request):
        messages.info(request, "Funkcja eksportu będzie dostępna wkrótce.")
        return redirect('produkty')
    
    @login_required
    def import_produkty(request):
        messages.info(request, "Funkcja importu będzie dostępna wkrótce.")
        return redirect('produkty')
    
    @login_required
    def export_faktury(request):
        messages.info(request, "Funkcja eksportu będzie dostępna wkrótce.")
        return redirect('panel_uzytkownika')
    
    @login_required
    def import_faktury(request):
        messages.info(request, "Funkcja importu będzie dostępna wkrótce.")
        return redirect('panel_uzytkownika')
