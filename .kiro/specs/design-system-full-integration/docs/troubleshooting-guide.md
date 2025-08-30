# Troubleshooting Guide

This guide provides solutions to common issues encountered during design system migration and integration.

## Table of Contents

1. [Component Migration Issues](#component-migration-issues)
2. [Styling Conflicts](#styling-conflicts)
3. [Performance Problems](#performance-problems)
4. [Polish Business Logic Issues](#polish-business-logic-issues)
5. [Testing Problems](#testing-problems)
6. [Build and Bundle Issues](#build-and-bundle-issues)
7. [Accessibility Issues](#accessibility-issues)
8. [Browser Compatibility](#browser-compatibility)

## Component Migration Issues

### Issue: Component Not Rendering

**Symptoms:**
- Component appears blank or doesn't render
- Console shows no errors
- Props seem correct

**Possible Causes:**
1. Missing design system provider
2. Incorrect import path
3. Missing required props
4. Theme not loaded

**Solutions:**

```jsx
// 1. Ensure ThemeProvider is wrapping your app
import { ThemeProvider } from '@design-system/theme';

function App() {
  return (
    <ThemeProvider theme="polish-business">
      <YourComponent />
    </ThemeProvider>
  );
}

// 2. Check import paths
// ❌ Incorrect
import { Button } from '@design-system';

// ✅ Correct
import { Button } from '@design-system/primitives';

// 3. Provide required props
// ❌ Missing required props
<Input onChange={handleChange} />

// ✅ With required props
<Input 
  label="Required label"
  value={value}
  onChange={handleChange} 
/>
```

### Issue: Props Not Working as Expected

**Symptoms:**
- Component renders but props don't take effect
- Styling doesn't match expected design
- Event handlers not firing

**Possible Causes:**
1. Prop name mismatch from legacy components
2. Incorrect prop type
3. Props being overridden by CSS

**Solutions:**

```jsx
// Check prop mapping
// ❌ Legacy prop names
<Button className="btn-primary" size="large" />

// ✅ Design system prop names
<Button variant="primary" size="lg" />

// Check prop types
// ❌ Incorrect type
<Input maxLength="100" />

// ✅ Correct type
<Input maxLength={100} />

// Check event handler format
// ❌ Legacy event handler
<Input onChange={(e) => setValue(e.target.value)} />

// ✅ Design system event handler
<Input onChange={(value) => setValue(value)} />
```

### Issue: Component Styling Broken

**Symptoms:**
- Component appears unstyled
- Partial styling applied
- Layout broken

**Possible Causes:**
1. CSS not loaded
2. CSS order conflicts
3. Missing design tokens

**Solutions:**

```jsx
// 1. Ensure CSS is imported
import '@design-system/styles/index.css';

// 2. Check CSS loading order in your build
// Design system CSS should load before custom CSS

// 3. Verify design tokens are available
// Check if CSS custom properties are defined
const element = document.documentElement;
const tokenValue = getComputedStyle(element)
  .getPropertyValue('--ds-color-primary-500');

if (!tokenValue) {
  console.error('Design tokens not loaded');
}
```

## Styling Conflicts

### Issue: Bootstrap CSS Conflicts

**Symptoms:**
- Design system components look wrong
- Inconsistent styling across components
- CSS specificity issues

**Solutions:**

```css
/* 1. Scope Bootstrap to specific areas */
.legacy-content {
  /* Bootstrap styles only apply here */
}

/* 2. Use CSS layers for proper ordering */
@layer bootstrap, design-system, custom;

@layer bootstrap {
  /* Bootstrap CSS */
}

@layer design-system {
  /* Design system CSS */
}

/* 3. Reset conflicting Bootstrap styles */
.ds-component {
  /* Reset Bootstrap button styles */
  border: none;
  background: none;
  padding: 0;
  margin: 0;
}
```

### Issue: Custom CSS Overriding Design System

**Symptoms:**
- Design system components don't match design
- Inconsistent appearance
- Styles not updating with theme changes

**Solutions:**

```css
/* ❌ Avoid using !important */
.custom-button {
  background-color: red !important;
}

/* ✅ Use design system theming */
.custom-button {
  --ds-button-bg-primary: var(--ds-color-red-500);
}

/* ✅ Use CSS custom properties */
.invoice-form {
  --ds-input-border-color: var(--ds-color-blue-300);
  --ds-button-padding: var(--ds-space-3) var(--ds-space-6);
}

/* ✅ Use component variants */
/* Define in theme configuration */
const customTheme = {
  components: {
    Button: {
      variants: {
        invoice: {
          backgroundColor: 'var(--ds-color-blue-500)',
          color: 'white'
        }
      }
    }
  }
};
```

### Issue: Responsive Styles Not Working

**Symptoms:**
- Components don't adapt to screen size
- Mobile layout broken
- Responsive props not working

**Solutions:**

```jsx
// ✅ Use responsive arrays
<Grid 
  cols={[1, 2, 3]} // 1 col mobile, 2 tablet, 3 desktop
  gap={["sm", "md", "lg"]} // Responsive gap
/>

<Text 
  variant={["body-sm", "body-md", "body-lg"]} // Responsive typography
/>

// ✅ Use responsive utilities
<Box 
  display={["none", "block"]} // Hidden on mobile
  padding={["sm", "md"]} // Responsive padding
/>
```

## Performance Problems

### Issue: Slow Component Rendering

**Symptoms:**
- Components take time to appear
- Laggy interactions
- High CPU usage

**Solutions:**

```jsx
// 1. Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  return <ComplexVisualization data={data} />;
}, (prevProps, nextProps) => {
  return prevProps.data.id === nextProps.data.id;
});

// 2. Implement lazy loading
const LazyChart = lazy(() => import('@design-system/patterns/Chart'));

function Dashboard() {
  return (
    <Suspense fallback={<Spinner />}>
      <LazyChart data={chartData} />
    </Suspense>
  );
}

// 3. Optimize re-renders with useMemo
const MemoizedInvoiceList = ({ invoices, filters }) => {
  const filteredInvoices = useMemo(() => {
    return invoices.filter(invoice => 
      filters.every(filter => filter(invoice))
    );
  }, [invoices, filters]);

  return <InvoiceTable data={filteredInvoices} />;
};
```

### Issue: Large Bundle Size

**Symptoms:**
- Slow initial page load
- Large JavaScript bundles
- Poor performance metrics

**Solutions:**

```jsx
// 1. Use tree shaking - import only what you need
// ❌ Imports entire library
import * as DS from '@design-system/components';

// ✅ Import specific components
import { Button } from '@design-system/primitives/Button';
import { Input } from '@design-system/primitives/Input';

// 2. Use dynamic imports for large components
const ChartComponent = lazy(() => 
  import('@design-system/patterns/Chart')
);

// 3. Configure webpack for better tree shaking
// webpack.config.js
module.exports = {
  optimization: {
    usedExports: true,
    sideEffects: false
  }
};
```

### Issue: Memory Leaks

**Symptoms:**
- Increasing memory usage over time
- Browser becomes sluggish
- Components not unmounting properly

**Solutions:**

```jsx
// 1. Clean up event listeners
useEffect(() => {
  const handleResize = () => {
    // Handle resize
  };

  window.addEventListener('resize', handleResize);
  
  return () => {
    window.removeEventListener('resize', handleResize);
  };
}, []);

// 2. Cancel async operations
useEffect(() => {
  let cancelled = false;

  const fetchData = async () => {
    const result = await api.getData();
    if (!cancelled) {
      setData(result);
    }
  };

  fetchData();

  return () => {
    cancelled = true;
  };
}, []);

// 3. Use AbortController for fetch requests
useEffect(() => {
  const controller = new AbortController();

  fetch('/api/data', { signal: controller.signal })
    .then(response => response.json())
    .then(data => setData(data))
    .catch(error => {
      if (error.name !== 'AbortError') {
        console.error('Fetch error:', error);
      }
    });

  return () => {
    controller.abort();
  };
}, []);
```

## Polish Business Logic Issues

### Issue: NIP Validation Not Working

**Symptoms:**
- Valid NIPs marked as invalid
- Invalid NIPs passing validation
- Incorrect error messages

**Solutions:**

```jsx
// 1. Check NIP format
const validateNIPFormat = (nip) => {
  // Remove spaces and dashes
  const cleanNIP = nip.replace(/[\s-]/g, '');
  
  // Must be exactly 10 digits
  if (!/^\d{10}$/.test(cleanNIP)) {
    return false;
  }
  
  return true;
};

// 2. Implement proper checksum validation
const validateNIPChecksum = (nip) => {
  const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
  const digits = nip.split('').map(Number);
  
  const sum = digits.slice(0, 9).reduce((acc, digit, index) => {
    return acc + (digit * weights[index]);
  }, 0);
  
  const checksum = sum % 11;
  const expectedChecksum = checksum === 10 ? 0 : checksum;
  
  return digits[9] === expectedChecksum;
};

// 3. Use the design system NIP validator
<NIPValidator
  label="NIP firmy"
  value={nip}
  onChange={setNip}
  validation={{
    format: true,
    checksum: true,
    required: true
  }}
  onValidation={(isValid, message) => {
    if (!isValid) {
      setError(message);
    }
  }}
/>
```

### Issue: VAT Calculations Incorrect

**Symptoms:**
- Wrong VAT amounts calculated
- Rounding errors
- Incorrect total amounts

**Solutions:**

```jsx
// 1. Use proper decimal arithmetic
import { Decimal } from 'decimal.js';

const calculateVAT = (netAmount, vatRate) => {
  const net = new Decimal(netAmount);
  const rate = new Decimal(vatRate).div(100);
  const vatAmount = net.mul(rate);
  const grossAmount = net.add(vatAmount);
  
  return {
    net: net.toFixed(2),
    vat: vatAmount.toFixed(2),
    gross: grossAmount.toFixed(2)
  };
};

// 2. Use the design system VAT calculator
import { VATCalculator } from '@design-system/business';

<VATCalculator
  netAmount={netAmount}
  vatRate={vatRate}
  onCalculation={(result) => {
    setVATAmount(result.vat);
    setGrossAmount(result.gross);
  }}
  precision={2}
  roundingMode="half-up"
/>
```

### Issue: Date Formatting Problems

**Symptoms:**
- Dates display in wrong format
- Locale not applied correctly
- Date parsing errors

**Solutions:**

```jsx
// 1. Use proper Polish date formatting
const formatPolishDate = (date) => {
  return new Intl.DateTimeFormat('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(date);
};

// 2. Use the design system date picker
<DatePicker
  label="Data wystawienia"
  value={date}
  onChange={setDate}
  format="DD.MM.YYYY"
  locale="pl"
  parseFormat={['DD.MM.YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD']}
/>

// 3. Handle different date input formats
const parsePolishDate = (dateString) => {
  const formats = [
    /^(\d{2})\.(\d{2})\.(\d{4})$/, // DD.MM.YYYY
    /^(\d{2})\/(\d{2})\/(\d{4})$/, // DD/MM/YYYY
    /^(\d{4})-(\d{2})-(\d{2})$/    // YYYY-MM-DD
  ];
  
  for (const format of formats) {
    const match = dateString.match(format);
    if (match) {
      const [, day, month, year] = match;
      return new Date(year, month - 1, day);
    }
  }
  
  throw new Error('Invalid date format');
};
```

### Issue: Currency Formatting Problems

**Symptoms:**
- Wrong decimal separator
- Incorrect thousand separators
- Currency symbol placement wrong

**Solutions:**

```jsx
// 1. Use proper Polish currency formatting
const formatPolishCurrency = (amount) => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

// 2. Use the design system currency input
<CurrencyInput
  label="Kwota"
  value={amount}
  onChange={setAmount}
  currency="PLN"
  locale="pl-PL"
  thousandSeparator=" "
  decimalSeparator=","
  precision={2}
/>

// 3. Handle currency parsing
const parsePolishCurrency = (currencyString) => {
  // Remove currency symbol and spaces
  const cleaned = currencyString
    .replace(/PLN/g, '')
    .replace(/\s/g, '')
    .replace(/,/g, '.');
  
  return parseFloat(cleaned);
};
```

## Testing Problems

### Issue: Tests Failing After Migration

**Symptoms:**
- Existing tests break
- New components not found in tests
- Different DOM structure

**Solutions:**

```jsx
// 1. Update test selectors
// ❌ Old selectors
const button = screen.getByClassName('btn-primary');

// ✅ New selectors
const button = screen.getByRole('button', { name: /zapisz/i });
// or
const button = screen.getByTestId('save-button');

// 2. Mock design system components in tests
jest.mock('@design-system/primitives/Button', () => {
  return function MockButton({ children, ...props }) {
    return <button {...props}>{children}</button>;
  };
});

// 3. Provide theme context in tests
const renderWithTheme = (component) => {
  return render(
    <ThemeProvider theme="polish-business">
      {component}
    </ThemeProvider>
  );
};

test('renders invoice form', () => {
  renderWithTheme(<InvoiceForm />);
  expect(screen.getByLabelText('Numer faktury')).toBeInTheDocument();
});
```

### Issue: Snapshot Tests Breaking

**Symptoms:**
- All snapshot tests fail
- Different component structure
- Changed class names

**Solutions:**

```jsx
// 1. Update snapshots selectively
// Run tests with update flag
npm test -- --updateSnapshot

// 2. Use semantic testing instead of snapshots
// ❌ Brittle snapshot test
expect(component).toMatchSnapshot();

// ✅ Semantic testing
expect(screen.getByRole('button')).toBeInTheDocument();
expect(screen.getByLabelText('Email')).toHaveValue('test@example.com');

// 3. Create custom snapshot serializers
// jest.config.js
module.exports = {
  snapshotSerializers: [
    './test-utils/design-system-serializer.js'
  ]
};
```

### Issue: Accessibility Tests Failing

**Symptoms:**
- axe-core violations
- Screen reader tests failing
- Keyboard navigation broken

**Solutions:**

```jsx
// 1. Run accessibility tests
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('should not have accessibility violations', async () => {
  const { container } = render(<InvoiceForm />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

// 2. Test keyboard navigation
import userEvent from '@testing-library/user-event';

test('keyboard navigation works', async () => {
  const user = userEvent.setup();
  render(<InvoiceForm />);
  
  // Tab through form fields
  await user.tab();
  expect(screen.getByLabelText('Numer faktury')).toHaveFocus();
  
  await user.tab();
  expect(screen.getByLabelText('Data wystawienia')).toHaveFocus();
});

// 3. Test screen reader announcements
test('screen reader announcements', async () => {
  render(<InvoiceForm />);
  
  const errorMessage = screen.getByRole('alert');
  expect(errorMessage).toHaveTextContent('NIP jest wymagany');
});
```

## Build and Bundle Issues

### Issue: Build Failing

**Symptoms:**
- Compilation errors
- Module not found errors
- TypeScript errors

**Solutions:**

```bash
# 1. Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# 2. Check TypeScript configuration
# tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "node",
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true
  },
  "include": [
    "src/**/*",
    "node_modules/@design-system/types"
  ]
}

# 3. Update webpack configuration
# webpack.config.js
module.exports = {
  resolve: {
    alias: {
      '@design-system': path.resolve(__dirname, 'node_modules/@design-system')
    }
  }
};
```

### Issue: CSS Not Loading

**Symptoms:**
- Components appear unstyled
- Design tokens not available
- CSS imports failing

**Solutions:**

```jsx
// 1. Import CSS in correct order
// index.js or App.js
import '@design-system/styles/reset.css';
import '@design-system/styles/tokens.css';
import '@design-system/styles/components.css';
import './custom-styles.css'; // Your custom styles last

// 2. Configure CSS loading in webpack
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader']
      }
    ]
  }
};

// 3. Use CSS-in-JS if needed
import { createGlobalStyle } from 'styled-components';

const GlobalStyles = createGlobalStyle`
  @import '@design-system/styles/index.css';
`;
```

## Accessibility Issues

### Issue: Screen Reader Not Working

**Symptoms:**
- Screen reader doesn't announce content
- Missing ARIA labels
- Poor navigation experience

**Solutions:**

```jsx
// 1. Add proper ARIA labels
<Input
  label="NIP firmy"
  aria-describedby="nip-help"
  aria-invalid={hasError}
  aria-required="true"
/>
<div id="nip-help">
  NIP musi składać się z 10 cyfr
</div>

// 2. Use semantic HTML
// ❌ Non-semantic
<div onClick={handleClick}>Click me</div>

// ✅ Semantic
<button onClick={handleClick}>Click me</button>

// 3. Provide live region updates
<LiveRegion>
  {message && <div>{message}</div>}
</LiveRegion>
```

### Issue: Keyboard Navigation Broken

**Symptoms:**
- Can't tab through components
- Focus indicators missing
- Keyboard shortcuts not working

**Solutions:**

```jsx
// 1. Ensure proper tab order
<form>
  <Input tabIndex={1} label="First field" />
  <Input tabIndex={2} label="Second field" />
  <Button tabIndex={3}>Submit</Button>
</form>

// 2. Add focus indicators
.ds-button:focus {
  outline: 2px solid var(--ds-color-focus);
  outline-offset: 2px;
}

// 3. Handle keyboard events
const handleKeyDown = (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    handleClick();
  }
};

<div
  role="button"
  tabIndex={0}
  onKeyDown={handleKeyDown}
  onClick={handleClick}
>
  Custom button
</div>
```

## Browser Compatibility

### Issue: Components Not Working in IE11

**Symptoms:**
- White screen in IE11
- JavaScript errors
- CSS not applied

**Solutions:**

```jsx
// 1. Add polyfills
// polyfills.js
import 'core-js/stable';
import 'regenerator-runtime/runtime';

// 2. Configure Babel for IE11
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        ie: '11'
      }
    }]
  ]
};

// 3. Use CSS fallbacks
.ds-button {
  background: #007bff; /* Fallback */
  background: var(--ds-color-primary-500);
}
```

### Issue: Safari Specific Problems

**Symptoms:**
- Layout issues in Safari
- Date picker not working
- CSS Grid problems

**Solutions:**

```css
/* 1. Safari CSS fixes */
.ds-grid {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-orient: horizontal;
  -webkit-box-direction: normal;
  -ms-flex-direction: row;
  flex-direction: row;
}

/* 2. Safari date input fallback */
input[type="date"]::-webkit-calendar-picker-indicator {
  opacity: 1;
}

/* 3. Safari flexbox fixes */
.ds-flex-item {
  -webkit-box-flex: 1;
  -ms-flex: 1 1 auto;
  flex: 1 1 auto;
}
```

## Getting Help

### Debug Mode

Enable debug mode to get more detailed error information:

```jsx
// Enable debug mode
<ThemeProvider theme="polish-business" debug={true}>
  <App />
</ThemeProvider>
```

### Logging

Use the design system logger for debugging:

```jsx
import { logger } from '@design-system/utils';

// Log component state
logger.debug('Component rendered', { props, state });

// Log errors
logger.error('Validation failed', { field, value, error });
```

### Support Resources

1. **Documentation**: Check the design system documentation
2. **GitHub Issues**: Search existing issues or create new ones
3. **Team Chat**: Contact the design system team
4. **Stack Overflow**: Use tags `design-system` and `faktulove`

This troubleshooting guide should help resolve most common issues encountered during design system migration and usage.