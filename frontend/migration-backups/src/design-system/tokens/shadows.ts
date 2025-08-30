// Shadow Token Definitions
export interface ShadowScale {
  none: string;
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  inner: string;
}

// Elevation system with subtle shadows for Polish business applications
export const shadows: ShadowScale = {
  none: 'none',
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
};

// Semantic shadows for different component states
export const semanticShadows = {
  // Component elevation
  componentResting: shadows.sm,        // Default component shadow
  componentHover: shadows.md,          // Hover state shadow
  componentActive: shadows.xs,         // Active/pressed state shadow
  componentFocus: '0 0 0 3px rgba(37, 99, 235, 0.1)', // Focus ring shadow
  
  // Card shadows
  cardResting: shadows.sm,             // Default card shadow
  cardHover: shadows.lg,               // Card hover shadow
  cardPressed: shadows.xs,             // Card pressed shadow
  
  // Modal and overlay shadows
  modalOverlay: shadows['2xl'],        // Modal backdrop shadow
  dropdownShadow: shadows.lg,          // Dropdown menu shadow
  tooltipShadow: shadows.md,           // Tooltip shadow
  
  // Form element shadows
  inputShadow: shadows.xs,             // Input field shadow
  inputFocus: '0 0 0 3px rgba(37, 99, 235, 0.1)', // Input focus shadow
  inputError: '0 0 0 3px rgba(220, 38, 38, 0.1)', // Input error shadow
  
  // Button shadows
  buttonPrimary: shadows.sm,           // Primary button shadow
  buttonSecondary: shadows.xs,         // Secondary button shadow
  buttonHover: shadows.md,             // Button hover shadow
  buttonActive: shadows.inner,         // Button active shadow
  
  // Polish business context shadows
  invoiceShadow: shadows.sm,           // Invoice card shadow
  documentShadow: shadows.md,          // Document preview shadow
  tableShadow: shadows.xs,             // Data table shadow
  sidebarShadow: shadows.lg,           // Navigation sidebar shadow
} as const;

// Focus ring utilities for accessibility
export const focusRings = {
  default: '0 0 0 3px rgba(37, 99, 235, 0.1)',
  success: '0 0 0 3px rgba(5, 150, 105, 0.1)',
  warning: '0 0 0 3px rgba(217, 119, 6, 0.1)',
  error: '0 0 0 3px rgba(220, 38, 38, 0.1)',
  neutral: '0 0 0 3px rgba(107, 114, 128, 0.1)',
} as const;

export type ShadowKey = keyof typeof shadows;
export type SemanticShadowKey = keyof typeof semanticShadows;
export type FocusRingKey = keyof typeof focusRings;