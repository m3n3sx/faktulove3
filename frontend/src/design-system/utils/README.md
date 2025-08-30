# Design System Accessibility Infrastructure

This directory contains comprehensive accessibility utilities and testing infrastructure for the FaktuLove design system, with special focus on Polish business requirements and WCAG 2.1 Level AA compliance.

## Overview

The accessibility infrastructure provides:

1. **Automated Accessibility Testing** - jest-axe integration with Polish-specific configurations
2. **ARIA Support Utilities** - Comprehensive ARIA attributes and screen reader compatibility
3. **Focus Management** - Advanced focus handling for modals, dropdowns, and complex UI patterns
4. **Keyboard Navigation Testing** - Automated testing patterns for keyboard accessibility
5. **Polish Business Accessibility** - Specialized support for Polish accounting and business forms

## Files Structure

```
utils/
├── testUtils.ts                    # Main accessibility testing utilities
├── keyboardTestPatterns.ts         # Keyboard navigation test patterns
├── ariaUtils.ts                    # ARIA support and screen reader utilities
├── focusManagement.ts              # Focus management for complex components
├── accessibility.ts                # Core accessibility utilities (existing)
└── __tests__/
    ├── accessibility.test.ts       # Comprehensive accessibility tests
    ├── ariaUtils.test.ts           # ARIA utilities tests
    └── focusManagement.test.ts     # Focus management tests
```

## Key Features

### 1. Accessibility Testing Framework (`testUtils.ts`)

#### Core Testing Functions
- `renderWithA11y()` - Enhanced render function with accessibility setup
- `testA11y()` - Basic accessibility violation testing
- `testPolishA11y()` - Polish-specific accessibility testing with custom rules
- `runA11yTestSuite()` - Comprehensive accessibility test suite

#### Polish-Specific Configuration
```typescript
export const polishA11yConfig = {
  rules: {
    'html-has-lang': { enabled: true },
    'color-contrast': { enabled: true },
    'aria-allowed-attr': { enabled: true },
    // ... more Polish business-specific rules
  },
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
};
```

#### Keyboard Navigation Testing
- Tab navigation testing
- Shift+Tab reverse navigation
- Enter/Space key activation
- Escape key handling
- Arrow key navigation for dropdowns and radio groups

#### Screen Reader Testing
- ARIA label validation
- Role attribute testing
- ARIA state management
- Live region testing

#### Polish Business Testing
- NIP input accessibility validation
- Currency input with PLN formatting
- VAT rate selector accessibility
- Polish date format validation (DD.MM.YYYY)

### 2. Keyboard Navigation Patterns (`keyboardTestPatterns.ts`)

Provides automated testing patterns for different component types:

- **Button Pattern** - Enter and Space key activation
- **Input Pattern** - Form field navigation and input
- **Select Pattern** - Arrow key navigation in dropdowns
- **Radio Group Pattern** - Arrow key navigation within groups
- **Checkbox Pattern** - Space key toggle
- **Modal Pattern** - Focus trap and Escape handling
- **Dropdown Pattern** - Menu navigation with Home/End keys
- **Polish Business Form Pattern** - Specialized business form navigation

### 3. ARIA Support (`ariaUtils.ts`)

#### ARIA Constants and Utilities
```typescript
// Role definitions
export const ARIA_ROLES = {
  BUTTON: 'button',
  DIALOG: 'dialog',
  COMBOBOX: 'combobox',
  // ... comprehensive role definitions
};

// Property definitions
export const ARIA_PROPERTIES = {
  LABEL: 'aria-label',
  EXPANDED: 'aria-expanded',
  LIVE: 'aria-live',
  // ... all ARIA properties
};
```

#### Attribute Generation
```typescript
// Generate ARIA attributes for components
const buttonAttrs = generateAriaAttributes.button({
  label: 'Close Dialog',
  pressed: false,
  hasPopup: 'MENU'
});
```

#### Polish Labels
```typescript
export const polishAriaLabels = {
  CLOSE: 'Zamknij',
  SAVE: 'Zapisz',
  NIP_INPUT: 'Numer NIP',
  CURRENCY_INPUT: 'Kwota w złotych',
  // ... comprehensive Polish translations
};
```

#### Screen Reader Announcer
```typescript
const announcer = ScreenReaderAnnouncer.getInstance();
announcer.announcePolite('Form saved successfully');
announcer.announceError('Invalid NIP number');
announcer.announceSuccess('Invoice created');
```

### 4. Focus Management (`focusManagement.ts`)

#### Modal Focus Management
```typescript
const modalManager = new ModalFocusManager(modalElement, {
  initialFocus: '#first-input',
  returnFocus: triggerButton,
  escapeDeactivates: true
});

modalManager.activate(); // Trap focus in modal
modalManager.deactivate(); // Restore focus to trigger
```

#### Dropdown Focus Management
```typescript
const dropdownManager = new DropdownFocusManager(trigger, dropdown);
dropdownManager.open(); // Focus first item
dropdownManager.close(); // Return focus to trigger
```

#### Roving Tabindex Manager
```typescript
const rovingManager = new RovingTabindexManager(tablist);
rovingManager.setActiveItem(1); // Set active tab
rovingManager.focusActiveItem(); // Focus active tab
```

#### Polish Form Focus Manager
```typescript
const formManager = new PolishFormFocusManager(form);
formManager.createErrorSummary([
  { field: 'nip', message: 'Nieprawidłowy numer NIP' }
]);
formManager.focusFirstInvalidField();
```

## Usage Examples

### Basic Component Testing

```typescript
import { renderWithA11y, testPolishA11y, runA11yTestSuite } from '../utils/testUtils';

describe('MyComponent', () => {
  it('should be accessible', async () => {
    const { container } = renderWithA11y(<MyComponent />);
    await testPolishA11y(container);
  });

  it('should pass comprehensive accessibility tests', async () => {
    const { container } = renderWithA11y(<MyComponent />);
    await runA11yTestSuite(container, {
      testKeyboard: true,
      testScreenReader: true,
      testPolishBusiness: true
    });
  });
});
```

### Component with ARIA Support

```typescript
import { generateAriaAttributes, polishAriaLabels } from '../utils/ariaUtils';

const Button = ({ children, onClick, pressed = false }) => {
  const ariaAttrs = generateAriaAttributes.button({
    label: polishAriaLabels.CLOSE,
    pressed,
    hasPopup: 'MENU'
  });

  return (
    <button onClick={onClick} {...ariaAttrs}>
      {children}
    </button>
  );
};
```

### Modal with Focus Management

```typescript
import { ModalFocusManager } from '../utils/focusManagement';

const Modal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef();
  const focusManagerRef = useRef();

  useEffect(() => {
    if (isOpen && modalRef.current) {
      focusManagerRef.current = new ModalFocusManager(modalRef.current);
      focusManagerRef.current.activate();
    }

    return () => {
      if (focusManagerRef.current) {
        focusManagerRef.current.deactivate();
      }
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div ref={modalRef} role="dialog" aria-modal="true">
      {children}
    </div>
  );
};
```

## Polish Business Accessibility Features

### NIP Input Validation
- Real-time NIP format validation
- Screen reader announcements in Polish
- Proper error message association

### Currency Input (PLN)
- Polish złoty formatting
- Decimal precision handling
- Accessible value announcements

### VAT Rate Selector
- Standard Polish VAT rates (23%, 8%, 5%, 0%)
- Keyboard navigation
- Screen reader support

### Date Input (Polish Format)
- DD.MM.YYYY format validation
- Polish date announcements
- Fiscal year awareness

## Testing Strategy

The accessibility infrastructure supports multiple testing approaches:

1. **Unit Tests** - Individual component accessibility
2. **Integration Tests** - Component interaction accessibility
3. **Keyboard Navigation Tests** - Automated keyboard testing
4. **Screen Reader Tests** - ARIA and semantic testing
5. **Polish Business Tests** - Domain-specific accessibility

## WCAG 2.1 Level AA Compliance

All utilities are designed to ensure compliance with:

- **Perceivable** - Color contrast, text alternatives, adaptable content
- **Operable** - Keyboard accessible, no seizures, navigable
- **Understandable** - Readable, predictable, input assistance
- **Robust** - Compatible with assistive technologies

## Browser and Assistive Technology Support

Tested with:
- **Screen Readers**: NVDA, JAWS, VoiceOver
- **Browsers**: Chrome, Firefox, Safari, Edge
- **Keyboard Navigation**: Full keyboard support
- **Polish Language**: Native Polish screen reader support

## Contributing

When adding new accessibility features:

1. Follow WCAG 2.1 Level AA guidelines
2. Include Polish translations for user-facing text
3. Add comprehensive tests using the provided utilities
4. Test with actual assistive technologies
5. Document usage examples and patterns

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [Polish Accessibility Guidelines](https://www.gov.pl/web/dostepnosc-cyfrowa)
- [jest-axe Documentation](https://github.com/nickcolley/jest-axe)