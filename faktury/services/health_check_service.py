"""
Health Check Service for comprehensive system monitoring.

This service provides health checks for database, OCR services, static assets,
and overall system performance monitoring.
"""

import os
import time
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db import connection, connections
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Avg
from django.core.files.storage import default_storage

from faktury.models import (
    Faktura, OCRResult, DocumentUpload, 
    SystemHealthMetric
)
from faktury.services.ocr_integration import OCRIntegrationService
from faktury.services.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class HealthCheckService:
    """Comprehensive system health monitoring service."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.ocr_service = OCRIntegrationService()
        
    def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        start_time = time.time()
        health_data = {
            'status': 'healthy',
            'response_time': 0,
            'connection_count': 0,
            'query_performance': {},
            'errors': []
        }
        
        try:
            # Test database connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            # Measure response time
            health_data['response_time'] = round((time.time() - start_time) * 1000, 2)
            
            # Check connection count
            health_data['connection_count'] = len(connections.all())
            
            # Test query performance on key tables
            query_start = time.time()
            invoice_count = Faktura.objects.count()
            query_time = (time.time() - query_start) * 1000
            
            health_data['query_performance'] = {
                'invoice_count_query_ms': round(query_time, 2),
                'total_invoices': invoice_count
            }
            
            # Check for slow queries (if response time > 100ms)
            if health_data['response_time'] > 100:
                health_data['status'] = 'warning'
                health_data['errors'].append('Database response time is slow')
                
        except Exception as e:
            health_data['status'] = 'error'
            health_data['errors'].append(f'Database connection failed: {str(e)}')
            logger.error(f"Database health check failed: {e}")
            
        return health_data
    
    def check_ocr_services(self) -> Dict[str, Any]:
        """Check OCR service availability and performance."""
        health_data = {
            'status': 'healthy',
            'engines': {},
            'recent_processing': {},
            'errors': []
        }
        
        try:
            # Check OCR engine availability
            available_engines = self.ocr_service.get_available_engines()
            
            for engine_name in ['tesseract', 'easyocr', 'paddle']:
                engine_status = {
                    'available': engine_name in available_engines,
                    'last_used': None,
                    'success_rate': 0
                }
                
                if engine_status['available']:
                    # Check recent OCR results for this engine
                    recent_results = OCRResult.objects.filter(
                        engine_used=engine_name,
                        created_at__gte=timezone.now() - timedelta(hours=24)
                    )
                    
                    if recent_results.exists():
                        total_results = recent_results.count()
                        successful_results = recent_results.filter(
                            confidence_score__gte=0.7
                        ).count()
                        
                        engine_status['success_rate'] = round(
                            (successful_results / total_results) * 100, 2
                        ) if total_results > 0 else 0
                        
                        engine_status['last_used'] = recent_results.latest(
                            'created_at'
                        ).created_at.isoformat()
                
                health_data['engines'][engine_name] = engine_status
            
            # Check recent OCR processing performance
            recent_uploads = DocumentUpload.objects.filter(
                uploaded_at__gte=timezone.now() - timedelta(hours=24)
            )
            
            if recent_uploads.exists():
                avg_processing_time = recent_uploads.aggregate(
                    avg_time=Avg('processing_time')
                )['avg_time']
                
                health_data['recent_processing'] = {
                    'total_uploads': recent_uploads.count(),
                    'avg_processing_time_seconds': round(avg_processing_time or 0, 2),
                    'failed_uploads': recent_uploads.filter(
                        processing_status='failed'
                    ).count()
                }
            
            # Determine overall OCR health status
            available_count = sum(1 for engine in health_data['engines'].values() 
                                if engine['available'])
            
            if available_count == 0:
                health_data['status'] = 'error'
                health_data['errors'].append('No OCR engines available')
            elif available_count < 2:
                health_data['status'] = 'warning'
                health_data['errors'].append('Limited OCR engine availability')
                
        except Exception as e:
            health_data['status'] = 'error'
            health_data['errors'].append(f'OCR service check failed: {str(e)}')
            logger.error(f"OCR health check failed: {e}")
            
        return health_data
    
    def check_static_assets(self) -> Dict[str, Any]:
        """Check static asset availability and performance."""
        health_data = {
            'status': 'healthy',
            'critical_assets': {},
            'storage_info': {},
            'errors': []
        }
        
        try:
            # Critical assets to check
            critical_assets = [
                'css/main.css',
                'js/main.js',
                'admin/css/base.css',
                'admin/js/core.js'
            ]
            
            for asset_path in critical_assets:
                asset_status = {
                    'exists': False,
                    'size_bytes': 0,
                    'last_modified': None
                }
                
                try:
                    full_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], asset_path)
                    
                    if os.path.exists(full_path):
                        asset_status['exists'] = True
                        stat_info = os.stat(full_path)
                        asset_status['size_bytes'] = stat_info.st_size
                        asset_status['last_modified'] = datetime.fromtimestamp(
                            stat_info.st_mtime
                        ).isoformat()
                    
                except Exception as e:
                    logger.warning(f"Could not check asset {asset_path}: {e}")
                
                health_data['critical_assets'][asset_path] = asset_status
            
            # Check storage information
            if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
                try:
                    statvfs = os.statvfs(settings.STATIC_ROOT)
                    total_space = statvfs.f_frsize * statvfs.f_blocks
                    free_space = statvfs.f_frsize * statvfs.f_available
                    
                    health_data['storage_info'] = {
                        'total_space_gb': round(total_space / (1024**3), 2),
                        'free_space_gb': round(free_space / (1024**3), 2),
                        'usage_percent': round(((total_space - free_space) / total_space) * 100, 2)
                    }
                    
                    # Warning if storage usage > 90%
                    if health_data['storage_info']['usage_percent'] > 90:
                        health_data['status'] = 'warning'
                        health_data['errors'].append('High storage usage detected')
                        
                except Exception as e:
                    logger.warning(f"Could not get storage info: {e}")
            
            # Check for missing critical assets
            missing_assets = [
                asset for asset, status in health_data['critical_assets'].items()
                if not status['exists']
            ]
            
            if missing_assets:
                health_data['status'] = 'warning' if len(missing_assets) < 3 else 'error'
                health_data['errors'].append(f'Missing critical assets: {", ".join(missing_assets)}')
                
        except Exception as e:
            health_data['status'] = 'error'
            health_data['errors'].append(f'Static asset check failed: {str(e)}')
            logger.error(f"Static asset health check failed: {e}")
            
        return health_data
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage (CPU, memory, disk)."""
        health_data = {
            'status': 'healthy',
            'cpu_usage': 0,
            'memory_usage': {},
            'disk_usage': {},
            'errors': []
        }
        
        try:
            # CPU usage
            health_data['cpu_usage'] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            health_data['memory_usage'] = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_percent': memory.percent
            }
            
            # Disk usage
            disk = psutil.disk_usage('/')
            health_data['disk_usage'] = {
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'used_percent': round((disk.used / disk.total) * 100, 2)
            }
            
            # Check thresholds
            if health_data['cpu_usage'] > 80:
                health_data['status'] = 'warning'
                health_data['errors'].append('High CPU usage detected')
                
            if health_data['memory_usage']['used_percent'] > 85:
                health_data['status'] = 'warning'
                health_data['errors'].append('High memory usage detected')
                
            if health_data['disk_usage']['used_percent'] > 90:
                health_data['status'] = 'warning'
                health_data['errors'].append('High disk usage detected')
                
        except Exception as e:
            health_data['status'] = 'error'
            health_data['errors'].append(f'System resource check failed: {str(e)}')
            logger.error(f"System resource health check failed: {e}")
            
        return health_data
    
    def check_cache_health(self) -> Dict[str, Any]:
        """Check cache system health."""
        health_data = {
            'status': 'healthy',
            'cache_backend': str(cache.__class__.__name__),
            'test_result': False,
            'errors': []
        }
        
        try:
            # Test cache functionality
            test_key = 'health_check_test'
            test_value = f'test_{int(time.time())}'
            
            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)
            
            health_data['test_result'] = retrieved_value == test_value
            
            if not health_data['test_result']:
                health_data['status'] = 'error'
                health_data['errors'].append('Cache test failed')
            
            # Clean up test key
            cache.delete(test_key)
            
        except Exception as e:
            health_data['status'] = 'error'
            health_data['errors'].append(f'Cache health check failed: {str(e)}')
            logger.error(f"Cache health check failed: {e}")
            
        return health_data
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        report_start_time = time.time()
        
        report = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': 'healthy',
            'components': {},
            'summary': {},
            'recommendations': [],
            'generation_time_ms': 0
        }
        
        # Run all health checks
        checks = {
            'database': self.check_database_health,
            'ocr_services': self.check_ocr_services,
            'static_assets': self.check_static_assets,
            'system_resources': self.check_system_resources,
            'cache': self.check_cache_health
        }
        
        error_count = 0
        warning_count = 0
        
        for component_name, check_function in checks.items():
            try:
                component_health = check_function()
                report['components'][component_name] = component_health
                
                if component_health['status'] == 'error':
                    error_count += 1
                elif component_health['status'] == 'warning':
                    warning_count += 1
                    
            except Exception as e:
                error_count += 1
                report['components'][component_name] = {
                    'status': 'error',
                    'errors': [f'Health check failed: {str(e)}']
                }
                logger.error(f"Health check for {component_name} failed: {e}")
        
        # Determine overall status
        if error_count > 0:
            report['overall_status'] = 'error'
        elif warning_count > 0:
            report['overall_status'] = 'warning'
        
        # Generate summary
        report['summary'] = {
            'total_components': len(checks),
            'healthy_components': len(checks) - error_count - warning_count,
            'warning_components': warning_count,
            'error_components': error_count
        }
        
        # Generate recommendations
        if error_count > 0:
            report['recommendations'].append('Immediate attention required for failed components')
        if warning_count > 0:
            report['recommendations'].append('Monitor warning components closely')
        if error_count == 0 and warning_count == 0:
            report['recommendations'].append('System is operating normally')
        
        # Record generation time
        report['generation_time_ms'] = round((time.time() - report_start_time) * 1000, 2)
        
        # Store health report in database
        self._store_health_report(report)
        
        return report
    
    def _store_health_report(self, report: Dict[str, Any]) -> None:
        """Store health report in database for historical tracking."""
        try:
            for component_name, component_data in report['components'].items():
                SystemHealthMetric.objects.create(
                    component=component_name,
                    status=component_data['status'],
                    response_time=component_data.get('response_time', 0),
                    error_count=len(component_data.get('errors', [])),
                    metadata=component_data
                )
        except Exception as e:
            logger.error(f"Failed to store health report: {e}")
    
    def get_health_history(self, component: Optional[str] = None, 
                          hours: int = 24) -> List[Dict[str, Any]]:
        """Get health check history for analysis."""
        try:
            queryset = SystemHealthMetric.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=hours)
            ).order_by('-timestamp')
            
            if component:
                queryset = queryset.filter(component=component)
            
            return [
                {
                    'timestamp': record.timestamp.isoformat(),
                    'component': record.component,
                    'status': record.status,
                    'response_time': record.response_time,
                    'error_count': record.error_count,
                    'metadata': record.metadata
                }
                for record in queryset[:100]  # Limit to last 100 records
            ]
            
        except Exception as e:
            logger.error(f"Failed to get health history: {e}")
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for dashboard."""
        try:
            # Get recent performance data
            recent_activity = UserActivityLog.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=24)
            )
            
            metrics = {
                'requests_24h': recent_activity.count(),
                'successful_requests': recent_activity.filter(success=True).count(),
                'error_rate_percent': 0,
                'avg_response_time': 0,
                'top_errors': []
            }
            
            if metrics['requests_24h'] > 0:
                metrics['error_rate_percent'] = round(
                    ((metrics['requests_24h'] - metrics['successful_requests']) / 
                     metrics['requests_24h']) * 100, 2
                )
            
            # Get top errors
            error_logs = recent_activity.filter(success=False).values(
                'error_message'
            ).annotate(count=Count('error_message')).order_by('-count')[:5]
            
            metrics['top_errors'] = [
                {'error': log['error_message'], 'count': log['count']}
                for log in error_logs
            ]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}