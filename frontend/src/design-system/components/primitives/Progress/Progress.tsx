import React from 'react';
import { cn } from '../../../utils/cn';

export interface ProgressProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  label?: string;
  className?: string;
  testId?: string;
}

const VARIANT_CONFIG = {
  default: 'bg-primary-600',
  success: 'bg-success-600',
  warning: 'bg-warning-600',
  error: 'bg-error-600',
};

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  size = 'md',
  variant = 'default',
  showLabel = false,
  label,
  className,
  testId,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'h-1';
      case 'lg':
        return 'h-3';
      default:
        return 'h-2';
    }
  };

  const displayLabel = label || `${Math.round(percentage)}%`;

  return (
    <div className={cn('w-full', className)} data-testid={testId}>
      {showLabel && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-700">{displayLabel}</span>
          <span className="text-sm text-gray-500">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className={cn(
        'w-full bg-gray-200 rounded-full overflow-hidden',
        getSizeClasses()
      )}>
        <div
          className={cn(
            'h-full transition-all duration-300 ease-out rounded-full',
            VARIANT_CONFIG[variant]
          )}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
          aria-label={displayLabel}
        />
      </div>
    </div>
  );
};

Progress.displayName = 'Progress';