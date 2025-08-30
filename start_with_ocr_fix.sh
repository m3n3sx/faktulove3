#!/bin/bash
# FaktuLove OCR Fix Startup

echo "🚀 Starting FaktuLove with OCR fix..."

# Start mock OCR service in background
echo "📡 Starting mock OCR service..."
python3 mock_ocr_service.py &
OCR_PID=$!

# Wait a moment for service to start
sleep 2

# Check if mock service is running
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Mock OCR service running"
else
    echo "⚠️ Mock OCR service may not be running"
fi

# Start Django
echo "🌐 Starting Django server..."
python manage.py runserver 0.0.0.0:8000

# Cleanup on exit
trap "kill $OCR_PID 2>/dev/null" EXIT
