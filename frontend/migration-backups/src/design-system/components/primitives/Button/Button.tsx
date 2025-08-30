// Button Component
import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import { BaseComponentProps, SizeVariant } from '../../types';
import { ariaUtils, keyboardUtils } from '../../utils/accessibility';

// Button-specific props
export interface ButtonProps extends BaseComponentProps {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  /** Button size */
  size?: SizeVariant;
  /** Whether button is disabled */
  disabled?: boolean;
  /** Whether button is in loading state */
  loading?: boolean;
  /** Button type */
  type?: 'button' | 'submit' | 'reset';
  /** Click handler */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  /** Whether button should take full width */
  fullWidth?: boolean;
  /** Icon to display before text */
  startIcon?: React.ReactNode;
  /** Icon to display after text */
  endIcon?: React.ReactNode;
  /** ARIA label for accessibility */
  'aria-label'?: string;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
  /** Whether button is pressed (for toggle buttons) */
  'aria-pressed'?: boolean;
  /** Whether button controls an expanded element */
  'aria-expanded'?: boolean;
  /** Whether button has a popup */
  'aria-haspopup'?: boolean | 'false' | 'true' | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog';
}

// Button component
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      type = 'button',
      onClick,
      fullWidth = false,
      startIcon,
      endIcon,
      children,
      className,
      testId,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
      'aria-pressed': ariaPressed,
      'aria-expanded': ariaExpanded,
      'aria-haspopup': ariaHasPopup,
      ...rest
    },
    ref
  ) => {
    // Handle click with loading state
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
      if (loading || disabled) {
        event.preventDefault();
        return;
      }
      onClick?.(event);
    };

    // Handle keyboard events
    const handleKeyDown = keyboardUtils.onEnterOrSpace(() => {
      if (!loading && !disabled && onClick) {
        const syntheticEvent = {
          preventDefault: () => {},
          currentTarget: ref?.current,
        } as React.MouseEvent<HTMLButtonElement>;
        onClick(syntheticEvent);
      }
    });

    // Generate CSS classes
    const buttonClasses = clsx(
      // Base button styles
      'ds-button',
      'inline-flex',
      'items-center',
      'justify-center',
      'font-medium',
      'transition-all',
      'duration-200',
      'ease-out',
      'focus-visible',
      'disabled:cursor-not-allowed',
      'disabled:opacity-60',
      
      // Variant styles
      {
        // Primary variant
        'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 focus:ring-primary-600': 
          variant === 'primary' && !disabled && !loading,
        'bg-primary-300 text-white': 
          variant === 'primary' && (disabled || loading),
        
        // Secondary variant
        'bg-white text-primary-600 border border-primary-600 hover:bg-primary-50 active:bg-primary-100 focus:ring-primary-600': 
          variant === 'secondary' && !disabled && !loading,
        'bg-gray-50 text-gray-400 border border-gray-300': 
          variant === 'secondary' && (disabled || loading),
        
        // Ghost variant
        'bg-transparent text-primary-600 hover:bg-primary-50 active:bg-primary-100 focus:ring-primary-600': 
          variant === 'ghost' && !disabled && !loading,
        'bg-transparent text-gray-400': 
          variant === 'ghost' && (disabled || loading),
        
        // Danger variant
        'bg-error-600 text-white hover:bg-error-700 active:bg-error-800 focus:ring-error-600': 
          variant === 'danger' && !disabled && !loading,
        'bg-error-300 text-white': 
          variant === 'danger' && (disabled || loading),
      },
      
      // Size styles
      {
        'px-2 py-1 text-xs h-6 min-w-[1.5rem] gap-1': size === 'xs',
        'px-3 py-1.5 text-sm h-8 min-w-[2rem] gap-1.5': size === 'sm',
        'px-4 py-2 text-base h-10 min-w-[2.5rem] gap-2': size === 'md',
        'px-5 py-2.5 text-lg h-12 min-w-[3rem] gap-2': size === 'lg',
        'px-6 py-3 text-xl h-14 min-w-[3.5rem] gap-2.5': size === 'xl',
      },
      
      // Border radius
      'rounded-md',
      
      // Full width
      {
        'w-full': fullWidth,
      },
      
      // Loading state
      {
        'cursor-wait': loading,
      },
      
      // Custom className
      className
    );

    // Loading spinner component
    const LoadingSpinner = () => (
      <svg
        className={clsx(
          'animate-spin',
          {
            'w-3 h-3': size === 'xs',
            'w-4 h-4': size === 'sm',
            'w-5 h-5': size === 'md',
            'w-6 h-6': size === 'lg',
            'w-7 h-7': size === 'xl',
          }
        )}
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    );

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className={buttonClasses}
        data-testid={testId}
        aria-label={ariaLabel}
        aria-describedby={ariaDescribedBy}
        aria-pressed={ariaPressed}
        aria-expanded={ariaExpanded}
        aria-haspopup={ariaHasPopup}
        aria-busy={loading}
        {...rest}
      >
        {/* Start icon or loading spinner */}
        {loading ? (
          <LoadingSpinner />
        ) : startIcon ? (
          <span className="flex-shrink-0" aria-hidden="true">
            {startIcon}
          </span>
        ) : null}
        
        {/* Button text */}
        {children && (
          <span className={clsx({ 'sr-only': loading && !children })}>
            {children}
          </span>
        )}
        
        {/* End icon */}
        {!loading && endIcon && (
          <span className="flex-shrink-0" aria-hidden="true">
            {endIcon}
          </span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;