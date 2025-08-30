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
from ..services.enhanced_ocr_upload_manager import get_upload_manager
from ..services.ocr_feedback_system import get_feedback_system
from ..tasks import process_document_ocr_task

logger = logging.getLogger(__name__)


@login_required
def ocr_upload_view(request):
    """Simple OCR upload page"""
    
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.get('document')
            if not uploaded_file:
                messages.error(request, 'Nie wybrano pliku do przesłania.')
                return redirect('ocr_upload')
            
            # Simple file validation
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff']
            if uploaded_file.content_type not in allowed_types:
                messages.error(request, 'Nieobsługiwany typ pliku.')
                return redirect('ocr_upload')
            
            if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
                messages.error(request, 'Plik jest za duży (maksymalnie 10MB).')
                return redirect('ocr_upload')
            
            messages.success(request, f'Plik "{uploaded_file.name}" został przesłany pomyślnie.')
            return redirect('ocr_upload')
            
        except Exception as e:
            logger.error(f"Upload error: {e}", exc_info=True)
            messages.error(request, 'Wystąpił błąd podczas przesyłania pliku.')
            return redirect('ocr_upload')
    
    # GET request
    context = {
        'supported_types': {'application/pdf': '.pdf', 'image/jpeg': '.jpg', 'image/png': '.png', 'image/tiff': '.tiff'},
        'max_file_size_mb': 10,
    }
    
    return render(request, 'faktury/ocr/simple_upload.html', context)


@login_required
def test_csrf_view(request):
    """Test page for CSRF token handling"""
    return render(request, 'ocr/test_csrf.html')


from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_csrf_token(request):
    """Simple CSRF token endpoint for testing - no authentication required"""
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    
    return JsonResponse({
        'success': True,
        'csrf_token': csrf_token,
        'message': 'CSRF token retrieved successfully'
    })





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_validate_upload(request):
    """API endpoint to validate upload before queuing"""
    
    try:
        filename = request.data.get('filename')
        file_size = request.data.get('fileSize')
        content_type = request.data.get('contentType')
        
        if not all([filename, file_size, content_type]):
            return Response(
                {'valid': False, 'error': 'Missing file information'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a mock uploaded file for validation
        from django.core.files.uploadedfile import SimpleUploadedFile
        mock_file = SimpleUploadedFile(filename, b'', content_type=content_type)
        mock_file.size = int(file_size)
        
        # Use enhanced upload manager for validation
        upload_manager = get_upload_manager()
        validation_result = upload_manager.validate_upload_request(mock_file, request.user)
        
        return Response(validation_result)
        
    except Exception as e:
        logger.error(f"Upload validation error: {e}", exc_info=True)
        return Response(
            {'valid': False, 'error': 'Validation error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_upload_document(request):
    """Enhanced API endpoint for document upload with queue management"""
    
    try:
        uploaded_file = request.FILES.get('document')
        upload_id = request.data.get('upload_id')  # Optional client-provided ID
        
        if not uploaded_file:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use enhanced upload manager
        upload_manager = get_upload_manager()
        
        # Validate upload request
        validation_result = upload_manager.validate_upload_request(uploaded_file, request.user)
        if not validation_result['valid']:
            return Response(
                {'error': validation_result['error'], 'error_code': validation_result.get('error_code')}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Queue the upload
        queue_upload_id = upload_manager.queue_upload(uploaded_file, request.user)
        
        return Response({
            'success': True,
            'upload_id': queue_upload_id,
            'filename': uploaded_file.name,
            'status': 'queued',
            'message': 'Document queued for upload and processing.',
            'estimated_time': validation_result['file_info']['estimated_processing_time']
        }, status=status.HTTP_201_CREATED)
        
    except FileValidationError as e:
        return Response(
            {'error': f'File validation failed: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        logger.error(f"Enhanced API upload error: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error during upload'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_upload_progress(request, upload_id):
    """API endpoint to get upload progress"""
    
    try:
        upload_manager = get_upload_manager()
        progress = upload_manager.get_upload_progress(upload_id)
        
        if progress is None:
            return Response(
                {'error': 'Upload not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(progress)
        
    except Exception as e:
        logger.error(f"Progress check error: {e}", exc_info=True)
        return Response(
            {'error': 'Error checking progress'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_cancel_upload(request, upload_id):
    """API endpoint to cancel an upload"""
    
    try:
        upload_manager = get_upload_manager()
        success = upload_manager.cancel_upload(upload_id, request.user)
        
        if not success:
            return Response(
                {'error': 'Could not cancel upload'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'success': True, 'message': 'Upload cancelled'})
        
    except Exception as e:
        logger.error(f"Cancel upload error: {e}", exc_info=True)
        return Response(
            {'error': 'Error cancelling upload'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_retry_upload(request, upload_id):
    """API endpoint to retry a failed upload"""
    
    try:
        upload_manager = get_upload_manager()
        success = upload_manager.retry_failed_upload(upload_id, request.user)
        
        if not success:
            return Response(
                {'error': 'Could not retry upload'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'success': True, 'message': 'Upload retry initiated'})
        
    except Exception as e:
        logger.error(f"Retry upload error: {e}", exc_info=True)
        return Response(
            {'error': 'Error retrying upload'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_queue_status(request):
    """API endpoint to get upload queue status"""
    
    try:
        upload_manager = get_upload_manager()
        queue_status = upload_manager.get_queue_status()
        
        return Response(queue_status)
        
    except Exception as e:
        logger.error(f"Queue status error: {e}", exc_info=True)
        return Response(
            {'error': 'Error getting queue status'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_ocr_feedback(request, result_id):
    """API endpoint to get OCR feedback and confidence analysis"""
    
    try:
        ocr_result = OCRResult.objects.get(
            id=result_id,
            document__user=request.user
        )
        
        feedback_system = get_feedback_system()
        feedback = feedback_system.generate_ocr_feedback(ocr_result)
        
        return Response(feedback.to_dict())
        
    except OCRResult.DoesNotExist:
        return Response(
            {'error': 'OCR result not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"OCR feedback error: {e}", exc_info=True)
        return Response(
            {'error': 'Error generating OCR feedback'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_confidence_explanation(request, result_id):
    """API endpoint to get detailed confidence explanation"""
    
    try:
        ocr_result = OCRResult.objects.get(
            id=result_id,
            document__user=request.user
        )
        
        feedback_system = get_feedback_system()
        explanation = feedback_system.get_confidence_explanation(ocr_result.confidence_score)
        
        return Response(explanation)
        
    except OCRResult.DoesNotExist:
        return Response(
            {'error': 'OCR result not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Confidence explanation error: {e}", exc_info=True)
        return Response(
            {'error': 'Error getting confidence explanation'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_improvement_suggestions(request, result_id):
    """API endpoint to get improvement suggestions"""
    
    try:
        ocr_result = OCRResult.objects.get(
            id=result_id,
            document__user=request.user
        )
        
        feedback_system = get_feedback_system()
        suggestions = feedback_system.suggest_improvements(ocr_result)
        
        return Response({'suggestions': suggestions})
        
    except OCRResult.DoesNotExist:
        return Response(
            {'error': 'OCR result not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Improvement suggestions error: {e}", exc_info=True)
        return Response(
            {'error': 'Error getting improvement suggestions'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_correction_interface(request, result_id):
    """API endpoint to get manual correction interface data"""
    
    try:
        ocr_result = OCRResult.objects.get(
            id=result_id,
            document__user=request.user
        )
        
        feedback_system = get_feedback_system()
        interface_data = feedback_system.create_manual_correction_interface(ocr_result)
        
        return Response(interface_data)
        
    except OCRResult.DoesNotExist:
        return Response(
            {'error': 'OCR result not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Correction interface error: {e}", exc_info=True)
        return Response(
            {'error': 'Error creating correction interface'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_apply_corrections(request, result_id):
    """API endpoint to apply manual corrections"""
    
    try:
        ocr_result = OCRResult.objects.get(
            id=result_id,
            document__user=request.user
        )
        
        corrections = request.data.get('corrections', {})
        if not corrections:
            return Response(
                {'error': 'No corrections provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        feedback_system = get_feedback_system()
        result = feedback_system.apply_manual_corrections(ocr_result, corrections, request.user)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
    except OCRResult.DoesNotExist:
        return Response(
            {'error': 'OCR result not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Apply corrections error: {e}", exc_info=True)
        return Response(
            {'error': 'Error applying corrections'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_retry_processing(request, document_id):
    """API endpoint to retry OCR processing"""
    
    try:
        document = DocumentUpload.objects.get(
            id=document_id,
            user=request.user
        )
        
        retry_options = request.data.get('retry_options', {})
        
        feedback_system = get_feedback_system()
        success = feedback_system.retry_ocr_processing(document, retry_options)
        
        if success:
            return Response({
                'success': True,
                'message': 'OCR processing retry initiated'
            })
        else:
            return Response(
                {'error': 'Could not retry processing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except DocumentUpload.DoesNotExist:
        return Response(
            {'error': 'Document not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Retry processing error: {e}", exc_info=True)
        return Response(
            {'error': 'Error retrying processing'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@login_required
def ocr_upload_progress_view(request, upload_id):
    """Simple progress view"""
    
    context = {
        'upload_id': upload_id,
        'message': 'Funkcja w trakcie implementacji'
    }
    
    return render(request, 'faktury/ocr/simple_progress.html', context)


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

# Mock OCR Processing - dodane przez quick_fix.py
def mock_process_ocr(document_upload):
    """Mock OCR processing function"""
    from django.utils import timezone
    from .models import OCRResult, OCREngine
    import random
    
    try:
        # Pobierz mock engine
        mock_engine = OCREngine.objects.filter(engine_type='mock', is_active=True).first()
        
        if not mock_engine:
            return None
        
        # Utwórz mock wynik
        ocr_result = OCRResult.objects.create(
            document=document_upload,
            engine_used=mock_engine,
            confidence_score=mock_engine.configuration.get('mock_confidence', 0.85),
            confidence_level='high',
            extracted_text=mock_engine.configuration.get('mock_text', 'Mock OCR text'),
            extracted_data=mock_engine.configuration.get('mock_data', {}),
            processing_time=random.uniform(1, 3),
            needs_human_review=False
        )
        
        # Zaktualizuj status dokumentu
        document_upload.processing_status = 'completed'
        document_upload.processing_completed_at = timezone.now()
        document_upload.save()
        
        return ocr_result
        
    except Exception as e:
        document_upload.processing_status = 'failed'
        document_upload.error_message = str(e)
        document_upload.save()
        return None
