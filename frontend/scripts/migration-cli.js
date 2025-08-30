#!/usr/bin/env node

/**
 * Migration CLI Tool for Design System Integration
 * 
 * This tool provides automated component replacement, analysis, and validation
 * for migrating from legacy components to design system components.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const CONFIG = {
  sourceDir: path.join(__dirname, '../src'),
  outputDir: path.join(__dirname, '../migration-reports'),
  backupDir: path.join(__dirname, '../migration-backups'),
  componentMappings: {
    'Button': '@design-system/Button',
    'Input': '@design-system/Input',
    'Form': '@design-system/Form',
    'Table': '@design-system/Table',
    'Card': '@design-system/Card',
    'Select': '@design-system/Select',
    'Checkbox': '@design-system/Checkbox',
    'Radio': '@design-system/Radio',
  },
  polishBusinessComponents: {
    'CurrencyInput': '@design-system/polish-business/CurrencyInput',
    'VATRateSelector': '@design-system/polish-business/VATRateSelector',
    'NIPValidator': '@design-system/polish-business/NIPValidator',
    'DatePicker': '@design-system/polish-business/DatePicker',
    'InvoiceStatusBadge': '@design-system/polish-business/InvoiceStatusBadge',
    'ComplianceIndicator': '@design-system/polish-business/ComplianceIndicator',
  },
  fileExtensions: ['.tsx', '.ts', '.jsx', '.js'],
  excludePatterns: [
    'node_modules',
    'build',
    'dist',
    '.git',
    'migration-reports',
    'migration-backups',
  ],
};

/**
 * CLI Command Handler
 */
class MigrationCLI {
  constructor() {
    this.ensureDirectories();
  }

  /**
   * Ensure required directories exist
   */
  ensureDirectories() {
    [CONFIG.outputDir, CONFIG.backupDir].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  /**
   * Main CLI entry point
   */
  run() {
    const args = process.argv.slice(2);
    const command = args[0];

    switch (command) {
      case 'analyze':
        this.analyzeComponents(args.slice(1));
        break;
      case 'migrate':
        this.migrateComponent(args.slice(1));
        break;
      case 'validate':
        this.validateMigration(args.slice(1));
        break;
      case 'rollback':
        this.rollbackMigration(args.slice(1));
        break;
      case 'report':
        this.generateReport(args.slice(1));
        break;
      case 'help':
      default:
        this.showHelp();
        break;
    }
  }

  /**
   * Analyze component usage across the codebase
   */
  analyzeComponents(args) {
    console.log('🔍 Analyzing component usage...\n');

    const targetComponent = args[0];
    const files = this.findFiles(CONFIG.sourceDir);
    const analysis = {
      timestamp: new Date().toISOString(),
      totalFiles: files.length,
      components: {},
      polishBusinessComponents: {},
      migrationCandidates: [],
      issues: [],
    };

    // Analyze each file
    files.forEach(filePath => {
      const content = fs.readFileSync(filePath, 'utf8');
      this.analyzeFile(filePath, content, analysis, targetComponent);
    });

    // Generate analysis report
    const reportPath = path.join(CONFIG.outputDir, `analysis-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(analysis, null, 2));

    // Display summary
    this.displayAnalysisSummary(analysis);
    console.log(`\n📄 Full analysis report saved to: ${reportPath}`);
  }

  /**
   * Analyze a single file for component usage
   */
  analyzeFile(filePath, content, analysis, targetComponent) {
    const relativePath = path.relative(CONFIG.sourceDir, filePath);

    // Find component imports
    const importRegex = /import\s+(?:{[^}]*}|\w+)\s+from\s+['"]([^'"]+)['"]/g;
    let match;

    while ((match = importRegex.exec(content)) !== null) {
      const importPath = match[1];
      
      // Check for legacy component imports
      Object.keys(CONFIG.componentMappings).forEach(component => {
        if (importPath.includes(component) && !importPath.includes('@design-system')) {
          if (!analysis.components[component]) {
            analysis.components[component] = [];
          }
          analysis.components[component].push({
            file: relativePath,
            importPath,
            line: this.getLineNumber(content, match.index),
          });
        }
      });

      // Check for Polish business component opportunities
      Object.keys(CONFIG.polishBusinessComponents).forEach(component => {
        if (content.includes(component) && !importPath.includes('@design-system')) {
          if (!analysis.polishBusinessComponents[component]) {
            analysis.polishBusinessComponents[component] = [];
          }
          analysis.polishBusinessComponents[component].push({
            file: relativePath,
            context: this.getContext(content, component),
            line: this.getLineNumber(content, content.indexOf(component)),
          });
        }
      });
    }

    // Find component usage patterns
    Object.keys(CONFIG.componentMappings).forEach(component => {
      const usageRegex = new RegExp(`<${component}[^>]*>`, 'g');
      let usageMatch;

      while ((usageMatch = usageRegex.exec(content)) !== null) {
        analysis.migrationCandidates.push({
          component,
          file: relativePath,
          usage: usageMatch[0],
          line: this.getLineNumber(content, usageMatch.index),
          migrationTarget: CONFIG.componentMappings[component],
        });
      }
    });

    // Check for potential issues
    this.checkForIssues(filePath, content, analysis);
  }

  /**
   * Check for potential migration issues
   */
  checkForIssues(filePath, content, analysis) {
    const relativePath = path.relative(CONFIG.sourceDir, filePath);
    const issues = [];

    // Check for inline styles that might conflict
    if (content.includes('style={{')) {
      issues.push({
        type: 'inline-styles',
        message: 'File contains inline styles that may conflict with design system',
        file: relativePath,
      });
    }

    // Check for CSS class usage that might conflict
    const classNameRegex = /className=['"]([^'"]*)['"]/g;
    let match;
    while ((match = classNameRegex.exec(content)) !== null) {
      const classes = match[1];
      if (classes.includes('btn-') || classes.includes('form-') || classes.includes('table-')) {
        issues.push({
          type: 'legacy-css-classes',
          message: `Legacy CSS classes found: ${classes}`,
          file: relativePath,
          line: this.getLineNumber(content, match.index),
        });
      }
    }

    // Check for Polish business logic that could use specialized components
    const polishPatterns = [
      /NIP\s*[:=]/i,
      /VAT\s*[:=]/i,
      /PLN|zł/,
      /\d{2}[.-]\d{2}[.-]\d{4}/, // Polish date format
    ];

    polishPatterns.forEach((pattern, index) => {
      if (pattern.test(content)) {
        const patternNames = ['NIP validation', 'VAT handling', 'Currency formatting', 'Date formatting'];
        issues.push({
          type: 'polish-business-opportunity',
          message: `Could benefit from Polish business component for ${patternNames[index]}`,
          file: relativePath,
        });
      }
    });

    analysis.issues.push(...issues);
  }

  /**
   * Get line number for a character index
   */
  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  /**
   * Get context around a match
   */
  getContext(content, searchTerm) {
    const index = content.indexOf(searchTerm);
    const start = Math.max(0, index - 50);
    const end = Math.min(content.length, index + searchTerm.length + 50);
    return content.substring(start, end).replace(/\n/g, ' ').trim();
  }

  /**
   * Display analysis summary
   */
  displayAnalysisSummary(analysis) {
    console.log('📊 Analysis Summary:');
    console.log(`   Total files analyzed: ${analysis.totalFiles}`);
    console.log(`   Migration candidates: ${analysis.migrationCandidates.length}`);
    console.log(`   Potential issues: ${analysis.issues.length}\n`);

    // Component usage summary
    console.log('🔧 Component Usage:');
    Object.entries(analysis.components).forEach(([component, usages]) => {
      console.log(`   ${component}: ${usages.length} file(s)`);
    });

    // Polish business opportunities
    if (Object.keys(analysis.polishBusinessComponents).length > 0) {
      console.log('\n🇵🇱 Polish Business Component Opportunities:');
      Object.entries(analysis.polishBusinessComponents).forEach(([component, usages]) => {
        console.log(`   ${component}: ${usages.length} opportunity(ies)`);
      });
    }

    // Issues summary
    if (analysis.issues.length > 0) {
      console.log('\n⚠️  Potential Issues:');
      const issueTypes = {};
      analysis.issues.forEach(issue => {
        issueTypes[issue.type] = (issueTypes[issue.type] || 0) + 1;
      });
      Object.entries(issueTypes).forEach(([type, count]) => {
        console.log(`   ${type}: ${count} issue(s)`);
      });
    }
  }

  /**
   * Migrate a specific component
   */
  migrateComponent(args) {
    const componentName = args[0];
    const filePath = args[1];
    const dryRun = args.includes('--dry-run');

    if (!componentName) {
      console.error('❌ Component name is required');
      console.log('Usage: npm run migrate:cli migrate <component-name> [file-path] [--dry-run]');
      return;
    }

    console.log(`🔄 Migrating ${componentName}${filePath ? ` in ${filePath}` : ' across all files'}...\n`);

    const files = filePath ? [filePath] : this.findFiles(CONFIG.sourceDir);
    const migrationResults = {
      timestamp: new Date().toISOString(),
      component: componentName,
      totalFiles: files.length,
      modifiedFiles: [],
      errors: [],
      dryRun,
    };

    files.forEach(file => {
      try {
        const result = this.migrateComponentInFile(file, componentName, dryRun);
        if (result.modified) {
          migrationResults.modifiedFiles.push(result);
        }
      } catch (error) {
        migrationResults.errors.push({
          file,
          error: error.message,
        });
      }
    });

    // Save migration report
    const reportPath = path.join(CONFIG.outputDir, `migration-${componentName}-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(migrationResults, null, 2));

    // Display results
    console.log(`✅ Migration ${dryRun ? 'analysis' : 'completed'}:`);
    console.log(`   Files modified: ${migrationResults.modifiedFiles.length}`);
    console.log(`   Errors: ${migrationResults.errors.length}`);
    console.log(`   Report saved to: ${reportPath}`);

    if (migrationResults.errors.length > 0) {
      console.log('\n❌ Errors:');
      migrationResults.errors.forEach(error => {
        console.log(`   ${error.file}: ${error.error}`);
      });
    }
  }

  /**
   * Migrate component in a specific file
   */
  migrateComponentInFile(filePath, componentName, dryRun) {
    const content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    let modifiedContent = content;
    let modified = false;

    const targetImport = CONFIG.componentMappings[componentName] || 
                        CONFIG.polishBusinessComponents[componentName];

    if (!targetImport) {
      throw new Error(`Unknown component: ${componentName}`);
    }

    // Create backup if not dry run
    if (!dryRun) {
      this.createBackup(filePath, originalContent);
    }

    // Replace imports
    const importRegex = new RegExp(
      `import\\s+(?:{[^}]*${componentName}[^}]*}|${componentName})\\s+from\\s+['"][^'"]+['"]`,
      'g'
    );

    modifiedContent = modifiedContent.replace(importRegex, (match) => {
      if (!match.includes('@design-system')) {
        modified = true;
        return `import { ${componentName} } from '${targetImport}';`;
      }
      return match;
    });

    // Update prop usage if needed
    const propMappings = this.getComponentPropMappings(componentName);
    if (propMappings) {
      Object.entries(propMappings).forEach(([oldProp, newProp]) => {
        const propRegex = new RegExp(`${oldProp}=`, 'g');
        if (propRegex.test(modifiedContent)) {
          modifiedContent = modifiedContent.replace(propRegex, `${newProp}=`);
          modified = true;
        }
      });
    }

    // Write changes if not dry run
    if (!dryRun && modified) {
      fs.writeFileSync(filePath, modifiedContent);
    }

    return {
      file: path.relative(CONFIG.sourceDir, filePath),
      modified,
      changes: modified ? this.getChangeSummary(originalContent, modifiedContent) : [],
    };
  }

  /**
   * Get component prop mappings for migration
   */
  getComponentPropMappings(componentName) {
    const mappings = {
      'Button': {
        'primary': 'variant="primary"',
        'secondary': 'variant="secondary"',
        'large': 'size="lg"',
        'small': 'size="sm"',
      },
      'Input': {
        'fullWidth': 'className="w-full"',
        'error': 'variant="error"',
      },
      'CurrencyInput': {
        'currency': 'currency="PLN"',
      },
    };

    return mappings[componentName];
  }

  /**
   * Get summary of changes made
   */
  getChangeSummary(original, modified) {
    const changes = [];
    
    // Simple diff - in a real implementation, you'd use a proper diff library
    const originalLines = original.split('\n');
    const modifiedLines = modified.split('\n');
    
    for (let i = 0; i < Math.max(originalLines.length, modifiedLines.length); i++) {
      if (originalLines[i] !== modifiedLines[i]) {
        changes.push({
          line: i + 1,
          old: originalLines[i] || '',
          new: modifiedLines[i] || '',
        });
      }
    }
    
    return changes;
  }

  /**
   * Create backup of file before migration
   */
  createBackup(filePath, content) {
    const relativePath = path.relative(CONFIG.sourceDir, filePath);
    const backupPath = path.join(CONFIG.backupDir, `${Date.now()}-${relativePath.replace(/[/\\]/g, '-')}`);
    
    // Ensure backup directory exists
    const backupDir = path.dirname(backupPath);
    if (!fs.existsSync(backupDir)) {
      fs.mkdirSync(backupDir, { recursive: true });
    }
    
    fs.writeFileSync(backupPath, content);
  }

  /**
   * Validate migration results
   */
  validateMigration(args) {
    console.log('🔍 Validating migration...\n');

    const files = this.findFiles(CONFIG.sourceDir);
    const validation = {
      timestamp: new Date().toISOString(),
      totalFiles: files.length,
      validationResults: [],
      errors: [],
      warnings: [],
      summary: {
        passed: 0,
        failed: 0,
        warnings: 0,
      },
    };

    files.forEach(filePath => {
      try {
        const result = this.validateFile(filePath);
        validation.validationResults.push(result);
        
        if (result.passed) {
          validation.summary.passed++;
        } else {
          validation.summary.failed++;
        }
        
        validation.summary.warnings += result.warnings.length;
        validation.errors.push(...result.errors);
        validation.warnings.push(...result.warnings);
      } catch (error) {
        validation.errors.push({
          file: filePath,
          error: error.message,
        });
        validation.summary.failed++;
      }
    });

    // Save validation report
    const reportPath = path.join(CONFIG.outputDir, `validation-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(validation, null, 2));

    // Display results
    console.log('✅ Validation Results:');
    console.log(`   Passed: ${validation.summary.passed}`);
    console.log(`   Failed: ${validation.summary.failed}`);
    console.log(`   Warnings: ${validation.summary.warnings}`);
    console.log(`   Report saved to: ${reportPath}`);

    if (validation.errors.length > 0) {
      console.log('\n❌ Critical Issues:');
      validation.errors.slice(0, 5).forEach(error => {
        console.log(`   ${error.file || 'Unknown'}: ${error.error || error.message}`);
      });
      if (validation.errors.length > 5) {
        console.log(`   ... and ${validation.errors.length - 5} more errors`);
      }
    }
  }

  /**
   * Validate a single file
   */
  validateFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const relativePath = path.relative(CONFIG.sourceDir, filePath);
    
    const result = {
      file: relativePath,
      passed: true,
      errors: [],
      warnings: [],
    };

    // Check for mixed component usage (legacy + design system)
    const hasLegacyComponents = this.hasLegacyComponents(content);
    const hasDesignSystemComponents = this.hasDesignSystemComponents(content);
    
    if (hasLegacyComponents && hasDesignSystemComponents) {
      result.warnings.push({
        type: 'mixed-components',
        message: 'File contains both legacy and design system components',
      });
    }

    // Check for missing imports
    Object.keys(CONFIG.componentMappings).forEach(component => {
      const usageRegex = new RegExp(`<${component}[^>]*>`, 'g');
      const importRegex = new RegExp(`import.*${component}.*from.*@design-system`, 'g');
      
      if (usageRegex.test(content) && !importRegex.test(content)) {
        result.errors.push({
          type: 'missing-import',
          message: `Component ${component} is used but not imported from design system`,
        });
        result.passed = false;
      }
    });

    // Check for deprecated prop usage
    this.checkDeprecatedProps(content, result);

    // Check for accessibility issues
    this.checkAccessibility(content, result);

    return result;
  }

  /**
   * Check if file has legacy components
   */
  hasLegacyComponents(content) {
    return Object.keys(CONFIG.componentMappings).some(component => {
      const importRegex = new RegExp(`import.*${component}.*from.*(?!@design-system)`, 'g');
      return importRegex.test(content);
    });
  }

  /**
   * Check if file has design system components
   */
  hasDesignSystemComponents(content) {
    return content.includes('@design-system');
  }

  /**
   * Check for deprecated prop usage
   */
  checkDeprecatedProps(content, result) {
    const deprecatedProps = {
      'primary': 'Use variant="primary" instead',
      'secondary': 'Use variant="secondary" instead',
      'fullWidth': 'Use className="w-full" instead',
      'large': 'Use size="lg" instead',
      'small': 'Use size="sm" instead',
    };

    Object.entries(deprecatedProps).forEach(([prop, message]) => {
      const propRegex = new RegExp(`${prop}(?:=|\\s)`, 'g');
      if (propRegex.test(content)) {
        result.warnings.push({
          type: 'deprecated-prop',
          message: `Deprecated prop '${prop}': ${message}`,
        });
      }
    });
  }

  /**
   * Check for accessibility issues
   */
  checkAccessibility(content, result) {
    // Check for missing alt text on images
    const imgRegex = /<img[^>]*>/g;
    let match;
    while ((match = imgRegex.exec(content)) !== null) {
      if (!match[0].includes('alt=')) {
        result.warnings.push({
          type: 'accessibility',
          message: 'Image missing alt attribute',
        });
      }
    }

    // Check for buttons without accessible text
    const buttonRegex = /<button[^>]*>([^<]*)</g;
    while ((match = buttonRegex.exec(content)) !== null) {
      const buttonContent = match[1].trim();
      if (!buttonContent && !match[0].includes('aria-label')) {
        result.warnings.push({
          type: 'accessibility',
          message: 'Button without accessible text or aria-label',
        });
      }
    }
  }

  /**
   * Rollback migration
   */
  rollbackMigration(args) {
    const backupId = args[0];
    
    if (!backupId) {
      console.log('📋 Available backups:');
      this.listBackups();
      return;
    }

    console.log(`🔄 Rolling back migration using backup ${backupId}...\n`);

    try {
      this.restoreFromBackup(backupId);
      console.log('✅ Rollback completed successfully');
    } catch (error) {
      console.error('❌ Rollback failed:', error.message);
    }
  }

  /**
   * List available backups
   */
  listBackups() {
    const backups = fs.readdirSync(CONFIG.backupDir)
      .filter(file => file.match(/^\d+/))
      .sort((a, b) => {
        const aTime = parseInt(a.split('-')[0]);
        const bTime = parseInt(b.split('-')[0]);
        return bTime - aTime; // Most recent first
      });

    if (backups.length === 0) {
      console.log('   No backups available');
      return;
    }

    backups.slice(0, 10).forEach(backup => {
      const timestamp = parseInt(backup.split('-')[0]);
      const date = new Date(timestamp).toLocaleString();
      const file = backup.substring(backup.indexOf('-') + 1).replace(/-/g, '/');
      console.log(`   ${timestamp}: ${file} (${date})`);
    });

    if (backups.length > 10) {
      console.log(`   ... and ${backups.length - 10} more backups`);
    }
  }

  /**
   * Restore from backup
   */
  restoreFromBackup(backupId) {
    const backupFiles = fs.readdirSync(CONFIG.backupDir)
      .filter(file => file.startsWith(backupId));

    if (backupFiles.length === 0) {
      throw new Error(`No backup found with ID: ${backupId}`);
    }

    backupFiles.forEach(backupFile => {
      const backupPath = path.join(CONFIG.backupDir, backupFile);
      const originalPath = backupFile.substring(backupFile.indexOf('-') + 1).replace(/-/g, '/');
      const targetPath = path.join(CONFIG.sourceDir, originalPath);

      const backupContent = fs.readFileSync(backupPath, 'utf8');
      
      // Ensure target directory exists
      const targetDir = path.dirname(targetPath);
      if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
      }

      fs.writeFileSync(targetPath, backupContent);
      console.log(`   Restored: ${originalPath}`);
    });
  }

  /**
   * Generate comprehensive migration report
   */
  generateReport(args) {
    console.log('📊 Generating comprehensive migration report...\n');

    const reportType = args[0] || 'full';
    const report = {
      timestamp: new Date().toISOString(),
      type: reportType,
      summary: {},
      details: {},
    };

    // Run analysis
    const files = this.findFiles(CONFIG.sourceDir);
    const analysis = { components: {}, polishBusinessComponents: {}, migrationCandidates: [], issues: [] };
    
    files.forEach(filePath => {
      const content = fs.readFileSync(filePath, 'utf8');
      this.analyzeFile(filePath, content, analysis);
    });

    report.summary = {
      totalFiles: files.length,
      componentsFound: Object.keys(analysis.components).length,
      migrationCandidates: analysis.migrationCandidates.length,
      issues: analysis.issues.length,
      polishBusinessOpportunities: Object.keys(analysis.polishBusinessComponents).length,
    };

    report.details = {
      componentUsage: analysis.components,
      polishBusinessComponents: analysis.polishBusinessComponents,
      migrationCandidates: analysis.migrationCandidates,
      issues: analysis.issues,
    };

    // Save report
    const reportPath = path.join(CONFIG.outputDir, `comprehensive-report-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    // Generate HTML report
    this.generateHTMLReport(report, reportPath.replace('.json', '.html'));

    console.log('✅ Report generated:');
    console.log(`   JSON: ${reportPath}`);
    console.log(`   HTML: ${reportPath.replace('.json', '.html')}`);
  }

  /**
   * Generate HTML report
   */
  generateHTMLReport(report, outputPath) {
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Report - ${new Date(report.timestamp).toLocaleDateString()}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric { background: #f8f9fa; padding: 20px; border-radius: 6px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #007bff; }
        .metric-label { color: #666; margin-top: 5px; }
        .section { margin: 30px 0; }
        .component-list { display: grid; gap: 10px; }
        .component-item { background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff; }
        .issue-item { background: #fff3cd; padding: 15px; border-radius: 6px; border-left: 4px solid #ffc107; }
        .error-item { background: #f8d7da; padding: 15px; border-radius: 6px; border-left: 4px solid #dc3545; }
        .file-path { font-family: monospace; font-size: 0.9em; color: #666; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        .progress-bar { width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: #007bff; transition: width 0.3s ease; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Design System Migration Report</h1>
        <p><strong>Generated:</strong> ${new Date(report.timestamp).toLocaleString()}</p>
        
        <div class="section">
            <h2>Summary</h2>
            <div class="summary">
                <div class="metric">
                    <div class="metric-value">${report.summary.totalFiles}</div>
                    <div class="metric-label">Total Files</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${report.summary.componentsFound}</div>
                    <div class="metric-label">Components Found</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${report.summary.migrationCandidates}</div>
                    <div class="metric-label">Migration Candidates</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${report.summary.issues}</div>
                    <div class="metric-label">Issues Found</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${report.summary.polishBusinessOpportunities}</div>
                    <div class="metric-label">Polish Business Opportunities</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Component Usage</h2>
            <div class="component-list">
                ${Object.entries(report.details.componentUsage).map(([component, usages]) => `
                    <div class="component-item">
                        <h3>${component}</h3>
                        <p><strong>${usages.length}</strong> usage(s) found</p>
                        <details>
                            <summary>View Details</summary>
                            ${usages.map(usage => `
                                <div class="file-path">${usage.file}:${usage.line}</div>
                            `).join('')}
                        </details>
                    </div>
                `).join('')}
            </div>
        </div>

        ${report.details.issues.length > 0 ? `
        <div class="section">
            <h2>Issues & Recommendations</h2>
            <div class="component-list">
                ${report.details.issues.map(issue => `
                    <div class="${issue.type === 'error' ? 'error-item' : 'issue-item'}">
                        <strong>${issue.type.replace('-', ' ').toUpperCase()}:</strong> ${issue.message}
                        ${issue.file ? `<div class="file-path">${issue.file}${issue.line ? `:${issue.line}` : ''}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}

        <div class="section">
            <h2>Migration Candidates</h2>
            <table>
                <thead>
                    <tr>
                        <th>Component</th>
                        <th>File</th>
                        <th>Line</th>
                        <th>Migration Target</th>
                    </tr>
                </thead>
                <tbody>
                    ${report.details.migrationCandidates.map(candidate => `
                        <tr>
                            <td><code>${candidate.component}</code></td>
                            <td class="file-path">${candidate.file}</td>
                            <td>${candidate.line}</td>
                            <td><code>${candidate.migrationTarget}</code></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
    `;

    fs.writeFileSync(outputPath, html);
  }

  /**
   * Find all relevant files in directory
   */
  findFiles(dir) {
    const files = [];
    
    const walk = (currentDir) => {
      const items = fs.readdirSync(currentDir);
      
      items.forEach(item => {
        const fullPath = path.join(currentDir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          // Skip excluded directories
          if (!CONFIG.excludePatterns.some(pattern => fullPath.includes(pattern))) {
            walk(fullPath);
          }
        } else if (stat.isFile()) {
          // Include files with relevant extensions
          if (CONFIG.fileExtensions.some(ext => fullPath.endsWith(ext))) {
            files.push(fullPath);
          }
        }
      });
    };
    
    walk(dir);
    return files;
  }

  /**
   * Show help information
   */
  showHelp() {
    console.log(`
🚀 Design System Migration CLI

Usage: node migration-cli.js <command> [options]

Commands:
  analyze [component]     Analyze component usage across codebase
  migrate <component>     Migrate component to design system
  validate               Validate migration results
  rollback [backup-id]   Rollback migration using backup
  report [type]          Generate comprehensive migration report
  help                   Show this help message

Examples:
  node migration-cli.js analyze Button
  node migration-cli.js migrate Button --dry-run
  node migration-cli.js validate
  node migration-cli.js rollback 1640995200000
  node migration-cli.js report full

Options:
  --dry-run             Preview changes without applying them
  --verbose             Show detailed output
  --output <path>       Specify output directory for reports

For more information, visit: https://github.com/your-org/design-system-migration
    `);
  }
}

// Run CLI if called directly
if (require.main === module) {
  const cli = new MigrationCLI();
  cli.run();
}

module.exports = MigrationCLI;