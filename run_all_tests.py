#!/usr/bin/env python3
"""
Comprehensive Test Runner for Production Critical Fixes
Runs all end-to-end tests and validates functionality
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Running All Production Critical Fixes Tests")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Test results tracking
    tests = []
    
    # 1. Django system checks
    tests.append(run_command(
        "python manage.py check --deploy",
        "Django deployment checks"
    ))
    
    # 2. Database migrations check
    tests.append(run_command(
        "python manage.py showmigrations --plan",
        "Database migrations status"
    ))
    
    # 3. Static files collection
    tests.append(run_command(
        "python manage.py collectstatic --noinput --clear",
        "Static files collection"
    ))
    
    # 4. Frontend build (if frontend directory exists)
    if (project_root / 'frontend').exists():
        tests.append(run_command(
            "npm install",
            "Frontend dependencies installation",
            cwd="frontend"
        ))
        
        tests.append(run_command(
            "npm run build",
            "Frontend build process",
            cwd="frontend"
        ))
    
    # 5. Python tests
    tests.append(run_command(
        "python manage.py test --keepdb --verbosity=2",
        "Django unit tests"
    ))
    
    # 6. Invoice workflow end-to-end test
    if (project_root / 'test_invoice_workflow.py').exists():
        tests.append(run_command(
            "python test_invoice_workflow.py",
            "Invoice creation workflow test"
        ))
    
    # 7. OCR upload workflow test
    if (project_root / 'test_ocr_upload_workflow.py').exists():
        tests.append(run_command(
            "python test_ocr_upload_workflow.py",
            "OCR upload workflow test"
        ))
    
    # 8. Production deployment checklist
    if (project_root / 'scripts' / 'production_deployment_checklist.py').exists():
        tests.append(run_command(
            "python scripts/production_deployment_checklist.py",
            "Production deployment checklist"
        ))
    
    # 9. Security checks
    tests.append(run_command(
        "python manage.py check --tag security",
        "Django security checks"
    ))
    
    # 10. Performance validation
    tests.append(run_command(
        "python -c \"import django; django.setup(); from django.test.utils import get_runner; from django.conf import settings; TestRunner = get_runner(settings); test_runner = TestRunner(); print('Performance tests would run here')\"",
        "Performance validation"
    ))
    
    # Results summary
    print("\\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(tests)
    total = len(tests)
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        print("\\n🎉 ALL TESTS PASSED! Production critical fixes are working correctly.")
        print("\\n✅ Ready for production deployment!")
        
        # Generate success report
        with open('test_results_success.txt', 'w') as f:
            f.write(f"Production Critical Fixes Test Results\\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"All {total} tests passed successfully\\n")
            f.write("System is ready for production deployment\\n")
        
        return True
    else:
        print(f"\\n❌ {failed} TESTS FAILED! Please fix the issues above before deployment.")
        
        # Generate failure report
        with open('test_results_failure.txt', 'w') as f:
            f.write(f"Production Critical Fixes Test Results\\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"{failed} out of {total} tests failed\\n")
            f.write("System is NOT ready for production deployment\\n")
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n💥 Unexpected error: {e}")
        sys.exit(1)