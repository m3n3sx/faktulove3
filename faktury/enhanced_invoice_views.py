"""
Enhanced invoice views using design system components
"""
import datetime
import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count

from .models import Faktura, Firma, Kontrahent, PozycjaFaktury
from .enhanced_forms import (
    EnhancedFakturaForm, 
    EnhancedPozycjaFakturyFormSet,
    EnhancedKontrahentForm
)

logger = logging.getLogger(__name__)


@login_required
def enhanced_invoice_create(request):
    """Enhanced invoice creation view with design system components"""
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Uzupełnij dane swojej firmy przed wystawieniem faktury.")
        return redirect('dodaj_firme')

    kontrahent_id = request.GET.get('kontrahent')
    initial_data = {
        'miejsce_wystawienia': firma.miejscowosc,
        'typ_faktury': 'sprzedaz',
        'sprzedawca': firma.id
    }

    if kontrahent_id:
        initial_data['nabywca'] = kontrahent_id

    if request.method == 'POST':
        form = EnhancedFakturaForm(request.POST, user=request.user, initial=initial_data)
        formset = EnhancedPozycjaFakturyFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Save invoice
                    faktura = form.save(commit=False)
                    faktura.user = request.user
                    faktura.sprzedawca = firma
                    
                    # Generate invoice number if auto numbering is enabled
                    if form.cleaned_data.get('auto_numer', True):
                        faktura.numer = _generate_invoice_number(request.user, faktura.typ_dokumentu)
                    elif form.cleaned_data.get('wlasny_numer'):
                        faktura.numer = form.cleaned_data['wlasny_numer']
                    
                    faktura.save()
                    
                    # Save invoice items
                    formset.instance = faktura
                    formset.save()
                    
                    # Handle recurring invoice setup
                    if form.cleaned_data.get('cykliczna'):
                        _setup_recurring_invoice(faktura, form.cleaned_data)
                    
                    messages.success(request, f'Faktura {faktura.numer} została utworzona pomyślnie.')
                    return redirect('enhanced_invoice_detail', pk=faktura.pk)
                    
            except Exception as e:
                logger.error(f"Error creating invoice: {e}")
                messages.error(request, "Wystąpił błąd podczas tworzenia faktury.")
    else:
        form = EnhancedFakturaForm(user=request.user, initial=initial_data)
        formset = EnhancedPozycjaFakturyFormSet()

    context = {
        'form': form,
        'formset': formset,
        'firma': firma,
        'title': 'Nowa faktura',
        'kontrahenci': Kontrahent.objects.filter(user=request.user),
        'produkty': _get_user_products(request.user),
    }
    
    return render(request, 'faktury/enhanced_invoice_form.html', context)


@login_required
def enhanced_invoice_edit(request, pk):
    """Enhanced invoice editing view"""
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = EnhancedFakturaForm(request.POST, instance=faktura, user=request.user)
        formset = EnhancedPozycjaFakturyFormSet(request.POST, instance=faktura)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    faktura = form.save()
                    formset.save()
                    
                    messages.success(request, f'Faktura {faktura.numer} została zaktualizowana.')
                    return redirect('enhanced_invoice_detail', pk=faktura.pk)
                    
            except Exception as e:
                logger.error(f"Error updating invoice {pk}: {e}")
                messages.error(request, "Wystąpił błąd podczas aktualizacji faktury.")
    else:
        form = EnhancedFakturaForm(instance=faktura, user=request.user)
        formset = EnhancedPozycjaFakturyFormSet(instance=faktura)

    context = {
        'form': form,
        'formset': formset,
        'faktura': faktura,
        'title': f'Edytuj fakturę {faktura.numer}',
        'kontrahenci': Kontrahent.objects.filter(user=request.user),
        'produkty': _get_user_products(request.user),
    }
    
    return render(request, 'faktury/enhanced_invoice_form.html', context)


@login_required
def enhanced_invoice_detail(request, pk):
    """Enhanced invoice detail view with status management"""
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    
    # Calculate totals
    pozycje = faktura.pozycjafaktury_set.all()
    totals = _calculate_invoice_totals(pozycje)
    
    # Get compliance status
    compliance_rules = _get_compliance_rules(faktura)
    
    # Get status history (if implemented)
    status_history = _get_status_history(faktura)
    
    context = {
        'faktura': faktura,
        'pozycje': pozycje,
        'totals': totals,
        'compliance_rules': compliance_rules,
        'status_history': status_history,
        'can_edit': faktura.status in ['wystawiona', 'szkic'],
        'can_send': faktura.status in ['wystawiona'],
        'can_mark_paid': faktura.status in ['wystawiona', 'cz_oplacona'],
    }
    
    return render(request, 'faktury/enhanced_invoice_detail.html', context)


@login_required
def enhanced_invoice_list(request):
    """Enhanced invoice list view with filtering and status display"""
    invoices = Faktura.objects.filter(user=request.user).select_related('nabywca', 'sprzedawca')
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    date_from = request.GET.get('date_from')
    if date_from:
        invoices = invoices.filter(data_wystawienia__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        invoices = invoices.filter(data_wystawienia__lte=date_to)
    
    search_query = request.GET.get('search')
    if search_query:
        invoices = invoices.filter(
            Q(numer__icontains=search_query) |
            Q(nabywca__nazwa__icontains=search_query)
        )
    
    # Calculate summary statistics
    stats = _calculate_invoice_stats(invoices)
    
    # Pagination
    paginator = Paginator(invoices.order_by('-data_wystawienia'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'status_choices': Faktura.STATUS_CHOICES,
        'current_filters': {
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to,
            'search': search_query,
        }
    }
    
    return render(request, 'faktury/enhanced_invoice_list.html', context)


@login_required
def enhanced_invoice_status_update(request, pk):
    """AJAX endpoint for updating invoice status"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    new_status = request.POST.get('status')
    
    if new_status not in dict(Faktura.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    try:
        old_status = faktura.status
        faktura.status = new_status
        
        # Handle payment amount for paid status
        if new_status == 'oplacona':
            kwota_oplacona = request.POST.get('kwota_oplacona')
            if kwota_oplacona:
                faktura.kwota_oplacona = Decimal(kwota_oplacona)
        
        faktura.save()
        
        # Log status change (if logging is implemented)
        _log_status_change(faktura, old_status, new_status, request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'Status faktury zmieniony na {faktura.get_status_display()}',
            'new_status': new_status,
            'new_status_display': faktura.get_status_display()
        })
        
    except Exception as e:
        logger.error(f"Error updating invoice status: {e}")
        return JsonResponse({'error': 'Błąd podczas aktualizacji statusu'}, status=500)


@login_required
def enhanced_contractor_create(request):
    """Enhanced contractor creation with NIP validation"""
    if request.method == 'POST':
        form = EnhancedKontrahentForm(request.POST)
        
        if form.is_valid():
            kontrahent = form.save(commit=False)
            kontrahent.user = request.user
            kontrahent.save()
            
            messages.success(request, f'Kontrahent {kontrahent.nazwa} został dodany.')
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'kontrahent': {
                        'id': kontrahent.id,
                        'nazwa': kontrahent.nazwa,
                        'nip': kontrahent.nip,
                    }
                })
            
            return redirect('enhanced_invoice_create')
    else:
        form = EnhancedKontrahentForm()
    
    context = {
        'form': form,
        'title': 'Nowy kontrahent'
    }
    
    return render(request, 'faktury/enhanced_contractor_form.html', context)


# Helper functions

def _generate_invoice_number(user, typ_dokumentu):
    """Generate next invoice number"""
    today = datetime.date.today()
    ostatnia_faktura = Faktura.objects.filter(
        user=user,
        data_wystawienia__year=today.year,
        data_wystawienia__month=today.month,
        typ_dokumentu=typ_dokumentu
    ).order_by('-numer').first()

    if ostatnia_faktura:
        try:
            ostatni_numer = int(ostatnia_faktura.numer.split('/')[1])
            return f"{typ_dokumentu}/{ostatni_numer + 1:02d}/{today.month:02d}/{today.year}"
        except (ValueError, IndexError):
            liczba_faktur = Faktura.objects.filter(
                user=user,
                data_wystawienia__year=today.year,
                data_wystawienia__month=today.month,
                typ_dokumentu=typ_dokumentu
            ).count()
            return f"{typ_dokumentu}/{liczba_faktur + 1:02d}/{today.month:02d}/{today.year}"
    else:
        return f"{typ_dokumentu}/01/{today.month:02d}/{today.year}"


def _setup_recurring_invoice(faktura, form_data):
    """Setup recurring invoice configuration"""
    from .models import FakturaCykliczna
    
    FakturaCykliczna.objects.create(
        faktura_wzorcowa=faktura,
        cykl=form_data['cykl'],
        data_poczatkowa=form_data['data_poczatkowa'],
        data_koncowa=form_data.get('data_koncowa'),
        aktywna=True
    )


def _calculate_invoice_totals(pozycje):
    """Calculate invoice totals"""
    totals = {
        'netto': Decimal('0.00'),
        'vat': Decimal('0.00'),
        'brutto': Decimal('0.00'),
    }
    
    for pozycja in pozycje:
        wartosc_netto = pozycja.ilosc * pozycja.cena_netto
        
        if pozycja.vat == 'zw':
            vat_rate = Decimal('0.00')
        else:
            vat_rate = Decimal(pozycja.vat) / 100
        
        wartosc_vat = wartosc_netto * vat_rate
        wartosc_brutto = wartosc_netto + wartosc_vat
        
        totals['netto'] += wartosc_netto
        totals['vat'] += wartosc_vat
        totals['brutto'] += wartosc_brutto
    
    return totals


def _get_compliance_rules(faktura):
    """Get compliance rules for invoice"""
    rules = []
    
    # NIP validation rule
    if faktura.nabywca and faktura.nabywca.czy_firma:
        if faktura.nabywca.nip:
            rules.append({
                'id': 'nip_validation',
                'name': 'Walidacja NIP',
                'description': 'NIP nabywcy jest prawidłowy',
                'status': 'compliant',
                'details': f'NIP: {faktura.nabywca.nip}'
            })
        else:
            rules.append({
                'id': 'nip_validation',
                'name': 'Walidacja NIP',
                'description': 'Brak NIP dla firmy',
                'status': 'non-compliant',
                'details': 'Firma musi mieć podany NIP'
            })
    
    # VAT compliance rule
    has_vat_items = faktura.pozycjafaktury_set.exclude(vat='zw').exists()
    if has_vat_items and not faktura.zwolnienie_z_vat:
        rules.append({
            'id': 'vat_compliance',
            'name': 'Zgodność VAT',
            'description': 'Faktura zawiera prawidłowe stawki VAT',
            'status': 'compliant'
        })
    elif faktura.zwolnienie_z_vat and faktura.powod_zwolnienia:
        rules.append({
            'id': 'vat_exemption',
            'name': 'Zwolnienie z VAT',
            'description': 'Prawidłowo określone zwolnienie z VAT',
            'status': 'compliant',
            'details': f'Powód: {faktura.get_powod_zwolnienia_display()}'
        })
    
    # Payment terms rule
    if faktura.termin_platnosci:
        if faktura.termin_platnosci >= faktura.data_wystawienia:
            rules.append({
                'id': 'payment_terms',
                'name': 'Termin płatności',
                'description': 'Termin płatności jest prawidłowy',
                'status': 'compliant'
            })
        else:
            rules.append({
                'id': 'payment_terms',
                'name': 'Termin płatności',
                'description': 'Termin płatności w przeszłości',
                'status': 'warning',
                'details': 'Termin płatności nie może być wcześniejszy niż data wystawienia'
            })
    
    return rules


def _get_status_history(faktura):
    """Get status change history for invoice"""
    # This would be implemented if status history tracking is added
    return []


def _log_status_change(faktura, old_status, new_status, user):
    """Log status change"""
    # This would be implemented if status change logging is added
    pass


def _calculate_invoice_stats(invoices):
    """Calculate invoice statistics"""
    stats = invoices.aggregate(
        total_count=Count('id'),
        total_value=Sum('pozycjafaktury__ilosc') or Decimal('0.00'),
    )
    
    # Status breakdown
    status_counts = {}
    for status_code, status_name in Faktura.STATUS_CHOICES:
        count = invoices.filter(status=status_code).count()
        status_counts[status_code] = {
            'name': status_name,
            'count': count
        }
    
    stats['status_counts'] = status_counts
    return stats


def _get_user_products(user):
    """Get user's products for quick selection"""
    from .models import Produkt
    return Produkt.objects.filter(user=user)[:10]  # Limit to 10 most recent