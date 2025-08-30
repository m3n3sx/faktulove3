// Spacing Token Definitions
export interface SpacingScale {
  0: string;
  px: string;
  0.5: string;
  1: string;
  1.5: string;
  2: string;
  2.5: string;
  3: string;
  3.5: string;
  4: string;
  5: string;
  6: string;
  7: string;
  8: string;
  9: string;
  10: string;
  11: string;
  12: string;
  14: string;
  16: string;
  20: string;
  24: string;
  28: string;
  32: string;
  36: string;
  40: string;
  44: string;
  48: string;
  52: string;
  56: string;
  60: string;
  64: string;
  72: string;
  80: string;
  96: string;
}

// 8px grid-based spacing scale
export const spacing: SpacingScale = {
  0: '0px',
  px: '1px',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px - base unit
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px - 2x base
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px - 3x base
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px - 4x base
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px - 5x base
  11: '2.75rem',    // 44px
  12: '3rem',       // 48px - 6x base
  14: '3.5rem',     // 56px - 7x base
  16: '4rem',       // 64px - 8x base
  20: '5rem',       // 80px - 10x base
  24: '6rem',       // 96px - 12x base
  28: '7rem',       // 112px - 14x base
  32: '8rem',       // 128px - 16x base
  36: '9rem',       // 144px - 18x base
  40: '10rem',      // 160px - 20x base
  44: '11rem',      // 176px - 22x base
  48: '12rem',      // 192px - 24x base
  52: '13rem',      // 208px - 26x base
  56: '14rem',      // 224px - 28x base
  60: '15rem',      // 240px - 30x base
  64: '16rem',      // 256px - 32x base
  72: '18rem',      // 288px - 36x base
  80: '20rem',      // 320px - 40x base
  96: '24rem',      // 384px - 48x base
};

// Semantic spacing for common use cases
export const semanticSpacing = {
  // Component internal spacing
  componentPaddingXs: spacing[1],      // 4px
  componentPaddingSm: spacing[2],      // 8px
  componentPadding: spacing[3],        // 12px
  componentPaddingLg: spacing[4],      // 16px
  componentPaddingXl: spacing[6],      // 24px
  
  // Component margins
  componentMarginXs: spacing[1],       // 4px
  componentMarginSm: spacing[2],       // 8px
  componentMargin: spacing[4],         // 16px
  componentMarginLg: spacing[6],       // 24px
  componentMarginXl: spacing[8],       // 32px
  
  // Layout spacing
  layoutSpacingXs: spacing[2],         // 8px
  layoutSpacingSm: spacing[4],         // 16px
  layoutSpacing: spacing[6],           // 24px
  layoutSpacingLg: spacing[8],         // 32px
  layoutSpacingXl: spacing[12],        // 48px
  layoutSpacing2xl: spacing[16],       // 64px
  layoutSpacing3xl: spacing[20],       // 80px
  
  // Section spacing
  sectionSpacingSm: spacing[8],        // 32px
  sectionSpacing: spacing[12],         // 48px
  sectionSpacingLg: spacing[16],       // 64px
  sectionSpacingXl: spacing[20],       // 80px
  sectionSpacing2xl: spacing[24],      // 96px
  
  // Page spacing
  pageSpacing: spacing[6],             // 24px
  pageSpacingLg: spacing[8],           // 32px
  pageSpacingXl: spacing[12],          // 48px
  
  // Form spacing
  formFieldSpacing: spacing[4],        // 16px
  formGroupSpacing: spacing[6],        // 24px
  formSectionSpacing: spacing[8],      // 32px
  
  // Container spacing
  containerPaddingXs: spacing[4],      // 16px
  containerPaddingSm: spacing[6],      // 24px
  containerPadding: spacing[8],        // 32px
  containerPaddingLg: spacing[12],     // 48px
  containerPaddingXl: spacing[16],     // 64px
  
  // Table spacing
  tableCellPadding: spacing[3],        // 12px
  tableCellPaddingCompact: spacing[2], // 8px
  tableCellPaddingLoose: spacing[4],   // 16px
  tableRowSpacing: spacing[1],         // 4px
  tableSectionSpacing: spacing[6],     // 24px
  
  // Card spacing
  cardPaddingXs: spacing[3],           // 12px
  cardPaddingSm: spacing[4],           // 16px
  cardPadding: spacing[6],             // 24px
  cardPaddingLg: spacing[8],           // 32px
  cardMargin: spacing[4],              // 16px
  cardMarginLg: spacing[6],            // 24px
  
  // Modal and overlay spacing
  modalPadding: spacing[6],            // 24px
  modalPaddingLg: spacing[8],          // 32px
  modalMargin: spacing[4],             // 16px
  overlayPadding: spacing[4],          // 16px
  
  // Navigation spacing
  navItemPadding: spacing[3],          // 12px
  navItemMargin: spacing[1],           // 4px
  navSectionSpacing: spacing[6],       // 24px
  navGroupSpacing: spacing[4],         // 16px
  
  // Polish business context spacing
  invoiceHeaderSpacing: spacing[8],    // 32px - space between invoice header sections
  invoiceItemSpacing: spacing[3],      // 12px - tight spacing for invoice items
  invoiceItemPadding: spacing[2],      // 8px - padding within invoice items
  invoiceSectionSpacing: spacing[6],   // 24px - space between invoice sections
  invoiceTotalSpacing: spacing[4],     // 16px - space around totals
  
  contractorInfoSpacing: spacing[4],   // 16px - standard contractor info spacing
  contractorSectionSpacing: spacing[6], // 24px - space between contractor sections
  
  documentHeaderSpacing: spacing[8],   // 32px - space after document headers
  documentSectionSpacing: spacing[6],  // 24px - space between document sections
  documentFooterSpacing: spacing[8],   // 32px - space before document footers
  
  // Dashboard spacing
  dashboardCardSpacing: spacing[6],    // 24px - space between dashboard cards
  dashboardSectionSpacing: spacing[8], // 32px - space between dashboard sections
  dashboardWidgetPadding: spacing[6],  // 24px - padding inside widgets
  
  // Print spacing (for invoice printing)
  printMargin: spacing[20],            // 80px - print margins
  printSectionSpacing: spacing[8],     // 32px - sections in print
  printItemSpacing: spacing[2],        // 8px - items in print
} as const;

export type SemanticSpacingKey = keyof typeof semanticSpacing;

// Size variants for consistent component sizing
export const sizeVariants = {
  xs: {
    padding: `${spacing[1]} ${spacing[2]}`,    // 4px 8px
    height: spacing[6],                        // 24px
    fontSize: '0.75rem',                       // 12px
  },
  sm: {
    padding: `${spacing[1.5]} ${spacing[3]}`,  // 6px 12px
    height: spacing[8],                        // 32px
    fontSize: '0.875rem',                      // 14px
  },
  md: {
    padding: `${spacing[2]} ${spacing[4]}`,    // 8px 16px
    height: spacing[10],                       // 40px
    fontSize: '1rem',                          // 16px
  },
  lg: {
    padding: `${spacing[2.5]} ${spacing[5]}`,  // 10px 20px
    height: spacing[12],                       // 48px
    fontSize: '1.125rem',                      // 18px
  },
  xl: {
    padding: `${spacing[3]} ${spacing[6]}`,    // 12px 24px
    height: spacing[14],                       // 56px
    fontSize: '1.25rem',                       // 20px
  },
} as const;

export type SizeVariant = keyof typeof sizeVariants;

// Layout system tokens
export const layoutTokens = {
  // Container max widths
  containerMaxWidths: {
    xs: '475px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
    full: '100%',
  },
  
  // Grid system
  gridColumns: {
    1: '1',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: '10',
    11: '11',
    12: '12',
  },
  
  // Grid gaps
  gridGaps: {
    none: spacing[0],
    xs: spacing[1],
    sm: spacing[2],
    md: spacing[4],
    lg: spacing[6],
    xl: spacing[8],
    '2xl': spacing[12],
  },
  
  // Flexbox gaps
  flexGaps: {
    none: spacing[0],
    xs: spacing[1],
    sm: spacing[2],
    md: spacing[4],
    lg: spacing[6],
    xl: spacing[8],
    '2xl': spacing[12],
  },
  
  // Polish business layout patterns
  polishBusinessLayouts: {
    // Invoice layout spacing
    invoiceLayout: {
      headerHeight: spacing[20],        // 80px
      footerHeight: spacing[16],        // 64px
      sidebarWidth: spacing[64],        // 256px
      contentPadding: spacing[8],       // 32px
      itemSpacing: spacing[3],          // 12px
    },
    
    // Form layout spacing
    formLayout: {
      fieldSpacing: spacing[4],         // 16px
      groupSpacing: spacing[6],         // 24px
      sectionSpacing: spacing[8],       // 32px
      buttonSpacing: spacing[4],        // 16px
    },
    
    // Dashboard layout spacing
    dashboardLayout: {
      headerHeight: spacing[16],        // 64px
      sidebarWidth: spacing[64],        // 256px
      cardSpacing: spacing[6],          // 24px
      widgetPadding: spacing[6],        // 24px
      sectionSpacing: spacing[8],       // 32px
    },
    
    // Table layout spacing
    tableLayout: {
      cellPadding: spacing[3],          // 12px
      headerPadding: spacing[4],        // 16px
      rowSpacing: spacing[1],           // 4px
      sectionSpacing: spacing[6],       // 24px
    },
  },
} as const;

// Responsive spacing utilities
export const responsiveSpacing = {
  // Mobile-first responsive spacing
  responsivePadding: {
    xs: spacing[4],                     // 16px on mobile
    sm: spacing[6],                     // 24px on tablet
    lg: spacing[8],                     // 32px on desktop
  },
  
  responsiveMargin: {
    xs: spacing[4],                     // 16px on mobile
    sm: spacing[6],                     // 24px on tablet
    lg: spacing[8],                     // 32px on desktop
  },
  
  responsiveGap: {
    xs: spacing[4],                     // 16px on mobile
    sm: spacing[6],                     // 24px on tablet
    lg: spacing[8],                     // 32px on desktop
  },
  
  // Polish business responsive patterns
  polishBusinessResponsive: {
    invoicePadding: {
      xs: spacing[4],                   // 16px on mobile
      sm: spacing[6],                   // 24px on tablet
      lg: spacing[8],                   // 32px on desktop
    },
    
    formSpacing: {
      xs: spacing[4],                   // 16px on mobile
      sm: spacing[6],                   // 24px on tablet
      lg: spacing[8],                   // 32px on desktop
    },
    
    dashboardSpacing: {
      xs: spacing[4],                   // 16px on mobile
      sm: spacing[6],                   // 24px on tablet
      lg: spacing[8],                   // 32px on desktop
    },
  },
} as const;

// Advanced spacing utilities for complex layouts
export const advancedSpacing = {
  // Aspect ratios for consistent proportions
  aspectRatios: {
    square: '1 / 1',
    video: '16 / 9',
    photo: '4 / 3',
    portrait: '3 / 4',
    golden: '1.618 / 1',
    invoice: '210 / 297',              // A4 ratio for invoices
  },
  
  // Safe areas for mobile devices
  safeAreas: {
    top: 'env(safe-area-inset-top)',
    right: 'env(safe-area-inset-right)',
    bottom: 'env(safe-area-inset-bottom)',
    left: 'env(safe-area-inset-left)',
  },
  
  // Polish business document dimensions
  documentDimensions: {
    a4Width: '210mm',
    a4Height: '297mm',
    a4Margin: '20mm',
    invoiceWidth: '210mm',
    invoiceHeight: '297mm',
    receiptWidth: '80mm',
    receiptHeight: 'auto',
  },
  
  // Optical adjustments for visual balance
  opticalAdjustments: {
    // Slightly reduce spacing for visual elements that appear larger
    iconAdjustment: `-${spacing[0.5]}`,  // -2px
    buttonAdjustment: `-${spacing[1]}`,  // -4px
    cardAdjustment: `-${spacing[1]}`,    // -4px
  },
} as const;

// Export additional types
export type LayoutTokenKey = keyof typeof layoutTokens;
export type ResponsiveSpacingKey = keyof typeof responsiveSpacing;
export type AdvancedSpacingKey = keyof typeof advancedSpacing;