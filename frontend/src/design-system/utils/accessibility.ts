// Accessibility Utilities
import { focusRings } from '../tokens/shadows';

// ARIA utilities
export const ariaUtils = {
  // Generate unique IDs for ARIA relationships
  generateId: (prefix: string = 'ds'): string => {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  },
  
  // Common ARIA attributes
  describedBy: (id: string) => ({ 'aria-describedby': id }),
  labelledBy: (id: string) => ({ 'aria-labelledby': id }),
  expanded: (isExpanded: boolean) => ({ 'aria-expanded': isExpanded }),
  selected: (isSelected: boolean) => ({ 'aria-selected': isSelected }),
  checked: (isChecked: boolean) => ({ 'aria-checked': isChecked }),
  disabled: (isDisabled: boolean) => ({ 'aria-disabled': isDisabled }),
  hidden: (isHidden: boolean) => ({ 'aria-hidden': isHidden }),
  live: (politeness: 'polite' | 'assertive' | 'off' = 'polite') => ({ 'aria-live': politeness }),
  
  // Polish language support
  lang: (lang: string = 'pl') => ({ lang }),
} as const;

// Focus management utilities
export const focusUtils = {
  // Focus ring styles
  getFocusRing: (variant: keyof typeof focusRings = 'default'): string => {
    return focusRings[variant];
  },
  
  // Focus trap for modals and dropdowns
  trapFocus: (element: HTMLElement): (() => void) => {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>;
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;
      
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };
    
    element.addEventListener('keydown', handleTabKey);
    firstElement?.focus();
    
    // Return cleanup function
    return () => {
      element.removeEventListener('keydown', handleTabKey);
    };
  },
  
  // Restore focus after modal closes
  restoreFocus: (previousElement: HTMLElement | null) => {
    if (previousElement && typeof previousElement.focus === 'function') {
      previousElement.focus();
    }
  },
} as const;

// Keyboard navigation utilities
export const keyboardUtils = {
  // Common keyboard event handlers
  onEnterOrSpace: (callback: () => void) => (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      callback();
    }
  },
  
  onEscape: (callback: () => void) => (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      callback();
    }
  },
  
  onArrowKeys: (callbacks: {
    up?: () => void;
    down?: () => void;
    left?: () => void;
    right?: () => void;
  }) => (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault();
        callbacks.up?.();
        break;
      case 'ArrowDown':
        e.preventDefault();
        callbacks.down?.();
        break;
      case 'ArrowLeft':
        e.preventDefault();
        callbacks.left?.();
        break;
      case 'ArrowRight':
        e.preventDefault();
        callbacks.right?.();
        break;
    }
  },
} as const;

// Screen reader utilities
export const screenReaderUtils = {
  // Screen reader only text (visually hidden)
  srOnly: {
    position: 'absolute' as const,
    width: '1px',
    height: '1px',
    padding: '0',
    margin: '-1px',
    overflow: 'hidden' as const,
    clip: 'rect(0, 0, 0, 0)',
    whiteSpace: 'nowrap' as const,
    border: '0',
  },
  
  // Announce changes to screen readers
  announce: (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.style.width = '1px';
    announcement.style.height = '1px';
    announcement.style.overflow = 'hidden';
    
    document.body.appendChild(announcement);
    announcement.textContent = message;
    
    // Clean up after announcement
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  },
} as const;

// Color contrast utilities
export const contrastUtils = {
  // Check if color meets WCAG contrast requirements
  meetsContrastRequirement: (foreground: string, background: string, level: 'AA' | 'AAA' = 'AA'): boolean => {
    // This is a simplified implementation
    // In a real application, you would use a proper color contrast calculation library
    const requiredRatio = level === 'AAA' ? 7 : 4.5;
    // Implementation would calculate actual contrast ratio
    return true; // Placeholder
  },
  
  // Get accessible text color for background
  getAccessibleTextColor: (backgroundColor: string): string => {
    // Simplified implementation - would calculate luminance in real app
    return backgroundColor.includes('900') || backgroundColor.includes('800') ? '#ffffff' : '#000000';
  },
} as const;

// Polish accessibility considerations
export const polishA11yUtils = {
  // Polish language specific ARIA labels
  polishLabels: {
    close: 'Zamknij',
    open: 'Otwórz',
    menu: 'Menu',
    search: 'Szukaj',
    loading: 'Ładowanie',
    error: 'Błąd',
    success: 'Sukces',
    warning: 'Ostrzeżenie',
    required: 'Wymagane',
    optional: 'Opcjonalne',
    previous: 'Poprzedni',
    next: 'Następny',
    first: 'Pierwszy',
    last: 'Ostatni',
    page: 'Strona',
    of: 'z',
    invoice: 'Faktura',
    contractor: 'Kontrahent',
    amount: 'Kwota',
    date: 'Data',
    status: 'Status',
    edit: 'Edytuj',
    delete: 'Usuń',
    save: 'Zapisz',
    cancel: 'Anuluj',
  },
  
  // Format Polish currency for screen readers
  formatCurrencyForScreenReader: (amount: number): string => {
    return `${amount.toFixed(2).replace('.', ',')} złotych`;
  },
  
  // Format Polish date for screen readers
  formatDateForScreenReader: (date: Date): string => {
    return date.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  },
} as const;

// Accessibility testing utilities for development
export const a11yTestUtils = {
  // Log accessibility warnings in development
  logA11yWarning: (message: string, element?: HTMLElement) => {
    if (process.env.NODE_ENV === 'development') {
      console.warn(`[A11Y Warning]: ${message}`, element);
    }
  },
  
  // Check for missing ARIA labels
  checkAriaLabels: (element: HTMLElement) => {
    const interactiveElements = element.querySelectorAll('button, a, input, select, textarea');
    interactiveElements.forEach((el) => {
      const hasLabel = el.getAttribute('aria-label') || 
                      el.getAttribute('aria-labelledby') || 
                      el.textContent?.trim();
      
      if (!hasLabel) {
        a11yTestUtils.logA11yWarning('Interactive element missing accessible label', el as HTMLElement);
      }
    });
  },
} as const;

export type AriaUtilsType = typeof ariaUtils;
export type FocusUtilsType = typeof focusUtils;
export type KeyboardUtilsType = typeof keyboardUtils;
export type ScreenReaderUtilsType = typeof screenReaderUtils;