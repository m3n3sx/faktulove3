/**
 * Design System Optimization Module
 * Exports all optimization-related functionality
 */

export { ProductionMetricsAnalyzer, type OptimizationRecommendation, type BottleneckAnalysis, type UserBehaviorInsights } from './ProductionMetricsAnalyzer';
export { ComponentPerformanceOptimizer, type ComponentOptimization, type OptimizationConfig } from './ComponentPerformanceOptimizer';
export { DocumentationUpdater, type DocumentationUpdate, type UsagePattern, type DocumentationGap } from './DocumentationUpdater';
export { OptimizationOrchestrator, type OptimizationSession } from './OptimizationOrchestrator';

// Re-export monitoring components for convenience
export { PerformanceMonitor } from '../monitoring/PerformanceMonitor';
export { ComponentUsageTracker } from '../monitoring/ComponentUsageTracker';
export { IntegrationHealthMonitor } from '../monitoring/IntegrationHealthMonitor';

/**
 * Quick start function for running optimization analysis
 */
export async function runOptimizationAnalysis(): Promise<{
  recommendations: OptimizationRecommendation[];
  componentOptimizations: ComponentOptimization[];
  documentationUpdates: DocumentationUpdate[];
}> {
  const { ProductionMetricsAnalyzer } = await import('./ProductionMetricsAnalyzer');
  const { ComponentPerformanceOptimizer } = await import('./ComponentPerformanceOptimizer');
  const { DocumentationUpdater } = await import('./DocumentationUpdater');

  const metricsAnalyzer = new ProductionMetricsAnalyzer();
  const performanceOptimizer = new ComponentPerformanceOptimizer();
  const documentationUpdater = new DocumentationUpdater();

  try {
    // Run analysis
    const analysis = await metricsAnalyzer.analyzeProductionMetrics();
    const componentOptimizations = await performanceOptimizer.optimizeComponents();
    const docAnalysis = await documentationUpdater.analyzeDocumentationNeeds();

    return {
      recommendations: analysis.recommendations,
      componentOptimizations,
      documentationUpdates: docAnalysis.updates
    };
  } finally {
    // Cleanup
    metricsAnalyzer.cleanup();
    performanceOptimizer.cleanup();
    documentationUpdater.cleanup();
  }
}

/**
 * Start automated optimization monitoring
 */
export async function startOptimizationMonitoring(config?: Partial<OptimizationConfig>): Promise<OptimizationOrchestrator> {
  const { OptimizationOrchestrator } = await import('./OptimizationOrchestrator');
  
  const orchestrator = new OptimizationOrchestrator(config);
  orchestrator.scheduleAutomaticOptimization();
  
  return orchestrator;
}

/**
 * Generate comprehensive optimization report
 */
export async function generateOptimizationReport(): Promise<string> {
  const { OptimizationOrchestrator } = await import('./OptimizationOrchestrator');
  
  const orchestrator = new OptimizationOrchestrator();
  return await orchestrator.generateOptimizationReport();
}

// Type exports for external use
export type { OptimizationConfig } from './ComponentPerformanceOptimizer';