"""
Management command for compliance monitoring and data cleanup
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Monitor compliance and perform data cleanup according to Polish regulations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup-expired',
            action='store_true',
            help='Clean up expired data according to retention policies',
        )
        parser.add_argument(
            '--generate-report',
            action='store_true',
            help='Generate compliance report for the last month',
        )
        parser.add_argument(
            '--check-gdpr',
            type=int,
            help='Check GDPR compliance for specific user ID',
        )
        parser.add_argument(
            '--validate-invoices',
            action='store_true',
            help='Validate recent invoices for Polish VAT compliance',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to look back for reports (default: 30)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting compliance monitoring...')
        )
        
        try:
            if options['cleanup_expired']:
                self._cleanup_expired_data()
            
            if options['generate_report']:
                self._generate_compliance_report(options['days'])
            
            if options['check_gdpr']:
                self._check_gdpr_compliance(options['check_gdpr'])
            
            if options['validate_invoices']:
                self._validate_recent_invoices(options['days'])
            
            # Always run basic monitoring
            self._run_basic_monitoring()
            
            self.stdout.write(
                self.style.SUCCESS('Compliance monitoring completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during compliance monitoring: {e}')
            )
            logger.error(f"Compliance monitoring error: {e}")
    
    def _cleanup_expired_data(self):
        """Clean up expired data according to retention policies"""
        self.stdout.write('Cleaning up expired data...')
        
        from faktury.services.polish_compliance_service import PolishComplianceService
        
        compliance_service = PolishComplianceService()
        cleanup_stats = compliance_service.cleanup_expired_data()
        
        self.stdout.write(f'  Cleanup statistics:')
        for data_type, count in cleanup_stats.items():
            self.stdout.write(f'    {data_type}: {count} items')
        
        self.stdout.write(self.style.SUCCESS('✓ Data cleanup completed'))
    
    def _generate_compliance_report(self, days):
        """Generate compliance report for the specified period"""
        self.stdout.write(f'Generating compliance report for last {days} days...')
        
        from faktury.services.polish_compliance_service import PolishComplianceService
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        compliance_service = PolishComplianceService()
        report = compliance_service.generate_compliance_report(start_date, end_date)
        
        self.stdout.write(f'  Report Summary:')
        summary = report['summary']
        self.stdout.write(f'    Total invoices: {summary["total_invoices"]}')
        self.stdout.write(f'    Compliant invoices: {summary["compliant_invoices"]}')
        self.stdout.write(f'    Compliance rate: {summary["compliance_rate"]}%')
        self.stdout.write(f'    Average compliance score: {summary["average_compliance_score"]}')
        self.stdout.write(f'    Total violations: {summary["total_violations"]}')
        self.stdout.write(f'    Total warnings: {summary["total_warnings"]}')
        
        # Show most common violations
        if report['violation_analysis']['most_common_violations']:
            self.stdout.write(f'  Most common violations:')
            for violation, count in report['violation_analysis']['most_common_violations'][:5]:
                self.stdout.write(f'    {violation}: {count} times')
        
        # Show recommendations
        if report['recommendations']:
            self.stdout.write(f'  Recommendations:')
            for recommendation in report['recommendations']:
                self.stdout.write(f'    - {recommendation}')
        
        self.stdout.write(self.style.SUCCESS('✓ Compliance report generated'))
    
    def _check_gdpr_compliance(self, user_id):
        """Check GDPR compliance for specific user"""
        self.stdout.write(f'Checking GDPR compliance for user {user_id}...')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {user_id} not found'))
            return
        
        from faktury.services.polish_compliance_service import PolishComplianceService
        
        compliance_service = PolishComplianceService()
        gdpr_status = compliance_service.implement_gdpr_compliance(user)
        
        self.stdout.write(f'  GDPR Compliance Status for {user.username}:')
        
        # Data inventory
        inventory = gdpr_status['data_inventory']
        self.stdout.write(f'    Personal data: {len(inventory.get("personal_data", {}))} fields')
        self.stdout.write(f'    Business data: {len(inventory.get("business_data", {}))} records')
        
        doc_data = inventory.get('document_data', {})
        self.stdout.write(f'    Invoices: {doc_data.get("invoices_count", 0)}')
        self.stdout.write(f'    Contractors: {doc_data.get("contractors_count", 0)}')
        
        audit_data = inventory.get('audit_data', {})
        self.stdout.write(f'    Audit logs: {audit_data.get("audit_logs_count", 0)}')
        
        # User rights
        rights = gdpr_status['user_rights']
        implemented_rights = sum(1 for right in rights.values() if right.get('implemented', False))
        self.stdout.write(f'    Implemented rights: {implemented_rights}/{len(rights)}')
        
        # Recommendations
        if gdpr_status['recommendations']:
            self.stdout.write(f'  GDPR Recommendations:')
            for recommendation in gdpr_status['recommendations']:
                self.stdout.write(f'    - {recommendation}')
        
        self.stdout.write(self.style.SUCCESS('✓ GDPR compliance check completed'))
    
    def _validate_recent_invoices(self, days):
        """Validate recent invoices for Polish VAT compliance"""
        self.stdout.write(f'Validating invoices from last {days} days...')
        
        from faktury.models import Faktura
        from faktury.services.polish_compliance_service import PolishComplianceService
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        invoices = Faktura.objects.filter(
            data_wystawienia__range=[start_date, end_date]
        )
        
        compliance_service = PolishComplianceService()
        
        total_invoices = invoices.count()
        compliant_count = 0
        violation_count = 0
        warning_count = 0
        
        self.stdout.write(f'  Found {total_invoices} invoices to validate')
        
        for invoice in invoices[:10]:  # Limit to first 10 for performance
            invoice_data = compliance_service._extract_invoice_data(invoice)
            validation_result = compliance_service.validate_invoice_compliance(invoice_data)
            
            if validation_result['is_compliant']:
                compliant_count += 1
            
            violation_count += len(validation_result['violations'])
            warning_count += len(validation_result['warnings'])
            
            if validation_result['violations']:
                self.stdout.write(f'    Invoice {invoice.numer}: {len(validation_result["violations"])} violations')
        
        compliance_rate = (compliant_count / min(total_invoices, 10) * 100) if total_invoices > 0 else 100
        
        self.stdout.write(f'  Validation Results (sample of {min(total_invoices, 10)} invoices):')
        self.stdout.write(f'    Compliant: {compliant_count}')
        self.stdout.write(f'    Compliance rate: {compliance_rate:.1f}%')
        self.stdout.write(f'    Total violations: {violation_count}')
        self.stdout.write(f'    Total warnings: {warning_count}')
        
        self.stdout.write(self.style.SUCCESS('✓ Invoice validation completed'))
    
    def _run_basic_monitoring(self):
        """Run basic compliance monitoring checks"""
        self.stdout.write('Running basic compliance monitoring...')
        
        from faktury.models import SecurityAuditLog, DataRetentionPolicy, ComplianceReport
        
        # Check recent security events
        recent_violations = SecurityAuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24),
            success=False
        ).count()
        
        if recent_violations > 0:
            self.stdout.write(f'  ⚠️  {recent_violations} security violations in last 24 hours')
        else:
            self.stdout.write(f'  ✓ No security violations in last 24 hours')
        
        # Check data retention policies
        policies_count = DataRetentionPolicy.objects.count()
        active_policies = DataRetentionPolicy.objects.filter(auto_cleanup=True).count()
        
        self.stdout.write(f'  Data retention policies: {policies_count} total, {active_policies} active')
        
        # Check recent compliance reports
        recent_reports = ComplianceReport.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        self.stdout.write(f'  Compliance reports in last 7 days: {recent_reports}')
        
        # Check system health
        from faktury.models import SystemHealthMetric
        
        recent_health = SystemHealthMetric.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).first()
        
        if recent_health:
            self.stdout.write(f'  System health: {recent_health.get_status_display()}')
        else:
            self.stdout.write(f'  ⚠️  No recent system health data')
        
        self.stdout.write(self.style.SUCCESS('✓ Basic monitoring completed'))