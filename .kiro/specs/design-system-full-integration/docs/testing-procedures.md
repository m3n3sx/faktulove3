# Testing Procedures and Quality Standards

This document outlines comprehensive testing procedures and quality standards for the FaktuLove Design System integration.

## Table of Contents

1. [Testing Strategy Overview](#testing-strategy-overview)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [Visual Regression Testing](#visual-regression-testing)
5. [Accessibility Testing](#accessibility-testing)
6. [Performance Testing](#performance-testing)
7. [Polish Business Logic Testing](#polish-business-logic-testing)
8. [End-to-End Testing](#end-to-end-testing)
9. [Quality Gates](#quality-gates)
10. [Continuous Integration](#continuous-integration)

## Testing Strategy Overview

### Testing Pyramid

Our testing strategy follows the testing pyramid approach:

```
    /\
   /  \     E2E Tests (Few, High-level)
  /____\    
 /      \   Integration Tests (Some, Mid-level)
/________\  Unit Tests (Many, Low-level)
```

### Test Types and Coverage

| Test Type | Coverage Target | Tools | Frequency |
|-----------|----------------|-------|-----------|
| Unit Tests | >90% | Jest, RTL | Every commit |
| Integration Tests | >80% | Jest, RTL | Every PR |
| Visual Regression | 100% UI states | Playwright, Chromatic | Every PR |
| Accessibility | 100% components | jest-axe, Pa11y | Every PR |
| Performance | All components | Lighthouse, Bundle Analyzer | Every release |
| E2E Tests | Critical paths | Playwright | Nightly |

### Quality Standards

- **Zero tolerance** for accessibility violations
- **90%+ code coverage** for all components
- **100% visual coverage** for all component states
- **Sub-100ms** component render times
- **WCAG 2.1 AA compliance** for all interactive elements

## Unit Testing

### Testing Framework Setup

```typescript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/test-utils/setup.ts'],
  moduleNameMapping: {
    '^@design-system/(.*)$': '<rootDir>/src/design-system/$1',
    '\\.(css|less|scss)$': 'identity-obj-proxy'
  },
  collectCoverageFrom: [
    'src/design-system/**/*.{ts,tsx}',
    '!src/design-system/**/*.stories.{ts,tsx}',
    '!src/design-system/**/*.d.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    }
  }
};
```

### Test Setup Utilities

```typescript
// src/test-utils/setup.ts
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { toHaveNoViolations } from 'jest-axe';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Configure React Testing Library
configure({
  testIdAttribute: 'data-testid'
});

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}));
```

### Component Testing Template

```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';
import { Button } from './Button';
import { ThemeProvider } from '../../theme';

// Test wrapper with theme
const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme="polish-business">
      {ui}
    </ThemeProvider>
  );
};

describe('Button Component', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {
      renderWithTheme(<Button>Click me</Button>);
      
      const button = screen.getByRole('button', { name: /click me/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('ds-button');
      expect(button).toHaveClass('ds-button--primary');
      expect(button).toHaveClass('ds-button--md');
    });

    it('renders all variants correctly', () => {
      const variants = ['primary', 'secondary', 'outline', 'ghost'] as const;
      
      variants.forEach(variant => {
        const { rerender } = renderWithTheme(
          <Button variant={variant}>Test</Button>
        );
        
        const button = screen.getByRole('button');
        expect(button).toHaveClass(`ds-button--${variant}`);
        
        rerender(<Button variant={variant}>Test</Button>);
      });
    });

    it('renders all sizes correctly', () => {
      const sizes = ['sm', 'md', 'lg'] as const;
      
      sizes.forEach(size => {
        const { rerender } = renderWithTheme(
          <Button size={size}>Test</Button>
        );
        
        const button = screen.getByRole('button');
        expect(button).toHaveClass(`ds-button--${size}`);
        
        rerender(<Button size={size}>Test</Button>);
      });
    });

    it('applies custom className', () => {
      renderWithTheme(
        <Button className="custom-class">Test</Button>
      );
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
      expect(button).toHaveClass('ds-button');
    });
  });

  describe('States', () => {
    it('handles disabled state', () => {
      renderWithTheme(<Button disabled>Disabled</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveClass('ds-button--disabled');
    });

    it('handles loading state', () => {
      renderWithTheme(<Button loading>Loading</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveClass('ds-button--loading');
      expect(screen.getByTestId('spinner')).toBeInTheDocument();
    });

    it('shows loading spinner with correct size', () => {
      renderWithTheme(<Button loading size="lg">Loading</Button>);
      
      const spinner = screen.getByTestId('spinner');
      expect(spinner).toHaveClass('ds-spinner--sm'); // Spinner is always smaller
    });
  });

  describe('Interactions', () => {
    it('calls onClick when clicked', async () => {
      const user = userEvent.setup();
      const handleClick = jest.fn();
      
      renderWithTheme(
        <Button onClick={handleClick}>Click me</Button>
      );
      
      await user.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', async () => {
      const user = userEvent.setup();
      const handleClick = jest.fn();
      
      renderWithTheme(
        <Button onClick={handleClick} disabled>Disabled</Button>
      );
      
      await user.click(screen.getByRole('button'));
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('does not call onClick when loading', async () => {
      const user = userEvent.setup();
      const handleClick = jest.fn();
      
      renderWithTheme(
        <Button onClick={handleClick} loading>Loading</Button>
      );
      
      await user.click(screen.getByRole('button'));
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('handles keyboard activation', async () => {
      const user = userEvent.setup();
      const handleClick = jest.fn();
      
      renderWithTheme(
        <Button onClick={handleClick}>Keyboard</Button>
      );
      
      const button = screen.getByRole('button');
      button.focus();
      
      await user.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalledTimes(1);
      
      await user.keyboard(' ');
      expect(handleClick).toHaveBeenCalledTimes(2);
    });
  });

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      const { container } = renderWithTheme(
        <Button>Accessible button</Button>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('supports custom aria-label', () => {
      renderWithTheme(
        <Button aria-label="Custom label">Icon only</Button>
      );
      
      expect(screen.getByLabelText('Custom label')).toBeInTheDocument();
    });

    it('has proper focus indicators', () => {
      renderWithTheme(<Button>Focus me</Button>);
      
      const button = screen.getByRole('button');
      button.focus();
      
      expect(button).toHaveFocus();
      expect(button).toHaveClass('ds-button--focused');
    });
  });

  describe('Polish Business Integration', () => {
    it('renders Polish text correctly', () => {
      renderWithTheme(<Button>Zapisz fakturę</Button>);
      
      expect(screen.getByText('Zapisz fakturę')).toBeInTheDocument();
    });

    it('handles Polish special characters', () => {
      const polishText = 'Wyślij żądanie';
      renderWithTheme(<Button>{polishText}</Button>);
      
      expect(screen.getByText(polishText)).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty children', () => {
      renderWithTheme(<Button />);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toBeEmptyDOMElement();
    });

    it('handles very long text', () => {
      const longText = 'A'.repeat(1000);
      renderWithTheme(<Button>{longText}</Button>);
      
      expect(screen.getByText(longText)).toBeInTheDocument();
    });

    it('handles special characters in props', () => {
      renderWithTheme(
        <Button data-testid="special-chars-&-symbols">Test</Button>
      );
      
      expect(screen.getByTestId('special-chars-&-symbols')).toBeInTheDocument();
    });
  });
});
```

### Hook Testing

```typescript
// usePolishValidation.test.ts
import { renderHook, act } from '@testing-library/react';
import { usePolishValidation } from './usePolishValidation';

describe('usePolishValidation', () => {
  describe('NIP Validation', () => {
    it('validates correct NIP', () => {
      const { result } = renderHook(() => usePolishValidation());
      
      act(() => {
        const validation = result.current.validateNIP('1234567890');
        expect(validation.isValid).toBe(true);
        expect(validation.message).toBe('');
      });
    });

    it('rejects invalid NIP format', () => {
      const { result } = renderHook(() => usePolishValidation());
      
      act(() => {
        const validation = result.current.validateNIP('123');
        expect(validation.isValid).toBe(false);
        expect(validation.message).toBe('NIP musi składać się z 10 cyfr');
      });
    });

    it('rejects invalid NIP checksum', () => {
      const { result } = renderHook(() => usePolishValidation());
      
      act(() => {
        const validation = result.current.validateNIP('1234567891');
        expect(validation.isValid).toBe(false);
        expect(validation.message).toBe('Nieprawidłowa suma kontrolna NIP');
      });
    });
  });

  describe('Currency Validation', () => {
    it('validates Polish currency format', () => {
      const { result } = renderHook(() => usePolishValidation());
      
      act(() => {
        const validation = result.current.validateCurrency('1 234,56');
        expect(validation.isValid).toBe(true);
      });
    });

    it('rejects invalid currency format', () => {
      const { result } = renderHook(() => usePolishValidation());
      
      act(() => {
        const validation = result.current.validateCurrency('1,234.56');
        expect(validation.isValid).toBe(false);
        expect(validation.message).toContain('format');
      });
    });
  });
});
```

## Integration Testing

### Component Integration Tests

```typescript
// InvoiceForm.integration.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InvoiceForm } from './InvoiceForm';
import { ThemeProvider } from '../../theme';
import * as api from '../../services/api';

// Mock API calls
jest.mock('../../services/api');
const mockApi = api as jest.Mocked<typeof api>;

const renderInvoiceForm = (props = {}) => {
  const defaultProps = {
    companies: [
      { id: '1', name: 'Test Company', nip: '1234567890' }
    ],
    contractors: [
      { id: '1', name: 'Test Contractor', nip: '0987654321' }
    ],
    onSubmit: jest.fn(),
    ...props
  };

  return render(
    <ThemeProvider theme="polish-business">
      <InvoiceForm {...defaultProps} />
    </ThemeProvider>
  );
};

describe('InvoiceForm Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('completes full invoice creation workflow', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    
    renderInvoiceForm({ onSubmit });

    // Fill invoice number
    await user.type(
      screen.getByLabelText(/numer faktury/i),
      'FV/2024/01/001'
    );

    // Select company
    await user.click(screen.getByLabelText(/firma/i));
    await user.click(screen.getByText('Test Company'));

    // Select contractor
    await user.click(screen.getByLabelText(/kontrahent/i));
    await user.click(screen.getByText('Test Contractor'));

    // Add invoice item
    await user.type(
      screen.getByLabelText(/nazwa towaru/i),
      'Usługa programistyczna'
    );
    
    await user.clear(screen.getByLabelText(/ilość/i));
    await user.type(screen.getByLabelText(/ilość/i), '10');
    
    await user.clear(screen.getByLabelText(/cena netto/i));
    await user.type(screen.getByLabelText(/cena netto/i), '100,00');

    // Submit form
    await user.click(screen.getByRole('button', { name: /wystaw fakturę/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          number: 'FV/2024/01/001',
          companyId: '1',
          contractorId: '1',
          items: expect.arrayContaining([
            expect.objectContaining({
              name: 'Usługa programistyczna',
              quantity: 10,
              netPrice: 100,
              netAmount: 1000
            })
          ])
        })
      );
    });
  });

  it('validates form before submission', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    
    renderInvoiceForm({ onSubmit });

    // Try to submit without required fields
    await user.click(screen.getByRole('button', { name: /wystaw fakturę/i }));

    // Should show validation errors
    expect(screen.getByText(/numer faktury jest wymagany/i)).toBeInTheDocument();
    expect(screen.getByText(/firma jest wymagana/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('calculates totals correctly', async () => {
    const user = userEvent.setup();
    
    renderInvoiceForm();

    // Add first item
    await user.type(screen.getByLabelText(/nazwa towaru/i), 'Item 1');
    await user.clear(screen.getByLabelText(/ilość/i));
    await user.type(screen.getByLabelText(/ilość/i), '2');
    await user.clear(screen.getByLabelText(/cena netto/i));
    await user.type(screen.getByLabelText(/cena netto/i), '100,00');

    // Add second item
    await user.click(screen.getByText(/dodaj pozycję/i));
    
    const items = screen.getAllByLabelText(/nazwa towaru/i);
    await user.type(items[1], 'Item 2');
    
    const quantities = screen.getAllByLabelText(/ilość/i);
    await user.clear(quantities[1]);
    await user.type(quantities[1], '3');
    
    const prices = screen.getAllByLabelText(/cena netto/i);
    await user.clear(prices[1]);
    await user.type(prices[1], '50,00');

    // Check calculated totals
    await waitFor(() => {
      expect(screen.getByText('350,00 zł')).toBeInTheDocument(); // Net total
      expect(screen.getByText('80,50 zł')).toBeInTheDocument();  // VAT total
      expect(screen.getByText('430,50 zł')).toBeInTheDocument(); // Gross total
    });
  });
});
```

### API Integration Tests

```typescript
// api.integration.test.ts
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { invoiceApi } from './invoiceApi';

const server = setupServer(
  rest.post('/api/invoices/', (req, res, ctx) => {
    return res(
      ctx.json({
        id: '1',
        number: 'FV/2024/01/001',
        status: 'draft'
      })
    );
  }),
  
  rest.get('/api/invoices/:id', (req, res, ctx) => {
    return res(
      ctx.json({
        id: req.params.id,
        number: 'FV/2024/01/001',
        status: 'sent'
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Invoice API Integration', () => {
  it('creates invoice successfully', async () => {
    const invoiceData = {
      number: 'FV/2024/01/001',
      companyId: '1',
      contractorId: '1',
      items: []
    };

    const result = await invoiceApi.create(invoiceData);

    expect(result).toEqual({
      id: '1',
      number: 'FV/2024/01/001',
      status: 'draft'
    });
  });

  it('handles API errors gracefully', async () => {
    server.use(
      rest.post('/api/invoices/', (req, res, ctx) => {
        return res(
          ctx.status(400),
          ctx.json({
            error: 'Invalid invoice data'
          })
        );
      })
    );

    await expect(invoiceApi.create({})).rejects.toThrow('Invalid invoice data');
  });
});
```

## Visual Regression Testing

### Playwright Visual Testing Setup

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './src/design-system/__tests__/visual',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:6006', // Storybook URL
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] }
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] }
    }
  ],
  webServer: {
    command: 'npm run storybook',
    port: 6006,
    reuseExistingServer: !process.env.CI
  }
});
```

### Visual Test Examples

```typescript
// Button.visual.test.ts
import { test, expect } from '@playwright/test';

test.describe('Button Visual Tests', () => {
  test('all variants', async ({ page }) => {
    await page.goto('/?path=/story/button--variants');
    await page.waitForLoadState('networkidle');
    
    const canvas = page.locator('#storybook-root');
    await expect(canvas).toHaveScreenshot('button-variants.png');
  });

  test('all sizes', async ({ page }) => {
    await page.goto('/?path=/story/button--sizes');
    await page.waitForLoadState('networkidle');
    
    const canvas = page.locator('#storybook-root');
    await expect(canvas).toHaveScreenshot('button-sizes.png');
  });

  test('interactive states', async ({ page }) => {
    await page.goto('/?path=/story/button--interactive');
    await page.waitForLoadState('networkidle');
    
    const button = page.locator('[data-testid="interactive-button"]');
    
    // Default state
    await expect(button).toHaveScreenshot('button-default.png');
    
    // Hover state
    await button.hover();
    await expect(button).toHaveScreenshot('button-hover.png');
    
    // Focus state
    await button.focus();
    await expect(button).toHaveScreenshot('button-focus.png');
    
    // Active state
    await button.click();
    await expect(button).toHaveScreenshot('button-active.png');
  });

  test('responsive behavior', async ({ page }) => {
    await page.goto('/?path=/story/button--responsive');
    
    // Desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('#storybook-root')).toHaveScreenshot('button-desktop.png');
    
    // Tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('#storybook-root')).toHaveScreenshot('button-tablet.png');
    
    // Mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('#storybook-root')).toHaveScreenshot('button-mobile.png');
  });

  test('dark theme', async ({ page }) => {
    await page.goto('/?path=/story/button--variants');
    
    // Switch to dark theme
    await page.evaluate(() => {
      document.documentElement.setAttribute('data-theme', 'dark');
    });
    
    await page.waitForTimeout(100); // Allow theme transition
    await expect(page.locator('#storybook-root')).toHaveScreenshot('button-dark-theme.png');
  });

  test('polish business theme', async ({ page }) => {
    await page.goto('/?path=/story/button--variants');
    
    // Switch to Polish business theme
    await page.evaluate(() => {
      document.documentElement.setAttribute('data-theme', 'polish-business');
    });
    
    await page.waitForTimeout(100);
    await expect(page.locator('#storybook-root')).toHaveScreenshot('button-polish-theme.png');
  });
});
```

### Chromatic Integration

```typescript
// .storybook/main.ts
module.exports = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
    '@chromatic-com/storybook'
  ],
  framework: {
    name: '@storybook/react-vite',
    options: {}
  }
};
```

## Accessibility Testing

### Automated Accessibility Testing

```typescript
// accessibility.test.ts
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from '../Button';
import { Input } from '../Input';
import { Modal } from '../Modal';

expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  describe('Button Accessibility', () => {
    it('should not have violations', async () => {
      const { container } = render(<Button>Test Button</Button>);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA attributes', () => {
      const { container } = render(
        <Button aria-label="Save document" disabled>
          Save
        </Button>
      );
      
      const button = container.querySelector('button');
      expect(button).toHaveAttribute('aria-label', 'Save document');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });
  });

  describe('Form Accessibility', () => {
    it('should associate labels with inputs', async () => {
      const { container } = render(
        <div>
          <label htmlFor="email">Email</label>
          <Input id="email" type="email" />
        </div>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should announce errors to screen readers', async () => {
      const { container } = render(
        <div>
          <label htmlFor="email">Email</label>
          <Input 
            id="email" 
            type="email" 
            aria-describedby="email-error"
            aria-invalid="true"
          />
          <div id="email-error" role="alert">
            Email is required
          </div>
        </div>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Modal Accessibility', () => {
    it('should trap focus within modal', async () => {
      const { container } = render(
        <Modal isOpen onClose={() => {}}>
          <h2>Modal Title</h2>
          <button>First Button</button>
          <button>Second Button</button>
        </Modal>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });
});
```

### Manual Accessibility Testing

```typescript
// keyboard-navigation.test.ts
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InvoiceForm } from '../InvoiceForm';

describe('Keyboard Navigation', () => {
  it('should navigate through form fields with Tab', async () => {
    const user = userEvent.setup();
    
    render(<InvoiceForm />);
    
    // Tab through form fields
    await user.tab();
    expect(screen.getByLabelText('Invoice Number')).toHaveFocus();
    
    await user.tab();
    expect(screen.getByLabelText('Issue Date')).toHaveFocus();
    
    await user.tab();
    expect(screen.getByLabelText('Company')).toHaveFocus();
  });

  it('should activate buttons with Enter and Space', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();
    
    render(<Button onClick={handleClick}>Test Button</Button>);
    
    const button = screen.getByRole('button');
    button.focus();
    
    // Test Enter key
    await user.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalledTimes(1);
    
    // Test Space key
    await user.keyboard(' ');
    expect(handleClick).toHaveBeenCalledTimes(2);
  });

  it('should close modal with Escape key', async () => {
    const user = userEvent.setup();
    const handleClose = jest.fn();
    
    render(
      <Modal isOpen onClose={handleClose}>
        <p>Modal content</p>
      </Modal>
    );
    
    await user.keyboard('{Escape}');
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
```

### Screen Reader Testing

```typescript
// screen-reader.test.ts
import { render, screen } from '@testing-library/react';
import { LiveRegion } from '../LiveRegion';
import { FormErrorAnnouncer } from '../FormErrorAnnouncer';

describe('Screen Reader Support', () => {
  it('should announce live region updates', () => {
    const { rerender } = render(
      <LiveRegion>Initial message</LiveRegion>
    );
    
    expect(screen.getByRole('status')).toHaveTextContent('Initial message');
    
    rerender(<LiveRegion>Updated message</LiveRegion>);
    expect(screen.getByRole('status')).toHaveTextContent('Updated message');
  });

  it('should announce form errors', () => {
    render(
      <FormErrorAnnouncer errors={['Email is required', 'Password is too short']} />
    );
    
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent('Email is required');
    expect(alert).toHaveTextContent('Password is too short');
  });

  it('should provide proper heading hierarchy', () => {
    render(
      <div>
        <h1>Main Title</h1>
        <h2>Section Title</h2>
        <h3>Subsection Title</h3>
      </div>
    );
    
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Main Title');
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Section Title');
    expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Subsection Title');
  });
});
```

## Performance Testing

### Bundle Size Testing

```typescript
// bundle-size.test.ts
import { analyzeBundle } from '../utils/bundleAnalyzer';

describe('Bundle Size Tests', () => {
  it('should not exceed size limits', async () => {
    const analysis = await analyzeBundle();
    
    // Individual component limits
    expect(analysis.components.Button.gzipped).toBeLessThan(5 * 1024); // 5KB
    expect(analysis.components.Input.gzipped).toBeLessThan(8 * 1024);  // 8KB
    expect(analysis.components.Table.gzipped).toBeLessThan(15 * 1024); // 15KB
    
    // Total bundle limit
    expect(analysis.total.gzipped).toBeLessThan(500 * 1024); // 500KB
  });

  it('should have proper tree shaking', async () => {
    const analysis = await analyzeBundle();
    
    // Unused exports should not be included
    expect(analysis.unusedExports).toHaveLength(0);
    
    // Dead code should be eliminated
    expect(analysis.deadCode).toHaveLength(0);
  });
});
```

### Runtime Performance Testing

```typescript
// performance.test.ts
import { render } from '@testing-library/react';
import { performance } from 'perf_hooks';
import { Table } from '../Table';
import { generateMockData } from '../utils/mockData';

describe('Runtime Performance', () => {
  it('should render large tables efficiently', () => {
    const data = generateMockData(1000); // 1000 rows
    
    const startTime = performance.now();
    render(<Table data={data} />);
    const endTime = performance.now();
    
    const renderTime = endTime - startTime;
    expect(renderTime).toBeLessThan(100); // 100ms limit
  });

  it('should handle frequent updates efficiently', () => {
    const { rerender } = render(<Table data={[]} />);
    
    const startTime = performance.now();
    
    // Simulate 100 updates
    for (let i = 0; i < 100; i++) {
      const data = generateMockData(i + 1);
      rerender(<Table data={data} />);
    }
    
    const endTime = performance.now();
    const totalTime = endTime - startTime;
    
    expect(totalTime).toBeLessThan(1000); // 1 second limit
  });
});
```

## Polish Business Logic Testing

### NIP Validation Testing

```typescript
// nip-validation.test.ts
import { validateNIP, formatNIP } from '../utils/nipValidation';

describe('NIP Validation', () => {
  describe('Format Validation', () => {
    it('should accept valid NIP formats', () => {
      const validNIPs = [
        '1234567890',
        '123-456-78-90',
        '123 456 78 90',
        '123-456-789-0'
      ];
      
      validNIPs.forEach(nip => {
        expect(validateNIP(nip).isValid).toBe(true);
      });
    });

    it('should reject invalid NIP formats', () => {
      const invalidNIPs = [
        '123',
        '12345678901', // Too long
        'abcdefghij',  // Letters
        '123-45-678',  // Wrong format
        ''             // Empty
      ];
      
      invalidNIPs.forEach(nip => {
        expect(validateNIP(nip).isValid).toBe(false);
      });
    });
  });

  describe('Checksum Validation', () => {
    it('should validate correct checksums', () => {
      const validNIPs = [
        '5260001246', // Real NIP with valid checksum
        '7010001454',
        '9542205814'
      ];
      
      validNIPs.forEach(nip => {
        const result = validateNIP(nip);
        expect(result.isValid).toBe(true);
        expect(result.message).toBe('');
      });
    });

    it('should reject incorrect checksums', () => {
      const invalidNIPs = [
        '5260001247', // Wrong checksum
        '7010001455',
        '9542205815'
      ];
      
      invalidNIPs.forEach(nip => {
        const result = validateNIP(nip);
        expect(result.isValid).toBe(false);
        expect(result.message).toContain('suma kontrolna');
      });
    });
  });

  describe('NIP Formatting', () => {
    it('should format NIP correctly', () => {
      expect(formatNIP('1234567890')).toBe('123-456-78-90');
      expect(formatNIP('123 456 78 90')).toBe('123-456-78-90');
      expect(formatNIP('123-456-78-90')).toBe('123-456-78-90');
    });

    it('should handle invalid input gracefully', () => {
      expect(formatNIP('123')).toBe('123');
      expect(formatNIP('')).toBe('');
      expect(formatNIP('abc')).toBe('abc');
    });
  });
});
```

### VAT Calculation Testing

```typescript
// vat-calculation.test.ts
import { calculateVAT, POLISH_VAT_RATES } from '../utils/vatCalculation';

describe('VAT Calculation', () => {
  describe('Standard Rates', () => {
    it('should calculate 23% VAT correctly', () => {
      const result = calculateVAT(100, 23);
      
      expect(result.net).toBe(100);
      expect(result.vat).toBe(23);
      expect(result.gross).toBe(123);
    });

    it('should calculate 8% VAT correctly', () => {
      const result = calculateVAT(100, 8);
      
      expect(result.net).toBe(100);
      expect(result.vat).toBe(8);
      expect(result.gross).toBe(108);
    });

    it('should calculate 5% VAT correctly', () => {
      const result = calculateVAT(100, 5);
      
      expect(result.net).toBe(100);
      expect(result.vat).toBe(5);
      expect(result.gross).toBe(105);
    });

    it('should handle 0% VAT', () => {
      const result = calculateVAT(100, 0);
      
      expect(result.net).toBe(100);
      expect(result.vat).toBe(0);
      expect(result.gross).toBe(100);
    });
  });

  describe('Rounding', () => {
    it('should round to 2 decimal places', () => {
      const result = calculateVAT(33.33, 23);
      
      expect(result.net).toBe(33.33);
      expect(result.vat).toBe(7.67); // Rounded from 7.6659
      expect(result.gross).toBe(41.00);
    });

    it('should handle rounding edge cases', () => {
      const result = calculateVAT(0.01, 23);
      
      expect(result.net).toBe(0.01);
      expect(result.vat).toBe(0.00); // Rounded from 0.0023
      expect(result.gross).toBe(0.01);
    });
  });

  describe('Polish VAT Rates Validation', () => {
    it('should accept valid Polish VAT rates', () => {
      POLISH_VAT_RATES.forEach(rate => {
        expect(() => calculateVAT(100, rate)).not.toThrow();
      });
    });

    it('should reject invalid VAT rates', () => {
      const invalidRates = [10, 15, 25, -5, 100];
      
      invalidRates.forEach(rate => {
        expect(() => calculateVAT(100, rate)).toThrow();
      });
    });
  });
});
```

### Currency Formatting Testing

```typescript
// currency-formatting.test.ts
import { formatPolishCurrency, parsePolishCurrency } from '../utils/currencyFormatting';

describe('Polish Currency Formatting', () => {
  describe('Formatting', () => {
    it('should format currency with proper separators', () => {
      expect(formatPolishCurrency(1234.56)).toBe('1 234,56 zł');
      expect(formatPolishCurrency(1000000.99)).toBe('1 000 000,99 zł');
      expect(formatPolishCurrency(0)).toBe('0,00 zł');
    });

    it('should handle negative amounts', () => {
      expect(formatPolishCurrency(-1234.56)).toBe('-1 234,56 zł');
    });

    it('should handle very small amounts', () => {
      expect(formatPolishCurrency(0.01)).toBe('0,01 zł');
      expect(formatPolishCurrency(0.001)).toBe('0,00 zł'); // Rounded
    });
  });

  describe('Parsing', () => {
    it('should parse Polish currency format', () => {
      expect(parsePolishCurrency('1 234,56 zł')).toBe(1234.56);
      expect(parsePolishCurrency('1 000 000,99 zł')).toBe(1000000.99);
      expect(parsePolishCurrency('0,00 zł')).toBe(0);
    });

    it('should handle various input formats', () => {
      expect(parsePolishCurrency('1234,56')).toBe(1234.56);
      expect(parsePolishCurrency('1 234,56')).toBe(1234.56);
      expect(parsePolishCurrency('1234.56')).toBe(1234.56); // Fallback
    });

    it('should handle invalid input gracefully', () => {
      expect(parsePolishCurrency('invalid')).toBeNaN();
      expect(parsePolishCurrency('')).toBe(0);
    });
  });
});
```

## End-to-End Testing

### E2E Test Setup

```typescript
// e2e/invoice-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Invoice Management Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to invoices
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="login-button"]');
    await page.waitForURL('/dashboard');
  });

  test('complete invoice creation workflow', async ({ page }) => {
    // Navigate to invoice creation
    await page.click('[data-testid="create-invoice"]');
    await page.waitForURL('/invoices/new');

    // Fill invoice details
    await page.fill('[data-testid="invoice-number"]', 'FV/2024/01/001');
    await page.selectOption('[data-testid="company-select"]', '1');
    await page.selectOption('[data-testid="contractor-select"]', '1');

    // Add invoice item
    await page.fill('[data-testid="item-name-0"]', 'Programming Services');
    await page.fill('[data-testid="item-quantity-0"]', '10');
    await page.fill('[data-testid="item-price-0"]', '100,00');

    // Verify calculations
    await expect(page.locator('[data-testid="net-total"]')).toHaveText('1 000,00 zł');
    await expect(page.locator('[data-testid="vat-total"]')).toHaveText('230,00 zł');
    await expect(page.locator('[data-testid="gross-total"]')).toHaveText('1 230,00 zł');

    // Submit invoice
    await page.click('[data-testid="submit-invoice"]');
    await page.waitForURL('/invoices/1');

    // Verify invoice was created
    await expect(page.locator('[data-testid="invoice-number"]')).toHaveText('FV/2024/01/001');
    await expect(page.locator('[data-testid="invoice-status"]')).toHaveText('Draft');
  });

  test('invoice validation workflow', async ({ page }) => {
    await page.goto('/invoices/new');

    // Try to submit without required fields
    await page.click('[data-testid="submit-invoice"]');

    // Verify validation errors
    await expect(page.locator('[data-testid="error-invoice-number"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-company"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-contractor"]')).toBeVisible();

    // Fill required fields and verify errors disappear
    await page.fill('[data-testid="invoice-number"]', 'FV/2024/01/001');
    await expect(page.locator('[data-testid="error-invoice-number"]')).not.toBeVisible();
  });

  test('NIP validation in contractor form', async ({ page }) => {
    await page.goto('/contractors/new');

    // Enter invalid NIP
    await page.fill('[data-testid="contractor-nip"]', '1234567891');
    await page.blur('[data-testid="contractor-nip"]');

    // Verify validation error
    await expect(page.locator('[data-testid="nip-error"]')).toHaveText('Nieprawidłowa suma kontrolna NIP');

    // Enter valid NIP
    await page.fill('[data-testid="contractor-nip"]', '5260001246');
    await page.blur('[data-testid="contractor-nip"]');

    // Verify validation passes
    await expect(page.locator('[data-testid="nip-error"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="nip-success"]')).toBeVisible();
  });
});
```

## Quality Gates

### Pre-commit Quality Gates

```bash
#!/bin/bash
# .husky/pre-commit

echo "Running pre-commit quality checks..."

# 1. Lint check
echo "Checking code style..."
npm run lint
if [ $? -ne 0 ]; then
  echo "❌ Linting failed"
  exit 1
fi

# 2. Type check
echo "Checking TypeScript types..."
npm run type-check
if [ $? -ne 0 ]; then
  echo "❌ Type checking failed"
  exit 1
fi

# 3. Unit tests
echo "Running unit tests..."
npm run test:unit
if [ $? -ne 0 ]; then
  echo "❌ Unit tests failed"
  exit 1
fi

# 4. Build check
echo "Checking build..."
npm run build
if [ $? -ne 0 ]; then
  echo "❌ Build failed"
  exit 1
fi

echo "✅ All pre-commit checks passed"
```

### Pull Request Quality Gates

```yaml
# .github/workflows/pr-checks.yml
name: Pull Request Checks

on:
  pull_request:
    branches: [main, develop]

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Lint check
        run: npm run lint
      
      - name: Type check
        run: npm run type-check
      
      - name: Unit tests
        run: npm run test:unit -- --coverage
      
      - name: Integration tests
        run: npm run test:integration
      
      - name: Accessibility tests
        run: npm run test:a11y
      
      - name: Visual regression tests
        run: npm run test:visual
      
      - name: Performance tests
        run: npm run test:performance
      
      - name: Build check
        run: npm run build
      
      - name: Bundle size check
        run: npm run analyze:bundle
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
```

### Release Quality Gates

```typescript
// scripts/release-quality-check.ts
import { execSync } from 'child_process';
import { readFileSync } from 'fs';

interface QualityMetrics {
  coverage: number;
  bundleSize: number;
  performanceScore: number;
  accessibilityScore: number;
  visualRegressions: number;
}

const QUALITY_THRESHOLDS = {
  coverage: 90,
  bundleSize: 500 * 1024, // 500KB
  performanceScore: 90,
  accessibilityScore: 100,
  visualRegressions: 0
};

async function checkQualityGates(): Promise<boolean> {
  console.log('🔍 Running release quality checks...');
  
  try {
    // 1. Check test coverage
    const coverage = getCoveragePercentage();
    console.log(`📊 Test coverage: ${coverage}%`);
    
    if (coverage < QUALITY_THRESHOLDS.coverage) {
      console.error(`❌ Coverage below threshold: ${coverage}% < ${QUALITY_THRESHOLDS.coverage}%`);
      return false;
    }
    
    // 2. Check bundle size
    const bundleSize = getBundleSize();
    console.log(`📦 Bundle size: ${(bundleSize / 1024).toFixed(2)}KB`);
    
    if (bundleSize > QUALITY_THRESHOLDS.bundleSize) {
      console.error(`❌ Bundle size exceeds threshold: ${bundleSize} > ${QUALITY_THRESHOLDS.bundleSize}`);
      return false;
    }
    
    // 3. Check performance score
    const performanceScore = getPerformanceScore();
    console.log(`⚡ Performance score: ${performanceScore}`);
    
    if (performanceScore < QUALITY_THRESHOLDS.performanceScore) {
      console.error(`❌ Performance below threshold: ${performanceScore} < ${QUALITY_THRESHOLDS.performanceScore}`);
      return false;
    }
    
    // 4. Check accessibility score
    const accessibilityScore = getAccessibilityScore();
    console.log(`♿ Accessibility score: ${accessibilityScore}`);
    
    if (accessibilityScore < QUALITY_THRESHOLDS.accessibilityScore) {
      console.error(`❌ Accessibility below threshold: ${accessibilityScore} < ${QUALITY_THRESHOLDS.accessibilityScore}`);
      return false;
    }
    
    // 5. Check visual regressions
    const visualRegressions = getVisualRegressions();
    console.log(`👁️ Visual regressions: ${visualRegressions}`);
    
    if (visualRegressions > QUALITY_THRESHOLDS.visualRegressions) {
      console.error(`❌ Visual regressions detected: ${visualRegressions}`);
      return false;
    }
    
    console.log('✅ All quality gates passed!');
    return true;
    
  } catch (error) {
    console.error('❌ Quality check failed:', error);
    return false;
  }
}

function getCoveragePercentage(): number {
  const coverageReport = JSON.parse(
    readFileSync('./coverage/coverage-summary.json', 'utf8')
  );
  return coverageReport.total.lines.pct;
}

function getBundleSize(): number {
  const bundleStats = JSON.parse(
    readFileSync('./dist/bundle-stats.json', 'utf8')
  );
  return bundleStats.assets
    .filter((asset: any) => asset.name.endsWith('.js'))
    .reduce((total: number, asset: any) => total + asset.size, 0);
}

function getPerformanceScore(): number {
  const lighthouseReport = JSON.parse(
    readFileSync('./lighthouse-report.json', 'utf8')
  );
  return lighthouseReport.categories.performance.score * 100;
}

function getAccessibilityScore(): number {
  const axeReport = JSON.parse(
    readFileSync('./axe-report.json', 'utf8')
  );
  return axeReport.violations.length === 0 ? 100 : 0;
}

function getVisualRegressions(): number {
  const playwrightReport = JSON.parse(
    readFileSync('./playwright-report.json', 'utf8')
  );
  return playwrightReport.suites
    .flatMap((suite: any) => suite.specs)
    .filter((spec: any) => spec.tests.some((test: any) => test.status === 'failed'))
    .length;
}

// Run quality checks
checkQualityGates().then(passed => {
  process.exit(passed ? 0 : 1);
});
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18, 20]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linting
        run: npm run lint
      
      - name: Run type checking
        run: npm run type-check
      
      - name: Run unit tests
        run: npm run test:unit -- --coverage --watchAll=false
      
      - name: Run integration tests
        run: npm run test:integration
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          flags: unittests
          name: codecov-umbrella
  
  accessibility:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build Storybook
        run: npm run build-storybook
      
      - name: Run accessibility tests
        run: npm run test:a11y
      
      - name: Upload accessibility report
        uses: actions/upload-artifact@v3
        with:
          name: accessibility-report
          path: ./accessibility-report.html
  
  visual:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Build Storybook
        run: npm run build-storybook
      
      - name: Run visual regression tests
        run: npm run test:visual
      
      - name: Upload visual test results
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: visual-test-results
          path: test-results/
  
  performance:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run build
      
      - name: Run performance tests
        run: npm run test:performance
      
      - name: Analyze bundle size
        run: npm run analyze:bundle
      
      - name: Upload performance report
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: ./performance-report.json

  polish-business:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run Polish business logic tests
        run: npm run test:polish-business
      
      - name: Validate NIP/REGON algorithms
        run: npm run validate:polish-validation
      
      - name: Test VAT calculations
        run: npm run test:vat-calculations
      
      - name: Verify currency formatting
        run: npm run test:currency-formatting
```

This comprehensive testing documentation ensures that the FaktuLove Design System maintains high quality standards while supporting Polish business requirements and accessibility compliance.