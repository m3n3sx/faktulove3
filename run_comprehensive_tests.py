#!/usr/bin/env python3
"""
Comprehensive Test Runner for FaktuLove System Improvements
Runs all automated tests including unit, integration, e2e, performance, accessibility, and browser tests
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse


class ComprehensiveTestRunner:
    """Comprehensive test runner for all test suites"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {}
        self.project_root = Path(__file__).parent
        
        # Test suite configurations
        self.test_suites = {
            'unit': {
                'name': 'Unit Tests',
                'command': 'python -m pytest faktury/tests/test_comprehensive_unit_tests.py -v --tb=short',
                'timeout': 300,
                'required': True
            },
            'integration': {
                'name': 'Integration Tests',
                'command': 'python -m pytest faktury/tests/test_comprehensive_integration_tests.py -v --tb=short',
                'timeout': 600,
                'required': True
            },
            'e2e': {
                'name': 'End-to-End Tests',
                'command': 'python -m pytest faktury/tests/test_comprehensive_e2e_tests.py -v --tb=short',
                'timeout': 900,
                'required': False
            },
            'performance': {
                'name': 'Performance Tests',
                'command': 'python -m pytest faktury/tests/test_comprehensive_performance_tests.py -v --tb=short',
                'timeout': 600,
                'required': True
            },
            'accessibility': {
                'name': 'Accessibility Tests',
                'command': 'python -m pytest faktury/tests/test_accessibility_compliance.py -v --tb=short',
                'timeout': 300,
                'required': False
            },
            'browser': {
                'name': 'Cross-Browser Tests',
                'command': 'python -m pytest faktury/tests/test_cross_browser_compatibility.py -v --tb=short',
                'timeout': 900,
                'required': False
            },
            'mobile': {
                'name': 'Mobile Device Tests',
                'command': 'python -m pytest faktury/tests/test_mobile_device_compatibility.py -v --tb=short',
                'timeout': 600,
                'required': False
            },
            'visual': {
                'name': 'Visual Regression Tests',
                'command': 'python -m pytest faktury/tests/test_visual_regression.py -v --tb=short',
                'timeout': 600,
                'required': False
            }
        }
    
    def setup_environment(self):
        """Set up test environment"""
        print("🔧 Setting up test environment...")
        
        # Change to project directory
        os.chdir(self.project_root)
        
        # Check if virtual environment is activated
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("⚠️  Warning: Virtual environment not detected")
        
        # Create test results directory
        results_dir = Path('test_results')
        results_dir.mkdir(exist_ok=True)
        
        # Set environment variables for testing
        os.environ['DJANGO_SETTINGS_MODULE'] = 'faktulove.settings'
        os.environ['TESTING'] = 'True'
        
        print("✅ Environment setup complete")
    
    def run_django_checks(self):
        """Run Django system checks"""
        print("🔍 Running Django system checks...")
        
        try:
            result = subprocess.run(
                ['python', 'manage.py', 'check', '--deploy'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Django system checks passed")
                return True
            else:
                print(f"❌ Django system checks failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Django system checks timed out")
            return False
        except Exception as e:
            print(f"💥 Django system checks error: {e}")
            return False
    
    def run_test_suite(self, suite_name: str, suite_config: Dict) -> Dict:
        """Run a specific test suite"""
        print(f"🧪 Running {suite_config['name']}...")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                suite_config['command'].split(),
                capture_output=True,
                text=True,
                timeout=suite_config['timeout'],
                cwd=self.project_root
            )
            
            duration = time.time() - start_time
            
            # Parse pytest output for test counts
            output_lines = result.stdout.split('\n')
            test_summary = self._parse_pytest_output(output_lines)
            
            suite_result = {
                'name': suite_config['name'],
                'passed': result.returncode == 0,
                'duration': duration,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'required': suite_config['required'],
                **test_summary
            }
            
            if suite_result['passed']:
                print(f"✅ {suite_config['name']} - PASSED ({duration:.1f}s)")
            else:
                print(f"❌ {suite_config['name']} - FAILED ({duration:.1f}s)")
                if suite_config['required']:
                    print(f"   Error: {result.stderr[:200]}...")
            
            return suite_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏰ {suite_config['name']} - TIMEOUT ({duration:.1f}s)")
            
            return {
                'name': suite_config['name'],
                'passed': False,
                'duration': duration,
                'return_code': -1,
                'stdout': '',
                'stderr': 'Test suite timed out',
                'required': suite_config['required'],
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0
            }
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {suite_config['name']} - ERROR ({duration:.1f}s): {e}")
            
            return {
                'name': suite_config['name'],
                'passed': False,
                'duration': duration,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'required': suite_config['required'],
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0
            }
    
    def _parse_pytest_output(self, output_lines: List[str]) -> Dict:
        """Parse pytest output to extract test statistics"""
        stats = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0
        }
        
        for line in output_lines:
            if 'passed' in line and 'failed' in line:
                # Look for summary line like "5 passed, 2 failed, 1 skipped"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        try:
                            stats['passed_tests'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'failed' and i > 0:
                        try:
                            stats['failed_tests'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'skipped' and i > 0:
                        try:
                            stats['skipped_tests'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                
                stats['total_tests'] = stats['passed_tests'] + stats['failed_tests'] + stats['skipped_tests']
                break
        
        return stats
    
    def run_all_tests(self, suites_to_run: Optional[List[str]] = None):
        """Run all test suites"""
        self.start_time = time.time()
        
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        # Setup environment
        self.setup_environment()
        
        # Run Django checks first
        django_checks_passed = self.run_django_checks()
        
        # Determine which suites to run
        if suites_to_run:
            suites = {k: v for k, v in self.test_suites.items() if k in suites_to_run}
        else:
            suites = self.test_suites
        
        # Run test suites
        for suite_name, suite_config in suites.items():
            self.results[suite_name] = self.run_test_suite(suite_name, suite_config)
        
        self.end_time = time.time()
        
        # Generate report
        self.generate_report(django_checks_passed)
    
    def generate_report(self, django_checks_passed: bool):
        """Generate comprehensive test report"""
        total_duration = self.end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        # Overall statistics
        total_suites = len(self.results)
        passed_suites = sum(1 for r in self.results.values() if r['passed'])
        failed_suites = total_suites - passed_suites
        
        total_tests = sum(r['total_tests'] for r in self.results.values())
        passed_tests = sum(r['passed_tests'] for r in self.results.values())
        failed_tests = sum(r['failed_tests'] for r in self.results.values())
        skipped_tests = sum(r['skipped_tests'] for r in self.results.values())
        
        print(f"Django System Checks: {'✅ PASSED' if django_checks_passed else '❌ FAILED'}")
        print(f"Total Test Suites: {total_suites}")
        print(f"Passed Suites: {passed_suites} ✅")
        print(f"Failed Suites: {failed_suites} ❌")
        print(f"Total Duration: {total_duration:.1f}s")
        print()
        
        print(f"Total Individual Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests} ✅")
        print(f"Failed Tests: {failed_tests} ❌")
        print(f"Skipped Tests: {skipped_tests} ⏭️")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n" + "-" * 60)
        print("📋 DETAILED RESULTS BY SUITE")
        print("-" * 60)
        
        for suite_name, result in self.results.items():
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            required = "🔴 REQUIRED" if result['required'] else "🟡 OPTIONAL"
            
            print(f"{result['name']}: {status} {required}")
            print(f"  Duration: {result['duration']:.1f}s")
            print(f"  Tests: {result['total_tests']} total, {result['passed_tests']} passed, {result['failed_tests']} failed, {result['skipped_tests']} skipped")
            
            if not result['passed'] and result['stderr']:
                print(f"  Error: {result['stderr'][:100]}...")
            print()
        
        # Quality assessment
        print("-" * 60)
        print("🎯 QUALITY ASSESSMENT")
        print("-" * 60)
        
        required_suites = [r for r in self.results.values() if r['required']]
        required_passed = sum(1 for r in required_suites if r['passed'])
        required_total = len(required_suites)
        
        if required_total > 0:
            required_success_rate = (required_passed / required_total) * 100
        else:
            required_success_rate = 100
        
        overall_quality = self._assess_quality(
            django_checks_passed, required_success_rate, success_rate if total_tests > 0 else 0
        )
        
        print(f"Required Suites: {required_passed}/{required_total} passed ({required_success_rate:.1f}%)")
        print(f"Overall Quality: {overall_quality}")
        
        # Recommendations
        print("\n" + "-" * 60)
        print("💡 RECOMMENDATIONS")
        print("-" * 60)
        
        recommendations = self._generate_recommendations(
            django_checks_passed, required_success_rate, failed_suites
        )
        
        for rec in recommendations:
            print(f"• {rec}")
        
        # Save detailed report
        self._save_detailed_report(django_checks_passed, total_duration)
        
        # Exit code
        if not django_checks_passed or required_success_rate < 100:
            print(f"\n❌ CRITICAL ISSUES DETECTED - System not ready for production")
            return False
        elif failed_suites > 0:
            print(f"\n⚠️  SOME OPTIONAL TESTS FAILED - Review before production deployment")
            return True
        else:
            print(f"\n🎉 ALL TESTS PASSED - System ready for production!")
            return True
    
    def _assess_quality(self, django_checks: bool, required_rate: float, overall_rate: float) -> str:
        """Assess overall quality based on test results"""
        if not django_checks:
            return "❌ CRITICAL - Django checks failed"
        elif required_rate < 100:
            return "❌ CRITICAL - Required tests failed"
        elif overall_rate >= 95:
            return "🟢 EXCELLENT"
        elif overall_rate >= 90:
            return "🟡 GOOD"
        elif overall_rate >= 80:
            return "🟠 ACCEPTABLE"
        else:
            return "🔴 NEEDS IMPROVEMENT"
    
    def _generate_recommendations(self, django_checks: bool, required_rate: float, failed_suites: int) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if not django_checks:
            recommendations.append("Fix Django system check issues before deployment")
        
        if required_rate < 100:
            recommendations.append("Fix all required test failures before production")
        
        if failed_suites > 0:
            recommendations.append("Review and fix optional test failures")
        
        recommendations.extend([
            "Run tests in CI/CD pipeline for every deployment",
            "Monitor performance metrics in production",
            "Conduct security audit before go-live",
            "Perform user acceptance testing",
            "Set up production monitoring and alerting"
        ])
        
        return recommendations
    
    def _save_detailed_report(self, django_checks: bool, total_duration: float):
        """Save detailed JSON report"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'django_checks_passed': django_checks,
            'total_duration': total_duration,
            'test_suites': self.results,
            'summary': {
                'total_suites': len(self.results),
                'passed_suites': sum(1 for r in self.results.values() if r['passed']),
                'failed_suites': sum(1 for r in self.results.values() if not r['passed']),
                'total_tests': sum(r['total_tests'] for r in self.results.values()),
                'passed_tests': sum(r['passed_tests'] for r in self.results.values()),
                'failed_tests': sum(r['failed_tests'] for r in self.results.values()),
                'skipped_tests': sum(r['skipped_tests'] for r in self.results.values())
            }
        }
        
        report_file = Path('test_results') / f'comprehensive_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run comprehensive test suite')
    parser.add_argument(
        '--suites',
        nargs='+',
        choices=list(ComprehensiveTestRunner().test_suites.keys()),
        help='Specific test suites to run'
    )
    parser.add_argument(
        '--list-suites',
        action='store_true',
        help='List available test suites'
    )
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    
    if args.list_suites:
        print("Available test suites:")
        for suite_name, suite_config in runner.test_suites.items():
            required = "REQUIRED" if suite_config['required'] else "OPTIONAL"
            print(f"  {suite_name}: {suite_config['name']} ({required})")
        return
    
    try:
        success = runner.run_all_tests(args.suites)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()