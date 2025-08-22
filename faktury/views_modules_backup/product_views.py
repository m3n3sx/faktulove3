"""
Product management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from ..models import Produkt
from ..forms import ProduktForm
from ..decorators import ajax_login_required


@login_required
def produkty(request):
    """List products view"""
    produkty_list = Produkt.objects.filter(user=request.user).select_related('user').order_by('nazwa')
    return render(request, 'faktury/produkty.html', {'produkty': produkty_list})


@login_required
def dodaj_produkt(request):
    """Add product view"""
    if request.method == 'POST':
        form = ProduktForm(request.POST)
        if form.is_valid():
            produkt = form.save(commit=False)
            produkt.user = request.user
            produkt.save()
            messages.success(request, 'Produkt został dodany')
            return redirect('panel_uzytkownika')
    else:
        form = ProduktForm()

    return render(request, 'faktury/dodaj_produkt.html', {'form': form})


@login_required
def edytuj_produkt(request, pk):
    """Edit product view"""
    produkt = get_object_or_404(Produkt, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProduktForm(request.POST, instance=produkt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produkt zaktualizowany')
            return redirect('panel_uzytkownika')
    else:
        form = ProduktForm(instance=produkt)
    return render(request, 'faktury/edytuj_produkt.html', {'form': form})


@login_required
def usun_produkt(request, pk):
    """Delete product view"""
    produkt = get_object_or_404(Produkt, pk=pk, user=request.user)
    if request.method == 'POST':
        produkt.delete()
        messages.success(request, 'Produkt został usunięty.')
        return redirect('panel_uzytkownika')
    return render(request, 'faktury/usun_produkt.html', {'produkt': produkt})


@ajax_login_required
def dodaj_produkt_ajax(request):
    """Add product via AJAX"""
    if request.method == 'POST':
        try:
            form = ProduktForm(request.POST)
            if form.is_valid():
                produkt = form.save(commit=False)
                produkt.user = request.user
                produkt.save()
                return JsonResponse({
                    'id': produkt.pk, 
                    'nazwa': produkt.nazwa, 
                    'cena_netto': str(produkt.cena_netto), 
                    'vat': produkt.vat, 
                    'jednostka': produkt.jednostka
                })
            else:
                raise ValidationError(form.errors)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Wystąpił błąd: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def pobierz_dane_produktu(request):
    """Get product data via AJAX"""
    produkt_id = request.GET.get('id')
    if not produkt_id:
        return JsonResponse({'error': 'Missing product ID'}, status=400)
    
    try:
        produkt = Produkt.objects.get(pk=produkt_id, user=request.user)
        return JsonResponse({
            'nazwa': produkt.nazwa,
            'jednostka': produkt.jednostka,
            'cena_netto': str(produkt.cena_netto),
            'vat': produkt.vat,
        })
    except Produkt.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)
