/**
 * Polish Business Logic Test Suite
 * Tests Polish-specific business components, validation, formatting, and compliance
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';

// Import Polish business components
import { CurrencyInput } from '../components/business/CurrencyInput/CurrencyInput';
import { DatePicker } from '../components/business/DatePicker/DatePicker';
import { VATRateSelector } from '../components/business/VATRateSelector/VATRateSelector';
import { NIPValidator } from '../components/business/NIPValidator/NIPValidator';
import { InvoiceStatusBadge } from '../components/business/InvoiceStatusBadge/InvoiceStatusBadge';
import { ComplianceIndicator } from '../components/business/ComplianceIndicator/ComplianceIndicator';

// Import providers
import { DesignSystemProvider } from '../providers/DesignSystemProvider';
import { ThemeProvider } from '../providers/ThemeProvider';

// Import Polish business utilities
import { 
  formatPolishCurrency, 
  parsePolishCurrency,
  validateNIP,
  formatNIP,
  validateREGON,
  formatPolishDate,
  parsePolishDate,
  calculatePolishVAT,
  getPolishVATRates,
} from '../utils/polishBusiness';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

const TestWrapper: React.FC<{ children: React.ReactNode; theme?: string }> = ({ 
  children, 
  theme = 'light' 
}) => (
  <DesignSystemProvider>
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  </DesignSystemProvider>
);

describe('Polish Business Logic Tests', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
  });

  describe('CurrencyInput Component', () => {
    describe('Polish Currency Formatting', () => {
      it('formats PLN currency correctly', async () => {
        const handleChange = jest.fn();
        
        render(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              onChange={handleChange}
              aria-label="Amount in PLN"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/amount in pln/i);
        
        // Test basic formatting
        await user.type(input, '1234.56');
        expect(input).toHaveValue('1 234,56 zł');
        expect(handleChange).toHaveBeenCalledWith(1234.56);
      });

      it('handles large amounts correctly', async () => {
        render(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              aria-label="Large amount"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/large amount/i);
        
        await user.type(input, '1234567.89');
        expect(input).toHaveValue('1 234 567,89 zł');
      });

      it('handles decimal precision correctly', async () => {
        render(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              precision={2}
              aria-label="Precise amount"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/precise amount/i);
        
        // Test rounding to 2 decimal places
        await user.type(input, '123.456');
        expect(input).toHaveValue('123,46 zł');
      });

      it('validates minimum and maximum amounts', async () => {
        render(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              min={10}
              max={1000}
              aria-label="Validated amount"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/validated amount/i);
        
        // Test below minimum
        await user.type(input, '5');
        expect(screen.getByText(/minimum amount is 10,00 zł/i)).toBeInTheDocument();
        
        // Test above maximum
        await user.clear(input);
        await user.type(input, '1500');
        expect(screen.getByText(/maximum amount is 1 000,00 zł/i)).toBeInTheDocument();
      });

      it('handles negative amounts when allowed', async () => {
        render(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              allowNegative={true}
              aria-label="Negative amount"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/negative amount/i);
        
        await user.type(input, '-123.45');
        expect(input).toHaveValue('-123,45 zł');
      });

      it('prevents negative amounts when not allowed', async () => {
        render(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              allowNegative={false}
              aria-label="Positive only amount"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/positive only amount/i);
        
        await user.type(input, '-123.45');
        expect(input).toHaveValue('123,45 zł');
      });
    });

    describe('Currency Parsing', () => {
      it('parses formatted currency strings correctly', () => {
        expect(parsePolishCurrency('1 234,56 zł')).toBe(1234.56);
        expect(parsePolishCurrency('123,45 zł')).toBe(123.45);
        expect(parsePolishCurrency('1 000 000,00 zł')).toBe(1000000);
        expect(parsePolishCurrency('-500,25 zł')).toBe(-500.25);
      });

      it('handles various input formats', () => {
        expect(parsePolishCurrency('1234.56')).toBe(1234.56);
        expect(parsePolishCurrency('1,234.56')).toBe(1234.56);
        expect(parsePolishCurrency('1 234.56')).toBe(1234.56);
        expect(parsePolishCurrency('1234,56')).toBe(1234.56);
      });
    });

    describe('Accessibility', () => {
      it('maintains accessibility with currency formatting', async () => {
        const { container } = render(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              aria-label="Accessible currency input"
              aria-describedby="currency-help"
            />
            <div id="currency-help">
              Enter amount in Polish złoty
            </div>
          </TestWrapper>
        );

        const input = screen.getByLabelText(/accessible currency input/i);
        expect(input).toHaveAttribute('aria-describedby', 'currency-help');

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });
    });
  });

  describe('DatePicker Component', () => {
    describe('Polish Date Formatting', () => {
      it('formats dates in DD.MM.YYYY format', async () => {
        const handleChange = jest.fn();
        
        render(
          <TestWrapper>
            <DatePicker
              format="DD.MM.YYYY"
              onChange={handleChange}
              aria-label="Polish date"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/polish date/i);
        
        await user.type(input, '15.03.2024');
        expect(input).toHaveValue('15.03.2024');
        expect(handleChange).toHaveBeenCalledWith(new Date(2024, 2, 15));
      });

      it('validates Polish date format', async () => {
        render(
          <TestWrapper>
            <DatePicker
              format="DD.MM.YYYY"
              required
              aria-label="Validated date"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/validated date/i);
        
        // Test invalid format
        await user.type(input, '2024-03-15');
        expect(screen.getByText(/invalid date format/i)).toBeInTheDocument();
        
        // Test valid format
        await user.clear(input);
        await user.type(input, '15.03.2024');
        expect(screen.queryByText(/invalid date format/i)).not.toBeInTheDocument();
      });

      it('handles Polish month names', () => {
        const date = new Date(2024, 2, 15); // March 15, 2024
        const formatted = formatPolishDate(date, 'DD MMMM YYYY');
        expect(formatted).toBe('15 marca 2024');
      });

      it('validates date ranges', async () => {
        const minDate = new Date(2024, 0, 1);
        const maxDate = new Date(2024, 11, 31);
        
        render(
          <TestWrapper>
            <DatePicker
              format="DD.MM.YYYY"
              minDate={minDate}
              maxDate={maxDate}
              aria-label="Range validated date"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/range validated date/i);
        
        // Test date before minimum
        await user.type(input, '31.12.2023');
        expect(screen.getByText(/date must be after/i)).toBeInTheDocument();
        
        // Test date after maximum
        await user.clear(input);
        await user.type(input, '01.01.2025');
        expect(screen.getByText(/date must be before/i)).toBeInTheDocument();
      });
    });

    describe('Polish Business Date Logic', () => {
      it('handles Polish business days correctly', () => {
        // Test that weekends are handled appropriately
        const friday = new Date(2024, 2, 15); // Friday
        const saturday = new Date(2024, 2, 16); // Saturday
        const sunday = new Date(2024, 2, 17); // Sunday
        const monday = new Date(2024, 2, 18); // Monday

        expect(isPolishBusinessDay(friday)).toBe(true);
        expect(isPolishBusinessDay(saturday)).toBe(false);
        expect(isPolishBusinessDay(sunday)).toBe(false);
        expect(isPolishBusinessDay(monday)).toBe(true);
      });

      it('handles Polish holidays correctly', () => {
        // Test major Polish holidays
        const newYear = new Date(2024, 0, 1); // New Year's Day
        const constitution = new Date(2024, 4, 3); // Constitution Day
        const independence = new Date(2024, 10, 11); // Independence Day

        expect(isPolishHoliday(newYear)).toBe(true);
        expect(isPolishHoliday(constitution)).toBe(true);
        expect(isPolishHoliday(independence)).toBe(true);
      });
    });
  });

  describe('VATRateSelector Component', () => {
    describe('Polish VAT Rates', () => {
      it('provides correct Polish VAT rates', () => {
        render(
          <TestWrapper>
            <VATRateSelector aria-label="VAT rate selection" />
          </TestWrapper>
        );

        // Check that all Polish VAT rates are available
        expect(screen.getByText('0%')).toBeInTheDocument();
        expect(screen.getByText('5%')).toBeInTheDocument();
        expect(screen.getByText('8%')).toBeInTheDocument();
        expect(screen.getByText('23%')).toBeInTheDocument();
      });

      it('calculates VAT amounts correctly', () => {
        const netAmount = 1000;
        
        expect(calculatePolishVAT(netAmount, 0)).toEqual({
          net: 1000,
          vat: 0,
          gross: 1000,
        });

        expect(calculatePolishVAT(netAmount, 23)).toEqual({
          net: 1000,
          vat: 230,
          gross: 1230,
        });

        expect(calculatePolishVAT(netAmount, 8)).toEqual({
          net: 1000,
          vat: 80,
          gross: 1080,
        });
      });

      it('handles VAT rate changes', async () => {
        const handleChange = jest.fn();
        
        render(
          <TestWrapper>
            <VATRateSelector
              onChange={handleChange}
              aria-label="VAT rate"
            />
          </TestWrapper>
        );

        const select = screen.getByLabelText(/vat rate/i);
        
        await user.selectOptions(select, '23');
        expect(handleChange).toHaveBeenCalledWith(23);
        
        await user.selectOptions(select, '8');
        expect(handleChange).toHaveBeenCalledWith(8);
      });

      it('provides VAT rate descriptions', () => {
        render(
          <TestWrapper>
            <VATRateSelector
              showDescriptions={true}
              aria-label="VAT rate with descriptions"
            />
          </TestWrapper>
        );

        expect(screen.getByText(/standard rate/i)).toBeInTheDocument();
        expect(screen.getByText(/reduced rate/i)).toBeInTheDocument();
        expect(screen.getByText(/exempt/i)).toBeInTheDocument();
      });
    });
  });

  describe('NIPValidator Component', () => {
    describe('NIP Validation Logic', () => {
      it('validates correct NIP numbers', async () => {
        const handleValidation = jest.fn();
        
        render(
          <TestWrapper>
            <NIPValidator
              onValidation={handleValidation}
              aria-label="NIP number"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/nip number/i);
        
        // Test valid NIP numbers
        const validNIPs = [
          '1234567890',
          '5260001246',
          '7010001454',
        ];

        for (const nip of validNIPs) {
          await user.clear(input);
          await user.type(input, nip);
          
          expect(handleValidation).toHaveBeenCalledWith(true, nip);
          expect(screen.queryByText(/nieprawidłowy nip/i)).not.toBeInTheDocument();
        }
      });

      it('rejects invalid NIP numbers', async () => {
        const handleValidation = jest.fn();
        
        render(
          <TestWrapper>
            <NIPValidator
              onValidation={handleValidation}
              aria-label="NIP validation"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/nip validation/i);
        
        // Test invalid NIP numbers
        const invalidNIPs = [
          '1234567891', // Wrong checksum
          '123456789',  // Too short
          '12345678901', // Too long
          'abcdefghij',  // Non-numeric
        ];

        for (const nip of invalidNIPs) {
          await user.clear(input);
          await user.type(input, nip);
          
          expect(handleValidation).toHaveBeenCalledWith(false, nip);
          expect(screen.getByText(/nieprawidłowy nip/i)).toBeInTheDocument();
        }
      });

      it('formats NIP numbers correctly', async () => {
        render(
          <TestWrapper>
            <NIPValidator
              formatOnBlur={true}
              aria-label="Formatted NIP"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/formatted nip/i);
        
        await user.type(input, '1234567890');
        fireEvent.blur(input);
        
        expect(input).toHaveValue('123-456-78-90');
      });

      it('validates NIP checksum algorithm', () => {
        // Test the NIP checksum algorithm
        expect(validateNIP('1234567890')).toBe(true);
        expect(validateNIP('5260001246')).toBe(true);
        expect(validateNIP('7010001454')).toBe(true);
        
        expect(validateNIP('1234567891')).toBe(false);
        expect(validateNIP('0000000000')).toBe(false);
      });
    });

    describe('REGON Validation', () => {
      it('validates 9-digit REGON numbers', () => {
        expect(validateREGON('123456785')).toBe(true);
        expect(validateREGON('610188201')).toBe(true);
        
        expect(validateREGON('123456786')).toBe(false);
        expect(validateREGON('000000000')).toBe(false);
      });

      it('validates 14-digit REGON numbers', () => {
        expect(validateREGON('12345678512347')).toBe(true);
        
        expect(validateREGON('12345678512348')).toBe(false);
        expect(validateREGON('00000000000000')).toBe(false);
      });
    });
  });

  describe('InvoiceStatusBadge Component', () => {
    describe('Polish Invoice Statuses', () => {
      const polishStatuses = [
        { status: 'draft', label: 'Szkic', color: 'gray' },
        { status: 'sent', label: 'Wysłana', color: 'blue' },
        { status: 'paid', label: 'Opłacona', color: 'green' },
        { status: 'overdue', label: 'Przeterminowana', color: 'red' },
        { status: 'cancelled', label: 'Anulowana', color: 'gray' },
        { status: 'partial', label: 'Częściowo opłacona', color: 'yellow' },
      ] as const;

      polishStatuses.forEach(({ status, label, color }) => {
        it(`renders ${status} status correctly in Polish`, () => {
          render(
            <TestWrapper>
              <InvoiceStatusBadge status={status} locale="pl" />
            </TestWrapper>
          );

          const badge = screen.getByRole('status');
          expect(badge).toHaveTextContent(label);
          expect(badge).toHaveClass(`status-${color}`);
        });
      });

      it('handles status transitions correctly', () => {
        const StatusTransitionTest = () => {
          const [status, setStatus] = React.useState<any>('draft');
          
          return (
            <div>
              <InvoiceStatusBadge status={status} />
              <button onClick={() => setStatus('sent')}>Send</button>
              <button onClick={() => setStatus('paid')}>Mark Paid</button>
            </div>
          );
        };

        render(
          <TestWrapper>
            <StatusTransitionTest />
          </TestWrapper>
        );

        expect(screen.getByText(/szkic/i)).toBeInTheDocument();
        
        fireEvent.click(screen.getByText('Send'));
        expect(screen.getByText(/wysłana/i)).toBeInTheDocument();
        
        fireEvent.click(screen.getByText('Mark Paid'));
        expect(screen.getByText(/opłacona/i)).toBeInTheDocument();
      });
    });
  });

  describe('ComplianceIndicator Component', () => {
    describe('Polish Business Compliance', () => {
      it('shows compliance status for Polish requirements', () => {
        const requirements = [
          'VAT registration',
          'NIP validation',
          'REGON number',
          'Invoice numbering',
          'Date format compliance',
        ];

        render(
          <TestWrapper>
            <ComplianceIndicator
              compliant={true}
              requirements={requirements}
              locale="pl"
            />
          </TestWrapper>
        );

        expect(screen.getByText(/zgodne z przepisami/i)).toBeInTheDocument();
        requirements.forEach(req => {
          expect(screen.getByText(req)).toBeInTheDocument();
        });
      });

      it('shows non-compliance warnings', () => {
        const failedRequirements = [
          'Missing NIP validation',
          'Incorrect date format',
        ];

        render(
          <TestWrapper>
            <ComplianceIndicator
              compliant={false}
              requirements={[]}
              failedRequirements={failedRequirements}
              locale="pl"
            />
          </TestWrapper>
        );

        expect(screen.getByText(/niezgodne z przepisami/i)).toBeInTheDocument();
        failedRequirements.forEach(req => {
          expect(screen.getByText(req)).toBeInTheDocument();
        });
      });

      it('provides compliance improvement suggestions', () => {
        render(
          <TestWrapper>
            <ComplianceIndicator
              compliant={false}
              suggestions={[
                'Add valid NIP number',
                'Use DD.MM.YYYY date format',
                'Include VAT rate information',
              ]}
              locale="pl"
            />
          </TestWrapper>
        );

        expect(screen.getByText(/sugestie poprawy/i)).toBeInTheDocument();
        expect(screen.getByText(/add valid nip number/i)).toBeInTheDocument();
      });
    });
  });

  describe('Polish Business Utilities', () => {
    describe('Currency Formatting', () => {
      it('formats Polish currency correctly', () => {
        expect(formatPolishCurrency(1234.56)).toBe('1 234,56 zł');
        expect(formatPolishCurrency(1000000)).toBe('1 000 000,00 zł');
        expect(formatPolishCurrency(0.5)).toBe('0,50 zł');
        expect(formatPolishCurrency(-123.45)).toBe('-123,45 zł');
      });
    });

    describe('Date Formatting', () => {
      it('formats Polish dates correctly', () => {
        const date = new Date(2024, 2, 15); // March 15, 2024
        
        expect(formatPolishDate(date, 'DD.MM.YYYY')).toBe('15.03.2024');
        expect(formatPolishDate(date, 'DD/MM/YYYY')).toBe('15/03/2024');
        expect(formatPolishDate(date, 'DD MMMM YYYY')).toBe('15 marca 2024');
      });
    });

    describe('VAT Calculations', () => {
      it('calculates Polish VAT correctly', () => {
        const rates = getPolishVATRates();
        
        expect(rates).toEqual([0, 5, 8, 23]);
        
        // Test standard rate (23%)
        const result23 = calculatePolishVAT(1000, 23);
        expect(result23.net).toBe(1000);
        expect(result23.vat).toBe(230);
        expect(result23.gross).toBe(1230);
        
        // Test reduced rate (8%)
        const result8 = calculatePolishVAT(1000, 8);
        expect(result8.net).toBe(1000);
        expect(result8.vat).toBe(80);
        expect(result8.gross).toBe(1080);
      });
    });
  });

  describe('Integration with Polish Business Forms', () => {
    it('handles complete Polish invoice form', async () => {
      const handleSubmit = jest.fn();
      
      render(
        <TestWrapper>
          <form onSubmit={handleSubmit}>
            <NIPValidator
              name="sellerNIP"
              aria-label="Seller NIP"
              required
            />
            <NIPValidator
              name="buyerNIP"
              aria-label="Buyer NIP"
              required
            />
            <DatePicker
              name="issueDate"
              format="DD.MM.YYYY"
              aria-label="Issue date"
              required
            />
            <CurrencyInput
              name="netAmount"
              currency="PLN"
              aria-label="Net amount"
              required
            />
            <VATRateSelector
              name="vatRate"
              aria-label="VAT rate"
              required
            />
            <button type="submit">Create Invoice</button>
          </form>
        </TestWrapper>
      );

      // Fill out the form with valid Polish business data
      await user.type(screen.getByLabelText(/seller nip/i), '1234567890');
      await user.type(screen.getByLabelText(/buyer nip/i), '5260001246');
      await user.type(screen.getByLabelText(/issue date/i), '15.03.2024');
      await user.type(screen.getByLabelText(/net amount/i), '1000');
      await user.selectOptions(screen.getByLabelText(/vat rate/i), '23');

      // Submit the form
      fireEvent.submit(screen.getByRole('button', { name: /create invoice/i }));

      await waitFor(() => {
        expect(handleSubmit).toHaveBeenCalled();
      });
    });
  });
});

// Helper functions for Polish business logic
function isPolishBusinessDay(date: Date): boolean {
  const day = date.getDay();
  return day !== 0 && day !== 6; // Not Sunday (0) or Saturday (6)
}

function isPolishHoliday(date: Date): boolean {
  const month = date.getMonth();
  const day = date.getDate();
  
  // Major Polish holidays
  const holidays = [
    { month: 0, day: 1 },   // New Year's Day
    { month: 0, day: 6 },   // Epiphany
    { month: 4, day: 1 },   // Labour Day
    { month: 4, day: 3 },   // Constitution Day
    { month: 7, day: 15 },  // Assumption of Mary
    { month: 10, day: 1 },  // All Saints' Day
    { month: 10, day: 11 }, // Independence Day
    { month: 11, day: 25 }, // Christmas Day
    { month: 11, day: 26 }, // Boxing Day
  ];
  
  return holidays.some(holiday => 
    holiday.month === month && holiday.day === day
  );
}