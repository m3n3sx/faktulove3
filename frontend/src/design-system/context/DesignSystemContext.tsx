import React, { createContext, useContext, ReactNode } from 'react';
import { designSystemConfig, DesignSystemConfig } from '../config';

// Design System Context Interface
export interface DesignSystemContextValue {
  config: DesignSystemConfig;
  
  // Utility functions
  getToken: (path: string, fallback?: any) => any;
  getColor: (colorPath: string) => string;
  getSpacing: (spacingKey: string) => string;
  getTypography: (typographyKey: string) => any;
  getBreakpoint: (breakpointKey: string) => string;
  getShadow: (shadowKey: string) => string;
  getBorderRadius: (radiusKey: string) => string;
  
  // Component utilities
  getComponentSize: (size: 'xs' | 'sm' | 'md' | 'lg' | 'xl') => string;
  getComponentVariant: (component: string, variant: string) => any;
  
  // Polish business utilities
  formatCurrency: (amount: number, options?: Intl.NumberFormatOptions) => string;
  formatDate: (date: Date, format?: string) => string;
  validateNIP: (nip: string) => boolean;
  formatNIP: (nip: string) => string;
  getVATRate: (rate: number) => { value: number; label: string } | undefined;
  getInvoiceStatus: (status: string) => { label: string; color: string } | undefined;
  
  // Accessibility utilities
  getAriaLabel: (key: string, params?: Record<string, any>) => string;
  announceToScreenReader: (message: string, priority?: 'polite' | 'assertive') => void;
  getFocusRing: (variant?: 'default' | 'success' | 'warning' | 'error') => string;
  
  // Responsive utilities
  getMediaQuery: (breakpoint: string) => string;
  isBreakpointActive: (breakpoint: string) => boolean;
  
  // Theme utilities
  isDarkMode: () => boolean;
  isHighContrast: () => boolean;
  isReducedMotion: () => boolean;
}

// Create context
const DesignSystemContext = createContext<DesignSystemContextValue | undefined>(undefined);

// Provider props
interface DesignSystemContextProviderProps {
  children: ReactNode;
}

// Utility function to get nested object value by path
const getNestedValue = (obj: any, path: string, fallback?: any): any => {
  try {
    const keys = path.split('.');
    let value = obj;
    
    for (const key of keys) {
      value = value[key];
      if (value === undefined) {
        throw new Error(`Path ${path} not found`);
      }
    }
    
    return value;
  } catch (error) {
    if (fallback !== undefined) {
      if (designSystemConfig.development.warnings) {
        console.warn(`Design system path ${path} not found, using fallback:`, fallback);
      }
      return fallback;
    }
    throw error;
  }
};

// Polish business utilities
const createPolishBusinessUtils = () => ({
  formatCurrency: (amount: number, options?: Intl.NumberFormatOptions): string => {
    const defaultOptions = {
      style: 'currency',
      currency: designSystemConfig.polish.currency.code,
      minimumFractionDigits: designSystemConfig.polish.currency.decimalPlaces,
      maximumFractionDigits: designSystemConfig.polish.currency.decimalPlaces,
    };
    
    return new Intl.NumberFormat(
      designSystemConfig.polish.currency.locale,
      { ...defaultOptions, ...options }
    ).format(amount);
  },
  
  formatDate: (date: Date, format?: string): string => {
    const formatType = format || designSystemConfig.polish.date.format;
    
    switch (formatType) {
      case 'DD.MM.YYYY':
        return date.toLocaleDateString(designSystemConfig.polish.date.locale, {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        });
      case 'DD MMMM YYYY':
        return date.toLocaleDateString(designSystemConfig.polish.date.locale, {
          day: 'numeric',
          month: 'long',
          year: 'numeric'
        });
      case 'YYYY-MM-DD':
        return date.toISOString().split('T')[0];
      default:
        return date.toLocaleDateString(designSystemConfig.polish.date.locale);
    }
  },
  
  validateNIP: (nip: string): boolean => {
    // Remove all non-digit characters
    const cleanNip = nip.replace(/\D/g, '');
    
    // Check if NIP has exactly 10 digits
    if (cleanNip.length !== 10) {
      return false;
    }
    
    // Calculate checksum
    const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
    let sum = 0;
    
    for (let i = 0; i < 9; i++) {
      sum += parseInt(cleanNip[i]) * weights[i];
    }
    
    const checksum = sum % 11;
    const lastDigit = parseInt(cleanNip[9]);
    
    return checksum === lastDigit;
  },
  
  formatNIP: (nip: string): string => {
    const cleanNip = nip.replace(/\D/g, '');
    if (cleanNip.length === 10) {
      return `${cleanNip.slice(0, 3)}-${cleanNip.slice(3, 6)}-${cleanNip.slice(6, 8)}-${cleanNip.slice(8, 10)}`;
    }
    return nip;
  },
  
  getVATRate: (rate: number) => {
    return designSystemConfig.polish.vatRates.find(vat => vat.value === rate);
  },
  
  getInvoiceStatus: (status: string) => {
    return designSystemConfig.polish.invoiceStatuses[status as keyof typeof designSystemConfig.polish.invoiceStatuses];
  },
});

// Accessibility utilities
const createAccessibilityUtils = () => ({
  getAriaLabel: (key: string, params?: Record<string, any>): string => {
    const labels: Record<string, string> = {
      'invoice.create': 'Utwórz nową fakturę',
      'invoice.edit': 'Edytuj fakturę {number}',
      'invoice.delete': 'Usuń fakturę {number}',
      'invoice.status': 'Status faktury: {status}',
      'currency.amount': 'Kwota: {amount} złotych',
      'date.picker': 'Wybierz datę',
      'nip.input': 'Wprowadź numer NIP',
      'vat.rate': 'Stawka VAT: {rate} procent',
      'file.upload': 'Prześlij plik',
      'ocr.processing': 'Przetwarzanie dokumentu OCR',
      'ocr.confidence': 'Pewność rozpoznania: {confidence} procent',
      'navigation.main': 'Menu główne',
      'navigation.breadcrumb': 'Ścieżka nawigacji',
      'form.required': 'Pole wymagane',
      'form.error': 'Błąd walidacji: {error}',
      'table.sort': 'Sortuj według {column}',
      'modal.close': 'Zamknij okno dialogowe',
      'theme.toggle': 'Przełącz motyw',
      'language.select': 'Wybierz język',
    };
    
    let label = labels[key] || key;
    
    if (params) {
      Object.entries(params).forEach(([param, value]) => {
        label = label.replace(`{${param}}`, String(value));
      });
    }
    
    return label;
  },
  
  announceToScreenReader: (message: string, priority: 'polite' | 'assertive' = 'polite'): void => {
    const liveRegion = document.getElementById('design-system-announcements');
    if (liveRegion) {
      liveRegion.setAttribute('aria-live', priority);
      liveRegion.textContent = message;
      
      // Clear after announcement
      setTimeout(() => {
        liveRegion.textContent = '';
      }, 1000);
    }
  },
  
  getFocusRing: (variant: 'default' | 'success' | 'warning' | 'error' = 'default'): string => {
    const focusRings = designSystemConfig.components.focusRings;
    return focusRings[variant] || focusRings.default;
  },
});

// Responsive utilities
const createResponsiveUtils = () => ({
  getMediaQuery: (breakpoint: string): string => {
    const breakpoints = designSystemConfig.responsive.breakpoints;
    const value = breakpoints[breakpoint as keyof typeof breakpoints];
    return value ? `(min-width: ${value})` : '';
  },
  
  isBreakpointActive: (breakpoint: string): boolean => {
    if (typeof window === 'undefined') return false;
    
    const mediaQuery = createResponsiveUtils().getMediaQuery(breakpoint);
    return mediaQuery ? window.matchMedia(mediaQuery).matches : false;
  },
});

// Theme utilities
const createThemeUtils = () => ({
  isDarkMode: (): boolean => {
    if (typeof window === 'undefined') return false;
    return document.documentElement.classList.contains('theme-dark');
  },
  
  isHighContrast: (): boolean => {
    if (typeof window === 'undefined') return false;
    return document.documentElement.classList.contains('theme-high-contrast');
  },
  
  isReducedMotion: (): boolean => {
    if (typeof window === 'undefined') return false;
    return document.documentElement.classList.contains('theme-reduced-motion');
  },
});

// Context Provider
export const DesignSystemContextProvider: React.FC<DesignSystemContextProviderProps> = ({ children }) => {
  const polishUtils = createPolishBusinessUtils();
  const a11yUtils = createAccessibilityUtils();
  const responsiveUtils = createResponsiveUtils();
  const themeUtils = createThemeUtils();
  
  const contextValue: DesignSystemContextValue = {
    config: designSystemConfig,
    
    // Token utilities
    getToken: (path: string, fallback?: any) => getNestedValue(designSystemConfig, path, fallback),
    
    getColor: (colorPath: string): string => {
      const cssVarName = `--color-${colorPath.replace(/\./g, '-').replace(/([A-Z])/g, '-$1').toLowerCase()}`;
      return `var(${cssVarName})`;
    },
    
    getSpacing: (spacingKey: string): string => {
      return `var(--spacing-${spacingKey.replace('_', '-')})`;
    },
    
    getTypography: (typographyKey: string): any => {
      return getNestedValue(designSystemConfig.tokens.typography, typographyKey);
    },
    
    getBreakpoint: (breakpointKey: string): string => {
      return getNestedValue(designSystemConfig.tokens.breakpoints, breakpointKey);
    },
    
    getShadow: (shadowKey: string): string => {
      return `var(--shadow-${shadowKey})`;
    },
    
    getBorderRadius: (radiusKey: string): string => {
      return `var(--border-radius-${radiusKey})`;
    },
    
    // Component utilities
    getComponentSize: (size: 'xs' | 'sm' | 'md' | 'lg' | 'xl'): string => {
      const sizes = designSystemConfig.components.sizes;
      return sizes[size] || sizes.md;
    },
    
    getComponentVariant: (component: string, variant: string): any => {
      return getNestedValue(designSystemConfig.components, `${component}.${variant}`);
    },
    
    // Polish business utilities
    ...polishUtils,
    
    // Accessibility utilities
    ...a11yUtils,
    
    // Responsive utilities
    ...responsiveUtils,
    
    // Theme utilities
    ...themeUtils,
  };
  
  return (
    <DesignSystemContext.Provider value={contextValue}>
      {children}
    </DesignSystemContext.Provider>
  );
};

// Hook to use design system context
export const useDesignSystemContext = (): DesignSystemContextValue => {
  const context = useContext(DesignSystemContext);
  if (context === undefined) {
    throw new Error('useDesignSystemContext must be used within a DesignSystemContextProvider');
  }
  return context;
};

// Convenience hooks for specific utilities
export const useDesignSystemTokens = () => {
  const { getToken, getColor, getSpacing, getTypography, getBreakpoint, getShadow, getBorderRadius } = useDesignSystemContext();
  return { getToken, getColor, getSpacing, getTypography, getBreakpoint, getShadow, getBorderRadius };
};

export const usePolishBusinessUtils = () => {
  const { formatCurrency, formatDate, validateNIP, formatNIP, getVATRate, getInvoiceStatus } = useDesignSystemContext();
  return { formatCurrency, formatDate, validateNIP, formatNIP, getVATRate, getInvoiceStatus };
};

export const useAccessibilityUtils = () => {
  const { getAriaLabel, announceToScreenReader, getFocusRing } = useDesignSystemContext();
  return { getAriaLabel, announceToScreenReader, getFocusRing };
};

export const useResponsiveUtils = () => {
  const { getMediaQuery, isBreakpointActive } = useDesignSystemContext();
  return { getMediaQuery, isBreakpointActive };
};

export const useThemeUtils = () => {
  const { isDarkMode, isHighContrast, isReducedMotion } = useDesignSystemContext();
  return { isDarkMode, isHighContrast, isReducedMotion };
};

export default DesignSystemContext;