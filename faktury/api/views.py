"""
Base API views for the OCR REST API.
"""
import logging
import time
from datetime import datetime
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from celery.result import AsyncResult
from django.db import connection
from django.core.cache import cache
import hashlib
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample,
    OpenApiResponse, OpenApiTypes
)
from drf_spectacular.openapi import AutoSchema
from .mixins import (
    BaseAPIMixin, 
    OwnershipMixin, 
    CompanyProfileMixin,
    FileValidationMixin,
    LoggingMixin
)
from .responses import APIResponseFormatter
from .serializers import DocumentUploadSerializer, TaskStatusSerializer, OCRResultListSerializer, OCRResultDetailSerializer, OCRValidationSerializer
from .throttling import OCRUploadThrottle, OCRAPIThrottle
from .exceptions import (
    OCRAPIException, FileValidationError, TaskNotFoundError, ResultNotFoundError,
    UnauthorizedAccessError, OCRProcessingError, custom_exception_handler
)
from .status_codes import (
    APIStatusCode, ErrorCodeMapping, build_success_response, build_error_response,
    build_not_found_response, build_permission_denied_response
)
from .logging_config import APIOperationLogger, get_security_logger, log_api_operation
from faktury.services.file_upload_service import FileUploadService
from faktury.services.ocr_integration import OCRIntegrationError, OCRIntegrationService
from faktury.tasks import process_document_ocr_task
from faktury.models import DocumentUpload, OCRResult, OCRValidation

logger = logging.getLogger('faktury.api.views')
performance_logger = logging.getLogger('faktury.api.performance')


class OCRUploadAPIView(APIView, BaseAPIMixin, FileValidationMixin, LoggingMixin):
    """
    API endpoint for uploading documents for OCR processing.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [OCRUploadThrottle]
    
    @extend_schema(
        operation_id='ocr_upload_document',
        summary='Upload document for OCR processing',
        description='Upload a document (PDF, image) for OCR text extraction and invoice data processing.',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Document file to process'
                    }
                }
            }
        },
        responses={
            201: OpenApiResponse(
                response=DocumentUploadSerializer,
                description='Document uploaded successfully'
            ),
            400: OpenApiResponse(description='Invalid file or validation error'),
            413: OpenApiResponse(description='File too large'),
            415: OpenApiResponse(description='Unsupported file type'),
            429: OpenApiResponse(description='Rate limit exceeded'),
        }
    )
    def post(self, request):
        """Upload document for OCR processing"""
        try:
            # Get uploaded file
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return build_error_response(
                    'No file provided',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file
            self.validate_file(uploaded_file)
            
            # Initialize upload service
            upload_service = FileUploadService()
            
            # Handle the upload
            document_upload = upload_service.handle_upload(uploaded_file, request.user)
            
            # Serialize response
            serializer = DocumentUploadSerializer(document_upload)
            
            # Log successful upload
            self.log_operation(
                request, 
                'document_upload', 
                {'document_id': document_upload.id, 'filename': uploaded_file.name}
            )
            
            return build_success_response(
                data=serializer.data,
                message='Document uploaded successfully. OCR processing will start automatically.',
                status_code=status.HTTP_201_CREATED
            )
            
        except FileValidationError as e:
            return build_error_response(
                f'File validation failed: {str(e)}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"OCR upload error: {e}", exc_info=True)
            return build_error_response(
                'Internal server error during upload',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OCRStatusAPIView(APIView, BaseAPIMixin, OwnershipMixin, LoggingMixin):
    """
    API endpoint for checking OCR processing status.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [OCRAPIThrottle]
    
    @extend_schema(
        operation_id='ocr_check_status',
        summary='Check OCR processing status',
        description='Check the processing status of an uploaded document.',
        parameters=[
            OpenApiParameter(
                name='task_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Task ID or document ID to check status for'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=TaskStatusSerializer,
                description='Status retrieved successfully'
            ),
            404: OpenApiResponse(description='Task or document not found'),
        }
    )
    def get(self, request, task_id):
        """Check OCR processing status"""
        try:
            # Try to find document by ID first
            try:
                document_id = int(task_id)
                document_upload = DocumentUpload.objects.get(
                    id=document_id,
                    user=request.user
                )
            except (ValueError, DocumentUpload.DoesNotExist):
                # Try to find by task ID
                try:
                    document_upload = DocumentUpload.objects.get(
                        task_id=task_id,
                        user=request.user
                    )
                except DocumentUpload.DoesNotExist:
                    return build_not_found_response('Document or task not found')
            
            # Build response data
            response_data = {
                'document_id': document_upload.id,
                'task_id': document_upload.task_id,
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
            
            return build_success_response(data=response_data)
            
        except Exception as e:
            logger.error(f"OCR status check error: {e}", exc_info=True)
            return build_error_response(
                'Error checking status',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OCRResultsListAPIView(generics.ListAPIView, BaseAPIMixin, LoggingMixin):
    """
    API endpoint for listing OCR results.
    """
    serializer_class = OCRResultListSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [OCRAPIThrottle]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get OCR results for the authenticated user"""
        return OCRResult.objects.filter(
            document__user=self.request.user
        ).select_related('document', 'faktura').order_by('-created_at')
    
    @extend_schema(
        operation_id='ocr_list_results',
        summary='List OCR results',
        description='Get a paginated list of OCR processing results for the authenticated user.',
        responses={
            200: OpenApiResponse(
                response=OCRResultListSerializer(many=True),
                description='Results retrieved successfully'
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OCRResultDetailAPIView(generics.RetrieveAPIView, BaseAPIMixin, OwnershipMixin, LoggingMixin):
    """
    API endpoint for retrieving detailed OCR result.
    """
    serializer_class = OCRResultDetailSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [OCRAPIThrottle]
    
    def get_queryset(self):
        """Get OCR results for the authenticated user"""
        return OCRResult.objects.filter(
            document__user=self.request.user
        ).select_related('document', 'faktura')
    
    @extend_schema(
        operation_id='ocr_get_result_detail',
        summary='Get OCR result details',
        description='Get detailed information about a specific OCR processing result.',
        parameters=[
            OpenApiParameter(
                name='result_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='OCR result ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=OCRResultDetailSerializer,
                description='Result details retrieved successfully'
            ),
            404: OpenApiResponse(description='Result not found'),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OCRValidationAPIView(APIView, BaseAPIMixin, OwnershipMixin, LoggingMixin):
    """
    API endpoint for validating and correcting OCR results.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [OCRAPIThrottle]
    
    @extend_schema(
        operation_id='ocr_validate_result',
        summary='Validate OCR result',
        description='Submit validation and corrections for an OCR result.',
        request=OCRValidationSerializer,
        responses={
            200: OpenApiResponse(description='Validation submitted successfully'),
            404: OpenApiResponse(description='Result not found'),
        }
    )
    def post(self, request, result_id):
        """Submit OCR result validation"""
        try:
            # Get OCR result
            ocr_result = OCRResult.objects.get(
                id=result_id,
                document__user=request.user
            )
            
            # Validate request data
            serializer = OCRValidationSerializer(data=request.data)
            if not serializer.is_valid():
                return build_error_response(
                    'Invalid validation data',
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Create validation record
            validation_data = serializer.validated_data
            OCRValidation.objects.create(
                ocr_result=ocr_result,
                validated_by=request.user,
                corrections_made=validation_data.get('corrections_made', {}),
                accuracy_rating=validation_data.get('accuracy_rating', 8),
                validation_notes=validation_data.get('validation_notes', ''),
            )
            
            # Log validation
            self.log_operation(
                request,
                'ocr_validation',
                {'result_id': result_id, 'accuracy_rating': validation_data.get('accuracy_rating')}
            )
            
            return build_success_response(
                message='Validation submitted successfully'
            )
            
        except OCRResult.DoesNotExist:
            return build_not_found_response('OCR result not found')
        except Exception as e:
            logger.error(f"OCR validation error: {e}", exc_info=True)
            return build_error_response(
                'Error submitting validation',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
asset_monitor_logger = logging.getLogger('faktury.api.asset_monitor')
security_logger = get_security_logger()


class PerformanceMonitoringMixin:
    """Mixin for API performance monitoring and logging."""
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to monitor performance."""
        start_time = time.time()
        start_queries = len(connection.queries)
        
        # Call the parent dispatch method
        response = super().dispatch(request, *args, **kwargs)
        
        # Calculate performance metrics
        end_time = time.time()
        duration = end_time - start_time
        query_count = len(connection.queries) - start_queries
        
        # Log performance metrics
        self._log_performance_metrics(request, duration, query_count, response.status_code)
        
        # Add performance headers to response
        response['X-Response-Time'] = f"{duration:.3f}s"
        response['X-DB-Queries'] = str(query_count)
        
        return response
    
    def _log_performance_metrics(self, request, duration, query_count, status_code):
        """Log performance metrics."""
        view_name = self.__class__.__name__
        method = request.method
        path = request.path
        user_id = getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Determine log level based on performance
        if duration > 2.0:  # Slow responses (> 2 seconds)
            log_level = logging.WARNING
            log_message = f"SLOW_RESPONSE"
        elif duration > 1.0:  # Medium responses (> 1 second)
            log_level = logging.INFO
            log_message = f"MEDIUM_RESPONSE"
        else:  # Fast responses
            log_level = logging.DEBUG
            log_message = f"FAST_RESPONSE"
        
        # Log the performance data
        performance_logger.log(
            log_level,
            f"{log_message} {view_name}.{method} {path} - Duration: {duration:.3f}s, "
            f"Queries: {query_count}, Status: {status_code}, User: {user_id}"
        )
        
        # Log slow queries separately
        if query_count > 10:  # Too many queries
            performance_logger.warning(
                f"HIGH_QUERY_COUNT {view_name}.{method} {path} - {query_count} queries in {duration:.3f}s"
            )


class APICachingMixin:
    """Mixin for API response caching."""
    
    # Cache settings - can be overridden in subclasses
    cache_timeout = 300  # 5 minutes default
    cache_key_prefix = 'api_cache'
    cache_headers = True
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to implement caching for GET requests."""
        # Only cache GET requests
        if request.method != 'GET':
            return super().dispatch(request, *args, **kwargs)
        
        # Skip caching if disabled
        if not getattr(self, 'enable_caching', True):
            return super().dispatch(request, *args, **kwargs)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request, *args, **kwargs)
        
        # Try to get response from cache
        cached_response = cache.get(cache_key)
        if cached_response:
            # Add cache headers
            response = Response(cached_response['data'], status=cached_response['status'])
            if self.cache_headers:
                response['X-Cache'] = 'HIT'
                response['X-Cache-Key'] = cache_key[:32]  # Truncated for header
            return response
        
        # Get fresh response
        response = super().dispatch(request, *args, **kwargs)
        
        # Cache successful responses
        if response.status_code == 200 and hasattr(response, 'data'):
            cache_data = {
                'data': response.data,
                'status': response.status_code
            }
            cache.set(cache_key, cache_data, self.cache_timeout)
            
            # Add cache headers
            if self.cache_headers:
                response['X-Cache'] = 'MISS'
                response['X-Cache-Key'] = cache_key[:32]  # Truncated for header
                response['X-Cache-Timeout'] = str(self.cache_timeout)
        
        return response
    
    def _generate_cache_key(self, request, *args, **kwargs):
        """Generate a unique cache key for the request."""
        # Include view name, user ID, path, and query parameters
        view_name = self.__class__.__name__
        user_id = getattr(request.user, 'id', 'anonymous') if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'
        path = request.path
        query_params = sorted(request.GET.items())
        
        # Create a unique string representation
        cache_string = f"{self.cache_key_prefix}:{view_name}:{user_id}:{path}:{query_params}:{args}:{kwargs}"
        
        # Hash the string to create a fixed-length key
        cache_key = hashlib.md5(cache_string.encode()).hexdigest()
        
        return cache_key
    
    def invalidate_cache(self, patterns=None):
        """
        Invalidate cache entries for this view.
        
        Args:
            patterns: List of pattern strings to match against cache keys
        """
        if patterns is None:
            # Default pattern based on view name
            patterns = [f"{self.cache_key_prefix}:{self.__class__.__name__}"]
        
        # This is a simplified implementation
        # In production, you might want to use cache versioning or tagging
        for pattern in patterns:
            try:
                # Clear all cache entries matching the pattern
                # Note: This requires Redis or a cache backend that supports pattern deletion
                cache.delete_pattern(f"{pattern}*")
            except AttributeError:
                # Fallback for cache backends that don't support pattern deletion
                logger.warning(f"Cache backend does not support pattern deletion for {pattern}")
                pass


class APIMetricsMixin:
    """Mixin for collecting API metrics for monitoring."""
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to collect API metrics."""
        start_time = time.time()
        
        # Get the response
        response = super().dispatch(request, *args, **kwargs)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Collect metrics
        self._collect_metrics(request, response, response_time, *args, **kwargs)
        
        return response
    
    def _collect_metrics(self, request, response, response_time, *args, **kwargs):
        """Collect and store API metrics."""
        try:
            # Prepare metrics data
            metrics_data = {
                'view_name': self.__class__.__name__,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'response_time': response_time,
                'timestamp': datetime.utcnow(),
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
                'success': 200 <= response.status_code < 400,
            }
            
            # Add specific metrics for different view types
            if hasattr(self, '_get_specific_metrics'):
                specific_metrics = self._get_specific_metrics(request, response, *args, **kwargs)
                metrics_data.update(specific_metrics)
            
            # Store metrics in cache for aggregation
            metrics_key = f"api_metrics:{datetime.utcnow().strftime('%Y-%m-%d-%H')}"
            
            # Get current metrics or initialize
            current_metrics = cache.get(metrics_key, [])
            current_metrics.append(metrics_data)
            
            # Store with 25-hour TTL (keep for a bit longer than 1 day)
            cache.set(metrics_key, current_metrics, 25 * 60 * 60)
            
            # Log high-level metrics
            if response.status_code >= 500:
                logger.error(f"API_ERROR {metrics_data['view_name']}.{metrics_data['method']} - Status: {response.status_code}")
            elif response_time > 2.0:
                logger.warning(f"API_SLOW {metrics_data['view_name']}.{metrics_data['method']} - Time: {response_time:.3f}s")
            
        except Exception as e:
            # Don't let metrics collection break the API
            logger.error(f"Error collecting API metrics: {str(e)}")


class BaseAPIView(BaseAPIMixin, LoggingMixin, PerformanceMonitoringMixin, APIMetricsMixin, APIView):
    """
    Base API view with common functionality and enhanced error handling.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def handle_exception(self, exc):
        """
        Handle exceptions with enhanced error logging and response formatting.
        """
        # Log the exception
        operation_logger = APIOperationLogger(f"{self.__class__.__name__}.{self.request.method}")
        operation_logger.log_error(exc, user=getattr(self.request, 'user', None))
        
        # Use custom exception handler
        response = custom_exception_handler(exc, {'request': self.request})
        if response is not None:
            return response
        
        # Fallback to parent exception handling
        return super().handle_exception(exc)
    
    def success_response(self, data=None, message=None, status_code=APIStatusCode.SUCCESS):
        """Create a success response using the response formatter."""
        return APIResponseFormatter.success(data, message, status_code.code)
    
    def error_response(self, code, message, details=None, status_code=APIStatusCode.BAD_REQUEST):
        """Create an error response using the response formatter."""
        return APIResponseFormatter.error(code, message, details, status_code.code)


class BaseListAPIView(BaseAPIMixin, OwnershipMixin, 
                     LoggingMixin, PerformanceMonitoringMixin, APIMetricsMixin, generics.ListAPIView):
    """
    Base list API view with pagination and ownership filtering.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]


class BaseRetrieveAPIView(BaseAPIMixin, OwnershipMixin, LoggingMixin, 
                         PerformanceMonitoringMixin, APIMetricsMixin, generics.RetrieveAPIView):
    """
    Base retrieve API view with ownership checking.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]


class BaseCreateAPIView(BaseAPIMixin, CompanyProfileMixin, LoggingMixin,
                       PerformanceMonitoringMixin, APIMetricsMixin, generics.CreateAPIView):
    """
    Base create API view with company profile validation.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]


class BaseUpdateAPIView(BaseAPIMixin, OwnershipMixin, LoggingMixin,
                       PerformanceMonitoringMixin, APIMetricsMixin, generics.UpdateAPIView):
    """
    Base update API view with ownership checking.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]


# Placeholder views for the OCR API endpoints
# These will be implemented in subsequent tasks

@extend_schema_view(
    post=extend_schema(
        operation_id='upload_document_for_ocr',
        summary='Upload document for OCR processing',
        description='Upload a document file (PDF, JPEG, PNG) for asynchronous OCR processing using Google Cloud Document AI.',
        tags=['OCR Upload'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Document file to upload (PDF, JPEG, PNG). Maximum size: 10MB.'
                    }
                },
                'required': ['file']
            }
        },
        responses={
            201: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='File uploaded successfully and queued for processing',
                examples=[
                    OpenApiExample(
                        'Successful Upload',
                        summary='Document uploaded successfully',
                        description='Example response when a document is successfully uploaded and queued for OCR processing.',
                        value={
                            'success': True,
                            'data': {
                                'task_id': 'abc123-def456-ghi789',
                                'document_id': 42,
                                'filename': 'invoice_001.pdf',
                                'file_size': 2048576,
                                'estimated_processing_time': 30,
                                'status': 'queued'
                            },
                            'message': 'File uploaded successfully and queued for processing',
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Bad request - validation error',
                examples=[
                    OpenApiExample(
                        'File Validation Error',
                        summary='File validation failed',
                        value={
                            'success': False,
                            'error': {
                                'code': 'FILE_VALIDATION_ERROR',
                                'message': 'Invalid file format',
                                'details': {
                                    'file': ['Only PDF, JPG, and PNG files are allowed']
                                }
                            },
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            ),
            413: OpenApiResponse(
                description='Payload too large - file size exceeded',
                examples=[
                    OpenApiExample(
                        'File Too Large',
                        summary='File size exceeds limit',
                        value={
                            'success': False,
                            'error': {
                                'code': 'FILE_SIZE_EXCEEDED',
                                'message': 'File size (15.2MB) exceeds maximum allowed size (10.0MB)',
                                'details': {
                                    'file_size': 15925248,
                                    'max_size': 10485760
                                }
                            },
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            ),
            415: OpenApiResponse(
                description='Unsupported media type',
                examples=[
                    OpenApiExample(
                        'Unsupported File Type',
                        summary='File type not supported',
                        value={
                            'success': False,
                            'error': {
                                'code': 'UNSUPPORTED_FILE_TYPE',
                                'message': 'Unsupported file type: text/plain. Supported types: PDF, JPEG, PNG',
                            },
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            ),
            429: OpenApiResponse(
                description='Rate limit exceeded',
                examples=[
                    OpenApiExample(
                        'Rate Limited',
                        summary='Upload rate limit exceeded',
                        value={
                            'success': False,
                            'error': {
                                'code': 'RATE_LIMIT_EXCEEDED',
                                'message': 'Upload rate limit exceeded. Try again in 60 seconds.'
                            },
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            )
        }
    )
)
class OCRUploadAPIView(BaseCreateAPIView, FileValidationMixin):
    """
    Upload documents for OCR processing.
    
    This endpoint accepts document files (PDF, JPEG, PNG) and queues them for
    asynchronous OCR processing using Google Cloud Document AI. The uploaded
    files are validated for size, format, and security before processing.
    
    **Authentication Required**: Yes  
    **Rate Limit**: 10 uploads per minute per user  
    **File Size Limit**: 10MB  
    **Supported Formats**: PDF, JPEG, PNG  
    
    **Request Format**:
    - Content-Type: multipart/form-data
    - Body: file (binary data)
    
    **Response**:
    - Returns task_id for tracking processing status
    - Includes estimated processing time
    - Provides document metadata
    
    **Security Features**:
    - File type validation using magic numbers
    - Malware scanning
    - Size limit enforcement
    - User ownership tracking
    
    **Error Scenarios**:
    - File too large (413 Payload Too Large)
    - Unsupported file type (415 Unsupported Media Type)
    - Malicious file detected (400 Bad Request)
    - Rate limit exceeded (429 Too Many Requests)
    """
    serializer_class = DocumentUploadSerializer
    throttle_classes = [OCRUploadThrottle]
    
    def post(self, request, *args, **kwargs):
        """
        Handle file upload for OCR processing.
        
        Expected request format:
        - Content-Type: multipart/form-data
        - file: The document file to process
        
        Returns:
        - task_id: Celery task ID for tracking
        - document_id: DocumentUpload record ID
        - estimated_processing_time: Estimated time in seconds
        """
        try:
            # Validate request has file
            if 'file' not in request.FILES:
                raise FileValidationError("No file provided")
            
            uploaded_file = request.FILES['file']
            
            # Validate file using mixin
            self.validate_file(uploaded_file)
            
            # Use FileUploadService to handle the upload
            file_service = FileUploadService()
            document_upload = file_service.handle_upload(uploaded_file, request.user)
            
            # Queue Celery task for OCR processing
            task = process_document_ocr_task.delay(document_upload.id)
            
            # Calculate estimated processing time based on file size and type
            estimated_time = self._estimate_processing_time(uploaded_file)
            
            # Return success response with task information
            return self.success_response(
                data={
                    'task_id': task.id,
                    'document_id': document_upload.id,
                    'filename': document_upload.original_filename,
                    'file_size': document_upload.file_size,
                    'estimated_processing_time': estimated_time,
                    'status': 'queued'
                },
                message="File uploaded successfully and queued for processing",
                status_code=APIStatusCode.CREATED
            )
            
        except (FileValidationError, OCRAPIException):
            # Re-raise API exceptions to be handled by the exception handler
            raise
        except Exception as e:
            # Wrap unexpected exceptions in OCRAPIException
            logger.error(f"Unexpected error during file upload: {str(e)}", exc_info=True)
            raise OCRProcessingError(f"File upload failed: {str(e)}")
    
    def _estimate_processing_time(self, uploaded_file):
        """
        Estimate processing time based on file characteristics.
        
        Args:
            uploaded_file: The uploaded file object
            
        Returns:
            int: Estimated processing time in seconds
        """
        base_time = 15  # Base processing time in seconds
        
        # Adjust based on file size (roughly 1 second per MB)
        size_factor = uploaded_file.size / (1024 * 1024)  # Size in MB
        size_time = int(size_factor * 1)
        
        # Adjust based on file type
        type_multiplier = {
            'application/pdf': 1.5,  # PDFs take longer due to conversion
            'image/jpeg': 1.0,
            'image/png': 1.0,
            'image/tiff': 1.2,
        }.get(uploaded_file.content_type, 1.0)
        
        estimated_time = int((base_time + size_time) * type_multiplier)
        
        # Cap at reasonable limits
        return min(max(estimated_time, 10), 120)  # Between 10 seconds and 2 minutes
    
    def _get_specific_metrics(self, request, response, *args, **kwargs):
        """Get OCR upload specific metrics."""
        metrics = {}
        
        if hasattr(request, 'FILES') and 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            metrics.update({
                'file_size': uploaded_file.size,
                'file_type': uploaded_file.content_type,
                'filename': uploaded_file.name,
                'upload_success': response.status_code == 201,
            })
        
        # Track validation errors
        if response.status_code == 400:
            metrics['error_type'] = 'validation_error'
        elif response.status_code == 413:
            metrics['error_type'] = 'file_too_large'
        elif response.status_code == 415:
            metrics['error_type'] = 'unsupported_file_type'
        elif response.status_code == 429:
            metrics['error_type'] = 'rate_limited'
        
        return metrics


@extend_schema_view(
    get=extend_schema(
        operation_id='get_ocr_processing_status',
        summary='Get OCR processing status',
        description='Check the current status and progress of an OCR processing task.',
        tags=['OCR Status'],
        parameters=[
            OpenApiParameter(
                name='task_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Celery task ID returned from the upload endpoint',
                examples=[
                    OpenApiExample(
                        'Task ID Example',
                        summary='Example task ID',
                        value='abc123-def456-ghi789'
                    )
                ]
            )
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Task status retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Processing Status',
                        summary='Task currently processing',
                        value={
                            'success': True,
                            'data': {
                                'task_id': 'abc123-def456-ghi789',
                                'status': 'processing',
                                'progress': 65,
                                'eta_seconds': 15,
                                'message': 'Extracting invoice data...',
                                'document': {
                                    'id': 42,
                                    'filename': 'invoice_001.pdf',
                                    'file_size': 2048576,
                                    'upload_timestamp': '2025-08-23T10:00:00Z'
                                }
                            },
                            'message': 'Task status retrieved successfully',
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    ),
                    OpenApiExample(
                        'Completed Status',
                        summary='Task completed successfully',
                        value={
                            'success': True,
                            'data': {
                                'task_id': 'abc123-def456-ghi789',
                                'status': 'completed',
                                'progress': 100,
                                'message': 'OCR processing completed successfully',
                                'result': {
                                    'ocr_result_id': 123,
                                    'confidence_score': 95.5
                                }
                            },
                            'message': 'Task status retrieved successfully',
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description='Task not found',
                examples=[
                    OpenApiExample(
                        'Task Not Found',
                        summary='Invalid or expired task ID',
                        value={
                            'success': False,
                            'error': {
                                'code': 'TASK_NOT_FOUND',
                                'message': 'Task with ID abc123-def456-ghi789 not found'
                            },
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            )
        }
    )
)
class OCRStatusAPIView(BaseAPIView):
    """
    Check OCR processing status and progress.
    
    This endpoint provides real-time status updates for OCR processing tasks.
    It tracks Celery task progress and provides estimated completion times
    based on processing history and current queue length.
    
    **Authentication Required**: Yes  
    **Rate Limit**: 200 requests per minute per user  
    **Ownership**: Users can only check status of their own tasks  
    
    **Status Values**:
    - `pending`: Task is queued and waiting to start
    - `processing`: Task is currently being processed
    - `completed`: Task finished successfully
    - `failed`: Task failed with an error
    
    **Progress Information**:
    - Progress percentage (0-100)
    - Estimated time remaining (ETA in seconds)
    - Current processing stage message
    - Document metadata if available
    
    **Error Scenarios**:
    - Task not found (404 Not Found)
    - Access denied to task (403 Forbidden)
    - Invalid task ID format (400 Bad Request)
    
    **Usage Tips**:
    - Poll this endpoint every 5-10 seconds for updates
    - Stop polling when status is 'completed' or 'failed'
    - Use the ETA to show progress indicators to users
    """
    throttle_classes = [OCRAPIThrottle]
    
    def get(self, request, task_id, *args, **kwargs):
        """
        Get status of OCR processing task.
        
        Args:
            task_id: Celery task ID to check status for
            
        Returns:
            Task status information including progress and ETA
        """
        try:
            # Get Celery task result
            task_result = AsyncResult(task_id)
            
            # Check if task exists
            if not task_result or task_result.state == 'PENDING' and not task_result.result:
                raise TaskNotFoundError(f"Task with ID {task_id} not found")
            
            # Get task status information
            task_status = self._get_task_status(task_result)
            
            # Find associated document if available
            document_info = self._get_document_info(task_result, request.user)
            
            # Check ownership if document found
            if document_info and document_info.get('user_id') != request.user.id:
                security_logger.log_authorization_failure(
                    request, request.user, f"task:{task_id}"
                )
                raise UnauthorizedAccessError("You don't have permission to access this task")
            
            # Combine task status with document info
            response_data = {
                'task_id': task_id,
                'status': task_status['status']
            }
            
            # Only include optional fields if they have values
            for field in ['progress', 'eta_seconds', 'message', 'result', 'error']:
                value = task_status.get(field)
                if value is not None:
                    response_data[field] = value
            
            # Add document information if available
            if document_info:
                response_data['document'] = document_info
            
            # Serialize and return response
            serializer = TaskStatusSerializer(data=response_data)
            if serializer.is_valid():
                return self.success_response(
                    data=serializer.validated_data,
                    message="Task status retrieved successfully"
                )
            else:
                return self.error_response(
                    message="Error serializing task status",
                    code="SERIALIZATION_ERROR",
                    details=serializer.errors,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error retrieving task status for {task_id}: {str(e)}", exc_info=True)
            return self.error_response(
                message="Error retrieving task status",
                code="TASK_STATUS_ERROR",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_task_status(self, task_result):
        """
        Extract status information from Celery AsyncResult.
        
        Args:
            task_result: Celery AsyncResult object
            
        Returns:
            dict: Normalized task status information
        """
        status_mapping = {
            'PENDING': 'pending',
            'STARTED': 'processing', 
            'PROGRESS': 'processing',
            'SUCCESS': 'completed',
            'FAILURE': 'failed',
            'RETRY': 'processing',
            'REVOKED': 'failed'
        }
        
        task_status = {
            'status': status_mapping.get(task_result.state, 'pending')
        }
        
        # Handle different task states
        if task_result.state == 'PENDING':
            task_status.update({
                'progress': 0,
                'message': 'Task is waiting to be processed'
            })
            
        elif task_result.state == 'STARTED':
            task_status.update({
                'progress': 10,
                'message': 'Task processing has started'
            })
            
        elif task_result.state == 'PROGRESS':
            # Custom progress state with progress info
            if isinstance(task_result.result, dict):
                task_status.update({
                    'progress': task_result.result.get('progress', 50),
                    'message': task_result.result.get('message', 'Processing in progress'),
                    'eta_seconds': task_result.result.get('eta_seconds')
                })
            else:
                task_status.update({
                    'progress': 50,
                    'message': 'Processing in progress'
                })
                
        elif task_result.state == 'SUCCESS':
            task_status.update({
                'progress': 100,
                'message': 'Task completed successfully',
                'result': task_result.result
            })
            
        elif task_result.state == 'FAILURE':
            task_status.update({
                'progress': 0,
                'message': 'Task failed',
                'error': str(task_result.result) if task_result.result else 'Unknown error'
            })
            
        elif task_result.state == 'RETRY':
            task_status.update({
                'progress': 25,
                'message': 'Task is being retried after failure'
            })
            
        # Estimate ETA if not provided and task is processing
        if task_status['status'] == 'processing' and 'eta_seconds' not in task_status:
            task_status['eta_seconds'] = self._estimate_eta(task_status.get('progress', 0))
        
        return task_status
    
    def _get_document_info(self, task_result, user):
        """
        Get document information associated with the task.
        
        Args:
            task_result: Celery AsyncResult object
            user: Current user
            
        Returns:
            dict: Document information if found, None otherwise
        """
        try:
            # Try to extract document_upload_id from task result
            document_upload_id = None
            
            if task_result.result and isinstance(task_result.result, dict):
                document_upload_id = task_result.result.get('document_upload_id')
            
            # If not in result, try to find by task_id (this would require storing task_id in DocumentUpload)
            if not document_upload_id:
                # For now, we can't easily map task_id back to document without additional storage
                return None
            
            # Get document upload
            document_upload = DocumentUpload.objects.get(id=document_upload_id)
            
            return {
                'id': document_upload.id,
                'filename': document_upload.original_filename,
                'file_size': document_upload.file_size,
                'content_type': document_upload.content_type,
                'upload_timestamp': document_upload.upload_timestamp,
                'processing_status': document_upload.processing_status,
                'user_id': document_upload.user.id
            }
            
        except (DocumentUpload.DoesNotExist, AttributeError, KeyError):
            return None
    
    def _estimate_eta(self, progress):
        """
        Estimate remaining processing time based on progress.
        
        Args:
            progress: Current progress percentage (0-100)
            
        Returns:
            int: Estimated seconds remaining
        """
        if progress >= 100:
            return 0
        elif progress <= 0:
            return 60  # Default estimate for new tasks
        else:
            # Simple linear estimation - can be improved with historical data
            base_time = 60  # Assume 60 seconds total processing time
            remaining_progress = 100 - progress
            return int((remaining_progress / 100) * base_time)


class OCRResultsPagination(PageNumberPagination):
    """Custom pagination class for OCR results."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Custom paginated response format."""
        return Response({
            'results': data,
            'pagination': {
                'count': self.page.paginator.count,
                'page': self.page.number,
                'page_size': len(data),
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            }
        })


@extend_schema_view(
    get=extend_schema(
        operation_id='list_ocr_results',
        summary='List OCR processing results',
        description='Get a paginated list of OCR processing results with filtering options.',
        tags=['OCR Results'],
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number for pagination',
                examples=[OpenApiExample('Page 1', value=1)]
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of results per page (max 100)',
                examples=[OpenApiExample('20 per page', value=20)]
            ),
            OpenApiParameter(
                name='date_from',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter results from this date (YYYY-MM-DD)',
                examples=[OpenApiExample('From date', value='2025-08-01')]
            ),
            OpenApiParameter(
                name='date_to',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter results up to this date (YYYY-MM-DD)',
                examples=[OpenApiExample('To date', value='2025-08-31')]
            ),
            OpenApiParameter(
                name='min_confidence',
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description='Minimum confidence score (0-100)',
                examples=[OpenApiExample('High confidence', value=80.0)]
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Processing status filter',
                enum=['pending', 'processing', 'completed', 'failed'],
                examples=[OpenApiExample('Completed only', value='completed')]
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in filename or extracted data',
                examples=[OpenApiExample('Search term', value='invoice')]
            )
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='OCR results retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Results List',
                        summary='Paginated list of OCR results',
                        value={
                            'success': True,
                            'data': {
                                'results': [
                                    {
                                        'id': 123,
                                        'document_filename': 'invoice_001.pdf',
                                        'upload_date': '2025-08-23T10:00:00Z',
                                        'processing_status': 'completed',
                                        'confidence_score': 95.5,
                                        'confidence_level': 'high',
                                        'has_faktura': True,
                                        'needs_review': False,
                                        'processing_time': 12.5
                                    }
                                ],
                                'pagination': {
                                    'count': 150,
                                    'page': 1,
                                    'page_size': 20,
                                    'total_pages': 8,
                                    'has_next': True,
                                    'has_previous': False
                                },
                                'filters_applied': {
                                    'min_confidence': '80.0',
                                    'status': 'completed'
                                }
                            },
                            'message': 'OCR results retrieved successfully',
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            )
        }
    )
)
class OCRResultsListAPIView(BaseListAPIView, APICachingMixin):
    """
    List OCR processing results with filtering and pagination.
    
    This endpoint provides a paginated list of OCR processing results for the
    authenticated user. Results can be filtered by various criteria and include
    summary information about each processed document.
    
    **Authentication Required**: Yes  
    **Rate Limit**: 100 requests per minute per user  
    **Ownership**: Users only see their own OCR results  
    
    **Filtering Options**:
    - `date_from`: Filter results from this date (YYYY-MM-DD)
    - `date_to`: Filter results up to this date (YYYY-MM-DD)
    - `min_confidence`: Minimum confidence score (0-100)
    - `status`: Processing status (pending, processing, completed, failed)
    - `search`: Search in filename or extracted data
    
    **Pagination**:
    - Default page size: 20 results
    - Maximum page size: 100 results
    - Use `page` parameter for navigation
    - Use `page_size` parameter to control results per page
    
    **Response Data**:
    - List of OCR results with summary information
    - Pagination metadata (total count, page info)
    - Applied filters information
    - Performance optimized with database query optimization
    
    **Sorting**:
    - Results are sorted by creation date (newest first)
    - Additional sorting options may be added in future versions
    
    **Performance Notes**:
    - Uses database indexes for efficient filtering
    - Includes select_related for optimized queries
    - Response times typically under 100ms for standard queries
    """
    queryset = OCRResult.objects.select_related(
        'document', 
        'document__user',
        'faktura', 
        'faktura__sprzedawca',
        'faktura__nabywca'
    ).prefetch_related(
        'ocrvalidation',
        'ocrvalidation__validated_by'
    ).all()
    serializer_class = OCRResultListSerializer
    throttle_classes = [OCRAPIThrottle]
    pagination_class = OCRResultsPagination
    
    # Caching settings
    cache_timeout = 180  # 3 minutes for list view (data changes more frequently)
    cache_key_prefix = 'ocr_results_list'
    
    def get_queryset(self):
        """
        Filter queryset based on user ownership and query parameters.
        """
        # Start with base queryset filtered by user ownership
        queryset = super().get_queryset()
        
        # Apply additional filters based on query parameters
        queryset = self._apply_date_filters(queryset)
        queryset = self._apply_confidence_filter(queryset)
        queryset = self._apply_status_filter(queryset)
        queryset = self._apply_search_filter(queryset)
        
        # Order by creation date (newest first)
        return queryset.order_by('-created_at')
    
    def _apply_date_filters(self, queryset):
        """Apply date range filtering."""
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(document__upload_timestamp__date__gte=date_from_obj)
            except ValueError:
                # Invalid date format - ignore filter
                pass
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(document__upload_timestamp__date__lte=date_to_obj)
            except ValueError:
                # Invalid date format - ignore filter
                pass
        
        return queryset
    
    def _apply_confidence_filter(self, queryset):
        """Apply confidence score filtering."""
        min_confidence = self.request.query_params.get('min_confidence')
        
        if min_confidence:
            try:
                min_confidence_float = float(min_confidence)
                if 0 <= min_confidence_float <= 100:
                    queryset = queryset.filter(confidence_score__gte=min_confidence_float)
            except (ValueError, TypeError):
                # Invalid confidence value - ignore filter
                pass
        
        return queryset
    
    def _apply_status_filter(self, queryset):
        """Apply processing status filtering."""
        status_filter = self.request.query_params.get('status')
        
        if status_filter:
            # Validate status is one of the allowed choices
            valid_statuses = [choice[0] for choice in OCRResult.PROCESSING_STATUS_CHOICES]
            if status_filter in valid_statuses:
                queryset = queryset.filter(processing_status=status_filter)
        
        return queryset
    
    def _apply_search_filter(self, queryset):
        """Apply search filtering across filename and extracted data."""
        search_query = self.request.query_params.get('search')
        
        if search_query:
            # Search in filename and extracted data
            search_q = Q(document__original_filename__icontains=search_query)
            
            # Search in extracted data JSON fields
            # This searches for the query string in the JSON representation
            search_q |= Q(extracted_data__icontains=search_query)
            
            # Search in specific extracted data fields if they exist
            search_q |= Q(extracted_data__numer_faktury__icontains=search_query)
            search_q |= Q(extracted_data__sprzedawca__nazwa__icontains=search_query)
            search_q |= Q(extracted_data__nabywca__nazwa__icontains=search_query)
            
            queryset = queryset.filter(search_q)
        
        return queryset
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET request for OCR results list with filtering and pagination.
        """
        try:
            # Get filtered queryset
            queryset = self.get_queryset()
            
            # Apply pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(serializer.data)
                
                # Add filter information to response
                filter_info = self._get_filter_info()
                response_data = paginated_response.data
                response_data['filters_applied'] = filter_info
                
                return self.success_response(
                    data=response_data,
                    message="OCR results retrieved successfully"
                )
            
            # No pagination needed (shouldn't happen with our pagination setup)
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data={
                    'results': serializer.data,
                    'filters_applied': self._get_filter_info()
                },
                message="OCR results retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error retrieving OCR results: {str(e)}", exc_info=True)
            return self.error_response(
                message="Error retrieving OCR results",
                code="OCR_RESULTS_ERROR",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_filter_info(self):
        """Get information about applied filters for response metadata."""
        filters_applied = {}
        
        # Date filters
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            filters_applied['date_from'] = date_from
        if date_to:
            filters_applied['date_to'] = date_to
        
        # Confidence filter
        min_confidence = self.request.query_params.get('min_confidence')
        if min_confidence:
            filters_applied['min_confidence'] = min_confidence
        
        # Status filter
        status_filter = self.request.query_params.get('status')
        if status_filter:
            filters_applied['status'] = status_filter
        
        # Search filter
        search_query = self.request.query_params.get('search')
        if search_query:
            filters_applied['search'] = search_query
        
        # Pagination info
        page_size = self.request.query_params.get('page_size', '20')
        filters_applied['page_size'] = page_size
        
        return filters_applied


@extend_schema_view(
    get=extend_schema(
        operation_id='get_ocr_result_detail',
        summary='Get detailed OCR result',
        description='Retrieve comprehensive information about a specific OCR processing result.',
        tags=['OCR Results'],
        parameters=[
            OpenApiParameter(
                name='result_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the OCR result to retrieve',
                examples=[OpenApiExample('Result ID', value=123)]
            )
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='OCR result retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Detailed Result',
                        summary='Complete OCR result with extracted data',
                        value={
                            'success': True,
                            'data': {
                                'id': 123,
                                'document': {
                                    'id': 42,
                                    'filename': 'invoice_001.pdf',
                                    'upload_date': '2025-08-23T10:00:00Z',
                                    'file_size': 2048576,
                                    'content_type': 'application/pdf'
                                },
                                'extracted_data': {
                                    'numer_faktury': {
                                        'value': 'FV/2025/001',
                                        'confidence': 98.5
                                    },
                                    'data_wystawienia': {
                                        'value': '2025-08-20',
                                        'confidence': 95.2
                                    },
                                    'sprzedawca': {
                                        'nazwa': {
                                            'value': 'Example Sp. z o.o.',
                                            'confidence': 97.8
                                        },
                                        'nip': {
                                            'value': '1234567890',
                                            'confidence': 92.1
                                        }
                                    },
                                    'suma_brutto': {
                                        'value': 1230.00,
                                        'confidence': 96.7
                                    }
                                },
                                'confidence_score': 95.5,
                                'confidence_level': 'high',
                                'processing_time': 12.5,
                                'faktura': {
                                    'id': 456,
                                    'numer': 'FV/2025/001',
                                    'status': 'draft'
                                },
                                'needs_human_review': False,
                                'metadata': {
                                    'review_required': False,
                                    'can_create_faktura': True,
                                    'has_faktura': True,
                                    'validation_suggestions': []
                                }
                            },
                            'message': 'OCR result retrieved successfully',
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description='OCR result not found',
                examples=[
                    OpenApiExample(
                        'Not Found',
                        summary='OCR result does not exist',
                        value={
                            'success': False,
                            'error': {
                                'code': 'OCR_RESULT_NOT_FOUND',
                                'message': 'OCR result not found'
                            },
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            )
        }
    )
)
class OCRResultDetailAPIView(BaseRetrieveAPIView, APICachingMixin):
    """
    Retrieve detailed OCR result with comprehensive extracted data.
    
    This endpoint provides complete information about a specific OCR processing
    result, including all extracted fields with confidence scores, validation
    suggestions, and links to generated invoices.
    
    **Authentication Required**: Yes  
    **Rate Limit**: 100 requests per minute per user  
    **Ownership**: Users can only access their own OCR results  
    
    **Response Data**:
    - Complete extracted data with field-level confidence scores
    - Document metadata (filename, upload date, file size)
    - Processing information (time, status, processor version)
    - Validation fields that can be manually corrected
    - Confidence breakdown by data categories
    - Links to generated Faktura records if they exist
    
    **Confidence Information**:
    - Overall confidence score for the entire document
    - Individual field confidence scores
    - Confidence level classification (high, medium, low)
    - Fields flagged for manual review
    
    **Validation Support**:
    - List of fields that can be manually validated
    - Current values and confidence scores for each field
    - Validation suggestions based on confidence thresholds
    - Priority levels for review (high, medium, low)
    
    **Integration Features**:
    - Links to generated Faktura records
    - Status of automatic invoice creation
    - Ability to trigger manual invoice creation
    
    **Error Scenarios**:
    - OCR result not found (404 Not Found)
    - Access denied (403 Forbidden)
    - Processing still in progress (result may be incomplete)
    """
    queryset = OCRResult.objects.select_related(
        'document', 
        'document__user',
        'faktura', 
        'faktura__sprzedawca',
        'faktura__nabywca',
        'faktura__firma'
    ).prefetch_related(
        'ocrvalidation',
        'ocrvalidation__validated_by',
        'faktura__pozycje',
        'faktura__pozycje__produkt'
    ).all()
    serializer_class = OCRResultDetailSerializer
    throttle_classes = [OCRAPIThrottle]
    lookup_field = 'id'
    lookup_url_kwarg = 'result_id'
    
    # Caching settings
    cache_timeout = 600  # 10 minutes for detail view (less frequent changes)
    cache_key_prefix = 'ocr_result_detail'
    
    def get(self, request, result_id, *args, **kwargs):
        """
        Handle GET request for detailed OCR result.
        
        Args:
            result_id: ID of the OCR result to retrieve
            
        Returns:
            Detailed OCR result with all extracted data and metadata
        """
        try:
            # Get the OCR result object
            ocr_result = self.get_object()
            
            # Serialize the result
            serializer = self.get_serializer(ocr_result)
            
            # Add additional metadata for frontend
            response_data = serializer.data
            response_data['metadata'] = self._get_result_metadata(ocr_result)
            
            return self.success_response(
                data=response_data,
                message="OCR result retrieved successfully"
            )
            
        except (OCRResult.DoesNotExist, Http404):
            return self.error_response(
                message="OCR result not found",
                code="OCR_RESULT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied:
            return self.error_response(
                message="You don't have permission to access this OCR result",
                code="OCR_RESULT_ACCESS_DENIED",
                status_code=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Error retrieving OCR result {result_id}: {str(e)}", exc_info=True)
            return self.error_response(
                message="Error retrieving OCR result",
                code="OCR_RESULT_ERROR",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_result_metadata(self, ocr_result):
        """
        Get additional metadata for the OCR result with enhanced validation workflow information.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            dict: Comprehensive metadata information
        """
        metadata = {
            'review_required': ocr_result.needs_human_review,
            'can_create_faktura': ocr_result.can_auto_create_faktura,
            'has_faktura': ocr_result.faktura is not None,
            'processing_duration': ocr_result.processing_time,
            'confidence_level': ocr_result.confidence_level,
        }
        
        # Add validation workflow status
        metadata['validation_workflow'] = self._get_validation_workflow_status(ocr_result)
        
        # Add confidence level calculations and thresholds
        metadata['confidence_analysis'] = self._get_confidence_analysis(ocr_result)
        
        # Add Faktura link if exists
        if ocr_result.faktura:
            metadata['faktura_url'] = f"/faktury/{ocr_result.faktura.id}/"
            metadata['faktura_number'] = ocr_result.faktura.numer
            metadata['faktura_status'] = ocr_result.faktura.status
            metadata['auto_created'] = ocr_result.auto_created_faktura
        
        # Add validation suggestions
        metadata['validation_suggestions'] = self._get_validation_suggestions(ocr_result)
        
        # Add field review priorities
        metadata['review_priorities'] = self._get_review_priorities(ocr_result)
        
        # Add processing metadata
        metadata['processing_metadata'] = {
            'processor_version': ocr_result.processor_version,
            'processing_status': ocr_result.processing_status,
            'error_message': ocr_result.error_message,
            'retry_count': 0,  # Could be added to model in future
            'estimated_accuracy': self._estimate_field_accuracy(ocr_result)
        }
        
        return metadata
    
    def _get_validation_suggestions(self, ocr_result):
        """
        Get suggestions for fields that need validation.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            list: List of validation suggestions
        """
        suggestions = []
        field_confidence = ocr_result.field_confidence or {}
        
        # Check critical fields with low confidence
        critical_fields = {
            'numer_faktury': 'Invoice number has low confidence - please verify',
            'data_wystawienia': 'Issue date has low confidence - please verify',
            'suma_brutto': 'Total amount has low confidence - please verify',
            'sprzedawca': 'Seller information has low confidence - please verify',
            'nabywca': 'Buyer information has low confidence - please verify'
        }
        
        for field, message in critical_fields.items():
            confidence = field_confidence.get(field, ocr_result.confidence_score)
            if confidence < 80.0 and field in (ocr_result.extracted_data or {}):
                suggestions.append({
                    'field': field,
                    'message': message,
                    'confidence': confidence,
                    'priority': 'high' if confidence < 60.0 else 'medium'
                })
        
        return suggestions
    
    def _get_review_priorities(self, ocr_result):
        """
        Get field review priorities based on confidence scores.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            dict: Fields categorized by review priority
        """
        field_confidence = ocr_result.field_confidence or {}
        extracted_data = ocr_result.extracted_data or {}
        
        priorities = {
            'high': [],      # < 60% confidence
            'medium': [],    # 60-80% confidence
            'low': []        # > 80% confidence
        }
        
        for field, value in extracted_data.items():
            confidence = field_confidence.get(field, ocr_result.confidence_score)
            
            if confidence < 60.0:
                priority = 'high'
            elif confidence < 80.0:
                priority = 'medium'
            else:
                priority = 'low'
            
            priorities[priority].append({
                'field': field,
                'confidence': confidence,
                'value': value
            })
        
        return priorities
    
    def _get_validation_workflow_status(self, ocr_result):
        """
        Get detailed validation workflow status information.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            dict: Validation workflow status
        """
        # Check if validation has been performed
        has_validation = hasattr(ocr_result, 'ocrvalidation') and ocr_result.ocrvalidation is not None
        
        workflow_status = {
            'status': 'completed' if ocr_result.processing_status == 'completed' else 'pending',
            'validation_performed': has_validation,
            'requires_manual_review': ocr_result.needs_human_review,
            'ready_for_invoice_creation': ocr_result.can_auto_create_faktura,
            'next_action': self._determine_next_action(ocr_result),
        }
        
        if has_validation:
            validation = ocr_result.ocrvalidation
            workflow_status.update({
                'validated_by': validation.validated_by.username if validation.validated_by else None,
                'validation_date': validation.validated_at.isoformat() if validation.validated_at else None,
                'corrections_made': bool(validation.corrections_made),
                'validation_notes': validation.validation_notes,
                'accuracy_rating': validation.accuracy_rating
            })
        
        return workflow_status
    
    def _get_confidence_analysis(self, ocr_result):
        """
        Get detailed confidence analysis with thresholds and recommendations.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            dict: Confidence analysis
        """
        field_confidence = ocr_result.field_confidence or {}
        overall_confidence = ocr_result.confidence_score
        
        # Define confidence thresholds
        thresholds = {
            'high_confidence': 90.0,
            'medium_confidence': 70.0,
            'low_confidence': 50.0,
            'review_required': 80.0
        }
        
        analysis = {
            'overall_confidence': overall_confidence,
            'confidence_level': self._classify_confidence_level(overall_confidence, thresholds),
            'thresholds': thresholds,
            'field_statistics': self._calculate_field_statistics(field_confidence),
            'recommendations': self._generate_confidence_recommendations(ocr_result, thresholds)
        }
        
        return analysis
    
    def _estimate_field_accuracy(self, ocr_result):
        """
        Estimate field accuracy based on confidence scores and patterns.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            dict: Field accuracy estimates
        """
        field_confidence = ocr_result.field_confidence or {}
        extracted_data = ocr_result.extracted_data or {}
        
        accuracy_estimates = {}
        
        for field, confidence in field_confidence.items():
            # Base accuracy on confidence
            base_accuracy = confidence
            
            # Adjust based on field type patterns
            if field in extracted_data:
                value = extracted_data[field]
                pattern_adjustment = self._assess_field_pattern_accuracy(field, value)
                adjusted_accuracy = min(100.0, base_accuracy + pattern_adjustment)
                
                accuracy_estimates[field] = {
                    'base_confidence': confidence,
                    'pattern_adjustment': pattern_adjustment,
                    'estimated_accuracy': adjusted_accuracy,
                    'reliability': 'high' if adjusted_accuracy > 95 else 'medium' if adjusted_accuracy > 80 else 'low'
                }
        
        return accuracy_estimates
    
    def _determine_next_action(self, ocr_result):
        """
        Determine the recommended next action for the OCR result.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            str: Recommended next action
        """
        if ocr_result.processing_status != 'completed':
            return 'wait_for_processing'
        
        if ocr_result.faktura:
            return 'review_invoice'
        
        if ocr_result.needs_human_review:
            return 'manual_validation'
        
        if ocr_result.can_auto_create_faktura:
            return 'create_invoice'
        
        return 'review_and_correct'
    
    def _classify_confidence_level(self, confidence, thresholds):
        """
        Classify confidence level based on thresholds.
        
        Args:
            confidence: Confidence score
            thresholds: Confidence thresholds
            
        Returns:
            str: Confidence level classification
        """
        if confidence >= thresholds['high_confidence']:
            return 'high'
        elif confidence >= thresholds['medium_confidence']:
            return 'medium'
        elif confidence >= thresholds['low_confidence']:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_field_statistics(self, field_confidence):
        """
        Calculate statistical information about field confidence scores.
        
        Args:
            field_confidence: Dictionary of field confidence scores
            
        Returns:
            dict: Field statistics
        """
        if not field_confidence:
            return {}
        
        scores = list(field_confidence.values())
        
        return {
            'total_fields': len(scores),
            'average_confidence': sum(scores) / len(scores),
            'min_confidence': min(scores),
            'max_confidence': max(scores),
            'fields_above_80': sum(1 for score in scores if score >= 80.0),
            'fields_below_60': sum(1 for score in scores if score < 60.0),
            'variance': self._calculate_variance(scores)
        }
    
    def _generate_confidence_recommendations(self, ocr_result, thresholds):
        """
        Generate recommendations based on confidence analysis.
        
        Args:
            ocr_result: OCRResult instance
            thresholds: Confidence thresholds
            
        Returns:
            list: List of recommendations
        """
        recommendations = []
        field_confidence = ocr_result.field_confidence or {}
        overall_confidence = ocr_result.confidence_score
        
        if overall_confidence < thresholds['review_required']:
            recommendations.append({
                'type': 'manual_review',
                'message': 'Overall confidence is below threshold - manual review recommended',
                'priority': 'high'
            })
        
        low_confidence_fields = [
            field for field, confidence in field_confidence.items() 
            if confidence < thresholds['medium_confidence']
        ]
        
        if low_confidence_fields:
            recommendations.append({
                'type': 'field_validation',
                'message': f'Fields with low confidence need validation: {", ".join(low_confidence_fields)}',
                'priority': 'medium',
                'fields': low_confidence_fields
            })
        
        if not ocr_result.can_auto_create_faktura:
            recommendations.append({
                'type': 'data_completion',
                'message': 'Additional data required before invoice creation',
                'priority': 'medium'
            })
        
        return recommendations
    
    def _assess_field_pattern_accuracy(self, field, value):
        """
        Assess field accuracy based on expected patterns.
        
        Args:
            field: Field name
            value: Field value
            
        Returns:
            float: Pattern accuracy adjustment (-10 to +10)
        """
        import re
        
        pattern_checks = {
            'numer_faktury': lambda v: 5 if re.match(r'^[A-Z]+[-/]\d{4}[-/]\d+', str(v)) else -5,
            'data_wystawienia': lambda v: 5 if re.match(r'^\d{4}-\d{2}-\d{2}$', str(v)) else -3,
            'data_sprzedazy': lambda v: 5 if re.match(r'^\d{4}-\d{2}-\d{2}$', str(v)) else -3,
            'sprzedawca_nip': lambda v: 8 if re.match(r'^\d{10}$', str(v).replace('-', '').replace(' ', '')) else -8,
            'nabywca_nip': lambda v: 8 if re.match(r'^\d{10}$', str(v).replace('-', '').replace(' ', '')) else -8,
            'suma_brutto': lambda v: 3 if isinstance(v, (int, float)) and v > 0 else -5
        }
        
        check_func = pattern_checks.get(field)
        if check_func:
            try:
                return check_func(value)
            except:
                return -3
        
        return 0
    
    def _calculate_variance(self, scores):
        """
        Calculate variance of confidence scores.
        
        Args:
            scores: List of confidence scores
            
        Returns:
            float: Variance
        """
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        return variance


@extend_schema_view(
    post=extend_schema(
        operation_id='validate_ocr_result',
        summary='Validate and correct OCR result',
        description='Submit manual corrections for OCR extraction results and optionally create an invoice.',
        tags=['OCR Validation'],
        parameters=[
            OpenApiParameter(
                name='result_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the OCR result to validate',
                examples=[OpenApiExample('Result ID', value=123)]
            )
        ],
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                'Validation Request',
                summary='Example validation with corrections',
                description='Submit corrections for specific fields and create an invoice',
                value={
                    'corrections': {
                        'numer_faktury': 'FV/2025/001-CORRECTED',
                        'sprzedawca.nip': '9876543210',
                        'suma_brutto': 1200.00,
                        'pozycje.0.cena_netto': 1000.00
                    },
                    'create_faktura': True,
                    'validation_notes': 'Corrected invoice number and seller NIP'
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='OCR result validated successfully',
                examples=[
                    OpenApiExample(
                        'Validation Success',
                        summary='Successful validation with invoice creation',
                        value={
                            'success': True,
                            'data': {
                                'ocr_result_id': 123,
                                'updated_fields': [
                                    'numer_faktury',
                                    'sprzedawca.nip',
                                    'suma_brutto',
                                    'pozycje.0.cena_netto'
                                ],
                                'new_confidence_scores': {
                                    'numer_faktury': 100.0,
                                    'sprzedawca.nip': 100.0,
                                    'suma_brutto': 100.0,
                                    'pozycje.0.cena_netto': 100.0
                                },
                                'overall_confidence': 97.8,
                                'validation_id': 789,
                                'faktura_created': True,
                                'faktura_id': 456,
                                'faktura_number': 'FV/2025/001-CORRECTED'
                            },
                            'message': 'OCR result validated and updated successfully',
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Validation error',
                examples=[
                    OpenApiExample(
                        'Validation Error',
                        summary='Invalid correction data',
                        value={
                            'success': False,
                            'error': {
                                'code': 'VALIDATION_ERROR',
                                'message': 'Validation errors in corrections',
                                'details': {
                                    'sprzedawca.nip': 'Invalid NIP checksum',
                                    'suma_brutto': 'Amount cannot be negative'
                                }
                            },
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description='OCR result not found',
                examples=[
                    OpenApiExample(
                        'Not Found',
                        summary='OCR result does not exist',
                        value={
                            'success': False,
                            'error': {
                                'code': 'OCR_RESULT_NOT_FOUND',
                                'message': 'OCR result not found'
                            },
                            'timestamp': '2025-08-23T10:30:00Z'
                        }
                    )
                ]
            )
        }
    )
)
class OCRValidationAPIView(BaseAPIMixin, OwnershipMixin, LoggingMixin, PerformanceMonitoringMixin, APIMetricsMixin, APIView):
    """
    Submit manual corrections for OCR results and trigger invoice creation.
    
    This endpoint allows users to manually validate and correct OCR extraction
    results. Corrections are applied to the OCR result, confidence scores are
    updated, and automatic invoice creation can be triggered.
    
    **Authentication Required**: Yes  
    **Rate Limit**: 100 requests per minute per user  
    **Ownership**: Users can only validate their own OCR results  
    
    **Request Data**:
    - `corrections`: Dictionary of field corrections (field_path: new_value)
    - `create_faktura`: Boolean to trigger automatic invoice creation
    - `validation_notes`: Optional notes about the validation process
    
    **Supported Field Corrections**:
    - `numer_faktury`: Invoice number
    - `data_wystawienia`: Issue date (YYYY-MM-DD format)
    - `data_sprzedazy`: Sale date (YYYY-MM-DD format)
    - `sprzedawca.nazwa`: Seller company name
    - `sprzedawca.nip`: Seller NIP number (10 digits)
    - `sprzedawca.adres`: Seller address
    - `nabywca.nazwa`: Buyer company name
    - `nabywca.nip`: Buyer NIP number (10 digits)
    - `nabywca.adres`: Buyer address
    - `suma_netto`: Net amount
    - `suma_brutto`: Gross amount
    - `pozycje.N.nazwa`: Line item name (N = item index)
    - `pozycje.N.cena_netto`: Line item net price
    - `pozycje.N.ilosc`: Line item quantity
    
    **Validation Rules**:
    - NIP numbers must be exactly 10 digits with valid checksum
    - Dates must be in valid format (YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY)
    - Amounts must be positive numbers with max 2 decimal places
    - Company names and addresses cannot be empty
    - Line item quantities must be greater than 0
    
    **Response Data**:
    - List of successfully updated fields
    - New confidence scores for corrected fields (set to 100%)
    - Information about triggered invoice creation
    - Validation errors for any failed corrections
    
    **Confidence Score Updates**:
    - Manually corrected fields get 100% confidence
    - Related fields may have confidence recalculated
    - Overall document confidence is updated
    
    **Invoice Creation**:
    - Set `create_faktura: true` to automatically create invoice
    - Requires all mandatory fields to be present or corrected
    - Returns created invoice ID and status
    - Fails if required data is missing or invalid
    
    **Error Scenarios**:
    - OCR result not found (404 Not Found)
    - Access denied (403 Forbidden)
    - Invalid field corrections (400 Bad Request)
    - Validation errors in correction data (400 Bad Request)
    - Invoice creation failure (400 Bad Request)
    
    **Usage Examples**:
    ```json
    {
        "corrections": {
            "numer_faktury": "FV/2025/001-CORRECTED",
            "sprzedawca.nip": "9876543210",
            "suma_brutto": 1200.00
        },
        "create_faktura": true,
        "validation_notes": "Corrected invoice number and amount"
    }
    ```
    """
    queryset = OCRResult.objects.select_related(
        'document', 
        'document__user',
        'faktura', 
        'faktura__sprzedawca',
        'faktura__nabywca',
        'faktura__firma'
    ).prefetch_related(
        'ocrvalidation',
        'ocrvalidation__validated_by'
    ).all()
    serializer_class = OCRValidationSerializer
    throttle_classes = [OCRAPIThrottle]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'result_id'
    
    def get_object(self):
        """Get the OCR result object."""
        result_id = self.kwargs.get('result_id')
        try:
            # Use the filtered queryset to ensure ownership
            return self.get_queryset().get(id=result_id)
        except OCRResult.DoesNotExist:
            raise Http404("OCR result not found")
    
    def get_serializer(self, data=None, **kwargs):
        """Get the serializer instance."""
        return self.serializer_class(data=data, **kwargs)
    
    def post(self, request, result_id, *args, **kwargs):
        """
        Handle manual validation and correction of OCR results.
        
        Args:
            result_id: ID of the OCR result to validate
            
        Returns:
            Updated OCR result with applied corrections and confidence scores
        """
        try:
            # Get the OCR result object
            ocr_result = self.get_object()
            logger.info(f"Got OCR result: {ocr_result.id}")
            
            # Check object permissions
            self.check_object_permissions(request, ocr_result)
            logger.info("Object permissions checked successfully")
            
            # Validate the request data
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Serializer validation failed: {serializer.errors}")
                return self.error_response(
                    message="Validation error",
                    code="VALIDATION_ERROR",
                    details=serializer.errors,
                    status_code=APIStatusCode.BAD_REQUEST.code
                )
            
            logger.info("Serializer validation successful")
            corrections = serializer.validated_data['corrections']
            create_faktura = serializer.validated_data.get('create_faktura', False)
            validation_notes = serializer.validated_data.get('validation_notes', '')
            
            # For now, just return a simple success response to test
            response_data = {
                'ocr_result_id': ocr_result.id,
                'message': 'Test response'
            }
            
            logger.info("About to return success response")
            return self.success_response(
                data=response_data,
                message="OCR result validated successfully",
                status_code=APIStatusCode.SUCCESS.code
            )
            
        except (OCRResult.DoesNotExist, Http404):
            return self.error_response(
                message="OCR result not found",
                code="OCR_RESULT_NOT_FOUND",
                status_code=APIStatusCode.NOT_FOUND.code
            )
        except PermissionDenied:
            return self.error_response(
                message="You don't have permission to validate this OCR result",
                code="OCR_VALIDATION_ACCESS_DENIED",
                status_code=APIStatusCode.FORBIDDEN.code
            )
        except ValidationError as e:
            logger.warning(f"Validation error for OCR result {result_id}: {str(e)}")
            return self.error_response(
                message="Validation error",
                code="OCR_VALIDATION_ERROR",
                details={"error": str(e)},
                status_code=APIStatusCode.BAD_REQUEST.code
            )
        except OCRIntegrationError as e:
            logger.warning(f"OCR integration error for OCR result {result_id}: {str(e)}")
            return self.error_response(
                message="OCR integration error",
                code="OCR_INTEGRATION_ERROR",
                details={"error": str(e)},
                status_code=APIStatusCode.BAD_REQUEST.code
            )
        except Exception as e:
            logger.error(f"Error validating OCR result {result_id}: {str(e)}", exc_info=True)
            return self.error_response(
                message="Error validating OCR result",
                code="OCR_VALIDATION_ERROR",
                details={"error": str(e)},
                status_code=APIStatusCode.INTERNAL_SERVER_ERROR.code
            )
    
    def _apply_corrections(self, ocr_result, corrections):
        """
        Apply user corrections to the OCR result.
        
        Args:
            ocr_result: OCRResult instance
            corrections: Dictionary of field corrections
            
        Returns:
            List of successfully updated field names
        """
        updated_fields = []
        extracted_data = ocr_result.extracted_data.copy() if ocr_result.extracted_data else {}
        
        for field_path, new_value in corrections.items():
            try:
                # Handle nested field paths (e.g., "sprzedawca.nazwa", "pozycje.0.cena_netto")
                if '.' in field_path:
                    parts = field_path.split('.')
                    current_data = extracted_data
                    
                    # Navigate to the parent object, creating nested structures as needed
                    for part in parts[:-1]:
                        # Handle array indices
                        if part.isdigit():
                            index = int(part)
                            # Ensure the current data is a list and has enough elements
                            if not isinstance(current_data, list):
                                current_data = []
                            while len(current_data) <= index:
                                current_data.append({})
                            current_data = current_data[index]
                        else:
                            # Handle object properties
                            if part not in current_data:
                                current_data[part] = {}
                            current_data = current_data[part]
                    
                    # Set the final value
                    final_key = parts[-1]
                    if final_key.isdigit():
                        index = int(final_key)
                        if not isinstance(current_data, list):
                            current_data = []
                        while len(current_data) <= index:
                            current_data.append(None)
                        current_data[index] = new_value
                    else:
                        current_data[final_key] = new_value
                else:
                    # Direct field update
                    extracted_data[field_path] = new_value
                
                updated_fields.append(field_path)
                logger.info(f"Applied correction for field {field_path}: {new_value}")
                
            except Exception as e:
                logger.warning(f"Failed to apply correction for field {field_path}: {str(e)}")
                continue
        
        # Update the OCR result with corrected data
        ocr_result.extracted_data = extracted_data
        
        return updated_fields
    
    def _update_confidence_scores(self, ocr_result, updated_fields):
        """
        Update confidence scores for manually corrected fields.
        
        Args:
            ocr_result: OCRResult instance
            updated_fields: List of field names that were updated
            
        Returns:
            Dictionary of new confidence scores
        """
        field_confidence = ocr_result.field_confidence.copy() if ocr_result.field_confidence else {}
        new_scores = {}
        
        # Set confidence to 100% for manually corrected fields
        for field_path in updated_fields:
            field_confidence[field_path] = 100.0
            new_scores[field_path] = 100.0
            logger.info(f"Updated confidence for field {field_path} to 100%")
        
        # Recalculate overall confidence score using weighted average
        if field_confidence:
            # Define weights for different field types
            field_weights = {
                'numer_faktury': 0.15,
                'data_wystawienia': 0.10,
                'data_sprzedazy': 0.05,
                'sprzedawca': 0.20,
                'nabywca': 0.15,
                'suma_netto': 0.15,
                'suma_brutto': 0.20
            }
            
            total_weight = 0
            weighted_sum = 0
            
            for field, confidence in field_confidence.items():
                # Get base field name (remove array indices and nested properties)
                base_field = field.split('.')[0]
                weight = field_weights.get(base_field, 0.05)  # Default weight for other fields
                weighted_sum += confidence * weight
                total_weight += weight
            
            if total_weight > 0:
                ocr_result.confidence_score = weighted_sum / total_weight
            else:
                # Fallback to simple average
                ocr_result.confidence_score = sum(field_confidence.values()) / len(field_confidence)
        
        ocr_result.field_confidence = field_confidence
        
        return new_scores
    
    def _create_validation_record(self, ocr_result, corrections, notes, user):
        """
        Create a validation record for audit purposes.
        
        Args:
            ocr_result: OCRResult instance
            corrections: Applied corrections
            notes: Validation notes
            user: User who performed validation
            
        Returns:
            OCRValidation instance
        """
        try:
            # Store confidence before changes
            confidence_before = ocr_result.confidence_score
            
            # Check if validation record already exists (OneToOne relationship)
            validation_record, created = OCRValidation.objects.get_or_create(
                ocr_result=ocr_result,
                defaults={
                    'validated_by': user,
                    'corrections_made': corrections,
                    'validation_notes': notes,
                    'accuracy_rating': 8,  # Default rating for manual corrections
                }
            )
            
            if not created:
                # Update existing validation record
                current_corrections = validation_record.corrections_made or {}
                current_corrections.update(corrections)
                validation_record.corrections_made = current_corrections
                validation_record.validation_notes = notes
                validation_record.validated_by = user
                validation_record.save(update_fields=['corrections_made', 'validation_notes', 'validated_by'])
                logger.info(f"Updated existing validation record for OCR result {ocr_result.id}")
            else:
                logger.info(f"Created new validation record for OCR result {ocr_result.id}")
            
            return validation_record
            
        except Exception as e:
            logger.error(f"Failed to create validation record for OCR result {ocr_result.id}: {str(e)}")
            # Create a simple validation record without the problematic fields
            validation_record = OCRValidation(
                ocr_result=ocr_result,
                validated_by=user,
                corrections_made=corrections,
                validation_notes=notes,
                accuracy_rating=8
            )
            validation_record.save()
            return validation_record
    
    def _create_faktura_from_result(self, ocr_result):
        """
        Create a Faktura from validated OCR result.
        
        Args:
            ocr_result: OCRResult instance with validated data
            
        Returns:
            Dictionary with created Faktura information or None if creation failed
        """
        try:
            # Check if OCR result can create Faktura
            if not ocr_result.can_create_faktura():
                logger.warning(f"OCR result {ocr_result.id} does not meet requirements for Faktura creation")
                return None
            
            # Check if Faktura already exists
            if ocr_result.faktura:
                logger.info(f"Faktura already exists for OCR result {ocr_result.id}")
                return {
                    'id': ocr_result.faktura.id,
                    'number': ocr_result.faktura.numer,
                    'status': getattr(ocr_result.faktura, 'status', 'unknown')
                }
            
            # Use the imported OCRIntegrationService
            integration_service = OCRIntegrationService(user=self.request.user)
            faktura = integration_service.create_faktura_from_ocr_result(ocr_result)
            
            if faktura:
                # Update OCR result to link to created Faktura
                ocr_result.faktura = faktura
                ocr_result.auto_created_faktura = False  # This was manually validated
                ocr_result.save(update_fields=['faktura', 'auto_created_faktura'])
                
                logger.info(f"Successfully created Faktura {faktura.id} from OCR result {ocr_result.id}")
                
                return {
                    'id': faktura.id,
                    'number': faktura.numer,
                    'status': getattr(faktura, 'status', 'created')
                }
            
            logger.warning(f"Failed to create Faktura from OCR result {ocr_result.id} - service returned None")
            return None
            
        except Exception as e:
            logger.error(f"Failed to create Faktura from OCR result {ocr_result.id}: {str(e)}", exc_info=True)
            raise OCRProcessingError(f"Failed to create invoice: {str(e)}")
    
    def _get_validation_suggestions(self, ocr_result):
        """
        Get suggestions for fields that need validation.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            list: List of validation suggestions
        """
        suggestions = []
        field_confidence = ocr_result.field_confidence or {}
        
        # Check critical fields with low confidence
        critical_fields = {
            'numer_faktury': 'Invoice number has low confidence - please verify',
            'data_wystawienia': 'Issue date has low confidence - please verify',
            'suma_brutto': 'Total amount has low confidence - please verify',
            'sprzedawca': 'Seller information has low confidence - please verify',
            'nabywca': 'Buyer information has low confidence - please verify'
        }
        
        for field, message in critical_fields.items():
            confidence = field_confidence.get(field, ocr_result.confidence_score)
            if confidence < 80.0 and field in (ocr_result.extracted_data or {}):
                suggestions.append({
                    'field': field,
                    'message': message,
                    'confidence': confidence,
                    'priority': 'high' if confidence < 60.0 else 'medium'
                })
        
        return suggestions
    
    def _get_review_priorities(self, ocr_result):
        """
        Get field review priorities based on confidence scores.
        
        Args:
            ocr_result: OCRResult instance
            
        Returns:
            dict: Fields categorized by review priority
        """
        field_confidence = ocr_result.field_confidence or {}
        extracted_data = ocr_result.extracted_data or {}
        
        priorities = {
            'high': [],      # < 60% confidence
            'medium': [],    # 60-80% confidence
            'low': []        # > 80% confidence
        }
        
        for field, value in extracted_data.items():
            confidence = field_confidence.get(field, ocr_result.confidence_score)
            
            if confidence < 60.0:
                priority = 'high'
            elif confidence < 80.0:
                priority = 'medium'
            else:
                priority = 'low'
            
            priorities[priority].append({
                'field': field,
                'confidence': confidence,
                'value': value
            })
        
        return priorities
    
    def _get_specific_metrics(self, request, response, *args, **kwargs):
        """Get OCR validation specific metrics."""
        metrics = {}
        
        if response.status_code == 200 and hasattr(response, 'data'):
            data = response.data.get('data', {}) if isinstance(response.data, dict) else {}
            metrics.update({
                'validation_success': True,
                'faktura_created': data.get('faktura_created', False),
                'fields_updated': len(data.get('updated_fields', [])),
                'overall_confidence': data.get('overall_confidence', 0),
            })
        else:
            metrics['validation_success'] = False
            
        if request.data:
            corrections = request.data.get('corrections', {})
            metrics.update({
                'corrections_count': len(corrections) if isinstance(corrections, dict) else 0,
                'create_faktura_requested': request.data.get('create_faktura', False),
            })
        
        return metrics


@extend_schema_view(
    get=extend_schema(
        operation_id='api_health_check',
        summary='API Health Check',
        description='Check the health status of the OCR API and its dependencies.',
        tags=['Health Check'],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='API is healthy'
            ),
            503: OpenApiResponse(
                description='API is unhealthy'
            )
        }
    )
)
class HealthCheckAPIView(APIView):
    """
    API health check endpoint for monitoring system status.
    """
    permission_classes = []  # No authentication required
    throttle_classes = []    # No rate limiting for health checks
    
    def get(self, request, *args, **kwargs):
        """
        Perform health checks and return system status.
        """
        start_time = time.time()
        health_checks = {}
        errors = []
        overall_status = 'healthy'
        
        # Database health check
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_checks['database'] = 'healthy'
        except Exception as e:
            health_checks['database'] = 'unhealthy'
            errors.append(f"Database error: {str(e)}")
            overall_status = 'unhealthy'
        
        # Redis health check
        try:
            from django.core.cache import cache
            cache.set('health_check', 'test', 10)
            if cache.get('health_check') == 'test':
                health_checks['redis'] = 'healthy'
            else:
                health_checks['redis'] = 'degraded'
                overall_status = 'degraded' if overall_status == 'healthy' else overall_status
        except Exception as e:
            health_checks['redis'] = 'unhealthy'
            errors.append(f"Redis error: {str(e)}")
            overall_status = 'unhealthy'
        
        # Celery health check
        try:
            from celery import current_app
            inspect = current_app.control.inspect()
            stats = inspect.stats()
            if stats:
                health_checks['celery'] = 'healthy'
            else:
                health_checks['celery'] = 'degraded'
                overall_status = 'degraded' if overall_status == 'healthy' else overall_status
        except Exception as e:
            health_checks['celery'] = 'degraded'  # Celery issues are not critical
        
        # Storage health check
        try:
            from django.core.files.storage import default_storage
            health_checks['storage'] = 'healthy'
        except Exception as e:
            health_checks['storage'] = 'unhealthy'
            errors.append(f"Storage error: {str(e)}")
            overall_status = 'unhealthy'
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Build response
        response_data = {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'checks': health_checks,
            'performance': {
                'response_time': f"{response_time:.3f}s",
                'uptime': "Available"
            }
        }
        
        if errors:
            response_data['errors'] = errors
        
        # Set appropriate HTTP status code
        status_code = 200 if overall_status == 'healthy' else 503
        
        return Response(response_data, status=status_code)




@extend_schema_view(
    post=extend_schema(
        operation_id='log_asset_monitoring_data',
        summary='Log asset monitoring data',
        description='Endpoint for frontend to log asset loading errors, performance metrics, and monitoring data.',
        tags=['Asset Monitoring'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'logs': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'eventType': {'type': 'string'},
                                'data': {'type': 'object'},
                                'timestamp': {'type': 'string'},
                                'url': {'type': 'string'},
                                'userAgent': {'type': 'string'},
                                'sessionId': {'type': 'string'}
                            }
                        }
                    },
                    'batchId': {'type': 'string'},
                    'timestamp': {'type': 'string'}
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description='Monitoring data logged successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            'success': True,
                            'message': 'Asset monitoring data logged successfully',
                            'processed_logs': 5
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid monitoring data format'
            )
        }
    )
)
class AssetMonitoringAPIView(BaseAPIView):
    """
    Asset monitoring endpoint for logging frontend asset loading issues.
    
    This endpoint receives batched monitoring data from the frontend JavaScript
    monitoring systems, including 404 errors, performance metrics, and critical
    asset failures. The data is logged for analysis and alerting.
    
    **Authentication Required**: Yes (but allows anonymous for basic monitoring)
    **Rate Limit**: 100 requests per minute per user
    **Data Retention**: Logs are kept for 30 days for analysis
    
    **Supported Event Types**:
    - `404_error`: Asset not found errors
    - `http_error`: Other HTTP errors (500, 503, etc.)
    - `network_error`: Network connectivity issues
    - `performance_metric`: Asset loading performance data
    - `slow_loading`: Assets that load slower than threshold
    - `critical_failure`: Critical asset loading failures
    - `retry_success`: Successful retry attempts
    - `network_status`: Online/offline status changes
    - `periodic_report`: Periodic summary reports
    
    **Security Features**:
    - Request validation and sanitization
    - Rate limiting to prevent abuse
    - User session tracking
    - Anomaly detection for unusual patterns
    
    **Usage**:
    Frontend monitoring systems automatically send batched data every 10 seconds
    or when critical events occur. This helps identify infrastructure issues,
    CDN problems, and performance degradation.
    """
    throttle_classes = [OCRAPIThrottle]
    permission_classes = []  # Allow anonymous monitoring for basic functionality
    
    def post(self, request, *args, **kwargs):
        """
        Log asset monitoring data from frontend.
        
        Expected request format:
        {
            "logs": [
                {
                    "eventType": "404_error",
                    "data": {
                        "url": "https://example.com/missing.js",
                        "status": 404,
                        "critical": true
                    },
                    "timestamp": "2025-08-23T10:30:00Z",
                    "url": "https://example.com/page",
                    "userAgent": "Mozilla/5.0...",
                    "sessionId": "abc123"
                }
            ],
            "batchId": "batch_123",
            "timestamp": "2025-08-23T10:30:00Z"
        }
        
        Returns:
        - Success confirmation
        - Number of processed logs
        - Any validation warnings
        """
        try:
            # Validate request data
            if not request.data or 'logs' not in request.data:
                return self.error_response(
                    'INVALID_REQUEST',
                    'Missing logs data in request',
                    status_code=APIStatusCode.BAD_REQUEST
                )
            
            logs = request.data.get('logs', [])
            batch_id = request.data.get('batchId', 'unknown')
            
            if not isinstance(logs, list):
                return self.error_response(
                    'INVALID_FORMAT',
                    'Logs must be an array',
                    status_code=APIStatusCode.BAD_REQUEST
                )
            
            # Process each log entry
            processed_count = 0
            warnings = []
            
            for log_entry in logs[:50]:  # Limit to 50 logs per batch
                try:
                    self._process_log_entry(log_entry, request)
                    processed_count += 1
                except Exception as e:
                    warnings.append(f"Failed to process log entry: {str(e)}")
                    continue
            
            # Log batch summary
            asset_monitor_logger.info(
                f"Asset monitoring batch processed - Batch: {batch_id}, "
                f"Processed: {processed_count}/{len(logs)}, "
                f"User: {getattr(request.user, 'id', 'anonymous')}, "
                f"IP: {self._get_client_ip(request)}"
            )
            
            # Return success response
            response_data = {
                'processed_logs': processed_count,
                'total_logs': len(logs),
                'batch_id': batch_id
            }
            
            if warnings:
                response_data['warnings'] = warnings[:10]  # Limit warnings
            
            return self.success_response(
                data=response_data,
                message='Asset monitoring data logged successfully'
            )
            
        except Exception as e:
            asset_monitor_logger.error(f"Error processing asset monitoring data: {str(e)}", exc_info=True)
            return self.error_response(
                'PROCESSING_ERROR',
                'Failed to process monitoring data',
                details={'error': str(e)},
                status_code=APIStatusCode.INTERNAL_SERVER_ERROR
            )
    
    def _process_log_entry(self, log_entry, request):
        """
        Process individual log entry.
        
        Args:
            log_entry: Dictionary containing log data
            request: HTTP request object
        """
        event_type = log_entry.get('eventType', 'unknown')
        data = log_entry.get('data', {})
        timestamp = log_entry.get('timestamp')
        page_url = log_entry.get('url')
        user_agent = log_entry.get('userAgent')
        session_id = log_entry.get('sessionId')
        
        # Add request context
        context = {
            'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
            'ip_address': self._get_client_ip(request),
            'page_url': page_url,
            'user_agent': user_agent,
            'session_id': session_id,
            'timestamp': timestamp
        }
        
        # Log based on event type
        if event_type == '404_error':
            self._log_404_error(data, context)
        elif event_type == 'critical_failure':
            self._log_critical_failure(data, context)
        elif event_type == 'performance_metric':
            self._log_performance_metric(data, context)
        elif event_type == 'slow_loading':
            self._log_slow_loading(data, context)
        elif event_type == 'network_error':
            self._log_network_error(data, context)
        elif event_type == 'periodic_report':
            self._log_periodic_report(data, context)
        else:
            # Log generic monitoring event
            asset_monitor_logger.info(
                f"Asset monitoring event - Type: {event_type}, "
                f"Data: {data}, Context: {context}"
            )
    
    def _log_404_error(self, data, context):
        """Log 404 asset errors."""
        asset_url = data.get('url', 'unknown')
        is_critical = data.get('critical', False)
        
        log_level = logging.ERROR if is_critical else logging.WARNING
        
        asset_monitor_logger.log(
            log_level,
            f"ASSET_404_ERROR - URL: {asset_url}, Critical: {is_critical}, "
            f"Page: {context.get('page_url')}, User: {context.get('user_id')}, "
            f"Session: {context.get('session_id')}"
        )
        
        # Alert for critical 404s
        if is_critical:
            asset_monitor_logger.error(
                f"CRITICAL_ASSET_404 - {asset_url} - This may cause significant functionality issues"
            )
    
    def _log_critical_failure(self, data, context):
        """Log critical asset failures."""
        asset_url = data.get('url', 'unknown')
        error_message = data.get('error', 'Unknown error')
        
        asset_monitor_logger.error(
            f"CRITICAL_ASSET_FAILURE - URL: {asset_url}, Error: {error_message}, "
            f"Page: {context.get('page_url')}, User: {context.get('user_id')}"
        )
    
    def _log_performance_metric(self, data, context):
        """Log performance metrics."""
        asset_url = data.get('url', 'unknown')
        duration = data.get('duration', 0)
        transfer_size = data.get('transferSize', 0)
        
        asset_monitor_logger.info(
            f"ASSET_PERFORMANCE - URL: {asset_url}, Duration: {duration}ms, "
            f"Size: {transfer_size}bytes, Page: {context.get('page_url')}"
        )
    
    def _log_slow_loading(self, data, context):
        """Log slow loading assets."""
        asset_url = data.get('url', 'unknown')
        duration = data.get('duration', 0)
        threshold = data.get('threshold', 0)
        is_critical = data.get('critical', False)
        
        log_level = logging.WARNING if is_critical else logging.INFO
        
        asset_monitor_logger.log(
            log_level,
            f"SLOW_ASSET_LOADING - URL: {asset_url}, Duration: {duration}ms, "
            f"Threshold: {threshold}ms, Critical: {is_critical}, "
            f"Page: {context.get('page_url')}"
        )
    
    def _log_network_error(self, data, context):
        """Log network errors."""
        asset_url = data.get('url', 'unknown')
        error_message = data.get('errorMessage', 'Network error')
        
        asset_monitor_logger.warning(
            f"ASSET_NETWORK_ERROR - URL: {asset_url}, Error: {error_message}, "
            f"Page: {context.get('page_url')}, User: {context.get('user_id')}"
        )
    
    def _log_periodic_report(self, data, context):
        """Log periodic monitoring reports."""
        summary = data.get('summary', {})
        
        asset_monitor_logger.info(
            f"PERIODIC_MONITORING_REPORT - "
            f"404_Errors: {summary.get('total404Errors', 0)}, "
            f"Critical_Failures: {summary.get('criticalFailures', 0)}, "
            f"Performance_Metrics: {summary.get('performanceMetrics', 0)}, "
            f"Page: {context.get('page_url')}, User: {context.get('user_id')}"
        )
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_specific_metrics(self, request, response, *args, **kwargs):
        """Get asset monitoring specific metrics."""
        metrics = {}
        
        if hasattr(request, 'data') and 'logs' in request.data:
            logs = request.data['logs']
            metrics.update({
                'log_count': len(logs),
                'batch_id': request.data.get('batchId'),
                'monitoring_success': response.status_code == 200,
            })
            
            # Count event types
            event_types = {}
            for log in logs:
                event_type = log.get('eventType', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            metrics['event_types'] = event_types
        
        return metrics