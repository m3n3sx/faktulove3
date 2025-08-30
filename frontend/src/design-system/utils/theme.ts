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

// Polish business theme configuration
export const polishBusinessTheme = {
  // Polish business color schemes
  colors: {
    // Invoice status colors
    invoice: {
      draft: { light: colors.neutral[500], dark: colors.neutral[400] },
      sent: { light: colors.primary[600], dark: colors.primary[400] },
      paid: { light: colors.success[600], dark: colors.success[400] },
      overdue: { light: colors.error[600], dark: colors.error[400] },
      cancelled: { light: colors.neutral[400], dark: colors.neutral[500] },
    },
    
    // VAT rate colors
    vat: {
      standard: { light: colors.primary[600], dark: colors.primary[400] },
      reduced: { light: colors.warning[600], dark: colors.warning[400] },
      zero: { light: colors.neutral[500], dark: colors.neutral[400] },
      exempt: { light: colors.primary[600], dark: colors.primary[400] },
    },
    
    // Compliance colors
    compliance: {
      compliant: { light: colors.success[600], dark: colors.success[400] },
      warning: { light: colors.warning[600], dark: colors.warning[400] },
      error: { light: colors.error[600], dark: colors.error[400] },
      pending: { light: colors.primary[600], dark: colors.primary[400] },
    },
    
    // Polish flag colors for special occasions
    poland: {
      white: '#ffffff',
      red: '#dc143c',
    },
  },
  
  // Polish business typography
  typography: {
    // Currency formatting
    currency: {
      fontFamily: 'var(--font-family-mono)',
      fontWeight: 'var(--font-weight-semibold)',
      fontSize: 'var(--font-size-base)',
    },
    
    // NIP/REGON formatting
    businessNumber: {
      fontFamily: 'var(--font-family-mono)',
      fontWeight: 'var(--font-weight-medium)',
      fontSize: 'var(--font-size-sm)',
    },
    
    // Invoice number formatting
    invoiceNumber: {
      fontFamily: 'var(--font-family-mono)',
      fontWeight: 'var(--font-weight-bold)',
      fontSize: 'var(--font-size-lg)',
    },
  },
  
  // Polish business spacing
  spacing: {
    invoiceSection: 'var(--spacing-6)',
    formGroup: 'var(--spacing-4)',
    businessCard: 'var(--spacing-5)',
  },
} as const;

// CSS custom properties generator for runtime theme switching
export const generateCSSCustomProperties = (isDark = false, isHighContrast = false) => {
  const cssVars: Record<string, string> = {};
  
  // Color variables
  Object.entries(colors).forEach(([colorName, colorScale]) => {
    Object.entries(colorScale).forEach(([shade, value]) => {
      cssVars[`--color-${colorName}-${shade}`] = value as string;
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
    
    // Polish business colors for dark mode
    cssVars['--color-invoice-draft'] = polishBusinessTheme.colors.invoice.draft.dark;
    cssVars['--color-invoice-sent'] = polishBusinessTheme.colors.invoice.sent.dark;
    cssVars['--color-invoice-paid'] = polishBusinessTheme.colors.invoice.paid.dark;
    cssVars['--color-invoice-overdue'] = polishBusinessTheme.colors.invoice.overdue.dark;
    cssVars['--color-invoice-cancelled'] = polishBusinessTheme.colors.invoice.cancelled.dark;
    
    cssVars['--color-vat-standard'] = polishBusinessTheme.colors.vat.standard.dark;
    cssVars['--color-vat-reduced'] = polishBusinessTheme.colors.vat.reduced.dark;
    cssVars['--color-vat-zero'] = polishBusinessTheme.colors.vat.zero.dark;
    cssVars['--color-vat-exempt'] = polishBusinessTheme.colors.vat.exempt.dark;
    
    cssVars['--color-compliance-compliant'] = polishBusinessTheme.colors.compliance.compliant.dark;
    cssVars['--color-compliance-warning'] = polishBusinessTheme.colors.compliance.warning.dark;
    cssVars['--color-compliance-error'] = polishBusinessTheme.colors.compliance.error.dark;
    cssVars['--color-compliance-pending'] = polishBusinessTheme.colors.compliance.pending.dark;
  } else {
    // Light mode semantic colors
    Object.entries(semanticColors).forEach(([name, value]) => {
      cssVars[`--color-${name.replace(/([A-Z])/g, '-$1').toLowerCase()}`] = value;
    });
    
    // Polish business colors for light mode
    cssVars['--color-invoice-draft'] = polishBusinessTheme.colors.invoice.draft.light;
    cssVars['--color-invoice-sent'] = polishBusinessTheme.colors.invoice.sent.light;
    cssVars['--color-invoice-paid'] = polishBusinessTheme.colors.invoice.paid.light;
    cssVars['--color-invoice-overdue'] = polishBusinessTheme.colors.invoice.overdue.light;
    cssVars['--color-invoice-cancelled'] = polishBusinessTheme.colors.invoice.cancelled.light;
    
    cssVars['--color-vat-standard'] = polishBusinessTheme.colors.vat.standard.light;
    cssVars['--color-vat-reduced'] = polishBusinessTheme.colors.vat.reduced.light;
    cssVars['--color-vat-zero'] = polishBusinessTheme.colors.vat.zero.light;
    cssVars['--color-vat-exempt'] = polishBusinessTheme.colors.vat.exempt.light;
    
    cssVars['--color-compliance-compliant'] = polishBusinessTheme.colors.compliance.compliant.light;
    cssVars['--color-compliance-warning'] = polishBusinessTheme.colors.compliance.warning.light;
    cssVars['--color-compliance-error'] = polishBusinessTheme.colors.compliance.error.light;
    cssVars['--color-compliance-pending'] = polishBusinessTheme.colors.compliance.pending.light;
  }
  
  // High contrast overrides
  if (isHighContrast) {
    if (isDark) {
      cssVars['--color-text-primary'] = '#ffffff';
      cssVars['--color-text-secondary'] = '#ffffff';
      cssVars['--color-background-primary'] = '#000000';
      cssVars['--color-background-secondary'] = '#000000';
      cssVars['--color-border-default'] = '#ffffff';
      
      // High contrast Polish business colors for dark mode
      cssVars['--color-invoice-paid'] = '#00ff00';
      cssVars['--color-invoice-overdue'] = '#ff0000';
      cssVars['--color-compliance-compliant'] = '#00ff00';
      cssVars['--color-compliance-error'] = '#ff0000';
    } else {
      cssVars['--color-text-primary'] = '#000000';
      cssVars['--color-text-secondary'] = '#000000';
      cssVars['--color-background-primary'] = '#ffffff';
      cssVars['--color-background-secondary'] = '#ffffff';
      cssVars['--color-border-default'] = '#000000';
      
      // High contrast Polish business colors for light mode
      cssVars['--color-invoice-paid'] = '#008000';
      cssVars['--color-invoice-overdue'] = '#ff0000';
      cssVars['--color-compliance-compliant'] = '#008000';
      cssVars['--color-compliance-error'] = '#ff0000';
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
    cssVars[`--shadow-sm-${key}`] = value;
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

// Polish business formatting utilities
export const polishBusinessUtils = {
  // Currency formatting
  formatCurrency: (amount: number, options?: Intl.NumberFormatOptions): string => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      ...options,
    }).format(amount);
  },
  
  // Date formatting
  formatDate: (date: Date | string, format: 'short' | 'long' | 'numeric' = 'short'): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    const formatOptions: Record<string, Intl.DateTimeFormatOptions> = {
      short: { day: '2-digit', month: '2-digit', year: 'numeric' },
      long: { day: 'numeric', month: 'long', year: 'numeric' },
      numeric: { day: 'numeric', month: 'numeric', year: 'numeric' },
    };
    
    return new Intl.DateTimeFormat('pl-PL', formatOptions[format]).format(dateObj);
  },
  
  // NIP formatting and validation
  formatNIP: (nip: string): string => {
    const cleaned = nip.replace(/\D/g, '');
    if (cleaned.length === 10) {
      return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 6)}-${cleaned.slice(6, 8)}-${cleaned.slice(8)}`;
    }
    return nip;
  },
  
  validateNIP: (nip: string): boolean => {
    const cleaned = nip.replace(/\D/g, '');
    if (cleaned.length !== 10) return false;
    
    const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
    const digits = cleaned.split('').map(Number);
    
    const sum = weights.reduce((acc, weight, index) => acc + weight * digits[index], 0);
    const checksum = sum % 11;
    
    return checksum === digits[9];
  },
  
  // REGON formatting
  formatREGON: (regon: string): string => {
    const cleaned = regon.replace(/\D/g, '');
    if (cleaned.length === 9) {
      return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    } else if (cleaned.length === 14) {
      return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 6)}-${cleaned.slice(6, 8)}-${cleaned.slice(8)}`;
    }
    return regon;
  },
  
  // VAT rate formatting
  formatVATRate: (rate: number): string => {
    if (rate === 0) return '0%';
    if (rate === -1) return 'zw.';
    return `${Math.round(rate * 100)}%`;
  },
  
  // Invoice number formatting
  formatInvoiceNumber: (number: string, year?: number): string => {
    const currentYear = year || new Date().getFullYear();
    if (number.includes('/')) return number;
    return `${number}/${currentYear}`;
  },
  
  // Polish postal code formatting
  formatPostalCode: (code: string): string => {
    const cleaned = code.replace(/\D/g, '');
    if (cleaned.length === 5) {
      return `${cleaned.slice(0, 2)}-${cleaned.slice(2)}`;
    }
    return code;
  },
  
  // Bank account number formatting (Polish IBAN)
  formatBankAccount: (account: string): string => {
    const cleaned = account.replace(/\s/g, '');
    if (cleaned.length === 26 && cleaned.startsWith('PL')) {
      return cleaned.replace(/(.{2})(.{4})(.{4})(.{4})(.{4})(.{4})(.{4})/, '$1 $2 $3 $4 $5 $6 $7');
    } else if (cleaned.length === 26) {
      return `PL ${cleaned.replace(/(.{4})/g, '$1 ').trim()}`;
    }
    return account;
  },
  
  // Get invoice status color
  getInvoiceStatusColor: (status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'): string => {
    return `var(--color-invoice-${status})`;
  },
  
  // Get VAT rate color
  getVATRateColor: (rate: number): string => {
    if (rate === 0.23) return 'var(--color-vat-standard)';
    if (rate === 0.08 || rate === 0.05) return 'var(--color-vat-reduced)';
    if (rate === 0) return 'var(--color-vat-zero)';
    if (rate === -1) return 'var(--color-vat-exempt)';
    return 'var(--color-vat-standard)';
  },
  
  // Get compliance status color
  getComplianceColor: (status: 'compliant' | 'warning' | 'error' | 'pending'): string => {
    return `var(--color-compliance-${status})`;
  },
};

// Theme type definitions
export type Theme = typeof theme;
export type PolishBusinessTheme = typeof polishBusinessTheme;
export type ColorPath = string;
export type SpacingKey = keyof typeof spacing;
export type SemanticSpacingKey = keyof typeof semanticSpacing;
export type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
export type VATRateType = 'standard' | 'reduced' | 'zero' | 'exempt';
export type ComplianceStatus = 'compliant' | 'warning' | 'error' | 'pending';