from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import FakturaForm, PozycjaFakturyFormSet, KontrahentForm, FirmaForm, ProduktForm, UserRegistrationForm, UserProfileForm, KwotaOplaconaForm #add new form
from .models import Faktura, Kontrahent, Firma, PozycjaFaktury, Produkt
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.core.paginator import Paginator
import requests, json, os, re
from weasyprint import HTML, CSS
from django.template.loader import get_template, render_to_string
from django.conf import settings
import datetime
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
import tempfile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import zipfile
import re
import PyPDF2
import pytesseract

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

def rejestracja(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Po rejestracji, automatycznie zaloguj użytkownika
            #login(request, user) #uzyjemy autologowania django-allauth, wiec ta linia jest niepotrzebna
            messages.success(request, 'Rejestracja przebiegła pomyślnie. Możesz się teraz zalogować.')
            return redirect('account_login')  # Przekierowanie na stronę logowania
    else:
        form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request, 'registration/register.html', {'form': form, 'profile_form': profile_form})

@login_required
def panel_uzytkownika(request):
    faktury = Faktura.objects.filter(user=request.user)

    # Sorting
    sort_by = request.GET.get('sort', '-data_wystawienia')  # Default sort by newest first
    if sort_by.replace('-','') in ['typ_dokumentu', 'numer', 'data_sprzedazy', 'data_wystawienia', 'termin_platnosci', 'nabywca__nazwa', 'suma_netto', 'suma_brutto', 'status']:
        faktury = faktury.order_by(sort_by)
    # Handle Product/Service sorting.  Bit trickier due to the many-to-many relationship.
    elif sort_by.replace('-','') == 'produkt_usluga':
        if sort_by.startswith('-'):
            faktury = faktury.annotate(first_product_name=F('pozycjafaktury__nazwa')).order_by('-first_product_name')
        else:
            faktury = faktury.annotate(first_product_name=F('pozycjafaktury__nazwa')).order_by('first_product_name')
    else:
        faktury = faktury.order_by('-data_wystawienia')  #default value


    # Pobierz dane firmy użytkownika (jeśli istnieją)
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        firma = None

    context = {
        'faktury': faktury,
        'firma': firma,
        'sort_by': sort_by, # Pass the current sort order to the template
    }
    return render(request, 'faktury/panel_uzytkownika.html', context)



@login_required
def kontrahenci(request):
    kontrahenci_list = Kontrahent.objects.filter(user=request.user).order_by('nazwa')
    return render(request, 'faktury/kontrahenci.html', {'kontrahenci': kontrahenci_list})

@login_required
def produkty(request):
    produkty_list = Produkt.objects.filter(user=request.user).order_by('nazwa')
    return render(request, 'faktury/produkty.html', {'produkty': produkty_list})


@login_required
def dodaj_fakture(request):
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Uzupełnij dane swojej firmy przed wystawieniem faktury.")
        return redirect('dodaj_firme')

    if request.method == 'POST':
        faktura_form = FakturaForm(request.POST)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')

        if faktura_form.is_valid() and pozycje_formset.is_valid():
            faktura = faktura_form.save(commit=False)
            faktura.user = request.user
            faktura.sprzedawca = firma

            today = datetime.date.today()
            faktura.numer = f"FV/{today.day}/{today.month}/{today.year}"
            ostatnia_faktura = Faktura.objects.filter(
                user=request.user,
                data_wystawienia__year=today.year,
                data_wystawienia__month=today.month,
            ).order_by('-numer').first()

            if ostatnia_faktura:
                try:
                    ostatni_numer = int(ostatnia_faktura.numer.split('/')[1])
                    faktura.numer = f"FV/{ostatni_numer + 1}/{today.month}/{today.year}"
                except (ValueError, IndexError):
                    faktura.numer = f"FV/1/{today.month}/{today.year}"
            else:
                faktura.numer = f"FV/1/{today.month}/{today.year}"

            faktura.save()

            for pozycja_form in pozycje_formset:
                if pozycja_form.cleaned_data and not pozycja_form.cleaned_data.get('DELETE'): # Sprawdzamy DELETE *tutaj*
                    pozycja = pozycja_form.save(commit=False)
                    pozycja.faktura = faktura
                    pozycja.save()
            messages.success(request, "Faktura została dodana.")
            return redirect('panel_uzytkownika')
        else:
            messages.error(request, "Popraw błędy w formularzu.")

    else: # GET request
        initial_data = {
            'miejsce_wystawienia': firma.miejscowosc,
        }
        faktura_form = FakturaForm(initial=initial_data)
        pozycje_formset = PozycjaFakturyFormSet(prefix='pozycje')

    # Dodaj choices do każdego formularza w formsecie
    for form in pozycje_formset:
        form.fields['jednostka'].widget.choices = JEDNOSTKI

    return render(request, 'faktury/dodaj_fakture.html', {'faktura_form': faktura_form, 'pozycje_formset': pozycje_formset, 'firma': firma})

@login_required
def update_payment(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)

    if request.method == 'POST':
        form = KwotaOplaconaForm(request.POST, instance=faktura)
        if form.is_valid():
            form.save()
            messages.success(request, "Kwota opłacona zaktualizowana.")
            return redirect('panel_uzytkownika')
    else:
        form = KwotaOplaconaForm(instance=faktura)

    return render(request, 'faktury/update_payment.html', {'form': form, 'faktura': faktura})

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

    return render(request, 'faktury/edytuj_fakture.html', {
        'faktura_form': faktura_form,
        'pozycje_formset': pozycje_formset,
        'faktura': faktura,
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
def dodaj_kontrahenta(request):
    if request.method == 'POST':
        form = KontrahentForm(request.POST)
        if form.is_valid():
            kontrahent = form.save(commit=False)
            kontrahent.user = request.user  # Przypisz kontrahenta do zalogowanego użytkownika
            kontrahent.save()
            messages.success(request, "Kontrahent został dodany.")
            return redirect('panel_uzytkownika')  # Przekierowanie na panel
    else:
        form = KontrahentForm()
    return render(request, 'faktury/dodaj_kontrahenta.html', {'form': form})

@login_required
@csrf_exempt
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
            czy_firma=czy_firma  # Ustaw na podstawie parametru z GET
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
    kontrahent = get_object_or_404(Kontrahent, pk=pk, user=request.user)  # Get kontrahent, 404 if not found or not owned by user
    if request.method == 'POST':
        form = KontrahentForm(request.POST, instance=kontrahent)  # Pass instance=kontrahent
        if form.is_valid():
            form.save()
            messages.success(request, 'Kontrahent zaktualizowany')
            return redirect('panel_uzytkownika')  # Or redirect to a detail view
    else:
        form = KontrahentForm(instance=kontrahent)  # Pass instance=kontrahent

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
            return redirect('panel_uzytkownika')
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




@csrf_exempt  # Wyłącz ochronę CSRF TYLKO dla tego widoku (uproszczenie dla AJAX) - w produkcyjnym środowisku użyj innego rozwiązania
@login_required
def pobierz_dane_z_gus(request):
    nip = request.GET.get('nip')
    if not nip:
        return JsonResponse({'error': 'Brak numeru NIP.'}, status=400)

    # Użyj API GUS (https://api.stat.gov.pl/Home/RegonApi) - to jest *przykładowe* zapytanie, musisz dostosować je do faktycznego API
    url = f'https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc/ajax/DaneSzukajPodmioty'
    headers = {
      'Content-Type': 'application/json',
      'sid': '' #umieść tu swój klucz API, musisz sie zarejestrować w GUS
    }

    payload = {
      'jestWojewodztwo': False,
      'pParametryWyszukiwania':
        {
          'Nip': nip,
        }
    }

    try:
      response = requests.post(url, headers=headers, data=json.dumps(payload))
      response.raise_for_status()  # Rzuć wyjątek dla kodów błędów 4xx lub 5xx
      data = response.json()
      # Przetwarzanie odpowiedzi - zakładam, że API zwraca dane w formacie JSON
      # Dostosuj to do *rzeczywistej* struktury odpowiedzi z API GUS
      if data:
            #dane['root']['dane']  # Przykładowa struktura - dostosuj!
            dane_firmy = data.get('root').get('dane')[0] #dostosuj do api
            if dane_firmy:
                return JsonResponse({
                    'nazwa': dane_firmy.get('Nazwa'),
                    'ulica': dane_firmy.get('Ulica'),
                    'numer_domu': dane_firmy.get('NrNieruchomosci'),
                    'numer_mieszkania': dane_firmy.get('NrLokalu'),
                    'kod_pocztowy': dane_firmy.get('KodPocztowy'),
                    'miejscowosc': dane_firmy.get('Miejscowosc'),
                    'regon': dane_firmy.get("Regon"),
                    'kraj' : 'Polska' # to mozna na stale, api gus obsluguje polskie firmy
                })
            else:
                return JsonResponse({'error': 'Nie znaleziono firmy o podanym numerze NIP.'}, status=404)
      else:
        return JsonResponse({'error': 'Nie znaleziono firmy o podanym numerze NIP.'}, status=404)



    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Błąd komunikacji z API GUS: {e}'}, status=500)
    except (KeyError, IndexError) as e:
         return JsonResponse({'error': f'Błąd parsowania danych z API GUS {e}'}, status=500)
@login_required
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
def dodaj_fakture_z_obrazu(request):
    if request.method == 'POST':
        if 'obraz_faktury' not in request.FILES:  # Check if a file was uploaded!
            messages.error(request, "Nie przesłano pliku.")
            return render(request, 'faktury/dodaj_fakture_z_obrazu.html')

        uploaded_file = request.FILES['obraz_faktury']

        if not (uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))):
            messages.error(request, "Nieobsługiwany format pliku. Akceptowane formaty to: PNG, JPG, JPEG, PDF.")
            return render(request, 'faktury/dodaj_fakture_z_obrazu.html')

        tmp_file = None  # Initialize tmp_file to None
        try:
            # --- PDF Handling ---
            if uploaded_file.name.lower().endswith('.pdf'):
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)  # Use the file directly
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"

                    if text.strip():
                        # --- TEXT PARSING (SAME AS BEFORE, BUT using 'text') ---
                        faktura_data = {}
                        pozycje = []
                        in_items_table = False

                        # ... (rest of your parsing logic, as before) ...
                        # (same parsing logic as in previous complete code examples)

                        # --- Create Django Objects (example - adapt to your parsing!) ---
                        if not faktura_data.get('numer'):
                            messages.error(request, "Nie udało się znaleźć numeru faktury.")
                            return redirect('panel_uzytkownika')  # Or a different error page

                        try:
                            firma_sprzedawcy = Firma.objects.get(user=request.user)
                        except Firma.DoesNotExist:
                            messages.error(request, "Uzupełnij dane swojej firmy przed wystawieniem faktury.")
                            return redirect('dodaj_firme')

                        faktura = Faktura(
                            user=request.user,
                            sprzedawca=firma_sprzedawcy,
                            numer=faktura_data['numer'],
                            data_wystawienia=faktura_data.get('data_wystawienia', datetime.date.today()),
                            data_sprzedazy=faktura_data.get('data_sprzedazy', datetime.date.today()),
                            miejsce_wystawienia=faktura_data.get('miejsce_wystawienia', firma_sprzedawcy.miejscowosc),
                            # ... (other Faktura fields) ...
                            typ_dokumentu='FV',
                            sposob_platnosci='przelew',
                            termin_platnosci=datetime.date.today() + datetime.timedelta(days=14),
                            waluta='PLN',
                            status='wystawiona'
                        )


                        if 'nip_nabywcy' in faktura_data:
                            kontrahent, created = Kontrahent.objects.get_or_create(
                                user=request.user,
                                nip=faktura_data['nip_nabywcy'],
                                defaults={'nazwa': 'Tymczasowy Kontrahent', 'ulica': '', 'numer_domu':'', 'kod_pocztowy':'', 'miejscowosc':'', 'kraj':'Polska'}
                            )
                            faktura.nabywca = kontrahent
                        else:
                            messages.error(request, "Nie udało się sparsować NIP nabywcy.")
                            return redirect('panel_uzytkownika')

                        faktura.save()  # Save *before* adding items

                        for pozycja_data in pozycje:
                            pozycja = PozycjaFaktury(
                                faktura=faktura,
                                nazwa=pozycja_data['nazwa'],
                                ilosc=pozycja_data['ilosc'],
                                jednostka=pozycja_data['jednostka'],
                                cena_netto=pozycja_data['cena_netto'],
                                vat=pozycja_data['vat'],
                                rabat=pozycja_data.get('rabat', 0)  # Use get() with a default
                            )
                            pozycja.save()

                        messages.success(request, f"Faktura {faktura.numer} została dodana z obrazu.")
                        return redirect('panel_uzytkownika')  # Or to a detail view

                except PyPDF2.errors.PdfReadError as e:
                    messages.error(request, f"Nie udało się otworzyć pliku PDF: {e}")
                    return render(request, 'faktury/dodaj_fakture_z_obrazu.html')
                except Exception as e:
                    messages.error(request, f"Błąd ogólny przy przetwarzaniu PDF: {e}")
                    return render(request, 'faktury/dodaj_fakture_z_obrazu.html')

            # --- OCR (if not a PDF, or if PDF parsing failed) ---
            else:
                # Zapisz obraz tymczasowo, *jeśli* to nie jest PDF
                path = default_storage.save('tmp/' + obraz.name, ContentFile(obraz.read()))
                tmp_file = os.path.join(settings.MEDIA_ROOT, path)
                try:
                    img = Image.open(tmp_file)
                    text = pytesseract.image_to_string(img, lang='pol')
                    print(text)  # For debugging - see what Tesseract extracts

                    # --- PARSING LOGIC (IDENTICAL TO THE PDF SECTION - use the extracted 'text') ---
                    faktura_data = {}  # Dictionary to store extracted data
                    pozycje = []
                    in_items_table = False

                    # ... (rest of your parsing logic, *exactly* as in the PDF section) ...
                    # --- General Information ---
                    for line in text.splitlines():
                        line = line.strip()  # Remove leading/trailing whitespace
                        if not line:
                            continue

                        # --- General Information ---
                        if match := re.search(r'Faktura\s+nr\s*[:\.]?\s*([A-Za-z0-9\-/]+)', line, re.IGNORECASE):
                            faktura_data['numer'] = match.group(1).strip()
                            continue

                        elif match := re.search(r'Data\s+wystawienia\s*[:\.]?\s*(\d{4}-\d{2}-\d{2}|\d{2}[./-]\d{2}[./-]\d{4})', line, re.IGNORECASE):
                            try:
                                # Attempt parsing in multiple date formats
                                date_str = match.group(1)
                                for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d-%m-%Y', '%d/%m/%Y'):
                                    try:
                                        faktura_data['data_wystawienia'] = datetime.datetime.strptime(date_str, fmt).date()
                                        break  # Stop trying formats once one works
                                    except ValueError:
                                        pass
                                else:
                                    messages.warning(request, f"Nie udało się sparsować daty wystawienia: {date_str}")
                            except:
                                messages.warning(request, "Problem z parsowaniem daty wystawienia")
                            continue


                        elif match := re.search(r'Data\s+sprzedaży\s*[:\.]?\s*(\d{4}-\d{2}-\d{2}|\d{2}[./-]\d{2}[./-]\d{4})', line, re.IGNORECASE):
                            try:
                                date_str = match.group(1)
                                for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d-%m-%Y', '%d/%m/%Y'):
                                    try:
                                        faktura_data['data_sprzedazy'] = datetime.datetime.strptime(date_str, fmt).date()
                                        break
                                    except ValueError:
                                        pass
                                else:
                                     messages.warning(request, f"Nie udało się sparsować daty sprzedaży: {date_str}")
                            except:
                                 messages.warning(request, "Problem z parsowaniem daty sprzedaży")
                            continue

                        elif match := re.search(r'Miejsce\s+wystawienia\s*[:\.]?\s*(.+)', line, re.IGNORECASE):
                            faktura_data['miejsce_wystawienia'] = match.group(1).strip()
                            continue

                        # --- Seller/Buyer Data (Simplified - needs robust handling) ---

                        elif "Sprzedawca" in line:
                            # VERY basic example - needs to be much more robust
                            try:
                                lines_sprzedawca = text.split("Sprzedawca")[1].split("Nabywca")[0] #Get text between "Sprzedawca" and "Nabywca"
                                match_nip_sprzedawcy = re.search(r'NIP[:\s]*(\d+)', lines_sprzedawca, re.IGNORECASE)
                                nip_sprzedawcy = match_nip_sprzedawcy.group(1) if match_nip_sprzedawcy else None
                                if nip_sprzedawcy:
                                    faktura_data['nip_sprzedawcy'] = nip_sprzedawcy
                            except:
                                 messages.warning(request, f"Problem z parsowaniem danych sprzedawcy")
                            continue

                        elif "Nabywca" in line:
                             try:
                                lines_nabywcy = text.split("Nabywca")[1].split("Pozycje na fakturze")[0]
                                match_nip_nabywcy = re.search(r'NIP[:\s]*(\d+)', lines_nabywcy, re.IGNORECASE)
                                nip_nabywcy = match_nip_nabywcy.group(1) if match_nip_nabywcy else None
                                if nip_nabywcy:
                                    faktura_data['nip_nabywcy'] = nip_nabywcy
                             except:
                                 messages.warning(request, f"Problem z parsowaniem danych nabywcy")
                             continue


                        # --- Invoice Items ---
                        elif "Pozycje na fakturze" in line:
                            in_items_table = True  # We've entered the items table
                            continue  # Skip this header line

                        elif in_items_table:
                            # VERY basic item parsing.  This WILL need adjustment!
                            match_item = re.search(r'^\s*([\w\s]+)\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\d+%|zw\.?)\s+([\d,\.]+)\s+([\d,\.]+)', line)
                            #      1. Nazwa  2.Rabat  3. ilosc 4.jednostka  5.cena_netto   6. vat       7.wartosc_netto  8.wartosc_brutto

                            if match_item:
                                try:
                                    nazwa = match_item.group(1).strip()
                                    rabat =  match_item.group(2).strip()
                                    ilosc = float(match_item.group(3).replace(',', '.'))
                                    jednostka = match_item.group(4).strip()
                                    cena_netto = Decimal(match_item.group(5).replace(',', '.'))
                                    vat = match_item.group(6).strip()
                                    wartosc_netto_str = match_item.group(7).replace(',', '.')
                                    wartosc_brutto_str = match_item.group(8).replace(',', '.')

                                    # Check if the values can be converted to float
                                    try:
                                        wartosc_netto = Decimal(wartosc_netto_str)
                                        wartosc_brutto = Decimal(wartosc_brutto_str)
                                    except:
                                        messages.warning(request, f"Nieprawidłowy format wartości netto/brutto w pozycji: {line}")
                                        continue # Skip this line
                                    if "zw" in vat.lower():
                                        vat = "zw"
                                    else:
                                        vat = vat.replace("%", "").strip() # Remove %

                                    pozycje.append({
                                        'nazwa': nazwa,
                                        'rabat': rabat,
                                        'ilosc': ilosc,
                                        'jednostka': jednostka,
                                        'cena_netto': cena_netto,
                                        'vat': vat,
                                        'wartosc_netto': wartosc_netto,
                                        'wartosc_brutto': wartosc_brutto,
                                    })
                                except:
                                     messages.warning(request, f"Problem z parsowaniem pozycji: {line}")
                                     continue # Skip this line
                            elif line.strip() == "": #Empty line
                                continue
                            else:
                                #This line is not an empty line, neither an item
                                in_items_table = False #We assume that we are out of table
                    #Koniec petli parsujacej

                    # --- Create Django Objects ---

                    if not faktura_data.get('numer'):
                        messages.error(request, "Nie udało się znaleźć numeru faktury.")
                        return redirect('panel_uzytkownika')  # Or wherever is appropriate

                    # Get or create Firma (assuming user is logged in)
                    try:
                        firma_sprzedawcy = Firma.objects.get(user=request.user)
                    except Firma.DoesNotExist:
                        messages.error(request, "Uzupełnij dane swojej firmy przed wystawieniem faktury.")
                        return redirect('dodaj_firme')

                    faktura = Faktura(
                        user=request.user,
                        sprzedawca=firma_sprzedawcy,
                        numer=faktura_data['numer'],
                        data_wystawienia=faktura_data.get('data_wystawienia', datetime.date.today()),  # Use get with default
                        data_sprzedazy=faktura_data.get('data_sprzedazy', datetime.date.today()),miejsce_wystawienia=faktura_data.get('miejsce_wystawienia', firma_sprzedawcy.miejscowosc),
                        #Dodaj inne pola
                        typ_dokumentu = 'FV',
                        sposob_platnosci = 'przelew',
                        termin_platnosci = datetime.date.today() + datetime.timedelta(days=14),
                        waluta = 'PLN',
                        status = 'wystawiona'
                    )

                    # --- Kontrahent Handling ---
                    # VERY BASIC example.  You'll need more robust logic.
                    if 'nip_nabywcy' in faktura_data:
                        kontrahent, created = Kontrahent.objects.get_or_create(
                            user=request.user,
                            nip=faktura_data['nip_nabywcy'],
                            defaults={'nazwa': 'Tymczasowy Kontrahent', 'ulica': '', 'numer_domu':'', 'kod_pocztowy':'', 'miejscowosc':'', 'kraj':'Polska'} #Dodaj brakujace pola
                        )
                        faktura.nabywca = kontrahent
                    else:
                        messages.error(request, "Nie udało się sparsować NIP nabywcy.")
                        return redirect('panel_uzytkownika')  # Or some other error handling



                    faktura.save()  # Save *before* adding items

                    # Add invoice items
                    for pozycja_data in pozycje:
                        pozycja = PozycjaFaktury(
                            faktura=faktura,
                            nazwa=pozycja_data['nazwa'],
                            ilosc=pozycja_data['ilosc'],
                            jednostka=pozycja_data['jednostka'],
                            cena_netto=pozycja_data['cena_netto'],
                            vat=pozycja_data['vat'],
                            rabat = pozycja_data.get('rabat', 0) #Pobierz rabat
                        )
                        pozycja.save()


                    messages.success(request, f"Faktura {faktura.numer} została dodana z obrazu.")
                    return redirect('panel_uzytkownika')

        except Exception as e:
            messages.error(request, f"Błąd podczas przetwarzania faktury (OCR): {e}")
            return redirect('panel_uzytkownika')

        finally:
            print("Usuwam plik tymczasowy")
            # *Always* remove the temporary file, even if there's an error
            if tmp_file and os.path.exists(tmp_file):  # Check if tmp_file is defined *and* exists
                os.remove(tmp_file)

    else:
        return render(request, 'faktury/dodaj_fakture_z_obrazu.html')
