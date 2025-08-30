import React, { useState, useEffect } from 'react';
import { useMigrationTracker } from './ComponentWrapper';

/**
 * Validation rule types
 */
export type ValidationRuleType = 
  | 'import-consistency'
  | 'prop-compatibility'
  | 'accessibility'
  | 'performance'
  | 'polish-business'
  | 'css-conflicts'
  | 'dependency-check';

/**
 * Validation result
 */
export interface ValidationResult {
  ruleType: ValidationRuleType;
  severity: 'error' | 'warning' | 'info';
  message: string;
  file?: string;
  line?: number;
  column?: number;
  suggestion?: string;
  autoFixable?: boolean;
}

/**
 * Validation report
 */
export interface ValidationReport {
  timestamp: Date;
  totalFiles: number;
  totalIssues: number;
  errors: ValidationResult[];
  warnings: ValidationResult[];
  info: ValidationResult[];
  summary: {
    [K in ValidationRuleType]: {
      errors: number;
      warnings: number;
      info: number;
    };
  };
  overallScore: number; // 0-100
}

/**
 * Validation configuration
 */
export interface ValidationConfig {
  enabledRules: ValidationRuleType[];
  strictMode: boolean;
  polishBusinessValidation: boolean;
  accessibilityLevel: 'AA' | 'AAA';
  performanceThresholds: {
    bundleSize: number; // KB
    renderTime: number; // ms
  };
}

/**
 * Migration Validator Hook
 */
export function useMigrationValidator() {
  const [validationReport, setValidationReport] = useState<ValidationReport | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [config, setConfig] = useState<ValidationConfig>({
    enabledRules: [
      'import-consistency',
      'prop-compatibility',
      'accessibility',
      'performance',
      'polish-business',
      'css-conflicts',
      'dependency-check',
    ],
    strictMode: false,
    polishBusinessValidation: true,
    accessibilityLevel: 'AA',
    performanceThresholds: {
      bundleSize: 500,
      renderTime: 100,
    },
  });

  const migrationTracker = useMigrationTracker();

  /**
   * Run comprehensive validation
   */
  const runValidation = async (targetFiles?: string[]) => {
    setIsValidating(true);
    
    try {
      const report = await performValidation(config, targetFiles);
      setValidationReport(report);
      return report;
    } catch (error) {
      console.error('Validation failed:', error);
      throw error;
    } finally {
      setIsValidating(false);
    }
  };

  /**
   * Auto-fix issues where possible
   */
  const autoFixIssues = async (issues: ValidationResult[]) => {
    const fixableIssues = issues.filter(issue => issue.autoFixable);
    
    if (fixableIssues.length === 0) {
      return { fixed: 0, errors: [] };
    }

    try {
      // In a real implementation, this would apply fixes to actual files
      const results = await Promise.all(
        fixableIssues.map(issue => applyAutoFix(issue))
      );
      
      const fixed = results.filter(r => r.success).length;
      const errors = results.filter(r => !r.success).map(r => r.error);
      
      // Re-run validation after fixes
      if (fixed > 0) {
        await runValidation();
      }
      
      return { fixed, errors };
    } catch (error) {
      console.error('Auto-fix failed:', error);
      return { fixed: 0, errors: [error instanceof Error ? error.message : String(error)] };
    }
  };

  /**
   * Get validation score breakdown
   */
  const getScoreBreakdown = () => {
    if (!validationReport) return null;

    const maxScore = 100;
    const errorPenalty = 10;
    const warningPenalty = 3;
    const infoPenalty = 1;

    const totalPenalty = 
      validationReport.errors.length * errorPenalty +
      validationReport.warnings.length * warningPenalty +
      validationReport.info.length * infoPenalty;

    const score = Math.max(0, maxScore - totalPenalty);

    return {
      score,
      breakdown: {
        errors: validationReport.errors.length,
        warnings: validationReport.warnings.length,
        info: validationReport.info.length,
        totalPenalty,
      },
      grade: score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F',
    };
  };

  return {
    validationReport,
    isValidating,
    config,
    setConfig,
    runValidation,
    autoFixIssues,
    getScoreBreakdown,
  };
}

/**
 * Perform validation (simulated implementation)
 */
async function performValidation(
  config: ValidationConfig,
  targetFiles?: string[]
): Promise<ValidationReport> {
  // Simulate validation process
  await new Promise(resolve => setTimeout(resolve, 2000));

  const results: ValidationResult[] = [];
  const files = targetFiles || [
    'src/components/Button.tsx',
    'src/components/Input.tsx',
    'src/components/Form.tsx',
    'src/pages/InvoiceForm.tsx',
    'src/pages/Dashboard.tsx',
  ];

  // Simulate validation rules
  files.forEach(file => {
    results.push(...simulateValidationForFile(file, config));
  });

  const errors = results.filter(r => r.severity === 'error');
  const warnings = results.filter(r => r.severity === 'warning');
  const info = results.filter(r => r.severity === 'info');

  // Calculate summary
  const summary = config.enabledRules.reduce((acc, ruleType) => {
    acc[ruleType] = {
      errors: results.filter(r => r.ruleType === ruleType && r.severity === 'error').length,
      warnings: results.filter(r => r.ruleType === ruleType && r.severity === 'warning').length,
      info: results.filter(r => r.ruleType === ruleType && r.severity === 'info').length,
    };
    return acc;
  }, {} as ValidationReport['summary']);

  // Calculate overall score
  const maxScore = 100;
  const errorPenalty = 10;
  const warningPenalty = 3;
  const infoPenalty = 1;
  
  const totalPenalty = 
    errors.length * errorPenalty +
    warnings.length * warningPenalty +
    info.length * infoPenalty;

  const overallScore = Math.max(0, maxScore - totalPenalty);

  return {
    timestamp: new Date(),
    totalFiles: files.length,
    totalIssues: results.length,
    errors,
    warnings,
    info,
    summary,
    overallScore,
  };
}

/**
 * Simulate validation for a single file
 */
function simulateValidationForFile(
  file: string,
  config: ValidationConfig
): ValidationResult[] {
  const results: ValidationResult[] = [];

  // Import consistency validation
  if (config.enabledRules.includes('import-consistency')) {
    if (Math.random() > 0.7) {
      results.push({
        ruleType: 'import-consistency',
        severity: 'error',
        message: 'Mixed imports from legacy and design system components',
        file,
        line: Math.floor(Math.random() * 50) + 1,
        suggestion: 'Use only design system imports',
        autoFixable: true,
      });
    }
  }

  // Prop compatibility validation
  if (config.enabledRules.includes('prop-compatibility')) {
    if (Math.random() > 0.6) {
      results.push({
        ruleType: 'prop-compatibility',
        severity: 'warning',
        message: 'Deprecated prop usage detected',
        file,
        line: Math.floor(Math.random() * 50) + 1,
        suggestion: 'Replace with new prop API',
        autoFixable: true,
      });
    }
  }

  // Accessibility validation
  if (config.enabledRules.includes('accessibility')) {
    if (Math.random() > 0.8) {
      results.push({
        ruleType: 'accessibility',
        severity: config.accessibilityLevel === 'AAA' ? 'error' : 'warning',
        message: 'Missing aria-label on interactive element',
        file,
        line: Math.floor(Math.random() * 50) + 1,
        suggestion: 'Add descriptive aria-label',
        autoFixable: false,
      });
    }
  }

  // Performance validation
  if (config.enabledRules.includes('performance')) {
    if (Math.random() > 0.9) {
      results.push({
        ruleType: 'performance',
        severity: 'warning',
        message: 'Large component bundle detected',
        file,
        suggestion: 'Consider code splitting or lazy loading',
        autoFixable: false,
      });
    }
  }

  // Polish business validation
  if (config.enabledRules.includes('polish-business') && config.polishBusinessValidation) {
    if (file.includes('Invoice') && Math.random() > 0.5) {
      results.push({
        ruleType: 'polish-business',
        severity: 'info',
        message: 'Could benefit from Polish business components',
        file,
        line: Math.floor(Math.random() * 50) + 1,
        suggestion: 'Consider using NIPValidator or CurrencyInput',
        autoFixable: false,
      });
    }
  }

  // CSS conflicts validation
  if (config.enabledRules.includes('css-conflicts')) {
    if (Math.random() > 0.7) {
      results.push({
        ruleType: 'css-conflicts',
        severity: 'warning',
        message: 'Potential CSS class conflict with design system',
        file,
        line: Math.floor(Math.random() * 50) + 1,
        suggestion: 'Use design system utility classes',
        autoFixable: true,
      });
    }
  }

  // Dependency check validation
  if (config.enabledRules.includes('dependency-check')) {
    if (Math.random() > 0.8) {
      results.push({
        ruleType: 'dependency-check',
        severity: 'error',
        message: 'Missing design system dependency',
        file,
        suggestion: 'Install required design system package',
        autoFixable: false,
      });
    }
  }

  return results;
}

/**
 * Apply auto-fix for a validation issue
 */
async function applyAutoFix(issue: ValidationResult): Promise<{ success: boolean; error?: string }> {
  // Simulate auto-fix process
  await new Promise(resolve => setTimeout(resolve, 100));

  // In a real implementation, this would modify actual files
  switch (issue.ruleType) {
    case 'import-consistency':
      // Fix import statements
      return { success: Math.random() > 0.1 };
    
    case 'prop-compatibility':
      // Update prop usage
      return { success: Math.random() > 0.2 };
    
    case 'css-conflicts':
      // Replace CSS classes
      return { success: Math.random() > 0.15 };
    
    default:
      return { success: false, error: 'Auto-fix not supported for this rule type' };
  }
}

/**
 * Migration Validator UI Component
 */
export interface MigrationValidatorProps {
  onValidationComplete?: (report: ValidationReport) => void;
}

export const MigrationValidator: React.FC<MigrationValidatorProps> = ({
  onValidationComplete,
}) => {
  const {
    validationReport,
    isValidating,
    config,
    setConfig,
    runValidation,
    autoFixIssues,
    getScoreBreakdown,
  } = useMigrationValidator();

  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [autoFixing, setAutoFixing] = useState(false);

  const scoreBreakdown = getScoreBreakdown();

  const handleValidation = async () => {
    const report = await runValidation(selectedFiles.length > 0 ? selectedFiles : undefined);
    onValidationComplete?.(report);
  };

  const handleAutoFix = async () => {
    if (!validationReport) return;
    
    setAutoFixing(true);
    try {
      const fixableIssues = [
        ...validationReport.errors,
        ...validationReport.warnings,
      ].filter(issue => issue.autoFixable);
      
      const result = await autoFixIssues(fixableIssues);
      
      if (result.fixed > 0) {
        alert(`Fixed ${result.fixed} issue(s)`);
      } else {
        alert('No auto-fixable issues found');
      }
      
      if (result.errors.length > 0) {
        console.error('Auto-fix errors:', result.errors);
      }
    } catch (error) {
      console.error('Auto-fix failed:', error);
    } finally {
      setAutoFixing(false);
    }
  };

  const getSeverityColor = (severity: ValidationResult['severity']) => {
    switch (severity) {
      case 'error': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'info': return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getSeverityIcon = (severity: ValidationResult['severity']) => {
    switch (severity) {
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
    }
  };

  return (
    <div className="migration-validator p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6">Migration Validator</h2>
      
      {/* Configuration */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Validation Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-2">Validation Rules</h4>
            <div className="space-y-2">
              {[
                { key: 'import-consistency', label: 'Import Consistency' },
                { key: 'prop-compatibility', label: 'Prop Compatibility' },
                { key: 'accessibility', label: 'Accessibility' },
                { key: 'performance', label: 'Performance' },
                { key: 'polish-business', label: 'Polish Business' },
                { key: 'css-conflicts', label: 'CSS Conflicts' },
                { key: 'dependency-check', label: 'Dependency Check' },
              ].map(rule => (
                <label key={rule.key} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={config.enabledRules.includes(rule.key as ValidationRuleType)}
                    onChange={(e) => {
                      const newRules = e.target.checked
                        ? [...config.enabledRules, rule.key as ValidationRuleType]
                        : config.enabledRules.filter(r => r !== rule.key);
                      setConfig({ ...config, enabledRules: newRules });
                    }}
                    className="mr-2"
                  />
                  {rule.label}
                </label>
              ))}
            </div>
          </div>
          
          <div className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config.strictMode}
                onChange={(e) => setConfig({ ...config, strictMode: e.target.checked })}
                className="mr-2"
              />
              Strict Mode
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config.polishBusinessValidation}
                onChange={(e) => setConfig({ ...config, polishBusinessValidation: e.target.checked })}
                className="mr-2"
              />
              Polish Business Validation
            </label>
            
            <div>
              <label className="block text-sm font-medium mb-1">
                Accessibility Level
              </label>
              <select
                value={config.accessibilityLevel}
                onChange={(e) => setConfig({ ...config, accessibilityLevel: e.target.value as 'AA' | 'AAA' })}
                className="w-full px-3 py-2 border border-gray-300 rounded"
              >
                <option value="AA">WCAG 2.1 AA</option>
                <option value="AAA">WCAG 2.1 AAA</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">
                Bundle Size Threshold (KB)
              </label>
              <input
                type="number"
                value={config.performanceThresholds.bundleSize}
                onChange={(e) => setConfig({
                  ...config,
                  performanceThresholds: {
                    ...config.performanceThresholds,
                    bundleSize: parseInt(e.target.value),
                  },
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded"
              />
            </div>
          </div>
        </div>
        
        <div className="mt-4 flex space-x-4">
          <button
            onClick={handleValidation}
            disabled={isValidating}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isValidating ? 'Validating...' : 'Run Validation'}
          </button>
          
          {validationReport && (
            <button
              onClick={handleAutoFix}
              disabled={autoFixing}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {autoFixing ? 'Fixing...' : 'Auto-Fix Issues'}
            </button>
          )}
        </div>
      </div>

      {/* Validation Results */}
      {validationReport && (
        <>
          {/* Score */}
          {scoreBreakdown && (
            <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Validation Score</h3>
                <div className="flex items-center space-x-4">
                  <div className="text-3xl font-bold text-blue-600">
                    {scoreBreakdown.score}
                  </div>
                  <div className={`text-2xl font-bold px-3 py-1 rounded ${
                    scoreBreakdown.grade === 'A' ? 'bg-green-100 text-green-800' :
                    scoreBreakdown.grade === 'B' ? 'bg-blue-100 text-blue-800' :
                    scoreBreakdown.grade === 'C' ? 'bg-yellow-100 text-yellow-800' :
                    scoreBreakdown.grade === 'D' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {scoreBreakdown.grade}
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium text-red-600">Errors:</span> {scoreBreakdown.breakdown.errors}
                </div>
                <div>
                  <span className="font-medium text-yellow-600">Warnings:</span> {scoreBreakdown.breakdown.warnings}
                </div>
                <div>
                  <span className="font-medium text-blue-600">Info:</span> {scoreBreakdown.breakdown.info}
                </div>
              </div>
            </div>
          )}

          {/* Summary */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Validation Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">
                  {validationReport.totalFiles}
                </div>
                <div className="text-sm text-gray-700">Files Checked</div>
              </div>
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {validationReport.errors.length}
                </div>
                <div className="text-sm text-red-700">Errors</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {validationReport.warnings.length}
                </div>
                <div className="text-sm text-yellow-700">Warnings</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {validationReport.info.length}
                </div>
                <div className="text-sm text-blue-700">Info</div>
              </div>
            </div>
          </div>

          {/* Issues List */}
          <div className="space-y-6">
            {['errors', 'warnings', 'info'].map(severity => {
              const issues = validationReport[severity as keyof Pick<ValidationReport, 'errors' | 'warnings' | 'info'>] as ValidationResult[];
              
              if (issues.length === 0) return null;
              
              return (
                <div key={severity}>
                  <h3 className="text-lg font-semibold mb-3 capitalize">
                    {severity} ({issues.length})
                  </h3>
                  <div className="space-y-2">
                    {issues.map((issue, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border ${getSeverityColor(issue.severity)}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="text-lg">{getSeverityIcon(issue.severity)}</span>
                              <span className="font-medium">{issue.ruleType.replace('-', ' ')}</span>
                              {issue.autoFixable && (
                                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                                  Auto-fixable
                                </span>
                              )}
                            </div>
                            <p className="mb-2">{issue.message}</p>
                            {issue.file && (
                              <p className="text-sm font-mono text-gray-600">
                                {issue.file}{issue.line ? `:${issue.line}` : ''}
                              </p>
                            )}
                            {issue.suggestion && (
                              <p className="text-sm text-gray-700 mt-2">
                                <strong>Suggestion:</strong> {issue.suggestion}
                              </p>
                            )}
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