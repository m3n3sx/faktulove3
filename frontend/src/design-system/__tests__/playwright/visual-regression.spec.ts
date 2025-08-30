/**
 * Playwright Visual Regression Tests
 * Cross-browser visual testing for design system components
 */

import { test, expect } from '@playwright/test';

// Test configuration
const themes = ['light', 'dark', 'high-contrast', 'polish-business'];
const viewports = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1440, height: 900 },
};

// Helper function to set theme
async function setTheme(page: any, theme: string) {
  await page.evaluate((themeName) => {
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem('design-system-theme', themeName);
  }, theme);
  
  // Wait for theme to apply
  await page.waitForTimeout(100);
}

// Helper function to navigate to component showcase
async function navigateToShowcase(page: any, component: string) {
  await page.goto(`/design-system/showcase/${component}`);
  await page.waitForLoadState('networkidle');
}

test.describe('Design System Visual Regression Tests', () => {
  
  test.describe('Component Showcase Tests', () => {
    
    test('Button component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'button');
      
      // Test all themes
      for (const theme of themes) {
        await setTheme(page, theme);
        
        // Take screenshot of button showcase
        await expect(page.locator('[data-testid="button-showcase"]')).toHaveScreenshot(
          `button-showcase-${theme}.png`
        );
        
        // Test button states
        const hoverButton = page.locator('[data-testid="button-hover"]');
        await hoverButton.hover();
        await expect(hoverButton).toHaveScreenshot(`button-hover-${theme}.png`);
        
        const focusButton = page.locator('[data-testid="button-focus"]');
        await focusButton.focus();
        await expect(focusButton).toHaveScreenshot(`button-focus-${theme}.png`);
      }
    });

    test('Input component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'input');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        // Test input showcase
        await expect(page.locator('[data-testid="input-showcase"]')).toHaveScreenshot(
          `input-showcase-${theme}.png`
        );
        
        // Test input states
        const errorInput = page.locator('[data-testid="input-error"]');
        await expect(errorInput).toHaveScreenshot(`input-error-${theme}.png`);
        
        const successInput = page.locator('[data-testid="input-success"]');
        await expect(successInput).toHaveScreenshot(`input-success-${theme}.png`);
        
        // Test input focus
        const focusInput = page.locator('[data-testid="input-focus"]');
        await focusInput.focus();
        await expect(focusInput).toHaveScreenshot(`input-focus-${theme}.png`);
      }
    });

    test('Form component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'form');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="form-showcase"]')).toHaveScreenshot(
          `form-showcase-${theme}.png`
        );
        
        // Test form validation states
        const submitButton = page.locator('[data-testid="form-submit"]');
        await submitButton.click();
        
        // Wait for validation to appear
        await page.waitForSelector('[data-testid="form-errors"]');
        await expect(page.locator('[data-testid="form-showcase"]')).toHaveScreenshot(
          `form-validation-${theme}.png`
        );
      }
    });

    test('Table component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'table');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="table-showcase"]')).toHaveScreenshot(
          `table-showcase-${theme}.png`
        );
        
        // Test table sorting
        const sortHeader = page.locator('[data-testid="table-sort-header"]').first();
        await sortHeader.click();
        await expect(page.locator('[data-testid="table-showcase"]')).toHaveScreenshot(
          `table-sorted-${theme}.png`
        );
      }
    });

    test('Card component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'card');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="card-showcase"]')).toHaveScreenshot(
          `card-showcase-${theme}.png`
        );
      }
    });
  });

  test.describe('Polish Business Components Tests', () => {
    
    test('CurrencyInput component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'currency-input');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="currency-input-showcase"]')).toHaveScreenshot(
          `currency-input-showcase-${theme}.png`
        );
        
        // Test currency formatting
        const currencyInput = page.locator('[data-testid="currency-input"]');
        await currencyInput.fill('1234.56');
        await currencyInput.blur();
        
        await expect(page.locator('[data-testid="currency-input-showcase"]')).toHaveScreenshot(
          `currency-input-formatted-${theme}.png`
        );
      }
    });

    test('DatePicker component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'date-picker');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="date-picker-showcase"]')).toHaveScreenshot(
          `date-picker-showcase-${theme}.png`
        );
        
        // Test date picker open state
        const datePickerTrigger = page.locator('[data-testid="date-picker-trigger"]');
        await datePickerTrigger.click();
        
        await page.waitForSelector('[data-testid="date-picker-calendar"]');
        await expect(page.locator('[data-testid="date-picker-showcase"]')).toHaveScreenshot(
          `date-picker-open-${theme}.png`
        );
      }
    });

    test('NIPValidator component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'nip-validator');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="nip-validator-showcase"]')).toHaveScreenshot(
          `nip-validator-showcase-${theme}.png`
        );
        
        // Test valid NIP
        const nipInput = page.locator('[data-testid="nip-input"]');
        await nipInput.fill('1234567890');
        await nipInput.blur();
        
        await expect(page.locator('[data-testid="nip-validator-showcase"]')).toHaveScreenshot(
          `nip-validator-valid-${theme}.png`
        );
        
        // Test invalid NIP
        await nipInput.fill('1234567891');
        await nipInput.blur();
        
        await expect(page.locator('[data-testid="nip-validator-showcase"]')).toHaveScreenshot(
          `nip-validator-invalid-${theme}.png`
        );
      }
    });

    test('VATRateSelector component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'vat-rate-selector');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="vat-rate-selector-showcase"]')).toHaveScreenshot(
          `vat-rate-selector-showcase-${theme}.png`
        );
        
        // Test VAT rate selection
        const vatSelector = page.locator('[data-testid="vat-rate-selector"]');
        await vatSelector.click();
        
        await page.waitForSelector('[data-testid="vat-rate-options"]');
        await expect(page.locator('[data-testid="vat-rate-selector-showcase"]')).toHaveScreenshot(
          `vat-rate-selector-open-${theme}.png`
        );
      }
    });

    test('InvoiceStatusBadge component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'invoice-status-badge');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="invoice-status-badge-showcase"]')).toHaveScreenshot(
          `invoice-status-badge-showcase-${theme}.png`
        );
      }
    });
  });

  test.describe('Layout Components Tests', () => {
    
    test('Grid component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'grid');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="grid-showcase"]')).toHaveScreenshot(
          `grid-showcase-${theme}.png`
        );
      }
    });

    test('Container component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'container');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="container-showcase"]')).toHaveScreenshot(
          `container-showcase-${theme}.png`
        );
      }
    });

    test('Stack component visual regression', async ({ page }) => {
      await navigateToShowcase(page, 'stack');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        await expect(page.locator('[data-testid="stack-showcase"]')).toHaveScreenshot(
          `stack-showcase-${theme}.png`
        );
      }
    });
  });

  test.describe('Responsive Layout Tests', () => {
    
    Object.entries(viewports).forEach(([viewportName, viewport]) => {
      test(`Responsive layout on ${viewportName}`, async ({ page }) => {
        await page.setViewportSize(viewport);
        await page.goto('/design-system/showcase/responsive');
        await page.waitForLoadState('networkidle');
        
        for (const theme of themes) {
          await setTheme(page, theme);
          
          await expect(page.locator('[data-testid="responsive-showcase"]')).toHaveScreenshot(
            `responsive-${viewportName}-${theme}.png`
          );
        }
      });
    });

    test('Invoice form responsive layout', async ({ page }) => {
      await page.goto('/design-system/showcase/invoice-form');
      await page.waitForLoadState('networkidle');
      
      Object.entries(viewports).forEach(async ([viewportName, viewport]) => {
        await page.setViewportSize(viewport);
        
        for (const theme of themes) {
          await setTheme(page, theme);
          
          await expect(page.locator('[data-testid="invoice-form-showcase"]')).toHaveScreenshot(
            `invoice-form-${viewportName}-${theme}.png`
          );
        }
      });
    });

    test('Dashboard responsive layout', async ({ page }) => {
      await page.goto('/design-system/showcase/dashboard');
      await page.waitForLoadState('networkidle');
      
      Object.entries(viewports).forEach(async ([viewportName, viewport]) => {
        await page.setViewportSize(viewport);
        
        for (const theme of themes) {
          await setTheme(page, theme);
          
          await expect(page.locator('[data-testid="dashboard-showcase"]')).toHaveScreenshot(
            `dashboard-${viewportName}-${theme}.png`
          );
        }
      });
    });
  });

  test.describe('Theme Switching Tests', () => {
    
    test('Theme switching animation', async ({ page }) => {
      await page.goto('/design-system/showcase/theme-switching');
      await page.waitForLoadState('networkidle');
      
      // Start with light theme
      await setTheme(page, 'light');
      await expect(page.locator('[data-testid="theme-showcase"]')).toHaveScreenshot(
        'theme-switching-light.png'
      );
      
      // Switch to dark theme
      const themeToggle = page.locator('[data-testid="theme-toggle"]');
      await themeToggle.click();
      
      // Wait for theme transition
      await page.waitForTimeout(300);
      await expect(page.locator('[data-testid="theme-showcase"]')).toHaveScreenshot(
        'theme-switching-dark.png'
      );
      
      // Switch to high contrast theme
      const themeSelector = page.locator('[data-testid="theme-selector"]');
      await themeSelector.selectOption('high-contrast');
      
      await page.waitForTimeout(300);
      await expect(page.locator('[data-testid="theme-showcase"]')).toHaveScreenshot(
        'theme-switching-high-contrast.png'
      );
    });

    test('Polish business theme customizations', async ({ page }) => {
      await page.goto('/design-system/showcase/polish-business-theme');
      await page.waitForLoadState('networkidle');
      
      await setTheme(page, 'polish-business');
      
      await expect(page.locator('[data-testid="polish-business-showcase"]')).toHaveScreenshot(
        'polish-business-theme.png'
      );
      
      // Test Polish business components in theme
      await expect(page.locator('[data-testid="polish-currency-showcase"]')).toHaveScreenshot(
        'polish-business-currency.png'
      );
      
      await expect(page.locator('[data-testid="polish-vat-showcase"]')).toHaveScreenshot(
        'polish-business-vat.png'
      );
      
      await expect(page.locator('[data-testid="polish-nip-showcase"]')).toHaveScreenshot(
        'polish-business-nip.png'
      );
    });
  });

  test.describe('Complex Integration Tests', () => {
    
    test('Complete invoice form integration', async ({ page }) => {
      await page.goto('/design-system/showcase/complete-invoice-form');
      await page.waitForLoadState('networkidle');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        // Initial form state
        await expect(page.locator('[data-testid="complete-invoice-form"]')).toHaveScreenshot(
          `complete-invoice-form-initial-${theme}.png`
        );
        
        // Fill out form
        await page.fill('[data-testid="invoice-number"]', 'INV-001');
        await page.fill('[data-testid="seller-nip"]', '1234567890');
        await page.fill('[data-testid="buyer-nip"]', '5260001246');
        await page.fill('[data-testid="net-amount"]', '1000');
        await page.selectOption('[data-testid="vat-rate"]', '23');
        await page.fill('[data-testid="issue-date"]', '15.03.2024');
        
        // Form with data
        await expect(page.locator('[data-testid="complete-invoice-form"]')).toHaveScreenshot(
          `complete-invoice-form-filled-${theme}.png`
        );
        
        // Submit form to show validation
        await page.click('[data-testid="submit-button"]');
        
        // Wait for success state
        await page.waitForSelector('[data-testid="form-success"]');
        await expect(page.locator('[data-testid="complete-invoice-form"]')).toHaveScreenshot(
          `complete-invoice-form-success-${theme}.png`
        );
      }
    });

    test('Dashboard with real data', async ({ page }) => {
      await page.goto('/design-system/showcase/dashboard-with-data');
      await page.waitForLoadState('networkidle');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        // Full dashboard
        await expect(page.locator('[data-testid="dashboard-with-data"]')).toHaveScreenshot(
          `dashboard-with-data-${theme}.png`
        );
        
        // Test interactive elements
        const chartFilter = page.locator('[data-testid="chart-filter"]');
        await chartFilter.selectOption('monthly');
        
        await page.waitForTimeout(500); // Wait for chart update
        await expect(page.locator('[data-testid="dashboard-charts"]')).toHaveScreenshot(
          `dashboard-charts-monthly-${theme}.png`
        );
      }
    });

    test('OCR interface integration', async ({ page }) => {
      await page.goto('/design-system/showcase/ocr-interface');
      await page.waitForLoadState('networkidle');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        // Initial OCR interface
        await expect(page.locator('[data-testid="ocr-interface"]')).toHaveScreenshot(
          `ocr-interface-initial-${theme}.png`
        );
        
        // Simulate file upload
        const fileInput = page.locator('[data-testid="file-upload-input"]');
        await fileInput.setInputFiles({
          name: 'test-invoice.pdf',
          mimeType: 'application/pdf',
          buffer: Buffer.from('test pdf content'),
        });
        
        // Wait for upload processing
        await page.waitForSelector('[data-testid="ocr-processing"]');
        await expect(page.locator('[data-testid="ocr-interface"]')).toHaveScreenshot(
          `ocr-interface-processing-${theme}.png`
        );
        
        // Wait for results
        await page.waitForSelector('[data-testid="ocr-results"]');
        await expect(page.locator('[data-testid="ocr-interface"]')).toHaveScreenshot(
          `ocr-interface-results-${theme}.png`
        );
      }
    });
  });

  test.describe('Error States and Edge Cases', () => {
    
    test('Form validation error states', async ({ page }) => {
      await page.goto('/design-system/showcase/form-validation');
      await page.waitForLoadState('networkidle');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        // Submit empty form to trigger validation
        await page.click('[data-testid="submit-button"]');
        
        await page.waitForSelector('[data-testid="validation-errors"]');
        await expect(page.locator('[data-testid="form-validation-showcase"]')).toHaveScreenshot(
          `form-validation-errors-${theme}.png`
        );
        
        // Test individual field errors
        await page.fill('[data-testid="email-input"]', 'invalid-email');
        await page.blur('[data-testid="email-input"]');
        
        await expect(page.locator('[data-testid="email-field"]')).toHaveScreenshot(
          `email-field-error-${theme}.png`
        );
      }
    });

    test('Loading states', async ({ page }) => {
      await page.goto('/design-system/showcase/loading-states');
      await page.waitForLoadState('networkidle');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        // Button loading state
        await page.click('[data-testid="trigger-loading"]');
        await expect(page.locator('[data-testid="loading-button"]')).toHaveScreenshot(
          `button-loading-${theme}.png`
        );
        
        // Table loading state
        await expect(page.locator('[data-testid="loading-table"]')).toHaveScreenshot(
          `table-loading-${theme}.png`
        );
        
        // Form loading state
        await expect(page.locator('[data-testid="loading-form"]')).toHaveScreenshot(
          `form-loading-${theme}.png`
        );
      }
    });

    test('Empty states', async ({ page }) => {
      await page.goto('/design-system/showcase/empty-states');
      await page.waitForLoadState('networkidle');
      
      for (const theme of themes) {
        await setTheme(page, theme);
        
        // Empty table
        await expect(page.locator('[data-testid="empty-table"]')).toHaveScreenshot(
          `empty-table-${theme}.png`
        );
        
        // Empty dashboard
        await expect(page.locator('[data-testid="empty-dashboard"]')).toHaveScreenshot(
          `empty-dashboard-${theme}.png`
        );
        
        // Empty search results
        await expect(page.locator('[data-testid="empty-search"]')).toHaveScreenshot(
          `empty-search-${theme}.png`
        );
      }
    });
  });
});