import type { Meta, StoryObj } from '@storybook/react';
import { Select, SelectOption } from './Select';
import { Button } from '../Button/Button';

// Mock options for stories
const basicOptions: SelectOption[] = [
  { value: 'option1', label: 'Opcja 1' },
  { value: 'option2', label: 'Opcja 2' },
  { value: 'option3', label: 'Opcja 3' },
  { value: 'option4', label: 'Opcja 4' },
];

const optionsWithDisabled: SelectOption[] = [
  { value: 'option1', label: 'Opcja 1' },
  { value: 'option2', label: 'Opcja 2' },
  { value: 'option3', label: 'Opcja 3 (wyłączona)', disabled: true },
  { value: 'option4', label: 'Opcja 4' },
  { value: 'option5', label: 'Opcja 5' },
];

const manyOptions: SelectOption[] = Array.from({ length: 20 }, (_, i) => ({
  value: `option${i + 1}`,
  label: `Opcja ${i + 1}`,
}));

const meta: Meta<typeof Select> = {
  title: 'Design System/Primitives/Select',
  component: Select,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Select component with single and multi-select capability, search functionality, and full accessibility support.',
      },
    },
  },
  argTypes: {
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      description: 'Size of the select component',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the select is disabled',
    },
    error: {
      control: 'boolean',
      description: 'Whether the select is in error state',
    },
    required: {
      control: 'boolean',
      description: 'Whether the select is required',
    },
    multiple: {
      control: 'boolean',
      description: 'Whether multiple selection is allowed',
    },
    searchable: {
      control: 'boolean',
      description: 'Whether search functionality is enabled',
    },
    clearable: {
      control: 'boolean',
      description: 'Whether clear functionality is enabled',
    },
    placeholder: {
      control: 'text',
      description: 'Placeholder text',
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
    options: basicOptions,
    placeholder: 'Wybierz opcję',
  },
};

export default meta;
type Story = StoryObj<typeof Select>;

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
    label: 'Wybierz opcję',
    disabled: true,
    value: 'option1',
  },
};

export const Error: Story = {
  args: {
    label: 'Wybierz opcję',
    error: true,
    errorMessage: 'Proszę wybrać prawidłową opcję',
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
export const Multiple: Story = {
  args: {
    label: 'Wybierz opcje (wielokrotny wybór)',
    multiple: true,
    helperText: 'Możesz wybrać więcej niż jedną opcję',
  },
};

export const MultipleWithValue: Story = {
  args: {
    label: 'Wybierz opcje (wielokrotny wybór)',
    multiple: true,
    value: ['option1', 'option3'],
  },
};

export const Searchable: Story = {
  args: {
    label: 'Wybierz opcję (z wyszukiwaniem)',
    searchable: true,
    options: manyOptions,
    helperText: 'Wpisz aby wyszukać opcję',
  },
};

export const Clearable: Story = {
  args: {
    label: 'Wybierz opcję (z możliwością wyczyszczenia)',
    clearable: true,
    value: 'option2',
    helperText: 'Kliknij X aby wyczyścić wybór',
  },
};

export const SearchableAndClearable: Story = {
  args: {
    label: 'Wybierz opcję (wyszukiwanie + czyszczenie)',
    searchable: true,
    clearable: true,
    options: manyOptions,
    value: 'option5',
  },
};

export const WithDisabledOptions: Story = {
  args: {
    label: 'Wybierz opcję',
    options: optionsWithDisabled,
    helperText: 'Niektóre opcje są wyłączone',
  },
};

// Complex Stories
export const MultipleSearchableClearable: Story = {
  args: {
    label: 'Zaawansowany select',
    multiple: true,
    searchable: true,
    clearable: true,
    options: manyOptions,
    value: ['option2', 'option5', 'option8'],
    helperText: 'Wielokrotny wybór z wyszukiwaniem i czyszczeniem',
  },
};

export const LongOptions: Story = {
  args: {
    label: 'Opcje z długimi nazwami',
    options: [
      { value: 'long1', label: 'To jest bardzo długa nazwa opcji która może się nie zmieścić' },
      { value: 'long2', label: 'Kolejna długa opcja z polskimi znakami ąćęłńóśźż' },
      { value: 'long3', label: 'Jeszcze jedna opcja o bardzo długiej nazwie dla testów' },
    ],
    helperText: 'Test z długimi nazwami opcji',
  },
};

// Polish Business Context Stories
export const PolishBusinessSelect: Story = {
  args: {
    label: 'Rodzaj działalności',
    options: [
      { value: 'handel', label: 'Handel detaliczny' },
      { value: 'uslugi', label: 'Usługi profesjonalne' },
      { value: 'produkcja', label: 'Produkcja i wytwarzanie' },
      { value: 'transport', label: 'Transport i logistyka' },
      { value: 'it', label: 'Technologie informatyczne' },
      { value: 'budowa', label: 'Budownictwo' },
      { value: 'inne', label: 'Inne' },
    ],
    helperText: 'Wybierz główny rodzaj działalności firmy',
    required: true,
  },
};

export const VATRateSelect: Story = {
  args: {
    label: 'Stawka VAT',
    options: [
      { value: '23', label: '23% - stawka podstawowa' },
      { value: '8', label: '8% - stawka obniżona' },
      { value: '5', label: '5% - stawka obniżona' },
      { value: '0', label: '0% - stawka zerowa' },
      { value: 'zw', label: 'zw. - zwolnione z VAT' },
      { value: 'np', label: 'n.p. - nie podlega VAT' },
    ],
    helperText: 'Wybierz odpowiednią stawkę VAT',
    required: true,
  },
};

// Accessibility Stories
export const AccessibilityDemo: Story = {
  args: {
    label: 'Select z pełną dostępnością',
    options: basicOptions,
    helperText: 'Ten select spełnia standardy WCAG 2.1 Level AA',
    'aria-label': 'Dostępny select',
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

// Form Integration Story
export const FormIntegration: Story = {
  render: () => (
    <form onSubmit={(e) => { e.preventDefault(); alert('Form submitted!'); }}>
      <div className="space-y-4">
        <Select
          name="country"
          label="Kraj"
          options={[
            { value: 'pl', label: 'Polska' },
            { value: 'de', label: 'Niemcy' },
            { value: 'fr', label: 'Francja' },
            { value: 'uk', label: 'Wielka Brytania' },
          ]}
          required
          helperText="Wybierz kraj"
        />
        <Select
          name="languages"
          label="Języki"
          multiple
          options={[
            { value: 'pl', label: 'Polski' },
            { value: 'en', label: 'Angielski' },
            { value: 'de', label: 'Niemiecki' },
            { value: 'fr', label: 'Francuski' },
          ]}
          helperText="Wybierz znane języki"
        />
        <button 
          type="submit" 
          variant="primary"
        >
          Wyślij
        </button>
      </div>
    </form>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Przykład integracji z formularzem - select automatycznie tworzy ukryte pola input dla wysyłania danych.',
      },
    },
  },
};