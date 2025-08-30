// Core compatibility system
export {
  createCompatibilityWrapper,
  useMigrationTracker,
  MigrationStatus,
  MigrationError,
  type MigrationConfig,
  type PropMapping,
  type WrapperConfig,
  type MigrationStatusProps,
} from './ComponentWrapper';

// Import MigrationConfig for use in this file
import type { MigrationConfig } from './ComponentWrapper';

// Migration utilities
export {
  MigrationUtils,
  useMigrationUtils,
  MigrationDashboard,
  type MigrationReport,
  type MigrationAnalysis,
  type MigrationDashboardProps,
} from './MigrationUtils';

// Component usage analyzer
export {
  useComponentUsageAnalyzer,
  ComponentUsageAnalyzer,
  type ComponentUsage,
  type AnalysisConfig,
} from './ComponentUsageAnalyzer';

// Migration validator
export {
  useMigrationValidator,
  MigrationValidator,
  type ValidationResult,
  type ValidationReport,
  type ValidationConfig,
  type ValidationRuleType,
} from './MigrationValidator';

// Migration tester
export {
  useMigrationTester,
  MigrationTester,
  type TestResult,
  type TestSuiteReport,
  type TestSuiteConfig,
  type MigrationTestType,
} from './MigrationTester';

// Rollback utilities
export {
  RollbackUtils,
  useRollbackUtils,
  RollbackControlPanel,
  type RollbackConfig,
  type RollbackResult,
  type RollbackControlPanelProps,
} from './RollbackUtils';

// Pre-built component wrappers
export { Button, type ButtonProps } from './wrappers/ButtonWrapper';
export { Input, type InputProps } from './wrappers/InputWrapper';
export { Form, type FormProps } from './wrappers/FormWrapper';

// Utility functions for common migration patterns
export const migrationHelpers = {
  /**
   * Create a simple prop mapping for boolean to string transformations
   */
  createBooleanToStringMapping: (
    booleanProps: string[],
    stringValues: Record<string, string>
  ) => {
    const propMap: Record<string, string> = {};
    const propTransforms: Record<string, (value: any) => any> = {};
    
    booleanProps.forEach(prop => {
      if (stringValues[prop]) {
        propMap[prop] = 'variant'; // or whatever the target prop is
        propTransforms[prop] = (value: boolean) => value ? stringValues[prop] : undefined;
      }
    });
    
    return { propMap, propTransforms, removedProps: booleanProps };
  },
  
  /**
   * Create size mapping from legacy size names to new size names
   */
  createSizeMapping: (
    sizeProp: string = 'size',
    sizeMap: Record<string, string> = { small: 'sm', medium: 'md', large: 'lg' }
  ) => ({
    propTransforms: {
      [sizeProp]: (value: string) => sizeMap[value] || value,
    },
  }),
  
  /**
   * Create className mapping for full-width and other layout props
   */
  createLayoutMapping: (layoutProps: Record<string, string>) => {
    const propTransforms: Record<string, (value: any) => any> = {};
    
    Object.entries(layoutProps).forEach(([prop, className]) => {
      propTransforms[prop] = (value: boolean) => value ? className : undefined;
    });
    
    return {
      propMap: Object.fromEntries(
        Object.keys(layoutProps).map(prop => [prop, 'className'])
      ),
      propTransforms,
      removedProps: Object.keys(layoutProps),
    };
  },
};

// Common migration configurations
export const commonMigrationConfigs = {
  /**
   * Standard in-progress migration config
   */
  inProgress: (componentName: string, targetDate?: string): MigrationConfig => ({
    status: 'in_progress',
    migrationVersion: '1.0.0',
    targetDate: targetDate || '2025-02-15',
    notes: `Migrating ${componentName} to design system`,
    showWarnings: process.env.NODE_ENV === 'development',
  }),
  
  /**
   * Completed migration config
   */
  completed: (componentName: string, version: string = '1.0.0'): MigrationConfig => ({
    status: 'completed',
    migrationVersion: version,
    notes: `${componentName} successfully migrated to design system`,
    showWarnings: false,
  }),
  
  /**
   * Not started migration config
   */
  notStarted: (componentName: string): MigrationConfig => ({
    status: 'not_started',
    notes: `${componentName} migration not yet started`,
    showWarnings: false,
  }),
  
  /**
   * Deprecated component config
   */
  deprecated: (componentName: string, replacement?: string): MigrationConfig => ({
    status: 'deprecated',
    notes: replacement 
      ? `${componentName} is deprecated. Use ${replacement} instead.`
      : `${componentName} is deprecated and should be replaced.`,
    showWarnings: true,
  }),
};