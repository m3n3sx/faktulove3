import React from 'react';
import { createCompatibilityWrapper, WrapperConfig } from '../ComponentWrapper';
import { Input as DesignSystemInput } from '../../components/primitives/Input';

// Legacy input props
export interface LegacyInputProps {
  type?: string;
  value?: string;
  defaultValue?: string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  // Legacy props
  error?: boolean;
  errorMessage?: string;
  label?: string;
  helpText?: string;
  fullWidth?: boolean;
  size?: 'small' | 'medium' | 'large';
}

// Legacy Input component (placeholder)
const LegacyInput: React.FC<LegacyInputProps> = (props) => {
  const { 
    error, 
    errorMessage, 
    label, 
    helpText, 
    fullWidth, 
    size = 'medium',
    className = '',
    ...rest 
  } = props;
  
  let classes = 'legacy-input ' + className;
  if (error) classes += ' legacy-input--error';
  if (fullWidth) classes += ' legacy-input--full-width';
  classes += ` legacy-input--${size}`;
  
  return (
    <div className="legacy-input-wrapper">
      {label && <label className="legacy-input-label">{label}</label>}
      <input className={classes} {...rest} />
      {errorMessage && <span className="legacy-input-error">{errorMessage}</span>}
      {helpText && <span className="legacy-input-help">{helpText}</span>}
    </div>
  );
};

// Configuration for Input migration
const inputWrapperConfig: WrapperConfig = {
  migration: {
    status: 'in_progress',
    migrationVersion: '1.0.0',
    targetDate: '2025-02-15',
    notes: 'Migrating Input component to design system. Legacy error and size props are mapped to new system.',
    showWarnings: process.env.NODE_ENV === 'development',
  },
  propMapping: {
    propMap: {
      errorMessage: 'error',
      helpText: 'description',
      fullWidth: 'className',
    },
    propTransforms: {
      size: (value: 'small' | 'medium' | 'large') => {
        const sizeMap = { small: 'sm', medium: 'md', large: 'lg' };
        return sizeMap[value] || 'md';
      },
      fullWidth: (value: boolean) => value ? 'w-full' : undefined,
      error: (value: boolean) => value ? 'error' : undefined,
    },
    defaultProps: {
      size: 'md',
    },
    removedProps: ['fullWidth'],
  },
  customWrapper: (props: LegacyInputProps, NewComponent) => {
    const { 
      error, 
      errorMessage, 
      helpText, 
      fullWidth, 
      size = 'medium',
      className = '',
      ...rest 
    } = props;
    
    // Map legacy size to new size
    const sizeMap = { small: 'sm', medium: 'md', large: 'lg' };
    const newSize = sizeMap[size] || 'md';
    
    // Handle error state
    const variant = error ? 'error' : 'default';
    
    // Handle full width
    const newClassName = fullWidth ? `${className} w-full`.trim() : className;
    
    const newProps = {
      ...rest,
      size: newSize,
      variant,
      error: errorMessage,
      description: helpText,
      className: newClassName,
    };
    
    return React.createElement(NewComponent, newProps);
  },
};

// Create the wrapped Input component
export const Input = createCompatibilityWrapper(
  'Input',
  LegacyInput,
  DesignSystemInput,
  inputWrapperConfig
);

// Export types for TypeScript support
export type InputProps = LegacyInputProps;