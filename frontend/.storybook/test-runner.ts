/**
 * Storybook Test Runner Configuration
 * Configures visual regression testing for Storybook stories
 */

import type { TestRunnerConfig } from '@storybook/test-runner';
import { toMatchImageSnapshot } from 'jest-image-snapshot';

const config: TestRunnerConfig = {
  setup() {
    // Add custom matchers
    expect.extend({ toMatchImageSnapshot });
  },
  
  async preRender(page, context) {
    // Disable animations for consistent screenshots
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `,
    });
    
    // Set consistent font rendering
    await page.addStyleTag({
      content: `
        body {
          font-family: system-ui, -apple-system, sans-serif !important;
          -webkit-font-smoothing: antialiased !important;
          -moz-osx-font-smoothing: grayscale !important;
        }
      `,
    });
  },
  
  async postRender(page, context) {
    // Wait for any async rendering to complete
    await page.waitForTimeout(100);
    
    // Take screenshot for visual regression testing
    const image = await page.screenshot({
      clip: {
        x: 0,
        y: 0,
        width: 1200,
        height: 800,
      },
    });
    
    // Compare with baseline
    expect(image).toMatchImageSnapshot({
      customSnapshotIdentifier: `${context.id}`,
      failureThreshold: 0.05,
      failureThresholdType: 'percent',
      customDiffConfig: {
        threshold: 0.2,
      },
    });
  },
  
  // Test different viewports
  async postVisit(page, context) {
    const viewports = [
      { width: 375, height: 667, name: 'mobile' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 1440, height: 900, name: 'desktop' },
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(100);
      
      const image = await page.screenshot({
        clip: {
          x: 0,
          y: 0,
          width: viewport.width,
          height: Math.min(viewport.height, 800),
        },
      });
      
      expect(image).toMatchImageSnapshot({
        customSnapshotIdentifier: `${context.id}-${viewport.name}`,
        failureThreshold: 0.05,
        failureThresholdType: 'percent',
      });
    }
  },
  
  // Test different themes
  async postVisit(page, context) {
    const themes = ['light', 'dark', 'high-contrast', 'polish-business'];
    
    for (const theme of themes) {
      // Set theme
      await page.evaluate((themeName) => {
        document.documentElement.setAttribute('data-theme', themeName);
      }, theme);
      
      await page.waitForTimeout(100);
      
      const image = await page.screenshot({
        clip: {
          x: 0,
          y: 0,
          width: 1200,
          height: 800,
        },
      });
      
      expect(image).toMatchImageSnapshot({
        customSnapshotIdentifier: `${context.id}-${theme}`,
        failureThreshold: 0.05,
        failureThresholdType: 'percent',
      });
    }
  },
};

export default config;