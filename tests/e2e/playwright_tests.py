#!/usr/bin/env python3
"""
Playwright E2E Tests for FaktuLove OCR
Advanced browser automation and testing
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ Playwright not available. Install with: pip install playwright && playwright install")
    exit(1)

class PlaywrightFaktuLoveTester:
    """Advanced Playwright testing for FaktuLove"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'base_url': base_url,
            'tests': [],
            'performance_metrics': {},
            'accessibility_issues': [],
            'security_findings': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
    async def run_all_tests(self):
        """Run comprehensive Playwright tests"""
        print("🎭 Starting Playwright comprehensive tests")
        
        async with async_playwright() as p:
            # Test with multiple browsers
            browsers = [
                ('chromium', p.chromium),
                ('firefox', p.firefox),
                ('webkit', p.webkit)
            ]
            
            for browser_name, browser_type in browsers:
                try:
                    print(f"\n🌐 Testing with {browser_name.upper()}")
                    browser = await browser_type.launch(headless=True)
                    await self._test_browser(browser, browser_name)
                    await browser.close()
                except Exception as e:
                    self._record_result(f"{browser_name} - Browser Launch", False, str(e))
                    print(f"❌ {browser_name} failed: {e}")
                    
        await self._generate_report()
        
    async def _test_browser(self, browser: Browser, browser_name: str):
        """Test with specific browser"""
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=f'FaktuLove-E2E-Test/{browser_name}'
        )
        
        page = await context.new_page()
        
        # Enable console logging
        page.on('console', lambda msg: print(f"🖥️ Console [{msg.type}]: {msg.text}"))
        page.on('pageerror', lambda error: print(f"💥 Page Error: {error}"))
        
        test_scenarios = [
            ('Page Load', self._test_page_load),
            ('Performance Metrics', self._test_performance),
            ('Network Analysis', self._test_network),
            ('JavaScript Execution', self._test_javascript),
            ('Form Interactions', self._test_forms),
            ('Navigation Flow', self._test_navigation),
            ('Mobile Responsiveness', self._test_mobile),
            ('Accessibility Audit', self._test_accessibility),
            ('Security Headers', self._test_security),
            ('Error Handling', self._test_error_handling),
            ('OCR Functionality', self._test_ocr_features),
            ('Admin Interface', self._test_admin_interface)
        ]
        
        for test_name, test_func in test_scenarios:
            full_name = f"{browser_name} - {test_name}"
            try:
                print(f"  🧪 Running: {test_name}")
                result = await test_func(page, browser_name)
                
                self._record_result(full_name, result['success'], result.get('message', ''))
                
                if result['success']:
                    print(f"    ✅ {test_name} - PASSED")
                else:
                    print(f"    ❌ {test_name} - FAILED: {result.get('message', '')}")
                    
            except Exception as e:
                self._record_result(full_name, False, f"Exception: {str(e)}")
                print(f"    💥 {test_name} - ERROR: {str(e)}")
                
        await context.close()
        
    async def _test_page_load(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test basic page loading"""
        try:
            start_time = time.time()
            response = await page.goto(self.base_url, wait_until='networkidle')
            load_time = time.time() - start_time
            
            status_code = response.status if response else 0
            title = await page.title()
            url = page.url
            
            # Check for error indicators
            content = await page.content()
            error_indicators = [
                'Server Error', 'Internal Server Error', 'NoReverseMatch',
                'TemplateDoesNotExist', 'ImportError', 'SyntaxError'
            ]
            
            has_errors = any(error in content for error in error_indicators)
            
            return {
                'success': status_code < 400 and not has_errors,
                'message': f"Status: {status_code}, Load time: {load_time:.2f}s, Title: '{title}'",
                'metrics': {
                    'load_time': load_time,
                    'status_code': status_code,
                    'title': title,
                    'url': url
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_performance(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test performance metrics"""
        try:
            # Enable performance monitoring
            await page.goto(self.base_url)
            
            # Get performance metrics
            metrics = await page.evaluate("""
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    return {
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                        firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || 0
                    };
                }
            """)
            
            # Store performance metrics
            self.results['performance_metrics'][browser_name] = metrics
            
            # Check if performance is acceptable
            dom_load_ok = metrics['domContentLoaded'] < 3000  # 3 seconds
            load_ok = metrics['loadComplete'] < 5000  # 5 seconds
            
            return {
                'success': dom_load_ok and load_ok,
                'message': f"DOM: {metrics['domContentLoaded']:.0f}ms, Load: {metrics['loadComplete']:.0f}ms",
                'metrics': metrics
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_network(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test network requests"""
        try:
            requests = []
            failed_requests = []
            
            async def handle_request(request):
                requests.append({
                    'url': request.url,
                    'method': request.method,
                    'resource_type': request.resource_type
                })
                
            async def handle_response(response):
                if response.status >= 400:
                    failed_requests.append({
                        'url': response.url,
                        'status': response.status,
                        'status_text': response.status_text
                    })
                    
            page.on('request', handle_request)
            page.on('response', handle_response)
            
            await page.goto(self.base_url, wait_until='networkidle')
            
            return {
                'success': len(failed_requests) == 0,
                'message': f"Requests: {len(requests)}, Failed: {len(failed_requests)}",
                'details': {
                    'total_requests': len(requests),
                    'failed_requests': failed_requests[:5],  # First 5 failures
                    'request_types': list(set(req['resource_type'] for req in requests))
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_javascript(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test JavaScript execution"""
        try:
            console_messages = []
            
            def handle_console(msg):
                console_messages.append({
                    'type': msg.type,
                    'text': msg.text,
                    'location': msg.location
                })
                
            page.on('console', handle_console)
            
            await page.goto(self.base_url, wait_until='networkidle')
            
            # Test basic JavaScript functionality
            js_result = await page.evaluate("() => 'JavaScript is working'")
            
            # Count errors and warnings
            errors = [msg for msg in console_messages if msg['type'] == 'error']
            warnings = [msg for msg in console_messages if msg['type'] == 'warning']
            
            return {
                'success': js_result == 'JavaScript is working' and len(errors) == 0,
                'message': f"JS Test: {js_result}, Errors: {len(errors)}, Warnings: {len(warnings)}",
                'console_messages': {
                    'errors': errors[:3],
                    'warnings': warnings[:3]
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_forms(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test form interactions"""
        try:
            await page.goto(self.base_url)
            
            # Find forms
            forms = await page.query_selector_all('form')
            inputs = await page.query_selector_all('input')
            
            # Check for CSRF tokens
            csrf_tokens = await page.query_selector_all('input[name="csrfmiddlewaretoken"]')
            
            return {
                'success': True,
                'message': f"Forms: {len(forms)}, Inputs: {len(inputs)}, CSRF tokens: {len(csrf_tokens)}",
                'form_data': {
                    'forms_count': len(forms),
                    'inputs_count': len(inputs),
                    'csrf_tokens': len(csrf_tokens)
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_navigation(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test navigation flow"""
        try:
            await page.goto(self.base_url)
            
            # Find navigation links
            links = await page.query_selector_all('a[href]')
            internal_links = []
            
            for link in links[:10]:  # Test first 10 links
                href = await link.get_attribute('href')
                if href and (href.startswith('/') or self.base_url in href):
                    internal_links.append(href)
                    
            # Test a few internal links
            working_links = 0
            for link in internal_links[:5]:  # Test first 5 internal links
                try:
                    if link.startswith('/'):
                        full_url = f"{self.base_url}{link}"
                    else:
                        full_url = link
                        
                    response = await page.goto(full_url, wait_until='domcontentloaded')
                    if response and response.status < 400:
                        working_links += 1
                        
                except Exception:
                    pass
                    
            return {
                'success': working_links > 0,
                'message': f"Internal links: {len(internal_links)}, Working: {working_links}",
                'navigation_data': {
                    'total_links': len(links),
                    'internal_links': len(internal_links),
                    'working_links': working_links
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_mobile(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test mobile responsiveness"""
        try:
            # Test different viewport sizes
            viewports = [
                {'width': 375, 'height': 667, 'name': 'iPhone'},
                {'width': 768, 'height': 1024, 'name': 'iPad'},
                {'width': 1920, 'height': 1080, 'name': 'Desktop'}
            ]
            
            responsive_results = []
            
            for viewport in viewports:
                await page.set_viewport_size(viewport['width'], viewport['height'])
                await page.goto(self.base_url)
                
                # Check if content fits viewport
                body_width = await page.evaluate('document.body.scrollWidth')
                viewport_width = viewport['width']
                
                fits_viewport = body_width <= viewport_width + 50  # Allow small margin
                
                responsive_results.append({
                    'viewport': viewport['name'],
                    'fits': fits_viewport,
                    'body_width': body_width,
                    'viewport_width': viewport_width
                })
                
            successful_viewports = sum(1 for result in responsive_results if result['fits'])
            
            return {
                'success': successful_viewports >= 2,  # At least 2 viewports should work
                'message': f"Responsive on {successful_viewports}/{len(viewports)} viewports",
                'responsive_data': responsive_results
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_accessibility(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test accessibility features"""
        try:
            await page.goto(self.base_url)
            
            # Check basic accessibility features
            title = await page.title()
            has_title = bool(title and title.strip())
            
            # Check for lang attribute
            html_lang = await page.get_attribute('html', 'lang')
            has_lang = bool(html_lang)
            
            # Check images for alt attributes
            images = await page.query_selector_all('img')
            images_with_alt = 0
            
            for img in images:
                alt = await img.get_attribute('alt')
                if alt is not None:
                    images_with_alt += 1
                    
            alt_ratio = images_with_alt / len(images) if images else 1
            
            # Check for headings structure
            headings = await page.query_selector_all('h1, h2, h3, h4, h5, h6')
            
            accessibility_issues = []
            if not has_title:
                accessibility_issues.append("Missing page title")
            if not has_lang:
                accessibility_issues.append("Missing lang attribute")
            if alt_ratio < 0.8:
                accessibility_issues.append(f"Low alt text coverage: {alt_ratio:.1%}")
            if len(headings) == 0:
                accessibility_issues.append("No heading structure found")
                
            self.results['accessibility_issues'].extend(accessibility_issues)
            
            return {
                'success': len(accessibility_issues) <= 2,  # Allow minor issues
                'message': f"A11y issues: {len(accessibility_issues)}, Alt coverage: {alt_ratio:.1%}",
                'accessibility_data': {
                    'has_title': has_title,
                    'has_lang': has_lang,
                    'alt_ratio': alt_ratio,
                    'headings_count': len(headings),
                    'issues': accessibility_issues
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_security(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test security headers and features"""
        try:
            response = await page.goto(self.base_url)
            
            if not response:
                return {'success': False, 'message': 'No response received'}
                
            headers = response.headers
            
            # Check for security headers
            security_headers = {
                'x-frame-options': headers.get('x-frame-options'),
                'x-content-type-options': headers.get('x-content-type-options'),
                'x-xss-protection': headers.get('x-xss-protection'),
                'content-security-policy': headers.get('content-security-policy'),
                'strict-transport-security': headers.get('strict-transport-security')
            }
            
            present_headers = {k: v for k, v in security_headers.items() if v}
            
            # Check for CSRF tokens
            csrf_tokens = await page.query_selector_all('input[name="csrfmiddlewaretoken"]')
            
            security_findings = []
            if len(present_headers) < 2:
                security_findings.append("Few security headers present")
            if len(csrf_tokens) == 0:
                security_findings.append("No CSRF tokens found")
                
            self.results['security_findings'].extend(security_findings)
            
            return {
                'success': len(security_findings) <= 1,  # Allow minor security issues
                'message': f"Security headers: {len(present_headers)}, CSRF tokens: {len(csrf_tokens)}",
                'security_data': {
                    'headers': present_headers,
                    'csrf_tokens': len(csrf_tokens),
                    'findings': security_findings
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_error_handling(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test error handling"""
        try:
            # Test 404 page
            response = await page.goto(f"{self.base_url}/nonexistent-page-12345/", wait_until='domcontentloaded')
            
            content = await page.content()
            content_lower = content.lower()
            
            # Check for proper error handling
            has_error_page = any(term in content_lower for term in ['404', 'not found', 'error'])
            
            # Check that sensitive information is not exposed
            has_sensitive_info = any(term in content for term in [
                'Traceback', 'SECRET_KEY', 'DATABASE_URL', '/home/', 'Exception:'
            ])
            
            return {
                'success': has_error_page and not has_sensitive_info,
                'message': f"Error page: {has_error_page}, Sensitive info: {has_sensitive_info}",
                'error_data': {
                    'has_error_page': has_error_page,
                    'has_sensitive_info': has_sensitive_info,
                    'status_code': response.status if response else 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_ocr_features(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test OCR-specific features"""
        try:
            # Try to access OCR upload page
            response = await page.goto(f"{self.base_url}/ocr/upload/", wait_until='domcontentloaded')
            
            content = await page.content()
            content_lower = content.lower()
            
            # Check for OCR-related content or authentication redirect
            ocr_indicators = ['upload', 'file', 'ocr', 'document']
            auth_indicators = ['login', 'authentication', 'sign in']
            
            has_ocr_content = any(indicator in content_lower for indicator in ocr_indicators)
            has_auth_redirect = any(indicator in content_lower for indicator in auth_indicators)
            
            # Either should have OCR content or be redirected to auth
            is_accessible = has_ocr_content or has_auth_redirect
            
            return {
                'success': is_accessible,
                'message': f"OCR accessible: {is_accessible}, Has OCR content: {has_ocr_content}, Auth redirect: {has_auth_redirect}",
                'ocr_data': {
                    'has_ocr_content': has_ocr_content,
                    'has_auth_redirect': has_auth_redirect,
                    'status_code': response.status if response else 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    async def _test_admin_interface(self, page: Page, browser_name: str) -> Dict[str, Any]:
        """Test admin interface"""
        try:
            # Try to access admin
            response = await page.goto(f"{self.base_url}/admin/", wait_until='domcontentloaded')
            
            content = await page.content()
            content_lower = content.lower()
            
            # Check for admin interface or login
            admin_indicators = ['django administration', 'admin', 'login']
            has_admin_interface = any(indicator in content_lower for indicator in admin_indicators)
            
            return {
                'success': has_admin_interface,
                'message': f"Admin interface accessible: {has_admin_interface}",
                'admin_data': {
                    'has_admin_interface': has_admin_interface,
                    'status_code': response.status if response else 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exception: {str(e)}'}
            
    def _record_result(self, test_name: str, success: bool, message: str):
        """Record test result"""
        self.results['tests'].append({
            'name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        self.results['summary']['total'] += 1
        if success:
            self.results['summary']['passed'] += 1
        else:
            self.results['summary']['failed'] += 1
            
    async def _generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Generating Playwright test report...")
        
        # Save detailed JSON report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"playwright_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        # Generate HTML report
        html_report = self._generate_html_report()
        html_file = f"playwright_test_report_{timestamp}.html"
        
        with open(html_file, 'w') as f:
            f.write(html_report)
            
        # Print summary
        summary = self.results['summary']
        print(f"\n{'='*60}")
        print(f"🎭 PLAYWRIGHT TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {(summary['passed']/summary['total']*100):.1f}%")
        print(f"\nReports saved:")
        print(f"- JSON: {report_file}")
        print(f"- HTML: {html_file}")
        
        if self.results['accessibility_issues']:
            print(f"\n♿ Accessibility Issues:")
            for issue in self.results['accessibility_issues'][:5]:
                print(f"- {issue}")
                
        if self.results['security_findings']:
            print(f"\n🛡️ Security Findings:")
            for finding in self.results['security_findings'][:5]:
                print(f"- {finding}")
                
        print(f"{'='*60}")
        
        return {
            'json_report': report_file,
            'html_report': html_file,
            'summary': summary
        }
        
    def _generate_html_report(self) -> str:
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Playwright FaktuLove Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        .metric h3 {{ margin: 0; font-size: 2em; color: #333; }}
        .metric p {{ margin: 5px 0 0 0; color: #666; }}
        .test-result {{ margin: 15px 0; padding: 15px; border-radius: 8px; border-left: 4px solid; }}
        .success {{ background: #d4edda; border-left-color: #28a745; }}
        .failure {{ background: #f8d7da; border-left-color: #dc3545; }}
        .test-name {{ font-weight: bold; margin-bottom: 5px; }}
        .test-message {{ color: #666; }}
        .timestamp {{ color: #999; font-size: 0.9em; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .performance-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .performance-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 Playwright FaktuLove Test Report</h1>
            <p><strong>Base URL:</strong> {self.results['base_url']}</p>
            <p><strong>Generated:</strong> {self.results['timestamp']}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <h3>{self.results['summary']['total']}</h3>
                <p>Total Tests</p>
            </div>
            <div class="metric">
                <h3 style="color: #28a745">{self.results['summary']['passed']}</h3>
                <p>Passed</p>
            </div>
            <div class="metric">
                <h3 style="color: #dc3545">{self.results['summary']['failed']}</h3>
                <p>Failed</p>
            </div>
            <div class="metric">
                <h3>{(self.results['summary']['passed']/self.results['summary']['total']*100):.1f}%</h3>
                <p>Success Rate</p>
            </div>
        </div>
"""
        
        # Performance metrics section
        if self.results['performance_metrics']:
            html += """
        <div class="section">
            <h2>⚡ Performance Metrics</h2>
            <div class="performance-grid">
"""
            for browser, metrics in self.results['performance_metrics'].items():
                html += f"""
                <div class="performance-card">
                    <h4>{browser.title()}</h4>
                    <p><strong>DOM Load:</strong> {metrics.get('domContentLoaded', 0):.0f}ms</p>
                    <p><strong>Full Load:</strong> {metrics.get('loadComplete', 0):.0f}ms</p>
                    <p><strong>First Paint:</strong> {metrics.get('firstPaint', 0):.0f}ms</p>
                </div>
"""
            html += """
            </div>
        </div>
"""
        
        # Test results section
        html += """
        <div class="section">
            <h2>📋 Test Results</h2>
"""
        
        for test in self.results['tests']:
            status_class = 'success' if test['success'] else 'failure'
            status_icon = '✅' if test['success'] else '❌'
            
            html += f"""
            <div class="test-result {status_class}">
                <div class="test-name">{status_icon} {test['name']}</div>
                <div class="test-message">{test['message']}</div>
                <div class="timestamp">{test['timestamp']}</div>
            </div>
"""
        
        # Issues sections
        if self.results['accessibility_issues']:
            html += """
        <div class="section">
            <h2>♿ Accessibility Issues</h2>
            <ul>
"""
            for issue in self.results['accessibility_issues']:
                html += f"<li>{issue}</li>"
            html += """
            </ul>
        </div>
"""
        
        if self.results['security_findings']:
            html += """
        <div class="section">
            <h2>🛡️ Security Findings</h2>
            <ul>
"""
            for finding in self.results['security_findings']:
                html += f"<li>{finding}</li>"
            html += """
            </ul>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        return html


async def main():
    """Main function to run Playwright tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FaktuLove Playwright E2E Tests')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL to test')
    
    args = parser.parse_args()
    
    # Run Playwright tests
    tester = PlaywrightFaktuLoveTester(args.url)
    await tester.run_all_tests()


if __name__ == '__main__':
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not available. Install with:")
        print("pip install playwright")
        print("playwright install")
        exit(1)
        
    asyncio.run(main())