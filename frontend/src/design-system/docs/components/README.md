# Components Documentation

The FaktuLove Design System provides a comprehensive set of components organized into four main categories. Each component is designed with accessibility, Polish business needs, and developer experience in mind.

## 🧩 Component Categories

### [Primitive Components](./primitives/README.md)
Basic building blocks that form the foundation of the design system.

- **[Button](./primitives/Button.md)** - Primary, secondary, ghost, and danger button variants
- **[Input](./primitives/Input.md)** - Text inputs with validation states and Polish formatting
- **[Select](./primitives/Select.md)** - Dropdown selections with search and multi-select
- **[Checkbox](./primitives/Checkbox.md)** - Boolean selections with indeterminate state
- **[Radio](./primitives/Radio.md)** - Single choice selections in groups
- **[Switch](./primitives/Switch.md)** - Toggle switches for boolean settings

### [Pattern Components](./patterns/README.md)
Composite components that combine primitives for common use cases.

- **[Card](./patterns/Card.md)** - Content containers with headers, bodies, and footers
- **[Form](./patterns/Form.md)** - Form layouts with validation and Polish business patterns
- **[Table](./patterns/Table.md)** - Data tables with sorting, pagination, and Polish formatting
- **[Modal](./patterns/Modal.md)** - Overlay dialogs with focus management
- **[Toast](./patterns/Toast.md)** - Notification system with Polish messages

### [Layout Components](./layouts/README.md)
Structural components for organizing page layouts and content.

- **[Container](./layouts/Container.md)** - Max-width containers with responsive padding
- **[Grid](./layouts/Grid.md)** - CSS Grid-based layout system
- **[Flex](./layouts/Flex.md)** - Flexbox utilities with gap support
- **[Stack](./layouts/Stack.md)** - Vertical and horizontal spacing utilities
- **[Sidebar](./layouts/Sidebar.md)** - Collapsible navigation sidebar
- **[Breadcrumb](./layouts/Breadcrumb.md)** - Navigation hierarchy display

### [Polish Business Components](./business/README.md)
Specialized components designed for Polish business and accounting needs.

- **[CurrencyInput](./business/CurrencyInput.md)** - PLN currency formatting and validation
- **[DatePicker](./business/DatePicker.md)** - Polish date formats (DD.MM.YYYY)
- **[VATRateSelector](./business/VATRateSelector.md)** - Polish VAT rates (23%, 8%, 5%, 0%)
- **[NIPValidator](./business/NIPValidator.md)** - Polish tax ID validation
- **[InvoiceStatusBadge](./business/InvoiceStatusBadge.md)** - Invoice lifecycle status
- **[ComplianceIndicator](./business/ComplianceIndicator.md)** - Regulatory compliance status

## 🎯 Component Design Principles

### Consistency
All components follow consistent design patterns:
- **Visual Hierarchy**: Clear typography and spacing scales
- **Color Usage**: Semantic color system with Polish business context
- **Interaction Patterns**: Consistent hover, focus, and active states
- **Sizing**: Standardized size variants (xs, sm, md, lg, xl)

### Accessibility
Every component meets WCAG 2.1 Level AA standards:
- **Keyboard Navigation**: Full keyboard support for all interactive elements
- **Screen Reader Support**: Proper ARIA labels and semantic markup
- **Focus Management**: Visible focus indicators and logical tab order
- **Color Contrast**: Minimum 4.5:1 contrast ratios
- **Polish Language**: Proper language attributes and screen reader support

### Polish Business Context
Components are tailored for Polish business applications:
- **Currency Formatting**: PLN (Polish Złoty) with proper decimal separators
- **Date Formats**: DD.MM.YYYY format preferred in business contexts
- **Tax System**: Polish VAT rates and NIP validation
- **Language**: Polish terminology and cultural conventions
- **Regulations**: Compliance with Polish accounting standards

### Developer Experience
Components are designed for ease of use:
- **TypeScript Support**: Comprehensive type definitions
- **Consistent APIs**: Similar prop patterns across components
- **Composition**: Components work well together
- **Documentation**: Clear examples and usage guidelines
- **Testing**: Built-in test utilities and accessibility testing

## 🚀 Quick Start

### Basic Usage
```tsx
import React from 'react';
import { 
  Button, 
  Input, 
  Card, 
  CurrencyInput 
} from '@faktulove/design-system';

function InvoiceForm() {
  return (
    <Card>
      <Card.Header>
        <h2>Nowa Faktura</h2>
      </Card.Header>
      <Card.Body>
        <Input 
          placeholder="Numer faktury" 
          aria-label="Numer faktury"
        />
        <CurrencyInput 
          currency="PLN"
          placeholder="Kwota"
          aria-label="Kwota faktury"
        />
      </Card.Body>
      <Card.Footer>
        <Button variant="primary">
          Zapisz Fakturę
        </Button>
      </Card.Footer>
    </Card>
  );
}
```

### With Theme Provider
```tsx
import { ThemeProvider } from '@faktulove/design-system';

function App() {
  return (
    <ThemeProvider theme="light">
      <InvoiceForm />
    </ThemeProvider>
  );
}
```

## 📋 Component API Patterns

### Common Props
Most components share these common props:

```tsx
interface BaseComponentProps {
  /**
   * Additional CSS classes
   */
  className?: string;
  
  /**
   * Inline styles
   */
  style?: React.CSSProperties;
  
  /**
   * Test identifier
   */
  'data-testid'?: string;
  
  /**
   * Accessible label (required for interactive components)
   */
  'aria-label'?: string;
  
  /**
   * Associated description element ID
   */
  'aria-describedby'?: string;
}
```

### Size Variants
Components with size variants use consistent sizing:

```tsx
type SizeVariant = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

// Usage
<Button size="lg">Large Button</Button>
<Input size="sm" placeholder="Small input" />
```

### Color Variants
Components use semantic color variants:

```tsx
type ColorVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error';

// Usage
<Button variant="primary">Primary Action</Button>
<Button variant="danger">Delete Item</Button>
```

### State Props
Interactive components support common states:

```tsx
interface StateProps {
  /**
   * Whether the component is disabled
   */
  disabled?: boolean;
  
  /**
   * Loading state with spinner
   */
  loading?: boolean;
  
  /**
   * Error message to display
   */
  error?: string;
  
  /**
   * Success message to display
   */
  success?: string;
}
```

## 🎨 Styling Components

### CSS Custom Properties
All components support CSS custom property overrides:

```tsx
<Button 
  style={{
    '--ds-button-bg': '#custom-color',
    '--ds-button-padding': '12px 24px',
  }}
>
  Custom Styled Button
</Button>
```

### CSS Classes
Components accept additional CSS classes:

```tsx
<Button className="my-custom-button">
  Styled Button
</Button>
```

### Styled Components
Components work well with styled-components:

```tsx
import styled from 'styled-components';
import { Button } from '@faktulove/design-system';

const CustomButton = styled(Button)`
  background: linear-gradient(45deg, #fe6b8b 30%, #ff8e53 90%);
  border-radius: 3px;
  border: 0;
  color: white;
  height: 48px;
  padding: 0 30px;
  box-shadow: 0 3px 5px 2px rgba(255, 105, 135, .3);
`;
```

## 🧪 Testing Components

### Accessibility Testing
```tsx
import { renderWithA11y, testPolishA11y } from '@faktulove/design-system/testing';

test('component is accessible', async () => {
  const { container } = renderWithA11y(
    <Button>Test Button</Button>
  );
  
  await testPolishA11y(container);
});
```

### Interaction Testing
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('button handles click events', async () => {
  const handleClick = jest.fn();
  const user = userEvent.setup();
  
  render(<Button onClick={handleClick}>Click me</Button>);
  
  await user.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

### Polish Business Testing
```tsx
test('currency input formats PLN correctly', async () => {
  const user = userEvent.setup();
  
  render(<CurrencyInput currency="PLN" />);
  
  const input = screen.getByRole('textbox');
  await user.type(input, '1234.56');
  
  expect(input).toHaveValue('1 234,56 zł');
});
```

## 📱 Responsive Design

### Responsive Props
Many components support responsive prop values:

```tsx
<Grid 
  cols={{ base: 1, md: 2, lg: 3 }}
  gap={{ base: 2, md: 4 }}
>
  <div>Responsive grid item</div>
</Grid>
```

### Breakpoint Utilities
```tsx
import { useBreakpoint } from '@faktulove/design-system';

function ResponsiveComponent() {
  const { isMobile, isTablet, isDesktop } = useBreakpoint();
  
  return (
    <div>
      {isMobile && <MobileView />}
      {isTablet && <TabletView />}
      {isDesktop && <DesktopView />}
    </div>
  );
}
```

## 🌍 Internationalization

### Polish Language Support
Components include proper Polish language support:

```tsx
// Automatic Polish formatting
<CurrencyInput currency="PLN" /> // Formats as "1 234,56 zł"
<DatePicker format="DD.MM.YYYY" /> // Polish date format
<VATRateSelector /> // Polish VAT rates

// Polish ARIA labels
<Button aria-label="Zapisz dokument">
  <SaveIcon />
</Button>
```

### Text Length Considerations
Components accommodate longer Polish text:

```tsx
// Components handle longer Polish translations
<Button>Zapisz i wyślij fakturę</Button> // Longer than English equivalent
```

## 🔧 Customization

### Theme Customization
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

### Component Variants
Create custom component variants:

```tsx
const CustomButton = ({ variant = 'custom', ...props }) => {
  return (
    <Button 
      {...props}
      className={`custom-button custom-button--${variant}`}
    />
  );
};
```

## 📚 Resources

### Storybook
Interactive component documentation and examples:
```bash
npm run storybook
# Open http://localhost:6006
```

### Component Source Code
All components are open source and available in the repository:
- [GitHub Repository](https://github.com/faktulove/design-system)
- [Component Source](https://github.com/faktulove/design-system/tree/main/src/components)

### Design Resources
- [Figma Design System](https://figma.com/faktulove-design-system)
- [Design Tokens](../design-tokens.md)
- [Accessibility Guidelines](../accessibility.md)

---

**Explore each component category to learn more about specific components and their usage patterns.** 🧩