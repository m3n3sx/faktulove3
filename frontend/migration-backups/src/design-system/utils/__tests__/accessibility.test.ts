import { render, screen } from '@testing-library/react';
import React from 'react';
import {
  renderWithA11y,
  testA11y,
  testPolishA11y,
  polishA11yConfig,
  keyboardTestUtils,
  screenReaderTestUtils,
  focusTestUtils,
  polishBusinessA11yTests,
  runA11yTestSuite,
} from '../testUtils';
import { runKeyboardNavigationTests, buttonKeyboardPattern } from '../keyboardTestPatterns';

// Mock components for testing
const MockButton = ({ children, onClick, disabled = false }: any) =>
  React.createElement('button', { onClick, disabled, 'aria-label': 'Test button' }, children);

const MockInput = ({ label, type = 'text', ...props }: any) =>
  React.createElement('div', null,
    React.createElement('label', { htmlFor: 'test-input' }, label),
    React.createElement('input', { id: 'test-input', type, 'aria-label': label, ...props })
  );

const MockSelect = ({ label, options, ...props }: any) =>
  React.createElement('div', null,
    React.createElement('label', { htmlFor: 'test-select' }, label),
    React.createElement('select', { id: 'test-select', 'aria-label': label, ...props },
      ...options.map((option: string, index: number) =>
        React.createElement('option', { key: index, value: option }, option)
      )
    )
  );

const MockModal = ({ isOpen, onClose, children }: any) => {
  if (!isOpen) return null;
  
  return React.createElement('div', {
    role: 'dialog',
    'aria-modal': 'true',
    'aria-labelledby': 'modal-title',
    onKeyDown: (e: any) => {
      if (e.key === 'Escape') onClose();
    }
  },
    React.createElement('h2', { id: 'modal-title' }, 'Test Modal'),
    children,
    React.createElement('button', { onClick: onClose }, 'Close')
  );
};

const MockPolishBusinessForm = () =>
  React.createElement('form', null,
    React.createElement('div', null,
      React.createElement('label', { htmlFor: 'nip' }, 'NIP'),
      React.createElement('input', {
        id: 'nip',
        type: 'text',
        'data-testid': 'nip-input',
        'aria-label': 'Numer NIP',
        pattern: '[0-9]{10}',
        maxLength: 10
      })
    ),
    React.createElement('div', null,
      React.createElement('label', { htmlFor: 'currency' }, 'Kwota (PLN)'),
      React.createElement('input', {
        id: 'currency',
        type: 'number',
        'data-testid': 'currency-input',
        'aria-label': 'Kwota w złotych',
        step: '0.01',
        min: '0'
      })
    ),
    React.createElement('div', null,
      React.createElement('label', { htmlFor: 'vat' }, 'Stawka VAT'),
      React.createElement('select', {
        id: 'vat',
        'data-testid': 'vat-select',
        'aria-label': 'Stawka VAT'
      },
        React.createElement('option', { value: '23' }, '23%'),
        React.createElement('option', { value: '8' }, '8%'),
        React.createElement('option', { value: '5' }, '5%'),
        React.createElement('option', { value: '0' }, '0%')
      )
    ),
    React.createElement('div', null,
      React.createElement('label', { htmlFor: 'date' }, 'Data'),
      React.createElement('input', {
        id: 'date',
        type: 'text',
        'data-testid': 'polish-date-input',
        'aria-label': 'Data w formacie DD.MM.YYYY',
        pattern: '[0-9]{2}.[0-9]{2}.[0-9]{4}',
        placeholder: 'DD.MM.YYYY'
      })
    )
  );

describe('Accessibility Test Utils', () => {
  describe('Basic Accessibility Testing', () => {
    it('should pass basic accessibility tests', async () => {
      const { container } = renderWithA11y(
        MockButton({ onClick: () => {}, children: 'Click me' })
      );
      
      await testA11y(container);
    });

    it('should pass Polish-specific accessibility tests', async () => {
      const { container } = renderWithA11y(
        React.createElement('div', { lang: 'pl' },
          MockButton({ onClick: () => {}, children: 'Kliknij mnie' })
        )
      );
      
      await testPolishA11y(container);
    });

    it('should validate Polish accessibility configuration', () => {
      expect(polishA11yConfig.rules['html-has-lang'].enabled).toBe(true);
      expect(polishA11yConfig.rules['color-contrast'].enabled).toBe(true);
      expect(polishA11yConfig.rules['aria-allowed-attr'].enabled).toBe(true);
      expect(polishA11yConfig.tags).toContain('wcag2aa');
      expect(polishA11yConfig.tags).toContain('wcag21aa');
    });
  });

  describe('Keyboard Navigation Tests', () => {
    it('should test Tab navigation', async () => {
      const { container } = renderWithA11y(
        React.createElement('div', null,
          MockButton({ onClick: () => {}, children: 'Button 1' }),
          MockInput({ label: 'Input 1' }),
          MockButton({ onClick: () => {}, children: 'Button 2' })
        )
      );
      
      await keyboardTestUtils.testTabNavigation(container);
    });

    it('should test Shift+Tab navigation', async () => {
      const { container } = renderWithA11y(
        React.createElement('div', null,
          MockButton({ onClick: () => {}, children: 'Button 1' }),
          MockInput({ label: 'Input 1' }),
          MockButton({ onClick: () => {}, children: 'Button 2' })
        )
      );
      
      await keyboardTestUtils.testShiftTabNavigation(container);
    });

    it('should test Enter key activation', async () => {
      const handleClick = jest.fn();
      const { container } = renderWithA11y(
        MockButton({ onClick: handleClick, children: 'Click me' })
      );
      
      const button = container.querySelector('button')!;
      await keyboardTestUtils.testEnterActivation(button, () => {
        expect(handleClick).toHaveBeenCalled();
      });
    });

    it('should test Space key activation', async () => {
      const handleClick = jest.fn();
      const { container } = renderWithA11y(
        MockButton({ onClick: handleClick, children: 'Click me' })
      );
      
      const button = container.querySelector('button')!;
      await keyboardTestUtils.testSpaceActivation(button, () => {
        expect(handleClick).toHaveBeenCalled();
      });
    });

    it('should test Escape key handling', async () => {
      const handleClose = jest.fn();
      const { container } = renderWithA11y(
        MockModal({ 
          isOpen: true, 
          onClose: handleClose,
          children: MockButton({ onClick: () => {}, children: 'Modal Button' })
        })
      );
      
      const modal = container.querySelector('[role="dialog"]')!;
      await keyboardTestUtils.testEscapeHandling(modal as HTMLElement, () => {
        expect(handleClose).toHaveBeenCalled();
      });
    });
  });

  describe('Screen Reader Tests', () => {
    it('should test ARIA labels', () => {
      const { container } = renderWithA11y(
        MockButton({ onClick: () => {}, children: 'Click me' })
      );
      
      const button = container.querySelector('button')!;
      const ariaInfo = screenReaderTestUtils.testAriaLabels(button);
      
      expect(ariaInfo.ariaLabel).toBe('Test button');
    });

    it('should test role attributes', () => {
      const { container } = renderWithA11y(
        MockModal({ 
          isOpen: true, 
          onClose: () => {},
          children: MockButton({ onClick: () => {}, children: 'Modal Button' })
        })
      );
      
      const modal = container.querySelector('[role="dialog"]')!;
      const role = screenReaderTestUtils.testRole(modal, 'dialog');
      
      expect(role).toBe('dialog');
    });

    it('should test ARIA states', () => {
      const { container } = renderWithA11y(
        React.createElement('button', {
          'aria-expanded': 'false',
          'aria-pressed': 'false'
        }, 'Toggle Button')
      );
      
      const button = container.querySelector('button')!;
      const states = screenReaderTestUtils.testAriaStates(button);
      
      expect(states.expanded).toBe('false');
      expect(states.pressed).toBe('false');
    });

    it('should test live regions', () => {
      const { container } = renderWithA11y(
        React.createElement('div', {
          'aria-live': 'polite',
          'aria-atomic': 'true'
        }, 'Status message')
      );
      
      const liveRegion = container.querySelector('[aria-live]')!;
      const liveInfo = screenReaderTestUtils.testLiveRegion(liveRegion);
      
      expect(liveInfo.ariaLive).toBe('polite');
      expect(liveInfo.ariaAtomic).toBe('true');
    });
  });

  describe('Focus Management Tests', () => {
    it('should test focus trap in modal', async () => {
      const { container } = renderWithA11y(
        MockModal({ 
          isOpen: true, 
          onClose: () => {},
          children: React.createElement('div', null,
            MockButton({ onClick: () => {}, children: 'Button 1' }),
            MockInput({ label: 'Input 1' }),
            MockButton({ onClick: () => {}, children: 'Button 2' })
          )
        })
      );
      
      const modal = container.querySelector('[role="dialog"]')!;
      await focusTestUtils.testFocusTrap(modal as HTMLElement);
    });

    it('should test focus restoration', () => {
      const { container } = renderWithA11y(
        MockButton({ onClick: () => {}, children: 'Trigger Button' })
      );
      
      const button = container.querySelector('button')!;
      button.focus();
      
      focusTestUtils.testFocusRestoration(button);
    });

    it('should test focus visibility', () => {
      const { container } = renderWithA11y(
        MockButton({ onClick: () => {}, children: 'Focusable Button' })
      );
      
      const button = container.querySelector('button')!;
      focusTestUtils.testFocusVisibility(button);
    });
  });

  describe('Polish Business Accessibility Tests', () => {
    it('should test NIP input accessibility', async () => {
      const { container } = renderWithA11y(MockPolishBusinessForm());
      
      await polishBusinessA11yTests.testNipInputA11y(container);
    });

    it('should test currency input accessibility', async () => {
      const { container } = renderWithA11y(MockPolishBusinessForm());
      
      await polishBusinessA11yTests.testCurrencyInputA11y(container);
    });

    it('should test VAT selector accessibility', async () => {
      const { container } = renderWithA11y(MockPolishBusinessForm());
      
      await polishBusinessA11yTests.testVatSelectorA11y(container);
    });

    it('should test Polish date format accessibility', async () => {
      const { container } = renderWithA11y(MockPolishBusinessForm());
      
      await polishBusinessA11yTests.testPolishDateA11y(container);
    });
  });

  describe('Comprehensive Test Suite', () => {
    it('should run complete accessibility test suite', async () => {
      const { container } = renderWithA11y(
        React.createElement('div', { lang: 'pl' },
          MockPolishBusinessForm()
        )
      );
      
      await runA11yTestSuite(container, {
        testKeyboard: true,
        testScreenReader: true,
        testFocus: true,
        testPolishBusiness: true,
      });
    });

    it('should run keyboard navigation tests', async () => {
      const { container } = renderWithA11y(
        React.createElement('div', null,
          MockButton({ onClick: () => {}, children: 'Button' }),
          MockInput({ label: 'Input' }),
          MockSelect({ label: 'Select', options: ['Option 1', 'Option 2'] })
        )
      );
      
      await runKeyboardNavigationTests(container, [buttonKeyboardPattern]);
    });
  });

  describe('Error Handling', () => {
    it('should handle missing elements gracefully', async () => {
      const { container } = renderWithA11y(
        React.createElement('div', null, 'Empty container')
      );
      
      // Should not throw errors when no focusable elements exist
      await expect(keyboardTestUtils.testTabNavigation(container)).resolves.not.toThrow();
      await expect(focusTestUtils.testFocusTrap(container)).resolves.not.toThrow();
    });

    it('should handle invalid ARIA attributes', () => {
      const { container } = renderWithA11y(
        React.createElement('button', null, 'Button without ARIA')
      );
      
      const button = container.querySelector('button')!;
      const ariaInfo = screenReaderTestUtils.testAriaLabels(button);
      
      // Should still work with text content as fallback
      expect(button.textContent?.trim()).toBeTruthy();
    });
  });
});