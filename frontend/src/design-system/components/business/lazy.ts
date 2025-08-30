/**
 * Lazy-loaded Polish Business Components
 * 
 * This module provides lazy-loaded versions of Polish business components
 * to optimize bundle size and improve initial load performance.
 */

import { createLazyComponent } from '../../utils/lazyLoading';

// Lazy load business components
export const LazyCurrencyInput = createLazyComponent(
  () => import('./CurrencyInput/CurrencyInput').then(module => ({ default: module.CurrencyInput }))
);

export const LazyNIPValidator = createLazyComponent(
  () => import('./NIPValidator/NIPValidator').then(module => ({ default: module.NIPValidator }))
);

export const LazyVATRateSelector = createLazyComponent(
  () => import('./VATRateSelector/VATRateSelector').then(module => ({ default: module.VATRateSelector }))
);

export const LazyDatePicker = createLazyComponent(
  () => import('./DatePicker/DatePicker').then(module => ({ default: module.DatePicker }))
);

export const LazyInvoiceStatusBadge = createLazyComponent(
  () => import('./InvoiceStatusBadge/InvoiceStatusBadge').then(module => ({ default: module.InvoiceStatusBadge }))
);

export const LazyComplianceIndicator = createLazyComponent(
  () => import('./ComplianceIndicator/ComplianceIndicator').then(module => ({ default: module.ComplianceIndicator }))
);

export const LazyPolishBusinessThemeDemo = createLazyComponent(
  () => import('./PolishBusinessThemeDemo/PolishBusinessThemeDemo').then(module => ({ default: module.PolishBusinessThemeDemo }))
);

// Preload business components when Polish business features are detected
export function preloadPolishBusinessComponents(): Promise<any[]> {
  return Promise.all([
    LazyCurrencyInput.preload(),
    LazyNIPValidator.preload(),
    LazyVATRateSelector.preload(),
    LazyDatePicker.preload(),
    LazyInvoiceStatusBadge.preload(),
    LazyComplianceIndicator.preload(),
  ]);
}

// Business component bundle
export const PolishBusinessBundle = {
  CurrencyInput: LazyCurrencyInput,
  NIPValidator: LazyNIPValidator,
  VATRateSelector: LazyVATRateSelector,
  DatePicker: LazyDatePicker,
  InvoiceStatusBadge: LazyInvoiceStatusBadge,
  ComplianceIndicator: LazyComplianceIndicator,
  PolishBusinessThemeDemo: LazyPolishBusinessThemeDemo,
  preload: preloadPolishBusinessComponents,
};

export default PolishBusinessBundle;