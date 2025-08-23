"""
Schema preprocessing and postprocessing hooks for drf-spectacular.
"""
import logging
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

logger = logging.getLogger(__name__)


def preprocess_schema_hook(endpoints):
    """
    Preprocess the API endpoints before schema generation.
    
    This hook allows us to modify endpoints, add custom metadata,
    or filter endpoints based on various criteria.
    """
    # For now, just return the endpoints as-is
    # This hook is called during endpoint discovery, not schema generation
    return endpoints


def preprocess_schema_result_hook(result, generator, request, public):
    """
    Preprocess the OpenAPI schema result before final generation.
    
    This hook allows us to modify the schema structure, add custom
    components, or filter endpoints based on user permissions.
    """
    try:
        # Add custom security schemes
        if 'components' not in result:
            result['components'] = {}
        
        if 'securitySchemes' not in result['components']:
            result['components']['securitySchemes'] = {}
        
        # Add JWT Bearer authentication
        result['components']['securitySchemes']['jwtAuth'] = {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'JWT token authentication. Obtain token from /api/v1/auth/token/ endpoint.'
        }
        
        # Add session authentication
        result['components']['securitySchemes']['sessionAuth'] = {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'sessionid',
            'description': 'Django session authentication using session cookies.'
        }
        
        # Add token authentication
        result['components']['securitySchemes']['tokenAuth'] = {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Token authentication. Use format: "Token <your-token>"'
        }
        
        # Add global security requirements
        result['security'] = [
            {'jwtAuth': []},
            {'sessionAuth': []},
            {'tokenAuth': []}
        ]
        
        # Add custom response schemas
        if 'schemas' not in result['components']:
            result['components']['schemas'] = {}
        
        # Add standard API response schema
        result['components']['schemas']['APIResponse'] = {
            'type': 'object',
            'properties': {
                'success': {
                    'type': 'boolean',
                    'description': 'Indicates if the operation was successful'
                },
                'data': {
                    'type': 'object',
                    'description': 'Response data (varies by endpoint)',
                    'nullable': True
                },
                'message': {
                    'type': 'string',
                    'description': 'Human-readable message about the operation',
                    'nullable': True
                },
                'timestamp': {
                    'type': 'string',
                    'format': 'date-time',
                    'description': 'ISO 8601 timestamp of the response'
                }
            },
            'required': ['success', 'timestamp']
        }
        
        # Add error response schema
        result['components']['schemas']['APIErrorResponse'] = {
            'type': 'object',
            'properties': {
                'success': {
                    'type': 'boolean',
                    'enum': [False],
                    'description': 'Always false for error responses'
                },
                'error': {
                    'type': 'object',
                    'properties': {
                        'code': {
                            'type': 'string',
                            'description': 'Machine-readable error code'
                        },
                        'message': {
                            'type': 'string',
                            'description': 'Human-readable error message'
                        },
                        'details': {
                            'type': 'object',
                            'description': 'Additional error details (field-specific errors, etc.)',
                            'nullable': True
                        }
                    },
                    'required': ['code', 'message']
                },
                'timestamp': {
                    'type': 'string',
                    'format': 'date-time',
                    'description': 'ISO 8601 timestamp of the response'
                }
            },
            'required': ['success', 'error', 'timestamp']
        }
        
        # Add pagination schema
        result['components']['schemas']['PaginationInfo'] = {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'description': 'Total number of items'
                },
                'page': {
                    'type': 'integer',
                    'description': 'Current page number'
                },
                'page_size': {
                    'type': 'integer',
                    'description': 'Number of items per page'
                },
                'total_pages': {
                    'type': 'integer',
                    'description': 'Total number of pages'
                },
                'has_next': {
                    'type': 'boolean',
                    'description': 'Whether there is a next page'
                },
                'has_previous': {
                    'type': 'boolean',
                    'description': 'Whether there is a previous page'
                }
            },
            'required': ['count', 'page', 'page_size', 'total_pages', 'has_next', 'has_previous']
        }
        
        # Add file upload schema
        result['components']['schemas']['FileUpload'] = {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Document file to upload (PDF, JPEG, PNG). Maximum size: 10MB.'
                }
            },
            'required': ['file']
        }
        
        logger.info("Schema preprocessing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in schema preprocessing: {str(e)}", exc_info=True)
    
    return result


def postprocess_schema_hook(result, generator, request, public):
    """
    Postprocess the OpenAPI schema after generation.
    
    This hook allows us to make final modifications to the generated schema,
    such as adding examples, modifying descriptions, or cleaning up the structure.
    """
    try:
        # Add examples to common schemas
        if 'components' in result and 'schemas' in result['components']:
            schemas = result['components']['schemas']
            
            # Add example to APIResponse
            if 'APIResponse' in schemas:
                schemas['APIResponse']['example'] = {
                    'success': True,
                    'data': {
                        'task_id': 'abc123-def456-ghi789',
                        'document_id': 42,
                        'estimated_processing_time': 30
                    },
                    'message': 'File uploaded successfully and queued for processing',
                    'timestamp': '2025-08-23T10:30:00Z'
                }
            
            # Add example to APIErrorResponse
            if 'APIErrorResponse' in schemas:
                schemas['APIErrorResponse']['example'] = {
                    'success': False,
                    'error': {
                        'code': 'FILE_SIZE_EXCEEDED',
                        'message': 'File size (15.2MB) exceeds maximum allowed size (10.0MB)',
                        'details': {
                            'file_size': 15925248,
                            'max_size': 10485760
                        }
                    },
                    'timestamp': '2025-08-23T10:30:00Z'
                }
        
        # Add common response examples to endpoints
        if 'paths' in result:
            for path, methods in result['paths'].items():
                for method, operation in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                        # Add common error responses
                        if 'responses' not in operation:
                            operation['responses'] = {}
                        
                        # Add 401 Unauthorized response
                        if '401' not in operation['responses']:
                            operation['responses']['401'] = {
                                'description': 'Authentication credentials were not provided or are invalid',
                                'content': {
                                    'application/json': {
                                        'schema': {'$ref': '#/components/schemas/APIErrorResponse'},
                                        'example': {
                                            'success': False,
                                            'error': {
                                                'code': 'AUTHENTICATION_REQUIRED',
                                                'message': 'Authentication credentials were not provided'
                                            },
                                            'timestamp': '2025-08-23T10:30:00Z'
                                        }
                                    }
                                }
                            }
                        
                        # Add 403 Forbidden response for authenticated endpoints
                        if '403' not in operation['responses'] and path.startswith('/api/'):
                            operation['responses']['403'] = {
                                'description': 'Permission denied or rate limit exceeded',
                                'content': {
                                    'application/json': {
                                        'schema': {'$ref': '#/components/schemas/APIErrorResponse'},
                                        'example': {
                                            'success': False,
                                            'error': {
                                                'code': 'PERMISSION_DENIED',
                                                'message': 'You do not have permission to perform this action'
                                            },
                                            'timestamp': '2025-08-23T10:30:00Z'
                                        }
                                    }
                                }
                            }
                        
                        # Add 429 Rate Limited response for API endpoints
                        if '429' not in operation['responses'] and '/api/ocr/' in path:
                            operation['responses']['429'] = {
                                'description': 'Rate limit exceeded',
                                'content': {
                                    'application/json': {
                                        'schema': {'$ref': '#/components/schemas/APIErrorResponse'},
                                        'example': {
                                            'success': False,
                                            'error': {
                                                'code': 'RATE_LIMIT_EXCEEDED',
                                                'message': 'Rate limit exceeded. Try again in 60 seconds.'
                                            },
                                            'timestamp': '2025-08-23T10:30:00Z'
                                        }
                                    }
                                },
                                'headers': {
                                    'Retry-After': {
                                        'description': 'Number of seconds to wait before retrying',
                                        'schema': {
                                            'type': 'integer'
                                        }
                                    }
                                }
                            }
        
        # Clean up and organize tags
        if 'tags' in result:
            # Sort tags alphabetically
            result['tags'] = sorted(result['tags'], key=lambda x: x['name'])
        
        logger.info("Schema postprocessing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in schema postprocessing: {str(e)}", exc_info=True)
    
    return result


# Custom field extensions for better schema generation
@extend_schema_field(serializers.CharField)
def task_id_field():
    """Custom field for Celery task IDs."""
    return {
        'type': 'string',
        'format': 'uuid',
        'description': 'Celery task ID for tracking processing status',
        'example': 'abc123-def456-ghi789'
    }


@extend_schema_field(serializers.FloatField)
def confidence_score_field():
    """Custom field for confidence scores."""
    return {
        'type': 'number',
        'format': 'float',
        'minimum': 0.0,
        'maximum': 100.0,
        'description': 'Confidence score as a percentage (0-100)',
        'example': 95.5
    }


@extend_schema_field(serializers.JSONField)
def extracted_data_field():
    """Custom field for OCR extracted data."""
    return {
        'type': 'object',
        'description': 'Extracted data from OCR processing with confidence scores',
        'example': {
            'numer_faktury': {
                'value': 'FV/2025/001',
                'confidence': 98.5
            },
            'data_wystawienia': {
                'value': '2025-08-20',
                'confidence': 95.2
            },
            'sprzedawca': {
                'nazwa': {
                    'value': 'Example Sp. z o.o.',
                    'confidence': 97.8
                },
                'nip': {
                    'value': '1234567890',
                    'confidence': 92.1
                }
            },
            'suma_brutto': {
                'value': 1230.00,
                'confidence': 96.7
            }
        }
    }