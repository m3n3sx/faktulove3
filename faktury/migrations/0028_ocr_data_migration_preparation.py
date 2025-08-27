# Generated migration for OCR data migration preparation

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('faktury', '0027_add_fallback_handling_fields'),
    ]

    operations = [
        # Create OCREngine model first
        migrations.CreateModel(
            name='OCREngine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nazwa silnika')),
                ('engine_type', models.CharField(
                    choices=[
                        ('tesseract', 'Tesseract OCR'),
                        ('easyocr', 'EasyOCR'),
                        ('composite', 'Composite Engine'),
                        ('google_cloud', 'Google Cloud Document AI'),
                    ],
                    max_length=20,
                    verbose_name='Typ silnika'
                )),
                ('version', models.CharField(max_length=20, verbose_name='Wersja')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktywny')),
                ('priority', models.IntegerField(default=1, verbose_name='Priorytet')),
                ('configuration', models.JSONField(blank=True, default=dict, verbose_name='Konfiguracja')),
                ('total_documents_processed', models.PositiveIntegerField(default=0, verbose_name='Przetworzone dokumenty')),
                ('average_processing_time', models.FloatField(blank=True, null=True, verbose_name='Średni czas przetwarzania (s)')),
                ('average_confidence_score', models.FloatField(blank=True, null=True, verbose_name='Średnia pewność (%)')),
                ('success_rate', models.FloatField(blank=True, null=True, verbose_name='Wskaźnik sukcesu (%)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Data aktualizacji')),
            ],
            options={
                'verbose_name': 'Silnik OCR',
                'verbose_name_plural': 'Silniki OCR',
                'ordering': ['priority', 'name'],
            },
        ),
        
        # Add enhanced fields to OCRResult for new architecture support
        migrations.AddField(
            model_name='ocrresult',
            name='primary_engine',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='primary_results',
                to='faktury.ocrengine',
                verbose_name='Główny silnik OCR'
            ),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='processing_location',
            field=models.CharField(
                blank=True,
                max_length=50,
                verbose_name='Lokalizacja przetwarzania'
            ),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='engine_results',
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name='Wyniki z poszczególnych silników'
            ),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='best_engine_result',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                verbose_name='Najlepszy wynik silnika'
            ),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='pipeline_version',
            field=models.CharField(
                default='2.0',
                max_length=20,
                verbose_name='Wersja pipeline\'u'
            ),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='preprocessing_applied',
            field=models.JSONField(
                blank=True,
                default=list,
                verbose_name='Zastosowane przetwarzanie wstępne'
            ),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='fallback_used',
            field=models.BooleanField(
                default=False,
                verbose_name='Użyto mechanizmu fallback'
            ),
        ),
        
        # Add field_confidence if it doesn't exist
        migrations.AddField(
            model_name='ocrresult',
            name='field_confidence',
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name='Pewność poszczególnych pól'
            ),
        ),
        

        
        # Create OCRProcessingStep model if it doesn't exist
        migrations.CreateModel(
            name='OCRProcessingStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_name', models.CharField(max_length=50, verbose_name='Nazwa kroku')),
                ('step_type', models.CharField(
                    choices=[
                        ('preprocessing', 'Preprocessing'),
                        ('ocr_extraction', 'OCR Text Extraction'),
                        ('field_extraction', 'Field Extraction'),
                        ('confidence_calculation', 'Confidence Calculation'),
                        ('validation', 'Data Validation'),
                        ('post_processing', 'Post Processing'),
                    ],
                    max_length=25,
                    verbose_name='Typ kroku'
                )),
                ('step_order', models.PositiveIntegerField(verbose_name='Kolejność kroku')),
                ('step_status', models.CharField(
                    choices=[
                        ('pending', 'Oczekuje'),
                        ('processing', 'Przetwarzanie'),
                        ('completed', 'Zakończone'),
                        ('failed', 'Błąd'),
                        ('skipped', 'Pominięte'),
                    ],
                    default='pending',
                    max_length=20,
                    verbose_name='Status kroku'
                )),
                ('processing_time', models.FloatField(verbose_name='Czas przetwarzania (s)')),
                ('confidence_score', models.FloatField(verbose_name='Pewność kroku (%)')),
                ('step_data', models.JSONField(verbose_name='Dane kroku')),
                ('input_data', models.JSONField(blank=True, default=dict, verbose_name='Dane wejściowe')),
                ('output_data', models.JSONField(blank=True, default=dict, verbose_name='Dane wyjściowe')),
                ('error_message', models.TextField(blank=True, null=True, verbose_name='Komunikat błędu')),
                ('started_at', models.DateTimeField(verbose_name='Rozpoczęcie')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Zakończenie')),
                ('ocr_result', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='processing_steps',
                    to='faktury.ocrresult',
                    verbose_name='Wynik OCR'
                )),
                ('engine_used', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='faktury.ocrengine',
                    verbose_name='Użyty silnik'
                )),
            ],
            options={
                'verbose_name': 'Krok przetwarzania OCR',
                'verbose_name_plural': 'Kroki przetwarzania OCR',
                'ordering': ['ocr_result', 'step_order'],
            },
        ),
        
        # Create OCRValidation model if it doesn't exist
        migrations.CreateModel(
            name='OCRValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validation_timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Data walidacji')),
                ('corrections_made', models.JSONField(default=dict, verbose_name='Wprowadzone poprawki')),
                ('accuracy_rating', models.IntegerField(
                    choices=[(i, f"{i}/10") for i in range(1, 11)],
                    verbose_name='Ocena dokładności'
                )),
                ('validation_notes', models.TextField(blank=True, verbose_name='Notatki walidacji')),
                ('time_spent_minutes', models.PositiveIntegerField(
                    blank=True,
                    null=True,
                    verbose_name='Czas walidacji (minuty)'
                )),
                ('ocr_result', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='faktury.ocrresult',
                    verbose_name='Wynik OCR'
                )),
                ('validated_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='auth.user',
                    verbose_name='Zwalidowany przez'
                )),
            ],
            options={
                'verbose_name': 'Walidacja OCR',
                'verbose_name_plural': 'Walidacje OCR',
                'ordering': ['-validation_timestamp'],
            },
        ),
        
        # Create OCRProcessingLog model if it doesn't exist
        migrations.CreateModel(
            name='OCRProcessingLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Znacznik czasu')),
                ('level', models.CharField(
                    choices=[
                        ('DEBUG', 'Debug'),
                        ('INFO', 'Info'),
                        ('WARNING', 'Warning'),
                        ('ERROR', 'Error'),
                        ('CRITICAL', 'Critical'),
                    ],
                    max_length=10,
                    verbose_name='Poziom'
                )),
                ('message', models.TextField(verbose_name='Wiadomość')),
                ('details', models.JSONField(blank=True, default=dict, verbose_name='Szczegóły')),
                ('document', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='faktury.documentupload',
                    verbose_name='Dokument'
                )),
                ('processing_step', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='faktury.ocrprocessingstep',
                    verbose_name='Krok przetwarzania'
                )),
            ],
            options={
                'verbose_name': 'Log przetwarzania OCR',
                'verbose_name_plural': 'Logi przetwarzania OCR',
                'ordering': ['-timestamp'],
            },
        ),
        
        # Add many-to-many relationship for engines_used
        migrations.AddField(
            model_name='ocrresult',
            name='engines_used',
            field=models.ManyToManyField(
                related_name='all_results',
                through='faktury.OCRProcessingStep',
                to='faktury.ocrengine',
                verbose_name='Użyte silniki'
            ),
        ),
        
        # Add indexes for performance
        migrations.AddIndex(
            model_name='ocrengine',
            index=models.Index(fields=['engine_type', 'is_active'], name='faktury_ocrengine_type_active_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrengine',
            index=models.Index(fields=['priority'], name='faktury_ocrengine_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrprocessingstep',
            index=models.Index(fields=['ocr_result', 'step_order'], name='faktury_ocrprocessingstep_result_order_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrprocessingstep',
            index=models.Index(fields=['engine_used', '-started_at'], name='faktury_ocrprocessingstep_engine_time_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrprocessingstep',
            index=models.Index(fields=['step_type', 'step_status'], name='faktury_ocrprocessingstep_type_status_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrvalidation',
            index=models.Index(fields=['validated_by', '-validation_timestamp'], name='faktury_ocrvalidation_user_time_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrvalidation',
            index=models.Index(fields=['accuracy_rating'], name='faktury_ocrvalidation_rating_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrprocessinglog',
            index=models.Index(fields=['document', '-timestamp'], name='faktury_ocrprocessinglog_doc_time_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrprocessinglog',
            index=models.Index(fields=['processing_step', '-timestamp'], name='faktury_ocrprocessinglog_step_time_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrprocessinglog',
            index=models.Index(fields=['level'], name='faktury_ocrprocessinglog_level_idx'),
        ),
        
        # Add constraints
        migrations.AddConstraint(
            model_name='ocrengine',
            constraint=models.UniqueConstraint(fields=['name', 'version'], name='unique_engine_version'),
        ),
        migrations.AddConstraint(
            model_name='ocrprocessingstep',
            constraint=models.UniqueConstraint(
                fields=['ocr_result', 'step_name', 'step_order'],
                name='unique_step_per_result'
            ),
        ),
    ]