import { create } from '@storybook/theming';

export default create({
  base: 'light',
  brandTitle: 'FaktuLove Design System',
  brandUrl: 'https://faktulove.com',
  brandTarget: '_self',

  // Colors
  colorPrimary: '#2563eb', // Primary blue from design tokens
  colorSecondary: '#059669', // Success green from design tokens

  // UI
  appBg: '#ffffff',
  appContentBg: '#ffffff',
  appBorderColor: '#e5e7eb',
  appBorderRadius: 8,

  // Typography
  fontBase: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  fontCode: 'ui-monospace, SFMono-Regular, "SF Mono", Monaco, Consolas, monospace',

  // Text colors
  textColor: '#111827',
  textInverseColor: '#ffffff',

  // Toolbar default and active colors
  barTextColor: '#6b7280',
  barSelectedColor: '#2563eb',
  barBg: '#f9fafb',

  // Form colors
  inputBg: '#ffffff',
  inputBorder: '#d1d5db',
  inputTextColor: '#111827',
  inputBorderRadius: 6,
});