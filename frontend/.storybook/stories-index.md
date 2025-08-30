# FaktuLove Design System - Story Index

This document provides an overview of all component stories available in the Storybook.

## Primitive Components

### Button
**Location**: `src/design-system/components/primitives/Button/Button.stories.tsx`

**Stories**:
- `Primary` - Primary button variant
- `Secondary` - Secondary button variant  
- `Ghost` - Ghost button variant
- `Danger` - Danger button variant
- `Sizes` - All size variants (xs, sm, md, lg, xl)
- `States` - Normal, disabled, and loading states
- `WithIcons` - Buttons with start and end icons
- `FullWidth` - Full-width button variants
- `PolishBusinessVariants` - Polish business-specific buttons
- `InvoiceActions` - Invoice-specific action buttons
- `VATRates` - VAT rate selection buttons
- `StatusToggles` - Invoice status toggle buttons
- `AccessibilityFeatures` - Accessibility demonstration
- `Playground` - Interactive testing

**Accessibility Features**:
- Color contrast validation
- Button name validation
- Keyboard navigation testing
- ARIA label support

### Input
**Location**: `src/design-system/components/primitives/Input/Input.stories.tsx`

**Stories**:
- `Default` - Basic input component
- `WithHelperText` - Input with helper text
- `Required` - Required field indicator
- `WithError` - Error state display
- `InputTypes` - Different input types (text, email, password, etc.)
- `Sizes` - All size variants
- `States` - Normal, disabled, readonly, error states
- `WithIcons` - Inputs with icons
- `PolishBusinessInputs` - Currency, NIP, REGON, postal code, phone inputs
- `CurrencyVariants` - Different currency configurations
- `ValidationExamples` - Real-time validation examples
- `PhoneVariants` - Phone input variations
- `AccessibilityFeatures` - Accessibility demonstration
- `Playground` - Interactive testing

**Accessibility Features**:
- Label association validation
- ARIA input field name validation
- Error message announcements
- Keyboard navigation support

### Other Primitives
- **Checkbox**: `Checkbox.stories.tsx` - Standard and indeterminate states
- **Radio**: `Radio.stories.tsx` - Individual and grouped radio buttons
- **Select**: `Select.stories.tsx` - Single and multi-select options
- **Switch**: `Switch.stories.tsx` - Toggle switches for boolean settings

## Pattern Components

### Form
**Location**: `src/design-system/components/patterns/Form/Form.stories.tsx`

**Stories**:
- `Basic` - Simple form with validation
- `PolishBusiness` - Polish business form with NIP/REGON validation
- `RealTimeValidation` - Real-time validation example
- `WithLoadingState` - Form with loading state
- `WithInitialValues` - Pre-populated form
- `ValidationModes` - Different validation timing modes

**Accessibility Features**:
- Form field associations
- Error message handling
- Required field indicators
- Keyboard navigation

### Card
**Location**: `src/design-system/components/patterns/Card/Card.stories.tsx`

**Stories**:
- Basic card layouts
- Header, body, footer sections
- Interactive cards
- Polish business card examples

### Table
**Location**: `src/design-system/components/patterns/Table/Table.stories.tsx`

**Stories**:
- Data display with sorting
- Pagination examples
- Polish formatting (currency, dates)
- Row selection
- Responsive table patterns

## Layout Components

### Grid
**Location**: `src/design-system/components/layouts/Grid/Grid.stories.tsx`

**Stories**:
- `Default` - Basic grid layout
- `ColumnVariations` - 2, 3, 4 column layouts
- `GapVariations` - Different gap sizes (0, 2, 4, 8)
- `ResponsiveGrid` - Responsive breakpoint behavior
- `AutoFitGrid` - Auto-fit grid with minimum item widths
- `CardGrid` - Real-world card layout example
- `DashboardLayout` - Complex dashboard layout
- `Playground` - Interactive testing

**Accessibility Features**:
- Semantic markup
- Responsive behavior
- Color contrast validation

### Other Layouts
- **Container**: Max-width containers with responsive padding
- **Flex**: Flexbox utilities with gap support
- **Stack**: Vertical and horizontal spacing utilities
- **Sidebar**: Collapsible navigation sidebar
- **Breadcrumb**: Navigation hierarchy display

## Business Components

### CurrencyInput
**Location**: `src/design-system/components/business/CurrencyInput/CurrencyInput.stories.tsx`

**Stories**:
- `Default` - Basic currency input
- `WithValue` - Pre-filled currency value
- `Currencies` - PLN, EUR, USD, GBP support
- `DecimalPrecision` - 0, 2, 4 decimal places
- `NegativeValues` - Positive only vs. negative allowed
- `States` - Normal, disabled, error states
- `PolishBusinessScenarios` - Invoice and payment scenarios
- `FormattingBehavior` - Focus/blur formatting demonstration
- `AccessibilityFeatures` - Accessibility demonstration
- `Playground` - Interactive testing

**Polish Business Features**:
- PLN currency formatting
- Comma decimal separator
- Invoice and payment contexts
- VAT amount calculations
- Correction and refund scenarios

### InvoiceStatusBadge
**Location**: `src/design-system/components/business/InvoiceStatusBadge/InvoiceStatusBadge.stories.tsx`

**Stories**:
- `Default` - Basic status badge
- `AllStatuses` - All available invoice statuses
- `Sizes` - Small, medium, large variants
- `StatusWorkflow` - Business process visualization
- `StatusCategories` - Positive, neutral, problematic groupings
- `InTableContext` - Usage in invoice tables
- `CustomStyling` - Custom styling examples
- `AccessibilityFeatures` - Accessibility demonstration
- `Playground` - Interactive testing

**Polish Business Features**:
- Polish status labels (Szkic, Wysłana, Opłacona, etc.)
- Business workflow visualization
- Status-appropriate colors and icons
- Table integration examples

### Other Business Components
- **DatePicker**: Polish date format (DD.MM.YYYY)
- **VATRateSelector**: Standard Polish VAT rates (23%, 8%, 5%, 0%)
- **NIPValidator**: Real-time NIP validation with formatting
- **ComplianceIndicator**: Regulatory compliance status

## Story Categories

### Accessibility Stories
Every component includes accessibility-focused stories:
- **AccessibilityFeatures**: Demonstrates ARIA labels, descriptions, keyboard navigation
- **Color contrast validation**: Ensures WCAG 2.1 Level AA compliance
- **Keyboard navigation**: Tests focus management and keyboard interactions
- **Screen reader support**: Validates semantic markup and announcements

### Polish Business Stories
Components include Polish business context:
- **PolishBusinessVariants**: Business-specific component variants
- **PolishBusinessScenarios**: Real-world usage examples
- **Polish formatting**: Currency, dates, phone numbers, postal codes
- **Regulatory compliance**: NIP, REGON, VAT validation

### Interactive Stories
All components include interactive testing:
- **Playground**: Interactive controls for all props
- **States**: Different component states (normal, disabled, error, loading)
- **Variants**: Visual and functional variants
- **Sizes**: Different size options

### Real-world Examples
Components include practical usage examples:
- **Dashboard layouts**: Complex grid arrangements
- **Form scenarios**: Complete form workflows
- **Table contexts**: Data display patterns
- **Card layouts**: Content organization

## Testing Coverage

### Accessibility Testing
- **Color contrast**: WCAG 2.1 Level AA compliance
- **Keyboard navigation**: Full keyboard accessibility
- **Screen reader compatibility**: Proper ARIA markup
- **Focus management**: Logical focus order

### Responsive Testing
- **Breakpoint behavior**: xs, sm, md, lg, xl breakpoints
- **Mobile-first design**: Progressive enhancement
- **Viewport testing**: Different screen sizes
- **Touch interactions**: Mobile-friendly controls

### Polish Business Testing
- **Currency formatting**: PLN with comma separator
- **Date formatting**: DD.MM.YYYY format
- **Number validation**: NIP, REGON, phone validation
- **Business workflows**: Invoice lifecycle testing

## Usage Guidelines

### Creating New Stories
1. Use the story template: `.storybook/story-template.tsx`
2. Include accessibility configuration
3. Add Polish business context where relevant
4. Create comprehensive variant coverage
5. Include real-world usage examples

### Story Naming Convention
- Use descriptive names: `WithIcons`, `PolishBusinessScenarios`
- Group related stories: `Sizes`, `States`, `Variants`
- Include context: `InTableContext`, `DashboardLayout`
- End with `Playground` for interactive testing

### Documentation Standards
- Include component descriptions
- Document all props and variants
- Explain Polish business context
- Provide usage guidelines
- Include accessibility notes

## Resources

- [Storybook Best Practices](https://storybook.js.org/docs/writing-stories/introduction)
- [Accessibility Testing](https://storybook.js.org/addons/@storybook/addon-a11y)
- [Polish Business Regulations](https://www.gov.pl/web/kas)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)