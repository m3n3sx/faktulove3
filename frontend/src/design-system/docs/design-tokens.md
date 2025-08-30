# Design Tokens

Design tokens are the visual design atoms of the FaktuLove Design System. They store visual design attributes such as colors, typography, spacing, and more. These tokens ensure consistency across all components and applications.

## 🎨 Token Architecture

### Token Hierarchy
```
Global Tokens → Semantic Tokens → Component Tokens → Components
```

1. **Global Tokens**: Core design decisions (raw values)
2. **Semantic Tokens**: Context-specific mappings (primary, success, warning)
3. **Component Tokens**: Component-specific overrides
4. **Components**: Final implementation using tokens

### Token Format
```tsx
// Global token
const blue600 = '#2563eb';

// Semantic token
const primary = blue600;

// Component token
const buttonPrimaryBg = primary;

// Usage in component
<button style={{ backgroundColor: buttonPrimaryBg }}>
```

## 🌈 Color Tokens

### Color Palette
The design system uses a carefully crafted color palette optimized for Polish business applications.

#### Primary Colors
```tsx
export const colors = {
  primary: {
    50: '#eff6ff',   // Lightest blue
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',  // Primary brand color
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',  // Darkest blue
  },
} as const;
```

#### Semantic Colors
```tsx
export const semanticColors = {
  // Success states (Polish business green)
  success: {
    50: '#ecfdf5',
    100: '#d1fae5',
    200: '#a7f3d0',
    300: '#6ee7b7',
    400: '#34d399',
    500: '#10b981',
    600: '#059669',  // Success color
    700: '#047857',
    800: '#065f46',
    900: '#064e3b',
  },
  
  // Warning states (Polish business orange)
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',  // Warning color
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
  },
  
  // Error states
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',  // Error color
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
  },
  
  // Neutral colors
  neutral: {
    50: '#f9fafb',   // Lightest gray
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',  // Darkest gray
  },
} as const;
```

### Polish Business Colors
```tsx
export const polishBusinessColors = {
  // Polish flag colors for special occasions
  polish: {
    white: '#ffffff',
    red: '#dc143c',
  },
  
  // Currency colors
  currency: {
    pln: '#2563eb',      // Polish Złoty
    eur: '#003399',      // Euro
    usd: '#228b22',      // US Dollar
  },
  
  // VAT rate colors
  vat: {
    standard: '#059669',  // 23% - green
    reduced: '#d97706',   // 8%, 5% - orange
    zero: '#6b7280',      // 0% - gray
    exempt: '#7c3aed',    // Exempt - purple
  },
} as const;
```

### Color Usage
```tsx
import { colors, semanticColors } from '@faktulove/design-system/tokens';

// Using colors in components
const Button = styled.button`
  background-color: ${colors.primary[600]};
  color: ${colors.neutral[50]};
  
  &:hover {
    background-color: ${colors.primary[700]};
  }
  
  &.success {
    background-color: ${semanticColors.success[600]};
  }
`;
```

### CSS Custom Properties
```css
:root {
  /* Primary colors */
  --ds-color-primary-50: #eff6ff;
  --ds-color-primary-600: #2563eb;
  --ds-color-primary-900: #1e3a8a;
  
  /* Semantic colors */
  --ds-color-success-600: #059669;
  --ds-color-warning-600: #d97706;
  --ds-color-error-600: #dc2626;
  
  /* Polish business colors */
  --ds-color-currency-pln: #2563eb;
  --ds-color-vat-standard: #059669;
}
```

## 📝 Typography Tokens

### Font Families
```tsx
export const typography = {
  fontFamily: {
    sans: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ],
    mono: [
      '"JetBrains Mono"',
      'Menlo',
      'Monaco',
      'Consolas',
      '"Liberation Mono"',
      '"Courier New"',
      'monospace',
    ],
  },
} as const;
```

### Font Sizes (8px Grid System)
```tsx
export const fontSize = {
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem', // 36px
  '5xl': '3rem',    // 48px
  '6xl': '3.75rem', // 60px
} as const;
```

### Font Weights
```tsx
export const fontWeight = {
  thin: '100',
  extralight: '200',
  light: '300',
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
  extrabold: '800',
  black: '900',
} as const;
```

### Line Heights
```tsx
export const lineHeight = {
  none: '1',
  tight: '1.25',
  snug: '1.375',
  normal: '1.5',
  relaxed: '1.625',
  loose: '2',
} as const;
```

### Typography Usage
```tsx
// In components
const Heading = styled.h1`
  font-family: ${typography.fontFamily.sans.join(', ')};
  font-size: ${fontSize['2xl']};
  font-weight: ${fontWeight.bold};
  line-height: ${lineHeight.tight};
`;

// CSS custom properties
:root {
  --ds-font-family-sans: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
  --ds-font-size-lg: 1.125rem;
  --ds-font-weight-semibold: 600;
  --ds-line-height-normal: 1.5;
}
```

### Polish Typography Considerations
```tsx
export const polishTypography = {
  // Ensure proper character support
  fontFeatures: {
    // Enable Polish diacritics
    'kern': 1,
    'liga': 1,
    'calt': 1,
  },
  
  // Longer text considerations
  lineLength: {
    optimal: '65ch',  // Slightly longer for Polish text
    maximum: '75ch',
  },
  
  // Polish business document typography
  business: {
    invoiceNumber: {
      fontFamily: typography.fontFamily.mono,
      fontSize: fontSize.sm,
      fontWeight: fontWeight.medium,
    },
    currency: {
      fontSize: fontSize.lg,
      fontWeight: fontWeight.semibold,
      fontVariantNumeric: 'tabular-nums',
    },
  },
} as const;
```

## 📏 Spacing Tokens

### Spacing Scale (8px Grid System)
```tsx
export const spacing = {
  0: '0',
  px: '1px',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px
  11: '2.75rem',    // 44px
  12: '3rem',       // 48px
  14: '3.5rem',     // 56px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
  28: '7rem',       // 112px
  32: '8rem',       // 128px
  36: '9rem',       // 144px
  40: '10rem',      // 160px
  44: '11rem',      // 176px
  48: '12rem',      // 192px
  52: '13rem',      // 208px
  56: '14rem',      // 224px
  60: '15rem',      // 240px
  64: '16rem',      // 256px
  72: '18rem',      // 288px
  80: '20rem',      // 320px
  96: '24rem',      // 384px
} as const;
```

### Semantic Spacing
```tsx
export const semanticSpacing = {
  // Component spacing
  component: {
    xs: spacing[1],    // 4px
    sm: spacing[2],    // 8px
    md: spacing[4],    // 16px
    lg: spacing[6],    // 24px
    xl: spacing[8],    // 32px
  },
  
  // Layout spacing
  layout: {
    xs: spacing[4],    // 16px
    sm: spacing[6],    // 24px
    md: spacing[8],    // 32px
    lg: spacing[12],   // 48px
    xl: spacing[16],   // 64px
  },
  
  // Polish business spacing
  business: {
    formField: spacing[4],     // 16px between form fields
    cardPadding: spacing[6],   // 24px card padding
    sectionGap: spacing[8],    // 32px between sections
  },
} as const;
```

### Spacing Usage
```tsx
// In components
const Card = styled.div`
  padding: ${spacing[6]};
  margin-bottom: ${spacing[4]};
  gap: ${spacing[2]};
`;

// CSS custom properties
:root {
  --ds-spacing-2: 0.5rem;
  --ds-spacing-4: 1rem;
  --ds-spacing-6: 1.5rem;
}
```

## 📱 Breakpoint Tokens

### Responsive Breakpoints
```tsx
export const breakpoints = {
  sm: '640px',    // Small devices (phones)
  md: '768px',    // Medium devices (tablets)
  lg: '1024px',   // Large devices (laptops)
  xl: '1280px',   // Extra large devices (desktops)
  '2xl': '1536px', // 2X large devices (large desktops)
} as const;
```

### Polish Business Breakpoints
```tsx
export const polishBusinessBreakpoints = {
  // Optimized for Polish business users
  mobile: breakpoints.sm,      // 640px - mobile phones
  tablet: breakpoints.md,      // 768px - tablets
  desktop: breakpoints.lg,     // 1024px - business laptops
  widescreen: breakpoints.xl,  // 1280px - office monitors
} as const;
```

### Breakpoint Usage
```tsx
// In styled components
const ResponsiveGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  
  @media (min-width: ${breakpoints.md}) {
    grid-template-columns: 1fr 1fr;
  }
  
  @media (min-width: ${breakpoints.lg}) {
    grid-template-columns: 1fr 1fr 1fr;
  }
`;

// CSS custom properties
:root {
  --ds-breakpoint-sm: 640px;
  --ds-breakpoint-md: 768px;
  --ds-breakpoint-lg: 1024px;
}
```

## 🌟 Shadow Tokens

### Shadow Scale
```tsx
export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
} as const;
```

### Semantic Shadows
```tsx
export const semanticShadows = {
  // Component shadows
  button: shadows.sm,
  card: shadows.base,
  modal: shadows.xl,
  dropdown: shadows.lg,
  
  // Interactive shadows
  hover: shadows.md,
  focus: '0 0 0 3px rgb(37 99 235 / 0.1)', // Primary color with opacity
  
  // Polish business shadows
  invoice: shadows.base,
  receipt: shadows.sm,
  document: shadows.md,
} as const;
```

## 🔄 Border Radius Tokens

### Border Radius Scale
```tsx
export const borderRadius = {
  none: '0',
  sm: '0.125rem',   // 2px
  base: '0.25rem',  // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  '3xl': '1.5rem',  // 24px
  full: '9999px',   // Fully rounded
} as const;
```

### Semantic Border Radius
```tsx
export const semanticBorderRadius = {
  // Component border radius
  button: borderRadius.md,
  input: borderRadius.md,
  card: borderRadius.lg,
  modal: borderRadius.xl,
  
  // Polish business border radius
  invoice: borderRadius.lg,
  badge: borderRadius.full,
  document: borderRadius.base,
} as const;
```

## 🎯 Using Design Tokens

### Import Tokens
```tsx
// Import specific token categories
import { colors, spacing, typography } from '@faktulove/design-system/tokens';

// Import all tokens
import * as tokens from '@faktulove/design-system/tokens';
```

### TypeScript Support
```tsx
// Tokens are fully typed
type ColorScale = typeof colors.primary;
type SpacingValue = keyof typeof spacing;
type FontSize = keyof typeof fontSize;

// Use in component props
interface ComponentProps {
  color?: keyof typeof colors.primary;
  spacing?: keyof typeof spacing;
  fontSize?: keyof typeof fontSize;
}
```

### CSS Custom Properties
```css
/* All tokens are available as CSS custom properties */
.my-component {
  color: var(--ds-color-primary-600);
  font-size: var(--ds-font-size-lg);
  padding: var(--ds-spacing-4);
  border-radius: var(--ds-border-radius-md);
  box-shadow: var(--ds-shadow-base);
}
```

### JavaScript/TypeScript Usage
```tsx
// In styled components
const StyledButton = styled.button`
  background-color: ${colors.primary[600]};
  padding: ${spacing[3]} ${spacing[6]};
  font-size: ${fontSize.base};
  border-radius: ${borderRadius.md};
  box-shadow: ${shadows.sm};
`;

// In inline styles
const buttonStyle = {
  backgroundColor: colors.primary[600],
  padding: `${spacing[3]} ${spacing[6]}`,
  fontSize: fontSize.base,
  borderRadius: borderRadius.md,
  boxShadow: shadows.sm,
};
```

## 🎨 Theme Customization

### Custom Theme Creation
```tsx
import { createTheme } from '@faktulove/design-system';

const customTheme = createTheme({
  colors: {
    primary: {
      600: '#your-brand-color',
    },
  },
  spacing: {
    // Override specific spacing values
    4: '1.2rem', // Custom 16px equivalent
  },
  typography: {
    fontFamily: {
      sans: ['Your Font', ...typography.fontFamily.sans],
    },
  },
});
```

### Polish Business Theme
```tsx
const polishBusinessTheme = createTheme({
  colors: {
    // Polish business-optimized colors
    primary: polishBusinessColors.currency.pln,
    success: polishBusinessColors.vat.standard,
    warning: polishBusinessColors.vat.reduced,
  },
  typography: {
    // Optimized for Polish text
    lineHeight: {
      normal: '1.6', // Slightly more space for Polish diacritics
    },
  },
});
```

## 📚 Token Documentation

### Token Naming Convention
- **Prefix**: All tokens use `ds-` prefix in CSS
- **Category**: Color, spacing, typography, etc.
- **Scale**: Numeric scale (50-900 for colors, 1-96 for spacing)
- **Semantic**: Descriptive names for specific use cases

### Token Categories
1. **Colors**: Brand colors, semantic colors, neutral colors
2. **Typography**: Font families, sizes, weights, line heights
3. **Spacing**: Margins, padding, gaps (8px grid system)
4. **Breakpoints**: Responsive design breakpoints
5. **Shadows**: Elevation and depth
6. **Border Radius**: Corner rounding
7. **Polish Business**: Specialized tokens for Polish business needs

---

**Design tokens ensure consistency and make it easy to maintain and scale the design system.** 🎨