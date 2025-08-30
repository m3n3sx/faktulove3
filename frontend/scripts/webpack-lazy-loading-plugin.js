/**
 * Webpack Lazy Loading Plugin
 * 
 * Custom webpack plugin to optimize lazy loading of design system components
 */

const path = require('path');

class LazyLoadingPlugin {
  constructor(options = {}) {
    this.options = {
      // Default options
      generatePreloadManifest: true,
      optimizeChunkNames: true,
      addResourceHints: true,
      ...options,
    };
  }

  apply(compiler) {
    const pluginName = 'LazyLoadingPlugin';

    compiler.hooks.compilation.tap(pluginName, (compilation) => {
      // Optimize chunk names for lazy loaded components
      if (this.options.optimizeChunkNames) {
        compilation.hooks.chunkIds.tap(pluginName, (chunks) => {
          for (const chunk of chunks) {
            if (chunk.name && chunk.name.includes('lazy')) {
              // Optimize chunk names for better caching
              const optimizedName = this.optimizeChunkName(chunk.name);
              chunk.name = optimizedName;
            }
          }
        });
      }

      // Generate preload manifest
      if (this.options.generatePreloadManifest) {
        compilation.hooks.processAssets.tap(
          {
            name: pluginName,
            stage: compilation.PROCESS_ASSETS_STAGE_OPTIMIZE_INLINE,
          },
          (assets) => {
            const manifest = this.generatePreloadManifest(compilation);
            const manifestJson = JSON.stringify(manifest, null, 2);
            
            compilation.emitAsset(
              'lazy-loading-manifest.json',
              new compiler.webpack.sources.RawSource(manifestJson)
            );
          }
        );
      }

      // Add resource hints for lazy loaded chunks
      if (this.options.addResourceHints) {
        compilation.hooks.htmlWebpackPluginBeforeHtmlGeneration?.tap(
          pluginName,
          (data) => {
            const resourceHints = this.generateResourceHints(compilation);
            data.assets.resourceHints = resourceHints;
          }
        );
      }
    });

    // Optimize module concatenation for lazy chunks
    compiler.hooks.normalModuleFactory.tap(pluginName, (factory) => {
      factory.hooks.module.tap(pluginName, (module, createData) => {
        if (this.isDesignSystemModule(createData.resource)) {
          // Mark design system modules for optimization
          module.buildMeta = module.buildMeta || {};
          module.buildMeta.designSystemModule = true;
        }
      });
    });
  }

  /**
   * Optimize chunk names for better caching and identification
   */
  optimizeChunkName(originalName) {
    const nameMap = {
      'lazy-polish-business': 'pb',
      'lazy-accessibility': 'a11y',
      'lazy-patterns': 'patterns',
      'lazy-layouts': 'layouts',
      'lazy-forms': 'forms',
    };

    for (const [original, optimized] of Object.entries(nameMap)) {
      if (originalName.includes(original)) {
        return originalName.replace(original, optimized);
      }
    }

    return originalName;
  }

  /**
   * Generate preload manifest for lazy loaded components
   */
  generatePreloadManifest(compilation) {
    const manifest = {
      version: '1.0.0',
      timestamp: Date.now(),
      chunks: {},
      preloadStrategy: {
        immediate: [],
        idle: [],
        interaction: [],
        onDemand: [],
      },
    };

    // Analyze chunks and categorize them
    for (const chunk of compilation.chunks) {
      if (chunk.name) {
        const chunkInfo = {
          name: chunk.name,
          files: Array.from(chunk.files),
          size: this.calculateChunkSize(chunk, compilation),
          modules: this.getChunkModules(chunk),
        };

        manifest.chunks[chunk.name] = chunkInfo;

        // Categorize chunks based on naming patterns
        if (chunk.name.includes('design-system-core') || chunk.name.includes('primitives')) {
          manifest.preloadStrategy.immediate.push(chunk.name);
        } else if (chunk.name.includes('layouts') || chunk.name.includes('forms')) {
          manifest.preloadStrategy.idle.push(chunk.name);
        } else if (chunk.name.includes('polish-business') || chunk.name.includes('accessibility')) {
          manifest.preloadStrategy.interaction.push(chunk.name);
        } else if (chunk.name.includes('patterns') || chunk.name.includes('charts')) {
          manifest.preloadStrategy.onDemand.push(chunk.name);
        }
      }
    }

    return manifest;
  }

  /**
   * Generate resource hints for HTML
   */
  generateResourceHints(compilation) {
    const hints = {
      preload: [],
      prefetch: [],
    };

    for (const chunk of compilation.chunks) {
      if (chunk.name) {
        const files = Array.from(chunk.files);
        
        // Add preload hints for critical chunks
        if (chunk.name.includes('design-system-core') || chunk.name.includes('primitives')) {
          files.forEach(file => {
            if (file.endsWith('.js')) {
              hints.preload.push({
                href: file,
                as: 'script',
                crossorigin: 'anonymous',
              });
            } else if (file.endsWith('.css')) {
              hints.preload.push({
                href: file,
                as: 'style',
                crossorigin: 'anonymous',
              });
            }
          });
        }

        // Add prefetch hints for lazy chunks
        if (chunk.name.includes('polish-business') || chunk.name.includes('patterns')) {
          files.forEach(file => {
            if (file.endsWith('.js')) {
              hints.prefetch.push({
                href: file,
                as: 'script',
                crossorigin: 'anonymous',
              });
            }
          });
        }
      }
    }

    return hints;
  }

  /**
   * Calculate chunk size
   */
  calculateChunkSize(chunk, compilation) {
    let size = 0;
    
    for (const file of chunk.files) {
      const asset = compilation.assets[file];
      if (asset) {
        size += asset.size();
      }
    }
    
    return size;
  }

  /**
   * Get modules in chunk
   */
  getChunkModules(chunk) {
    const modules = [];
    
    for (const module of chunk.modulesIterable || []) {
      if (module.resource) {
        const relativePath = path.relative(process.cwd(), module.resource);
        modules.push(relativePath);
      }
    }
    
    return modules;
  }

  /**
   * Check if module is part of design system
   */
  isDesignSystemModule(resource) {
    if (!resource) return false;
    
    return resource.includes('/design-system/') || 
           resource.includes('\\design-system\\');
  }
}

module.exports = LazyLoadingPlugin;