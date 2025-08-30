/**
 * Lazy-loaded Accessibility Components
 * 
 * This module provides lazy-loaded versions of accessibility components
 * to optimize bundle size while ensuring accessibility features are available when needed.
 */

import { createLazyComponent } from '../../utils/lazyLoading';

// Lazy load accessibility components
export const LazySkipLinks = createLazyComponent(
  () => import('./SkipLinks/SkipLinks').then(module => ({ default: module.SkipLinks }))
);

export const LazyKeyboardShortcutsHelp = createLazyComponent(
  () => import('./KeyboardShortcutsHelp/KeyboardShortcutsHelp').then(module => ({ default: module.KeyboardShortcutsHelp }))
);

export const LazyLiveRegion = createLazyComponent(
  () => import('./LiveRegion/LiveRegion').then(module => ({ default: module.LiveRegion }))
);

export const LazyPoliteLiveRegion = createLazyComponent(
  () => import('./LiveRegion/LiveRegion').then(module => ({ default: module.PoliteLiveRegion }))
);

export const LazyAssertiveLiveRegion = createLazyComponent(
  () => import('./LiveRegion/LiveRegion').then(module => ({ default: module.AssertiveLiveRegion }))
);

export const LazyStatusRegion = createLazyComponent(
  () => import('./LiveRegion/LiveRegion').then(module => ({ default: module.StatusRegion }))
);

export const LazyAlertRegion = createLazyComponent(
  () => import('./LiveRegion/LiveRegion').then(module => ({ default: module.AlertRegion }))
);

export const LazyAriaLabel = createLazyComponent(
  () => import('./AriaLabel/AriaLabel').then(module => ({ default: module.AriaLabel }))
);

export const LazyScreenReaderOnly = createLazyComponent(
  () => import('./AriaLabel/AriaLabel').then(module => ({ default: module.ScreenReaderOnly }))
);

export const LazyVisuallyHidden = createLazyComponent(
  () => import('./AriaLabel/AriaLabel').then(module => ({ default: module.VisuallyHidden }))
);

export const LazyFormErrorAnnouncer = createLazyComponent(
  () => import('./FormErrorAnnouncer/FormErrorAnnouncer').then(module => ({ default: module.FormErrorAnnouncer }))
);

export const LazyPolishBusinessFormErrorAnnouncer = createLazyComponent(
  () => import('./FormErrorAnnouncer/FormErrorAnnouncer').then(module => ({ default: module.PolishBusinessFormErrorAnnouncer }))
);

// Preload core accessibility components
export function preloadCoreAccessibilityComponents(): Promise<any[]> {
  return Promise.all([
    LazySkipLinks.preload(),
    LazyLiveRegion.preload(),
    LazyAriaLabel.preload(),
    LazyScreenReaderOnly.preload(),
  ]);
}

// Preload keyboard navigation components
export function preloadKeyboardNavigationComponents(): Promise<any[]> {
  return Promise.all([
    LazyKeyboardShortcutsHelp.preload(),
    LazySkipLinks.preload(),
  ]);
}

// Preload screen reader components
export function preloadScreenReaderComponents(): Promise<any[]> {
  return Promise.all([
    LazyLiveRegion.preload(),
    LazyPoliteLiveRegion.preload(),
    LazyAssertiveLiveRegion.preload(),
    LazyStatusRegion.preload(),
    LazyAlertRegion.preload(),
    LazyAriaLabel.preload(),
    LazyScreenReaderOnly.preload(),
    LazyVisuallyHidden.preload(),
  ]);
}

// Preload form accessibility components
export function preloadFormAccessibilityComponents(): Promise<any[]> {
  return Promise.all([
    LazyFormErrorAnnouncer.preload(),
    LazyPolishBusinessFormErrorAnnouncer.preload(),
    LazyAriaLabel.preload(),
  ]);
}

// Accessibility component bundles
export const CoreAccessibilityBundle = {
  SkipLinks: LazySkipLinks,
  LiveRegion: LazyLiveRegion,
  AriaLabel: LazyAriaLabel,
  ScreenReaderOnly: LazyScreenReaderOnly,
  preload: preloadCoreAccessibilityComponents,
};

export const KeyboardNavigationBundle = {
  KeyboardShortcutsHelp: LazyKeyboardShortcutsHelp,
  SkipLinks: LazySkipLinks,
  preload: preloadKeyboardNavigationComponents,
};

export const ScreenReaderBundle = {
  LiveRegion: LazyLiveRegion,
  PoliteLiveRegion: LazyPoliteLiveRegion,
  AssertiveLiveRegion: LazyAssertiveLiveRegion,
  StatusRegion: LazyStatusRegion,
  AlertRegion: LazyAlertRegion,
  AriaLabel: LazyAriaLabel,
  ScreenReaderOnly: LazyScreenReaderOnly,
  VisuallyHidden: LazyVisuallyHidden,
  preload: preloadScreenReaderComponents,
};

export const FormAccessibilityBundle = {
  FormErrorAnnouncer: LazyFormErrorAnnouncer,
  PolishBusinessFormErrorAnnouncer: LazyPolishBusinessFormErrorAnnouncer,
  AriaLabel: LazyAriaLabel,
  preload: preloadFormAccessibilityComponents,
};

export const AccessibilityBundle = {
  // Core components
  SkipLinks: LazySkipLinks,
  KeyboardShortcutsHelp: LazyKeyboardShortcutsHelp,
  
  // Live regions
  LiveRegion: LazyLiveRegion,
  PoliteLiveRegion: LazyPoliteLiveRegion,
  AssertiveLiveRegion: LazyAssertiveLiveRegion,
  StatusRegion: LazyStatusRegion,
  AlertRegion: LazyAlertRegion,
  
  // ARIA components
  AriaLabel: LazyAriaLabel,
  ScreenReaderOnly: LazyScreenReaderOnly,
  VisuallyHidden: LazyVisuallyHidden,
  
  // Form accessibility
  FormErrorAnnouncer: LazyFormErrorAnnouncer,
  PolishBusinessFormErrorAnnouncer: LazyPolishBusinessFormErrorAnnouncer,
  
  // Bundle preloaders
  preloadCore: preloadCoreAccessibilityComponents,
  preloadKeyboard: preloadKeyboardNavigationComponents,
  preloadScreenReader: preloadScreenReaderComponents,
  preloadForms: preloadFormAccessibilityComponents,
};

export default AccessibilityBundle;