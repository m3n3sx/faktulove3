import type { Meta, StoryObj } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import { CurrencyInput } from './CurrencyInput';

const meta: Meta<typeof CurrencyInput> = {
  title: 'Design System/Business/CurrencyInput',
  component: CurrencyInput,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A specialized input component for currency values with Polish formatting, automatic number formatting, and validation.',
      },
    },
    a11y: {
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true,
          },
          {
            id: 'label',
            enabled: true,
          },
          {
            id: 'keyboard-navigation',
            enabled: true,
          },
        ],
      },
    },
  },
  argTypes: {
    currency: {
      control: 'select',
      options: ['PLN', 'EUR', 'USD', 'GBP'],
      description: 'Currency code for formatting',
    },
    locale: {
      control: 'select',
      options: ['pl-PL', 'en-US', 'de-DE', 'fr-FR'],
      description: 'Locale for number formatting',
    },
    maxDecimals: {
      control: { type: 'number', min: 0, max: 4 },
      description: 'Maximum number of decimal places',
    },
    allowNegative: {
      control: 'boolean',
      description: 'Whether negative values are allowed',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the input is disabled',
    },
    error: {
      control: 'boolean',
      description: 'Whether the input has an error state',
    },
    onChange: {
      action: 'changed',
      description: 'Callback when value changes',
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof CurrencyInput>;

// Basic currency input
export const Default: Story = {
  args: {
    placeholder: '0,00 zł',
    onChange: action('currency-changed'),
  },
};

// With initial value
export const WithValue: Story = {
  args: {
    value: 1234.56,
    onChange: action('currency-changed'),
  },
};

// Different currencies
export const Currencies: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          Polish Złoty (PLN)
        </label>
        <CurrencyInput 
          currency="PLN" 
          locale="pl-PL" 
          placeholder="0,00 zł"
          onChange={action('pln-changed')} 
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          Euro (EUR)
        </label>
        <CurrencyInput 
          currency="EUR" 
          locale="pl-PL" 
          placeholder="0,00 €"
          onChange={action('eur-changed')} 
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          US Dollar (USD)
        </label>
        <CurrencyInput 
          currency="USD" 
          locale="en-US" 
          placeholder="$0.00"
          onChange={action('usd-changed')} 
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          British Pound (GBP)
        </label>
        <CurrencyInput 
          currency="GBP" 
          locale="en-GB" 
          placeholder="£0.00"
          onChange={action('gbp-changed')} 
        />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Currency input supports different currencies with appropriate formatting.',
      },
    },
  },
};

// Different decimal precision
export const DecimalPrecision: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          No decimals (whole numbers)
        </label>
        <CurrencyInput 
          maxDecimals={0}
          placeholder="0 zł"
          onChange={action('whole-changed')} 
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          2 decimal places (standard)
        </label>
        <CurrencyInput 
          maxDecimals={2}
          placeholder="0,00 zł"
          onChange={action('standard-changed')} 
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          4 decimal places (precise)
        </label>
        <CurrencyInput 
          maxDecimals={4}
          placeholder="0,0000 zł"
          onChange={action('precise-changed')} 
        />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Different decimal precision options for various use cases.',
      },
    },
  },
};

// Negative values
export const NegativeValues: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          Positive only (default)
        </label>
        <CurrencyInput 
          allowNegative={false}
          placeholder="0,00 zł"
          onChange={action('positive-only-changed')} 
        />
        <p className="text-xs text-neutral-500 mt-1">
          Negative values will be converted to positive
        </p>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          Allow negative values
        </label>
        <CurrencyInput 
          allowNegative={true}
          placeholder="0,00 zł"
          onChange={action('negative-allowed-changed')} 
        />
        <p className="text-xs text-neutral-500 mt-1">
          Can enter negative amounts (e.g., refunds)
        </p>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Control whether negative values are allowed.',
      },
    },
  },
};

// States
export const States: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          Normal state
        </label>
        <CurrencyInput 
          placeholder="0,00 zł"
          onChange={action('normal-changed')} 
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          Disabled state
        </label>
        <CurrencyInput 
          value={1234.56}
          disabled={true}
          onChange={action('disabled-changed')} 
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          Error state
        </label>
        <CurrencyInput 
          error={true}
          errorMessage="Kwota musi być większa niż 0"
          placeholder="0,00 zł"
          onChange={action('error-changed')} 
        />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Different states of the currency input component.',
      },
    },
  },
};

// Polish business scenarios
export const PolishBusinessScenarios: Story = {
  render: () => (
    <div className="space-y-6 w-80">
      <div>
        <h3 className="text-lg font-semibold mb-4">Faktury i płatności</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Wartość netto
            </label>
            <CurrencyInput 
              placeholder="0,00 zł"
              onChange={action('net-value-changed')} 
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Kwota VAT (23%)
            </label>
            <CurrencyInput 
              placeholder="0,00 zł"
              onChange={action('vat-amount-changed')} 
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Wartość brutto
            </label>
            <CurrencyInput 
              placeholder="0,00 zł"
              onChange={action('gross-value-changed')} 
            />
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">Korekty i zwroty</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Kwota korekty
            </label>
            <CurrencyInput 
              allowNegative={true}
              placeholder="0,00 zł"
              onChange={action('correction-changed')} 
            />
            <p className="text-xs text-neutral-500 mt-1">
              Ujemne wartości dla zwrotów
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Rabat
            </label>
            <CurrencyInput 
              placeholder="0,00 zł"
              onChange={action('discount-changed')} 
            />
          </div>
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Real-world Polish business scenarios using currency input.',
      },
    },
  },
};

// Formatting behavior demonstration
export const FormattingBehavior: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          Try typing: 1234.56
        </label>
        <CurrencyInput 
          placeholder="0,00 zł"
          onChange={action('formatting-changed')} 
        />
        <p className="text-xs text-neutral-500 mt-1">
          Formats automatically when you leave the field
        </p>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-1">
          With initial value: 9876.54
        </label>
        <CurrencyInput 
          value={9876.54}
          onChange={action('initial-value-changed')} 
        />
        <p className="text-xs text-neutral-500 mt-1">
          Click to edit, shows raw number for editing
        </p>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Demonstrates the formatting behavior when focusing and blurring the input.',
      },
    },
  },
};

// Accessibility features
export const AccessibilityFeatures: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <div>
        <label 
          htmlFor="accessible-currency" 
          className="block text-sm font-medium text-neutral-700 mb-1"
        >
          Kwota faktury
        </label>
        <CurrencyInput 
          testId="accessible-currency"
          placeholder="0,00 zł"
          onChange={action('accessible-changed')}
        />
        <p className="text-xs text-neutral-500 mt-1">
          Proper label association for screen readers
        </p>
      </div>
      
      <div>
        <label 
          htmlFor="described-currency" 
          className="block text-sm font-medium text-neutral-700 mb-1"
        >
          Kwota z opisem
        </label>
        <CurrencyInput 
          testId="described-currency"
          placeholder="0,00 zł"
          onChange={action('described-changed')}
        />
        <p id="currency-description" className="text-xs text-neutral-500 mt-1">
          Wprowadź kwotę w złotych polskich. Używaj przecinka jako separatora dziesiętnego.
        </p>
      </div>
      
      <div>
        <label 
          htmlFor="error-currency" 
          className="block text-sm font-medium text-neutral-700 mb-1"
        >
          Kwota z błędem
        </label>
        <CurrencyInput 
          testId="error-currency"
          error={true}
          errorMessage="Kwota musi być większa niż 0 zł"
          placeholder="0,00 zł"
          onChange={action('error-accessible-changed')}
        />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Accessibility features including proper labeling, descriptions, and error handling.',
      },
    },
  },
};

// Interactive playground
export const Playground: Story = {
  args: {
    currency: 'PLN',
    locale: 'pl-PL',
    placeholder: '0,00 zł',
    maxDecimals: 2,
    allowNegative: false,
    disabled: false,
    error: false,
    errorMessage: '',
    onChange: action('playground-changed'),
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive playground to test different currency input configurations.',
      },
    },
  },
};