/**
 * Focus management utilities for modal and dropdown components
 * Provides comprehensive focus handling for complex UI patterns
 */

import { FocusManager } from './ariaUtils';

/**
 * Focus trap configuration options
 */
export interface FocusTrapOptions {
  initialFocus?: HTMLElement | string;
  returnFocus?: HTMLElement;
  escapeDeactivates?: boolean;
  clickOutsideDeactivates?: boolean;
  allowOutsideClick?: boolean;
  preventScroll?: boolean;
}

/**
 * Modal focus management class
 */
export class ModalFocusManager {
  private container: HTMLElement;
  private options: FocusTrapOptions;
  private previousFocus: HTMLElement | null = null;
  private isActive: boolean = false;
  private keydownHandler: (event: KeyboardEvent) => void;
  private clickHandler: (event: MouseEvent) => void;

  constructor(container: HTMLElement, options: FocusTrapOptions = {}) {
    this.container = container;
    this.options = {
      escapeDeactivates: true,
      clickOutsideDeactivates: true,
      allowOutsideClick: false,
      preventScroll: true,
      ...options,
    };

    this.keydownHandler = this.handleKeydown.bind(this);
    this.clickHandler = this.handleClick.bind(this);
  }

  /**
   * Activate focus trap
   */
  public activate(): void {
    if (this.isActive) return;

    // Save current focus
    this.previousFocus = document.activeElement as HTMLElement;

    // Set up event listeners
    document.addEventListener('keydown', this.keydownHandler);
    if (this.options.clickOutsideDeactivates) {
      document.addEventListener('click', this.clickHandler);
    }

    // Prevent body scroll if requested
    if (this.options.preventScroll) {
      document.body.style.overflow = 'hidden';
    }

    // Set initial focus
    this.setInitialFocus();

    this.isActive = true;
  }

  /**
   * Deactivate focus trap
   */
  public deactivate(): void {
    if (!this.isActive) return;

    // Remove event listeners
    document.removeEventListener('keydown', this.keydownHandler);
    document.removeEventListener('click', this.clickHandler);

    // Restore body scroll
    if (this.options.preventScroll) {
      document.body.style.overflow = '';
    }

    // Restore previous focus
    this.restoreFocus();

    this.isActive = false;
  }

  private setInitialFocus(): void {
    let initialFocusElement: HTMLElement | null = null;

    if (this.options.initialFocus) {
      if (typeof this.options.initialFocus === 'string') {
        initialFocusElement = this.container.querySelector(this.options.initialFocus);
      } else {
        initialFocusElement = this.options.initialFocus;
      }
    }

    if (!initialFocusElement) {
      const focusableElements = FocusManager.getFocusableElements(this.container);
      initialFocusElement = focusableElements[0] || this.container;
    }

    if (initialFocusElement) {
      initialFocusElement.focus();
    }
  }

  private restoreFocus(): void {
    const returnFocusElement = this.options.returnFocus || this.previousFocus;
    if (returnFocusElement && document.contains(returnFocusElement)) {
      returnFocusElement.focus();
    }
  }

  private handleKeydown(event: KeyboardEvent): void {
    // Handle Escape key
    if (event.key === 'Escape' && this.options.escapeDeactivates) {
      event.preventDefault();
      this.deactivate();
      return;
    }

    // Handle Tab key for focus trapping
    if (event.key === 'Tab') {
      this.handleTabKey(event);
    }
  }

  private handleTabKey(event: KeyboardEvent): void {
    const focusableElements = FocusManager.getFocusableElements(this.container);
    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    const currentElement = document.activeElement as HTMLElement;

    if (event.shiftKey) {
      // Shift + Tab (backward)
      if (currentElement === firstElement || !this.container.contains(currentElement)) {
        event.preventDefault();
        lastElement.focus();
      }
    } else {
      // Tab (forward)
      if (currentElement === lastElement || !this.container.contains(currentElement)) {
        event.preventDefault();
        firstElement.focus();
      }
    }
  }

  private handleClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!this.container.contains(target) && !this.options.allowOutsideClick) {
      event.preventDefault();
      this.deactivate();
    }
  }
}

/**
 * Dropdown focus management class
 */
export class DropdownFocusManager {
  private trigger: HTMLElement;
  private dropdown: HTMLElement;
  private isOpen: boolean = false;
  private keydownHandler: (event: KeyboardEvent) => void;
  private clickHandler: (event: MouseEvent) => void;

  constructor(trigger: HTMLElement, dropdown: HTMLElement) {
    this.trigger = trigger;
    this.dropdown = dropdown;

    this.keydownHandler = this.handleKeydown.bind(this);
    this.clickHandler = this.handleClick.bind(this);
  }

  /**
   * Open dropdown and manage focus
   */
  public open(): void {
    if (this.isOpen) return;

    this.isOpen = true;

    // Set up event listeners
    document.addEventListener('keydown', this.keydownHandler);
    document.addEventListener('click', this.clickHandler);

    // Focus first item in dropdown
    const focusableElements = FocusManager.getFocusableElements(this.dropdown);
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  }

  /**
   * Close dropdown and restore focus
   */
  public close(): void {
    if (!this.isOpen) return;

    this.isOpen = false;

    // Remove event listeners
    document.removeEventListener('keydown', this.keydownHandler);
    document.removeEventListener('click', this.clickHandler);

    // Return focus to trigger
    this.trigger.focus();
  }

  private handleKeydown(event: KeyboardEvent): void {
    if (!this.isOpen) return;

    switch (event.key) {
      case 'Escape':
        event.preventDefault();
        this.close();
        break;

      case 'ArrowDown':
        event.preventDefault();
        this.focusNext();
        break;

      case 'ArrowUp':
        event.preventDefault();
        this.focusPrevious();
        break;

      case 'Home':
        event.preventDefault();
        this.focusFirst();
        break;

      case 'End':
        event.preventDefault();
        this.focusLast();
        break;

      case 'Tab':
        // Allow Tab to close dropdown and continue normal tab sequence
        this.close();
        break;
    }
  }

  private handleClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!this.dropdown.contains(target) && !this.trigger.contains(target)) {
      this.close();
    }
  }

  private focusNext(): void {
    const focusableElements = FocusManager.getFocusableElements(this.dropdown);
    const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);
    const nextIndex = (currentIndex + 1) % focusableElements.length;
    focusableElements[nextIndex]?.focus();
  }

  private focusPrevious(): void {
    const focusableElements = FocusManager.getFocusableElements(this.dropdown);
    const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);
    const previousIndex = currentIndex === 0 ? focusableElements.length - 1 : currentIndex - 1;
    focusableElements[previousIndex]?.focus();
  }

  private focusFirst(): void {
    const focusableElements = FocusManager.getFocusableElements(this.dropdown);
    focusableElements[0]?.focus();
  }

  private focusLast(): void {
    const focusableElements = FocusManager.getFocusableElements(this.dropdown);
    focusableElements[focusableElements.length - 1]?.focus();
  }
}

/**
 * Roving tabindex manager for radio groups, toolbars, etc.
 */
export class RovingTabindexManager {
  private container: HTMLElement;
  private items: HTMLElement[] = [];
  private currentIndex: number = 0;
  private keydownHandler: (event: KeyboardEvent) => void;

  constructor(container: HTMLElement, itemSelector: string = '[role="option"], [role="menuitem"], [role="tab"]') {
    this.container = container;
    this.keydownHandler = this.handleKeydown.bind(this);
    
    this.updateItems(itemSelector);
    this.setupTabindex();
    this.container.addEventListener('keydown', this.keydownHandler);
  }

  /**
   * Update the list of managed items
   */
  public updateItems(itemSelector: string): void {
    this.items = Array.from(this.container.querySelectorAll(itemSelector));
    this.setupTabindex();
  }

  /**
   * Set active item by index
   */
  public setActiveItem(index: number): void {
    if (index < 0 || index >= this.items.length) return;

    // Remove tabindex from all items
    this.items.forEach(item => item.setAttribute('tabindex', '-1'));
    
    // Set tabindex on active item
    this.items[index].setAttribute('tabindex', '0');
    this.currentIndex = index;
  }

  /**
   * Focus active item
   */
  public focusActiveItem(): void {
    this.items[this.currentIndex]?.focus();
  }

  /**
   * Destroy the manager
   */
  public destroy(): void {
    this.container.removeEventListener('keydown', this.keydownHandler);
  }

  private setupTabindex(): void {
    this.items.forEach((item, index) => {
      item.setAttribute('tabindex', index === this.currentIndex ? '0' : '-1');
    });
  }

  private handleKeydown(event: KeyboardEvent): void {
    let newIndex = this.currentIndex;

    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        event.preventDefault();
        newIndex = (this.currentIndex + 1) % this.items.length;
        break;

      case 'ArrowLeft':
      case 'ArrowUp':
        event.preventDefault();
        newIndex = this.currentIndex === 0 ? this.items.length - 1 : this.currentIndex - 1;
        break;

      case 'Home':
        event.preventDefault();
        newIndex = 0;
        break;

      case 'End':
        event.preventDefault();
        newIndex = this.items.length - 1;
        break;

      default:
        return;
    }

    this.setActiveItem(newIndex);
    this.focusActiveItem();
  }
}

/**
 * Focus management utilities for Polish business forms
 */
export class PolishFormFocusManager {
  private form: HTMLElement;
  private errorSummary: HTMLElement | null = null;

  constructor(form: HTMLElement) {
    this.form = form;
  }

  /**
   * Create and focus error summary for form validation
   */
  public createErrorSummary(errors: Array<{ field: string; message: string }>): void {
    // Remove existing error summary
    this.removeErrorSummary();

    if (errors.length === 0) return;

    // Create error summary container
    this.errorSummary = document.createElement('div');
    this.errorSummary.setAttribute('role', 'alert');
    this.errorSummary.setAttribute('aria-live', 'assertive');
    this.errorSummary.setAttribute('tabindex', '-1');
    this.errorSummary.className = 'error-summary';

    // Create heading
    const heading = document.createElement('h2');
    heading.textContent = errors.length === 1 
      ? 'Znaleziono 1 błąd w formularzu:' 
      : `Znaleziono ${errors.length} błędów w formularzu:`;
    this.errorSummary.appendChild(heading);

    // Create error list
    const errorList = document.createElement('ul');
    errors.forEach(error => {
      const listItem = document.createElement('li');
      const link = document.createElement('a');
      link.href = `#${error.field}`;
      link.textContent = error.message;
      link.addEventListener('click', (e) => {
        e.preventDefault();
        this.focusField(error.field);
      });
      listItem.appendChild(link);
      errorList.appendChild(listItem);
    });
    this.errorSummary.appendChild(errorList);

    // Insert at beginning of form
    this.form.insertBefore(this.errorSummary, this.form.firstChild);

    // Focus error summary
    this.errorSummary.focus();
  }

  /**
   * Remove error summary
   */
  public removeErrorSummary(): void {
    if (this.errorSummary && this.errorSummary.parentNode) {
      this.errorSummary.parentNode.removeChild(this.errorSummary);
      this.errorSummary = null;
    }
  }

  /**
   * Focus specific form field
   */
  public focusField(fieldId: string): void {
    const field = document.getElementById(fieldId);
    if (field) {
      field.focus();
      
      // Scroll field into view
      field.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
    }
  }

  /**
   * Focus first invalid field
   */
  public focusFirstInvalidField(): void {
    const invalidField = this.form.querySelector('[aria-invalid="true"]') as HTMLElement;
    if (invalidField) {
      invalidField.focus();
    }
  }

  /**
   * Set up form navigation helpers
   */
  public setupFormNavigation(): void {
    const fields = this.form.querySelectorAll('input, select, textarea');
    
    fields.forEach((field, index) => {
      field.addEventListener('keydown', (event: KeyboardEvent) => {
        // Ctrl+Enter to submit form
        if (event.ctrlKey && event.key === 'Enter') {
          event.preventDefault();
          const submitButton = this.form.querySelector('[type="submit"]') as HTMLButtonElement;
          if (submitButton) {
            submitButton.click();
          }
        }
      });
    });
  }
}

/**
 * Utility functions for focus management
 */
export const focusUtils = {
  /**
   * Check if element is currently focused
   */
  isFocused: (element: HTMLElement): boolean => {
    return document.activeElement === element;
  },

  /**
   * Check if element is focusable
   */
  isFocusable: (element: HTMLElement): boolean => {
    return FocusManager.isFocusable(element);
  },

  /**
   * Get next focusable element
   */
  getNextFocusable: (current: HTMLElement, container: HTMLElement = document.body): HTMLElement | null => {
    const focusableElements = FocusManager.getFocusableElements(container);
    const currentIndex = focusableElements.indexOf(current);
    return focusableElements[currentIndex + 1] || null;
  },

  /**
   * Get previous focusable element
   */
  getPreviousFocusable: (current: HTMLElement, container: HTMLElement = document.body): HTMLElement | null => {
    const focusableElements = FocusManager.getFocusableElements(container);
    const currentIndex = focusableElements.indexOf(current);
    return focusableElements[currentIndex - 1] || null;
  },

  /**
   * Create focus outline for custom elements
   */
  createFocusOutline: (element: HTMLElement): void => {
    element.style.outline = '2px solid #2563eb';
    element.style.outlineOffset = '2px';
  },

  /**
   * Remove focus outline
   */
  removeFocusOutline: (element: HTMLElement): void => {
    element.style.outline = '';
    element.style.outlineOffset = '';
  },

  /**
   * Ensure element is visible when focused
   */
  ensureVisible: (element: HTMLElement): void => {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest'
    });
  },
};