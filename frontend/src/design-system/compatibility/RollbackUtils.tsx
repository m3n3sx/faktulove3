import React from 'react';
import { MigrationError, useMigrationTracker } from './ComponentWrapper';

/**
 * Rollback configuration
 */
export interface RollbackConfig {
  componentName: string;
  reason: string;
  timestamp: Date;
  previousVersion?: string;
  rollbackStrategy: 'immediate' | 'gradual' | 'manual';
  affectedModules: string[];
}

/**
 * Rollback result
 */
export interface RollbackResult {
  success: boolean;
  componentName: string;
  message: string;
  errors?: string[];
  rollbackConfig: RollbackConfig;
}

/**
 * Utility class for handling migration rollbacks
 */
export class RollbackUtils {
  private static instance: RollbackUtils;
  private rollbackHistory: Map<string, RollbackConfig[]> = new Map();
  
  static getInstance(): RollbackUtils {
    if (!RollbackUtils.instance) {
      RollbackUtils.instance = new RollbackUtils();
    }
    return RollbackUtils.instance;
  }
  
  /**
   * Execute rollback for a component
   */
  async rollbackComponent(
    componentName: string,
    reason: string,
    strategy: 'immediate' | 'gradual' | 'manual' = 'immediate'
  ): Promise<RollbackResult> {
    const tracker = useMigrationTracker();
    const currentStatus = tracker.getMigrationStatus(componentName);
    
    if (!currentStatus) {
      return {
        success: false,
        componentName,
        message: `No migration found for component: ${componentName}`,
        rollbackConfig: {
          componentName,
          reason,
          timestamp: new Date(),
          rollbackStrategy: strategy,
          affectedModules: [],
        },
      };
    }
    
    const rollbackConfig: RollbackConfig = {
      componentName,
      reason,
      timestamp: new Date(),
      previousVersion: currentStatus.migrationVersion,
      rollbackStrategy: strategy,
      affectedModules: this.getAffectedModules(componentName),
    };
    
    try {
      // Record rollback in history
      const history = this.rollbackHistory.get(componentName) || [];
      history.push(rollbackConfig);
      this.rollbackHistory.set(componentName, history);
      
      // Execute rollback based on strategy
      switch (strategy) {
        case 'immediate':
          await this.executeImmediateRollback(componentName);
          break;
        case 'gradual':
          await this.executeGradualRollback(componentName);
          break;
        case 'manual':
          await this.prepareManualRollback(componentName);
          break;
      }
      
      // Update migration status to not_started
      tracker.trackMigration(componentName, {
        status: 'not_started',
        notes: `Rolled back due to: ${reason}`,
        showWarnings: true,
      });
      
      return {
        success: true,
        componentName,
        message: `Successfully rolled back ${componentName} using ${strategy} strategy`,
        rollbackConfig,
      };
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      return {
        success: false,
        componentName,
        message: `Rollback failed for ${componentName}: ${errorMessage}`,
        errors: [errorMessage],
        rollbackConfig,
      };
    }
  }
  
  /**
   * Execute immediate rollback - switches back to legacy component immediately
   */
  private async executeImmediateRollback(componentName: string): Promise<void> {
    // In a real implementation, this would:
    // 1. Update component registry to use legacy component
    // 2. Clear any cached design system components
    // 3. Trigger re-render of affected components
    
    console.log(`Executing immediate rollback for ${componentName}`);
    
    // Simulate rollback process
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Notify about rollback
    this.notifyRollback(componentName, 'immediate');
  }
  
  /**
   * Execute gradual rollback - phases out new component over time
   */
  private async executeGradualRollback(componentName: string): Promise<void> {
    console.log(`Executing gradual rollback for ${componentName}`);
    
    // In a real implementation, this would:
    // 1. Set up feature flags to gradually reduce new component usage
    // 2. Monitor for issues during rollback
    // 3. Complete rollback over multiple deployments
    
    await new Promise(resolve => setTimeout(resolve, 200));
    
    this.notifyRollback(componentName, 'gradual');
  }
  
  /**
   * Prepare manual rollback - provides instructions for manual intervention
   */
  private async prepareManualRollback(componentName: string): Promise<void> {
    console.log(`Preparing manual rollback for ${componentName}`);
    
    // Generate rollback instructions
    const instructions = this.generateRollbackInstructions(componentName);
    
    // In a real implementation, this would:
    // 1. Create rollback documentation
    // 2. Generate code patches
    // 3. Create rollback checklist
    
    console.log('Manual rollback instructions:', instructions);
    
    this.notifyRollback(componentName, 'manual');
  }
  
  /**
   * Get modules affected by component rollback
   */
  private getAffectedModules(componentName: string): string[] {
    // In a real implementation, this would analyze the codebase
    // to find all modules using the component
    
    const commonModules = ['invoice', 'ocr', 'dashboard', 'auth'];
    return commonModules.filter(() => Math.random() > 0.5); // Simulate
  }
  
  /**
   * Generate rollback instructions for manual rollback
   */
  private generateRollbackInstructions(componentName: string): string[] {
    return [
      `1. Locate all imports of ${componentName} from design system`,
      `2. Replace with legacy ${componentName} imports`,
      `3. Update prop usage to match legacy component API`,
      `4. Test affected functionality thoroughly`,
      `5. Update tests to use legacy component expectations`,
      `6. Remove design system component references`,
      `7. Verify no design system dependencies remain`,
    ];
  }
  
  /**
   * Notify about rollback completion
   */
  private notifyRollback(componentName: string, strategy: string): void {
    // In a real implementation, this would:
    // 1. Send notifications to development team
    // 2. Update monitoring dashboards
    // 3. Log rollback event
    
    console.log(`Rollback completed for ${componentName} using ${strategy} strategy`);
  }
  
  /**
   * Get rollback history for a component
   */
  getRollbackHistory(componentName: string): RollbackConfig[] {
    return this.rollbackHistory.get(componentName) || [];
  }
  
  /**
   * Get all rollback history
   */
  getAllRollbackHistory(): Map<string, RollbackConfig[]> {
    return new Map(this.rollbackHistory);
  }
  
  /**
   * Check if component can be safely rolled back
   */
  canRollback(componentName: string): { canRollback: boolean; reasons: string[] } {
    const tracker = useMigrationTracker();
    const status = tracker.getMigrationStatus(componentName);
    const errors = tracker.getErrors(componentName);
    const reasons: string[] = [];
    
    if (!status) {
      reasons.push('Component not found in migration tracker');
      return { canRollback: false, reasons };
    }
    
    if (status.status === 'not_started') {
      reasons.push('Component migration not started - nothing to rollback');
      return { canRollback: false, reasons };
    }
    
    if (status.status === 'completed' && errors.length === 0) {
      reasons.push('Component migration completed successfully - rollback not recommended');
    }
    
    if (errors.length > 0) {
      reasons.push(`Component has ${errors.length} error(s) - rollback recommended`);
    }
    
    const affectedModules = this.getAffectedModules(componentName);
    if (affectedModules.length > 5) {
      reasons.push(`Rollback affects ${affectedModules.length} modules - consider gradual rollback`);
    }
    
    return { canRollback: true, reasons };
  }
}

/**
 * React hook for rollback utilities
 */
export function useRollbackUtils() {
  return RollbackUtils.getInstance();
}

/**
 * Rollback Control Panel Component
 */
export interface RollbackControlPanelProps {
  componentName: string;
  onRollbackComplete?: (result: RollbackResult) => void;
}

export const RollbackControlPanel: React.FC<RollbackControlPanelProps> = ({
  componentName,
  onRollbackComplete,
}) => {
  const rollbackUtils = useRollbackUtils();
  const tracker = useMigrationTracker();
  const [isRollingBack, setIsRollingBack] = React.useState(false);
  const [rollbackResult, setRollbackResult] = React.useState<RollbackResult | null>(null);
  
  const status = tracker.getMigrationStatus(componentName);
  const errors = tracker.getErrors(componentName);
  const rollbackCheck = rollbackUtils.canRollback(componentName);
  const history = rollbackUtils.getRollbackHistory(componentName);
  
  const handleRollback = async (strategy: 'immediate' | 'gradual' | 'manual', reason: string) => {
    setIsRollingBack(true);
    setRollbackResult(null);
    
    try {
      const result = await rollbackUtils.rollbackComponent(componentName, reason, strategy);
      setRollbackResult(result);
      onRollbackComplete?.(result);
    } catch (error) {
      setRollbackResult({
        success: false,
        componentName,
        message: `Rollback failed: ${error}`,
        rollbackConfig: {
          componentName,
          reason,
          timestamp: new Date(),
          rollbackStrategy: strategy,
          affectedModules: [],
        },
      });
    } finally {
      setIsRollingBack(false);
    }
  };
  
  if (!status) {
    return (
      <div className="rollback-panel p-4 bg-gray-50 rounded-lg">
        <p className="text-gray-600">Component not found in migration tracker.</p>
      </div>
    );
  }
  
  return (
    <div className="rollback-panel p-6 bg-white rounded-lg shadow-lg border">
      <h3 className="text-lg font-semibold mb-4">Rollback Control Panel</h3>
      <p className="text-sm text-gray-600 mb-4">Component: <strong>{componentName}</strong></p>
      
      {/* Current Status */}
      <div className="mb-6">
        <h4 className="font-medium mb-2">Current Status</h4>
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            status.status === 'completed' ? 'bg-green-100 text-green-800' :
            status.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
            status.status === 'not_started' ? 'bg-gray-100 text-gray-800' :
            'bg-red-100 text-red-800'
          }`}>
            {status.status.replace('_', ' ')}
          </span>
          {errors.length > 0 && (
            <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
              {errors.length} error(s)
            </span>
          )}
        </div>
      </div>
      
      {/* Rollback Assessment */}
      <div className="mb-6">
        <h4 className="font-medium mb-2">Rollback Assessment</h4>
        <div className={`p-3 rounded-lg ${
          rollbackCheck.canRollback ? 'bg-yellow-50 border border-yellow-200' : 'bg-red-50 border border-red-200'
        }`}>
          <p className={`font-medium ${rollbackCheck.canRollback ? 'text-yellow-800' : 'text-red-800'}`}>
            {rollbackCheck.canRollback ? 'Rollback Available' : 'Rollback Not Recommended'}
          </p>
          <ul className={`mt-2 text-sm ${rollbackCheck.canRollback ? 'text-yellow-700' : 'text-red-700'}`}>
            {rollbackCheck.reasons.map((reason, index) => (
              <li key={index}>• {reason}</li>
            ))}
          </ul>
        </div>
      </div>
      
      {/* Rollback Actions */}
      {rollbackCheck.canRollback && (
        <div className="mb-6">
          <h4 className="font-medium mb-3">Rollback Options</h4>
          <div className="space-y-3">
            <button
              onClick={() => handleRollback('immediate', 'User requested immediate rollback')}
              disabled={isRollingBack}
              className="w-full p-3 text-left border rounded-lg hover:bg-red-50 hover:border-red-300 disabled:opacity-50"
            >
              <div className="font-medium text-red-800">Immediate Rollback</div>
              <div className="text-sm text-red-600">Switch back to legacy component immediately</div>
            </button>
            
            <button
              onClick={() => handleRollback('gradual', 'User requested gradual rollback')}
              disabled={isRollingBack}
              className="w-full p-3 text-left border rounded-lg hover:bg-yellow-50 hover:border-yellow-300 disabled:opacity-50"
            >
              <div className="font-medium text-yellow-800">Gradual Rollback</div>
              <div className="text-sm text-yellow-600">Phase out new component over time</div>
            </button>
            
            <button
              onClick={() => handleRollback('manual', 'User requested manual rollback')}
              disabled={isRollingBack}
              className="w-full p-3 text-left border rounded-lg hover:bg-blue-50 hover:border-blue-300 disabled:opacity-50"
            >
              <div className="font-medium text-blue-800">Manual Rollback</div>
              <div className="text-sm text-blue-600">Generate rollback instructions for manual execution</div>
            </button>
          </div>
        </div>
      )}
      
      {/* Rollback Result */}
      {rollbackResult && (
        <div className="mb-6">
          <h4 className="font-medium mb-2">Rollback Result</h4>
          <div className={`p-3 rounded-lg ${
            rollbackResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            <p className={`font-medium ${rollbackResult.success ? 'text-green-800' : 'text-red-800'}`}>
              {rollbackResult.success ? 'Success' : 'Failed'}
            </p>
            <p className={`text-sm mt-1 ${rollbackResult.success ? 'text-green-700' : 'text-red-700'}`}>
              {rollbackResult.message}
            </p>
            {rollbackResult.errors && (
              <ul className="mt-2 text-sm text-red-700">
                {rollbackResult.errors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
      
      {/* Rollback History */}
      {history.length > 0 && (
        <div>
          <h4 className="font-medium mb-2">Rollback History</h4>
          <div className="space-y-2">
            {history.map((rollback, index) => (
              <div key={index} className="p-2 bg-gray-50 rounded text-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium">{rollback.rollbackStrategy} rollback</div>
                    <div className="text-gray-600">{rollback.reason}</div>
                  </div>
                  <div className="text-gray-500 text-xs">
                    {rollback.timestamp.toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {isRollingBack && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span>Executing rollback...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};