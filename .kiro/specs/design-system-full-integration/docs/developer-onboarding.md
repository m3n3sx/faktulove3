# Developer Onboarding Guide

Welcome to the FaktuLove Design System! This guide will help you get up and running with our design system integration for Polish business applications.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Design System Architecture](#design-system-architecture)
5. [Development Workflow](#development-workflow)
6. [Testing Guidelines](#testing-guidelines)
7. [Code Standards](#code-standards)
8. [Polish Business Requirements](#polish-business-requirements)
9. [Contribution Guidelines](#contribution-guidelines)
10. [Resources and Support](#resources-and-support)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18.0.0 or higher)
- **npm** (v8.0.0 or higher) or **yarn** (v1.22.0 or higher)
- **Python** (v3.11 or higher) for Django backend
- **PostgreSQL** (v13 or higher) for production database
- **Git** for version control

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/faktulove/faktulove.git
   cd faktulove
   ```

2. **Install dependencies:**
   ```bash
   # Backend dependencies
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database:**
   ```bash
   python manage.py migrate
   python manage.py loaddata fixtures/design_system_test_data.json
   ```

5. **Start the development servers:**
   ```bash
   # Terminal 1: Django backend
   python manage.py runserver
   
   # Terminal 2: React frontend
   cd frontend
   npm start
   ```

6. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Design System Storybook: http://localhost:6006

## Development Environment Setup

### IDE Configuration

#### VS Code (Recommended)

Install the following extensions:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "steoates.autoimport-es6-ts",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

#### Settings Configuration

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "emmet.includeLanguages": {
    "javascript": "javascriptreact",
    "typescript": "typescriptreact"
  }
}
```

### Environment Variables

Create your `.env` file based on `.env.example`:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/faktulove
REDIS_URL=redis://localhost:6379/0

# Design System Configuration
DESIGN_SYSTEM_VERSION=1.0.0
DESIGN_SYSTEM_THEME=polish-business
DESIGN_SYSTEM_DEBUG=True

# Polish Business Settings
DEFAULT_CURRENCY=PLN
DEFAULT_LOCALE=pl-PL
VAT_RATES=0,5,8,23
NIP_VALIDATION_ENABLED=True
REGON_VALIDATION_ENABLED=True

# OCR Configuration
OCR_SERVICE_URL=http://localhost:8001
TESSERACT_LANG=pol
EASYOCR_LANG=pl

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Setup

#### Development (SQLite)

For local development, SQLite is configured by default:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/design_system_test_data.json
```

#### Production (PostgreSQL)

For production-like development:

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
brew install postgresql  # macOS

# Create database
sudo -u postgres createdb faktulove
sudo -u postgres createuser faktulove_user
sudo -u postgres psql -c "ALTER USER faktulove_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE faktulove TO faktulove_user;"

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://faktulove_user:your_password@localhost:5432/faktulove

# Run migrations
python manage.py migrate
```

## Project Structure

### Backend Structure

```
faktulove/
├── faktury/                    # Main Django app
│   ├── api/                   # REST API endpoints
│   ├── services/              # Business logic layer
│   ├── views_modules/         # Modular view organization
│   ├── templates/             # Django templates with design system
│   ├── static/                # Static assets
│   ├── migrations/            # Database migrations
│   └── tests/                 # Backend tests
├── faktulove/                 # Django project settings
├── static/                    # Collected static files
├── media/                     # User uploaded files
└── requirements.txt           # Python dependencies
```

### Frontend Structure

```
frontend/
├── src/
│   ├── design-system/         # Design system components
│   │   ├── components/        # React components
│   │   │   ├── primitives/    # Basic UI components
│   │   │   ├── patterns/      # Complex UI patterns
│   │   │   ├── business/      # Polish business components
│   │   │   └── accessibility/ # Accessibility components
│   │   ├── styles/            # CSS and themes
│   │   ├── utils/             # Utility functions
│   │   ├── hooks/             # Custom React hooks
│   │   └── types/             # TypeScript type definitions
│   ├── components/            # Application-specific components
│   ├── pages/                 # Page components
│   ├── services/              # API services
│   └── utils/                 # Application utilities
├── public/                    # Static assets
├── .storybook/                # Storybook configuration
└── package.json               # Node.js dependencies
```

### Design System Structure

```
frontend/src/design-system/
├── components/
│   ├── primitives/            # Basic components
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.stories.tsx
│   │   │   ├── Button.test.tsx
│   │   │   └── index.ts
│   │   ├── Input/
│   │   ├── Select/
│   │   └── ...
│   ├── patterns/              # Complex patterns
│   │   ├── Form/
│   │   ├── Table/
│   │   ├── Modal/
│   │   └── ...
│   ├── business/              # Polish business components
│   │   ├── NIPValidator/
│   │   ├── CurrencyInput/
│   │   ├── VATRateSelector/
│   │   └── ...
│   └── accessibility/         # Accessibility components
│       ├── LiveRegion/
│       ├── SkipLink/
│       └── ...
├── styles/                    # Styling system
│   ├── tokens/                # Design tokens
│   ├── themes/                # Theme configurations
│   └── utilities/             # CSS utilities
├── utils/                     # Utility functions
├── hooks/                     # Custom hooks
└── types/                     # TypeScript definitions
```

## Design System Architecture

### Component Hierarchy

The design system follows a hierarchical structure:

1. **Tokens**: Design tokens (colors, spacing, typography)
2. **Primitives**: Basic UI components (Button, Input, Text)
3. **Patterns**: Complex UI patterns (Form, Table, Modal)
4. **Business**: Polish business-specific components
5. **Accessibility**: Accessibility-focused components

### Component Anatomy

Each component follows a consistent structure:

```typescript
// Component interface
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

// Component implementation
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  children,
  onClick,
  ...props
}) => {
  const classes = cn(
    'ds-button',
    `ds-button--${variant}`,
    `ds-button--${size}`,
    {
      'ds-button--loading': loading,
      'ds-button--disabled': disabled
    }
  );

  return (
    <button
      className={classes}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
};
```

### Theming System

The design system uses CSS custom properties for theming:

```css
/* Design tokens */
:root {
  /* Colors */
  --ds-color-primary-50: #eff6ff;
  --ds-color-primary-500: #3b82f6;
  --ds-color-primary-900: #1e3a8a;
  
  /* Spacing */
  --ds-space-1: 0.25rem;
  --ds-space-2: 0.5rem;
  --ds-space-4: 1rem;
  
  /* Typography */
  --ds-font-size-sm: 0.875rem;
  --ds-font-size-base: 1rem;
  --ds-font-size-lg: 1.125rem;
}

/* Polish business theme */
[data-theme="polish-business"] {
  --ds-color-primary-500: #dc2626; /* Polish red */
  --ds-color-secondary-500: #ffffff; /* Polish white */
}
```

## Development Workflow

### Branch Strategy

We use Git Flow with the following branches:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `hotfix/*`: Critical bug fixes
- `release/*`: Release preparation branches

### Feature Development Process

1. **Create a feature branch:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/new-component-name
   ```

2. **Develop your feature:**
   - Write component code
   - Add Storybook stories
   - Write unit tests
   - Update documentation

3. **Test your changes:**
   ```bash
   # Run all tests
   npm test
   
   # Run specific tests
   npm test -- --testNamePattern="Button"
   
   # Run visual regression tests
   npm run test:visual
   
   # Run accessibility tests
   npm run test:a11y
   ```

4. **Create a pull request:**
   - Ensure all tests pass
   - Add screenshots for UI changes
   - Request review from design system team

5. **Merge and deploy:**
   - Squash and merge to develop
   - Deploy to staging for testing
   - Merge to main for production release

### Component Development Checklist

When creating a new component:

- [ ] Component implementation with TypeScript
- [ ] Storybook stories with all variants
- [ ] Unit tests with React Testing Library
- [ ] Accessibility tests with jest-axe
- [ ] Visual regression tests with Playwright
- [ ] Documentation with usage examples
- [ ] Polish business validation (if applicable)
- [ ] Responsive design implementation
- [ ] Dark mode support
- [ ] Performance optimization

### Code Review Guidelines

#### What to Look For

1. **Code Quality:**
   - TypeScript types are properly defined
   - Component props are well-documented
   - Error handling is implemented
   - Performance considerations are addressed

2. **Design System Compliance:**
   - Uses design tokens consistently
   - Follows component naming conventions
   - Implements accessibility requirements
   - Supports theming system

3. **Polish Business Requirements:**
   - Proper NIP/REGON validation
   - Correct VAT calculations
   - Polish date/currency formatting
   - Compliance with Polish regulations

4. **Testing:**
   - Unit tests cover all functionality
   - Accessibility tests pass
   - Visual regression tests are included
   - Edge cases are tested

#### Review Checklist

- [ ] Code follows established patterns
- [ ] TypeScript types are accurate
- [ ] Component is accessible (WCAG 2.1 AA)
- [ ] Polish business logic is correct
- [ ] Tests are comprehensive
- [ ] Documentation is complete
- [ ] Performance impact is acceptable
- [ ] Breaking changes are documented

## Testing Guidelines

### Testing Strategy

We use a multi-layered testing approach:

1. **Unit Tests**: Component logic and behavior
2. **Integration Tests**: Component interactions
3. **Visual Regression Tests**: UI consistency
4. **Accessibility Tests**: WCAG compliance
5. **Performance Tests**: Bundle size and runtime performance

### Unit Testing

Use React Testing Library for component testing:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });
});
```

### Accessibility Testing

Use jest-axe for automated accessibility testing:

```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from './Button';

expect.extend(toHaveNoViolations);

describe('Button Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<Button>Accessible button</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Visual Regression Testing

Use Playwright for visual testing:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Button Visual Tests', () => {
  test('should match button variants', async ({ page }) => {
    await page.goto('/storybook/?path=/story/button--variants');
    await expect(page).toHaveScreenshot('button-variants.png');
  });

  test('should match button states', async ({ page }) => {
    await page.goto('/storybook/?path=/story/button--states');
    await expect(page).toHaveScreenshot('button-states.png');
  });
});
```

### Polish Business Testing

Test Polish business logic thoroughly:

```typescript
import { validateNIP, formatPolishCurrency } from '../utils/polishBusiness';

describe('Polish Business Utils', () => {
  describe('NIP Validation', () => {
    it('validates correct NIP', () => {
      expect(validateNIP('1234567890')).toBe(true);
    });

    it('rejects invalid NIP', () => {
      expect(validateNIP('1234567891')).toBe(false);
    });

    it('handles NIP with spaces and dashes', () => {
      expect(validateNIP('123-456-78-90')).toBe(true);
      expect(validateNIP('123 456 78 90')).toBe(true);
    });
  });

  describe('Currency Formatting', () => {
    it('formats Polish currency correctly', () => {
      expect(formatPolishCurrency(1234.56)).toBe('1 234,56 zł');
    });

    it('handles zero amounts', () => {
      expect(formatPolishCurrency(0)).toBe('0,00 zł');
    });
  });
});
```

## Code Standards

### TypeScript Guidelines

1. **Use strict TypeScript configuration:**
   ```json
   {
     "compilerOptions": {
       "strict": true,
       "noImplicitAny": true,
       "noImplicitReturns": true,
       "noUnusedLocals": true,
       "noUnusedParameters": true
     }
   }
   ```

2. **Define proper interfaces:**
   ```typescript
   // Good
   interface ButtonProps {
     variant: 'primary' | 'secondary';
     size: 'sm' | 'md' | 'lg';
     disabled?: boolean;
     children: React.ReactNode;
   }

   // Avoid
   interface ButtonProps {
     variant: string;
     size: string;
     disabled: boolean | undefined;
     children: any;
   }
   ```

3. **Use generic types appropriately:**
   ```typescript
   interface SelectProps<T> {
     value: T;
     options: Array<{ value: T; label: string }>;
     onChange: (value: T) => void;
   }
   ```

### React Guidelines

1. **Use functional components with hooks:**
   ```typescript
   // Good
   const Button: React.FC<ButtonProps> = ({ variant, children }) => {
     return <button className={`btn-${variant}`}>{children}</button>;
   };

   // Avoid class components for new code
   ```

2. **Implement proper error boundaries:**
   ```typescript
   const ComponentWithErrorBoundary = () => (
     <ErrorBoundary fallback={<ErrorMessage />}>
       <YourComponent />
     </ErrorBoundary>
   );
   ```

3. **Use React.memo for performance optimization:**
   ```typescript
   const ExpensiveComponent = React.memo<Props>(({ data }) => {
     // Expensive rendering logic
   }, (prevProps, nextProps) => {
     return prevProps.data.id === nextProps.data.id;
   });
   ```

### CSS Guidelines

1. **Use CSS custom properties for theming:**
   ```css
   .button {
     background-color: var(--ds-color-primary-500);
     padding: var(--ds-space-2) var(--ds-space-4);
     border-radius: var(--ds-border-radius-md);
   }
   ```

2. **Follow BEM naming convention for CSS classes:**
   ```css
   .ds-button { /* Block */ }
   .ds-button--primary { /* Modifier */ }
   .ds-button__icon { /* Element */ }
   ```

3. **Use logical properties for internationalization:**
   ```css
   .component {
     margin-inline-start: var(--ds-space-2);
     padding-block: var(--ds-space-1);
   }
   ```

### Naming Conventions

1. **Components**: PascalCase (`Button`, `InputField`)
2. **Files**: PascalCase for components (`Button.tsx`)
3. **Variables**: camelCase (`isLoading`, `handleClick`)
4. **Constants**: UPPER_SNAKE_CASE (`MAX_ITEMS`, `DEFAULT_THEME`)
5. **CSS Classes**: kebab-case with prefix (`ds-button`, `ds-input-field`)

## Polish Business Requirements

### Regulatory Compliance

1. **VAT Compliance:**
   - Support Polish VAT rates (0%, 5%, 8%, 23%)
   - Proper VAT calculation and rounding
   - VAT exemption handling
   - KSeF (National e-Invoice System) compliance

2. **NIP Validation:**
   - Format validation (10 digits)
   - Checksum validation
   - Proper error messages in Polish

3. **Date Formatting:**
   - Polish date format (DD.MM.YYYY)
   - Polish locale for date pickers
   - Business day calculations
   - Polish holiday calendar

4. **Currency Formatting:**
   - Polish złoty (PLN) formatting
   - Proper decimal separator (comma)
   - Thousand separator (space)
   - Currency symbol placement

### Localization Requirements

1. **Language Support:**
   - All UI text in Polish
   - Proper Polish grammar forms
   - Date and number localization
   - Error messages in Polish

2. **Cultural Considerations:**
   - Polish business practices
   - Invoice numbering conventions
   - Payment terms standards
   - Legal document requirements

### Implementation Examples

```typescript
// NIP Validation Component
const NIPValidator: React.FC<NIPValidatorProps> = ({ value, onChange, onValidation }) => {
  const validateNIP = (nip: string) => {
    const cleanNIP = nip.replace(/[\s-]/g, '');
    
    if (!/^\d{10}$/.test(cleanNIP)) {
      onValidation(false, 'NIP musi składać się z 10 cyfr');
      return false;
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
      onValidation(false, 'Nieprawidłowa suma kontrolna NIP');
      return false;
    }
    
    onValidation(true, '');
    return true;
  };

  return (
    <Input
      label="NIP"
      value={value}
      onChange={onChange}
      onBlur={() => validateNIP(value)}
      validation={validateNIP}
      placeholder="1234567890"
      maxLength={13} // Allow for spaces and dashes
    />
  );
};
```

## Contribution Guidelines

### Getting Started with Contributions

1. **Fork the repository** and create your feature branch
2. **Set up your development environment** following this guide
3. **Read the existing code** to understand patterns and conventions
4. **Start with small contributions** to get familiar with the codebase

### Types of Contributions

1. **Bug Fixes:**
   - Fix existing component issues
   - Improve accessibility
   - Performance optimizations

2. **New Components:**
   - Add missing primitive components
   - Create new business components
   - Implement accessibility components

3. **Documentation:**
   - Improve existing documentation
   - Add usage examples
   - Create tutorials

4. **Testing:**
   - Add missing tests
   - Improve test coverage
   - Add visual regression tests

### Contribution Process

1. **Create an Issue:**
   - Describe the problem or feature request
   - Provide examples and use cases
   - Get feedback from maintainers

2. **Implement the Solution:**
   - Follow coding standards
   - Write comprehensive tests
   - Update documentation

3. **Submit a Pull Request:**
   - Provide clear description
   - Include screenshots for UI changes
   - Ensure all checks pass

4. **Code Review:**
   - Address reviewer feedback
   - Make necessary changes
   - Maintain code quality

### Component Contribution Checklist

- [ ] Component follows design system patterns
- [ ] TypeScript interfaces are properly defined
- [ ] Accessibility requirements are met (WCAG 2.1 AA)
- [ ] Polish business requirements are implemented (if applicable)
- [ ] Unit tests achieve >90% coverage
- [ ] Visual regression tests are included
- [ ] Storybook stories demonstrate all variants
- [ ] Documentation includes usage examples
- [ ] Performance impact is minimal
- [ ] Breaking changes are documented

## Resources and Support

### Documentation

- **Design System Documentation**: `/docs/design-system/`
- **API Documentation**: `/docs/api/`
- **Component Library**: Storybook at `http://localhost:6006`
- **Polish Business Guide**: `/docs/polish-business-requirements.md`

### Tools and Libraries

#### Frontend
- **React**: UI library
- **TypeScript**: Type safety
- **Storybook**: Component development
- **React Testing Library**: Component testing
- **Playwright**: E2E and visual testing
- **jest-axe**: Accessibility testing

#### Backend
- **Django**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **Redis**: Caching and sessions
- **Celery**: Background tasks

#### Development Tools
- **ESLint**: JavaScript linting
- **Prettier**: Code formatting
- **Husky**: Git hooks
- **lint-staged**: Pre-commit linting

### Getting Help

1. **Team Chat**: Join our Slack channel `#design-system`
2. **GitHub Issues**: Create issues for bugs and feature requests
3. **Code Reviews**: Request reviews from `@design-system-team`
4. **Office Hours**: Weekly design system office hours (Fridays 2-3 PM)

### Learning Resources

1. **Design System Principles**: 
   - [Atomic Design by Brad Frost](https://atomicdesign.bradfrost.com/)
   - [Design Systems Handbook](https://www.designbetter.co/design-systems-handbook)

2. **React and TypeScript**:
   - [React Documentation](https://react.dev/)
   - [TypeScript Handbook](https://www.typescriptlang.org/docs/)

3. **Accessibility**:
   - [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
   - [A11y Project](https://www.a11yproject.com/)

4. **Polish Business Requirements**:
   - [Polish VAT Law](https://www.gov.pl/web/kas/vat)
   - [KSeF Documentation](https://www.gov.pl/web/kas/krajowy-system-e-faktur)

### Common Commands

```bash
# Development
npm start                    # Start development server
npm run storybook           # Start Storybook
python manage.py runserver  # Start Django server

# Testing
npm test                    # Run unit tests
npm run test:watch         # Run tests in watch mode
npm run test:coverage      # Run tests with coverage
npm run test:a11y          # Run accessibility tests
npm run test:visual        # Run visual regression tests

# Building
npm run build              # Build for production
npm run build-storybook    # Build Storybook

# Linting and Formatting
npm run lint               # Run ESLint
npm run lint:fix           # Fix ESLint issues
npm run format             # Format code with Prettier

# Django Commands
python manage.py migrate                    # Run migrations
python manage.py makemigrations            # Create migrations
python manage.py collectstatic             # Collect static files
python manage.py test                      # Run Django tests
python manage.py validate_design_system_integration  # Validate integration
```

Welcome to the team! We're excited to have you contribute to the FaktuLove Design System. If you have any questions, don't hesitate to reach out to the team.