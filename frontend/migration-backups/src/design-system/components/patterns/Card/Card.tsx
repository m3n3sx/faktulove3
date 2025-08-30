import React from 'react';
import { BaseComponentProps, SizeVariant } from '../../../types';

// Card component props
export interface CardProps extends BaseComponentProps {
  variant?: 'default' | 'outlined' | 'elevated' | 'flat';
  size?: SizeVariant;
  padding?: SizeVariant | 'none';
  children: React.ReactNode;
}

export interface CardHeaderProps extends BaseComponentProps {
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export interface CardBodyProps extends BaseComponentProps {
  children: React.ReactNode;
}

export interface CardFooterProps extends BaseComponentProps {
  children: React.ReactNode;
  align?: 'left' | 'center' | 'right' | 'between';
}

// Card variant styles
const cardVariants = {
  default: 'bg-white border border-neutral-200 shadow-sm',
  outlined: 'bg-white border-2 border-neutral-300',
  elevated: 'bg-white border border-neutral-200 shadow-lg',
  flat: 'bg-neutral-50 border-0',
} as const;

// Card size styles
const cardSizes = {
  xs: 'max-w-xs',
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
} as const;

// Card padding styles
const cardPadding = {
  none: 'p-0',
  xs: 'p-2',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
  xl: 'p-10',
} as const;

// Main Card component
export const Card: React.FC<CardProps> = ({
  variant = 'default',
  size,
  padding = 'md',
  children,
  className = '',
  testId = 'card',
  ...props
}) => {
  const baseClasses = 'rounded-lg overflow-hidden';
  const variantClasses = cardVariants[variant];
  const sizeClasses = size ? cardSizes[size] : '';
  const paddingClasses = cardPadding[padding];

  return (
    <div
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${paddingClasses} ${className}`}
      data-testid={testId}
      role="article"
      {...props}
    >
      {children}
    </div>
  );
};

// Card Header component
export const CardHeader: React.FC<CardHeaderProps> = ({
  children,
  actions,
  className = '',
  testId = 'card-header',
  ...props
}) => {
  return (
    <div
      className={`flex items-center justify-between p-6 border-b border-neutral-200 ${className}`}
      data-testid={testId}
      {...props}
    >
      <div className="flex-1">
        {children}
      </div>
      {actions && (
        <div className="flex items-center gap-2 ml-4">
          {actions}
        </div>
      )}
    </div>
  );
};

// Card Body component
export const CardBody: React.FC<CardBodyProps> = ({
  children,
  className = '',
  testId = 'card-body',
  ...props
}) => {
  return (
    <div
      className={`p-6 ${className}`}
      data-testid={testId}
      {...props}
    >
      {children}
    </div>
  );
};

// Card Footer component
export const CardFooter: React.FC<CardFooterProps> = ({
  children,
  align = 'right',
  className = '',
  testId = 'card-footer',
  ...props
}) => {
  const alignmentClasses = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
    between: 'justify-between',
  };

  return (
    <div
      className={`flex items-center ${alignmentClasses[align]} p-6 border-t border-neutral-200 bg-neutral-50 ${className}`}
      data-testid={testId}
      {...props}
    >
      {children}
    </div>
  );
};

// Container component for responsive max-width layouts
export interface ContainerProps extends BaseComponentProps {
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  padding?: boolean;
  center?: boolean;
  children: React.ReactNode;
}

const containerSizes = {
  sm: 'max-w-screen-sm',   // 640px
  md: 'max-w-screen-md',   // 768px
  lg: 'max-w-screen-lg',   // 1024px
  xl: 'max-w-screen-xl',   // 1280px
  '2xl': 'max-w-screen-2xl', // 1536px
  full: 'max-w-full',
} as const;

export const Container: React.FC<ContainerProps> = ({
  size = 'lg',
  padding = true,
  center = true,
  children,
  className = '',
  testId = 'container',
  ...props
}) => {
  const sizeClasses = containerSizes[size];
  const paddingClasses = padding ? 'px-4 sm:px-6 lg:px-8' : '';
  const centerClasses = center ? 'mx-auto' : '';

  return (
    <div
      className={`${sizeClasses} ${paddingClasses} ${centerClasses} ${className}`}
      data-testid={testId}
      {...props}
    >
      {children}
    </div>
  );
};

// Compound Card component with subcomponents
Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;