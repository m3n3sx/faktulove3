// Input Component Stories
import type { Meta, StoryObj } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import { Input } from './Input';
import { 
  CurrencyInput, 
  NIPInput, 
  REGONInput, 
  PostalCodeInput, 
  PhoneInput 
} from './PolishBusinessInput';

// Icons for stories
const SearchIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8"></circle>
    <path d="m21 21-4.35-4.35"></path>
  </svg>
);

const UserIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
);

const EmailIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
    <polyline points="22,6 12,13 2,6"></polyline>
  </svg>
);

const meta: Meta<typeof Input> = {
  title: 'Design System/Primitives/Input',
  component: Input,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile input component with multiple types, sizes, and states. Includes Polish business-specific variants for common data entry needs.',
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
            id: 'aria-input-field-name',
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
    type: {
      control: 'select',
      options: ['text', 'email', 'password', 'number', 'tel', 'url', 'search'],
      description: 'Input type',
    },
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      description: 'Size of the input',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the input is disabled',
    },
    readOnly: {
      control: 'boolean',
      description: 'Whether the input is readonly',
    },
    required: {
      control: 'boolean',
      description: 'Whether the input is required',
    },
    error: {
      control: 'boolean',
      description: 'Whether the input has an error state',
    },
    iconPosition: {
      control: 'select',
      options: ['start', 'end'],
      description: 'Position of the icon',
    },
    onChange: {
      action: 'changed',
      description: 'Change handler',
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof Input>;

// Basic Input Stories
export const Default: Story = {
  args: {
    label: 'Default Input',
    placeholder: 'Enter text...',
    onChange: action('input-changed'),
  },
};

export const WithHelperText: Story = {
  args: {
    label: 'Input with Helper',
    placeholder: 'Enter your username',
    helperText: 'This will be your unique identifier',
    onChange: action('input-changed'),
  },
};

export const Required: Story = {
  args: {
    label: 'Required Field',
    placeholder: 'This field is required',
    required: true,
    onChange: action('input-changed'),
  },
};

export const WithError: Story = {
  args: {
    label: 'Input with Error',
    placeholder: 'Enter valid email',
    error: true,
    errorMessage: 'Please enter a valid email address',
    onChange: action('input-changed'),
  },
};

// Input Types
export const InputTypes: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <Input 
        label="Text Input" 
        type="text" 
        placeholder="Enter text" 
        onChange={action('text-changed')} 
      />
      <Input 
        label="Email Input" 
        type="email" 
        placeholder="Enter email" 
        onChange={action('email-changed')} 
      />
      <Input 
        label="Password Input" 
        type="password" 
        placeholder="Enter password" 
        onChange={action('password-changed')} 
      />
      <Input 
        label="Number Input" 
        type="number" 
        placeholder="Enter number" 
        onChange={action('number-changed')} 
      />
      <Input 
        label="Phone Input" 
        type="tel" 
        placeholder="Enter phone" 
        onChange={action('tel-changed')} 
      />
      <Input 
        label="Search Input" 
        type="search" 
        placeholder="Search..." 
        onChange={action('search-changed')} 
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Different input types for various data entry needs.',
      },
    },
  },
};

// Size Variants
export const Sizes: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <Input 
        label="Extra Small" 
        size="xs" 
        placeholder="Extra small input" 
        onChange={action('xs-changed')} 
      />
      <Input 
        label="Small" 
        size="sm" 
        placeholder="Small input" 
        onChange={action('sm-changed')} 
      />
      <Input 
        label="Medium" 
        size="md" 
        placeholder="Medium input" 
        onChange={action('md-changed')} 
      />
      <Input 
        label="Large" 
        size="lg" 
        placeholder="Large input" 
        onChange={action('lg-changed')} 
      />
      <Input 
        label="Extra Large" 
        size="xl" 
        placeholder="Extra large input" 
        onChange={action('xl-changed')} 
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Input components come in five different sizes.',
      },
    },
  },
};

// States
export const States: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <Input 
        label="Normal State" 
        placeholder="Normal input" 
        onChange={action('normal-changed')} 
      />
      <Input 
        label="Disabled State" 
        placeholder="Disabled input" 
        disabled 
        onChange={action('disabled-changed')} 
      />
      <Input 
        label="Readonly State" 
        value="Readonly value" 
        readOnly 
        onChange={action('readonly-changed')} 
      />
      <Input 
        label="Error State" 
        placeholder="Input with error" 
        error 
        errorMessage="This field has an error" 
        onChange={action('error-changed')} 
      />
      <Input 
        label="Required Field" 
        placeholder="Required input" 
        required 
        helperText="This field is required" 
        onChange={action('required-changed')} 
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Different states that inputs can have.',
      },
    },
  },
};

// With Icons
export const WithIcons: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <Input 
        label="Search" 
        placeholder="Search users..." 
        icon={<SearchIcon />} 
        iconPosition="start" 
        onChange={action('search-changed')} 
      />
      <Input 
        label="Username" 
        placeholder="Enter username" 
        icon={<UserIcon />} 
        iconPosition="start" 
        onChange={action('username-changed')} 
      />
      <Input 
        label="Email" 
        type="email" 
        placeholder="Enter email" 
        icon={<EmailIcon />} 
        iconPosition="end" 
        onChange={action('email-changed')} 
      />
      <Input 
        label="Search with Error" 
        placeholder="Search..." 
        icon={<SearchIcon />} 
        iconPosition="start" 
        error 
        errorMessage="Search query is too short" 
        onChange={action('search-error-changed')} 
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Inputs can include icons at the start or end position.',
      },
    },
  },
};

// Polish Business Inputs
export const PolishBusinessInputs: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <CurrencyInput 
        label="Kwota" 
        placeholder="0,00" 
        helperText="Podaj kwotę w złotych" 
        onChange={action('currency-changed')} 
      />
      <NIPInput 
        label="NIP" 
        placeholder="123-456-78-90" 
        helperText="Numer identyfikacji podatkowej" 
        onChange={action('nip-changed')} 
      />
      <REGONInput 
        label="REGON" 
        regonType={9} 
        placeholder="123-456-789" 
        helperText="Numer w rejestrze REGON" 
        onChange={action('regon-changed')} 
      />
      <PostalCodeInput 
        label="Kod pocztowy" 
        placeholder="00-000" 
        helperText="Polski kod pocztowy" 
        onChange={action('postal-changed')} 
      />
      <PhoneInput 
        label="Telefon" 
        placeholder="123 456 789" 
        helperText="Numer telefonu" 
        onChange={action('phone-changed')} 
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Specialized input components for Polish business data with automatic formatting and validation.',
      },
    },
  },
};

// Currency Input Variants
export const CurrencyVariants: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <CurrencyInput 
        label="Kwota w PLN" 
        currency="zł" 
        decimals={2} 
        onChange={action('pln-changed')} 
      />
      <CurrencyInput 
        label="Amount in EUR" 
        currency="EUR" 
        decimals={2} 
        onChange={action('eur-changed')} 
      />
      <CurrencyInput 
        label="Whole Numbers Only" 
        currency="zł" 
        decimals={0} 
        onChange={action('whole-changed')} 
      />
      <CurrencyInput 
        label="With Range" 
        currency="zł" 
        min={0} 
        max={10000} 
        helperText="Wartość między 0 a 10,000 zł" 
        onChange={action('range-changed')} 
      />
      <CurrencyInput 
        label="Allow Negative" 
        currency="zł" 
        allowNegative 
        helperText="Może być ujemna" 
        onChange={action('negative-changed')} 
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Currency input with different configurations for various use cases.',
      },
    },
  },
};

// Validation Examples
export const ValidationExamples: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <NIPInput 
        label="NIP z walidacją" 
        showValidation 
        helperText="Wprowadź poprawny NIP" 
        onChange={action('nip-validation-changed')} 
      />
      <REGONInput 
        label="REGON 9-cyfrowy" 
        regonType={9} 
        showValidation 
        helperText="9-cyfrowy numer REGON" 
        onChange={action('regon9-validation-changed')} 
      />
      <REGONInput 
        label="REGON 14-cyfrowy" 
        regonType={14} 
        showValidation 
        helperText="14-cyfrowy numer REGON" 
        onChange={action('regon14-validation-changed')} 
      />
      <PostalCodeInput 
        label="Kod pocztowy z walidacją" 
        showValidation 
        helperText="Format: 00-000" 
        onChange={action('postal-validation-changed')} 
      />
      <PhoneInput 
        label="Telefon z walidacją" 
        showValidation 
        helperText="9-cyfrowy numer telefonu" 
        onChange={action('phone-validation-changed')} 
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Polish business inputs with real-time validation and visual feedback.',
      },
    },
  },
};

// Phone Input Variants
export const PhoneVariants: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <PhoneInput 
        label="Telefon krajowy" 
        includeCountryCode={false} 
        placeholder="123 456 789" 
        helperText="Numer bez kierunkowego" 
        onChange={action('domestic-phone-changed')} 
      />
      <PhoneInput 
        label="Telefon międzynarodowy" 
        includeCountryCode 
        placeholder="+48 123 456 789" 
        helperText="Numer z kierunkowym +48" 
        onChange={action('international-phone-changed')} 
      />
      <PhoneInput 
        label="Telefon bez walidacji" 
        showValidation={false} 
        placeholder="123 456 789" 
        helperText="Bez automatycznej walidacji" 
        onChange={action('no-validation-phone-changed')} 
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Phone input variants for different formatting needs.',
      },
    },
  },
};

// Accessibility Demo
export const AccessibilityFeatures: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <Input 
        label="Pole z opisem" 
        placeholder="Wprowadź tekst" 
        helperText="Ten tekst pomoże użytkownikowi" 
        aria-describedby="custom-description" 
        onChange={action('described-changed')} 
      />
      <Input 
        label="Pole z błędem" 
        placeholder="Niepoprawna wartość" 
        error 
        errorMessage="To pole jest wymagane" 
        aria-invalid={true} 
        onChange={action('invalid-changed')} 
      />
      <Input 
        label="Pole z niestandardową etykietą" 
        placeholder="Wpisz tutaj" 
        aria-label="Niestandardowa etykieta dla czytników ekranu" 
        onChange={action('custom-label-changed')} 
      />
      <CurrencyInput 
        label="Kwota z opisem" 
        helperText="Kwota będzie sformatowana automatycznie" 
        aria-describedby="currency-help" 
        onChange={action('currency-a11y-changed')} 
      />
      <div id="currency-help" className="text-sm text-gray-600">
        Dodatkowy opis dla czytników ekranu
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Demonstration of accessibility features including ARIA labels, descriptions, and error handling.',
      },
    },
  },
};

// Interactive Playground
export const Playground: Story = {
  args: {
    label: 'Playground Input',
    placeholder: 'Enter text...',
    type: 'text',
    size: 'md',
    disabled: false,
    readOnly: false,
    required: false,
    error: false,
    errorMessage: '',
    helperText: '',
    onChange: action('playground-changed'),
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive playground to test different input configurations.',
      },
    },
  },
};