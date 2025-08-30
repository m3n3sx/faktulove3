#!/usr/bin/env node

/**
 * Bundle Analysis Script
 * 
 * Analyzes the webpack bundle to identify optimization opportunities
 * and track design system impact on bundle size.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const gzipSize = require('gzip-size');

class BundleAnalyzer {
  constructor() {
    this.buildDir = path.join(process.cwd(), 'build');
    this.reportDir = path.join(process.cwd(), 'bundle-reports');
    this.previousReport = null;
    
    // Ensure report directory exists
    if (!fs.existsSync(this.reportDir)) {
      fs.mkdirSync(this.reportDir, { recursive: true });
    }
  }

  /**
   * Run complete bundle analysis
   */
  async analyze() {
    console.log('📊 Starting bundle analysis...\n');

    try {
      // Build the project with analysis
      console.log('🔨 Building project for analysis...');
      execSync('ANALYZE=true npm run build', { 
        stdio: 'inherit',
        env: { ...process.env, GENERATE_SOURCEMAP: 'true' }
      });

      // Load previous report for comparison
      this.loadPreviousReport();

      // Analyze bundle files
      const analysis = await this.analyzeBundleFiles();

      // Generate report
      const report = this.generateReport(analysis);

      // Save report
      this.saveReport(report);

      // Display summary
      this.displaySummary(report);

      console.log('\n🎉 Bundle analysis completed!');
      console.log(`📄 Detailed report saved to: ${path.join(this.reportDir, 'latest-report.json')}`);
      console.log(`📈 HTML report available at: ${path.join(this.buildDir, 'bundle-report.html')}`);

    } catch (error) {
      console.error('❌ Bundle analysis failed:', error.message);
      process.exit(1);
    }
  }

  /**
   * Analyze bundle files in build directory
   */
  async analyzeBundleFiles() {
    const staticDir = path.join(this.buildDir, 'static');
    const jsDir = path.join(staticDir, 'js');
    const cssDir = path.join(staticDir, 'css');

    const analysis = {
      timestamp: new Date().toISOString(),
      javascript: {
        files: [],
        totalSize: 0,
        totalGzipSize: 0,
      },
      css: {
        files: [],
        totalSize: 0,
        totalGzipSize: 0,
      },
      designSystem: {
        estimatedSize: 0,
        estimatedGzipSize: 0,
        components: [],
      },
      chunks: {},
    };

    // Analyze JavaScript files
    if (fs.existsSync(jsDir)) {
      const jsFiles = fs.readdirSync(jsDir).filter(file => file.endsWith('.js'));
      
      for (const file of jsFiles) {
        const filePath = path.join(jsDir, file);
        const content = fs.readFileSync(filePath);
        const size = content.length;
        const gzipSizeValue = await gzipSize(content);

        const fileAnalysis = {
          name: file,
          size,
          gzipSize: gzipSizeValue,
          isChunk: file.includes('.chunk.'),
          isMain: file.includes('main.'),
          isVendor: file.includes('vendor') || file.includes('node_modules'),
          designSystemContent: this.analyzeDesignSystemContent(content.toString()),
        };

        analysis.javascript.files.push(fileAnalysis);
        analysis.javascript.totalSize += size;
        analysis.javascript.totalGzipSize += gzipSizeValue;

        // Track design system usage
        if (fileAnalysis.designSystemContent.hasDesignSystem) {
          analysis.designSystem.estimatedSize += fileAnalysis.designSystemContent.estimatedSize;
          analysis.designSystem.estimatedGzipSize += Math.round(gzipSizeValue * fileAnalysis.designSystemContent.ratio);
          analysis.designSystem.components.push(...fileAnalysis.designSystemContent.components);
        }

        // Categorize chunks
        if (file.includes('design-system')) {
          analysis.chunks.designSystem = fileAnalysis;
        } else if (file.includes('design-tokens')) {
          analysis.chunks.designTokens = fileAnalysis;
        } else if (file.includes('vendor')) {
          analysis.chunks.vendor = fileAnalysis;
        } else if (file.includes('main')) {
          analysis.chunks.main = fileAnalysis;
        }
      }
    }

    // Analyze CSS files
    if (fs.existsSync(cssDir)) {
      const cssFiles = fs.readdirSync(cssDir).filter(file => file.endsWith('.css'));
      
      for (const file of cssFiles) {
        const filePath = path.join(cssDir, file);
        const content = fs.readFileSync(filePath);
        const size = content.length;
        const gzipSizeValue = await gzipSize(content);

        const fileAnalysis = {
          name: file,
          size,
          gzipSize: gzipSizeValue,
          tailwindClasses: this.countTailwindClasses(content.toString()),
          customProperties: this.countCustomProperties(content.toString()),
        };

        analysis.css.files.push(fileAnalysis);
        analysis.css.totalSize += size;
        analysis.css.totalGzipSize += gzipSizeValue;
      }
    }

    return analysis;
  }

  /**
   * Analyze design system content in JavaScript files
   */
  analyzeDesignSystemContent(content) {
    const designSystemImports = content.match(/from ['"]@\/design-system['"]/g) || [];
    const designSystemComponents = content.match(/import\s+\{([^}]+)\}\s+from\s+['"]@\/design-system['"]/g) || [];
    
    const components = [];
    designSystemComponents.forEach(importStatement => {
      const matches = importStatement.match(/\{([^}]+)\}/);
      if (matches) {
        const componentNames = matches[1].split(',').map(name => name.trim());
        components.push(...componentNames);
      }
    });

    const hasDesignSystem = designSystemImports.length > 0;
    const estimatedSize = hasDesignSystem ? content.length * 0.1 : 0; // Rough estimate
    const ratio = hasDesignSystem ? 0.1 : 0;

    return {
      hasDesignSystem,
      estimatedSize,
      ratio,
      components: [...new Set(components)], // Remove duplicates
      importCount: designSystemImports.length,
    };
  }

  /**
   * Count Tailwind CSS classes in CSS content
   */
  countTailwindClasses(content) {
    const tailwindPatterns = [
      /\.(text|bg|border|ring)-(primary|secondary|success|warning|error)-\d+/g,
      /\.(p|m|px|py|mx|my|pt|pb|pl|pr|mt|mb|ml|mr)-\d+/g,
      /\.(w|h|min-w|min-h|max-w|max-h)-\d+/g,
      /\.text-(xs|sm|base|lg|xl|2xl|3xl|4xl)/g,
      /\.font-(thin|extralight|light|normal|medium|semibold|bold|extrabold|black)/g,
      /\.rounded-(none|xs|sm|md|lg|xl|2xl|3xl|full)/g,
      /\.shadow-(none|xs|sm|md|lg|xl|2xl|inner)/g,
    ];

    let totalClasses = 0;
    tailwindPatterns.forEach(pattern => {
      const matches = content.match(pattern) || [];
      totalClasses += matches.length;
    });

    return totalClasses;
  }

  /**
   * Count CSS custom properties
   */
  countCustomProperties(content) {
    const customPropertyPattern = /--[\w-]+:/g;
    const matches = content.match(customPropertyPattern) || [];
    return matches.length;
  }

  /**
   * Load previous report for comparison
   */
  loadPreviousReport() {
    const previousReportPath = path.join(this.reportDir, 'latest-report.json');
    if (fs.existsSync(previousReportPath)) {
      try {
        this.previousReport = JSON.parse(fs.readFileSync(previousReportPath, 'utf8'));
      } catch (error) {
        console.warn('⚠️  Could not load previous report for comparison');
      }
    }
  }

  /**
   * Generate comprehensive report
   */
  generateReport(analysis) {
    const report = {
      ...analysis,
      summary: {
        totalBundleSize: analysis.javascript.totalSize + analysis.css.totalSize,
        totalGzipSize: analysis.javascript.totalGzipSize + analysis.css.totalGzipSize,
        designSystemImpact: {
          size: analysis.designSystem.estimatedSize,
          gzipSize: analysis.designSystem.estimatedGzipSize,
          percentage: Math.round((analysis.designSystem.estimatedSize / analysis.javascript.totalSize) * 100),
        },
        chunkAnalysis: this.analyzeChunks(analysis.chunks),
        recommendations: this.generateRecommendations(analysis),
      },
      comparison: this.previousReport ? this.compareWithPrevious(analysis, this.previousReport) : null,
    };

    return report;
  }

  /**
   * Analyze chunk distribution
   */
  analyzeChunks(chunks) {
    const chunkAnalysis = {
      total: Object.keys(chunks).length,
      largest: null,
      smallest: null,
      designSystemChunks: [],
    };

    const chunkSizes = Object.entries(chunks).map(([name, chunk]) => ({
      name,
      size: chunk.size,
      gzipSize: chunk.gzipSize,
    }));

    if (chunkSizes.length > 0) {
      chunkSizes.sort((a, b) => b.size - a.size);
      chunkAnalysis.largest = chunkSizes[0];
      chunkAnalysis.smallest = chunkSizes[chunkSizes.length - 1];
    }

    // Identify design system chunks
    Object.entries(chunks).forEach(([name, chunk]) => {
      if (name.includes('design') || chunk.designSystemContent?.hasDesignSystem) {
        chunkAnalysis.designSystemChunks.push({ name, ...chunk });
      }
    });

    return chunkAnalysis;
  }

  /**
   * Generate optimization recommendations
   */
  generateRecommendations(analysis) {
    const recommendations = [];

    // Bundle size recommendations
    if (analysis.javascript.totalSize > 1024 * 1024) { // > 1MB
      recommendations.push({
        type: 'size',
        priority: 'high',
        message: 'JavaScript bundle is larger than 1MB. Consider code splitting and lazy loading.',
      });
    }

    // Design system recommendations
    if (analysis.designSystem.estimatedSize > 200 * 1024) { // > 200KB
      recommendations.push({
        type: 'design-system',
        priority: 'medium',
        message: 'Design system bundle is large. Ensure tree-shaking is working correctly.',
      });
    }

    // CSS recommendations
    if (analysis.css.totalSize > 100 * 1024) { // > 100KB
      recommendations.push({
        type: 'css',
        priority: 'medium',
        message: 'CSS bundle is large. Verify PurgeCSS is removing unused styles.',
      });
    }

    // Chunk recommendations
    const mainChunk = analysis.chunks.main;
    if (mainChunk && mainChunk.size > 500 * 1024) { // > 500KB
      recommendations.push({
        type: 'chunks',
        priority: 'high',
        message: 'Main chunk is large. Consider moving more code to vendor or feature chunks.',
      });
    }

    // Gzip recommendations
    const gzipRatio = analysis.javascript.totalGzipSize / analysis.javascript.totalSize;
    if (gzipRatio > 0.7) {
      recommendations.push({
        type: 'compression',
        priority: 'low',
        message: 'Gzip compression ratio is low. Code may not be minified properly.',
      });
    }

    return recommendations;
  }

  /**
   * Compare with previous report
   */
  compareWithPrevious(current, previous) {
    const comparison = {
      bundleSize: {
        current: current.javascript.totalSize + current.css.totalSize,
        previous: previous.javascript.totalSize + previous.css.totalSize,
        change: 0,
        changePercent: 0,
      },
      gzipSize: {
        current: current.javascript.totalGzipSize + current.css.totalGzipSize,
        previous: previous.javascript.totalGzipSize + previous.css.totalGzipSize,
        change: 0,
        changePercent: 0,
      },
      designSystem: {
        current: current.designSystem.estimatedSize,
        previous: previous.designSystem.estimatedSize,
        change: 0,
        changePercent: 0,
      },
    };

    // Calculate changes
    Object.keys(comparison).forEach(key => {
      const curr = comparison[key].current;
      const prev = comparison[key].previous;
      comparison[key].change = curr - prev;
      comparison[key].changePercent = prev > 0 ? Math.round(((curr - prev) / prev) * 100) : 0;
    });

    return comparison;
  }

  /**
   * Save report to file
   */
  saveReport(report) {
    const reportPath = path.join(this.reportDir, 'latest-report.json');
    const timestampedPath = path.join(this.reportDir, `report-${Date.now()}.json`);

    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    fs.writeFileSync(timestampedPath, JSON.stringify(report, null, 2));
  }

  /**
   * Display summary in console
   */
  displaySummary(report) {
    const { summary, comparison } = report;

    console.log('\n📊 Bundle Analysis Summary');
    console.log('==========================');
    console.log(`Total Bundle Size: ${this.formatBytes(summary.totalBundleSize)}`);
    console.log(`Total Gzip Size: ${this.formatBytes(summary.totalGzipSize)}`);
    console.log(`Design System Impact: ${this.formatBytes(summary.designSystemImpact.size)} (${summary.designSystemImpact.percentage}%)`);

    if (comparison) {
      console.log('\n📈 Changes from Previous Build');
      console.log('==============================');
      console.log(`Bundle Size: ${this.formatChange(comparison.bundleSize.change, comparison.bundleSize.changePercent)}`);
      console.log(`Gzip Size: ${this.formatChange(comparison.gzipSize.change, comparison.gzipSize.changePercent)}`);
      console.log(`Design System: ${this.formatChange(comparison.designSystem.change, comparison.designSystem.changePercent)}`);
    }

    console.log('\n🔍 Chunk Analysis');
    console.log('==================');
    console.log(`Total Chunks: ${summary.chunkAnalysis.total}`);
    if (summary.chunkAnalysis.largest) {
      console.log(`Largest Chunk: ${summary.chunkAnalysis.largest.name} (${this.formatBytes(summary.chunkAnalysis.largest.size)})`);
    }
    console.log(`Design System Chunks: ${summary.chunkAnalysis.designSystemChunks.length}`);

    if (summary.recommendations.length > 0) {
      console.log('\n💡 Recommendations');
      console.log('==================');
      summary.recommendations.forEach(rec => {
        const priority = rec.priority === 'high' ? '🔴' : rec.priority === 'medium' ? '🟡' : '🟢';
        console.log(`${priority} ${rec.message}`);
      });
    }
  }

  /**
   * Format bytes to human readable string
   */
  formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Format change with color coding
   */
  formatChange(change, changePercent) {
    const sign = change >= 0 ? '+' : '';
    const color = change > 0 ? '🔴' : change < 0 ? '🟢' : '⚪';
    return `${color} ${sign}${this.formatBytes(change)} (${sign}${changePercent}%)`;
  }
}

// CLI interface
if (require.main === module) {
  const analyzer = new BundleAnalyzer();
  analyzer.analyze().catch(error => {
    console.error('Bundle analysis failed:', error);
    process.exit(1);
  });
}

module.exports = BundleAnalyzer;