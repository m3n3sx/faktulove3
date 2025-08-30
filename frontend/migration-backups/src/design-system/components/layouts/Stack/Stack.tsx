import React from 'react';
import { cn } from '../../../utils/cn';

export interface StackProps {
  children: React.ReactNode;
  className?: string;
  direction?: 'vertical' | 'horizontal';
  spacing?: number | string;
  align?: 'start' | 'end' | 'center' | 'stretch';
  divider?: React.ReactNode;
  testId?: string;
}

export const Stack: React.FC<StackProps> = ({
  children,
  className,
  direction = 'vertical',
  spacing = 4,
  align = 'stretch',
  divider,
  testId,
}) => {
  const getStackClasses = () => {
    const classes = ['flex'];

    // Direction
    if (direction === 'vertical') {
      classes.push('flex-col');
    } else {
      classes.push('flex-row');
    }

    // Alignment
    const alignMap = {
      'start': direction === 'vertical' ? 'items-start' : 'justify-start',
      'end': direction === 'vertical' ? 'items-end' : 'justify-end',
      'center': direction === 'vertical' ? 'items-center' : 'justify-center',
      'stretch': direction === 'vertical' ? 'items-stretch' : 'justify-stretch',
    };
    classes.push(alignMap[align]);

    // Spacing
    if (typeof spacing === 'number') {
      classes.push(`gap-${spacing}`);
    } else {
      classes.push(`gap-[${spacing}]`);
    }

    return classes.join(' ');
  };

  const childrenArray = React.Children.toArray(children);

  if (divider && childrenArray.length > 1) {
    const childrenWithDividers = childrenArray.reduce<React.ReactNode[]>((acc, child, index) => {
      acc.push(child);
      if (index < childrenArray.length - 1) {
        acc.push(
          <div key={`divider-${index}`} className="flex-shrink-0">
            {divider}
          </div>
        );
      }
      return acc;
    }, []);

    return (
      <div
        className={cn(getStackClasses().replace(/gap-\S+/, ''), className)}
        data-testid={testId}
      >
        {childrenWithDividers}
      </div>
    );
  }

  return (
    <div
      className={cn(getStackClasses(), className)}
      data-testid={testId}
    >
      {children}
    </div>
  );
};

Stack.displayName = 'Stack';