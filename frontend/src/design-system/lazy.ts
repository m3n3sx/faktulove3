/**
 * Lazy-loaded Design System Entry Point
 * 
 * This module provides lazy-loaded versions of all design system components
 * for optimal bundle splitting and performance.
 */

// Core utilities and tokens (always loaded)
export { cn } from './utils/cn';
export * from './tokens';
export * from './types';
export { designSystemConfig } from './config';

// Providers (always loaded for context)
export { ThemeProvider } from './providers/ThemeProvider';
export type { ThemeProviderProps } from './providers/ThemeProvider';

export { DesignSystemProvider, useDesignSystem, usePolishBusiness, useAccessibility } from './providers/DesignSystemProvider';

export { 
  DesignSystemContextProvider,
  useDesignSystemContext,
  useDesignSystemTokens,
  usePolishBusinessUtils,
  useAccessibilityUtils,
  useResponsiveUtils,
  useThemeUtils
} from './context/DesignSystemContext';

// Lazy loading utilities
export * from './utils/lazyLoading';
export { LazyLoadingManager, lazyLoadingManager } from './utils/LazyLoadingManager';

// Primitive components (loaded immediately for core functionality)
export { Button } from './components/primitives/Button/Button';
export type { ButtonProps } from './components/primitives/Button/Button';

export { Input } from './components/primitives/Input/Input';
export type { InputProps } from './components/primitives/Input/Input';

export { Typography } from './components/primitives/Typography/Typography';
export type { TypographyProps } from './components/primitives/Typography/Typography';

// Layout components (loaded on demand)
import { createLazyComponent } from './utils/lazyLoading';

export const Container = createLazyComponent(
  () => import('./components/layouts/Container/Container').then(module => ({ default: module.Container }))
);

export const Grid = createLazyComponent(
  () => import('./components/layouts/Grid/Grid').then(module => ({ default: module.Grid }))
);

export const Flex = createLazyComponent(
  () => import('./components/layouts/Flex/Flex').then(module => ({ default: module.Flex }))
);

export const Stack = createLazyComponent(
  () => import('./components/layouts/Stack/Stack').then(module => ({ default: module.Stack }))
);

// Form components (loaded when forms are detected)
export const Textarea = createLazyComponent(
  () => import('./components/primitives/Textarea/Textarea').then(module => ({ default: module.Textarea }))
);

export const Select = createLazyComponent(
  () => import('./components/primitives/Select/Select').then(module => ({ default: module.Select }))
);

export const Checkbox = createLazyComponent(
  () => import('./components/primitives/Checkbox/Checkbox').then(module => ({ default: module.Checkbox }))
);

export const Radio = createLazyComponent(
  () => import('./components/primitives/Radio/Radio').then(module => ({ default: module.Radio }))
);

export const Switch = createLazyComponent(
  () => import('./components/primitives/Switch/Switch').then(module => ({ default: module.Switch }))
);

// UI components (loaded on demand)
export const Badge = createLazyComponent(
  () => import('./components/primitives/Badge/Badge').then(module => ({ default: module.Badge }))
);

export const Progress = createLazyComponent(
  () => import('./components/primitives/Progress/Progress').then(module => ({ default: module.Progress }))
);

export const Breadcrumb = createLazyComponent(
  () => import('./components/layouts/Breadcrumb/Breadcrumb').then(module => ({ default: module.Breadcrumb }))
);

export const Sidebar = createLazyComponent(
  () => import('./components/layouts/Sidebar/Sidebar').then(module => ({ default: module.Sidebar }))
);

// Lazy-loaded component bundles
export { PolishBusinessBundle } from './components/business/lazy';
export { PatternBundle, ChartBundle, FormBundle, TableBundle, ThemeBundle } from './components/patterns/lazy';
export { AccessibilityBundle, CoreAccessibilityBundle, KeyboardNavigationBundle, ScreenReaderBundle, FormAccessibilityBundle } from './components/accessibility/lazy';

// Individual lazy components for backward compatibility
export {
  LazyCurrencyInput,
  LazyNIPValidator,
  LazyVATRateSelector,
  LazyDatePicker,
  LazyInvoiceStatusBadge,
  LazyComplianceIndicator,
  LazyPolishBusinessThemeDemo,
} from './components/business/lazy';

export {
  LazyChart,
  LazyChartCard,
  LazyFileUpload,
  LazyTable,
  LazyForm,
  LazyCard,
  LazyThemeControls,
  LazyThemeDemo,
} from './components/patterns/lazy';

export {
  LazySkipLinks,
  LazyKeyboardShortcutsHelp,
  LazyLiveRegion,
  LazyPoliteLiveRegion,
  LazyAssertiveLiveRegion,
  LazyStatusRegion,
  LazyAlertRegion,
  LazyAriaLabel,
  LazyScreenReaderOnly,
  LazyVisuallyHidden,
  LazyFormErrorAnnouncer,
  LazyPolishBusinessFormErrorAnnouncer,
} from './components/accessibility/lazy';

// Hooks (loaded on demand)
export * from './hooks';

// Utilities (loaded on demand)
export * from './utils/accessibility';
export * from './utils/responsive';
export { polishBusinessTheme, polishBusinessUtils } from './utils/theme';
export type { InvoiceStatus, VATRateType, ComplianceStatus } from './utils/theme';

// Keyboard Navigation
export * from './utils/keyboardShortcuts';
export * from './utils/focusManagement';
export * from './utils/ariaUtils';

// Integration
export { IntegrationTest } from './integration/IntegrationTest';

// Type exports for lazy components
export type { CurrencyInputProps } from './components/business/CurrencyInput/CurrencyInput';
export type { NIPValidatorProps } from './components/business/NIPValidator/NIPValidator';
export type { VATRateSelectorProps } from './components/business/VATRateSelector/VATRateSelector';
export type { DatePickerProps } from './components/business/DatePicker/DatePicker';
export type { InvoiceStatusBadgeProps } from './components/business/InvoiceStatusBadge/InvoiceStatusBadge';
export type { ComplianceIndicatorProps } from './components/business/ComplianceIndicator/ComplianceIndicator';

export type { ChartProps, ChartCardProps, ChartDataPoint } from './components/patterns/Chart/Chart';
export type { FileUploadProps, FileUploadFile } from './components/patterns/FileUpload/FileUpload';
export type { TableProps } from './components/patterns/Table/Table';
export type { FormProps } from './components/patterns/Form/Form';
export type { CardProps } from './components/patterns/Card/Card';

export type { ContainerProps } from './components/layouts/Container/Container';
export type { GridProps } from './components/layouts/Grid/Grid';
export type { FlexProps } from './components/layouts/Flex/Flex';
export type { StackProps } from './components/layouts/Stack/Stack';
export type { BreadcrumbProps } from './components/layouts/Breadcrumb/Breadcrumb';
export type { SidebarProps } from './components/layouts/Sidebar/Sidebar';

export type { TextareaProps } from './components/primitives/Textarea/Textarea';
export type { SelectProps } from './components/primitives/Select/Select';
export type { CheckboxProps } from './components/primitives/Checkbox/Checkbox';
export type { RadioProps } from './components/primitives/Radio/Radio';
export type { SwitchProps } from './components/primitives/Switch/Switch';
export type { BadgeProps, BadgeVariant } from './components/primitives/Badge/Badge';
export type { ProgressProps } from './components/primitives/Progress/Progress';

export type { SkipLinksProps } from './components/accessibility/SkipLinks/SkipLinks';
export type { KeyboardShortcutsHelpProps } from './components/accessibility/KeyboardShortcutsHelp/KeyboardShortcutsHelp';
export type { LiveRegionProps } from './components/accessibility/LiveRegion/LiveRegion';
export type { AriaLabelProps } from './components/accessibility/AriaLabel/AriaLabel';
export type { FormErrorAnnouncerProps, FormError } from './components/accessibility/FormErrorAnnouncer/FormErrorAnnouncer';