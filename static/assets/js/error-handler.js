class ErrorHandler {
    constructor() {
        this.errors = [];
        this.assetErrors = [];
        this.userNotifications = [];
        this.isInitialized = false;
        this.config = {
            maxErrors: 50,
            showUserNotifications: true,
            logToConsole: true,
            logToServer: false,
            criticalAssets: ['jquery', 'bootstrap', 'app.js', 'style.css']
        };
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        this.setupGlobalErrorHandler();
        this.setupUnhandledRejectionHandler();
        this.setupAssetLoadingMonitor();
        this.setupResourceErrorHandler();
        this.initNotificationSystem();
        this.isInitialized = true;
        this.log('ErrorHandler initialized successfully');
    }

    setupGlobalErrorHandler() {
        window.addEventListener('error', (event) => {
            const error = {
                type: 'javascript',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href
            };
            this.handleError(error);
        });
    }

    setupUnhandledRejectionHandler() {
        window.addEventListener('unhandledrejection', (event) => {
            const error = {
                type: 'promise_rejection',
                message: event.reason?.message || 'Unhandled promise rejection',
                reason: event.reason,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href
            };
            this.handleError(error);
        });
    }

    setupAssetLoadingMonitor() {
        document.addEventListener('DOMContentLoaded', () => {
            this.monitorScriptLoading();
            this.monitorStylesheetLoading();
        });
    }

    setupResourceErrorHandler() {
        window.addEventListener('error', (event) => {
            if (event.target !== window) {
                const element = event.target;
                const assetError = {
                    type: 'asset_load_failure',
                    tagName: element.tagName,
                    src: element.src || element.href,
                    timestamp: new Date().toISOString(),
                    critical: this.isCriticalAsset(element.src || element.href)
                };
                this.handleAssetError(assetError);
            }
        }, true);
    }

    monitorScriptLoading() {
        const scripts = document.querySelectorAll('script[src]');
        scripts.forEach(script => {
            if (!script.hasAttribute('data-monitored')) {
                script.setAttribute('data-monitored', 'true');
                script.addEventListener('error', () => {
                    const assetError = {
                        type: 'script_load_failure',
                        src: script.src,
                        timestamp: new Date().toISOString(),
                        critical: this.isCriticalAsset(script.src)
                    };
                    this.handleAssetError(assetError);
                });
                script.addEventListener('load', () => {
                    this.log(`Script loaded successfully: ${script.src}`);
                });
            }
        });
    }

    monitorStylesheetLoading() {
        const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
        stylesheets.forEach(link => {
            if (!link.hasAttribute('data-monitored')) {
                link.setAttribute('data-monitored', 'true');
                link.addEventListener('error', () => {
                    const assetError = {
                        type: 'stylesheet_load_failure',
                        href: link.href,
                        timestamp: new Date().toISOString(),
                        critical: this.isCriticalAsset(link.href)
                    };
                    this.handleAssetError(assetError);
                });
                link.addEventListener('load', () => {
                    this.log(`Stylesheet loaded successfully: ${link.href}`);
                });
            }
        });
    }

    handleError(error) {
        this.errors.push(error);
        if (this.errors.length > this.config.maxErrors) {
            this.errors.shift();
        }
        
        if (this.config.logToConsole) {
            console.error('JavaScript Error:', error);
        }
        
        if (this.config.logToServer) {
            this.logErrorToServer(error);
        }
        
        if (this.shouldShowUserNotification(error)) {
            this.showUserNotification('An error occurred while loading the page. Some features may not work properly.', 'warning');
        }
    }

    handleAssetError(assetError) {
        this.assetErrors.push(assetError);
        
        if (this.config.logToConsole) {
            console.error('Asset Loading Error:', assetError);
        }
        
        if (assetError.critical) {
            this.handleCriticalAssetFailure(assetError);
        }
        
        if (assetError.critical && this.config.showUserNotifications) {
            this.showUserNotification('Some essential files failed to load. The page may not work correctly.', 'error');
        }
        
        this.attemptAssetFallback(assetError);
    }

    isCriticalAsset(url) {
        if (!url) return false;
        return this.config.criticalAssets.some(asset => 
            url.toLowerCase().includes(asset.toLowerCase())
        );
    }

    handleCriticalAssetFailure(assetError) {
        const assetName = this.getAssetName(assetError.src || assetError.href);
        console.error(`Critical asset failed to load: ${assetName}`);
        
        switch (assetName.toLowerCase()) {
            case 'jquery':
                this.handleJQueryFailure();
                break;
            case 'bootstrap':
                this.handleBootstrapFailure();
                break;
            case 'app.js':
                this.handleAppJSFailure();
                break;
            case 'style.css':
                this.handleStylesheetFailure();
                break;
        }
    }

    attemptAssetFallback(assetError) {
        if (window.CDNFallback && typeof window.CDNFallback.loadFallback === 'function') {
            const assetName = this.getAssetName(assetError.src || assetError.href);
            try {
                window.CDNFallback.loadFallback(assetName);
            } catch (error) {
                console.warn('CDN fallback failed:', error);
            }
        }
    }

    handleJQueryFailure() {
        this.showUserNotification('Core functionality is unavailable. Please refresh the page.', 'error');
        this.disableJQueryFeatures();
    }

    handleBootstrapFailure() {
        this.showUserNotification('Page styling may appear broken. Functionality should still work.', 'warning');
    }

    handleAppJSFailure() {
        this.showUserNotification('Some interactive features may not work properly.', 'warning');
    }

    handleStylesheetFailure() {
        this.showUserNotification('Page styling may appear broken.', 'info');
    }

    disableJQueryFeatures() {
        document.body.classList.add('no-jquery');
        window.DISABLE_DATATABLES = true;
        window.DISABLE_CHARTS = true;
        
        const interactiveElements = document.querySelectorAll('[data-requires-jquery]');
        interactiveElements.forEach(element => {
            element.innerHTML = '<p class="text-muted">This feature requires JavaScript libraries that failed to load.</p>';
        });
    }

    initNotificationSystem() {
        if (!document.getElementById('error-notifications')) {
            const container = document.createElement('div');
            container.id = 'error-notifications';
            container.className = 'error-notifications-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
    }

    showUserNotification(message, type = 'info') {
        if (!this.config.showUserNotifications) return;
        
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date().toISOString()
        };
        
        this.userNotifications.push(notification);
        this.displayNotification(notification);
        
        setTimeout(() => {
            this.removeNotification(notification.id);
        }, 10000);
    }

    displayNotification(notification) {
        const container = document.getElementById('error-notifications');
        if (!container) return;
        
        const notificationElement = document.createElement('div');
        notificationElement.id = `notification-${notification.id}`;
        notificationElement.className = `alert alert-${this.getBootstrapAlertClass(notification.type)} alert-dismissible fade show`;
        notificationElement.style.cssText = `
            margin-bottom: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        `;
        
        notificationElement.innerHTML = `
            <strong>${this.getNotificationTitle(notification.type)}</strong>
            ${notification.message}
            <button type="button" class="btn-close" onclick="window.ErrorHandler.removeNotification(${notification.id})"></button>
        `;
        
        container.appendChild(notificationElement);
    }

    removeNotification(notificationId) {
        const element = document.getElementById(`notification-${notificationId}`);
        if (element) {
            element.remove();
        }
        this.userNotifications = this.userNotifications.filter(n => n.id !== notificationId);
    }

    getBootstrapAlertClass(type) {
        const classes = {
            'error': 'danger',
            'warning': 'warning',
            'info': 'info',
            'success': 'success'
        };
        return classes[type] || 'info';
    }

    getNotificationTitle(type) {
        const titles = {
            'error': 'Error: ',
            'warning': 'Warning: ',
            'info': 'Info: ',
            'success': 'Success: '
        };
        return titles[type] || '';
    }

    getAssetName(url) {
        if (!url) return '';
        return url.split('/').pop().split('?')[0];
    }

    shouldShowUserNotification(error) {
        if (error.message && error.message.includes('Script error')) {
            return false;
        }
        return error.type === 'javascript' && error.message;
    }

    logErrorToServer(error) {
        fetch('/api/log-error/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(error)
        }).catch(err => {
            console.warn('Failed to log error to server:', err);
        });
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    log(message) {
        if (this.config.logToConsole) {
            console.log(`[ErrorHandler] ${message}`);
        }
    }

    getErrorStats() {
        return {
            totalErrors: this.errors.length,
            totalAssetErrors: this.assetErrors.length,
            criticalAssetErrors: this.assetErrors.filter(e => e.critical).length,
            recentErrors: this.errors.slice(-10),
            recentAssetErrors: this.assetErrors.slice(-10)
        };
    }

    clearErrors() {
        this.errors = [];
        this.assetErrors = [];
        this.userNotifications = [];
        
        const container = document.getElementById('error-notifications');
        if (container) {
            container.innerHTML = '';
        }
    }

    test() {
        console.log('Testing ErrorHandler...');
        this.handleError({
            type: 'javascript',
            message: 'Test error',
            filename: 'test.js',
            lineno: 1,
            colno: 1,
            timestamp: new Date().toISOString()
        });
        this.handleAssetError({
            type: 'script_load_failure',
            src: 'test-script.js',
            timestamp: new Date().toISOString(),
            critical: true
        });
        console.log('ErrorHandler test completed. Check notifications and console.');
    }
}

window.ErrorHandler = new ErrorHandler();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorHandler;
}
