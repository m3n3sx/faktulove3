import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { theme } from '../utils/theme';

// Theme types
export type ThemeMode = 'light' | 'dark' | 'auto';
export type ContrastMode = 'normal' | 'high';

export interface ThemeConfig {
  mode: ThemeMode;
  contrast: ContrastMode;
  reducedMotion: boolean;
}

export interface ThemeContextValue {
  config: ThemeConfig;
  setMode: (mode: ThemeMode) => void;
  setContrast: (contrast: ContrastMode) => void;
  setReducedMotion: (reducedMotion: boolean) => void;
  toggleMode: () => void;
  toggleContrast: () => void;
  theme: typeof theme;
  isDark: boolean;
  isHighContrast: boolean;
}

// Default theme configuration
const defaultConfig: ThemeConfig = {
  mode: 'auto',
  contrast: 'normal',
  reducedMotion: false,
};

// Theme context
const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

// Local storage keys
const STORAGE_KEYS = {
  MODE: 'faktulove-theme-mode',
  CONTRAST: 'faktulove-theme-contrast',
  REDUCED_MOTION: 'faktulove-theme-reduced-motion',
} as const;

// Theme provider props
export interface ThemeProviderProps {
  children: ReactNode;
  defaultMode?: ThemeMode;
  defaultContrast?: ContrastMode;
  defaultReducedMotion?: boolean;
}

// CSS custom properties generator
const generateCSSCustomProperties = (config: ThemeConfig, systemPrefersDark: boolean): Record<string, string> => {
  const cssVars: Record<string, string> = {};
  
  // Determine if we should use dark mode
  const isDark = config.mode === 'dark' || (config.mode === 'auto' && systemPrefersDark);
  
  // Base color tokens
  Object.entries(theme.colors).forEach(([colorName, colorScale]) => {
    Object.entries(colorScale).forEach(([shade, value]) => {
      cssVars[`--color-${colorName}-${shade}`] = value;
    });
  });
  
  // Semantic colors with theme-aware overrides
  if (isDark) {
    // Dark mode semantic color overrides
    cssVars['--color-text-primary'] = theme.colors.neutral[50];
    cssVars['--color-text-secondary'] = theme.colors.neutral[300];
    cssVars['--color-text-muted'] = theme.colors.neutral[400];
    cssVars['--color-text-inverse'] = theme.colors.neutral[900];
    cssVars['--color-text-disabled'] = theme.colors.neutral[500];
    cssVars['--color-text-placeholder'] = theme.colors.neutral[500];
    
    cssVars['--color-background-primary'] = theme.colors.neutral[900];
    cssVars['--color-background-secondary'] = theme.colors.neutral[800];
    cssVars['--color-background-muted'] = theme.colors.neutral[700];
    cssVars['--color-background-inverse'] = theme.colors.neutral[50];
    cssVars['--color-background-disabled'] = theme.colors.neutral[800];
    cssVars['--color-background-hover'] = theme.colors.neutral[800];
    cssVars['--color-background-pressed'] = theme.colors.neutral[700];
    
    cssVars['--color-border-default'] = theme.colors.neutral[700];
    cssVars['--color-border-muted'] = theme.colors.neutral[800];
    cssVars['--color-border-strong'] = theme.colors.neutral[600];
    
    // Adjust interactive colors for dark mode
    cssVars['--color-interactive'] = theme.colors.primary[500];
    cssVars['--color-interactive-hover'] = theme.colors.primary[400];
    cssVars['--color-interactive-active'] = theme.colors.primary[600];
    cssVars['--color-interactive-disabled'] = theme.colors.neutral[600];
    
    // Status colors with dark backgrounds
    cssVars['--color-status-success-background'] = theme.colors.success[900];
    cssVars['--color-status-warning-background'] = theme.colors.warning[900];
    cssVars['--color-status-error-background'] = theme.colors.error[900];
    cssVars['--color-status-info-background'] = theme.colors.primary[900];
    
    // Invoice status colors for dark mode
    cssVars['--color-invoice-draft-background'] = theme.colors.neutral[800];
    cssVars['--color-invoice-sent-background'] = theme.colors.primary[900];
    cssVars['--color-invoice-paid-background'] = theme.colors.success[900];
    cssVars['--color-invoice-overdue-background'] = theme.colors.error[900];
    cssVars['--color-invoice-cancelled-background'] = theme.colors.neutral[800];
  } else {
    // Light mode semantic colors (default)
    Object.entries(theme.semanticColors).forEach(([name, value]) => {
      const cssVarName = `--color-${name.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
      cssVars[cssVarName] = value;
    });
  }
  
  // High contrast mode overrides
  if (config.contrast === 'high') {
    if (isDark) {
      cssVars['--color-text-primary'] = '#ffffff';
      cssVars['--color-text-secondary'] = '#ffffff';
      cssVars['--color-background-primary'] = '#000000';
      cssVars['--color-background-secondary'] = '#000000';
      cssVars['--color-border-default'] = '#ffffff';
      cssVars['--color-border-strong'] = '#ffffff';
    } else {
      cssVars['--color-text-primary'] = '#000000';
      cssVars['--color-text-secondary'] = '#000000';
      cssVars['--color-background-primary'] = '#ffffff';
      cssVars['--color-background-secondary'] = '#ffffff';
      cssVars['--color-border-default'] = '#000000';
      cssVars['--color-border-strong'] = '#000000';
    }
    
    // Enhanced focus rings for high contrast
    cssVars['--focus-ring-default'] = '0 0 0 3px #ffff00';
    cssVars['--focus-ring-success'] = '0 0 0 3px #00ff00';
    cssVars['--focus-ring-warning'] = '0 0 0 3px #ffaa00';
    cssVars['--focus-ring-error'] = '0 0 0 3px #ff0000';
  }
  
  // Typography tokens
  Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
    cssVars[`--font-size-${key}`] = value;
  });
  
  Object.entries(theme.typography.fontWeight).forEach(([key, value]) => {
    cssVars[`--font-weight-${key}`] = value.toString();
  });
  
  Object.entries(theme.typography.lineHeight).forEach(([key, value]) => {
    cssVars[`--line-height-${key}`] = value.toString();
  });
  
  // Spacing tokens
  Object.entries(theme.spacing).forEach(([key, value]) => {
    cssVars[`--spacing-${key.replace('_', '-')}`] = value;
  });
  
  Object.entries(theme.semanticSpacing).forEach(([key, value]) => {
    const cssVarName = `--spacing-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
    cssVars[cssVarName] = value;
  });
  
  // Shadow tokens
  Object.entries(theme.shadows).forEach(([key, value]) => {
    cssVars[`--shadow-${key}`] = value;
  });
  
  // Border radius tokens
  Object.entries(theme.borderRadius).forEach(([key, value]) => {
    cssVars[`--border-radius-${key}`] = value;
  });
  
  // Animation duration overrides for reduced motion
  if (config.reducedMotion) {
    cssVars['--animation-duration-fast'] = '0ms';
    cssVars['--animation-duration-normal'] = '0ms';
    cssVars['--animation-duration-slow'] = '0ms';
  } else {
    cssVars['--animation-duration-fast'] = '150ms';
    cssVars['--animation-duration-normal'] = '300ms';
    cssVars['--animation-duration-slow'] = '500ms';
  }
  
  return cssVars;
};

// Apply CSS custom properties to document root
const applyCSSCustomProperties = (cssVars: Record<string, string>) => {
  const root = document.documentElement;
  Object.entries(cssVars).forEach(([property, value]) => {
    root.style.setProperty(property, value);
  });
};

// Theme provider component
export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultMode = 'auto',
  defaultContrast = 'normal',
  defaultReducedMotion = false,
}) => {
  // Load initial config from localStorage or defaults
  const [config, setConfig] = useState<ThemeConfig>(() => {
    if (typeof window === 'undefined') {
      return { mode: defaultMode, contrast: defaultContrast, reducedMotion: defaultReducedMotion };
    }
    
    const savedMode = localStorage.getItem(STORAGE_KEYS.MODE) as ThemeMode;
    const savedContrast = localStorage.getItem(STORAGE_KEYS.CONTRAST) as ContrastMode;
    const savedReducedMotion = localStorage.getItem(STORAGE_KEYS.REDUCED_MOTION) === 'true';
    
    return {
      mode: savedMode || defaultMode,
      contrast: savedContrast || defaultContrast,
      reducedMotion: savedReducedMotion || defaultReducedMotion,
    };
  });
  
  // Track system preferences
  const [systemPrefersDark, setSystemPrefersDark] = useState(false);
  const [systemPrefersHighContrast, setSystemPrefersHighContrast] = useState(false);
  const [systemPrefersReducedMotion, setSystemPrefersReducedMotion] = useState(false);
  
  // Detect system preferences
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    setSystemPrefersDark(darkModeQuery.matches);
    setSystemPrefersHighContrast(highContrastQuery.matches);
    setSystemPrefersReducedMotion(reducedMotionQuery.matches);
    
    const handleDarkModeChange = (e: MediaQueryListEvent) => setSystemPrefersDark(e.matches);
    const handleHighContrastChange = (e: MediaQueryListEvent) => setSystemPrefersHighContrast(e.matches);
    const handleReducedMotionChange = (e: MediaQueryListEvent) => setSystemPrefersReducedMotion(e.matches);
    
    darkModeQuery.addEventListener('change', handleDarkModeChange);
    highContrastQuery.addEventListener('change', handleHighContrastChange);
    reducedMotionQuery.addEventListener('change', handleReducedMotionChange);
    
    return () => {
      darkModeQuery.removeEventListener('change', handleDarkModeChange);
      highContrastQuery.removeEventListener('change', handleHighContrastChange);
      reducedMotionQuery.removeEventListener('change', handleReducedMotionChange);
    };
  }, []);
  
  // Apply theme changes
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const effectiveConfig = {
      ...config,
      // Auto-detect system preferences when in auto mode
      contrast: config.contrast === 'normal' && systemPrefersHighContrast ? 'high' : config.contrast,
      reducedMotion: config.reducedMotion || systemPrefersReducedMotion,
    };
    
    const cssVars = generateCSSCustomProperties(effectiveConfig, systemPrefersDark);
    applyCSSCustomProperties(cssVars);
    
    // Update document classes for CSS selectors
    const root = document.documentElement;
    const isDark = config.mode === 'dark' || (config.mode === 'auto' && systemPrefersDark);
    
    root.classList.toggle('theme-dark', isDark);
    root.classList.toggle('theme-light', !isDark);
    root.classList.toggle('theme-high-contrast', effectiveConfig.contrast === 'high');
    root.classList.toggle('theme-reduced-motion', effectiveConfig.reducedMotion);
    
    // Set color-scheme for browser UI
    root.style.colorScheme = isDark ? 'dark' : 'light';
  }, [config, systemPrefersDark, systemPrefersHighContrast, systemPrefersReducedMotion]);
  
  // Theme control functions
  const setMode = (mode: ThemeMode) => {
    setConfig(prev => ({ ...prev, mode }));
    localStorage.setItem(STORAGE_KEYS.MODE, mode);
  };
  
  const setContrast = (contrast: ContrastMode) => {
    setConfig(prev => ({ ...prev, contrast }));
    localStorage.setItem(STORAGE_KEYS.CONTRAST, contrast);
  };
  
  const setReducedMotion = (reducedMotion: boolean) => {
    setConfig(prev => ({ ...prev, reducedMotion }));
    localStorage.setItem(STORAGE_KEYS.REDUCED_MOTION, reducedMotion.toString());
  };
  
  const toggleMode = () => {
    const newMode = config.mode === 'light' ? 'dark' : config.mode === 'dark' ? 'auto' : 'light';
    setMode(newMode);
  };
  
  const toggleContrast = () => {
    setContrast(config.contrast === 'normal' ? 'high' : 'normal');
  };
  
  // Computed values
  const isDark = config.mode === 'dark' || (config.mode === 'auto' && systemPrefersDark);
  const isHighContrast = config.contrast === 'high' || (config.contrast === 'normal' && systemPrefersHighContrast);
  
  const contextValue: ThemeContextValue = {
    config,
    setMode,
    setContrast,
    setReducedMotion,
    toggleMode,
    toggleContrast,
    theme,
    isDark,
    isHighContrast,
  };
  
  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

// Theme hook
export const useTheme = (): ThemeContextValue => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Theme utilities hook
export const useThemeUtils = () => {
  const { theme, isDark, isHighContrast } = useTheme();
  
  return {
    // Color utilities
    getColor: (path: string, fallback?: string): string => {
      try {
        const keys = path.split('.');
        let value: any = theme.colors;
        
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
    },
    
    // Semantic color utilities
    getSemanticColor: (key: keyof typeof theme.semanticColors): string => {
      return theme.semanticColors[key];
    },
    
    // Theme-aware color selection
    getThemeAwareColor: (lightColor: string, darkColor: string): string => {
      return isDark ? darkColor : lightColor;
    },
    
    // Contrast-aware color selection
    getContrastAwareColor: (normalColor: string, highContrastColor: string): string => {
      return isHighContrast ? highContrastColor : normalColor;
    },
    
    // Polish business color utilities
    getInvoiceStatusColor: (status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled') => {
      const colorMap = {
        draft: 'var(--color-invoice-draft)',
        sent: 'var(--color-invoice-sent)',
        paid: 'var(--color-invoice-paid)',
        overdue: 'var(--color-invoice-overdue)',
        cancelled: 'var(--color-invoice-cancelled)',
      };
      return colorMap[status];
    },
    
    getInvoiceStatusBackground: (status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled') => {
      const colorMap = {
        draft: 'var(--color-invoice-draft-background)',
        sent: 'var(--color-invoice-sent-background)',
        paid: 'var(--color-invoice-paid-background)',
        overdue: 'var(--color-invoice-overdue-background)',
        cancelled: 'var(--color-invoice-cancelled-background)',
      };
      return colorMap[status];
    },
    
    // Spacing utilities
    getSpacing: (key: keyof typeof theme.spacing): string => {
      return theme.spacing[key];
    },
    
    getSemanticSpacing: (key: keyof typeof theme.semanticSpacing): string => {
      return theme.semanticSpacing[key];
    },
    
    // Typography utilities
    getFontSize: (key: keyof typeof theme.typography.fontSize): string => {
      return theme.typography.fontSize[key];
    },
    
    getFontWeight: (key: keyof typeof theme.typography.fontWeight): number => {
      return theme.typography.fontWeight[key];
    },
    
    // Shadow utilities
    getShadow: (key: keyof typeof theme.shadows): string => {
      return theme.shadows[key];
    },
    
    // Border radius utilities
    getBorderRadius: (key: keyof typeof theme.borderRadius): string => {
      return theme.borderRadius[key];
    },
    
    // Theme state
    isDark,
    isHighContrast,
  };
};

// CSS-in-JS theme object for styled-components or emotion
export const createStyledTheme = (themeConfig: ThemeConfig, systemPrefersDark: boolean) => {
  const isDark = themeConfig.mode === 'dark' || (themeConfig.mode === 'auto' && systemPrefersDark);
  const isHighContrast = themeConfig.contrast === 'high';
  
  return {
    ...theme,
    mode: themeConfig.mode,
    contrast: themeConfig.contrast,
    reducedMotion: themeConfig.reducedMotion,
    isDark,
    isHighContrast,
    
    // Theme-aware semantic colors
    semanticColors: {
      ...theme.semanticColors,
      // Override with dark mode colors if needed
      ...(isDark && {
        textPrimary: theme.colors.neutral[50],
        textSecondary: theme.colors.neutral[300],
        backgroundPrimary: theme.colors.neutral[900],
        backgroundSecondary: theme.colors.neutral[800],
        borderDefault: theme.colors.neutral[700],
      }),
      
      // Override with high contrast colors if needed
      ...(isHighContrast && {
        textPrimary: isDark ? '#ffffff' : '#000000',
        textSecondary: isDark ? '#ffffff' : '#000000',
        backgroundPrimary: isDark ? '#000000' : '#ffffff',
        borderDefault: isDark ? '#ffffff' : '#000000',
      }),
    },
  };
};

export default ThemeProvider;