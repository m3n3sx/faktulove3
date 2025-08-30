/**
 * Core Web Vitals monitoring for design system performance tracking
 * Tracks LCP, FID, CLS, and other performance metrics
 */

interface WebVitalMetric {
  name: string;
  value: number;
  delta: number;
  id: string;
  navigationType: string;
}

interface PerformanceData {
  timestamp: number;
  url: string;
  userAgent: string;
  connectionType?: string;
  metrics: {
    lcp?: number;
    fid?: number;
    cls?: number;
    fcp?: number;
    ttfb?: number;
  };
  designSystemMetrics: {
    componentRenderTime: number;
    bundleSize: number;
    cssLoadTime: number;
    themeLoadTime: number;
  };
}

class CoreWebVitalsMonitor {
  private metrics: Map<string, number> = new Map();
  private observers: PerformanceObserver[] = [];
  private reportingEndpoint: string;

  constructor(reportingEndpoint: string = '/api/performance-metrics/') {
    this.reportingEndpoint = reportingEndpoint;
    this.initializeObservers();
  }

  private initializeObservers(): void {
    // Largest Contentful Paint (LCP)
    this.observeLCP();
    
    // First Input Delay (FID)
    this.observeFID();
    
    // Cumulative Layout Shift (CLS)
    this.observeCLS();
    
    // First Contentful Paint (FCP)
    this.observeFCP();
    
    // Time to First Byte (TTFB)
    this.observeTTFB();
  }

  private observeLCP(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        this.metrics.set('lcp', lastEntry.startTime);
        this.reportMetric('lcp', lastEntry.startTime);
      });

      observer.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.push(observer);
    }
  }

  private observeFID(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          this.metrics.set('fid', entry.processingStart - entry.startTime);
          this.reportMetric('fid', entry.processingStart - entry.startTime);
        });
      });

      observer.observe({ entryTypes: ['first-input'] });
      this.observers.push(observer);
    }
  }

  private observeCLS(): void {
    if ('PerformanceObserver' in window) {
      let clsValue = 0;
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
            this.metrics.set('cls', clsValue);
          }
        });
      });

      observer.observe({ entryTypes: ['layout-shift'] });
      this.observers.push(observer);
    }
  }

  private observeFCP(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.name === 'first-contentful-paint') {
            this.metrics.set('fcp', entry.startTime);
            this.reportMetric('fcp', entry.startTime);
          }
        });
      });

      observer.observe({ entryTypes: ['paint'] });
      this.observers.push(observer);
    }
  }

  private observeTTFB(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (entry.entryType === 'navigation') {
            const ttfb = entry.responseStart - entry.requestStart;
            this.metrics.set('ttfb', ttfb);
            this.reportMetric('ttfb', ttfb);
          }
        });
      });

      observer.observe({ entryTypes: ['navigation'] });
      this.observers.push(observer);
    }
  }

  private reportMetric(name: string, value: number): void {
    // Report to analytics endpoint
    this.sendToAnalytics({
      metric: name,
      value,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent
    });
  }

  public measureComponentRenderTime(componentName: string, renderFn: () => void): number {
    const startTime = performance.now();
    renderFn();
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    this.reportMetric(`component-render-${componentName}`, renderTime);
    return renderTime;
  }

  public measureBundleSize(): Promise<number> {
    return new Promise((resolve) => {
      if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          let totalSize = 0;
          
          entries.forEach((entry: any) => {
            if (entry.name.includes('design-system') || entry.name.includes('bundle')) {
              totalSize += entry.transferSize || 0;
            }
          });
          
          this.metrics.set('bundleSize', totalSize);
          this.reportMetric('bundleSize', totalSize);
          resolve(totalSize);
        });

        observer.observe({ entryTypes: ['resource'] });
      } else {
        resolve(0);
      }
    });
  }

  public getMetrics(): Map<string, number> {
    return new Map(this.metrics);
  }

  public generateReport(): PerformanceData {
    const connectionType = (navigator as any).connection?.effectiveType || 'unknown';
    
    return {
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      connectionType,
      metrics: {
        lcp: this.metrics.get('lcp'),
        fid: this.metrics.get('fid'),
        cls: this.metrics.get('cls'),
        fcp: this.metrics.get('fcp'),
        ttfb: this.metrics.get('ttfb')
      },
      designSystemMetrics: {
        componentRenderTime: this.metrics.get('avgComponentRender') || 0,
        bundleSize: this.metrics.get('bundleSize') || 0,
        cssLoadTime: this.metrics.get('cssLoadTime') || 0,
        themeLoadTime: this.metrics.get('themeLoadTime') || 0
      }
    };
  }

  private async sendToAnalytics(data: any): Promise<void> {
    try {
      await fetch(this.reportingEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
    } catch (error) {
      console.warn('Failed to send performance metric:', error);
    }
  }

  public cleanup(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
    this.metrics.clear();
  }
}

export { CoreWebVitalsMonitor, type PerformanceData, type WebVitalMetric };