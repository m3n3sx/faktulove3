// Design System Tokens Tests
import { colors, typography, spacing, breakpoints, shadows, borderRadius } from '../tokens';
import { designSystemConfig } from '../config';
import { theme } from '../utils/theme';

describe('Design System Tokens', () => {
  describe('Colors', () => {
    it('should have all required color scales', () => {
      expect(colors.primary).toBeDefined();
      expect(colors.secondary).toBeDefined();
      expect(colors.success).toBeDefined();
      expect(colors.warning).toBeDefined();
      expect(colors.error).toBeDefined();
      expect(colors.neutral).toBeDefined();
    });

    it('should have correct primary brand color', () => {
      expect(colors.primary[600]).toBe('#2563eb');
    });

    it('should have correct success color for Polish business', () => {
      expect(colors.success[600]).toBe('#059669');
    });

    it('should have correct warning color for Polish business', () => {
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

  describe('Typography', () => {
    it('should have Inter font family with Polish character support', () => {
      expect(typography.fontFamily.sans[0]).toBe('Inter');
    });

    it('should have complete font size scale', () => {
      expect(typography.fontSize.xs).toBe('0.75rem');
      expect(typography.fontSize.sm).toBe('0.875rem');
      expect(typography.fontSize.base).toBe('1rem');
      expect(typography.fontSize.lg).toBe('1.125rem');
      expect(typography.fontSize.xl).toBe('1.25rem');
      expect(typography.fontSize['2xl']).toBe('1.5rem');
      expect(typography.fontSize['3xl']).toBe('1.875rem');
      expect(typography.fontSize['4xl']).toBe('2.25rem');
      expect(typography.fontSize['5xl']).toBe('3rem');
      expect(typography.fontSize['6xl']).toBe('3.75rem');
    });

    it('should have complete font weight scale', () => {
      expect(typography.fontWeight.thin).toBe(100);
      expect(typography.fontWeight.normal).toBe(400);
      expect(typography.fontWeight.medium).toBe(500);
      expect(typography.fontWeight.semibold).toBe(600);
      expect(typography.fontWeight.bold).toBe(700);
      expect(typography.fontWeight.black).toBe(900);
    });
  });

  describe('Spacing', () => {
    it('should follow 8px grid system', () => {
      expect(spacing[2]).toBe('0.5rem'); // 8px base unit
      expect(spacing[4]).toBe('1rem');   // 16px - 2x base
      expect(spacing[6]).toBe('1.5rem'); // 24px - 3x base
      expect(spacing[8]).toBe('2rem');   // 32px - 4x base
    });

    it('should have complete spacing scale', () => {
      expect(spacing[0]).toBe('0px');
      expect(spacing.px).toBe('1px');
      expect(spacing[96]).toBe('24rem');
    });
  });

  describe('Breakpoints', () => {
    it('should have responsive breakpoints for Polish business apps', () => {
      expect(breakpoints.xs).toBe('475px');
      expect(breakpoints.sm).toBe('640px');
      expect(breakpoints.md).toBe('768px');
      expect(breakpoints.lg).toBe('1024px');
      expect(breakpoints.xl).toBe('1280px');
      expect(breakpoints['2xl']).toBe('1536px');
    });
  });

  describe('Shadows', () => {
    it('should have elevation system', () => {
      expect(shadows.none).toBe('none');
      expect(shadows.xs).toBeDefined();
      expect(shadows.sm).toBeDefined();
      expect(shadows.md).toBeDefined();
      expect(shadows.lg).toBeDefined();
      expect(shadows.xl).toBeDefined();
      expect(shadows['2xl']).toBeDefined();
      expect(shadows.inner).toBeDefined();
    });
  });

  describe('Border Radius', () => {
    it('should have consistent border radius scale', () => {
      expect(borderRadius.none).toBe('0px');
      expect(borderRadius.xs).toBe('0.125rem');
      expect(borderRadius.sm).toBe('0.25rem');
      expect(borderRadius.md).toBe('0.375rem');
      expect(borderRadius.lg).toBe('0.5rem');
      expect(borderRadius.xl).toBe('0.75rem');
      expect(borderRadius['2xl']).toBe('1rem');
      expect(borderRadius['3xl']).toBe('1.5rem');
      expect(borderRadius.full).toBe('9999px');
    });
  });
});

describe('Design System Configuration', () => {
  it('should have correct version', () => {
    expect(designSystemConfig.version).toBe('1.0.0');
  });

  it('should have Polish business context', () => {
    expect(designSystemConfig.polish.currency.symbol).toBe('zł');
    expect(designSystemConfig.polish.currency.code).toBe('PLN');
    expect(designSystemConfig.polish.date.locale).toBe('pl-PL');
    expect(designSystemConfig.polish.date.format).toBe('DD.MM.YYYY');
  });

  it('should have VAT rates for Polish business', () => {
    const vatRates = designSystemConfig.polish.vatRates;
    expect(vatRates).toContainEqual({ value: 0.23, label: '23%' });
    expect(vatRates).toContainEqual({ value: 0.08, label: '8%' });
    expect(vatRates).toContainEqual({ value: 0.05, label: '5%' });
    expect(vatRates).toContainEqual({ value: 0, label: '0%' });
    expect(vatRates).toContainEqual({ value: -1, label: 'zw.' });
  });

  it('should have invoice statuses in Polish', () => {
    const statuses = designSystemConfig.polish.invoiceStatuses;
    expect(statuses.draft.label).toBe('Szkic');
    expect(statuses.sent.label).toBe('Wysłana');
    expect(statuses.paid.label).toBe('Opłacona');
    expect(statuses.overdue.label).toBe('Przeterminowana');
    expect(statuses.cancelled.label).toBe('Anulowana');
  });

  it('should have accessibility configuration', () => {
    expect(designSystemConfig.accessibility.wcagLevel).toBe('AA');
    expect(designSystemConfig.accessibility.contrastRatios.normal).toBe(4.5);
    expect(designSystemConfig.accessibility.screenReader.locale).toBe('pl-PL');
  });
});

describe('Theme Utilities', () => {
  it('should provide complete theme object', () => {
    expect(theme.colors).toBeDefined();
    expect(theme.typography).toBeDefined();
    expect(theme.spacing).toBeDefined();
    expect(theme.breakpoints).toBeDefined();
    expect(theme.shadows).toBeDefined();
    expect(theme.borderRadius).toBeDefined();
  });

  it('should have semantic tokens', () => {
    expect(theme.semanticColors).toBeDefined();
    expect(theme.semanticSpacing).toBeDefined();
    expect(theme.semanticShadows).toBeDefined();
    expect(theme.semanticBorderRadius).toBeDefined();
  });
});