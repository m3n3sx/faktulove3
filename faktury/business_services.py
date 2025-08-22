from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import logging
from .models import Faktura, PozycjaFaktury, Firma, Kontrahent, Partnerstwo, FakturaCykliczna
from .notifications.models import Notification
from django.db.models import Q
from django.utils import timezone
# from .utils import generuj_numer  # Commented out - will be implemented later

logger = logging.getLogger(__name__)

def auto_ksieguj_fakture_service(faktura):
    if faktura.typ_faktury == 'sprzedaz':
        logger.info(f"Auto-księgowanie rozpoczęte dla faktury sprzedaży: {faktura.numer}")
        try:
            with transaction.atomic():
                logger.info(f"Wyszukiwanie partnerstwa dla firmy sprzedawcy: {faktura.sprzedawca.nazwa}")
                partnerstwo = Partnerstwo.objects.filter(
                    (Q(firma1=faktura.sprzedawca) | Q(firma2=faktura.sprzedawca)),
                    aktywne=True,
                    auto_ksiegowanie=True
                ).first()

                if not partnerstwo:
                    logger.warning(f"Brak aktywnego partnerstwa dla faktury {faktura.numer}. Auto-księgowanie przerwane.")
                    return

                firma_partnera = partnerstwo.firma2 if partnerstwo.firma1 == faktura.sprzedawca else partnerstwo.firma1
                logger.info(f"Znaleziono partnerstwo. Firma partnera: {firma_partnera.nazwa}")

                logger.info(f"Tworzenie/aktualizacja kontrahenta dla firmy partnera w systemie firmy sprzedawcy.")
                kontrahent_partnera, kontrahent_created = Kontrahent.objects.update_or_create(
                    user=firma_partnera.user,
                    nip=firma_partnera.nip,
                    defaults={
                        'nazwa': firma_partnera.nazwa,
                        'ulica': firma_partnera.ulica,
                        'numer_domu': firma_partnera.numer_domu,
                        'kod_pocztowy': firma_partnera.kod_pocztowy,
                        'miejscowosc': firma_partnera.miejscowosc,
                        'kraj': firma_partnera.kraj,
                        'czy_firma': True
                    }
                )
                if kontrahent_created:
                    logger.info(f"Utworzono kontrahenta {kontrahent_partnera.nazwa} w systemie firmy {firma_partnera.nazwa}")
                else:
                    logger.info(f"Kontrahent {kontrahent_partnera.nazwa} już istnieje w systemie firmy {firma_partnera.nazwa}.")


                # Generate unique number for cost invoice
                cost_number = f"FK-AUTO/{timezone.now().year}/{faktura.numer}"
                
                logger.info(f"Tworzenie faktury kosztowej w systemie firmy partnera.")
                kopia_faktury = Faktura.objects.create(
                    user=firma_partnera.user,
                    typ_dokumentu='FV',  # Always FV for auto-accounting
                    numer=cost_number,   # Unique number for cost invoice
                    data_wystawienia=faktura.data_wystawienia,
                    data_sprzedazy=faktura.data_sprzedazy,
                    miejsce_wystawienia=firma_partnera.miejscowosc or "Warszawa",
                    sprzedawca=faktura.sprzedawca,  # Original selling company
                    nabywca=kontrahent_partnera,  # Partner company as kontrahent
                    typ_faktury='koszt',  # Cost invoice
                    sposob_platnosci=faktura.sposob_platnosci,
                    termin_platnosci=faktura.termin_platnosci,
                    status='wystawiona',
                    waluta=faktura.waluta,
                    uwagi=f"Auto-księgowanie faktury {faktura.numer} od {faktura.sprzedawca.nazwa}",
                    auto_ksiegowana=True,  # Mark as auto-accounted
                    faktura_zrodlowa=faktura  # Link to source invoice
                )
                logger.info(f"Utworzono fakturę kosztową {kopia_faktury.numer} w panelu {firma_partnera.nazwa}")

                logger.info(f"Kopiowanie pozycji faktury.")
                for pozycja in faktura.pozycjafaktury_set.all():
                    PozycjaFaktury.objects.create(
                        faktura=kopia_faktury,
                        nazwa=pozycja.nazwa,
                        rabat=pozycja.rabat,
                        rabat_typ=pozycja.rabat_typ,
                        ilosc=pozycja.ilosc,
                        jednostka=pozycja.jednostka,
                        cena_netto=pozycja.cena_netto,
                        vat=pozycja.vat
                    )
                logger.info(f"Pozycje faktury skopiowane.")
                
                # Create notification for partner company
                Notification.objects.create(
                    user=firma_partnera.user,
                    title="Nowa faktura kosztowa z auto-księgowania",
                    content=f"Utworzono automatycznie fakturę kosztową {cost_number} na podstawie faktury {faktura.numer} od {faktura.sprzedawca.nazwa}",
                    type="INFO"
                )
                
                # Mark original invoice as auto-accounted
                faktura.auto_ksiegowana = True
                faktura.save(update_fields=['auto_ksiegowana'])
                
                logger.info(f"Auto-księgowanie zakończone sukcesem dla faktury {faktura.numer}.")
                return kopia_faktury

        except Exception as e:
            logger.error(f"Błąd auto-księgowania faktury {faktura.numer}: {str(e)}", exc_info=True)
            raise
    else:
        logger.info(f"Faktura {faktura.numer} nie jest fakturą sprzedaży - pomijanie auto-księgowania")
        return None


def sprawdz_partnerstwa_auto_ksiegowanie(user):
    """Check and process pending auto-accounting for partnerships"""
    try:
        firma = Firma.objects.get(user=user)
        
        # Find all active partnerships with auto-accounting enabled
        partnerstwa = Partnerstwo.objects.filter(
            Q(firma1=firma) | Q(firma2=firma),
            aktywne=True,
            auto_ksiegowanie=True
        )
        
        processed_count = 0
        
        for partnerstwo in partnerstwa:
            # Find unprocessed sales invoices that should be auto-accounted
            faktury_do_ksiegowania = Faktura.objects.filter(
                sprzedawca=firma,
                typ_faktury='sprzedaz',
                auto_ksiegowana=False
            )
            
            for faktura in faktury_do_ksiegowania:
                try:
                    auto_ksieguj_fakture_service(faktura)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Błąd auto-księgowania faktury {faktura.numer}: {e}")
        
        logger.info(f"Przetworzono {processed_count} faktur w auto-księgowaniu dla użytkownika {user.username}")
        return processed_count
        
    except Firma.DoesNotExist:
        logger.warning(f"Brak firmy dla użytkownika {user.username}")
        return 0


def generuj_fakture_cykliczna(cykl):
    """Generate invoice from recurring cycle"""
    if not cykl.czy_mozna_generowac:
        logger.warning(f"Nie można wygenerować faktury dla cyklu {cykl.id} - warunki nie spełnione")
        return None
    
    try:
        with transaction.atomic():
            oryginalna = cykl.oryginalna_faktura
            
            # Generate new invoice number
            prefix = "FV-CYK" if oryginalna.typ_faktury == 'sprzedaz' else "FK-CYK"
            nowy_numer = f"{prefix}/{cykl.liczba_cykli + 1:03d}/{timezone.now().year}/{oryginalna.numer}"
            
            # Calculate dates
            today = timezone.now().date()
            data_sprzedazy = cykl.nastepna_generacja
            
            # Calculate payment deadline based on original invoice
            if oryginalna.termin_platnosci and oryginalna.data_sprzedazy:
                days_diff = (oryginalna.termin_platnosci - oryginalna.data_sprzedazy).days
                termin_platnosci = data_sprzedazy + timezone.timedelta(days=days_diff)
            else:
                termin_platnosci = data_sprzedazy + timezone.timedelta(days=14)  # Default 14 days
            
            # Create new invoice
            nowa_faktura = Faktura.objects.create(
                user=oryginalna.user,
                typ_dokumentu=oryginalna.typ_dokumentu,
                numer=nowy_numer,
                data_wystawienia=today,
                data_sprzedazy=data_sprzedazy,
                termin_platnosci=termin_platnosci,
                miejsce_wystawienia=oryginalna.miejsce_wystawienia,
                sprzedawca=oryginalna.sprzedawca,
                nabywca=oryginalna.nabywca,
                typ_faktury=oryginalna.typ_faktury,
                sposob_platnosci=oryginalna.sposob_platnosci,
                status='wystawiona',
                waluta=oryginalna.waluta,
                uwagi=f"Faktura cykliczna #{cykl.liczba_cykli + 1} - bazowa: {oryginalna.numer}",
                faktura_cykliczna=cykl
            )
            
            # Copy invoice items
            for pozycja in oryginalna.pozycjafaktury_set.all():
                PozycjaFaktury.objects.create(
                    faktura=nowa_faktura,
                    nazwa=pozycja.nazwa,
                    ilosc=pozycja.ilosc,
                    jednostka=pozycja.jednostka,
                    cena_netto=pozycja.cena_netto,
                    vat=pozycja.vat,
                    rabat=pozycja.rabat,
                    rabat_typ=pozycja.rabat_typ
                )
            
            # Update cycle
            cykl.nastepna_generacja = cykl.oblicz_nastepna_date()
            cykl.liczba_cykli += 1
            cykl.ostatnia_generacja = timezone.now()
            
            # Check if cycle should end
            if cykl.data_koncowa and cykl.nastepna_generacja > cykl.data_koncowa:
                cykl.aktywna = False
                
            if cykl.maksymalna_liczba_cykli and cykl.liczba_cykli >= cykl.maksymalna_liczba_cykli:
                cykl.aktywna = False
            
            cykl.save()
            
            # Create notification
            if cykl.powiadom_o_generacji:
                Notification.objects.create(
                    user=oryginalna.user,
                    title="Wygenerowano fakturę cykliczną",
                    content=f"Automatycznie wygenerowano fakturę {nowa_faktura.numer} z cyklu {cykl}",
                    type="SUCCESS"
                )
            
            # Trigger auto-accounting if applicable
            if nowa_faktura.typ_faktury == 'sprzedaz':
                try:
                    auto_ksieguj_fakture_service(nowa_faktura)
                except Exception as e:
                    logger.error(f"Błąd auto-księgowania faktury cyklicznej {nowa_faktura.numer}: {e}")
            
            logger.info(f"Wygenerowano fakturę cykliczną {nowa_faktura.numer} z cyklu {cykl.id}")
            return nowa_faktura
            
    except Exception as e:
        logger.error(f"Błąd generowania faktury cyklicznej dla cyklu {cykl.id}: {str(e)}", exc_info=True)
        raise


def sprawdz_faktury_cykliczne():
    """Check and generate due recurring invoices"""
    today = timezone.now().date()
    
    cykle_do_generacji = FakturaCykliczna.objects.filter(
        aktywna=True,
        nastepna_generacja__lte=today
    ).select_related('oryginalna_faktura')
    
    wygenerowane = 0
    bledy = 0
    
    for cykl in cykle_do_generacji:
        try:
            faktura = generuj_fakture_cykliczna(cykl)
            if faktura:
                wygenerowane += 1
                logger.info(f"Wygenerowano fakturę cykliczną: {faktura.numer}")
        except Exception as e:
            bledy += 1
            logger.error(f"Błąd generowania faktury dla cyklu {cykl.id}: {e}")
    
    logger.info(f"Sprawdzenie cykli zakończone: {wygenerowane} wygenerowanych, {bledy} błędów")
    return wygenerowane, bledy


def powiadom_o_nadchodzacych_cyklach():
    """Notify users about upcoming recurring invoices"""
    today = timezone.now().date()
    
    # Find cycles that are due for notification
    cykle_powiadomien = FakturaCykliczna.objects.filter(
        aktywna=True,
        powiadom_o_generacji=True,
        nastepna_generacja__gt=today
    ).select_related('oryginalna_faktura')
    
    powiadomienia_wyslane = 0
    
    for cykl in cykle_powiadomien:
        dni_do_generacji = cykl.dni_do_nastepnej_generacji
        
        if dni_do_generacji <= cykl.dni_przed_generacja:
            # Check if notification was already sent for this cycle
            ostatnie_powiadomienie = Notification.objects.filter(
                user=cykl.oryginalna_faktura.user,
                title__contains="Nadchodząca faktura cykliczna",
                content__contains=cykl.oryginalna_faktura.numer,
                timestamp__date=today
            ).exists()
            
            if not ostatnie_powiadomienie:
                Notification.objects.create(
                    user=cykl.oryginalna_faktura.user,
                    title="Nadchodząca faktura cykliczna",
                    content=f"Za {dni_do_generacji} dni zostanie wygenerowana faktura cykliczna na podstawie {cykl.oryginalna_faktura.numer}",
                    type="INFO"
                )
                powiadomienia_wyslane += 1
    
    logger.info(f"Wysłano {powiadomienia_wyslane} powiadomień o nadchodzących cyklach")
    return powiadomienia_wyslane