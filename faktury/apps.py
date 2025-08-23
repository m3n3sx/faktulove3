from django.apps import AppConfig

class FakturyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faktury'

    def ready(self):
        import faktury.signals  # Rejestracja sygnałów
        from .signals import connect_ocr_signals
        connect_ocr_signals()  # Ensure OCR signals are connected

    