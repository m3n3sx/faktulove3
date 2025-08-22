from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faktury.notifications'

    def ready(self):
        # Rejestracja sygnałów powiązanych z aplikacją notifications (jeśli istnieją)
        import faktury.notifications.signals  # Upewnij się, że plik signals.py istnieje w katalogu notifications

    
