/**
 * Playwright Global Teardown
 * Cleans up after visual regression tests
 */

import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('Cleaning up Playwright visual regression testing environment...');
  
  try {
    // Clean up test artifacts if needed
    const testResultsDir = path.join(process.cwd(), 'test-results');
    
    if (fs.existsSync(testResultsDir)) {
      // Generate test summary
      const summaryPath = path.join(testResultsDir, 'visual-regression-summary.json');
      
      const summary = {
        timestamp: new Date().toISOString(),
        testRun: 'visual-regression',
        environment: {
          node: process.version,
          platform: process.platform,
          arch: process.arch,
        },
        config: {
          browsers: config.projects?.map(p => p.name) || [],
          baseURL: config.use?.baseURL,
        },
      };
      
      fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
      console.log(`📊 Test summary written to ${summaryPath}`);
    }
    
    // Clean up temporary files
    const tempDir = path.join(process.cwd(), '.temp-visual-tests');
    if (fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
      console.log('🧹 Cleaned up temporary files');
    }
    
    console.log('✅ Playwright teardown completed successfully');
    
  } catch (error) {
    console.error('❌ Playwright teardown failed:', error);
    // Don't throw error in teardown to avoid masking test failures
  }
}

export default globalTeardown;