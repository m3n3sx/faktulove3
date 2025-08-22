"""
Calendar and scheduling views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json

from ..models import Faktura, ZadanieUzytkownika, FakturaCykliczna, Wiadomosc
from ..notifications.models import Notification


@login_required
def kalendarz(request):
    """Main calendar view"""
    # Get current month/year from request or use current
    try:
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month
    
    # Calculate date ranges
    current_date = datetime(year, month, 1).date()
    next_month = current_date.replace(day=28) + timedelta(days=4)
    next_month = next_month - timedelta(days=next_month.day - 1)
    prev_month = (current_date - timedelta(days=1)).replace(day=1)
    
    context = {
        'current_date': current_date,
        'next_month': next_month,
        'prev_month': prev_month,
        'year': year,
        'month': month
    }
    
    return render(request, 'faktury/kalendarz.html', context)


@login_required
def get_events(request):
    """API endpoint for calendar events"""
    # Get date range from request
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if not start_date or not end_date:
        return JsonResponse({'error': 'Start and end dates required'}, status=400)
    
    try:
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    events = []
    
    # Invoice events
    faktury = Faktura.objects.filter(
        user=request.user,
        data_wystawienia__range=[start_date, end_date]
    ).select_related('nabywca', 'sprzedawca')
    
    for faktura in faktury:
        events.append({
            'id': f'faktura_{faktura.id}',
            'title': f'Faktura {faktura.numer}',
            'start': faktura.data_wystawienia.isoformat(),
            'url': f'/faktury/szczegoly/{faktura.id}/',
            'backgroundColor': '#3498db',
            'borderColor': '#2980b9',
            'textColor': 'white',
            'extendedProps': {
                'type': 'faktura',
                'status': faktura.status,
                'suma': str(faktura.suma_brutto),
                'nabywca': faktura.nabywca.nazwa if faktura.nabywca else 'Brak'
            }
        })
    
    # Payment deadlines
    terminy_platnosci = Faktura.objects.filter(
        user=request.user,
        termin_platnosci__range=[start_date, end_date],
        status__in=['wystawiona', 'wyslana']
    ).select_related('nabywca')
    
    for faktura in terminy_platnosci:
        color = '#e74c3c' if faktura.termin_platnosci < timezone.now().date() else '#f39c12'
        
        events.append({
            'id': f'termin_{faktura.id}',
            'title': f'Termin płatności: {faktura.numer}',
            'start': faktura.termin_platnosci.isoformat(),
            'url': f'/faktury/szczegoly/{faktura.id}/',
            'backgroundColor': color,
            'borderColor': color,
            'textColor': 'white',
            'extendedProps': {
                'type': 'termin_platnosci',
                'overdue': faktura.termin_platnosci < timezone.now().date(),
                'suma': str(faktura.suma_brutto),
                'nabywca': faktura.nabywca.nazwa if faktura.nabywca else 'Brak'
            }
        })
    
    # User tasks
    zadania = ZadanieUzytkownika.objects.filter(
        user=request.user,
        termin_wykonania__range=[start_date, end_date]
    )
    
    for zadanie in zadania:
        color = '#27ae60' if zadanie.wykonane else '#9b59b6'
        
        events.append({
            'id': f'zadanie_{zadanie.id}',
            'title': zadanie.tytul,
            'start': zadanie.termin_wykonania.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'textColor': 'white',
            'extendedProps': {
                'type': 'zadanie',
                'wykonane': zadanie.wykonane,
                'opis': zadanie.opis
            }
        })
    
    # Recurring invoice generations
    cykle = FakturaCykliczna.objects.filter(
        oryginalna_faktura__user=request.user,
        aktywna=True,
        nastepna_generacja__range=[start_date, end_date]
    ).select_related('oryginalna_faktura')
    
    for cykl in cykle:
        events.append({
            'id': f'cykl_{cykl.id}',
            'title': f'Generacja: {cykl.oryginalna_faktura.numer}',
            'start': cykl.nastepna_generacja.isoformat(),
            'backgroundColor': '#17a2b8',
            'borderColor': '#138496',
            'textColor': 'white',
            'extendedProps': {
                'type': 'cykl',
                'cykl_nazwa': cykl.get_cykl_display(),
                'numer_cyklu': cykl.liczba_cykli + 1
            }
        })
    
    return JsonResponse(events, safe=False)


@login_required
def dashboard_kalendarza(request):
    """Calendar dashboard with summary"""
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = today.replace(day=1)
    next_month = month_start.replace(day=28) + timedelta(days=4)
    month_end = next_month - timedelta(days=next_month.day)
    
    # Today's events
    dzisiejsze_faktury = Faktura.objects.filter(
        user=request.user,
        data_wystawienia=today
    ).count()
    
    dzisiejsze_terminy = Faktura.objects.filter(
        user=request.user,
        termin_platnosci=today,
        status__in=['wystawiona', 'wyslana']
    ).count()
    
    dzisiejsze_zadania = ZadanieUzytkownika.objects.filter(
        user=request.user,
        termin_wykonania=today,
        wykonane=False
    ).count()
    
    # This week's summary
    tygodniowe_faktury = Faktura.objects.filter(
        user=request.user,
        data_wystawienia__range=[week_start, week_end]
    ).count()
    
    tygodniowe_terminy = Faktura.objects.filter(
        user=request.user,
        termin_platnosci__range=[week_start, week_end],
        status__in=['wystawiona', 'wyslana']
    ).count()
    
    # Overdue payments
    przeterminowane = Faktura.objects.filter(
        user=request.user,
        termin_platnosci__lt=today,
        status__in=['wystawiona', 'wyslana']
    ).count()
    
    # Upcoming recurring invoices
    nadchodzace_cykle = FakturaCykliczna.objects.filter(
        oryginalna_faktura__user=request.user,
        aktywna=True,
        nastepna_generacja__range=[today, today + timedelta(days=7)]
    ).select_related('oryginalna_faktura')
    
    # Recent notifications
    ostatnie_powiadomienia = Notification.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:5]
    
    context = {
        'dzisiaj': {
            'faktury': dzisiejsze_faktury,
            'terminy': dzisiejsze_terminy,
            'zadania': dzisiejsze_zadania
        },
        'tydzien': {
            'faktury': tygodniowe_faktury,
            'terminy': tygodniowe_terminy
        },
        'przeterminowane': przeterminowane,
        'nadchodzace_cykle': nadchodzace_cykle,
        'ostatnie_powiadomienia': ostatnie_powiadomienia,
        'today': today
    }
    
    return render(request, 'faktury/dashboard_kalendarza.html', context)


@login_required
def dodaj_wydarzenie(request):
    """Add new calendar event (task)"""
    if request.method == 'POST':
        tytul = request.POST.get('tytul', '').strip()
        opis = request.POST.get('opis', '').strip()
        termin = request.POST.get('termin')
        
        if not tytul or not termin:
            messages.error(request, 'Tytuł i termin są wymagane.')
            return redirect('kalendarz')
        
        try:
            termin_date = datetime.strptime(termin, '%Y-%m-%d').date()
            
            ZadanieUzytkownika.objects.create(
                user=request.user,
                tytul=tytul,
                opis=opis,
                termin_wykonania=termin_date
            )
            
            messages.success(request, 'Wydarzenie zostało dodane do kalendarza.')
            
        except ValueError:
            messages.error(request, 'Nieprawidłowy format daty.')
    
    return redirect('kalendarz')


@login_required
def edytuj_wydarzenie(request, zadanie_id):
    """Edit calendar event (task)"""
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=zadanie_id, user=request.user)
    
    if request.method == 'POST':
        tytul = request.POST.get('tytul', '').strip()
        opis = request.POST.get('opis', '').strip()
        termin = request.POST.get('termin')
        wykonane = request.POST.get('wykonane') == 'on'
        
        if not tytul or not termin:
            messages.error(request, 'Tytuł i termin są wymagane.')
            return redirect('kalendarz')
        
        try:
            termin_date = datetime.strptime(termin, '%Y-%m-%d').date()
            
            zadanie.tytul = tytul
            zadanie.opis = opis
            zadanie.termin_wykonania = termin_date
            zadanie.wykonane = wykonane
            zadanie.save()
            
            messages.success(request, 'Wydarzenie zostało zaktualizowane.')
            
        except ValueError:
            messages.error(request, 'Nieprawidłowy format daty.')
    
    return redirect('kalendarz')


@login_required
def usun_wydarzenie(request, zadanie_id):
    """Delete calendar event (task)"""
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=zadanie_id, user=request.user)
    
    if request.method == 'POST':
        zadanie.delete()
        messages.success(request, 'Wydarzenie zostało usunięte.')
    
    return redirect('kalendarz')


@login_required
def oznacz_zadanie_wykonane(request, zadanie_id):
    """Mark task as completed"""
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=zadanie_id, user=request.user)
    
    if request.method == 'POST':
        zadanie.wykonane = True
        zadanie.data_wykonania = timezone.now()
        zadanie.save()
        
        messages.success(request, 'Zadanie zostało oznaczone jako wykonane.')
    
    return redirect('kalendarz')


@login_required
def get_calendar_stats(request):
    """API endpoint for calendar statistics"""
    today = timezone.now().date()
    
    # Get date range from request
    start_date = request.GET.get('start', today.isoformat())
    end_date = request.GET.get('end', (today + timedelta(days=30)).isoformat())
    
    try:
        start_date = datetime.fromisoformat(start_date).date()
        end_date = datetime.fromisoformat(end_date).date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Calculate statistics
    stats = {
        'faktury': {
            'total': Faktura.objects.filter(
                user=request.user,
                data_wystawienia__range=[start_date, end_date]
            ).count(),
            'sprzedaz': Faktura.objects.filter(
                user=request.user,
                typ_faktury='sprzedaz',
                data_wystawienia__range=[start_date, end_date]
            ).count(),
            'koszt': Faktura.objects.filter(
                user=request.user,
                typ_faktury='koszt',
                data_wystawienia__range=[start_date, end_date]
            ).count()
        },
        'terminy': {
            'nadchodzace': Faktura.objects.filter(
                user=request.user,
                termin_platnosci__range=[today, end_date],
                status__in=['wystawiona', 'wyslana']
            ).count(),
            'przeterminowane': Faktura.objects.filter(
                user=request.user,
                termin_platnosci__lt=today,
                status__in=['wystawiona', 'wyslana']
            ).count()
        },
        'zadania': {
            'total': ZadanieUzytkownika.objects.filter(
                user=request.user,
                termin_wykonania__range=[start_date, end_date]
            ).count(),
            'wykonane': ZadanieUzytkownika.objects.filter(
                user=request.user,
                termin_wykonania__range=[start_date, end_date],
                wykonane=True
            ).count(),
            'niewykonane': ZadanieUzytkownika.objects.filter(
                user=request.user,
                termin_wykonania__range=[start_date, end_date],
                wykonane=False
            ).count()
        },
        'cykle': {
            'aktywne': FakturaCykliczna.objects.filter(
                oryginalna_faktura__user=request.user,
                aktywna=True
            ).count(),
            'do_generacji': FakturaCykliczna.objects.filter(
                oryginalna_faktura__user=request.user,
                aktywna=True,
                nastepna_generacja__lte=today
            ).count()
        }
    }
    
    return JsonResponse(stats)
