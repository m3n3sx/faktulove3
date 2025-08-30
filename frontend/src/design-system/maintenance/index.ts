/**
 * Design System Maintenance Module
 * Exports all maintenance-related functionality
 */

export { DesignSystemMaintenance, type MaintenanceConfig, type MaintenanceTask, type MaintenanceResult } from './DesignSystemMaintenance';
export { ContinuousIntegration, type CIConfig, type CIJob, type TestSuite, type TestResult, type DeploymentTarget } from './ContinuousIntegration';
export { EvolutionPlan, type EvolutionMilestone, type VersionPlan, type MaintenanceSchedule, type TechnologyRoadmap } from './EvolutionPlan';
export { MaintenanceOrchestrator, type MaintenanceOrchestrationConfig, type MaintenanceStatus, type MaintenanceAlert } from './MaintenanceOrchestrator';

/**
 * Quick start function for initializing maintenance system
 */
export async function initializeMaintenanceSystem(config?: Partial<MaintenanceOrchestrationConfig>): Promise<MaintenanceOrchestrator> {
  const { MaintenanceOrchestrator } = await import('./MaintenanceOrchestrator');
  
  const orchestrator = new MaintenanceOrchestrator(config);
  await orchestrator.startOrchestration();
  
  return orchestrator;
}

/**
 * Run a comprehensive health check
 */
export async function runHealthCheck(): Promise<MaintenanceStatus> {
  const { MaintenanceOrchestrator } = await import('./MaintenanceOrchestrator');
  
  const orchestrator = new MaintenanceOrchestrator();
  try {
    return await orchestrator.performHealthCheck();
  } finally {
    orchestrator.cleanup();
  }
}

/**
 * Generate maintenance report
 */
export async function generateMaintenanceReport(): Promise<string> {
  const { MaintenanceOrchestrator } = await import('./MaintenanceOrchestrator');
  
  const orchestrator = new MaintenanceOrchestrator();
  try {
    return await orchestrator.generatePeriodicReport();
  } finally {
    orchestrator.cleanup();
  }
}

/**
 * Run CI pipeline
 */
export async function runCIPipeline(trigger: 'push' | 'pull-request' | 'manual' = 'manual'): Promise<CIJob> {
  const { ContinuousIntegration } = await import('./ContinuousIntegration');
  
  const ci = new ContinuousIntegration();
  try {
    return await ci.runCIPipeline(trigger);
  } finally {
    ci.cleanup();
  }
}

/**
 * Get evolution plan status
 */
export function getEvolutionStatus(): {
  upcomingMilestones: EvolutionMilestone[];
  overdueMilestones: EvolutionMilestone[];
  projectHealth: any;
} {
  const { EvolutionPlan } = require('./EvolutionPlan');
  
  const evolution = new EvolutionPlan();
  try {
    return {
      upcomingMilestones: evolution.getUpcomingMilestones(),
      overdueMilestones: evolution.getOverdueMilestones(),
      projectHealth: evolution.calculateProjectHealth()
    };
  } finally {
    evolution.cleanup();
  }
}

// Type re-exports for convenience
export type { MaintenanceOrchestrationConfig } from './MaintenanceOrchestrator';