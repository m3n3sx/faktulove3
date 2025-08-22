"""
Advanced notification service for FaktuLove
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User

from ..models import Faktura, FakturaCykliczna, ZadanieUzytkownika, Partnerstwo
from ..notifications.models import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications and alerts"""
    
    @staticmethod
    def create_notification(user, title, content, notification_type='INFO', link=None):
        """Create a new notification"""
        return Notification.objects.create(
            user=user,
            title=title,
            content=content,
            type=notification_type,
            link=link or '#'
        )
    
    @staticmethod
    def sprawdz_przeterminowane_faktury():
        """Check for overdue invoices and create notifications"""
        today = timezone.now().date()
        
        # Find overdue invoices without recent notifications
        przeterminowane = Faktura.objects.filter(
            termin_platnosci__lt=today,
            status__in=['wystawiona', 'wyslana']
        ).select_related('user', 'nabywca')
        
        powiadomienia_utworzone = 0
        
        for faktura in przeterminowane:
            # Check if notification was already sent today
            existing = Notification.objects.filter(
                user=faktura.user,
                title__contains="Przeterminowana faktura",
                content__contains=faktura.numer,
                timestamp__date=today
            ).exists()
            
            if not existing:
                dni_po_terminie = (today - faktura.termin_platnosci).days
                
                NotificationService.create_notification(
                    user=faktura.user,
                    title="Przeterminowana faktura",
                    content=f"Faktura {faktura.numer} jest przeterminowana o {dni_po_terminie} dni. Nabywca: {faktura.nabywca.nazwa if faktura.nabywca else 'Brak'}",
                    notification_type="WARNING",
                    link=f"/faktury/szczegoly/{faktura.id}/"
                )
                powiadomienia_utworzone += 1
        
        logger.info(f"Utworzono {powiadomienia_utworzone} powiadomień o przeterminowanych fakturach")
        return powiadomienia_utworzone
    
    @staticmethod
    def sprawdz_nadchodzace_terminy():
        """Check for upcoming payment deadlines"""
        today = timezone.now().date()
        
        # Check for payments due in 3, 7, and 14 days
        warning_days = [3, 7, 14]
        powiadomienia_utworzone = 0
        
        for days in warning_days:
            target_date = today + timedelta(days=days)
            
            faktury = Faktura.objects.filter(
                termin_platnosci=target_date,
                status__in=['wystawiona', 'wyslana']
            ).select_related('user', 'nabywca')
            
            for faktura in faktury:
                # Check if notification was already sent
                existing = Notification.objects.filter(
                    user=faktura.user,
                    title__contains="Nadchodzący termin płatności",
                    content__contains=faktura.numer,
                    timestamp__date=today
                ).exists()
                
                if not existing:
                    NotificationService.create_notification(
                        user=faktura.user,
                        title="Nadchodzący termin płatności",
                        content=f"Za {days} dni upływa termin płatności faktury {faktura.numer}. Nabywca: {faktura.nabywca.nazwa if faktura.nabywca else 'Brak'}",
                        notification_type="INFO",
                        link=f"/faktury/szczegoly/{faktura.id}/"
                    )
                    powiadomienia_utworzone += 1
        
        logger.info(f"Utworzono {powiadomienia_utworzone} powiadomień o nadchodzących terminach")
        return powiadomienia_utworzone
    
    @staticmethod
    def sprawdz_niewykonane_zadania():
        """Check for overdue tasks"""
        today = timezone.now().date()
        
        przeterminowane_zadania = ZadanieUzytkownika.objects.filter(
            termin_wykonania__lt=today,
            wykonane=False
        ).select_related('user')
        
        powiadomienia_utworzone = 0
        
        for zadanie in przeterminowane_zadania:
            # Check if notification was already sent today
            existing = Notification.objects.filter(
                user=zadanie.user,
                title__contains="Przeterminowane zadanie",
                content__contains=zadanie.tytul,
                timestamp__date=today
            ).exists()
            
            if not existing:
                dni_po_terminie = (today - zadanie.termin_wykonania).days
                
                NotificationService.create_notification(
                    user=zadanie.user,
                    title="Przeterminowane zadanie",
                    content=f"Zadanie '{zadanie.tytul}' jest przeterminowane o {dni_po_terminie} dni",
                    notification_type="WARNING"
                )
                powiadomienia_utworzone += 1
        
        logger.info(f"Utworzono {powiadomienia_utworzone} powiadomień o przeterminowanych zadaniach")
        return powiadomienia_utworzone
    
    @staticmethod
    def sprawdz_cykle_do_generacji():
        """Check for recurring invoices ready for generation"""
        today = timezone.now().date()
        
        cykle = FakturaCykliczna.objects.filter(
            aktywna=True,
            nastepna_generacja__lte=today
        ).select_related('oryginalna_faktura__user')
        
        powiadomienia_utworzone = 0
        
        for cykl in cykle:
            # Check if notification was already sent
            existing = Notification.objects.filter(
                user=cykl.oryginalna_faktura.user,
                title__contains="Faktura do wygenerowania",
                content__contains=cykl.oryginalna_faktura.numer,
                timestamp__date=today
            ).exists()
            
            if not existing:
                NotificationService.create_notification(
                    user=cykl.oryginalna_faktura.user,
                    title="Faktura do wygenerowania",
                    content=f"Faktura cykliczna {cykl.oryginalna_faktura.numer} jest gotowa do wygenerowania",
                    notification_type="INFO",
                    link=f"/faktury/cykle/szczegoly/{cykl.id}/"
                )
                powiadomienia_utworzone += 1
        
        logger.info(f"Utworzono {powiadomienia_utworzone} powiadomień o cyklach do generacji")
        return powiadomienia_utworzone
    
    @staticmethod
    def sprawdz_nowe_partnerstwa():
        """Check for new partnership opportunities"""
        # This could be extended to analyze customer patterns
        # and suggest partnerships
        pass
    
    @staticmethod
    def wyslij_podsumowanie_dzienne(user):
        """Send daily summary to user"""
        today = timezone.now().date()
        
        # Calculate daily stats
        faktury_dzisiaj = Faktura.objects.filter(
            user=user,
            data_wystawienia=today
        ).count()
        
        terminy_dzisiaj = Faktura.objects.filter(
            user=user,
            termin_platnosci=today,
            status__in=['wystawiona', 'wyslana']
        ).count()
        
        zadania_dzisiaj = ZadanieUzytkownika.objects.filter(
            user=user,
            termin_wykonania=today,
            wykonane=False
        ).count()
        
        przeterminowane = Faktura.objects.filter(
            user=user,
            termin_platnosci__lt=today,
            status__in=['wystawiona', 'wyslana']
        ).count()
        
        # Create summary content
        content_parts = []
        
        if faktury_dzisiaj > 0:
            content_parts.append(f"• {faktury_dzisiaj} nowych faktur")
        
        if terminy_dzisiaj > 0:
            content_parts.append(f"• {terminy_dzisiaj} terminów płatności dzisiaj")
        
        if zadania_dzisiaj > 0:
            content_parts.append(f"• {zadania_dzisiaj} zadań do wykonania")
        
        if przeterminowane > 0:
            content_parts.append(f"• {przeterminowane} przeterminowanych faktur")
        
        if not content_parts:
            content = "Brak ważnych wydarzeń na dzisiaj."
        else:
            content = "Podsumowanie dnia:\n" + "\n".join(content_parts)
        
        # Check if summary was already sent today
        existing = Notification.objects.filter(
            user=user,
            title="Podsumowanie dnia",
            timestamp__date=today
        ).exists()
        
        if not existing:
            NotificationService.create_notification(
                user=user,
                title="Podsumowanie dnia",
                content=content,
                notification_type="INFO"
            )
            return True
        
        return False
    
    @staticmethod
    def wyczysc_stare_powiadomienia(dni=30):
        """Clean up old notifications"""
        cutoff_date = timezone.now() - timedelta(days=dni)
        
        deleted_count = Notification.objects.filter(
            timestamp__lt=cutoff_date,
            is_read=True
        ).delete()[0]
        
        logger.info(f"Usunięto {deleted_count} starych powiadomień")
        return deleted_count
    
    @staticmethod
    def sprawdz_wszystkie_powiadomienia():
        """Run all notification checks"""
        logger.info("Rozpoczynam sprawdzanie wszystkich powiadomień")
        
        total_created = 0
        
        try:
            total_created += NotificationService.sprawdz_przeterminowane_faktury()
            total_created += NotificationService.sprawdz_nadchodzace_terminy()
            total_created += NotificationService.sprawdz_niewykonane_zadania()
            total_created += NotificationService.sprawdz_cykle_do_generacji()
            
            logger.info(f"Sprawdzanie powiadomień zakończone. Utworzono łącznie {total_created} powiadomień")
            
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania powiadomień: {str(e)}", exc_info=True)
            raise
        
        return total_created
    
    @staticmethod
    def wyslij_podsumowania_dla_wszystkich():
        """Send daily summaries to all active users"""
        today = timezone.now().date()
        
        # Get users who have invoices or tasks
        active_users = User.objects.filter(
            Q(faktura__isnull=False) | Q(zadanieuzytkownika__isnull=False)
        ).distinct()
        
        podsumowania_wyslane = 0
        
        for user in active_users:
            try:
                if NotificationService.wyslij_podsumowanie_dzienne(user):
                    podsumowania_wyslane += 1
            except Exception as e:
                logger.error(f"Błąd wysyłania podsumowania dla użytkownika {user.username}: {e}")
        
        logger.info(f"Wysłano {podsumowania_wyslane} dziennych podsumowań")
        return podsumowania_wyslane
