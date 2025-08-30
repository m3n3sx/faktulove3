import React from 'react';
import { Select } from '../../primitives/Select/Select';

export interface VATRate {
  value: number;
  label: string;
  description?: string;
}

export interface VATRateSelectorProps {
  value?: number;
  onChange?: (rate: number) => void;
  onBlur?: (event: React.FocusEvent<HTMLSelectElement>) => void;
  disabled?: boolean;
  error?: boolean;
  errorMessage?: string;
  className?: string;
  testId?: string;
  customRates?: VATRate[];
  includeExempt?: boolean;
}

const DEFAULT_POLISH_VAT_RATES: VATRate[] = [
  { value: 23, label: '23%', description: 'Standardowa stawka VAT' },
  { value: 8, label: '8%', description: 'Obniżona stawka VAT' },
  { value: 5, label: '5%', description: 'Obniżona stawka VAT' },
  { value: 0, label: '0%', description: 'Stawka zerowa VAT' },
];

const EXEMPT_RATES: VATRate[] = [
  { value: -1, label: 'zw.', description: 'Zwolnione z VAT' },
  { value: -2, label: 'np.', description: 'Nie podlega VAT' },
];

export const VATRateSelector: React.FC<VATRateSelectorProps> = ({
  value,
  onChange,
  onBlur,
  disabled = false,
  error = false,
  errorMessage,
  className,
  testId,
  customRates,
  includeExempt = true,
}) => {
  const rates = customRates || DEFAULT_POLISH_VAT_RATES;
  const allRates = includeExempt ? [...rates, ...EXEMPT_RATES] : rates;

  const handleChange = (selectedValue: string) => {
    const numericValue = parseInt(selectedValue, 10);
    onChange?.(numericValue);
  };

  const formatRateLabel = (rate: VATRate) => {
    if (rate.value < 0) {
      return rate.label;
    }
    return `${rate.value}%`;
  };

  const options = allRates.map((rate) => ({
    value: rate.value.toString(),
    label: formatRateLabel(rate),
    description: rate.description,
  }));

  return (
    <div className={className}>
      <Select
        value={value?.toString() || ''}
        onChange={handleChange}
        onBlur={onBlur}
        options={options}
        placeholder="Wybierz stawkę VAT"
        disabled={disabled}
        error={error}
        testId={testId}
        renderOption={(option) => (
          <div className="flex flex-col">
            <span className="font-medium">{option.label}</span>
            {option.description && (
              <span className="text-sm text-neutral-600">{option.description}</span>
            )}
          </div>
        )}
      />
      
      {errorMessage && error && (
        <p className="mt-1 text-sm text-error-600" data-testid={`${testId}-error`}>
          {errorMessage}
        </p>
      )}
    </div>
  );
};

VATRateSelector.displayName = 'VATRateSelector';