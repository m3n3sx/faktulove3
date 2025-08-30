import React from 'react';
import { render, screen } from '@testing-library/react';
import { Switch } from '../Switch';

describe('Switch Component - Basic Tests', () => {
  it('renders without crashing', () => {
    render(<Switch label="Test Switch" />);
    expect(screen.getByRole('switch')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Switch label="Test Label" />);
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('renders with description', () => {
    render(<Switch label="Test" description="Test description" />);
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('can be checked', () => {
    render(<Switch label="Test" checked={true} />);
    const switchElement = screen.getByRole('switch');
    expect(switchElement).toBeChecked();
  });

  it('can be disabled', () => {
    render(<Switch label="Test" disabled={true} />);
    const switchElement = screen.getByRole('switch');
    expect(switchElement).toBeDisabled();
  });

  it('shows error message', () => {
    render(<Switch label="Test" error={true} errorMessage="Error!" />);
    expect(screen.getByText('Error!')).toBeInTheDocument();
  });

  it('has proper ARIA attributes', () => {
    render(<Switch label="Test" checked={true} />);
    const switchElement = screen.getByRole('switch');
    expect(switchElement).toHaveAttribute('aria-checked', 'true');
  });
});