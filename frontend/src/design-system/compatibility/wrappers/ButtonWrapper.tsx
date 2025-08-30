import React from 'react';
import { createCompatibilityWrapper, WrapperConfig } from '../ComponentWrapper';
import { Button as DesignSystemButton } from '../../components/primitives/Button';

// Legacy button props (example of what might exist in the current app)
export interface LegacyButtonProps {
  type?: 'button' | 'submit' | 'reset';
  className?: string;
  disabled?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children?: React.ReactNode;
  // Legacy props that need mapping
  primary?: boolean;
  secondary?: boolean;
  danger?: boolean;
  small?: boolean;
  large?: boolean;
  loading?: boolean;
}

// Legacy Button component (placeholder - this would be the existing component)
const LegacyButton: React.FC<LegacyButtonProps> = (props) => {
  const { primary, secondary, danger, small, large, className = '', ...rest } = props;
  
  let classes = 'legacy-button ' + className;
  if (primary) classes += ' legacy-button--primary';
  if (secondary) classes += ' legacy-button--secondary';
  if (danger) classes += ' legacy-button--danger';
  if (small) classes += ' legacy-button--small';
  if (large) classes += ' legacy-button--large';
  
  return <button className={classes} {...rest} />;
};

// Configuration for Button migration
const buttonWrapperConfig: WrapperConfig = {
  migration: {
    status: 'in_progress',
    migrationVersion: '1.0.0',
    targetDate: '2025-02-15',
    notes: 'Migrating Button component to design system. Legacy variant props are mapped to new variant system.',
    showWarnings: process.env.NODE_ENV === 'development',
  },
  propMapping: {
    propMap: {
      // Map legacy props to new design system props
      primary: 'variant',
      secondary: 'variant',
      danger: 'variant',
      small: 'size',
      large: 'size',
      loading: 'isLoading',
    },
    propTransforms: {
      // Transform legacy boolean variants to string variants
      primary: (value: boolean) => value ? 'primary' : undefined,
      secondary: (value: boolean) => value ? 'secondary' : undefined,
      danger: (value: boolean) => value ? 'destructive' : undefined,
      small: (value: boolean) => value ? 'sm' : undefined,
      large: (value: boolean) => value ? 'lg' : undefined,
    },
    defaultProps: {
      variant: 'default',
      size: 'md',
    },
    removedProps: ['primary', 'secondary', 'danger', 'small', 'large'],
  },
  customWrapper: (props: LegacyButtonProps, NewComponent) => {
    // Custom logic to handle complex prop transformations
    const { primary, secondary, danger, small, large, loading, ...rest } = props;
    
    // Determine variant based on legacy boolean props
    let variant = 'default';
    if (primary) variant = 'primary';
    else if (secondary) variant = 'secondary';
    else if (danger) variant = 'destructive';
    
    // Determine size based on legacy boolean props
    let size = 'md';
    if (small) size = 'sm';
    else if (large) size = 'lg';
    
    const newProps = {
      ...rest,
      variant,
      size,
      isLoading: loading,
    };
    
    return React.createElement(NewComponent, newProps);
  },
};

// Create the wrapped Button component
export const Button = createCompatibilityWrapper(
  'Button',
  LegacyButton,
  DesignSystemButton,
  buttonWrapperConfig
);

// Export types for TypeScript support
export type ButtonProps = LegacyButtonProps;