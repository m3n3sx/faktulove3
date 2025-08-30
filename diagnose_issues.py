#!/usr/bin/env python3
"""
Diagnoza problemów z systemem FaktuLove
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')
django.setup()

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from django.core.management import call_command
from faktury.models import Firma, OCREngine, DocumentUpload, OCRResult

def check_invoice_creation():
    """Sprawdź funkcjonalność dodawania faktury"""
    print("\n🧾 Sprawdzanie dodawania faktury...")
    
    try:
        # Sprawdź czy URL istnieje
        url = reverse('dodaj_fakture')
        print(f"✅ URL dodaj_fakture: {url}")
        
        # Sprawdź czy view istnieje
        from faktury.views import dodaj_fakture_sprzedaz
        print("✅ View dodaj_fakture_sprzedaz istnieje")
        
        # Sprawdź czy template istnieje
        template_path = Path('faktury/templates/faktury/dodaj_fakture.html')
        if template_path.exists():
            print("✅ Template dodaj_fakture.html istnieje")
        else:
            print("❌ Template dodaj_fakture.html nie istnieje")
        
        # Sprawdź czy są użytkownicy z firmami
        users_with_firms = User.objects.filter(firma__isnull=False).count()
        print(f"📊 Użytkownicy z firmami: {users_with_firms}")
        
        if users_with_firms == 0:
            print("⚠️ Brak użytkowników z firmami - może powodować problemy")
        
    except Exception as e:
        print(f"❌ Błąd sprawdzania faktury: {e}")

def check_admin_panel():
    """Sprawdź panel administracyjny"""
    print("\n🔧 Sprawdzanie panelu administracyjnego...")
    
    try:
        # Sprawdź URL admin
        from django.contrib import admin
        print("✅ Django admin załadowany")
        
        # Sprawdź czy OCREngine jest zarejestrowany
        from faktury.admin import OCREngineAdmin
        print("✅ OCREngineAdmin zarejestrowany")
        
        # Sprawdź czy model OCREngine istnieje
        ocr_engines = OCREngine.objects.count()
        print(f"📊 OCR Engines w bazie: {ocr_engines}")
        
        if ocr_engines == 0:
            print("⚠️ Brak OCR engines - dodaję domyślne...")
            # Dodaj domyślny OCR engine
            OCREngine.objects.get_or_create(
                name='Tesseract',
                defaults={
                    'engine_type': 'tesseract',
                    'version': '5.0',
                    'is_active': True,
                    'priority': 1,
                    'configuration': {
                        'language': 'pol+eng',
                        'psm': 6,
                        'oem': 3
                    }
                }
            )
            print("✅ Dodano domyślny OCR engine")
        
        # Sprawdź dostęp do admin URLs
        client = Client()
        response = client.get('/admin/')
        print(f"📡 Admin panel response: {response.status_code}")
        
        # Sprawdź konkretny URL OCREngine
        try:
            response = client.get('/admin/faktury/ocrengine/')
            print(f"📡 OCREngine admin response: {response.status_code}")
        except Exception as e:
            print(f"❌ Błąd dostępu do OCREngine admin: {e}")
        
    except Exception as e:
        print(f"❌ Błąd sprawdzania admin: {e}")

def check_ocr_functionality():
    """Sprawdź funkcjonalność OCR"""
    print("\n📤 Sprawdzanie funkcjonalności OCR...")
    
    try:
        # Sprawdź URL OCR
        url = reverse('ocr_upload')
        print(f"✅ URL ocr_upload: {url}")
        
        # Sprawdź czy view istnieje
        from faktury.views_modules.ocr_views import ocr_upload_view
        print("✅ View ocr_upload_view istnieje")
        
        # Sprawdź template OCR
        template_path = Path('faktury/templates/faktury/ocr/upload.html')
        if template_path.exists():
            print("✅ Template ocr/upload.html istnieje")
        else:
            print("❌ Template ocr/upload.html nie istnieje")
        
        # Sprawdź DocumentUpload model
        uploads_count = DocumentUpload.objects.count()
        print(f"📊 Przesłane dokumenty: {uploads_count}")
        
        # Sprawdź OCRResult model
        results_count = OCRResult.objects.count()
        print(f"📊 Wyniki OCR: {results_count}")
        
        # Sprawdź Celery tasks
        try:
            from faktury.tasks import process_document_ocr_task
            print("✅ OCR task process_document_ocr_task istnieje")
        except ImportError as e:
            print(f"❌ Błąd importu OCR task: {e}")
        
        # Sprawdź Redis connection
        try:
            import redis
            from django.conf import settings
            r = redis.from_url(settings.CELERY_BROKER_URL)
            r.ping()
            print("✅ Redis connection OK")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
        
        # Sprawdź OCR engines
        active_engines = OCREngine.objects.filter(is_active=True).count()
        print(f"📊 Aktywne OCR engines: {active_engines}")
        
        if active_engines == 0:
            print("⚠️ Brak aktywnych OCR engines")
        
    except Exception as e:
        print(f"❌ Błąd sprawdzania OCR: {e}")

def check_static_files():
    """Sprawdź pliki statyczne"""
    print("\n📁 Sprawdzanie plików statycznych...")
    
    critical_files = [
        'static/assets/css/remixicon.css',
        'static/assets/js/safe-error-handler.js',
        'static/js/react.production.min.js',
        'static/js/upload-app.bundle.js'
    ]
    
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - BRAK")

def check_database():
    """Sprawdź bazę danych"""
    print("\n🗄️ Sprawdzanie bazy danych...")
    
    try:
        # Sprawdź migracje
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM django_migrations WHERE app = 'faktury'")
        migrations_count = cursor.fetchone()[0]
        print(f"📊 Migracje faktury: {migrations_count}")
        
        # Sprawdź tabele
        tables = connection.introspection.table_names()
        important_tables = [
            'faktury_firma', 'faktury_faktura', 'faktury_kontrahent',
            'faktury_documentupload', 'faktury_ocrresult', 'faktury_ocrengine'
        ]
        
        for table in important_tables:
            if table in tables:
                print(f"✅ Tabela {table}")
            else:
                print(f"❌ Tabela {table} - BRAK")
        
    except Exception as e:
        print(f"❌ Błąd sprawdzania bazy: {e}")

def fix_common_issues():
    """Napraw typowe problemy"""
    print("\n🔧 Naprawianie typowych problemów...")
    
    try:
        # Uruchom migracje
        print("Uruchamianie migracji...")
        call_command('migrate', verbosity=0)
        print("✅ Migracje zakończone")
        
        # Zbierz pliki statyczne
        print("Zbieranie plików statycznych...")
        call_command('collectstatic', interactive=False, verbosity=0)
        print("✅ Pliki statyczne zebrane")
        
        # Sprawdź i dodaj domyślne OCR engines
        if OCREngine.objects.count() == 0:
            print("Dodawanie domyślnych OCR engines...")
            
            # Tesseract
            OCREngine.objects.create(
                name='Tesseract',
                engine_type='tesseract',
                version='5.0',
                is_active=True,
                priority=1,
                configuration={
                    'language': 'pol+eng',
                    'psm': 6,
                    'oem': 3
                }
            )
            
            # EasyOCR
            OCREngine.objects.create(
                name='EasyOCR',
                engine_type='easyocr',
                version='1.6',
                is_active=True,
                priority=2,
                configuration={
                    'languages': ['pl', 'en'],
                    'gpu': False
                }
            )
            
            print("✅ Dodano domyślne OCR engines")
        
    except Exception as e:
        print(f"❌ Błąd naprawiania: {e}")

def main():
    """Główna funkcja diagnostyczna"""
    print("🔍 DIAGNOZA PROBLEMÓW FAKTULOVE")
    print("=" * 50)
    
    check_database()
    check_static_files()
    check_invoice_creation()
    check_admin_panel()
    check_ocr_functionality()
    
    print("\n🔧 PRÓBA NAPRAWY PROBLEMÓW")
    print("=" * 50)
    fix_common_issues()
    
    print("\n📋 PODSUMOWANIE")
    print("=" * 50)
    print("Diagnoza zakończona. Sprawdź powyższe wyniki.")
    print("Jeśli nadal są problemy, sprawdź logi Django i Celery.")
    
    # Dodatkowe instrukcje
    print("\n💡 DODATKOWE KROKI:")
    print("1. Uruchom Celery worker: celery -A faktulove worker -l info")
    print("2. Uruchom Redis: redis-server")
    print("3. Sprawdź logi: tail -f logs/django.log")
    print("4. Sprawdź uprawnienia plików w media/")

if __name__ == '__main__':
    main()