// Design System Configuration
import { colors, semanticColors } from './tokens/colors';
import { typography, typographyStyles } from './tokens/typography';
import { spacing, semanticSpacing, sizeVariants } from './tokens/spacing';
import { breakpoints, mediaQueries, containerMaxWidths } from './tokens/breakpoints';
import { shadows, semanticShadows, focusRings } from './tokens/shadows';
import { borderRadius, semanticBorderRadius } from './tokens/borderRadius';

// Complete design system configuration
export const designSystemConfig = {
  // Version information
  version: '1.0.0',
  name: 'FaktuLove Design System',
  
  // Core tokens
  tokens: {
    colors,
    typography,
    spacing,
    breakpoints,
    shadows,
    borderRadius,
  },
  
  // Semantic tokens
  semantic: {
    colors: semanticColors,
    spacing: semanticSpacing,
    shadows: semanticShadows,
    borderRadius: semanticBorderRadius,
    typography: typographyStyles,
  },
  
  // Component configuration
  components: {
    // Size variants for consistent component sizing
    sizes: sizeVariants,
    
    // Focus ring configuration
    focusRings,
    
    // Animation configuration
    animations: {
      duration: {
        fast: '150ms',
        normal: '300ms',
        slow: '500ms',
      },
      easing: {
        ease: 'ease',
        easeIn: 'ease-in',
        easeOut: 'ease-out',
        easeInOut: 'ease-in-out',
        linear: 'linear',
      },
    },
    
    // Z-index scale
    zIndex: {
      hide: -1,
      auto: 'auto',
      base: 0,
      docked: 10,
      dropdown: 1000,
      sticky: 1100,
      banner: 1200,
      overlay: 1300,
      modal: 1400,
      popover: 1500,
      skipLink: 1600,
      toast: 1700,
      tooltip: 1800,
    },
  },
  
  // Responsive configuration
  responsive: {
    breakpoints,
    mediaQueries,
    containerMaxWidths,
  },
  
  // Polish business context configuration
  polish: {
    // Currency formatting
    currency: {
      symbol: 'zł',
      code: 'PLN',
      locale: 'pl-PL',
      decimalPlaces: 2,
    },
    
    // Date formatting
    date: {
      locale: 'pl-PL',
      format: 'DD.MM.YYYY',
      longFormat: 'DD MMMM YYYY',
    },
    
    // VAT rates
    vatRates: [
      { value: 0.23, label: '23%' },
      { value: 0.08, label: '8%' },
      { value: 0.05, label: '5%' },
      { value: 0, label: '0%' },
      { value: -1, label: 'zw.' }, // zwolniony (exempt)
    ],
    
    // Invoice statuses
    invoiceStatuses: {
      draft: { label: 'Szkic', color: 'neutral' },
      sent: { label: 'Wysłana', color: 'primary' },
      paid: { label: 'Opłacona', color: 'success' },
      overdue: { label: 'Przeterminowana', color: 'error' },
      cancelled: { label: 'Anulowana', color: 'neutral' },
    },
    
    // Common Polish business terms
    terms: {
      invoice: 'Faktura',
      contractor: 'Kontrahent',
      company: 'Firma',
      amount: 'Kwota',
      netAmount: 'Kwota netto',
      grossAmount: 'Kwota brutto',
      vatAmount: 'Kwota VAT',
      date: 'Data',
      issueDate: 'Data wystawienia',
      dueDate: 'Termin płatności',
      paymentMethod: 'Sposób płatności',
      bankAccount: 'Numer konta',
      nip: 'NIP',
      regon: 'REGON',
      krs: 'KRS',
      address: 'Adres',
      city: 'Miasto',
      postalCode: 'Kod pocztowy',
      country: 'Kraj',
      phone: 'Telefon',
      email: 'E-mail',
      website: 'Strona internetowa',
    },
  },
  
  // Accessibility configuration
  accessibility: {
    // WCAG compliance level
    wcagLevel: 'AA',
    
    // Minimum contrast ratios
    contrastRatios: {
      normal: 4.5,
      large: 3,
      enhanced: 7,
    },
    
    // Focus management
    focus: {
      outlineWidth: '2px',
      outlineOffset: '2px',
      outlineStyle: 'solid',
    },
    
    // Screen reader support
    screenReader: {
      locale: 'pl-PL',
      announcements: true,
      liveRegions: true,
    },
  },
  
  // Development configuration
  development: {
    // Enable design system warnings
    warnings: process.env.NODE_ENV === 'development',
    
    // Enable accessibility testing
    a11yTesting: process.env.NODE_ENV === 'development',
    
    // Enable performance monitoring
    performanceMonitoring: process.env.NODE_ENV === 'development',
  },
} as const;

// Type definitions
export type DesignSystemConfig = typeof designSystemConfig;
export type ColorVariant = keyof typeof colors;
export type SemanticColorKey = keyof typeof semanticColors;
export type SpacingKey = keyof typeof spacing;
export type BreakpointKey = keyof typeof breakpoints;
export type ShadowKey = keyof typeof shadows;
export type BorderRadiusKey = keyof typeof borderRadius;
export type SizeVariant = keyof typeof sizeVariants;
export type TypographyStyleKey = keyof typeof typographyStyles;

// Export individual configurations for easier access
export const { tokens, semantic, components, responsive, polish, accessibility, development } = designSystemConfig;

// Utility function to get design system value
export const getDesignSystemValue = (path: string, fallback?: any): any => {
  try {
    const keys = path.split('.');
    let value: any = designSystemConfig;
    
    for (const key of keys) {
      value = value[key];
      if (value === undefined) {
        throw new Error(`Design system path ${path} not found`);
      }
    }
    
    return value;
  } catch (error) {
    if (fallback !== undefined) {
      if (development.warnings) {
        console.warn(`Design system value ${path} not found, using fallback:`, fallback);
      }
      return fallback;
    }
    throw error;
  }
};

// Export default configuration
export default designSystemConfig;