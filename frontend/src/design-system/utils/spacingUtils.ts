// Spacing Utility Functions
import { 
  spacing, 
  semanticSpacing, 
  layoutTokens, 
  responsiveSpacing, 
  advancedSpacing,
  sizeVariants 
} from '../tokens/spacing';

// Spacing utility functions
export const spacingUtils = {
  // Convert spacing token to pixels
  getSpacingInPixels: (spacingKey: keyof typeof spacing): number => {
    const value = spacing[spacingKey];
    if (value.endsWith('rem')) {
      return parseFloat(value) * 16; // Assuming 1rem = 16px
    }
    if (value.endsWith('px')) {
      return parseFloat(value);
    }
    return 0;
  },

  // Get spacing value by key
  getSpacing: (spacingKey: keyof typeof spacing): string => {
    return spacing[spacingKey];
  },

  // Get semantic spacing value
  getSemanticSpacing: (semanticKey: keyof typeof semanticSpacing): string => {
    return semanticSpacing[semanticKey];
  },

  // Calculate spacing for specific use cases
  calculateSpacing: (
    baseSpacing: keyof typeof spacing,
    multiplier: number = 1,
    adjustment: number = 0
  ): string => {
    const baseValue = spacingUtils.getSpacingInPixels(baseSpacing);
    const calculated = (baseValue * multiplier) + adjustment;
    return `${calculated / 16}rem`;
  },

  // Get responsive spacing CSS
  getResponsiveSpacing: (
    property: 'padding' | 'margin' | 'gap',
    values: {
      xs?: keyof typeof spacing;
      sm?: keyof typeof spacing;
      md?: keyof typeof spacing;
      lg?: keyof typeof spacing;
      xl?: keyof typeof spacing;
      '2xl'?: keyof typeof spacing;
    }
  ): Record<string, any> => {
    const css: Record<string, any> = {};
    
    // Base value (mobile first)
    if (values.xs) {
      css[property] = spacing[values.xs];
    }
    
    // Responsive values
    Object.entries(values).forEach(([breakpoint, spacingKey]) => {
      if (breakpoint !== 'xs' && spacingKey) {
        const mediaQuery = `@media (min-width: ${getBreakpointValue(breakpoint)})`;
        if (!css[mediaQuery]) {
          css[mediaQuery] = {};
        }
        css[mediaQuery][property] = spacing[spacingKey];
      }
    });
    
    return css;
  },

  // Generate spacing classes for CSS
  generateSpacingClasses: (prefix: string = 'space'): Record<string, string> => {
    const classes: Record<string, string> = {};
    
    Object.entries(spacing).forEach(([key, value]) => {
      classes[`${prefix}-${key}`] = value;
    });
    
    return classes;
  },

  // Check if spacing follows 8px grid
  followsEightPxGrid: (spacingKey: keyof typeof spacing): boolean => {
    const pixels = spacingUtils.getSpacingInPixels(spacingKey);
    return pixels % 8 === 0 || pixels === 1 || pixels === 2; // Allow 1px and 2px for borders
  },

  // Get optimal spacing for content density
  getOptimalSpacing: (
    context: 'compact' | 'comfortable' | 'spacious',
    element: 'component' | 'layout' | 'section' | 'page'
  ): keyof typeof spacing => {
    const spacingMap = {
      compact: {
        component: 2,
        layout: 4,
        section: 6,
        page: 8,
      },
      comfortable: {
        component: 4,
        layout: 6,
        section: 8,
        page: 12,
      },
      spacious: {
        component: 6,
        layout: 8,
        section: 12,
        page: 16,
      },
    };
    
    return spacingMap[context][element] as keyof typeof spacing;
  },
} as const;

// Polish business spacing utilities
export const polishBusinessSpacing = {
  // Get invoice layout spacing
  getInvoiceSpacing: (element: 'header' | 'item' | 'section' | 'total' | 'footer'): string => {
    const spacingMap = {
      header: semanticSpacing.invoiceHeaderSpacing,
      item: semanticSpacing.invoiceItemSpacing,
      section: semanticSpacing.invoiceSectionSpacing,
      total: semanticSpacing.invoiceTotalSpacing,
      footer: semanticSpacing.documentFooterSpacing,
    };
    return spacingMap[element];
  },

  // Get form spacing for Polish business forms
  getFormSpacing: (element: 'field' | 'group' | 'section' | 'page'): string => {
    const spacingMap = {
      field: semanticSpacing.formFieldSpacing,
      group: semanticSpacing.formGroupSpacing,
      section: semanticSpacing.formSectionSpacing,
      page: semanticSpacing.pageSpacing,
    };
    return spacingMap[element];
  },

  // Get dashboard spacing
  getDashboardSpacing: (element: 'card' | 'section' | 'widget'): string => {
    const spacingMap = {
      card: semanticSpacing.dashboardCardSpacing,
      section: semanticSpacing.dashboardSectionSpacing,
      widget: semanticSpacing.dashboardWidgetPadding,
    };
    return spacingMap[element];
  },

  // Get table spacing for Polish business tables
  getTableSpacing: (element: 'cell' | 'row' | 'section', density: 'compact' | 'normal' | 'loose' = 'normal'): string => {
    if (element === 'cell') {
      const densityMap = {
        compact: semanticSpacing.tableCellPaddingCompact,
        normal: semanticSpacing.tableCellPadding,
        loose: semanticSpacing.tableCellPaddingLoose,
      };
      return densityMap[density];
    }
    
    const spacingMap = {
      row: semanticSpacing.tableRowSpacing,
      section: semanticSpacing.tableSectionSpacing,
    };
    return spacingMap[element] || semanticSpacing.tableCellPadding;
  },

  // Get print spacing for invoice printing
  getPrintSpacing: (element: 'margin' | 'section' | 'item'): string => {
    const spacingMap = {
      margin: semanticSpacing.printMargin,
      section: semanticSpacing.printSectionSpacing,
      item: semanticSpacing.printItemSpacing,
    };
    return spacingMap[element];
  },

  // Calculate spacing for Polish text length
  calculatePolishTextSpacing: (textLength: number, context: 'label' | 'input' | 'button' = 'input'): string => {
    // Polish text is typically 20-30% longer, so adjust spacing accordingly
    const baseSpacing = {
      label: 2,
      input: 3,
      button: 4,
    };
    
    const base = baseSpacing[context];
    const adjustment = textLength > 20 ? 1 : 0; // Add extra space for longer Polish text
    
    return spacing[(base + adjustment) as keyof typeof spacing];
  },

  // Get responsive spacing for Polish business layouts
  getResponsiveBusinessSpacing: (
    context: 'invoice' | 'form' | 'dashboard'
  ): { xs: string; sm: string; lg: string } => {
    return (responsiveSpacing.polishBusinessResponsive as any)[`${context}Spacing`];
  },
} as const;

// Layout utility functions
export const layoutUtils = {
  // Get container max width
  getContainerMaxWidth: (size: keyof typeof layoutTokens.containerMaxWidths): string => {
    return layoutTokens.containerMaxWidths[size];
  },

  // Get grid columns
  getGridColumns: (columns: keyof typeof layoutTokens.gridColumns): string => {
    return layoutTokens.gridColumns[columns];
  },

  // Get grid gap
  getGridGap: (gap: keyof typeof layoutTokens.gridGaps): string => {
    return layoutTokens.gridGaps[gap];
  },

  // Generate CSS Grid template
  generateGridTemplate: (
    columns: number,
    gap: keyof typeof layoutTokens.gridGaps = 'md'
  ): React.CSSProperties => {
    return {
      display: 'grid',
      gridTemplateColumns: `repeat(${columns}, 1fr)`,
      gap: layoutTokens.gridGaps[gap],
    };
  },

  // Generate Flexbox layout
  generateFlexLayout: (
    direction: 'row' | 'column' = 'row',
    gap: keyof typeof layoutTokens.flexGaps = 'md',
    justify: 'start' | 'end' | 'center' | 'between' | 'around' | 'evenly' = 'start',
    align: 'start' | 'end' | 'center' | 'baseline' | 'stretch' = 'start'
  ): React.CSSProperties => {
    const justifyMap = {
      start: 'flex-start',
      end: 'flex-end',
      center: 'center',
      between: 'space-between',
      around: 'space-around',
      evenly: 'space-evenly',
    };
    
    const alignMap = {
      start: 'flex-start',
      end: 'flex-end',
      center: 'center',
      baseline: 'baseline',
      stretch: 'stretch',
    };
    
    return {
      display: 'flex',
      flexDirection: direction,
      gap: layoutTokens.flexGaps[gap],
      justifyContent: justifyMap[justify],
      alignItems: alignMap[align],
    };
  },

  // Get Polish business layout
  getPolishBusinessLayout: (
    layout: keyof typeof layoutTokens.polishBusinessLayouts
  ): typeof layoutTokens.polishBusinessLayouts[keyof typeof layoutTokens.polishBusinessLayouts] => {
    return layoutTokens.polishBusinessLayouts[layout];
  },

  // Calculate optimal layout for content
  calculateOptimalLayout: (
    contentItems: number,
    containerWidth: number,
    minItemWidth: number = 200
  ): { columns: number; gap: keyof typeof layoutTokens.gridGaps } => {
    const maxColumns = Math.floor(containerWidth / minItemWidth);
    const optimalColumns = Math.min(contentItems, maxColumns, 12);
    
    // Adjust gap based on number of columns
    const gap: keyof typeof layoutTokens.gridGaps = 
      optimalColumns <= 2 ? 'xl' :
      optimalColumns <= 4 ? 'lg' :
      optimalColumns <= 6 ? 'md' : 'sm';
    
    return { columns: optimalColumns, gap };
  },
} as const;

// Advanced spacing utilities
export const advancedSpacingUtils = {
  // Get aspect ratio
  getAspectRatio: (ratio: keyof typeof advancedSpacing.aspectRatios): string => {
    return advancedSpacing.aspectRatios[ratio];
  },

  // Get safe area inset
  getSafeAreaInset: (side: keyof typeof advancedSpacing.safeAreas): string => {
    return advancedSpacing.safeAreas[side];
  },

  // Get document dimensions
  getDocumentDimensions: (
    document: keyof typeof advancedSpacing.documentDimensions
  ): string => {
    return advancedSpacing.documentDimensions[document];
  },

  // Apply optical adjustments
  applyOpticalAdjustment: (
    baseSpacing: string,
    adjustment: keyof typeof advancedSpacing.opticalAdjustments
  ): string => {
    const adjustmentValue = advancedSpacing.opticalAdjustments[adjustment];
    return `calc(${baseSpacing} + ${adjustmentValue})`;
  },

  // Generate print-safe spacing
  generatePrintSpacing: (element: 'margin' | 'padding' | 'gap'): React.CSSProperties => {
    const printSpacing = {
      margin: advancedSpacing.documentDimensions.a4Margin,
      padding: semanticSpacing.printSectionSpacing,
      gap: semanticSpacing.printItemSpacing,
    };
    
    return {
      '@media print': {
        [element]: printSpacing[element],
      },
    } as any;
  },

  // Calculate spacing for different screen densities
  calculateDensitySpacing: (
    baseSpacing: keyof typeof spacing,
    density: 'low' | 'normal' | 'high' = 'normal'
  ): string => {
    const densityMultipliers = {
      low: 1.25,    // 25% larger for low-density screens
      normal: 1,    // Standard spacing
      high: 0.875,  // 12.5% smaller for high-density screens
    };
    
    const baseValue = spacingUtils.getSpacingInPixels(baseSpacing);
    const adjusted = baseValue * densityMultipliers[density];
    
    return `${adjusted / 16}rem`;
  },
} as const;

// Helper function to get breakpoint values
function getBreakpointValue(breakpoint: string): string {
  const breakpoints = {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  };
  return breakpoints[breakpoint as keyof typeof breakpoints] || '0px';
}

// Export all utilities
export { layoutTokens, responsiveSpacing, advancedSpacing };
export default spacingUtils;