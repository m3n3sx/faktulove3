#!/usr/bin/env python3
"""
Simple test runner for Selenium OCR tests
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run Selenium tests with proper setup"""
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Create test results directory
    test_results_dir = project_root / 'test_results'
    test_results_dir.mkdir(exist_ok=True)
    
    print("🚀 Starting Selenium OCR Tests")
    print("=" * 50)
    
    # Check if Chrome/Chromium is available
    chrome_available = False
    for chrome_cmd in ['google-chrome', 'chromium-browser', 'chromium']:
        try:
            result = subprocess.run([chrome_cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Found Chrome: {result.stdout.strip()}")
                chrome_available = True
                break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    if not chrome_available:
        print("❌ Chrome/Chromium not found. Please install Chrome or Chromium.")
        print("   Ubuntu/Debian: sudo apt install chromium-browser")
        print("   Or download Chrome from: https://www.google.com/chrome/")
        return 1
    
    # Check if selenium is installed
    try:
        import selenium
        print(f"✅ Selenium version: {selenium.__version__}")
    except ImportError:
        print("❌ Selenium not installed. Installing...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'selenium'], check=True)
            print("✅ Selenium installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Selenium")
            return 1
    
    # Check if requests is installed
    try:
        import requests
        print(f"✅ Requests available")
    except ImportError:
        print("❌ Requests not installed. Installing...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'], check=True)
            print("✅ Requests installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Requests")
            return 1
    
    # Run the tests
    try:
        test_file = project_root / 'tests' / 'e2e' / 'selenium_ocr_tests.py'
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return 1
        
        print(f"\n🧪 Running tests from: {test_file}")
        result = subprocess.run([sys.executable, str(test_file)], 
                              cwd=project_root, timeout=300)
        
        if result.returncode == 0:
            print("\n✅ All tests completed successfully!")
        else:
            print(f"\n⚠️ Tests completed with return code: {result.returncode}")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("\n⏰ Tests timed out after 5 minutes")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())