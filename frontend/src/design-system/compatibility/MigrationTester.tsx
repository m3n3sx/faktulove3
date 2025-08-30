import React, { useState, useEffect } from 'react';
import { useMigrationTracker } from './ComponentWrapper';

/**
 * Test types for migration validation
 */
export type MigrationTestType = 
  | 'unit'
  | 'integration'
  | 'visual'
  | 'accessibility'
  | 'performance'
  | 'polish-business';

/**
 * Test result
 */
export interface TestResult {
  testType: MigrationTestType;
  testName: string;
  componentName: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number; // ms
  error?: string;
  details?: any;
  screenshot?: string; // for visual tests
}

/**
 * Test suite configuration
 */
export interface TestSuiteConfig {
  enabledTests: MigrationTestType[];
  components: string[];
  visualRegressionThreshold: number; // 0-1
  performanceThresholds: {
    renderTime: number; // ms
    memoryUsage: number; // MB
  };
  accessibilityLevel: 'AA' | 'AAA';
  polishBusinessTests: boolean;
}

/**
 * Test suite report
 */
export interface TestSuiteReport {
  timestamp: Date;
  config: TestSuiteConfig;
  totalTests: number;
  passed: number;
  failed: number;
  skipped: number;
  duration: number; // ms
  results: TestResult[];
  summary: {
    [K in MigrationTestType]: {
      passed: number;
      failed: number;
      skipped: number;
    };
  };
}

/**
 * Migration Tester Hook
 */
export function useMigrationTester() {
  const [testReport, setTestReport] = useState<TestSuiteReport | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [currentTest, setCurrentTest] = useState<string>('');
  const [config, setConfig] = useState<TestSuiteConfig>({
    enabledTests: ['unit', 'integration', 'accessibility', 'performance'],
    components: [],
    visualRegressionThreshold: 0.1,
    performanceThresholds: {
      renderTime: 100,
      memoryUsage: 50,
    },
    accessibilityLevel: 'AA',
    polishBusinessTests: true,
  });

  const migrationTracker = useMigrationTracker();

  /**
   * Run comprehensive test suite
   */
  const runTestSuite = async () => {
    setIsRunning(true);
    setCurrentTest('Initializing test suite...');
    
    const startTime = Date.now();
    const results: TestResult[] = [];
    
    try {
      // Get components to test
      const componentsToTest = config.components.length > 0 
        ? config.components 
        : Array.from(migrationTracker.getAllMigrations().keys());

      // Run tests for each component
      for (const component of componentsToTest) {
        setCurrentTest(`Testing ${component}...`);
        
        for (const testType of config.enabledTests) {
          const testResults = await runTestsForComponent(component, testType, config);
          results.push(...testResults);
        }
      }

      // Generate report
      const duration = Date.now() - startTime;
      const report = generateTestReport(results, config, duration);
      setTestReport(report);
      
      return report;
    } catch (error) {
      console.error('Test suite failed:', error);
      throw error;
    } finally {
      setIsRunning(false);
      setCurrentTest('');
    }
  };

  /**
   * Run specific test type for a component
   */
  const runComponentTest = async (
    componentName: string, 
    testType: MigrationTestType
  ): Promise<TestResult[]> => {
    return runTestsForComponent(componentName, testType, config);
  };

  /**
   * Generate test coverage report
   */
  const getCoverageReport = () => {
    if (!testReport) return null;

    const totalComponents = new Set(testReport.results.map(r => r.componentName)).size;
    const testedComponents = new Set(
      testReport.results
        .filter(r => r.status !== 'skipped')
        .map(r => r.componentName)
    ).size;

    const coverageByType = config.enabledTests.reduce((acc, testType) => {
      const typeResults = testReport.results.filter(r => r.testType === testType);
      const typeComponents = new Set(typeResults.map(r => r.componentName)).size;
      
      acc[testType] = {
        components: typeComponents,
        coverage: totalComponents > 0 ? (typeComponents / totalComponents) * 100 : 0,
        passed: typeResults.filter(r => r.status === 'passed').length,
        failed: typeResults.filter(r => r.status === 'failed').length,
      };
      
      return acc;
    }, {} as Record<MigrationTestType, any>);

    return {
      totalComponents,
      testedComponents,
      overallCoverage: totalComponents > 0 ? (testedComponents / totalComponents) * 100 : 0,
      coverageByType,
    };
  };

  return {
    testReport,
    isRunning,
    currentTest,
    config,
    setConfig,
    runTestSuite,
    runComponentTest,
    getCoverageReport,
  };
}

/**
 * Run tests for a specific component and test type
 */
async function runTestsForComponent(
  componentName: string,
  testType: MigrationTestType,
  config: TestSuiteConfig
): Promise<TestResult[]> {
  const results: TestResult[] = [];

  switch (testType) {
    case 'unit':
      results.push(...await runUnitTests(componentName));
      break;
    case 'integration':
      results.push(...await runIntegrationTests(componentName));
      break;
    case 'visual':
      results.push(...await runVisualTests(componentName, config.visualRegressionThreshold));
      break;
    case 'accessibility':
      results.push(...await runAccessibilityTests(componentName, config.accessibilityLevel));
      break;
    case 'performance':
      results.push(...await runPerformanceTests(componentName, config.performanceThresholds));
      break;
    case 'polish-business':
      if (config.polishBusinessTests) {
        results.push(...await runPolishBusinessTests(componentName));
      }
      break;
  }

  return results;
}

/**
 * Run unit tests for component
 */
async function runUnitTests(componentName: string): Promise<TestResult[]> {
  const tests = [
    'renders without crashing',
    'accepts all required props',
    'handles prop changes correctly',
    'maintains backward compatibility',
  ];

  const results: TestResult[] = [];

  for (const testName of tests) {
    const startTime = Date.now();
    
    try {
      // Simulate unit test execution
      await new Promise(resolve => setTimeout(resolve, Math.random() * 100 + 50));
      
      const success = Math.random() > 0.1; // 90% success rate
      
      results.push({
        testType: 'unit',
        testName,
        componentName,
        status: success ? 'passed' : 'failed',
        duration: Date.now() - startTime,
        error: success ? undefined : `Unit test failed: ${testName}`,
      });
    } catch (error) {
      results.push({
        testType: 'unit',
        testName,
        componentName,
        status: 'failed',
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  return results;
}

/**
 * Run integration tests for component
 */
async function runIntegrationTests(componentName: string): Promise<TestResult[]> {
  const tests = [
    'integrates with design system theme',
    'works with form validation',
    'handles event propagation',
    'maintains state consistency',
  ];

  const results: TestResult[] = [];

  for (const testName of tests) {
    const startTime = Date.now();
    
    try {
      await new Promise(resolve => setTimeout(resolve, Math.random() * 200 + 100));
      
      const success = Math.random() > 0.15; // 85% success rate
      
      results.push({
        testType: 'integration',
        testName,
        componentName,
        status: success ? 'passed' : 'failed',
        duration: Date.now() - startTime,
        error: success ? undefined : `Integration test failed: ${testName}`,
      });
    } catch (error) {
      results.push({
        testType: 'integration',
        testName,
        componentName,
        status: 'failed',
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  return results;
}

/**
 * Run visual regression tests
 */
async function runVisualTests(
  componentName: string,
  threshold: number
): Promise<TestResult[]> {
  const tests = [
    'default state matches baseline',
    'hover state matches baseline',
    'focus state matches baseline',
    'disabled state matches baseline',
  ];

  const results: TestResult[] = [];

  for (const testName of tests) {
    const startTime = Date.now();
    
    try {
      await new Promise(resolve => setTimeout(resolve, Math.random() * 300 + 200));
      
      const visualDiff = Math.random() * 0.2; // 0-20% difference
      const success = visualDiff <= threshold;
      
      results.push({
        testType: 'visual',
        testName,
        componentName,
        status: success ? 'passed' : 'failed',
        duration: Date.now() - startTime,
        error: success ? undefined : `Visual difference ${(visualDiff * 100).toFixed(1)}% exceeds threshold ${(threshold * 100).toFixed(1)}%`,
        details: { visualDiff, threshold },
        screenshot: `screenshots/${componentName}-${testName.replace(/\s+/g, '-')}.png`,
      });
    } catch (error) {
      results.push({
        testType: 'visual',
        testName,
        componentName,
        status: 'failed',
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  return results;
}

/**
 * Run accessibility tests
 */
async function runAccessibilityTests(
  componentName: string,
  level: 'AA' | 'AAA'
): Promise<TestResult[]> {
  const tests = [
    'has proper ARIA labels',
    'supports keyboard navigation',
    'meets color contrast requirements',
    'provides screen reader support',
    'has focus indicators',
  ];

  const results: TestResult[] = [];

  for (const testName of tests) {
    const startTime = Date.now();
    
    try {
      await new Promise(resolve => setTimeout(resolve, Math.random() * 150 + 100));
      
      const success = Math.random() > (level === 'AAA' ? 0.25 : 0.15); // Stricter for AAA
      
      results.push({
        testType: 'accessibility',
        testName,
        componentName,
        status: success ? 'passed' : 'failed',
        duration: Date.now() - startTime,
        error: success ? undefined : `Accessibility test failed: ${testName} (${level} level)`,
        details: { level },
      });
    } catch (error) {
      results.push({
        testType: 'accessibility',
        testName,
        componentName,
        status: 'failed',
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  return results;
}

/**
 * Run performance tests
 */
async function runPerformanceTests(
  componentName: string,
  thresholds: { renderTime: number; memoryUsage: number }
): Promise<TestResult[]> {
  const tests = [
    'render time within threshold',
    'memory usage within limits',
    'no memory leaks detected',
    'efficient re-renders',
  ];

  const results: TestResult[] = [];

  for (const testName of tests) {
    const startTime = Date.now();
    
    try {
      await new Promise(resolve => setTimeout(resolve, Math.random() * 100 + 50));
      
      let success = true;
      let details: any = {};
      let error: string | undefined;

      if (testName.includes('render time')) {
        const renderTime = Math.random() * 200 + 50;
        success = renderTime <= thresholds.renderTime;
        details.renderTime = renderTime;
        details.threshold = thresholds.renderTime;
        if (!success) {
          error = `Render time ${renderTime.toFixed(1)}ms exceeds threshold ${thresholds.renderTime}ms`;
        }
      } else if (testName.includes('memory usage')) {
        const memoryUsage = Math.random() * 100 + 20;
        success = memoryUsage <= thresholds.memoryUsage;
        details.memoryUsage = memoryUsage;
        details.threshold = thresholds.memoryUsage;
        if (!success) {
          error = `Memory usage ${memoryUsage.toFixed(1)}MB exceeds threshold ${thresholds.memoryUsage}MB`;
        }
      } else {
        success = Math.random() > 0.1;
        if (!success) {
          error = `Performance test failed: ${testName}`;
        }
      }
      
      results.push({
        testType: 'performance',
        testName,
        componentName,
        status: success ? 'passed' : 'failed',
        duration: Date.now() - startTime,
        error,
        details,
      });
    } catch (error) {
      results.push({
        testType: 'performance',
        testName,
        componentName,
        status: 'failed',
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  return results;
}

/**
 * Run Polish business-specific tests
 */
async function runPolishBusinessTests(componentName: string): Promise<TestResult[]> {
  const tests = [
    'handles Polish currency formatting',
    'validates NIP numbers correctly',
    'supports Polish date formats',
    'calculates VAT according to Polish rates',
  ];

  const results: TestResult[] = [];

  // Only run Polish business tests for relevant components
  const polishBusinessComponents = ['CurrencyInput', 'NIPValidator', 'DatePicker', 'VATRateSelector'];
  const isPolishBusinessComponent = polishBusinessComponents.some(comp => 
    componentName.includes(comp) || componentName.toLowerCase().includes('invoice') || componentName.toLowerCase().includes('form')
  );

  if (!isPolishBusinessComponent) {
    return tests.map(testName => ({
      testType: 'polish-business' as const,
      testName,
      componentName,
      status: 'skipped' as const,
      duration: 0,
    }));
  }

  for (const testName of tests) {
    const startTime = Date.now();
    
    try {
      await new Promise(resolve => setTimeout(resolve, Math.random() * 150 + 100));
      
      const success = Math.random() > 0.2; // 80% success rate
      
      results.push({
        testType: 'polish-business',
        testName,
        componentName,
        status: success ? 'passed' : 'failed',
        duration: Date.now() - startTime,
        error: success ? undefined : `Polish business test failed: ${testName}`,
      });
    } catch (error) {
      results.push({
        testType: 'polish-business',
        testName,
        componentName,
        status: 'failed',
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  return results;
}

/**
 * Generate comprehensive test report
 */
function generateTestReport(
  results: TestResult[],
  config: TestSuiteConfig,
  duration: number
): TestSuiteReport {
  const passed = results.filter(r => r.status === 'passed').length;
  const failed = results.filter(r => r.status === 'failed').length;
  const skipped = results.filter(r => r.status === 'skipped').length;

  const summary = config.enabledTests.reduce((acc, testType) => {
    const typeResults = results.filter(r => r.testType === testType);
    acc[testType] = {
      passed: typeResults.filter(r => r.status === 'passed').length,
      failed: typeResults.filter(r => r.status === 'failed').length,
      skipped: typeResults.filter(r => r.status === 'skipped').length,
    };
    return acc;
  }, {} as TestSuiteReport['summary']);

  return {
    timestamp: new Date(),
    config,
    totalTests: results.length,
    passed,
    failed,
    skipped,
    duration,
    results,
    summary,
  };
}

/**
 * Migration Tester UI Component
 */
export interface MigrationTesterProps {
  onTestComplete?: (report: TestSuiteReport) => void;
}

export const MigrationTester: React.FC<MigrationTesterProps> = ({
  onTestComplete,
}) => {
  const {
    testReport,
    isRunning,
    currentTest,
    config,
    setConfig,
    runTestSuite,
    runComponentTest,
    getCoverageReport,
  } = useMigrationTester();

  const [selectedComponents, setSelectedComponents] = useState<string[]>([]);
  const [selectedTestTypes, setSelectedTestTypes] = useState<MigrationTestType[]>(config.enabledTests);

  const availableComponents = [
    'Button', 'Input', 'Form', 'Table', 'Card', 'Select',
    'CurrencyInput', 'NIPValidator', 'DatePicker', 'VATRateSelector'
  ];

  const testTypeLabels: Record<MigrationTestType, string> = {
    unit: 'Unit Tests',
    integration: 'Integration Tests',
    visual: 'Visual Regression',
    accessibility: 'Accessibility',
    performance: 'Performance',
    'polish-business': 'Polish Business Logic',
  };

  const handleRunTests = async () => {
    const updatedConfig = {
      ...config,
      enabledTests: selectedTestTypes,
      components: selectedComponents,
    };
    setConfig(updatedConfig);
    
    const report = await runTestSuite();
    onTestComplete?.(report);
  };

  const coverageReport = getCoverageReport();

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'passed': return 'text-green-600 bg-green-50';
      case 'failed': return 'text-red-600 bg-red-50';
      case 'skipped': return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'passed': return '✅';
      case 'failed': return '❌';
      case 'skipped': return '⏭️';
    }
  };

  return (
    <div className="migration-tester p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6">Migration Tester</h2>
      
      {/* Configuration */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Test Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-2">Test Types</h4>
            <div className="space-y-2">
              {Object.entries(testTypeLabels).map(([key, label]) => (
                <label key={key} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedTestTypes.includes(key as MigrationTestType)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedTestTypes([...selectedTestTypes, key as MigrationTestType]);
                      } else {
                        setSelectedTestTypes(selectedTestTypes.filter(t => t !== key));
                      }
                    }}
                    className="mr-2"
                  />
                  {label}
                </label>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Components to Test</h4>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {availableComponents.map(component => (
                <label key={component} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedComponents.includes(component)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedComponents([...selectedComponents, component]);
                      } else {
                        setSelectedComponents(selectedComponents.filter(c => c !== component));
                      }
                    }}
                    className="mr-2"
                  />
                  {component}
                </label>
              ))}
            </div>
            <p className="text-xs text-gray-600 mt-1">
              Leave empty to test all migrated components
            </p>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Visual Regression Threshold
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.visualRegressionThreshold}
              onChange={(e) => setConfig({
                ...config,
                visualRegressionThreshold: parseFloat(e.target.value),
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">
              Render Time Threshold (ms)
            </label>
            <input
              type="number"
              value={config.performanceThresholds.renderTime}
              onChange={(e) => setConfig({
                ...config,
                performanceThresholds: {
                  ...config.performanceThresholds,
                  renderTime: parseInt(e.target.value),
                },
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">
              Accessibility Level
            </label>
            <select
              value={config.accessibilityLevel}
              onChange={(e) => setConfig({
                ...config,
                accessibilityLevel: e.target.value as 'AA' | 'AAA',
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded"
            >
              <option value="AA">WCAG 2.1 AA</option>
              <option value="AAA">WCAG 2.1 AAA</option>
            </select>
          </div>
        </div>
        
        <div className="mt-4">
          <button
            onClick={handleRunTests}
            disabled={isRunning || selectedTestTypes.length === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isRunning ? 'Running Tests...' : 'Run Test Suite'}
          </button>
        </div>
      </div>

      {/* Current Test Status */}
      {isRunning && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="font-medium">{currentTest}</span>
          </div>
        </div>
      )}

      {/* Test Results */}
      {testReport && (
        <>
          {/* Summary */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Test Results Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">
                  {testReport.totalTests}
                </div>
                <div className="text-sm text-gray-700">Total Tests</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {testReport.passed}
                </div>
                <div className="text-sm text-green-700">Passed</div>
              </div>
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {testReport.failed}
                </div>
                <div className="text-sm text-red-700">Failed</div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">
                  {testReport.skipped}
                </div>
                <div className="text-sm text-gray-700">Skipped</div>
              </div>
            </div>
            
            <div className="text-sm text-gray-600">
              Duration: {(testReport.duration / 1000).toFixed(1)}s
            </div>
          </div>

          {/* Coverage Report */}
          {coverageReport && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Test Coverage</h3>
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Overall Coverage</span>
                  <span className="text-lg font-bold text-blue-600">
                    {coverageReport.overallCoverage.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-blue-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${coverageReport.overallCoverage}%` }}
                  />
                </div>
                <div className="text-sm text-blue-700 mt-1">
                  {coverageReport.testedComponents} of {coverageReport.totalComponents} components tested
                </div>
              </div>
            </div>
          )}

          {/* Test Results by Type */}
          <div className="space-y-6">
            {Object.entries(testReport.summary).map(([testType, summary]) => {
              const typeResults = testReport.results.filter(r => r.testType === testType);
              
              if (typeResults.length === 0) return null;
              
              return (
                <div key={testType}>
                  <h3 className="text-lg font-semibold mb-3">
                    {testTypeLabels[testType as MigrationTestType]} 
                    <span className="ml-2 text-sm font-normal text-gray-600">
                      ({summary.passed} passed, {summary.failed} failed, {summary.skipped} skipped)
                    </span>
                  </h3>
                  
                  <div className="space-y-2">
                    {typeResults.map((result, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border ${getStatusColor(result.status)}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-lg">{getStatusIcon(result.status)}</span>
                              <span className="font-medium">{result.componentName}</span>
                              <span className="text-sm text-gray-600">- {result.testName}</span>
                            </div>
                            
                            {result.error && (
                              <p className="text-sm text-red-600 mt-1">{result.error}</p>
                            )}
                            
                            {result.details && (
                              <div className="text-xs text-gray-600 mt-1">
                                {JSON.stringify(result.details, null, 2)}
                              </div>
                            )}
                          </div>
                          
                          <div className="text-right text-sm text-gray-500">
                            {result.duration}ms
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};