/**
 * Design System Evolution Plan
 * Manages long-term maintenance, updates, and evolution of the design system
 */

interface EvolutionMilestone {
  id: string;
  name: string;
  version: string;
  targetDate: number;
  status: 'planned' | 'in-progress' | 'completed' | 'delayed' | 'cancelled';
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: 'feature' | 'improvement' | 'maintenance' | 'breaking-change' | 'polish-business';
  description: string;
  requirements: string[];
  deliverables: string[];
  dependencies: string[];
  risks: EvolutionRisk[];
  progress: number; // 0-100
  assignedTeam?: string;
  estimatedEffort: number; // hours
  actualEffort?: number; // hours
}

interface EvolutionRisk {
  id: string;
  description: string;
  probability: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
  mitigation: string;
  status: 'identified' | 'mitigated' | 'occurred';
}

interface VersionPlan {
  version: string;
  type: 'major' | 'minor' | 'patch';
  releaseDate: number;
  milestones: string[];
  breakingChanges: string[];
  newFeatures: string[];
  improvements: string[];
  bugFixes: string[];
  polishBusinessEnhancements: string[];
  migrationGuide?: string;
}

interface MaintenanceSchedule {
  activity: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  nextDue: number;
  responsible: string;
  description: string;
  automatable: boolean;
  priority: 'critical' | 'high' | 'medium' | 'low';
}

interface TechnologyRoadmap {
  technology: string;
  currentVersion: string;
  targetVersion: string;
  migrationPlan: string;
  timeline: number;
  effort: number;
  risks: string[];
  benefits: string[];
}

class EvolutionPlan {
  private milestones: Map<string, EvolutionMilestone> = new Map();
  private versionPlans: Map<string, VersionPlan> = new Map();
  private maintenanceSchedule: MaintenanceSchedule[] = [];
  private technologyRoadmap: TechnologyRoadmap[] = [];
  private currentVersion: string = '1.0.0';

  constructor() {
    this.initializeEvolutionPlan();
  }

  private initializeEvolutionPlan(): void {
    this.createInitialMilestones();
    this.createVersionPlans();
    this.createMaintenanceSchedule();
    this.createTechnologyRoadmap();
  }

  private createInitialMilestones(): void {
    // Q1 2025 Milestones
    this.addMilestone({
      id: 'accessibility-enhancement-q1',
      name: 'Accessibility Enhancement Phase 1',
      version: '1.1.0',
      targetDate: new Date('2025-03-31').getTime(),
      status: 'planned',
      priority: 'high',
      category: 'improvement',
      description: 'Enhance accessibility features across all components to achieve WCAG 2.1 AAA compliance',
      requirements: [
        'All components must pass WCAG 2.1 AAA automated tests',
        'Screen reader compatibility for all interactive elements',
        'Keyboard navigation support for complex components',
        'High contrast mode support'
      ],
      deliverables: [
        'Updated accessibility documentation',
        'Enhanced screen reader support',
        'Improved keyboard navigation',
        'Accessibility testing automation'
      ],
      dependencies: [],
      risks: [
        {
          id: 'acc-risk-1',
          description: 'Complex components may require significant refactoring',
          probability: 'medium',
          impact: 'high',
          mitigation: 'Start with simpler components and build expertise',
          status: 'identified'
        }
      ],
      progress: 0,
      estimatedEffort: 320 // hours
    });

    this.addMilestone({
      id: 'polish-business-expansion-q1',
      name: 'Polish Business Components Expansion',
      version: '1.1.0',
      targetDate: new Date('2025-03-31').getTime(),
      status: 'planned',
      priority: 'high',
      category: 'polish-business',
      description: 'Expand Polish business-specific components and improve existing ones',
      requirements: [
        'Enhanced NIP validation with real-time API integration',
        'REGON and KRS number validation components',
        'Polish banking integration components',
        'Enhanced VAT calculation with current rates API'
      ],
      deliverables: [
        'REGON validator component',
        'KRS validator component',
        'Banking integration components',
        'Real-time VAT rates integration',
        'Polish business documentation'
      ],
      dependencies: [],
      risks: [
        {
          id: 'polish-risk-1',
          description: 'External API dependencies may be unreliable',
          probability: 'medium',
          impact: 'medium',
          mitigation: 'Implement fallback mechanisms and caching',
          status: 'identified'
        }
      ],
      progress: 0,
      estimatedEffort: 240 // hours
    });

    // Q2 2025 Milestones
    this.addMilestone({
      id: 'performance-optimization-q2',
      name: 'Performance Optimization Phase 2',
      version: '1.2.0',
      targetDate: new Date('2025-06-30').getTime(),
      status: 'planned',
      priority: 'medium',
      category: 'improvement',
      description: 'Advanced performance optimizations and bundle size reduction',
      requirements: [
        'Bundle size reduction by 30%',
        'Component render time improvement by 25%',
        'Lazy loading for all heavy components',
        'Advanced tree shaking implementation'
      ],
      deliverables: [
        'Optimized component bundles',
        'Advanced lazy loading system',
        'Performance monitoring dashboard',
        'Bundle analysis automation'
      ],
      dependencies: ['accessibility-enhancement-q1'],
      risks: [
        {
          id: 'perf-risk-1',
          description: 'Aggressive optimizations may break existing functionality',
          probability: 'low',
          impact: 'high',
          mitigation: 'Comprehensive testing and gradual rollout',
          status: 'identified'
        }
      ],
      progress: 0,
      estimatedEffort: 200 // hours
    });

    // Q3 2025 Milestones
    this.addMilestone({
      id: 'react-19-migration-q3',
      name: 'React 19 Migration',
      version: '2.0.0',
      targetDate: new Date('2025-09-30').getTime(),
      status: 'planned',
      priority: 'medium',
      category: 'breaking-change',
      description: 'Migrate design system to React 19 and leverage new features',
      requirements: [
        'Full compatibility with React 19',
        'Leverage new React 19 features (Server Components, etc.)',
        'Update all dependencies',
        'Maintain backward compatibility where possible'
      ],
      deliverables: [
        'React 19 compatible components',
        'Migration guide for consumers',
        'Updated documentation',
        'Automated migration tools'
      ],
      dependencies: ['performance-optimization-q2'],
      risks: [
        {
          id: 'react-risk-1',
          description: 'Breaking changes in React 19 may require extensive refactoring',
          probability: 'high',
          impact: 'high',
          mitigation: 'Early testing with React 19 beta versions',
          status: 'identified'
        }
      ],
      progress: 0,
      estimatedEffort: 400 // hours
    });

    // Q4 2025 Milestones
    this.addMilestone({
      id: 'ai-integration-q4',
      name: 'AI-Powered Design System Features',
      version: '2.1.0',
      targetDate: new Date('2025-12-31').getTime(),
      status: 'planned',
      priority: 'low',
      category: 'feature',
      description: 'Integrate AI-powered features for enhanced user experience',
      requirements: [
        'AI-powered component suggestions',
        'Automated accessibility improvements',
        'Smart form validation',
        'Intelligent Polish business data processing'
      ],
      deliverables: [
        'AI component recommendation system',
        'Automated accessibility scanner',
        'Smart validation components',
        'AI-powered Polish business helpers'
      ],
      dependencies: ['react-19-migration-q3'],
      risks: [
        {
          id: 'ai-risk-1',
          description: 'AI features may be unreliable or inconsistent',
          probability: 'medium',
          impact: 'medium',
          mitigation: 'Implement as optional enhancements with fallbacks',
          status: 'identified'
        }
      ],
      progress: 0,
      estimatedEffort: 320 // hours
    });
  }

  private createVersionPlans(): void {
    // Version 1.1.0 - Q1 2025
    this.addVersionPlan({
      version: '1.1.0',
      type: 'minor',
      releaseDate: new Date('2025-03-31').getTime(),
      milestones: ['accessibility-enhancement-q1', 'polish-business-expansion-q1'],
      breakingChanges: [],
      newFeatures: [
        'REGON validator component',
        'KRS validator component',
        'Enhanced screen reader support',
        'High contrast mode'
      ],
      improvements: [
        'Better keyboard navigation',
        'Improved accessibility documentation',
        'Enhanced NIP validation'
      ],
      bugFixes: [
        'Fix focus management in modal components',
        'Resolve color contrast issues',
        'Fix Polish date formatting edge cases'
      ],
      polishBusinessEnhancements: [
        'Real-time VAT rates integration',
        'Banking integration components',
        'Enhanced business number validation'
      ]
    });

    // Version 1.2.0 - Q2 2025
    this.addVersionPlan({
      version: '1.2.0',
      type: 'minor',
      releaseDate: new Date('2025-06-30').getTime(),
      milestones: ['performance-optimization-q2'],
      breakingChanges: [],
      newFeatures: [
        'Advanced lazy loading system',
        'Performance monitoring dashboard',
        'Bundle analysis automation'
      ],
      improvements: [
        '30% bundle size reduction',
        '25% render performance improvement',
        'Enhanced tree shaking'
      ],
      bugFixes: [
        'Fix memory leaks in heavy components',
        'Resolve bundle splitting issues',
        'Fix performance regression in tables'
      ],
      polishBusinessEnhancements: [
        'Optimized Polish business component performance',
        'Cached validation results'
      ]
    });

    // Version 2.0.0 - Q3 2025
    this.addVersionPlan({
      version: '2.0.0',
      type: 'major',
      releaseDate: new Date('2025-09-30').getTime(),
      milestones: ['react-19-migration-q3'],
      breakingChanges: [
        'React 19 minimum requirement',
        'Deprecated component APIs removed',
        'Updated TypeScript interfaces'
      ],
      newFeatures: [
        'React 19 Server Components support',
        'Enhanced concurrent features',
        'New React 19 hooks integration'
      ],
      improvements: [
        'Better server-side rendering',
        'Improved hydration performance',
        'Enhanced developer experience'
      ],
      bugFixes: [
        'Fix React 19 compatibility issues',
        'Resolve SSR hydration mismatches'
      ],
      polishBusinessEnhancements: [
        'Server-side Polish business validation',
        'Enhanced SSR for Polish components'
      ],
      migrationGuide: 'docs/migration/v2.0.0-migration-guide.md'
    });
  }

  private createMaintenanceSchedule(): void {
    this.maintenanceSchedule = [
      {
        activity: 'Security vulnerability scan',
        frequency: 'daily',
        nextDue: Date.now() + 24 * 60 * 60 * 1000,
        responsible: 'DevOps Team',
        description: 'Automated scan for security vulnerabilities in dependencies',
        automatable: true,
        priority: 'critical'
      },
      {
        activity: 'Performance metrics review',
        frequency: 'weekly',
        nextDue: Date.now() + 7 * 24 * 60 * 60 * 1000,
        responsible: 'Performance Team',
        description: 'Review performance metrics and identify regressions',
        automatable: false,
        priority: 'high'
      },
      {
        activity: 'Dependency updates',
        frequency: 'weekly',
        nextDue: Date.now() + 7 * 24 * 60 * 60 * 1000,
        responsible: 'Development Team',
        description: 'Update dependencies to latest stable versions',
        automatable: true,
        priority: 'medium'
      },
      {
        activity: 'Documentation review',
        frequency: 'monthly',
        nextDue: Date.now() + 30 * 24 * 60 * 60 * 1000,
        responsible: 'Documentation Team',
        description: 'Review and update component documentation',
        automatable: false,
        priority: 'medium'
      },
      {
        activity: 'Accessibility audit',
        frequency: 'monthly',
        nextDue: Date.now() + 30 * 24 * 60 * 60 * 1000,
        responsible: 'Accessibility Team',
        description: 'Comprehensive accessibility audit of all components',
        automatable: true,
        priority: 'high'
      },
      {
        activity: 'Polish business compliance review',
        frequency: 'quarterly',
        nextDue: Date.now() + 90 * 24 * 60 * 60 * 1000,
        responsible: 'Business Team',
        description: 'Review Polish business requirements and regulations',
        automatable: false,
        priority: 'high'
      },
      {
        activity: 'Technology roadmap review',
        frequency: 'quarterly',
        nextDue: Date.now() + 90 * 24 * 60 * 60 * 1000,
        responsible: 'Architecture Team',
        description: 'Review and update technology roadmap',
        automatable: false,
        priority: 'medium'
      },
      {
        activity: 'Design system strategy review',
        frequency: 'yearly',
        nextDue: Date.now() + 365 * 24 * 60 * 60 * 1000,
        responsible: 'Leadership Team',
        description: 'Strategic review of design system direction and goals',
        automatable: false,
        priority: 'high'
      }
    ];
  }

  private createTechnologyRoadmap(): void {
    this.technologyRoadmap = [
      {
        technology: 'React',
        currentVersion: '18.2.0',
        targetVersion: '19.0.0',
        migrationPlan: 'Gradual migration with backward compatibility',
        timeline: new Date('2025-09-30').getTime(),
        effort: 400,
        risks: [
          'Breaking changes in React 19',
          'Third-party library compatibility',
          'Performance regressions'
        ],
        benefits: [
          'Better server-side rendering',
          'Improved concurrent features',
          'Enhanced developer experience'
        ]
      },
      {
        technology: 'TypeScript',
        currentVersion: '4.9.0',
        targetVersion: '5.2.0',
        migrationPlan: 'Update type definitions and fix compatibility issues',
        timeline: new Date('2025-06-30').getTime(),
        effort: 80,
        risks: [
          'Type definition changes',
          'Stricter type checking'
        ],
        benefits: [
          'Better type safety',
          'Improved IDE support',
          'New language features'
        ]
      },
      {
        technology: 'Webpack',
        currentVersion: '5.75.0',
        targetVersion: '5.90.0',
        migrationPlan: 'Update configuration and optimize build process',
        timeline: new Date('2025-03-31').getTime(),
        effort: 40,
        risks: [
          'Build configuration changes',
          'Plugin compatibility'
        ],
        benefits: [
          'Better build performance',
          'Improved tree shaking',
          'Enhanced optimization'
        ]
      },
      {
        technology: 'Storybook',
        currentVersion: '7.0.0',
        targetVersion: '8.0.0',
        migrationPlan: 'Update stories and configuration',
        timeline: new Date('2025-12-31').getTime(),
        effort: 120,
        risks: [
          'Story format changes',
          'Addon compatibility'
        ],
        benefits: [
          'Better documentation experience',
          'Enhanced testing integration',
          'Improved performance'
        ]
      }
    ];
  }

  private addMilestone(milestone: EvolutionMilestone): void {
    this.milestones.set(milestone.id, milestone);
  }

  private addVersionPlan(versionPlan: VersionPlan): void {
    this.versionPlans.set(versionPlan.version, versionPlan);
  }

  public getMilestones(): EvolutionMilestone[] {
    return Array.from(this.milestones.values());
  }

  public getMilestone(id: string): EvolutionMilestone | undefined {
    return this.milestones.get(id);
  }

  public updateMilestoneProgress(id: string, progress: number): void {
    const milestone = this.milestones.get(id);
    if (milestone) {
      milestone.progress = Math.max(0, Math.min(100, progress));
      
      if (progress >= 100 && milestone.status !== 'completed') {
        milestone.status = 'completed';
      } else if (progress > 0 && milestone.status === 'planned') {
        milestone.status = 'in-progress';
      }
    }
  }

  public getVersionPlans(): VersionPlan[] {
    return Array.from(this.versionPlans.values());
  }

  public getVersionPlan(version: string): VersionPlan | undefined {
    return this.versionPlans.get(version);
  }

  public getMaintenanceSchedule(): MaintenanceSchedule[] {
    return [...this.maintenanceSchedule];
  }

  public getTechnologyRoadmap(): TechnologyRoadmap[] {
    return [...this.technologyRoadmap];
  }

  public getUpcomingMilestones(days: number = 90): EvolutionMilestone[] {
    const cutoffDate = Date.now() + (days * 24 * 60 * 60 * 1000);
    
    return this.getMilestones()
      .filter(milestone => 
        milestone.targetDate <= cutoffDate && 
        milestone.status !== 'completed' && 
        milestone.status !== 'cancelled'
      )
      .sort((a, b) => a.targetDate - b.targetDate);
  }

  public getOverdueMilestones(): EvolutionMilestone[] {
    const now = Date.now();
    
    return this.getMilestones()
      .filter(milestone => 
        milestone.targetDate < now && 
        milestone.status !== 'completed' && 
        milestone.status !== 'cancelled'
      )
      .sort((a, b) => a.targetDate - b.targetDate);
  }

  public getDueMaintenance(days: number = 7): MaintenanceSchedule[] {
    const cutoffDate = Date.now() + (days * 24 * 60 * 60 * 1000);
    
    return this.maintenanceSchedule
      .filter(activity => activity.nextDue <= cutoffDate)
      .sort((a, b) => a.nextDue - b.nextDue);
  }

  public calculateProjectHealth(): {
    overallScore: number;
    milestonesOnTrack: number;
    milestonesDelayed: number;
    maintenanceCompliance: number;
    technologyDebt: number;
  } {
    const milestones = this.getMilestones();
    const totalMilestones = milestones.length;
    
    // Calculate milestone health
    const onTrackMilestones = milestones.filter(m => {
      if (m.status === 'completed') return true;
      if (m.status === 'cancelled') return false;
      
      const timeRemaining = m.targetDate - Date.now();
      const progressExpected = timeRemaining > 0 ? 
        Math.max(0, 100 - (timeRemaining / (30 * 24 * 60 * 60 * 1000)) * 20) : 100;
      
      return m.progress >= progressExpected * 0.8; // 80% of expected progress
    }).length;
    
    const delayedMilestones = milestones.filter(m => {
      if (m.status === 'completed' || m.status === 'cancelled') return false;
      return m.targetDate < Date.now();
    }).length;
    
    // Calculate maintenance compliance
    const overdueMaintenance = this.getDueMaintenance(0).length;
    const totalMaintenance = this.maintenanceSchedule.length;
    const maintenanceCompliance = totalMaintenance > 0 ? 
      ((totalMaintenance - overdueMaintenance) / totalMaintenance) * 100 : 100;
    
    // Calculate technology debt
    const outdatedTech = this.technologyRoadmap.filter(tech => {
      const isOverdue = tech.timeline < Date.now();
      const versionGap = this.calculateVersionGap(tech.currentVersion, tech.targetVersion);
      return isOverdue || versionGap > 2;
    }).length;
    
    const technologyDebt = this.technologyRoadmap.length > 0 ?
      ((this.technologyRoadmap.length - outdatedTech) / this.technologyRoadmap.length) * 100 : 100;
    
    // Calculate overall score
    const overallScore = (
      (onTrackMilestones / Math.max(1, totalMilestones)) * 40 +
      (maintenanceCompliance / 100) * 30 +
      (technologyDebt / 100) * 30
    );
    
    return {
      overallScore: Math.round(overallScore),
      milestonesOnTrack: onTrackMilestones,
      milestonesDelayed: delayedMilestones,
      maintenanceCompliance: Math.round(maintenanceCompliance),
      technologyDebt: Math.round(technologyDebt)
    };
  }

  private calculateVersionGap(current: string, target: string): number {
    // Simple version gap calculation (major.minor.patch)
    const currentParts = current.split('.').map(Number);
    const targetParts = target.split('.').map(Number);
    
    const majorGap = targetParts[0] - currentParts[0];
    const minorGap = targetParts[1] - currentParts[1];
    
    return majorGap * 10 + minorGap; // Weight major versions more heavily
  }

  public generateEvolutionReport(): string {
    const health = this.calculateProjectHealth();
    const upcomingMilestones = this.getUpcomingMilestones();
    const overdueMilestones = this.getOverdueMilestones();
    const dueMaintenance = this.getDueMaintenance();
    
    let report = '# Design System Evolution Plan Report\n\n';
    report += `Generated: ${new Date().toISOString()}\n\n`;
    
    // Executive Summary
    report += '## Executive Summary\n\n';
    report += `- **Overall Health Score:** ${health.overallScore}/100\n`;
    report += `- **Milestones On Track:** ${health.milestonesOnTrack}\n`;
    report += `- **Delayed Milestones:** ${health.milestonesDelayed}\n`;
    report += `- **Maintenance Compliance:** ${health.maintenanceCompliance}%\n`;
    report += `- **Technology Debt Score:** ${health.technologyDebt}%\n\n`;
    
    // Upcoming Milestones
    report += '## Upcoming Milestones (Next 90 Days)\n\n';
    if (upcomingMilestones.length === 0) {
      report += 'No milestones due in the next 90 days.\n\n';
    } else {
      upcomingMilestones.forEach(milestone => {
        const daysUntil = Math.ceil((milestone.targetDate - Date.now()) / (24 * 60 * 60 * 1000));
        report += `### ${milestone.name} (${milestone.version})\n`;
        report += `- **Due:** ${daysUntil} days (${new Date(milestone.targetDate).toDateString()})\n`;
        report += `- **Progress:** ${milestone.progress}%\n`;
        report += `- **Priority:** ${milestone.priority}\n`;
        report += `- **Status:** ${milestone.status}\n\n`;
      });
    }
    
    // Overdue Milestones
    if (overdueMilestones.length > 0) {
      report += '## ⚠️ Overdue Milestones\n\n';
      overdueMilestones.forEach(milestone => {
        const daysOverdue = Math.ceil((Date.now() - milestone.targetDate) / (24 * 60 * 60 * 1000));
        report += `### ${milestone.name} (${milestone.version})\n`;
        report += `- **Overdue by:** ${daysOverdue} days\n`;
        report += `- **Progress:** ${milestone.progress}%\n`;
        report += `- **Priority:** ${milestone.priority}\n\n`;
      });
    }
    
    // Due Maintenance
    if (dueMaintenance.length > 0) {
      report += '## 🔧 Due Maintenance Activities\n\n';
      dueMaintenance.forEach(activity => {
        const daysUntil = Math.ceil((activity.nextDue - Date.now()) / (24 * 60 * 60 * 1000));
        const status = daysUntil < 0 ? 'OVERDUE' : 'DUE SOON';
        report += `- **${activity.activity}** (${status})\n`;
        report += `  - Responsible: ${activity.responsible}\n`;
        report += `  - Priority: ${activity.priority}\n`;
        report += `  - Automatable: ${activity.automatable ? 'Yes' : 'No'}\n\n`;
      });
    }
    
    // Technology Roadmap
    report += '## Technology Roadmap\n\n';
    this.technologyRoadmap.forEach(tech => {
      const daysUntil = Math.ceil((tech.timeline - Date.now()) / (24 * 60 * 60 * 1000));
      const status = daysUntil < 0 ? 'OVERDUE' : `${daysUntil} days`;
      
      report += `### ${tech.technology}\n`;
      report += `- **Current:** ${tech.currentVersion} → **Target:** ${tech.targetVersion}\n`;
      report += `- **Timeline:** ${status}\n`;
      report += `- **Effort:** ${tech.effort} hours\n\n`;
    });
    
    // Version Plans
    report += '## Upcoming Releases\n\n';
    const sortedVersions = this.getVersionPlans()
      .sort((a, b) => a.releaseDate - b.releaseDate)
      .slice(0, 3);
    
    sortedVersions.forEach(version => {
      const daysUntil = Math.ceil((version.releaseDate - Date.now()) / (24 * 60 * 60 * 1000));
      
      report += `### Version ${version.version} (${version.type})\n`;
      report += `- **Release Date:** ${daysUntil} days (${new Date(version.releaseDate).toDateString()})\n`;
      report += `- **New Features:** ${version.newFeatures.length}\n`;
      report += `- **Improvements:** ${version.improvements.length}\n`;
      report += `- **Breaking Changes:** ${version.breakingChanges.length}\n`;
      report += `- **Polish Business Enhancements:** ${version.polishBusinessEnhancements.length}\n\n`;
    });
    
    // Recommendations
    report += '## Recommendations\n\n';
    
    if (health.overallScore < 70) {
      report += '- 🚨 **Critical:** Overall health score is below 70%. Review delayed milestones and overdue maintenance.\n';
    }
    
    if (health.milestonesDelayed > 0) {
      report += `- ⚠️ **High:** ${health.milestonesDelayed} milestone(s) are delayed. Consider resource reallocation.\n`;
    }
    
    if (health.maintenanceCompliance < 80) {
      report += '- ⚠️ **Medium:** Maintenance compliance is below 80%. Schedule overdue activities.\n';
    }
    
    if (health.technologyDebt < 70) {
      report += '- ⚠️ **Medium:** Technology debt is high. Prioritize technology updates.\n';
    }
    
    if (dueMaintenance.filter(m => m.priority === 'critical').length > 0) {
      report += '- 🚨 **Critical:** Critical maintenance activities are due. Address immediately.\n';
    }
    
    return report;
  }

  public updateCurrentVersion(version: string): void {
    this.currentVersion = version;
  }

  public getCurrentVersion(): string {
    return this.currentVersion;
  }

  public addCustomMilestone(milestone: Omit<EvolutionMilestone, 'id'>): string {
    const id = `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.addMilestone({ ...milestone, id });
    return id;
  }

  public removeMilestone(id: string): boolean {
    return this.milestones.delete(id);
  }

  public cleanup(): void {
    this.milestones.clear();
    this.versionPlans.clear();
    this.maintenanceSchedule.length = 0;
    this.technologyRoadmap.length = 0;
  }
}

export { EvolutionPlan, type EvolutionMilestone, type VersionPlan, type MaintenanceSchedule, type TechnologyRoadmap };