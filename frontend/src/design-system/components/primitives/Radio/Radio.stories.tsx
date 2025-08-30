import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { Radio, RadioGroup, RadioOption } from './Radio';
import { Button } from '../Button/Button';

// Mock options for stories
const basicOptions: RadioOption[] = [
  { value: 'option1', label: 'Opcja 1' },
  { value: 'option2', label: 'Opcja 2' },
  { value: 'option3', label: 'Opcja 3' },
];

const optionsWithDescriptions: RadioOption[] = [
  { 
    value: 'basic', 
    label: 'Plan Podstawowy',
    description: 'Do 10 faktur miesięcznie, podstawowe funkcje'
  },
  { 
    value: 'professional', 
    label: 'Plan Profesjonalny',
    description: 'Do 100 faktur miesięcznie, zaawansowane funkcje'
  },
  { 
    value: 'enterprise', 
    label: 'Plan Enterprise',
    description: 'Nieograniczona liczba faktur, pełne wsparcie'
  },
];

const optionsWithDisabled: RadioOption[] = [
  { value: 'available1', label: 'Dostępna opcja 1' },
  { value: 'available2', label: 'Dostępna opcja 2' },
  { value: 'disabled', label: 'Opcja niedostępna', disabled: true },
  { value: 'available3', label: 'Dostępna opcja 3' },
];

const meta: Meta<typeof RadioGroup> = {
  title: 'Design System/Primitives/Radio',
  component: RadioGroup,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Radio and RadioGroup components with full accessibility support, keyboard navigation, and Polish localization.',
      },
    },
  },
  argTypes: {
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      description: 'Size of the radio buttons',
    },
    direction: {
      control: 'select',
      options: ['horizontal', 'vertical'],
      description: 'Layout direction of radio options',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether all radio buttons are disabled',
    },
    error: {
      control: 'boolean',
      description: 'Whether the radio group is in error state',
    },
    required: {
      control: 'boolean',
      description: 'Whether the radio group is required',
    },
    label: {
      control: 'text',
      description: 'Label for the radio group',
    },
    helperText: {
      control: 'text',
      description: 'Helper text',
    },
    errorMessage: {
      control: 'text',
      description: 'Error message',
    },
  },
  args: {
    options: basicOptions,
    name: 'example-radio',
  },
};

export default meta;
type Story = StoryObj<typeof RadioGroup>;

// Basic Stories
export const Default: Story = {
  args: {
    label: 'Wybierz opcję',
  },
};

export const WithValue: Story = {
  args: {
    label: 'Wybierz opcję',
    value: 'option2',
  },
};

export const WithHelperText: Story = {
  args: {
    label: 'Wybierz opcję',
    helperText: 'Wybierz jedną z dostępnych opcji',
  },
};

export const Required: Story = {
  args: {
    label: 'Wybierz opcję',
    required: true,
    helperText: 'To pole jest wymagane',
  },
};

// State Stories
export const Disabled: Story = {
  args: {
    label: 'Wyłączona grupa opcji',
    disabled: true,
    value: 'option1',
  },
};

export const Error: Story = {
  args: {
    label: 'Wybierz opcję',
    error: true,
    errorMessage: 'Musisz wybrać jedną z opcji',
  },
};

export const ErrorWithValue: Story = {
  args: {
    label: 'Wybierz opcję',
    error: true,
    errorMessage: 'Wybrana opcja jest nieprawidłowa',
    value: 'option1',
  },
};

// Layout Stories
export const Vertical: Story = {
  args: {
    label: 'Układ pionowy (domyślny)',
    direction: 'vertical',
  },
};

export const Horizontal: Story = {
  args: {
    label: 'Układ poziomy',
    direction: 'horizontal',
  },
};

// Size Stories
export const ExtraSmall: Story = {
  args: {
    label: 'Rozmiar XS',
    size: 'xs',
  },
};

export const Small: Story = {
  args: {
    label: 'Rozmiar SM',
    size: 'sm',
  },
};

export const Medium: Story = {
  args: {
    label: 'Rozmiar MD',
    size: 'md',
  },
};

export const Large: Story = {
  args: {
    label: 'Rozmiar LG',
    size: 'lg',
  },
};

export const ExtraLarge: Story = {
  args: {
    label: 'Rozmiar XL',
    size: 'xl',
  },
};

// Feature Stories
export const WithDescriptions: Story = {
  args: {
    label: 'Wybierz plan',
    options: optionsWithDescriptions,
    helperText: 'Porównaj funkcje dostępne w każdym planie',
  },
};

export const WithDisabledOptions: Story = {
  args: {
    label: 'Wybierz opcję',
    options: optionsWithDisabled,
    helperText: 'Niektóre opcje są niedostępne',
  },
};

// Complex Stories
export const AllSizes: Story = {
  render: () => (
    <div className="space-y-6">
      <RadioGroup
        name="size-xs"
        label="Extra Small (XS)"
        size="xs"
        options={basicOptions}
        value="option1"
      />
      <RadioGroup
        name="size-sm"
        label="Small (SM)"
        size="sm"
        options={basicOptions}
        value="option1"
      />
      <RadioGroup
        name="size-md"
        label="Medium (MD)"
        size="md"
        options={basicOptions}
        value="option1"
      />
      <RadioGroup
        name="size-lg"
        label="Large (LG)"
        size="lg"
        options={basicOptions}
        value="option1"
      />
      <RadioGroup
        name="size-xl"
        label="Extra Large (XL)"
        size="xl"
        options={basicOptions}
        value="option1"
      />
    </div>
  ),
};

export const AllStates: Story = {
  render: () => (
    <div className="space-y-6">
      <RadioGroup
        name="state-default"
        label="Domyślny stan"
        options={basicOptions}
      />
      <RadioGroup
        name="state-selected"
        label="Z wybraną opcją"
        options={basicOptions}
        value="option2"
      />
      <RadioGroup
        name="state-disabled"
        label="Wyłączony"
        options={basicOptions}
        disabled={true}
        value="option1"
      />
      <RadioGroup
        name="state-error"
        label="Z błędem"
        options={basicOptions}
        error={true}
        errorMessage="Musisz wybrać opcję"
      />
    </div>
  ),
};

// Polish Business Context Stories
export const CompanyType: Story = {
  args: {
    label: 'Forma prawna firmy',
    name: 'company-type',
    options: [
      { value: 'jednoosobowa', label: 'Działalność jednoosobowa' },
      { value: 'spolka-cywilna', label: 'Spółka cywilna' },
      { value: 'spolka-z-oo', label: 'Spółka z ograniczoną odpowiedzialnością' },
      { value: 'spolka-akcyjna', label: 'Spółka akcyjna' },
      { value: 'inne', label: 'Inna forma prawna' },
    ],
    helperText: 'Wybierz formę prawną prowadzonej działalności',
    required: true,
  },
};

export const VATSettlement: Story = {
  args: {
    label: 'Sposób rozliczania VAT',
    name: 'vat-settlement',
    options: [
      { 
        value: 'monthly', 
        label: 'Miesięczny',
        description: 'Składanie deklaracji VAT co miesiąc'
      },
      { 
        value: 'quarterly', 
        label: 'Kwartalny',
        description: 'Składanie deklaracji VAT co kwartał'
      },
      { 
        value: 'not-applicable', 
        label: 'Nie dotyczy',
        description: 'Nie jestem płatnikiem VAT'
      },
    ],
    helperText: 'Wybierz częstotliwość rozliczania VAT',
    required: true,
  },
};

export const PaymentMethod: Story = {
  args: {
    label: 'Preferowana metoda płatności',
    name: 'payment-method',
    direction: 'horizontal',
    options: [
      { value: 'card', label: 'Karta płatnicza' },
      { value: 'transfer', label: 'Przelew bankowy' },
      { value: 'blik', label: 'BLIK' },
      { value: 'paypal', label: 'PayPal' },
    ],
    helperText: 'Wybierz metodę płatności za subskrypcję',
  },
};

export const InvoiceFrequency: Story = {
  args: {
    label: 'Częstotliwość wystawiania faktur',
    name: 'invoice-frequency',
    options: [
      { 
        value: 'daily', 
        label: 'Codziennie',
        description: 'Faktury wystawiane każdego dnia roboczego'
      },
      { 
        value: 'weekly', 
        label: 'Tygodniowo',
        description: 'Faktury wystawiane raz w tygodniu'
      },
      { 
        value: 'monthly', 
        label: 'Miesięcznie',
        description: 'Faktury wystawiane raz w miesiącu'
      },
      { 
        value: 'on-demand', 
        label: 'Na żądanie',
        description: 'Faktury wystawiane według potrzeb'
      },
    ],
    helperText: 'Wybierz jak często wystawiasz faktury',
  },
};

// Individual Radio Component Stories
export const SingleRadio: Story = {
  render: () => (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Pojedyncze komponenty Radio:</h3>
      <Radio
        name="single-radio"
        value="option1"
        label="Pojedynczy radio button"
        helperText="To jest pojedynczy komponent Radio"
      />
      <Radio
        name="single-radio"
        value="option2"
        label="Drugi radio button"
        checked={true}
      />
      <Radio
        name="single-radio"
        value="option3"
        label="Wyłączony radio button"
        disabled={true}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Przykład użycia pojedynczych komponentów Radio zamiast RadioGroup.',
      },
    },
  },
};

// Accessibility Stories
export const AccessibilityDemo: Story = {
  args: {
    label: 'Radio group z pełną dostępnością',
    options: basicOptions,
    helperText: 'Ten radio group spełnia standardy WCAG 2.1 Level AA',
    'aria-label': 'Dostępna grupa opcji',
    required: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Demonstracja pełnej dostępności - obsługa klawiatury, screen readerów, i właściwe atrybuty ARIA.',
      },
    },
  },
};

// Interactive Stories
export const InteractiveExample: Story = {
  render: () => {
    const [value, setValue] = React.useState<string>('');
    
    return (
      <div className="space-y-4">
        <RadioGroup
          name="interactive-radio"
          label="Interaktywny radio group"
          options={basicOptions}
          value={value}
          onChange={(newValue) => setValue(newValue)}
          helperText={`Wybrana wartość: ${value || 'brak'}`}
        />
        <div className="flex gap-2">
          <button
            onClick={() => setValue('option1')}
            className="px-3 py-1 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
          >
            Wybierz opcję 1
          </button>
          <button
            onClick={() => setValue('option2')}
            className="px-3 py-1 bg-success-600 text-white rounded-md text-sm hover:bg-green-700"
          >
            Wybierz opcję 2
          </button>
          <button
            onClick={() => setValue('')}
            className="px-3 py-1 bg-error-600 text-white rounded-md text-sm hover:bg-red-700"
          >
            Wyczyść wybór
          </button>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Interaktywny przykład pokazujący kontrolę stanu radio group.',
      },
    },
  },
};

// Form Integration Story
export const FormIntegration: Story = {
  render: () => (
    <form onSubmit={(e) => { e.preventDefault(); alert('Form submitted!'); }}>
      <div className="space-y-6">
        <RadioGroup
          name="company-size"
          label="Wielkość firmy"
          options={[
            { value: 'micro', label: 'Mikroprzedsiębiorstwo (do 9 pracowników)' },
            { value: 'small', label: 'Małe przedsiębiorstwo (10-49 pracowników)' },
            { value: 'medium', label: 'Średnie przedsiębiorstwo (50-249 pracowników)' },
            { value: 'large', label: 'Duże przedsiębiorstwo (250+ pracowników)' },
          ]}
          required
          helperText="Wybierz wielkość Twojej firmy"
        />
        
        <RadioGroup
          name="industry"
          label="Branża"
          direction="horizontal"
          options={[
            { value: 'it', label: 'IT' },
            { value: 'finance', label: 'Finanse' },
            { value: 'retail', label: 'Handel' },
            { value: 'manufacturing', label: 'Produkcja' },
            { value: 'other', label: 'Inna' },
          ]}
          helperText="Wybierz branżę działalności"
        />
        
        <button 
          type="submit" 
          variant="primary"
        >
          Wyślij formularz
        </button>
      </div>
    </form>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Przykład integracji z formularzem - radio groups z nazwami i wartościami.',
      },
    },
  },
};