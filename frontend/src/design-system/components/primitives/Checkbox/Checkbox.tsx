// Checkbox Component
import React, { forwardRef, useId, useEffect, useRef } from 'react';
import { clsx } from 'clsx';
import { BaseComponentProps, SizeVariant } from '../../../types';
import { ariaUtils, keyboardUtils } from '../../../utils/accessibility';

// Checkbox-specific props
export interface CheckboxProps extends BaseComponentProps {
  /** Whether checkbox is checked */
  checked?: boolean;
  /** Default checked state for uncontrolled checkbox */
  defaultChecked?: boolean;
  /** Whether checkbox is in indeterminate state */
  indeterminate?: boolean;
  /** Whether checkbox is disabled */
  disabled?: boolean;
  /** Whether checkbox is required */
  required?: boolean;
  /** Checkbox size */
  size?: SizeVariant;
  /** Error state */
  error?: boolean;
  /** Error message */
  errorMessage?: string;
  /** Helper text */
  helperText?: string;
  /** Label text */
  label?: string;
  /** Label position */
  labelPosition?: 'start' | 'end';
  /** Change handler */
  onChange?: (checked: boolean, event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Focus handler */
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  /** Blur handler */
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  /** Name attribute */
  name?: string;
  /** Value attribute */
  value?: string;
  /** ARIA label for accessibility */
  'aria-label'?: string;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
  /** ARIA invalid for accessibility */
  'aria-invalid'?: boolean;
}

// Checkbox component
export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  (
    {
      checked,
      defaultChecked,
      indeterminate = false,
      disabled = false,
      required = false,
      size = 'md',
      error = false,
      errorMessage,
      helperText,
      label,
      labelPosition = 'end',
      onChange,
      onFocus,
      onBlur,
      name,
      value,
      className,
      testId,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
      'aria-invalid': ariaInvalid,
      ...rest
    },
    ref
  ) => {
    const checkboxId = useId();
    const errorId = useId();
    const helperId = useId();
    const internalRef = useRef<HTMLInputElement>(null);
    const checkboxRef = ref || internalRef;

    // Set indeterminate state using useEffect
    useEffect(() => {
      if (checkboxRef && 'current' in checkboxRef && checkboxRef.current) {
        checkboxRef.current.indeterminate = indeterminate;
      }
    }, [indeterminate, checkboxRef]);

    // Handle change events
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(event.target.checked, event);
    };

    // Generate describedby IDs
    const describedByIds = [
      ariaDescribedBy,
      errorMessage ? errorId : null,
      helperText ? helperId : null,
    ].filter(Boolean).join(' ') || undefined;

    // Container classes
    const containerClasses = clsx(
      'ds-checkbox-container',
      'relative',
      {
        'opacity-60': disabled,
      }
    );

    // Wrapper classes (for label and checkbox alignment)
    const wrapperClasses = clsx(
      'ds-checkbox-wrapper',
      'flex',
      'items-start',
      'gap-2',
      {
        'flex-row-reverse justify-end': labelPosition === 'start',
        'flex-row': labelPosition === 'end',
      }
    );

    // Checkbox input classes
    const inputClasses = clsx(
      'ds-checkbox-input',
      'peer',
      'appearance-none',
      'border',
      'rounded-md',
      'transition-all',
      'duration-200',
      'ease-out',
      'cursor-pointer',
      'focus-visible',
      'flex-shrink-0',
      
      // Size styles
      {
        'w-3 h-3': size === 'xs',
        'w-4 h-4': size === 'sm',
        'w-5 h-5': size === 'md',
        'w-6 h-6': size === 'lg',
        'w-7 h-7': size === 'xl',
      },
      
      // State styles
      {
        // Normal state
        'border-border-default bg-white text-primary-600': !error && !disabled,
        
        // Checked state
        'border-primary-600 bg-primary-600': (checked || indeterminate) && !error && !disabled,
        
        // Error state
        'border-border-error bg-error-50': error && !disabled,
        'border-error-600 bg-error-600': (checked || indeterminate) && error && !disabled,
        
        // Disabled state
        'border-border-muted bg-background-disabled cursor-not-allowed': disabled,
        'border-border-muted bg-border-muted': (checked || indeterminate) && disabled,
      },
      
      // Hover styles (only when not disabled)
      {
        'hover:border-border-strong': !disabled && !checked && !indeterminate && !error,
        'hover:bg-primary-700': !disabled && (checked || indeterminate) && !error,
        'hover:bg-error-700': !disabled && (checked || indeterminate) && error,
      },
      
      // Focus styles
      'focus:ring-2 focus:ring-offset-2',
      {
        'focus:ring-primary-600/20': !error,
        'focus:ring-error-600/20': error,
      }
    );

    // Checkbox icon classes
    const iconClasses = clsx(
      'ds-checkbox-icon',
      'absolute',
      'inset-0',
      'flex',
      'items-center',
      'justify-center',
      'pointer-events-none',
      'text-white',
      
      // Size-specific icon sizing
      {
        'text-xs': size === 'xs',
        'text-sm': size === 'sm',
        'text-base': size === 'md',
        'text-lg': size === 'lg',
        'text-xl': size === 'xl',
      }
    );

    // Label classes
    const labelClasses = clsx(
      'ds-checkbox-label',
      'typography-form-label',
      'cursor-pointer',
      'select-none',
      'leading-tight',
      {
        'text-text-disabled cursor-not-allowed': disabled,
        'text-error-600': error && !disabled,
        'text-text-primary': !error && !disabled,
      }
    );

    // Helper text classes
    const helperClasses = clsx(
      'ds-checkbox-helper',
      'typography-form-helper',
      'mt-1',
      {
        'text-text-muted': !error,
        'text-error-600': error,
      }
    );

    // Check icon SVG
    const CheckIcon = () => (
      <svg
        className="w-full h-full"
        fill="currentColor"
        viewBox="0 0 20 20"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
          clipRule="evenodd"
        />
      </svg>
    );

    // Indeterminate icon SVG
    const IndeterminateIcon = () => (
      <svg
        className="w-full h-full"
        fill="currentColor"
        viewBox="0 0 20 20"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
          clipRule="evenodd"
        />
      </svg>
    );

    return (
      <div className={clsx(containerClasses, className)}>
        <div className={wrapperClasses}>
          {/* Checkbox input with custom styling */}
          <div className="relative">
            <input
              ref={checkboxRef}
              id={checkboxId}
              type="checkbox"
              checked={checked}
              defaultChecked={defaultChecked}
              disabled={disabled}
              required={required}
              onChange={handleChange}
              onFocus={onFocus}
              onBlur={onBlur}
              name={name}
              value={value}
              className={inputClasses}
              data-testid={testId}
              aria-label={ariaLabel}
              aria-describedby={describedByIds}
              aria-invalid={ariaInvalid ?? error}
              aria-required={required}
              {...rest}
            />
            
            {/* Custom checkbox icon */}
            <div className={iconClasses}>
              {indeterminate ? (
                <IndeterminateIcon />
              ) : checked ? (
                <CheckIcon />
              ) : null}
            </div>
          </div>
          
          {/* Label */}
          {label && (
            <label htmlFor={checkboxId} className={labelClasses}>
              {label}
              {required && (
                <span className="text-error-600 ml-1" aria-label="wymagane">
                  *
                </span>
              )}
            </label>
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

Checkbox.displayName = 'Checkbox';

export default Checkbox;