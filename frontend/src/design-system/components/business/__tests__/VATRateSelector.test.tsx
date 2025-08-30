import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { VATRateSelector } from '../VATRateSelector/VATRateSelector';

describe('VATRateSelector Component', () => {
  it('renders with default Polish VAT rates', () => {
    render(<VATRateSelector testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    expect(select).toBeInTheDocument();
    expect(select).toHaveAttribute('placeholder', 'Wybierz stawkę VAT');
  });

  it('displays all default Polish VAT rates', () => {
    render(<VATRateSelector testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    expect(screen.getByText('23%')).toBeInTheDocument();
    expect(screen.getByText('8%')).toBeInTheDocument();
    expect(screen.getByText('5%')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('includes exempt rates by default', () => {
    render(<VATRateSelector testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    expect(screen.getByText('zw.')).toBeInTheDocument();
    expect(screen.getByText('np.')).toBeInTheDocument();
  });

  it('excludes exempt rates when includeExempt is false', () => {
    render(<VATRateSelector includeExempt={false} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    expect(screen.queryByText('zw.')).not.toBeInTheDocument();
    expect(screen.queryByText('np.')).not.toBeInTheDocument();
  });

  it('calls onChange with selected VAT rate', () => {
    const handleChange = jest.fn();
    render(<VATRateSelector onChange={handleChange} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    const option23 = screen.getByText('23%');
    fireEvent.click(option23);
    
    expect(handleChange).toHaveBeenCalledWith(23);
  });

  it('handles exempt rate selection', () => {
    const handleChange = jest.fn();
    render(<VATRateSelector onChange={handleChange} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    const exemptOption = screen.getByText('zw.');
    fireEvent.click(exemptOption);
    
    expect(handleChange).toHaveBeenCalledWith(-1);
  });

  it('displays selected value correctly', () => {
    render(<VATRateSelector value={23} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector') as HTMLSelectElement;
    expect(select.value).toBe('23');
  });

  it('displays exempt value correctly', () => {
    render(<VATRateSelector value={-1} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector') as HTMLSelectElement;
    expect(select.value).toBe('-1');
  });

  it('uses custom VAT rates when provided', () => {
    const customRates = [
      { value: 15, label: '15%', description: 'Custom rate' },
      { value: 10, label: '10%', description: 'Another custom rate' },
    ];
    
    render(<VATRateSelector customRates={customRates} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    expect(screen.getByText('15%')).toBeInTheDocument();
    expect(screen.getByText('10%')).toBeInTheDocument();
    expect(screen.queryByText('23%')).not.toBeInTheDocument();
  });

  it('shows rate descriptions in options', () => {
    render(<VATRateSelector testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    expect(screen.getByText('Standardowa stawka VAT')).toBeInTheDocument();
    expect(screen.getByText('Obniżona stawka VAT')).toBeInTheDocument();
    expect(screen.getByText('Stawka zerowa VAT')).toBeInTheDocument();
  });

  it('shows error message when error is true', () => {
    render(
      <VATRateSelector 
        error={true} 
        errorMessage="Please select a VAT rate" 
        testId="vat-selector" 
      />
    );
    
    const errorMessage = screen.getByTestId('vat-selector-error');
    expect(errorMessage).toHaveTextContent('Please select a VAT rate');
  });

  it('applies error styling when error is true', () => {
    render(<VATRateSelector error={true} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    expect(select).toHaveClass('border-error-300');
  });

  it('is disabled when disabled prop is true', () => {
    render(<VATRateSelector disabled={true} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    expect(select).toBeDisabled();
  });

  it('calls onBlur when select loses focus', () => {
    const handleBlur = jest.fn();
    render(<VATRateSelector onBlur={handleBlur} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.focus(select);
    fireEvent.blur(select);
    
    expect(handleBlur).toHaveBeenCalled();
  });

  it('applies custom className', () => {
    render(<VATRateSelector className="custom-class" testId="vat-selector" />);
    
    const container = screen.getByTestId('vat-selector').parentElement;
    expect(container).toHaveClass('custom-class');
  });

  it('handles zero VAT rate correctly', () => {
    const handleChange = jest.fn();
    render(<VATRateSelector onChange={handleChange} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    const zeroOption = screen.getByText('0%');
    fireEvent.click(zeroOption);
    
    expect(handleChange).toHaveBeenCalledWith(0);
  });

  it('formats rate labels correctly for positive rates', () => {
    const customRates = [
      { value: 25, label: '25%' },
      { value: 12, label: '12%' },
    ];
    
    render(<VATRateSelector customRates={customRates} includeExempt={false} testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    expect(screen.getByText('25%')).toBeInTheDocument();
    expect(screen.getByText('12%')).toBeInTheDocument();
  });

  it('formats exempt rate labels correctly', () => {
    render(<VATRateSelector testId="vat-selector" />);
    
    const select = screen.getByTestId('vat-selector');
    fireEvent.click(select);
    
    expect(screen.getByText('zw.')).toBeInTheDocument();
    expect(screen.getByText('np.')).toBeInTheDocument();
  });
});