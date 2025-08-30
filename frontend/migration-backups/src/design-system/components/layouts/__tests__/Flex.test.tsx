import React from 'react';
import { render, screen } from '@testing-library/react';
import { Flex } from '../Flex/Flex';

describe('Flex Component', () => {
  it('renders children correctly', () => {
    render(
      <Flex testId="test-flex">
        <div>Child 1</div>
        <div>Child 2</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toBeInTheDocument();
    expect(flex).toHaveTextContent('Child 1');
    expect(flex).toHaveTextContent('Child 2');
  });

  it('applies default flex classes', () => {
    render(
      <Flex testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('flex', 'flex-row', 'flex-nowrap', 'justify-start', 'items-start');
  });

  it('applies custom direction', () => {
    render(
      <Flex direction="col" testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('flex-col');
  });

  it('applies reverse direction', () => {
    render(
      <Flex direction="row-reverse" testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('flex-row-reverse');
  });

  it('applies wrap configuration', () => {
    render(
      <Flex wrap="wrap" testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('flex-wrap');
  });

  it('applies justify content', () => {
    render(
      <Flex justify="center" testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('justify-center');
  });

  it('applies align items', () => {
    render(
      <Flex align="center" testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('items-center');
  });

  it('applies gap', () => {
    render(
      <Flex gap={4} testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('gap-4');
  });

  it('applies custom gap with string value', () => {
    render(
      <Flex gap="1.5rem" testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('gap-[1.5rem]');
  });

  it('applies grow and shrink', () => {
    render(
      <Flex grow shrink testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('flex-grow', 'flex-shrink');
  });

  it('applies custom className', () => {
    render(
      <Flex className="custom-class" testId="test-flex">
        <div>Content</div>
      </Flex>
    );

    const flex = screen.getByTestId('test-flex');
    expect(flex).toHaveClass('custom-class');
  });

  it('handles all justify options correctly', () => {
    const justifyOptions = ['start', 'end', 'center', 'between', 'around', 'evenly'] as const;
    
    justifyOptions.forEach((justify) => {
      const { unmount } = render(
        <Flex justify={justify} testId={`test-flex-${justify}`}>
          <div>Content</div>
        </Flex>
      );

      const flex = screen.getByTestId(`test-flex-${justify}`);
      expect(flex).toHaveClass(`justify-${justify}`);
      unmount();
    });
  });

  it('handles all align options correctly', () => {
    const alignOptions = ['start', 'end', 'center', 'baseline', 'stretch'] as const;
    
    alignOptions.forEach((align) => {
      const { unmount } = render(
        <Flex align={align} testId={`test-flex-${align}`}>
          <div>Content</div>
        </Flex>
      );

      const flex = screen.getByTestId(`test-flex-${align}`);
      expect(flex).toHaveClass(`items-${align}`);
      unmount();
    });
  });
});