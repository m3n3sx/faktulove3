import React from 'react';
import { render, screen } from '@testing-library/react';
import { Checkbox } from '../Checkbox';

describe('Checkbox Component - Basic Tests', () => {
  it('renders without crashing', () => {
    render(<Checkbox label="Test Checkbox" />);
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Checkbox label="Test Label" />);
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('can be checked', () => {
    render(<Checkbox label="Test" checked={true} />);
    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toBeChecked();
  });

  it('can be disabled', () => {
    render(<Checkbox label="Test" disabled={true} />);
    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toBeDisabled();
  });

  it('shows error message', () => {
    render(<Checkbox label="Test" error={true} errorMessage="Error!" />);
    expect(screen.getByText('Error!')).toBeInTheDocument();
  });
});