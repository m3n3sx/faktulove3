import React from 'react';
import { cn } from '../../../utils/cn';
import { typographyStyles, TypographyStyleKey } from '../../../tokens/typography';

export interface TypographyProps {
  children: React.ReactNode;
  variant?: TypographyStyleKey;
  as?: keyof JSX.IntrinsicElements;
  className?: string;
  color?: 'primary' | 'secondary' | 'muted' | 'success' | 'warning' | 'error';
  testId?: string;
}

const colorClasses = {
  primary: 'text-neutral-900',
  secondary: 'text-neutral-700',
  muted: 'text-neutral-500',
  success: 'text-success-600',
  warning: 'text-warning-600',
  error: 'text-error-600',
} as const;

export const Typography: React.FC<TypographyProps> = ({
  children,
  variant = 'body',
  as,
  className,
  color = 'primary',
  testId,
  ...props
}) => {
  // Determine the HTML element to render
  const getDefaultElement = (): keyof JSX.IntrinsicElements => {
    if (variant.startsWith('h')) return variant as keyof JSX.IntrinsicElements;
    if (variant === 'caption' || variant === 'label') return 'span';
    if (variant === 'code') return 'code';
    return 'p';
  };

  const Element = as || getDefaultElement();
  const style = typographyStyles[variant];
  
  // Convert style object to CSS classes
  const getTypographyClasses = () => {
    const classes: string[] = [];
    
    // Font size mapping
    const fontSizeMap: Record<string, string> = {
      '0.75rem': 'text-xs',
      '0.875rem': 'text-sm',
      '1rem': 'text-base',
      '1.125rem': 'text-lg',
      '1.25rem': 'text-xl',
      '1.5rem': 'text-2xl',
      '1.875rem': 'text-3xl',
      '2.25rem': 'text-4xl',
      '3rem': 'text-5xl',
      '3.75rem': 'text-6xl',
    };
    
    // Font weight mapping
    const fontWeightMap: Record<number, string> = {
      100: 'font-thin',
      200: 'font-extralight',
      300: 'font-light',
      400: 'font-normal',
      500: 'font-medium',
      600: 'font-semibold',
      700: 'font-bold',
      800: 'font-extrabold',
      900: 'font-black',
    };
    
    // Line height mapping
    const lineHeightMap: Record<number, string> = {
      1: 'leading-none',
      1.25: 'leading-tight',
      1.375: 'leading-snug',
      1.5: 'leading-normal',
      1.625: 'leading-relaxed',
      2: 'leading-loose',
    };
    
    if (style.fontSize && fontSizeMap[style.fontSize]) {
      classes.push(fontSizeMap[style.fontSize]);
    }
    
    if (style.fontWeight && fontWeightMap[style.fontWeight]) {
      classes.push(fontWeightMap[style.fontWeight]);
    }
    
    if (style.lineHeight && lineHeightMap[style.lineHeight]) {
      classes.push(lineHeightMap[style.lineHeight]);
    }
    
    if (style.textTransform === 'uppercase') {
      classes.push('uppercase');
    }
    
    if (style.textAlign === 'center') {
      classes.push('text-center');
    } else if (style.textAlign === 'right') {
      classes.push('text-right');
    }
    
    if (style.textDecoration === 'underline') {
      classes.push('underline');
    }
    
    return classes.join(' ');
  };

  return (
    <Element
      className={cn(
        getTypographyClasses(),
        colorClasses[color],
        className
      )}
      data-testid={testId}
      {...props}
    >
      {children}
    </Element>
  );
};

Typography.displayName = 'Typography';