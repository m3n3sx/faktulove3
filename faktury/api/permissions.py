"""
Custom permissions for the OCR REST API.
"""
from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Supports OCR results access control with proper ownership validation.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific object."""
        # Staff users have read-only access to all objects
        if request.user.is_staff and request.method in permissions.SAFE_METHODS:
            return True
        
        # Check ownership for all methods
        return self._check_ownership(request.user, obj)
    
    def _check_ownership(self, user, obj):
        """
        Check if user owns the object.
        Handles various ownership patterns for OCR-related models.
        """
        if not user or not user.is_authenticated:
            return False
        
        # Direct user ownership
        if hasattr(obj, 'user'):
            return obj.user == user
        
        # Alternative ownership field names
        if hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == user
        
        # OCRResult ownership through document
        if hasattr(obj, 'document'):
            if hasattr(obj.document, 'user'):
                return obj.document.user == user
            elif hasattr(obj.document, 'uploaded_by'):
                return obj.document.uploaded_by == user
        
        # DocumentUpload direct ownership
        if obj.__class__.__name__ == 'DocumentUpload':
            return obj.user == user
        
        # OCRResult direct ownership check
        if obj.__class__.__name__ == 'OCRResult':
            return obj.document.user == user
        
        # Faktura ownership (if OCR result is linked to faktura)
        if hasattr(obj, 'faktura') and obj.faktura:
            return obj.faktura.firma.user == user
        
        logger.warning(f"Unknown ownership pattern for object {obj.__class__.__name__}")
        return False


class OCRUploadPermission(permissions.BasePermission):
    """
    Permission for OCR upload operations with company profile and quota validation.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to upload OCR documents."""
        # User must be authenticated
        if not request.user.is_authenticated:
            self.message = "Authentication required for OCR uploads."
            return False
        
        # Check if user has active company profile
        try:
            from faktury.models import Firma, DocumentUpload
            
            firma = Firma.objects.filter(user=request.user).first()
            if not firma:
                self.message = "Active company profile required for OCR uploads."
                return False
            
            # Check upload quotas (daily limit)
            daily_limit = getattr(view, 'daily_upload_limit', 50)  # Default 50 uploads per day
            today = timezone.now().date()
            today_uploads = DocumentUpload.objects.filter(
                user=request.user,
                upload_timestamp__date=today
            ).count()
            
            if today_uploads >= daily_limit:
                self.message = f"Daily upload limit of {daily_limit} documents exceeded."
                return False
            
            # Check hourly rate limit (more restrictive)
            hourly_limit = getattr(view, 'hourly_upload_limit', 10)  # Default 10 uploads per hour
            one_hour_ago = timezone.now() - timedelta(hours=1)
            recent_uploads = DocumentUpload.objects.filter(
                user=request.user,
                upload_timestamp__gte=one_hour_ago
            ).count()
            
            if recent_uploads >= hourly_limit:
                self.message = f"Hourly upload limit of {hourly_limit} documents exceeded."
                return False
            
            # Check if user account is in good standing
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                if hasattr(profile, 'is_suspended') and profile.is_suspended:
                    self.message = "Account suspended. Contact support for assistance."
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking OCR upload permission for user {request.user.id}: {str(e)}")
            self.message = "Unable to verify upload permissions. Please try again."
            return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for OCR uploads."""
        # For upload operations, we mainly care about the general permission
        # But we can add object-specific checks here if needed
        return self.has_permission(request, view)


class HasCompanyProfile(permissions.BasePermission):
    """
    Permission that requires user to have a company profile.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self.message = "Authentication required."
            return False
        
        try:
            from faktury.models import Firma
            has_profile = Firma.objects.filter(user=request.user).exists()
            if not has_profile:
                self.message = "Company profile required to access this resource."
            return has_profile
        except Exception as e:
            logger.error(f"Error checking company profile for user {request.user.id}: {str(e)}")
            self.message = "Unable to verify company profile."
            return False


class OCRResultOwnership(permissions.BasePermission):
    """
    Permission class specifically for OCR result ownership validation.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user owns the OCR result."""
        return self._validate_ocr_ownership(request.user, obj)
    
    def _validate_ocr_ownership(self, user, obj):
        """
        Validate OCR result ownership with detailed logging.
        """
        if not user or not user.is_authenticated:
            return False
        
        try:
            # Handle OCRResult objects
            if obj.__class__.__name__ == 'OCRResult':
                is_owner = obj.document.user == user
                if not is_owner:
                    logger.warning(f"User {user.id} attempted to access OCR result {obj.id} owned by {obj.document.user.id}")
                return is_owner
            
            # Handle DocumentUpload objects
            elif obj.__class__.__name__ == 'DocumentUpload':
                is_owner = obj.user == user
                if not is_owner:
                    logger.warning(f"User {user.id} attempted to access document {obj.id} owned by {obj.user.id}")
                return is_owner
            
            # Handle other related objects
            elif hasattr(obj, 'document') and hasattr(obj.document, 'user'):
                return obj.document.user == user
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating OCR ownership for user {user.id}: {str(e)}")
            return False


class CanValidateOCRResults(permissions.BasePermission):
    """
    Permission for manual OCR validation operations.
    """
    
    def has_permission(self, request, view):
        """Check if user can perform OCR validation."""
        if not request.user.is_authenticated:
            self.message = "Authentication required for OCR validation."
            return False
        
        # Check if user has company profile
        try:
            from faktury.models import Firma
            if not Firma.objects.filter(user=request.user).exists():
                self.message = "Company profile required for OCR validation."
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking OCR validation permission for user {request.user.id}: {str(e)}")
            self.message = "Unable to verify validation permissions."
            return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user can validate specific OCR result."""
        # Must own the OCR result
        if not self._validate_ownership(request.user, obj):
            self.message = "You can only validate your own OCR results."
            return False
        
        # OCR result must be in a state that allows validation
        if hasattr(obj, 'processing_status'):
            if obj.processing_status not in ['completed', 'manual_review']:
                self.message = "OCR result must be completed before validation."
                return False
        
        return True
    
    def _validate_ownership(self, user, obj):
        """Validate ownership for OCR validation."""
        if obj.__class__.__name__ == 'OCRResult':
            return obj.document.user == user
        elif obj.__class__.__name__ == 'DocumentUpload':
            return obj.user == user
        return False


# Utility functions for user ownership validation
def validate_user_owns_document(user, document_id):
    """
    Validate that user owns a specific document.
    
    Args:
        user: Django User instance
        document_id: ID of the DocumentUpload
        
    Returns:
        bool: True if user owns the document
    """
    try:
        from faktury.models import DocumentUpload
        return DocumentUpload.objects.filter(
            id=document_id,
            user=user
        ).exists()
    except Exception as e:
        logger.error(f"Error validating document ownership: {str(e)}")
        return False


def validate_user_owns_ocr_result(user, result_id):
    """
    Validate that user owns a specific OCR result.
    
    Args:
        user: Django User instance
        result_id: ID of the OCRResult
        
    Returns:
        bool: True if user owns the OCR result
    """
    try:
        from faktury.models import OCRResult
        return OCRResult.objects.filter(
            id=result_id,
            document__user=user
        ).exists()
    except Exception as e:
        logger.error(f"Error validating OCR result ownership: {str(e)}")
        return False


def get_user_ocr_results_queryset(user):
    """
    Get queryset of OCR results owned by user.
    
    Args:
        user: Django User instance
        
    Returns:
        QuerySet: OCR results owned by the user
    """
    try:
        from faktury.models import OCRResult
        return OCRResult.objects.filter(document__user=user)
    except Exception as e:
        logger.error(f"Error getting user OCR results: {str(e)}")
        return OCRResult.objects.none()


def get_user_documents_queryset(user):
    """
    Get queryset of documents owned by user.
    
    Args:
        user: Django User instance
        
    Returns:
        QuerySet: Documents owned by the user
    """
    try:
        from faktury.models import DocumentUpload
        return DocumentUpload.objects.filter(user=user)
    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        return DocumentUpload.objects.none()