"""
Performance Monitor Service
Tracks page load times, system metrics, and provides performance optimization recommendations.
"""

import time
import logging
import statistics
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import connection, transaction
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Max, Min
import psutil
import json

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Container for performance metrics"""
    
    def __init__(self):
        self.page_load_time = None
        self.database_query_time = None
        self.cache_hit_ratio = None
        self.memory_usage = None
        self.cpu_usage = None
        self.response_time = None
        self.error_rate = None
        self.throughput = None
        self.timestamp = timezone.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'page_load_time': self.page_load_time,
            'database_query_time': self.database_query_time,
            'cache_hit_ratio': self.cache_hit_ratio,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'response_time': self.response_time,
            'error_rate': self.error_rate,
            'throughput': self.throughput,
            'timestamp': self.timestamp.isoformat()
        }


class DatabaseQueryAnalyzer:
    """Analyzes database query performance"""
    
    def __init__(self):
        self.query_log = []
        self.slow_query_threshold = 0.1  # 100ms
    
    def start_monitoring(self):
        """Start monitoring database queries"""
        self.query_log.clear()
        connection.force_debug_cursor = True
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return analysis"""
        queries = connection.queries
        connection.force_debug_cursor = False
        
        if not queries:
            return {
                'total_queries': 0,
                'total_time': 0,
                'slow_queries': 0,
                'average_time': 0,
                'recommendations': []
            }
        
        query_times = [float(q['time']) for q in queries]
        slow_queries = [q for q in queries if float(q['time']) > self.slow_query_threshold]
        
        analysis = {
            'total_queries': len(queries),
            'total_time': sum(query_times),
            'slow_queries': len(slow_queries),
            'average_time': statistics.mean(query_times),
            'max_time': max(query_times),
            'min_time': min(query_times),
            'recommendations': []
        }
        
        # Generate recommendations
        if len(slow_queries) > 0:
            analysis['recommendations'].append(
                f"Optimize {len(slow_queries)} slow queries (>{self.slow_query_threshold}s)"
            )
        
        if len(queries) > 50:
            analysis['recommendations'].append(
                "Consider reducing number of database queries (N+1 problem?)"
            )
        
        # Analyze query patterns
        select_queries = [q for q in queries if q['sql'].strip().upper().startswith('SELECT')]
        if len(select_queries) > len(queries) * 0.8:
            analysis['recommendations'].append(
                "High ratio of SELECT queries - consider caching frequently accessed data"
            )
        
        return analysis


class CacheAnalyzer:
    """Analyzes cache performance"""
    
    def __init__(self):
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            # Try to get cache stats from Redis if available
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_client'):
                client = cache._cache.get_client()
                if hasattr(client, 'info'):
                    redis_info = client.info()
                    return {
                        'hits': redis_info.get('keyspace_hits', 0),
                        'misses': redis_info.get('keyspace_misses', 0),
                        'hit_ratio': self._calculate_hit_ratio(
                            redis_info.get('keyspace_hits', 0),
                            redis_info.get('keyspace_misses', 0)
                        ),
                        'memory_usage': redis_info.get('used_memory', 0),
                        'connected_clients': redis_info.get('connected_clients', 0),
                        'recommendations': self._generate_cache_recommendations(redis_info)
                    }
        except Exception as e:
            logger.warning(f"Could not get Redis cache stats: {e}")
        
        # Fallback to basic cache testing
        return self._test_cache_performance()
    
    def _calculate_hit_ratio(self, hits: int, misses: int) -> float:
        """Calculate cache hit ratio"""
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0
    
    def _test_cache_performance(self) -> Dict[str, Any]:
        """Test cache performance with sample operations"""
        test_key = 'performance_test_key'
        test_value = 'performance_test_value'
        
        # Test cache set
        start_time = time.time()
        cache.set(test_key, test_value, 60)
        set_time = time.time() - start_time
        
        # Test cache get
        start_time = time.time()
        retrieved_value = cache.get(test_key)
        get_time = time.time() - start_time
        
        # Clean up
        cache.delete(test_key)
        
        return {
            'set_time': set_time * 1000,  # Convert to ms
            'get_time': get_time * 1000,
            'cache_working': retrieved_value == test_value,
            'recommendations': [
                "Cache performance test completed"
            ] if retrieved_value == test_value else [
                "Cache may not be working properly"
            ]
        }
    
    def _generate_cache_recommendations(self, redis_info: Dict) -> List[str]:
        """Generate cache optimization recommendations"""
        recommendations = []
        
        hit_ratio = self._calculate_hit_ratio(
            redis_info.get('keyspace_hits', 0),
            redis_info.get('keyspace_misses', 0)
        )
        
        if hit_ratio < 80:
            recommendations.append(f"Cache hit ratio is low ({hit_ratio:.1f}%) - review caching strategy")
        
        memory_usage = redis_info.get('used_memory', 0)
        max_memory = redis_info.get('maxmemory', 0)
        
        if max_memory > 0 and memory_usage / max_memory > 0.8:
            recommendations.append("Cache memory usage is high - consider increasing memory or TTL optimization")
        
        return recommendations


class SystemResourceMonitor:
    """Monitors system resource usage"""
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O (if available)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            except Exception:
                network_stats = {}
            
            metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'memory_used_gb': memory.used / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'network': network_stats,
                'recommendations': []
            }
            
            # Generate recommendations
            if cpu_percent > 80:
                metrics['recommendations'].append("High CPU usage detected - consider optimization")
            
            if memory.percent > 80:
                metrics['recommendations'].append("High memory usage detected - check for memory leaks")
            
            if disk.percent > 90:
                metrics['recommendations'].append("Low disk space - consider cleanup or expansion")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'error': str(e),
                'recommendations': ["Could not retrieve system metrics"]
            }


class PerformanceMonitor:
    """
    Main performance monitoring service that tracks page load times,
    system metrics, and provides optimization recommendations.
    """
    
    def __init__(self):
        self.db_analyzer = DatabaseQueryAnalyzer()
        self.cache_analyzer = CacheAnalyzer()
        self.system_monitor = SystemResourceMonitor()
        self.performance_budgets = {
            'page_load_time': 3.0,  # 3 seconds
            'database_query_time': 0.5,  # 500ms
            'cache_hit_ratio': 80.0,  # 80%
            'memory_usage': 80.0,  # 80%
            'cpu_usage': 70.0,  # 70%
        }
    
    def start_request_monitoring(self, request_id: str = None) -> str:
        """Start monitoring a request"""
        if not request_id:
            request_id = f"req_{int(time.time() * 1000)}"
        
        # Store start time in cache
        cache.set(f"perf_start_{request_id}", time.time(), 300)  # 5 minutes
        
        # Start database monitoring
        self.db_analyzer.start_monitoring()
        
        return request_id
    
    def end_request_monitoring(self, request_id: str, user: User = None, 
                             url: str = None) -> PerformanceMetrics:
        """End monitoring and collect metrics"""
        metrics = PerformanceMetrics()
        
        # Calculate response time
        start_time = cache.get(f"perf_start_{request_id}")
        if start_time:
            metrics.response_time = time.time() - start_time
            cache.delete(f"perf_start_{request_id}")
        
        # Get database metrics
        db_analysis = self.db_analyzer.stop_monitoring()
        metrics.database_query_time = db_analysis.get('total_time', 0)
        
        # Get cache metrics
        cache_stats = self.cache_analyzer.get_cache_stats()
        metrics.cache_hit_ratio = cache_stats.get('hit_ratio', 0)
        
        # Get system metrics
        system_metrics = self.system_monitor.get_system_metrics()
        metrics.memory_usage = system_metrics.get('memory_percent', 0)
        metrics.cpu_usage = system_metrics.get('cpu_percent', 0)
        
        # Store metrics for analysis
        self._store_metrics(metrics, user, url, db_analysis, cache_stats, system_metrics)
        
        return metrics
    
    def _store_metrics(self, metrics: PerformanceMetrics, user: User = None,
                      url: str = None, db_analysis: Dict = None,
                      cache_stats: Dict = None, system_metrics: Dict = None):
        """Store performance metrics for later analysis"""
        try:
            # Store in cache for recent metrics
            cache_key = f"perf_metrics_{int(time.time())}"
            cache_data = {
                'metrics': metrics.to_dict(),
                'user_id': user.id if user else None,
                'url': url,
                'db_analysis': db_analysis,
                'cache_stats': cache_stats,
                'system_metrics': system_metrics
            }
            cache.set(cache_key, cache_data, 3600)  # 1 hour
            
            # Store in database if PerformanceMetric model exists
            self._store_in_database(metrics, user, url)
            
        except Exception as e:
            logger.error(f"Error storing performance metrics: {e}")
    
    def _store_in_database(self, metrics: PerformanceMetrics, user: User = None, url: str = None):
        """Store metrics in database if model exists"""
        try:
            # Try to import and use PerformanceMetric model
            from faktury.models import PerformanceMetric
            
            PerformanceMetric.objects.create(
                user=user,
                url=url or '',
                page_load_time=metrics.page_load_time or 0,
                database_query_time=metrics.database_query_time or 0,
                cache_hit_ratio=metrics.cache_hit_ratio or 0,
                memory_usage=metrics.memory_usage or 0,
                cpu_usage=metrics.cpu_usage or 0,
                response_time=metrics.response_time or 0,
                timestamp=metrics.timestamp
            )
            
        except ImportError:
            # Model doesn't exist yet, skip database storage
            logger.debug("PerformanceMetric model not found, skipping database storage")
        except Exception as e:
            logger.error(f"Error storing metrics in database: {e}")
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate performance report for the last N hours"""
        try:
            # Get metrics from cache
            cache_keys = []
            current_time = int(time.time())
            start_time = current_time - (hours * 3600)
            
            # Collect recent metrics from cache
            metrics_data = []
            for timestamp in range(start_time, current_time, 300):  # Every 5 minutes
                cache_key = f"perf_metrics_{timestamp}"
                data = cache.get(cache_key)
                if data:
                    metrics_data.append(data)
            
            if not metrics_data:
                return {
                    'error': 'No performance data available',
                    'recommendations': ['Start monitoring to collect performance data']
                }
            
            # Analyze metrics
            response_times = [d['metrics']['response_time'] for d in metrics_data 
                            if d['metrics']['response_time']]
            db_times = [d['metrics']['database_query_time'] for d in metrics_data 
                       if d['metrics']['database_query_time']]
            cache_ratios = [d['metrics']['cache_hit_ratio'] for d in metrics_data 
                          if d['metrics']['cache_hit_ratio']]
            
            report = {
                'period_hours': hours,
                'total_requests': len(metrics_data),
                'performance_summary': {
                    'avg_response_time': statistics.mean(response_times) if response_times else 0,
                    'max_response_time': max(response_times) if response_times else 0,
                    'min_response_time': min(response_times) if response_times else 0,
                    'avg_db_time': statistics.mean(db_times) if db_times else 0,
                    'avg_cache_hit_ratio': statistics.mean(cache_ratios) if cache_ratios else 0,
                },
                'budget_compliance': self._check_budget_compliance(metrics_data),
                'recommendations': self._generate_recommendations(metrics_data),
                'timestamp': timezone.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {
                'error': str(e),
                'recommendations': ['Fix performance monitoring system']
            }
    
    def _check_budget_compliance(self, metrics_data: List[Dict]) -> Dict[str, Any]:
        """Check compliance with performance budgets"""
        compliance = {}
        
        for budget_name, budget_value in self.performance_budgets.items():
            violations = []
            
            for data in metrics_data:
                metric_value = data['metrics'].get(budget_name.replace('_', '_'), 0)
                if metric_value > budget_value:
                    violations.append({
                        'timestamp': data['metrics']['timestamp'],
                        'value': metric_value,
                        'budget': budget_value
                    })
            
            compliance[budget_name] = {
                'budget': budget_value,
                'violations': len(violations),
                'compliance_rate': (len(metrics_data) - len(violations)) / len(metrics_data) * 100 if metrics_data else 100,
                'worst_violation': max(violations, key=lambda x: x['value']) if violations else None
            }
        
        return compliance
    
    def _generate_recommendations(self, metrics_data: List[Dict]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if not metrics_data:
            return ["No data available for recommendations"]
        
        # Analyze response times
        response_times = [d['metrics']['response_time'] for d in metrics_data 
                         if d['metrics']['response_time']]
        if response_times:
            avg_response = statistics.mean(response_times)
            if avg_response > self.performance_budgets['page_load_time']:
                recommendations.append(
                    f"Average response time ({avg_response:.2f}s) exceeds budget "
                    f"({self.performance_budgets['page_load_time']}s)"
                )
        
        # Analyze database performance
        db_times = [d['metrics']['database_query_time'] for d in metrics_data 
                   if d['metrics']['database_query_time']]
        if db_times:
            avg_db_time = statistics.mean(db_times)
            if avg_db_time > self.performance_budgets['database_query_time']:
                recommendations.append(
                    f"Database query time ({avg_db_time:.2f}s) is high - consider query optimization"
                )
        
        # Analyze cache performance
        cache_ratios = [d['metrics']['cache_hit_ratio'] for d in metrics_data 
                       if d['metrics']['cache_hit_ratio']]
        if cache_ratios:
            avg_cache_ratio = statistics.mean(cache_ratios)
            if avg_cache_ratio < self.performance_budgets['cache_hit_ratio']:
                recommendations.append(
                    f"Cache hit ratio ({avg_cache_ratio:.1f}%) is low - review caching strategy"
                )
        
        # System resource recommendations
        memory_usage = [d['metrics']['memory_usage'] for d in metrics_data 
                       if d['metrics']['memory_usage']]
        if memory_usage:
            avg_memory = statistics.mean(memory_usage)
            if avg_memory > self.performance_budgets['memory_usage']:
                recommendations.append(
                    f"Memory usage ({avg_memory:.1f}%) is high - check for memory leaks"
                )
        
        if not recommendations:
            recommendations.append("Performance is within acceptable limits")
        
        return recommendations
    
    def optimize_database_queries(self) -> Dict[str, Any]:
        """Analyze and provide database optimization recommendations"""
        try:
            with connection.cursor() as cursor:
                # Check for missing indexes
                cursor.execute("""
                    SELECT schemaname, tablename, attname, n_distinct, correlation
                    FROM pg_stats
                    WHERE schemaname = 'public'
                    AND n_distinct > 100
                    ORDER BY n_distinct DESC
                    LIMIT 10;
                """)
                
                potential_indexes = cursor.fetchall()
                
                # Check for slow queries (if pg_stat_statements is available)
                try:
                    cursor.execute("""
                        SELECT query, calls, total_time, mean_time
                        FROM pg_stat_statements
                        WHERE mean_time > 100
                        ORDER BY mean_time DESC
                        LIMIT 5;
                    """)
                    slow_queries = cursor.fetchall()
                except Exception:
                    slow_queries = []
                
                return {
                    'potential_indexes': potential_indexes,
                    'slow_queries': slow_queries,
                    'recommendations': [
                        "Consider adding indexes for high-cardinality columns",
                        "Review and optimize slow queries",
                        "Use EXPLAIN ANALYZE to understand query execution plans"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error analyzing database queries: {e}")
            return {
                'error': str(e),
                'recommendations': ['Enable query analysis tools for better insights']
            }
    
    def implement_intelligent_caching(self) -> Dict[str, Any]:
        """Implement intelligent caching strategy"""
        caching_strategy = {
            'static_content': {
                'ttl': 86400,  # 24 hours
                'keys': ['css_files', 'js_files', 'images'],
                'strategy': 'long_term'
            },
            'user_data': {
                'ttl': 3600,  # 1 hour
                'keys': ['user_profile', 'user_preferences'],
                'strategy': 'medium_term'
            },
            'dynamic_content': {
                'ttl': 300,  # 5 minutes
                'keys': ['invoice_list', 'company_data'],
                'strategy': 'short_term'
            },
            'frequently_accessed': {
                'ttl': 1800,  # 30 minutes
                'keys': ['ocr_results', 'document_metadata'],
                'strategy': 'adaptive'
            }
        }
        
        recommendations = [
            "Implement cache warming for frequently accessed data",
            "Use cache tags for efficient invalidation",
            "Monitor cache hit ratios and adjust TTL values",
            "Consider using Redis for distributed caching",
            "Implement cache compression for large objects"
        ]
        
        return {
            'caching_strategy': caching_strategy,
            'recommendations': recommendations,
            'implementation_status': 'planned'
        }
    
    def add_performance_alerts(self) -> Dict[str, Any]:
        """Configure performance monitoring alerts"""
        alert_thresholds = {
            'response_time': {
                'warning': 2.0,  # 2 seconds
                'critical': 5.0,  # 5 seconds
                'action': 'Check server resources and optimize slow endpoints'
            },
            'database_query_time': {
                'warning': 0.3,  # 300ms
                'critical': 1.0,  # 1 second
                'action': 'Optimize database queries and check indexes'
            },
            'cache_hit_ratio': {
                'warning': 70.0,  # 70%
                'critical': 50.0,  # 50%
                'action': 'Review caching strategy and increase cache TTL'
            },
            'memory_usage': {
                'warning': 75.0,  # 75%
                'critical': 90.0,  # 90%
                'action': 'Check for memory leaks and optimize memory usage'
            },
            'error_rate': {
                'warning': 1.0,   # 1%
                'critical': 5.0,  # 5%
                'action': 'Investigate error causes and fix issues'
            }
        }
        
        return {
            'alert_thresholds': alert_thresholds,
            'notification_channels': ['email', 'slack', 'dashboard'],
            'recommendations': [
                "Set up automated alerts for performance degradation",
                "Create performance dashboards for real-time monitoring",
                "Implement escalation procedures for critical alerts"
            ]
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()