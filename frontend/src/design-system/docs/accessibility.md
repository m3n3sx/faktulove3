# Accessibility Guidelines

The FaktuLove Design System is built with accessibility as a core principle, ensuring that all users, including those with disabilities, can effectively use Polish business applications.

## 🎯 Accessibility Standards

### WCAG 2.1 Level AA Compliance
All components meet or exceed WCAG 2.1 Level AA standards:

- **Perceivable**: Information is presentable in ways users can perceive
- **Operable**: Interface components are operable by all users
- **Understandable**: Information and UI operation are understandable
- **Robust**: Content is robust enough for various assistive technologies

### Polish Language Support
- Proper `lang="pl"` attributes for Polish content
- Screen reader announcements in Polish
- Cultural considerations for Polish users
- Support for Polish keyboard layouts

## 🎨 Visual Accessibility

### Color Contrast
All color combinations meet WCAG AA contrast requirements:

```tsx
// Minimum contrast ratios
const contrastRatios = {
  normalText: 4.5, // 4.5:1 for normal text
  largeText: 3.0,  // 3.0:1 for large text (18px+ or 14px+ bold)
  uiComponents: 3.0, // 3.0:1 for UI components and graphics
};
```

### Color Independence
Information is never conveyed by color alone:

```tsx
// ✅ Good - uses icon + color + text
<Button variant="danger" icon={<AlertIcon />}>
  Usuń fakturę
</Button>

// ❌ Avoid - color only
<Button style={{ color: 'red' }}>
  Delete
</Button>
```

### Focus Indicators
All interactive elements have visible focus indicators:

```css
/* Focus styles are automatically applied */
.ds-button:focus-visible {
  outline: 2px solid var(--ds-color-primary-600);
  outline-offset: 2px;
}
```

## ⌨️ Keyboard Navigation

### Tab Order
All components support logical tab order:

```tsx
function AccessibleForm() {
  return (
    <form>
      {/* Tab order: 1 */}
      <Input aria-label="Nazwa firmy" />
      
      {/* Tab order: 2 */}
      <Input aria-label="NIP" />
      
      {/* Tab order: 3 */}
      <Button type="submit">Zapisz</Button>
    </form>
  );
}
```

### Keyboard Shortcuts
Standard keyboard interactions are supported:

| Key | Action | Components |
|-----|--------|------------|
| `Tab` | Move focus forward | All interactive elements |
| `Shift + Tab` | Move focus backward | All interactive elements |
| `Enter` | Activate element | Buttons, links |
| `Space` | Activate element | Buttons, checkboxes |
| `Arrow Keys` | Navigate options | Select, radio groups |
| `Escape` | Close/cancel | Modals, dropdowns |

### Focus Management
```tsx
import { useFocusManagement } from '@faktulove/design-system';

function Modal({ isOpen, onClose }) {
  const { focusRef, restoreFocus } = useFocusManagement();

  useEffect(() => {
    if (isOpen) {
      // Focus first element in modal
      focusRef.current?.focus();
    } else {
      // Restore focus to trigger element
      restoreFocus();
    }
  }, [isOpen]);

  return (
    <div role="dialog" aria-modal="true">
      <button ref={focusRef} onClick={onClose}>
        Zamknij
      </button>
    </div>
  );
}
```

## 🔊 Screen Reader Support

### ARIA Labels and Descriptions
All components include proper ARIA attributes:

```tsx
// Input with label and description
<Input
  aria-label="Numer faktury"
  aria-describedby="invoice-help"
  placeholder="FV/2024/001"
/>
<div id="invoice-help">
  Format: FV/ROK/NUMER
</div>

// Button with description
<Button
  aria-label="Usuń fakturę"
  aria-describedby="delete-warning"
>
  <TrashIcon />
</Button>
<div id="delete-warning" className="sr-only">
  Ta akcja jest nieodwracalna
</div>
```

### Live Regions
Dynamic content changes are announced:

```tsx
function StatusMessage({ message, type }) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className={`status-${type}`}
    >
      {message}
    </div>
  );
}

// Usage
<StatusMessage 
  message="Faktura została zapisana pomyślnie" 
  type="success" 
/>
```

### Screen Reader Only Content
```tsx
// Hidden content for screen readers
<span className="sr-only">
  Pole wymagane
</span>

// CSS for sr-only class
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## 🧩 Component-Specific Accessibility

### Button Accessibility
```tsx
// Basic accessible button
<Button aria-label="Zapisz fakturę">
  <SaveIcon />
</Button>

// Button with loading state
<Button loading aria-label="Zapisywanie faktury...">
  Zapisz
</Button>

// Disabled button with explanation
<Button 
  disabled 
  aria-label="Zapisz fakturę"
  aria-describedby="save-disabled-reason"
>
  Zapisz
</Button>
<div id="save-disabled-reason" className="sr-only">
  Wypełnij wszystkie wymagane pola
</div>
```

### Form Accessibility
```tsx
function AccessibleForm() {
  return (
    <form role="form" aria-labelledby="form-title">
      <h2 id="form-title">Nowa faktura</h2>
      
      <fieldset>
        <legend>Dane podstawowe</legend>
        
        <Input
          required
          aria-label="Numer faktury"
          aria-describedby="invoice-number-help"
          error={errors.invoiceNumber}
          aria-invalid={!!errors.invoiceNumber}
        />
        <div id="invoice-number-help">
          Numer faktury w formacie FV/ROK/NUMER
        </div>
      </fieldset>
      
      <Button type="submit" aria-describedby="submit-help">
        Utwórz fakturę
      </Button>
      <div id="submit-help" className="sr-only">
        Naciśnij Enter lub kliknij, aby utworzyć fakturę
      </div>
    </form>
  );
}
```

### Table Accessibility
```tsx
function AccessibleTable({ data, columns }) {
  return (
    <table role="table" aria-label="Lista faktur">
      <caption>
        Tabela zawiera {data.length} faktur. 
        Użyj klawiszy strzałek do nawigacji.
      </caption>
      
      <thead>
        <tr role="row">
          {columns.map(column => (
            <th 
              key={column.key}
              role="columnheader"
              aria-sort={getSortDirection(column.key)}
            >
              {column.header}
            </th>
          ))}
        </tr>
      </thead>
      
      <tbody>
        {data.map((row, index) => (
          <tr key={row.id} role="row">
            {columns.map(column => (
              <td 
                key={column.key}
                role="gridcell"
                aria-describedby={`row-${index}-${column.key}-desc`}
              >
                {row[column.key]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## 🇵🇱 Polish-Specific Accessibility

### Language Attributes
```tsx
// Polish content with proper language attribute
<div lang="pl">
  <h1>System fakturowania</h1>
  <p>Zarządzaj fakturami swojej firmy</p>
</div>

// Mixed language content
<div lang="pl">
  <p>Numer <span lang="en">ID</span>: 12345</p>
</div>
```

### Polish Business Terms
```tsx
// Proper ARIA labels in Polish
<Input
  aria-label="Numer Identyfikacji Podatkowej (NIP)"
  placeholder="123-456-78-90"
/>

<Select aria-label="Stawka podatku VAT">
  <option value="23">23% - stawka podstawowa</option>
  <option value="8">8% - stawka obniżona</option>
  <option value="5">5% - stawka obniżona</option>
  <option value="0">0% - stawka zerowa</option>
</Select>
```

### Currency and Number Formatting
```tsx
// Accessible currency display
<span 
  aria-label="Kwota: tysiąc dwieście trzydzieści cztery złote i pięćdziesiąt sześć groszy"
>
  1 234,56 zł
</span>

// Accessible percentage
<span aria-label="Dwadzieścia trzy procent">
  23%
</span>
```

## 🧪 Accessibility Testing

### Automated Testing
```tsx
import { renderWithA11y, testPolishA11y } from '@faktulove/design-system/testing';

test('component meets accessibility standards', async () => {
  const { container } = renderWithA11y(
    <Button>Test Button</Button>
  );
  
  // Test WCAG compliance
  await testPolishA11y(container);
});

test('keyboard navigation works correctly', async () => {
  const { container } = renderWithA11y(
    <form>
      <Input aria-label="First input" />
      <Input aria-label="Second input" />
      <Button>Submit</Button>
    </form>
  );
  
  // Test tab navigation
  await keyboardTestUtils.testTabNavigation(container);
});
```

### Manual Testing Checklist

#### Visual Testing
- [ ] All text has sufficient color contrast
- [ ] Focus indicators are visible and clear
- [ ] Content is readable at 200% zoom
- [ ] No information is conveyed by color alone

#### Keyboard Testing
- [ ] All interactive elements are keyboard accessible
- [ ] Tab order is logical and intuitive
- [ ] Focus is properly managed in dynamic content
- [ ] Keyboard shortcuts work as expected

#### Screen Reader Testing
- [ ] All content is announced correctly
- [ ] ARIA labels and descriptions are meaningful
- [ ] Dynamic content changes are announced
- [ ] Polish content is pronounced correctly

### Testing Tools

#### Browser Extensions
- **axe DevTools**: Automated accessibility testing
- **WAVE**: Web accessibility evaluation
- **Lighthouse**: Accessibility audit included

#### Screen Readers
- **NVDA** (Windows): Free screen reader
- **JAWS** (Windows): Popular commercial screen reader
- **VoiceOver** (macOS): Built-in screen reader
- **Orca** (Linux): Open source screen reader

#### Polish Screen Reader Testing
```bash
# Test with Polish language settings
# Ensure proper pronunciation of Polish business terms
```

## 📋 Accessibility Checklist

### Component Development
- [ ] Semantic HTML elements used
- [ ] ARIA attributes added where needed
- [ ] Keyboard navigation implemented
- [ ] Focus management handled
- [ ] Color contrast verified
- [ ] Screen reader tested
- [ ] Polish language support verified

### Content Creation
- [ ] Meaningful alt text for images
- [ ] Descriptive link text
- [ ] Proper heading hierarchy
- [ ] Form labels associated with inputs
- [ ] Error messages are clear and helpful
- [ ] Instructions are provided where needed

### Testing
- [ ] Automated accessibility tests pass
- [ ] Manual keyboard testing completed
- [ ] Screen reader testing performed
- [ ] Color contrast verified
- [ ] Polish language testing done
- [ ] User testing with disabled users

## 🔧 Accessibility Utilities

### Focus Management
```tsx
import { 
  useFocusManagement,
  createFocusTrap,
  restoreFocus 
} from '@faktulove/design-system';

// Focus trap for modals
const focusTrap = createFocusTrap(modalRef.current);
focusTrap.activate();

// Restore focus when modal closes
focusTrap.deactivate();
restoreFocus();
```

### ARIA Utilities
```tsx
import { 
  generateAriaId,
  announceToScreenReader,
  setAriaLive 
} from '@faktulove/design-system';

// Generate unique IDs for ARIA relationships
const labelId = generateAriaId('label');
const descId = generateAriaId('description');

// Announce messages to screen readers
announceToScreenReader('Faktura została zapisana', 'polite');

// Set live region content
setAriaLive('status', 'Ładowanie danych...', 'polite');
```

## 📚 Resources

### WCAG Guidelines
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Resources](https://webaim.org/)

### Polish Accessibility
- [Fundacja Widzialni](https://widzialni.org/) - Polish accessibility foundation
- [WCAG 2.1 w języku polskim](https://www.w3.org/Translations/WCAG21-pl/)
- [Dostępność cyfrowa](https://www.gov.pl/web/dostepnosc-cyfrowa)

### Testing Tools
- [axe-core](https://github.com/dequelabs/axe-core)
- [jest-axe](https://github.com/nickcolley/jest-axe)
- [Testing Library](https://testing-library.com/)

---

**Accessibility is not optional - it's essential for creating inclusive Polish business applications.** 🌟