# Implementation Plan

- [x] 1. Create Status Synchronization Service

  - Create `faktury/services/status_sync_service.py` with unified status logic
  - Implement `sync_document_status()` method to update DocumentUpload based on OCRResult
  - Implement `get_combined_status()` method to return unified status for frontend
  - Add comprehensive error handling and logging
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Enhance DocumentUpload Model Methods

  - Add `get_unified_status()` method to DocumentUpload model
  - Add `get_status_display_data()` method with display metadata
  - Add `get_processing_progress()` method for progress calculation
  - Update status choices to include OCR-specific states
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3. Fix OCR Signal Handlers for Status Synchronization

  - Modify `handle_ocr_result_created` signal to sync DocumentUpload status
  - Add status synchronization when OCRResult status changes
  - Ensure atomic status updates to prevent race conditions
  - Add proper error handling for signal processing failures
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 4. Create AJAX Status Endpoints

  - Create `faktury/views_modules/ocr_status_views.py` with AJAX endpoints
  - Implement `get_status_ajax` view for real-time status polling
  - Add JSON response with unified status and progress data
  - Include error handling and proper HTTP status codes
  - _Requirements: 1.5, 2.1, 2.2_

- [x] 5. Update OCR Status Template with Real-time Updates

  - Modify `faktury/templates/faktury/ocr/status.html` to use unified status
  - Add JavaScript for AJAX polling of status updates
  - Implement progressive status indicators with proper transitions
  - Add error handling and connection status display
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 6. Enhance OCR Result Processing Status Updates

  - Update `process_ocr_result` function to properly sync document status
  - Ensure status updates are atomic and consistent
  - Add proper error state handling and recovery
  - Update logging for better debugging
  - _Requirements: 3.1, 3.2, 3.3, 4.2_

- [x] 7. Add URL Patterns for AJAX Endpoints

  - Add URL patterns for new AJAX status endpoints
  - Ensure proper URL naming and parameter handling
  - Add appropriate permissions and authentication checks
  - _Requirements: 1.5_

- [x] 8. Create Unit Tests for Status Synchronization

  - Write tests for StatusSyncService methods
  - Test all status transition scenarios
  - Test error handling and edge cases
  - Test signal handler status synchronization
  - _Requirements: 3.1, 3.2, 3.3, 4.4_

- [x] 9. Create Integration Tests for End-to-End Flow

  - Test complete OCR processing pipeline with status updates
  - Test AJAX polling functionality
  - Test error scenarios and recovery
  - Test concurrent document processing
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.4_

- [x] 10. Update Management Command for Testing
  - Enhance `test_ocr_integration.py` command to test status synchronization
  - Add status verification and debugging output
  - Test various confidence scenarios and status transitions
  - _Requirements: 3.1, 3.2, 3.3_
