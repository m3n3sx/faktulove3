/**
 * Manual CDN Fallback Test
 * Simple test that can be run in browser console to verify fallback functionality
 */

(function() {
    'use strict';

    // Manual test function that can be called from browser console
    window.testCDNFallback = function() {
        console.log('=== CDN Fallback Manual Test ===');
        
        // Test 1: Check if fallback system is loaded
        console.log('1. Checking if CDN fallback system is loaded...');
        if (typeof window.CDNFallback !== 'undefined') {
            console.log('✓ CDNFallback is available');
        } else {
            console.log('✗ CDNFallback is not available');
            return;
        }
        
        // Test 2: Check if dependency manager is loaded
        console.log('2. Checking if dependency manager is loaded...');
        if (typeof window.DependencyManager !== 'undefined') {
            console.log('✓ DependencyManager is available');
            
            // Show dependency status
            const stats = window.DependencyManager.getStats();
            console.log('Dependency stats:', stats);
        } else {
            console.log('✗ DependencyManager is not available');
        }
        
        // Test 3: Check if asset monitor is loaded
        console.log('3. Checking if asset monitor is loaded...');
        if (typeof window.AssetMonitor !== 'undefined') {
            console.log('✓ AssetMonitor is available');
            
            // Show asset stats
            const assetStats = window.AssetMonitor.getStats();
            console.log('Asset stats:', assetStats);
        } else {
            console.log('✗ AssetMonitor is not available');
        }
        
        // Test 4: Check available fallback URLs
        console.log('4. Checking available fallback URLs...');
        if (window.CDNFallback) {
            const fallbackUrls = window.CDNFallback.fallbackUrls;
            console.log('Available fallbacks:', Object.keys(fallbackUrls));
            
            // Test specific fallbacks
            const testFiles = ['jquery-3.7.1.min.js', 'bootstrap.bundle.min.js', 'apexcharts.min.js'];
            testFiles.forEach(file => {
                if (window.CDNFallback.hasFallback(file)) {
                    console.log(`✓ Fallback available for ${file}`);
                } else {
                    console.log(`✗ No fallback for ${file}`);
                }
            });
        }
        
        // Test 5: Check library availability
        console.log('5. Checking library availability...');
        const libraries = {
            'jQuery': typeof $ !== 'undefined' || typeof jQuery !== 'undefined',
            'Bootstrap': typeof bootstrap !== 'undefined',
            'ApexCharts': typeof ApexCharts !== 'undefined',
            'DataTables': typeof $.fn !== 'undefined' && typeof $.fn.DataTable !== 'undefined'
        };
        
        Object.entries(libraries).forEach(([name, available]) => {
            if (available) {
                console.log(`✓ ${name} is available`);
            } else {
                console.log(`✗ ${name} is not available`);
            }
        });
        
        console.log('=== Test Complete ===');
        console.log('To manually trigger a fallback test, run: testManualFallback("jquery-3.7.1.min.js")');
    };
    
    // Manual fallback trigger function
    window.testManualFallback = function(filename) {
        console.log(`Testing manual fallback for: ${filename}`);
        
        if (!window.CDNFallback) {
            console.log('✗ CDNFallback not available');
            return;
        }
        
        if (window.CDNFallback.loadFallback(filename)) {
            console.log(`✓ Fallback triggered for ${filename}`);
            
            // Listen for success/failure events
            const successHandler = (event) => {
                if (event.detail.original && event.detail.original.filename === filename) {
                    console.log(`✓ Fallback successful for ${filename}:`, event.detail.fallback);
                    window.removeEventListener('cdnFallbackFallbackSuccess', successHandler);
                }
            };
            
            const failureHandler = (event) => {
                if (event.detail.filename === filename) {
                    console.log(`✗ Fallback failed for ${filename}`);
                    window.removeEventListener('cdnFallbackFallbackFailed', failureHandler);
                }
            };
            
            window.addEventListener('cdnFallbackFallbackSuccess', successHandler);
            window.addEventListener('cdnFallbackFallbackFailed', failureHandler);
            
        } else {
            console.log(`✗ No fallback available for ${filename}`);
        }
    };
    
    // Simulate asset failure function
    window.simulateAssetFailure = function(filename) {
        console.log(`Simulating asset failure for: ${filename}`);
        
        if (!window.CDNFallback) {
            console.log('✗ CDNFallback not available');
            return;
        }
        
        // Create mock failed asset
        const mockAsset = {
            filename: filename,
            src: `/static/assets/js/lib/${filename}`,
            type: filename.endsWith('.css') ? 'link' : 'script',
            element: null
        };
        
        // Trigger fallback handling
        window.CDNFallback.handleFailedAsset(mockAsset);
        console.log(`Asset failure simulated for ${filename}`);
    };
    
    // Auto-run test when page loads (if in test mode)
    if (window.location.pathname.includes('test-cdn-fallback')) {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                console.log('Auto-running CDN fallback test...');
                window.testCDNFallback();
            }, 2000);
        });
    }
    
    console.log('Manual CDN Fallback Test functions loaded. Run testCDNFallback() to start testing.');
    
})();