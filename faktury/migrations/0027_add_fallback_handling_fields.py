# Generated migration for fallback handling fields

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('faktury', '0026_alter_documentupload_processing_status'),
    ]

    operations = [
        # Add fallback handling fields to DocumentUpload
        migrations.AddField(
            model_name='documentupload',
            name='retry_count',
            field=models.IntegerField(default=0, verbose_name='Liczba ponownych prób'),
        ),
        migrations.AddField(
            model_name='documentupload',
            name='next_retry_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Następna próba o'),
        ),
        migrations.AddField(
            model_name='documentupload',
            name='preferred_engine',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Preferowany silnik OCR'),
        ),
        migrations.AddField(
            model_name='documentupload',
            name='manual_review_reason',
            field=models.TextField(blank=True, null=True, verbose_name='Powód przeglądu manualnego'),
        ),
        migrations.AddField(
            model_name='documentupload',
            name='manual_review_queued_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Dodano do przeglądu o'),
        ),
        migrations.AddField(
            model_name='documentupload',
            name='manual_review_completed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Przegląd zakończono o'),
        ),
        migrations.AddField(
            model_name='documentupload',
            name='manual_review_completed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='completed_reviews', to=settings.AUTH_USER_MODEL, verbose_name='Przegląd wykonał'),
        ),
        migrations.AddField(
            model_name='documentupload',
            name='processing_error',
            field=models.TextField(blank=True, null=True, verbose_name='Błąd przetwarzania'),
        ),
        
        # Add manual verification fields to OCRResult
        migrations.AddField(
            model_name='ocrresult',
            name='manual_verification_required',
            field=models.BooleanField(default=False, verbose_name='Wymaga weryfikacji manualnej'),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='manually_verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_ocr_results', to=settings.AUTH_USER_MODEL, verbose_name='Zweryfikowane przez'),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='manually_verified_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data weryfikacji manualnej'),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='processing_notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notatki przetwarzania'),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Data aktualizacji'),
        ),
        
        # Update status choices for DocumentUpload
        migrations.AlterField(
            model_name='documentupload',
            name='processing_status',
            field=models.CharField(
                choices=[
                    ('uploaded', 'Przesłany'),
                    ('queued', 'W kolejce'),
                    ('processing', 'Przetwarzany'),
                    ('ocr_completed', 'OCR zakończone'),
                    ('integration_processing', 'Tworzenie faktury'),
                    ('completed', 'Zakończony'),
                    ('failed', 'Błąd'),
                    ('manual_review', 'Wymaga przeglądu'),
                    ('manual_review_required', 'Wymaga przeglądu manualnego'),
                    ('retry_scheduled', 'Zaplanowano ponowną próbę'),
                    ('retry_with_different_engine', 'Ponowna próba z innym silnikiem'),
                    ('retry_with_preprocessing', 'Ponowna próba z przetwarzaniem'),
                    ('partial_success', 'Częściowy sukces'),
                    ('processing_aborted', 'Przetwarzanie przerwane'),
                    ('rejected', 'Odrzucony'),
                    ('cancelled', 'Anulowany'),
                ],
                default='uploaded',
                max_length=30,
                verbose_name='Status przetwarzania'
            ),
        ),
        
        # Update status choices for OCRResult
        migrations.AlterField(
            model_name='ocrresult',
            name='processing_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Oczekuje'),
                    ('processing', 'Przetwarzanie'),
                    ('completed', 'Zakończone'),
                    ('failed', 'Błąd'),
                    ('manual_review', 'Wymaga przeglądu'),
                    ('manual_review_required', 'Wymaga przeglądu manualnego'),
                    ('partial_success', 'Częściowy sukces'),
                    ('manually_verified', 'Zweryfikowane manualnie'),
                    ('rejected', 'Odrzucone'),
                ],
                default='pending',
                max_length=25,
                verbose_name='Status przetwarzania'
            ),
        ),
        
        # Add indexes for new fields
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS faktury_documentupload_retry_count_idx ON faktury_documentupload (retry_count);",
            reverse_sql="DROP INDEX IF EXISTS faktury_documentupload_retry_count_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS faktury_documentupload_next_retry_at_idx ON faktury_documentupload (next_retry_at);",
            reverse_sql="DROP INDEX IF EXISTS faktury_documentupload_next_retry_at_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS faktury_documentupload_manual_review_queued_at_idx ON faktury_documentupload (manual_review_queued_at);",
            reverse_sql="DROP INDEX IF EXISTS faktury_documentupload_manual_review_queued_at_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS faktury_ocrresult_manual_verification_required_idx ON faktury_ocrresult (manual_verification_required);",
            reverse_sql="DROP INDEX IF EXISTS faktury_ocrresult_manual_verification_required_idx;"
        ),
    ]