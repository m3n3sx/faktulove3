"""
Rollout Monitoring Service
Monitors performance, errors, and user feedback during production rollout
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.db.models import Avg, Count, Q
from django.contrib.auth.models import User
import statistics

logger = logging.getLogger(__name__)

class RolloutMonitoringService:
    """Service for monitoring production rollout metrics"""
    
    CACHE_PREFIX = "rollout_monitoring"
    CACHE_TIMEOUT = 60  # 1 minute for real-time monitoring
    
    def __init__(self):
        self.monitoring_active = True
    
    def get_error_rate(self, time_window_minutes: int = 5) -> float:
        """Get current error rate as percentage"""
        try:
            from faktury.models import ErrorLog
            
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=time_window_minutes)
            
            # Count total requests and errors in time window
            total_requests = self._get_request_count(start_time, end_time)
            error_count = ErrorLog.objects.filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time,
                level__in=['ERROR', 'CRITICAL']
            ).count()
            
            if total_requests == 0:
                return 0.0
            
            error_rate = (error_count / total_requests) * 100
            
            # Cache the result
            cache_key = f"{self.CACHE_PREFIX}_error_rate"
            cache.set(cache_key, error_rate, self.CACHE_TIMEOUT)
            
            return error_rate
            
        except Exception as e:
            logger.error(f"Failed to calculate error rate: {e}")
            return 0.0
    
    def get_response_time_metrics(self, time_window_minutes: int = 5) -> Dict[str, float]:
        """Get response time metrics (P50, P95, P99)"""
        try:
            from faktury.models import RequestLog
            
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=time_window_minutes)
            
            # Get response times from request logs
            response_times = list(
                RequestLog.objects.filter(
                    timestamp__gte=start_time,
                    timestamp__lte=end_time
                ).values_list('response_time_ms', flat=True)
            )
            
            if not response_times:
                return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0}
            
            metrics = {
                "p50": statistics.median(response_times),
                "p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
                "p99": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times),
                "avg": statistics.mean(response_times)
            }
            
            # Cache the result
            cache_key = f"{self.CACHE_PREFIX}_response_times"
            cache.set(cache_key, metrics, self.CACHE_TIMEOUT)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate response time metrics: {e}")
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0}
    
    def get_user_satisfaction_score(self, time_window_hours: int = 1) -> float:
        """Get user satisfaction score from feedback"""
        try:
            from faktury.models import UserFeedback
            
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            # Get average satisfaction rating
            avg_rating = UserFeedback.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time,
                rating__isnull=False
            ).aggregate(avg_rating=Avg('rating'))['avg_rating']
            
            satisfaction_score = avg_rating if avg_rating is not None else 0.0
            
            # Cache the result
            cache_key = f"{self.CACHE_PREFIX}_user_satisfaction"
            cache.set(cache_key, satisfaction_score, self.CACHE_TIMEOUT * 5)  # Cache longer
            
            return satisfaction_score
            
        except Exception as e:
            logger.error(f"Failed to calculate user satisfaction: {e}")
            return 0.0
    
    def get_feature_adoption_rates(self) -> Dict[str, float]:
        """Get adoption rates for design system features"""
        try:
            from faktury.models import FeatureUsageLog
            from faktury.services.feature_flag_service import feature_flag_service
            
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)  # Last hour
            
            adoption_rates = {}
            
            # Get all design system flags
            for flag_name in feature_flag_service.all_flags.keys():
                # Count unique users who used this feature
                users_with_feature = FeatureUsageLog.objects.filter(
                    feature_name=flag_name,
                    timestamp__gte=start_time,
                    timestamp__lte=end_time
                ).values('user_id').distinct().count()
                
                # Count total active users in the same period
                total_active_users = FeatureUsageLog.objects.filter(
                    timestamp__gte=start_time,
                    timestamp__lte=end_time
                ).values('user_id').distinct().count()
                
                if total_active_users > 0:
                    adoption_rate = users_with_feature / total_active_users
                else:
                    adoption_rate = 0.0
                
                adoption_rates[flag_name] = adoption_rate
            
            # Cache the result
            cache_key = f"{self.CACHE_PREFIX}_feature_adoption"
            cache.set(cache_key, adoption_rates, self.CACHE_TIMEOUT * 2)
            
            return adoption_rates
            
        except Exception as e:
            logger.error(f"Failed to calculate feature adoption rates: {e}")
            return {}
    
    def get_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            # Get component metrics
            error_rate = self.get_error_rate()
            response_times = self.get_response_time_metrics()
            
            # Calculate performance score based on multiple factors
            # Error rate component (0-40 points)
            error_score = max(0, 40 - (error_rate * 8))  # Penalty for errors
            
            # Response time component (0-40 points)
            p95_response = response_times.get("p95", 0)
            if p95_response <= 1000:  # Under 1 second
                response_score = 40
            elif p95_response <= 2000:  # Under 2 seconds
                response_score = 30
            elif p95_response <= 3000:  # Under 3 seconds
                response_score = 20
            elif p95_response <= 5000:  # Under 5 seconds
                response_score = 10
            else:
                response_score = 0
            
            # Availability component (0-20 points)
            # This would be based on uptime monitoring
            availability_score = 20  # Assume 100% for now
            
            total_score = error_score + response_score + availability_score
            
            # Cache the result
            cache_key = f"{self.CACHE_PREFIX}_performance_score"
            cache.set(cache_key, total_score, self.CACHE_TIMEOUT)
            
            return total_score
            
        except Exception as e:
            logger.error(f"Failed to calculate performance score: {e}")
            return 0.0
    
    def get_business_impact_metrics(self) -> Dict[str, Any]:
        """Get business impact metrics during rollout"""
        try:
            from faktury.models import Faktura, UserSession
            
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            # Invoice creation rate
            invoices_created = Faktura.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time
            ).count()
            
            # User engagement metrics
            active_sessions = UserSession.objects.filter(
                last_activity__gte=start_time
            ).count()
            
            # Conversion rate (invoices per session)
            conversion_rate = invoices_created / active_sessions if active_sessions > 0 else 0
            
            # Revenue impact (if available)
            total_revenue = Faktura.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time
            ).aggregate(total=models.Sum('kwota_brutto'))['total'] or 0
            
            metrics = {
                "invoices_created": invoices_created,
                "active_sessions": active_sessions,
                "conversion_rate": conversion_rate,
                "total_revenue": float(total_revenue),
                "revenue_per_session": float(total_revenue) / active_sessions if active_sessions > 0 else 0
            }
            
            # Cache the result
            cache_key = f"{self.CACHE_PREFIX}_business_impact"
            cache.set(cache_key, metrics, self.CACHE_TIMEOUT * 2)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate business impact metrics: {e}")
            return {}
    
    def get_user_feedback_summary(self, time_window_hours: int = 1) -> Dict[str, Any]:
        """Get summary of user feedback during rollout"""
        try:
            from faktury.models import UserFeedback
            
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            feedback_queryset = UserFeedback.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time
            )
            
            # Count feedback by rating
            rating_counts = {}
            for i in range(1, 6):
                rating_counts[f"rating_{i}"] = feedback_queryset.filter(rating=i).count()
            
            # Count feedback by category
            category_counts = feedback_queryset.values('category').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Get recent comments
            recent_comments = list(
                feedback_queryset.filter(
                    comment__isnull=False
                ).exclude(
                    comment=""
                ).order_by('-created_at')[:10].values(
                    'rating', 'comment', 'category', 'created_at'
                )
            )
            
            summary = {
                "total_feedback": feedback_queryset.count(),
                "rating_distribution": rating_counts,
                "category_distribution": list(category_counts),
                "recent_comments": recent_comments,
                "average_rating": feedback_queryset.aggregate(
                    avg=Avg('rating')
                )['avg'] or 0
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get user feedback summary: {e}")
            return {}
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics that might indicate problems"""
        anomalies = []
        
        try:
            # Check error rate anomaly
            current_error_rate = self.get_error_rate(5)  # Last 5 minutes
            historical_error_rate = self.get_error_rate(60)  # Last hour average
            
            if current_error_rate > historical_error_rate * 2 and current_error_rate > 1.0:
                anomalies.append({
                    "type": "error_rate_spike",
                    "severity": "high" if current_error_rate > 5.0 else "medium",
                    "message": f"Error rate spiked to {current_error_rate:.2f}% (historical: {historical_error_rate:.2f}%)",
                    "current_value": current_error_rate,
                    "historical_value": historical_error_rate
                })
            
            # Check response time anomaly
            current_response_times = self.get_response_time_metrics(5)
            
            if current_response_times["p95"] > 5000:  # Over 5 seconds
                anomalies.append({
                    "type": "response_time_degradation",
                    "severity": "high" if current_response_times["p95"] > 10000 else "medium",
                    "message": f"P95 response time is {current_response_times['p95']:.0f}ms",
                    "current_value": current_response_times["p95"]
                })
            
            # Check user satisfaction anomaly
            satisfaction = self.get_user_satisfaction_score(1)
            if satisfaction < 2.0 and satisfaction > 0:  # Low satisfaction
                anomalies.append({
                    "type": "low_user_satisfaction",
                    "severity": "medium",
                    "message": f"User satisfaction dropped to {satisfaction:.1f}/5.0",
                    "current_value": satisfaction
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    def generate_rollout_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data for rollout monitoring"""
        try:
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "error_rate": self.get_error_rate(),
                "response_times": self.get_response_time_metrics(),
                "user_satisfaction": self.get_user_satisfaction_score(),
                "feature_adoption": self.get_feature_adoption_rates(),
                "performance_score": self.get_performance_score(),
                "business_impact": self.get_business_impact_metrics(),
                "user_feedback": self.get_user_feedback_summary(),
                "anomalies": self.detect_anomalies()
            }
            
            # Add rollout status
            from faktury.services.feature_flag_service import feature_flag_service
            dashboard_data["rollout_status"] = feature_flag_service.get_flag_statistics()
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard data: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def log_rollout_event(self, event_type: str, details: Dict[str, Any]):
        """Log significant rollout events"""
        try:
            from faktury.models import RolloutEvent
            
            RolloutEvent.objects.create(
                event_type=event_type,
                details=json.dumps(details),
                timestamp=datetime.now()
            )
            
            logger.info(f"Rollout event logged: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to log rollout event: {e}")
    
    def _get_request_count(self, start_time: datetime, end_time: datetime) -> int:
        """Get total request count in time window"""
        try:
            from faktury.models import RequestLog
            return RequestLog.objects.filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time
            ).count()
        except Exception:
            # Fallback: estimate based on typical traffic
            minutes = (end_time - start_time).total_seconds() / 60
            return int(minutes * 10)  # Assume 10 requests per minute

# Global instance
rollout_monitoring_service = RolloutMonitoringService()