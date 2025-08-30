/**
 * CSS Integration Utilities
 * 
 * Utilities for integrating design system CSS with Django templates
 * and ensuring consistent styling across the application.
 */

import { designSystemConfig } from '../config';

// CSS custom property generator
export const generateCSSCustomProperties = (config = designSystemConfig): Record<string, string> => {
  const cssVars: Record<string, string> = {};
  
  // Color tokens
  Object.entries(config.tokens.colors).forEach(([colorName, colorScale]) => {
    if (typeof colorScale === 'object') {
      Object.entries(colorScale).forEach(([shade, value]) => {
        cssVars[`--color-${colorName}-${shade}`] = value;
      });
    } else {
      cssVars[`--color-${colorName}`] = colorScale;
    }
  });
  
  // Semantic colors
  Object.entries(config.semantic.colors).forEach(([name, value]) => {
    const cssVarName = `--color-${name.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
    cssVars[cssVarName] = value;
  });
  
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
    cssVars[`--spacing-${key.replace('_', '-')}`] = value;
  });
  
  // Semantic spacing
  Object.entries(config.semantic.spacing).forEach(([key, value]) => {
    const cssVarName = `--spacing-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
    cssVars[cssVarName] = value;
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
  Object.entries(config.components.animations.duration).forEach(([key, value]) => {
    cssVars[`--animation-duration-${key}`] = value;
  });
  
  Object.entries(config.components.animations.easing).forEach(([key, value]) => {
    cssVars[`--animation-easing-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`] = value;
  });
  
  // Z-index tokens
  Object.entries(config.components.zIndex).forEach(([key, value]) => {
    cssVars[`--z-index-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`] = value.toString();
  });
  
  // Focus ring tokens
  Object.entries(config.components.focusRings).forEach(([key, value]) => {
    cssVars[`--focus-ring-${key}`] = value;
  });
  
  // Polish business specific tokens
  cssVars['--polish-currency-symbol'] = config.polish.currency.symbol;
  cssVars['--polish-currency-code'] = config.polish.currency.code;
  cssVars['--polish-date-format'] = config.polish.date.format;
  
  return cssVars;
};

// Apply CSS custom properties to document root
export const applyCSSCustomProperties = (cssVars: Record<string, string>): void => {
  if (typeof document === 'undefined') return;
  
  const root = document.documentElement;
  Object.entries(cssVars).forEach(([property, value]) => {
    root.style.setProperty(property, value);
  });
};

// Generate CSS string for server-side rendering
export const generateCSSString = (config = designSystemConfig): string => {
  const cssVars = generateCSSCustomProperties(config);
  const cssRules = Object.entries(cssVars)
    .map(([property, value]) => `  ${property}: ${value};`)
    .join('\n');
  
  return `:root {\n${cssRules}\n}`;
};

// CSS class utilities
export const cssClassUtils = {
  // Generate design system class names
  designSystemClass: (component: string, variant?: string, size?: string): string => {
    let className = `ds-${component}`;
    if (variant) className += ` ds-${component}--${variant}`;
    if (size) className += ` ds-${component}--${size}`;
    return className;
  },
  
  // Generate Polish business class names
  polishBusinessClass: (type: string, variant?: string): string => {
    let className = `polish-${type}`;
    if (variant) className += ` polish-${type}--${variant}`;
    return className;
  },
  
  // Generate theme class names
  themeClass: (theme: string): string => {
    return `theme-${theme}`;
  },
  
  // Generate responsive class names
  responsiveClass: (breakpoint: string, className: string): string => {
    return `${breakpoint}:${className}`;
  },
  
  // Generate state class names
  stateClass: (state: string, className: string): string => {
    return `${state}:${className}`;
  },
};

// CSS integration for Django templates
export const djangoCSSIntegration = {
  // Generate CSS for Django template inclusion
  generateDjangoCSS: (): string => {
    const baseCSS = generateCSSString();
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
`;
    
    return baseCSS + djangoSpecificCSS;
  },
  
  // Generate CSS file for Django static files
  generateStaticCSS: (): string => {
    return `/* FaktuLove Design System - Django Integration */
/* Auto-generated CSS file for Django templates */

${djangoCSSIntegration.generateDjangoCSS()}

/* Responsive design for Django templates */
@media (max-width: 768px) {
  .django-design-system .form-control,
  .django-design-system input,
  .django-design-system select,
  .django-design-system textarea {
    font-size: var(--font-size-base);
  }
  
  .django-design-system .btn {
    width: 100%;
    margin-bottom: var(--spacing-2);
  }
}

/* Print styles for Django templates */
@media print {
  .django-design-system {
    color: black;
    background: white;
  }
  
  .django-design-system .btn {
    display: none;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .django-design-system .form-control:focus,
  .django-design-system input:focus,
  .django-design-system select:focus,
  .django-design-system textarea:focus {
    outline: 2px solid var(--color-border-focus);
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
  },
};

// Theme integration utilities
export const themeIntegration = {
  // Apply theme to document
  applyTheme: (theme: 'light' | 'dark' | 'auto', contrast: 'normal' | 'high' = 'normal'): void => {
    if (typeof document === 'undefined') return;
    
    const root = document.documentElement;
    
    // Remove existing theme classes
    root.classList.remove('theme-light', 'theme-dark', 'theme-high-contrast');
    
    // Apply theme classes
    if (theme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
    } else {
      root.classList.add(`theme-${theme}`);
    }
    
    if (contrast === 'high') {
      root.classList.add('theme-high-contrast');
    }
    
    // Apply reduced motion if preferred
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      root.classList.add('theme-reduced-motion');
    }
  },
  
  // Get current theme
  getCurrentTheme: (): { theme: string; contrast: string; reducedMotion: boolean } => {
    if (typeof document === 'undefined') {
      return { theme: 'light', contrast: 'normal', reducedMotion: false };
    }
    
    const root = document.documentElement;
    const theme = root.classList.contains('theme-dark') ? 'dark' : 'light';
    const contrast = root.classList.contains('theme-high-contrast') ? 'high' : 'normal';
    const reducedMotion = root.classList.contains('theme-reduced-motion');
    
    return { theme, contrast, reducedMotion };
  },
};

// Export all utilities
export default {
  generateCSSCustomProperties,
  applyCSSCustomProperties,
  generateCSSString,
  cssClassUtils,
  djangoCSSIntegration,
  themeIntegration,
};