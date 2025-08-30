/**
 * FaktuLove Design System
 * Main export file for all design system components and utilities
 */

// Primitive Components
export { Button } from './components/primitives/Button/Button';
export type { ButtonProps } from './components/primitives/Button/Button';

export { Input } from './components/primitives/Input/Input';
export type { InputProps } from './components/primitives/Input/Input';

export { Textarea } from './components/primitives/Textarea/Textarea';
export type { TextareaProps } from './components/primitives/Textarea/Textarea';

export { Select } from './components/primitives/Select/Select';
export type { SelectProps } from './components/primitives/Select/Select';

export { Checkbox } from './components/primitives/Checkbox/Checkbox';
export type { CheckboxProps } from './components/primitives/Checkbox/Checkbox';

export { Radio } from './components/primitives/Radio/Radio';
export type { RadioProps } from './components/primitives/Radio/Radio';

export { Switch } from './components/primitives/Switch/Switch';
export type { SwitchProps } from './components/primitives/Switch/Switch';

export { Badge } from './components/primitives/Badge/Badge';
export type { BadgeProps, BadgeVariant } from './components/primitives/Badge/Badge';

export { Progress } from './components/primitives/Progress/Progress';
export type { ProgressProps } from './components/primitives/Progress/Progress';

export { Typography } from './components/primitives/Typography/Typography';
export type { TypographyProps } from './components/primitives/Typography/Typography';

// Layout Components
export { Container } from './components/layouts/Container/Container';
export type { ContainerProps } from './components/layouts/Container/Container';

export { Grid } from './components/layouts/Grid/Grid';
export type { GridProps } from './components/layouts/Grid/Grid';

export { Flex } from './components/layouts/Flex/Flex';
export type { FlexProps } from './components/layouts/Flex/Flex';

export { Stack } from './components/layouts/Stack/Stack';
export type { StackProps } from './components/layouts/Stack/Stack';

export { Breadcrumb } from './components/layouts/Breadcrumb/Breadcrumb';
export type { BreadcrumbProps } from './components/layouts/Breadcrumb/Breadcrumb';

export { Sidebar } from './components/layouts/Sidebar/Sidebar';
export type { SidebarProps } from './components/layouts/Sidebar/Sidebar';

// Pattern Components
export { Card } from './components/patterns/Card/Card';
export type { CardProps } from './components/patterns/Card/Card';

export { Table } from './components/patterns/Table/Table';
export type { TableProps } from './components/patterns/Table/Table';

export { Form } from './components/patterns/Form/Form';
export type { FormProps } from './components/patterns/Form/Form';

export { FileUpload } from './components/patterns/FileUpload/FileUpload';
export type { FileUploadProps, FileUploadFile } from './components/patterns/FileUpload/FileUpload';

export { Chart, ChartCard } from './components/patterns/Chart/Chart';
export type { ChartProps, ChartCardProps, ChartDataPoint } from './components/patterns/Chart/Chart';

// Business Components
export { CurrencyInput } from './components/business/CurrencyInput/CurrencyInput';
export type { CurrencyInputProps } from './components/business/CurrencyInput/CurrencyInput';

export { NIPValidator } from './components/business/NIPValidator/NIPValidator';
export type { NIPValidatorProps } from './components/business/NIPValidator/NIPValidator';

export { VATRateSelector } from './components/business/VATRateSelector/VATRateSelector';
export type { VATRateSelectorProps } from './components/business/VATRateSelector/VATRateSelector';

export { DatePicker } from './components/business/DatePicker/DatePicker';
export type { DatePickerProps } from './components/business/DatePicker/DatePicker';

export { InvoiceStatusBadge } from './components/business/InvoiceStatusBadge/InvoiceStatusBadge';
export type { InvoiceStatusBadgeProps } from './components/business/InvoiceStatusBadge/InvoiceStatusBadge';

export { ComplianceIndicator } from './components/business/ComplianceIndicator/ComplianceIndicator';
export type { ComplianceIndicatorProps } from './components/business/ComplianceIndicator/ComplianceIndicator';

export { PolishBusinessThemeDemo } from './components/business/PolishBusinessThemeDemo/PolishBusinessThemeDemo';
export type { PolishBusinessThemeDemoProps } from './components/business/PolishBusinessThemeDemo/PolishBusinessThemeDemo';

// Accessibility Components
export { SkipLinks } from './components/accessibility/SkipLinks/SkipLinks';
export type { SkipLinksProps } from './components/accessibility/SkipLinks/SkipLinks';

export { KeyboardShortcutsHelp } from './components/accessibility/KeyboardShortcutsHelp/KeyboardShortcutsHelp';
export type { KeyboardShortcutsHelpProps } from './components/accessibility/KeyboardShortcutsHelp/KeyboardShortcutsHelp';

export { 
  LiveRegion, 
  PoliteLiveRegion, 
  AssertiveLiveRegion, 
  StatusRegion, 
  AlertRegion,
  useLiveRegion 
} from './components/accessibility/LiveRegion/LiveRegion';
export type { LiveRegionProps } from './components/accessibility/LiveRegion/LiveRegion';

export {
  AriaLabel,
  NIPLabel,
  CurrencyLabel,
  DateLabel,
  VATLabel,
  InvoiceNumberLabel,
  ScreenReaderOnly,
  VisuallyHidden,
  AriaDescription,
  AriaErrorMessage,
  LoadingAnnouncement,
  SuccessAnnouncement,
  ProgressAnnouncement,
} from './components/accessibility/AriaLabel/AriaLabel';
export type { AriaLabelProps } from './components/accessibility/AriaLabel/AriaLabel';

export {
  FormErrorAnnouncer,
  PolishBusinessFormErrorAnnouncer,
  useFormErrorAnnouncer,
} from './components/accessibility/FormErrorAnnouncer/FormErrorAnnouncer';
export type { FormErrorAnnouncerProps, FormError } from './components/accessibility/FormErrorAnnouncer/FormErrorAnnouncer';

// Providers
export { ThemeProvider } from './providers/ThemeProvider';
export type { ThemeProviderProps } from './providers/ThemeProvider';

export { DesignSystemProvider, useDesignSystem, usePolishBusiness, useAccessibility } from './providers/DesignSystemProvider';

// Context
export { 
  DesignSystemContextProvider,
  useDesignSystemContext,
  useDesignSystemTokens,
  usePolishBusinessUtils,
  useAccessibilityUtils,
  useResponsiveUtils,
  useThemeUtils
} from './context/DesignSystemContext';

// Utilities
export { cn } from './utils/cn';
export * from './utils/accessibility';
export * from './utils/responsive';
export { polishBusinessTheme, polishBusinessUtils } from './utils/theme';
export type { InvoiceStatus, VATRateType, ComplianceStatus } from './utils/theme';

// Keyboard Navigation
export * from './utils/keyboardShortcuts';
export { focusUtils, ModalFocusManager, DropdownFocusManager, RovingTabindexManager, PolishFormFocusManager } from './utils/focusManagement';
export { ariaUtils, generateAriaAttributes, polishAriaLabels, ScreenReaderAnnouncer, FocusManager, ARIA_ROLES, ARIA_PROPERTIES } from './utils/ariaUtils';

// Hooks
export { useFocusTrap, useDropdownNavigation, useRovingTabindex, useArrowNavigation, useKeyboardNavigationState, useSkipLinks, usePolishFormNavigation, useTableNavigation, useFocusRestoration } from './hooks/useKeyboardNavigation';
export { useKeyboardShortcuts as useKeyboardShortcutsHook } from './hooks/useKeyboardNavigation';

// Tokens
export * from './tokens';

// Types
export * from './types';

// Configuration
export { designSystemConfig } from './config';

// Integration
export { IntegrationTest } from './integration/IntegrationTest';