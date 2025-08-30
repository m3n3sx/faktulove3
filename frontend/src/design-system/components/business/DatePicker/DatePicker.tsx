import React, { useState, useRef, useEffect } from 'react';
import { Input } from '../../primitives/Input/Input';
import { cn } from '../../../utils/cn';
import { Grid } from '../../layouts/Grid/Grid';

export interface DatePickerProps {
  value?: Date | string;
  onChange?: (date: Date | null) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: boolean;
  errorMessage?: string;
  className?: string;
  testId?: string;
  minDate?: Date;
  maxDate?: Date;
  locale?: string;
}

export const DatePicker: React.FC<DatePickerProps> = ({
  value,
  onChange,
  onBlur,
  placeholder = 'DD.MM.YYYY',
  disabled = false,
  error = false,
  errorMessage,
  className,
  testId,
  minDate,
  maxDate,
  locale = 'pl-PL',
}) => {
  const [displayValue, setDisplayValue] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const calendarRef = useRef<HTMLDivElement>(null);

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString(locale, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const parseDate = (str: string): Date | null => {
    if (!str || str.trim() === '') return null;
    
    // Handle DD.MM.YYYY format
    const parts = str.split('.');
    if (parts.length !== 3) return null;
    
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; // Month is 0-indexed
    const year = parseInt(parts[2], 10);
    
    if (isNaN(day) || isNaN(month) || isNaN(year)) return null;
    if (day < 1 || day > 31 || month < 0 || month > 11 || year < 1900) return null;
    
    const date = new Date(year, month, day);
    
    // Check if the date is valid (handles invalid dates like 31.02.2023)
    if (date.getDate() !== day || date.getMonth() !== month || date.getFullYear() !== year) {
      return null;
    }
    
    return date;
  };

  React.useEffect(() => {
    if (value) {
      const date = value instanceof Date ? value : parseDate(value);
      setSelectedDate(date);
      setDisplayValue(date ? formatDate(date) : '');
    } else {
      setSelectedDate(null);
      setDisplayValue('');
    }
  }, [value]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    let inputValue = event.target.value;
    
    // Auto-format as user types
    inputValue = inputValue.replace(/[^\d]/g, '');
    
    if (inputValue.length >= 2 && inputValue.length < 4) {
      inputValue = inputValue.slice(0, 2) + '.' + inputValue.slice(2);
    } else if (inputValue.length >= 4) {
      inputValue = inputValue.slice(0, 2) + '.' + inputValue.slice(2, 4) + '.' + inputValue.slice(4, 8);
    }
    
    setDisplayValue(inputValue);
  };

  const handleInputBlur = (event: React.FocusEvent<HTMLInputElement>) => {
    const date = parseDate(displayValue);
    
    if (date) {
      // Validate against min/max dates
      if (minDate && date < minDate) {
        setDisplayValue('');
        onChange?.(null);
      } else if (maxDate && date > maxDate) {
        setDisplayValue('');
        onChange?.(null);
      } else {
        setSelectedDate(date);
        setDisplayValue(formatDate(date));
        onChange?.(date);
      }
    } else if (displayValue.trim() !== '') {
      // Invalid date format
      setDisplayValue('');
      onChange?.(null);
    }
    
    onBlur?.(event);
  };

  const handleInputFocus = () => {
    setIsOpen(true);
  };

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    setDisplayValue(formatDate(date));
    setIsOpen(false);
    onChange?.(date);
    inputRef.current?.focus();
  };

  const generateCalendar = () => {
    const today = new Date();
    const currentMonth = selectedDate ? selectedDate.getMonth() : today.getMonth();
    const currentYear = selectedDate ? selectedDate.getFullYear() : today.getFullYear();
    
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay() + 1); // Start from Monday
    
    const days = [];
    const current = new Date(startDate);
    
    for (let i = 0; i < 42; i++) { // 6 weeks
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }
    
    return { days, currentMonth, currentYear };
  };

  const { days, currentMonth, currentYear } = generateCalendar();

  const isDateDisabled = (date: Date) => {
    if (minDate && date < minDate) return true;
    if (maxDate && date > maxDate) return true;
    return false;
  };

  const isDateSelected = (date: Date) => {
    return selectedDate && 
           date.getDate() === selectedDate.getDate() &&
           date.getMonth() === selectedDate.getMonth() &&
           date.getFullYear() === selectedDate.getFullYear();
  };

  const isDateToday = (date: Date) => {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
  };

  // Close calendar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (calendarRef.current && !calendarRef.current.contains(event.target as Node) &&
          inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  return (
    <div className={cn('relative', className)}>
      <Input
        ref={inputRef}
        value={displayValue}
        onChange={handleInputChange}
        onFocus={handleInputFocus}
        onBlur={handleInputBlur}
        placeholder={placeholder}
        disabled={disabled}
        error={error}
        testId={testId}
        maxLength={10}
      />
      
      {isOpen && !disabled && (
        <div
          ref={calendarRef}
          className={cn(
            'absolute top-full left-0 z-50 mt-1',
            'bg-white border border-neutral-200 rounded-md-lg shadow-sm-lg',
            'p-4 min-w-[280px]'
          )}
          data-testid={`${testId}-calendar`}
        >
          {/* Calendar Header */}
          <div className="flex items-center justify-between mb-4">
            <button
              type="button"
              onClick={() => {
                const newDate = new Date(currentYear, currentMonth - 1, 1);
                setSelectedDate(newDate);
              }}
              className="p-1 hover:bg-neutral-100 rounded-md"
              data-testid={`${testId}-prev-month`}
            >
              ←
            </button>
            
            <h3 className="font-medium">
              {new Date(currentYear, currentMonth).toLocaleDateString(locale, {
                month: 'long',
                year: 'numeric'
              })}
            </h3>
            
            <button
              type="button"
              onClick={() => {
                const newDate = new Date(currentYear, currentMonth + 1, 1);
                setSelectedDate(newDate);
              }}
              className="p-1 hover:bg-neutral-100 rounded-md"
              data-testid={`${testId}-next-month`}
            >
              →
            </button>
          </div>
          
          {/* Calendar Grid */}
          <div className="grid grid-cols-7">
            {['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'Sb', 'Nd'].map((day) => (
              <div key={day} className="text-center text-sm font-medium text-neutral-600 p-2">
                {day}
              </div>
            ))}
          </div>
          
          <div className="grid grid-cols-7">
            {days.map((date, index) => {
              const isCurrentMonth = date.getMonth() === currentMonth;
              const isDisabled = isDateDisabled(date);
              const isSelected = isDateSelected(date);
              const isToday = isDateToday(date);
              
              return (
                <button
                  key={index}
                  type="button"
                  onClick={() => !isDisabled && handleDateSelect(date)}
                  disabled={isDisabled}
                  className={cn(
                    'p-2 text-sm rounded-md hover:bg-neutral-100',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500',
                    !isCurrentMonth && 'text-neutral-400',
                    isSelected && 'bg-primary-600 text-white hover:bg-primary-700',
                    isToday && !isSelected && 'bg-primary-100 text-primary-900',
                    isDisabled && 'opacity-50 cursor-not-allowed hover:bg-transparent'
                  )}
                  data-testid={`${testId}-date-${date.getDate()}`}
                >
                  {date.getDate()}
                </button>
              );
            })}
          </div>
        </div>
      )}
      
      {errorMessage && error && (
        <p className="mt-1 text-sm text-error-600" data-testid={`${testId}-error`}>
          {errorMessage}
        </p>
      )}
    </div>
  );
};

DatePicker.displayName = 'DatePicker';