import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { Checkbox } from './Checkbox';

const meta: Meta<typeof Checkbox> = {
  title: 'Design System/Primitives/Checkbox',
  component: Checkbox,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Checkbox component with support for checked, unchecked, and indeterminate states, full accessibility support, and Polish localization.',
      },
    },
  },
  argTypes: {
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      description: 'Size of the checkbox',
    },
    checked: {
      control: 'boolean',
      description: 'Whether the checkbox is checked',
    },
    indeterminate: {
      control: 'boolean',
      description: 'Whether the checkbox is in indeterminate state',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the checkbox is disabled',
    },
    error: {
      control: 'boolean',
      description: 'Whether the checkbox is in error state',
    },
    required: {
      control: 'boolean',
      description: 'Whether the checkbox is required',
    },
    labelPosition: {
      control: 'select',
      options: ['start', 'end'],
      description: 'Position of the label relative to checkbox',
    },
    label: {
      control: 'text',
      description: 'Label text',
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
    label: 'Checkbox label',
  },
};

export default meta;
type Story = StoryObj<typeof Checkbox>;

// Basic Stories
export const Default: Story = {
  args: {
    label: 'Domyślny checkbox',
  },
};

export const Checked: Story = {
  args: {
    label: 'Zaznaczony checkbox',
    checked: true,
  },
};

export const Unchecked: Story = {
  args: {
    label: 'Niezaznaczony checkbox',
    checked: false,
  },
};

export const Indeterminate: Story = {
  args: {
    label: 'Checkbox w stanie nieokreślonym',
    indeterminate: true,
  },
};

export const WithoutLabel: Story = {
  args: {
    'aria-label': 'Checkbox bez widocznej etykiety',
  },
};

export const WithHelperText: Story = {
  args: {
    label: 'Checkbox z tekstem pomocniczym',
    helperText: 'Ten tekst pomaga zrozumieć przeznaczenie checkboxa',
  },
};

export const Required: Story = {
  args: {
    label: 'Wymagany checkbox',
    required: true,
    helperText: 'To pole jest wymagane',
  },
};

// State Stories
export const Disabled: Story = {
  args: {
    label: 'Wyłączony checkbox',
    disabled: true,
  },
};

export const DisabledChecked: Story = {
  args: {
    label: 'Wyłączony zaznaczony checkbox',
    disabled: true,
    checked: true,
  },
};

export const DisabledIndeterminate: Story = {
  args: {
    label: 'Wyłączony nieokreślony checkbox',
    disabled: true,
    indeterminate: true,
  },
};

export const Error: Story = {
  args: {
    label: 'Checkbox z błędem',
    error: true,
    errorMessage: 'Musisz zaznaczyć ten checkbox',
  },
};

export const ErrorChecked: Story = {
  args: {
    label: 'Zaznaczony checkbox z błędem',
    error: true,
    checked: true,
    errorMessage: 'Nieprawidłowy wybór',
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

// Label Position Stories
export const LabelAtEnd: Story = {
  args: {
    label: 'Etykieta na końcu (domyślnie)',
    labelPosition: 'end',
  },
};

export const LabelAtStart: Story = {
  args: {
    label: 'Etykieta na początku',
    labelPosition: 'start',
  },
};

// Complex Stories
export const AllSizes: Story = {
  render: () => (
    <div className="space-y-4">
      <Checkbox size="xs" label="Extra Small (XS)" />
      <Checkbox size="sm" label="Small (SM)" />
      <Checkbox size="md" label="Medium (MD)" />
      <Checkbox size="lg" label="Large (LG)" />
      <Checkbox size="xl" label="Extra Large (XL)" />
    </div>
  ),
};

export const AllStates: Story = {
  render: () => (
    <div className="space-y-4">
      <Checkbox label="Niezaznaczony" checked={false} />
      <Checkbox label="Zaznaczony" checked={true} />
      <Checkbox label="Nieokreślony" indeterminate={true} />
      <Checkbox label="Wyłączony" disabled={true} />
      <Checkbox label="Wyłączony zaznaczony" disabled={true} checked={true} />
      <Checkbox label="Z błędem" error={true} errorMessage="Błąd walidacji" />
    </div>
  ),
};

// Polish Business Context Stories
export const TermsAndConditions: Story = {
  args: {
    label: 'Akceptuję regulamin i politykę prywatności',
    required: true,
    helperText: 'Wymagane do kontynuacji',
  },
};

export const NewsletterSubscription: Story = {
  args: {
    label: 'Chcę otrzymywać newsletter z informacjami o nowych funkcjach',
    helperText: 'Możesz zrezygnować w każdej chwili',
  },
};

export const VATPayerStatus: Story = {
  args: {
    label: 'Jestem płatnikiem VAT',
    helperText: 'Zaznacz jeśli Twoja firma jest zarejestrowana jako płatnik VAT',
  },
};

export const GDPRConsent: Story = {
  args: {
    label: 'Wyrażam zgodę na przetwarzanie danych osobowych zgodnie z RODO',
    required: true,
    helperText: 'Zgoda jest wymagana do świadczenia usług',
  },
};

// Form Group Story
export const CheckboxGroup: Story = {
  render: () => (
    <fieldset className="space-y-3">
      <legend className="text-lg font-medium text-gray-900 mb-3">
        Wybierz usługi które Cię interesują:
      </legend>
      <Checkbox label="Fakturowanie elektroniczne" />
      <Checkbox label="Księgowość online" />
      <Checkbox label="Rozliczenia podatkowe" />
      <Checkbox label="Kadry i płace" />
      <Checkbox label="Analityka biznesowa" />
      <div className="mt-4 text-sm text-gray-600">
        Możesz wybrać więcej niż jedną opcję
      </div>
    </fieldset>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Przykład grupy checkboxów w kontekście biznesowym - wybór usług.',
      },
    },
  },
};

// Accessibility Stories
export const AccessibilityDemo: Story = {
  args: {
    label: 'Checkbox z pełną dostępnością',
    helperText: 'Ten checkbox spełnia standardy WCAG 2.1 Level AA',
    'aria-label': 'Dostępny checkbox',
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
    const [checked, setChecked] = React.useState(false);
    const [indeterminate, setIndeterminate] = React.useState(false);
    
    return (
      <div className="space-y-4">
        <Checkbox
          label="Interaktywny checkbox"
          checked={checked}
          indeterminate={indeterminate}
          onChange={(newChecked) => {
            setChecked(newChecked);
            setIndeterminate(false);
          }}
          helperText={`Stan: ${indeterminate ? 'nieokreślony' : checked ? 'zaznaczony' : 'niezaznaczony'}`}
        />
        <div className="flex gap-2">
          <button
            onClick={() => {
              setChecked(true);
              setIndeterminate(false);
            }}
            className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
          >
            Zaznacz
          </button>
          <button
            onClick={() => {
              setChecked(false);
              setIndeterminate(false);
            }}
            className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
          >
            Odznacz
          </button>
          <button
            onClick={() => {
              setIndeterminate(true);
              setChecked(false);
            }}
            className="px-3 py-1 bg-yellow-600 text-white rounded text-sm hover:bg-yellow-700"
          >
            Nieokreślony
          </button>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Interaktywny przykład pokazujący wszystkie stany checkboxa.',
      },
    },
  },
};

// Form Integration Story
export const FormIntegration: Story = {
  render: () => (
    <form onSubmit={(e) => { e.preventDefault(); alert('Form submitted!'); }}>
      <div className="space-y-4">
        <fieldset className="space-y-3">
          <legend className="text-lg font-medium text-gray-900">
            Preferencje konta
          </legend>
          <Checkbox
            name="notifications"
            value="email"
            label="Powiadomienia email"
            helperText="Otrzymuj powiadomienia o nowych fakturach"
          />
          <Checkbox
            name="notifications"
            value="sms"
            label="Powiadomienia SMS"
            helperText="Otrzymuj ważne powiadomienia przez SMS"
          />
          <Checkbox
            name="marketing"
            value="newsletter"
            label="Newsletter marketingowy"
            helperText="Informacje o nowych funkcjach i promocjach"
          />
          <Checkbox
            name="terms"
            value="accepted"
            label="Akceptuję regulamin"
            required
            helperText="Wymagane do kontynuacji"
          />
        </fieldset>
        <button 
          type="submit" 
          className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
        >
          Zapisz preferencje
        </button>
      </div>
    </form>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Przykład integracji z formularzem - checkboxy z nazwami i wartościami.',
      },
    },
  },
};