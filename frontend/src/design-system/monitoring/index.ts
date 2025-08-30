/**
 * Design System Monitoring Suite
 * Comprehensive monitoring and analytics for design system integration
 */

// Core monitoring components
export { PerformanceMonitor, getPerformanceMonitor } from './PerformanceMonitor';
export { CoreWebVitalsMonitor } from './CoreWebVitals';
export { BundleAnalyzer } from './BundleAnalyzer';
export { ComponentPerformanceTracker } from './ComponentPerformanceTracker';
export { UserExperienceMetrics } from './UserExperienceMetrics';

// Integration health monitoring
export { IntegrationHealthMonitor } from './IntegrationHealthMonitor';
export { ComponentUsageTracker } from './ComponentUsageTracker';
export { MigrationProgressTracker } from './MigrationProgressTracker';
export { ErrorTracker } from './ErrorTracker';
export { AccessibilityComplianceMonitor } from './AccessibilityComplianceMonitor';

// React hooks
export { usePerformanceMonitoring, useInteractionTracking, withPerformanceTracking } from '../hooks/usePerformanceMonitoring';

// Types
export type { PerformanceReport, MonitoringConfig } from './PerformanceMonitor';
export type { PerformanceData, WebVitalMetric } from './CoreWebVitals';
export type { BundleMetrics, LoadingMetrics } from './BundleAnalyzer';
export type { ComponentMetrics, RenderProfile } from './ComponentPerformanceTracker';
export type { UserInteraction, AccessibilityMetrics, SatisfactionMetrics } from './UserExperienceMetrics';
export type { HealthScore, HealthAlert, IntegrationReport } from './IntegrationHealthMonitor';
export type { ComponentUsage, MigrationStatus, IntegrationHealth } from './ComponentUsageTracker';
export type { MigrationTask, MigrationMetrics, ComponentMigrationStatus } from './MigrationProgressTracker';
export type { DesignSystemError, ErrorMetrics, ErrorPattern } from './ErrorTracker';
export type { AccessibilityViolation, ComplianceReport } from './AccessibilityComplianceMonitor';

/**
 * Initialize complete monitoring suite
 */
export function initializeMonitoring(config?: {
  enablePerformanceMonitoring?: boolean;
  enableIntegrationHealth?: boolean;
  enableAccessibilityCompliance?: boolean;
  reportingInterval?: number;
  reportingEndpoint?: string;
}) {
  const {
    enablePerformanceMonitoring = true,
    enableIntegrationHealth = true,
    enableAccessibilityCompliance = true,
    reportingInterval = 300000, // 5 minutes
    reportingEndpoint = '/api/v1/performance-metrics/'
  } = config || {};

  const monitors: any[] = [];

  if (enablePerformanceMonitoring) {
    const performanceMonitor = getPerformanceMonitor({
      reportingInterval,
      reportingEndpoint,
      enableWebVitals: true,
      enableBundleAnalysis: true,
      enableComponentTracking: true,
      enableUXTracking: true
    });
    
    performanceMonitor.startMonitoring();
    monitors.push(performanceMonitor);
  }

  if (enableIntegrationHealth) {
    const healthMonitor = new IntegrationHealthMonitor();
    healthMonitor.startMonitoring();
    monitors.push(healthMonitor);
  }

  if (enableAccessibilityCompliance) {
    const accessibilityMonitor = new AccessibilityComplianceMonitor();
    accessibilityMonitor.startMonitoring();
    monitors.push(accessibilityMonitor);
  }

  // Return cleanup function
  return () => {
    monitors.forEach(monitor => {
      if (monitor.stopMonitoring) {
        monitor.stopMonitoring();
      }
      if (monitor.cleanup) {
        monitor.cleanup();
      }
    });
  };
}

/**
 * Generate comprehensive monitoring dashboard data
 */
export async function generateMonitoringDashboard() {
  const performanceMonitor = getPerformanceMonitor();
  const healthMonitor = new IntegrationHealthMonitor();
  const accessibilityMonitor = new AccessibilityComplianceMonitor();

  const [
    performanceReport,
    integrationReport,
    accessibilityReport
  ] = await Promise.all([
    performanceMonitor.generateReport(),
    healthMonitor.generateIntegrationReport(),
    accessibilityMonitor.performAccessibilityCheck()
  ]);

  return {
    timestamp: Date.now(),
    performance: performanceReport,
    integration: integrationReport,
    accessibility: accessibilityReport,
    summary: {
      overallHealth: integrationReport.healthScore.overall,
      performanceScore: performanceReport.overallScore,
      accessibilityScore: accessibilityReport.overallScore,
      criticalIssues: [
        ...integrationReport.alerts.filter(alert => alert.type === 'critical'),
        ...accessibilityReport.violations.filter(v => v.severity === 'error')
      ].length
    }
  };
}