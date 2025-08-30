"""
URL patterns for enhanced invoice management with design system components
"""
from django.urls import path
from . import enhanced_invoice_views

app_name = 'enhanced_invoices'

urlpatterns = [
    # Enhanced invoice management
    path('enhanced/', enhanced_invoice_views.enhanced_invoice_list, name='enhanced_invoice_list'),
    path('enhanced/create/', enhanced_invoice_views.enhanced_invoice_create, name='enhanced_invoice_create'),
    path('enhanced/<int:pk>/', enhanced_invoice_views.enhanced_invoice_detail, name='enhanced_invoice_detail'),
    path('enhanced/<int:pk>/edit/', enhanced_invoice_views.enhanced_invoice_edit, name='enhanced_invoice_edit'),
    path('enhanced/<int:pk>/status/', enhanced_invoice_views.enhanced_invoice_status_update, name='enhanced_invoice_status_update'),
    
    # Enhanced contractor management
    path('enhanced/contractors/create/', enhanced_invoice_views.enhanced_contractor_create, name='enhanced_contractor_create'),
]