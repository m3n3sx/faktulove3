import type { Meta, StoryObj } from '@storybook/react';
import { action } from '@storybook/addon-actions';
// Import your component here
// import { YourComponent } from './YourComponent';

// Replace with your component
const YourComponent = ({ children, ...props }: any) => <div {...props}>{children}</div>;

const meta: Meta<typeof YourComponent> = {
  title: 'Design System/Category/YourComponent',
  component: YourComponent,
  parameters: {
    layout: 'centered', // or 'padded', 'fullscreen'
    docs: {
      description: {
        component: 'Brief description of what this component does and its main use cases.',
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
          // Add other relevant accessibility rules
          // { id: 'label', enabled: true },
          // { id: 'button-name', enabled: true },
          // { id: 'aria-input-field-name', enabled: true },
        ],
      },
    },
  },
  argTypes: {
    // Define controls for component props
    variant: {
      control: 'select',
      options: ['primary', 'secondary'],
      description: 'Visual variant of the component',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Size of the component',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the component is disabled',
    },
    onClick: {
      action: 'clicked',
      description: 'Click handler',
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof YourComponent>;

// Basic story
export const Default: Story = {
  args: {
    children: 'Default content',
    // Add default props here
  },
};

// Different variants
export const Variants: Story = {
  render: () => (
    <div className="flex gap-4">
      <YourComponent variant="primary">Primary</YourComponent>
      <YourComponent variant="secondary">Secondary</YourComponent>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Different visual variants of the component.',
      },
    },
  },
};

// Different sizes
export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <YourComponent size="sm">Small</YourComponent>
      <YourComponent size="md">Medium</YourComponent>
      <YourComponent size="lg">Large</YourComponent>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Component comes in different sizes.',
      },
    },
  },
};

// Different states
export const States: Story = {
  render: () => (
    <div className="space-y-4">
      <div className="flex gap-4">
        <YourComponent>Normal</YourComponent>
        <YourComponent disabled>Disabled</YourComponent>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Different states the component can have.',
      },
    },
  },
};

// Polish business context (if applicable)
export const PolishBusinessContext: Story = {
  render: () => (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-2">Kontekst biznesowy</h3>
        <YourComponent>Polski tekst</YourComponent>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Component used in Polish business context with appropriate formatting and labels.',
      },
    },
  },
};

// Accessibility demonstration
export const AccessibilityFeatures: Story = {
  render: () => (
    <div className="space-y-4">
      <div>
        <label htmlFor="accessible-component" className="block text-sm font-medium mb-1">
          Accessible Component
        </label>
        <YourComponent 
          id="accessible-component"
          aria-label="Accessible component example"
          aria-describedby="component-description"
        >
          Accessible Content
        </YourComponent>
        <p id="component-description" className="text-sm text-neutral-600 mt-1">
          This component includes proper accessibility features.
        </p>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Demonstration of accessibility features including proper labeling and ARIA attributes.',
      },
    },
  },
};

// Interactive playground
export const Playground: Story = {
  args: {
    children: 'Playground Content',
    variant: 'primary',
    size: 'md',
    disabled: false,
    onClick: action('playground-clicked'),
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive playground to test different component configurations.',
      },
    },
  },
};

// Real-world usage example
export const RealWorldExample: Story = {
  render: () => (
    <div className="max-w-md mx-auto p-6 bg-white border border-neutral-200 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Real-world Example</h2>
      <p className="text-neutral-600 mb-4">
        This shows how the component would be used in a real application.
      </p>
      <YourComponent>
        Example Usage
      </YourComponent>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Example of how this component would be used in a real application.',
      },
    },
  },
};