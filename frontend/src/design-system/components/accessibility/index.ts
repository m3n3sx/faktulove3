/**
 * Accessibility components export
 */

export { SkipLinks } from './SkipLinks/SkipLinks';
export type { SkipLinksProps } from './SkipLinks/SkipLinks';

export { KeyboardShortcutsHelp } from './KeyboardShortcutsHelp/KeyboardShortcutsHelp';
export type { KeyboardShortcutsHelpProps } from './KeyboardShortcutsHelp/KeyboardShortcutsHelp';

export { 
  LiveRegion, 
  PoliteLiveRegion, 
  AssertiveLiveRegion, 
  StatusRegion, 
  AlertRegion,
  useLiveRegion 
} from './LiveRegion/LiveRegion';
export type { LiveRegionProps } from './LiveRegion/LiveRegion';

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
} from './AriaLabel/AriaLabel';
export type { AriaLabelProps } from './AriaLabel/AriaLabel';

export {
  FormErrorAnnouncer,
  PolishBusinessFormErrorAnnouncer,
  useFormErrorAnnouncer,
} from './FormErrorAnnouncer/FormErrorAnnouncer';
export type { FormErrorAnnouncerProps, FormError } from './FormErrorAnnouncer/FormErrorAnnouncer';