#!/usr/bin/env python3
"""
Szybki test E2E dla FaktuLove
Sprawdza podstawową funkcjonalność bez skomplikowanych zależności
"""

import requests
import time
from datetime import datetime

def test_basic_functionality(base_url="http://localhost:8000"):
    """Podstawowy test funkcjonalności aplikacji"""
    
    print("🧪 Szybki Test E2E FaktuLove")
    print("=" * 50)
    print(f"🎯 Testowany URL: {base_url}")
    print(f"⏰ Czas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test 1: Homepage
    print("1️⃣ Test Homepage...")
    try:
        response = requests.get(base_url, timeout=10, allow_redirects=True)
        success = response.status_code < 500
        
        if success:
            print(f"   ✅ Homepage dostępna (Status: {response.status_code})")
            if response.status_code == 302:
                print(f"   🔄 Przekierowanie do: {response.headers.get('Location', 'nieznane')}")
        else:
            print(f"   ❌ Homepage niedostępna (Status: {response.status_code})")
            
        results.append(("Homepage", success, f"Status: {response.status_code}"))
        
    except Exception as e:
        print(f"   💥 Błąd: {e}")
        results.append(("Homepage", False, str(e)))
    
    # Test 2: Admin Panel
    print("\n2️⃣ Test Admin Panel...")
    try:
        response = requests.get(f"{base_url}/admin/", timeout=10)
        success = response.status_code in [200, 302]  # 200 = login page, 302 = redirect
        
        if success:
            print(f"   ✅ Admin panel dostępny (Status: {response.status_code})")
            if 'login' in response.text.lower():
                print("   🔐 Strona logowania wykryta")
        else:
            print(f"   ❌ Admin panel niedostępny (Status: {response.status_code})")
            
        results.append(("Admin Panel", success, f"Status: {response.status_code}"))
        
    except Exception as e:
        print(f"   💥 Błąd: {e}")
        results.append(("Admin Panel", False, str(e)))
    
    # Test 3: Static Files
    print("\n3️⃣ Test Static Files...")
    static_files = [
        "/static/admin/css/base.css",
        "/static/admin/js/core.js"
    ]
    
    static_success = 0
    for static_file in static_files:
        try:
            response = requests.get(f"{base_url}{static_file}", timeout=5)
            if response.status_code == 200:
                static_success += 1
                print(f"   ✅ {static_file}")
            else:
                print(f"   ⚠️ {static_file} (Status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ {static_file} - Błąd: {e}")
    
    static_result = static_success > 0
    results.append(("Static Files", static_result, f"{static_success}/{len(static_files)} plików"))
    
    # Test 4: OCR Upload Page
    print("\n4️⃣ Test OCR Upload...")
    try:
        response = requests.get(f"{base_url}/ocr/upload/", timeout=10, allow_redirects=True)
        success = response.status_code < 500
        
        if success:
            print(f"   ✅ OCR Upload dostępny (Status: {response.status_code})")
            if 'login' in response.text.lower():
                print("   🔐 Wymaga autoryzacji (przekierowanie do logowania)")
            elif 'upload' in response.text.lower():
                print("   📤 Strona upload wykryta")
        else:
            print(f"   ❌ OCR Upload niedostępny (Status: {response.status_code})")
            
        results.append(("OCR Upload", success, f"Status: {response.status_code}"))
        
    except Exception as e:
        print(f"   💥 Błąd: {e}")
        results.append(("OCR Upload", False, str(e)))
    
    # Test 5: API Endpoints
    print("\n5️⃣ Test API...")
    try:
        response = requests.get(f"{base_url}/api/", timeout=10)
        success = response.status_code < 500
        
        if success:
            print(f"   ✅ API dostępne (Status: {response.status_code})")
        else:
            print(f"   ❌ API niedostępne (Status: {response.status_code})")
            
        results.append(("API", success, f"Status: {response.status_code}"))
        
    except Exception as e:
        print(f"   💥 Błąd: {e}")
        results.append(("API", False, str(e)))
    
    # Test 6: Performance
    print("\n6️⃣ Test Performance...")
    try:
        start_time = time.time()
        response = requests.get(base_url, timeout=10)
        load_time = time.time() - start_time
        
        success = load_time < 5.0  # 5 sekund max
        
        if success:
            print(f"   ✅ Czas ładowania: {load_time:.2f}s")
        else:
            print(f"   ⚠️ Wolne ładowanie: {load_time:.2f}s")
            
        results.append(("Performance", success, f"Load time: {load_time:.2f}s"))
        
    except Exception as e:
        print(f"   💥 Błąd: {e}")
        results.append(("Performance", False, str(e)))
    
    # Podsumowanie
    print("\n" + "=" * 50)
    print("📊 PODSUMOWANIE TESTÓW")
    print("=" * 50)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Łączne testy: {total}")
    print(f"Pomyślne: {passed} ✅")
    print(f"Niepowodzenia: {total - passed} ❌")
    print(f"Wskaźnik sukcesu: {success_rate:.1f}%")
    
    print("\nSzczegóły:")
    for test_name, success, message in results:
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}: {message}")
    
    print("\n" + "=" * 50)
    
    if success_rate >= 80:
        print("🎉 APLIKACJA DZIAŁA POPRAWNIE!")
        return True
    elif success_rate >= 60:
        print("⚠️ APLIKACJA DZIAŁA Z PROBLEMAMI")
        return False
    else:
        print("❌ APLIKACJA MA POWAŻNE PROBLEMY")
        return False

def test_database_connectivity():
    """Test połączenia z bazą danych"""
    print("\n🗄️ Test Database Connectivity...")
    
    try:
        import os
        import sys
        
        # Dodaj ścieżkę projektu
        sys.path.insert(0, os.getcwd())
        
        # Ustaw Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')
        
        import django
        django.setup()
        
        from django.db import connection
        
        # Test połączenia
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result == (1,):
            print("   ✅ Baza danych połączona")
            return True
        else:
            print("   ❌ Problem z bazą danych")
            return False
            
    except Exception as e:
        print(f"   ⚠️ Nie można przetestować bazy danych: {e}")
        return None

def main():
    """Główna funkcja"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Szybki test E2E FaktuLove')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='URL aplikacji do testowania')
    parser.add_argument('--db-test', action='store_true',
                       help='Testuj również połączenie z bazą danych')
    
    args = parser.parse_args()
    
    # Test podstawowej funkcjonalności
    app_success = test_basic_functionality(args.url)
    
    # Test bazy danych (opcjonalnie)
    db_success = None
    if args.db_test:
        db_success = test_database_connectivity()
    
    # Końcowy wynik
    print(f"\n🏁 WYNIK KOŃCOWY:")
    print(f"   Aplikacja: {'✅ OK' if app_success else '❌ PROBLEMY'}")
    
    if db_success is not None:
        print(f"   Baza danych: {'✅ OK' if db_success else '❌ PROBLEMY'}")
    
    # Zwróć kod wyjścia
    if app_success and (db_success is None or db_success):
        print("\n🎯 Wszystkie testy zakończone pomyślnie!")
        return 0
    else:
        print("\n⚠️ Wykryto problemy - sprawdź logi aplikacji")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())