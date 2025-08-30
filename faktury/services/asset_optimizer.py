"""
Asset Optimizer Service
Handles CSS and JavaScript minification, lazy loading, image optimization, and CDN-ready asset organization.
"""

import os
import re
import gzip
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.utils.safestring import mark_safe
import json

logger = logging.getLogger(__name__)


class CSSMinifier:
    """Minifies CSS files by removing whitespace, comments, and optimizing rules"""
    
    def __init__(self):
        self.compression_stats = {
            'original_size': 0,
            'minified_size': 0,
            'files_processed': 0
        }
    
    def minify_css(self, css_content: str) -> str:
        """Minify CSS content"""
        original_size = len(css_content)
        
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r'{\s*', '{', css_content)
        css_content = re.sub(r'}\s*', '}', css_content)
        css_content = re.sub(r':\s*', ':', css_content)
        css_content = re.sub(r';\s*', ';', css_content)
        css_content = re.sub(r',\s*', ',', css_content)
        
        # Remove trailing semicolons before closing braces
        css_content = re.sub(r';+}', '}', css_content)
        
        # Remove leading/trailing whitespace
        css_content = css_content.strip()
        
        # Update stats
        minified_size = len(css_content)
        self.compression_stats['original_size'] += original_size
        self.compression_stats['minified_size'] += minified_size
        self.compression_stats['files_processed'] += 1
        
        return css_content
    
    def optimize_css_properties(self, css_content: str) -> str:
        """Optimize CSS properties for better performance"""
        # Optimize color values
        css_content = re.sub(r'#([0-9a-fA-F])\1([0-9a-fA-F])\2([0-9a-fA-F])\3', r'#\1\2\3', css_content)
        
        # Optimize zero values
        css_content = re.sub(r'0px|0em|0rem|0%|0pt', '0', css_content)
        
        # Remove unnecessary quotes from URLs
        css_content = re.sub(r'url\(["\']([^"\']*)["\']', r'url(\1)', css_content)
        
        return css_content


class JavaScriptMinifier:
    """Minifies JavaScript files by removing whitespace, comments, and optimizing code"""
    
    def __init__(self):
        self.compression_stats = {
            'original_size': 0,
            'minified_size': 0,
            'files_processed': 0
        }
    
    def minify_js(self, js_content: str) -> str:
        """Basic JavaScript minification"""
        original_size = len(js_content)
        
        # Remove single-line comments (but preserve URLs)
        js_content = re.sub(r'(?<!:)//.*$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        js_content = re.sub(r';\s*', ';', js_content)
        js_content = re.sub(r'{\s*', '{', js_content)
        js_content = re.sub(r'}\s*', '}', js_content)
        js_content = re.sub(r',\s*', ',', js_content)
        
        # Remove trailing semicolons before closing braces
        js_content = re.sub(r';+}', '}', js_content)
        
        # Remove leading/trailing whitespace
        js_content = js_content.strip()
        
        # Update stats
        minified_size = len(js_content)
        self.compression_stats['original_size'] += original_size
        self.compression_stats['minified_size'] += minified_size
        self.compression_stats['files_processed'] += 1
        
        return js_content


class ImageOptimizer:
    """Optimizes images and implements WebP support"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        self.optimization_stats = {
            'images_processed': 0,
            'total_size_saved': 0,
            'webp_conversions': 0
        }
    
    def should_optimize_image(self, file_path: str) -> bool:
        """Check if image should be optimized"""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_formats
    
    def get_webp_path(self, image_path: str) -> str:
        """Get WebP version path for an image"""
        path = Path(image_path)
        return str(path.with_suffix('.webp'))
    
    def generate_responsive_sizes(self, image_path: str) -> List[Dict[str, Any]]:
        """Generate responsive image size configurations"""
        sizes = [
            {'width': 320, 'suffix': '_mobile'},
            {'width': 768, 'suffix': '_tablet'},
            {'width': 1200, 'suffix': '_desktop'},
            {'width': 1920, 'suffix': '_large'}
        ]
        
        responsive_images = []
        base_path = Path(image_path)
        
        for size_config in sizes:
            responsive_path = base_path.with_name(
                f"{base_path.stem}{size_config['suffix']}{base_path.suffix}"
            )
            responsive_images.append({
                'path': str(responsive_path),
                'width': size_config['width'],
                'media_query': f"(max-width: {size_config['width']}px)"
            })
        
        return responsive_images
    
    def create_lazy_loading_placeholder(self, width: int, height: int) -> str:
        """Create a base64 placeholder for lazy loading"""
        # Simple 1x1 transparent pixel
        placeholder = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}'%3E%3C/svg%3E"
        return placeholder.format(w=width, h=height)


class AssetBundler:
    """Bundles multiple assets into single files for better performance"""
    
    def __init__(self):
        self.bundles = {
            'css': {},
            'js': {}
        }
    
    def create_css_bundle(self, files: List[str], bundle_name: str) -> str:
        """Create a CSS bundle from multiple files"""
        minifier = CSSMinifier()
        bundled_content = []
        
        for file_path in files:
            try:
                full_path = find(file_path)
                if full_path and os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        minified = minifier.minify_css(content)
                        bundled_content.append(f"/* {file_path} */\n{minified}")
                else:
                    logger.warning(f"CSS file not found: {file_path}")
            except Exception as e:
                logger.error(f"Error processing CSS file {file_path}: {e}")
        
        bundle_content = '\n'.join(bundled_content)
        self.bundles['css'][bundle_name] = bundle_content
        
        return bundle_content
    
    def create_js_bundle(self, files: List[str], bundle_name: str) -> str:
        """Create a JavaScript bundle from multiple files"""
        minifier = JavaScriptMinifier()
        bundled_content = []
        
        for file_path in files:
            try:
                full_path = find(file_path)
                if full_path and os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        minified = minifier.minify_js(content)
                        bundled_content.append(f"/* {file_path} */\n{minified}")
                else:
                    logger.warning(f"JS file not found: {file_path}")
            except Exception as e:
                logger.error(f"Error processing JS file {file_path}: {e}")
        
        bundle_content = '\n'.join(bundled_content)
        self.bundles['js'][bundle_name] = bundle_content
        
        return bundle_content
    
    def save_bundle(self, bundle_content: str, bundle_path: str) -> str:
        """Save bundle to file and return versioned path"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(bundle_path), exist_ok=True)
            
            # Generate content hash for versioning
            content_hash = hashlib.md5(bundle_content.encode()).hexdigest()[:8]
            
            # Create versioned filename
            path = Path(bundle_path)
            versioned_path = path.with_name(f"{path.stem}.{content_hash}{path.suffix}")
            
            # Save bundle
            with open(versioned_path, 'w', encoding='utf-8') as f:
                f.write(bundle_content)
            
            # Create gzipped version
            gzipped_path = str(versioned_path) + '.gz'
            with gzip.open(gzipped_path, 'wt', encoding='utf-8') as f:
                f.write(bundle_content)
            
            return str(versioned_path)
            
        except Exception as e:
            logger.error(f"Error saving bundle {bundle_path}: {e}")
            return bundle_path


class LazyLoadingManager:
    """Manages lazy loading for images and heavy assets"""
    
    def __init__(self):
        self.lazy_load_threshold = 2  # Load images 2 viewport heights before they're visible
    
    def generate_lazy_image_html(self, src: str, alt: str = '', 
                                css_class: str = '', width: int = None, 
                                height: int = None) -> str:
        """Generate HTML for lazy-loaded image"""
        img_optimizer = ImageOptimizer()
        
        # Create placeholder
        placeholder = img_optimizer.create_lazy_loading_placeholder(
            width or 300, height or 200
        )
        
        # Generate responsive sizes if image exists
        webp_src = img_optimizer.get_webp_path(src)
        
        html = f'''
        <picture class="lazy-image {css_class}">
            <source data-srcset="{webp_src}" type="image/webp">
            <img 
                src="{placeholder}"
                data-src="{src}"
                alt="{alt}"
                class="lazy-load"
                loading="lazy"
                {f'width="{width}"' if width else ''}
                {f'height="{height}"' if height else ''}
            >
        </picture>
        '''
        
        return mark_safe(html.strip())
    
    def generate_lazy_loading_script(self) -> str:
        """Generate JavaScript for lazy loading functionality"""
        script = '''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Intersection Observer for lazy loading
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const src = img.getAttribute('data-src');
                        const srcset = img.getAttribute('data-srcset');
                        
                        if (src) {
                            img.src = src;
                            img.removeAttribute('data-src');
                        }
                        
                        if (srcset) {
                            img.srcset = srcset;
                            img.removeAttribute('data-srcset');
                        }
                        
                        img.classList.remove('lazy-load');
                        img.classList.add('lazy-loaded');
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '200px 0px'  // Load 200px before entering viewport
            });
            
            // Observe all lazy images
            document.querySelectorAll('img.lazy-load').forEach(img => {
                imageObserver.observe(img);
            });
            
            // Fallback for browsers without Intersection Observer
            if (!('IntersectionObserver' in window)) {
                document.querySelectorAll('img.lazy-load').forEach(img => {
                    const src = img.getAttribute('data-src');
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                    }
                });
            }
        });
        </script>
        '''
        
        return mark_safe(script.strip())


class CDNManager:
    """Manages CDN-ready asset organization and versioning"""
    
    def __init__(self):
        self.cdn_base_url = getattr(settings, 'CDN_BASE_URL', '')
        self.asset_manifest = {}
        self.cache_headers = {
            'css': 'max-age=31536000, immutable',  # 1 year
            'js': 'max-age=31536000, immutable',   # 1 year
            'images': 'max-age=2592000',           # 30 days
            'fonts': 'max-age=31536000, immutable' # 1 year
        }
    
    def generate_asset_manifest(self, static_root: str) -> Dict[str, Any]:
        """Generate asset manifest for CDN deployment"""
        manifest = {
            'version': self.get_build_version(),
            'assets': {},
            'bundles': {},
            'integrity': {}
        }
        
        # Scan static files
        static_path = Path(static_root)
        if static_path.exists():
            for file_path in static_path.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(static_path)
                    
                    # Generate file hash for integrity
                    file_hash = self.generate_file_hash(file_path)
                    
                    # Add to manifest
                    manifest['assets'][str(relative_path)] = {
                        'hash': file_hash,
                        'size': file_path.stat().st_size,
                        'cdn_url': self.get_cdn_url(str(relative_path)),
                        'cache_control': self.get_cache_control(file_path.suffix)
                    }
        
        self.asset_manifest = manifest
        return manifest
    
    def get_build_version(self) -> str:
        """Get current build version"""
        # Try to get from environment or generate from timestamp
        import time
        return os.environ.get('BUILD_VERSION', str(int(time.time())))
    
    def generate_file_hash(self, file_path: Path) -> str:
        """Generate SHA-256 hash for file integrity"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Error generating hash for {file_path}: {e}")
            return ''
    
    def get_cdn_url(self, asset_path: str) -> str:
        """Get CDN URL for asset"""
        if self.cdn_base_url:
            return f"{self.cdn_base_url.rstrip('/')}/{asset_path.lstrip('/')}"
        return asset_path
    
    def get_cache_control(self, file_extension: str) -> str:
        """Get appropriate cache control header for file type"""
        ext = file_extension.lower().lstrip('.')
        
        if ext in ['css', 'js']:
            return self.cache_headers['css']
        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
            return self.cache_headers['images']
        elif ext in ['woff', 'woff2', 'ttf', 'eot']:
            return self.cache_headers['fonts']
        else:
            return 'max-age=86400'  # 1 day default
    
    def save_manifest(self, output_path: str):
        """Save asset manifest to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(self.asset_manifest, f, indent=2)
            logger.info(f"Asset manifest saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving manifest: {e}")


class AssetOptimizer:
    """
    Main asset optimizer that coordinates all optimization tasks.
    """
    
    def __init__(self):
        self.css_minifier = CSSMinifier()
        self.js_minifier = JavaScriptMinifier()
        self.image_optimizer = ImageOptimizer()
        self.bundler = AssetBundler()
        self.lazy_loader = LazyLoadingManager()
        self.cdn_manager = CDNManager()
        
        self.optimization_results = {
            'css_files_processed': 0,
            'js_files_processed': 0,
            'images_processed': 0,
            'total_size_saved': 0,
            'bundles_created': 0,
            'errors': []
        }
    
    def optimize_css_files(self, css_files: List[str], output_dir: str) -> List[str]:
        """Optimize CSS files and return optimized file paths"""
        optimized_files = []
        
        for css_file in css_files:
            try:
                # Find the file
                file_path = find(css_file)
                if not file_path or not os.path.exists(file_path):
                    logger.warning(f"CSS file not found: {css_file}")
                    continue
                
                # Read and minify
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                minified_content = self.css_minifier.minify_css(content)
                optimized_content = self.css_minifier.optimize_css_properties(minified_content)
                
                # Generate output path
                output_path = os.path.join(output_dir, f"min_{os.path.basename(css_file)}")
                
                # Save optimized file
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(optimized_content)
                
                # Create gzipped version
                with gzip.open(f"{output_path}.gz", 'wt', encoding='utf-8') as f:
                    f.write(optimized_content)
                
                optimized_files.append(output_path)
                self.optimization_results['css_files_processed'] += 1
                
                # Calculate size savings
                original_size = len(content)
                optimized_size = len(optimized_content)
                self.optimization_results['total_size_saved'] += (original_size - optimized_size)
                
                logger.info(f"Optimized CSS: {css_file} ({original_size} -> {optimized_size} bytes)")
                
            except Exception as e:
                error_msg = f"Error optimizing CSS file {css_file}: {e}"
                logger.error(error_msg)
                self.optimization_results['errors'].append(error_msg)
        
        return optimized_files
    
    def optimize_js_files(self, js_files: List[str], output_dir: str) -> List[str]:
        """Optimize JavaScript files and return optimized file paths"""
        optimized_files = []
        
        for js_file in js_files:
            try:
                # Find the file
                file_path = find(js_file)
                if not file_path or not os.path.exists(file_path):
                    logger.warning(f"JS file not found: {js_file}")
                    continue
                
                # Read and minify
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                minified_content = self.js_minifier.minify_js(content)
                
                # Generate output path
                output_path = os.path.join(output_dir, f"min_{os.path.basename(js_file)}")
                
                # Save optimized file
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(minified_content)
                
                # Create gzipped version
                with gzip.open(f"{output_path}.gz", 'wt', encoding='utf-8') as f:
                    f.write(minified_content)
                
                optimized_files.append(output_path)
                self.optimization_results['js_files_processed'] += 1
                
                # Calculate size savings
                original_size = len(content)
                optimized_size = len(minified_content)
                self.optimization_results['total_size_saved'] += (original_size - optimized_size)
                
                logger.info(f"Optimized JS: {js_file} ({original_size} -> {optimized_size} bytes)")
                
            except Exception as e:
                error_msg = f"Error optimizing JS file {js_file}: {e}"
                logger.error(error_msg)
                self.optimization_results['errors'].append(error_msg)
        
        return optimized_files
    
    def create_asset_bundles(self, bundle_config: Dict[str, List[str]], output_dir: str) -> Dict[str, str]:
        """Create asset bundles based on configuration"""
        bundle_paths = {}
        
        for bundle_name, files in bundle_config.items():
            try:
                if bundle_name.endswith('.css'):
                    # CSS bundle
                    content = self.bundler.create_css_bundle(files, bundle_name)
                    bundle_path = os.path.join(output_dir, bundle_name)
                    
                elif bundle_name.endswith('.js'):
                    # JavaScript bundle
                    content = self.bundler.create_js_bundle(files, bundle_name)
                    bundle_path = os.path.join(output_dir, bundle_name)
                
                else:
                    logger.warning(f"Unknown bundle type: {bundle_name}")
                    continue
                
                # Save bundle with versioning
                versioned_path = self.bundler.save_bundle(content, bundle_path)
                bundle_paths[bundle_name] = versioned_path
                self.optimization_results['bundles_created'] += 1
                
                logger.info(f"Created bundle: {bundle_name} -> {versioned_path}")
                
            except Exception as e:
                error_msg = f"Error creating bundle {bundle_name}: {e}"
                logger.error(error_msg)
                self.optimization_results['errors'].append(error_msg)
        
        return bundle_paths
    
    def setup_lazy_loading(self) -> Dict[str, str]:
        """Set up lazy loading for images and heavy assets"""
        try:
            # Generate lazy loading script
            lazy_script = self.lazy_loader.generate_lazy_loading_script()
            
            # Generate CSS for lazy loading
            lazy_css = '''
            .lazy-image {
                display: block;
                position: relative;
                overflow: hidden;
            }
            
            .lazy-load {
                opacity: 0;
                transition: opacity 0.3s;
                filter: blur(5px);
            }
            
            .lazy-loaded {
                opacity: 1;
                filter: none;
            }
            
            .lazy-image::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                z-index: 1;
            }
            
            .lazy-loaded::before {
                display: none;
            }
            
            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
            '''
            
            return {
                'script': lazy_script,
                'css': lazy_css
            }
            
        except Exception as e:
            error_msg = f"Error setting up lazy loading: {e}"
            logger.error(error_msg)
            self.optimization_results['errors'].append(error_msg)
            return {}
    
    def prepare_cdn_deployment(self, static_root: str, manifest_path: str) -> Dict[str, Any]:
        """Prepare assets for CDN deployment"""
        try:
            # Generate asset manifest
            manifest = self.cdn_manager.generate_asset_manifest(static_root)
            
            # Save manifest
            self.cdn_manager.save_manifest(manifest_path)
            
            return {
                'manifest': manifest,
                'cdn_ready': True,
                'total_assets': len(manifest.get('assets', {}))
            }
            
        except Exception as e:
            error_msg = f"Error preparing CDN deployment: {e}"
            logger.error(error_msg)
            self.optimization_results['errors'].append(error_msg)
            return {'cdn_ready': False, 'error': error_msg}
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        css_stats = self.css_minifier.compression_stats
        js_stats = self.js_minifier.compression_stats
        
        total_original_size = css_stats['original_size'] + js_stats['original_size']
        total_minified_size = css_stats['minified_size'] + js_stats['minified_size']
        
        compression_ratio = (
            (total_original_size - total_minified_size) / total_original_size * 100
            if total_original_size > 0 else 0
        )
        
        return {
            'summary': {
                'css_files_processed': self.optimization_results['css_files_processed'],
                'js_files_processed': self.optimization_results['js_files_processed'],
                'bundles_created': self.optimization_results['bundles_created'],
                'total_size_saved_bytes': self.optimization_results['total_size_saved'],
                'total_size_saved_kb': self.optimization_results['total_size_saved'] / 1024,
                'compression_ratio_percent': compression_ratio,
                'errors_count': len(self.optimization_results['errors'])
            },
            'css_optimization': css_stats,
            'js_optimization': js_stats,
            'errors': self.optimization_results['errors'],
            'recommendations': self.generate_optimization_recommendations()
        }
    
    def generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on results"""
        recommendations = []
        
        css_stats = self.css_minifier.compression_stats
        js_stats = self.js_minifier.compression_stats
        
        # Check compression effectiveness
        if css_stats['files_processed'] > 0:
            css_ratio = (css_stats['original_size'] - css_stats['minified_size']) / css_stats['original_size'] * 100
            if css_ratio < 20:
                recommendations.append("CSS files have low compression ratio - consider removing unused styles")
        
        if js_stats['files_processed'] > 0:
            js_ratio = (js_stats['original_size'] - js_stats['minified_size']) / js_stats['original_size'] * 100
            if js_ratio < 30:
                recommendations.append("JavaScript files have low compression ratio - consider code splitting")
        
        # Check bundle creation
        if self.optimization_results['bundles_created'] == 0:
            recommendations.append("Consider creating asset bundles to reduce HTTP requests")
        
        # Check for errors
        if self.optimization_results['errors']:
            recommendations.append(f"Fix {len(self.optimization_results['errors'])} optimization errors")
        
        # General recommendations
        recommendations.extend([
            "Enable gzip compression on your web server",
            "Set appropriate cache headers for static assets",
            "Consider using a CDN for global asset delivery",
            "Implement lazy loading for images below the fold",
            "Use WebP format for images where supported"
        ])
        
        return recommendations


# Global asset optimizer instance
asset_optimizer = AssetOptimizer()