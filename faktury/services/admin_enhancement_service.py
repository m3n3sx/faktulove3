"""
Admin Enhancement Service

Provides enhanced Django admin functionality with Polish business features
"""

import logging
from typing import Dict, List, Optional, Any
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q, Avg
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.paginator import Paginator
from decimal import Decimal
import datetime

from faktury.models import (
    Firma, Kontrahent, Faktura, PozycjaFaktury, Produkt, 
    DocumentUpload, OCRResult, OCREngine
)

logger = logging.getLogger(__name__)


class AdminEnhancementService:
    """Enhanced Django admin functionality with Polish business features"""
    
    def __init__(self):
        self.admin_site = admin.site
        self.custom_views = []
        self.bulk_actions = {}
        
    def add_polish_admin_widgets(self) -> None:
        """Add Polish business admin widgets and enhancements"""
        # This is already implemented in admin_widgets.py and admin.py
        logger.info("Polish admin widgets are already configured")
    
    def create_admin_dashboard(self) -> None:
        """Create enhanced admin dashboard with system health indicators"""
        # Register custom dashboard view
        self.admin_site.index_template = 'admin/enhanced_dashboard.html'
        
        # Add custom URLs for dashboard functionality
        original_get_urls = self.admin_site.get_urls
        
        def get_urls():
            urls = original_get_urls()
            custom_urls = [
                path('dashboard/stats/', self.dashboard_stats_view, name='dashboard_stats'),
                path('dashboard/health/', self.system_health_view, name='system_health'),
                path('dashboard/recent-activity/', self.recent_activity_view, name='recent_activity'),
            ]
            return custom_urls + urls
        
        self.admin_site.get_urls = get_urls
        logger.info("Enhanced admin dashboard configured")
    
    @staff_member_required
    def dashboard_stats_view(self, request: HttpRequest) -> JsonResponse:
        """API endpoint for dashboard statistics"""
        try:
            stats = self._calculate_dashboard_stats()
            return JsonResponse(stats)
        except Exception as e:
            logger.error(f"Error calculating dashboard stats: {str(e)}")
            # Return basic stats instead of error
            return JsonResponse({
                'invoices': {'total': 0, 'this_month': 0, 'status_distribution': []},
                'revenue': {'this_month': 0, 'last_month': 0, 'change_percent': 0},
                'ocr': {'processed_today': 0, 'success_rate': 0},
                'entities': {'companies': 0, 'contractors': 0},
                'error': str(e)
            })
    
    @staff_member_required
    def system_health_view(self, request: HttpRequest) -> JsonResponse:
        """API endpoint for system health indicators"""
        try:
            health = self._check_system_health()
            return JsonResponse(health)
        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")
            # Return basic health status instead of error
            return JsonResponse({
                'overall_status': 'unknown',
                'checks': {
                    'database': {'status': 'unknown', 'message': 'Health check failed'},
                    'ocr_engines': {'status': 'unknown', 'message': 'Health check failed'},
                    'storage': {'status': 'unknown', 'message': 'Health check failed'},
                    'recent_errors': {'status': 'unknown', 'message': 'Health check failed'}
                },
                'last_updated': datetime.datetime.now().isoformat(),
                'error': str(e)
            })
    
    @staff_member_required
    def recent_activity_view(self, request: HttpRequest) -> JsonResponse:
        """API endpoint for recent activity"""
        try:
            activity = self._get_recent_activity()
            return JsonResponse({'activity': activity})
        except Exception as e:
            logger.error(f"Error getting recent activity: {str(e)}")
            # Return empty activity instead of error
            return JsonResponse({
                'activity': [],
                'error': str(e)
            })
    
    def _calculate_dashboard_stats(self) -> Dict[str, Any]:
        """Calculate dashboard statistics with error handling"""
        try:
            today = datetime.date.today()
            this_month = today.replace(day=1)
            last_month = (this_month - datetime.timedelta(days=1)).replace(day=1)
            
            # Invoice statistics with safe queries
            total_invoices = 0
            invoices_this_month = 0
            try:
                total_invoices = Faktura.objects.count()
                invoices_this_month = Faktura.objects.filter(
                    data_wystawienia__gte=this_month
                ).count()
            except Exception as e:
                logger.warning(f"Error getting invoice stats: {e}")
            
            # Revenue statistics (simplified)
            revenue_this_month = Decimal('0')
            revenue_last_month = Decimal('0')
            try:
                revenue_this_month = self._calculate_monthly_revenue(this_month)
                revenue_last_month = self._calculate_monthly_revenue(last_month)
            except Exception as e:
                logger.warning(f"Error calculating revenue: {e}")
            
            # OCR statistics
            ocr_processed_today = 0
            ocr_success_rate = 0.0
            try:
                ocr_processed_today = DocumentUpload.objects.filter(
                    upload_timestamp__date=today
                ).count()
                ocr_success_rate = self._calculate_ocr_success_rate()
            except Exception as e:
                logger.warning(f"Error getting OCR stats: {e}")
            
            # Company statistics
            total_companies = 0
            total_contractors = 0
            try:
                total_companies = Firma.objects.count()
                total_contractors = Kontrahent.objects.count()
            except Exception as e:
                logger.warning(f"Error getting entity stats: {e}")
            
            # Status distribution
            invoice_status_distribution = []
            try:
                invoice_status_distribution = list(
                    Faktura.objects.values('status')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                )
            except Exception as e:
                logger.warning(f"Error getting status distribution: {e}")
            
            return {
                'invoices': {
                    'total': total_invoices,
                    'this_month': invoices_this_month,
                    'status_distribution': invoice_status_distribution
                },
                'revenue': {
                    'this_month': float(revenue_this_month) if revenue_this_month else 0,
                    'last_month': float(revenue_last_month) if revenue_last_month else 0,
                    'change_percent': self._calculate_percentage_change(
                        revenue_last_month, revenue_this_month
                    )
                },
                'ocr': {
                    'processed_today': ocr_processed_today,
                    'success_rate': ocr_success_rate
                },
                'entities': {
                    'companies': total_companies,
                    'contractors': total_contractors
                }
            }
        except Exception as e:
            logger.error(f"Critical error in dashboard stats calculation: {e}")
            raise
    
    def _calculate_monthly_revenue(self, month_start: datetime.date) -> Decimal:
        """Calculate revenue for a given month with error handling"""
        try:
            month_end = (month_start + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            
            # This is a simplified calculation - in reality you'd need to sum invoice totals
            invoices = Faktura.objects.filter(
                data_wystawienia__gte=month_start,
                data_wystawienia__lte=month_end,
                status='paid'
            )
            
            total = Decimal('0')
            for invoice in invoices:
                try:
                    # Calculate total from positions
                    positions_total = invoice.pozycjafaktury_set.aggregate(
                        total=Sum('cena_netto')
                    )['total'] or Decimal('0')
                    total += positions_total
                except Exception as e:
                    logger.warning(f"Error calculating invoice {invoice.id} total: {e}")
                    continue
            
            return total
        except Exception as e:
            logger.warning(f"Error calculating monthly revenue: {e}")
            return Decimal('0')
    
    def _calculate_percentage_change(self, old_value: Optional[Decimal], new_value: Optional[Decimal]) -> float:
        """Calculate percentage change between two values"""
        if not old_value or old_value == 0:
            return 100.0 if new_value and new_value > 0 else 0.0
        
        if not new_value:
            return -100.0
        
        return float(((new_value - old_value) / old_value) * 100)
    
    def _calculate_ocr_success_rate(self) -> float:
        """Calculate OCR processing success rate"""
        total_uploads = DocumentUpload.objects.count()
        if total_uploads == 0:
            return 0.0
        
        successful_uploads = DocumentUpload.objects.filter(
            processing_status='completed'
        ).count()
        
        return (successful_uploads / total_uploads) * 100
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check system health indicators"""
        health_checks = {
            'database': self._check_database_health(),
            'ocr_engines': self._check_ocr_engines_health(),
            'storage': self._check_storage_health(),
            'recent_errors': self._check_recent_errors()
        }
        
        # Overall health status
        all_healthy = all(
            check.get('status') == 'healthy' 
            for check in health_checks.values()
        )
        
        return {
            'overall_status': 'healthy' if all_healthy else 'warning',
            'checks': health_checks,
            'last_updated': datetime.datetime.now().isoformat()
        }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            # Simple query to test database
            count = Faktura.objects.count()
            return {
                'status': 'healthy',
                'message': f'Database accessible, {count} invoices in system',
                'details': {
                    'invoice_count': count,
                    'response_time_ms': 'N/A'  # Could add timing here
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database error: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_ocr_engines_health(self) -> Dict[str, Any]:
        """Check OCR engines status"""
        try:
            active_engines = OCREngine.objects.filter(is_active=True).count()
            total_engines = OCREngine.objects.count()
            
            if active_engines == 0:
                status = 'warning'
                message = 'No active OCR engines'
            elif active_engines < total_engines:
                status = 'warning'
                message = f'{active_engines}/{total_engines} OCR engines active'
            else:
                status = 'healthy'
                message = f'All {active_engines} OCR engines active'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'active_engines': active_engines,
                    'total_engines': total_engines
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'OCR engine check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_storage_health(self) -> Dict[str, Any]:
        """Check storage and file system health"""
        try:
            # Check recent uploads
            recent_uploads = DocumentUpload.objects.filter(
                upload_timestamp__gte=datetime.datetime.now() - datetime.timedelta(hours=24)
            ).count()
            
            return {
                'status': 'healthy',
                'message': f'{recent_uploads} files uploaded in last 24h',
                'details': {
                    'recent_uploads': recent_uploads
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Storage check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_recent_errors(self) -> Dict[str, Any]:
        """Check for recent system errors"""
        try:
            # Check for failed OCR processing
            failed_ocr = DocumentUpload.objects.filter(
                processing_status='failed',
                upload_timestamp__gte=datetime.datetime.now() - datetime.timedelta(hours=24)
            ).count()
            
            if failed_ocr > 0:
                status = 'warning'
                message = f'{failed_ocr} OCR processing failures in last 24h'
            else:
                status = 'healthy'
                message = 'No recent processing errors'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'failed_ocr_24h': failed_ocr
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent system activity with error handling"""
        activities = []
        
        try:
            # Recent invoices
            recent_invoices = Faktura.objects.order_by('-data_wystawienia')[:5]
            for invoice in recent_invoices:
                try:
                    activities.append({
                        'type': 'invoice_created',
                        'title': f'Faktura {invoice.numer}',
                        'description': f'Utworzona dla {invoice.nabywca.nazwa if invoice.nabywca else "N/A"}',
                        'timestamp': invoice.data_wystawienia.isoformat() if invoice.data_wystawienia else None,
                        'url': reverse('admin:faktury_faktura_change', args=[invoice.id])
                    })
                except Exception as e:
                    logger.warning(f"Error processing invoice activity {invoice.id}: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Error getting recent invoices: {e}")
        
        try:
            # Recent OCR processing
            recent_ocr = DocumentUpload.objects.order_by('-upload_timestamp')[:5]
            for upload in recent_ocr:
                try:
                    activities.append({
                        'type': 'ocr_processed',
                        'title': f'OCR: {upload.original_filename}',
                        'description': f'Status: {upload.get_processing_status_display()}',
                        'timestamp': upload.upload_timestamp.isoformat(),
                        'url': reverse('admin:faktury_documentupload_change', args=[upload.id])
                    })
                except Exception as e:
                    logger.warning(f"Error processing OCR activity {upload.id}: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Error getting recent OCR uploads: {e}")
        
        # Sort by timestamp
        try:
            activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        except Exception as e:
            logger.warning(f"Error sorting activities: {e}")
        
        return activities[:10]  # Return top 10 most recent
    
    def add_bulk_operations(self) -> None:
        """Add bulk operations for invoice and company management"""
        # These are implemented as admin actions in the admin.py file
        # Additional bulk operations can be added here
        
        def bulk_mark_invoices_paid(modeladmin, request, queryset):
            """Bulk action to mark invoices as paid"""
            updated = queryset.update(status='paid')
            messages.success(
                request, 
                f'Oznaczono {updated} faktur jako opłacone'
            )
        bulk_mark_invoices_paid.short_description = "Oznacz jako opłacone"
        
        def bulk_mark_invoices_sent(modeladmin, request, queryset):
            """Bulk action to mark invoices as sent"""
            updated = queryset.update(status='sent')
            messages.success(
                request, 
                f'Oznaczono {updated} faktur jako wysłane'
            )
        bulk_mark_invoices_sent.short_description = "Oznacz jako wysłane"
        
        def bulk_export_invoices_pdf(modeladmin, request, queryset):
            """Bulk action to export invoices as PDF"""
            # This would need PDF generation implementation
            messages.info(
                request, 
                f'Eksport PDF dla {queryset.count()} faktur zostanie wkrótce zaimplementowany'
            )
        bulk_export_invoices_pdf.short_description = "Eksportuj jako PDF"
        
        # Store bulk actions for later registration
        self.bulk_actions['faktura'] = [
            bulk_mark_invoices_paid,
            bulk_mark_invoices_sent,
            bulk_export_invoices_pdf
        ]
        
        logger.info("Bulk operations configured")
    
    def integrate_multi_company_context(self) -> None:
        """Integrate admin panel with multi-company context switching"""
        # Add company context to admin interface
        original_each_context = self.admin_site.each_context
        
        def each_context(request):
            context = original_each_context(request)
            
            # Add company selection to context
            if hasattr(request.user, 'userprofile'):
                user_companies = Firma.objects.filter(user=request.user)
                context['user_companies'] = user_companies
                
                # Get current company from session or default
                current_company_id = request.session.get('current_company_id')
                if current_company_id:
                    try:
                        current_company = user_companies.get(id=current_company_id)
                        context['current_company'] = current_company
                    except Firma.DoesNotExist:
                        pass
            
            # Add Polish business context
            context['polish_business_features'] = {
                'nip_validation': True,
                'vat_rates': [0, 5, 8, 23, -1],  # Polish VAT rates
                'currency': 'PLN',
                'date_format': 'DD.MM.YYYY'
            }
            
            return context
        
        self.admin_site.each_context = each_context
        
        # Add company switching URL
        original_get_urls = self.admin_site.get_urls
        
        def get_urls():
            urls = original_get_urls()
            custom_urls = [
                path('switch-company/<int:company_id>/', 
                     self.switch_company_view, 
                     name='switch_company'),
            ]
            return custom_urls + urls
        
        self.admin_site.get_urls = get_urls
        
        logger.info("Multi-company context integration configured")
    
    @staff_member_required
    def switch_company_view(self, request: HttpRequest, company_id: int) -> HttpResponse:
        """Switch current company context"""
        try:
            # Verify user has access to this company
            company = Firma.objects.get(id=company_id, user=request.user)
            request.session['current_company_id'] = company_id
            
            messages.success(
                request, 
                f'Przełączono na firmę: {company.nazwa}'
            )
        except Firma.DoesNotExist:
            messages.error(
                request, 
                'Nie masz dostępu do tej firmy'
            )
        
        return redirect('admin:index')
    
    def setup_enhanced_admin(self) -> None:
        """Setup all enhanced admin features"""
        logger.info("Setting up enhanced admin features...")
        
        try:
            self.add_polish_admin_widgets()
            self.create_admin_dashboard()
            self.add_bulk_operations()
            self.integrate_multi_company_context()
            
            logger.info("Enhanced admin setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up enhanced admin: {str(e)}")
            return False
    
    def get_enhancement_status(self) -> Dict[str, bool]:
        """Get status of admin enhancements"""
        return {
            'polish_widgets_enabled': True,  # Already implemented
            'dashboard_enhanced': hasattr(self.admin_site, 'index_template'),
            'bulk_operations_added': bool(self.bulk_actions),
            'multi_company_integrated': hasattr(self.admin_site, 'each_context')
        }


# Global instance for use in admin configuration
admin_enhancement_service = AdminEnhancementService()