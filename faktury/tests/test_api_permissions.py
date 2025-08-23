"""
Unit tests for API permissions system.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from unittest.mock import Mock, patch

from faktury.models import Firma, DocumentUpload, OCRResult
from faktury.api.permissions import (
    IsOwnerOrReadOnly,
    OCRUploadPermission,
    HasCompanyProfile,
    OCRResultOwnership,
    CanValidateOCRResults,
    validate_user_owns_document,
    validate_user_owns_ocr_result,
    get_user_ocr_results_queryset,
    get_user_documents_queryset
)


class IsOwnerOrReadOnlyTestCase(TestCase):
    """Test IsOwnerOrReadOnly permission class."""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsOwnerOrReadOnly()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create test companies
        self.firma1 = Firma.objects.create(
            user=self.user1,
            nazwa='Test Company 1',
            nip='1234567890'
        )
        self.firma2 = Firma.objects.create(
            user=self.user2,
            nazwa='Test Company 2',
            nip='0987654321'
        )
        
        # Create test document
        self.document = DocumentUpload.objects.create(
            user=self.user1,
            original_filename='test.pdf',
            file_path='/test/path.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
    
    def test_has_permission_authenticated_user(self):
        """Test that authenticated users have permission."""
        request = self.factory.get('/')
        request.user = self.user1
        
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_has_permission_unauthenticated_user(self):
        """Test that unauthenticated users don't have permission."""
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        self.assertFalse(self.permission.has_permission(request, None))
    
    def test_has_object_permission_owner(self):
        """Test that owners have object permission."""
        request = self.factory.get('/')
        request.user = self.user1
        
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.document)
        )
    
    def test_has_object_permission_non_owner(self):
        """Test that non-owners don't have object permission."""
        request = self.factory.get('/')
        request.user = self.user2
        
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.document)
        )
    
    def test_has_object_permission_staff_read_only(self):
        """Test that staff users have read-only access."""
        request = self.factory.get('/')
        request.user = self.staff_user
        
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.document)
        )
        
        # Test write access for staff (should be False)
        request = self.factory.post('/')
        request.user = self.staff_user
        
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.document)
        )


class OCRUploadPermissionTestCase(TestCase):
    """Test OCRUploadPermission class."""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = OCRUploadPermission()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user_no_company = User.objects.create_user(
            username='nocompany',
            email='nocompany@example.com',
            password='testpass123'
        )
        
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Company',
            nip='1234567890'
        )
    
    def test_has_permission_authenticated_with_company(self):
        """Test permission for authenticated user with company."""
        request = self.factory.post('/')
        request.user = self.user
        
        view = Mock()
        view.daily_upload_limit = 50
        view.hourly_upload_limit = 10
        
        self.assertTrue(self.permission.has_permission(request, view))
    
    def test_has_permission_unauthenticated(self):
        """Test permission for unauthenticated user."""
        request = self.factory.post('/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        self.assertFalse(self.permission.has_permission(request, None))
        self.assertEqual(
            self.permission.message,
            "Authentication required for OCR uploads."
        )
    
    def test_has_permission_no_company(self):
        """Test permission for user without company."""
        request = self.factory.post('/')
        request.user = self.user_no_company
        
        self.assertFalse(self.permission.has_permission(request, None))
        self.assertEqual(
            self.permission.message,
            "Active company profile required for OCR uploads."
        )
    
    def test_daily_upload_limit_exceeded(self):
        """Test daily upload limit enforcement."""
        # Create documents to exceed daily limit
        for i in range(5):
            DocumentUpload.objects.create(
                user=self.user,
                original_filename=f'test{i}.pdf',
                file_path=f'/test/path{i}.pdf',
                file_size=1024,
                content_type='application/pdf'
            )
        
        request = self.factory.post('/')
        request.user = self.user
        
        view = Mock()
        view.daily_upload_limit = 3  # Set limit lower than existing uploads
        view.hourly_upload_limit = 10
        
        self.assertFalse(self.permission.has_permission(request, view))
        self.assertIn("Daily upload limit", self.permission.message)
    
    def test_hourly_upload_limit_exceeded(self):
        """Test hourly upload limit enforcement."""
        # Create recent documents to exceed hourly limit
        recent_time = timezone.now() - timedelta(minutes=30)
        for i in range(3):
            doc = DocumentUpload.objects.create(
                user=self.user,
                original_filename=f'recent{i}.pdf',
                file_path=f'/test/recent{i}.pdf',
                file_size=1024,
                content_type='application/pdf'
            )
            doc.upload_timestamp = recent_time
            doc.save()
        
        request = self.factory.post('/')
        request.user = self.user
        
        view = Mock()
        view.daily_upload_limit = 50
        view.hourly_upload_limit = 2  # Set limit lower than recent uploads
        
        self.assertFalse(self.permission.has_permission(request, view))
        self.assertIn("Hourly upload limit", self.permission.message)


class HasCompanyProfileTestCase(TestCase):
    """Test HasCompanyProfile permission class."""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = HasCompanyProfile()
        
        self.user_with_company = User.objects.create_user(
            username='withcompany',
            email='with@example.com',
            password='testpass123'
        )
        self.user_without_company = User.objects.create_user(
            username='withoutcompany',
            email='without@example.com',
            password='testpass123'
        )
        
        self.firma = Firma.objects.create(
            user=self.user_with_company,
            nazwa='Test Company',
            nip='1234567890'
        )
    
    def test_has_permission_with_company(self):
        """Test permission for user with company profile."""
        request = self.factory.get('/')
        request.user = self.user_with_company
        
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_has_permission_without_company(self):
        """Test permission for user without company profile."""
        request = self.factory.get('/')
        request.user = self.user_without_company
        
        self.assertFalse(self.permission.has_permission(request, None))
        self.assertEqual(
            self.permission.message,
            "Company profile required to access this resource."
        )
    
    def test_has_permission_unauthenticated(self):
        """Test permission for unauthenticated user."""
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        self.assertFalse(self.permission.has_permission(request, None))
        self.assertEqual(self.permission.message, "Authentication required.")


class OCRResultOwnershipTestCase(TestCase):
    """Test OCRResultOwnership permission class."""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = OCRResultOwnership()
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        self.document = DocumentUpload.objects.create(
            user=self.user1,
            original_filename='test.pdf',
            file_path='/test/path.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        self.ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Test OCR text',
            extracted_data={'test': 'data'},
            confidence_score=95.0,
            processing_time=1.5
        )
    
    def test_has_object_permission_owner(self):
        """Test object permission for owner."""
        request = self.factory.get('/')
        request.user = self.user1
        
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.ocr_result)
        )
    
    def test_has_object_permission_non_owner(self):
        """Test object permission for non-owner."""
        request = self.factory.get('/')
        request.user = self.user2
        
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.ocr_result)
        )


class UtilityFunctionsTestCase(TestCase):
    """Test utility functions for ownership validation."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        self.document = DocumentUpload.objects.create(
            user=self.user1,
            original_filename='test.pdf',
            file_path='/test/path.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        self.ocr_result = OCRResult.objects.create(
            document=self.document,
            raw_text='Test OCR text',
            extracted_data={'test': 'data'},
            confidence_score=95.0,
            processing_time=1.5
        )
    
    def test_validate_user_owns_document_owner(self):
        """Test document ownership validation for owner."""
        self.assertTrue(
            validate_user_owns_document(self.user1, self.document.id)
        )
    
    def test_validate_user_owns_document_non_owner(self):
        """Test document ownership validation for non-owner."""
        self.assertFalse(
            validate_user_owns_document(self.user2, self.document.id)
        )
    
    def test_validate_user_owns_ocr_result_owner(self):
        """Test OCR result ownership validation for owner."""
        self.assertTrue(
            validate_user_owns_ocr_result(self.user1, self.ocr_result.id)
        )
    
    def test_validate_user_owns_ocr_result_non_owner(self):
        """Test OCR result ownership validation for non-owner."""
        self.assertFalse(
            validate_user_owns_ocr_result(self.user2, self.ocr_result.id)
        )
    
    def test_get_user_ocr_results_queryset(self):
        """Test getting user's OCR results queryset."""
        queryset = get_user_ocr_results_queryset(self.user1)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.ocr_result)
        
        # Test for user without results
        queryset2 = get_user_ocr_results_queryset(self.user2)
        self.assertEqual(queryset2.count(), 0)
    
    def test_get_user_documents_queryset(self):
        """Test getting user's documents queryset."""
        queryset = get_user_documents_queryset(self.user1)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.document)
        
        # Test for user without documents
        queryset2 = get_user_documents_queryset(self.user2)
        self.assertEqual(queryset2.count(), 0)