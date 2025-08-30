# FaktuLove Design System

A comprehensive design system for building consistent, accessible, and scalable user interfaces for Polish business applications.

## 🎯 Overview

The FaktuLove Design System provides a unified visual language and component library specifically designed for Polish business and accounting needs. It ensures consistency across all user interfaces while maintaining high accessibility standards and cultural appropriateness.

### Key Features

- **Polish Business Focus**: Components and patterns tailored for Polish accounting and business workflows
- **Accessibility First**: WCAG 2.1 Level AA compliance with Polish language support
- **Type Safety**: Full TypeScript support with comprehensive type definitions
- **Theme System**: Support for light, dark, and high-contrast themes
- **Responsive Design**: Mobile-first approach with Polish business user preferences
- **Performance Optimized**: Lightweight components with minimal bundle impact

## 🚀 Quick Start

### Installation

```bash
npm install @faktulove/design-system
```

### Basic Usage

```tsx
import React from 'react';
import { Button, Input, Card } from '@faktulove/design-system';
import '@faktulove/design-system/styles';

function App() {
  return (
    <Card>
      <Card.Header>
        <h2>Faktura</h2>
      </Card.Header>
      <Card.Body>
        <Input 
          placeholder="Numer faktury" 
          aria-label="Numer faktury"
        />
        <Button variant="primary">
          Zapisz fakturę
        </Button>
      </Card.Body>
    </Card>
  );
}
```

### With Theme Provider

```tsx
import React from 'react';
import { ThemeProvider, Button } from '@faktulove/design-system';

function App() {
  return (
    <ThemeProvider theme="light">
      <Button variant="primary">
        Themed Button
      </Button>
    </ThemeProvider>
  );
}
```

## 📚 Documentation Structure

- [**Getting Started**](./getting-started.md) - Installation and setup guide
- [**Design Tokens**](./design-tokens.md) - Colors, typography, spacing, and more
- [**Components**](./components/README.md) - Complete component documentation
- [**Accessibility**](./accessibility.md) - Accessibility guidelines and features
- [**Polish Business**](./polish-business.md) - Polish-specific components and patterns
- [**Migration Guide**](./migration-guide.md) - Migrating from existing components
- [**Contributing**](./contributing.md) - How to contribute to the design system

## 🎨 Design Principles

### 1. Consistency
All components follow consistent visual patterns and interaction behaviors to create a cohesive user experience.

### 2. Accessibility
Every component meets WCAG 2.1 Level AA standards with proper ARIA support and keyboard navigation.

### 3. Polish Business Context
Components are designed with Polish business culture and accounting practices in mind.

### 4. Performance
Lightweight, tree-shakeable components that don't impact application performance.

### 5. Developer Experience
Comprehensive TypeScript support, clear documentation, and intuitive APIs.

## 🧩 Component Categories

### Primitive Components
Basic building blocks for creating interfaces:
- [Button](./components/primitives/Button.md) - Primary, secondary, ghost, and danger variants
- [Input](./components/primitives/Input.md) - Text inputs with validation states
- [Select](./components/primitives/Select.md) - Dropdown selections
- [Checkbox](./components/primitives/Checkbox.md) - Boolean selections
- [Radio](./components/primitives/Radio.md) - Single choice selections
- [Switch](./components/primitives/Switch.md) - Toggle switches

### Pattern Components
Composite components for common use cases:
- [Card](./components/patterns/Card.md) - Content containers
- [Form](./components/patterns/Form.md) - Form layouts with validation
- [Table](./components/patterns/Table.md) - Data tables with sorting and pagination

### Layout Components
Structural components for page organization:
- [Grid](./components/layouts/Grid.md) - CSS Grid-based layouts
- [Container](./components/layouts/Container.md) - Max-width containers
- [Stack](./components/layouts/Stack.md) - Vertical and horizontal spacing

### Polish Business Components
Specialized components for Polish business needs:
- [CurrencyInput](./components/business/CurrencyInput.md) - PLN currency formatting
- [DatePicker](./components/business/DatePicker.md) - Polish date formats
- [VATRateSelector](./components/business/VATRateSelector.md) - Polish VAT rates
- [NIPValidator](./components/business/NIPValidator.md) - NIP number validation
- [InvoiceStatusBadge](./components/business/InvoiceStatusBadge.md) - Invoice status indicators

## 🎨 Design Tokens

### Colors
```tsx
import { colors } from '@faktulove/design-system/tokens';

// Primary brand color
colors.primary[600] // #2563eb

// Success states
colors.success[600] // #059669

// Warning states
colors.warning[600] // #d97706
```

### Typography
```tsx
import { typography } from '@faktulove/design-system/tokens';

// Font family with Polish character support
typography.fontFamily.sans // 'Inter', sans-serif

// Font sizes following 8px grid
typography.fontSize.lg // 1.125rem (18px)
```

### Spacing
```tsx
import { spacing } from '@faktulove/design-system/tokens';

// 8px grid system
spacing[4] // 1rem (16px)
spacing[8] // 2rem (32px)
```

## ♿ Accessibility Features

### WCAG 2.1 Level AA Compliance
- Color contrast ratios of 4.5:1 or higher
- Proper focus indicators on all interactive elements
- Screen reader support with ARIA labels
- Keyboard navigation for all components

### Polish Language Support
- Proper language attributes for Polish content
- Screen reader announcements in Polish
- Polish keyboard layout considerations
- Cultural color and interaction patterns

### Testing
```bash
# Run accessibility tests
npm run test:a11y

# Run comprehensive accessibility audit
npm run test:design-system --a11y
```

## 🌍 Internationalization

### Polish Business Context
- Currency formatting for PLN (Polish Złoty)
- Date formats (DD.MM.YYYY)
- NIP (Tax Identification Number) validation
- Polish VAT rates (23%, 8%, 5%, 0%)
- Business terminology in Polish

### Text Length Considerations
Components accommodate longer Polish text lengths compared to English, ensuring proper layout and readability.

## 🎭 Theming

### Available Themes
- **Light Theme**: Default theme for general use
- **Dark Theme**: Reduced eye strain for extended use
- **High Contrast**: Enhanced accessibility for users with visual impairments

### Theme Usage
```tsx
import { ThemeProvider } from '@faktulove/design-system';

function App() {
  return (
    <ThemeProvider theme="dark">
      {/* Your app content */}
    </ThemeProvider>
  );
}
```

### Custom Themes
```tsx
import { createTheme } from '@faktulove/design-system';

const customTheme = createTheme({
  colors: {
    primary: {
      600: '#your-brand-color',
    },
  },
});
```

## 📱 Responsive Design

### Breakpoints
```tsx
import { breakpoints } from '@faktulove/design-system/tokens';

breakpoints.sm  // 640px
breakpoints.md  // 768px
breakpoints.lg  // 1024px
breakpoints.xl  // 1280px
```

### Responsive Components
```tsx
<Grid 
  cols={{ base: 1, md: 2, lg: 3 }}
  gap={4}
>
  <div>Responsive grid item</div>
</Grid>
```

## 🧪 Testing

### Test Utilities
```tsx
import { renderWithA11y, testPolishA11y } from '@faktulove/design-system/testing';

test('component is accessible', async () => {
  const { container } = renderWithA11y(<Button>Test</Button>);
  await testPolishA11y(container);
});
```

### Visual Regression Testing
```bash
# Run visual regression tests
npm run test:visual
```

### Performance Testing
```bash
# Run performance tests
npm run test:performance
```

## 🔧 Development

### Local Development
```bash
# Install dependencies
npm install

# Start Storybook
npm run storybook

# Run tests
npm run test:design-system

# Build design system
npm run build
```

### Contributing
See our [Contributing Guide](./contributing.md) for information on how to contribute to the design system.

## 📦 Bundle Size

The design system is optimized for minimal bundle impact:
- Tree-shakeable components
- CSS-in-JS with automatic purging
- Lazy-loaded theme assets
- Optimized icon sets

## 🆘 Support

### Getting Help
- [GitHub Issues](https://github.com/faktulove/design-system/issues) - Bug reports and feature requests
- [Discussions](https://github.com/faktulove/design-system/discussions) - Questions and community support
- [Storybook](http://localhost:6006) - Interactive component documentation

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.

---

**Made with ❤️ for Polish businesses by the FaktuLove team**