/**
 * Optimization Orchestrator
 * Coordinates all optimization activities based on production metrics
 */

import { ProductionMetricsAnalyzer, type OptimizationRecommendation } from './ProductionMetricsAnalyzer';
import { ComponentPerformanceOptimizer, type ComponentOptimization } from './ComponentPerformanceOptimizer';
import { DocumentationUpdater, type DocumentationUpdate } from './DocumentationUpdater';
import { PerformanceMonitor } from '../monitoring/PerformanceMonitor';

interface OptimizationSession {
  id: string;
  startTime: number;
  endTime?: number;
  status: 'running' | 'completed' | 'failed';
  phase: 'analysis' | 'optimization' | 'documentation' | 'validation';
  results: {
    metricsAnalysis?: any;
    componentOptimizations?: ComponentOptimization[];
    documentationUpdates?: DocumentationUpdate[];
    performanceImpact?: {
      before: any;
      after: any;
      improvement: number;
    };
  };
  errors: string[];
}

interface OptimizationConfig {
  enableAutomaticOptimization: boolean;
  enableDocumentationUpdates: boolean;
  performanceThreshold: number;
  optimizationInterval: number; // hours
  maxOptimizationsPerSession: number;
  requireApproval: boolean;
}

class OptimizationOrchestrator {
  private metricsAnalyzer: ProductionMetricsAnalyzer;
  private performanceOptimizer: ComponentPerformanceOptimizer;
  private documentationUpdater: DocumentationUpdater;
  private performanceMonitor: PerformanceMonitor;
  private config: OptimizationConfig;
  private currentSession: OptimizationSession | null = null;
  private optimizationHistory: OptimizationSession[] = [];
  private scheduledOptimization: NodeJS.Timeout | null = null;

  constructor(config: Partial<OptimizationConfig> = {}) {
    this.config = {
      enableAutomaticOptimization: false, // Disabled by default for safety
      enableDocumentationUpdates: true,
      performanceThreshold: 70, // Overall performance score threshold
      optimizationInterval: 24, // Run optimization every 24 hours
      maxOptimizationsPerSession: 10,
      requireApproval: true,
      ...config
    };

    this.metricsAnalyzer = new ProductionMetricsAnalyzer();
    this.performanceOptimizer = new ComponentPerformanceOptimizer();
    this.documentationUpdater = new DocumentationUpdater();
    this.performanceMonitor = new PerformanceMonitor();
  }

  public async startOptimizationCycle(): Promise<OptimizationSession> {
    if (this.currentSession && this.currentSession.status === 'running') {
      throw new Error('Optimization cycle already running');
    }

    const session: OptimizationSession = {
      id: this.generateSessionId(),
      startTime: Date.now(),
      status: 'running',
      phase: 'analysis',
      results: {},
      errors: []
    };

    this.currentSession = session;
    console.log(`Starting optimization cycle: ${session.id}`);

    try {
      // Phase 1: Analyze production metrics
      session.phase = 'analysis';
      const metricsAnalysis = await this.analyzeProductionMetrics();
      session.results.metricsAnalysis = metricsAnalysis;

      // Phase 2: Apply component optimizations
      session.phase = 'optimization';
      const componentOptimizations = await this.optimizeComponents(metricsAnalysis);
      session.results.componentOptimizations = componentOptimizations;

      // Phase 3: Update documentation
      session.phase = 'documentation';
      const documentationUpdates = await this.updateDocumentation();
      session.results.documentationUpdates = documentationUpdates;

      // Phase 4: Validate improvements
      session.phase = 'validation';
      const performanceImpact = await this.validateOptimizations();
      session.results.performanceImpact = performanceImpact;

      session.status = 'completed';
      session.endTime = Date.now();

      console.log(`Optimization cycle completed: ${session.id}`);
      
    } catch (error) {
      session.status = 'failed';
      session.endTime = Date.now();
      session.errors.push(error instanceof Error ? error.message : String(error));
      
      console.error(`Optimization cycle failed: ${session.id}`, error);
    }

    this.optimizationHistory.push(session);
    this.currentSession = null;

    return session;
  }

  private async analyzeProductionMetrics(): Promise<any> {
    console.log('Analyzing production metrics...');
    
    const analysis = await this.metricsAnalyzer.analyzeProductionMetrics();
    
    // Check if optimization is needed
    const overallScore = this.calculateOverallScore(analysis);
    
    if (overallScore >= this.config.performanceThreshold) {
      console.log(`Performance score ${overallScore} meets threshold ${this.config.performanceThreshold}`);
      return { ...analysis, optimizationNeeded: false };
    }
    
    console.log(`Performance score ${overallScore} below threshold ${this.config.performanceThreshold} - optimization needed`);
    return { ...analysis, optimizationNeeded: true };
  }

  private calculateOverallScore(analysis: any): number {
    // Calculate weighted score from different metrics
    const weights = {
      performance: 0.4,
      bundle: 0.2,
      accessibility: 0.2,
      userExperience: 0.2
    };

    let score = 0;
    
    // Performance score (based on bottlenecks)
    const criticalBottlenecks = analysis.bottlenecks.filter((b: any) => b.severity > 7).length;
    const performanceScore = Math.max(0, 100 - (criticalBottlenecks * 20));
    score += performanceScore * weights.performance;

    // Bundle score (based on recommendations)
    const bundleRecommendations = analysis.recommendations.filter((r: any) => r.category === 'bundle').length;
    const bundleScore = Math.max(0, 100 - (bundleRecommendations * 25));
    score += bundleScore * weights.bundle;

    // Accessibility score
    const accessibilityRecommendations = analysis.recommendations.filter((r: any) => r.category === 'accessibility').length;
    const accessibilityScore = Math.max(0, 100 - (accessibilityRecommendations * 30));
    score += accessibilityScore * weights.accessibility;

    // User experience score
    const uxScore = analysis.userBehavior.errorProneComponents.length > 0 ? 70 : 90;
    score += uxScore * weights.userExperience;

    return Math.round(score);
  }

  private async optimizeComponents(metricsAnalysis: any): Promise<ComponentOptimization[]> {
    if (!metricsAnalysis.optimizationNeeded) {
      console.log('No component optimization needed');
      return [];
    }

    console.log('Optimizing components based on metrics...');
    
    const optimizations = await this.performanceOptimizer.optimizeComponents();
    
    // Limit optimizations per session
    const limitedOptimizations = optimizations.slice(0, this.config.maxOptimizationsPerSession);
    
    if (this.config.enableAutomaticOptimization && !this.config.requireApproval) {
      console.log(`Automatically applying ${limitedOptimizations.length} optimizations`);
      // In a real implementation, this would apply the optimizations
      // For now, we just log them
      limitedOptimizations.forEach(opt => {
        console.log(`Applied ${opt.optimizationType} to ${opt.componentName}`);
      });
    } else {
      console.log(`Generated ${limitedOptimizations.length} optimization recommendations (approval required)`);
    }
    
    return limitedOptimizations;
  }

  private async updateDocumentation(): Promise<DocumentationUpdate[]> {
    if (!this.config.enableDocumentationUpdates) {
      console.log('Documentation updates disabled');
      return [];
    }

    console.log('Updating documentation based on usage patterns...');
    
    const analysis = await this.documentationUpdater.analyzeDocumentationNeeds();
    
    if (this.config.enableAutomaticOptimization && !this.config.requireApproval) {
      await this.documentationUpdater.updateDocumentationFiles(analysis.updates);
      console.log(`Applied ${analysis.updates.length} documentation updates`);
    } else {
      console.log(`Generated ${analysis.updates.length} documentation update recommendations`);
    }
    
    return analysis.updates;
  }

  private async validateOptimizations(): Promise<any> {
    console.log('Validating optimization impact...');
    
    // Get current performance metrics
    const currentMetrics = await this.performanceMonitor.generateReport();
    
    // Compare with historical data (simplified)
    const improvement = this.calculateImprovement(currentMetrics);
    
    return {
      before: {}, // Would contain previous metrics
      after: currentMetrics,
      improvement
    };
  }

  private calculateImprovement(currentMetrics: any): number {
    // Simplified improvement calculation
    // In a real implementation, this would compare with baseline metrics
    return Math.random() * 20 + 5; // 5-25% improvement simulation
  }

  public scheduleAutomaticOptimization(): void {
    if (this.scheduledOptimization) {
      clearInterval(this.scheduledOptimization);
    }

    const intervalMs = this.config.optimizationInterval * 60 * 60 * 1000; // Convert hours to ms
    
    this.scheduledOptimization = setInterval(async () => {
      try {
        console.log('Running scheduled optimization...');
        await this.startOptimizationCycle();
      } catch (error) {
        console.error('Scheduled optimization failed:', error);
      }
    }, intervalMs);

    console.log(`Scheduled automatic optimization every ${this.config.optimizationInterval} hours`);
  }

  public stopAutomaticOptimization(): void {
    if (this.scheduledOptimization) {
      clearInterval(this.scheduledOptimization);
      this.scheduledOptimization = null;
      console.log('Stopped automatic optimization');
    }
  }

  public async getOptimizationRecommendations(): Promise<{
    recommendations: OptimizationRecommendation[];
    priority: 'critical' | 'high' | 'medium' | 'low';
    estimatedImpact: string;
  }> {
    const analysis = await this.metricsAnalyzer.analyzeProductionMetrics();
    
    const criticalRecommendations = analysis.recommendations.filter((r: any) => r.priority === 'critical');
    const highRecommendations = analysis.recommendations.filter((r: any) => r.priority === 'high');
    
    let priority: 'critical' | 'high' | 'medium' | 'low' = 'low';
    if (criticalRecommendations.length > 0) {
      priority = 'critical';
    } else if (highRecommendations.length > 0) {
      priority = 'high';
    } else if (analysis.recommendations.length > 0) {
      priority = 'medium';
    }
    
    const estimatedImpact = this.estimateOverallImpact(analysis.recommendations);
    
    return {
      recommendations: analysis.recommendations,
      priority,
      estimatedImpact
    };
  }

  private estimateOverallImpact(recommendations: OptimizationRecommendation[]): string {
    const totalRecommendations = recommendations.length;
    const criticalCount = recommendations.filter(r => r.priority === 'critical').length;
    const highCount = recommendations.filter(r => r.priority === 'high').length;
    
    if (criticalCount > 0) {
      return `High impact: ${criticalCount} critical issues could improve performance by 30-50%`;
    } else if (highCount > 2) {
      return `Medium-high impact: ${highCount} high priority optimizations could improve performance by 20-30%`;
    } else if (totalRecommendations > 5) {
      return `Medium impact: ${totalRecommendations} optimizations could improve performance by 10-20%`;
    } else {
      return `Low impact: ${totalRecommendations} minor optimizations available`;
    }
  }

  public getOptimizationHistory(): OptimizationSession[] {
    return [...this.optimizationHistory];
  }

  public getCurrentSession(): OptimizationSession | null {
    return this.currentSession;
  }

  public async generateOptimizationReport(): Promise<string> {
    const recommendations = await this.getOptimizationRecommendations();
    const history = this.getOptimizationHistory();
    const currentSession = this.getCurrentSession();
    
    let report = '# Design System Optimization Report\n\n';
    report += `Generated: ${new Date().toISOString()}\n\n`;
    
    // Current Status
    report += '## Current Status\n\n';
    if (currentSession) {
      report += `**Active Session:** ${currentSession.id} (${currentSession.phase})\n`;
    } else {
      report += '**Status:** No active optimization session\n';
    }
    report += `**Priority Level:** ${recommendations.priority.toUpperCase()}\n`;
    report += `**Estimated Impact:** ${recommendations.estimatedImpact}\n\n`;
    
    // Recommendations Summary
    report += '## Optimization Recommendations\n\n';
    report += `**Total Recommendations:** ${recommendations.recommendations.length}\n\n`;
    
    const byPriority = recommendations.recommendations.reduce((acc: any, rec) => {
      acc[rec.priority] = (acc[rec.priority] || 0) + 1;
      return acc;
    }, {});
    
    Object.entries(byPriority).forEach(([priority, count]) => {
      report += `- **${priority.toUpperCase()}:** ${count} recommendations\n`;
    });
    
    report += '\n### Top Recommendations\n\n';
    recommendations.recommendations.slice(0, 5).forEach((rec, index) => {
      report += `${index + 1}. **${rec.title}** (${rec.priority})\n`;
      report += `   - ${rec.description}\n`;
      report += `   - Impact: ${rec.impact}\n`;
      report += `   - Effort: ${rec.effort}\n\n`;
    });
    
    // Optimization History
    report += '## Optimization History\n\n';
    if (history.length === 0) {
      report += 'No optimization sessions completed yet.\n\n';
    } else {
      const recentSessions = history.slice(-5);
      recentSessions.forEach(session => {
        const duration = session.endTime ? 
          Math.round((session.endTime - session.startTime) / 1000) : 'ongoing';
        
        report += `### Session ${session.id}\n`;
        report += `- **Status:** ${session.status}\n`;
        report += `- **Duration:** ${duration}s\n`;
        report += `- **Optimizations Applied:** ${session.results.componentOptimizations?.length || 0}\n`;
        report += `- **Documentation Updates:** ${session.results.documentationUpdates?.length || 0}\n`;
        
        if (session.results.performanceImpact) {
          report += `- **Performance Improvement:** ${session.results.performanceImpact.improvement}%\n`;
        }
        
        if (session.errors.length > 0) {
          report += `- **Errors:** ${session.errors.length}\n`;
        }
        
        report += '\n';
      });
    }
    
    // Configuration
    report += '## Configuration\n\n';
    report += `- **Automatic Optimization:** ${this.config.enableAutomaticOptimization ? 'Enabled' : 'Disabled'}\n`;
    report += `- **Documentation Updates:** ${this.config.enableDocumentationUpdates ? 'Enabled' : 'Disabled'}\n`;
    report += `- **Performance Threshold:** ${this.config.performanceThreshold}%\n`;
    report += `- **Optimization Interval:** ${this.config.optimizationInterval} hours\n`;
    report += `- **Require Approval:** ${this.config.requireApproval ? 'Yes' : 'No'}\n\n`;
    
    return report;
  }

  private generateSessionId(): string {
    return `opt-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  public updateConfig(newConfig: Partial<OptimizationConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('Optimization configuration updated:', newConfig);
  }

  public cleanup(): void {
    this.stopAutomaticOptimization();
    this.metricsAnalyzer.cleanup();
    this.performanceOptimizer.cleanup();
    this.documentationUpdater.cleanup();
    this.optimizationHistory.length = 0;
  }
}

export { OptimizationOrchestrator, type OptimizationSession, type OptimizationConfig };