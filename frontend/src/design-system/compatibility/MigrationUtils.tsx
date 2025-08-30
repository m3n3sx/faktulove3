import React from 'react';
import { MigrationStatus, MigrationConfig, useMigrationTracker } from './ComponentWrapper';

/**
 * Migration report data structure
 */
export interface MigrationReport {
  componentName: string;
  status: MigrationStatus;
  config: MigrationConfig;
  errors: string[];
  lastUpdated: Date;
}

/**
 * Migration analysis results
 */
export interface MigrationAnalysis {
  totalComponents: number;
  completedMigrations: number;
  inProgressMigrations: number;
  notStartedMigrations: number;
  deprecatedComponents: number;
  completionPercentage: number;
  estimatedCompletionDate?: Date;
  criticalIssues: string[];
  recommendations: string[];
}

/**
 * Utility class for migration management
 */
export class MigrationUtils {
  private static instance: MigrationUtils;
  
  static getInstance(): MigrationUtils {
    if (!MigrationUtils.instance) {
      MigrationUtils.instance = new MigrationUtils();
    }
    return MigrationUtils.instance;
  }
  
  /**
   * Generate comprehensive migration report
   */
  generateReport(): MigrationReport[] {
    const tracker = useMigrationTracker();
    const migrations = tracker.getAllMigrations();
    const reports: MigrationReport[] = [];
    
    migrations.forEach((config, componentName) => {
      const errors = tracker.getErrors(componentName);
      reports.push({
        componentName,
        status: config.status,
        config,
        errors: errors.map(e => e.message),
        lastUpdated: new Date(),
      });
    });
    
    return reports.sort((a, b) => a.componentName.localeCompare(b.componentName));
  }
  
  /**
   * Analyze migration progress and provide insights
   */
  analyzeMigrationProgress(): MigrationAnalysis {
    const tracker = useMigrationTracker();
    const stats = tracker.getStatistics();
    const migrations = tracker.getAllMigrations();
    
    const completionPercentage = stats.total > 0 
      ? Math.round((stats.completed / stats.total) * 100)
      : 0;
    
    // Estimate completion date based on current progress
    let estimatedCompletionDate: Date | undefined;
    if (stats.in_progress > 0) {
      const avgDaysPerMigration = 3; // Estimate
      const remainingDays = (stats.not_started + stats.in_progress) * avgDaysPerMigration;
      estimatedCompletionDate = new Date();
      estimatedCompletionDate.setDate(estimatedCompletionDate.getDate() + remainingDays);
    }
    
    // Identify critical issues
    const criticalIssues: string[] = [];
    migrations.forEach((config, componentName) => {
      const errors = tracker.getErrors(componentName);
      if (errors.length > 0) {
        criticalIssues.push(`${componentName}: ${errors.length} error(s)`);
      }
      if (config.status === 'deprecated') {
        criticalIssues.push(`${componentName}: Component is deprecated`);
      }
    });
    
    // Generate recommendations
    const recommendations: string[] = [];
    if (stats.not_started > 0) {
      recommendations.push(`Start migration for ${stats.not_started} pending components`);
    }
    if (stats.deprecated > 0) {
      recommendations.push(`Update ${stats.deprecated} deprecated components`);
    }
    if (criticalIssues.length > 0) {
      recommendations.push(`Address ${criticalIssues.length} critical issues`);
    }
    if (completionPercentage > 80) {
      recommendations.push('Consider final testing and cleanup phase');
    }
    
    return {
      totalComponents: stats.total,
      completedMigrations: stats.completed,
      inProgressMigrations: stats.in_progress,
      notStartedMigrations: stats.not_started,
      deprecatedComponents: stats.deprecated,
      completionPercentage,
      estimatedCompletionDate,
      criticalIssues,
      recommendations,
    };
  }
  
  /**
   * Export migration data for external tools
   */
  exportMigrationData(): string {
    const report = this.generateReport();
    const analysis = this.analyzeMigrationProgress();
    
    const exportData = {
      timestamp: new Date().toISOString(),
      analysis,
      components: report,
    };
    
    return JSON.stringify(exportData, null, 2);
  }
  
  /**
   * Validate migration configuration
   */
  validateMigrationConfig(componentName: string, config: MigrationConfig): string[] {
    const issues: string[] = [];
    
    if (!config.status) {
      issues.push('Migration status is required');
    }
    
    if (config.status === 'in_progress' && !config.targetDate) {
      issues.push('Target date should be set for in-progress migrations');
    }
    
    if (config.status === 'completed' && !config.migrationVersion) {
      issues.push('Migration version should be recorded for completed migrations');
    }
    
    if (config.targetDate) {
      const targetDate = new Date(config.targetDate);
      const now = new Date();
      if (targetDate < now && config.status !== 'completed') {
        issues.push('Target date has passed but migration is not completed');
      }
    }
    
    return issues;
  }
}

/**
 * React hook for migration utilities
 */
export function useMigrationUtils() {
  return MigrationUtils.getInstance();
}

/**
 * Migration Dashboard Component
 */
export interface MigrationDashboardProps {
  showDetails?: boolean;
  onComponentClick?: (componentName: string) => void;
}

export const MigrationDashboard: React.FC<MigrationDashboardProps> = ({
  showDetails = false,
  onComponentClick,
}) => {
  const utils = useMigrationUtils();
  const analysis = utils.analyzeMigrationProgress();
  const report = utils.generateReport();
  
  const getStatusColor = (status: MigrationStatus): string => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'in_progress': return 'text-blue-600';
      case 'not_started': return 'text-gray-600';
      case 'deprecated': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };
  
  const getStatusIcon = (status: MigrationStatus): string => {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '🔄';
      case 'not_started': return '⏳';
      case 'deprecated': return '⚠️';
      default: return '❓';
    }
  };
  
  return (
    <div className="migration-dashboard p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6">Migration Dashboard</h2>
      
      {/* Progress Overview */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Progress Overview</h3>
          <span className="text-2xl font-bold text-blue-600">
            {analysis.completionPercentage}%
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
          <div 
            className="bg-blue-600 h-4 rounded-full transition-all duration-300"
            style={{ width: `${analysis.completionPercentage}%` }}
          />
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {analysis.completedMigrations}
            </div>
            <div className="text-sm text-green-700">Completed</div>
          </div>
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {analysis.inProgressMigrations}
            </div>
            <div className="text-sm text-blue-700">In Progress</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-600">
              {analysis.notStartedMigrations}
            </div>
            <div className="text-sm text-gray-700">Not Started</div>
          </div>
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {analysis.deprecatedComponents}
            </div>
            <div className="text-sm text-red-700">Deprecated</div>
          </div>
        </div>
      </div>
      
      {/* Estimated Completion */}
      {analysis.estimatedCompletionDate && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-semibold text-blue-800 mb-2">Estimated Completion</h4>
          <p className="text-blue-700">
            {analysis.estimatedCompletionDate.toLocaleDateString()}
          </p>
        </div>
      )}
      
      {/* Critical Issues */}
      {analysis.criticalIssues.length > 0 && (
        <div className="mb-6 p-4 bg-red-50 rounded-lg">
          <h4 className="font-semibold text-red-800 mb-2">Critical Issues</h4>
          <ul className="list-disc list-inside text-red-700">
            {analysis.criticalIssues.map((issue, index) => (
              <li key={index}>{issue}</li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div className="mb-6 p-4 bg-yellow-50 rounded-lg">
          <h4 className="font-semibold text-yellow-800 mb-2">Recommendations</h4>
          <ul className="list-disc list-inside text-yellow-700">
            {analysis.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Component List */}
      {showDetails && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Component Status</h3>
          <div className="space-y-2">
            {report.map((item) => (
              <div 
                key={item.componentName}
                className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer hover:bg-gray-50 ${
                  item.errors.length > 0 ? 'border-red-200 bg-red-50' : 'border-gray-200'
                }`}
                onClick={() => onComponentClick?.(item.componentName)}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-lg">
                    {getStatusIcon(item.status)}
                  </span>
                  <div>
                    <div className="font-medium">{item.componentName}</div>
                    {item.config.notes && (
                      <div className="text-sm text-gray-600">
                        {item.config.notes}
                      </div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-medium ${getStatusColor(item.status)}`}>
                    {item.status.replace('_', ' ')}
                  </div>
                  {item.config.targetDate && (
                    <div className="text-sm text-gray-500">
                      Target: {new Date(item.config.targetDate).toLocaleDateString()}
                    </div>
                  )}
                  {item.errors.length > 0 && (
                    <div className="text-sm text-red-600">
                      {item.errors.length} error(s)
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};