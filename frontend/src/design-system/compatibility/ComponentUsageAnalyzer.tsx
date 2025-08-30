import React, { useState, useEffect } from 'react';
import { useMigrationTracker } from './ComponentWrapper';

/**
 * Component usage data structure
 */
export interface ComponentUsage {
  componentName: string;
  totalUsages: number;
  files: Array<{
    path: string;
    usages: number;
    lines: number[];
    migrationStatus: 'not_started' | 'in_progress' | 'completed' | 'deprecated';
  }>;
  migrationPriority: 'high' | 'medium' | 'low';
  estimatedEffort: 'small' | 'medium' | 'large';
  dependencies: string[];
  polishBusinessOpportunities: Array<{
    type: 'nip-validation' | 'vat-calculation' | 'currency-formatting' | 'date-formatting';
    description: string;
    suggestedComponent: string;
  }>;
}

/**
 * Analysis configuration
 */
export interface AnalysisConfig {
  includeTests: boolean;
  includeStorybook: boolean;
  minUsageThreshold: number;
  excludePatterns: string[];
  polishBusinessDetection: boolean;
}

/**
 * Component Usage Analyzer Hook
 */
export function useComponentUsageAnalyzer() {
  const [analysisData, setAnalysisData] = useState<ComponentUsage[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [config, setConfig] = useState<AnalysisConfig>({
    includeTests: false,
    includeStorybook: false,
    minUsageThreshold: 1,
    excludePatterns: ['node_modules', 'build', 'dist'],
    polishBusinessDetection: true,
  });

  const migrationTracker = useMigrationTracker();

  /**
   * Analyze component usage across the codebase
   */
  const analyzeUsage = async (targetComponents?: string[]) => {
    setIsAnalyzing(true);
    
    try {
      // In a real implementation, this would scan the actual filesystem
      // For now, we'll simulate the analysis
      const mockAnalysis = await simulateComponentAnalysis(targetComponents, config);
      setAnalysisData(mockAnalysis);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  /**
   * Get migration recommendations based on usage analysis
   */
  const getMigrationRecommendations = () => {
    return analysisData
      .filter(component => component.migrationPriority === 'high')
      .sort((a, b) => b.totalUsages - a.totalUsages)
      .slice(0, 5)
      .map(component => ({
        componentName: component.componentName,
        reason: `High usage (${component.totalUsages} instances) with ${component.estimatedEffort} migration effort`,
        priority: component.migrationPriority,
        estimatedDays: getEstimatedMigrationDays(component),
      }));
  };

  /**
   * Get Polish business component opportunities
   */
  const getPolishBusinessOpportunities = () => {
    return analysisData
      .flatMap(component => 
        component.polishBusinessOpportunities.map(opportunity => ({
          ...opportunity,
          componentName: component.componentName,
          usageCount: component.totalUsages,
        }))
      )
      .sort((a, b) => b.usageCount - a.usageCount);
  };

  /**
   * Export analysis data
   */
  const exportAnalysis = (format: 'json' | 'csv' | 'html' = 'json') => {
    const data = {
      timestamp: new Date().toISOString(),
      config,
      components: analysisData,
      recommendations: getMigrationRecommendations(),
      polishBusinessOpportunities: getPolishBusinessOpportunities(),
      summary: {
        totalComponents: analysisData.length,
        totalUsages: analysisData.reduce((sum, comp) => sum + comp.totalUsages, 0),
        highPriorityComponents: analysisData.filter(c => c.migrationPriority === 'high').length,
        polishBusinessOpportunities: getPolishBusinessOpportunities().length,
      },
    };

    switch (format) {
      case 'json':
        return JSON.stringify(data, null, 2);
      case 'csv':
        return convertToCSV(data);
      case 'html':
        return generateHTMLReport(data);
      default:
        return JSON.stringify(data, null, 2);
    }
  };

  return {
    analysisData,
    isAnalyzing,
    config,
    setConfig,
    analyzeUsage,
    getMigrationRecommendations,
    getPolishBusinessOpportunities,
    exportAnalysis,
  };
}

/**
 * Simulate component analysis (in real implementation, this would scan files)
 */
async function simulateComponentAnalysis(
  targetComponents?: string[],
  config?: AnalysisConfig
): Promise<ComponentUsage[]> {
  // Simulate async analysis
  await new Promise(resolve => setTimeout(resolve, 1000));

  const components = targetComponents || [
    'Button', 'Input', 'Form', 'Table', 'Card', 'Select', 'Checkbox', 'Radio'
  ];

  return components.map(componentName => {
    const totalUsages = Math.floor(Math.random() * 50) + 5;
    const fileCount = Math.floor(Math.random() * 10) + 2;
    
    return {
      componentName,
      totalUsages,
      files: Array.from({ length: fileCount }, (_, i) => ({
        path: `src/components/${componentName.toLowerCase()}/${componentName}${i + 1}.tsx`,
        usages: Math.floor(totalUsages / fileCount) + (i === 0 ? totalUsages % fileCount : 0),
        lines: Array.from({ length: Math.floor(Math.random() * 5) + 1 }, () => 
          Math.floor(Math.random() * 100) + 1
        ),
        migrationStatus: (['not_started', 'in_progress', 'completed', 'deprecated'] as const)[
          Math.floor(Math.random() * 4)
        ],
      })),
      migrationPriority: (['high', 'medium', 'low'] as const)[Math.floor(Math.random() * 3)],
      estimatedEffort: (['small', 'medium', 'large'] as const)[Math.floor(Math.random() * 3)],
      dependencies: components.filter(() => Math.random() > 0.7).slice(0, 3),
      polishBusinessOpportunities: generatePolishBusinessOpportunities(componentName),
    };
  });
}

/**
 * Generate Polish business opportunities for a component
 */
function generatePolishBusinessOpportunities(componentName: string) {
  const opportunities = [];
  
  if (componentName === 'Input') {
    opportunities.push({
      type: 'nip-validation' as const,
      description: 'Input fields handling NIP numbers could use NIPValidator component',
      suggestedComponent: '@design-system/polish-business/NIPValidator',
    });
  }
  
  if (componentName === 'Form') {
    opportunities.push({
      type: 'vat-calculation' as const,
      description: 'Forms with VAT calculations could use VATRateSelector component',
      suggestedComponent: '@design-system/polish-business/VATRateSelector',
    });
  }
  
  if (componentName === 'Input' || componentName === 'Form') {
    if (Math.random() > 0.5) {
      opportunities.push({
        type: 'currency-formatting' as const,
        description: 'Currency inputs could use CurrencyInput component for PLN formatting',
        suggestedComponent: '@design-system/polish-business/CurrencyInput',
      });
    }
    
    if (Math.random() > 0.6) {
      opportunities.push({
        type: 'date-formatting' as const,
        description: 'Date inputs could use DatePicker with Polish date formats',
        suggestedComponent: '@design-system/polish-business/DatePicker',
      });
    }
  }
  
  return opportunities;
}

/**
 * Get estimated migration days for a component
 */
function getEstimatedMigrationDays(component: ComponentUsage): number {
  const baseEffort = {
    small: 1,
    medium: 3,
    large: 7,
  };
  
  const usageMultiplier = Math.min(component.totalUsages / 10, 2);
  const dependencyMultiplier = 1 + (component.dependencies.length * 0.2);
  
  return Math.ceil(baseEffort[component.estimatedEffort] * usageMultiplier * dependencyMultiplier);
}

/**
 * Convert analysis data to CSV format
 */
function convertToCSV(data: any): string {
  const headers = [
    'Component',
    'Total Usages',
    'Files',
    'Priority',
    'Effort',
    'Dependencies',
    'Polish Business Opportunities'
  ];
  
  const rows = data.components.map((comp: ComponentUsage) => [
    comp.componentName,
    comp.totalUsages,
    comp.files.length,
    comp.migrationPriority,
    comp.estimatedEffort,
    comp.dependencies.join('; '),
    comp.polishBusinessOpportunities.length,
  ]);
  
  return [headers, ...rows].map(row => row.join(',')).join('\n');
}

/**
 * Generate HTML report
 */
function generateHTMLReport(data: any): string {
  return `
<!DOCTYPE html>
<html>
<head>
    <title>Component Usage Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .high { color: #d32f2f; font-weight: bold; }
        .medium { color: #f57c00; }
        .low { color: #388e3c; }
    </style>
</head>
<body>
    <h1>Component Usage Analysis Report</h1>
    <p>Generated: ${new Date(data.timestamp).toLocaleString()}</p>
    
    <h2>Summary</h2>
    <ul>
        <li>Total Components: ${data.summary.totalComponents}</li>
        <li>Total Usages: ${data.summary.totalUsages}</li>
        <li>High Priority Components: ${data.summary.highPriorityComponents}</li>
        <li>Polish Business Opportunities: ${data.summary.polishBusinessOpportunities}</li>
    </ul>
    
    <h2>Component Details</h2>
    <table>
        <thead>
            <tr>
                <th>Component</th>
                <th>Usages</th>
                <th>Files</th>
                <th>Priority</th>
                <th>Effort</th>
                <th>Dependencies</th>
            </tr>
        </thead>
        <tbody>
            ${data.components.map((comp: ComponentUsage) => `
                <tr>
                    <td>${comp.componentName}</td>
                    <td>${comp.totalUsages}</td>
                    <td>${comp.files.length}</td>
                    <td class="${comp.migrationPriority}">${comp.migrationPriority}</td>
                    <td>${comp.estimatedEffort}</td>
                    <td>${comp.dependencies.join(', ')}</td>
                </tr>
            `).join('')}
        </tbody>
    </table>
    
    <h2>Migration Recommendations</h2>
    <ol>
        ${data.recommendations.map((rec: any) => `
            <li>
                <strong>${rec.componentName}</strong> - ${rec.reason}
                <br><small>Estimated: ${rec.estimatedDays} day(s)</small>
            </li>
        `).join('')}
    </ol>
    
    <h2>Polish Business Opportunities</h2>
    <ul>
        ${data.polishBusinessOpportunities.map((opp: any) => `
            <li>
                <strong>${opp.componentName}</strong>: ${opp.description}
                <br><small>Suggested: ${opp.suggestedComponent}</small>
            </li>
        `).join('')}
    </ul>
</body>
</html>
  `;
}

/**
 * Component Usage Analyzer UI Component
 */
export interface ComponentUsageAnalyzerProps {
  onAnalysisComplete?: (data: ComponentUsage[]) => void;
}

export const ComponentUsageAnalyzer: React.FC<ComponentUsageAnalyzerProps> = ({
  onAnalysisComplete,
}) => {
  const {
    analysisData,
    isAnalyzing,
    config,
    setConfig,
    analyzeUsage,
    getMigrationRecommendations,
    getPolishBusinessOpportunities,
    exportAnalysis,
  } = useComponentUsageAnalyzer();

  const [selectedComponents, setSelectedComponents] = useState<string[]>([]);
  const [exportFormat, setExportFormat] = useState<'json' | 'csv' | 'html'>('json');

  const availableComponents = [
    'Button', 'Input', 'Form', 'Table', 'Card', 'Select', 'Checkbox', 'Radio',
    'Modal', 'Dropdown', 'Tabs', 'Accordion', 'Tooltip', 'Badge'
  ];

  const handleAnalyze = async () => {
    await analyzeUsage(selectedComponents.length > 0 ? selectedComponents : undefined);
    onAnalysisComplete?.(analysisData);
  };

  const handleExport = () => {
    const data = exportAnalysis(exportFormat);
    const blob = new Blob([data], { 
      type: exportFormat === 'json' ? 'application/json' : 
           exportFormat === 'csv' ? 'text/csv' : 'text/html' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `component-analysis.${exportFormat}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const recommendations = getMigrationRecommendations();
  const polishOpportunities = getPolishBusinessOpportunities();

  return (
    <div className="component-usage-analyzer p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6">Component Usage Analyzer</h2>
      
      {/* Configuration */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Analysis Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-2">Target Components</label>
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
              Leave empty to analyze all components
            </p>
          </div>
          
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config.includeTests}
                onChange={(e) => setConfig({ ...config, includeTests: e.target.checked })}
                className="mr-2"
              />
              Include test files
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config.includeStorybook}
                onChange={(e) => setConfig({ ...config, includeStorybook: e.target.checked })}
                className="mr-2"
              />
              Include Storybook files
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config.polishBusinessDetection}
                onChange={(e) => setConfig({ ...config, polishBusinessDetection: e.target.checked })}
                className="mr-2"
              />
              Detect Polish business opportunities
            </label>
            
            <div>
              <label className="block text-sm font-medium mb-1">
                Minimum usage threshold
              </label>
              <input
                type="number"
                value={config.minUsageThreshold}
                onChange={(e) => setConfig({ ...config, minUsageThreshold: parseInt(e.target.value) })}
                className="w-full px-3 py-1 border border-gray-300 rounded"
                min="1"
              />
            </div>
          </div>
        </div>
        
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
        </button>
      </div>

      {/* Results */}
      {analysisData.length > 0 && (
        <>
          {/* Summary */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Analysis Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {analysisData.length}
                </div>
                <div className="text-sm text-blue-700">Components</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {analysisData.reduce((sum, comp) => sum + comp.totalUsages, 0)}
                </div>
                <div className="text-sm text-green-700">Total Usages</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {analysisData.filter(c => c.migrationPriority === 'high').length}
                </div>
                <div className="text-sm text-yellow-700">High Priority</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {polishOpportunities.length}
                </div>
                <div className="text-sm text-purple-700">Polish Business Opportunities</div>
              </div>
            </div>
          </div>

          {/* Migration Recommendations */}
          {recommendations.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Migration Recommendations</h3>
              <div className="space-y-2">
                {recommendations.map((rec, index) => (
                  <div key={index} className="p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                    <div className="font-medium">{rec.componentName}</div>
                    <div className="text-sm text-gray-600">{rec.reason}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      Estimated: {rec.estimatedDays} day(s)
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Polish Business Opportunities */}
          {polishOpportunities.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">🇵🇱 Polish Business Opportunities</h3>
              <div className="space-y-2">
                {polishOpportunities.map((opp, index) => (
                  <div key={index} className="p-3 bg-purple-50 border-l-4 border-purple-400 rounded">
                    <div className="font-medium">{opp.componentName}</div>
                    <div className="text-sm text-gray-600">{opp.description}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      Suggested: <code>{opp.suggestedComponent}</code>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Component Details */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Component Details</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-300 px-4 py-2 text-left">Component</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Usages</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Files</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Priority</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Effort</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Dependencies</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisData.map((component, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2 font-medium">
                        {component.componentName}
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {component.totalUsages}
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {component.files.length}
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          component.migrationPriority === 'high' ? 'bg-red-100 text-red-800' :
                          component.migrationPriority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {component.migrationPriority}
                        </span>
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {component.estimatedEffort}
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {component.dependencies.join(', ') || 'None'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Export */}
          <div className="flex items-center space-x-4">
            <select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value as 'json' | 'csv' | 'html')}
              className="px-3 py-2 border border-gray-300 rounded"
            >
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="html">HTML</option>
            </select>
            
            <button
              onClick={handleExport}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Export Analysis
            </button>
          </div>
        </>
      )}
    </div>
  );
};