/**
 * JavaScript Error Tracking System
 */
class ErrorTracker {
    constructor() {
        this.errors = [];
        this.maxErrors = 50;
        this.isInitialized = false;
        this.reportingEnabled = true;
        this.errorCounts = new Map();
        this.lastReportTime = 0;
        this.reportThrottle = 5000; // 5 seconds
        
        if (window.ErrorTracker && window.ErrorTracker.isInitialized) {
            return window.ErrorTracker;
        }
        
        this.init();
        window.ErrorTracker = this;
    }

    init() {
        if (this.isInitialized) return;
        
        try {
            this.setupErrorHandlers();
            this.setupPerformanceMonitoring();
            this.setupReportingEndpoint();
            this.isInitialized = true;
            console.log('ErrorTracker initialized');
        } catch (error) {
            console.error('Failed to initialize ErrorTracker:', error);
        }
    }

    setupErrorHandlers() {
        // Global error handler
        window.addEventListener('error', (event) => {
            this.handleError({
                type: 'javascript',
                message: event.message || 'Unknown error',
                filename: event.filename || 'unknown',
                lineno: event.lineno || 0,
                colno: event.colno || 0,
                stack: event.error?.stack || '',
                timestamp: new Date().toISOString(),
                url: window.location.href,
                userAgent: navigator.userAgent
            });
        });

        // Promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError({
                type: 'promise_rejection',
                message: event.reason?.message || 'Unhandled promise rejection',
                stack: event.reason?.stack || '',
                timestamp: new Date().toISOString(),
                url: window.location.href,
                userAgent: navigator.userAgent
            });
        });

        // Resource loading errors
        window.addEventListener('error', (event) => {
            if (event.target && event.target !== window) {
                this.handleError({
                    type: 'resource',
                    message: `Failed to load ${event.target.tagName}: ${event.target.src || event.target.href}`,
                    resource: event.target.src || event.target.href,
                    timestamp: new Date().toISOString(),
                    url: window.location.href
                });
            }
        }, true);
    }

    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                if (window.performance && window.performance.timing) {
                    const timing = window.performance.timing;
                    const loadTime = timing.loadEventEnd - timing.navigationStart;
                    
                    if (loadTime > 10000) { // More than 10 seconds
                        this.handleError({
                            type: 'performance',
                            message: `Slow page load: ${loadTime}ms`,
                            loadTime: loadTime,
                            timestamp: new Date().toISOString(),
                            url: window.location.href
                        });
                    }
                }
            }, 1000);
        });

        // Monitor memory usage (if available)
        if (window.performance && window.performance.memory) {
            setInterval(() => {
                const memory = window.performance.memory;
                const usedPercent = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
                
                if (usedPercent > 90) {
                    this.handleError({
                        type: 'memory',
                        message: `High memory usage: ${usedPercent.toFixed(1)}%`,
                        memoryUsage: {
                            used: memory.usedJSHeapSize,
                            total: memory.totalJSHeapSize,
                            limit: memory.jsHeapSizeLimit
                        },
                        timestamp: new Date().toISOString(),
                        url: window.location.href
                    });
                }
            }, 30000); // Check every 30 seconds
        }
    }

    handleError(errorInfo) {
        // Rate limiting
        const errorKey = `${errorInfo.type}:${errorInfo.message}`;
        const count = this.errorCounts.get(errorKey) || 0;
        this.errorCounts.set(errorKey, count + 1);
        
        // Skip if too many of the same error
        if (count > 5) return;
        
        // Add error to collection
        if (this.errors.length >= this.maxErrors) {
            this.errors.shift(); // Remove oldest
        }
        
        this.errors.push({
            ...errorInfo,
            id: Date.now() + Math.random(),
            count: count + 1
        });
        
        console.error('Application Error:', errorInfo);
        
        // Report to server (throttled)
        if (this.reportingEnabled && this.shouldReport(errorInfo)) {
            this.reportToServer(errorInfo);
        }
        
        // Show user notification for critical errors
        this.showUserNotification(errorInfo);
    }

    shouldReport(errorInfo) {
        const now = Date.now();
        if (now - this.lastReportTime < this.reportThrottle) {
            return false;
        }
        
        // Report critical errors immediately
        const criticalTypes = ['javascript', 'promise_rejection'];
        if (criticalTypes.includes(errorInfo.type)) {
            this.lastReportTime = now;
            return true;
        }
        
        return false;
    }

    reportToServer(errorInfo) {
        try {
            fetch('/api/javascript-errors/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify({
                    ...errorInfo,
                    sessionId: this.getSessionId(),
                    userId: this.getUserId()
                })
            }).catch(() => {
                // Silently fail to prevent error loops
            });
        } catch (e) {
            // Silently fail
        }
    }

    showUserNotification(errorInfo) {
        // Only show notifications for critical errors that affect user experience
        if (errorInfo.type === 'resource' && errorInfo.resource?.includes('.css')) {
            if (typeof Toastify !== 'undefined') {
                Toastify({
                    text: "Niektóre style mogą nie działać poprawnie",
                    duration: 5000,
                    gravity: "top",
                    position: "right",
                    backgroundColor: "#ffc107"
                }).showToast();
            }
        } else if (errorInfo.type === 'javascript' && errorInfo.message.includes('InvoiceFormManager')) {
            if (typeof Toastify !== 'undefined') {
                Toastify({
                    text: "Wystąpił problem z formularzem faktury",
                    duration: 5000,
                    gravity: "top",
                    position: "right",
                    backgroundColor: "#dc3545"
                }).showToast();
            }
        }
    }

    setupReportingEndpoint() {
        // Create global error reporting function
        window.reportError = (message, details = {}) => {
            this.handleError({
                type: 'manual',
                message: message,
                details: details,
                timestamp: new Date().toISOString(),
                url: window.location.href
            });
        };
        
        // Create error dashboard access
        window.getErrorDashboard = () => {
            return {
                errors: this.errors,
                errorCounts: Object.fromEntries(this.errorCounts),
                stats: this.getErrorStats(),
                timestamp: new Date().toISOString()
            };
        };
    }

    getErrorStats() {
        const stats = {
            total: this.errors.length,
            byType: {},
            recent: 0,
            critical: 0
        };
        
        const oneHourAgo = Date.now() - (60 * 60 * 1000);
        
        this.errors.forEach(error => {
            // Count by type
            stats.byType[error.type] = (stats.byType[error.type] || 0) + 1;
            
            // Count recent errors
            if (new Date(error.timestamp).getTime() > oneHourAgo) {
                stats.recent++;
            }
            
            // Count critical errors
            if (['javascript', 'promise_rejection'].includes(error.type)) {
                stats.critical++;
            }
        });
        
        return stats;
    }

    getSessionId() {
        let sessionId = sessionStorage.getItem('errorTracker_sessionId');
        if (!sessionId) {
            sessionId = Date.now().toString(36) + Math.random().toString(36).substr(2);
            sessionStorage.setItem('errorTracker_sessionId', sessionId);
        }
        return sessionId;
    }

    getUserId() {
        // Try to get user ID from various sources
        const userMeta = document.querySelector('meta[name="user-id"]');
        if (userMeta) return userMeta.content;
        
        // Try to get from global variable
        if (window.currentUserId) return window.currentUserId;
        
        return 'anonymous';
    }

    getErrors() {
        return [...this.errors];
    }

    clearErrors() {
        this.errors = [];
        this.errorCounts.clear();
    }

    enableReporting() {
        this.reportingEnabled = true;
    }

    disableReporting() {
        this.reportingEnabled = false;
    }

    getHealthStatus() {
        const stats = this.getErrorStats();
        const recentErrors = stats.recent;
        const criticalErrors = stats.critical;
        
        if (criticalErrors > 5 || recentErrors > 10) {
            return 'unhealthy';
        } else if (criticalErrors > 0 || recentErrors > 3) {
            return 'degraded';
        } else {
            return 'healthy';
        }
    }
}

// Initialize safely
try {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new ErrorTracker();
        });
    } else {
        new ErrorTracker();
    }
} catch (error) {
    console.error('Failed to initialize ErrorTracker:', error);
}