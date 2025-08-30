/**
 * Lazy Loading Utilities for Design System Components
 * 
 * Provides utilities for code splitting and lazy loading of design system components
 * to optimize bundle size and improve performance.
 */

import { lazy, ComponentType, LazyExoticComponent } from 'react';

/**
 * Configuration for lazy loading components
 */
export interface LazyLoadConfig {
  /** Delay before loading the component (in ms) */
  delay?: number;
  /** Whether to preload the component on hover */
  preloadOnHover?: boolean;
  /** Whether to preload the component on viewport intersection */
  preloadOnIntersection?: boolean;
  /** Custom loading component */
  fallback?: ComponentType;
  /** Error boundary component */
  errorBoundary?: ComponentType<{ error: Error; retry: () => void }>;
}

/**
 * Enhanced lazy loading wrapper with preloading capabilities
 */
export function createLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  config: LazyLoadConfig = {}
): LazyExoticComponent<T> & { preload: () => Promise<{ default: T }> } {
  const LazyComponent = lazy(importFn);
  
  // Add preload method to the lazy component
  (LazyComponent as any).preload = importFn;
  
  return LazyComponent as LazyExoticComponent<T> & { preload: () => Promise<{ default: T }> };
}

/**
 * Preload a lazy component
 */
export function preloadComponent<T extends ComponentType<any>>(
  lazyComponent: LazyExoticComponent<T> & { preload?: () => Promise<{ default: T }> }
): Promise<{ default: T }> | void {
  if (lazyComponent.preload) {
    return lazyComponent.preload();
  }
}

/**
 * Preload multiple components
 */
export function preloadComponents(
  components: Array<LazyExoticComponent<any> & { preload?: () => Promise<any> }>
): Promise<any[]> {
  const preloadPromises = components
    .map(component => preloadComponent(component))
    .filter(Boolean) as Promise<any>[];
  
  return Promise.all(preloadPromises);
}

/**
 * Hook for preloading components on hover
 */
export function usePreloadOnHover<T extends ComponentType<any>>(
  lazyComponent: LazyExoticComponent<T> & { preload?: () => Promise<{ default: T }> }
) {
  const handleMouseEnter = () => {
    preloadComponent(lazyComponent);
  };
  
  return { onMouseEnter: handleMouseEnter };
}

/**
 * Hook for preloading components on intersection
 */
export function usePreloadOnIntersection<T extends ComponentType<any>>(
  lazyComponent: LazyExoticComponent<T> & { preload?: () => Promise<{ default: T }> },
  options: IntersectionObserverInit = {}
) {
  const ref = React.useRef<HTMLElement>(null);
  
  React.useEffect(() => {
    const element = ref.current;
    if (!element) return;
    
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            preloadComponent(lazyComponent);
            observer.unobserve(element);
          }
        });
      },
      options
    );
    
    observer.observe(element);
    
    return () => {
      observer.unobserve(element);
    };
  }, [lazyComponent]);
  
  return ref;
}

/**
 * Component groups for strategic lazy loading
 */
export const ComponentGroups = {
  // Core components - loaded immediately
  CORE: 'core',
  
  // Layout components - loaded on demand
  LAYOUT: 'layout',
  
  // Form components - loaded when forms are needed
  FORMS: 'forms',
  
  // Business components - loaded for Polish business features
  BUSINESS: 'business',
  
  // Charts and data visualization - loaded when needed
  CHARTS: 'charts',
  
  // Accessibility components - loaded when accessibility features are used
  ACCESSIBILITY: 'accessibility',
  
  // Advanced patterns - loaded on demand
  PATTERNS: 'patterns',
} as const;

export type ComponentGroup = typeof ComponentGroups[keyof typeof ComponentGroups];

/**
 * Component loading strategy configuration
 */
export interface LoadingStrategy {
  /** Components to load immediately */
  immediate: ComponentGroup[];
  
  /** Components to preload on idle */
  preloadOnIdle: ComponentGroup[];
  
  /** Components to load on demand */
  onDemand: ComponentGroup[];
  
  /** Components to preload on user interaction */
  preloadOnInteraction: ComponentGroup[];
}

/**
 * Default loading strategy optimized for Polish business applications
 */
export const defaultLoadingStrategy: LoadingStrategy = {
  immediate: [ComponentGroups.CORE],
  preloadOnIdle: [ComponentGroups.LAYOUT, ComponentGroups.FORMS],
  onDemand: [ComponentGroups.CHARTS, ComponentGroups.PATTERNS],
  preloadOnInteraction: [ComponentGroups.BUSINESS, ComponentGroups.ACCESSIBILITY],
};

/**
 * Preload components based on loading strategy
 */
export function preloadByStrategy(
  strategy: LoadingStrategy = defaultLoadingStrategy
): void {
  // Preload on idle
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      strategy.preloadOnIdle.forEach(group => {
        // Implementation would preload components in each group
        console.log(`Preloading ${group} components on idle`);
      });
    });
  } else {
    // Fallback for browsers without requestIdleCallback
    setTimeout(() => {
      strategy.preloadOnIdle.forEach(group => {
        console.log(`Preloading ${group} components (fallback)`);
      });
    }, 100);
  }
}

/**
 * Bundle splitting configuration for webpack
 */
export const bundleSplittingConfig = {
  // Design system core (tokens, utilities)
  'design-system-core': {
    test: /[\\/]src[\\/]design-system[\\/](tokens|utils|types)[\\/]/,
    name: 'design-system-core',
    priority: 50,
    chunks: 'all' as const,
  },
  
  // Primitive components
  'design-system-primitives': {
    test: /[\\/]src[\\/]design-system[\\/]components[\\/]primitives[\\/]/,
    name: 'design-system-primitives',
    priority: 40,
    chunks: 'all' as const,
  },
  
  // Layout components
  'design-system-layouts': {
    test: /[\\/]src[\\/]design-system[\\/]components[\\/]layouts[\\/]/,
    name: 'design-system-layouts',
    priority: 35,
    chunks: 'all' as const,
  },
  
  // Business components
  'design-system-business': {
    test: /[\\/]src[\\/]design-system[\\/]components[\\/]business[\\/]/,
    name: 'design-system-business',
    priority: 30,
    chunks: 'all' as const,
  },
  
  // Pattern components
  'design-system-patterns': {
    test: /[\\/]src[\\/]design-system[\\/]components[\\/]patterns[\\/]/,
    name: 'design-system-patterns',
    priority: 25,
    chunks: 'all' as const,
  },
  
  // Accessibility components
  'design-system-accessibility': {
    test: /[\\/]src[\\/]design-system[\\/]components[\\/]accessibility[\\/]/,
    name: 'design-system-accessibility',
    priority: 20,
    chunks: 'all' as const,
  },
};

/**
 * Performance monitoring for lazy loaded components
 */
export class LazyLoadingPerformanceMonitor {
  private static instance: LazyLoadingPerformanceMonitor;
  private loadTimes: Map<string, number> = new Map();
  private loadCounts: Map<string, number> = new Map();
  
  static getInstance(): LazyLoadingPerformanceMonitor {
    if (!LazyLoadingPerformanceMonitor.instance) {
      LazyLoadingPerformanceMonitor.instance = new LazyLoadingPerformanceMonitor();
    }
    return LazyLoadingPerformanceMonitor.instance;
  }
  
  recordLoadStart(componentName: string): void {
    this.loadTimes.set(`${componentName}_start`, performance.now());
  }
  
  recordLoadEnd(componentName: string): void {
    const startTime = this.loadTimes.get(`${componentName}_start`);
    if (startTime) {
      const loadTime = performance.now() - startTime;
      this.loadTimes.set(componentName, loadTime);
      
      const currentCount = this.loadCounts.get(componentName) || 0;
      this.loadCounts.set(componentName, currentCount + 1);
      
      // Log performance metrics
      console.log(`Component ${componentName} loaded in ${loadTime.toFixed(2)}ms`);
    }
  }
  
  getMetrics(): { componentName: string; averageLoadTime: number; loadCount: number }[] {
    const metrics: { componentName: string; averageLoadTime: number; loadCount: number }[] = [];
    
    this.loadTimes.forEach((loadTime, componentName) => {
      if (!componentName.endsWith('_start')) {
        const loadCount = this.loadCounts.get(componentName) || 1;
        metrics.push({
          componentName,
          averageLoadTime: loadTime,
          loadCount,
        });
      }
    });
    
    return metrics;
  }
}

// React import for hooks
import React from 'react';