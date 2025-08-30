"""
Template tags for optimized asset loading and lazy loading functionality.
"""

import os
import json
from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.safestring import mark_safe
from django.core.cache import cache
from faktury.services.asset_optimizer import asset_optimizer

register = template.Library()


@register.simple_tag
def optimized_css(bundle_name, **kwargs):
    """
    Load optimized CSS bundle or fallback to individual files.
    
    Usage:
    {% optimized_css 'main' %}
    {% optimized_css 'admin' media='screen' %}
    """
    # Try to load minified bundle first
    bundle_path = f"minified/{bundle_name}.css"
    
    try:
        # Check if bundle exists
        if staticfiles_storage.exists(bundle_path):
            url = staticfiles_storage.url(bundle_path)
            
            # Add optional attributes
            attrs = []
            for key, value in kwargs.items():
                attrs.append(f'{key}="{value}"')
            
            attrs_str = ' ' + ' '.join(attrs) if attrs else ''
            
            return mark_safe(f'<link rel="stylesheet" href="{url}"{attrs_str}>')
        
        else:
            # Fallback to individual files
            return mark_safe(f'<!-- Bundle {bundle_name}.css not found, include individual files -->')
    
    except Exception:
        return mark_safe(f'<!-- Error loading CSS bundle: {bundle_name} -->')


@register.simple_tag
def optimized_js(bundle_name, **kwargs):
    """
    Load optimized JavaScript bundle or fallback to individual files.
    
    Usage:
    {% optimized_js 'main' %}
    {% optimized_js 'admin' defer=True %}
    """
    # Try to load minified bundle first
    bundle_path = f"minified/{bundle_name}.js"
    
    try:
        # Check if bundle exists
        if staticfiles_storage.exists(bundle_path):
            url = staticfiles_storage.url(bundle_path)
            
            # Add optional attributes
            attrs = []
            for key, value in kwargs.items():
                if value is True:
                    attrs.append(key)
                else:
                    attrs.append(f'{key}="{value}"')
            
            attrs_str = ' ' + ' '.join(attrs) if attrs else ''
            
            return mark_safe(f'<script src="{url}"{attrs_str}></script>')
        
        else:
            # Fallback to individual files
            return mark_safe(f'<!-- Bundle {bundle_name}.js not found, include individual files -->')
    
    except Exception:
        return mark_safe(f'<!-- Error loading JS bundle: {bundle_name} -->')


@register.simple_tag
def lazy_image(src, alt='', css_class='', width=None, height=None, **kwargs):
    """
    Generate lazy-loaded image with WebP support and responsive sizing.
    
    Usage:
    {% lazy_image 'images/hero.jpg' alt='Hero image' width=800 height=600 %}
    {% lazy_image 'images/thumbnail.jpg' css_class='thumbnail' %}
    """
    try:
        # Generate WebP path
        webp_src = src.replace('.jpg', '.webp').replace('.jpeg', '.webp').replace('.png', '.webp')
        
        # Create placeholder
        placeholder = f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {width or 300} {height or 200}'%3E%3C/svg%3E"
        
        # Build attributes
        img_attrs = []
        if width:
            img_attrs.append(f'width="{width}"')
        if height:
            img_attrs.append(f'height="{height}"')
        
        for key, value in kwargs.items():
            img_attrs.append(f'{key}="{value}"')
        
        attrs_str = ' ' + ' '.join(img_attrs) if img_attrs else ''
        
        # Generate HTML
        html = f'''
        <picture class="lazy-image {css_class}">
            <source data-srcset="{staticfiles_storage.url(webp_src)}" type="image/webp">
            <img 
                src="{placeholder}"
                data-src="{staticfiles_storage.url(src)}"
                alt="{alt}"
                class="lazy-load"
                loading="lazy"
                {attrs_str}
            >
        </picture>
        '''
        
        return mark_safe(html.strip())
    
    except Exception as e:
        # Fallback to regular image
        return mark_safe(f'<img src="{staticfiles_storage.url(src)}" alt="{alt}" class="{css_class}">')


@register.simple_tag
def lazy_loading_script():
    """
    Include lazy loading JavaScript functionality.
    
    Usage:
    {% lazy_loading_script %}
    """
    script_path = "minified/lazy-loading.js"
    
    try:
        if staticfiles_storage.exists(script_path):
            url = staticfiles_storage.url(script_path)
            return mark_safe(f'<script src="{url}" defer></script>')
        else:
            # Inline fallback script
            return mark_safe(asset_optimizer.lazy_loader.generate_lazy_loading_script())
    
    except Exception:
        return mark_safe('<!-- Lazy loading script not available -->')


@register.simple_tag
def lazy_loading_css():
    """
    Include lazy loading CSS styles.
    
    Usage:
    {% lazy_loading_css %}
    """
    css_path = "minified/lazy-loading.css"
    
    try:
        if staticfiles_storage.exists(css_path):
            url = staticfiles_storage.url(css_path)
            return mark_safe(f'<link rel="stylesheet" href="{url}">')
        else:
            # Inline fallback CSS
            lazy_assets = asset_optimizer.setup_lazy_loading()
            if lazy_assets and 'css' in lazy_assets:
                return mark_safe(f'<style>{lazy_assets["css"]}</style>')
    
    except Exception:
        return mark_safe('<!-- Lazy loading CSS not available -->')


@register.simple_tag
def preload_asset(asset_path, asset_type='auto', **kwargs):
    """
    Generate preload link for critical assets.
    
    Usage:
    {% preload_asset 'css/critical.css' 'style' %}
    {% preload_asset 'js/main.js' 'script' %}
    {% preload_asset 'fonts/main.woff2' 'font' crossorigin='anonymous' %}
    """
    try:
        url = staticfiles_storage.url(asset_path)
        
        # Auto-detect asset type if not specified
        if asset_type == 'auto':
            ext = os.path.splitext(asset_path)[1].lower()
            if ext == '.css':
                asset_type = 'style'
            elif ext == '.js':
                asset_type = 'script'
            elif ext in ['.woff', '.woff2', '.ttf', '.eot']:
                asset_type = 'font'
            elif ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                asset_type = 'image'
            else:
                asset_type = 'fetch'
        
        # Build attributes
        attrs = [f'rel="preload"', f'href="{url}"', f'as="{asset_type}"']
        
        for key, value in kwargs.items():
            attrs.append(f'{key}="{value}"')
        
        return mark_safe(f'<link {" ".join(attrs)}>')
    
    except Exception:
        return mark_safe(f'<!-- Error preloading asset: {asset_path} -->')


@register.simple_tag
def prefetch_asset(asset_path):
    """
    Generate prefetch link for future navigation assets.
    
    Usage:
    {% prefetch_asset 'js/next-page.js' %}
    """
    try:
        url = staticfiles_storage.url(asset_path)
        return mark_safe(f'<link rel="prefetch" href="{url}">')
    except Exception:
        return mark_safe(f'<!-- Error prefetching asset: {asset_path} -->')


@register.simple_tag
def preconnect_domain(domain, crossorigin=False):
    """
    Generate preconnect link for external domains.
    
    Usage:
    {% preconnect_domain 'https://fonts.googleapis.com' %}
    {% preconnect_domain 'https://cdn.example.com' crossorigin=True %}
    """
    attrs = ['rel="preconnect"', f'href="{domain}"']
    
    if crossorigin:
        attrs.append('crossorigin')
    
    return mark_safe(f'<link {" ".join(attrs)}>')


@register.simple_tag
def asset_manifest():
    """
    Get asset manifest for CDN deployment.
    
    Usage:
    {% asset_manifest as manifest %}
    """
    try:
        manifest_path = os.path.join(settings.STATIC_ROOT or 'staticfiles', 'asset-manifest.json')
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    
    return {}


@register.filter
def cdn_url(asset_path):
    """
    Convert asset path to CDN URL if CDN is configured.
    
    Usage:
    {{ 'css/main.css'|cdn_url }}
    """
    try:
        cdn_base = getattr(settings, 'CDN_BASE_URL', '')
        
        if cdn_base:
            return f"{cdn_base.rstrip('/')}/{asset_path.lstrip('/')}"
        else:
            return staticfiles_storage.url(asset_path)
    except Exception:
        return asset_path


@register.simple_tag
def critical_css(css_content):
    """
    Inline critical CSS for above-the-fold content.
    
    Usage:
    {% critical_css %}
    body { font-family: Arial, sans-serif; }
    .header { background: #333; }
    {% endcritical_css %}
    """
    minifier = asset_optimizer.css_minifier
    minified_css = minifier.minify_css(css_content)
    
    return mark_safe(f'<style>{minified_css}</style>')


@register.inclusion_tag('asset_optimization/performance_hints.html')
def performance_hints():
    """
    Include performance optimization hints and resource hints.
    
    Usage:
    {% performance_hints %}
    """
    return {
        'preconnect_domains': [
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
        ],
        'dns_prefetch_domains': [
            '//cdn.example.com',
            '//analytics.google.com',
        ]
    }


@register.simple_tag(takes_context=True)
def asset_performance_data(context):
    """
    Collect asset performance data for monitoring.
    
    Usage:
    {% asset_performance_data %}
    """
    request = context.get('request')
    if not request:
        return ''
    
    # Generate performance monitoring script
    script = '''
    <script>
    window.addEventListener('load', function() {
        if ('performance' in window) {
            const resources = performance.getEntriesByType('resource');
            const assetPerformance = {
                css: [],
                js: [],
                images: [],
                fonts: []
            };
            
            resources.forEach(resource => {
                const url = resource.name;
                const duration = resource.duration;
                const size = resource.transferSize || 0;
                
                if (url.includes('.css')) {
                    assetPerformance.css.push({url, duration, size});
                } else if (url.includes('.js')) {
                    assetPerformance.js.push({url, duration, size});
                } else if (url.match(/\\.(jpg|jpeg|png|gif|webp|svg)$/)) {
                    assetPerformance.images.push({url, duration, size});
                } else if (url.match(/\\.(woff|woff2|ttf|eot)$/)) {
                    assetPerformance.fonts.push({url, duration, size});
                }
            });
            
            // Send to performance monitoring endpoint
            if (assetPerformance.css.length > 0 || assetPerformance.js.length > 0) {
                fetch('/api/performance/assets/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    },
                    body: JSON.stringify(assetPerformance)
                }).catch(console.error);
            }
        }
    });
    </script>
    '''
    
    return mark_safe(script)


@register.simple_tag
def webp_support_detection():
    """
    Generate WebP support detection script.
    
    Usage:
    {% webp_support_detection %}
    """
    script = '''
    <script>
    (function() {
        function supportsWebP(callback) {
            const webP = new Image();
            webP.onload = webP.onerror = function () {
                callback(webP.height === 2);
            };
            webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
        }
        
        supportsWebP(function(supported) {
            if (supported) {
                document.documentElement.classList.add('webp');
            } else {
                document.documentElement.classList.add('no-webp');
            }
        });
    })();
    </script>
    '''
    
    return mark_safe(script)


# Create the template for performance hints
@register.simple_tag
def create_performance_hints_template():
    """Create the performance hints template file"""
    template_dir = os.path.join(settings.BASE_DIR, 'faktury', 'templates', 'asset_optimization')
    os.makedirs(template_dir, exist_ok=True)
    
    template_content = '''<!-- Performance optimization hints -->
{% for domain in preconnect_domains %}
<link rel="preconnect" href="{{ domain }}">
{% endfor %}

{% for domain in dns_prefetch_domains %}
<link rel="dns-prefetch" href="{{ domain }}">
{% endfor %}

<!-- Resource hints for better performance -->
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
'''
    
    template_path = os.path.join(template_dir, 'performance_hints.html')
    with open(template_path, 'w') as f:
        f.write(template_content)
    
    return template_path