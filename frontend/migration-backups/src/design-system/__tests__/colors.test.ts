// Color System Tests
import { 
  colors, 
  semanticColors, 
  polishBusinessColors, 
  colorAccessibility 
} from '../tokens/colors';
import { 
  colorUtils, 
  polishColorUtils, 
  colorA11yUtils 
} from '../utils/colorUtils';

describe('Color System', () => {
  describe('Color Tokens', () => {
    it('should have all required color scales', () => {
      expect(colors.primary).toBeDefined();
      expect(colors.secondary).toBeDefined();
      expect(colors.success).toBeDefined();
      expect(colors.warning).toBeDefined();
      expect(colors.error).toBeDefined();
      expect(colors.neutral).toBeDefined();
    });

    it('should have correct Polish business brand colors', () => {
      expect(colors.primary[600]).toBe('#2563eb');
      expect(colors.success[600]).toBe('#059669');
      expect(colors.warning[600]).toBe('#d97706');
    });

    it('should have complete color scales (50-900)', () => {
      Object.values(colors).forEach(colorScale => {
        expect(colorScale[50]).toBeDefined();
        expect(colorScale[100]).toBeDefined();
        expect(colorScale[200]).toBeDefined();
        expect(colorScale[300]).toBeDefined();
        expect(colorScale[400]).toBeDefined();
        expect(colorScale[500]).toBeDefined();
        expect(colorScale[600]).toBeDefined();
        expect(colorScale[700]).toBeDefined();
        expect(colorScale[800]).toBeDefined();
        expect(colorScale[900]).toBeDefined();
      });
    });
  });

  describe('Semantic Colors', () => {
    it('should have comprehensive text color mappings', () => {
      expect(semanticColors.textPrimary).toBeDefined();
      expect(semanticColors.textSecondary).toBeDefined();
      expect(semanticColors.textMuted).toBeDefined();
      expect(semanticColors.textInverse).toBeDefined();
      expect(semanticColors.textDisabled).toBeDefined();
      expect(semanticColors.textLink).toBeDefined();
    });

    it('should have comprehensive background color mappings', () => {
      expect(semanticColors.backgroundPrimary).toBeDefined();
      expect(semanticColors.backgroundSecondary).toBeDefined();
      expect(semanticColors.backgroundMuted).toBeDefined();
      expect(semanticColors.backgroundOverlay).toBeDefined();
      expect(semanticColors.backgroundDisabled).toBeDefined();
    });

    it('should have comprehensive border color mappings', () => {
      expect(semanticColors.borderDefault).toBeDefined();
      expect(semanticColors.borderMuted).toBeDefined();
      expect(semanticColors.borderStrong).toBeDefined();
      expect(semanticColors.borderFocus).toBeDefined();
      expect(semanticColors.borderError).toBeDefined();
    });

    it('should have interactive color states', () => {
      expect(semanticColors.interactive).toBeDefined();
      expect(semanticColors.interactiveHover).toBeDefined();
      expect(semanticColors.interactiveActive).toBeDefined();
      expect(semanticColors.interactiveDisabled).toBeDefined();
    });

    it('should have status colors with backgrounds and borders', () => {
      expect(semanticColors.statusSuccess).toBeDefined();
      expect(semanticColors.statusSuccessBackground).toBeDefined();
      expect(semanticColors.statusSuccessBorder).toBeDefined();
      expect(semanticColors.statusWarning).toBeDefined();
      expect(semanticColors.statusError).toBeDefined();
      expect(semanticColors.statusInfo).toBeDefined();
    });
  });

  describe('Polish Business Colors', () => {
    it('should have invoice status colors', () => {
      expect(semanticColors.invoiceDraft).toBeDefined();
      expect(semanticColors.invoiceSent).toBeDefined();
      expect(semanticColors.invoicePaid).toBeDefined();
      expect(semanticColors.invoiceOverdue).toBeDefined();
      expect(semanticColors.invoiceCancelled).toBeDefined();
    });

    it('should have VAT rate colors', () => {
      expect(semanticColors.vatStandard).toBeDefined();
      expect(semanticColors.vatReduced).toBeDefined();
      expect(semanticColors.vatZero).toBeDefined();
      expect(semanticColors.vatExempt).toBeDefined();
    });

    it('should have currency colors', () => {
      expect(semanticColors.currencyPositive).toBeDefined();
      expect(semanticColors.currencyNegative).toBeDefined();
      expect(semanticColors.currencyNeutral).toBeDefined();
    });

    it('should have form validation colors', () => {
      expect(semanticColors.formValid).toBeDefined();
      expect(semanticColors.formInvalid).toBeDefined();
      expect(semanticColors.formPending).toBeDefined();
    });
  });

  describe('Polish Business Color Functions', () => {
    it('should return correct invoice status colors', () => {
      expect(polishBusinessColors.getInvoiceStatusColor('draft')).toBe(semanticColors.invoiceDraft);
      expect(polishBusinessColors.getInvoiceStatusColor('sent')).toBe(semanticColors.invoiceSent);
      expect(polishBusinessColors.getInvoiceStatusColor('paid')).toBe(semanticColors.invoicePaid);
      expect(polishBusinessColors.getInvoiceStatusColor('overdue')).toBe(semanticColors.invoiceOverdue);
      expect(polishBusinessColors.getInvoiceStatusColor('cancelled')).toBe(semanticColors.invoiceCancelled);
    });

    it('should return correct VAT rate colors', () => {
      expect(polishBusinessColors.getVATRateColor(0.23)).toBe(semanticColors.vatStandard);
      expect(polishBusinessColors.getVATRateColor(0.08)).toBe(semanticColors.vatReduced);
      expect(polishBusinessColors.getVATRateColor(0.05)).toBe(semanticColors.vatReduced);
      expect(polishBusinessColors.getVATRateColor(0)).toBe(semanticColors.vatZero);
      expect(polishBusinessColors.getVATRateColor(-1)).toBe(semanticColors.vatExempt);
    });

    it('should return correct currency colors', () => {
      expect(polishBusinessColors.getCurrencyColor(100)).toBe(semanticColors.currencyPositive);
      expect(polishBusinessColors.getCurrencyColor(-100)).toBe(semanticColors.currencyNegative);
      expect(polishBusinessColors.getCurrencyColor(0)).toBe(semanticColors.currencyNeutral);
    });

    it('should return correct validation colors', () => {
      expect(polishBusinessColors.getValidationColor('valid')).toBe(semanticColors.formValid);
      expect(polishBusinessColors.getValidationColor('invalid')).toBe(semanticColors.formInvalid);
      expect(polishBusinessColors.getValidationColor('pending')).toBe(semanticColors.formPending);
    });
  });

  describe('Color Utilities', () => {
    it('should convert hex to RGB correctly', () => {
      const rgb = colorUtils.hexToRgb('#2563eb');
      expect(rgb).toEqual({ r: 37, g: 99, b: 235 });
    });

    it('should convert RGB to hex correctly', () => {
      const hex = colorUtils.rgbToHex(37, 99, 235);
      expect(hex).toBe('#2563eb');
    });

    it('should calculate luminance correctly', () => {
      const whiteLuminance = colorUtils.getLuminance('#ffffff');
      const blackLuminance = colorUtils.getLuminance('#000000');
      expect(whiteLuminance).toBeGreaterThan(blackLuminance);
    });

    it('should calculate contrast ratio correctly', () => {
      const contrast = colorUtils.getContrastRatio('#ffffff', '#000000');
      expect(contrast).toBe(21); // Maximum contrast ratio
    });

    it('should check WCAG compliance correctly', () => {
      const highContrast = colorUtils.meetsWCAG('#000000', '#ffffff');
      const lowContrast = colorUtils.meetsWCAG('#888888', '#999999');
      expect(highContrast).toBe(true);
      expect(lowContrast).toBe(false);
    });

    it('should get accessible text color', () => {
      const textOnWhite = colorUtils.getAccessibleTextColor('#ffffff');
      const textOnBlack = colorUtils.getAccessibleTextColor('#000000');
      expect(textOnWhite).toBe('#000000');
      expect(textOnBlack).toBe('#ffffff');
    });

    it('should lighten colors correctly', () => {
      const lightened = colorUtils.lighten('#2563eb', 20);
      expect(lightened).toBeDefined();
      expect(lightened).not.toBe('#2563eb');
    });

    it('should darken colors correctly', () => {
      const darkened = colorUtils.darken('#2563eb', 20);
      expect(darkened).toBeDefined();
      expect(darkened).not.toBe('#2563eb');
    });

    it('should add alpha to colors', () => {
      const withAlpha = colorUtils.addAlpha('#2563eb', 0.5);
      expect(withAlpha).toMatch(/^rgba\(\d+, \d+, \d+, 0\.5\)$/);
    });
  });

  describe('Polish Color Utilities', () => {
    it('should get invoice status colors with proper structure', () => {
      const colors = polishColorUtils.getInvoiceStatusColors('paid');
      expect(colors).toHaveProperty('color');
      expect(colors).toHaveProperty('backgroundColor');
      expect(colors).toHaveProperty('borderColor');
      expect(colors).toHaveProperty('textColor');
    });

    it('should get VAT rate colors with proper structure', () => {
      const colors = polishColorUtils.getVATRateColors(0.23);
      expect(colors).toHaveProperty('color');
      expect(colors).toHaveProperty('backgroundColor');
      expect(colors).toHaveProperty('borderColor');
      expect(colors).toHaveProperty('textColor');
    });

    it('should get currency colors with proper structure', () => {
      const colors = polishColorUtils.getCurrencyColors(1000);
      expect(colors).toHaveProperty('color');
      expect(colors).toHaveProperty('backgroundColor');
      expect(colors).toHaveProperty('textColor');
    });

    it('should get validation colors with proper structure', () => {
      const colors = polishColorUtils.getValidationColors('valid');
      expect(colors).toHaveProperty('color');
      expect(colors).toHaveProperty('backgroundColor');
      expect(colors).toHaveProperty('borderColor');
      expect(colors).toHaveProperty('textColor');
    });

    it('should provide chart colors array', () => {
      const chartColors = polishColorUtils.getChartColors();
      expect(Array.isArray(chartColors)).toBe(true);
      expect(chartColors.length).toBeGreaterThan(0);
    });

    it('should provide document colors with proper structure', () => {
      const docColors = polishColorUtils.getDocumentColors();
      expect(docColors).toHaveProperty('header');
      expect(docColors).toHaveProperty('body');
      expect(docColors).toHaveProperty('footer');
      expect(docColors).toHaveProperty('table');
    });
  });

  describe('Color Accessibility', () => {
    it('should have accessibility configuration', () => {
      expect(colorAccessibility.contrastRatios).toBeDefined();
      expect(colorAccessibility.contrastRatios.AA_NORMAL).toBe(4.5);
      expect(colorAccessibility.contrastRatios.AAA_NORMAL).toBe(7);
    });

    it('should have high contrast pairs', () => {
      expect(colorAccessibility.highContrastPairs).toBeDefined();
      expect(colorAccessibility.highContrastPairs.textOnLight).toBeDefined();
      expect(colorAccessibility.highContrastPairs.textOnDark).toBeDefined();
    });

    it('should have Polish business combinations', () => {
      expect(colorAccessibility.polishBusinessCombinations).toBeDefined();
      expect(colorAccessibility.polishBusinessCombinations.invoiceHeader).toBeDefined();
      expect(colorAccessibility.polishBusinessCombinations.formField).toBeDefined();
    });
  });

  describe('Color Accessibility Testing', () => {
    it('should test semantic colors', () => {
      const results = colorA11yUtils.testSemanticColors();
      expect(Array.isArray(results)).toBe(true);
      expect(results.length).toBeGreaterThan(0);
      
      results.forEach(result => {
        expect(result).toHaveProperty('combination');
        expect(result).toHaveProperty('contrast');
        expect(result).toHaveProperty('passes');
        expect(result).toHaveProperty('level');
      });
    });

    it('should test Polish business colors', () => {
      const results = colorA11yUtils.testPolishBusinessColors();
      expect(Array.isArray(results)).toBe(true);
      expect(results.length).toBeGreaterThan(0);
      
      results.forEach(result => {
        expect(result).toHaveProperty('context');
        expect(result).toHaveProperty('combination');
        expect(result).toHaveProperty('contrast');
        expect(result).toHaveProperty('passes');
      });
    });

    it('should generate accessibility report', () => {
      const report = colorA11yUtils.generateA11yReport();
      expect(report).toHaveProperty('summary');
      expect(report).toHaveProperty('semanticResults');
      expect(report).toHaveProperty('businessResults');
      expect(report).toHaveProperty('recommendations');
      
      expect(report.summary).toHaveProperty('total');
      expect(report.summary).toHaveProperty('passed');
      expect(report.summary).toHaveProperty('failed');
      expect(report.summary).toHaveProperty('passRate');
    });

    it('should provide recommendations', () => {
      const report = colorA11yUtils.generateA11yReport();
      expect(Array.isArray(report.recommendations)).toBe(true);
      expect(report.recommendations.length).toBeGreaterThan(0);
    });
  });

  describe('Integration with Design System', () => {
    it('should integrate with semantic colors', () => {
      // Test that all semantic colors are valid hex colors
      Object.values(semanticColors).forEach(color => {
        if (typeof color === 'string' && color.startsWith('#')) {
          expect(colorUtils.hexToRgb(color)).not.toBeNull();
        }
      });
    });

    it('should provide consistent color naming', () => {
      // Test that color names follow consistent patterns
      const semanticKeys = Object.keys(semanticColors);
      const textColors = semanticKeys.filter(key => key.startsWith('text'));
      const backgroundColors = semanticKeys.filter(key => key.startsWith('background'));
      const borderColors = semanticKeys.filter(key => key.startsWith('border'));
      
      expect(textColors.length).toBeGreaterThan(0);
      expect(backgroundColors.length).toBeGreaterThan(0);
      expect(borderColors.length).toBeGreaterThan(0);
    });
  });
});