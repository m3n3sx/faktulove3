// Color Utility Functions
import { colors, semanticColors, polishBusinessColors, colorAccessibility } from '../tokens/colors';

// Color manipulation utilities
export const colorUtils = {
  // Convert hex to RGB
  hexToRgb: (hex: string): { r: number; g: number; b: number } | null => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  },

  // Convert RGB to hex
  rgbToHex: (r: number, g: number, b: number): string => {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  },

  // Calculate relative luminance (WCAG formula)
  getLuminance: (hex: string): number => {
    const rgb = colorUtils.hexToRgb(hex);
    if (!rgb) return 0;

    const { r, g, b } = rgb;
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  },

  // Calculate contrast ratio between two colors
  getContrastRatio: (color1: string, color2: string): number => {
    const lum1 = colorUtils.getLuminance(color1);
    const lum2 = colorUtils.getLuminance(color2);
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    return (brightest + 0.05) / (darkest + 0.05);
  },

  // Check if color combination meets WCAG standards
  meetsWCAG: (foreground: string, background: string, level: 'AA' | 'AAA' = 'AA', size: 'normal' | 'large' = 'normal'): boolean => {
    const contrast = colorUtils.getContrastRatio(foreground, background);
    const requiredRatio = level === 'AAA' 
      ? (size === 'large' ? 4.5 : 7)
      : (size === 'large' ? 3 : 4.5);
    return contrast >= requiredRatio;
  },

  // Get accessible text color for background
  getAccessibleTextColor: (backgroundColor: string): string => {
    const whiteContrast = colorUtils.getContrastRatio('#ffffff', backgroundColor);
    const blackContrast = colorUtils.getContrastRatio('#000000', backgroundColor);
    return whiteContrast > blackContrast ? '#ffffff' : '#000000';
  },

  // Lighten a color by percentage
  lighten: (hex: string, percent: number): string => {
    const rgb = colorUtils.hexToRgb(hex);
    if (!rgb) return hex;

    const { r, g, b } = rgb;
    const amount = Math.round(2.55 * percent);
    
    return colorUtils.rgbToHex(
      Math.min(255, r + amount),
      Math.min(255, g + amount),
      Math.min(255, b + amount)
    );
  },

  // Darken a color by percentage
  darken: (hex: string, percent: number): string => {
    const rgb = colorUtils.hexToRgb(hex);
    if (!rgb) return hex;

    const { r, g, b } = rgb;
    const amount = Math.round(2.55 * percent);
    
    return colorUtils.rgbToHex(
      Math.max(0, r - amount),
      Math.max(0, g - amount),
      Math.max(0, b - amount)
    );
  },

  // Add alpha to hex color
  addAlpha: (hex: string, alpha: number): string => {
    const rgb = colorUtils.hexToRgb(hex);
    if (!rgb) return hex;

    const { r, g, b } = rgb;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  },
} as const;

// Polish business color utilities
export const polishColorUtils = {
  // Get invoice status colors with proper contrast
  getInvoiceStatusColors: (status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled') => {
    const baseColor = polishBusinessColors.getInvoiceStatusColor(status);
    const backgroundColor = polishBusinessColors.getInvoiceStatusBackground(status);
    
    return {
      color: baseColor,
      backgroundColor,
      borderColor: baseColor,
      textColor: colorUtils.getAccessibleTextColor(backgroundColor),
    };
  },

  // Get VAT rate colors
  getVATRateColors: (rate: number) => {
    const baseColor = polishBusinessColors.getVATRateColor(rate);
    const backgroundColor = colorUtils.lighten(baseColor, 90);
    
    return {
      color: baseColor,
      backgroundColor,
      borderColor: baseColor,
      textColor: colorUtils.getAccessibleTextColor(backgroundColor),
    };
  },

  // Get currency amount colors
  getCurrencyColors: (amount: number) => {
    const baseColor = polishBusinessColors.getCurrencyColor(amount);
    
    return {
      color: baseColor,
      backgroundColor: 'transparent',
      textColor: baseColor,
    };
  },

  // Get form validation colors
  getValidationColors: (state: 'valid' | 'invalid' | 'pending') => {
    const baseColor = polishBusinessColors.getValidationColor(state);
    const backgroundColor = colorUtils.lighten(baseColor, 95);
    
    return {
      color: baseColor,
      backgroundColor,
      borderColor: baseColor,
      textColor: colorUtils.getAccessibleTextColor(backgroundColor),
    };
  },

  // Polish business color palette for charts and data visualization
  getChartColors: () => [
    colors.primary[600],   // Main data series
    colors.success[600],   // Positive trends
    colors.warning[600],   // Neutral/warning data
    colors.error[600],     // Negative trends
    colors.secondary[600], // Additional data
    colors.primary[400],   // Light variant
    colors.success[400],   // Light positive
    colors.warning[400],   // Light warning
  ],

  // Get professional color combinations for Polish business documents
  getDocumentColors: () => ({
    header: {
      background: colors.primary[600],
      text: '#ffffff',
      accent: colors.primary[100],
    },
    body: {
      background: '#ffffff',
      text: colors.neutral[900],
      accent: colors.neutral[100],
    },
    footer: {
      background: colors.neutral[50],
      text: colors.neutral[700],
      accent: colors.neutral[200],
    },
    table: {
      headerBackground: colors.neutral[100],
      headerText: colors.neutral[900],
      rowBackground: '#ffffff',
      rowAlternateBackground: colors.neutral[50],
      rowText: colors.neutral[900],
      border: colors.neutral[200],
    },
  }),
} as const;

// Color accessibility testing utilities
export const colorA11yUtils = {
  // Test all semantic color combinations
  testSemanticColors: () => {
    const results: Array<{
      combination: string;
      contrast: number;
      passes: boolean;
      level: string;
    }> = [];

    // Test common text/background combinations
    const testCombinations = [
      { name: 'Primary text on light background', fg: semanticColors.textPrimary, bg: semanticColors.backgroundPrimary },
      { name: 'Secondary text on light background', fg: semanticColors.textSecondary, bg: semanticColors.backgroundPrimary },
      { name: 'Muted text on light background', fg: semanticColors.textMuted, bg: semanticColors.backgroundPrimary },
      { name: 'Interactive text on light background', fg: semanticColors.interactive, bg: semanticColors.backgroundPrimary },
      { name: 'Success text on success background', fg: semanticColors.statusSuccess, bg: semanticColors.statusSuccessBackground },
      { name: 'Warning text on warning background', fg: semanticColors.statusWarning, bg: semanticColors.statusWarningBackground },
      { name: 'Error text on error background', fg: semanticColors.statusError, bg: semanticColors.statusErrorBackground },
    ];

    testCombinations.forEach(({ name, fg, bg }) => {
      const contrast = colorUtils.getContrastRatio(fg, bg);
      const passesAA = contrast >= 4.5;
      const passesAAA = contrast >= 7;
      
      results.push({
        combination: name,
        contrast: Math.round(contrast * 100) / 100,
        passes: passesAA,
        level: passesAAA ? 'AAA' : passesAA ? 'AA' : 'Fail',
      });
    });

    return results;
  },

  // Test Polish business color combinations
  testPolishBusinessColors: () => {
    const results: Array<{
      context: string;
      combination: string;
      contrast: number;
      passes: boolean;
    }> = [];

    // Test invoice status combinations
    const invoiceStatuses: Array<'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'> = 
      ['draft', 'sent', 'paid', 'overdue', 'cancelled'];

    invoiceStatuses.forEach(status => {
      const colors = polishColorUtils.getInvoiceStatusColors(status);
      const contrast = colorUtils.getContrastRatio(colors.color, colors.backgroundColor);
      
      results.push({
        context: 'Invoice Status',
        combination: `${status} status`,
        contrast: Math.round(contrast * 100) / 100,
        passes: contrast >= 4.5,
      });
    });

    return results;
  },

  // Generate accessibility report
  generateA11yReport: () => {
    const semanticResults = colorA11yUtils.testSemanticColors();
    const businessResults = colorA11yUtils.testPolishBusinessColors();
    
    const totalTests = semanticResults.length + businessResults.length;
    const passedTests = [
      ...semanticResults.filter(r => r.passes),
      ...businessResults.filter(r => r.passes)
    ].length;
    
    return {
      summary: {
        total: totalTests,
        passed: passedTests,
        failed: totalTests - passedTests,
        passRate: Math.round((passedTests / totalTests) * 100),
      },
      semanticResults,
      businessResults,
      recommendations: colorA11yUtils.getRecommendations(semanticResults, businessResults),
    };
  },

  // Get accessibility recommendations
  getRecommendations: (semanticResults: any[], businessResults: any[]) => {
    const recommendations: string[] = [];
    
    const failedSemantic = semanticResults.filter(r => !r.passes);
    const failedBusiness = businessResults.filter(r => !r.passes);
    
    if (failedSemantic.length > 0) {
      recommendations.push(`${failedSemantic.length} semantic color combinations need improvement for WCAG AA compliance.`);
    }
    
    if (failedBusiness.length > 0) {
      recommendations.push(`${failedBusiness.length} Polish business color combinations need contrast adjustments.`);
    }
    
    if (failedSemantic.length === 0 && failedBusiness.length === 0) {
      recommendations.push('All color combinations meet WCAG AA accessibility standards! 🎉');
    }
    
    return recommendations;
  },
} as const;

// Export all utilities
export { polishBusinessColors, colorAccessibility };
export default colorUtils;