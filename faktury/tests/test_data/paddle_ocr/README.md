# PaddleOCR Test Data

This directory contains test data for PaddleOCR integration tests and benchmarks.

## Test Document Categories

### High-Quality Invoices
- Clear, well-formatted Polish invoices
- Expected accuracy: >90%
- Expected processing time: <2s

### Medium-Quality Scans
- Standard quality scanned documents
- Expected accuracy: >80%
- Expected processing time: <3s

### Low-Quality Scans
- Noisy, low-resolution documents
- Expected accuracy: >65%
- Expected processing time: <4s

### Handwritten Elements
- Invoices with handwritten annotations
- Expected accuracy: >55%
- Expected processing time: <5s

### PDF Documents
- Digital PDF invoices
- Expected accuracy: >95%
- Expected processing time: <1.5s

## Test Data Structure

Each test document includes:
- Original document file
- Expected extraction results (JSON)
- Processing metadata
- Validation checksums

## Usage

Test data is used by:
- `test_paddle_ocr_integration_benchmarks.py`
- Performance monitoring scripts
- Accuracy validation tests
- Load testing scenarios