import React from 'react';
import { render, screen } from '@testing-library/react';
import { Progress } from '../Progress';

describe('Progress', () => {
  it('renders correctly', () => {
    render(<Progress value={50} testId="progress" />);
    const progress = screen.getByTestId('progress');
    expect(progress).toBeInTheDocument();
  });

  it('displays correct percentage', () => {
    render(<Progress value={75} testId="progress" />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '75');
    expect(progressBar).toHaveStyle('width: 75%');
  });

  it('shows label when enabled', () => {
    render(<Progress value={60} showLabel label="Uploading..." testId="progress" />);
    expect(screen.getByText('Uploading...')).toBeInTheDocument();
    expect(screen.getByText('60%')).toBeInTheDocument();
  });

  it('applies variant styles correctly', () => {
    render(<Progress value={50} variant="success" testId="progress" />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('bg-success-600');
  });

  it('applies size classes correctly', () => {
    render(<Progress value={50} size="lg" testId="progress" />);
    const container = screen.getByTestId('progress').querySelector('div:nth-child(1)');
    expect(container).toHaveClass('h-3');
  });

  it('handles edge cases for percentage calculation', () => {
    // Test negative value
    render(<Progress value={-10} testId="negative" />);
    let progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveStyle('width: 0%');

    // Test value over max
    render(<Progress value={150} max={100} testId="over-max" />);
    progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveStyle('width: 100%');
  });

  it('uses custom max value', () => {
    render(<Progress value={50} max={200} testId="custom-max" />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuemax', '200');
    expect(progressBar).toHaveStyle('width: 25%'); // 50/200 = 25%
  });
});