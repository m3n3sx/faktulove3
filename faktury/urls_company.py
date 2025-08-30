"""
URL patterns for company management
"""
from django.urls import path
from .views_modules import company_management_views

urlpatterns = [
    # Company Dashboard
    path('dashboard/', company_management_views.company_dashboard, name='company_dashboard'),
    path('switch-context/', company_management_views.switch_company_context, name='switch_company_context'),
    
    # Company Management
    path('list/', company_management_views.company_list, name='company_list'),
    path('<int:company_id>/', company_management_views.company_detail, name='company_detail'),
    path('<int:company_id>/edit/', company_management_views.edit_company, name='edit_company'),
    path('create-test/', company_management_views.create_test_companies, name='create_test_companies'),
    
    # Partnership Management
    path('partnerships/', company_management_views.partnership_management, name='partnership_management'),
    path('partnerships/create/', company_management_views.create_partnership, name='create_partnership'),
    path('partnerships/<int:partnership_id>/', company_management_views.partnership_detail, name='partnership_detail'),
    path('partnerships/invite/', company_management_views.invite_partnership, name='invite_partnership'),
    
    # API Endpoints
    path('api/<int:company_id>/statistics/', company_management_views.company_statistics_api, name='company_statistics_api'),
    path('api/partnerships/<int:partnership_id>/analytics/', company_management_views.partnership_analytics_api, name='partnership_analytics_api'),
]