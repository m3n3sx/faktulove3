import type { Meta, StoryObj } from '@storybook/react';
import { Grid } from './Grid';

const meta: Meta<typeof Grid> = {
  title: 'Design System/Layouts/Grid',
  component: Grid,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'A flexible CSS Grid layout component with responsive breakpoints, auto-fit capabilities, and customizable gaps.',
      },
    },
    a11y: {
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true,
          },
        ],
      },
    },
  },
  argTypes: {
    cols: {
      control: { type: 'number', min: 1, max: 12 },
      description: 'Number of columns or responsive column configuration',
    },
    gap: {
      control: { type: 'number', min: 0, max: 12 },
      description: 'Gap between grid items',
    },
    rows: {
      control: { type: 'number', min: 1, max: 6 },
      description: 'Number of rows or auto',
    },
    autoFit: {
      control: 'boolean',
      description: 'Enable auto-fit grid behavior',
    },
    minItemWidth: {
      control: 'text',
      description: 'Minimum width for auto-fit items',
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof Grid>;

// Demo item component
const GridItem: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className = '' 
}) => (
  <div className={`bg-primary-100 border border-primary-200 rounded-lg p-4 text-center text-primary-800 font-medium ${className}`}>
    {children}
  </div>
);

// Basic grid
export const Default: Story = {
  render: (args) => (
    <Grid {...args}>
      <GridItem>Item 1</GridItem>
      <GridItem>Item 2</GridItem>
      <GridItem>Item 3</GridItem>
      <GridItem>Item 4</GridItem>
      <GridItem>Item 5</GridItem>
      <GridItem>Item 6</GridItem>
    </Grid>
  ),
  args: {
    cols: 3,
    gap: 4,
  },
};

// Different column counts
export const ColumnVariations: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">2 kolumny</h3>
        <Grid cols={2} gap={4}>
          <GridItem>Item 1</GridItem>
          <GridItem>Item 2</GridItem>
          <GridItem>Item 3</GridItem>
          <GridItem>Item 4</GridItem>
        </Grid>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">3 kolumny</h3>
        <Grid cols={3} gap={4}>
          <GridItem>Item 1</GridItem>
          <GridItem>Item 2</GridItem>
          <GridItem>Item 3</GridItem>
          <GridItem>Item 4</GridItem>
          <GridItem>Item 5</GridItem>
          <GridItem>Item 6</GridItem>
        </Grid>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">4 kolumny</h3>
        <Grid cols={4} gap={4}>
          <GridItem>Item 1</GridItem>
          <GridItem>Item 2</GridItem>
          <GridItem>Item 3</GridItem>
          <GridItem>Item 4</GridItem>
          <GridItem>Item 5</GridItem>
          <GridItem>Item 6</GridItem>
          <GridItem>Item 7</GridItem>
          <GridItem>Item 8</GridItem>
        </Grid>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Grid with different column counts.',
      },
    },
  },
};

// Different gaps
export const GapVariations: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">Bez odstępu (gap: 0)</h3>
        <Grid cols={3} gap={0}>
          <GridItem>Item 1</GridItem>
          <GridItem>Item 2</GridItem>
          <GridItem>Item 3</GridItem>
        </Grid>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">Mały odstęp (gap: 2)</h3>
        <Grid cols={3} gap={2}>
          <GridItem>Item 1</GridItem>
          <GridItem>Item 2</GridItem>
          <GridItem>Item 3</GridItem>
        </Grid>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">Średni odstęp (gap: 4)</h3>
        <Grid cols={3} gap={4}>
          <GridItem>Item 1</GridItem>
          <GridItem>Item 2</GridItem>
          <GridItem>Item 3</GridItem>
        </Grid>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">Duży odstęp (gap: 8)</h3>
        <Grid cols={3} gap={8}>
          <GridItem>Item 1</GridItem>
          <GridItem>Item 2</GridItem>
          <GridItem>Item 3</GridItem>
        </Grid>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Grid with different gap sizes.',
      },
    },
  },
};

// Responsive grid
export const ResponsiveGrid: Story = {
  render: () => (
    <div>
      <h3 className="text-lg font-semibold mb-4">Responsywna siatka</h3>
      <p className="text-sm text-neutral-600 mb-4">
        Zmień rozmiar okna aby zobaczyć efekt: 1 kolumna na mobile, 2 na tablet, 4 na desktop
      </p>
      <Grid cols={{ xs: 1, sm: 2, md: 3, lg: 4 }} gap={4}>
        <GridItem>Responsywny 1</GridItem>
        <GridItem>Responsywny 2</GridItem>
        <GridItem>Responsywny 3</GridItem>
        <GridItem>Responsywny 4</GridItem>
        <GridItem>Responsywny 5</GridItem>
        <GridItem>Responsywny 6</GridItem>
        <GridItem>Responsywny 7</GridItem>
        <GridItem>Responsywny 8</GridItem>
      </Grid>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Responsive grid that adapts to different screen sizes.',
      },
    },
  },
};

// Auto-fit grid
export const AutoFitGrid: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">Auto-fit (min 200px)</h3>
        <p className="text-sm text-neutral-600 mb-4">
          Elementy automatycznie dopasowują się do dostępnej przestrzeni
        </p>
        <Grid autoFit minItemWidth="200px" gap={4}>
          <GridItem>Auto 1</GridItem>
          <GridItem>Auto 2</GridItem>
          <GridItem>Auto 3</GridItem>
          <GridItem>Auto 4</GridItem>
          <GridItem>Auto 5</GridItem>
        </Grid>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">Auto-fit (min 300px)</h3>
        <Grid autoFit minItemWidth="300px" gap={4}>
          <GridItem>Szerszy 1</GridItem>
          <GridItem>Szerszy 2</GridItem>
          <GridItem>Szerszy 3</GridItem>
          <GridItem>Szerszy 4</GridItem>
        </Grid>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Auto-fit grid that automatically adjusts the number of columns based on available space.',
      },
    },
  },
};

// Card grid layout
export const CardGrid: Story = {
  render: () => (
    <div>
      <h3 className="text-lg font-semibold mb-4">Siatka kart</h3>
      <Grid cols={{ xs: 1, sm: 2, lg: 3 }} gap={6}>
        <div className="bg-white border border-neutral-200 rounded-lg p-6 shadow-sm">
          <h4 className="text-lg font-semibold mb-2">Faktura FV/2024/001</h4>
          <p className="text-neutral-600 mb-4">ABC Sp. z o.o.</p>
          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold text-primary-600">1 230,00 zł</span>
            <span className="bg-success-100 text-success-800 px-2 py-1 rounded text-sm">Opłacona</span>
          </div>
        </div>
        
        <div className="bg-white border border-neutral-200 rounded-lg p-6 shadow-sm">
          <h4 className="text-lg font-semibold mb-2">Faktura FV/2024/002</h4>
          <p className="text-neutral-600 mb-4">XYZ S.A.</p>
          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold text-primary-600">2 460,00 zł</span>
            <span className="bg-error-100 text-error-800 px-2 py-1 rounded text-sm">Przeterminowana</span>
          </div>
        </div>
        
        <div className="bg-white border border-neutral-200 rounded-lg p-6 shadow-sm">
          <h4 className="text-lg font-semibold mb-2">Faktura FV/2024/003</h4>
          <p className="text-neutral-600 mb-4">DEF Sp. j.</p>
          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold text-primary-600">615,00 zł</span>
            <span className="bg-primary-100 text-primary-800 px-2 py-1 rounded text-sm">Wysłana</span>
          </div>
        </div>
        
        <div className="bg-white border border-neutral-200 rounded-lg p-6 shadow-sm">
          <h4 className="text-lg font-semibold mb-2">Faktura FV/2024/004</h4>
          <p className="text-neutral-600 mb-4">GHI Sp. z o.o.</p>
          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold text-primary-600">3 075,00 zł</span>
            <span className="bg-neutral-100 text-neutral-800 px-2 py-1 rounded text-sm">Szkic</span>
          </div>
        </div>
      </Grid>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Real-world example of using Grid for invoice cards layout.',
      },
    },
  },
};

// Dashboard layout
export const DashboardLayout: Story = {
  render: () => (
    <div>
      <h3 className="text-lg font-semibold mb-4">Layout dashboardu</h3>
      <Grid cols={{ xs: 1, sm: 2, lg: 4 }} gap={4} className="mb-6">
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-primary-700 mb-1">Faktury wysłane</h4>
          <p className="text-2xl font-bold text-primary-900">24</p>
        </div>
        <div className="bg-success-50 border border-success-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-success-700 mb-1">Opłacone</h4>
          <p className="text-2xl font-bold text-success-900">18</p>
        </div>
        <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-warning-700 mb-1">Oczekujące</h4>
          <p className="text-2xl font-bold text-warning-900">4</p>
        </div>
        <div className="bg-error-50 border border-error-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-error-700 mb-1">Przeterminowane</h4>
          <p className="text-2xl font-bold text-error-900">2</p>
        </div>
      </Grid>
      
      <Grid cols={{ xs: 1, lg: 2 }} gap={6}>
        <div className="bg-white border border-neutral-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold mb-4">Ostatnie faktury</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span>FV/2024/001</span>
              <span className="text-success-600 font-medium">1 230,00 zł</span>
            </div>
            <div className="flex justify-between items-center">
              <span>FV/2024/002</span>
              <span className="text-error-600 font-medium">2 460,00 zł</span>
            </div>
            <div className="flex justify-between items-center">
              <span>FV/2024/003</span>
              <span className="text-primary-600 font-medium">615,00 zł</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white border border-neutral-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold mb-4">Przychody miesięczne</h4>
          <div className="h-32 bg-neutral-100 rounded flex items-center justify-center text-neutral-500">
            Wykres przychodów
          </div>
        </div>
      </Grid>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Complex dashboard layout using nested grids.',
      },
    },
  },
};

// Interactive playground
export const Playground: Story = {
  render: (args) => (
    <Grid {...args}>
      <GridItem>Item 1</GridItem>
      <GridItem>Item 2</GridItem>
      <GridItem>Item 3</GridItem>
      <GridItem>Item 4</GridItem>
      <GridItem>Item 5</GridItem>
      <GridItem>Item 6</GridItem>
      <GridItem>Item 7</GridItem>
      <GridItem>Item 8</GridItem>
      <GridItem>Item 9</GridItem>
    </Grid>
  ),
  args: {
    cols: 3,
    gap: 4,
    autoFit: false,
    minItemWidth: '250px',
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive playground to test different grid configurations.',
      },
    },
  },
};