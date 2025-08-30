/**
 * Main performance monitoring system that integrates all monitoring components
 * Provides unified interface for tracking design system performance
 */

import { CoreWebVitalsMonitor, type PerformanceData } from './CoreWebVitals';
import { BundleAnalyzer, type BundleMetrics } from './BundleAnalyzer';
import { ComponentPerformanceTracker, type ComponentMetrics } from './ComponentPerformanceTracker';
import { UserExperienceMetrics, type AccessibilityMetrics } from './UserExperienceMetrics';

interface PerformanceReport {
  timestamp: number;
  webVitals: PerformanceData;
  bundle: BundleMetrics;
  components: ComponentMetrics[];
  userExperience: {
    accessibility: AccessibilityMetrics;
    satisfaction: any;
    interactions: any[];
  };
  recommendations: string[];
  overallScore: number;
}

interface MonitoringConfig {
  enableWebVitals: boolean;
  enableBundleAnalysis: boolean;
  enableComponentTracking: boolean;
  enableUXTracking: boolean;
  reportingInterval: number;
  reportingEndpoint: string;
}

class PerformanceMonitor {
  private webVitalsMonitor: CoreWebVitalsMonitor;
  private bundleAnalyzer: BundleAnalyzer;
  private componentTracker: ComponentPerformanceTracker;
  private uxMetrics: UserExperienceMetrics;
  private config: MonitoringConfig;
  private reportingTimer: NodeJS.Timeout | null = null;

  constructor(config: Partial<MonitoringConfig> = {}) {
    this.config = {
      enableWebVitals: true,
      enableBundleAnalysis: true,
      enableComponentTracking: true,
      enableUXTracking: true,
      reportingInterval: 60000, // 1 minute
      reportingEndpoint: '/api/performance-metrics/',
      ...config
    };

    this.initializeMonitors();
  }

  private initializeMonitors(): void {
    if (this.config.enableWebVitals) {
      this.webVitalsMonitor = new CoreWebVitalsMonitor(this.config.reportingEndpoint);
    }

    if (this.config.enableBundleAnalysis) {
      this.bundleAnalyzer = new BundleAnalyzer();
    }

    if (this.config.enableComponentTracking) {
      this.componentTracker = ComponentPerformanceTracker.getInstance();
    }

    if (this.config.enableUXTracking) {
      this.uxMetrics = new UserExperienceMetrics();
      this.uxMetrics.startTracking();
    }
  }

  public startMonitoring(): void {
    console.log('Starting design system performance monitoring...');

    // Start periodic reporting
    if (this.config.reportingInterval > 0) {
      this.reportingTimer = setInterval(() => {
        this.generateAndSendReport();
      }, this.config.reportingInterval);
    }

    // Monitor page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pauseMonitoring();
      } else {
        this.resumeMonitoring();
      }
    });

    // Monitor page unload
    window.addEventListener('beforeunload', () => {
      this.generateAndSendReport();
    });
  }

  public stopMonitoring(): void {
    console.log('Stopping design system performance monitoring...');

    if (this.reportingTimer) {
      clearInterval(this.reportingTimer);
      this.reportingTimer = null;
    }

    this.cleanup();
  }

  private pauseMonitoring(): void {
    if (this.uxMetrics) {
      this.uxMetrics.stopTracking();
    }
  }

  private resumeMonitoring(): void {
    if (this.uxMetrics) {
      this.uxMetrics.startTracking();
    }
  }

  public async generateReport(): Promise<PerformanceReport> {
    const timestamp = Date.now();
    
    // Collect data from all monitors
    const webVitals = this.webVitalsMonitor?.generateReport() || {} as PerformanceData;
    const bundle = this.bundleAnalyzer?.getBundleMetrics() || {} as BundleMetrics;
    const components = this.componentTracker?.getComponentMetrics() as ComponentMetrics[] || [];
    const uxData = this.uxMetrics?.getMetrics() || {
      accessibility: {} as AccessibilityMetrics,
      satisfaction: {},
      interactions: []
    };

    // Generate recommendations
    const recommendations = this.generateRecommendations(webVitals, bundle, components, uxData);
    
    // Calculate overall score
    const overallScore = this.calculateOverallScore(webVitals, bundle, components, uxData);

    return {
      timestamp,
      webVitals,
      bundle,
      components,
      userExperience: uxData,
      recommendations,
      overallScore
    };
  }

  private generateRecommendations(
    webVitals: PerformanceData,
    bundle: BundleMetrics,
    components: ComponentMetrics[],
    uxData: any
  ): string[] {
    const recommendations: string[] = [];

    // Web Vitals recommendations
    if (webVitals.metrics?.lcp && webVitals.metrics.lcp > 2500) {
      recommendations.push('LCP exceeds 2.5s - optimize largest contentful paint');
    }

    if (webVitals.metrics?.fid && webVitals.metrics.fid > 100) {
      recommendations.push('FID exceeds 100ms - optimize JavaScript execution');
    }

    if (webVitals.metrics?.cls && webVitals.metrics.cls > 0.1) {
      recommendations.push('CLS exceeds 0.1 - reduce layout shifts');
    }

    // Bundle recommendations
    if (bundle.totalSize > 500000) {
      recommendations.push('Bundle size exceeds 500KB - implement code splitting');
    }

    if (bundle.unusedCode > 30) {
      recommendations.push('High unused code percentage - improve tree shaking');
    }

    // Component recommendations
    const slowComponents = components.filter(c => c.averageRenderTime > 16);
    if (slowComponents.length > 0) {
      recommendations.push(`${slowComponents.length} components exceed 16ms render time`);
    }

    // UX recommendations
    if (uxData.accessibility?.screenReader?.missingLabels > 0) {
      recommendations.push('Missing accessibility labels detected');
    }

    if (uxData.accessibility?.colorContrast?.violations > 0) {
      recommendations.push('Color contrast violations found');
    }

    return recommendations;
  }

  private calculateOverallScore(
    webVitals: PerformanceData,
    bundle: BundleMetrics,
    components: ComponentMetrics[],
    uxData: any
  ): number {
    let score = 100;

    // Web Vitals scoring (40% weight)
    let webVitalsScore = 100;
    if (webVitals.metrics?.lcp) {
      if (webVitals.metrics.lcp > 4000) webVitalsScore -= 30;
      else if (webVitals.metrics.lcp > 2500) webVitalsScore -= 15;
    }
    
    if (webVitals.metrics?.fid) {
      if (webVitals.metrics.fid > 300) webVitalsScore -= 25;
      else if (webVitals.metrics.fid > 100) webVitalsScore -= 10;
    }
    
    if (webVitals.metrics?.cls) {
      if (webVitals.metrics.cls > 0.25) webVitalsScore -= 20;
      else if (webVitals.metrics.cls > 0.1) webVitalsScore -= 10;
    }

    // Bundle scoring (20% weight)
    let bundleScore = 100;
    if (bundle.totalSize > 1000000) bundleScore -= 40;
    else if (bundle.totalSize > 500000) bundleScore -= 20;
    
    if (bundle.unusedCode > 50) bundleScore -= 30;
    else if (bundle.unusedCode > 30) bundleScore -= 15;

    // Component scoring (20% weight)
    let componentScore = 100;
    const slowComponents = components.filter(c => c.averageRenderTime > 16);
    if (slowComponents.length > 0) {
      componentScore -= Math.min(40, slowComponents.length * 5);
    }

    // UX scoring (20% weight)
    let uxScore = 100;
    if (uxData.accessibility?.screenReader?.missingLabels > 0) {
      uxScore -= 25;
    }
    if (uxData.accessibility?.colorContrast?.violations > 0) {
      uxScore -= 20;
    }

    // Calculate weighted average
    score = (webVitalsScore * 0.4) + (bundleScore * 0.2) + (componentScore * 0.2) + (uxScore * 0.2);
    
    return Math.max(0, Math.round(score));
  }

  private async generateAndSendReport(): Promise<void> {
    try {
      const report = await this.generateReport();
      await this.sendReport(report);
    } catch (error) {
      console.error('Failed to generate or send performance report:', error);
    }
  }

  private async sendReport(report: PerformanceReport): Promise<void> {
    try {
      await fetch(this.config.reportingEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(report),
      });
    } catch (error) {
      console.warn('Failed to send performance report:', error);
    }
  }

  public trackComponentRender(componentName: string, renderFn: () => void): number {
    if (this.componentTracker) {
      const endTracking = this.componentTracker.startTracking(componentName);
      renderFn();
      return endTracking();
    }
    
    renderFn();
    return 0;
  }

  public recordTaskCompletion(taskName: string, duration: number, success: boolean): void {
    if (this.uxMetrics) {
      this.uxMetrics.recordTaskCompletion(taskName, duration, success);
    }
  }

  public recordUserFeedback(sentiment: 'positive' | 'negative' | 'neutral'): void {
    if (this.uxMetrics) {
      this.uxMetrics.recordUserFeedback(sentiment);
    }
  }

  public async checkAccessibility(): Promise<void> {
    if (this.uxMetrics) {
      await this.uxMetrics.checkColorContrast();
    }
  }

  private cleanup(): void {
    this.webVitalsMonitor?.cleanup();
    this.bundleAnalyzer?.cleanup();
    this.uxMetrics?.cleanup();
  }
}

// Singleton instance for global access
let monitorInstance: PerformanceMonitor | null = null;

export function getPerformanceMonitor(config?: Partial<MonitoringConfig>): PerformanceMonitor {
  if (!monitorInstance) {
    monitorInstance = new PerformanceMonitor(config);
  }
  return monitorInstance;
}

export { PerformanceMonitor, type PerformanceReport, type MonitoringConfig };