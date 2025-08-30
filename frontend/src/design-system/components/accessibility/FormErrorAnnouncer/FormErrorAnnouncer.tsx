/**
 * Form Error Announcer Component
 * Provides accessible error announcements for Polish business forms
 */

import React, { useEffect, useRef } from 'react';
import { polishAriaLabels } from '../../../utils/ariaUtils';
import { useLiveRegion } from '../LiveRegion/LiveRegion';
import './FormErrorAnnouncer.css';

export interface FormError {
  field: string;
  message: string;
  type?: 'required' | 'invalid' | 'format' | 'business';
}

export interface FormErrorAnnouncerProps {
  /** Array of form errors */
  errors: FormError[];
  /** Whether to show visual error summary */
  showSummary?: boolean;
  /** Function called when error link is clicked */
  onErrorClick?: (fieldId: string) => void;
  /** Additional CSS class */
  className?: string;
  /** Custom error summary title */
  summaryTitle?: string;
}

export const FormErrorAnnouncer: React.FC<FormErrorAnnouncerProps> = ({
  errors,
  showSummary = true,
  onErrorClick,
  className = '',
  summaryTitle,
}) => {
  const { announceError, announcePolite } = useLiveRegion();
  const previousErrorCount = useRef(0);
  const summaryRef = useRef<HTMLDivElement>(null);

  // Announce errors when they change
  useEffect(() => {
    const currentErrorCount = errors.length;
    
    if (currentErrorCount > previousErrorCount.current) {
      // New errors added
      const newErrorCount = currentErrorCount - previousErrorCount.current;
      const message = newErrorCount === 1
        ? 'Znaleziono 1 nowy błąd w formularzu'
        : `Znaleziono ${newErrorCount} nowych błędów w formularzu`;
      
      announceError(message);
      
      // Focus error summary if it exists
      if (summaryRef.current) {
        summaryRef.current.focus();
      }
    } else if (currentErrorCount === 0 && previousErrorCount.current > 0) {
      // All errors cleared
      announcePolite('Wszystkie błędy zostały poprawione');
    }
    
    previousErrorCount.current = currentErrorCount;
  }, [errors, announceError, announcePolite]);

  const handleErrorClick = (event: React.MouseEvent<HTMLAnchorElement>, fieldId: string) => {
    event.preventDefault();
    
    if (onErrorClick) {
      onErrorClick(fieldId);
    } else {
      // Default behavior - focus the field
      const field = document.getElementById(fieldId);
      if (field) {
        field.focus();
        field.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  };

  const getErrorTypeLabel = (type?: string): string => {
    switch (type) {
      case 'required':
        return 'Pole wymagane';
      case 'invalid':
        return 'Nieprawidłowa wartość';
      case 'format':
        return 'Nieprawidłowy format';
      case 'business':
        return 'Błąd biznesowy';
      default:
        return 'Błąd';
    }
  };

  const getPolishErrorMessage = (error: FormError): string => {
    // Add Polish business-specific error context
    const typeLabel = getErrorTypeLabel(error.type);
    return `${typeLabel}: ${error.message}`;
  };

  if (errors.length === 0) {
    return null;
  }

  const title = summaryTitle || (errors.length === 1
    ? 'Znaleziono 1 błąd w formularzu:'
    : `Znaleziono ${errors.length} błędów w formularzu:`);

  return (
    <>
      {showSummary && (
        <div
          ref={summaryRef}
          className={`form-error-summary ${className}`}
          role="alert"
          aria-labelledby="error-summary-title"
          tabIndex={-1}
        >
          <h2 id="error-summary-title" className="error-summary-title">
            {title}
          </h2>
          
          <ul className="error-summary-list" role="list">
            {errors.map((error, index) => (
              <li key={`${error.field}-${index}`} className="error-summary-item">
                <a
                  href={`#${error.field}`}
                  className="error-summary-link"
                  onClick={(e) => handleErrorClick(e, error.field)}
                  aria-describedby={`error-type-${index}`}
                >
                  {error.message}
                </a>
                <span
                  id={`error-type-${index}`}
                  className="error-type-label sr-only"
                >
                  {getErrorTypeLabel(error.type)}
                </span>
              </li>
            ))}
          </ul>
          
          <div className="error-summary-help">
            <p>
              Kliknij na błąd aby przejść do odpowiedniego pola lub użyj klawisza Tab
              aby poruszać się po formularzu.
            </p>
          </div>
        </div>
      )}
      
      {/* Individual field error announcements */}
      {errors.map((error, index) => (
        <div
          key={`announcement-${error.field}-${index}`}
          className="field-error-announcement sr-only"
          role="alert"
          aria-live="polite"
        >
          {getPolishErrorMessage(error)}
        </div>
      ))}
    </>
  );
};

/**
 * Polish Business Form Error Announcer
 * Pre-configured for Polish business form validation
 */
export const PolishBusinessFormErrorAnnouncer: React.FC<Omit<FormErrorAnnouncerProps, 'summaryTitle'>> = (props) => {
  const getBusinessErrorTitle = (errorCount: number): string => {
    if (errorCount === 1) {
      return 'Znaleziono błąd w danych biznesowych:';
    }
    return `Znaleziono ${errorCount} błędów w danych biznesowych:`;
  };

  return (
    <FormErrorAnnouncer
      {...props}
      summaryTitle={getBusinessErrorTitle(props.errors.length)}
      className={`polish-business-errors ${props.className || ''}`}
    />
  );
};

/**
 * Hook for managing form error announcements
 */
export const useFormErrorAnnouncer = () => {
  const { announceError, announceSuccess, announcePolite } = useLiveRegion();

  const announceFieldError = (fieldName: string, error: string) => {
    const message = `Błąd w polu ${fieldName}: ${error}`;
    announceError(message);
  };

  const announceFieldSuccess = (fieldName: string) => {
    const message = `Pole ${fieldName} zostało poprawnie wypełnione`;
    announcePolite(message);
  };

  const announceFormSubmission = () => {
    announcePolite('Formularz jest wysyłany...');
  };

  const announceFormSuccess = () => {
    announceSuccess('Formularz został pomyślnie wysłany');
  };

  const announceFormError = (errorCount: number) => {
    const message = errorCount === 1
      ? 'Formularz zawiera 1 błąd. Sprawdź powyżej.'
      : `Formularz zawiera ${errorCount} błędów. Sprawdź powyżej.`;
    announceError(message);
  };

  const announceValidationStart = () => {
    announcePolite('Sprawdzanie poprawności danych...');
  };

  const announceValidationComplete = (hasErrors: boolean) => {
    if (hasErrors) {
      announceError('Sprawdzanie zakończone. Znaleziono błędy.');
    } else {
      announceSuccess('Sprawdzanie zakończone. Wszystkie dane są poprawne.');
    }
  };

  // Polish business-specific announcements
  const announceNIPValidation = (isValid: boolean) => {
    if (isValid) {
      announceSuccess('Numer NIP jest prawidłowy');
    } else {
      announceError('Numer NIP jest nieprawidłowy');
    }
  };

  const announceCurrencyValidation = (isValid: boolean, currency: string = 'PLN') => {
    if (isValid) {
      announceSuccess(`Kwota w ${currency} jest prawidłowa`);
    } else {
      announceError(`Nieprawidłowa kwota w ${currency}`);
    }
  };

  const announceDateValidation = (isValid: boolean) => {
    if (isValid) {
      announceSuccess('Data jest prawidłowa');
    } else {
      announceError('Nieprawidłowa data. Użyj formatu DD.MM.YYYY');
    }
  };

  const announceVATValidation = (isValid: boolean) => {
    if (isValid) {
      announceSuccess('Stawka VAT została wybrana');
    } else {
      announceError('Wybierz stawkę VAT');
    }
  };

  return {
    announceFieldError,
    announceFieldSuccess,
    announceFormSubmission,
    announceFormSuccess,
    announceFormError,
    announceValidationStart,
    announceValidationComplete,
    announceNIPValidation,
    announceCurrencyValidation,
    announceDateValidation,
    announceVATValidation,
  };
};

export default FormErrorAnnouncer;