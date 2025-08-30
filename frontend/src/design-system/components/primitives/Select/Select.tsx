// Select Component
import React, { forwardRef, useState, useRef, useEffect, useId } from 'react';
import { clsx } from 'clsx';
import { BaseComponentProps, SizeVariant } from '../../../types';
import { ariaUtils, keyboardUtils } from '../../../utils/accessibility';

// Select option interface
export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

// Select-specific props
export interface SelectProps extends BaseComponentProps {
  /** Select value */
  value?: string | string[];
  /** Default value for uncontrolled select */
  defaultValue?: string | string[];
  /** Placeholder text */
  placeholder?: string;
  /** Whether select is disabled */
  disabled?: boolean;
  /** Whether select is required */
  required?: boolean;
  /** Whether multiple selection is allowed */
  multiple?: boolean;
  /** Select size */
  size?: SizeVariant;
  /** Error state */
  error?: boolean;
  /** Error message */
  errorMessage?: string;
  /** Helper text */
  helperText?: string;
  /** Label text */
  label?: string;
  /** Options */
  options: SelectOption[];
  /** Change handler */
  onChange?: (value: string | string[]) => void;
  /** Focus handler */
  onFocus?: (event: React.FocusEvent<HTMLButtonElement>) => void;
  /** Blur handler */
  onBlur?: (event: React.FocusEvent<HTMLButtonElement>) => void;
  /** Search functionality */
  searchable?: boolean;
  /** Clear functionality */
  clearable?: boolean;
  /** Name attribute */
  name?: string;
  /** ARIA label for accessibility */
  'aria-label'?: string;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
  /** ARIA invalid for accessibility */
  'aria-invalid'?: boolean;
}

// Select component
export const Select = forwardRef<HTMLButtonElement, SelectProps>(
  (
    {
      value,
      defaultValue,
      placeholder = 'Wybierz opcję',
      disabled = false,
      required = false,
      multiple = false,
      size = 'md',
      error = false,
      errorMessage,
      helperText,
      label,
      options = [],
      onChange,
      onFocus,
      onBlur,
      searchable = false,
      clearable = false,
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
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [focusedIndex, setFocusedIndex] = useState(-1);
    const [internalValue, setInternalValue] = useState<string | string[]>(
      value ?? defaultValue ?? (multiple ? [] : '')
    );

    const selectId = useId();
    const errorId = useId();
    const helperId = useId();
    const listboxId = useId();
    
    const containerRef = useRef<HTMLDivElement>(null);
    const searchInputRef = useRef<HTMLInputElement>(null);
    const listboxRef = useRef<HTMLUListElement>(null);

    // Update internal value when controlled value changes
    useEffect(() => {
      if (value !== undefined) {
        setInternalValue(value);
      }
    }, [value]);

    // Filter options based on search term
    const filteredOptions = searchable && searchTerm
      ? options.filter(option => 
          option.label.toLowerCase().includes(searchTerm.toLowerCase())
        )
      : options;

    // Get selected option(s) for display
    const getSelectedDisplay = () => {
      if (multiple && Array.isArray(internalValue)) {
        if (internalValue.length === 0) return placeholder;
        if (internalValue.length === 1) {
          const option = options.find(opt => opt.value === internalValue[0]);
          return option?.label || internalValue[0];
        }
        return `${internalValue.length} opcji wybranych`;
      } else {
        const option = options.find(opt => opt.value === internalValue);
        return option?.label || placeholder;
      }
    };

    // Handle option selection
    const handleOptionSelect = (optionValue: string) => {
      let newValue: string | string[];

      if (multiple) {
        const currentArray = Array.isArray(internalValue) ? internalValue : [];
        if (currentArray.includes(optionValue)) {
          newValue = currentArray.filter(v => v !== optionValue);
        } else {
          newValue = [...currentArray, optionValue];
        }
      } else {
        newValue = optionValue;
        setIsOpen(false);
      }

      if (value === undefined) {
        setInternalValue(newValue);
      }
      onChange?.(newValue);
    };

    // Handle clear selection
    const handleClear = (event: React.MouseEvent) => {
      event.stopPropagation();
      const newValue = multiple ? [] : '';
      if (value === undefined) {
        setInternalValue(newValue);
      }
      onChange?.(newValue);
    };

    // Handle toggle dropdown
    const handleToggle = () => {
      if (disabled) return;
      setIsOpen(!isOpen);
      setFocusedIndex(-1);
      if (!isOpen && searchable) {
        setSearchTerm('');
      }
    };

    // Handle focus events
    const handleFocus = (event: React.FocusEvent<HTMLButtonElement>) => {
      onFocus?.(event);
    };

    const handleBlur = (event: React.FocusEvent<HTMLButtonElement>) => {
      // Delay blur to allow for option selection
      setTimeout(() => {
        if (!containerRef.current?.contains(document.activeElement)) {
          setIsOpen(false);
          setSearchTerm('');
          setFocusedIndex(-1);
        }
      }, 150);
      onBlur?.(event);
    };

    // Handle keyboard navigation
    const handleKeyDown = (event: React.KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
          } else {
            setFocusedIndex(prev => 
              prev < filteredOptions.length - 1 ? prev + 1 : 0
            );
          }
          break;
        case 'ArrowUp':
          event.preventDefault();
          if (isOpen) {
            setFocusedIndex(prev => 
              prev > 0 ? prev - 1 : filteredOptions.length - 1
            );
          }
          break;
        case 'Enter':
        case ' ':
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
          } else if (focusedIndex >= 0) {
            handleOptionSelect(filteredOptions[focusedIndex].value);
          }
          break;
        case 'Escape':
          event.preventDefault();
          setIsOpen(false);
          setFocusedIndex(-1);
          break;
        case 'Tab':
          setIsOpen(false);
          break;
      }
    };

    // Handle search input change
    const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      setSearchTerm(event.target.value);
      setFocusedIndex(-1);
    };

    // Close dropdown when clicking outside
    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
          setIsOpen(false);
          setSearchTerm('');
          setFocusedIndex(-1);
        }
      };

      if (isOpen) {
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
      }
    }, [isOpen]);

    // Focus search input when dropdown opens
    useEffect(() => {
      if (isOpen && searchable && searchInputRef.current) {
        searchInputRef.current.focus();
      }
    }, [isOpen, searchable]);

    // Generate describedby IDs
    const describedByIds = [
      ariaDescribedBy,
      errorMessage ? errorId : null,
      helperText ? helperId : null,
    ].filter(Boolean).join(' ') || undefined;

    // Container classes
    const containerClasses = clsx(
      'ds-select-container',
      'relative',
      'w-full',
      {
        'opacity-60': disabled,
      }
    );

    // Trigger button classes
    const triggerClasses = clsx(
      'ds-select-trigger',
      'relative',
      'w-full',
      'flex',
      'items-center',
      'justify-between',
      'border',
      'rounded-md-md',
      'transition-all',
      'duration-200',
      'ease-out',
      'text-left',
      'cursor-pointer',
      
      // Size styles
      {
        'h-6 px-2 py-1 text-xs': size === 'xs',
        'h-8 px-3 py-1.5 text-sm': size === 'sm',
        'h-10 px-3 py-2 text-base': size === 'md',
        'h-12 px-4 py-2.5 text-lg': size === 'lg',
        'h-14 px-4 py-3 text-xl': size === 'xl',
      },
      
      // State styles
      {
        // Normal state
        'border-border-default bg-white text-text-primary': !error && !isOpen && !disabled,
        
        // Open state
        'border-border-focus bg-white text-text-primary ring-2 ring-primary-600/20': 
          isOpen && !error && !disabled,
        
        // Error state
        'border-border-error bg-error-50 text-text-primary ring-2 ring-error-600/20': 
          error && !disabled,
        
        // Disabled state
        'border-border-muted bg-background-disabled text-text-disabled cursor-not-allowed': 
          disabled,
      },
      
      // Hover styles (only when not disabled)
      {
        'hover:border-border-strong': !disabled && !isOpen && !error,
      }
    );

    // Dropdown classes
    const dropdownClasses = clsx(
      'ds-select-dropdown',
      'absolute',
      'z-50',
      'w-full',
      'mt-1',
      'bg-white',
      'border',
      'border-border-default',
      'rounded-md-md',
      'shadow-sm-lg',
      'max-h-60',
      'overflow-auto',
      'py-1'
    );

    // Option classes
    const getOptionClasses = (index: number, isSelected: boolean, isDisabled: boolean) => clsx(
      'ds-select-option',
      'relative',
      'flex',
      'items-center',
      'px-3',
      'py-2',
      'text-sm',
      'cursor-pointer',
      'transition-colors',
      'duration-150',
      {
        'bg-primary-50 text-primary-600': index === focusedIndex && !isDisabled,
        'bg-primary-100 text-primary-700': isSelected && !isDisabled,
        'text-text-disabled cursor-not-allowed': isDisabled,
        'text-text-primary hover:bg-background-secondary': !isSelected && !isDisabled && index !== focusedIndex,
      }
    );

    // Label classes
    const labelClasses = clsx(
      'ds-select-label',
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
      'ds-select-helper',
      'typography-form-helper',
      'mt-1',
      {
        'text-text-muted': !error,
        'text-error-600': error,
      }
    );

    // Check if option is selected
    const isOptionSelected = (optionValue: string) => {
      if (multiple && Array.isArray(internalValue)) {
        return internalValue.includes(optionValue);
      }
      return internalValue === optionValue;
    };

    // Check if there's a selection to clear
    const hasSelection = multiple 
      ? Array.isArray(internalValue) && internalValue.length > 0
      : internalValue !== '';

    return (
      <div ref={containerRef} className={clsx(containerClasses, className)}>
        {/* Label */}
        {label && (
          <label htmlFor={selectId} className={labelClasses}>
            {label}
            {required && (
              <span className="text-error-600 ml-1" aria-label="wymagane">
                *
              </span>
            )}
          </label>
        )}
        
        {/* Hidden input for form submission */}
        {name && (
          <input
            type="hidden"
            name={name}
            value={Array.isArray(internalValue) ? internalValue.join(',') : internalValue}
          />
        )}
        
        {/* Trigger button */}
        <button
          ref={ref}
          id={selectId}
          type="button"
          disabled={disabled}
          onClick={handleToggle}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          className={triggerClasses}
          data-testid={testId}
          aria-label={ariaLabel}
          aria-describedby={describedByIds}
          aria-invalid={ariaInvalid ?? error}
          aria-required={required}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          {...rest}
        >
          {/* Selected value display */}
          <span className={clsx(
            'block truncate',
            {
              'text-text-placeholder': !hasSelection,
            }
          )}>
            {getSelectedDisplay()}
          </span>
          
          {/* Icons */}
          <div className="flex items-center gap-1">
            {/* Clear button */}
            {clearable && hasSelection && !disabled && (
              <button
                type="button"
                onClick={handleClear}
                className="flex items-center justify-center w-4 h-4 text-text-muted hover:text-text-primary transition-colors"
                aria-label="Wyczyść wybór"
                tabIndex={-1}
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
            
            {/* Dropdown arrow */}
            <svg
              className={clsx(
                'w-4 h-4 text-text-muted transition-transform duration-200',
                {
                  'rotate-180': isOpen,
                }
              )}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </button>
        
        {/* Dropdown */}
        {isOpen && (
          <div className={dropdownClasses}>
            {/* Search input */}
            {searchable && (
              <div className="px-3 py-2 border-b border-border-muted">
                <input
                  ref={searchInputRef}
                  type="text"
                  value={searchTerm}
                  onChange={handleSearchChange}
                  placeholder="Szukaj..."
                  className="w-full px-2 py-1 text-sm border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-primary-600/20 focus:border-border-focus"
                />
              </div>
            )}
            
            {/* Options list */}
            <ul
              ref={listboxRef}
              id={listboxId}
              role="listbox"
              aria-multiselectable={multiple}
              aria-label={ariaLabel || label || 'Opcje'}
            >
              {filteredOptions.length === 0 ? (
                <li className="px-3 py-2 text-sm text-text-muted">
                  {searchTerm ? 'Brak wyników' : 'Brak opcji'}
                </li>
              ) : (
                filteredOptions.map((option, index) => {
                  const isSelected = isOptionSelected(option.value);
                  return (
                    <li
                      key={option.value}
                      role="option"
                      aria-selected={isSelected}
                      aria-disabled={option.disabled}
                      className={getOptionClasses(index, isSelected, option.disabled || false)}
                      onClick={() => !option.disabled && handleOptionSelect(option.value)}
                      onMouseEnter={() => setFocusedIndex(index)}
                    >
                      {/* Checkbox for multiple selection */}
                      {multiple && (
                        <div className="flex items-center mr-2">
                          <div className={clsx(
                            'w-4 h-4 border rounded-md flex items-center justify-center',
                            {
                              'border-primary-600 bg-primary-600': isSelected,
                              'border-border-default': !isSelected,
                            }
                          )}>
                            {isSelected && (
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {/* Option label */}
                      <span className="block truncate">{option.label}</span>
                      
                      {/* Selected indicator for single selection */}
                      {!multiple && isSelected && (
                        <svg className="w-4 h-4 ml-auto text-primary-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </li>
                  );
                })
              )}
            </ul>
          </div>
        )}
        
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

Select.displayName = 'Select';

export default Select;