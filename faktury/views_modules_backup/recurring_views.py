"""
Recurring invoices management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from ..models import Faktura, FakturaCykliczna
from ..forms import FakturaCyklicznaForm
from ..services import generuj_fakture_cykliczna


@login_required
def lista_faktur_cyklicznych(request):
    """List recurring invoices for user"""
    cykle = FakturaCykliczna.objects.filter(
        oryginalna_faktura__user=request.user
    ).select_related('oryginalna_faktura').order_by('-data_utworzenia')
    
    # Calculate statistics
    aktywne = cykle.filter(aktywna=True).count()
    nieaktywne = cykle.filter(aktywna=False).count()
    do_generacji = cykle.filter(
        aktywna=True,
        nastepna_generacja__lte=timezone.now().date()
    ).count()
    
    context = {
        'cykle': cykle,
        'statystyki': {
            'aktywne': aktywne,
            'nieaktywne': nieaktywne,
            'do_generacji': do_generacji,
            'laczna_liczba': cykle.count()
        }
    }
    
    return render(request, 'faktury/lista_faktur_cyklicznych.html', context)


@login_required
def dodaj_cykl_faktur(request, faktura_id):
    """Create recurring cycle for invoice"""
    faktura = get_object_or_404(Faktura, pk=faktura_id, user=request.user)
    
    # Check if cycle already exists
    if FakturaCykliczna.objects.filter(oryginalna_faktura=faktura).exists():
        messages.error(request, 'Cykl dla tej faktury już istnieje.')
        return redirect('szczegoly_faktury', pk=faktura_id)
    
    if request.method == 'POST':
        form = FakturaCyklicznaForm(request.POST)
        if form.is_valid():
            cykl = form.save(commit=False)
            cykl.oryginalna_faktura = faktura
            
            # Set initial next generation date
            if not cykl.nastepna_generacja:
                cykl.nastepna_generacja = cykl.data_poczatkowa
            
            cykl.save()
            messages.success(request, f'Utworzono cykl faktury dla {faktura.numer}.')
            return redirect('lista_faktur_cyklicznych')
    else:
        # Pre-fill form with sensible defaults
        initial_data = {
            'data_poczatkowa': timezone.now().date(),
            'cykl': 'M',  # Monthly by default
        }
        form = FakturaCyklicznaForm(initial=initial_data)
    
    context = {
        'form': form,
        'faktura': faktura
    }
    return render(request, 'faktury/dodaj_cykl_faktur.html', context)


@login_required
def szczegoly_cyklu(request, cykl_id):
    """Recurring cycle details"""
    cykl = get_object_or_404(
        FakturaCykliczna,
        pk=cykl_id,
        oryginalna_faktura__user=request.user
    )
    
    # Get generated invoices
    faktury_wygenerowane = Faktura.objects.filter(
        faktura_cykliczna=cykl
    ).order_by('-data_wystawienia')
    
    context = {
        'cykl': cykl,
        'faktury_wygenerowane': faktury_wygenerowane
    }
    
    return render(request, 'faktury/szczegoly_cyklu.html', context)


@login_required
def edytuj_cykl(request, cykl_id):
    """Edit recurring cycle"""
    cykl = get_object_or_404(
        FakturaCykliczna,
        pk=cykl_id,
        oryginalna_faktura__user=request.user
    )
    
    if request.method == 'POST':
        form = FakturaCyklicznaForm(request.POST, instance=cykl)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cykl faktury został zaktualizowany.')
            return redirect('szczegoly_cyklu', cykl_id=cykl.id)
    else:
        form = FakturaCyklicznaForm(instance=cykl)
    
    context = {
        'form': form,
        'cykl': cykl
    }
    return render(request, 'faktury/edytuj_cykl.html', context)


@login_required
def usun_cykl(request, cykl_id):
    """Delete recurring cycle"""
    cykl = get_object_or_404(
        FakturaCykliczna,
        pk=cykl_id,
        oryginalna_faktura__user=request.user
    )
    
    if request.method == 'POST':
        cykl_numer = cykl.oryginalna_faktura.numer
        cykl.delete()
        messages.success(request, f'Cykl faktury {cykl_numer} został usunięty.')
        return redirect('lista_faktur_cyklicznych')
    
    context = {'cykl': cykl}
    return render(request, 'faktury/usun_cykl.html', context)


@login_required
def przelacz_aktywnosc_cyklu(request, cykl_id):
    """Toggle cycle active status"""
    cykl = get_object_or_404(
        FakturaCykliczna,
        pk=cykl_id,
        oryginalna_faktura__user=request.user
    )
    
    if request.method == 'POST':
        cykl.aktywna = not cykl.aktywna
        cykl.save()
        
        status = "aktywowany" if cykl.aktywna else "deaktywowany"
        messages.success(request, f'Cykl faktury został {status}.')
    
    return redirect('szczegoly_cyklu', cykl_id=cykl.id)


@login_required
def generuj_fakture_reczne(request, cykl_id):
    """Manually generate invoice from cycle"""
    cykl = get_object_or_404(
        FakturaCykliczna,
        pk=cykl_id,
        oryginalna_faktura__user=request.user
    )
    
    if request.method == 'POST':
        try:
            nowa_faktura = generuj_fakture_cykliczna(cykl)
            if nowa_faktura:
                messages.success(
                    request,
                    f'Wygenerowano fakturę {nowa_faktura.numer} z cyklu.'
                )
                return redirect('szczegoly_faktury', pk=nowa_faktura.id)
            else:
                messages.error(request, 'Nie można wygenerować faktury - sprawdź warunki cyklu.')
        except Exception as e:
            messages.error(request, f'Błąd podczas generowania faktury: {str(e)}')
    
    return redirect('szczegoly_cyklu', cykl_id=cykl.id)


@login_required
def zakoncz_cykl(request, cykl_id):
    """End recurring cycle"""
    cykl = get_object_or_404(
        FakturaCykliczna,
        pk=cykl_id,
        oryginalna_faktura__user=request.user
    )
    
    if request.method == 'POST':
        powod = request.POST.get('powod', 'Zakończony przez użytkownika')
        cykl.zakoncz_cykl(powod)
        messages.success(request, 'Cykl faktury został zakończony.')
        return redirect('lista_faktur_cyklicznych')
    
    context = {'cykl': cykl}
    return render(request, 'faktury/zakoncz_cykl.html', context)


@login_required
def podglad_nastepnej_faktury(request, cykl_id):
    """Preview next invoice in cycle"""
    cykl = get_object_or_404(
        FakturaCykliczna,
        pk=cykl_id,
        oryginalna_faktura__user=request.user
    )
    
    # Calculate what the next invoice would look like
    oryginalna = cykl.oryginalna_faktura
    
    # Mock data for preview
    today = timezone.now().date()
    data_sprzedazy = cykl.nastepna_generacja
    
    if oryginalna.termin_platnosci and oryginalna.data_sprzedazy:
        days_diff = (oryginalna.termin_platnosci - oryginalna.data_sprzedazy).days
        termin_platnosci = data_sprzedazy + timezone.timedelta(days=days_diff)
    else:
        termin_platnosci = data_sprzedazy + timezone.timedelta(days=14)
    
    prefix = "FV-CYK" if oryginalna.typ_faktury == 'sprzedaz' else "FK-CYK"
    nowy_numer = f"{prefix}/{cykl.liczba_cykli + 1:03d}/{timezone.now().year}/{oryginalna.numer}"
    
    # Create mock invoice object for preview
    mock_faktura = {
        'numer': nowy_numer,
        'data_wystawienia': today,
        'data_sprzedazy': data_sprzedazy,
        'termin_platnosci': termin_platnosci,
        'sprzedawca': oryginalna.sprzedawca,
        'nabywca': oryginalna.nabywca,
        'typ_faktury': oryginalna.typ_faktury,
        'pozycje': oryginalna.pozycjafaktury_set.all()
    }
    
    context = {
        'cykl': cykl,
        'mock_faktura': mock_faktura,
        'oryginalna': oryginalna
    }
    
    return render(request, 'faktury/podglad_nastepnej_faktury.html', context)


@login_required
def api_cykle_status(request):
    """API endpoint for cycle status information"""
    cykle = FakturaCykliczna.objects.filter(
        oryginalna_faktura__user=request.user,
        aktywna=True
    ).select_related('oryginalna_faktura')
    
    data = []
    for cykl in cykle:
        data.append({
            'id': cykl.id,
            'numer_oryginalnej': cykl.oryginalna_faktura.numer,
            'cykl': cykl.get_cykl_display(),
            'nastepna_generacja': cykl.nastepna_generacja.isoformat(),
            'dni_do_generacji': cykl.dni_do_nastepnej_generacji,
            'czy_mozna_generowac': cykl.czy_mozna_generowac,
            'liczba_cykli': cykl.liczba_cykli
        })
    
    return JsonResponse({'cykle': data})
