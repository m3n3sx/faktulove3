/**
 * Critical CSS Extractor
 * 
 * Extracts critical above-the-fold CSS for faster initial page rendering
 */

const fs = require('fs');
const path = require('path');
const postcss = require('postcss');

class CriticalCSSExtractor {
  constructor(options = {}) {
    this.options = {
      // CSS files to analyze
      cssFiles: [
        './src/design-system/styles/base.css',
        './src/design-system/styles/tokens.css',
        './src/design-system/styles/utilities.css',
      ],
      
      // HTML templates to analyze for critical styles
      htmlTemplates: [
        '../faktury/templates/base.html',
        '../faktury/templates/faktury/dashboard.html',
        '../faktury/templates/faktury/invoice_list.html',
        '../faktury/templates/account/login.html',
      ],
      
      // Output paths
      outputDir: './build/static/css',
      criticalCSSFile: 'critical.css',
      nonCriticalCSSFile: 'non-critical.css',
      
      // Critical CSS selectors (always include)
      criticalSelectors: [
        // Base styles
        'html',
        'body',
        '*',
        '*::before',
        '*::after',
        
        // Design system core
        '.ds-theme-light',
        '.ds-theme-dark',
        '.ds-theme-polish-business',
        
        // Layout essentials
        '.ds-container',
        '.ds-grid',
        '.ds-flex',
        '.ds-stack',
        
        // Typography essentials
        '.ds-text-base',
        '.ds-text-lg',
        '.ds-text-xl',
        '.ds-font-normal',
        '.ds-font-medium',
        '.ds-font-semibold',
        
        // Button essentials (likely above fold)
        '.ds-button',
        '.ds-button-primary',
        '.ds-button-secondary',
        
        // Form essentials
        '.ds-input',
        '.ds-label',
        '.ds-form-field',
        
        // Navigation (always above fold)
        '.ds-nav',
        '.ds-sidebar',
        '.ds-breadcrumb',
        
        // Loading states (shown immediately)
        '.ds-loading',
        '.ds-spinner',
        '.ds-skeleton',
        
        // Error states (might be shown immediately)
        '.ds-error',
        '.ds-alert',
        
        // Accessibility (always needed)
        '.sr-only',
        '.focus-visible',
        '.visually-hidden',
        
        // Polish business essentials
        '.currency-input',
        '.nip-validator',
        '.invoice-status',
      ],
      
      // Patterns for critical selectors
      criticalPatterns: [
        // Responsive utilities for mobile-first
        /^(sm|md):/, // Only include smaller breakpoints as critical
        
        // Essential spacing
        /^(p|m|px|py|mx|my)-(0|1|2|3|4)$/,
        
        // Essential colors
        /^(text|bg)-(primary|error|success)-(600|700|800)$/,
        
        // Essential layout
        /^(flex|grid|block|inline|hidden)$/,
        
        // Essential positioning
        /^(relative|absolute|fixed|sticky)$/,
        
        // Essential display
        /^(block|inline|flex|grid|hidden)$/,
      ],
      
      // Non-critical patterns (defer loading)
      nonCriticalPatterns: [
        // Large breakpoints
        /^(lg|xl|2xl):/,
        
        // Animation classes
        /^animate-/,
        /^transition-/,
        
        // Advanced spacing
        /^(p|m|px|py|mx|my)-(8|10|12|16|20|24|32)$/,
        
        // Decorative colors
        /^(text|bg)-(50|100|200|300|400|500)$/,
        
        // Advanced shadows
        /^shadow-(lg|xl|2xl)$/,
        
        // Complex patterns
        /^pattern-/,
        /^decoration-/,
      ],
      
      // Maximum critical CSS size (in bytes)
      maxCriticalSize: 14 * 1024, // 14KB (recommended for HTTP/1.1)
      
      ...options,
    };
  }

  /**
   * Extract critical CSS from all sources
   */
  async extractCriticalCSS() {
    const results = {
      criticalCSS: '',
      nonCriticalCSS: '',
      criticalSize: 0,
      nonCriticalSize: 0,
      criticalSelectors: new Set(),
      nonCriticalSelectors: new Set(),
      warnings: [],
    };

    // Process each CSS file
    for (const cssFile of this.options.cssFiles) {
      if (fs.existsSync(cssFile)) {
        const fileResult = await this.processCSSFile(cssFile);
        
        results.criticalCSS += fileResult.critical;
        results.nonCriticalCSS += fileResult.nonCritical;
        
        fileResult.criticalSelectors.forEach(sel => results.criticalSelectors.add(sel));
        fileResult.nonCriticalSelectors.forEach(sel => results.nonCriticalSelectors.add(sel));
      } else {
        results.warnings.push(`CSS file not found: ${cssFile}`);
      }
    }

    // Analyze HTML templates for used selectors
    const usedSelectors = await this.analyzeHTMLTemplates();
    
    // Prioritize selectors found in HTML
    const prioritizedResult = this.prioritizeSelectors(results, usedSelectors);
    
    // Check size constraints
    results.criticalSize = Buffer.byteLength(prioritizedResult.criticalCSS, 'utf8');
    results.nonCriticalSize = Buffer.byteLength(prioritizedResult.nonCriticalCSS, 'utf8');
    
    if (results.criticalSize > this.options.maxCriticalSize) {
      results.warnings.push(
        `Critical CSS size (${this.formatBytes(results.criticalSize)}) exceeds recommended limit (${this.formatBytes(this.options.maxCriticalSize)})`
      );
    }

    // Write output files
    await this.writeOutputFiles(prioritizedResult);
    
    return results;
  }

  /**
   * Process a single CSS file
   */
  async processCSSFile(filePath) {
    const css = fs.readFileSync(filePath, 'utf8');
    const ast = postcss.parse(css);
    
    const result = {
      critical: '',
      nonCritical: '',
      criticalSelectors: new Set(),
      nonCriticalSelectors: new Set(),
    };

    ast.walkRules(rule => {
      const selector = rule.selector;
      const isCritical = this.isCriticalSelector(selector);
      
      if (isCritical) {
        result.critical += rule.toString() + '\n';
        result.criticalSelectors.add(selector);
      } else {
        result.nonCritical += rule.toString() + '\n';
        result.nonCriticalSelectors.add(selector);
      }
    });

    // Include critical at-rules (media queries, keyframes, etc.)
    ast.walkAtRules(atRule => {
      if (this.isCriticalAtRule(atRule)) {
        result.critical += atRule.toString() + '\n';
      } else {
        result.nonCritical += atRule.toString() + '\n';
      }
    });

    return result;
  }

  /**
   * Check if a selector is critical
   */
  isCriticalSelector(selector) {
    // Check explicit critical selectors
    if (this.options.criticalSelectors.includes(selector)) {
      return true;
    }

    // Check critical patterns
    for (const pattern of this.options.criticalPatterns) {
      if (pattern.test(selector)) {
        return true;
      }
    }

    // Check non-critical patterns (exclude)
    for (const pattern of this.options.nonCriticalPatterns) {
      if (pattern.test(selector)) {
        return false;
      }
    }

    // Default: consider basic selectors critical
    const basicSelectors = /^[a-zA-Z][a-zA-Z0-9-]*$|^\.[a-zA-Z][a-zA-Z0-9-]*$/;
    return basicSelectors.test(selector);
  }

  /**
   * Check if an at-rule is critical
   */
  isCriticalAtRule(atRule) {
    switch (atRule.name) {
      case 'charset':
      case 'import':
        return true;
      
      case 'media':
        // Only include mobile-first media queries as critical
        const mediaQuery = atRule.params;
        return mediaQuery.includes('max-width: 768px') || 
               mediaQuery.includes('max-width: 640px') ||
               !mediaQuery.includes('min-width');
      
      case 'keyframes':
        // Only include essential animations
        return atRule.params.includes('spin') || 
               atRule.params.includes('pulse') ||
               atRule.params.includes('fade');
      
      case 'font-face':
        // Include font-face declarations as critical
        return true;
      
      default:
        return false;
    }
  }

  /**
   * Analyze HTML templates to find used selectors
   */
  async analyzeHTMLTemplates() {
    const usedSelectors = new Set();
    
    for (const templatePath of this.options.htmlTemplates) {
      if (fs.existsSync(templatePath)) {
        const html = fs.readFileSync(templatePath, 'utf8');
        const selectors = this.extractSelectorsFromHTML(html);
        selectors.forEach(sel => usedSelectors.add(sel));
      }
    }
    
    return usedSelectors;
  }

  /**
   * Extract CSS selectors from HTML content
   */
  extractSelectorsFromHTML(html) {
    const selectors = new Set();
    
    // Extract class names
    const classMatches = html.match(/class\s*=\s*["']([^"']+)["']/g);
    if (classMatches) {
      classMatches.forEach(match => {
        const classes = match.match(/["']([^"']+)["']/)[1].split(/\s+/);
        classes.forEach(className => {
          if (className.trim()) {
            selectors.add(`.${className.trim()}`);
          }
        });
      });
    }
    
    // Extract ID selectors
    const idMatches = html.match(/id\s*=\s*["']([^"']+)["']/g);
    if (idMatches) {
      idMatches.forEach(match => {
        const id = match.match(/["']([^"']+)["']/)[1];
        selectors.add(`#${id}`);
      });
    }
    
    // Extract element selectors (basic ones)
    const elementMatches = html.match(/<(\w+)/g);
    if (elementMatches) {
      elementMatches.forEach(match => {
        const element = match.substring(1);
        if (['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'button', 'input', 'form'].includes(element)) {
          selectors.add(element);
        }
      });
    }
    
    return selectors;
  }

  /**
   * Prioritize selectors based on HTML usage
   */
  prioritizeSelectors(results, usedSelectors) {
    let criticalCSS = '';
    let nonCriticalCSS = '';
    
    // Split CSS into rules and prioritize based on usage
    const criticalRules = results.criticalCSS.split('\n').filter(rule => rule.trim());
    const nonCriticalRules = results.nonCriticalCSS.split('\n').filter(rule => rule.trim());
    
    // Prioritize critical rules that are actually used
    const usedCriticalRules = [];
    const unusedCriticalRules = [];
    
    criticalRules.forEach(rule => {
      const hasUsedSelector = Array.from(usedSelectors).some(selector => 
        rule.includes(selector.replace('.', '\\.').replace('#', '\\#'))
      );
      
      if (hasUsedSelector) {
        usedCriticalRules.push(rule);
      } else {
        unusedCriticalRules.push(rule);
      }
    });
    
    // Build final critical CSS (used rules first)
    criticalCSS = usedCriticalRules.join('\n') + '\n' + unusedCriticalRules.join('\n');
    nonCriticalCSS = nonCriticalRules.join('\n');
    
    // If critical CSS is too large, move some rules to non-critical
    let criticalSize = Buffer.byteLength(criticalCSS, 'utf8');
    
    if (criticalSize > this.options.maxCriticalSize) {
      const rules = criticalCSS.split('\n').filter(rule => rule.trim());
      const keptRules = [];
      let currentSize = 0;
      
      for (const rule of rules) {
        const ruleSize = Buffer.byteLength(rule + '\n', 'utf8');
        
        if (currentSize + ruleSize <= this.options.maxCriticalSize) {
          keptRules.push(rule);
          currentSize += ruleSize;
        } else {
          nonCriticalCSS = rule + '\n' + nonCriticalCSS;
        }
      }
      
      criticalCSS = keptRules.join('\n');
    }
    
    return {
      criticalCSS,
      nonCriticalCSS,
    };
  }

  /**
   * Write output files
   */
  async writeOutputFiles(result) {
    // Ensure output directory exists
    if (!fs.existsSync(this.options.outputDir)) {
      fs.mkdirSync(this.options.outputDir, { recursive: true });
    }
    
    // Write critical CSS
    const criticalPath = path.join(this.options.outputDir, this.options.criticalCSSFile);
    fs.writeFileSync(criticalPath, result.criticalCSS);
    
    // Write non-critical CSS
    const nonCriticalPath = path.join(this.options.outputDir, this.options.nonCriticalCSSFile);
    fs.writeFileSync(nonCriticalPath, result.nonCriticalCSS);
    
    console.log(`Critical CSS written to: ${criticalPath}`);
    console.log(`Non-critical CSS written to: ${nonCriticalPath}`);
  }

  /**
   * Generate inline critical CSS for HTML
   */
  generateInlineCriticalCSS(criticalCSS) {
    // Minify critical CSS for inlining
    const minified = criticalCSS
      .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comments
      .replace(/\s+/g, ' ') // Collapse whitespace
      .replace(/;\s*}/g, '}') // Remove unnecessary semicolons
      .replace(/\s*{\s*/g, '{') // Clean up braces
      .replace(/\s*}\s*/g, '}')
      .replace(/\s*,\s*/g, ',') // Clean up commas
      .replace(/\s*:\s*/g, ':') // Clean up colons
      .replace(/\s*;\s*/g, ';') // Clean up semicolons
      .trim();
    
    return `<style>${minified}</style>`;
  }

  /**
   * Generate preload link for non-critical CSS
   */
  generatePreloadLink(nonCriticalCSSPath) {
    return `<link rel="preload" href="${nonCriticalCSSPath}" as="style" onload="this.onload=null;this.rel='stylesheet'">`;
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
  const extractor = new CriticalCSSExtractor();
  
  extractor.extractCriticalCSS()
    .then(results => {
      console.log('\nCritical CSS Extraction Complete!');
      console.log(`Critical CSS size: ${extractor.formatBytes(results.criticalSize)}`);
      console.log(`Non-critical CSS size: ${extractor.formatBytes(results.nonCriticalSize)}`);
      console.log(`Critical selectors: ${results.criticalSelectors.size}`);
      console.log(`Non-critical selectors: ${results.nonCriticalSelectors.size}`);
      
      if (results.warnings.length > 0) {
        console.log('\nWarnings:');
        results.warnings.forEach(warning => console.log(`  - ${warning}`));
      }
    })
    .catch(error => {
      console.error('Error extracting critical CSS:', error);
      process.exit(1);
    });
}

module.exports = CriticalCSSExtractor;