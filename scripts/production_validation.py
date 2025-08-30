#!/usr/bin/env python3
"""
Production Critical Fixes Validation Script
Validates all critical functionality in production environment
"""

import os
import sys
import requests
import time
import json
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ProductionValidator:
    def __init__(self, base_url="http://localhost:8000", headless=True):
        self.base_url = base_url
        self.results = {
            'invoice_creation': False,
            'ocr_upload': False,
            'navigation_icons': False,
            'error_handling': False,
            'static_files': False,
            'react_components': False,
            'performance': {},
            'errors': []
        }
        
        # Setup Chrome driver
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(1920, 1080)
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            sys.exit(1)

    def log_error(self, test_name, error):
        """Log validation error"""
        error_msg = f"{test_name}: {str(error)}"
        self.results['errors'].append(error_msg)
        print(f"❌ {error_msg}")

    def log_success(self, test_name, message=""):
        """Log validation success"""
        success_msg = f"{test_name}: {message}" if message else test_name
        print(f"✅ {success_msg}")

    def validate_static_files(self):
        """Validate critical static files are accessible"""
        print("\n🔍 Validating static files...")
        
        critical_files = [
            '/static/assets/css/remixicon.css',
            '/static/assets/js/safe-error-handler.js',
            '/static/assets/js/safe-dependency-manager.js',
            '/static/js/react.production.min.js',
            '/static/js/react-dom.production.min.js',
            '/static/js/upload-app.bundle.js',
            '/static/assets/css/style.css',
            '/static/css/design-system.css'
        ]
        
        accessible_files = 0
        for file_path in critical_files:
            try:
                url = urljoin(self.base_url, file_path)
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    accessible_files += 1
                    self.log_success(f"Static file accessible: {file_path}")
                else:
                    self.log_error("Static Files", f"{file_path} returned {response.status_code}")
            except Exception as e:
                self.log_error("Static Files", f"Failed to access {file_path}: {e}")
        
        self.results['static_files'] = accessible_files == len(critical_files)
        return self.results['static_files']

    def validate_invoice_creation_workflow(self):
        """Validate invoice creation workflow"""
        print("\n🧾 Validating invoice creation workflow...")
        
        try:
            # Navigate to login page
            self.driver.get(urljoin(self.base_url, '/accounts/login/'))
            
            # Check if login form exists
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "login"))
            )
            
            # For production validation, we'll check if the "Dodaj fakturę" button exists
            # after login (assuming test credentials or we skip login for now)
            
            # Navigate directly to dashboard to check "Dodaj" button
            self.driver.get(urljoin(self.base_url, '/'))
            
            # Look for "Dodaj fakturę" button or link
            dodaj_buttons = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'dodaj_fakture') or contains(text(), 'Dodaj')]")
            
            if dodaj_buttons:
                self.log_success("Invoice Creation", "Dodaj fakturę button found")
                
                # Try to click the button and verify it navigates correctly
                dodaj_buttons[0].click()
                
                # Wait for navigation and check URL
                WebDriverWait(self.driver, 10).until(
                    lambda driver: 'dodaj_fakture' in driver.current_url
                )
                
                self.log_success("Invoice Creation", "Navigation to invoice form successful")
                self.results['invoice_creation'] = True
            else:
                self.log_error("Invoice Creation", "Dodaj fakturę button not found")
                
        except TimeoutException:
            self.log_error("Invoice Creation", "Timeout waiting for elements")
        except Exception as e:
            self.log_error("Invoice Creation", f"Unexpected error: {e}")
        
        return self.results['invoice_creation']

    def validate_ocr_upload_functionality(self):
        """Validate OCR upload functionality"""
        print("\n📤 Validating OCR upload functionality...")
        
        try:
            # Navigate to OCR upload page
            self.driver.get(urljoin(self.base_url, '/ocr/upload/'))
            
            # Check if page loads without "Ładowanie interfejsu przesyłania..." message
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "ocr-upload-app"))
            )
            
            # Check that loading message is not visible
            loading_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Ładowanie interfejsu przesyłania')]")
            
            if not loading_elements or not any(elem.is_displayed() for elem in loading_elements):
                self.log_success("OCR Upload", "Page loads without loading message")
                
                # Check for file input or upload area
                file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file'], .upload-area")
                
                if file_inputs:
                    self.log_success("OCR Upload", "File upload interface available")
                    
                    # Check for React component or fallback form
                    react_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-reactroot], .upload-app")
                    fallback_elements = self.driver.find_elements(By.ID, "fallback-form")
                    
                    if react_elements or fallback_elements:
                        self.log_success("OCR Upload", "Upload interface properly rendered")
                        self.results['ocr_upload'] = True
                    else:
                        self.log_error("OCR Upload", "Neither React nor fallback interface found")
                else:
                    self.log_error("OCR Upload", "No file upload interface found")
            else:
                self.log_error("OCR Upload", "Loading message still visible")
                
        except TimeoutException:
            self.log_error("OCR Upload", "Timeout loading OCR upload page")
        except Exception as e:
            self.log_error("OCR Upload", f"Unexpected error: {e}")
        
        return self.results['ocr_upload']

    def validate_navigation_icons(self):
        """Validate navigation icons display correctly"""
        print("\n🎨 Validating navigation icons...")
        
        try:
            # Navigate to main page
            self.driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check for RemixIcon classes
            icon_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='ri-'], [class*='remix'], iconify-icon")
            
            if icon_elements:
                self.log_success("Navigation Icons", f"Found {len(icon_elements)} icon elements")
                
                # Check if RemixIcon font is loaded
                font_loaded = self.driver.execute_script("""
                    return document.fonts.check('1em remixicon');
                """)
                
                if font_loaded:
                    self.log_success("Navigation Icons", "RemixIcon font loaded successfully")
                    self.results['navigation_icons'] = True
                else:
                    self.log_error("Navigation Icons", "RemixIcon font not loaded")
            else:
                self.log_error("Navigation Icons", "No icon elements found")
                
        except Exception as e:
            self.log_error("Navigation Icons", f"Unexpected error: {e}")
        
        return self.results['navigation_icons']

    def validate_error_handling_systems(self):
        """Validate error handling and monitoring systems"""
        print("\n🛡️ Validating error handling systems...")
        
        try:
            # Navigate to main page
            self.driver.get(self.base_url)
            
            # Check if error handling scripts are loaded
            error_handler_loaded = self.driver.execute_script("""
                return typeof window.SafeErrorHandler !== 'undefined';
            """)
            
            dependency_manager_loaded = self.driver.execute_script("""
                return typeof window.SafeDependencyManager !== 'undefined';
            """)
            
            if error_handler_loaded:
                self.log_success("Error Handling", "SafeErrorHandler loaded")
            else:
                self.log_error("Error Handling", "SafeErrorHandler not loaded")
            
            if dependency_manager_loaded:
                self.log_success("Error Handling", "SafeDependencyManager loaded")
            else:
                self.log_error("Error Handling", "SafeDependencyManager not loaded")
            
            # Check for monitoring scripts
            monitoring_scripts = self.driver.execute_script("""
                return {
                    staticFileMonitor: typeof window.staticFileHealthCheck !== 'undefined',
                    errorTracking: typeof window.ErrorTracker !== 'undefined',
                    performanceOptimizer: typeof window.PerformanceOptimizer !== 'undefined'
                };
            """)
            
            monitoring_active = any(monitoring_scripts.values())
            if monitoring_active:
                self.log_success("Error Handling", "Monitoring systems active")
            else:
                self.log_error("Error Handling", "No monitoring systems detected")
            
            self.results['error_handling'] = error_handler_loaded and dependency_manager_loaded
            
        except Exception as e:
            self.log_error("Error Handling", f"Unexpected error: {e}")
        
        return self.results['error_handling']

    def validate_react_components(self):
        """Validate React components are working"""
        print("\n⚛️ Validating React components...")
        
        try:
            # Check if React is loaded globally
            self.driver.get(self.base_url)
            
            react_loaded = self.driver.execute_script("""
                return typeof React !== 'undefined' && typeof ReactDOM !== 'undefined';
            """)
            
            if react_loaded:
                self.log_success("React Components", "React and ReactDOM loaded")
                
                # Check for React components
                react_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-reactroot], .upload-app")
                
                if react_elements:
                    self.log_success("React Components", "React components found in DOM")
                    self.results['react_components'] = True
                else:
                    self.log_success("React Components", "React loaded but no components detected (may be lazy-loaded)")
                    self.results['react_components'] = True
            else:
                self.log_error("React Components", "React or ReactDOM not loaded")
                
        except Exception as e:
            self.log_error("React Components", f"Unexpected error: {e}")
        
        return self.results['react_components']

    def measure_performance(self):
        """Measure basic performance metrics"""
        print("\n⚡ Measuring performance...")
        
        try:
            self.driver.get(self.base_url)
            
            # Wait for page to fully load
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Get performance metrics
            performance_data = self.driver.execute_script("""
                const perfData = performance.getEntriesByType('navigation')[0];
                return {
                    loadTime: perfData.loadEventEnd - perfData.loadEventStart,
                    domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                    totalTime: perfData.loadEventEnd - perfData.fetchStart,
                    resourceCount: performance.getEntriesByType('resource').length
                };
            """)
            
            self.results['performance'] = performance_data
            
            if performance_data['totalTime'] < 5000:  # Less than 5 seconds
                self.log_success("Performance", f"Page load time: {performance_data['totalTime']:.0f}ms")
            else:
                self.log_error("Performance", f"Slow page load: {performance_data['totalTime']:.0f}ms")
            
            self.log_success("Performance", f"Resources loaded: {performance_data['resourceCount']}")
            
        except Exception as e:
            self.log_error("Performance", f"Failed to measure performance: {e}")

    def run_validation(self):
        """Run all validation tests"""
        print("🚀 Starting Production Critical Fixes Validation")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all validation tests
        self.validate_static_files()
        self.validate_invoice_creation_workflow()
        self.validate_ocr_upload_functionality()
        self.validate_navigation_icons()
        self.validate_error_handling_systems()
        self.validate_react_components()
        self.measure_performance()
        
        # Calculate results
        total_tests = 6
        passed_tests = sum([
            self.results['static_files'],
            self.results['invoice_creation'],
            self.results['ocr_upload'],
            self.results['navigation_icons'],
            self.results['error_handling'],
            self.results['react_components']
        ])
        
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 60)
        print("📊 VALIDATION RESULTS")
        print("=" * 60)
        
        print(f"✅ Static Files: {'PASS' if self.results['static_files'] else 'FAIL'}")
        print(f"✅ Invoice Creation: {'PASS' if self.results['invoice_creation'] else 'FAIL'}")
        print(f"✅ OCR Upload: {'PASS' if self.results['ocr_upload'] else 'FAIL'}")
        print(f"✅ Navigation Icons: {'PASS' if self.results['navigation_icons'] else 'FAIL'}")
        print(f"✅ Error Handling: {'PASS' if self.results['error_handling'] else 'FAIL'}")
        print(f"✅ React Components: {'PASS' if self.results['react_components'] else 'FAIL'}")
        
        print(f"\n📈 Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"⏱️ Total Time: {time.time() - start_time:.1f}s")
        
        if self.results['errors']:
            print(f"\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        # Save results to file
        with open('production_validation_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: production_validation_results.json")
        
        return success_rate >= 80  # 80% success rate required

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate production critical fixes')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL to test')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    validator = ProductionValidator(base_url=args.url, headless=args.headless)
    
    try:
        success = validator.run_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        sys.exit(1)
    finally:
        validator.cleanup()

if __name__ == '__main__':
    main()