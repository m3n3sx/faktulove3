import React from 'react';
import { createCompatibilityWrapper, WrapperConfig } from '../ComponentWrapper';
import { Form as DesignSystemForm } from '../../components/patterns/Form/Form';

// Legacy form props
export interface LegacyFormProps {
  onSubmit?: (event: React.FormEvent<HTMLFormElement>) => void;
  className?: string;
  children?: React.ReactNode;
  // Legacy props
  inline?: boolean;
  horizontal?: boolean;
  validation?: 'client' | 'server' | 'both';
  autoComplete?: boolean;
  noValidate?: boolean;
}

// Legacy Form component (placeholder)
const LegacyForm: React.FC<LegacyFormProps> = (props) => {
  const { 
    inline, 
    horizontal, 
    validation, 
    autoComplete = true,
    className = '',
    ...rest 
  } = props;
  
  let classes = 'legacy-form ' + className;
  if (inline) classes += ' legacy-form--inline';
  if (horizontal) classes += ' legacy-form--horizontal';
  
  return (
    <form 
      className={classes} 
      autoComplete={autoComplete ? 'on' : 'off'}
      {...rest} 
    />
  );
};

// Configuration for Form migration
const formWrapperConfig: WrapperConfig = {
  migration: {
    status: 'in_progress',
    migrationVersion: '1.0.0',
    targetDate: '2025-02-15',
    notes: 'Migrating Form component to design system. Legacy layout props are mapped to new layout system.',
    showWarnings: process.env.NODE_ENV === 'development',
  },
  propMapping: {
    propMap: {
      inline: 'layout',
      horizontal: 'layout',
      validation: 'validationMode',
      autoComplete: 'autoComplete',
    },
    propTransforms: {
      inline: (value: boolean) => value ? 'inline' : undefined,
      horizontal: (value: boolean) => value ? 'horizontal' : undefined,
      autoComplete: (value: boolean) => value ? 'on' : 'off',
    },
    defaultProps: {
      layout: 'vertical',
      validationMode: 'client',
    },
    removedProps: ['inline', 'horizontal'],
  },
  customWrapper: (props: LegacyFormProps, NewComponent) => {
    const { 
      inline, 
      horizontal, 
      validation, 
      autoComplete = true,
      ...rest 
    } = props;
    
    // Determine layout based on legacy boolean props
    let layout = 'vertical';
    if (inline) layout = 'inline';
    else if (horizontal) layout = 'horizontal';
    
    const newProps = {
      ...rest,
      layout,
      validationMode: validation || 'client',
      autoComplete: autoComplete ? 'on' : 'off',
    };
    
    return React.createElement(NewComponent, newProps);
  },
};

// Create the wrapped Form component
export const Form = createCompatibilityWrapper(
  'Form',
  LegacyForm,
  DesignSystemForm,
  formWrapperConfig
);

// Export types for TypeScript support
export type FormProps = LegacyFormProps;