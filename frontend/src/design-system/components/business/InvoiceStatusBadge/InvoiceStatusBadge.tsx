import React from 'react';
import { cn } from '../../../utils/cn';
import { useThemeUtils } from '../../../providers/ThemeProvider';

export type InvoiceStatus = 
  | 'draft'
  | 'sent'
  | 'viewed'
  | 'paid'
  | 'overdue'
  | 'cancelled'
  | 'corrected';

export interface InvoiceStatusBadgeProps {
  status: InvoiceStatus;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  testId?: string;
}

const STATUS_CONFIG: Record<InvoiceStatus, {
  label: string;
  baseClasses: string;
  themeColorVar: string;
}> = {
  draft: {
    label: 'Szkic',
    baseClasses: 'bg-background-muted text-text-secondary border-border-muted',
    themeColorVar: '--color-invoice-draft',
  },
  sent: {
    label: 'Wysłana',
    baseClasses: 'bg-primary-50 text-primary-800 border-primary-200',
    themeColorVar: '--color-invoice-sent',
  },
  viewed: {
    label: 'Wyświetlona',
    baseClasses: 'bg-info-50 text-info-800 border-info-200',
    themeColorVar: '--color-invoice-sent',
  },
  paid: {
    label: 'Opłacona',
    baseClasses: 'bg-success-50 text-success-800 border-success-200',
    themeColorVar: '--color-invoice-paid',
  },
  overdue: {
    label: 'Przeterminowana',
    baseClasses: 'bg-error-50 text-error-800 border-error-200',
    themeColorVar: '--color-invoice-overdue',
  },
  cancelled: {
    label: 'Anulowana',
    baseClasses: 'bg-background-muted text-text-muted border-border-muted',
    themeColorVar: '--color-invoice-cancelled',
  },
  corrected: {
    label: 'Skorygowana',
    baseClasses: 'bg-warning-50 text-warning-800 border-warning-200',
    themeColorVar: '--color-invoice-sent',
  },
};

export const InvoiceStatusBadge: React.FC<InvoiceStatusBadgeProps> = ({
  status,
  className,
  size = 'md',
  testId,
}) => {
  const config = STATUS_CONFIG[status];
  const { getInvoiceStatusColor, isDark } = useThemeUtils();
  
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

  const getStatusIcon = () => {
    switch (status) {
      case 'paid':
        return (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'overdue':
        return (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'sent':
        return (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
            <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
          </svg>
        );
      case 'viewed':
        return (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
            <path
              fillRule="evenodd"
              d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'cancelled':
        return (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'corrected':
        return (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full border transition-colors duration-200',
        getSizeClasses(),
        config.baseClasses,
        className
      )}
      style={{
        color: getInvoiceStatusColor(status as any),
        borderColor: getInvoiceStatusColor(status as any),
      }}
      data-testid={testId}
      data-status={status}
    >
      {getStatusIcon()}
      {config.label}
    </span>
  );
};

InvoiceStatusBadge.displayName = 'InvoiceStatusBadge';