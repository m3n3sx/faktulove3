// Button Component Stories
import type { Meta, StoryObj } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import { Button } from './Button';
import { 
  PolishBusinessButton, 
  InvoiceActionButton, 
  VATRateButton, 
  StatusToggleButton 
} from './PolishBusinessButton';

// Icons for stories
const PlusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
);

const DownloadIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="7,10 12,15 17,10"></polyline>
    <line x1="12" y1="15" x2="12" y2="3"></line>
  </svg>
);

const meta: Meta<typeof Button> = {
  title: 'Design System/Primitives/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants, sizes, and states. Includes Polish business-specific variants for invoice management.',
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
            id: 'button-name',
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
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost', 'danger'],
      description: 'Visual variant of the button',
    },
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      description: 'Size of the button',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the button is disabled',
    },
    loading: {
      control: 'boolean',
      description: 'Whether the button is in loading state',
    },
    fullWidth: {
      control: 'boolean',
      description: 'Whether the button takes full width',
    },
    onClick: {
      action: 'clicked',
      description: 'Click handler',
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof Button>;

// Basic Button Stories
export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Primary Button',
    onClick: action('primary-clicked'),
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Secondary Button',
    onClick: action('secondary-clicked'),
  },
};

export const Ghost: Story = {
  args: {
    variant: 'ghost',
    children: 'Ghost Button',
    onClick: action('ghost-clicked'),
  },
};

export const Danger: Story = {
  args: {
    variant: 'danger',
    children: 'Danger Button',
    onClick: action('danger-clicked'),
  },
};

// Size Variants
export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button size="xs" onClick={action('xs-clicked')}>Extra Small</Button>
      <Button size="sm" onClick={action('sm-clicked')}>Small</Button>
      <Button size="md" onClick={action('md-clicked')}>Medium</Button>
      <Button size="lg" onClick={action('lg-clicked')}>Large</Button>
      <Button size="xl" onClick={action('xl-clicked')}>Extra Large</Button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Buttons come in five different sizes to accommodate various use cases.',
      },
    },
  },
};

// States
export const States: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <Button onClick={action('normal-clicked')}>Normal</Button>
        <Button disabled onClick={action('disabled-clicked')}>Disabled</Button>
        <Button loading onClick={action('loading-clicked')}>Loading</Button>
      </div>
      <div className="flex items-center gap-4">
        <Button variant="secondary" onClick={action('secondary-normal-clicked')}>Normal</Button>
        <Button variant="secondary" disabled onClick={action('secondary-disabled-clicked')}>Disabled</Button>
        <Button variant="secondary" loading onClick={action('secondary-loading-clicked')}>Loading</Button>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Buttons support normal, disabled, and loading states across all variants.',
      },
    },
  },
};

// With Icons
export const WithIcons: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <Button startIcon={<PlusIcon />} onClick={action('start-icon-clicked')}>
          Add Item
        </Button>
        <Button endIcon={<DownloadIcon />} onClick={action('end-icon-clicked')}>
          Download
        </Button>
        <Button 
          startIcon={<PlusIcon />} 
          endIcon={<DownloadIcon />} 
          onClick={action('both-icons-clicked')}
        >
          Both Icons
        </Button>
      </div>
      <div className="flex items-center gap-4">
        <Button 
          variant="secondary" 
          startIcon={<PlusIcon />} 
          loading 
          onClick={action('loading-with-icon-clicked')}
        >
          Loading with Icon
        </Button>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Buttons can include start and end icons. Loading state replaces start icon with spinner.',
      },
    },
  },
};

// Full Width
export const FullWidth: Story = {
  render: () => (
    <div className="w-80 space-y-4">
      <Button fullWidth onClick={action('full-width-primary-clicked')}>
        Full Width Primary
      </Button>
      <Button variant="secondary" fullWidth onClick={action('full-width-secondary-clicked')}>
        Full Width Secondary
      </Button>
      <Button variant="ghost" fullWidth onClick={action('full-width-ghost-clicked')}>
        Full Width Ghost
      </Button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Buttons can take the full width of their container.',
      },
    },
  },
};

// Polish Business Buttons
export const PolishBusinessVariants: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <PolishBusinessButton variant="invoice" onClick={action('invoice-clicked')}>
          Utwórz Fakturę
        </PolishBusinessButton>
        <PolishBusinessButton variant="contractor" onClick={action('contractor-clicked')}>
          Kontrahenci
        </PolishBusinessButton>
        <PolishBusinessButton variant="payment" onClick={action('payment-clicked')}>
          Płatności
        </PolishBusinessButton>
      </div>
      <div className="flex items-center gap-4">
        <PolishBusinessButton variant="export" onClick={action('export-clicked')}>
          Eksportuj
        </PolishBusinessButton>
        <PolishBusinessButton variant="print" onClick={action('print-clicked')}>
          Drukuj
        </PolishBusinessButton>
        <PolishBusinessButton variant="cancel" onClick={action('cancel-clicked')}>
          Anuluj
        </PolishBusinessButton>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Polish business-specific button variants with appropriate styling and ARIA labels.',
      },
    },
  },
};

// Invoice Action Buttons
export const InvoiceActions: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <InvoiceActionButton action="create" onClick={action('create-clicked')}>
          Utwórz
        </InvoiceActionButton>
        <InvoiceActionButton action="edit" onClick={action('edit-clicked')}>
          Edytuj
        </InvoiceActionButton>
        <InvoiceActionButton action="send" onClick={action('send-clicked')}>
          Wyślij
        </InvoiceActionButton>
      </div>
      <div className="flex items-center gap-4">
        <InvoiceActionButton action="pay" onClick={action('pay-clicked')}>
          Opłać
        </InvoiceActionButton>
        <InvoiceActionButton action="duplicate" onClick={action('duplicate-clicked')}>
          Duplikuj
        </InvoiceActionButton>
        <InvoiceActionButton action="cancel" onClick={action('cancel-clicked')}>
          Anuluj
        </InvoiceActionButton>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Specialized buttons for invoice actions with Polish labels and appropriate variants.',
      },
    },
  },
};

// VAT Rate Buttons
export const VATRates: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <VATRateButton rate={0.23} selected={true} onClick={action('vat-23-clicked')} />
        <VATRateButton rate={0.08} onClick={action('vat-8-clicked')} />
        <VATRateButton rate={0.05} onClick={action('vat-5-clicked')} />
        <VATRateButton rate={0} onClick={action('vat-0-clicked')} />
        <VATRateButton rate={-1} onClick={action('vat-exempt-clicked')} />
      </div>
      <div className="text-sm text-gray-600">
        Standard Polish VAT rates: 23% (selected), 8%, 5%, 0%, and exempt (zw.)
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'VAT rate selection buttons with Polish formatting and proper ARIA labels.',
      },
    },
  },
};

// Status Toggle Buttons
export const StatusToggles: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <StatusToggleButton 
          status="draft" 
          onStatusChange={action('status-changed')}
        />
        <StatusToggleButton 
          status="sent" 
          onStatusChange={action('status-changed')}
        />
        <StatusToggleButton 
          status="paid" 
          onStatusChange={action('status-changed')}
        />
      </div>
      <div className="flex items-center gap-4">
        <StatusToggleButton 
          status="overdue" 
          onStatusChange={action('status-changed')}
        />
        <StatusToggleButton 
          status="cancelled" 
          onStatusChange={action('status-changed')}
        />
      </div>
      <div className="text-sm text-gray-600">
        Click buttons to change invoice status (some transitions are automatic)
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Invoice status toggle buttons with Polish labels and smart state transitions.',
      },
    },
  },
};

// Accessibility Demo
export const AccessibilityFeatures: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <Button 
          aria-label="Dodaj nowy element do listy"
          startIcon={<PlusIcon />}
          onClick={action('accessible-clicked')}
        >
          Dodaj
        </Button>
        <Button 
          aria-describedby="help-text"
          onClick={action('described-clicked')}
        >
          Pomoc
        </Button>
        <Button 
          aria-pressed={true}
          onClick={action('toggle-clicked')}
        >
          Przełącznik
        </Button>
      </div>
      <div id="help-text" className="text-sm text-gray-600">
        Ten przycisk otwiera panel pomocy
      </div>
      <div className="text-sm text-gray-600">
        All buttons include proper ARIA labels, keyboard navigation, and screen reader support.
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Demonstration of accessibility features including ARIA labels, descriptions, and keyboard navigation.',
      },
    },
  },
};

// Interactive Playground
export const Playground: Story = {
  args: {
    variant: 'primary',
    size: 'md',
    children: 'Playground Button',
    disabled: false,
    loading: false,
    fullWidth: false,
    onClick: action('playground-clicked'),
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive playground to test different button configurations.',
      },
    },
  },
};