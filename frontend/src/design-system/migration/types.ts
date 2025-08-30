/**
 * Migration Types
 * 
 * Type definitions for the design system migration utilities.
 */

export interface MigrationOptions {
  /** Enable gradual migration mode */
  gradual?: boolean;
  /** Preserve existing class names alongside new ones */
  preserveClasses?: boolean;
  /** Enable migration warnings in development */
  warnings?: boolean;
  /** Custom component mappings */
  customMappings?: ComponentMapping[];
}

export interface ComponentMapping {
  /** Original component name or selector */
  from: string;
  /** New design system component */
  to: string;
  /** Props transformation function */
  transformProps?: (props: any) => any;
  /** Additional migration notes */
  notes?: string;
}

export interface StyleMapping {
  /** Original CSS class or style */
  from: string;
  /** New design system class or token */
  to: string;
  /** Whether this mapping is deprecated */
  deprecated?: boolean;
  /** Migration warning message */
  warning?: string;
}

export interface MigrationReport {
  /** Components successfully migrated */
  migratedComponents: string[];
  /** Components that need manual migration */
  manualMigration: string[];
  /** Deprecated styles found */
  deprecatedStyles: string[];
  /** Migration warnings */
  warnings: string[];
  /** Migration errors */
  errors: string[];
}

export interface LegacyComponentProps {
  /** Original className prop */
  className?: string;
  /** Original style prop */
  style?: React.CSSProperties;
  /** Any other legacy props */
  [key: string]: any;
}