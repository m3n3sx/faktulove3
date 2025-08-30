#!/usr/bin/env node

/**
 * Design System Build Script
 * 
 * This script generates CSS files for Django integration and ensures
 * the design system is properly built for production use.
 */

const fs = require('fs');
const path = require('path');

// Import design system configuration (we'll use a simplified version for Node.js)
const designSystemConfig = {
  version: '1.0.0',
  name: 'FaktuLove Design System',
  
  // Simplified tokens for build process
  tokens: {
    colors: {
      primary: {
        50: '#eff6ff',
        100: '#dbeafe',
        200: '#bfdbfe',
        300: '#93c5fd',
        400: '#60a5fa',
        500: '#3b82f6',
        600: '#2563eb',
        700: '#1d4ed8',
        800: '#1e40af',
        900: '#1e3a8a',
      },
      neutral: {
        50: '#fafafa',
        100: '#f5f5f5',
        200: '#e5e5e5',
        300: '#d4d4d4',
        400: '#a3a3a3',
        500: '#737373',
        600: '#525252',
        700: '#404040',
        800: '#262626',
        900: '#171717',
      },
      success: {
        50: '#f0fdf4',
        100: '#dcfce7',
        200: '#bbf7d0',
        300: '#86efac',
        400: '#4ade80',
        500: '#22c55e',
        600: '#059669',
        700: '#15803d',
        800: '#166534',
        900: '#14532d',
      },
      warning: {
        50: '#fffbeb',
        100: '#fef3c7',
        200: '#fde68a',
        300: '#fcd34d',
        400: '#fbbf24',
        500: '#f59e0b',
        600: '#d97706',
        700: '#b45309',
        800: '#92400e',
        900: '#78350f',
      },
      error: {
        50: '#fef2f2',
        100: '#fee2e2',
        200: '#fecaca',
        300: '#fca5a5',
        400: '#f87171',
        500: '#ef4444',
        600: '#dc2626',
        700: '#b91c1c',
        800: '#991b1b',
        900: '#7f1d1d',
      },
    },
    spacing: {
      0: '0px',
      px: '1px',
      0.5: '0.125rem',
      1: '0.25rem',
      1.5: '0.375rem',
      2: '0.5rem',
      2.5: '0.625rem',
      3: '0.75rem',
      3.5: '0.875rem',
      4: '1rem',
      5: '1.25rem',
      6: '1.5rem',
      7: '1.75rem',
      8: '2rem',
      9: '2.25rem',
      10: '2.5rem',
      11: '2.75rem',
      12: '3rem',
      14: '3.5rem',
      16: '4rem',
      20: '5rem',
      24: '6rem',
      28: '7rem',
      32: '8rem',
      36: '9rem',
      40: '10rem',
      44: '11rem',
      48: '12rem',
      52: '13rem',
      56: '14rem',
      60: '15rem',
      64: '16rem',
      72: '18rem',
      80: '20rem',
      96: '24rem',
    },
    typography: {
      fontSize: {
        xs: '0.75rem',
        sm: '0.875rem',
        base: '1rem',
        lg: '1.125rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
        '3xl': '1.875rem',
        '4xl': '2.25rem',
        '5xl': '3rem',
        '6xl': '3.75rem',
      },
      fontWeight: {
        thin: 100,
        extralight: 200,
        light: 300,
        normal: 400,
        medium: 500,
        semibold: 600,
        bold: 700,
        extrabold: 800,
        black: 900,
      },
      lineHeight: {
        none: 1,
        tight: 1.25,
        snug: 1.375,
        normal: 1.5,
        relaxed: 1.625,
        loose: 2,
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', 'sans-serif'],
        serif: ['Georgia', 'Cambria', 'Times New Roman', 'Times', 'serif'],
        mono: ['Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
      },
    },
    shadows: {
      none: 'none',
      xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
      sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    },
    borderRadius: {
      none: '0px',
      xs: '0.125rem',
      sm: '0.25rem',
      md: '0.375rem',
      lg: '0.5rem',
      xl: '0.75rem',
      '2xl': '1rem',
      '3xl': '1.5rem',
      full: '9999px',
    },
  },
};

// Generate CSS custom properties
function generateCSSCustomProperties(config) {
  const cssVars = {};
  
  // Color tokens
  Object.entries(config.tokens.colors).forEach(([colorName, colorScale]) => {
    Object.entries(colorScale).forEach(([shade, value]) => {
      cssVars[`--color-${colorName}-${shade}`] = value;
    });
  });
  
  // Semantic colors (simplified)
  cssVars['--color-text-primary'] = 'var(--color-neutral-900)';
  cssVars['--color-text-secondary'] = 'var(--color-neutral-600)';
  cssVars['--color-text-muted'] = 'var(--color-neutral-500)';
  cssVars['--color-text-inverse'] = 'var(--color-neutral-50)';
  cssVars['--color-background-primary'] = 'var(--color-neutral-50)';
  cssVars['--color-background-secondary'] = 'var(--color-neutral-100)';
  cssVars['--color-background-muted'] = 'var(--color-neutral-200)';
  cssVars['--color-border-default'] = 'var(--color-neutral-200)';
  cssVars['--color-border-strong'] = 'var(--color-neutral-300)';
  cssVars['--color-interactive'] = 'var(--color-primary-600)';
  cssVars['--color-interactive-hover'] = 'var(--color-primary-700)';
  cssVars['--color-status-success'] = 'var(--color-success-600)';
  cssVars['--color-status-warning'] = 'var(--color-warning-600)';
  cssVars['--color-status-error'] = 'var(--color-error-600)';
  
  // Typography tokens
  Object.entries(config.tokens.typography.fontSize).forEach(([key, value]) => {
    cssVars[`--font-size-${key}`] = value;
  });
  
  Object.entries(config.tokens.typography.fontWeight).forEach(([key, value]) => {
    cssVars[`--font-weight-${key}`] = value.toString();
  });
  
  Object.entries(config.tokens.typography.lineHeight).forEach(([key, value]) => {
    cssVars[`--line-height-${key}`] = value.toString();
  });
  
  // Font families
  cssVars['--font-family-sans'] = config.tokens.typography.fontFamily.sans.join(', ');
  cssVars['--font-family-serif'] = config.tokens.typography.fontFamily.serif.join(', ');
  cssVars['--font-family-mono'] = config.tokens.typography.fontFamily.mono.join(', ');
  
  // Spacing tokens
  Object.entries(config.tokens.spacing).forEach(([key, value]) => {
    const cssKey = key.toString().replace('.', '_');
    cssVars[`--spacing-${cssKey.replace('_', '-')}`] = value;
  });
  
  // Shadow tokens
  Object.entries(config.tokens.shadows).forEach(([key, value]) => {
    cssVars[`--shadow-${key}`] = value;
  });
  
  // Border radius tokens
  Object.entries(config.tokens.borderRadius).forEach(([key, value]) => {
    cssVars[`--border-radius-${key}`] = value;
  });
  
  // Animation tokens
  cssVars['--animation-duration-fast'] = '150ms';
  cssVars['--animation-duration-normal'] = '300ms';
  cssVars['--animation-duration-slow'] = '500ms';
  cssVars['--animation-easing-ease'] = 'ease';
  cssVars['--animation-easing-ease-in'] = 'ease-in';
  cssVars['--animation-easing-ease-out'] = 'ease-out';
  cssVars['--animation-easing-ease-in-out'] = 'ease-in-out';
  
  // Focus rings
  cssVars['--focus-ring-default'] = '0 0 0 3px rgba(37, 99, 235, 0.1)';
  cssVars['--focus-ring-success'] = '0 0 0 3px rgba(5, 150, 105, 0.1)';
  cssVars['--focus-ring-warning'] = '0 0 0 3px rgba(217, 119, 6, 0.1)';
  cssVars['--focus-ring-error'] = '0 0 0 3px rgba(220, 38, 38, 0.1)';
  
  return cssVars;
}

// Generate CSS string
function generateCSSString(cssVars) {
  const cssRules = Object.entries(cssVars)
    .map(([property, value]) => `  ${property}: ${value};`)
    .join('\n');
  
  return `:root {\n${cssRules}\n}`;
}

// Generate Django integration CSS
function generateDjangoCSS(cssVars) {
  const baseCSS = generateCSSString(cssVars);
  
  const djangoSpecificCSS = `
/* Django Template Integration */
.django-design-system {
  font-family: var(--font-family-sans);
  color: var(--color-text-primary);
  background-color: var(--color-background-primary);
}

.django-design-system * {
  box-sizing: border-box;
}

/* Django form integration */
.django-design-system .form-control,
.django-design-system input,
.django-design-system select,
.django-design-system textarea {
  font-family: inherit;
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  color: var(--color-text-primary);
  background-color: var(--color-background-primary);
  border: 1px solid var(--color-border-default);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-2) var(--spacing-3);
  transition: all var(--animation-duration-fast) var(--animation-easing-ease-out);
}

.django-design-system .form-control:focus,
.django-design-system input:focus,
.django-design-system select:focus,
.django-design-system textarea:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  border-color: var(--color-interactive);
  box-shadow: var(--focus-ring-default);
}

/* Django button integration */
.django-design-system .btn,
.django-design-system button {
  font-family: inherit;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--animation-duration-fast) var(--animation-easing-ease-out);
}

.django-design-system .btn-primary {
  background-color: var(--color-interactive);
  color: var(--color-text-inverse);
  border-color: var(--color-interactive);
}

.django-design-system .btn-primary:hover {
  background-color: var(--color-interactive-hover);
  border-color: var(--color-interactive-hover);
}

.django-design-system .btn-primary:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  box-shadow: var(--focus-ring-default);
}

/* Polish business styling */
.django-design-system .currency {
  font-family: var(--font-family-mono);
  font-variant-numeric: tabular-nums;
  text-align: right;
}

.django-design-system .nip {
  font-family: var(--font-family-mono);
  letter-spacing: 0.05em;
}

.django-design-system .invoice-number {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-medium);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  :root {
    --color-text-primary: var(--color-neutral-50);
    --color-text-secondary: var(--color-neutral-300);
    --color-text-muted: var(--color-neutral-400);
    --color-text-inverse: var(--color-neutral-900);
    --color-background-primary: var(--color-neutral-900);
    --color-background-secondary: var(--color-neutral-800);
    --color-background-muted: var(--color-neutral-700);
    --color-border-default: var(--color-neutral-700);
    --color-border-strong: var(--color-neutral-600);
    --color-interactive: var(--color-primary-500);
    --color-interactive-hover: var(--color-primary-400);
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .django-design-system .form-control:focus,
  .django-design-system input:focus,
  .django-design-system select:focus,
  .django-design-system textarea:focus {
    outline: 2px solid var(--color-interactive);
    outline-offset: 2px;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .django-design-system * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
`;
  
  return baseCSS + djangoSpecificCSS;
}

// Main build function
function buildDesignSystem() {
  console.log('🎨 Building FaktuLove Design System...');
  
  try {
    // Generate CSS custom properties
    const cssVars = generateCSSCustomProperties(designSystemConfig);
    
    // Generate Django integration CSS
    const djangoCSS = generateDjangoCSS(cssVars);
    
    // Ensure output directories exist
    const outputDirs = [
      path.join(__dirname, '../build/static/css'),
      path.join(__dirname, '../../faktury/static/faktury/css'),
      path.join(__dirname, '../../static/css'),
    ];
    
    outputDirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
    
    // Write CSS files
    const cssFileName = 'design-system-integration.css';
    
    outputDirs.forEach(dir => {
      const filePath = path.join(dir, cssFileName);
      fs.writeFileSync(filePath, djangoCSS);
      console.log(`✅ Generated ${filePath}`);
    });
    
    // Generate build info
    const buildInfo = {
      version: designSystemConfig.version,
      name: designSystemConfig.name,
      buildTime: new Date().toISOString(),
      tokensCount: Object.keys(cssVars).length,
      files: outputDirs.map(dir => path.join(dir, cssFileName)),
    };
    
    // Write build info
    const buildInfoPath = path.join(__dirname, '../build/design-system-build-info.json');
    fs.writeFileSync(buildInfoPath, JSON.stringify(buildInfo, null, 2));
    
    console.log(`✅ Design system build complete!`);
    console.log(`   Version: ${buildInfo.version}`);
    console.log(`   Tokens: ${buildInfo.tokensCount}`);
    console.log(`   Files: ${buildInfo.files.length}`);
    
    return buildInfo;
    
  } catch (error) {
    console.error('❌ Design system build failed:', error);
    process.exit(1);
  }
}

// Run build if called directly
if (require.main === module) {
  buildDesignSystem();
}

module.exports = {
  buildDesignSystem,
  generateCSSCustomProperties,
  generateDjangoCSS,
  designSystemConfig,
};