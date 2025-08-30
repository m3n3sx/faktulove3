import type { Meta, StoryObj } from '@storybook/react';
import { InvoiceStatusBadge, type InvoiceStatus } from './InvoiceStatusBadge';

const meta: Meta<typeof InvoiceStatusBadge> = {
  title: 'Design System/Business/InvoiceStatusBadge',
  component: InvoiceStatusBadge,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A badge component for displaying invoice status with Polish labels, appropriate colors, and icons for each status type.',
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
            id: 'keyboard-navigation',
            enabled: true,
          },
        ],
      },
    },
  },
  argTypes: {
    status: {
      control: 'select',
      options: ['draft', 'sent', 'viewed', 'paid', 'overdue', 'cancelled', 'corrected'],
      description: 'Invoice status',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Size of the badge',
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof InvoiceStatusBadge>;

// Basic badge
export const Default: Story = {
  args: {
    status: 'sent',
  },
};

// All statuses
export const AllStatuses: Story = {
  render: () => (
    <div className="flex flex-wrap gap-3">
      <InvoiceStatusBadge status="draft" />
      <InvoiceStatusBadge status="sent" />
      <InvoiceStatusBadge status="viewed" />
      <InvoiceStatusBadge status="paid" />
      <InvoiceStatusBadge status="overdue" />
      <InvoiceStatusBadge status="cancelled" />
      <InvoiceStatusBadge status="corrected" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All available invoice statuses with their Polish labels and appropriate colors.',
      },
    },
  },
};

// Different sizes
export const Sizes: Story = {
  render: () => (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium w-16">Small:</span>
        <InvoiceStatusBadge status="paid" size="sm" />
        <InvoiceStatusBadge status="overdue" size="sm" />
        <InvoiceStatusBadge status="sent" size="sm" />
      </div>
      
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium w-16">Medium:</span>
        <InvoiceStatusBadge status="paid" size="md" />
        <InvoiceStatusBadge status="overdue" size="md" />
        <InvoiceStatusBadge status="sent" size="md" />
      </div>
      
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium w-16">Large:</span>
        <InvoiceStatusBadge status="paid" size="lg" />
        <InvoiceStatusBadge status="overdue" size="lg" />
        <InvoiceStatusBadge status="sent" size="lg" />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Badge component comes in three sizes: small, medium, and large.',
      },
    },
  },
};

// Status workflow demonstration
export const StatusWorkflow: Story = {
  render: () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-3">Normalny przepływ faktury</h3>
        <div className="flex items-center gap-2">
          <InvoiceStatusBadge status="draft" />
          <span className="text-neutral-400">→</span>
          <InvoiceStatusBadge status="sent" />
          <span className="text-neutral-400">→</span>
          <InvoiceStatusBadge status="viewed" />
          <span className="text-neutral-400">→</span>
          <InvoiceStatusBadge status="paid" />
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-3">Problematyczne scenariusze</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <InvoiceStatusBadge status="sent" />
            <span className="text-neutral-400">→</span>
            <InvoiceStatusBadge status="overdue" />
            <span className="text-sm text-neutral-600 ml-2">Przekroczony termin płatności</span>
          </div>
          
          <div className="flex items-center gap-2">
            <InvoiceStatusBadge status="draft" />
            <span className="text-neutral-400">→</span>
            <InvoiceStatusBadge status="cancelled" />
            <span className="text-sm text-neutral-600 ml-2">Anulowanie przed wysłaniem</span>
          </div>
          
          <div className="flex items-center gap-2">
            <InvoiceStatusBadge status="paid" />
            <span className="text-neutral-400">→</span>
            <InvoiceStatusBadge status="corrected" />
            <span className="text-sm text-neutral-600 ml-2">Korekta po opłaceniu</span>
          </div>
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Demonstration of typical invoice status workflows in Polish business context.',
      },
    },
  },
};

// Status categories
export const StatusCategories: Story = {
  render: () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-3 text-success-700">Pozytywne statusy</h3>
        <div className="flex flex-wrap gap-2">
          <InvoiceStatusBadge status="paid" />
          <InvoiceStatusBadge status="sent" />
          <InvoiceStatusBadge status="viewed" />
        </div>
        <p className="text-sm text-neutral-600 mt-2">
          Statusy wskazujące na prawidłowy przebieg procesu
        </p>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-3 text-neutral-700">Neutralne statusy</h3>
        <div className="flex flex-wrap gap-2">
          <InvoiceStatusBadge status="draft" />
          <InvoiceStatusBadge status="corrected" />
        </div>
        <p className="text-sm text-neutral-600 mt-2">
          Statusy robocze lub informacyjne
        </p>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-3 text-error-700">Problematyczne statusy</h3>
        <div className="flex flex-wrap gap-2">
          <InvoiceStatusBadge status="overdue" />
          <InvoiceStatusBadge status="cancelled" />
        </div>
        <p className="text-sm text-neutral-600 mt-2">
          Statusy wymagające uwagi lub działania
        </p>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Invoice statuses grouped by their business meaning and urgency.',
      },
    },
  },
};

// In table context
export const InTableContext: Story = {
  render: () => (
    <div className="w-full max-w-4xl">
      <table className="w-full border-collapse border border-neutral-200">
        <thead>
          <tr className="bg-neutral-50">
            <th className="border border-neutral-200 px-4 py-2 text-left">Numer faktury</th>
            <th className="border border-neutral-200 px-4 py-2 text-left">Kontrahent</th>
            <th className="border border-neutral-200 px-4 py-2 text-left">Kwota</th>
            <th className="border border-neutral-200 px-4 py-2 text-left">Status</th>
            <th className="border border-neutral-200 px-4 py-2 text-left">Termin</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border border-neutral-200 px-4 py-2">FV/2024/001</td>
            <td className="border border-neutral-200 px-4 py-2">ABC Sp. z o.o.</td>
            <td className="border border-neutral-200 px-4 py-2">1 230,00 zł</td>
            <td className="border border-neutral-200 px-4 py-2">
              <InvoiceStatusBadge status="paid" size="sm" />
            </td>
            <td className="border border-neutral-200 px-4 py-2">2024-01-15</td>
          </tr>
          <tr>
            <td className="border border-neutral-200 px-4 py-2">FV/2024/002</td>
            <td className="border border-neutral-200 px-4 py-2">XYZ S.A.</td>
            <td className="border border-neutral-200 px-4 py-2">2 460,00 zł</td>
            <td className="border border-neutral-200 px-4 py-2">
              <InvoiceStatusBadge status="overdue" size="sm" />
            </td>
            <td className="border border-neutral-200 px-4 py-2">2024-01-10</td>
          </tr>
          <tr>
            <td className="border border-neutral-200 px-4 py-2">FV/2024/003</td>
            <td className="border border-neutral-200 px-4 py-2">DEF Sp. j.</td>
            <td className="border border-neutral-200 px-4 py-2">615,00 zł</td>
            <td className="border border-neutral-200 px-4 py-2">
              <InvoiceStatusBadge status="sent" size="sm" />
            </td>
            <td className="border border-neutral-200 px-4 py-2">2024-02-01</td>
          </tr>
          <tr>
            <td className="border border-neutral-200 px-4 py-2">FV/2024/004</td>
            <td className="border border-neutral-200 px-4 py-2">GHI Sp. z o.o.</td>
            <td className="border border-neutral-200 px-4 py-2">3 075,00 zł</td>
            <td className="border border-neutral-200 px-4 py-2">
              <InvoiceStatusBadge status="draft" size="sm" />
            </td>
            <td className="border border-neutral-200 px-4 py-2">-</td>
          </tr>
        </tbody>
      </table>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Invoice status badges used in a typical invoice list table.',
      },
    },
  },
};

// With custom styling
export const CustomStyling: Story = {
  render: () => (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-3">Standardowe style</h3>
        <div className="flex flex-wrap gap-2">
          <InvoiceStatusBadge status="paid" />
          <InvoiceStatusBadge status="overdue" />
          <InvoiceStatusBadge status="sent" />
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-3">Z niestandardowymi klasami</h3>
        <div className="flex flex-wrap gap-2">
          <InvoiceStatusBadge 
            status="paid" 
            className="shadow-sm-lg transform hover:scale-105 transition-transform" 
          />
          <InvoiceStatusBadge 
            status="overdue" 
            className="animate-pulse" 
          />
          <InvoiceStatusBadge 
            status="sent" 
            className="border-2 border-dashed" 
          />
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Examples of custom styling applied to status badges.',
      },
    },
  },
};

// Accessibility demonstration
export const AccessibilityFeatures: Story = {
  render: () => (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-3">Dostępność</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <InvoiceStatusBadge status="paid" testId="accessible-paid" />
            <span className="text-sm text-neutral-600">
              Zawiera ikonę i tekst dla lepszej czytelności
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <InvoiceStatusBadge status="overdue" testId="accessible-overdue" />
            <span className="text-sm text-neutral-600">
              Kolory spełniają wymagania kontrastu WCAG
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <InvoiceStatusBadge status="cancelled" testId="accessible-cancelled" />
            <span className="text-sm text-neutral-600">
              Atrybuty data-* dla testów automatycznych
            </span>
          </div>
        </div>
      </div>
      
      <div className="text-sm text-neutral-600 bg-neutral-50 p-3 rounded-md">
        <strong>Funkcje dostępności:</strong>
        <ul className="list-disc list-inside mt-1 space-y-1">
          <li>Wysokie kontrasty kolorów (WCAG AA)</li>
          <li>Ikony wspierające tekst</li>
          <li>Semantyczne atrybuty HTML</li>
          <li>Czytelne polskie etykiety</li>
        </ul>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Accessibility features including high contrast colors, icons, and semantic attributes.',
      },
    },
  },
};

// Interactive playground
export const Playground: Story = {
  args: {
    status: 'sent',
    size: 'md',
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive playground to test different badge configurations.',
      },
    },
  },
};