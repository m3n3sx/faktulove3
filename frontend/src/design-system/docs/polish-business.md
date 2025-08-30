# Polish Business Components

The FaktuLove Design System includes specialized components designed specifically for Polish business and accounting needs. These components handle Polish-specific formatting, validation, and business logic.

## 🇵🇱 Overview

Polish business applications have unique requirements that differ from international standards:

- **Currency**: Polish Złoty (PLN) formatting with proper decimal separators
- **Tax System**: Polish VAT rates and NIP validation
- **Date Formats**: DD.MM.YYYY format preferred in business contexts
- **Language**: Polish terminology and cultural conventions
- **Regulations**: Compliance with Polish accounting and tax regulations

## 💰 CurrencyInput Component

Handles Polish Złoty (PLN) currency formatting with proper localization.

### Basic Usage
```tsx
import { CurrencyInput } from '@faktulove/design-system';

function InvoiceForm() {
  const [amount, setAmount] = useState('');

  return (
    <CurrencyInput
      currency="PLN"
      value={amount}
      onChange={setAmount}
      placeholder="Wprowadź kwotę"
      aria-label="Kwota faktury"
    />
  );
}
```

### Features
- **Polish Number Formatting**: Uses space as thousands separator (1 234,56 zł)
- **Decimal Handling**: Comma as decimal separator (Polish standard)
- **Currency Symbol**: Displays "zł" suffix
- **Input Validation**: Prevents invalid characters
- **Accessibility**: Proper ARIA labels in Polish

### Props
```tsx
interface CurrencyInputProps {
  currency: 'PLN' | 'EUR' | 'USD';
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  success?: string;
  'aria-label': string;
  'aria-describedby'?: string;
}
```

### Examples
```tsx
// Basic PLN input
<CurrencyInput
  currency="PLN"
  placeholder="0,00 zł"
  aria-label="Kwota netto"
/>

// With validation
<CurrencyInput
  currency="PLN"
  value={amount}
  onChange={setAmount}
  error={errors.amount}
  aria-label="Kwota brutto"
  aria-describedby="amount-help"
/>
<div id="amount-help">
  Wprowadź kwotę w złotych polskich
</div>

// Disabled state
<CurrencyInput
  currency="PLN"
  value="1 234,56 zł"
  disabled
  aria-label="Kwota obliczona automatycznie"
/>
```

## 📅 DatePicker Component

Polish date picker with DD.MM.YYYY format and Polish calendar localization.

### Basic Usage
```tsx
import { DatePicker } from '@faktulove/design-system';

function InvoiceForm() {
  const [date, setDate] = useState('');

  return (
    <DatePicker
      value={date}
      onChange={setDate}
      format="DD.MM.YYYY"
      placeholder="dd.mm.rrrr"
      aria-label="Data wystawienia faktury"
    />
  );
}
```

### Features
- **Polish Date Format**: DD.MM.YYYY (e.g., 15.03.2024)
- **Polish Calendar**: Month and day names in Polish
- **Keyboard Navigation**: Arrow keys for date navigation
- **Validation**: Automatic date validation
- **Business Context**: Fiscal year awareness

### Props
```tsx
interface DatePickerProps {
  value?: string;
  onChange?: (date: string) => void;
  format?: 'DD.MM.YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
  placeholder?: string;
  minDate?: string;
  maxDate?: string;
  disabled?: boolean;
  error?: string;
  'aria-label': string;
}
```

### Examples
```tsx
// Invoice date picker
<DatePicker
  value={invoiceDate}
  onChange={setInvoiceDate}
  format="DD.MM.YYYY"
  placeholder="Data wystawienia"
  aria-label="Data wystawienia faktury"
/>

// Due date with validation
<DatePicker
  value={dueDate}
  onChange={setDueDate}
  minDate={invoiceDate} // Cannot be before invoice date
  error={errors.dueDate}
  aria-label="Termin płatności"
  aria-describedby="due-date-help"
/>
<div id="due-date-help">
  Termin płatności nie może być wcześniejszy niż data wystawienia
</div>

// Fiscal year selector
<DatePicker
  value={fiscalYear}
  onChange={setFiscalYear}
  format="YYYY"
  placeholder="Rok podatkowy"
  aria-label="Rok podatkowy"
/>
```

## 🧾 VATRateSelector Component

Selector for Polish VAT rates with standard rates pre-configured.

### Basic Usage
```tsx
import { VATRateSelector } from '@faktulove/design-system';

function ProductForm() {
  const [vatRate, setVatRate] = useState('23');

  return (
    <VATRateSelector
      value={vatRate}
      onChange={setVatRate}
      aria-label="Stawka VAT"
    />
  );
}
```

### Features
- **Standard Polish VAT Rates**: 23%, 8%, 5%, 0%
- **Rate Descriptions**: Clear descriptions for each rate
- **Accessibility**: Proper ARIA labels and descriptions
- **Validation**: Ensures valid VAT rate selection

### Polish VAT Rates
```tsx
const polishVATRates = [
  { value: '23', label: '23%', description: 'Stawka podstawowa' },
  { value: '8', label: '8%', description: 'Stawka obniżona' },
  { value: '5', label: '5%', description: 'Stawka obniżona' },
  { value: '0', label: '0%', description: 'Stawka zerowa' },
  { value: 'zw', label: 'zw.', description: 'Zwolnione z VAT' },
  { value: 'np', label: 'n.p.', description: 'Nie podlega VAT' },
];
```

### Props
```tsx
interface VATRateSelectorProps {
  value?: string;
  onChange?: (rate: string) => void;
  disabled?: boolean;
  error?: string;
  includeExemptions?: boolean; // Include "zw." and "n.p." options
  'aria-label': string;
}
```

### Examples
```tsx
// Basic VAT selector
<VATRateSelector
  value={vatRate}
  onChange={setVatRate}
  aria-label="Stawka VAT dla produktu"
/>

// With exemptions
<VATRateSelector
  value={vatRate}
  onChange={setVatRate}
  includeExemptions
  aria-label="Stawka VAT"
  aria-describedby="vat-help"
/>
<div id="vat-help">
  Wybierz odpowiednią stawkę VAT dla tego produktu lub usługi
</div>

// Service-specific rates
<VATRateSelector
  value={serviceVatRate}
  onChange={setServiceVatRate}
  aria-label="Stawka VAT dla usługi"
/>
```

## 🏢 NIPValidator Component

Input component with real-time NIP (Tax Identification Number) validation.

### Basic Usage
```tsx
import { NIPValidator } from '@faktulove/design-system';

function ClientForm() {
  const [nip, setNip] = useState('');
  const [isValid, setIsValid] = useState(false);

  return (
    <NIPValidator
      value={nip}
      onChange={setNip}
      onValidationChange={setIsValid}
      placeholder="123-456-78-90"
      aria-label="Numer NIP klienta"
    />
  );
}
```

### Features
- **Real-time Validation**: Validates NIP as user types
- **Automatic Formatting**: Formats NIP with hyphens (123-456-78-90)
- **Checksum Validation**: Validates NIP checksum algorithm
- **Error Messages**: Clear Polish error messages
- **API Integration**: Optional GUS API validation

### NIP Validation Rules
```tsx
const nipValidation = {
  length: 10, // Must be exactly 10 digits
  format: /^\d{3}-\d{3}-\d{2}-\d{2}$/, // With hyphens
  checksum: true, // Must pass checksum algorithm
  blacklist: ['0000000000', '1111111111'], // Invalid patterns
};
```

### Props
```tsx
interface NIPValidatorProps {
  value?: string;
  onChange?: (nip: string) => void;
  onValidationChange?: (isValid: boolean) => void;
  placeholder?: string;
  disabled?: boolean;
  validateWithGUS?: boolean; // Validate against GUS database
  'aria-label': string;
}
```

### Examples
```tsx
// Basic NIP validator
<NIPValidator
  value={clientNip}
  onChange={setClientNip}
  onValidationChange={setNipValid}
  placeholder="Wprowadź NIP"
  aria-label="Numer NIP klienta"
/>

// With GUS validation
<NIPValidator
  value={companyNip}
  onChange={setCompanyNip}
  validateWithGUS
  aria-label="NIP firmy"
  aria-describedby="nip-help"
/>
<div id="nip-help">
  NIP zostanie zweryfikowany w bazie GUS
</div>

// Read-only display
<NIPValidator
  value="123-456-78-90"
  disabled
  aria-label="NIP własnej firmy"
/>
```

### Validation Messages
```tsx
const nipValidationMessages = {
  invalid: 'Nieprawidłowy numer NIP',
  tooShort: 'NIP musi mieć 10 cyfr',
  tooLong: 'NIP nie może mieć więcej niż 10 cyfr',
  invalidChecksum: 'Nieprawidłowa suma kontrolna NIP',
  notFound: 'NIP nie został znaleziony w bazie GUS',
  valid: 'NIP jest prawidłowy',
};
```

## 📊 InvoiceStatusBadge Component

Status badge for Polish invoice lifecycle states.

### Basic Usage
```tsx
import { InvoiceStatusBadge } from '@faktulove/design-system';

function InvoiceList() {
  return (
    <div>
      {invoices.map(invoice => (
        <div key={invoice.id}>
          <span>{invoice.number}</span>
          <InvoiceStatusBadge status={invoice.status} />
        </div>
      ))}
    </div>
  );
}
```

### Features
- **Polish Status Labels**: Status names in Polish
- **Color Coding**: Semantic colors for different states
- **Accessibility**: Proper ARIA labels and roles
- **Customizable**: Support for custom status types

### Invoice Status Types
```tsx
type InvoiceStatus = 
  | 'draft'      // Szkic
  | 'sent'       // Wysłana
  | 'paid'       // Opłacona
  | 'overdue'    // Przeterminowana
  | 'cancelled'  // Anulowana
  | 'corrected'; // Skorygowana

const statusLabels = {
  draft: 'Szkic',
  sent: 'Wysłana',
  paid: 'Opłacona',
  overdue: 'Przeterminowana',
  cancelled: 'Anulowana',
  corrected: 'Skorygowana',
};
```

### Props
```tsx
interface InvoiceStatusBadgeProps {
  status: InvoiceStatus;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  'aria-label'?: string;
}
```

### Examples
```tsx
// Basic status badge
<InvoiceStatusBadge status="paid" />

// With custom size and icon
<InvoiceStatusBadge 
  status="overdue" 
  size="lg"
  showIcon
  aria-label="Status faktury: przeterminowana"
/>

// In table context
<table>
  <thead>
    <tr>
      <th>Numer</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    {invoices.map(invoice => (
      <tr key={invoice.id}>
        <td>{invoice.number}</td>
        <td>
          <InvoiceStatusBadge 
            status={invoice.status}
            aria-label={`Status faktury ${invoice.number}: ${statusLabels[invoice.status]}`}
          />
        </td>
      </tr>
    ))}
  </tbody>
</table>
```

## 🏛️ ComplianceIndicator Component

Indicator for Polish regulatory compliance status.

### Basic Usage
```tsx
import { ComplianceIndicator } from '@faktulove/design-system';

function ComplianceStatus() {
  return (
    <ComplianceIndicator
      type="jpk"
      status="compliant"
      aria-label="Status zgodności JPK_VAT"
    />
  );
}
```

### Features
- **Compliance Types**: JPK, KSeF, SAF-T support
- **Status Indicators**: Visual compliance status
- **Tooltips**: Detailed compliance information
- **Updates**: Real-time compliance monitoring

### Compliance Types
```tsx
type ComplianceType = 
  | 'jpk'    // Jednolity Plik Kontrolny
  | 'ksef'   // Krajowy System e-Faktur
  | 'saft'   // Standard Audit File for Tax
  | 'vat'    // VAT compliance
  | 'pit'    // PIT compliance
  | 'cit';   // CIT compliance

type ComplianceStatus = 
  | 'compliant'     // Zgodny
  | 'warning'       // Ostrzeżenie
  | 'non-compliant' // Niezgodny
  | 'unknown';      // Nieznany
```

### Examples
```tsx
// JPK compliance
<ComplianceIndicator
  type="jpk"
  status="compliant"
  lastCheck="2024-03-15"
  aria-label="JPK_VAT: zgodny, ostatnia weryfikacja 15.03.2024"
/>

// KSeF status with warning
<ComplianceIndicator
  type="ksef"
  status="warning"
  message="Wymagana aktualizacja certyfikatu"
  aria-label="KSeF: ostrzeżenie - wymagana aktualizacja certyfikatu"
/>

// Multiple compliance indicators
<div className="compliance-panel">
  <ComplianceIndicator type="jpk" status="compliant" />
  <ComplianceIndicator type="ksef" status="warning" />
  <ComplianceIndicator type="vat" status="compliant" />
</div>
```

## 🧮 Polish Business Utilities

### Number Formatting
```tsx
import { formatPolishNumber, formatPolishCurrency } from '@faktulove/design-system';

// Format numbers with Polish conventions
const formattedNumber = formatPolishNumber(1234567.89);
// Result: "1 234 567,89"

const formattedCurrency = formatPolishCurrency(1234.56);
// Result: "1 234,56 zł"
```

### Date Formatting
```tsx
import { formatPolishDate, parsePolishDate } from '@faktulove/design-system';

// Format dates for Polish business context
const formattedDate = formatPolishDate(new Date(), 'DD.MM.YYYY');
// Result: "15.03.2024"

const parsedDate = parsePolishDate('15.03.2024');
// Result: Date object
```

### Validation Utilities
```tsx
import { 
  validateNIP, 
  validateREGON, 
  validatePolishPostalCode 
} from '@faktulove/design-system';

// Validate Polish business identifiers
const nipValid = validateNIP('1234567890');
const regonValid = validateREGON('123456789');
const postalCodeValid = validatePolishPostalCode('00-001');
```

## 🎨 Styling Polish Components

### CSS Custom Properties
```css
:root {
  /* Polish currency colors */
  --ds-currency-pln-color: #2563eb;
  --ds-currency-symbol-color: #6b7280;
  
  /* VAT rate colors */
  --ds-vat-standard-color: #059669;
  --ds-vat-reduced-color: #d97706;
  --ds-vat-zero-color: #6b7280;
  
  /* Status colors */
  --ds-status-paid-color: #059669;
  --ds-status-overdue-color: #dc2626;
  --ds-status-draft-color: #6b7280;
}
```

### Component Customization
```tsx
// Custom styled currency input
<CurrencyInput
  currency="PLN"
  className="custom-currency-input"
  style={{
    '--ds-input-border-color': '#2563eb',
    '--ds-currency-symbol-color': '#1d4ed8',
  }}
/>
```

## 🧪 Testing Polish Components

### Unit Testing
```tsx
import { render, screen } from '@testing-library/react';
import { CurrencyInput, NIPValidator } from '@faktulove/design-system';

test('formats PLN currency correctly', () => {
  render(<CurrencyInput currency="PLN" value="1234.56" />);
  expect(screen.getByDisplayValue('1 234,56 zł')).toBeInTheDocument();
});

test('validates NIP correctly', async () => {
  const { user } = render(<NIPValidator />);
  
  await user.type(screen.getByRole('textbox'), '1234567890');
  expect(screen.getByDisplayValue('123-456-78-90')).toBeInTheDocument();
});
```

### Accessibility Testing
```tsx
import { testPolishA11y } from '@faktulove/design-system/testing';

test('Polish components are accessible', async () => {
  const { container } = render(
    <div>
      <CurrencyInput currency="PLN" aria-label="Kwota" />
      <VATRateSelector aria-label="Stawka VAT" />
      <NIPValidator aria-label="Numer NIP" />
    </div>
  );
  
  await testPolishA11y(container);
});
```

## 📚 Resources

### Polish Business Regulations
- [Ministerstwo Finansów](https://www.gov.pl/web/finanse) - Polish Ministry of Finance
- [JPK Documentation](https://www.podatki.gov.pl/jednolity-plik-kontrolny/) - JPK requirements
- [KSeF Information](https://www.podatki.gov.pl/ksef/) - National e-Invoice System

### Polish Standards
- [Polish VAT Rates](https://www.podatki.gov.pl/vat/) - Current VAT rates
- [NIP Validation](https://sprawdz-status-vat.mf.gov.pl/) - NIP verification service
- [GUS Database](https://wyszukiwarkaregon.stat.gov.pl/) - Business registry

---

**These components make it easy to build compliant Polish business applications with proper formatting and validation.** 🇵🇱