import React from 'react';
import { render, screen } from '@testing-library/react';
import { Badge } from '../Badge';
import { CheckCircle } from 'lucide-react';

describe('Badge', () => {
  it('renders correctly', () => {
    render(<Badge>Test Badge</Badge>);
    expect(screen.getByText('Test Badge')).toBeInTheDocument();
  });

  it('applies variant styles correctly', () => {
    render(<Badge variant="success" testId="success-badge">Success</Badge>);
    const badge = screen.getByTestId('success-badge');
    expect(badge).toHaveClass('bg-success-100', 'text-success-800', 'border-success-200');
  });

  it('applies size classes correctly', () => {
    render(<Badge size="lg" testId="large-badge">Large Badge</Badge>);
    const badge = screen.getByTestId('large-badge');
    expect(badge).toHaveClass('px-4', 'py-2', 'text-base');
  });

  it('renders with icon', () => {
    render(
      <Badge icon={<CheckCircle data-testid="check-icon" />} testId="icon-badge">
        With Icon
      </Badge>
    );
    expect(screen.getByTestId('check-icon')).toBeInTheDocument();
    expect(screen.getByText('With Icon')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<Badge className="custom-class" testId="custom-badge">Custom</Badge>);
    const badge = screen.getByTestId('custom-badge');
    expect(badge).toHaveClass('custom-class');
  });

  it('has correct default props', () => {
    render(<Badge testId="default-badge">Default</Badge>);
    const badge = screen.getByTestId('default-badge');
    expect(badge).toHaveClass('bg-neutral-100', 'text-neutral-800', 'px-3', 'py-1', 'text-sm');
  });
});