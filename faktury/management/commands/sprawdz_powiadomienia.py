"""
Management command to check and send notifications
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from faktury.services.notification_service import NotificationService


class Command(BaseCommand):
    help = 'Sprawdza i wysyła powiadomienia o ważnych wydarzeniach'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['all', 'overdue', 'upcoming', 'tasks', 'cycles', 'summaries'],
            default='all',
            help='Typ powiadomień do sprawdzenia',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Pokazuje co zostałoby zrobione bez wykonywania akcji',
        )
        parser.add_argument(
            '--clean-old',
            action='store_true',
            help='Czyści stare powiadomienia',
        )
        parser.add_argument(
            '--clean-days',
            type=int,
            default=30,
            help='Liczba dni dla czyszczenia starych powiadomień (domyślnie 30)',
        )

    def handle(self, *args, **options):
        notification_type = options['type']
        dry_run = options['dry_run']
        clean_old = options['clean_old']
        clean_days = options['clean_days']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('TRYB TESTOWY - żadne powiadomienia nie zostaną utworzone')
            )
            return
        
        self.stdout.write(f'Rozpoczynam sprawdzanie powiadomień typu: {notification_type}')
        
        try:
            total_created = 0
            
            if notification_type == 'all':
                total_created = NotificationService.sprawdz_wszystkie_powiadomienia()
            
            elif notification_type == 'overdue':
                total_created = NotificationService.sprawdz_przeterminowane_faktury()
                self.stdout.write('Sprawdzono przeterminowane faktury')
            
            elif notification_type == 'upcoming':
                total_created = NotificationService.sprawdz_nadchodzace_terminy()
                self.stdout.write('Sprawdzono nadchodzące terminy')
            
            elif notification_type == 'tasks':
                total_created = NotificationService.sprawdz_niewykonane_zadania()
                self.stdout.write('Sprawdzono niewykonane zadania')
            
            elif notification_type == 'cycles':
                total_created = NotificationService.sprawdz_cykle_do_generacji()
                self.stdout.write('Sprawdzono cykle do generacji')
            
            elif notification_type == 'summaries':
                total_created = NotificationService.wyslij_podsumowania_dla_wszystkich()
                self.stdout.write('Wysłano podsumowania dzienne')
            
            if total_created > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Utworzono {total_created} powiadomień')
                )
            else:
                self.stdout.write('Brak nowych powiadomień do utworzenia')
            
            # Clean old notifications if requested
            if clean_old:
                deleted_count = NotificationService.wyczysc_stare_powiadomienia(clean_days)
                self.stdout.write(
                    self.style.SUCCESS(f'Usunięto {deleted_count} starych powiadomień')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Błąd podczas sprawdzania powiadomień: {str(e)}')
            )
            raise
