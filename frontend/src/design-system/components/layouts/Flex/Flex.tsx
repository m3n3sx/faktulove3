import React from 'react';
import { cn } from '../../../utils/cn';

export interface FlexProps {
  children: React.ReactNode;
  className?: string;
  direction?: 'row' | 'row-reverse' | 'col' | 'col-reverse';
  wrap?: 'wrap' | 'wrap-reverse' | 'nowrap';
  justify?: 'start' | 'end' | 'center' | 'between' | 'around' | 'evenly';
  align?: 'start' | 'end' | 'center' | 'baseline' | 'stretch';
  gap?: number | string;
  grow?: boolean;
  shrink?: boolean;
  testId?: string;
}

export const Flex: React.FC<FlexProps> = ({
  children,
  className,
  direction = 'row',
  wrap = 'nowrap',
  justify = 'start',
  align = 'start',
  gap = 0,
  grow = false,
  shrink = false,
  testId,
}) => {
  const getFlexClasses = () => {
    const classes = ['flex'];

    // Direction
    const directionMap = {
      'row': 'flex-row',
      'row-reverse': 'flex-row-reverse',
      'col': 'flex-col',
      'col-reverse': 'flex-col-reverse',
    };
    classes.push(directionMap[direction]);

    // Wrap
    const wrapMap = {
      'wrap': 'flex-wrap',
      'wrap-reverse': 'flex-wrap-reverse',
      'nowrap': 'flex-nowrap',
    };
    classes.push(wrapMap[wrap]);

    // Justify content
    const justifyMap = {
      'start': 'justify-start',
      'end': 'justify-end',
      'center': 'justify-center',
      'between': 'justify-between',
      'around': 'justify-around',
      'evenly': 'justify-evenly',
    };
    classes.push(justifyMap[justify]);

    // Align items
    const alignMap = {
      'start': 'items-start',
      'end': 'items-end',
      'center': 'items-center',
      'baseline': 'items-baseline',
      'stretch': 'items-stretch',
    };
    classes.push(alignMap[align]);

    // Gap
    if (typeof gap === 'number' && gap > 0) {
      classes.push(`gap-${gap}`);
    } else if (typeof gap === 'string') {
      classes.push(`gap-[${gap}]`);
    }

    // Grow and shrink
    if (grow) classes.push('flex-grow');
    if (shrink) classes.push('flex-shrink');

    return classes.join(' ');
  };

  return (
    <div
      className={cn(getFlexClasses(), className)}
      data-testid={testId}
    >
      {children}
    </div>
  );
};

Flex.displayName = 'Flex';