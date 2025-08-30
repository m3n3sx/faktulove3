/**
 * ARIA Label Components
 * Provides comprehensive ARIA labeling for Polish business applications
 */

import React from 'react';
import { polishAriaLabels, ariaUtils } from '../../../utils/ariaUtils';

export interface AriaLabelProps {
  /** The element ID to label */
  htmlFor?: string;
  /** The label text */
  children: React.ReactNode;
  /** Whether the field is required */
  required?: boolean;
  /** Additional description */
  description?: string;
  /** Error message */
  error?: string;
  /** Help text */
  help?: string;
  /** Additional CSS class */
  className?: string;
}

/**
 * Enhanced label component with ARIA support
 */
export const AriaLabel: React.FC<AriaLabelProps> = ({
  htmlFor,
  children,
  required = false,
  description,
  error,
  help,
  className = '',
}) => {
  const labelId = ariaUtils.generateId('label');
  const descriptionId = description ? ariaUtils.generateId('desc') : undefined;
  const errorId = error ? ariaUtils.generateId('error') : undefined;
  const helpId = help ? ariaUtils.generateId('help') : undefined;

  return (
    <div className={`aria-label-container ${className}`}>
      <label
        id={labelId}
        htmlFor={htmlFor}
        className={`aria-label ${required ? 'required' : ''} ${error ? 'error' : ''}`}
      >
        {children}
        {required && (
          <span className="required-indicator" aria-label={polishAriaLabels.REQUIRED_FIELD}>
            *
          </span>
        )}
      </label>
      
      {description && (
        <div id={descriptionId} className="aria-description">
          {description}
        </div>
      )}
      
      {help && (
        <div id={helpId} className="aria-help">
          {help}
        </div>
      )}
      
      {error && (
        <div
          id={errorId}
          className="aria-error"
          role="alert"
          aria-live="polite"
        >
          <span className="sr-only">{polishAriaLabels.ERROR_MESSAGE}: </span>
          {error}
        </div>
      )}
    </div>
  );
};

/**
 * Polish NIP input label
 */
export const NIPLabel: React.FC<Omit<AriaLabelProps, 'children'> & { label?: string }> = ({
  label = polishAriaLabels.NIP_INPUT,
  ...props
}) => (
  <AriaLabel
    {...props}
    description={props.description || 'Format: 1234567890 (10 cyfr)'}
  >
    {label}
  </AriaLabel>
);

/**
 * Polish currency input label
 */
export const CurrencyLabel: React.FC<Omit<AriaLabelProps, 'children'> & { 
  label?: string;
  currency?: string;
}> = ({
  label = polishAriaLabels.CURRENCY_INPUT,
  currency = 'PLN',
  ...props
}) => (
  <AriaLabel
    {...props}
    description={props.description || `Kwota w ${currency}. Format: 1234.56`}
  >
    {label}
  </AriaLabel>
);

/**
 * Polish date input label
 */
export const DateLabel: React.FC<Omit<AriaLabelProps, 'children'> & { label?: string }> = ({
  label = polishAriaLabels.DATE_INPUT,
  ...props
}) => (
  <AriaLabel
    {...props}
    description={props.description || polishAriaLabels.DATE_FORMAT}
  >
    {label}
  </AriaLabel>
);

/**
 * VAT rate selector label
 */
export const VATLabel: React.FC<Omit<AriaLabelProps, 'children'> & { label?: string }> = ({
  label = polishAriaLabels.VAT_RATE,
  ...props
}) => (
  <AriaLabel
    {...props}
    description={props.description || 'Wybierz stawkę VAT dla faktury'}
  >
    {label}
  </AriaLabel>
);

/**
 * Invoice number label
 */
export const InvoiceNumberLabel: React.FC<Omit<AriaLabelProps, 'children'> & { label?: string }> = ({
  label = polishAriaLabels.INVOICE_NUMBER,
  ...props
}) => (
  <AriaLabel
    {...props}
    description={props.description || 'Format: FV/YYYY/NNN'}
  >
    {label}
  </AriaLabel>
);

/**
 * Screen reader only text component
 */
export const ScreenReaderOnly: React.FC<{
  children: React.ReactNode;
  as?: React.ElementType;
  className?: string;
}> = ({ children, as: Component = 'span', className = '' }) => (
  <Component className={`sr-only ${className}`}>
    {children}
  </Component>
);

/**
 * Visually hidden but accessible text
 */
export const VisuallyHidden: React.FC<{
  children: React.ReactNode;
  focusable?: boolean;
  className?: string;
}> = ({ children, focusable = false, className = '' }) => (
  <span 
    className={`visually-hidden ${focusable ? 'focusable' : ''} ${className}`}
    tabIndex={focusable ? 0 : undefined}
  >
    {children}
  </span>
);

/**
 * ARIA description component
 */
export const AriaDescription: React.FC<{
  id?: string;
  children: React.ReactNode;
  className?: string;
}> = ({ id, children, className = '' }) => (
  <div
    id={id}
    className={`aria-description ${className}`}
    role="note"
  >
    {children}
  </div>
);

/**
 * ARIA error message component
 */
export const AriaErrorMessage: React.FC<{
  id?: string;
  children: React.ReactNode;
  className?: string;
}> = ({ id, children, className = '' }) => (
  <div
    id={id}
    className={`aria-error-message ${className}`}
    role="alert"
    aria-live="polite"
  >
    <ScreenReaderOnly>{polishAriaLabels.ERROR_MESSAGE}: </ScreenReaderOnly>
    {children}
  </div>
);

/**
 * Loading announcement component
 */
export const LoadingAnnouncement: React.FC<{
  message?: string;
  className?: string;
}> = ({ message = polishAriaLabels.LOADING, className = '' }) => (
  <div
    className={`loading-announcement ${className}`}
    role="status"
    aria-live="polite"
    aria-label={message}
  >
    <ScreenReaderOnly>{message}</ScreenReaderOnly>
    <div className="loading-spinner" aria-hidden="true">
      <div className="spinner"></div>
    </div>
  </div>
);

/**
 * Success announcement component
 */
export const SuccessAnnouncement: React.FC<{
  message: string;
  className?: string;
}> = ({ message, className = '' }) => (
  <div
    className={`success-announcement ${className}`}
    role="status"
    aria-live="polite"
  >
    <ScreenReaderOnly>{polishAriaLabels.SUCCESS}: </ScreenReaderOnly>
    {message}
  </div>
);

/**
 * Progress announcement component
 */
export const ProgressAnnouncement: React.FC<{
  current: number;
  total: number;
  label?: string;
  className?: string;
}> = ({ current, total, label = 'Postęp', className = '' }) => {
  const percentage = Math.round((current / total) * 100);
  const announcement = `${label}: ${current} z ${total}, ${percentage}%`;
  
  return (
    <div
      className={`progress-announcement ${className}`}
      role="progressbar"
      aria-valuenow={current}
      aria-valuemin={0}
      aria-valuemax={total}
      aria-valuetext={announcement}
      aria-live="polite"
    >
      <ScreenReaderOnly>{announcement}</ScreenReaderOnly>
    </div>
  );
};

export default AriaLabel;