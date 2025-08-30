"""
Company Management Views for multi-tenancy support
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, timedelta, date

from ..models import Firma, Kontrahent, Partnerstwo, Faktura
from ..services.company_management_service import CompanyManagementService
from ..services.partnership_manager import PartnershipManager
from ..company_forms import (
    EnhancedFirmaForm, CompanyContextSwitchForm, EnhancedPartnerstwoForm,
    PartnershipInviteForm, CompanyPermissionsForm, CompanyStatisticsFilterForm
)


@login_required
def company_dashboard(request):
    """
    Main company dashboard with multi-company support
    """
    try:
        company_service = CompanyManagementService()
        
        # Get user's companies
        user_companies = company_service.get_user_companies(request.user)
        
        # Get current company context (from session or default to user's company)
        current_company_id = request.session.get('current_company_id')
        current_company = None
        
        if current_company_id:
            try:
                current_company = Firma.objects.get(id=current_company_id)
                # Verify user has access
                if not company_service.user_has_company_access(request.user, current_company_id):
                    current_company = None
                    del request.session['current_company_id']
            except Firma.DoesNotExist:
                current_company = None
                del request.session['current_company_id']
        
        # Default to user's own company if no context set
        if not current_company and hasattr(request.user, 'firma'):
            current_company = request.user.firma
            request.session['current_company_id'] = current_company.id
        
        # Get company statistics
        company_stats = {}
        if current_company:
            company_stats = company_service.get_company_statistics(current_company)
        
        # Get recent activities
        recent_invoices = []
        if current_company:
            recent_invoices = Faktura.objects.filter(
                Q(sprzedawca=current_company) | Q(user=current_company.user)
            ).select_related('nabywca', 'sprzedawca').order_by('-data_wystawienia')[:10]
        
        # Company context switch form
        context_form = CompanyContextSwitchForm(request.user)
        
        context = {
            'user_companies': user_companies,
            'current_company': current_company,
            'company_stats': company_stats,
            'recent_invoices': recent_invoices,
            'context_form': context_form,
        }
        
        return render(request, 'faktury/company/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Błąd podczas ładowania panelu: {str(e)}')
        return render(request, 'faktury/company/dashboard.html', {})


@login_required
def switch_company_context(request):
    """
    Switch between company contexts
    """
    if request.method == 'POST':
        form = CompanyContextSwitchForm(request.user, request.POST)
        if form.is_valid():
            company = form.cleaned_data['company']
            
            # Verify access
            company_service = CompanyManagementService()
            if company_service.user_has_company_access(request.user, company.id):
                request.session['current_company_id'] = company.id
                messages.success(request, f'Przełączono na firmę: {company.nazwa}')
            else:
                messages.error(request, 'Brak uprawnień do tej firmy')
    
    return redirect('company_dashboard')


@login_required
def create_test_companies(request):
    """
    Create test companies for demonstration
    """
    if request.method == 'POST':
        try:
            company_service = CompanyManagementService()
            created_companies = company_service.create_test_companies()
            
            if created_companies:
                messages.success(
                    request, 
                    f'Utworzono {len(created_companies)} firm testowych'
                )
            else:
                messages.info(request, 'Firmy testowe już istnieją')
                
        except Exception as e:
            messages.error(request, f'Błąd podczas tworzenia firm testowych: {str(e)}')
    
    return redirect('company_dashboard')


@login_required
def company_list(request):
    """
    List all companies user has access to
    """
    try:
        company_service = CompanyManagementService()
        user_companies = company_service.get_user_companies(request.user)
        
        # Add statistics for each company
        companies_with_stats = []
        for company_data in user_companies:
            company = Firma.objects.get(id=company_data['id'])
            stats = company_service.get_company_statistics(company)
            company_data['stats'] = stats
            companies_with_stats.append(company_data)
        
        context = {
            'companies': companies_with_stats,
        }
        
        return render(request, 'faktury/company/list.html', context)
        
    except Exception as e:
        messages.error(request, f'Błąd podczas ładowania listy firm: {str(e)}')
        return render(request, 'faktury/company/list.html', {'companies': []})


@login_required
def company_detail(request, company_id):
    """
    Detailed view of a specific company
    """
    try:
        company_service = CompanyManagementService()
        
        # Verify access
        if not company_service.user_has_company_access(request.user, company_id):
            messages.error(request, 'Brak uprawnień do tej firmy')
            return redirect('company_list')
        
        company = get_object_or_404(Firma, id=company_id)
        
        # Get company statistics
        stats = company_service.get_company_statistics(company)
        
        # Get partnerships
        partnerships = Partnerstwo.objects.filter(
            Q(firma1=company) | Q(firma2=company)
        ).select_related('firma1', 'firma2').order_by('-data_utworzenia')
        
        # Get recent invoices
        recent_invoices = Faktura.objects.filter(
            Q(sprzedawca=company) | Q(user=company.user)
        ).select_related('nabywca', 'sprzedawca').order_by('-data_wystawienia')[:20]
        
        # Statistics filter form
        filter_form = CompanyStatisticsFilterForm(request.user, request.GET or None)
        
        context = {
            'company': company,
            'stats': stats,
            'partnerships': partnerships,
            'recent_invoices': recent_invoices,
            'filter_form': filter_form,
            'is_owner': company.user == request.user,
        }
        
        return render(request, 'faktury/company/detail.html', context)
        
    except Exception as e:
        messages.error(request, f'Błąd podczas ładowania szczegółów firmy: {str(e)}')
        return redirect('company_list')


@login_required
def edit_company(request, company_id):
    """
    Edit company information
    """
    try:
        company_service = CompanyManagementService()
        
        # Verify access (only owner can edit)
        company = get_object_or_404(Firma, id=company_id)
        if company.user != request.user:
            messages.error(request, 'Tylko właściciel może edytować dane firmy')
            return redirect('company_detail', company_id=company_id)
        
        if request.method == 'POST':
            form = EnhancedFirmaForm(request.POST, request.FILES, instance=company)
            if form.is_valid():
                form.save()
                messages.success(request, 'Dane firmy zostały zaktualizowane')
                return redirect('company_detail', company_id=company_id)
        else:
            form = EnhancedFirmaForm(instance=company)
        
        context = {
            'form': form,
            'company': company,
        }
        
        return render(request, 'faktury/company/edit.html', context)
        
    except Exception as e:
        messages.error(request, f'Błąd podczas edycji firmy: {str(e)}')
        return redirect('company_list')


@login_required
def partnership_management(request):
    """
    Partnership management interface
    """
    try:
        if not hasattr(request.user, 'firma'):
            messages.error(request, 'Najpierw dodaj dane swojej firmy')
            return redirect('dodaj_firme')
        
        user_company = request.user.firma
        partnership_manager = PartnershipManager()
        
        # Get partnerships
        partnerships = Partnerstwo.objects.filter(
            Q(firma1=user_company) | Q(firma2=user_company)
        ).select_related('firma1', 'firma2').order_by('-data_utworzenia')
        
        # Get partnership details
        partnerships_with_details = []
        for partnership in partnerships:
            details = partnership_manager.get_partnership_details(partnership)
            partnerships_with_details.append({
                'partnership': partnership,
                'details': details,
                'other_company': details.get('partnership', {}).get('firma2') if partnership.firma1 == user_company else details.get('partnership', {}).get('firma1')
            })
        
        # Partnership invite form
        invite_form = PartnershipInviteForm()
        
        context = {
            'partnerships': partnerships_with_details,
            'invite_form': invite_form,
            'user_company': user_company,
        }
        
        return render(request, 'faktury/company/partnerships.html', context)
        
    except Exception as e:
        messages.error(request, f'Błąd podczas ładowania partnerstw: {str(e)}')
        return render(request, 'faktury/company/partnerships.html', {})


@login_required
def create_partnership(request):
    """
    Create new partnership
    """
    if request.method == 'POST':
        try:
            if not hasattr(request.user, 'firma'):
                messages.error(request, 'Najpierw dodaj dane swojej firmy')
                return redirect('dodaj_firme')
            
            form = EnhancedPartnerstwoForm(request.user, request.POST)
            if form.is_valid():
                partnership = form.save(commit=False)
                partnership.firma1 = request.user.firma
                
                # Check if partnership already exists
                existing = Partnerstwo.objects.filter(
                    Q(firma1=partnership.firma1, firma2=partnership.firma2) |
                    Q(firma1=partnership.firma2, firma2=partnership.firma1)
                ).first()
                
                if existing:
                    messages.error(request, 'Partnerstwo z tą firmą już istnieje')
                else:
                    partnership.save()
                    
                    # Create cross-contractors
                    partnership_manager = PartnershipManager()
                    partnership_manager._create_cross_contractors(
                        partnership.firma1, partnership.firma2
                    )
                    
                    messages.success(
                        request, 
                        f'Partnerstwo z firmą {partnership.firma2.nazwa} zostało utworzone'
                    )
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                        
        except Exception as e:
            messages.error(request, f'Błąd podczas tworzenia partnerstwa: {str(e)}')
    
    return redirect('partnership_management')


@login_required
def partnership_detail(request, partnership_id):
    """
    Detailed partnership view with analytics
    """
    try:
        if not hasattr(request.user, 'firma'):
            messages.error(request, 'Najpierw dodaj dane swojej firmy')
            return redirect('dodaj_firme')
        
        user_company = request.user.firma
        partnership = get_object_or_404(
            Partnerstwo,
            Q(firma1=user_company) | Q(firma2=user_company),
            id=partnership_id
        )
        
        partnership_manager = PartnershipManager()
        
        # Get detailed analytics
        details = partnership_manager.get_partnership_details(partnership)
        transaction_tracking = partnership_manager.track_partner_transactions(partnership)
        
        # Generate report
        report = partnership_manager.generate_partnership_report(partnership)
        
        context = {
            'partnership': partnership,
            'details': details,
            'transaction_tracking': transaction_tracking,
            'report': report,
            'user_company': user_company,
        }
        
        return render(request, 'faktury/company/partnership_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'Błąd podczas ładowania szczegółów partnerstwa: {str(e)}')
        return redirect('partnership_management')


@login_required
@require_http_methods(["POST"])
def invite_partnership(request):
    """
    Invite company to partnership via NIP
    """
    try:
        if not hasattr(request.user, 'firma'):
            messages.error(request, 'Najpierw dodaj dane swojej firmy')
            return redirect('dodaj_firme')
        
        form = PartnershipInviteForm(request.POST)
        if form.is_valid():
            target_company = form.cleaned_data['target_company']
            
            # Check if partnership already exists
            existing = Partnerstwo.objects.filter(
                Q(firma1=request.user.firma, firma2=target_company) |
                Q(firma1=target_company, firma2=request.user.firma)
            ).first()
            
            if existing:
                messages.error(request, 'Partnerstwo z tą firmą już istnieje')
            else:
                # Create partnership
                partnership = Partnerstwo.objects.create(
                    firma1=request.user.firma,
                    firma2=target_company,
                    typ_partnerstwa=form.cleaned_data['partnership_type'],
                    opis=form.cleaned_data.get('message', ''),
                    aktywne=True,
                    auto_ksiegowanie=form.cleaned_data.get('auto_accounting', True)
                )
                
                # Create cross-contractors
                partnership_manager = PartnershipManager()
                partnership_manager._create_cross_contractors(
                    partnership.firma1, partnership.firma2
                )
                
                messages.success(
                    request,
                    f'Wysłano zaproszenie do partnerstwa firmie {target_company.nazwa}'
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
                    
    except Exception as e:
        messages.error(request, f'Błąd podczas wysyłania zaproszenia: {str(e)}')
    
    return redirect('partnership_management')


@login_required
def company_statistics_api(request, company_id):
    """
    API endpoint for company statistics
    """
    try:
        company_service = CompanyManagementService()
        
        # Verify access
        if not company_service.user_has_company_access(request.user, company_id):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        company = get_object_or_404(Firma, id=company_id)
        stats = company_service.get_company_statistics(company)
        
        # Convert Decimal to float for JSON serialization
        for key, value in stats.items():
            if hasattr(value, 'quantize'):  # Decimal
                stats[key] = float(value)
        
        return JsonResponse(stats)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def partnership_analytics_api(request, partnership_id):
    """
    API endpoint for partnership analytics
    """
    try:
        if not hasattr(request.user, 'firma'):
            return JsonResponse({'error': 'No company found'}, status=400)
        
        user_company = request.user.firma
        partnership = get_object_or_404(
            Partnerstwo,
            Q(firma1=user_company) | Q(firma2=user_company),
            id=partnership_id
        )
        
        partnership_manager = PartnershipManager()
        tracking = partnership_manager.track_partner_transactions(partnership)
        
        # Convert Decimal to float for JSON serialization
        def convert_decimals(obj):
            if isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            elif hasattr(obj, 'quantize'):  # Decimal
                return float(obj)
            else:
                return obj
        
        tracking = convert_decimals(tracking)
        
        return JsonResponse(tracking)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)