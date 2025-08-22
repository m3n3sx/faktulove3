"""
Custom middleware for additional security headers
"""


class SecurityHeadersMiddleware:
    """
    Middleware that adds security headers to responses
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class FirmaCheckMiddleware:
    """
    Middleware to check if user has company data configured
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude paths that don't require company check
        excluded_paths = [
            '/admin/',
            '/accounts/',
            '/dodaj_firme/',
            '/edytuj_firme/',
            '/static/',
            '/media/',
        ]
        
        # Check if path should be excluded
        path_excluded = any(request.path.startswith(path) for path in excluded_paths)
        
        if (request.user.is_authenticated and 
            not path_excluded and 
            not request.user.is_superuser):
            
            try:
                from faktury.models import Firma
                Firma.objects.get(user=request.user)
            except Firma.DoesNotExist:
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.warning(request, "Uzupełnij dane swojej firmy przed korzystaniem z systemu.")
                return redirect('dodaj_firme')
        
        response = self.get_response(request)
        return response
