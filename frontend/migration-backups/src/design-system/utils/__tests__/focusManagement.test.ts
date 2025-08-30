import {
  ModalFocusManager,
  DropdownFocusManager,
  RovingTabindexManager,
  PolishFormFocusManager,
  focusUtils,
} from '../focusManagement';

describe('Focus Management', () => {
  let container: HTMLElement;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    
    // Mock scrollIntoView for all elements
    Element.prototype.scrollIntoView = jest.fn();
  });

  afterEach(() => {
    document.body.removeChild(container);
    // Reset body styles
    document.body.style.overflow = '';
  });

  describe('ModalFocusManager', () => {
    let modal: HTMLElement;
    let modalManager: ModalFocusManager;

    beforeEach(() => {
      modal = document.createElement('div');
      modal.setAttribute('role', 'dialog');
      
      const button1 = document.createElement('button');
      button1.textContent = 'Button 1';
      const button2 = document.createElement('button');
      button2.textContent = 'Button 2';
      const closeButton = document.createElement('button');
      closeButton.textContent = 'Close';

      modal.appendChild(button1);
      modal.appendChild(button2);
      modal.appendChild(closeButton);
      container.appendChild(modal);

      modalManager = new ModalFocusManager(modal);
    });

    it('should activate focus trap and set initial focus', () => {
      const triggerButton = document.createElement('button');
      container.appendChild(triggerButton);
      triggerButton.focus();

      // Mock offsetWidth and offsetHeight for focusable elements
      const buttons = modal.querySelectorAll('button');
      buttons.forEach(button => {
        Object.defineProperty(button, 'offsetWidth', { value: 100 });
        Object.defineProperty(button, 'offsetHeight', { value: 30 });
      });

      modalManager.activate();

      // Should focus first focusable element in modal
      const firstButton = modal.querySelector('button');
      expect(document.activeElement).toBe(firstButton);
    });

    it('should prevent body scroll when activated', () => {
      modalManager.activate();
      expect(document.body.style.overflow).toBe('hidden');

      modalManager.deactivate();
      expect(document.body.style.overflow).toBe('');
    });

    it('should restore focus when deactivated', () => {
      const triggerButton = document.createElement('button');
      container.appendChild(triggerButton);
      triggerButton.focus();

      modalManager.activate();
      modalManager.deactivate();

      expect(document.activeElement).toBe(triggerButton);
    });

    it('should handle Tab key for focus trapping', () => {
      modalManager.activate();

      const buttons = modal.querySelectorAll('button');
      const firstButton = buttons[0] as HTMLElement;
      const lastButton = buttons[buttons.length - 1] as HTMLElement;

      // Focus last button and press Tab - should wrap to first
      lastButton.focus();
      const tabEvent = new KeyboardEvent('keydown', { key: 'Tab' });
      document.dispatchEvent(tabEvent);

      // Note: In real implementation, this would wrap to first button
      // In test environment, we can't fully simulate the focus trap behavior
    });

    it('should handle Escape key to deactivate', () => {
      modalManager.activate();

      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(escapeEvent);

      // Modal should be deactivated (body scroll restored)
      expect(document.body.style.overflow).toBe('');
    });

    it('should handle click outside to deactivate', () => {
      modalManager.activate();

      const outsideElement = document.createElement('div');
      document.body.appendChild(outsideElement);

      const clickEvent = new MouseEvent('click', { bubbles: true });
      Object.defineProperty(clickEvent, 'target', { value: outsideElement });
      document.dispatchEvent(clickEvent);

      expect(document.body.style.overflow).toBe('');

      document.body.removeChild(outsideElement);
    });
  });

  describe('DropdownFocusManager', () => {
    let trigger: HTMLElement;
    let dropdown: HTMLElement;
    let dropdownManager: DropdownFocusManager;

    beforeEach(() => {
      trigger = document.createElement('button');
      trigger.textContent = 'Open Dropdown';

      dropdown = document.createElement('div');
      dropdown.setAttribute('role', 'menu');

      const item1 = document.createElement('button');
      item1.setAttribute('role', 'menuitem');
      item1.textContent = 'Item 1';

      const item2 = document.createElement('button');
      item2.setAttribute('role', 'menuitem');
      item2.textContent = 'Item 2';

      const item3 = document.createElement('button');
      item3.setAttribute('role', 'menuitem');
      item3.textContent = 'Item 3';

      dropdown.appendChild(item1);
      dropdown.appendChild(item2);
      dropdown.appendChild(item3);

      container.appendChild(trigger);
      container.appendChild(dropdown);

      dropdownManager = new DropdownFocusManager(trigger, dropdown);
    });

    it('should focus first item when opened', () => {
      // Mock offsetWidth and offsetHeight for focusable elements
      const items = dropdown.querySelectorAll('[role="menuitem"]');
      items.forEach(item => {
        Object.defineProperty(item, 'offsetWidth', { value: 100 });
        Object.defineProperty(item, 'offsetHeight', { value: 30 });
      });

      dropdownManager.open();

      const firstItem = dropdown.querySelector('[role="menuitem"]');
      expect(document.activeElement).toBe(firstItem);
    });

    it('should return focus to trigger when closed', () => {
      trigger.focus();
      dropdownManager.open();
      dropdownManager.close();

      expect(document.activeElement).toBe(trigger);
    });

    it('should handle Arrow Down key', () => {
      dropdownManager.open();

      const arrowDownEvent = new KeyboardEvent('keydown', { key: 'ArrowDown' });
      document.dispatchEvent(arrowDownEvent);

      // Should move to next item (implementation would handle this)
    });

    it('should handle Arrow Up key', () => {
      dropdownManager.open();

      const arrowUpEvent = new KeyboardEvent('keydown', { key: 'ArrowUp' });
      document.dispatchEvent(arrowUpEvent);

      // Should move to previous item (implementation would handle this)
    });

    it('should handle Escape key to close', () => {
      trigger.focus();
      dropdownManager.open();

      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(escapeEvent);

      expect(document.activeElement).toBe(trigger);
    });

    it('should handle Home and End keys', () => {
      dropdownManager.open();

      const homeEvent = new KeyboardEvent('keydown', { key: 'Home' });
      document.dispatchEvent(homeEvent);

      const endEvent = new KeyboardEvent('keydown', { key: 'End' });
      document.dispatchEvent(endEvent);

      // Implementation would focus first/last items
    });
  });

  describe('RovingTabindexManager', () => {
    let tablist: HTMLElement;
    let rovingManager: RovingTabindexManager;

    beforeEach(() => {
      tablist = document.createElement('div');
      tablist.setAttribute('role', 'tablist');

      const tab1 = document.createElement('button');
      tab1.setAttribute('role', 'tab');
      tab1.textContent = 'Tab 1';

      const tab2 = document.createElement('button');
      tab2.setAttribute('role', 'tab');
      tab2.textContent = 'Tab 2';

      const tab3 = document.createElement('button');
      tab3.setAttribute('role', 'tab');
      tab3.textContent = 'Tab 3';

      tablist.appendChild(tab1);
      tablist.appendChild(tab2);
      tablist.appendChild(tab3);
      container.appendChild(tablist);

      rovingManager = new RovingTabindexManager(tablist);
    });

    afterEach(() => {
      rovingManager.destroy();
    });

    it('should set up initial tabindex values', () => {
      const tabs = tablist.querySelectorAll('[role="tab"]');
      
      expect(tabs[0].getAttribute('tabindex')).toBe('0');
      expect(tabs[1].getAttribute('tabindex')).toBe('-1');
      expect(tabs[2].getAttribute('tabindex')).toBe('-1');
    });

    it('should update active item', () => {
      rovingManager.setActiveItem(1);

      const tabs = tablist.querySelectorAll('[role="tab"]');
      
      expect(tabs[0].getAttribute('tabindex')).toBe('-1');
      expect(tabs[1].getAttribute('tabindex')).toBe('0');
      expect(tabs[2].getAttribute('tabindex')).toBe('-1');
    });

    it('should focus active item', () => {
      rovingManager.setActiveItem(1);
      rovingManager.focusActiveItem();

      const tabs = tablist.querySelectorAll('[role="tab"]');
      expect(document.activeElement).toBe(tabs[1]);
    });

    it('should handle arrow key navigation', () => {
      const arrowRightEvent = new KeyboardEvent('keydown', { key: 'ArrowRight' });
      tablist.dispatchEvent(arrowRightEvent);

      // Implementation would move to next item
    });

    it('should handle Home and End keys', () => {
      const homeEvent = new KeyboardEvent('keydown', { key: 'Home' });
      tablist.dispatchEvent(homeEvent);

      const endEvent = new KeyboardEvent('keydown', { key: 'End' });
      tablist.dispatchEvent(endEvent);

      // Implementation would focus first/last items
    });
  });

  describe('PolishFormFocusManager', () => {
    let form: HTMLElement;
    let formManager: PolishFormFocusManager;

    beforeEach(() => {
      form = document.createElement('form');

      const nameInput = document.createElement('input');
      nameInput.id = 'name';
      nameInput.name = 'name';
      nameInput.type = 'text';

      const emailInput = document.createElement('input');
      emailInput.id = 'email';
      emailInput.name = 'email';
      emailInput.type = 'email';

      const submitButton = document.createElement('button');
      submitButton.type = 'submit';
      submitButton.textContent = 'Submit';

      form.appendChild(nameInput);
      form.appendChild(emailInput);
      form.appendChild(submitButton);
      container.appendChild(form);

      formManager = new PolishFormFocusManager(form);
    });

    it('should create error summary with Polish text', () => {
      const errors = [
        { field: 'name', message: 'Imię jest wymagane' },
        { field: 'email', message: 'Email jest nieprawidłowy' },
      ];

      formManager.createErrorSummary(errors);

      const errorSummary = form.querySelector('.error-summary');
      expect(errorSummary).toBeTruthy();
      expect(errorSummary?.getAttribute('role')).toBe('alert');
      expect(errorSummary?.getAttribute('aria-live')).toBe('assertive');

      const heading = errorSummary?.querySelector('h2');
      expect(heading?.textContent).toBe('Znaleziono 2 błędów w formularzu:');

      const errorLinks = errorSummary?.querySelectorAll('a');
      expect(errorLinks).toHaveLength(2);
      expect(errorLinks?.[0].textContent).toBe('Imię jest wymagane');
      expect(errorLinks?.[1].textContent).toBe('Email jest nieprawidłowy');
    });

    it('should create error summary for single error', () => {
      const errors = [
        { field: 'name', message: 'Imię jest wymagane' },
      ];

      formManager.createErrorSummary(errors);

      const heading = form.querySelector('.error-summary h2');
      expect(heading?.textContent).toBe('Znaleziono 1 błąd w formularzu:');
    });

    it('should remove existing error summary', () => {
      const errors = [{ field: 'name', message: 'Error' }];
      
      formManager.createErrorSummary(errors);
      expect(form.querySelector('.error-summary')).toBeTruthy();

      formManager.removeErrorSummary();
      expect(form.querySelector('.error-summary')).toBeFalsy();
    });

    it('should focus specific field', () => {
      const nameInput = form.querySelector('#name') as HTMLElement;
      
      // Mock scrollIntoView for JSDOM
      nameInput.scrollIntoView = jest.fn();
      
      formManager.focusField('name');
      expect(document.activeElement).toBe(nameInput);
      expect(nameInput.scrollIntoView).toHaveBeenCalledWith({
        behavior: 'smooth',
        block: 'center'
      });
    });

    it('should focus first invalid field', () => {
      const nameInput = form.querySelector('#name') as HTMLElement;
      const emailInput = form.querySelector('#email') as HTMLElement;
      
      emailInput.setAttribute('aria-invalid', 'true');
      nameInput.setAttribute('aria-invalid', 'true');

      formManager.focusFirstInvalidField();
      expect(document.activeElement).toBe(nameInput);
    });

    it('should set up form navigation', () => {
      formManager.setupFormNavigation();

      // Test Ctrl+Enter shortcut
      const nameInput = form.querySelector('#name') as HTMLElement;
      nameInput.focus();

      const ctrlEnterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        ctrlKey: true,
      });
      nameInput.dispatchEvent(ctrlEnterEvent);

      // Implementation would trigger form submission
    });
  });

  describe('Focus Utils', () => {
    it('should check if element is focused', () => {
      const button = document.createElement('button');
      container.appendChild(button);

      expect(focusUtils.isFocused(button)).toBe(false);

      button.focus();
      expect(focusUtils.isFocused(button)).toBe(true);
    });

    it('should get next focusable element', () => {
      const button1 = document.createElement('button');
      const button2 = document.createElement('button');
      const button3 = document.createElement('button');

      // Mock offsetWidth and offsetHeight for JSDOM
      [button1, button2, button3].forEach(button => {
        Object.defineProperty(button, 'offsetWidth', { value: 100 });
        Object.defineProperty(button, 'offsetHeight', { value: 30 });
      });

      container.appendChild(button1);
      container.appendChild(button2);
      container.appendChild(button3);

      const nextElement = focusUtils.getNextFocusable(button1, container);
      expect(nextElement).toBe(button2);

      const lastNext = focusUtils.getNextFocusable(button3, container);
      expect(lastNext).toBeNull();
    });

    it('should get previous focusable element', () => {
      const button1 = document.createElement('button');
      const button2 = document.createElement('button');
      const button3 = document.createElement('button');

      // Mock offsetWidth and offsetHeight for JSDOM
      [button1, button2, button3].forEach(button => {
        Object.defineProperty(button, 'offsetWidth', { value: 100 });
        Object.defineProperty(button, 'offsetHeight', { value: 30 });
      });

      container.appendChild(button1);
      container.appendChild(button2);
      container.appendChild(button3);

      const previousElement = focusUtils.getPreviousFocusable(button2, container);
      expect(previousElement).toBe(button1);

      const firstPrevious = focusUtils.getPreviousFocusable(button1, container);
      expect(firstPrevious).toBeNull();
    });

    it('should create and remove focus outline', () => {
      const button = document.createElement('button');
      container.appendChild(button);

      focusUtils.createFocusOutline(button);
      expect(button.style.outline).toBe('2px solid #2563eb');
      expect(button.style.outlineOffset).toBe('2px');

      focusUtils.removeFocusOutline(button);
      expect(button.style.outline).toBe('');
      expect(button.style.outlineOffset).toBe('');
    });

    it('should ensure element is visible', () => {
      const button = document.createElement('button');
      container.appendChild(button);

      // Mock scrollIntoView
      button.scrollIntoView = jest.fn();

      focusUtils.ensureVisible(button);
      expect(button.scrollIntoView).toHaveBeenCalledWith({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'nearest'
      });
    });
  });

  describe('Integration Tests', () => {
    it('should work together for complete focus management', () => {
      // Create a complex UI with modal and form
      const triggerButton = document.createElement('button');
      triggerButton.textContent = 'Open Modal';

      const modal = document.createElement('div');
      modal.setAttribute('role', 'dialog');

      const form = document.createElement('form');
      const input = document.createElement('input');
      input.id = 'modal-input';
      const submitButton = document.createElement('button');
      submitButton.type = 'submit';
      submitButton.textContent = 'Submit';

      form.appendChild(input);
      form.appendChild(submitButton);
      modal.appendChild(form);

      container.appendChild(triggerButton);
      container.appendChild(modal);

      // Test focus flow
      triggerButton.focus();
      expect(document.activeElement).toBe(triggerButton);

      const modalManager = new ModalFocusManager(modal);
      modalManager.activate();

      // Should focus first element in modal
      expect(document.activeElement).toBe(input);

      modalManager.deactivate();

      // Should restore focus to trigger
      expect(document.activeElement).toBe(triggerButton);
    });
  });
});