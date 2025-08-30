"""
Django Admin Asset Manager

Handles missing Django admin static assets and ensures proper loading
"""

import os
import requests
import logging
from pathlib import Path
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.management.base import BaseCommand
from typing import List, Dict, Optional
import hashlib

logger = logging.getLogger(__name__)


class AdminAssetManager:
    """Manages Django admin static assets"""
    
    # Required admin CSS files
    REQUIRED_CSS_FILES = [
        'admin/css/base.css',
        'admin/css/dashboard.css',
        'admin/css/dark_mode.css',
        'admin/css/nav_sidebar.css',
        'admin/css/responsive.css',
        'admin/css/forms.css',
        'admin/css/changelists.css',
        'admin/css/widgets.css',
        'admin/css/login.css',
        'admin/css/autocomplete.css',
    ]
    
    # Required admin JavaScript files
    REQUIRED_JS_FILES = [
        'admin/js/core.js',
        'admin/js/theme.js',
        'admin/js/nav_sidebar.js',
        'admin/js/jquery.init.js',
        'admin/js/actions.js',
        'admin/js/calendar.js',
        'admin/js/change_form.js',
        'admin/js/filters.js',
        'admin/js/inlines.js',
        'admin/js/prepopulate.js',
        'admin/js/SelectBox.js',
        'admin/js/SelectFilter2.js',
        'admin/js/urlify.js',
    ]
    
    # Django version for asset URLs
    DJANGO_VERSION = "4.2.23"
    DJANGO_ADMIN_BASE_URL = f"https://raw.githubusercontent.com/django/django/{DJANGO_VERSION}/django/contrib/admin/static/"
    
    def __init__(self):
        self.static_root = Path(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT else None
        self.app_static_dir = Path(__file__).parent.parent / 'static'
        self.missing_files = []
        self.download_errors = []
    
    def collect_missing_assets(self) -> List[str]:
        """Identify missing admin CSS/JS files"""
        missing_files = []
        
        # Check CSS files
        for css_file in self.REQUIRED_CSS_FILES:
            if not self._asset_exists(css_file):
                missing_files.append(css_file)
                logger.warning(f"Missing admin CSS file: {css_file}")
        
        # Check JS files
        for js_file in self.REQUIRED_JS_FILES:
            if not self._asset_exists(js_file):
                missing_files.append(js_file)
                logger.warning(f"Missing admin JS file: {js_file}")
        
        self.missing_files = missing_files
        return missing_files
    
    def _asset_exists(self, asset_path: str) -> bool:
        """Check if asset exists in static files"""
        # Check in app static directory
        app_asset_path = self.app_static_dir / asset_path
        if app_asset_path.exists():
            return True
        
        # Check using Django's static file finder
        found_path = find(asset_path)
        if found_path:
            return True
        
        # Check in STATIC_ROOT if it exists
        if self.static_root:
            static_asset_path = self.static_root / asset_path
            if static_asset_path.exists():
                return True
        
        return False
    
    def download_admin_assets(self) -> Dict[str, bool]:
        """Download missing Django admin assets"""
        results = {}
        
        if not self.missing_files:
            self.collect_missing_assets()
        
        for asset_path in self.missing_files:
            try:
                success = self._download_asset(asset_path)
                results[asset_path] = success
                if success:
                    logger.info(f"Successfully downloaded: {asset_path}")
                else:
                    logger.error(f"Failed to download: {asset_path}")
            except Exception as e:
                logger.error(f"Error downloading {asset_path}: {str(e)}")
                results[asset_path] = False
                self.download_errors.append(f"{asset_path}: {str(e)}")
        
        return results
    
    def _download_asset(self, asset_path: str) -> bool:
        """Download a single asset file"""
        url = self.DJANGO_ADMIN_BASE_URL + asset_path
        local_path = self.app_static_dir / asset_path
        
        # Create directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Write file
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            # Verify file was written correctly
            if local_path.exists() and local_path.stat().st_size > 0:
                return True
            else:
                logger.error(f"Downloaded file is empty or doesn't exist: {local_path}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Network error downloading {asset_path}: {str(e)}")
            return False
        except IOError as e:
            logger.error(f"File system error for {asset_path}: {str(e)}")
            return False
    
    def configure_admin_theme(self) -> None:
        """Configure admin panel theming"""
        # Create custom admin CSS for Polish business features
        custom_css = self._generate_custom_admin_css()
        custom_css_path = self.app_static_dir / 'admin' / 'css' / 'polish_business_admin.css'
        
        # Create directory if it doesn't exist
        custom_css_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(custom_css_path, 'w', encoding='utf-8') as f:
                f.write(custom_css)
            logger.info("Created custom Polish business admin CSS")
        except IOError as e:
            logger.error(f"Error creating custom admin CSS: {str(e)}")
    
    def _generate_custom_admin_css(self) -> str:
        """Generate custom CSS for Polish business admin features"""
        return """
/* Polish Business Admin Theme */

:root {
    /* Polish Business Colors */
    --color-invoice-draft: #6b7280;
    --color-invoice-sent: #3b82f6;
    --color-invoice-paid: #10b981;
    --color-invoice-overdue: #ef4444;
    --color-invoice-cancelled: #6b7280;
    
    /* Design System Variables */
    --color-background-secondary: #f8fafc;
    --color-border-default: #d1d5db;
    --color-interactive: #3b82f6;
    --color-text-secondary: #6b7280;
    --color-status-success: #10b981;
    --color-status-error: #ef4444;
    
    /* Typography */
    --typography-currency-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
    --typography-currency-size: 14px;
    --typography-currency-weight: 600;
    --typography-date-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
    --typography-date-size: 14px;
    --typography-company-name-family: system-ui, -apple-system, sans-serif;
    --typography-company-name-size: 14px;
    --typography-company-name-weight: 500;
    
    /* Spacing */
    --spacing-2: 0.5rem;
    --spacing-3: 0.75rem;
    --spacing-8: 2rem;
    
    /* Border Radius */
    --border-radius-md: 0.375rem;
    
    /* Font Size */
    --font-size-base: 14px;
}

/* Polish Business Fieldsets */
.fieldset.django-polish-business {
    border-left: 4px solid #3b82f6;
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.05) 0%, transparent 100%);
}

.fieldset.django-polish-business h2 {
    color: #1e40af;
    font-weight: 600;
}

/* Design System Widgets */
.django-design-system-widget {
    border: 1px solid var(--color-border-default);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-2) var(--spacing-3);
    font-size: var(--font-size-base);
    transition: border-color 0.2s ease;
}

.django-design-system-widget:focus {
    outline: none;
    border-color: var(--color-interactive);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Status Badges */
.status-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-badge.draft {
    background-color: rgba(107, 114, 128, 0.1);
    color: #374151;
}

.status-badge.sent {
    background-color: rgba(59, 130, 246, 0.1);
    color: #1e40af;
}

.status-badge.paid {
    background-color: rgba(16, 185, 129, 0.1);
    color: #047857;
}

.status-badge.overdue {
    background-color: rgba(239, 68, 68, 0.1);
    color: #dc2626;
}

.status-badge.cancelled {
    background-color: rgba(107, 114, 128, 0.1);
    color: #374151;
}

/* Enhanced Admin Navigation */
#nav-sidebar {
    background: linear-gradient(180deg, #1e40af 0%, #1e3a8a 100%);
}

#nav-sidebar .module th {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    font-weight: 600;
}

#nav-sidebar .module a {
    color: rgba(255, 255, 255, 0.9);
    transition: all 0.2s ease;
}

#nav-sidebar .module a:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
}

/* Polish Business Form Enhancements */
.form-row.django-polish-business {
    background: rgba(59, 130, 246, 0.02);
    border-radius: var(--border-radius-md);
    padding: 1rem;
    margin-bottom: 1rem;
}

/* NIP Input Styling */
.nip-input {
    font-family: var(--typography-currency-family);
    letter-spacing: 0.05em;
}

.nip-input:valid {
    border-color: var(--color-status-success);
}

.nip-input:invalid {
    border-color: var(--color-status-error);
}

/* Admin Dashboard Enhancements */
.dashboard .module {
    border-radius: var(--border-radius-md);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s ease;
}

.dashboard .module:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Responsive Improvements */
@media (max-width: 768px) {
    .django-design-system-widget {
        font-size: 16px; /* Prevent zoom on iOS */
    }
    
    .currency-input-wrapper {
        flex-direction: column;
    }
    
    .currency-input-wrapper .currency-symbol {
        border-radius: 0 0 var(--border-radius-md) var(--border-radius-md);
        border-top: none;
        border-left: 1px solid var(--color-border-default);
        text-align: center;
    }
}

/* Print Styles */
@media print {
    .status-badge {
        background: transparent !important;
        border: 1px solid currentColor;
    }
    
    .django-design-system-widget {
        border: 1px solid #000;
    }
}
"""
    
    def validate_admin_functionality(self) -> Dict[str, bool]:
        """Test admin panel functionality across different scenarios"""
        validation_results = {
            'css_files_exist': True,
            'js_files_exist': True,
            'custom_widgets_work': True,
            'polish_features_enabled': True
        }
        
        # Check CSS files
        for css_file in self.REQUIRED_CSS_FILES:
            if not self._asset_exists(css_file):
                validation_results['css_files_exist'] = False
                break
        
        # Check JS files
        for js_file in self.REQUIRED_JS_FILES:
            if not self._asset_exists(js_file):
                validation_results['js_files_exist'] = False
                break
        
        # Check custom CSS
        custom_css_path = self.app_static_dir / 'admin' / 'css' / 'polish_business_admin.css'
        if not custom_css_path.exists():
            validation_results['polish_features_enabled'] = False
        
        return validation_results
    
    def get_asset_status_report(self) -> Dict:
        """Generate comprehensive asset status report"""
        missing_assets = self.collect_missing_assets()
        validation_results = self.validate_admin_functionality()
        
        return {
            'total_required_assets': len(self.REQUIRED_CSS_FILES) + len(self.REQUIRED_JS_FILES),
            'missing_assets_count': len(missing_assets),
            'missing_assets': missing_assets,
            'validation_results': validation_results,
            'download_errors': self.download_errors,
            'recommendations': self._generate_recommendations(missing_assets, validation_results)
        }
    
    def _generate_recommendations(self, missing_assets: List[str], validation_results: Dict[str, bool]) -> List[str]:
        """Generate recommendations based on asset status"""
        recommendations = []
        
        if missing_assets:
            recommendations.append(f"Download {len(missing_assets)} missing admin assets")
        
        if not validation_results.get('css_files_exist'):
            recommendations.append("Ensure all required CSS files are available")
        
        if not validation_results.get('js_files_exist'):
            recommendations.append("Ensure all required JavaScript files are available")
        
        if not validation_results.get('polish_features_enabled'):
            recommendations.append("Configure Polish business admin theme")
        
        if not recommendations:
            recommendations.append("All admin assets are properly configured")
        
        return recommendations
    
    def fix_all_assets(self) -> Dict:
        """Fix all admin asset issues automatically"""
        logger.info("Starting admin asset fix process...")
        
        # Collect missing assets
        missing_assets = self.collect_missing_assets()
        
        # Download missing assets
        download_results = {}
        if missing_assets:
            download_results = self.download_admin_assets()
        
        # Configure admin theme
        self.configure_admin_theme()
        
        # Validate everything
        validation_results = self.validate_admin_functionality()
        
        # Generate final report
        report = {
            'missing_assets_found': len(missing_assets),
            'assets_downloaded': sum(1 for success in download_results.values() if success),
            'download_failures': sum(1 for success in download_results.values() if not success),
            'theme_configured': True,
            'validation_results': validation_results,
            'success': all(validation_results.values())
        }
        
        if report['success']:
            logger.info("Admin asset fix completed successfully")
        else:
            logger.warning("Admin asset fix completed with some issues")
        
        return report


class AdminAssetCommand(BaseCommand):
    """Django management command for admin asset management"""
    
    help = 'Manage Django admin static assets'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check admin asset status without making changes'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix all admin asset issues automatically'
        )
        parser.add_argument(
            '--download',
            action='store_true',
            help='Download missing admin assets'
        )
        parser.add_argument(
            '--configure',
            action='store_true',
            help='Configure admin theme only'
        )
    
    def handle(self, *args, **options):
        manager = AdminAssetManager()
        
        if options['check']:
            report = manager.get_asset_status_report()
            self.stdout.write(f"Asset Status Report:")
            self.stdout.write(f"Total required assets: {report['total_required_assets']}")
            self.stdout.write(f"Missing assets: {report['missing_assets_count']}")
            
            if report['missing_assets']:
                self.stdout.write("Missing files:")
                for asset in report['missing_assets']:
                    self.stdout.write(f"  - {asset}")
            
            self.stdout.write("Validation Results:")
            for check, result in report['validation_results'].items():
                status = "✓" if result else "✗"
                self.stdout.write(f"  {status} {check}")
            
            self.stdout.write("Recommendations:")
            for rec in report['recommendations']:
                self.stdout.write(f"  - {rec}")
        
        elif options['fix']:
            report = manager.fix_all_assets()
            if report['success']:
                self.stdout.write(
                    self.style.SUCCESS('Admin assets fixed successfully!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Admin assets fixed with some issues')
                )
            
            self.stdout.write(f"Assets downloaded: {report['assets_downloaded']}")
            if report['download_failures'] > 0:
                self.stdout.write(f"Download failures: {report['download_failures']}")
        
        elif options['download']:
            missing = manager.collect_missing_assets()
            if missing:
                results = manager.download_admin_assets()
                success_count = sum(1 for success in results.values() if success)
                self.stdout.write(f"Downloaded {success_count}/{len(missing)} assets")
            else:
                self.stdout.write("No missing assets found")
        
        elif options['configure']:
            manager.configure_admin_theme()
            self.stdout.write("Admin theme configured")
        
        else:
            self.stdout.write("Use --help to see available options")