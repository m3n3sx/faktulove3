# OCR API Rate Limiting and Throttling

This document explains the rate limiting and throttling system implemented for the OCR REST API.

## Overview

The throttling system provides rate limiting functionality to prevent abuse and ensure fair usage across users. It uses Redis as the backend for distributed rate limiting and provides clear error messages with retry timing information.

## Throttle Classes

### OCRUploadThrottle
- **Rate Limit**: 10 uploads per minute per user
- **Purpose**: Limits file uploads to prevent system overload
- **Scope**: `ocr_upload`
- **Usage**: Applied to file upload endpoints

### OCRAPIThrottle
- **Rate Limit**: 100 requests per minute per user
- **Purpose**: General API rate limiting for status checks and result retrieval
- **Scope**: `ocr_api`
- **Usage**: Applied to general API endpoints

### OCRAnonymousThrottle
- **Rate Limit**: 5 requests per minute per IP
- **Purpose**: Very limited access for unauthenticated users
- **Scope**: `ocr_anon`
- **Usage**: Applied to endpoints accessible by anonymous users

### OCRBurstThrottle
- **Rate Limit**: 30 requests per minute per user
- **Purpose**: Allows short-term spikes in activity
- **Scope**: `ocr_burst`
- **Usage**: Can be combined with other throttles for burst handling

## Configuration

### Django Settings

The throttling system is configured in `faktulove/settings.py`:

```python
# Redis Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
    }
}

# REST Framework Throttle Rates
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'ocr_upload': '10/min',
        'ocr_api': '100/min',
        'ocr_anon': '5/min',
        'ocr_burst': '30/min',
    },
}
```

### Requirements

Add to `requirements.txt`:
```
django-redis>=5.4.0
```

## Usage in Views

### Basic Usage

```python
from rest_framework.views import APIView
from faktury.api.throttling import OCRUploadThrottle, OCRAPIThrottle

class OCRUploadView(APIView):
    throttle_classes = [OCRUploadThrottle]
    
    def post(self, request):
        # Upload logic here
        pass

class OCRStatusView(APIView):
    throttle_classes = [OCRAPIThrottle]
    
    def get(self, request, task_id):
        # Status check logic here
        pass
```

### Using the Throttle Status Mixin

```python
from faktury.api.throttling import ThrottleStatusMixin, OCRUploadThrottle

class OCRUploadView(ThrottleStatusMixin, APIView):
    throttle_classes = [OCRUploadThrottle]
    throttle_classes_for_headers = [OCRUploadThrottle]
    
    def post(self, request):
        # Upload logic here
        # Response will automatically include throttle headers
        pass
```

## Utility Functions

### get_throttle_status()

Get current throttle status for a user:

```python
from faktury.api.throttling import get_throttle_status, OCRUploadThrottle

status = get_throttle_status(request, OCRUploadThrottle)
# Returns:
# {
#     'limit': 10,
#     'remaining': 7,
#     'reset_time': 1640995200.0,
#     'reset_in_seconds': 45,
#     'duration': 60
# }
```

### add_throttle_headers()

Add rate limiting headers to responses:

```python
from faktury.api.throttling import add_throttle_headers, OCRUploadThrottle

response = Response({'data': 'example'})
response = add_throttle_headers(response, request, [OCRUploadThrottle])
# Adds headers like:
# X-RateLimit-Limit-ocr_upload: 10
# X-RateLimit-Remaining-ocr_upload: 7
# X-RateLimit-Reset-ocr_upload: 1640995200
```

### check_throttle_limits()

Check multiple throttle limits at once:

```python
from faktury.api.throttling import check_throttle_limits, OCRUploadThrottle, OCRAPIThrottle

results = check_throttle_limits(request, [OCRUploadThrottle, OCRAPIThrottle])
# Returns status for each throttle class
```

## Error Handling

When rate limits are exceeded, the system returns:

- **HTTP Status**: 429 Too Many Requests
- **Error Format**:
```json
{
    "success": false,
    "error": {
        "code": "RATE_LIMITED",
        "message": "Upload rate limit exceeded. You can upload up to 10 files per 60 seconds. Please try again in 45 seconds.",
        "details": {
            "retry_after": 45,
            "retry_after_seconds": 45
        }
    },
    "timestamp": "2025-08-23T10:30:00Z"
}
```

## Response Headers

The system adds standard rate limiting headers to responses:

- `X-RateLimit-Limit-{scope}`: The rate limit ceiling for the given scope
- `X-RateLimit-Remaining-{scope}`: The number of requests left for the time window
- `X-RateLimit-Reset-{scope}`: The time at which the rate limit window resets (Unix timestamp)

## Testing

Run the throttling tests:

```bash
python manage.py test faktury.tests.test_api_throttling
```

The test suite includes:
- Rate limit enforcement tests
- Error message validation
- Header addition tests
- Utility function tests
- Error handling tests

## Production Considerations

1. **Redis Configuration**: Ensure Redis is properly configured and monitored in production
2. **Rate Limit Tuning**: Adjust rate limits based on actual usage patterns
3. **Monitoring**: Monitor throttle hit rates and adjust limits as needed
4. **Logging**: All throttle events are logged for analysis
5. **Graceful Degradation**: The system handles Redis failures gracefully

## Troubleshooting

### Common Issues

1. **Redis Connection Errors**: Check Redis server status and connection settings
2. **Rate Limits Too Low**: Monitor logs for frequent throttling and adjust limits
3. **Cache Key Conflicts**: Ensure proper cache key prefixing in settings

### Debug Mode

In development, you can disable throttling by setting:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {},
}
```

## Security Considerations

1. **IP-based Throttling**: Anonymous users are throttled by IP address
2. **User-based Throttling**: Authenticated users are throttled by user ID
3. **Bypass Protection**: Rate limits cannot be easily bypassed
4. **DoS Protection**: Helps protect against denial-of-service attacks