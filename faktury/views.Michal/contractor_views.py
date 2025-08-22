### views/contractor_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from faktury.models import Kontrahent
from faktury.forms import KontrahentForm
import csv
from django.http import HttpResponse

@login_required
def kontrahenci(request):
    kontrahenci_list = Kontrahent.objects.filter(user=request.user).order_by('nazwa')
    return render(request, 'faktury/kontrahenci.html', {'kontrahenci': kontrahenci_list})

@login_required
def dodaj_kontrahenta(request):
    if request.method == 'POST':
        form = KontrahentForm(request.POST)
        if form.is_valid():
            kontrahent = form.save(commit=False)
            kontrahent.user = request.user
            kontrahent.save()
            messages.success(request, "Kontrahent został dodany.")
            return redirect('kontrahenci')
    else:
        form = KontrahentForm()
    return render(request, 'faktury/dodaj_kontrahenta.html', {'form': form})

@login_required
def edytuj_kontrahenta(request, pk):
    kontrahent = get_object_or_404(Kontrahent, pk=pk)
    if request.method == 'POST':
        form = KontrahentForm(request.POST, instance=kontrahent)
        if form.is_valid():
            form.save()
            messages.success(request, "Dane kontrahenta zostały zaktualizowane.")
            return redirect('kontrahenci')
    else:
        form = KontrahentForm(instance=kontrahent)
    return render(request, 'faktury/edytuj_kontrahenta.html', {'form': form, 'kontrahent': kontrahent})

@login_required
def usun_kontrahenta(request, pk):
    kontrahent = get_object_or_404(Kontrahent, pk=pk)
    kontrahent.delete()
    messages.success(request, "Kontrahent został usunięty.")
    return redirect('kontrahenci')

@login_required
def import_kontrahenci(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        next(reader)  # Pominięcie nagłówka
        for row in reader:
            Kontrahent.objects.create(user=request.user, nazwa=row[0], nip=row[1], adres=row[2])
        messages.success(request, "Kontrahenci zostali zaimportowani.")
        return redirect('kontrahenci')
    return render(request, 'faktury/import_kontrahenci.html')

@login_required
def szczegoly_kontrahenta(request, pk):
    kontrahent = get_object_or_404(Kontrahent, pk=pk)
    return render(request, 'faktury/szczegoly_kontrahenta.html', {'kontrahent': kontrahent})