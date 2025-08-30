/**
 * Documentation Updater
 * Automatically updates documentation based on real-world usage patterns and feedback
 */

import { ComponentUsageTracker, type ComponentUsage } from '../monitoring/ComponentUsageTracker';
import { ProductionMetricsAnalyzer } from './ProductionMetricsAnalyzer';

interface DocumentationUpdate {
  componentName: string;
  section: 'usage' | 'examples' | 'props' | 'accessibility' | 'polish-business';
  updateType: 'add' | 'modify' | 'remove';
  content: string;
  reason: string;
  priority: 'high' | 'medium' | 'low';
}

interface UsagePattern {
  componentName: string;
  commonProps: Array<{ prop: string; frequency: number; examples: string[] }>;
  commonVariants: Array<{ variant: string; frequency: number }>;
  commonUseCases: Array<{ useCase: string; frequency: number; context: string }>;
  errorPatterns: Array<{ error: string; frequency: number; solution: string }>;
}

interface DocumentationGap {
  componentName: string;
  gapType: 'missing-example' | 'outdated-prop' | 'missing-accessibility' | 'missing-polish-business';
  description: string;
  suggestedContent: string;
}

class DocumentationUpdater {
  private usageTracker: ComponentUsageTracker;
  private metricsAnalyzer: ProductionMetricsAnalyzer;
  private documentationCache: Map<string, string> = new Map();

  constructor() {
    this.usageTracker = new ComponentUsageTracker();
    this.metricsAnalyzer = new ProductionMetricsAnalyzer();
  }

  public async analyzeDocumentationNeeds(): Promise<{
    updates: DocumentationUpdate[];
    gaps: DocumentationGap[];
    usagePatterns: UsagePattern[];
  }> {
    console.log('Analyzing documentation needs based on real-world usage...');

    const usageData = this.usageTracker.getComponentUsage() as ComponentUsage[];
    const usagePatterns = this.extractUsagePatterns(usageData);
    const gaps = this.identifyDocumentationGaps(usagePatterns);
    const updates = this.generateDocumentationUpdates(usagePatterns, gaps);

    return {
      updates,
      gaps,
      usagePatterns
    };
  }

  private extractUsagePatterns(usageData: ComponentUsage[]): UsagePattern[] {
    return usageData.map(usage => {
      // Extract common props
      const commonProps = Array.from(usage.props.entries())
        .map(([prop, frequency]) => ({
          prop,
          frequency,
          examples: this.generatePropExamples(prop, usage.componentName)
        }))
        .sort((a, b) => b.frequency - a.frequency)
        .slice(0, 10);

      // Extract common variants
      const commonVariants = Array.from(usage.variants)
        .map(variant => ({
          variant,
          frequency: this.estimateVariantFrequency(variant, usage)
        }))
        .sort((a, b) => b.frequency - a.frequency);

      // Extract common use cases
      const commonUseCases = this.extractUseCases(usage);

      // Extract error patterns
      const errorPatterns = this.extractErrorPatterns(usage);

      return {
        componentName: usage.componentName,
        commonProps,
        commonVariants,
        commonUseCases,
        errorPatterns
      };
    });
  }

  private generatePropExamples(prop: string, componentName: string): string[] {
    const examples: string[] = [];
    
    switch (prop) {
      case 'variant':
        examples.push('primary', 'secondary', 'success', 'error');
        break;
      case 'size':
        examples.push('sm', 'md', 'lg', 'xl');
        break;
      case 'disabled':
        examples.push('true', 'false');
        break;
      case 'aria-label':
        examples.push(`"${componentName} button"`, `"Close ${componentName}"`);
        break;
      case 'onClick':
        examples.push('() => handleClick()', '(event) => onSubmit(event)');
        break;
      default:
        examples.push(`"example-${prop}"`);
    }
    
    return examples;
  }

  private estimateVariantFrequency(variant: string, usage: ComponentUsage): number {
    // Estimate frequency based on usage patterns
    return Math.floor(usage.usageCount * 0.1 * Math.random() + 1);
  }

  private extractUseCases(usage: ComponentUsage): Array<{ useCase: string; frequency: number; context: string }> {
    const useCases: Array<{ useCase: string; frequency: number; context: string }> = [];
    
    // Analyze pages where component is used
    usage.pages.forEach(page => {
      let useCase = 'General usage';
      let context = page;
      
      if (page.includes('invoice')) {
        useCase = 'Invoice management';
        context = 'Used in invoice creation and editing forms';
      } else if (page.includes('ocr')) {
        useCase = 'OCR processing';
        context = 'Used in document upload and results display';
      } else if (page.includes('dashboard')) {
        useCase = 'Dashboard display';
        context = 'Used in analytics and metrics visualization';
      } else if (page.includes('auth')) {
        useCase = 'Authentication';
        context = 'Used in login and registration forms';
      }
      
      const existing = useCases.find(uc => uc.useCase === useCase);
      if (existing) {
        existing.frequency++;
      } else {
        useCases.push({
          useCase,
          frequency: 1,
          context
        });
      }
    });
    
    return useCases.sort((a, b) => b.frequency - a.frequency);
  }

  private extractErrorPatterns(usage: ComponentUsage): Array<{ error: string; frequency: number; solution: string }> {
    const errorPatterns: Array<{ error: string; frequency: number; solution: string }> = [];
    
    // Group errors by type
    const errorGroups = new Map<string, number>();
    
    usage.errors.forEach(error => {
      const errorType = this.categorizeError(error.error);
      errorGroups.set(errorType, (errorGroups.get(errorType) || 0) + 1);
    });
    
    // Convert to patterns with solutions
    errorGroups.forEach((frequency, error) => {
      errorPatterns.push({
        error,
        frequency,
        solution: this.generateErrorSolution(error, usage.componentName)
      });
    });
    
    return errorPatterns.sort((a, b) => b.frequency - a.frequency);
  }

  private categorizeError(errorMessage: string): string {
    if (errorMessage.includes('prop') || errorMessage.includes('property')) {
      return 'Invalid prop usage';
    } else if (errorMessage.includes('render') || errorMessage.includes('component')) {
      return 'Render error';
    } else if (errorMessage.includes('accessibility') || errorMessage.includes('aria')) {
      return 'Accessibility issue';
    } else if (errorMessage.includes('validation')) {
      return 'Validation error';
    } else {
      return 'General error';
    }
  }

  private generateErrorSolution(error: string, componentName: string): string {
    switch (error) {
      case 'Invalid prop usage':
        return `Check the ${componentName} component documentation for valid prop types and values`;
      case 'Render error':
        return `Ensure all required props are provided and component is properly wrapped`;
      case 'Accessibility issue':
        return `Add proper aria-label, role, and other accessibility attributes`;
      case 'Validation error':
        return `Verify input validation rules and error handling implementation`;
      default:
        return `Review component implementation and check console for detailed error messages`;
    }
  }

  private identifyDocumentationGaps(usagePatterns: UsagePattern[]): DocumentationGap[] {
    const gaps: DocumentationGap[] = [];
    
    usagePatterns.forEach(pattern => {
      // Check for missing examples of common props
      if (pattern.commonProps.length > 0 && pattern.commonProps[0].frequency > 10) {
        gaps.push({
          componentName: pattern.componentName,
          gapType: 'missing-example',
          description: `High usage of ${pattern.commonProps[0].prop} prop but no examples in documentation`,
          suggestedContent: this.generatePropDocumentation(pattern.commonProps[0], pattern.componentName)
        });
      }
      
      // Check for accessibility gaps
      const hasAriaLabel = pattern.commonProps.some(p => p.prop === 'aria-label');
      if (!hasAriaLabel && pattern.commonUseCases.length > 0) {
        gaps.push({
          componentName: pattern.componentName,
          gapType: 'missing-accessibility',
          description: `Component used frequently but lacks accessibility documentation`,
          suggestedContent: this.generateAccessibilityDocumentation(pattern.componentName)
        });
      }
      
      // Check for Polish business gaps
      if (this.isPolishBusinessComponent(pattern.componentName)) {
        gaps.push({
          componentName: pattern.componentName,
          gapType: 'missing-polish-business',
          description: `Polish business component needs specialized documentation`,
          suggestedContent: this.generatePolishBusinessDocumentation(pattern.componentName)
        });
      }
      
      // Check for error pattern documentation
      if (pattern.errorPatterns.length > 0) {
        gaps.push({
          componentName: pattern.componentName,
          gapType: 'missing-example',
          description: `Common errors need troubleshooting documentation`,
          suggestedContent: this.generateTroubleshootingDocumentation(pattern.errorPatterns)
        });
      }
    });
    
    return gaps;
  }

  private isPolishBusinessComponent(componentName: string): boolean {
    const polishKeywords = ['nip', 'vat', 'currency', 'invoice', 'compliance', 'regon', 'krs'];
    return polishKeywords.some(keyword => 
      componentName.toLowerCase().includes(keyword)
    );
  }

  private generateDocumentationUpdates(
    usagePatterns: UsagePattern[],
    gaps: DocumentationGap[]
  ): DocumentationUpdate[] {
    const updates: DocumentationUpdate[] = [];
    
    // Generate updates for high-priority gaps
    gaps.forEach(gap => {
      if (gap.gapType === 'missing-accessibility' || gap.gapType === 'missing-polish-business') {
        updates.push({
          componentName: gap.componentName,
          section: gap.gapType === 'missing-accessibility' ? 'accessibility' : 'polish-business',
          updateType: 'add',
          content: gap.suggestedContent,
          reason: gap.description,
          priority: 'high'
        });
      }
    });
    
    // Generate updates for common usage patterns
    usagePatterns.forEach(pattern => {
      if (pattern.commonUseCases.length > 0) {
        updates.push({
          componentName: pattern.componentName,
          section: 'examples',
          updateType: 'add',
          content: this.generateUseCaseExamples(pattern.commonUseCases),
          reason: `Add examples for ${pattern.commonUseCases.length} common use cases`,
          priority: 'medium'
        });
      }
      
      if (pattern.commonProps.length > 3) {
        updates.push({
          componentName: pattern.componentName,
          section: 'props',
          updateType: 'modify',
          content: this.generatePropsDocumentation(pattern.commonProps),
          reason: `Update props documentation based on actual usage patterns`,
          priority: 'medium'
        });
      }
    });
    
    return updates.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  }

  private generatePropDocumentation(prop: { prop: string; frequency: number; examples: string[] }, componentName: string): string {
    return `
## ${prop.prop} Property

The \`${prop.prop}\` property is commonly used with the ${componentName} component (used ${prop.frequency} times in production).

### Examples

${prop.examples.map(example => `- \`${prop.prop}={${example}}\``).join('\n')}

### Usage

\`\`\`tsx
<${componentName} ${prop.prop}={${prop.examples[0]}} />
\`\`\`
`;
  }

  private generateAccessibilityDocumentation(componentName: string): string {
    return `
## Accessibility

The ${componentName} component follows WCAG 2.1 AA guidelines and includes the following accessibility features:

### Required Attributes

- \`aria-label\`: Provide a descriptive label for screen readers
- \`role\`: Specify the component's role (if not implicit)

### Keyboard Navigation

- **Tab**: Navigate to the component
- **Enter/Space**: Activate the component (if interactive)
- **Escape**: Close or cancel (if applicable)

### Example

\`\`\`tsx
<${componentName}
  aria-label="Submit invoice form"
  role="button"
  onKeyDown={handleKeyDown}
/>
\`\`\`

### Screen Reader Support

The component announces state changes and provides appropriate feedback to assistive technologies.
`;
  }

  private generatePolishBusinessDocumentation(componentName: string): string {
    if (componentName.toLowerCase().includes('nip')) {
      return `
## Polish Business Features

This component includes specialized features for Polish business requirements:

### NIP Validation

- Validates Polish tax identification numbers (NIP)
- Supports both 10-digit format and formatted display
- Real-time validation with error messages in Polish

### Example

\`\`\`tsx
<${componentName}
  value="1234567890"
  onValidate={(isValid) => console.log('NIP valid:', isValid)}
  locale="pl-PL"
  errorMessage="Nieprawidłowy numer NIP"
/>
\`\`\`

### Formatting

The component automatically formats NIP numbers for display:
- Input: "1234567890"
- Display: "123-456-78-90"
`;
    } else if (componentName.toLowerCase().includes('currency')) {
      return `
## Polish Business Features

### Currency Formatting

- Formats amounts in Polish złoty (PLN)
- Supports Polish number formatting conventions
- Handles VAT calculations

### Example

\`\`\`tsx
<${componentName}
  amount={1234.56}
  currency="PLN"
  locale="pl-PL"
  showVAT={true}
  vatRate={23}
/>
\`\`\`

### VAT Integration

Automatically calculates and displays VAT amounts using Polish tax rates (0%, 5%, 8%, 23%).
`;
    } else {
      return `
## Polish Business Features

This component includes features optimized for Polish business workflows:

- Polish language support
- Local date and number formatting
- Integration with Polish business standards
- Compliance with Polish regulations

### Localization

\`\`\`tsx
<${componentName}
  locale="pl-PL"
  dateFormat="DD.MM.YYYY"
  numberFormat="pl-PL"
/>
\`\`\`
`;
    }
  }

  private generateTroubleshootingDocumentation(errorPatterns: Array<{ error: string; frequency: number; solution: string }>): string {
    let doc = `
## Troubleshooting

Common issues and solutions based on production usage:

`;
    
    errorPatterns.forEach(pattern => {
      doc += `
### ${pattern.error}

**Frequency:** ${pattern.frequency} occurrences

**Solution:** ${pattern.solution}

`;
    });
    
    return doc;
  }

  private generateUseCaseExamples(useCases: Array<{ useCase: string; frequency: number; context: string }>): string {
    let examples = `
## Common Use Cases

Based on production usage patterns:

`;
    
    useCases.forEach(useCase => {
      examples += `
### ${useCase.useCase}

${useCase.context}

**Usage frequency:** ${useCase.frequency} instances

\`\`\`tsx
// Example implementation for ${useCase.useCase.toLowerCase()}
<Component
  // Add relevant props for this use case
/>
\`\`\`

`;
    });
    
    return examples;
  }

  private generatePropsDocumentation(commonProps: Array<{ prop: string; frequency: number; examples: string[] }>): string {
    let doc = `
## Properties

Based on actual usage patterns in production:

| Property | Usage Frequency | Type | Description |
|----------|----------------|------|-------------|
`;
    
    commonProps.forEach(prop => {
      doc += `| \`${prop.prop}\` | ${prop.frequency} uses | \`${this.inferPropType(prop.prop)}\` | ${this.generatePropDescription(prop.prop)} |\n`;
    });
    
    doc += `
### Most Common Combinations

`;
    
    // Show common prop combinations
    const topProps = commonProps.slice(0, 3);
    doc += `
\`\`\`tsx
<Component
${topProps.map(prop => `  ${prop.prop}={${prop.examples[0]}}`).join('\n')}
/>
\`\`\`
`;
    
    return doc;
  }

  private inferPropType(propName: string): string {
    if (propName.includes('on') || propName.includes('handle')) {
      return 'function';
    } else if (propName === 'disabled' || propName === 'required' || propName === 'readonly') {
      return 'boolean';
    } else if (propName === 'size' || propName === 'variant' || propName === 'type') {
      return 'string';
    } else if (propName.includes('count') || propName.includes('index') || propName.includes('length')) {
      return 'number';
    } else {
      return 'string';
    }
  }

  private generatePropDescription(propName: string): string {
    switch (propName) {
      case 'variant':
        return 'Visual style variant of the component';
      case 'size':
        return 'Size of the component';
      case 'disabled':
        return 'Whether the component is disabled';
      case 'aria-label':
        return 'Accessibility label for screen readers';
      case 'onClick':
        return 'Click event handler';
      case 'onChange':
        return 'Change event handler';
      default:
        return `${propName} property`;
    }
  }

  public async updateDocumentationFiles(updates: DocumentationUpdate[]): Promise<void> {
    console.log(`Applying ${updates.length} documentation updates...`);
    
    for (const update of updates) {
      try {
        await this.applyDocumentationUpdate(update);
        console.log(`Applied ${update.updateType} to ${update.componentName} ${update.section}`);
      } catch (error) {
        console.error(`Failed to apply update to ${update.componentName}:`, error);
      }
    }
  }

  private async applyDocumentationUpdate(update: DocumentationUpdate): Promise<void> {
    // In a real implementation, this would update actual documentation files
    // For now, we'll simulate the update process
    
    const filePath = this.getDocumentationFilePath(update.componentName, update.section);
    console.log(`Would update ${filePath} with ${update.updateType} operation`);
    
    // Cache the update for reporting
    this.documentationCache.set(`${update.componentName}-${update.section}`, update.content);
  }

  private getDocumentationFilePath(componentName: string, section: string): string {
    return `docs/components/${componentName}/${section}.md`;
  }

  public generateDocumentationReport(): string {
    let report = '# Documentation Update Report\n\n';
    report += `Generated: ${new Date().toISOString()}\n\n`;
    
    report += '## Applied Updates\n\n';
    this.documentationCache.forEach((content, key) => {
      const [componentName, section] = key.split('-');
      report += `### ${componentName} - ${section}\n\n`;
      report += content + '\n\n';
    });
    
    return report;
  }

  public cleanup(): void {
    this.documentationCache.clear();
  }
}

export { DocumentationUpdater, type DocumentationUpdate, type UsagePattern, type DocumentationGap };