import type { Meta, StoryObj } from '@storybook/react';
import { ThemeControls } from './ThemeControls';
import { ThemeProvider } from '../../providers/ThemeProvider';

const meta: Meta<typeof ThemeControls> = {
  title: 'Design System/Patterns/ThemeControls',
  component: ThemeControls,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Theme controls component for managing theme settings including dark mode, high contrast, and reduced motion preferences.',
      },
    },
  },
  decorators: [
    (Story) => (
      <ThemeProvider>
        <div className="w-96">
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
  argTypes: {
    showAdvanced: {
      control: 'boolean',
      description: 'Show advanced theme controls and status information',
    },
    compact: {
      control: 'boolean',
      description: 'Use compact layout with icon buttons',
    },
    className: {
      control: 'text',
      description: 'Additional CSS classes',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ThemeControls>;

export const Default: Story = {
  args: {},
};

export const Advanced: Story = {
  args: {
    showAdvanced: true,
  },
};

export const Compact: Story = {
  args: {
    compact: true,
  },
  decorators: [
    (Story) => (
      <ThemeProvider>
        <div className="flex items-center justify-center p-4 bg-background-secondary rounded-lg">
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
};

export const CompactAdvanced: Story = {
  args: {
    compact: true,
    showAdvanced: true,
  },
  decorators: [
    (Story) => (
      <ThemeProvider>
        <div className="flex items-center justify-center p-4 bg-background-secondary rounded-lg">
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
};

// Interactive story to demonstrate theme switching
export const Interactive: Story = {
  args: {
    showAdvanced: true,
  },
  render: (args) => (
    <ThemeProvider>
      <div className="space-y-6">
        <ThemeControls {...args} />
        
        {/* Demo content to show theme changes */}
        <div className="p-6 bg-background-primary border border-border-default rounded-lg">
          <h3 className="text-lg font-semibold text-text-primary mb-2">
            Przykład treści
          </h3>
          <p className="text-text-secondary mb-4">
            Ta sekcja pokazuje jak zmiany motywu wpływają na wygląd treści.
            Spróbuj zmienić ustawienia motywu powyżej, aby zobaczyć efekt.
          </p>
          
          <div className="flex gap-2">
            <button className="px-4 py-2 bg-interactive text-white rounded-md hover:bg-interactive-hover transition-colors">
              Przycisk główny
            </button>
            <button className="px-4 py-2 border border-border-default text-text-primary rounded-md hover:bg-background-hover transition-colors">
              Przycisk drugorzędny
            </button>
          </div>
        </div>
        
        {/* Status indicators */}
        <div className="grid grid-cols-3 gap-4">
          <div className="p-3 bg-status-success-background border border-status-success-border rounded-lg">
            <div className="text-status-success font-medium">Sukces</div>
            <div className="text-xs text-text-muted">Operacja zakończona</div>
          </div>
          
          <div className="p-3 bg-status-warning-background border border-status-warning-border rounded-lg">
            <div className="text-status-warning font-medium">Ostrzeżenie</div>
            <div className="text-xs text-text-muted">Wymaga uwagi</div>
          </div>
          
          <div className="p-3 bg-status-error-background border border-status-error-border rounded-lg">
            <div className="text-status-error font-medium">Błąd</div>
            <div className="text-xs text-text-muted">Wystąpił problem</div>
          </div>
        </div>
      </div>
    </ThemeProvider>
  ),
};

// Polish business context story
export const PolishBusiness: Story = {
  args: {
    showAdvanced: true,
  },
  render: (args) => (
    <ThemeProvider>
      <div className="space-y-6">
        <ThemeControls {...args} />
        
        {/* Polish business demo content */}
        <div className="p-6 bg-background-primary border border-border-default rounded-lg">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Faktura nr FV/2025/001
          </h3>
          
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="font-medium text-text-primary mb-2">Sprzedawca</h4>
              <div className="text-sm text-text-secondary space-y-1">
                <div>FaktuLove Sp. z o.o.</div>
                <div>ul. Przykładowa 123</div>
                <div>00-001 Warszawa</div>
                <div className="font-mono">NIP: 123-456-78-90</div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-text-primary mb-2">Nabywca</h4>
              <div className="text-sm text-text-secondary space-y-1">
                <div>Przykładowy Klient Sp. z o.o.</div>
                <div>ul. Kliencka 456</div>
                <div>00-002 Kraków</div>
                <div className="font-mono">NIP: 987-654-32-10</div>
              </div>
            </div>
          </div>
          
          <div className="border border-border-default rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-background-secondary">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-medium text-text-primary">Usługa</th>
                  <th className="px-4 py-2 text-right text-sm font-medium text-text-primary">Cena netto</th>
                  <th className="px-4 py-2 text-right text-sm font-medium text-text-primary">VAT</th>
                  <th className="px-4 py-2 text-right text-sm font-medium text-text-primary">Cena brutto</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-border-default">
                  <td className="px-4 py-2 text-sm text-text-primary">Usługi księgowe</td>
                  <td className="px-4 py-2 text-right text-sm font-mono text-currency-positive">1 000,00 zł</td>
                  <td className="px-4 py-2 text-right text-sm text-vat-standard">23%</td>
                  <td className="px-4 py-2 text-right text-sm font-mono font-medium text-currency-positive">1 230,00 zł</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div className="mt-4 flex justify-end">
            <div className="bg-invoice-paid-background border border-status-success-border px-3 py-1 rounded-full">
              <span className="text-sm font-medium text-invoice-paid">Opłacona</span>
            </div>
          </div>
        </div>
      </div>
    </ThemeProvider>
  ),
};