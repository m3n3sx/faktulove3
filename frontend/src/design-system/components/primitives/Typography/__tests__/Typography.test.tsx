import React from 'react';
import { render, screen } from '@testing-library/react';
import { Typography } from '../Typography';

describe('Typography', () => {
  it('renders children correctly', () => {
    render(<Typography>Test content</Typography>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('applies correct variant styles', () => {
    render(<Typography variant="h1" testId="heading">Heading</Typography>);
    const element = screen.getByTestId('heading');
    expect(element.tagName).toBe('H1');
    expect(element).toHaveClass('text-4xl', 'font-bold', 'leading-tight');
  });

  it('applies correct color classes', () => {
    render(<Typography color="success" testId="success-text">Success</Typography>);
    const element = screen.getByTestId('success-text');
    expect(element).toHaveClass('text-success-600');
  });

  it('uses custom element when specified', () => {
    render(<Typography as="span" testId="span-element">Span content</Typography>);
    const element = screen.getByTestId('span-element');
    expect(element.tagName).toBe('SPAN');
  });

  it('applies custom className', () => {
    render(<Typography className="custom-class" testId="custom">Custom</Typography>);
    const element = screen.getByTestId('custom');
    expect(element).toHaveClass('custom-class');
  });

  it('renders code variant with correct element', () => {
    render(<Typography variant="code" testId="code-element">Code</Typography>);
    const element = screen.getByTestId('code-element');
    expect(element.tagName).toBe('CODE');
  });

  it('renders Polish business variants correctly', () => {
    render(<Typography variant="invoiceNumber" testId="invoice">FV/2024/001</Typography>);
    const element = screen.getByTestId('invoice');
    expect(element).toHaveClass('text-lg', 'font-semibold');
  });
});