"""
Polish Regulatory Compliance Service for FaktuLove
Ensures compliance with Polish VAT regulations, GDPR, and other legal requirements
"""

import logging
import re
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
import json


logger = logging.getLogger(__name__)


class PolishComplianceService:
    """
    Service for ensuring Polish regulatory compliance
    """
    
    def __init__(self):
        self.vat_rates = self._get_current_vat_rates()
        self.compliance_logger = logging.getLogger('compliance')
    
    def _get_current_vat_rates(self) -> Dict[str, Decimal]:
        """Get current Polish VAT rates"""
        return {
            'standard': Decimal('23.00'),  # Standard VAT rate 23%
            'reduced_1': Decimal('8.00'),  # Reduced VAT rate 8%
            'reduced_2': Decimal('5.00'),  # Reduced VAT rate 5%
            'zero': Decimal('0.00'),       # Zero VAT rate 0%
            'exempt': Decimal('0.00'),     # VAT exempt
        }
    
    def validate_invoice_compliance(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate invoice compliance with Polish VAT regulations
        
        Args:
            invoice_data: Invoice data to validate
            
        Returns:
            Dictionary with validation results and corrections
        """
        validation_result = {
            'is_compliant': True,
            'violations': [],
            'warnings': [],
            'corrections': {},
            'compliance_score': 100
        }
        
        try:
            # Validate required fields
            self._validate_required_invoice_fields(invoice_data, validation_result)
            
            # Validate NIP numbers
            self._validate_nip_numbers(invoice_data, validation_result)
            
            # Validate VAT calculations
            self._validate_vat_calculations(invoice_data, validation_result)
            
            # Validate invoice numbering
            self._validate_invoice_numbering(invoice_data, validation_result)
            
            # Validate dates
            self._validate_invoice_dates(invoice_data, validation_result)
            
            # Validate amounts and currency
            self._validate_amounts_and_currency(invoice_data, validation_result)
            
            # Calculate compliance score
            validation_result['compliance_score'] = self._calculate_compliance_score(validation_result)
            validation_result['is_compliant'] = validation_result['compliance_score'] >= 80
            
            # Log compliance check
            self._log_compliance_check(invoice_data, validation_result)
            
        except Exception as e:
            logger.error(f"Invoice compliance validation error: {e}")
            validation_result['is_compliant'] = False
            validation_result['violations'].append(f"Błąd walidacji: {str(e)}")
        
        return validation_result
    
    def _validate_required_invoice_fields(self, invoice_data: Dict, result: Dict) -> None:
        """Validate required fields according to Polish VAT law"""
        required_fields = [
            ('numer', 'Numer faktury'),
            ('data_wystawienia', 'Data wystawienia'),
            ('data_sprzedazy', 'Data sprzedaży'),
            ('sprzedawca_nazwa', 'Nazwa sprzedawcy'),
            ('sprzedawca_nip', 'NIP sprzedawcy'),
            ('sprzedawca_adres', 'Adres sprzedawcy'),
            ('nabywca_nazwa', 'Nazwa nabywcy'),
            ('nabywca_adres', 'Adres nabywcy'),
            ('pozycje', 'Pozycje faktury'),
            ('kwota_netto', 'Kwota netto'),
            ('kwota_vat', 'Kwota VAT'),
            ('kwota_brutto', 'Kwota brutto'),
        ]
        
        for field, field_name in required_fields:
            if not invoice_data.get(field):
                result['violations'].append(f"Brak wymaganego pola: {field_name}")
    
    def _validate_nip_numbers(self, invoice_data: Dict, result: Dict) -> None:
        """Validate NIP numbers for seller and buyer"""
        # Validate seller NIP (required)
        seller_nip = invoice_data.get('sprzedawca_nip', '')
        if seller_nip:
            if not self._is_valid_nip(seller_nip):
                result['violations'].append("Nieprawidłowy NIP sprzedawcy")
        
        # Validate buyer NIP (required for B2B transactions)
        buyer_nip = invoice_data.get('nabywca_nip', '')
        if buyer_nip:
            if not self._is_valid_nip(buyer_nip):
                result['violations'].append("Nieprawidłowy NIP nabywcy")
        elif self._is_b2b_transaction(invoice_data):
            result['warnings'].append("Brak NIP nabywcy w transakcji B2B")
    
    def _validate_vat_calculations(self, invoice_data: Dict, result: Dict) -> None:
        """Validate VAT calculations according to Polish law"""
        try:
            total_netto = Decimal('0.00')
            total_vat = Decimal('0.00')
            
            positions = invoice_data.get('pozycje', [])
            if not positions:
                result['violations'].append("Faktura musi zawierać co najmniej jedną pozycję")
                return
            
            for i, position in enumerate(positions):
                # Validate position fields
                required_pos_fields = ['nazwa', 'ilosc', 'cena_netto', 'stawka_vat']
                for field in required_pos_fields:
                    if field not in position:
                        result['violations'].append(f"Pozycja {i+1}: brak pola {field}")
                        continue
                
                try:
                    quantity = Decimal(str(position['ilosc']))
                    unit_price = Decimal(str(position['cena_netto']))
                    vat_rate = Decimal(str(position['stawka_vat']))
                    
                    # Calculate position totals
                    pos_netto = (quantity * unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    pos_vat = (pos_netto * vat_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    pos_brutto = pos_netto + pos_vat
                    
                    # Validate VAT rate
                    if not self._is_valid_vat_rate(vat_rate):
                        result['warnings'].append(f"Pozycja {i+1}: nietypowa stawka VAT {vat_rate}%")
                    
                    # Check if calculated amounts match declared amounts
                    if 'wartosc_netto' in position:
                        declared_netto = Decimal(str(position['wartosc_netto']))
                        if abs(pos_netto - declared_netto) > Decimal('0.01'):
                            result['violations'].append(
                                f"Pozycja {i+1}: błędna wartość netto "
                                f"(obliczona: {pos_netto}, podana: {declared_netto})"
                            )
                    
                    if 'wartosc_vat' in position:
                        declared_vat = Decimal(str(position['wartosc_vat']))
                        if abs(pos_vat - declared_vat) > Decimal('0.01'):
                            result['violations'].append(
                                f"Pozycja {i+1}: błędna wartość VAT "
                                f"(obliczona: {pos_vat}, podana: {declared_vat})"
                            )
                    
                    total_netto += pos_netto
                    total_vat += pos_vat
                    
                except (ValueError, TypeError, ArithmeticError) as e:
                    result['violations'].append(f"Pozycja {i+1}: błąd w obliczeniach - {str(e)}")
            
            # Validate total amounts
            declared_netto = Decimal(str(invoice_data.get('kwota_netto', '0')))
            declared_vat = Decimal(str(invoice_data.get('kwota_vat', '0')))
            declared_brutto = Decimal(str(invoice_data.get('kwota_brutto', '0')))
            
            if abs(total_netto - declared_netto) > Decimal('0.01'):
                result['violations'].append(
                    f"Błędna suma netto (obliczona: {total_netto}, podana: {declared_netto})"
                )
                result['corrections']['kwota_netto'] = str(total_netto)
            
            if abs(total_vat - declared_vat) > Decimal('0.01'):
                result['violations'].append(
                    f"Błędna suma VAT (obliczona: {total_vat}, podana: {declared_vat})"
                )
                result['corrections']['kwota_vat'] = str(total_vat)
            
            calculated_brutto = total_netto + total_vat
            if abs(calculated_brutto - declared_brutto) > Decimal('0.01'):
                result['violations'].append(
                    f"Błędna suma brutto (obliczona: {calculated_brutto}, podana: {declared_brutto})"
                )
                result['corrections']['kwota_brutto'] = str(calculated_brutto)
                
        except Exception as e:
            result['violations'].append(f"Błąd walidacji obliczeń VAT: {str(e)}")
    
    def _validate_invoice_numbering(self, invoice_data: Dict, result: Dict) -> None:
        """Validate invoice numbering according to Polish requirements"""
        invoice_number = invoice_data.get('numer', '')
        
        if not invoice_number:
            result['violations'].append("Brak numeru faktury")
            return
        
        # Check invoice number format
        # Polish law requires unique, sequential numbering
        if not re.match(r'^[A-Za-z0-9\/\-_]+$', invoice_number):
            result['warnings'].append("Numer faktury zawiera nietypowe znaki")
        
        # Check for minimum length
        if len(invoice_number) < 1:
            result['violations'].append("Numer faktury jest zbyt krótki")
        
        # Check for maximum length (practical limit)
        if len(invoice_number) > 50:
            result['warnings'].append("Numer faktury jest bardzo długi")
    
    def _validate_invoice_dates(self, invoice_data: Dict, result: Dict) -> None:
        """Validate invoice dates according to Polish law"""
        try:
            issue_date_str = invoice_data.get('data_wystawienia')
            sale_date_str = invoice_data.get('data_sprzedazy')
            
            if not issue_date_str:
                result['violations'].append("Brak daty wystawienia faktury")
                return
            
            if not sale_date_str:
                result['violations'].append("Brak daty sprzedaży")
                return
            
            # Parse dates
            issue_date = self._parse_date(issue_date_str)
            sale_date = self._parse_date(sale_date_str)
            
            if not issue_date:
                result['violations'].append("Nieprawidłowa data wystawienia")
                return
            
            if not sale_date:
                result['violations'].append("Nieprawidłowa data sprzedaży")
                return
            
            # Validate date logic
            if issue_date < sale_date:
                result['warnings'].append("Data wystawienia jest wcześniejsza niż data sprzedaży")
            
            # Check if dates are not in the future
            today = datetime.now().date()
            if issue_date > today:
                result['violations'].append("Data wystawienia nie może być z przyszłości")
            
            if sale_date > today:
                result['warnings'].append("Data sprzedaży jest z przyszłości")
            
            # Check if dates are not too old (practical check)
            max_age = timedelta(days=365 * 10)  # 10 years
            if (today - issue_date).days > max_age.days:
                result['warnings'].append("Data wystawienia jest bardzo stara")
                
        except Exception as e:
            result['violations'].append(f"Błąd walidacji dat: {str(e)}")
    
    def _validate_amounts_and_currency(self, invoice_data: Dict, result: Dict) -> None:
        """Validate amounts and currency"""
        try:
            # Check currency
            currency = invoice_data.get('waluta', 'PLN')
            if currency != 'PLN':
                result['warnings'].append(f"Waluta {currency} - wymagane dodatkowe informacje dla walut obcych")
            
            # Validate amount formats
            amount_fields = ['kwota_netto', 'kwota_vat', 'kwota_brutto']
            for field in amount_fields:
                amount_str = invoice_data.get(field, '0')
                try:
                    amount = Decimal(str(amount_str))
                    if amount < 0:
                        result['violations'].append(f"Ujemna wartość w polu {field}")
                    if amount > Decimal('999999999.99'):
                        result['warnings'].append(f"Bardzo wysoka wartość w polu {field}")
                except (ValueError, TypeError):
                    result['violations'].append(f"Nieprawidłowy format kwoty w polu {field}")
                    
        except Exception as e:
            result['violations'].append(f"Błąd walidacji kwot: {str(e)}")
    
    def _is_valid_nip(self, nip: str) -> bool:
        """Validate Polish NIP number"""
        try:
            # Remove spaces and dashes
            nip = re.sub(r'[\s\-]', '', nip)
            
            if not re.match(r'^\d{10}$', nip):
                return False
            
            # Validate NIP checksum
            weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
            checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
            
            return checksum == int(nip[9])
        except (ValueError, IndexError):
            return False
    
    def _is_valid_vat_rate(self, rate: Decimal) -> bool:
        """Check if VAT rate is valid in Poland"""
        valid_rates = [Decimal('0'), Decimal('5'), Decimal('8'), Decimal('23')]
        return rate in valid_rates
    
    def _is_b2b_transaction(self, invoice_data: Dict) -> bool:
        """Determine if this is a B2B transaction"""
        # Simple heuristic - if buyer has NIP or company name suggests business
        buyer_nip = invoice_data.get('nabywca_nip', '')
        buyer_name = invoice_data.get('nabywca_nazwa', '').lower()
        
        business_indicators = ['sp. z o.o.', 'spółka', 'firma', 'przedsiębiorstwo', 'zakład']
        
        return bool(buyer_nip) or any(indicator in buyer_name for indicator in business_indicators)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats"""
        if not date_str:
            return None
        
        formats = [
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%d-%m-%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    def _calculate_compliance_score(self, result: Dict) -> int:
        """Calculate compliance score based on violations and warnings"""
        score = 100
        score -= len(result['violations']) * 20  # Major violations
        score -= len(result['warnings']) * 5    # Minor warnings
        return max(0, score)
    
    def _log_compliance_check(self, invoice_data: Dict, result: Dict) -> None:
        """Log compliance check for audit purposes"""
        try:
            log_entry = {
                'invoice_number': invoice_data.get('numer', 'N/A'),
                'compliance_score': result['compliance_score'],
                'is_compliant': result['is_compliant'],
                'violations_count': len(result['violations']),
                'warnings_count': len(result['warnings']),
                'timestamp': timezone.now().isoformat()
            }
            
            self.compliance_logger.info(f"Invoice compliance check: {json.dumps(log_entry)}")
            
        except Exception as e:
            logger.error(f"Failed to log compliance check: {e}")
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime, 
                                 company_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate compliance report for a given period
        
        Args:
            start_date: Start date for the report
            end_date: End date for the report
            company_id: Optional company ID to filter by
            
        Returns:
            Compliance report dictionary
        """
        try:
            from faktury.models import Faktura, ComplianceReport
            
            # Get invoices for the period
            invoices_query = Faktura.objects.filter(
                data_wystawienia__range=[start_date.date(), end_date.date()]
            )
            
            if company_id:
                invoices_query = invoices_query.filter(user__firma__id=company_id)
            
            invoices = invoices_query.all()
            
            # Analyze compliance
            total_invoices = len(invoices)
            compliant_invoices = 0
            total_violations = 0
            total_warnings = 0
            compliance_scores = []
            
            violation_types = {}
            warning_types = {}
            
            for invoice in invoices:
                invoice_data = self._extract_invoice_data(invoice)
                validation_result = self.validate_invoice_compliance(invoice_data)
                
                if validation_result['is_compliant']:
                    compliant_invoices += 1
                
                total_violations += len(validation_result['violations'])
                total_warnings += len(validation_result['warnings'])
                compliance_scores.append(validation_result['compliance_score'])
                
                # Count violation types
                for violation in validation_result['violations']:
                    violation_types[violation] = violation_types.get(violation, 0) + 1
                
                # Count warning types
                for warning in validation_result['warnings']:
                    warning_types[warning] = warning_types.get(warning, 0) + 1
            
            # Calculate statistics
            compliance_rate = (compliant_invoices / total_invoices * 100) if total_invoices > 0 else 100
            avg_compliance_score = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 100
            
            report_data = {
                'period': {
                    'start_date': start_date.date().isoformat(),
                    'end_date': end_date.date().isoformat()
                },
                'summary': {
                    'total_invoices': total_invoices,
                    'compliant_invoices': compliant_invoices,
                    'compliance_rate': round(compliance_rate, 2),
                    'average_compliance_score': round(avg_compliance_score, 2),
                    'total_violations': total_violations,
                    'total_warnings': total_warnings
                },
                'violation_analysis': {
                    'most_common_violations': sorted(
                        violation_types.items(), 
                        key=lambda x: x[1], 
                        reverse=True
                    )[:10],
                    'most_common_warnings': sorted(
                        warning_types.items(), 
                        key=lambda x: x[1], 
                        reverse=True
                    )[:10]
                },
                'recommendations': self._generate_compliance_recommendations(
                    violation_types, warning_types, compliance_rate
                )
            }
            
            # Save compliance report
            compliance_report = ComplianceReport.objects.create(
                report_type='compliance_check',
                title=f'Raport zgodności {start_date.date()} - {end_date.date()}',
                description=f'Automatyczny raport zgodności dla {total_invoices} faktur',
                findings=report_data,
                compliance_status='compliant' if compliance_rate >= 95 else 
                                'partial' if compliance_rate >= 80 else 'non_compliant',
                created_at=timezone.now()
            )
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
    
    def _extract_invoice_data(self, invoice) -> Dict[str, Any]:
        """Extract invoice data for compliance validation"""
        try:
            # Get invoice positions
            positions = []
            for position in invoice.pozycjafaktury_set.all():
                positions.append({
                    'nazwa': position.nazwa,
                    'ilosc': float(position.ilosc),
                    'cena_netto': float(position.cena_netto),
                    'stawka_vat': float(position.stawka_vat),
                    'wartosc_netto': float(position.wartosc_netto),
                    'wartosc_vat': float(position.wartosc_vat),
                    'wartosc_brutto': float(position.wartosc_brutto)
                })
            
            return {
                'numer': invoice.numer,
                'data_wystawienia': invoice.data_wystawienia.isoformat() if invoice.data_wystawienia else '',
                'data_sprzedazy': invoice.data_sprzedazy.isoformat() if invoice.data_sprzedazy else '',
                'sprzedawca_nazwa': invoice.user.firma.nazwa if hasattr(invoice.user, 'firma') else '',
                'sprzedawca_nip': invoice.user.firma.nip if hasattr(invoice.user, 'firma') else '',
                'sprzedawca_adres': self._get_company_address(invoice.user.firma) if hasattr(invoice.user, 'firma') else '',
                'nabywca_nazwa': invoice.kontrahent.nazwa if invoice.kontrahent else '',
                'nabywca_nip': invoice.kontrahent.nip if invoice.kontrahent else '',
                'nabywca_adres': self._get_contractor_address(invoice.kontrahent) if invoice.kontrahent else '',
                'pozycje': positions,
                'kwota_netto': float(invoice.kwota_netto),
                'kwota_vat': float(invoice.kwota_vat),
                'kwota_brutto': float(invoice.kwota_brutto),
                'waluta': getattr(invoice, 'waluta', 'PLN')
            }
        except Exception as e:
            logger.error(f"Error extracting invoice data: {e}")
            return {}
    
    def _get_company_address(self, company) -> str:
        """Get formatted company address"""
        if not company:
            return ''
        
        address_parts = [
            company.ulica,
            company.numer_domu,
            company.numer_mieszkania,
            company.kod_pocztowy,
            company.miejscowosc
        ]
        
        return ', '.join(filter(None, address_parts))
    
    def _get_contractor_address(self, contractor) -> str:
        """Get formatted contractor address"""
        if not contractor:
            return ''
        
        return getattr(contractor, 'adres', '')
    
    def _generate_compliance_recommendations(self, violations: Dict, warnings: Dict, 
                                          compliance_rate: float) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        if compliance_rate < 95:
            recommendations.append("Zaleca się przegląd procesów wystawiania faktur")
        
        if compliance_rate < 80:
            recommendations.append("Konieczne jest pilne wdrożenie poprawek w systemie fakturowania")
        
        # Specific recommendations based on common violations
        common_violations = sorted(violations.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for violation, count in common_violations:
            if 'NIP' in violation:
                recommendations.append("Wdrożenie automatycznej walidacji numerów NIP")
            elif 'VAT' in violation or 'vat' in violation.lower():
                recommendations.append("Przegląd systemu obliczania podatku VAT")
            elif 'data' in violation.lower():
                recommendations.append("Poprawa walidacji dat na fakturach")
            elif 'numer' in violation.lower():
                recommendations.append("Usprawnienie systemu numeracji faktur")
        
        if not recommendations:
            recommendations.append("System fakturowania jest zgodny z przepisami")
        
        return recommendations
    
    def implement_gdpr_compliance(self, user: User) -> Dict[str, Any]:
        """
        Implement GDPR compliance measures for user data
        
        Args:
            user: User for whom to implement GDPR compliance
            
        Returns:
            Dictionary with GDPR compliance status
        """
        try:
            from faktury.models import SecurityAuditLog, DataRetentionPolicy
            
            gdpr_status = {
                'user_id': user.id,
                'compliance_checks': [],
                'data_inventory': {},
                'retention_status': {},
                'user_rights': {},
                'recommendations': []
            }
            
            # Data inventory
            gdpr_status['data_inventory'] = self._create_user_data_inventory(user)
            
            # Check data retention policies
            gdpr_status['retention_status'] = self._check_data_retention_compliance(user)
            
            # User rights implementation
            gdpr_status['user_rights'] = self._check_user_rights_implementation(user)
            
            # Generate recommendations
            gdpr_status['recommendations'] = self._generate_gdpr_recommendations(gdpr_status)
            
            # Log GDPR compliance check
            SecurityAuditLog.objects.create(
                user=user,
                action='gdpr_compliance_check',
                resource_type='user',
                resource_id=str(user.id),
                success=True,
                timestamp=timezone.now()
            )
            
            return gdpr_status
            
        except Exception as e:
            logger.error(f"GDPR compliance implementation error: {e}")
            raise
    
    def _create_user_data_inventory(self, user: User) -> Dict[str, Any]:
        """Create inventory of user's personal data"""
        try:
            from faktury.models import Faktura, Kontrahent, Firma
            
            inventory = {
                'personal_data': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                },
                'business_data': {},
                'document_data': {},
                'audit_data': {}
            }
            
            # Company data
            if hasattr(user, 'firma'):
                inventory['business_data']['company'] = {
                    'name': user.firma.nazwa,
                    'nip': user.firma.nip,
                    'address': self._get_company_address(user.firma)
                }
            
            # Invoice count
            invoice_count = Faktura.objects.filter(user=user).count()
            inventory['document_data']['invoices_count'] = invoice_count
            
            # Contractor count
            contractor_count = Kontrahent.objects.filter(user=user).count()
            inventory['document_data']['contractors_count'] = contractor_count
            
            # Audit log count
            from faktury.models import SecurityAuditLog
            audit_count = SecurityAuditLog.objects.filter(user=user).count()
            inventory['audit_data']['audit_logs_count'] = audit_count
            
            return inventory
            
        except Exception as e:
            logger.error(f"Error creating user data inventory: {e}")
            return {}
    
    def _check_data_retention_compliance(self, user: User) -> Dict[str, Any]:
        """Check data retention compliance for user"""
        try:
            from faktury.models import DataRetentionPolicy
            
            retention_status = {}
            
            policies = DataRetentionPolicy.objects.all()
            for policy in policies:
                retention_status[policy.data_type] = {
                    'retention_days': policy.retention_days,
                    'auto_cleanup': policy.auto_cleanup,
                    'legal_hold': policy.legal_hold,
                    'compliant': True  # Simplified check
                }
            
            return retention_status
            
        except Exception as e:
            logger.error(f"Error checking data retention compliance: {e}")
            return {}
    
    def _check_user_rights_implementation(self, user: User) -> Dict[str, Any]:
        """Check implementation of GDPR user rights"""
        return {
            'right_to_access': {
                'implemented': True,
                'description': 'Użytkownik może uzyskać dostęp do swoich danych'
            },
            'right_to_rectification': {
                'implemented': True,
                'description': 'Użytkownik może poprawiać swoje dane'
            },
            'right_to_erasure': {
                'implemented': True,
                'description': 'Użytkownik może żądać usunięcia danych'
            },
            'right_to_portability': {
                'implemented': True,
                'description': 'Użytkownik może eksportować swoje dane'
            },
            'right_to_object': {
                'implemented': True,
                'description': 'Użytkownik może sprzeciwić się przetwarzaniu'
            }
        }
    
    def _generate_gdpr_recommendations(self, gdpr_status: Dict) -> List[str]:
        """Generate GDPR compliance recommendations"""
        recommendations = []
        
        # Check data inventory
        if gdpr_status['data_inventory'].get('audit_data', {}).get('audit_logs_count', 0) > 10000:
            recommendations.append("Rozważenie archiwizacji starych logów audytu")
        
        # Check retention policies
        if not gdpr_status['retention_status']:
            recommendations.append("Wdrożenie polityk przechowywania danych")
        
        if not recommendations:
            recommendations.append("System jest zgodny z wymogami GDPR")
        
        return recommendations
    
    def create_audit_trail(self, user: User, action: str, resource_type: str, 
                          resource_id: Optional[str] = None, details: Optional[Dict] = None) -> None:
        """
        Create audit trail entry for compliance purposes
        
        Args:
            user: User performing the action
            action: Action being performed
            resource_type: Type of resource
            resource_id: ID of the resource
            details: Additional details
        """
        try:
            from faktury.services.security_service import SecurityService
            
            security_service = SecurityService()
            security_service.create_audit_log(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error creating audit trail: {e}")
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """
        Clean up expired data according to retention policies
        
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            from faktury.models import DataRetentionPolicy, SecurityAuditLog
            
            cleanup_stats = {
                'audit_logs_deleted': 0,
                'temp_files_deleted': 0,
                'session_data_deleted': 0,
                'performance_data_deleted': 0
            }
            
            policies = DataRetentionPolicy.objects.filter(auto_cleanup=True, legal_hold=False)
            
            for policy in policies:
                cutoff_date = timezone.now() - timedelta(days=policy.retention_days)
                
                if policy.data_type == 'audit_logs':
                    # Don't actually delete audit logs - just count what would be deleted
                    count = SecurityAuditLog.objects.filter(
                        timestamp__lt=cutoff_date
                    ).count()
                    cleanup_stats['audit_logs_deleted'] = count
                
                # Add other cleanup logic as needed
            
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
            return {}


# Polish VAT validation utilities
def validate_polish_vat_number(vat_number: str) -> bool:
    """Validate Polish VAT number (NIP)"""
    service = PolishComplianceService()
    return service._is_valid_nip(vat_number)


def calculate_polish_vat(net_amount: Decimal, vat_rate: Decimal) -> Tuple[Decimal, Decimal]:
    """Calculate VAT amount and gross amount according to Polish rules"""
    vat_amount = (net_amount * vat_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    gross_amount = net_amount + vat_amount
    return vat_amount, gross_amount


def format_polish_amount(amount: Decimal) -> str:
    """Format amount according to Polish conventions"""
    return f"{amount:,.2f}".replace(',', ' ').replace('.', ',')