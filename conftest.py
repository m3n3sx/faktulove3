"""
Global pytest configuration and fixtures for FaktuLove testing framework
"""
import os
import pytest
import tempfile
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from unittest.mock import Mock, patch
from faktury.models import Firma, Kontrahent, Faktura
from faktury.services.company_management_service import CompanyManagementService
import time
from datetime import datetime, timedelta


# Test database configuration
@pytest.fixture(scope='session')
def django_db_setup():
    """Configure test database settings"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }


# User fixtures
@pytest.fixture
def test_user():
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user():
    """Create an admin user"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def test_company(test_user):
    """Create a test company"""
    return Firma.objects.create(
        nazwa='Test Company Sp. z o.o.',
        nip='1234567890',
        regon='123456789',
        adres='ul. Testowa 1, 00-001 Warszawa',
        user=test_user
    )


@pytest.fixture
def test_contractor(test_user):
    """Create a test contractor"""
    return Kontrahent.objects.create(
        nazwa='Test Contractor',
        nip='0987654321',
        adres='ul. Kontrahenta 2, 00-002 Kraków',
        firma=Firma.objects.filter(user=test_user).first()
    )


@pytest.fixture
def test_invoice(test_company, test_contractor):
    """Create a test invoice"""
    return Faktura.objects.create(
        numer='TEST/001/2025',
        data_wystawienia=datetime.now().date(),
        data_sprzedazy=datetime.now().date(),
        kontrahent=test_contractor,
        firma=test_company,
        wartosc_netto=100.00,
        wartosc_brutto=123.00,
        vat=23.00
    )


# File upload fixtures
@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    return SimpleUploadedFile(
        "test_invoice.pdf",
        b"PDF content here",
        content_type="application/pdf"
    )


@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing"""
    return SimpleUploadedFile(
        "test_invoice.jpg",
        b"JPEG content here",
        content_type="image/jpeg"
    )


@pytest.fixture
def temp_media_root():
    """Create temporary media directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.object(settings, 'MEDIA_ROOT', temp_dir):
            yield temp_dir


# OCR service mocks
@pytest.fixture
def mock_ocr_service():
    """Mock OCR service for testing"""
    mock = Mock()
    mock.process_document.return_value = {
        'text': 'Sample extracted text',
        'confidence': 0.95,
        'fields': {
            'invoice_number': 'INV/001/2025',
            'date': '2025-01-01',
            'total': '123.00'
        }
    }
    return mock


@pytest.fixture
def mock_paddle_ocr():
    """Mock PaddleOCR service"""
    with patch('faktury.services.paddle_ocr_service.PaddleOCR') as mock:
        mock.return_value.ocr.return_value = [
            [
                [[0, 0], [100, 0], [100, 20], [0, 20]],
                ('Sample text', 0.95)
            ]
        ]
        yield mock


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Database fixtures
@pytest.fixture
def clean_db():
    """Ensure clean database state"""
    # Clean up any existing test data
    User.objects.filter(username__startswith='test').delete()
    Firma.objects.filter(nazwa__contains='Test').delete()
    Kontrahent.objects.filter(nazwa__contains='Test').delete()
    Faktura.objects.filter(numer__startswith='TEST').delete()


# API client fixtures
@pytest.fixture
def api_client():
    """Django REST framework API client"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, test_user):
    """Authenticated API client"""
    api_client.force_authenticate(user=test_user)
    return api_client


# Multi-company fixtures
@pytest.fixture
def multi_company_setup(test_user):
    """Setup multiple companies for testing"""
    service = CompanyManagementService()
    companies = service.create_test_companies()
    return {
        'user': test_user,
        'companies': companies,
        'service': service
    }


# Error simulation fixtures
@pytest.fixture
def simulate_database_error():
    """Simulate database connection errors"""
    def _simulate_error():
        from django.db import connection
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor.side_effect = Exception("Database connection failed")
            yield mock_cursor
    return _simulate_error


@pytest.fixture
def simulate_network_error():
    """Simulate network connectivity issues"""
    def _simulate_error():
        import requests
        with patch.object(requests, 'post') as mock_post:
            mock_post.side_effect = requests.ConnectionError("Network unreachable")
            yield mock_post
    return _simulate_error


# Browser testing fixtures (for Selenium)
@pytest.fixture
def browser_driver():
    """Selenium WebDriver for browser testing"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    except ImportError:
        pytest.skip("Selenium not installed")
    except Exception as e:
        pytest.skip(f"Browser driver not available: {e}")


# Mobile testing fixtures
@pytest.fixture
def mobile_browser_driver():
    """Mobile browser simulation"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        mobile_emulation = {
            "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        }
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    except ImportError:
        pytest.skip("Selenium not installed")
    except Exception as e:
        pytest.skip(f"Mobile browser driver not available: {e}")


# Test data factories
class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_polish_company_data():
        """Create realistic Polish company test data"""
        return {
            'nazwa': 'Testowa Firma Sp. z o.o.',
            'nip': '1234567890',
            'regon': '123456789',
            'krs': '0000123456',
            'adres': 'ul. Marszałkowska 1, 00-001 Warszawa',
            'kod_pocztowy': '00-001',
            'miasto': 'Warszawa',
            'telefon': '+48 22 123 45 67',
            'email': 'kontakt@testowa-firma.pl'
        }
    
    @staticmethod
    def create_invoice_data():
        """Create realistic invoice test data"""
        return {
            'numer': f'FV/{datetime.now().strftime("%m/%Y")}/001',
            'data_wystawienia': datetime.now().date(),
            'data_sprzedazy': datetime.now().date(),
            'data_platnosci': (datetime.now() + timedelta(days=14)).date(),
            'wartosc_netto': 1000.00,
            'vat': 230.00,
            'wartosc_brutto': 1230.00,
            'uwagi': 'Testowa faktura'
        }


@pytest.fixture
def test_data_factory():
    """Test data factory fixture"""
    return TestDataFactory()


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom settings"""
    import django
    from django.conf import settings
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            TESTING=True,
            USE_TZ=True,
            SECRET_KEY='test-secret-key-for-testing-only',
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'django.contrib.admin',
                'rest_framework',
                'faktury',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            MEDIA_ROOT='/tmp/test_media',
            STATIC_ROOT='/tmp/test_static',
        )
    
    django.setup()


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add markers based on test file location
        if "test_ocr" in item.nodeid:
            item.add_marker(pytest.mark.ocr)
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        if "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if "test_security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)


def pytest_runtest_setup(item):
    """Setup for each test"""
    # Skip slow tests unless explicitly requested
    if "slow" in item.keywords and not item.config.getoption("--runslow", default=False):
        pytest.skip("need --runslow option to run")


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--runslow", action="store_true", default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--browser", action="store", default="chrome",
        help="browser to use for browser tests"
    )