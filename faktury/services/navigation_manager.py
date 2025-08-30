"""
Navigation Manager Service
Handles application navigation validation and fixes broken routes
"""
from django.urls import reverse, NoReverseMatch
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class NavigationManager:
    """Manages application navigation and routing"""
    
    # Define all expected routes and their status
    EXPECTED_ROUTES = {
        'panel_uzytkownika': {'required': True, 'description': 'Main dashboard'},
        'kontrahenci': {'required': True, 'description': 'Contractors list'},
        'produkty': {'required': True, 'description': 'Products list'},
        'ocr_upload': {'required': True, 'description': 'OCR upload page'},
        'company': {'required': True, 'description': 'Company dashboard'},
        'company_html': {'required': True, 'description': 'Company page (HTML)'},
        'view_profile': {'required': True, 'description': 'User profile'},
        'view_profile_html': {'required': True, 'description': 'User profile (HTML)'},
        'email_html': {'required': True, 'description': 'Email inbox'},
        'email_inbox': {'required': True, 'description': 'Email inbox'},
        'notifications_list': {'required': True, 'description': 'Notifications list'},
        'twoje_sprawy': {'required': True, 'description': 'Your matters'},
        'lista_zespolow': {'required': True, 'description': 'Teams list'},
        'lista_partnerstw': {'required': True, 'description': 'Partners list'},
    }
    
    def validate_routes(self) -> List[str]:
        """Validate all application routes and return list of broken ones"""
        broken_routes = []
        
        for route_name, route_info in self.EXPECTED_ROUTES.items():
            try:
                reverse(route_name)
                logger.info(f"Route '{route_name}' is valid")
            except NoReverseMatch:
                if route_info['required']:
                    broken_routes.append(route_name)
                    logger.warning(f"Required route '{route_name}' is broken: {route_info['description']}")
                else:
                    logger.info(f"Optional route '{route_name}' is missing: {route_info['description']}")
        
        return broken_routes
    
    def fix_broken_links(self) -> Dict[str, str]:
        """Fix broken navigation links by providing fallbacks"""
        fixes = {}
        broken_routes = self.validate_routes()
        
        for route in broken_routes:
            if route in ['company', 'company_html']:
                fixes[route] = 'panel_uzytkownika'  # Redirect to main dashboard
            elif route in ['email_html', 'email_inbox']:
                fixes[route] = 'notifications_list'  # Redirect to notifications
            elif route in ['view_profile', 'view_profile_html']:
                fixes[route] = 'user_profile'  # Use existing profile view
            else:
                fixes[route] = 'panel_uzytkownika'  # Default fallback
        
        return fixes
    
    def create_breadcrumbs(self, current_path: str) -> List[Dict]:
        """Generate breadcrumb navigation based on current path"""
        breadcrumbs = [{'name': 'Dashboard', 'url': reverse('panel_uzytkownika')}]
        
        # Define breadcrumb mappings
        breadcrumb_map = {
            'kontrahenci': {'name': 'Kontrahenci', 'parent': None},
            'produkty': {'name': 'Produkty', 'parent': None},
            'ocr_upload': {'name': 'OCR Upload', 'parent': None},
            'company': {'name': 'Firma', 'parent': None},
            'view_profile': {'name': 'Profil', 'parent': None},
            'notifications_list': {'name': 'Powiadomienia', 'parent': None},
            'twoje_sprawy': {'name': 'Twoje sprawy', 'parent': None},
            'lista_zespolow': {'name': 'Zespoły', 'parent': None},
            'lista_partnerstw': {'name': 'Partnerzy', 'parent': None},
        }
        
        # Extract route name from path
        for route_name, breadcrumb_info in breadcrumb_map.items():
            try:
                route_url = reverse(route_name)
                if current_path.startswith(route_url):
                    breadcrumbs.append({
                        'name': breadcrumb_info['name'],
                        'url': route_url,
                        'active': True
                    })
                    break
            except NoReverseMatch:
                continue
        
        return breadcrumbs
    
    def get_navigation_status(self) -> Dict:
        """Get comprehensive navigation status report"""
        broken_routes = self.validate_routes()
        fixes = self.fix_broken_links()
        
        return {
            'total_routes': len(self.EXPECTED_ROUTES),
            'broken_routes': len(broken_routes),
            'broken_route_names': broken_routes,
            'fixes_available': fixes,
            'status': 'healthy' if not broken_routes else 'needs_attention'
        }


class MissingPageHandler:
    """Handles creation and routing of missing pages"""
    
    @staticmethod
    @login_required
    def create_company_page(request):
        """Create functional company management page"""
        try:
            from faktury.models import Firma
            firma = Firma.objects.get(user=request.user)
        except Firma.DoesNotExist:
            return redirect('dodaj_firme')
        
        context = {
            'firma': firma,
            'page_title': 'Zarządzanie firmą',
            'breadcrumbs': NavigationManager().create_breadcrumbs(request.path)
        }
        return render(request, 'faktury/company_dashboard.html', context)
    
    @staticmethod
    @login_required
    def create_profile_page(request):
        """Create user profile management page"""
        context = {
            'user': request.user,
            'page_title': 'Profil użytkownika',
            'breadcrumbs': NavigationManager().create_breadcrumbs(request.path)
        }
        return render(request, 'faktury/view_profile.html', context)
    
    @staticmethod
    @login_required
    def create_email_page(request):
        """Create email settings page"""
        context = {
            'page_title': 'Skrzynka e-mail',
            'breadcrumbs': NavigationManager().create_breadcrumbs(request.path),
            'messages': []  # Placeholder for email messages
        }
        return render(request, 'faktury/email_inbox.html', context)
    
    @staticmethod
    @login_required
    def create_notifications_page(request):
        """Create notifications management page"""
        try:
            from faktury.models import Notification
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
        except:
            notifications = []
        
        context = {
            'notifications': notifications,
            'page_title': 'Powiadomienia',
            'breadcrumbs': NavigationManager().create_breadcrumbs(request.path)
        }
        return render(request, 'faktury/notifications_list.html', context)
    
    @staticmethod
    def create_404_fallback(request, exception=None):
        """Create graceful 404 fallback page"""
        nav_manager = NavigationManager()
        fixes = nav_manager.fix_broken_links()
        
        context = {
            'page_title': 'Strona nie została znaleziona',
            'error_message': 'Przepraszamy, strona której szukasz nie istnieje.',
            'suggested_links': [
                {'name': 'Dashboard', 'url': reverse('panel_uzytkownika')},
                {'name': 'Kontrahenci', 'url': reverse('kontrahenci')},
                {'name': 'Produkty', 'url': reverse('produkty')},
            ],
            'fixes_available': fixes
        }
        return render(request, 'faktury/404_fallback.html', context, status=404)


# Utility functions for template usage
def get_navigation_context(request):
    """Get navigation context for templates"""
    nav_manager = NavigationManager()
    return {
        'navigation_status': nav_manager.get_navigation_status(),
        'breadcrumbs': nav_manager.create_breadcrumbs(request.path),
        'current_user': request.user if request.user.is_authenticated else None
    }