
from django.forms import inlineformset_factory
from RegonAPI import RegonAPI
from .utils import generuj_numer
from .notifications.models import Notification
from .decorators import ajax_login_required
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum, F, FloatField, DecimalField, Case, When
from django.core.paginator import Paginator
from django.template.loader import get_template, render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from import_export.formats import base_formats
from .resources import KontrahentResource, ProduktResource, FakturaResource
import tempfile
from django.core.mail import EmailMessage
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail  
from .faktury_ksiegowosc import auto_ksieguj_fakture
import secrets 
import string 
import calendar
from .forms import (
    FakturaCyklicznaForm, FakturaForm, CzlonekZespoluFormSet, PozycjaFakturyForm, PozycjaFakturyFormSet,
    KontrahentForm, FirmaForm, ProduktForm, UserRegistrationForm,
    UserProfileForm, KwotaOplaconaForm, ZespolForm, WiadomoscForm,
    ZadanieForm, ZadanieUzytkownikaForm, PartnerstwoForm, ParagonForm, FakturaProformaForm, KpForm, KorektaFakturyForm
)
from .models import (
    Partnerstwo, User, Faktura, Kontrahent, Firma,
    Produkt, PozycjaFaktury, Zespol, CzlonekZespolu,
    Wiadomosc, Zadanie, ZadanieUzytkownika,
)
from django.core.validators import validate_integer

from tablib import Dataset
from requests.exceptions import RequestException
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from .faktury_ksiegowosc import auto_ksieguj_fakture
import datetime
import json
from decimal import Decimal
from io import BytesIO
import zipfile
import requests
from weasyprint import HTML
from django.core.files.storage import default_storage
from dateutil.relativedelta import relativedelta
import zeep
from zeep import Client
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
from requests import Session
from django.conf import settings
import logging

import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


#Dodaj jednostki do formularza (dynamicznie)
JEDNOSTKI = [
    ('szt', 'szt'),
    ('kg', 'kg'),
    ('m', 'm'),
    ('l', 'l'),
    ('usł', 'usł'),
    ('godz', 'godz'),
    ('dzień', 'dzień'),
    ('inne', 'inne'),
]

#  DODANE SMIECIOWO - START

def check_payment_terms(request):
    # twoja logika
    return HttpResponse("OK")

def api_faktury_list(request):
    data = {
        "faktury": []  # tutaj powinna być twoja logika zwracająca dane
    }
    return JsonResponse(data)

def api_faktura_detail(request, pk):
    try:
        faktura = {"id": pk, "numer": "123/2024"}  # przykładowe dane
    except:
        raise Http404("Faktura nie znaleziona")

    return JsonResponse(faktura)

def api_kontrahenci_list(request):
    kontrahenci = []  # tu powinna być twoja logika np. pobieranie z bazy danych
    return JsonResponse({"kontrahenci": kontrahenci})

def api_kontrahent_detail(request, pk):
    # przykładowe dane, zastąp swoją logiką pobierania kontrahenta
    kontrahent = {"id": pk, "nazwa": "Kontrahent XYZ"}

    if not kontrahent:
        raise Http404("Kontrahent nie istnieje")

    return JsonResponse(kontrahent)

def api_produkty_list(request):
    produkty = []  # tutaj powinna być logika pobierania danych o produktach
    return JsonResponse({"produkty": produkty})

def api_produkt_detail(request, pk):
    produkt = {"id": pk, "nazwa": "Produkt ABC"}  # zamień na swoją logikę

    if not produkt:
        raise Http404("Produkt nie istnieje")

    return JsonResponse(produkt)

def api_zadania_list(request):
    zadania = []  # zastąp swoją logiką
    return JsonResponse({"zadania": zadania})

def api_zadanie_detail(request, pk):
    zadanie = {"id": pk, "opis": "Przykładowe zadanie"}  # podmień na realne dane

    if not zadanie:
        raise Http404("Zadanie nie istnieje")

    return JsonResponse(zadanie)

# DODANE SMIECIOWO - END

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Konto dla {username} zostało utworzone! Możesz się teraz zalogować.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required  # Użytkownik musi być zalogowany, aby zobaczyć profil
def user_profile(request, pk):
    user = get_object_or_404(User, pk=pk)  # Pobierz użytkownika po ID
    # Opcjonalnie, dodaj tutaj sprawdzanie uprawnień (czy bieżący użytkownik może oglądać profil tego użytkownika)
    return render(request, 'faktury/user_profile.html', {'profile_user': user}) #Przekazujemy do szablonu uzytkownika, ktorego profil ogladamy

def generate_password(length=12):
    """Generuje losowe hasło o podanej długości."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password

def send_credentials(email, username, password):
    """Wysyła e-mail z danymi do logowania."""
    subject = "Twoje dane do logowania do Systemu Faktur"
    message = f"""
    Witaj,

    Zostało utworzone dla Ciebie konto w Systemie Faktur.

    Twoje dane do logowania:

    Login: {username}
    Hasło: {password}

    Zaloguj się tutaj: {settings.ALLOWED_HOSTS[0]}/accounts/login/

    """
    # Upewnij się, że masz skonfigurowane settings.EMAIL_HOST_USER
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
@login_required
def lista_zespolow(request):
    firma = get_object_or_404(Firma, user=request.user)
    zespoly = firma.zespoly.all()  # Pobierz zespoły *tej* firmy
    return render(request, 'faktury/lista_zespolow.html', {'zespoly': zespoly})

@login_required
def szczegoly_zespolu(request, zespol_id):
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    # Upewnij się, że użytkownik ma dostęp do tego zespołu (jest w firmie)
    if request.user != zespol.firma.user and not CzlonekZespolu.objects.filter(user=request.user, zespol=zespol).exists():
        messages.error(request, "Nie masz dostępu do tego zespołu.")
        return redirect('panel_uzytkownika')

    czlonkowie = zespol.czlonkowie.all()
    wiadomosci = zespol.wiadomosci.all()  # Później: ogranicz do ostatnich N
    zadania = zespol.zadania.all()
    # Dodaj formularz wiadomości do kontekstu, aby go wyświetlić na stronie szczegółów
    wiadomosc_form = WiadomoscForm()

    context = {
        'zespol': zespol,
        'czlonkowie': czlonkowie,
        'wiadomosci': wiadomosci,
        'zadania': zadania,
        'wiadomosc_form': wiadomosc_form,  # Dodaj formularz do kontekstu
    }

    return render(request, 'faktury/szczegoly_zespolu.html', context)
@login_required
@transaction.atomic # Add atomic transaction for safety
def dodaj_zespol(request):
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

            zespol.save() # Save Zespol instance FIRST, inside atomic transaction

            czlonkowie_formset.instance = zespol # Relate formset to saved Zespol

            for czlonek_form in czlonkowie_formset: # Iterate through formset FORMS, not saved objects
                if czlonek_form.cleaned_data and not czlonek_form.cleaned_data.get('DELETE'):
                    czlonek = czlonek_form.save(commit=False) # Prepare CzlonekZespolu object from form
                    czlonek.zespol = zespol # Explicitly set the relationship AGAIN (for extra safety)

                    email = czlonek_form.cleaned_data.get('email')
                    rola = czlonek_form.cleaned_data.get('rola')
                    imie = czlonek_form.cleaned_data.get('imie')
                    nazwisko = czlonek_form.cleaned_data.get('nazwisko')

                    user = None
                    try:
                        user = User.objects.get(email=email)
                    except User.DoesNotExist:
                        password = generate_password()
                        username = email
                        user = User.objects.create_user(username=username, email=email, password=password)
                        send_credentials(email, username, password)

                    czlonek.user = user
                    czlonek.save() # Save each CzlonekZespolu instance INDIVIDUALLY

            messages.success(request, "Zespół został dodany, a członkowie zespołu zostali dodani.")
            return redirect('lista_zespolow')
        else:
            messages.error(request, "Popraw błędy w formularzu.")
    else:
        form = ZespolForm()
        czlonkowie_formset = CzlonekZespoluFormSet(prefix='czlonkowie', queryset=CzlonekZespolu.objects.none())
    return render(request, 'faktury/dodaj_zespol.html', {'form': form, 'czlonkowie_formset': czlonkowie_formset})

@login_required
def szczegoly_czlonka_zespolu(request, czlonek_id):
    czlonek = get_object_or_404(CzlonekZespolu, pk=czlonek_id)
    zadania_przypisane = Zadanie.objects.filter(przypisane_do=czlonek)
    zadania_wykonane = zadania_przypisane.filter(status='zakonczone') # Filtruj zadania wykonane
    wiadomosc_form = WiadomoscForm() # Formularz wiadomości - opcjonalnie, jeśli chcesz wysyłać wiadomości z profilu

    context = {
        'czlonek': czlonek,
        'zadania_przypisane': zadania_przypisane,
        'zadania_wykonane': zadania_wykonane,
        'wiadomosc_form': wiadomosc_form, # Dodaj formularz wiadomości do kontekstu
    }
    return render(request, 'faktury/szczegoly_czlonka_zespolu.html', context)

@login_required
def edytuj_zespol(request, zespol_id):
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    if request.method == 'POST':
        form = ZespolForm(request.POST, instance=zespol)
        czlonkowie_formset = CzlonekZespoluFormSet(request.POST, instance=zespol, prefix='czlonkowie')
        if form.is_valid() and czlonkowie_formset.is_valid():
            form.save()
            czlonkowie_formset.save() # Save updated team members (profiles)
            messages.success(request, "Zespół został zaktualizowany.")
            return redirect('szczegoly_zespolu', zespol_id=zespol.pk)
    else:
        form = ZespolForm(instance=zespol)
        czlonkowie_formset = CzlonekZespoluFormSet(instance=zespol, prefix='czlonkowie')

    return render(request, 'faktury/edytuj_zespol.html', {'form': form, 'zespol': zespol, 'czlonkowie_formset': czlonkowie_formset})
@login_required
def usun_zespol(request, zespol_id):
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    if request.user != zespol.firma.user:
        messages.error(request, "Nie masz uprawnień do usunięcia tego zespołu.")
        return redirect('lista_zespolow')
    if request.method == 'POST':
        zespol.delete()
        messages.success(request, 'Zespół został usunięty.')
        return redirect('lista_zespolow')  # Przekieruj do listy zespołów
    return render(request, 'faktury/usun_zespol.html', {'zespol': zespol})


@login_required
def wyslij_wiadomosc(request, zespol_id):
    zespol = get_object_or_404(Zespol, pk=zespol_id)
    #Sprawdz czy uzytkownik nalezy do zespolu.
    if not CzlonekZespolu.objects.filter(user=request.user, zespol=zespol).exists():
        messages.error(request, 'Nie jesteś członkiem tego zespołu.')  # Zmieniony komunikat
        return redirect('szczegoly_zespolu', zespol_id=zespol.pk)

    if request.method == 'POST':
        form = WiadomoscForm(request.POST)
        if form.is_valid():
            wiadomosc = form.save(commit=False)
            wiadomosc.zespol = zespol
            # Ustaw nadawcę na podstawie zalogowanego użytkownika i zespołu
            try:
                wiadomosc.nadawca = CzlonekZespolu.objects.get(user=request.user, zespol=zespol)
            except CzlonekZespolu.DoesNotExist:
                messages.error(request, 'Nie jesteś członkiem tego zespołu.') # Zmieniony komunikat
                return redirect('szczegoly_zespolu', zespol_id=zespol.pk)

            wiadomosc.save()
            messages.success(request, "Wiadomość wysłana") # Dodajemy messages
            return redirect('szczegoly_zespolu', zespol_id=zespol.pk)  # Przekierowanie
        else:
            messages.error(request, "Błąd wysyłania wiadomości") # Dodajemy messages

    else:
        form = WiadomoscForm() # Pusty formularz do GET

    return render(request, 'faktury/wyslij_wiadomosc.html', {'form': form, 'zespol': zespol})
@login_required
def dodaj_zadanie(request, zespol_id):
    zespol = get_object_or_404(Zespol, pk=zespol_id)
     # Sprawdzamy, czy użytkownik ma uprawnienia do tego zespołu
    if request.user != zespol.firma.user:
        messages.error(request, "Nie masz uprawnień do dodawania zadań w tym zespole.")
        return redirect('szczegoly_zespolu', zespol_id=zespol_id)

    if request.method == 'POST':
        form = ZadanieForm(request.POST)
        if form.is_valid():
            zadanie = form.save(commit=False)
            zadanie.zespol = zespol
            zadanie.save()
            messages.success(request, "Zadanie zostało dodane.")
            return redirect('szczegoly_zespolu', zespol_id=zespol.pk)
    else:
        form = ZadanieForm()
        #Dodajemy choices, by przypisać zadanie do członka zespolu:
        form.fields['przypisane_do'].queryset = CzlonekZespolu.objects.filter(zespol=zespol)
    return render(request, 'faktury/dodaj_zadanie.html', {'form': form, 'zespol': zespol})

@login_required
def edytuj_zadanie(request, zadanie_id):
    zadanie = get_object_or_404(Zadanie, pk=zadanie_id)
    if request.user != zadanie.zespol.firma.user and request.user != zadanie.przypisane_do.user: #Sprawdz uprawnienia
        messages.error(request,"Nie masz uprawnień do edycji tego zadania.")
        return redirect('szczegoly_zespolu', zespol_id=zadanie.zespol.pk)
    if request.method == 'POST':
        form = ZadanieForm(request.POST, instance=zadanie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zadanie zaktualizowane')
            return redirect('szczegoly_zespolu', zespol_id=zadanie.zespol.pk)
    else:
        form = ZadanieForm(instance=zadanie)
        #Dodajemy choices
        form.fields['przypisane_do'].queryset = CzlonekZespolu.objects.filter(zespol=zadanie.zespol) #Przypisani uzytkownicy do danego zespolu.
    return render(request, 'faktury/edytuj_zadanie.html', {'form': form, 'zadanie': zadanie})

@login_required
def usun_zadanie(request, pk):
    zadanie = get_object_or_404(Zadanie, pk=zadanie_id)
    if request.user != zadanie.zespol.firma.user: #tylko user, który jest przypisany do firmy
        messages.error(request, 'Brak uprawnień')
        return redirect('szczegoly_zespolu', zespol_id=zadanie.zespol.pk)
    if request.method == "POST":
        zadanie.delete()
        messages.success(request, 'Zadanie zostało usunięte.')
        return redirect('szczegoly_zespolu', zespol_id=zadanie.zespol.pk)
    return render(request, 'faktury/usun_zadanie.html', {'zadanie': zadanie})

@login_required
def oznacz_zadanie_jako_wykonane(request, zadanie_id):
    zadanie = get_object_or_404(Zadanie, pk=zadanie_id)
     # Sprawdzamy, czy użytkownik ma uprawnienia do oznaczania zadania jako wykonane (przypisany lub wlasciciel firmy)
    if request.user != zadanie.przypisane_do.user and request.user != zadanie.zespol.firma.user :
        messages.error(request, "Nie masz uprawnień do oznaczenia tego zadania jako wykonane.")
        return redirect('szczegoly_zespolu', zespol_id=zadanie.zespol.pk)

    if request.method == 'POST':
        zadanie.status = 'zakonczone'
        zadanie.data_zakonczenia = timezone.now() # Ustawiamy datę zakończenia
        zadanie.save()
        messages.success(request, "Zadanie oznaczone jako wykonane.")
        return redirect('szczegoly_zespolu', zespol_id=zadanie.zespol.pk)

    return redirect('szczegoly_zespolu', zespol_id=zadanie.zespol.pk) # W razie GET, po prostu przekierowujemy
def rejestracja(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Rejestracja przebiegła pomyślnie. Możesz się teraz zalogować.')
            return redirect('account_login')
    else:
        form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request, 'registration/register.html', {'form': form, 'profile_form': profile_form})

##############################################
# Funkcje pomocnicze
##############################################

def get_total(queryset, typ_faktury, start_date, end_date):
    """Calculate total for given date range and invoice type - FIXED VAT calculation"""
    from decimal import Decimal
    
    total = queryset.filter(
        data_sprzedazy__gte=start_date,
        data_sprzedazy__lt=end_date,
        typ_faktury=typ_faktury
    ).aggregate(
        total=Sum(
            F('pozycjafaktury__ilosc') *
            F('pozycjafaktury__cena_netto') *
            Case(
                # Proper VAT calculation with string values
                When(pozycjafaktury__vat='23', then=Decimal('1.23')),
                When(pozycjafaktury__vat='8', then=Decimal('1.08')),
                When(pozycjafaktury__vat='5', then=Decimal('1.05')),
                When(pozycjafaktury__vat='0', then=Decimal('1.00')),
                When(pozycjafaktury__vat='zw', then=Decimal('1.00')),
                default=Decimal('1.23'),  # Default to 23% VAT
                output_field=DecimalField(max_digits=5, decimal_places=2)
            ),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )['total'] or Decimal('0.00')
    return float(total)  # Convert to float for compatibility with existing code

def get_time_series(queryset, typ_faktury, start_date, end_date, points=10):
    total_seconds = (end_date - start_date).total_seconds()
    interval = datetime.timedelta(seconds=total_seconds / points)
    labels = []
    series = []
    for i in range(points):
        interval_start = start_date + interval * i
        interval_end = start_date + interval * (i + 1)
        total = get_total(queryset, typ_faktury, interval_start, interval_end)
        labels.append(interval_start.strftime("%d/%m"))
        series.append(round(total, 2))
    return labels, series

def compare_periods(queryset, typ_faktury, current_start, current_end, previous_start, previous_end):
    """
    Oblicza procentową zmianę między okresem bieżącym a poprzednim.
    Zwraca None, gdy wartość z poprzedniego okresu jest zerowa.
    """
    current_total = get_total(queryset, typ_faktury, current_start, current_end)
    previous_total = get_total(queryset, typ_faktury, previous_start, previous_end)
    if previous_total:
        change = ((current_total - previous_total) / previous_total) * 100
    else:
        change = None
    return change

##############################################
# Widok główny
##############################################

@login_required
def panel_uzytkownika(request):
    # Pobieramy faktury aktualnego użytkownika
    faktury = Faktura.objects.filter(user=request.user)

    # Sortowanie faktur
    sort_by = request.GET.get('sort', '-data_wystawienia')
    valid_sort_fields = [
        'typ_dokumentu', 'numer', 'data_sprzedazy', 'data_wystawienia',
        'termin_platnosci', 'nabywca__nazwa', 'suma_netto', 'suma_brutto',
        'status', 'typ_faktury'
    ]
    if sort_by.replace('-', '') in valid_sort_fields:
        faktury = faktury.order_by(sort_by)
    elif sort_by.replace('-', '') == 'produkt_usluga':
        faktury = faktury.annotate(first_product_name=F('pozycjafaktury__nazwa'))
        faktury = faktury.order_by(('-' if sort_by.startswith('-') else '') + 'first_product_name')
    else:
        faktury = faktury.order_by('-data_wystawienia')

    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        firma = None

    # Ustalenie zakresów czasowych
    today = timezone.now().date()
    # Tydzień: od poniedziałku do niedzieli
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=7)
    # Miesiąc: od pierwszego dnia bieżącego miesiąca do pierwszego dnia następnego miesiąca
    month_start = today.replace(day=1)
    month_end = (month_start + datetime.timedelta(days=32)).replace(day=1)
    # Kwartał: określamy na podstawie miesiąca (przybliżenie)
    quarter = (today.month - 1) // 3 + 1
    quarter_start = datetime.date(today.year, 3 * quarter - 2, 1)
    quarter_end = quarter_start + datetime.timedelta(days=92)  # przybliżony koniec kwartału
    # Rok: od 1 stycznia do 1 stycznia kolejnego roku
    year_start = today.replace(month=1, day=1)
    year_end = today.replace(year=today.year + 1, month=1, day=1)
    # Okres zbiorczy: od 1970-01-01 do jutra
    total_start = datetime.date(1970, 1, 1)
    total_end = today + datetime.timedelta(days=1)

    ##############################################
    # Obliczenia sum dla bieżących okresów
    ##############################################

    # Sprzedaż
    sprzedaz_tygodniowa = round(get_total(faktury, 'sprzedaz', week_start, week_end), 2)
    sprzedaz_miesieczna = round(get_total(faktury, 'sprzedaz', month_start, month_end), 2)
    sprzedaz_kwartalna = round(get_total(faktury, 'sprzedaz', quarter_start, quarter_end), 2)
    sprzedaz_roczna = round(get_total(faktury, 'sprzedaz', year_start, year_end), 2)
    sprzedaz_calkowita = round(get_total(faktury, 'sprzedaz', total_start, total_end), 2)

    # Koszty
    koszt_tygodniowy = round(get_total(faktury, 'koszt', week_start, week_end), 2)
    koszt_miesieczny = round(get_total(faktury, 'koszt', month_start, month_end), 2)
    koszt_kwartalny = round(get_total(faktury, 'koszt', quarter_start, quarter_end), 2)
    koszt_roczny = round(get_total(faktury, 'koszt', year_start, year_end), 2)
    koszty_calkowite = round(get_total(faktury, 'koszt', total_start, total_end), 2)

    ##############################################
    # Obliczenia porównań z poprzednimi okresami
    ##############################################

    # Dla sprzedaży
    sprzedaz_weekly_change = compare_periods(
        faktury, 'sprzedaz',
        week_start, week_end,
        week_start - datetime.timedelta(days=7), week_start
    )
    sprzedaz_monthly_change = compare_periods(
        faktury, 'sprzedaz',
        month_start, month_end,
        month_start - relativedelta(months=1), month_start
    )
    sprzedaz_quarterly_change = compare_periods(
        faktury, 'sprzedaz',
        quarter_start, quarter_end,
        quarter_start - relativedelta(months=3), quarter_start
    )
    sprzedaz_yearly_change = compare_periods(
        faktury, 'sprzedaz',
        year_start, year_end,
        year_start - relativedelta(years=1), year_start
    )
    # Dla kosztów
    koszty_weekly_change = compare_periods(
        faktury, 'koszt',
        week_start, week_end,
        week_start - datetime.timedelta(days=7), week_start
    )
    koszty_monthly_change = compare_periods(
        faktury, 'koszt',
        month_start, month_end,
        month_start - relativedelta(months=1), month_start
    )
    koszty_quarterly_change = compare_periods(
        faktury, 'koszt',
        quarter_start, quarter_end,
        quarter_start - relativedelta(months=3), quarter_start
    )
    koszty_yearly_change = compare_periods(
        faktury, 'koszt',
        year_start, year_end,
        year_start - relativedelta(years=1), year_start
    )

    ##############################################
    # Generowanie danych szeregowych dla wykresów
    ##############################################

    sales_weekly_labels, sales_weekly_series = get_time_series(faktury, 'sprzedaz', week_start, week_end)
    sales_monthly_labels, sales_monthly_series = get_time_series(faktury, 'sprzedaz', month_start, month_end)
    sales_quarterly_labels, sales_quarterly_series = get_time_series(faktury, 'sprzedaz', quarter_start, quarter_end)
    sales_yearly_labels, sales_yearly_series = get_time_series(faktury, 'sprzedaz', year_start, year_end)
    sales_total_labels, sales_total_series = get_time_series(faktury, 'sprzedaz', total_start, total_end)
    
    costs_weekly_labels, costs_weekly_series = get_time_series(faktury, 'koszt', week_start, week_end)
    costs_monthly_labels, costs_monthly_series = get_time_series(faktury, 'koszt', month_start, month_end)
    costs_quarterly_labels, costs_quarterly_series = get_time_series(faktury, 'koszt', quarter_start, quarter_end)
    costs_yearly_labels, costs_yearly_series = get_time_series(faktury, 'koszt', year_start, year_end)
    costs_total_labels, costs_total_series = get_time_series(faktury, 'koszt', total_start, total_end)

    ##############################################
    # Przygotowanie kontekstu
    ##############################################

    context = {
        'faktury': faktury,
        'firma': firma,
        'sort_by': sort_by,
        'sprzedaz': {
            'Tygodniowa': sprzedaz_tygodniowa,
            'Miesięczna': sprzedaz_miesieczna,
            'Kwartalna': sprzedaz_kwartalna,
            'Roczna': sprzedaz_roczna,
            'Całkowita': sprzedaz_calkowita,
        },
        'koszty': {
            'Tygodniowy': koszt_tygodniowy,
            'Miesięczny': koszt_miesieczny,
            'Kwartalny': koszt_kwartalny,
            'Roczny': koszt_roczny,
            'Całkowity': koszty_calkowite,
        },
        'comparisons': {
            'sprzedaz': {
                'Tygodniowa': sprzedaz_weekly_change,
                'Miesięczna': sprzedaz_monthly_change,
                'Kwartalna': sprzedaz_quarterly_change,
                'Roczna': sprzedaz_yearly_change,
            },
            'koszty': {
                'Tygodniowy': koszty_weekly_change,
                'Miesięczny': koszty_monthly_change,
                'Kwartalny': koszty_quarterly_change,
                'Roczny': koszty_yearly_change,
            }
        },
        # Dane do wykresów – konwertowane do JSON
        'sales_weekly_labels': json.dumps(sales_weekly_labels),
        'sales_weekly_series': json.dumps(sales_weekly_series),
        'sales_monthly_labels': json.dumps(sales_monthly_labels),
        'sales_monthly_series': json.dumps(sales_monthly_series),
        'sales_quarterly_labels': json.dumps(sales_quarterly_labels),
        'sales_quarterly_series': json.dumps(sales_quarterly_series),
        'sales_yearly_labels': json.dumps(sales_yearly_labels),
        'sales_yearly_series': json.dumps(sales_yearly_series),
        'sales_total_labels': json.dumps(sales_total_labels),
        'sales_total_series': json.dumps(sales_total_series),

        'costs_weekly_labels': json.dumps(costs_weekly_labels),
        'costs_weekly_series': json.dumps(costs_weekly_series),
        'costs_monthly_labels': json.dumps(costs_monthly_labels),
        'costs_monthly_series': json.dumps(costs_monthly_series),
        'costs_quarterly_labels': json.dumps(costs_quarterly_labels),
        'costs_quarterly_series': json.dumps(costs_quarterly_series),
        'costs_yearly_labels': json.dumps(costs_yearly_labels),
        'costs_yearly_series': json.dumps(costs_yearly_series),
        'costs_total_labels': json.dumps(costs_total_labels),
        'costs_total_series': json.dumps(costs_total_series),
    }
    return render(request, 'faktury/panel_uzytkownika.html', context)

@login_required
def faktury_sprzedaz(request):
    # Pobieramy tylko faktury typu "sprzedaz"
    faktury = Faktura.objects.filter(user=request.user, typ_faktury='sprzedaz')
    context = {'faktury': faktury}
    return render(request, 'faktury/faktury_sprzedaz.html', context)

@login_required
def faktury_koszt(request):
    # Pobieramy tylko faktury typu "koszt"
    faktury = Faktura.objects.filter(user=request.user, typ_faktury='koszt')
    context = {'faktury': faktury}
    return render(request, 'faktury/faktury_koszt.html', context)

@login_required
def szczegoly_faktury(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    return render(request, 'faktury/szczegoly_faktury.html', {'faktura': faktura})

@login_required
def dodaj_fakture_sprzedaz(request):
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Uzupełnij dane swojej firmy przed wystawieniem faktury.")
        return redirect('dodaj_firme')

    kontrahent_id = request.GET.get('kontrahent')
    initial_data = {
        'miejsce_wystawienia': firma.miejscowosc,
        'typ_faktury': 'sprzedaz',
        'sprzedawca': firma.id
    }

    if kontrahent_id:
        initial_data['nabywca'] = kontrahent_id

    # Generowanie numeru faktury
    today = datetime.date.today()
    ostatnia_faktura = Faktura.objects.filter(
        user=request.user,
        data_wystawienia__year=today.year,
        data_wystawienia__month=today.month,
        typ_faktury='sprzedaz'
    ).order_by('-numer').first()

    if ostatnia_faktura:
        try:
            ostatni_numer = int(ostatnia_faktura.numer.split('/')[1])
            numer_faktury = f"FV/{ostatni_numer + 1:02d}/{today.month:02d}/{today.year}"
        except (ValueError, IndexError):
            liczba_faktur = Faktura.objects.filter(
                user=request.user,
                data_wystawienia__year=today.year,
                data_wystawienia__month=today.month,
                typ_faktury='sprzedaz'
            ).count()
            numer_faktury = f"FV/{liczba_faktur + 1:02d}/{today.month:02d}/{today.year}"
    else:
        numer_faktury = f"FV/01/{today.month:02d}/{today.year}"

    initial_data['numer'] = numer_faktury

    if request.method == 'POST':
        faktura_form = FakturaForm(request.POST, initial=initial_data)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')

        if faktura_form.is_valid() and pozycje_formset.is_valid():
            try:
                with transaction.atomic():
                    # Utwórz fakturę
                    faktura = faktura_form.save(commit=False)
                    faktura.user = request.user
                    faktura.typ_faktury = 'sprzedaz'
                    faktura.sprzedawca = firma

                     # Walidacja NIP przez kontrahenta
                    if not faktura.nabywca or not faktura.nabywca.nip:
                        messages.error(request, "Wybierz kontrahenta z poprawnym NIP")
                        return redirect('dodaj_fakture')

                    # Walidacja numeru
                    auto_numer = faktura_form.cleaned_data.get('auto_numer', True)
                    wlasny_numer = faktura_form.cleaned_data.get('wlasny_numer', '')
                    
                    if auto_numer:
                        faktura.numer = initial_data['numer']
                    elif wlasny_numer:
                        faktura.numer = wlasny_numer
                    else:
                        messages.error(request, "Wprowadź własny numer faktury.")
                        return render(request, 'faktury/dodaj_fakture.html', {
                            'faktura_form': faktura_form,
                            'pozycje_formset': pozycje_formset,
                            'firma': firma,
                            'produkty': Produkt.objects.filter(user=request.user),
                            'produkt_form': ProduktForm()
                        })
                    
                    # Ensure sposob_platnosci is always provided
                    sposob_platnosci = faktura_form.cleaned_data.get('sposob_platnosci', 'przelew')
                    faktura.sposob_platnosci = sposob_platnosci
                    
                    faktura.save()

                    # Zapisz pozycje faktury
                    for pozycja_form in pozycje_formset:
                        if pozycja_form.cleaned_data and not pozycja_form.cleaned_data.get('DELETE'):
                            pozycja = pozycja_form.save(commit=False)
                            pozycja.faktura = faktura
                            pozycja.save()

                    messages.success(request, "Faktura została dodana i zaksięgowana.")
                    return redirect('panel_uzytkownika')
            except Exception as e:
                logger.error(f"Błąd przy zapisie faktury: {str(e)}", exc_info=True)
                messages.error(request, "Wystąpił błąd przy zapisie faktury.")
                return redirect('panel_uzytkownika')
        else:
            print("Błędy formularza faktury:", faktura_form.errors)
            print("Błędy formsetu pozycji:", pozycje_formset.errors)
            messages.error(request, f"Błędy w formularzu: {faktura_form.errors}")
            messages.error(request, f"Błędy w pozycjach: {pozycje_formset.errors}")
            messages.error(request, "Popraw błędy w formularzu.")
            if pozycje_formset.non_form_errors():
                for error in pozycje_formset.non_form_errors():
                    messages.error(request, error)
            return render(request, 'faktury/dodaj_fakture.html', {
                'faktura_form': faktura_form,
                'pozycje_formset': pozycje_formset,
                'firma': firma,
                'produkty': Produkt.objects.filter(user=request.user),
                'produkt_form': ProduktForm()
            })

    else:
        faktura_form = FakturaForm(initial=initial_data)
        pozycje_formset = PozycjaFakturyFormSet(prefix='pozycje')

    for form in pozycje_formset:
        form.fields['jednostka'].widget.choices = JEDNOSTKI

    produkty = Produkt.objects.filter(user=request.user)
    return render(request, 'faktury/dodaj_fakture.html', {
        'faktura_form': faktura_form,
        'pozycje_formset': pozycje_formset,
        'firma': firma,
        'produkty': produkty,
        'produkt_form': ProduktForm(),
        'numer_faktury': initial_data.get('numer', '')
    })
@login_required
def dodaj_fakture_koszt(request): # Nowa funkcja
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Uzupełnij dane swojej firmy przed wystawieniem faktury.")
        return redirect('dodaj_firme')

    # Pobierz ID kontrahenta z parametru GET,  jeśli jest
    kontrahent_id = request.GET.get('kontrahent')
    initial_data = {
            'miejsce_wystawienia': firma.miejscowosc,
            'typ_faktury': 'koszt',  # Domyślny typ
        }
     #Jeśli mamy ID kontrahent, dodajemy do initial data
    if kontrahent_id:
        initial_data['nabywca'] = kontrahent_id

    if request.method == 'POST':
        faktura_form = FakturaForm(request.POST)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')

        if faktura_form.is_valid() and pozycje_formset.is_valid():
            faktura = faktura_form.save(commit=False)
            faktura.user = request.user
            faktura.typ_faktury = 'koszt'  # Ustaw typ_faktury na 'koszt'
            faktura.sprzedawca = firma #Poprawione.
            #faktura.nabywca = firma   # Ustawiamy nabywcę na zalogowaną firmę, ŹLE

            # Automatyczne generowanie numeru faktury
            today = datetime.date.today()
            faktura.numer = f"FK/{today.day}/{today.month}/{today.year}" # Inny prefix dla kosztowych
            ostatnia_faktura = Faktura.objects.filter(
                user=request.user,
                data_wystawienia__year=today.year,
                data_wystawienia__month=today.month,
                typ_faktury='koszt' # Dodajemy filtr po typie faktury
            ).order_by('-numer').last()

            if ostatnia_faktura:
                try:
                    ostatni_numer = int(ostatnia_faktura.numer.split('/')[1])
                    faktura.numer = f"FK/{ostatni_numer + 1}/{today.month}/{today.year}"
                except (ValueError, IndexError):
                    faktura.numer = f"FK/1/{today.month}/{today.year}"
            else:
                faktura.numer = f"FK/1/{today.month}/{today.year}" # Pierwsza faktura kosztowa

            faktura.save()


            for pozycja_form in pozycje_formset:
                if pozycja_form.cleaned_data and not pozycja_form.cleaned_data.get('DELETE'):
                    pozycja = pozycja_form.save(commit=False)
                    pozycja.faktura = faktura
                    pozycja.save()
            messages.success(request, "Faktura kosztowa została dodana.")
            return redirect('panel_uzytkownika')
        else:
            messages.error(request, "Popraw błędy w formularzu.")
            logger.error(f"FakturaForm Errors: {faktura_form.errors}")
            logger.error(f"PozycjeFormset Errors: {pozycje_formset.errors}")
            if pozycje_formset.non_form_errors():
                logger.error(f"PozycjeFormset Non-Form Errors: {pozycje_formset.non_form_errors()}")

    else:  # GET request
        initial_data = {
            'miejsce_wystawienia': firma.miejscowosc,
            'typ_faktury': 'koszt',  # Domyślny typ
        }
        faktura_form = FakturaForm(initial=initial_data)
        pozycje_formset = PozycjaFakturyFormSet(prefix='pozycje')

    for form in pozycje_formset:
        form.fields['jednostka'].widget.choices = JEDNOSTKI

    produkty = Produkt.objects.filter(user=request.user)
    return render(request, 'faktury/dodaj_fakture_koszt.html', {'faktura_form': faktura_form, 'pozycje_formset': pozycje_formset, 'firma': firma, 'produkty': produkty, 'produkt_form': ProduktForm()})

@login_required
def zarzadzaj_cyklem(request, faktura_id):  # Dodaj faktura_id jako argument
    faktura = get_object_or_404(Faktura, pk=faktura_id, user=request.user) # Użyj faktura_id, filtruj po user

    if request.method == 'POST':
        form = FakturaCyklicznaForm(request.POST)
        if form.is_valid():
            cykl = form.save(commit=False)
            cykl.oryginalna_faktura = faktura
            cykl.nastepna_generacja = cykl.data_poczatkowa
            cykl.save()
            messages.success(request, "Cykl został ustawiony")
            return redirect('szczegoly_faktury', pk=faktura.pk) #Przekieruj do szczegółów faktury
    else:
        form = FakturaCyklicznaForm()

    return render(request, 'faktury/zarzadzaj_cyklem.html', {
        'form': form,
        'faktura': faktura
    })

@login_required
def wyslij_fakture_mailem(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    kontrahent = faktura.nabywca  #  uproszczenie

    if request.method == 'POST':
        form = EmailFakturyForm(request.POST)
        if form.is_valid():
            adres_email = form.cleaned_data['adres_email']
            temat = form.cleaned_data.get('temat', f"Faktura VAT nr {faktura.numer}")  # Domyślny temat
            tresc = form.cleaned_data.get('tresc', '') # Pobierz tresc, domyslnie pusta

            # Renderuj treść e-maila z szablonu (jeśli masz) - użyj tego samego email_faktura.html
            message = render_to_string('faktury/email_faktura.html', {'faktura': faktura})
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [adres_email]  # Wysyłamy na adres z formularza

            email = EmailMessage(temat, message, from_email, recipient_list)
            email.content_subtype = "html"


            # Generowanie PDF (tak jak poprzednio, ale do BytesIO)
            html_string = render_to_string('faktury/faktura_pdf.html', {'faktura': faktura})
            html = HTML(string=html_string, base_url=request.build_absolute_uri())
            pdf_file = BytesIO()  # Zapisuj do BytesIO
            html.write_pdf(pdf_file)


            # Dodaj załącznik
            email.attach(f'faktura_{faktura.numer}.pdf', pdf_file.getvalue(), 'application/pdf')


            try:
                email.send()
                messages.success(request, f"Faktura {faktura.numer} została wysłana do {adres_email}.")
                return redirect('szczegoly_faktury', pk=pk)  # Przekieruj z powrotem
            except Exception as e:
                messages.error(request, f"Błąd wysyłania e-maila: {e}")
                # W przypadku błędu, *ponownie* wyświetlamy formularz, z komunikatem o błędzie
                return render(request, 'faktury/wyslij_fakture.html', {'form': form, 'faktura': faktura})

    else:  # GET request
        # Utwórz formularz z *domyślnym* adresem e-mail kontrahenta (jeśli istnieje)
        initial_data = {}
        if kontrahent and kontrahent.email:
            initial_data['adres_email'] = kontrahent.email

        form = EmailFakturyForm(initial=initial_data)

    return render(request, 'faktury/wyslij_fakture.html', {'form': form, 'faktura': faktura}) # Przekazujemy formularz i fakturę do szablonu

@login_required
def dodaj_kontrahenta(request):  # New, non-AJAX view
    if request.method == 'POST':
        form = KontrahentForm(request.POST)
        if form.is_valid():
            kontrahent = form.save(commit=False)
            kontrahent.user = request.user
            kontrahent.save()
            messages.success(request, "Kontrahent został dodany.")
            return redirect('kontrahenci')  # Redirect to kontrahent list
    else:
        form = KontrahentForm()
    return render(request, 'faktury/dodaj_kontrahenta.html', {'form': form})
@login_required
def kontrahenci(request):
    kontrahenci_list = Kontrahent.objects.filter(user=request.user).order_by('nazwa')
    return render(request, 'faktury/kontrahenci.html', {'kontrahenci': kontrahenci_list})

@login_required
def produkty(request):
    produkty_list = Produkt.objects.filter(user=request.user).order_by('nazwa')
    return render(request, 'faktury/produkty.html', {'produkty': produkty_list})

@login_required
def update_payment(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    if request.method == 'POST':
        form = KwotaOplaconaForm(request.POST, instance=faktura)
        if form.is_valid():
            old_status = faktura.status
            new_status = form.cleaned_data['status']
            
            if old_status != new_status:
                Notification.objects.create(
                    user=request.user,
                    message=f"Zmiana statusu faktury {faktura.numer}: {old_status} → {new_status}",
                    link=reverse('szczegoly_faktury', args=[faktura.pk])
                )
            
            form.save()
            messages.success(request, "Kwota opłacona zaktualizowana.")
            return redirect('panel_uzytkownika')
    else:
        form = KwotaOplaconaForm(instance=faktura)

    return render(request, 'faktury/update_payment.html', {'form': form, 'faktura': faktura})

@login_required
def szczegoly_kontrahenta(request, pk):
    kontrahent = get_object_or_404(Kontrahent, pk=pk, user=request.user)
    faktury = Faktura.objects.filter(nabywca=kontrahent).order_by('-data_wystawienia')  # Pobierz faktury dla kontrahenta
    return render(request, 'faktury/szczegoly_kontrahenta.html', {'kontrahent': kontrahent, 'faktury': faktury})


@ajax_login_required
def dodaj_kontrahenta_ajax(request):
    if request.method == 'GET':
        nip = request.GET.get('nip')
        nazwa = request.GET.get('nazwa')
        ulica = request.GET.get('ulica')
        numer_domu = request.GET.get('numer_domu')
        numer_mieszkania = request.GET.get('numer_mieszkania')
        kod_pocztowy = request.GET.get('kod_pocztowy')
        miejscowosc = request.GET.get('miejscowosc')
        kraj = request.GET.get('kraj')
        czy_firma_str = request.GET.get('czy_firma', 'true') # Pobierz jako string, domyślnie 'true'
        czy_firma = czy_firma_str.lower() == 'true' # Konwertuj na bool


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
     kontrahent = get_object_or_404(Kontrahent, pk=pk, user=request.user)
     if request.method == "POST":
         kontrahent.delete()
         messages.success(request, 'Kontrahent został usunięty.')
         return redirect('panel_uzytkownika')
     return render(request, 'faktury/usun_kontrahenta.html', {'kontrahent': kontrahent})

@login_required
def dodaj_firme(request):
    try:
        # Sprawdź, czy firma już istnieje dla tego użytkownika
        firma = Firma.objects.get(user=request.user)
        return redirect('edytuj_firme')  # Przekieruj do edycji, jeśli firma już istnieje
    except Firma.DoesNotExist:
        pass  # Kontynuuj, jeśli firma nie istnieje

    if request.method == 'POST':
        form = FirmaForm(request.POST, request.FILES)
        if form.is_valid():
            firma = form.save(commit=False)
            firma.user = request.user
            firma.save()
            messages.success(request, "Dane firmy zostały dodane.")
            return redirect('panel_uzytkownika')
    else:
        form = FirmaForm()
    return render(request, 'faktury/dodaj_firme.html', {'form': form})

@login_required
def edytuj_firme(request):
    firma = get_object_or_404(Firma, user=request.user)
    if request.method == 'POST':
        form = FirmaForm(request.POST, request.FILES, instance=firma)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dane firmy zaktualizowane')
            return redirect('panel_uzytkownika')
    else:
        form = FirmaForm(instance=firma)
    return render(request, 'faktury/edytuj_firme.html', {'form': form})

@login_required
def dodaj_produkt(request):
    if request.method == 'POST':
        form = ProduktForm(request.POST)
        if form.is_valid():
            produkt = form.save(commit=False)
            produkt.user = request.user
            produkt.save()
            messages.success(request, 'Produkt został dodany')
            return redirect('panel_uzytkownika') #Zmienione
    else:
        form = ProduktForm()

    return render(request, 'faktury/dodaj_produkt.html', {'form':form})

@login_required
def edytuj_produkt(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProduktForm(request.POST, instance=produkt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produkt zaktualizowany')
            return redirect('panel_uzytkownika')
    else:
        form = ProduktForm(instance=produkt)
    return render(request, 'faktury/edytuj_produkt.html', {'form':form})

@login_required
def usun_produkt(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk, user=request.user)
    if request.method == 'POST':
        produkt.delete()
        messages.success(request, 'Produkt został usunięty.')
        return redirect('panel_uzytkownika')
    return render(request, 'faktury/usun_produkt.html', {'produkt': produkt})

@login_required
def stworz_proforme(request):
    if request.method == 'POST':
        form = FakturaProformaForm(request.POST)
        if form.is_valid():
            faktura = form.save(commit=False)
            faktura.typ_dokumentu = 'FP'
            faktura.numer = generuj_numer('FP')
            faktura.save()
            return redirect('szczegoly_faktury', pk=faktura.pk)
    else:
        form = FakturaProformaForm()
    return render(request, 'faktury/proforma.html', {'form': form})

@login_required
def konwertuj_proforme_na_fakture(request, pk):
    proforma = get_object_or_404(Faktura, pk=pk, typ_dokumentu='FP')
    faktura = Faktura.objects.create(
        user=request.user,
        typ_dokumentu='FV',
        dokument_podstawowy=proforma,
        # Kopiuj pozostałe pola...
    )
    return redirect('szczegoly_faktury', pk=faktura.pk)

@login_required
def stworz_korekte(request, faktura_pk):
    podstawowa = get_object_or_404(Faktura, pk=faktura_pk)
    if request.method == 'POST':
        form = KorektaFakturyForm(request.POST)
        if form.is_valid():
            korekta = form.save(commit=False)
            korekta.typ_dokumentu = 'KOR'
            korekta.dokument_podstawowy = podstawowa
            korekta.save()
            return redirect('szczegoly_faktury', pk=korekta.pk)
    else:
        form = KorektaFakturyForm(initial={
            'nabywca': podstawowa.nabywca,
            'sprzedawca': podstawowa.sprzedawca,
            # Inne pola...
        })
    return render(request, 'faktury/korekta.html', {'form': form, 'podstawowa': podstawowa})


def get_gus_session():
    """Logowanie do API GUS i zwrócenie tokena sesji."""
    HEADERS["SOAPAction"] = "http://CIS/BIR/PUBL/2014/07/Zaloguj"
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                      xmlns:wsdl="http://CIS/BIR/PUBL/2014/07">
        <soapenv:Header/>
        <soapenv:Body>
            <wsdl:Zaloguj>
                <wsdl:pKluczUzytkownika>{API_KEY}</wsdl:pKluczUzytkownika>
            </wsdl:Zaloguj>
        </soapenv:Body>
    </soapenv:Envelope>"""

    try:
        response = requests.post(GUS_API_URL, data=body, headers=HEADERS)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        namespace = {"ns": "http://CIS/BIR/PUBL/2014/07"}
        session_id = root.find(".//ns:ZalogujResult", namespace)
        return session_id.text if session_id is not None else None
    except requests.RequestException as e:
        return None

@login_required
def pobierz_dane_z_gus(request):
    """
    Funkcja pobiera dane firmy z API GUS na podstawie numeru NIP.
    Używa klucza API z settings.py.
    """
    nip = request.GET.get('nip')
    if not nip:
        return JsonResponse({'error': 'Brak numeru NIP.'}, status=400)

    url = 'https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc/ajax/DaneSzukajPodmioty'
    headers = {
        'Content-Type': 'application/json',
        'sid': settings.GUS_API_KEY  # Użyj klucza API z settings.py
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
def generuj_pdf(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    # Renderuj szablon HTML do stringa
    html_string = render_to_string('faktury/faktura_pdf.html', {'faktura': faktura})

    # Utwórz obiekt HTML z WeasyPrint
    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    # Wygeneruj PDF
    # Zapisz PDF do tymczasowego pliku
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output:
        html.write_pdf(output)
        pdf_file_path = output.name

    # Pobierz zawartość pliku
    with open(pdf_file_path, 'rb') as f:
        pdf_content = f.read()

    # Usuń tymczasowy plik
    import os
    os.remove(pdf_file_path)
    # Zwróć PDF jako odpowiedź HTTP
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="faktura_{faktura.numer}.pdf"'
    return response

@login_required
def generuj_wiele_pdf(request):
    if request.method == 'POST':
        selected_invoice_ids = request.POST.getlist('selected_invoices')  # Pobierz listę ID zaznaczonych faktur

        if not selected_invoice_ids:
            messages.warning(request, "Nie wybrano żadnych faktur.")
            return redirect('panel_uzytkownika')

        # Pobierz obiekty Faktura dla wybranych ID
        faktury = Faktura.objects.filter(pk__in=selected_invoice_ids, user=request.user)

        # Generuj PDF dla każdej faktury i łącz je w jeden plik (lub zwracaj jako archiwum ZIP)
        pdf_files = []
        for faktura in faktury:
            html_string = render_to_string('faktury/faktura_pdf.html', {'faktura': faktura})
            html = HTML(string=html_string, base_url=request.build_absolute_uri())
            pdf_file = BytesIO()  # Zapisuj PDF do pamięci, a nie do pliku
            html.write_pdf(pdf_file)
            pdf_files.append((f'faktura_{faktura.numer}.pdf', pdf_file.getvalue())) #nazwa pliku i jego zawartosc

        # Opcja 1: Połącz PDF-y w jeden (używając np. PyPDF2)
        # merged_pdf = BytesIO() #pamiec podreczna
        # merger = PyPDF2.PdfMerger()
        # for filename, file_content in pdf_files:
        #      merger.append(BytesIO(file_content))
        # merger.write(merged_pdf)
        # response = HttpResponse(merged_pdf.getvalue(), content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="faktury.pdf"'
        # return response

        # Opcja 2: Zwróć ZIP (prostsza i często lepsza opcja)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for filename, file_content in pdf_files:
                zip_file.writestr(filename, file_content)

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="faktury.zip"'
        return response

    else: #GET request
        messages.warning(request, "Nieprawidłowe żądanie.")
        return redirect('panel_uzytkownika')





@login_required
def dodaj_produkt_ajax(request):
    if request.method == 'POST':
        try:
            form = ProduktForm(request.POST)
            if form.is_valid():
                produkt = form.save(commit=False)
                produkt.user = request.user
                produkt.save()
                return JsonResponse({'id': produkt.pk, 'nazwa': produkt.nazwa, 'cena_netto': str(produkt.cena_netto), 'vat': produkt.vat, 'jednostka': produkt.jednostka})
            else:
                raise ValidationError(form.errors)
        except ValidationError as e:
            return JsonResponse({'error': e.message}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def pobierz_dane_produktu(request):
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

@login_required
def edytuj_fakture(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)

    if request.method == 'POST':
        faktura_form = FakturaForm(request.POST, instance=faktura)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, instance=faktura, prefix='pozycje')
        if faktura_form.is_valid() and pozycje_formset.is_valid():
            faktura_form.save()
            pozycje_formset.save()
            messages.success(request, 'Faktura zaktualizowana')
            return redirect('panel_uzytkownika')  # Przekieruj na listę faktur
    else:
        faktura_form = FakturaForm(instance=faktura)
        pozycje_formset = PozycjaFakturyFormSet(instance=faktura, prefix='pozycje')

    # Dodaj choices do każdego formularza w formsecie, w przypadku edycji.
    for form in pozycje_formset:
        form.fields['jednostka'].widget.choices = JEDNOSTKI

    produkty = Produkt.objects.filter(user=request.user) #do selecta w formularzu
    return render(request, 'faktury/edytuj_fakture.html', {
        'faktura_form': faktura_form,
        'pozycje_formset': pozycje_formset,
        'faktura': faktura, # Potrzebne, bo używamy {{ faktura.numer }} w tytule
        'produkty': produkty,
        'produkt_form': ProduktForm()
    })

@login_required
def usun_fakture(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    if request.method == 'POST':
        faktura.delete()
        messages.success(request, 'Faktura została usunięta.')
        return redirect('panel_uzytkownika')
    return render(request, 'faktury/usun_fakture.html', {'faktura': faktura})

@login_required
def dodaj_zadanie_uzytkownika(request):
    if request.method == 'POST':
        form = ZadanieUzytkownikaForm(request.POST)
        if form.is_valid():
            zadanie = form.save(commit=False)
            zadanie.user = request.user
            zadanie.save()
            messages.success(request, "Zadanie zostało dodane.")
            return redirect('twoje_sprawy')
    else:
        form = ZadanieUzytkownikaForm()
        # Poprawka: Ograniczamy wybór faktur do faktur użytkownika
        form.fields['faktura'].queryset = Faktura.objects.filter(user=request.user)
    return render(request, 'faktury/dodaj_zadanie_uzytkownika.html', {'form': form})

@login_required
def edytuj_zadanie_uzytkownika(request, pk):
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ZadanieUzytkownikaForm(request.POST, instance=zadanie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zadanie zaktualizowane')
            return redirect('twoje_sprawy')
    else:
        form = ZadanieUzytkownikaForm(instance=zadanie)
        # Poprawka: Ograniczamy wybór faktur do faktur użytkownika
        form.fields['faktura'].queryset = Faktura.objects.filter(user=request.user)
    return render(request, 'faktury/edytuj_zadanie_uzytkownika.html', {'form': form, 'zadanie': zadanie})
    
@login_required
def twoje_sprawy(request):
    zadania = ZadanieUzytkownika.objects.filter(user=request.user).order_by('termin_wykonania')
    today = timezone.now().date()

    # Powiadomienia dla przeterminowanych faktur
    overdue_invoices = Faktura.objects.filter(
        user=request.user,
        termin_platnosci__lt=today,
        status__in=['wystawiona', 'cz_oplacona']
    ).order_by('termin_platnosci')

    for invoice in overdue_invoices:
        try:
            # Pobierz aktualny status z bazy danych
            current_status = Faktura.objects.get(pk=invoice.pk).status
            if current_status in ['wystawiona', 'cz_oplacona']:
                if not Notification.objects.filter(
                    user=request.user,
                    title__contains=f"Przeterminowana faktura {invoice.numer}"
                ).exists():
                    Notification.objects.create(
                        user=request.user,
                        title=f"Przeterminowana faktura {invoice.numer}!",
                        content=f"Termin płatności: {invoice.termin_platnosci}",
                        link=reverse('szczegoly_faktury', args=[invoice.pk])
                    )
        except Faktura.DoesNotExist:
            logger.error(f"Faktura {invoice.pk} nie istnieje")

    # Powiadomienia dla nadchodzących (do 7 dni)
    upcoming_invoices = Faktura.objects.filter(
        user=request.user,
        termin_platnosci__gte=today,
        termin_platnosci__lte=today + datetime.timedelta(days=7),
        status__in=['wystawiona', 'cz_oplacona']
    ).order_by('termin_platnosci')

    # Przygotowanie danych dla kalendarza
    wydarzenia = []

    for faktura in Faktura.objects.filter(user=request.user).order_by('termin_platnosci'):
        color = 'blue' if faktura.typ_faktury == 'sprzedaz' else 'red'
        title = f"Termin płatności: {faktura.numer} ({'Sprzedaż' if faktura.typ_faktury == 'sprzedaz' else 'Koszt'})"
        wydarzenia.append({
            'title': title,
            'start': faktura.termin_platnosci.isoformat(),
            'end': faktura.termin_platnosci.isoformat(),
            'color': color,
            'url': reverse('szczegoly_faktury', args=[faktura.pk])
        })

    for zadanie in zadania:
        wydarzenia.append({
            'title': zadanie.tytul,
            'start': zadanie.termin_wykonania.isoformat(),
            'end': zadanie.termin_wykonania.isoformat(),
            'color': 'green'
        })

    return render(request, 'faktury/twoje_sprawy.html', {
        'wydarzenia': json.dumps(wydarzenia),
        'zadania': zadania,
        'faktury': Faktura.objects.filter(user=request.user),
        'today': today,
        'faktura_form': FakturaForm(),
        'upcoming_invoices': upcoming_invoices,
        'overdue_invoices': overdue_invoices
    })
@login_required
def usun_zadanie_uzytkownika(request, pk):
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk, user=request.user)
    if request.method == 'POST':
        zadanie.delete()
        messages.success(request, 'Zadanie zostało usunięte.')
        return redirect('twoje_sprawy')
    return render(request, 'faktury/usun_zadanie_uzytkownika.html', {'zadanie': zadanie})

@login_required
def oznacz_zadanie_uzytkownika_wykonane(request, pk):
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk, user=request.user)
    if request.method == 'POST':
        zadanie.wykonane = True  # Oznacz jako wykonane
        zadanie.save()
        messages.success(request, "Zadanie oznaczone jako wykonane.")
        return redirect('twoje_sprawy')
    return redirect('twoje_sprawy') #GET

@login_required
def moje_zadania(request):
    # Pobierz zadania użytkownika i faktury z terminami płatności

    #Pobieramy zadania użytkownika
    zadania = ZadanieUzytkownika.objects.filter(user=request.user).order_by('termin_wykonania')
    return render(request, 'faktury/moje_zadania.html', {'zadania': zadania})

@login_required
def szczegoly_zadania_uzytkownika(request, pk):
    zadanie = get_object_or_404(ZadanieUzytkownika, pk=pk, user=request.user) # Ensure it belongs to the user!
    return render(request, 'faktury/szczegoly_zadania_uzytkownika.html', {'zadanie': zadanie})
@login_required
def wyslij_przypomnienie(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    kontrahent = faktura.nabywca

    if not kontrahent.email:
        messages.error(request, "Kontrahent nie ma podanego adresu e-mail.")
        return redirect('szczegoly_faktury', pk=pk)  # Redirect back

    subject = f"Przypomnienie o płatności: Faktura VAT nr {faktura.numer}"
    message = render_to_string('faktury/email_przypomnienie.html', {'faktura': faktura})
    from_email = settings.DEFAULT_FROM_EMAIL  # Use your default from address
    recipient_list = [kontrahent.email]

    email = EmailMessage(subject, message, from_email, recipient_list)
    email.content_subtype = "html"  # Set the content type to HTML


     # Wygeneruj PDF i dołącz
    html_string = render_to_string('faktury/faktura_pdf.html', {'faktura': faktura})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = BytesIO() # Zapisz do BytesIO
    html.write_pdf(pdf_file)
    email.attach(f'faktura_{faktura.numer}.pdf', pdf_file.getvalue(), 'application/pdf')


    try:
        email.send()
        messages.success(request, f"Wysłano przypomnienie do {kontrahent.email}.")
    except Exception as e:
        messages.error(request, f"Błąd wysyłania przypomnienia: {e}")

    return redirect('szczegoly_faktury', pk=pk)


def get_events(request):
    """Zwraca wydarzenia (faktury i zadania) dla kalendarza w formacie JSON."""

    # Pobierz faktury użytkownika
    faktury = Faktura.objects.filter(user=request.user)
    wydarzenia = []

    for faktura in faktury:
        if faktura.typ_faktury == 'sprzedaz':
            color = 'var(--warning-600)'
            title = f"Termin płatności: {faktura.numer} (Sprzedaż)"
        else:
            color = 'var(--danger-600)'
            title = f"Termin płatności: {faktura.numer} (Koszt)"

        wydarzenia.append({
            'title': title,
            'start': faktura.termin_platnosci.isoformat(),
            'end': faktura.termin_platnosci.isoformat(),
            'color': color,
            'url': reverse('szczegoly_faktury', args=[faktura.pk]),
            'allDay': True,  # <-- dzięki temu widać je także w widoku tygodnia/dnia
        })

    # Zadania użytkownika
    zadania = ZadanieUzytkownika.objects.filter(user=request.user)
    for zadanie in zadania:
        wydarzenia.append({
            'title': zadanie.tytul,
            'start': zadanie.termin_wykonania.isoformat(),
            'end': zadanie.termin_wykonania.isoformat(),
            'color': 'var(--success-600)',
            'allDay': True,  # <-- również całodniowe
        })

    return JsonResponse(wydarzenia, safe=False)

@login_required
def get_calendar_data(request):
    """Zwraca dane dla kalendarza w formacie JSON."""

    faktury = Faktura.objects.filter(user=request.user)
    zadania = ZadanieUzytkownika.objects.filter(user=request.user)

    events = []

    for faktura in faktury:
        events.append({
            'id': f'faktura-{faktura.pk}',
            'title': f"{'Sprzedaż' if faktura.typ_faktury == 'sprzedaz' else 'Koszt'}: {faktura.numer}",
            'start': faktura.termin_platnosci.isoformat(),
            'end': faktura.termin_platnosci.isoformat(),
            'allDay': True,
            'url': reverse('szczegoly_faktury', args=[faktura.pk]),
            'backgroundColor': 'blue' if faktura.typ_faktury == 'sprzedaz' else 'red',
            'classNames': ['faktura-event'],  # Dodatkowa klasa CSS
        })

    for zadanie in zadania:
        events.append({
            'id': f'zadanie-{zadanie.pk}',
            'title': zadanie.tytul,
            'start': zadanie.termin_wykonania.isoformat(),
            'end': zadanie.termin_wykonania.isoformat(),
            'allDay': True,
            'url': reverse('szczegoly_zadania_uzytkownika', args=[zadanie.pk]),
             'backgroundColor': 'green',
             'classNames': ['zadanie-event'],

        })

    return JsonResponse(events, safe=False)  # safe=False jest *konieczne* gdy zwracamy listę

@login_required
def wyslij_wiadomosc(request, zespol_id):
    zespol = get_object_or_404(Zespol, pk=zespol_id)

    # Security Check: Ensure the user is the owner of the company.
    if request.user != zespol.firma.user:
         messages.error(request,"Nie masz uprawnień do wysyłania wiadomości w tym zespole.")
         return redirect('szczegoly_zespolu', zespol_id=zespol_id)

    if request.method == 'POST':
        form = WiadomoscForm(request.POST)
        if form.is_valid():
            wiadomosc = form.save(commit=False)
            # --- Get the CzlonekZespolu for the current user *in this team* ---
            try:
                czlonek = CzlonekZespolu.objects.get(zespol=zespol, email=request.user.email)  # Fetch CzlonekZespolu
                wiadomosc.nadawca = czlonek # Assign the CzlonekZespolu object
            except CzlonekZespolu.DoesNotExist:
                messages.error(request, "Nie jesteś członkiem tego zespołu.")
                return redirect('szczegoly_zespolu', zespol_id=zespol_id)

            wiadomosc.zespol = zespol
            wiadomosc.save()  # Save *before* adding ManyToMany relationships

            # --- Handle recipients (ManyToManyField) ---
            odbiorcy = form.cleaned_data['odbiorcy']
            wiadomosc.odbiorcy.set(odbiorcy)  # Use .set() for ManyToMany

            messages.success(request, "Wiadomość została wysłana.")
            return redirect('szczegoly_zespolu', zespol_id=zespol_id)
        else:
            messages.error(request,"Popraw błędy.")

    else:
        form = WiadomoscForm()
        # Limit the choices for 'odbiorcy' to members of the current team.
        form.fields['odbiorcy'].queryset = CzlonekZespolu.objects.filter(zespol=zespol) # Correct way.

    return render(request, 'faktury/wyslij_wiadomosc.html', {'form': form, 'zespol': zespol})

#PARTNERZY

@login_required
@transaction.atomic
def dodaj_partnerstwo(request):
    try:
        firma_uzytkownika = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Uzupełnij dane swojej firmy przed dodaniem partnera.")
        return redirect('dodaj_firme')

    if request.method == 'POST':
        form = PartnerstwoForm(request.POST, user=request.user)  # Przekaż user
        if form.is_valid():
            try:
                partnerstwo = form.save(commit=False)
                partnerstwo.firma1 = firma_uzytkownika
                partnerstwo.full_clean()
                partnerstwo.save()

                messages.success(request, "Partnerstwo zostało dodane.")
                return redirect('lista_partnerstw')

            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                         messages.error(request, f"{field}: {error}")
            except IntegrityError:
                messages.error(request, "Partnerstwo z tą firmą już istnieje.")
    else:
        form = PartnerstwoForm(user=request.user)  # Przekaż user

    return render(request, 'faktury/dodaj_partnerstwo.html', {
        'form': form,
        'firma': firma_uzytkownika
    })



@login_required
def lista_partnerstw(request):
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Uzupełnij dane swojej firmy.")
        return redirect('dodaj_firme')

    partnerstwa = Partnerstwo.objects.filter(
        Q(firma1=firma) | Q(firma2=firma))

    partners = []
    for p in partnerstwa:
        partner = {
            'id': p.id,
            'data_utworzenia': p.data_utworzenia,
            'aktywne': p.aktywne,
            'auto_ksiegowanie': p.auto_ksiegowanie,
            'typ_partnerstwa': p.get_typ_partnerstwa_display(), #Dodaj typ partnerstwa
            'opis': p.opis, #Dodaj opis
            'data_rozpoczecia': p.data_rozpoczecia, #Dodaj date
            'data_zakonczenia': p.data_zakonczenia #Dodaj date
        }

        if p.firma1 == firma:
            partner.update({
                'kierunek': 'wychodzące',
                'firma_partnera': p.firma2,
                'nazwa_partnera': p.firma2.nazwa,
                'nip_partnera': p.firma2.nip
            })
        else:
            partner.update({
                'kierunek': 'przychodzące',
                'firma_partnera': p.firma1,
                'nazwa_partnera': p.firma1.nazwa,
                'nip_partnera': p.firma1.nip
            })

        partners.append(partner)

    return render(request, 'faktury/lista_partnerstw.html', {
        'partnerstwa': partners,
        'firma': firma
    })



@login_required
@transaction.atomic
def usun_partnerstwo(request, partnerstwo_id):
    try:
        partnerstwo = Partnerstwo.objects.get(id=partnerstwo_id)
        firma = Firma.objects.get(user=request.user)
    except Partnerstwo.DoesNotExist:
        messages.error(request, "Partnerstwo nie istnieje.")
        return redirect('lista_partnerstw')
    except Firma.DoesNotExist:
        messages.error(request, "Nie znaleziono danych firmy.")
        return redirect('panel_uzytkownika')

    if firma not in [partnerstwo.firma1, partnerstwo.firma2]:
        messages.error(request, "Nie masz uprawnień do usunięcia tego partnerstwa.")
        return redirect('lista_partnerstw')

    if request.method == 'POST':
        try:
            partnerstwo.delete()
            messages.success(request, "Partnerstwo zostało usunięte.")
        except Exception as e:
            messages.error(request, f"Błąd podczas usuwania: {str(e)}")
        return redirect('lista_partnerstw')

    return render(request, 'faktury/usun_partnerstwo.html', {
        'partnerstwo': partnerstwo,
        'firma_partnera': partnerstwo.firma2 if partnerstwo.firma1 == firma else partnerstwo.firma1
    })


#Nowy widok do edycji.
@login_required
@transaction.atomic
def edytuj_partnerstwo(request, partnerstwo_id):
    try:
        partnerstwo = Partnerstwo.objects.get(id=partnerstwo_id)
        firma = Firma.objects.get(user=request.user)
    except Partnerstwo.DoesNotExist:
        messages.error(request, "Partnerstwo nie istnieje.")
        return redirect('lista_partnerstw')
    except Firma.DoesNotExist:
        messages.error(request, "Nie znaleziono danych firmy.")
        return redirect('panel_uzytkownika')

    if firma not in [partnerstwo.firma1, partnerstwo.firma2]:
        messages.error(request, "Nie masz uprawnień do edycji tego partnerstwa.")
        return redirect('lista_partnerstw')
    if request.method == "POST":
            form = PartnerstwoForm(request.POST, instance=partnerstwo, user=request.user) #Przekaż user do formularza
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Partnerstwo zaktualizowane')
                    return redirect('lista_partnerstw')
                except ValidationError as e:
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}") #Obsłuż błędy walidacji
                except IntegrityError:
                    messages.error(request, 'Partnerstwo z tą firmą już istnieje') #Błąd integralności

            else:
                messages.error(request, "Popraw błędy w formularzu.") #Błędy formularza

    else:
        form = PartnerstwoForm(instance=partnerstwo, user=request.user)  # Przekazujemy user

    return render(request, 'faktury/edytuj_partnerstwo.html', {'form': form, 'partnerstwo': partnerstwo}) #Dodaj partnerstwo do kontekstu
def create_notification(user, message, link=None):
    notification = Notification.objects.create(
        user=user,
        message=message,
        link=link,
        created_at=timezone.now()
    )
    return notification

@login_required
def notifications(request):
    unread = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    data = [{
        'id': n.id,
        'message': n.message,
        'link': n.link,
        'time': naturaltime(n.created_at)
    } for n in unread]
    return JsonResponse(data, safe=False)

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'notifications': notifications
    }
    return render(request, 'notifications_list.html', context)

def delete_notification(request, notification_id):
    if request.method == "POST":
        # Pobieramy powiadomienie, które chcemy usunąć
        notification = get_object_or_404(Notification, id=notification_id)
        notification.delete()
    return redirect(reverse("notifications_list"))

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})

# Removed duplicate function - using the one from notifications app

def notifications_json(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    data = [{
        'id': n.id,
        'title': n.message,  # Assuming 'message' field contains the notification title/content
        'content': n.message, # Setting content the same as title since the model does not have a separate content field.
        'timestamp': n.created_at.isoformat(),
        'link': n.link
    } for n in notifications]
    return JsonResponse(data, safe=False)

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})

def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications_list')

@login_required
def szczegoly_wiadomosci(request, pk):
    """
    Display the details of a message.
    """
    wiadomosc = get_object_or_404(Wiadomosc, pk=pk)
    
    # Mark the message as read if it wasn't already
    if not wiadomosc.przeczytana:
        wiadomosc.przeczytana = True
        wiadomosc.save()
    
    context = {'wiadomosc': wiadomosc}
    return render(request, 'faktury/szczegoly_wiadomosci.html', context)

@login_required
def odp_wiadomosc(request, pk):
    """
    View for replying to a message.
    Gets the original message (parent_msg) and allows sending a reply in the same thread.
    """
    parent_msg = get_object_or_404(Wiadomosc, pk=pk)
    
    if request.method == 'POST':
        form = WiadomoscForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            # Set the sender and the message we're replying to
            reply.nadawca = CzlonekZespolu.objects.get(user=request.user, zespol=parent_msg.zespol)
            reply.zespol = parent_msg.zespol
            reply.parent = parent_msg
            # Add "Re:" prefix to the subject if it doesn't already have it
            if not parent_msg.temat.startswith('Re:'):
                reply.temat = "Re: " + parent_msg.temat
            else:
                reply.temat = parent_msg.temat
            reply.save()
            
            # Set recipients (same as the original message)
            if parent_msg.odbiorcy.exists():
                reply.odbiorcy.set(parent_msg.odbiorcy.all())
            
            messages.success(request, "Odpowiedź wysłana.")
            return redirect('szczegoly_zespolu', zespol_id=parent_msg.zespol.pk)
        else:
            messages.error(request, "Wystąpił błąd przy wysyłaniu odpowiedzi.")
    else:
        initial_data = {
            'temat': "Re: " + parent_msg.temat if not parent_msg.temat.startswith("Re:") else parent_msg.temat
        }
        form = WiadomoscForm(initial=initial_data)
        # Limit recipients to team members
        form.fields['odbiorca_user'].queryset = CzlonekZespolu.objects.filter(zespol=parent_msg.zespol)
        
    return render(request, 'faktury/odp_wiadomosc.html', {'form': form, 'parent_msg': parent_msg})

@login_required
def unread_notifications_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def export_kontrahenci(request):
    resource = KontrahentResource()
    dataset = resource.export(Kontrahent.objects.filter(firma=request.user.firma))
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="kontrahenci.xlsx"'
    return response

@login_required
def import_kontrahenci(request):
    if request.method == 'POST':
        resource = KontrahentResource()
        file = request.FILES['file']
        dataset = Dataset().load(file.read(), format=file.name.split('.')[-1])
        result = resource.import_data(dataset, dry_run=True)  # Testowy import
        if not result.has_errors():
            resource.import_data(dataset, dry_run=False)  # Prawdziwy import
            messages.success(request, "Dane zostały zaimportowane!")
            return redirect('kontrahenci')
        else:
            messages.error(request, "Błędy podczas importu!")
    return render(request, 'faktury/import.html')

# Eksport produktów
@login_required
def export_produkty(request):
    resource = ProduktResource()
    queryset = Produkt.objects.filter(user=request.user)
    dataset = resource.export(queryset)
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="produkty.xlsx"'
    return response

# Import produktów
@login_required
def import_kontrahenci(request):
    if request.method == 'POST':
        # Sprawdź czy plik został wysłany
        if 'file' not in request.FILES:
            messages.error(request, "Nie wybrano pliku do importu")
            return redirect('import_kontrahenci')
            
        try:
            resource = KontrahentResource()
            file = request.FILES['file']
            
            # Reszta logiki importu
            dataset = Dataset()
            file_format = file.name.split('.')[-1].lower()
            
            if file_format == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
            elif file_format == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:
                messages.error(request, "Nieobsługiwany format pliku")
                return redirect('import_kontrahenci')

            result = resource.import_data(dataset, dry_run=True)
            
            if not result.has_errors():
                resource.import_data(dataset, dry_run=False)
                messages.success(request, "Kontrahenci zaimportowani pomyślnie!")
                return redirect('kontrahenci')
            else:
                messages.error(request, "Błędy w pliku importu")
                
        except Exception as e:
            messages.error(request, f"Błąd podczas importu: {str(e)}")
    
    return render(request, 'faktury/import.html')

# Eksport faktur
@login_required
def export_faktury(request):
    resource = FakturaResource()
    queryset = Faktura.objects.filter(user=request.user)
    dataset = resource.export(queryset)
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="faktury.xlsx"'
    return response

# Import faktur
@login_required
def import_faktury(request):
    if request.method == 'POST':
        resource = FakturaResource()
        file = request.FILES['file']
        dataset = resource.import_data(file.read().decode(), format=file.name.split('.')[-1])
        
        if not dataset.has_errors():
            resource.import_data(dataset, dry_run=False)
            messages.success(request, "Faktury zostały zaimportowane!")
            return redirect('faktury')
        else:
            messages.error(request, "Błędy w pliku importu!")
    
    return render(request, 'faktury/import.html')

@login_required
def import_produkty(request):
    if request.method == 'POST':
        resource = ProduktResource()
        file = request.FILES['file']
        
        try:
            # Utwórz instancję Dataset
            dataset = Dataset()
            
            # Wczytaj plik
            file_format = file.name.split('.')[-1].lower()
            
            if file_format == 'csv':
                imported_data = dataset.load(file.read().decode('utf-8'), format='csv')
            elif file_format == 'xlsx':
                imported_data = dataset.load(file.read(), format='xlsx')
            else:
                messages.error(request, "Nieobsługiwany format pliku")
                return redirect('import_produkty')

            # Wykonaj import
            result = resource.import_data(imported_data, dry_run=True)
            
            if not result.has_errors():
                resource.import_data(imported_data, dry_run=False)
                messages.success(request, "Produkty zaimportowane pomyślnie!")
                return redirect('produkty')
            else:
                messages.error(request, "Błędy w danych:")
                for error in result.row_errors():
                    messages.error(request, f"Wiersz {error[0]}: {error[1]}")
                    
        except Exception as e:
            messages.error(request, f"Błąd podczas importu: {str(e)}")
    
    return render(request, 'faktury/import.html')

@login_required
def stworz_paragon(request):
    if request.method == 'POST':
        form = ParagonForm(request.POST)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')
        
        if form.is_valid() and pozycje_formset.is_valid():
            paragon = form.save(commit=False)
            paragon.typ_dokumentu = 'PAR'
            paragon.save()
            
            pozycje = pozycje_formset.save(commit=False)
            for pozycja in pozycje:
                pozycja.faktura = paragon
                pozycja.save()
            
            return redirect('szczegoly_faktury', pk=paragon.pk)
    else:
        form = ParagonForm()
        pozycje_formset = PozycjaFakturyFormSet(prefix='pozycje')
    
    return render(request, 'faktury/paragon.html', {
        'form': form,
        'pozycje_formset': pozycje_formset
    })

def stworz_kp(request):
    if request.method == 'POST':
        form = KpForm(request.POST)
        if form.is_valid():
            kp = form.save(commit=False)
            kp.typ_dokumentu = 'KP'
            kp.save()
            return redirect('szczegoly_faktury', pk=kp.pk)
    else:
        form = KpForm()
    return render(request, 'faktury/kp.html', {'form': form})

@login_required
def stworz_proforma(request):
    if request.method == 'POST':
        form = FakturaProformaForm(request.POST)
        if form.is_valid():
            faktura = form.save(commit=False)
            faktura.typ_dokumentu = 'FP'
            faktura.numer = generuj_numer('FP')
            faktura.save()
            return redirect('szczegoly_faktury', pk=faktura.pk)
    else:
        form = FakturaProformaForm()
    return render(request, 'faktury/proforma.html', {'form': form})

@login_required 
def stworz_paragon(request):
    if request.method == 'POST':
        form = ParagonForm(request.POST)
        if form.is_valid():
            paragon = form.save(commit=False)
            paragon.typ_dokumentu = 'PAR'
            paragon.save()
            return redirect('szczegoly_faktury', pk=paragon.pk)
    else:
        form = ParagonForm()
    return render(request, 'faktury/paragon.html', {'form': form})

@login_required
def stworz_kp(request):
    try:
        firma_uzytkownika = request.user.firma
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw dodaj dane swojej firmy!")
        return redirect('dodaj_firme')

    if request.method == 'POST':
        form = KpForm(request.POST)
        if form.is_valid():
            kp = form.save(commit=False)
            kp.typ_dokumentu = 'KP'
            kp.sprzedawca = firma_uzytkownika
            kp.numer = f"KP/{datetime.date.today().year}/{Faktura.objects.filter(typ_dokumentu='KP').count() + 1:04d}"
            kp.save()
            return redirect('szczegoly_faktury', pk=kp.pk)
    else:
        form = KpForm(initial={
            'kwota_oplacona': 0,
            'nabywca': firma_uzytkownika
        })
    
    return render(request, 'faktury/kp.html', {'form': form})


@login_required
def stworz_korekte(request, faktura_pk):
    podstawowa = get_object_or_404(Faktura, pk=faktura_pk)
    
    if request.method == 'POST':
        form = KorektaFakturyForm(request.POST)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')
        
        if form.is_valid() and pozycje_formset.is_valid():
            korekta = form.save(commit=False)
            korekta.typ_dokumentu = 'KOR'
            korekta.dokument_podstawowy = podstawowa
            korekta.save()
            
            # Zapisujemy pozycje
            for pozycja_form in pozycje_formset:
                if pozycja_form.cleaned_data and not pozycja_form.cleaned_data.get('DELETE'):
                    pozycja = pozycja_form.save(commit=False)
                    pozycja.faktura = korekta
                    pozycja.save()
            
            messages.success(request, "Korekta została zapisana.")
            return redirect('szczegoly_faktury', pk=korekta.pk)
    else:
        # Inicjalizujemy formularz danymi z podstawowej faktury
        form = KorektaFakturyForm(initial={
            'nabywca': podstawowa.nabywca,
            'sprzedawca': podstawowa.sprzedawca,
            'status': 'wystawiona',
            'waluta': podstawowa.waluta,
            'data_wystawienia': timezone.now().date(),
            'data_sprzedazy': podstawowa.data_sprzedazy,
            'termin_platnosci': podstawowa.termin_platnosci,
            'miejsce_wystawienia': podstawowa.miejsce_wystawienia,
            'sposob_platnosci': podstawowa.sposob_platnosci,
            'typ_faktury': podstawowa.typ_faktury,
        })
        
        # Inicjalizujemy formset pozycjami z podstawowej faktury
        PozycjaFormSet = inlineformset_factory(
            Faktura, PozycjaFaktury,
            form=PozycjaFakturyForm, extra=0, can_delete=True
        )
        pozycje_formset = PozycjaFormSet(instance=podstawowa, prefix='pozycje')
    
    return render(request, 'faktury/korekta.html', {
        'form': form,
        'pozycje_formset': pozycje_formset,
        'podstawowa': podstawowa
    })

def generate_kp(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    
    if faktura.sposob_platnosci != 'gotowka' or faktura.status != 'oplacona':
        messages.error(request, "KP można wygenerować tylko dla faktur z płatnością gotówkową i statusem 'opłacona'.")
        return redirect('szczegoly_faktury', pk=pk)

    # Generuj numer KP
    year = datetime.date.today().year
    count = Faktura.objects.filter(
        user=request.user,
        typ_dokumentu='KP',
        data_wystawienia__year=year
    ).count() + 1
    numer_kp = f"KP/{year}/{count:04d}"

    try:
        with transaction.atomic():
            kp = Faktura.objects.create(
                user=request.user,
                typ_dokumentu='KP',
                numer=numer_kp,
                sprzedawca=faktura.sprzedawca,
                nabywca=faktura.nabywca,
                data_wystawienia=datetime.date.today(),
                data_sprzedazy=faktura.data_sprzedazy,
                termin_platnosci=datetime.date.today(),
                sposob_platnosci='gotowka',
                status='oplacona',
                kwota_oplacona=faktura.suma_brutto,
                dokument_podstawowy=faktura,
                typ_faktury=faktura.typ_faktury
            )

            # Powiąż KP z fakturą
            faktura.kp = kp
            faktura.save()

            # Generate PDF
            html = render_to_string('faktury/kp_pdf.html', {'faktura': kp})
            pdf = HTML(string=html).write_pdf()

            # Save PDF to response
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="kp_{kp.numer}.pdf"'

            return response

    except Exception as e:
        logger.error(f"Błąd generowania KP: {str(e)}")
        messages.error(request, "Wystąpił błąd podczas generowania KP.")
        return HttpResponse("Wygenerowano KP") # Zastąp to właściwą logiką

@login_required
def kp_list(request):
    """Wyświetla listę dokumentów KP użytkownika."""
    kps = Faktura.objects.filter(user=request.user, typ_dokumentu='KP').order_by('-data_wystawienia')
    return render(request, 'faktury/kp_list.html', {'kps': kps})

@login_required
def szczegoly_kp(request, pk):
    kp = get_object_or_404(Faktura, pk=pk, user=request.user)
    return render(request, 'faktury/szczegoly_kp.html', {'kp': kp})

@login_required
def lista_wiadomosci(request):
    # Wiadomości od partnerów
    partner_wiadomosci = Wiadomosc.objects.filter(
        odbiorca_user=request.user, 
        typ_wiadomosci='partner'
    ).order_by('-data_wyslania')
    
    # Wiadomości systemowe
    system_wiadomosci = Wiadomosc.objects.filter(
        odbiorca_user=request.user,
        typ_wiadomosci='system'
    ).order_by('-data_wyslania')

    # Oznacz nieprzeczytane jako przeczytane przy pierwszym otwarciu
    if not request.GET.get('page'):
        partner_wiadomosci.filter(przeczytana=False).update(przeczytana=True)

    return render(request, 'wiadomosci/lista.html', {
        'partner_wiadomosci': partner_wiadomosci,
        'system_wiadomosci': system_wiadomosci
    })

@login_required
def wyslij_wiadomosc(request):
    partnerstwa = Partnerstwo.objects.filter(
        Q(firma1=request.user.firma) | Q(firma2=request.user.firma),
        aktywne=True
    )
    
    if request.method == 'POST':
        form = WiadomoscForm(request.POST, user=request.user)
        if form.is_valid():
            wiadomosc = form.save(commit=False)
            wiadomosc.nadawca = request.user
            wiadomosc.typ_wiadomosci = 'partner'
            
            # Ustaw odbiorcę na podstawie partnerstwa
            partnerstwo = form.cleaned_data['partnerstwo']
            if partnerstwo.firma1 == request.user.firma:
                wiadomosc.odbiorca_user = partnerstwo.firma2.user
            else:
                wiadomosc.odbiorca_user = partnerstwo.firma1.user
            
            wiadomosc.save()
            messages.success(request, "Wiadomość wysłana!")
            return redirect('lista_wiadomosci')
    else:
        form = WiadomoscForm(user=request.user)
        form.fields['partnerstwo'].queryset = partnerstwa

    return render(request, 'wiadomosci/wyslij.html', {'form': form})

@login_required
@staff_member_required
def wyslij_systemowa(request):
    if request.method == 'POST':
        form = SystemowaWiadomoscForm(request.POST)
        if form.is_valid():
            users = User.objects.all()
            for user in users:
                Wiadomosc.objects.create(
                    temat=form.cleaned_data['temat'],
                    tresc=form.cleaned_data['tresc'],
                    odbiorca_user=user,
                    typ_wiadomosci='system'
                )
            messages.success(request, "Wiadomość systemowa wysłana do wszystkich użytkowników")
            return redirect('lista_wiadomosci')
    else:
        form = SystemowaWiadomoscForm()
    
    return render(request, 'wiadomosci/wyslij_systemowa.html', {'form': form})
