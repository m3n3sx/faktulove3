"""
Management command to optimize static assets and set up delivery optimization.
"""

import os
import json
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.staticfiles.finders import find
from faktury.services.asset_optimizer import asset_optimizer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Optimize static assets for better performance and delivery'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--minify-css',
            action='store_true',
            help='Minify CSS files'
        )
        parser.add_argument(
            '--minify-js',
            action='store_true',
            help='Minify JavaScript files'
        )
        parser.add_argument(
            '--create-bundles',
            action='store_true',
            help='Create asset bundles'
        )
        parser.add_argument(
            '--setup-lazy-loading',
            action='store_true',
            help='Set up lazy loading for images'
        )
        parser.add_argument(
            '--prepare-cdn',
            action='store_true',
            help='Prepare assets for CDN deployment'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='static/minified',
            help='Output directory for optimized assets'
        )
        parser.add_argument(
            '--bundle-config',
            type=str,
            help='Path to bundle configuration JSON file'
        )
        parser.add_argument(
            '--cdn-url',
            type=str,
            help='CDN base URL for asset deployment'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Asset Optimization')
        )
        
        try:
            output_dir = options['output_dir']
            
            if options['minify_css']:
                self.minify_css_files(output_dir)
            
            if options['minify_js']:
                self.minify_js_files(output_dir)
            
            if options['create_bundles']:
                self.create_asset_bundles(output_dir, options.get('bundle_config'))
            
            if options['setup_lazy_loading']:
                self.setup_lazy_loading(output_dir)
            
            if options['prepare_cdn']:
                self.prepare_cdn_deployment(options.get('cdn_url'))
            
            # If no specific option, run complete optimization
            if not any([
                options['minify_css'],
                options['minify_js'],
                options['create_bundles'],
                options['setup_lazy_loading'],
                options['prepare_cdn']
            ]):
                self.run_complete_optimization(output_dir, options)
            
            # Generate and display report
            self.display_optimization_report()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Asset optimization completed')
            )
            
        except Exception as e:
            logger.error(f"Asset optimization error: {e}")
            raise CommandError(f"Asset optimization failed: {e}")
    
    def minify_css_files(self, output_dir: str):
        """Minify CSS files"""
        self.stdout.write("🎨 Minifying CSS files...")
        
        # Find CSS files to optimize
        css_files = self.find_css_files()
        
        if not css_files:
            self.stdout.write("⚠️ No CSS files found to optimize")
            return
        
        # Optimize CSS files
        optimized_files = asset_optimizer.optimize_css_files(css_files, output_dir)
        
        self.stdout.write(f"✅ Optimized {len(optimized_files)} CSS files")
        for file_path in optimized_files:
            self.stdout.write(f"  📄 {os.path.basename(file_path)}")
    
    def minify_js_files(self, output_dir: str):
        """Minify JavaScript files"""
        self.stdout.write("⚡ Minifying JavaScript files...")
        
        # Find JS files to optimize
        js_files = self.find_js_files()
        
        if not js_files:
            self.stdout.write("⚠️ No JavaScript files found to optimize")
            return
        
        # Optimize JS files
        optimized_files = asset_optimizer.optimize_js_files(js_files, output_dir)
        
        self.stdout.write(f"✅ Optimized {len(optimized_files)} JavaScript files")
        for file_path in optimized_files:
            self.stdout.write(f"  📄 {os.path.basename(file_path)}")
    
    def create_asset_bundles(self, output_dir: str, config_path: str = None):
        """Create asset bundles"""
        self.stdout.write("📦 Creating asset bundles...")
        
        # Load bundle configuration
        bundle_config = self.load_bundle_config(config_path)
        
        if not bundle_config:
            self.stdout.write("⚠️ No bundle configuration provided, using default")
            bundle_config = self.get_default_bundle_config()
        
        # Create bundles
        bundle_paths = asset_optimizer.create_asset_bundles(bundle_config, output_dir)
        
        self.stdout.write(f"✅ Created {len(bundle_paths)} asset bundles:")
        for bundle_name, bundle_path in bundle_paths.items():
            self.stdout.write(f"  📦 {bundle_name} -> {os.path.basename(bundle_path)}")
    
    def setup_lazy_loading(self, output_dir: str):
        """Set up lazy loading for images"""
        self.stdout.write("🖼️ Setting up lazy loading...")
        
        # Set up lazy loading
        lazy_loading_assets = asset_optimizer.setup_lazy_loading()
        
        if lazy_loading_assets:
            # Save lazy loading CSS
            css_path = os.path.join(output_dir, 'lazy-loading.css')
            os.makedirs(os.path.dirname(css_path), exist_ok=True)
            
            with open(css_path, 'w') as f:
                f.write(lazy_loading_assets['css'])
            
            # Save lazy loading JavaScript
            js_path = os.path.join(output_dir, 'lazy-loading.js')
            with open(js_path, 'w') as f:
                # Extract script content from HTML
                script_content = lazy_loading_assets['script']
                script_content = script_content.replace('<script>', '').replace('</script>', '')
                f.write(script_content.strip())
            
            self.stdout.write("✅ Lazy loading assets created:")
            self.stdout.write(f"  🎨 CSS: {css_path}")
            self.stdout.write(f"  ⚡ JavaScript: {js_path}")
        else:
            self.stdout.write("❌ Failed to set up lazy loading")
    
    def prepare_cdn_deployment(self, cdn_url: str = None):
        """Prepare assets for CDN deployment"""
        self.stdout.write("🌐 Preparing CDN deployment...")
        
        # Set CDN URL if provided
        if cdn_url:
            settings.CDN_BASE_URL = cdn_url
            self.stdout.write(f"  🔗 CDN URL: {cdn_url}")
        
        # Get static root
        static_root = getattr(settings, 'STATIC_ROOT', 'staticfiles')
        manifest_path = os.path.join(static_root, 'asset-manifest.json')
        
        # Prepare CDN deployment
        cdn_result = asset_optimizer.prepare_cdn_deployment(static_root, manifest_path)
        
        if cdn_result.get('cdn_ready'):
            self.stdout.write("✅ CDN deployment prepared:")
            self.stdout.write(f"  📋 Manifest: {manifest_path}")
            self.stdout.write(f"  📁 Assets: {cdn_result.get('total_assets', 0)} files")
            
            # Display sample CDN URLs
            manifest = cdn_result.get('manifest', {})
            assets = manifest.get('assets', {})
            
            if assets:
                self.stdout.write("  🔗 Sample CDN URLs:")
                for asset_path, asset_info in list(assets.items())[:3]:
                    self.stdout.write(f"    {asset_info.get('cdn_url', asset_path)}")
        else:
            self.stdout.write(f"❌ CDN preparation failed: {cdn_result.get('error', 'Unknown error')}")
    
    def find_css_files(self) -> list:
        """Find CSS files to optimize"""
        css_files = []
        
        # Common CSS file patterns
        css_patterns = [
            'css/*.css',
            'faktury/css/*.css',
            'admin/css/*.css',
            'assets/css/*.css'
        ]
        
        for pattern in css_patterns:
            try:
                # This is a simplified approach - in a real implementation,
                # you'd use Django's static file finders more comprehensively
                if pattern.startswith('css/'):
                    css_files.extend([
                        'css/main.css',
                        'css/bootstrap.css',
                        'css/style.css'
                    ])
                elif pattern.startswith('faktury/'):
                    css_files.extend([
                        'faktury/css/faktury.css',
                        'faktury/css/forms.css'
                    ])
            except Exception as e:
                logger.warning(f"Error finding CSS files for pattern {pattern}: {e}")
        
        # Remove duplicates and filter existing files
        unique_files = []
        for css_file in set(css_files):
            if find(css_file):
                unique_files.append(css_file)
        
        return unique_files
    
    def find_js_files(self) -> list:
        """Find JavaScript files to optimize"""
        js_files = []
        
        # Common JS file patterns
        js_patterns = [
            'js/*.js',
            'faktury/js/*.js',
            'admin/js/*.js',
            'assets/js/*.js'
        ]
        
        for pattern in js_patterns:
            try:
                if pattern.startswith('js/'):
                    js_files.extend([
                        'js/main.js',
                        'js/bootstrap.js',
                        'js/jquery.js'
                    ])
                elif pattern.startswith('faktury/'):
                    js_files.extend([
                        'faktury/js/faktury.js',
                        'faktury/js/forms.js',
                        'faktury/js/ocr-upload.js'
                    ])
            except Exception as e:
                logger.warning(f"Error finding JS files for pattern {pattern}: {e}")
        
        # Remove duplicates and filter existing files
        unique_files = []
        for js_file in set(js_files):
            if find(js_file):
                unique_files.append(js_file)
        
        return unique_files
    
    def load_bundle_config(self, config_path: str = None) -> dict:
        """Load bundle configuration from JSON file"""
        if not config_path:
            return {}
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.stdout.write(f"⚠️ Bundle config file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            self.stdout.write(f"❌ Invalid JSON in bundle config: {e}")
            return {}
    
    def get_default_bundle_config(self) -> dict:
        """Get default bundle configuration"""
        return {
            'main.css': [
                'css/bootstrap.css',
                'css/main.css',
                'faktury/css/faktury.css'
            ],
            'main.js': [
                'js/jquery.js',
                'js/bootstrap.js',
                'js/main.js',
                'faktury/js/faktury.js'
            ],
            'admin.css': [
                'admin/css/base.css',
                'admin/css/dashboard.css'
            ],
            'admin.js': [
                'admin/js/core.js',
                'admin/js/admin.js'
            ]
        }
    
    def run_complete_optimization(self, output_dir: str, options: dict):
        """Run complete asset optimization"""
        self.stdout.write("🚀 Running complete asset optimization...")
        
        # Run all optimization steps
        self.minify_css_files(output_dir)
        self.minify_js_files(output_dir)
        self.create_asset_bundles(output_dir, options.get('bundle_config'))
        self.setup_lazy_loading(output_dir)
        
        if options.get('cdn_url'):
            self.prepare_cdn_deployment(options['cdn_url'])
        
        # Generate optimization guide
        self.generate_optimization_guide(output_dir)
    
    def generate_optimization_guide(self, output_dir: str):
        """Generate optimization implementation guide"""
        guide_content = """
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
    SetEnvIfNoCase Request_URI \\.(?:gif|jpe?g|png)$ no-gzip dont-vary
    SetEnvIfNoCase Request_URI \\.(?:exe|t?gz|zip|bz2|sit|rar)$ no-gzip dont-vary
</Location>

# Cache headers
<LocationMatch "\\.(css|js|png|jpg|jpeg|gif|ico|svg)$">
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
"""
        
        guide_path = os.path.join(output_dir, 'OPTIMIZATION_GUIDE.md')
        os.makedirs(os.path.dirname(guide_path), exist_ok=True)
        
        with open(guide_path, 'w') as f:
            f.write(guide_content.strip())
        
        self.stdout.write(f"📖 Optimization guide saved: {guide_path}")
    
    def display_optimization_report(self):
        """Display comprehensive optimization report"""
        self.stdout.write("\n📊 Asset Optimization Report")
        self.stdout.write("=" * 50)
        
        report = asset_optimizer.get_optimization_report()
        summary = report['summary']
        
        # Display summary
        self.stdout.write(f"📄 CSS files processed: {summary['css_files_processed']}")
        self.stdout.write(f"⚡ JS files processed: {summary['js_files_processed']}")
        self.stdout.write(f"📦 Bundles created: {summary['bundles_created']}")
        self.stdout.write(f"💾 Size saved: {summary['total_size_saved_kb']:.1f} KB")
        self.stdout.write(f"📈 Compression ratio: {summary['compression_ratio_percent']:.1f}%")
        
        # Display errors if any
        if summary['errors_count'] > 0:
            self.stdout.write(f"\n❌ Errors encountered: {summary['errors_count']}")
            for error in report['errors'][:5]:  # Show first 5 errors
                self.stdout.write(f"  • {error}")
        
        # Display recommendations
        recommendations = report['recommendations']
        if recommendations:
            self.stdout.write(f"\n💡 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:5], 1):  # Show first 5
                self.stdout.write(f"  {i}. {rec}")
        
        self.stdout.write("\n✅ Optimization complete! Check the generated files and implementation guide.")