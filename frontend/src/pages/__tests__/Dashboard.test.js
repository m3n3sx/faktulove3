import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from '../Dashboard';

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: {} })),
}));

// Create a test query client
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithQueryClient = (component) => {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('Dashboard', () => {
  it('renders dashboard header correctly', () => {
    renderWithQueryClient(<Dashboard />);
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Overview of your OCR processing activity and system performance.')).toBeInTheDocument();
  });

  it('renders key metrics cards', () => {
    renderWithQueryClient(<Dashboard />);
    
    // Check for metric labels
    expect(screen.getByText('Total Documents')).toBeInTheDocument();
    expect(screen.getByText('Success Rate')).toBeInTheDocument();
    expect(screen.getByText('Avg Processing Time')).toBeInTheDocument();
    expect(screen.getByText('Avg Confidence')).toBeInTheDocument();
  });

  it('renders processing status section', () => {
    renderWithQueryClient(<Dashboard />);
    
    expect(screen.getByText('Processing Status')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('Processing')).toBeInTheDocument();
    expect(screen.getByText('Failed')).toBeInTheDocument();
  });

  it('renders activity overview section', () => {
    renderWithQueryClient(<Dashboard />);
    
    expect(screen.getByText('Activity Overview')).toBeInTheDocument();
    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.getByText('This Week')).toBeInTheDocument();
    expect(screen.getByText('This Month')).toBeInTheDocument();
  });

  it('renders business impact section', () => {
    renderWithQueryClient(<Dashboard />);
    
    expect(screen.getByText('Business Impact')).toBeInTheDocument();
    expect(screen.getByText('Invoices Created')).toBeInTheDocument();
    expect(screen.getByText('Manual Review')).toBeInTheDocument();
    expect(screen.getByText('Time Saved')).toBeInTheDocument();
  });

  it('renders recent documents section', () => {
    renderWithQueryClient(<Dashboard />);
    
    expect(screen.getByText('Recent Documents')).toBeInTheDocument();
  });

  it('renders quick actions section', () => {
    renderWithQueryClient(<Dashboard />);
    
    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('Upload Documents')).toBeInTheDocument();
    expect(screen.getByText('View Statistics')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('displays mock data correctly', () => {
    renderWithQueryClient(<Dashboard />);
    
    // Check for mock data values
    expect(screen.getByText('1,247')).toBeInTheDocument(); // total_documents
    expect(screen.getByText('95.3%')).toBeInTheDocument(); // success_rate
    expect(screen.getByText('2.8s')).toBeInTheDocument(); // average_processing_time
    expect(screen.getByText('94.2%')).toBeInTheDocument(); // average_confidence
  });

  it('uses design system components correctly', () => {
    renderWithQueryClient(<Dashboard />);
    
    // Check that Container is used (should have max-width classes)
    const container = screen.getByText('Dashboard').closest('[data-testid="container"]');
    expect(container).toBeInTheDocument();
  });
});