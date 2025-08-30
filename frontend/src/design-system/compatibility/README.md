# Design System Compatibility Layer

The compatibility layer provides a smooth migration path from legacy components to the new design system components. It includes wrapper utilities, migration tracking, rollback capabilities, and comprehensive tooling for managing the transition.

## Features

- **Component Wrappers**: Seamlessly bridge legacy and new component APIs
- **Migration Tracking**: Monitor progress and identify issues
- **Prop Mapping**: Automatically transform legacy props to new component props
- **Rollback Support**: Safely revert problematic migrations
- **Development Tools**: Dashboard and utilities for managing migrations
- **Fallback Mechanisms**: Graceful degradation when migrations fail

## Quick Start

### Basic Component Wrapper

```typescript
import { createCompatibilityWrapper, commonMigrationConfigs } from './compatibility';

// Create a wrapped component
const Button = createCompatibilityWrapper(
  'Button',
  LegacyButton,
  DesignSystemButton,
  {
    migration: commonMigrationConfigs.inProgress('Button'),
    propMapping: {
      propMap: { primary: 'variant' },
      propTransforms: { 
        primary: (value: boolean) => value ? 'primary' : 'default' 
      },
      removedProps: ['primary'],
    },
  }
);
```

### Using Migration Helpers

```typescript
import { migrationHelpers } from './compatibility';

const propMapping = {
  ...migrationHelpers.createBooleanToStringMapping(
    ['primary', 'secondary', 'danger'],
    { primary: 'primary', secondary: 'secondary', danger: 'destructive' }
  ),
  ...migrationHelpers.createSizeMapping(),
  ...migrationHelpers.createLayoutMapping({ fullWidth: 'w-full' }),
};
```

## Core Concepts

### Migration Status

Components can have one of four migration statuses:

- **`not_started`**: Migration hasn't begun, uses legacy component
- **`in_progress`**: Migration active, uses new component with compatibility layer
- **`completed`**: Migration finished, uses new component directly
- **`deprecated`**: Component is deprecated, shows warnings

### Prop Mapping

The prop mapping system handles three types of transformations:

1. **Prop Renaming**: Map old prop names to new ones
2. **Value Transformation**: Convert prop values (e.g., boolean to string)
3. **Prop Removal**: Remove props that don't exist in new component

```typescript
const propMapping: PropMapping = {
  propMap: {
    // Rename props
    oldPropName: 'newPropName',
  },
  propTransforms: {
    // Transform values
    size: (value: 'small' | 'large') => value === 'small' ? 'sm' : 'lg',
  },
  defaultProps: {
    // Set defaults for new component
    variant: 'default',
  },
  removedProps: [
    // Props to remove
    'oldPropName',
  ],
};
```

### Custom Wrapper Logic

For complex transformations, use custom wrapper logic:

```typescript
const config: WrapperConfig = {
  migration: commonMigrationConfigs.inProgress('Table'),
  customWrapper: (props: LegacyTableProps, NewComponent) => {
    // Custom transformation logic
    const transformedProps = {
      ...props,
      columns: props.columns.map(col => ({
        ...col,
        header: col.title, // Rename title to header
      })),
    };
    
    return React.createElement(NewComponent, transformedProps);
  },
};
```

## Migration Tracking

### Using the Migration Tracker

```typescript
import { useMigrationTracker } from './compatibility';

const MyComponent = () => {
  const tracker = useMigrationTracker();
  
  // Get statistics
  const stats = tracker.getStatistics();
  
  // Get component status
  const status = tracker.getMigrationStatus('Button');
  
  // Get errors
  const errors = tracker.getErrors('Button');
  
  return <div>Migration progress: {stats.completed}/{stats.total}</div>;
};
```

### Migration Dashboard

```typescript
import { MigrationDashboard } from './compatibility';

const AdminPanel = () => (
  <MigrationDashboard 
    showDetails={true}
    onComponentClick={(componentName) => {
      console.log('Selected component:', componentName);
    }}
  />
);
```

## Rollback System

### Rollback Strategies

1. **Immediate**: Switch back to legacy component immediately
2. **Gradual**: Phase out new component over time
3. **Manual**: Generate instructions for manual rollback

### Using Rollback Utilities

```typescript
import { useRollbackUtils } from './compatibility';

const MyComponent = () => {
  const rollbackUtils = useRollbackUtils();
  
  const handleRollback = async () => {
    const result = await rollbackUtils.rollbackComponent(
      'Button',
      'Performance issues detected',
      'immediate'
    );
    
    if (result.success) {
      console.log('Rollback successful');
    } else {
      console.error('Rollback failed:', result.message);
    }
  };
  
  return <button onClick={handleRollback}>Rollback Button</button>;
};
```

### Rollback Control Panel

```typescript
import { RollbackControlPanel } from './compatibility';

const ComponentManager = () => (
  <RollbackControlPanel
    componentName="Button"
    onRollbackComplete={(result) => {
      if (result.success) {
        alert('Rollback completed successfully');
      }
    }}
  />
);
```

## Error Handling

### Migration Errors

The system automatically handles migration errors:

```typescript
// Errors are tracked and can be retrieved
const errors = tracker.getErrors('Button');

// Fallback mechanisms are used when migrations fail
const config: WrapperConfig = {
  migration: commonMigrationConfigs.inProgress('Button'),
  fallbackComponent: LegacyButton, // Used if migration fails
  // ... other config
};
```

### Error Boundaries

Wrap your app with error boundaries to catch migration issues:

```typescript
import { DesignSystemErrorBoundary } from './compatibility';

const App = () => (
  <DesignSystemErrorBoundary>
    <YourApp />
  </DesignSystemErrorBoundary>
);
```

## Development Tools

### Migration Status Display

```typescript
import { MigrationStatus } from './compatibility';

// Show status for specific component
<MigrationStatus componentName="Button" showDetails={true} />

// Show overall statistics
<MigrationStatus />
```

### Migration Utilities

```typescript
import { useMigrationUtils } from './compatibility';

const DevTools = () => {
  const utils = useMigrationUtils();
  
  // Generate comprehensive report
  const report = utils.generateReport();
  
  // Analyze progress
  const analysis = utils.analyzeMigrationProgress();
  
  // Export data
  const exportData = utils.exportMigrationData();
  
  return (
    <div>
      <h3>Completion: {analysis.completionPercentage}%</h3>
      <button onClick={() => console.log(exportData)}>
        Export Migration Data
      </button>
    </div>
  );
};
```

## Best Practices

### 1. Start with Simple Components

Begin migration with simple, widely-used components like buttons and inputs.

### 2. Use Migration Helpers

Leverage the built-in helpers for common transformation patterns:

```typescript
// Instead of manual mapping
const propMapping = migrationHelpers.createBooleanToStringMapping(
  ['primary', 'secondary'],
  { primary: 'primary', secondary: 'secondary' }
);
```

### 3. Test Thoroughly

Always test components after migration:

```typescript
// Enable warnings in development
const config: WrapperConfig = {
  migration: {
    status: 'in_progress',
    showWarnings: process.env.NODE_ENV === 'development',
  },
  // ... other config
};
```

### 4. Monitor Progress

Use the dashboard to track migration progress and identify issues early.

### 5. Plan Rollbacks

Always have a rollback strategy for critical components:

```typescript
const config: WrapperConfig = {
  migration: commonMigrationConfigs.inProgress('CriticalComponent'),
  fallbackComponent: LegacyCriticalComponent,
  // ... other config
};
```

## Configuration Options

### Migration Config

```typescript
interface MigrationConfig {
  status: 'not_started' | 'in_progress' | 'completed' | 'deprecated';
  migrationVersion?: string;
  targetDate?: string;
  notes?: string;
  showWarnings?: boolean;
}
```

### Prop Mapping Config

```typescript
interface PropMapping {
  propMap?: Record<string, string>;
  propTransforms?: Record<string, (value: any) => any>;
  defaultProps?: Record<string, any>;
  removedProps?: string[];
}
```

### Wrapper Config

```typescript
interface WrapperConfig {
  migration: MigrationConfig;
  propMapping?: PropMapping;
  fallbackComponent?: ComponentType<any>;
  customWrapper?: (props: any, NewComponent: ComponentType<any>) => React.ReactElement;
}
```

## Troubleshooting

### Common Issues

1. **Props not mapping correctly**: Check prop transforms and mapping configuration
2. **Component not rendering**: Verify fallback component is provided
3. **Performance issues**: Consider gradual rollback for problematic components
4. **Type errors**: Ensure prop types are compatible between legacy and new components

### Debug Mode

Enable debug logging in development:

```typescript
// Set environment variable
process.env.MIGRATION_DEBUG = 'true';

// Or enable warnings
const config: WrapperConfig = {
  migration: {
    status: 'in_progress',
    showWarnings: true,
  },
};
```

### Getting Help

1. Check the migration dashboard for component status
2. Review error logs in the migration tracker
3. Use the rollback control panel for problematic components
4. Export migration data for analysis

## Examples

See the `examples/MigrationExample.tsx` file for comprehensive usage examples including:

- Basic component wrappers
- Complex prop transformations
- Migration dashboard integration
- Rollback control panels
- Development tools usage

## API Reference

### Core Functions

- `createCompatibilityWrapper()`: Create a component wrapper
- `useMigrationTracker()`: Access migration tracking
- `useMigrationUtils()`: Access migration utilities
- `useRollbackUtils()`: Access rollback utilities

### Components

- `MigrationDashboard`: Visual migration progress dashboard
- `MigrationStatus`: Display component migration status
- `RollbackControlPanel`: Rollback management interface

### Utilities

- `migrationHelpers`: Common prop mapping patterns
- `commonMigrationConfigs`: Standard migration configurations
- `MigrationUtils`: Migration analysis and reporting
- `RollbackUtils`: Rollback management and execution