import React from 'react';
import {
  createCompatibilityWrapper,
  MigrationDashboard,
  RollbackControlPanel,
  useMigrationTracker,
  commonMigrationConfigs,
  migrationHelpers,
} from '../index';

// Example: Migrating a Card component
interface LegacyCardProps {
  title?: string;
  children?: React.ReactNode;
  className?: string;
  elevated?: boolean;
  bordered?: boolean;
  padding?: 'small' | 'medium' | 'large';
  onClick?: () => void;
}

// Legacy Card component (what currently exists)
const LegacyCard: React.FC<LegacyCardProps> = ({
  title,
  children,
  className = '',
  elevated,
  bordered,
  padding = 'medium',
  onClick,
}) => {
  let classes = 'legacy-card ' + className;
  if (elevated) classes += ' legacy-card--elevated';
  if (bordered) classes += ' legacy-card--bordered';
  classes += ` legacy-card--padding-${padding}`;
  
  return (
    <div className={classes} onClick={onClick}>
      {title && <h3 className="legacy-card-title">{title}</h3>}
      <div className="legacy-card-content">{children}</div>
    </div>
  );
};

// New design system Card component (placeholder)
interface DesignSystemCardProps {
  title?: string;
  children?: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'outlined';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

const DesignSystemCard: React.FC<DesignSystemCardProps> = ({
  title,
  children,
  className = '',
  variant = 'default',
  size = 'md',
  onClick,
}) => {
  let classes = `ds-card ds-card--${variant} ds-card--${size} ${className}`;
  
  return (
    <div className={classes} onClick={onClick}>
      {title && <h3 className="ds-card-title">{title}</h3>}
      <div className="ds-card-content">{children}</div>
    </div>
  );
};

// Create the migrated Card component using compatibility wrapper
const Card = createCompatibilityWrapper(
  'Card',
  LegacyCard,
  DesignSystemCard,
  {
    migration: commonMigrationConfigs.inProgress('Card', '2025-02-20'),
    propMapping: {
      propMap: {
        elevated: 'variant',
        bordered: 'variant',
        padding: 'size',
      },
      propTransforms: {
        elevated: (value: boolean) => value ? 'elevated' : undefined,
        bordered: (value: boolean) => value ? 'outlined' : undefined,
        padding: (value: 'small' | 'medium' | 'large') => {
          const sizeMap = { small: 'sm', medium: 'md', large: 'lg' };
          return sizeMap[value] || 'md';
        },
      },
      defaultProps: {
        variant: 'default',
        size: 'md',
      },
      removedProps: ['elevated', 'bordered'],
    },
  }
);

// Example: Complex component with custom wrapper logic
interface LegacyTableProps {
  data: any[];
  columns: Array<{
    key: string;
    title: string;
    width?: string;
    sortable?: boolean;
  }>;
  striped?: boolean;
  hoverable?: boolean;
  compact?: boolean;
  onRowClick?: (row: any, index: number) => void;
}

const LegacyTable: React.FC<LegacyTableProps> = ({ data, columns, striped, hoverable, compact, onRowClick }) => {
  let tableClasses = 'legacy-table';
  if (striped) tableClasses += ' legacy-table--striped';
  if (hoverable) tableClasses += ' legacy-table--hoverable';
  if (compact) tableClasses += ' legacy-table--compact';
  
  return (
    <table className={tableClasses}>
      <thead>
        <tr>
          {columns.map(col => (
            <th key={col.key} style={{ width: col.width }}>
              {col.title}
              {col.sortable && <span className="sort-icon">↕</span>}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, index) => (
          <tr key={index} onClick={() => onRowClick?.(row, index)}>
            {columns.map(col => (
              <td key={col.key}>{row[col.key]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

// Design system Table component (placeholder)
interface DesignSystemTableProps {
  data: any[];
  columns: Array<{
    key: string;
    header: string;
    width?: string;
    sortable?: boolean;
  }>;
  variant?: 'default' | 'striped';
  size?: 'sm' | 'md' | 'lg';
  interactive?: boolean;
  onRowClick?: (row: any, index: number) => void;
}

const DesignSystemTable: React.FC<DesignSystemTableProps> = ({
  data,
  columns,
  variant = 'default',
  size = 'md',
  interactive,
  onRowClick,
}) => {
  let tableClasses = `ds-table ds-table--${variant} ds-table--${size}`;
  if (interactive) tableClasses += ' ds-table--interactive';
  
  return (
    <table className={tableClasses}>
      <thead>
        <tr>
          {columns.map(col => (
            <th key={col.key} style={{ width: col.width }}>
              {col.header}
              {col.sortable && <span className="ds-sort-icon">↕</span>}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, index) => (
          <tr key={index} onClick={() => onRowClick?.(row, index)}>
            {columns.map(col => (
              <td key={col.key}>{row[col.key]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

// Create Table with custom wrapper logic
const Table = createCompatibilityWrapper(
  'Table',
  LegacyTable,
  DesignSystemTable,
  {
    migration: commonMigrationConfigs.inProgress('Table', '2025-02-25'),
    customWrapper: (props: LegacyTableProps, NewComponent) => {
      const { striped, hoverable, compact, columns, ...rest } = props;
      
      // Transform columns array
      const newColumns = columns.map(col => ({
        ...col,
        header: col.title, // Map title to header
      }));
      
      // Determine variant and size
      let variant = 'default';
      if (striped) variant = 'striped';
      
      let size = 'md';
      if (compact) size = 'sm';
      
      const newProps = {
        ...rest,
        columns: newColumns,
        variant,
        size,
        interactive: hoverable,
      };
      
      return React.createElement(NewComponent, newProps);
    },
  }
);

// Example usage component
export const MigrationExampleApp: React.FC = () => {
  const tracker = useMigrationTracker();
  const [selectedComponent, setSelectedComponent] = React.useState<string | null>(null);
  
  // Sample data for examples
  const tableData = [
    { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User' },
    { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User' },
  ];
  
  const tableColumns = [
    { key: 'id', title: 'ID', width: '60px' },
    { key: 'name', title: 'Name', sortable: true },
    { key: 'email', title: 'Email', sortable: true },
    { key: 'role', title: 'Role' },
  ];
  
  return (
    <div className="migration-example-app p-6 space-y-8">
      <h1 className="text-3xl font-bold mb-8">Design System Migration Example</h1>
      
      {/* Migration Dashboard */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Migration Dashboard</h2>
        <MigrationDashboard 
          showDetails={true}
          onComponentClick={setSelectedComponent}
        />
      </section>
      
      {/* Example Components */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Example Components</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Card Examples */}
          <div>
            <h3 className="text-lg font-medium mb-3">Card Component</h3>
            <div className="space-y-4">
              <Card title="Default Card">
                This is a default card using the compatibility wrapper.
              </Card>
              
              <Card title="Elevated Card" elevated>
                This card uses the legacy 'elevated' prop which gets mapped to variant='elevated'.
              </Card>
              
              <Card title="Small Bordered Card" bordered padding="small">
                This card demonstrates prop transformation from legacy to new API.
              </Card>
            </div>
          </div>
          
          {/* Table Example */}
          <div>
            <h3 className="text-lg font-medium mb-3">Table Component</h3>
            <Table
              data={tableData}
              columns={tableColumns}
              striped
              hoverable
              onRowClick={(row: any) => console.log('Clicked row:', row)}
            />
          </div>
        </div>
      </section>
      
      {/* Rollback Control Panel */}
      {selectedComponent && (
        <section>
          <h2 className="text-2xl font-semibold mb-4">Rollback Control</h2>
          <RollbackControlPanel
            componentName={selectedComponent}
            onRollbackComplete={(result) => {
              console.log('Rollback completed:', result);
              if (result.success) {
                alert(`Successfully rolled back ${selectedComponent}`);
              } else {
                alert(`Rollback failed: ${result.message}`);
              }
            }}
          />
        </section>
      )}
      
      {/* Migration Statistics */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Migration Statistics</h2>
        <div className="bg-gray-50 p-4 rounded-lg">
          <pre className="text-sm">
            {JSON.stringify(tracker.getStatistics(), null, 2)}
          </pre>
        </div>
      </section>
      
      {/* Usage Examples */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Code Examples</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-2">Basic Wrapper Creation</h3>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
{`const Button = createCompatibilityWrapper(
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
);`}
            </pre>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-2">Using Migration Helpers</h3>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
{`const propMapping = {
  ...migrationHelpers.createBooleanToStringMapping(
    ['primary', 'secondary', 'danger'],
    { primary: 'primary', secondary: 'secondary', danger: 'destructive' }
  ),
  ...migrationHelpers.createSizeMapping(),
  ...migrationHelpers.createLayoutMapping({ fullWidth: 'w-full' }),
};`}
            </pre>
          </div>
        </div>
      </section>
    </div>
  );
};

// CSS for the example (would normally be in a separate file)
const exampleStyles = `
.legacy-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.legacy-card--elevated {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.legacy-card--bordered {
  border: 1px solid #e5e7eb;
}

.legacy-card--padding-small { padding: 8px; }
.legacy-card--padding-medium { padding: 16px; }
.legacy-card--padding-large { padding: 24px; }

.legacy-card-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
}

.legacy-table {
  width: 100%;
  border-collapse: collapse;
}

.legacy-table th,
.legacy-table td {
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.legacy-table--striped tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

.legacy-table--hoverable tbody tr:hover {
  background-color: #f3f4f6;
}

.legacy-table--compact th,
.legacy-table--compact td {
  padding: 4px 8px;
}

.ds-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.ds-card--elevated {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.ds-card--outlined {
  border: 2px solid #e5e7eb;
}

.ds-card--sm { padding: 12px; }
.ds-card--md { padding: 20px; }
.ds-card--lg { padding: 28px; }

.ds-table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 8px;
  overflow: hidden;
}

.ds-table th,
.ds-table td {
  padding: 12px 16px;
  text-align: left;
}

.ds-table--striped tbody tr:nth-child(even) {
  background-color: #f8fafc;
}

.ds-table--interactive tbody tr:hover {
  background-color: #f1f5f9;
  cursor: pointer;
}

.ds-table--sm th,
.ds-table--sm td {
  padding: 6px 12px;
}

.ds-table--lg th,
.ds-table--lg td {
  padding: 16px 20px;
}
`;

// Inject styles (in a real app, these would be in CSS files)
if (typeof document !== 'undefined') {
  const styleElement = document.createElement('style');
  styleElement.textContent = exampleStyles;
  document.head.appendChild(styleElement);
}