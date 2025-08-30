// Design System Main Export
export * from './tokens';
export * from './components';
export * from './utils';
export * from './providers';
export * from './config';
export * from './types';

// Re-export commonly used items for convenience
export { designSystemConfig as config } from './config';
export { theme } from './utils/theme';
export { ThemeProvider, useTheme, useThemeUtils } from './providers';

// Export design system version
export const DESIGN_SYSTEM_VERSION = '1.0.0';