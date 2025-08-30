// Color Token Definitions
export interface ColorScale {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;
  600: string;
  700: string;
  800: string;
  900: string;
}

export interface ColorTokens {
  primary: ColorScale;
  secondary: ColorScale;
  success: ColorScale;
  warning: ColorScale;
  error: ColorScale;
  neutral: ColorScale;
}

// Primary Blue - FaktuLove brand color
export const primary: ColorScale = {
  50: '#eff6ff',
  100: '#dbeafe',
  200: '#bfdbfe',
  300: '#93c5fd',
  400: '#60a5fa',
  500: '#3b82f6',
  600: '#2563eb', // Brand primary
  700: '#1d4ed8',
  800: '#1e40af',
  900: '#1e3a8a',
};

// Secondary Gray
export const secondary: ColorScale = {
  50: '#f9fafb',
  100: '#f3f4f6',
  200: '#e5e7eb',
  300: '#d1d5db',
  400: '#9ca3af',
  500: '#6b7280',
  600: '#4b5563',
  700: '#374151',
  800: '#1f2937',
  900: '#111827',
};

// Success Green
export const success: ColorScale = {
  50: '#f0fdf4',
  100: '#dcfce7',
  200: '#bbf7d0',
  300: '#86efac',
  400: '#4ade80',
  500: '#22c55e',
  600: '#059669', // Polish business success color
  700: '#15803d',
  800: '#166534',
  900: '#14532d',
};

// Warning Orange
export const warning: ColorScale = {
  50: '#fffbeb',
  100: '#fef3c7',
  200: '#fde68a',
  300: '#fcd34d',
  400: '#fbbf24',
  500: '#f59e0b',
  600: '#d97706', // Polish business warning color
  700: '#b45309',
  800: '#92400e',
  900: '#78350f',
};

// Error Red
export const error: ColorScale = {
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
};

// Neutral Gray Scale
export const neutral: ColorScale = {
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
};

// Complete color tokens object
export const colors: ColorTokens = {
  primary,
  secondary,
  success,
  warning,
  error,
  neutral,
};

// Semantic color mappings for Polish business context
export const semanticColors = {
  // Text colors
  textPrimary: neutral[900],
  textSecondary: neutral[600],
  textMuted: neutral[500],
  textInverse: neutral[50],
  textDisabled: neutral[400],
  textPlaceholder: neutral[400],
  textLink: primary[600],
  textLinkHover: primary[700],
  
  // Background colors
  backgroundPrimary: neutral[50],
  backgroundSecondary: neutral[100],
  backgroundMuted: neutral[200],
  backgroundInverse: neutral[900],
  backgroundOverlay: 'rgba(0, 0, 0, 0.5)',
  backgroundDisabled: neutral[100],
  backgroundHover: neutral[50],
  backgroundPressed: neutral[100],
  
  // Border colors
  borderDefault: neutral[200],
  borderMuted: neutral[100],
  borderStrong: neutral[300],
  borderFocus: primary[600],
  borderError: error[600],
  borderSuccess: success[600],
  borderWarning: warning[600],
  
  // Interactive colors
  interactive: primary[600],
  interactiveHover: primary[700],
  interactiveActive: primary[800],
  interactiveDisabled: neutral[300],
  interactiveFocus: primary[600],
  
  // Status colors
  statusSuccess: success[600],
  statusSuccessBackground: success[50],
  statusSuccessBorder: success[200],
  statusWarning: warning[600],
  statusWarningBackground: warning[50],
  statusWarningBorder: warning[200],
  statusError: error[600],
  statusErrorBackground: error[50],
  statusErrorBorder: error[200],
  statusInfo: primary[600],
  statusInfoBackground: primary[50],
  statusInfoBorder: primary[200],
  
  // Polish business specific colors
  polishBusinessPrimary: primary[600],    // Professional blue for Polish business
  polishBusinessAccent: success[600],     // Success green for positive actions
  polishBusinessWarning: warning[600],    // Warning orange for attention
  polishBusinessDanger: error[600],       // Error red for critical actions
  
  // Invoice specific colors
  invoiceDraft: neutral[500],
  invoiceDraftBackground: neutral[50],
  invoiceSent: primary[600],
  invoiceSentBackground: primary[50],
  invoicePaid: success[600],
  invoicePaidBackground: success[50],
  invoiceOverdue: error[600],
  invoiceOverdueBackground: error[50],
  invoiceCancelled: neutral[400],
  invoiceCancelledBackground: neutral[50],
  
  // VAT and tax colors
  vatStandard: primary[600],              // 23% VAT
  vatReduced: success[600],               // 8%, 5% VAT
  vatZero: neutral[600],                  // 0% VAT
  vatExempt: warning[600],                // Exempt (zw.)
  
  // Currency and financial colors
  currencyPositive: success[700],         // Positive amounts
  currencyNegative: error[700],           // Negative amounts
  currencyNeutral: neutral[700],          // Zero or neutral amounts
  
  // Form validation colors
  formValid: success[600],
  formValidBackground: success[50],
  formInvalid: error[600],
  formInvalidBackground: error[50],
  formPending: warning[600],
  formPendingBackground: warning[50],
} as const;

// Color utility functions for Polish business context
export const polishBusinessColors = {
  // Get invoice status color
  getInvoiceStatusColor: (status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled') => {
    const colorMap = {
      draft: semanticColors.invoiceDraft,
      sent: semanticColors.invoiceSent,
      paid: semanticColors.invoicePaid,
      overdue: semanticColors.invoiceOverdue,
      cancelled: semanticColors.invoiceCancelled,
    };
    return colorMap[status];
  },
  
  // Get invoice status background color
  getInvoiceStatusBackground: (status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled') => {
    const colorMap = {
      draft: semanticColors.invoiceDraftBackground,
      sent: semanticColors.invoiceSentBackground,
      paid: semanticColors.invoicePaidBackground,
      overdue: semanticColors.invoiceOverdueBackground,
      cancelled: semanticColors.invoiceCancelledBackground,
    };
    return colorMap[status];
  },
  
  // Get VAT rate color
  getVATRateColor: (rate: number) => {
    if (rate === 0.23) return semanticColors.vatStandard;
    if (rate === 0.08 || rate === 0.05) return semanticColors.vatReduced;
    if (rate === 0) return semanticColors.vatZero;
    if (rate === -1) return semanticColors.vatExempt; // Exempt
    return semanticColors.vatStandard;
  },
  
  // Get currency amount color
  getCurrencyColor: (amount: number) => {
    if (amount > 0) return semanticColors.currencyPositive;
    if (amount < 0) return semanticColors.currencyNegative;
    return semanticColors.currencyNeutral;
  },
  
  // Get validation state color
  getValidationColor: (state: 'valid' | 'invalid' | 'pending') => {
    const colorMap = {
      valid: semanticColors.formValid,
      invalid: semanticColors.formInvalid,
      pending: semanticColors.formPending,
    };
    return colorMap[state];
  },
} as const;

export type SemanticColorKey = keyof typeof semanticColors;

// Color accessibility utilities
export const colorAccessibility = {
  // WCAG contrast ratios
  contrastRatios: {
    AA_NORMAL: 4.5,
    AA_LARGE: 3,
    AAA_NORMAL: 7,
    AAA_LARGE: 4.5,
  },
  
  // High contrast color pairs for accessibility
  highContrastPairs: {
    // Text on background combinations that meet WCAG AA
    textOnLight: {
      primary: neutral[900],
      secondary: neutral[700],
      muted: neutral[600],
    },
    textOnDark: {
      primary: neutral[50],
      secondary: neutral[200],
      muted: neutral[300],
    },
    textOnPrimary: {
      primary: neutral[50],
      secondary: primary[100],
      muted: primary[200],
    },
    textOnSuccess: {
      primary: neutral[50],
      secondary: success[100],
      muted: success[200],
    },
    textOnWarning: {
      primary: neutral[900],
      secondary: warning[800],
      muted: warning[700],
    },
    textOnError: {
      primary: neutral[50],
      secondary: error[100],
      muted: error[200],
    },
  },
  
  // Get accessible text color for background
  getAccessibleTextColor: (backgroundColor: string): string => {
    // Simplified implementation - in production, use proper contrast calculation
    const darkBackgrounds = [
      neutral[700], neutral[800], neutral[900],
      primary[700], primary[800], primary[900],
      success[700], success[800], success[900],
      error[700], error[800], error[900],
    ];
    
    return darkBackgrounds.includes(backgroundColor) 
      ? neutral[50] 
      : neutral[900];
  },
  
  // Color combinations for Polish business context
  polishBusinessCombinations: {
    // Professional combinations for invoices
    invoiceHeader: {
      background: primary[600],
      text: neutral[50],
      accent: primary[100],
    },
    invoiceBody: {
      background: neutral[50],
      text: neutral[900],
      accent: neutral[200],
    },
    invoiceFooter: {
      background: neutral[100],
      text: neutral[700],
      accent: neutral[300],
    },
    
    // Form combinations
    formField: {
      background: neutral[50],
      text: neutral[900],
      border: neutral[200],
      focus: primary[600],
    },
    formError: {
      background: error[50],
      text: error[800],
      border: error[200],
      focus: error[600],
    },
    formSuccess: {
      background: success[50],
      text: success[800],
      border: success[200],
      focus: success[600],
    },
    
    // Dashboard combinations
    dashboardCard: {
      background: neutral[50],
      text: neutral[900],
      border: neutral[200],
      shadowSm: 'rgba(0, 0, 0, 0.1)',
    },
    dashboardHeader: {
      background: neutral[900],
      text: neutral[50],
      accent: neutral[700],
    },
  },
} as const;

// Dark mode color palette
export const darkModeColors = {
  // Text colors in dark mode
  textPrimary: neutral[50],
  textSecondary: neutral[300],
  textMuted: neutral[400],
  textInverse: neutral[900],
  textDisabled: neutral[500],
  textPlaceholder: neutral[500],
  textLink: primary[400],
  textLinkHover: primary[300],
  
  // Background colors in dark mode
  backgroundPrimary: neutral[900],
  backgroundSecondary: neutral[800],
  backgroundMuted: neutral[700],
  backgroundInverse: neutral[50],
  backgroundOverlay: 'rgba(0, 0, 0, 0.8)',
  backgroundDisabled: neutral[800],
  backgroundHover: neutral[800],
  backgroundPressed: neutral[700],
  
  // Border colors in dark mode
  borderDefault: neutral[700],
  borderMuted: neutral[800],
  borderStrong: neutral[600],
  borderFocus: primary[500],
  borderError: error[500],
  borderSuccess: success[500],
  borderWarning: warning[500],
  
  // Interactive colors adjusted for dark mode
  interactive: primary[500],
  interactiveHover: primary[400],
  interactiveActive: primary[600],
  interactiveDisabled: neutral[600],
  interactiveFocus: primary[500],
  
  // Status colors for dark mode
  statusSuccess: success[400],
  statusSuccessBackground: success[900],
  statusSuccessBorder: success[700],
  statusWarning: warning[400],
  statusWarningBackground: warning[900],
  statusWarningBorder: warning[700],
  statusError: error[400],
  statusErrorBackground: error[900],
  statusErrorBorder: error[700],
  statusInfo: primary[400],
  statusInfoBackground: primary[900],
  statusInfoBorder: primary[700],
  
  // Polish business colors for dark mode
  polishBusinessPrimary: primary[500],
  polishBusinessAccent: success[400],
  polishBusinessWarning: warning[400],
  polishBusinessDanger: error[400],
  
  // Invoice status colors for dark mode
  invoiceDraft: neutral[400],
  invoiceDraftBackground: neutral[800],
  invoiceSent: primary[400],
  invoiceSentBackground: primary[900],
  invoicePaid: success[400],
  invoicePaidBackground: success[900],
  invoiceOverdue: error[400],
  invoiceOverdueBackground: error[900],
  invoiceCancelled: neutral[500],
  invoiceCancelledBackground: neutral[800],
  
  // VAT and tax colors for dark mode
  vatStandard: primary[400],
  vatReduced: success[400],
  vatZero: neutral[400],
  vatExempt: warning[400],
  
  // Currency colors for dark mode
  currencyPositive: success[400],
  currencyNegative: error[400],
  currencyNeutral: neutral[300],
  
  // Form validation colors for dark mode
  formValid: success[400],
  formValidBackground: success[900],
  formInvalid: error[400],
  formInvalidBackground: error[900],
  formPending: warning[400],
  formPendingBackground: warning[900],
} as const;

// High contrast color palette
export const highContrastColors = {
  light: {
    // High contrast light mode
    textPrimary: '#000000',
    textSecondary: '#000000',
    textMuted: '#000000',
    textInverse: '#ffffff',
    textDisabled: '#666666',
    textPlaceholder: '#666666',
    textLink: '#0000ff',
    textLinkHover: '#0000cc',
    
    backgroundPrimary: '#ffffff',
    backgroundSecondary: '#ffffff',
    backgroundMuted: '#f0f0f0',
    backgroundInverse: '#000000',
    backgroundOverlay: 'rgba(0, 0, 0, 0.9)',
    backgroundDisabled: '#f0f0f0',
    backgroundHover: '#f0f0f0',
    backgroundPressed: '#e0e0e0',
    
    borderDefault: '#000000',
    borderMuted: '#666666',
    borderStrong: '#000000',
    borderFocus: '#0000ff',
    borderError: '#ff0000',
    borderSuccess: '#008000',
    borderWarning: '#ff8000',
    
    interactive: '#0000ff',
    interactiveHover: '#0000cc',
    interactiveActive: '#000099',
    interactiveDisabled: '#666666',
    interactiveFocus: '#0000ff',
    
    statusSuccess: '#008000',
    statusSuccessBackground: '#ffffff',
    statusSuccessBorder: '#008000',
    statusWarning: '#ff8000',
    statusWarningBackground: '#ffffff',
    statusWarningBorder: '#ff8000',
    statusError: '#ff0000',
    statusErrorBackground: '#ffffff',
    statusErrorBorder: '#ff0000',
    statusInfo: '#0000ff',
    statusInfoBackground: '#ffffff',
    statusInfoBorder: '#0000ff',
  },
  
  dark: {
    // High contrast dark mode
    textPrimary: '#ffffff',
    textSecondary: '#ffffff',
    textMuted: '#ffffff',
    textInverse: '#000000',
    textDisabled: '#999999',
    textPlaceholder: '#999999',
    textLink: '#66ccff',
    textLinkHover: '#99ddff',
    
    backgroundPrimary: '#000000',
    backgroundSecondary: '#000000',
    backgroundMuted: '#1a1a1a',
    backgroundInverse: '#ffffff',
    backgroundOverlay: 'rgba(255, 255, 255, 0.9)',
    backgroundDisabled: '#1a1a1a',
    backgroundHover: '#1a1a1a',
    backgroundPressed: '#333333',
    
    borderDefault: '#ffffff',
    borderMuted: '#999999',
    borderStrong: '#ffffff',
    borderFocus: '#66ccff',
    borderError: '#ff6666',
    borderSuccess: '#66ff66',
    borderWarning: '#ffcc66',
    
    interactive: '#66ccff',
    interactiveHover: '#99ddff',
    interactiveActive: '#33aaff',
    interactiveDisabled: '#999999',
    interactiveFocus: '#66ccff',
    
    statusSuccess: '#66ff66',
    statusSuccessBackground: '#000000',
    statusSuccessBorder: '#66ff66',
    statusWarning: '#ffcc66',
    statusWarningBackground: '#000000',
    statusWarningBorder: '#ffcc66',
    statusError: '#ff6666',
    statusErrorBackground: '#000000',
    statusErrorBorder: '#ff6666',
    statusInfo: '#66ccff',
    statusInfoBackground: '#000000',
    statusInfoBorder: '#66ccff',
  },
} as const;

// Export all color-related types
export type PolishBusinessColorFunction = keyof typeof polishBusinessColors;
export type ColorAccessibilityKey = keyof typeof colorAccessibility;