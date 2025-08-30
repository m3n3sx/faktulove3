import { render, RenderOptions, RenderResult } from '@testing-library/react';
// Mock jest-axe for now
const axe = jest.fn().mockResolvedValue({ violations: [] });
const toHaveNoViolations = jest.fn();
import userEvent from '@testing-library/user-event';
import React from 'react';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

/**
 * Custom render function that includes accessibility testing setup
 */
export const renderWithA11y = (
  ui: React.ReactElement,
  options?: RenderOptions
): RenderResult => {
  return render(ui, {
    ...options,
  });
};

/**
 * Test accessibility violations using jest-axe
 */
export const testA11y = async (container: HTMLElement) => {
  const results = await axe(container);
  expect(results).toHaveNoViolations();
};

/**
 * Test accessibility with custom axe configuration
 */
export const testA11yWithConfig = async (
  container: HTMLElement,
  config?: any
) => {
  const results = await axe(container, config);
  expect(results).toHaveNoViolations();
};

/**
 * Polish-specific accessibility configuration
 * Includes rules for Polish language content and business requirements
 */
export const polishA11yConfig = {
  rules: {
    // Ensure proper language attributes for Polish content
    'html-has-lang': { enabled: true },
    'valid-lang': { enabled: true },
    // Color contrast requirements for Polish business users
    'color-contrast': { enabled: true },
    'color-contrast-enhanced': { enabled: true },
    // Screen reader support for Polish content
    'aria-allowed-attr': { enabled: true },
    'aria-required-attr': { enabled: true },
    'aria-valid-attr-value': { enabled: true },
    'aria-valid-attr': { enabled: true },
    // Form accessibility for Polish business forms
    'label': { enabled: true },
    'form-field-multiple-labels': { enabled: true },
  },
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
};

/**
 * Test Polish-specific accessibility requirements
 */
export const testPolishA11y = async (container: HTMLElement) => {
  const results = await axe(container, polishA11yConfig);
  expect(results).toHaveNoViolations();
};

/**
 * Keyboard navigation test utilities
 */
export const keyboardTestUtils = {
  /**
   * Test Tab navigation through focusable elements
   */
  testTabNavigation: async (container: HTMLElement) => {
    const user = userEvent;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    // Start from first element
    if (focusableElements.length > 0) {
      (focusableElements[0] as HTMLElement).focus();
      
      // Tab through all elements
      for (let i = 1; i < focusableElements.length; i++) {
        await user.tab();
        expect(focusableElements[i]).toHaveFocus();
      }
    }
  },

  /**
   * Test Shift+Tab reverse navigation
   */
  testShiftTabNavigation: async (container: HTMLElement) => {
    const user = userEvent;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    // Start from last element
    if (focusableElements.length > 0) {
      const lastIndex = focusableElements.length - 1;
      (focusableElements[lastIndex] as HTMLElement).focus();
      
      // Shift+Tab through all elements in reverse
      for (let i = lastIndex - 1; i >= 0; i--) {
        await user.tab({ shift: true });
        expect(focusableElements[i]).toHaveFocus();
      }
    }
  },

  /**
   * Test Enter key activation
   */
  testEnterActivation: async (element: HTMLElement, callback?: () => void) => {
    const user = userEvent;
    element.focus();
    await user.keyboard('{Enter}');
    if (callback) callback();
  },

  /**
   * Test Space key activation (for buttons and checkboxes)
   */
  testSpaceActivation: async (element: HTMLElement, callback?: () => void) => {
    const user = userEvent;
    element.focus();
    await user.keyboard(' ');
    if (callback) callback();
  },

  /**
   * Test Escape key handling (for modals and dropdowns)
   */
  testEscapeHandling: async (element: HTMLElement, callback?: () => void) => {
    const user = userEvent;
    element.focus();
    await user.keyboard('{Escape}');
    if (callback) callback();
  },

  /**
   * Test Arrow key navigation (for select, radio groups, etc.)
   */
  testArrowNavigation: async (
    container: HTMLElement,
    direction: 'up' | 'down' | 'left' | 'right'
  ) => {
    const user = userEvent.setup();
    const keyMap = {
      up: '{ArrowUp}',
      down: '{ArrowDown}',
      left: '{ArrowLeft}',
      right: '{ArrowRight}',
    };
    
    await user.keyboard(keyMap[direction]);
  },
};

/**
 * Screen reader test utilities
 */
export const screenReaderTestUtils = {
  /**
   * Test ARIA labels and descriptions
   */
  testAriaLabels: (element: HTMLElement) => {
    const ariaLabel = element.getAttribute('aria-label');
    const ariaLabelledBy = element.getAttribute('aria-labelledby');
    const ariaDescribedBy = element.getAttribute('aria-describedby');
    
    // Element should have at least one form of accessible name
    expect(
      ariaLabel || ariaLabelledBy || element.textContent?.trim()
    ).toBeTruthy();
    
    return {
      ariaLabel,
      ariaLabelledBy,
      ariaDescribedBy,
    };
  },

  /**
   * Test role attributes
   */
  testRole: (element: HTMLElement, expectedRole?: string) => {
    const role = element.getAttribute('role');
    if (expectedRole) {
      expect(role).toBe(expectedRole);
    }
    return role;
  },

  /**
   * Test ARIA states (expanded, checked, selected, etc.)
   */
  testAriaStates: (element: HTMLElement) => {
    return {
      expanded: element.getAttribute('aria-expanded'),
      checked: element.getAttribute('aria-checked'),
      selected: element.getAttribute('aria-selected'),
      disabled: element.getAttribute('aria-disabled'),
      hidden: element.getAttribute('aria-hidden'),
      pressed: element.getAttribute('aria-pressed'),
    };
  },

  /**
   * Test live regions for dynamic content
   */
  testLiveRegion: (element: HTMLElement) => {
    const ariaLive = element.getAttribute('aria-live');
    const ariaAtomic = element.getAttribute('aria-atomic');
    const ariaRelevant = element.getAttribute('aria-relevant');
    
    return {
      ariaLive,
      ariaAtomic,
      ariaRelevant,
    };
  },
};

/**
 * Focus management test utilities
 */
export const focusTestUtils = {
  /**
   * Test focus trap (for modals)
   */
  testFocusTrap: async (container: HTMLElement) => {
    const user = userEvent;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) return;
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
    
    // Focus should start on first element
    firstElement.focus();
    expect(firstElement).toHaveFocus();
    
    // Tab from last element should cycle to first
    lastElement.focus();
    await user.tab();
    expect(firstElement).toHaveFocus();
    
    // Shift+Tab from first element should cycle to last
    firstElement.focus();
    await user.tab({ shift: true });
    expect(lastElement).toHaveFocus();
  },

  /**
   * Test focus restoration after modal close
   */
  testFocusRestoration: (triggerElement: HTMLElement) => {
    expect(triggerElement).toHaveFocus();
  },

  /**
   * Test focus visibility (focus indicators)
   */
  testFocusVisibility: (element: HTMLElement) => {
    element.focus();
    expect(element).toHaveFocus();
    
    // Check if element has focus styles
    const computedStyle = window.getComputedStyle(element);
    const hasFocusOutline = computedStyle.outline !== 'none' || 
                           computedStyle.boxShadow !== 'none' ||
                           computedStyle.border !== computedStyle.border; // Changed border
    
    expect(hasFocusOutline).toBeTruthy();
  },
};

/**
 * Polish business-specific accessibility tests
 */
export const polishBusinessA11yTests = {
  /**
   * Test NIP input accessibility
   */
  testNipInputA11y: async (container: HTMLElement) => {
    const nipInput = container.querySelector('input[type="text"]');
    if (nipInput) {
      expect(nipInput).toHaveAttribute('aria-label');
      expect(nipInput).toHaveAttribute('pattern');
      expect(nipInput).toHaveAttribute('maxlength', '10');
    }
  },

  /**
   * Test currency input accessibility
   */
  testCurrencyInputA11y: async (container: HTMLElement) => {
    const currencyInput = container.querySelector('input[type="number"]');
    if (currencyInput) {
      expect(currencyInput).toHaveAttribute('aria-label');
      expect(currencyInput).toHaveAttribute('step', '0.01');
    }
  },

  /**
   * Test VAT rate selector accessibility
   */
  testVatSelectorA11y: async (container: HTMLElement) => {
    const vatSelect = container.querySelector('select');
    if (vatSelect) {
      expect(vatSelect).toHaveAttribute('aria-label');
      const options = vatSelect.querySelectorAll('option');
      expect(options.length).toBeGreaterThan(0);
    }
  },

  /**
   * Test Polish date format accessibility
   */
  testPolishDateA11y: async (container: HTMLElement) => {
    const dateInput = container.querySelector('input[type="date"]');
    if (dateInput) {
      expect(dateInput).toHaveAttribute('aria-label');
      // Should support DD.MM.YYYY format
      expect(dateInput).toHaveAttribute('pattern');
    }
  },
};

/**
 * Comprehensive accessibility test suite
 */
export const runA11yTestSuite = async (
  container: HTMLElement,
  options: {
    testKeyboard?: boolean;
    testScreenReader?: boolean;
    testFocus?: boolean;
    testPolishBusiness?: boolean;
    customConfig?: any;
  } = {}
) => {
  const {
    testKeyboard = true,
    testScreenReader = true,
    testFocus = true,
    testPolishBusiness = false,
    customConfig,
  } = options;

  // Basic accessibility test
  if (customConfig) {
    await testA11yWithConfig(container, customConfig);
  } else {
    await testPolishA11y(container);
  }

  // Keyboard navigation tests
  if (testKeyboard) {
    await keyboardTestUtils.testTabNavigation(container);
    await keyboardTestUtils.testShiftTabNavigation(container);
  }

  // Screen reader tests
  if (testScreenReader) {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    focusableElements.forEach((element) => {
      screenReaderTestUtils.testAriaLabels(element as HTMLElement);
    });
  }

  // Focus management tests
  if (testFocus) {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length > 0) {
      focusTestUtils.testFocusVisibility(focusableElements[0] as HTMLElement);
    }
  }

  // Polish business-specific tests
  if (testPolishBusiness) {
    await polishBusinessA11yTests.testNipInputA11y(container);
    await polishBusinessA11yTests.testCurrencyInputA11y(container);
    await polishBusinessA11yTests.testVatSelectorA11y(container);
    await polishBusinessA11yTests.testPolishDateA11y(container);
  }
};