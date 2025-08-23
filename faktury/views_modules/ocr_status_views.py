"""
OCR Status Views for Real-time Status Updates

This module provides AJAX endpoints for real-time status polling of OCR document processing.
It uses the StatusSyncService to provide unified status information for the frontend.
"""

import logging
from typing import Dict, Any

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import DocumentUpload, OCRResult
from ..services.status_sync_service import StatusSyncService, StatusSyncError

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def get_status_ajax(request, document_id):
    """
    AJAX endpoint for real-time status polling
    
    Returns unified status information including document and OCR status,
    progress data, and display metadata for frontend use.
    
    Args:
        request: HTTP request object
        document_id: ID of the DocumentUpload to check status for
        
    Returns:
        JsonResponse with unified status data or error information
    """
    try:
        # Get document upload for current user
        try:
            document_upload = DocumentUpload.objects.get(
                id=document_id, 
                user=request.user
            )
        except DocumentUpload.DoesNotExist:
            logger.warning(f"Document {document_id} not found for user {request.user.id}")
            return JsonResponse({
                'success': False,
                'error': 'Document not found',
                'error_code': 'DOCUMENT_NOT_FOUND'
            }, status=404)
        
        # Sync status before returning data to ensure accuracy
        try:
            StatusSyncService.sync_document_status(document_upload)
        except StatusSyncError as e:
            logger.warning(f"Status sync failed for document {document_id}: {e}")
            # Continue with existing status if sync fails
        except Exception as e:
            logger.warning(f"Unexpected error during status sync for document {document_id}: {e}")
            # Continue with existing status if sync fails
        
        # Get unified status information
        status_data = StatusSyncService.get_combined_status(document_upload)
        
        # Add timestamp for client-side caching
        status_data['timestamp'] = timezone.now().isoformat()
        
        # Add polling configuration
        status_data['polling'] = {
            'should_continue': not status_data.get('is_final', False),
            'interval_ms': _get_polling_interval(status_data['status']),
            'max_retries': 3
        }
        
        return JsonResponse({
            'success': True,
            'data': status_data
        })
        
    except Exception as e:
        logger.error(f"Error getting status for document {document_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR',
            'message': 'An error occurred while retrieving document status'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_status(request, document_id):
    """
    REST API endpoint for status polling
    
    Provides the same functionality as get_status_ajax but with REST framework
    decorators for API consistency.
    
    Args:
        request: DRF request object
        document_id: ID of the DocumentUpload to check status for
        
    Returns:
        Response with unified status data or error information
    """
    try:
        # Get document upload for current user
        try:
            document_upload = DocumentUpload.objects.get(
                id=document_id, 
                user=request.user
            )
        except DocumentUpload.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Document not found',
                'error_code': 'DOCUMENT_NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Sync status before returning data
        try:
            StatusSyncService.sync_document_status(document_upload)
        except StatusSyncError as e:
            logger.warning(f"Status sync failed for document {document_id}: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error during status sync for document {document_id}: {e}")
        
        # Get unified status information
        status_data = StatusSyncService.get_combined_status(document_upload)
        
        # Add API-specific metadata
        status_data.update({
            'timestamp': timezone.now().isoformat(),
            'api_version': '1.0',
            'polling': {
                'should_continue': not status_data.get('is_final', False),
                'interval_ms': _get_polling_interval(status_data['status']),
                'max_retries': 3
            }
        })
        
        return Response({
            'success': True,
            'data': status_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"API error getting status for document {document_id}: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR',
            'message': 'An error occurred while retrieving document status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
@require_http_methods(["GET"])
def get_status_display_ajax(request, document_id):
    """
    AJAX endpoint for template-optimized status display data
    
    Returns status information optimized for template rendering with
    CSS classes, icons, and display-friendly formatting.
    
    Args:
        request: HTTP request object
        document_id: ID of the DocumentUpload to check status for
        
    Returns:
        JsonResponse with template-optimized status display data
    """
    try:
        # Get document upload for current user
        try:
            document_upload = DocumentUpload.objects.get(
                id=document_id, 
                user=request.user
            )
        except DocumentUpload.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Document not found',
                'error_code': 'DOCUMENT_NOT_FOUND'
            }, status=404)
        
        # Sync status before returning data
        try:
            StatusSyncService.sync_document_status(document_upload)
        except StatusSyncError as e:
            logger.warning(f"Status sync failed for document {document_id}: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error during status sync for document {document_id}: {e}")
        
        # Get display-optimized status data
        display_data = StatusSyncService.get_status_display_data(document_upload)
        
        # Add timestamp and polling info
        display_data.update({
            'timestamp': timezone.now().isoformat(),
            'polling': {
                'should_continue': not display_data.get('is_final', False),
                'interval_ms': _get_polling_interval(display_data['status'])
            }
        })
        
        return JsonResponse({
            'success': True,
            'data': display_data
        })
        
    except Exception as e:
        logger.error(f"Error getting display status for document {document_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_progress_ajax(request, document_id):
    """
    AJAX endpoint for progress information only
    
    Lightweight endpoint that returns only progress percentage and
    basic status information for progress bar updates.
    
    Args:
        request: HTTP request object
        document_id: ID of the DocumentUpload to check progress for
        
    Returns:
        JsonResponse with progress information
    """
    try:
        # Get document upload for current user
        try:
            document_upload = DocumentUpload.objects.get(
                id=document_id, 
                user=request.user
            )
        except DocumentUpload.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Document not found',
                'error_code': 'DOCUMENT_NOT_FOUND'
            }, status=404)
        
        # Get progress information
        progress = StatusSyncService.get_processing_progress(document_upload)
        combined_status = StatusSyncService.get_combined_status(document_upload)
        
        progress_data = {
            'progress': progress,
            'status': combined_status['status'],
            'display': combined_status['display'],
            'is_final': combined_status.get('is_final', False),
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'data': progress_data
        })
        
    except Exception as e:
        logger.error(f"Error getting progress for document {document_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_bulk_status(request):
    """
    REST API endpoint for bulk status checking
    
    Allows checking status of multiple documents in a single request.
    Useful for dashboard views that need to display status of multiple documents.
    
    Query parameters:
        document_ids: Comma-separated list of document IDs
        
    Returns:
        Response with status data for all requested documents
    """
    try:
        # Get document IDs from query parameters
        document_ids_param = request.GET.get('document_ids', '')
        if not document_ids_param:
            return Response({
                'success': False,
                'error': 'No document IDs provided',
                'error_code': 'MISSING_DOCUMENT_IDS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse document IDs
        try:
            document_ids = [int(id.strip()) for id in document_ids_param.split(',') if id.strip()]
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid document ID format',
                'error_code': 'INVALID_DOCUMENT_IDS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Limit number of documents to prevent abuse
        if len(document_ids) > 50:
            return Response({
                'success': False,
                'error': 'Too many documents requested (max 50)',
                'error_code': 'TOO_MANY_DOCUMENTS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get documents for current user
        documents = DocumentUpload.objects.filter(
            id__in=document_ids,
            user=request.user
        )
        
        # Collect status data for each document
        status_data = {}
        sync_stats = {'updated': 0, 'failed': 0}
        
        for document in documents:
            try:
                # Sync status
                if StatusSyncService.sync_document_status(document):
                    sync_stats['updated'] += 1
            except StatusSyncError:
                sync_stats['failed'] += 1
            
            # Get status data
            try:
                status_data[document.id] = StatusSyncService.get_combined_status(document)
            except Exception as e:
                logger.error(f"Error getting status for document {document.id}: {e}")
                status_data[document.id] = {
                    'status': 'error',
                    'display': 'Błąd',
                    'error_message': str(e)
                }
        
        # Add metadata
        response_data = {
            'success': True,
            'data': status_data,
            'metadata': {
                'requested_count': len(document_ids),
                'found_count': len(documents),
                'sync_stats': sync_stats,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in bulk status check: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Helper functions

def _get_polling_interval(status: str) -> int:
    """
    Get appropriate polling interval based on status
    
    Args:
        status: Current processing status
        
    Returns:
        int: Polling interval in milliseconds
    """
    # Different polling intervals based on status
    intervals = {
        'uploaded': 2000,      # 2 seconds - waiting to start
        'queued': 3000,        # 3 seconds - in queue
        'processing': 1000,    # 1 second - actively processing
        'ocr_completed': 5000, # 5 seconds - completed, less frequent
        'manual_review': 10000, # 10 seconds - waiting for user
        'failed': 30000,       # 30 seconds - failed, very infrequent
        'cancelled': 0,        # No polling needed
        'completed': 0,        # No polling needed
    }
    
    return intervals.get(status, 5000)  # Default 5 seconds


def _format_error_response(error_message: str, error_code: str = None, status_code: int = 500) -> JsonResponse:
    """
    Format consistent error response
    
    Args:
        error_message: Human-readable error message
        error_code: Machine-readable error code
        status_code: HTTP status code
        
    Returns:
        JsonResponse with error information
    """
    response_data = {
        'success': False,
        'error': error_message,
        'timestamp': timezone.now().isoformat()
    }
    
    if error_code:
        response_data['error_code'] = error_code
    
    return JsonResponse(response_data, status=status_code)