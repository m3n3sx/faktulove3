# Generated manually for OCR optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faktury', '0021_add_ocr_fields_to_faktura'),
    ]

    operations = [
        # Add individual indexes for OCR fields
        migrations.AddIndex(
            model_name='faktura',
            index=models.Index(
                fields=['ocr_confidence'], 
                name='faktury_faktura_ocr_confidence_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='faktura',
            index=models.Index(
                fields=['manual_verification_required'], 
                name='faktury_faktura_manual_verification_idx'
            ),
        ),
        
        # Add compound index for user + ocr_confidence (for user-specific OCR queries)
        migrations.AddIndex(
            model_name='faktura',
            index=models.Index(
                fields=['user', 'ocr_confidence'], 
                name='faktury_faktura_user_ocr_confidence_idx'
            ),
        ),
        
        # Add compound index for user + manual_verification_required (for filtering user's invoices requiring verification)
        migrations.AddIndex(
            model_name='faktura',
            index=models.Index(
                fields=['user', 'manual_verification_required'], 
                name='faktury_faktura_user_manual_verification_idx'
            ),
        ),
        
        # Add index for OCR extraction timestamp (for temporal queries)
        migrations.AddIndex(
            model_name='faktura',
            index=models.Index(
                fields=['-ocr_extracted_at'], 
                name='faktury_faktura_ocr_extracted_at_idx'
            ),
        ),
        
        # Add compound index for source_document (for linking back to original documents)
        migrations.AddIndex(
            model_name='faktura',
            index=models.Index(
                fields=['source_document'], 
                name='faktury_faktura_source_document_idx'
            ),
        ),
    ]