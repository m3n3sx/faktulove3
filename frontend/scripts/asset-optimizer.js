/**
 * Asset Optimizer
 * 
 * Optimizes fonts, icons, and other static assets for better performance
 */

const fs = require('fs');
const path = require('path');

class AssetOptimizer {
  constructor(options = {}) {
    this.options = {
      // Asset directories
      fontsDir: './public/fonts',
      iconsDir: './src/design-system/icons',
      imagesDir: './public/images',
      
      // Output directory
      outputDir: './build/static',
      
      // Font optimization
      fontOptimization: {
        // Font formats to generate
        formats: ['woff2', 'woff'],
        
        // Font subsets to create
        subsets: {
          latin: 'U+0020-007F',
          'latin-ext': 'U+0100-017F,U+0180-024F,U+1E00-1EFF',
          polish: 'U+0100-017F,U+0104,U+0106,U+0118,U+0141,U+0143,U+00D3,U+015A,U+0179,U+017B,U+0105,U+0107,U+0119,U+0142,U+0144,U+00F3,U+015B,U+017A,U+017C',
        },
        
        // Font display strategy
        fontDisplay: 'swap',
        
        // Preload critical fonts
        preloadFonts: [
          'Inter-Regular.woff2',
          'Inter-Medium.woff2',
          'Inter-SemiBold.woff2',
        ],
      },
      
      // Icon optimization
      iconOptimization: {
        // SVG optimization settings
        svgoConfig: {
          plugins: [
            'removeDoctype',
            'removeXMLProcInst',
            'removeComments',
            'removeMetadata',
            'removeTitle',
            'removeDesc',
            'removeUselessDefs',
            'removeEditorsNSData',
            'removeEmptyAttrs',
            'removeHiddenElems',
            'removeEmptyText',
            'removeEmptyContainers',
            'removeViewBox',
            'cleanupEnableBackground',
            'convertStyleToAttrs',
            'convertColors',
            'convertPathData',
            'convertTransform',
            'removeUnknownsAndDefaults',
            'removeNonInheritableGroupAttrs',
            'removeUselessStrokeAndFill',
            'removeUnusedNS',
            'cleanupIDs',
            'cleanupNumericValues',
            'moveElemsAttrsToGroup',
            'moveGroupAttrsToElems',
            'collapseGroups',
            'removeRasterImages',
            'mergePaths',
            'convertShapeToPath',
            'sortAttrs',
            'removeDimensions',
          ],
        },
        
        // Icon sprite generation
        generateSprite: true,
        spriteFileName: 'icons.svg',
        
        // Icon categories for lazy loading
        categories: {
          critical: ['chevron-down', 'menu', 'close', 'search', 'user'],
          business: ['invoice', 'currency', 'calculator', 'chart', 'document'],
          ui: ['check', 'alert', 'info', 'warning', 'error'],
          navigation: ['arrow-left', 'arrow-right', 'home', 'settings'],
        },
      },
      
      // Image optimization
      imageOptimization: {
        // Quality settings
        jpeg: { quality: 85 },
        png: { quality: 90 },
        webp: { quality: 80 },
        
        // Generate responsive images
        responsive: {
          sizes: [320, 640, 768, 1024, 1280, 1920],
          formats: ['webp', 'jpg'],
        },
        
        // Lazy loading placeholder
        placeholder: {
          generate: true,
          quality: 20,
          blur: 5,
        },
      },
      
      ...options,
    };
  }

  /**
   * Optimize all assets
   */
  async optimizeAssets() {
    const results = {
      fonts: await this.optimizeFonts(),
      icons: await this.optimizeIcons(),
      images: await this.optimizeImages(),
      timestamp: Date.now(),
    };

    // Generate asset manifest
    await this.generateAssetManifest(results);
    
    // Generate preload hints
    await this.generatePreloadHints(results);
    
    return results;
  }

  /**
   * Optimize fonts
   */
  async optimizeFonts() {
    const results = {
      processed: [],
      errors: [],
      preloadHints: [],
      cssGenerated: '',
    };

    if (!fs.existsSync(this.options.fontsDir)) {
      results.errors.push('Fonts directory not found');
      return results;
    }

    const fontFiles = fs.readdirSync(this.options.fontsDir)
      .filter(file => file.match(/\.(ttf|otf|woff|woff2)$/));

    for (const fontFile of fontFiles) {
      try {
        const result = await this.processFontFile(fontFile);
        results.processed.push(result);
        
        // Generate CSS for font
        results.cssGenerated += this.generateFontCSS(result);
        
        // Add preload hints for critical fonts
        if (this.options.fontOptimization.preloadFonts.includes(result.woff2File)) {
          results.preloadHints.push({
            href: `/fonts/${result.woff2File}`,
            as: 'font',
            type: 'font/woff2',
            crossorigin: 'anonymous',
          });
        }
      } catch (error) {
        results.errors.push({
          file: fontFile,
          error: error.message,
        });
      }
    }

    // Write font CSS file
    const fontCSSPath = path.join(this.options.outputDir, 'css', 'fonts.css');
    await this.ensureDirectoryExists(path.dirname(fontCSSPath));
    fs.writeFileSync(fontCSSPath, results.cssGenerated);

    return results;
  }

  /**
   * Process a single font file
   */
  async processFontFile(fontFile) {
    const fontPath = path.join(this.options.fontsDir, fontFile);
    const fontName = path.basename(fontFile, path.extname(fontFile));
    
    // For this example, we'll assume the fonts are already optimized
    // In a real implementation, you'd use tools like fonttools or similar
    
    const result = {
      originalFile: fontFile,
      fontName: fontName,
      woff2File: `${fontName}.woff2`,
      woffFile: `${fontName}.woff`,
      subsets: Object.keys(this.options.fontOptimization.subsets),
      sizeBefore: fs.statSync(fontPath).size,
      sizeAfter: fs.statSync(fontPath).size, // Placeholder
    };

    return result;
  }

  /**
   * Generate CSS for font
   */
  generateFontCSS(fontResult) {
    const fontFamily = fontResult.fontName.replace(/-/g, ' ');
    
    let css = '';
    
    // Generate @font-face for each subset
    for (const subset of fontResult.subsets) {
      css += `
@font-face {
  font-family: '${fontFamily}';
  font-style: normal;
  font-weight: 400;
  font-display: ${this.options.fontOptimization.fontDisplay};
  src: url('/fonts/${fontResult.woff2File}') format('woff2'),
       url('/fonts/${fontResult.woffFile}') format('woff');
  unicode-range: ${this.options.fontOptimization.subsets[subset]};
}
`;
    }
    
    return css;
  }

  /**
   * Optimize icons
   */
  async optimizeIcons() {
    const results = {
      processed: [],
      errors: [],
      sprite: null,
      categories: {},
    };

    if (!fs.existsSync(this.options.iconsDir)) {
      results.errors.push('Icons directory not found');
      return results;
    }

    const iconFiles = fs.readdirSync(this.options.iconsDir)
      .filter(file => file.endsWith('.svg'));

    // Process individual icons
    for (const iconFile of iconFiles) {
      try {
        const result = await this.processIconFile(iconFile);
        results.processed.push(result);
        
        // Categorize icon
        const category = this.categorizeIcon(iconFile);
        if (!results.categories[category]) {
          results.categories[category] = [];
        }
        results.categories[category].push(result);
      } catch (error) {
        results.errors.push({
          file: iconFile,
          error: error.message,
        });
      }
    }

    // Generate icon sprite
    if (this.options.iconOptimization.generateSprite) {
      results.sprite = await this.generateIconSprite(results.processed);
    }

    return results;
  }

  /**
   * Process a single icon file
   */
  async processIconFile(iconFile) {
    const iconPath = path.join(this.options.iconsDir, iconFile);
    const iconName = path.basename(iconFile, '.svg');
    
    let svgContent = fs.readFileSync(iconPath, 'utf8');
    const sizeBefore = Buffer.byteLength(svgContent, 'utf8');
    
    // Basic SVG optimization (in real implementation, use SVGO)
    svgContent = svgContent
      .replace(/<!--[\s\S]*?-->/g, '') // Remove comments
      .replace(/\s+/g, ' ') // Collapse whitespace
      .replace(/>\s+</g, '><') // Remove whitespace between tags
      .trim();
    
    const sizeAfter = Buffer.byteLength(svgContent, 'utf8');
    
    // Write optimized icon
    const outputPath = path.join(this.options.outputDir, 'icons', iconFile);
    await this.ensureDirectoryExists(path.dirname(outputPath));
    fs.writeFileSync(outputPath, svgContent);
    
    return {
      originalFile: iconFile,
      iconName: iconName,
      optimizedFile: outputPath,
      sizeBefore: sizeBefore,
      sizeAfter: sizeAfter,
      savings: sizeBefore - sizeAfter,
      savingsPercentage: ((sizeBefore - sizeAfter) / sizeBefore * 100).toFixed(1),
    };
  }

  /**
   * Categorize icon based on name
   */
  categorizeIcon(iconFile) {
    const iconName = path.basename(iconFile, '.svg');
    
    for (const [category, icons] of Object.entries(this.options.iconOptimization.categories)) {
      if (icons.includes(iconName)) {
        return category;
      }
    }
    
    return 'other';
  }

  /**
   * Generate icon sprite
   */
  async generateIconSprite(processedIcons) {
    let spriteContent = '<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">\n';
    
    for (const icon of processedIcons) {
      const iconPath = icon.optimizedFile;
      let iconSVG = fs.readFileSync(iconPath, 'utf8');
      
      // Extract SVG content and wrap in symbol
      const svgMatch = iconSVG.match(/<svg[^>]*>([\s\S]*?)<\/svg>/);
      if (svgMatch) {
        const content = svgMatch[1];
        const viewBoxMatch = iconSVG.match(/viewBox="([^"]*)"/);
        const viewBox = viewBoxMatch ? viewBoxMatch[1] : '0 0 24 24';
        
        spriteContent += `  <symbol id="icon-${icon.iconName}" viewBox="${viewBox}">\n`;
        spriteContent += `    ${content}\n`;
        spriteContent += `  </symbol>\n`;
      }
    }
    
    spriteContent += '</svg>';
    
    // Write sprite file
    const spritePath = path.join(this.options.outputDir, 'icons', this.options.iconOptimization.spriteFileName);
    fs.writeFileSync(spritePath, spriteContent);
    
    return {
      file: spritePath,
      icons: processedIcons.length,
      size: Buffer.byteLength(spriteContent, 'utf8'),
    };
  }

  /**
   * Optimize images (placeholder implementation)
   */
  async optimizeImages() {
    const results = {
      processed: [],
      errors: [],
      responsive: [],
    };

    // This would implement image optimization using tools like sharp or imagemin
    // For now, it's a placeholder
    
    return results;
  }

  /**
   * Generate asset manifest
   */
  async generateAssetManifest(results) {
    const manifest = {
      timestamp: results.timestamp,
      fonts: {
        files: results.fonts.processed.map(font => ({
          name: font.fontName,
          woff2: `/fonts/${font.woff2File}`,
          woff: `/fonts/${font.woffFile}`,
          preload: this.options.fontOptimization.preloadFonts.includes(font.woff2File),
        })),
        css: '/css/fonts.css',
      },
      icons: {
        sprite: results.icons.sprite ? `/icons/${this.options.iconOptimization.spriteFileName}` : null,
        categories: Object.keys(results.icons.categories),
        individual: results.icons.processed.map(icon => ({
          name: icon.iconName,
          file: `/icons/${icon.originalFile}`,
          category: this.categorizeIcon(icon.originalFile),
        })),
      },
      images: {
        // Placeholder for image manifest
      },
    };

    const manifestPath = path.join(this.options.outputDir, 'asset-manifest.json');
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
    
    console.log(`Asset manifest generated: ${manifestPath}`);
    
    return manifest;
  }

  /**
   * Generate preload hints
   */
  async generatePreloadHints(results) {
    const hints = [];
    
    // Font preload hints
    results.fonts.preloadHints.forEach(hint => {
      hints.push(`<link rel="preload" href="${hint.href}" as="${hint.as}" type="${hint.type}" crossorigin="${hint.crossorigin}">`);
    });
    
    // Critical icon sprite preload
    if (results.icons.sprite) {
      hints.push(`<link rel="preload" href="/icons/${this.options.iconOptimization.spriteFileName}" as="image" type="image/svg+xml">`);
    }
    
    // Write preload hints file
    const hintsPath = path.join(this.options.outputDir, 'preload-hints.html');
    fs.writeFileSync(hintsPath, hints.join('\n'));
    
    console.log(`Preload hints generated: ${hintsPath}`);
    
    return hints;
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
  const optimizer = new AssetOptimizer();
  
  optimizer.optimizeAssets()
    .then(results => {
      console.log('\nAsset Optimization Complete!');
      console.log(`Fonts processed: ${results.fonts.processed.length}`);
      console.log(`Icons processed: ${results.icons.processed.length}`);
      console.log(`Images processed: ${results.images.processed.length}`);
      
      if (results.icons.sprite) {
        console.log(`Icon sprite generated: ${optimizer.formatBytes(results.icons.sprite.size)}`);
      }
    })
    .catch(error => {
      console.error('Error optimizing assets:', error);
      process.exit(1);
    });
}

module.exports = AssetOptimizer;