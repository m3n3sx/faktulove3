# FaktuLove Design System Storybook

This Storybook instance provides comprehensive documentation and testing for the FaktuLove Design System components.

## Setup

The Storybook is configured with the following addons:

- **@storybook/preset-create-react-app**: Compatibility with Create React App
- **@storybook/addon-essentials**: Core Storybook functionality
- **@storybook/addon-a11y**: Accessibility testing and validation
- **@storybook/addon-docs**: Auto-generated documentation
- **@storybook/addon-controls**: Interactive component controls
- **@storybook/addon-actions**: Action logging for events
- **@storybook/addon-viewport**: Responsive design testing

## Accessibility Features

All component stories include accessibility testing with:

- **Color contrast validation**: Ensures WCAG 2.1 Level AA compliance
- **Keyboard navigation testing**: Validates proper focus management
- **Screen reader compatibility**: Tests ARIA labels and semantic markup
- **Interactive controls**: Test different component states and props

## Component Coverage

### Primitive Components

#### Button (`/primitives/Button`)
- **Basic variants**: Primary, secondary, ghost, danger
- **Size variants**: xs, sm, md, lg, xl
- **States**: Normal, disabled, loading
- **Icons**: Start and end icon support
- **Polish business variants**: Invoice, contractor, payment actions
- **Accessibility**: Full keyboard navigation, ARIA labels

#### Input (`/primitives/Input`)
- **Input types**: Text, email, password, number, tel, search
- **Size variants**: xs, sm, md, lg, xl
- **States**: Normal, disabled, readonly, error, required
- **Icons**: Start and end positioning
- **Polish business inputs**: Currency, NIP, REGON, postal code, phone
- **Validation**: Real-time validation with Polish patterns
- **Accessibility**: Proper labeling, error announcements

#### Other Primitives
- **Checkbox**: Standard and indeterminate states
- **Radio**: Individual and grouped radio buttons
- **Select**: Single and multi-select with search
- **Switch**: Toggle switches for boolean settings

### Pattern Components

#### Form (`/patterns/Form`)
- **Validation modes**: onChange, onBlur, onSubmit
- **Polish business forms**: NIP, REGON, VAT validation
- **Real-time validation**: Custom validation rules
- **Loading states**: Form submission handling
- **Initial values**: Pre-populated forms
- **Accessibility**: Form field associations, error handling

#### Card (`/patterns/Card`)
- **Layout variants**: Header, body, footer sections
- **Content types**: Text, images, actions
- **Responsive behavior**: Mobile-first design
- **Polish business context**: Invoice cards, contractor cards

#### Table (`/patterns/Table`)
- **Data display**: Sortable columns, pagination
- **Polish formatting**: Currency, dates, NIP numbers
- **Row selection**: Single and multi-select
- **Responsive design**: Mobile table patterns
- **Accessibility**: Table headers, row descriptions

### Layout Components

#### Grid (`/layouts/Grid`)
- **Column configurations**: 1-12 columns
- **Responsive breakpoints**: xs, sm, md, lg, xl
- **Auto-fit behavior**: Dynamic column sizing
- **Gap variations**: 0-12 spacing units
- **Real-world examples**: Dashboard layouts, card grids

#### Other Layouts
- **Container**: Max-width containers with responsive padding
- **Flex**: Flexbox utilities with gap support
- **Stack**: Vertical and horizontal spacing utilities
- **Sidebar**: Collapsible navigation sidebar
- **Breadcrumb**: Navigation hierarchy display

### Business Components

#### CurrencyInput (`/business/CurrencyInput`)
- **Currency support**: PLN, EUR, USD, GBP
- **Decimal precision**: 0-4 decimal places
- **Negative values**: Optional negative amount support
- **Polish formatting**: Comma decimal separator
- **Real-time formatting**: Focus/blur behavior
- **Business scenarios**: Invoices, payments, corrections

#### InvoiceStatusBadge (`/business/InvoiceStatusBadge`)
- **Status types**: Draft, sent, viewed, paid, overdue, cancelled, corrected
- **Size variants**: sm, md, lg
- **Polish labels**: Localized status names
- **Status workflows**: Business process visualization
- **Icons**: Status-appropriate icons
- **Accessibility**: High contrast colors, semantic markup

#### Other Business Components
- **DatePicker**: Polish date format (DD.MM.YYYY)
- **VATRateSelector**: Standard Polish VAT rates
- **NIPValidator**: Real-time NIP validation
- **ComplianceIndicator**: Regulatory compliance status

## Usage Guidelines

### Story Structure

Each component story follows this structure:

```typescript
export const StoryName: Story = {
  args: {
    // Component props
  },
  parameters: {
    docs: {
      description: {
        story: 'Description of what this story demonstrates',
      },
    },
  },
};
```

### Accessibility Testing

All stories include accessibility configuration:

```typescript
parameters: {
  a11y: {
    config: {
      rules: [
        { id: 'color-contrast', enabled: true },
        { id: 'keyboard-navigation', enabled: true },
        { id: 'label', enabled: true },
      ],
    },
  },
}
```

### Interactive Controls

Stories use Storybook controls for interactive testing:

```typescript
argTypes: {
  variant: {
    control: 'select',
    options: ['primary', 'secondary', 'ghost'],
    description: 'Visual variant of the component',
  },
  disabled: {
    control: 'boolean',
    description: 'Whether the component is disabled',
  },
}
```

## Polish Business Context

The design system includes specialized components for Polish business needs:

- **Currency formatting**: PLN with comma decimal separator
- **Date formatting**: DD.MM.YYYY format
- **VAT rates**: 23%, 8%, 5%, 0%, exempt
- **NIP validation**: Real-time Polish tax number validation
- **REGON validation**: 9 and 14-digit business registry numbers
- **Postal codes**: Polish XX-XXX format
- **Phone numbers**: Polish mobile and landline formats

## Development Workflow

1. **Component Development**: Create component with TypeScript interfaces
2. **Story Creation**: Write comprehensive stories covering all variants
3. **Accessibility Testing**: Ensure WCAG compliance with a11y addon
4. **Documentation**: Add usage guidelines and examples
5. **Visual Testing**: Test across different viewports and themes

## Running Storybook

```bash
# Development server
npm run storybook

# Build static version
npm run build-storybook
```

## Browser Support

The design system supports:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

When adding new components:

1. Create the component with proper TypeScript interfaces
2. Write comprehensive stories covering all use cases
3. Include accessibility testing configuration
4. Add Polish business context where relevant
5. Document usage guidelines and best practices
6. Test across different screen sizes and themes

## Resources

- [Storybook Documentation](https://storybook.js.org/docs)
- [Accessibility Addon](https://storybook.js.org/addons/@storybook/addon-a11y)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Polish Business Regulations](https://www.gov.pl/web/kas)