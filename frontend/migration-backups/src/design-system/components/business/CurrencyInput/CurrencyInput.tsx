import React, { useState, useCallback } from 'react';
import { Input } from '../../primitives/Input/Input';
import { cn } from '../../../utils/cn';

export interface CurrencyInputProps {
  value?: number | string;
  onChange?: (value: number | null) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  currency?: string;
  locale?: string;
  placeholder?: string;
  disabled?: boolean;
  error?: boolean;
  errorMessage?: string;
  className?: string;
  testId?: string;
  allowNegative?: boolean;
  maxDecimals?: number;
}

export const CurrencyInput: React.FC<CurrencyInputProps> = ({
  value,
  onChange,
  onBlur,
  currency = 'PLN',
  locale = 'pl-PL',
  placeholder = '0,00 zł',
  disabled = false,
  error = false,
  errorMessage,
  className,
  testId,
  allowNegative = false,
  maxDecimals = 2,
}) => {
  const [displayValue, setDisplayValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const formatCurrency = useCallback((num: number): string => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
      minimumFractionDigits: maxDecimals,
      maximumFractionDigits: maxDecimals,
    }).format(num);
  }, [locale, currency, maxDecimals]);

  const parseCurrency = useCallback((str: string): number | null => {
    if (!str || str.trim() === '') return null;
    
    // Remove currency symbols and spaces
    const cleaned = str
      .replace(/[^\d,.-]/g, '')
      .replace(',', '.');
    
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? null : parsed;
  }, []);

  const formatForDisplay = useCallback((num: number | string | undefined): string => {
    if (num === undefined || num === null || num === '') return '';
    
    const numValue = typeof num === 'string' ? parseCurrency(num) : num;
    if (numValue === null) return '';
    
    return formatCurrency(numValue);
  }, [formatCurrency, parseCurrency]);

  const formatForEditing = useCallback((num: number | string | undefined): string => {
    if (num === undefined || num === null || num === '') return '';
    
    const numValue = typeof num === 'string' ? parseCurrency(num) : num;
    if (numValue === null) return '';
    
    // Format for editing (just the number with Polish decimal separator)
    return numValue.toFixed(maxDecimals).replace('.', ',');
  }, [parseCurrency, maxDecimals]);

  React.useEffect(() => {
    if (!isFocused) {
      setDisplayValue(formatForDisplay(value));
    }
  }, [value, isFocused, formatForDisplay]);

  const handleFocus = (event: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(true);
    setDisplayValue(formatForEditing(value));
    event.target.select();
  };

  const handleBlur = (event: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false);
    const numValue = parseCurrency(displayValue);
    
    if (numValue !== null && !allowNegative && numValue < 0) {
      const positiveValue = Math.abs(numValue);
      onChange?.(positiveValue);
      setDisplayValue(formatForDisplay(positiveValue));
    } else {
      onChange?.(numValue);
      setDisplayValue(formatForDisplay(numValue));
    }
    
    onBlur?.(event);
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = event.target.value;
    
    // Allow only numbers, comma, dot, and minus (if negative allowed)
    const allowedChars = allowNegative ? /[0-9,.-]/ : /[0-9,.]/;
    const filteredValue = inputValue
      .split('')
      .filter(char => allowedChars.test(char))
      .join('');
    
    setDisplayValue(filteredValue);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    // Allow: backspace, delete, tab, escape, enter
    if ([8, 9, 27, 13, 46].indexOf(event.keyCode) !== -1 ||
        // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
        (event.keyCode === 65 && event.ctrlKey === true) ||
        (event.keyCode === 67 && event.ctrlKey === true) ||
        (event.keyCode === 86 && event.ctrlKey === true) ||
        (event.keyCode === 88 && event.ctrlKey === true) ||
        // Allow: home, end, left, right
        (event.keyCode >= 35 && event.keyCode <= 39)) {
      return;
    }
    
    // Ensure that it is a number and stop the keypress
    if ((event.shiftKey || (event.keyCode < 48 || event.keyCode > 57)) && 
        (event.keyCode < 96 || event.keyCode > 105) &&
        // Allow comma and dot
        event.keyCode !== 188 && event.keyCode !== 190 && event.keyCode !== 110 &&
        // Allow minus if negative allowed
        !(allowNegative && event.keyCode === 189)) {
      event.preventDefault();
    }
  };

  return (
    <div className={cn('relative', className)}>
      <Input
        value={displayValue}
        onChange={handleChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        error={error}
        className="text-right"
        testId={testId}
      />
      
      {!isFocused && !disabled && (
        <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
          <span className="text-neutral-500 text-sm">{currency}</span>
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

CurrencyInput.displayName = 'CurrencyInput';