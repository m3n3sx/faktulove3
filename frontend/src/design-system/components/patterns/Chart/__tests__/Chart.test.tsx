import React from 'react';
import { render, screen } from '@testing-library/react';
import { Chart, ChartCard } from '../Chart';

const mockData = [
  { label: 'PDF', value: 892, percentage: 71.5 },
  { label: 'JPEG', value: 234, percentage: 18.8 },
  { label: 'PNG', value: 89, percentage: 7.1 },
  { label: 'TIFF', value: 32, percentage: 2.6 }
];

describe('Chart', () => {
  it('renders chart with title', () => {
    render(
      <Chart 
        data={mockData} 
        type="bar" 
        title="File Type Distribution"
        testId="test-chart"
      />
    );
    
    expect(screen.getByText('File Type Distribution')).toBeInTheDocument();
    expect(screen.getByTestId('test-chart')).toBeInTheDocument();
  });

  it('renders bar chart correctly', () => {
    render(
      <Chart 
        data={mockData} 
        type="bar" 
        showValues={true}
        testId="bar-chart"
      />
    );
    
    const chart = screen.getByTestId('bar-chart');
    expect(chart).toHaveAttribute('role', 'img');
    expect(chart).toHaveAttribute('aria-label', 'bar chart showing data');
  });

  it('renders pie chart with percentages', () => {
    render(
      <Chart 
        data={mockData} 
        type="pie" 
        showPercentages={true}
        testId="pie-chart"
      />
    );
    
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
    // Check that data labels are rendered
    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('JPEG')).toBeInTheDocument();
  });

  it('renders distribution chart', () => {
    render(
      <Chart 
        data={mockData} 
        type="distribution" 
        testId="distribution-chart"
      />
    );
    
    expect(screen.getByTestId('distribution-chart')).toBeInTheDocument();
    // Check that values are displayed
    expect(screen.getByText('892')).toBeInTheDocument();
    expect(screen.getByText('234')).toBeInTheDocument();
  });

  it('renders trend chart', () => {
    const trendData = [
      { label: 'Jan', value: 401, metadata: { successRate: 95.3 } },
      { label: 'Feb', value: 456, metadata: { successRate: 96.1 } },
    ];
    
    render(
      <Chart 
        data={trendData} 
        type="trend" 
        testId="trend-chart"
      />
    );
    
    expect(screen.getByTestId('trend-chart')).toBeInTheDocument();
    expect(screen.getByText('Jan')).toBeInTheDocument();
    expect(screen.getByText('401')).toBeInTheDocument();
  });

  it('applies Polish formatting when enabled', () => {
    const largeNumberData = [
      { label: 'Large Number', value: 1234567 }
    ];
    
    render(
      <Chart 
        data={largeNumberData} 
        type="distribution" 
        polishFormatting={true}
        testId="polish-chart"
      />
    );
    
    // Polish formatting should use spaces as thousand separators
    expect(screen.getByText('1 234 567')).toBeInTheDocument();
  });

  it('disables Polish formatting when specified', () => {
    const largeNumberData = [
      { label: 'Large Number', value: 1234567 }
    ];
    
    render(
      <Chart 
        data={largeNumberData} 
        type="distribution" 
        polishFormatting={false}
        testId="non-polish-chart"
      />
    );
    
    expect(screen.getByText('1234567')).toBeInTheDocument();
  });

  it('renders custom accessibility label', () => {
    render(
      <Chart 
        data={mockData} 
        type="bar" 
        accessibilityLabel="Custom chart description"
        testId="accessible-chart"
      />
    );
    
    const chart = screen.getByTestId('accessible-chart');
    expect(chart).toHaveAttribute('aria-label', 'Custom chart description');
  });
});

describe('ChartCard', () => {
  it('renders chart within a card', () => {
    render(
      <ChartCard 
        data={mockData} 
        type="bar" 
        title="Chart in Card"
        testId="chart-card"
      />
    );
    
    expect(screen.getByText('Chart in Card')).toBeInTheDocument();
    expect(screen.getByTestId('chart-card')).toBeInTheDocument();
  });

  it('applies card variant correctly', () => {
    render(
      <ChartCard 
        data={mockData} 
        type="bar" 
        cardVariant="outlined"
        testId="outlined-chart-card"
      />
    );
    
    expect(screen.getByTestId('outlined-chart-card')).toBeInTheDocument();
  });
});