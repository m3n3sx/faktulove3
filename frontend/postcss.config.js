/**
 * PostCSS Configuration for Design System
 * 
 * Optimizes CSS processing and purging for the design system using build configuration.
 */

const buildConfig = require('./build-config');

module.exports = {
  plugins: [
    // Tailwind CSS
    require('tailwindcss'),
    
    // Autoprefixer for browser compatibility
    require('autoprefixer'),
    
    // CSS optimization for production
    ...(process.env.NODE_ENV === 'production' && process.env.CSS_OPTIMIZE === 'true' ? [
      // Enhanced PurgeCSS using build configuration
      require('@fullhuman/postcss-purgecss')(buildConfig.cssOptimization.purgeCSS),
      
      // Enhanced CSS minification using build configuration
      require('cssnano')(buildConfig.cssOptimization.minification),
    ] : []),
  ],
};