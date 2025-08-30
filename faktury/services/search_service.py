"""
Advanced search and filtering service for FaktuLove system.
Provides comprehensive search functionality for invoices and companies with Polish business criteria.
"""

from django.db import models
from django.db.models import Q, F, Value, CharField, Case, When
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.aggregates import StringAgg
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
import re
import logging

from faktury.models import Faktura, Kontrahent, Firma, Partnerstwo

logger = logging.getLogger(__name__)


class AdvancedSearchService:
    """
    Advanced search service with Polish business criteria support.
    Provides fast and accurate search functionality for invoices and companies.
    """
    
    # Polish NIP validation pattern
    NIP_PATTERN = re.compile(r'^\d{10}$|^\d{3}-\d{3}-\d{2}-\d{2}$|^\d{3}-\d{2}-\d{2}-\d{3}$')
    
    # Polish postal code pattern
    POSTAL_CODE_PATTERN = re.compile(r'^\d{2}-\d{3}$')
    
    # Common Polish VAT rates
    POLISH_VAT_RATES = ['23', '8', '5', '0', 'zw']
    
    def __init__(self):
        self.search_history = []
        self.saved_searches = {}
    
    def search_invoices(
        self,
        query: str = "",
        filters: Dict[str, Any] = None,
        user=None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'data_wystawienia',
        sort_order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Advanced invoice search with Polish business criteria.
        
        Args:
            query: Search query string
            filters: Dictionary of filter criteria
            user: User object for filtering user-specific data
            page: Page number for pagination
            per_page: Items per page
            sort_by: Field to sort by
            sort_order: 'asc' or 'desc'
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Start with base queryset
            queryset = Faktura.objects.select_related(
                'nabywca', 'sprzedawca', 'user', 'source_document'
            ).prefetch_related('pozycjafaktury_set')
            
            # Filter by user if provided
            if user:
                queryset = queryset.filter(user=user)
            
            # Apply text search
            if query:
                queryset = self._apply_text_search(queryset, query)
            
            # Apply filters
            if filters:
                queryset = self._apply_filters(queryset, filters)
            
            # Apply sorting
            queryset = self._apply_sorting(queryset, sort_by, sort_order)
            
            # Get total count before pagination
            total_count = queryset.count()
            
            # Apply pagination
            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)
            
            # Prepare results
            results = []
            for faktura in page_obj:
                results.append(self._serialize_invoice(faktura))
            
            # Save to search history
            self._save_to_history(query, filters, total_count)
            
            return {
                'results': results,
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'search_time': timezone.now(),
                'query': query,
                'filters': filters
            }
            
        except Exception as e:
            logger.error(f"Error in invoice search: {str(e)}")
            return {
                'results': [],
                'total_count': 0,
                'error': str(e)
            }
    
    def search_companies(
        self,
        query: str = "",
        filters: Dict[str, Any] = None,
        user=None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Advanced company search with Polish business criteria.
        """
        try:
            # Start with base queryset
            queryset = Kontrahent.objects.select_related('firma', 'user')
            
            # Filter by user if provided
            if user:
                queryset = queryset.filter(user=user)
            
            # Apply text search
            if query:
                queryset = self._apply_company_text_search(queryset, query)
            
            # Apply filters
            if filters:
                queryset = self._apply_company_filters(queryset, filters)
            
            # Apply sorting
            queryset = queryset.order_by('nazwa')
            
            # Get total count before pagination
            total_count = queryset.count()
            
            # Apply pagination
            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)
            
            # Prepare results
            results = []
            for kontrahent in page_obj:
                results.append(self._serialize_company(kontrahent))
            
            return {
                'results': results,
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'search_time': timezone.now(),
                'query': query,
                'filters': filters
            }
            
        except Exception as e:
            logger.error(f"Error in company search: {str(e)}")
            return {
                'results': [],
                'total_count': 0,
                'error': str(e)
            }
    
    def _apply_text_search(self, queryset, query: str):
        """Apply full-text search to invoice queryset with Polish language support."""
        # Clean and prepare query
        clean_query = query.strip()
        
        # Check if query looks like NIP
        if self.NIP_PATTERN.match(clean_query.replace('-', '')):
            nip_query = clean_query.replace('-', '')
            return queryset.filter(
                Q(nabywca__nip__icontains=nip_query) |
                Q(sprzedawca__nip__icontains=nip_query)
            )
        
        # Check if query looks like invoice number
        if re.match(r'^[A-Z]*\d+', clean_query):
            return queryset.filter(numer__icontains=clean_query)
        
        # Full-text search across multiple fields
        search_fields = Q(
            Q(numer__icontains=clean_query) |
            Q(nabywca__nazwa__icontains=clean_query) |
            Q(sprzedawca__nazwa__icontains=clean_query) |
            Q(nabywca__nip__icontains=clean_query) |
            Q(sprzedawca__nip__icontains=clean_query) |
            Q(nabywca__miejscowosc__icontains=clean_query) |
            Q(sprzedawca__miejscowosc__icontains=clean_query) |
            Q(uwagi__icontains=clean_query) |
            Q(wystawca__icontains=clean_query) |
            Q(odbiorca__icontains=clean_query)
        )
        
        return queryset.filter(search_fields)
    
    def _apply_company_text_search(self, queryset, query: str):
        """Apply full-text search to company queryset."""
        clean_query = query.strip()
        
        # Check if query looks like NIP
        if self.NIP_PATTERN.match(clean_query.replace('-', '')):
            nip_query = clean_query.replace('-', '')
            return queryset.filter(nip__icontains=nip_query)
        
        # Full-text search across company fields
        search_fields = Q(
            Q(nazwa__icontains=clean_query) |
            Q(nip__icontains=clean_query) |
            Q(regon__icontains=clean_query) |
            Q(miejscowosc__icontains=clean_query) |
            Q(ulica__icontains=clean_query) |
            Q(email__icontains=clean_query) |
            Q(telefon__icontains=clean_query) |
            Q(dodatkowy_opis__icontains=clean_query)
        )
        
        return queryset.filter(search_fields)
    
    def _apply_filters(self, queryset, filters: Dict[str, Any]):
        """Apply advanced filters to invoice queryset."""
        # Date range filters
        if filters.get('date_from'):
            queryset = queryset.filter(data_wystawienia__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(data_wystawienia__lte=filters['date_to'])
        
        # Amount range filters
        if filters.get('amount_from'):
            queryset = queryset.filter(
                pozycjafaktury__wartosc_brutto__gte=filters['amount_from']
            )
        
        if filters.get('amount_to'):
            queryset = queryset.filter(
                pozycjafaktury__wartosc_brutto__lte=filters['amount_to']
            )
        
        # Status filters
        if filters.get('status'):
            if isinstance(filters['status'], list):
                queryset = queryset.filter(status__in=filters['status'])
            else:
                queryset = queryset.filter(status=filters['status'])
        
        # Document type filters
        if filters.get('typ_dokumentu'):
            if isinstance(filters['typ_dokumentu'], list):
                queryset = queryset.filter(typ_dokumentu__in=filters['typ_dokumentu'])
            else:
                queryset = queryset.filter(typ_dokumentu=filters['typ_dokumentu'])
        
        # Invoice type filters (sprzedaz/koszt)
        if filters.get('typ_faktury'):
            queryset = queryset.filter(typ_faktury=filters['typ_faktury'])
        
        # VAT exemption filter
        if filters.get('zwolnienie_z_vat') is not None:
            queryset = queryset.filter(zwolnienie_z_vat=filters['zwolnienie_z_vat'])
        
        # Payment method filter
        if filters.get('sposob_platnosci'):
            queryset = queryset.filter(sposob_platnosci=filters['sposob_platnosci'])
        
        # Currency filter
        if filters.get('waluta'):
            queryset = queryset.filter(waluta=filters['waluta'])
        
        # OCR confidence filter
        if filters.get('ocr_confidence_min'):
            queryset = queryset.filter(
                ocr_confidence__gte=filters['ocr_confidence_min']
            )
        
        # Manual verification filter
        if filters.get('manual_verification_required') is not None:
            queryset = queryset.filter(
                manual_verification_required=filters['manual_verification_required']
            )
        
        # City filter
        if filters.get('miasto'):
            queryset = queryset.filter(
                Q(nabywca__miejscowosc__icontains=filters['miasto']) |
                Q(sprzedawca__miejscowosc__icontains=filters['miasto'])
            )
        
        # Overdue invoices filter
        if filters.get('overdue'):
            today = timezone.now().date()
            queryset = queryset.filter(
                termin_platnosci__lt=today,
                status__in=['wystawiona', 'cz_oplacona']
            )
        
        return queryset
    
    def _apply_company_filters(self, queryset, filters: Dict[str, Any]):
        """Apply filters to company queryset."""
        # Company type filter
        if filters.get('czy_firma') is not None:
            queryset = queryset.filter(czy_firma=filters['czy_firma'])
        
        # City filter
        if filters.get('miasto'):
            queryset = queryset.filter(miejscowosc__icontains=filters['miasto'])
        
        # Country filter
        if filters.get('kraj'):
            queryset = queryset.filter(kraj__icontains=filters['kraj'])
        
        # Has NIP filter
        if filters.get('has_nip'):
            if filters['has_nip']:
                queryset = queryset.exclude(nip__isnull=True).exclude(nip='')
            else:
                queryset = queryset.filter(Q(nip__isnull=True) | Q(nip=''))
        
        # Has email filter
        if filters.get('has_email'):
            if filters['has_email']:
                queryset = queryset.exclude(email__isnull=True).exclude(email='')
            else:
                queryset = queryset.filter(Q(email__isnull=True) | Q(email=''))
        
        return queryset
    
    def _apply_sorting(self, queryset, sort_by: str, sort_order: str):
        """Apply sorting to queryset."""
        valid_sort_fields = [
            'data_wystawienia', 'data_sprzedazy', 'termin_platnosci',
            'numer', 'nabywca__nazwa', 'sprzedawca__nazwa',
            'status', 'typ_dokumentu', 'waluta', 'ocr_confidence'
        ]
        
        if sort_by not in valid_sort_fields:
            sort_by = 'data_wystawienia'
        
        if sort_order == 'asc':
            return queryset.order_by(sort_by)
        else:
            return queryset.order_by(f'-{sort_by}')
    
    def _serialize_invoice(self, faktura) -> Dict[str, Any]:
        """Serialize invoice for search results."""
        return {
            'id': faktura.id,
            'numer': faktura.numer,
            'typ_dokumentu': faktura.get_typ_dokumentu_display(),
            'data_wystawienia': faktura.data_wystawienia.isoformat(),
            'data_sprzedazy': faktura.data_sprzedazy.isoformat(),
            'termin_platnosci': faktura.termin_platnosci.isoformat(),
            'nabywca': {
                'nazwa': faktura.nabywca.nazwa,
                'nip': faktura.nabywca.nip,
                'miejscowosc': faktura.nabywca.miejscowosc
            },
            'sprzedawca': {
                'nazwa': faktura.sprzedawca.nazwa,
                'nip': faktura.sprzedawca.nip,
                'miejscowosc': faktura.sprzedawca.miejscowosc
            },
            'status': faktura.get_status_display(),
            'waluta': faktura.waluta,
            'typ_faktury': faktura.get_typ_faktury_display(),
            'ocr_confidence': faktura.ocr_confidence,
            'manual_verification_required': faktura.manual_verification_required,
            'url': f'/faktury/{faktura.id}/'
        }
    
    def _serialize_company(self, kontrahent) -> Dict[str, Any]:
        """Serialize company for search results."""
        return {
            'id': kontrahent.id,
            'nazwa': kontrahent.nazwa,
            'nip': kontrahent.nip,
            'regon': kontrahent.regon,
            'miejscowosc': kontrahent.miejscowosc,
            'ulica': kontrahent.ulica,
            'kod_pocztowy': kontrahent.kod_pocztowy,
            'kraj': kontrahent.kraj,
            'czy_firma': kontrahent.czy_firma,
            'email': kontrahent.email,
            'telefon': kontrahent.telefon,
            'url': f'/kontrahenci/{kontrahent.id}/'
        }
    
    def _save_to_history(self, query: str, filters: Dict[str, Any], result_count: int):
        """Save search to history."""
        search_entry = {
            'query': query,
            'filters': filters,
            'result_count': result_count,
            'timestamp': timezone.now(),
        }
        
        self.search_history.append(search_entry)
        
        # Keep only last 50 searches
        if len(self.search_history) > 50:
            self.search_history = self.search_history[-50:]
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history."""
        return self.search_history[-limit:]
    
    def save_search(self, name: str, query: str, filters: Dict[str, Any], user_id: int):
        """Save a search for later use."""
        search_key = f"{user_id}_{name}"
        self.saved_searches[search_key] = {
            'name': name,
            'query': query,
            'filters': filters,
            'created_at': timezone.now(),
            'user_id': user_id
        }
    
    def get_saved_searches(self, user_id: int) -> List[Dict[str, Any]]:
        """Get saved searches for a user."""
        user_searches = []
        for key, search in self.saved_searches.items():
            if search['user_id'] == user_id:
                user_searches.append(search)
        
        return sorted(user_searches, key=lambda x: x['created_at'], reverse=True)
    
    def delete_saved_search(self, name: str, user_id: int) -> bool:
        """Delete a saved search."""
        search_key = f"{user_id}_{name}"
        if search_key in self.saved_searches:
            del self.saved_searches[search_key]
            return True
        return False
    
    def get_search_suggestions(self, query: str, user=None) -> List[str]:
        """Get search suggestions based on query and user data."""
        suggestions = []
        
        if not query or len(query) < 2:
            return suggestions
        
        # Get company name suggestions
        if user:
            companies = Kontrahent.objects.filter(
                user=user,
                nazwa__icontains=query
            ).values_list('nazwa', flat=True)[:5]
            suggestions.extend(companies)
        
        # Get invoice number suggestions
        if user:
            invoice_numbers = Faktura.objects.filter(
                user=user,
                numer__icontains=query
            ).values_list('numer', flat=True)[:5]
            suggestions.extend(invoice_numbers)
        
        return list(set(suggestions))[:10]
    
    def get_filter_options(self, user=None) -> Dict[str, List]:
        """Get available filter options for the user."""
        options = {
            'status': [
                {'value': 'wystawiona', 'label': 'Wystawiona'},
                {'value': 'oplacona', 'label': 'Opłacona'},
                {'value': 'cz_oplacona', 'label': 'Częściowo opłacona'},
                {'value': 'anulowana', 'label': 'Anulowana'},
            ],
            'typ_dokumentu': [
                {'value': 'FV', 'label': 'Faktura VAT'},
                {'value': 'FP', 'label': 'Faktura Proforma'},
                {'value': 'KOR', 'label': 'Korekta Faktury'},
                {'value': 'RC', 'label': 'Rachunek'},
                {'value': 'PAR', 'label': 'Paragon'},
                {'value': 'KP', 'label': 'KP - Dowód Wpłaty'},
                {'value': 'RB', 'label': 'Rachunek Bankowy'},
            ],
            'typ_faktury': [
                {'value': 'sprzedaz', 'label': 'Sprzedaż'},
                {'value': 'koszt', 'label': 'Koszt'},
            ],
            'sposob_platnosci': [
                {'value': 'przelew', 'label': 'Przelew'},
                {'value': 'gotowka', 'label': 'Gotówka'},
            ],
            'waluta': [
                {'value': 'PLN', 'label': 'PLN'},
                {'value': 'EUR', 'label': 'EUR'},
                {'value': 'USD', 'label': 'USD'},
            ]
        }
        
        # Add user-specific cities if user provided
        if user:
            cities = Kontrahent.objects.filter(
                user=user
            ).values_list('miejscowosc', flat=True).distinct()
            options['miasta'] = [{'value': city, 'label': city} for city in cities if city]
        
        return options


# Global search service instance
search_service = AdvancedSearchService()