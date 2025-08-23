"""
Custom throttling classes for OCR API endpoints.

This module provides rate limiting functionality for OCR-related API endpoints
to prevent abuse and ensure fair usage across users.
"""

import time
from django.core.cache import cache
from django.conf import settings
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.exceptions import Throttled


class OCRUploadThrottle(UserRateThrottle):
    """
    Throttle class for OCR upload endpoints.
    
    Limits uploads to 10 per minute per authenticated user to prevent
    system overload and ensure fair resource allocation.
    """
    scope = 'ocr_upload'
    rate = '10/min'
    
    def get_cache_key(self, request, view):
        """
        Generate cache key for rate limiting.
        
        Uses user ID to ensure per-user rate limiting.
        """
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            # For anonymous users, fall back to IP-based throttling
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def throttle_failure(self):
        """
        Called when throttle limit is exceeded.
        
        Raises a custom Throttled exception with retry timing information.
        """
        wait_time = self.wait()
        retry_after = int(wait_time) if wait_time else 60
        
        detail = (
            f"Upload rate limit exceeded. You can upload up to {self.num_requests} "
            f"files per {self.duration} seconds. Please try again in {retry_after} seconds."
        )
        
        raise Throttled(wait=wait_time, detail=detail)


class OCRAPIThrottle(UserRateThrottle):
    """
    General throttle class for OCR API endpoints.
    
    Provides higher limits for general API operations like status checking
    and result retrieval compared to upload operations.
    """
    scope = 'ocr_api'
    rate = '100/min'
    
    def get_cache_key(self, request, view):
        """
        Generate cache key for rate limiting.
        
        Uses user ID to ensure per-user rate limiting.
        """
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            # For anonymous users, fall back to IP-based throttling
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def throttle_failure(self):
        """
        Called when throttle limit is exceeded.
        
        Raises a custom Throttled exception with retry timing information.
        """
        wait_time = self.wait()
        retry_after = int(wait_time) if wait_time else 60
        
        detail = (
            f"API rate limit exceeded. You can make up to {self.num_requests} "
            f"requests per {self.duration} seconds. Please try again in {retry_after} seconds."
        )
        
        raise Throttled(wait=wait_time, detail=detail)


class OCRAnonymousThrottle(AnonRateThrottle):
    """
    Throttle class for anonymous users accessing OCR endpoints.
    
    Provides very limited access for unauthenticated users to prevent abuse.
    """
    scope = 'ocr_anon'
    rate = '5/min'
    
    def throttle_failure(self):
        """
        Called when throttle limit is exceeded.
        
        Raises a custom Throttled exception encouraging authentication.
        """
        wait_time = self.wait()
        retry_after = int(wait_time) if wait_time else 60
        
        detail = (
            f"Anonymous rate limit exceeded. Please authenticate to get higher limits. "
            f"Try again in {retry_after} seconds or log in for increased access."
        )
        
        raise Throttled(wait=wait_time, detail=detail)


class OCRBurstThrottle(UserRateThrottle):
    """
    Burst throttle for handling short-term spikes in OCR requests.
    
    Allows for brief bursts of activity while maintaining overall rate limits.
    """
    scope = 'ocr_burst'
    rate = '30/min'
    
    def get_cache_key(self, request, view):
        """Generate cache key for burst rate limiting."""
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def throttle_failure(self):
        """Handle burst throttle failures."""
        wait_time = self.wait()
        retry_after = int(wait_time) if wait_time else 60
        
        detail = (
            f"Burst rate limit exceeded. Please slow down your requests. "
            f"Try again in {retry_after} seconds."
        )
        
        raise Throttled(wait=wait_time, detail=detail)


def get_throttle_status(request, throttle_class):
    """
    Utility function to get current throttle status for a user.
    
    Args:
        request: Django request object
        throttle_class: Throttle class to check
        
    Returns:
        dict: Throttle status information including remaining requests and reset time
    """
    try:
        throttle = throttle_class()
        
        # Handle None request gracefully
        if request is None:
            now = time.time()
            return {
                'limit': throttle.num_requests,
                'remaining': throttle.num_requests,  # Full limit available for None request
                'reset_time': now + throttle.duration,
                'reset_in_seconds': throttle.duration,
                'duration': throttle.duration
            }
        
        # Get current usage from cache without consuming a request
        cache_key = throttle.get_cache_key(request, None)
        history = cache.get(cache_key, [])
        
        # Calculate remaining requests
        now = time.time()
        # Clean up old entries
        while history and history[-1] <= now - throttle.duration:
            history.pop()
        
        remaining = throttle.num_requests - len(history)
        
        # Calculate reset time
        if history:
            reset_time = history[-1] + throttle.duration
        else:
            reset_time = now + throttle.duration
        
        return {
            'limit': throttle.num_requests,
            'remaining': max(0, remaining),
            'reset_time': reset_time,
            'reset_in_seconds': max(0, int(reset_time - now)),
            'duration': throttle.duration
        }
    except Exception:
        # Return default values if anything goes wrong
        now = time.time()
        throttle = throttle_class()
        return {
            'limit': throttle.num_requests,
            'remaining': throttle.num_requests,
            'reset_time': now + throttle.duration,
            'reset_in_seconds': throttle.duration,
            'duration': throttle.duration
        }


def add_throttle_headers(response, request, throttle_classes):
    """
    Add rate limiting headers to API responses.
    
    Args:
        response: DRF Response object
        request: Django request object
        throttle_classes: List of throttle classes to check
    """
    for throttle_class in throttle_classes:
        try:
            status = get_throttle_status(request, throttle_class)
            scope = throttle_class.scope
            
            # Add standard rate limiting headers
            response[f'X-RateLimit-Limit-{scope}'] = status['limit']
            response[f'X-RateLimit-Remaining-{scope}'] = status['remaining']
            response[f'X-RateLimit-Reset-{scope}'] = int(status['reset_time'])
            
        except Exception:
            # Don't fail the request if throttle status check fails
            pass
    
    return response


class ThrottleStatusMixin:
    """
    Mixin to add throttle status information to API views.
    """
    throttle_classes_for_headers = []
    
    def finalize_response(self, request, response, *args, **kwargs):
        """Add throttle headers to response."""
        response = super().finalize_response(request, response, *args, **kwargs)
        
        # Add throttle headers if specified
        if self.throttle_classes_for_headers:
            response = add_throttle_headers(response, request, self.throttle_classes_for_headers)
        elif hasattr(self, 'throttle_classes') and self.throttle_classes:
            response = add_throttle_headers(response, request, self.throttle_classes)
        
        return response


def check_throttle_limits(request, throttle_classes):
    """
    Check if request would be throttled by any of the given throttle classes.
    
    Args:
        request: Django request object
        throttle_classes: List of throttle classes to check
        
    Returns:
        dict: Status information including whether request would be throttled
    """
    results = {}
    
    for throttle_class in throttle_classes:
        throttle = throttle_class()
        allowed = throttle.allow_request(request, None)
        
        status = get_throttle_status(request, throttle_class)
        status['allowed'] = allowed
        
        if not allowed:
            status['wait_time'] = throttle.wait()
        
        results[throttle_class.scope] = status
    
    return results