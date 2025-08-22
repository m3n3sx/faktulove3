"""
OCR Views for Document Processing
"""

import logging
from typing import Dict, Any

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import models

from ..models import DocumentUpload, OCRResult, OCRValidation, Faktura
from ..services.file_upload_service import FileUploadService, FileValidationError
from ..tasks import process_ocr_document

logger = logging.getLogger(__name__)


@login_required
def ocr_upload_view(request):
    """Main OCR upload page"""
    
    if request.method == 'POST':
        return handle_file_upload(request)
    
    # GET request - show upload form
    context = {
        'supported_types': list(settings.SUPPORTED_DOCUMENT_TYPES.keys()),
        'max_file_size_mb': settings.DOCUMENT_AI_CONFIG['max_file_size'] // (1024 * 1024),
        'recent_uploads': DocumentUpload.objects.filter(user=request.user)[:10],
    }
    
    return render(request, 'faktury/ocr/upload.html', context)


@login_required 
@require_http_methods(["POST"])
def handle_file_upload(request):
    """Handle file upload via form submission"""
    
    try:
        uploaded_file = request.FILES.get('document')
        if not uploaded_file:
            messages.error(request, 'Nie wybrano pliku do przesłania.')
            return redirect('ocr_upload')
        
        # Initialize upload service
        upload_service = FileUploadService()
        
        # Handle the upload
        document_upload = upload_service.handle_upload(uploaded_file, request.user)
        
        # Start OCR processing asynchronously
        task = process_ocr_document.delay(document_upload.id)
        
        messages.success(
            request, 
            f'Plik "{uploaded_file.name}" został przesłany. '
            f'Przetwarzanie OCR rozpoczęte (ID: {task.id}).'
        )
        
        return redirect('ocr_status', document_id=document_upload.id)
        
    except FileValidationError as e:
        messages.error(request, f'Błąd walidacji pliku: {e}')
        return redirect('ocr_upload')
        
    except Exception as e:
        logger.error(f"File upload error: {e}", exc_info=True)
        messages.error(request, 'Wystąpił błąd podczas przesyłania pliku.')
        return redirect('ocr_upload')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_upload_document(request):
    """API endpoint for document upload"""
    
    try:
        uploaded_file = request.FILES.get('document')
        if not uploaded_file:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize upload service
        upload_service = FileUploadService()
        
        # Handle the upload
        document_upload = upload_service.handle_upload(uploaded_file, request.user)
        
        # Start OCR processing asynchronously
        task = process_ocr_document.delay(document_upload.id)
        
        return Response({
            'success': True,
            'document_id': document_upload.id,
            'task_id': task.id,
            'filename': uploaded_file.name,
            'status': 'uploaded',
            'message': 'Document uploaded successfully. OCR processing started.'
        }, status=status.HTTP_201_CREATED)
        
    except FileValidationError as e:
        return Response(
            {'error': f'File validation failed: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        logger.error(f"API upload error: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error during upload'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@login_required
def ocr_status_view(request, document_id):
    """View OCR processing status"""
    
    document_upload = get_object_or_404(
        DocumentUpload, 
        id=document_id, 
        user=request.user
    )
    
    # Get OCR result if available
    ocr_result = None
    try:
        ocr_result = OCRResult.objects.get(document=document_upload)
    except OCRResult.DoesNotExist:
        pass
    
    context = {
        'document': document_upload,
        'ocr_result': ocr_result,
        'processing_duration': document_upload.processing_duration,
    }
    
    return render(request, 'faktury/ocr/status.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_processing_status(request, document_id):
    """API endpoint to check processing status"""
    
    try:
        document_upload = DocumentUpload.objects.get(
            id=document_id, 
            user=request.user
        )
        
        response_data = {
            'document_id': document_upload.id,
            'filename': document_upload.original_filename,
            'status': document_upload.processing_status,
            'upload_time': document_upload.upload_timestamp,
            'processing_started': document_upload.processing_started_at,
            'processing_completed': document_upload.processing_completed_at,
            'processing_duration': document_upload.processing_duration,
            'error_message': document_upload.error_message,
        }
        
        # Add OCR result data if available
        try:
            ocr_result = OCRResult.objects.get(document=document_upload)
            response_data.update({
                'ocr_available': True,
                'confidence_score': ocr_result.confidence_score,
                'confidence_level': ocr_result.confidence_level,
                'needs_review': ocr_result.needs_human_review,
                'extracted_data': ocr_result.extracted_data,
            })
            
            # Add invoice data if created
            if ocr_result.faktura:
                response_data.update({
                    'invoice_created': True,
                    'invoice_id': ocr_result.faktura.id,
                    'invoice_number': ocr_result.faktura.numer,
                })
            
        except OCRResult.DoesNotExist:
            response_data['ocr_available'] = False
        
        return Response(response_data)
        
    except DocumentUpload.DoesNotExist:
        return Response(
            {'error': 'Document not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@login_required
def ocr_results_list(request):
    """List all OCR results for user"""
    
    # Get user's OCR results
    ocr_results = OCRResult.objects.filter(
        document__user=request.user
    ).select_related('document', 'faktura').order_by('-created_at')
    
    context = {
        'ocr_results': ocr_results,
        'confidence_thresholds': settings.OCR_SETTINGS['confidence_thresholds'],
    }
    
    return render(request, 'faktury/ocr/results_list.html', context)


@login_required
def ocr_result_detail(request, result_id):
    """View detailed OCR result"""
    
    ocr_result = get_object_or_404(
        OCRResult,
        id=result_id,
        document__user=request.user
    )
    
    context = {
        'ocr_result': ocr_result,
        'extracted_data': ocr_result.extracted_data,
        'confidence_thresholds': settings.OCR_SETTINGS['confidence_thresholds'],
    }
    
    return render(request, 'faktury/ocr/result_detail.html', context)


@login_required
@require_http_methods(["POST"])
def create_invoice_from_ocr(request, result_id):
    """Create invoice from OCR result with user modifications"""
    
    ocr_result = get_object_or_404(
        OCRResult,
        id=result_id,
        document__user=request.user
    )
    
    if ocr_result.faktura:
        messages.warning(request, 'Faktura została już utworzona z tego wyniku OCR.')
        return redirect('szczegoly_faktury', id=ocr_result.faktura.id)
    
    try:
        # Get user modifications from form
        modifications = _extract_user_modifications(request.POST)
        
        # Apply modifications to extracted data
        modified_data = {**ocr_result.extracted_data, **modifications}
        
        # Create invoice
        faktura = _create_invoice_with_data(modified_data, request.user)
        
        # Link OCR result to invoice
        ocr_result.faktura = faktura
        ocr_result.save()
        
        # Create validation record
        OCRValidation.objects.create(
            ocr_result=ocr_result,
            validated_by=request.user,
            corrections_made=modifications,
            accuracy_rating=int(request.POST.get('accuracy_rating', 8)),
            validation_notes=request.POST.get('validation_notes', ''),
        )
        
        messages.success(
            request, 
            f'Faktura {faktura.numer} została utworzona na podstawie OCR.'
        )
        
        return redirect('szczegoly_faktury', id=faktura.id)
        
    except Exception as e:
        logger.error(f"Error creating invoice from OCR: {e}", exc_info=True)
        messages.error(request, f'Błąd podczas tworzenia faktury: {e}')
        return redirect('ocr_result_detail', result_id=result_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_ocr_statistics(request):
    """API endpoint for OCR processing statistics"""
    
    user_documents = DocumentUpload.objects.filter(user=request.user)
    user_results = OCRResult.objects.filter(document__user=request.user)
    
    # Calculate statistics
    stats = {
        'total_documents': user_documents.count(),
        'completed_processing': user_documents.filter(processing_status='completed').count(),
        'failed_processing': user_documents.filter(processing_status='failed').count(),
        'currently_processing': user_documents.filter(processing_status='processing').count(),
        
        'total_ocr_results': user_results.count(),
        'high_confidence': user_results.filter(confidence_score__gte=95).count(),
        'medium_confidence': user_results.filter(
            confidence_score__gte=80, 
            confidence_score__lt=95
        ).count(),
        'low_confidence': user_results.filter(confidence_score__lt=80).count(),
        
        'auto_created_invoices': user_results.filter(faktura__isnull=False).count(),
        'pending_review': user_results.filter(
            faktura__isnull=True,
            confidence_score__gte=80
        ).count(),
    }
    
    # Calculate average confidence
    if user_results.exists():
        avg_confidence = user_results.aggregate(
            avg=models.Avg('confidence_score')
        )['avg']
        stats['average_confidence'] = round(avg_confidence, 2) if avg_confidence else 0
    else:
        stats['average_confidence'] = 0
    
    # Calculate average processing time
    completed_results = user_results.filter(processing_time__gt=0)
    if completed_results.exists():
        avg_time = completed_results.aggregate(
            avg=models.Avg('processing_time')
        )['avg']
        stats['average_processing_time'] = round(avg_time, 2) if avg_time else 0
    else:
        stats['average_processing_time'] = 0
    
    return Response(stats)


# Helper functions

def _extract_user_modifications(post_data) -> Dict[str, Any]:
    """Extract user modifications from form data"""
    modifications = {}
    
    # Map form fields to extracted data fields
    field_mapping = {
        'invoice_number': 'invoice_number',
        'invoice_date': 'invoice_date', 
        'due_date': 'due_date',
        'supplier_name': 'supplier_name',
        'supplier_nip': 'supplier_nip',
        'buyer_name': 'buyer_name',
        'buyer_nip': 'buyer_nip',
        'total_amount': 'total_amount',
        'net_amount': 'net_amount',
        'vat_amount': 'vat_amount',
    }
    
    for form_field, data_field in field_mapping.items():
        value = post_data.get(form_field)
        if value:
            modifications[data_field] = value
    
    return modifications


def _create_invoice_with_data(extracted_data: Dict[str, Any], user) -> Faktura:
    """Create invoice with extracted/modified data"""
    # This is a simplified version - you might want to use the existing
    # invoice creation logic from tasks.py
    from ..tasks import _create_invoice_from_ocr
    from ..models import OCRResult
    
    # Create a temporary OCR result for the creation function
    temp_result = OCRResult(extracted_data=extracted_data)
    
    return _create_invoice_from_ocr(temp_result, user)