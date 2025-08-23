# Design Document

## Overview

The OCR status synchronization issue occurs because the frontend template checks `document.processing_status` but the actual OCR processing updates `ocr_result.processing_status`. The document status remains "uploaded" while the OCR result progresses through its own status lifecycle. This creates a disconnect between what the user sees and the actual processing state.

The solution involves implementing proper status synchronization between DocumentUpload and OCRResult models, adding real-time status updates via WebSockets or AJAX polling, and ensuring the frontend displays the most current processing state.

## Architecture

### Current Flow Issues
1. **DocumentUpload** status remains "uploaded" after initial processing
2. **OCRResult** has its own status lifecycle (pending → processing → completed/failed)
3. **Frontend template** only checks DocumentUpload.processing_status
4. **No real-time updates** - users must manually refresh

### Proposed Architecture
```
DocumentUpload → OCRResult → Status Synchronization → Frontend Updates
     ↓              ↓              ↓                    ↓
  uploaded      pending         sync_status()      real-time UI
     ↓              ↓              ↓                    ↓
  processing    processing      sync_status()      status updates
     ↓              ↓              ↓                    ↓
  completed     completed       sync_status()      final status
```

## Components and Interfaces

### 1. Status Synchronization Service
**Location:** `faktury/services/status_sync_service.py`

**Purpose:** Synchronize status between DocumentUpload and OCRResult models

**Key Methods:**
- `sync_document_status(document_upload)` - Update document status based on OCR result
- `get_combined_status(document_upload)` - Get unified status for frontend
- `get_status_display_data(document_upload)` - Get status with display metadata

### 2. Enhanced OCR Signal Handlers
**Location:** `faktury/signals.py` (modifications)

**Purpose:** Automatically sync status when OCR processing state changes

**Enhancements:**
- Update DocumentUpload status when OCRResult status changes
- Trigger real-time notifications
- Handle error states properly

### 3. Real-time Status Updates
**Location:** `faktury/views_modules/ocr_status_views.py`

**Purpose:** Provide AJAX endpoints for status polling

**Endpoints:**
- `GET /ocr/status/<document_id>/ajax/` - Get current status as JSON
- `GET /ocr/status/<document_id>/poll/` - Long-polling endpoint

### 4. Enhanced Frontend Status Display
**Location:** `faktury/templates/faktury/ocr/status.html` (modifications)

**Purpose:** Display unified status with real-time updates

**Features:**
- Unified status display logic
- AJAX polling for status updates
- Progressive status indicators
- Error handling and retry options

## Data Models

### DocumentUpload Status Enhancement
```python
class DocumentUpload(models.Model):
    # Existing fields...
    
    # Enhanced status choices
    PROCESSING_STATUS_CHOICES = [
        ('uploaded', 'Przesłano'),
        ('queued', 'W kolejce'),
        ('processing', 'Przetwarzanie'),
        ('ocr_completed', 'OCR zakończone'),
        ('integration_processing', 'Tworzenie faktury'),
        ('completed', 'Zakończone'),
        ('failed', 'Błąd'),
        ('manual_review', 'Wymaga przeglądu'),
    ]
    
    # New methods
    def get_unified_status(self):
        """Get unified status considering OCR result"""
        
    def get_status_display_data(self):
        """Get status with display metadata"""
```

### OCRResult Status Enhancement
```python
class OCRResult(models.Model):
    # Existing fields...
    
    # New methods
    def sync_document_status(self):
        """Sync parent document status"""
        
    def get_processing_progress(self):
        """Get processing progress percentage"""
```

## Error Handling

### Status Sync Failures
- **Retry Logic:** Implement exponential backoff for status sync failures
- **Fallback Display:** Show last known status if sync fails
- **Error Logging:** Log all sync failures for debugging

### Real-time Update Failures
- **Graceful Degradation:** Fall back to manual refresh if AJAX fails
- **Connection Handling:** Handle network timeouts and errors
- **User Feedback:** Show connection status to users

### OCR Processing Failures
- **Clear Error Messages:** Display user-friendly error descriptions
- **Retry Options:** Allow users to retry failed processing
- **Manual Override:** Provide manual data entry option

## Testing Strategy

### Unit Tests
- **Status Sync Service:** Test all status synchronization scenarios
- **Signal Handlers:** Test automatic status updates
- **Model Methods:** Test unified status calculation

### Integration Tests
- **End-to-End Flow:** Test complete OCR processing pipeline
- **Status Transitions:** Test all status transition scenarios
- **Error Scenarios:** Test error handling and recovery

### Frontend Tests
- **AJAX Polling:** Test real-time status updates
- **Status Display:** Test status display logic
- **Error Handling:** Test frontend error scenarios

### Performance Tests
- **Polling Efficiency:** Test AJAX polling performance
- **Database Queries:** Optimize status query performance
- **Concurrent Processing:** Test multiple document processing

## Implementation Phases

### Phase 1: Status Synchronization
1. Create StatusSyncService
2. Enhance signal handlers
3. Add unified status methods
4. Update database queries

### Phase 2: Real-time Updates
1. Create AJAX status endpoints
2. Implement frontend polling
3. Add WebSocket support (optional)
4. Handle connection errors

### Phase 3: Enhanced UI
1. Update status templates
2. Add progress indicators
3. Improve error displays
4. Add retry functionality

### Phase 4: Testing & Optimization
1. Comprehensive testing
2. Performance optimization
3. Error handling refinement
4. Documentation updates