import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { DatePicker } from '../DatePicker/DatePicker';

describe('DatePicker Component', () => {
  it('renders with default props', () => {
    render(<DatePicker testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('placeholder', 'DD.MM.YYYY');
  });

  it('displays formatted date value', () => {
    const date = new Date(2023, 11, 25); // December 25, 2023
    render(<DatePicker value={date} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker') as HTMLInputElement;
    expect(input.value).toBe('25.12.2023');
  });

  it('opens calendar on focus', () => {
    render(<DatePicker testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.focus(input);
    
    const calendar = screen.getByTestId('date-picker-calendar');
    expect(calendar).toBeInTheDocument();
  });

  it('closes calendar when clicking outside', () => {
    render(
      <div>
        <DatePicker testId="date-picker" />
        <div data-testid="outside">Outside</div>
      </div>
    );
    
    const input = screen.getByTestId('date-picker');
    fireEvent.focus(input);
    
    const calendar = screen.getByTestId('date-picker-calendar');
    expect(calendar).toBeInTheDocument();
    
    const outside = screen.getByTestId('outside');
    fireEvent.mouseDown(outside);
    
    expect(screen.queryByTestId('date-picker-calendar')).not.toBeInTheDocument();
  });

  it('auto-formats input as user types', () => {
    render(<DatePicker testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    
    fireEvent.change(input, { target: { value: '25122023' } });
    expect((input as HTMLInputElement).value).toBe('25.12.2023');
  });

  it('calls onChange with parsed date', () => {
    const handleChange = jest.fn();
    render(<DatePicker onChange={handleChange} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.change(input, { target: { value: '25.12.2023' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith(new Date(2023, 11, 25));
  });

  it('handles invalid date input', () => {
    const handleChange = jest.fn();
    render(<DatePicker onChange={handleChange} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.change(input, { target: { value: '32.13.2023' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith(null);
    expect((input as HTMLInputElement).value).toBe('');
  });

  it('validates against minDate', () => {
    const minDate = new Date(2023, 11, 20);
    const handleChange = jest.fn();
    
    render(<DatePicker minDate={minDate} onChange={handleChange} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.change(input, { target: { value: '15.12.2023' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith(null);
    expect((input as HTMLInputElement).value).toBe('');
  });

  it('validates against maxDate', () => {
    const maxDate = new Date(2023, 11, 20);
    const handleChange = jest.fn();
    
    render(<DatePicker maxDate={maxDate} onChange={handleChange} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.change(input, { target: { value: '25.12.2023' } });
    fireEvent.blur(input);
    
    expect(handleChange).toHaveBeenCalledWith(null);
    expect((input as HTMLInputElement).value).toBe('');
  });

  it('allows selecting date from calendar', () => {
    const handleChange = jest.fn();
    render(<DatePicker onChange={handleChange} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.focus(input);
    
    const dateButton = screen.getByTestId('date-picker-date-15');
    fireEvent.click(dateButton);
    
    expect(handleChange).toHaveBeenCalled();
    expect(screen.queryByTestId('date-picker-calendar')).not.toBeInTheDocument();
  });

  it('navigates between months in calendar', () => {
    render(<DatePicker value={new Date(2023, 11, 15)} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.focus(input);
    
    const nextButton = screen.getByTestId('date-picker-next-month');
    fireEvent.click(nextButton);
    
    // Should show January 2024
    expect(screen.getByText(/styczeń 2024/i)).toBeInTheDocument();
  });

  it('shows error message when error is true', () => {
    render(
      <DatePicker 
        error={true} 
        errorMessage="Invalid date" 
        testId="date-picker" 
      />
    );
    
    const errorMessage = screen.getByTestId('date-picker-error');
    expect(errorMessage).toHaveTextContent('Invalid date');
  });

  it('is disabled when disabled prop is true', () => {
    render(<DatePicker disabled={true} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    expect(input).toBeDisabled();
  });

  it('does not open calendar when disabled', () => {
    render(<DatePicker disabled={true} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.focus(input);
    
    const calendar = screen.queryByTestId('date-picker-calendar');
    expect(calendar).not.toBeInTheDocument();
  });

  it('highlights today in calendar', () => {
    const today = new Date();
    render(<DatePicker testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.focus(input);
    
    const todayButton = screen.getByTestId(`date-picker-date-${today.getDate()}`);
    expect(todayButton).toHaveClass('bg-primary-100');
  });

  it('highlights selected date in calendar', () => {
    const selectedDate = new Date(2023, 11, 15);
    render(<DatePicker value={selectedDate} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.focus(input);
    
    const selectedButton = screen.getByTestId('date-picker-date-15');
    expect(selectedButton).toHaveClass('bg-primary-600', 'text-white');
  });

  it('disables dates outside min/max range in calendar', () => {
    const minDate = new Date(2023, 11, 10);
    const maxDate = new Date(2023, 11, 20);
    
    render(
      <DatePicker 
        minDate={minDate} 
        maxDate={maxDate} 
        value={new Date(2023, 11, 15)} 
        testId="date-picker" 
      />
    );
    
    const input = screen.getByTestId('date-picker');
    fireEvent.focus(input);
    
    const disabledButton = screen.getByTestId('date-picker-date-5');
    expect(disabledButton).toBeDisabled();
    expect(disabledButton).toHaveClass('opacity-50', 'cursor-not-allowed');
  });

  it('calls onBlur when input loses focus', () => {
    const handleBlur = jest.fn();
    render(<DatePicker onBlur={handleBlur} testId="date-picker" />);
    
    const input = screen.getByTestId('date-picker');
    fireEvent.focus(input);
    fireEvent.blur(input);
    
    expect(handleBlur).toHaveBeenCalled();
  });
});