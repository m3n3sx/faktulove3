import {
  ARIA_ROLES,
  ARIA_PROPERTIES,
  ARIA_LIVE_REGIONS,
  generateAriaAttributes,
  polishAriaLabels,
  ScreenReaderAnnouncer,
  FocusManager,
  ariaUtils,
} from '../ariaUtils';

// Mock DOM methods for testing
Object.defineProperty(window, 'getComputedStyle', {
  value: () => ({
    outline: 'none',
    boxShadow: 'none',
    border: '1px solid black',
  }),
});

describe('ARIA Utils', () => {
  let container: HTMLElement;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
    // Clean up any live regions
    const announcer = ScreenReaderAnnouncer.getInstance();
    announcer.cleanup();
    FocusManager.clearStacks();
  });

  describe('ARIA Constants', () => {
    it('should have correct ARIA roles', () => {
      expect(ARIA_ROLES.BUTTON).toBe('button');
      expect(ARIA_ROLES.DIALOG).toBe('dialog');
      expect(ARIA_ROLES.COMBOBOX).toBe('combobox');
      expect(ARIA_ROLES.ALERT).toBe('alert');
    });

    it('should have correct ARIA properties', () => {
      expect(ARIA_PROPERTIES.LABEL).toBe('aria-label');
      expect(ARIA_PROPERTIES.EXPANDED).toBe('aria-expanded');
      expect(ARIA_PROPERTIES.LIVE).toBe('aria-live');
      expect(ARIA_PROPERTIES.DESCRIBEDBY).toBe('aria-describedby');
    });

    it('should have correct live region values', () => {
      expect(ARIA_LIVE_REGIONS.POLITE).toBe('polite');
      expect(ARIA_LIVE_REGIONS.ASSERTIVE).toBe('assertive');
      expect(ARIA_LIVE_REGIONS.OFF).toBe('off');
    });
  });

  describe('Generate ARIA Attributes', () => {
    it('should generate button attributes correctly', () => {
      const attrs = generateAriaAttributes.button({
        label: 'Test Button',
        pressed: true,
        expanded: false,
        hasPopup: 'MENU',
        disabled: false,
      });

      expect(attrs['aria-label']).toBe('Test Button');
      expect(attrs['aria-pressed']).toBe('true');
      expect(attrs['aria-expanded']).toBe('false');
      expect(attrs['aria-haspopup']).toBe('menu');
      expect(attrs['aria-disabled']).toBeUndefined();
    });

    it('should generate input attributes correctly', () => {
      const attrs = generateAriaAttributes.input({
        label: 'Test Input',
        required: true,
        invalid: true,
        errorMessage: 'error-msg',
        placeholder: 'Enter text',
      });

      expect(attrs['aria-label']).toBe('Test Input');
      expect(attrs['aria-required']).toBe('true');
      expect(attrs['aria-invalid']).toBe('true');
      expect(attrs['aria-errormessage']).toBe('error-msg');
      expect(attrs['aria-placeholder']).toBe('Enter text');
    });

    it('should generate select attributes correctly', () => {
      const attrs = generateAriaAttributes.select({
        label: 'Test Select',
        expanded: true,
        hasPopup: true,
        controls: 'listbox-id',
        activeDescendant: 'option-1',
      });

      expect(attrs.role).toBe('combobox');
      expect(attrs['aria-label']).toBe('Test Select');
      expect(attrs['aria-expanded']).toBe('true');
      expect(attrs['aria-haspopup']).toBe('listbox');
      expect(attrs['aria-controls']).toBe('listbox-id');
      expect(attrs['aria-activedescendant']).toBe('option-1');
    });

    it('should generate modal attributes correctly', () => {
      const attrs = generateAriaAttributes.modal({
        labelledBy: 'modal-title',
        describedBy: 'modal-desc',
        modal: true,
      });

      expect(attrs.role).toBe('dialog');
      expect(attrs['aria-labelledby']).toBe('modal-title');
      expect(attrs['aria-describedby']).toBe('modal-desc');
      expect(attrs['aria-modal']).toBe('true');
    });

    it('should generate live region attributes correctly', () => {
      const attrs = generateAriaAttributes.liveRegion({
        live: 'ASSERTIVE',
        atomic: true,
        relevant: 'additions text',
        busy: false,
      });

      expect(attrs['aria-live']).toBe('assertive');
      expect(attrs['aria-atomic']).toBe('true');
      expect(attrs['aria-relevant']).toBe('additions text');
      expect(attrs['aria-busy']).toBe('false');
    });
  });

  describe('Polish ARIA Labels', () => {
    it('should have Polish translations for common actions', () => {
      expect(polishAriaLabels.CLOSE).toBe('Zamknij');
      expect(polishAriaLabels.SAVE).toBe('Zapisz');
      expect(polishAriaLabels.CANCEL).toBe('Anuluj');
      expect(polishAriaLabels.DELETE).toBe('Usuń');
    });

    it('should have Polish translations for business terms', () => {
      expect(polishAriaLabels.NIP_INPUT).toBe('Numer NIP');
      expect(polishAriaLabels.CURRENCY_INPUT).toBe('Kwota w złotych');
      expect(polishAriaLabels.VAT_RATE).toBe('Stawka VAT');
      expect(polishAriaLabels.INVOICE_NUMBER).toBe('Numer faktury');
    });

    it('should have Polish translations for status messages', () => {
      expect(polishAriaLabels.LOADING).toBe('Ładowanie...');
      expect(polishAriaLabels.ERROR).toBe('Błąd');
      expect(polishAriaLabels.SUCCESS).toBe('Sukces');
      expect(polishAriaLabels.WARNING).toBe('Ostrzeżenie');
    });
  });

  describe('Screen Reader Announcer', () => {
    let announcer: ScreenReaderAnnouncer;

    beforeEach(() => {
      // Clear any existing live regions
      const existingRegions = document.querySelectorAll('[aria-live]');
      existingRegions.forEach(region => region.remove());
      
      // Reset singleton
      (ScreenReaderAnnouncer as any).instance = null;
      announcer = ScreenReaderAnnouncer.getInstance();
    });

    afterEach(() => {
      announcer.clear();
      announcer.cleanup();
    });

    it('should create live regions on initialization', () => {
      const politeRegion = document.querySelector('[aria-live="polite"]');
      const assertiveRegion = document.querySelector('[aria-live="assertive"]');

      expect(politeRegion).toBeTruthy();
      expect(assertiveRegion).toBeTruthy();
    });

    it('should announce polite messages', () => {
      announcer.announcePolite('Test polite message');
      
      const politeRegion = document.querySelector('[aria-live="polite"]');
      expect(politeRegion?.textContent).toBe('Test polite message');
    });

    it('should announce assertive messages', () => {
      announcer.announceAssertive('Test assertive message');
      
      const assertiveRegion = document.querySelector('[aria-live="assertive"]');
      expect(assertiveRegion?.textContent).toBe('Test assertive message');
    });

    it('should announce errors with Polish prefix', () => {
      announcer.announceError('Test error message');
      
      const assertiveRegion = document.querySelector('[aria-live="assertive"]');
      expect(assertiveRegion?.textContent).toBe('Błąd: Test error message');
    });

    it('should announce success with Polish prefix', () => {
      announcer.announceSuccess('Test success message');
      
      const politeRegion = document.querySelector('[aria-live="polite"]');
      expect(politeRegion?.textContent).toBe('Sukces: Test success message');
    });

    it('should announce loading state', () => {
      announcer.announceLoading();
      
      const politeRegion = document.querySelector('[aria-live="polite"]');
      expect(politeRegion?.textContent).toBe('Ładowanie...');
    });

    it('should clear announcements', () => {
      announcer.announcePolite('Test message');
      announcer.clear();
      
      const politeRegion = document.querySelector('[aria-live="polite"]');
      const assertiveRegion = document.querySelector('[aria-live="assertive"]');
      
      expect(politeRegion?.textContent).toBe('');
      expect(assertiveRegion?.textContent).toBe('');
    });
  });

  describe('Focus Manager', () => {
    it('should save and restore focus', () => {
      const button1 = document.createElement('button');
      const button2 = document.createElement('button');
      container.appendChild(button1);
      container.appendChild(button2);

      button1.focus();
      expect(document.activeElement).toBe(button1);

      FocusManager.saveFocus(button2);
      expect(document.activeElement).toBe(button2);

      FocusManager.restoreFocus();
      expect(document.activeElement).toBe(button1);
    });

    it('should get focusable elements', () => {
      const button = document.createElement('button');
      const input = document.createElement('input');
      const disabledButton = document.createElement('button');
      disabledButton.disabled = true;
      const hiddenInput = document.createElement('input');
      hiddenInput.style.display = 'none';

      // Mock offsetWidth and offsetHeight for JSDOM
      Object.defineProperty(button, 'offsetWidth', { value: 100 });
      Object.defineProperty(button, 'offsetHeight', { value: 30 });
      Object.defineProperty(input, 'offsetWidth', { value: 200 });
      Object.defineProperty(input, 'offsetHeight', { value: 30 });
      Object.defineProperty(disabledButton, 'offsetWidth', { value: 100 });
      Object.defineProperty(disabledButton, 'offsetHeight', { value: 30 });
      Object.defineProperty(hiddenInput, 'offsetWidth', { value: 0 });
      Object.defineProperty(hiddenInput, 'offsetHeight', { value: 0 });

      container.appendChild(button);
      container.appendChild(input);
      container.appendChild(disabledButton);
      container.appendChild(hiddenInput);

      const focusableElements = FocusManager.getFocusableElements(container);
      
      expect(focusableElements).toHaveLength(2);
      expect(focusableElements).toContain(button);
      expect(focusableElements).toContain(input);
      expect(focusableElements).not.toContain(disabledButton);
      expect(focusableElements).not.toContain(hiddenInput);
    });

    it('should check if element is focusable', () => {
      const button = document.createElement('button');
      const disabledButton = document.createElement('button');
      disabledButton.disabled = true;

      // Mock offsetWidth and offsetHeight for JSDOM
      Object.defineProperty(button, 'offsetWidth', { value: 100 });
      Object.defineProperty(button, 'offsetHeight', { value: 30 });
      Object.defineProperty(disabledButton, 'offsetWidth', { value: 100 });
      Object.defineProperty(disabledButton, 'offsetHeight', { value: 30 });

      container.appendChild(button);
      container.appendChild(disabledButton);

      expect(FocusManager.isFocusable(button)).toBe(true);
      expect(FocusManager.isFocusable(disabledButton)).toBe(false);
    });

    it('should move focus to next element', () => {
      const button1 = document.createElement('button');
      const button2 = document.createElement('button');
      const button3 = document.createElement('button');

      container.appendChild(button1);
      container.appendChild(button2);
      container.appendChild(button3);

      button1.focus();
      FocusManager.focusNext(container);
      expect(document.activeElement).toBe(button2);

      FocusManager.focusNext(container);
      expect(document.activeElement).toBe(button3);

      // Should wrap to first element
      FocusManager.focusNext(container);
      expect(document.activeElement).toBe(button1);
    });

    it('should move focus to previous element', () => {
      const button1 = document.createElement('button');
      const button2 = document.createElement('button');
      const button3 = document.createElement('button');

      container.appendChild(button1);
      container.appendChild(button2);
      container.appendChild(button3);

      button3.focus();
      FocusManager.focusPrevious(container);
      expect(document.activeElement).toBe(button2);

      FocusManager.focusPrevious(container);
      expect(document.activeElement).toBe(button1);

      // Should wrap to last element
      FocusManager.focusPrevious(container);
      expect(document.activeElement).toBe(button3);
    });
  });

  describe('ARIA Utils', () => {
    it('should generate unique IDs', () => {
      const id1 = ariaUtils.generateId('test');
      const id2 = ariaUtils.generateId('test');

      expect(id1).toMatch(/^test-[a-z0-9]+$/);
      expect(id2).toMatch(/^test-[a-z0-9]+$/);
      expect(id1).not.toBe(id2);
    });

    it('should check if element has accessible name', () => {
      const buttonWithLabel = document.createElement('button');
      buttonWithLabel.setAttribute('aria-label', 'Test button');

      const buttonWithText = document.createElement('button');
      buttonWithText.textContent = 'Click me';

      const buttonWithoutName = document.createElement('button');

      expect(ariaUtils.hasAccessibleName(buttonWithLabel)).toBe(true);
      expect(ariaUtils.hasAccessibleName(buttonWithText)).toBe(true);
      expect(ariaUtils.hasAccessibleName(buttonWithoutName)).toBe(false);
    });

    it('should get accessible name from various sources', () => {
      const buttonWithLabel = document.createElement('button');
      buttonWithLabel.setAttribute('aria-label', 'Aria label');

      const buttonWithText = document.createElement('button');
      buttonWithText.textContent = 'Button text';

      const inputWithPlaceholder = document.createElement('input');
      inputWithPlaceholder.placeholder = 'Placeholder text';

      expect(ariaUtils.getAccessibleName(buttonWithLabel)).toBe('Aria label');
      expect(ariaUtils.getAccessibleName(buttonWithText)).toBe('Button text');
      expect(ariaUtils.getAccessibleName(inputWithPlaceholder)).toBe('Placeholder text');
    });

    it('should set accessible name', () => {
      const button = document.createElement('button');
      ariaUtils.setAccessibleName(button, 'New label');

      expect(button.getAttribute('aria-label')).toBe('New label');
    });

    it('should create and remove ARIA description', () => {
      const button = document.createElement('button');
      container.appendChild(button);

      const descriptionId = ariaUtils.createDescription(button, 'Test description');

      expect(button.getAttribute('aria-describedby')).toBe(descriptionId);
      
      const descriptionElement = document.getElementById(descriptionId);
      expect(descriptionElement).toBeTruthy();
      expect(descriptionElement?.textContent).toBe('Test description');

      ariaUtils.removeDescription(button, descriptionId);

      expect(button.getAttribute('aria-describedby')).toBeNull();
      expect(document.getElementById(descriptionId)).toBeNull();
    });
  });

  describe('Integration Tests', () => {
    it('should work together for complete accessibility setup', () => {
      // Create a modal with proper ARIA attributes
      const modal = document.createElement('div');
      const modalAttrs = generateAriaAttributes.modal({
        labelledBy: 'modal-title',
        modal: true,
      });

      Object.entries(modalAttrs).forEach(([key, value]) => {
        modal.setAttribute(key, value.toString());
      });

      const title = document.createElement('h2');
      title.id = 'modal-title';
      title.textContent = 'Test Modal';

      const button = document.createElement('button');
      const buttonAttrs = generateAriaAttributes.button({
        label: polishAriaLabels.CLOSE,
      });

      Object.entries(buttonAttrs).forEach(([key, value]) => {
        button.setAttribute(key, value.toString());
      });

      modal.appendChild(title);
      modal.appendChild(button);
      container.appendChild(modal);

      // Test ARIA attributes
      expect(modal.getAttribute('role')).toBe('dialog');
      expect(modal.getAttribute('aria-labelledby')).toBe('modal-title');
      expect(modal.getAttribute('aria-modal')).toBe('true');
      expect(button.getAttribute('aria-label')).toBe('Zamknij');

      // Test focus management
      FocusManager.saveFocus(button);
      expect(document.activeElement).toBe(button);

      // Test screen reader announcements
      const announcer = ScreenReaderAnnouncer.getInstance();
      announcer.announcePolite('Modal opened');

      const politeRegion = document.querySelector('[aria-live="polite"]');
      expect(politeRegion?.textContent).toBe('Modal opened');
    });
  });
});