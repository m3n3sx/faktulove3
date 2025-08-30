import React from 'react';
import { render, screen } from '@testing-library/react';
import { Grid } from '../Grid/Grid';

describe('Grid Component', () => {
  it('renders children correctly', () => {
    render(
      <Grid testId="test-grid">
        <div>Child 1</div>
        <div>Child 2</div>
      </Grid>
    );

    const grid = screen.getByTestId('test-grid');
    expect(grid).toBeInTheDocument();
    expect(grid).toHaveTextContent('Child 1');
    expect(grid).toHaveTextContent('Child 2');
  });

  it('applies default grid classes', () => {
    render(
      <Grid testId="test-grid">
        <div>Content</div>
      </Grid>
    );

    const grid = screen.getByTestId('test-grid');
    expect(grid).toHaveClass('grid', 'grid-cols-12', 'gap-4');
  });

  it('applies custom column count', () => {
    render(
      <Grid cols={6} testId="test-grid">
        <div>Content</div>
      </Grid>
    );

    const grid = screen.getByTestId('test-grid');
    expect(grid).toHaveClass('grid-cols-6');
  });

  it('applies responsive column configuration', () => {
    render(
      <Grid cols={{ xs: 1, sm: 2, md: 3, lg: 4 }} testId="test-grid">
        <div>Content</div>
      </Grid>
    );

    const grid = screen.getByTestId('test-grid');
    expect(grid).toHaveClass('grid-cols-1', 'sm:grid-cols-2', 'md:grid-cols-3', 'lg:grid-cols-4');
  });

  it('applies custom gap', () => {
    render(
      <Grid gap={8} testId="test-grid">
        <div>Content</div>
      </Grid>
    );

    const grid = screen.getByTestId('test-grid');
    expect(grid).toHaveClass('gap-8');
  });

  it('applies custom gap with string value', () => {
    render(
      <Grid gap="2rem" testId="test-grid">
        <div>Content</div>
      </Grid>
    );

    const grid = screen.getByTestId('test-grid');
    expect(grid).toHaveClass('gap-[2rem]');
  });

  it('applies auto-fit grid with min item width', () => {
    render(
      <Grid autoFit minItemWidth="300px" testId="test-grid">
        <div>Content</div>
      </Grid>
    );

    const grid = screen.getByTestId('test-grid');
    expect(grid).toHaveClass('grid-cols-[repeat(auto-fit,minmax(var(--min-item-width),1fr))]');
    expect(grid).toHaveStyle({ '--min-item-width': '300px' });
  });

  it('applies custom className', () => {
    render(
      <Grid className="custom-class" testId="test-grid">
        <div>Content</div>
      </Grid>
    );

    const grid = screen.getByTestId('test-grid');
    expect(grid).toHaveClass('custom-class');
  });

  it('applies row configuration', () => {
    render(
      <Grid rows={3} testId="test-grid">
        <div>Content</div>
      </Grid>
    );

    const grid = screen.getByTestId('test-grid');
    expect(grid).toHaveClass('grid-rows-3');
  });
});