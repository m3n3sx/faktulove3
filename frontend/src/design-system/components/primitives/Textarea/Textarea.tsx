// Textarea Component
import React, { forwardRef, useState, useId } from 'react';
import { clsx } from 'clsx';
import { BaseComponentProps, SizeVariant } from '../../../types';
import { ariaUtils, keyboardUtils } from '../../../utils/accessibility';

// Textarea-specific props
export interface TextareaProps extends BaseComponentProps, Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'size' | 'className' | 'children'> {
  /** Textarea size */
  size?: SizeVariant;
  /** Additional CSS classes */
  className?: string;
  /** Test ID for testing */
  testId?: string;
  /** Error state */
  error?: boolean;
  /** Error message */
  errorMessage?: string;
  /** Helper text */
  helperText?: string;
  /** Label text */
  label?: string;
  /** Resize behavior */
  resize?: 'none' | 'both' | 'horizontal' | 'vertical';

  /** ARIA label for accessibility */
  'aria-label'?: string;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
  /** ARIA invalid for accessibility */
  'aria-invalid'?: boolean;
}

// Textarea component
export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
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
      resize = 'vertical',
      onChange,
      onFocus,
      onBlur,
      rows = 3,
      cols,
      maxLength,
      minLength,
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
    const textareaId = useId();
    const errorId = useId();
    const helperId = useId();

    // Handle focus events
    const handleFocus = (event: React.FocusEvent<HTMLTextAreaElement>) => {
      setFocused(true);
      onFocus?.(event);
    };

    const handleBlur = (event: React.FocusEvent<HTMLTextAreaElement>) => {
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
      'ds-textarea-container',
      'relative',
      'w-full',
      {
        'opacity-60': disabled,
      }
    );

    // Textarea wrapper classes
    const wrapperClasses = clsx(
      'ds-textarea-wrapper',
      'relative',
      'flex',
      'transition-all',
      'duration-200',
      'ease-out',
      'border',
      'rounded-md-md',
      
      // Size styles
      {
        'min-h-[2rem]': size === 'xs',
        'min-h-[2.5rem]': size === 'sm',
        'min-h-[3rem]': size === 'md',
        'min-h-[3.5rem]': size === 'lg',
        'min-h-[4rem]': size === 'xl',
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

    // Textarea classes
    const textareaClasses = clsx(
      'ds-textarea',
      'flex-1',
      'bg-transparent',
      'border-0',
      'outline-none',
      'placeholder-text-placeholder',
      'w-full',
      
      // Size-specific padding and font
      {
        'px-2 py-1 text-xs': size === 'xs',
        'px-3 py-1.5 text-sm': size === 'sm',
        'px-3 py-2 text-base': size === 'md',
        'px-4 py-2.5 text-lg': size === 'lg',
        'px-4 py-3 text-xl': size === 'xl',
      },
      
      // Resize behavior
      {
        'resize-none': resize === 'none',
        'resize': resize === 'both',
        'resize-x': resize === 'horizontal',
        'resize-y': resize === 'vertical',
      },
      
      // Disabled styles
      {
        'cursor-not-allowed': disabled,
        'cursor-default': readOnly,
      }
    );

    // Label classes
    const labelClasses = clsx(
      'ds-textarea-label',
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
      'ds-textarea-helper',
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
          <label htmlFor={textareaId} className={labelClasses}>
            {label}
            {required && (
              <span className="text-error-600 ml-1" aria-label="wymagane">
                *
              </span>
            )}
          </label>
        )}
        
        {/* Textarea wrapper */}
        <div className={wrapperClasses}>
          {/* Textarea element */}
          <textarea
            ref={ref}
            id={textareaId}
            value={value}
            defaultValue={defaultValue}
            placeholder={placeholder}
            disabled={disabled}
            required={required}
            readOnly={readOnly}
            onChange={onChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            rows={rows}
            cols={cols}
            maxLength={maxLength}
            minLength={minLength}
            name={name}
            className={textareaClasses}
            data-testid={testId}
            aria-label={ariaLabel}
            aria-describedby={describedByIds}
            aria-invalid={ariaInvalid ?? error}
            aria-required={required}
            {...rest}
          />
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

Textarea.displayName = 'Textarea';

export default Textarea;