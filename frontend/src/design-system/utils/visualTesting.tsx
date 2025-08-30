/**
 * Visual Testing Utilities
 * Helper functions for visual regression testing
 */

import { render, RenderResult } from '@testing-library/react';
import React from 'react';

// Mock expect function for TypeScript (should be provided by Jest in actual tests)
declare const expect: any;

// Visual testing configuration
export interface VisualTestConfig {
  threshold?: number;
  failureThreshold?: number;
  failureThresholdType?: 'pixel' | 'percent';
  customDiffConfig?: {
    threshold?: number;
    includeAA?: boolean;
  };
}

// Default visual test configuration
export const defaultVisualConfig: VisualTestConfig = {
  threshold: 0.2,
  failureThreshold: 0.05,
  failureThresholdType: 'percent',
  customDiffConfig: {
    threshold: 0.2,
    includeAA: false,
  },
};

// Theme configurations for testing
export const testThemes = {
  light: {
    name: 'light',
    colors: {
      primary: '#0066cc',
      secondary: '#6c757d',
      success: '#28a745',
      warning: '#ffc107',
      danger: '#dc3545',
      background: '#ffffff',
      surface: '#f8f9fa',
      text: '#212529',
    },
  },
  dark: {
    name: 'dark',
    colors: {
      primary: '#4dabf7',
      secondary: '#adb5bd',
      success: '#51cf66',
      warning: '#ffd43b',
      danger: '#ff6b6b',
      background: '#121212',
      surface: '#1e1e1e',
      text: '#ffffff',
    },
  },
  'high-contrast': {
    name: 'high-contrast',
    colors: {
      primary: '#0000ff',
      secondary: '#808080',
      success: '#008000',
      warning: '#ffff00',
      danger: '#ff0000',
      background: '#ffffff',
      surface: '#f0f0f0',
      text: '#000000',
    },
  },
  'polish-business': {
    name: 'polish-business',
    colors: {
      primary: '#dc143c',
      secondary: '#6c757d',
      success: '#28a745',
      warning: '#ffc107',
      danger: '#dc3545',
      background: '#ffffff',
      surface: '#f8f9fa',
      text: '#212529',
    },
  },
};

// Viewport configurations for responsive testing
export const testViewports = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1440, height: 900 },
  wide: { width: 1920, height: 1080 },
};

// Component state configurations
export const componentStates = {
  default: {},
  hover: { 'data-state': 'hover' },
  focus: { 'data-state': 'focus' },
  active: { 'data-state': 'active' },
  disabled: { disabled: true },
  loading: { loading: true },
  error: { error: 'Error message' },
  success: { success: 'Success message' },
};

// Helper function to create visual test wrapper
export const createVisualTestWrapper = (
  theme: keyof typeof testThemes = 'light',
  viewport?: keyof typeof testViewports
) => {
  return ({ children }: { children: React.ReactNode }): JSX.Element => {
    React.useEffect(() => {
      // Set theme
      document.documentElement.setAttribute('data-theme', theme);
      
      // Set viewport if specified
      if (viewport) {
        const { width, height } = testViewports[viewport];
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: width,
        });
        Object.defineProperty(window, 'innerHeight', {
          writable: true,
          configurable: true,
          value: height,
        });
        window.dispatchEvent(new Event('resize'));
      }
      
      // Disable animations for consistent screenshots
      const style = document.createElement('style');
      style.textContent = `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `;
      document.head.appendChild(style);
      
      return () => {
        document.head.removeChild(style);
      };
    }, []);

    return (
      <div
        style={{
          padding: '20px',
          backgroundColor: testThemes[theme].colors.background,
          color: testThemes[theme].colors.text,
          fontFamily: 'system-ui, -apple-system, sans-serif',
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale',
        }}
      >
        {children}
      </div>
    );
  };
};

// Helper function to render component for visual testing
export const renderForVisualTest = (
  component: React.ReactElement,
  options: {
    theme?: keyof typeof testThemes;
    viewport?: keyof typeof testViewports;
    wrapper?: React.ComponentType<{ children: React.ReactNode }>;
  } = {}
): RenderResult => {
  const { theme = 'light', viewport, wrapper } = options;
  
  const TestWrapper = wrapper || createVisualTestWrapper(theme, viewport);
  
  return render(component, { wrapper: TestWrapper });
};

// Helper function to test component across all themes
export const testComponentAcrossThemes = async (
  component: React.ReactElement,
  testName: string,
  customConfig?: VisualTestConfig
) => {
  const config = { ...defaultVisualConfig, ...customConfig };
  
  for (const theme of Object.keys(testThemes) as Array<keyof typeof testThemes>) {
    const { container } = renderForVisualTest(component, { theme });
    
    // Wait for any async rendering
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const screenshot = container.firstChild as HTMLElement;
    
    expect(screenshot).toMatchImageSnapshot({
      ...config,
      customSnapshotIdentifier: `${testName}-${theme}`,
    });
  }
};

// Helper function to test component across all viewports
export const testComponentAcrossViewports = async (
  component: React.ReactElement,
  testName: string,
  customConfig?: VisualTestConfig
) => {
  const config = { ...defaultVisualConfig, ...customConfig };
  
  for (const viewport of Object.keys(testViewports) as Array<keyof typeof testViewports>) {
    const { container } = renderForVisualTest(component, { viewport });
    
    // Wait for any async rendering
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const screenshot = container.firstChild as HTMLElement;
    
    expect(screenshot).toMatchImageSnapshot({
      ...config,
      customSnapshotIdentifier: `${testName}-${viewport}`,
    });
  }
};

// Helper function to test component in all states
export const testComponentStates = async (
  ComponentClass: React.ComponentType<any>,
  baseProps: any,
  testName: string,
  customConfig?: VisualTestConfig
) => {
  const config = { ...defaultVisualConfig, ...customConfig };
  
  for (const [stateName, stateProps] of Object.entries(componentStates)) {
    const component = React.createElement(ComponentClass, {
      ...baseProps,
      ...stateProps,
    });
    
    const { container } = renderForVisualTest(component);
    
    // Wait for any async rendering
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const screenshot = container.firstChild as HTMLElement;
    
    expect(screenshot).toMatchImageSnapshot({
      ...config,
      customSnapshotIdentifier: `${testName}-${stateName}`,
    });
  }
};

// Helper function for comprehensive component testing
export const comprehensiveVisualTest = async (
  ComponentClass: React.ComponentType<any>,
  baseProps: any,
  testName: string,
  options: {
    testThemes?: boolean;
    testViewports?: boolean;
    testStates?: boolean;
    customConfig?: VisualTestConfig;
  } = {}
) => {
  const {
    testThemes: shouldTestThemes = true,
    testViewports: shouldTestViewports = true,
    testStates: shouldTestStates = true,
    customConfig,
  } = options;
  
  const component = React.createElement(ComponentClass, baseProps);
  
  // Test across themes
  if (shouldTestThemes) {
    await testComponentAcrossThemes(component, testName, customConfig);
  }
  
  // Test across viewports
  if (shouldTestViewports) {
    await testComponentAcrossViewports(component, testName, customConfig);
  }
  
  // Test component states
  if (shouldTestStates) {
    await testComponentStates(ComponentClass, baseProps, testName, customConfig);
  }
};

// Helper function to create visual test matrix
export const createVisualTestMatrix = (
  components: Array<{
    name: string;
    component: React.ComponentType<any>;
    props: any;
    variants?: Array<{ name: string; props: any }>;
  }>,
  options: {
    themes?: Array<keyof typeof testThemes>;
    viewports?: Array<keyof typeof testViewports>;
    states?: Array<keyof typeof componentStates>;
  } = {}
) => {
  const {
    themes = Object.keys(testThemes) as Array<keyof typeof testThemes>,
    viewports = Object.keys(testViewports) as Array<keyof typeof testViewports>,
    states = Object.keys(componentStates) as Array<keyof typeof componentStates>,
  } = options;
  
  const testMatrix: Array<{
    name: string;
    component: React.ReactElement;
    theme: keyof typeof testThemes;
    viewport: keyof typeof testViewports;
    state: keyof typeof componentStates;
  }> = [];
  
  for (const { name, component: Component, props, variants = [] } of components) {
    const componentVariants = [{ name: 'default', props }, ...variants];
    
    for (const variant of componentVariants) {
      for (const theme of themes) {
        for (const viewport of viewports) {
          for (const state of states) {
            const stateProps = componentStates[state];
            const component = React.createElement(Component, {
              ...props,
              ...variant.props,
              ...stateProps,
            });
            
            testMatrix.push({
              name: `${name}-${variant.name}-${theme}-${viewport}-${state}`,
              component,
              theme,
              viewport,
              state,
            });
          }
        }
      }
    }
  }
  
  return testMatrix;
};

// Helper function to run visual test matrix
export const runVisualTestMatrix = async (
  testMatrix: ReturnType<typeof createVisualTestMatrix>,
  customConfig?: VisualTestConfig
) => {
  const config = { ...defaultVisualConfig, ...customConfig };
  
  for (const test of testMatrix) {
    const { container } = renderForVisualTest(test.component, {
      theme: test.theme,
      viewport: test.viewport,
    });
    
    // Wait for any async rendering
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const screenshot = container.firstChild as HTMLElement;
    
    expect(screenshot).toMatchImageSnapshot({
      ...config,
      customSnapshotIdentifier: test.name,
    });
  }
};

// Export visual testing utilities
export const visualTestUtils = {
  createVisualTestWrapper,
  renderForVisualTest,
  testComponentAcrossThemes,
  testComponentAcrossViewports,
  testComponentStates,
  comprehensiveVisualTest,
  createVisualTestMatrix,
  runVisualTestMatrix,
  testThemes,
  testViewports,
  componentStates,
  defaultVisualConfig,
};