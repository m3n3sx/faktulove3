"""
Performance monitoring API views for design system metrics collection
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
import json
import logging

# Import models from the main models module to avoid conflicts
from ..models import PerformanceMetric, ComponentPerformanceMetric, AccessibilityMetric

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([])  # Allow anonymous for now, can be restricted later
def collect_performance_metrics(request):
    """
    Collect performance metrics from frontend design system monitoring
    """
    try:
        data = request.data
        
        # Extract user info if available
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key
        
        # Create main performance metric record
        performance_metric = PerformanceMetric.objects.create(
            user=user,
            session_id=session_id,
            url=data.get('webVitals', {}).get('url', ''),
            user_agent=data.get('webVitals', {}).get('userAgent', ''),
            lcp=data.get('webVitals', {}).get('metrics', {}).get('lcp'),
            fid=data.get('webVitals', {}).get('metrics', {}).get('fid'),
            cls=data.get('webVitals', {}).get('metrics', {}).get('cls'),
            fcp=data.get('webVitals', {}).get('metrics', {}).get('fcp'),
            ttfb=data.get('webVitals', {}).get('metrics', {}).get('ttfb'),
            component_render_time=data.get('webVitals', {}).get('designSystemMetrics', {}).get('componentRenderTime'),
            bundle_size=data.get('bundle', {}).get('totalSize'),
            css_load_time=data.get('webVitals', {}).get('designSystemMetrics', {}).get('cssLoadTime'),
            theme_load_time=data.get('webVitals', {}).get('designSystemMetrics', {}).get('themeLoadTime'),
            raw_data=data
        )
        
        # Store component performance data
        components_data = data.get('components', [])
        for component_data in components_data:
            ComponentPerformanceMetric.objects.create(
                performance_metric=performance_metric,
                component_name=component_data.get('name', ''),
                render_count=component_data.get('renderCount', 0),
                total_render_time=component_data.get('totalRenderTime', 0),
                average_render_time=component_data.get('averageRenderTime', 0),
                max_render_time=component_data.get('maxRenderTime', 0),
                min_render_time=component_data.get('minRenderTime', 0),
                props_changes=component_data.get('propsChanges', 0),
                memory_usage=component_data.get('memoryUsage', 0)
            )
        
        # Store accessibility metrics
        accessibility_data = data.get('userExperience', {}).get('accessibility', {})
        if accessibility_data:
            AccessibilityMetric.objects.create(
                performance_metric=performance_metric,
                keyboard_navigation_usage=accessibility_data.get('keyboardNavigation', {}).get('usage', 0),
                keyboard_navigation_errors=accessibility_data.get('keyboardNavigation', {}).get('errors', 0),
                screen_reader_detected=accessibility_data.get('screenReader', {}).get('detected', False),
                aria_errors=accessibility_data.get('screenReader', {}).get('ariaErrors', 0),
                missing_labels=accessibility_data.get('screenReader', {}).get('missingLabels', 0),
                color_contrast_violations=accessibility_data.get('colorContrast', {}).get('violations', 0),
                focus_trap_errors=accessibility_data.get('focusManagement', {}).get('trapErrors', 0),
                lost_focus_count=accessibility_data.get('focusManagement', {}).get('lostFocus', 0)
            )
        
        logger.info(f"Performance metrics collected for session {session_id}")
        
        return Response({
            'status': 'success',
            'message': 'Performance metrics collected successfully',
            'metric_id': performance_metric.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error collecting performance metrics: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Failed to collect performance metrics',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_performance_dashboard(request):
    """
    Get performance dashboard data for admin users
    """
    try:
        # Get recent metrics (last 24 hours)
        from datetime import timedelta
        since = timezone.now() - timedelta(hours=24)
        
        metrics = PerformanceMetric.objects.filter(timestamp__gte=since)
        
        # Calculate averages
        avg_metrics = metrics.aggregate(
            avg_lcp=models.Avg('lcp'),
            avg_fid=models.Avg('fid'),
            avg_cls=models.Avg('cls'),
            avg_fcp=models.Avg('fcp'),
            avg_ttfb=models.Avg('ttfb'),
            avg_bundle_size=models.Avg('bundle_size'),
            avg_component_render_time=models.Avg('component_render_time')
        )
        
        # Get component performance data
        component_metrics = ComponentPerformanceMetric.objects.filter(
            performance_metric__timestamp__gte=since
        ).values('component_name').annotate(
            avg_render_time=models.Avg('average_render_time'),
            total_renders=models.Sum('render_count'),
            max_render_time=models.Max('max_render_time')
        ).order_by('-avg_render_time')[:10]
        
        # Get accessibility issues
        accessibility_issues = AccessibilityMetric.objects.filter(
            performance_metric__timestamp__gte=since
        ).aggregate(
            total_missing_labels=models.Sum('missing_labels'),
            total_contrast_violations=models.Sum('color_contrast_violations'),
            total_keyboard_errors=models.Sum('keyboard_navigation_errors'),
            screen_reader_usage=models.Count('id', filter=models.Q(screen_reader_detected=True))
        )
        
        # Generate recommendations
        recommendations = []
        
        if avg_metrics['avg_lcp'] and avg_metrics['avg_lcp'] > 2500:
            recommendations.append('LCP is slow - optimize largest contentful paint')
        
        if avg_metrics['avg_bundle_size'] and avg_metrics['avg_bundle_size'] > 500000:
            recommendations.append('Bundle size is large - implement code splitting')
        
        if accessibility_issues['total_missing_labels'] > 0:
            recommendations.append(f"{accessibility_issues['total_missing_labels']} missing accessibility labels")
        
        if accessibility_issues['total_contrast_violations'] > 0:
            recommendations.append(f"{accessibility_issues['total_contrast_violations']} color contrast violations")
        
        return Response({
            'status': 'success',
            'data': {
                'webVitals': avg_metrics,
                'componentPerformance': list(component_metrics),
                'accessibilityIssues': accessibility_issues,
                'recommendations': recommendations,
                'totalSessions': metrics.count(),
                'timeRange': '24 hours'
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating performance dashboard: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Failed to generate performance dashboard',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def collect_single_metric(request):
    """
    Collect a single performance metric (for real-time reporting)
    """
    try:
        data = request.data
        metric_name = data.get('metric')
        value = data.get('value')
        timestamp = data.get('timestamp', timezone.now().timestamp())
        url = data.get('url', '')
        
        # Store in a simple format for real-time metrics
        logger.info(f"Single metric collected: {metric_name}={value} at {url}")
        
        # You could store this in Redis for real-time dashboards
        # or aggregate into the main PerformanceMetric model
        
        return Response({
            'status': 'success',
            'message': f'Metric {metric_name} collected'
        })
        
    except Exception as e:
        logger.error(f"Error collecting single metric: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Failed to collect metric'
        }, status=status.HTTP_400_BAD_REQUEST)