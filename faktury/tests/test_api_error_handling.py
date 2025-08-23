"""
Tests for OCR REST API error handling system.

This module tests the comprehensive error handling system including:
- Custom exception classes
- Error response formatting
- HTTP status code mapping
- Field-specific validation errors
- Logging functionality
"""

import json
import logging
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response

from faktury.api.exceptions import (
    OCRAPIException, FileValidationError, FileSizeExceededError,
    UnsupportedFileTypeError, MaliciousFileError, TaskNotFoundError,
    ResultNotFoundError, UnauthorizedAccessError, RateLimitExceededError,
    ValidationError, custom_exception_handler
)
from faktury.api.responses import APIResponseFormatter
from faktury.api.status_codes import (
    APIStatusCode, ErrorCodeMapping, build_success_response,
    build_error_response, build_validation_error_response
)
from faktury.api.logging_config import APIOperationLogger, SecurityLogger
from faktury.models import DocumentUpload, OCRResult, Firma


class CustomExceptionTests(TestCase):
    """Test custom exception classes."""
    
    def test_base_ocr_api_exception(self):
        """Test base OCRAPIException functionality."""
        exc = OCRAPIException()
        self.assertEqual(str(exc), "An error occurred in the OCR API")
        self.assertEqual(exc.code, "OCR_API_ERROR")
        self.assertEqual(exc.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(exc.details, {})
    
    def test_custom_exception_parameters(self):
        """Test custom exception with parameters."""
        exc = FileValidationError(
            message="Custom error message",
            code="CUSTOM_CODE",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"field": "error details"}
        )
        
        self.assertEqual(str(exc), "Custom error message")
        self.assertEqual(exc.code, "CUSTOM_CODE")
        self.assertEqual(exc.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(exc.details, {"field": "error details"})
    
    def test_file_validation_errors(self):
        """Test file validation exception types."""
        # FileSizeExceededError
        exc = FileSizeExceededError()
        self.assertEqual(exc.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        
        # UnsupportedFileTypeError
        exc = UnsupportedFileTypeError()
        self.assertEqual(exc.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        # MaliciousFileError
        exc = MaliciousFileError()
        self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_resource_not_found_errors(self):
        """Test resource not found exception types."""
        exc = TaskNotFoundError()
        self.assertEqual(exc.status_code, status.HTTP_404_NOT_FOUND)
        
        exc = ResultNotFoundError()
        self.assertEqual(exc.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_authorization_errors(self):
        """Test authorization exception types."""
        exc = UnauthorizedAccessError()
        self.assertEqual(exc.status_code, status.HTTP_403_FORBIDDEN)
        
        exc = RateLimitExceededError()
        self.assertEqual(exc.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class CustomExceptionHandlerTests(TestCase):
    """Test custom exception handler."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_handle_ocr_api_exception(self):
        """Test handling of OCRAPIException."""
        exc = FileValidationError("Test error message", code="TEST_ERROR")
        context = {'request': MagicMock(user=self.user, path='/api/test/')}
        
        with patch('faktury.api.exceptions.logger') as mock_logger:
            response = custom_exception_handler(exc, context)
            
            self.assertIsInstance(response, Response)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            
            response_data = response.data
            self.assertFalse(response_data['success'])
            self.assertEqual(response_data['error']['code'], 'TEST_ERROR')
            self.assertEqual(response_data['error']['message'], 'Test error message')
            
            # Check logging was called
            mock_logger.error.assert_called_once()
    
    def test_handle_validation_error(self):
        """Test handling of DRF validation errors."""
        from rest_framework.exceptions import ValidationError as DRFValidationError
        
        exc = DRFValidationError({'field1': ['Error message 1'], 'field2': ['Error message 2']})
        context = {'request': MagicMock()}
        
        response = custom_exception_handler(exc, context)
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.data
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error']['code'], 'VALIDATION_ERROR')
        self.assertIn('field1', response_data['error']['details'])
        self.assertIn('field2', response_data['error']['details'])
    
    def test_handle_authentication_error(self):
        """Test handling of authentication errors."""
        from rest_framework.exceptions import AuthenticationFailed
        
        exc = AuthenticationFailed("Invalid credentials")
        context = {'request': MagicMock()}
        
        response = custom_exception_handler(exc, context)
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response_data = response.data
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error']['code'], 'AUTHENTICATION_REQUIRED')


class ResponseFormatterTests(TestCase):
    """Test API response formatter."""
    
    def test_success_response(self):
        """Test success response formatting."""
        data = {'key': 'value'}
        message = "Operation successful"
        
        response = APIResponseFormatter.success(data, message)
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.data
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data'], data)
        self.assertEqual(response_data['message'], message)
        self.assertIn('timestamp', response_data)
    
    def test_error_response(self):
        """Test error response formatting."""
        code = "TEST_ERROR"
        message = "Test error message"
        details = {'field': 'error details'}
        
        response = APIResponseFormatter.error(code, message, details)
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.data
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error']['code'], code)
        self.assertEqual(response_data['error']['message'], message)
        self.assertEqual(response_data['error']['details'], details)
        self.assertIn('timestamp', response_data)
    
    def test_validation_error_response(self):
        """Test validation error response formatting."""
        errors = {
            'field1': ['Error message 1'],
            'field2': ['Error message 2', 'Another error']
        }
        
        response = APIResponseFormatter.validation_error(errors)
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.data
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error']['code'], 'VALIDATION_ERROR')
        self.assertEqual(response_data['error']['details']['field1'], ['Error message 1'])
        self.assertEqual(response_data['error']['details']['field2'], ['Error message 2', 'Another error'])


class StatusCodeMappingTests(TestCase):
    """Test HTTP status code mapping."""
    
    def test_error_code_mapping(self):
        """Test error code to status code mapping."""
        # File validation errors
        self.assertEqual(
            ErrorCodeMapping.get_status_code('FILE_SIZE_EXCEEDED'),
            APIStatusCode.PAYLOAD_TOO_LARGE
        )
        
        self.assertEqual(
            ErrorCodeMapping.get_status_code('UNSUPPORTED_FILE_TYPE'),
            APIStatusCode.UNSUPPORTED_MEDIA_TYPE
        )
        
        # Authentication errors
        self.assertEqual(
            ErrorCodeMapping.get_status_code('UNAUTHORIZED_ACCESS'),
            APIStatusCode.FORBIDDEN
        )
        
        # Rate limiting errors
        self.assertEqual(
            ErrorCodeMapping.get_status_code('RATE_LIMIT_EXCEEDED'),
            APIStatusCode.TOO_MANY_REQUESTS
        )
    
    def test_unknown_error_code(self):
        """Test handling of unknown error codes."""
        result = ErrorCodeMapping.get_status_code('UNKNOWN_ERROR')
        self.assertEqual(result, APIStatusCode.INTERNAL_SERVER_ERROR)
    
    def test_build_response_functions(self):
        """Test response building utility functions."""
        # Success response
        data, status_code = build_success_response({'key': 'value'})
        self.assertTrue(data['success'])
        self.assertEqual(status_code, 200)
        
        # Error response
        data, status_code = build_error_response('TEST_ERROR', 'Test message')
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'TEST_ERROR')
        self.assertEqual(status_code, 400)
        
        # Validation error response
        data, status_code = build_validation_error_response({'field': ['error']})
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'VALIDATION_ERROR')
        self.assertEqual(status_code, 400)


class LoggingTests(TestCase):
    """Test API logging functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('faktury.api.logging_config.logger')
    def test_operation_logger(self, mock_logger):
        """Test API operation logging."""
        operation_logger = APIOperationLogger('test_operation')
        
        # Test log start
        operation_logger.log_start(user=self.user, details={'key': 'value'})
        mock_logger.info.assert_called()
        
        # Test log success
        operation_logger.log_success(user=self.user, duration_ms=100)
        self.assertEqual(mock_logger.info.call_count, 2)
        
        # Test log error
        error = Exception("Test error")
        operation_logger.log_error(error, user=self.user)
        mock_logger.error.assert_called()
    
    @patch('faktury.api.logging_config.logger')
    def test_security_logger(self, mock_logger):
        """Test security logging."""
        security_logger = SecurityLogger()
        request = MagicMock()
        request.META = {'HTTP_USER_AGENT': 'test-agent', 'REMOTE_ADDR': '127.0.0.1'}
        request.path = '/api/test/'
        request.method = 'POST'
        
        # Test authentication failure
        security_logger.log_authentication_failure(request, "Invalid credentials")
        mock_logger.warning.assert_called()
        
        # Test authorization failure
        security_logger.log_authorization_failure(request, self.user, "test_resource")
        self.assertEqual(mock_logger.warning.call_count, 2)
        
        # Test rate limit exceeded
        security_logger.log_rate_limit_exceeded(request, self.user, "upload_limit")
        self.assertEqual(mock_logger.warning.call_count, 3)
        
        # Test suspicious activity
        security_logger.log_suspicious_activity(request, "malicious_file", {"details": "test"})
        mock_logger.error.assert_called()


class APIErrorHandlingIntegrationTests(APITestCase):
    """Integration tests for API error handling."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create a company for the user
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa="Test Company",
            nip="1234567890"
        )
    
    def test_file_upload_validation_errors(self):
        """Test file upload validation error handling."""
        # Test missing file
        response = self.client.post('/api/ocr/upload/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)
    
    def test_file_size_exceeded_error(self):
        """Test file size exceeded error handling."""
        # Create a large file (mock)
        large_file = SimpleUploadedFile(
            "large_file.pdf",
            b"x" * (11 * 1024 * 1024),  # 11MB file
            content_type="application/pdf"
        )
        
        with patch('faktury.api.serializers.settings') as mock_settings:
            mock_settings.DOCUMENT_AI_CONFIG = {'max_file_size': 10 * 1024 * 1024}
            mock_settings.SUPPORTED_DOCUMENT_TYPES = {'application/pdf': 'PDF'}
            
            response = self.client.post('/api/ocr/upload/', {'file': large_file})
            
            self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
            self.assertFalse(response.data['success'])
            self.assertEqual(response.data['error']['code'], 'FILE_SIZE_EXCEEDED')
    
    def test_unsupported_file_type_error(self):
        """Test unsupported file type error handling."""
        unsupported_file = SimpleUploadedFile(
            "test.txt",
            b"This is a text file",
            content_type="text/plain"
        )
        
        with patch('faktury.api.serializers.settings') as mock_settings:
            mock_settings.SUPPORTED_DOCUMENT_TYPES = {'application/pdf': 'PDF'}
            
            response = self.client.post('/api/ocr/upload/', {'file': unsupported_file})
            
            self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            self.assertFalse(response.data['success'])
            self.assertEqual(response.data['error']['code'], 'UNSUPPORTED_FILE_TYPE')
    
    def test_task_not_found_error(self):
        """Test task not found error handling."""
        response = self.client.get('/api/ocr/status/nonexistent-task-id/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'TASK_NOT_FOUND')
    
    def test_unauthorized_access_error(self):
        """Test unauthorized access error handling."""
        # Create another user and their OCR result
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create a document upload for the other user
        document = DocumentUpload.objects.create(
            user=other_user,
            original_filename='test.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        ocr_result = OCRResult.objects.create(
            document=document,
            extracted_data={'test': 'data'},
            confidence_score=95.0
        )
        
        # Try to access other user's OCR result
        response = self.client.get(f'/api/ocr/result/{ocr_result.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'PERMISSION_DENIED')
    
    def test_validation_error_response_format(self):
        """Test validation error response format."""
        # Test with invalid corrections data
        document = DocumentUpload.objects.create(
            user=self.user,
            original_filename='test.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        ocr_result = OCRResult.objects.create(
            document=document,
            extracted_data={'numer_faktury': 'FV/001'},
            confidence_score=95.0
        )
        
        # Send invalid validation data
        invalid_data = {
            'corrections': 'invalid_format',  # Should be dict
            'create_faktura': True
        }
        
        response = self.client.post(f'/api/ocr/validate/{ocr_result.id}/', invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'VALIDATION_ERROR')
        self.assertIn('details', response.data['error'])
    
    def test_response_timestamp_format(self):
        """Test that all responses include proper timestamp format."""
        response = self.client.get('/api/ocr/results/')
        
        self.assertIn('timestamp', response.data)
        # Check timestamp format (ISO 8601 with Z suffix)
        timestamp = response.data['timestamp']
        self.assertTrue(timestamp.endswith('Z'))
        self.assertRegex(timestamp, r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z')
    
    @override_settings(DEBUG=False)
    def test_production_error_handling(self):
        """Test error handling in production mode."""
        # In production, we should not expose internal error details
        with patch('faktury.api.views.FileUploadService') as mock_service:
            mock_service.side_effect = Exception("Internal database error")
            
            file_data = SimpleUploadedFile(
                "test.pdf",
                b"PDF content",
                content_type="application/pdf"
            )
            
            response = self.client.post('/api/ocr/upload/', {'file': file_data})
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertFalse(response.data['success'])
            # Should not expose internal error details in production
            self.assertNotIn("Internal database error", str(response.data))