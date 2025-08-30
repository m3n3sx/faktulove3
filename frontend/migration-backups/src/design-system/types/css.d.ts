// CSS Module and Custom Properties Type Definitions

declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

declare module '*.scss' {
  const content: { [className: string]: string };
  export default content;
}

declare module '*.sass' {
  const content: { [className: string]: string };
  export default content;
}

// CSS Custom Properties interface
export interface CSSCustomProperties {
  // Color properties
  '--color-primary-50'?: string;
  '--color-primary-100'?: string;
  '--color-primary-200'?: string;
  '--color-primary-300'?: string;
  '--color-primary-400'?: string;
  '--color-primary-500'?: string;
  '--color-primary-600'?: string;
  '--color-primary-700'?: string;
  '--color-primary-800'?: string;
  '--color-primary-900'?: string;
  
  '--color-text-primary'?: string;
  '--color-text-secondary'?: string;
  '--color-text-muted'?: string;
  '--color-text-inverse'?: string;
  
  '--color-background-primary'?: string;
  '--color-background-secondary'?: string;
  '--color-background-muted'?: string;
  '--color-background-inverse'?: string;
  
  '--color-border-default'?: string;
  '--color-border-muted'?: string;
  '--color-border-strong'?: string;
  
  '--color-interactive'?: string;
  '--color-interactive-hover'?: string;
  '--color-interactive-active'?: string;
  '--color-interactive-disabled'?: string;
  
  // Typography properties
  '--font-family-sans'?: string;
  '--font-family-serif'?: string;
  '--font-family-mono'?: string;
  
  '--font-size-xs'?: string;
  '--font-size-sm'?: string;
  '--font-size-base'?: string;
  '--font-size-lg'?: string;
  '--font-size-xl'?: string;
  '--font-size-2xl'?: string;
  '--font-size-3xl'?: string;
  '--font-size-4xl'?: string;
  '--font-size-5xl'?: string;
  '--font-size-6xl'?: string;
  
  // Spacing properties
  '--spacing-0'?: string;
  '--spacing-px'?: string;
  '--spacing-0_5'?: string;
  '--spacing-1'?: string;
  '--spacing-2'?: string;
  '--spacing-3'?: string;
  '--spacing-4'?: string;
  '--spacing-5'?: string;
  '--spacing-6'?: string;
  '--spacing-8'?: string;
  '--spacing-10'?: string;
  '--spacing-12'?: string;
  '--spacing-16'?: string;
  '--spacing-20'?: string;
  '--spacing-24'?: string;
  '--spacing-32'?: string;
  
  // Shadow properties
  '--shadow-none'?: string;
  '--shadow-xs'?: string;
  '--shadow-sm'?: string;
  '--shadow-md'?: string;
  '--shadow-lg'?: string;
  '--shadow-xl'?: string;
  '--shadow-2xl'?: string;
  '--shadow-inner'?: string;
  
  // Focus ring properties
  '--focus-ring-default'?: string;
  '--focus-ring-success'?: string;
  '--focus-ring-warning'?: string;
  '--focus-ring-error'?: string;
  '--focus-ring-neutral'?: string;
  
  // Border radius properties
  '--border-radius-none'?: string;
  '--border-radius-xs'?: string;
  '--border-radius-sm'?: string;
  '--border-radius-md'?: string;
  '--border-radius-lg'?: string;
  '--border-radius-xl'?: string;
  '--border-radius-2xl'?: string;
  '--border-radius-3xl'?: string;
  '--border-radius-full'?: string;
  
  // Animation properties
  '--animation-duration-fast'?: string;
  '--animation-duration-normal'?: string;
  '--animation-duration-slow'?: string;
  
  // Z-index properties
  '--z-index-dropdown'?: string;
  '--z-index-sticky'?: string;
  '--z-index-modal'?: string;
  '--z-index-popover'?: string;
  '--z-index-tooltip'?: string;
}

// Extend React CSSProperties to include custom properties
declare module 'react' {
  interface CSSProperties extends CSSCustomProperties {}
}

// CSS-in-JS style object type
export type StyleObject = React.CSSProperties & CSSCustomProperties;

// Utility type for component style props
export type ComponentStyleProps = {
  style?: StyleObject;
  className?: string;
};

// Theme-aware style function type
export type ThemeStyleFunction<T = any> = (theme: any) => T;

// Responsive style value type
export type ResponsiveStyleValue<T> = T | {
  xs?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  '2xl'?: T;
};

// CSS variable utility type
export type CSSVariable = `--${string}`;

// Design system CSS class names
export type DesignSystemClassName = 
  | 'sr-only'
  | 'focus-visible'
  | 'text-primary'
  | 'text-secondary'
  | 'text-muted'
  | 'bg-primary'
  | 'bg-secondary'
  | 'border-default'
  | 'interactive'
  | 'container'
  | 'currency'
  | 'date-polish'
  | 'nip-format'
  | 'invoice-number'
  | 'status-badge'
  | 'animate-fade-in'
  | 'animate-slide-up'
  | 'loading'
  | 'truncate'
  | 'print-only'
  | 'no-print';

export default CSSCustomProperties;