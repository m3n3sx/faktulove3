# OCR Data Migration Guide

This guide covers the migration of OCR data from Google Cloud Document AI to open-source OCR engines.

## Overview

The migration process includes:
1. **Data Migration**: Update existing OCRResult records to use new OCR engines
2. **Processor Mapping**: Map Google Cloud processor versions to open-source engines
3. **Confidence Recalculation**: Recalculate confidence scores for historical data
4. **Validation**: Ensure data integrity throughout the process
5. **Rollback**: Ability to restore pre-migration state if needed

## Migration Scripts

### 1. migrate_ocr_data.py
Main migration command that handles the complete migration process.

**Usage:**
```bash
# Preview migration changes (recommended first step)
python manage.py migrate_ocr_data --dry-run

# Execute migration with default settings
python manage.py migrate_ocr_data --execute

# Execute with custom batch size and backup file
python manage.py migrate_ocr_data --execute --batch-size=50 --backup-file=my_backup.json

# Force migration even if validation fails
python manage.py migrate_ocr_data --execute --force
```

**Options:**
- `--dry-run`: Preview changes without executing them
- `--execute`: Execute the migration
- `--batch-size=N`: Process N records at a time (default: 100)
- `--backup-file=FILE`: Specify backup file location (default: ocr_migration_backup.json)
- `--force`: Force migration even if validation fails

### 2. validate_ocr_migration.py
Validation command for checking migration integrity.

**Usage:**
```bash
# Pre-migration validation
python manage.py validate_ocr_migration --pre-migration

# Post-migration validation
python manage.py validate_ocr_migration --post-migration

# Comprehensive validation with output file
python manage.py validate_ocr_migration --full-check --output-file=validation_report.json
```

**Options:**
- `--pre-migration`: Run pre-migration validation checks
- `--post-migration`: Run post-migration validation checks
- `--full-check`: Run comprehensive validation
- `--output-file=FILE`: Save validation results to JSON file
- `--sample-size=N`: Sample size for performance testing (default: 1000)

### 3. rollback_ocr_migration.py
Rollback command to restore pre-migration state.

**Usage:**
```bash
# Preview rollback changes
python manage.py rollback_ocr_migration --backup-file=ocr_migration_backup.json --dry-run

# Execute rollback
python manage.py rollback_ocr_migration --backup-file=ocr_migration_backup.json --execute

# Auto-detect backup file and rollback
python manage.py rollback_ocr_migration --auto-detect-backup --execute

# Rollback with cleanup of migration artifacts
python manage.py rollback_ocr_migration --backup-file=backup.json --execute --cleanup-migration-artifacts
```

**Options:**
- `--backup-file=FILE`: Specify backup file to use for rollback
- `--auto-detect-backup`: Automatically find and use most recent backup file
- `--dry-run`: Preview rollback changes
- `--execute`: Execute the rollback
- `--force`: Force rollback even if validation fails
- `--preserve-new-data`: Keep data created after migration
- `--cleanup-migration-artifacts`: Remove migration-specific engines and processing steps

## Migration Process

### Step 1: Pre-Migration Preparation

1. **Run database migration** to add new schema:
   ```bash
   python manage.py migrate
   ```

2. **Validate current state**:
   ```bash
   python manage.py validate_ocr_migration --pre-migration
   ```

3. **Preview migration changes**:
   ```bash
   python manage.py migrate_ocr_data --dry-run
   ```

### Step 2: Execute Migration

1. **Run the migration**:
   ```bash
   python manage.py migrate_ocr_data --execute
   ```

2. **Validate migration success**:
   ```bash
   python manage.py validate_ocr_migration --post-migration
   ```

### Step 3: Post-Migration Verification

1. **Run comprehensive validation**:
   ```bash
   python manage.py validate_ocr_migration --full-check --output-file=final_validation.json
   ```

2. **Test API functionality** to ensure backward compatibility

3. **Monitor system performance** for any degradation

### Step 4: Rollback (if needed)

If issues are discovered after migration:

1. **Stop all OCR processing** to prevent data conflicts

2. **Execute rollback**:
   ```bash
   python manage.py rollback_ocr_migration --backup-file=ocr_migration_backup.json --execute
   ```

3. **Validate rollback**:
   ```bash
   python manage.py validate_ocr_migration --pre-migration
   ```

## Data Mapping

### Processor Version Mapping

| Original Processor | New Engine | Notes |
|-------------------|------------|-------|
| `google-document-ai-*` | Composite Engine | Maps to multi-engine approach |
| `document-ai-*` | Composite Engine | Maps to multi-engine approach |
| `null` or empty | Composite Engine | Default for unknown processors |
| `mock` | Composite Engine | Test data mapping |

### Engine Priority

1. **Composite Engine** (Priority 1): Combines multiple engines for best results
2. **Tesseract OCR** (Priority 2): Primary text extraction engine
3. **EasyOCR** (Priority 3): Secondary engine for improved accuracy

### Confidence Score Recalculation

Confidence scores are recalculated based on:
- **Field presence** (60% base confidence for non-empty fields)
- **Field-specific validation** (additional confidence based on field type)
- **Polish language patterns** (bonus for recognized Polish business formats)
- **Data structure quality** (bonus for well-structured data)

## Backup and Recovery

### Backup Data Structure

The backup file contains:
```json
{
  "ocr_result_id": {
    "processor_version": "original_processor_version",
    "processing_location": "original_location",
    "primary_engine_id": null,
    "pipeline_version": "1.0",
    "confidence_score": 85.5
  }
}
```

### Recovery Procedures

1. **Immediate Recovery**: Use rollback command with backup file
2. **Database Recovery**: Restore from database backup if rollback fails
3. **Partial Recovery**: Use `--preserve-new-data` to keep post-migration data

## Monitoring and Troubleshooting

### Key Metrics to Monitor

- **Migration Progress**: Number of records processed vs. total
- **Error Rate**: Failed migrations per batch
- **Performance**: Processing time per record
- **Confidence Distribution**: Changes in confidence score patterns

### Common Issues

1. **Validation Failures**:
   - Check for orphaned OCR results
   - Verify foreign key integrity
   - Use `--force` flag if issues are non-critical

2. **Performance Issues**:
   - Reduce batch size with `--batch-size` parameter
   - Monitor database connection pool
   - Check available memory and disk space

3. **Rollback Issues**:
   - Ensure backup file is intact and readable
   - Check for new data created after migration
   - Use `--force` flag for problematic rollbacks

### Logging

Migration activities are logged to:
- **Django logs**: Standard Django logging configuration
- **Migration logs**: Detailed migration progress and errors
- **Validation reports**: JSON files with comprehensive validation results

## Testing

Run the test suite to verify migration functionality:

```bash
# Run all migration tests
python manage.py test faktury.tests.test_ocr_data_migration

# Run specific test cases
python manage.py test faktury.tests.test_ocr_data_migration.OCRDataMigrationTestCase
python manage.py test faktury.tests.test_ocr_data_migration.OCRMigrationValidationTestCase
python manage.py test faktury.tests.test_ocr_data_migration.OCRMigrationRollbackTestCase
```

## Best Practices

1. **Always run dry-run first** to preview changes
2. **Validate before and after migration** to ensure data integrity
3. **Keep backup files safe** for potential rollback needs
4. **Monitor system performance** during and after migration
5. **Test API compatibility** after migration
6. **Document any custom modifications** for future reference

## Support

For issues or questions regarding the migration:

1. Check the validation report for specific error details
2. Review Django logs for detailed error messages
3. Use the test suite to verify functionality
4. Consult the migration code comments for implementation details

## Migration Checklist

- [ ] Database schema migration applied
- [ ] Pre-migration validation passed
- [ ] Dry-run migration completed successfully
- [ ] Backup file location confirmed
- [ ] Migration executed successfully
- [ ] Post-migration validation passed
- [ ] API compatibility verified
- [ ] Performance monitoring in place
- [ ] Rollback procedure tested (optional)
- [ ] Documentation updated