import React from 'react';
import { render, screen } from '@testing-library/react';
import { Stack } from '../Stack/Stack';

describe('Stack Component', () => {
  it('renders children correctly', () => {
    render(
      <Stack testId="test-stack">
        <div>Child 1</div>
        <div>Child 2</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    expect(stack).toBeInTheDocument();
    expect(stack).toHaveTextContent('Child 1');
    expect(stack).toHaveTextContent('Child 2');
  });

  it('applies default vertical stack classes', () => {
    render(
      <Stack testId="test-stack">
        <div>Content</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    expect(stack).toHaveClass('flex', 'flex-col', 'items-stretch', 'gap-4');
  });

  it('applies horizontal direction', () => {
    render(
      <Stack direction="horizontal" testId="test-stack">
        <div>Content</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    expect(stack).toHaveClass('flex-row');
  });

  it('applies custom spacing', () => {
    render(
      <Stack spacing={8} testId="test-stack">
        <div>Content</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    expect(stack).toHaveClass('gap-8');
  });

  it('applies custom spacing with string value', () => {
    render(
      <Stack spacing="2rem" testId="test-stack">
        <div>Content</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    expect(stack).toHaveClass('gap-[2rem]');
  });

  it('applies alignment for vertical stack', () => {
    render(
      <Stack align="center" testId="test-stack">
        <div>Content</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    expect(stack).toHaveClass('items-center');
  });

  it('applies alignment for horizontal stack', () => {
    render(
      <Stack direction="horizontal" align="center" testId="test-stack">
        <div>Content</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    expect(stack).toHaveClass('justify-center');
  });

  it('renders dividers between children', () => {
    const divider = <hr data-testid="divider" />;
    
    render(
      <Stack divider={divider} testId="test-stack">
        <div>Child 1</div>
        <div>Child 2</div>
        <div>Child 3</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    const dividers = screen.getAllByTestId('divider');
    
    expect(stack).toBeInTheDocument();
    expect(dividers).toHaveLength(2); // One less than children count
  });

  it('does not render dividers with single child', () => {
    const divider = <hr data-testid="divider" />;
    
    render(
      <Stack divider={divider} testId="test-stack">
        <div>Single Child</div>
      </Stack>
    );

    const dividers = screen.queryAllByTestId('divider');
    expect(dividers).toHaveLength(0);
  });

  it('removes gap class when using dividers', () => {
    const divider = <hr />;
    
    render(
      <Stack divider={divider} spacing={4} testId="test-stack">
        <div>Child 1</div>
        <div>Child 2</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    expect(stack).not.toHaveClass('gap-4');
  });

  it('applies custom className', () => {
    render(
      <Stack className="custom-class" testId="test-stack">
        <div>Content</div>
      </Stack>
    );

    const stack = screen.getByTestId('test-stack');
    expect(stack).toHaveClass('custom-class');
  });

  it('handles all alignment options for vertical stack', () => {
    const alignOptions = ['start', 'end', 'center', 'stretch'] as const;
    
    alignOptions.forEach((align) => {
      const { unmount } = render(
        <Stack align={align} testId={`test-stack-${align}`}>
          <div>Content</div>
        </Stack>
      );

      const stack = screen.getByTestId(`test-stack-${align}`);
      expect(stack).toHaveClass(`items-${align}`);
      unmount();
    });
  });

  it('handles all alignment options for horizontal stack', () => {
    const alignOptions = ['start', 'end', 'center', 'stretch'] as const;
    
    alignOptions.forEach((align) => {
      const { unmount } = render(
        <Stack direction="horizontal" align={align} testId={`test-stack-h-${align}`}>
          <div>Content</div>
        </Stack>
      );

      const stack = screen.getByTestId(`test-stack-h-${align}`);
      const expectedClass = align === 'stretch' ? 'justify-stretch' : `justify-${align}`;
      expect(stack).toHaveClass(expectedClass);
      unmount();
    });
  });
});