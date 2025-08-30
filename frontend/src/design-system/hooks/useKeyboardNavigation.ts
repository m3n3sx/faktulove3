/**
 * React hooks for keyboard navigation and accessibility
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { FocusManager, ModalFocusManager, DropdownFocusManager, RovingTabindexManager } from '../utils/focusManagement';
import { keyboardShortcuts, KeyboardShortcut } from '../utils/keyboardShortcuts';

/**
 * Hook for managing focus trap in modals and dialogs
 */
export const useFocusTrap = (isActive: boolean, options?: {
  initialFocus?: string;
  returnFocus?: HTMLElement;
  escapeDeactivates?: boolean;
}) => {
  const containerRef = useRef<HTMLElement>(null);
  const focusManagerRef = useRef<ModalFocusManager | null>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    if (isActive) {
      // Save current focus
      previousFocusRef.current = document.activeElement as HTMLElement;
      
      // Create focus manager
      focusManagerRef.current = new ModalFocusManager(containerRef.current, {
        initialFocus: options?.initialFocus,
        returnFocus: options?.returnFocus || previousFocusRef.current,
        escapeDeactivates: options?.escapeDeactivates ?? true,
      });
      
      focusManagerRef.current.activate();
    } else {
      // Deactivate focus trap
      if (focusManagerRef.current) {
        focusManagerRef.current.deactivate();
        focusManagerRef.current = null;
      }
    }

    return () => {
      if (focusManagerRef.current) {
        focusManagerRef.current.deactivate();
      }
    };
  }, [isActive, options]);

  return containerRef;
};

/**
 * Hook for managing dropdown keyboard navigation
 */
export const useDropdownNavigation = (isOpen: boolean) => {
  const triggerRef = useRef<HTMLElement>(null);
  const dropdownRef = useRef<HTMLElement>(null);
  const focusManagerRef = useRef<DropdownFocusManager | null>(null);

  useEffect(() => {
    if (!triggerRef.current || !dropdownRef.current) return;

    if (isOpen) {
      focusManagerRef.current = new DropdownFocusManager(
        triggerRef.current,
        dropdownRef.current
      );
      focusManagerRef.current.open();
    } else {
      if (focusManagerRef.current) {
        focusManagerRef.current.close();
        focusManagerRef.current = null;
      }
    }

    return () => {
      if (focusManagerRef.current) {
        focusManagerRef.current.close();
      }
    };
  }, [isOpen]);

  return { triggerRef, dropdownRef };
};

/**
 * Hook for managing roving tabindex navigation (radio groups, toolbars, etc.)
 */
export const useRovingTabindex = (itemSelector: string = '[role="option"]') => {
  const containerRef = useRef<HTMLElement>(null);
  const managerRef = useRef<RovingTabindexManager | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    managerRef.current = new RovingTabindexManager(containerRef.current, itemSelector);

    return () => {
      if (managerRef.current) {
        managerRef.current.destroy();
      }
    };
  }, [itemSelector]);

  const setActiveItem = useCallback((index: number) => {
    managerRef.current?.setActiveItem(index);
  }, []);

  const focusActiveItem = useCallback(() => {
    managerRef.current?.focusActiveItem();
  }, []);

  return { containerRef, setActiveItem, focusActiveItem };
};

/**
 * Hook for keyboard shortcuts in components
 */
export const useKeyboardShortcuts = (
  shortcuts: KeyboardShortcut[],
  context?: string,
  enabled: boolean = true
) => {
  useEffect(() => {
    if (!enabled) return;

    // Register shortcuts
    shortcuts.forEach(shortcut => {
      if (context) {
        shortcut.context = context;
      }
      keyboardShortcuts.register(shortcut);
    });

    // Push context if provided
    if (context) {
      keyboardShortcuts.pushContext(context);
    }

    // Cleanup
    return () => {
      shortcuts.forEach(shortcut => {
        keyboardShortcuts.unregister(shortcut);
      });
      
      if (context) {
        keyboardShortcuts.popContext();
      }
    };
  }, [shortcuts, context, enabled]);
};

/**
 * Hook for arrow key navigation in lists and grids
 */
export const useArrowNavigation = (options: {
  orientation?: 'horizontal' | 'vertical' | 'both';
  wrap?: boolean;
  itemSelector?: string;
}) => {
  const containerRef = useRef<HTMLElement>(null);
  const { orientation = 'vertical', wrap = true, itemSelector = '[tabindex]' } = options;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      const items = Array.from(container.querySelectorAll(itemSelector)) as HTMLElement[];
      const currentIndex = items.indexOf(document.activeElement as HTMLElement);
      
      if (currentIndex === -1) return;

      let nextIndex = currentIndex;

      switch (event.key) {
        case 'ArrowDown':
          if (orientation === 'vertical' || orientation === 'both') {
            event.preventDefault();
            nextIndex = wrap ? (currentIndex + 1) % items.length : Math.min(currentIndex + 1, items.length - 1);
          }
          break;
        case 'ArrowUp':
          if (orientation === 'vertical' || orientation === 'both') {
            event.preventDefault();
            nextIndex = wrap ? (currentIndex - 1 + items.length) % items.length : Math.max(currentIndex - 1, 0);
          }
          break;
        case 'ArrowRight':
          if (orientation === 'horizontal' || orientation === 'both') {
            event.preventDefault();
            nextIndex = wrap ? (currentIndex + 1) % items.length : Math.min(currentIndex + 1, items.length - 1);
          }
          break;
        case 'ArrowLeft':
          if (orientation === 'horizontal' || orientation === 'both') {
            event.preventDefault();
            nextIndex = wrap ? (currentIndex - 1 + items.length) % items.length : Math.max(currentIndex - 1, 0);
          }
          break;
        case 'Home':
          event.preventDefault();
          nextIndex = 0;
          break;
        case 'End':
          event.preventDefault();
          nextIndex = items.length - 1;
          break;
      }

      if (nextIndex !== currentIndex && items[nextIndex]) {
        items[nextIndex].focus();
      }
    };

    container.addEventListener('keydown', handleKeyDown);

    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  }, [orientation, wrap, itemSelector]);

  return containerRef;
};

/**
 * Hook for managing keyboard navigation state
 */
export const useKeyboardNavigationState = () => {
  const [isKeyboardUser, setIsKeyboardUser] = useState(false);
  const [lastInteraction, setLastInteraction] = useState<'mouse' | 'keyboard'>('mouse');

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        setIsKeyboardUser(true);
        setLastInteraction('keyboard');
        document.body.classList.add('keyboard-navigation-active');
      }
    };

    const handleMouseDown = () => {
      setIsKeyboardUser(false);
      setLastInteraction('mouse');
      document.body.classList.remove('keyboard-navigation-active');
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  return { isKeyboardUser, lastInteraction };
};

/**
 * Hook for skip links functionality
 */
export const useSkipLinks = () => {
  const skipToContent = useCallback((targetId: string) => {
    const target = document.getElementById(targetId);
    if (target) {
      target.focus();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, []);

  const skipToNavigation = useCallback(() => {
    const nav = document.querySelector('nav[role="navigation"], .main-navigation, #main-nav');
    if (nav) {
      const firstFocusable = nav.querySelector('a, button') as HTMLElement;
      if (firstFocusable) {
        firstFocusable.focus();
        firstFocusable.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, []);

  const skipToSearch = useCallback(() => {
    const search = document.querySelector('input[type="search"], .search-input, #search') as HTMLElement;
    if (search) {
      search.focus();
      search.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, []);

  return { skipToContent, skipToNavigation, skipToSearch };
};

/**
 * Hook for Polish business form keyboard navigation
 */
export const usePolishFormNavigation = () => {
  const formRef = useRef<HTMLFormElement>(null);
  const [errors, setErrors] = useState<Array<{ field: string; message: string }>>([]);

  const createErrorSummary = useCallback((formErrors: Array<{ field: string; message: string }>) => {
    setErrors(formErrors);
    
    if (!formRef.current || formErrors.length === 0) return;

    // Remove existing error summary
    const existingSummary = formRef.current.querySelector('.error-summary');
    if (existingSummary) {
      existingSummary.remove();
    }

    // Create new error summary
    const errorSummary = document.createElement('div');
    errorSummary.className = 'error-summary';
    errorSummary.setAttribute('role', 'alert');
    errorSummary.setAttribute('aria-live', 'assertive');
    errorSummary.setAttribute('tabindex', '-1');

    const heading = document.createElement('h2');
    heading.textContent = formErrors.length === 1 
      ? 'Znaleziono 1 błąd w formularzu:' 
      : `Znaleziono ${formErrors.length} błędów w formularzu:`;
    errorSummary.appendChild(heading);

    const errorList = document.createElement('ul');
    formErrors.forEach(error => {
      const listItem = document.createElement('li');
      const link = document.createElement('a');
      link.href = `#${error.field}`;
      link.textContent = error.message;
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const field = document.getElementById(error.field);
        if (field) {
          field.focus();
          field.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
      listItem.appendChild(link);
      errorList.appendChild(listItem);
    });
    errorSummary.appendChild(errorList);

    // Insert at beginning of form
    formRef.current.insertBefore(errorSummary, formRef.current.firstChild);

    // Focus error summary
    errorSummary.focus();
  }, []);

  const clearErrorSummary = useCallback(() => {
    setErrors([]);
    if (formRef.current) {
      const errorSummary = formRef.current.querySelector('.error-summary');
      if (errorSummary) {
        errorSummary.remove();
      }
    }
  }, []);

  const focusFirstInvalidField = useCallback(() => {
    if (!formRef.current) return;
    
    const invalidField = formRef.current.querySelector('[aria-invalid="true"]') as HTMLElement;
    if (invalidField) {
      invalidField.focus();
      invalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, []);

  // Set up form keyboard shortcuts
  useEffect(() => {
    const form = formRef.current;
    if (!form) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl+Enter to submit form
      if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault();
        const submitButton = form.querySelector('[type="submit"]') as HTMLButtonElement;
        if (submitButton) {
          submitButton.click();
        }
      }
    };

    form.addEventListener('keydown', handleKeyDown);

    return () => {
      form.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return {
    formRef,
    errors,
    createErrorSummary,
    clearErrorSummary,
    focusFirstInvalidField,
  };
};

/**
 * Hook for table keyboard navigation
 */
export const useTableNavigation = () => {
  const tableRef = useRef<HTMLTableElement>(null);

  useEffect(() => {
    const table = tableRef.current;
    if (!table) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      
      // Only handle navigation for focusable table elements
      if (!target.matches('th, td, button, a, input, select')) return;

      const cell = target.closest('th, td') as HTMLTableCellElement;
      if (!cell) return;

      const row = cell.parentElement as HTMLTableRowElement;
      const cellIndex = Array.from(row.children).indexOf(cell);
      const rowIndex = Array.from(table.rows).indexOf(row);

      let newRow: HTMLTableRowElement | null = null;
      let newCell: HTMLTableCellElement | null = null;

      switch (event.key) {
        case 'ArrowUp':
          event.preventDefault();
          newRow = table.rows[rowIndex - 1];
          if (newRow) {
            newCell = newRow.children[cellIndex] as HTMLTableCellElement;
          }
          break;
        case 'ArrowDown':
          event.preventDefault();
          newRow = table.rows[rowIndex + 1];
          if (newRow) {
            newCell = newRow.children[cellIndex] as HTMLTableCellElement;
          }
          break;
        case 'ArrowLeft':
          event.preventDefault();
          newCell = cell.previousElementSibling as HTMLTableCellElement;
          break;
        case 'ArrowRight':
          event.preventDefault();
          newCell = cell.nextElementSibling as HTMLTableCellElement;
          break;
        case 'Home':
          if (event.ctrlKey) {
            event.preventDefault();
            newCell = table.rows[0]?.children[0] as HTMLTableCellElement;
          } else {
            event.preventDefault();
            newCell = row.children[0] as HTMLTableCellElement;
          }
          break;
        case 'End':
          if (event.ctrlKey) {
            event.preventDefault();
            const lastRow = table.rows[table.rows.length - 1];
            newCell = lastRow?.children[lastRow.children.length - 1] as HTMLTableCellElement;
          } else {
            event.preventDefault();
            newCell = row.children[row.children.length - 1] as HTMLTableCellElement;
          }
          break;
      }

      if (newCell) {
        const focusableElement = newCell.querySelector('button, a, input, select') as HTMLElement || newCell;
        focusableElement.focus();
      }
    };

    table.addEventListener('keydown', handleKeyDown);

    return () => {
      table.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return tableRef;
};

/**
 * Hook for managing focus restoration after route changes
 */
export const useFocusRestoration = () => {
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const saveFocus = useCallback(() => {
    previousFocusRef.current = document.activeElement as HTMLElement;
  }, []);

  const restoreFocus = useCallback(() => {
    if (previousFocusRef.current && document.contains(previousFocusRef.current)) {
      previousFocusRef.current.focus();
    } else {
      // Focus main content if previous element is not available
      const main = document.querySelector('main, [role="main"], #main-content') as HTMLElement;
      if (main) {
        main.focus();
      }
    }
  }, []);

  const focusMainContent = useCallback(() => {
    const main = document.querySelector('main, [role="main"], #main-content') as HTMLElement;
    if (main) {
      main.setAttribute('tabindex', '-1');
      main.focus();
      main.addEventListener('blur', () => {
        main.removeAttribute('tabindex');
      }, { once: true });
    }
  }, []);

  return { saveFocus, restoreFocus, focusMainContent };
};