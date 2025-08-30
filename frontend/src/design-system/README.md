# FaktuLove Design System

A comprehensive design system for FaktuLove, providing consistent visual language, accessibility standards, and reusable components aligned with Polish business and accounting needs.

## Overview

The FaktuLove Design System is built on a token-based architecture that separates design decisions from implementation details, enabling consistent theming across React components and future platform extensions.

### Key Features

- 🎨 **Token-based Architecture**: Consistent design tokens for colors, typography, spacing, and more
- ♿ **Accessibility First**: WCAG 2.1 Level AA compliance with Polish language support
- 🇵🇱 **Polish Business Context**: Specialized components for Polish accounting and business needs
- 📱 **Responsive Design**: Mobile-first approach with Polish business application patterns
- 🔧 **TypeScript Support**: Full type safety with comprehensive interfaces
- 🎯 **Developer Experience**: Comprehensive documentation and testing utilities

## Installation

The design system is already integrated into the FaktuLove frontend. To use it in your components:

```typescript
import { Button, Input, colors, spacing } from '@/design-system';
```

## Architecture

### Token System

The design system follows a three-tier token architecture:

1. **Global Tokens**: Core design decisions (colors, typography, spacing)
2. **Semantic Tokens**: Context-specific mappings (primary, success, warning)
3. **Component Tokens**: Component-specific overrides and variations

```
Global Tokens → Semantic Tokens → Component Tokens → Components
```

### File Structure

```
src/design-system/
├── tokens/              # Design tokens
│   ├── colors.ts       # Color palette definitions
│   ├── typography.ts   # Font scales and families
│   ├── spacing.ts      # Spacing scale (8px grid)
│   ├── breakpoints.ts  # Responsive breakpoints
│   ├── shadows.ts      # Elevation system
│   └── borderRadius.ts # Border radius scale
├── components/         # React components
│   ├── primitives/     # Base components (Button, Input)
│   ├── patterns/       # Composite components (Form, Card)
│   └── layouts/        # Layout components (Grid, Container)
├── utils/              # Utility functions
│   ├── theme.ts        # Theme utilities
│   ├── accessibility.ts # A11y helpers
│   └── responsive.ts   # Responsive utilities
├── styles/             # CSS files
│   ├── tokens.css      # CSS custom properties
│   ├── base.css        # Base styles
│   └── utilities.css   # Utility classes
├── types/              # TypeScript definitions
└── config.ts           # Design system configuration
```

## Design Tokens

### Colors

The color system is designed for Polish business applications with semantic meaning:

```typescript
import { colors, semanticColors } from '@/design-system';

// Brand colors
colors.primary[600]  // #2563eb - FaktuLove brand blue
colors.success[600]  // #059669 - Polish business success green
colors.warning[600]  // #d97706 - Polish business warning orange

// Semantic colors
semanticColors.textPrimary      // Main text color
semanticColors.interactive      // Interactive elements
semanticColors.statusSuccess    // Success states
```

### Typography

Inter font family with full Polish character support:

```typescript
import { typography, typographyStyles } from '@/design-system';

// Font scales
typography.fontSize.base    // 1rem (16px)
typography.fontSize.lg      // 1.125rem (18px)

// Semantic styles
typographyStyles.h1         // Heading 1 style
typographyStyles.body       // Body text style
typographyStyles.button     // Button text style
```

### Spacing

8px grid-based spacing system:

```typescript
import { spacing, semanticSpacing } from '@/design-system';

// Base spacing
spacing[2]  // 0.5rem (8px) - base unit
spacing[4]  // 1rem (16px) - 2x base
spacing[6]  // 1.5rem (24px) - 3x base

// Semantic spacing
semanticSpacing.componentPadding    // Standard component padding
semanticSpacing.layoutSpacing       // Layout spacing
semanticSpacing.formFieldSpacing    // Form field spacing
```

## Components

### Primitive Components

Basic building blocks with minimal styling:

```typescript
import { Button, Input, Select } from '@/design-system';

// Button with variants
<Button variant="primary" size="md">
  Save Invoice
</Button>

// Input with Polish formatting
<Input
  type="text"
  label="NIP"
  placeholder="123-456-78-90"
  className="nip-format"
/>

// Select with Polish options
<Select
  label="VAT Rate"
  options={[
    { value: '0.23', label: '23%' },
    { value: '0.08', label: '8%' },
    { value: '0.05', label: '5%' },
    { value: '0', label: '0%' },
    { value: '-1', label: 'zw.' }
  ]}
/>
```

### Polish Business Components

Specialized components for Polish accounting:

```typescript
import { CurrencyInput, DatePicker, NIPValidator } from '@/design-system';

// Currency input with PLN formatting
<CurrencyInput
  label="Amount"
  value={1234.56}
  currency="PLN"
  locale="pl-PL"
/>

// Date picker with Polish format
<DatePicker
  label="Issue Date"
  format="DD.MM.YYYY"
  locale="pl-PL"
/>

// NIP validator
<NIPValidator
  value="1234567890"
  onValidation={(isValid) => console.log(isValid)}
/>
```

## Responsive Design

Mobile-first responsive utilities:

```typescript
import { useBreakpoint, useResponsiveValue } from '@/design-system';

// Responsive hook
const isMobile = useBreakpoint('md'); // true if >= md breakpoint

// Responsive values
const columns = useResponsiveValue({
  xs: 1,
  md: 2,
  lg: 3
});
```

## Accessibility

Built-in accessibility features:

```typescript
import { ariaUtils, focusUtils, screenReaderUtils } from '@/design-system';

// ARIA utilities
const buttonProps = {
  ...ariaUtils.expanded(isOpen),
  ...ariaUtils.describedBy('help-text')
};

// Focus management
const cleanup = focusUtils.trapFocus(modalElement);

// Screen reader announcements
screenReaderUtils.announce('Invoice saved successfully', 'polite');
```

## Polish Language Support

### Currency Formatting

```typescript
import { polishA11yUtils } from '@/design-system';

// Format currency for screen readers
const announcement = polishA11yUtils.formatCurrencyForScreenReader(1234.56);
// "1234,56 złotych"
```

### Date Formatting

```typescript
// Format date for screen readers
const dateAnnouncement = polishA11yUtils.formatDateForScreenReader(new Date());
// "15 stycznia 2025"
```

### Business Terms

```typescript
import { designSystemConfig } from '@/design-system';

const terms = designSystemConfig.polish.terms;
console.log(terms.invoice);     // "Faktura"
console.log(terms.contractor);  // "Kontrahent"
console.log(terms.amount);      // "Kwota"
```

## CSS Custom Properties

The design system generates CSS custom properties for runtime theming:

```css
:root {
  --color-primary-600: #2563eb;
  --color-text-primary: #171717;
  --spacing-4: 1rem;
  --font-size-base: 1rem;
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
```

## Testing

Comprehensive testing utilities:

```typescript
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from '@/design-system';

expect.extend(toHaveNoViolations);

test('Button meets accessibility standards', async () => {
  const { container } = render(<Button>Test</Button>);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Development

### Adding New Components

1. Create component in appropriate directory (`primitives/`, `patterns/`, `layouts/`)
2. Add TypeScript interfaces in `types/index.ts`
3. Export from `components/index.ts`
4. Add tests in `__tests__/`
5. Update documentation

### Design Token Updates

1. Update token files in `tokens/`
2. Update CSS custom properties in `styles/tokens.css`
3. Update Tailwind configuration if needed
4. Run tests to ensure compatibility

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the established patterns and conventions
2. Ensure accessibility compliance (WCAG 2.1 Level AA)
3. Add comprehensive tests
4. Update documentation
5. Consider Polish business context

## License

Internal use only - FaktuLove Design System