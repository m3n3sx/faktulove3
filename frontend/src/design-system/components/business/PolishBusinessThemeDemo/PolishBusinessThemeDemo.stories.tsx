import type { Meta, StoryObj } from '@storybook/react';
import { PolishBusinessThemeDemo } from './PolishBusinessThemeDemo';
import { ThemeProvider } from '../../../providers/ThemeProvider';
import { ThemeControls } from '../../patterns/ThemeControls/ThemeControls';

const meta: Meta<typeof PolishBusinessThemeDemo> = {
  title: 'Design System/Business/PolishBusinessThemeDemo',
  component: PolishBusinessThemeDemo,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Demonstration of Polish business theming with invoice statuses, VAT rates, currency formatting, and compliance indicators.',
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
};

export default meta;
type Story = StoryObj<typeof PolishBusinessThemeDemo>;

export const Default: Story = {
  args: {},
};

export const WithThemeControls: Story = {
  args: {},
  render: (args) => (
    <ThemeProvider>
      <div className="min-h-screen bg-background-primary">
        {/* Fixed theme controls */}
        <div className="sticky top-0 z-10 bg-background-primary border-b border-border-default p-4">
          <div className="max-w-4xl mx-auto">
            <ThemeControls compact showAdvanced />
          </div>
        </div>
        
        {/* Demo content */}
        <div className="p-6">
          <PolishBusinessThemeDemo {...args} />
        </div>
      </div>
    </ThemeProvider>
  ),
};

export const DarkMode: Story = {
  args: {},
  decorators: [
    (Story) => (
      <ThemeProvider defaultMode="dark">
        <div className="min-h-screen bg-background-primary p-6">
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
};

export const HighContrast: Story = {
  args: {},
  decorators: [
    (Story) => (
      <ThemeProvider defaultContrast="high">
        <div className="min-h-screen bg-background-primary p-6">
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
};

export const DarkHighContrast: Story = {
  args: {},
  decorators: [
    (Story) => (
      <ThemeProvider defaultMode="dark" defaultContrast="high">
        <div className="min-h-screen bg-background-primary p-6">
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
};