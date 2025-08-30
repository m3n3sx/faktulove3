# Asset Optimization Implementation Guide

## Files Generated

### Minified Assets
- CSS files: Minified and optimized for production
- JavaScript files: Minified and compressed
- Gzipped versions: Pre-compressed for web server delivery

### Bundles
- main.css: Combined CSS bundle for main site
- main.js: Combined JavaScript bundle for main site
- admin.css: Admin-specific CSS bundle
- admin.js: Admin-specific JavaScript bundle

### Lazy Loading
- lazy-loading.css: Styles for lazy loading functionality
- lazy-loading.js: JavaScript for intersection observer-based lazy loading

## Implementation Steps

### 1. Update Django Settings

Add to your settings.py:

```python
# Static files optimization
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# CDN configuration (if using CDN)
CDN_BASE_URL = 'https://your-cdn-domain.com'

# Asset optimization settings
ASSET_OPTIMIZATION = {
    'MINIFY_CSS': True,
    'MINIFY_JS': True,
    'USE_BUNDLES': True,
    'LAZY_LOADING': True,
}
```

### 2. Update Templates

Replace individual asset includes with bundles:

```html
<!-- Before -->
<link rel="stylesheet" href="{% static 'css/bootstrap.css' %}">
<link rel="stylesheet" href="{% static 'css/main.css' %}">
<link rel="stylesheet" href="{% static 'faktury/css/faktury.css' %}">

<!-- After -->
<link rel="stylesheet" href="{% static 'minified/main.css' %}">
```

### 3. Implement Lazy Loading

Add lazy loading CSS and JS to your base template:

```html
<link rel="stylesheet" href="{% static 'minified/lazy-loading.css' %}">
<script src="{% static 'minified/lazy-loading.js' %}" defer></script>
```

Use lazy loading for images:

```html
<!-- Replace regular img tags -->
<img src="{% static 'images/large-image.jpg' %}" alt="Description">

<!-- With lazy loading -->
<picture class="lazy-image">
    <source data-srcset="{% static 'images/large-image.webp' %}" type="image/webp">
    <img 
        src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 200'%3E%3C/svg%3E"
        data-src="{% static 'images/large-image.jpg' %}"
        alt="Description"
        class="lazy-load"
        loading="lazy"
    >
</picture>
```

### 4. Web Server Configuration

#### Nginx Configuration

```nginx
# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/css application/javascript application/json image/svg+xml;

# Static file caching
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    
    # Serve pre-compressed files
    gzip_static on;
}

# WebP support
location ~* \.(jpg|jpeg|png)$ {
    add_header Vary Accept;
    try_files $uri.webp $uri =404;
}
```

#### Apache Configuration

```apache
# Enable compression
LoadModule deflate_module modules/mod_deflate.so
<Location "/static/">
    SetOutputFilter DEFLATE
    SetEnvIfNoCase Request_URI \.(?:gif|jpe?g|png)$ no-gzip dont-vary
    SetEnvIfNoCase Request_URI \.(?:exe|t?gz|zip|bz2|sit|rar)$ no-gzip dont-vary
</Location>

# Cache headers
<LocationMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 year"
</LocationMatch>
```

### 5. Performance Monitoring

Monitor the impact of optimizations:

```python
# Add to your performance monitoring
PERFORMANCE_BUDGETS = {
    'css_load_time': 500,  # 500ms
    'js_load_time': 1000,  # 1s
    'image_load_time': 2000,  # 2s
    'total_page_size': 2048,  # 2MB
}
```

## Best Practices

1. **Regular Optimization**: Run asset optimization as part of your deployment process
2. **Bundle Splitting**: Create separate bundles for different page types
3. **Critical CSS**: Inline critical CSS for above-the-fold content
4. **Progressive Enhancement**: Ensure lazy loading degrades gracefully
5. **Performance Testing**: Regularly test with tools like Lighthouse

## Troubleshooting

### Common Issues

1. **Missing Files**: Ensure all referenced files exist in static directories
2. **Bundle Errors**: Check bundle configuration for correct file paths
3. **Lazy Loading**: Verify Intersection Observer support or provide fallbacks
4. **CDN Issues**: Test CDN URLs and ensure proper CORS headers

### Performance Validation

Use these commands to validate optimizations:

```bash
# Test gzip compression
curl -H "Accept-Encoding: gzip" -I http://your-site.com/static/minified/main.css

# Check file sizes
ls -lh static/minified/

# Validate lazy loading
# Use browser dev tools to check network tab for deferred image loading
```