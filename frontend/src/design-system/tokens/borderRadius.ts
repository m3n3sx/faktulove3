// Border Radius Token Definitions
export interface BorderRadiusScale {
  none: string;
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  '3xl': string;
  full: string;
}

// Border radius scale for consistent rounded-md corners
export const borderRadius: BorderRadiusScale = {
  none: '0px',
  xs: '0.125rem',   // 2px
  sm: '0.25rem',    // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  '3xl': '1.5rem',  // 24px
  full: '9999px',   // Fully rounded-md
};

// Semantic border radius for different component types
export const semanticBorderRadius = {
  // Component border radius
  componentDefault: borderRadius.md,     // Default component radius (6px)
  componentSmall: borderRadius.sm,       // Small component radius (4px)
  componentLarge: borderRadius.lg,       // Large component radius (8px)
  
  // Button border radius
  buttonDefault: borderRadius.md,        // Default button radius
  buttonSmall: borderRadius.sm,          // Small button radius
  buttonLarge: borderRadius.lg,          // Large button radius
  buttonPill: borderRadius.full,         // Pill-shaped button
  
  // Input border radius
  inputDefault: borderRadius.md,         // Default input radius
  inputSmall: borderRadius.sm,           // Small input radius
  inputLarge: borderRadius.lg,           // Large input radius
  
  // Card border radius
  cardDefault: borderRadius.lg,          // Default card radius
  cardSmall: borderRadius.md,            // Small card radius
  cardLarge: borderRadius.xl,            // Large card radius
  
  // Modal border radius
  modalDefault: borderRadius.xl,         // Default modal radius
  modalLarge: borderRadius['2xl'],       // Large modal radius
  
  // Image border radius
  imageDefault: borderRadius.md,         // Default image radius
  imageRounded: borderRadius.lg,         // Rounded image
  imageCircle: borderRadius.full,        // Circular image
  
  // Badge border radius
  badgeDefault: borderRadius.sm,         // Default badge radius
  badgePill: borderRadius.full,          // Pill-shaped badge
  
  // Polish business context border radius
  invoiceCard: borderRadius.lg,          // Invoice card radius
  documentPreview: borderRadius.md,      // Document preview radius
  tableCell: borderRadius.sm,            // Table cell radius
  formField: borderRadius.md,            // Form field radius
  statusBadge: borderRadius.full,        // Status badge radius
} as const;

export type BorderRadiusKey = keyof typeof borderRadius;
export type SemanticBorderRadiusKey = keyof typeof semanticBorderRadius;