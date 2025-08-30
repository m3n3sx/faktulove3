#!/usr/bin/env node

/**
 * Component Migration Script
 * 
 * Automated script to help migrate existing FaktuLove components
 * to use the new design system.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const config = {
  sourceDir: 'src',
  excludeDirs: ['node_modules', '.git', 'build', 'dist'],
  fileExtensions: ['.js', '.jsx', '.ts', '.tsx'],
  backupDir: 'migration-backups',
  dryRun: process.argv.includes('--dry-run'),
  verbose: process.argv.includes('--verbose')
};

// Component mappings for automated migration
const componentMappings = [
  {
    pattern: /className="([^"]*bg-primary-600[^"]*)"/g,
    replacement: 'variant="primary"',
    component: 'Button',
    import: "import { Button } from '@/design-system';"
  },
  {
    pattern: /className="([^"]*border border-gray-300[^"]*)"/g,
    replacement: 'variant="secondary"',
    component: 'Button',
    import: "import { Button } from '@/design-system';"
  },
  {
    pattern: /className="([^"]*max-w-7xl mx-auto[^"]*)"/g,
    replacement: 'maxWidth="7xl"',
    component: 'Container',
    import: "import { Container } from '@/design-system';"
  },
  {
    pattern: /className="([^"]*grid grid-cols-(\d+)[^"]*)"/g,
    replacement: (match, fullClass, cols) => `cols={${cols}}`,
    component: 'Grid',
    import: "import { Grid } from '@/design-system';"
  }
];

// Style mappings for CSS class migration
const styleMappings = [
  { from: 'text-green-600', to: 'text-success-600' },
  { from: 'bg-green-600', to: 'bg-success-600' },
  { from: 'text-red-600', to: 'text-error-600' },
  { from: 'bg-red-600', to: 'bg-error-600' },
  { from: 'text-yellow-600', to: 'text-warning-600' },
  { from: 'bg-yellow-600', to: 'bg-warning-600' },
  { from: 'rounded', to: 'rounded-md' },
  { from: 'shadow', to: 'shadow-sm' }
];

class ComponentMigrator {
  constructor() {
    this.migratedFiles = [];
    this.errors = [];
    this.warnings = [];
    this.stats = {
      filesProcessed: 0,
      componentsUpdated: 0,
      stylesUpdated: 0,
      importsAdded: 0
    };
  }

  /**
   * Main migration process
   */
  async migrate() {
    console.log('🚀 Starting FaktuLove Design System Migration...\n');
    
    if (config.dryRun) {
      console.log('🔍 Running in DRY RUN mode - no files will be modified\n');
    }

    try {
      // Create backup directory
      if (!config.dryRun) {
        this.createBackupDirectory();
      }

      // Find all component files
      const files = this.findComponentFiles(config.sourceDir);
      console.log(`📁 Found ${files.length} component files to analyze\n`);

      // Process each file
      for (const file of files) {
        await this.processFile(file);
      }

      // Generate migration report
      this.generateReport();

    } catch (error) {
      console.error('❌ Migration failed:', error.message);
      process.exit(1);
    }
  }

  /**
   * Find all component files to migrate
   */
  findComponentFiles(dir) {
    const files = [];
    
    const scanDirectory = (currentDir) => {
      const items = fs.readdirSync(currentDir);
      
      for (const item of items) {
        const fullPath = path.join(currentDir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          if (!config.excludeDirs.includes(item)) {
            scanDirectory(fullPath);
          }
        } else if (stat.isFile()) {
          const ext = path.extname(item);
          if (config.fileExtensions.includes(ext)) {
            files.push(fullPath);
          }
        }
      }
    };
    
    scanDirectory(dir);
    return files;
  }

  /**
   * Process a single file for migration
   */
  async processFile(filePath) {
    try {
      const originalContent = fs.readFileSync(filePath, 'utf8');
      let content = originalContent;
      let hasChanges = false;
      const fileChanges = {
        components: [],
        styles: [],
        imports: []
      };

      if (config.verbose) {
        console.log(`📄 Processing: ${filePath}`);
      }

      // Backup original file
      if (!config.dryRun) {
        this.backupFile(filePath, originalContent);
      }

      // Apply component mappings
      for (const mapping of componentMappings) {
        const matches = content.match(mapping.pattern);
        if (matches) {
          if (typeof mapping.replacement === 'function') {
            content = content.replace(mapping.pattern, mapping.replacement);
          } else {
            content = content.replace(mapping.pattern, mapping.replacement);
          }
          
          hasChanges = true;
          fileChanges.components.push(mapping.component);
          
          // Add import if not already present
          if (!content.includes(mapping.import)) {
            content = this.addImport(content, mapping.import);
            fileChanges.imports.push(mapping.component);
          }
        }
      }

      // Apply style mappings
      for (const styleMapping of styleMappings) {
        if (content.includes(styleMapping.from)) {
          const regex = new RegExp(`\\b${styleMapping.from}\\b`, 'g');
          content = content.replace(regex, styleMapping.to);
          hasChanges = true;
          fileChanges.styles.push(`${styleMapping.from} → ${styleMapping.to}`);
        }
      }

      // Check for Polish business patterns
      const polishPatterns = this.checkPolishBusinessPatterns(content);
      if (polishPatterns.length > 0) {
        this.warnings.push(`${filePath}: Consider using Polish business components: ${polishPatterns.join(', ')}`);
      }

      // Write updated content
      if (hasChanges && !config.dryRun) {
        fs.writeFileSync(filePath, content, 'utf8');
        this.migratedFiles.push({
          path: filePath,
          changes: fileChanges
        });
      }

      // Update statistics
      this.stats.filesProcessed++;
      if (hasChanges) {
        this.stats.componentsUpdated += fileChanges.components.length;
        this.stats.stylesUpdated += fileChanges.styles.length;
        this.stats.importsAdded += fileChanges.imports.length;
      }

      if (config.verbose && hasChanges) {
        console.log(`  ✅ Updated: ${fileChanges.components.length} components, ${fileChanges.styles.length} styles`);
      }

    } catch (error) {
      this.errors.push(`Error processing ${filePath}: ${error.message}`);
    }
  }

  /**
   * Add import statement to file
   */
  addImport(content, importStatement) {
    const lines = content.split('\n');
    let insertIndex = 0;
    
    // Find the last import statement
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].startsWith('import ')) {
        insertIndex = i + 1;
      } else if (lines[i].trim() === '' && insertIndex > 0) {
        break;
      }
    }
    
    lines.splice(insertIndex, 0, importStatement);
    return lines.join('\n');
  }

  /**
   * Check for Polish business patterns
   */
  checkPolishBusinessPatterns(content) {
    const patterns = [];
    
    if (content.includes('PLN') || content.includes('currency')) {
      patterns.push('CurrencyInput');
    }
    
    if (content.includes('NIP') || content.includes('tax number')) {
      patterns.push('NIPValidator');
    }
    
    if (content.includes('VAT') || content.includes('23%')) {
      patterns.push('VATRateSelector');
    }
    
    if (content.includes('DD.MM.YYYY') || content.includes('Polish date')) {
      patterns.push('DatePicker');
    }
    
    return patterns;
  }

  /**
   * Create backup directory
   */
  createBackupDirectory() {
    const backupPath = path.join(process.cwd(), config.backupDir);
    if (!fs.existsSync(backupPath)) {
      fs.mkdirSync(backupPath, { recursive: true });
    }
  }

  /**
   * Backup original file
   */
  backupFile(filePath, content) {
    const relativePath = path.relative(process.cwd(), filePath);
    const backupPath = path.join(config.backupDir, relativePath);
    const backupDir = path.dirname(backupPath);
    
    if (!fs.existsSync(backupDir)) {
      fs.mkdirSync(backupDir, { recursive: true });
    }
    
    fs.writeFileSync(backupPath, content, 'utf8');
  }

  /**
   * Generate migration report
   */
  generateReport() {
    console.log('\n📊 Migration Report');
    console.log('==================');
    console.log(`Files processed: ${this.stats.filesProcessed}`);
    console.log(`Components updated: ${this.stats.componentsUpdated}`);
    console.log(`Styles updated: ${this.stats.stylesUpdated}`);
    console.log(`Imports added: ${this.stats.importsAdded}`);
    console.log(`Files migrated: ${this.migratedFiles.length}`);
    
    if (this.warnings.length > 0) {
      console.log('\n⚠️  Warnings:');
      this.warnings.forEach(warning => console.log(`  ${warning}`));
    }
    
    if (this.errors.length > 0) {
      console.log('\n❌ Errors:');
      this.errors.forEach(error => console.log(`  ${error}`));
    }
    
    if (this.migratedFiles.length > 0) {
      console.log('\n✅ Successfully migrated files:');
      this.migratedFiles.forEach(file => {
        console.log(`  ${file.path}`);
        if (file.changes.components.length > 0) {
          console.log(`    Components: ${file.changes.components.join(', ')}`);
        }
        if (file.changes.styles.length > 0) {
          console.log(`    Styles: ${file.changes.styles.join(', ')}`);
        }
      });
    }
    
    // Generate detailed report file
    const reportPath = path.join(config.backupDir, 'migration-report.json');
    const report = {
      timestamp: new Date().toISOString(),
      config,
      stats: this.stats,
      migratedFiles: this.migratedFiles,
      warnings: this.warnings,
      errors: this.errors
    };
    
    if (!config.dryRun) {
      fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
      console.log(`\n📄 Detailed report saved to: ${reportPath}`);
    }
    
    console.log('\n🎉 Migration completed!');
    
    if (config.dryRun) {
      console.log('\n💡 Run without --dry-run to apply changes');
    } else {
      console.log('\n💡 Next steps:');
      console.log('  1. Review migrated files for correctness');
      console.log('  2. Run tests to ensure functionality');
      console.log('  3. Update any remaining manual migration items');
      console.log('  4. Remove compatibility layer when ready');
    }
  }
}

// CLI interface
if (require.main === module) {
  const migrator = new ComponentMigrator();
  migrator.migrate().catch(error => {
    console.error('Migration failed:', error);
    process.exit(1);
  });
}

module.exports = ComponentMigrator;