// Typography Token Definitions
export interface FontFamilyTokens {
  sans: string[];
  serif: string[];
  mono: string[];
}

export interface FontSizeScale {
  xs: string;
  sm: string;
  base: string;
  lg: string;
  xl: string;
  '2xl': string;
  '3xl': string;
  '4xl': string;
  '5xl': string;
  '6xl': string;
}

export interface FontWeightScale {
  thin: number;
  extralight: number;
  light: number;
  normal: number;
  medium: number;
  semibold: number;
  bold: number;
  extrabold: number;
  black: number;
}

export interface LineHeightScale {
  none: number;
  tight: number;
  snug: number;
  normal: number;
  relaxed: number;
  loose: number;
}

export interface TypographyTokens {
  fontFamily: FontFamilyTokens;
  fontSize: FontSizeScale;
  fontWeight: FontWeightScale;
  lineHeight: LineHeightScale;
}

// Font families with Polish character support
export const fontFamily: FontFamilyTokens = {
  sans: [
    'Inter',
    '-apple-system',
    'BlinkMacSystemFont',
    'Segoe UI',
    'Roboto',
    'Oxygen',
    'Ubuntu',
    'Cantarell',
    'Fira Sans',
    'Droid Sans',
    'Helvetica Neue',
    'sans-serif'
  ],
  serif: [
    'Georgia',
    'Cambria',
    'Times New Roman',
    'Times',
    'serif'
  ],
  mono: [
    'Menlo',
    'Monaco',
    'Consolas',
    'Liberation Mono',
    'Courier New',
    'monospace'
  ],
};

// Font size scale following 8px grid system
export const fontSize: FontSizeScale = {
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem', // 36px
  '5xl': '3rem',    // 48px
  '6xl': '3.75rem', // 60px
};

// Font weight scale
export const fontWeight: FontWeightScale = {
  thin: 100,
  extralight: 200,
  light: 300,
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
  extrabold: 800,
  black: 900,
};

// Line height scale
export const lineHeight: LineHeightScale = {
  none: 1,
  tight: 1.25,
  snug: 1.375,
  normal: 1.5,
  relaxed: 1.625,
  loose: 2,
};

// Complete typography tokens
export const typography: TypographyTokens = {
  fontFamily,
  fontSize,
  fontWeight,
  lineHeight,
};

// Semantic typography styles for Polish business context
export const typographyStyles = {
  // Headings
  h1: {
    fontSize: fontSize['4xl'],
    fontWeight: fontWeight.bold,
    lineHeight: lineHeight.tight,
    fontFamily: fontFamily.sans.join(', '),
    letterSpacing: '-0.025em',
  },
  h2: {
    fontSize: fontSize['3xl'],
    fontWeight: fontWeight.bold,
    lineHeight: lineHeight.tight,
    fontFamily: fontFamily.sans.join(', '),
    letterSpacing: '-0.025em',
  },
  h3: {
    fontSize: fontSize['2xl'],
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.snug,
    fontFamily: fontFamily.sans.join(', '),
    letterSpacing: '-0.025em',
  },
  h4: {
    fontSize: fontSize.xl,
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.snug,
    fontFamily: fontFamily.sans.join(', '),
  },
  h5: {
    fontSize: fontSize.lg,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
  h6: {
    fontSize: fontSize.base,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
  
  // Body text
  bodyLarge: {
    fontSize: fontSize.lg,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.relaxed,
    fontFamily: fontFamily.sans.join(', '),
  },
  body: {
    fontSize: fontSize.base,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
  bodySmall: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
  
  // UI text
  caption: {
    fontSize: fontSize.xs,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
    textTransform: 'uppercase' as const,
    letterSpacing: '0.05em',
  },
  label: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
  button: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.none,
    fontFamily: fontFamily.sans.join(', '),
    letterSpacing: '0.025em',
  },
  
  // Links
  link: {
    fontSize: fontSize.base,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
    textDecoration: 'underline',
    textDecorationColor: 'transparent',
  },
  
  // Code
  code: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.mono.join(', '),
    letterSpacing: '0.025em',
  },
  codeBlock: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.relaxed,
    fontFamily: fontFamily.mono.join(', '),
    letterSpacing: '0.025em',
  },
  
  // Polish business specific styles
  invoiceTitle: {
    fontSize: fontSize['2xl'],
    fontWeight: fontWeight.bold,
    lineHeight: lineHeight.tight,
    fontFamily: fontFamily.sans.join(', '),
    letterSpacing: '-0.025em',
    textTransform: 'uppercase' as const,
  },
  invoiceNumber: {
    fontSize: fontSize.lg,
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.mono.join(', '),
    letterSpacing: '0.05em',
  },
  companyName: {
    fontSize: fontSize.xl,
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.snug,
    fontFamily: fontFamily.sans.join(', '),
  },
  contractorName: {
    fontSize: fontSize.lg,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
  currencyAmount: {
    fontSize: fontSize.base,
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.mono.join(', '),
    fontVariantNumeric: 'tabular-nums',
    textAlign: 'right' as const,
  },
  currencyAmountLarge: {
    fontSize: fontSize.lg,
    fontWeight: fontWeight.bold,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.mono.join(', '),
    fontVariantNumeric: 'tabular-nums',
    textAlign: 'right' as const,
  },
  dateFormat: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.mono.join(', '),
    fontVariantNumeric: 'tabular-nums',
  },
  nipFormat: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.mono.join(', '),
    letterSpacing: '0.1em',
  },
  vatRate: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
    textAlign: 'center' as const,
  },
  statusBadge: {
    fontSize: fontSize.xs,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.none,
    fontFamily: fontFamily.sans.join(', '),
    textTransform: 'uppercase' as const,
    letterSpacing: '0.05em',
  },
  tableHeader: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
    textTransform: 'uppercase' as const,
    letterSpacing: '0.025em',
  },
  tableCell: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
  formLabel: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
  formHelperText: {
    fontSize: fontSize.xs,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
  formErrorText: {
    fontSize: fontSize.xs,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.normal,
    fontFamily: fontFamily.sans.join(', '),
  },
} as const;

// Responsive typography scales for different screen sizes
export const responsiveTypography = {
  // Mobile-first responsive headings
  h1Responsive: {
    fontSize: fontSize['2xl'],
    '@media (min-width: 768px)': {
      fontSize: fontSize['3xl'],
    },
    '@media (min-width: 1024px)': {
      fontSize: fontSize['4xl'],
    },
  },
  h2Responsive: {
    fontSize: fontSize.xl,
    '@media (min-width: 768px)': {
      fontSize: fontSize['2xl'],
    },
    '@media (min-width: 1024px)': {
      fontSize: fontSize['3xl'],
    },
  },
  h3Responsive: {
    fontSize: fontSize.lg,
    '@media (min-width: 768px)': {
      fontSize: fontSize.xl,
    },
    '@media (min-width: 1024px)': {
      fontSize: fontSize['2xl'],
    },
  },
  
  // Responsive body text
  bodyResponsive: {
    fontSize: fontSize.sm,
    '@media (min-width: 768px)': {
      fontSize: fontSize.base,
    },
  },
  
  // Responsive invoice elements
  invoiceTitleResponsive: {
    fontSize: fontSize.xl,
    '@media (min-width: 768px)': {
      fontSize: fontSize['2xl'],
    },
  },
  currencyResponsive: {
    fontSize: fontSize.sm,
    '@media (min-width: 768px)': {
      fontSize: fontSize.base,
    },
  },
} as const;

// Typography utilities for Polish language support
export const polishTypographyUtils = {
  // Polish character support check
  supportsPolishChars: (fontFamily: string[]): boolean => {
    // In a real implementation, this would test font rendering
    // For now, we assume Inter supports Polish characters
    return fontFamily.includes('Inter');
  },
  
  // Polish text formatting rules
  polishTextRules: {
    // Polish uses different quotation marks
    quotationMarks: {
      primary: '„"',
      secondary: '‚'',
    },
    
    // Polish decimal separator
    decimalSeparator: ',',
    
    // Polish thousand separator
    thousandSeparator: ' ',
    
    // Polish date format
    dateFormat: 'DD.MM.YYYY',
    
    // Polish time format
    timeFormat: 'HH:mm',
    
    // Polish currency format
    currencyFormat: '0,00 zł',
  },
  
  // Text length considerations for Polish
  polishTextLengths: {
    // Polish text is typically 20-30% longer than English
    expansionFactor: 1.25,
    
    // Common Polish business terms and their lengths
    commonTerms: {
      'faktura': 7,
      'kontrahent': 10,
      'wystawiona': 10,
      'opłacona': 8,
      'przeterminowana': 15,
      'anulowana': 9,
    },
  },
  
  // Get appropriate line height for Polish text
  getPolishLineHeight: (fontSize: string): number => {
    // Polish text with diacritics may need slightly more line height
    const baseFontSize = parseFloat(fontSize);
    if (baseFontSize <= 14) return 1.6; // Extra space for small text
    if (baseFontSize <= 18) return 1.5;
    return 1.4;
  },
  
  // Format Polish currency
  formatPolishCurrency: (amount: number): string => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  },
  
  // Format Polish date
  formatPolishDate: (date: Date): string => {
    return new Intl.DateTimeFormat('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }).format(date);
  },
  
  // Format Polish number
  formatPolishNumber: (number: number): string => {
    return new Intl.NumberFormat('pl-PL').format(number);
  },
} as const;

export type TypographyStyleKey = keyof typeof typographyStyles;
export type ResponsiveTypographyKey = keyof typeof responsiveTypography;
export type PolishTypographyUtilsKey = keyof typeof polishTypographyUtils;