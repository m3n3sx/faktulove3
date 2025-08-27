class AssetLoadingMonitor {
    constructor() {
        this.monitoringData = {
            errors404: [],
            performanceMetrics: [],
            criticalFailures: [],
            retryAttempts: {},
            serverLogs: []
        };
        
        this.config = {
            enableServerLogging: true,
            maxRetryAttempts: 3,
            retryDelay: 2000,
            performanceThreshold: 3000,
            criticalAssets: [
                'jquery',
                'bootstrap',
                'app.js',
                'style.css',
                'dependency-manager.js',
                'cdn-fallback.js'
            ],
            monitoringEndpoint: '/api/asset-monitoring/',
            alertThresholds: {
                error404Count: 5,
                criticalFailureCount: 2,
                performanceThreshold: 5000
            }
        };
        
        this.logQueue = [];
        this.isInitialized = false;
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.setupErrorMonitoring();
        this.setupPerformanceMonitoring();
        this.setupServerLogging();
        this.startPeriodicReporting();
        
        this.isInitialized = true;
        console.log('Asset Loading Monitor initialized');
    }
    
    setupErrorMonitoring() {
        // Monitor for 404 errors on static assets
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = performance.now();
            try {
                const response = await originalFetch(...args);
                const endTime = performance.now();
                
                // Check if it's a static asset request
                if (this.isStaticAssetRequest(args[0])) {
                    if (response.status === 404) {
                        this.handle404Error(args[0], 'fetch');
                    }
                    this.recordPerformanceMetric(args[0], endTime - startTime);
                }
                
                return response;
            } catch (error) {
                if (this.isStaticAssetRequest(args[0])) {
                    this.handle404Error(args[0], 'fetch', error);
                }
                throw error;
            }
        };
        
        // Monitor script loading errors
        const originalCreateElement = document.createElement;
        document.createElement = function(tagName) {
            const element = originalCreateElement.call(this, tagName);
            
            if (tagName.toLowerCase() === 'script') {
                element.addEventListener('error', (e) => {
                    if (e.target.src) {
                        this.handle404Error(e.target.src, 'script');
                    }
                });
                
                element.addEventListener('load', (e) => {
                    if (e.target.src) {
                        this.recordPerformanceMetric(e.target.src, performance.now());
                    }
                });
            }
            
            return element;
        };
        
        // Monitor CSS loading errors
        const originalLink = document.createElement('link');
        const originalSetAttribute = originalLink.setAttribute;
        originalLink.setAttribute = function(name, value) {
            if (name === 'href' && value) {
                this.addEventListener('error', (e) => {
                    this.handle404Error(value, 'css');
                });
            }
            return originalSetAttribute.call(this, name, value);
        };
    }
    
    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            const loadTime = performance.now();
            this.recordPerformanceMetric('page_load', loadTime);
            
            // Check for critical asset failures
            this.checkCriticalAssetStatus();
        });
        
        // Monitor resource loading performance
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.entryType === 'resource') {
                        this.recordPerformanceMetric(entry.name, entry.duration);
                        
                        if (entry.duration > this.config.performanceThreshold) {
                            this.recordPerformanceIssue(entry.name, 'slow_loading', entry.duration);
                        }
                    }
                }
            });
            observer.observe({ entryTypes: ['resource'] });
        }
    }
    
    setupServerLogging() {
        this.logQueue = [];
        this.serverLogInterval = setInterval(() => {
            this.flushLogQueue();
        }, 10000); // Flush logs every 10 seconds
    }
    
    isStaticAssetRequest(url) {
        if (typeof url === 'string') {
            return url.includes('/static/') || url.includes('/media/');
        }
        return false;
    }
    
    handle404Error(url, type, error = null) {
        const errorData = {
            url: url,
            type: type,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            error: error ? error.message : null
        };
        
        this.monitoringData.errors404.push(errorData);
        
        // Check if it's a critical asset
        const isCritical = this.config.criticalAssets.some(asset => 
            url.includes(asset)
        );
        
        if (isCritical) {
            this.monitoringData.criticalFailures.push(errorData);
            this.triggerAlert('critical_asset_404', errorData);
        }
        
        // Log to server
        this.logToServer('404_error', errorData);
        
        // Check alert thresholds
        this.checkAlertThresholds();
    }
    
    recordPerformanceMetric(url, duration) {
        this.monitoringData.performanceMetrics.push({
            url: url,
            duration: duration,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 100 metrics
        if (this.monitoringData.performanceMetrics.length > 100) {
            this.monitoringData.performanceMetrics.shift();
        }
    }
    
    recordPerformanceIssue(url, issue, duration) {
        this.logToServer('performance_issue', {
            url: url,
            issue: issue,
            duration: duration,
            timestamp: new Date().toISOString()
        });
    }
    
    checkCriticalAssetStatus() {
        const criticalAssets = [
            'jquery',
            'bootstrap',
            'app.js'
        ];
        
        const missingAssets = criticalAssets.filter(asset => {
            if (asset === 'jquery') return typeof $ === 'undefined';
            if (asset === 'bootstrap') return typeof bootstrap === 'undefined';
            if (asset === 'app.js') return typeof window.App === 'undefined';
            return false;
        });
        
        if (missingAssets.length > 0) {
            this.triggerAlert('critical_assets_missing', {
                missingAssets: missingAssets,
                timestamp: new Date().toISOString()
            });
        }
    }
    
    checkAlertThresholds() {
        const recentErrors = this.monitoringData.errors404.filter(error => {
            const errorTime = new Date(error.timestamp);
            const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
            return errorTime > fiveMinutesAgo;
        });
        
        if (recentErrors.length >= this.config.alertThresholds.error404Count) {
            this.triggerAlert('high_404_rate', {
                errorCount: recentErrors.length,
                timeWindow: '5 minutes'
            });
        }
        
        const recentCriticalFailures = this.monitoringData.criticalFailures.filter(failure => {
            const failureTime = new Date(failure.timestamp);
            const tenMinutesAgo = new Date(Date.now() - 10 * 60 * 1000);
            return failureTime > tenMinutesAgo;
        });
        
        if (recentCriticalFailures.length >= this.config.alertThresholds.criticalFailureCount) {
            this.triggerAlert('critical_failures_threshold', {
                failureCount: recentCriticalFailures.length,
                timeWindow: '10 minutes'
            });
        }
    }
    
    triggerAlert(type, data) {
        const alertData = {
            type: type,
            data: data,
            timestamp: new Date().toISOString(),
            severity: this.getAlertSeverity(type)
        };
        
        // Log alert
        this.logToServer('alert', alertData);
        
        // Show user notification if critical
        if (alertData.severity === 'critical') {
            this.showUserNotification(alertData);
        }
        
        // Send to monitoring endpoint
        this.sendToMonitoringEndpoint(alertData);
    }
    
    getAlertSeverity(type) {
        const severityMap = {
            'critical_asset_404': 'critical',
            'critical_assets_missing': 'critical',
            'critical_failures_threshold': 'critical',
            'high_404_rate': 'warning',
            'performance_issue': 'info'
        };
        return severityMap[type] || 'info';
    }
    
    showUserNotification(alertData) {
        // Create user-friendly notification
        const notification = document.createElement('div');
        notification.className = 'asset-monitor-alert';
        notification.innerHTML = `
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <strong>System Notice:</strong> Some resources are loading slowly. 
                Please refresh the page if you experience issues.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 10000);
    }
    
    logToServer(level, data) {
        const logEntry = {
            level: level,
            data: data,
            timestamp: new Date().toISOString(),
            sessionId: this.getSessionId(),
            pageUrl: window.location.href
        };
        
        this.logQueue.push(logEntry);
        
        // Flush immediately if queue is getting large
        if (this.logQueue.length >= 50) {
            this.flushLogQueue();
        }
    }
    
    flushLogQueue() {
        if (this.logQueue.length === 0) return;
        
        const logsToSend = [...this.logQueue];
        this.logQueue = [];
        
        if (this.config.enableServerLogging) {
            fetch(this.config.monitoringEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    logs: logsToSend,
                    timestamp: new Date().toISOString()
                })
            }).catch(error => {
                console.warn('Failed to send asset monitoring logs:', error);
            });
        }
    }
    
    sendToMonitoringEndpoint(data) {
        fetch(this.config.monitoringEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(data)
        }).catch(error => {
            console.warn('Failed to send monitoring data:', error);
        });
    }
    
    startPeriodicReporting() {
        setInterval(() => {
            this.generateReport();
        }, 60000); // Report every minute
    }
    
    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                total404Errors: this.monitoringData.errors404.length,
                totalCriticalFailures: this.monitoringData.criticalFailures.length,
                averageLoadTime: this.calculateAverageLoadTime(),
                pageLoadTime: this.getPageLoadTime()
            },
            recentErrors: this.monitoringData.errors404.slice(-10),
            performanceMetrics: this.monitoringData.performanceMetrics.slice(-20)
        };
        
        this.logToServer('periodic_report', report);
    }
    
    calculateAverageLoadTime() {
        if (this.monitoringData.performanceMetrics.length === 0) return 0;
        
        const total = this.monitoringData.performanceMetrics.reduce((sum, metric) => {
            return sum + metric.duration;
        }, 0);
        
        return total / this.monitoringData.performanceMetrics.length;
    }
    
    getPageLoadTime() {
        if ('performance' in window) {
            const navigation = performance.getEntriesByType('navigation')[0];
            return navigation ? navigation.loadEventEnd - navigation.loadEventStart : 0;
        }
        return 0;
    }
    
    getSessionId() {
        if (!this.sessionId) {
            this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        return this.sessionId;
    }
    
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
    
    // Public API methods
    getMonitoringData() {
        return {
            ...this.monitoringData,
            config: this.config
        };
    }
    
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }
    
    resetMonitoring() {
        this.monitoringData = {
            errors404: [],
            performanceMetrics: [],
            criticalFailures: [],
            retryAttempts: {},
            serverLogs: []
        };
    }
}

// Initialize the monitor when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.AssetLoadingMonitor = new AssetLoadingMonitor();
    });
} else {
    window.AssetLoadingMonitor = new AssetLoadingMonitor();
}