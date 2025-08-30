import React from 'react';
import { cn } from '../../../utils/cn';

export type BadgeVariant = 
  | 'default'
  | 'primary'
  | 'success'
  | 'warning'
  | 'error'
  | 'info';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  icon?: React.ReactNode;
  testId?: string;
}

const VARIANT_CONFIG: Record<BadgeVariant, string> = {
  default: 'bg-neutral-100 text-neutral-800 border-neutral-200',
  primary: 'bg-primary-100 text-primary-800 border-primary-200',
  success: 'bg-success-100 text-success-800 border-success-200',
  warning: 'bg-warning-100 text-warning-800 border-warning-200',
  error: 'bg-error-100 text-error-800 border-error-200',
  info: 'bg-blue-100 text-blue-800 border-blue-200',
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className,
  icon,
  testId,
}) => {
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-1 text-xs';
      case 'lg':
        return 'px-4 py-2 text-base';
      default:
        return 'px-3 py-1 text-sm';
    }
  };

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-md-full border',
        getSizeClasses(),
        VARIANT_CONFIG[variant],
        className
      )}
      data-testid={testId}
    >
      {icon && <span className="mr-1">{icon}</span>}
      {children}
    </span>
  );
};

Badge.displayName = 'Badge';