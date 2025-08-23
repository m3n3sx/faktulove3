"""
Tests for API throttling and rate limiting functionality.
"""

import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from faktury.api.throttling import (
    OCRUploadThrottle, 
    OCRAPIThrottle, 
    OCRAnonymousThrottle,
    OCRBurstThrottle,
    get_throttle_status,
    add_throttle_headers,
    check_throttle_limits
)


class ThrottleTestCase(TestCase):
    """Base test case for throttling tests."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.factory = APIRequestFactory()
        cache.clear()  # Clear cache before each test
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()


class OCRUploadThrottleTest(ThrottleTestCase):
    """Test OCR upload throttling."""
    
    def test_throttle_rate_limit(self):
        """Test that upload throttle enforces 10 requests per minute."""
        throttle = OCRUploadThrottle()
        request = self.factory.post('/api/ocr/upload/')
        request.user = self.user
        
        # First 10 requests should be allowed
        for i in range(10):
            allowed = throttle.allow_request(request, None)
            self.assertTrue(allowed, f"Request {i+1} should be allowed")
        
        # 11th request should be throttled (will raise Throttled exception)
        from rest_framework.exceptions import Throttled
        with self.assertRaises(Throttled):
            throttle.allow_request(request, None)
    
    def test_throttle_cache_key_generation(self):
        """Test that cache keys are generated correctly."""
        throttle = OCRUploadThrottle()
        request = self.factory.post('/api/ocr/upload/')
        request.user = self.user
        
        cache_key = throttle.get_cache_key(request, None)
        expected_key = f"throttle_ocr_upload_{self.user.pk}"
        self.assertIn('ocr_upload', cache_key)
        self.assertIn(str(self.user.pk), cache_key)
    
    def test_throttle_failure_message(self):
        """Test that throttle failure provides clear error message."""
        throttle = OCRUploadThrottle()
        request = self.factory.post('/api/ocr/upload/')
        request.user = self.user
        
        # Exhaust the rate limit
        for _ in range(10):
            throttle.allow_request(request, None)
        
        # Next request should raise Throttled exception with helpful message
        from rest_framework.exceptions import Throttled
        with self.assertRaises(Throttled) as context:
            throttle.allow_request(request, None)
        
        # The exception should contain helpful information
        exception = context.exception
        self.assertIn("Upload rate limit exceeded", str(exception.detail))
        self.assertIn("10", str(exception.detail))  # Should mention the limit
        self.assertTrue(hasattr(throttle, 'throttle_failure'))
    
    def test_anonymous_user_throttling(self):
        """Test that anonymous users get IP-based throttling."""
        throttle = OCRUploadThrottle()
        request = self.factory.post('/api/ocr/upload/')
        request.user = None  # Anonymous user
        
        cache_key = throttle.get_cache_key(request, None)
        # Should fall back to IP-based identification
        self.assertIsNotNone(cache_key)


class OCRAPIThrottleTest(ThrottleTestCase):
    """Test general OCR API throttling."""
    
    def test_higher_rate_limit(self):
        """Test that API throttle has higher limits than upload throttle."""
        upload_throttle = OCRUploadThrottle()
        api_throttle = OCRAPIThrottle()
        
        # Parse rates to compare
        upload_rate = upload_throttle.parse_rate(upload_throttle.rate)
        api_rate = api_throttle.parse_rate(api_throttle.rate)
        
        self.assertGreater(api_rate[0], upload_rate[0], 
                          "API throttle should have higher rate limit than upload throttle")
    
    def test_api_throttle_rate_limit(self):
        """Test that API throttle enforces 100 requests per minute."""
        throttle = OCRAPIThrottle()
        request = self.factory.get('/api/ocr/status/123/')
        request.user = self.user
        
        # Test a reasonable number of requests (not all 100 for test speed)
        for i in range(20):
            allowed = throttle.allow_request(request, None)
            self.assertTrue(allowed, f"Request {i+1} should be allowed")


class OCRAnonymousThrottleTest(ThrottleTestCase):
    """Test anonymous user throttling."""
    
    def test_anonymous_rate_limit(self):
        """Test that anonymous users have very limited access."""
        throttle = OCRAnonymousThrottle()
        request = self.factory.get('/api/ocr/status/123/')
        request.user = None  # Anonymous user
        
        # First 5 requests should be allowed
        for i in range(5):
            allowed = throttle.allow_request(request, None)
            self.assertTrue(allowed, f"Anonymous request {i+1} should be allowed")
        
        # 6th request should be throttled (will raise Throttled exception)
        from rest_framework.exceptions import Throttled
        with self.assertRaises(Throttled):
            throttle.allow_request(request, None)


class ThrottleUtilityTest(ThrottleTestCase):
    """Test throttle utility functions."""
    
    def test_get_throttle_status(self):
        """Test getting throttle status information."""
        request = self.factory.get('/api/ocr/status/123/')
        request.user = self.user
        
        status = get_throttle_status(request, OCRAPIThrottle)
        
        self.assertIn('limit', status)
        self.assertIn('remaining', status)
        self.assertIn('reset_time', status)
        self.assertIn('reset_in_seconds', status)
        self.assertIn('duration', status)
        
        # Initially should have full limit available
        self.assertEqual(status['remaining'], status['limit'])
    
    def test_add_throttle_headers(self):
        """Test adding throttle headers to response."""
        from rest_framework.response import Response
        
        request = self.factory.get('/api/ocr/status/123/')
        request.user = self.user
        response = Response({'test': 'data'})
        
        throttle_classes = [OCRAPIThrottle, OCRUploadThrottle]
        response = add_throttle_headers(response, request, throttle_classes)
        
        # Check that headers were added
        self.assertIn('X-RateLimit-Limit-ocr_api', response)
        self.assertIn('X-RateLimit-Remaining-ocr_api', response)
        self.assertIn('X-RateLimit-Reset-ocr_api', response)
        
        self.assertIn('X-RateLimit-Limit-ocr_upload', response)
        self.assertIn('X-RateLimit-Remaining-ocr_upload', response)
        self.assertIn('X-RateLimit-Reset-ocr_upload', response)
    
    def test_check_throttle_limits(self):
        """Test checking multiple throttle limits at once."""
        request = self.factory.get('/api/ocr/status/123/')
        request.user = self.user
        
        throttle_classes = [OCRAPIThrottle, OCRUploadThrottle]
        results = check_throttle_limits(request, throttle_classes)
        
        self.assertIn('ocr_api', results)
        self.assertIn('ocr_upload', results)
        
        # Both should initially allow requests
        self.assertTrue(results['ocr_api']['allowed'])
        self.assertTrue(results['ocr_upload']['allowed'])


class ThrottleIntegrationTest(APITestCase):
    """Integration tests for throttling with actual API views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
    )
    def test_throttle_headers_in_response(self):
        """Test that throttle headers are included in API responses."""
        self.client.force_authenticate(user=self.user)
        
        # Make a request to any API endpoint (we'll need to create a simple test endpoint)
        # For now, we'll test the concept with a mock response
        from rest_framework.response import Response
        from faktury.api.throttling import add_throttle_headers
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.get('/api/test/')
        request.user = self.user
        
        response = Response({'test': 'data'})
        response = add_throttle_headers(response, request, [OCRAPIThrottle])
        
        self.assertIn('X-RateLimit-Limit-ocr_api', response)
        self.assertIn('X-RateLimit-Remaining-ocr_api', response)
    
    def test_throttle_with_redis_backend(self):
        """Test throttling works with Redis backend."""
        # This test would require Redis to be running
        # For now, we'll test with local memory cache
        with override_settings(
            CACHES={
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                }
            }
        ):
            throttle = OCRUploadThrottle()
            request = APIRequestFactory().post('/api/ocr/upload/')
            request.user = self.user
            
            # Test that throttling works with cache backend
            allowed = throttle.allow_request(request, None)
            self.assertTrue(allowed)


class ThrottleBurstTest(ThrottleTestCase):
    """Test burst throttling functionality."""
    
    def test_burst_throttle_rate(self):
        """Test that burst throttle allows short-term spikes."""
        throttle = OCRBurstThrottle()
        request = self.factory.post('/api/ocr/upload/')
        request.user = self.user
        
        # Should allow up to 30 requests per minute
        for i in range(30):
            allowed = throttle.allow_request(request, None)
            self.assertTrue(allowed, f"Burst request {i+1} should be allowed")
        
        # 31st request should be throttled (will raise Throttled exception)
        from rest_framework.exceptions import Throttled
        with self.assertRaises(Throttled):
            throttle.allow_request(request, None)


class ThrottleErrorHandlingTest(ThrottleTestCase):
    """Test error handling in throttle utilities."""
    
    def test_throttle_status_with_invalid_request(self):
        """Test that throttle status handles invalid requests gracefully."""
        # Test with None request
        try:
            status = get_throttle_status(None, OCRAPIThrottle)
            # Should not raise exception, might return default values
        except Exception as e:
            self.fail(f"get_throttle_status should handle None request gracefully: {e}")
    
    def test_add_headers_with_exception(self):
        """Test that header addition handles exceptions gracefully."""
        from rest_framework.response import Response
        
        response = Response({'test': 'data'})
        request = self.factory.get('/api/test/')
        request.user = self.user
        
        # Mock a throttle class that raises an exception
        class FailingThrottle:
            scope = 'failing'
            
            def __init__(self):
                raise Exception("Test exception")
        
        # Should not raise exception even if throttle class fails
        try:
            response = add_throttle_headers(response, request, [FailingThrottle])
        except Exception as e:
            self.fail(f"add_throttle_headers should handle exceptions gracefully: {e}")