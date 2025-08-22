"""
Pomocnicze decoratory dla aplikacji faktury
"""
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


def ajax_required(f):
    """
    Decorator that ensures the request is AJAX
    """
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'This endpoint requires AJAX request'}, status=400)
        return f(request, *args, **kwargs)
    return wrapper


def ajax_login_required(f):
    """
    Combines login_required and ajax_required decorators
    """
    @wraps(f)
    @login_required
    @ajax_required
    def wrapper(request, *args, **kwargs):
        return f(request, *args, **kwargs)
    return wrapper


def require_POST_ajax(f):
    """
    Requires POST method and AJAX for the view
    """
    @wraps(f)
    @require_http_methods(["POST"])
    @ajax_required
    def wrapper(request, *args, **kwargs):
        return f(request, *args, **kwargs)
    return wrapper
