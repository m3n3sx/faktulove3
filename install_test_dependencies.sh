#!/bin/bash

# Skrypt instalacji zależności testowych dla FaktuLove E2E
# Instaluje wszystkie wymagane narzędzia do testowania

set -e

echo "🚀 Instalacja zależności testowych dla FaktuLove E2E"
echo "=================================================="

# Sprawdź czy Python jest dostępny
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nie jest zainstalowany"
    exit 1
fi

echo "✅ Python3 znaleziony: $(python3 --version)"

# Sprawdź czy pip jest dostępny
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 nie jest zainstalowany"
    exit 1
fi

echo "✅ pip3 znaleziony"

# Instaluj Python dependencies
echo ""
echo "📦 Instalowanie zależności Python..."
pip3 install --upgrade pip

# Podstawowe zależności testowe
pip3 install selenium
pip3 install playwright
pip3 install requests
pip3 install pytest
pip3 install pytest-html
pip3 install pytest-xvfb
pip3 install webdriver-manager
pip3 install beautifulsoup4
pip3 install lxml

echo "✅ Zależności Python zainstalowane"

# Instaluj Playwright browsers
echo ""
echo "🌐 Instalowanie przeglądarek Playwright..."
python3 -m playwright install

echo "✅ Przeglądarki Playwright zainstalowane"

# Sprawdź czy Node.js jest dostępny dla Cypress
echo ""
echo "🔍 Sprawdzanie Node.js dla Cypress..."
if command -v node &> /dev/null; then
    echo "✅ Node.js znaleziony: $(node --version)"
    
    if command -v npm &> /dev/null; then
        echo "✅ npm znaleziony: $(npm --version)"
        
        # Inicjalizuj package.json jeśli nie istnieje
        if [ ! -f package.json ]; then
            echo "📝 Tworzenie package.json..."
            npm init -y
        fi
        
        # Instaluj Cypress
        echo "📦 Instalowanie Cypress..."
        npm install cypress --save-dev
        
        # Utwórz podstawową konfigurację Cypress
        echo "⚙️ Konfigurowanie Cypress..."
        mkdir -p cypress/e2e
        
        cat > cypress.config.js << 'EOF'
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8000',
    supportFile: false,
    specPattern: 'tests/e2e/*.js',
    screenshotsFolder: 'tests/screenshots',
    videosFolder: 'tests/videos',
    video: true,
    screenshot: true,
    viewportWidth: 1920,
    viewportHeight: 1080,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    setupNodeEvents(on, config) {
      // implement node event listeners here
      on('task', {
        generateTestReport(data) {
          console.log('Test report data:', data)
          return null
        }
      })
    },
  },
})
EOF
        
        echo "✅ Cypress zainstalowany i skonfigurowany"
    else
        echo "⚠️ npm nie znaleziony - Cypress nie zostanie zainstalowany"
    fi
else
    echo "⚠️ Node.js nie znaleziony - Cypress nie zostanie zainstalowany"
    echo "   Aby zainstalować Node.js:"
    echo "   - Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "   - lub pobierz z: https://nodejs.org/"
fi

# Sprawdź czy Chrome/Chromium jest dostępny
echo ""
echo "🔍 Sprawdzanie przeglądarek..."
if command -v google-chrome &> /dev/null; then
    echo "✅ Google Chrome znaleziony"
elif command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium znaleziony"
elif command -v chromium &> /dev/null; then
    echo "✅ Chromium znaleziony"
else
    echo "⚠️ Chrome/Chromium nie znaleziony - instalowanie..."
    
    # Próbuj zainstalować Chromium
    if command -v apt-get &> /dev/null; then
        echo "📦 Instalowanie Chromium przez apt-get..."
        sudo apt-get update
        sudo apt-get install -y chromium-browser
    elif command -v yum &> /dev/null; then
        echo "📦 Instalowanie Chromium przez yum..."
        sudo yum install -y chromium
    else
        echo "⚠️ Nie można automatycznie zainstalować Chromium"
        echo "   Zainstaluj ręcznie przeglądarkę Chrome lub Chromium"
    fi
fi

if command -v firefox &> /dev/null; then
    echo "✅ Firefox znaleziony"
else
    echo "⚠️ Firefox nie znaleziony - instalowanie..."
    
    # Próbuj zainstalować Firefox
    if command -v apt-get &> /dev/null; then
        echo "📦 Instalowanie Firefox przez apt-get..."
        sudo apt-get install -y firefox
    elif command -v yum &> /dev/null; then
        echo "📦 Instalowanie Firefox przez yum..."
        sudo yum install -y firefox
    else
        echo "⚠️ Nie można automatycznie zainstalować Firefox"
        echo "   Zainstaluj ręcznie przeglądarkę Firefox"
    fi
fi

# Sprawdź czy WebDriver jest dostępny
echo ""
echo "🔍 Sprawdzanie WebDriver..."

# Sprawdź ChromeDriver
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver znaleziony: $(chromedriver --version | head -n1)"
else
    echo "⚠️ ChromeDriver nie znaleziony - instalowanie..."
    
    if command -v apt-get &> /dev/null; then
        echo "📦 Instalowanie ChromeDriver przez apt-get..."
        sudo apt-get install -y chromium-chromedriver
        
        # Dodaj do PATH jeśli nie ma
        if ! command -v chromedriver &> /dev/null; then
            echo "🔗 Tworzenie linku symbolicznego dla ChromeDriver..."
            sudo ln -sf /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver
        fi
    else
        echo "⚠️ Nie można automatycznie zainstalować ChromeDriver"
        echo "   Pobierz z: https://chromedriver.chromium.org/"
    fi
fi

# Sprawdź GeckoDriver
if command -v geckodriver &> /dev/null; then
    echo "✅ GeckoDriver znaleziony: $(geckodriver --version | head -n1)"
else
    echo "⚠️ GeckoDriver nie znaleziony - instalowanie..."
    
    if command -v apt-get &> /dev/null; then
        echo "📦 Instalowanie GeckoDriver przez apt-get..."
        sudo apt-get install -y firefox-geckodriver
        
        # Dodaj do PATH jeśli nie ma
        if ! command -v geckodriver &> /dev/null; then
            echo "🔗 Tworzenie linku symbolicznego dla GeckoDriver..."
            sudo ln -sf /usr/bin/geckodriver /usr/local/bin/geckodriver 2>/dev/null || true
        fi
    else
        echo "⚠️ Nie można automatycznie zainstalować GeckoDriver"
        echo "   Pobierz z: https://github.com/mozilla/geckodriver/releases"
    fi
fi

echo ""
echo "🎯 Tworzenie struktury katalogów testowych..."
mkdir -p tests/e2e
mkdir -p tests/reports
mkdir -p tests/screenshots
mkdir -p tests/videos

echo "✅ Struktura katalogów utworzona"

# Utwórz plik konfiguracyjny pytest
echo ""
echo "⚙️ Konfigurowanie pytest..."
cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --html=tests/reports/pytest_report.html 
    --self-contained-html
    --tb=short
    -v
markers =
    e2e: End-to-end tests
    selenium: Selenium tests
    playwright: Playwright tests
    slow: Slow running tests
EOF

echo "✅ pytest skonfigurowany"

# Sprawdź czy wszystko działa
echo ""
echo "🧪 Sprawdzanie instalacji..."

# Test Selenium
python3 -c "
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print('✅ Selenium - OK')
except ImportError as e:
    print(f'❌ Selenium - Błąd: {e}')
"

# Test Playwright
python3 -c "
try:
    from playwright.sync_api import sync_playwright
    print('✅ Playwright - OK')
except ImportError as e:
    print(f'❌ Playwright - Błąd: {e}')
"

# Test requests
python3 -c "
try:
    import requests
    print('✅ Requests - OK')
except ImportError as e:
    print(f'❌ Requests - Błąd: {e}')
"

# Uczyń pliki wykonywalnymi
echo ""
echo "🔧 Ustawianie uprawnień..."
chmod +x run_e2e_tests.py
chmod +x tests/e2e/*.py

echo ""
echo "=================================================="
echo "✅ Instalacja zależności testowych zakończona!"
echo ""
echo "🚀 Aby uruchomić wszystkie testy E2E:"
echo "   python3 run_e2e_tests.py"
echo ""
echo "🔧 Aby uruchomić konkretny typ testów:"
echo "   python3 tests/e2e/test_comprehensive_application.py"
echo "   python3 tests/e2e/playwright_tests.py"
echo "   npx cypress run --spec tests/e2e/cypress_tests.js"
echo ""
echo "📊 Raporty będą zapisane w:"
echo "   - JSON/HTML: katalog główny projektu"
echo "   - pytest: tests/reports/"
echo "   - Screenshots: tests/screenshots/"
echo "   - Videos: tests/videos/"
echo ""
echo "🎯 Przykładowe uruchomienie z parametrami:"
echo "   python3 run_e2e_tests.py --url http://localhost:8000"
echo "   python3 run_e2e_tests.py --install-deps  # ponowna instalacja"
echo "=================================================="