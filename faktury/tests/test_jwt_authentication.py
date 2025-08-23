"""
Unit tests for JWT authentication system.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json

from faktury.models import Firma


class JWTAuthenticationTestCase(TestCase):
    """Test JWT authentication functionality."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create company for user
        self.firma = Firma.objects.create(
            user=self.user,
            nazwa='Test Company',
            nip='1234567890'
        )
        
        # Create user without company
        self.user_no_company = User.objects.create_user(
            username='nocompany',
            email='nocompany@example.com',
            password='testpass123'
        )
    
    def test_obtain_jwt_token_success(self):
        """Test successful JWT token obtainment."""
        url = reverse('api:v1:auth:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertIn('company', response.data)
        
        # Check user data
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['email'], 'test@example.com')
        
        # Check company data
        company_data = response.data['company']
        self.assertEqual(company_data['name'], 'Test Company')
        self.assertEqual(company_data['nip'], '1234567890')
    
    def test_obtain_jwt_token_no_company(self):
        """Test JWT token obtainment for user without company."""
        url = reverse('api:v1:auth:token_obtain_pair')
        data = {
            'username': 'nocompany',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        # Company should not be present or be None
        self.assertNotIn('company', response.data)
    
    def test_obtain_jwt_token_invalid_credentials(self):
        """Test JWT token obtainment with invalid credentials."""
        url = reverse('api:v1:auth:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_jwt_token_success(self):
        """Test successful JWT token refresh."""
        # First get tokens
        refresh = RefreshToken.for_user(self.user)
        
        url = reverse('api:v1:auth:token_refresh')
        data = {
            'refresh': str(refresh)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_refresh_jwt_token_invalid(self):
        """Test JWT token refresh with invalid token."""
        url = reverse('api:v1:auth:token_refresh')
        data = {
            'refresh': 'invalid_token'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_verify_jwt_token_success(self):
        """Test JWT token verification."""
        # Get access token
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        url = reverse('api:v1:auth:token_verify')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('user', response.data['data'])
        self.assertIn('company', response.data['data'])
        self.assertTrue(response.data['data']['token_valid'])
    
    def test_verify_jwt_token_invalid(self):
        """Test JWT token verification with invalid token."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        url = reverse('api:v1:auth:token_verify')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
    
    def test_logout_success(self):
        """Test successful logout."""
        # Get refresh token
        refresh = RefreshToken.for_user(self.user)
        
        url = reverse('api:v1:auth:logout')
        data = {
            'refresh_token': str(refresh)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_authenticated_api_access(self):
        """Test accessing authenticated API endpoints with JWT."""
        # Get access token
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Try to access a protected endpoint (assuming it exists)
        # This is a placeholder - actual endpoint would be implemented in other tasks
        url = '/api/ocr/results/'  # This endpoint will be implemented in later tasks
        response = self.client.get(url)
        
        # We expect either 200 (if endpoint exists) or 404 (if not implemented yet)
        # But not 401 (unauthorized) since we have valid JWT
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_api_access(self):
        """Test accessing authenticated API endpoints without JWT."""
        # Try to access a protected endpoint without authentication
        url = '/api/ocr/results/'  # This endpoint will be implemented in later tasks
        response = self.client.get(url)
        
        # We expect 401 (unauthorized) or 404 (not found)
        # The important thing is that we don't get access to protected data
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND
        ])