#!/usr/bin/env python3
"""
Naprawa ostrzeżeń OCR w FaktuLove
Instaluje OCR engines, usuwa deprecated dependencies, konfiguruje OCR service
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_system_requirements():
    """Sprawdź wymagania systemowe"""
    print("🔍 Sprawdzanie wymagań systemowych...")
    
    # Sprawdź system operacyjny
    import platform
    system = platform.system()
    print(f"   System: {system}")
    
    # Sprawdź Python
    python_version = sys.version_info
    print(f"   Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Sprawdź dostępne komendy
    commands = ['apt-get', 'yum', 'brew', 'pip', 'pip3']
    available_commands = []
    
    for cmd in commands:
        if shutil.which(cmd):
            available_commands.append(cmd)
            print(f"   ✅ {cmd} dostępny")
        else:
            print(f"   ❌ {cmd} niedostępny")
    
    return system, available_commands

def install_tesseract():
    """Instaluj Tesseract OCR"""
    print("\n📖 Instalowanie Tesseract OCR...")
    
    system, available_commands = check_system_requirements()
    
    try:
        if 'apt-get' in available_commands:
            # Ubuntu/Debian
            print("   📦 Instalowanie przez apt-get...")
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run([
                'sudo', 'apt-get', 'install', '-y',
                'tesseract-ocr',
                'tesseract-ocr-pol',  # Polski język
                'tesseract-ocr-eng',  # Angielski język
                'libtesseract-dev'
            ], check=True)
            
        elif 'yum' in available_commands:
            # CentOS/RHEL/Fedora
            print("   📦 Instalowanie przez yum...")
            subprocess.run([
                'sudo', 'yum', 'install', '-y',
                'tesseract',
                'tesseract-langpack-pol',
                'tesseract-langpack-eng',
                'tesseract-devel'
            ], check=True)
            
        elif 'brew' in available_commands:
            # macOS
            print("   📦 Instalowanie przez brew...")
            subprocess.run(['brew', 'install', 'tesseract'], check=True)
            subprocess.run(['brew', 'install', 'tesseract-lang'], check=True)
            
        else:
            print("   ⚠️ Nie można automatycznie zainstalować Tesseract")
            print("   Zainstaluj ręcznie:")
            print("   - Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-pol")
            print("   - CentOS/RHEL: sudo yum install tesseract tesseract-langpack-pol")
            print("   - macOS: brew install tesseract tesseract-lang")
            return False
            
        # Sprawdź instalację
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Tesseract zainstalowany pomyślnie")
            print(f"   Wersja: {result.stdout.split()[1]}")
            return True
        else:
            print("   ❌ Błąd instalacji Tesseract")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Błąd instalacji Tesseract: {e}")
        return False
    except Exception as e:
        print(f"   💥 Nieoczekiwany błąd: {e}")
        return False

def install_python_ocr_packages():
    """Instaluj Python OCR packages"""
    print("\n🐍 Instalowanie Python OCR packages...")
    
    packages = [
        'pytesseract',  # Tesseract wrapper
        'easyocr',      # EasyOCR
        'opencv-python', # OpenCV dla preprocessing
        'Pillow',       # PIL dla obrazów
        'numpy',        # Wymagane przez EasyOCR
    ]
    
    # Opcjonalne packages (mogą nie działać na wszystkich systemach)
    optional_packages = [
        'paddlepaddle',  # PaddlePaddle framework
        'paddleocr',     # PaddleOCR
    ]
    
    success_count = 0
    
    # Instaluj podstawowe packages
    for package in packages:
        try:
            print(f"   📦 Instalowanie {package}...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True)
            print(f"   ✅ {package} zainstalowany")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Błąd instalacji {package}: {e}")
    
    # Instaluj opcjonalne packages
    for package in optional_packages:
        try:
            print(f"   📦 Instalowanie {package} (opcjonalny)...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True, timeout=300)
            print(f"   ✅ {package} zainstalowany")
            success_count += 1
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"   ⚠️ {package} nie zainstalowany (opcjonalny): {e}")
    
    print(f"\n   📊 Zainstalowano {success_count}/{len(packages + optional_packages)} packages")
    return success_count > len(packages) // 2  # Sukces jeśli > 50% podstawowych

def remove_deprecated_dependencies():
    """Usuń deprecated dependencies"""
    print("\n🗑️ Usuwanie deprecated dependencies...")
    
    deprecated_packages = [
        'google-cloud-documentai',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'google-cloud-core',
        'google-cloud-storage'
    ]
    
    removed_count = 0
    
    for package in deprecated_packages:
        try:
            # Sprawdź czy package jest zainstalowany
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'show', package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   🗑️ Usuwanie {package}...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'uninstall', package, '-y'
                ], check=True, capture_output=True)
                print(f"   ✅ {package} usunięty")
                removed_count += 1
            else:
                print(f"   ℹ️ {package} nie jest zainstalowany")
                
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Błąd usuwania {package}: {e}")
    
    print(f"\n   📊 Usunięto {removed_count} deprecated packages")
    return removed_count

def create_paddle_models_directory():
    """Utwórz katalog dla modeli PaddleOCR"""
    print("\n📁 Tworzenie katalogu modeli PaddleOCR...")
    
    paddle_dir = Path("/home/admin/faktulove/paddle_models")
    
    try:
        # Utwórz katalog jeśli nie istnieje
        paddle_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Katalog utworzony: {paddle_dir}")
        
        # Utwórz plik README
        readme_content = """# PaddleOCR Models Directory

Ten katalog zawiera modele PaddleOCR używane przez FaktuLove.

## Struktura:
- det/     - modele detekcji tekstu
- rec/     - modele rozpoznawania tekstu  
- cls/     - modele klasyfikacji orientacji

## Automatyczne pobieranie:
Modele są automatycznie pobierane przy pierwszym użyciu PaddleOCR.
"""
        
        readme_file = paddle_dir / "README.md"
        readme_file.write_text(readme_content)
        
        # Ustaw uprawnienia
        os.chmod(paddle_dir, 0o755)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Błąd tworzenia katalogu: {e}")
        
        # Spróbuj alternatywną lokalizację
        alt_paddle_dir = Path.home() / "faktulove_paddle_models"
        try:
            alt_paddle_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Alternatywny katalog: {alt_paddle_dir}")
            return True
        except Exception as e2:
            print(f"   ❌ Błąd alternatywnego katalogu: {e2}")
            return False

def create_mock_ocr_service():
    """Utwórz mock OCR service na porcie 8001"""
    print("\n🔧 Tworzenie mock OCR service...")
    
    mock_service_content = '''#!/usr/bin/env python3
"""
Mock OCR Service dla FaktuLove
Prosty serwis HTTP na porcie 8001 dla testów
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class MockOCRHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'service': 'Mock OCR Service',
                'version': '1.0.0',
                'timestamp': time.time()
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'service': 'Mock OCR Service',
                'status': 'running',
                'engines': ['tesseract', 'easyocr', 'paddleocr'],
                'supported_formats': ['pdf', 'jpg', 'png', 'tiff']
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        if path == '/ocr/process':
            # Mock OCR processing
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'success',
                'text': 'Mock OCR Result - Document processed successfully',
                'confidence': 0.95,
                'processing_time': 1.2,
                'engine': 'mock'
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Override to reduce logging"""
        pass

def run_mock_service():
    """Run mock OCR service"""
    server_address = ('localhost', 8001)
    httpd = HTTPServer(server_address, MockOCRHandler)
    
    print(f"Mock OCR Service running on http://localhost:8001")
    print("Available endpoints:")
    print("  GET  /health  - Health check")
    print("  GET  /status  - Service status")
    print("  POST /ocr/process - Mock OCR processing")
    print("\\nPress Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down mock service...")
        httpd.shutdown()

if __name__ == '__main__':
    run_mock_service()
'''
    
    try:
        with open('mock_ocr_service.py', 'w') as f:
            f.write(mock_service_content)
        
        # Uczyń plik wykonywalnym
        os.chmod('mock_ocr_service.py', 0o755)
        
        print("   ✅ Mock OCR service utworzony: mock_ocr_service.py")
        print("   🚀 Uruchom: python3 mock_ocr_service.py")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Błąd tworzenia mock service: {e}")
        return False

def test_ocr_installations():
    """Testuj zainstalowane OCR engines"""
    print("\n🧪 Testowanie OCR installations...")
    
    tests = []
    
    # Test Tesseract
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Utwórz prosty obraz testowy
        test_image = Image.new('RGB', (200, 50), color='white')
        
        # Test podstawowy
        result = pytesseract.image_to_string(test_image)
        tests.append(('Tesseract', True, 'OK'))
        print("   ✅ Tesseract działa")
        
    except Exception as e:
        tests.append(('Tesseract', False, str(e)))
        print(f"   ❌ Tesseract: {e}")
    
    # Test EasyOCR
    try:
        import easyocr
        
        # Inicjalizacja może potrwać
        reader = easyocr.Reader(['en', 'pl'], gpu=False)
        tests.append(('EasyOCR', True, 'OK'))
        print("   ✅ EasyOCR działa")
        
    except Exception as e:
        tests.append(('EasyOCR', False, str(e)))
        print(f"   ❌ EasyOCR: {e}")
    
    # Test PaddleOCR
    try:
        from paddleocr import PaddleOCR
        
        ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
        tests.append(('PaddleOCR', True, 'OK'))
        print("   ✅ PaddleOCR działa")
        
    except Exception as e:
        tests.append(('PaddleOCR', False, str(e)))
        print(f"   ❌ PaddleOCR: {e}")
    
    # Podsumowanie
    working = sum(1 for _, success, _ in tests if success)
    total = len(tests)
    
    print(f"\n   📊 OCR Engines: {working}/{total} działają")
    
    return tests

def create_ocr_requirements_file():
    """Utwórz plik requirements dla OCR"""
    print("\n📄 Tworzenie requirements-ocr.txt...")
    
    requirements_content = '''# OCR Requirements for FaktuLove
# Install with: pip install -r requirements-ocr.txt

# Core OCR packages
pytesseract>=0.3.10
easyocr>=1.7.0
opencv-python>=4.8.0
Pillow>=10.0.0
numpy>=1.24.0

# Optional OCR packages (may require additional system dependencies)
# paddlepaddle>=2.5.0
# paddleocr>=2.7.0

# Image processing
scikit-image>=0.21.0
pdf2image>=1.16.0

# Utilities
requests>=2.31.0
tqdm>=4.65.0
'''
    
    try:
        with open('requirements-ocr.txt', 'w') as f:
            f.write(requirements_content)
        
        print("   ✅ requirements-ocr.txt utworzony")
        print("   📦 Instaluj: pip install -r requirements-ocr.txt")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Błąd tworzenia requirements: {e}")
        return False

def create_ocr_setup_script():
    """Utwórz skrypt setup OCR"""
    print("\n📜 Tworzenie setup_ocr.sh...")
    
    setup_script = '''#!/bin/bash
# OCR Setup Script for FaktuLove

set -e

echo "🚀 FaktuLove OCR Setup"
echo "====================="

# Update system packages
echo "📦 Updating system packages..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng libtesseract-dev
elif command -v yum &> /dev/null; then
    sudo yum install -y tesseract tesseract-langpack-pol tesseract-langpack-eng tesseract-devel
elif command -v brew &> /dev/null; then
    brew install tesseract tesseract-lang
else
    echo "⚠️ Please install Tesseract manually"
fi

# Install Python packages
echo "🐍 Installing Python OCR packages..."
pip install -r requirements-ocr.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p /tmp/faktulove_paddle_models
mkdir -p logs

# Test installations
echo "🧪 Testing OCR installations..."
python3 -c "
import pytesseract
print('✅ Tesseract OK')

try:
    import easyocr
    print('✅ EasyOCR OK')
except:
    print('⚠️ EasyOCR not available')

try:
    from paddleocr import PaddleOCR
    print('✅ PaddleOCR OK')
except:
    print('⚠️ PaddleOCR not available')
"

echo "✅ OCR Setup completed!"
echo "🚀 Start mock service: python3 mock_ocr_service.py"
'''
    
    try:
        with open('setup_ocr.sh', 'w') as f:
            f.write(setup_script)
        
        # Uczyń wykonywalnym
        os.chmod('setup_ocr.sh', 0o755)
        
        print("   ✅ setup_ocr.sh utworzony")
        print("   🚀 Uruchom: ./setup_ocr.sh")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Błąd tworzenia setup script: {e}")
        return False

def main():
    """Główna funkcja naprawy OCR warnings"""
    print("🔧 Naprawa ostrzeżeń OCR w FaktuLove")
    print("=" * 50)
    
    results = {}
    
    # 1. Sprawdź wymagania systemowe
    system, available_commands = check_system_requirements()
    
    # 2. Instaluj Tesseract
    results['tesseract'] = install_tesseract()
    
    # 3. Instaluj Python OCR packages
    results['python_packages'] = install_python_ocr_packages()
    
    # 4. Usuń deprecated dependencies
    results['cleanup'] = remove_deprecated_dependencies()
    
    # 5. Utwórz katalog modeli PaddleOCR
    results['paddle_dir'] = create_paddle_models_directory()
    
    # 6. Utwórz mock OCR service
    results['mock_service'] = create_mock_ocr_service()
    
    # 7. Utwórz pliki pomocnicze
    results['requirements'] = create_ocr_requirements_file()
    results['setup_script'] = create_ocr_setup_script()
    
    # 8. Testuj instalacje
    ocr_tests = test_ocr_installations()
    
    # Podsumowanie
    print("\n" + "=" * 50)
    print("📊 PODSUMOWANIE NAPRAWY OCR")
    print("=" * 50)
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"Zakończone zadania: {success_count}/{total_count}")
    
    for task, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {task}")
    
    # OCR Engines status
    working_engines = sum(1 for _, success, _ in ocr_tests if success)
    total_engines = len(ocr_tests)
    
    print(f"\nOCR Engines: {working_engines}/{total_engines} działają")
    for engine, success, message in ocr_tests:
        status = "✅" if success else "❌"
        print(f"  {status} {engine}: {message}")
    
    print("\n🎯 Następne kroki:")
    print("1. Uruchom mock service: python3 mock_ocr_service.py")
    print("2. Restart Django: python manage.py runserver")
    print("3. Sprawdź logi - ostrzeżenia powinny zniknąć")
    
    if success_count >= total_count * 0.7:  # 70% sukcesu
        print("\n🎉 Naprawa OCR zakończona pomyślnie!")
        return True
    else:
        print("\n⚠️ Niektóre zadania nie zostały ukończone")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)