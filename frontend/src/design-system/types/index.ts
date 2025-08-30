// Design System Type Definitions

import React from 'react';
import { designSystemConfig } from '../config';

// Base component props that all design system components should extend
export interface BaseComponentProps {
  /** Additional CSS class names */
  className?: string;
  /** Inline styles */
  style?: React.CSSProperties;
  /** Test ID for testing purposes */
  testId?: string;
  /** Children elements */
  children?: React.ReactNode;
  /** Unique identifier */
  id?: string;
}

// Size variants used across components
export type SizeVariant = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

// Color variants for semantic meaning
export type ColorVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'neutral';

// Component state variants
export type StateVariant = 'default' | 'hover' | 'active' | 'disabled' | 'loading' | 'focus';

// Visual variants for different component styles
export type VisualVariant = 'solid' | 'outline' | 'ghost' | 'link';

// Responsive value type for properties that can vary by breakpoint
export type ResponsiveValue<T> = T | {
  xs?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  '2xl'?: T;
};

// Design token types
export type ColorScale = {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;
  600: string;
  700: string;
  800: string;
  900: string;
};

export type SpacingValue = keyof typeof designSystemConfig.tokens.spacing;
export type ColorValue = keyof typeof designSystemConfig.tokens.colors;
export type BreakpointValue = keyof typeof designSystemConfig.tokens.breakpoints;
export type ShadowValue = keyof typeof designSystemConfig.tokens.shadows;
export type BorderRadiusValue = keyof typeof designSystemConfig.tokens.borderRadius;

// Component-specific prop types
export interface ButtonProps extends BaseComponentProps {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  /** Button size */
  size?: SizeVariant;
  /** Whether button is disabled */
  disabled?: boolean;
  /** Whether button is in loading state */
  loading?: boolean;
  /** Button type */
  type?: 'button' | 'submit' | 'reset';
  /** Click handler */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  /** Whether button should take full width */
  fullWidth?: boolean;
  /** Icon to display before text */
  startIcon?: React.ReactNode;
  /** Icon to display after text */
  endIcon?: React.ReactNode;
}

export interface InputProps extends BaseComponentProps {
  /** Input type */
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search';
  /** Input value */
  value?: string;
  /** Default value for uncontrolled input */
  defaultValue?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Whether input is disabled */
  disabled?: boolean;
  /** Whether input is required */
  required?: boolean;
  /** Whether input is readonly */
  readOnly?: boolean;
  /** Input size */
  size?: SizeVariant;
  /** Error state */
  error?: boolean;
  /** Error message */
  errorMessage?: string;
  /** Helper text */
  helperText?: string;
  /** Label text */
  label?: string;
  /** Change handler */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Focus handler */
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  /** Blur handler */
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  /** Icon to display in input */
  icon?: React.ReactNode;
  /** Icon position */
  iconPosition?: 'start' | 'end';
}

export interface SelectProps extends BaseComponentProps {
  /** Select value */
  value?: string | string[];
  /** Default value for uncontrolled select */
  defaultValue?: string | string[];
  /** Placeholder text */
  placeholder?: string;
  /** Whether select is disabled */
  disabled?: boolean;
  /** Whether select is required */
  required?: boolean;
  /** Whether multiple selection is allowed */
  multiple?: boolean;
  /** Select size */
  size?: SizeVariant;
  /** Error state */
  error?: boolean;
  /** Error message */
  errorMessage?: string;
  /** Helper text */
  helperText?: string;
  /** Label text */
  label?: string;
  /** Options */
  options: Array<{
    value: string;
    label: string;
    disabled?: boolean;
  }>;
  /** Change handler */
  onChange?: (value: string | string[]) => void;
  /** Search functionality */
  searchable?: boolean;
  /** Clear functionality */
  clearable?: boolean;
}

export interface CardProps extends BaseComponentProps {
  /** Card variant */
  variant?: 'default' | 'outlined' | 'elevated';
  /** Card padding */
  padding?: SpacingValue;
  /** Whether card is interactive */
  interactive?: boolean;
  /** Click handler for interactive cards */
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void;
}

export interface ModalProps extends BaseComponentProps {
  /** Whether modal is open */
  open: boolean;
  /** Close handler */
  onClose: () => void;
  /** Modal title */
  title?: string;
  /** Modal size */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Whether modal can be closed by clicking backdrop */
  closeOnBackdropClick?: boolean;
  /** Whether modal can be closed by pressing escape */
  closeOnEscape?: boolean;
  /** Whether to show close button */
  showCloseButton?: boolean;
  /** Footer content */
  footer?: React.ReactNode;
}

export interface ToastProps extends BaseComponentProps {
  /** Toast type */
  type?: 'success' | 'error' | 'warning' | 'info';
  /** Toast title */
  title?: string;
  /** Toast message */
  message: string;
  /** Whether toast is visible */
  visible: boolean;
  /** Duration in milliseconds (0 for persistent) */
  duration?: number;
  /** Close handler */
  onClose?: () => void;
  /** Action button */
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Polish business-specific types
export interface PolishCurrencyProps {
  /** Amount in PLN */
  amount: number;
  /** Whether to show currency symbol */
  showSymbol?: boolean;
  /** Number of decimal places */
  decimals?: number;
  /** Locale for formatting */
  locale?: string;
}

export interface PolishDateProps {
  /** Date to format */
  date: Date | string;
  /** Date format */
  format?: 'short' | 'long' | 'numeric';
  /** Locale for formatting */
  locale?: string;
}

export interface NIPValidatorProps {
  /** NIP number to validate */
  nip: string;
  /** Whether to format NIP with dashes */
  formatted?: boolean;
  /** Validation callback */
  onValidation?: (isValid: boolean) => void;
}

export interface InvoiceStatusProps {
  /** Invoice status */
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  /** Custom status label */
  label?: string;
  /** Show status icon */
  showIcon?: boolean;
}

export interface VATRateProps {
  /** VAT rate (0-1 for percentage, -1 for exempt) */
  rate: number;
  /** Whether to show percentage symbol */
  showPercent?: boolean;
  /** Custom label for exempt */
  exemptLabel?: string;
}

// Form-related types
export interface FormFieldProps extends BaseComponentProps {
  /** Field name */
  name: string;
  /** Field label */
  label?: string;
  /** Whether field is required */
  required?: boolean;
  /** Error message */
  error?: string;
  /** Helper text */
  helperText?: string;
  /** Field description */
  description?: string;
}

export interface FormProps extends BaseComponentProps {
  /** Form submit handler */
  onSubmit?: (event: React.FormEvent<HTMLFormElement>) => void;
  /** Whether form is in loading state */
  loading?: boolean;
  /** Form validation errors */
  errors?: Record<string, string>;
  /** Form layout */
  layout?: 'vertical' | 'horizontal' | 'inline';
}

// Layout types
export interface ContainerProps extends BaseComponentProps {
  /** Container max width */
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Container padding */
  padding?: SpacingValue;
  /** Whether container is centered */
  centered?: boolean;
}

export interface GridProps extends BaseComponentProps {
  /** Number of columns */
  columns?: ResponsiveValue<number>;
  /** Grid gap */
  gap?: SpacingValue;
  /** Grid template areas */
  areas?: string[];
  /** Grid auto flow */
  autoFlow?: 'row' | 'column' | 'dense';
}

export interface FlexProps extends BaseComponentProps {
  /** Flex direction */
  direction?: ResponsiveValue<'row' | 'column' | 'row-reverse' | 'column-reverse'>;
  /** Justify content */
  justify?: ResponsiveValue<'start' | 'end' | 'center' | 'between' | 'around' | 'evenly'>;
  /** Align items */
  align?: ResponsiveValue<'start' | 'end' | 'center' | 'baseline' | 'stretch'>;
  /** Flex wrap */
  wrap?: ResponsiveValue<'nowrap' | 'wrap' | 'wrap-reverse'>;
  /** Gap between items */
  gap?: SpacingValue;
}

// Accessibility types
export interface AccessibilityProps {
  /** ARIA label */
  'aria-label'?: string;
  /** ARIA labelledby */
  'aria-labelledby'?: string;
  /** ARIA describedby */
  'aria-describedby'?: string;
  /** ARIA expanded */
  'aria-expanded'?: boolean;
  /** ARIA selected */
  'aria-selected'?: boolean;
  /** ARIA checked */
  'aria-checked'?: boolean;
  /** ARIA disabled */
  'aria-disabled'?: boolean;
  /** ARIA hidden */
  'aria-hidden'?: boolean;
  /** ARIA live region */
  'aria-live'?: 'polite' | 'assertive' | 'off';
  /** Role */
  role?: string;
  /** Tab index */
  tabIndex?: number;
}

// Event handler types
export type ClickHandler = (event: React.MouseEvent) => void;
export type ChangeHandler<T = string> = (value: T) => void;
export type FocusHandler = (event: React.FocusEvent) => void;
export type KeyboardHandler = (event: React.KeyboardEvent) => void;

// Component ref types
export type ButtonRef = React.RefObject<HTMLButtonElement>;
export type InputRef = React.RefObject<HTMLInputElement>;
export type DivRef = React.RefObject<HTMLDivElement>;

// Theme types
export type ThemeMode = 'light' | 'dark' | 'auto';
export type ThemeContext = {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  tokens: typeof designSystemConfig.tokens;
  semantic: typeof designSystemConfig.semantic;
};

// Export all types
export type {
  BaseComponentProps,
  SizeVariant,
  ColorVariant,
  StateVariant,
  VisualVariant,
  ResponsiveValue,
  ColorScale,
  SpacingValue,
  ColorValue,
  BreakpointValue,
  ShadowValue,
  BorderRadiusValue,
};

// Default export for convenience - using type-only exports
// Note: TypeScript types cannot be included in default exports as values
// All types are available as named exports above