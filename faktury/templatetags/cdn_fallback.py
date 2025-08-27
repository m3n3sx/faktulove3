"""
Template tags for CDN fallback system
"""
from django import template
from django.conf import settings
from django.templatetags.static import static
import json

register = template.Library()

# CDN fallback configuration
CDN_FALLBACKS = {
    'assets/css/lib/bootstrap.min.css': {
        'cdn': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
        'integrity': 'sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN',
        'critical': True
    },
    'assets/css/lib/dataTables.min.css': {
        'cdn': 'https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css',
        'critical': False
    },
    'assets/css/lib/flatpickr.min.css': {
        'cdn': 'https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.css',
        'critical': False
    },
    'assets/css/lib/full-calendar.css': {
        'cdn': 'https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.css',
        'critical': False
    },
    'assets/css/lib/magnific-popup.css': {
        'cdn': 'https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/magnific-popup.min.css',
        'critical': False
    },
    'assets/css/lib/slick.css': {
        'cdn': 'https://cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.css',
        'critical': False
    },
    'assets/css/lib/prism.css': {
        'cdn': 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css',
        'critical': False
    },
    'assets/js/lib/jquery-3.7.1.min.js': {
        'cdn': 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js',
        'integrity': 'sha512-v2CJ7UaYy4JwqLDIrZUI/4hqeoQieOmAZNXBeQyjo21dadnwR+8ZaIJVT8EE2iyI61OV8e6M8PP2/4hpQINQ/g==',
        'critical': True
    },
    'assets/js/lib/bootstrap.bundle.min.js': {
        'cdn': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
        'integrity': 'sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL',
        'critical': True
    },
    'assets/js/lib/apexcharts.min.js': {
        'cdn': 'https://cdn.jsdelivr.net/npm/apexcharts@latest/dist/apexcharts.min.js',
        'critical': True
    },
    'assets/js/lib/dataTables.min.js': {
        'cdn': 'https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js',
        'critical': False
    },
    'assets/js/lib/iconify-icon.min.js': {
        'cdn': 'https://code.iconify.design/3/3.1.1/iconify.min.js',
        'critical': False
    },
    'assets/js/lib/jquery-ui.min.js': {
        'cdn': 'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.13.2/jquery-ui.min.js',
        'critical': False
    },
    'assets/js/lib/magnific-popup.min.js': {
        'cdn': 'https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/jquery.magnific-popup.min.js',
        'critical': False
    },
    'assets/js/lib/slick.min.js': {
        'cdn': 'https://cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.min.js',
        'critical': False
    },
    'assets/js/lib/prism.js': {
        'cdn': 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js',
        'critical': False
    }
}


@register.simple_tag
def static_with_fallback(path):
    """
    Generate static URL with fallback configuration
    """
    static_url = static(path)
    fallback_config = CDN_FALLBACKS.get(path, {})
    
    if fallback_config:
        return {
            'url': static_url,
            'fallback': fallback_config,
            'path': path
        }
    
    return {'url': static_url, 'path': path}


@register.inclusion_tag('partials/cdn_fallback_css.html')
def load_css_with_fallback(path):
    """
    Load CSS with fallback support
    """
    config = static_with_fallback(path)
    return {'config': config}


@register.inclusion_tag('partials/cdn_fallback_js.html')
def load_js_with_fallback(path):
    """
    Load JavaScript with fallback support
    """
    config = static_with_fallback(path)
    return {'config': config}


@register.simple_tag
def cdn_fallback_config():
    """
    Output CDN fallback configuration as JSON for JavaScript
    """
    return json.dumps(CDN_FALLBACKS)


@register.simple_tag
def critical_assets_only():
    """
    Return only critical assets for priority loading
    """
    critical = {k: v for k, v in CDN_FALLBACKS.items() if v.get('critical', False)}
    return json.dumps(critical)