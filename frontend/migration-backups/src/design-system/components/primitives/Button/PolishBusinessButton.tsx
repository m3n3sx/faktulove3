// Polish Business Button Variants
import React, { forwardRef } from 'react';
import { Button, ButtonProps } from './Button';
import { polishA11yUtils } from '../../utils/accessibility';

// Polish business button variants
export interface PolishBusinessButtonProps extends Omit<ButtonProps, 'variant'> {
  /** Polish business variant */
  variant?: 'invoice' | 'contractor' | 'payment' | 'export' | 'print' | 'cancel';
}

// Polish business button component
export const PolishBusinessButton = forwardRef<HTMLButtonElement, PolishBusinessButtonProps>(
  ({ variant = 'invoice', children, 'aria-label': ariaLabel, ...rest }, ref) => {
    // Map Polish business variants to base variants
    const getBaseVariant = (polishVariant: PolishBusinessButtonProps['variant']): ButtonProps['variant'] => {
      switch (polishVariant) {
        case 'invoice':
        case 'payment':
          return 'primary';
        case 'contractor':
        case 'export':
          return 'secondary';
        case 'print':
          return 'ghost';
        case 'cancel':
          return 'danger';
        default:
          return 'primary';
      }
    };

    // Get Polish aria label if not provided
    const getPolishAriaLabel = (polishVariant: PolishBusinessButtonProps['variant']): string => {
      const labels = {
        invoice: 'Utwórz fakturę',
        contractor: 'Zarządzaj kontrahentami',
        payment: 'Oznacz jako opłacone',
        export: 'Eksportuj dane',
        print: 'Drukuj dokument',
        cancel: 'Anuluj operację',
      };
      return labels[polishVariant || 'invoice'];
    };

    return (
      <Button
        ref={ref}
        variant={getBaseVariant(variant)}
        aria-label={ariaLabel || getPolishAriaLabel(variant)}
        {...rest}
      >
        {children}
      </Button>
    );
  }
);

PolishBusinessButton.displayName = 'PolishBusinessButton';

// Invoice action buttons
export interface InvoiceActionButtonProps extends Omit<ButtonProps, 'variant'> {
  action: 'create' | 'edit' | 'send' | 'pay' | 'cancel' | 'duplicate';
}

export const InvoiceActionButton = forwardRef<HTMLButtonElement, InvoiceActionButtonProps>(
  ({ action, children, 'aria-label': ariaLabel, ...rest }, ref) => {
    const getVariantAndLabel = (actionType: InvoiceActionButtonProps['action']) => {
      const config = {
        create: { variant: 'primary' as const, label: 'Utwórz nową fakturę', icon: '➕' },
        edit: { variant: 'secondary' as const, label: 'Edytuj fakturę', icon: '✏️' },
        send: { variant: 'primary' as const, label: 'Wyślij fakturę', icon: '📧' },
        pay: { variant: 'primary' as const, label: 'Oznacz jako opłacone', icon: '✅' },
        cancel: { variant: 'danger' as const, label: 'Anuluj fakturę', icon: '❌' },
        duplicate: { variant: 'ghost' as const, label: 'Duplikuj fakturę', icon: '📋' },
      };
      return config[actionType];
    };

    const { variant, label } = getVariantAndLabel(action);

    return (
      <Button
        ref={ref}
        variant={variant}
        aria-label={ariaLabel || label}
        {...rest}
      >
        {children}
      </Button>
    );
  }
);

InvoiceActionButton.displayName = 'InvoiceActionButton';

// VAT rate button
export interface VATRateButtonProps extends Omit<ButtonProps, 'variant' | 'children'> {
  rate: number; // 0.23, 0.08, 0.05, 0, -1 (exempt)
  selected?: boolean;
}

export const VATRateButton = forwardRef<HTMLButtonElement, VATRateButtonProps>(
  ({ rate, selected = false, 'aria-label': ariaLabel, ...rest }, ref) => {
    const getVATDisplay = (vatRate: number): string => {
      if (vatRate === -1) return 'zw.';
      if (vatRate === 0) return '0%';
      return `${Math.round(vatRate * 100)}%`;
    };

    const getVATAriaLabel = (vatRate: number): string => {
      if (vatRate === -1) return 'Stawka VAT zwolniona';
      if (vatRate === 0) return 'Stawka VAT zero procent';
      return `Stawka VAT ${Math.round(vatRate * 100)} procent`;
    };

    return (
      <Button
        ref={ref}
        variant={selected ? 'primary' : 'secondary'}
        size="sm"
        aria-label={ariaLabel || getVATAriaLabel(rate)}
        aria-pressed={selected}
        className="min-w-[3rem] font-mono"
        {...rest}
      >
        {getVATDisplay(rate)}
      </Button>
    );
  }
);

VATRateButton.displayName = 'VATRateButton';

// Status toggle button
export interface StatusToggleButtonProps extends Omit<ButtonProps, 'variant' | 'children'> {
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  onStatusChange?: (newStatus: StatusToggleButtonProps['status']) => void;
}

export const StatusToggleButton = forwardRef<HTMLButtonElement, StatusToggleButtonProps>(
  ({ status, onStatusChange, 'aria-label': ariaLabel, ...rest }, ref) => {
    const getStatusConfig = (currentStatus: StatusToggleButtonProps['status']) => {
      const configs = {
        draft: { 
          variant: 'ghost' as const, 
          label: 'Szkic', 
          ariaLabel: 'Status: Szkic - kliknij aby zmienić',
          nextStatus: 'sent' as const 
        },
        sent: { 
          variant: 'secondary' as const, 
          label: 'Wysłana', 
          ariaLabel: 'Status: Wysłana - kliknij aby oznaczyć jako opłacona',
          nextStatus: 'paid' as const 
        },
        paid: { 
          variant: 'primary' as const, 
          label: 'Opłacona', 
          ariaLabel: 'Status: Opłacona',
          nextStatus: 'paid' as const 
        },
        overdue: { 
          variant: 'danger' as const, 
          label: 'Przeterminowana', 
          ariaLabel: 'Status: Przeterminowana - kliknij aby oznaczyć jako opłacona',
          nextStatus: 'paid' as const 
        },
        cancelled: { 
          variant: 'ghost' as const, 
          label: 'Anulowana', 
          ariaLabel: 'Status: Anulowana',
          nextStatus: 'cancelled' as const 
        },
      };
      return configs[currentStatus];
    };

    const config = getStatusConfig(status);

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
      if (onStatusChange && config.nextStatus !== status) {
        onStatusChange(config.nextStatus);
      }
      rest.onClick?.(event);
    };

    return (
      <Button
        ref={ref}
        variant={config.variant}
        size="sm"
        onClick={handleClick}
        aria-label={ariaLabel || config.ariaLabel}
        className="typography-status-badge"
        {...rest}
      >
        {config.label}
      </Button>
    );
  }
);

StatusToggleButton.displayName = 'StatusToggleButton';

// Export all components
export default PolishBusinessButton;