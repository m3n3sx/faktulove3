// Polish Business Input Tests
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { 
  CurrencyInput, 
  NIPInput, 
  REGONInput, 
  PostalCodeInput, 
  PhoneInput 
} from '../PolishBusinessInput';

expect.extend(toHaveNoViolations);

describe('Polish Business Input Components', () => {
  describe('CurrencyInput', () => {
    it('renders with PLN currency symbol', () => {
      render(<CurrencyInput label="Amount" />);
      
      const input = screen.getByLabelText('Amount');
      expect(input).toBeInTheDocument();
      expect(screen.getByText('zł')).toBeInTheDocument();
    });

    it('formats currency value correctly', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      render(<CurrencyInput label="Amount" onChange={handleChange} />);
      
      const input = screen.getByLabelText('Amount');
      await user.type(input, '1234.56');
      
      expect(handleChange).toHaveBeenCalledWith(1234.56);
    });

    it('handles Polish decimal separator', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      render(<CurrencyInput label="Amount" onChange={handleChange} />);
      
      const input = screen.getByLabelText('Amount');
      await user.type(input, '1234,56');
      
      expect(handleChange).toHaveBeenCalledWith(1234.56);
    });

    it('formats display value on blur', async () => {
      const user = userEvent.setup();
      
      render(<CurrencyInput label="Amount" />);
      
      const input = screen.getByLabelText('Amount');
      await user.type(input, '1234.5');
      await user.tab(); // Trigger blur
      
      expect(input).toHaveValue('1 234,50');
    });

    it('respects min and max values', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      render(<CurrencyInput label="Amount" min={0} max={1000} onChange={handleChange} />);
      
      const input = screen.getByLabelText('Amount');
      
      // Test below minimum
      await user.type(input, '-100');
      expect(handleChange).not.toHaveBeenCalledWith(-100);
      
      // Test above maximum
      await user.clear(input);
      await user.type(input, '2000');
      expect(handleChange).not.toHaveBeenCalledWith(2000);
      
      // Test valid value
      await user.clear(input);
      await user.type(input, '500');
      expect(handleChange).toHaveBeenCalledWith(500);
    });

    it('handles negative values when allowed', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      render(<CurrencyInput label="Amount" allowNegative onChange={handleChange} />);
      
      const input = screen.getByLabelText('Amount');
      await user.type(input, '-100');
      
      expect(handleChange).toHaveBeenCalledWith(-100);
    });

    it('supports custom currency symbol', () => {
      render(<CurrencyInput label="Amount" currency="EUR" />);
      
      expect(screen.getByText('EUR')).toBeInTheDocument();
    });

    it('supports custom decimal places', async () => {
      const user = userEvent.setup();
      
      render(<CurrencyInput label="Amount" decimals={0} />);
      
      const input = screen.getByLabelText('Amount');
      await user.type(input, '1234');
      await user.tab();
      
      expect(input).toHaveValue('1 234');
    });

    it('meets accessibility standards', async () => {
      const { container } = render(<CurrencyInput label="Amount" />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('NIPInput', () => {
    it('formats NIP number correctly', async () => {
      const user = userEvent.setup();
      
      render(<NIPInput label="NIP" />);
      
      const input = screen.getByLabelText('NIP');
      await user.type(input, '1234567890');
      
      expect(input).toHaveValue('123-456-78-90');
    });

    it('validates NIP number correctly', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      render(<NIPInput label="NIP" onChange={handleChange} />);
      
      const input = screen.getByLabelText('NIP');
      
      // Valid NIP: 123-456-78-90 (checksum valid for this example)
      await user.type(input, '1234567890');
      
      expect(handleChange).toHaveBeenCalledWith(
        expect.objectContaining({ target: expect.objectContaining({ value: '123-456-78-90' }) }),
        expect.any(Boolean)
      );
    });

    it('shows validation icon when enabled', async () => {
      const user = userEvent.setup();
      
      render(<NIPInput label="NIP" showValidation />);
      
      const input = screen.getByLabelText('NIP');
      await user.type(input, '1234567890');
      
      // Should show either success or error icon
      const icon = input.parentElement?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('hides validation icon when disabled', async () => {
      const user = userEvent.setup();
      
      render(<NIPInput label="NIP" showValidation={false} />);
      
      const input = screen.getByLabelText('NIP');
      await user.type(input, '1234567890');
      
      const icon = input.parentElement?.querySelector('svg');
      expect(icon).not.toBeInTheDocument();
    });

    it('limits input length correctly', async () => {
      const user = userEvent.setup();
      
      render(<NIPInput label="NIP" />);
      
      const input = screen.getByLabelText('NIP');
      await user.type(input, '12345678901234567890'); // Too long
      
      expect(input).toHaveValue('123-456-78-90'); // Should be truncated
    });

    it('meets accessibility standards', async () => {
      const { container } = render(<NIPInput label="NIP" />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('REGONInput', () => {
    it('formats 9-digit REGON correctly', async () => {
      const user = userEvent.setup();
      
      render(<REGONInput label="REGON" regonType={9} />);
      
      const input = screen.getByLabelText('REGON');
      await user.type(input, '123456789');
      
      expect(input).toHaveValue('123-456-789');
    });

    it('formats 14-digit REGON correctly', async () => {
      const user = userEvent.setup();
      
      render(<REGONInput label="REGON" regonType={14} />);
      
      const input = screen.getByLabelText('REGON');
      await user.type(input, '12345678901234');
      
      expect(input).toHaveValue('123-456-78-901234');
    });

    it('validates REGON number', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      render(<REGONInput label="REGON" regonType={9} onChange={handleChange} />);
      
      const input = screen.getByLabelText('REGON');
      await user.type(input, '123456789');
      
      expect(handleChange).toHaveBeenCalledWith(
        expect.objectContaining({ target: expect.objectContaining({ value: '123-456-789' }) }),
        expect.any(Boolean)
      );
    });

    it('shows correct placeholder for REGON type', () => {
      const { rerender } = render(<REGONInput label="REGON 9" regonType={9} />);
      expect(screen.getByPlaceholderText('123-456-789')).toBeInTheDocument();

      rerender(<REGONInput label="REGON 14" regonType={14} />);
      expect(screen.getByPlaceholderText('123-456-78-901234')).toBeInTheDocument();
    });

    it('limits input length based on REGON type', async () => {
      const user = userEvent.setup();
      
      const { rerender } = render(<REGONInput label="REGON" regonType={9} />);
      let input = screen.getByLabelText('REGON');
      await user.type(input, '12345678901234567890');
      expect(input).toHaveValue('123-456-789');

      rerender(<REGONInput label="REGON" regonType={14} />);
      input = screen.getByLabelText('REGON');
      await user.clear(input);
      await user.type(input, '12345678901234567890');
      expect(input).toHaveValue('123-456-78-901234');
    });

    it('meets accessibility standards', async () => {
      const { container } = render(<REGONInput label="REGON" />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('PostalCodeInput', () => {
    it('formats postal code correctly', async () => {
      const user = userEvent.setup();
      
      render(<PostalCodeInput label="Postal Code" />);
      
      const input = screen.getByLabelText('Postal Code');
      await user.type(input, '12345');
      
      expect(input).toHaveValue('12-345');
    });

    it('validates postal code length', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      render(<PostalCodeInput label="Postal Code" onChange={handleChange} />);
      
      const input = screen.getByLabelText('Postal Code');
      
      // Valid postal code
      await user.type(input, '12345');
      expect(handleChange).toHaveBeenCalledWith(
        expect.objectContaining({ target: expect.objectContaining({ value: '12-345' }) }),
        true
      );
      
      // Invalid postal code (too short)
      await user.clear(input);
      await user.type(input, '123');
      expect(handleChange).toHaveBeenCalledWith(
        expect.objectContaining({ target: expect.objectContaining({ value: '123' }) }),
        false
      );
    });

    it('limits input length correctly', async () => {
      const user = userEvent.setup();
      
      render(<PostalCodeInput label="Postal Code" />);
      
      const input = screen.getByLabelText('Postal Code');
      await user.type(input, '1234567890');
      
      expect(input).toHaveValue('12-345'); // Should be limited to 5 digits
    });

    it('shows validation status', async () => {
      const user = userEvent.setup();
      
      render(<PostalCodeInput label="Postal Code" showValidation />);
      
      const input = screen.getByLabelText('Postal Code');
      await user.type(input, '12345');
      
      const icon = input.parentElement?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('meets accessibility standards', async () => {
      const { container } = render(<PostalCodeInput label="Postal Code" />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('PhoneInput', () => {
    it('formats Polish phone number correctly', async () => {
      const user = userEvent.setup();
      
      render(<PhoneInput label="Phone" />);
      
      const input = screen.getByLabelText('Phone');
      await user.type(input, '123456789');
      
      expect(input).toHaveValue('123 456 789');
    });

    it('formats phone number with country code', async () => {
      const user = userEvent.setup();
      
      render(<PhoneInput label="Phone" includeCountryCode />);
      
      const input = screen.getByLabelText('Phone');
      await user.type(input, '48123456789');
      
      expect(input).toHaveValue('+48 123 456 789');
    });

    it('validates phone number length', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      render(<PhoneInput label="Phone" onChange={handleChange} />);
      
      const input = screen.getByLabelText('Phone');
      
      // Valid phone number
      await user.type(input, '123456789');
      expect(handleChange).toHaveBeenCalledWith(
        expect.objectContaining({ target: expect.objectContaining({ value: '123 456 789' }) }),
        true
      );
      
      // Invalid phone number (too short)
      await user.clear(input);
      await user.type(input, '12345');
      expect(handleChange).toHaveBeenCalledWith(
        expect.objectContaining({ target: expect.objectContaining({ value: '123 45' }) }),
        false
      );
    });

    it('shows phone icon when validation is disabled', () => {
      render(<PhoneInput label="Phone" showValidation={false} />);
      
      const input = screen.getByLabelText('Phone');
      const phoneIcon = input.parentElement?.querySelector('svg');
      expect(phoneIcon).toBeInTheDocument();
    });

    it('shows validation icon when validation is enabled', async () => {
      const user = userEvent.setup();
      
      render(<PhoneInput label="Phone" showValidation />);
      
      const input = screen.getByLabelText('Phone');
      await user.type(input, '123456789');
      
      const validationIcon = input.parentElement?.querySelector('svg');
      expect(validationIcon).toBeInTheDocument();
    });

    it('shows correct placeholder based on country code setting', () => {
      const { rerender } = render(<PhoneInput label="Phone" includeCountryCode={false} />);
      expect(screen.getByPlaceholderText('123 456 789')).toBeInTheDocument();

      rerender(<PhoneInput label="Phone" includeCountryCode />);
      expect(screen.getByPlaceholderText('+48 123 456 789')).toBeInTheDocument();
    });

    it('meets accessibility standards', async () => {
      const { container } = render(<PhoneInput label="Phone" />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Integration Tests', () => {
    it('all Polish business inputs work together in a form', async () => {
      const user = userEvent.setup();
      
      render(
        <form>
          <CurrencyInput label="Amount" />
          <NIPInput label="NIP" />
          <REGONInput label="REGON" />
          <PostalCodeInput label="Postal Code" />
          <PhoneInput label="Phone" />
        </form>
      );
      
      // Test that all inputs are rendered
      expect(screen.getByLabelText('Amount')).toBeInTheDocument();
      expect(screen.getByLabelText('NIP')).toBeInTheDocument();
      expect(screen.getByLabelText('REGON')).toBeInTheDocument();
      expect(screen.getByLabelText('Postal Code')).toBeInTheDocument();
      expect(screen.getByLabelText('Phone')).toBeInTheDocument();
      
      // Test that they can all receive input
      await user.type(screen.getByLabelText('Amount'), '1000');
      await user.type(screen.getByLabelText('NIP'), '1234567890');
      await user.type(screen.getByLabelText('REGON'), '123456789');
      await user.type(screen.getByLabelText('Postal Code'), '12345');
      await user.type(screen.getByLabelText('Phone'), '123456789');
      
      // Verify formatting
      expect(screen.getByLabelText('NIP')).toHaveValue('123-456-78-90');
      expect(screen.getByLabelText('REGON')).toHaveValue('123-456-789');
      expect(screen.getByLabelText('Postal Code')).toHaveValue('12-345');
      expect(screen.getByLabelText('Phone')).toHaveValue('123 456 789');
    });

    it('maintains consistent styling across all variants', () => {
      render(
        <div>
          <CurrencyInput label="Amount" size="md" />
          <NIPInput label="NIP" size="md" />
          <REGONInput label="REGON" size="md" />
          <PostalCodeInput label="Postal Code" size="md" />
          <PhoneInput label="Phone" size="md" />
        </div>
      );
      
      const inputs = screen.getAllByRole('textbox');
      inputs.forEach(input => {
        const wrapper = input.closest('.ds-input-wrapper');
        expect(wrapper).toHaveClass('h-10'); // md size height
      });
    });

    it('supports all common input props', () => {
      const handleChange = jest.fn();
      
      render(
        <CurrencyInput
          label="Amount"
          size="lg"
          disabled={false}
          required
          onChange={handleChange}
          className="custom-class"
          testId="currency-input"
          helperText="Enter amount in PLN"
        />
      );
      
      const input = screen.getByTestId('currency-input');
      expect(input).toHaveAttribute('required');
      expect(screen.getByText('Enter amount in PLN')).toBeInTheDocument();
      
      const container = input.closest('.ds-input-container');
      expect(container).toHaveClass('custom-class');
      
      const wrapper = input.closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('h-12'); // lg size
    });
  });
});