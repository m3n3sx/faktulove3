#!/bin/bash
# Run all tests

source venv/bin/activate

echo "Running Django tests..."
python manage.py test faktury.tests

echo "Running OCR integration tests..."
python manage.py test faktury.tests.test_ocr_integration

echo "Tests complete"