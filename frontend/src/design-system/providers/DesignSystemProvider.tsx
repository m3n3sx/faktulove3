import React, { createContext, useContext, ReactNode, useEffect } from 'react';
import { designSystemConfig } from '../config';
import { useTheme } from './ThemeProvider';

// Design System Context
interface DesignSystemContextValue {
  config: typeof designSystemConfig;
  utils: {
    // Component utilities
    getComponentSize: (size: 'xs' | 'sm' | 'md' | 'lg' | 'xl') => string;
    getSpacing: (key: string) => string;
    getColor: (path: string) => string;
    
    // Polish business utilities
    formatCurrency: (amount: number, currency?: string) => string;
    formatDate: (date: Date, format?: string) => string;
    validateNIP: (nip: string) => boolean;
    formatNIP: (nip: string) => string;
    
    // Accessibility utilities
    getAriaLabel: (key: string, params?: Record<string, any>) => string;
    announceToScreenReader: (message: string, priority?: 'polite' | 'assertive') => void;
  };
}

const DesignSystemContext = createContext<DesignSystemContextValue | undefined>(undefined);

// Provider props
interface DesignSystemProviderProps {
  children: ReactNode;
}

// Polish business utilities
const polishBusinessUtils = {
  formatCurrency: (amount: number, currency = 'PLN'): string => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  },
  
  formatDate: (date: Date, format = 'DD.MM.YYYY'): string => {
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    
    switch (format) {
      case 'DD.MM.YYYY':
        return `${day}.${month}.${year}`;
      case 'YYYY-MM-DD':
        return `${year}-${month}-${day}`;
      case 'DD MMMM YYYY':
        return date.toLocaleDateString('pl-PL', {
          day: 'numeric',
          month: 'long',
          year: 'numeric'
        });
      default:
        return date.toLocaleDateString('pl-PL');
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
};

// Accessibility utilities
const accessibilityUtils = {
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
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    // Remove the announcement after a short delay
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  },
};

// Design System Provider
export const DesignSystemProvider: React.FC<DesignSystemProviderProps> = ({ children }) => {
  const { theme } = useTheme();
  
  // Initialize design system on mount
  useEffect(() => {
    // Add design system class to document root
    document.documentElement.classList.add('design-system-initialized');
    
    // Set up design system meta information
    const metaDesignSystem = document.createElement('meta');
    metaDesignSystem.name = 'design-system';
    metaDesignSystem.content = `${designSystemConfig.name} v${designSystemConfig.version}`;
    document.head.appendChild(metaDesignSystem);
    
    // Initialize accessibility features
    if (designSystemConfig.accessibility.screenReader.announcements) {
      // Create live region for announcements
      const liveRegion = document.createElement('div');
      liveRegion.id = 'design-system-announcements';
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.className = 'sr-only';
      document.body.appendChild(liveRegion);
    }
    
    // Development warnings
    if (designSystemConfig.development.warnings && process.env.NODE_ENV === 'development') {
      console.log(`🎨 ${designSystemConfig.name} v${designSystemConfig.version} initialized`);
    }
    
    return () => {
      // Cleanup on unmount
      document.documentElement.classList.remove('design-system-initialized');
      const metaElement = document.querySelector('meta[name="design-system"]');
      if (metaElement) {
        document.head.removeChild(metaElement);
      }
      const liveRegion = document.getElementById('design-system-announcements');
      if (liveRegion) {
        document.body.removeChild(liveRegion);
      }
    };
  }, []);
  
  const utils = {
    // Component utilities
    getComponentSize: (size: 'xs' | 'sm' | 'md' | 'lg' | 'xl'): string => {
      const sizeMap = designSystemConfig.components.sizes;
      return sizeMap[size] || sizeMap.md;
    },
    
    getSpacing: (key: string): string => {
      return `var(--spacing-${key.replace('_', '-')})`;
    },
    
    getColor: (path: string): string => {
      const cssVarName = `--color-${path.replace(/\./g, '-').replace(/([A-Z])/g, '-$1').toLowerCase()}`;
      return `var(${cssVarName})`;
    },
    
    // Polish business utilities
    ...polishBusinessUtils,
    
    // Accessibility utilities
    ...accessibilityUtils,
  };
  
  const contextValue: DesignSystemContextValue = {
    config: designSystemConfig,
    utils,
  };
  
  return (
    <DesignSystemContext.Provider value={contextValue}>
      {children}
    </DesignSystemContext.Provider>
  );
};

// Hook to use design system context
export const useDesignSystem = (): DesignSystemContextValue => {
  const context = useContext(DesignSystemContext);
  if (context === undefined) {
    throw new Error('useDesignSystem must be used within a DesignSystemProvider');
  }
  return context;
};

// Utility hooks for common use cases
export const usePolishBusiness = () => {
  const { utils } = useDesignSystem();
  return {
    formatCurrency: utils.formatCurrency,
    formatDate: utils.formatDate,
    validateNIP: utils.validateNIP,
    formatNIP: utils.formatNIP,
  };
};

export const useAccessibility = () => {
  const { utils } = useDesignSystem();
  return {
    getAriaLabel: utils.getAriaLabel,
    announceToScreenReader: utils.announceToScreenReader,
  };
};

export default DesignSystemProvider;