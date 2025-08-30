// Design System Utilities Export
export * from './theme';
export * from './themeStorage';
export * from './userPreferences';
export * from './accessibility';
export * from './responsive';
export * from './colorUtils';
export * from './typographyUtils';
export * from './spacingUtils';
export * from './testUtils';
export * from './keyboardTestPatterns';
export * from './keyboardShortcuts';
export { ariaUtils } from './ariaUtils';
export { focusUtils } from './focusManagement';
export * from './cn';

// Lazy loading utilities
export * from './lazyLoading';
export { LazyLoadingManager, lazyLoadingManager } from './LazyLoadingManager';

// Re-export testing utilities for easy access
export {
  renderWithA11y,
  testA11y,
  testA11yWithConfig,
  testPolishA11y,
  polishA11yConfig,
  keyboardTestUtils,
  screenReaderTestUtils,
  focusTestUtils,
  polishBusinessA11yTests,
  runA11yTestSuite,
} from './testUtils';