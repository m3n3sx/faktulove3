"""
Super Admin Panel Views
Comprehensive admin interface for system management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.conf import settings
import json
import logging
from datetime import datetime, timedelta

from ..models import (
    Firma, Kontrahent, Faktura, Produkt, UserProfile, 
    Partnerstwo, FakturaCykliczna
)
from ..services.gus_service import gus_service
from ..forms import FirmaForm, UserProfileForm

logger = logging.getLogger(__name__)


def is_superuser(user):
    """Check if user is superuser"""
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_superuser)
def superadmin_dashboard(request):
    """
    Main super admin dashboard with system overview
    """
    # System statistics
    stats = {
        'users': {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'inactive': User.objects.filter(is_active=False).count(),
            'superusers': User.objects.filter(is_superuser=True).count(),
            'new_today': User.objects.filter(date_joined__date=timezone.now().date()).count(),
            'new_week': User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count(),
        },
        'companies': {
            'total': Firma.objects.count(),
            'with_nip': Firma.objects.exclude(nip__isnull=True).exclude(nip='').count(),
            'without_nip': Firma.objects.filter(Q(nip__isnull=True) | Q(nip='')).count(),
        },
        'invoices': {
            'total': Faktura.objects.count(),
            'sales': Faktura.objects.filter(typ_faktury='sprzedaz').count(),
            'costs': Faktura.objects.filter(typ_faktury='koszt').count(),
            'this_month': Faktura.objects.filter(data_wystawienia__month=timezone.now().month).count(),
            'auto_accounted': Faktura.objects.filter(auto_ksiegowana=True).count(),
        },
        'contractors': {
            'total': Kontrahent.objects.count(),
            'companies': Kontrahent.objects.filter(czy_firma=True).count(),
            'individuals': Kontrahent.objects.filter(czy_firma=False).count(),
        },
        'partnerships': {
            'total': Partnerstwo.objects.count(),
            'active': Partnerstwo.objects.filter(aktywne=True).count(),
            'with_auto_accounting': Partnerstwo.objects.filter(auto_ksiegowanie=True).count(),
        },
        'products': {
            'total': Produkt.objects.count(),
        },
        'system': {
            'debug_mode': settings.DEBUG,
            'database': 'SQLite' if 'sqlite' in settings.DATABASES['default']['ENGINE'] else 'MySQL/PostgreSQL',
            'gus_configured': bool(getattr(settings, 'GUS_API_KEY', None)),
            'email_configured': bool(getattr(settings, 'EMAIL_HOST', None)),
        }
    }
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_invoices = Faktura.objects.order_by('-data_wystawienia')[:10]
    recent_companies = Firma.objects.order_by('-id')[:10]
    
    # System health checks
    health_checks = []
    
    # Check GUS API
    if stats['system']['gus_configured']:
        gus_test = gus_service.test_connection()
        health_checks.append({
            'name': 'GUS API',
            'status': 'ok' if gus_test['success'] else 'error',
            'message': gus_test['message']
        })
    else:
        health_checks.append({
            'name': 'GUS API',
            'status': 'warning',
            'message': 'GUS API key not configured'
        })
    
    # Check database
    try:
        User.objects.count()
        health_checks.append({
            'name': 'Database',
            'status': 'ok',
            'message': 'Database connection working'
        })
    except Exception as e:
        health_checks.append({
            'name': 'Database',
            'status': 'error',
            'message': f'Database error: {str(e)}'
        })
    
    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_invoices': recent_invoices,
        'recent_companies': recent_companies,
        'health_checks': health_checks,
        'page_title': 'Super Admin Dashboard'
    }
    
    return render(request, 'superadmin/dashboard.html', context)


@login_required
@user_passes_test(is_superuser)
def user_management(request):
    """
    User management interface
    """
    # Get all users with related data
    users_list = User.objects.select_related('userprofile').prefetch_related('firma').annotate(
        invoice_count=Count('faktura'),
        company_count=Count('firma')
    ).order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Filter functionality
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users_list = users_list.filter(is_active=True)
    elif status_filter == 'inactive':
        users_list = users_list.filter(is_active=False)
    elif status_filter == 'superuser':
        users_list = users_list.filter(is_superuser=True)
    elif status_filter == 'staff':
        users_list = users_list.filter(is_staff=True)
    
    # Pagination
    paginator = Paginator(users_list, 25)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'search_query': search_query,
        'status_filter': status_filter,
        'page_title': 'User Management'
    }
    
    return render(request, 'superadmin/user_management.html', context)


@login_required
@user_passes_test(is_superuser)
def user_detail(request, user_id):
    """
    Detailed user information and management
    """
    user = get_object_or_404(User, id=user_id)
    
    # Get user's profile
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = None
    
    # Get user's company
    try:
        company = user.firma
    except Firma.DoesNotExist:
        company = None
    
    # Get user's statistics
    user_stats = {
        'invoices': {
            'total': Faktura.objects.filter(user=user).count(),
            'sales': Faktura.objects.filter(user=user, typ_faktury='sprzedaz').count(),
            'costs': Faktura.objects.filter(user=user, typ_faktury='koszt').count(),
        },
        'contractors': Kontrahent.objects.filter(user=user).count(),
        'products': Produkt.objects.filter(user=user).count(),
        'partnerships': Partnerstwo.objects.filter(
            Q(firma1__user=user) | Q(firma2__user=user)
        ).count() if company else 0,
    }
    
    # Recent activity
    recent_invoices = Faktura.objects.filter(user=user).order_by('-data_wystawienia')[:5]
    recent_contractors = Kontrahent.objects.filter(user=user).order_by('-id')[:5]
    
    context = {
        'user_obj': user,  # Renamed to avoid conflict with request.user
        'profile': profile,
        'company': company,
        'user_stats': user_stats,
        'recent_invoices': recent_invoices,
        'recent_contractors': recent_contractors,
        'page_title': f'User: {user.username}'
    }
    
    return render(request, 'superadmin/user_detail.html', context)


@login_required
@user_passes_test(is_superuser)
def user_toggle_status(request, user_id):
    """
    Toggle user active status (AJAX)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = get_object_or_404(User, id=user_id)
    
    # Don't allow deactivating self
    if user == request.user:
        return JsonResponse({'error': 'Cannot deactivate your own account'}, status=400)
    
    user.is_active = not user.is_active
    user.save()
    
    action = 'activated' if user.is_active else 'deactivated'
    logger.info(f"User {user.username} {action} by admin {request.user.username}")
    
    return JsonResponse({
        'success': True,
        'message': f'User {user.username} has been {action}',
        'is_active': user.is_active
    })


@login_required
@user_passes_test(is_superuser)
def user_reset_password(request, user_id):
    """
    Reset user password
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            logger.info(f"Password reset for user {user.username} by admin {request.user.username}")
            messages.success(request, f'Password successfully reset for user {user.username}')
            return redirect('superadmin:user_detail', user_id=user.id)
    else:
        form = SetPasswordForm(user)
    
    context = {
        'form': form,
        'user_obj': user,
        'page_title': f'Reset Password: {user.username}'
    }
    
    return render(request, 'superadmin/user_reset_password.html', context)


@login_required
@user_passes_test(is_superuser)
def company_management(request):
    """
    Company management interface
    """
    companies_list = Firma.objects.select_related('user').annotate(
        invoice_count=Count('sprzedawca_faktury'),
        contractor_count=Count('user__kontrahent')
    ).order_by('-id')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        companies_list = companies_list.filter(
            Q(nazwa__icontains=search_query) |
            Q(nip__icontains=search_query) |
            Q(regon__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Filter functionality
    filter_type = request.GET.get('filter', '')
    if filter_type == 'with_nip':
        companies_list = companies_list.exclude(nip__isnull=True).exclude(nip='')
    elif filter_type == 'without_nip':
        companies_list = companies_list.filter(Q(nip__isnull=True) | Q(nip=''))
    elif filter_type == 'with_logo':
        companies_list = companies_list.exclude(logo__isnull=True).exclude(logo='')
    
    # Pagination
    paginator = Paginator(companies_list, 25)
    page_number = request.GET.get('page')
    companies = paginator.get_page(page_number)
    
    context = {
        'companies': companies,
        'search_query': search_query,
        'filter_type': filter_type,
        'page_title': 'Company Management'
    }
    
    return render(request, 'superadmin/company_management.html', context)


@login_required
@user_passes_test(is_superuser)
def system_settings(request):
    """
    System settings and configuration
    """
    # GUS API test
    gus_status = None
    if request.method == 'POST' and 'test_gus' in request.POST:
        gus_status = gus_service.test_connection()
        if gus_status['success']:
            messages.success(request, f"GUS API: {gus_status['message']}")
        else:
            messages.error(request, f"GUS API: {gus_status['message']}")
    
    # System information
    system_info = {
        'debug_mode': settings.DEBUG,
        'secret_key_set': bool(settings.SECRET_KEY and settings.SECRET_KEY != 'your-secret-key-here'),
        'database_engine': settings.DATABASES['default']['ENGINE'],
        'gus_api_key': bool(getattr(settings, 'GUS_API_KEY', None)),
        'email_host': getattr(settings, 'EMAIL_HOST', None),
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'csrf_trusted_origins': getattr(settings, 'CSRF_TRUSTED_ORIGINS', []),
    }
    
    context = {
        'system_info': system_info,
        'gus_status': gus_status,
        'page_title': 'System Settings'
    }
    
    return render(request, 'superadmin/system_settings.html', context)


@login_required
@user_passes_test(is_superuser)
def gus_test_api(request):
    """
    Test GUS API functionality (AJAX)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    nip = data.get('nip', '').strip()
    
    if not nip:
        return JsonResponse({'error': 'NIP is required'}, status=400)
    
    # Test GUS API
    result = gus_service.search_by_nip(nip)
    
    if result.get('success'):
        return JsonResponse({
            'success': True,
            'message': 'GUS API working correctly',
            'data': result['data']
        })
    else:
        return JsonResponse({
            'success': False,
            'message': result.get('error', 'Unknown error'),
            'error': result.get('error')
        })


@login_required
@user_passes_test(is_superuser)
def system_logs(request):
    """
    View system logs and activity
    """
    # This is a basic implementation
    # In production, you might want to integrate with logging framework
    
    log_entries = []
    
    # Recent user logins (you'd need to implement login logging)
    recent_users = User.objects.filter(last_login__isnull=False).order_by('-last_login')[:20]
    for user in recent_users:
        log_entries.append({
            'timestamp': user.last_login,
            'type': 'login',
            'user': user.username,
            'message': f'User logged in'
        })
    
    # Recent user registrations
    recent_registrations = User.objects.order_by('-date_joined')[:10]
    for user in recent_registrations:
        log_entries.append({
            'timestamp': user.date_joined,
            'type': 'registration',
            'user': user.username,
            'message': f'New user registered'
        })
    
    # Sort by timestamp
    log_entries.sort(key=lambda x: x['timestamp'] or timezone.now(), reverse=True)
    
    # Pagination
    paginator = Paginator(log_entries, 50)
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)
    
    context = {
        'logs': logs,
        'page_title': 'System Logs'
    }
    
    return render(request, 'superadmin/system_logs.html', context)


@login_required
@user_passes_test(is_superuser)
def mass_actions(request):
    """
    Mass actions interface
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_users = request.POST.getlist('selected_users')
        
        if action == 'activate' and selected_users:
            User.objects.filter(id__in=selected_users).update(is_active=True)
            messages.success(request, f'Activated {len(selected_users)} users')
            
        elif action == 'deactivate' and selected_users:
            # Don't deactivate superusers or current user
            exclude_ids = [request.user.id]
            exclude_ids.extend(User.objects.filter(is_superuser=True).values_list('id', flat=True))
            
            users_to_deactivate = [uid for uid in selected_users if int(uid) not in exclude_ids]
            User.objects.filter(id__in=users_to_deactivate).update(is_active=False)
            messages.success(request, f'Deactivated {len(users_to_deactivate)} users')
            
        elif action == 'delete_inactive' and selected_users:
            # Only delete inactive users without companies/invoices
            users_to_delete = User.objects.filter(
                id__in=selected_users,
                is_active=False,
                firma__isnull=True,
                faktura__isnull=True
            )
            count = users_to_delete.count()
            users_to_delete.delete()
            messages.success(request, f'Deleted {count} inactive users')
        
        return redirect('superadmin:user_management')
    
    return redirect('superadmin:user_management')


@login_required
@user_passes_test(is_superuser)
def export_data(request):
    """
    Export system data
    """
    export_type = request.GET.get('type', '')
    
    if export_type == 'users':
        # Export users data
        response = JsonResponse({
            'users': list(User.objects.values(
                'id', 'username', 'email', 'first_name', 'last_name',
                'is_active', 'is_staff', 'date_joined', 'last_login'
            ))
        })
        response['Content-Disposition'] = 'attachment; filename="users_export.json"'
        return response
        
    elif export_type == 'companies':
        # Export companies data
        response = JsonResponse({
            'companies': list(Firma.objects.values(
                'id', 'nazwa', 'nip', 'regon', 'ulica', 'miejscowosc',
                'kod_pocztowy', 'user__username'
            ))
        })
        response['Content-Disposition'] = 'attachment; filename="companies_export.json"'
        return response
    
    return JsonResponse({'error': 'Invalid export type'}, status=400)
