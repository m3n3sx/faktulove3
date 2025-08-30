import React, { useState } from 'react';
import {
  MigrationDashboard,
  ComponentUsageAnalyzer,
  MigrationValidator,
  MigrationTester,
  RollbackControlPanel,
  type ValidationReport,
  type TestSuiteReport,
  type ComponentUsage,
} from '../index';

/**
 * Comprehensive Migration Management Interface
 * 
 * This component demonstrates the complete migration workflow using all
 * the gradual migration utilities together.
 */
export const ComprehensiveMigrationExample: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analyze' | 'validate' | 'test' | 'rollback'>('dashboard');
  const [selectedComponent, setSelectedComponent] = useState<string>('');
  const [analysisData, setAnalysisData] = useState<ComponentUsage[]>([]);
  const [validationReport, setValidationReport] = useState<ValidationReport | null>(null);
  const [testReport, setTestReport] = useState<TestSuiteReport | null>(null);

  const tabs = [
    { id: 'dashboard', label: '📊 Dashboard', description: 'Migration overview and progress tracking' },
    { id: 'analyze', label: '🔍 Analyze', description: 'Component usage analysis and recommendations' },
    { id: 'validate', label: '✅ Validate', description: 'Migration validation and issue detection' },
    { id: 'test', label: '🧪 Test', description: 'Comprehensive testing suite for migrations' },
    { id: 'rollback', label: '🔄 Rollback', description: 'Rollback controls and recovery options' },
  ];

  const handleComponentClick = (componentName: string) => {
    setSelectedComponent(componentName);
    setActiveTab('rollback');
  };

  const handleAnalysisComplete = (data: ComponentUsage[]) => {
    setAnalysisData(data);
    console.log('Analysis completed:', data);
  };

  const handleValidationComplete = (report: ValidationReport) => {
    setValidationReport(report);
    console.log('Validation completed:', report);
  };

  const handleTestComplete = (report: TestSuiteReport) => {
    setTestReport(report);
    console.log('Testing completed:', report);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">
                🚀 Migration Dashboard
              </h3>
              <p className="text-blue-700 mb-4">
                Track your design system migration progress, view component status, and get recommendations.
              </p>
            </div>
            
            <MigrationDashboard 
              showDetails={true}
              onComponentClick={handleComponentClick}
            />
            
            {/* Quick Actions */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold mb-3">Quick Actions</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                <button
                  onClick={() => setActiveTab('analyze')}
                  className="p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
                >
                  <div className="font-medium">Analyze Components</div>
                  <div className="text-sm text-gray-600">Find migration opportunities</div>
                </button>
                
                <button
                  onClick={() => setActiveTab('validate')}
                  className="p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
                >
                  <div className="font-medium">Validate Migration</div>
                  <div className="text-sm text-gray-600">Check for issues</div>
                </button>
                
                <button
                  onClick={() => setActiveTab('test')}
                  className="p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
                >
                  <div className="font-medium">Run Tests</div>
                  <div className="text-sm text-gray-600">Comprehensive testing</div>
                </button>
                
                <button
                  onClick={() => window.open('https://github.com/your-org/design-system-migration', '_blank')}
                  className="p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
                >
                  <div className="font-medium">CLI Tools</div>
                  <div className="text-sm text-gray-600">Command line utilities</div>
                </button>
              </div>
            </div>
          </div>
        );

      case 'analyze':
        return (
          <div className="space-y-6">
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-purple-800 mb-2">
                🔍 Component Usage Analysis
              </h3>
              <p className="text-purple-700 mb-4">
                Analyze your codebase to identify components that need migration and discover Polish business opportunities.
              </p>
            </div>
            
            <ComponentUsageAnalyzer onAnalysisComplete={handleAnalysisComplete} />
            
            {/* CLI Commands */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold mb-3">CLI Commands</h4>
              <div className="space-y-2 font-mono text-sm">
                <div className="bg-black text-green-400 p-2 rounded">
                  $ npm run migrate:analyze
                </div>
                <div className="bg-black text-green-400 p-2 rounded">
                  $ npm run migrate:analyze:component Button
                </div>
                <div className="bg-black text-green-400 p-2 rounded">
                  $ npm run migrate:report:html
                </div>
              </div>
            </div>
          </div>
        );

      case 'validate':
        return (
          <div className="space-y-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                ✅ Migration Validation
              </h3>
              <p className="text-green-700 mb-4">
                Validate your migration with comprehensive checks for imports, props, accessibility, and Polish business logic.
              </p>
            </div>
            
            <MigrationValidator onValidationComplete={handleValidationComplete} />
            
            {/* Validation Summary */}
            {validationReport && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold mb-3">Latest Validation Results</h4>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="p-3 bg-red-50 rounded">
                    <div className="text-2xl font-bold text-red-600">{validationReport.errors.length}</div>
                    <div className="text-sm text-red-700">Errors</div>
                  </div>
                  <div className="p-3 bg-yellow-50 rounded">
                    <div className="text-2xl font-bold text-yellow-600">{validationReport.warnings.length}</div>
                    <div className="text-sm text-yellow-700">Warnings</div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded">
                    <div className="text-2xl font-bold text-blue-600">{validationReport.overallScore}</div>
                    <div className="text-sm text-blue-700">Score</div>
                  </div>
                </div>
              </div>
            )}
            
            {/* CLI Commands */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold mb-3">CLI Commands</h4>
              <div className="space-y-2 font-mono text-sm">
                <div className="bg-black text-green-400 p-2 rounded">
                  $ npm run migrate:validate
                </div>
                <div className="bg-black text-green-400 p-2 rounded">
                  $ npm run migrate:component Button --dry-run
                </div>
              </div>
            </div>
          </div>
        );

      case 'test':
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">
                🧪 Migration Testing Suite
              </h3>
              <p className="text-blue-700 mb-4">
                Run comprehensive tests including unit, integration, visual regression, accessibility, and Polish business logic tests.
              </p>
            </div>
            
            <MigrationTester onTestComplete={handleTestComplete} />
            
            {/* Test Summary */}
            {testReport && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold mb-3">Latest Test Results</h4>
                <div className="grid grid-cols-4 gap-4 text-center">
                  <div className="p-3 bg-gray-50 rounded">
                    <div className="text-2xl font-bold text-gray-600">{testReport.totalTests}</div>
                    <div className="text-sm text-gray-700">Total</div>
                  </div>
                  <div className="p-3 bg-green-50 rounded">
                    <div className="text-2xl font-bold text-green-600">{testReport.passed}</div>
                    <div className="text-sm text-green-700">Passed</div>
                  </div>
                  <div className="p-3 bg-red-50 rounded">
                    <div className="text-2xl font-bold text-red-600">{testReport.failed}</div>
                    <div className="text-sm text-red-700">Failed</div>
                  </div>
                  <div className="p-3 bg-yellow-50 rounded">
                    <div className="text-2xl font-bold text-yellow-600">{testReport.skipped}</div>
                    <div className="text-sm text-yellow-700">Skipped</div>
                  </div>
                </div>
                <div className="mt-3 text-sm text-gray-600 text-center">
                  Duration: {(testReport.duration / 1000).toFixed(1)}s
                </div>
              </div>
            )}
          </div>
        );

      case 'rollback':
        return (
          <div className="space-y-6">
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-orange-800 mb-2">
                🔄 Migration Rollback Controls
              </h3>
              <p className="text-orange-700 mb-4">
                Safely rollback migrations when issues are detected. Choose from immediate, gradual, or manual rollback strategies.
              </p>
            </div>
            
            {selectedComponent ? (
              <RollbackControlPanel 
                componentName={selectedComponent}
                onRollbackComplete={(result) => {
                  console.log('Rollback completed:', result);
                  if (result.success) {
                    alert(`Successfully rolled back ${result.componentName}`);
                  } else {
                    alert(`Rollback failed: ${result.message}`);
                  }
                }}
              />
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
                <h4 className="font-semibold mb-2">Select a Component</h4>
                <p className="text-gray-600 mb-4">
                  Choose a component from the dashboard or enter a component name to manage rollback options.
                </p>
                
                <div className="max-w-md mx-auto">
                  <input
                    type="text"
                    placeholder="Enter component name (e.g., Button)"
                    value={selectedComponent}
                    onChange={(e) => setSelectedComponent(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded mb-3"
                  />
                  <button
                    onClick={() => setSelectedComponent(selectedComponent || 'Button')}
                    disabled={!selectedComponent.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                  >
                    Load Rollback Controls
                  </button>
                </div>
              </div>
            )}
            
            {/* CLI Commands */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold mb-3">CLI Commands</h4>
              <div className="space-y-2 font-mono text-sm">
                <div className="bg-black text-green-400 p-2 rounded">
                  $ npm run migrate:rollback
                </div>
                <div className="bg-black text-green-400 p-2 rounded">
                  $ npm run migrate:rollback 1640995200000
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="comprehensive-migration-example min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Design System Migration Center
            </h1>
            <p className="mt-2 text-gray-600">
              Comprehensive tools for migrating to the FaktuLove design system with Polish business components
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <span>{tab.label}</span>
                </div>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Description */}
      <div className="bg-blue-50 border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <p className="text-blue-700 text-sm">
            {tabs.find(tab => tab.id === activeTab)?.description}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderTabContent()}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Design System Migration Tools v1.0.0
            </div>
            <div className="flex space-x-4 text-sm">
              <a href="#" className="text-blue-600 hover:text-blue-800">Documentation</a>
              <a href="#" className="text-blue-600 hover:text-blue-800">GitHub</a>
              <a href="#" className="text-blue-600 hover:text-blue-800">Support</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveMigrationExample;