# Design System Architecture

## Overview

The FaktuLove Design System provides a comprehensive foundation for building consistent, accessible, and scalable user interfaces. It establishes a unified visual language that reflects Polish business culture while maintaining modern web standards and accessibility compliance.

The system is built on a token-based architecture that separates design decisions from implementation details, enabling consistent theming across React components and future platform extensions.

## Architecture

### Token-Based Design System

The design system follows a three-tier token architecture:

1. **Global Tokens**: Core design decisions (colors, typography, spacing)
2. **Semantic Tokens**: Context-specific mappings (primary, success, warning)
3. **Component Tokens**: Component-specific overrides and variations

```
Global Tokens → Semantic Tokens → Component Tokens → Components
```

### Technology Stack

- **TypeScript**: Type-safe token definitions and component interfaces
- **Tailwind CSS**: Utility-first styling with custom configuration
- **CSS Custom Properties**: Runtime theme switching capability
- **React 18**: Component implementation with modern patterns
- **Storybook**: Component documentation and testing
- **Jest + React Testing Library**: Automated testing

### File Structure

```
frontend/src/design-system/
├── tokens/
│   ├── colors.ts           # Color palette definitions
│   ├── typography.ts       # Font scales and families
│   ├── spacing.ts          # Spacing scale (8px grid)
│   ├── breakpoints.ts      # Responsive breakpoints
│   ├── shadows.ts          # Elevation system
│   └── index.ts           # Token exports
├── components/
│   ├── primitives/        # Base components (Button, Input)
│   ├── patterns/          # Composite components (Form, Card)
│   ├── layouts/           # Layout components (Grid, Container)
│   └── index.ts          # Component exports
├── utils/
│   ├── theme.ts          # Theme utilities
│   ├── accessibility.ts  # A11y helpers
│   └── responsive.ts     # Responsive utilities
└── index.ts              # Main export
```

## Components and Interfaces

### Core Component Categories

#### 1. Primitive Components
Basic building blocks with minimal styling and maximum flexibility:

- **Button**: Primary, secondary, ghost, and danger variants
- **Input**: Text, email, password, number with validation states
- **Select**: Single and multi-select with search capability
- **Checkbox**: Standard and indeterminate states
- **Radio**: Grouped radio button sets
- **Switch**: Toggle switches for boolean settings

#### 2. Pattern Components
Composite components for common use cases:

- **Form**: Complete form layouts with validation
- **Card**: Content containers with headers and actions
- **Table**: Data tables with sorting and pagination
- **Modal**: Overlay dialogs with focus management
- **Toast**: Notification system with queue management
- **Breadcrumb**: Navigation hierarchy display

#### 3. Layout Components
Structural components for page organization:

- **Container**: Max-width containers with responsive padding
- **Grid**: CSS Grid-based layout system
- **Flex**: Flexbox utilities with gap support
- **Stack**: Vertical and horizontal spacing utilities
- **Sidebar**: Collapsible navigation sidebar

### TypeScript Interface Design

```typescript
// Base component props interface
interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
  testId?: string;
}

// Size variants for consistent scaling
type SizeVariant = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

// Color variants for semantic meaning
type ColorVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error';

// Component state variants
type StateVariant = 'default' | 'hover' | 'active' | 'disabled' | 'loading';
```

## Data Models

### Design Token Structure

```typescript
interface DesignTokens {
  colors: {
    primary: ColorScale;
    secondary: ColorScale;
    success: ColorScale;
    warning: ColorScale;
    error: ColorScale;
    neutral: ColorScale;
  };
  typography: {
    fontFamily: FontFamilyTokens;
    fontSize: FontSizeScale;
    fontWeight: FontWeightScale;
    lineHeight: LineHeightScale;
  };
  spacing: SpacingScale;
  breakpoints: BreakpointTokens;
  shadows: ShadowScale;
  borderRadius: BorderRadiusScale;
}

interface ColorScale {
  50: string;   // Lightest
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;  // Base color
  600: string;
  700: string;
  800: string;
  900: string;  // Darkest
}
```

### Component Configuration

```typescript
interface ComponentConfig {
  variants: {
    [key: string]: {
      base: string;
      states: {
        default: string;
        hover: string;
        active: string;
        disabled: string;
      };
    };
  };
  sizes: {
    [key in SizeVariant]: {
      padding: string;
      fontSize: string;
      height: string;
    };
  };
}
```

## Error Handling

### Design System Error Boundaries

1. **Token Resolution Errors**: Fallback to default values when custom tokens fail
2. **Component Prop Validation**: TypeScript compile-time validation with runtime warnings
3. **Accessibility Violations**: Development-time warnings for missing ARIA attributes
4. **Theme Loading Failures**: Graceful degradation to system defaults

### Error Recovery Strategies

```typescript
// Token fallback system
const getToken = (path: string, fallback: string) => {
  try {
    return resolveTokenPath(path);
  } catch (error) {
    console.warn(`Token ${path} not found, using fallback: ${fallback}`);
    return fallback;
  }
};

// Component error boundaries
class DesignSystemErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log design system errors for monitoring
    logDesignSystemError(error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <FallbackComponent />;
    }
    return this.props.children;
  }
}
```

## Testing Strategy

### Unit Testing Approach

1. **Token Validation Tests**: Ensure all tokens resolve correctly
2. **Component Rendering Tests**: Verify components render with all prop combinations
3. **Accessibility Tests**: Automated a11y testing with jest-axe
4. **Visual Regression Tests**: Storybook visual testing integration
5. **Interaction Tests**: User event simulation and state management

### Test Structure

```typescript
// Component test example
describe('Button Component', () => {
  it('renders with correct variant styles', () => {
    render(<Button variant="primary">Click me</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-primary-600');
  });

  it('meets accessibility standards', async () => {
    const { container } = render(<Button>Accessible button</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('handles keyboard navigation', () => {
    render(<Button onClick={mockFn}>Test</Button>);
    const button = screen.getByRole('button');
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(mockFn).toHaveBeenCalled();
  });
});
```

### Storybook Integration

```typescript
// Story configuration for comprehensive testing
export default {
  title: 'Design System/Button',
  component: Button,
  parameters: {
    docs: { description: { component: 'Primary button component' } },
    a11y: { config: { rules: [{ id: 'color-contrast', enabled: true }] } }
  },
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary', 'ghost'] },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
    disabled: { control: 'boolean' }
  }
};
```

## Polish Business Requirements Integration

### Cultural Adaptations

1. **Typography**: Inter font with full Polish character support (ą, ć, ę, ł, ń, ó, ś, ź, ż)
2. **Color Psychology**: Blue conveys trust and professionalism in Polish business culture
3. **Layout Density**: Slightly higher information density preferred by Polish users
4. **Form Patterns**: Validation messages in Polish with appropriate tone

### Accounting-Specific Components

1. **Currency Input**: PLN formatting with proper decimal handling
2. **Date Picker**: Polish date format (DD.MM.YYYY) with fiscal year awareness
3. **VAT Rate Selector**: Standard Polish VAT rates (23%, 8%, 5%, 0%)
4. **NIP Validator**: Real-time NIP number validation with formatting
5. **Invoice Status Badge**: Polish invoice lifecycle states

### Accessibility for Polish Users

1. **Screen Reader Support**: Polish language announcements
2. **Keyboard Shortcuts**: Polish keyboard layout considerations
3. **High Contrast Mode**: Enhanced contrast for older users
4. **Text Scaling**: Support for 200% zoom without horizontal scrolling

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Set up token system and TypeScript definitions
- Configure Tailwind with custom tokens
- Create base component interfaces
- Establish testing infrastructure

### Phase 2: Core Components (Week 3-4)
- Implement primitive components (Button, Input, Select)
- Add accessibility features and ARIA support
- Create comprehensive test suites
- Set up Storybook documentation

### Phase 3: Pattern Components (Week 5-6)
- Build composite components (Form, Card, Table)
- Implement Polish-specific components
- Add responsive behavior and mobile optimization
- Create usage guidelines and examples

### Phase 4: Integration & Documentation (Week 7-8)
- Integrate with existing FaktuLove codebase
- Create migration guides for existing components
- Finalize documentation and accessibility audit
- Performance optimization and bundle analysis