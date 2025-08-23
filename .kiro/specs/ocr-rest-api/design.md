# Design Document

## Overview

The OCR REST API system will provide a comprehensive RESTful interface for the React frontend to interact with the OCR document processing pipeline. The API will be built using Django REST Framework (DRF) and will handle file uploads, asynchronous processing with Celery, status tracking, result retrieval, and manual validation workflows.

The system leverages the existing OCR infrastructure including DocumentUpload and OCRResult models, Celery task processing, and the status synchronization service. The API will provide secure, rate-limited endpoints with consistent JSON responses and comprehensive error handling.

## Architecture

### API Layer Architecture
```
React Frontend → Django REST API → Business Logic → Celery Tasks → OCR Services
     ↓              ↓                    ↓              ↓            ↓
  HTTP/JSON    DRF Serializers    Service Layer    Async Queue   Document AI
     ↓              ↓                    ↓              ↓            ↓
  CORS/Auth    Validation/Perms   Database ORM    Redis/Results  Google Cloud
```

### Request/Response Flow
1. **Upload Flow**: POST /api/ocr/upload/ → File validation → Celery task → task_id response
2. **Status Flow**: GET /api/ocr/status/<task_id>/ → Status check → Progress/ETA response
3. **Results Flow**: GET /api/ocr/results/ → Query filtering → Paginated results
4. **Detail Flow**: GET /api/ocr/result/<id>/ → Permission check → Detailed result
5. **Validation Flow**: POST /api/ocr/validate/<id>/ → Data validation → Update result

### Security Architecture
- **Authentication**: Django session-based auth + JWT tokens for API
- **Authorization**: User-based permissions (users can only access their own data)
- **Rate Limiting**: Django-ratelimit with Redis backend
- **CSRF Protection**: DRF CSRF handling for session auth
- **File Validation**: MIME type validation, size limits, malware scanning

## Components and Interfaces

### 1. API Views (faktury/api/views.py)

**OCRUploadAPIView**
- Handles file upload and validation
- Creates DocumentUpload record
- Queues Celery task for processing
- Returns task_id for tracking

**OCRStatusAPIView**
- Provides real-time status updates
- Calculates progress percentage
- Estimates completion time
- Handles task not found scenarios

**OCRResultsListAPIView**
- Lists user's OCR results with pagination
- Supports filtering by date, confidence, status
- Includes metadata for frontend pagination
- Optimized queries with select_related/prefetch_related

**OCRResultDetailAPIView**
- Returns detailed OCR result with confidence scores
- Includes links to generated Faktura if exists
- Highlights fields requiring manual review
- Provides structured data for frontend forms

**OCRValidationAPIView**
- Accepts manual corrections from users
- Updates OCR result with validated data
- Recalculates confidence scores
- Triggers Faktura creation if applicable

### 2. Serializers (faktury/api/serializers.py)

**DocumentUploadSerializer**
- Validates file uploads (size, type, content)
- Handles file storage and metadata extraction
- Provides clean data for DocumentUpload creation

**OCRResultListSerializer**
- Lightweight serializer for list views
- Includes essential fields and computed properties
- Optimized for performance with minimal queries

**OCRResultDetailSerializer**
- Comprehensive serializer for detail views
- Includes all extracted data with confidence scores
- Nested serializers for related objects (Faktura, etc.)

**OCRValidationSerializer**
- Validates manual corrections from users
- Handles field-specific validation rules
- Supports partial updates for individual fields

**TaskStatusSerializer**
- Serializes Celery task status information
- Includes progress, ETA, and error details
- Handles different task states consistently

### 3. Permissions (faktury/api/permissions.py)

**IsOwnerOrReadOnly**
- Ensures users can only access their own OCR results
- Allows read-only access for staff/admin users
- Handles edge cases for shared documents

**OCRUploadPermission**
- Validates user has active company profile
- Checks upload quotas and limits
- Ensures user is authenticated and verified

### 4. Rate Limiting (faktury/api/throttling.py)

**OCRUploadThrottle**
- Limits uploads to 10 per minute per user
- Uses Redis for distributed rate limiting
- Provides clear error messages with retry timing

**OCRAPIThrottle**
- General API rate limiting for other endpoints
- Higher limits for status checking and results retrieval
- Configurable per-user and per-IP limits

### 5. File Handling Service Enhancement

**Enhanced FileUploadService**
- Validates file types using python-magic
- Implements virus scanning integration
- Handles file storage with proper naming
- Generates secure file URLs for processing

## Data Models

### API Response Models

**Standard API Response Format**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2025-08-23T10:30:00Z"
}
```

**Error Response Format**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file format",
    "details": {
      "file": ["Only PDF, JPG, and PNG files are allowed"]
    }
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

### Enhanced Model Methods

**DocumentUpload API Extensions**
```python
class DocumentUpload(models.Model):
    # Existing fields...
    
    def to_api_dict(self):
        """Convert to API-friendly dictionary"""
        
    def get_task_id(self):
        """Get associated Celery task ID"""
        
    def get_api_status(self):
        """Get status formatted for API responses"""
```

**OCRResult API Extensions**
```python
class OCRResult(models.Model):
    # Existing fields...
    
    def to_api_dict(self, include_sensitive=False):
        """Convert to API-friendly dictionary"""
        
    def get_validation_fields(self):
        """Get fields that can be manually validated"""
        
    def apply_manual_corrections(self, corrections):
        """Apply user corrections and update confidence"""
```

## Error Handling

### HTTP Status Code Strategy
- **200 OK**: Successful operations
- **201 Created**: Successful uploads and creations
- **400 Bad Request**: Validation errors, invalid data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Permission denied, rate limited
- **404 Not Found**: Resource not found
- **413 Payload Too Large**: File size exceeded
- **415 Unsupported Media Type**: Invalid file type
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server errors

### Error Response Consistency
All error responses follow the standard format with:
- Clear error codes for programmatic handling
- Human-readable error messages
- Field-specific validation errors
- Suggested actions for resolution

### Logging Strategy
- **Request Logging**: All API requests with user, endpoint, and timing
- **Error Logging**: Detailed error information without sensitive data
- **Performance Logging**: Slow queries and processing times
- **Security Logging**: Authentication failures and suspicious activity

## Testing Strategy

### Unit Tests
- **Serializer Tests**: Validation logic and data transformation
- **View Tests**: HTTP methods, permissions, and response formats
- **Permission Tests**: Access control and ownership validation
- **Rate Limiting Tests**: Throttling behavior and limits

### Integration Tests
- **End-to-End API Tests**: Complete workflows from upload to validation
- **Celery Integration Tests**: Task queuing and status updates
- **File Upload Tests**: Various file types and sizes
- **Error Scenario Tests**: Network failures, invalid data, etc.

### Performance Tests
- **Load Testing**: API performance under concurrent requests
- **File Upload Performance**: Large file handling and timeouts
- **Database Query Optimization**: N+1 queries and slow operations
- **Rate Limiting Performance**: Throttling accuracy and overhead

### Security Tests
- **Authentication Tests**: Token validation and session handling
- **Authorization Tests**: User isolation and permission enforcement
- **File Security Tests**: Malicious file detection and handling
- **Rate Limiting Security**: Bypass attempts and abuse prevention

## API Endpoints Specification

### 1. POST /api/ocr/upload/
**Purpose**: Upload document for OCR processing

**Request**:
```json
{
  "file": "<multipart file>",
  "filename": "invoice.pdf"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "task_id": "abc123-def456-ghi789",
    "document_id": 42,
    "estimated_processing_time": 30
  }
}
```

### 2. GET /api/ocr/status/<task_id>/
**Purpose**: Get processing status and progress

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "processing",
    "progress": 65,
    "eta_seconds": 15,
    "message": "Extracting invoice data..."
  }
}
```

### 3. GET /api/ocr/results/
**Purpose**: List user's OCR results with filtering

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)
- `date_from`: Filter from date (YYYY-MM-DD)
- `date_to`: Filter to date (YYYY-MM-DD)
- `min_confidence`: Minimum confidence score (0-100)
- `status`: Processing status filter
- `search`: Search in filename or extracted data

**Response**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 123,
        "filename": "invoice_001.pdf",
        "upload_date": "2025-08-23T10:00:00Z",
        "status": "completed",
        "confidence_score": 95.5,
        "has_faktura": true,
        "needs_review": false
      }
    ],
    "pagination": {
      "count": 150,
      "page": 1,
      "page_size": 20,
      "total_pages": 8,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

### 4. GET /api/ocr/result/<result_id>/
**Purpose**: Get detailed OCR result

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "document": {
      "filename": "invoice_001.pdf",
      "upload_date": "2025-08-23T10:00:00Z"
    },
    "extracted_data": {
      "numer_faktury": {
        "value": "FV/2025/001",
        "confidence": 98.5
      },
      "data_wystawienia": {
        "value": "2025-08-20",
        "confidence": 95.2
      },
      "sprzedawca": {
        "nazwa": {
          "value": "Example Sp. z o.o.",
          "confidence": 97.8
        },
        "nip": {
          "value": "1234567890",
          "confidence": 92.1
        }
      },
      "pozycje": [
        {
          "nazwa": {
            "value": "Usługa konsultingowa",
            "confidence": 89.3
          },
          "cena_netto": {
            "value": 1000.00,
            "confidence": 96.7
          }
        }
      ]
    },
    "faktura": {
      "id": 456,
      "url": "/api/faktury/456/"
    },
    "needs_review": false,
    "processing_time": 12.5
  }
}
```

### 5. POST /api/ocr/validate/<result_id>/
**Purpose**: Submit manual corrections

**Request**:
```json
{
  "corrections": {
    "numer_faktury": "FV/2025/001-CORRECTED",
    "sprzedawca.nip": "9876543210",
    "pozycje.0.cena_netto": 1200.00
  },
  "create_faktura": true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "updated_fields": ["numer_faktury", "sprzedawca.nip", "pozycje.0.cena_netto"],
    "new_confidence_scores": {
      "numer_faktury": 100.0,
      "sprzedawca.nip": 100.0,
      "pozycje.0.cena_netto": 100.0
    },
    "faktura_created": true,
    "faktura_id": 789
  }
}
```

## Implementation Phases

### Phase 1: Core API Infrastructure
1. Set up DRF configuration and CORS
2. Create base API views and serializers
3. Implement authentication and permissions
4. Add rate limiting and throttling

### Phase 2: Upload and Status Endpoints
1. Implement file upload endpoint with validation
2. Create status tracking endpoint
3. Integrate with existing Celery tasks
4. Add comprehensive error handling

### Phase 3: Results and Detail Endpoints
1. Create results list endpoint with filtering
2. Implement detailed result endpoint
3. Add pagination and optimization
4. Include related object serialization

### Phase 4: Validation and Enhancement
1. Implement manual validation endpoint
2. Add confidence score updates
3. Integrate with Faktura creation
4. Add comprehensive logging

### Phase 5: Testing and Documentation
1. Write comprehensive test suite
2. Add API documentation with Swagger
3. Performance optimization
4. Security audit and hardening