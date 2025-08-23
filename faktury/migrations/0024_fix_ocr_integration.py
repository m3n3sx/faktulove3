# Generated manually for OCR integration fixes

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('faktury', '0023_add_ocr_constraints'),
    ]

    operations = [
        # Fix OCRResult foreign key to Faktura with proper related_name
        migrations.AlterField(
            model_name='ocrresult',
            name='faktura',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL,  # Changed from CASCADE to SET_NULL
                related_name='ocr_results',  # Added proper related_name
                to='faktury.faktura', 
                verbose_name='Powiązana faktura'
            ),
        ),
        
        # Add processing status to OCRResult for better tracking
        migrations.AddField(
            model_name='ocrresult',
            name='processing_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Oczekuje'),
                    ('processing', 'Przetwarzanie'),
                    ('completed', 'Zakończone'),
                    ('failed', 'Błąd'),
                    ('manual_review', 'Wymaga przeglądu'),
                ],
                default='pending',
                max_length=20,
                verbose_name='Status przetwarzania'
            ),
        ),
        
        # Add error message field for failed processing
        migrations.AddField(
            model_name='ocrresult',
            name='error_message',
            field=models.TextField(
                blank=True, 
                null=True, 
                verbose_name='Komunikat błędu'
            ),
        ),
        
        # Add auto-created flag to track automatically created invoices
        migrations.AddField(
            model_name='ocrresult',
            name='auto_created_faktura',
            field=models.BooleanField(
                default=False,
                verbose_name='Automatycznie utworzona faktura'
            ),
        ),
        
        # Add index for processing status
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(
                fields=['processing_status'], 
                name='faktury_ocrresult_processing_status_idx'
            ),
        ),
        
        # Add compound index for document and processing status
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(
                fields=['document', 'processing_status'], 
                name='faktury_ocrresult_doc_status_idx'
            ),
        ),
    ]