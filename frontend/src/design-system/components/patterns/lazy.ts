/**
 * Lazy-loaded Pattern Components
 * 
 * This module provides lazy-loaded versions of complex pattern components
 * to optimize bundle size and improve initial load performance.
 */

import { createLazyComponent } from '../../utils/lazyLoading';

// Lazy load pattern components
export const LazyChart = createLazyComponent(
  () => import('./Chart/Chart').then(module => ({ default: module.Chart }))
);

export const LazyChartCard = createLazyComponent(
  () => import('./Chart/Chart').then(module => ({ default: module.ChartCard }))
);

export const LazyFileUpload = createLazyComponent(
  () => import('./FileUpload/FileUpload').then(module => ({ default: module.FileUpload }))
);

export const LazyTable = createLazyComponent(
  () => import('./Table/Table').then(module => ({ default: module.Table }))
);

export const LazyForm = createLazyComponent(
  () => import('./Form/Form').then(module => ({ default: module.Form }))
);

export const LazyCard = createLazyComponent(
  () => import('./Card/Card').then(module => ({ default: module.Card }))
);

export const LazyThemeControls = createLazyComponent(
  () => import('./ThemeControls/ThemeControls').then(module => ({ default: module.ThemeControls }))
);

export const LazyThemeDemo = createLazyComponent(
  () => import('./ThemeDemo/ThemeDemo').then(module => ({ default: module.ThemeDemo }))
);

// Preload chart components when data visualization is needed
export function preloadChartComponents(): Promise<any[]> {
  return Promise.all([
    LazyChart.preload(),
    LazyChartCard.preload(),
  ]);
}

// Preload form components when forms are needed
export function preloadFormComponents(): Promise<any[]> {
  return Promise.all([
    LazyForm.preload(),
    LazyFileUpload.preload(),
  ]);
}

// Preload table components when data tables are needed
export function preloadTableComponents(): Promise<any[]> {
  return Promise.all([
    LazyTable.preload(),
  ]);
}

// Preload theme components when theming is needed
export function preloadThemeComponents(): Promise<any[]> {
  return Promise.all([
    LazyThemeControls.preload(),
    LazyThemeDemo.preload(),
  ]);
}

// Pattern component bundles
export const ChartBundle = {
  Chart: LazyChart,
  ChartCard: LazyChartCard,
  preload: preloadChartComponents,
};

export const FormBundle = {
  Form: LazyForm,
  FileUpload: LazyFileUpload,
  preload: preloadFormComponents,
};

export const TableBundle = {
  Table: LazyTable,
  preload: preloadTableComponents,
};

export const ThemeBundle = {
  ThemeControls: LazyThemeControls,
  ThemeDemo: LazyThemeDemo,
  preload: preloadThemeComponents,
};

export const PatternBundle = {
  Chart: LazyChart,
  ChartCard: LazyChartCard,
  FileUpload: LazyFileUpload,
  Table: LazyTable,
  Form: LazyForm,
  Card: LazyCard,
  ThemeControls: LazyThemeControls,
  ThemeDemo: LazyThemeDemo,
  
  // Bundle preloaders
  preloadCharts: preloadChartComponents,
  preloadForms: preloadFormComponents,
  preloadTables: preloadTableComponents,
  preloadThemes: preloadThemeComponents,
};

export default PatternBundle;