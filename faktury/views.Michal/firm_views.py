### views/firm_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from faktury.models import Firma
from faktury.forms import FirmaForm

@login_required
def dodaj_firme(request):
    if request.method == 'POST':
        form = FirmaForm(request.POST)
        if form.is_valid():
            firma = form.save(commit=False)
            firma.user = request.user
            firma.save()
            messages.success(request, "Firma została dodana.")
            return redirect('panel_uzytkownika')
    else:
        form = FirmaForm()
    return render(request, 'faktury/dodaj_firme.html', {'form': form})

@login_required
def edytuj_firme(request, pk):
    firma = get_object_or_404(Firma, pk=pk)
    if request.method == 'POST':
        form = FirmaForm(request.POST, instance=firma)
        if form.is_valid():
            form.save()
            messages.success(request, "Dane firmy zostały zaktualizowane.")
            return redirect('panel_uzytkownika')
    else:
        form = FirmaForm(instance=firma)
    return render(request, 'faktury/edytuj_firme.html', {'form': form, 'firma': firma})

@login_required
def usun_firme(request, pk):
    firma = get_object_or_404(Firma, pk=pk)
    firma.delete()
    messages.success(request, "Firma została usunięta.")
    return redirect('panel_uzytkownika')