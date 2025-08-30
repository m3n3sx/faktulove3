import type { Meta, StoryObj } from '@storybook/react';
import { Progress } from './Progress';

const meta: Meta<typeof Progress> = {
  title: 'Primitives/Progress',
  component: Progress,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    value: {
      control: { type: 'range', min: 0, max: 100, step: 1 },
    },
    variant: {
      control: 'select',
      options: ['default', 'success', 'warning', 'error'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    value: 50,
  },
};

export const WithLabel: Story = {
  args: {
    value: 75,
    showLabel: true,
    label: 'Uploading document...',
  },
};

export const Variants: Story = {
  render: () => (
    <div className="w-64 space-y-4">
      <Progress value={25} variant="default" showLabel label="Default" />
      <Progress value={50} variant="success" showLabel label="Success" />
      <Progress value={75} variant="warning" showLabel label="Warning" />
      <Progress value={90} variant="error" showLabel label="Error" />
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="w-64 space-y-4">
      <Progress value={60} size="sm" showLabel label="Small" />
      <Progress value={60} size="md" showLabel label="Medium" />
      <Progress value={60} size="lg" showLabel label="Large" />
    </div>
  ),
};

export const FileUploadProgress: Story = {
  render: () => (
    <div className="w-80 space-y-4">
      <Progress value={0} showLabel label="Initializing upload..." />
      <Progress value={25} showLabel label="Uploading invoice.pdf..." />
      <Progress value={75} variant="warning" showLabel label="Processing OCR..." />
      <Progress value={100} variant="success" showLabel label="Upload complete!" />
    </div>
  ),
};