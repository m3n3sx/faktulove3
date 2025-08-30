/**
 * ARIA utilities for screen reader compatibility and accessibility support
 */

/**
 * ARIA role definitions for common component patterns
 */
export const ARIA_ROLES = {
  // Interactive elements
  BUTTON: 'button',
  LINK: 'link',
  MENUITEM: 'menuitem',
  MENUITEMCHECKBOX: 'menuitemcheckbox',
  MENUITEMRADIO: 'menuitemradio',
  OPTION: 'option',
  TAB: 'tab',
  TABPANEL: 'tabpanel',
  TREEITEM: 'treeitem',
  
  // Composite elements
  COMBOBOX: 'combobox',
  GRID: 'grid',
  LISTBOX: 'listbox',
  MENU: 'menu',
  MENUBAR: 'menubar',
  RADIOGROUP: 'radiogroup',
  TABLIST: 'tablist',
  TREE: 'tree',
  TREEGRID: 'treegrid',
  
  // Document structure
  ARTICLE: 'article',
  BANNER: 'banner',
  COMPLEMENTARY: 'complementary',
  CONTENTINFO: 'contentinfo',
  FORM: 'form',
  MAIN: 'main',
  NAVIGATION: 'navigation',
  REGION: 'region',
  SEARCH: 'search',
  
  // Live regions
  ALERT: 'alert',
  ALERTDIALOG: 'alertdialog',
  DIALOG: 'dialog',
  LOG: 'log',
  MARQUEE: 'marquee',
  STATUS: 'status',
  TIMER: 'timer',
  
  // Polish business-specific roles
  INVOICE_FORM: 'form',
  INVOICE_SECTION: 'region',
  CURRENCY_INPUT: 'spinbutton',
  DATE_PICKER: 'combobox',
  VAT_SELECTOR: 'combobox',
} as const;

/**
 * ARIA properties for enhanced accessibility
 */
export const ARIA_PROPERTIES = {
  // Widget attributes
  AUTOCOMPLETE: 'aria-autocomplete',
  CHECKED: 'aria-checked',
  DISABLED: 'aria-disabled',
  EXPANDED: 'aria-expanded',
  HASPOPUP: 'aria-haspopup',
  HIDDEN: 'aria-hidden',
  INVALID: 'aria-invalid',
  LABEL: 'aria-label',
  LEVEL: 'aria-level',
  MULTILINE: 'aria-multiline',
  MULTISELECTABLE: 'aria-multiselectable',
  ORIENTATION: 'aria-orientation',
  PLACEHOLDER: 'aria-placeholder',
  PRESSED: 'aria-pressed',
  READONLY: 'aria-readonly',
  REQUIRED: 'aria-required',
  SELECTED: 'aria-selected',
  SORT: 'aria-sort',
  VALUEMAX: 'aria-valuemax',
  VALUEMIN: 'aria-valuemin',
  VALUENOW: 'aria-valuenow',
  VALUETEXT: 'aria-valuetext',
  
  // Live region attributes
  ATOMIC: 'aria-atomic',
  BUSY: 'aria-busy',
  LIVE: 'aria-live',
  RELEVANT: 'aria-relevant',
  
  // Drag-and-drop attributes
  DROPEFFECT: 'aria-dropeffect',
  GRABBED: 'aria-grabbed',
  
  // Relationship attributes
  ACTIVEDESCENDANT: 'aria-activedescendant',
  COLCOUNT: 'aria-colcount',
  COLINDEX: 'aria-colindex',
  COLSPAN: 'aria-colspan',
  CONTROLS: 'aria-controls',
  DESCRIBEDBY: 'aria-describedby',
  DETAILS: 'aria-details',
  ERRORMESSAGE: 'aria-errormessage',
  FLOWTO: 'aria-flowto',
  LABELLEDBY: 'aria-labelledby',
  OWNS: 'aria-owns',
  POSINSET: 'aria-posinset',
  ROWCOUNT: 'aria-rowcount',
  ROWINDEX: 'aria-rowindex',
  ROWSPAN: 'aria-rowspan',
  SETSIZE: 'aria-setsize',
} as const;

/**
 * ARIA live region politeness levels
 */
export const ARIA_LIVE_REGIONS = {
  OFF: 'off',
  POLITE: 'polite',
  ASSERTIVE: 'assertive',
} as const;

/**
 * ARIA has-popup values
 */
export const ARIA_HASPOPUP = {
  FALSE: 'false',
  TRUE: 'true',
  MENU: 'menu',
  LISTBOX: 'listbox',
  TREE: 'tree',
  GRID: 'grid',
  DIALOG: 'dialog',
} as const;

/**
 * Generate ARIA attributes for components
 */
export const generateAriaAttributes = {
  /**
   * Generate ARIA attributes for button components
   */
  button: (options: {
    label?: string;
    labelledBy?: string;
    describedBy?: string;
    pressed?: boolean;
    expanded?: boolean;
    hasPopup?: keyof typeof ARIA_HASPOPUP;
    controls?: string;
    disabled?: boolean;
  }) => {
    const attrs: Record<string, string | boolean> = {};
    
    if (options.label) attrs[ARIA_PROPERTIES.LABEL] = options.label;
    if (options.labelledBy) attrs[ARIA_PROPERTIES.LABELLEDBY] = options.labelledBy;
    if (options.describedBy) attrs[ARIA_PROPERTIES.DESCRIBEDBY] = options.describedBy;
    if (options.pressed !== undefined) attrs[ARIA_PROPERTIES.PRESSED] = options.pressed.toString();
    if (options.expanded !== undefined) attrs[ARIA_PROPERTIES.EXPANDED] = options.expanded.toString();
    if (options.hasPopup) attrs[ARIA_PROPERTIES.HASPOPUP] = ARIA_HASPOPUP[options.hasPopup];
    if (options.controls) attrs[ARIA_PROPERTIES.CONTROLS] = options.controls;
    if (options.disabled) attrs[ARIA_PROPERTIES.DISABLED] = 'true';
    
    return attrs;
  },

  /**
   * Generate ARIA attributes for input components
   */
  input: (options: {
    label?: string;
    labelledBy?: string;
    describedBy?: string;
    required?: boolean;
    invalid?: boolean;
    errorMessage?: string;
    placeholder?: string;
    readonly?: boolean;
    disabled?: boolean;
    autocomplete?: string;
  }) => {
    const attrs: Record<string, string | boolean> = {};
    
    if (options.label) attrs[ARIA_PROPERTIES.LABEL] = options.label;
    if (options.labelledBy) attrs[ARIA_PROPERTIES.LABELLEDBY] = options.labelledBy;
    if (options.describedBy) attrs[ARIA_PROPERTIES.DESCRIBEDBY] = options.describedBy;
    if (options.required) attrs[ARIA_PROPERTIES.REQUIRED] = 'true';
    if (options.invalid) attrs[ARIA_PROPERTIES.INVALID] = 'true';
    if (options.errorMessage) attrs[ARIA_PROPERTIES.ERRORMESSAGE] = options.errorMessage;
    if (options.placeholder) attrs[ARIA_PROPERTIES.PLACEHOLDER] = options.placeholder;
    if (options.readonly) attrs[ARIA_PROPERTIES.READONLY] = 'true';
    if (options.disabled) attrs[ARIA_PROPERTIES.DISABLED] = 'true';
    if (options.autocomplete) attrs[ARIA_PROPERTIES.AUTOCOMPLETE] = options.autocomplete;
    
    return attrs;
  },

  /**
   * Generate ARIA attributes for select/combobox components
   */
  select: (options: {
    label?: string;
    labelledBy?: string;
    describedBy?: string;
    expanded?: boolean;
    hasPopup?: boolean;
    controls?: string;
    activeDescendant?: string;
    required?: boolean;
    invalid?: boolean;
    disabled?: boolean;
  }) => {
    const attrs: Record<string, string | boolean> = {};
    
    attrs.role = ARIA_ROLES.COMBOBOX;
    if (options.label) attrs[ARIA_PROPERTIES.LABEL] = options.label;
    if (options.labelledBy) attrs[ARIA_PROPERTIES.LABELLEDBY] = options.labelledBy;
    if (options.describedBy) attrs[ARIA_PROPERTIES.DESCRIBEDBY] = options.describedBy;
    if (options.expanded !== undefined) attrs[ARIA_PROPERTIES.EXPANDED] = options.expanded.toString();
    if (options.hasPopup) attrs[ARIA_PROPERTIES.HASPOPUP] = ARIA_HASPOPUP.LISTBOX;
    if (options.controls) attrs[ARIA_PROPERTIES.CONTROLS] = options.controls;
    if (options.activeDescendant) attrs[ARIA_PROPERTIES.ACTIVEDESCENDANT] = options.activeDescendant;
    if (options.required) attrs[ARIA_PROPERTIES.REQUIRED] = 'true';
    if (options.invalid) attrs[ARIA_PROPERTIES.INVALID] = 'true';
    if (options.disabled) attrs[ARIA_PROPERTIES.DISABLED] = 'true';
    
    return attrs;
  },

  /**
   * Generate ARIA attributes for modal/dialog components
   */
  modal: (options: {
    label?: string;
    labelledBy?: string;
    describedBy?: string;
    modal?: boolean;
  }) => {
    const attrs: Record<string, string | boolean> = {};
    
    attrs.role = ARIA_ROLES.DIALOG;
    if (options.label) attrs[ARIA_PROPERTIES.LABEL] = options.label;
    if (options.labelledBy) attrs[ARIA_PROPERTIES.LABELLEDBY] = options.labelledBy;
    if (options.describedBy) attrs[ARIA_PROPERTIES.DESCRIBEDBY] = options.describedBy;
    if (options.modal !== false) attrs['aria-modal'] = 'true';
    
    return attrs;
  },

  /**
   * Generate ARIA attributes for live regions
   */
  liveRegion: (options: {
    live?: keyof typeof ARIA_LIVE_REGIONS;
    atomic?: boolean;
    relevant?: string;
    busy?: boolean;
  }) => {
    const attrs: Record<string, string | boolean> = {};
    
    if (options.live) attrs[ARIA_PROPERTIES.LIVE] = ARIA_LIVE_REGIONS[options.live];
    if (options.atomic !== undefined) attrs[ARIA_PROPERTIES.ATOMIC] = options.atomic.toString();
    if (options.relevant) attrs[ARIA_PROPERTIES.RELEVANT] = options.relevant;
    if (options.busy !== undefined) attrs[ARIA_PROPERTIES.BUSY] = options.busy.toString();
    
    return attrs;
  },
};

/**
 * Polish-specific ARIA labels and descriptions
 */
export const polishAriaLabels = {
  // Common actions
  CLOSE: 'Zamknij',
  OPEN: 'Otwórz',
  SAVE: 'Zapisz',
  CANCEL: 'Anuluj',
  DELETE: 'Usuń',
  EDIT: 'Edytuj',
  ADD: 'Dodaj',
  REMOVE: 'Usuń',
  SEARCH: 'Szukaj',
  FILTER: 'Filtruj',
  SORT: 'Sortuj',
  
  // Form elements
  REQUIRED_FIELD: 'Pole wymagane',
  OPTIONAL_FIELD: 'Pole opcjonalne',
  INVALID_INPUT: 'Nieprawidłowe dane',
  ERROR_MESSAGE: 'Komunikat o błędzie',
  HELP_TEXT: 'Tekst pomocniczy',
  
  // Business-specific labels
  NIP_INPUT: 'Numer NIP',
  NIP_INVALID: 'Nieprawidłowy numer NIP',
  REGON_INPUT: 'Numer REGON',
  CURRENCY_INPUT: 'Kwota w złotych',
  CURRENCY_INVALID: 'Nieprawidłowa kwota',
  VAT_RATE: 'Stawka VAT',
  DATE_INPUT: 'Data',
  DATE_FORMAT: 'Format daty: DD.MM.YYYY',
  DATE_INVALID: 'Nieprawidłowa data',
  
  // Invoice-specific labels
  INVOICE_NUMBER: 'Numer faktury',
  INVOICE_DATE: 'Data faktury',
  INVOICE_DUE_DATE: 'Termin płatności',
  INVOICE_AMOUNT: 'Kwota faktury',
  INVOICE_VAT_AMOUNT: 'Kwota VAT',
  INVOICE_GROSS_AMOUNT: 'Kwota brutto',
  INVOICE_NET_AMOUNT: 'Kwota netto',
  
  // Status messages
  LOADING: 'Ładowanie...',
  SAVING: 'Zapisywanie...',
  SAVED: 'Zapisano',
  ERROR: 'Błąd',
  SUCCESS: 'Sukces',
  WARNING: 'Ostrzeżenie',
  
  // Navigation
  MAIN_MENU: 'Menu główne',
  BREADCRUMB: 'Ścieżka nawigacji',
  PAGINATION: 'Paginacja',
  PREVIOUS_PAGE: 'Poprzednia strona',
  NEXT_PAGE: 'Następna strona',
  FIRST_PAGE: 'Pierwsza strona',
  LAST_PAGE: 'Ostatnia strona',
  
  // Table elements
  TABLE: 'Tabela',
  TABLE_CAPTION: 'Opis tabeli',
  COLUMN_HEADER: 'Nagłówek kolumny',
  ROW_HEADER: 'Nagłówek wiersza',
  SORT_ASCENDING: 'Sortuj rosnąco',
  SORT_DESCENDING: 'Sortuj malejąco',
  SORT_NONE: 'Bez sortowania',
};

/**
 * Screen reader announcement utilities
 */
export class ScreenReaderAnnouncer {
  private static instance: ScreenReaderAnnouncer;
  private liveRegion: HTMLElement | null = null;
  private politeRegion: HTMLElement | null = null;
  private assertiveRegion: HTMLElement | null = null;

  private constructor() {
    this.createLiveRegions();
  }

  public static getInstance(): ScreenReaderAnnouncer {
    if (!ScreenReaderAnnouncer.instance) {
      ScreenReaderAnnouncer.instance = new ScreenReaderAnnouncer();
    }
    return ScreenReaderAnnouncer.instance;
  }

  private createLiveRegions(): void {
    // Create polite live region
    this.politeRegion = document.createElement('div');
    this.politeRegion.setAttribute('aria-live', 'polite');
    this.politeRegion.setAttribute('aria-atomic', 'true');
    this.politeRegion.setAttribute('aria-relevant', 'additions text');
    this.politeRegion.style.position = 'absolute';
    this.politeRegion.style.left = '-10000px';
    this.politeRegion.style.width = '1px';
    this.politeRegion.style.height = '1px';
    this.politeRegion.style.overflow = 'hidden';
    document.body.appendChild(this.politeRegion);

    // Create assertive live region
    this.assertiveRegion = document.createElement('div');
    this.assertiveRegion.setAttribute('aria-live', 'assertive');
    this.assertiveRegion.setAttribute('aria-atomic', 'true');
    this.assertiveRegion.setAttribute('aria-relevant', 'additions text');
    this.assertiveRegion.style.position = 'absolute';
    this.assertiveRegion.style.left = '-10000px';
    this.assertiveRegion.style.width = '1px';
    this.assertiveRegion.style.height = '1px';
    this.assertiveRegion.style.overflow = 'hidden';
    document.body.appendChild(this.assertiveRegion);
  }

  /**
   * Announce message politely (won't interrupt current screen reader output)
   */
  public announcePolite(message: string): void {
    if (this.politeRegion) {
      this.politeRegion.textContent = message;
    }
  }

  /**
   * Announce message assertively (will interrupt current screen reader output)
   */
  public announceAssertive(message: string): void {
    if (this.assertiveRegion) {
      this.assertiveRegion.textContent = message;
    }
  }

  /**
   * Announce form validation error
   */
  public announceError(message: string): void {
    this.announceAssertive(`${polishAriaLabels.ERROR}: ${message}`);
  }

  /**
   * Announce successful action
   */
  public announceSuccess(message: string): void {
    this.announcePolite(`${polishAriaLabels.SUCCESS}: ${message}`);
  }

  /**
   * Announce loading state
   */
  public announceLoading(message: string = polishAriaLabels.LOADING): void {
    this.announcePolite(message);
  }

  /**
   * Announce page navigation
   */
  public announceNavigation(message: string): void {
    this.announcePolite(message);
  }

  /**
   * Clear all announcements
   */
  public clear(): void {
    if (this.politeRegion) this.politeRegion.textContent = '';
    if (this.assertiveRegion) this.assertiveRegion.textContent = '';
  }

  /**
   * Cleanup live regions (for testing)
   */
  public cleanup(): void {
    if (this.politeRegion) {
      document.body.removeChild(this.politeRegion);
      this.politeRegion = null;
    }
    if (this.assertiveRegion) {
      document.body.removeChild(this.assertiveRegion);
      this.assertiveRegion = null;
    }
  }
}

/**
 * Focus management utilities for modals and dropdowns
 */
export class FocusManager {
  private static focusStack: HTMLElement[] = [];
  private static trapStack: HTMLElement[] = [];

  /**
   * Save current focus and set new focus
   */
  public static saveFocus(newFocusElement?: HTMLElement): void {
    const currentFocus = document.activeElement as HTMLElement;
    if (currentFocus) {
      this.focusStack.push(currentFocus);
    }
    
    if (newFocusElement) {
      newFocusElement.focus();
    }
  }

  /**
   * Restore previously saved focus
   */
  public static restoreFocus(): void {
    const previousFocus = this.focusStack.pop();
    if (previousFocus && document.contains(previousFocus)) {
      previousFocus.focus();
    }
  }

  /**
   * Set up focus trap for modal or dropdown
   */
  public static trapFocus(container: HTMLElement): void {
    this.trapStack.push(container);
    
    const focusableElements = this.getFocusableElements(container);
    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return;

      if (event.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    };

    container.addEventListener('keydown', handleKeyDown);
    
    // Store cleanup function
    (container as any)._focusTrapCleanup = () => {
      container.removeEventListener('keydown', handleKeyDown);
    };

    // Focus first element
    firstElement.focus();
  }

  /**
   * Remove focus trap
   */
  public static releaseFocusTrap(): void {
    const container = this.trapStack.pop();
    if (container && (container as any)._focusTrapCleanup) {
      (container as any)._focusTrapCleanup();
      delete (container as any)._focusTrapCleanup;
    }
  }

  /**
   * Get all focusable elements within a container
   */
  public static getFocusableElements(container: HTMLElement): HTMLElement[] {
    const focusableSelectors = [
      'button:not([disabled])',
      '[href]',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]',
    ].join(', ');

    return Array.from(container.querySelectorAll(focusableSelectors))
      .filter((element) => {
        const el = element as HTMLElement;
        return el.offsetWidth > 0 && el.offsetHeight > 0 && !el.hidden;
      }) as HTMLElement[];
  }

  /**
   * Check if element is focusable
   */
  public static isFocusable(element: HTMLElement): boolean {
    const focusableElements = this.getFocusableElements(document.body);
    return focusableElements.includes(element);
  }

  /**
   * Move focus to next focusable element
   */
  public static focusNext(container: HTMLElement = document.body): void {
    const focusableElements = this.getFocusableElements(container);
    const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);
    const nextIndex = (currentIndex + 1) % focusableElements.length;
    focusableElements[nextIndex]?.focus();
  }

  /**
   * Move focus to previous focusable element
   */
  public static focusPrevious(container: HTMLElement = document.body): void {
    const focusableElements = this.getFocusableElements(container);
    const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);
    const previousIndex = currentIndex === 0 ? focusableElements.length - 1 : currentIndex - 1;
    focusableElements[previousIndex]?.focus();
  }

  /**
   * Clear focus stacks (for testing)
   */
  public static clearStacks(): void {
    this.focusStack = [];
    this.trapStack = [];
  }
}

/**
 * Utility functions for ARIA support
 */
export const ariaUtils = {
  /**
   * Generate unique ID for ARIA relationships
   */
  generateId: (prefix: string = 'aria'): string => {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Check if element has accessible name
   */
  hasAccessibleName: (element: HTMLElement): boolean => {
    return !!(
      element.getAttribute('aria-label') ||
      element.getAttribute('aria-labelledby') ||
      element.textContent?.trim() ||
      (element as HTMLInputElement).placeholder ||
      element.getAttribute('title')
    );
  },

  /**
   * Get accessible name for element
   */
  getAccessibleName: (element: HTMLElement): string => {
    const ariaLabel = element.getAttribute('aria-label');
    if (ariaLabel) return ariaLabel;

    const ariaLabelledBy = element.getAttribute('aria-labelledby');
    if (ariaLabelledBy) {
      const labelElement = document.getElementById(ariaLabelledBy);
      if (labelElement) return labelElement.textContent?.trim() || '';
    }

    const textContent = element.textContent?.trim();
    if (textContent) return textContent;

    const placeholder = (element as HTMLInputElement).placeholder;
    if (placeholder) return placeholder;

    const title = element.getAttribute('title');
    if (title) return title;

    return '';
  },

  /**
   * Set accessible name for element
   */
  setAccessibleName: (element: HTMLElement, name: string): void => {
    element.setAttribute('aria-label', name);
  },

  /**
   * Create ARIA description relationship
   */
  createDescription: (element: HTMLElement, description: string): string => {
    const descriptionId = ariaUtils.generateId('desc');
    const descriptionElement = document.createElement('div');
    descriptionElement.id = descriptionId;
    descriptionElement.textContent = description;
    descriptionElement.style.display = 'none';
    
    document.body.appendChild(descriptionElement);
    element.setAttribute('aria-describedby', descriptionId);
    
    return descriptionId;
  },

  /**
   * Remove ARIA description
   */
  removeDescription: (element: HTMLElement, descriptionId: string): void => {
    const descriptionElement = document.getElementById(descriptionId);
    if (descriptionElement) {
      document.body.removeChild(descriptionElement);
    }
    element.removeAttribute('aria-describedby');
  },
};