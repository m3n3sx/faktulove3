from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

def edytuj_fakture(request, pk):
    return HttpResponse(f"Editing invoice with ID: {pk}")

from django.shortcuts import render, get_object_or_404, redirect
from ..models import Faktura
from ..forms import FakturaForm

def edytuj_fakture(request, pk):
    faktura = get_object_or_404(Faktura, pk=pk)
    if request.method == "POST":
        form = FakturaForm(request.POST, instance=faktura)
        if form.is_valid():
            form.save()
            return redirect('lista_faktur')  # Assuming 'lista_faktur' is the name for the invoice list view
    else:
        form = FakturaForm(instance=faktura)
    return render(request, 'faktury/edytuj_fakture.html', {'form': form})

"""
Invoice management views
"""
import datetime
import logging
from decimal import Decimal
from io import BytesIO
from zipfile import ZipFile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from weasyprint import HTML, CSS

from ..models import Faktura, Firma, Kontrahent, Produkt, PozycjaFaktury
from ..forms import (
    FakturaForm, PozycjaFakturyFormSet, ProduktForm, KwotaOplaconaForm,
    FakturaProformaForm, KorektaFakturyForm, ParagonForm, KpForm
)
from ..utils import generuj_numer
from ..constants import JEDNOSTKI

logger = logging.getLogger(__name__)


@login_required
def szczegoly_faktury(request, pk):
    """Invoice details view"""
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    return render(request, 'faktury/szczegoly_faktury.html', {'faktura': faktura})


@login_required
def dodaj_fakture_sprzedaz(request):
    """Add sales invoice view"""
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

    # Generate invoice number
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
                    # Create invoice
                    faktura = faktura_form.save(commit=False)
                    faktura.user = request.user
                    faktura.typ_faktury = 'sprzedaz'
                    faktura.sprzedawca = firma

                    # Validate NIP through contractor
                    if not faktura.nabywca or not faktura.nabywca.nip:
                        messages.error(request, "Wybierz kontrahenta z poprawnym NIP")
                        return redirect('dodaj_fakture')

                    # Number validation
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
                    
                    # Ensure payment method is always provided
                    sposob_platnosci = faktura_form.cleaned_data.get('sposob_platnosci', 'przelew')
                    faktura.sposob_platnosci = sposob_platnosci
                    
                    faktura.save()

                    # Save invoice items
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
            logger.error(f"Błędy formularza faktury: {faktura_form.errors}")
            logger.error(f"Błędy formsetu pozycji: {pozycje_formset.errors}")
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
def dodaj_fakture_koszt(request):
    """Add cost invoice view"""
    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        messages.error(request, "Uzupełnij dane swojej firmy przed wystawieniem faktury.")
        return redirect('dodaj_firme')

    kontrahent_id = request.GET.get('kontrahent')
    initial_data = {
        'miejsce_wystawienia': firma.miejscowosc,
        'typ_faktury': 'koszt',
    }

    if kontrahent_id:
        initial_data['nabywca'] = kontrahent_id

    # Generate cost invoice number
    today = datetime.date.today()
    ostatnia_faktura = Faktura.objects.filter(
        user=request.user,
        data_wystawienia__year=today.year,
        data_wystawienia__month=today.month,
        typ_faktury='koszt'
    ).order_by('-numer').first()

    if ostatnia_faktura:
        try:
            ostatni_numer = int(ostatnia_faktura.numer.split('/')[1])
            numer_faktury = f"FK/{ostatni_numer + 1:02d}/{today.month:02d}/{today.year}"
        except (ValueError, IndexError):
            liczba_faktur = Faktura.objects.filter(
                user=request.user,
                data_wystawienia__year=today.year,
                data_wystawienia__month=today.month,
                typ_faktury='koszt'
            ).count()
            numer_faktury = f"FK/{liczba_faktur + 1:02d}/{today.month:02d}/{today.year}"
    else:
        numer_faktury = f"FK/01/{today.month:02d}/{today.year}"

    initial_data['numer'] = numer_faktury

    if request.method == 'POST':
        faktura_form = FakturaForm(request.POST, initial=initial_data)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')

        if faktura_form.is_valid() and pozycje_formset.is_valid():
            try:
                with transaction.atomic():
                    faktura = faktura_form.save(commit=False)
                    faktura.user = request.user
                    faktura.typ_faktury = 'koszt'
                    faktura.nabywca = firma

                    auto_numer = faktura_form.cleaned_data.get('auto_numer', True)
                    wlasny_numer = faktura_form.cleaned_data.get('wlasny_numer', '')
                    
                    if auto_numer:
                        faktura.numer = initial_data['numer']
                    elif wlasny_numer:
                        faktura.numer = wlasny_numer
                    else:
                        messages.error(request, "Wprowadź własny numer faktury.")
                        return render(request, 'faktury/dodaj_fakture_koszt.html', {
                            'faktura_form': faktura_form,
                            'pozycje_formset': pozycje_formset,
                            'firma': firma,
                            'produkty': Produkt.objects.filter(user=request.user),
                            'produkt_form': ProduktForm()
                        })
                    
                    sposob_platnosci = faktura_form.cleaned_data.get('sposob_platnosci', 'przelew')
                    faktura.sposob_platnosci = sposob_platnosci
                    
                    faktura.save()

                    for pozycja_form in pozycje_formset:
                        if pozycja_form.cleaned_data and not pozycja_form.cleaned_data.get('DELETE'):
                            pozycja = pozycja_form.save(commit=False)
                            pozycja.faktura = faktura
                            pozycja.save()

                    messages.success(request, "Faktura kosztowa została dodana.")
                    return redirect('panel_uzytkownika')
            except Exception as e:
                logger.error(f"Błąd przy zapisie faktury kosztowej: {str(e)}", exc_info=True)
                messages.error(request, "Wystąpił błąd przy zapisie faktury.")
                return redirect('panel_uzytkownika')
        else:
            messages.error(request, "Popraw błędy w formularzu.")
            logger.error(f"FakturaForm Errors: {faktura_form.errors}")
            logger.error(f"PozycjeFormset Errors: {pozycje_formset.errors}")
            if pozycje_formset.non_form_errors():
                logger.error(f"PozycjeFormset Non-Form Errors: {pozycje_formset.non_form_errors()}")

    else:
        faktura_form = FakturaForm(initial=initial_data)
        pozycje_formset = PozycjaFakturyFormSet(prefix='pozycje')

    for form in pozycje_formset:
        form.fields['jednostka'].widget.choices = JEDNOSTKI

    produkty = Produkt.objects.filter(user=request.user)
    return render(request, 'faktury/dodaj_fakture_koszt.html', {
        'faktura_form': faktura_form,
        'pozycje_formset': pozycje_formset,
        'firma': firma,
        'produkty': produkty,
        'produkt_form': ProduktForm(),
        'numer_faktury': initial_data.get('numer', '')
    })


@login_required
def edytuj_fakture(request, pk):
    """Edit invoice view"""
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)

    if request.method == 'POST':
        faktura_form = FakturaForm(request.POST, instance=faktura)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, instance=faktura, prefix='pozycje')

        if faktura_form.is_valid() and pozycje_formset.is_valid():
            faktura_form.save()
            pozycje_formset.save()
            messages.success(request, 'Faktura została zaktualizowana')
            return redirect('szczegoly_faktury', pk=faktura.pk)
    else:
        faktura_form = FakturaForm(instance=faktura)
        pozycje_formset = PozycjaFakturyFormSet(instance=faktura, prefix='pozycje')

    return render(request, 'faktury/edytuj_fakture.html', {
        'faktura_form': faktura_form,
        'pozycje_formset': pozycje_formset,
        'faktura': faktura
    })


@login_required
def usun_fakture(request, pk):
    """Delete invoice view"""
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    if request.method == 'POST':
        faktura.delete()
        messages.success(request, 'Faktura została usunięta.')
        return redirect('panel_uzytkownika')
    return render(request, 'faktury/usun_fakture.html', {'faktura': faktura})


@login_required
def generuj_pdf(request, pk):
    """Generate PDF for invoice"""
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    
    # Render HTML template to string
    html_string = render_to_string('faktury/faktura_pdf.html', {'faktura': faktura})

    # Create HTML object with WeasyPrint
    html = HTML(string=html_string)
    
    # Generate PDF
    pdf = html.write_pdf()

    # Create HTTP response with PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="faktura_{faktura.numer}.pdf"'
    
    return response


@login_required
def generuj_wiele_pdf(request):
    """Generate multiple PDFs in ZIP file"""
    if request.method == 'POST':
        selected_invoice_ids = request.POST.getlist('selected_invoices')

        if not selected_invoice_ids:
            messages.error(request, 'Nie wybrano żadnej faktury.')
            return redirect('panel_uzytkownika')

        faktury = Faktura.objects.filter(id__in=selected_invoice_ids, user=request.user)

        # Create ZIP file in memory
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for faktura in faktury:
                # Generate PDF for each invoice
                html_string = render_to_string('faktury/faktura_pdf.html', {'faktura': faktura})
                html = HTML(string=html_string)
                pdf = html.write_pdf()
                
                # Add PDF to ZIP
                zip_file.writestr(f"faktura_{faktura.numer}.pdf", pdf)

        zip_buffer.seek(0)

        # Create HTTP response with ZIP
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="faktury.zip"'
        
        return response
    else:
        return redirect('panel_uzytkownika')


@login_required
def wyslij_fakture_mailem(request, pk):
    """Send invoice via email"""
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    kontrahent = faktura.nabywca

    if not kontrahent or not kontrahent.email:
        messages.error(request, 'Kontrahent nie ma podanego adresu email.')
        return redirect('szczegoly_faktury', pk=pk)

    try:
        # Generate PDF
        html_string = render_to_string('faktury/faktura_pdf.html', {'faktura': faktura})
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        # Prepare email
        subject = f'Faktura {faktura.numer}'
        message = f'W załączniku przesyłamy fakturę {faktura.numer}.'
        from_email = settings.EMAIL_HOST_USER
        to_email = [kontrahent.email]

        email = EmailMessage(subject, message, from_email, to_email)
        email.attach(f'faktura_{faktura.numer}.pdf', pdf, 'application/pdf')
        email.send()

        messages.success(request, f'Faktura została wysłana na adres {kontrahent.email}.')
    except Exception as e:
        logger.error(f"Błąd wysyłania emaila: {str(e)}")
        messages.error(request, 'Wystąpił błąd podczas wysyłania emaila.')

    return redirect('szczegoly_faktury', pk=pk)


@login_required
def update_payment(request, pk):
    """Update payment status"""
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    if request.method == 'POST':
        form = KwotaOplaconaForm(request.POST, instance=faktura)
        if form.is_valid():
            old_status = faktura.status
            form.save()
            new_status = form.instance.status
            if old_status != new_status:
                messages.success(request, f'Status płatności został zmieniony z "{old_status}" na "{new_status}".')
            else:
                messages.success(request, 'Dane płatności zostały zaktualizowane.')
            return redirect('szczegoly_faktury', pk=pk)
    else:
        form = KwotaOplaconaForm(instance=faktura)
    return render(request, 'faktury/update_payment.html', {'form': form, 'faktura': faktura})


@login_required
def wyslij_przypomnienie(request, pk):
    """Send payment reminder"""
    faktura = get_object_or_404(Faktura, pk=pk, user=request.user)
    kontrahent = faktura.nabywca

    if not kontrahent or not kontrahent.email:
        messages.error(request, 'Kontrahent nie ma podanego adresu email.')
        return redirect('szczegoly_faktury', pk=pk)

    try:
        subject = f'Przypomnienie o płatności - Faktura {faktura.numer}'
        message = f"""
        Szanowni Państwo,

        Przypominamy o zaległej płatności za fakturę {faktura.numer} 
        z dnia {faktura.data_wystawienia.strftime('%d.%m.%Y')}.

        Kwota do zapłaty: {faktura.suma_brutto} PLN
        Termin płatności: {faktura.termin_platnosci.strftime('%d.%m.%Y')}

        Prosimy o jak najszybszą regulację należności.

        Z poważaniem,
        {request.user.get_full_name() or request.user.username}
        """
        
        from_email = settings.EMAIL_HOST_USER
        to_email = [kontrahent.email]

        send_mail(subject, message, from_email, to_email)
        messages.success(request, f'Przypomnienie zostało wysłane na adres {kontrahent.email}.')
    except Exception as e:
        logger.error(f"Błąd wysyłania przypomnienia: {str(e)}")
        messages.error(request, 'Wystąpił błąd podczas wysyłania przypomnienia.')

    return redirect('szczegoly_faktury', pk=pk)


@login_required
def zarzadzaj_cyklem(request, faktura_id):
    """Manage invoice cycle"""
    faktura = get_object_or_404(Faktura, pk=faktura_id, user=request.user)

    if request.method == 'POST':
        # Handle cycle management logic here
        messages.success(request, 'Cykl faktury został zaktualizowany.')
        return redirect('szczegoly_faktury', pk=faktura_id)

    return render(request, 'faktury/zarzadzaj_cyklem.html', {'faktura': faktura})


@login_required
def stworz_proforma(request):
    """Create proforma invoice"""
    if request.method == 'POST':
        form = FakturaProformaForm(request.POST)
        if form.is_valid():
            faktura = form.save(commit=False)
            faktura.typ_dokumentu = 'FP'
            faktura.user = request.user
            faktura.numer = generuj_numer('FP')
            faktura.save()
            messages.success(request, 'Faktura proforma została utworzona.')
            return redirect('szczegoly_faktury', pk=faktura.pk)
    else:
        form = FakturaProformaForm()
    return render(request, 'faktury/proforma.html', {'form': form})


@login_required
def stworz_korekte(request, faktura_pk):
    """Create correction invoice"""
    podstawowa = get_object_or_404(Faktura, pk=faktura_pk, user=request.user)
    
    if request.method == 'POST':
        form = KorektaFakturyForm(request.POST)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')
        
        if form.is_valid() and pozycje_formset.is_valid():
            korekta = form.save(commit=False)
            korekta.typ_dokumentu = 'KOR'
            korekta.dokument_podstawowy = podstawowa
            korekta.user = request.user
            korekta.save()
            
            # Save invoice items
            for pozycja_form in pozycje_formset:
                if pozycja_form.cleaned_data and not pozycja_form.cleaned_data.get('DELETE'):
                    pozycja = pozycja_form.save(commit=False)
                    pozycja.faktura = korekta
                    pozycja.save()
            
            messages.success(request, "Korekta została zapisana.")
            return redirect('szczegoly_faktury', pk=korekta.pk)
    else:
        # Initialize form with data from base invoice
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
        
        # Initialize formset with items from base invoice
        pozycje_formset = PozycjaFakturyFormSet(prefix='pozycje')
    
    return render(request, 'faktury/korekta.html', {
        'form': form,
        'pozycje_formset': pozycje_formset,
        'podstawowa': podstawowa
    })


@login_required
def stworz_paragon(request):
    """Create receipt"""
    if request.method == 'POST':
        form = ParagonForm(request.POST)
        pozycje_formset = PozycjaFakturyFormSet(request.POST, prefix='pozycje')
        
        if form.is_valid() and pozycje_formset.is_valid():
            paragon = form.save(commit=False)
            paragon.typ_dokumentu = 'PAR'
            paragon.user = request.user
            paragon.numer = generuj_numer('PAR')
            paragon.save()
            
            # Save invoice items
            for pozycja_form in pozycje_formset:
                if pozycja_form.cleaned_data and not pozycja_form.cleaned_data.get('DELETE'):
                    pozycja = pozycja_form.save(commit=False)
                    pozycja.faktura = paragon
                    pozycja.save()
            
            messages.success(request, 'Paragon został utworzony.')
            return redirect('szczegoly_faktury', pk=paragon.pk)
    else:
        form = ParagonForm()
        pozycje_formset = PozycjaFakturyFormSet(prefix='pozycje')
    
    return render(request, 'faktury/paragon.html', {
        'form': form,
        'pozycje_formset': pozycje_formset
    })


@login_required
def generate_kp(request):
    """Generate KP document - legacy name for stworz_kp"""
    return stworz_kp(request)


@login_required
def stworz_kp(request):
    """Create KP document"""
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
            kp.user = request.user
            kp.numer = f"KP/{datetime.date.today().year}/{Faktura.objects.filter(typ_dokumentu='KP').count() + 1:04d}"
            kp.save()
            messages.success(request, 'Dokument KP został utworzony.')
            return redirect('szczegoly_faktury', pk=kp.pk)
    else:
        form = KpForm(initial={
            'kwota_oplacona': 0,
            'nabywca': firma_uzytkownika
        })
    
    return render(request, 'faktury/kp.html', {'form': form})


@login_required
def kp_list(request):
    """List KP documents"""
    kp_dokumenty = Faktura.objects.filter(
        user=request.user, 
        typ_dokumentu='KP'
    ).order_by('-data_wystawienia')
    
    return render(request, 'faktury/kp_list.html', {'kp_dokumenty': kp_dokumenty})


@login_required
def szczegoly_kp(request, pk):
    """KP document details"""
    kp = get_object_or_404(Faktura, pk=pk, user=request.user, typ_dokumentu='KP')
    return render(request, 'faktury/szczegoly_kp.html', {'kp': kp})


@login_required
def konwertuj_proforme_na_fakture(request, pk):
    """Convert proforma to invoice"""
    proforma = get_object_or_404(Faktura, pk=pk, typ_dokumentu='FP', user=request.user)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create new invoice based on proforma
                faktura = Faktura.objects.create(
                    user=request.user,
                    typ_dokumentu='FV',
                    dokument_podstawowy=proforma,
                    nabywca=proforma.nabywca,
                    sprzedawca=proforma.sprzedawca,
                    data_wystawienia=timezone.now().date(),
                    data_sprzedazy=proforma.data_sprzedazy,
                    termin_platnosci=proforma.termin_platnosci,
                    miejsce_wystawienia=proforma.miejsce_wystawienia,
                    sposob_platnosci=proforma.sposob_platnosci,
                    typ_faktury=proforma.typ_faktury,
                    waluta=proforma.waluta,
                    numer=generuj_numer('FV'),
                    status='wystawiona'
                )

                # Copy invoice items
                for pozycja in proforma.pozycjafaktury_set.all():
                    PozycjaFaktury.objects.create(
                        faktura=faktura,
                        nazwa=pozycja.nazwa,
                        ilosc=pozycja.ilosc,
                        jednostka=pozycja.jednostka,
                        cena_netto=pozycja.cena_netto,
                        vat=pozycja.vat,
                        rabat=pozycja.rabat,
                        rabat_typ=pozycja.rabat_typ
                    )

                messages.success(request, f'Proforma została przekonwertowana na fakturę {faktura.numer}.')
                return redirect('szczegoly_faktury', pk=faktura.pk)
        except Exception as e:
            logger.error(f"Błąd konwersji proformy: {str(e)}")
            messages.error(request, 'Wystąpił błąd podczas konwersji proformy.')
            return redirect('szczegoly_faktury', pk=pk)
    
    return render(request, 'faktury/konwertuj_proforme.html', {'proforma': proforma})
