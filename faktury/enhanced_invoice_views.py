"""
Enhanced invoice views for Polish VAT law compliance
Wszystkie widoki dla dokumentów zgodnych z polskim prawem
"""
import datetime
import logging
from decimal import Decimal
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum

from .models import Faktura, Firma, Kontrahent, Produkt, PozycjaFaktury
from .enhanced_forms import (
    EnhancedFakturaForm, EnhancedPozycjaFakturyFormSet,
    FakturaProFormaForm, FakturaKorygujacaForm, RachunekForm,
    FakturaZaliczkowaForm, DokumentKasowyForm
)
from .utils import generuj_numer

logger = logging.getLogger(__name__)


def generuj_numer_dokumentu(typ_dokumentu, user, data_wystawienia=None):
    """
    Generuje numer dokumentu zgodnie z polskimi standardami
    """
    if data_wystawienia is None:
        data_wystawienia = datetime.date.today()
    
    year = data_wystawienia.year
    month = data_wystawienia.month
    
    # Maping typów dokumentów na prefiksy
    prefiksy = {
        'FV': 'FV',      # Faktura VAT
        'FVS': 'FVS',    # Faktura VAT Sprzedażowa
        'FVK': 'FVK',    # Faktura VAT Kosztowa
        'FP': 'FP',      # Faktura Pro Forma
        'KOR': 'KOR',    # Faktura Korygująca
        'KP': 'KP',      # Korekta Pozytywna
        'KN': 'KN',      # Korekta Negatywna
        'FZ': 'FZ',      # Faktura Zaliczkowa
        'FK': 'FK',      # Faktura Końcowa
        'RC': 'RC',      # Rachunek
        'PAR': 'PAR',    # Paragon
        'KP_DOK': 'KP',  # Dokument Kasowy Przychodowy
        'KW_DOK': 'KW',  # Dokument Kasowy Rozchodowy
        'WDT': 'WDT',    # WDT
        'IMP': 'IMP',    # Import
        'EXP': 'EXP',    # Eksport
    }
    
    prefiks = prefiksy.get(typ_dokumentu, 'DOK')
    
    # Znajdź ostatni numer dla tego typu dokumentu w tym roku
    last_doc = Faktura.objects.filter(
        user=user,
        typ_dokumentu=typ_dokumentu,
        data_wystawienia__year=year
    ).order_by('-numer').first()
    
    if last_doc and last_doc.numer:
        try:
            # Wyciągnij numer z formatu: PREFIKS/NR/MM/YYYY
            parts = last_doc.numer.split('/')
            if len(parts) >= 2:
                last_number = int(parts[1])
                next_number = last_number + 1
            else:
                next_number = 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1
    
    return f"{prefiks}/{next_number:04d}/{month:02d}/{year}"


@login_required
def lista_dokumentow(request):
    """Lista wszystkich dokumentów użytkownika"""
    
    # Filtry
    typ_filter = request.GET.get('typ', '')
    status_filter = request.GET.get('status', '')
    data_od = request.GET.get('data_od', '')
    data_do = request.GET.get('data_do', '')
    search = request.GET.get('search', '')
    
    dokumenty = Faktura.objects.filter(user=request.user)
    
    # Zastosuj filtry
    if typ_filter:
        dokumenty = dokumenty.filter(typ_dokumentu=typ_filter)
    
    if status_filter:
        dokumenty = dokumenty.filter(status=status_filter)
    
    if data_od:
        try:
            data_od_parsed = datetime.datetime.strptime(data_od, '%Y-%m-%d').date()
            dokumenty = dokumenty.filter(data_wystawienia__gte=data_od_parsed)
        except ValueError:
            pass
    
    if data_do:
        try:
            data_do_parsed = datetime.datetime.strptime(data_do, '%Y-%m-%d').date()
            dokumenty = dokumenty.filter(data_wystawienia__lte=data_do_parsed)
        except ValueError:
            pass
    
    if search:
        dokumenty = dokumenty.filter(
            Q(numer__icontains=search) |
            Q(nabywca__nazwa__icontains=search) |
            Q(nabywca__nip__icontains=search)
        )
    
    dokumenty = dokumenty.order_by('-data_wystawienia', '-numer')
    
    # Paginacja
    paginator = Paginator(dokumenty, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statystyki
    stats = {
        'total_count': dokumenty.count(),
        'total_value': dokumenty.aggregate(
            suma=Sum('pozycjafaktury__wartosc_brutto')
        )['suma'] or Decimal('0.00'),
        'unpaid_count': dokumenty.filter(
            status__in=['wystawiona', 'wyslana', 'dostarczona']
        ).count(),
        'overdue_count': dokumenty.filter(
            status__in=['wystawiona', 'wyslana', 'dostarczona'],
            termin_platnosci__lt=datetime.date.today()
        ).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'typ_filter': typ_filter,
        'status_filter': status_filter,
        'data_od': data_od,
        'data_do': data_do,
        'search': search,
        'typy_dokumentow': Faktura.TYP_DOKUMENTU_CHOICES,
        'statusy': Faktura.STATUS_CHOICES,
    }
    
    return render(request, 'faktury/enhanced/lista_dokumentow.html', context)


@login_required
def dodaj_fakture_vat(request):
    """Dodaj fakturę VAT - główny formularz"""
    
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw uzupełnij dane swojej firmy.")
        return redirect('dodaj_firme')
    
    if request.method == 'POST':
        form = EnhancedFakturaForm(request.POST)
        formset = EnhancedPozycjaFakturyFormSet(request.POST, prefix='pozycje')
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Zapisz fakturę
                    faktura = form.save(commit=False)
                    faktura.user = request.user
                    faktura.sprzedawca = firma
                    faktura.typ_dokumentu = 'FV'
                    
                    # Generuj numer
                    if form.cleaned_data.get('auto_numer', True):
                        faktura.numer = generuj_numer_dokumentu(
                            'FV', request.user, faktura.data_wystawienia
                        )
                    else:
                        faktura.numer = form.cleaned_data['wlasny_numer']
                    
                    # Ustaw termin płatności z dni_platnosci
                    dni_platnosci = form.cleaned_data.get('dni_platnosci', 14)
                    if dni_platnosci:
                        faktura.termin_platnosci = (
                            faktura.data_wystawienia + 
                            datetime.timedelta(days=dni_platnosci)
                        )
                    
                    faktura.save()
                    
                    # Zapisz pozycje
                    pozycje = formset.save(commit=False)
                    for pozycja in pozycje:
                        pozycja.faktura = faktura
                        pozycja.save()
                    
                    messages.success(request, f"Faktura {faktura.numer} została utworzona.")
                    return redirect('szczegoly_faktury', pk=faktura.pk)
                    
            except Exception as e:
                logger.error(f"Błąd przy tworzeniu faktury: {str(e)}")
                messages.error(request, "Wystąpił błąd przy zapisie faktury.")
        else:
            messages.error(request, "Popraw błędy w formularzu.")
    
    else:
        # Początkowe wartości
        initial_data = {
            'data_wystawienia': datetime.date.today(),
            'data_sprzedazy': datetime.date.today(),
            'miejsce_wystawienia': firma.miejscowosc or 'Warszawa',
            'sposob_platnosci': 'przelew',
            'status': 'wystawiona',
            'waluta': 'PLN',
        }
        
        form = EnhancedFakturaForm(initial=initial_data)
        formset = EnhancedPozycjaFakturyFormSet(prefix='pozycje')
    
    context = {
        'form': form,
        'formset': formset,
        'firma': firma,
        'title': 'Nowa faktura VAT',
        'typ_dokumentu': 'FV',
    }
    
    return render(request, 'faktury/enhanced/dodaj_fakture.html', context)


@login_required
def dodaj_proforma(request):
    """Dodaj fakturę pro forma"""
    
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw uzupełnij dane swojej firmy.")
        return redirect('dodaj_firme')
    
    if request.method == 'POST':
        form = FakturaProFormaForm(request.POST)
        formset = EnhancedPozycjaFakturyFormSet(request.POST, prefix='pozycje')
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    faktura = form.save(commit=False)
                    faktura.user = request.user
                    faktura.sprzedawca = firma
                    faktura.typ_dokumentu = 'FP'
                    faktura.status = 'projekt'  # Proforma ma status projekt
                    
                    faktura.numer = generuj_numer_dokumentu(
                        'FP', request.user, faktura.data_wystawienia
                    )
                    
                    faktura.save()
                    
                    pozycje = formset.save(commit=False)
                    for pozycja in pozycje:
                        pozycja.faktura = faktura
                        pozycja.save()
                    
                    messages.success(request, f"Proforma {faktura.numer} została utworzona.")
                    return redirect('szczegoly_faktury', pk=faktura.pk)
                    
            except Exception as e:
                logger.error(f"Błąd przy tworzeniu proformy: {str(e)}")
                messages.error(request, "Wystąpił błąd przy zapisie proformy.")
    
    else:
        initial_data = {
            'data_wystawienia': datetime.date.today(),
            'data_sprzedazy': datetime.date.today(),
            'miejsce_wystawienia': firma.miejscowosc or 'Warszawa',
            'sposob_platnosci': 'przelew',
            'waluta': 'PLN',
        }
        
        form = FakturaProFormaForm(initial=initial_data)
        formset = EnhancedPozycjaFakturyFormSet(prefix='pozycje')
    
    context = {
        'form': form,
        'formset': formset,
        'firma': firma,
        'title': 'Nowa faktura pro forma',
        'typ_dokumentu': 'FP',
    }
    
    return render(request, 'faktury/enhanced/dodaj_fakture.html', context)


@login_required
def dodaj_korekte(request, faktura_id=None):
    """Dodaj fakturę korygującą"""
    
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw uzupełnij dane swojej firmy.")
        return redirect('dodaj_firme')
    
    dokument_podstawowy = None
    if faktura_id:
        dokument_podstawowy = get_object_or_404(
            Faktura, pk=faktura_id, user=request.user
        )
    
    if request.method == 'POST':
        form = FakturaKorygujacaForm(request.POST, user=request.user)
        formset = EnhancedPozycjaFakturyFormSet(request.POST, prefix='pozycje')
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    faktura = form.save(commit=False)
                    faktura.user = request.user
                    faktura.sprzedawca = firma
                    faktura.typ_dokumentu = 'KOR'
                    
                    faktura.numer = generuj_numer_dokumentu(
                        'KOR', request.user, faktura.data_wystawienia
                    )
                    
                    faktura.save()
                    
                    pozycje = formset.save(commit=False)
                    for pozycja in pozycje:
                        pozycja.faktura = faktura
                        pozycja.save()
                    
                    # Zaktualizuj status dokumentu podstawowego
                    if faktura.dokument_podstawowy:
                        faktura.dokument_podstawowy.status = 'skorygowana'
                        faktura.dokument_podstawowy.save()
                    
                    messages.success(request, f"Korekta {faktura.numer} została utworzona.")
                    return redirect('szczegoly_faktury', pk=faktura.pk)
                    
            except Exception as e:
                logger.error(f"Błąd przy tworzeniu korekty: {str(e)}")
                messages.error(request, "Wystąpił błąd przy zapisie korekty.")
    
    else:
        initial_data = {
            'data_wystawienia': datetime.date.today(),
            'miejsce_wystawienia': firma.miejscowosc or 'Warszawa',
            'sposob_platnosci': 'przelew',
            'waluta': 'PLN',
        }
        
        if dokument_podstawowy:
            initial_data.update({
                'dokument_podstawowy': dokument_podstawowy,
                'nabywca': dokument_podstawowy.nabywca,
                'data_sprzedazy': dokument_podstawowy.data_sprzedazy,
                'termin_platnosci': dokument_podstawowy.termin_platnosci,
                'sposob_platnosci': dokument_podstawowy.sposob_platnosci,
                'waluta': dokument_podstawowy.waluta,
            })
        
        form = FakturaKorygujacaForm(initial=initial_data, user=request.user)
        formset = EnhancedPozycjaFakturyFormSet(prefix='pozycje')
    
    context = {
        'form': form,
        'formset': formset,
        'firma': firma,
        'dokument_podstawowy': dokument_podstawowy,
        'title': 'Nowa faktura korygująca',
        'typ_dokumentu': 'KOR',
    }
    
    return render(request, 'faktury/enhanced/dodaj_korekte.html', context)


@login_required
def dodaj_rachunek(request):
    """Dodaj rachunek (dla małych kwot, bez VAT)"""
    
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw uzupełnij dane swojej firmy.")
        return redirect('dodaj_firme')
    
    if request.method == 'POST':
        form = RachunekForm(request.POST)
        formset = EnhancedPozycjaFakturyFormSet(request.POST, prefix='pozycje')
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    faktura = form.save(commit=False)
                    faktura.user = request.user
                    faktura.sprzedawca = firma
                    faktura.typ_dokumentu = 'RC'
                    
                    faktura.numer = generuj_numer_dokumentu(
                        'RC', request.user, faktura.data_wystawienia
                    )
                    
                    faktura.save()
                    
                    pozycje = formset.save(commit=False)
                    for pozycja in pozycje:
                        pozycja.faktura = faktura
                        pozycja.vat = 'zw'  # Rachunek bez VAT
                        pozycja.save()
                    
                    messages.success(request, f"Rachunek {faktura.numer} został utworzony.")
                    return redirect('szczegoly_faktury', pk=faktura.pk)
                    
            except Exception as e:
                logger.error(f"Błąd przy tworzeniu rachunku: {str(e)}")
                messages.error(request, "Wystąpił błąd przy zapisie rachunku.")
    
    else:
        initial_data = {
            'data_wystawienia': datetime.date.today(),
            'data_sprzedazy': datetime.date.today(),
            'miejsce_wystawienia': firma.miejscowosc or 'Warszawa',
            'sposob_platnosci': 'gotowka',
            'status': 'wystawiona',
            'waluta': 'PLN',
            'zwolnienie_z_vat': True,
            'powod_zwolnienia': 'art43_1',
        }
        
        form = RachunekForm(initial=initial_data)
        formset = EnhancedPozycjaFakturyFormSet(prefix='pozycje')
    
    context = {
        'form': form,
        'formset': formset,
        'firma': firma,
        'title': 'Nowy rachunek',
        'typ_dokumentu': 'RC',
    }
    
    return render(request, 'faktury/enhanced/dodaj_fakture.html', context)


@login_required
def dodaj_fakture_zaliczkowa(request):
    """Dodaj fakturę zaliczkową"""
    
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw uzupełnij dane swojej firmy.")
        return redirect('dodaj_firme')
    
    if request.method == 'POST':
        form = FakturaZaliczkowaForm(request.POST)
        formset = EnhancedPozycjaFakturyFormSet(request.POST, prefix='pozycje')
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    faktura = form.save(commit=False)
                    faktura.user = request.user
                    faktura.sprzedawca = firma
                    faktura.typ_dokumentu = 'FZ'
                    
                    faktura.numer = generuj_numer_dokumentu(
                        'FZ', request.user, faktura.data_wystawienia
                    )
                    
                    faktura.save()
                    
                    # Zapisz pozycje z uwzględnieniem procentu zaliczki
                    procent_zaliczki = form.cleaned_data['procent_zaliczki']
                    pozycje = formset.save(commit=False)
                    
                    for pozycja in pozycje:
                        pozycja.faktura = faktura
                        # Przelicz cenę na zaliczkę
                        pozycja.cena_netto = pozycja.cena_netto * (procent_zaliczki / 100)
                        pozycja.save()
                    
                    messages.success(request, f"Faktura zaliczkowa {faktura.numer} została utworzona.")
                    return redirect('szczegoly_faktury', pk=faktura.pk)
                    
            except Exception as e:
                logger.error(f"Błąd przy tworzeniu faktury zaliczkowej: {str(e)}")
                messages.error(request, "Wystąpił błąd przy zapisie faktury zaliczkowej.")
    
    else:
        initial_data = {
            'data_wystawienia': datetime.date.today(),
            'data_sprzedazy': datetime.date.today(),
            'miejsce_wystawienia': firma.miejscowosc or 'Warszawa',
            'sposob_platnosci': 'przelew',
            'status': 'wystawiona',
            'waluta': 'PLN',
            'procent_zaliczki': Decimal('30.00'),  # Domyślnie 30%
        }
        
        form = FakturaZaliczkowaForm(initial=initial_data)
        formset = EnhancedPozycjaFakturyFormSet(prefix='pozycje')
    
    context = {
        'form': form,
        'formset': formset,
        'firma': firma,
        'title': 'Nowa faktura zaliczkowa',
        'typ_dokumentu': 'FZ',
    }
    
    return render(request, 'faktury/enhanced/dodaj_fakture_zaliczkowa.html', context)


@login_required
def dodaj_dokument_kasowy(request):
    """Dodaj dokument kasowy (KP/KW)"""
    
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Najpierw uzupełnij dane swojej firmy.")
        return redirect('dodaj_firme')
    
    if request.method == 'POST':
        form = DokumentKasowyForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    dokument = form.save(commit=False)
                    dokument.user = request.user
                    dokument.sprzedawca = firma
                    
                    rodzaj = form.cleaned_data['rodzaj_operacji']
                    dokument.typ_dokumentu = 'KP_DOK' if rodzaj == 'wplata' else 'KW_DOK'
                    
                    dokument.numer = generuj_numer_dokumentu(
                        dokument.typ_dokumentu, request.user, dokument.data_wystawienia
                    )
                    
                    # Utwórz pozycję dla operacji kasowej
                    dokument.save()
                    
                    PozycjaFaktury.objects.create(
                        faktura=dokument,
                        nazwa=form.cleaned_data['nazwa_operacji'],
                        ilosc=1,
                        jednostka='szt',
                        cena_netto=form.cleaned_data['kwota'],
                        vat='zw'  # Operacje kasowe bez VAT
                    )
                    
                    messages.success(request, f"Dokument kasowy {dokument.numer} został utworzony.")
                    return redirect('szczegoly_faktury', pk=dokument.pk)
                    
            except Exception as e:
                logger.error(f"Błąd przy tworzeniu dokumentu kasowego: {str(e)}")
                messages.error(request, "Wystąpił błąd przy zapisie dokumentu kasowego.")
    
    else:
        initial_data = {
            'data_wystawienia': datetime.date.today(),
            'miejsce_wystawienia': firma.miejscowosc or 'Warszawa',
            'rodzaj_operacji': 'wplata',
        }
        
        form = DokumentKasowyForm(initial=initial_data)
    
    context = {
        'form': form,
        'firma': firma,
        'title': 'Nowy dokument kasowy',
    }
    
    return render(request, 'faktury/enhanced/dodaj_dokument_kasowy.html', context)


@login_required
def konwertuj_proforma_na_fakture(request, proforma_id):
    """Konwertuj fakturę pro forma na fakturę VAT"""
    
    proforma = get_object_or_404(
        Faktura, pk=proforma_id, user=request.user, typ_dokumentu='FP'
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Utwórz nową fakturę na podstawie proformy
                faktura = Faktura.objects.create(
                    user=request.user,
                    typ_dokumentu='FV',
                    dokument_podstawowy=proforma,
                    sprzedawca=proforma.sprzedawca,
                    nabywca=proforma.nabywca,
                    data_wystawienia=datetime.date.today(),
                    data_sprzedazy=proforma.data_sprzedazy,
                    termin_platnosci=proforma.termin_platnosci,
                    miejsce_wystawienia=proforma.miejsce_wystawienia,
                    sposob_platnosci=proforma.sposob_platnosci,
                    waluta=proforma.waluta,
                    status='wystawiona',
                    numer=generuj_numer_dokumentu('FV', request.user),
                    zwolnienie_z_vat=proforma.zwolnienie_z_vat,
                    powod_zwolnienia=proforma.powod_zwolnienia,
                    numer_konta_bankowego=proforma.numer_konta_bankowego,
                    tytul_przelewu=proforma.tytul_przelewu,
                    wystawca=proforma.wystawca,
                    odbiorca=proforma.odbiorca,
                    uwagi=proforma.uwagi,
                )
                
                # Skopiuj pozycje
                for pozycja in proforma.pozycjafaktury_set.all():
                    PozycjaFaktury.objects.create(
                        faktura=faktura,
                        nazwa=pozycja.nazwa,
                        ilosc=pozycja.ilosc,
                        jednostka=pozycja.jednostka,
                        cena_netto=pozycja.cena_netto,
                        vat=pozycja.vat,
                        rabat=pozycja.rabat,
                        rabat_typ=pozycja.rabat_typ,
                    )
                
                # Zaktualizuj status proformy
                proforma.status = 'zaksiegowana'
                proforma.save()
                
                messages.success(
                    request, 
                    f"Proforma {proforma.numer} została przekonwertowana na fakturę {faktura.numer}."
                )
                return redirect('szczegoly_faktury', pk=faktura.pk)
                
        except Exception as e:
            logger.error(f"Błąd przy konwersji proformy: {str(e)}")
            messages.error(request, "Wystąpił błąd przy konwersji proformy.")
    
    context = {
        'proforma': proforma,
        'title': f'Konwersja proformy {proforma.numer} na fakturę VAT',
    }
    
    return render(request, 'faktury/enhanced/konwertuj_proforma.html', context)


@login_required
def raport_vat(request):
    """Raport VAT dla dokumentów"""
    
    # Parametry raportu
    data_od = request.GET.get('data_od', '')
    data_do = request.GET.get('data_do', '')
    
    if not data_od:
        # Domyślnie bieżący miesiąc
        today = datetime.date.today()
        data_od = today.replace(day=1).strftime('%Y-%m-%d')
    
    if not data_do:
        # Koniec bieżącego miesiąca
        today = datetime.date.today()
        next_month = today.replace(day=28) + datetime.timedelta(days=4)
        data_do = (next_month - datetime.timedelta(days=next_month.day)).strftime('%Y-%m-%d')
    
    try:
        data_od_parsed = datetime.datetime.strptime(data_od, '%Y-%m-%d').date()
        data_do_parsed = datetime.datetime.strptime(data_do, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "Nieprawidłowy format daty.")
        return redirect('raport_vat')
    
    # Faktury sprzedaży
    faktury_sprzedaz = Faktura.objects.filter(
        user=request.user,
        typ_dokumentu__in=['FV', 'FVS'],
        data_sprzedazy__range=[data_od_parsed, data_do_parsed]
    ).order_by('data_sprzedazy', 'numer')
    
    # Faktury kosztów
    faktury_koszty = Faktura.objects.filter(
        user=request.user,
        typ_dokumentu__in=['FVK'],
        data_sprzedazy__range=[data_od_parsed, data_do_parsed]
    ).order_by('data_sprzedazy', 'numer')
    
    # Oblicz sumy VAT
    def oblicz_sumy_vat(faktury):
        sumy = {}
        for faktura in faktury:
            for pozycja in faktura.pozycjafaktury_set.all():
                stawka = pozycja.vat
                if stawka not in sumy:
                    sumy[stawka] = {
                        'netto': Decimal('0.00'),
                        'vat': Decimal('0.00'),
                        'brutto': Decimal('0.00')
                    }
                
                sumy[stawka]['netto'] += pozycja.wartosc_netto
                sumy[stawka]['vat'] += pozycja.kwota_vat if hasattr(pozycja, 'kwota_vat') else Decimal('0.00')
                sumy[stawka]['brutto'] += pozycja.wartosc_brutto
        
        return sumy
    
    sumy_sprzedaz = oblicz_sumy_vat(faktury_sprzedaz)
    sumy_koszty = oblicz_sumy_vat(faktury_koszty)
    
    # VAT do zapłaty
    vat_nalezny = sum([s['vat'] for s in sumy_sprzedaz.values()])
    vat_naliczony = sum([s['vat'] for s in sumy_koszty.values()])
    vat_do_zaplaty = vat_nalezny - vat_naliczony
    
    context = {
        'data_od': data_od,
        'data_do': data_do,
        'faktury_sprzedaz': faktury_sprzedaz,
        'faktury_koszty': faktury_koszty,
        'sumy_sprzedaz': sumy_sprzedaz,
        'sumy_koszty': sumy_koszty,
        'vat_nalezny': vat_nalezny,
        'vat_naliczony': vat_naliczony,
        'vat_do_zaplaty': vat_do_zaplaty,
    }
    
    return render(request, 'faktury/enhanced/raport_vat.html', context)


@login_required
def api_kontrahenci_autocomplete(request):
    """API dla autocomplete kontrahentów"""
    term = request.GET.get('term', '')
    
    kontrahenci = Kontrahent.objects.filter(
        firma__user=request.user,
        nazwa__icontains=term
    )[:10]
    
    results = []
    for k in kontrahenci:
        results.append({
            'id': k.id,
            'label': f"{k.nazwa} ({k.nip})",
            'value': k.nazwa,
            'nip': k.nip,
            'adres': f"{k.ulica}, {k.kod_pocztowy} {k.miejscowosc}",
        })
    
    return JsonResponse(results, safe=False)


@login_required
def api_produkty_autocomplete(request):
    """API dla autocomplete produktów"""
    term = request.GET.get('term', '')
    
    produkty = Produkt.objects.filter(
        user=request.user,
        nazwa__icontains=term
    )[:10]
    
    results = []
    for p in produkty:
        results.append({
            'id': p.id,
            'label': p.nazwa,
            'value': p.nazwa,
            'cena': str(p.cena),
            'jednostka': p.jednostka,
        })
    
    return JsonResponse(results, safe=False)


@login_required
def api_kontrahenci_create(request):
    """API do tworzenia nowego kontrahenta"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metoda nie dozwolona'})
    
    try:
        # Get user's company
        firma = Firma.objects.filter(user=request.user).first()
        if not firma:
            return JsonResponse({'success': False, 'error': 'Brak przypisanej firmy'})
        
        # Create new contractor
        kontrahent = Kontrahent.objects.create(
            firma=firma,
            nazwa=request.POST.get('nazwa'),
            nip=request.POST.get('nip', ''),
            regon=request.POST.get('regon', ''),
            email=request.POST.get('email', ''),
            ulica=request.POST.get('adres', ''),
            kod_pocztowy=request.POST.get('kod_pocztowy', ''),
            miejscowosc=request.POST.get('miasto', ''),
            telefon=request.POST.get('telefon', '')
        )
        
        return JsonResponse({
            'success': True,
            'kontrahent': {
                'id': kontrahent.id,
                'nazwa': kontrahent.nazwa,
                'nip': kontrahent.nip
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating contractor: {e}")
        return JsonResponse({'success': False, 'error': str(e)})
