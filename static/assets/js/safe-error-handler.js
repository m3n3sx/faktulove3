/**
 * Safe Error Handler - prevents infinite loops and provides basic error handling
 */
class SafeErrorHandler {
    constructor() {
        this.errors = [];
        this.maxErrors = 10; // Limit to prevent memory issues
        this.isInitialized = false;
        this.errorCount = 0;
        this.maxErrorsPerMinute = 20; // Rate limiting
        this.errorTimestamps = [];

        // Prevent multiple initializations
        if (window.SafeErrorHandler && window.SafeErrorHandler.isInitialized) {
            return window.SafeErrorHandler;
        }

        this.init();
        window.SafeErrorHandler = this;
    }

    init() {
        if (this.isInitialized) return;

        try {
            this.setupBasicErrorHandler();
            this.isInitialized = true;
            console.log('SafeErrorHandler initialized');
        } catch (error) {
            console.error('Failed to initialize SafeErrorHandler:', error);
        }
    }

    setupBasicErrorHandler() {
        // Rate-limited error handler
        window.addEventListener('error', (event) => {
            if (this.shouldIgnoreError(event)) return;

            try {
                this.logError({
                    type: 'javascript',
                    message: event.message || 'Unknown error',
                    filename: event.filename || 'unknown',
                    lineno: event.lineno || 0,
                    timestamp: new Date().toISOString()
                });
            } catch (handlerError) {
                // Prevent handler errors from causing loops
                console.error('Error in error handler:', handlerError);
            }
        });

        // Handle promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            if (this.shouldIgnoreError(event)) return;

            try {
                this.logError({
                    type: 'promise_rejection',
                    message: event.reason?.message || 'Unhandled promise rejection',
                    timestamp: new Date().toISOString()
                });
            } catch (handlerError) {
                console.error('Error in promise rejection handler:', handlerError);
            }
        });
    }

    shouldIgnoreError(event) {
        // Rate limiting
        const now = Date.now();
        this.errorTimestamps = this.errorTimestamps.filter(time => now - time < 60000); // Keep last minute

        if (this.errorTimestamps.length >= this.maxErrorsPerMinute) {
            return true; // Ignore if too many errors
        }

        this.errorTimestamps.push(now);

        // Ignore certain error types that might cause loops
        const message = event.message || event.reason?.message || '';
        const ignoredMessages = [
            'Script error',
            'Non-Error promise rejection captured',
            'ResizeObserver loop limit exceeded',
            'Network request failed'
        ];

        return ignoredMessages.some(ignored => message.includes(ignored));
    }

    logError(error) {
        // Limit stored errors
        if (this.errors.length >= this.maxErrors) {
            this.errors.shift(); // Remove oldest error
        }

        this.errors.push(error);

        // Simple console logging
        console.error('Application Error:', error);

        // Optional: Send to server (disabled by default to prevent loops)
        // this.sendToServer(error);
    }

    getErrors() {
        return [...this.errors]; // Return copy
    }

    clearErrors() {
        this.errors = [];
        this.errorTimestamps = [];
    }

    // Optional server reporting (use with caution)
    sendToServer(error) {
        // Only send critical errors to prevent spam
        if (error.type === 'javascript' && error.filename && !error.filename.includes('extension')) {
            try {
                fetch('/api/errors/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    },
                    body: JSON.stringify(error)
                }).catch(() => {
                    // Silently fail to prevent error loops
                });
            } catch (e) {
                // Silently fail
            }
        }
    }
}

// Initialize safely
try {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new SafeErrorHandler();
        });
    } else {
        new SafeErrorHandler();
    }
} catch (error) {
    console.error('Failed to initialize SafeErrorHandler:', error);
}