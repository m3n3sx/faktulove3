/**
 * Asset Loading Monitor for FaktuLove Application
 * Specialized monitoring for 404 errors and performance tracking
 */

(function() {
    'use strict';

    const AssetLoadingMonitor = {
        config: {
            enable404Monitoring: true,
            enablePerformanceTracking: true,
            enableNetworkMonitoring: true,
            reportingEndpoint: '/api/asset-errors/',
            batchSize: 10,
            reportingInterval: 30000 // 30 seconds
        },

        errors: {
            notFound: [],
            networkErrors: [],
            timeouts: []
        },

        performance: {
            loadTimes: {},
            networkTiming: {},
            resourceSizes: {}
        },

        reportingQueue: [],
        reportingTimer: null,

        /**
         * Initialize asset loading monitor
         */
        init: function() {
            this.setupErrorMonitoring();
            this.setupPerformanceMonitoring();
            this.setupNetworkMonitoring();
            this.startReportingTimer();
            console.log('AssetLoadingMonitor initialized');
        },

        /**
         * Setup 404 and loading error monitoring
         */
        setupErrorMonitoring: function() {
            if (!this.config.enable404Monitoring) return;

            const self = this;

            // Monitor resource loading errors
            window.addEventListener('error', function(event) {
                if (event.target !== window) {
                    const element = event.target;
                    const src = element.src || element.href;
                    
                    if (src) {
                        self.handleResourceError(element, src, 'load_error');
                    }
                }
            }, true);

            // Monitor fetch/XHR errors
            this.interceptFetch();
            this.interceptXHR();

            // Monitor CSS loading errors
            this.monitorCSSErrors();
        },

        /**
         * Handle resource loading errors
         */
        handleResourceError: function(element, src, errorType) {
            const error = {
                type: errorType,
                src: src,
                element: element.tagName.toLowerCase(),
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href,
                referrer: document.referrer
            };

            // Determine error category
            if (src.includes('404') || errorType === 'not_found') {
                this.errors.notFound.push(error);
            } else if (errorType === 'network_error') {
                this.errors.networkErrors.push(error);
            } else if (errorType === 'timeout') {
                this.errors.timeouts.push(error);
            }

            // Add to reporting queue
            this.addToReportingQueue(error);

            // Log error
            console.warn(`Asset loading error (${errorType}):`, src);

            // Trigger error event
            this.triggerMonitorEvent('assetError', error);

            // Attempt recovery if possible
            this.attemptErrorRecovery(element, src, errorType);
        },

        /**
         * Intercept fetch requests to monitor errors
         */
        interceptFetch: function() {
            const self = this;
            const originalFetch = window.fetch;

            window.fetch = function(resource, options) {
                const startTime = performance.now();
                const url = typeof resource === 'string' ? resource : resource.url;

                return originalFetch.apply(this, arguments)
                    .then(response => {
                        const endTime = performance.now();
                        const loadTime = endTime - startTime;

                        // Track performance
                        self.trackRequestPerformance(url, loadTime, response);

                        // Check for errors
                        if (!response.ok) {
                            if (response.status === 404) {
                                self.handleResourceError({ tagName: 'fetch' }, url, 'not_found');
                            } else {
                                self.handleResourceError({ tagName: 'fetch' }, url, 'network_error');
                            }
                        }

                        return response;
                    })
                    .catch(error => {
                        const endTime = performance.now();
                        const loadTime = endTime - startTime;

                        // Handle network errors
                        self.handleResourceError({ tagName: 'fetch' }, url, 'network_error');
                        self.trackRequestPerformance(url, loadTime, null, error);

                        throw error;
                    });
            };
        },

        /**
         * Intercept XMLHttpRequest to monitor errors
         */
        interceptXHR: function() {
            const self = this;
            const originalOpen = XMLHttpRequest.prototype.open;
            const originalSend = XMLHttpRequest.prototype.send;

            XMLHttpRequest.prototype.open = function(method, url) {
                this._url = url;
                this._startTime = performance.now();
                return originalOpen.apply(this, arguments);
            };

            XMLHttpRequest.prototype.send = function() {
                const xhr = this;
                
                xhr.addEventListener('load', function() {
                    const endTime = performance.now();
                    const loadTime = endTime - xhr._startTime;

                    self.trackRequestPerformance(xhr._url, loadTime, xhr);

                    if (xhr.status === 404) {
                        self.handleResourceError({ tagName: 'xhr' }, xhr._url, 'not_found');
                    } else if (xhr.status >= 400) {
                        self.handleResourceError({ tagName: 'xhr' }, xhr._url, 'network_error');
                    }
                });

                xhr.addEventListener('error', function() {
                    const endTime = performance.now();
                    const loadTime = endTime - xhr._startTime;

                    self.trackRequestPerformance(xhr._url, loadTime, xhr, 'network_error');
                    self.handleResourceError({ tagName: 'xhr' }, xhr._url, 'network_error');
                });

                xhr.addEventListener('timeout', function() {
                    self.handleResourceError({ tagName: 'xhr' }, xhr._url, 'timeout');
                });

                return originalSend.apply(this, arguments);
            };
        },

        /**
         * Monitor CSS loading errors
         */
        monitorCSSErrors: function() {
            const self = this;
            
            // Check existing stylesheets
            Array.from(document.styleSheets).forEach(function(sheet) {
                try {
                    // Try to access rules to check if CSS loaded
                    const rules = sheet.cssRules || sheet.rules;
                    if (!rules && sheet.href) {
                        self.handleResourceError({ tagName: 'link' }, sheet.href, 'load_error');
                    }
                } catch (e) {
                    // Cross-origin or other access error
                    if (sheet.href) {
                        console.warn('Cannot access stylesheet rules:', sheet.href);
                    }
                }
            });

            // Monitor new stylesheets
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.tagName === 'LINK' && node.rel === 'stylesheet') {
                            setTimeout(function() {
                                self.checkStylesheetLoading(node);
                            }, 1000);
                        }
                    });
                });
            });

            observer.observe(document.head, { childList: true });
        },

        /**
         * Check if stylesheet loaded successfully
         */
        checkStylesheetLoading: function(linkElement) {
            try {
                const sheet = linkElement.sheet;
                if (!sheet || (!sheet.cssRules && !sheet.rules)) {
                    this.handleResourceError(linkElement, linkElement.href, 'load_error');
                }
            } catch (e) {
                // Assume loaded if we can't check (cross-origin)
            }
        },

        /**
         * Setup performance monitoring
         */
        setupPerformanceMonitoring: function() {
            if (!this.config.enablePerformanceTracking) return;

            const self = this;

            // Monitor resource timing
            if ('PerformanceObserver' in window) {
                const observer = new PerformanceObserver(function(list) {
                    list.getEntries().forEach(function(entry) {
                        self.trackResourcePerformance(entry);
                    });
                });

                observer.observe({ entryTypes: ['resource'] });
            }

            // Monitor navigation timing
            window.addEventListener('load', function() {
                setTimeout(function() {
                    self.trackNavigationPerformance();
                }, 1000);
            });
        },

        /**
         * Track resource performance
         */
        trackResourcePerformance: function(entry) {
            const resourceData = {
                name: entry.name,
                duration: entry.duration,
                size: entry.transferSize || 0,
                type: this.getResourceType(entry.name),
                startTime: entry.startTime,
                responseEnd: entry.responseEnd,
                timestamp: new Date().toISOString()
            };

            // Store performance data
            this.performance.loadTimes[entry.name] = resourceData;

            // Check for slow loading resources
            if (entry.duration > 5000) { // 5 seconds
                this.handleSlowResource(resourceData);
            }

            // Check for large resources
            if (entry.transferSize > 1024 * 1024) { // 1MB
                this.handleLargeResource(resourceData);
            }
        },

        /**
         * Track request performance (fetch/XHR)
         */
        trackRequestPerformance: function(url, loadTime, response, error) {
            const requestData = {
                url: url,
                loadTime: loadTime,
                status: response ? (response.status || 200) : 0,
                error: error || null,
                timestamp: new Date().toISOString()
            };

            this.performance.networkTiming[url] = requestData;

            // Check for slow requests
            if (loadTime > 10000) { // 10 seconds
                this.handleSlowRequest(requestData);
            }
        },

        /**
         * Track navigation performance
         */
        trackNavigationPerformance: function() {
            if (!('navigation' in performance)) return;

            const timing = performance.getEntriesByType('navigation')[0];
            if (!timing) return;

            const navigationData = {
                domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                loadComplete: timing.loadEventEnd - timing.navigationStart,
                dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
                tcpConnection: timing.connectEnd - timing.connectStart,
                serverResponse: timing.responseEnd - timing.requestStart,
                domProcessing: timing.domContentLoadedEventEnd - timing.responseEnd,
                resourceLoading: timing.loadEventEnd - timing.domContentLoadedEventEnd,
                timestamp: new Date().toISOString()
            };

            this.performance.navigation = navigationData;

            // Report slow page loads
            if (navigationData.loadComplete > 10000) { // 10 seconds
                this.handleSlowPageLoad(navigationData);
            }
        },

        /**
         * Setup network monitoring
         */
        setupNetworkMonitoring: function() {
            if (!this.config.enableNetworkMonitoring) return;

            // Monitor connection changes
            if ('connection' in navigator) {
                const connection = navigator.connection;
                
                connection.addEventListener('change', () => {
                    this.handleConnectionChange(connection);
                });

                // Initial connection info
                this.trackConnectionInfo(connection);
            }

            // Monitor online/offline status
            window.addEventListener('online', () => {
                this.handleNetworkStatusChange('online');
            });

            window.addEventListener('offline', () => {
                this.handleNetworkStatusChange('offline');
            });
        },

        /**
         * Handle connection changes
         */
        handleConnectionChange: function(connection) {
            const connectionData = {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData,
                timestamp: new Date().toISOString()
            };

            this.addToReportingQueue({
                type: 'connection_change',
                data: connectionData
            });

            console.log('Connection changed:', connectionData);
        },

        /**
         * Handle network status changes
         */
        handleNetworkStatusChange: function(status) {
            const statusData = {
                status: status,
                timestamp: new Date().toISOString()
            };

            this.addToReportingQueue({
                type: 'network_status',
                data: statusData
            });

            console.log('Network status changed:', status);
        },

        /**
         * Attempt error recovery
         */
        attemptErrorRecovery: function(element, src, errorType) {
            // Try CDN fallback if available
            if (window.CDNFallback && this.isLocalResource(src)) {
                const filename = src.split('/').pop();
                if (window.CDNFallback.hasFallback(filename)) {
                    console.log(`Attempting CDN fallback for: ${filename}`);
                    window.CDNFallback.loadFallback(filename);
                }
            }

            // Retry after delay for network errors
            if (errorType === 'network_error' && element.tagName) {
                setTimeout(() => {
                    this.retryResourceLoad(element, src);
                }, 2000);
            }
        },

        /**
         * Retry resource loading
         */
        retryResourceLoad: function(element, originalSrc) {
            if (element.tagName === 'SCRIPT') {
                const newScript = document.createElement('script');
                newScript.src = originalSrc + '?retry=' + Date.now();
                document.head.appendChild(newScript);
            } else if (element.tagName === 'LINK') {
                const newLink = document.createElement('link');
                newLink.rel = 'stylesheet';
                newLink.href = originalSrc + '?retry=' + Date.now();
                document.head.appendChild(newLink);
            }
        },

        /**
         * Handle slow resources
         */
        handleSlowResource: function(resourceData) {
            console.warn('Slow resource detected:', resourceData);
            
            this.addToReportingQueue({
                type: 'slow_resource',
                data: resourceData
            });
        },

        /**
         * Handle large resources
         */
        handleLargeResource: function(resourceData) {
            console.warn('Large resource detected:', resourceData);
            
            this.addToReportingQueue({
                type: 'large_resource',
                data: resourceData
            });
        },

        /**
         * Handle slow requests
         */
        handleSlowRequest: function(requestData) {
            console.warn('Slow request detected:', requestData);
            
            this.addToReportingQueue({
                type: 'slow_request',
                data: requestData
            });
        },

        /**
         * Handle slow page loads
         */
        handleSlowPageLoad: function(navigationData) {
            console.warn('Slow page load detected:', navigationData);
            
            this.addToReportingQueue({
                type: 'slow_page_load',
                data: navigationData
            });
        },

        /**
         * Add item to reporting queue
         */
        addToReportingQueue: function(item) {
            this.reportingQueue.push(item);
            
            // Send immediately if queue is full
            if (this.reportingQueue.length >= this.config.batchSize) {
                this.sendReports();
            }
        },

        /**
         * Start reporting timer
         */
        startReportingTimer: function() {
            const self = this;
            
            this.reportingTimer = setInterval(function() {
                if (self.reportingQueue.length > 0) {
                    self.sendReports();
                }
            }, this.config.reportingInterval);
        },

        /**
         * Send reports to server
         */
        sendReports: function() {
            if (this.reportingQueue.length === 0) return;

            const reports = this.reportingQueue.splice(0, this.config.batchSize);
            
            fetch(this.config.reportingEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    reports: reports,
                    metadata: {
                        userAgent: navigator.userAgent,
                        url: window.location.href,
                        timestamp: new Date().toISOString()
                    }
                })
            })
            .catch(error => {
                console.warn('Failed to send asset error reports:', error);
                // Put reports back in queue for retry
                this.reportingQueue.unshift(...reports);
            });
        },

        /**
         * Utility methods
         */
        getResourceType: function(url) {
            if (url.includes('.css')) return 'css';
            if (url.includes('.js')) return 'js';
            if (url.match(/\.(jpg|jpeg|png|gif|svg|webp)$/i)) return 'image';
            if (url.includes('.woff') || url.includes('.ttf')) return 'font';
            return 'other';
        },

        isLocalResource: function(url) {
            return !url.includes('://') || url.includes(window.location.hostname);
        },

        trackConnectionInfo: function(connection) {
            this.performance.connection = {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData
            };
        },

        getCSRFToken: function() {
            const token = document.querySelector('meta[name="csrf-token"]');
            return token ? token.getAttribute('content') : '';
        },

        triggerMonitorEvent: function(eventType, data) {
            const event = new CustomEvent('assetLoadingMonitor' + eventType.charAt(0).toUpperCase() + eventType.slice(1), {
                detail: data
            });
            window.dispatchEvent(event);
        },

        /**
         * Get monitoring statistics
         */
        getStats: function() {
            return {
                errors: {
                    notFound: this.errors.notFound.length,
                    networkErrors: this.errors.networkErrors.length,
                    timeouts: this.errors.timeouts.length
                },
                performance: {
                    resourceCount: Object.keys(this.performance.loadTimes).length,
                    averageLoadTime: this.calculateAverageLoadTime(),
                    slowResources: this.getSlowResources().length
                },
                reporting: {
                    queueSize: this.reportingQueue.length,
                    totalReported: this.errors.notFound.length + this.errors.networkErrors.length + this.errors.timeouts.length
                }
            };
        },

        calculateAverageLoadTime: function() {
            const loadTimes = Object.values(this.performance.loadTimes);
            if (loadTimes.length === 0) return 0;
            
            const total = loadTimes.reduce((sum, resource) => sum + resource.duration, 0);
            return total / loadTimes.length;
        },

        getSlowResources: function() {
            return Object.values(this.performance.loadTimes).filter(resource => resource.duration > 5000);
        }
    };

    // Initialize asset loading monitor when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            AssetLoadingMonitor.init();
        });
    } else {
        AssetLoadingMonitor.init();
    }

    // Make AssetLoadingMonitor globally available
    window.AssetLoadingMonitor = AssetLoadingMonitor;

})();