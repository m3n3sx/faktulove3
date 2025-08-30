import React, { createContext, useContext, useState, useCallback, FormEvent } from 'react';
import { BaseComponentProps } from '../../../types';

// Polish validation patterns
export const POLISH_VALIDATION_PATTERNS = {
  NIP: /^\d{3}-?\d{3}-?\d{2}-?\d{2}$|^\d{3}-?\d{2}-?\d{2}-?\d{3}$/,
  REGON: /^\d{9}$|^\d{14}$/,
  PESEL: /^\d{11}$/,
  POSTAL_CODE: /^\d{2}-\d{3}$/,
  PHONE: /^(\+48\s?)?(\d{3}\s?\d{3}\s?\d{3}|\d{2}\s?\d{3}\s?\d{2}\s?\d{2})$/,
} as const;

// Validation functions
export const validateNIP = (nip: string): boolean => {
  const cleanNip = nip.replace(/[-\s]/g, '');
  if (!POLISH_VALIDATION_PATTERNS.NIP.test(cleanNip)) return false;
  
  // NIP checksum validation
  const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
  const digits = cleanNip.split('').map(Number);
  const sum = digits.slice(0, 9).reduce((acc, digit, index) => acc + digit * weights[index], 0);
  const checksum = sum % 11;
  
  return checksum === digits[9];
};

export const validateREGON = (regon: string): boolean => {
  const cleanRegon = regon.replace(/[-\s]/g, '');
  if (!POLISH_VALIDATION_PATTERNS.REGON.test(cleanRegon)) return false;
  
  // REGON checksum validation for 9-digit REGON
  if (cleanRegon.length === 9) {
    const weights = [8, 9, 2, 3, 4, 5, 6, 7];
    const digits = cleanRegon.split('').map(Number);
    const sum = digits.slice(0, 8).reduce((acc, digit, index) => acc + digit * weights[index], 0);
    const checksum = sum % 11;
    const expectedChecksum = checksum === 10 ? 0 : checksum;
    
    return expectedChecksum === digits[8];
  }
  
  return true; // For 14-digit REGON, basic format validation is sufficient
};

// Form validation types
export interface ValidationRule {
  required?: boolean;
  pattern?: RegExp;
  minLength?: number;
  maxLength?: number;
  custom?: (value: any) => string | null;
  polishValidator?: 'NIP' | 'REGON' | 'PESEL' | 'POSTAL_CODE' | 'PHONE';
}

export interface FormField {
  name: string;
  value: any;
  error?: string;
  touched: boolean;
  rules?: ValidationRule;
}

export interface FormState {
  fields: Record<string, FormField>;
  isSubmitting: boolean;
  isValid: boolean;
  errors: Record<string, string>;
}

// Form context
interface FormContextValue {
  state: FormState;
  updateField: (name: string, value: any) => void;
  validateField: (name: string) => void;
  setFieldTouched: (name: string) => void;
  registerField: (name: string, rules?: ValidationRule) => void;
  unregisterField: (name: string) => void;
}

const FormContext = createContext<FormContextValue | null>(null);

export const useFormContext = () => {
  const context = useContext(FormContext);
  if (!context) {
    throw new Error('useFormContext must be used within a Form component');
  }
  return context;
};

// Form field validation
const validateFieldValue = (value: any, rules?: ValidationRule): string | null => {
  if (!rules) return null;

  // Required validation
  if (rules.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
    return 'To pole jest wymagane';
  }

  // Skip other validations if field is empty and not required
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return null;
  }

  // Pattern validation
  if (rules.pattern && typeof value === 'string' && !rules.pattern.test(value)) {
    return 'Nieprawidłowy format';
  }

  // Length validation
  if (rules.minLength && typeof value === 'string' && value.length < rules.minLength) {
    return `Minimalna długość: ${rules.minLength} znaków`;
  }

  if (rules.maxLength && typeof value === 'string' && value.length > rules.maxLength) {
    return `Maksymalna długość: ${rules.maxLength} znaków`;
  }

  // Polish-specific validation
  if (rules.polishValidator && typeof value === 'string') {
    switch (rules.polishValidator) {
      case 'NIP':
        return validateNIP(value) ? null : 'Nieprawidłowy numer NIP';
      case 'REGON':
        return validateREGON(value) ? null : 'Nieprawidłowy numer REGON';
      case 'PESEL':
        return POLISH_VALIDATION_PATTERNS.PESEL.test(value.replace(/[-\s]/g, '')) ? null : 'Nieprawidłowy numer PESEL';
      case 'POSTAL_CODE':
        return POLISH_VALIDATION_PATTERNS.POSTAL_CODE.test(value) ? null : 'Nieprawidłowy kod pocztowy (format: 00-000)';
      case 'PHONE':
        return POLISH_VALIDATION_PATTERNS.PHONE.test(value) ? null : 'Nieprawidłowy numer telefonu';
    }
  }

  // Custom validation
  if (rules.custom) {
    return rules.custom(value);
  }

  return null;
};

// Form component props
export interface FormProps extends BaseComponentProps {
  onSubmit: (data: Record<string, any>) => void | Promise<void>;
  initialValues?: Record<string, any>;
  validationMode?: 'onChange' | 'onBlur' | 'onSubmit';
  children: React.ReactNode;
}

export interface FormFieldProps extends BaseComponentProps {
  name: string;
  label?: string;
  rules?: ValidationRule;
  children: React.ReactElement;
}

// Form component
export const Form: React.FC<FormProps> = ({
  onSubmit,
  initialValues = {},
  validationMode = 'onBlur',
  children,
  className = '',
  testId = 'form',
  ...props
}) => {
  const [state, setState] = useState<FormState>({
    fields: {},
    isSubmitting: false,
    isValid: true,
    errors: {},
  });

  const updateField = useCallback((name: string, value: any) => {
    setState(prev => {
      const field = prev.fields[name];
      if (!field) return prev;

      const error = validationMode === 'onChange' 
        ? validateFieldValue(value, field.rules)
        : field.error;

      const updatedField = { ...field, value, error };
      const updatedFields = { ...prev.fields, [name]: updatedField };
      
      // Update form-level validation state
      const errors = Object.fromEntries(
        Object.entries(updatedFields)
          .filter(([, field]) => field.error)
          .map(([name, field]) => [name, field.error!])
      );
      
      return {
        ...prev,
        fields: updatedFields,
        errors,
        isValid: Object.keys(errors).length === 0,
      };
    });
  }, [validationMode]);

  const validateField = useCallback((name: string) => {
    setState(prev => {
      const field = prev.fields[name];
      if (!field) return prev;

      const error = validateFieldValue(field.value, field.rules);
      const updatedField = { ...field, error };
      const updatedFields = { ...prev.fields, [name]: updatedField };
      
      const errors = Object.fromEntries(
        Object.entries(updatedFields)
          .filter(([, field]) => field.error)
          .map(([name, field]) => [name, field.error!])
      );
      
      return {
        ...prev,
        fields: updatedFields,
        errors,
        isValid: Object.keys(errors).length === 0,
      };
    });
  }, []);

  const setFieldTouched = useCallback((name: string) => {
    setState(prev => {
      const field = prev.fields[name];
      if (!field || field.touched) return prev;

      const error = validationMode === 'onBlur' 
        ? validateFieldValue(field.value, field.rules)
        : field.error;

      const updatedField = { ...field, touched: true, error };
      const updatedFields = { ...prev.fields, [name]: updatedField };
      
      const errors = Object.fromEntries(
        Object.entries(updatedFields)
          .filter(([, field]) => field.error)
          .map(([name, field]) => [name, field.error!])
      );
      
      return {
        ...prev,
        fields: updatedFields,
        errors,
        isValid: Object.keys(errors).length === 0,
      };
    });
  }, [validationMode]);

  const registerField = useCallback((name: string, rules?: ValidationRule) => {
    setState(prev => {
      if (prev.fields[name]) return prev;

      const initialValue = initialValues[name] || '';
      const field: FormField = {
        name,
        value: initialValue,
        touched: false,
        rules,
      };

      return {
        ...prev,
        fields: { ...prev.fields, [name]: field },
      };
    });
  }, [initialValues]);

  const unregisterField = useCallback((name: string) => {
    setState(prev => {
      const { [name]: removed, ...remainingFields } = prev.fields;
      const { [name]: removedError, ...remainingErrors } = prev.errors;
      
      return {
        ...prev,
        fields: remainingFields,
        errors: remainingErrors,
        isValid: Object.keys(remainingErrors).length === 0,
      };
    });
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    // Validate all fields before submission
    const validatedFields = { ...state.fields };
    const errors: Record<string, string> = {};
    
    Object.entries(validatedFields).forEach(([name, field]) => {
      const error = validateFieldValue(field.value, field.rules);
      if (error) {
        errors[name] = error;
        validatedFields[name] = { ...field, error, touched: true };
      }
    });

    setState(prev => ({
      ...prev,
      fields: validatedFields,
      errors,
      isValid: Object.keys(errors).length === 0,
      isSubmitting: Object.keys(errors).length === 0,
    }));

    if (Object.keys(errors).length === 0) {
      try {
        const formData = Object.fromEntries(
          Object.entries(state.fields).map(([name, field]) => [name, field.value])
        );
        
        await onSubmit(formData);
      } catch (error) {
        console.error('Form submission error:', error);
      } finally {
        setState(prev => ({ ...prev, isSubmitting: false }));
      }
    }
  };

  const contextValue: FormContextValue = {
    state,
    updateField,
    validateField,
    setFieldTouched,
    registerField,
    unregisterField,
  };

  return (
    <FormContext.Provider value={contextValue}>
      <form
        onSubmit={handleSubmit}
        className={`space-y-6 ${className}`}
        data-testid={testId}
        noValidate
        {...props}
      >
        {children}
      </form>
    </FormContext.Provider>
  );
};

// Form field wrapper component
export const FormField: React.FC<FormFieldProps> = ({
  name,
  label,
  rules,
  children,
  className = '',
  testId = `form-field-${name}`,
}) => {
  const { state, updateField, validateField, setFieldTouched, registerField, unregisterField } = useFormContext();

  React.useEffect(() => {
    registerField(name, rules);
    return () => unregisterField(name);
  }, [name, rules, registerField, unregisterField]);

  const field = state.fields[name];
  const hasError = field?.error && field?.touched;

  // Clone the child element and add form-related props
  const childElement = React.cloneElement(children, {
    value: field?.value || '',
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      updateField(name, e.target.value);
    },
    onBlur: () => {
      setFieldTouched(name);
      if (validationMode === 'onBlur') {
        validateField(name);
      }
    },
    'aria-invalid': hasError,
    'aria-describedby': hasError ? `${name}-error` : undefined,
    id: name,
  });

  return (
    <div className={`form-field ${className}`} data-testid={testId}>
      {label && (
        <label
          htmlFor={name}
          className="block text-sm font-medium text-neutral-700 mb-2"
        >
          {label}
          {rules?.required && (
            <span className="text-error-600 ml-1" aria-label="wymagane">*</span>
          )}
        </label>
      )}
      
      {childElement}
      
      {hasError && (
        <p
          id={`${name}-error`}
          className="mt-2 text-sm text-error-600"
          role="alert"
          aria-live="polite"
        >
          {field.error}
        </p>
      )}
    </div>
  );
};