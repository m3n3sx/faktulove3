#!/usr/bin/env python3
"""
Production Validation Runner
Executes all production critical fixes validation tests
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

class ProductionValidationRunner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {
            'deployment_checklist': {},
            'functionality_validation': {},
            'performance_monitoring': {},
            'overall_status': 'unknown',
            'timestamp': time.time(),
            'summary': {}
        }
        
    def run_deployment_checklist(self):
        """Run deployment checklist"""
        print("🔍 Running deployment checklist...")
        
        try:
            result = subprocess.run([
                sys.executable, 
                'scripts/production_deployment_checklist.py'
            ], capture_output=True, text=True, timeout=300)
            
            self.results['deployment_checklist'] = {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            # Try to load detailed results
            checklist_file = self.project_root / 'deployment_checklist_results.json'
            if checklist_file.exists():
                with open(checklist_file, 'r') as f:
                    detailed_results = json.load(f)
                    self.results['deployment_checklist']['detailed'] = detailed_results
            
            if result.returncode == 0:
                print("✅ Deployment checklist: PASSED")
            else:
                print("❌ Deployment checklist: FAILED")
                
        except subprocess.TimeoutExpired:
            print("⏰ Deployment checklist: TIMEOUT")
            self.results['deployment_checklist'] = {
                'exit_code': -1,
                'error': 'timeout',
                'success': False
            }
        except Exception as e:
            print(f"💥 Deployment checklist: ERROR - {e}")
            self.results['deployment_checklist'] = {
                'exit_code': -1,
                'error': str(e),
                'success': False
            }
    
    def run_functionality_validation(self):
        """Run functionality validation"""
        print("\n🧪 Running functionality validation...")
        
        try:
            # Check if selenium is available
            try:
                import selenium
                selenium_available = True
            except ImportError:
                selenium_available = False
                print("⚠️ Selenium not available, skipping browser tests")
            
            if selenium_available:
                result = subprocess.run([
                    sys.executable, 
                    'scripts/production_validation.py',
                    '--headless'
                ], capture_output=True, text=True, timeout=600)
                
                self.results['functionality_validation'] = {
                    'exit_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                }
                
                # Try to load detailed results
                validation_file = self.project_root / 'production_validation_results.json'
                if validation_file.exists():
                    with open(validation_file, 'r') as f:
                        detailed_results = json.load(f)
                        self.results['functionality_validation']['detailed'] = detailed_results
                
                if result.returncode == 0:
                    print("✅ Functionality validation: PASSED")
                else:
                    print("❌ Functionality validation: FAILED")
            else:
                self.results['functionality_validation'] = {
                    'exit_code': -1,
                    'error': 'selenium_not_available',
                    'success': False,
                    'skipped': True
                }
                print("⚠️ Functionality validation: SKIPPED (Selenium not available)")
                
        except subprocess.TimeoutExpired:
            print("⏰ Functionality validation: TIMEOUT")
            self.results['functionality_validation'] = {
                'exit_code': -1,
                'error': 'timeout',
                'success': False
            }
        except Exception as e:
            print(f"💥 Functionality validation: ERROR - {e}")
            self.results['functionality_validation'] = {
                'exit_code': -1,
                'error': str(e),
                'success': False
            }
    
    def run_performance_monitoring(self):
        """Run performance monitoring"""
        print("\n⚡ Running performance monitoring...")
        
        try:
            # Check if selenium is available
            try:
                import selenium
                selenium_available = True
            except ImportError:
                selenium_available = False
                print("⚠️ Selenium not available, skipping performance tests")
            
            if selenium_available:
                result = subprocess.run([
                    sys.executable, 
                    'scripts/performance_monitoring.py',
                    '--headless'
                ], capture_output=True, text=True, timeout=600)
                
                self.results['performance_monitoring'] = {
                    'exit_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                }
                
                # Try to load detailed results
                performance_file = self.project_root / 'performance_monitoring_report.json'
                if performance_file.exists():
                    with open(performance_file, 'r') as f:
                        detailed_results = json.load(f)
                        self.results['performance_monitoring']['detailed'] = detailed_results
                
                if result.returncode == 0:
                    print("✅ Performance monitoring: PASSED")
                else:
                    print("❌ Performance monitoring: FAILED")
            else:
                self.results['performance_monitoring'] = {
                    'exit_code': -1,
                    'error': 'selenium_not_available',
                    'success': False,
                    'skipped': True
                }
                print("⚠️ Performance monitoring: SKIPPED (Selenium not available)")
                
        except subprocess.TimeoutExpired:
            print("⏰ Performance monitoring: TIMEOUT")
            self.results['performance_monitoring'] = {
                'exit_code': -1,
                'error': 'timeout',
                'success': False
            }
        except Exception as e:
            print(f"💥 Performance monitoring: ERROR - {e}")
            self.results['performance_monitoring'] = {
                'exit_code': -1,
                'error': str(e),
                'success': False
            }
    
    def generate_summary(self):
        """Generate validation summary"""
        print("\n📊 Generating validation summary...")
        
        # Count successful tests
        tests = ['deployment_checklist', 'functionality_validation', 'performance_monitoring']
        successful_tests = 0
        total_tests = 0
        skipped_tests = 0
        
        for test in tests:
            if test in self.results:
                if self.results[test].get('skipped', False):
                    skipped_tests += 1
                else:
                    total_tests += 1
                    if self.results[test].get('success', False):
                        successful_tests += 1
        
        # Calculate success rate
        if total_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
        else:
            success_rate = 0
        
        # Determine overall status
        if success_rate >= 90:
            overall_status = 'excellent'
        elif success_rate >= 75:
            overall_status = 'good'
        elif success_rate >= 50:
            overall_status = 'acceptable'
        else:
            overall_status = 'needs_work'
        
        self.results['overall_status'] = overall_status
        self.results['summary'] = {
            'successful_tests': successful_tests,
            'total_tests': total_tests,
            'skipped_tests': skipped_tests,
            'success_rate': success_rate,
            'overall_status': overall_status
        }
        
        return success_rate >= 75  # 75% success rate required
    
    def print_final_report(self):
        """Print final validation report"""
        print("\n" + "=" * 70)
        print("🎯 PRODUCTION VALIDATION FINAL REPORT")
        print("=" * 70)
        
        summary = self.results['summary']
        
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"✅ Successful Tests: {summary['successful_tests']}")
        print(f"📊 Total Tests: {summary['total_tests']}")
        print(f"⏭️ Skipped Tests: {summary['skipped_tests']}")
        print(f"🎯 Overall Status: {summary['overall_status'].upper()}")
        
        # Detailed results
        print(f"\n📋 Test Results:")
        
        # Deployment Checklist
        deployment = self.results.get('deployment_checklist', {})
        if deployment.get('success'):
            print("✅ Deployment Checklist: PASSED")
        elif deployment.get('skipped'):
            print("⏭️ Deployment Checklist: SKIPPED")
        else:
            print("❌ Deployment Checklist: FAILED")
        
        # Functionality Validation
        functionality = self.results.get('functionality_validation', {})
        if functionality.get('success'):
            print("✅ Functionality Validation: PASSED")
        elif functionality.get('skipped'):
            print("⏭️ Functionality Validation: SKIPPED")
        else:
            print("❌ Functionality Validation: FAILED")
        
        # Performance Monitoring
        performance = self.results.get('performance_monitoring', {})
        if performance.get('success'):
            print("✅ Performance Monitoring: PASSED")
        elif performance.get('skipped'):
            print("⏭️ Performance Monitoring: SKIPPED")
        else:
            print("❌ Performance Monitoring: FAILED")
        
        # Production readiness
        is_ready = summary['success_rate'] >= 75
        
        print(f"\n{'🎉' if is_ready else '⚠️'} Production Readiness: {'READY' if is_ready else 'NOT READY'}")
        
        if not is_ready:
            print("\n💡 Recommendations:")
            print("   • Address failed tests before production deployment")
            print("   • Install selenium for complete validation: pip install selenium")
            print("   • Review detailed test outputs for specific issues")
        
        # Save complete results
        with open('production_validation_complete.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Complete results saved to: production_validation_complete.json")
        
        return is_ready
    
    def run_complete_validation(self):
        """Run complete production validation"""
        print("🚀 Starting Complete Production Validation")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all validation tests
        self.run_deployment_checklist()
        self.run_functionality_validation()
        self.run_performance_monitoring()
        
        # Generate summary and final report
        success = self.generate_summary()
        ready = self.print_final_report()
        
        print(f"\n⏱️ Total validation time: {time.time() - start_time:.1f}s")
        
        return ready

def main():
    """Main function"""
    runner = ProductionValidationRunner()
    
    try:
        ready = runner.run_complete_validation()
        sys.exit(0 if ready else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Production validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Production validation failed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()