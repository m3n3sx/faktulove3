// Typography Utility Functions
import { typography, typographyStyles, responsiveTypography, polishTypographyUtils } from '../tokens/typography';

// Typography utility functions
export const typographyUtils = {
  // Get font size in pixels
  getFontSizeInPixels: (fontSize: string): number => {
    if (fontSize.endsWith('rem')) {
      return parseFloat(fontSize) * 16; // Assuming 1rem = 16px
    }
    if (fontSize.endsWith('px')) {
      return parseFloat(fontSize);
    }
    return 16; // Default fallback
  },

  // Get optimal line height for font size
  getOptimalLineHeight: (fontSize: string, context: 'heading' | 'body' | 'ui' = 'body'): number => {
    const sizeInPx = typographyUtils.getFontSizeInPixels(fontSize);
    
    switch (context) {
      case 'heading':
        if (sizeInPx >= 32) return 1.2;
        if (sizeInPx >= 24) return 1.25;
        return 1.3;
      case 'ui':
        return 1.4;
      case 'body':
      default:
        if (sizeInPx <= 14) return 1.6;
        if (sizeInPx <= 18) return 1.5;
        return 1.4;
    }
  },

  // Calculate reading time for Polish text
  calculateReadingTime: (text: string, wordsPerMinute: number = 200): number => {
    // Polish text typically has longer words, so adjust WPM
    const polishAdjustedWPM = wordsPerMinute * 0.85;
    const words = text.trim().split(/\s+/).length;
    return Math.ceil(words / polishAdjustedWPM);
  },

  // Get text contrast requirements
  getContrastRequirements: (fontSize: string, fontWeight: number): { normal: number; enhanced: number } => {
    const sizeInPx = typographyUtils.getFontSizeInPixels(fontSize);
    const isLargeText = sizeInPx >= 18 || (sizeInPx >= 14 && fontWeight >= 700);
    
    return {
      normal: isLargeText ? 3 : 4.5,
      enhanced: isLargeText ? 4.5 : 7,
    };
  },

  // Generate CSS for typography style
  generateTypographyCSS: (styleKey: keyof typeof typographyStyles): React.CSSProperties => {
    const style = typographyStyles[styleKey];
    return {
      fontSize: style.fontSize,
      fontWeight: style.fontWeight,
      lineHeight: style.lineHeight,
      fontFamily: style.fontFamily,
      letterSpacing: (style as any).letterSpacing,
      textTransform: (style as any).textTransform,
      textAlign: (style as any).textAlign,
      fontVariantNumeric: (style as any).fontVariantNumeric,
      textDecoration: (style as any).textDecoration,
      textDecorationColor: (style as any).textDecorationColor,
    };
  },

  // Get responsive typography CSS
  generateResponsiveCSS: (styleKey: keyof typeof responsiveTypography): Record<string, any> => {
    return responsiveTypography[styleKey];
  },
} as const;

// Polish business typography utilities
export const polishBusinessTypography = {
  // Format Polish currency for display
  formatCurrency: (amount: number, options?: {
    showSymbol?: boolean;
    decimals?: number;
    locale?: string;
  }): string => {
    const { showSymbol = true, decimals = 2, locale = 'pl-PL' } = options || {};
    
    const formatted = new Intl.NumberFormat(locale, {
      style: showSymbol ? 'currency' : 'decimal',
      currency: 'PLN',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(amount);
    
    return formatted;
  },

  // Format Polish date for display
  formatDate: (date: Date | string, format: 'short' | 'long' | 'numeric' = 'numeric'): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    const formatOptions: Record<'short' | 'long' | 'numeric', Intl.DateTimeFormatOptions> = {
      short: { day: '2-digit', month: '2-digit', year: 'numeric' },
      long: { day: 'numeric', month: 'long', year: 'numeric' },
      numeric: { day: '2-digit', month: '2-digit', year: 'numeric' },
    };
    
    return new Intl.DateTimeFormat('pl-PL', formatOptions[format]).format(dateObj);
  },

  // Format NIP number with proper spacing
  formatNIP: (nip: string): string => {
    const cleanNip = nip.replace(/\D/g, '');
    if (cleanNip.length !== 10) return nip;
    
    return `${cleanNip.slice(0, 3)}-${cleanNip.slice(3, 6)}-${cleanNip.slice(6, 8)}-${cleanNip.slice(8)}`;
  },

  // Format REGON number
  formatREGON: (regon: string): string => {
    const cleanRegon = regon.replace(/\D/g, '');
    if (cleanRegon.length === 9) {
      return `${cleanRegon.slice(0, 3)}-${cleanRegon.slice(3, 6)}-${cleanRegon.slice(6)}`;
    }
    if (cleanRegon.length === 14) {
      return `${cleanRegon.slice(0, 3)}-${cleanRegon.slice(3, 6)}-${cleanRegon.slice(6, 8)}-${cleanRegon.slice(8)}`;
    }
    return regon;
  },

  // Format Polish postal code
  formatPostalCode: (code: string): string => {
    const cleanCode = code.replace(/\D/g, '');
    if (cleanCode.length !== 5) return code;
    
    return `${cleanCode.slice(0, 2)}-${cleanCode.slice(2)}`;
  },

  // Get invoice status display text
  getInvoiceStatusText: (status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'): string => {
    const statusMap = {
      draft: 'Szkic',
      sent: 'Wysłana',
      paid: 'Opłacona',
      overdue: 'Przeterminowana',
      cancelled: 'Anulowana',
    };
    return statusMap[status];
  },

  // Get VAT rate display text
  getVATRateText: (rate: number): string => {
    if (rate === -1) return 'zw.'; // zwolniony (exempt)
    if (rate === 0) return '0%';
    return `${Math.round(rate * 100)}%`;
  },

  // Format Polish phone number
  formatPhoneNumber: (phone: string): string => {
    const cleanPhone = phone.replace(/\D/g, '');
    
    if (cleanPhone.length === 9) {
      return `${cleanPhone.slice(0, 3)} ${cleanPhone.slice(3, 6)} ${cleanPhone.slice(6)}`;
    }
    if (cleanPhone.length === 11 && cleanPhone.startsWith('48')) {
      return `+48 ${cleanPhone.slice(2, 5)} ${cleanPhone.slice(5, 8)} ${cleanPhone.slice(8)}`;
    }
    
    return phone;
  },

  // Get appropriate text size for content length
  getTextSizeForContent: (content: string, context: 'title' | 'body' | 'caption' = 'body'): keyof typeof typography.fontSize => {
    const length = content.length;
    
    switch (context) {
      case 'title':
        if (length > 50) return 'xl';
        if (length > 30) return '2xl';
        return '3xl';
      case 'caption':
        return 'xs';
      case 'body':
      default:
        if (length > 200) return 'sm';
        return 'base';
    }
  },

  // Check if text needs truncation
  needsTruncation: (text: string, maxLength: number): boolean => {
    return text.length > maxLength;
  },

  // Truncate text with Polish-aware word boundaries
  truncateText: (text: string, maxLength: number, suffix: string = '...'): string => {
    if (text.length <= maxLength) return text;
    
    const truncated = text.slice(0, maxLength - suffix.length);
    const lastSpace = truncated.lastIndexOf(' ');
    
    // If we can break at a word boundary, do so
    if (lastSpace > maxLength * 0.7) {
      return truncated.slice(0, lastSpace) + suffix;
    }
    
    return truncated + suffix;
  },

  // Get text metrics for layout calculations
  getTextMetrics: (text: string, fontSize: string, fontFamily: string): {
    estimatedWidth: number;
    estimatedHeight: number;
    lineCount: number;
  } => {
    // Simplified estimation - in production, use canvas measurement
    const avgCharWidth = typographyUtils.getFontSizeInPixels(fontSize) * 0.6;
    const lineHeight = typographyUtils.getFontSizeInPixels(fontSize) * 1.5;
    
    const estimatedWidth = text.length * avgCharWidth;
    const lineCount = Math.ceil(text.length / 50); // Rough estimate
    const estimatedHeight = lineCount * lineHeight;
    
    return {
      estimatedWidth,
      estimatedHeight,
      lineCount,
    };
  },
} as const;

// Typography accessibility utilities
export const typographyA11yUtils = {
  // Check if font size meets accessibility requirements
  meetsFontSizeRequirements: (fontSize: string, context: 'body' | 'ui' | 'caption' = 'body'): boolean => {
    const sizeInPx = typographyUtils.getFontSizeInPixels(fontSize);
    
    switch (context) {
      case 'body':
        return sizeInPx >= 16; // WCAG recommendation
      case 'ui':
        return sizeInPx >= 14; // Minimum for UI elements
      case 'caption':
        return sizeInPx >= 12; // Minimum for captions
      default:
        return sizeInPx >= 16;
    }
  },

  // Get ARIA label for formatted content
  getAriaLabel: (content: string, type: 'currency' | 'date' | 'nip' | 'phone' | 'status' | 'text' = 'text'): string => {
    switch (type) {
      case 'currency':
        const amount = parseFloat(content.replace(/[^\d,.-]/g, '').replace(',', '.'));
        return `${amount.toFixed(2).replace('.', ',')} złotych`;
      case 'date':
        const date = new Date(content);
        return date.toLocaleDateString('pl-PL', { 
          day: 'numeric', 
          month: 'long', 
          year: 'numeric' 
        });
      case 'nip':
        return `NIP ${content.replace(/\D/g, '').split('').join(' ')}`;
      case 'phone':
        return `telefon ${content.replace(/\D/g, '').split('').join(' ')}`;
      case 'status':
        return content; // Status is already human-readable
      default:
        return content;
    }
  },

  // Generate screen reader friendly text
  generateScreenReaderText: (
    content: string, 
    context: {
      type?: 'currency' | 'date' | 'nip' | 'phone' | 'status' | 'text';
      prefix?: string;
      suffix?: string;
    } = {}
  ): string => {
    const { type = 'text', prefix = '', suffix = '' } = context;
    
    let screenReaderText = typographyA11yUtils.getAriaLabel(content, type);
    
    if (prefix) screenReaderText = `${prefix} ${screenReaderText}`;
    if (suffix) screenReaderText = `${screenReaderText} ${suffix}`;
    
    return screenReaderText;
  },

  // Check line height accessibility
  meetsLineHeightRequirements: (lineHeight: number | string): boolean => {
    const numericLineHeight = typeof lineHeight === 'string' 
      ? parseFloat(lineHeight) 
      : lineHeight;
    
    return numericLineHeight >= 1.5; // WCAG 2.1 requirement
  },

  // Get recommended line height for font size
  getRecommendedLineHeight: (fontSize: string): number => {
    return polishTypographyUtils.getPolishLineHeight(fontSize);
  },
} as const;

// Export all utilities
export { polishTypographyUtils };
export default typographyUtils;