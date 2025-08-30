#!/usr/bin/env python3
"""
Minimalny fix OCR warnings - tylko mock service i konfiguracja
"""

import os
import json
from pathlib import Path

def create_mock_ocr_service():
    """Utwórz mock OCR service"""
    print("🔧 Tworzenie mock OCR service...")
    
    mock_service = '''#!/usr/bin/env python3
"""Mock OCR Service na porcie 8001"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class MockOCRHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'service': 'Mock OCR Service',
                'timestamp': time.time()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def main():
    server = HTTPServer(('localhost', 8001), MockOCRHandler)
    print("🚀 Mock OCR Service running on http://localhost:8001")
    print("📡 Health check: http://localhost:8001/health")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\n🛑 Stopping mock service...")
        server.shutdown()

if __name__ == '__main__':
    main()
'''
    
    with open('mock_ocr_service.py', 'w') as f:
        f.write(mock_service)
    
    os.chmod('mock_ocr_service.py', 0o755)
    print("   ✅ Mock service utworzony")

def create_paddle_dir():
    """Utwórz katalog PaddleOCR"""
    print("📁 Tworzenie katalogu PaddleOCR...")
    
    paddle_dir = Path.home() / "faktulove_paddle_models"
    paddle_dir.mkdir(exist_ok=True)
    
    readme = paddle_dir / "README.md"
    readme.write_text("# PaddleOCR Models\\nModels directory for FaktuLove")
    
    print(f"   ✅ Katalog: {paddle_dir}")

def create_startup_script():
    """Utwórz skrypt startowy"""
    print("📜 Tworzenie skryptu startowego...")
    
    startup = '''#!/bin/bash
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
'''
    
    with open('start_with_ocr_fix.sh', 'w') as f:
        f.write(startup)
    
    os.chmod('start_with_ocr_fix.sh', 0o755)
    print("   ✅ Skrypt: start_with_ocr_fix.sh")

def main():
    print("⚡ Minimalny OCR Fix")
    print("=" * 30)
    
    create_mock_ocr_service()
    create_paddle_dir()
    create_startup_script()
    
    print("\n✅ OCR Fix ukończony!")
    print("\n🚀 Uruchom aplikację:")
    print("   ./start_with_ocr_fix.sh")
    print("\n📡 Lub ręcznie:")
    print("   1. python3 mock_ocr_service.py  # terminal 1")
    print("   2. python manage.py runserver   # terminal 2")

if __name__ == '__main__':
    main()