import React from 'react';
import { render, screen } from '@testing-library/react';
import { Container } from '../Container/Container';

describe('Container Component', () => {
  it('renders children correctly', () => {
    render(
      <Container testId="test-container">
        <div>Container Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).toBeInTheDocument();
    expect(container).toHaveTextContent('Container Content');
  });

  it('applies default classes', () => {
    render(
      <Container testId="test-container">
        <div>Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).toHaveClass('w-full', 'max-w-6xl', 'mx-auto', 'px-4', 'sm:px-6', 'lg:px-8');
  });

  it('applies size-specific max-width classes', () => {
    const sizes = [
      { size: 'sm' as const, expectedClass: 'max-w-2xl' },
      { size: 'md' as const, expectedClass: 'max-w-4xl' },
      { size: 'lg' as const, expectedClass: 'max-w-6xl' },
      { size: 'xl' as const, expectedClass: 'max-w-7xl' },
      { size: 'full' as const, expectedClass: 'max-w-full' },
    ];

    sizes.forEach(({ size, expectedClass }) => {
      const { unmount } = render(
        <Container size={size} testId={`test-container-${size}`}>
          <div>Content</div>
        </Container>
      );

      const container = screen.getByTestId(`test-container-${size}`);
      expect(container).toHaveClass(expectedClass);
      unmount();
    });
  });

  it('does not apply mx-auto for full size', () => {
    render(
      <Container size="full" testId="test-container">
        <div>Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).not.toHaveClass('mx-auto');
  });

  it('applies mx-auto for non-full sizes', () => {
    render(
      <Container size="lg" testId="test-container">
        <div>Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).toHaveClass('mx-auto');
  });

  it('applies padding by default', () => {
    render(
      <Container testId="test-container">
        <div>Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
  });

  it('does not apply padding when padding is false', () => {
    render(
      <Container padding={false} testId="test-container">
        <div>Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).not.toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
  });

  it('applies center content classes when centerContent is true', () => {
    render(
      <Container centerContent testId="test-container">
        <div>Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).toHaveClass('flex', 'items-center', 'justify-center');
  });

  it('does not apply center content classes by default', () => {
    render(
      <Container testId="test-container">
        <div>Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).not.toHaveClass('flex', 'items-center', 'justify-center');
  });

  it('applies custom className', () => {
    render(
      <Container className="custom-class" testId="test-container">
        <div>Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).toHaveClass('custom-class');
  });

  it('combines all options correctly', () => {
    render(
      <Container 
        size="xl" 
        padding={false} 
        centerContent 
        className="custom-class" 
        testId="test-container"
      >
        <div>Content</div>
      </Container>
    );

    const container = screen.getByTestId('test-container');
    expect(container).toHaveClass(
      'w-full',
      'max-w-7xl',
      'mx-auto',
      'flex',
      'items-center',
      'justify-center',
      'custom-class'
    );
    expect(container).not.toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
  });
});