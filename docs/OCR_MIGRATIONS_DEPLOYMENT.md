# OCR Migrations Deployment Guide

## Overview
This guide covers the deployment of OCR-related database migrations for the FaktuLove system. The migrations add performance indexes and data integrity constraints to the existing OCR fields in the Faktura model.

## Migration Files Created
- `faktury/migrations/0022_add_ocr_indexes.py` - Adds performance indexes
- `faktury/migrations/0023_add_ocr_constraints.py` - Adds data integrity constraints
- `ocr_migrations_sql_preview.sql` - SQL preview for review

## Pre-Deployment Checklist

### 1. Environment Verification
```bash
# Verify Django version
python manage.py --version
# Should be Django 4.2.x

# Verify PostgreSQL connection
python manage.py dbshell
# Should connect successfully
```

### 2. Database Backup
```bash
# Create backup before migration
pg_dump -h localhost -U your_username -d faktulove_db > backup_pre_ocr_migrations_$(date +%Y%m%d_%H%M%S).sql

# Or using Django management command if available
python manage.py dumpdata > backup_pre_ocr_migrations_$(date +%Y%m%d_%H%M%S).json
```

### 3. Check Current Migration State
```bash
# Check current migration status
python manage.py showmigrations faktury

# Should show 0021_add_ocr_fields_to_faktura as applied
```

## Deployment Steps

### Step 1: Apply Index Migration
```bash
# Apply the indexes migration
python manage.py migrate faktury 0022

# Expected output:
# Running migrations:
#   Applying faktury.0022_add_ocr_indexes... OK
```

### Step 2: Apply Constraints Migration
```bash
# Apply the constraints migration
python manage.py migrate faktury 0023

# Expected output:
# Running migrations:
#   Applying faktury.0023_add_ocr_constraints... OK
```

### Step 3: Verify Migration Success
```bash
# Check final migration state
python manage.py showmigrations faktury

# Verify indexes were created (PostgreSQL)
python manage.py dbshell
\d+ faktury_faktura
# Should show the new indexes

# Check constraints
SELECT conname, consrc FROM pg_constraint WHERE conrelid = 'faktury_faktura'::regclass;
```

## Performance Impact

### Index Creation Time
- **Small databases** (< 10k invoices): ~1-5 seconds
- **Medium databases** (10k-100k invoices): ~10-30 seconds  
- **Large databases** (> 100k invoices): ~1-5 minutes

### Storage Impact
- Each index adds approximately 8-16 bytes per row
- Total additional storage: ~50-100 bytes per invoice
- For 100k invoices: ~5-10 MB additional storage

## Rollback Procedure

If issues occur, rollback using:

```bash
# Rollback constraints migration
python manage.py migrate faktury 0022

# Rollback indexes migration  
python manage.py migrate faktury 0021

# Restore from backup if needed
psql -h localhost -U your_username -d faktulove_db < backup_file.sql
```

## Post-Deployment Verification

### 1. Test OCR Queries
```python
# Test in Django shell
python manage.py shell

from faktury.models import Faktura

# Test confidence filtering (should use index)
low_confidence = Faktura.objects.filter(ocr_confidence__lt=80.0)
print(f"Low confidence invoices: {low_confidence.count()}")

# Test manual verification filtering (should use index)
needs_verification = Faktura.objects.filter(manual_verification_required=True)
print(f"Invoices needing verification: {needs_verification.count()}")

# Test user-specific queries (should use compound indexes)
user_low_confidence = Faktura.objects.filter(
    user_id=1, 
    ocr_confidence__lt=80.0
)
print(f"User's low confidence invoices: {user_low_confidence.count()}")
```

### 2. Test Constraint Validation
```python
# Test in Django shell
from faktury.models import Faktura
from django.core.exceptions import ValidationError

# Test invalid confidence (should fail)
try:
    faktura = Faktura(ocr_confidence=150.0)  # Invalid: > 100
    faktura.full_clean()
    print("ERROR: Should have failed validation")
except ValidationError as e:
    print("SUCCESS: Confidence validation working")

# Test invalid processing time (should fail)
try:
    faktura = Faktura(ocr_processing_time=-1.0)  # Invalid: negative
    faktura.full_clean()
    print("ERROR: Should have failed validation")
except ValidationError as e:
    print("SUCCESS: Processing time validation working")
```

## Monitoring

### Query Performance
Monitor these common OCR queries for performance improvements:

```sql
-- Query 1: Low confidence invoices
EXPLAIN ANALYZE SELECT * FROM faktury_faktura WHERE ocr_confidence < 80.0;

-- Query 2: User's verification queue
EXPLAIN ANALYZE SELECT * FROM faktury_faktura 
WHERE user_id = 1 AND manual_verification_required = true;

-- Query 3: Recent OCR processing
EXPLAIN ANALYZE SELECT * FROM faktury_faktura 
WHERE ocr_extracted_at > NOW() - INTERVAL '7 days' 
ORDER BY ocr_extracted_at DESC;
```

### Index Usage
```sql
-- Check index usage statistics
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE tablename = 'faktury_faktura' 
AND indexname LIKE '%ocr%';
```

## Troubleshooting

### Common Issues

1. **Migration fails with "relation already exists"**
   - Check if indexes already exist manually
   - Use `DROP INDEX IF EXISTS` if needed

2. **Constraint violation on existing data**
   - Clean up invalid data before applying constraints:
   ```sql
   UPDATE faktury_faktura SET ocr_confidence = NULL WHERE ocr_confidence < 0 OR ocr_confidence > 100;
   UPDATE faktury_faktura SET ocr_processing_time = NULL WHERE ocr_processing_time < 0;
   ```

3. **Performance degradation during migration**
   - Run during low-traffic periods
   - Consider creating indexes CONCURRENTLY in production:
   ```sql
   CREATE INDEX CONCURRENTLY faktury_faktura_ocr_confidence_idx ON faktury_faktura (ocr_confidence);
   ```

## Success Criteria

✅ All migrations applied successfully  
✅ No data loss or corruption  
✅ Indexes created and being used by queries  
✅ Constraints preventing invalid data  
✅ OCR queries showing improved performance  
✅ Application functionality unchanged  

## Support

For issues during deployment:
1. Check Django and PostgreSQL logs
2. Verify database connectivity
3. Ensure sufficient disk space for indexes
4. Contact development team if rollback needed

---

**Deployment Date**: ___________  
**Deployed By**: ___________  
**Environment**: ___________  
**Status**: ___________