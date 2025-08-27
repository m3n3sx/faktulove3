class AssetMonitor {
    constructor() {
        this.loadingMetrics = [];
        this.failedAssets = [];
        this.performanceData = {};
        this.isInitialized = false;
        this.config = {
            trackPerformance: true,
            alertThreshold: 5000,
            maxMetrics: 100,
            criticalAssets: ['jquery', 'bootstrap', 'app.js', 'style.css', 'cdn-fallback.js', 'dependency-manager.js'],
            monitoredExtensions: ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf']
        };
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        this.setupPerformanceMonitoring();
        this.setupNetworkMonitoring();
        this.setupMutationObserver();
        this.startPerformanceTracking();
        this.isInitialized = true;
        this.log('AssetMonitor initialized successfully');
    }

    setupPerformanceMonitoring() {
        if (!this.config.trackPerformance) return;
        
        document.addEventListener('DOMContentLoaded', () => {
            this.analyzeExistingAssets();
        });
        
        if ('PerformanceObserver' in window) {
            this.setupPerformanceObserver();
        }
    }

    setupPerformanceObserver() {
        try {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    if (this.isMonitoredAsset(entry.name)) {
                        this.recordAssetPerformance(entry);
                    }
                });
            });
            observer.observe({ entryTypes: ['resource'] });
            this.log('PerformanceObserver initialized');
        } catch (error) {
            console.warn('PerformanceObserver not supported:', error);
        }
    }

    setupNetworkMonitoring() {
        if (window.fetch) {
            const originalFetch = window.fetch;
            window.fetch = (...args) => {
                const url = args[0];
                const startTime = performance.now();
                
                return originalFetch.apply(this, args)
                    .then(response => {
                        const endTime = performance.now();
                        this.recordNetworkRequest(url, response.status, endTime - startTime);
                        return response;
                    })
                    .catch(error => {
                        const endTime = performance.now();
                        this.recordNetworkError(url, error, endTime - startTime);
                        throw error;
                    });
            };
        }
        
        if (window.XMLHttpRequest) {
            this.monitorXHR();
        }
    }

    monitorXHR() {
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._assetMonitor = {
                url: url,
                method: method,
                startTime: null
            };
            return originalOpen.apply(this, [method, url, ...args]);
        };
        
        XMLHttpRequest.prototype.send = function(...args) {
            if (this._assetMonitor) {
                this._assetMonitor.startTime = performance.now();
                this.addEventListener('loadend', () => {
                    const endTime = performance.now();
                    const duration = endTime - this._assetMonitor.startTime;
                    if (window.AssetMonitor) {
                        window.AssetMonitor.recordXHRRequest(this._assetMonitor.url, this.status, duration);
                    }
                });
            }
            return originalSend.apply(this, args);
        };
    }

    setupMutationObserver() {
        if (!window.MutationObserver) return;
        
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.monitorNewAsset(node);
                    }
                });
            });
        });
        
        observer.observe(document, {
            childList: true,
            subtree: true
        });
    }

    monitorNewAsset(element) {
        if (element.tagName === 'SCRIPT' && element.src) {
            this.monitorScript(element);
        } else if (element.tagName === 'LINK' && element.rel === 'stylesheet') {
            this.monitorStylesheet(element);
        } else if (element.tagName === 'IMG' && element.src) {
            this.monitorImage(element);
        }
    }

    monitorScript(script) {
        const startTime = performance.now();
        const url = script.src;
        
        script.addEventListener('load', () => {
            const loadTime = performance.now() - startTime;
            this.recordAssetLoad(url, 'script', loadTime, true);
        });
        
        script.addEventListener('error', () => {
            const loadTime = performance.now() - startTime;
            this.recordAssetLoad(url, 'script', loadTime, false);
            this.handleAssetFailure(url, 'script');
        });
    }

    monitorStylesheet(link) {
        const startTime = performance.now();
        const url = link.href;
        
        link.addEventListener('load', () => {
            const loadTime = performance.now() - startTime;
            this.recordAssetLoad(url, 'stylesheet', loadTime, true);
        });
        
        link.addEventListener('error', () => {
            const loadTime = performance.now() - startTime;
            this.recordAssetLoad(url, 'stylesheet', loadTime, false);
            this.handleAssetFailure(url, 'stylesheet');
        });
    }

    monitorImage(img) {
        const startTime = performance.now();
        const url = img.src;
        
        img.addEventListener('load', () => {
            const loadTime = performance.now() - startTime;
            this.recordAssetLoad(url, 'image', loadTime, true);
        });
        
        img.addEventListener('error', () => {
            const loadTime = performance.now() - startTime;
            this.recordAssetLoad(url, 'image', loadTime, false);
            this.handleAssetFailure(url, 'image');
        });
    }

    analyzeExistingAssets() {
        document.querySelectorAll('script[src]').forEach(script => {
            this.checkAssetAvailability(script.src, 'script');
        });
        
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
            this.checkAssetAvailability(link.href, 'stylesheet');
        });
        
        document.querySelectorAll('img[src]').forEach(img => {
            this.checkAssetAvailability(img.src, 'image');
        });
    }

    checkAssetAvailability(url, type) {
        if (!url || url.startsWith('data:')) return;
        
        const startTime = performance.now();
        
        fetch(url, { method: 'HEAD' })
            .then(response => {
                const loadTime = performance.now() - startTime;
                this.recordAssetLoad(url, type, loadTime, response.ok);
                
                if (!response.ok) {
                    this.handleAssetFailure(url, type, response.status);
                }
            })
            .catch(error => {
                const loadTime = performance.now() - startTime;
                this.recordAssetLoad(url, type, loadTime, false);
                this.handleAssetFailure(url, type, 0, error);
            });
    }

    recordAssetPerformance(entry) {
        const metric = {
            name: entry.name,
            type: this.getAssetType(entry.name),
            startTime: entry.startTime,
            duration: entry.duration,
            transferSize: entry.transferSize,
            encodedBodySize: entry.encodedBodySize,
            decodedBodySize: entry.decodedBodySize,
            timestamp: new Date().toISOString(),
            critical: this.isCriticalAsset(entry.name)
        };
        
        this.loadingMetrics.push(metric);
        
        if (this.loadingMetrics.length > this.config.maxMetrics) {
            this.loadingMetrics.shift();
        }
        
        if (metric.duration > this.config.alertThreshold) {
            this.handleSlowAsset(metric);
        }
        
        this.log(`Asset loaded: ${this.getAssetName(entry.name)} (${Math.round(entry.duration)}ms)`);
    }

    recordAssetLoad(url, type, loadTime, success) {
        const record = {
            url,
            type,
            loadTime,
            success,
            timestamp: new Date().toISOString(),
            critical: this.isCriticalAsset(url)
        };
        
        if (success) {
            this.loadingMetrics.push(record);
        } else {
            this.failedAssets.push(record);
        }
        
        if (success && loadTime > this.config.alertThreshold) {
            this.handleSlowAsset(record);
        }
    }

    recordNetworkRequest(url, status, duration) {
        if (!this.isMonitoredAsset(url)) return;
        
        const record = {
            url,
            status,
            duration,
            success: status >= 200 && status < 300,
            timestamp: new Date().toISOString()
        };
        
        if (status === 404) {
            this.handle404Error(url);
        }
        
        this.performanceData[url] = record;
    }

    recordNetworkError(url, error, duration) {
        if (!this.isMonitoredAsset(url)) return;
        
        const record = {
            url,
            error: error.message,
            duration,
            success: false,
            timestamp: new Date().toISOString()
        };
        
        this.failedAssets.push(record);
        this.handleAssetFailure(url, 'network', 0, error);
    }

    recordXHRRequest(url, status, duration) {
        if (!this.isMonitoredAsset(url)) return;
        this.recordNetworkRequest(url, status, duration);
    }

    handleAssetFailure(url, type, status = 0, error = null) {
        const failure = {
            url,
            type,
            status,
            error: error?.message,
            timestamp: new Date().toISOString(),
            critical: this.isCriticalAsset(url)
        };
        
        this.failedAssets.push(failure);
        console.error(`Asset loading failed: ${url} (${type})`, failure);
        
        if (failure.critical) {
            this.alertCriticalAssetFailure(failure);
        }
        
        if (window.ErrorHandler) {
            window.ErrorHandler.handleAssetError({
                type: 'asset_load_failure',
                src: url,
                timestamp: failure.timestamp,
                critical: failure.critical
            });
        }
    }

    handle404Error(url) {
        console.error(`404 Error: Asset not found - ${url}`);
        
        const error404 = {
            url,
            status: 404,
            timestamp: new Date().toISOString(),
            critical: this.isCriticalAsset(url)
        };
        
        this.failedAssets.push(error404);
        
        if (error404.critical) {
            this.alertCriticalAssetFailure(error404);
        }
    }

    handleSlowAsset(metric) {
        console.warn(`Slow asset loading detected: ${metric.name || metric.url} (${Math.round(metric.duration || metric.loadTime)}ms)`);
        
        if (metric.critical && window.ErrorHandler) {
            window.ErrorHandler.showUserNotification(
                `Slow loading detected for critical asset: ${this.getAssetName(metric.name || metric.url)}`,
                'warning'
            );
        }
    }

    alertCriticalAssetFailure(failure) {
        const assetName = this.getAssetName(failure.url);
        console.error(`CRITICAL ASSET FAILURE: ${assetName}`);
        
        if (window.ErrorHandler) {
            window.ErrorHandler.showUserNotification(
                `Critical asset failed to load: ${assetName}. Some features may not work.`,
                'error'
            );
        }
        
        this.attemptFallbackLoading(failure.url);
    }

    attemptFallbackLoading(url) {
        if (window.CDNFallback && typeof window.CDNFallback.loadFallback === 'function') {
            const assetName = this.getAssetName(url);
            try {
                window.CDNFallback.loadFallback(assetName);
            } catch (error) {
                console.warn('CDN fallback failed:', error);
            }
        }
    }

    startPerformanceTracking() {
        window.addEventListener('load', () => {
            this.recordPageLoadMetrics();
        });
        
        if (window.performance && window.performance.timing) {
            this.recordNavigationTiming();
        }
    }

    recordPageLoadMetrics() {
        const timing = window.performance.timing;
        this.performanceData.pageLoad = {
            domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
            pageLoad: timing.loadEventEnd - timing.navigationStart,
            domReady: timing.domComplete - timing.navigationStart,
            timestamp: new Date().toISOString()
        };
        
        this.log(`Page load metrics recorded: ${JSON.stringify(this.performanceData.pageLoad)}`);
    }

    recordNavigationTiming() {
        const timing = window.performance.timing;
        this.performanceData.navigation = {
            redirect: timing.redirectEnd - timing.redirectStart,
            dns: timing.domainLookupEnd - timing.domainLookupStart,
            connect: timing.connectEnd - timing.connectStart,
            request: timing.responseStart - timing.requestStart,
            response: timing.responseEnd - timing.responseStart,
            processing: timing.domComplete - timing.domLoading,
            timestamp: new Date().toISOString()
        };
    }

    isMonitoredAsset(url) {
        if (!url) return false;
        return this.config.monitoredExtensions.some(ext => 
            url.toLowerCase().includes(ext)
        );
    }

    isCriticalAsset(url) {
        if (!url) return false;
        return this.config.criticalAssets.some(asset => 
            url.toLowerCase().includes(asset.toLowerCase())
        );
    }

    getAssetType(url) {
        if (!url) return 'unknown';
        
        const extension = url.split('.').pop().toLowerCase().split('?')[0];
        const typeMap = {
            'js': 'script',
            'css': 'stylesheet',
            'png': 'image',
            'jpg': 'image',
            'jpeg': 'image',
            'gif': 'image',
            'svg': 'image',
            'woff': 'font',
            'woff2': 'font',
            'ttf': 'font'
        };
        
        return typeMap[extension] || 'other';
    }

    getAssetName(url) {
        if (!url) return '';
        return url.split('/').pop().split('?')[0];
    }

    getPerformanceSummary() {
        const successfulLoads = this.loadingMetrics.filter(m => m.success !== false);
        const failedLoads = this.failedAssets;
        const criticalFailures = failedLoads.filter(f => f.critical);
        
        const avgLoadTime = successfulLoads.length > 0 
            ? successfulLoads.reduce((sum, m) => sum + (m.duration || m.loadTime), 0) / successfulLoads.length 
            : 0;
        
        return {
            totalAssets: successfulLoads.length + failedLoads.length,
            successfulLoads: successfulLoads.length,
            failedLoads: failedLoads.length,
            criticalFailures: criticalFailures.length,
            averageLoadTime: Math.round(avgLoadTime),
            slowAssets: successfulLoads.filter(m => (m.duration || m.loadTime) > this.config.alertThreshold).length,
            pageLoadMetrics: this.performanceData.pageLoad,
            navigationMetrics: this.performanceData.navigation
        };
    }

    getFailedAssetsReport() {
        return {
            total: this.failedAssets.length,
            critical: this.failedAssets.filter(f => f.critical).length,
            by404: this.failedAssets.filter(f => f.status === 404).length,
            byType: this.groupBy(this.failedAssets, 'type'),
            recent: this.failedAssets.slice(-10)
        };
    }

    groupBy(array, property) {
        return array.reduce((groups, item) => {
            const key = item[property] || 'unknown';
            groups[key] = (groups[key] || 0) + 1;
            return groups;
        }, {});
    }

    log(message) {
        console.log(`[AssetMonitor] ${message}`);
    }

    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            performance: this.getPerformanceSummary(),
            failures: this.getFailedAssetsReport(),
            metrics: this.loadingMetrics.slice(-20),
            config: this.config
        };
        
        console.log('Asset Monitoring Report:', report);
        return report;
    }

    clearData() {
        this.loadingMetrics = [];
        this.failedAssets = [];
        this.performanceData = {};
        this.log('Monitoring data cleared');
    }
}

window.AssetMonitor = new AssetMonitor();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = AssetMonitor;
}
