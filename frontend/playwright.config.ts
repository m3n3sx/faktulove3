/**
 * Playwright Configuration for Visual Regression Testing
 * Configures cross-browser visual testing and responsive layout testing
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './src/design-system/__tests__/playwright',
  
  // Run tests in files that have 'visual' in the filename
  testMatch: /.*visual.*\.spec\.ts/,
  
  // Folder for test artifacts such as screenshots, videos, traces, etc.
  outputDir: 'test-results/',
  
  // Folder for test artifacts such as screenshots
  use: {
    // Base URL for tests
    baseURL: 'http://localhost:3000',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Take screenshot on failure
    screenshot: 'only-on-failure',
    
    // Record video on failure
    video: 'retain-on-failure',
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Enable visual comparisons
        screenshot: 'only-on-failure',
      },
    },
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        screenshot: 'only-on-failure',
      },
    },
    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        screenshot: 'only-on-failure',
      },
    },
    
    // Mobile browsers
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        screenshot: 'only-on-failure',
      },
    },
    {
      name: 'Mobile Safari',
      use: { 
        ...devices['iPhone 12'],
        screenshot: 'only-on-failure',
      },
    },
    
    // Tablet browsers
    {
      name: 'Tablet Chrome',
      use: { 
        ...devices['iPad Pro'],
        screenshot: 'only-on-failure',
      },
    },
  ],

  // Run your local dev server before starting the tests
  webServer: {
    command: 'npm start',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },

  // Global test timeout
  timeout: 30000,
  
  // Expect timeout for assertions
  expect: {
    // Timeout for expect() calls
    timeout: 10000,
    
    // Threshold for visual comparisons
    toHaveScreenshot: {
      threshold: 0.2,
      mode: 'percent',
    },
    
    toMatchSnapshot: {
      threshold: 0.2,
      mode: 'percent',
    },
  },

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }],
  ],

  // Global setup and teardown
  globalSetup: require.resolve('./src/design-system/__tests__/playwright/global-setup.ts'),
  globalTeardown: require.resolve('./src/design-system/__tests__/playwright/global-teardown.ts'),

  // Retry configuration
  retries: process.env.CI ? 2 : 0,
  
  // Parallel workers
  workers: process.env.CI ? 1 : undefined,
});