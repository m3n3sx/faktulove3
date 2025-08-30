/**
 * Performance Optimizer - optimizes static file loading and caching
 */
class PerformanceOptimizer {
    constructor() {
        this.isInitialized = false;
        this.loadTimes = new Map();
        this.criticalResources = new Set();
        this.deferredResources = new Set();
        
        if (window.PerformanceOptimizer && window.PerformanceOptimizer.isInitialized) {
            return window.PerformanceOptimizer;
        }
        
        this.init();
        window.PerformanceOptimizer = this;
    }

    init() {
        if (this.isInitialized) return;
        
        try {
            this.setupResourcePrioritization();
            this.setupLazyLoading();
            this.setupCaching();
            this.setupCompressionDetection();
            this.monitorPerformance();
            this.isInitialized = true;
            console.log('PerformanceOptimizer initialized');
        } catch (error) {
            console.error('Failed to initialize PerformanceOptimizer:', error);
        }
    }

    setupResourcePrioritization() {
        // Define critical resources that should load first
        this.criticalResources = new Set([
            '/static/assets/css/style.css',
            '/static/assets/css/remixicon.css',
            '/static/assets/js/lib/bootstrap.bundle.min.js',
            '/static/assets/js/safe-error-handler.js'
        ]);

        // Define resources that can be deferred
        this.deferredResources = new Set([
            '/static/assets/js/charts-manager.js',
            '/static/assets/js/tables-manager.js',
            '/static/assets/css/lib/prism.css',
            '/static/assets/js/lib/prism.js'
        ]);

        // Add resource hints for critical resources
        this.addResourceHints();
    }

    addResourceHints() {
        const head = document.head;
        
        // Add preload hints for critical CSS
        this.criticalResources.forEach(resource => {
            if (resource.endsWith('.css')) {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.href = resource;
                link.as = 'style';
                link.onload = () => {
                    link.rel = 'stylesheet';
                };
                head.appendChild(link);
            }
        });

        // Add prefetch hints for deferred resources
        this.deferredResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = resource;
            head.appendChild(link);
        });
    }

    setupLazyLoading() {
        // Lazy load non-critical images
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            imageObserver.unobserve(img);
                        }
                    }
                });
            });

            // Observe images with data-src attribute
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }

        // Lazy load non-critical scripts
        this.setupScriptLazyLoading();
    }

    setupScriptLazyLoading() {
        // Load scripts based on user interaction or page visibility
        const loadDeferredScripts = () => {
            this.deferredResources.forEach(resource => {
                if (resource.endsWith('.js')) {
                    this.loadScript(resource);
                }
            });
        };

        // Load on first user interaction
        const interactionEvents = ['click', 'scroll', 'keydown', 'touchstart'];
        const loadOnInteraction = () => {
            loadDeferredScripts();
            interactionEvents.forEach(event => {
                document.removeEventListener(event, loadOnInteraction);
            });
        };

        interactionEvents.forEach(event => {
            document.addEventListener(event, loadOnInteraction, { once: true, passive: true });
        });

        // Fallback: load after 3 seconds
        setTimeout(loadDeferredScripts, 3000);
    }

    loadScript(src) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = src;
            script.async = true;
            
            const startTime = performance.now();
            
            script.onload = () => {
                const loadTime = performance.now() - startTime;
                this.loadTimes.set(src, loadTime);
                resolve();
            };
            
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    setupCaching() {
        // Implement service worker for caching (if supported)
        if ('serviceWorker' in navigator) {
            this.registerServiceWorker();
        }

        // Setup localStorage caching for small resources
        this.setupLocalStorageCache();
    }

    registerServiceWorker() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    }

    setupLocalStorageCache() {
        // Cache small CSS/JS files in localStorage
        const cacheableResources = [
            '/static/assets/css/icon-fallbacks.css',
            '/static/assets/js/csrf-utils.js'
        ];

        cacheableResources.forEach(resource => {
            this.cacheResourceInLocalStorage(resource);
        });
    }

    async cacheResourceInLocalStorage(url) {
        try {
            const cacheKey = `cache_${url}`;
            const cached = localStorage.getItem(cacheKey);
            
            if (!cached) {
                const response = await fetch(url);
                const content = await response.text();
                
                // Only cache if content is small (< 50KB)
                if (content.length < 50000) {
                    localStorage.setItem(cacheKey, content);
                    localStorage.setItem(`${cacheKey}_timestamp`, Date.now().toString());
                }
            }
        } catch (error) {
            console.warn(`Failed to cache ${url}:`, error);
        }
    }

    setupCompressionDetection() {
        // Detect if gzip compression is enabled
        const testUrl = '/static/assets/css/style.css';
        
        fetch(testUrl, { method: 'HEAD' })
            .then(response => {
                const encoding = response.headers.get('content-encoding');
                if (encoding && (encoding.includes('gzip') || encoding.includes('br'))) {
                    console.log('✓ Compression enabled:', encoding);
                } else {
                    console.warn('⚠ Compression not detected - consider enabling gzip/brotli');
                }
            })
            .catch(() => {
                // Silently fail
            });
    }

    monitorPerformance() {
        // Monitor Core Web Vitals
        this.measureCoreWebVitals();
        
        // Monitor resource loading times
        this.monitorResourceTiming();
        
        // Setup performance reporting
        this.setupPerformanceReporting();
    }

    measureCoreWebVitals() {
        // Largest Contentful Paint (LCP)
        if ('PerformanceObserver' in window) {
            try {
                const lcpObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    
                    if (lastEntry.startTime > 2500) {
                        console.warn(`⚠ LCP is slow: ${lastEntry.startTime.toFixed(0)}ms (should be < 2500ms)`);
                    } else {
                        console.log(`✓ LCP: ${lastEntry.startTime.toFixed(0)}ms`);
                    }
                });
                
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                // LCP not supported
            }

            // First Input Delay (FID) - approximation
            try {
                const fidObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach(entry => {
                        const fid = entry.processingStart - entry.startTime;
                        if (fid > 100) {
                            console.warn(`⚠ FID is slow: ${fid.toFixed(0)}ms (should be < 100ms)`);
                        } else {
                            console.log(`✓ FID: ${fid.toFixed(0)}ms`);
                        }
                    });
                });
                
                fidObserver.observe({ entryTypes: ['first-input'] });
            } catch (e) {
                // FID not supported
            }
        }
    }

    monitorResourceTiming() {
        if (window.performance && window.performance.getEntriesByType) {
            setTimeout(() => {
                const resources = window.performance.getEntriesByType('resource');
                const slowResources = resources.filter(resource => 
                    resource.duration > 1000 && 
                    (resource.name.includes('/static/') || resource.name.includes('/media/'))
                );

                if (slowResources.length > 0) {
                    console.warn('⚠ Slow loading resources:', slowResources.map(r => ({
                        name: r.name.split('/').pop(),
                        duration: Math.round(r.duration)
                    })));
                }
            }, 5000);
        }
    }

    setupPerformanceReporting() {
        // Report performance metrics to server
        window.addEventListener('load', () => {
            setTimeout(() => {
                this.reportPerformanceMetrics();
            }, 2000);
        });
    }

    reportPerformanceMetrics() {
        if (!window.performance || !window.performance.timing) return;

        const timing = window.performance.timing;
        const metrics = {
            pageLoadTime: timing.loadEventEnd - timing.navigationStart,
            domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
            firstPaint: this.getFirstPaint(),
            resourceCount: window.performance.getEntriesByType('resource').length,
            timestamp: new Date().toISOString(),
            url: window.location.pathname
        };

        // Only report if page load is slow
        if (metrics.pageLoadTime > 3000) {
            this.sendMetricsToServer(metrics);
        }
    }

    getFirstPaint() {
        if (window.performance && window.performance.getEntriesByType) {
            const paintEntries = window.performance.getEntriesByType('paint');
            const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
            return firstPaint ? firstPaint.startTime : null;
        }
        return null;
    }

    sendMetricsToServer(metrics) {
        try {
            fetch('/api/performance-metrics/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify(metrics)
            }).catch(() => {
                // Silently fail
            });
        } catch (e) {
            // Silently fail
        }
    }

    // Public API methods
    getPerformanceReport() {
        return {
            loadTimes: Object.fromEntries(this.loadTimes),
            criticalResources: Array.from(this.criticalResources),
            deferredResources: Array.from(this.deferredResources),
            timestamp: new Date().toISOString()
        };
    }

    optimizeImages() {
        // Convert images to WebP if supported
        if (this.supportsWebP()) {
            document.querySelectorAll('img[src$=".jpg"], img[src$=".png"]').forEach(img => {
                const webpSrc = img.src.replace(/\.(jpg|png)$/, '.webp');
                
                // Test if WebP version exists
                const testImg = new Image();
                testImg.onload = () => {
                    img.src = webpSrc;
                };
                testImg.src = webpSrc;
            });
        }
    }

    supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }

    enableCriticalCSS() {
        // Inline critical CSS for above-the-fold content
        const criticalCSS = `
            .dashboard-main { display: block; }
            .btn { padding: 8px 16px; border-radius: 4px; }
            .alert { padding: 12px; margin: 16px 0; border-radius: 4px; }
        `;
        
        const style = document.createElement('style');
        style.textContent = criticalCSS;
        document.head.insertBefore(style, document.head.firstChild);
    }
}

// Initialize safely
try {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new PerformanceOptimizer();
        });
    } else {
        new PerformanceOptimizer();
    }
} catch (error) {
    console.error('Failed to initialize PerformanceOptimizer:', error);
}