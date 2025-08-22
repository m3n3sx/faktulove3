### views/product_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from faktury.models import Produkt
from faktury.forms import ProduktForm

@login_required
def produkty(request):
    produkty_list = Produkt.objects.filter(user=request.user).order_by('nazwa')
    return render(request, 'faktury/produkty.html', {'produkty': produkty_list})

@login_required
def dodaj_produkt(request):
    if request.method == 'POST':
        form = ProduktForm(request.POST)
        if form.is_valid():
            produkt = form.save(commit=False)
            produkt.user = request.user
            produkt.save()
            messages.success(request, "Produkt został dodany.")
            return redirect('produkty')
    else:
        form = ProduktForm()
    return render(request, 'faktury/dodaj_produkt.html', {'form': form})

@login_required
def edytuj_produkt(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)
    if request.method == 'POST':
        form = ProduktForm(request.POST, instance=produkt)
        if form.is_valid():
            form.save()
            messages.success(request, "Produkt został zaktualizowany.")
            return redirect('produkty')
    else:
        form = ProduktForm(instance=produkt)
    return render(request, 'faktury/edytuj_produkt.html', {'form': form, 'produkt': produkt})

@login_required
def usun_produkt(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)
    produkt.delete()
    messages.success(request, "Produkt został usunięty.")
    return redirect('produkty')