import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { CurrencyInput } from '../CurrencyInput/CurrencyInput';

describe('CurrencyInput Component', () => {
  it('renders with default props', () => {
    render(<CurrencyInput testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('placeholder', '0,00 zł');
  });

  it('displays formatted currency value when not focused', () => {
    render(<CurrencyInput value={1234.56} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input') as HTMLInputElement;
    expect(input.value).toBe('1 234,56 zł');
  });

  it('displays editable format when focused', () => {
    render(<CurrencyInput value={1234.56} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    fireEvent.focus(input);
    
    expect((input as HTMLInputElement).value).toBe('1234,56');
  });

  it('calls onChange with parsed numeric value', () => {
    const handleChange = jest.fn();
    render(<CurrencyInput onChange={handleChange} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: '123,45' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith(123.45);
  });

  it('handles invalid input gracefully', () => {
    const handleChange = jest.fn();
    render(<CurrencyInput onChange={handleChange} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: 'invalid' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith(null);
  });

  it('prevents negative values when allowNegative is false', () => {
    const handleChange = jest.fn();
    render(<CurrencyInput onChange={handleChange} allowNegative={false} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: '-123,45' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith(123.45);
  });

  it('allows negative values when allowNegative is true', () => {
    const handleChange = jest.fn();
    render(<CurrencyInput onChange={handleChange} allowNegative={true} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: '-123,45' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith(-123.45);
  });

  it('respects maxDecimals setting', () => {
    render(<CurrencyInput value={123.456789} maxDecimals={3} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    fireEvent.focus(input);
    
    expect((input as HTMLInputElement).value).toBe('123,457');
  });

  it('displays currency symbol when not focused', () => {
    render(<CurrencyInput value={100} currency="EUR" testId="currency-input" />);
    
    const currencySymbol = screen.getByText('EUR');
    expect(currencySymbol).toBeInTheDocument();
  });

  it('hides currency symbol when focused', () => {
    render(<CurrencyInput value={100} currency="EUR" testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    fireEvent.focus(input);
    
    const currencySymbol = screen.queryByText('EUR');
    expect(currencySymbol).not.toBeInTheDocument();
  });

  it('shows error message when error is true', () => {
    render(
      <CurrencyInput 
        error={true} 
        errorMessage="Invalid amount" 
        testId="currency-input" 
      />
    );
    
    const errorMessage = screen.getByTestId('currency-input-error');
    expect(errorMessage).toHaveTextContent('Invalid amount');
  });

  it('applies error styling when error is true', () => {
    render(<CurrencyInput error={true} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    expect(input).toHaveClass('border-error-300');
  });

  it('is disabled when disabled prop is true', () => {
    render(<CurrencyInput disabled={true} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    expect(input).toBeDisabled();
  });

  it('selects all text on focus', () => {
    render(<CurrencyInput value={123.45} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input') as HTMLInputElement;
    const selectSpy = jest.spyOn(input, 'select');
    
    fireEvent.focus(input);
    
    expect(selectSpy).toHaveBeenCalled();
  });

  it('filters non-numeric characters during typing', () => {
    render(<CurrencyInput testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: 'abc123def,45ghi' } });
    
    expect((input as HTMLInputElement).value).toBe('123,45');
  });

  it('handles different locales correctly', () => {
    render(<CurrencyInput value={1234.56} locale="en-US" currency="USD" testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input') as HTMLInputElement;
    expect(input.value).toBe('$1,234.56');
  });

  it('calls onBlur when input loses focus', () => {
    const handleBlur = jest.fn();
    render(<CurrencyInput onBlur={handleBlur} testId="currency-input" />);
    
    const input = screen.getByTestId('currency-input');
    fireEvent.focus(input);
    fireEvent.blur(input);
    
    expect(handleBlur).toHaveBeenCalled();
  });
});