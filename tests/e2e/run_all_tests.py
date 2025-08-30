#!/usr/bin/env python3
"""
Master Test Runner for FaktuLove OCR
Runs all E2E tests (Playwright, Selenium, Cypress) and generates comprehensive report
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class MasterTestRunner:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        self.start_time = datetime.now()
        
    def setup_test_environment(self):
        """Setup test environment and dependencies"""
        print("🔧 Setting up test environment...")
        
        # Create test results directory
        os.makedirs('test_results', exist_ok=True)
        
        # Check if server is running
        try:
            import requests
            response = requests.get(self.base_url, timeout=5)
            print(f"✅ Server is running (Status: {response.status_code})")
            return True
        except Exception as e:
            print(f"❌ Server not accessible: {e}")
            return False
    
    def install_dependencies(self):
        """Install required test dependencies"""
        print("📦 Installing test dependencies...")
        
        dependencies = [
            'playwright',
            'selenium',
            'requests',
            'pytest',
            'pytest-asyncio'
        ]
        
        for dep in dependencies:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                             check=True, capture_output=True)
                print(f"✅ {dep} installed")
            except subprocess.CalledProcessError:
                print(f"⚠️ Failed to install {dep}")
        
        # Install Playwright browsers
        try:
            subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], 
                         check=True, capture_output=True)
            print("✅ Playwright browsers installed")
        except subprocess.CalledProcessError:
            print("⚠️ Failed to install Playwright browsers")
    
    async def run_playwright_tests(self):
        """Run Playwright E2E tests"""
        print("\n🎭 Running Playwright Tests...")
        print("-" * 40)
        
        try:
            # Import and run Playwright tests
            from playwright_comprehensive_tests import FaktuLoveE2ETests
            
            tester = FaktuLoveE2ETests(self.base_url)
            await tester.run_all_tests()
            
            # Load results
            with open('test_results/e2e_test_report.json', 'r') as f:
                self.test_results['playwright'] = json.load(f)
            
            print("✅ Playwright tests completed")
            
        except Exception as e:
            print(f"❌ Playwright tests failed: {e}")
            self.test_results['playwright'] = {
                'error': str(e),
                'summary': {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 1}
            }
    
    def run_selenium_tests(self):
        """Run Selenium tests"""
        print("\n🔍 Running Selenium Tests...")
        print("-" * 40)
        
        try:
            # Import and run Selenium tests
            from selenium_ocr_tests import SeleniumOCRTests
            
            tester = SeleniumOCRTests(self.base_url)
            tester.run_all_tests()
            
            # Load results
            with open('test_results/selenium_test_report.json', 'r') as f:
                self.test_results['selenium'] = json.load(f)
            
            print("✅ Selenium tests completed")
            
        except Exception as e:
            print(f"❌ Selenium tests failed: {e}")
            self.test_results['selenium'] = {
                'error': str(e),
                'summary': {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 1}
            }
    
    def run_cypress_tests(self):
        """Run Cypress tests"""
        print("\n🌲 Running Cypress Tests...")
        print("-" * 40)
        
        try:
            # Check if Cypress is available
            cypress_config = {
                "e2e": {
                    "baseUrl": self.base_url,
                    "supportFile": False,
                    "video": False,
                    "screenshotOnRunFailure": True,
                    "viewportWidth": 1920,
                    "viewportHeight": 1080
                }
            }
            
            # Write Cypress config
            with open('cypress.config.js', 'w') as f:
                f.write(f"""
const {{ defineConfig }} = require('cypress');

module.exports = defineConfig({{
  e2e: {{
    baseUrl: '{self.base_url}',
    supportFile: false,
    video: false,
    screenshotOnRunFailure: true,
    viewportWidth: 1920,
    viewportHeight: 1080,
    setupNodeEvents(on, config) {{
      on('task', {{
        generateCypressReport() {{
          console.log('Cypress tests completed');
          return null;
        }}
      }});
    }}
  }}
}});
""")
            
            # Try to run Cypress (if installed)
            result = subprocess.run([
                'npx', 'cypress', 'run', 
                '--spec', 'tests/e2e/cypress_integration_tests.js',
                '--headless'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Cypress tests completed")
                self.test_results['cypress'] = {
                    'summary': {'total_tests': 1, 'passed_tests': 1, 'failed_tests': 0},
                    'output': result.stdout
                }
            else:
                print("⚠️ Cypress tests had issues")
                self.test_results['cypress'] = {
                    'summary': {'total_tests': 1, 'passed_tests': 0, 'failed_tests': 1},
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except FileNotFoundError:
            print("ℹ️ Cypress not available (npm/npx not found)")
            self.test_results['cypress'] = {
                'summary': {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0},
                'skipped': 'Cypress not available'
            }
        except subprocess.TimeoutExpired:
            print("⚠️ Cypress tests timed out")
            self.test_results['cypress'] = {
                'summary': {'total_tests': 1, 'passed_tests': 0, 'failed_tests': 1},
                'error': 'Test execution timed out'
            }
        except Exception as e:
            print(f"❌ Cypress tests failed: {e}")
            self.test_results['cypress'] = {
                'error': str(e),
                'summary': {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 1}
            }
    
    def run_manual_verification_tests(self):
        """Run manual verification tests"""
        print("\n🔍 Running Manual Verification Tests...")
        print("-" * 40)
        
        manual_tests = []
        
        # Test 1: Server Response
        try:
            import requests
            response = requests.get(self.base_url, timeout=10)
            manual_tests.append({
                'test': 'Server Response',
                'success': response.status_code < 400,
                'details': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'response_time': response.elapsed.total_seconds()
                }
            })
            print(f"✅ Server responds with {response.status_code}")
        except Exception as e:
            manual_tests.append({
                'test': 'Server Response',
                'success': False,
                'details': {'error': str(e)}
            })
            print(f"❌ Server not responding: {e}")
        
        # Test 2: OCR Endpoint
        try:
            ocr_response = requests.get(f"{self.base_url}/ocr/upload/", timeout=10)
            manual_tests.append({
                'test': 'OCR Endpoint',
                'success': ocr_response.status_code < 500,  # Allow redirects
                'details': {
                    'status_code': ocr_response.status_code,
                    'final_url': ocr_response.url
                }
            })
            print(f"✅ OCR endpoint responds with {ocr_response.status_code}")
        except Exception as e:
            manual_tests.append({
                'test': 'OCR Endpoint',
                'success': False,
                'details': {'error': str(e)}
            })
            print(f"❌ OCR endpoint error: {e}")
        
        # Test 3: Static Files
        try:
            static_response = requests.get(f"{self.base_url}/static/", timeout=10)
            manual_tests.append({
                'test': 'Static Files',
                'success': static_response.status_code < 500,
                'details': {'status_code': static_response.status_code}
            })
            print(f"✅ Static files endpoint: {static_response.status_code}")
        except Exception as e:
            manual_tests.append({
                'test': 'Static Files',
                'success': False,
                'details': {'error': str(e)}
            })
            print(f"❌ Static files error: {e}")
        
        # Test 4: Admin Panel
        try:
            admin_response = requests.get(f"{self.base_url}/admin/", timeout=10)
            manual_tests.append({
                'test': 'Admin Panel',
                'success': admin_response.status_code < 500,
                'details': {'status_code': admin_response.status_code}
            })
            print(f"✅ Admin panel: {admin_response.status_code}")
        except Exception as e:
            manual_tests.append({
                'test': 'Admin Panel',
                'success': False,
                'details': {'error': str(e)}
            })
            print(f"❌ Admin panel error: {e}")
        
        # Calculate results
        passed_tests = sum(1 for test in manual_tests if test['success'])
        total_tests = len(manual_tests)
        
        self.test_results['manual'] = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests
            },
            'test_results': manual_tests
        }
        
        print(f"✅ Manual tests completed: {passed_tests}/{total_tests} passed")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        # Calculate overall statistics
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        framework_results = {}
        
        for framework, results in self.test_results.items():
            if 'summary' in results:
                summary = results['summary']
                framework_tests = summary.get('total_tests', 0)
                framework_passed = summary.get('passed_tests', 0)
                framework_failed = summary.get('failed_tests', 0)
                
                total_tests += framework_tests
                total_passed += framework_passed
                total_failed += framework_failed
                
                success_rate = (framework_passed / framework_tests * 100) if framework_tests > 0 else 0
                
                framework_results[framework] = {
                    'tests': framework_tests,
                    'passed': framework_passed,
                    'failed': framework_failed,
                    'success_rate': success_rate
                }
                
                status_emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
                print(f"{status_emoji} {framework.upper()}: {framework_passed}/{framework_tests} passed ({success_rate:.1f}%)")
            else:
                print(f"❌ {framework.upper()}: Error or skipped")
                framework_results[framework] = {'error': results.get('error', 'Unknown error')}
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed} ✅")
        print(f"   Failed: {total_failed} ❌")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Duration: {duration:.1f} seconds")
        
        # Determine overall status
        if overall_success_rate >= 80:
            overall_status = "✅ EXCELLENT"
        elif overall_success_rate >= 60:
            overall_status = "⚠️ GOOD"
        elif overall_success_rate >= 40:
            overall_status = "⚠️ NEEDS IMPROVEMENT"
        else:
            overall_status = "❌ CRITICAL ISSUES"
        
        print(f"\n🎯 OVERALL STATUS: {overall_status}")
        
        # Generate recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if total_failed > 0:
            print("   • Review failed tests and fix underlying issues")
        
        if 'playwright' in self.test_results and self.test_results['playwright'].get('summary', {}).get('failed_tests', 0) > 0:
            print("   • Check browser compatibility and JavaScript errors")
        
        if 'selenium' in self.test_results and self.test_results['selenium'].get('summary', {}).get('failed_tests', 0) > 0:
            print("   • Verify OCR upload functionality and form interactions")
        
        if overall_success_rate < 80:
            print("   • Consider implementing additional error handling")
            print("   • Review server configuration and dependencies")
        
        # Save comprehensive report
        comprehensive_report = {
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'overall_summary': {
                'total_tests': total_tests,
                'passed_tests': total_passed,
                'failed_tests': total_failed,
                'success_rate': overall_success_rate,
                'status': overall_status
            },
            'framework_results': framework_results,
            'detailed_results': self.test_results
        }
        
        with open('test_results/comprehensive_test_report.json', 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        # Generate HTML report
        self.generate_html_report(comprehensive_report)
        
        print(f"\n📄 Reports saved:")
        print(f"   • JSON: test_results/comprehensive_test_report.json")
        print(f"   • HTML: test_results/test_report.html")
        print(f"   • Screenshots: test_results/*.png")
        
        return comprehensive_report
    
    def generate_html_report(self, report_data):
        """Generate HTML test report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FaktuLove OCR - Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .status-excellent {{ color: #28a745; }}
        .status-good {{ color: #ffc107; }}
        .status-critical {{ color: #dc3545; }}
        .framework-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-box {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #ffc107, #dc3545); }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 FaktuLove OCR - Comprehensive Test Report</h1>
            <p>Generated: {report_data['timestamp']}</p>
            <p>Duration: {report_data['duration_seconds']:.1f} seconds</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Tests</h3>
                <h2>{report_data['overall_summary']['total_tests']}</h2>
            </div>
            <div class="stat-box">
                <h3>Passed</h3>
                <h2 class="success">{report_data['overall_summary']['passed_tests']}</h2>
            </div>
            <div class="stat-box">
                <h3>Failed</h3>
                <h2 class="error">{report_data['overall_summary']['failed_tests']}</h2>
            </div>
            <div class="stat-box">
                <h3>Success Rate</h3>
                <h2>{report_data['overall_summary']['success_rate']:.1f}%</h2>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {report_data['overall_summary']['success_rate']}%"></div>
        </div>
        
        <h2>Overall Status: <span class="status-{report_data['overall_summary']['status'].split()[1].lower()}">{report_data['overall_summary']['status']}</span></h2>
        
        <h2>Framework Results</h2>
"""
        
        for framework, results in report_data['framework_results'].items():
            if 'error' in results:
                html_content += f"""
        <div class="framework-section">
            <h3>❌ {framework.upper()}</h3>
            <p class="error">Error: {results['error']}</p>
        </div>
"""
            else:
                status_class = "success" if results['success_rate'] >= 80 else "warning" if results['success_rate'] >= 50 else "error"
                html_content += f"""
        <div class="framework-section">
            <h3 class="{status_class}">{'✅' if results['success_rate'] >= 80 else '⚠️' if results['success_rate'] >= 50 else '❌'} {framework.upper()}</h3>
            <p>Tests: {results['tests']} | Passed: {results['passed']} | Failed: {results['failed']} | Success Rate: {results['success_rate']:.1f}%</p>
        </div>
"""
        
        html_content += """
        <h2>Detailed Results</h2>
        <pre>""" + json.dumps(report_data['detailed_results'], indent=2) + """</pre>
        
        <footer style="text-align: center; margin-top: 30px; color: #666;">
            <p>Generated by FaktuLove OCR Test Suite</p>
        </footer>
    </div>
</body>
</html>
"""
        
        with open('test_results/test_report.html', 'w') as f:
            f.write(html_content)
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("🚀 FaktuLove OCR - Comprehensive Test Suite")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Cannot proceed without server running")
            return
        
        self.install_dependencies()
        
        # Run all test suites
        await self.run_playwright_tests()
        self.run_selenium_tests()
        self.run_cypress_tests()
        self.run_manual_verification_tests()
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report()
        
        return report

async def main():
    """Main test runner"""
    runner = MasterTestRunner()
    await runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())