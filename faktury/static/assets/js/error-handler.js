/**
 * Global Error Handler for FaktuLove Application
 * Provides centralized error handling, logging, and user notifications
 */

(function() {
    'use strict';

    // Global error handler configuration
    const ErrorHandler = {
        config: {
            enableConsoleLogging: true,
            enableUserNotifications: true,
            enableRemoteLogging: false,
            maxErrorsPerSession: 50,
            notificationDuration: 5000
        },

        errors: [],
        errorCount: 0,

        /**
         * Initialize the global error handler
         */
        init: function() {
            this.setupGlobalErrorHandlers();
            this.setupUnhandledRejectionHandler();
            this.setupResourceErrorHandler();
            console.log('ErrorHandler initialized');
        },

        /**
         * Setup global JavaScript error handlers
         */
        setupGlobalErrorHandlers: function() {
            const self = this;
            
            // Global error handler for uncaught exceptions
            window.addEventListener('error', function(event) {
                self.handleError({
                    type: 'javascript',
                    message: event.message,
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno,
                    error: event.error,
                    stack: event.error ? event.error.stack : null,
                    timestamp: new Date().toISOString()
                });
            });

            // Override console.error to capture logged errors
            const originalConsoleError = console.error;
            console.error = function() {
                originalConsoleError.apply(console, arguments);
                self.handleError({
                    type: 'console',
                    message: Array.from(arguments).join(' '),
                    timestamp: new Date().toISOString()
                });
            };
        },

        /**
         * Setup handler for unhandled promise rejections
         */
        setupUnhandledRejectionHandler: function() {
            const self = this;
            
            window.addEventListener('unhandledrejection', function(event) {
                self.handleError({
                    type: 'promise',
                    message: event.reason ? event.reason.toString() : 'Unhandled promise rejection',
                    reason: event.reason,
                    timestamp: new Date().toISOString()
                });
            });
        },

        /**
         * Setup handler for resource loading errors
         */
        setupResourceErrorHandler: function() {
            const self = this;
            
            // Monitor for failed resource loads
            window.addEventListener('error', function(event) {
                if (event.target !== window) {
                    const element = event.target;
                    const resourceType = element.tagName.toLowerCase();
                    const src = element.src || element.href;
                    
                    if (src) {
                        self.handleError({
                            type: 'resource',
                            message: `Failed to load ${resourceType}: ${src}`,
                            resourceType: resourceType,
                            src: src,
                            element: element,
                            timestamp: new Date().toISOString()
                        });
                    }
                }
            }, true); // Use capture phase to catch resource errors
        },

        /**
         * Handle and process errors
         */
        handleError: function(errorInfo) {
            if (this.errorCount >= this.config.maxErrorsPerSession) {
                return; // Prevent error spam
            }

            this.errorCount++;
            this.errors.push(errorInfo);

            // Log to console if enabled
            if (this.config.enableConsoleLogging) {
                this.logToConsole(errorInfo);
            }

            // Show user notification if enabled
            if (this.config.enableUserNotifications) {
                this.showUserNotification(errorInfo);
            }

            // Send to remote logging if enabled
            if (this.config.enableRemoteLogging) {
                this.sendToRemoteLogging(errorInfo);
            }

            // Trigger custom error event
            this.triggerErrorEvent(errorInfo);
        },

        /**
         * Log error to console with formatting
         */
        logToConsole: function(errorInfo) {
            const prefix = `[ErrorHandler:${errorInfo.type}]`;
            
            switch (errorInfo.type) {
                case 'javascript':
                    console.group(`${prefix} JavaScript Error`);
                    console.error('Message:', errorInfo.message);
                    console.error('File:', errorInfo.filename);
                    console.error('Line:', errorInfo.lineno, 'Column:', errorInfo.colno);
                    if (errorInfo.stack) {
                        console.error('Stack:', errorInfo.stack);
                    }
                    console.groupEnd();
                    break;
                    
                case 'resource':
                    console.warn(`${prefix} Resource Load Failed:`, errorInfo.src);
                    break;
                    
                case 'promise':
                    console.error(`${prefix} Unhandled Promise Rejection:`, errorInfo.reason);
                    break;
                    
                default:
                    console.error(`${prefix}`, errorInfo.message);
            }
        },

        /**
         * Show user-friendly error notification
         */
        showUserNotification: function(errorInfo) {
            let message = '';
            let severity = 'warning';

            switch (errorInfo.type) {
                case 'resource':
                    if (errorInfo.src.includes('.css')) {
                        message = 'Some styling may not display correctly due to a missing file.';
                    } else if (errorInfo.src.includes('.js')) {
                        message = 'Some functionality may be limited due to a missing script.';
                        severity = 'error';
                    } else {
                        message = 'A resource failed to load. Some features may not work properly.';
                    }
                    break;
                    
                case 'javascript':
                    message = 'A technical error occurred. Please refresh the page if you experience issues.';
                    severity = 'error';
                    break;
                    
                case 'promise':
                    message = 'An operation failed to complete. Please try again.';
                    severity = 'warning';
                    break;
                    
                default:
                    message = 'An unexpected error occurred.';
                    severity = 'warning';
            }

            this.displayNotification(message, severity);
        },

        /**
         * Display notification to user
         */
        displayNotification: function(message, severity) {
            // Try to use Toastify if available
            if (typeof Toastify !== 'undefined') {
                const backgroundColor = severity === 'error' ? '#dc3545' : '#ffc107';
                Toastify({
                    text: message,
                    duration: this.config.notificationDuration,
                    gravity: 'top',
                    position: 'right',
                    backgroundColor: backgroundColor,
                    stopOnFocus: true
                }).showToast();
                return;
            }

            // Fallback to custom notification
            this.showCustomNotification(message, severity);
        },

        /**
         * Show custom notification when Toastify is not available
         */
        showCustomNotification: function(message, severity) {
            const notification = document.createElement('div');
            notification.className = `error-notification error-notification-${severity}`;
            notification.textContent = message;
            
            // Style the notification
            Object.assign(notification.style, {
                position: 'fixed',
                top: '20px',
                right: '20px',
                padding: '12px 16px',
                borderRadius: '4px',
                color: 'white',
                backgroundColor: severity === 'error' ? '#dc3545' : '#ffc107',
                zIndex: '10000',
                maxWidth: '300px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                fontSize: '14px',
                cursor: 'pointer'
            });

            // Add close functionality
            notification.addEventListener('click', function() {
                notification.remove();
            });

            document.body.appendChild(notification);

            // Auto-remove after duration
            setTimeout(function() {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, this.config.notificationDuration);
        },

        /**
         * Send error to remote logging service
         */
        sendToRemoteLogging: function(errorInfo) {
            // Implementation for remote logging
            // This could send to a logging service like Sentry, LogRocket, etc.
            try {
                fetch('/api/log-error/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({
                        error: errorInfo,
                        userAgent: navigator.userAgent,
                        url: window.location.href,
                        timestamp: new Date().toISOString()
                    })
                }).catch(function(err) {
                    console.warn('Failed to send error to remote logging:', err);
                });
            } catch (e) {
                console.warn('Remote logging failed:', e);
            }
        },

        /**
         * Trigger custom error event for other components to listen to
         */
        triggerErrorEvent: function(errorInfo) {
            const event = new CustomEvent('errorHandlerError', {
                detail: errorInfo
            });
            window.dispatchEvent(event);
        },

        /**
         * Get CSRF token for API requests
         */
        getCSRFToken: function() {
            const token = document.querySelector('meta[name="csrf-token"]');
            return token ? token.getAttribute('content') : '';
        },

        /**
         * Get error statistics
         */
        getStats: function() {
            const stats = {
                totalErrors: this.errors.length,
                errorsByType: {},
                recentErrors: this.errors.slice(-10)
            };

            this.errors.forEach(function(error) {
                stats.errorsByType[error.type] = (stats.errorsByType[error.type] || 0) + 1;
            });

            return stats;
        },

        /**
         * Clear error history
         */
        clearErrors: function() {
            this.errors = [];
            this.errorCount = 0;
        },

        /**
         * Manual error reporting
         */
        reportError: function(message, type, additionalInfo) {
            this.handleError({
                type: type || 'manual',
                message: message,
                additionalInfo: additionalInfo,
                timestamp: new Date().toISOString()
            });
        }
    };

    // Initialize error handler when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            ErrorHandler.init();
        });
    } else {
        ErrorHandler.init();
    }

    // Make ErrorHandler globally available
    window.ErrorHandler = ErrorHandler;

})();