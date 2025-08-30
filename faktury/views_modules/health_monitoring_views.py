"""
Health monitoring views for system administration.

Provides views for system health dashboard, health history API,
and automated alerting functionality.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings

from faktury.services.health_check_service import HealthCheckService
from faktury.models import SystemHealthMetric

logger = logging.getLogger(__name__)


def is_superuser(user):
    """Check if user is superuser."""
    return user.is_authenticated and user.is_superuser


@method_decorator([staff_member_required, user_passes_test(is_superuser)], name='dispatch')
class SystemHealthDashboardView(View):
    """System health dashboard for administrators."""
    
    def __init__(self):
        super().__init__()
        self.health_service = HealthCheckService()
    
    def get(self, request):
        """Display system health dashboard."""
        try:
            # Generate comprehensive health report
            health_report = self.health_service.generate_health_report()
            
            # Get performance metrics
            performance_metrics = self.health_service.get_performance_metrics()
            
            context = {
                'health_report': health_report,
                'performance_metrics': performance_metrics,
                'title': 'System Health Dashboard'
            }
            
            return render(request, 'admin/system_health_dashboard.html', context)
            
        except Exception as e:
            logger.error(f"Failed to load health dashboard: {e}")
            context = {
                'error': 'Failed to load health dashboard',
                'title': 'System Health Dashboard'
            }
            return render(request, 'admin/system_health_dashboard.html', context)


@staff_member_required
@user_passes_test(is_superuser)
@require_http_methods(["GET"])
def health_history_api(request):
    """API endpoint for health history data."""
    try:
        # Get query parameters
        component = request.GET.get('component')
        hours = int(request.GET.get('hours', 24))
        
        health_service = HealthCheckService()
        history_data = health_service.get_health_history(component, hours)
        
        # Format data for Chart.js
        labels = []
        response_times = []
        error_counts = []
        
        for record in reversed(history_data[-20:]):  # Last 20 records
            timestamp = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
            labels.append(timestamp.strftime('%H:%M'))
            response_times.append(record['response_time'])
            error_counts.append(record['error_count'])
        
        chart_data = {
            'labels': labels,
            'response_times': response_times,
            'error_counts': error_counts
        }
        
        return JsonResponse(chart_data)
        
    except Exception as e:
        logger.error(f"Failed to get health history: {e}")
        return JsonResponse({'error': 'Failed to get health history'}, status=500)


@staff_member_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def trigger_health_check(request):
    """Manually trigger a health check."""
    try:
        health_service = HealthCheckService()
        health_report = health_service.generate_health_report()
        
        return JsonResponse({
            'success': True,
            'report': health_report,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to trigger health check: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@user_passes_test(is_superuser)
@require_http_methods(["GET"])
def component_details_api(request, component_name):
    """Get detailed information about a specific component."""
    try:
        health_service = HealthCheckService()
        
        # Get component-specific health check
        if component_name == 'database':
            component_data = health_service.check_database_health()
        elif component_name == 'ocr_services':
            component_data = health_service.check_ocr_services()
        elif component_name == 'static_assets':
            component_data = health_service.check_static_assets()
        elif component_name == 'system_resources':
            component_data = health_service.check_system_resources()
        elif component_name == 'cache':
            component_data = health_service.check_cache_health()
        else:
            return JsonResponse({'error': 'Unknown component'}, status=404)
        
        # Get historical data for this component
        history = health_service.get_health_history(component_name, 24)
        
        return JsonResponse({
            'component': component_name,
            'current_status': component_data,
            'history': history[:10]  # Last 10 records
        })
        
    except Exception as e:
        logger.error(f"Failed to get component details for {component_name}: {e}")
        return JsonResponse({'error': 'Failed to get component details'}, status=500)


class HealthAlertingService:
    """Service for automated health alerting."""
    
    def __init__(self):
        self.health_service = HealthCheckService()
        self.alert_thresholds = {
            'error_components': 1,  # Alert if any component has errors
            'warning_components': 3,  # Alert if 3+ components have warnings
            'response_time_ms': 1000,  # Alert if response time > 1s
            'error_rate_percent': 5,  # Alert if error rate > 5%
        }
    
    def check_and_send_alerts(self) -> Dict[str, Any]:
        """Check system health and send alerts if needed."""
        try:
            health_report = self.health_service.generate_health_report()
            performance_metrics = self.health_service.get_performance_metrics()
            
            alerts_sent = []
            
            # Check for error components
            if health_report['summary']['error_components'] >= self.alert_thresholds['error_components']:
                alert_message = self._create_error_alert(health_report)
                if self._send_alert('Critical System Error', alert_message):
                    alerts_sent.append('critical_error')
            
            # Check for too many warnings
            elif health_report['summary']['warning_components'] >= self.alert_thresholds['warning_components']:
                alert_message = self._create_warning_alert(health_report)
                if self._send_alert('System Warning', alert_message):
                    alerts_sent.append('multiple_warnings')
            
            # Check error rate
            if performance_metrics.get('error_rate_percent', 0) > self.alert_thresholds['error_rate_percent']:
                alert_message = self._create_performance_alert(performance_metrics)
                if self._send_alert('High Error Rate Alert', alert_message):
                    alerts_sent.append('high_error_rate')
            
            return {
                'alerts_sent': alerts_sent,
                'health_status': health_report['overall_status'],
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to check and send alerts: {e}")
            return {'error': str(e)}
    
    def _create_error_alert(self, health_report: Dict[str, Any]) -> str:
        """Create alert message for critical errors."""
        error_components = []
        
        for component_name, component_data in health_report['components'].items():
            if component_data['status'] == 'error':
                errors = ', '.join(component_data.get('errors', []))
                error_components.append(f"- {component_name}: {errors}")
        
        message = f"""
CRITICAL SYSTEM ALERT - FaktuLove

System Status: {health_report['overall_status'].upper()}
Error Components: {health_report['summary']['error_components']}

Failed Components:
{chr(10).join(error_components)}

Timestamp: {health_report['timestamp']}
Generation Time: {health_report['generation_time_ms']}ms

Please check the system health dashboard immediately.
        """.strip()
        
        return message
    
    def _create_warning_alert(self, health_report: Dict[str, Any]) -> str:
        """Create alert message for multiple warnings."""
        warning_components = []
        
        for component_name, component_data in health_report['components'].items():
            if component_data['status'] == 'warning':
                errors = ', '.join(component_data.get('errors', []))
                warning_components.append(f"- {component_name}: {errors}")
        
        message = f"""
SYSTEM WARNING - FaktuLove

System Status: {health_report['overall_status'].upper()}
Warning Components: {health_report['summary']['warning_components']}

Components with Warnings:
{chr(10).join(warning_components)}

Timestamp: {health_report['timestamp']}

Please review the system health dashboard.
        """.strip()
        
        return message
    
    def _create_performance_alert(self, performance_metrics: Dict[str, Any]) -> str:
        """Create alert message for performance issues."""
        message = f"""
PERFORMANCE ALERT - FaktuLove

High Error Rate Detected: {performance_metrics.get('error_rate_percent', 0)}%

24-hour Statistics:
- Total Requests: {performance_metrics.get('requests_24h', 0)}
- Successful Requests: {performance_metrics.get('successful_requests', 0)}
- Error Rate: {performance_metrics.get('error_rate_percent', 0)}%

Top Errors:
{chr(10).join([f"- {error['error']}: {error['count']} times" for error in performance_metrics.get('top_errors', [])[:3]])}

Please investigate the cause of increased error rates.
        """.strip()
        
        return message
    
    def _send_alert(self, subject: str, message: str) -> bool:
        """Send alert email to administrators."""
        try:
            admin_emails = getattr(settings, 'HEALTH_ALERT_EMAILS', [])
            
            if not admin_emails:
                # Fallback to ADMINS setting
                admin_emails = [email for name, email in getattr(settings, 'ADMINS', [])]
            
            if admin_emails:
                send_mail(
                    subject=f"[FaktuLove] {subject}",
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@faktulove.com'),
                    recipient_list=admin_emails,
                    fail_silently=False
                )
                logger.info(f"Health alert sent: {subject}")
                return True
            else:
                logger.warning("No admin emails configured for health alerts")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send health alert: {e}")
            return False


@staff_member_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def test_alerting_system(request):
    """Test the alerting system."""
    try:
        alerting_service = HealthAlertingService()
        result = alerting_service.check_and_send_alerts()
        
        return JsonResponse({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Failed to test alerting system: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@user_passes_test(is_superuser)
@require_http_methods(["GET"])
def system_metrics_api(request):
    """Get system metrics for monitoring."""
    try:
        health_service = HealthCheckService()
        
        # Get current health status
        health_report = health_service.generate_health_report()
        performance_metrics = health_service.get_performance_metrics()
        
        # Get system resource usage
        system_resources = health_service.check_system_resources()
        
        metrics = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': health_report['overall_status'],
            'component_count': {
                'healthy': health_report['summary']['healthy_components'],
                'warning': health_report['summary']['warning_components'],
                'error': health_report['summary']['error_components']
            },
            'performance': {
                'requests_24h': performance_metrics.get('requests_24h', 0),
                'error_rate': performance_metrics.get('error_rate_percent', 0),
                'successful_requests': performance_metrics.get('successful_requests', 0)
            },
            'resources': {
                'cpu_usage': system_resources.get('cpu_usage', 0),
                'memory_usage': system_resources.get('memory_usage', {}).get('used_percent', 0),
                'disk_usage': system_resources.get('disk_usage', {}).get('used_percent', 0)
            }
        }
        
        return JsonResponse(metrics)
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return JsonResponse({'error': 'Failed to get system metrics'}, status=500)