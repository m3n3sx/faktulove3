### views/invoice_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from faktury.models import Faktura, Firma
from faktury.forms import FakturaForm, PozycjaFakturyFormSet

@login_required
def faktury_sprzedaz(request):
    faktury = Faktura.objects.filter(typ_faktury='sprzedaz')
    return render(request, 'faktury/faktury_sprzedaz.html', {'faktury': faktury})

@login_required
def faktury_koszt(request):
    faktury = Faktura.objects.filter(typ_faktury='koszt')
    return render(request, 'faktury/faktury_koszt.html', {'faktury': faktury})

@login_required
def dodaj_fakture_sprzedaz(request):
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Uzupełnij dane firmy przed wystawieniem faktury.")
        return redirect('dodaj_firme')

    if request.method == 'POST':
        faktura_form = FakturaForm(request.POST)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')

        if faktura_form.is_valid() and pozycje_formset.is_valid():
            faktura = faktura_form.save(commit=False)
            faktura.user = request.user
            faktura.typ_faktury = 'sprzedaz'
            faktura.sprzedawca = firma
            faktura.save()
            pozycje_formset.instance = faktura
            pozycje_formset.save()
            messages.success(request, "Faktura została dodana.")
            return redirect('panel_uzytkownika')
    else:
        faktura_form = FakturaForm()
        pozycje_formset = PozycjaFakturyFormSet(prefix='pozycje')

    return render(request, 'faktury/dodaj_fakture.html', {'faktura_form': faktura_form, 'pozycje_formset': pozycje_formset})

@login_required
def dodaj_fakture_koszt(request):
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Uzupełnij dane firmy przed wystawieniem faktury kosztowej.")
        return redirect('dodaj_firme')

    if request.method == 'POST':
        faktura_form = FakturaForm(request.POST)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')

        if faktura_form.is_valid() and pozycje_formset.is_valid():
            faktura = faktura_form.save(commit=False)
            faktura.user = request.user
            faktura.typ_faktury = 'koszt'
            faktura.sprzedawca = firma
            faktura.save()
            pozycje_formset.instance = faktura
            pozycje_formset.save()
            messages.success(request, "Faktura kosztowa została dodana.")
            return redirect('panel_uzytkownika')
    else:
        faktura_form = FakturaForm()
        pozycje_formset = PozycjaFakturyFormSet(prefix='pozycje')

    return render(request, 'faktury/dodaj_fakture_koszt.html', {'faktura_form': faktura_form, 'pozycje_formset': pozycje_formset})

@login_required
def edytuj_fakture(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk)
    if request.method == 'POST':
        faktura_form = FakturaForm(request.POST, instance=faktura)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, instance=faktura, prefix='pozycje')
        
        if faktura_form.is_valid() and pozycje_formset.is_valid():
            faktura_form.save()
            pozycje_formset.save()
            messages.success(request, "Faktura została zaktualizowana.")
            return redirect('panel_uzytkownika')
    else:
        faktura_form = FakturaForm(instance=faktura)
        pozycje_formset = PozycjaFakturyFormSet(instance=faktura, prefix='pozycje')
    
    return render(request, 'faktury/edytuj_fakture.html', {'faktura_form': faktura_form, 'pozycje_formset': pozycje_formset, 'faktura': faktura})

@login_required
def usun_fakture(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk)
    faktura.delete()
    messages.success(request, "Faktura została usunięta.")
    return redirect('panel_uzytkownika')

@login_required
def szczegoly_faktury(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk)
    return render(request, 'faktury/szczegoly_faktury.html', {'faktura': faktura})

@login_required
def wyslij_fakture_mailem(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk)
    subject = f"Faktura {faktura.numer}"
    message = f"Załączam fakturę {faktura.numer} do opłacenia."
    recipient = faktura.kontrahent.email
    send_mail(subject, message, 'noreply@twojadomena.com', [recipient])
    messages.success(request, "Faktura została wysłana e-mailem.")
    return redirect('szczegoly_faktury', pk=pk)

@login_required
def wyslij_przypomnienie(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk)
    subject = f"Przypomnienie o płatności: Faktura {faktura.numer}"
    message = f"To przypomnienie o zaległej płatności za fakturę {faktura.numer}."
    recipient = faktura.kontrahent.email
    send_mail(subject, message, 'noreply@twojadomena.com', [recipient])
    messages.success(request, "Przypomnienie o fakturze zostało wysłane.")
    return redirect('szczegoly_faktury', pk=pk)