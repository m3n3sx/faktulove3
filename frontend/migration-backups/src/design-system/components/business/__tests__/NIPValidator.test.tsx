import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { NIPValidator } from '../NIPValidator/NIPValidator';

describe('NIPValidator Component', () => {
  it('renders with default props', () => {
    render(<NIPValidator testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('placeholder', 'NIP (np. 123-456-78-90)');
  });

  it('formats NIP as user types', () => {
    render(<NIPValidator testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.change(input, { target: { value: '1234567890' } });
    
    expect((input as HTMLInputElement).value).toBe('123-456-78-90');
  });

  it('validates correct NIP', () => {
    const handleChange = jest.fn();
    render(<NIPValidator onChange={handleChange} testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    // Using a valid NIP: 123-456-32-18 (checksum is correct)
    fireEvent.change(input, { target: { value: '1234563218' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith('1234563218', true);
    expect(screen.getByTestId('nip-validator-valid-icon')).toBeInTheDocument();
    expect(screen.getByTestId('nip-validator-success')).toHaveTextContent('NIP jest prawidłowy');
  });

  it('validates incorrect NIP', () => {
    const handleChange = jest.fn();
    render(<NIPValidator onChange={handleChange} testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.change(input, { target: { value: '1234567890' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith('1234567890', false);
    expect(screen.getByTestId('nip-validator-invalid-icon')).toBeInTheDocument();
    expect(screen.getByTestId('nip-validator-error')).toHaveTextContent('Nieprawidłowy NIP - błędna suma kontrolna');
  });

  it('validates NIP length', () => {
    render(<NIPValidator testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.change(input, { target: { value: '123456789' } }); // 9 digits
    fireEvent.blur(input);
    
    expect(screen.getByTestId('nip-validator-error')).toHaveTextContent('NIP musi składać się z 10 cyfr');
  });

  it('rejects NIP with all same digits', () => {
    render(<NIPValidator testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.change(input, { target: { value: '1111111111' } });
    fireEvent.blur(input);
    
    expect(screen.getByTestId('nip-validator-error')).toHaveTextContent('NIP nie może składać się z samych identycznych cyfr');
  });

  it('filters non-numeric characters', () => {
    render(<NIPValidator testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.change(input, { target: { value: 'abc123def456ghi789jkl0' } });
    
    expect((input as HTMLInputElement).value).toBe('123-456-78-90');
  });

  it('limits input to 10 digits', () => {
    render(<NIPValidator testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.change(input, { target: { value: '12345678901234' } });
    
    expect((input as HTMLInputElement).value).toBe('123-456-78-90');
  });

  it('shows validation icon when showValidationIcon is true', () => {
    render(<NIPValidator showValidationIcon={true} value="1234563218" testId="nip-validator" />);
    
    expect(screen.getByTestId('nip-validator-valid-icon')).toBeInTheDocument();
  });

  it('hides validation icon when showValidationIcon is false', () => {
    render(<NIPValidator showValidationIcon={false} value="1234563218" testId="nip-validator" />);
    
    expect(screen.queryByTestId('nip-validator-valid-icon')).not.toBeInTheDocument();
  });

  it('performs real-time validation when realTimeValidation is true', () => {
    const handleChange = jest.fn();
    render(<NIPValidator realTimeValidation={true} onChange={handleChange} testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.change(input, { target: { value: '1234563218' } });
    
    // Should validate immediately without blur
    expect(handleChange).toHaveBeenCalledWith('1234563218', true);
  });

  it('does not perform real-time validation when realTimeValidation is false', () => {
    const handleChange = jest.fn();
    render(<NIPValidator realTimeValidation={false} onChange={handleChange} testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.change(input, { target: { value: '1234563218' } });
    
    // Should not validate until blur
    expect(handleChange).toHaveBeenCalledWith('1234563218', false);
  });

  it('shows custom error message when provided', () => {
    render(
      <NIPValidator 
        error={true} 
        errorMessage="Custom error message" 
        testId="nip-validator" 
      />
    );
    
    expect(screen.getByTestId('nip-validator-error')).toHaveTextContent('Custom error message');
  });

  it('is disabled when disabled prop is true', () => {
    render(<NIPValidator disabled={true} testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    expect(input).toBeDisabled();
  });

  it('calls onBlur when input loses focus', () => {
    const handleBlur = jest.fn();
    render(<NIPValidator onBlur={handleBlur} testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.focus(input);
    fireEvent.blur(input);
    
    expect(handleBlur).toHaveBeenCalled();
  });

  it('handles empty input correctly', () => {
    const handleChange = jest.fn();
    render(<NIPValidator onChange={handleChange} testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    fireEvent.change(input, { target: { value: '' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith('', false);
    expect(screen.queryByTestId('nip-validator-error')).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<NIPValidator className="custom-class" testId="nip-validator" />);
    
    const container = screen.getByTestId('nip-validator').parentElement;
    expect(container).toHaveClass('custom-class');
  });

  it('formats partial input correctly', () => {
    render(<NIPValidator testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator');
    
    fireEvent.change(input, { target: { value: '123' } });
    expect((input as HTMLInputElement).value).toBe('123');
    
    fireEvent.change(input, { target: { value: '123456' } });
    expect((input as HTMLInputElement).value).toBe('123-456');
    
    fireEvent.change(input, { target: { value: '12345678' } });
    expect((input as HTMLInputElement).value).toBe('123-456-78');
  });

  it('handles controlled value prop', () => {
    const { rerender } = render(<NIPValidator value="123456" testId="nip-validator" />);
    
    const input = screen.getByTestId('nip-validator') as HTMLInputElement;
    expect(input.value).toBe('123-456');
    
    rerender(<NIPValidator value="1234567890" testId="nip-validator" />);
    expect(input.value).toBe('123-456-78-90');
  });
});