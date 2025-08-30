"""
Management command to optimize user experience and workflows.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
from faktury.services.user_experience_optimizer import UserExperienceOptimizer


class Command(BaseCommand):
    help = 'Optimize user experience and workflows'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze-only',
            action='store_true',
            help='Only analyze workflows without implementing changes'
        )
        
        parser.add_argument(
            '--implement-optimizations',
            action='store_true',
            help='Implement UX optimizations'
        )
        
        parser.add_argument(
            '--generate-report',
            action='store_true',
            help='Generate UX optimization report'
        )
        
        parser.add_argument(
            '--output-dir',
            type=str,
            default='ux_reports',
            help='Directory to save reports'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting UX optimization...'))
        
        optimizer = UserExperienceOptimizer()
        
        # Analyze user workflows
        self.stdout.write('\nAnalyzing user workflows...')
        analysis_results = optimizer.analyze_user_flows()
        self.display_analysis_results(analysis_results)
        
        # Implement optimizations if requested
        if options['implement_optimizations'] and not options['analyze_only']:
            self.stdout.write('\nImplementing UX optimizations...')
            
            # Reduce click complexity
            click_results = optimizer.reduce_click_complexity()
            self.display_click_reduction_results(click_results)
            
            # Add keyboard shortcuts and accessibility
            accessibility_results = optimizer.add_keyboard_shortcuts_and_accessibility()
            self.display_accessibility_results(accessibility_results)
            
            # Create contextual help
            help_results = optimizer.create_contextual_help_and_onboarding_tooltips()
            self.display_help_results(help_results)
        
        # Generate report if requested
        if options['generate_report']:
            self.generate_reports(optimizer, analysis_results, options['output_dir'])
        
        self.stdout.write(self.style.SUCCESS('\nUX optimization completed!'))
    
    def display_analysis_results(self, results):
        """Display workflow analysis results."""
        self.stdout.write(f"\n📊 Workflow Analysis:")
        self.stdout.write(f"  Workflows analyzed: {results['workflows_analyzed']}")
        self.stdout.write(f"  Click reduction potential: {results['click_reduction_potential']}")
        self.stdout.write(f"  Optimization opportunities: {len(results['optimization_opportunities'])}")
        self.stdout.write(f"  Pain points identified: {len(results['pain_points'])}")
        
        if results['optimization_opportunities']:
            self.stdout.write(f"\n🎯 Top Optimization Opportunities:")
            for opportunity in results['optimization_opportunities'][:3]:
                workflow_name = opportunity['workflow'].replace('_', ' ').title()
                self.stdout.write(f"  • {workflow_name}: {opportunity['reduction_potential']} clicks can be saved")
        
        if results['pain_points']:
            self.stdout.write(f"\n⚠️  Key Pain Points:")
            for pain_point in results['pain_points'][:5]:
                workflow_name = pain_point['workflow'].replace('_', ' ').title()
                self.stdout.write(f"  • {workflow_name}: {pain_point['issue']}")
        
        if results['recommendations']:
            self.stdout.write(f"\n💡 Recommendations:")
            for rec in results['recommendations']:
                priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '⚪')
                self.stdout.write(f"  {priority_icon} {rec['category']}: {rec['description']}")
    
    def display_click_reduction_results(self, results):
        """Display click reduction implementation results."""
        self.stdout.write(f"\n🖱️  Click Complexity Reduction:")
        self.stdout.write(f"  Quick actions added: {results['quick_actions_added']}")
        self.stdout.write(f"  Shortcuts implemented: {results['shortcuts_implemented']}")
        self.stdout.write(f"  Wizards created: {results['wizards_created']}")
        self.stdout.write(f"  Auto-save enabled: {results['auto_save_enabled']}")
        
        if results['errors']:
            self.stdout.write(self.style.ERROR(f"  Errors: {len(results['errors'])}"))
            for error in results['errors']:
                self.stdout.write(self.style.ERROR(f"    - {error}"))
    
    def display_accessibility_results(self, results):
        """Display accessibility implementation results."""
        self.stdout.write(f"\n♿ Accessibility & Keyboard Shortcuts:")
        self.stdout.write(f"  Shortcuts added: {results['shortcuts_added']}")
        self.stdout.write(f"  Accessibility improvements: {results['accessibility_improvements']}")
        self.stdout.write(f"  ARIA labels added: {results['aria_labels_added']}")
        self.stdout.write(f"  Focus management improved: {results['focus_management_improved']}")
        
        if results['errors']:
            self.stdout.write(self.style.ERROR(f"  Errors: {len(results['errors'])}"))
    
    def display_help_results(self, results):
        """Display contextual help implementation results."""
        self.stdout.write(f"\n❓ Contextual Help & Onboarding:")
        self.stdout.write(f"  Help tooltips created: {results['help_tooltips_created']}")
        self.stdout.write(f"  Onboarding tours created: {results['onboarding_tours_created']}")
        self.stdout.write(f"  Help modals created: {results['help_modals_created']}")
        
        if results['errors']:
            self.stdout.write(self.style.ERROR(f"  Errors: {len(results['errors'])}"))
    
    def generate_reports(self, optimizer, analysis_results, output_dir):
        """Generate UX optimization reports."""
        self.stdout.write(f"\n📄 Generating reports...")
        
        # Create output directory
        reports_dir = os.path.join(settings.BASE_DIR, output_dir)
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate HTML report
        html_report = optimizer.generate_ux_optimization_report()
        html_path = os.path.join(reports_dir, 'ux_optimization_report.html')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # Generate JSON report for programmatic access
        json_path = os.path.join(reports_dir, 'ux_analysis_results.json')
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        # Generate keyboard shortcuts reference
        shortcuts_html = self._generate_shortcuts_reference(optimizer)
        shortcuts_path = os.path.join(reports_dir, 'keyboard_shortcuts_reference.html')
        
        with open(shortcuts_path, 'w', encoding='utf-8') as f:
            f.write(shortcuts_html)
        
        self.stdout.write(f"  HTML report: {html_path}")
        self.stdout.write(f"  JSON data: {json_path}")
        self.stdout.write(f"  Shortcuts reference: {shortcuts_path}")
    
    def _generate_shortcuts_reference(self, optimizer):
        """Generate keyboard shortcuts reference card."""
        shortcuts = optimizer.keyboard_shortcuts
        
        html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Keyboard Shortcuts Reference - FaktuLove</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .section { margin: 20px 0; }
        .shortcut-table { width: 100%; border-collapse: collapse; }
        .shortcut-table th, .shortcut-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .shortcut-table th { background: #f8f9fa; }
        .shortcut-key { font-family: monospace; background: #e9ecef; padding: 4px 8px; border-radius: 4px; }
        .context-title { color: #495057; margin-top: 30px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Keyboard Shortcuts Reference</h1>
        <p>Quick reference for all keyboard shortcuts in FaktuLove</p>
    </div>
'''
        
        for context, context_shortcuts in shortcuts.items():
            context_title = {
                'global': 'Globalne skróty',
                'invoice_form': 'Formularz faktury',
                'invoice_list': 'Lista faktur'
            }.get(context, context)
            
            html += f'''
    <div class="section">
        <h2 class="context-title">{context_title}</h2>
        <table class="shortcut-table">
            <thead>
                <tr>
                    <th>Skrót</th>
                    <th>Opis</th>
                </tr>
            </thead>
            <tbody>
'''
            
            for key, shortcut in context_shortcuts.items():
                formatted_key = key.replace('ctrl+', 'Ctrl+').replace('shift+', 'Shift+').replace('alt+', 'Alt+')
                html += f'''
                <tr>
                    <td><span class="shortcut-key">{formatted_key}</span></td>
                    <td>{shortcut['description']}</td>
                </tr>
'''
            
            html += '''
            </tbody>
        </table>
    </div>
'''
        
        html += '''
    <div class="section">
        <h2>Wskazówki</h2>
        <ul>
            <li>Skróty globalne działają na każdej stronie aplikacji</li>
            <li>Skróty kontekstowe działają tylko na odpowiednich stronach</li>
            <li>Użyj Ctrl+/ aby wyświetlić pomoc ze skrótami w aplikacji</li>
            <li>Wszystkie skróty są dostępne dla użytkowników klawiatury</li>
        </ul>
    </div>
</body>
</html>
'''
        
        return html