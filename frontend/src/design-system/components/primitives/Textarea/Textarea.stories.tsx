import type { Meta, StoryObj } from '@storybook/react';
import { Textarea } from './Textarea';

const meta: Meta<typeof Textarea> = {
  title: 'Design System/Primitives/Textarea',
  component: Textarea,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'A flexible textarea component with Polish business support, validation, and accessibility features.',
      },
    },
  },
  argTypes: {
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
    },
    resize: {
      control: 'select',
      options: ['none', 'both', 'horizontal', 'vertical'],
    },
    error: {
      control: 'boolean',
    },
    disabled: {
      control: 'boolean',
    },
    required: {
      control: 'boolean',
    },
    readOnly: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Textarea>;

export const Default: Story = {
  args: {
    placeholder: 'Enter your message...',
  },
};

export const WithLabel: Story = {
  args: {
    label: 'Description',
    placeholder: 'Enter description...',
  },
};

export const WithHelperText: Story = {
  args: {
    label: 'Comments',
    placeholder: 'Enter your comments...',
    helperText: 'Please provide detailed feedback',
  },
};

export const Required: Story = {
  args: {
    label: 'Required Field',
    placeholder: 'This field is required...',
    required: true,
  },
};

export const Error: Story = {
  args: {
    label: 'Message',
    placeholder: 'Enter message...',
    error: true,
    errorMessage: 'This field is required',
  },
};

export const Disabled: Story = {
  args: {
    label: 'Disabled Field',
    placeholder: 'This field is disabled...',
    disabled: true,
    value: 'This textarea is disabled',
  },
};

export const ReadOnly: Story = {
  args: {
    label: 'Read Only Field',
    readOnly: true,
    value: 'This content cannot be edited',
  },
};

export const Sizes: Story = {
  render: () => (
    <div className="space-y-4">
      <Textarea size="xs" label="Extra Small" placeholder="Extra small textarea..." />
      <Textarea size="sm" label="Small" placeholder="Small textarea..." />
      <Textarea size="md" label="Medium" placeholder="Medium textarea..." />
      <Textarea size="lg" label="Large" placeholder="Large textarea..." />
      <Textarea size="xl" label="Extra Large" placeholder="Extra large textarea..." />
    </div>
  ),
};

export const ResizeOptions: Story = {
  render: () => (
    <div className="space-y-4">
      <Textarea resize="none" label="No Resize" placeholder="Cannot be resized..." />
      <Textarea resize="vertical" label="Vertical Resize" placeholder="Can be resized vertically..." />
      <Textarea resize="horizontal" label="Horizontal Resize" placeholder="Can be resized horizontally..." />
      <Textarea resize="both" label="Both Directions" placeholder="Can be resized in both directions..." />
    </div>
  ),
};

export const PolishBusiness: Story = {
  args: {
    label: 'Opis faktury',
    placeholder: 'Wprowadź opis faktury...',
    helperText: 'Podaj szczegółowy opis usług lub towarów',
    rows: 4,
  },
};