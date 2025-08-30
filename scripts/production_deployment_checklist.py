#!/usr/bin/env python3
"""
Production Deployment Checklist
Comprehensive validation of all production critical fixes
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

class ProductionDeploymentChecker:
    def __init__(self):
        self.results = {
            'static_files': {},
            'react_components': {},
            'javascript_systems': {},
            'django_configuration': {},
            'monitoring_systems': {},
            'performance_optimization': {},
            'security_checks': {},
            'database_status': {},
            'overall_status': 'unknown',
            'critical_issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        self.project_root = Path.cwd()
        
    def log_success(self, category, message):
        """Log success message"""
        print(f"✅ {category}: {message}")
        
    def log_warning(self, category, message):
        """Log warning message"""
        print(f"⚠️ {category}: {message}")
        self.results['warnings'].append(f"{category}: {message}")
        
    def log_error(self, category, message):
        """Log error message"""
        print(f"❌ {category}: {message}")
        self.results['critical_issues'].append(f"{category}: {message}")
        
    def check_static_files(self):
        """Check static file configuration and availability"""
        print("\n📁 Checking static files configuration...")
        
        # Check critical static files exist
        critical_files = [
            'static/assets/css/remixicon.css',
            'static/assets/js/safe-error-handler.js',
            'static/assets/js/safe-dependency-manager.js',
            'static/js/react.production.min.js',
            'static/js/react-dom.production.min.js',
            'static/js/upload-app.bundle.js',
            'static/assets/css/style.css',
            'static/css/design-system.css'
        ]
        
        existing_files = []
        missing_files = []
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
                self.log_success("Static Files", f"{file_path} exists")
            else:
                missing_files.append(file_path)
                self.log_error("Static Files", f"{file_path} missing")
        
        # Check font files
        font_files = [
            'static/assets/fonts/remixicon.woff2',
            'static/assets/fonts/remixicon.woff',
            'static/assets/fonts/remixicon.ttf'
        ]
        
        font_count = 0
        for font_file in font_files:
            if (self.project_root / font_file).exists():
                font_count += 1
        
        if font_count >= 2:
            self.log_success("Static Files", f"Icon fonts available ({font_count}/3)")
        else:
            self.log_error("Static Files", f"Insufficient icon fonts ({font_count}/3)")
        
        self.results['static_files'] = {
            'existing_files': existing_files,
            'missing_files': missing_files,
            'font_files_available': font_count,
            'status': 'ok' if not missing_files else 'error'
        }
        
        return len(missing_files) == 0

    def check_react_components(self):
        """Check React components and build status"""
        print("\n⚛️ Checking React components...")
        
        # Check if React bundles exist
        react_files = [
            'static/js/react.production.min.js',
            'static/js/react-dom.production.min.js',
            'static/js/upload-app.bundle.js'
        ]
        
        react_status = {}
        all_react_files_exist = True
        
        for react_file in react_files:
            file_path = self.project_root / react_file
            if file_path.exists():
                file_size = file_path.stat().st_size
                react_status[react_file] = {
                    'exists': True,
                    'size_kb': file_size / 1024
                }
                self.log_success("React", f"{react_file} exists ({file_size/1024:.1f} KB)")
            else:
                react_status[react_file] = {'exists': False}
                all_react_files_exist = False
                self.log_error("React", f"{react_file} missing")
        
        # Check frontend source files
        frontend_src = self.project_root / 'frontend' / 'src'
        if frontend_src.exists():
            self.log_success("React", "Frontend source directory exists")
        else:
            self.log_warning("React", "Frontend source directory not found")
        
        # Check build scripts
        build_scripts = [
            'frontend/scripts/build-upload-app.js',
            'frontend/scripts/build-simple-upload-app.js'
        ]
        
        build_scripts_exist = 0
        for script in build_scripts:
            if (self.project_root / script).exists():
                build_scripts_exist += 1
                self.log_success("React", f"Build script {script} exists")
        
        self.results['react_components'] = {
            'files': react_status,
            'all_files_exist': all_react_files_exist,
            'build_scripts_available': build_scripts_exist,
            'status': 'ok' if all_react_files_exist else 'error'
        }
        
        return all_react_files_exist

    def check_javascript_systems(self):
        """Check JavaScript error handling and dependency management"""
        print("\n🔧 Checking JavaScript systems...")
        
        # Check error handling scripts
        js_files = {
            'static/assets/js/safe-error-handler.js': 'Error Handler',
            'static/assets/js/safe-dependency-manager.js': 'Dependency Manager',
            'static/assets/js/static-file-monitor.js': 'Static File Monitor',
            'static/assets/js/error-tracking.js': 'Error Tracking',
            'static/assets/js/performance-optimizer.js': 'Performance Optimizer'
        }
        
        js_status = {}
        critical_js_missing = 0
        
        for js_file, description in js_files.items():
            file_path = self.project_root / js_file
            if file_path.exists():
                # Check file size to ensure it's not empty
                file_size = file_path.stat().st_size
                if file_size > 100:  # At least 100 bytes
                    js_status[js_file] = {'exists': True, 'size': file_size}
                    self.log_success("JavaScript", f"{description} exists and has content")
                else:
                    js_status[js_file] = {'exists': True, 'size': file_size, 'empty': True}
                    self.log_warning("JavaScript", f"{description} exists but appears empty")
            else:
                js_status[js_file] = {'exists': False}
                if 'safe-' in js_file:  # Critical files
                    critical_js_missing += 1
                    self.log_error("JavaScript", f"{description} missing (critical)")
                else:
                    self.log_warning("JavaScript", f"{description} missing")
        
        # Check base.html for script loading
        base_template = self.project_root / 'faktury' / 'templates' / 'base.html'
        if base_template.exists():
            with open(base_template, 'r', encoding='utf-8') as f:
                content = f.read()
                
            script_checks = {
                'safe-error-handler.js': 'safe-error-handler.js' in content,
                'safe-dependency-manager.js': 'safe-dependency-manager.js' in content,
                'upload-app.bundle.js': 'upload-app.bundle.js' in content
            }
            
            for script, loaded in script_checks.items():
                if loaded:
                    self.log_success("JavaScript", f"{script} loaded in base template")
                else:
                    self.log_warning("JavaScript", f"{script} not loaded in base template")
        
        self.results['javascript_systems'] = {
            'files': js_status,
            'critical_missing': critical_js_missing,
            'status': 'ok' if critical_js_missing == 0 else 'error'
        }
        
        return critical_js_missing == 0

    def check_django_configuration(self):
        """Check Django configuration for production"""
        print("\n🐍 Checking Django configuration...")
        
        config_checks = {}
        
        # Check if manage.py exists
        manage_py = self.project_root / 'manage.py'
        if manage_py.exists():
            self.log_success("Django", "manage.py exists")
            config_checks['manage_py'] = True
        else:
            self.log_error("Django", "manage.py not found")
            config_checks['manage_py'] = False
        
        # Check settings files
        settings_files = [
            'faktulove/settings.py',
            'faktury_projekt/settings.py'
        ]
        
        settings_found = False
        for settings_file in settings_files:
            if (self.project_root / settings_file).exists():
                self.log_success("Django", f"Settings file {settings_file} exists")
                settings_found = True
                break
        
        if not settings_found:
            self.log_error("Django", "No Django settings file found")
        
        config_checks['settings'] = settings_found
        
        # Check for migrations
        migrations_dir = self.project_root / 'faktury' / 'migrations'
        if migrations_dir.exists():
            migration_files = list(migrations_dir.glob('*.py'))
            migration_count = len([f for f in migration_files if f.name != '__init__.py'])
            
            if migration_count > 0:
                self.log_success("Django", f"Migrations available ({migration_count} files)")
                config_checks['migrations'] = True
            else:
                self.log_warning("Django", "No migration files found")
                config_checks['migrations'] = False
        else:
            self.log_error("Django", "Migrations directory not found")
            config_checks['migrations'] = False
        
        # Check requirements.txt
        requirements_file = self.project_root / 'requirements.txt'
        if requirements_file.exists():
            self.log_success("Django", "requirements.txt exists")
            config_checks['requirements'] = True
        else:
            self.log_warning("Django", "requirements.txt not found")
            config_checks['requirements'] = False
        
        self.results['django_configuration'] = {
            'checks': config_checks,
            'status': 'ok' if all(config_checks.values()) else 'warning'
        }
        
        return settings_found and config_checks['manage_py']

    def check_monitoring_systems(self):
        """Check monitoring and error handling systems"""
        print("\n🛡️ Checking monitoring systems...")
        
        monitoring_files = {
            'static/assets/js/safe-error-handler.js': 'SafeErrorHandler',
            'static/assets/js/safe-dependency-manager.js': 'SafeDependencyManager',
            'static/assets/js/static-file-monitor.js': 'StaticFileMonitor',
            'static/assets/js/error-tracking.js': 'ErrorTracker',
            'static/assets/js/performance-optimizer.js': 'PerformanceOptimizer'
        }
        
        monitoring_status = {}
        active_systems = 0
        
        for file_path, system_name in monitoring_files.items():
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.stat().st_size > 100:
                monitoring_status[system_name] = True
                active_systems += 1
                self.log_success("Monitoring", f"{system_name} available")
            else:
                monitoring_status[system_name] = False
                self.log_warning("Monitoring", f"{system_name} not available")
        
        # Check middleware
        middleware_file = self.project_root / 'faktury' / 'middleware' / 'ocr_security_middleware.py'
        if middleware_file.exists():
            self.log_success("Monitoring", "OCR security middleware exists")
            monitoring_status['SecurityMiddleware'] = True
        else:
            self.log_warning("Monitoring", "OCR security middleware not found")
            monitoring_status['SecurityMiddleware'] = False
        
        monitoring_score = (active_systems / len(monitoring_files)) * 100
        
        self.results['monitoring_systems'] = {
            'systems': monitoring_status,
            'active_count': active_systems,
            'total_count': len(monitoring_files),
            'score': monitoring_score,
            'status': 'ok' if monitoring_score >= 60 else 'warning'
        }
        
        return monitoring_score >= 60

    def check_performance_optimization(self):
        """Check performance optimization implementations"""
        print("\n⚡ Checking performance optimizations...")
        
        optimizations = {}
        
        # Check CSS optimization
        css_files = list(self.project_root.glob('static/**/*.css'))
        minified_css = len([f for f in css_files if '.min.' in f.name])
        
        if minified_css > 0:
            self.log_success("Performance", f"Minified CSS files found ({minified_css})")
            optimizations['minified_css'] = True
        else:
            self.log_warning("Performance", "No minified CSS files found")
            optimizations['minified_css'] = False
        
        # Check JS optimization
        js_files = list(self.project_root.glob('static/**/*.js'))
        minified_js = len([f for f in js_files if '.min.' in f.name or 'bundle' in f.name])
        
        if minified_js > 0:
            self.log_success("Performance", f"Optimized JS files found ({minified_js})")
            optimizations['minified_js'] = True
        else:
            self.log_warning("Performance", "No optimized JS files found")
            optimizations['minified_js'] = False
        
        # Check for compression-ready files
        gzip_files = list(self.project_root.glob('static/**/*.gz'))
        if gzip_files:
            self.log_success("Performance", f"Gzip files available ({len(gzip_files)})")
            optimizations['gzip_files'] = True
        else:
            self.log_warning("Performance", "No gzip files found")
            optimizations['gzip_files'] = False
        
        # Check performance monitoring script
        perf_script = self.project_root / 'static' / 'assets' / 'js' / 'performance-optimizer.js'
        if perf_script.exists():
            self.log_success("Performance", "Performance optimizer script exists")
            optimizations['performance_monitoring'] = True
        else:
            self.log_warning("Performance", "Performance optimizer script not found")
            optimizations['performance_monitoring'] = False
        
        optimization_score = (sum(optimizations.values()) / len(optimizations)) * 100
        
        self.results['performance_optimization'] = {
            'optimizations': optimizations,
            'score': optimization_score,
            'status': 'ok' if optimization_score >= 50 else 'warning'
        }
        
        return optimization_score >= 50

    def check_security(self):
        """Check security configurations"""
        print("\n🔒 Checking security configurations...")
        
        security_checks = {}
        
        # Check for security middleware
        security_middleware = self.project_root / 'faktury' / 'middleware' / 'ocr_security_middleware.py'
        if security_middleware.exists():
            self.log_success("Security", "OCR security middleware exists")
            security_checks['ocr_middleware'] = True
        else:
            self.log_warning("Security", "OCR security middleware not found")
            security_checks['ocr_middleware'] = False
        
        # Check for CSRF protection in templates
        base_template = self.project_root / 'faktury' / 'templates' / 'base.html'
        if base_template.exists():
            with open(base_template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'csrf_token' in content:
                self.log_success("Security", "CSRF token usage found in templates")
                security_checks['csrf_protection'] = True
            else:
                self.log_warning("Security", "CSRF token not found in base template")
                security_checks['csrf_protection'] = False
        
        # Check for secure file upload handling
        ocr_views = self.project_root / 'faktury' / 'views_modules' / 'ocr_views.py'
        if ocr_views.exists():
            with open(ocr_views, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'FileValidationError' in content and 'csrf_exempt' not in content:
                self.log_success("Security", "Secure file upload handling implemented")
                security_checks['secure_upload'] = True
            else:
                self.log_warning("Security", "File upload security may need review")
                security_checks['secure_upload'] = False
        
        security_score = (sum(security_checks.values()) / len(security_checks)) * 100
        
        self.results['security_checks'] = {
            'checks': security_checks,
            'score': security_score,
            'status': 'ok' if security_score >= 70 else 'warning'
        }
        
        return security_score >= 70

    def run_deployment_check(self):
        """Run complete deployment checklist"""
        print("🚀 Production Deployment Checklist")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all checks
        checks = [
            ("Static Files", self.check_static_files),
            ("React Components", self.check_react_components),
            ("JavaScript Systems", self.check_javascript_systems),
            ("Django Configuration", self.check_django_configuration),
            ("Monitoring Systems", self.check_monitoring_systems),
            ("Performance Optimization", self.check_performance_optimization),
            ("Security", self.check_security)
        ]
        
        passed_checks = 0
        total_checks = len(checks)
        
        for check_name, check_func in checks:
            try:
                if check_func():
                    passed_checks += 1
            except Exception as e:
                self.log_error(check_name, f"Check failed with error: {e}")
        
        # Calculate overall status
        success_rate = (passed_checks / total_checks) * 100
        
        if success_rate >= 90:
            self.results['overall_status'] = 'excellent'
        elif success_rate >= 75:
            self.results['overall_status'] = 'good'
        elif success_rate >= 60:
            self.results['overall_status'] = 'acceptable'
        else:
            self.results['overall_status'] = 'needs_work'
        
        # Generate recommendations
        if success_rate < 100:
            self.results['recommendations'].append("Address all critical issues before deployment")
        
        if len(self.results['critical_issues']) > 0:
            self.results['recommendations'].append("Fix critical issues immediately")
        
        if len(self.results['warnings']) > 3:
            self.results['recommendations'].append("Review and address warnings for optimal performance")
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT CHECKLIST RESULTS")
        print("=" * 60)
        
        print(f"✅ Passed Checks: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
        print(f"🎯 Overall Status: {self.results['overall_status'].upper()}")
        
        if self.results['critical_issues']:
            print(f"\n❌ Critical Issues ({len(self.results['critical_issues'])}):")
            for issue in self.results['critical_issues']:
                print(f"   • {issue}")
        
        if self.results['warnings']:
            print(f"\n⚠️ Warnings ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
        
        if self.results['recommendations']:
            print(f"\n💡 Recommendations ({len(self.results['recommendations'])}):")
            for rec in self.results['recommendations']:
                print(f"   • {rec}")
        
        print(f"\n⏱️ Check completed in: {time.time() - start_time:.1f}s")
        
        # Save results
        with open('deployment_checklist_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"💾 Results saved to: deployment_checklist_results.json")
        
        # Deployment readiness
        is_ready = (success_rate >= 75 and 
                   len(self.results['critical_issues']) == 0)
        
        if is_ready:
            print("\n🎉 DEPLOYMENT READY!")
            print("All critical systems are operational.")
        else:
            print("\n⚠️ NOT READY FOR DEPLOYMENT")
            print("Please address critical issues before deploying.")
        
        return is_ready

def main():
    """Main function"""
    checker = ProductionDeploymentChecker()
    
    try:
        ready = checker.run_deployment_check()
        sys.exit(0 if ready else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Deployment check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Deployment check failed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()