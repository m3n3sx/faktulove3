// Spacing System Tests
import { 
  spacing, 
  semanticSpacing, 
  layoutTokens, 
  responsiveSpacing, 
  advancedSpacing,
  sizeVariants 
} from '../tokens/spacing';
import { 
  spacingUtils, 
  polishBusinessSpacing, 
  layoutUtils, 
  advancedSpacingUtils 
} from '../utils/spacingUtils';

describe('Spacing System', () => {
  describe('Spacing Tokens', () => {
    it('should follow 8px grid system', () => {
      expect(spacing[2]).toBe('0.5rem');   // 8px base unit
      expect(spacing[4]).toBe('1rem');     // 16px - 2x base
      expect(spacing[6]).toBe('1.5rem');   // 24px - 3x base
      expect(spacing[8]).toBe('2rem');     // 32px - 4x base
      expect(spacing[12]).toBe('3rem');    // 48px - 6x base
      expect(spacing[16]).toBe('4rem');    // 64px - 8x base
    });

    it('should have complete spacing scale', () => {
      expect(spacing[0]).toBe('0px');
      expect(spacing.px).toBe('1px');
      expect(spacing[0.5]).toBe('0.125rem');
      expect(spacing[1]).toBe('0.25rem');
      expect(spacing[96]).toBe('24rem');
    });

    it('should have consistent rem-based values', () => {
      Object.values(spacing).forEach(value => {
        expect(value).toMatch(/^(\d+(\.\d+)?rem|0px|1px)$/);
      });
    });

    it('should maintain mathematical relationships', () => {
      const spacing2 = parseFloat(spacing[2]);
      const spacing4 = parseFloat(spacing[4]);
      const spacing8 = parseFloat(spacing[8]);
      
      expect(spacing4).toBe(spacing2 * 2);
      expect(spacing8).toBe(spacing4 * 2);
    });
  });

  describe('Semantic Spacing', () => {
    it('should have component spacing tokens', () => {
      expect(semanticSpacing.componentPaddingXs).toBeDefined();
      expect(semanticSpacing.componentPadding).toBeDefined();
      expect(semanticSpacing.componentPaddingLg).toBeDefined();
      expect(semanticSpacing.componentMargin).toBeDefined();
      expect(semanticSpacing.componentMarginLg).toBeDefined();
    });

    it('should have layout spacing tokens', () => {
      expect(semanticSpacing.layoutSpacing).toBeDefined();
      expect(semanticSpacing.layoutSpacingLg).toBeDefined();
      expect(semanticSpacing.layoutSpacingXl).toBeDefined();
      expect(semanticSpacing.layoutSpacing2xl).toBeDefined();
    });

    it('should have section spacing tokens', () => {
      expect(semanticSpacing.sectionSpacing).toBeDefined();
      expect(semanticSpacing.sectionSpacingLg).toBeDefined();
      expect(semanticSpacing.sectionSpacingXl).toBeDefined();
      expect(semanticSpacing.sectionSpacing2xl).toBeDefined();
    });

    it('should have form spacing tokens', () => {
      expect(semanticSpacing.formFieldSpacing).toBeDefined();
      expect(semanticSpacing.formGroupSpacing).toBeDefined();
      expect(semanticSpacing.formSectionSpacing).toBeDefined();
    });

    it('should have Polish business specific spacing', () => {
      expect(semanticSpacing.invoiceHeaderSpacing).toBeDefined();
      expect(semanticSpacing.invoiceItemSpacing).toBeDefined();
      expect(semanticSpacing.invoiceSectionSpacing).toBeDefined();
      expect(semanticSpacing.contractorInfoSpacing).toBeDefined();
      expect(semanticSpacing.documentHeaderSpacing).toBeDefined();
      expect(semanticSpacing.dashboardCardSpacing).toBeDefined();
    });

    it('should have table spacing tokens', () => {
      expect(semanticSpacing.tableCellPadding).toBeDefined();
      expect(semanticSpacing.tableCellPaddingCompact).toBeDefined();
      expect(semanticSpacing.tableCellPaddingLoose).toBeDefined();
      expect(semanticSpacing.tableRowSpacing).toBeDefined();
    });

    it('should have print spacing tokens', () => {
      expect(semanticSpacing.printMargin).toBeDefined();
      expect(semanticSpacing.printSectionSpacing).toBeDefined();
      expect(semanticSpacing.printItemSpacing).toBeDefined();
    });
  });

  describe('Size Variants', () => {
    it('should have all size variants', () => {
      expect(sizeVariants.xs).toBeDefined();
      expect(sizeVariants.sm).toBeDefined();
      expect(sizeVariants.md).toBeDefined();
      expect(sizeVariants.lg).toBeDefined();
      expect(sizeVariants.xl).toBeDefined();
    });

    it('should have consistent structure for all variants', () => {
      Object.values(sizeVariants).forEach(variant => {
        expect(variant).toHaveProperty('padding');
        expect(variant).toHaveProperty('height');
        expect(variant).toHaveProperty('fontSize');
      });
    });

    it('should have progressive sizing', () => {
      const heights = Object.values(sizeVariants).map(v => parseFloat(v.height));
      for (let i = 1; i < heights.length; i++) {
        expect(heights[i]).toBeGreaterThan(heights[i - 1]);
      }
    });
  });

  describe('Layout Tokens', () => {
    it('should have container max widths', () => {
      expect(layoutTokens.containerMaxWidths.xs).toBe('475px');
      expect(layoutTokens.containerMaxWidths.sm).toBe('640px');
      expect(layoutTokens.containerMaxWidths.md).toBe('768px');
      expect(layoutTokens.containerMaxWidths.lg).toBe('1024px');
      expect(layoutTokens.containerMaxWidths.xl).toBe('1280px');
      expect(layoutTokens.containerMaxWidths['2xl']).toBe('1536px');
      expect(layoutTokens.containerMaxWidths.full).toBe('100%');
    });

    it('should have grid columns', () => {
      expect(layoutTokens.gridColumns[1]).toBe('1');
      expect(layoutTokens.gridColumns[6]).toBe('6');
      expect(layoutTokens.gridColumns[12]).toBe('12');
    });

    it('should have grid gaps', () => {
      expect(layoutTokens.gridGaps.none).toBe(spacing[0]);
      expect(layoutTokens.gridGaps.xs).toBe(spacing[1]);
      expect(layoutTokens.gridGaps.sm).toBe(spacing[2]);
      expect(layoutTokens.gridGaps.md).toBe(spacing[4]);
      expect(layoutTokens.gridGaps.lg).toBe(spacing[6]);
      expect(layoutTokens.gridGaps.xl).toBe(spacing[8]);
      expect(layoutTokens.gridGaps['2xl']).toBe(spacing[12]);
    });

    it('should have Polish business layouts', () => {
      expect(layoutTokens.polishBusinessLayouts.invoiceLayout).toBeDefined();
      expect(layoutTokens.polishBusinessLayouts.formLayout).toBeDefined();
      expect(layoutTokens.polishBusinessLayouts.dashboardLayout).toBeDefined();
      expect(layoutTokens.polishBusinessLayouts.tableLayout).toBeDefined();
    });

    it('should have consistent layout structure', () => {
      Object.values(layoutTokens.polishBusinessLayouts).forEach(layout => {
        expect(typeof layout).toBe('object');
        expect(Object.keys(layout).length).toBeGreaterThan(0);
      });
    });
  });

  describe('Responsive Spacing', () => {
    it('should have responsive padding', () => {
      expect(responsiveSpacing.responsivePadding.xs).toBeDefined();
      expect(responsiveSpacing.responsivePadding.sm).toBeDefined();
      expect(responsiveSpacing.responsivePadding.lg).toBeDefined();
    });

    it('should have responsive margin', () => {
      expect(responsiveSpacing.responsiveMargin.xs).toBeDefined();
      expect(responsiveSpacing.responsiveMargin.sm).toBeDefined();
      expect(responsiveSpacing.responsiveMargin.lg).toBeDefined();
    });

    it('should have Polish business responsive patterns', () => {
      expect(responsiveSpacing.polishBusinessResponsive.invoicePadding).toBeDefined();
      expect(responsiveSpacing.polishBusinessResponsive.formSpacing).toBeDefined();
      expect(responsiveSpacing.polishBusinessResponsive.dashboardSpacing).toBeDefined();
    });

    it('should have progressive responsive values', () => {
      const { invoicePadding } = responsiveSpacing.polishBusinessResponsive;
      const xsValue = parseFloat(invoicePadding.xs);
      const smValue = parseFloat(invoicePadding.sm);
      const lgValue = parseFloat(invoicePadding.lg);
      
      expect(smValue).toBeGreaterThanOrEqual(xsValue);
      expect(lgValue).toBeGreaterThanOrEqual(smValue);
    });
  });

  describe('Advanced Spacing', () => {
    it('should have aspect ratios', () => {
      expect(advancedSpacing.aspectRatios.square).toBe('1 / 1');
      expect(advancedSpacing.aspectRatios.video).toBe('16 / 9');
      expect(advancedSpacing.aspectRatios.photo).toBe('4 / 3');
      expect(advancedSpacing.aspectRatios.invoice).toBe('210 / 297');
    });

    it('should have safe areas', () => {
      expect(advancedSpacing.safeAreas.top).toBe('env(safe-area-inset-top)');
      expect(advancedSpacing.safeAreas.right).toBe('env(safe-area-inset-right)');
      expect(advancedSpacing.safeAreas.bottom).toBe('env(safe-area-inset-bottom)');
      expect(advancedSpacing.safeAreas.left).toBe('env(safe-area-inset-left)');
    });

    it('should have document dimensions', () => {
      expect(advancedSpacing.documentDimensions.a4Width).toBe('210mm');
      expect(advancedSpacing.documentDimensions.a4Height).toBe('297mm');
      expect(advancedSpacing.documentDimensions.a4Margin).toBe('20mm');
      expect(advancedSpacing.documentDimensions.invoiceWidth).toBe('210mm');
    });

    it('should have optical adjustments', () => {
      expect(advancedSpacing.opticalAdjustments.iconAdjustment).toBeDefined();
      expect(advancedSpacing.opticalAdjustments.buttonAdjustment).toBeDefined();
      expect(advancedSpacing.opticalAdjustments.cardAdjustment).toBeDefined();
    });
  });

  describe('Spacing Utilities', () => {
    it('should convert spacing to pixels correctly', () => {
      expect(spacingUtils.getSpacingInPixels(2)).toBe(8);   // 0.5rem = 8px
      expect(spacingUtils.getSpacingInPixels(4)).toBe(16);  // 1rem = 16px
      expect(spacingUtils.getSpacingInPixels(8)).toBe(32);  // 2rem = 32px
    });

    it('should get spacing values correctly', () => {
      expect(spacingUtils.getSpacing(2)).toBe('0.5rem');
      expect(spacingUtils.getSpacing(4)).toBe('1rem');
      expect(spacingUtils.getSpacing(8)).toBe('2rem');
    });

    it('should get semantic spacing values correctly', () => {
      expect(spacingUtils.getSemanticSpacing('componentPadding')).toBe(spacing[3]);
      expect(spacingUtils.getSemanticSpacing('layoutSpacing')).toBe(spacing[6]);
      expect(spacingUtils.getSemanticSpacing('sectionSpacing')).toBe(spacing[12]);
    });

    it('should calculate spacing with multipliers and adjustments', () => {
      const calculated = spacingUtils.calculateSpacing(4, 1.5, 4);
      expect(calculated).toBe('1.5rem'); // (16 * 1.5 + 4) / 16 = 1.5rem
    });

    it('should generate responsive spacing CSS', () => {
      const css = spacingUtils.getResponsiveSpacing('padding', {
        xs: 4,
        md: 6,
        lg: 8,
      });
      
      expect(css.padding).toBe(spacing[4]);
      expect(css['@media (min-width: 768px)']).toBeDefined();
      expect(css['@media (min-width: 1024px)']).toBeDefined();
    });

    it('should check 8px grid compliance', () => {
      expect(spacingUtils.followsEightPxGrid(2)).toBe(true);   // 8px
      expect(spacingUtils.followsEightPxGrid(4)).toBe(true);   // 16px
      expect(spacingUtils.followsEightPxGrid(6)).toBe(true);   // 24px
      expect(spacingUtils.followsEightPxGrid('px')).toBe(true); // 1px allowed
    });

    it('should get optimal spacing for different contexts', () => {
      const compactComponent = spacingUtils.getOptimalSpacing('compact', 'component');
      const spaciousLayout = spacingUtils.getOptimalSpacing('spacious', 'layout');
      
      expect(compactComponent).toBe(2);
      expect(spaciousLayout).toBe(8);
    });
  });

  describe('Polish Business Spacing', () => {
    it('should get invoice spacing correctly', () => {
      expect(polishBusinessSpacing.getInvoiceSpacing('header')).toBe(semanticSpacing.invoiceHeaderSpacing);
      expect(polishBusinessSpacing.getInvoiceSpacing('item')).toBe(semanticSpacing.invoiceItemSpacing);
      expect(polishBusinessSpacing.getInvoiceSpacing('section')).toBe(semanticSpacing.invoiceSectionSpacing);
      expect(polishBusinessSpacing.getInvoiceSpacing('total')).toBe(semanticSpacing.invoiceTotalSpacing);
    });

    it('should get form spacing correctly', () => {
      expect(polishBusinessSpacing.getFormSpacing('field')).toBe(semanticSpacing.formFieldSpacing);
      expect(polishBusinessSpacing.getFormSpacing('group')).toBe(semanticSpacing.formGroupSpacing);
      expect(polishBusinessSpacing.getFormSpacing('section')).toBe(semanticSpacing.formSectionSpacing);
    });

    it('should get dashboard spacing correctly', () => {
      expect(polishBusinessSpacing.getDashboardSpacing('card')).toBe(semanticSpacing.dashboardCardSpacing);
      expect(polishBusinessSpacing.getDashboardSpacing('section')).toBe(semanticSpacing.dashboardSectionSpacing);
      expect(polishBusinessSpacing.getDashboardSpacing('widget')).toBe(semanticSpacing.dashboardWidgetPadding);
    });

    it('should get table spacing with density options', () => {
      expect(polishBusinessSpacing.getTableSpacing('cell', 'compact')).toBe(semanticSpacing.tableCellPaddingCompact);
      expect(polishBusinessSpacing.getTableSpacing('cell', 'normal')).toBe(semanticSpacing.tableCellPadding);
      expect(polishBusinessSpacing.getTableSpacing('cell', 'loose')).toBe(semanticSpacing.tableCellPaddingLoose);
    });

    it('should get print spacing correctly', () => {
      expect(polishBusinessSpacing.getPrintSpacing('margin')).toBe(semanticSpacing.printMargin);
      expect(polishBusinessSpacing.getPrintSpacing('section')).toBe(semanticSpacing.printSectionSpacing);
      expect(polishBusinessSpacing.getPrintSpacing('item')).toBe(semanticSpacing.printItemSpacing);
    });

    it('should calculate Polish text spacing', () => {
      const shortText = polishBusinessSpacing.calculatePolishTextSpacing(10, 'label');
      const longText = polishBusinessSpacing.calculatePolishTextSpacing(30, 'input');
      
      expect(shortText).toBe(spacing[2]);
      expect(longText).toBe(spacing[4]); // Adjusted for longer Polish text
    });

    it('should get responsive business spacing', () => {
      const invoiceSpacing = polishBusinessSpacing.getResponsiveBusinessSpacing('invoice');
      const formSpacing = polishBusinessSpacing.getResponsiveBusinessSpacing('form');
      const dashboardSpacing = polishBusinessSpacing.getResponsiveBusinessSpacing('dashboard');
      
      expect(invoiceSpacing).toHaveProperty('xs');
      expect(invoiceSpacing).toHaveProperty('sm');
      expect(invoiceSpacing).toHaveProperty('lg');
      expect(formSpacing).toHaveProperty('xs');
      expect(dashboardSpacing).toHaveProperty('xs');
    });
  });

  describe('Layout Utils', () => {
    it('should get container max widths', () => {
      expect(layoutUtils.getContainerMaxWidth('sm')).toBe('640px');
      expect(layoutUtils.getContainerMaxWidth('lg')).toBe('1024px');
      expect(layoutUtils.getContainerMaxWidth('full')).toBe('100%');
    });

    it('should get grid columns', () => {
      expect(layoutUtils.getGridColumns(3)).toBe('3');
      expect(layoutUtils.getGridColumns(6)).toBe('6');
      expect(layoutUtils.getGridColumns(12)).toBe('12');
    });

    it('should get grid gaps', () => {
      expect(layoutUtils.getGridGap('sm')).toBe(spacing[2]);
      expect(layoutUtils.getGridGap('md')).toBe(spacing[4]);
      expect(layoutUtils.getGridGap('lg')).toBe(spacing[6]);
    });

    it('should generate grid template CSS', () => {
      const css = layoutUtils.generateGridTemplate(3, 'md');
      
      expect(css.display).toBe('grid');
      expect(css.gridTemplateColumns).toBe('repeat(3, 1fr)');
      expect(css.gap).toBe(layoutTokens.gridGaps.md);
    });

    it('should generate flex layout CSS', () => {
      const css = layoutUtils.generateFlexLayout('column', 'lg', 'center', 'stretch');
      
      expect(css.display).toBe('flex');
      expect(css.flexDirection).toBe('column');
      expect(css.gap).toBe(layoutTokens.flexGaps.lg);
      expect(css.justifyContent).toBe('center');
      expect(css.alignItems).toBe('stretch');
    });

    it('should get Polish business layouts', () => {
      const invoiceLayout = layoutUtils.getPolishBusinessLayout('invoiceLayout');
      const formLayout = layoutUtils.getPolishBusinessLayout('formLayout');
      
      expect(invoiceLayout).toHaveProperty('headerHeight');
      expect(invoiceLayout).toHaveProperty('contentPadding');
      expect(formLayout).toHaveProperty('fieldSpacing');
      expect(formLayout).toHaveProperty('groupSpacing');
    });

    it('should calculate optimal layout', () => {
      const layout = layoutUtils.calculateOptimalLayout(8, 1200, 200);
      
      expect(layout.columns).toBeGreaterThan(0);
      expect(layout.columns).toBeLessThanOrEqual(12);
      expect(layout.gap).toBeDefined();
    });
  });

  describe('Advanced Spacing Utils', () => {
    it('should get aspect ratios', () => {
      expect(advancedSpacingUtils.getAspectRatio('square')).toBe('1 / 1');
      expect(advancedSpacingUtils.getAspectRatio('video')).toBe('16 / 9');
      expect(advancedSpacingUtils.getAspectRatio('invoice')).toBe('210 / 297');
    });

    it('should get safe area insets', () => {
      expect(advancedSpacingUtils.getSafeAreaInset('top')).toBe('env(safe-area-inset-top)');
      expect(advancedSpacingUtils.getSafeAreaInset('bottom')).toBe('env(safe-area-inset-bottom)');
    });

    it('should get document dimensions', () => {
      expect(advancedSpacingUtils.getDocumentDimensions('a4Width')).toBe('210mm');
      expect(advancedSpacingUtils.getDocumentDimensions('a4Height')).toBe('297mm');
      expect(advancedSpacingUtils.getDocumentDimensions('invoiceWidth')).toBe('210mm');
    });

    it('should apply optical adjustments', () => {
      const adjusted = advancedSpacingUtils.applyOpticalAdjustment('1rem', 'iconAdjustment');
      expect(adjusted).toContain('calc(');
      expect(adjusted).toContain('1rem');
    });

    it('should generate print spacing', () => {
      const css = advancedSpacingUtils.generatePrintSpacing('margin');
      expect(css['@media print']).toBeDefined();
      expect(css['@media print'].margin).toBeDefined();
    });

    it('should calculate density spacing', () => {
      const lowDensity = advancedSpacingUtils.calculateDensitySpacing(4, 'low');
      const normalDensity = advancedSpacingUtils.calculateDensitySpacing(4, 'normal');
      const highDensity = advancedSpacingUtils.calculateDensitySpacing(4, 'high');
      
      expect(parseFloat(lowDensity)).toBeGreaterThan(parseFloat(normalDensity));
      expect(parseFloat(normalDensity)).toBeGreaterThan(parseFloat(highDensity));
    });
  });

  describe('Integration Tests', () => {
    it('should maintain consistency between spacing and semantic spacing', () => {
      // Check that semantic spacing values reference actual spacing tokens
      Object.values(semanticSpacing).forEach(value => {
        expect(Object.values(spacing)).toContain(value);
      });
    });

    it('should have logical progression in size variants', () => {
      const variants = Object.keys(sizeVariants);
      const heights = variants.map(variant => 
        parseFloat(sizeVariants[variant as keyof typeof sizeVariants].height)
      );
      
      for (let i = 1; i < heights.length; i++) {
        expect(heights[i]).toBeGreaterThan(heights[i - 1]);
      }
    });

    it('should provide consistent Polish business spacing', () => {
      const invoiceSpacing = polishBusinessSpacing.getInvoiceSpacing('section');
      const documentSpacing = polishBusinessSpacing.getFormSpacing('section');
      
      // Both should use reasonable spacing values
      expect(parseFloat(invoiceSpacing)).toBeGreaterThan(0);
      expect(parseFloat(documentSpacing)).toBeGreaterThan(0);
    });

    it('should support responsive design patterns', () => {
      const responsive = responsiveSpacing.polishBusinessResponsive.invoicePadding;
      
      expect(parseFloat(responsive.xs)).toBeLessThanOrEqual(parseFloat(responsive.sm));
      expect(parseFloat(responsive.sm)).toBeLessThanOrEqual(parseFloat(responsive.lg));
    });
  });
});