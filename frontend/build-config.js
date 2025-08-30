/**
 * Build Configuration for Design System Optimization
 * 
 * Configuration settings for optimizing the design system build process.
 */

module.exports = {
  // Bundle splitting configuration with lazy loading optimization
  bundleSplitting: {
    // Design system core (tokens, utilities, providers) - highest priority
    designSystemCore: {
      name: 'design-system-core',
      test: /[\\/]src[\\/]design-system[\\/](tokens|utils|providers|context|types)[\\/]/,
      priority: 50,
      chunks: 'all',
      reuseExistingChunk: true,
      enforce: true,
    },
    
    // Design system primitives (buttons, inputs) - high priority for immediate loading
    designSystemPrimitives: {
      name: 'design-system-primitives',
      test: /[\\/]src[\\/]design-system[\\/]components[\\/]primitives[\\/](Button|Input|Typography)[\\/]/,
      priority: 45,
      chunks: 'all',
      reuseExistingChunk: true,
    },
    
    // Design system forms - lazy loaded
    designSystemForms: {
      name: 'design-system-forms',
      test: /[\\/]src[\\/]design-system[\\/]components[\\/]primitives[\\/](Textarea|Select|Checkbox|Radio|Switch)[\\/]/,
      priority: 40,
      chunks: 'async',
      reuseExistingChunk: true,
    },
    
    // Design system layouts - lazy loaded
    designSystemLayouts: {
      name: 'design-system-layouts',
      test: /[\\/]src[\\/]design-system[\\/]components[\\/]layouts[\\/]/,
      priority: 35,
      chunks: 'async',
      reuseExistingChunk: true,
    },
    
    // Polish business components - lazy loaded
    polishBusiness: {
      name: 'polish-business',
      test: /[\\/]src[\\/]design-system[\\/]components[\\/]business[\\/]/,
      priority: 30,
      chunks: 'async',
      reuseExistingChunk: true,
    },
    
    // Pattern components - lazy loaded
    designSystemPatterns: {
      name: 'design-system-patterns',
      test: /[\\/]src[\\/]design-system[\\/]components[\\/]patterns[\\/]/,
      priority: 25,
      chunks: 'async',
      reuseExistingChunk: true,
    },
    
    // Accessibility components - lazy loaded
    designSystemAccessibility: {
      name: 'design-system-accessibility',
      test: /[\\/]src[\\/]design-system[\\/]components[\\/]accessibility[\\/]/,
      priority: 20,
      chunks: 'async',
      reuseExistingChunk: true,
    },
    
    // React vendor chunk
    react: {
      name: 'react-vendor',
      test: /[\\/]node_modules[\\/](react|react-dom|react-router|react-query)[\\/]/,
      priority: 15,
      chunks: 'all',
    },
    
    // UI libraries
    uiLibraries: {
      name: 'ui-libraries',
      test: /[\\/]node_modules[\\/](lucide-react|clsx|react-hot-toast)[\\/]/,
      priority: 10,
      chunks: 'all',
    },
  },

  // Tree shaking configuration
  treeShaking: {
    // Mark design system as side-effect free
    sideEffects: [
      '**/*.css',
      '**/*.scss',
      '**/*.sass',
      '**/*.less',
      '**/polyfills.js',
    ],
    
    // Modules to optimize
    optimizeModules: [
      'src/design-system',
      'lucide-react',
      'react-query',
    ],
  },

  // CSS optimization with enhanced tree-shaking
  cssOptimization: {
    // Enhanced PurgeCSS configuration
    purgeCSS: {
      content: [
        './src/**/*.{js,jsx,ts,tsx}',
        './public/index.html',
        './src/design-system/**/*.{js,jsx,ts,tsx}',
        '../faktury/templates/**/*.html',
        '../faktury/templatetags/**/*.py',
      ],
      
      // Safelist for dynamic classes
      safelist: [
        // Design system prefixes
        /^ds-/,
        
        // State classes
        /^(hover|focus|active|disabled|loading|selected|checked|invalid|valid):/,
        
        // Responsive classes
        /^(sm|md|lg|xl|2xl):/,
        
        // Polish business classes
        /^(currency|nip|vat|invoice|polish-business)-/,
        
        // Animation classes
        /^animate-/,
        /^transition-/,
        
        // Accessibility
        'sr-only',
        'focus-visible',
        'visually-hidden',
        'screen-reader-only',
        
        // Form states
        'invalid',
        'valid',
        'required',
        'optional',
        'pristine',
        'dirty',
        'touched',
        'untouched',
        
        // Loading states
        'loading',
        'loaded',
        'error',
        'success',
        'pending',
        
        // Theme classes
        'theme-light',
        'theme-dark',
        'theme-polish-business',
        'theme-high-contrast',
        
        // Component states
        'open',
        'closed',
        'expanded',
        'collapsed',
        'visible',
        'hidden',
        
        // Common utilities that might be used dynamically
        'text-primary-600',
        'text-success-600',
        'text-warning-600',
        'text-error-600',
        'bg-primary-600',
        'bg-success-600',
        'bg-warning-600',
        'bg-error-600',
      ],
      
      // Enhanced patterns for dynamic classes
      safelistPatterns: [
        // Color utilities (all variants)
        /^text-(primary|secondary|success|warning|error|muted)-(50|100|200|300|400|500|600|700|800|900)$/,
        /^bg-(primary|secondary|success|warning|error|muted)-(50|100|200|300|400|500|600|700|800|900)$/,
        /^border-(primary|secondary|success|warning|error|muted)-(50|100|200|300|400|500|600|700|800|900)$/,
        
        // Spacing utilities (extended range)
        /^(p|m|px|py|mx|my|pt|pb|pl|pr|mt|mb|ml|mr)-(0|0\.5|1|1\.5|2|2\.5|3|3\.5|4|5|6|7|8|9|10|11|12|14|16|20|24|28|32|36|40|44|48|52|56|60|64|72|80|96)$/,
        
        // Typography utilities
        /^text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)$/,
        /^font-(thin|extralight|light|normal|medium|semibold|bold|extrabold|black)$/,
        /^leading-(none|tight|snug|normal|relaxed|loose|3|4|5|6|7|8|9|10)$/,
        /^tracking-(tighter|tight|normal|wide|wider|widest)$/,
        
        // Layout utilities
        /^(w|h|min-w|min-h|max-w|max-h)-(0|px|0\.5|1|1\.5|2|2\.5|3|3\.5|4|5|6|7|8|9|10|11|12|14|16|20|24|28|32|36|40|44|48|52|56|60|64|72|80|96|auto|full|screen|min|max|fit)$/,
        
        // Flexbox and Grid utilities
        /^(flex|items|justify|content|self)-(start|end|center|between|around|evenly|stretch|baseline|auto)$/,
        /^(grid-cols|col-span|row-span|grid-rows)-(1|2|3|4|5|6|7|8|9|10|11|12|auto|subgrid)$/,
        /^(order)-(1|2|3|4|5|6|7|8|9|10|11|12|first|last|none)$/,
        
        // Border utilities
        /^rounded-(none|xs|sm|md|lg|xl|2xl|3xl|full)$/,
        /^border-(0|1|2|4|8)$/,
        /^(border-t|border-r|border-b|border-l)-(0|1|2|4|8)$/,
        
        // Shadow utilities
        /^shadow-(none|xs|sm|md|lg|xl|2xl|inner)$/,
        
        // Position utilities
        /^(top|right|bottom|left|inset)-(0|px|0\.5|1|1\.5|2|2\.5|3|3\.5|4|5|6|7|8|9|10|11|12|14|16|20|24|28|32|36|40|44|48|52|56|60|64|72|80|96|auto|full)$/,
        
        // Z-index utilities
        /^z-(0|10|20|30|40|50|auto)$/,
        
        // Opacity utilities
        /^opacity-(0|5|10|20|25|30|40|50|60|70|75|80|90|95|100)$/,
        
        // Polish business specific patterns
        /^(nip|regon|krs|vat|currency|invoice)-(valid|invalid|pending|processing|completed|error|success|warning)$/,
        /^(currency)-(pln|eur|usd)$/,
        /^(vat)-(0|5|8|23)$/,
        
        // Component state patterns
        /^(button|input|select|checkbox|radio|card|modal|dropdown)-(primary|secondary|success|warning|error|disabled|loading|active|focus|hover)$/,
        
        // Responsive patterns
        /^(sm|md|lg|xl|2xl):(.*?)$/,
        
        // Dark mode patterns
        /^dark:(.*?)$/,
        
        // Motion patterns
        /^(motion-safe|motion-reduce):(.*?)$/,
      ],
      
      // Blocklist for classes to always remove
      blocklist: [
        // Development only classes
        /^debug-/,
        /^dev-/,
        /^test-/,
        
        // Unused framework classes
        /^unused-/,
        
        // Old component classes (if migrating)
        /^old-/,
        /^legacy-/,
        /^deprecated-/,
        
        // Specific unused utilities
        'container', // If not using Tailwind's container
      ],
      
      // Variables to keep
      variables: true,
      
      // Keyframes to keep
      keyframes: true,
      
      // Font faces to keep
      fontFace: true,
    },
    
    // Critical CSS extraction
    criticalCSS: {
      enabled: true,
      maxSize: 14 * 1024, // 14KB
      inlineThreshold: 2 * 1024, // 2KB - inline if smaller
      
      // Critical selectors (always include)
      criticalSelectors: [
        'html',
        'body',
        '*',
        '*::before',
        '*::after',
        '.ds-theme-light',
        '.ds-theme-dark',
        '.ds-container',
        '.ds-button',
        '.ds-input',
        '.ds-nav',
        '.sr-only',
        '.focus-visible',
      ],
      
      // Critical patterns
      criticalPatterns: [
        /^(sm|md):/, // Mobile-first critical breakpoints
        /^(p|m|px|py|mx|my)-(0|1|2|3|4)$/, // Essential spacing
        /^(text|bg)-(primary|error|success)-(600|700|800)$/, // Essential colors
        /^(flex|grid|block|inline|hidden)$/, // Essential display
      ],
    },
    
    // Enhanced CSS minification
    minification: {
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
        mergeLonghand: true,
        mergeIdents: false, // Keep animation names
        discardUnused: true,
        autoprefixer: {
          add: true,
          remove: true,
        },
      }],
    },
    
    // Asset optimization
    assets: {
      // Font optimization
      fonts: {
        preload: ['Inter-Regular.woff2', 'Inter-Medium.woff2'],
        display: 'swap',
        subsets: ['latin', 'latin-ext', 'polish'],
      },
      
      // Icon optimization
      icons: {
        sprite: true,
        optimize: true,
        categories: {
          critical: ['chevron-down', 'menu', 'close', 'search'],
          business: ['invoice', 'currency', 'calculator'],
          ui: ['check', 'alert', 'info', 'warning', 'error'],
        },
      },
      
      // Image optimization
      images: {
        formats: ['webp', 'avif', 'jpg', 'png'],
        quality: { webp: 80, avif: 75, jpg: 85, png: 90 },
        responsive: true,
        lazy: true,
      },
    },
  },

  // Dynamic import optimization
  dynamicImports: {
    // Preload strategy for dynamic imports
    preloadStrategy: {
      // Preload on idle
      idle: [
        'design-system-layouts',
        'design-system-forms',
      ],
      
      // Preload on interaction
      interaction: [
        'polish-business',
        'design-system-accessibility',
      ],
      
      // Load on demand
      onDemand: [
        'design-system-patterns',
      ],
    },
    
    // Webpack magic comments for dynamic imports
    webpackChunkNames: {
      polishBusiness: 'polish-business-[index]',
      patterns: 'patterns-[index]',
      accessibility: 'accessibility-[index]',
      layouts: 'layouts-[index]',
      forms: 'forms-[index]',
    },
    
    // Prefetch and preload hints
    resourceHints: {
      prefetch: [
        'polish-business',
        'design-system-patterns',
      ],
      preload: [
        'design-system-core',
        'design-system-primitives',
      ],
    },
  },

  // Performance budgets with lazy loading considerations
  performanceBudgets: {
    // Bundle size limits (adjusted for lazy loading)
    maxBundleSize: {
      javascript: 800 * 1024, // 800KB (reduced due to lazy loading)
      css: 80 * 1024, // 80KB
      designSystemCore: 150 * 1024, // 150KB (core components)
      designSystemLazy: 100 * 1024, // 100KB per lazy chunk
      total: 1.2 * 1024 * 1024, // 1.2MB (reduced total)
    },
    
    // Gzip size limits
    maxGzipSize: {
      javascript: 250 * 1024, // 250KB
      css: 25 * 1024, // 25KB
      designSystemCore: 45 * 1024, // 45KB
      designSystemLazy: 30 * 1024, // 30KB per lazy chunk
      total: 350 * 1024, // 350KB
    },
    
    // Performance metrics (improved with lazy loading)
    coreWebVitals: {
      lcp: 2000, // 2.0 seconds (improved)
      fid: 80, // 80ms (improved)
      cls: 0.08, // 0.08 (improved)
      fcp: 1500, // 1.5 seconds (improved)
      ttfb: 500, // 500ms (improved)
    },
    
    // Lazy loading specific metrics
    lazyLoadingMetrics: {
      maxChunkLoadTime: 500, // 500ms max for lazy chunks
      maxConcurrentChunks: 3, // Max 3 chunks loading simultaneously
      preloadThreshold: 100, // 100ms before user needs component
    },
  },

  // Compression settings
  compression: {
    gzip: {
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192, // 8KB
      minRatio: 0.8,
    },
    
    brotli: {
      algorithm: 'brotliCompress',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8,
    },
  },

  // Development optimizations
  development: {
    // Fast refresh for design system components
    fastRefresh: true,
    
    // Source maps
    sourceMaps: 'eval-source-map',
    
    // Hot module replacement
    hmr: true,
    
    // Bundle analysis in development
    bundleAnalysis: process.env.ANALYZE === 'true',
  },

  // Production optimizations
  production: {
    // Minification
    minify: true,
    
    // Source maps
    sourceMaps: 'source-map',
    
    // Bundle splitting
    splitChunks: true,
    
    // Tree shaking
    treeShaking: true,
    
    // CSS optimization
    optimizeCSS: true,
    
    // Compression
    compression: ['gzip', 'brotli'],
    
    // Bundle analysis
    bundleAnalysis: process.env.ANALYZE === 'true',
  },
};