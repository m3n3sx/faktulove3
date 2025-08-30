# Design System Contribution Guidelines

This document outlines the guidelines and standards for contributing to the FaktuLove Design System integration project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Standards](#development-standards)
4. [Component Development](#component-development)
5. [Testing Requirements](#testing-requirements)
6. [Documentation Standards](#documentation-standards)
7. [Polish Business Integration](#polish-business-integration)
8. [Quality Assurance](#quality-assurance)
9. [Review Process](#review-process)
10. [Release Process](#release-process)

## Code of Conduct

### Our Commitment

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, experience level, or identity.

### Expected Behavior

- **Be respectful**: Treat all community members with respect and kindness
- **Be collaborative**: Work together to improve the design system
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Help newcomers learn and grow
- **Be inclusive**: Welcome diverse perspectives and approaches

### Unacceptable Behavior

- Harassment, discrimination, or offensive language
- Personal attacks or trolling
- Publishing private information without consent
- Any behavior that would be inappropriate in a professional setting

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Read the [Developer Onboarding Guide](./developer-onboarding.md)
- Set up your development environment
- Familiarized yourself with the codebase
- Joined the team communication channels

### First Contributions

Good first contributions include:

1. **Documentation improvements**
2. **Bug fixes for existing components**
3. **Adding missing tests**
4. **Improving accessibility**
5. **Small feature enhancements**

### Finding Work

- Check the [GitHub Issues](https://github.com/faktulove/faktulove/issues) for open tasks
- Look for issues labeled `good first issue` or `help wanted`
- Join design system team meetings to discuss priorities
- Propose new features through RFC (Request for Comments) process

## Development Standards

### Code Quality Standards

#### TypeScript Requirements

All new code must be written in TypeScript with strict type checking:

```typescript
// ✅ Good: Proper typing
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

// ❌ Bad: Loose typing
interface ButtonProps {
  variant: string;
  size: string;
  disabled: boolean;
  loading: boolean;
  children: any;
  onClick: Function;
}
```

#### React Component Standards

```typescript
// ✅ Good: Functional component with proper props
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  children,
  onClick,
  ...rest
}) => {
  const handleClick = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
    if (!disabled && !loading && onClick) {
      onClick(event);
    }
  }, [disabled, loading, onClick]);

  return (
    <button
      className={cn(
        'ds-button',
        `ds-button--${variant}`,
        `ds-button--${size}`,
        {
          'ds-button--disabled': disabled,
          'ds-button--loading': loading
        }
      )}
      disabled={disabled || loading}
      onClick={handleClick}
      {...rest}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
};

// ❌ Bad: Class component, poor prop handling
class Button extends React.Component {
  render() {
    return <button onClick={this.props.onClick}>{this.props.children}</button>;
  }
}
```

#### CSS Standards

Use CSS custom properties and follow BEM naming:

```css
/* ✅ Good: Design tokens and BEM */
.ds-button {
  background-color: var(--ds-color-primary-500);
  color: var(--ds-color-primary-contrast);
  padding: var(--ds-space-2) var(--ds-space-4);
  border-radius: var(--ds-border-radius-md);
  font-size: var(--ds-font-size-base);
  font-weight: var(--ds-font-weight-medium);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--ds-transition-fast) ease;
}

.ds-button--secondary {
  background-color: var(--ds-color-secondary-500);
  color: var(--ds-color-secondary-contrast);
}

.ds-button--disabled {
  opacity: var(--ds-opacity-disabled);
  cursor: not-allowed;
}

/* ❌ Bad: Hard-coded values, poor naming */
.button {
  background: #007bff;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
}
```

### Performance Standards

#### Bundle Size Requirements

- Individual components must not exceed 50KB gzipped
- Total design system bundle must not exceed 500KB gzipped
- Use tree shaking to minimize unused code
- Implement lazy loading for large components

#### Runtime Performance

- Components must render in under 16ms (60fps)
- Use React.memo for expensive components
- Implement proper dependency arrays in hooks
- Avoid unnecessary re-renders

```typescript
// ✅ Good: Optimized component
const ExpensiveList = React.memo<ExpensiveListProps>(({ items, onItemClick }) => {
  const memoizedItems = useMemo(() => 
    items.map(item => processItem(item)), 
    [items]
  );

  const handleItemClick = useCallback((id: string) => {
    onItemClick(id);
  }, [onItemClick]);

  return (
    <ul>
      {memoizedItems.map(item => (
        <ListItem 
          key={item.id} 
          item={item} 
          onClick={handleItemClick} 
        />
      ))}
    </ul>
  );
}, (prevProps, nextProps) => {
  return (
    prevProps.items.length === nextProps.items.length &&
    prevProps.items.every((item, index) => item.id === nextProps.items[index].id)
  );
});
```

## Component Development

### Component Architecture

#### File Structure

Each component must follow this structure:

```
ComponentName/
├── index.ts                 # Public exports
├── ComponentName.tsx        # Main component
├── ComponentName.stories.tsx # Storybook stories
├── ComponentName.test.tsx   # Unit tests
├── ComponentName.css        # Component styles
├── types.ts                 # Type definitions
└── utils.ts                 # Component utilities
```

#### Component Template

```typescript
// ComponentName.tsx
import React from 'react';
import { cn } from '../../utils/classNames';
import { ComponentNameProps } from './types';
import './ComponentName.css';

export const ComponentName: React.FC<ComponentNameProps> = ({
  variant = 'default',
  size = 'md',
  className,
  children,
  ...rest
}) => {
  return (
    <div
      className={cn(
        'ds-component-name',
        `ds-component-name--${variant}`,
        `ds-component-name--${size}`,
        className
      )}
      {...rest}
    >
      {children}
    </div>
  );
};

ComponentName.displayName = 'ComponentName';
```

#### Storybook Stories Template

```typescript
// ComponentName.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { ComponentName } from './ComponentName';

const meta: Meta<typeof ComponentName> = {
  title: 'Design System/Components/ComponentName',
  component: ComponentName,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A brief description of what this component does.'
      }
    }
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'primary', 'secondary']
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg']
    }
  }
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Default component'
  }
};

export const Variants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem' }}>
      <ComponentName variant="default">Default</ComponentName>
      <ComponentName variant="primary">Primary</ComponentName>
      <ComponentName variant="secondary">Secondary</ComponentName>
    </div>
  )
};

export const Sizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
      <ComponentName size="sm">Small</ComponentName>
      <ComponentName size="md">Medium</ComponentName>
      <ComponentName size="lg">Large</ComponentName>
    </div>
  )
};
```

### Accessibility Requirements

All components must meet WCAG 2.1 AA standards:

#### Keyboard Navigation

```typescript
const InteractiveComponent: React.FC<Props> = ({ onActivate }) => {
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onActivate();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onClick={onActivate}
      aria-label="Activate feature"
    >
      Interactive content
    </div>
  );
};
```

#### ARIA Labels and Descriptions

```typescript
const FormField: React.FC<FormFieldProps> = ({ 
  label, 
  error, 
  helpText, 
  children 
}) => {
  const fieldId = useId();
  const errorId = `${fieldId}-error`;
  const helpId = `${fieldId}-help`;

  return (
    <div className="ds-form-field">
      <label htmlFor={fieldId} className="ds-form-field__label">
        {label}
      </label>
      
      {React.cloneElement(children, {
        id: fieldId,
        'aria-describedby': cn(
          error && errorId,
          helpText && helpId
        ),
        'aria-invalid': !!error
      })}
      
      {helpText && (
        <div id={helpId} className="ds-form-field__help">
          {helpText}
        </div>
      )}
      
      {error && (
        <div id={errorId} className="ds-form-field__error" role="alert">
          {error}
        </div>
      )}
    </div>
  );
};
```

#### Focus Management

```typescript
const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      ref={modalRef}
      className="ds-modal"
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
      onKeyDown={handleKeyDown}
    >
      {children}
    </div>
  );
};
```

## Testing Requirements

### Test Coverage Standards

- **Unit Tests**: Minimum 90% code coverage
- **Integration Tests**: All component interactions
- **Accessibility Tests**: All components must pass axe-core
- **Visual Regression Tests**: All visual states documented

### Unit Testing Template

```typescript
// ComponentName.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ComponentName } from './ComponentName';

expect.extend(toHaveNoViolations);

describe('ComponentName', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {
      render(<ComponentName>Test content</ComponentName>);
      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('applies correct CSS classes', () => {
      render(<ComponentName variant="primary" size="lg">Test</ComponentName>);
      const element = screen.getByText('Test');
      expect(element).toHaveClass('ds-component-name');
      expect(element).toHaveClass('ds-component-name--primary');
      expect(element).toHaveClass('ds-component-name--lg');
    });
  });

  describe('Interactions', () => {
    it('handles click events', async () => {
      const user = userEvent.setup();
      const handleClick = jest.fn();
      
      render(<ComponentName onClick={handleClick}>Clickable</ComponentName>);
      
      await user.click(screen.getByText('Clickable'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('handles keyboard navigation', async () => {
      const user = userEvent.setup();
      const handleActivate = jest.fn();
      
      render(<ComponentName onActivate={handleActivate}>Interactive</ComponentName>);
      
      const element = screen.getByText('Interactive');
      element.focus();
      await user.keyboard('{Enter}');
      expect(handleActivate).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<ComponentName>Accessible content</ComponentName>);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('supports screen readers', () => {
      render(<ComponentName aria-label="Screen reader label">Content</ComponentName>);
      expect(screen.getByLabelText('Screen reader label')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty content gracefully', () => {
      render(<ComponentName />);
      expect(screen.getByRole('generic')).toBeInTheDocument();
    });

    it('handles long content', () => {
      const longContent = 'A'.repeat(1000);
      render(<ComponentName>{longContent}</ComponentName>);
      expect(screen.getByText(longContent)).toBeInTheDocument();
    });
  });
});
```

### Visual Regression Testing

```typescript
// ComponentName.visual.test.ts
import { test, expect } from '@playwright/test';

test.describe('ComponentName Visual Tests', () => {
  test('default appearance', async ({ page }) => {
    await page.goto('/storybook/?path=/story/componentname--default');
    await expect(page.locator('[data-testid="component-name"]')).toHaveScreenshot();
  });

  test('all variants', async ({ page }) => {
    await page.goto('/storybook/?path=/story/componentname--variants');
    await expect(page.locator('[data-testid="variants-container"]')).toHaveScreenshot();
  });

  test('responsive behavior', async ({ page }) => {
    await page.goto('/storybook/?path=/story/componentname--responsive');
    
    // Test mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('[data-testid="component-name"]')).toHaveScreenshot('mobile.png');
    
    // Test tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('[data-testid="component-name"]')).toHaveScreenshot('tablet.png');
    
    // Test desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('[data-testid="component-name"]')).toHaveScreenshot('desktop.png');
  });
});
```

## Documentation Standards

### Component Documentation

Each component must include:

1. **README.md** with usage examples
2. **Storybook stories** with all variants
3. **API documentation** with prop descriptions
4. **Accessibility notes**
5. **Polish business considerations** (if applicable)

### README Template

```markdown
# ComponentName

Brief description of what the component does and when to use it.

## Usage

```tsx
import { ComponentName } from '@design-system/components';

function MyComponent() {
  return (
    <ComponentName variant="primary" size="lg">
      Content here
    </ComponentName>
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | 'default' \| 'primary' \| 'secondary' | 'default' | Visual variant of the component |
| size | 'sm' \| 'md' \| 'lg' | 'md' | Size of the component |
| disabled | boolean | false | Whether the component is disabled |
| children | ReactNode | - | Content to display |

## Variants

### Default
Standard appearance for general use.

### Primary
Emphasized appearance for primary actions.

### Secondary
Subdued appearance for secondary actions.

## Accessibility

- Supports keyboard navigation with Tab, Enter, and Space keys
- Includes proper ARIA labels and descriptions
- Compatible with screen readers
- Meets WCAG 2.1 AA standards

## Polish Business Considerations

- Supports Polish text and special characters
- Follows Polish UI conventions
- Compatible with Polish business workflows

## Examples

### Basic Usage
```tsx
<ComponentName>Basic content</ComponentName>
```

### With Props
```tsx
<ComponentName variant="primary" size="lg" disabled>
  Disabled primary component
</ComponentName>
```

### Polish Business Example
```tsx
<ComponentName>
  Faktura nr FV/2024/01/001
</ComponentName>
```
```

## Polish Business Integration

### Validation Requirements

All Polish business components must implement proper validation:

```typescript
// NIP Validation Example
export const validateNIP = (nip: string): ValidationResult => {
  const cleanNIP = nip.replace(/[\s-]/g, '');
  
  // Format validation
  if (!/^\d{10}$/.test(cleanNIP)) {
    return {
      isValid: false,
      message: 'NIP musi składać się z 10 cyfr'
    };
  }
  
  // Checksum validation
  const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
  const digits = cleanNIP.split('').map(Number);
  const sum = digits.slice(0, 9).reduce((acc, digit, index) => 
    acc + (digit * weights[index]), 0
  );
  
  const checksum = sum % 11;
  const expectedChecksum = checksum === 10 ? 0 : checksum;
  
  if (digits[9] !== expectedChecksum) {
    return {
      isValid: false,
      message: 'Nieprawidłowa suma kontrolna NIP'
    };
  }
  
  return {
    isValid: true,
    message: ''
  };
};
```

### Localization Standards

```typescript
// Polish date formatting
export const formatPolishDate = (date: Date): string => {
  return new Intl.DateTimeFormat('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(date);
};

// Polish currency formatting
export const formatPolishCurrency = (amount: number): string => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

// Polish number formatting
export const formatPolishNumber = (number: number): string => {
  return new Intl.NumberFormat('pl-PL').format(number);
};
```

### Compliance Requirements

Components must support Polish business regulations:

```typescript
// VAT rate validation
export const POLISH_VAT_RATES = [0, 5, 8, 23] as const;

export const validateVATRate = (rate: number): boolean => {
  return POLISH_VAT_RATES.includes(rate as any);
};

// Invoice number validation
export const validatePolishInvoiceNumber = (number: string): ValidationResult => {
  // Common Polish invoice number patterns
  const patterns = [
    /^FV\/\d{4}\/\d{2}\/\d+$/, // FV/YYYY/MM/###
    /^\d+\/\d{4}$/,            // ###/YYYY
    /^FV-\d+\/\d{4}$/          // FV-###/YYYY
  ];
  
  const isValid = patterns.some(pattern => pattern.test(number));
  
  return {
    isValid,
    message: isValid ? '' : 'Nieprawidłowy format numeru faktury'
  };
};
```

## Quality Assurance

### Pre-commit Checks

All commits must pass:

1. **ESLint**: No linting errors
2. **TypeScript**: No type errors
3. **Prettier**: Code is properly formatted
4. **Tests**: All tests pass
5. **Build**: Project builds successfully

### Continuous Integration

Our CI pipeline runs:

1. **Unit Tests**: Jest with React Testing Library
2. **Integration Tests**: Playwright E2E tests
3. **Visual Regression**: Chromatic visual testing
4. **Accessibility Tests**: axe-core automated testing
5. **Performance Tests**: Bundle size and runtime performance
6. **Security Scans**: Dependency vulnerability checks

### Quality Gates

Before merging, ensure:

- [ ] All tests pass (unit, integration, visual, accessibility)
- [ ] Code coverage is above 90%
- [ ] No accessibility violations
- [ ] Bundle size impact is acceptable
- [ ] Performance benchmarks are met
- [ ] Documentation is complete
- [ ] Polish business requirements are satisfied

## Review Process

### Code Review Checklist

#### Functionality
- [ ] Component works as expected
- [ ] All props are properly handled
- [ ] Edge cases are covered
- [ ] Error handling is implemented

#### Code Quality
- [ ] TypeScript types are accurate
- [ ] Code follows established patterns
- [ ] Performance is optimized
- [ ] No code smells or anti-patterns

#### Design System Compliance
- [ ] Uses design tokens consistently
- [ ] Follows naming conventions
- [ ] Implements theming support
- [ ] Matches design specifications

#### Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] ARIA labels are correct
- [ ] Focus management is proper

#### Polish Business
- [ ] Validation logic is correct
- [ ] Localization is implemented
- [ ] Compliance requirements are met
- [ ] Business rules are followed

#### Testing
- [ ] Unit tests are comprehensive
- [ ] Integration tests cover workflows
- [ ] Visual tests document all states
- [ ] Accessibility tests pass

#### Documentation
- [ ] README is complete
- [ ] Storybook stories are comprehensive
- [ ] API documentation is accurate
- [ ] Examples are helpful

### Review Timeline

- **Initial Review**: Within 24 hours
- **Follow-up Reviews**: Within 12 hours
- **Final Approval**: Within 48 hours of submission

### Reviewer Responsibilities

Reviewers should:

1. **Test the changes** locally
2. **Verify functionality** matches requirements
3. **Check code quality** and patterns
4. **Validate accessibility** compliance
5. **Ensure documentation** is complete
6. **Provide constructive feedback**

## Release Process

### Versioning Strategy

We follow Semantic Versioning (SemVer):

- **Major (X.0.0)**: Breaking changes
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, backward compatible

### Release Types

#### Patch Release (Weekly)
- Bug fixes
- Performance improvements
- Documentation updates
- Minor accessibility improvements

#### Minor Release (Monthly)
- New components
- New features
- Non-breaking API changes
- Major documentation additions

#### Major Release (Quarterly)
- Breaking changes
- Architecture updates
- Major API changes
- Design system overhauls

### Release Checklist

- [ ] All tests pass in CI
- [ ] Visual regression tests approved
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Migration guide created (for breaking changes)
- [ ] Stakeholders notified
- [ ] Release notes prepared

### Post-Release

After each release:

1. **Monitor** for issues and bug reports
2. **Gather feedback** from users
3. **Plan improvements** for next release
4. **Update roadmap** based on learnings

---

Thank you for contributing to the FaktuLove Design System! Your contributions help create better experiences for Polish businesses using our platform.