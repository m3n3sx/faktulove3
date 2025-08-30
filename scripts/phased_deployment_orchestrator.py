#!/usr/bin/env python3
"""
Phased Deployment Orchestrator
Coordinates the complete phased deployment and validation process
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class PhasedDeploymentOrchestrator:
    """Orchestrates phased deployment and validation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.deployment_log = []
        self.start_time = datetime.now()
        
    def log_step(self, step, status, message=""):
        """Log deployment step"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'step': step,
            'status': status,
            'message': message
        }
        self.deployment_log.append(log_entry)
        
        status_icon = "✓" if status == "SUCCESS" else "✗" if status == "FAILED" else "⏳"
        print(f"{status_icon} [{timestamp}] {step}: {status} {message}")
        
    def run_command(self, command, description):
        """Run shell command with logging"""
        self.log_step(description, "RUNNING")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.log_step(description, "SUCCESS", f"Exit code: {result.returncode}")
                return True, result.stdout
            else:
                self.log_step(description, "FAILED", f"Exit code: {result.returncode}, Error: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.log_step(description, "FAILED", "Command timed out after 5 minutes")
            return False, "Timeout"
        except Exception as e:
            self.log_step(description, "FAILED", f"Exception: {str(e)}")
            return False, str(e)
            
    def run_python_script(self, script_path, description):
        """Run Python script with proper environment"""
        command = f"python {script_path}"
        return self.run_command(command, description)
        
    def check_prerequisites(self):
        """Check deployment prerequisites"""
        print("\n=== Checking Deployment Prerequisites ===")
        
        # Check if virtual environment is activated
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.log_step("Virtual Environment Check", "WARNING", "Virtual environment not detected")
        else:
            self.log_step("Virtual Environment Check", "SUCCESS")
            
        # Check database connectivity
        success, output = self.run_command("python manage.py check --database default", "Database Connectivity Check")
        if not success:
            return False
            
        # Check static files
        success, output = self.run_command("python manage.py check --deploy", "Django Deployment Check")
        if not success:
            self.log_step("Django Deployment Check", "WARNING", "Some deployment checks failed")
            
        # Check required services
        services_to_check = [
            ("Redis", "redis-cli ping"),
            ("Database", "python manage.py dbshell --command='SELECT 1;'")
        ]
        
        for service_name, command in services_to_check:
            success, output = self.run_command(command, f"{service_name} Service Check")
            if not success:
                self.log_step(f"{service_name} Service Check", "WARNING", f"Service may not be available: {output}")
                
        return True
        
    def backup_current_state(self):
        """Create backup of current system state"""
        print("\n=== Creating System Backup ===")
        
        backup_timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
        backup_dir = f"backups/{backup_timestamp}"
        
        # Create backup directory
        success, output = self.run_command(f"mkdir -p {backup_dir}", "Create Backup Directory")
        if not success:
            return False
            
        # Backup database
        success, output = self.run_command(
            f"python manage.py dumpdata --natural-foreign --natural-primary > {backup_dir}/database_backup.json",
            "Database Backup"
        )
        if not success:
            self.log_step("Database Backup", "WARNING", "Database backup failed, continuing...")
            
        # Backup media files
        success, output = self.run_command(f"cp -r media {backup_dir}/", "Media Files Backup")
        if not success:
            self.log_step("Media Files Backup", "WARNING", "Media backup failed, continuing...")
            
        # Backup configuration files
        config_files = ['.env', 'faktulove/settings.py', 'requirements.txt']
        for config_file in config_files:
            if os.path.exists(config_file):
                success, output = self.run_command(f"cp {config_file} {backup_dir}/", f"Backup {config_file}")
                
        self.log_step("System Backup", "SUCCESS", f"Backup created in {backup_dir}")
        return True
        
    def run_migrations(self):
        """Run database migrations"""
        print("\n=== Running Database Migrations ===")
        
        # Check for pending migrations
        success, output = self.run_command("python manage.py showmigrations --plan", "Check Pending Migrations")
        if not success:
            return False
            
        # Run migrations
        success, output = self.run_command("python manage.py migrate", "Apply Database Migrations")
        return success
        
    def collect_static_files(self):
        """Collect and optimize static files"""
        print("\n=== Collecting Static Files ===")
        
        # Collect static files
        success, output = self.run_command("python manage.py collectstatic --noinput", "Collect Static Files")
        if not success:
            return False
            
        # Optimize assets if available
        success, output = self.run_command("python manage.py optimize_assets", "Optimize Static Assets")
        if not success:
            self.log_step("Asset Optimization", "WARNING", "Asset optimization failed, continuing...")
            
        return True
        
    def run_phase_1_validation(self):
        """Run Phase 1: Core fixes validation"""
        print("\n=== Phase 1: Core Fixes Validation ===")
        
        success, output = self.run_python_script(
            "scripts/deploy_and_validate_core_fixes.py",
            "Core Fixes Validation"
        )
        
        if success:
            self.log_step("Phase 1 Validation", "SUCCESS", "All core fixes validated successfully")
        else:
            self.log_step("Phase 1 Validation", "FAILED", "Core fixes validation failed")
            
        return success
        
    def run_phase_2_validation(self):
        """Run Phase 2: Complete system validation"""
        print("\n=== Phase 2: Complete System Validation ===")
        
        success, output = self.run_python_script(
            "scripts/complete_system_validation.py",
            "Complete System Validation"
        )
        
        if success:
            self.log_step("Phase 2 Validation", "SUCCESS", "Complete system validation passed")
        else:
            self.log_step("Phase 2 Validation", "FAILED", "Complete system validation failed")
            
        return success
        
    def run_comprehensive_tests(self):
        """Run comprehensive test suite"""
        print("\n=== Running Comprehensive Tests ===")
        
        # Run unit tests
        success, output = self.run_command("python -m pytest faktury/tests/ -v", "Unit Tests")
        if not success:
            self.log_step("Unit Tests", "WARNING", "Some unit tests failed")
            
        # Run integration tests
        success, output = self.run_command("python run_comprehensive_tests.py", "Comprehensive Test Suite")
        if not success:
            self.log_step("Comprehensive Tests", "WARNING", "Some comprehensive tests failed")
            
        return True  # Continue even if some tests fail
        
    def restart_services(self):
        """Restart application services"""
        print("\n=== Restarting Services ===")
        
        # Restart Gunicorn if running
        success, output = self.run_command("./scripts/restart_gunicorn.sh", "Restart Gunicorn")
        if not success:
            self.log_step("Restart Gunicorn", "WARNING", "Gunicorn restart failed or not running")
            
        # Restart Celery workers if running
        success, output = self.run_command("pkill -f 'celery worker'", "Stop Celery Workers")
        time.sleep(2)  # Wait for graceful shutdown
        
        success, output = self.run_command("celery -A faktury_projekt worker -D", "Start Celery Workers")
        if not success:
            self.log_step("Start Celery Workers", "WARNING", "Celery workers start failed")
            
        return True
        
    def generate_deployment_report(self):
        """Generate comprehensive deployment report"""
        print("\n=== Generating Deployment Report ===")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Count success/failure rates
        total_steps = len(self.deployment_log)
        successful_steps = len([log for log in self.deployment_log if log['status'] == 'SUCCESS'])
        failed_steps = len([log for log in self.deployment_log if log['status'] == 'FAILED'])
        warning_steps = len([log for log in self.deployment_log if log['status'] == 'WARNING'])
        
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        report = {
            'deployment_timestamp': self.start_time.isoformat(),
            'deployment_duration': str(duration),
            'overall_status': 'SUCCESS' if failed_steps == 0 else 'PARTIAL' if successful_steps > failed_steps else 'FAILED',
            'statistics': {
                'total_steps': total_steps,
                'successful_steps': successful_steps,
                'failed_steps': failed_steps,
                'warning_steps': warning_steps,
                'success_rate': success_rate
            },
            'deployment_log': self.deployment_log,
            'recommendations': self._generate_deployment_recommendations()
        }
        
        # Save report
        report_file = f"deployment_reports/phased_deployment_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('deployment_reports', exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # Print summary
        print(f"\n=== DEPLOYMENT SUMMARY ===")
        print(f"Overall Status: {report['overall_status']}")
        print(f"Duration: {duration}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Steps: {successful_steps} successful, {failed_steps} failed, {warning_steps} warnings")
        print(f"Report saved to: {report_file}")
        
        if report['recommendations']:
            print(f"\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
                
        return report
        
    def _generate_deployment_recommendations(self):
        """Generate deployment recommendations"""
        recommendations = []
        
        failed_steps = [log for log in self.deployment_log if log['status'] == 'FAILED']
        warning_steps = [log for log in self.deployment_log if log['status'] == 'WARNING']
        
        if failed_steps:
            recommendations.append("Address failed deployment steps before proceeding to production")
            
        if warning_steps:
            recommendations.append("Review warning messages and consider addressing them")
            
        # Check specific issues
        for log in self.deployment_log:
            if 'timeout' in log.get('message', '').lower():
                recommendations.append("Consider increasing timeout values for long-running operations")
            if 'database' in log.get('step', '').lower() and log['status'] == 'FAILED':
                recommendations.append("Verify database connectivity and permissions")
            if 'static' in log.get('step', '').lower() and log['status'] == 'FAILED':
                recommendations.append("Check static files configuration and permissions")
                
        return recommendations
        
    def run_phased_deployment(self):
        """Execute complete phased deployment"""
        print("=" * 60)
        print("FAKTULOVE PHASED DEPLOYMENT ORCHESTRATOR")
        print("=" * 60)
        print(f"Start Time: {self.start_time}")
        print()
        
        try:
            # Phase 0: Prerequisites and preparation
            if not self.check_prerequisites():
                self.log_step("Prerequisites Check", "FAILED", "Prerequisites not met")
                return False
                
            if not self.backup_current_state():
                self.log_step("System Backup", "FAILED", "Backup creation failed")
                return False
                
            # Phase 1: Database and static files
            if not self.run_migrations():
                self.log_step("Database Migrations", "FAILED", "Migration failed")
                return False
                
            if not self.collect_static_files():
                self.log_step("Static Files Collection", "FAILED", "Static files collection failed")
                return False
                
            # Phase 2: Core fixes validation
            if not self.run_phase_1_validation():
                self.log_step("Phase 1 Deployment", "FAILED", "Core fixes validation failed")
                return False
                
            # Phase 3: Complete system validation
            if not self.run_phase_2_validation():
                self.log_step("Phase 2 Deployment", "FAILED", "Complete system validation failed")
                return False
                
            # Phase 4: Comprehensive testing
            self.run_comprehensive_tests()  # Continue even if tests fail
            
            # Phase 5: Service restart
            self.restart_services()
            
            # Generate final report
            report = self.generate_deployment_report()
            
            if report['overall_status'] == 'SUCCESS':
                print("\n🎉 PHASED DEPLOYMENT COMPLETED SUCCESSFULLY!")
                return True
            else:
                print(f"\n⚠️  PHASED DEPLOYMENT COMPLETED WITH ISSUES: {report['overall_status']}")
                return False
                
        except Exception as e:
            self.log_step("Deployment Orchestration", "FAILED", f"Critical error: {str(e)}")
            print(f"\n❌ DEPLOYMENT FAILED: {str(e)}")
            return False

def main():
    """Main execution function"""
    orchestrator = PhasedDeploymentOrchestrator()
    success = orchestrator.run_phased_deployment()
    
    if success:
        print("\nDeployment completed successfully!")
        sys.exit(0)
    else:
        print("\nDeployment completed with issues. Please review the deployment report.")
        sys.exit(1)

if __name__ == '__main__':
    main()