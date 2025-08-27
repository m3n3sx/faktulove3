"""
Deployment Monitoring Service for OCR Migration
Monitors performance and accuracy metrics during staged deployment
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Avg, Count, Q
from faktury.models import OCRResult, DocumentUpload

logger = logging.getLogger(__name__)


class DeploymentMonitoringService:
    """Service for monitoring OCR deployment metrics"""
    
    # Cache keys
    CACHE_KEY_PREFIX = "ocr_deployment_metrics"
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # Metric thresholds
    PERFORMANCE_THRESHOLDS = {
        'max_processing_time': 30.0,  # seconds
        'min_success_rate': 0.95,     # 95%
        'min_confidence': 0.80,       # 80%
        'max_error_rate': 0.05,       # 5%
    }
    
    # Alert thresholds
    ALERT_THRESHOLDS = {
        'critical_error_rate': 0.10,   # 10%
        'critical_processing_time': 60.0,  # 60 seconds
        'critical_success_rate': 0.90,  # 90%
    }
    
    def __init__(self):
        self.metrics_cache = {}
    
    def collect_processing_metrics(self, time_window_hours: int = 1) -> Dict[str, Any]:
        """
        Collect OCR processing metrics for the specified time window
        
        Args:
            time_window_hours: Time window in hours to collect metrics
            
        Returns:
            Dict containing processing metrics
        """
        cache_key = f"{self.CACHE_KEY_PREFIX}_processing_{time_window_hours}h"
        cached_metrics = cache.get(cache_key)
        
        if cached_metrics:
            return cached_metrics
        
        # Calculate time window
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        # Query OCR results
        ocr_results = OCRResult.objects.filter(
            created_at__gte=start_time,
            created_at__lte=end_time
        )
        
        # Query document uploads
        document_uploads = DocumentUpload.objects.filter(
            uploaded_at__gte=start_time,
            uploaded_at__lte=end_time
        )
        
        # Calculate metrics
        total_processed = ocr_results.count()
        total_uploaded = document_uploads.count()
        
        successful_results = ocr_results.filter(
            processing_status='completed',
            confidence_score__gte=0.80
        )
        
        failed_results = ocr_results.filter(
            processing_status__in=['failed', 'error']
        )
        
        # Processing time metrics
        processing_times = []
        for result in ocr_results.filter(processing_status='completed'):
            if result.processing_time:
                processing_times.append(result.processing_time)
        
        # Confidence score metrics
        confidence_scores = list(
            successful_results.values_list('confidence_score', flat=True)
        )
        
        # Engine usage metrics
        engine_usage = {}
        for result in ocr_results:
            engine = result.processor_version or 'unknown'
            engine_usage[engine] = engine_usage.get(engine, 0) + 1
        
        metrics = {
            'time_window': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'hours': time_window_hours
            },
            'volume': {
                'total_uploaded': total_uploaded,
                'total_processed': total_processed,
                'successful': successful_results.count(),
                'failed': failed_results.count(),
                'processing_rate': total_processed / max(total_uploaded, 1)
            },
            'performance': {
                'success_rate': successful_results.count() / max(total_processed, 1),
                'error_rate': failed_results.count() / max(total_processed, 1),
                'avg_processing_time': sum(processing_times) / max(len(processing_times), 1),
                'max_processing_time': max(processing_times) if processing_times else 0,
                'min_processing_time': min(processing_times) if processing_times else 0
            },
            'accuracy': {
                'avg_confidence': sum(confidence_scores) / max(len(confidence_scores), 1),
                'high_confidence_rate': len([c for c in confidence_scores if c >= 0.95]) / max(len(confidence_scores), 1),
                'low_confidence_rate': len([c for c in confidence_scores if c < 0.80]) / max(len(confidence_scores), 1)
            },
            'engines': engine_usage,
            'collected_at': timezone.now().isoformat()
        }
        
        # Cache metrics
        cache.set(cache_key, metrics, self.CACHE_TIMEOUT)
        
        return metrics
    
    def collect_comparison_metrics(self, time_window_hours: int = 1) -> Dict[str, Any]:
        """
        Collect comparison metrics between Google Cloud and open-source OCR
        
        Args:
            time_window_hours: Time window in hours to collect metrics
            
        Returns:
            Dict containing comparison metrics
        """
        cache_key = f"{self.CACHE_KEY_PREFIX}_comparison_{time_window_hours}h"
        cached_metrics = cache.get(cache_key)
        
        if cached_metrics:
            return cached_metrics
        
        # Calculate time window
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        # Query results by engine type
        google_cloud_results = OCRResult.objects.filter(
            created_at__gte=start_time,
            created_at__lte=end_time,
            processor_version__icontains='google'
        )
        
        opensource_results = OCRResult.objects.filter(
            created_at__gte=start_time,
            created_at__lte=end_time,
            processor_version__in=['tesseract', 'easyocr', 'composite']
        )
        
        def calculate_engine_metrics(queryset, engine_name):
            """Calculate metrics for a specific engine"""
            total = queryset.count()
            if total == 0:
                return {
                    'total': 0,
                    'success_rate': 0,
                    'avg_confidence': 0,
                    'avg_processing_time': 0,
                    'error_rate': 0
                }
            
            successful = queryset.filter(
                processing_status='completed',
                confidence_score__gte=0.80
            ).count()
            
            failed = queryset.filter(
                processing_status__in=['failed', 'error']
            ).count()
            
            avg_confidence = queryset.filter(
                processing_status='completed'
            ).aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0
            
            processing_times = list(
                queryset.filter(
                    processing_status='completed',
                    processing_time__isnull=False
                ).values_list('processing_time', flat=True)
            )
            
            avg_processing_time = sum(processing_times) / max(len(processing_times), 1)
            
            return {
                'total': total,
                'success_rate': successful / total,
                'avg_confidence': avg_confidence,
                'avg_processing_time': avg_processing_time,
                'error_rate': failed / total
            }
        
        google_metrics = calculate_engine_metrics(google_cloud_results, 'google_cloud')
        opensource_metrics = calculate_engine_metrics(opensource_results, 'opensource')
        
        # Calculate comparison
        comparison = {
            'time_window': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'hours': time_window_hours
            },
            'google_cloud': google_metrics,
            'opensource': opensource_metrics,
            'comparison': {
                'confidence_diff': opensource_metrics['avg_confidence'] - google_metrics['avg_confidence'],
                'speed_diff': google_metrics['avg_processing_time'] - opensource_metrics['avg_processing_time'],
                'success_rate_diff': opensource_metrics['success_rate'] - google_metrics['success_rate'],
                'volume_ratio': opensource_metrics['total'] / max(google_metrics['total'], 1)
            },
            'collected_at': timezone.now().isoformat()
        }
        
        # Cache comparison metrics
        cache.set(cache_key, comparison, self.CACHE_TIMEOUT)
        
        return comparison
    
    def check_health_status(self) -> Dict[str, Any]:
        """
        Check overall health status of OCR system
        
        Returns:
            Dict containing health status
        """
        # Get recent metrics
        metrics = self.collect_processing_metrics(time_window_hours=1)
        
        health_status = {
            'overall_status': 'healthy',
            'checks': {},
            'alerts': [],
            'timestamp': timezone.now().isoformat()
        }
        
        # Check processing time
        avg_processing_time = metrics['performance']['avg_processing_time']
        if avg_processing_time > self.ALERT_THRESHOLDS['critical_processing_time']:
            health_status['overall_status'] = 'critical'
            health_status['alerts'].append({
                'type': 'critical',
                'message': f"Average processing time too high: {avg_processing_time:.2f}s"
            })
        elif avg_processing_time > self.PERFORMANCE_THRESHOLDS['max_processing_time']:
            health_status['overall_status'] = 'warning'
            health_status['alerts'].append({
                'type': 'warning',
                'message': f"Average processing time elevated: {avg_processing_time:.2f}s"
            })
        
        health_status['checks']['processing_time'] = {
            'status': 'pass' if avg_processing_time <= self.PERFORMANCE_THRESHOLDS['max_processing_time'] else 'fail',
            'value': avg_processing_time,
            'threshold': self.PERFORMANCE_THRESHOLDS['max_processing_time']
        }
        
        # Check success rate
        success_rate = metrics['performance']['success_rate']
        if success_rate < self.ALERT_THRESHOLDS['critical_success_rate']:
            health_status['overall_status'] = 'critical'
            health_status['alerts'].append({
                'type': 'critical',
                'message': f"Success rate too low: {success_rate:.2%}"
            })
        elif success_rate < self.PERFORMANCE_THRESHOLDS['min_success_rate']:
            if health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'
            health_status['alerts'].append({
                'type': 'warning',
                'message': f"Success rate below threshold: {success_rate:.2%}"
            })
        
        health_status['checks']['success_rate'] = {
            'status': 'pass' if success_rate >= self.PERFORMANCE_THRESHOLDS['min_success_rate'] else 'fail',
            'value': success_rate,
            'threshold': self.PERFORMANCE_THRESHOLDS['min_success_rate']
        }
        
        # Check error rate
        error_rate = metrics['performance']['error_rate']
        if error_rate > self.ALERT_THRESHOLDS['critical_error_rate']:
            health_status['overall_status'] = 'critical'
            health_status['alerts'].append({
                'type': 'critical',
                'message': f"Error rate too high: {error_rate:.2%}"
            })
        elif error_rate > self.PERFORMANCE_THRESHOLDS['max_error_rate']:
            if health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'
            health_status['alerts'].append({
                'type': 'warning',
                'message': f"Error rate elevated: {error_rate:.2%}"
            })
        
        health_status['checks']['error_rate'] = {
            'status': 'pass' if error_rate <= self.PERFORMANCE_THRESHOLDS['max_error_rate'] else 'fail',
            'value': error_rate,
            'threshold': self.PERFORMANCE_THRESHOLDS['max_error_rate']
        }
        
        # Check confidence score
        avg_confidence = metrics['accuracy']['avg_confidence']
        if avg_confidence < self.PERFORMANCE_THRESHOLDS['min_confidence']:
            if health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'
            health_status['alerts'].append({
                'type': 'warning',
                'message': f"Average confidence below threshold: {avg_confidence:.2%}"
            })
        
        health_status['checks']['confidence'] = {
            'status': 'pass' if avg_confidence >= self.PERFORMANCE_THRESHOLDS['min_confidence'] else 'fail',
            'value': avg_confidence,
            'threshold': self.PERFORMANCE_THRESHOLDS['min_confidence']
        }
        
        return health_status
    
    def generate_deployment_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Generate comprehensive deployment report
        
        Args:
            time_window_hours: Time window in hours for the report
            
        Returns:
            Dict containing deployment report
        """
        # Collect all metrics
        processing_metrics = self.collect_processing_metrics(time_window_hours)
        comparison_metrics = self.collect_comparison_metrics(time_window_hours)
        health_status = self.check_health_status()
        
        # Generate report
        report = {
            'report_info': {
                'generated_at': timezone.now().isoformat(),
                'time_window_hours': time_window_hours,
                'report_type': 'deployment_monitoring'
            },
            'executive_summary': {
                'overall_health': health_status['overall_status'],
                'total_processed': processing_metrics['volume']['total_processed'],
                'success_rate': processing_metrics['performance']['success_rate'],
                'avg_processing_time': processing_metrics['performance']['avg_processing_time'],
                'avg_confidence': processing_metrics['accuracy']['avg_confidence']
            },
            'detailed_metrics': {
                'processing': processing_metrics,
                'comparison': comparison_metrics,
                'health': health_status
            },
            'recommendations': self._generate_recommendations(
                processing_metrics, comparison_metrics, health_status
            )
        }
        
        return report
    
    def _generate_recommendations(self, processing_metrics: Dict, 
                                comparison_metrics: Dict, 
                                health_status: Dict) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        # Performance recommendations
        if processing_metrics['performance']['avg_processing_time'] > 20:
            recommendations.append(
                "Consider optimizing OCR processing pipeline - average processing time is high"
            )
        
        if processing_metrics['performance']['success_rate'] < 0.95:
            recommendations.append(
                "Investigate processing failures - success rate is below target"
            )
        
        # Accuracy recommendations
        if processing_metrics['accuracy']['avg_confidence'] < 0.85:
            recommendations.append(
                "Review OCR accuracy - average confidence is below optimal level"
            )
        
        # Comparison recommendations
        if comparison_metrics.get('comparison', {}).get('confidence_diff', 0) < -0.05:
            recommendations.append(
                "Open-source OCR confidence is significantly lower than Google Cloud - consider tuning"
            )
        
        if comparison_metrics.get('comparison', {}).get('speed_diff', 0) < -5:
            recommendations.append(
                "Open-source OCR is slower than Google Cloud - consider performance optimization"
            )
        
        # Health recommendations
        if health_status['overall_status'] == 'critical':
            recommendations.append(
                "CRITICAL: System health is degraded - immediate attention required"
            )
        elif health_status['overall_status'] == 'warning':
            recommendations.append(
                "System health shows warnings - monitor closely and consider adjustments"
            )
        
        if not recommendations:
            recommendations.append("System is performing well - continue monitoring")
        
        return recommendations


# Global instance
deployment_monitor = DeploymentMonitoringService()