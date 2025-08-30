#!/usr/bin/env python3
"""
Performance Monitoring and Optimization Verification Script
Validates Core Web Vitals, static file loading, and monitoring systems
"""

import os
import sys
import time
import json
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PerformanceMonitor:
    def __init__(self, base_url="http://localhost:8000", headless=True):
        self.base_url = base_url
        self.results = {
            'core_web_vitals': {},
            'static_file_performance': {},
            'error_tracking': {},
            'monitoring_systems': {},
            'optimization_status': {},
            'recommendations': [],
            'overall_score': 0
        }
        
        # Setup Chrome driver with performance logging
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Enable performance logging
        chrome_options.add_experimental_option('perfLoggingPrefs', {
            'enableNetwork': True,
            'enablePage': True,
        })
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(1920, 1080)
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            sys.exit(1)

    def measure_core_web_vitals(self):
        """Measure Core Web Vitals metrics"""
        print("\n📊 Measuring Core Web Vitals...")
        
        try:
            self.driver.get(self.base_url)
            
            # Wait for page to fully load
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Wait a bit more for all resources to load
            time.sleep(3)
            
            # Measure Core Web Vitals using JavaScript
            web_vitals = self.driver.execute_script("""
                return new Promise((resolve) => {
                    const vitals = {};
                    
                    // Largest Contentful Paint (LCP)
                    new PerformanceObserver((entryList) => {
                        const entries = entryList.getEntries();
                        const lastEntry = entries[entries.length - 1];
                        vitals.lcp = lastEntry.startTime;
                    }).observe({entryTypes: ['largest-contentful-paint']});
                    
                    // First Input Delay (FID) - simulate with click
                    vitals.fid = 0; // Will be measured on interaction
                    
                    // Cumulative Layout Shift (CLS)
                    let clsValue = 0;
                    new PerformanceObserver((entryList) => {
                        for (const entry of entryList.getEntries()) {
                            if (!entry.hadRecentInput) {
                                clsValue += entry.value;
                            }
                        }
                        vitals.cls = clsValue;
                    }).observe({entryTypes: ['layout-shift']});
                    
                    // Get navigation timing
                    const perfData = performance.getEntriesByType('navigation')[0];
                    vitals.ttfb = perfData.responseStart - perfData.requestStart;
                    vitals.fcp = performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0;
                    vitals.loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                    vitals.domContentLoaded = perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart;
                    vitals.totalLoadTime = perfData.loadEventEnd - perfData.fetchStart;
                    
                    // Resource timing
                    const resources = performance.getEntriesByType('resource');
                    vitals.resourceCount = resources.length;
                    vitals.totalResourceSize = resources.reduce((total, resource) => {
                        return total + (resource.transferSize || 0);
                    }, 0);
                    
                    setTimeout(() => resolve(vitals), 2000);
                });
            """)
            
            self.results['core_web_vitals'] = web_vitals
            
            # Evaluate Core Web Vitals
            self.evaluate_web_vitals(web_vitals)
            
        except Exception as e:
            print(f"❌ Failed to measure Core Web Vitals: {e}")
            self.results['core_web_vitals'] = {'error': str(e)}

    def evaluate_web_vitals(self, vitals):
        """Evaluate Core Web Vitals against thresholds"""
        print("\n📈 Evaluating Core Web Vitals...")
        
        # Core Web Vitals thresholds (good/needs improvement/poor)
        thresholds = {
            'lcp': [2500, 4000],  # ms
            'fid': [100, 300],    # ms
            'cls': [0.1, 0.25],   # score
            'ttfb': [800, 1800],  # ms
            'fcp': [1800, 3000],  # ms
        }
        
        scores = {}
        
        for metric, value in vitals.items():
            if metric in thresholds and isinstance(value, (int, float)):
                good_threshold, poor_threshold = thresholds[metric]
                
                if value <= good_threshold:
                    scores[metric] = 'good'
                    print(f"✅ {metric.upper()}: {value:.0f}ms - Good")
                elif value <= poor_threshold:
                    scores[metric] = 'needs_improvement'
                    print(f"⚠️ {metric.upper()}: {value:.0f}ms - Needs Improvement")
                else:
                    scores[metric] = 'poor'
                    print(f"❌ {metric.upper()}: {value:.0f}ms - Poor")
        
        # Overall performance score
        good_count = sum(1 for score in scores.values() if score == 'good')
        total_count = len(scores)
        performance_score = (good_count / total_count * 100) if total_count > 0 else 0
        
        print(f"\n📊 Performance Score: {performance_score:.1f}% ({good_count}/{total_count} metrics good)")
        
        self.results['core_web_vitals']['scores'] = scores
        self.results['core_web_vitals']['performance_score'] = performance_score

    def analyze_static_file_performance(self):
        """Analyze static file loading performance"""
        print("\n📁 Analyzing static file performance...")
        
        try:
            # Get resource timing data
            resource_data = self.driver.execute_script("""
                const resources = performance.getEntriesByType('resource');
                const staticFiles = resources.filter(resource => 
                    resource.name.includes('/static/') || 
                    resource.name.includes('.css') || 
                    resource.name.includes('.js') ||
                    resource.name.includes('.woff') ||
                    resource.name.includes('.ttf')
                );
                
                return staticFiles.map(resource => ({
                    name: resource.name.split('/').pop(),
                    url: resource.name,
                    duration: resource.duration,
                    transferSize: resource.transferSize || 0,
                    encodedBodySize: resource.encodedBodySize || 0,
                    decodedBodySize: resource.decodedBodySize || 0,
                    compressionRatio: resource.encodedBodySize > 0 ? 
                        (resource.decodedBodySize / resource.encodedBodySize) : 1
                }));
            """)
            
            if resource_data:
                total_size = sum(r['transferSize'] for r in resource_data)
                avg_duration = sum(r['duration'] for r in resource_data) / len(resource_data)
                compressed_files = sum(1 for r in resource_data if r['compressionRatio'] > 1.1)
                
                self.results['static_file_performance'] = {
                    'total_files': len(resource_data),
                    'total_size_kb': total_size / 1024,
                    'average_load_time_ms': avg_duration,
                    'compressed_files': compressed_files,
                    'compression_ratio': compressed_files / len(resource_data) if resource_data else 0,
                    'files': resource_data[:10]  # Top 10 files
                }
                
                print(f"✅ Static files analyzed: {len(resource_data)} files")
                print(f"📦 Total size: {total_size/1024:.1f} KB")
                print(f"⏱️ Average load time: {avg_duration:.1f}ms")
                print(f"🗜️ Compressed files: {compressed_files}/{len(resource_data)} ({compressed_files/len(resource_data)*100:.1f}%)")
                
                # Recommendations
                if total_size > 1024 * 1024:  # > 1MB
                    self.results['recommendations'].append("Consider reducing static file sizes")
                
                if avg_duration > 500:  # > 500ms
                    self.results['recommendations'].append("Static file loading is slow, consider CDN or optimization")
                
                if compressed_files / len(resource_data) < 0.7:  # < 70% compressed
                    self.results['recommendations'].append("Enable compression for more static files")
            
        except Exception as e:
            print(f"❌ Failed to analyze static files: {e}")

    def validate_monitoring_systems(self):
        """Validate monitoring and error tracking systems"""
        print("\n🛡️ Validating monitoring systems...")
        
        try:
            monitoring_status = self.driver.execute_script("""
                return {
                    safeErrorHandler: {
                        loaded: typeof window.SafeErrorHandler !== 'undefined',
                        initialized: window.SafeErrorHandler && window.SafeErrorHandler.isInitialized,
                        errorCount: window.SafeErrorHandler ? window.SafeErrorHandler.errors.length : 0
                    },
                    safeDependencyManager: {
                        loaded: typeof window.SafeDependencyManager !== 'undefined',
                        initialized: window.SafeDependencyManager && window.SafeDependencyManager.isInitialized,
                        loadedScripts: window.SafeDependencyManager ? window.SafeDependencyManager.getStatus().loaded.length : 0
                    },
                    staticFileMonitor: {
                        available: typeof window.staticFileHealthCheck !== 'undefined'
                    },
                    errorTracking: {
                        available: typeof window.ErrorTracker !== 'undefined'
                    },
                    performanceOptimizer: {
                        available: typeof window.PerformanceOptimizer !== 'undefined'
                    }
                };
            """)
            
            self.results['monitoring_systems'] = monitoring_status
            
            # Evaluate monitoring systems
            systems_active = 0
            total_systems = 5
            
            if monitoring_status['safeErrorHandler']['loaded']:
                print("✅ SafeErrorHandler loaded")
                systems_active += 1
            else:
                print("❌ SafeErrorHandler not loaded")
            
            if monitoring_status['safeDependencyManager']['loaded']:
                print("✅ SafeDependencyManager loaded")
                systems_active += 1
            else:
                print("❌ SafeDependencyManager not loaded")
            
            if monitoring_status['staticFileMonitor']['available']:
                print("✅ Static File Monitor available")
                systems_active += 1
            else:
                print("❌ Static File Monitor not available")
            
            if monitoring_status['errorTracking']['available']:
                print("✅ Error Tracking available")
                systems_active += 1
            else:
                print("❌ Error Tracking not available")
            
            if monitoring_status['performanceOptimizer']['available']:
                print("✅ Performance Optimizer available")
                systems_active += 1
            else:
                print("❌ Performance Optimizer not available")
            
            monitoring_score = (systems_active / total_systems) * 100
            print(f"\n📊 Monitoring Systems Score: {monitoring_score:.1f}% ({systems_active}/{total_systems})")
            
            self.results['monitoring_systems']['score'] = monitoring_score
            
        except Exception as e:
            print(f"❌ Failed to validate monitoring systems: {e}")

    def check_optimization_status(self):
        """Check optimization implementations"""
        print("\n⚡ Checking optimization status...")
        
        try:
            optimization_checks = self.driver.execute_script("""
                return {
                    lazyLoading: {
                        images: document.querySelectorAll('img[loading="lazy"]').length,
                        totalImages: document.querySelectorAll('img').length
                    },
                    criticalCSS: {
                        inlineStyles: document.querySelectorAll('style').length,
                        externalCSS: document.querySelectorAll('link[rel="stylesheet"]').length
                    },
                    resourceHints: {
                        preload: document.querySelectorAll('link[rel="preload"]').length,
                        prefetch: document.querySelectorAll('link[rel="prefetch"]').length,
                        preconnect: document.querySelectorAll('link[rel="preconnect"]').length
                    },
                    compression: {
                        gzipSupported: 'gzip' in (navigator.userAgent || ''),
                        brotliSupported: 'br' in (navigator.userAgent || '')
                    }
                };
            """)
            
            self.results['optimization_status'] = optimization_checks
            
            # Evaluate optimizations
            optimizations = []
            
            lazy_ratio = optimization_checks['lazyLoading']['images'] / max(optimization_checks['lazyLoading']['totalImages'], 1)
            if lazy_ratio > 0.5:
                optimizations.append("Lazy loading implemented")
                print("✅ Lazy loading implemented for images")
            else:
                print("⚠️ Consider implementing lazy loading for images")
                self.results['recommendations'].append("Implement lazy loading for images")
            
            if optimization_checks['criticalCSS']['inlineStyles'] > 0:
                optimizations.append("Critical CSS inlined")
                print("✅ Critical CSS appears to be inlined")
            else:
                print("⚠️ Consider inlining critical CSS")
                self.results['recommendations'].append("Consider inlining critical CSS")
            
            resource_hints = sum(optimization_checks['resourceHints'].values())
            if resource_hints > 0:
                optimizations.append("Resource hints implemented")
                print(f"✅ Resource hints implemented ({resource_hints} hints)")
            else:
                print("⚠️ Consider adding resource hints (preload, prefetch)")
                self.results['recommendations'].append("Add resource hints for better performance")
            
            optimization_score = len(optimizations) / 3 * 100
            print(f"\n📊 Optimization Score: {optimization_score:.1f}%")
            
            self.results['optimization_status']['score'] = optimization_score
            
        except Exception as e:
            print(f"❌ Failed to check optimization status: {e}")

    def test_error_tracking(self):
        """Test error tracking functionality"""
        print("\n🧪 Testing error tracking...")
        
        try:
            # Trigger a test error and see if it's caught
            error_caught = self.driver.execute_script("""
                let errorCaught = false;
                
                // Store original error count
                const originalErrorCount = window.SafeErrorHandler ? window.SafeErrorHandler.errors.length : 0;
                
                // Trigger a test error
                try {
                    throw new Error('Test error for monitoring validation');
                } catch (e) {
                    // Error should be caught by global handler
                }
                
                // Check if error was caught
                setTimeout(() => {
                    const newErrorCount = window.SafeErrorHandler ? window.SafeErrorHandler.errors.length : 0;
                    errorCaught = newErrorCount > originalErrorCount;
                }, 100);
                
                return new Promise(resolve => {
                    setTimeout(() => {
                        const newErrorCount = window.SafeErrorHandler ? window.SafeErrorHandler.errors.length : 0;
                        resolve({
                            errorCaught: newErrorCount > originalErrorCount,
                            originalCount: originalErrorCount,
                            newCount: newErrorCount
                        });
                    }, 500);
                });
            """)
            
            if error_caught['errorCaught']:
                print("✅ Error tracking is working")
                self.results['error_tracking']['working'] = True
            else:
                print("⚠️ Error tracking may not be working properly")
                self.results['error_tracking']['working'] = False
            
            self.results['error_tracking']['test_result'] = error_caught
            
        except Exception as e:
            print(f"❌ Failed to test error tracking: {e}")
            self.results['error_tracking']['working'] = False

    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n📋 Generating performance report...")
        
        # Calculate overall score
        scores = []
        
        if 'performance_score' in self.results['core_web_vitals']:
            scores.append(self.results['core_web_vitals']['performance_score'])
        
        if 'score' in self.results['monitoring_systems']:
            scores.append(self.results['monitoring_systems']['score'])
        
        if 'score' in self.results['optimization_status']:
            scores.append(self.results['optimization_status']['score'])
        
        self.results['overall_score'] = sum(scores) / len(scores) if scores else 0
        
        # Generate recommendations based on results
        if self.results['overall_score'] < 70:
            self.results['recommendations'].append("Overall performance needs improvement")
        
        if 'total_size_kb' in self.results['static_file_performance']:
            if self.results['static_file_performance']['total_size_kb'] > 1024:
                self.results['recommendations'].append("Reduce static file bundle size")
        
        # Save detailed report
        report_data = {
            'timestamp': time.time(),
            'url': self.base_url,
            'results': self.results
        }
        
        with open('performance_monitoring_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"💾 Performance report saved to: performance_monitoring_report.json")

    def run_monitoring(self):
        """Run complete performance monitoring"""
        print("⚡ Starting Performance Monitoring and Optimization Verification")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all monitoring tests
        self.measure_core_web_vitals()
        self.analyze_static_file_performance()
        self.validate_monitoring_systems()
        self.check_optimization_status()
        self.test_error_tracking()
        self.generate_performance_report()
        
        # Print final results
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE MONITORING RESULTS")
        print("=" * 70)
        
        print(f"🎯 Overall Performance Score: {self.results['overall_score']:.1f}%")
        
        if 'performance_score' in self.results['core_web_vitals']:
            print(f"📈 Core Web Vitals Score: {self.results['core_web_vitals']['performance_score']:.1f}%")
        
        if 'score' in self.results['monitoring_systems']:
            print(f"🛡️ Monitoring Systems Score: {self.results['monitoring_systems']['score']:.1f}%")
        
        if 'score' in self.results['optimization_status']:
            print(f"⚡ Optimization Score: {self.results['optimization_status']['score']:.1f}%")
        
        if self.results['recommendations']:
            print(f"\n💡 Recommendations ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n⏱️ Total monitoring time: {time.time() - start_time:.1f}s")
        
        return self.results['overall_score'] >= 70  # 70% threshold for success

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor performance and optimization')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL to monitor')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(base_url=args.url, headless=args.headless)
    
    try:
        success = monitor.run_monitoring()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Monitoring failed with error: {e}")
        sys.exit(1)
    finally:
        monitor.cleanup()

if __name__ == '__main__':
    main()