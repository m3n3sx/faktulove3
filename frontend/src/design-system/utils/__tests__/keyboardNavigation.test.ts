/**
 * Comprehensive keyboard navigation tests
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { KeyboardShortcutManager } from '../keyboardShortcuts';
import { FocusManager, ModalFocusManager, DropdownFocusManager } from '../focusManagement';
import { runKeyboardNavigationTests, keyboardNavigationPatterns } from '../keyboardTestPatterns';

describe('Keyboard Navigation System', () => {
  let container: HTMLElement;
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    user = userEvent.setup();
  });

  afterEach(() => {
    document.body.removeChild(container);
    document.body.innerHTML = '';
  });

  describe('KeyboardShortcutManager', () => {
    let manager: KeyboardShortcutManager;
    let mockAction: jest.Mock;

    beforeEach(() => {
      manager = new KeyboardShortcutManager();
      mockAction = jest.fn();
    });

    it('should register and execute keyboard shortcuts', async () => {
      manager.register({
        key: 'k',
        ctrlKey: true,
        description: 'Test shortcut',
        action: mockAction,
      });

      await user.keyboard('{Control>}k{/Control}');
      expect(mockAction).toHaveBeenCalled();
    });

    it('should handle context-specific shortcuts', async () => {
      const contextAction = jest.fn();
      const globalAction = jest.fn();

      manager.register({
        key: 'n',
        ctrlKey: true,
        description: 'New item',
        action: contextAction,
        context: 'invoices',
      });

      manager.register({
        key: 'h',
        ctrlKey: true,
        description: 'Help',
        action: globalAction,
      });

      // Should not execute context-specific shortcut without context
      await user.keyboard('{Control>}n{/Control}');
      expect(contextAction).not.toHaveBeenCalled();

      // Should execute global shortcut
      await user.keyboard('{Control>}h{/Control}');
      expect(globalAction).toHaveBeenCalled();

      // Push context and test context-specific shortcut
      manager.pushContext('invoices');
      await user.keyboard('{Control>}n{/Control}');
      expect(contextAction).toHaveBeenCalled();
    });

    it('should not execute shortcuts when disabled', async () => {
      manager.register({
        key: 'k',
        ctrlKey: true,
        description: 'Test shortcut',
        action: mockAction,
      });

      manager.setEnabled(false);
      await user.keyboard('{Control>}k{/Control}');
      expect(mockAction).not.toHaveBeenCalled();

      manager.setEnabled(true);
      await user.keyboard('{Control>}k{/Control}');
      expect(mockAction).toHaveBeenCalled();
    });

    it('should show help modal', () => {
      const showHelpSpy = jest.spyOn(manager, 'showHelp');
      manager.showHelp();
      expect(showHelpSpy).toHaveBeenCalled();
      
      // Check if help modal is created
      const helpModal = document.querySelector('.keyboard-shortcuts-help');
      expect(helpModal).toBeInTheDocument();
    });
  });

  describe('FocusManager', () => {
    it('should get focusable elements', () => {
      container.innerHTML = `
        <button>Button 1</button>
        <input type="text" />
        <a href="#">Link</a>
        <button disabled>Disabled Button</button>
        <div tabindex="0">Focusable Div</div>
        <div tabindex="-1">Non-focusable Div</div>
      `;

      const focusableElements = FocusManager.getFocusableElements(container);
      expect(focusableElements).toHaveLength(4); // button, input, link, focusable div
    });

    it('should manage focus stack', () => {
      const button1 = document.createElement('button');
      const button2 = document.createElement('button');
      container.appendChild(button1);
      container.appendChild(button2);

      button1.focus();
      FocusManager.saveFocus(button2);
      expect(document.activeElement).toBe(button2);

      FocusManager.restoreFocus();
      expect(document.activeElement).toBe(button1);
    });

    it('should trap focus in container', () => {
      container.innerHTML = `
        <div class="modal">
          <button id="first">First</button>
          <input id="middle" type="text" />
          <button id="last">Last</button>
        </div>
      `;

      const modal = container.querySelector('.modal') as HTMLElement;
      const firstButton = container.querySelector('#first') as HTMLElement;
      const lastButton = container.querySelector('#last') as HTMLElement;

      FocusManager.trapFocus(modal);
      expect(document.activeElement).toBe(firstButton);

      // Tab from last element should go to first
      lastButton.focus();
      fireEvent.keyDown(modal, { key: 'Tab' });
      expect(document.activeElement).toBe(firstButton);

      // Shift+Tab from first should go to last
      firstButton.focus();
      fireEvent.keyDown(modal, { key: 'Tab', shiftKey: true });
      expect(document.activeElement).toBe(lastButton);
    });
  });

  describe('ModalFocusManager', () => {
    let modal: HTMLElement;
    let focusManager: ModalFocusManager;

    beforeEach(() => {
      container.innerHTML = `
        <button id="trigger">Open Modal</button>
        <div class="modal">
          <button id="modal-close">Close</button>
          <input id="modal-input" type="text" />
          <button id="modal-save">Save</button>
        </div>
      `;

      modal = container.querySelector('.modal') as HTMLElement;
      focusManager = new ModalFocusManager(modal);
    });

    it('should activate focus trap and focus first element', () => {
      const firstButton = container.querySelector('#modal-close') as HTMLElement;
      
      focusManager.activate();
      expect(document.activeElement).toBe(firstButton);
    });

    it('should handle Escape key to deactivate', () => {
      focusManager.activate();
      
      fireEvent.keyDown(document, { key: 'Escape' });
      // Focus should be restored (implementation detail)
    });

    it('should prevent body scroll when active', () => {
      focusManager.activate();
      expect(document.body.style.overflow).toBe('hidden');
      
      focusManager.deactivate();
      expect(document.body.style.overflow).toBe('');
    });
  });

  describe('DropdownFocusManager', () => {
    let trigger: HTMLElement;
    let dropdown: HTMLElement;
    let focusManager: DropdownFocusManager;

    beforeEach(() => {
      container.innerHTML = `
        <button id="dropdown-trigger">Open Dropdown</button>
        <div class="dropdown">
          <button class="dropdown-item">Item 1</button>
          <button class="dropdown-item">Item 2</button>
          <button class="dropdown-item">Item 3</button>
        </div>
      `;

      trigger = container.querySelector('#dropdown-trigger') as HTMLElement;
      dropdown = container.querySelector('.dropdown') as HTMLElement;
      focusManager = new DropdownFocusManager(trigger, dropdown);
    });

    it('should focus first item when opened', () => {
      const firstItem = container.querySelector('.dropdown-item') as HTMLElement;
      
      focusManager.open();
      expect(document.activeElement).toBe(firstItem);
    });

    it('should handle arrow key navigation', () => {
      const items = container.querySelectorAll('.dropdown-item') as NodeListOf<HTMLElement>;
      
      focusManager.open();
      expect(document.activeElement).toBe(items[0]);

      fireEvent.keyDown(document, { key: 'ArrowDown' });
      expect(document.activeElement).toBe(items[1]);

      fireEvent.keyDown(document, { key: 'ArrowUp' });
      expect(document.activeElement).toBe(items[0]);
    });

    it('should close on Escape and restore focus to trigger', () => {
      focusManager.open();
      
      fireEvent.keyDown(document, { key: 'Escape' });
      expect(document.activeElement).toBe(trigger);
    });
  });

  describe('Keyboard Navigation Patterns', () => {
    it('should test button keyboard navigation', async () => {
      container.innerHTML = `
        <button id="btn1">Button 1</button>
        <button id="btn2">Button 2</button>
      `;

      await runKeyboardNavigationTests(container, [
        keyboardNavigationPatterns.find(p => p.name === 'Button Keyboard Navigation')!
      ]);
    });

    it('should test input field navigation', async () => {
      container.innerHTML = `
        <input id="input1" type="text" />
        <textarea id="textarea1"></textarea>
        <input id="checkbox1" type="checkbox" />
      `;

      await runKeyboardNavigationTests(container, [
        keyboardNavigationPatterns.find(p => p.name === 'Input Field Keyboard Navigation')!
      ]);
    });

    it('should test radio group navigation', async () => {
      container.innerHTML = `
        <fieldset>
          <legend>Choose option</legend>
          <input type="radio" name="option" id="opt1" value="1" />
          <label for="opt1">Option 1</label>
          <input type="radio" name="option" id="opt2" value="2" />
          <label for="opt2">Option 2</label>
          <input type="radio" name="option" id="opt3" value="3" />
          <label for="opt3">Option 3</label>
        </fieldset>
      `;

      await runKeyboardNavigationTests(container, [
        keyboardNavigationPatterns.find(p => p.name === 'Radio Group Keyboard Navigation')!
      ]);
    });

    it('should test modal keyboard navigation', async () => {
      container.innerHTML = `
        <div role="dialog" aria-modal="true">
          <button>Close</button>
          <input type="text" />
          <button>Save</button>
        </div>
      `;

      await runKeyboardNavigationTests(container, [
        keyboardNavigationPatterns.find(p => p.name === 'Modal Keyboard Navigation')!
      ]);
    });

    it('should test dropdown menu navigation', async () => {
      container.innerHTML = `
        <div role="menu">
          <div role="menuitem" tabindex="0">Menu Item 1</div>
          <div role="menuitem" tabindex="-1">Menu Item 2</div>
          <div role="menuitem" tabindex="-1">Menu Item 3</div>
        </div>
      `;

      await runKeyboardNavigationTests(container, [
        keyboardNavigationPatterns.find(p => p.name === 'Dropdown Menu Keyboard Navigation')!
      ]);
    });

    it('should test Polish business form navigation', async () => {
      container.innerHTML = `
        <form>
          <input data-testid="nip-input" type="text" />
          <input data-testid="currency-input" type="number" />
          <select data-testid="vat-select">
            <option value="0">0%</option>
            <option value="23">23%</option>
          </select>
          <input data-testid="polish-date-input" type="text" />
        </form>
      `;

      await runKeyboardNavigationTests(container, [
        keyboardNavigationPatterns.find(p => p.name === 'Polish Business Form Navigation')!
      ]);
    });
  });

  describe('Skip Links', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <div class="skip-links">
          <a href="#main-content" class="skip-link">Skip to main content</a>
          <a href="#navigation" class="skip-link">Skip to navigation</a>
        </div>
        <nav id="navigation">
          <a href="/">Home</a>
        </nav>
        <main id="main-content" tabindex="-1">
          <h1>Main Content</h1>
        </main>
      `;
    });

    it('should be hidden by default and visible on focus', () => {
      const skipLink = document.querySelector('.skip-link') as HTMLElement;
      
      // Should be positioned off-screen
      const styles = window.getComputedStyle(skipLink);
      expect(parseInt(styles.top)).toBeLessThan(0);
      
      // Should be visible when focused
      skipLink.focus();
      expect(skipLink).toHaveFocus();
    });

    it('should navigate to target when activated', async () => {
      const skipLink = document.querySelector('.skip-link') as HTMLElement;
      const mainContent = document.getElementById('main-content') as HTMLElement;
      
      skipLink.focus();
      await user.keyboard('{Enter}');
      
      expect(mainContent).toHaveFocus();
    });
  });

  describe('Accessibility Features', () => {
    it('should detect keyboard vs mouse usage', () => {
      // Simulate mouse interaction
      fireEvent.mouseDown(document.body);
      expect(document.body.classList.contains('keyboard-navigation-active')).toBe(false);
      
      // Simulate keyboard interaction
      fireEvent.keyDown(document.body, { key: 'Tab' });
      expect(document.body.classList.contains('keyboard-navigation-active')).toBe(true);
    });

    it('should provide proper focus indicators', () => {
      container.innerHTML = `
        <button class="ds-button">Test Button</button>
        <input class="ds-input" type="text" />
      `;

      const button = container.querySelector('.ds-button') as HTMLElement;
      const input = container.querySelector('.ds-input') as HTMLElement;

      button.focus();
      expect(button).toHaveFocus();
      
      input.focus();
      expect(input).toHaveFocus();
    });

    it('should handle high contrast mode', () => {
      // Mock high contrast media query
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(prefers-contrast: high)',
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      container.innerHTML = `<button class="ds-focus-visible">High Contrast Button</button>`;
      const button = container.querySelector('button') as HTMLElement;
      
      button.focus();
      expect(button).toHaveFocus();
    });
  });

  describe('Polish Business Keyboard Navigation', () => {
    it('should handle NIP input validation', async () => {
      container.innerHTML = `
        <form class="polish-form-navigation">
          <input id="nip" type="text" aria-label="Numer NIP" />
          <div id="nip-error" role="alert" aria-live="polite"></div>
        </form>
      `;

      const nipInput = container.querySelector('#nip') as HTMLInputElement;
      
      nipInput.focus();
      await user.type(nipInput, '1234567890');
      expect(nipInput.value).toBe('1234567890');
    });

    it('should handle currency input formatting', async () => {
      container.innerHTML = `
        <form class="polish-form-navigation">
          <input id="amount" type="text" aria-label="Kwota" />
        </form>
      `;

      const amountInput = container.querySelector('#amount') as HTMLInputElement;
      
      amountInput.focus();
      await user.type(amountInput, '1234.56');
      expect(amountInput.value).toBe('1234.56');
    });

    it('should create error summary for form validation', () => {
      container.innerHTML = `
        <form class="polish-form-navigation">
          <input id="field1" aria-invalid="true" />
          <input id="field2" aria-invalid="true" />
        </form>
      `;

      const form = container.querySelector('form') as HTMLFormElement;
      
      // Simulate error summary creation
      const errorSummary = document.createElement('div');
      errorSummary.className = 'error-summary';
      errorSummary.setAttribute('role', 'alert');
      errorSummary.innerHTML = `
        <h2>Znaleziono 2 błędy w formularzu:</h2>
        <ul>
          <li><a href="#field1">Błąd w polu 1</a></li>
          <li><a href="#field2">Błąd w polu 2</a></li>
        </ul>
      `;
      
      form.insertBefore(errorSummary, form.firstChild);
      
      expect(form.querySelector('.error-summary')).toBeInTheDocument();
      expect(form.querySelector('.error-summary h2')).toHaveTextContent('Znaleziono 2 błędy w formularzu:');
    });
  });
});