# Contributing to FaktuLove Design System

Thank you for your interest in contributing to the FaktuLove Design System! This guide will help you get started with contributing code, documentation, and improvements.

## 🎯 How to Contribute

### Types of Contributions
- **Bug Reports**: Report issues with existing components
- **Feature Requests**: Suggest new components or improvements
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve guides, examples, and API documentation
- **Testing**: Add or improve test coverage
- **Accessibility**: Enhance accessibility features
- **Polish Localization**: Improve Polish language support

## 🚀 Getting Started

### Prerequisites
- Node.js 16 or higher
- npm or yarn
- Git
- Basic knowledge of React and TypeScript
- Understanding of accessibility principles

### Development Setup
```bash
# Clone the repository
git clone https://github.com/faktulove/design-system.git
cd design-system

# Install dependencies
npm install

# Start Storybook for development
npm run storybook

# Run tests
npm run test

# Run design system test suite
npm run test:design-system
```

### Project Structure
```
frontend/src/design-system/
├── components/           # Component implementations
│   ├── primitives/      # Basic components (Button, Input)
│   ├── patterns/        # Composite components (Card, Form)
│   ├── layouts/         # Layout components (Grid, Container)
│   └── business/        # Polish business components
├── tokens/              # Design tokens (colors, typography)
├── utils/               # Utility functions and helpers
├── styles/              # CSS and styling
├── docs/                # Documentation
└── __tests__/           # Test files
```

## 🧩 Adding New Components

### Component Development Process
1. **Research**: Understand the use case and requirements
2. **Design**: Create component API and design specifications
3. **Implementation**: Build the component with TypeScript
4. **Testing**: Add comprehensive tests
5. **Documentation**: Create Storybook stories and documentation
6. **Review**: Submit pull request for review

### Component Template
```tsx
// components/primitives/NewComponent/NewComponent.tsx
import React from 'react';
import { cn } from '../../utils/cn';

export interface NewComponentProps {
  /**
   * The variant of the component
   */
  variant?: 'primary' | 'secondary';
  
  /**
   * The size of the component
   */
  size?: 'sm' | 'md' | 'lg';
  
  /**
   * Whether the component is disabled
   */
  disabled?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
  
  /**
   * Child elements
   */
  children?: React.ReactNode;
  
  /**
   * Accessible label for screen readers
   */
  'aria-label': string;
}

export const NewComponent = React.forwardRef<
  HTMLDivElement,
  NewComponentProps
>(({ 
  variant = 'primary',
  size = 'md',
  disabled = false,
  className,
  children,
  'aria-label': ariaLabel,
  ...props 
}, ref) => {
  const baseClasses = 'ds-new-component';
  const variantClasses = {
    primary: 'ds-new-component--primary',
    secondary: 'ds-new-component--secondary',
  };
  const sizeClasses = {
    sm: 'ds-new-component--sm',
    md: 'ds-new-component--md',
    lg: 'ds-new-component--lg',
  };

  return (
    <div
      ref={ref}
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        disabled && 'ds-new-component--disabled',
        className
      )}
      aria-label={ariaLabel}
      aria-disabled={disabled}
      {...props}
    >
      {children}
    </div>
  );
});

NewComponent.displayName = 'NewComponent';
```

### Component Tests
```tsx
// components/primitives/NewComponent/__tests__/NewComponent.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import { NewComponent } from '../NewComponent';
import { runA11yTestSuite } from '../../../utils/testUtils';

describe('NewComponent', () => {
  it('renders correctly', () => {
    render(
      <NewComponent aria-label="Test component">
        Test content
      </NewComponent>
    );
    
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('applies variant classes correctly', () => {
    render(
      <NewComponent variant="secondary" aria-label="Test component">
        Test
      </NewComponent>
    );
    
    const component = screen.getByLabelText('Test component');
    expect(component).toHaveClass('ds-new-component--secondary');
  });

  it('meets accessibility standards', async () => {
    const { container } = render(
      <NewComponent aria-label="Accessible component">
        Content
      </NewComponent>
    );
    
    await runA11yTestSuite(container, {
      testKeyboard: true,
      testScreenReader: true,
      testFocus: true,
    });
  });

  it('handles disabled state correctly', () => {
    render(
      <NewComponent disabled aria-label="Disabled component">
        Disabled
      </NewComponent>
    );
    
    const component = screen.getByLabelText('Disabled component');
    expect(component).toHaveAttribute('aria-disabled', 'true');
    expect(component).toHaveClass('ds-new-component--disabled');
  });
});
```

### Storybook Stories
```tsx
// components/primitives/NewComponent/NewComponent.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { NewComponent } from './NewComponent';

const meta: Meta<typeof NewComponent> = {
  title: 'Primitives/NewComponent',
  component: NewComponent,
  parameters: {
    docs: {
      description: {
        component: 'A new component for the design system.',
      },
    },
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary'],
      description: 'The visual variant of the component',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'The size of the component',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the component is disabled',
    },
  },
};

export default meta;
type Story = StoryObj<typeof NewComponent>;

export const Default: Story = {
  args: {
    'aria-label': 'Default new component',
    children: 'Default Component',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    'aria-label': 'Secondary new component',
    children: 'Secondary Component',
  },
};

export const Sizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
      <NewComponent size="sm" aria-label="Small component">
        Small
      </NewComponent>
      <NewComponent size="md" aria-label="Medium component">
        Medium
      </NewComponent>
      <NewComponent size="lg" aria-label="Large component">
        Large
      </NewComponent>
    </div>
  ),
};

export const Disabled: Story = {
  args: {
    disabled: true,
    'aria-label': 'Disabled new component',
    children: 'Disabled Component',
  },
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(2, 1fr)' }}>
      <NewComponent variant="primary" aria-label="Primary component">
        Primary
      </NewComponent>
      <NewComponent variant="secondary" aria-label="Secondary component">
        Secondary
      </NewComponent>
      <NewComponent variant="primary" disabled aria-label="Primary disabled">
        Primary Disabled
      </NewComponent>
      <NewComponent variant="secondary" disabled aria-label="Secondary disabled">
        Secondary Disabled
      </NewComponent>
    </div>
  ),
};
```

## 🎨 Design Tokens

### Adding New Tokens
```tsx
// tokens/newTokens.ts
export const newTokens = {
  // Use consistent naming convention
  newToken: {
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
} as const;

export type NewTokens = typeof newTokens;
```

### Token Guidelines
- Use consistent naming conventions
- Follow the 8px grid system for spacing
- Ensure color tokens meet accessibility contrast requirements
- Document the purpose and usage of each token
- Use semantic names rather than descriptive names

## ♿ Accessibility Requirements

### Accessibility Checklist
- [ ] Semantic HTML elements used
- [ ] Proper ARIA attributes added
- [ ] Keyboard navigation implemented
- [ ] Focus management handled correctly
- [ ] Color contrast meets WCAG AA standards
- [ ] Screen reader compatibility verified
- [ ] Polish language support included

### Accessibility Testing
```tsx
// Always include accessibility tests
test('component is accessible', async () => {
  const { container } = renderWithA11y(<Component />);
  await runA11yTestSuite(container, {
    testKeyboard: true,
    testScreenReader: true,
    testFocus: true,
    testPolishBusiness: true, // For Polish business components
  });
});
```

## 🇵🇱 Polish Localization

### Polish Language Guidelines
- Use proper Polish terminology for business concepts
- Ensure proper character encoding for Polish characters (ą, ć, ę, ł, ń, ó, ś, ź, ż)
- Follow Polish date and number formatting conventions
- Use appropriate Polish business language tone

### Polish Business Components
When creating Polish business components:
- Research Polish business regulations and standards
- Use official terminology from Polish government sources
- Implement proper validation for Polish business identifiers
- Follow Polish formatting conventions

## 🧪 Testing Guidelines

### Test Coverage Requirements
- **Unit Tests**: All components must have comprehensive unit tests
- **Accessibility Tests**: All components must pass accessibility tests
- **Visual Regression Tests**: Components should have visual regression tests
- **Performance Tests**: Complex components should have performance tests

### Test Structure
```tsx
describe('ComponentName', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    it('renders correctly', () => {});
    it('applies props correctly', () => {});
  });

  // Interaction tests
  describe('Interactions', () => {
    it('handles click events', () => {});
    it('handles keyboard events', () => {});
  });

  // Accessibility tests
  describe('Accessibility', () => {
    it('meets WCAG standards', () => {});
    it('supports keyboard navigation', () => {});
    it('works with screen readers', () => {});
  });

  // Polish-specific tests (if applicable)
  describe('Polish Business Features', () => {
    it('formats Polish currency correctly', () => {});
    it('validates Polish business identifiers', () => {});
  });
});
```

## 📝 Documentation Standards

### Component Documentation
Each component should include:
- Clear description of purpose and use cases
- Complete API documentation with all props
- Usage examples with code snippets
- Accessibility information
- Polish business context (if applicable)

### Documentation Template
```markdown
# ComponentName

Brief description of the component and its purpose.

## Usage

```tsx
import { ComponentName } from '@faktulove/design-system';

function Example() {
  return (
    <ComponentName variant="primary">
      Example content
    </ComponentName>
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | 'primary' \| 'secondary' | 'primary' | Visual variant |
| size | 'sm' \| 'md' \| 'lg' | 'md' | Component size |

## Accessibility

- Supports keyboard navigation
- Includes proper ARIA attributes
- Meets WCAG 2.1 Level AA standards

## Examples

### Basic Usage
[Example code]

### With Different Variants
[Example code]
```

## 🔄 Pull Request Process

### Before Submitting
1. **Test thoroughly**: Run all tests and ensure they pass
2. **Check accessibility**: Verify accessibility compliance
3. **Update documentation**: Add or update relevant documentation
4. **Follow conventions**: Ensure code follows project conventions
5. **Add changeset**: Document your changes for release notes

### Pull Request Template
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Accessibility improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Accessibility tests pass
- [ ] Visual regression tests pass
- [ ] Manual testing completed

## Accessibility
- [ ] WCAG 2.1 Level AA compliance verified
- [ ] Keyboard navigation tested
- [ ] Screen reader compatibility verified
- [ ] Polish language support verified (if applicable)

## Documentation
- [ ] Component documentation updated
- [ ] Storybook stories added/updated
- [ ] Migration guide updated (if breaking change)

## Screenshots
[Add screenshots if applicable]
```

### Review Process
1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Code Review**: Team members review code quality and design
3. **Accessibility Review**: Accessibility expert reviews compliance
4. **Design Review**: Design team reviews visual consistency
5. **Polish Business Review**: Polish business expert reviews (if applicable)

## 🐛 Bug Reports

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- Browser: [e.g., Chrome 91]
- OS: [e.g., Windows 10]
- Design System Version: [e.g., 1.2.3]

## Screenshots
[Add screenshots if applicable]

## Additional Context
Any other relevant information.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
## Feature Description
Clear description of the proposed feature.

## Use Case
Describe the problem this feature would solve.

## Proposed Solution
Describe your proposed solution.

## Alternatives Considered
Describe alternative solutions you've considered.

## Polish Business Context
If applicable, describe Polish business requirements.

## Additional Context
Any other relevant information.
```

## 📋 Code Standards

### TypeScript Guidelines
- Use strict TypeScript configuration
- Provide comprehensive type definitions
- Use proper JSDoc comments for public APIs
- Avoid `any` types - use proper typing

### React Guidelines
- Use functional components with hooks
- Use `React.forwardRef` for components that need ref forwarding
- Use proper prop destructuring and default values
- Follow React best practices for performance

### CSS Guidelines
- Use CSS custom properties for theming
- Follow BEM-like naming convention for CSS classes
- Ensure responsive design principles
- Maintain consistent spacing using design tokens

### Naming Conventions
- Components: PascalCase (e.g., `ButtonComponent`)
- Files: PascalCase for components, camelCase for utilities
- CSS classes: kebab-case with `ds-` prefix (e.g., `ds-button--primary`)
- Props: camelCase
- Types: PascalCase with descriptive suffixes

## 🚀 Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Changelog
All changes are documented in the changelog with:
- Clear description of changes
- Migration instructions for breaking changes
- Credits to contributors

## 🆘 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community support
- **Slack**: Internal team communication
- **Email**: Direct contact for sensitive issues

### Resources
- [Design System Documentation](./README.md)
- [Storybook](http://localhost:6006)
- [Accessibility Guidelines](./accessibility.md)
- [Polish Business Guide](./polish-business.md)

## 🙏 Recognition

### Contributors
All contributors are recognized in:
- README.md contributors section
- Release notes
- Annual contributor report

### Types of Recognition
- Code contributions
- Documentation improvements
- Bug reports and testing
- Community support
- Design feedback

---

**Thank you for contributing to the FaktuLove Design System! Your contributions help create better experiences for Polish businesses.** 🚀