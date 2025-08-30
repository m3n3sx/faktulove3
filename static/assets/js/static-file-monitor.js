/**
 * Static File Loading Monitor - tracks and reports missing static files
 */
class StaticFileMonitor {
    constructor() {
        this.missingFiles = new Set();
        this.loadedFiles = new Set();
        this.isInitialized = false;
        this.reportingEnabled = true;
        
        if (window.StaticFileMonitor && window.StaticFileMonitor.isInitialized) {
            return window.StaticFileMonitor;
        }
        
        this.init();
        window.StaticFileMonitor = this;
    }

    init() {
        if (this.isInitialized) return;
        
        try {
            this.setupResourceMonitoring();
            this.checkCriticalFiles();
            this.setupHealthCheck();
            this.isInitialized = true;
            console.log('StaticFileMonitor initialized');
        } catch (error) {
            console.error('Failed to initialize StaticFileMonitor:', error);
        }
    }

    setupResourceMonitoring() {
        // Monitor resource loading errors
        window.addEventListener('error', (event) => {
            if (event.target && (event.target.tagName === 'LINK' || event.target.tagName === 'SCRIPT' || event.target.tagName === 'IMG')) {
                this.handleMissingResource(event.target);
            }
        }, true);

        // Monitor CSS loading
        document.addEventListener('DOMContentLoaded', () => {
            this.checkCSSFiles();
        });
    }

    handleMissingResource(element) {
        const src = element.src || element.href;
        if (src && !this.missingFiles.has(src)) {
            this.missingFiles.add(src);
            
            const resourceInfo = {
                type: element.tagName.toLowerCase(),
                src: src,
                timestamp: new Date().toISOString(),
                page: window.location.pathname
            };
            
            console.error('Missing static file:', resourceInfo);
            this.reportMissingFile(resourceInfo);
        }
    }

    checkCriticalFiles() {
        const criticalFiles = [
            { type: 'css', path: '/static/assets/css/style.css' },
            { type: 'css', path: '/static/assets/css/remixicon.css' },
            { type: 'js', path: '/static/assets/js/lib/bootstrap.bundle.min.js' },
            { type: 'js', path: '/staticfiles/js/react.production.min.js' },
            { type: 'js', path: '/staticfiles/js/react-dom.production.min.js' }
        ];

        criticalFiles.forEach(file => {
            this.checkFileExists(file.path, file.type);
        });
    }

    checkFileExists(path, type) {
        if (type === 'css') {
            // Check if CSS file is loaded
            const links = document.querySelectorAll('link[rel="stylesheet"]');
            const found = Array.from(links).some(link => link.href.includes(path));
            
            if (!found) {
                this.missingFiles.add(path);
                this.reportMissingFile({
                    type: 'css',
                    src: path,
                    timestamp: new Date().toISOString(),
                    page: window.location.pathname,
                    critical: true
                });
            }
        } else if (type === 'js') {
            // Check if JS file is loaded
            const scripts = document.querySelectorAll('script[src]');
            const found = Array.from(scripts).some(script => script.src.includes(path));
            
            if (!found) {
                this.missingFiles.add(path);
                this.reportMissingFile({
                    type: 'js',
                    src: path,
                    timestamp: new Date().toISOString(),
                    page: window.location.pathname,
                    critical: true
                });
            }
        }
    }

    checkCSSFiles() {
        // Check if CSS files are actually loading content
        const testElement = document.createElement('div');
        testElement.className = 'ri-home-line'; // RemixIcon test
        testElement.style.position = 'absolute';
        testElement.style.left = '-9999px';
        document.body.appendChild(testElement);
        
        setTimeout(() => {
            const computed = window.getComputedStyle(testElement);
            if (computed.fontFamily.indexOf('remixicon') === -1) {
                this.reportMissingFile({
                    type: 'font',
                    src: '/static/assets/fonts/remixicon.woff2',
                    timestamp: new Date().toISOString(),
                    page: window.location.pathname,
                    critical: true,
                    message: 'RemixIcon font not loaded'
                });
            }
            document.body.removeChild(testElement);
        }, 100);
    }

    reportMissingFile(fileInfo) {
        if (!this.reportingEnabled) return;
        
        // Log to console
        console.error('Static file missing:', fileInfo);
        
        // Send to server (with rate limiting)
        if (fileInfo.critical) {
            this.sendToServer(fileInfo);
        }
        
        // Show user notification for critical files
        if (fileInfo.critical && typeof Toastify !== 'undefined') {
            Toastify({
                text: `Błąd ładowania pliku: ${fileInfo.src.split('/').pop()}`,
                duration: 5000,
                gravity: "top",
                position: "right",
                backgroundColor: "#dc3545"
            }).showToast();
        }
    }

    sendToServer(fileInfo) {
        try {
            fetch('/api/static-file-error/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify(fileInfo)
            }).catch(() => {
                // Silently fail to prevent error loops
            });
        } catch (e) {
            // Silently fail
        }
    }

    setupHealthCheck() {
        // Create health check endpoint
        window.staticFileHealthCheck = () => {
            return {
                missing: Array.from(this.missingFiles),
                loaded: Array.from(this.loadedFiles),
                status: this.missingFiles.size === 0 ? 'healthy' : 'degraded',
                timestamp: new Date().toISOString()
            };
        };
    }

    getMissingFiles() {
        return Array.from(this.missingFiles);
    }

    getStatus() {
        return {
            missing: this.getMissingFiles(),
            loaded: Array.from(this.loadedFiles),
            healthy: this.missingFiles.size === 0
        };
    }

    enableReporting() {
        this.reportingEnabled = true;
    }

    disableReporting() {
        this.reportingEnabled = false;
    }
}

// Initialize safely
try {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new StaticFileMonitor();
        });
    } else {
        new StaticFileMonitor();
    }
} catch (error) {
    console.error('Failed to initialize StaticFileMonitor:', error);
}