// Typography System Tests
import { 
  typography, 
  typographyStyles, 
  responsiveTypography, 
  polishTypographyUtils 
} from '../tokens/typography';
import { 
  typographyUtils, 
  polishBusinessTypography, 
  typographyA11yUtils 
} from '../utils/typographyUtils';

describe('Typography System', () => {
  describe('Typography Tokens', () => {
    it('should have Inter font family with Polish character support', () => {
      expect(typography.fontFamily.sans[0]).toBe('Inter');
      expect(typography.fontFamily.sans).toContain('-apple-system');
      expect(typography.fontFamily.sans).toContain('BlinkMacSystemFont');
    });

    it('should have complete font size scale following 8px grid', () => {
      expect(typography.fontSize.xs).toBe('0.75rem');    // 12px
      expect(typography.fontSize.sm).toBe('0.875rem');   // 14px
      expect(typography.fontSize.base).toBe('1rem');     // 16px
      expect(typography.fontSize.lg).toBe('1.125rem');   // 18px
      expect(typography.fontSize.xl).toBe('1.25rem');    // 20px
      expect(typography.fontSize['2xl']).toBe('1.5rem'); // 24px
      expect(typography.fontSize['3xl']).toBe('1.875rem'); // 30px
      expect(typography.fontSize['4xl']).toBe('2.25rem'); // 36px
      expect(typography.fontSize['5xl']).toBe('3rem');   // 48px
      expect(typography.fontSize['6xl']).toBe('3.75rem'); // 60px
    });

    it('should have complete font weight scale', () => {
      expect(typography.fontWeight.thin).toBe(100);
      expect(typography.fontWeight.extralight).toBe(200);
      expect(typography.fontWeight.light).toBe(300);
      expect(typography.fontWeight.normal).toBe(400);
      expect(typography.fontWeight.medium).toBe(500);
      expect(typography.fontWeight.semibold).toBe(600);
      expect(typography.fontWeight.bold).toBe(700);
      expect(typography.fontWeight.extrabold).toBe(800);
      expect(typography.fontWeight.black).toBe(900);
    });

    it('should have appropriate line height scale', () => {
      expect(typography.lineHeight.none).toBe(1);
      expect(typography.lineHeight.tight).toBe(1.25);
      expect(typography.lineHeight.snug).toBe(1.375);
      expect(typography.lineHeight.normal).toBe(1.5);
      expect(typography.lineHeight.relaxed).toBe(1.625);
      expect(typography.lineHeight.loose).toBe(2);
    });
  });

  describe('Typography Styles', () => {
    it('should have complete heading hierarchy', () => {
      expect(typographyStyles.h1).toBeDefined();
      expect(typographyStyles.h2).toBeDefined();
      expect(typographyStyles.h3).toBeDefined();
      expect(typographyStyles.h4).toBeDefined();
      expect(typographyStyles.h5).toBeDefined();
      expect(typographyStyles.h6).toBeDefined();
    });

    it('should have body text variations', () => {
      expect(typographyStyles.bodyLarge).toBeDefined();
      expect(typographyStyles.body).toBeDefined();
      expect(typographyStyles.bodySmall).toBeDefined();
    });

    it('should have UI text styles', () => {
      expect(typographyStyles.caption).toBeDefined();
      expect(typographyStyles.label).toBeDefined();
      expect(typographyStyles.button).toBeDefined();
      expect(typographyStyles.link).toBeDefined();
    });

    it('should have code styles', () => {
      expect(typographyStyles.code).toBeDefined();
      expect(typographyStyles.codeBlock).toBeDefined();
    });

    it('should have Polish business specific styles', () => {
      expect(typographyStyles.invoiceTitle).toBeDefined();
      expect(typographyStyles.invoiceNumber).toBeDefined();
      expect(typographyStyles.companyName).toBeDefined();
      expect(typographyStyles.contractorName).toBeDefined();
      expect(typographyStyles.currencyAmount).toBeDefined();
      expect(typographyStyles.currencyAmountLarge).toBeDefined();
      expect(typographyStyles.dateFormat).toBeDefined();
      expect(typographyStyles.nipFormat).toBeDefined();
      expect(typographyStyles.vatRate).toBeDefined();
      expect(typographyStyles.statusBadge).toBeDefined();
    });

    it('should have form-related styles', () => {
      expect(typographyStyles.formLabel).toBeDefined();
      expect(typographyStyles.formHelperText).toBeDefined();
      expect(typographyStyles.formErrorText).toBeDefined();
    });

    it('should have table styles', () => {
      expect(typographyStyles.tableHeader).toBeDefined();
      expect(typographyStyles.tableCell).toBeDefined();
    });
  });

  describe('Responsive Typography', () => {
    it('should have responsive heading styles', () => {
      expect(responsiveTypography.h1Responsive).toBeDefined();
      expect(responsiveTypography.h2Responsive).toBeDefined();
      expect(responsiveTypography.h3Responsive).toBeDefined();
    });

    it('should have responsive body text', () => {
      expect(responsiveTypography.bodyResponsive).toBeDefined();
    });

    it('should have responsive Polish business elements', () => {
      expect(responsiveTypography.invoiceTitleResponsive).toBeDefined();
      expect(responsiveTypography.currencyResponsive).toBeDefined();
    });
  });

  describe('Polish Typography Utils', () => {
    it('should support Polish character detection', () => {
      expect(polishTypographyUtils.supportsPolishChars(['Inter'])).toBe(true);
    });

    it('should have Polish text formatting rules', () => {
      expect(polishTypographyUtils.polishTextRules.quotationMarks.primary).toBe('„"');
      expect(polishTypographyUtils.polishTextRules.decimalSeparator).toBe(',');
      expect(polishTypographyUtils.polishTextRules.thousandSeparator).toBe(' ');
      expect(polishTypographyUtils.polishTextRules.dateFormat).toBe('DD.MM.YYYY');
      expect(polishTypographyUtils.polishTextRules.currencyFormat).toBe('0,00 zł');
    });

    it('should account for Polish text expansion', () => {
      expect(polishTypographyUtils.polishTextLengths.expansionFactor).toBe(1.25);
    });

    it('should provide appropriate line height for Polish text', () => {
      const smallTextLineHeight = polishTypographyUtils.getPolishLineHeight('12px');
      const mediumTextLineHeight = polishTypographyUtils.getPolishLineHeight('16px');
      const largeTextLineHeight = polishTypographyUtils.getPolishLineHeight('24px');
      
      expect(smallTextLineHeight).toBe(1.6);
      expect(mediumTextLineHeight).toBe(1.5);
      expect(largeTextLineHeight).toBe(1.4);
    });

    it('should format Polish currency correctly', () => {
      const formatted = polishTypographyUtils.formatPolishCurrency(1234.56);
      expect(formatted).toMatch(/1[\s,]234[,.]56.*zł/);
    });

    it('should format Polish date correctly', () => {
      const date = new Date('2025-01-15');
      const formatted = polishTypographyUtils.formatPolishDate(date);
      expect(formatted).toBe('15.01.2025');
    });

    it('should format Polish number correctly', () => {
      const formatted = polishTypographyUtils.formatPolishNumber(1234567);
      expect(formatted).toMatch(/1[\s]234[\s]567/);
    });
  });

  describe('Typography Utilities', () => {
    it('should convert font sizes to pixels correctly', () => {
      expect(typographyUtils.getFontSizeInPixels('1rem')).toBe(16);
      expect(typographyUtils.getFontSizeInPixels('1.5rem')).toBe(24);
      expect(typographyUtils.getFontSizeInPixels('18px')).toBe(18);
    });

    it('should calculate optimal line height', () => {
      const headingLineHeight = typographyUtils.getOptimalLineHeight('2rem', 'heading');
      const bodyLineHeight = typographyUtils.getOptimalLineHeight('1rem', 'body');
      const uiLineHeight = typographyUtils.getOptimalLineHeight('0.875rem', 'ui');
      
      expect(headingLineHeight).toBeLessThan(bodyLineHeight);
      expect(uiLineHeight).toBe(1.4);
    });

    it('should calculate reading time for Polish text', () => {
      const shortText = 'Krótki tekst';
      const longText = 'To jest dłuższy tekst który powinien zająć więcej czasu na przeczytanie i zawiera więcej słów niż poprzedni przykład.';
      
      const shortTime = typographyUtils.calculateReadingTime(shortText);
      const longTime = typographyUtils.calculateReadingTime(longText);
      
      expect(longTime).toBeGreaterThan(shortTime);
      expect(shortTime).toBeGreaterThan(0);
    });

    it('should get contrast requirements based on font size and weight', () => {
      const smallTextRequirements = typographyUtils.getContrastRequirements('14px', 400);
      const largeTextRequirements = typographyUtils.getContrastRequirements('18px', 400);
      const boldTextRequirements = typographyUtils.getContrastRequirements('14px', 700);
      
      expect(smallTextRequirements.normal).toBe(4.5);
      expect(largeTextRequirements.normal).toBe(3);
      expect(boldTextRequirements.normal).toBe(3);
    });

    it('should generate typography CSS correctly', () => {
      const css = typographyUtils.generateTypographyCSS('h1');
      
      expect(css.fontSize).toBeDefined();
      expect(css.fontWeight).toBeDefined();
      expect(css.lineHeight).toBeDefined();
      expect(css.fontFamily).toBeDefined();
    });
  });

  describe('Polish Business Typography', () => {
    it('should format currency with options', () => {
      const withSymbol = polishBusinessTypography.formatCurrency(1234.56);
      const withoutSymbol = polishBusinessTypography.formatCurrency(1234.56, { showSymbol: false });
      const customDecimals = polishBusinessTypography.formatCurrency(1234.56, { decimals: 0 });
      
      expect(withSymbol).toContain('zł');
      expect(withoutSymbol).not.toContain('zł');
      expect(customDecimals).not.toContain(',56');
    });

    it('should format dates in different formats', () => {
      const date = new Date('2025-01-15');
      
      const shortFormat = polishBusinessTypography.formatDate(date, 'short');
      const longFormat = polishBusinessTypography.formatDate(date, 'long');
      const numericFormat = polishBusinessTypography.formatDate(date, 'numeric');
      
      expect(shortFormat).toBe('15.01.2025');
      expect(longFormat).toContain('stycznia');
      expect(numericFormat).toBe('15.01.2025');
    });

    it('should format NIP correctly', () => {
      const nip = '1234567890';
      const formatted = polishBusinessTypography.formatNIP(nip);
      expect(formatted).toBe('123-456-78-90');
    });

    it('should format REGON correctly', () => {
      const regon9 = '123456789';
      const regon14 = '12345678901234';
      
      const formatted9 = polishBusinessTypography.formatREGON(regon9);
      const formatted14 = polishBusinessTypography.formatREGON(regon14);
      
      expect(formatted9).toBe('123-456-789');
      expect(formatted14).toBe('123-456-78-901234');
    });

    it('should format postal code correctly', () => {
      const code = '12345';
      const formatted = polishBusinessTypography.formatPostalCode(code);
      expect(formatted).toBe('12-345');
    });

    it('should get invoice status text in Polish', () => {
      expect(polishBusinessTypography.getInvoiceStatusText('draft')).toBe('Szkic');
      expect(polishBusinessTypography.getInvoiceStatusText('sent')).toBe('Wysłana');
      expect(polishBusinessTypography.getInvoiceStatusText('paid')).toBe('Opłacona');
      expect(polishBusinessTypography.getInvoiceStatusText('overdue')).toBe('Przeterminowana');
      expect(polishBusinessTypography.getInvoiceStatusText('cancelled')).toBe('Anulowana');
    });

    it('should get VAT rate text correctly', () => {
      expect(polishBusinessTypography.getVATRateText(0.23)).toBe('23%');
      expect(polishBusinessTypography.getVATRateText(0.08)).toBe('8%');
      expect(polishBusinessTypography.getVATRateText(0)).toBe('0%');
      expect(polishBusinessTypography.getVATRateText(-1)).toBe('zw.');
    });

    it('should format phone numbers correctly', () => {
      const mobile = '123456789';
      const international = '48123456789';
      
      const formattedMobile = polishBusinessTypography.formatPhoneNumber(mobile);
      const formattedInternational = polishBusinessTypography.formatPhoneNumber(international);
      
      expect(formattedMobile).toBe('123 456 789');
      expect(formattedInternational).toBe('+48 123 456 789');
    });

    it('should suggest appropriate text size for content length', () => {
      const shortTitle = 'Krótki tytuł';
      const longTitle = 'To jest bardzo długi tytuł który przekracza standardową długość';
      
      const shortSize = polishBusinessTypography.getTextSizeForContent(shortTitle, 'title');
      const longSize = polishBusinessTypography.getTextSizeForContent(longTitle, 'title');
      
      expect(shortSize).toBe('3xl');
      expect(longSize).toBe('xl');
    });

    it('should detect when text needs truncation', () => {
      const shortText = 'Krótki tekst';
      const longText = 'To jest bardzo długi tekst który przekracza limit';
      
      expect(polishBusinessTypography.needsTruncation(shortText, 20)).toBe(false);
      expect(polishBusinessTypography.needsTruncation(longText, 20)).toBe(true);
    });

    it('should truncate text at word boundaries', () => {
      const text = 'To jest przykład długiego tekstu który zostanie obcięty';
      const truncated = polishBusinessTypography.truncateText(text, 30);
      
      expect(truncated.length).toBeLessThanOrEqual(30);
      expect(truncated).toContain('...');
      expect(truncated).not.toContain('zostanie obcięty');
    });

    it('should estimate text metrics', () => {
      const text = 'Przykładowy tekst';
      const metrics = polishBusinessTypography.getTextMetrics(text, '16px', 'Inter');
      
      expect(metrics.estimatedWidth).toBeGreaterThan(0);
      expect(metrics.estimatedHeight).toBeGreaterThan(0);
      expect(metrics.lineCount).toBeGreaterThan(0);
    });
  });

  describe('Typography Accessibility', () => {
    it('should check font size accessibility requirements', () => {
      expect(typographyA11yUtils.meetsFontSizeRequirements('16px', 'body')).toBe(true);
      expect(typographyA11yUtils.meetsFontSizeRequirements('12px', 'body')).toBe(false);
      expect(typographyA11yUtils.meetsFontSizeRequirements('14px', 'ui')).toBe(true);
      expect(typographyA11yUtils.meetsFontSizeRequirements('12px', 'caption')).toBe(true);
    });

    it('should generate appropriate ARIA labels', () => {
      const currencyLabel = typographyA11yUtils.getAriaLabel('1234,56 zł', 'currency');
      const dateLabel = typographyA11yUtils.getAriaLabel('2025-01-15', 'date');
      const nipLabel = typographyA11yUtils.getAriaLabel('123-456-78-90', 'nip');
      
      expect(currencyLabel).toContain('złotych');
      expect(dateLabel).toContain('stycznia');
      expect(nipLabel).toContain('NIP');
    });

    it('should generate screen reader friendly text', () => {
      const screenReaderText = typographyA11yUtils.generateScreenReaderText(
        '1234,56 zł',
        { type: 'currency', prefix: 'Kwota', suffix: 'do zapłaty' }
      );
      
      expect(screenReaderText).toContain('Kwota');
      expect(screenReaderText).toContain('do zapłaty');
      expect(screenReaderText).toContain('złotych');
    });

    it('should check line height accessibility', () => {
      expect(typographyA11yUtils.meetsLineHeightRequirements(1.5)).toBe(true);
      expect(typographyA11yUtils.meetsLineHeightRequirements(1.2)).toBe(false);
      expect(typographyA11yUtils.meetsLineHeightRequirements('1.6')).toBe(true);
    });

    it('should provide recommended line height', () => {
      const recommended = typographyA11yUtils.getRecommendedLineHeight('16px');
      expect(recommended).toBeGreaterThanOrEqual(1.5);
    });
  });

  describe('Integration Tests', () => {
    it('should integrate typography styles with utilities', () => {
      const invoiceNumberStyle = typographyStyles.invoiceNumber;
      const css = typographyUtils.generateTypographyCSS('invoiceNumber');
      
      expect(css.fontSize).toBe(invoiceNumberStyle.fontSize);
      expect(css.fontWeight).toBe(invoiceNumberStyle.fontWeight);
      expect(css.fontFamily).toBe(invoiceNumberStyle.fontFamily);
    });

    it('should provide consistent Polish formatting', () => {
      const currency = polishBusinessTypography.formatCurrency(1234.56);
      const date = polishBusinessTypography.formatDate(new Date('2025-01-15'));
      const nip = polishBusinessTypography.formatNIP('1234567890');
      
      expect(currency).toMatch(/1[\s,]234[,.]56/);
      expect(date).toBe('15.01.2025');
      expect(nip).toBe('123-456-78-90');
    });

    it('should maintain accessibility standards across all styles', () => {
      Object.entries(typographyStyles).forEach(([key, style]) => {
        const requirements = typographyUtils.getContrastRequirements(
          style.fontSize, 
          style.fontWeight
        );
        expect(requirements.normal).toBeGreaterThan(0);
        expect(requirements.enhanced).toBeGreaterThan(requirements.normal);
      });
    });
  });
});