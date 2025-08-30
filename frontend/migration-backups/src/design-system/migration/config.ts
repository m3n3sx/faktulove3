/**
 * Migration Configuration
 * 
 * Configuration for migrating existing FaktuLove components to the design system.
 */

import type { ComponentMapping, StyleMapping } from './types';

/**
 * Component mappings from legacy to design system components
 */
export const componentMappings: ComponentMapping[] = [
  // Button mappings
  {
    from: 'button.bg-primary-600',
    to: 'Button',
    transformProps: (props) => ({
      ...props,
      variant: 'primary',
      size: props.className?.includes('px-4 py-2') ? 'md' : 'lg'
    }),
    notes: 'Primary buttons should use variant="primary"'
  },
  {
    from: 'button.border.border-gray-300',
    to: 'Button',
    transformProps: (props) => ({
      ...props,
      variant: 'secondary'
    }),
    notes: 'Secondary buttons should use variant="secondary"'
  },
  
  // Input mappings
  {
    from: 'input[type="text"]',
    to: 'Input',
    transformProps: (props) => ({
      ...props,
      variant: props.className?.includes('border-red') ? 'error' : 'default'
    })
  },
  {
    from: 'input[type="email"]',
    to: 'Input',
    transformProps: (props) => ({
      ...props,
      type: 'email'
    })
  },
  
  // Layout mappings
  {
    from: 'div.max-w-7xl.mx-auto',
    to: 'Container',
    transformProps: (props) => ({
      ...props,
      maxWidth: '7xl'
    })
  },
  {
    from: 'div.grid.grid-cols-',
    to: 'Grid',
    transformProps: (props) => {
      const cols = props.className?.match(/grid-cols-(\d+)/)?.[1];
      return {
        ...props,
        cols: cols ? parseInt(cols) : 1
      };
    }
  }
];

/**
 * Style mappings from legacy classes to design system tokens
 */
export const styleMappings: StyleMapping[] = [
  // Color mappings
  { from: 'text-primary-600', to: 'text-primary-600', deprecated: false },
  { from: 'bg-primary-600', to: 'bg-primary-600', deprecated: false },
  { from: 'text-green-600', to: 'text-success-600', deprecated: true, warning: 'Use text-success-600 instead' },
  { from: 'bg-green-600', to: 'bg-success-600', deprecated: true, warning: 'Use bg-success-600 instead' },
  { from: 'text-red-600', to: 'text-error-600', deprecated: true, warning: 'Use text-error-600 instead' },
  { from: 'bg-red-600', to: 'bg-error-600', deprecated: true, warning: 'Use bg-error-600 instead' },
  { from: 'text-yellow-600', to: 'text-warning-600', deprecated: true, warning: 'Use text-warning-600 instead' },
  { from: 'bg-yellow-600', to: 'bg-warning-600', deprecated: true, warning: 'Use bg-warning-600 instead' },
  
  // Spacing mappings (8px grid system)
  { from: 'p-1', to: 'p-1', deprecated: false },
  { from: 'p-2', to: 'p-2', deprecated: false },
  { from: 'p-3', to: 'p-3', deprecated: false },
  { from: 'p-4', to: 'p-4', deprecated: false },
  { from: 'p-5', to: 'p-5', deprecated: true, warning: 'Use p-4 or p-6 for 8px grid alignment' },
  { from: 'p-6', to: 'p-6', deprecated: false },
  
  // Typography mappings
  { from: 'text-sm', to: 'text-sm', deprecated: false },
  { from: 'text-base', to: 'text-base', deprecated: false },
  { from: 'text-lg', to: 'text-lg', deprecated: false },
  { from: 'text-xl', to: 'text-xl', deprecated: false },
  { from: 'text-2xl', to: 'text-2xl', deprecated: false },
  
  // Border radius mappings
  { from: 'rounded', to: 'rounded-md', deprecated: true, warning: 'Use rounded-md for consistency' },
  { from: 'rounded-sm', to: 'rounded-sm', deprecated: false },
  { from: 'rounded-md', to: 'rounded-md', deprecated: false },
  { from: 'rounded-lg', to: 'rounded-lg', deprecated: false },
  
  // Shadow mappings
  { from: 'shadow', to: 'shadow-sm', deprecated: true, warning: 'Use shadow-sm for consistency' },
  { from: 'shadow-sm', to: 'shadow-sm', deprecated: false },
  { from: 'shadow-md', to: 'shadow-md', deprecated: false },
  { from: 'shadow-lg', to: 'shadow-lg', deprecated: false }
];

/**
 * Polish business-specific component mappings
 */
export const polishBusinessMappings: ComponentMapping[] = [
  {
    from: 'input[data-currency="PLN"]',
    to: 'CurrencyInput',
    transformProps: (props) => ({
      ...props,
      currency: 'PLN'
    }),
    notes: 'Use CurrencyInput for Polish currency formatting'
  },
  {
    from: 'input[data-nip]',
    to: 'NIPValidator',
    transformProps: (props) => ({
      ...props,
      validateOnChange: true
    }),
    notes: 'Use NIPValidator for Polish tax number validation'
  },
  {
    from: 'select[data-vat-rates]',
    to: 'VATRateSelector',
    transformProps: (props) => ({
      ...props,
      rates: ['23%', '8%', '5%', '0%']
    }),
    notes: 'Use VATRateSelector for Polish VAT rates'
  }
];

/**
 * Default migration configuration
 */
export const migrationConfig = {
  componentMappings: [...componentMappings, ...polishBusinessMappings],
  styleMappings,
  options: {
    gradual: true,
    preserveClasses: true,
    warnings: process.env.NODE_ENV === 'development'
  }
};