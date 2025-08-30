# Getting Started with FaktuLove Design System

This guide will help you get up and running with the FaktuLove Design System in your React application.

## 📋 Prerequisites

- React 18.0 or higher
- TypeScript 4.5 or higher (recommended)
- Node.js 16 or higher

## 🚀 Installation

### NPM
```bash
npm install @faktulove/design-system
```

### Yarn
```bash
yarn add @faktulove/design-system
```

### Peer Dependencies
The design system requires these peer dependencies:
```bash
npm install react react-dom
```

## 🎨 Setup Styles

### Import Base Styles
Add the design system styles to your application:

```tsx
// In your main App.tsx or index.tsx
import '@faktulove/design-system/styles';
```

### With CSS Modules
If you're using CSS modules, import the styles differently:

```tsx
import '@faktulove/design-system/styles/index.css';
```

### Tailwind CSS Integration
If you're using Tailwind CSS, extend your configuration:

```js
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './node_modules/@faktulove/design-system/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      // Design system tokens will be automatically included
    },
  },
  plugins: [],
};
```

## 🧩 Basic Usage

### Import Components
```tsx
import React from 'react';
import { Button, Input, Card } from '@faktulove/design-system';

function MyComponent() {
  return (
    <Card>
      <Card.Header>
        <h2>Welcome to FaktuLove</h2>
      </Card.Header>
      <Card.Body>
        <Input 
          placeholder="Enter your name"
          aria-label="Name input"
        />
        <Button variant="primary">
          Submit
        </Button>
      </Card.Body>
    </Card>
  );
}
```

### Tree Shaking
Import only the components you need for optimal bundle size:

```tsx
// ✅ Good - tree shaking friendly
import { Button } from '@faktulove/design-system';

// ❌ Avoid - imports entire library
import * as DS from '@faktulove/design-system';
```

## 🎭 Theme Setup

### Basic Theme Provider
Wrap your application with the ThemeProvider:

```tsx
import React from 'react';
import { ThemeProvider } from '@faktulove/design-system';
import App from './App';

function Root() {
  return (
    <ThemeProvider theme="light">
      <App />
    </ThemeProvider>
  );
}

export default Root;
```

### Dynamic Theme Switching
```tsx
import React, { useState } from 'react';
import { ThemeProvider, Button } from '@faktulove/design-system';

function App() {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeProvider theme={theme}>
      <div>
        <Button onClick={toggleTheme}>
          Switch to {theme === 'light' ? 'dark' : 'light'} theme
        </Button>
        {/* Your app content */}
      </div>
    </ThemeProvider>
  );
}
```

### Theme Persistence
```tsx
import React from 'react';
import { ThemeProvider, useThemeStorage } from '@faktulove/design-system';

function App() {
  const { theme, setTheme } = useThemeStorage();

  return (
    <ThemeProvider theme={theme}>
      {/* Theme will be automatically persisted */}
    </ThemeProvider>
  );
}
```

## 🌍 Polish Business Components

### Currency Input
```tsx
import { CurrencyInput } from '@faktulove/design-system';

function InvoiceForm() {
  const [amount, setAmount] = useState('');

  return (
    <CurrencyInput
      currency="PLN"
      value={amount}
      onChange={setAmount}
      placeholder="Wprowadź kwotę"
      aria-label="Kwota faktury"
    />
  );
}
```

### NIP Validator
```tsx
import { NIPValidator } from '@faktulove/design-system';

function ClientForm() {
  const [nip, setNip] = useState('');
  const [isValid, setIsValid] = useState(false);

  return (
    <NIPValidator
      value={nip}
      onChange={setNip}
      onValidationChange={setIsValid}
      placeholder="Wprowadź NIP"
      aria-label="Numer NIP klienta"
    />
  );
}
```

### VAT Rate Selector
```tsx
import { VATRateSelector } from '@faktulove/design-system';

function ProductForm() {
  const [vatRate, setVatRate] = useState('23');

  return (
    <VATRateSelector
      value={vatRate}
      onChange={setVatRate}
      aria-label="Stawka VAT"
    />
  );
}
```

## 📱 Responsive Design

### Responsive Grid
```tsx
import { Grid, Card } from '@faktulove/design-system';

function Dashboard() {
  return (
    <Grid 
      cols={{ base: 1, md: 2, lg: 3 }}
      gap={4}
    >
      <Card>
        <Card.Body>Mobile: 1 column</Card.Body>
      </Card>
      <Card>
        <Card.Body>Tablet: 2 columns</Card.Body>
      </Card>
      <Card>
        <Card.Body>Desktop: 3 columns</Card.Body>
      </Card>
    </Grid>
  );
}
```

### Responsive Utilities
```tsx
import { useBreakpoint } from '@faktulove/design-system';

function ResponsiveComponent() {
  const { isMobile, isTablet, isDesktop } = useBreakpoint();

  return (
    <div>
      {isMobile && <div>Mobile view</div>}
      {isTablet && <div>Tablet view</div>}
      {isDesktop && <div>Desktop view</div>}
    </div>
  );
}
```

## ♿ Accessibility Setup

### Basic Accessibility
All components come with built-in accessibility features:

```tsx
import { Button, Input } from '@faktulove/design-system';

function AccessibleForm() {
  return (
    <form>
      <Input
        aria-label="Email address"
        type="email"
        required
        aria-describedby="email-help"
      />
      <div id="email-help">
        We'll never share your email with anyone else.
      </div>
      
      <Button type="submit" aria-describedby="submit-help">
        Submit Form
      </Button>
      <div id="submit-help">
        Click to submit the form
      </div>
    </form>
  );
}
```

### Focus Management
```tsx
import { useFocusManagement } from '@faktulove/design-system';

function Modal({ isOpen, onClose }) {
  const { focusRef, restoreFocus } = useFocusManagement();

  useEffect(() => {
    if (isOpen) {
      focusRef.current?.focus();
    } else {
      restoreFocus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div role="dialog" aria-modal="true">
      <button ref={focusRef} onClick={onClose}>
        Close Modal
      </button>
      {/* Modal content */}
    </div>
  );
}
```

## 🧪 Testing Setup

### Test Utilities
```tsx
import { render } from '@testing-library/react';
import { renderWithA11y, testPolishA11y } from '@faktulove/design-system/testing';
import { Button } from '@faktulove/design-system';

test('button is accessible', async () => {
  const { container } = renderWithA11y(
    <Button>Test Button</Button>
  );
  
  await testPolishA11y(container);
});
```

### Jest Configuration
Add to your `jest.config.js`:

```js
module.exports = {
  setupFilesAfterEnv: [
    '@testing-library/jest-dom',
    '@faktulove/design-system/testing/setup',
  ],
  moduleNameMapping: {
    '^@faktulove/design-system/(.*)$': '<rootDir>/node_modules/@faktulove/design-system/$1',
  },
};
```

## 🔧 TypeScript Configuration

### Type Definitions
The design system includes comprehensive TypeScript definitions:

```tsx
import type { 
  ButtonProps, 
  InputProps, 
  Theme 
} from '@faktulove/design-system';

interface MyComponentProps {
  primaryButton: ButtonProps;
  emailInput: InputProps;
  theme: Theme;
}
```

### Custom Theme Types
```tsx
import type { Theme } from '@faktulove/design-system';

interface CustomTheme extends Theme {
  customColors: {
    brand: string;
    accent: string;
  };
}
```

## 🎨 Customization

### CSS Custom Properties
Override design tokens using CSS custom properties:

```css
:root {
  --ds-color-primary-600: #your-brand-color;
  --ds-font-family-sans: 'Your Font', sans-serif;
  --ds-spacing-4: 1.5rem; /* Override 16px default */
}
```

### Component Styling
```tsx
import { Button } from '@faktulove/design-system';

function CustomButton() {
  return (
    <Button 
      className="custom-button"
      style={{ 
        '--ds-button-bg': '#custom-color' 
      }}
    >
      Custom Styled Button
    </Button>
  );
}
```

## 📦 Bundle Optimization

### Code Splitting
```tsx
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const Table = lazy(() => import('@faktulove/design-system').then(m => ({ default: m.Table })));

function DataView() {
  return (
    <Suspense fallback={<div>Loading table...</div>}>
      <Table data={data} columns={columns} />
    </Suspense>
  );
}
```

### Webpack Configuration
```js
// webpack.config.js
module.exports = {
  resolve: {
    alias: {
      '@faktulove/design-system': path.resolve(__dirname, 'node_modules/@faktulove/design-system'),
    },
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        designSystem: {
          test: /[\\/]node_modules[\\/]@faktulove[\\/]design-system[\\/]/,
          name: 'design-system',
          chunks: 'all',
        },
      },
    },
  },
};
```

## 🚨 Common Issues

### Styles Not Loading
```tsx
// ❌ Missing style import
import { Button } from '@faktulove/design-system';

// ✅ Include styles
import '@faktulove/design-system/styles';
import { Button } from '@faktulove/design-system';
```

### TypeScript Errors
```tsx
// ❌ Missing type imports
const button: ButtonProps = { variant: 'primary' };

// ✅ Import types
import type { ButtonProps } from '@faktulove/design-system';
const button: ButtonProps = { variant: 'primary' };
```

### Theme Not Applied
```tsx
// ❌ Missing ThemeProvider
function App() {
  return <Button>No theme</Button>;
}

// ✅ Wrap with ThemeProvider
function App() {
  return (
    <ThemeProvider theme="light">
      <Button>Themed button</Button>
    </ThemeProvider>
  );
}
```

## 📚 Next Steps

1. **Explore Components**: Check out the [Component Documentation](./components/README.md)
2. **Learn Design Tokens**: Read about [Design Tokens](./design-tokens.md)
3. **Accessibility Guide**: Review [Accessibility Guidelines](./accessibility.md)
4. **Polish Business Features**: Explore [Polish Business Components](./polish-business.md)
5. **Migration Guide**: If migrating, see [Migration Guide](./migration-guide.md)

## 🆘 Getting Help

- **Documentation**: Browse the complete documentation
- **Storybook**: Interactive component examples at `http://localhost:6006`
- **GitHub Issues**: Report bugs or request features
- **Community**: Join discussions and get help from other developers

---

Ready to build amazing Polish business applications! 🚀