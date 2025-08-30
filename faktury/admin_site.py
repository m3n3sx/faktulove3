"""
Custom Django admin site with design system integration
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import staff_member_required
from django.utils.decorators import method_decorator


class DesignSystemAdminSite(AdminSite):
    """Custom admin site with design system integration"""
    
    site_title = _('FaktuLove Administration')
    site_header = _('FaktuLove')
    index_title = _('Panel administracyjny')
    
    def __init__(self, name='admin'):
        super().__init__(name)
        self.enable_nav_sidebar = True
    
    def get_urls(self):
        """Add custom URLs for design system features"""
        urls = super().get_urls()
        custom_urls = [
            path('design-system-demo/', 
                 self.admin_view(self.design_system_demo_view), 
                 name='design_system_demo'),
            path('polish-business-tools/', 
                 self.admin_view(self.polish_business_tools_view), 
                 name='polish_business_tools'),
        ]
        return custom_urls + urls
    
    def design_system_demo_view(self, request):
        """Demo view showing design system components"""
        context = {
            **self.each_context(request),
            'title': 'Design System Demo',
            'demo_components': [
                {
                    'name': 'Buttons',
                    'description': 'Various button styles and states',
                    'examples': [
                        {'type': 'primary', 'text': 'Primary Button'},
                        {'type': 'secondary', 'text': 'Secondary Button'},
                        {'type': 'danger', 'text': 'Danger Button'},
                    ]
                },
                {
                    'name': 'Form Fields',
                    'description': 'Polish business form components',
                    'examples': [
                        {'type': 'nip', 'label': 'NIP Field'},
                        {'type': 'currency', 'label': 'Currency Field'},
                        {'type': 'vat', 'label': 'VAT Rate Field'},
                        {'type': 'date', 'label': 'Polish Date Field'},
                    ]
                },
                {
                    'name': 'Status Badges',
                    'description': 'Invoice status indicators',
                    'examples': [
                        {'status': 'draft', 'text': 'Szkic'},
                        {'status': 'sent', 'text': 'Wysłana'},
                        {'status': 'paid', 'text': 'Opłacona'},
                        {'status': 'overdue', 'text': 'Przeterminowana'},
                        {'status': 'cancelled', 'text': 'Anulowana'},
                    ]
                }
            ]
        }
        
        return TemplateResponse(request, 'admin/design_system_demo.html', context)
    
    def polish_business_tools_view(self, request):
        """Tools for Polish business operations"""
        context = {
            **self.each_context(request),
            'title': 'Narzędzia biznesowe',
            'tools': [
                {
                    'name': 'Walidator NIP',
                    'description': 'Sprawdź poprawność numeru NIP',
                    'url': '#nip-validator'
                },
                {
                    'name': 'Kalkulator VAT',
                    'description': 'Oblicz kwoty VAT dla różnych stawek',
                    'url': '#vat-calculator'
                },
                {
                    'name': 'Formatowanie dat',
                    'description': 'Konwertuj daty do polskiego formatu',
                    'url': '#date-formatter'
                },
                {
                    'name': 'Formatowanie walut',
                    'description': 'Formatuj kwoty w polskich złotych',
                    'url': '#currency-formatter'
                }
            ]
        }
        
        return TemplateResponse(request, 'admin/polish_business_tools.html', context)
    
    def index(self, request, extra_context=None):
        """Enhanced admin index with design system integration"""
        context = {
            'design_system_enabled': True,
            'polish_business_context': True,
            'quick_actions': [
                {
                    'name': 'Dodaj fakturę',
                    'url': '/admin/faktury/faktura/add/',
                    'icon': '📄',
                    'description': 'Utwórz nową fakturę'
                },
                {
                    'name': 'Dodaj kontrahenta',
                    'url': '/admin/faktury/kontrahent/add/',
                    'icon': '🏢',
                    'description': 'Dodaj nowego kontrahenta'
                },
                {
                    'name': 'Przetwarzanie OCR',
                    'url': '/admin/faktury/documentupload/',
                    'icon': '🔍',
                    'description': 'Zarządzaj dokumentami OCR'
                },
                {
                    'name': 'Design System Demo',
                    'url': '/admin/design-system-demo/',
                    'icon': '🎨',
                    'description': 'Zobacz komponenty design system'
                }
            ]
        }
        
        if extra_context:
            context.update(extra_context)
        
        return super().index(request, context)


# Create custom admin site instance
design_system_admin_site = DesignSystemAdminSite(name='design_system_admin')

# Register all models with the custom admin site
from .admin import *
from .models import *

# Re-register models with custom admin site
design_system_admin_site.register(Faktura, FakturaAdmin)
design_system_admin_site.register(Kontrahent, KontrahentAdmin)
design_system_admin_site.register(Firma, FirmaAdmin)
design_system_admin_site.register(Produkt, ProduktAdmin)
design_system_admin_site.register(PozycjaFaktury, PozycjaFakturyAdmin)
design_system_admin_site.register(UserProfile, UserProfileAdmin)
design_system_admin_site.register(Partnerstwo, PartnerstwoAdmin)
design_system_admin_site.register(DocumentUpload, DocumentUploadAdmin)
design_system_admin_site.register(OCRResult, OCRResultAdmin)
design_system_admin_site.register(OCRValidation, OCRValidationAdmin)
design_system_admin_site.register(OCRProcessingLog, OCRProcessingLogAdmin)
design_system_admin_site.register(OCREngine, OCREngineAdmin)
design_system_admin_site.register(OCRProcessingStep, OCRProcessingStepAdmin)