import React, { useState, useEffect } from 'react';
import { Input } from '../../primitives/Input/Input';
import { cn } from '../../../utils/cn';

export interface NIPValidatorProps {
  value?: string;
  onChange?: (value: string, isValid: boolean) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: boolean;
  errorMessage?: string;
  className?: string;
  testId?: string;
  showValidationIcon?: boolean;
  realTimeValidation?: boolean;
}

export const NIPValidator: React.FC<NIPValidatorProps> = ({
  value = '',
  onChange,
  onBlur,
  placeholder = 'NIP (np. 123-456-78-90)',
  disabled = false,
  error = false,
  errorMessage,
  className,
  testId,
  showValidationIcon = true,
  realTimeValidation = true,
}) => {
  const [displayValue, setDisplayValue] = useState('');
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const [validationMessage, setValidationMessage] = useState('');

  const validateNIP = (nip: string): { isValid: boolean; message: string } => {
    if (!nip || nip.trim() === '') {
      return { isValid: false, message: '' };
    }

    // Remove all non-digit characters
    const cleanNIP = nip.replace(/\D/g, '');

    // Check length
    if (cleanNIP.length !== 10) {
      return { isValid: false, message: 'NIP musi składać się z 10 cyfr' };
    }

    // Check if all digits are the same
    if (/^(\d)\1{9}$/.test(cleanNIP)) {
      return { isValid: false, message: 'NIP nie może składać się z samych identycznych cyfr' };
    }

    // Calculate checksum
    const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
    let sum = 0;

    for (let i = 0; i < 9; i++) {
      sum += parseInt(cleanNIP[i]) * weights[i];
    }

    const checksum = sum % 11;
    const lastDigit = parseInt(cleanNIP[9]);

    if (checksum === 10) {
      return { isValid: false, message: 'Nieprawidłowy NIP - błędna suma kontrolna' };
    }

    if (checksum !== lastDigit) {
      return { isValid: false, message: 'Nieprawidłowy NIP - błędna suma kontrolna' };
    }

    return { isValid: true, message: 'NIP jest prawidłowy' };
  };

  const formatNIP = (nip: string): string => {
    const cleanNIP = nip.replace(/\D/g, '');
    
    if (cleanNIP.length <= 3) return cleanNIP;
    if (cleanNIP.length <= 6) return `${cleanNIP.slice(0, 3)}-${cleanNIP.slice(3)}`;
    if (cleanNIP.length <= 8) return `${cleanNIP.slice(0, 3)}-${cleanNIP.slice(3, 6)}-${cleanNIP.slice(6)}`;
    return `${cleanNIP.slice(0, 3)}-${cleanNIP.slice(3, 6)}-${cleanNIP.slice(6, 8)}-${cleanNIP.slice(8, 10)}`;
  };

  useEffect(() => {
    const formatted = formatNIP(value);
    setDisplayValue(formatted);
    
    if (realTimeValidation && value) {
      const validation = validateNIP(value);
      setIsValid(validation.isValid);
      setValidationMessage(validation.message);
    }
  }, [value, realTimeValidation]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = event.target.value;
    const cleanValue = inputValue.replace(/\D/g, '');
    
    // Limit to 10 digits
    if (cleanValue.length > 10) return;
    
    const formatted = formatNIP(cleanValue);
    setDisplayValue(formatted);
    
    let validation = { isValid: false, message: '' };
    
    if (realTimeValidation) {
      validation = validateNIP(cleanValue);
      setIsValid(validation.isValid);
      setValidationMessage(validation.message);
    }
    
    onChange?.(cleanValue, validation.isValid);
  };

  const handleBlur = (event: React.FocusEvent<HTMLInputElement>) => {
    const cleanValue = displayValue.replace(/\D/g, '');
    const validation = validateNIP(cleanValue);
    
    setIsValid(validation.isValid);
    setValidationMessage(validation.message);
    
    onChange?.(cleanValue, validation.isValid);
    onBlur?.(event);
  };

  const getValidationIcon = () => {
    if (!showValidationIcon || isValid === null) return null;
    
    if (isValid) {
      return (
        <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
          <svg
            className="w-5 h-5 text-success-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            data-testid={`${testId}-valid-icon`}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
      );
    } else {
      return (
        <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
          <svg
            className="w-5 h-5 text-error-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            data-testid={`${testId}-invalid-icon`}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </div>
      );
    }
  };

  const hasError = error || (isValid === false && validationMessage !== '');
  const currentErrorMessage = errorMessage || (isValid === false ? validationMessage : '');

  return (
    <div className={cn('relative', className)}>
      <Input
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder={placeholder}
        disabled={disabled}
        error={hasError}
        testId={testId}
        maxLength={13} // XXX-XXX-XX-XX format
      />
      
      {getValidationIcon()}
      
      {currentErrorMessage && hasError && (
        <p className="mt-1 text-sm text-error-600" data-testid={`${testId}-error`}>
          {currentErrorMessage}
        </p>
      )}
      
      {isValid === true && validationMessage && !hasError && (
        <p className="mt-1 text-sm text-success-600" data-testid={`${testId}-success`}>
          {validationMessage}
        </p>
      )}
    </div>
  );
};

NIPValidator.displayName = 'NIPValidator';