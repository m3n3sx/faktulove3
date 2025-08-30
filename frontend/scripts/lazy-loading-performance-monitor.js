/**
 * Lazy Loading Performance Monitor
 * 
 * Monitors and reports performance metrics for lazy-loaded components
 */

const fs = require('fs');
const path = require('path');
const gzipSize = require('gzip-size');

class LazyLoadingPerformanceMonitor {
  constructor(options = {}) {
    this.options = {
      outputPath: path.join(process.cwd(), 'performance-reports'),
      thresholds: {
        chunkSize: 100 * 1024, // 100KB
        gzipSize: 30 * 1024, // 30KB
        loadTime: 500, // 500ms
      },
      ...options,
    };
    
    this.metrics = {
      chunks: new Map(),
      loadTimes: new Map(),
      errors: [],
      timestamp: Date.now(),
    };
  }

  /**
   * Analyze webpack build output for lazy loading performance
   */
  async analyzeBuildOutput(buildPath) {
    const statsPath = path.join(buildPath, 'asset-manifest.json');
    
    if (!fs.existsSync(statsPath)) {
      throw new Error('Asset manifest not found. Run build first.');
    }

    const manifest = JSON.parse(fs.readFileSync(statsPath, 'utf8'));
    
    // Analyze chunks
    for (const [key, filePath] of Object.entries(manifest.files || {})) {
      if (key.includes('chunk') && filePath.endsWith('.js')) {
        await this.analyzeChunk(key, path.join(buildPath, filePath));
      }
    }

    // Generate report
    return this.generateReport();
  }

  /**
   * Analyze individual chunk
   */
  async analyzeChunk(chunkName, filePath) {
    if (!fs.existsSync(filePath)) {
      this.metrics.errors.push(`Chunk file not found: ${filePath}`);
      return;
    }

    const stats = fs.statSync(filePath);
    const content = fs.readFileSync(filePath);
    const gzipped = await gzipSize(content);

    const chunkMetrics = {
      name: chunkName,
      size: stats.size,
      gzipSize: gzipped,
      compressionRatio: (1 - gzipped / stats.size) * 100,
      isLazyChunk: this.isLazyChunk(chunkName),
      category: this.categorizeChunk(chunkName),
      exceedsThreshold: {
        size: stats.size > this.options.thresholds.chunkSize,
        gzip: gzipped > this.options.thresholds.gzipSize,
      },
    };

    this.metrics.chunks.set(chunkName, chunkMetrics);
  }

  /**
   * Check if chunk is lazy-loaded
   */
  isLazyChunk(chunkName) {
    const lazyPatterns = [
      'lazy',
      'async',
      'polish-business',
      'accessibility',
      'patterns',
      'charts',
      'forms',
    ];

    return lazyPatterns.some(pattern => 
      chunkName.toLowerCase().includes(pattern)
    );
  }

  /**
   * Categorize chunk by type
   */
  categorizeChunk(chunkName) {
    const categories = {
      core: ['main', 'runtime', 'vendor'],
      primitives: ['button', 'input', 'typography'],
      layouts: ['grid', 'flex', 'container', 'stack'],
      business: ['polish-business', 'currency', 'nip', 'vat'],
      patterns: ['chart', 'table', 'form', 'card'],
      accessibility: ['accessibility', 'a11y', 'aria', 'keyboard'],
    };

    for (const [category, patterns] of Object.entries(categories)) {
      if (patterns.some(pattern => 
        chunkName.toLowerCase().includes(pattern)
      )) {
        return category;
      }
    }

    return 'other';
  }

  /**
   * Generate performance report
   */
  generateReport() {
    const chunks = Array.from(this.metrics.chunks.values());
    
    const report = {
      timestamp: this.metrics.timestamp,
      summary: this.generateSummary(chunks),
      chunks: chunks,
      recommendations: this.generateRecommendations(chunks),
      errors: this.metrics.errors,
    };

    // Ensure output directory exists
    if (!fs.existsSync(this.options.outputPath)) {
      fs.mkdirSync(this.options.outputPath, { recursive: true });
    }

    // Write JSON report
    const reportPath = path.join(
      this.options.outputPath,
      `lazy-loading-report-${Date.now()}.json`
    );
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    // Write HTML report
    const htmlReportPath = path.join(
      this.options.outputPath,
      `lazy-loading-report-${Date.now()}.html`
    );
    fs.writeFileSync(htmlReportPath, this.generateHtmlReport(report));

    console.log(`Performance report generated:`);
    console.log(`  JSON: ${reportPath}`);
    console.log(`  HTML: ${htmlReportPath}`);

    return report;
  }

  /**
   * Generate summary statistics
   */
  generateSummary(chunks) {
    const lazyChunks = chunks.filter(chunk => chunk.isLazyChunk);
    const coreChunks = chunks.filter(chunk => !chunk.isLazyChunk);

    const totalSize = chunks.reduce((sum, chunk) => sum + chunk.size, 0);
    const totalGzipSize = chunks.reduce((sum, chunk) => sum + chunk.gzipSize, 0);
    const lazySize = lazyChunks.reduce((sum, chunk) => sum + chunk.size, 0);
    const lazyGzipSize = lazyChunks.reduce((sum, chunk) => sum + chunk.gzipSize, 0);

    return {
      totalChunks: chunks.length,
      lazyChunks: lazyChunks.length,
      coreChunks: coreChunks.length,
      totalSize: this.formatBytes(totalSize),
      totalGzipSize: this.formatBytes(totalGzipSize),
      lazySize: this.formatBytes(lazySize),
      lazyGzipSize: this.formatBytes(lazyGzipSize),
      lazySizePercentage: ((lazySize / totalSize) * 100).toFixed(1),
      averageCompressionRatio: (
        chunks.reduce((sum, chunk) => sum + chunk.compressionRatio, 0) / chunks.length
      ).toFixed(1),
      chunksExceedingThreshold: chunks.filter(chunk => 
        chunk.exceedsThreshold.size || chunk.exceedsThreshold.gzip
      ).length,
    };
  }

  /**
   * Generate optimization recommendations
   */
  generateRecommendations(chunks) {
    const recommendations = [];

    // Check for oversized chunks
    const oversizedChunks = chunks.filter(chunk => chunk.exceedsThreshold.size);
    if (oversizedChunks.length > 0) {
      recommendations.push({
        type: 'warning',
        title: 'Oversized Chunks Detected',
        description: `${oversizedChunks.length} chunks exceed the size threshold of ${this.formatBytes(this.options.thresholds.chunkSize)}`,
        chunks: oversizedChunks.map(chunk => chunk.name),
        suggestion: 'Consider further splitting these chunks or removing unused code.',
      });
    }

    // Check compression ratios
    const poorCompressionChunks = chunks.filter(chunk => chunk.compressionRatio < 50);
    if (poorCompressionChunks.length > 0) {
      recommendations.push({
        type: 'info',
        title: 'Poor Compression Ratios',
        description: `${poorCompressionChunks.length} chunks have compression ratios below 50%`,
        chunks: poorCompressionChunks.map(chunk => chunk.name),
        suggestion: 'These chunks may contain binary data or already compressed content.',
      });
    }

    // Check lazy loading distribution
    const lazyChunks = chunks.filter(chunk => chunk.isLazyChunk);
    const coreChunks = chunks.filter(chunk => !chunk.isLazyChunk);
    const lazyRatio = lazyChunks.length / chunks.length;

    if (lazyRatio < 0.3) {
      recommendations.push({
        type: 'suggestion',
        title: 'Low Lazy Loading Adoption',
        description: `Only ${(lazyRatio * 100).toFixed(1)}% of chunks are lazy-loaded`,
        suggestion: 'Consider lazy loading more components to improve initial bundle size.',
      });
    }

    // Category-specific recommendations
    const categoryStats = this.getCategoryStats(chunks);
    for (const [category, stats] of Object.entries(categoryStats)) {
      if (stats.averageSize > this.options.thresholds.chunkSize) {
        recommendations.push({
          type: 'warning',
          title: `Large ${category} Chunks`,
          description: `${category} chunks average ${this.formatBytes(stats.averageSize)}`,
          suggestion: `Consider splitting ${category} components into smaller chunks.`,
        });
      }
    }

    return recommendations;
  }

  /**
   * Get statistics by category
   */
  getCategoryStats(chunks) {
    const stats = {};

    chunks.forEach(chunk => {
      if (!stats[chunk.category]) {
        stats[chunk.category] = {
          count: 0,
          totalSize: 0,
          totalGzipSize: 0,
        };
      }

      stats[chunk.category].count++;
      stats[chunk.category].totalSize += chunk.size;
      stats[chunk.category].totalGzipSize += chunk.gzipSize;
    });

    // Calculate averages
    Object.keys(stats).forEach(category => {
      const categoryStats = stats[category];
      categoryStats.averageSize = categoryStats.totalSize / categoryStats.count;
      categoryStats.averageGzipSize = categoryStats.totalGzipSize / categoryStats.count;
    });

    return stats;
  }

  /**
   * Generate HTML report
   */
  generateHtmlReport(report) {
    return `
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lazy Loading Performance Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .metric-label { font-size: 14px; color: #666; margin-top: 5px; }
        .recommendations { margin: 20px 0; }
        .recommendation { margin: 10px 0; padding: 15px; border-radius: 6px; }
        .recommendation.warning { background: #fff3cd; border-left: 4px solid #ffc107; }
        .recommendation.info { background: #d1ecf1; border-left: 4px solid #17a2b8; }
        .recommendation.suggestion { background: #d4edda; border-left: 4px solid #28a745; }
        .chunks-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .chunks-table th, .chunks-table td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        .chunks-table th { background: #f8f9fa; font-weight: 600; }
        .chunk-lazy { color: #28a745; font-weight: 500; }
        .chunk-core { color: #6c757d; }
        .size-warning { color: #dc3545; font-weight: 500; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Lazy Loading Performance Report</h1>
        <p>Generated: ${new Date(report.timestamp).toLocaleString('pl-PL')}</p>
        
        <h2>Summary</h2>
        <div class="summary">
            <div class="metric">
                <div class="metric-value">${report.summary.totalChunks}</div>
                <div class="metric-label">Total Chunks</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.lazyChunks}</div>
                <div class="metric-label">Lazy Chunks</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.totalSize}</div>
                <div class="metric-label">Total Size</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.totalGzipSize}</div>
                <div class="metric-label">Gzipped Size</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.lazySizePercentage}%</div>
                <div class="metric-label">Lazy Loading Ratio</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.averageCompressionRatio}%</div>
                <div class="metric-label">Avg Compression</div>
            </div>
        </div>

        <h2>Recommendations</h2>
        <div class="recommendations">
            ${report.recommendations.map(rec => `
                <div class="recommendation ${rec.type}">
                    <h3>${rec.title}</h3>
                    <p>${rec.description}</p>
                    <p><strong>Suggestion:</strong> ${rec.suggestion}</p>
                    ${rec.chunks ? `<p><strong>Affected chunks:</strong> ${rec.chunks.join(', ')}</p>` : ''}
                </div>
            `).join('')}
        </div>

        <h2>Chunk Details</h2>
        <table class="chunks-table">
            <thead>
                <tr>
                    <th>Chunk Name</th>
                    <th>Category</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Gzipped</th>
                    <th>Compression</th>
                </tr>
            </thead>
            <tbody>
                ${report.chunks.map(chunk => `
                    <tr>
                        <td>${chunk.name}</td>
                        <td>${chunk.category}</td>
                        <td class="${chunk.isLazyChunk ? 'chunk-lazy' : 'chunk-core'}">
                            ${chunk.isLazyChunk ? 'Lazy' : 'Core'}
                        </td>
                        <td class="${chunk.exceedsThreshold.size ? 'size-warning' : ''}">
                            ${this.formatBytes(chunk.size)}
                        </td>
                        <td class="${chunk.exceedsThreshold.gzip ? 'size-warning' : ''}">
                            ${this.formatBytes(chunk.gzipSize)}
                        </td>
                        <td>${chunk.compressionRatio.toFixed(1)}%</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    </div>
</body>
</html>`;
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
  const buildPath = process.argv[2] || path.join(process.cwd(), 'build');
  
  const monitor = new LazyLoadingPerformanceMonitor();
  
  monitor.analyzeBuildOutput(buildPath)
    .then(report => {
      console.log('\nPerformance Analysis Complete!');
      console.log(`Total chunks: ${report.summary.totalChunks}`);
      console.log(`Lazy chunks: ${report.summary.lazyChunks}`);
      console.log(`Total size: ${report.summary.totalSize}`);
      console.log(`Gzipped size: ${report.summary.totalGzipSize}`);
      console.log(`Recommendations: ${report.recommendations.length}`);
    })
    .catch(error => {
      console.error('Error analyzing build output:', error);
      process.exit(1);
    });
}

module.exports = LazyLoadingPerformanceMonitor;