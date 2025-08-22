"""
Company dashboard and management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from ..models import Firma, Faktura, Kontrahent, Produkt
from ..forms import FirmaForm


@login_required
def company_dashboard(request):
    """
    Company dashboard with overview and quick actions
    """
    try:
        firma = Firma.objects.get(user=request.user)
        has_company = True
    except Firma.DoesNotExist:
        firma = None
        has_company = False
    
    # If no company exists, redirect to add company
    if not has_company:
        messages.info(request, 'Proszę dodać dane swojej firmy aby rozpocząć korzystanie z FaktuLove.')
        return redirect('dodaj_firme')
    
    # Get company statistics
    stats = get_company_stats(request.user)
    
    context = {
        'firma': firma,
        'has_company': has_company,
        'stats': stats,
        'page_title': 'Dashboard Firmy',
        'show_add_company_btn': not has_company
    }
    
    return render(request, 'faktury/company_dashboard.html', context)


@login_required
def company_info(request):
    """
    Company information view (read-only)
    """
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, 'Nie znaleziono danych firmy.')
        return redirect('dodaj_firme')
    
    context = {
        'firma': firma,
        'page_title': 'Informacje o firmie'
    }
    
    return render(request, 'faktury/company_info.html', context)


@login_required
def company_settings(request):
    """
    Company settings and configuration
    """
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, 'Nie znaleziono danych firmy.')
        return redirect('dodaj_firme')
    
    if request.method == 'POST':
        form = FirmaForm(request.POST, request.FILES, instance=firma)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ustawienia firmy zostały zaktualizowane.')
            
            # AJAX response for better UX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Ustawienia zostały zapisane.'
                })
            
            return redirect('company_dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = FirmaForm(instance=firma)
    
    context = {
        'form': form,
        'firma': firma,
        'page_title': 'Ustawienia firmy'
    }
    
    return render(request, 'faktury/company_settings.html', context)


def get_company_stats(user):
    """
    Get company statistics
    """
    try:
        firma = Firma.objects.get(user=user)
    except Firma.DoesNotExist:
        return None
    
    # Calculate stats
    faktury_count = Faktura.objects.filter(user=user).count()
    kontrahenci_count = Kontrahent.objects.filter(user=user).count()
    produkty_count = Produkt.objects.filter(user=user).count()
    
    # Revenue calculations
    faktury_sprzedaz = Faktura.objects.filter(user=user, typ='sprzedaż')
    total_revenue = sum(f.wartosc_brutto for f in faktury_sprzedaz if f.wartosc_brutto)
    
    # Outstanding invoices
    outstanding_invoices = faktury_sprzedaz.filter(payment_status__in=['niezaplacona', 'czesciowo_zaplacona'])
    outstanding_amount = sum(f.wartosc_brutto for f in outstanding_invoices if f.wartosc_brutto)
    
    return {
        'faktury_count': faktury_count,
        'kontrahenci_count': kontrahenci_count,
        'produkty_count': produkty_count,
        'total_revenue': total_revenue,
        'outstanding_amount': outstanding_amount,
        'outstanding_count': outstanding_invoices.count(),
        'firma': firma
    }


@login_required
def company_api_status(request):
    """
    API endpoint for company status
    """
    try:
        firma = Firma.objects.get(user=request.user)
        stats = get_company_stats(request.user)
        
        return JsonResponse({
            'success': True,
            'company_exists': True,
            'company_name': firma.nazwa,
            'stats': {
                'faktury_count': stats['faktury_count'],
                'kontrahenci_count': stats['kontrahenci_count'],
                'produkty_count': stats['produkty_count'],
                'total_revenue': float(stats['total_revenue']) if stats['total_revenue'] else 0,
                'outstanding_amount': float(stats['outstanding_amount']) if stats['outstanding_amount'] else 0
            }
        })
    except Firma.DoesNotExist:
        return JsonResponse({
            'success': False,
            'company_exists': False,
            'message': 'Firma nie została skonfigurowana'
        })
