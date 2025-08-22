"""
Cache utilities for improved performance
"""
from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def get_cache_key(prefix, *args, **kwargs):
    """
    Generate a cache key based on prefix and arguments
    """
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


def cache_user_stats(user, timeout=300):
    """
    Cache user statistics for dashboard
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = get_cache_key('user_stats', user.id)
            result = cache.get(cache_key)
            
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_user_cache(user):
    """
    Invalidate all cache for a specific user
    """
    patterns = [
        f"user_stats:{user.id}:*",
        f"user_invoices:{user.id}:*",
        f"user_contractors:{user.id}:*",
        f"user_products:{user.id}:*",
    ]
    
    for pattern in patterns:
        try:
            cache.delete_pattern(pattern)
        except AttributeError:
            # If cache backend doesn't support delete_pattern
            pass


class CachedQuerySet:
    """
    Wrapper for caching querysets
    """
    def __init__(self, queryset, cache_key, timeout=300):
        self.queryset = queryset
        self.cache_key = cache_key
        self.timeout = timeout
    
    def get_cached_result(self):
        """
        Get cached result or execute query
        """
        result = cache.get(self.cache_key)
        
        if result is None:
            result = list(self.queryset)
            cache.set(self.cache_key, result, self.timeout)
        
        return result


def cache_frequently_accessed_data():
    """
    Pre-cache frequently accessed data
    """
    # This can be called from management commands or celery tasks
    pass
