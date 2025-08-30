/**
 * Migration progress tracking for design system integration
 * Monitors the progress of migrating from old components to new design system components
 */

interface MigrationTask {
  id: string;
  componentName: string;
  oldComponent: string;
  newComponent: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'blocked';
  progress: number; // 0-100
  startDate?: number;
  completedDate?: number;
  blockers: string[];
  files: string[];
  estimatedEffort: number; // hours
  actualEffort?: number; // hours
}

interface MigrationMetrics {
  totalTasks: number;
  completedTasks: number;
  inProgressTasks: number;
  blockedTasks: number;
  overallProgress: number;
  estimatedCompletion: number; // timestamp
  velocity: number; // tasks per day
}

interface ComponentMigrationStatus {
  componentName: string;
  totalInstances: number;
  migratedInstances: number;
  remainingInstances: number;
  migrationRate: number; // percentage
  lastActivity: number;
  files: {
    total: number;
    migrated: number;
    remaining: string[];
  };
}

class MigrationProgressTracker {
  private tasks: Map<string, MigrationTask> = new Map();
  private componentStatus: Map<string, ComponentMigrationStatus> = new Map();
  private completionHistory: Array<{ taskId: string; timestamp: number }> = [];
  private isTracking: boolean = false;

  constructor() {
    this.loadMigrationPlan();
    this.initializeTracking();
  }

  private loadMigrationPlan(): void {
    // Load migration tasks from configuration or API
    const migrationPlan = this.getDefaultMigrationPlan();
    
    migrationPlan.forEach(task => {
      this.tasks.set(task.id, task);
    });
  }

  private getDefaultMigrationPlan(): MigrationTask[] {
    return [
      {
        id: 'button-migration',
        componentName: 'Button',
        oldComponent: 'LegacyButton',
        newComponent: 'DSButton',
        status: 'completed',
        progress: 100,
        blockers: [],
        files: ['src/components/Button.js', 'src/pages/*.js'],
        estimatedEffort: 8,
        actualEffort: 6
      },
      {
        id: 'input-migration',
        componentName: 'Input',
        oldComponent: 'FormInput',
        newComponent: 'DSInput',
        status: 'completed',
        progress: 100,
        blockers: [],
        files: ['src/components/Input.js', 'src/forms/*.js'],
        estimatedEffort: 12,
        actualEffort: 10
      },
      {
        id: 'table-migration',
        componentName: 'Table',
        oldComponent: 'DataTable',
        newComponent: 'DSTable',
        status: 'completed',
        progress: 100,
        blockers: [],
        files: ['src/components/Table.js', 'src/pages/invoices/*.js'],
        estimatedEffort: 16,
        actualEffort: 14
      },
      {
        id: 'form-migration',
        componentName: 'Form',
        oldComponent: 'CustomForm',
        newComponent: 'DSForm',
        status: 'completed',
        progress: 100,
        blockers: [],
        files: ['src/components/Form.js', 'src/forms/*.js'],
        estimatedEffort: 20,
        actualEffort: 18
      },
      {
        id: 'card-migration',
        componentName: 'Card',
        oldComponent: 'InfoCard',
        newComponent: 'DSCard',
        status: 'completed',
        progress: 100,
        blockers: [],
        files: ['src/components/Card.js', 'src/pages/dashboard/*.js'],
        estimatedEffort: 10,
        actualEffort: 8
      },
      {
        id: 'modal-migration',
        componentName: 'Modal',
        oldComponent: 'PopupModal',
        newComponent: 'DSModal',
        status: 'completed',
        progress: 100,
        blockers: [],
        files: ['src/components/Modal.js', 'src/pages/*.js'],
        estimatedEffort: 14,
        actualEffort: 12
      },
      {
        id: 'navigation-migration',
        componentName: 'Navigation',
        oldComponent: 'SideNav',
        newComponent: 'DSNavigation',
        status: 'completed',
        progress: 100,
        blockers: [],
        files: ['src/components/Navigation.js', 'src/layouts/*.js'],
        estimatedEffort: 18,
        actualEffort: 16
      },
      {
        id: 'polish-business-integration',
        componentName: 'PolishBusinessComponents',
        oldComponent: 'CustomValidators',
        newComponent: 'DSPolishBusiness',
        status: 'completed',
        progress: 100,
        blockers: [],
        files: ['src/components/business/*.js', 'src/forms/invoice/*.js'],
        estimatedEffort: 24,
        actualEffort: 22
      }
    ];
  }

  private initializeTracking(): void {
    if (typeof window === 'undefined') return;

    // Track file changes through build system integration
    this.setupBuildIntegration();
    
    // Track component usage changes
    this.setupUsageTracking();
    
    // Load historical data
    this.loadHistoricalData();
  }

  private setupBuildIntegration(): void {
    // This would integrate with webpack or build system to track file changes
    // For now, we'll simulate with periodic checks
    if (this.isTracking) {
      setInterval(() => {
        this.checkMigrationProgress();
      }, 30000); // Check every 30 seconds
    }
  }

  private setupUsageTracking(): void {
    // Monitor DOM for old vs new component usage
    if ('MutationObserver' in window) {
      const observer = new MutationObserver(() => {
        this.updateComponentUsageMetrics();
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class']
      });
    }
  }

  private loadHistoricalData(): void {
    // Load completion history from localStorage or API
    const stored = localStorage.getItem('migration-progress-history');
    if (stored) {
      try {
        this.completionHistory = JSON.parse(stored);
      } catch (error) {
        console.warn('Failed to load migration history:', error);
      }
    }
  }

  private saveHistoricalData(): void {
    try {
      localStorage.setItem('migration-progress-history', JSON.stringify(this.completionHistory));
    } catch (error) {
      console.warn('Failed to save migration history:', error);
    }
  }

  public startTracking(): void {
    this.isTracking = true;
    this.setupBuildIntegration();
  }

  public stopTracking(): void {
    this.isTracking = false;
  }

  public updateTaskStatus(taskId: string, status: MigrationTask['status'], progress?: number): void {
    const task = this.tasks.get(taskId);
    if (!task) return;

    const oldStatus = task.status;
    task.status = status;
    
    if (progress !== undefined) {
      task.progress = Math.max(0, Math.min(100, progress));
    }

    // Track status changes
    if (status === 'in_progress' && oldStatus === 'not_started') {
      task.startDate = Date.now();
    }

    if (status === 'completed' && oldStatus !== 'completed') {
      task.completedDate = Date.now();
      this.completionHistory.push({
        taskId,
        timestamp: Date.now()
      });
      this.saveHistoricalData();
    }

    // Update component status
    this.updateComponentStatus(task.componentName);
  }

  public addBlocker(taskId: string, blocker: string): void {
    const task = this.tasks.get(taskId);
    if (task && !task.blockers.includes(blocker)) {
      task.blockers.push(blocker);
      
      if (task.status !== 'blocked' && task.blockers.length > 0) {
        task.status = 'blocked';
      }
    }
  }

  public removeBlocker(taskId: string, blocker: string): void {
    const task = this.tasks.get(taskId);
    if (task) {
      task.blockers = task.blockers.filter(b => b !== blocker);
      
      if (task.status === 'blocked' && task.blockers.length === 0) {
        task.status = task.progress > 0 ? 'in_progress' : 'not_started';
      }
    }
  }

  public recordActualEffort(taskId: string, hours: number): void {
    const task = this.tasks.get(taskId);
    if (task) {
      task.actualEffort = hours;
    }
  }

  private updateComponentStatus(componentName: string): void {
    const relatedTasks = Array.from(this.tasks.values())
      .filter(task => task.componentName === componentName);
    
    if (relatedTasks.length === 0) return;

    const totalInstances = relatedTasks.reduce((sum, task) => sum + task.files.length, 0);
    const migratedInstances = relatedTasks.reduce((sum, task) => {
      return sum + Math.floor((task.progress / 100) * task.files.length);
    }, 0);

    const status: ComponentMigrationStatus = {
      componentName,
      totalInstances,
      migratedInstances,
      remainingInstances: totalInstances - migratedInstances,
      migrationRate: totalInstances > 0 ? (migratedInstances / totalInstances) * 100 : 0,
      lastActivity: Math.max(...relatedTasks.map(task => task.completedDate || task.startDate || 0)),
      files: {
        total: totalInstances,
        migrated: migratedInstances,
        remaining: relatedTasks
          .filter(task => task.progress < 100)
          .flatMap(task => task.files)
      }
    };

    this.componentStatus.set(componentName, status);
  }

  private checkMigrationProgress(): void {
    // This would check actual file system or build output
    // For now, we'll simulate progress updates
    this.tasks.forEach((task, taskId) => {
      if (task.status === 'in_progress' && Math.random() > 0.8) {
        // Simulate progress
        const newProgress = Math.min(100, task.progress + Math.random() * 10);
        this.updateTaskStatus(taskId, task.status, newProgress);
        
        if (newProgress >= 100) {
          this.updateTaskStatus(taskId, 'completed');
        }
      }
    });
  }

  private updateComponentUsageMetrics(): void {
    // Count old vs new component usage in DOM
    const oldComponents = document.querySelectorAll('[class*="legacy-"], [class*="old-"]');
    const newComponents = document.querySelectorAll('[class*="ds-"], [data-ds-component]');
    
    // Update metrics based on actual usage
    this.componentStatus.forEach((status, componentName) => {
      // This is a simplified example - in practice, you'd have more sophisticated detection
      const oldUsage = Array.from(oldComponents).filter(el => 
        el.className.toLowerCase().includes(componentName.toLowerCase())
      ).length;
      
      const newUsage = Array.from(newComponents).filter(el => 
        el.className.toLowerCase().includes(componentName.toLowerCase()) ||
        el.getAttribute('data-ds-component')?.toLowerCase().includes(componentName.toLowerCase())
      ).length;
      
      if (oldUsage + newUsage > 0) {
        status.migrationRate = (newUsage / (oldUsage + newUsage)) * 100;
        status.lastActivity = Date.now();
      }
    });
  }

  public getMigrationMetrics(): MigrationMetrics {
    const tasks = Array.from(this.tasks.values());
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(task => task.status === 'completed').length;
    const inProgressTasks = tasks.filter(task => task.status === 'in_progress').length;
    const blockedTasks = tasks.filter(task => task.status === 'blocked').length;
    
    const overallProgress = totalTasks > 0 ? 
      tasks.reduce((sum, task) => sum + task.progress, 0) / totalTasks : 0;
    
    // Calculate velocity (tasks completed per day)
    const recentCompletions = this.completionHistory.filter(
      completion => Date.now() - completion.timestamp < 7 * 24 * 60 * 60 * 1000 // Last 7 days
    );
    const velocity = recentCompletions.length / 7;
    
    // Estimate completion date
    const remainingTasks = totalTasks - completedTasks;
    const estimatedDays = velocity > 0 ? remainingTasks / velocity : 0;
    const estimatedCompletion = Date.now() + (estimatedDays * 24 * 60 * 60 * 1000);
    
    return {
      totalTasks,
      completedTasks,
      inProgressTasks,
      blockedTasks,
      overallProgress,
      estimatedCompletion,
      velocity
    };
  }

  public getComponentMigrationStatus(): ComponentMigrationStatus[] {
    return Array.from(this.componentStatus.values());
  }

  public getMigrationTasks(): MigrationTask[] {
    return Array.from(this.tasks.values());
  }

  public getBlockedTasks(): MigrationTask[] {
    return Array.from(this.tasks.values()).filter(task => task.status === 'blocked');
  }

  public generateProgressReport(): {
    metrics: MigrationMetrics;
    componentStatus: ComponentMigrationStatus[];
    blockedTasks: MigrationTask[];
    recommendations: string[];
    timeline: Array<{ date: string; completedTasks: number }>;
  } {
    const metrics = this.getMigrationMetrics();
    const componentStatus = this.getComponentMigrationStatus();
    const blockedTasks = this.getBlockedTasks();
    
    // Generate recommendations
    const recommendations: string[] = [];
    
    if (metrics.velocity < 1) {
      recommendations.push('Migration velocity is low - consider allocating more resources');
    }
    
    if (blockedTasks.length > 0) {
      recommendations.push(`${blockedTasks.length} tasks are blocked - resolve blockers to improve progress`);
    }
    
    const staleComponents = componentStatus.filter(status => 
      Date.now() - status.lastActivity > 14 * 24 * 60 * 60 * 1000 // 14 days
    );
    
    if (staleComponents.length > 0) {
      recommendations.push(`${staleComponents.length} components have stale migration status`);
    }
    
    if (metrics.overallProgress < 50) {
      recommendations.push('Migration is less than 50% complete - prioritize remaining tasks');
    }
    
    // Generate timeline
    const timeline = this.generateTimeline();
    
    return {
      metrics,
      componentStatus,
      blockedTasks,
      recommendations,
      timeline
    };
  }

  private generateTimeline(): Array<{ date: string; completedTasks: number }> {
    const timeline: Array<{ date: string; completedTasks: number }> = [];
    const now = new Date();
    
    // Generate last 30 days
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      const completedTasks = this.completionHistory.filter(completion => {
        const completionDate = new Date(completion.timestamp);
        return completionDate.toISOString().split('T')[0] === dateStr;
      }).length;
      
      timeline.push({ date: dateStr, completedTasks });
    }
    
    return timeline;
  }

  public cleanup(): void {
    this.stopTracking();
    this.saveHistoricalData();
  }
}

export { MigrationProgressTracker, type MigrationTask, type MigrationMetrics, type ComponentMigrationStatus };