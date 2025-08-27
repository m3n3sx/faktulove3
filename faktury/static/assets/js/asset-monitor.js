/**
 * Asset Monitor for FaktuLove Application
 * Monitors asset loading status and provides fallback mechanisms
 */

(function() {
    'use strict';

    const AssetMonitor = {
        config: {
            checkInterval: 5000, // Check every 5 seconds
            retryAttempts: 3,
            retryDelay: 2000,
            enablePerformanceMonitoring: true
        },

        assets: {
            critical: [],
            optional: [],
            failed: [],
            loaded: []
        },

        performance: {
            loadTimes: {},
            totalLoadTime: 0,
            startTime: performance.now()
        },

        /**
         * Initialize asset monitoring
         */
        init: function() {
            this.identifyAssets();
            this.startMonitoring();
            this.setupPerformanceMonitoring();
            console.log('AssetMonitor initialized');
        },

        /**
         * Identify and categorize assets on the page
         */
        identifyAssets: function() {
            const self = this;
            
            // Critical CSS assets
            const criticalCSS = [
                'bootstrap.min.css',
                'style.css',
                'remixicon.css'
            ];

            // Critical JavaScript assets
            const criticalJS = [
                'jquery',
                'bootstrap.bundle.min.js',
                'app.js'
            ];

            // Optional assets
            const optionalAssets = [
                'dataTables.min.css',
                'dataTables.min.js',
                'apexcharts.min.js',
                'flatpickr.min.css',
                'magnific-popup.css'
            ];

            // Scan all link and script tags
            document.querySelectorAll('link[rel="stylesheet"], script[src]').forEach(function(element) {
                const src = element.href || element.src;
                if (!src) return;

                const filename = src.split('/').pop();
                const assetInfo = {
                    element: element,
                    src: src,
                    filename: filename,
                    type: element.tagName.toLowerCase(),
                    loadTime: null,
                    status: 'pending'
                };

                // Categorize asset
                if (self.isCriticalAsset(filename, criticalCSS.concat(criticalJS))) {
                    self.assets.critical.push(assetInfo);
                } else if (self.isOptionalAsset(filename, optionalAssets)) {
                    self.assets.optional.push(assetInfo);
                }
            });

            console.log('Assets identified:', {
                critical: this.assets.critical.length,
                optional: this.assets.optional.length
            });
        },

        /**
         * Check if asset is critical
         */
        isCriticalAsset: function(filename, criticalList) {
            return criticalList.some(function(critical) {
                return filename.includes(critical);
            });
        },

        /**
         * Check if asset is optional
         */
        isOptionalAsset: function(filename, optionalList) {
            return optionalList.some(function(optional) {
                return filename.includes(optional);
            });
        },

        /**
         * Start monitoring asset loading
         */
        startMonitoring: function() {
            const self = this;
            
            // Monitor critical assets immediately
            this.checkAssetStatus(this.assets.critical, true);
            
            // Monitor optional assets
            this.checkAssetStatus(this.assets.optional, false);

            // Set up periodic monitoring
            setInterval(function() {
                self.performPeriodicCheck();
            }, this.config.checkInterval);
        },

        /**
         * Check status of asset list
         */
        checkAssetStatus: function(assetList, isCritical) {
            const self = this;
            
            assetList.forEach(function(asset) {
                if (asset.status === 'pending') {
                    self.testAssetLoad(asset, isCritical);
                }
            });
        },

        /**
         * Test if an asset has loaded successfully
         */
        testAssetLoad: function(asset, isCritical) {
            const self = this;
            const startTime = performance.now();

            if (asset.type === 'link') {
                // Test CSS loading
                this.testCSSLoad(asset, startTime, isCritical);
            } else if (asset.type === 'script') {
                // Test JavaScript loading
                this.testJSLoad(asset, startTime, isCritical);
            }
        },

        /**
         * Test CSS asset loading
         */
        testCSSLoad: function(asset, startTime, isCritical) {
            const self = this;
            
            // Check if stylesheet is loaded
            const isLoaded = Array.from(document.styleSheets).some(function(sheet) {
                try {
                    return sheet.href && sheet.href.includes(asset.filename);
                } catch (e) {
                    return false;
                }
            });

            if (isLoaded) {
                this.markAssetLoaded(asset, startTime);
            } else {
                // Check if element exists and has error
                if (asset.element.sheet === null) {
                    this.markAssetFailed(asset, isCritical);
                }
            }
        },

        /**
         * Test JavaScript asset loading
         */
        testJSLoad: function(asset, startTime, isCritical) {
            const self = this;
            
            // For jQuery, check if $ is available
            if (asset.filename.includes('jquery')) {
                if (typeof $ !== 'undefined' || typeof jQuery !== 'undefined') {
                    this.markAssetLoaded(asset, startTime);
                    return;
                }
            }

            // For Bootstrap, check if bootstrap is available
            if (asset.filename.includes('bootstrap')) {
                if (typeof bootstrap !== 'undefined') {
                    this.markAssetLoaded(asset, startTime);
                    return;
                }
            }

            // For ApexCharts, check if ApexCharts is available
            if (asset.filename.includes('apexcharts')) {
                if (typeof ApexCharts !== 'undefined') {
                    this.markAssetLoaded(asset, startTime);
                    return;
                }
            }

            // Generic check - if script element exists and no error occurred
            if (asset.element && !asset.element.hasAttribute('data-error')) {
                // Assume loaded if element exists and no explicit error
                setTimeout(function() {
                    if (asset.status === 'pending') {
                        self.markAssetLoaded(asset, startTime);
                    }
                }, 1000);
            }
        },

        /**
         * Mark asset as successfully loaded
         */
        markAssetLoaded: function(asset, startTime) {
            asset.status = 'loaded';
            asset.loadTime = performance.now() - startTime;
            this.assets.loaded.push(asset);
            this.performance.loadTimes[asset.filename] = asset.loadTime;

            console.log(`Asset loaded: ${asset.filename} (${asset.loadTime.toFixed(2)}ms)`);
            
            // Trigger loaded event
            this.triggerAssetEvent('assetLoaded', asset);
        },

        /**
         * Mark asset as failed to load
         */
        markAssetFailed: function(asset, isCritical) {
            asset.status = 'failed';
            this.assets.failed.push(asset);

            console.warn(`Asset failed to load: ${asset.filename}`);
            
            // Report to error handler if available
            if (window.ErrorHandler) {
                window.ErrorHandler.reportError(
                    `Failed to load ${asset.type}: ${asset.filename}`,
                    'asset',
                    { asset: asset, isCritical: isCritical }
                );
            }

            // Trigger failed event
            this.triggerAssetEvent('assetFailed', asset);

            // Attempt fallback for critical assets
            if (isCritical && window.CDNFallback) {
                window.CDNFallback.handleFailedAsset(asset);
            }
        },

        /**
         * Perform periodic asset status check
         */
        performPeriodicCheck: function() {
            // Check for any new assets that might have been added dynamically
            this.identifyAssets();
            
            // Re-check failed assets (for retry logic)
            const self = this;
            this.assets.failed.forEach(function(asset) {
                if (asset.retryCount < self.config.retryAttempts) {
                    asset.retryCount = (asset.retryCount || 0) + 1;
                    asset.status = 'pending';
                    
                    setTimeout(function() {
                        self.testAssetLoad(asset, self.isCriticalAsset(asset.filename, []));
                    }, self.config.retryDelay);
                }
            });
        },

        /**
         * Setup performance monitoring
         */
        setupPerformanceMonitoring: function() {
            if (!this.config.enablePerformanceMonitoring) return;

            const self = this;
            
            // Monitor page load performance
            window.addEventListener('load', function() {
                self.performance.totalLoadTime = performance.now() - self.performance.startTime;
                self.generatePerformanceReport();
            });

            // Monitor navigation timing if available
            if ('navigation' in performance) {
                setTimeout(function() {
                    self.analyzeNavigationTiming();
                }, 1000);
            }
        },

        /**
         * Generate performance report
         */
        generatePerformanceReport: function() {
            const report = {
                totalLoadTime: this.performance.totalLoadTime,
                assetLoadTimes: this.performance.loadTimes,
                failedAssets: this.assets.failed.length,
                totalAssets: this.assets.critical.length + this.assets.optional.length,
                criticalAssetsLoaded: this.assets.critical.filter(a => a.status === 'loaded').length,
                optionalAssetsLoaded: this.assets.optional.filter(a => a.status === 'loaded').length
            };

            console.group('Asset Loading Performance Report');
            console.log('Total page load time:', report.totalLoadTime.toFixed(2) + 'ms');
            console.log('Critical assets loaded:', report.criticalAssetsLoaded + '/' + this.assets.critical.length);
            console.log('Optional assets loaded:', report.optionalAssetsLoaded + '/' + this.assets.optional.length);
            console.log('Failed assets:', report.failedAssets);
            console.log('Asset load times:', report.assetLoadTimes);
            console.groupEnd();

            // Store report for external access
            this.lastPerformanceReport = report;
            
            // Trigger performance report event
            this.triggerAssetEvent('performanceReport', report);
        },

        /**
         * Analyze navigation timing
         */
        analyzeNavigationTiming: function() {
            const timing = performance.getEntriesByType('navigation')[0];
            if (!timing) return;

            const analysis = {
                dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
                tcpConnection: timing.connectEnd - timing.connectStart,
                serverResponse: timing.responseEnd - timing.requestStart,
                domProcessing: timing.domContentLoadedEventEnd - timing.responseEnd,
                resourceLoading: timing.loadEventEnd - timing.domContentLoadedEventEnd
            };

            console.log('Navigation timing analysis:', analysis);
            this.navigationTiming = analysis;
        },

        /**
         * Trigger asset-related events
         */
        triggerAssetEvent: function(eventType, data) {
            const event = new CustomEvent('assetMonitor' + eventType.charAt(0).toUpperCase() + eventType.slice(1), {
                detail: data
            });
            window.dispatchEvent(event);
        },

        /**
         * Get asset loading statistics
         */
        getStats: function() {
            return {
                critical: {
                    total: this.assets.critical.length,
                    loaded: this.assets.critical.filter(a => a.status === 'loaded').length,
                    failed: this.assets.critical.filter(a => a.status === 'failed').length
                },
                optional: {
                    total: this.assets.optional.length,
                    loaded: this.assets.optional.filter(a => a.status === 'loaded').length,
                    failed: this.assets.optional.filter(a => a.status === 'failed').length
                },
                performance: this.lastPerformanceReport,
                navigationTiming: this.navigationTiming
            };
        },

        /**
         * Force check of specific asset
         */
        checkAsset: function(filename) {
            const asset = this.findAssetByFilename(filename);
            if (asset) {
                this.testAssetLoad(asset, this.isCriticalAsset(filename, []));
                return asset;
            }
            return null;
        },

        /**
         * Find asset by filename
         */
        findAssetByFilename: function(filename) {
            const allAssets = this.assets.critical.concat(this.assets.optional);
            return allAssets.find(function(asset) {
                return asset.filename.includes(filename);
            });
        }
    };

    // Initialize asset monitor when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            AssetMonitor.init();
        });
    } else {
        AssetMonitor.init();
    }

    // Make AssetMonitor globally available
    window.AssetMonitor = AssetMonitor;

})();