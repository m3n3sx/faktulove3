-- SQL Preview for OCR Migrations
-- This file shows the SQL commands that will be executed by the Django migrations

-- ============================================================================
-- Migration 0022: Add OCR Indexes
-- ============================================================================

-- Individual index on ocr_confidence for filtering by confidence level
CREATE INDEX "faktury_faktura_ocr_confidence_idx" ON "faktury_faktura" ("ocr_confidence");

-- Individual index on manual_verification_required for filtering invoices requiring manual review
CREATE INDEX "faktury_faktura_manual_verification_idx" ON "faktury_faktura" ("manual_verification_required");

-- Compound index on user + ocr_confidence for user-specific OCR confidence queries
CREATE INDEX "faktury_faktura_user_ocr_confidence_idx" ON "faktury_faktura" ("user_id", "ocr_confidence");

-- Compound index on user + manual_verification_required for user-specific verification queries
CREATE INDEX "faktury_faktura_user_manual_verification_idx" ON "faktury_faktura" ("user_id", "manual_verification_required");

-- Index on ocr_extracted_at (descending) for temporal OCR queries
CREATE INDEX "faktury_faktura_ocr_extracted_at_idx" ON "faktury_faktura" ("ocr_extracted_at" DESC);

-- Index on source_document for linking back to original documents
CREATE INDEX "faktury_faktura_source_document_idx" ON "faktury_faktura" ("source_document_id");

-- ============================================================================
-- Migration 0023: Add OCR Constraints
-- ============================================================================

-- Check constraint for ocr_confidence (0.0 to 100.0)
ALTER TABLE faktury_faktura 
ADD CONSTRAINT faktury_faktura_ocr_confidence_range 
CHECK (ocr_confidence IS NULL OR (ocr_confidence >= 0.0 AND ocr_confidence <= 100.0));

-- Check constraint for ocr_processing_time (>= 0.0)
ALTER TABLE faktury_faktura 
ADD CONSTRAINT faktury_faktura_ocr_processing_time_positive 
CHECK (ocr_processing_time IS NULL OR ocr_processing_time >= 0.0);

-- ============================================================================
-- Performance Benefits
-- ============================================================================

-- These indexes will optimize the following common queries:

-- 1. Find invoices with low OCR confidence requiring review:
--    SELECT * FROM faktury_faktura WHERE ocr_confidence < 80.0;
--    Uses: faktury_faktura_ocr_confidence_idx

-- 2. Find user's invoices requiring manual verification:
--    SELECT * FROM faktury_faktura WHERE user_id = ? AND manual_verification_required = true;
--    Uses: faktury_faktura_user_manual_verification_idx

-- 3. Find user's invoices with confidence above threshold:
--    SELECT * FROM faktury_faktura WHERE user_id = ? AND ocr_confidence > 90.0;
--    Uses: faktury_faktura_user_ocr_confidence_idx

-- 4. Find recently processed OCR invoices:
--    SELECT * FROM faktury_faktura WHERE ocr_extracted_at > '2025-08-01' ORDER BY ocr_extracted_at DESC;
--    Uses: faktury_faktura_ocr_extracted_at_idx

-- 5. Find invoices linked to specific document:
--    SELECT * FROM faktury_faktura WHERE source_document_id = ?;
--    Uses: faktury_faktura_source_document_idx

-- ============================================================================
-- Data Integrity Benefits
-- ============================================================================

-- The constraints ensure:
-- 1. OCR confidence is always between 0% and 100%
-- 2. Processing time is never negative
-- 3. Database-level validation prevents invalid data insertion
-- 4. Consistent data quality across the application