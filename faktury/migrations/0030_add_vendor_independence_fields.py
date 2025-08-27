# Generated migration for vendor independence tracking
from django.db import migrations, models


def set_default_ensemble_engines(apps, schema_editor):
    """Set default empty list for ensemble_engines_used field"""
    OCRResult = apps.get_model('faktury', 'OCRResult')
    OCRResult.objects.filter(ensemble_engines_used__isnull=True).update(ensemble_engines_used=[])


class Migration(migrations.Migration):

    dependencies = [
        ('faktury', '0029_fix_ocr_model_references'),
    ]

    operations = [
        # Add simple fields first
        migrations.AddField(
            model_name='ocrresult',
            name='ocr_engine',
            field=models.CharField(default='ensemble', max_length=50, verbose_name='Silnik OCR'),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='vendor_independent',
            field=models.BooleanField(default=True, verbose_name='Niezależny od dostawcy'),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='google_cloud_replaced',
            field=models.BooleanField(default=True, verbose_name='Google Cloud zastąpiony'),
        ),
        migrations.AddField(
            model_name='ocrresult',
            name='cost_per_processing',
            field=models.DecimalField(decimal_places=4, default=0.0, max_digits=10, verbose_name='Koszt przetwarzania'),
        ),
        # Add JSON field separately to avoid constraint issues
        migrations.AddField(
            model_name='ocrresult',
            name='ensemble_engines_used',
            field=models.TextField(default='[]', verbose_name='Użyte silniki ensemble'),
        ),
        # Set default values for JSON field
        migrations.RunPython(set_default_ensemble_engines, migrations.RunPython.noop),
        # Add performance indexes
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(fields=['vendor_independent'], name='faktury_ocrresult_vendor_independent_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(fields=['google_cloud_replaced'], name='faktury_ocrresult_google_cloud_replaced_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(fields=['ocr_engine'], name='faktury_ocrresult_ocr_engine_idx'),
        ),
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(fields=['cost_per_processing'], name='faktury_ocrresult_cost_per_processing_idx'),
        ),
        # Compound index for vendor independence tracking
        migrations.AddIndex(
            model_name='ocrresult',
            index=models.Index(fields=['vendor_independent', 'google_cloud_replaced'], name='faktury_ocrresult_vendor_status_idx'),
        ),
    ]