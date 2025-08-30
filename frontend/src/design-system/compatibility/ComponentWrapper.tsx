import React, { ComponentType, forwardRef } from 'react';

/**
 * Migration status for tracking component migration progress
 */
export type MigrationStatus = 'not_started' | 'in_progress' | 'completed' | 'deprecated';

/**
 * Configuration for component migration
 */
export interface MigrationConfig {
  /** Current migration status */
  status: MigrationStatus;
  /** Version when migration started */
  migrationVersion?: string;
  /** Target completion date */
  targetDate?: string;
  /** Migration notes and instructions */
  notes?: string;
  /** Whether to show migration warnings */
  showWarnings?: boolean;
}

/**
 * Props mapping configuration for component migration
 */
export interface PropMapping {
  /** Map old prop names to new prop names */
  propMap?: Record<string, string>;
  /** Transform prop values */
  propTransforms?: Record<string, (value: any) => any>;
  /** Default props for new component */
  defaultProps?: Record<string, any>;
  /** Props to remove during migration */
  removedProps?: string[];
}

/**
 * Wrapper configuration for component compatibility
 */
export interface WrapperConfig {
  /** Migration configuration */
  migration: MigrationConfig;
  /** Props mapping configuration */
  propMapping?: PropMapping;
  /** Fallback component if migration fails */
  fallbackComponent?: ComponentType<any>;
  /** Custom wrapper logic */
  customWrapper?: (props: any, NewComponent: ComponentType<any>) => React.ReactElement;
}

/**
 * Error thrown during component migration
 */
export class MigrationError extends Error {
  constructor(
    public componentName: string,
    public reason: string,
    public originalError?: Error
  ) {
    super(`Migration failed for ${componentName}: ${reason}`);
    this.name = 'MigrationError';
  }
}

/**
 * Migration status tracking
 */
class MigrationTracker {
  private static instance: MigrationTracker;
  private migrations: Map<string, MigrationConfig> = new Map();
  private errors: Map<string, MigrationError[]> = new Map();

  static getInstance(): MigrationTracker {
    if (!MigrationTracker.instance) {
      MigrationTracker.instance = new MigrationTracker();
    }
    return MigrationTracker.instance;
  }

  trackMigration(componentName: string, config: MigrationConfig): void {
    this.migrations.set(componentName, config);
  }

  trackError(componentName: string, error: MigrationError): void {
    const errors = this.errors.get(componentName) || [];
    errors.push(error);
    this.errors.set(componentName, errors);
  }

  getMigrationStatus(componentName: string): MigrationConfig | undefined {
    return this.migrations.get(componentName);
  }

  getErrors(componentName: string): MigrationError[] {
    return this.errors.get(componentName) || [];
  }

  getAllMigrations(): Map<string, MigrationConfig> {
    return new Map(this.migrations);
  }

  getStatistics() {
    const statuses = Array.from(this.migrations.values()).map(m => m.status);
    return {
      total: statuses.length,
      not_started: statuses.filter(s => s === 'not_started').length,
      in_progress: statuses.filter(s => s === 'in_progress').length,
      completed: statuses.filter(s => s === 'completed').length,
      deprecated: statuses.filter(s => s === 'deprecated').length,
    };
  }
}

/**
 * Transform props according to mapping configuration
 */
function transformProps(props: any, mapping: PropMapping): any {
  const { propMap = {}, propTransforms = {}, defaultProps = {}, removedProps = [] } = mapping;
  
  // Start with default props
  let transformedProps = { ...defaultProps };
  
  // Apply prop mapping and transformations
  Object.entries(props).forEach(([key, value]) => {
    // Skip removed props
    if (removedProps.includes(key)) {
      return;
    }
    
    // Map prop name if needed
    const newKey = propMap[key] || key;
    
    // Transform prop value if needed
    const transformedValue = propTransforms[key] ? propTransforms[key](value) : value;
    
    transformedProps[newKey] = transformedValue;
  });
  
  return transformedProps;
}

/**
 * Log migration warning
 */
function logMigrationWarning(componentName: string, config: MigrationConfig): void {
  if (!config.showWarnings) return;
  
  const message = `Component "${componentName}" is using compatibility wrapper (status: ${config.status})`;
  const details = config.notes ? `\nNotes: ${config.notes}` : '';
  const target = config.targetDate ? `\nTarget completion: ${config.targetDate}` : '';
  
  console.warn(`🔄 ${message}${details}${target}`);
}

/**
 * Create a compatibility wrapper for component migration
 */
export function createCompatibilityWrapper<T = any>(
  componentName: string,
  OldComponent: ComponentType<T>,
  NewComponent: ComponentType<any>,
  config: WrapperConfig
): ComponentType<any> {
  const tracker = MigrationTracker.getInstance();
  
  // Track this migration
  tracker.trackMigration(componentName, config.migration);
  
  const WrappedComponent = forwardRef<any, any>((props, ref) => {
    try {
      // Log migration warning if enabled
      logMigrationWarning(componentName, config.migration);
      
      // Handle different migration statuses
      switch (config.migration.status) {
        case 'not_started':
          // Use old component as-is
          return React.createElement(OldComponent as any, { ...props, ref });
          
        case 'deprecated':
          // Show deprecation warning and use fallback
          console.warn(`⚠️ Component "${componentName}" is deprecated. Please migrate to the new design system component.`);
          if (config.fallbackComponent) {
            return React.createElement(config.fallbackComponent as any, { ...props, ref });
          }
          return React.createElement(OldComponent as any, { ...props, ref });
          
        case 'in_progress':
        case 'completed':
          // Use custom wrapper if provided
          if (config.customWrapper) {
            return config.customWrapper(props, NewComponent);
          }
          
          // Transform props if mapping is provided
          const transformedProps = config.propMapping 
            ? transformProps(props, config.propMapping)
            : props;
          
          // Use new component with transformed props
          return React.createElement(NewComponent as any, { ...transformedProps, ref });
          
        default:
          throw new MigrationError(componentName, `Unknown migration status: ${config.migration.status}`);
      }
    } catch (error) {
      const migrationError = error instanceof MigrationError 
        ? error 
        : new MigrationError(componentName, 'Unexpected error during migration', error as Error);
      
      // Track the error
      tracker.trackError(componentName, migrationError);
      
      // Log error
      console.error('Migration Error:', migrationError);
      
      // Use fallback component if available
      if (config.fallbackComponent) {
        console.warn(`Using fallback component for "${componentName}"`);
        return React.createElement(config.fallbackComponent as any, { ...props, ref });
      }
      
      // Fall back to old component
      console.warn(`Falling back to old component for "${componentName}"`);
      return React.createElement(OldComponent as any, { ...props, ref });
    }
  });
  
  WrappedComponent.displayName = `CompatibilityWrapper(${componentName})`;
  
  return WrappedComponent;
}

/**
 * Hook to access migration tracker
 */
export function useMigrationTracker() {
  return MigrationTracker.getInstance();
}

/**
 * Component to display migration status
 */
export interface MigrationStatusProps {
  componentName?: string;
  showDetails?: boolean;
}

export const MigrationStatus: React.FC<MigrationStatusProps> = ({ 
  componentName, 
  showDetails = false 
}) => {
  const tracker = useMigrationTracker();
  
  if (componentName) {
    const status = tracker.getMigrationStatus(componentName);
    const errors = tracker.getErrors(componentName);
    
    if (!status) return null;
    
    return (
      <div className="migration-status" data-component={componentName}>
        <span className={`status-badge status-${status.status}`}>
          {status.status}
        </span>
        {showDetails && (
          <div className="migration-details">
            {status.notes && <p>{status.notes}</p>}
            {status.targetDate && <p>Target: {status.targetDate}</p>}
            {errors.length > 0 && (
              <div className="migration-errors">
                <h4>Errors:</h4>
                {errors.map((error, index) => (
                  <p key={index} className="error">{error instanceof Error ? error.message : String(error)}</p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }
  
  // Show overall statistics
  const stats = tracker.getStatistics();
  
  return (
    <div className="migration-statistics">
      <h3>Migration Progress</h3>
      <div className="stats-grid">
        <div className="stat">
          <span className="stat-label">Total:</span>
          <span className="stat-value">{stats.total}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Not Started:</span>
          <span className="stat-value">{stats.not_started}</span>
        </div>
        <div className="stat">
          <span className="stat-label">In Progress:</span>
          <span className="stat-value">{stats.in_progress}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Completed:</span>
          <span className="stat-value">{stats.completed}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Deprecated:</span>
          <span className="stat-value">{stats.deprecated}</span>
        </div>
      </div>
    </div>
  );
};