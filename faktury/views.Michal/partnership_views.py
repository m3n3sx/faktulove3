### views/partnership_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from faktury.models import Partnerstwo
from faktury.forms import PartnerstwoForm

@login_required
def lista_partnerstw(request):
    partnerstwa = Partnerstwo.objects.filter(user=request.user)
    return render(request, 'faktury/lista_partnerstw.html', {'partnerstwa': partnerstwa})

@login_required
def dodaj_partnerstwo(request):
    if request.method == 'POST':
        form = PartnerstwoForm(request.POST)
        if form.is_valid():
            partnerstwo = form.save(commit=False)
            partnerstwo.user = request.user
            partnerstwo.save()
            messages.success(request, "Partnerstwo zostało dodane.")
            return redirect('lista_partnerstw')
    else:
        form = PartnerstwoForm()
    return render(request, 'faktury/dodaj_partnerstwo.html', {'form': form})

@login_required
def edytuj_partnerstwo(request, pk):
    partnerstwo = get_object_or_404(Partnerstwo, pk=pk)
    if request.method == 'POST':
        form = PartnerstwoForm(request.POST, instance=partnerstwo)
        if form.is_valid():
            form.save()
            messages.success(request, "Partnerstwo zostało zaktualizowane.")
            return redirect('lista_partnerstw')
    else:
        form = PartnerstwoForm(instance=partnerstwo)
    return render(request, 'faktury/edytuj_partnerstwo.html', {'form': form, 'partnerstwo': partnerstwo})

@login_required
def usun_partnerstwo(request, pk):
    partnerstwo = get_object_or_404(Partnerstwo, pk=pk)
    partnerstwo.delete()
    messages.success(request, "Partnerstwo zostało usunięte.")
    return redirect('lista_partnerstw')
