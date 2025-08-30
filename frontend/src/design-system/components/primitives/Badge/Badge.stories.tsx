import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from './Badge';
import { CheckCircle, AlertCircle, Clock, X } from 'lucide-react';

const meta: Meta<typeof Badge> = {
  title: 'Primitives/Badge',
  component: Badge,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'primary', 'success', 'warning', 'error', 'info'],
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
    children: 'Default Badge',
  },
};

export const Variants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="default">Default</Badge>
      <Badge variant="primary">Primary</Badge>
      <Badge variant="success">Success</Badge>
      <Badge variant="warning">Warning</Badge>
      <Badge variant="error">Error</Badge>
      <Badge variant="info">Info</Badge>
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <Badge size="sm">Small</Badge>
      <Badge size="md">Medium</Badge>
      <Badge size="lg">Large</Badge>
    </div>
  ),
};

export const WithIcons: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="success" icon={<CheckCircle className="w-3 h-3" />}>
        Completed
      </Badge>
      <Badge variant="warning" icon={<Clock className="w-3 h-3" />}>
        Processing
      </Badge>
      <Badge variant="error" icon={<AlertCircle className="w-3 h-3" />}>
        Failed
      </Badge>
      <Badge variant="info" icon={<X className="w-3 h-3" />}>
        Cancelled
      </Badge>
    </div>
  ),
};

export const FileUploadStatuses: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="info" icon={<Clock className="w-3 h-3" />}>
        Pending
      </Badge>
      <Badge variant="warning" icon={<Clock className="w-3 h-3 animate-spin" />}>
        Processing
      </Badge>
      <Badge variant="success" icon={<CheckCircle className="w-3 h-3" />}>
        Completed
      </Badge>
      <Badge variant="error" icon={<AlertCircle className="w-3 h-3" />}>
        Failed
      </Badge>
    </div>
  ),
};