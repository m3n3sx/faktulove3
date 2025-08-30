"""
API views for advanced search and filtering functionality.
Provides REST endpoints for invoice and company search with Polish business criteria.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import json
import logging
from datetime import datetime
from typing import Dict, Any

from faktury.services.search_service import search_service

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def search_invoices_api(request):
    """
    Advanced invoice search API endpoint.
    
    GET: Search with query parameters
    POST: Search with JSON payload for complex filters
    """
    try:
        if request.method == 'GET':
            # Extract search parameters from query string
            query = request.GET.get('q', '')
            page = int(request.GET.get('page', 1))
            per_page = min(int(request.GET.get('per_page', 20)), 100)  # Max 100 items
            sort_by = request.GET.get('sort_by', 'data_wystawienia')
            sort_order = request.GET.get('sort_order', 'desc')
            
            # Build filters from query parameters
            filters = {}
            
            # Date filters
            if request.GET.get('date_from'):
                try:
                    filters['date_from'] = datetime.strptime(
                        request.GET.get('date_from'), '%Y-%m-%d'
                    ).date()
                except ValueError:
                    pass
            
            if request.GET.get('date_to'):
                try:
                    filters['date_to'] = datetime.strptime(
                        request.GET.get('date_to'), '%Y-%m-%d'
                    ).date()
                except ValueError:
                    pass
            
            # Status filter
            if request.GET.get('status'):
                filters['status'] = request.GET.getlist('status')
            
            # Document type filter
            if request.GET.get('typ_dokumentu'):
                filters['typ_dokumentu'] = request.GET.getlist('typ_dokumentu')
            
            # Invoice type filter
            if request.GET.get('typ_faktury'):
                filters['typ_faktury'] = request.GET.get('typ_faktury')
            
            # Amount filters
            if request.GET.get('amount_from'):
                try:
                    filters['amount_from'] = float(request.GET.get('amount_from'))
                except ValueError:
                    pass
            
            if request.GET.get('amount_to'):
                try:
                    filters['amount_to'] = float(request.GET.get('amount_to'))
                except ValueError:
                    pass
            
            # OCR confidence filter
            if request.GET.get('ocr_confidence_min'):
                try:
                    filters['ocr_confidence_min'] = float(request.GET.get('ocr_confidence_min'))
                except ValueError:
                    pass
            
            # Boolean filters
            if request.GET.get('overdue') == 'true':
                filters['overdue'] = True
            
            if request.GET.get('manual_verification_required') == 'true':
                filters['manual_verification_required'] = True
            
        else:  # POST
            data = json.loads(request.body)
            query = data.get('query', '')
            page = data.get('page', 1)
            per_page = min(data.get('per_page', 20), 100)
            sort_by = data.get('sort_by', 'data_wystawienia')
            sort_order = data.get('sort_order', 'desc')
            filters = data.get('filters', {})
            
            # Convert date strings to date objects
            if 'date_from' in filters and isinstance(filters['date_from'], str):
                try:
                    filters['date_from'] = datetime.strptime(
                        filters['date_from'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    del filters['date_from']
            
            if 'date_to' in filters and isinstance(filters['date_to'], str):
                try:
                    filters['date_to'] = datetime.strptime(
                        filters['date_to'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    del filters['date_to']
        
        # Perform search
        results = search_service.search_invoices(
            query=query,
            filters=filters,
            user=request.user,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in invoice search API: {str(e)}")
        return Response(
            {'error': 'Wystąpił błąd podczas wyszukiwania faktur'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def search_companies_api(request):
    """
    Advanced company search API endpoint.
    """
    try:
        if request.method == 'GET':
            query = request.GET.get('q', '')
            page = int(request.GET.get('page', 1))
            per_page = min(int(request.GET.get('per_page', 20)), 100)
            
            # Build filters from query parameters
            filters = {}
            
            if request.GET.get('czy_firma') == 'true':
                filters['czy_firma'] = True
            elif request.GET.get('czy_firma') == 'false':
                filters['czy_firma'] = False
            
            if request.GET.get('miasto'):
                filters['miasto'] = request.GET.get('miasto')
            
            if request.GET.get('kraj'):
                filters['kraj'] = request.GET.get('kraj')
            
            if request.GET.get('has_nip') == 'true':
                filters['has_nip'] = True
            elif request.GET.get('has_nip') == 'false':
                filters['has_nip'] = False
            
            if request.GET.get('has_email') == 'true':
                filters['has_email'] = True
            elif request.GET.get('has_email') == 'false':
                filters['has_email'] = False
                
        else:  # POST
            data = json.loads(request.body)
            query = data.get('query', '')
            page = data.get('page', 1)
            per_page = min(data.get('per_page', 20), 100)
            filters = data.get('filters', {})
        
        # Perform search
        results = search_service.search_companies(
            query=query,
            filters=filters,
            user=request.user,
            page=page,
            per_page=per_page
        )
        
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in company search API: {str(e)}")
        return Response(
            {'error': 'Wystąpił błąd podczas wyszukiwania kontrahentów'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_suggestions_api(request):
    """
    Get search suggestions based on query.
    """
    try:
        query = request.GET.get('q', '')
        
        if len(query) < 2:
            return Response({'suggestions': []}, status=status.HTTP_200_OK)
        
        # Check cache first
        cache_key = f"search_suggestions_{request.user.id}_{query}"
        cached_suggestions = cache.get(cache_key)
        
        if cached_suggestions is not None:
            return Response({'suggestions': cached_suggestions}, status=status.HTTP_200_OK)
        
        # Get suggestions
        suggestions = search_service.get_search_suggestions(query, request.user)
        
        # Cache for 5 minutes
        cache.set(cache_key, suggestions, 300)
        
        return Response({'suggestions': suggestions}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {str(e)}")
        return Response(
            {'suggestions': []},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_options_api(request):
    """
    Get available filter options for the user.
    """
    try:
        # Check cache first
        cache_key = f"filter_options_{request.user.id}"
        cached_options = cache.get(cache_key)
        
        if cached_options is not None:
            return Response(cached_options, status=status.HTTP_200_OK)
        
        # Get filter options
        options = search_service.get_filter_options(request.user)
        
        # Cache for 1 hour
        cache.set(cache_key, options, 3600)
        
        return Response(options, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting filter options: {str(e)}")
        return Response(
            {'error': 'Wystąpił błąd podczas pobierania opcji filtrowania'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_history_api(request):
    """
    Get user's search history.
    """
    try:
        limit = min(int(request.GET.get('limit', 10)), 50)
        history = search_service.get_search_history(limit)
        
        # Convert datetime objects to strings for JSON serialization
        for entry in history:
            entry['timestamp'] = entry['timestamp'].isoformat()
        
        return Response({'history': history}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting search history: {str(e)}")
        return Response(
            {'history': []},
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_search_api(request):
    """
    Save a search for later use.
    """
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        query = data.get('query', '')
        filters = data.get('filters', {})
        
        if not name:
            return Response(
                {'error': 'Nazwa wyszukiwania jest wymagana'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save search
        search_service.save_search(name, query, filters, request.user.id)
        
        return Response(
            {'message': 'Wyszukiwanie zostało zapisane'},
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error saving search: {str(e)}")
        return Response(
            {'error': 'Wystąpił błąd podczas zapisywania wyszukiwania'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saved_searches_api(request):
    """
    Get user's saved searches.
    """
    try:
        saved_searches = search_service.get_saved_searches(request.user.id)
        
        # Convert datetime objects to strings for JSON serialization
        for search in saved_searches:
            search['created_at'] = search['created_at'].isoformat()
        
        return Response({'saved_searches': saved_searches}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting saved searches: {str(e)}")
        return Response(
            {'saved_searches': []},
            status=status.HTTP_200_OK
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_saved_search_api(request, search_name):
    """
    Delete a saved search.
    """
    try:
        success = search_service.delete_saved_search(search_name, request.user.id)
        
        if success:
            return Response(
                {'message': 'Zapisane wyszukiwanie zostało usunięte'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Nie znaleziono zapisanego wyszukiwania'},
                status=status.HTTP_404_NOT_FOUND
            )
        
    except Exception as e:
        logger.error(f"Error deleting saved search: {str(e)}")
        return Response(
            {'error': 'Wystąpił błąd podczas usuwania wyszukiwania'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class QuickSearchView(View):
    """
    Quick search view for AJAX requests.
    """
    
    def get(self, request):
        """Handle quick search requests."""
        try:
            query = request.GET.get('q', '').strip()
            search_type = request.GET.get('type', 'invoices')  # invoices or companies
            
            if len(query) < 2:
                return JsonResponse({'results': []})
            
            if search_type == 'companies':
                results = search_service.search_companies(
                    query=query,
                    user=request.user,
                    per_page=10
                )
            else:
                results = search_service.search_invoices(
                    query=query,
                    user=request.user,
                    per_page=10
                )
            
            return JsonResponse({
                'results': results['results'][:10],  # Limit to 10 for quick search
                'total_count': results['total_count']
            })
            
        except Exception as e:
            logger.error(f"Error in quick search: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_stats_api(request):
    """
    Get search statistics and analytics.
    """
    try:
        from faktury.models import Faktura, Kontrahent
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Get basic counts
        total_invoices = Faktura.objects.filter(user=request.user).count()
        total_companies = Kontrahent.objects.filter(user=request.user).count()
        
        # Get recent activity (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_invoices = Faktura.objects.filter(
            user=request.user,
            data_wystawienia__gte=thirty_days_ago
        ).count()
        
        # Get status distribution
        status_stats = Faktura.objects.filter(user=request.user).values('status').annotate(
            count=Count('id')
        )
        
        # Get document type distribution
        doc_type_stats = Faktura.objects.filter(user=request.user).values('typ_dokumentu').annotate(
            count=Count('id')
        )
        
        # Get OCR statistics
        ocr_stats = {
            'total_ocr_processed': Faktura.objects.filter(
                user=request.user,
                source_document__isnull=False
            ).count(),
            'high_confidence': Faktura.objects.filter(
                user=request.user,
                ocr_confidence__gte=90
            ).count(),
            'needs_verification': Faktura.objects.filter(
                user=request.user,
                manual_verification_required=True
            ).count()
        }
        
        stats = {
            'totals': {
                'invoices': total_invoices,
                'companies': total_companies,
                'recent_invoices': recent_invoices
            },
            'status_distribution': list(status_stats),
            'document_type_distribution': list(doc_type_stats),
            'ocr_statistics': ocr_stats
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting search stats: {str(e)}")
        return Response(
            {'error': 'Wystąpił błąd podczas pobierania statystyk'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )