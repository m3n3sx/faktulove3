// Radio Component
import React, { forwardRef, useId } from 'react';
import { clsx } from 'clsx';
import { BaseComponentProps, SizeVariant } from '../../../types';
import { ariaUtils, keyboardUtils } from '../../../utils/accessibility';

// Radio option interface
export interface RadioOption {
  value: string;
  label: string;
  disabled?: boolean;
  description?: string;
}

// Radio-specific props
export interface RadioProps extends BaseComponentProps {
  /** Whether radio is checked */
  checked?: boolean;
  /** Default checked state for uncontrolled radio */
  defaultChecked?: boolean;
  /** Whether radio is disabled */
  disabled?: boolean;
  /** Whether radio is required */
  required?: boolean;
  /** Radio size */
  size?: SizeVariant;
  /** Error state */
  error?: boolean;
  /** Label text */
  label?: string;
  /** Label position */
  labelPosition?: 'start' | 'end';
  /** Change handler */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
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

// RadioGroup-specific props
export interface RadioGroupProps extends BaseComponentProps {
  /** Selected value */
  value?: string;
  /** Default value for uncontrolled group */
  defaultValue?: string;
  /** Whether group is disabled */
  disabled?: boolean;
  /** Whether group is required */
  required?: boolean;
  /** Radio size */
  size?: SizeVariant;
  /** Error state */
  error?: boolean;
  /** Error message */
  errorMessage?: string;
  /** Helper text */
  helperText?: string;
  /** Group label */
  label?: string;
  /** Options */
  options: RadioOption[];
  /** Layout direction */
  direction?: 'horizontal' | 'vertical';
  /** Change handler */
  onChange?: (value: string, event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Name attribute */
  name?: string;
  /** ARIA label for accessibility */
  'aria-label'?: string;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
  /** ARIA invalid for accessibility */
  'aria-invalid'?: boolean;
}

// Radio component
export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  (
    {
      checked,
      defaultChecked,
      disabled = false,
      required = false,
      size = 'md',
      error = false,
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
    const radioId = useId();

    // Container classes
    const containerClasses = clsx(
      'ds-radio-container',
      'relative',
      {
        'opacity-60': disabled,
      }
    );

    // Wrapper classes (for label and radio alignment)
    const wrapperClasses = clsx(
      'ds-radio-wrapper',
      'flex',
      'items-start',
      'gap-2',
      {
        'flex-row-reverse justify-end': labelPosition === 'start',
        'flex-row': labelPosition === 'end',
      }
    );

    // Radio input classes
    const inputClasses = clsx(
      'ds-radio-input',
      'peer',
      'appearance-none',
      'border',
      'rounded-md-full',
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
        'border-border-default bg-white': !error && !disabled,
        
        // Checked state
        'border-primary-600 bg-white': checked && !error && !disabled,
        
        // Error state
        'border-border-error bg-error-50': error && !disabled,
        'border-error-600 bg-error-50': checked && error && !disabled,
        
        // Disabled state
        'border-border-muted bg-background-disabled cursor-not-allowed': disabled,
      },
      
      // Hover styles (only when not disabled)
      {
        'hover:border-border-strong': !disabled && !checked && !error,
        'hover:border-primary-700': !disabled && checked && !error,
        'hover:border-error-700': !disabled && checked && error,
      },
      
      // Focus styles
      'focus:ring-2 focus:ring-offset-2',
      {
        'focus:ring-primary-600/20': !error,
        'focus:ring-error-600/20': error,
      }
    );

    // Radio dot classes
    const dotClasses = clsx(
      'ds-radio-dot',
      'absolute',
      'inset-0',
      'flex',
      'items-center',
      'justify-center',
      'pointer-events-none',
      
      // Dot visibility
      {
        'opacity-0': !checked,
        'opacity-100': checked,
      }
    );

    // Dot inner circle classes
    const dotInnerClasses = clsx(
      'rounded-md-full',
      'transition-all',
      'duration-200',
      
      // Size styles
      {
        'w-1 h-1': size === 'xs',
        'w-1.5 h-1.5': size === 'sm',
        'w-2 h-2': size === 'md',
        'w-2.5 h-2.5': size === 'lg',
        'w-3 h-3': size === 'xl',
      },
      
      // Color styles
      {
        'bg-primary-600': !error && !disabled,
        'bg-error-600': error && !disabled,
        'bg-border-muted': disabled,
      }
    );

    // Label classes
    const labelClasses = clsx(
      'ds-radio-label',
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

    return (
      <div className={clsx(containerClasses, className)}>
        <div className={wrapperClasses}>
          {/* Radio input with custom styling */}
          <div className="relative">
            <input
              ref={ref}
              id={radioId}
              type="radio"
              checked={checked}
              defaultChecked={defaultChecked}
              disabled={disabled}
              required={required}
              onChange={onChange}
              onFocus={onFocus}
              onBlur={onBlur}
              name={name}
              value={value}
              className={inputClasses}
              data-testid={testId}
              aria-label={ariaLabel}
              aria-describedby={ariaDescribedBy}
              aria-invalid={ariaInvalid ?? error}
              aria-required={required}
              {...rest}
            />
            
            {/* Custom radio dot */}
            <div className={dotClasses}>
              <div className={dotInnerClasses} />
            </div>
          </div>
          
          {/* Label */}
          {label && (
            <label htmlFor={radioId} className={labelClasses}>
              {label}
              {required && (
                <span className="text-error-600 ml-1" aria-label="wymagane">
                  *
                </span>
              )}
            </label>
          )}
        </div>
      </div>
    );
  }
);

Radio.displayName = 'Radio';

// RadioGroup component
export const RadioGroup = forwardRef<HTMLFieldSetElement, RadioGroupProps>(
  (
    {
      value,
      defaultValue,
      disabled = false,
      required = false,
      size = 'md',
      error = false,
      errorMessage,
      helperText,
      label,
      options = [],
      direction = 'vertical',
      onChange,
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
    const groupId = useId();
    const errorId = useId();
    const helperId = useId();

    // Handle change events
    const handleChange = (optionValue: string, event: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(optionValue, event);
    };

    // Generate describedby IDs
    const describedByIds = [
      ariaDescribedBy,
      errorMessage ? errorId : null,
      helperText ? helperId : null,
    ].filter(Boolean).join(' ') || undefined;

    // Container classes
    const containerClasses = clsx(
      'ds-radio-group-container',
      'relative',
      {
        'opacity-60': disabled,
      }
    );

    // Fieldset classes
    const fieldsetClasses = clsx(
      'ds-radio-group-fieldset',
      'border-0',
      'p-0',
      'm-0',
      'min-w-0'
    );

    // Legend classes
    const legendClasses = clsx(
      'ds-radio-group-legend',
      'typography-form-label',
      'text-text-primary',
      'mb-2',
      'p-0',
      {
        'text-text-disabled': disabled,
        'text-error-600': error,
      }
    );

    // Options container classes
    const optionsClasses = clsx(
      'ds-radio-group-options',
      'flex',
      'gap-3',
      {
        'flex-col': direction === 'vertical',
        'flex-row flex-wrap': direction === 'horizontal',
      }
    );

    // Helper text classes
    const helperClasses = clsx(
      'ds-radio-group-helper',
      'typography-form-helper',
      'mt-2',
      {
        'text-text-muted': !error,
        'text-error-600': error,
      }
    );

    return (
      <div className={clsx(containerClasses, className)}>
        <fieldset
          ref={ref}
          className={fieldsetClasses}
          data-testid={testId}
          aria-describedby={describedByIds}
          aria-invalid={ariaInvalid ?? error}
          aria-required={required}
          {...rest}
        >
          {/* Group label */}
          {label && (
            <legend className={legendClasses}>
              {label}
              {required && (
                <span className="text-error-600 ml-1" aria-label="wymagane">
                  *
                </span>
              )}
            </legend>
          )}
          
          {/* Radio options */}
          <div className={optionsClasses} role="radiogroup" aria-label={ariaLabel || label}>
            {options.map((option) => (
              <div key={option.value} className="flex flex-col">
                <Radio
                  name={name}
                  value={option.value}
                  checked={value === option.value}
                  defaultChecked={defaultValue === option.value}
                  disabled={disabled || option.disabled}
                  required={required}
                  size={size}
                  error={error}
                  label={option.label}
                  onChange={(event) => handleChange(option.value, event)}
                />
                {/* Option description */}
                {option.description && (
                  <div className="ml-7 mt-1 typography-form-helper text-text-muted">
                    {option.description}
                  </div>
                )}
              </div>
            ))}
          </div>
        </fieldset>
        
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

RadioGroup.displayName = 'RadioGroup';

export default Radio;