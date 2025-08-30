from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from . import views_modules
from .views_modules import ocr_status_views, search_api_views, data_export_import_views, health_monitoring_views
from .admin_api import DashboardStatsView, SystemHealthView, RecentActivityView

urlpatterns = [
path('api/get-company-data/', views.pobierz_dane_z_gus, name='pobierz_dane_z_gus'),
    path('', views.panel_uzytkownika, name='panel_uzytkownika'),
    path('dashboard/', views.panel_uzytkownika, name='dashboard'),  # Alias for main dashboard
    path('edytuj_fakture/<int:pk>/', views.edytuj_fakture, name='edytuj_fakture'),
    path('usun_fakture/<int:pk>/', views.usun_fakture, name='usun_fakture'),
    path('dodaj_kontrahenta/', views.dodaj_kontrahenta, name='dodaj_kontrahenta'),
    path('edytuj_kontrahenta/<int:pk>/', views.edytuj_kontrahenta, name='edytuj_kontrahenta'),
    path('usun_kontrahenta/<int:pk>/', views.usun_kontrahenta, name='usun_kontrahenta'),
    path('dodaj_firme/', views.dodaj_firme, name='dodaj_firme'),
    path('edytuj_firme/', views.edytuj_firme, name='edytuj_firme'),
    
    # Company aliases for better UX
    path('company/', views.company_dashboard, name='company'),
    path('company.html', views.company_dashboard, name='company_html'),
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/info/', views.company_info, name='company_info'),
    path('company/settings/', views.company_settings, name='company_settings'),
    path('company/status/', views.company_api_status, name='company_api_status'),
    
    # Profile and user pages
    path('view-profile.html', views.view_profile, name='view_profile_html'),
    path('profile/', views.view_profile, name='view_profile'),
    
    # Email and notifications
    path('email.html', views.email_inbox, name='email_html'),
    path('email/', views.email_inbox, name='email_inbox'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('firma/', views.edytuj_firme, name='firma'),
    path('dodaj_produkt/', views.dodaj_produkt, name='dodaj_produkt'),
    path('edytuj_produkt/<int:pk>/', views.edytuj_produkt, name='edytuj_produkt'),
    path('usun_produkt/<int:pk>/', views.usun_produkt, name='usun_produkt'),
    path('pobierz_dane_z_gus/', views.pobierz_dane_z_gus, name='pobierz_dane_z_gus'),
    path('generuj_pdf/<int:pk>/', views.generuj_pdf, name='generuj_pdf'),
    path('test-cdn-fallback/', views.test_cdn_fallback, name='test_cdn_fallback'),
    path('pobierz_dane_kontrahenta/', views.pobierz_dane_kontrahenta, name='pobierz_dane_kontrahenta'),
    path('update_payment/<int:pk>/', views.update_payment, name='update_payment'),
    path('dodaj_kontrahenta_ajax/', views.dodaj_kontrahenta_ajax, name='dodaj_kontrahenta_ajax'),
    path('kontrahenci/', views.kontrahenci, name='kontrahenci'),
    path('produkty/', views.produkty, name='produkty'),
    path('generuj_wiele_pdf/', views.generuj_wiele_pdf, name='generuj_wiele_pdf'),
    path('dodaj_fakture/', views.dodaj_fakture_sprzedaz, name='dodaj_fakture'),
    path('dodaj_fakture/koszt/', views.dodaj_fakture_koszt, name='dodaj_fakture_koszt'),
    path('sprzedaz/', views.faktury_sprzedaz, name='faktury_sprzedaz'),
    path('koszt/', views.faktury_koszt, name='faktury_koszt'),
    path('kontrahenci/<int:pk>/', views.szczegoly_kontrahenta, name='szczegoly_kontrahenta'),
    path('kontrahenci/edytuj/<int:pk>/', views.edytuj_kontrahenta, name='edytuj_kontrahenta'),
    path('kontrahenci/usun/<int:pk>/', views.usun_kontrahenta, name='usun_kontrahenta'),
    path('faktura/<int:pk>/', views.szczegoly_faktury, name='szczegoly_faktury'),
    path('faktura/edytuj/<int:pk>/', views.edytuj_fakture, name='edytuj_fakture'),
    path('faktura/<int:pk>/wyslij/', views.wyslij_fakture_mailem, name='wyslij_fakture'),
    path('zespoly/', views.lista_zespolow, name='lista_zespolow'),
    path('zespoly/<int:zespol_id>/', views.szczegoly_zespolu, name='szczegoly_zespolu'),
    path('zespoly/dodaj/', views.dodaj_zespol, name='dodaj_zespol'),
    path('zespoly/edytuj/<int:zespol_id>/', views.edytuj_zespol, name='edytuj_zespol'),
    path('zespoly/usun/<int:zespol_id>/', views.usun_zespol, name='usun_zespol'),
    path('zespoly/<int:zespol_id>/wyslij_wiadomosc/', views.wyslij_wiadomosc, name='wyslij_wiadomosc'),
    path('zespoly/<int:zespol_id>/dodaj_zadanie/', views.dodaj_zadanie, name='dodaj_zadanie'),
    path('zadania/edytuj/<int:zadanie_id>/', views.edytuj_zadanie, name='edytuj_zadanie'),
    path('zadania/usun/<int:zadanie_id>/', views.usun_zadanie, name='usun_zadanie'),
    path('zadania/oznacz/<int:zadanie_id>/', views.oznacz_zadanie_jako_wykonane, name='oznacz_zadanie'),
    path('uzytkownik/<int:pk>/', views.user_profile, name='user_profile'),
    path('twoje_sprawy/', views.twoje_sprawy, name='twoje_sprawy'),
    path('get_events/', views.get_events, name='get_events'),
    path('moje_zadania/', views.moje_zadania, name='moje_zadania'),
    path('zadania_uzytkownika/dodaj', views.dodaj_zadanie_uzytkownika, name='dodaj_zadanie_uzytkownika'),
    path('zadania_uzytkownika/edytuj/<int:pk>/', views.edytuj_zadanie_uzytkownika, name='edytuj_zadanie_uzytkownika'),
    path('zadania_uzytkownika/usun/<int:pk>/', views.usun_zadanie_uzytkownika, name='usun_zadanie_uzytkownika'),
    path('zadania_uzytkownika/oznacz/<int:pk>/', views.oznacz_zadanie_uzytkownika_wykonane, name='oznacz_zadanie_uzytkownika'),
    path('zadania_uzytkownika/<int:pk>/', views.szczegoly_zadania_uzytkownika, name='szczegoly_zadania_uzytkownika'),
    path('faktura/<int:pk>/przypomnij/', views.wyslij_przypomnienie, name='wyslij_przypomnienie'),
    path('dodaj_partnerstwo/', views.dodaj_partnerstwo, name='dodaj_partnerstwo'),
    path('partnerzy/', views.lista_partnerstw, name='lista_partnerstw'),
    path('usun_partnerstwo/<int:partnerstwo_id>/', views.usun_partnerstwo, name='usun_partnerstwo'),
    path('partnerzy/edytuj/<int:partnerstwo_id>/', views.edytuj_partnerstwo, name='edytuj_partnerstwo'),
    # Enhanced Authentication URLs
    path('register/', views.rejestracja, name='register'),
    path('enhanced-signup/', views.enhanced_registration, name='enhanced_signup'),
    path('profile/', views.enhanced_profile, name='user_profile'),
    path('profile/<int:pk>/', views.enhanced_profile, name='user_profile_detail'),
    
    # AJAX endpoints for authentication
    path('ajax/check-email/', views.check_email_availability, name='check_email_availability'),
    path('ajax/check-username/', views.check_username_availability, name='check_username_availability'),
    path('ajax/resend-confirmation/', views.resend_confirmation_email, name='resend_confirmation_email'),
    path('notifications/', include('faktury.notifications.urls', namespace='notifications')),
    path('export/kontrahenci/', views.export_kontrahenci, name='export_kontrahenci'),
    path('export/produkty/', views.export_produkty, name='export_produkty'),
    path('export/faktury/', views.export_faktury, name='export_faktury'),
    path('import/kontrahenci/', views.import_kontrahenci, name='import_kontrahenci'),
    path('import/produkty/', views.import_produkty, name='import_produkty'),
    path('import/faktury/', views.import_faktury, name='import_faktury'),
    path('faktura/<int:faktura_id>/cykl/', views.zarzadzaj_cyklem, name='zarzadzaj_cyklem'),
    path('proforma/', views.stworz_proforma, name='stworz_proforma'),
    path('stworz-proforma/', views.stworz_proforma, name='stworz_proforma'),
    path('korekta/<int:faktura_pk>/', views.stworz_korekte, name='stworz_korekte'),
    path('paragon/', views.stworz_paragon, name='stworz_paragon'),
    path('konwertuj/<int:pk>/', views.konwertuj_proforme_na_fakture, name='konwertuj_proforme'),
    path('generate-kp/<int:pk>/', views.generate_kp, name='generate-kp'),
    path('kp_list/', views.kp_list, name='kp_list'),
    path('kp/<int:pk>/', views.szczegoly_kp, name='szczegoly_kp'),
    path('check-payment-terms/', views.check_payment_terms, name='check-payment-terms'),
    path('api/faktury/', views.api_faktury_list, name='api_faktury_list'),
    path('api/faktury/<int:pk>/', views.api_faktura_detail, name='api_faktura_detail'),
    

    path('api/kontrahenci/', views.api_kontrahenci_list, name='api_kontrahenci_list'),
    path('api/kontrahenci/<int:pk>/', views.api_kontrahent_detail, name='api_kontrahent_detail'),
    path('api/produkty/', views.api_produkty_list, name='api_produkty_list'),
    path('api/produkty/<int:pk>/', views.api_produkt_detail, name='api_produkt_detail'),
    path('api/zadania/', views.api_zadania_list, name='api_zadania_list'),
    path('api/zadania/<int:pk>/', views.api_zadanie_detail, name='api_zadanie_detail'),
    
    # Error reporting APIs
    path('api/javascript-errors/', views_modules.error_api_views.javascript_errors, name='api_javascript_errors'),
    path('api/static-file-error/', views_modules.error_api_views.static_file_errors, name='api_static_file_errors'),
    path('api/performance-metrics/', views_modules.error_api_views.performance_metrics, name='api_performance_metrics'),
    path('api/health/network/', views_modules.error_api_views.network_status, name='api_network_status'),
    path('api/sync/offline-data/', views_modules.error_api_views.OfflineSyncView.as_view(), name='api_offline_sync'),
    path('api/sync/status/', views_modules.error_api_views.OfflineSyncView.as_view(), name='api_sync_status'),
    path('api/error-report/', views_modules.error_api_views.ErrorReportView.as_view(), name='api_error_report'),
    
    # Validation APIs
    path('api/validate-field/', views_modules.validation_api_views.validate_field, name='api_validate_field'),
    path('api/validate-form/', views_modules.validation_api_views.FormValidationView.as_view(), name='api_validate_form'),
    path('api/validation-rules/', views_modules.validation_api_views.validation_rules, name='api_validation_rules'),
    path('api/validate-business-number/', views_modules.validation_api_views.validate_business_number, name='api_validate_business_number'),
    path('wiadomosci/', views.lista_wiadomosci, name='lista_wiadomosci'),
    path('wiadomosci/wyslij/', views.wyslij_wiadomosc, name='wyslij_wiadomosc'),
    path('wiadomosci/systemowa/', views.wyslij_systemowa, name='wyslij_systemowa'),
    path('wiadomosci/<int:pk>/', views.szczegoly_wiadomosci, name='szczegoly_wiadomosci'),
    path('wiadomosci/odp/<int:pk>/', views.odp_wiadomosc, name='odp_wiadomosc'),
    path('dodaj/produkt/ajax/', views.dodaj_produkt_ajax, name='dodaj_produkt_ajax'),
    path('pobierz_dane_produktu/', views.pobierz_dane_produktu, name='pobierz_dane_produktu'),
    path('faktura/<int:pk>/generuj_kp/', views.generate_kp, name='generate_kp'),
    path('zadania/usun/<int:zadanie_id>/', views.usun_zadanie, name='usun_zadanie'),
    path('czlonek_zespolu/<int:czlonek_id>/', views.szczegoly_czlonka_zespolu, name='szczegoly_czlonka_zespolu'),

    # Enhanced invoice system URLs
    path('enhanced/', include('faktury.enhanced_urls')),
    
    # OCR URLs - Document processing and status tracking
    path('ocr/', include([
        # Main OCR views (HTML responses)
        path('upload/', views_modules.ocr_views.ocr_upload_view, name='ocr_upload'),
        path('upload/progress/<str:upload_id>/', views_modules.ocr_views.ocr_upload_progress_view, name='ocr_upload_progress'),
        path('status/<int:document_id>/', views_modules.ocr_views.ocr_status_view, name='ocr_status'),
        path('results/', views_modules.ocr_views.ocr_results_list, name='ocr_results_list'),
        path('result/<int:result_id>/', views_modules.ocr_views.ocr_result_detail, name='ocr_result_detail'),
        path('create-invoice/<int:result_id>/', views_modules.ocr_views.create_invoice_from_ocr, name='create_invoice_from_ocr'),
        path('test-csrf/', views_modules.ocr_views.test_csrf_view, name='test_csrf'),
        path('get-csrf-token/', views_modules.ocr_views.get_csrf_token, name='get_csrf_token'),
        
        # AJAX Status endpoints for real-time updates (JSON responses)
        # Authentication: @login_required, Parameter validation: <int:document_id>
        path('ajax/status/<int:document_id>/', ocr_status_views.get_status_ajax, name='ocr_ajax_status'),
        path('ajax/status/<int:document_id>/display/', ocr_status_views.get_status_display_ajax, name='ocr_ajax_status_display'),
        path('ajax/status/<int:document_id>/progress/', ocr_status_views.get_progress_ajax, name='ocr_ajax_progress'),
        
        # REST API endpoints (JSON responses with DRF authentication)
        # Authentication: @api_view + @permission_classes([IsAuthenticated])
        path('api/validate-upload/', views_modules.ocr_views.api_validate_upload, name='ocr_api_validate_upload'),
        path('api/upload/', views_modules.ocr_views.api_upload_document, name='ocr_api_upload'),
        path('api/progress/<str:upload_id>/', views_modules.ocr_views.api_upload_progress, name='ocr_api_upload_progress'),
        path('api/cancel/<str:upload_id>/', views_modules.ocr_views.api_cancel_upload, name='ocr_api_cancel_upload'),
        path('api/retry/<str:upload_id>/', views_modules.ocr_views.api_retry_upload, name='ocr_api_retry_upload'),
        path('api/queue/status/', views_modules.ocr_views.api_queue_status, name='ocr_api_queue_status'),
        path('api/feedback/<int:result_id>/', views_modules.ocr_views.api_ocr_feedback, name='ocr_api_feedback'),
        path('api/confidence/<int:result_id>/', views_modules.ocr_views.api_confidence_explanation, name='ocr_api_confidence'),
        path('api/suggestions/<int:result_id>/', views_modules.ocr_views.api_improvement_suggestions, name='ocr_api_suggestions'),
        path('api/correction/<int:result_id>/', views_modules.ocr_views.api_correction_interface, name='ocr_api_correction'),
        path('api/correction/<int:result_id>/apply/', views_modules.ocr_views.api_apply_corrections, name='ocr_api_apply_corrections'),
        path('api/documents/<int:document_id>/retry/', views_modules.ocr_views.api_retry_processing, name='ocr_api_retry_processing'),
        path('api/documents/<int:document_id>/status/', views_modules.ocr_views.api_processing_status, name='ocr_api_status'),
        path('api/documents/<int:document_id>/status/unified/', ocr_status_views.api_get_status, name='ocr_api_status_unified'),
        path('api/documents/status/bulk/', ocr_status_views.api_bulk_status, name='ocr_api_bulk_status'),
        path('api/statistics/', views_modules.ocr_views.api_ocr_statistics, name='ocr_api_statistics'),
    ])),
    
    # REST API endpoints are included in main project URLs (faktulove/urls.py)
    
    # Admin Dashboard API endpoints
    path('admin/dashboard/stats/', DashboardStatsView.as_view(), name='admin_dashboard_stats'),
    path('admin/dashboard/health/', SystemHealthView.as_view(), name='admin_system_health'),
    path('admin/dashboard/recent-activity/', RecentActivityView.as_view(), name='admin_recent_activity'),
    
    # Company Management URLs
    path('companies/', include('faktury.urls_company')),
    
    # Advanced Search URLs
    path('search/', views.advanced_search_view, name='advanced_search'),
    path('search/quick/', search_api_views.QuickSearchView.as_view(), name='quick_search'),
    
    # Search API endpoints
    path('api/search/invoices/', search_api_views.search_invoices_api, name='api_search_invoices'),
    path('api/search/companies/', search_api_views.search_companies_api, name='api_search_companies'),
    path('api/search/suggestions/', search_api_views.search_suggestions_api, name='api_search_suggestions'),
    path('api/search/filter-options/', search_api_views.filter_options_api, name='api_filter_options'),
    path('api/search/history/', search_api_views.search_history_api, name='api_search_history'),
    path('api/search/save/', search_api_views.save_search_api, name='api_save_search'),
    path('api/search/saved/', search_api_views.saved_searches_api, name='api_saved_searches'),
    path('api/search/saved/<str:search_name>/', search_api_views.delete_saved_search_api, name='api_delete_saved_search'),
    path('api/search/stats/', search_api_views.search_stats_api, name='api_search_stats'),
    
    # Data Export and Import URLs
    path('data-management/', views.data_management_view, name='data_management'),
    
    # Export API endpoints
    path('api/export/invoices/', data_export_import_views.export_invoices_api, name='api_export_invoices'),
    path('api/export/companies/', data_export_import_views.export_companies_api, name='api_export_companies'),
    path('api/export/products/', data_export_import_views.export_products_api, name='api_export_products'),
    path('api/export/templates/', data_export_import_views.export_templates_api, name='api_export_templates'),
    path('api/export/statistics/', data_export_import_views.export_statistics_api, name='api_export_statistics'),
    path('api/export/progress/<str:progress_id>/', data_export_import_views.export_progress_api, name='api_export_progress'),
    
    # Import API endpoints
    path('api/import/data/', data_export_import_views.import_data_api, name='api_import_data'),
    
    # Backup and Restore API endpoints
    path('api/create/backup/', data_export_import_views.create_backup_api, name='api_create_backup'),
    path('api/restore/backup/', data_export_import_views.restore_backup_api, name='api_restore_backup'),
    
    # Bulk Operations
    path('api/bulk-operations/', data_export_import_views.BulkOperationsView.as_view(), name='api_bulk_operations'),
    
    # Health Monitoring URLs (Admin only)
    path('admin/health/', include([
        path('dashboard/', views_modules.health_monitoring_views.SystemHealthDashboardView.as_view(), name='admin_health_dashboard'),
        path('api/history/', views_modules.health_monitoring_views.health_history_api, name='admin_health_history_api'),
        path('api/trigger/', views_modules.health_monitoring_views.trigger_health_check, name='admin_trigger_health_check'),
        path('api/component/<str:component_name>/', views_modules.health_monitoring_views.component_details_api, name='admin_component_details'),
        path('api/test-alerts/', views_modules.health_monitoring_views.test_alerting_system, name='admin_test_alerts'),
        path('api/metrics/', views_modules.health_monitoring_views.system_metrics_api, name='admin_system_metrics'),
    ])),
]
