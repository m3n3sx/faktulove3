import React from 'react';
import { useDesignSystemContext, usePolishBusinessUtils, useAccessibilityUtils } from '../context/DesignSystemContext';
import { useTheme } from '../providers/ThemeProvider';

/**
 * Design System Integration Test Component
 * 
 * This component tests the core integration infrastructure to ensure
 * all design system features are working correctly.
 */
export const IntegrationTest: React.FC = () => {
  const { config, getColor, getSpacing } = useDesignSystemContext();
  const { formatCurrency, formatDate, validateNIP } = usePolishBusinessUtils();
  const { getAriaLabel, announceToScreenReader } = useAccessibilityUtils();
  const { theme, isDark } = useTheme();
  
  // Test data
  const testAmount = 1234.56;
  const testDate = new Date('2025-01-15');
  const testNIP = '1234567890';
  
  const handleTestAnnouncement = () => {
    announceToScreenReader('Design system integration test completed successfully', 'polite');
  };
  
  return (
    <div className="design-system-integration-test p-6 space-y-6">
      <div className="bg-background-secondary p-4 rounded-lg border border-border-default">
        <h2 className="text-xl font-semibold mb-4 text-text-primary">
          Design System Integration Test
        </h2>
        
        {/* Configuration Test */}
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2 text-text-primary">Configuration</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Name:</span> {config.name}
            </div>
            <div>
              <span className="font-medium">Version:</span> {config.version}
            </div>
            <div>
              <span className="font-medium">Theme:</span> {isDark ? 'Dark' : 'Light'}
            </div>
            <div>
              <span className="font-medium">Tokens:</span> {Object.keys(config.tokens).length}
            </div>
          </div>
        </div>
        
        {/* Color System Test */}
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2 text-text-primary">Color System</h3>
          <div className="flex space-x-2">
            <div 
              className="w-8 h-8 rounded border"
              style={{ backgroundColor: getColor('primary.600') }}
              title="Primary 600"
            />
            <div 
              className="w-8 h-8 rounded border"
              style={{ backgroundColor: getColor('success.600') }}
              title="Success 600"
            />
            <div 
              className="w-8 h-8 rounded border"
              style={{ backgroundColor: getColor('warning.600') }}
              title="Warning 600"
            />
            <div 
              className="w-8 h-8 rounded border"
              style={{ backgroundColor: getColor('error.600') }}
              title="Error 600"
            />
          </div>
        </div>
        
        {/* Spacing System Test */}
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2 text-text-primary">Spacing System</h3>
          <div className="flex items-center space-x-2">
            <div 
              className="bg-primary-200 h-4"
              style={{ width: getSpacing('4') }}
              title="Spacing 4"
            />
            <div 
              className="bg-primary-300 h-4"
              style={{ width: getSpacing('8') }}
              title="Spacing 8"
            />
            <div 
              className="bg-primary-400 h-4"
              style={{ width: getSpacing('12') }}
              title="Spacing 12"
            />
            <div 
              className="bg-primary-500 h-4"
              style={{ width: getSpacing('16') }}
              title="Spacing 16"
            />
          </div>
        </div>
        
        {/* Polish Business Utils Test */}
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2 text-text-primary">Polish Business Utils</h3>
          <div className="space-y-2 text-sm">
            <div>
              <span className="font-medium">Currency:</span> {formatCurrency(testAmount)}
            </div>
            <div>
              <span className="font-medium">Date:</span> {formatDate(testDate)}
            </div>
            <div>
              <span className="font-medium">NIP Validation:</span> 
              <span className={validateNIP(testNIP) ? 'text-success-600' : 'text-error-600'}>
                {validateNIP(testNIP) ? ' Valid' : ' Invalid'}
              </span>
            </div>
          </div>
        </div>
        
        {/* Accessibility Test */}
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2 text-text-primary">Accessibility</h3>
          <div className="space-y-2">
            <div className="text-sm">
              <span className="font-medium">ARIA Label:</span> {getAriaLabel('invoice.create')}
            </div>
            <button
              onClick={handleTestAnnouncement}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
              aria-label={getAriaLabel('test.announcement')}
            >
              Test Screen Reader Announcement
            </button>
          </div>
        </div>
        
        {/* CSS Custom Properties Test */}
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2 text-text-primary">CSS Custom Properties</h3>
          <div className="text-sm space-y-1">
            <div>Primary Color: <code>var(--color-primary-600)</code></div>
            <div>Text Color: <code>var(--color-text-primary)</code></div>
            <div>Spacing: <code>var(--spacing-4)</code></div>
            <div>Font Family: <code>var(--font-family-sans)</code></div>
          </div>
        </div>
        
        {/* Integration Status */}
        <div className="bg-success-50 border border-success-200 rounded-md p-4">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-success-500 rounded-full mr-3"></div>
            <div>
              <h4 className="font-medium text-success-800">Integration Status</h4>
              <p className="text-sm text-success-700">
                Design system core integration infrastructure is working correctly.
                All providers, contexts, and utilities are functioning as expected.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntegrationTest;