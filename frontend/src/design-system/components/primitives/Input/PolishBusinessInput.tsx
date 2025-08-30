// Polish Business Input Components
import React, { forwardRef, useState, useCallback } from 'react';
import { Input, InputProps } from './Input';
import { polishBusinessTypography } from '../../utils/typographyUtils';

// Currency Input Component
export interface CurrencyInputProps extends Omit<InputProps, 'type' | 'value' | 'onChange'> {
  /** Currency value in PLN */
  value?: number;
  /** Default currency value */
  defaultValue?: number;
  /** Change handler with numeric value */
  onChange?: (value: number | null) => void;
  /** Currency symbol */
  currency?: string;
  /** Number of decimal places */
  decimals?: number;
  /** Minimum value */
  min?: number;
  /** Maximum value */
  max?: number;
  /** Allow negative values */
  allowNegative?: boolean;
}

export const CurrencyInput = forwardRef<HTMLInputElement, CurrencyInputProps>(
  (
    {
      value,
      defaultValue,
      onChange,
      currency = 'zł',
      decimals = 2,
      min,
      max,
      allowNegative = false,
      placeholder = '0,00',
      className,
      ...rest
    },
    ref
  ) => {
    const [displayValue, setDisplayValue] = useState(() => {
      const initialValue = value ?? defaultValue;
      return initialValue !== undefined 
        ? polishBusinessTypography.formatCurrency(initialValue, { showSymbol: false, decimals })
        : '';
    });

    // Format number for display
    const formatForDisplay = useCallback((num: number): string => {
      return polishBusinessTypography.formatCurrency(num, { showSymbol: false, decimals });
    }, [decimals]);

    // Parse display value to number
    const parseDisplayValue = useCallback((str: string): number | null => {
      if (!str.trim()) return null;
      
      // Remove spaces and replace comma with dot
      const cleaned = str.replace(/\s/g, '').replace(',', '.');
      const parsed = parseFloat(cleaned);
      
      return isNaN(parsed) ? null : parsed;
    }, []);

    // Handle input change
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = event.target.value;
      setDisplayValue(inputValue);
      
      const numericValue = parseDisplayValue(inputValue);
      
      // Validate range
      if (numericValue !== null) {
        if (!allowNegative && numericValue < 0) return;
        if (min !== undefined && numericValue < min) return;
        if (max !== undefined && numericValue > max) return;
      }
      
      onChange?.(numericValue);
    };

    // Handle blur to format the value
    const handleBlur = (event: React.FocusEvent<HTMLInputElement>) => {
      const numericValue = parseDisplayValue(displayValue);
      if (numericValue !== null) {
        setDisplayValue(formatForDisplay(numericValue));
      }
      rest.onBlur?.(event);
    };

    // Currency icon
    const CurrencyIcon = () => (
      <span className="text-text-muted font-medium">{currency}</span>
    );

    return (
      <Input
        ref={ref}
        type="text"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder={placeholder}
        icon={<CurrencyIcon />}
        iconPosition="end"
        className={clsx('typography-currency', className)}
        inputMode="decimal"
        {...rest}
      />
    );
  }
);

CurrencyInput.displayName = 'CurrencyInput';

// NIP Input Component
export interface NIPInputProps extends Omit<InputProps, 'type' | 'maxLength' | 'pattern'> {
  /** Change handler with validation status */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>, isValid: boolean) => void;
  /** Show validation status */
  showValidation?: boolean;
}

export const NIPInput = forwardRef<HTMLInputElement, NIPInputProps>(
  (
    {
      value,
      onChange,
      showValidation = true,
      placeholder = '123-456-78-90',
      className,
      ...rest
    },
    ref
  ) => {
    const [isValid, setIsValid] = useState<boolean | null>(null);

    // Validate NIP number
    const validateNIP = useCallback((nip: string): boolean => {
      const cleanNip = nip.replace(/\D/g, '');
      if (cleanNip.length !== 10) return false;
      
      // NIP checksum validation
      const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
      let sum = 0;
      
      for (let i = 0; i < 9; i++) {
        sum += parseInt(cleanNip[i]) * weights[i];
      }
      
      const checksum = sum % 11;
      return checksum === parseInt(cleanNip[9]);
    }, []);

    // Format NIP for display
    const formatNIP = useCallback((nip: string): string => {
      const cleanNip = nip.replace(/\D/g, '');
      if (cleanNip.length <= 3) return cleanNip;
      if (cleanNip.length <= 6) return `${cleanNip.slice(0, 3)}-${cleanNip.slice(3)}`;
      if (cleanNip.length <= 8) return `${cleanNip.slice(0, 3)}-${cleanNip.slice(3, 6)}-${cleanNip.slice(6)}`;
      return `${cleanNip.slice(0, 3)}-${cleanNip.slice(3, 6)}-${cleanNip.slice(6, 8)}-${cleanNip.slice(8, 10)}`;
    }, []);

    // Handle input change
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = event.target.value;
      const formattedValue = formatNIP(inputValue);
      
      // Update the input value
      event.target.value = formattedValue;
      
      // Validate
      const valid = validateNIP(formattedValue);
      setIsValid(formattedValue.length > 0 ? valid : null);
      
      onChange?.(event, valid);
    };

    // Validation icon
    const ValidationIcon = () => {
      if (!showValidation || isValid === null) return null;
      
      return isValid ? (
        <svg className="w-5 h-5 text-success-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-error-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      );
    };

    return (
      <Input
        ref={ref}
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        maxLength={13} // 123-456-78-90
        icon={showValidation ? <ValidationIcon /> : undefined}
        iconPosition="end"
        error={showValidation && isValid === false}
        className={clsx('typography-nip', className)}
        {...rest}
      />
    );
  }
);

NIPInput.displayName = 'NIPInput';

// REGON Input Component
export interface REGONInputProps extends Omit<InputProps, 'type' | 'maxLength'> {
  /** REGON type (9 or 14 digits) */
  regonType?: 9 | 14;
  /** Change handler with validation status */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>, isValid: boolean) => void;
  /** Show validation status */
  showValidation?: boolean;
}

export const REGONInput = forwardRef<HTMLInputElement, REGONInputProps>(
  (
    {
      regonType = 9,
      value,
      onChange,
      showValidation = true,
      placeholder,
      className,
      ...rest
    },
    ref
  ) => {
    const [isValid, setIsValid] = useState<boolean | null>(null);

    // Validate REGON number
    const validateREGON = useCallback((regon: string, type: 9 | 14): boolean => {
      const cleanRegon = regon.replace(/\D/g, '');
      if (cleanRegon.length !== type) return false;
      
      // REGON checksum validation (simplified)
      const weights9 = [8, 9, 2, 3, 4, 5, 6, 7];
      const weights14 = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8];
      
      const weights = type === 9 ? weights9 : weights14;
      let sum = 0;
      
      for (let i = 0; i < weights.length; i++) {
        sum += parseInt(cleanRegon[i]) * weights[i];
      }
      
      const checksum = sum % 11;
      const expectedChecksum = checksum === 10 ? 0 : checksum;
      return expectedChecksum === parseInt(cleanRegon[weights.length]);
    }, []);

    // Format REGON for display
    const formatREGON = useCallback((regon: string, type: 9 | 14): string => {
      const cleanRegon = regon.replace(/\D/g, '');
      
      if (type === 9) {
        if (cleanRegon.length <= 3) return cleanRegon;
        if (cleanRegon.length <= 6) return `${cleanRegon.slice(0, 3)}-${cleanRegon.slice(3)}`;
        return `${cleanRegon.slice(0, 3)}-${cleanRegon.slice(3, 6)}-${cleanRegon.slice(6, 9)}`;
      } else {
        if (cleanRegon.length <= 3) return cleanRegon;
        if (cleanRegon.length <= 6) return `${cleanRegon.slice(0, 3)}-${cleanRegon.slice(3)}`;
        if (cleanRegon.length <= 8) return `${cleanRegon.slice(0, 3)}-${cleanRegon.slice(3, 6)}-${cleanRegon.slice(6)}`;
        return `${cleanRegon.slice(0, 3)}-${cleanRegon.slice(3, 6)}-${cleanRegon.slice(6, 8)}-${cleanRegon.slice(8, 14)}`;
      }
    }, []);

    // Handle input change
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = event.target.value;
      const formattedValue = formatREGON(inputValue, regonType);
      
      // Update the input value
      event.target.value = formattedValue;
      
      // Validate
      const valid = validateREGON(formattedValue, regonType);
      setIsValid(formattedValue.length > 0 ? valid : null);
      
      onChange?.(event, valid);
    };

    // Validation icon (same as NIP)
    const ValidationIcon = () => {
      if (!showValidation || isValid === null) return null;
      
      return isValid ? (
        <svg className="w-5 h-5 text-success-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-error-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      );
    };

    const defaultPlaceholder = regonType === 9 ? '123-456-789' : '123-456-78-901234';

    return (
      <Input
        ref={ref}
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={placeholder || defaultPlaceholder}
        maxLength={regonType === 9 ? 11 : 17} // Including dashes
        icon={showValidation ? <ValidationIcon /> : undefined}
        iconPosition="end"
        error={showValidation && isValid === false}
        className={clsx('font-mono', className)}
        {...rest}
      />
    );
  }
);

REGONInput.displayName = 'REGONInput';

// Postal Code Input Component
export interface PostalCodeInputProps extends Omit<InputProps, 'type' | 'maxLength' | 'pattern'> {
  /** Change handler with validation status */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>, isValid: boolean) => void;
  /** Show validation status */
  showValidation?: boolean;
}

export const PostalCodeInput = forwardRef<HTMLInputElement, PostalCodeInputProps>(
  (
    {
      value,
      onChange,
      showValidation = true,
      placeholder = '00-000',
      className,
      ...rest
    },
    ref
  ) => {
    const [isValid, setIsValid] = useState<boolean | null>(null);

    // Validate Polish postal code
    const validatePostalCode = useCallback((code: string): boolean => {
      const cleanCode = code.replace(/\D/g, '');
      return cleanCode.length === 5;
    }, []);

    // Format postal code for display
    const formatPostalCode = useCallback((code: string): string => {
      const cleanCode = code.replace(/\D/g, '');
      if (cleanCode.length <= 2) return cleanCode;
      return `${cleanCode.slice(0, 2)}-${cleanCode.slice(2, 5)}`;
    }, []);

    // Handle input change
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = event.target.value;
      const formattedValue = formatPostalCode(inputValue);
      
      // Update the input value
      event.target.value = formattedValue;
      
      // Validate
      const valid = validatePostalCode(formattedValue);
      setIsValid(formattedValue.length > 0 ? valid : null);
      
      onChange?.(event, valid);
    };

    // Validation icon (same as NIP)
    const ValidationIcon = () => {
      if (!showValidation || isValid === null) return null;
      
      return isValid ? (
        <svg className="w-5 h-5 text-success-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-error-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      );
    };

    return (
      <Input
        ref={ref}
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        maxLength={6} // 00-000
        icon={showValidation ? <ValidationIcon /> : undefined}
        iconPosition="end"
        error={showValidation && isValid === false}
        className={clsx('font-mono', className)}
        {...rest}
      />
    );
  }
);

PostalCodeInput.displayName = 'PostalCodeInput';

// Phone Input Component
export interface PhoneInputProps extends Omit<InputProps, 'type'> {
  /** Change handler with validation status */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>, isValid: boolean) => void;
  /** Show validation status */
  showValidation?: boolean;
  /** Include country code */
  includeCountryCode?: boolean;
}

export const PhoneInput = forwardRef<HTMLInputElement, PhoneInputProps>(
  (
    {
      value,
      onChange,
      showValidation = true,
      includeCountryCode = false,
      placeholder,
      className,
      ...rest
    },
    ref
  ) => {
    const [isValid, setIsValid] = useState<boolean | null>(null);

    // Validate Polish phone number
    const validatePhone = useCallback((phone: string, withCountryCode: boolean): boolean => {
      const cleanPhone = phone.replace(/\D/g, '');
      
      if (withCountryCode) {
        return cleanPhone.length === 11 && cleanPhone.startsWith('48');
      } else {
        return cleanPhone.length === 9;
      }
    }, []);

    // Format phone number for display
    const formatPhone = useCallback((phone: string, withCountryCode: boolean): string => {
      const cleanPhone = phone.replace(/\D/g, '');
      
      if (withCountryCode) {
        if (cleanPhone.length <= 2) return cleanPhone;
        if (cleanPhone.length <= 5) return `+${cleanPhone.slice(0, 2)} ${cleanPhone.slice(2)}`;
        if (cleanPhone.length <= 8) return `+${cleanPhone.slice(0, 2)} ${cleanPhone.slice(2, 5)} ${cleanPhone.slice(5)}`;
        return `+${cleanPhone.slice(0, 2)} ${cleanPhone.slice(2, 5)} ${cleanPhone.slice(5, 8)} ${cleanPhone.slice(8, 11)}`;
      } else {
        if (cleanPhone.length <= 3) return cleanPhone;
        if (cleanPhone.length <= 6) return `${cleanPhone.slice(0, 3)} ${cleanPhone.slice(3)}`;
        return `${cleanPhone.slice(0, 3)} ${cleanPhone.slice(3, 6)} ${cleanPhone.slice(6, 9)}`;
      }
    }, []);

    // Handle input change
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = event.target.value;
      const formattedValue = formatPhone(inputValue, includeCountryCode);
      
      // Update the input value
      event.target.value = formattedValue;
      
      // Validate
      const valid = validatePhone(formattedValue, includeCountryCode);
      setIsValid(formattedValue.length > 0 ? valid : null);
      
      onChange?.(event, valid);
    };

    // Phone icon
    const PhoneIcon = () => (
      <svg className="w-5 h-5 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
      </svg>
    );

    // Validation icon
    const ValidationIcon = () => {
      if (!showValidation || isValid === null) return null;
      
      return isValid ? (
        <svg className="w-5 h-5 text-success-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-error-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      );
    };

    const defaultPlaceholder = includeCountryCode ? '+48 123 456 789' : '123 456 789';

    return (
      <Input
        ref={ref}
        type="tel"
        value={value}
        onChange={handleChange}
        placeholder={placeholder || defaultPlaceholder}
        icon={showValidation ? <ValidationIcon /> : <PhoneIcon />}
        iconPosition={showValidation ? 'end' : 'start'}
        error={showValidation && isValid === false}
        className={clsx('font-mono', className)}
        {...rest}
      />
    );
  }
);

PhoneInput.displayName = 'PhoneInput';

// Import clsx for className handling
import { clsx } from 'clsx';

export default CurrencyInput;