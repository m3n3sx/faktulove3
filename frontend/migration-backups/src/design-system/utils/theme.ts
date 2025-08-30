// Theme Utilities
import { colors, semanticColors } from '../tokens/colors';
import { typography, typographyStyles } from '../tokens/typography';
import { spacing, semanticSpacing } from '../tokens/spacing';
import { breakpoints, mediaQueries } from '../tokens/breakpoints';
import { shadows, semanticShadows } from '../tokens/shadows';
import { borderRadius, semanticBorderRadius } from '../tokens/borderRadius';

// Complete design system theme object
export const theme = {
  colors,
  semanticColors,
  typography,
  typographyStyles,
  spacing,
  semanticSpacing,
  breakpoints,
  mediaQueries,
  shadows,
  semanticShadows,
  borderRadius,
  semanticBorderRadius,
} as const;

// Theme utility functions
export const getColor = (path: string, fallback?: string): string => {
  try {
    const keys = path.split('.');
    let value: any = colors;
    
    for (const key of keys) {
      value = value[key];
      if (value === undefined) {
        throw new Error(`Color path ${path} not found`);
      }
    }
    
    return value;
  } catch (error) {
    if (fallback) {
      console.warn(`Color ${path} not found, using fallback: ${fallback}`);
      return fallback;
    }
    throw error;
  }
};

export const getSpacing = (key: keyof typeof spacing): string => {
  return spacing[key];
};

export const getSemanticSpacing = (key: keyof typeof semanticSpacing): string => {
  return semanticSpacing[key];
};

export const getShadow = (key: keyof typeof shadows): string => {
  return shadows[key];
};

export const getSemanticShadow = (key: keyof typeof semanticShadows): string => {
  return semanticShadows[key];
};

export const getBorderRadius = (key: keyof typeof borderRadius): string => {
  return borderRadius[key];
};

export const getSemanticBorderRadius = (key: keyof typeof semanticBorderRadius): string => {
  return semanticBorderRadius[key];
};

// CSS custom properties generator for runtime theme switching
export const generateCSSCustomProperties = (isDark = false, isHighContrast = false) => {
  const cssVars: Record<string, string> = {};
  
  // Color variables
  Object.entries(colors).forEach(([colorName, colorScale]) => {
    Object.entries(colorScale).forEach(([shade, value]) => {
      cssVars[`--color-${colorName}-${shade}`] = value;
    });
  });
  
  // Semantic color variables with theme awareness
  if (isDark) {
    // Dark mode semantic color overrides
    cssVars['--color-text-primary'] = colors.neutral[50];
    cssVars['--color-text-secondary'] = colors.neutral[300];
    cssVars['--color-text-muted'] = colors.neutral[400];
    cssVars['--color-text-inverse'] = colors.neutral[900];
    cssVars['--color-background-primary'] = colors.neutral[900];
    cssVars['--color-background-secondary'] = colors.neutral[800];
    cssVars['--color-background-muted'] = colors.neutral[700];
    cssVars['--color-background-inverse'] = colors.neutral[50];
    cssVars['--color-border-default'] = colors.neutral[700];
    cssVars['--color-border-muted'] = colors.neutral[800];
    cssVars['--color-border-strong'] = colors.neutral[600];
  } else {
    // Light mode semantic colors
    Object.entries(semanticColors).forEach(([name, value]) => {
      cssVars[`--color-${name.replace(/([A-Z])/g, '-$1').toLowerCase()}`] = value;
    });
  }
  
  // High contrast overrides
  if (isHighContrast) {
    if (isDark) {
      cssVars['--color-text-primary'] = '#ffffff';
      cssVars['--color-text-secondary'] = '#ffffff';
      cssVars['--color-background-primary'] = '#000000';
      cssVars['--color-background-secondary'] = '#000000';
      cssVars['--color-border-default'] = '#ffffff';
    } else {
      cssVars['--color-text-primary'] = '#000000';
      cssVars['--color-text-secondary'] = '#000000';
      cssVars['--color-background-primary'] = '#ffffff';
      cssVars['--color-background-secondary'] = '#ffffff';
      cssVars['--color-border-default'] = '#000000';
    }
  }
  
  // Spacing variables
  Object.entries(spacing).forEach(([key, value]) => {
    cssVars[`--spacing-${key.replace('_', '-')}`] = value;
  });
  
  // Semantic spacing variables
  Object.entries(semanticSpacing).forEach(([key, value]) => {
    cssVars[`--spacing-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`] = value;
  });
  
  // Typography variables
  Object.entries(typography.fontSize).forEach(([key, value]) => {
    cssVars[`--font-size-${key}`] = value;
  });
  
  Object.entries(typography.fontWeight).forEach(([key, value]) => {
    cssVars[`--font-weight-${key}`] = value.toString();
  });
  
  Object.entries(typography.lineHeight).forEach(([key, value]) => {
    cssVars[`--line-height-${key}`] = value.toString();
  });
  
  // Shadow variables
  Object.entries(shadows).forEach(([key, value]) => {
    cssVars[`--shadow-${key}`] = value;
  });
  
  // Border radius variables
  Object.entries(borderRadius).forEach(([key, value]) => {
    cssVars[`--border-radius-${key}`] = value;
  });
  
  return cssVars;
};

// Apply CSS custom properties to document root
export const applyCSSCustomProperties = (cssVars: Record<string, string>) => {
  if (typeof document === 'undefined') return;
  
  const root = document.documentElement;
  Object.entries(cssVars).forEach(([property, value]) => {
    root.style.setProperty(property, value);
  });
};

// CSS custom property utilities
export const getCSSCustomProperty = (property: string, fallback?: string): string => {
  if (typeof document === 'undefined') return fallback || '';
  
  const value = getComputedStyle(document.documentElement).getPropertyValue(property);
  return value.trim() || fallback || '';
};

export const setCSSCustomProperty = (property: string, value: string): void => {
  if (typeof document === 'undefined') return;
  
  document.documentElement.style.setProperty(property, value);
};

export const removeCSSCustomProperty = (property: string): void => {
  if (typeof document === 'undefined') return;
  
  document.documentElement.style.removeProperty(property);
};

// Theme type definitions
export type Theme = typeof theme;
export type ColorPath = string;
export type SpacingKey = keyof typeof spacing;
export type SemanticSpacingKey = keyof typeof semanticSpacing;