"""
Performance Monitoring Middleware
Automatically tracks performance metrics for all requests.
"""

import time
import logging
from typing import Optional
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from faktury.services.performance_monitor import performance_monitor

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to automatically track performance metrics for all requests.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Start performance monitoring for the request"""
        try:
            # Generate unique request ID
            request_id = f"req_{int(time.time() * 1000)}_{id(request)}"
            request._performance_request_id = request_id
            
            # Start monitoring
            performance_monitor.start_request_monitoring(request_id)
            
            # Store start time for additional metrics
            request._performance_start_time = time.time()
            
        except Exception as e:
            logger.error(f"Error starting performance monitoring: {e}")
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """End performance monitoring and collect metrics"""
        try:
            # Check if monitoring was started
            if not hasattr(request, '_performance_request_id'):
                return response
            
            request_id = request._performance_request_id
            
            # Get user if authenticated
            user = request.user if request.user.is_authenticated else None
            
            # Get URL
            url = request.build_absolute_uri()
            
            # End monitoring and collect metrics
            metrics = performance_monitor.end_request_monitoring(
                request_id=request_id,
                user=user,
                url=url
            )
            
            # Add response-specific metrics
            if hasattr(request, '_performance_start_time'):
                total_time = time.time() - request._performance_start_time
                metrics.page_load_time = total_time
            
            # Add response status to metrics
            if hasattr(metrics, 'raw_data'):
                metrics.raw_data.update({
                    'status_code': response.status_code,
                    'content_length': len(response.content) if hasattr(response, 'content') else 0,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'method': request.method,
                    'path': request.path,
                })
            
            # Log performance issues
            self._log_performance_issues(metrics, request, response)
            
        except Exception as e:
            logger.error(f"Error ending performance monitoring: {e}")
        
        return response
    
    def _log_performance_issues(self, metrics, request: HttpRequest, response: HttpResponse):
        """Log performance issues if thresholds are exceeded"""
        try:
            # Check response time
            if metrics.response_time and metrics.response_time > 3.0:  # 3 seconds
                logger.warning(
                    f"Slow response detected: {request.path} took {metrics.response_time:.2f}s"
                )
            
            # Check database query time
            if metrics.database_query_time and metrics.database_query_time > 0.5:  # 500ms
                logger.warning(
                    f"Slow database queries: {request.path} DB time {metrics.database_query_time:.2f}s"
                )
            
            # Check memory usage
            if metrics.memory_usage and metrics.memory_usage > 80:  # 80%
                logger.warning(
                    f"High memory usage: {request.path} memory at {metrics.memory_usage:.1f}%"
                )
            
            # Check for errors
            if response.status_code >= 500:
                logger.error(
                    f"Server error: {request.path} returned {response.status_code}"
                )
            
        except Exception as e:
            logger.error(f"Error logging performance issues: {e}")


class DatabaseQueryCountMiddleware(MiddlewareMixin):
    """
    Middleware to track database query count and identify N+1 problems.
    """
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Reset query count for the request"""
        from django.db import connection
        connection.queries_log.clear()
        request._db_query_start_count = len(connection.queries)
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Log database query statistics"""
        try:
            from django.db import connection
            
            if hasattr(request, '_db_query_start_count'):
                query_count = len(connection.queries) - request._db_query_start_count
                
                # Log excessive queries
                if query_count > 20:  # Threshold for too many queries
                    logger.warning(
                        f"High query count: {request.path} executed {query_count} queries"
                    )
                
                # Add query count to response headers in debug mode
                if hasattr(response, '__setitem__'):
                    response['X-DB-Query-Count'] = str(query_count)
        
        except Exception as e:
            logger.error(f"Error tracking database queries: {e}")
        
        return response


class CachePerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to track cache performance and hit ratios.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0
        }
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Initialize cache tracking for request"""
        request._cache_operations = {
            'hits': 0,
            'misses': 0,
            'sets': 0
        }
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Log cache performance statistics"""
        try:
            if hasattr(request, '_cache_operations'):
                cache_ops = request._cache_operations
                total_ops = sum(cache_ops.values())
                
                if total_ops > 0:
                    hit_ratio = (cache_ops['hits'] / total_ops) * 100
                    
                    # Log poor cache performance
                    if hit_ratio < 50 and total_ops > 5:  # Less than 50% hit ratio
                        logger.warning(
                            f"Poor cache performance: {request.path} hit ratio {hit_ratio:.1f}%"
                        )
                    
                    # Add cache stats to response headers in debug mode
                    if hasattr(response, '__setitem__'):
                        response['X-Cache-Hit-Ratio'] = f"{hit_ratio:.1f}%"
                        response['X-Cache-Operations'] = str(total_ops)
        
        except Exception as e:
            logger.error(f"Error tracking cache performance: {e}")
        
        return response


class PerformanceBudgetMiddleware(MiddlewareMixin):
    """
    Middleware to enforce performance budgets and alert on violations.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.performance_budgets = {
            'response_time': 3.0,      # 3 seconds
            'db_query_time': 0.5,      # 500ms
            'memory_usage': 80.0,      # 80%
            'query_count': 20,         # 20 queries
        }
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Check performance budgets and log violations"""
        try:
            violations = []
            
            # Check response time
            if hasattr(request, '_performance_start_time'):
                response_time = time.time() - request._performance_start_time
                if response_time > self.performance_budgets['response_time']:
                    violations.append(f"Response time: {response_time:.2f}s > {self.performance_budgets['response_time']}s")
            
            # Check database queries
            from django.db import connection
            if hasattr(request, '_db_query_start_count'):
                query_count = len(connection.queries) - request._db_query_start_count
                if query_count > self.performance_budgets['query_count']:
                    violations.append(f"Query count: {query_count} > {self.performance_budgets['query_count']}")
            
            # Log budget violations
            if violations:
                logger.warning(
                    f"Performance budget violations for {request.path}: {'; '.join(violations)}"
                )
                
                # Add violation headers in debug mode
                if hasattr(response, '__setitem__'):
                    response['X-Performance-Budget-Violations'] = str(len(violations))
        
        except Exception as e:
            logger.error(f"Error checking performance budgets: {e}")
        
        return response