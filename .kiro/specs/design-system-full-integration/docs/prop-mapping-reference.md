# Prop Mapping Reference

This document provides comprehensive prop mapping tables for migrating from legacy components to the design system components.

## Table of Contents

1. [Primitive Components](#primitive-components)
2. [Form Components](#form-components)
3. [Layout Components](#layout-components)
4. [Polish Business Components](#polish-business-components)
5. [Event Handler Mappings](#event-handler-mappings)
6. [CSS Class Mappings](#css-class-mappings)

## Primitive Components

### Button Component

| Legacy Prop/Class | Design System Prop | Type | Default | Notes |
|------------------|-------------------|------|---------|-------|
| `className="btn"` | Built-in | - | - | Base styling included |
| `className="btn-primary"` | `variant="primary"` | string | "default" | Semantic variants |
| `className="btn-secondary"` | `variant="secondary"` | string | "default" | |
| `className="btn-success"` | `variant="success"` | string | "default" | |
| `className="btn-danger"` | `variant="danger"` | string | "default" | |
| `className="btn-warning"` | `variant="warning"` | string | "default" | |
| `className="btn-info"` | `variant="info"` | string | "default" | |
| `className="btn-light"` | `variant="ghost"` | string | "default" | |
| `className="btn-dark"` | `variant="dark"` | string | "default" | |
| `className="btn-outline-*"` | `variant="outline"` | string | "default" | Use with `color` prop |
| `className="btn-sm"` | `size="sm"` | string | "md" | Size tokens |
| `className="btn-lg"` | `size="lg"` | string | "md" | |
| `className="btn-block"` | `fullWidth={true}` | boolean | false | Full width button |
| `disabled={true}` | `disabled={true}` | boolean | false | Same prop |
| `type="submit"` | `type="submit"` | string | "button" | Same prop |
| `onClick={handler}` | `onClick={handler}` | function | - | Same prop |
| Custom loading state | `loading={true}` | boolean | false | Built-in loading state |
| Custom icon | `icon={<Icon />}` | ReactNode | - | Built-in icon support |
| Custom icon position | `iconPosition="left"` | string | "left" | Icon positioning |

**Migration Example:**
```jsx
// Before
<button 
  className="btn btn-primary btn-lg btn-block"
  disabled={isLoading}
  onClick={handleSubmit}
>
  {isLoading ? 'Zapisywanie...' : 'Zapisz'}
</button>

// After
<Button
  variant="primary"
  size="lg"
  fullWidth
  loading={isLoading}
  onClick={handleSubmit}
>
  Zapisz
</Button>
```

### Input Component

| Legacy Prop/Class | Design System Prop | Type | Default | Notes |
|------------------|-------------------|------|---------|-------|
| `className="form-control"` | Built-in | - | - | Base styling included |
| `className="form-control-sm"` | `size="sm"` | string | "md" | Size variants |
| `className="form-control-lg"` | `size="lg"` | string | "md" | |
| `placeholder="text"` | `placeholder="text"` | string | - | Same prop |
| `value={value}` | `value={value}` | string | - | Same prop |
| `onChange={handler}` | `onChange={handler}` | function | - | Simplified handler |
| `onBlur={handler}` | `onBlur={handler}` | function | - | Same prop |
| `onFocus={handler}` | `onFocus={handler}` | function | - | Same prop |
| `required={true}` | `required={true}` | boolean | false | Same prop |
| `disabled={true}` | `disabled={true}` | boolean | false | Same prop |
| `readOnly={true}` | `readOnly={true}` | boolean | false | Same prop |
| `type="text"` | `type="text"` | string | "text" | Same prop |
| `type="email"` | `type="email"` | string | "text" | Same prop |
| `type="password"` | `type="password"` | string | "text" | Same prop |
| `type="number"` | `type="number"` | string | "text" | Same prop |
| `autoComplete="off"` | `autoComplete="off"` | string | - | Same prop |
| `maxLength={100}` | `maxLength={100}` | number | - | Same prop |
| `minLength={5}` | `minLength={5}` | number | - | Same prop |
| Manual label | `label="Label text"` | string | - | Built-in label |
| Manual error display | `error="Error message"` | string | - | Built-in error handling |
| Manual help text | `helpText="Help text"` | string | - | Built-in help text |
| Custom validation | `validation="email"` | string | - | Built-in validation |
| - | `validation="nip"` | string | - | Polish NIP validation |
| - | `validation="regon"` | string | - | Polish REGON validation |
| - | `validation="pesel"` | string | - | Polish PESEL validation |

**Migration Example:**
```jsx
// Before
<div className="form-group">
  <label htmlFor="email">Email</label>
  <input
    id="email"
    type="email"
    className="form-control"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
    required
  />
  {emailError && <div className="invalid-feedback">{emailError}</div>}
</div>

// After
<Input
  label="Email"
  type="email"
  value={email}
  onChange={setEmail}
  validation="email"
  required
  error={emailError}
/>
```

### Select Component

| Legacy Prop/Class | Design System Prop | Type | Default | Notes |
|------------------|-------------------|------|---------|-------|
| `className="form-select"` | Built-in | - | - | Base styling included |
| `className="form-select-sm"` | `size="sm"` | string | "md" | Size variants |
| `className="form-select-lg"` | `size="lg"` | string | "md" | |
| `value={value}` | `value={value}` | string | - | Same prop |
| `onChange={handler}` | `onChange={handler}` | function | - | Simplified handler |
| `disabled={true}` | `disabled={true}` | boolean | false | Same prop |
| `required={true}` | `required={true}` | boolean | false | Same prop |
| `multiple={true}` | `multiple={true}` | boolean | false | Same prop |
| Manual options | `options={[]}` | array | [] | Structured options |
| Manual label | `label="Label text"` | string | - | Built-in label |
| Manual placeholder | `placeholder="Select..."` | string | - | Built-in placeholder |
| - | `searchable={true}` | boolean | false | Search functionality |
| - | `clearable={true}` | boolean | false | Clear selection |
| - | `loading={true}` | boolean | false | Loading state |

**Migration Example:**
```jsx
// Before
<select 
  className="form-select"
  value={vatRate}
  onChange={(e) => setVatRate(e.target.value)}
>
  <option value="">Wybierz stawkę VAT</option>
  <option value="0">0%</option>
  <option value="5">5%</option>
  <option value="8">8%</option>
  <option value="23">23%</option>
</select>

// After
<Select
  label="Stawka VAT"
  value={vatRate}
  onChange={setVatRate}
  placeholder="Wybierz stawkę VAT"
  options={[
    { value: '0', label: '0%' },
    { value: '5', label: '5%' },
    { value: '8', label: '8%' },
    { value: '23', label: '23%' }
  ]}
/>
```

### Textarea Component

| Legacy Prop/Class | Design System Prop | Type | Default | Notes |
|------------------|-------------------|------|---------|-------|
| `className="form-control"` | Built-in | - | - | Base styling included |
| `rows={4}` | `rows={4}` | number | 3 | Same prop |
| `cols={50}` | Use CSS or `style` | - | - | Use design tokens |
| `placeholder="text"` | `placeholder="text"` | string | - | Same prop |
| `value={value}` | `value={value}` | string | - | Same prop |
| `onChange={handler}` | `onChange={handler}` | function | - | Simplified handler |
| `disabled={true}` | `disabled={true}` | boolean | false | Same prop |
| `required={true}` | `required={true}` | boolean | false | Same prop |
| `maxLength={500}` | `maxLength={500}` | number | - | Same prop |
| Manual label | `label="Label text"` | string | - | Built-in label |
| Manual character count | `showCharCount={true}` | boolean | false | Built-in character count |
| - | `autoResize={true}` | boolean | false | Auto-resize functionality |

## Form Components

### Form Component

| Legacy Prop/Class | Design System Prop | Type | Default | Notes |
|------------------|-------------------|------|---------|-------|
| `className="needs-validation"` | Built-in | - | - | Validation included |
| `onSubmit={handler}` | `onSubmit={handler}` | function | - | Same prop |
| `noValidate={true}` | `noValidate={true}` | boolean | false | Same prop |
| Manual validation | `validation="polish-business"` | string | - | Built-in validation schemas |
| - | `initialValues={}` | object | {} | Initial form values |
| - | `validationSchema={}` | object | - | Custom validation schema |
| - | `onValidationChange={}` | function | - | Validation state callback |

### FormField Component

| Legacy Prop/Class | Design System Prop | Type | Default | Notes |
|------------------|-------------------|------|---------|-------|
| `className="form-group"` | Built-in | - | - | Field wrapper included |
| Manual label | `label="Label text"` | string | - | Built-in label |
| Manual error display | `error="Error message"` | string | - | Built-in error handling |
| Manual help text | `helpText="Help text"` | string | - | Built-in help text |
| - | `required={true}` | boolean | false | Required indicator |
| - | `optional={true}` | boolean | false | Optional indicator |

## Layout Components

### Grid Component

| Legacy Bootstrap Class | Design System Prop | Type | Default | Notes |
|----------------------|-------------------|------|---------|-------|
| `className="container"` | Use `Container` component | - | - | Separate component |
| `className="container-fluid"` | `<Container fluid>` | boolean | false | Fluid container |
| `className="row"` | Built-in | - | - | Grid container |
| `className="col"` | `cols={1}` | number/array | 1 | Column count |
| `className="col-md-6"` | `cols={[1, 2]}` | array | [1] | Responsive columns |
| `className="col-lg-4"` | `cols={[1, 2, 3]}` | array | [1] | Responsive columns |
| `className="g-3"` | `gap="md"` | string | "none" | Gap tokens |
| `className="justify-content-center"` | `justify="center"` | string | "start" | Justify content |
| `className="align-items-center"` | `align="center"` | string | "stretch" | Align items |

**Migration Example:**
```jsx
// Before
<div className="container">
  <div className="row g-3">
    <div className="col-md-8">
      <main>Content</main>
    </div>
    <div className="col-md-4">
      <aside>Sidebar</aside>
    </div>
  </div>
</div>

// After
<Container>
  <Grid cols={[1, 2]} colSpan={[1, '2fr 1fr']} gap="md">
    <main>Content</main>
    <aside>Sidebar</aside>
  </Grid>
</Container>
```

### Card Component

| Legacy Bootstrap Class | Design System Prop | Type | Default | Notes |
|----------------------|-------------------|------|---------|-------|
| `className="card"` | Built-in | - | - | Base card styling |
| `className="card-header"` | `<Card.Header>` | component | - | Compound component |
| `className="card-body"` | `<Card.Body>` | component | - | Compound component |
| `className="card-footer"` | `<Card.Footer>` | component | - | Compound component |
| `className="card-title"` | `<Card.Title>` | component | - | Compound component |
| `className="card-text"` | Use `Text` component | - | - | Typography component |
| `className="border-primary"` | `variant="primary"` | string | "default" | Semantic variants |
| `className="shadow"` | `variant="elevated"` | string | "default" | Elevation variants |

## Polish Business Components

### CurrencyInput Component

| Legacy Implementation | Design System Prop | Type | Default | Notes |
|---------------------|-------------------|------|---------|-------|
| `type="number"` + manual formatting | Built-in | - | - | Automatic formatting |
| Manual currency symbol | `currency="PLN"` | string | "PLN" | Currency code |
| Manual decimal handling | `precision={2}` | number | 2 | Decimal places |
| Manual thousand separators | `thousandSeparator=" "` | string | " " | Polish formatting |
| Manual decimal separator | `decimalSeparator=","` | string | "," | Polish formatting |
| Manual validation | `validation="currency"` | string | - | Built-in validation |
| - | `min={0}` | number | - | Minimum value |
| - | `max={999999}` | number | - | Maximum value |
| - | `formatOnBlur={true}` | boolean | true | Format on blur |

### NIPValidator Component

| Legacy Implementation | Design System Prop | Type | Default | Notes |
|---------------------|-------------------|------|---------|-------|
| Manual NIP validation | Built-in | - | - | Automatic validation |
| Manual format checking | `format={true}` | boolean | true | Format validation |
| Manual checksum validation | `checksum={true}` | boolean | true | Checksum validation |
| Manual error messages | Built-in Polish messages | - | - | Localized messages |
| - | `showValidationIcon={true}` | boolean | false | Visual validation feedback |
| - | `validateOnBlur={true}` | boolean | true | Validation timing |
| - | `allowEmpty={false}` | boolean | false | Empty value handling |

### VATRateSelector Component

| Legacy Implementation | Design System Prop | Type | Default | Notes |
|---------------------|-------------------|------|---------|-------|
| Manual VAT options | Built-in Polish rates | - | - | Standard Polish VAT rates |
| Manual descriptions | `includeDescriptions={true}` | boolean | false | Rate descriptions |
| Manual calculations | `showCalculation={true}` | boolean | false | VAT calculation display |
| - | `includeZeroRate={true}` | boolean | true | Include 0% rate |
| - | `includeExempt={true}` | boolean | true | Include exempt option |
| - | `customRates={[]}` | array | [] | Additional custom rates |

### DatePicker Component

| Legacy Implementation | Design System Prop | Type | Default | Notes |
|---------------------|-------------------|------|---------|-------|
| `type="date"` | Built-in picker | - | - | Enhanced date picker |
| Manual format handling | `format="DD.MM.YYYY"` | string | "DD.MM.YYYY" | Polish date format |
| Manual locale | `locale="pl"` | string | "pl" | Polish locale |
| - | `businessDays={true}` | boolean | false | Business days only |
| - | `holidays="polish"` | string | - | Polish holidays |
| - | `minDate={new Date()}` | Date | - | Minimum selectable date |
| - | `maxDate={new Date()}` | Date | - | Maximum selectable date |
| - | `showWeekNumbers={true}` | boolean | false | Week numbers display |

## Event Handler Mappings

### Standard Event Handlers

| Legacy Handler | Design System Handler | Parameters | Notes |
|---------------|---------------------|------------|-------|
| `onChange={(e) => setValue(e.target.value)}` | `onChange={(value) => setValue(value)}` | `value` | Direct value |
| `onBlur={(e) => handleBlur(e.target.value)}` | `onBlur={(value) => handleBlur(value)}` | `value` | Direct value |
| `onFocus={(e) => handleFocus()}` | `onFocus={() => handleFocus()}` | none | Same |
| `onClick={(e) => handleClick()}` | `onClick={() => handleClick()}` | none | Same |
| `onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}` | `onSubmit={(data) => handleSubmit(data)}` | `data` | Form data object |

### Form Event Handlers

| Legacy Handler | Design System Handler | Parameters | Notes |
|---------------|---------------------|------------|-------|
| Manual form validation | `onValidationChange={(isValid, errors) => {}}` | `isValid, errors` | Validation state |
| Manual field validation | `onFieldValidation={(field, isValid, error) => {}}` | `field, isValid, error` | Field validation |
| Manual form reset | `onReset={() => resetForm()}` | none | Form reset |
| Manual form dirty state | `onDirtyChange={(isDirty) => {}}` | `isDirty` | Form dirty state |

### Polish Business Event Handlers

| Component | Handler | Parameters | Notes |
|-----------|---------|------------|-------|
| NIPValidator | `onValidation={(isValid, message) => {}}` | `isValid, message` | NIP validation result |
| CurrencyInput | `onFormatChange={(formatted, raw) => {}}` | `formatted, raw` | Format change |
| VATRateSelector | `onRateChange={(rate, description) => {}}` | `rate, description` | VAT rate selection |
| DatePicker | `onDateChange={(date, formatted) => {}}` | `date, formatted` | Date selection |

## CSS Class Mappings

### Bootstrap to Design System

| Bootstrap Class | Design System Equivalent | Notes |
|----------------|-------------------------|-------|
| `.text-primary` | `<Text color="primary">` | Use component prop |
| `.text-secondary` | `<Text color="secondary">` | Use component prop |
| `.text-success` | `<Text color="success">` | Use component prop |
| `.text-danger` | `<Text color="danger">` | Use component prop |
| `.text-warning` | `<Text color="warning">` | Use component prop |
| `.text-info` | `<Text color="info">` | Use component prop |
| `.text-muted` | `<Text color="muted">` | Use component prop |
| `.fw-bold` | `<Text weight="bold">` | Use component prop |
| `.fw-normal` | `<Text weight="normal">` | Use component prop |
| `.fs-1` to `.fs-6` | `<Text variant="heading-*">` | Use semantic variants |
| `.lead` | `<Text variant="lead">` | Use semantic variant |
| `.small` | `<Text variant="caption">` | Use semantic variant |

### Spacing Classes

| Bootstrap Class | Design System Equivalent | Notes |
|----------------|-------------------------|-------|
| `.m-0` to `.m-5` | `<Stack gap="none">` to `<Stack gap="xl">` | Use layout components |
| `.p-0` to `.p-5` | `<Box padding="none">` to `<Box padding="xl">` | Use layout components |
| `.mt-*`, `.mb-*`, etc. | Use layout component props | Directional spacing |
| `.g-*` (gap) | `<Grid gap="*">` or `<Stack gap="*">` | Use layout components |

### Display Classes

| Bootstrap Class | Design System Equivalent | Notes |
|----------------|-------------------------|-------|
| `.d-none` | `<Box display="none">` | Use layout component |
| `.d-block` | `<Box display="block">` | Use layout component |
| `.d-flex` | `<Stack>` or `<Grid>` | Use layout components |
| `.justify-content-*` | `<Stack justify="*">` | Use layout component props |
| `.align-items-*` | `<Stack align="*">` | Use layout component props |

### Responsive Classes

| Bootstrap Class | Design System Equivalent | Notes |
|----------------|-------------------------|-------|
| `.d-md-block` | `<Box display={["none", "block"]}>` | Responsive arrays |
| `.col-md-6` | `<Grid cols={[1, 2]}>` | Responsive grid |
| `.fs-md-4` | `<Text variant={["body", "heading-md"]}>` | Responsive typography |

## Migration Utilities

### Prop Mapping Helper

```jsx
// Utility function for prop mapping
const mapLegacyProps = (legacyProps) => {
  const mapping = {
    className: (value) => {
      if (value.includes('btn-primary')) return { variant: 'primary' };
      if (value.includes('btn-lg')) return { size: 'lg' };
      if (value.includes('form-control')) return {}; // Built-in styling
      return {};
    },
    onChange: (handler) => {
      // Convert event handler to value handler
      return (value) => handler({ target: { value } });
    }
  };

  return Object.entries(legacyProps).reduce((acc, [key, value]) => {
    if (mapping[key]) {
      return { ...acc, ...mapping[key](value) };
    }
    return { ...acc, [key]: value };
  }, {});
};
```

### Component Wrapper for Gradual Migration

```jsx
// Wrapper component for gradual migration
const LegacyButton = ({ className, children, ...props }) => {
  const dsProps = mapLegacyProps({ className, ...props });
  
  // Use design system component with mapped props
  return <Button {...dsProps}>{children}</Button>;
};
```

This prop mapping reference provides comprehensive guidance for migrating component props from legacy implementations to the design system while maintaining Polish business functionality.