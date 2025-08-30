/**
 * React hook for integrating performance monitoring with design system components
 */

import { useEffect, useRef, useCallback } from 'react';
import { getPerformanceMonitor } from '../monitoring/PerformanceMonitor';

interface UsePerformanceMonitoringOptions {
  componentName?: string;
  trackRenders?: boolean;
  trackInteractions?: boolean;
  reportingInterval?: number;
}

export function usePerformanceMonitoring(options: UsePerformanceMonitoringOptions = {}) {
  const {
    componentName,
    trackRenders = true,
    trackInteractions = true,
    reportingInterval = 60000
  } = options;

  const monitor = useRef(getPerformanceMonitor({
    reportingInterval,
    enableWebVitals: true,
    enableBundleAnalysis: true,
    enableComponentTracking: trackRenders,
    enableUXTracking: trackInteractions
  }));

  const renderStartTime = useRef<number>(0);

  // Start monitoring on mount
  useEffect(() => {
    monitor.current.startMonitoring();
    
    return () => {
      monitor.current.stopMonitoring();
    };
  }, []);

  // Track component renders
  useEffect(() => {
    if (trackRenders && componentName) {
      renderStartTime.current = performance.now();
      
      return () => {
        const renderTime = performance.now() - renderStartTime.current;
        monitor.current.trackComponentRender(componentName, () => {});
      };
    }
  });

  // Callback to manually track task completion
  const trackTaskCompletion = useCallback((taskName: string, duration: number, success: boolean) => {
    monitor.current.recordTaskCompletion(taskName, duration, success);
  }, []);

  // Callback to record user feedback
  const recordFeedback = useCallback((sentiment: 'positive' | 'negative' | 'neutral') => {
    monitor.current.recordUserFeedback(sentiment);
  }, []);

  // Callback to check accessibility
  const checkAccessibility = useCallback(async () => {
    await monitor.current.checkAccessibility();
  }, []);

  // Callback to generate performance report
  const generateReport = useCallback(async () => {
    return await monitor.current.generateReport();
  }, []);

  return {
    trackTaskCompletion,
    recordFeedback,
    checkAccessibility,
    generateReport,
    monitor: monitor.current
  };
}

/**
 * Higher-order component for automatic performance tracking
 */
export function withPerformanceTracking<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName: string
) {
  return function PerformanceTrackedComponent(props: P) {
    const { trackTaskCompletion } = usePerformanceMonitoring({
      componentName,
      trackRenders: true,
      trackInteractions: true
    });

    return <WrappedComponent {...props} />;
  };
}

/**
 * Hook for tracking specific user interactions
 */
export function useInteractionTracking() {
  const monitor = useRef(getPerformanceMonitor());

  const trackClick = useCallback((elementName: string) => {
    // Track click interactions
    const startTime = performance.now();
    
    return () => {
      const duration = performance.now() - startTime;
      monitor.current.recordTaskCompletion(`click-${elementName}`, duration, true);
    };
  }, []);

  const trackFormSubmission = useCallback((formName: string, success: boolean, errors?: string[]) => {
    monitor.current.recordTaskCompletion(`form-${formName}`, 0, success);
    
    if (!success && errors) {
      // Record form errors for UX analysis
      console.warn(`Form submission failed for ${formName}:`, errors);
    }
  }, []);

  const trackNavigation = useCallback((fromPage: string, toPage: string) => {
    const startTime = performance.now();
    
    return () => {
      const duration = performance.now() - startTime;
      monitor.current.recordTaskCompletion(`navigation-${fromPage}-to-${toPage}`, duration, true);
    };
  }, []);

  return {
    trackClick,
    trackFormSubmission,
    trackNavigation
  };
}