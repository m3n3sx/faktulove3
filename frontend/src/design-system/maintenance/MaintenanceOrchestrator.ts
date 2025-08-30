/**
 * Maintenance Orchestrator
 * Coordinates all maintenance activities for the design system
 */

import { DesignSystemMaintenance, type MaintenanceConfig, type MaintenanceTask } from './DesignSystemMaintenance';
import { ContinuousIntegration, type CIConfig, type CIJob } from './ContinuousIntegration';
import { EvolutionPlan, type EvolutionMilestone } from './EvolutionPlan';

interface MaintenanceOrchestrationConfig {
  maintenance: Partial<MaintenanceConfig>;
  ci: Partial<CIConfig>;
  enableAutomation: boolean;
  notificationChannels: string[];
  reportingInterval: number; // hours
}

interface MaintenanceStatus {
  overall: 'healthy' | 'warning' | 'critical';
  maintenance: {
    score: number;
    activeTasks: number;
    overdueTasks: number;
  };
  ci: {
    score: number;
    activeJobs: number;
    successRate: number;
  };
  evolution: {
    score: number;
    onTrackMilestones: number;
    delayedMilestones: number;
  };
  lastUpdated: number;
}

interface MaintenanceAlert {
  id: string;
  type: 'maintenance' | 'ci' | 'evolution';
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  description: string;
  timestamp: number;
  acknowledged: boolean;
  actionRequired: boolean;
  suggestedActions: string[];
}

class MaintenanceOrchestrator {
  private maintenance: DesignSystemMaintenance;
  private ci: ContinuousIntegration;
  private evolution: EvolutionPlan;
  private config: MaintenanceOrchestrationConfig;
  private alerts: Map<string, MaintenanceAlert> = new Map();
  private reportingTimer: NodeJS.Timeout | null = null;
  private isRunning: boolean = false;

  constructor(config: Partial<MaintenanceOrchestrationConfig> = {}) {
    this.config = {
      maintenance: {},
      ci: {},
      enableAutomation: false, // Disabled by default for safety
      notificationChannels: ['console'],
      reportingInterval: 24, // 24 hours
      ...config
    };

    this.maintenance = new DesignSystemMaintenance(this.config.maintenance);
    this.ci = new ContinuousIntegration(this.config.ci);
    this.evolution = new EvolutionPlan();
  }

  public async startOrchestration(): Promise<void> {
    if (this.isRunning) {
      console.warn('Maintenance orchestration is already running');
      return;
    }

    this.isRunning = true;
    console.log('🚀 Starting design system maintenance orchestration...');

    try {
      // Start maintenance scheduler
      this.maintenance.startMaintenanceScheduler();

      // Start periodic reporting
      if (this.config.reportingInterval > 0) {
        this.reportingTimer = setInterval(async () => {
          await this.generatePeriodicReport();
        }, this.config.reportingInterval * 60 * 60 * 1000);
      }

      // Run initial health check
      await this.performHealthCheck();

      console.log('✅ Maintenance orchestration started successfully');

    } catch (error) {
      this.isRunning = false;
      console.error('❌ Failed to start maintenance orchestration:', error);
      throw error;
    }
  }

  public stopOrchestration(): void {
    if (!this.isRunning) {
      return;
    }

    this.isRunning = false;
    console.log('🛑 Stopping design system maintenance orchestration...');

    // Stop maintenance scheduler
    this.maintenance.stopMaintenanceScheduler();

    // Stop CI (if running)
    this.ci.cleanup();

    // Clear reporting timer
    if (this.reportingTimer) {
      clearInterval(this.reportingTimer);
      this.reportingTimer = null;
    }

    console.log('✅ Maintenance orchestration stopped');
  }

  public async performHealthCheck(): Promise<MaintenanceStatus> {
    console.log('🔍 Performing comprehensive health check...');

    try {
      // Get maintenance status
      const maintenanceTasks = this.maintenance.getMaintenanceTasks();
      const overdueTasks = maintenanceTasks.filter(task => 
        task.nextRun && task.nextRun < Date.now()
      ).length;
      const activeTasks = maintenanceTasks.filter(task => 
        task.status === 'running'
      ).length;

      // Calculate maintenance score
      const maintenanceScore = this.calculateMaintenanceScore(maintenanceTasks);

      // Get CI status
      const ciJobs = this.ci.getJobHistory().slice(-10); // Last 10 jobs
      const successfulJobs = ciJobs.filter(job => job.status === 'passed').length;
      const ciSuccessRate = ciJobs.length > 0 ? (successfulJobs / ciJobs.length) * 100 : 100;
      const activeCIJobs = this.ci.getActiveJobs().length;

      // Calculate CI score
      const ciScore = Math.min(100, ciSuccessRate + (activeCIJobs > 0 ? -10 : 0));

      // Get evolution status
      const evolutionHealth = this.evolution.calculateProjectHealth();

      // Determine overall status
      const overallScore = (maintenanceScore * 0.4) + (ciScore * 0.3) + (evolutionHealth.overallScore * 0.3);
      let overall: MaintenanceStatus['overall'] = 'healthy';
      
      if (overallScore < 60) {
        overall = 'critical';
      } else if (overallScore < 80) {
        overall = 'warning';
      }

      const status: MaintenanceStatus = {
        overall,
        maintenance: {
          score: Math.round(maintenanceScore),
          activeTasks,
          overdueTasks
        },
        ci: {
          score: Math.round(ciScore),
          activeJobs: activeCIJobs,
          successRate: Math.round(ciSuccessRate)
        },
        evolution: {
          score: evolutionHealth.overallScore,
          onTrackMilestones: evolutionHealth.milestonesOnTrack,
          delayedMilestones: evolutionHealth.milestonesDelayed
        },
        lastUpdated: Date.now()
      };

      // Generate alerts based on status
      await this.generateHealthAlerts(status);

      console.log(`📊 Health check completed - Overall status: ${overall.toUpperCase()}`);
      
      return status;

    } catch (error) {
      console.error('❌ Health check failed:', error);
      
      // Return critical status on failure
      return {
        overall: 'critical',
        maintenance: { score: 0, activeTasks: 0, overdueTasks: 0 },
        ci: { score: 0, activeJobs: 0, successRate: 0 },
        evolution: { score: 0, onTrackMilestones: 0, delayedMilestones: 0 },
        lastUpdated: Date.now()
      };
    }
  }

  private calculateMaintenanceScore(tasks: MaintenanceTask[]): number {
    if (tasks.length === 0) return 100;

    let score = 100;
    const now = Date.now();

    tasks.forEach(task => {
      // Penalize overdue tasks
      if (task.nextRun && task.nextRun < now) {
        const daysOverdue = (now - task.nextRun) / (24 * 60 * 60 * 1000);
        const penalty = Math.min(30, daysOverdue * 5); // Max 30 points penalty
        score -= penalty;
      }

      // Penalize failed tasks
      if (task.status === 'failed') {
        score -= 15;
      }

      // Bonus for completed tasks
      if (task.status === 'completed' && task.lastRun && (now - task.lastRun) < 24 * 60 * 60 * 1000) {
        score += 2;
      }
    });

    return Math.max(0, Math.min(100, score));
  }

  private async generateHealthAlerts(status: MaintenanceStatus): Promise<void> {
    // Clear old alerts
    this.clearOldAlerts();

    // Generate maintenance alerts
    if (status.maintenance.overdueTasks > 0) {
      this.addAlert({
        type: 'maintenance',
        severity: status.maintenance.overdueTasks > 3 ? 'critical' : 'warning',
        title: 'Overdue Maintenance Tasks',
        description: `${status.maintenance.overdueTasks} maintenance task(s) are overdue`,
        actionRequired: true,
        suggestedActions: [
          'Review overdue maintenance tasks',
          'Allocate resources to complete tasks',
          'Update maintenance schedule if needed'
        ]
      });
    }

    if (status.maintenance.score < 70) {
      this.addAlert({
        type: 'maintenance',
        severity: status.maintenance.score < 50 ? 'critical' : 'warning',
        title: 'Low Maintenance Score',
        description: `Maintenance score is ${status.maintenance.score}% (below 70% threshold)`,
        actionRequired: true,
        suggestedActions: [
          'Investigate maintenance issues',
          'Increase maintenance frequency',
          'Review maintenance procedures'
        ]
      });
    }

    // Generate CI alerts
    if (status.ci.successRate < 80) {
      this.addAlert({
        type: 'ci',
        severity: status.ci.successRate < 60 ? 'critical' : 'warning',
        title: 'Low CI Success Rate',
        description: `CI success rate is ${status.ci.successRate}% (below 80% threshold)`,
        actionRequired: true,
        suggestedActions: [
          'Review failed CI jobs',
          'Fix failing tests',
          'Improve CI pipeline stability'
        ]
      });
    }

    // Generate evolution alerts
    if (status.evolution.delayedMilestones > 0) {
      this.addAlert({
        type: 'evolution',
        severity: status.evolution.delayedMilestones > 2 ? 'critical' : 'warning',
        title: 'Delayed Milestones',
        description: `${status.evolution.delayedMilestones} milestone(s) are delayed`,
        actionRequired: true,
        suggestedActions: [
          'Review delayed milestones',
          'Reallocate resources',
          'Update milestone timelines'
        ]
      });
    }

    if (status.evolution.score < 70) {
      this.addAlert({
        type: 'evolution',
        severity: status.evolution.score < 50 ? 'critical' : 'warning',
        title: 'Low Evolution Score',
        description: `Evolution plan score is ${status.evolution.score}% (below 70% threshold)`,
        actionRequired: true,
        suggestedActions: [
          'Review evolution plan progress',
          'Address project health issues',
          'Update roadmap priorities'
        ]
      });
    }

    // Send notifications for critical alerts
    const criticalAlerts = Array.from(this.alerts.values())
      .filter(alert => alert.severity === 'critical' && !alert.acknowledged);

    if (criticalAlerts.length > 0) {
      await this.sendCriticalAlertNotifications(criticalAlerts);
    }
  }

  private addAlert(alertData: Omit<MaintenanceAlert, 'id' | 'timestamp' | 'acknowledged'>): void {
    const alert: MaintenanceAlert = {
      ...alertData,
      id: this.generateAlertId(),
      timestamp: Date.now(),
      acknowledged: false
    };

    this.alerts.set(alert.id, alert);
  }

  private clearOldAlerts(): void {
    const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
    
    Array.from(this.alerts.entries()).forEach(([id, alert]) => {
      if (alert.timestamp < oneDayAgo && alert.acknowledged) {
        this.alerts.delete(id);
      }
    });
  }

  private async sendCriticalAlertNotifications(alerts: MaintenanceAlert[]): Promise<void> {
    const message = this.formatCriticalAlertsMessage(alerts);
    
    for (const channel of this.config.notificationChannels) {
      try {
        await this.sendNotification(channel, message);
      } catch (error) {
        console.error(`Failed to send critical alert to ${channel}:`, error);
      }
    }
  }

  private formatCriticalAlertsMessage(alerts: MaintenanceAlert[]): string {
    let message = '🚨 CRITICAL DESIGN SYSTEM ALERTS\n\n';
    
    alerts.forEach(alert => {
      message += `**${alert.title}**\n`;
      message += `${alert.description}\n`;
      message += `Type: ${alert.type}\n`;
      message += `Time: ${new Date(alert.timestamp).toISOString()}\n\n`;
      
      if (alert.suggestedActions.length > 0) {
        message += 'Suggested Actions:\n';
        alert.suggestedActions.forEach(action => {
          message += `- ${action}\n`;
        });
        message += '\n';
      }
    });
    
    return message;
  }

  private async sendNotification(channel: string, message: string): Promise<void> {
    switch (channel) {
      case 'console':
        console.log('🚨 Critical Alert Notification:\n' + message);
        break;
      case 'email':
        // In a real implementation, this would send an email
        console.log('📧 Critical alert email sent');
        break;
      case 'slack':
        // In a real implementation, this would send to Slack
        console.log('💬 Critical alert Slack message sent');
        break;
      default:
        console.warn(`Unknown notification channel: ${channel}`);
    }
  }

  public async runMaintenanceTask(taskId: string): Promise<void> {
    console.log(`🔧 Running maintenance task: ${taskId}`);
    await this.maintenance.runMaintenanceTask(taskId);
  }

  public async runCIPipeline(trigger: 'push' | 'pull-request' | 'manual' = 'manual'): Promise<CIJob> {
    console.log(`🚀 Running CI pipeline: ${trigger}`);
    return await this.ci.runCIPipeline(trigger);
  }

  public async deployToEnvironment(
    environment: 'staging' | 'production',
    version: string
  ): Promise<void> {
    console.log(`🚀 Deploying to ${environment}: ${version}`);
    
    // Run CI pipeline first
    const ciJob = await this.runCIPipeline('manual');
    
    if (ciJob.status !== 'passed') {
      throw new Error(`CI pipeline failed, cannot deploy to ${environment}`);
    }
    
    // Deploy to environment
    await this.ci.deployToEnvironment(environment, version);
    
    // Update current version in evolution plan
    if (environment === 'production') {
      this.evolution.updateCurrentVersion(version);
    }
  }

  public getAlerts(): MaintenanceAlert[] {
    return Array.from(this.alerts.values())
      .sort((a, b) => b.timestamp - a.timestamp);
  }

  public acknowledgeAlert(alertId: string): boolean {
    const alert = this.alerts.get(alertId);
    if (alert) {
      alert.acknowledged = true;
      return true;
    }
    return false;
  }

  public async generatePeriodicReport(): Promise<string> {
    console.log('📊 Generating periodic maintenance report...');
    
    const status = await this.performHealthCheck();
    const maintenanceReport = await this.maintenance.generateMaintenanceReport();
    const ciReport = await this.ci.generateCIReport();
    const evolutionReport = this.evolution.generateEvolutionReport();
    
    let report = '# Design System Maintenance Status Report\n\n';
    report += `Generated: ${new Date().toISOString()}\n\n`;
    
    // Executive Summary
    report += '## Executive Summary\n\n';
    report += `- **Overall Status:** ${status.overall.toUpperCase()}\n`;
    report += `- **Maintenance Score:** ${status.maintenance.score}%\n`;
    report += `- **CI Success Rate:** ${status.ci.successRate}%\n`;
    report += `- **Evolution Score:** ${status.evolution.score}%\n`;
    report += `- **Active Alerts:** ${this.getAlerts().filter(a => !a.acknowledged).length}\n\n`;
    
    // Active Alerts
    const activeAlerts = this.getAlerts().filter(a => !a.acknowledged);
    if (activeAlerts.length > 0) {
      report += '## 🚨 Active Alerts\n\n';
      activeAlerts.forEach(alert => {
        const severity = alert.severity === 'critical' ? '🚨' : 
                        alert.severity === 'error' ? '❌' : 
                        alert.severity === 'warning' ? '⚠️' : 'ℹ️';
        
        report += `### ${severity} ${alert.title}\n`;
        report += `- **Type:** ${alert.type}\n`;
        report += `- **Severity:** ${alert.severity}\n`;
        report += `- **Description:** ${alert.description}\n`;
        report += `- **Time:** ${new Date(alert.timestamp).toISOString()}\n\n`;
      });
    }
    
    // Detailed Reports
    report += '## Maintenance Report\n\n';
    report += maintenanceReport + '\n\n';
    
    report += '## CI Report\n\n';
    report += ciReport + '\n\n';
    
    report += '## Evolution Report\n\n';
    report += evolutionReport + '\n\n';
    
    // Send report notifications
    if (this.config.notificationChannels.includes('email')) {
      await this.sendNotification('email', 'Periodic maintenance report generated');
    }
    
    return report;
  }

  private generateAlertId(): string {
    return `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  public updateConfig(newConfig: Partial<MaintenanceOrchestrationConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    // Update sub-system configs
    if (newConfig.maintenance) {
      this.maintenance.updateConfig(newConfig.maintenance);
    }
    
    if (newConfig.ci) {
      this.ci.updateConfig(newConfig.ci);
    }
    
    console.log('Maintenance orchestration configuration updated');
  }

  public getMaintenanceSystem(): DesignSystemMaintenance {
    return this.maintenance;
  }

  public getCISystem(): ContinuousIntegration {
    return this.ci;
  }

  public getEvolutionPlan(): EvolutionPlan {
    return this.evolution;
  }

  public cleanup(): void {
    this.stopOrchestration();
    this.maintenance.cleanup();
    this.ci.cleanup();
    this.evolution.cleanup();
    this.alerts.clear();
  }
}

export { MaintenanceOrchestrator, type MaintenanceOrchestrationConfig, type MaintenanceStatus, type MaintenanceAlert };