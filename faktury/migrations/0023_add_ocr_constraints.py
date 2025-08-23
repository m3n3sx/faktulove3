# Generated manually for OCR data integrity

from django.db import migrations, models
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('faktury', '0022_add_ocr_indexes'),
    ]

    operations = [
        # Add constraints for ocr_confidence (0.0 to 100.0)
        migrations.AlterField(
            model_name='faktura',
            name='ocr_confidence',
            field=models.FloatField(
                blank=True, 
                null=True, 
                verbose_name='Pewność OCR (%)',
                validators=[
                    MinValueValidator(0.0, message='Pewność OCR nie może być mniejsza niż 0%'),
                    MaxValueValidator(100.0, message='Pewność OCR nie może być większa niż 100%')
                ]
            ),
        ),
        
        # Add constraints for ocr_processing_time (>= 0)
        migrations.AlterField(
            model_name='faktura',
            name='ocr_processing_time',
            field=models.FloatField(
                blank=True, 
                null=True, 
                verbose_name='Czas przetwarzania OCR (s)',
                validators=[
                    MinValueValidator(0.0, message='Czas przetwarzania OCR nie może być ujemny')
                ]
            ),
        ),
        
        # Database constraints are handled at the Django model level via validators
        # This ensures compatibility with both SQLite and PostgreSQL
        # The actual constraints are defined in the model field validators
    ]