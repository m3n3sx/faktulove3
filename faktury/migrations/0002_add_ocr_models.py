# Generated manually for OCR functionality

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('faktury', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_filename', models.CharField(max_length=255, verbose_name='Nazwa pliku')),
                ('file_path', models.CharField(max_length=500, verbose_name='Ścieżka pliku')),
                ('file_size', models.BigIntegerField(verbose_name='Rozmiar pliku (bytes)')),
                ('content_type', models.CharField(max_length=100, verbose_name='Typ MIME')),
                ('upload_timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Data przesłania')),
                ('processing_status', models.CharField(choices=[('uploaded', 'Przesłany'), ('processing', 'Przetwarzany'), ('completed', 'Zakończony'), ('failed', 'Błąd'), ('cancelled', 'Anulowany')], default='uploaded', max_length=20, verbose_name='Status przetwarzania')),
                ('processing_started_at', models.DateTimeField(blank=True, null=True, verbose_name='Rozpoczęcie przetwarzania')),
                ('processing_completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Zakończenie przetwarzania')),
                ('error_message', models.TextField(blank=True, null=True, verbose_name='Komunikat błędu')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Użytkownik')),
            ],
            options={
                'verbose_name': 'Przesłany dokument',
                'verbose_name_plural': 'Przesłane dokumenty',
                'ordering': ['-upload_timestamp'],
            },
        ),
        migrations.CreateModel(
            name='OCRResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_text', models.TextField(verbose_name='Surowy tekst OCR')),
                ('extracted_data', models.JSONField(verbose_name='Wyodrębnione dane')),
                ('confidence_score', models.FloatField(verbose_name='Pewność OCR (%)')),
                ('processing_time', models.FloatField(verbose_name='Czas przetwarzania (s)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')),
                ('field_confidence', models.JSONField(blank=True, default=dict, verbose_name='Pewność poszczególnych pól')),
                ('processor_version', models.CharField(blank=True, max_length=50, verbose_name='Wersja procesora')),
                ('processing_location', models.CharField(blank=True, max_length=50, verbose_name='Lokalizacja przetwarzania')),
                ('document', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='faktury.documentupload', verbose_name='Dokument')),
                ('faktura', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='faktury.faktura', verbose_name='Powiązana faktura')),
            ],
            options={
                'verbose_name': 'Wynik OCR',
                'verbose_name_plural': 'Wyniki OCR',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OCRValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validation_timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Data walidacji')),
                ('corrections_made', models.JSONField(default=dict, verbose_name='Wprowadzone poprawki')),
                ('accuracy_rating', models.IntegerField(choices=[(1, '1/10'), (2, '2/10'), (3, '3/10'), (4, '4/10'), (5, '5/10'), (6, '6/10'), (7, '7/10'), (8, '8/10'), (9, '9/10'), (10, '10/10')], verbose_name='Ocena dokładności')),
                ('validation_notes', models.TextField(blank=True, verbose_name='Notatki walidacji')),
                ('time_spent_minutes', models.PositiveIntegerField(blank=True, null=True, verbose_name='Czas walidacji (minuty)')),
                ('ocr_result', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='faktury.ocrresult', verbose_name='Wynik OCR')),
                ('validated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Zwalidowany przez')),
            ],
            options={
                'verbose_name': 'Walidacja OCR',
                'verbose_name_plural': 'Walidacje OCR',
                'ordering': ['-validation_timestamp'],
            },
        ),
        migrations.CreateModel(
            name='OCRProcessingLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Znacznik czasu')),
                ('level', models.CharField(choices=[('DEBUG', 'Debug'), ('INFO', 'Info'), ('WARNING', 'Warning'), ('ERROR', 'Error'), ('CRITICAL', 'Critical')], max_length=10, verbose_name='Poziom')),
                ('message', models.TextField(verbose_name='Wiadomość')),
                ('details', models.JSONField(blank=True, default=dict, verbose_name='Szczegóły')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='faktury.documentupload', verbose_name='Dokument')),
            ],
            options={
                'verbose_name': 'Log przetwarzania OCR',
                'verbose_name_plural': 'Logi przetwarzania OCR',
                'ordering': ['-timestamp'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='documentupload',
            index=models.Index(fields=['user', '-upload_timestamp'], name='faktury_documentupload_user_upload_idx'),
        ),
        migrations.AddIndex(
            model_name='documentupload',
            index=models.Index(fields=['processing_status'], name='faktury_documentupload_status_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(fields=['document'], name='faktury_ocrresult_document_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(fields=['faktura'], name='faktury_ocrresult_faktura_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(fields=['-created_at'], name='faktury_ocrresult_created_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(fields=['confidence_score'], name='faktury_ocrresult_confidence_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrvalidation',
            index=models.Index(fields=['validated_by', '-validation_timestamp'], name='faktury_ocrvalidation_user_validation_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrvalidation',
            index=models.Index(fields=['accuracy_rating'], name='faktury_ocrvalidation_accuracy_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrprocessinglog',
            index=models.Index(fields=['document', '-timestamp'], name='faktury_ocrprocessinglog_document_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrprocessinglog',
            index=models.Index(fields=['level'], name='faktury_ocrprocessinglog_level_idx'),
        ),
    ]