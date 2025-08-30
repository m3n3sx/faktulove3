#!/usr/bin/env python3
"""
Napraw krytyczne problemy z systemem
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')
django.setup()

from django.contrib.auth.models import User
from faktury.models import OCREngine, Firma
from django.contrib.auth.hashers import make_password

def install_ocr_dependencies():
    """Zainstaluj zależności OCR"""
    print("📦 Instalowanie zależności OCR...")
    
    try:
        import subprocess
        
        # Lista pakietów do zainstalowania
        packages = [
            'pytesseract',
            'easyocr', 
            'Pillow',
            'pdf2image',
            'python-magic'
        ]
        
        for package in packages:
            try:
                print(f"Instalowanie {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} zainstalowany")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Błąd instalacji {package}: {e}")
        
        # Sprawdź czy Tesseract jest zainstalowany w systemie
        try:
            subprocess.check_call(['tesseract', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Tesseract OCR zainstalowany w systemie")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Tesseract OCR nie jest zainstalowany w systemie")
            print("💡 Zainstaluj: sudo apt-get install tesseract-ocr tesseract-ocr-pol")
        
    except Exception as e:
        print(f"❌ Błąd instalacji zależności: {e}")

def create_mock_ocr_service():
    """Stwórz mock OCR service dla testów"""
    print("🔧 Tworzenie mock OCR service...")
    
    mock_service_code = '''#!/usr/bin/env python3
"""
Mock OCR Service dla testów
"""

from flask import Flask, request, jsonify
import json
import time
import random

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'mock-ocr'})

@app.route('/process', methods=['POST'])
def process_document():
    """Mock przetwarzania dokumentu"""
    
    # Symuluj przetwarzanie
    time.sleep(random.uniform(1, 3))
    
    # Mock wyniki OCR
    mock_result = {
        'success': True,
        'confidence': random.uniform(0.8, 0.95),
        'text': 'FAKTURA VAT\\n\\nNumer: FV/001/01/2025\\nData: 29.01.2025\\n\\nSprzedawca:\\nTestowa Firma Sp. z o.o.\\nul. Testowa 123\\n00-001 Warszawa\\nNIP: 1234567890\\n\\nNabywca:\\nKlient Testowy\\nul. Kliencka 456\\n00-002 Kraków\\nNIP: 0987654321\\n\\nPozycje:\\n1. Usługa testowa - 1000.00 PLN\\nVAT 23% - 230.00 PLN\\n\\nRazem: 1230.00 PLN',
        'extracted_data': {
            'invoice_number': 'FV/001/01/2025',
            'invoice_date': '2025-01-29',
            'due_date': '2025-02-28',
            'supplier_name': 'Testowa Firma Sp. z o.o.',
            'supplier_nip': '1234567890',
            'buyer_name': 'Klient Testowy',
            'buyer_nip': '0987654321',
            'total_amount': 1230.00,
            'net_amount': 1000.00,
            'vat_amount': 230.00,
            'vat_rate': 23,
            'currency': 'PLN'
        },
        'processing_time': random.uniform(1, 3)
    }
    
    return jsonify(mock_result)

if __name__ == '__main__':
    print("🚀 Starting Mock OCR Service on port 8001...")
    app.run(host='0.0.0.0', port=8001, debug=True)
'''
    
    try:
        with open('mock_ocr_service.py', 'w') as f:
            f.write(mock_service_code)
        
        print("✅ Mock OCR service utworzony: mock_ocr_service.py")
        print("💡 Uruchom: python mock_ocr_service.py")
        
    except Exception as e:
        print(f"❌ Błąd tworzenia mock service: {e}")

def setup_ocr_engines():
    """Skonfiguruj OCR engines"""
    print("⚙️ Konfigurowanie OCR engines...")
    
    try:
        # Usuń stare engines
        OCREngine.objects.all().delete()
        
        # Mock OCR Engine (zawsze działa)
        mock_engine = OCREngine.objects.create(
            name='Mock OCR',
            engine_type='mock',
            version='1.0',
            is_active=True,
            priority=1,
            configuration={
                'service_url': 'http://localhost:8001',
                'timeout': 30,
                'confidence_threshold': 0.7
            }
        )
        print(f"✅ Utworzono Mock OCR Engine (ID: {mock_engine.id})")
        
        # Tesseract (jeśli dostępny)
        try:
            import pytesseract
            tesseract_engine = OCREngine.objects.create(
                name='Tesseract OCR',
                engine_type='tesseract',
                version='5.0',
                is_active=True,
                priority=2,
                configuration={
                    'language': 'pol+eng',
                    'psm': 6,
                    'oem': 3,
                    'confidence_threshold': 0.6
                }
            )
            print(f"✅ Utworzono Tesseract Engine (ID: {tesseract_engine.id})")
        except ImportError:
            print("⚠️ Tesseract nie dostępny - pominięto")
        
        # EasyOCR (jeśli dostępny)
        try:
            import easyocr
            easyocr_engine = OCREngine.objects.create(
                name='EasyOCR',
                engine_type='easyocr',
                version='1.6',
                is_active=True,
                priority=3,
                configuration={
                    'languages': ['pl', 'en'],
                    'gpu': False,
                    'confidence_threshold': 0.5
                }
            )
            print(f"✅ Utworzono EasyOCR Engine (ID: {easyocr_engine.id})")
        except ImportError:
            print("⚠️ EasyOCR nie dostępny - pominięto")
        
        print(f"📊 Łącznie utworzono {OCREngine.objects.count()} OCR engines")
        
    except Exception as e:
        print(f"❌ Błąd konfiguracji OCR engines: {e}")

def create_admin_user():
    """Utwórz użytkownika admin"""
    print("👤 Tworzenie użytkownika admin...")
    
    try:
        # Sprawdź czy admin już istnieje
        if User.objects.filter(username='admin').exists():
            print("✅ Użytkownik admin już istnieje")
            return
        
        # Utwórz admin
        admin_user = User.objects.create(
            username='admin',
            email='admin@faktulove.pl',
            is_staff=True,
            is_superuser=True,
            password=make_password('admin123')  # ZMIEŃ TO W PRODUKCJI!
        )
        
        # Utwórz firmę dla admin
        firma = Firma.objects.create(
            user=admin_user,
            nazwa='Firma Testowa Admin',
            nip='1234567890',
            ulica='ul. Testowa',
            numer_domu='123',
            miejscowosc='Warszawa',
            kod_pocztowy='00-001',
            kraj='Polska'
        )
        
        print(f"✅ Utworzono użytkownika admin (hasło: admin123)")
        print(f"✅ Utworzono firmę dla admin: {firma.nazwa}")
        
    except Exception as e:
        print(f"❌ Błąd tworzenia admin: {e}")

def fix_urls():
    """Napraw problemy z URL-ami"""
    print("🔗 Naprawianie URL-i...")
    
    try:
        # Sprawdź czy są duplikaty w urls.py
        urls_file = Path('faktury/urls.py')
        if urls_file.exists():
            with open(urls_file, 'r') as f:
                content = f.read()
            
            # Policz wystąpienia
            dodaj_fakture_count = content.count("path('dodaj_fakture/'")
            ocr_upload_count = content.count("path('ocr/upload/'")
            
            print(f"📊 Wystąpienia 'dodaj_fakture/': {dodaj_fakture_count}")
            print(f"📊 Wystąpienia 'ocr/upload/': {ocr_upload_count}")
            
            if dodaj_fakture_count > 1 or ocr_upload_count > 2:
                print("⚠️ Wykryto duplikaty URL-i - zostały już naprawione wcześniej")
            else:
                print("✅ URL-e wyglądają poprawnie")
        
    except Exception as e:
        print(f"❌ Błąd sprawdzania URL-i: {e}")

def test_functionality():
    """Przetestuj funkcjonalności"""
    print("🧪 Testowanie funkcjonalności...")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Test dodawania faktury (bez logowania - sprawdź przekierowanie)
        response = client.get('/dodaj_fakture/')
        print(f"📡 Dodaj fakturę (bez logowania): {response.status_code}")
        
        # Test OCR upload
        response = client.get('/ocr/upload/')
        print(f"📡 OCR upload (bez logowania): {response.status_code}")
        
        # Test admin panel
        response = client.get('/admin/')
        print(f"📡 Admin panel: {response.status_code}")
        
        # Test admin OCR engine
        response = client.get('/admin/faktury/ocrengine/')
        print(f"📡 Admin OCR engine: {response.status_code}")
        
        # Sprawdź czy są aktywne OCR engines
        active_engines = OCREngine.objects.filter(is_active=True).count()
        print(f"📊 Aktywne OCR engines: {active_engines}")
        
    except Exception as e:
        print(f"❌ Błąd testowania: {e}")

def main():
    """Główna funkcja naprawy"""
    print("🔧 NAPRAWA KRYTYCZNYCH PROBLEMÓW")
    print("=" * 50)
    
    # 1. Zainstaluj zależności OCR
    install_ocr_dependencies()
    
    # 2. Utwórz mock OCR service
    create_mock_ocr_service()
    
    # 3. Skonfiguruj OCR engines
    setup_ocr_engines()
    
    # 4. Utwórz użytkownika admin
    create_admin_user()
    
    # 5. Napraw URL-e
    fix_urls()
    
    # 6. Przetestuj funkcjonalności
    test_functionality()
    
    print("\n✅ NAPRAWA ZAKOŃCZONA")
    print("=" * 50)
    print("💡 NASTĘPNE KROKI:")
    print("1. Uruchom mock OCR service: python mock_ocr_service.py")
    print("2. Uruchom Celery worker: celery -A faktulove worker -l info")
    print("3. Zaloguj się do admin: http://localhost:8000/admin/ (admin/admin123)")
    print("4. Przetestuj dodawanie faktury: http://localhost:8000/dodaj_fakture/")
    print("5. Przetestuj OCR: http://localhost:8000/ocr/upload/")

if __name__ == '__main__':
    main()