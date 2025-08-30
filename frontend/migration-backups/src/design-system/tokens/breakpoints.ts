// Breakpoint Token Definitions
export interface BreakpointTokens {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
}

// Responsive breakpoints optimized for Polish business applications
export const breakpoints: BreakpointTokens = {
  xs: '475px',    // Small mobile devices
  sm: '640px',    // Mobile devices
  md: '768px',    // Tablets
  lg: '1024px',   // Small desktops
  xl: '1280px',   // Large desktops
  '2xl': '1536px', // Extra large screens
};

// Breakpoint utilities for media queries
export const mediaQueries = {
  xs: `@media (min-width: ${breakpoints.xs})`,
  sm: `@media (min-width: ${breakpoints.sm})`,
  md: `@media (min-width: ${breakpoints.md})`,
  lg: `@media (min-width: ${breakpoints.lg})`,
  xl: `@media (min-width: ${breakpoints.xl})`,
  '2xl': `@media (min-width: ${breakpoints['2xl']})`,
  
  // Max-width queries
  maxXs: `@media (max-width: ${parseInt(breakpoints.xs) - 1}px)`,
  maxSm: `@media (max-width: ${parseInt(breakpoints.sm) - 1}px)`,
  maxMd: `@media (max-width: ${parseInt(breakpoints.md) - 1}px)`,
  maxLg: `@media (max-width: ${parseInt(breakpoints.lg) - 1}px)`,
  maxXl: `@media (max-width: ${parseInt(breakpoints.xl) - 1}px)`,
  max2xl: `@media (max-width: ${parseInt(breakpoints['2xl']) - 1}px)`,
  
  // Range queries
  smToMd: `@media (min-width: ${breakpoints.sm}) and (max-width: ${parseInt(breakpoints.md) - 1}px)`,
  mdToLg: `@media (min-width: ${breakpoints.md}) and (max-width: ${parseInt(breakpoints.lg) - 1}px)`,
  lgToXl: `@media (min-width: ${breakpoints.lg}) and (max-width: ${parseInt(breakpoints.xl) - 1}px)`,
} as const;

// Container max-widths for different breakpoints
export const containerMaxWidths = {
  xs: '100%',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// Grid columns for different breakpoints
export const gridColumns = {
  xs: 1,
  sm: 2,
  md: 3,
  lg: 4,
  xl: 6,
  '2xl': 8,
} as const;

// Polish business context responsive utilities
export const polishBusinessBreakpoints = {
  // Invoice table breakpoints
  invoiceTableCollapse: breakpoints.md,    // Collapse invoice table on tablets
  invoiceTableFull: breakpoints.lg,        // Full invoice table on desktop
  
  // Form layout breakpoints
  formSingleColumn: breakpoints.sm,        // Single column forms on mobile
  formTwoColumn: breakpoints.md,           // Two column forms on tablets
  formThreeColumn: breakpoints.lg,         // Three column forms on desktop
  
  // Navigation breakpoints
  mobileNav: breakpoints.md,               // Mobile navigation below tablet
  desktopNav: breakpoints.lg,              // Desktop navigation on large screens
  
  // Dashboard breakpoints
  dashboardMobile: breakpoints.sm,         // Mobile dashboard layout
  dashboardTablet: breakpoints.md,         // Tablet dashboard layout
  dashboardDesktop: breakpoints.xl,        // Desktop dashboard layout
} as const;

export type BreakpointKey = keyof typeof breakpoints;
export type MediaQueryKey = keyof typeof mediaQueries;