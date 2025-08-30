# Developer Onboarding Guide

Welcome to the FaktuLove Design System! This guide will help you get up to speed quickly and become productive with our design system, whether you're new to the team or transitioning from another project.

## 🎯 Learning Path

### Week 1: Foundations
- [ ] **Setup Development Environment** (Day 1)
- [ ] **Understand Design System Principles** (Day 1-2)
- [ ] **Explore Design Tokens** (Day 2-3)
- [ ] **Learn Component Basics** (Day 3-4)
- [ ] **Practice with Simple Components** (Day 4-5)

### Week 2: Components & Patterns
- [ ] **Master Primitive Components** (Day 1-2)
- [ ] **Learn Pattern Components** (Day 2-3)
- [ ] **Understand Layout System** (Day 3-4)
- [ ] **Explore Polish Business Components** (Day 4-5)

### Week 3: Advanced Topics
- [ ] **Accessibility Implementation** (Day 1-2)
- [ ] **Testing Strategies** (Day 2-3)
- [ ] **Performance Optimization** (Day 3-4)
- [ ] **Contribution Workflow** (Day 4-5)

### Week 4: Real-World Application
- [ ] **Build Complete Feature** (Day 1-3)
- [ ] **Code Review & Feedback** (Day 3-4)
- [ ] **Documentation & Knowledge Sharing** (Day 4-5)

## 🚀 Quick Start Checklist

### Development Environment Setup
```bash
# 1. Clone the repository
git clone https://github.com/faktulove/design-system.git
cd design-system

# 2. Install dependencies
npm install

# 3. Start Storybook
npm run storybook

# 4. Run tests
npm run test:design-system

# 5. Open in browser
# Storybook: http://localhost:6006
# Tests: Watch mode in terminal
```

### IDE Setup
```json
// .vscode/settings.json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "emmet.includeLanguages": {
    "typescript": "html",
    "typescriptreact": "html"
  }
}
```

### Browser Extensions
- **React Developer Tools**: Debug React components
- **axe DevTools**: Accessibility testing
- **Storybook**: Component development

## 📚 Essential Concepts

### Design System Architecture
```
Design Tokens → Components → Patterns → Applications
     ↓              ↓          ↓           ↓
   Colors,      Button,    Card,      Invoice
   Spacing,     Input,     Form,      Management
   Typography   Select     Table      System
```

### Component Hierarchy
```tsx
// Primitive Components (Building blocks)
<Button variant="primary">Save</Button>
<Input placeholder="Enter value" />

// Pattern Components (Combinations)
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>
    <Input placeholder="Name" />
    <Button>Submit</Button>
  </Card.Body>
</Card>

// Layout Components (Structure)
<Container>
  <Grid cols={2}>
    <Card>Content 1</Card>
    <Card>Content 2</Card>
  </Grid>
</Container>

// Polish Business Components (Specialized)
<CurrencyInput currency="PLN" />
<NIPValidator />
<VATRateSelector />
```

### Design Token Usage
```tsx
import { colors, spacing, typography } from '@faktulove/design-system/tokens';

// Using tokens in components
const StyledComponent = styled.div`
  color: ${colors.primary[600]};
  padding: ${spacing[4]};
  font-size: ${typography.fontSize.lg};
`;

// CSS custom properties
.my-component {
  color: var(--ds-color-primary-600);
  padding: var(--ds-spacing-4);
  font-size: var(--ds-font-size-lg);
}
```

## 🧩 Component Development Workflow

### 1. Planning Phase
```markdown
## Component Planning Checklist
- [ ] Define component purpose and use cases
- [ ] Research existing patterns and standards
- [ ] Identify required props and variants
- [ ] Consider accessibility requirements
- [ ] Plan Polish business context (if applicable)
- [ ] Design API and TypeScript interfaces
```

### 2. Implementation Phase
```tsx
// Step 1: Create component interface
interface MyComponentProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
  'aria-label': string;
}

// Step 2: Implement component
export const MyComponent = React.forwardRef<HTMLDivElement, MyComponentProps>(
  ({ variant = 'primary', size = 'md', disabled = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'ds-my-component',
          `ds-my-component--${variant}`,
          `ds-my-component--${size}`,
          disabled && 'ds-my-component--disabled'
        )}
        aria-disabled={disabled}
        {...props}
      >
        {children}
      </div>
    );
  }
);

// Step 3: Add display name
MyComponent.displayName = 'MyComponent';
```

### 3. Testing Phase
```tsx
// Comprehensive test suite
describe('MyComponent', () => {
  // Rendering tests
  it('renders correctly', () => {
    render(<MyComponent aria-label="Test">Content</MyComponent>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  // Accessibility tests
  it('meets accessibility standards', async () => {
    const { container } = renderWithA11y(
      <MyComponent aria-label="Accessible component">Content</MyComponent>
    );
    await testPolishA11y(container);
  });

  // Interaction tests
  it('handles user interactions', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(
      <MyComponent onClick={handleClick} aria-label="Clickable">
        Click me
      </MyComponent>
    );
    
    await user.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalled();
  });
});
```

### 4. Documentation Phase
```tsx
// Storybook stories
export default {
  title: 'Components/MyComponent',
  component: MyComponent,
  parameters: {
    docs: {
      description: {
        component: 'A versatile component for...',
      },
    },
  },
} as Meta;

export const Default: Story = {
  args: {
    'aria-label': 'Default component',
    children: 'Default Content',
  },
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem' }}>
      <MyComponent variant="primary" aria-label="Primary">Primary</MyComponent>
      <MyComponent variant="secondary" aria-label="Secondary">Secondary</MyComponent>
    </div>
  ),
};
```

## 🇵🇱 Polish Business Context

### Understanding Polish Business Needs
```tsx
// Polish business components handle specific requirements
const polishBusinessRequirements = {
  currency: {
    symbol: 'zł',
    format: '1 234,56 zł', // Space as thousands separator, comma as decimal
    placement: 'suffix',
  },
  
  dates: {
    format: 'DD.MM.YYYY',
    separator: '.',
    businessContext: 'fiscal year awareness',
  },
  
  taxSystem: {
    nip: '123-456-78-90', // Tax identification number format
    vatRates: ['23%', '8%', '5%', '0%'], // Standard Polish VAT rates
    compliance: ['JPK', 'KSeF', 'SAF-T'], // Regulatory requirements
  },
  
  language: {
    locale: 'pl-PL',
    characterSet: 'UTF-8', // Support for Polish diacritics
    textLength: 'longer than English', // Plan for longer translations
  },
};
```

### Polish Component Examples
```tsx
// Currency formatting
<CurrencyInput 
  currency="PLN"
  value="1234.56"
  onChange={setValue}
  aria-label="Kwota faktury"
/>
// Displays: 1 234,56 zł

// NIP validation
<NIPValidator
  value={nip}
  onChange={setNip}
  onValidationChange={setIsValid}
  aria-label="Numer NIP"
/>
// Formats: 123-456-78-90

// VAT rate selection
<VATRateSelector
  value={vatRate}
  onChange={setVatRate}
  aria-label="Stawka VAT"
/>
// Options: 23%, 8%, 5%, 0%, zw., n.p.
```

## ♿ Accessibility Best Practices

### WCAG 2.1 Level AA Compliance
```tsx
// Essential accessibility patterns
const accessibilityPatterns = {
  // Semantic HTML
  semanticMarkup: (
    <button type="button" aria-label="Zapisz dokument">
      <SaveIcon aria-hidden="true" />
    </button>
  ),
  
  // Keyboard navigation
  keyboardSupport: {
    tab: 'Move focus forward',
    shiftTab: 'Move focus backward',
    enter: 'Activate button/link',
    space: 'Activate button/checkbox',
    escape: 'Close modal/dropdown',
    arrows: 'Navigate options',
  },
  
  // Screen reader support
  screenReader: (
    <div>
      <input
        aria-label="Numer faktury"
        aria-describedby="invoice-help"
        aria-required="true"
        aria-invalid={hasError}
      />
      <div id="invoice-help">
        Format: FV/ROK/NUMER
      </div>
    </div>
  ),
  
  // Focus management
  focusManagement: {
    visible: 'Always show focus indicators',
    logical: 'Maintain logical tab order',
    trapped: 'Trap focus in modals',
    restored: 'Restore focus when closing',
  },
};
```

### Polish Accessibility Considerations
```tsx
// Polish language accessibility
const polishA11y = {
  language: (
    <div lang="pl">
      <h1>System fakturowania</h1>
      <p>Zarządzaj fakturami swojej firmy</p>
    </div>
  ),
  
  screenReaderAnnouncements: {
    currency: 'Kwota: tysiąc dwieście trzydzieści cztery złote',
    status: 'Faktura została zapisana pomyślnie',
    error: 'Błąd: Nieprawidłowy numer NIP',
  },
  
  culturalConsiderations: {
    colorMeaning: 'Red = danger, Green = success (universal)',
    businessTerms: 'Use official Polish business terminology',
    formality: 'Professional tone in business applications',
  },
};
```

## 🧪 Testing Strategies

### Test-Driven Development
```tsx
// 1. Write test first
test('currency input formats PLN correctly', async () => {
  const user = userEvent.setup();
  
  render(<CurrencyInput currency="PLN" />);
  
  const input = screen.getByRole('textbox');
  await user.type(input, '1234.56');
  
  expect(input).toHaveValue('1 234,56 zł');
});

// 2. Implement component to pass test
// 3. Refactor and improve
// 4. Add more tests for edge cases
```

### Testing Pyramid
```tsx
// Unit Tests (70%)
describe('Component Unit Tests', () => {
  it('renders with correct props', () => {});
  it('handles state changes', () => {});
  it('validates input correctly', () => {});
});

// Integration Tests (20%)
describe('Component Integration Tests', () => {
  it('works with other components', () => {});
  it('handles form submission', () => {});
  it('manages focus correctly', () => {});
});

// E2E Tests (10%)
describe('End-to-End Tests', () => {
  it('completes user workflow', () => {});
  it('handles error scenarios', () => {});
  it('works across browsers', () => {});
});
```

### Accessibility Testing
```tsx
// Automated accessibility testing
import { runA11yTestSuite } from '@faktulove/design-system/testing';

test('component is fully accessible', async () => {
  const { container } = renderWithA11y(<Component />);
  
  await runA11yTestSuite(container, {
    testKeyboard: true,
    testScreenReader: true,
    testFocus: true,
    testPolishBusiness: true,
  });
});
```

## 🎨 Styling Guidelines

### CSS Architecture
```scss
// BEM-like naming with design system prefix
.ds-component {
  // Base styles
  
  &--variant {
    // Variant styles
  }
  
  &--size {
    // Size styles
  }
  
  &--state {
    // State styles (disabled, loading, etc.)
  }
  
  &__element {
    // Child element styles
  }
}
```

### CSS Custom Properties
```css
/* Component-specific custom properties */
.ds-button {
  background-color: var(--ds-button-bg, var(--ds-color-primary-600));
  color: var(--ds-button-color, var(--ds-color-neutral-50));
  padding: var(--ds-button-padding, var(--ds-spacing-3) var(--ds-spacing-6));
  border-radius: var(--ds-button-radius, var(--ds-border-radius-md));
}

/* Theme customization */
:root {
  --ds-button-bg: #custom-color;
  --ds-button-padding: 12px 24px;
}
```

### Responsive Design
```tsx
// Mobile-first responsive design
const ResponsiveComponent = styled.div`
  // Mobile styles (base)
  padding: ${spacing[4]};
  
  // Tablet styles
  @media (min-width: ${breakpoints.md}) {
    padding: ${spacing[6]};
  }
  
  // Desktop styles
  @media (min-width: ${breakpoints.lg}) {
    padding: ${spacing[8]};
  }
`;
```

## 🔧 Development Tools

### Essential VS Code Extensions
```json
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-json",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

### Useful Snippets
```json
// .vscode/snippets.json
{
  "React Component": {
    "prefix": "dscomp",
    "body": [
      "import React from 'react';",
      "import { cn } from '../../utils/cn';",
      "",
      "export interface ${1:ComponentName}Props {",
      "  children?: React.ReactNode;",
      "  className?: string;",
      "  'aria-label': string;",
      "}",
      "",
      "export const ${1:ComponentName} = React.forwardRef<",
      "  HTMLDivElement,",
      "  ${1:ComponentName}Props",
      ">(({ children, className, ...props }, ref) => {",
      "  return (",
      "    <div",
      "      ref={ref}",
      "      className={cn('ds-${2:component-name}', className)}",
      "      {...props}",
      "    >",
      "      {children}",
      "    </div>",
      "  );",
      "});",
      "",
      "${1:ComponentName}.displayName = '${1:ComponentName}';"
    ]
  }
}
```

### Git Workflow
```bash
# Feature development workflow
git checkout -b feature/new-component
git add .
git commit -m "feat: add new component with accessibility support"
git push origin feature/new-component

# Create pull request with template
# Get code review
# Merge to main
```

## 📈 Performance Considerations

### Bundle Size Optimization
```tsx
// Tree-shaking friendly imports
import { Button } from '@faktulove/design-system'; // ✅ Good
import * as DS from '@faktulove/design-system'; // ❌ Avoid

// Lazy loading for heavy components
const Table = lazy(() => import('@faktulove/design-system').then(m => ({ 
  default: m.Table 
})));
```

### Runtime Performance
```tsx
// Memoization for expensive calculations
const ExpensiveComponent = React.memo(({ data }) => {
  const processedData = useMemo(() => {
    return data.map(item => processItem(item));
  }, [data]);
  
  return <div>{processedData}</div>;
});

// Callback optimization
const OptimizedComponent = ({ onSubmit }) => {
  const handleSubmit = useCallback((data) => {
    onSubmit(data);
  }, [onSubmit]);
  
  return <Form onSubmit={handleSubmit} />;
};
```

## 🚨 Common Pitfalls

### Accessibility Mistakes
```tsx
// ❌ Missing ARIA label
<Button><SaveIcon /></Button>

// ✅ Proper ARIA label
<Button aria-label="Zapisz dokument">
  <SaveIcon aria-hidden="true" />
</Button>

// ❌ Color-only information
<span style={{ color: 'red' }}>Error</span>

// ✅ Icon + color + text
<span className="error">
  <ErrorIcon aria-hidden="true" />
  Błąd: Nieprawidłowe dane
</span>
```

### Polish Business Mistakes
```tsx
// ❌ Wrong currency format
<span>1,234.56 PLN</span>

// ✅ Correct Polish format
<span>1 234,56 zł</span>

// ❌ Wrong date format
<span>03/15/2024</span>

// ✅ Polish business format
<span>15.03.2024</span>
```

### Performance Mistakes
```tsx
// ❌ Inline object creation
<Component style={{ padding: '16px' }} />

// ✅ Stable reference
const componentStyle = { padding: '16px' };
<Component style={componentStyle} />

// ❌ Missing dependency array
useEffect(() => {
  fetchData();
}); // Runs on every render

// ✅ Proper dependencies
useEffect(() => {
  fetchData();
}, [id]); // Runs only when id changes
```

## 📚 Learning Resources

### Internal Resources
- **[Design System Documentation](./README.md)**: Complete documentation
- **[Storybook](http://localhost:6006)**: Interactive component examples
- **[Component Source Code](https://github.com/faktulove/design-system)**: Implementation details
- **Team Slack Channels**: #design-system, #frontend-help

### External Resources
- **React**: [Official React Documentation](https://react.dev/)
- **TypeScript**: [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- **Accessibility**: [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- **Testing**: [Testing Library Documentation](https://testing-library.com/)
- **Polish Standards**: [Polish Government Digital Standards](https://www.gov.pl/web/dostepnosc-cyfrowa)

### Practice Projects
1. **Simple Form**: Build a contact form with validation
2. **Data Table**: Create a sortable, filterable table
3. **Invoice Creator**: Build a Polish invoice creation form
4. **Dashboard**: Create a responsive dashboard layout

## 🎯 Success Metrics

### Week 1 Goals
- [ ] Successfully set up development environment
- [ ] Understand design token system
- [ ] Create first simple component
- [ ] Write basic tests

### Week 2 Goals
- [ ] Build complex component with multiple variants
- [ ] Implement proper accessibility features
- [ ] Create comprehensive Storybook stories
- [ ] Handle Polish business requirements

### Week 3 Goals
- [ ] Contribute to existing component improvements
- [ ] Write advanced tests with accessibility coverage
- [ ] Optimize component performance
- [ ] Help other team members

### Week 4 Goals
- [ ] Lead component development project
- [ ] Mentor new team members
- [ ] Contribute to design system documentation
- [ ] Present work to stakeholders

## 🆘 Getting Help

### When You're Stuck
1. **Check Documentation**: Start with design system docs
2. **Explore Storybook**: See working examples
3. **Search Codebase**: Look for similar implementations
4. **Ask Team**: Use Slack channels or direct messages
5. **Create Issue**: Document bugs or feature requests

### Escalation Path
1. **Peer Review**: Ask teammate for quick review
2. **Senior Developer**: Escalate to senior team member
3. **Tech Lead**: Involve tech lead for architectural decisions
4. **Design Team**: Consult designers for visual/UX questions

---

**Welcome to the team! We're excited to have you contribute to the FaktuLove Design System.** 🚀