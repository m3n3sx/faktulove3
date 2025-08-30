"""
GDPR Data Service for FaktuLove
Handles user data export, import, and deletion according to GDPR requirements
"""

import json
import logging
import zipfile
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, IO
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class GDPRDataService:
    """
    Service for handling GDPR data requests
    """
    
    def __init__(self):
        self.export_logger = logging.getLogger('gdpr_export')
    
    def export_user_data(self, user: User, format: str = 'json') -> Dict[str, Any]:
        """
        Export all user data in compliance with GDPR Article 20 (Right to data portability)
        
        Args:
            user: User whose data to export
            format: Export format ('json', 'csv', 'xml')
            
        Returns:
            Dictionary containing export information
        """
        try:
            export_data = {
                'export_info': {
                    'user_id': user.id,
                    'username': user.username,
                    'export_date': timezone.now().isoformat(),
                    'format': format,
                    'gdpr_article': 'Article 20 - Right to data portability'
                },
                'personal_data': self._export_personal_data(user),
                'business_data': self._export_business_data(user),
                'document_data': self._export_document_data(user),
                'system_data': self._export_system_data(user),
                'audit_data': self._export_audit_data(user)
            }
            
            # Log the export
            self._log_data_export(user, export_data)
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting user data for user {user.id}: {e}")
            raise
    
    def _export_personal_data(self, user: User) -> Dict[str, Any]:
        """Export personal data"""
        personal_data = {
            'user_account': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
        }
        
        # User profile data
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            personal_data['profile'] = {
                'imie': profile.imie,
                'nazwisko': profile.nazwisko,
                'telefon': profile.telefon,
                'avatar': profile.avatar.url if profile.avatar else None
            }
        
        return personal_data
    
    def _export_business_data(self, user: User) -> Dict[str, Any]:
        """Export business-related data"""
        business_data = {}
        
        # Company data
        if hasattr(user, 'firma'):
            company = user.firma
            business_data['company'] = {
                'id': company.id,
                'nazwa': company.nazwa,
                'nip': company.nip,
                'regon': company.regon,
                'ulica': company.ulica,
                'numer_domu': company.numer_domu,
                'numer_mieszkania': company.numer_mieszkania,
                'kod_pocztowy': company.kod_pocztowy,
                'miejscowosc': company.miejscowosc,
                'kraj': company.kraj,
                'logo': company.logo.url if company.logo else None
            }
        
        # Contractors
        from faktury.models import Kontrahent
        contractors = Kontrahent.objects.filter(user=user)
        business_data['contractors'] = []
        
        for contractor in contractors:
            business_data['contractors'].append({
                'id': contractor.id,
                'nazwa': contractor.nazwa,
                'nip': contractor.nip,
                'regon': contractor.regon,
                'adres': contractor.adres,
                'kod_pocztowy': contractor.kod_pocztowy,
                'miejscowosc': contractor.miejscowosc,
                'kraj': contractor.kraj,
                'telefon': contractor.telefon,
                'email': contractor.email,
                'is_own_company': contractor.is_own_company
            })
        
        # Products
        from faktury.models import Produkt
        products = Produkt.objects.filter(user=user)
        business_data['products'] = []
        
        for product in products:
            business_data['products'].append({
                'id': product.id,
                'nazwa': product.nazwa,
                'opis': product.opis,
                'cena_netto': str(product.cena_netto),
                'stawka_vat': str(product.stawka_vat),
                'jednostka': product.jednostka,
                'kod_produktu': product.kod_produktu,
                'kategoria': product.kategoria
            })
        
        return business_data
    
    def _export_document_data(self, user: User) -> Dict[str, Any]:
        """Export document-related data"""
        document_data = {}
        
        # Invoices
        from faktury.models import Faktura, PozycjaFaktury
        invoices = Faktura.objects.filter(user=user)
        document_data['invoices'] = []
        
        for invoice in invoices:
            invoice_data = {
                'id': invoice.id,
                'numer': invoice.numer,
                'typ_dokumentu': invoice.typ_dokumentu,
                'data_wystawienia': invoice.data_wystawienia.isoformat() if invoice.data_wystawienia else None,
                'data_sprzedazy': invoice.data_sprzedazy.isoformat() if invoice.data_sprzedazy else None,
                'termin_platnosci': invoice.termin_platnosci.isoformat() if invoice.termin_platnosci else None,
                'sposob_platnosci': invoice.sposob_platnosci,
                'status': invoice.status,
                'kwota_netto': str(invoice.kwota_netto),
                'kwota_vat': str(invoice.kwota_vat),
                'kwota_brutto': str(invoice.kwota_brutto),
                'uwagi': invoice.uwagi,
                'kontrahent_id': invoice.kontrahent.id if invoice.kontrahent else None,
                'positions': []
            }
            
            # Invoice positions
            positions = PozycjaFaktury.objects.filter(faktura=invoice)
            for position in positions:
                invoice_data['positions'].append({
                    'id': position.id,
                    'nazwa': position.nazwa,
                    'ilosc': str(position.ilosc),
                    'jednostka': position.jednostka,
                    'cena_netto': str(position.cena_netto),
                    'stawka_vat': str(position.stawka_vat),
                    'wartosc_netto': str(position.wartosc_netto),
                    'wartosc_vat': str(position.wartosc_vat),
                    'wartosc_brutto': str(position.wartosc_brutto)
                })
            
            document_data['invoices'].append(invoice_data)
        
        # Recurring invoices
        from faktury.models import FakturaCykliczna
        recurring_invoices = FakturaCykliczna.objects.filter(user=user)
        document_data['recurring_invoices'] = []
        
        for recurring in recurring_invoices:
            document_data['recurring_invoices'].append({
                'id': recurring.id,
                'nazwa': recurring.nazwa,
                'cykl': recurring.cykl,
                'data_rozpoczecia': recurring.data_rozpoczecia.isoformat() if recurring.data_rozpoczecia else None,
                'data_zakonczenia': recurring.data_zakonczenia.isoformat() if recurring.data_zakonczenia else None,
                'aktywna': recurring.aktywna,
                'szablon_faktury_id': recurring.szablon_faktury.id if recurring.szablon_faktury else None
            })
        
        return document_data
    
    def _export_system_data(self, user: User) -> Dict[str, Any]:
        """Export system-related data"""
        system_data = {}
        
        # Teams and partnerships
        from faktury.models import Zespol, CzlonekZespolu, Partnerstwo
        
        # Teams where user is a member
        team_memberships = CzlonekZespolu.objects.filter(user=user)
        system_data['team_memberships'] = []
        
        for membership in team_memberships:
            system_data['team_memberships'].append({
                'team_id': membership.zespol.id,
                'team_name': membership.zespol.nazwa,
                'role': membership.rola,
                'joined_date': membership.data_dolaczenia.isoformat() if membership.data_dolaczenia else None
            })
        
        # Partnerships
        partnerships = Partnerstwo.objects.filter(
            models.Q(firma1__user=user) | models.Q(firma2__user=user)
        )
        system_data['partnerships'] = []
        
        for partnership in partnerships:
            system_data['partnerships'].append({
                'id': partnership.id,
                'typ_partnerstwa': partnership.typ_partnerstwa,
                'data_rozpoczecia': partnership.data_rozpoczecia.isoformat() if partnership.data_rozpoczecia else None,
                'data_zakonczenia': partnership.data_zakonczenia.isoformat() if partnership.data_zakonczenia else None,
                'aktywne': partnership.aktywne,
                'firma1_id': partnership.firma1.id,
                'firma2_id': partnership.firma2.id
            })
        
        # Messages
        from faktury.models import Wiadomosc
        messages = Wiadomosc.objects.filter(
            models.Q(nadawca=user) | models.Q(odbiorca=user)
        )
        system_data['messages'] = []
        
        for message in messages:
            system_data['messages'].append({
                'id': message.id,
                'tytul': message.tytul,
                'tresc': message.tresc,
                'data_wyslania': message.data_wyslania.isoformat(),
                'przeczytana': message.przeczytana,
                'typ_wiadomosci': message.typ_wiadomosci,
                'nadawca_id': message.nadawca.id if message.nadawca else None,
                'odbiorca_id': message.odbiorca.id if message.odbiorca else None
            })
        
        return system_data
    
    def _export_audit_data(self, user: User) -> Dict[str, Any]:
        """Export audit and security data"""
        audit_data = {}
        
        # Security audit logs
        from faktury.models import SecurityAuditLog
        audit_logs = SecurityAuditLog.objects.filter(user=user).order_by('-timestamp')[:100]  # Last 100 entries
        audit_data['security_logs'] = []
        
        for log in audit_logs:
            audit_data['security_logs'].append({
                'id': log.id,
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'timestamp': log.timestamp.isoformat(),
                'ip_address': log.ip_address,
                'success': log.success,
                'risk_level': log.risk_level
            })
        
        # OCR processing data
        from faktury.models import DocumentUpload, OCRResult
        
        # Document uploads
        uploads = DocumentUpload.objects.filter(user=user)
        audit_data['document_uploads'] = []
        
        for upload in uploads:
            audit_data['document_uploads'].append({
                'id': upload.id,
                'original_filename': upload.original_filename,
                'file_size': upload.file_size,
                'mime_type': upload.mime_type,
                'upload_timestamp': upload.upload_timestamp.isoformat(),
                'processing_status': upload.processing_status
            })
        
        # OCR results
        ocr_results = OCRResult.objects.filter(document__user=user)
        audit_data['ocr_results'] = []
        
        for result in ocr_results:
            audit_data['ocr_results'].append({
                'id': result.id,
                'confidence_score': float(result.confidence_score),
                'processing_time': float(result.processing_time),
                'engine_used': result.engine_used,
                'created_at': result.created_at.isoformat(),
                'document_id': result.document.id
            })
        
        return audit_data
    
    def create_data_export_file(self, user: User, format: str = 'json') -> tuple:
        """
        Create a downloadable file with user's data
        
        Args:
            user: User whose data to export
            format: Export format
            
        Returns:
            Tuple of (file_content, filename, content_type)
        """
        try:
            export_data = self.export_user_data(user, format)
            
            if format == 'json':
                content = json.dumps(export_data, indent=2, ensure_ascii=False)
                filename = f'gdpr_export_{user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                content_type = 'application/json'
            
            elif format == 'zip':
                # Create ZIP file with multiple formats
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
                
                with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Add JSON export
                    json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
                    zip_file.writestr('data_export.json', json_content.encode('utf-8'))
                    
                    # Add CSV exports for tabular data
                    self._add_csv_to_zip(zip_file, export_data)
                    
                    # Add README
                    readme_content = self._create_export_readme(user, export_data)
                    zip_file.writestr('README.txt', readme_content.encode('utf-8'))
                
                with open(temp_file.name, 'rb') as f:
                    content = f.read()
                
                os.unlink(temp_file.name)  # Clean up temp file
                
                filename = f'gdpr_export_{user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
                content_type = 'application/zip'
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return content, filename, content_type
            
        except Exception as e:
            logger.error(f"Error creating export file for user {user.id}: {e}")
            raise
    
    def _add_csv_to_zip(self, zip_file: zipfile.ZipFile, export_data: Dict) -> None:
        """Add CSV files to ZIP export"""
        import csv
        import io
        
        # Export invoices as CSV
        if export_data.get('document_data', {}).get('invoices'):
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            
            # Header
            writer.writerow([
                'ID', 'Numer', 'Typ', 'Data wystawienia', 'Data sprzedaży',
                'Termin płatności', 'Status', 'Kwota netto', 'Kwota VAT', 'Kwota brutto'
            ])
            
            # Data
            for invoice in export_data['document_data']['invoices']:
                writer.writerow([
                    invoice['id'], invoice['numer'], invoice['typ_dokumentu'],
                    invoice['data_wystawienia'], invoice['data_sprzedazy'],
                    invoice['termin_platnosci'], invoice['status'],
                    invoice['kwota_netto'], invoice['kwota_vat'], invoice['kwota_brutto']
                ])
            
            zip_file.writestr('invoices.csv', csv_buffer.getvalue().encode('utf-8'))
        
        # Export contractors as CSV
        if export_data.get('business_data', {}).get('contractors'):
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            
            # Header
            writer.writerow([
                'ID', 'Nazwa', 'NIP', 'REGON', 'Adres', 'Kod pocztowy',
                'Miejscowość', 'Telefon', 'Email'
            ])
            
            # Data
            for contractor in export_data['business_data']['contractors']:
                writer.writerow([
                    contractor['id'], contractor['nazwa'], contractor['nip'],
                    contractor['regon'], contractor['adres'], contractor['kod_pocztowy'],
                    contractor['miejscowosc'], contractor['telefon'], contractor['email']
                ])
            
            zip_file.writestr('contractors.csv', csv_buffer.getvalue().encode('utf-8'))
    
    def _create_export_readme(self, user: User, export_data: Dict) -> str:
        """Create README file for data export"""
        readme = f"""
GDPR Data Export for {user.username}
=====================================

Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
User ID: {user.id}
GDPR Article: Article 20 - Right to data portability

This export contains all personal data associated with your account
in compliance with the General Data Protection Regulation (GDPR).

Files included:
- data_export.json: Complete data export in JSON format
- invoices.csv: Invoice data in CSV format
- contractors.csv: Contractor data in CSV format
- README.txt: This file

Data categories included:
- Personal account information
- Business data (company, contractors, products)
- Document data (invoices, recurring invoices)
- System data (teams, partnerships, messages)
- Audit data (security logs, OCR processing)

Data summary:
- Invoices: {len(export_data.get('document_data', {}).get('invoices', []))}
- Contractors: {len(export_data.get('business_data', {}).get('contractors', []))}
- Products: {len(export_data.get('business_data', {}).get('products', []))}
- Security logs: {len(export_data.get('audit_data', {}).get('security_logs', []))}

If you have any questions about this export or your data rights,
please contact our support team.

For more information about GDPR and your rights, visit:
https://gdpr.eu/what-is-gdpr/
        """.strip()
        
        return readme
    
    def delete_user_data(self, user: User, verification_code: str) -> Dict[str, Any]:
        """
        Delete user data in compliance with GDPR Article 17 (Right to erasure)
        
        Args:
            user: User whose data to delete
            verification_code: Verification code for safety
            
        Returns:
            Dictionary with deletion results
        """
        try:
            # Verify deletion code (implement your verification logic)
            if not self._verify_deletion_code(user, verification_code):
                raise ValidationError("Invalid verification code")
            
            deletion_result = {
                'user_id': user.id,
                'username': user.username,
                'deletion_date': timezone.now().isoformat(),
                'deleted_data': {},
                'retained_data': {},
                'gdpr_article': 'Article 17 - Right to erasure'
            }
            
            with transaction.atomic():
                # Log the deletion request first
                self._log_data_deletion(user, deletion_result)
                
                # Delete user data according to retention policies
                deletion_result['deleted_data'] = self._perform_data_deletion(user)
                
                # Identify data that must be retained for legal reasons
                deletion_result['retained_data'] = self._identify_retained_data(user)
                
                # Anonymize the user account instead of deleting it completely
                self._anonymize_user_account(user)
            
            return deletion_result
            
        except Exception as e:
            logger.error(f"Error deleting user data for user {user.id}: {e}")
            raise
    
    def _verify_deletion_code(self, user: User, code: str) -> bool:
        """Verify deletion verification code"""
        # Implement your verification logic here
        # This could be a code sent via email, SMS, etc.
        return len(code) >= 6  # Simple check for demo
    
    def _perform_data_deletion(self, user: User) -> Dict[str, int]:
        """Perform actual data deletion"""
        deleted_counts = {}
        
        # Delete non-essential data
        from faktury.models import (
            SecurityAuditLog, DocumentUpload, OCRResult,
            Wiadomosc, CzlonekZespolu
        )
        
        # Delete security logs (except critical ones)
        non_critical_logs = SecurityAuditLog.objects.filter(
            user=user,
            risk_level__in=['low', 'medium']
        )
        deleted_counts['security_logs'] = non_critical_logs.count()
        non_critical_logs.delete()
        
        # Delete OCR uploads and results
        ocr_results = OCRResult.objects.filter(document__user=user)
        deleted_counts['ocr_results'] = ocr_results.count()
        ocr_results.delete()
        
        uploads = DocumentUpload.objects.filter(user=user)
        deleted_counts['document_uploads'] = uploads.count()
        uploads.delete()
        
        # Delete messages (non-business critical)
        personal_messages = Wiadomosc.objects.filter(
            models.Q(nadawca=user) | models.Q(odbiorca=user),
            typ_wiadomosci='osobista'
        )
        deleted_counts['personal_messages'] = personal_messages.count()
        personal_messages.delete()
        
        # Remove from teams
        team_memberships = CzlonekZespolu.objects.filter(user=user)
        deleted_counts['team_memberships'] = team_memberships.count()
        team_memberships.delete()
        
        return deleted_counts
    
    def _identify_retained_data(self, user: User) -> Dict[str, Any]:
        """Identify data that must be retained for legal reasons"""
        retained_data = {}
        
        from faktury.models import Faktura, SecurityAuditLog
        
        # Invoices must be retained for tax purposes (5 years in Poland)
        invoices_count = Faktura.objects.filter(user=user).count()
        retained_data['invoices'] = {
            'count': invoices_count,
            'reason': 'Legal requirement - tax records (5 years retention)',
            'anonymized': True
        }
        
        # Critical security logs must be retained
        critical_logs = SecurityAuditLog.objects.filter(
            user=user,
            risk_level__in=['high', 'critical']
        ).count()
        retained_data['critical_security_logs'] = {
            'count': critical_logs,
            'reason': 'Security and compliance requirements',
            'anonymized': True
        }
        
        return retained_data
    
    def _anonymize_user_account(self, user: User) -> None:
        """Anonymize user account while retaining necessary business data"""
        # Generate anonymous identifier
        anonymous_id = f"deleted_user_{user.id}_{int(timezone.now().timestamp())}"
        
        # Anonymize personal data
        user.username = anonymous_id
        user.email = f"{anonymous_id}@deleted.local"
        user.first_name = "Deleted"
        user.last_name = "User"
        user.is_active = False
        user.set_unusable_password()
        user.save()
        
        # Anonymize company data if exists
        if hasattr(user, 'firma'):
            company = user.firma
            company.nazwa = f"Deleted Company {company.id}"
            company.nip = None
            company.regon = None
            company.save()
        
        # Anonymize profile data if exists
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            profile.imie = "Deleted"
            profile.nazwisko = "User"
            profile.telefon = ""
            if profile.avatar:
                profile.avatar.delete()
            profile.save()
    
    def _log_data_export(self, user: User, export_data: Dict) -> None:
        """Log data export for audit purposes"""
        try:
            from faktury.services.security_service import SecurityService
            
            security_service = SecurityService()
            security_service.create_audit_log(
                user=user,
                action='data_export',
                resource_type='user',
                resource_id=str(user.id),
                details={
                    'export_format': export_data['export_info']['format'],
                    'data_categories': list(export_data.keys()),
                    'gdpr_article': 'Article 20'
                },
                success=True
            )
            
        except Exception as e:
            logger.error(f"Failed to log data export: {e}")
    
    def _log_data_deletion(self, user: User, deletion_result: Dict) -> None:
        """Log data deletion for audit purposes"""
        try:
            from faktury.services.security_service import SecurityService
            
            security_service = SecurityService()
            security_service.create_audit_log(
                user=user,
                action='data_deletion',
                resource_type='user',
                resource_id=str(user.id),
                details={
                    'gdpr_article': 'Article 17',
                    'deletion_timestamp': deletion_result['deletion_date']
                },
                success=True
            )
            
        except Exception as e:
            logger.error(f"Failed to log data deletion: {e}")


# Import models at the end to avoid circular imports
from django.db import models