import React from 'react';
import { cn } from '../../../utils/cn';
import { breakpoints } from '../../../tokens/breakpoints';

export interface GridProps {
  children: React.ReactNode;
  className?: string;
  cols?: number | Partial<Record<keyof typeof breakpoints, number>>;
  gap?: number | string;
  rows?: number | 'auto';
  autoFit?: boolean;
  minItemWidth?: string;
  testId?: string;
}

export const Grid: React.FC<GridProps> = ({
  children,
  className,
  cols = 12,
  gap = 4,
  rows = 'auto',
  autoFit = false,
  minItemWidth = '250px',
  testId,
}) => {
  const getGridClasses = () => {
    const classes = ['grid'];

    // Handle responsive columns
    if (typeof cols === 'number') {
      classes.push(`grid-cols-${cols}`);
    } else {
      // Responsive columns
      Object.entries(cols).forEach(([breakpoint, colCount]) => {
        if (breakpoint === 'xs') {
          classes.push(`grid-cols-${colCount}`);
        } else {
          classes.push(`${breakpoint}:grid-cols-${colCount}`);
        }
      });
    }

    // Handle rows
    if (typeof rows === 'number') {
      classes.push(`grid-rows-${rows}`);
    }

    // Handle gap
    if (typeof gap === 'number') {
      classes.push(`gap-${gap}`);
    } else {
      classes.push(`gap-[${gap}]`);
    }

    // Auto-fit grid
    if (autoFit) {
      classes.push('grid-cols-[repeat(auto-fit,minmax(var(--min-item-width),1fr))]');
    }

    return classes.join(' ');
  };

  const style = autoFit ? { '--min-item-width': minItemWidth } as React.CSSProperties : undefined;

  return (
    <div
      className={cn(getGridClasses(), className)}
      style={style}
      data-testid={testId}
    >
      {children}
    </div>
  );
};

Grid.displayName = 'Grid';