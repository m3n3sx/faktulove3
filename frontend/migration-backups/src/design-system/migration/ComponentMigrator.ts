/**
 * Component Migrator
 * 
 * Utilities for migrating existing components to the design system.
 */

import type { ComponentMapping, MigrationReport, MigrationOptions } from './types';
import { migrationConfig } from './config';

export class ComponentMigrator {
  private options: MigrationOptions;
  private mappings: ComponentMapping[];
  
  constructor(options: MigrationOptions = migrationConfig.options) {
    this.options = options;
    this.mappings = migrationConfig.componentMappings;
  }
  
  /**
   * Analyze a component file for migration opportunities
   */
  analyzeFile(fileContent: string, filePath: string): MigrationReport {
    const report: MigrationReport = {
      migratedComponents: [],
      manualMigration: [],
      deprecatedStyles: [],
      warnings: [],
      errors: []
    };
    
    try {
      // Check for component mappings
      this.mappings.forEach(mapping => {
        const regex = this.createMappingRegex(mapping.from);
        const matches = fileContent.match(regex);
        
        if (matches) {
          if (mapping.transformProps) {
            report.migratedComponents.push(`${mapping.from} → ${mapping.to}`);
          } else {
            report.manualMigration.push(`${mapping.from} requires manual migration to ${mapping.to}`);
          }
          
          if (mapping.notes) {
            report.warnings.push(`${filePath}: ${mapping.notes}`);
          }
        }
      });
      
      // Check for deprecated styles
      migrationConfig.styleMappings.forEach(styleMapping => {
        if (styleMapping.deprecated && fileContent.includes(styleMapping.from)) {
          report.deprecatedStyles.push(styleMapping.from);
          if (styleMapping.warning) {
            report.warnings.push(`${filePath}: ${styleMapping.warning}`);
          }
        }
      });
      
      // Check for common patterns that need migration
      this.checkCommonPatterns(fileContent, filePath, report);
      
    } catch (error) {
      report.errors.push(`Error analyzing ${filePath}: ${error}`);
    }
    
    return report;
  }
  
  /**
   * Generate migration suggestions for a component
   */
  generateMigrationSuggestions(componentCode: string): string[] {
    const suggestions: string[] = [];
    
    // Check for button patterns
    if (componentCode.includes('button') && componentCode.includes('className')) {
      suggestions.push('Consider using the Button component from the design system');
      suggestions.push('Replace className-based styling with variant props');
    }
    
    // Check for input patterns
    if (componentCode.includes('input') && componentCode.includes('type=')) {
      suggestions.push('Consider using the Input component from the design system');
      suggestions.push('Use validation states instead of manual border styling');
    }
    
    // Check for grid patterns
    if (componentCode.includes('grid-cols-')) {
      suggestions.push('Consider using the Grid component from the design system');
      suggestions.push('Replace Tailwind grid classes with Grid component props');
    }
    
    // Check for Polish business patterns
    if (componentCode.includes('PLN') || componentCode.includes('currency')) {
      suggestions.push('Consider using CurrencyInput for Polish currency formatting');
    }
    
    if (componentCode.includes('NIP') || componentCode.includes('tax')) {
      suggestions.push('Consider using NIPValidator for Polish tax number validation');
    }
    
    if (componentCode.includes('VAT') || componentCode.includes('23%')) {
      suggestions.push('Consider using VATRateSelector for Polish VAT rates');
    }
    
    return suggestions;
  }
  
  /**
   * Create a regex pattern for component mapping
   */
  private createMappingRegex(pattern: string): RegExp {
    // Convert CSS selector-like patterns to regex
    let regexPattern = pattern
      .replace(/\./g, '\\.')
      .replace(/\[/g, '\\[')
      .replace(/\]/g, '\\]')
      .replace(/\*/g, '.*');
    
    return new RegExp(regexPattern, 'g');
  }
  
  /**
   * Check for common patterns that need migration
   */
  private checkCommonPatterns(
    fileContent: string, 
    filePath: string, 
    report: MigrationReport
  ): void {
    // Check for hardcoded colors
    const colorPatterns = [
      /#[0-9a-fA-F]{6}/g, // Hex colors
      /rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)/g, // RGB colors
      /rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)/g // RGBA colors
    ];
    
    colorPatterns.forEach(pattern => {
      const matches = fileContent.match(pattern);
      if (matches) {
        report.warnings.push(
          `${filePath}: Found hardcoded colors (${matches.join(', ')}). Consider using design tokens.`
        );
      }
    });
    
    // Check for hardcoded spacing values
    const spacingPattern = /padding:\s*\d+px|margin:\s*\d+px/g;
    const spacingMatches = fileContent.match(spacingPattern);
    if (spacingMatches) {
      report.warnings.push(
        `${filePath}: Found hardcoded spacing values. Consider using the 8px grid system.`
      );
    }
    
    // Check for hardcoded font sizes
    const fontSizePattern = /font-size:\s*\d+px/g;
    const fontSizeMatches = fileContent.match(fontSizePattern);
    if (fontSizeMatches) {
      report.warnings.push(
        `${filePath}: Found hardcoded font sizes. Consider using typography tokens.`
      );
    }
    
    // Check for accessibility issues
    if (fileContent.includes('onClick') && !fileContent.includes('onKeyDown')) {
      report.warnings.push(
        `${filePath}: Interactive elements should support keyboard navigation.`
      );
    }
    
    if (fileContent.includes('<button') && !fileContent.includes('aria-')) {
      report.warnings.push(
        `${filePath}: Buttons should include appropriate ARIA attributes.`
      );
    }
  }
  
  /**
   * Generate a migration script for a component
   */
  generateMigrationScript(componentPath: string, targetComponent: string): string {
    return `
// Migration script for ${componentPath}
// Generated by Design System Component Migrator

import { ${targetComponent} } from '@/design-system';

// TODO: Replace legacy component with design system component
// 1. Import the new component
// 2. Replace className-based styling with component props
// 3. Update prop names to match design system API
// 4. Test accessibility and responsive behavior
// 5. Remove legacy styles and dependencies

// Example migration:
// Before:
// <button className="bg-primary-600 text-white px-4 py-2 rounded-md">
//   Click me
// </button>

// After:
// <Button variant="primary" size="md">
//   Click me
// </Button>
`;
  }
}