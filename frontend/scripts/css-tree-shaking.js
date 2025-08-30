/**
 * CSS Tree Shaking Configuration
 * 
 * Removes unused CSS from the design system to optimize bundle size
 */

const fs = require('fs');
const path = require('path');
const postcss = require('postcss');
const purgecss = require('@fullhuman/postcss-purgecss');
const cssnano = require('cssnano');

class CSSTreeShaker {
  constructor(options = {}) {
    this.options = {
      // Content paths to analyze for used CSS classes
      content: [
        './src/**/*.{js,jsx,ts,tsx}',
        './public/index.html',
        '../faktury/templates/**/*.html',
        '../faktury/templatetags/**/*.py',
      ],
      
      // CSS files to process
      css: [
        './src/design-system/styles/**/*.css',
        './src/**/*.css',
      ],
      
      // Output directory
      outputDir: './build/static/css',
      
      // Safelist for dynamic classes
      safelist: [
        // Design system prefixes
        /^ds-/,
        
        // State classes
        /^(hover|focus|active|disabled|loading|selected|checked):/,
        
        // Responsive classes
        /^(sm|md|lg|xl|2xl):/,
        
        // Polish business classes
        /^(currency|nip|vat|invoice|polish-business)-/,
        
        // Animation classes
        /^animate-/,
        
        // Accessibility
        'sr-only',
        'focus-visible',
        'visually-hidden',
        
        // Common utilities that might be used dynamically
        'text-primary-600',
        'text-success-600',
        'text-warning-600',
        'text-error-600',
        'bg-primary-600',
        'bg-success-600',
        'bg-warning-600',
        'bg-error-600',
        
        // Form states
        'invalid',
        'valid',
        'required',
        'optional',
        
        // Loading states
        'loading',
        'loaded',
        'error',
        
        // Theme classes
        'theme-light',
        'theme-dark',
        'theme-polish-business',
      ],
      
      // Patterns for dynamic classes
      safelistPatterns: [
        // Color utilities
        /^text-(primary|secondary|success|warning|error)-(50|100|200|300|400|500|600|700|800|900)$/,
        /^bg-(primary|secondary|success|warning|error)-(50|100|200|300|400|500|600|700|800|900)$/,
        /^border-(primary|secondary|success|warning|error)-(50|100|200|300|400|500|600|700|800|900)$/,
        
        // Spacing utilities
        /^(p|m|px|py|mx|my|pt|pb|pl|pr|mt|mb|ml|mr)-(0|1|2|3|4|5|6|8|10|12|16|20|24|32)$/,
        
        // Typography utilities
        /^text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl)$/,
        /^font-(thin|extralight|light|normal|medium|semibold|bold|extrabold|black)$/,
        /^leading-(none|tight|snug|normal|relaxed|loose)$/,
        
        // Layout utilities
        /^(w|h|min-w|min-h|max-w|max-h)-(0|1|2|3|4|5|6|8|10|12|16|20|24|32|40|48|56|64|72|80|96|auto|full|screen)$/,
        
        // Border utilities
        /^rounded-(none|xs|sm|md|lg|xl|2xl|3xl|full)$/,
        /^border-(0|1|2|4|8)$/,
        
        // Shadow utilities
        /^shadow-(none|xs|sm|md|lg|xl|2xl|inner)$/,
        
        // Grid utilities
        /^(grid-cols|col-span|row-span)-(1|2|3|4|5|6|7|8|9|10|11|12|auto)$/,
        
        // Flex utilities
        /^(flex|items|justify|content|self)-(start|end|center|between|around|evenly|stretch|baseline)$/,
        
        // Polish business specific patterns
        /^(nip|regon|krs|vat|currency|invoice)-(valid|invalid|pending|processing|completed)$/,
        
        // Component state patterns
        /^(button|input|select|checkbox|radio)-(primary|secondary|success|warning|error|disabled|loading)$/,
      ],
      
      // Blocklist for classes to always remove
      blocklist: [
        // Development only classes
        /^debug-/,
        /^dev-/,
        
        // Unused framework classes
        /^unused-/,
        
        // Old component classes (if migrating)
        /^old-/,
        /^legacy-/,
      ],
      
      ...options,
    };
  }

  /**
   * Process CSS files and remove unused styles
   */
  async processCSSFiles() {
    const results = {
      processed: [],
      errors: [],
      totalSizeBefore: 0,
      totalSizeAfter: 0,
      savings: 0,
    };

    // Find all CSS files
    const cssFiles = await this.findCSSFiles();
    
    for (const cssFile of cssFiles) {
      try {
        const result = await this.processSingleFile(cssFile);
        results.processed.push(result);
        results.totalSizeBefore += result.sizeBefore;
        results.totalSizeAfter += result.sizeAfter;
      } catch (error) {
        results.errors.push({
          file: cssFile,
          error: error.message,
        });
      }
    }

    results.savings = results.totalSizeBefore - results.totalSizeAfter;
    results.savingsPercentage = ((results.savings / results.totalSizeBefore) * 100).toFixed(1);

    return results;
  }

  /**
   * Find all CSS files to process
   */
  async findCSSFiles() {
    const cssFiles = [];
    
    for (const pattern of this.options.css) {
      const files = await this.globFiles(pattern);
      cssFiles.push(...files);
    }
    
    return [...new Set(cssFiles)]; // Remove duplicates
  }

  /**
   * Process a single CSS file
   */
  async processSingleFile(filePath) {
    const originalCSS = fs.readFileSync(filePath, 'utf8');
    const sizeBefore = Buffer.byteLength(originalCSS, 'utf8');

    // Configure PurgeCSS
    const purgeCSSConfig = {
      content: this.options.content,
      safelist: {
        standard: this.options.safelist,
        deep: this.options.safelistPatterns,
      },
      blocklist: this.options.blocklist,
      keyframes: true,
      fontFace: true,
      variables: true,
    };

    // Configure cssnano for minification
    const cssnanoConfig = {
      preset: ['default', {
        discardComments: { removeAll: true },
        normalizeWhitespace: true,
        colormin: true,
        convertValues: true,
        discardDuplicates: true,
        discardEmpty: true,
        mergeRules: true,
        minifyFontValues: true,
        minifyParams: true,
        minifySelectors: true,
        reduceIdents: false, // Keep CSS custom properties
        zindex: false, // Don't optimize z-index values
      }],
    };

    // Process CSS with PostCSS
    const result = await postcss([
      purgecss(purgeCSSConfig),
      cssnano(cssnanoConfig),
    ]).process(originalCSS, {
      from: filePath,
      to: filePath,
    });

    const processedCSS = result.css;
    const sizeAfter = Buffer.byteLength(processedCSS, 'utf8');
    const savings = sizeBefore - sizeAfter;
    const savingsPercentage = ((savings / sizeBefore) * 100).toFixed(1);

    // Write processed CSS to output directory
    const outputPath = this.getOutputPath(filePath);
    await this.ensureDirectoryExists(path.dirname(outputPath));
    fs.writeFileSync(outputPath, processedCSS);

    return {
      file: filePath,
      outputFile: outputPath,
      sizeBefore,
      sizeAfter,
      savings,
      savingsPercentage,
    };
  }

  /**
   * Get output path for processed CSS file
   */
  getOutputPath(inputPath) {
    const relativePath = path.relative(process.cwd(), inputPath);
    const fileName = path.basename(inputPath, '.css');
    const outputFileName = `${fileName}.optimized.css`;
    
    return path.join(this.options.outputDir, outputFileName);
  }

  /**
   * Ensure directory exists
   */
  async ensureDirectoryExists(dirPath) {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
  }

  /**
   * Simple glob implementation for finding files
   */
  async globFiles(pattern) {
    // Simple implementation - in production, use a proper glob library
    const files = [];
    
    if (pattern.includes('**')) {
      // Recursive search
      const baseDir = pattern.split('**')[0];
      const extension = pattern.split('.').pop();
      
      const searchDir = (dir) => {
        if (!fs.existsSync(dir)) return;
        
        const items = fs.readdirSync(dir);
        
        for (const item of items) {
          const fullPath = path.join(dir, item);
          const stat = fs.statSync(fullPath);
          
          if (stat.isDirectory()) {
            searchDir(fullPath);
          } else if (item.endsWith(`.${extension}`)) {
            files.push(fullPath);
          }
        }
      };
      
      searchDir(baseDir);
    } else {
      // Direct file
      if (fs.existsSync(pattern)) {
        files.push(pattern);
      }
    }
    
    return files;
  }

  /**
   * Generate optimization report
   */
  generateReport(results) {
    const report = {
      timestamp: Date.now(),
      summary: {
        filesProcessed: results.processed.length,
        errors: results.errors.length,
        totalSizeBefore: this.formatBytes(results.totalSizeBefore),
        totalSizeAfter: this.formatBytes(results.totalSizeAfter),
        totalSavings: this.formatBytes(results.savings),
        savingsPercentage: results.savingsPercentage,
      },
      files: results.processed,
      errors: results.errors,
      configuration: {
        contentPaths: this.options.content,
        safelistCount: this.options.safelist.length,
        safelistPatternCount: this.options.safelistPatterns.length,
        blocklistCount: this.options.blocklist.length,
      },
    };

    // Write report
    const reportPath = path.join(this.options.outputDir, 'css-optimization-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log('\nCSS Optimization Complete!');
    console.log(`Files processed: ${report.summary.filesProcessed}`);
    console.log(`Total size before: ${report.summary.totalSizeBefore}`);
    console.log(`Total size after: ${report.summary.totalSizeAfter}`);
    console.log(`Total savings: ${report.summary.totalSavings} (${report.summary.savingsPercentage}%)`);
    console.log(`Report saved: ${reportPath}`);

    return report;
  }

  /**
   * Format bytes to human readable format
   */
  formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }
}

// CLI usage
if (require.main === module) {
  const treeShaker = new CSSTreeShaker();
  
  treeShaker.processCSSFiles()
    .then(results => {
      treeShaker.generateReport(results);
    })
    .catch(error => {
      console.error('Error processing CSS files:', error);
      process.exit(1);
    });
}

module.exports = CSSTreeShaker;