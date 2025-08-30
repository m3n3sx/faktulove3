import React from 'react';
import { render, screen } from '@testing-library/react';
import { Radio, RadioGroup, RadioOption } from '../Radio';

const mockOptions: RadioOption[] = [
  { value: 'option1', label: 'Option 1' },
  { value: 'option2', label: 'Option 2' },
  { value: 'option3', label: 'Option 3' },
];

describe('Radio Component - Basic Tests', () => {
  it('renders without crashing', () => {
    render(<Radio label="Test Radio" name="test" value="test" />);
    expect(screen.getByRole('radio')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Radio label="Test Label" name="test" value="test" />);
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('can be checked', () => {
    render(<Radio label="Test" name="test" value="test" checked={true} />);
    const radio = screen.getByRole('radio');
    expect(radio).toBeChecked();
  });

  it('can be disabled', () => {
    render(<Radio label="Test" name="test" value="test" disabled={true} />);
    const radio = screen.getByRole('radio');
    expect(radio).toBeDisabled();
  });
});

describe('RadioGroup Component - Basic Tests', () => {
  it('renders without crashing', () => {
    render(<RadioGroup options={mockOptions} name="test-group" />);
    expect(screen.getByRole('radiogroup')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<RadioGroup options={mockOptions} name="test-group" label="Test Group" />);
    expect(screen.getByText('Test Group')).toBeInTheDocument();
  });

  it('renders all options', () => {
    render(<RadioGroup options={mockOptions} name="test-group" />);
    mockOptions.forEach(option => {
      expect(screen.getByText(option.label)).toBeInTheDocument();
    });
  });

  it('shows selected value', () => {
    render(<RadioGroup options={mockOptions} name="test-group" value="option1" />);
    const selectedRadio = screen.getByDisplayValue('option1');
    expect(selectedRadio).toBeChecked();
  });

  it('shows error message', () => {
    render(<RadioGroup options={mockOptions} name="test-group" error={true} errorMessage="Error!" />);
    expect(screen.getByText('Error!')).toBeInTheDocument();
  });
});