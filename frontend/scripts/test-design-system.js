#!/usr/bin/env node

/**
 * Design System Test Runner
 * Comprehensive test runner for all design system tests including unit, integration,
 * performance, visual regression, and accessibility tests
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Test configuration
const testConfig = {
  unit: {
    command: 'npm test -- --testPathPattern="__tests__.*\\.test\\.(ts|tsx)$" --watchAll=false',
    description: 'Unit tests for component integration',
    timeout: 300000, // 5 minutes
  },
  integration: {
    command: 'npm test -- --testPathPattern="integration.*\\.test\\.(ts|tsx)$" --watchAll=false',
    description: 'Integration tests for component compatibility',
    timeout: 600000, // 10 minutes
  },
  performance: {
    command: 'npm test -- --testPathPattern="performance.*\\.test\\.(ts|tsx)$" --watchAll=false',
    description: 'Performance benchmarking tests',
    timeout: 900000, // 15 minutes
  },
  accessibility: {
    command: 'npm test -- --testPathPattern="accessibility.*\\.test\\.(ts|tsx)$" --watchAll=false',
    description: 'Accessibility compliance tests',
    timeout: 600000, // 10 minutes
  },
  visual: {
    command: 'npm run test:visual',
    description: 'Visual regression tests',
    timeout: 1200000, // 20 minutes
  },
  comprehensive: {
    command: 'npm test -- --testPathPattern="comprehensive.*\\.test\\.(ts|tsx)$" --watchAll=false',
    description: 'Comprehensive component tests',
    timeout: 900000, // 15 minutes
  },
  'prop-mapping': {
    command: 'npm test -- --testPathPattern="prop-mapping.*\\.test\\.(ts|tsx)$" --watchAll=false',
    description: 'Prop mapping and compatibility tests',
    timeout: 300000, // 5 minutes
  },
  'polish-business': {
    command: 'npm test -- --testPathPattern="polish-business.*\\.test\\.(ts|tsx)$" --watchAll=false',
    description: 'Polish business logic tests',
    timeout: 300000, // 5 minutes
  },
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

// Utility functions
const log = (message, color = colors.reset) => {
  console.log(`${color}${message}${colors.reset}`);
};

const logSuccess = (message) => log(`✅ ${message}`, colors.green);
const logError = (message) => log(`❌ ${message}`, colors.red);
const logWarning = (message) => log(`⚠️  ${message}`, colors.yellow);
const logInfo = (message) => log(`ℹ️  ${message}`, colors.blue);
const logHeader = (message) => log(`\n${colors.bright}${message}${colors.reset}`, colors.cyan);

// Test result tracking
const testResults = {
  passed: [],
  failed: [],
  skipped: [],
  startTime: Date.now(),
};

// Run a single test suite
const runTestSuite = async (suiteName, config) => {
  logHeader(`Running ${suiteName} tests`);
  logInfo(config.description);
  
  return new Promise((resolve) => {
    const startTime = Date.now();
    
    try {
      const child = spawn('npm', ['test', '--', ...config.command.split(' ').slice(2)], {
        stdio: 'pipe',
        shell: true,
        timeout: config.timeout,
      });
      
      let output = '';
      let errorOutput = '';
      
      child.stdout.on('data', (data) => {
        output += data.toString();
        process.stdout.write(data);
      });
      
      child.stderr.on('data', (data) => {
        errorOutput += data.toString();
        process.stderr.write(data);
      });
      
      child.on('close', (code) => {
        const duration = Date.now() - startTime;
        const result = {
          suite: suiteName,
          passed: code === 0,
          duration,
          output,
          errorOutput,
        };
        
        if (code === 0) {
          logSuccess(`${suiteName} tests passed (${duration}ms)`);
          testResults.passed.push(result);
        } else {
          logError(`${suiteName} tests failed (${duration}ms)`);
          testResults.failed.push(result);
        }
        
        resolve(result);
      });
      
      child.on('error', (error) => {
        logError(`Failed to run ${suiteName} tests: ${error.message}`);
        testResults.failed.push({
          suite: suiteName,
          passed: false,
          duration: Date.now() - startTime,
          error: error.message,
        });
        resolve({ passed: false, error });
      });
      
    } catch (error) {
      logError(`Error running ${suiteName} tests: ${error.message}`);
      testResults.failed.push({
        suite: suiteName,
        passed: false,
        duration: Date.now() - startTime,
        error: error.message,
      });
      resolve({ passed: false, error });
    }
  });
};

// Generate test report
const generateReport = () => {
  const totalDuration = Date.now() - testResults.startTime;
  const totalTests = testResults.passed.length + testResults.failed.length + testResults.skipped.length;
  
  logHeader('Test Results Summary');
  
  log(`Total test suites: ${totalTests}`);
  logSuccess(`Passed: ${testResults.passed.length}`);
  logError(`Failed: ${testResults.failed.length}`);
  logWarning(`Skipped: ${testResults.skipped.length}`);
  log(`Total duration: ${totalDuration}ms`);
  
  if (testResults.failed.length > 0) {
    logHeader('Failed Test Suites');
    testResults.failed.forEach(result => {
      logError(`${result.suite}: ${result.error || 'Test failures detected'}`);
    });
  }
  
  // Generate detailed report file
  const reportPath = path.join(process.cwd(), 'test-results', 'design-system-test-report.json');
  const reportDir = path.dirname(reportPath);
  
  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
  }
  
  const detailedReport = {
    timestamp: new Date().toISOString(),
    summary: {
      total: totalTests,
      passed: testResults.passed.length,
      failed: testResults.failed.length,
      skipped: testResults.skipped.length,
      duration: totalDuration,
    },
    results: [...testResults.passed, ...testResults.failed, ...testResults.skipped],
    environment: {
      node: process.version,
      npm: execSync('npm --version', { encoding: 'utf8' }).trim(),
      platform: process.platform,
      arch: process.arch,
    },
  };
  
  fs.writeFileSync(reportPath, JSON.stringify(detailedReport, null, 2));
  logInfo(`Detailed report saved to: ${reportPath}`);
  
  return testResults.failed.length === 0;
};

// Setup test environment
const setupTestEnvironment = () => {
  logHeader('Setting up test environment');
  
  try {
    // Ensure test results directory exists
    const testResultsDir = path.join(process.cwd(), 'test-results');
    if (!fs.existsSync(testResultsDir)) {
      fs.mkdirSync(testResultsDir, { recursive: true });
    }
    
    // Check if design system is built
    const designSystemBuild = path.join(process.cwd(), 'src', 'design-system', 'index.ts');
    if (!fs.existsSync(designSystemBuild)) {
      logWarning('Design system not found, building...');
      execSync('npm run build:design-system', { stdio: 'inherit' });
    }
    
    logSuccess('Test environment setup complete');
    return true;
  } catch (error) {
    logError(`Failed to setup test environment: ${error.message}`);
    return false;
  }
};

// Cleanup test environment
const cleanupTestEnvironment = () => {
  logHeader('Cleaning up test environment');
  
  try {
    // Clean up temporary files
    const tempDirs = [
      path.join(process.cwd(), '.temp-test-files'),
      path.join(process.cwd(), 'coverage', 'tmp'),
    ];
    
    tempDirs.forEach(dir => {
      if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true });
      }
    });
    
    logSuccess('Test environment cleanup complete');
  } catch (error) {
    logWarning(`Cleanup warning: ${error.message}`);
  }
};

// Main test runner
const runTests = async (suites = []) => {
  logHeader('Design System Test Runner');
  logInfo('Running comprehensive design system tests');
  
  // Setup environment
  if (!setupTestEnvironment()) {
    process.exit(1);
  }
  
  // Determine which test suites to run
  const suitesToRun = suites.length > 0 ? suites : Object.keys(testConfig);
  
  logInfo(`Running test suites: ${suitesToRun.join(', ')}`);
  
  // Run test suites sequentially to avoid resource conflicts
  for (const suiteName of suitesToRun) {
    if (!testConfig[suiteName]) {
      logWarning(`Unknown test suite: ${suiteName}`);
      testResults.skipped.push({ suite: suiteName, reason: 'Unknown suite' });
      continue;
    }
    
    await runTestSuite(suiteName, testConfig[suiteName]);
  }
  
  // Generate report
  const allPassed = generateReport();
  
  // Cleanup
  cleanupTestEnvironment();
  
  // Exit with appropriate code
  process.exit(allPassed ? 0 : 1);
};

// CLI interface
const main = () => {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Design System Test Runner

Usage: node test-design-system.js [options] [test-suites...]

Options:
  --help, -h          Show this help message
  --list, -l          List available test suites
  --parallel, -p      Run tests in parallel (experimental)
  --coverage, -c      Generate coverage report
  --watch, -w         Watch mode (not recommended for CI)

Test Suites:
${Object.entries(testConfig).map(([name, config]) => 
  `  ${name.padEnd(15)} ${config.description}`
).join('\n')}

Examples:
  node test-design-system.js                    # Run all tests
  node test-design-system.js unit integration   # Run specific suites
  node test-design-system.js --coverage         # Run with coverage
    `);
    return;
  }
  
  if (args.includes('--list') || args.includes('-l')) {
    console.log('Available test suites:');
    Object.entries(testConfig).forEach(([name, config]) => {
      console.log(`  ${colors.cyan}${name}${colors.reset}: ${config.description}`);
    });
    return;
  }
  
  // Extract test suite names from arguments
  const suites = args.filter(arg => !arg.startsWith('--') && !arg.startsWith('-'));
  
  // Handle coverage option
  if (args.includes('--coverage') || args.includes('-c')) {
    process.env.GENERATE_COVERAGE = 'true';
  }
  
  // Handle watch mode
  if (args.includes('--watch') || args.includes('-w')) {
    logWarning('Watch mode is not recommended for comprehensive testing');
    process.env.WATCH_MODE = 'true';
  }
  
  // Run tests
  runTests(suites).catch(error => {
    logError(`Test runner failed: ${error.message}`);
    process.exit(1);
  });
};

// Handle process signals
process.on('SIGINT', () => {
  logWarning('Test runner interrupted');
  cleanupTestEnvironment();
  process.exit(130);
});

process.on('SIGTERM', () => {
  logWarning('Test runner terminated');
  cleanupTestEnvironment();
  process.exit(143);
});

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  runTests,
  testConfig,
  generateReport,
};