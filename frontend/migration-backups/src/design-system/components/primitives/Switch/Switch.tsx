// Switch Component
import React, { forwardRef, useId } from 'react';
import { clsx } from 'clsx';
import { BaseComponentProps, SizeVariant } from '../../../types';
import { ariaUtils, keyboardUtils } from '../../../utils/accessibility';

// Switch-specific props
export interface SwitchProps extends BaseComponentProps {
  /** Whether switch is checked */
  checked?: boolean;
  /** Default checked state for uncontrolled switch */
  defaultChecked?: boolean;
  /** Whether switch is disabled */
  disabled?: boolean;
  /** Whether switch is required */
  required?: boolean;
  /** Switch size */
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
  /** Description text */
  description?: string;
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
  /** Icon to show when checked */
  checkedIcon?: React.ReactNode;
  /** Icon to show when unchecked */
  uncheckedIcon?: React.ReactNode;
  /** ARIA label for accessibility */
  'aria-label'?: string;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
  /** ARIA invalid for accessibility */
  'aria-invalid'?: boolean;
}

// Switch component
export const Switch = forwardRef<HTMLInputElement, SwitchProps>(
  (
    {
      checked,
      defaultChecked,
      disabled = false,
      required = false,
      size = 'md',
      error = false,
      errorMessage,
      helperText,
      label,
      labelPosition = 'end',
      description,
      onChange,
      onFocus,
      onBlur,
      name,
      value,
      checkedIcon,
      uncheckedIcon,
      className,
      testId,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
      'aria-invalid': ariaInvalid,
      ...rest
    },
    ref
  ) => {
    const switchId = useId();
    const errorId = useId();
    const helperId = useId();
    const descriptionId = useId();

    // Handle change events
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(event.target.checked, event);
    };

    // Handle keyboard events
    const handleKeyDown = keyboardUtils.onEnterOrSpace((event) => {
      if (!disabled) {
        const input = event.currentTarget as HTMLInputElement;
        input.click();
      }
    });

    // Generate describedby IDs
    const describedByIds = [
      ariaDescribedBy,
      description ? descriptionId : null,
      errorMessage ? errorId : null,
      helperText ? helperId : null,
    ].filter(Boolean).join(' ') || undefined;

    // Container classes
    const containerClasses = clsx(
      'ds-switch-container',
      'relative',
      {
        'opacity-60': disabled,
      }
    );

    // Wrapper classes (for label and switch alignment)
    const wrapperClasses = clsx(
      'ds-switch-wrapper',
      'flex',
      'items-start',
      'gap-3',
      {
        'flex-row-reverse justify-end': labelPosition === 'start',
        'flex-row': labelPosition === 'end',
      }
    );

    // Switch track classes
    const trackClasses = clsx(
      'ds-switch-track',
      'relative',
      'inline-flex',
      'border-2',
      'border-transparent',
      'rounded-full',
      'cursor-pointer',
      'transition-all',
      'duration-200',
      'ease-out',
      'focus-within:ring-2',
      'focus-within:ring-offset-2',
      'flex-shrink-0',
      
      // Size styles
      {
        'w-7 h-4': size === 'xs',
        'w-9 h-5': size === 'sm',
        'w-11 h-6': size === 'md',
        'w-14 h-7': size === 'lg',
        'w-16 h-8': size === 'xl',
      },
      
      // State styles
      {
        // Unchecked state
        'bg-border-muted': !checked && !error && !disabled,
        
        // Checked state
        'bg-primary-600': checked && !error && !disabled,
        
        // Error state
        'bg-error-200': !checked && error && !disabled,
        'bg-error-600': checked && error && !disabled,
        
        // Disabled state
        'bg-background-disabled cursor-not-allowed': disabled,
      },
      
      // Hover styles (only when not disabled)
      {
        'hover:bg-border-strong': !disabled && !checked && !error,
        'hover:bg-primary-700': !disabled && checked && !error,
        'hover:bg-error-700': !disabled && checked && error,
      },
      
      // Focus styles
      {
        'focus-within:ring-primary-600/20': !error,
        'focus-within:ring-error-600/20': error,
      }
    );

    // Switch thumb classes
    const thumbClasses = clsx(
      'ds-switch-thumb',
      'pointer-events-none',
      'inline-block',
      'rounded-full',
      'bg-white',
      'shadow-lg',
      'ring-0',
      'transition-all',
      'duration-200',
      'ease-out',
      'flex',
      'items-center',
      'justify-center',
      
      // Size styles
      {
        'w-3 h-3': size === 'xs',
        'w-4 h-4': size === 'sm',
        'w-5 h-5': size === 'md',
        'w-6 h-6': size === 'lg',
        'w-7 h-7': size === 'xl',
      },
      
      // Position styles
      {
        'translate-x-0': !checked,
        'translate-x-3': checked && size === 'xs',
        'translate-x-4': checked && size === 'sm',
        'translate-x-5': checked && size === 'md',
        'translate-x-7': checked && size === 'lg',
        'translate-x-9': checked && size === 'xl',
      }
    );

    // Hidden input classes
    const inputClasses = clsx(
      'ds-switch-input',
      'sr-only'
    );

    // Label classes
    const labelClasses = clsx(
      'ds-switch-label',
      'typography-form-label',
      'cursor-pointer',
      'select-none',
      {
        'text-text-disabled cursor-not-allowed': disabled,
        'text-error-600': error && !disabled,
        'text-text-primary': !error && !disabled,
      }
    );

    // Description classes
    const descriptionClasses = clsx(
      'ds-switch-description',
      'typography-form-helper',
      'mt-1',
      {
        'text-text-muted': !error && !disabled,
        'text-text-disabled': disabled,
        'text-error-600': error && !disabled,
      }
    );

    // Helper text classes
    const helperClasses = clsx(
      'ds-switch-helper',
      'typography-form-helper',
      'mt-1',
      {
        'text-text-muted': !error,
        'text-error-600': error,
      }
    );

    // Icon classes
    const iconClasses = clsx(
      'ds-switch-icon',
      {
        'text-xs': size === 'xs',
        'text-sm': size === 'sm',
        'text-base': size === 'md',
        'text-lg': size === 'lg',
        'text-xl': size === 'xl',
      }
    );

    return (
      <div className={clsx(containerClasses, className)}>
        <div className={wrapperClasses}>
          {/* Switch track and thumb */}
          <label htmlFor={switchId} className={trackClasses}>
            {/* Hidden input */}
            <input
              ref={ref}
              id={switchId}
              type="checkbox"
              role="switch"
              checked={checked}
              defaultChecked={defaultChecked}
              disabled={disabled}
              required={required}
              onChange={handleChange}
              onFocus={onFocus}
              onBlur={onBlur}
              onKeyDown={handleKeyDown}
              name={name}
              value={value}
              className={inputClasses}
              data-testid={testId}
              aria-label={ariaLabel}
              aria-describedby={describedByIds}
              aria-invalid={ariaInvalid ?? error}
              aria-required={required}
              aria-checked={checked}
              {...rest}
            />
            
            {/* Switch thumb */}
            <span className={thumbClasses}>
              {/* Icons */}
              {checked && checkedIcon && (
                <span className={iconClasses} aria-hidden="true">
                  {checkedIcon}
                </span>
              )}
              {!checked && uncheckedIcon && (
                <span className={iconClasses} aria-hidden="true">
                  {uncheckedIcon}
                </span>
              )}
            </span>
          </label>
          
          {/* Label and description */}
          {(label || description) && (
            <div className="flex flex-col">
              {label && (
                <label htmlFor={switchId} className={labelClasses}>
                  {label}
                  {required && (
                    <span className="text-error-600 ml-1" aria-label="wymagane">
                      *
                    </span>
                  )}
                </label>
              )}
              {description && (
                <div id={descriptionId} className={descriptionClasses}>
                  {description}
                </div>
              )}
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

Switch.displayName = 'Switch';

export default Switch;