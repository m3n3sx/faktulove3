"""
Super Admin URLs
Comprehensive admin interface URLs
"""
from django.urls import path
from faktury.views_modules import superadmin_views

app_name = 'superadmin'

urlpatterns = [
    # Main dashboard
    path('', superadmin_views.superadmin_dashboard, name='dashboard'),
    
    # User management
    path('users/', superadmin_views.user_management, name='user_management'),
    path('users/<int:user_id>/', superadmin_views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', superadmin_views.user_toggle_status, name='user_toggle_status'),
    path('users/<int:user_id>/reset-password/', superadmin_views.user_reset_password, name='user_reset_password'),
    path('users/mass-actions/', superadmin_views.mass_actions, name='mass_actions'),
    
    # Company management
    path('companies/', superadmin_views.company_management, name='company_management'),
    
    # System management
    path('settings/', superadmin_views.system_settings, name='system_settings'),
    path('logs/', superadmin_views.system_logs, name='system_logs'),
    
    # API endpoints
    path('api/gus-test/', superadmin_views.gus_test_api, name='gus_test_api'),
    path('api/export/', superadmin_views.export_data, name='export_data'),
]
