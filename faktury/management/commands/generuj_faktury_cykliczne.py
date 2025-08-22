from django.core.management.base import BaseCommand
from django.utils import timezone
from faktury.services import sprawdz_faktury_cykliczne, powiadom_o_nadchodzacych_cyklach


class Command(BaseCommand):
    help = 'Generuje cykliczne faktury według harmonogramu i wysyła powiadomienia'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Pokazuje co zostałoby zrobione bez wykonywania akcji',
        )
        parser.add_argument(
            '--notifications-only',
            action='store_true',
            help='Tylko wysyła powiadomienia bez generowania faktur',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        notifications_only = options['notifications_only']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('TRYB TESTOWY - żadne zmiany nie zostaną zapisane')
            )
            return
        
        self.stdout.write('Rozpoczynam sprawdzanie faktur cyklicznych...')
        
        try:
            if not notifications_only:
                # Generate recurring invoices
                wygenerowane, bledy = sprawdz_faktury_cykliczne()
                
                if wygenerowane > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'Wygenerowano {wygenerowane} faktur cyklicznych')
                    )
                
                if bledy > 0:
                    self.stdout.write(
                        self.style.ERROR(f'Wystąpiło {bledy} błędów podczas generowania')
                    )
                
                if wygenerowane == 0 and bledy == 0:
                    self.stdout.write('Brak faktur do wygenerowania')
            
            # Send notifications about upcoming invoices
            powiadomienia = powiadom_o_nadchodzacych_cyklach()
            
            if powiadomienia > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Wysłano {powiadomienia} powiadomień o nadchodzących fakturach')
                )
            else:
                self.stdout.write('Brak powiadomień do wysłania')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Błąd podczas przetwarzania: {str(e)}')
            )
            raise {
            'D': timedelta(days=1),
            'W': timedelta(weeks=1),
            'M': timedelta(days=30),
            'K': timedelta(days=90),
            'R': timedelta(days=365),
        }
        return delty.get(cykl, timedelta(days=30))