import React from 'react';
import { render, screen } from '@testing-library/react';
import { InvoiceStatusBadge } from '../InvoiceStatusBadge/InvoiceStatusBadge';

describe('InvoiceStatusBadge Component', () => {
  it('renders draft status correctly', () => {
    render(<InvoiceStatusBadge status="draft" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent('Szkic');
    expect(badge).toHaveAttribute('data-status', 'draft');
    expect(badge).toHaveClass('bg-neutral-100', 'text-neutral-800');
  });

  it('renders sent status correctly', () => {
    render(<InvoiceStatusBadge status="sent" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveTextContent('Wysłana');
    expect(badge).toHaveAttribute('data-status', 'sent');
    expect(badge).toHaveClass('bg-primary-100', 'text-primary-800');
  });

  it('renders viewed status correctly', () => {
    render(<InvoiceStatusBadge status="viewed" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveTextContent('Wyświetlona');
    expect(badge).toHaveAttribute('data-status', 'viewed');
    expect(badge).toHaveClass('bg-blue-100', 'text-blue-800');
  });

  it('renders paid status correctly', () => {
    render(<InvoiceStatusBadge status="paid" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveTextContent('Opłacona');
    expect(badge).toHaveAttribute('data-status', 'paid');
    expect(badge).toHaveClass('bg-success-100', 'text-success-800');
  });

  it('renders overdue status correctly', () => {
    render(<InvoiceStatusBadge status="overdue" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveTextContent('Przeterminowana');
    expect(badge).toHaveAttribute('data-status', 'overdue');
    expect(badge).toHaveClass('bg-error-100', 'text-error-800');
  });

  it('renders cancelled status correctly', () => {
    render(<InvoiceStatusBadge status="cancelled" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveTextContent('Anulowana');
    expect(badge).toHaveAttribute('data-status', 'cancelled');
    expect(badge).toHaveClass('bg-neutral-100', 'text-neutral-600');
  });

  it('renders corrected status correctly', () => {
    render(<InvoiceStatusBadge status="corrected" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveTextContent('Skorygowana');
    expect(badge).toHaveAttribute('data-status', 'corrected');
    expect(badge).toHaveClass('bg-warning-100', 'text-warning-800');
  });

  it('applies small size classes', () => {
    render(<InvoiceStatusBadge status="paid" size="sm" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveClass('px-2', 'py-1', 'text-xs');
  });

  it('applies medium size classes by default', () => {
    render(<InvoiceStatusBadge status="paid" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveClass('px-3', 'py-1', 'text-sm');
  });

  it('applies large size classes', () => {
    render(<InvoiceStatusBadge status="paid" size="lg" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveClass('px-4', 'py-2', 'text-base');
  });

  it('applies custom className', () => {
    render(<InvoiceStatusBadge status="paid" className="custom-class" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveClass('custom-class');
  });

  it('displays appropriate icon for paid status', () => {
    render(<InvoiceStatusBadge status="paid" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    const icon = badge.querySelector('svg');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('w-3', 'h-3', 'mr-1');
  });

  it('displays appropriate icon for overdue status', () => {
    render(<InvoiceStatusBadge status="overdue" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    const icon = badge.querySelector('svg');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('w-3', 'h-3', 'mr-1');
  });

  it('displays appropriate icon for sent status', () => {
    render(<InvoiceStatusBadge status="sent" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    const icon = badge.querySelector('svg');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('w-3', 'h-3', 'mr-1');
  });

  it('displays appropriate icon for viewed status', () => {
    render(<InvoiceStatusBadge status="viewed" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    const icon = badge.querySelector('svg');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('w-3', 'h-3', 'mr-1');
  });

  it('displays appropriate icon for cancelled status', () => {
    render(<InvoiceStatusBadge status="cancelled" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    const icon = badge.querySelector('svg');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('w-3', 'h-3', 'mr-1');
  });

  it('displays appropriate icon for corrected status', () => {
    render(<InvoiceStatusBadge status="corrected" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    const icon = badge.querySelector('svg');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('w-3', 'h-3', 'mr-1');
  });

  it('does not display icon for draft status', () => {
    render(<InvoiceStatusBadge status="draft" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    const icon = badge.querySelector('svg');
    expect(icon).not.toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    render(<InvoiceStatusBadge status="paid" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveAttribute('data-status', 'paid');
  });

  it('renders with consistent styling structure', () => {
    render(<InvoiceStatusBadge status="sent" testId="status-badge" />);
    
    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveClass(
      'inline-flex',
      'items-center',
      'font-medium',
      'rounded-md-full',
      'border'
    );
  });

  it('handles all status types without errors', () => {
    const statuses = ['draft', 'sent', 'viewed', 'paid', 'overdue', 'cancelled', 'corrected'] as const;
    
    statuses.forEach((status) => {
      const { unmount } = render(<InvoiceStatusBadge status={status} testId={`status-${status}`} />);
      
      const badge = screen.getByTestId(`status-${status}`);
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveAttribute('data-status', status);
      
      unmount();
    });
  });
});