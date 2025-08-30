import React from 'react';
import { cn } from '../../../utils/cn';

export interface ContainerProps {
  children: React.ReactNode;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  padding?: boolean;
  centerContent?: boolean;
  testId?: string;
}

export const Container: React.FC<ContainerProps> = ({
  children,
  className,
  size = 'lg',
  padding = true,
  centerContent = false,
  testId,
}) => {
  const getContainerClasses = () => {
    const classes = ['w-full'];

    // Max width based on size
    const sizeMap = {
      'sm': 'max-w-2xl',
      'md': 'max-w-4xl',
      'lg': 'max-w-6xl',
      'xl': 'max-w-7xl',
      'full': 'max-w-full',
    };
    classes.push(sizeMap[size]);

    // Center the container
    if (size !== 'full') {
      classes.push('mx-auto');
    }

    // Add padding
    if (padding) {
      classes.push('px-4 sm:px-6 lg:px-8');
    }

    // Center content
    if (centerContent) {
      classes.push('flex items-center justify-center');
    }

    return classes.join(' ');
  };

  return (
    <div
      className={cn(getContainerClasses(), className)}
      data-testid={testId}
    >
      {children}
    </div>
  );
};

Container.displayName = 'Container';