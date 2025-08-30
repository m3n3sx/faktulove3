import type { Meta, StoryObj } from '@storybook/react';
import { Typography } from './Typography';

const meta: Meta<typeof Typography> = {
  title: 'Design System/Primitives/Typography',
  component: Typography,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'body', 'bodyLarge', 'bodySmall',
        'caption', 'label', 'button', 'link', 'code',
        'invoiceTitle', 'invoiceNumber', 'companyName', 'contractorName',
        'currencyAmount', 'currencyAmountLarge', 'dateFormat', 'nipFormat',
        'vatRate', 'statusBadge', 'tableHeader', 'tableCell',
        'formLabel', 'formHelperText', 'formErrorText'
      ],
    },
    color: {
      control: 'select',
      options: ['primary', 'secondary', 'muted', 'success', 'warning', 'error'],
    },
    as: {
      control: 'select',
      options: ['p', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'code'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'This is default body text',
    variant: 'body',
  },
};

export const Headings: Story = {
  render: () => (
    <div className="space-y-4">
      <Typography variant="h1">Heading 1</Typography>
      <Typography variant="h2">Heading 2</Typography>
      <Typography variant="h3">Heading 3</Typography>
      <Typography variant="h4">Heading 4</Typography>
      <Typography variant="h5">Heading 5</Typography>
      <Typography variant="h6">Heading 6</Typography>
    </div>
  ),
};

export const BodyText: Story = {
  render: () => (
    <div className="space-y-4">
      <Typography variant="bodyLarge">Large body text for important content</Typography>
      <Typography variant="body">Regular body text for most content</Typography>
      <Typography variant="bodySmall">Small body text for secondary information</Typography>
    </div>
  ),
};

export const Colors: Story = {
  render: () => (
    <div className="space-y-2">
      <Typography color="primary">Primary text color</Typography>
      <Typography color="secondary">Secondary text color</Typography>
      <Typography color="muted">Muted text color</Typography>
      <Typography color="success">Success text color</Typography>
      <Typography color="warning">Warning text color</Typography>
      <Typography color="error">Error text color</Typography>
    </div>
  ),
};

export const PolishBusiness: Story = {
  render: () => (
    <div className="space-y-4">
      <Typography variant="invoiceTitle">FAKTURA VAT</Typography>
      <Typography variant="invoiceNumber">FV/2024/001</Typography>
      <Typography variant="companyName">ACME Corporation Sp. z o.o.</Typography>
      <Typography variant="contractorName">Jan Kowalski</Typography>
      <Typography variant="currencyAmount">1,234.56 zł</Typography>
      <Typography variant="currencyAmountLarge">12,345.67 zł</Typography>
      <Typography variant="dateFormat">15.01.2024</Typography>
      <Typography variant="nipFormat">123-456-78-90</Typography>
      <Typography variant="vatRate">23%</Typography>
    </div>
  ),
};

export const FormElements: Story = {
  render: () => (
    <div className="space-y-2">
      <Typography variant="formLabel">Form Label</Typography>
      <Typography variant="formHelperText">Helper text to guide the user</Typography>
      <Typography variant="formErrorText" color="error">Error message for validation</Typography>
    </div>
  ),
};

export const TableElements: Story = {
  render: () => (
    <div className="space-y-2">
      <Typography variant="tableHeader">TABLE HEADER</Typography>
      <Typography variant="tableCell">Table cell content</Typography>
    </div>
  ),
};

export const UIElements: Story = {
  render: () => (
    <div className="space-y-2">
      <Typography variant="caption">CAPTION TEXT</Typography>
      <Typography variant="label">Label Text</Typography>
      <Typography variant="button">Button Text</Typography>
      <Typography variant="link">Link Text</Typography>
      <Typography variant="code">Code Text</Typography>
      <Typography variant="statusBadge">STATUS</Typography>
    </div>
  ),
};