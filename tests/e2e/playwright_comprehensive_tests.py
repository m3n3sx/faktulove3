#!/usr/bin/env python3
"""
Comprehensive Playwright E2E Tests for FaktuLove OCR
Tests all critical user journeys and OCR functionality
"""

import asyncio
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import pytest

class FaktuLoveE2ETests:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.browser = None
        self.context = None
        self.page = None
        
    async def setup(self):
        """Setup browser and context"""
        playwright = await async_playwright().start()
        
        # Launch browser with comprehensive options
        self.browser = await playwright.chromium.launch(
            headless=False,  # Set to True for CI
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--allow-running-insecure-content'
            ]
        )
        
        # Create context with realistic viewport
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # Enable request/response logging
        self.context.on('request', self._log_request)
        self.context.on('response', self._log_response)
        
        self.page = await self.context.new_page()
        
        # Set longer timeouts for slow operations
        self.page.set_default_timeout(30000)  # 30 seconds
        
    async def teardown(self):
        """Cleanup browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    def _log_request(self, request):
        """Log HTTP requests"""
        print(f"🔄 REQUEST: {request.method} {request.url}")
        
    def _log_response(self, response):
        """Log HTTP responses"""
        status_emoji = "✅" if response.status < 400 else "❌"
        print(f"{status_emoji} RESPONSE: {response.status} {response.url}")
        
    async def _log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
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
        
    async def test_01_homepage_accessibility(self):
        """Test homepage loads and is accessible"""
        test_name = "Homepage Accessibility"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Navigate to homepage
            response = await self.page.goto(self.base_url)
            
            # Check response status
            if response.status >= 400:
                raise Exception(f"HTTP {response.status}: {response.status_text}")
            
            # Wait for page to load
            await self.page.wait_for_load_state('networkidle')
            
            # Check page title
            title = await self.page.title()
            print(f"   Page title: {title}")
            
            # Check for critical elements
            body = await self.page.query_selector('body')
            if not body:
                raise Exception("No body element found")
            
            # Check for navigation
            nav_elements = await self.page.query_selector_all('nav, .navbar, .navigation')
            print(f"   Navigation elements found: {len(nav_elements)}")
            
            # Check for main content
            main_content = await self.page.query_selector('main, .main-content, .content')
            if main_content:
                print("   ✅ Main content area found")
            else:
                print("   ⚠️ No main content area found")
            
            # Take screenshot
            await self.page.screenshot(path='test_results/homepage_screenshot.png')
            
            await self._log_test_result(test_name, True, {
                'url': self.page.url,
                'title': title,
                'status_code': response.status,
                'nav_elements': len(nav_elements)
            })
            
        except Exception as e:
            await self._log_test_result(test_name, False, {'error': str(e)})
            # Take error screenshot
            await self.page.screenshot(path='test_results/homepage_error.png')
    
    async def test_02_authentication_flow(self):
        """Test user authentication"""
        test_name = "Authentication Flow"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Look for login elements
            login_links = await self.page.query_selector_all('a[href*="login"], .login-link, #login')
            login_forms = await self.page.query_selector_all('form[action*="login"], .login-form')
            
            print(f"   Login links found: {len(login_links)}")
            print(f"   Login forms found: {len(login_forms)}")
            
            # Check if already logged in
            logout_elements = await self.page.query_selector_all('a[href*="logout"], .logout')
            user_menu = await self.page.query_selector_all('.user-menu, .profile-menu')
            
            if logout_elements or user_menu:
                print("   ✅ User appears to be logged in")
                auth_status = "logged_in"
            elif login_links or login_forms:
                print("   ℹ️ Login interface available")
                auth_status = "login_available"
                
                # Try to find and click login link
                if login_links:
                    await login_links[0].click()
                    await self.page.wait_for_load_state('networkidle')
                    
                    # Check if login form appeared
                    username_field = await self.page.query_selector('input[name="username"], input[name="email"], #id_username')
                    password_field = await self.page.query_selector('input[name="password"], input[type="password"], #id_password')
                    
                    if username_field and password_field:
                        print("   ✅ Login form fields found")
                    else:
                        print("   ⚠️ Login form fields not found")
            else:
                print("   ⚠️ No authentication interface found")
                auth_status = "no_auth"
            
            await self._log_test_result(test_name, True, {
                'auth_status': auth_status,
                'login_links': len(login_links),
                'login_forms': len(login_forms)
            })
            
        except Exception as e:
            await self._log_test_result(test_name, False, {'error': str(e)})
    
    async def test_03_ocr_upload_interface(self):
        """Test OCR upload interface accessibility"""
        test_name = "OCR Upload Interface"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Navigate to OCR upload page
            ocr_url = f"{self.base_url}/ocr/upload/"
            response = await self.page.goto(ocr_url)
            
            print(f"   OCR URL response: {response.status}")
            
            # Wait for page load
            await self.page.wait_for_load_state('networkidle')
            
            # Check current URL (might be redirected)
            current_url = self.page.url
            print(f"   Current URL: {current_url}")
            
            # Look for OCR-related elements
            upload_forms = await self.page.query_selector_all('form[enctype*="multipart"], .upload-form')
            file_inputs = await self.page.query_selector_all('input[type="file"]')
            upload_buttons = await self.page.query_selector_all('button[type="submit"], .upload-btn, .btn-upload')
            
            print(f"   Upload forms: {len(upload_forms)}")
            print(f"   File inputs: {len(file_inputs)}")
            print(f"   Upload buttons: {len(upload_buttons)}")
            
            # Check for drag-and-drop areas
            dropzones = await self.page.query_selector_all('.dropzone, .drag-drop, [data-dropzone]')
            print(f"   Dropzones: {len(dropzones)}")
            
            # Check for progress indicators
            progress_elements = await self.page.query_selector_all('.progress, .progress-bar, .upload-progress')
            print(f"   Progress elements: {len(progress_elements)}")
            
            # Take screenshot of OCR interface
            await self.page.screenshot(path='test_results/ocr_interface.png')
            
            # Determine if OCR interface is functional
            ocr_functional = len(file_inputs) > 0 or len(dropzones) > 0
            
            await self._log_test_result(test_name, ocr_functional, {
                'ocr_url': ocr_url,
                'current_url': current_url,
                'response_status': response.status,
                'upload_forms': len(upload_forms),
                'file_inputs': len(file_inputs),
                'functional': ocr_functional
            })
            
        except Exception as e:
            await self._log_test_result(test_name, False, {'error': str(e)})
    
    async def test_04_navigation_links(self):
        """Test all navigation links"""
        test_name = "Navigation Links"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Go back to homepage
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Find all navigation links
            nav_links = await self.page.query_selector_all('nav a, .navbar a, .menu a, .navigation a')
            
            print(f"   Found {len(nav_links)} navigation links")
            
            working_links = 0
            broken_links = 0
            link_results = []
            
            for i, link in enumerate(nav_links[:10]):  # Test first 10 links
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    
                    if not href or href.startswith('#') or href.startswith('javascript:'):
                        continue
                    
                    print(f"   Testing link {i+1}: {text} -> {href}")
                    
                    # Click link and check response
                    await link.click()
                    await self.page.wait_for_load_state('networkidle', timeout=10000)
                    
                    current_url = self.page.url
                    
                    # Check if page loaded successfully
                    error_indicators = await self.page.query_selector_all('.error, .not-found, .404')
                    
                    if len(error_indicators) == 0:
                        working_links += 1
                        link_results.append({'text': text, 'href': href, 'status': 'working'})
                        print(f"     ✅ Link working")
                    else:
                        broken_links += 1
                        link_results.append({'text': text, 'href': href, 'status': 'error'})
                        print(f"     ❌ Link shows error page")
                    
                    # Go back to homepage for next test
                    await self.page.goto(self.base_url)
                    await self.page.wait_for_load_state('networkidle')
                    
                except Exception as link_error:
                    broken_links += 1
                    link_results.append({'text': text or 'Unknown', 'href': href or 'Unknown', 'status': 'exception', 'error': str(link_error)})
                    print(f"     ❌ Link error: {link_error}")
            
            success_rate = working_links / (working_links + broken_links) if (working_links + broken_links) > 0 else 0
            
            await self._log_test_result(test_name, success_rate > 0.5, {
                'total_links': len(nav_links),
                'tested_links': working_links + broken_links,
                'working_links': working_links,
                'broken_links': broken_links,
                'success_rate': success_rate,
                'link_details': link_results
            })
            
        except Exception as e:
            await self._log_test_result(test_name, False, {'error': str(e)})
    
    async def test_05_responsive_design(self):
        """Test responsive design on different screen sizes"""
        test_name = "Responsive Design"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Test different viewport sizes
            viewports = [
                {'width': 1920, 'height': 1080, 'name': 'Desktop Large'},
                {'width': 1366, 'height': 768, 'name': 'Desktop Standard'},
                {'width': 768, 'height': 1024, 'name': 'Tablet'},
                {'width': 375, 'height': 667, 'name': 'Mobile'}
            ]
            
            responsive_results = []
            
            for viewport in viewports:
                print(f"   Testing {viewport['name']} ({viewport['width']}x{viewport['height']})")
                
                # Set viewport
                await self.page.set_viewport_size(viewport['width'], viewport['height'])
                
                # Reload page
                await self.page.reload()
                await self.page.wait_for_load_state('networkidle')
                
                # Check for mobile menu indicators
                mobile_menu = await self.page.query_selector_all('.mobile-menu, .hamburger, .menu-toggle')
                
                # Check for responsive classes
                responsive_elements = await self.page.query_selector_all('[class*="col-"], [class*="responsive"], [class*="mobile"]')
                
                # Take screenshot
                screenshot_name = f"test_results/responsive_{viewport['name'].lower().replace(' ', '_')}.png"
                await self.page.screenshot(path=screenshot_name)
                
                responsive_results.append({
                    'viewport': viewport['name'],
                    'size': f"{viewport['width']}x{viewport['height']}",
                    'mobile_menu_elements': len(mobile_menu),
                    'responsive_elements': len(responsive_elements)
                })
                
                print(f"     Mobile menu elements: {len(mobile_menu)}")
                print(f"     Responsive elements: {len(responsive_elements)}")
            
            # Reset to default viewport
            await self.page.set_viewport_size(1920, 1080)
            
            await self._log_test_result(test_name, True, {
                'viewports_tested': len(viewports),
                'results': responsive_results
            })
            
        except Exception as e:
            await self._log_test_result(test_name, False, {'error': str(e)})
    
    async def test_06_javascript_errors(self):
        """Test for JavaScript errors"""
        test_name = "JavaScript Errors"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            js_errors = []
            console_messages = []
            
            # Listen for console messages
            def handle_console(msg):
                console_messages.append({
                    'type': msg.type,
                    'text': msg.text,
                    'location': msg.location
                })
                if msg.type == 'error':
                    js_errors.append(msg.text)
                    print(f"   ❌ JS Error: {msg.text}")
                elif msg.type == 'warning':
                    print(f"   ⚠️ JS Warning: {msg.text}")
            
            self.page.on('console', handle_console)
            
            # Navigate and interact with page
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Try to trigger JavaScript by interacting with elements
            clickable_elements = await self.page.query_selector_all('button, .btn, a[href="#"]')
            
            for i, element in enumerate(clickable_elements[:5]):  # Test first 5 clickable elements
                try:
                    await element.click()
                    await self.page.wait_for_timeout(1000)  # Wait for any JS to execute
                except Exception:
                    pass  # Ignore click errors, we're just testing for JS errors
            
            # Check for network errors
            failed_requests = []
            
            def handle_request_failed(request):
                failed_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'failure': request.failure
                })
                print(f"   ❌ Request failed: {request.url}")
            
            self.page.on('requestfailed', handle_request_failed)
            
            await self._log_test_result(test_name, len(js_errors) == 0, {
                'js_errors': js_errors,
                'console_messages': len(console_messages),
                'failed_requests': failed_requests,
                'error_count': len(js_errors)
            })
            
        except Exception as e:
            await self._log_test_result(test_name, False, {'error': str(e)})
    
    async def test_07_performance_metrics(self):
        """Test page performance metrics"""
        test_name = "Performance Metrics"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Navigate with performance timing
            start_time = time.time()
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')
            load_time = time.time() - start_time
            
            # Get performance metrics
            performance_metrics = await self.page.evaluate('''() => {
                const navigation = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                    loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                    firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                    firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
                };
            }''')
            
            # Check resource loading
            resources = await self.page.evaluate('''() => {
                return performance.getEntriesByType('resource').map(r => ({
                    name: r.name,
                    duration: r.duration,
                    size: r.transferSize || 0
                }));
            }''')
            
            # Calculate metrics
            total_resources = len(resources)
            total_size = sum(r['size'] for r in resources)
            slow_resources = [r for r in resources if r['duration'] > 1000]  # > 1 second
            
            print(f"   Page load time: {load_time:.2f}s")
            print(f"   Total resources: {total_resources}")
            print(f"   Total size: {total_size / 1024:.2f} KB")
            print(f"   Slow resources: {len(slow_resources)}")
            
            # Performance thresholds
            performance_good = (
                load_time < 5.0 and  # Page loads in under 5 seconds
                len(slow_resources) < 5 and  # Less than 5 slow resources
                total_size < 5 * 1024 * 1024  # Less than 5MB total
            )
            
            await self._log_test_result(test_name, performance_good, {
                'load_time': load_time,
                'total_resources': total_resources,
                'total_size_kb': total_size / 1024,
                'slow_resources': len(slow_resources),
                'performance_metrics': performance_metrics,
                'performance_good': performance_good
            })
            
        except Exception as e:
            await self._log_test_result(test_name, False, {'error': str(e)})
    
    async def run_all_tests(self):
        """Run all E2E tests"""
        print("🚀 Starting Comprehensive FaktuLove E2E Tests")
        print("=" * 60)
        
        # Create results directory
        os.makedirs('test_results', exist_ok=True)
        
        await self.setup()
        
        try:
            # Run all tests
            await self.test_01_homepage_accessibility()
            await self.test_02_authentication_flow()
            await self.test_03_ocr_upload_interface()
            await self.test_04_navigation_links()
            await self.test_05_responsive_design()
            await self.test_06_javascript_errors()
            await self.test_07_performance_metrics()
            
        finally:
            await self.teardown()
        
        # Generate test report
        await self.generate_report()
    
    async def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
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
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'test_results': self.test_results
        }
        
        with open('test_results/e2e_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: test_results/e2e_test_report.json")
        print("🖼️ Screenshots saved to: test_results/")
        
        return report_data

async def main():
    """Main test runner"""
    tester = FaktuLoveE2ETests()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())