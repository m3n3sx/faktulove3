"""
Maintenance Mode Middleware

Handles maintenance mode functionality by checking if maintenance mode is enabled
and displaying appropriate maintenance page to users.
"""

import logging
from django.http import HttpResponse
from django.template import Template, Context
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class MaintenanceMiddleware(MiddlewareMixin):
    """Middleware to handle maintenance mode."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.maintenance_mode_key = 'system_maintenance_mode'
        self.exempt_paths = [
            '/admin/',
            '/api/health/',
            '/static/',
            '/media/',
        ]
        self.exempt_ips = getattr(settings, 'MAINTENANCE_EXEMPT_IPS', [])
    
    def process_request(self, request):
        """Process request and check for maintenance mode."""
        # Skip maintenance check for exempt paths
        if self._is_exempt_path(request.path):
            return None
        
        # Skip maintenance check for exempt IPs
        if self._is_exempt_ip(request):
            return None
        
        # Skip maintenance check for superusers
        if request.user.is_authenticated and request.user.is_superuser:
            return None
        
        # Check if maintenance mode is enabled
        maintenance_info = cache.get(self.maintenance_mode_key)
        
        if maintenance_info and maintenance_info.get('enabled'):
            return self._render_maintenance_page(maintenance_info)
        
        return None
    
    def _is_exempt_path(self, path):
        """Check if the path is exempt from maintenance mode."""
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False
    
    def _is_exempt_ip(self, request):
        """Check if the IP address is exempt from maintenance mode."""
        if not self.exempt_ips:
            return False
        
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip in self.exempt_ips
    
    def _render_maintenance_page(self, maintenance_info):
        """Render the maintenance page."""
        try:
            maintenance_template = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Konserwacja systemu - FaktuLove</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }
        
        .maintenance-container {
            background: white;
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 20px;
        }
        
        .maintenance-icon {
            font-size: 80px;
            margin-bottom: 30px;
            color: #667eea;
        }
        
        .maintenance-title {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 20px;
            color: #2d3748;
        }
        
        .maintenance-message {
            font-size: 1.2em;
            line-height: 1.6;
            margin-bottom: 30px;
            color: #4a5568;
        }
        
        .maintenance-details {
            background: #f7fafc;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #667eea;
        }
        
        .maintenance-time {
            font-size: 0.9em;
            color: #718096;
            margin-bottom: 10px;
        }
        
        .maintenance-contact {
            font-size: 1em;
            color: #4a5568;
        }
        
        .maintenance-contact a {
            color: #667eea;
            text-decoration: none;
        }
        
        .maintenance-contact a:hover {
            text-decoration: underline;
        }
        
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #e2e8f0;
            border-radius: 2px;
            overflow: hidden;
            margin-top: 30px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
            animation: progress 2s ease-in-out infinite;
        }
        
        @keyframes progress {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 100%; }
        }
        
        .refresh-info {
            margin-top: 20px;
            font-size: 0.9em;
            color: #718096;
        }
        
        @media (max-width: 768px) {
            .maintenance-container {
                padding: 40px 20px;
                margin: 10px;
            }
            
            .maintenance-title {
                font-size: 2em;
            }
            
            .maintenance-icon {
                font-size: 60px;
            }
        }
    </style>
</head>
<body>
    <div class="maintenance-container">
        <div class="maintenance-icon">🔧</div>
        
        <h1 class="maintenance-title">Konserwacja systemu</h1>
        
        <div class="maintenance-message">
            {{ message }}
        </div>
        
        <div class="maintenance-details">
            {% if enabled_at %}
            <div class="maintenance-time">
                Konserwacja rozpoczęta: {{ enabled_at }}
            </div>
            {% endif %}
            
            <div class="maintenance-contact">
                W przypadku pilnych spraw prosimy o kontakt: 
                <a href="mailto:support@faktulove.com">support@faktulove.com</a>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        
        <div class="refresh-info">
            Strona odświeży się automatycznie co 30 sekund
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function() {
            location.reload();
        }, 30000);
        
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {
            const container = document.querySelector('.maintenance-container');
            container.style.opacity = '0';
            container.style.transform = 'translateY(20px)';
            
            setTimeout(function() {
                container.style.transition = 'all 0.6s ease';
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            }, 100);
        });
    </script>
</body>
</html>
            """
            
            template = Template(maintenance_template)
            context = Context({
                'message': maintenance_info.get('message', 'System maintenance in progress'),
                'enabled_at': maintenance_info.get('enabled_at', ''),
                'enabled_by': maintenance_info.get('enabled_by', '')
            })
            
            html_content = template.render(context)
            
            response = HttpResponse(html_content, status=503)
            response['Retry-After'] = '1800'  # 30 minutes
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to render maintenance page: {e}")
            
            # Fallback simple maintenance page
            simple_html = """
            <html>
            <head><title>Maintenance - FaktuLove</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>System Maintenance</h1>
                <p>The system is currently under maintenance. Please try again later.</p>
                <p>Konserwacja systemu. Prosimy spróbować ponownie później.</p>
            </body>
            </html>
            """
            
            return HttpResponse(simple_html, status=503)