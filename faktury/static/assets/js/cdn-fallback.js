/**
 * CDN Fallback System for FaktuLove Application
 * Provides fallback mechanisms when local assets fail to load
 */

(function() {
    'use strict';

    const CDNFallback = {
        config: {
            enableFallback: true,
            fallbackTimeout: 5000,
            maxRetries: 2,
            enableIntegrityCheck: true
        },

        // CDN fallback URLs for critical assets
        fallbackUrls: {
            // jQuery
            'jquery-3.7.1.min.js': [
                'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js',
                'https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js',
                'https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js'
            ],
            'jquery.min.js': [
                'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js',
                'https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js'
            ],

            // Bootstrap
            'bootstrap.bundle.min.js': [
                'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/js/bootstrap.bundle.min.js'
            ],
            'bootstrap.min.css': [
                'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css'
            ],

            // ApexCharts
            'apexcharts.min.js': [
                'https://cdn.jsdelivr.net/npm/apexcharts@latest/dist/apexcharts.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/apexcharts/3.44.0/apexcharts.min.js'
            ],

            // DataTables
            'dataTables.min.js': [
                'https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.21/js/jquery.dataTables.min.js'
            ],
            'dataTables.min.css': [
                'https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.21/css/jquery.dataTables.min.css'
            ],

            // Flatpickr
            'flatpickr.min.js': [
                'https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.13/flatpickr.min.js'
            ],
            'flatpickr.min.css': [
                'https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.13/flatpickr.min.css'
            ],

            // Magnific Popup
            'magnific-popup.min.js': [
                'https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/jquery.magnific-popup.min.js'
            ],
            'magnific-popup.css': [
                'https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/magnific-popup.min.css'
            ],

            // Slick Slider
            'slick.min.js': [
                'https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.js'
            ],
            'slick.css': [
                'https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.css'
            ]
        },

        // Integrity hashes for security (optional)
        integrityHashes: {
            'bootstrap@5.3.2/dist/css/bootstrap.min.css': 'sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN',
            'bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js': 'sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL'
        },

        loadedFallbacks: [],
        failedFallbacks: [],

        /**
         * Initialize CDN fallback system
         */
        init: function() {
            this.setupAssetMonitoring();
            console.log('CDNFallback initialized');
        },

        /**
         * Setup monitoring for asset failures
         */
        setupAssetMonitoring: function() {
            const self = this;
            
            // Listen for asset monitor events
            window.addEventListener('assetMonitorAssetFailed', function(event) {
                if (self.config.enableFallback) {
                    self.handleFailedAsset(event.detail);
                }
            });

            // Listen for resource errors directly
            window.addEventListener('error', function(event) {
                if (event.target !== window && self.config.enableFallback) {
                    const element = event.target;
                    const src = element.src || element.href;
                    
                    if (src && self.shouldHandleFallback(src)) {
                        self.handleFailedAsset({
                            element: element,
                            src: src,
                            filename: src.split('/').pop(),
                            type: element.tagName.toLowerCase()
                        });
                    }
                }
            }, true);
        },

        /**
         * Check if we should handle fallback for this asset
         */
        shouldHandleFallback: function(src) {
            // Only handle local assets, not already CDN assets
            return !src.includes('://') || src.includes(window.location.hostname);
        },

        /**
         * Handle failed asset by attempting CDN fallback
         */
        handleFailedAsset: function(asset) {
            if (!this.config.enableFallback) return;

            const filename = this.extractFilename(asset.filename || asset.src);
            const fallbackUrls = this.getFallbackUrls(filename);

            if (fallbackUrls.length === 0) {
                console.warn(`No CDN fallback available for: ${filename}`);
                return;
            }

            console.log(`Attempting CDN fallback for: ${filename}`);
            this.loadFallbackAsset(asset, fallbackUrls, 0);
        },

        /**
         * Extract clean filename from URL
         */
        extractFilename: function(url) {
            if (!url) return '';
            
            const filename = url.split('/').pop().split('?')[0];
            
            // Handle common variations
            const variations = [
                filename,
                filename.replace('.min', ''),
                filename.replace(/\d+\.\d+\.\d+/, '').replace('..', '.'),
                filename.replace(/[-_]\d+\.\d+\.\d+/, '')
            ];

            // Find the best match in our fallback URLs
            for (const variation of variations) {
                if (this.fallbackUrls[variation]) {
                    return variation;
                }
            }

            return filename;
        },

        /**
         * Get fallback URLs for a filename
         */
        getFallbackUrls: function(filename) {
            const exactMatch = this.fallbackUrls[filename];
            if (exactMatch) return exactMatch;

            // Try partial matches
            for (const key in this.fallbackUrls) {
                if (filename.includes(key.replace('.min', '')) || key.includes(filename.replace('.min', ''))) {
                    return this.fallbackUrls[key];
                }
            }

            return [];
        },

        /**
         * Load fallback asset from CDN
         */
        loadFallbackAsset: function(originalAsset, fallbackUrls, urlIndex) {
            if (urlIndex >= fallbackUrls.length) {
                console.error(`All CDN fallbacks failed for: ${originalAsset.filename}`);
                this.failedFallbacks.push(originalAsset);
                this.triggerFallbackEvent('fallbackFailed', originalAsset);
                return;
            }

            const fallbackUrl = fallbackUrls[urlIndex];
            const self = this;

            console.log(`Trying CDN fallback ${urlIndex + 1}/${fallbackUrls.length}: ${fallbackUrl}`);

            if (originalAsset.type === 'script' || originalAsset.element?.tagName === 'SCRIPT') {
                this.loadFallbackScript(fallbackUrl, originalAsset, function(success) {
                    if (success) {
                        self.onFallbackSuccess(originalAsset, fallbackUrl);
                    } else {
                        self.loadFallbackAsset(originalAsset, fallbackUrls, urlIndex + 1);
                    }
                });
            } else if (originalAsset.type === 'link' || originalAsset.element?.tagName === 'LINK') {
                this.loadFallbackCSS(fallbackUrl, originalAsset, function(success) {
                    if (success) {
                        self.onFallbackSuccess(originalAsset, fallbackUrl);
                    } else {
                        self.loadFallbackAsset(originalAsset, fallbackUrls, urlIndex + 1);
                    }
                });
            }
        },

        /**
         * Load fallback JavaScript file
         */
        loadFallbackScript: function(url, originalAsset, callback) {
            const script = document.createElement('script');
            script.src = url;
            script.async = true;
            
            // Add integrity if available
            const integrity = this.getIntegrityHash(url);
            if (integrity && this.config.enableIntegrityCheck) {
                script.integrity = integrity;
                script.crossOrigin = 'anonymous';
            }

            const timeout = setTimeout(function() {
                callback(false);
            }, this.config.fallbackTimeout);

            script.onload = function() {
                clearTimeout(timeout);
                callback(true);
            };

            script.onerror = function() {
                clearTimeout(timeout);
                callback(false);
            };

            document.head.appendChild(script);
        },

        /**
         * Load fallback CSS file
         */
        loadFallbackCSS: function(url, originalAsset, callback) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = url;
            
            // Add integrity if available
            const integrity = this.getIntegrityHash(url);
            if (integrity && this.config.enableIntegrityCheck) {
                link.integrity = integrity;
                link.crossOrigin = 'anonymous';
            }

            const timeout = setTimeout(function() {
                callback(false);
            }, this.config.fallbackTimeout);

            link.onload = function() {
                clearTimeout(timeout);
                callback(true);
            };

            link.onerror = function() {
                clearTimeout(timeout);
                callback(false);
            };

            document.head.appendChild(link);
        },

        /**
         * Get integrity hash for URL
         */
        getIntegrityHash: function(url) {
            for (const key in this.integrityHashes) {
                if (url.includes(key)) {
                    return this.integrityHashes[key];
                }
            }
            return null;
        },

        /**
         * Handle successful fallback loading
         */
        onFallbackSuccess: function(originalAsset, fallbackUrl) {
            console.log(`CDN fallback successful: ${fallbackUrl}`);
            
            this.loadedFallbacks.push({
                original: originalAsset,
                fallback: fallbackUrl,
                timestamp: new Date().toISOString()
            });

            // Remove original failed element if it exists
            if (originalAsset.element && originalAsset.element.parentNode) {
                originalAsset.element.parentNode.removeChild(originalAsset.element);
            }

            this.triggerFallbackEvent('fallbackSuccess', {
                original: originalAsset,
                fallback: fallbackUrl
            });

            // Notify other systems that the asset is now available
            this.notifyAssetAvailable(originalAsset, fallbackUrl);
        },

        /**
         * Notify other systems that an asset is now available
         */
        notifyAssetAvailable: function(originalAsset, fallbackUrl) {
            const filename = originalAsset.filename;
            
            // Trigger specific events for known libraries
            if (filename.includes('jquery')) {
                this.triggerLibraryEvent('jqueryReady');
            } else if (filename.includes('bootstrap')) {
                this.triggerLibraryEvent('bootstrapReady');
            } else if (filename.includes('apexcharts')) {
                this.triggerLibraryEvent('apexchartsReady');
            } else if (filename.includes('dataTables')) {
                this.triggerLibraryEvent('datatablesReady');
            }
        },

        /**
         * Trigger library-specific ready events
         */
        triggerLibraryEvent: function(eventName) {
            const event = new CustomEvent(eventName, {
                detail: { source: 'cdnFallback' }
            });
            window.dispatchEvent(event);
        },

        /**
         * Trigger fallback-related events
         */
        triggerFallbackEvent: function(eventType, data) {
            const event = new CustomEvent('cdnFallback' + eventType.charAt(0).toUpperCase() + eventType.slice(1), {
                detail: data
            });
            window.dispatchEvent(event);
        },

        /**
         * Manually trigger fallback for specific asset
         */
        loadFallback: function(filename) {
            const fallbackUrls = this.getFallbackUrls(filename);
            if (fallbackUrls.length > 0) {
                const mockAsset = {
                    filename: filename,
                    type: filename.endsWith('.css') ? 'link' : 'script'
                };
                this.loadFallbackAsset(mockAsset, fallbackUrls, 0);
                return true;
            }
            return false;
        },

        /**
         * Check if fallback is available for asset
         */
        hasFallback: function(filename) {
            return this.getFallbackUrls(filename).length > 0;
        },

        /**
         * Get fallback statistics
         */
        getStats: function() {
            return {
                loadedFallbacks: this.loadedFallbacks.length,
                failedFallbacks: this.failedFallbacks.length,
                availableFallbacks: Object.keys(this.fallbackUrls).length,
                recentFallbacks: this.loadedFallbacks.slice(-5)
            };
        },

        /**
         * Add custom fallback URL
         */
        addFallback: function(filename, urls) {
            if (!Array.isArray(urls)) {
                urls = [urls];
            }
            this.fallbackUrls[filename] = urls;
        }
    };

    // Initialize CDN fallback when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            CDNFallback.init();
        });
    } else {
        CDNFallback.init();
    }

    // Make CDNFallback globally available
    window.CDNFallback = CDNFallback;

})();