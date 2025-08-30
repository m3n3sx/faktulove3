/**
 * Playwright Global Setup
 * Sets up the testing environment for visual regression tests
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('Setting up Playwright visual regression testing environment...');
  
  // Launch browser for setup
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    
    // Wait for the application to be ready
    await page.waitForSelector('[data-testid="app-ready"]', { timeout: 30000 });
    
    // Set up design system for testing
    await page.evaluate(() => {
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
      
      // Set consistent font rendering
      document.body.style.fontFamily = 'system-ui, -apple-system, sans-serif';
      document.body.style.webkitFontSmoothing = 'antialiased';
      document.body.style.mozOsxFontSmoothing = 'grayscale';
      
      // Ensure consistent viewport
      document.body.style.margin = '0';
      document.body.style.padding = '0';
    });
    
    // Pre-load design system assets
    await page.evaluate(() => {
      // Preload CSS
      const cssLinks = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
      return Promise.all(
        cssLinks.map(link => {
          return new Promise((resolve) => {
            if (link.sheet) {
              resolve(true);
            } else {
              link.addEventListener('load', () => resolve(true));
              link.addEventListener('error', () => resolve(false));
            }
          });
        })
      );
    });
    
    // Initialize design system themes
    await page.evaluate(() => {
      const themes = ['light', 'dark', 'high-contrast', 'polish-business'];
      
      themes.forEach(theme => {
        localStorage.setItem(`design-system-theme-${theme}-loaded`, 'true');
      });
    });
    
    console.log('✅ Playwright setup completed successfully');
    
  } catch (error) {
    console.error('❌ Playwright setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;