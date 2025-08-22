### views/task_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from faktury.models import ZadanieUzytkownika
from faktury.forms import ZadanieUzytkownikaForm

@login_required
def moje_zadania(request):
    zadania = ZadanieUzytkownika.objects.filter(user=request.user).order_by('termin_wykonania')
    return render(request, 'faktury/moje_zadania.html', {'zadania': zadania})

@login_required
def dodaj_zadanie_uzytkownika(request):
    if request.method == 'POST':
        form = ZadanieUzytkownikaForm(request.POST)
        if form.is_valid():
            zadanie = form.save(commit=False)
            zadanie.user = request.user
            zadanie.save()
            messages.success(request, "Zadanie zostało dodane.")
            return redirect('moje_zadania')
    else:
        form = ZadanieUzytkownikaForm()
    return render(request, 'faktury/dodaj_zadanie_uzytkownika.html', {'form': form})

@login_required
def edytuj_zadanie_uzytkownika(request, pk):
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk)
    if request.method == 'POST':
        form = ZadanieUzytkownikaForm(request.POST, instance=zadanie)
        if form.is_valid():
            form.save()
            messages.success(request, "Zadanie zostało zaktualizowane.")
            return redirect('moje_zadania')
    else:
        form = ZadanieUzytkownikaForm(instance=zadanie)
    return render(request, 'faktury/edytuj_zadanie_uzytkownika.html', {'form': form, 'zadanie': zadanie})

@login_required
def usun_zadanie_uzytkownika(request, pk):
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk)
    zadanie.delete()
    messages.success(request, "Zadanie zostało usunięte.")
    return redirect('moje_zadania')

@login_required
def oznacz_zadanie_uzytkownika_wykonane(request, pk):
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk)
    zadanie.wykonane = True
    zadanie.save()
    messages.success(request, "Zadanie zostało oznaczone jako wykonane.")
    return redirect('moje_zadania')

@login_required
def szczegoly_zadania_uzytkownika(request, pk):
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk)
    return render(request, 'faktury/szczegoly_zadania_uzytkownika.html', {'zadanie': zadanie})

@login_required
def twoje_sprawy(request):
    return render(request, 'faktury/twoje_sprawy.html')