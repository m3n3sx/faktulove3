/**
 * Webpack Configuration for Design System Bundle Optimization
 * 
 * This configuration extends Create React App's webpack setup
 * to optimize the design system bundle size and performance.
 */

const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');
const LazyLoadingPlugin = require('./scripts/webpack-lazy-loading-plugin');
const buildConfig = require('./build-config');

module.exports = function override(config, env) {
  // Apply design system integration optimizations
  const isProduction = env === 'production';
  
  // Configure bundle splitting for design system
  if (isProduction) {
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        ...config.optimization.splitChunks,
        cacheGroups: {
          ...config.optimization.splitChunks.cacheGroups,
          
          // Apply build config bundle splitting
          ...Object.entries(buildConfig.bundleSplitting).reduce((acc, [key, value]) => {
            acc[key] = value;
            return acc;
          }, {}),
        },
      },
    };

    // Tree shaking optimization with design system configuration
    config.optimization.usedExports = true;
    config.optimization.sideEffects = buildConfig.treeShaking.sideEffects;

    // Add compression plugins
    if (buildConfig.production.compression.includes('gzip')) {
      config.plugins.push(
        new CompressionPlugin(buildConfig.compression.gzip)
      );
    }

    // Lazy loading optimization plugin
    config.plugins.push(
      new LazyLoadingPlugin({
        generatePreloadManifest: true,
        optimizeChunkNames: true,
        addResourceHints: true,
      })
    );

    // CSS optimization plugins
    if (buildConfig.cssOptimization.criticalCSS.enabled) {
      const CriticalCSSExtractor = require('./scripts/critical-css-extractor');
      const criticalExtractor = new CriticalCSSExtractor(buildConfig.cssOptimization.criticalCSS);
      
      // Add critical CSS extraction to the build process
      config.plugins.push({
        apply: (compiler) => {
          compiler.hooks.afterEmit.tapAsync('CriticalCSSExtractor', (compilation, callback) => {
            criticalExtractor.extractCriticalCSS()
              .then(() => callback())
              .catch(callback);
          });
        },
      });
    }

    // Asset optimization
    const AssetOptimizer = require('./scripts/asset-optimizer');
    const assetOptimizer = new AssetOptimizer(buildConfig.cssOptimization.assets);
    
    config.plugins.push({
      apply: (compiler) => {
        compiler.hooks.afterEmit.tapAsync('AssetOptimizer', (compilation, callback) => {
          assetOptimizer.optimizeAssets()
            .then(() => callback())
            .catch(callback);
        });
      },
    });

    // Bundle analyzer (only when ANALYZE=true)
    if (buildConfig.production.bundleAnalysis) {
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: 'bundle-report.html',
        })
      );
    }
  }

  // Resolve aliases for design system
  config.resolve.alias = {
    ...config.resolve.alias,
    '@/design-system': path.resolve(__dirname, 'src/design-system'),
    '@/components': path.resolve(__dirname, 'src/components'),
    '@/pages': path.resolve(__dirname, 'src/pages'),
    '@/utils': path.resolve(__dirname, 'src/utils'),
  };

  // CSS optimization with design system integration
  const cssRule = config.module.rules.find(rule => 
    rule.test && rule.test.toString().includes('css')
  );
  
  if (cssRule) {
    // Enhance existing CSS rule for design system
    cssRule.use = cssRule.use.map(use => {
      if (typeof use === 'object' && use.loader && use.loader.includes('css-loader')) {
        return {
          ...use,
          options: {
            ...use.options,
            modules: {
              auto: (resourcePath) => {
                // Enable CSS modules for component styles, but not for design system tokens
                return resourcePath.includes('/components/') && 
                       !resourcePath.includes('/design-system/styles/');
              },
              localIdentName: isProduction ? '[hash:base64:5]' : '[name]__[local]--[hash:base64:5]',
            },
            importLoaders: 1,
          },
        };
      }
      return use;
    });
  } else {
    // Add CSS rule if not found
    config.module.rules.push({
      test: /\.css$/,
      use: [
        'style-loader',
        {
          loader: 'css-loader',
          options: {
            modules: {
              auto: (resourcePath) => {
                return resourcePath.includes('/components/') && 
                       !resourcePath.includes('/design-system/styles/');
              },
              localIdentName: isProduction ? '[hash:base64:5]' : '[name]__[local]--[hash:base64:5]',
            },
            importLoaders: 1,
          },
        },
        'postcss-loader',
      ],
    });
  }

  return config;
};