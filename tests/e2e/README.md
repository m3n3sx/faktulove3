# FaktuLove E2E Tests - Kompleksowe Testy End-to-End

Kompleksowy zestaw testów E2E dla aplikacji FaktuLove OCR, wykorzystujący różne narzędzia testowe do pełnej weryfikacji funkcjonalności.

## 🎯 Cel Testów

Testy E2E mają na celu:
- Weryfikację działania aplikacji w rzeczywistych warunkach
- Sprawdzenie wszystkich krytycznych funkcjonalności
- Wykrycie problemów z integracją i wydajnością
- Zapewnienie jakości przed wdrożeniem

## 🧪 Dostępne Narzędzia Testowe

### 1. **Comprehensive Application Tests** (`test_comprehensive_application.py`)
- Kompleksowe testy wszystkich aspektów aplikacji
- Wykorzystuje Selenium, Playwright i testy API
- Generuje szczegółowe raporty HTML i JSON

### 2. **Selenium Tests** (`selenium_ocr_tests.py`)
- Testy WebDriver z Chrome i Firefox
- Fokus na funkcjonalności OCR
- Cross-browser testing

### 3. **Playwright Tests** (`playwright_tests.py`)
- Nowoczesne testy z Playwright
- Testy wydajności i accessibility
- Wsparcie dla Chromium, Firefox i WebKit

### 4. **Cypress Tests** (`cypress_tests.js`)
- Nowoczesne testy E2E w JavaScript
- Interaktywne testy UI
- Automatyczne screenshoty i nagrania

## 🚀 Szybki Start

### 1. Instalacja Zależności

```bash
# Automatyczna instalacja wszystkich zależności
chmod +x install_test_dependencies.sh
./install_test_dependencies.sh

# Lub ręczna instalacja
python3 run_e2e_tests.py --install-deps
```

### 2. Uruchomienie Wszystkich Testów

```bash
# Uruchom wszystkie testy E2E
python3 run_e2e_tests.py

# Z niestandardowym URL
python3 run_e2e_tests.py --url http://localhost:8080
```

### 3. Uruchomienie Konkretnych Testów

```bash
# Tylko testy Selenium
python3 tests/e2e/selenium_ocr_tests.py

# Tylko testy Playwright
python3 tests/e2e/playwright_tests.py

# Tylko testy Cypress
npx cypress run --spec tests/e2e/cypress_tests.js

# Kompleksowe testy aplikacji
python3 tests/e2e/test_comprehensive_application.py
```

## 📋 Wymagania Systemowe

### Podstawowe Wymagania
- **Python 3.8+**
- **pip3**
- **Aktywna aplikacja FaktuLove** (domyślnie na `http://localhost:8000`)

### Przeglądarki
- **Chrome/Chromium** (zalecane)
- **Firefox** (opcjonalne)
- **Safari** (tylko macOS, przez Playwright WebKit)

### Opcjonalne
- **Node.js 16+** i **npm** (dla testów Cypress)
- **Xvfb** (dla testów headless na serwerach Linux)

## 🔧 Konfiguracja

### Zmienne Środowiskowe

```bash
# URL aplikacji do testowania
export BASE_URL="http://localhost:8000"

# Tryb headless (domyślnie true)
export HEADLESS="true"

# Timeout dla testów (sekundy)
export TEST_TIMEOUT="30"

# Katalog dla screenshotów
export SCREENSHOTS_DIR="tests/screenshots"
```

### Konfiguracja Cypress

Edytuj `cypress.config.js`:

```javascript
module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8000',
    viewportWidth: 1920,
    viewportHeight: 1080,
    defaultCommandTimeout: 10000,
    // ... inne opcje
  },
})
```

### Konfiguracja pytest

Edytuj `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
addopts = --html=tests/reports/pytest_report.html --self-contained-html
markers =
    e2e: End-to-end tests
    slow: Slow running tests
```

## 📊 Raporty i Wyniki

### Lokalizacja Raportów

```
├── e2e_test_report_YYYYMMDD_HHMMSS.html    # Główny raport HTML
├── e2e_test_report_YYYYMMDD_HHMMSS.json    # Szczegółowe dane JSON
├── tests/
│   ├── reports/
│   │   └── pytest_report.html              # Raport pytest
│   ├── screenshots/                        # Screenshoty z testów
│   └── videos/                             # Nagrania Cypress
```

### Interpretacja Wyników

#### Status Testów
- ✅ **PASSED** - Test zakończony pomyślnie
- ❌ **FAILED** - Test zakończony niepowodzeniem
- ⚠️ **WARNING** - Test z ostrzeżeniami
- 💥 **ERROR** - Błąd wykonania testu

#### Metryki Wydajności
- **Load Time** - Czas ładowania strony
- **DOM Content Loaded** - Czas załadowania DOM
- **First Paint** - Pierwszy render
- **Network Requests** - Liczba żądań sieciowych

#### Problemy Accessibility
- Brakujące atrybuty `alt` w obrazach
- Brak struktury nagłówków
- Problemy z kontrastem kolorów
- Brakujące etykiety formularzy

## 🐛 Rozwiązywanie Problemów

### Częste Problemy

#### 1. Błąd "ChromeDriver not found"
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Lub pobierz ręcznie
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
```

#### 2. Błąd "Playwright browsers not installed"
```bash
python3 -m playwright install
```

#### 3. Błąd "Connection refused"
```bash
# Sprawdź czy aplikacja działa
curl http://localhost:8000

# Uruchom aplikację Django
python manage.py runserver
```

#### 4. Błąd "npm command not found"
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Debugowanie Testów

#### Tryb Verbose
```bash
python3 run_e2e_tests.py --verbose
```

#### Tryb Nie-Headless (z GUI)
```bash
export HEADLESS=false
python3 tests/e2e/selenium_ocr_tests.py
```

#### Screenshoty przy Błędach
Screenshoty są automatycznie zapisywane w `tests/screenshots/` przy każdym błędzie testu.

#### Logi Przeglądarki
```bash
# Włącz szczegółowe logi
export BROWSER_LOG_LEVEL=DEBUG
```

## 🔄 Integracja CI/CD

### GitHub Actions

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: ./install_test_dependencies.sh
      - name: Run E2E tests
        run: python3 run_e2e_tests.py
      - name: Upload test reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: |
            *.html
            *.json
            tests/screenshots/
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh './install_test_dependencies.sh'
            }
        }
        stage('E2E Tests') {
            steps {
                sh 'python3 run_e2e_tests.py'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'e2e_test_report_*.html',
                        reportName: 'E2E Test Report'
                    ])
                }
            }
        }
    }
}
```

## 📈 Najlepsze Praktyki

### 1. Przygotowanie Środowiska
- Zawsze uruchamiaj testy na czystej bazie danych
- Upewnij się, że aplikacja jest w stanie testowym
- Wyłącz zewnętrzne integracje (email, płatności)

### 2. Pisanie Testów
- Używaj Page Object Pattern dla Selenium
- Dodawaj explicit waits zamiast sleep()
- Testuj krytyczne ścieżki użytkownika
- Unikaj testowania implementacji, testuj zachowanie

### 3. Utrzymanie Testów
- Regularnie aktualizuj selektory
- Monitoruj czas wykonania testów
- Usuwaj flaky tests
- Dokumentuj zmiany w testach

### 4. Wydajność
- Uruchamiaj testy równolegle gdy to możliwe
- Używaj headless mode na CI/CD
- Optymalizuj czas ładowania stron testowych
- Cachuj dane testowe

## 🤝 Współpraca

### Dodawanie Nowych Testów

1. **Selenium Tests**: Dodaj do `selenium_ocr_tests.py`
2. **Playwright Tests**: Dodaj do `playwright_tests.py`
3. **Cypress Tests**: Dodaj do `cypress_tests.js`
4. **API Tests**: Dodaj do głównego orchestratora

### Zgłaszanie Problemów

Przy zgłaszaniu problemów z testami załącz:
- Logi z wykonania testów
- Screenshoty błędów
- Informacje o środowisku (OS, Python, przeglądarki)
- Kroki do reprodukcji

### Code Review

Przy review testów E2E sprawdź:
- Czy test jest stabilny i powtarzalny
- Czy używa odpowiednich selektorów
- Czy ma odpowiednie timeouty
- Czy generuje czytelne komunikaty błędów

## 📚 Dodatkowe Zasoby

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Cypress Documentation](https://docs.cypress.io/)
- [pytest Documentation](https://docs.pytest.org/)

## 📞 Wsparcie

W przypadku problemów z testami E2E:
1. Sprawdź sekcję "Rozwiązywanie Problemów"
2. Przejrzyj logi testów
3. Skontaktuj się z zespołem QA
4. Utwórz issue w repozytorium

---

**Ostatnia aktualizacja**: 2025-01-29
**Wersja**: 1.0.0
**Autor**: FaktuLove Development Team