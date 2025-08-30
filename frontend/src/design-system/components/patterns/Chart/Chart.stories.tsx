import type { Meta, StoryObj } from '@storybook/react';
import { Chart, ChartCard } from './Chart';

const meta: Meta<typeof Chart> = {
  title: 'Design System/Patterns/Chart',
  component: Chart,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['bar', 'pie', 'line', 'distribution', 'trend'],
    },
    height: {
      control: { type: 'range', min: 200, max: 600, step: 50 },
    },
    showLegend: {
      control: 'boolean',
    },
    showValues: {
      control: 'boolean',
    },
    showPercentages: {
      control: 'boolean',
    },
    polishFormatting: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

const fileTypeData = [
  { label: 'PDF', value: 892, percentage: 71.5 },
  { label: 'JPEG', value: 234, percentage: 18.8 },
  { label: 'PNG', value: 89, percentage: 7.1 },
  { label: 'TIFF', value: 32, percentage: 2.6 }
];

const confidenceData = [
  { label: '95-100%', value: 567, percentage: 45.5 },
  { label: '90-95%', value: 423, percentage: 33.9 },
  { label: '80-90%', value: 189, percentage: 15.2 },
  { label: '70-80%', value: 45, percentage: 3.6 },
  { label: '<70%', value: 23, percentage: 1.8 }
];

const processingTimeData = [
  { label: '<2s', value: 234, percentage: 18.8 },
  { label: '2-3s', value: 567, percentage: 45.5 },
  { label: '3-5s', value: 345, percentage: 27.7 },
  { label: '5-10s', value: 89, percentage: 7.1 },
  { label: '>10s', value: 12, percentage: 1.0 }
];

const monthlyTrendData = [
  { label: 'Lip', value: 234, metadata: { successRate: 92.1 } },
  { label: 'Sie', value: 267, metadata: { successRate: 93.5 } },
  { label: 'Wrz', value: 298, metadata: { successRate: 94.2 } },
  { label: 'Paź', value: 312, metadata: { successRate: 94.8 } },
  { label: 'Lis', value: 345, metadata: { successRate: 95.1 } },
  { label: 'Gru', value: 378, metadata: { successRate: 95.5 } },
  { label: 'Sty', value: 401, metadata: { successRate: 95.3 } }
];

export const BarChart: Story = {
  args: {
    data: fileTypeData,
    type: 'bar',
    title: 'File Type Distribution',
    showValues: true,
    height: 300,
  },
};

export const PieChart: Story = {
  args: {
    data: confidenceData,
    type: 'pie',
    title: 'Confidence Score Distribution',
    showPercentages: true,
    height: 400,
  },
};

export const DistributionChart: Story = {
  args: {
    data: processingTimeData,
    type: 'distribution',
    title: 'Processing Time Distribution',
    showValues: true,
  },
};

export const TrendChart: Story = {
  args: {
    data: monthlyTrendData,
    type: 'trend',
    title: 'Monthly Document Processing Trends',
  },
};

export const PolishBusinessCharts: Story = {
  render: () => (
    <div className="space-y-6">
      <ChartCard
        data={[
          { label: 'Faktury VAT', value: 1247 },
          { label: 'Rachunki', value: 456 },
          { label: 'Korekty', value: 89 },
          { label: 'Inne', value: 234 }
        ]}
        type="bar"
        title="Rodzaje Dokumentów"
        showValues={true}
        polishFormatting={true}
      />
      
      <ChartCard
        data={[
          { label: 'Sty 2024', value: 12456, metadata: { successRate: 95.3 } },
          { label: 'Lut 2024', value: 13789, metadata: { successRate: 96.1 } },
          { label: 'Mar 2024', value: 14234, metadata: { successRate: 94.8 } },
          { label: 'Kwi 2024', value: 15678, metadata: { successRate: 97.2 } },
          { label: 'Maj 2024', value: 16123, metadata: { successRate: 96.5 } },
          { label: 'Cze 2024', value: 17456, metadata: { successRate: 95.9 } }
        ]}
        type="trend"
        title="Miesięczne Trendy Przetwarzania"
        polishFormatting={true}
      />
    </div>
  ),
};

export const ResponsiveCharts: Story = {
  render: () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <ChartCard
        data={fileTypeData}
        type="pie"
        title="File Types"
        showPercentages={true}
        responsive={true}
      />
      
      <ChartCard
        data={confidenceData}
        type="distribution"
        title="Confidence Levels"
        showValues={true}
        responsive={true}
      />
    </div>
  ),
};

export const AccessibleCharts: Story = {
  render: () => (
    <div className="space-y-6">
      <Chart
        data={fileTypeData}
        type="bar"
        title="Document Types Processed"
        accessibilityLabel="Bar chart showing distribution of document types: PDF 892 documents (71.5%), JPEG 234 documents (18.8%), PNG 89 documents (7.1%), TIFF 32 documents (2.6%)"
        showValues={true}
      />
      
      <Chart
        data={confidenceData}
        type="pie"
        title="OCR Confidence Scores"
        accessibilityLabel="Pie chart showing OCR confidence score distribution across 5 ranges, with highest confidence (95-100%) representing 45.5% of documents"
        showPercentages={true}
      />
    </div>
  ),
};