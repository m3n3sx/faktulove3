import React from 'react';
import { render, screen } from '@testing-library/react';
import { Select, SelectOption } from '../Select';

const mockOptions: SelectOption[] = [
  { value: 'option1', label: 'Option 1' },
  { value: 'option2', label: 'Option 2' },
  { value: 'option3', label: 'Option 3' },
];

describe('Select Component - Basic Tests', () => {
  it('renders without crashing', () => {
    render(<Select options={mockOptions} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Select options={mockOptions} label="Test Label" />);
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('shows placeholder', () => {
    render(<Select options={mockOptions} placeholder="Choose option" />);
    expect(screen.getByText('Choose option')).toBeInTheDocument();
  });

  it('can be disabled', () => {
    render(<Select options={mockOptions} disabled={true} />);
    const select = screen.getByRole('button');
    expect(select).toBeDisabled();
  });

  it('shows error message', () => {
    render(<Select options={mockOptions} error={true} errorMessage="Error!" />);
    expect(screen.getByText('Error!')).toBeInTheDocument();
  });

  it('shows selected value', () => {
    render(<Select options={mockOptions} value="option1" />);
    expect(screen.getByText('Option 1')).toBeInTheDocument();
  });
});