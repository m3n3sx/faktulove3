"""
URL configuration for the OCR REST API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from . import views
from . import performance_views
from .authentication import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    logout_view,
    verify_token_view,
    csrf_token_view
)

app_name = 'api'

# Authentication URL patterns
auth_patterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', verify_token_view, name='token_verify'),
    path('csrf/', csrf_token_view, name='csrf_token'),
    path('logout/', logout_view, name='logout'),
]

# API v1 URL patterns
v1_patterns = [
    # Authentication endpoints
    path('auth/', include((auth_patterns, 'auth'), namespace='auth')),
    
    # OCR endpoints - will be implemented in subsequent tasks
    path('ocr/upload/', views.OCRUploadAPIView.as_view(), name='ocr-upload'),
    path('ocr/status/<str:task_id>/', views.OCRStatusAPIView.as_view(), name='ocr-status'),
    path('ocr/results/', views.OCRResultsListAPIView.as_view(), name='ocr-results'),
    path('ocr/result/<int:result_id>/', views.OCRResultDetailAPIView.as_view(), name='ocr-result-detail'),
    path('ocr/validate/<int:result_id>/', views.OCRValidationAPIView.as_view(), name='ocr-validate'),
    
    # Performance monitoring endpoints
    path('performance-metrics/', performance_views.collect_performance_metrics, name='performance-metrics'),
    path('performance-dashboard/', performance_views.get_performance_dashboard, name='performance-dashboard'),
    path('performance-metric/', performance_views.collect_single_metric, name='single-metric'),
]

urlpatterns = [
    # API v1 endpoints
    path('v1/', include((v1_patterns, 'v1'), namespace='v1')),
    
    # Documentation endpoints
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]