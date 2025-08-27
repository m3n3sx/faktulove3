/**
 * CDN Fallback System - Fixed Version
 * Handles asset loading with proper fallback logic
 */

(function() {
    'use strict';

    const CDN_FALLBACKS = {
        'assets/css/lib/bootstrap.min.css': {
            cdn: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
            integrity: 'sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN',
            critical: true
        },
        'assets/css/lib/dataTables.min.css': {
            cdn: 'https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css',
            critical: false
        },
        'assets/css/lib/flatpickr.min.css': {
            cdn: 'https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.css',
            critical: false
        },
        'assets/css/lib/full-calendar.css': {
            cdn: 'https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.css',
            critical: false
        },
        'assets/css/lib/magnific-popup.css': {
            cdn: 'https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/magnific-popup.min.css',
            critical: false
        },
        'assets/css/lib/slick.css': {
            cdn: 'https://cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.css',
            critical: false
        },
        'assets/css/lib/prism.css': {
            cdn: 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css',
            critical: false
        },
        'assets/js/lib/jquery-3.7.1.min.js': {
            cdn: 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js',
            integrity: 'sha512-v2CJ7UaYy4JwqLDIrZUI/4hqeoQieOmAZNXBeQyjo21dadnwR+8ZaIJVT8EE2iyI61OV8e6M8PP2/4hpQINQ/g==',
            critical: true,
            test: function() { return typeof jQuery !== 'undefined'; }
        },
        'assets/js/lib/bootstrap.bundle.min.js': {
            cdn: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
            integrity: 'sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL',
            critical: true,
            test: function() { return typeof bootstrap !== 'undefined'; }
        },
        'assets/js/lib/apexcharts.min.js': {
            cdn: 'https://cdn.jsdelivr.net/npm/apexcharts@latest/dist/apexcharts.min.js',
            critical: true,
            test: function() { return typeof ApexCharts !== 'undefined'; }
        },
        'assets/js/lib/dataTables.min.js': {
            cdn: 'https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js',
            critical: false,
            test: function() { return typeof $.fn.DataTable !== 'undefined'; }
        },
        'assets/js/lib/iconify-icon.min.js': {
            cdn: 'https://code.iconify.design/3/3.1.1/iconify.min.js',
            critical: false,
            test: function() { return typeof Iconify !== 'undefined'; }
        },
        'assets/js/lib/jquery-ui.min.js': {
            cdn: 'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.13.2/jquery-ui.min.js',
            critical: false,
            test: function() { return typeof $.ui !== 'undefined'; }
        },
        'assets/js/lib/magnific-popup.min.js': {
            cdn: 'https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/jquery.magnific-popup.min.js',
            critical: false,
            test: function() { return typeof $.fn.magnificPopup !== 'undefined'; }
        },
        'assets/js/lib/slick.min.js': {
            cdn: 'https://cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.min.js',
            critical: false,
            test: function() { return typeof $.fn.slick !== 'undefined'; }
        },
        'assets/js/lib/prism.js': {
            cdn: 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js',
            critical: false,
            test: function() { return typeof Prism !== 'undefined'; }
        }
    };

    const loadingState = {
        failed: [],
        loaded: [],
        fallbacksUsed: [],
        cdnFailures: new Set() // Track CDN failures to avoid infinite loops
    };

    const utils = {
        log: function(message, type = 'info') {
            if (console && console[type]) {
                console[type]('[CDN Fallback]', message);
            }
        },

        createLink: function(href, integrity = null) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            if (integrity) {
                link.integrity = integrity;
                link.crossOrigin = 'anonymous';
            }
            return link;
        },

        createScript: function(src, integrity = null) {
            const script = document.createElement('script');
            script.src = src;
            if (integrity) {
                script.integrity = integrity;
                script.crossOrigin = 'anonymous';
            }
            return script;
        },

        isCSS: function(url) {
            return url.includes('.css');
        },

        isCDN: function(url) {
            return url.includes('cdn.jsdelivr.net') || 
                   url.includes('cdnjs.cloudflare.com') || 
                   url.includes('code.iconify.design') ||
                   url.includes('cdn.datatables.net');
        },

        getStaticUrl: function(path) {
            const staticUrl = window.STATIC_URL || '/static/';
            return staticUrl + path;
        },

        normalizeAssetPath: function(fullPath) {
            const staticUrl = window.STATIC_URL || '/static/';
            if (fullPath.startsWith(staticUrl)) {
                return fullPath.substring(staticUrl.length);
            }
            return fullPath;
        }
    };

    const assetLoader = {
        loadCSS: function(href, fallbackConfig) {
            return new Promise((resolve, reject) => {
                const link = utils.createLink(href, fallbackConfig.integrity);
                
                link.onload = function() {
                    utils.log(`CSS loaded successfully: ${href}`);
                    loadingState.loaded.push(href);
                    resolve(link);
                };
                
                link.onerror = function() {
                    utils.log(`CSS failed to load: ${href}`, 'warn');
                    loadingState.failed.push(href);
                    reject(new Error(`Failed to load CSS: ${href}`));
                };
                
                document.head.appendChild(link);
            });
        },

        loadJS: function(src, fallbackConfig) {
            return new Promise((resolve, reject) => {
                const script = utils.createScript(src, fallbackConfig.integrity);
                
                script.onload = function() {
                    utils.log(`JS loaded successfully: ${src}`);
                    loadingState.loaded.push(src);
                    
                    if (fallbackConfig.test && !fallbackConfig.test()) {
                        utils.log(`JS library test failed: ${src}`, 'warn');
                        reject(new Error(`Library test failed: ${src}`));
                        return;
                    }
                    
                    resolve(script);
                };
                
                script.onerror = function() {
                    utils.log(`JS failed to load: ${src}`, 'warn');
                    loadingState.failed.push(src);
                    reject(new Error(`Failed to load JS: ${src}`));
                };
                
                document.head.appendChild(script);
            });
        },

        loadFallback: function(assetPath, fallbackConfig) {
            const cdnUrl = fallbackConfig.cdn;
            
            // Check if this CDN has already failed
            if (loadingState.cdnFailures.has(cdnUrl)) {
                utils.log(`CDN already failed, skipping: ${cdnUrl}`, 'warn');
                return Promise.reject(new Error(`CDN already failed: ${cdnUrl}`));
            }
            
            utils.log(`Loading fallback from CDN: ${cdnUrl}`, 'warn');
            loadingState.fallbacksUsed.push({
                original: assetPath,
                fallback: cdnUrl,
                timestamp: new Date().toISOString()
            });
            
            if (utils.isCSS(cdnUrl)) {
                return this.loadCSS(cdnUrl, fallbackConfig);
            } else {
                return this.loadJS(cdnUrl, fallbackConfig);
            }
        }
    };

    const fallbackSystem = {
        init: function() {
            utils.log('Initializing CDN fallback system');
            this.checkExistingAssets();
            this.setupErrorHandlers();
            this.reportStatus();
        },

        checkExistingAssets: function() {
            Object.keys(CDN_FALLBACKS).forEach(assetPath => {
                const fullPath = utils.getStaticUrl(assetPath);
                this.testAsset(fullPath, CDN_FALLBACKS[assetPath]);
            });
        },

        testAsset: function(fullPath, fallbackConfig) {
            const assetPath = utils.normalizeAssetPath(fullPath);
            
            if (utils.isCSS(fullPath)) {
                this.testCSSAsset(fullPath, fallbackConfig);
            } else {
                this.testJSAsset(fullPath, fallbackConfig);
            }
        },

        testCSSAsset: function(href, fallbackConfig) {
            const testLink = utils.createLink(href);
            
            testLink.onload = function() {
                loadingState.loaded.push(href);
            };
            
            testLink.onerror = function() {
                fallbackSystem.handleAssetFailure(href, fallbackConfig);
            };
            
            document.head.appendChild(testLink);
            
            // Remove test link after a short delay
            setTimeout(() => {
                if (testLink.parentNode) {
                    testLink.parentNode.removeChild(testLink);
                }
            }, 100);
        },

        testJSAsset: function(src, fallbackConfig) {
            // If library is already available, mark as loaded
            if (fallbackConfig.test && fallbackConfig.test()) {
                loadingState.loaded.push(src);
                return;
            }
            
            const testScript = utils.createScript(src);
            
            testScript.onload = function() {
                if (!fallbackConfig.test || fallbackConfig.test()) {
                    loadingState.loaded.push(src);
                } else {
                    fallbackSystem.handleAssetFailure(src, fallbackConfig);
                }
                
                if (testScript.parentNode) {
                    testScript.parentNode.removeChild(testScript);
                }
            };
            
            testScript.onerror = function() {
                fallbackSystem.handleAssetFailure(src, fallbackConfig);
                
                if (testScript.parentNode) {
                    testScript.parentNode.removeChild(testScript);
                }
            };
            
            document.head.appendChild(testScript);
        },

        handleAssetFailure: function(assetUrl, fallbackConfig) {
            utils.log(`Asset failed, attempting fallback: ${assetUrl}`, 'error');
            loadingState.failed.push(assetUrl);
            
            // Check if this is already a CDN URL (to avoid infinite fallback loops)
            if (utils.isCDN(assetUrl)) {
                utils.log(`Skipping CDN fallback for already failed CDN asset: ${assetUrl}`, 'warn');
                loadingState.cdnFailures.add(assetUrl);
                this.handleCriticalFailure(assetUrl, fallbackConfig);
                return;
            }
            
            assetLoader.loadFallback(assetUrl, fallbackConfig)
                .then(() => {
                    utils.log(`Fallback successful for: ${assetUrl}`);
                })
                .catch(error => {
                    utils.log(`Fallback also failed for: ${assetUrl}`, 'error');
                    
                    // Mark CDN as failed
                    if (utils.isCDN(fallbackConfig.cdn)) {
                        loadingState.cdnFailures.add(fallbackConfig.cdn);
                    }
                    
                    this.handleCriticalFailure(assetUrl, fallbackConfig);
                });
        },

        handleCriticalFailure: function(assetUrl, fallbackConfig) {
            if (fallbackConfig.critical) {
                utils.log(`Critical asset failed: ${assetUrl}`, 'error');
                this.showUserNotification(assetUrl);
            }
        },

        showUserNotification: function(assetUrl) {
            const notification = document.createElement('div');
            notification.className = 'cdn-fallback-notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                padding: 12px 16px;
                z-index: 9999;
                max-width: 300px;
                font-size: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            `;
            
            notification.innerHTML = `
                <strong>Asset Loading Issue</strong><br>
                Some features may not work properly due to network issues.
                <button onclick="this.parentNode.remove()" style="float: right; background: none; border: none; font-size: 16px; cursor: pointer;">&times;</button>
            `;
            
            document.body.appendChild(notification);
            
            // Auto-remove after 10 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 10000);
        },

        setupErrorHandlers: function() {
            window.addEventListener('error', (event) => {
                if (event.target && (event.target.tagName === 'LINK' || event.target.tagName === 'SCRIPT')) {
                    const url = event.target.href || event.target.src;
                    const assetPath = utils.normalizeAssetPath(url);
                    
                    if (CDN_FALLBACKS[assetPath]) {
                        utils.log(`Caught loading error for: ${url}`, 'warn');
                        this.handleAssetFailure(url, CDN_FALLBACKS[assetPath]);
                    }
                }
            }, true);
        },

        reportStatus: function() {
            setTimeout(() => {
                utils.log('Asset loading report:', 'info');
                utils.log(`Loaded: ${loadingState.loaded.length}`, 'info');
                utils.log(`Failed: ${loadingState.failed.length}`, 'warn');
                utils.log(`Fallbacks used: ${loadingState.fallbacksUsed.length}`, 'warn');
                utils.log(`CDN failures: ${loadingState.cdnFailures.size}`, 'warn');
                
                if (loadingState.fallbacksUsed.length > 0) {
                    utils.log('Fallbacks used:', loadingState.fallbacksUsed);
                }
                
                if (loadingState.cdnFailures.size > 0) {
                    utils.log('CDN failures:', Array.from(loadingState.cdnFailures));
                }
                
                // Store status in window for debugging
                window.cdnFallbackStatus = {
                    loaded: loadingState.loaded,
                    failed: loadingState.failed,
                    fallbacksUsed: loadingState.fallbacksUsed,
                    cdnFailures: Array.from(loadingState.cdnFailures)
                };
            }, 2000);
        },

        loadAsset: function(assetPath) {
            const fallbackConfig = CDN_FALLBACKS[assetPath];
            if (!fallbackConfig) {
                utils.log(`No fallback configured for: ${assetPath}`, 'warn');
                return Promise.reject(new Error('No fallback configured'));
            }
            
            const fullPath = utils.getStaticUrl(assetPath);
            return assetLoader.loadFallback(fullPath, fallbackConfig);
        },

        simulateFailure: function(assetPath) {
            const fallbackConfig = CDN_FALLBACKS[assetPath];
            if (fallbackConfig) {
                utils.log(`Simulating failure for: ${assetPath}`, 'warn');
                this.handleAssetFailure(utils.getStaticUrl(assetPath), fallbackConfig);
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            fallbackSystem.init();
        });
    } else {
        fallbackSystem.init();
    }

    // Expose public API
    window.CDNFallback = {
        loadAsset: fallbackSystem.loadAsset.bind(fallbackSystem),
        loadFallback: function(assetName) {
            // Try to find the asset by name in the CDN_FALLBACKS
            let assetPath = null;
            for (const path in CDN_FALLBACKS) {
                if (path.endsWith(assetName)) {
                    assetPath = path;
                    break;
                }
            }
            
            if (assetPath && CDN_FALLBACKS[assetPath]) {
                const fallbackConfig = CDN_FALLBACKS[assetPath];
                return assetLoader.loadFallback(assetPath, fallbackConfig);
            } else {
                utils.log(`No fallback configured for asset: ${assetName}`, 'warn');
                return Promise.reject(new Error(`No fallback configured for: ${assetName}`));
            }
        },
        simulateFailure: fallbackSystem.simulateFailure.bind(fallbackSystem),
        getStatus: function() {
            return {
                loaded: loadingState.loaded,
                failed: loadingState.failed,
                fallbacksUsed: loadingState.fallbacksUsed,
                cdnFailures: Array.from(loadingState.cdnFailures)
            };
        },
        hasFallback: function(assetPath) {
            return CDN_FALLBACKS.hasOwnProperty(assetPath);
        },
        handleFailedAsset: function(asset) {
            const assetPath = utils.normalizeAssetPath(asset.src || asset.href);
            if (CDN_FALLBACKS[assetPath]) {
                fallbackSystem.handleAssetFailure(asset.src || asset.href, CDN_FALLBACKS[assetPath]);
            }
        }
    };

})();
