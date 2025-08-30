import userEvent from '@testing-library/user-event';

/**
 * Keyboard navigation test patterns for different component types
 */

export interface KeyboardTestPattern {
  name: string;
  description: string;
  test: (container: HTMLElement) => Promise<void>;
}

/**
 * Button keyboard navigation pattern
 */
export const buttonKeyboardPattern: KeyboardTestPattern = {
  name: 'Button Keyboard Navigation',
  description: 'Tests Enter and Space key activation for buttons',
  test: async (container: HTMLElement) => {
    const user = userEvent;
    const buttons = container.querySelectorAll('button');
    
    for (const button of Array.from(buttons)) {
      // Test Enter key activation
      button.focus();
      expect(button).toHaveFocus();
      
      const clickHandler = jest.fn();
      button.addEventListener('click', clickHandler);
      
      await user.keyboard('{Enter}');
      expect(clickHandler).toHaveBeenCalled();
      
      // Test Space key activation
      clickHandler.mockClear();
      await user.keyboard(' ');
      expect(clickHandler).toHaveBeenCalled();
      
      button.removeEventListener('click', clickHandler);
    }
  },
};

/**
 * Input field keyboard navigation pattern
 */
export const inputKeyboardPattern: KeyboardTestPattern = {
  name: 'Input Field Keyboard Navigation',
  description: 'Tests keyboard navigation and input for form fields',
  test: async (container: HTMLElement) => {
    const user = userEvent;
    const inputs = container.querySelectorAll('input, textarea');
    
    for (const input of Array.from(inputs)) {
      const element = input as HTMLInputElement | HTMLTextAreaElement;
      
      // Test focus
      element.focus();
      expect(element).toHaveFocus();
      
      // Test typing
      if (element.type !== 'checkbox' && element.type !== 'radio') {
        await user.clear(element);
        await user.type(element, 'test input');
        expect(element.value).toBe('test input');
      }
      
      // Test Tab to next element
      await user.tab();
    }
  },
};

/**
 * Select dropdown keyboard navigation pattern
 */
export const selectKeyboardPattern: KeyboardTestPattern = {
  name: 'Select Dropdown Keyboard Navigation',
  description: 'Tests arrow key navigation and selection in dropdowns',
  test: async (container: HTMLElement) => {
    const user = userEvent;
    const selects = container.querySelectorAll('select');
    
    for (const select of Array.from(selects)) {
      select.focus();
      expect(select).toHaveFocus();
      
      const options = select.querySelectorAll('option');
      if (options.length > 1) {
        // Test arrow down navigation
        await user.keyboard('{ArrowDown}');
        
        // Test arrow up navigation
        await user.keyboard('{ArrowUp}');
        
        // Test Enter to select
        await user.keyboard('{Enter}');
      }
    }
  },
};

/**
 * Radio group keyboard navigation pattern
 */
export const radioGroupKeyboardPattern: KeyboardTestPattern = {
  name: 'Radio Group Keyboard Navigation',
  description: 'Tests arrow key navigation within radio groups',
  test: async (container: HTMLElement) => {
    const user = userEvent;
    const radioGroups = new Map<string, HTMLInputElement[]>();
    
    // Group radio buttons by name
    const radios = container.querySelectorAll('input[type="radio"]');
    radios.forEach((radio) => {
      const input = radio as HTMLInputElement;
      const name = input.name;
      if (!radioGroups.has(name)) {
        radioGroups.set(name, []);
      }
      radioGroups.get(name)!.push(input);
    });
    
    // Test each radio group
    for (const [name, group] of Array.from(radioGroups)) {
      if (group.length > 1) {
        // Focus first radio
        group[0].focus();
        expect(group[0]).toHaveFocus();
        
        // Test arrow key navigation
        await user.keyboard('{ArrowDown}');
        expect(group[1]).toHaveFocus();
        expect(group[1]).toBeChecked();
        
        await user.keyboard('{ArrowUp}');
        expect(group[0]).toHaveFocus();
        expect(group[0]).toBeChecked();
      }
    }
  },
};

/**
 * Checkbox keyboard navigation pattern
 */
export const checkboxKeyboardPattern: KeyboardTestPattern = {
  name: 'Checkbox Keyboard Navigation',
  description: 'Tests Space key toggle for checkboxes',
  test: async (container: HTMLElement) => {
    const user = userEvent;
    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    
    for (const checkbox of Array.from(checkboxes)) {
      const input = checkbox as HTMLInputElement;
      
      input.focus();
      expect(input).toHaveFocus();
      
      const initialChecked = input.checked;
      
      // Test Space key toggle
      await user.keyboard(' ');
      expect(input.checked).toBe(!initialChecked);
      
      // Test again to toggle back
      await user.keyboard(' ');
      expect(input.checked).toBe(initialChecked);
    }
  },
};

/**
 * Modal keyboard navigation pattern
 */
export const modalKeyboardPattern: KeyboardTestPattern = {
  name: 'Modal Keyboard Navigation',
  description: 'Tests focus trap and Escape key handling in modals',
  test: async (container: HTMLElement) => {
    const user = userEvent;
    const modal = container.querySelector('[role="dialog"]');
    
    if (!modal) return;
    
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) return;
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
    
    // Test initial focus
    firstElement.focus();
    expect(firstElement).toHaveFocus();
    
    // Test focus trap - Tab from last element should go to first
    lastElement.focus();
    await user.tab();
    expect(firstElement).toHaveFocus();
    
    // Test reverse focus trap - Shift+Tab from first should go to last
    firstElement.focus();
    await user.tab({ shift: true });
    expect(lastElement).toHaveFocus();
    
    // Test Escape key handling
    const escapeHandler = jest.fn();
    modal.addEventListener('keydown', (e) => {
      if ((e as KeyboardEvent).key === 'Escape') escapeHandler();
    });
    
    await user.keyboard('{Escape}');
    expect(escapeHandler).toHaveBeenCalled();
    
    modal.removeEventListener('keydown', escapeHandler);
  },
};

/**
 * Dropdown menu keyboard navigation pattern
 */
export const dropdownKeyboardPattern: KeyboardTestPattern = {
  name: 'Dropdown Menu Keyboard Navigation',
  description: 'Tests arrow key navigation and Escape handling in dropdown menus',
  test: async (container: HTMLElement) => {
    const user = userEvent;
    const dropdown = container.querySelector('[role="menu"]');
    
    if (!dropdown) return;
    
    const menuItems = dropdown.querySelectorAll('[role="menuitem"]');
    
    if (menuItems.length === 0) return;
    
    // Test arrow down navigation
    (menuItems[0] as HTMLElement).focus();
    expect(menuItems[0]).toHaveFocus();
    
    if (menuItems.length > 1) {
      await user.keyboard('{ArrowDown}');
      expect(menuItems[1]).toHaveFocus();
      
      // Test arrow up navigation
      await user.keyboard('{ArrowUp}');
      expect(menuItems[0]).toHaveFocus();
    }
    
    // Test Home key (first item)
    await user.keyboard('{Home}');
    expect(menuItems[0]).toHaveFocus();
    
    // Test End key (last item)
    await user.keyboard('{End}');
    expect(menuItems[menuItems.length - 1]).toHaveFocus();
    
    // Test Escape key
    const escapeHandler = jest.fn();
    dropdown.addEventListener('keydown', (e) => {
      if ((e as KeyboardEvent).key === 'Escape') escapeHandler();
    });
    
    await user.keyboard('{Escape}');
    expect(escapeHandler).toHaveBeenCalled();
    
    dropdown.removeEventListener('keydown', escapeHandler);
  },
};

/**
 * Tab navigation pattern for complex components
 */
export const tabNavigationPattern: KeyboardTestPattern = {
  name: 'Tab Navigation Pattern',
  description: 'Tests sequential Tab navigation through all focusable elements',
  test: async (container: HTMLElement) => {
    const user = userEvent;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) return;
    
    // Start from first element
    (focusableElements[0] as HTMLElement).focus();
    expect(focusableElements[0]).toHaveFocus();
    
    // Tab through all elements
    for (let i = 1; i < focusableElements.length; i++) {
      await user.tab();
      expect(focusableElements[i]).toHaveFocus();
    }
    
    // Test reverse navigation with Shift+Tab
    for (let i = focusableElements.length - 2; i >= 0; i--) {
      await user.tab({ shift: true });
      expect(focusableElements[i]).toHaveFocus();
    }
  },
};

/**
 * Polish business form keyboard navigation pattern
 */
export const polishBusinessFormPattern: KeyboardTestPattern = {
  name: 'Polish Business Form Navigation',
  description: 'Tests keyboard navigation for Polish business-specific form elements',
  test: async (container: HTMLElement) => {
    const user = userEvent;
    
    // Test NIP input
    const nipInput = container.querySelector('input[data-testid="nip-input"]');
    if (nipInput) {
      (nipInput as HTMLInputElement).focus();
      expect(nipInput).toHaveFocus();
      await user.clear(nipInput as HTMLInputElement);
      await user.type(nipInput as HTMLInputElement, '1234567890');
      expect((nipInput as HTMLInputElement).value).toBe('1234567890');
    }
    
    // Test currency input
    const currencyInput = container.querySelector('input[data-testid="currency-input"]');
    if (currencyInput) {
      (currencyInput as HTMLInputElement).focus();
      expect(currencyInput).toHaveFocus();
      await user.clear(currencyInput as HTMLInputElement);
      await user.type(currencyInput as HTMLInputElement, '123.45');
      expect((currencyInput as HTMLInputElement).value).toBe('123.45');
    }
    
    // Test VAT rate selector
    const vatSelect = container.querySelector('select[data-testid="vat-select"]');
    if (vatSelect) {
      (vatSelect as HTMLSelectElement).focus();
      expect(vatSelect).toHaveFocus();
      await user.keyboard('{ArrowDown}');
      await user.keyboard('{Enter}');
    }
    
    // Test Polish date input
    const dateInput = container.querySelector('input[data-testid="polish-date-input"]');
    if (dateInput) {
      (dateInput as HTMLInputElement).focus();
      expect(dateInput).toHaveFocus();
      await user.clear(dateInput as HTMLInputElement);
      await user.type(dateInput as HTMLInputElement, '31.12.2023');
    }
  },
};

/**
 * All keyboard navigation patterns
 */
export const keyboardNavigationPatterns: KeyboardTestPattern[] = [
  buttonKeyboardPattern,
  inputKeyboardPattern,
  selectKeyboardPattern,
  radioGroupKeyboardPattern,
  checkboxKeyboardPattern,
  modalKeyboardPattern,
  dropdownKeyboardPattern,
  tabNavigationPattern,
  polishBusinessFormPattern,
];

/**
 * Run all keyboard navigation tests for a component
 */
export const runKeyboardNavigationTests = async (
  container: HTMLElement,
  patterns: KeyboardTestPattern[] = keyboardNavigationPatterns
) => {
  for (const pattern of patterns) {
    try {
      await pattern.test(container);
    } catch (error) {
      console.error(`Keyboard navigation test failed for ${pattern.name}:`, error);
      throw error;
    }
  }
};

/**
 * Run specific keyboard navigation test by name
 */
export const runKeyboardNavigationTest = async (
  container: HTMLElement,
  patternName: string
) => {
  const pattern = keyboardNavigationPatterns.find(p => p.name === patternName);
  if (!pattern) {
    throw new Error(`Keyboard navigation pattern "${patternName}" not found`);
  }
  
  await pattern.test(container);
};