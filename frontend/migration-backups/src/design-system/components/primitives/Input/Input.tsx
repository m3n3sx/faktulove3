// Input Component
import React, { forwardRef, useState, useId } from 'react';
import { clsx } from 'clsx';
import { BaseComponentProps, SizeVariant } from '../../types';
import { ariaUtils, keyboardUtils } from '../../utils/accessibility';

// Input-specific props
export interface InputProps extends BaseComponentProps {
  /** Input type */
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search';
  /** Input value */
  value?: string;
  /** Default value for uncontrolled input */
  defaultValue?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Whether input is disabled */
  disabled?: boolean;
  /** Whether input is required */
  required?: boolean;
  /** Whether input is readonly */
  readOnly?: boolean;
  /** Input size */
  size?: SizeVariant;
  /** Error state */
  error?: boolean;
  /** Error message */
  errorMessage?: string;
  /** Helper text */
  helperText?: string;
  /** Label text */
  label?: string;
  /** Change handler */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Focus handler */
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  /** Blur handler */
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  /** Icon to display in input */
  icon?: React.ReactNode;
  /** Icon position */
  iconPosition?: 'start' | 'end';
  /** Maximum length */
  maxLength?: number;
  /** Minimum length */
  minLength?: number;
  /** Pattern for validation */
  pattern?: string;
  /** Autocomplete attribute */
  autoComplete?: string;
  /** Name attribute */
  name?: string;
  /** ARIA label for accessibility */
  'aria-label'?: string;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
  /** ARIA invalid for accessibility */
  'aria-invalid'?: boolean;
}

// Input component
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      type = 'text',
      value,
      defaultValue,
      placeholder,
      disabled = false,
      required = false,
      readOnly = false,
      size = 'md',
      error = false,
      errorMessage,
      helperText,
      label,
      onChange,
      onFocus,
      onBlur,
      icon,
      iconPosition = 'start',
      maxLength,
      minLength,
      pattern,
      autoComplete,
      name,
      className,
      testId,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
      'aria-invalid': ariaInvalid,
      ...rest
    },
    ref
  ) => {
    const [focused, setFocused] = useState(false);
    const inputId = useId();
    const errorId = useId();
    const helperId = useId();

    // Handle focus events
    const handleFocus = (event: React.FocusEvent<HTMLInputElement>) => {
      setFocused(true);
      onFocus?.(event);
    };

    const handleBlur = (event: React.FocusEvent<HTMLInputElement>) => {
      setFocused(false);
      onBlur?.(event);
    };

    // Generate describedby IDs
    const describedByIds = [
      ariaDescribedBy,
      errorMessage ? errorId : null,
      helperText ? helperId : null,
    ].filter(Boolean).join(' ') || undefined;

    // Container classes
    const containerClasses = clsx(
      'ds-input-container',
      'relative',
      'w-full',
      {
        'opacity-60': disabled,
      }
    );

    // Input wrapper classes
    const wrapperClasses = clsx(
      'ds-input-wrapper',
      'relative',
      'flex',
      'items-center',
      'border',
      'rounded-md',
      'transition-all',
      'duration-200',
      'ease-out',
      
      // Size styles
      {
        'h-6': size === 'xs',
        'h-8': size === 'sm',
        'h-10': size === 'md',
        'h-12': size === 'lg',
        'h-14': size === 'xl',
      },
      
      // State styles
      {
        // Normal state
        'border-border-default bg-white text-text-primary': !error && !focused && !disabled,
        
        // Focused state
        'border-border-focus bg-white text-text-primary ring-2 ring-primary-600/20': 
          focused && !error && !disabled,
        
        // Error state
        'border-border-error bg-error-50 text-text-primary ring-2 ring-error-600/20': 
          error && !disabled,
        
        // Disabled state
        'border-border-muted bg-background-disabled text-text-disabled cursor-not-allowed': 
          disabled,
        
        // Readonly state
        'bg-background-secondary': readOnly && !disabled,
      },
      
      // Hover styles (only when not disabled)
      {
        'hover:border-border-strong': !disabled && !focused && !error,
      }
    );

    // Input classes
    const inputClasses = clsx(
      'ds-input',
      'flex-1',
      'bg-transparent',
      'border-0',
      'outline-none',
      'placeholder-text-placeholder',
      
      // Size-specific padding and font
      {
        'px-2 py-1 text-xs': size === 'xs',
        'px-3 py-1.5 text-sm': size === 'sm',
        'px-3 py-2 text-base': size === 'md',
        'px-4 py-2.5 text-lg': size === 'lg',
        'px-4 py-3 text-xl': size === 'xl',
      },
      
      // Icon padding adjustments
      {
        'pl-8': icon && iconPosition === 'start' && size === 'xs',
        'pl-9': icon && iconPosition === 'start' && size === 'sm',
        'pl-10': icon && iconPosition === 'start' && size === 'md',
        'pl-12': icon && iconPosition === 'start' && size === 'lg',
        'pl-14': icon && iconPosition === 'start' && size === 'xl',
        
        'pr-8': icon && iconPosition === 'end' && size === 'xs',
        'pr-9': icon && iconPosition === 'end' && size === 'sm',
        'pr-10': icon && iconPosition === 'end' && size === 'md',
        'pr-12': icon && iconPosition === 'end' && size === 'lg',
        'pr-14': icon && iconPosition === 'end' && size === 'xl',
      },
      
      // Disabled styles
      {
        'cursor-not-allowed': disabled,
        'cursor-default': readOnly,
      }
    );

    // Icon classes
    const iconClasses = clsx(
      'ds-input-icon',
      'absolute',
      'flex',
      'items-center',
      'justify-center',
      'pointer-events-none',
      'text-text-muted',
      
      // Position
      {
        'left-0': iconPosition === 'start',
        'right-0': iconPosition === 'end',
      },
      
      // Size-specific positioning and sizing
      {
        'w-6 h-6 text-xs': size === 'xs',
        'w-8 h-8 text-sm': size === 'sm',
        'w-10 h-10 text-base': size === 'md',
        'w-12 h-12 text-lg': size === 'lg',
        'w-14 h-14 text-xl': size === 'xl',
      }
    );

    // Label classes
    const labelClasses = clsx(
      'ds-input-label',
      'block',
      'typography-form-label',
      'text-text-primary',
      'mb-1',
      {
        'text-text-disabled': disabled,
        'text-error-600': error,
      }
    );

    // Helper text classes
    const helperClasses = clsx(
      'ds-input-helper',
      'typography-form-helper',
      'mt-1',
      {
        'text-text-muted': !error,
        'text-error-600': error,
      }
    );

    return (
      <div className={clsx(containerClasses, className)}>
        {/* Label */}
        {label && (
          <label htmlFor={inputId} className={labelClasses}>
            {label}
            {required && (
              <span className="text-error-600 ml-1" aria-label="wymagane">
                *
              </span>
            )}
          </label>
        )}
        
        {/* Input wrapper */}
        <div className={wrapperClasses}>
          {/* Start icon */}
          {icon && iconPosition === 'start' && (
            <div className={iconClasses} aria-hidden="true">
              {icon}
            </div>
          )}
          
          {/* Input element */}
          <input
            ref={ref}
            id={inputId}
            type={type}
            value={value}
            defaultValue={defaultValue}
            placeholder={placeholder}
            disabled={disabled}
            required={required}
            readOnly={readOnly}
            onChange={onChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            maxLength={maxLength}
            minLength={minLength}
            pattern={pattern}
            autoComplete={autoComplete}
            name={name}
            className={inputClasses}
            data-testid={testId}
            aria-label={ariaLabel}
            aria-describedby={describedByIds}
            aria-invalid={ariaInvalid ?? error}
            aria-required={required}
            {...rest}
          />
          
          {/* End icon */}
          {icon && iconPosition === 'end' && (
            <div className={iconClasses} aria-hidden="true">
              {icon}
            </div>
          )}
        </div>
        
        {/* Helper text or error message */}
        {(helperText || errorMessage) && (
          <div
            id={errorMessage ? errorId : helperId}
            className={helperClasses}
            role={error ? 'alert' : undefined}
            aria-live={error ? 'polite' : undefined}
          >
            {errorMessage || helperText}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;