/**
 * Integration health monitoring system for design system
 * Combines all monitoring components to provide comprehensive health insights
 */

import { ComponentUsageTracker, type ComponentUsage, type IntegrationHealth } from './ComponentUsageTracker';
import { MigrationProgressTracker, type MigrationMetrics, type ComponentMigrationStatus } from './MigrationProgressTracker';
import { ErrorTracker, type ErrorMetrics, type DesignSystemError } from './ErrorTracker';
import { UserExperienceMetrics, type AccessibilityMetrics } from './UserExperienceMetrics';

interface HealthScore {
  overall: number;
  migration: number;
  adoption: number;
  quality: number;
  accessibility: number;
  performance: number;
}

interface HealthAlert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  category: 'migration' | 'adoption' | 'quality' | 'accessibility' | 'performance';
  message: string;
  timestamp: number;
  resolved: boolean;
  actionRequired: string;
}

interface IntegrationReport {
  timestamp: number;
  healthScore: HealthScore;
  alerts: HealthAlert[];
  metrics: {
    migration: MigrationMetrics;
    usage: IntegrationHealth;
    errors: ErrorMetrics;
    accessibility: AccessibilityMetrics;
  };
  recommendations: {
    priority: 'high' | 'medium' | 'low';
    category: string;
    action: string;
    impact: string;
  }[];
  trends: {
    migrationVelocity: number[];
    errorRate: number[];
    adoptionRate: number[];
    accessibilityScore: number[];
  };
}

class IntegrationHealthMonitor {
  private usageTracker: ComponentUsageTracker;
  private migrationTracker: MigrationProgressTracker;
  private errorTracker: ErrorTracker;
  private uxMetrics: UserExperienceMetrics;
  private alerts: Map<string, HealthAlert> = new Map();
  private isMonitoring: boolean = false;
  private reportingInterval: number = 300000; // 5 minutes
  private reportingTimer: NodeJS.Timeout | null = null;

  constructor() {
    this.usageTracker = new ComponentUsageTracker();
    this.migrationTracker = new MigrationProgressTracker();
    this.errorTracker = new ErrorTracker();
    this.uxMetrics = new UserExperienceMetrics();
    
    this.initializeMonitoring();
  }

  private initializeMonitoring(): void {
    // Start all monitoring components
    this.usageTracker.startTracking();
    this.migrationTracker.startTracking();
    this.errorTracker.startTracking();
    this.uxMetrics.startTracking();
    
    // Set up periodic health checks
    this.setupHealthChecks();
  }

  private setupHealthChecks(): void {
    if (this.isMonitoring) {
      this.reportingTimer = setInterval(() => {
        this.performHealthCheck();
      }, this.reportingInterval);
    }
  }

  public startMonitoring(): void {
    this.isMonitoring = true;
    this.setupHealthChecks();
    console.log('Integration health monitoring started');
  }

  public stopMonitoring(): void {
    this.isMonitoring = false;
    
    if (this.reportingTimer) {
      clearInterval(this.reportingTimer);
      this.reportingTimer = null;
    }
    
    this.usageTracker.stopTracking();
    this.migrationTracker.stopTracking();
    this.errorTracker.stopTracking();
    this.uxMetrics.stopTracking();
    
    console.log('Integration health monitoring stopped');
  }

  private async performHealthCheck(): Promise<void> {
    try {
      // Check migration progress
      await this.checkMigrationHealth();
      
      // Check component adoption
      await this.checkAdoptionHealth();
      
      // Check error rates
      await this.checkQualityHealth();
      
      // Check accessibility
      await this.checkAccessibilityHealth();
      
      // Generate alerts for critical issues
      await this.generateAlerts();
      
    } catch (error) {
      console.error('Health check failed:', error);
    }
  }

  private async checkMigrationHealth(): Promise<void> {
    const migrationMetrics = this.migrationTracker.getMigrationMetrics();
    
    // Check for stalled migration
    if (migrationMetrics.velocity < 0.5 && migrationMetrics.overallProgress < 90) {
      this.createAlert({
        type: 'warning',
        category: 'migration',
        message: 'Migration velocity is low - progress may be stalled',
        actionRequired: 'Review blocked tasks and allocate resources'
      });
    }
    
    // Check for blocked tasks
    const blockedTasks = this.migrationTracker.getBlockedTasks();
    if (blockedTasks.length > 0) {
      this.createAlert({
        type: 'critical',
        category: 'migration',
        message: `${blockedTasks.length} migration tasks are blocked`,
        actionRequired: 'Resolve blockers to continue migration progress'
      });
    }
    
    // Check completion timeline
    if (migrationMetrics.estimatedCompletion > Date.now() + 30 * 24 * 60 * 60 * 1000) { // 30 days
      this.createAlert({
        type: 'warning',
        category: 'migration',
        message: 'Migration completion is more than 30 days away',
        actionRequired: 'Consider increasing migration velocity'
      });
    }
  }

  private async checkAdoptionHealth(): Promise<void> {
    const usageHealth = this.usageTracker.calculateIntegrationHealth();
    
    // Check component adoption rate
    if (usageHealth.componentAdoption < 50) {
      this.createAlert({
        type: 'warning',
        category: 'adoption',
        message: 'Low design system component adoption rate',
        actionRequired: 'Promote design system usage and provide training'
      });
    }
    
    // Check for unused components
    const allUsage = this.usageTracker.getComponentUsage() as ComponentUsage[];
    const unusedComponents = allUsage.filter(usage => usage.usageCount === 0);
    
    if (unusedComponents.length > 5) {
      this.createAlert({
        type: 'info',
        category: 'adoption',
        message: `${unusedComponents.length} components are not being used`,
        actionRequired: 'Review component necessity or improve documentation'
      });
    }
  }

  private async checkQualityHealth(): Promise<void> {
    const errorMetrics = this.errorTracker.getErrorMetrics();
    
    // Check error rate
    if (errorMetrics.errorRate > 5) {
      this.createAlert({
        type: 'critical',
        category: 'quality',
        message: 'High error rate detected in design system components',
        actionRequired: 'Investigate and fix component errors immediately'
      });
    }
    
    // Check unresolved errors
    if (errorMetrics.unresolvedErrors > 20) {
      this.createAlert({
        type: 'warning',
        category: 'quality',
        message: `${errorMetrics.unresolvedErrors} unresolved errors`,
        actionRequired: 'Prioritize error resolution and bug fixes'
      });
    }
    
    // Check critical errors
    const criticalErrors = this.errorTracker.getErrors({ severity: 'critical', resolved: false });
    if (criticalErrors.length > 0) {
      this.createAlert({
        type: 'critical',
        category: 'quality',
        message: `${criticalErrors.length} critical errors need immediate attention`,
        actionRequired: 'Fix critical errors immediately'
      });
    }
  }

  private async checkAccessibilityHealth(): Promise<void> {
    const uxData = this.uxMetrics.getMetrics();
    const uxReport = this.uxMetrics.generateUXReport();
    
    // Check accessibility score
    if (uxReport.accessibilityScore < 80) {
      this.createAlert({
        type: 'critical',
        category: 'accessibility',
        message: 'Accessibility score is below acceptable threshold',
        actionRequired: 'Address accessibility issues immediately'
      });
    }
    
    // Check for missing labels
    if (uxData.accessibility.screenReader.missingLabels > 0) {
      this.createAlert({
        type: 'warning',
        category: 'accessibility',
        message: `${uxData.accessibility.screenReader.missingLabels} elements missing accessibility labels`,
        actionRequired: 'Add proper ARIA labels to all interactive elements'
      });
    }
    
    // Check color contrast violations
    if (uxData.accessibility.colorContrast.violations > 0) {
      this.createAlert({
        type: 'warning',
        category: 'accessibility',
        message: `${uxData.accessibility.colorContrast.violations} color contrast violations`,
        actionRequired: 'Fix color contrast to meet WCAG guidelines'
      });
    }
  }

  private createAlert(alertData: Omit<HealthAlert, 'id' | 'timestamp' | 'resolved'>): void {
    const alert: HealthAlert = {
      id: this.generateAlertId(),
      timestamp: Date.now(),
      resolved: false,
      ...alertData
    };
    
    this.alerts.set(alert.id, alert);
    
    // Limit stored alerts
    if (this.alerts.size > 100) {
      const oldestAlerts = Array.from(this.alerts.entries())
        .sort(([, a], [, b]) => a.timestamp - b.timestamp)
        .slice(0, 50);
      
      oldestAlerts.forEach(([id]) => this.alerts.delete(id));
    }
  }

  private generateAlertId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async generateAlerts(): Promise<void> {
    // This method is called after all health checks to generate summary alerts
    const activeAlerts = Array.from(this.alerts.values()).filter(alert => !alert.resolved);
    
    if (activeAlerts.length > 10) {
      this.createAlert({
        type: 'warning',
        category: 'quality',
        message: `${activeAlerts.length} active alerts require attention`,
        actionRequired: 'Review and resolve outstanding alerts'
      });
    }
  }

  public calculateHealthScore(): HealthScore {
    const migrationMetrics = this.migrationTracker.getMigrationMetrics();
    const usageHealth = this.usageTracker.calculateIntegrationHealth();
    const errorMetrics = this.errorTracker.getErrorMetrics();
    const uxReport = this.uxMetrics.generateUXReport();
    
    // Migration score (0-100)
    const migration = migrationMetrics.overallProgress;
    
    // Adoption score (0-100)
    const adoption = usageHealth.componentAdoption;
    
    // Quality score (0-100) - based on error rate
    const quality = Math.max(0, 100 - (errorMetrics.errorRate * 10));
    
    // Accessibility score (0-100)
    const accessibility = uxReport.accessibilityScore;
    
    // Performance score (0-100) - placeholder, would come from performance metrics
    const performance = 85;
    
    // Overall score - weighted average
    const overall = (
      migration * 0.25 +
      adoption * 0.25 +
      quality * 0.20 +
      accessibility * 0.20 +
      performance * 0.10
    );
    
    return {
      overall: Math.round(overall),
      migration: Math.round(migration),
      adoption: Math.round(adoption),
      quality: Math.round(quality),
      accessibility: Math.round(accessibility),
      performance: Math.round(performance)
    };
  }

  public getActiveAlerts(): HealthAlert[] {
    return Array.from(this.alerts.values())
      .filter(alert => !alert.resolved)
      .sort((a, b) => {
        // Sort by type priority, then by timestamp
        const typePriority = { critical: 3, warning: 2, info: 1 };
        const aPriority = typePriority[a.type];
        const bPriority = typePriority[b.type];
        
        if (aPriority !== bPriority) {
          return bPriority - aPriority;
        }
        
        return b.timestamp - a.timestamp;
      });
  }

  public resolveAlert(alertId: string): void {
    const alert = this.alerts.get(alertId);
    if (alert) {
      alert.resolved = true;
    }
  }

  public async generateIntegrationReport(): Promise<IntegrationReport> {
    const timestamp = Date.now();
    const healthScore = this.calculateHealthScore();
    const alerts = this.getActiveAlerts();
    
    // Collect metrics from all trackers
    const migrationMetrics = this.migrationTracker.getMigrationMetrics();
    const usageHealth = this.usageTracker.calculateIntegrationHealth();
    const errorMetrics = this.errorTracker.getErrorMetrics();
    const uxData = this.uxMetrics.getMetrics();
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(healthScore, alerts);
    
    // Generate trends (simplified - would use historical data in production)
    const trends = {
      migrationVelocity: [migrationMetrics.velocity],
      errorRate: [errorMetrics.errorRate],
      adoptionRate: [usageHealth.componentAdoption],
      accessibilityScore: [healthScore.accessibility]
    };
    
    return {
      timestamp,
      healthScore,
      alerts,
      metrics: {
        migration: migrationMetrics,
        usage: usageHealth,
        errors: errorMetrics,
        accessibility: uxData.accessibility
      },
      recommendations,
      trends
    };
  }

  private generateRecommendations(healthScore: HealthScore, alerts: HealthAlert[]): IntegrationReport['recommendations'] {
    const recommendations: IntegrationReport['recommendations'] = [];
    
    // Migration recommendations
    if (healthScore.migration < 80) {
      recommendations.push({
        priority: 'high',
        category: 'Migration',
        action: 'Accelerate component migration process',
        impact: 'Improves consistency and reduces technical debt'
      });
    }
    
    // Adoption recommendations
    if (healthScore.adoption < 60) {
      recommendations.push({
        priority: 'medium',
        category: 'Adoption',
        action: 'Increase design system component usage',
        impact: 'Better consistency and maintainability'
      });
    }
    
    // Quality recommendations
    if (healthScore.quality < 70) {
      recommendations.push({
        priority: 'high',
        category: 'Quality',
        action: 'Reduce component error rates',
        impact: 'Improves user experience and developer productivity'
      });
    }
    
    // Accessibility recommendations
    if (healthScore.accessibility < 85) {
      recommendations.push({
        priority: 'high',
        category: 'Accessibility',
        action: 'Address accessibility compliance issues',
        impact: 'Ensures inclusive user experience and legal compliance'
      });
    }
    
    // Alert-based recommendations
    const criticalAlerts = alerts.filter(alert => alert.type === 'critical');
    if (criticalAlerts.length > 0) {
      recommendations.push({
        priority: 'high',
        category: 'Critical Issues',
        action: `Resolve ${criticalAlerts.length} critical alerts immediately`,
        impact: 'Prevents system failures and user experience degradation'
      });
    }
    
    return recommendations.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  }

  public cleanup(): void {
    this.stopMonitoring();
    this.usageTracker.cleanup();
    this.migrationTracker.cleanup();
    this.errorTracker.cleanup();
    this.uxMetrics.cleanup();
    this.alerts.clear();
  }
}

export { IntegrationHealthMonitor, type HealthScore, type HealthAlert, type IntegrationReport };