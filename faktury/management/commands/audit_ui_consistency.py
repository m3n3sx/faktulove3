"""
Management command to audit UI consistency across the FaktuLove application.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
from faktury.services.ui_consistency_manager import UIConsistencyManager


class Command(BaseCommand):
    help = 'Audit UI consistency and generate recommendations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--apply-fixes',
            action='store_true',
            help='Apply automatic fixes for common issues'
        )
        
        parser.add_argument(
            '--generate-report',
            action='store_true',
            help='Generate HTML report of findings'
        )
        
        parser.add_argument(
            '--output-dir',
            type=str,
            default='ui_audit_reports',
            help='Directory to save reports'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting UI consistency audit...'))
        
        manager = UIConsistencyManager()
        
        # Run audit
        audit_results = manager.audit_ui_components()
        
        # Display summary
        self.display_audit_summary(audit_results)
        
        # Apply design system if requested
        if options['apply_fixes']:
            self.stdout.write('\nApplying design system fixes...')
            design_results = manager.apply_design_system()
            self.display_design_system_results(design_results)
            
            # Optimize mobile experience
            mobile_results = manager.optimize_mobile_experience()
            self.display_mobile_optimization_results(mobile_results)
            
            # Add loading states
            loading_results = manager.add_loading_states_and_skeleton_screens()
            self.display_loading_states_results(loading_results)
        
        # Generate report if requested
        if options['generate_report']:
            self.generate_reports(manager, audit_results, options['output_dir'])
        
        self.stdout.write(self.style.SUCCESS('\nUI consistency audit completed!'))
    
    def display_audit_summary(self, results):
        """Display audit summary."""
        self.stdout.write(f"\n📊 Audit Summary:")
        self.stdout.write(f"  Templates analyzed: {results['templates_analyzed']}")
        self.stdout.write(f"  Inconsistencies found: {len(results['inconsistencies'])}")
        self.stdout.write(f"  Accessibility issues: {len(results['accessibility_issues'])}")
        self.stdout.write(f"  CSS issues: {len(results['css_issues'])}")
        self.stdout.write(f"  Recommendations: {len(results['recommendations'])}")
        
        # Show top issues
        if results['inconsistencies']:
            self.stdout.write(f"\n🔍 Top Inconsistencies:")
            for issue in results['inconsistencies'][:5]:
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(issue['severity'], '⚪')
                self.stdout.write(f"  {severity_icon} {issue['type']}: {issue['issue']}")
        
        if results['accessibility_issues']:
            self.stdout.write(f"\n♿ Accessibility Issues:")
            for issue in results['accessibility_issues'][:5]:
                self.stdout.write(f"  🔴 {issue['type']}: {issue['issue']}")
    
    def display_design_system_results(self, results):
        """Display design system application results."""
        self.stdout.write(f"\n🎨 Design System Application:")
        self.stdout.write(f"  Templates updated: {results['templates_updated']}")
        self.stdout.write(f"  CSS files created: {results['css_files_created']}")
        self.stdout.write(f"  Components created: {results['components_created']}")
        
        if results['errors']:
            self.stdout.write(self.style.ERROR(f"  Errors: {len(results['errors'])}"))
            for error in results['errors']:
                self.stdout.write(self.style.ERROR(f"    - {error}"))
    
    def display_mobile_optimization_results(self, results):
        """Display mobile optimization results."""
        self.stdout.write(f"\n📱 Mobile Optimization:")
        self.stdout.write(f"  CSS rules added: {results['css_rules_added']}")
        self.stdout.write(f"  Mobile issues fixed: {results['mobile_issues_fixed']}")
        
        if results['errors']:
            self.stdout.write(self.style.ERROR(f"  Errors: {len(results['errors'])}"))
    
    def display_loading_states_results(self, results):
        """Display loading states implementation results."""
        self.stdout.write(f"\n⏳ Loading States & Skeletons:")
        self.stdout.write(f"  Skeleton screens created: {results['skeleton_screens_created']}")
        self.stdout.write(f"  Templates updated: {results['templates_updated']}")
        
        if results['errors']:
            self.stdout.write(self.style.ERROR(f"  Errors: {len(results['errors'])}"))
    
    def generate_reports(self, manager, audit_results, output_dir):
        """Generate audit reports."""
        self.stdout.write(f"\n📄 Generating reports...")
        
        # Create output directory
        reports_dir = os.path.join(settings.BASE_DIR, output_dir)
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate HTML report
        html_report = manager.generate_consistency_report()
        html_path = os.path.join(reports_dir, 'ui_consistency_report.html')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # Generate JSON report for programmatic access
        json_path = os.path.join(reports_dir, 'ui_audit_results.json')
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(audit_results, f, indent=2, default=str)
        
        self.stdout.write(f"  HTML report: {html_path}")
        self.stdout.write(f"  JSON data: {json_path}")