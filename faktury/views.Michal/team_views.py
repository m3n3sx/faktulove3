### views/team_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from faktury.models import Zespol, Firma, CzlonekZespolu
from faktury.forms import ZespolForm, CzlonekZespoluFormSet

@login_required
def lista_zespolow(request):
    firma = get_object_or_404(Firma, user=request.user)
    zespoly = firma.zespoly.all()
    return render(request, 'faktury/lista_zespolow.html', {'zespoly': zespoly})

@login_required
def dodaj_zespol(request):
    if request.method == 'POST':
        form = ZespolForm(request.POST)
        if form.is_valid():
            zespol = form.save(commit=False)
            zespol.firma = get_object_or_404(Firma, user=request.user)
            zespol.save()
            messages.success(request, "Zespół został dodany.")
            return redirect('lista_zespolow')
    else:
        form = ZespolForm()
    return render(request, 'faktury/dodaj_zespol.html', {'form': form})

@login_required
def szczegoly_zespolu(request, zespol_id):
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    czlonkowie = zespol.czlonkowie.all()
    return render(request, 'faktury/szczegoly_zespolu.html', {'zespol': zespol, 'czlonkowie': czlonkowie})

@login_required
def edytuj_zespol(request, zespol_id):
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    if request.method == 'POST':
        form = ZespolForm(request.POST, instance=zespol)
        if form.is_valid():
            form.save()
            messages.success(request, "Zespół został zaktualizowany.")
            return redirect('lista_zespolow')
    else:
        form = ZespolForm(instance=zespol)
    return render(request, 'faktury/edytuj_zespol.html', {'form': form, 'zespol': zespol})

@login_required
def usun_zespol(request, zespol_id):
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    zespol.delete()
    messages.success(request, "Zespół został usunięty.")
    return redirect('lista_zespolow')
