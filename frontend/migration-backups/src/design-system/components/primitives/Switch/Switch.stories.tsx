import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { Switch } from './Switch';

const meta: Meta<typeof Switch> = {
  title: 'Design System/Primitives/Switch',
  component: Switch,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Switch component for boolean settings with full accessibility support, custom icons, and Polish localization.',
      },
    },
  },
  argTypes: {
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      description: 'Size of the switch',
    },
    checked: {
      control: 'boolean',
      description: 'Whether the switch is checked',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the switch is disabled',
    },
    error: {
      control: 'boolean',
      description: 'Whether the switch is in error state',
    },
    required: {
      control: 'boolean',
      description: 'Whether the switch is required',
    },
    labelPosition: {
      control: 'select',
      options: ['start', 'end'],
      description: 'Position of the label relative to switch',
    },
    label: {
      control: 'text',
      description: 'Label text',
    },
    description: {
      control: 'text',
      description: 'Description text',
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
    label: 'Switch label',
  },
};

export default meta;
type Story = StoryObj<typeof Switch>;

// Basic Stories
export const Default: Story = {
  args: {
    label: 'Domyślny switch',
  },
};

export const Checked: Story = {
  args: {
    label: 'Włączony switch',
    checked: true,
  },
};

export const Unchecked: Story = {
  args: {
    label: 'Wyłączony switch',
    checked: false,
  },
};

export const WithoutLabel: Story = {
  args: {
    'aria-label': 'Switch bez widocznej etykiety',
  },
};

export const WithDescription: Story = {
  args: {
    label: 'Switch z opisem',
    description: 'Ten opis wyjaśnia przeznaczenie switcha',
  },
};

export const WithHelperText: Story = {
  args: {
    label: 'Switch z tekstem pomocniczym',
    helperText: 'Dodatkowe informacje o funkcji switcha',
  },
};

export const WithDescriptionAndHelper: Story = {
  args: {
    label: 'Kompletny switch',
    description: 'Główny opis funkcji switcha',
    helperText: 'Dodatkowe informacje pomocnicze',
  },
};

export const Required: Story = {
  args: {
    label: 'Wymagany switch',
    required: true,
    description: 'Ten switch jest wymagany',
  },
};

// State Stories
export const Disabled: Story = {
  args: {
    label: 'Wyłączony switch',
    disabled: true,
  },
};

export const DisabledChecked: Story = {
  args: {
    label: 'Wyłączony włączony switch',
    disabled: true,
    checked: true,
  },
};

export const Error: Story = {
  args: {
    label: 'Switch z błędem',
    error: true,
    errorMessage: 'Musisz włączyć tę opcję',
  },
};

export const ErrorChecked: Story = {
  args: {
    label: 'Włączony switch z błędem',
    error: true,
    checked: true,
    errorMessage: 'Nieprawidłowa konfiguracja',
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
    description: 'Switch z etykietą po prawej stronie',
  },
};

export const LabelAtStart: Story = {
  args: {
    label: 'Etykieta na początku',
    labelPosition: 'start',
    description: 'Switch z etykietą po lewej stronie',
  },
};

// Icon Stories
export const WithIcons: Story = {
  args: {
    label: 'Switch z ikonami',
    checked: true,
    checkedIcon: (
      <svg className="w-full h-full" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
      </svg>
    ),
    uncheckedIcon: (
      <svg className="w-full h-full" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
      </svg>
    ),
    description: 'Switch z ikonami zaznaczenia i odznaczenia',
  },
};

export const WithCustomIcons: Story = {
  args: {
    label: 'Switch z niestandardowymi ikonami',
    checked: false,
    size: 'lg',
    checkedIcon: <span>🌙</span>,
    uncheckedIcon: <span>☀️</span>,
    description: 'Przełącznik trybu ciemnego/jasnego',
  },
};

// Complex Stories
export const AllSizes: Story = {
  render: () => (
    <div className="space-y-4">
      <Switch size="xs" label="Extra Small (XS)" checked={true} />
      <Switch size="sm" label="Small (SM)" checked={true} />
      <Switch size="md" label="Medium (MD)" checked={true} />
      <Switch size="lg" label="Large (LG)" checked={true} />
      <Switch size="xl" label="Extra Large (XL)" checked={true} />
    </div>
  ),
};

export const AllStates: Story = {
  render: () => (
    <div className="space-y-4">
      <Switch label="Wyłączony" checked={false} />
      <Switch label="Włączony" checked={true} />
      <Switch label="Wyłączony (disabled)" disabled={true} checked={false} />
      <Switch label="Włączony (disabled)" disabled={true} checked={true} />
      <Switch label="Z błędem" error={true} errorMessage="Błąd walidacji" />
      <Switch label="Wymagany" required={true} />
    </div>
  ),
};

// Polish Business Context Stories
export const NotificationSettings: Story = {
  args: {
    label: 'Powiadomienia email',
    description: 'Otrzymuj powiadomienia o nowych fakturach na email',
    checked: true,
  },
};

export const AutoBackup: Story = {
  args: {
    label: 'Automatyczne kopie zapasowe',
    description: 'Twórz kopie zapasowe danych co 24 godziny',
    helperText: 'Zalecane dla bezpieczeństwa danych',
    checked: true,
  },
};

export const VATCalculation: Story = {
  args: {
    label: 'Automatyczne obliczanie VAT',
    description: 'System automatycznie obliczy VAT na podstawie stawek',
    helperText: 'Można wyłączyć dla faktur bez VAT',
    checked: true,
  },
};

export const TwoFactorAuth: Story = {
  args: {
    label: 'Uwierzytelnianie dwuskładnikowe',
    description: 'Dodatkowa warstwa bezpieczeństwa dla Twojego konta',
    helperText: 'Wymagane dla kont z uprawnieniami administratora',
    required: true,
    checked: false,
  },
};

export const MarketingConsent: Story = {
  args: {
    label: 'Zgoda marketingowa',
    description: 'Wyrażam zgodę na otrzymywanie informacji marketingowych',
    helperText: 'Możesz zmienić to ustawienie w każdej chwili',
    checked: false,
  },
};

export const DarkMode: Story = {
  args: {
    label: 'Tryb ciemny',
    description: 'Przełącz na ciemny motyw interfejsu',
    size: 'lg',
    checkedIcon: <span>🌙</span>,
    uncheckedIcon: <span>☀️</span>,
    checked: false,
  },
};

// Settings Panel Story
export const SettingsPanel: Story = {
  render: () => (
    <div className="max-w-md space-y-6 p-6 bg-white border border-gray-200 rounded-lg">
      <h3 className="text-lg font-semibold text-gray-900">Ustawienia konta</h3>
      
      <div className="space-y-4">
        <Switch
          label="Powiadomienia email"
          description="Otrzymuj powiadomienia o nowych fakturach"
          checked={true}
        />
        
        <Switch
          label="Powiadomienia SMS"
          description="Otrzymuj ważne powiadomienia przez SMS"
          checked={false}
        />
        
        <Switch
          label="Automatyczne kopie zapasowe"
          description="Twórz kopie zapasowe danych codziennie"
          helperText="Zalecane dla bezpieczeństwa"
          checked={true}
        />
        
        <Switch
          label="Tryb ciemny"
          description="Przełącz na ciemny motyw interfejsu"
          size="lg"
          checkedIcon={<span>🌙</span>}
          uncheckedIcon={<span>☀️</span>}
          checked={false}
        />
        
        <Switch
          label="Uwierzytelnianie dwuskładnikowe"
          description="Dodatkowa warstwa bezpieczeństwa"
          required={true}
          checked={false}
          error={true}
          errorMessage="Wymagane dla kont administratora"
        />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Przykład panelu ustawień z różnymi switchami.',
      },
    },
  },
};

// Accessibility Stories
export const AccessibilityDemo: Story = {
  args: {
    label: 'Switch z pełną dostępnością',
    description: 'Ten switch spełnia standardy WCAG 2.1 Level AA',
    helperText: 'Obsługuje klawiaturę i screen readery',
    'aria-label': 'Dostępny switch',
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
    const [notifications, setNotifications] = React.useState(true);
    const [darkMode, setDarkMode] = React.useState(false);
    
    return (
      <div className="space-y-6">
        <div className="space-y-4">
          <Switch
            label="Główny switch"
            checked={checked}
            onChange={(newChecked) => setChecked(newChecked)}
            description={`Stan: ${checked ? 'włączony' : 'wyłączony'}`}
          />
          
          <Switch
            label="Powiadomienia"
            checked={notifications}
            onChange={(newChecked) => setNotifications(newChecked)}
            description="Kontrola powiadomień"
          />
          
          <Switch
            label="Tryb ciemny"
            checked={darkMode}
            onChange={(newChecked) => setDarkMode(newChecked)}
            size="lg"
            checkedIcon={<span>🌙</span>}
            uncheckedIcon={<span>☀️</span>}
            description="Przełącznik motywu"
          />
        </div>
        
        <div className="p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium mb-2">Stan switchów:</h4>
          <ul className="text-sm space-y-1">
            <li>Główny switch: {checked ? 'włączony' : 'wyłączony'}</li>
            <li>Powiadomienia: {notifications ? 'włączone' : 'wyłączone'}</li>
            <li>Tryb ciemny: {darkMode ? 'włączony' : 'wyłączony'}</li>
          </ul>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Interaktywny przykład pokazujący kontrolę stanu switchów.',
      },
    },
  },
};

// Form Integration Story
export const FormIntegration: Story = {
  render: () => (
    <form onSubmit={(e) => { e.preventDefault(); alert('Form submitted!'); }}>
      <div className="space-y-6">
        <fieldset className="space-y-4">
          <legend className="text-lg font-medium text-gray-900">
            Preferencje powiadomień
          </legend>
          
          <Switch
            name="email-notifications"
            value="enabled"
            label="Powiadomienia email"
            description="Otrzymuj powiadomienia o fakturach na email"
            defaultChecked={true}
          />
          
          <Switch
            name="sms-notifications"
            value="enabled"
            label="Powiadomienia SMS"
            description="Otrzymuj ważne powiadomienia przez SMS"
            defaultChecked={false}
          />
          
          <Switch
            name="push-notifications"
            value="enabled"
            label="Powiadomienia push"
            description="Otrzymuj powiadomienia w przeglądarce"
            defaultChecked={true}
          />
        </fieldset>
        
        <fieldset className="space-y-4">
          <legend className="text-lg font-medium text-gray-900">
            Ustawienia bezpieczeństwa
          </legend>
          
          <Switch
            name="two-factor-auth"
            value="enabled"
            label="Uwierzytelnianie dwuskładnikowe"
            description="Dodatkowa warstwa bezpieczeństwa"
            required={true}
            defaultChecked={false}
          />
          
          <Switch
            name="auto-logout"
            value="enabled"
            label="Automatyczne wylogowanie"
            description="Wyloguj po 30 minutach nieaktywności"
            defaultChecked={true}
          />
        </fieldset>
        
        <button 
          type="submit" 
          className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
        >
          Zapisz ustawienia
        </button>
      </div>
    </form>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Przykład integracji z formularzem - switche z nazwami i wartościami.',
      },
    },
  },
};