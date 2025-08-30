/**
 * Bundle size and loading performance monitoring
 * Tracks design system bundle impact and optimization opportunities
 */

interface BundleMetrics {
  totalSize: number;
  gzippedSize: number;
  loadTime: number;
  cacheHitRate: number;
  chunkSizes: Record<string, number>;
  unusedCode: number;
}

interface LoadingMetrics {
  initialLoad: number;
  lazyLoadTime: number;
  cachePerformance: number;
  networkLatency: number;
}

class BundleAnalyzer {
  private metrics: BundleMetrics;
  private loadingMetrics: LoadingMetrics;
  private observer: PerformanceObserver | null = null;

  constructor() {
    this.metrics = {
      totalSize: 0,
      gzippedSize: 0,
      loadTime: 0,
      cacheHitRate: 0,
      chunkSizes: {},
      unusedCode: 0
    };

    this.loadingMetrics = {
      initialLoad: 0,
      lazyLoadTime: 0,
      cachePerformance: 0,
      networkLatency: 0
    };

    this.initializeMonitoring();
  }

  private initializeMonitoring(): void {
    if ('PerformanceObserver' in window) {
      this.observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        this.analyzeResourceEntries(entries);
      });

      this.observer.observe({ entryTypes: ['resource', 'navigation'] });
    }

    // Monitor bundle loading on page load
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.analyzeBundleLoad());
    } else {
      this.analyzeBundleLoad();
    }
  }

  private analyzeResourceEntries(entries: PerformanceEntry[]): void {
    entries.forEach((entry: any) => {
      if (this.isDesignSystemResource(entry.name)) {
        this.trackResourceMetrics(entry);
      }
    });
  }

  private isDesignSystemResource(url: string): boolean {
    return url.includes('design-system') || 
           url.includes('ds-') || 
           url.includes('components') ||
           url.includes('theme');
  }

  private trackResourceMetrics(entry: any): void {
    const size = entry.transferSize || entry.encodedBodySize || 0;
    const loadTime = entry.responseEnd - entry.startTime;
    const fromCache = entry.transferSize === 0 && entry.decodedBodySize > 0;

    // Update total metrics
    this.metrics.totalSize += size;
    this.metrics.loadTime = Math.max(this.metrics.loadTime, loadTime);

    // Track chunk sizes
    const chunkName = this.extractChunkName(entry.name);
    if (chunkName) {
      this.metrics.chunkSizes[chunkName] = size;
    }

    // Update cache hit rate
    if (fromCache) {
      this.metrics.cacheHitRate += 1;
    }

    // Track loading performance
    this.loadingMetrics.networkLatency = entry.responseStart - entry.requestStart;
  }

  private extractChunkName(url: string): string | null {
    const match = url.match(/\/([^\/]+)\.(js|css)$/);
    return match ? match[1] : null;
  }

  private async analyzeBundleLoad(): Promise<void> {
    const startTime = performance.now();
    
    try {
      // Analyze initial bundle load
      await this.measureInitialLoad();
      
      // Check for unused code
      await this.detectUnusedCode();
      
      // Measure lazy loading performance
      await this.measureLazyLoading();
      
    } catch (error) {
      console.warn('Bundle analysis failed:', error);
    }

    const endTime = performance.now();
    this.loadingMetrics.initialLoad = endTime - startTime;
  }

  private async measureInitialLoad(): Promise<void> {
    return new Promise((resolve) => {
      const scripts = document.querySelectorAll('script[src*="design-system"]');
      const styles = document.querySelectorAll('link[href*="design-system"]');
      
      let loadedCount = 0;
      const totalResources = scripts.length + styles.length;

      if (totalResources === 0) {
        resolve();
        return;
      }

      const onLoad = () => {
        loadedCount++;
        if (loadedCount === totalResources) {
          resolve();
        }
      };

      scripts.forEach(script => {
        if (script.complete) {
          onLoad();
        } else {
          script.addEventListener('load', onLoad);
        }
      });

      styles.forEach(link => {
        if ((link as HTMLLinkElement).sheet) {
          onLoad();
        } else {
          link.addEventListener('load', onLoad);
        }
      });
    });
  }

  private async detectUnusedCode(): Promise<void> {
    if ('CSS' in window && 'supports' in (window as any).CSS) {
      try {
        // Use Coverage API if available (Chrome DevTools)
        if ('coverage' in window) {
          const coverage = (window as any).coverage;
          const result = await coverage.startJSCoverage();
          
          // Calculate unused code percentage
          let totalBytes = 0;
          let usedBytes = 0;
          
          result.forEach((entry: any) => {
            if (this.isDesignSystemResource(entry.url)) {
              totalBytes += entry.text.length;
              entry.ranges.forEach((range: any) => {
                usedBytes += range.end - range.start;
              });
            }
          });
          
          this.metrics.unusedCode = totalBytes > 0 ? 
            ((totalBytes - usedBytes) / totalBytes) * 100 : 0;
        }
      } catch (error) {
        console.warn('Code coverage analysis failed:', error);
      }
    }
  }

  private async measureLazyLoading(): Promise<void> {
    const startTime = performance.now();
    
    // Simulate lazy loading measurement
    const lazyComponents = document.querySelectorAll('[data-lazy-component]');
    
    if (lazyComponents.length > 0) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const loadTime = performance.now() - startTime;
            this.loadingMetrics.lazyLoadTime = Math.max(
              this.loadingMetrics.lazyLoadTime, 
              loadTime
            );
          }
        });
      });

      lazyComponents.forEach(component => observer.observe(component));
    }
  }

  public getBundleMetrics(): BundleMetrics {
    return { ...this.metrics };
  }

  public getLoadingMetrics(): LoadingMetrics {
    return { ...this.loadingMetrics };
  }

  public generateOptimizationReport(): {
    recommendations: string[];
    metrics: BundleMetrics & LoadingMetrics;
    score: number;
  } {
    const recommendations: string[] = [];
    let score = 100;

    // Check bundle size
    if (this.metrics.totalSize > 500000) { // 500KB
      recommendations.push('Bundle size exceeds 500KB - consider code splitting');
      score -= 20;
    }

    // Check unused code
    if (this.metrics.unusedCode > 30) {
      recommendations.push(`${this.metrics.unusedCode.toFixed(1)}% unused code detected - implement tree shaking`);
      score -= 15;
    }

    // Check cache performance
    if (this.metrics.cacheHitRate < 0.8) {
      recommendations.push('Low cache hit rate - optimize caching strategy');
      score -= 10;
    }

    // Check loading performance
    if (this.loadingMetrics.initialLoad > 3000) { // 3 seconds
      recommendations.push('Slow initial load time - optimize critical path');
      score -= 25;
    }

    if (this.loadingMetrics.lazyLoadTime > 1000) { // 1 second
      recommendations.push('Slow lazy loading - optimize component loading');
      score -= 10;
    }

    return {
      recommendations,
      metrics: { ...this.metrics, ...this.loadingMetrics },
      score: Math.max(0, score)
    };
  }

  public trackChunkLoad(chunkName: string): Promise<number> {
    return new Promise((resolve) => {
      const startTime = performance.now();
      
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const chunkEntry = entries.find(entry => 
          entry.name.includes(chunkName)
        );
        
        if (chunkEntry) {
          const loadTime = chunkEntry.responseEnd - chunkEntry.startTime;
          resolve(loadTime);
          observer.disconnect();
        }
      });

      observer.observe({ entryTypes: ['resource'] });
      
      // Timeout after 10 seconds
      setTimeout(() => {
        observer.disconnect();
        resolve(performance.now() - startTime);
      }, 10000);
    });
  }

  public cleanup(): void {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }
}

export { BundleAnalyzer, type BundleMetrics, type LoadingMetrics };