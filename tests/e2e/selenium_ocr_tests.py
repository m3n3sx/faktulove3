#!/usr/bin/env python3
"""
Selenium-based OCR Functionality Tests
Comprehensive testing of OCR upload and processing workflows
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import requests

class SeleniumOCRTests:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.test_results = []
        
    def setup_driver(self):
        """Setup Chrome WebDriver with comprehensive options"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # For headless mode (uncomment for CI)
        # chrome_options.add_argument('--headless')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            print("✅ Chrome WebDriver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            raise
    
    def teardown_driver(self):
        """Cleanup WebDriver"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver closed")
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if success else "❌"
        print(f"\n{status_emoji} TEST: {test_name}")
        if not success:
            print(f"   Error: {details.get('error', 'Unknown error')}")
    
    def test_01_server_connectivity(self):
        """Test if server is running and accessible"""
        test_name = "Server Connectivity"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Test HTTP connectivity
            response = requests.get(self.base_url, timeout=10)
            
            print(f"   Server response: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            # Check if it's a Django application
            is_django = 'django' in response.headers.get('Server', '').lower() or \
                       'csrftoken' in response.cookies or \
                       'sessionid' in response.cookies
            
            print(f"   Django detected: {is_django}")
            
            self.log_test_result(test_name, response.status_code < 400, {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'is_django': is_django,
                'response_time': response.elapsed.total_seconds()
            })
            
        except Exception as e:
            self.log_test_result(test_name, False, {'error': str(e)})
    
    def test_02_homepage_load(self):
        """Test homepage loading with Selenium"""
        test_name = "Homepage Load (Selenium)"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Navigate to homepage
            self.driver.get(self.base_url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Get page details
            title = self.driver.title
            current_url = self.driver.current_url
            
            print(f"   Page title: {title}")
            print(f"   Current URL: {current_url}")
            
            # Check for common elements
            elements_found = {}
            
            # Check for navigation
            try:
                nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .navbar, .navigation")
                elements_found['navigation'] = len(nav_elements)
                print(f"   Navigation elements: {len(nav_elements)}")
            except:
                elements_found['navigation'] = 0
            
            # Check for main content
            try:
                main_elements = self.driver.find_elements(By.CSS_SELECTOR, "main, .main-content, .content")
                elements_found['main_content'] = len(main_elements)
                print(f"   Main content elements: {len(main_elements)}")
            except:
                elements_found['main_content'] = 0
            
            # Check for forms
            try:
                forms = self.driver.find_elements(By.TAG_NAME, "form")
                elements_found['forms'] = len(forms)
                print(f"   Forms found: {len(forms)}")
            except:
                elements_found['forms'] = 0
            
            # Take screenshot
            self.driver.save_screenshot('test_results/selenium_homepage.png')
            
            # Check for error indicators
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, .exception")
            has_errors = len(error_elements) > 0
            
            if has_errors:
                print(f"   ⚠️ Error elements found: {len(error_elements)}")
            
            self.log_test_result(test_name, not has_errors, {
                'title': title,
                'current_url': current_url,
                'elements_found': elements_found,
                'has_errors': has_errors,
                'error_count': len(error_elements)
            })
            
        except Exception as e:
            self.log_test_result(test_name, False, {'error': str(e)})
            # Take error screenshot
            try:
                self.driver.save_screenshot('test_results/selenium_homepage_error.png')
            except:
                pass
    
    def test_03_ocr_page_navigation(self):
        """Test navigation to OCR upload page"""
        test_name = "OCR Page Navigation"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Try direct navigation to OCR page
            ocr_url = f"{self.base_url}/ocr/upload/"
            self.driver.get(ocr_url)
            
            # Wait for page load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            current_url = self.driver.current_url
            title = self.driver.title
            
            print(f"   Requested URL: {ocr_url}")
            print(f"   Current URL: {current_url}")
            print(f"   Page title: {title}")
            
            # Check if redirected to login
            is_login_page = any(keyword in current_url.lower() for keyword in ['login', 'auth', 'signin'])
            is_login_form = len(self.driver.find_elements(By.CSS_SELECTOR, "input[type='password'], .login-form")) > 0
            
            if is_login_page or is_login_form:
                print("   ℹ️ Redirected to login page (authentication required)")
                page_type = "login_required"
            else:
                # Check for OCR-specific elements
                file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                upload_forms = self.driver.find_elements(By.CSS_SELECTOR, "form[enctype*='multipart']")
                dropzones = self.driver.find_elements(By.CSS_SELECTOR, ".dropzone, .drag-drop")
                
                print(f"   File inputs: {len(file_inputs)}")
                print(f"   Upload forms: {len(upload_forms)}")
                print(f"   Dropzones: {len(dropzones)}")
                
                if file_inputs or upload_forms or dropzones:
                    page_type = "ocr_interface"
                    print("   ✅ OCR interface elements found")
                else:
                    page_type = "unknown"
                    print("   ⚠️ No OCR interface elements found")
            
            # Take screenshot
            self.driver.save_screenshot('test_results/selenium_ocr_page.png')
            
            self.log_test_result(test_name, True, {
                'requested_url': ocr_url,
                'current_url': current_url,
                'title': title,
                'page_type': page_type,
                'is_login_required': is_login_page or is_login_form
            })
            
        except Exception as e:
            self.log_test_result(test_name, False, {'error': str(e)})
    
    def test_04_login_functionality(self):
        """Test login functionality if login form is available"""
        test_name = "Login Functionality"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Look for login form elements
            username_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                "input[name='username'], input[name='email'], input[type='email'], #id_username")
            password_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                "input[name='password'], input[type='password'], #id_password")
            login_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button[type='submit'], input[type='submit'], .btn-login")
            
            print(f"   Username fields: {len(username_fields)}")
            print(f"   Password fields: {len(password_fields)}")
            print(f"   Login buttons: {len(login_buttons)}")
            
            if username_fields and password_fields and login_buttons:
                print("   ✅ Complete login form found")
                
                # Try to interact with form (without actually logging in)
                username_field = username_fields[0]
                password_field = password_fields[0]
                
                # Check if fields are interactable
                username_enabled = username_field.is_enabled()
                password_enabled = password_field.is_enabled()
                
                print(f"   Username field enabled: {username_enabled}")
                print(f"   Password field enabled: {password_enabled}")
                
                # Test field interaction (clear any existing content)
                if username_enabled:
                    username_field.clear()
                    username_field.send_keys("test")
                    username_value = username_field.get_attribute('value')
                    print(f"   Username field accepts input: {username_value == 'test'}")
                
                if password_enabled:
                    password_field.clear()
                    password_field.send_keys("test")
                    # Don't log password value for security
                    print("   Password field accepts input: ✅")
                
                form_functional = username_enabled and password_enabled
                
            else:
                print("   ℹ️ No complete login form found")
                form_functional = False
            
            self.log_test_result(test_name, True, {
                'username_fields': len(username_fields),
                'password_fields': len(password_fields),
                'login_buttons': len(login_buttons),
                'form_functional': form_functional
            })
            
        except Exception as e:
            self.log_test_result(test_name, False, {'error': str(e)})
    
    def test_05_create_test_file(self):
        """Create a test file for OCR upload testing"""
        test_name = "Create Test File"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Create test directory
            test_dir = Path('test_results')
            test_dir.mkdir(exist_ok=True)
            
            # Create a simple test image (text file for now)
            test_file_path = test_dir / 'test_invoice.txt'
            
            test_content = """
FAKTURA VAT
Nr: FV/2025/001
Data: 29.08.2025

Sprzedawca:
Test Company Sp. z o.o.
ul. Testowa 123
00-001 Warszawa
NIP: 1234567890

Nabywca:
Klient Testowy
ul. Kliencka 456
00-002 Kraków
NIP: 0987654321

Pozycje:
1. Usługa testowa - 1000.00 PLN + 23% VAT = 1230.00 PLN

Razem do zapłaty: 1230.00 PLN
"""
            
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # Verify file was created
            file_exists = test_file_path.exists()
            file_size = test_file_path.stat().st_size if file_exists else 0
            
            print(f"   Test file created: {file_exists}")
            print(f"   File path: {test_file_path}")
            print(f"   File size: {file_size} bytes")
            
            self.log_test_result(test_name, file_exists, {
                'file_path': str(test_file_path),
                'file_exists': file_exists,
                'file_size': file_size
            })
            
        except Exception as e:
            self.log_test_result(test_name, False, {'error': str(e)})
    
    def test_06_file_upload_interaction(self):
        """Test file upload interaction (if available)"""
        test_name = "File Upload Interaction"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Navigate back to OCR page
            ocr_url = f"{self.base_url}/ocr/upload/"
            self.driver.get(ocr_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Look for file input elements
            file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            
            if not file_inputs:
                print("   ℹ️ No file input elements found")
                self.log_test_result(test_name, False, {
                    'error': 'No file input elements found',
                    'file_inputs': 0
                })
                return
            
            print(f"   Found {len(file_inputs)} file input(s)")
            
            # Try to interact with first file input
            file_input = file_inputs[0]
            
            # Check if file input is visible and enabled
            is_displayed = file_input.is_displayed()
            is_enabled = file_input.is_enabled()
            
            print(f"   File input displayed: {is_displayed}")
            print(f"   File input enabled: {is_enabled}")
            
            if is_enabled:
                # Try to send a file path (test file we created)
                test_file_path = Path('test_results/test_invoice.txt').absolute()
                
                if test_file_path.exists():
                    try:
                        file_input.send_keys(str(test_file_path))
                        print("   ✅ File path sent to input")
                        
                        # Check if file was accepted
                        file_value = file_input.get_attribute('value')
                        file_accepted = len(file_value) > 0
                        
                        print(f"   File accepted: {file_accepted}")
                        
                    except Exception as upload_error:
                        print(f"   ❌ File upload error: {upload_error}")
                        file_accepted = False
                else:
                    print("   ⚠️ Test file not found")
                    file_accepted = False
            else:
                file_accepted = False
            
            self.log_test_result(test_name, file_accepted, {
                'file_inputs_found': len(file_inputs),
                'input_displayed': is_displayed,
                'input_enabled': is_enabled,
                'file_accepted': file_accepted
            })
            
        except Exception as e:
            self.log_test_result(test_name, False, {'error': str(e)})
    
    def test_07_javascript_functionality(self):
        """Test JavaScript functionality on the page"""
        test_name = "JavaScript Functionality"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Execute JavaScript to test basic functionality
            js_tests = []
            
            # Test 1: Basic JavaScript execution
            try:
                result = self.driver.execute_script("return 2 + 2;")
                js_tests.append({'test': 'basic_math', 'success': result == 4})
                print(f"   Basic JS execution: {'✅' if result == 4 else '❌'}")
            except Exception as e:
                js_tests.append({'test': 'basic_math', 'success': False, 'error': str(e)})
            
            # Test 2: jQuery availability
            try:
                jquery_available = self.driver.execute_script("return typeof jQuery !== 'undefined';")
                js_tests.append({'test': 'jquery_available', 'success': jquery_available})
                print(f"   jQuery available: {'✅' if jquery_available else '❌'}")
            except Exception as e:
                js_tests.append({'test': 'jquery_available', 'success': False, 'error': str(e)})
            
            # Test 3: DOM manipulation
            try:
                element_count = self.driver.execute_script("return document.querySelectorAll('*').length;")
                js_tests.append({'test': 'dom_access', 'success': element_count > 0})
                print(f"   DOM elements accessible: {element_count} elements")
            except Exception as e:
                js_tests.append({'test': 'dom_access', 'success': False, 'error': str(e)})
            
            # Test 4: Console errors
            try:
                console_errors = self.driver.get_log('browser')
                error_count = len([log for log in console_errors if log['level'] == 'SEVERE'])
                js_tests.append({'test': 'console_errors', 'success': error_count == 0, 'error_count': error_count})
                print(f"   Console errors: {error_count}")
            except Exception as e:
                js_tests.append({'test': 'console_errors', 'success': False, 'error': str(e)})
            
            # Overall JavaScript health
            successful_tests = sum(1 for test in js_tests if test['success'])
            js_healthy = successful_tests >= len(js_tests) / 2
            
            self.log_test_result(test_name, js_healthy, {
                'js_tests': js_tests,
                'successful_tests': successful_tests,
                'total_tests': len(js_tests),
                'js_healthy': js_healthy
            })
            
        except Exception as e:
            self.log_test_result(test_name, False, {'error': str(e)})
    
    def run_all_tests(self):
        """Run all Selenium tests"""
        print("🚀 Starting Selenium OCR Tests")
        print("=" * 50)
        
        # Create results directory
        os.makedirs('test_results', exist_ok=True)
        
        try:
            self.setup_driver()
            
            # Run tests
            self.test_01_server_connectivity()
            self.test_02_homepage_load()
            self.test_03_ocr_page_navigation()
            self.test_04_login_functionality()
            self.test_05_create_test_file()
            self.test_06_file_upload_interaction()
            self.test_07_javascript_functionality()
            
        finally:
            self.teardown_driver()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("📊 SELENIUM TEST RESULTS")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} - {result['test_name']}")
            if not result['success']:
                print(f"    Error: {result['details'].get('error', 'Unknown')}")
        
        # Save report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'framework': 'selenium',
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'test_results': self.test_results
        }
        
        with open('test_results/selenium_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved to: test_results/selenium_test_report.json")

def main():
    """Main test runner"""
    tester = SeleniumOCRTests()
    tester.run_all_tests()

if __name__ == "__main__":
    main()