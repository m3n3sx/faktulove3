# Build System and Bundle Optimization

This document outlines the build system optimizations implemented for the FaktuLove design system to ensure optimal performance and minimal bundle size.

## Overview

The build system is optimized for:
- **Tree-shaking**: Eliminate unused code from the final bundle
- **Code splitting**: Split code into optimal chunks for caching
- **CSS optimization**: Remove unused styles and minify CSS
- **Compression**: Gzip and Brotli compression for smaller file sizes
- **Performance monitoring**: Track bundle size and runtime performance

## Bundle Splitting Strategy

### Chunk Configuration

The build system creates the following chunks for optimal caching:

1. **Design Tokens** (`design-tokens.js`)
   - Contains all design system tokens
   - Highest caching priority (rarely changes)
   - ~10-15KB gzipped

2. **Design System** (`design-system.js`)
   - Core design system components
   - High caching priority
   - ~50-80KB gzipped

3. **Polish Business** (`polish-business.js`)
   - Polish-specific business components
   - Medium caching priority
   - ~20-30KB gzipped

4. **React Vendor** (`react-vendor.js`)
   - React, React DOM, React Router
   - High caching priority
   - ~40-50KB gzipped

5. **UI Libraries** (`ui-libraries.js`)
   - Third-party UI libraries
   - Medium caching priority
   - ~15-25KB gzipped

### Benefits

- **Better Caching**: Design tokens rarely change, so they can be cached longer
- **Parallel Loading**: Multiple chunks can be loaded simultaneously
- **Incremental Updates**: Only changed chunks need to be re-downloaded
- **Reduced Initial Load**: Critical code loads first, non-critical code loads later

## Tree Shaking

### Configuration

Tree shaking is enabled for:
- Design system components (marked as side-effect free)
- Utility functions
- Third-party libraries (where supported)

### Side Effects

The following files are marked as having side effects:
- CSS files (`*.css`, `*.scss`, `*.sass`, `*.less`)
- Polyfills (`polyfills.js`)

### Optimization Tips

```typescript
// ✅ Good: Named imports enable tree shaking
import { Button, Input } from '@/design-system';

// ❌ Bad: Default imports prevent tree shaking
import * as DesignSystem from '@/design-system';

// ✅ Good: Import only what you need
import { colors } from '@/design-system/tokens';

// ❌ Bad: Imports entire tokens object
import tokens from '@/design-system/tokens';
```

## CSS Optimization

### PurgeCSS Configuration

PurgeCSS removes unused CSS classes based on:
- Component files (`src/**/*.{js,jsx,ts,tsx}`)
- HTML templates (`public/index.html`)
- Design system components

### Safelist

The following classes are always preserved:
- Design system prefixes (`ds-*`)
- State classes (`hover:*`, `focus:*`, `active:*`)
- Responsive classes (`sm:*`, `md:*`, `lg:*`)
- Polish business classes (`currency-*`, `nip-*`, `vat-*`)
- Animation classes (`animate-*`)
- Accessibility classes (`sr-only`, `focus-visible`)

### Dynamic Classes

For dynamically generated classes, use safelist patterns:

```javascript
// tailwind.config.js
module.exports = {
  // ...
  safelist: [
    // Pattern for color variants
    {
      pattern: /^(text|bg)-(primary|success|warning|error)-(50|100|200|300|400|500|600|700|800|900)$/,
    },
    // Specific classes
    'text-primary-600',
    'bg-success-500',
  ],
};
```

## Performance Budgets

### Bundle Size Limits

| Asset Type | Limit | Gzipped Limit |
|------------|-------|---------------|
| JavaScript | 1MB | 300KB |
| CSS | 100KB | 30KB |
| Design System | 200KB | 60KB |
| Total | 1.5MB | 400KB |

### Core Web Vitals Targets

| Metric | Target | Description |
|--------|--------|-------------|
| LCP | < 2.5s | Largest Contentful Paint |
| FID | < 100ms | First Input Delay |
| CLS | < 0.1 | Cumulative Layout Shift |
| FCP | < 1.8s | First Contentful Paint |
| TTFB | < 600ms | Time to First Byte |

## Build Scripts

### Available Commands

```bash
# Standard build
npm run build

# Build with bundle analysis
npm run build:analyze

# Optimized production build
npm run build:optimized

# Analyze existing bundle
npm run analyze:bundle

# Monitor runtime performance
npm run analyze:performance
```

### Bundle Analysis

The bundle analyzer provides:
- **Size breakdown** by chunk and module
- **Dependency analysis** showing what's included
- **Optimization suggestions** for reducing bundle size
- **Comparison** with previous builds

Example output:
```
📊 Bundle Analysis Summary
==========================
Total Bundle Size: 1.2MB
Total Gzip Size: 350KB
Design System Impact: 180KB (15%)

📈 Changes from Previous Build
==============================
Bundle Size: 🟢 -50KB (-4%)
Gzip Size: 🟢 -15KB (-4%)
Design System: 🟢 -10KB (-5%)
```

### Performance Monitoring

Runtime performance monitoring tracks:
- **Component render times** for all design system components
- **Memory usage** over time
- **Core Web Vitals** metrics
- **Design system impact** on overall performance

## Optimization Techniques

### 1. Component Lazy Loading

```typescript
// Lazy load heavy components
const DataTable = React.lazy(() => import('@/design-system/components/patterns/Table'));

// Use with Suspense
<Suspense fallback={<div>Loading...</div>}>
  <DataTable data={data} />
</Suspense>
```

### 2. Dynamic Imports

```typescript
// Dynamic import for code splitting
const loadPolishValidation = () => import('@/design-system/utils/polish-validation');

// Use when needed
const handleNIPValidation = async (nip: string) => {
  const { validateNIP } = await loadPolishValidation();
  return validateNIP(nip);
};
```

### 3. CSS-in-JS Optimization

```typescript
// Use CSS custom properties for dynamic styles
const Button = styled.button<{ variant: string }>`
  background-color: var(--color-${props => props.variant}-600);
  
  // Instead of generating multiple CSS classes
  ${props => props.variant === 'primary' && css`
    background-color: var(--color-primary-600);
  `}
`;
```

### 4. Image Optimization

```typescript
// Use next/image or similar for automatic optimization
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="FaktuLove Logo"
  width={200}
  height={50}
  priority // For above-the-fold images
/>
```

## Monitoring and Alerts

### Bundle Size Monitoring

Set up CI/CD alerts for:
- Bundle size increases > 10%
- Individual chunk size > limits
- Total bundle size > performance budget

### Performance Monitoring

Track in production:
- Core Web Vitals metrics
- Component render times
- Memory usage patterns
- Error rates

### Example CI Configuration

```yaml
# .github/workflows/bundle-analysis.yml
name: Bundle Analysis

on:
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Build and analyze
        run: npm run build:analyze
      - name: Upload bundle report
        uses: actions/upload-artifact@v2
        with:
          name: bundle-report
          path: build/bundle-report.html
```

## Troubleshooting

### Common Issues

**Issue**: Bundle size suddenly increased
**Solution**: 
1. Run `npm run analyze:bundle` to identify the cause
2. Check for new dependencies or imports
3. Verify tree-shaking is working correctly

**Issue**: CSS not being purged correctly
**Solution**:
1. Check PurgeCSS configuration in `postcss.config.js`
2. Add dynamic classes to safelist
3. Verify content paths include all component files

**Issue**: Design system components not tree-shaking
**Solution**:
1. Ensure components are exported as named exports
2. Check `sideEffects: false` in package.json
3. Verify import statements use named imports

### Performance Debugging

```typescript
// Add performance marks for debugging
performance.mark('component-render-start');
// Component render logic
performance.mark('component-render-end');
performance.measure('component-render', 'component-render-start', 'component-render-end');

// Log performance measures
const measures = performance.getEntriesByType('measure');
console.log('Performance measures:', measures);
```

## Best Practices

### Development

1. **Use named imports** to enable tree-shaking
2. **Import only what you need** from design system
3. **Lazy load heavy components** that aren't immediately visible
4. **Monitor bundle size** during development
5. **Test with production builds** regularly

### Production

1. **Enable all optimizations** (minification, compression, tree-shaking)
2. **Monitor Core Web Vitals** in real users
3. **Set up performance budgets** in CI/CD
4. **Regular bundle analysis** to catch regressions
5. **Cache optimization** with proper headers

### Design System Maintenance

1. **Keep components lightweight** and focused
2. **Minimize dependencies** in design system packages
3. **Use CSS custom properties** for theming
4. **Document performance impact** of new components
5. **Regular performance audits** of the design system

## Future Optimizations

### Planned Improvements

1. **Module Federation**: Share design system across multiple applications
2. **Service Worker**: Cache design system assets more aggressively
3. **Critical CSS**: Inline critical design system styles
4. **HTTP/3**: Take advantage of improved multiplexing
5. **WebAssembly**: Move heavy computations to WASM

### Experimental Features

1. **React Server Components**: Reduce client-side JavaScript
2. **Streaming SSR**: Improve perceived performance
3. **Selective Hydration**: Hydrate components on demand
4. **Edge Computing**: Move rendering closer to users