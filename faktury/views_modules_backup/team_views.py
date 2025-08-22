"""
Team and task management views
"""
import secrets
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from ..models import (
    Firma, Zespol, CzlonekZespolu, Zadanie, ZadanieUzytkownika, 
    Wiadomosc, Faktura
)
from ..forms import (
    ZespolForm, CzlonekZespoluFormSet, WiadomoscForm, ZadanieForm,
    ZadanieUzytkownikaForm
)


def generate_password(length=12):
    """Generate random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password


def send_credentials(email, username, password):
    """Send login credentials via email"""
    subject = "Twoje dane do logowania do Systemu Faktur"
    message = f"""
    Witaj,

    Zostało utworzone dla Ciebie konto w Systemie Faktur.

    Twoje dane do logowania:

    Login: {username}
    Hasło: {password}

    Zaloguj się tutaj: {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}/accounts/login/
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)


@login_required
def lista_zespolow(request):
    """List teams view"""
    try:
        firma = get_object_or_404(Firma, user=request.user)
        zespoly = firma.zespoly.select_related('firma').prefetch_related('czlonkowie__user').all()
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw dodaj dane swojej firmy.")
        return redirect('dodaj_firme')
    
    return render(request, 'faktury/lista_zespolow.html', {'zespoly': zespoly})


@login_required
def szczegoly_zespolu(request, zespol_id):
    """Team details view"""
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    
    # Check user access to this team
    if (request.user != zespol.firma.user and 
        not CzlonekZespolu.objects.filter(user=request.user, zespol=zespol).exists()):
        messages.error(request, "Nie masz dostępu do tego zespołu.")
        return redirect('panel_uzytkownika')

    czlonkowie = zespol.czlonkowie.select_related('user').all()
    wiadomosci = zespol.wiadomosci.select_related('autor').all().order_by('-data_utworzenia')[:50]
    zadania = zespol.zadania.select_related('przypisane_do__user').all()
    
    wiadomosc_form = WiadomoscForm()

    context = {
        'zespol': zespol,
        'czlonkowie': czlonkowie,
        'wiadomosci': wiadomosci,
        'zadania': zadania,
        'wiadomosc_form': wiadomosc_form,
    }

    return render(request, 'faktury/szczegoly_zespolu.html', context)


@login_required
@transaction.atomic
def dodaj_zespol(request):
    """Add team view"""
    if request.method == 'POST':
        form = ZespolForm(request.POST)
        czlonkowie_formset = CzlonekZespoluFormSet(request.POST, prefix='czlonkowie')
        
        if form.is_valid() and czlonkowie_formset.is_valid():
            zespol = form.save(commit=False)
            try:
                firma = Firma.objects.get(user=request.user)
                zespol.firma = firma
            except Firma.DoesNotExist:
                messages.error(request, "Musisz najpierw uzupełnić dane firmy.")
                return redirect('dodaj_firme')

            zespol.save()
            czlonkowie_formset.instance = zespol

            for czlonek_form in czlonkowie_formset:
                if czlonek_form.cleaned_data and not czlonek_form.cleaned_data.get('DELETE'):
                    czlonek = czlonek_form.save(commit=False)
                    czlonek.zespol = zespol

                    email = czlonek_form.cleaned_data.get('email')
                    imie = czlonek_form.cleaned_data.get('imie')
                    nazwisko = czlonek_form.cleaned_data.get('nazwisko')

                    user = None
                    try:
                        user = User.objects.get(email=email)
                    except User.DoesNotExist:
                        password = generate_password()
                        username = email
                        user = User.objects.create_user(
                            username=username, 
                            email=email, 
                            password=password,
                            first_name=imie,
                            last_name=nazwisko
                        )
                        send_credentials(email, username, password)

                    czlonek.user = user
                    czlonek.save()

            messages.success(request, "Zespół został dodany, a członkowie zespołu zostali dodani.")
            return redirect('lista_zespolow')
        else:
            messages.error(request, "Popraw błędy w formularzu.")
    else:
        form = ZespolForm()
        czlonkowie_formset = CzlonekZespoluFormSet(
            prefix='czlonkowie', 
            queryset=CzlonekZespolu.objects.none()
        )
    
    return render(request, 'faktury/dodaj_zespol.html', {
        'form': form, 
        'czlonkowie_formset': czlonkowie_formset
    })


@login_required
def szczegoly_czlonka_zespolu(request, czlonek_id):
    """Team member details view"""
    czlonek = get_object_or_404(CzlonekZespolu, pk=czlonek_id)
    
    # Check permissions
    if (request.user != czlonek.zespol.firma.user and 
        not CzlonekZespolu.objects.filter(user=request.user, zespol=czlonek.zespol).exists()):
        messages.error(request, "Nie masz dostępu do tego profilu.")
        return redirect('panel_uzytkownika')
    
    zadania_przypisane = Zadanie.objects.filter(przypisane_do=czlonek).select_related('zespol')
    zadania_wykonane = zadania_przypisane.filter(status='zakonczone')
    wiadomosc_form = WiadomoscForm()

    context = {
        'czlonek': czlonek,
        'zadania_przypisane': zadania_przypisane,
        'zadania_wykonane': zadania_wykonane,
        'wiadomosc_form': wiadomosc_form,
    }
    return render(request, 'faktury/szczegoly_czlonka_zespolu.html', context)


@login_required
def edytuj_zespol(request, zespol_id):
    """Edit team view"""
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    
    # Check permissions
    if request.user != zespol.firma.user:
        messages.error(request, "Nie masz uprawnień do edycji tego zespołu.")
        return redirect('lista_zespolow')
    
    if request.method == 'POST':
        form = ZespolForm(request.POST, instance=zespol)
        czlonkowie_formset = CzlonekZespoluFormSet(
            request.POST, 
            instance=zespol, 
            prefix='czlonkowie'
        )
        
        if form.is_valid() and czlonkowie_formset.is_valid():
            form.save()
            czlonkowie_formset.save()
            messages.success(request, "Zespół został zaktualizowany.")
            return redirect('szczegoly_zespolu', zespol_id=zespol.pk)
    else:
        form = ZespolForm(instance=zespol)
        czlonkowie_formset = CzlonekZespoluFormSet(
            instance=zespol, 
            prefix='czlonkowie'
        )

    return render(request, 'faktury/edytuj_zespol.html', {
        'form': form, 
        'zespol': zespol, 
        'czlonkowie_formset': czlonkowie_formset
    })


@login_required
def usun_zespol(request, zespol_id):
    """Delete team view"""
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    
    if request.user != zespol.firma.user:
        messages.error(request, "Nie masz uprawnień do usunięcia tego zespołu.")
        return redirect('lista_zespolow')
    
    if request.method == 'POST':
        zespol.delete()
        messages.success(request, 'Zespół został usunięty.')
        return redirect('lista_zespolow')
    
    return render(request, 'faktury/usun_zespol.html', {'zespol': zespol})


@login_required
def wyslij_wiadomosc(request, zespol_id):
    """Send message to team"""
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    
    # Check if user belongs to team
    if not CzlonekZespolu.objects.filter(user=request.user, zespol=zespol).exists():
        if request.user != zespol.firma.user:
            messages.error(request, "Nie masz uprawnień do wysyłania wiadomości w tym zespole.")
            return redirect('panel_uzytkownika')

    if request.method == 'POST':
        form = WiadomoscForm(request.POST)
        if form.is_valid():
            wiadomosc = form.save(commit=False)
            wiadomosc.autor = request.user
            wiadomosc.zespol = zespol
            wiadomosc.save()
            messages.success(request, 'Wiadomość została wysłana.')
            return redirect('szczegoly_zespolu', zespol_id=zespol_id)
        else:
            messages.error(request, 'Błąd w formularzu wiadomości.')
    
    return redirect('szczegoly_zespolu', zespol_id=zespol_id)


# Task Management Views

@login_required
def dodaj_zadanie(request, zespol_id):
    """Add task to team"""
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    
    # Check permissions
    if request.user != zespol.firma.user:
        messages.error(request, "Nie masz uprawnień do dodawania zadań w tym zespole.")
        return redirect('lista_zespolow')
    
    if request.method == 'POST':
        form = ZadanieForm(request.POST)
        if form.is_valid():
            zadanie = form.save(commit=False)
            zadanie.zespol = zespol
            zadanie.save()
            messages.success(request, 'Zadanie zostało dodane.')
            return redirect('szczegoly_zespolu', zespol_id=zespol_id)
    else:
        form = ZadanieForm()
    
    return render(request, 'faktury/dodaj_zadanie.html', {
        'form': form, 
        'zespol': zespol
    })


@login_required
def edytuj_zadanie(request, zadanie_id):
    """Edit task"""
    zadanie = get_object_or_404(Zadanie, pk=zadanie_id)
    
    # Check permissions
    if (request.user != zadanie.zespol.firma.user and 
        request.user != zadanie.przypisane_do.user):
        messages.error(request, "Nie masz uprawnień do edycji tego zadania.")
        return redirect('panel_uzytkownika')
    
    if request.method == 'POST':
        form = ZadanieForm(request.POST, instance=zadanie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zadanie zostało zaktualizowane.')
            return redirect('szczegoly_zespolu', zespol_id=zadanie.zespol.pk)
    else:
        form = ZadanieForm(instance=zadanie)
    
    return render(request, 'faktury/edytuj_zadanie.html', {
        'form': form, 
        'zadanie': zadanie
    })


@login_required
def usun_zadanie(request, zadanie_id):
    """Delete task"""
    zadanie = get_object_or_404(Zadanie, pk=zadanie_id)
    
    # Check permissions
    if request.user != zadanie.zespol.firma.user:
        messages.error(request, 'Brak uprawnień')
        return redirect('panel_uzytkownika')
    
    if request.method == 'POST':
        zespol_id = zadanie.zespol.pk
        zadanie.delete()
        messages.success(request, 'Zadanie zostało usunięte.')
        return redirect('szczegoly_zespolu', zespol_id=zespol_id)
    
    return render(request, 'faktury/usun_zadanie.html', {'zadanie': zadanie})


@login_required
def oznacz_zadanie_jako_wykonane(request, zadanie_id):
    """Mark task as completed"""
    zadanie = get_object_or_404(Zadanie, pk=zadanie_id)
    
    # Check permissions
    if (request.user != zadanie.przypisane_do.user and 
        request.user != zadanie.zespol.firma.user):
        messages.error(request, "Nie masz uprawnień do oznaczania tego zadania jako wykonane.")
        return redirect('panel_uzytkownika')
    
    if request.method == 'POST':
        zadanie.status = 'zakonczone'
        zadanie.data_zakonczenia = timezone.now()
        zadanie.save()
        messages.success(request, 'Zadanie zostało oznaczone jako wykonane.')
    
    return redirect('szczegoly_zespolu', zespol_id=zadanie.zespol.pk)


# User Task Management Views

@login_required
def twoje_sprawy(request):
    """User's personal tasks view"""
    zadania = ZadanieUzytkownika.objects.filter(user=request.user).order_by('termin_wykonania')
    today = timezone.now().date()
    
    # Separate tasks by status
    zadania_aktualne = zadania.filter(wykonane=False, termin_wykonania__gte=today)
    zadania_preterminowane = zadania.filter(wykonane=False, termin_wykonania__lt=today)
    zadania_wykonane = zadania.filter(wykonane=True)
    
    context = {
        'zadania_aktualne': zadania_aktualne,
        'zadania_preterminowane': zadania_preterminowane,
        'zadania_wykonane': zadania_wykonane,
        'today': today,
    }
    
    return render(request, 'faktury/twoje_sprawy.html', context)


@login_required
def moje_zadania(request):
    """User's tasks and invoice reminders"""
    # Get user tasks
    zadania_uzytkownika = ZadanieUzytkownika.objects.filter(
        user=request.user, 
        wykonane=False
    ).order_by('termin_wykonania')
    
    # Get unpaid invoices with approaching deadlines
    faktury_nieoplacone = Faktura.objects.for_user(request.user).nieoplacone().filter(
        termin_platnosci__gte=timezone.now().date()
    ).order_by('termin_platnosci')[:10]
    
    context = {
        'zadania': zadania_uzytkownika,
        'faktury_nieoplacone': faktury_nieoplacone,
    }
    
    return render(request, 'faktury/moje_zadania.html', context)


@login_required
def dodaj_zadanie_uzytkownika(request):
    """Add personal task"""
    if request.method == 'POST':
        form = ZadanieUzytkownikaForm(request.POST)
        if form.is_valid():
            zadanie = form.save(commit=False)
            zadanie.user = request.user
            zadanie.save()
            messages.success(request, 'Zadanie zostało dodane.')
            return redirect('twoje_sprawy')
    else:
        form = ZadanieUzytkownikaForm()
    
    return render(request, 'faktury/dodaj_zadanie_uzytkownika.html', {'form': form})


@login_required
def edytuj_zadanie_uzytkownika(request, pk):
    """Edit personal task"""
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ZadanieUzytkownikaForm(request.POST, instance=zadanie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zadanie zostało zaktualizowane.')
            return redirect('twoje_sprawy')
    else:
        form = ZadanieUzytkownikaForm(instance=zadanie)
    
    return render(request, 'faktury/edytuj_zadanie_uzytkownika.html', {
        'form': form, 
        'zadanie': zadanie
    })


@login_required
def usun_zadanie_uzytkownika(request, pk):
    """Delete personal task"""
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk, user=request.user)
    
    if request.method == 'POST':
        zadanie.delete()
        messages.success(request, 'Zadanie zostało usunięte.')
        return redirect('twoje_sprawy')
    
    return render(request, 'faktury/usun_zadanie_uzytkownika.html', {'zadanie': zadanie})


@login_required
def oznacz_zadanie_uzytkownika_wykonane(request, pk):
    """Mark personal task as completed"""
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk, user=request.user)
    
    if request.method == 'POST':
        zadanie.wykonane = True
        zadanie.data_wykonania = timezone.now()
        zadanie.save()
        messages.success(request, 'Zadanie zostało oznaczone jako wykonane.')
    
    return redirect('twoje_sprawy')


@login_required
def szczegoly_zadania_uzytkownika(request, pk):
    """Personal task details"""
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk, user=request.user)
    return render(request, 'faktury/szczegoly_zadania_uzytkownika.html', {'zadanie': zadanie})


# Calendar and Events API

@login_required
def get_events(request):
    """Return events (invoices and tasks) for calendar in JSON format"""
    events = []
    
    # Get user invoices
    faktury = Faktura.objects.for_user(request.user).with_related()
    
    for faktura in faktury:
        # Add invoice issue date
        events.append({
            'title': f'Faktura {faktura.numer}',
            'start': faktura.data_wystawienia.isoformat(),
            'url': f'/szczegoly_faktury/{faktura.pk}/',
            'color': '#3788d8',
            'type': 'faktura'
        })
        
        # Add payment deadline
        if faktura.termin_platnosci:
            events.append({
                'title': f'Termin płatności - {faktura.numer}',
                'start': faktura.termin_platnosci.isoformat(),
                'url': f'/szczegoly_faktury/{faktura.pk}/',
                'color': '#f39c12' if faktura.status != 'oplacona' else '#27ae60',
                'type': 'termin_platnosci'
            })
    
    # Get user tasks
    zadania = ZadanieUzytkownika.objects.filter(user=request.user)
    
    for zadanie in zadania:
        events.append({
            'title': zadanie.opis,
            'start': zadanie.termin_wykonania.isoformat(),
            'color': '#e74c3c' if not zadanie.wykonane else '#27ae60',
            'type': 'zadanie'
        })
    
    return JsonResponse(events, safe=False)


@login_required
def get_calendar_data(request):
    """Return calendar data in JSON format"""
    faktury = Faktura.objects.for_user(request.user)
    zadania = ZadanieUzytkownika.objects.filter(user=request.user)
    
    calendar_data = {
        'faktury': [],
        'zadania': [],
        'events': []
    }
    
    # Process invoices
    for faktura in faktury:
        calendar_data['faktury'].append({
            'id': faktura.pk,
            'numer': faktura.numer,
            'data_wystawienia': faktura.data_wystawienia.isoformat(),
            'termin_platnosci': faktura.termin_platnosci.isoformat() if faktura.termin_platnosci else None,
            'status': faktura.status,
            'suma_brutto': str(faktura.suma_brutto),
        })
    
    # Process tasks
    for zadanie in zadania:
        calendar_data['zadania'].append({
            'id': zadanie.pk,
            'opis': zadanie.opis,
            'termin_wykonania': zadanie.termin_wykonania.isoformat(),
            'wykonane': zadanie.wykonane,
        })
    
    return JsonResponse(calendar_data, safe=False)
