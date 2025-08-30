#!/usr/bin/env python3
"""
Diagnostyka problemów z OCR i przyciskami w FaktuLove
Sprawdza URLs, templates, views i JavaScript
"""

import os
import sys
import requests
from pathlib import Path

def check_urls_configuration():
    """Sprawdź konfigurację URLs"""
    print("🔍 Sprawdzanie konfiguracji URLs...")
    
    try:
        # Sprawdź główny urls.py
        urls_files = [
            'faktulove/urls.py',
            'faktury_projekt/urls.py', 
            'faktury/urls.py'
        ]
        
        for url_file in urls_files:
            if os.path.exists(url_file):
                print(f"✅ Znaleziono: {url_file}")
                with open(url_file, 'r') as f:
                    content = f.read()
                    
                # Szukaj wzorców OCR
                if 'ocr' in content.lower():
                    print(f"   📋 OCR patterns w {url_file}:")
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'ocr' in line.lower():
                            print(f"      L{i}: {line.strip()}")
                            
                # Szukaj include patterns
                if 'include' in content:
                    print(f"   🔗 Include patterns w {url_file}:")
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'include' in line and not line.strip().startswith('#'):
                            print(f"      L{i}: {line.strip()}")
            else:
                print(f"❌ Nie znaleziono: {url_file}")
                
    except Exception as e:
        print(f"💥 Błąd sprawdzania URLs: {e}")

def check_views_configuration():
    """Sprawdź konfigurację views"""
    print("\n🔍 Sprawdzanie views...")
    
    try:
        views_files = [
            'faktury/views.py',
            'faktury/views_modules/ocr_views.py'
        ]
        
        for view_file in views_files:
            if os.path.exists(view_file):
                print(f"✅ Znaleziono: {view_file}")
                with open(view_file, 'r') as f:
                    content = f.read()
                    
                # Szukaj funkcji OCR
                if 'ocr' in content.lower():
                    print(f"   📋 OCR functions w {view_file}:")
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if ('def ' in line and 'ocr' in line.lower()) or ('class ' in line and 'ocr' in line.lower()):
                            print(f"      L{i}: {line.strip()}")
                            
                # Szukaj upload functions
                if 'upload' in content.lower():
                    print(f"   📤 Upload functions w {view_file}:")
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if ('def ' in line and 'upload' in line.lower()) or ('class ' in line and 'upload' in line.lower()):
                            print(f"      L{i}: {line.strip()}")
            else:
                print(f"❌ Nie znaleziono: {view_file}")
                
    except Exception as e:
        print(f"💥 Błąd sprawdzania views: {e}")

def check_templates():
    """Sprawdź templates"""
    print("\n🔍 Sprawdzanie templates...")
    
    try:
        # Znajdź wszystkie template directories
        template_dirs = []
        for root, dirs, files in os.walk('.'):
            if 'templates' in root:
                template_dirs.append(root)
                
        print(f"📁 Znalezione katalogi templates: {len(template_dirs)}")
        for template_dir in template_dirs[:5]:  # Pokaż pierwsze 5
            print(f"   {template_dir}")
            
        # Szukaj głównych templates
        main_templates = [
            'templates/base.html',
            'templates/faktury/base.html',
            'faktury/templates/base.html',
            'faktury/templates/faktury/base.html'
        ]
        
        for template in main_templates:
            if os.path.exists(template):
                print(f"✅ Główny template: {template}")
                with open(template, 'r') as f:
                    content = f.read()
                    
                # Szukaj navigation
                if 'nav' in content.lower() or 'menu' in content.lower():
                    print(f"   🧭 Navigation znaleziona w {template}")
                    
                # Szukaj OCR links
                if 'ocr' in content.lower():
                    print(f"   🔗 OCR links w {template}")
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'ocr' in line.lower() and ('href' in line or 'url' in line):
                            print(f"      L{i}: {line.strip()}")
                            
        # Szukaj OCR templates
        ocr_templates = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.html') and 'ocr' in file.lower():
                    ocr_templates.append(os.path.join(root, file))
                    
        print(f"\n📋 OCR Templates znalezione: {len(ocr_templates)}")
        for template in ocr_templates[:10]:  # Pokaż pierwsze 10
            print(f"   {template}")
            
    except Exception as e:
        print(f"💥 Błąd sprawdzania templates: {e}")

def check_static_files():
    """Sprawdź pliki statyczne"""
    print("\n🔍 Sprawdzanie plików statycznych...")
    
    try:
        # Szukaj JavaScript files
        js_files = []
        css_files = []
        
        for root, dirs, files in os.walk('.'):
            if 'static' in root:
                for file in files:
                    if file.endswith('.js'):
                        js_files.append(os.path.join(root, file))
                    elif file.endswith('.css'):
                        css_files.append(os.path.join(root, file))
                        
        print(f"📄 JavaScript files: {len(js_files)}")
        print(f"🎨 CSS files: {len(css_files)}")
        
        # Sprawdź główne JS files
        main_js_files = [f for f in js_files if any(name in f.lower() for name in ['main', 'app', 'faktury', 'ocr'])]
        
        print(f"\n📋 Główne JS files:")
        for js_file in main_js_files[:5]:
            print(f"   {js_file}")
            
            # Sprawdź zawartość
            try:
                with open(js_file, 'r') as f:
                    content = f.read()
                    if 'ocr' in content.lower() or 'upload' in content.lower():
                        print(f"      🔗 Zawiera OCR/upload functionality")
            except:
                pass
                
    except Exception as e:
        print(f"💥 Błąd sprawdzania static files: {e}")

def test_endpoints():
    """Testuj dostępność endpointów"""
    print("\n🔍 Testowanie endpointów...")
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        ('/', 'Homepage'),
        ('/ocr/', 'OCR Root'),
        ('/ocr/upload/', 'OCR Upload'),
        ('/faktury/', 'Faktury Root'),
        ('/faktury/add/', 'Add Faktura'),
        ('/faktury/create/', 'Create Faktura'),
        ('/admin/', 'Admin Panel')
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5, allow_redirects=False)
            status = response.status_code
            
            if status == 200:
                print(f"✅ {name} ({endpoint}): OK")
            elif status == 302:
                location = response.headers.get('Location', 'unknown')
                print(f"🔄 {name} ({endpoint}): Redirect to {location}")
            elif status == 404:
                print(f"❌ {name} ({endpoint}): Not Found")
            else:
                print(f"⚠️ {name} ({endpoint}): Status {status}")
                
        except Exception as e:
            print(f"💥 {name} ({endpoint}): Error - {e}")

def check_database_models():
    """Sprawdź modele bazy danych"""
    print("\n🔍 Sprawdzanie modeli...")
    
    try:
        # Sprawdź models.py
        models_files = [
            'faktury/models.py'
        ]
        
        for model_file in models_files:
            if os.path.exists(model_file):
                print(f"✅ Znaleziono: {model_file}")
                with open(model_file, 'r') as f:
                    content = f.read()
                    
                # Szukaj modeli
                lines = content.split('\n')
                models = []
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith('class ') and 'Model' in line:
                        model_name = line.split('class ')[1].split('(')[0].strip()
                        models.append(model_name)
                        
                print(f"   📋 Modele znalezione: {', '.join(models)}")
                
                # Sprawdź czy są OCR-related modele
                ocr_models = [m for m in models if 'ocr' in m.lower() or 'upload' in m.lower() or 'document' in m.lower()]
                if ocr_models:
                    print(f"   🔗 OCR-related modele: {', '.join(ocr_models)}")
                    
    except Exception as e:
        print(f"💥 Błąd sprawdzania modeli: {e}")

def main():
    """Główna funkcja diagnostyczna"""
    print("🚀 Diagnostyka problemów OCR i przycisków FaktuLove")
    print("=" * 60)
    
    check_urls_configuration()
    check_views_configuration()
    check_templates()
    check_static_files()
    test_endpoints()
    check_database_models()
    
    print("\n" + "=" * 60)
    print("📊 PODSUMOWANIE DIAGNOSTYKI")
    print("=" * 60)
    print("Sprawdź wyniki powyżej aby zidentyfikować problemy:")
    print("1. ❌ Brakujące URL patterns dla OCR")
    print("2. ❌ Brakujące views dla OCR upload")
    print("3. ❌ Problemy z navigation w templates")
    print("4. ❌ Brakujące JavaScript dla przycisków")
    print("5. ❌ Problemy z routing")
    
    print("\n🔧 Następne kroki:")
    print("1. Napraw URL configuration")
    print("2. Dodaj brakujące views")
    print("3. Popraw navigation templates")
    print("4. Dodaj JavaScript functionality")

if __name__ == '__main__':
    main()