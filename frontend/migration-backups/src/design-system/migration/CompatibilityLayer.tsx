/**
 * Compatibility Layer
 * 
 * Provides backward compatibility for existing FaktuLove components
 * while gradually migrating to the new design system.
 */

import React from 'react';
import { cn } from '../utils/cn';
import { migrationConfig } from './config';
import type { LegacyComponentProps, MigrationOptions } from './types';

// Import design system components
import { Button } from '../components/primitives/Button/Button';
import { Input } from '../components/primitives/Input/Input';
import { Container } from '../components/layouts/Container/Container';
import { Grid } from '../components/layouts/Grid/Grid';
import { CurrencyInput } from '../components/business/CurrencyInput/CurrencyInput';
import { NIPValidator } from '../components/business/NIPValidator/NIPValidator';
import { VATRateSelector } from '../components/business/VATRateSelector/VATRateSelector';

interface CompatibilityLayerProps {
  children: React.ReactNode;
  options?: MigrationOptions;
}

/**
 * Context for migration options
 */
const MigrationContext = React.createContext<MigrationOptions>({
  gradual: true,
  preserveClasses: true,
  warnings: process.env.NODE_ENV === 'development'
});

/**
 * Hook to access migration options
 */
export const useMigrationOptions = () => React.useContext(MigrationContext);

/**
 * Compatibility layer provider
 */
export const CompatibilityLayer: React.FC<CompatibilityLayerProps> = ({ 
  children, 
  options = migrationConfig.options 
}) => {
  return (
    <MigrationContext.Provider value={options}>
      {children}
    </MigrationContext.Provider>
  );
};

/**
 * Legacy Button wrapper
 */
export const LegacyButton: React.FC<LegacyComponentProps> = (props) => {
  const options = useMigrationOptions();
  const { className, children, ...restProps } = props;
  
  // Determine variant based on legacy classes
  let variant: 'primary' | 'secondary' | 'ghost' | 'danger' = 'primary';
  let size: 'xs' | 'sm' | 'md' | 'lg' | 'xl' = 'md';
  
  if (className?.includes('bg-primary-600')) {
    variant = 'primary';
  } else if (className?.includes('border-gray-300')) {
    variant = 'secondary';
  } else if (className?.includes('bg-red-600')) {
    variant = 'danger';
  } else if (className?.includes('bg-transparent')) {
    variant = 'ghost';
  }
  
  if (className?.includes('px-2 py-1')) {
    size = 'sm';
  } else if (className?.includes('px-6 py-3')) {
    size = 'lg';
  }
  
  // Warn about migration in development
  if (options.warnings && process.env.NODE_ENV === 'development') {
    console.warn('LegacyButton: Consider migrating to design system Button component');
  }
  
  return (
    <Button
      variant={variant}
      size={size}
      className={options.preserveClasses ? className : undefined}
      {...restProps}
    >
      {children}
    </Button>
  );
};

/**
 * Legacy Input wrapper
 */
export const LegacyInput: React.FC<LegacyComponentProps> = (props) => {
  const options = useMigrationOptions();
  const { className, ...restProps } = props;
  
  // Determine variant based on legacy classes
  let variant: 'default' | 'error' | 'success' = 'default';
  
  if (className?.includes('border-red')) {
    variant = 'error';
  } else if (className?.includes('border-green')) {
    variant = 'success';
  }
  
  // Warn about migration in development
  if (options.warnings && process.env.NODE_ENV === 'development') {
    console.warn('LegacyInput: Consider migrating to design system Input component');
  }
  
  return (
    <Input
      variant={variant}
      className={options.preserveClasses ? className : undefined}
      {...restProps}
    />
  );
};

/**
 * Legacy Container wrapper
 */
export const LegacyContainer: React.FC<LegacyComponentProps> = (props) => {
  const options = useMigrationOptions();
  const { className, children, ...restProps } = props;
  
  // Determine max width based on legacy classes
  let maxWidth: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl' | '7xl' = '7xl';
  
  if (className?.includes('max-w-sm')) maxWidth = 'sm';
  else if (className?.includes('max-w-md')) maxWidth = 'md';
  else if (className?.includes('max-w-lg')) maxWidth = 'lg';
  else if (className?.includes('max-w-xl')) maxWidth = 'xl';
  else if (className?.includes('max-w-2xl')) maxWidth = '2xl';
  else if (className?.includes('max-w-3xl')) maxWidth = '3xl';
  else if (className?.includes('max-w-4xl')) maxWidth = '4xl';
  else if (className?.includes('max-w-5xl')) maxWidth = '5xl';
  else if (className?.includes('max-w-6xl')) maxWidth = '6xl';
  else if (className?.includes('max-w-7xl')) maxWidth = '7xl';
  
  // Warn about migration in development
  if (options.warnings && process.env.NODE_ENV === 'development') {
    console.warn('LegacyContainer: Consider migrating to design system Container component');
  }
  
  return (
    <Container
      maxWidth={maxWidth}
      className={options.preserveClasses ? className : undefined}
      {...restProps}
    >
      {children}
    </Container>
  );
};

/**
 * Legacy Grid wrapper
 */
export const LegacyGrid: React.FC<LegacyComponentProps> = (props) => {
  const options = useMigrationOptions();
  const { className, children, ...restProps } = props;
  
  // Extract grid columns from legacy classes
  const colsMatch = className?.match(/grid-cols-(\d+)/);
  const cols = colsMatch ? parseInt(colsMatch[1]) : 1;
  
  // Extract gap from legacy classes
  const gapMatch = className?.match(/gap-(\d+)/);
  const gap = gapMatch ? parseInt(gapMatch[1]) : 4;
  
  // Warn about migration in development
  if (options.warnings && process.env.NODE_ENV === 'development') {
    console.warn('LegacyGrid: Consider migrating to design system Grid component');
  }
  
  return (
    <Grid
      cols={cols}
      gap={gap}
      className={options.preserveClasses ? className : undefined}
      {...restProps}
    >
      {children}
    </Grid>
  );
};

/**
 * Style migration utility
 */
export const migrateStyles = (className: string): string => {
  const options = useMigrationOptions();
  let migratedClasses = className;
  
  migrationConfig.styleMappings.forEach(mapping => {
    if (migratedClasses.includes(mapping.from)) {
      migratedClasses = migratedClasses.replace(mapping.from, mapping.to);
      
      if (mapping.deprecated && options.warnings && process.env.NODE_ENV === 'development') {
        console.warn(`Deprecated style "${mapping.from}": ${mapping.warning}`);
      }
    }
  });
  
  return migratedClasses;
};

/**
 * HOC for automatic style migration
 */
export const withStyleMigration = <P extends object>(
  Component: React.ComponentType<P>
) => {
  return React.forwardRef<any, P & { className?: string }>((props, ref) => {
    const { className, ...restProps } = props;
    const migratedClassName = className ? migrateStyles(className) : undefined;
    
    return (
      <Component
        ref={ref}
        className={migratedClassName}
        {...(restProps as P)}
      />
    );
  });
};