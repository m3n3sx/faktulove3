/**
 * Component render performance tracking for design system components
 * Monitors render times, re-render frequency, and performance bottlenecks
 */

interface ComponentMetrics {
  name: string;
  renderCount: number;
  totalRenderTime: number;
  averageRenderTime: number;
  maxRenderTime: number;
  minRenderTime: number;
  lastRenderTime: number;
  propsChanges: number;
  memoryUsage: number;
}

interface RenderProfile {
  componentName: string;
  renderTime: number;
  timestamp: number;
  propsHash: string;
  stackTrace?: string;
}

class ComponentPerformanceTracker {
  private metrics: Map<string, ComponentMetrics> = new Map();
  private renderProfiles: RenderProfile[] = [];
  private isProfilingEnabled: boolean = false;
  private maxProfileHistory: number = 1000;

  constructor(enableProfiling: boolean = false) {
    this.isProfilingEnabled = enableProfiling;
    this.initializeProfiler();
  }

  private initializeProfiler(): void {
    if (this.isProfilingEnabled && 'performance' in window) {
      // Hook into React DevTools Profiler if available
      this.setupReactProfiler();
    }
  }

  private setupReactProfiler(): void {
    // This would integrate with React DevTools Profiler API
    // For now, we'll use manual tracking
    if (typeof window !== 'undefined' && (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__) {
      const hook = (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__;
      
      if (hook.onCommitFiberRoot) {
        const originalOnCommit = hook.onCommitFiberRoot;
        hook.onCommitFiberRoot = (id: any, root: any, priorityLevel: any) => {
          this.trackReactCommit(root);
          return originalOnCommit(id, root, priorityLevel);
        };
      }
    }
  }

  private trackReactCommit(root: any): void {
    // Extract component information from React fiber tree
    if (root && root.current) {
      this.traverseFiberTree(root.current);
    }
  }

  private traverseFiberTree(fiber: any): void {
    if (fiber.type && fiber.type.name) {
      const componentName = fiber.type.name;
      if (componentName.startsWith('DS') || componentName.includes('DesignSystem')) {
        // This is a design system component
        this.recordRender(componentName, 0); // We'd need actual render time here
      }
    }

    // Traverse children
    let child = fiber.child;
    while (child) {
      this.traverseFiberTree(child);
      child = child.sibling;
    }
  }

  public startTracking(componentName: string): () => number {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      this.recordRender(componentName, renderTime);
      return renderTime;
    };
  }

  public recordRender(
    componentName: string, 
    renderTime: number, 
    propsHash?: string
  ): void {
    const existing = this.metrics.get(componentName);
    
    if (existing) {
      existing.renderCount++;
      existing.totalRenderTime += renderTime;
      existing.averageRenderTime = existing.totalRenderTime / existing.renderCount;
      existing.maxRenderTime = Math.max(existing.maxRenderTime, renderTime);
      existing.minRenderTime = Math.min(existing.minRenderTime, renderTime);
      existing.lastRenderTime = renderTime;
      
      if (propsHash && propsHash !== this.getLastPropsHash(componentName)) {
        existing.propsChanges++;
      }
    } else {
      this.metrics.set(componentName, {
        name: componentName,
        renderCount: 1,
        totalRenderTime: renderTime,
        averageRenderTime: renderTime,
        maxRenderTime: renderTime,
        minRenderTime: renderTime,
        lastRenderTime: renderTime,
        propsChanges: 0,
        memoryUsage: this.estimateMemoryUsage(componentName)
      });
    }

    // Store render profile
    if (this.isProfilingEnabled) {
      this.renderProfiles.push({
        componentName,
        renderTime,
        timestamp: Date.now(),
        propsHash: propsHash || '',
        stackTrace: this.captureStackTrace()
      });

      // Limit profile history
      if (this.renderProfiles.length > this.maxProfileHistory) {
        this.renderProfiles = this.renderProfiles.slice(-this.maxProfileHistory);
      }
    }
  }

  private getLastPropsHash(componentName: string): string {
    const profiles = this.renderProfiles
      .filter(p => p.componentName === componentName)
      .sort((a, b) => b.timestamp - a.timestamp);
    
    return profiles.length > 1 ? profiles[1].propsHash : '';
  }

  private estimateMemoryUsage(componentName: string): number {
    // Rough estimation based on component complexity
    const baseSize = 1024; // 1KB base
    const complexityMultiplier = componentName.length * 10;
    return baseSize + complexityMultiplier;
  }

  private captureStackTrace(): string {
    if (this.isProfilingEnabled) {
      try {
        throw new Error();
      } catch (e) {
        return (e as Error).stack || '';
      }
    }
    return '';
  }

  public getComponentMetrics(componentName?: string): ComponentMetrics | ComponentMetrics[] {
    if (componentName) {
      return this.metrics.get(componentName) || this.createEmptyMetrics(componentName);
    }
    
    return Array.from(this.metrics.values());
  }

  private createEmptyMetrics(componentName: string): ComponentMetrics {
    return {
      name: componentName,
      renderCount: 0,
      totalRenderTime: 0,
      averageRenderTime: 0,
      maxRenderTime: 0,
      minRenderTime: 0,
      lastRenderTime: 0,
      propsChanges: 0,
      memoryUsage: 0
    };
  }

  public getSlowComponents(threshold: number = 16): ComponentMetrics[] {
    return Array.from(this.metrics.values())
      .filter(metric => metric.averageRenderTime > threshold)
      .sort((a, b) => b.averageRenderTime - a.averageRenderTime);
  }

  public getFrequentlyRerenderedComponents(threshold: number = 10): ComponentMetrics[] {
    return Array.from(this.metrics.values())
      .filter(metric => metric.renderCount > threshold)
      .sort((a, b) => b.renderCount - a.renderCount);
  }

  public generatePerformanceReport(): {
    summary: {
      totalComponents: number;
      averageRenderTime: number;
      slowComponents: number;
      frequentRerenders: number;
    };
    recommendations: string[];
    topIssues: ComponentMetrics[];
  } {
    const allMetrics = Array.from(this.metrics.values());
    const totalComponents = allMetrics.length;
    const averageRenderTime = totalComponents > 0 
      ? allMetrics.reduce((sum, m) => sum + m.averageRenderTime, 0) / totalComponents 
      : 0;
    
    const slowComponents = this.getSlowComponents(16);
    const frequentRerenders = this.getFrequentlyRerenderedComponents(10);
    
    const recommendations: string[] = [];
    
    if (slowComponents.length > 0) {
      recommendations.push(`${slowComponents.length} components exceed 16ms render time - consider optimization`);
    }
    
    if (frequentRerenders.length > 0) {
      recommendations.push(`${frequentRerenders.length} components re-render frequently - check prop stability`);
    }
    
    if (averageRenderTime > 10) {
      recommendations.push('Overall render performance is slow - consider React.memo and useMemo');
    }

    const topIssues = [...slowComponents, ...frequentRerenders]
      .sort((a, b) => (b.averageRenderTime * b.renderCount) - (a.averageRenderTime * a.renderCount))
      .slice(0, 5);

    return {
      summary: {
        totalComponents,
        averageRenderTime,
        slowComponents: slowComponents.length,
        frequentRerenders: frequentRerenders.length
      },
      recommendations,
      topIssues
    };
  }

  public exportProfiles(): RenderProfile[] {
    return [...this.renderProfiles];
  }

  public clearMetrics(): void {
    this.metrics.clear();
    this.renderProfiles = [];
  }

  public enableProfiling(enable: boolean = true): void {
    this.isProfilingEnabled = enable;
    if (enable) {
      this.setupReactProfiler();
    }
  }
}

// React Hook for component performance tracking
export function usePerformanceTracking(componentName: string) {
  const tracker = ComponentPerformanceTracker.getInstance();
  
  React.useEffect(() => {
    const endTracking = tracker.startTracking(componentName);
    
    return () => {
      endTracking();
    };
  });
}

// Singleton instance
let trackerInstance: ComponentPerformanceTracker | null = null;

ComponentPerformanceTracker.getInstance = function(): ComponentPerformanceTracker {
  if (!trackerInstance) {
    trackerInstance = new ComponentPerformanceTracker(
      process.env.NODE_ENV === 'development'
    );
  }
  return trackerInstance;
};

export { ComponentPerformanceTracker, type ComponentMetrics, type RenderProfile };