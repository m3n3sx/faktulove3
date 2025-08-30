# Design System Migration Utilities

This document provides comprehensive documentation for the gradual migration utilities that help transition from legacy components to the design system.

## Overview

The migration utilities provide a complete toolkit for:
- **Automated component analysis** - Discover migration opportunities
- **CLI tools** - Automate component replacement and validation
- **Testing framework** - Comprehensive testing for migrations
- **Rollback capabilities** - Safe recovery from failed migrations
- **Polish business integration** - Specialized components for Polish business requirements

## Components

### 1. Component Usage Analyzer

Analyzes your codebase to identify components that need migration and discovers Polish business opportunities.

```tsx
import { ComponentUsageAnalyzer } from '@design-system/compatibility';

<ComponentUsageAnalyzer 
  onAnalysisComplete={(data) => console.log('Analysis:', data)}
/>
```

**Features:**
- Scans codebase for component usage patterns
- Identifies migration priorities based on usage frequency
- Detects Polish business component opportunities (NIP validation, VAT calculations, etc.)
- Generates comprehensive reports in JSON, CSV, and HTML formats
- Provides migration effort estimates

### 2. Migration Validator

Validates migration results with comprehensive checks for imports, props, accessibility, and Polish business logic.

```tsx
import { MigrationValidator } from '@design-system/compatibility';

<MigrationValidator 
  onValidationComplete={(report) => console.log('Validation:', report)}
/>
```

**Validation Rules:**
- **Import Consistency** - Ensures consistent design system imports
- **Prop Compatibility** - Validates prop usage and mappings
- **Accessibility** - WCAG 2.1 AA/AAA compliance checks
- **Performance** - Bundle size and render time validation
- **Polish Business** - Validates Polish business logic integration
- **CSS Conflicts** - Detects potential styling conflicts
- **Dependency Check** - Verifies required dependencies

### 3. Migration Tester

Comprehensive testing suite for validating migrations across multiple dimensions.

```tsx
import { MigrationTester } from '@design-system/compatibility';

<MigrationTester 
  onTestComplete={(report) => console.log('Tests:', report)}
/>
```

**Test Types:**
- **Unit Tests** - Component functionality and prop handling
- **Integration Tests** - Theme integration and form validation
- **Visual Regression** - Screenshot comparison with configurable thresholds
- **Accessibility Tests** - Keyboard navigation and screen reader support
- **Performance Tests** - Render time and memory usage benchmarks
- **Polish Business Tests** - Currency formatting, NIP validation, VAT calculations

### 4. Migration Dashboard

Central hub for tracking migration progress and managing component status.

```tsx
import { MigrationDashboard } from '@design-system/compatibility';

<MigrationDashboard 
  showDetails={true}
  onComponentClick={(component) => handleComponentClick(component)}
/>
```

**Features:**
- Real-time migration progress tracking
- Component status overview (completed, in-progress, not started, deprecated)
- Critical issues and recommendations
- Estimated completion dates
- Interactive component management

### 5. Rollback Control Panel

Safe rollback capabilities with multiple strategies for recovery from failed migrations.

```tsx
import { RollbackControlPanel } from '@design-system/compatibility';

<RollbackControlPanel 
  componentName="Button"
  onRollbackComplete={(result) => handleRollback(result)}
/>
```

**Rollback Strategies:**
- **Immediate** - Switch back to legacy component immediately
- **Gradual** - Phase out new component over time using feature flags
- **Manual** - Generate rollback instructions for manual execution

## CLI Tools

### Installation

The CLI tools are available as npm scripts in your package.json:

```json
{
  "scripts": {
    "migrate:analyze": "node scripts/migration-cli.js analyze",
    "migrate:component": "node scripts/migration-cli.js migrate",
    "migrate:validate": "node scripts/migration-cli.js validate",
    "migrate:rollback": "node scripts/migration-cli.js rollback",
    "migrate:report": "node scripts/migration-cli.js report"
  }
}
```

### Usage Examples

#### Analyze Component Usage
```bash
# Analyze all components
npm run migrate:analyze

# Analyze specific component
npm run migrate:analyze Button

# Generate comprehensive report
npm run migrate:report html
```

#### Migrate Components
```bash
# Dry run migration (preview changes)
npm run migrate:component Button -- --dry-run

# Execute migration
npm run migrate:component Button

# Migrate specific file
npm run migrate:component Button src/components/MyButton.tsx
```

#### Validate Migration
```bash
# Validate all files
npm run migrate:validate

# Validate with strict mode
npm run migrate:validate -- --strict
```

#### Rollback Migration
```bash
# List available backups
npm run migrate:rollback

# Rollback using backup ID
npm run migrate:rollback 1640995200000
```

## Polish Business Components

The migration utilities include specialized support for Polish business requirements:

### Supported Components
- **NIPValidator** - Polish tax identification number validation
- **CurrencyInput** - Polish złoty (PLN) formatting
- **VATRateSelector** - Polish VAT rates (0%, 5%, 8%, 23%)
- **DatePicker** - Polish date formats (DD.MM.YYYY)
- **InvoiceStatusBadge** - Polish invoice status indicators
- **ComplianceIndicator** - Polish regulatory compliance

### Detection Patterns
The analyzer automatically detects opportunities for Polish business components:

```typescript
// Detected patterns that suggest Polish business components
const polishPatterns = [
  /NIP\s*[:=]/i,           // NIP validation opportunities
  /VAT\s*[:=]/i,           // VAT calculation opportunities  
  /PLN|zł/,                // Currency formatting opportunities
  /\d{2}[.-]\d{2}[.-]\d{4}/, // Polish date format opportunities
];
```

## Configuration

### Analysis Configuration
```typescript
interface AnalysisConfig {
  includeTests: boolean;              // Include test files in analysis
  includeStorybook: boolean;          // Include Storybook files
  minUsageThreshold: number;          // Minimum usage count to report
  excludePatterns: string[];          // Patterns to exclude from analysis
  polishBusinessDetection: boolean;   // Enable Polish business detection
}
```

### Validation Configuration
```typescript
interface ValidationConfig {
  enabledRules: ValidationRuleType[]; // Rules to run
  strictMode: boolean;                // Enable strict validation
  polishBusinessValidation: boolean;  // Validate Polish business logic
  accessibilityLevel: 'AA' | 'AAA';  // WCAG compliance level
  performanceThresholds: {
    bundleSize: number;               // KB threshold
    renderTime: number;               // ms threshold
  };
}
```

### Test Configuration
```typescript
interface TestSuiteConfig {
  enabledTests: MigrationTestType[];  // Test types to run
  components: string[];               // Components to test
  visualRegressionThreshold: number;  // Visual diff threshold (0-1)
  performanceThresholds: {
    renderTime: number;               // ms threshold
    memoryUsage: number;              // MB threshold
  };
  accessibilityLevel: 'AA' | 'AAA';  // WCAG level
  polishBusinessTests: boolean;       // Enable Polish business tests
}
```

## Integration Example

Complete integration example showing all utilities working together:

```tsx
import React from 'react';
import {
  MigrationDashboard,
  ComponentUsageAnalyzer,
  MigrationValidator,
  MigrationTester,
  RollbackControlPanel,
} from '@design-system/compatibility';

export const MigrationCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  return (
    <div className="migration-center">
      {/* Navigation */}
      <nav>
        <button onClick={() => setActiveTab('dashboard')}>Dashboard</button>
        <button onClick={() => setActiveTab('analyze')}>Analyze</button>
        <button onClick={() => setActiveTab('validate')}>Validate</button>
        <button onClick={() => setActiveTab('test')}>Test</button>
        <button onClick={() => setActiveTab('rollback')}>Rollback</button>
      </nav>
      
      {/* Content */}
      {activeTab === 'dashboard' && <MigrationDashboard showDetails />}
      {activeTab === 'analyze' && <ComponentUsageAnalyzer />}
      {activeTab === 'validate' && <MigrationValidator />}
      {activeTab === 'test' && <MigrationTester />}
      {activeTab === 'rollback' && <RollbackControlPanel componentName="Button" />}
    </div>
  );
};
```

## Best Practices

### Migration Strategy
1. **Start with Analysis** - Use the analyzer to identify high-impact components
2. **Prioritize by Usage** - Migrate most-used components first
3. **Test Thoroughly** - Run comprehensive tests before and after migration
4. **Validate Continuously** - Use validation tools throughout the process
5. **Plan for Rollback** - Always have a rollback strategy ready

### Polish Business Integration
1. **Detect Opportunities** - Use the analyzer to find Polish business patterns
2. **Validate Business Logic** - Ensure NIP, VAT, and currency handling is correct
3. **Test with Polish Data** - Use realistic Polish business data in tests
4. **Consider Compliance** - Validate against Polish regulatory requirements

### Performance Considerations
1. **Monitor Bundle Size** - Track impact on application bundle size
2. **Measure Render Performance** - Ensure no performance regressions
3. **Use Code Splitting** - Load design system components on demand
4. **Optimize CSS** - Remove unused styles during migration

## Troubleshooting

### Common Issues

#### Import Conflicts
```typescript
// Problem: Mixed imports
import { Button } from './legacy/Button';
import { Input } from '@design-system/Input';

// Solution: Use consistent imports
import { Button, Input } from '@design-system/components';
```

#### Prop Mapping Issues
```typescript
// Problem: Deprecated props
<Button primary large />

// Solution: Use new prop API
<Button variant="primary" size="lg" />
```

#### Polish Business Logic
```typescript
// Problem: Manual NIP validation
const isValidNIP = (nip) => { /* custom logic */ };

// Solution: Use NIPValidator component
import { NIPValidator } from '@design-system/polish-business';
<NIPValidator value={nip} onValidate={handleValidation} />
```

### Getting Help

1. **Check the Dashboard** - Review migration status and recommendations
2. **Run Validation** - Use the validator to identify specific issues
3. **Review Test Results** - Check test reports for detailed error information
4. **Use CLI Tools** - Generate comprehensive reports for analysis
5. **Consult Documentation** - Refer to component-specific migration guides

## Migration Checklist

- [ ] Run component usage analysis
- [ ] Review Polish business opportunities
- [ ] Plan migration priority based on usage
- [ ] Set up testing environment
- [ ] Create component backups
- [ ] Execute migration with dry-run first
- [ ] Run comprehensive validation
- [ ] Execute full test suite
- [ ] Monitor performance metrics
- [ ] Validate Polish business functionality
- [ ] Document any custom modifications
- [ ] Plan rollback strategy if needed

## Support

For additional support with migration utilities:
- Review the comprehensive example in `examples/ComprehensiveMigrationExample.tsx`
- Check CLI tool documentation in `scripts/migration-cli.js`
- Refer to component-specific migration guides
- Use the built-in help system: `npm run migrate:help`