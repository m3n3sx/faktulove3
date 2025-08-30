/**
 * CSS Optimization Pipeline
 * 
 * Comprehensive CSS optimization pipeline that combines tree-shaking,
 * critical CSS extraction, and asset optimization.
 */

const fs = require('fs');
const path = require('path');
const CSSTreeShaker = require('./css-tree-shaking');
const CriticalCSSExtractor = require('./critical-css-extractor');
const AssetOptimizer = require('./asset-optimizer');
const buildConfig = require('../build-config');

class CSSOptimizationPipeline {
  constructor(options = {}) {
    this.options = {
      // Input directories
      srcDir: './src',
      buildDir: './build',
      
      // Output directories
      outputDir: './build/static',
      reportsDir: './performance-reports',
      
      // Optimization stages
      stages: {
        treeShaking: true,
        criticalCSS: true,
        assetOptimization: true,
        performanceAnalysis: true,
      },
      
      // Build configuration
      buildConfig: buildConfig.cssOptimization,
      
      ...options,
    };
    
    this.results = {
      treeShaking: null,
      criticalCSS: null,
      assetOptimization: null,
      performanceAnalysis: null,
      totalSizeBefore: 0,
      totalSizeAfter: 0,
      totalSavings: 0,
      timestamp: Date.now(),
    };
  }

  /**
   * Run the complete CSS optimization pipeline
   */
  async runPipeline() {
    console.log('🚀 Starting CSS Optimization Pipeline...\n');
    
    try {
      // Stage 1: CSS Tree Shaking
      if (this.options.stages.treeShaking) {
        console.log('📦 Stage 1: CSS Tree Shaking');
        this.results.treeShaking = await this.runTreeShaking();
        console.log(`✅ Tree shaking complete - Saved ${this.formatBytes(this.results.treeShaking.savings)}\n`);
      }
      
      // Stage 2: Critical CSS Extraction
      if (this.options.stages.criticalCSS) {
        console.log('⚡ Stage 2: Critical CSS Extraction');
        this.results.criticalCSS = await this.runCriticalCSSExtraction();
        console.log(`✅ Critical CSS extracted - ${this.formatBytes(this.results.criticalCSS.criticalSize)} critical, ${this.formatBytes(this.results.criticalCSS.nonCriticalSize)} non-critical\n`);
      }
      
      // Stage 3: Asset Optimization
      if (this.options.stages.assetOptimization) {
        console.log('🎨 Stage 3: Asset Optimization');
        this.results.assetOptimization = await this.runAssetOptimization();
        console.log(`✅ Assets optimized - ${this.results.assetOptimization.fonts.processed.length} fonts, ${this.results.assetOptimization.icons.processed.length} icons\n`);
      }
      
      // Stage 4: Performance Analysis
      if (this.options.stages.performanceAnalysis) {
        console.log('📊 Stage 4: Performance Analysis');
        this.results.performanceAnalysis = await this.runPerformanceAnalysis();
        console.log(`✅ Performance analysis complete\n`);
      }
      
      // Generate comprehensive report
      const report = await this.generateComprehensiveReport();
      
      console.log('🎉 CSS Optimization Pipeline Complete!');
      console.log(`📈 Total savings: ${this.formatBytes(this.results.totalSavings)} (${this.results.savingsPercentage}%)`);
      console.log(`📋 Report generated: ${report.reportPath}`);
      
      return this.results;
      
    } catch (error) {
      console.error('❌ Pipeline failed:', error);
      throw error;
    }
  }

  /**
   * Run CSS tree shaking
   */
  async runTreeShaking() {
    const treeShaker = new CSSTreeShaker({
      ...this.options.buildConfig.purgeCSS,
      outputDir: path.join(this.options.outputDir, 'css'),
    });
    
    const results = await treeShaker.processCSSFiles();
    this.results.totalSizeBefore += results.totalSizeBefore;
    this.results.totalSizeAfter += results.totalSizeAfter;
    
    return results;
  }

  /**
   * Run critical CSS extraction
   */
  async runCriticalCSSExtraction() {
    const extractor = new CriticalCSSExtractor({
      ...this.options.buildConfig.criticalCSS,
      outputDir: path.join(this.options.outputDir, 'css'),
    });
    
    const results = await extractor.extractCriticalCSS();
    
    return results;
  }

  /**
   * Run asset optimization
   */
  async runAssetOptimization() {
    const optimizer = new AssetOptimizer({
      ...this.options.buildConfig.assets,
      outputDir: this.options.outputDir,
    });
    
    const results = await optimizer.optimizeAssets();
    
    return results;
  }

  /**
   * Run performance analysis
   */
  async runPerformanceAnalysis() {
    const analysis = {
      bundleSize: await this.analyzeBundleSize(),
      loadingPerformance: await this.analyzeLoadingPerformance(),
      cacheEfficiency: await this.analyzeCacheEfficiency(),
      recommendations: [],
    };
    
    // Generate recommendations based on analysis
    analysis.recommendations = this.generateRecommendations(analysis);
    
    return analysis;
  }

  /**
   * Analyze bundle size
   */
  async analyzeBundleSize() {
    const cssFiles = await this.findCSSFiles(path.join(this.options.buildDir, 'static/css'));
    
    let totalSize = 0;
    let gzippedSize = 0;
    const files = [];
    
    for (const file of cssFiles) {
      const stats = fs.statSync(file);
      const size = stats.size;
      
      // Estimate gzipped size (rough approximation)
      const estimatedGzipSize = Math.round(size * 0.3);
      
      totalSize += size;
      gzippedSize += estimatedGzipSize;
      
      files.push({
        name: path.basename(file),
        size: size,
        gzippedSize: estimatedGzipSize,
        type: this.categorizeFile(file),
      });
    }
    
    return {
      totalSize,
      gzippedSize,
      files,
      exceedsThreshold: totalSize > this.options.buildConfig.maxBundleSize?.css || 0,
    };
  }

  /**
   * Analyze loading performance
   */
  async analyzeLoadingPerformance() {
    const criticalCSSPath = path.join(this.options.outputDir, 'css', 'critical.css');
    const nonCriticalCSSPath = path.join(this.options.outputDir, 'css', 'non-critical.css');
    
    const analysis = {
      criticalCSSSize: 0,
      nonCriticalCSSSize: 0,
      estimatedLoadTime: 0,
      renderBlockingResources: [],
    };
    
    if (fs.existsSync(criticalCSSPath)) {
      analysis.criticalCSSSize = fs.statSync(criticalCSSPath).size;
    }
    
    if (fs.existsSync(nonCriticalCSSPath)) {
      analysis.nonCriticalCSSSize = fs.statSync(nonCriticalCSSPath).size;
    }
    
    // Estimate load time based on size (rough approximation)
    // Assumes 3G connection (~1.6 Mbps)
    const connectionSpeed = 1.6 * 1024 * 1024 / 8; // bytes per second
    analysis.estimatedLoadTime = (analysis.criticalCSSSize / connectionSpeed) * 1000; // milliseconds
    
    return analysis;
  }

  /**
   * Analyze cache efficiency
   */
  async analyzeCacheEfficiency() {
    const analysis = {
      staticAssets: 0,
      dynamicAssets: 0,
      cacheableAssets: 0,
      recommendations: [],
    };
    
    // This would analyze cache headers and asset naming patterns
    // For now, it's a placeholder
    
    return analysis;
  }

  /**
   * Generate optimization recommendations
   */
  generateRecommendations(analysis) {
    const recommendations = [];
    
    // Bundle size recommendations
    if (analysis.bundleSize.exceedsThreshold) {
      recommendations.push({
        type: 'warning',
        category: 'bundle-size',
        title: 'CSS Bundle Size Exceeds Threshold',
        description: `Total CSS size (${this.formatBytes(analysis.bundleSize.totalSize)}) exceeds recommended threshold`,
        impact: 'high',
        effort: 'medium',
        suggestions: [
          'Enable more aggressive tree-shaking',
          'Split CSS into smaller chunks',
          'Remove unused CSS frameworks',
          'Optimize CSS custom properties',
        ],
      });
    }
    
    // Critical CSS recommendations
    if (analysis.loadingPerformance.criticalCSSSize > 14 * 1024) {
      recommendations.push({
        type: 'warning',
        category: 'critical-css',
        title: 'Critical CSS Size Too Large',
        description: `Critical CSS (${this.formatBytes(analysis.loadingPerformance.criticalCSSSize)}) exceeds 14KB recommendation`,
        impact: 'medium',
        effort: 'low',
        suggestions: [
          'Reduce critical CSS selectors',
          'Move non-essential styles to non-critical CSS',
          'Optimize critical CSS patterns',
        ],
      });
    }
    
    // Loading performance recommendations
    if (analysis.loadingPerformance.estimatedLoadTime > 1000) {
      recommendations.push({
        type: 'info',
        category: 'performance',
        title: 'CSS Load Time Could Be Improved',
        description: `Estimated CSS load time: ${Math.round(analysis.loadingPerformance.estimatedLoadTime)}ms`,
        impact: 'medium',
        effort: 'medium',
        suggestions: [
          'Implement CSS preloading',
          'Use HTTP/2 server push for critical CSS',
          'Optimize CSS delivery strategy',
        ],
      });
    }
    
    return recommendations;
  }

  /**
   * Generate comprehensive report
   */
  async generateComprehensiveReport() {
    // Calculate total savings
    this.results.totalSavings = this.results.totalSizeBefore - this.results.totalSizeAfter;
    this.results.savingsPercentage = this.results.totalSizeBefore > 0 
      ? ((this.results.totalSavings / this.results.totalSizeBefore) * 100).toFixed(1)
      : '0';
    
    const report = {
      timestamp: this.results.timestamp,
      pipeline: {
        stages: this.options.stages,
        duration: Date.now() - this.results.timestamp,
      },
      summary: {
        totalSizeBefore: this.formatBytes(this.results.totalSizeBefore),
        totalSizeAfter: this.formatBytes(this.results.totalSizeAfter),
        totalSavings: this.formatBytes(this.results.totalSavings),
        savingsPercentage: this.results.savingsPercentage,
      },
      stages: {
        treeShaking: this.results.treeShaking,
        criticalCSS: this.results.criticalCSS,
        assetOptimization: this.results.assetOptimization,
        performanceAnalysis: this.results.performanceAnalysis,
      },
      recommendations: this.results.performanceAnalysis?.recommendations || [],
    };
    
    // Ensure reports directory exists
    if (!fs.existsSync(this.options.reportsDir)) {
      fs.mkdirSync(this.options.reportsDir, { recursive: true });
    }
    
    // Write JSON report
    const reportPath = path.join(this.options.reportsDir, `css-optimization-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    // Write HTML report
    const htmlReportPath = path.join(this.options.reportsDir, `css-optimization-${Date.now()}.html`);
    fs.writeFileSync(htmlReportPath, this.generateHTMLReport(report));
    
    return {
      report,
      reportPath,
      htmlReportPath,
    };
  }

  /**
   * Generate HTML report
   */
  generateHTMLReport(report) {
    return `
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS Optimization Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .metric-label { font-size: 14px; color: #666; margin-top: 5px; }
        .stage { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 6px; }
        .stage-success { border-color: #28a745; background: #f8fff9; }
        .stage-warning { border-color: #ffc107; background: #fffdf5; }
        .recommendations { margin: 20px 0; }
        .recommendation { margin: 10px 0; padding: 15px; border-radius: 6px; }
        .recommendation.warning { background: #fff3cd; border-left: 4px solid #ffc107; }
        .recommendation.info { background: #d1ecf1; border-left: 4px solid #17a2b8; }
        .impact-high { color: #dc3545; font-weight: bold; }
        .impact-medium { color: #fd7e14; font-weight: bold; }
        .impact-low { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CSS Optimization Report</h1>
        <p>Generated: ${new Date(report.timestamp).toLocaleString('pl-PL')}</p>
        <p>Duration: ${Math.round(report.pipeline.duration / 1000)}s</p>
        
        <h2>Summary</h2>
        <div class="summary">
            <div class="metric">
                <div class="metric-value">${report.summary.totalSizeBefore}</div>
                <div class="metric-label">Size Before</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.totalSizeAfter}</div>
                <div class="metric-label">Size After</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.totalSavings}</div>
                <div class="metric-label">Total Savings</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.savingsPercentage}%</div>
                <div class="metric-label">Savings Percentage</div>
            </div>
        </div>

        <h2>Optimization Stages</h2>
        
        ${report.stages.treeShaking ? `
        <div class="stage stage-success">
            <h3>✅ CSS Tree Shaking</h3>
            <p>Files processed: ${report.stages.treeShaking.processed.length}</p>
            <p>Savings: ${this.formatBytes(report.stages.treeShaking.savings)} (${report.stages.treeShaking.savingsPercentage}%)</p>
        </div>
        ` : ''}
        
        ${report.stages.criticalCSS ? `
        <div class="stage stage-success">
            <h3>⚡ Critical CSS Extraction</h3>
            <p>Critical CSS: ${this.formatBytes(report.stages.criticalCSS.criticalSize)}</p>
            <p>Non-critical CSS: ${this.formatBytes(report.stages.criticalCSS.nonCriticalSize)}</p>
            <p>Warnings: ${report.stages.criticalCSS.warnings.length}</p>
        </div>
        ` : ''}
        
        ${report.stages.assetOptimization ? `
        <div class="stage stage-success">
            <h3>🎨 Asset Optimization</h3>
            <p>Fonts optimized: ${report.stages.assetOptimization.fonts.processed.length}</p>
            <p>Icons optimized: ${report.stages.assetOptimization.icons.processed.length}</p>
        </div>
        ` : ''}

        <h2>Recommendations</h2>
        <div class="recommendations">
            ${report.recommendations.map(rec => `
                <div class="recommendation ${rec.type}">
                    <h3>${rec.title} <span class="impact-${rec.impact}">[${rec.impact.toUpperCase()} IMPACT]</span></h3>
                    <p>${rec.description}</p>
                    <p><strong>Effort:</strong> ${rec.effort}</p>
                    <ul>
                        ${rec.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                </div>
            `).join('')}
        </div>
    </div>
</body>
</html>`;
  }

  /**
   * Find CSS files in directory
   */
  async findCSSFiles(dir) {
    const files = [];
    
    if (!fs.existsSync(dir)) return files;
    
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        const subFiles = await this.findCSSFiles(fullPath);
        files.push(...subFiles);
      } else if (item.endsWith('.css')) {
        files.push(fullPath);
      }
    }
    
    return files;
  }

  /**
   * Categorize file by name
   */
  categorizeFile(filePath) {
    const fileName = path.basename(filePath);
    
    if (fileName.includes('critical')) return 'critical';
    if (fileName.includes('vendor')) return 'vendor';
    if (fileName.includes('design-system')) return 'design-system';
    if (fileName.includes('main')) return 'main';
    
    return 'other';
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
  const pipeline = new CSSOptimizationPipeline();
  
  pipeline.runPipeline()
    .then(results => {
      process.exit(0);
    })
    .catch(error => {
      console.error('Pipeline failed:', error);
      process.exit(1);
    });
}

module.exports = CSSOptimizationPipeline;