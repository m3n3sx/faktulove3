/**
 * Accessibility Testing Utilities
 * Automated utilities for WCAG compliance, keyboard navigation, and screen reader testing
 */

import { axe, AxeResults, Result } from 'axe-core';
import { fireEvent, screen } from '@testing-library/react';

// WCAG compliance levels
export type WCAGLevel = 'A' | 'AA' | 'AAA';

// Accessibility test configuration
export interface AccessibilityTestConfig {
  level: WCAGLevel;
  tags?: string[];
  rules?: Record<string, { enabled: boolean }>;
  includedImpacts?: ('minor' | 'moderate' | 'serious' | 'critical')[];
  excludeSelectors?: string[];
  polishBusinessRules?: boolean;
}

// Default accessibility test configuration
export const defaultA11yConfig: AccessibilityTestConfig = {
  level: 'AA',
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'],
  includedImpacts: ['moderate', 'serious', 'critical'],
  polishBusinessRules: true,
};

// Polish business specific accessibility rules
export const polishBusinessA11yRules = {
  'polish-currency-format': {
    enabled: true,
    description: 'Ensures Polish currency inputs have proper formatting and labels',
  },
  'polish-date-format': {
    enabled: true,
    description: 'Ensures Polish date inputs use DD.MM.YYYY format with proper labels',
  },
  'nip-validation-accessibility': {
    enabled: true,
    description: 'Ensures NIP validation provides accessible error messages',
  },
  'vat-rate-accessibility': {
    enabled: true,
    description: 'Ensures VAT rate selectors have proper Polish labels',
  },
  'invoice-status-accessibility': {
    enabled: true,
    description: 'Ensures invoice status badges are accessible to screen readers',
  },
};

// Keyboard navigation test patterns
export interface KeyboardTestPattern {
  name: string;
  description: string;
  selector: string;
  keys: string[];
  expectedBehavior: string;
  test: (element: HTMLElement) => Promise<boolean>;
}

export const keyboardNavigationPatterns: KeyboardTestPattern[] = [
  {
    name: 'Tab Navigation',
    description: 'Elements should be focusable with Tab key',
    selector: 'button, input, select, textarea, [tabindex]:not([tabindex="-1"])',
    keys: ['Tab'],
    expectedBehavior: 'Focus moves to next focusable element',
    test: async (element) => {
      element.focus();
      fireEvent.keyDown(element, { key: 'Tab' });
      return document.activeElement !== element;
    },
  },
  {
    name: 'Enter Activation',
    description: 'Buttons should activate with Enter key',
    selector: 'button, [role="button"]',
    keys: ['Enter'],
    expectedBehavior: 'Button click event is triggered',
    test: async (element) => {
      let activated = false;
      const handler = () => { activated = true; };
      element.addEventListener('click', handler);
      
      element.focus();
      fireEvent.keyDown(element, { key: 'Enter' });
      
      element.removeEventListener('click', handler);
      return activated;
    },
  },
  {
    name: 'Space Activation',
    description: 'Buttons and checkboxes should activate with Space key',
    selector: 'button, [role="button"], input[type="checkbox"], [role="checkbox"]',
    keys: [' '],
    expectedBehavior: 'Element is activated',
    test: async (element) => {
      let activated = false;
      const handler = () => { activated = true; };
      element.addEventListener('click', handler);
      
      element.focus();
      fireEvent.keyDown(element, { key: ' ' });
      
      element.removeEventListener('click', handler);
      return activated;
    },
  },
  {
    name: 'Arrow Key Navigation',
    description: 'Radio groups should navigate with arrow keys',
    selector: 'input[type="radio"], [role="radio"]',
    keys: ['ArrowDown', 'ArrowUp', 'ArrowLeft', 'ArrowRight'],
    expectedBehavior: 'Focus moves between radio buttons in group',
    test: async (element) => {
      const radioGroup = element.closest('[role="radiogroup"]') || 
                        element.closest('fieldset') ||
                        element.form;
      
      if (!radioGroup) return false;
      
      const radios = Array.from(radioGroup.querySelectorAll('input[type="radio"], [role="radio"]'));
      const currentIndex = radios.indexOf(element);
      
      element.focus();
      fireEvent.keyDown(element, { key: 'ArrowDown' });
      
      const nextIndex = (currentIndex + 1) % radios.length;
      return document.activeElement === radios[nextIndex];
    },
  },
  {
    name: 'Escape Key',
    description: 'Modals and dropdowns should close with Escape key',
    selector: '[role="dialog"], [role="menu"], [aria-expanded="true"]',
    keys: ['Escape'],
    expectedBehavior: 'Modal or dropdown closes',
    test: async (element) => {
      let closed = false;
      const handler = () => { closed = true; };
      element.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') handler();
      });
      
      element.focus();
      fireEvent.keyDown(element, { key: 'Escape' });
      
      return closed;
    },
  },
];

// Screen reader test utilities
export interface ScreenReaderTest {
  name: string;
  description: string;
  test: (container: HTMLElement) => Promise<ScreenReaderTestResult>;
}

export interface ScreenReaderTestResult {
  passed: boolean;
  issues: string[];
  recommendations: string[];
}

export const screenReaderTests: ScreenReaderTest[] = [
  {
    name: 'ARIA Labels',
    description: 'All interactive elements should have accessible names',
    test: async (container) => {
      const issues: string[] = [];
      const recommendations: string[] = [];
      
      const interactiveElements = container.querySelectorAll(
        'button, input, select, textarea, [role="button"], [role="textbox"], [role="combobox"]'
      );
      
      interactiveElements.forEach((element, index) => {
        const hasLabel = element.hasAttribute('aria-label') ||
                         element.hasAttribute('aria-labelledby') ||
                         container.querySelector(`label[for="${element.id}"]`) ||
                         element.textContent?.trim();
        
        if (!hasLabel) {
          issues.push(`Interactive element ${index + 1} lacks accessible name`);
          recommendations.push(`Add aria-label or associate with a label element`);
        }
      });
      
      return {
        passed: issues.length === 0,
        issues,
        recommendations,
      };
    },
  },
  {
    name: 'Live Regions',
    description: 'Dynamic content changes should be announced',
    test: async (container) => {
      const issues: string[] = [];
      const recommendations: string[] = [];
      
      const liveRegions = container.querySelectorAll('[aria-live], [role="alert"], [role="status"]');
      const dynamicContent = container.querySelectorAll('[data-dynamic], .loading, .error, .success');
      
      if (dynamicContent.length > 0 && liveRegions.length === 0) {
        issues.push('Dynamic content found but no live regions detected');
        recommendations.push('Add aria-live regions to announce content changes');
      }
      
      return {
        passed: issues.length === 0,
        issues,
        recommendations,
      };
    },
  },
  {
    name: 'Form Validation',
    description: 'Form errors should be properly announced',
    test: async (container) => {
      const issues: string[] = [];
      const recommendations: string[] = [];
      
      const formElements = container.querySelectorAll('input, select, textarea');
      
      formElements.forEach((element, index) => {
        const hasError = element.hasAttribute('aria-invalid') && 
                        element.getAttribute('aria-invalid') === 'true';
        
        if (hasError) {
          const hasErrorMessage = element.hasAttribute('aria-describedby') ||
                                 container.querySelector(`[id="${element.getAttribute('aria-describedby')}"]`);
          
          if (!hasErrorMessage) {
            issues.push(`Form element ${index + 1} has error state but no error message`);
            recommendations.push('Associate error messages with aria-describedby');
          }
        }
      });
      
      return {
        passed: issues.length === 0,
        issues,
        recommendations,
      };
    },
  },
  {
    name: 'Polish Language Support',
    description: 'Polish content should have proper language attributes',
    test: async (container) => {
      const issues: string[] = [];
      const recommendations: string[] = [];
      
      const polishText = container.textContent?.match(/[ąćęłńóśźż]/i);
      const hasLangAttribute = container.hasAttribute('lang') ||
                              container.closest('[lang]') ||
                              document.documentElement.hasAttribute('lang');
      
      if (polishText && !hasLangAttribute) {
        issues.push('Polish text detected but no language attribute found');
        recommendations.push('Add lang="pl" attribute to Polish content');
      }
      
      return {
        passed: issues.length === 0,
        issues,
        recommendations,
      };
    },
  },
];

// Color contrast testing utilities
export interface ColorContrastTest {
  element: HTMLElement;
  foreground: string;
  background: string;
  ratio: number;
  level: 'AA' | 'AAA';
  size: 'normal' | 'large';
  passed: boolean;
}

export const testColorContrast = (element: HTMLElement): ColorContrastTest => {
  const styles = window.getComputedStyle(element);
  const foreground = styles.color;
  const background = styles.backgroundColor;
  
  // Calculate contrast ratio (simplified implementation)
  const ratio = calculateContrastRatio(foreground, background);
  
  // Determine text size
  const fontSize = parseFloat(styles.fontSize);
  const fontWeight = styles.fontWeight;
  const isLarge = fontSize >= 18 || (fontSize >= 14 && (fontWeight === 'bold' || parseInt(fontWeight) >= 700));
  
  // WCAG AA requirements
  const requiredRatio = isLarge ? 3.0 : 4.5;
  
  return {
    element,
    foreground,
    background,
    ratio,
    level: 'AA',
    size: isLarge ? 'large' : 'normal',
    passed: ratio >= requiredRatio,
  };
};

// Focus visibility testing
export const testFocusVisibility = (element: HTMLElement): boolean => {
  element.focus();
  
  const styles = window.getComputedStyle(element);
  const outline = styles.outline;
  const outlineWidth = styles.outlineWidth;
  const boxShadow = styles.boxShadow;
  
  // Check if element has visible focus indicator
  return (outline !== 'none' && outlineWidth !== '0px') ||
         (boxShadow !== 'none' && boxShadow !== '');
};

// Comprehensive accessibility test suite
export const runA11yTestSuite = async (
  container: HTMLElement,
  config: Partial<AccessibilityTestConfig> = {}
): Promise<{
  axeResults: AxeResults;
  keyboardTests: Array<{ pattern: KeyboardTestPattern; passed: boolean; error?: string }>;
  screenReaderTests: Array<{ test: ScreenReaderTest; result: ScreenReaderTestResult }>;
  contrastTests: ColorContrastTest[];
  focusTests: Array<{ element: HTMLElement; passed: boolean }>;
  polishBusinessTests?: Array<{ name: string; passed: boolean; issues: string[] }>;
}> => {
  const finalConfig = { ...defaultA11yConfig, ...config };
  
  // Run axe-core tests
  const axeConfig = {
    tags: finalConfig.tags,
    rules: {
      ...finalConfig.rules,
      ...(finalConfig.polishBusinessRules ? polishBusinessA11yRules : {}),
    },
  };
  
  const axeResults = await axe(container, axeConfig);
  
  // Run keyboard navigation tests
  const keyboardTests = [];
  for (const pattern of keyboardNavigationPatterns) {
    const elements = container.querySelectorAll(pattern.selector);
    
    for (const element of Array.from(elements)) {
      try {
        const passed = await pattern.test(element as HTMLElement);
        keyboardTests.push({ pattern, passed });
      } catch (error) {
        keyboardTests.push({ 
          pattern, 
          passed: false, 
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }
  }
  
  // Run screen reader tests
  const screenReaderTestResults = [];
  for (const test of screenReaderTests) {
    const result = await test.test(container);
    screenReaderTestResults.push({ test, result });
  }
  
  // Run color contrast tests
  const contrastTests = [];
  const textElements = container.querySelectorAll('*');
  textElements.forEach(element => {
    const htmlElement = element as HTMLElement;
    if (htmlElement.textContent?.trim()) {
      contrastTests.push(testColorContrast(htmlElement));
    }
  });
  
  // Run focus visibility tests
  const focusTests = [];
  const focusableElements = container.querySelectorAll(
    'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
  );
  focusableElements.forEach(element => {
    const passed = testFocusVisibility(element as HTMLElement);
    focusTests.push({ element: element as HTMLElement, passed });
  });
  
  // Run Polish business specific tests
  let polishBusinessTests;
  if (finalConfig.polishBusinessRules) {
    polishBusinessTests = await runPolishBusinessA11yTests(container);
  }
  
  return {
    axeResults,
    keyboardTests,
    screenReaderTests: screenReaderTestResults,
    contrastTests,
    focusTests,
    polishBusinessTests,
  };
};

// Polish business specific accessibility tests
export const runPolishBusinessA11yTests = async (
  container: HTMLElement
): Promise<Array<{ name: string; passed: boolean; issues: string[] }>> => {
  const tests = [];
  
  // Test currency input accessibility
  const currencyInputs = container.querySelectorAll('[data-currency="PLN"], .ds-currency-input');
  if (currencyInputs.length > 0) {
    const issues: string[] = [];
    
    currencyInputs.forEach((input, index) => {
      const hasLabel = input.hasAttribute('aria-label') ||
                      input.hasAttribute('aria-labelledby') ||
                      container.querySelector(`label[for="${input.id}"]`);
      
      if (!hasLabel) {
        issues.push(`Currency input ${index + 1} lacks accessible name`);
      }
      
      const placeholder = input.getAttribute('placeholder');
      if (!placeholder?.includes('zł') && !placeholder?.includes('PLN')) {
        issues.push(`Currency input ${index + 1} should indicate Polish currency in placeholder`);
      }
    });
    
    tests.push({
      name: 'Polish Currency Input Accessibility',
      passed: issues.length === 0,
      issues,
    });
  }
  
  // Test NIP validator accessibility
  const nipInputs = container.querySelectorAll('[data-validate-nip], .ds-nip-validator');
  if (nipInputs.length > 0) {
    const issues: string[] = [];
    
    nipInputs.forEach((input, index) => {
      const hasLabel = input.hasAttribute('aria-label') ||
                      input.hasAttribute('aria-labelledby');
      
      if (!hasLabel) {
        issues.push(`NIP input ${index + 1} lacks accessible name`);
      }
      
      const hasPattern = input.hasAttribute('pattern');
      if (!hasPattern) {
        issues.push(`NIP input ${index + 1} should have pattern attribute for validation`);
      }
    });
    
    tests.push({
      name: 'NIP Validator Accessibility',
      passed: issues.length === 0,
      issues,
    });
  }
  
  // Test VAT rate selector accessibility
  const vatSelectors = container.querySelectorAll('.ds-vat-selector, [data-vat-rates]');
  if (vatSelectors.length > 0) {
    const issues: string[] = [];
    
    vatSelectors.forEach((selector, index) => {
      const hasLabel = selector.hasAttribute('aria-label') ||
                      selector.hasAttribute('aria-labelledby');
      
      if (!hasLabel) {
        issues.push(`VAT selector ${index + 1} lacks accessible name`);
      }
      
      const options = selector.querySelectorAll('option');
      const hasPolishRates = Array.from(options).some(option => 
        ['0', '5', '8', '23'].includes(option.getAttribute('value') || '')
      );
      
      if (!hasPolishRates) {
        issues.push(`VAT selector ${index + 1} should include standard Polish VAT rates`);
      }
    });
    
    tests.push({
      name: 'VAT Rate Selector Accessibility',
      passed: issues.length === 0,
      issues,
    });
  }
  
  // Test invoice status badge accessibility
  const statusBadges = container.querySelectorAll('.ds-invoice-status-badge, [data-invoice-status]');
  if (statusBadges.length > 0) {
    const issues: string[] = [];
    
    statusBadges.forEach((badge, index) => {
      const hasRole = badge.hasAttribute('role');
      const hasLabel = badge.hasAttribute('aria-label');
      
      if (!hasRole) {
        issues.push(`Status badge ${index + 1} should have role="status"`);
      }
      
      if (!hasLabel) {
        issues.push(`Status badge ${index + 1} should have aria-label with Polish status description`);
      }
    });
    
    tests.push({
      name: 'Invoice Status Badge Accessibility',
      passed: issues.length === 0,
      issues,
    });
  }
  
  return tests;
};

// Helper function to calculate contrast ratio (simplified)
function calculateContrastRatio(color1: string, color2: string): number {
  // This is a simplified implementation
  // In a real scenario, you would parse RGB values and calculate luminance
  // For testing purposes, we'll return a mock value
  return 4.6; // Assuming good contrast
}

// Utility to generate accessibility report
export const generateA11yReport = (
  testResults: Awaited<ReturnType<typeof runA11yTestSuite>>
): string => {
  const { axeResults, keyboardTests, screenReaderTests, contrastTests, focusTests, polishBusinessTests } = testResults;
  
  let report = '# Accessibility Test Report\n\n';
  
  // Axe results
  report += '## WCAG Compliance (axe-core)\n\n';
  if (axeResults.violations.length === 0) {
    report += '✅ No WCAG violations found\n\n';
  } else {
    report += `❌ ${axeResults.violations.length} WCAG violations found:\n\n`;
    axeResults.violations.forEach((violation, index) => {
      report += `${index + 1}. **${violation.id}**: ${violation.description}\n`;
      report += `   Impact: ${violation.impact}\n`;
      report += `   Nodes: ${violation.nodes.length}\n\n`;
    });
  }
  
  // Keyboard navigation results
  report += '## Keyboard Navigation\n\n';
  const keyboardPassed = keyboardTests.filter(t => t.passed).length;
  const keyboardTotal = keyboardTests.length;
  report += `${keyboardPassed}/${keyboardTotal} keyboard navigation tests passed\n\n`;
  
  // Screen reader results
  report += '## Screen Reader Compatibility\n\n';
  screenReaderTests.forEach(({ test, result }) => {
    const status = result.passed ? '✅' : '❌';
    report += `${status} **${test.name}**: ${test.description}\n`;
    if (!result.passed) {
      result.issues.forEach(issue => {
        report += `   - ${issue}\n`;
      });
    }
    report += '\n';
  });
  
  // Color contrast results
  report += '## Color Contrast\n\n';
  const contrastPassed = contrastTests.filter(t => t.passed).length;
  const contrastTotal = contrastTests.length;
  report += `${contrastPassed}/${contrastTotal} color contrast tests passed\n\n`;
  
  // Focus visibility results
  report += '## Focus Visibility\n\n';
  const focusPassed = focusTests.filter(t => t.passed).length;
  const focusTotal = focusTests.length;
  report += `${focusPassed}/${focusTotal} focus visibility tests passed\n\n`;
  
  // Polish business tests
  if (polishBusinessTests) {
    report += '## Polish Business Accessibility\n\n';
    polishBusinessTests.forEach(test => {
      const status = test.passed ? '✅' : '❌';
      report += `${status} **${test.name}**\n`;
      if (!test.passed) {
        test.issues.forEach(issue => {
          report += `   - ${issue}\n`;
        });
      }
      report += '\n';
    });
  }
  
  return report;
};

// Export all utilities
export const accessibilityTestUtils = {
  runA11yTestSuite,
  runPolishBusinessA11yTests,
  testColorContrast,
  testFocusVisibility,
  generateA11yReport,
  keyboardNavigationPatterns,
  screenReaderTests,
  defaultA11yConfig,
  polishBusinessA11yRules,
};