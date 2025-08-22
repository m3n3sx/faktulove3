"""
Contractor management views
"""
import json
import requests
import xml.etree.ElementTree as ET
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings

from ..models import Kontrahent, Firma, Faktura
from ..forms import KontrahentForm
from ..decorators import ajax_login_required


@login_required
def kontrahenci(request):
    """List contractors view"""
    kontrahenci_list = Kontrahent.objects.filter(user=request.user).select_related('user').order_by('nazwa')
    return render(request, 'faktury/kontrahenci.html', {'kontrahenci': kontrahenci_list})


@login_required
def dodaj_kontrahenta(request):
    """Add contractor view"""
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


@ajax_login_required
def dodaj_kontrahenta_ajax(request):
    """Add contractor via AJAX"""
    if request.method == 'GET':
        nip = request.GET.get('nip')
        nazwa = request.GET.get('nazwa')
        ulica = request.GET.get('ulica')
        numer_domu = request.GET.get('numer_domu')
        numer_mieszkania = request.GET.get('numer_mieszkania')
        kod_pocztowy = request.GET.get('kod_pocztowy')
        miejscowosc = request.GET.get('miejscowosc')
        kraj = request.GET.get('kraj')
        czy_firma_str = request.GET.get('czy_firma', 'true')
        czy_firma = czy_firma_str.lower() == 'true'

        kontrahent = Kontrahent(
            user=request.user,
            nip=nip,
            nazwa=nazwa,
            ulica=ulica,
            numer_domu=numer_domu,
            numer_mieszkania=numer_mieszkania,
            kod_pocztowy=kod_pocztowy,
            miejscowosc=miejscowosc,
            kraj=kraj,
            czy_firma=czy_firma
        )
        try:
            kontrahent.save()
            return JsonResponse({'id': kontrahent.id, 'nazwa': kontrahent.nazwa})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def pobierz_dane_kontrahenta(request):
    """Get contractor data via AJAX"""
    kontrahent_id = request.GET.get('id')
    if not kontrahent_id:
        return JsonResponse({'error': 'Brak parametru ID.'}, status=400)
    try:
        kontrahent = Kontrahent.objects.get(pk=kontrahent_id, user=request.user)
        return JsonResponse({
            'nazwa': kontrahent.nazwa,
            'nip': kontrahent.nip,
            'regon': kontrahent.regon,
            'ulica': kontrahent.ulica,
            'numer_domu': kontrahent.numer_domu,
            'numer_mieszkania': kontrahent.numer_mieszkania,
            'kod_pocztowy': kontrahent.kod_pocztowy,
            'miejscowosc': kontrahent.miejscowosc,
            'kraj': kontrahent.kraj,
            'czy_firma': kontrahent.czy_firma,
        })
    except Kontrahent.DoesNotExist:
        return JsonResponse({'error': 'Nie znaleziono kontrahenta.'}, status=404)


@login_required
def edytuj_kontrahenta(request, pk):
    """Edit contractor view"""
    kontrahent = get_object_or_404(Kontrahent, pk=pk, user=request.user)
    if request.method == 'POST':
        form = KontrahentForm(request.POST, instance=kontrahent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kontrahent zaktualizowany')
            return redirect('panel_uzytkownika')
    else:
        form = KontrahentForm(instance=kontrahent)
    return render(request, 'faktury/edytuj_kontrahenta.html', {'form': form})


@login_required
def usun_kontrahenta(request, pk):
    """Delete contractor view"""
    kontrahent = get_object_or_404(Kontrahent, pk=pk, user=request.user)
    if request.method == "POST":
        kontrahent.delete()
        messages.success(request, 'Kontrahent został usunięty.')
        return redirect('panel_uzytkownika')
    return render(request, 'faktury/usun_kontrahenta.html', {'kontrahent': kontrahent})


@login_required
def szczegoly_kontrahenta(request, pk):
    """Contractor details view"""
    kontrahent = get_object_or_404(Kontrahent, pk=pk, user=request.user)
    faktury = Faktura.objects.filter(nabywca=kontrahent).select_related('sprzedawca').prefetch_related('pozycjafaktury_set').order_by('-data_wystawienia')
    return render(request, 'faktury/szczegoly_kontrahenta.html', {
        'kontrahent': kontrahent, 
        'faktury': faktury
    })


@login_required
def pobierz_dane_z_gus(request):
    """
    Fetch company data from GUS API based on NIP number.
    Uses API key from settings.py.
    """
    nip = request.GET.get('nip')
    if not nip:
        return JsonResponse({'error': 'Brak numeru NIP.'}, status=400)

    url = 'https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc/ajax/DaneSzukajPodmioty'
    headers = {
        'Content-Type': 'application/json',
        'sid': settings.GUS_API_KEY
    }
    payload = {
        'jestWojewodztwo': False,
        'pParametryWyszukiwania': {
            'Nip': nip,
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data_list = response.json()

        if data_list and isinstance(data_list, list) and len(data_list) > 0:
            data = data_list[0]
            if data:
                return JsonResponse({
                    'nazwa': data.get('Nazwa'),
                    'ulica': data.get('Ulica', ''),
                    'numer_domu': data.get('NrNieruchomosci', ''),
                    'numer_mieszkania': data.get('NrLokalu', ''),
                    'kod_pocztowy': data.get('KodPocztowy', ''),
                    'miejscowosc': data.get('Miejscowosc', ''),
                    'regon': data.get("Regon", ''),
                    'kraj': 'Polska'
                })
            else:
                return JsonResponse({'error': 'Nie znaleziono firmy o podanym numerze NIP.'}, status=404)
        else:
            return JsonResponse({'error': 'Nieprawidłowa odpowiedź z API GUS.'}, status=500)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Błąd komunikacji z API GUS: {e}'}, status=500)
    except (KeyError, IndexError, json.JSONDecodeError, TypeError) as e:
        return JsonResponse({'error': f'Błąd parsowania danych z API GUS: {e}'}, status=500)
