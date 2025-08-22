"""
Partnership management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

from ..models import Firma, Partnerstwo, Faktura
from ..forms import PartnerstwoForm
from ..services import sprawdz_partnerstwa_auto_ksiegowanie


@login_required
def lista_partnerstw(request):
    """List partnerships for user's company"""
    try:
        firma = Firma.objects.get(user=request.user)
        
        # Get partnerships where user's company is involved
        partnerstwa = Partnerstwo.objects.filter(
            Q(firma1=firma) | Q(firma2=firma)
        ).select_related('firma1', 'firma2').order_by('-data_utworzenia')
        
        # Get statistics for each partnership
        partnership_stats = []
        for partnerstwo in partnerstwa:
            other_company = partnerstwo.firma2 if partnerstwo.firma1 == firma else partnerstwo.firma1
            
            # Count invoices
            faktury_wyslane = Faktura.objects.filter(
                sprzedawca=firma,
                nabywca__user=other_company.user,
                typ_faktury='sprzedaz'
            ).count()
            
            faktury_otrzymane = Faktura.objects.filter(
                sprzedawca=other_company,
                nabywca__user=request.user,
                typ_faktury='koszt'
            ).count()
            
            partnership_stats.append({
                'partnerstwo': partnerstwo,
                'other_company': other_company,
                'faktury_wyslane': faktury_wyslane,
                'faktury_otrzymane': faktury_otrzymane
            })
        
        context = {
            'partnership_stats': partnership_stats,
            'firma': firma
        }
        
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw dodaj dane swojej firmy.")
        return redirect('dodaj_firme')
    
    return render(request, 'faktury/lista_partnerstw.html', context)


@login_required
def dodaj_partnerstwo(request):
    """Add new partnership"""
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw dodaj dane swojej firmy.")
        return redirect('dodaj_firme')
    
    if request.method == 'POST':
        form = PartnerstwoForm(request.POST)
        if form.is_valid():
            partnerstwo = form.save(commit=False)
            partnerstwo.firma1 = firma
            
            # Check if partnership already exists
            existing = Partnerstwo.objects.filter(
                Q(firma1=firma, firma2=partnerstwo.firma2) |
                Q(firma1=partnerstwo.firma2, firma2=firma)
            ).first()
            
            if existing:
                messages.error(request, "Partnerstwo z tą firmą już istnieje.")
                return render(request, 'faktury/dodaj_partnerstwo.html', {'form': form})
            
            if partnerstwo.firma2 == firma:
                messages.error(request, "Nie możesz utworzyć partnerstwa z własną firmą.")
                return render(request, 'faktury/dodaj_partnerstwo.html', {'form': form})
            
            partnerstwo.save()
            messages.success(request, f'Partnerstwo z firmą {partnerstwo.firma2.nazwa} zostało utworzone.')
            return redirect('lista_partnerstw')
    else:
        form = PartnerstwoForm()
        # Filter out user's own company
        form.fields['firma2'].queryset = Firma.objects.exclude(user=request.user)
    
    return render(request, 'faktury/dodaj_partnerstwo.html', {'form': form})


@login_required
def edytuj_partnerstwo(request, partnerstwo_id):
    """Edit partnership"""
    try:
        firma = Firma.objects.get(user=request.user)
        partnerstwo = get_object_or_404(
            Partnerstwo, 
            Q(firma1=firma) | Q(firma2=firma),
            pk=partnerstwo_id
        )
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw dodaj dane swojej firmy.")
        return redirect('dodaj_firme')
    
    if request.method == 'POST':
        form = PartnerstwoForm(request.POST, instance=partnerstwo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partnerstwo zostało zaktualizowane.')
            return redirect('lista_partnerstw')
    else:
        form = PartnerstwoForm(instance=partnerstwo)
        # Don't allow changing companies
        form.fields['firma2'].widget.attrs['readonly'] = True
    
    return render(request, 'faktury/edytuj_partnerstwo.html', {
        'form': form, 
        'partnerstwo': partnerstwo
    })


@login_required
def usun_partnerstwo(request, partnerstwo_id):
    """Delete partnership"""
    try:
        firma = Firma.objects.get(user=request.user)
        partnerstwo = get_object_or_404(
            Partnerstwo, 
            Q(firma1=firma) | Q(firma2=firma),
            pk=partnerstwo_id
        )
    except Firma.DoesNotExist:
        messages.error(request, "Nie znaleziono firmy.")
        return redirect('lista_partnerstw')
    
    if request.method == 'POST':
        partner_name = partnerstwo.firma2.nazwa if partnerstwo.firma1 == firma else partnerstwo.firma1.nazwa
        partnerstwo.delete()
        messages.success(request, f'Partnerstwo z firmą {partner_name} zostało usunięte.')
        return redirect('lista_partnerstw')
    
    return render(request, 'faktury/usun_partnerstwo.html', {'partnerstwo': partnerstwo})


@login_required
def szczegoly_partnerstwa(request, partnerstwo_id):
    """Partnership details view"""
    try:
        firma = Firma.objects.get(user=request.user)
        partnerstwo = get_object_or_404(
            Partnerstwo, 
            Q(firma1=firma) | Q(firma2=firma),
            pk=partnerstwo_id
        )
    except Firma.DoesNotExist:
        messages.error(request, "Nie znaleziono firmy.")
        return redirect('lista_partnerstw')
    
    other_company = partnerstwo.firma2 if partnerstwo.firma1 == firma else partnerstwo.firma1
    
    # Get invoices related to this partnership
    faktury_wyslane = Faktura.objects.filter(
        sprzedawca=firma,
        nabywca__user=other_company.user,
        typ_faktury='sprzedaz'
    ).select_related('nabywca').order_by('-data_wystawienia')[:10]
    
    faktury_otrzymane = Faktura.objects.filter(
        sprzedawca=other_company,
        nabywca__user=request.user,
        typ_faktury='koszt'
    ).select_related('sprzedawca').order_by('-data_wystawienia')[:10]
    
    context = {
        'partnerstwo': partnerstwo,
        'other_company': other_company,
        'faktury_wyslane': faktury_wyslane,
        'faktury_otrzymane': faktury_otrzymane,
        'firma': firma
    }
    
    return render(request, 'faktury/szczegoly_partnerstwa.html', context)


@login_required
def uruchom_auto_ksiegowanie(request):
    """Manually trigger auto-accounting for pending invoices"""
    if request.method == 'POST':
        try:
            count = sprawdz_partnerstwa_auto_ksiegowanie(request.user)
            if count > 0:
                messages.success(
                    request, 
                    f'Pomyślnie przetworzono {count} faktur w auto-księgowaniu.'
                )
            else:
                messages.info(request, 'Brak faktur do auto-księgowania.')
        except Exception as e:
            messages.error(request, f'Błąd podczas auto-księgowania: {str(e)}')
    
    return redirect('lista_partnerstw')


@login_required
def przelacz_auto_ksiegowanie(request, partnerstwo_id):
    """Toggle auto-accounting for partnership"""
    try:
        firma = Firma.objects.get(user=request.user)
        partnerstwo = get_object_or_404(
            Partnerstwo, 
            Q(firma1=firma) | Q(firma2=firma),
            pk=partnerstwo_id
        )
        
        partnerstwo.auto_ksiegowanie = not partnerstwo.auto_ksiegowanie
        partnerstwo.save()
        
        status = "włączone" if partnerstwo.auto_ksiegowanie else "wyłączone"
        messages.success(request, f'Auto-księgowanie zostało {status}.')
        
    except Firma.DoesNotExist:
        messages.error(request, "Nie znaleziono firmy.")
    
    return redirect('lista_partnerstw')
