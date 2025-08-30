# Migration Guide

This guide helps you migrate from existing components to the FaktuLove Design System. Whether you're coming from custom components, Bootstrap, or another design system, this guide provides step-by-step instructions.

## 🎯 Migration Overview

### Benefits of Migration
- **Consistency**: Unified visual language across the application
- **Accessibility**: WCAG 2.1 Level AA compliance out of the box
- **Polish Business Support**: Components tailored for Polish business needs
- **Type Safety**: Full TypeScript support with comprehensive types
- **Performance**: Optimized components with minimal bundle impact
- **Maintenance**: Centralized component library reduces maintenance overhead

### Migration Strategy
1. **Gradual Migration**: Migrate components incrementally
2. **Compatibility Layer**: Use compatibility components during transition
3. **Testing**: Comprehensive testing at each migration step
4. **Documentation**: Update documentation as you migrate

## 🔄 From Custom Components

### Button Migration

#### Before (Custom Button)
```tsx
// Old custom button
interface CustomButtonProps {
  type?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

function CustomButton({ type = 'primary', size = 'medium', ...props }: CustomButtonProps) {
  const className = `btn btn-${type} btn-${size}`;
  return <button className={className} {...props} />;
}
```

#### After (Design System Button)
```tsx
// New design system button
import { Button } from '@faktulove/design-system';

// Direct replacement
<Button 
  variant="primary"  // type -> variant
  size="md"          // medium -> md
  disabled={disabled}
  onClick={onClick}
>
  {children}
</Button>
```

#### Migration Steps
1. **Replace imports**: Change custom button import to design system
2. **Update props**: Map old prop names to new ones
3. **Update styles**: Remove custom CSS classes
4. **Test accessibility**: Verify ARIA attributes are working

```tsx
// Migration helper function
function migrateButtonProps(oldProps: CustomButtonProps): ButtonProps {
  const { type, size, ...rest } = oldProps;
  
  return {
    ...rest,
    variant: type === 'primary' ? 'primary' : 'secondary',
    size: size === 'small' ? 'sm' : size === 'large' ? 'lg' : 'md',
  };
}
```

### Input Migration

#### Before (Custom Input)
```tsx
// Old custom input
interface CustomInputProps {
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  label?: string;
}

function CustomInput({ label, error, ...props }: CustomInputProps) {
  return (
    <div className="input-group">
      {label && <label>{label}</label>}
      <input className={`input ${error ? 'error' : ''}`} {...props} />
      {error && <span className="error-message">{error}</span>}
    </div>
  );
}
```

#### After (Design System Input)
```tsx
// New design system input
import { Input } from '@faktulove/design-system';

<Input
  type={type}
  placeholder={placeholder}
  value={value}
  onChange={(e) => onChange(e.target.value)} // Note: different signature
  error={error}
  aria-label={label} // Better accessibility
/>
```

#### Migration Steps
1. **Update onChange signature**: Design system uses value, not event
2. **Replace label with aria-label**: Better accessibility approach
3. **Remove wrapper divs**: Design system handles layout internally
4. **Update error handling**: Error prop now handles display automatically

### Form Migration

#### Before (Custom Form)
```tsx
// Old custom form
function CustomForm({ onSubmit, children }) {
  return (
    <form onSubmit={onSubmit} className="custom-form">
      <div className="form-fields">
        {children}
      </div>
      <div className="form-actions">
        <button type="submit">Submit</button>
      </div>
    </form>
  );
}
```

#### After (Design System Form)
```tsx
// New design system form
import { Form, Button } from '@faktulove/design-system';

<Form onSubmit={onSubmit}>
  {children}
  <Form.Actions>
    <Button type="submit" variant="primary">
      Submit
    </Button>
  </Form.Actions>
</Form>
```

## 🅱️ From Bootstrap

### Bootstrap to Design System Mapping

#### Button Classes
```tsx
// Bootstrap classes -> Design System props
const bootstrapMapping = {
  'btn-primary': { variant: 'primary' },
  'btn-secondary': { variant: 'secondary' },
  'btn-outline-primary': { variant: 'ghost' },
  'btn-danger': { variant: 'danger' },
  'btn-sm': { size: 'sm' },
  'btn-lg': { size: 'lg' },
  'disabled': { disabled: true },
};
```

#### Before (Bootstrap)
```tsx
// Bootstrap button
<button className="btn btn-primary btn-lg" disabled>
  Primary Button
</button>
```

#### After (Design System)
```tsx
// Design system button
<Button variant="primary" size="lg" disabled>
  Primary Button
</Button>
```

### Grid System Migration

#### Before (Bootstrap Grid)
```tsx
// Bootstrap grid
<div className="container">
  <div className="row">
    <div className="col-md-6">Column 1</div>
    <div className="col-md-6">Column 2</div>
  </div>
</div>
```

#### After (Design System Grid)
```tsx
// Design system grid
import { Container, Grid } from '@faktulove/design-system';

<Container>
  <Grid cols={{ base: 1, md: 2 }} gap={4}>
    <div>Column 1</div>
    <div>Column 2</div>
  </Grid>
</Container>
```

### Form Controls Migration

#### Before (Bootstrap Forms)
```tsx
// Bootstrap form
<div className="mb-3">
  <label htmlFor="email" className="form-label">Email</label>
  <input 
    type="email" 
    className="form-control" 
    id="email"
    placeholder="Enter email"
  />
  <div className="invalid-feedback">
    Please provide a valid email.
  </div>
</div>
```

#### After (Design System)
```tsx
// Design system form
<Input
  type="email"
  placeholder="Enter email"
  error="Please provide a valid email"
  aria-label="Email address"
/>
```

## 🎨 From Material-UI

### Component Mapping

#### Button Migration
```tsx
// Material-UI
import { Button } from '@mui/material';

<Button variant="contained" color="primary" size="large">
  Click me
</Button>

// Design System
import { Button } from '@faktulove/design-system';

<Button variant="primary" size="lg">
  Click me
</Button>
```

#### TextField Migration
```tsx
// Material-UI
import { TextField } from '@mui/material';

<TextField
  label="Name"
  variant="outlined"
  error={!!error}
  helperText={error}
  fullWidth
/>

// Design System
import { Input } from '@faktulove/design-system';

<Input
  aria-label="Name"
  error={error}
  className="w-full"
/>
```

## 🔧 Compatibility Layer

Create a compatibility layer to ease migration:

### Button Compatibility
```tsx
// compatibility/Button.tsx
import { Button as DSButton, ButtonProps as DSButtonProps } from '@faktulove/design-system';

interface LegacyButtonProps {
  type?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export function Button(props: LegacyButtonProps) {
  const { type, size, ...rest } = props;
  
  const dsProps: DSButtonProps = {
    ...rest,
    variant: type === 'primary' ? 'primary' : 'secondary',
    size: size === 'small' ? 'sm' : size === 'large' ? 'lg' : 'md',
  };
  
  return <DSButton {...dsProps} />;
}
```

### Input Compatibility
```tsx
// compatibility/Input.tsx
import { Input as DSInput, InputProps as DSInputProps } from '@faktulove/design-system';

interface LegacyInputProps {
  label?: string;
  error?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  [key: string]: any;
}

export function Input(props: LegacyInputProps) {
  const { label, onChange, ...rest } = props;
  
  const dsProps: DSInputProps = {
    ...rest,
    'aria-label': label,
    onChange: onChange ? (value: string) => {
      onChange({ target: { value } } as React.ChangeEvent<HTMLInputElement>);
    } : undefined,
  };
  
  return <DSInput {...dsProps} />;
}
```

## 🇵🇱 Polish Business Components Migration

### Currency Input Migration

#### Before (Custom Currency)
```tsx
// Old currency input
function CurrencyInput({ value, onChange }) {
  const formatCurrency = (val) => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN'
    }).format(val);
  };

  return (
    <input
      type="text"
      value={formatCurrency(value)}
      onChange={(e) => onChange(parseFloat(e.target.value))}
    />
  );
}
```

#### After (Design System)
```tsx
// New design system currency input
import { CurrencyInput } from '@faktulove/design-system';

<CurrencyInput
  currency="PLN"
  value={value}
  onChange={onChange}
  aria-label="Kwota"
/>
```

### NIP Validation Migration

#### Before (Custom NIP)
```tsx
// Old NIP validator
function NIPInput({ value, onChange, onValidate }) {
  const validateNIP = (nip) => {
    // Custom validation logic
    return nip.length === 10 && /^\d+$/.test(nip);
  };

  return (
    <input
      type="text"
      value={value}
      onChange={(e) => {
        const newValue = e.target.value;
        onChange(newValue);
        onValidate(validateNIP(newValue));
      }}
      placeholder="1234567890"
    />
  );
}
```

#### After (Design System)
```tsx
// New design system NIP validator
import { NIPValidator } from '@faktulove/design-system';

<NIPValidator
  value={value}
  onChange={onChange}
  onValidationChange={onValidate}
  aria-label="Numer NIP"
/>
```

## 🧪 Testing Migration

### Update Test Files

#### Before (Custom Component Tests)
```tsx
// Old test
test('button renders correctly', () => {
  render(<CustomButton type="primary">Click me</CustomButton>);
  expect(screen.getByRole('button')).toHaveClass('btn-primary');
});
```

#### After (Design System Tests)
```tsx
// New test with accessibility
import { renderWithA11y, testPolishA11y } from '@faktulove/design-system/testing';

test('button renders correctly and is accessible', async () => {
  const { container } = renderWithA11y(
    <Button variant="primary">Click me</Button>
  );
  
  expect(screen.getByRole('button')).toBeInTheDocument();
  await testPolishA11y(container);
});
```

### Test Utilities Migration
```tsx
// Old test utilities
const renderWithTheme = (component) => {
  return render(
    <ThemeProvider theme={customTheme}>
      {component}
    </ThemeProvider>
  );
};

// New test utilities (built-in)
import { renderWithA11y } from '@faktulove/design-system/testing';

// Automatically includes theme and accessibility testing
const { container } = renderWithA11y(<Component />);
```

## 📋 Migration Checklist

### Pre-Migration
- [ ] Audit existing components and their usage
- [ ] Identify components that need custom migration logic
- [ ] Plan migration order (start with leaf components)
- [ ] Set up design system in development environment
- [ ] Create compatibility layer for complex migrations

### During Migration
- [ ] Migrate one component type at a time
- [ ] Update imports and prop names
- [ ] Remove custom CSS classes
- [ ] Add proper ARIA labels and accessibility attributes
- [ ] Update tests to use design system testing utilities
- [ ] Verify visual consistency
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility

### Post-Migration
- [ ] Remove old component files
- [ ] Clean up unused CSS
- [ ] Update documentation
- [ ] Remove compatibility layer (when no longer needed)
- [ ] Performance audit
- [ ] Accessibility audit
- [ ] User acceptance testing

## 🔍 Common Migration Issues

### Styling Issues
```tsx
// Problem: Custom styles not applying
<Button className="my-custom-button">Click me</Button>

// Solution: Use CSS custom properties
<Button 
  className="my-custom-button"
  style={{ '--ds-button-bg': '#custom-color' }}
>
  Click me
</Button>
```

### Event Handler Changes
```tsx
// Problem: Different event signatures
// Old: onChange(event)
// New: onChange(value)

// Solution: Adapter function
const handleChange = (value) => {
  // Convert to old format if needed
  const syntheticEvent = { target: { value } };
  oldOnChange(syntheticEvent);
};
```

### Missing Features
```tsx
// Problem: Old component had features not in design system
// Solution: Extend design system component

import { Button as DSButton } from '@faktulove/design-system';

function ExtendedButton({ tooltip, ...props }) {
  return (
    <div title={tooltip}>
      <DSButton {...props} />
    </div>
  );
}
```

## 🚀 Migration Tools

### Automated Migration Script
```bash
#!/bin/bash
# migrate-components.sh

# Replace imports
find src -name "*.tsx" -exec sed -i 's/from "\.\.\/components\/Button"/from "@faktulove\/design-system"/g' {} \;

# Replace prop names
find src -name "*.tsx" -exec sed -i 's/type="/variant="/g' {} \;

echo "Migration complete! Please review changes and test thoroughly."
```

### Codemod Example
```tsx
// codemod/button-migration.js
const j = require('jscodeshift');

module.exports = function transformer(fileInfo, api) {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);

  // Replace Button imports
  root
    .find(j.ImportDeclaration, {
      source: { value: '../components/Button' }
    })
    .replaceWith(
      j.importDeclaration(
        [j.importSpecifier(j.identifier('Button'))],
        j.literal('@faktulove/design-system')
      )
    );

  // Replace type prop with variant
  root
    .find(j.JSXAttribute, { name: { name: 'type' } })
    .forEach(path => {
      path.node.name.name = 'variant';
    });

  return root.toSource();
};
```

## 📚 Resources

### Migration Tools
- [jscodeshift](https://github.com/facebook/jscodeshift) - JavaScript codemod toolkit
- [ast-grep](https://ast-grep.github.io/) - Code structural search and replace
- [Storybook Migration Guide](https://storybook.js.org/docs/react/migration-guide)

### Testing Resources
- [Testing Library Migration](https://testing-library.com/docs/react-testing-library/migrate-from-enzyme)
- [Jest Migration Guide](https://jestjs.io/docs/migration-guide)
- [Accessibility Testing](https://web.dev/accessibility-testing/)

### Design System Resources
- [Design System Migration Best Practices](https://designsystem.digital.gov/design-tokens/how-to-use-design-tokens/)
- [Component API Design](https://component.gallery/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Take your time with migration - it's better to migrate thoroughly than quickly!** 🚀