#!/usr/bin/env python3
"""
Naprawa problemów z OCR i przyciskami w FaktuLove
Diagnozuje i naprawia problemy z:
1. Zakładką OCR Faktury (wymaga logowania)
2. Przyciskiem "Dodaj" (Bootstrap dropdown)
3. JavaScript dependencies
"""

import os
import sys
import requests
from pathlib import Path

def test_authentication_flow():
    """Test przepływu autoryzacji"""
    print("🔐 Testowanie przepływu autoryzacji...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Homepage bez logowania
    try:
        response = requests.get(base_url, allow_redirects=False)
        print(f"   Homepage (bez logowania): {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"   Przekierowanie do: {location}")
            
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    # Test 2: OCR upload bez logowania
    try:
        response = requests.get(f"{base_url}/ocr/upload/", allow_redirects=False)
        print(f"   OCR Upload (bez logowania): {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"   Przekierowanie do: {location}")
            
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    # Test 3: Login page
    try:
        response = requests.get(f"{base_url}/accounts/login/")
        print(f"   Login page: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Strona logowania dostępna")
            
    except Exception as e:
        print(f"   ❌ Błąd: {e}")

def check_bootstrap_javascript():
    """Sprawdź Bootstrap JavaScript"""
    print("\n🔍 Sprawdzanie Bootstrap JavaScript...")
    
    # Sprawdź czy Bootstrap JS jest w base.html
    base_template = "faktury/templates/base.html"
    if os.path.exists(base_template):
        with open(base_template, 'r') as f:
            content = f.read()
            
        if 'bootstrap.bundle.min.js' in content:
            print("   ✅ Bootstrap JS znaleziony w base.html")
        else:
            print("   ❌ Bootstrap JS nie znaleziony w base.html")
            
        # Sprawdź czy jest jQuery
        if 'jquery' in content.lower():
            print("   ✅ jQuery znaleziony")
        else:
            print("   ❌ jQuery nie znaleziony")
            
        # Sprawdź czy są dropdown handlery
        if 'dropdown' in content.lower():
            print("   ✅ Dropdown handlers znalezione")
        else:
            print("   ⚠️ Brak dropdown handlers")
    else:
        print("   ❌ base.html nie znaleziony")

def check_static_files():
    """Sprawdź pliki statyczne"""
    print("\n📁 Sprawdzanie plików statycznych...")
    
    base_url = "http://localhost:8000"
    
    static_files = [
        "/static/assets/js/lib/bootstrap.bundle.min.js",
        "/static/assets/css/lib/bootstrap.min.css",
        "/static/assets/js/app.js",
        "/static/assets/js/navigation-manager.js"
    ]
    
    for static_file in static_files:
        try:
            response = requests.get(f"{base_url}{static_file}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {static_file}")
            else:
                print(f"   ❌ {static_file} (Status: {response.status_code})")
        except Exception as e:
            print(f"   💥 {static_file} - Błąd: {e}")

def create_test_user_script():
    """Stwórz skrypt do tworzenia użytkownika testowego"""
    print("\n👤 Tworzenie skryptu użytkownika testowego...")
    
    script_content = '''#!/usr/bin/env python3
"""
Skrypt do tworzenia użytkownika testowego dla FaktuLove
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')
django.setup()

from django.contrib.auth.models import User
from faktury.models import Firma

def create_test_user():
    """Utwórz użytkownika testowego"""
    
    # Sprawdź czy użytkownik już istnieje
    username = 'testuser'
    email = 'test@faktulove.pl'
    password = 'testpass123'
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ Użytkownik {username} już istnieje")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
        print(f"✅ Utworzono użytkownika: {username}")
        print(f"   Email: {email}")
        print(f"   Hasło: {password}")
    
    # Sprawdź czy ma firmę
    try:
        firma = Firma.objects.get(user=user)
        print(f"✅ Firma już istnieje: {firma.nazwa}")
    except Firma.DoesNotExist:
        firma = Firma.objects.create(
            user=user,
            nazwa="Test Company Sp. z o.o.",
            adres="ul. Testowa 123",
            kod_pocztowy="00-001",
            miasto="Warszawa",
            nip="1234567890",
            regon="123456789",
            email="firma@test.pl",
            telefon="+48 123 456 789"
        )
        print(f"✅ Utworzono firmę: {firma.nazwa}")
    
    return user, firma

if __name__ == '__main__':
    user, firma = create_test_user()
    print("\\n🎯 Dane do logowania:")
    print(f"Username: {user.username}")
    print(f"Password: testpass123")
    print(f"URL: http://localhost:8000/accounts/login/")
'''
    
    with open('create_test_user.py', 'w') as f:
        f.write(script_content)
    
    print("   ✅ Utworzono create_test_user.py")

def create_bootstrap_fix():
    """Stwórz fix dla Bootstrap dropdown"""
    print("\n🔧 Tworzenie fix dla Bootstrap dropdown...")
    
    js_fix = '''
// Bootstrap Dropdown Fix for FaktuLove
// Ensures dropdown functionality works properly

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Bootstrap Dropdown Fix loading...');
    
    // Wait for Bootstrap to be available
    function initializeDropdowns() {
        if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
            console.log('✅ Bootstrap available, initializing dropdowns');
            
            // Initialize all dropdowns
            const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
            dropdownElements.forEach(function(element) {
                try {
                    new bootstrap.Dropdown(element);
                    console.log('✅ Dropdown initialized:', element);
                } catch (error) {
                    console.error('❌ Dropdown initialization failed:', error);
                }
            });
            
            // Add click handlers for dropdown items
            const dropdownItems = document.querySelectorAll('.dropdown-item');
            dropdownItems.forEach(function(item) {
                item.addEventListener('click', function(e) {
                    const href = this.getAttribute('href');
                    if (href && href !== '' && href !== '#') {
                        console.log('🔗 Navigating to:', href);
                        window.location.href = href;
                    }
                });
            });
            
        } else {
            console.warn('⚠️ Bootstrap not available, retrying in 1 second...');
            setTimeout(initializeDropdowns, 1000);
        }
    }
    
    // Start initialization
    initializeDropdowns();
    
    // Fallback: Manual dropdown handling
    setTimeout(function() {
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
        dropdownToggles.forEach(function(toggle) {
            if (!toggle.hasAttribute('data-dropdown-initialized')) {
                toggle.setAttribute('data-dropdown-initialized', 'true');
                
                toggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const dropdown = this.nextElementSibling;
                    if (dropdown && dropdown.classList.contains('dropdown-menu')) {
                        // Toggle dropdown visibility
                        const isVisible = dropdown.style.display === 'block';
                        
                        // Hide all other dropdowns
                        document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
                            menu.style.display = 'none';
                        });
                        
                        // Toggle current dropdown
                        dropdown.style.display = isVisible ? 'none' : 'block';
                        
                        console.log('🔽 Manual dropdown toggled');
                    }
                });
            }
        });
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
                    menu.style.display = 'none';
                });
            }
        });
        
    }, 2000);
});

// OCR Navigation Fix
function navigateToOCR() {
    console.log('🔗 Navigating to OCR Upload...');
    window.location.href = '/ocr/upload/';
}

// Add OCR navigation to window for global access
window.navigateToOCR = navigateToOCR;

console.log('🎯 Bootstrap Dropdown Fix loaded');
'''
    
    # Zapisz fix do pliku statycznego
    static_js_dir = "faktury/static/assets/js"
    if not os.path.exists(static_js_dir):
        os.makedirs(static_js_dir, exist_ok=True)
    
    with open(f"{static_js_dir}/bootstrap-dropdown-fix.js", 'w') as f:
        f.write(js_fix)
    
    print("   ✅ Utworzono bootstrap-dropdown-fix.js")

def create_ocr_navigation_test():
    """Stwórz test nawigacji OCR"""
    print("\n🧪 Tworzenie testu nawigacji OCR...")
    
    test_content = '''#!/usr/bin/env python3
"""
Test nawigacji OCR z autoryzacją
"""

import requests
from requests.auth import HTTPBasicAuth

def test_ocr_with_login():
    """Test OCR z logowaniem"""
    
    base_url = "http://localhost:8000"
    
    # Utwórz sesję
    session = requests.Session()
    
    # 1. Pobierz stronę logowania
    print("1️⃣ Pobieranie strony logowania...")
    login_page = session.get(f"{base_url}/accounts/login/")
    print(f"   Status: {login_page.status_code}")
    
    if login_page.status_code == 200:
        # Wyciągnij CSRF token
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   ✅ CSRF token: {csrf_token[:20]}...")
            
            # 2. Zaloguj się
            print("2️⃣ Logowanie...")
            login_data = {
                'login': 'testuser',
                'password': 'testpass123',
                'csrfmiddlewaretoken': csrf_token
            }
            
            login_response = session.post(
                f"{base_url}/accounts/login/",
                data=login_data,
                headers={'Referer': f"{base_url}/accounts/login/"}
            )
            
            print(f"   Status: {login_response.status_code}")
            
            if login_response.status_code == 302:
                print("   ✅ Logowanie pomyślne (przekierowanie)")
                
                # 3. Test OCR upload
                print("3️⃣ Test OCR upload...")
                ocr_response = session.get(f"{base_url}/ocr/upload/")
                print(f"   Status: {ocr_response.status_code}")
                
                if ocr_response.status_code == 200:
                    print("   ✅ OCR upload dostępny po zalogowaniu")
                    
                    # Sprawdź zawartość strony
                    if 'upload' in ocr_response.text.lower():
                        print("   ✅ Strona zawiera formularz upload")
                    else:
                        print("   ⚠️ Brak formularza upload na stronie")
                        
                else:
                    print(f"   ❌ OCR upload niedostępny: {ocr_response.status_code}")
                    
            else:
                print("   ❌ Logowanie nieudane")
                print(f"   Response: {login_response.text[:200]}...")
        else:
            print("   ❌ Nie znaleziono CSRF token")
    else:
        print("   ❌ Strona logowania niedostępna")

if __name__ == '__main__':
    test_ocr_with_login()
'''
    
    with open('test_ocr_navigation.py', 'w') as f:
        f.write(test_content)
    
    print("   ✅ Utworzono test_ocr_navigation.py")

def update_base_template():
    """Zaktualizuj base template z fix dla dropdown"""
    print("\n📝 Aktualizacja base template...")
    
    base_template = "faktury/templates/base.html"
    if not os.path.exists(base_template):
        print("   ❌ base.html nie znaleziony")
        return
    
    with open(base_template, 'r') as f:
        content = f.read()
    
    # Sprawdź czy fix już istnieje
    if 'bootstrap-dropdown-fix.js' in content:
        print("   ✅ Bootstrap dropdown fix już dodany")
        return
    
    # Dodaj fix przed zamknięciem body
    fix_script = '''
  <!-- Bootstrap Dropdown Fix -->
  <script src="{% static 'assets/js/bootstrap-dropdown-fix.js' %}"></script>
  
</body>'''
    
    # Zamień </body> na fix + </body>
    updated_content = content.replace('</body>', fix_script)
    
    # Zapisz backup
    with open(f"{base_template}.backup", 'w') as f:
        f.write(content)
    
    # Zapisz zaktualizowany plik
    with open(base_template, 'w') as f:
        f.write(updated_content)
    
    print("   ✅ Dodano Bootstrap dropdown fix do base.html")
    print("   📄 Backup zapisany jako base.html.backup")

def create_comprehensive_fix_summary():
    """Stwórz podsumowanie napraw"""
    print("\n📊 Tworzenie podsumowania napraw...")
    
    summary = '''# Naprawa OCR i Przycisków - Podsumowanie

## 🎯 Zidentyfikowane Problemy

### 1. Zakładka "OCR Faktury" nie działa
**Przyczyna:** Wymaga autoryzacji (`@login_required`)
**Rozwiązanie:** 
- Użytkownik musi być zalogowany
- Utworzono skrypt `create_test_user.py` do tworzenia użytkownika testowego

### 2. Przycisk "Dodaj" nie działa
**Przyczyna:** Bootstrap dropdown wymaga JavaScript
**Rozwiązanie:**
- Dodano `bootstrap-dropdown-fix.js` z fallback handling
- Zaktualizowano `base.html` z fix

## 🔧 Utworzone Pliki

1. **create_test_user.py** - Tworzy użytkownika testowego
2. **test_ocr_navigation.py** - Testuje nawigację OCR z logowaniem  
3. **bootstrap-dropdown-fix.js** - Naprawia dropdown functionality
4. **base.html.backup** - Backup oryginalnego template

## 🚀 Kroki do Naprawy

### Krok 1: Utwórz użytkownika testowego
```bash
python3 create_test_user.py
```

### Krok 2: Zaloguj się w aplikacji
1. Idź do http://localhost:8000/accounts/login/
2. Użyj danych:
   - Username: `testuser`
   - Password: `testpass123`

### Krok 3: Testuj funkcjonalności
```bash
python3 test_ocr_navigation.py
```

### Krok 4: Sprawdź dropdown
1. Po zalogowaniu idź do głównej strony
2. Kliknij przycisk "Dodaj" 
3. Powinno pokazać się menu dropdown

## ✅ Oczekiwane Rezultaty

Po wykonaniu napraw:
- ✅ Zakładka "OCR Faktury" działa po zalogowaniu
- ✅ Przycisk "Dodaj" pokazuje dropdown menu
- ✅ Wszystkie linki w dropdown działają
- ✅ Nawigacja jest płynna i responsywna

## 🧪 Testowanie

### Test 1: OCR Upload
```bash
# Po zalogowaniu
curl -b cookies.txt http://localhost:8000/ocr/upload/
# Powinno zwrócić 200 OK
```

### Test 2: Dropdown Menu
1. Zaloguj się do aplikacji
2. Idź do głównej strony
3. Kliknij "Dodaj" - powinno pokazać menu
4. Kliknij "Fakturę" - powinno przekierować do formularza

## 🔍 Diagnostyka Problemów

Jeśli problemy nadal występują:

1. **Sprawdź console przeglądarki** (F12)
2. **Sprawdź logi Django** w terminalu
3. **Uruchom test nawigacji:**
   ```bash
   python3 test_ocr_navigation.py
   ```

## 📞 Wsparcie

W przypadku dalszych problemów sprawdź:
- Czy Bootstrap JS się ładuje
- Czy nie ma błędów JavaScript w console
- Czy użytkownik jest zalogowany
- Czy wszystkie static files są dostępne
'''
    
    with open('OCR_BUTTONS_FIX_SUMMARY.md', 'w') as f:
        f.write(summary)
    
    print("   ✅ Utworzono OCR_BUTTONS_FIX_SUMMARY.md")

def main():
    """Główna funkcja naprawy"""
    print("🔧 Naprawa problemów OCR i przycisków FaktuLove")
    print("=" * 60)
    
    # Diagnostyka
    test_authentication_flow()
    check_bootstrap_javascript()
    check_static_files()
    
    # Tworzenie napraw
    create_test_user_script()
    create_bootstrap_fix()
    create_ocr_navigation_test()
    update_base_template()
    create_comprehensive_fix_summary()
    
    print("\n" + "=" * 60)
    print("✅ NAPRAWA ZAKOŃCZONA")
    print("=" * 60)
    print("🎯 Następne kroki:")
    print("1. python3 create_test_user.py")
    print("2. Zaloguj się: http://localhost:8000/accounts/login/")
    print("3. python3 test_ocr_navigation.py")
    print("4. Testuj dropdown na głównej stronie")
    print("\n📖 Szczegóły w: OCR_BUTTONS_FIX_SUMMARY.md")

if __name__ == '__main__':
    main()