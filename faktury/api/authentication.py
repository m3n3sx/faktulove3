"""
JWT Authentication views for the OCR REST API.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes additional user information.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        
        # Add company information if available
        try:
            from faktury.models import Firma
            firma = Firma.objects.filter(user=user).first()
            if firma:
                token['company_id'] = firma.id
                token['company_name'] = firma.nazwa
        except Exception as e:
            logger.warning(f"Could not add company info to token for user {user.id}: {str(e)}")
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra response data
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_staff': self.user.is_staff,
        }
        
        # Add company information
        try:
            from faktury.models import Firma
            firma = Firma.objects.filter(user=self.user).first()
            if firma:
                data['company'] = {
                    'id': firma.id,
                    'name': firma.nazwa,
                    'nip': firma.nip,
                }
        except Exception as e:
            logger.warning(f"Could not add company info to response for user {self.user.id}: {str(e)}")
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with enhanced error handling.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                logger.info(f"Successful JWT login for user: {request.data.get('username', 'unknown')}")
            
            return response
            
        except Exception as e:
            logger.error(f"JWT authentication error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'AUTHENTICATION_ERROR',
                        'message': 'Authentication failed. Please check your credentials.',
                        'details': {}
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view with enhanced error handling.
    """
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                logger.info("Successful JWT token refresh")
            
            return response
            
        except Exception as e:
            logger.error(f"JWT token refresh error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'TOKEN_REFRESH_ERROR',
                        'message': 'Token refresh failed. Please login again.',
                        'details': {}
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    Logout view that blacklists the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        logger.info(f"User logged out successfully")
        return Response(
            {
                'success': True,
                'message': 'Successfully logged out.'
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {
                'success': False,
                'error': {
                    'code': 'LOGOUT_ERROR',
                    'message': 'Logout failed.',
                    'details': {}
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def verify_token_view(request):
    """
    Verify if the current JWT token is valid and return user info.
    """
    try:
        user = request.user
        if user.is_authenticated:
            # Get company information
            company_info = None
            try:
                from faktury.models import Firma
                firma = Firma.objects.filter(user=user).first()
                if firma:
                    company_info = {
                        'id': firma.id,
                        'name': firma.nazwa,
                        'nip': firma.nip,
                    }
            except Exception as e:
                logger.warning(f"Could not get company info for user {user.id}: {str(e)}")
            
            return Response(
                {
                    'success': True,
                    'data': {
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'is_staff': user.is_staff,
                        },
                        'company': company_info,
                        'token_valid': True
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'INVALID_TOKEN',
                        'message': 'Token is invalid or expired.',
                        'details': {}
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return Response(
            {
                'success': False,
                'error': {
                    'code': 'TOKEN_VERIFICATION_ERROR',
                    'message': 'Token verification failed.',
                    'details': {}
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    """
    Get CSRF token for AJAX requests.
    """
    try:
        from django.middleware.csrf import get_token
        csrf_token = get_token(request)
        
        return Response(
            {
                'success': True,
                'csrf_token': csrf_token,
                'message': 'CSRF token retrieved successfully'
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"CSRF token retrieval error: {str(e)}")
        return Response(
            {
                'success': False,
                'error': {
                    'code': 'CSRF_TOKEN_ERROR',
                    'message': 'Failed to retrieve CSRF token',
                    'details': {}
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )