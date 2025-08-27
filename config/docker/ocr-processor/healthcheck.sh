#!/bin/bash

# OCR Processor Health Check Script
# Verifies that all OCR components are working correctly

set -e

echo "🏥 OCR Health Check Starting..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

# Check if Tesseract is available
if ! command -v tesseract &> /dev/null; then
    echo "❌ Tesseract not found"
    exit 1
fi

# Check Tesseract version
TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
echo "✅ $TESSERACT_VERSION"

# Check Polish language support
if tesseract --list-langs 2>&1 | grep -q "pol"; then
    echo "✅ Polish language support available"
else
    echo "❌ Polish language support not found"
    exit 1
fi

# Check Python OCR modules
python3 -c "
import sys
try:
    import pytesseract
    print('✅ pytesseract available')
except ImportError:
    print('❌ pytesseract not available')
    sys.exit(1)

try:
    import easyocr
    print('✅ easyocr available')
except ImportError:
    print('❌ easyocr not available')
    sys.exit(1)

try:
    import cv2
    print('✅ opencv available')
except ImportError:
    print('❌ opencv not available')
    sys.exit(1)

try:
    from PIL import Image
    print('✅ PIL available')
except ImportError:
    print('❌ PIL not available')
    sys.exit(1)
"

# Check if OCR service is responding (if running)
if [ -n "$OCR_SERVICE_PORT" ]; then
    if curl -f -s "http://localhost:${OCR_SERVICE_PORT}/health" > /dev/null; then
        echo "✅ OCR service responding on port $OCR_SERVICE_PORT"
    else
        echo "⚠️  OCR service not responding (may not be started yet)"
    fi
fi

# Check directory permissions
if [ -w "/app/temp" ]; then
    echo "✅ Temp directory writable"
else
    echo "❌ Temp directory not writable"
    exit 1
fi

if [ -w "/app/models" ]; then
    echo "✅ Models directory writable"
else
    echo "❌ Models directory not writable"
    exit 1
fi

echo "✅ OCR Health Check Passed!"
exit 0