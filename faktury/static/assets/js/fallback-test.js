/**
 * CDN Fallback Test Suite
 * Tests the CDN fallback functionality by simulating asset failures
 */

(function() {
    'use strict';

    const FallbackTest = {
        config: {
            testTimeout: 10000,
            enableLogging: true
        },

        testResults: [],
        testCount: 0,

        /**
         * Initialize fallback testing
         */
        init: function() {
            console.log('CDN Fallback Test Suite initialized');
            this.setupTestEnvironment();
        },

        /**
         * Setup test environment
         */
        setupTestEnvironment: function() {
            // Listen for fallback events
            window.addEventListener('cdnFallbackFallbackSuccess', (event) => {
                this.logTestResult('fallback_success', event.detail);
            });

            window.addEventListener('cdnFallbackFallbackFailed', (event) => {
                this.logTestResult('fallback_failed', event.detail);
            });

            // Listen for dependency events
            window.addEventListener('dependencyManagerDependencyReady', (event) => {
                this.logTestResult('dependency_ready', event.detail);
            });

            window.addEventListener('dependencyManagerDependencyFailed', (event) => {
                this.logTestResult('dependency_failed', event.detail);
            });
        },

        /**
         * Test CDN fallback for a specific asset
         */
        testAssetFallback: function(filename, expectedLibrary) {
            return new Promise((resolve, reject) => {
                const testId = ++this.testCount;
                console.log(`Test ${testId}: Testing fallback for ${filename}`);

                // Create a mock failed asset
                const mockAsset = {
                    filename: filename,
                    src: `/static/assets/js/lib/${filename}`,
                    type: filename.endsWith('.css') ? 'link' : 'script',
                    element: null
                };

                // Check if CDN fallback is available
                if (!window.CDNFallback.hasFallback(filename)) {
                    reject(new Error(`No CDN fallback available for ${filename}`));
                    return;
                }

                // Set up timeout
                const timeout = setTimeout(() => {
                    reject(new Error(`Test timeout for ${filename}`));
                }, this.config.testTimeout);

                // Listen for success
                const successHandler = (event) => {
                    if (event.detail.original && event.detail.original.filename === filename) {
                        clearTimeout(timeout);
                        window.removeEventListener('cdnFallbackFallbackSuccess', successHandler);
                        
                        // Verify the library is now available
                        if (expectedLibrary && this.checkLibraryAvailability(expectedLibrary)) {
                            resolve({
                                testId: testId,
                                filename: filename,
                                fallbackUrl: event.detail.fallback,
                                libraryAvailable: true
                            });
                        } else {
                            resolve({
                                testId: testId,
                                filename: filename,
                                fallbackUrl: event.detail.fallback,
                                libraryAvailable: false,
                                warning: 'Library not detected after fallback'
                            });
                        }
                    }
                };

                window.addEventListener('cdnFallbackFallbackSuccess', successHandler);

                // Trigger the fallback
                window.CDNFallback.handleFailedAsset(mockAsset);
            });
        },

        /**
         * Check if a library is available
         */
        checkLibraryAvailability: function(libraryName) {
            switch (libraryName.toLowerCase()) {
                case 'jquery':
                    return typeof $ !== 'undefined' || typeof jQuery !== 'undefined';
                case 'bootstrap':
                    return typeof bootstrap !== 'undefined';
                case 'apexcharts':
                    return typeof ApexCharts !== 'undefined';
                case 'datatables':
                    return typeof $.fn.DataTable !== 'undefined';
                case 'flatpickr':
                    return typeof flatpickr !== 'undefined';
                case 'magnificpopup':
                    return typeof $.fn.magnificPopup !== 'undefined';
                case 'slick':
                    return typeof $.fn.slick !== 'undefined';
                default:
                    return false;
            }
        },

        /**
         * Test all critical assets
         */
        testAllCriticalAssets: function() {
            const criticalAssets = [
                { filename: 'jquery-3.7.1.min.js', library: 'jquery' },
                { filename: 'bootstrap.bundle.min.js', library: 'bootstrap' },
                { filename: 'apexcharts.min.js', library: 'apexcharts' },
                { filename: 'dataTables.min.js', library: 'datatables' },
                { filename: 'flatpickr.min.js', library: 'flatpickr' }
            ];

            console.group('Testing CDN Fallbacks for Critical Assets');

            const testPromises = criticalAssets.map(asset => {
                return this.testAssetFallback(asset.filename, asset.library)
                    .then(result => {
                        console.log(`✓ Test ${result.testId} passed:`, result);
                        return result;
                    })
                    .catch(error => {
                        console.error(`✗ Test failed for ${asset.filename}:`, error);
                        return { filename: asset.filename, error: error.message };
                    });
            });

            return Promise.all(testPromises).then(results => {
                console.groupEnd();
                this.generateTestReport(results);
                return results;
            });
        },

        /**
         * Test asset loading detection
         */
        testAssetLoadingDetection: function() {
            console.log('Testing asset loading detection...');

            // Create a fake script that will fail to load
            const fakeScript = document.createElement('script');
            fakeScript.src = '/static/assets/js/lib/nonexistent-library.js';
            fakeScript.setAttribute('data-test', 'true');

            return new Promise((resolve) => {
                const timeout = setTimeout(() => {
                    resolve({ detected: false, message: 'Asset failure not detected within timeout' });
                }, 3000);

                // Listen for asset monitor events
                const errorHandler = (event) => {
                    if (event.detail && event.detail.src && event.detail.src.includes('nonexistent-library.js')) {
                        clearTimeout(timeout);
                        window.removeEventListener('assetMonitorAssetFailed', errorHandler);
                        resolve({ detected: true, message: 'Asset failure detected successfully' });
                    }
                };

                window.addEventListener('assetMonitorAssetFailed', errorHandler);

                // Add the script to trigger the error
                document.head.appendChild(fakeScript);
            });
        },

        /**
         * Test dependency manager functionality
         */
        testDependencyManager: function() {
            console.log('Testing dependency manager...');

            if (!window.DependencyManager) {
                return Promise.resolve({ error: 'DependencyManager not available' });
            }

            const stats = window.DependencyManager.getStats();
            const allStatuses = window.DependencyManager.getAllStatuses();

            return Promise.resolve({
                stats: stats,
                statuses: allStatuses,
                jqueryReady: window.DependencyManager.isReady('jQuery'),
                bootstrapReady: window.DependencyManager.isReady('Bootstrap')
            });
        },

        /**
         * Run comprehensive fallback tests
         */
        runComprehensiveTests: function() {
            console.log('Starting comprehensive CDN fallback tests...');

            const tests = [
                this.testAssetLoadingDetection(),
                this.testDependencyManager(),
                this.testAllCriticalAssets()
            ];

            return Promise.all(tests).then(results => {
                const report = {
                    timestamp: new Date().toISOString(),
                    assetDetection: results[0],
                    dependencyManager: results[1],
                    fallbackTests: results[2],
                    summary: this.generateSummary(results)
                };

                console.group('Comprehensive Test Report');
                console.log(report);
                console.groupEnd();

                return report;
            });
        },

        /**
         * Generate test summary
         */
        generateSummary: function(results) {
            const fallbackResults = results[2];
            const successful = fallbackResults.filter(r => !r.error).length;
            const failed = fallbackResults.filter(r => r.error).length;

            return {
                totalTests: fallbackResults.length,
                successful: successful,
                failed: failed,
                successRate: ((successful / fallbackResults.length) * 100).toFixed(1) + '%',
                assetDetectionWorking: results[0].detected,
                dependencyManagerWorking: !!results[1].stats
            };
        },

        /**
         * Generate detailed test report
         */
        generateTestReport: function(results) {
            const report = {
                timestamp: new Date().toISOString(),
                totalTests: results.length,
                successful: results.filter(r => !r.error).length,
                failed: results.filter(r => r.error).length,
                results: results
            };

            console.log('CDN Fallback Test Report:', report);
            this.lastTestReport = report;
            return report;
        },

        /**
         * Log test result
         */
        logTestResult: function(type, data) {
            if (this.config.enableLogging) {
                console.log(`[FallbackTest:${type}]`, data);
            }
            
            this.testResults.push({
                type: type,
                data: data,
                timestamp: new Date().toISOString()
            });
        },

        /**
         * Get test statistics
         */
        getTestStats: function() {
            return {
                totalResults: this.testResults.length,
                lastReport: this.lastTestReport,
                recentResults: this.testResults.slice(-10)
            };
        },

        /**
         * Manual fallback trigger for testing
         */
        triggerManualFallback: function(filename) {
            if (window.CDNFallback) {
                return window.CDNFallback.loadFallback(filename);
            }
            return false;
        }
    };

    // Initialize test suite when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            FallbackTest.init();
        });
    } else {
        FallbackTest.init();
    }

    // Make FallbackTest globally available
    window.FallbackTest = FallbackTest;

})();