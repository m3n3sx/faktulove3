"""
Company management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Firma
from ..forms import FirmaForm


@login_required
def dodaj_firme(request):
    """Add company view"""
    try:
        # Check if company already exists for this user
        firma = Firma.objects.get(user=request.user)
        return redirect('edytuj_firme')  # Redirect to edit if company exists
    except Firma.DoesNotExist:
        pass  # Continue if company doesn't exist

    if request.method == 'POST':
        form = FirmaForm(request.POST, request.FILES)
        if form.is_valid():
            firma = form.save(commit=False)
            firma.user = request.user
            firma.save()
            messages.success(request, "Dane firmy zostały dodane.")
            return redirect('panel_uzytkownika')
    else:
        form = FirmaForm()
    return render(request, 'faktury/dodaj_firme.html', {'form': form})


@login_required
def edytuj_firme(request):
    """Edit company view"""
    firma = get_object_or_404(Firma, user=request.user)
    if request.method == 'POST':
        form = FirmaForm(request.POST, request.FILES, instance=firma)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dane firmy zaktualizowane')
            return redirect('panel_uzytkownika')
    else:
        form = FirmaForm(instance=firma)
    return render(request, 'faktury/edytuj_firme.html', {'form': form})
