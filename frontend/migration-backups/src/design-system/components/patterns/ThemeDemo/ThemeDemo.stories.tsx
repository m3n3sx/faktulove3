import type { Meta, StoryObj } from '@storybook/react';
import { ThemeDemo } from './ThemeDemo';
import { ThemeProvider } from '../../providers/ThemeProvider';
import { ThemeControls } from '../ThemeControls/ThemeControls';

const meta: Meta<typeof ThemeDemo> = {
  title: 'Design System/Patterns/ThemeDemo',
  component: ThemeDemo,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Comprehensive theme demonstration component showing all theme features including dark mode, high contrast, and Polish business-specific styling.',
      },
    },
  },
  decorators: [
    (Story) => (
      <ThemeProvider>
        <div className="min-h-screen bg-background-primary p-6">
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
  argTypes: {
    showSystemInfo: {
      control: 'boolean',
      description: 'Show system preference information',
    },
    showAccessibilityScore: {
      control: 'boolean',
      description: 'Show accessibility score and recommendations',
    },
    className: {
      control: 'text',
      description: 'Additional CSS classes',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ThemeDemo>;

export const Default: Story = {
  args: {
    showSystemInfo: true,
    showAccessibilityScore: true,
  },
};

export const BasicDemo: Story = {
  args: {
    showSystemInfo: false,
    showAccessibilityScore: false,
  },
};

export const WithSystemInfo: Story = {
  args: {
    showSystemInfo: true,
    showAccessibilityScore: false,
  },
};

export const WithAccessibilityScore: Story = {
  args: {
    showSystemInfo: false,
    showAccessibilityScore: true,
  },
};

// Interactive story with theme controls
export const Interactive: Story = {
  args: {
    showSystemInfo: true,
    showAccessibilityScore: true,
  },
  render: (args) => (
    <ThemeProvider>
      <div className="min-h-screen bg-background-primary">
        {/* Fixed theme controls */}
        <div className="sticky top-0 z-10 bg-background-primary border-b border-border-default p-4">
          <ThemeControls compact showAdvanced />
        </div>
        
        {/* Main demo content */}
        <div className="p-6">
          <ThemeDemo {...args} />
        </div>
      </div>
    </ThemeProvider>
  ),
};

// Dark mode focused story
export const DarkModeShowcase: Story = {
  args: {
    showSystemInfo: true,
    showAccessibilityScore: true,
  },
  decorators: [
    (Story) => (
      <ThemeProvider defaultMode="dark">
        <div className="min-h-screen bg-background-primary p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              Ciemny motyw - Prezentacja
            </h1>
            <p className="text-text-secondary">
              Demonstracja wszystkich komponentów w ciemnym motywie z polskimi wzorcami biznesowymi.
            </p>
          </div>
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
};

// High contrast focused story
export const HighContrastShowcase: Story = {
  args: {
    showSystemInfo: true,
    showAccessibilityScore: true,
  },
  decorators: [
    (Story) => (
      <ThemeProvider defaultContrast="high">
        <div className="min-h-screen bg-background-primary p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              Wysoki kontrast - Prezentacja
            </h1>
            <p className="text-text-secondary">
              Demonstracja wszystkich komponentów w trybie wysokiego kontrastu dla lepszej dostępności.
            </p>
          </div>
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
};

// Reduced motion focused story
export const ReducedMotionShowcase: Story = {
  args: {
    showSystemInfo: true,
    showAccessibilityScore: true,
  },
  decorators: [
    (Story) => (
      <ThemeProvider defaultReducedMotion={true}>
        <div className="min-h-screen bg-background-primary p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              Ograniczone animacje - Prezentacja
            </h1>
            <p className="text-text-secondary">
              Demonstracja wszystkich komponentów z wyłączonymi animacjami dla lepszej dostępności.
            </p>
          </div>
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
};

// Polish business context story
export const PolishBusinessContext: Story = {
  args: {
    showSystemInfo: true,
    showAccessibilityScore: true,
  },
  render: (args) => (
    <ThemeProvider>
      <div className="min-h-screen bg-background-primary">
        {/* Business header */}
        <div className="bg-polish-business-primary text-white p-6">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-2">FaktuLove</h1>
            <p className="text-primary-100">
              System zarządzania fakturami dla polskich przedsiębiorców
            </p>
          </div>
        </div>
        
        {/* Theme controls */}
        <div className="bg-background-secondary border-b border-border-default p-4">
          <div className="max-w-4xl mx-auto">
            <ThemeControls compact showAdvanced />
          </div>
        </div>
        
        {/* Main content */}
        <div className="max-w-4xl mx-auto p-6">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-text-primary mb-2">
              Prezentacja systemu motywów
            </h2>
            <p className="text-text-secondary">
              Kompletna demonstracja wszystkich funkcji motywów dostosowanych do polskiego rynku biznesowego.
            </p>
          </div>
          
          <ThemeDemo {...args} />
        </div>
        
        {/* Business footer */}
        <div className="bg-background-secondary border-t border-border-default p-6 mt-12">
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-text-muted text-sm">
              © 2025 FaktuLove. Wszystkie prawa zastrzeżone.
            </p>
          </div>
        </div>
      </div>
    </ThemeProvider>
  ),
};

// Accessibility testing story
export const AccessibilityTesting: Story = {
  args: {
    showSystemInfo: true,
    showAccessibilityScore: true,
  },
  parameters: {
    a11y: {
      config: {
        rules: [
          { id: 'color-contrast', enabled: true },
          { id: 'focus-order-semantics', enabled: true },
          { id: 'keyboard-navigation', enabled: true },
        ],
      },
    },
  },
  render: (args) => (
    <ThemeProvider>
      <div className="min-h-screen bg-background-primary p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-text-primary mb-2">
            Test dostępności motywów
          </h1>
          <p className="text-text-secondary mb-4">
            Ta strona testuje wszystkie aspekty dostępności systemu motywów.
          </p>
          
          {/* Accessibility instructions */}
          <div className="bg-status-info-background border border-status-info-border rounded-lg p-4 mb-6">
            <h3 className="text-status-info font-medium mb-2">Instrukcje testowania:</h3>
            <ul className="text-sm text-text-secondary space-y-1">
              <li>• Użyj klawiatury Tab do nawigacji między elementami</li>
              <li>• Sprawdź kontrast kolorów w różnych motywach</li>
              <li>• Przetestuj z czytnikiem ekranu</li>
              <li>• Sprawdź responsywność na różnych urządzeniach</li>
            </ul>
          </div>
        </div>
        
        <ThemeDemo {...args} />
      </div>
    </ThemeProvider>
  ),
};